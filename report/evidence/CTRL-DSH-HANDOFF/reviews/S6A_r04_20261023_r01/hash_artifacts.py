# -*- coding: utf-8 -*-
"""独立评审：计算被审 5 个源码/文档文件与 r04 全部 23 个证据文件的 SHA256。"""
import hashlib, os, sys

ROOT = r"D:\codex-worktrees\w6"
FILES = [
    r"docs\stage6\S6A_stage6_g0_behavior_spec_v1.md",
    r"docs\stage6\s6a_stage6_g0_behavior_v1.json",
    r"verification\s6_g0_selfcheck.py",
    r"verification\s6a_build_evidence.py",
    r"verification\s6a_rerun_legacy_failures.py",
    r".codex\STATE.md",
]
EV = r"report\evidence\S6-A\s6a_g0_20261022_r04"

def h(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

if __name__ == "__main__":
    for rel in FILES:
        p = os.path.join(ROOT, rel)
        print(f"{h(p)}  {rel}" if os.path.exists(p) else f"MISSING  {rel}")
    print("--- r04 evidence dir ---")
    d = os.path.join(ROOT, EV)
    names = sorted(os.listdir(d))
    print("evidence file count =", len(names))
    for n in names:
        p = os.path.join(d, n)
        print(f"{h(p)}  {n}")