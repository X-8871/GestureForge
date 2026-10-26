#!/usr/bin/env python3
"""将手册印刷第29–31页的 J11 坐标与绑定 XDC 逐项核对。"""

from __future__ import annotations

import re
import sys
from pathlib import Path


EXPECTED = {
    "cmos1_d[9]": "F17",
    "cmos1_i2c_sda_io": "F16",
    "cmos1_d[6]": "F20",
    "cmos1_i2c_scl_io": "F19",
    "cmos1_d[7]": "G20",
    "cmos1_d[2]": "G19",
    "cmos1_href": "H18",
    "cmos1_d[8]": "J18",
    "cmos1_d[3]": "L20",
    "cmos_rstn_tri_o[0]": "L19",
    "cmos1_d[4]": "M20",
    "cmos1_d[5]": "M19",
    "cmos1_d[1]": "K18",
    "cmos1_d[0]": "K17",
    "cmos1_vsync": "J19",
    "cmos1_pclk": "K19",
}


def main() -> int:
    """比较手册摘录的封装坐标与指定基线 XDC。"""
    root = Path(__file__).resolve().parents[4]
    xdc = root / "board" / "stage3" / "hardware" / "an5642_j11_cmos2.xdc"
    text = xdc.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^\s*set_property\s+PACKAGE_PIN\s+(\S+)\s+"
        r"\[get_ports\s+\{([^}]+)\}\]",
        re.MULTILINE,
    )
    observed = {port: pin for pin, port in pattern.findall(text) if port in EXPECTED}
    if observed != EXPECTED:
        missing = sorted(set(EXPECTED) - set(observed))
        mismatched = {
            port: {"expected": pin, "observed": observed.get(port)}
            for port, pin in EXPECTED.items()
            if observed.get(port) != pin
        }
        print(f"FAIL missing={missing} mismatched={mismatched}")
        return 1
    print(f"PASS J11 PIN3-18 package mapping: {len(EXPECTED)}/{len(EXPECTED)}")
    print(f"XDC={xdc.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
