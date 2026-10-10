"""独立审查：只写本次隔离目录，运行原生工具并核对原始证据。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("review_runner", ROOT / "verification/test_s2b_hp0_word_adapter_rtl.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
report = {"status": "FAIL", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "runs": []}
started = time.monotonic()
audit = []
for index in range(1, 9):
    directory = ROOT / f"report/evidence/S2B-T10/hp0_adapter_20261010_r{index:02}"
    previous = json.loads((directory / "result.json").read_text(encoding="utf-8"))
    manifest = json.loads((directory / "delivery_manifest.json").read_text(encoding="utf-8"))
    bindings = []
    for item in manifest["files"]:
        file = ROOT / item["path"]
        # 历史运行的当前源码可已被修复；原始快照和运行原件必须保持原绑定。
        if file.is_relative_to(directory):
            assert runner.sha(file) == item["sha256"], str(file)
            bindings.append(item["path"])
    for run in previous["runs"]:
        assert runner.sha(directory / (run["name"] + ".log")) == run["log_sha256"]
    audit.append({"run_id": directory.name, "status": previous["status"], "error": previous.get("error"), "runs": previous["runs"], "bound_files_checked": len(bindings), "result_sha256": runner.sha(directory / "result.json"), "manifest_sha256": runner.sha(directory / "delivery_manifest.json")})
(HERE / "historical_audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
work, evidence = HERE / "rebuild_cache", HERE / "rebuild_evidence"
work.mkdir()
evidence.mkdir()
try:
    runner.run(work, evidence, Path(r"D:\FPGA_S2A_MSYS2_20261001\env"), report)
    guard_spec = importlib.util.spec_from_file_location("review_guard", ROOT / "verification/test_s2b_request_guard_rtl.py")
    guard = importlib.util.module_from_spec(guard_spec)
    guard_spec.loader.exec_module(guard)
    guard_work, guard_evidence = HERE / "guard_cache", HERE / "guard_evidence"
    guard_work.mkdir()
    guard_evidence.mkdir()
    report["guard_regression"] = {"status": "FAIL", "runs": []}
    guard.run(guard_work, guard_evidence, Path(r"D:\FPGA_S2A_MSYS2_20261001\env"), report["guard_regression"])
    assert report["guard_regression"]["coverage"]["total_samples"] == 70736
except Exception as exc:
    report["status"] = "FAIL"
    report["error"] = repr(exc)
report["elapsed_seconds"] = round(time.monotonic() - started, 3)
(HERE / "rebuild_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(ROOT / "report/evidence/S2B-T10/hp0_adapter_20261010_r08/delivery_manifest.json")]
    before = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    (HERE / (mode + "_check.log")).write_bytes(result.stdout + result.stderr)
    (HERE / (mode + "_check.json")).write_text(json.dumps({"command": command, "native_exit_code": result.returncode, "seconds": round(time.monotonic()-before, 3)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(mode, result.returncode)
raise SystemExit(0 if report["status"].startswith("PASS_") else 2)
