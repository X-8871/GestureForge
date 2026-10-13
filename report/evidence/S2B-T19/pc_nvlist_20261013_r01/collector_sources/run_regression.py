"""记录本轮离线回归的实际命令、日志及源码前后绑定。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

root = Path.cwd()
run = root / "report/evidence/S2B-T19/pc_nvlist_20261013_r01"
initial_run = run
if len(sys.argv) > 1:
    run = run / sys.argv[1]
    run.mkdir(exist_ok=False)
cache = root / "tmp/2B/S2B-T19/pc_nvlist_20261013_r01"
paths = ["verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
         "vitis/run_s2b_visibility_probe.py", "verification/test_s2b_visibility_probe.py"]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {p: sha(initial_run / ("before_" + Path(p).name)) for p in paths}
after = {p: sha(root / p) for p in paths}
for p in paths:
    (run / ("after_" + Path(p).name)).write_bytes((root / p).read_bytes())
sdk = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")
original = root / "report/evidence/S2B-T19/cache_probe_20261013_r02/jtag_result.json"
rows = json.loads(original.read_text(encoding="utf-8"))["calls"]
row = [r for r in rows if r["api"] == "cpu1.rrd.pc"][-1]
(run / "actual_cpu1_rrd_r02.json").write_text(json.dumps({"source": str(original),
    "source_sha256": sha(original), "row": row}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
command = [sys.executable, "-X", "utf8", "-B", "-m", "unittest",
           "verification.test_s2b_board_jtag", "verification.test_s2b_visibility_probe", "-v"]
if len(sys.argv) > 2:
    command = [sys.executable, "-X", "utf8", "-B", "-m", "unittest",
               "verification.test_s2b_board_acceptance", "verification.test_s2b_csr_board_acceptance",
               "verification.test_s2b_board_transport", "-v"]
config = {"baseline": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
    "before_source_sha256": before, "after_source_sha256": after, "command": command,
    "cwd": str(root), "python_version": sys.version, "python_sha256": sha(Path(sys.executable)),
    "sdk_target_path": str(sdk), "sdk_target_sha256": sha(sdk), "actual_hardware_calls": 0,
    "run_count": 1, "peak_memory_bytes": None,
    "fixture_directory": str(cache), "prelaunch_shell_failure": {
        "exit_code": 1, "output": " PY : -c: line 1: syntax error near unexpected token `newline'\n PY : -c: line 1: `/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -B - <<'\n",
        "meaning": "此前heredoc引号在宿主shell解析时失败，未启动Python或回归。"}}
(run / "run_metadata_before.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
env = os.environ.copy()
env.update(TEMP=str(cache), TMP=str(cache), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
if len(sys.argv) > 2 and sys.argv[2] == "consumer_dependencies":
    dependencies = Path(r"C:\Users\22061\AppData\Local\Programs\Python\Python312\Lib\site-packages")
    if not dependencies.is_dir() or not (dependencies / "cv2/__init__.py").is_file():
        raise FileNotFoundError("既有cv2依赖精确路径不正确")
    env["PYTHONPATH"] = str(dependencies)
    config["additional_dependency_path"] = str(dependencies)
    config["cv2_init_sha256"] = sha(dependencies / "cv2/__init__.py")
    (run / "run_metadata_before.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
start = time.monotonic()
with (run / "unittest.stdout.log").open("xb") as out, (run / "unittest.stderr.log").open("xb") as err:
    result = subprocess.run(command, cwd=root, env=env, stdout=out, stderr=err)
config.update(exit_code=result.returncode, elapsed_seconds=time.monotonic() - start,
              after_run_source_sha256={p: sha(root / p) for p in paths})
(run / "run_result.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"exit_code": result.returncode, "elapsed_seconds": config["elapsed_seconds"]}, ensure_ascii=False))
sys.exit(result.returncode)
