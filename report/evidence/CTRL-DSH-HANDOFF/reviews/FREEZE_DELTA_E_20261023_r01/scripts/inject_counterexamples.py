#!/usr/bin/env python3
"""独立注入反例：approved_package_scan 的判别力（fail-closed 检验）。

在**我自己目录**内的项目根副本里，对**真实 run-dir** 逐例注入一行 PENDING 断言，
调用扫描器（**不带** --inject-self-test），记录真实退出码。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

CLONE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
INJ = OUT / "inj_root"

S6B_RUN = "report/evidence/S6-B/s6b_core_20261023_r07"
S6A_RUN = "report/evidence/S6-A/s6a_g0_20261023_r12"

CASES = [
    ("B1 JSON approval_status=PENDING_APPROVAL",
     '"approval_status": "PENDING_APPROVAL"'),
    ("B2 本包阈值仍为待批准状态（自然语言）",
     "本包全部阈值与指标仍为待批准状态"),
    ("B3 旧机读假字段 all_parameters_pending_approval=true",
     '"all_parameters_pending_approval": true'),
    ("B4 旧机读假字段 thresholds_are_draft_not_approved=true",
     '"thresholds_are_draft_not_approved": true'),
    ("B5 旧机读假字段 parameters_pending_approval=true",
     '"parameters_pending_approval": true'),
    ("B6 文档状态行 APPROVED_20261023（待批准）",
     "状态：`G0_PACKET_APPROVED_20261023`（待批准）。"),
    ("B7 T6-A01 约束（待批准）",
     "受 `T6-A01` 约束（待批准）。"),
    ("B8 局部字段 pending_confirmation（开放项）",
     '"pending_confirmation": "U6-16 开放项"'),
]

if INJ.exists():
    shutil.rmtree(INJ)
(INJ / "docs").mkdir(parents=True)
shutil.copytree(CLONE / "docs/stage6", INJ / "docs/stage6")
for rel in (S6A_RUN, S6B_RUN):
    dst = INJ / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CLONE / rel, dst)

lines = ["### 独立注入反例（扫描器无 --inject-self-test，直接对真实 run-dir 注入）", ""]
for run_rel, tag in ((S6B_RUN, "S6B"), (S6A_RUN, "S6A")):
    lines.append(f"--- {tag} run-dir: {run_rel}")
    probe = INJ / run_rel / "INJECTED_probe.txt"
    for name, text in CASES:
        probe.write_text(text + "\n", encoding="utf-8")
        cmd = [sys.executable, "-B", str(CLONE / "verification/approved_package_scan.py"),
               "--project-root", str(INJ), "--run-dir", run_rel,
               "--out", str(OUT / f"inj_{tag}_{name.split()[0]}.json")]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        payload = {}
        outp = OUT / f"inj_{tag}_{name.split()[0]}.json"
        if outp.is_file():
            payload = json.loads(outp.read_text(encoding="utf-8"))
        caught = r.returncode != 0
        lines.append(f"  {name}")
        lines.append(f"    exit={r.returncode} verdict={payload.get('verdict')} "
                     f"hits={len(payload.get('hits', []))} caught={'YES' if caught else 'NO（fail-open）'}")
        if payload.get("hits"):
            lines.append(f"    hit[0]={payload['hits'][0][:160]}")
    probe.unlink()
    # 基线（无注入）
    cmd = [sys.executable, "-B", str(CLONE / "verification/approved_package_scan.py"),
           "--project-root", str(INJ), "--run-dir", run_rel, "--out", str(OUT / f"inj_{tag}_baseline.json")]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines.append(f"  baseline(no injection): exit={r.returncode} stdout={r.stdout.strip()[:120]}")
    lines.append("")

OUT.joinpath("12_injection_counterexamples.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(x for x in lines if "exit=" in x or "baseline" in x))