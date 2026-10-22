#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐字段比对：我复刻的 8 个探针用例 vs 入库 probe_summary.json。"""
import json
from pathlib import Path

OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
RUN = Path("D:/codex-worktrees/w6/report/evidence/S6-A/s6a_g0_20261022_r05")
mine = json.loads((OUT / "my_probe.txt").read_text(encoding="utf-8"))
theirs = json.loads((RUN / "probe_summary.json").read_text(encoding="utf-8"))
tm = {r["case_id"]: r for r in theirs["results"]}
lines = []
all_same = True
for r in mine["probe_cases"]:
    t = tm[r["case_id"]]
    fields = ["expected_exit", "actual_exit", "expected_check", "failed_checks", "captured", "verdict"]
    diffs = {f: (r[f], t[f]) for f in fields if r[f] != t[f]}
    if diffs:
        all_same = False
    lines.append(f"{r['case_id']}: {'逐字段一致' if not diffs else diffs}")
lines.append(f"baseline_verdict: 我={mine['baseline_exit']} 入库={theirs['baseline_verdict']}")
lines.append(f"8 个探针用例逐字段完全一致：{all_same}")
lines.append(f"我额外自造 10 例：{[(r['case_id'], r['actual_exit'], r['failed_checks'], r['verdict']) for r in mine['extra_cases']]}")
(OUT / "my_probe_compare.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))