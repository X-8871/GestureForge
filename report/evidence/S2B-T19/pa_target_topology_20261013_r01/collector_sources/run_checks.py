"""保存离线目标拓扑专项与既有消费者回归的原生结果，不导入SDK或操作硬件。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[4]
evidence = root / "report/evidence/S2B-T19/pa_target_topology_20261013_r01"
sources = ["verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
           "vitis/run_s2b_visibility_probe.py", "verification/test_s2b_visibility_probe.py"]
def hashes():
    """按实际源码原字节绑定，不把旧证据源码当成本轮实现。"""
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sources}

mode = sys.argv[1]
modules = (["verification.test_s2b_board_jtag", "verification.test_s2b_visibility_probe"] if mode.startswith("special")
           else ["verification.test_s2b_board_acceptance", "verification.test_s2b_csr_board_acceptance", "verification.test_s2b_board_transport"])
if mode.startswith("focused"):
    modules = ["verification.test_s2b_visibility_probe.CsrDebugMapTests",
               "verification.test_s2b_visibility_probe.SdkBoundaryTests.test_official_public_targets_reselects_current_id_without_mutating_previous_id",
               "verification.test_s2b_visibility_probe.SdkBoundaryTests.test_actual_module_and_method_source_gate",
               "verification.test_s2b_visibility_probe.LifecycleTests.test_full_mock_lifecycle_after_loadhw_pa_pair_and_fpga_renumbering"]
command = [sys.executable, "-X", "utf8", "-B", "-m", "unittest", *modules, "-v"]
before = hashes()
env = dict(os.environ)
env["TEMP"] = env["TMP"] = str(Path(__file__).parent)
env["PYTHONPATH"] = str(root) + os.pathsep + r"C:\Users\22061\AppData\Local\Programs\Python\Python312\Lib\site-packages"
start = time.monotonic()
result = subprocess.run(command, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
elapsed = time.monotonic() - start
for name, raw in (("stdout", result.stdout), ("stderr", result.stderr)):
    (evidence / (mode + "_" + name + ".log")).write_bytes(raw)
receipt = {"baseline": "c8742858fbb23331763358775daa44dafb95db94", "before_source_sha256": before,
           "after_source_sha256": hashes(), "command": command, "cwd": str(root), "python_version": sys.version,
           "python_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(), "exit_code": result.returncode,
           "elapsed_seconds": elapsed, "run_count": 1, "actual_hardware_calls": 0, "peak_memory_bytes": None,
           "additional_dependency_path": r"C:\Users\22061\AppData\Local\Programs\Python\Python312\Lib\site-packages",
           "fixture_directory": str(Path(__file__).parent), "limitations": ["仅离线mock回归；公共unloadhw真实未返回原因未知。"]}
(evidence / (mode + "_run_result.json")).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"mode": mode, "exit_code": result.returncode, "elapsed_seconds": elapsed}, ensure_ascii=False))
print(result.stderr.decode("utf-8", errors="replace")[-6000:])
raise SystemExit(result.returncode)
