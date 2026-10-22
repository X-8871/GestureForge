#!/usr/bin/env python3
"""复核：baseline 构建产物与提交版 case_matrix.json 是否逐字节一致（除 run_id）。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
WORK = ISO / "tmp/review_inj/builder_base"
ORIG_SRC = ISO / "report/evidence/S6-B/s6b_core_20261023_r02/cases/build_case_matrix.py"
COMMITTED = ISO / "report/evidence/S6-B/s6b_core_20261023_r02/cases/case_matrix.json"
ENV = {**os.environ, "PYTHONUTF8": "1"}
if WORK.exists():
    shutil.rmtree(WORK)
(WORK / "cases").mkdir(parents=True)
text = ORIG_SRC.read_text(encoding="utf-8")
text = text.replace('RUN = Path(r"D:\\codex-worktrees\\w6\\report\\evidence\\S6-B\\s6b_core_20261023_r02")',
                    f'RUN = Path(r"{WORK}")')
(WORK / "builder.py").write_text(text, encoding="utf-8")
proc = subprocess.run([sys.executable, "-B", str(WORK / "builder.py")], capture_output=True, text=True,
                      encoding="utf-8", errors="replace", check=False, env=ENV)
print("baseline exit:", proc.returncode)
a = json.loads((WORK / "cases/case_matrix.json").read_text(encoding="utf-8"))
b = json.loads(COMMITTED.read_text(encoding="utf-8"))
print("run_id:", a["run_id"], "vs", b["run_id"])
a["run_id"] = b["run_id"]
ca = json.dumps(a, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
cb = json.dumps(b, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
print("canonical identical (run_id 归一后):", ca == cb)
if ca != cb:
    for k in a:
        if json.dumps(a[k], ensure_ascii=False, sort_keys=True) != json.dumps(b.get(k), ensure_ascii=False, sort_keys=True):
            print("  diff key:", k)