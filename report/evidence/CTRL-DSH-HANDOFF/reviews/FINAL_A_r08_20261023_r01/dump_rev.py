#!/usr/bin/env python3
"""按 rev + 前缀，用 git cat-file 批量导出提交字节（只读，不写被审仓库）。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MAIN = Path(r"D:/FPGA_Competition")
OUT = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/committed")


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(MAIN), *args], capture_output=True, check=True).stdout


def dump(rev: str, prefixes: list[str]) -> int:
    names = git("ls-tree", "-r", "--name-only", "-z", rev, "--", *prefixes).decode("utf-8").split("\0")
    names = [n for n in names if n]
    root = OUT / rev
    if root.exists():
        import shutil
        shutil.rmtree(root)
    if not names:
        print(f"{rev}: 无匹配路径")
        return 0
    proc = subprocess.Popen(["git", "-C", str(MAIN), "cat-file", "--batch"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    payload = "".join(f"{rev}:{n}\n" for n in names).encode("utf-8")
    out, _ = proc.communicate(payload)
    pos = 0
    for name in names:
        nl = out.index(b"\n", pos)
        header = out[pos:nl].decode("utf-8", "replace")
        size = int(header.rsplit(" ", 1)[1])
        data = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"{rev}: {len(names)} 个文件")
    return len(names)


if __name__ == "__main__":
    revs = ["f3c537d", "902be77", "e3aeb09", "05126fd", "bdcf896", "87a6bdc", "04ea58e1"]
    prefixes = [
        "report/evidence/S6-A/s6a_g0_20261022_r08",
        "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof",
        "report/evidence/S6-B/s6b_core_20261023_r03",
        "report/evidence/S6-B/s6b_core_20261023_r03_selfproof",
        "docs/stage6",
        "verification",
        ".codex/STATE.md",
    ]
    for rev in revs:
        dump(rev, prefixes)