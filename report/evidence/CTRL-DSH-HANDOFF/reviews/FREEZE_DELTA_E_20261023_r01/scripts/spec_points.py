#!/usr/bin/env python3
"""F5 复评点名的 12 处"待批准/非批准"文本在 F6d 的实际状态；以及历史语境标记分布。"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
OUT = pathlib.Path(r"D:\FPGA_Competition\tmp\review\FREEZE_DELTA_E_20261023_r01\10_spec_12_points.txt")
doc = (ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8").splitlines()

cited = [9, 10, 128, 130, 171, 185, 280, 282, 320, 321, 397]
out = ["### F5 复评点名的文本点在 F6d（2f16d668）的实际内容", ""]
for ln in cited:
    text = doc[ln - 1]
    has_pending = bool(re.search(r"待批准|PENDING", text))
    has_hist = bool(re.search(r"历史语境|当时|历史修订|历史状态|v1\.\d+（r\d+", text))
    out.append(f"L{ln}: pending_token={has_pending} historical_marker={has_hist}")
    out.append(f"    {text}")
    out.append("")

out.append("### 8 条历史修订记录行（含 APPROVED_20261023 的修订行）的实际标记状态")
out.append("")
for ln, text in enumerate(doc, 1):
    if "APPROVED_20261023" in text and ln < 45:
        hist = bool(re.search(r"历史语境|当时|历史修订|历史状态|v1\.\d+（r\d+", text))
        out.append(f"L{ln}: historical_machine_marker={hist}")
        out.append(f"    {text[:150]}...")
        out.append("")

out.append("### 规格文档中所有出现【历史语境】标记的行")
for ln, text in enumerate(doc, 1):
    if "历史语境" in text:
        out.append(f"L{ln}: {text[:200]}")

pathlib.Path(OUT).write_text("\n".join(out) + "\n", encoding="utf-8")
print("lines:", len(out))