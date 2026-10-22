#!/usr/bin/env python3
"""S6-B r02 复审：BLK-1 稳健性反例——若把「维持优先」也施加 T6-P01 门（对 §8 第 4 条的另一种读法），
C4-jitter-reset（被引用的证据用例）是否仍然 M4 可达。结束后按字节还原。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
SRC = ISO / "src/stage6/s6_core.py"
ORIG = SRC.read_bytes()
RUN = ISO / "report/evidence/S6-B/s6b_core_20261023_r02"
ENV = {**os.environ, "PYTHONUTF8": "1"}

OLD = "            continuing = [det for det in dets if self._target_continues(det)]"
NEW = ("            continuing = [det for det in dets if self._target_continues(det)\n"
       "                          and float(det['score']) >= self.th['p01']]  # 复审注入：给维持优先也加 P01 门")
text = ORIG.decode("utf-8")
assert OLD in text
SRC.write_bytes(text.replace(OLD, NEW, 1).encode("utf-8"))
try:
    proc = subprocess.run([sys.executable, "-B", str(ISO / "verification/s6b_run_cases.py"),
                           "--project-root", str(ISO), "--run-dir", str(RUN)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False, env=ENV)
    print("driver exit =", proc.returncode)
    print("stdout tail:", (proc.stdout.strip().splitlines() or [""])[-1][:250])
    report = json.loads((RUN / "run_report.json").read_text(encoding="utf-8"))
    for row in report["cases"]:
        if row["case_id"] in ("C4-jitter-reset", "C5-held-priority", "C6-no-hand-unknown-lowscore"):
            print(f"  {row['case_id']}: status={row['status']} transitions={row['observed']['transitions']}"
                  f" failures={row['assertions_failed'][:2]}")
    log = (RUN / "logs/C4-jitter-reset.jsonl").read_text(encoding="utf-8").splitlines()
    for line in log:
        r = json.loads(line)
        if r.get("transition"):
            print("  C4:", r.get("frame_id"), r["transition"], r.get("to_state"), "|", (r.get("reason") or "")[:50])
finally:
    SRC.write_bytes(ORIG)
    print("还原字节一致:", SRC.read_bytes() == ORIG)