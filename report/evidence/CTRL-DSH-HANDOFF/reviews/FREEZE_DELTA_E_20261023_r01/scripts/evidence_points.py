#!/usr/bin/env python3
"""F5 复评点名的证据包内 PENDING 文本点在 F6d 新包（r12/r07）中的实际内容。"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
OUT = pathlib.Path(r"D:\FPGA_Competition\tmp\review\FREEZE_DELTA_E_20261023_r01\11_evidence_points.txt")
SAMPLES = {
    "report/evidence/S6-A/s6a_g0_20261023_r12/S6A_run_summary.md": [1, 5, 6, 42],
    "report/evidence/S6-A/s6a_g0_20261023_r12/delivery_manifest.json": [378],
    "report/evidence/S6-A/s6a_g0_20261023_r12/coverage_matrix.json": [28, 57, 58, 122, 127, 132, 206, 224],
    "report/evidence/S6-A/s6a_g0_20261023_r12/fix_record.json": [10, 16, 81],
    "report/evidence/S6-A/s6a_g0_20261023_r12/fix_record.md": [5, 6],
    "report/evidence/S6-A/s6a_g0_20261023_r12/limitations_not_executed.json": [19, 44],
    "report/evidence/S6-B/s6b_core_20261023_r07/inputs_manifest.json": [9, 15, 27],
    "report/evidence/S6-B/s6b_core_20261023_r07/delivery_manifest.json": [9, 398],
    "report/evidence/S6-B/s6b_core_20261023_r07/limitations_not_executed.json": [15, 55],
    "report/evidence/S6-B/s6b_core_20261023_r07/reachability_notes.json": [4, 5, 6],
    "report/evidence/S6-B/s6b_core_20261023_r07/s6b_run_summary.md": [1, 7],
    "report/evidence/S6-B/s6b_core_20261023_r07/params_snapshot.json": [5, 6, 7, 241, 242, 243, 244, 245],
    "report/evidence/S6-B/s6b_core_20261023_r07/run_report.json": [5, 6, 7, 8, 9, 10, 11],
}
out = []
for rel, lns in SAMPLES.items():
    p = ROOT / rel
    if not p.is_file():
        out.append(f"!! missing {rel}")
        continue
    lines = p.read_text(encoding="utf-8").splitlines()
    out.append(f"=== {rel}（共 {len(lines)} 行）")
    for ln in lns:
        txt = lines[ln - 1] if ln - 1 < len(lines) else "<out of range>"
        pend = bool(re.search(r"待批准|PENDING|pending_approval|draft_not_approved", txt))
        hist = bool(re.search(r"历史语境|当时|历史修订|历史状态|v1\.\d+（r\d+", txt))
        out.append(f"  L{ln}: pending={pend} hist={hist} :: {txt.strip()[:230]}")
    out.append("")
OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
print("files:", len(SAMPLES))