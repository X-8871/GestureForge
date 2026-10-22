#!/usr/bin/env python3
"""S6-B r02 复审：N-07 旧行为反例注入（只改隔离副本，结束后按字节还原）。

旧行为 = state=NO_HAND 携带 detections 时静默忽略（不 count invalid / no_hand_with_detections）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
SRC = ISO / "src/stage6/s6_core.py"
ORIGINAL = SRC.read_bytes()
RUN = ISO / "report/evidence/S6-B/s6b_core_20261023_r02"
PY = sys.executable
ENV = {**os.environ, "PYTHONUTF8": "1"}

OLD_BLOCK = '''        # N-07：state=NO_HAND 却携带 detections 属非法输入（§11.3），计非法并丢弃该帧证据，
        # 不静默忽略（与 class_id 越界同一处理路径）。
        if state_value == "NO_HAND" and event.get("detections"):
            self.counters["invalid"] += 1
            self.counters["no_hand_with_detections"] += 1
            log["input_state"] = "INVALID"
            log["reason"] = ("E_FRAME_INVALID：state=NO_HAND 却携带 detections（§11.3）；"
                             "丢弃该帧证据并计异常（N-07）")
            self._anomaly(log, advancing=False)
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)
'''
NEW_BLOCK = '''        # 复审注入：还原旧行为（静默忽略 NO_HAND 携带的 detections）
        if state_value == "NO_HAND" and event.get("detections"):
            event = dict(event)
            event["detections"] = []
'''
text = ORIGINAL.decode("utf-8")
assert OLD_BLOCK in text, "未找到 N-07 代码块"
SRC.write_bytes(text.replace(OLD_BLOCK, NEW_BLOCK).encode("utf-8"))
print("注入完成：NO_HAND+detections 旧行为（静默忽略）")

try:
    proc = subprocess.run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"),
                           "--project-root", str(ISO), "--run-dir", str(RUN)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False, env=ENV)
    print("driver exit =", proc.returncode)
    print("stdout tail:", (proc.stdout.strip().splitlines() or [""])[-1][:300])
    report = json.loads((RUN / "run_report.json").read_text(encoding="utf-8"))
    failed = [c for c in report["cases"] if c["status"] != "PASS"]
    print("failed cases:", [c["case_id"] for c in failed])
    for case in failed:
        if case["case_id"] == "C6b-no-hand-with-detections":
            print("  C6b expected:", json.dumps(case["expected"]["core_counters"], ensure_ascii=False))
            print("  C6b observed:", json.dumps(case["observed"]["core_counters"], ensure_ascii=False))
            for a in case["assertions_failed"]:
                print("  assertion:", a)
finally:
    SRC.write_bytes(ORIGINAL)
    print("已按字节还原 s6_core.py:", SRC.read_bytes() == ORIGINAL)