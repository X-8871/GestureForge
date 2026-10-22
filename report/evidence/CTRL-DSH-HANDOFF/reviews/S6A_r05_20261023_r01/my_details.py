#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
ROOT = Path("D:/codex-worktrees/w6")
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
lines = []

probe = json.loads((OUT / "my_probe.txt").read_text(encoding="utf-8"))
for r in probe["probe_cases"] + probe["extra_cases"]:
    lines.append(f"{r['case_id']}: exit={r['actual_exit']} expect={r['expected_exit']} "
                 f"failed={r['failed_checks']} captured={r['captured']} verdict={r['verdict']}")
    lines.append(f"    {r['detail_first_240']}")

lines.append("")
lines.append("=" * 70)
lines.append("文档 §18 点名的证据文件名 vs 实际存在性")
lines.append("=" * 70)
doc = (ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
sec18 = doc.split("## 18.", 1)[1]
names = set(re.findall(r"`([A-Za-z0-9_][A-Za-z0-9_.\-]*\.(?:json|md|txt|jsonl))`", sec18))
actual = {p.name for p in RUN.rglob("*") if p.is_file()}
lines.append(f"§18 点名文件 {len(names)} 个：{sorted(names)}")
lines.append(f"§18 点名但运行目录不存在：{sorted(n for n in names if n not in actual)}")
lines.append(f"运行目录中未被 §18 点名：{sorted(actual - names)}")

lines.append("")
lines.append("=" * 70)
lines.append("probe 用例口径")
lines.append("=" * 70)
src = (ROOT / "verification/s6a_r05_probe.py").read_text(encoding="utf-8")
n_entries = len(re.findall(r'\{"id": "', src))
n_inject = len(re.findall(r'"target": "(?:json|cases)"', src))
lines.append(f"INJECTIONS 条目数={n_entries}（其中 target 非 None 的注入={n_inject}）")
lines.append(f"落盘 probe_*_stdout.txt 个数="
             f"{len(list(RUN.glob('probe_*_stdout.txt')))}；probe_summary.results="
             f"{len(json.loads((RUN / 'probe_summary.json').read_text(encoding='utf-8'))['results'])}")
lines.append(f"hashes_sha256.txt 行数="
             f"{len([l for l in (RUN / 'hashes_sha256.txt').read_text(encoding='utf-8').splitlines() if l.strip()])}")

lines.append("")
lines.append("=" * 70)
lines.append("coverage_matrix.json / limitations_not_executed.json 残留 v1.3 上下文")
lines.append("=" * 70)
for key in ("coverage_matrix.json", "limitations_not_executed.json", "fix_record.json",
            "S6A_run_summary.md", "hand_computed_cases.json", "upstream_bindings.json",
            "delivery_manifest.json", "inputs_manifest.json"):
    text = (RUN / key).read_text(encoding="utf-8")
    hits = [m.group(0).strip() for m in re.finditer(r".{0,60}v1\.3.{0,60}", text)]
    if hits:
        for h in hits:
            lines.append(f"  [{key}] …{h.replace(chr(10), ' ')}…")
lines.append(f"§18 中 v1.3 上下文：")
for m in re.finditer(r".{0,80}v1\.3.{0,80}", sec18):
    lines.append(f"  …{m.group(0).strip().replace(chr(10), ' ')}…")

(OUT / "my_details.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))