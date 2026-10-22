#!/usr/bin/env python3
"""补导 r07 证据目录 + S6-B r02 目录（对照用）。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MAIN = Path(r"D:/FPGA_Competition")
OUT = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/committed")


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(MAIN), *args], capture_output=True, check=True).stdout


def dump(rev: str, prefixes: list[str]) -> None:
    names = [n for n in git("ls-tree", "-r", "--name-only", "-z", rev, "--", *prefixes)
             .decode("utf-8").split("\0") if n]
    root = OUT / rev
    proc = subprocess.Popen(["git", "-C", str(MAIN), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, _ = proc.communicate("".join(f"{rev}:{n}\n" for n in names).encode("utf-8"))
    pos = 0
    for name in names:
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].decode("utf-8").rsplit(" ", 1)[1])
        data = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"{rev}: {len(names)} 个文件")


if __name__ == "__main__":
    dump("bdcf896", ["report/evidence/S6-A/s6a_g0_20261022_r07"])
    dump("87a6bdc", ["report/evidence/S6-B/s6b_core_20261023_r02"])