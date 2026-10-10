"""独立手算与异常交叉验证，复制现成监视器而不镜像生产账本。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
WORK = HERE / "extra_cache"
EVIDENCE = HERE / "extra_evidence"
WORK.mkdir()
EVIDENCE.mkdir()
(WORK / "source").mkdir()
sources = [ROOT / "src/s2b_request_guard.sv", ROOT / "src/s2b_hp0_word_adapter.sv", ROOT / "sim/tb_s2b_hp0_word_adapter.sv"]
sha = lambda file: hashlib.sha256(file.read_bytes()).hexdigest()
bound = [{"path": str(file), "sha256": sha(file)} for file in sources]
for file in sources[:2]:
    (WORK / "source" / file.name).write_bytes(file.read_bytes())
tb = sources[2].read_text(encoding="utf-8")
extra = (HERE / "extra_cases.sv").read_text(encoding="utf-8")
assert tb.count("    initial begin") == 1
assert tb.count("        directed();") == 1
tb = tb.replace("    initial begin", extra + "\n    initial begin").replace("        directed();", "        independent_cases();\n        directed();")
(WORK / "source" / sources[2].name).write_text(tb, encoding="utf-8")
(EVIDENCE / "independent_tb.sv").write_text(tb, encoding="utf-8")
toolchain = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
tools = toolchain / "mingw64/bin"
env = os.environ.copy()
env["PATH"] = str(toolchain / "usr/bin") + os.pathsep + str(tools) + os.pathsep + env.get("PATH", "")
env["VERILATOR_ROOT"] = str(tools.parent / "share/verilator")
report = {"sources": bound, "tb_sha256": sha(EVIDENCE / "independent_tb.sv"), "runs": [], "status": "FAIL"}
commands = [
    ("compile", [str(tools / "verilator_bin.exe"), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "-j", "1", "--threads", "1", "--top-module", "tb_s2b_hp0_word_adapter", "--Mdir", "obj_dir", "-MAKEFLAGS", "PYTHON3='\""+sys.executable+"\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0", *["source/"+file.name for file in sources]]),
    ("simulation", [str(WORK / "obj_dir/Vtb_s2b_hp0_word_adapter.exe"), "+VECTORS="+str(HERE / "rebuild_evidence/vectors.txt")]),
]
try:
    for name, command in commands:
        started = time.monotonic()
        with (EVIDENCE / (name+".log")).open("x", encoding="utf-8") as log:
            process = subprocess.Popen(command, cwd=WORK, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=log, stderr=subprocess.STDOUT, timeout=30)
                process.wait(timeout=30)
                raise RuntimeError("独立运行超时，保留日志")
        report["runs"].append({"name": name, "command": command, "native_exit_code": code, "seconds": round(time.monotonic()-started,3), "log_sha256": sha(EVIDENCE / (name+".log"))})
        assert code == 0, name
    log = (EVIDENCE / "simulation.log").read_text(encoding="utf-8")
    assert "PASS INDEPENDENT_HP0_CASES cases=11 hand_words=3 crossing_histories=8" in log
    assert "PASS HP0_WORD_ADAPTER vectors=8544 directed=179" in log
    for file, binding in zip(sources, bound):
        assert sha(file) == binding["sha256"], "运行期间被审文件变化"
    report["status"] = "PASS_INDEPENDENT_HAND_AND_CROSSING_CASES"
except Exception as exc:
    report["error"] = repr(exc)
(HERE / "extra_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False))
raise SystemExit(0 if report["status"].startswith("PASS_") else 2)
