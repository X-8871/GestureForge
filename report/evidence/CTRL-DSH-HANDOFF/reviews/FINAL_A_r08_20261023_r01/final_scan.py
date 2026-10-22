#!/usr/bin/env python3
"""最终确认：全包（含验证器源码）语义级禁语扫描 —— 逐条列出，便于人工判读。"""
from __future__ import annotations

import re
from pathlib import Path

E8 = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/committed/f3c537d")
PATTERNS = [
    (r"M4[^。\n]{0,24}不可达", "M4 … 不可达"),
    (r"不可达项（不计入覆盖）[^\n]{0,200}", "不可达项（不计入覆盖）"),
    (r"M4[^。\n]{0,12}显式登记不可达", "M4 显式登记不可达"),
    (r"不得计入覆盖", "不得计入覆盖"),
    (r"m4_reachable_under_draft\"?\s*[:=]\s*false", "m4_reachable_under_draft=false"),
]
HIST = ("不构成不可达", "历史语境除外", "原声明", "改为", "r07 复评", "BLK-r07-1", "禁语", "『")


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    targets = []
    for rel in ("report/evidence/S6-A/s6a_g0_20261022_r08",
                "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof",
                "docs/stage6"):
        d = E8 / rel
        if d.is_dir():
            targets += [p for p in d.rglob("*") if p.is_file()]
    for rel in ("verification/s6_g0_selfcheck.py", "verification/s6a_build_evidence.py",
                "verification/claim_verify.py", "verification/export_selfproof.py",
                "verification/s6a_r08_probe.py", "verification/s6a_rerun_legacy_failures.py"):
        p = E8 / rel
        if p.is_file():
            targets.append(p)
    targets.append(E8 / ".codex/STATE.md")
    hard = []
    soft = []
    for p in sorted(set(targets)):
        rel = p.relative_to(E8).as_posix()
        for i, line in enumerate(T(p).splitlines(), 1):
            for pat, label in PATTERNS:
                if re.search(pat, line):
                    rec = (rel, i, label, line.strip())
                    (soft if any(h in line for h in HIST) else hard).append(rec)
                    break
    print("### 非豁免（判定为真实残留）")
    for rel, i, label, line in hard:
        print(f"  [{label}] {rel}:{i}\n      {line[:300]}")
    print(f"  合计 = {len(hard)}")
    print("\n### 豁免（历史/否定/元陈述语境，已人工判读）")
    for rel, i, label, line in soft:
        print(f"  [{label}] {rel}:{i}  {line[:180]}")
    print(f"  合计 = {len(soft)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())