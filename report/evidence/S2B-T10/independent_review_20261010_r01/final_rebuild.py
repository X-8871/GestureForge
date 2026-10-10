"""最终冻结源码的独立重建与手算验证，失败原件不覆盖。"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
HERE = BASE / "final_d3"
HERE.mkdir()
RUN_ID = "hp0_adapter_20261010_r09"
TOOLCHAIN = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
load = lambda path: json.loads(path.read_text(encoding="utf-8"))

def module(name, path):
    """直接装载既有runner，不调用写正式目录的main。"""
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

runner = module("final_hp0", ROOT / "verification/test_s2b_hp0_word_adapter_rtl.py")
guard = module("final_guard", ROOT / "verification/test_s2b_request_guard_rtl.py")
report = {"status": "FAIL", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "runs": [], "limitations": ["只审候选leaf及guard等价修复；无outerCSR、STOP、drain timer、cache、owner或实物验证。", "候选0.1.1未冻结，inputs预期2；evidence包装通过不等于完整2B通过。", "固定ID不能识别新合法窗口中无归属标志的虚假旧同ID响应；旧事务必须先合法排空。", "峰值工作集未测；原生Verilator日志中的分配量并非进程峰值工作集。"]}
start = time.monotonic()
try:
    evidence = ROOT / "report/evidence/S2B-T10" / RUN_ID
    history = []
    for index in range(1,10):
        old = ROOT / f"report/evidence/S2B-T10/hp0_adapter_20261010_r{index:02}"
        manifest = load(old / "delivery_manifest.json")
        previous = load(old / "result.json")
        checked = 0
        for item in manifest["files"]:
            path = ROOT / item["path"]
            if path.is_relative_to(old):
                assert sha(path) == item["sha256"], str(path)
                checked += 1
        for run in previous["runs"]:
            assert sha(old / (run["name"]+".log")) == run["log_sha256"]
        history.append({"run_id": old.name, "status": previous["status"], "error": previous.get("error"), "run_exit_codes": [run["exit_code"] for run in previous["runs"]], "original_bound_files_checked": checked, "result_sha256": sha(old / "result.json"), "manifest_sha256": sha(old / "delivery_manifest.json")})
    (HERE / "historical_audit.json").write_text(json.dumps(history, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    work, out = HERE / "adapter_cache", HERE / "adapter_evidence"
    work.mkdir(); out.mkdir()
    runner.run(work, out, TOOLCHAIN, report)
    guard_work, guard_out = HERE / "guard_cache", HERE / "guard_evidence"
    guard_work.mkdir(); guard_out.mkdir()
    report["guard_regression"] = {"status": "FAIL", "runs": []}
    guard.run(guard_work, guard_out, TOOLCHAIN, report["guard_regression"])
    assert report["guard_regression"]["coverage"]["total_samples"] == 70736
    # 额外场景只复用公开端口监视器，数据预期采用手算固定常量。
    extra_work, extra_out = HERE / "extra_cache", HERE / "extra_evidence"
    extra_work.mkdir(); extra_out.mkdir(); (extra_work / "source").mkdir()
    for name in ("s2b_request_guard.sv", "s2b_hp0_word_adapter.sv"):
        (extra_work / "source" / name).write_bytes((work / "source" / name).read_bytes())
        (extra_out / name).write_bytes((work / "source" / name).read_bytes())
    tb = (work / "source/tb_s2b_hp0_word_adapter.sv").read_text(encoding="utf-8")
    assert tb.count("    initial begin") == tb.count("        directed();") == 1
    tb = tb.replace("    initial begin", (BASE / "extra_cases.sv").read_text(encoding="utf-8")+"\n    initial begin").replace("        directed();", "        independent_cases();\n        directed();")
    (extra_work / "source/tb_s2b_hp0_word_adapter.sv").write_text(tb, encoding="utf-8")
    (extra_out / "independent_tb.sv").write_text(tb, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = str(TOOLCHAIN / "usr/bin")+os.pathsep+str(TOOLCHAIN / "mingw64/bin")+os.pathsep+env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(TOOLCHAIN / "mingw64/share/verilator")
    report["extra"] = {"status": "FAIL", "runs": [], "cases": 11, "hand_words": 3, "crossing_histories": 8, "tb_sha256": sha(extra_out / "independent_tb.sv")}
    commands = [("compile", report["runs"][0]["command"]), ("simulation", [str(extra_work / "obj_dir/Vtb_s2b_hp0_word_adapter.exe"), "+VECTORS="+str(out / "vectors.txt")])]
    for name, command in commands:
        before = time.monotonic()
        with (extra_out / (name+".log")).open("x", encoding="utf-8") as log:
            process = subprocess.Popen(command, cwd=extra_work, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=log, stderr=subprocess.STDOUT, timeout=30)
                process.wait(timeout=30)
                raise RuntimeError("独立额外场景超时")
        report["extra"]["runs"].append({"name": name, "command": command, "native_exit_code": code, "seconds": round(time.monotonic()-before,3), "log_sha256": sha(extra_out / (name+".log"))})
        assert code == 0, name
    log_text = (extra_out / "simulation.log").read_text(encoding="utf-8")
    assert "PASS INDEPENDENT_HP0_CASES cases=11 hand_words=3 crossing_histories=8" in log_text
    assert "PASS HP0_WORD_ADAPTER vectors=8544 directed=179" in log_text
    report["extra"]["status"] = "PASS_INDEPENDENT_HAND_AND_CROSSING_CASES"
    report["packaging"] = []
    for mode in ("evidence", "inputs"):
        command = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(evidence / "delivery_manifest.json")]
        before = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=60)
        (HERE / (mode+"_check.log")).write_bytes(result.stdout+result.stderr)
        report["packaging"].append({"mode": mode, "command": command, "native_exit_code": result.returncode, "seconds": round(time.monotonic()-before,3)})
        assert result.returncode == (0 if mode == "evidence" else 2)
    for binding in report["sources"]:
        assert sha(ROOT / binding["path"]) == binding["sha256"], "最终验证期间源码变化"
    report["status"] = "PASS_FINAL_INDEPENDENT_RTL_REBUILD"
except Exception as exc:
    report["status"] = "FAIL"
    report["error"] = repr(exc)
report["elapsed_seconds"] = round(time.monotonic()-start,3)
(HERE / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report["status"].startswith("PASS_") else 2)
