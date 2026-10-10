#!/usr/bin/env python3
"""保留初次断言错误，补充检查器实际契约与源码不变证据。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

base = Path(__file__).resolve().parent
root = base.parents[3]
checks = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", "report/evidence/S2B-T09/request_guard_20261010_r03/delivery_manifest.json"]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=60)
    (base / ("checker_followup_" + mode + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    parsed = json.loads(result.stdout)
    expected = 0 if mode == "evidence" else 2
    assert result.returncode == expected
    if mode == "inputs":
        assert parsed["errors"] == ["interfaces[0] 接口未冻结，阻断 inputs 核验",
                                    "checks[3] 依赖检查状态为 BLOCKED，阻断 inputs 核验"]
    checks.append({"mode": mode, "command": command, "exit_code": result.returncode,
                   "status": parsed["status"], "errors": parsed["errors"]})
report = json.loads((base / "rebuild_result.json").read_text(encoding="utf-8"))
assert all(hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
           for entry in report["sources"])
assert report["status"] == "PASS_COMBINATIONAL_REQUEST_GUARD"
independent = json.loads((base / "independent_result.json").read_text(encoding="utf-8"))
assert independent["status"] == "PASS"
summary = {"verdict": "PASS", "source_commit": report["source_commit"], "sources": report["sources"],
           "checker": checks, "rebuild_samples": report["coverage"]["total_samples"],
           "rebuild_seconds": report["elapsed_seconds"], "independent_samples": independent["samples"],
           "seed": independent["seed"], "random_samples": independent["random_samples"],
           "review_driver_failure": {"exit_code": 1, "log": "driver.log",
             "reason": "任务卡误给 inputs 失败退出码1；实际检查器944行统一返回2，初次断言失败保留。"},
           "limitations": ["仅组合候选模块G2；物理候选0.1.1未冻结，部署依赖继续BLOCKED。",
                           "未执行综合、时序、AXI集成、所有权、cache/DDR或实物验收。",
                           "模块没有valid，不能据此证明物理AXI VALID零副作用。",
                           "峰值内存未测；编译一job、仿真一线程；原重建1次，新增仿真1次。"]}
(base / "review_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"verdict": "PASS", "checker_exit_codes": [x["exit_code"] for x in checks],
                  "sources_unchanged": True}, ensure_ascii=False))
