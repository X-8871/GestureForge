#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
doc = (Path("D:/codex-worktrees/w6") / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
parts = []
parts.append("=========== §9 ===========")
parts.append(doc[doc.find("## 9."):doc.find("## 10.")])
parts.append("=========== §14 相关行 ===========")
sec14 = doc[doc.find("## 14."):doc.find("## 15.")]
for ln in sec14.splitlines():
    if any(k in ln for k in ("T6-S01", "T6-S02", "T6-S03", "T6-S04")):
        parts.append(ln)
parts.append("=========== §15 ===========")
parts.append(doc[doc.find("## 15."):doc.find("## 16.")])
parts.append("=========== M3 行 + 稳定判定相关段落（§4 段） ===========")
sec4 = doc[doc.find("## 4."):doc.find("## 5.")]
for ln in sec4.splitlines():
    if "M3" in ln or "窗口" in ln or "W_min" in ln:
        parts.append(ln)
(OUT / "doc_s9_s14.txt").write_text("\n".join(parts) + "\n", encoding="utf-8")
print("ok")