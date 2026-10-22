#!/usr/bin/env python3
"""S6-B r02 复审：注入/反例核验（只写隔离目录）。

每个注入都在隔离副本上完成，调用隔离副本内的工具，记录真实退出码与关键输出。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
BASE = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso\tmp\review_inj")
RUN_REL = "report/evidence/S6-B/s6b_core_20261023_r02"
RUN = ISO / RUN_REL
PY = sys.executable


def run(args, cwd=ISO):
    p = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", check=False,
                       env={**__import__("os").environ, "PYTHONUTF8": "1"})
    return p


def show(name, proc, expect):
    tail = (proc.stdout.strip().splitlines() or [""])[-1]
    err = (proc.stderr.strip().splitlines() or [""])[-1]
    print(f"[{name}] expect={expect} actual={proc.returncode} :: out={tail[:200]} :: err={err[:200]}")
    return proc.returncode == expect


results = []
BASE.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- (a) 阈值注入 T6-S01=900
scratch = BASE / "threshold"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "cases").mkdir(exist_ok=True)
shutil.copy(RUN / "cases/case_matrix.json", scratch / "cases/case_matrix.json")
shutil.copy(RUN / "expected_freeze.json", scratch / "expected_freeze.json")
behavior = json.loads((ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
for item in behavior["parameters"]:
    if item["id"] == "T6-S01":
        item["draft_value"] = 900.0
        item["draft_source"] = "复审注入：T6-S01=900ms（仅隔离副本）"
tampered = scratch / "behavior_t6s01_900.json"
tampered.write_text(json.dumps(behavior, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
# 与 probe P4 同口径：用例文件换了路径身份，必须先按新路径重新冻结（否则测到的是 N-09 哈希门）
refreeze = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
                "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json"),
                "--freeze-only", "--force-freeze"])
print(f"[a pre-freeze] exit={refreeze.returncode} :: {(refreeze.stdout or '').strip()[:120]}")
proc = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
            "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json"),
            "--behavior-json", str(tampered)])
results.append(("a-T6S01-900", show("a T6-S01=900ms", proc, 1)))

# ---------------------------------------------------------------- (b) N-09 改用例输入
scratch = BASE / "cases_tampered"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "cases").mkdir(exist_ok=True)
cases = json.loads((RUN / "cases/case_matrix.json").read_text(encoding="utf-8"))
cases["cases"][0]["events"][0]["detections"][0]["score"] = 0.31  # 阈值内、行为等价
(scratch / "cases/case_matrix.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
shutil.copy(RUN / "expected_freeze.json", scratch / "expected_freeze.json")
proc = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
            "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json")])
results.append(("b-N09-single-case-edit", show("b N-09 改一个用例（score 0.90→0.31）", proc, 2)))

# 亚型：只改 description（连语义都不变）
scratch = BASE / "cases_desc_tampered"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "cases").mkdir(exist_ok=True)
cases = json.loads((RUN / "cases/case_matrix.json").read_text(encoding="utf-8"))
cases["cases"][0]["description"] = cases["cases"][0]["description"] + "（复审注入：仅文案）"
(scratch / "cases/case_matrix.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
shutil.copy(RUN / "expected_freeze.json", scratch / "expected_freeze.json")
proc = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
            "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json")])
results.append(("b2-N09-desc-only", show("b2 N-09 只改文案", proc, 2)))

# ---------------------------------------------------------------- (c) N-06 删除必需参数
for pid in ("T6-03", "T6-A03", "T6-S02"):
    scratch = BASE / f"del_{pid}"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "cases").mkdir(exist_ok=True)
    shutil.copy(RUN / "cases/case_matrix.json", scratch / "cases/case_matrix.json")
    shutil.copy(RUN / "expected_freeze.json", scratch / "expected_freeze.json")
    behavior = json.loads((ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
    behavior["parameters"] = [p for p in behavior["parameters"] if p["id"] != pid]
    path = scratch / f"behavior_del_{pid}.json"
    path.write_text(json.dumps(behavior, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    proc = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
                "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json"),
                "--behavior-json", str(path)])
    results.append((f"c-N06-del-{pid}", show(f"c N-06 删除 {pid}", proc, 2)))

# ---------------------------------------------------------------- (d) 契约版本不符
scratch = BASE / "wrong_version"
scratch.mkdir(parents=True, exist_ok=True)
(scratch / "cases").mkdir(exist_ok=True)
shutil.copy(RUN / "cases/case_matrix.json", scratch / "cases/case_matrix.json")
shutil.copy(RUN / "expected_freeze.json", scratch / "expected_freeze.json")
behavior = json.loads((ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
behavior["artifact_version"] = "S6A-G0-v1.5"
path = scratch / "behavior_v15.json"
path.write_text(json.dumps(behavior, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
proc = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"), "--project-root", str(ISO),
            "--run-dir", str(scratch), "--cases", str(scratch / "cases/case_matrix.json"),
            "--behavior-json", str(path)])
results.append(("d-version-mismatch", show("d 契约版本 v1.5（核心期望 v1.6）", proc, 2)))

print("ALL_INJECTIONS_OK" if all(ok for _, ok in results) else "SOME_INJECTION_UNEXPECTED",
      {n: ok for n, ok in results})