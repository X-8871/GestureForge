#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立复核：把 io_placed 报告里 16 个摄像头信号的落点与 J10 期望表逐条比对。

用法：
    python verify_io_placement.py <design_1_wrapper_io_placed.rpt>

用途：
  * 对 J10 变体的 io_placed 报告 => 期望 16/16 命中（PASS）；
  * 也可对 J11 变体的报告做**阴性对照** => 期望 0/16（证明本比对确实按 FPGA 脚判定，
    而不是解析失败后“看着像通过”）。
退出码：0 = 全部命中；1 = 存在不一致；2 = 输入/解析错误。
"""

import re
import sys

# 官方 23_ov5640_dual cmos2 通道（= J10）的 16 个 FPGA 脚
EXPECTED = [
    (3,  "W19", "cmos1_d[9]"),
    (4,  "W18", "cmos1_i2c_sda_io"),
    (5,  "R14", "cmos1_d[6]"),
    (6,  "P14", "cmos1_i2c_scl_io"),
    (7,  "Y17", "cmos1_d[7]"),
    (8,  "Y16", "cmos1_d[2]"),
    (9,  "W15", "cmos1_href"),
    (10, "V15", "cmos1_d[8]"),
    (11, "Y14", "cmos1_d[3]"),
    (12, "W14", "cmos_rstn_tri_o[0]"),
    (13, "P18", "cmos1_d[4]"),
    (14, "N17", "cmos1_d[5]"),
    (15, "U15", "cmos1_d[1]"),
    (16, "U14", "cmos1_d[0]"),
    (17, "P16", "cmos1_vsync"),
    (18, "P15", "cmos1_pclk"),
]


def parse_io_report(path):
    placed = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) < 6:
                continue
            pin, sig, _bank, _pname, use, iostd = cols[0], cols[1], cols[2], cols[3], cols[4], cols[5]
            if not sig or sig == "Signal Name" or pin == "Pin Number":
                continue
            if set(pin) <= set("+- "):
                continue
            placed[sig] = {"fpga_pin": pin, "use": use, "iostd": iostd}
    return placed


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_io_placement.py <io_placed.rpt>")
    path = sys.argv[1]
    placed = parse_io_report(path)
    print("IO_REPORT=%s" % path)
    print("PARSED_IO_SIGNALS=%d" % len(placed))
    if len(placed) < 20:
        print("FAIL=io_report_parse_suspiciously_small")
        return 2

    hits, misses = 0, []
    print("")
    print("%-7s %-6s %-22s %-22s %-7s %s" % ("J10pin", "want", "port", "actual", "match", "iostd"))
    for j10_pin, want_fpga, port in EXPECTED:
        got = placed.get(port)
        actual = got["fpga_pin"] if got else "<absent>"
        iostd = got["iostd"] if got else ""
        ok = bool(got) and actual == want_fpga
        hits += 1 if ok else 0
        if not ok:
            misses.append((j10_pin, want_fpga, port, actual))
        print("%-7d %-6s %-22s %-22s %-7s %s" % (j10_pin, want_fpga, port, actual, "OK" if ok else "MISMATCH", iostd))

    print("")
    print("MATCHED=%d/16" % hits)
    if misses:
        print("MISMATCHES=%s" % misses)
        return 1
    print("RESULT=ALL_16_MATCH_J10_TABLE")
    return 0


if __name__ == "__main__":
    sys.exit(main())