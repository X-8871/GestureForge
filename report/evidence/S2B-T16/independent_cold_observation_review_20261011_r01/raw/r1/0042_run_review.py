"""独立审查命令驱动：限制内存与时间，保存原生退出码及原始日志。"""
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import types
import unittest

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
SDK = Path("D:/Xilinx/2026.1/Vitis/cli/xsdb/target.py")
MANIFEST = ROOT / "report/evidence/S2B-T16/cold_observation_20261011_r01/delivery_manifest.json"
SOURCES = ["verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py", "verification/test_s2b_cold_observation.py"]


def sha(path):
    """按原始字节绑定输入，不解释路径。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    """只创建本轮隔离产物。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def execute_suite():
    """只改测试临时落点，不改变生产代码和测试判断。"""
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(RUN))
    tempfile.tempdir = str(RUN / "scratch")
    import verification.test_s2b_board_jtag as original
    import verification.test_s2b_cold_observation as cold
    import verification.test_s2b_csr_board_acceptance as csr
    import independent_cases
    csr.TEST_PARENT = RUN / "scratch"
    path = ROOT / "verification/test_s2b_visibility_probe.py"
    code = path.read_text(encoding="utf-8")
    needle = 'parent=REAL_ROOT/"tmp/2B/S2B-T19"'
    assert code.count(needle) == 2
    code = code.replace(needle, 'parent=Path(os.environ["COLD_REVIEW_RUN"])/"scratch"')
    module = types.ModuleType("verification.independent_visibility_tests")
    module.__file__ = str(path)
    module.__package__ = "verification"
    module.os = os
    sys.modules[module.__name__] = module
    exec(compile(code, str(path), "exec"), module.__dict__)
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(mod) for mod in (original, cold, module, csr, independent_cases))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if "--child" in sys.argv:
    raise SystemExit(execute_suite())

assert ROOT.name == "FPGA_Competition" and SDK.is_file() and MANIFEST.is_file()
(RUN / "scratch").mkdir()
os.environ["COLD_REVIEW_RUN"] = str(RUN)
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["TEMP"] = os.environ["TMP"] = str(RUN / "scratch")
baseline = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
assert baseline == "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
binding_results = [{"path": row["path"], "expected": row["sha256"], "actual": sha(ROOT / row["path"])} for row in manifest["files"]]
assert all(row["expected"] == row["actual"] for row in binding_results)
before = {path: sha(ROOT / path) for path in SOURCES}
write("binding_audit.json", {"manifest_sha256": sha(MANIFEST), "files": binding_results, "sdk_sha256": sha(SDK), "source_commit": baseline})
sdk_lines = SDK.read_text(encoding="utf-8").splitlines()
with (RUN / "sdk_excerpt.txt").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write("\n".join(f"{index + 1}: {sdk_lines[index]}" for index in range(4596, 4671)) + "\n")
started = time.monotonic()
command = [sys.executable, "-B", str(Path(__file__).absolute()), "--child"]


class MemoryCounters(ctypes.Structure):
    """Windows原生工作集计数。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


api = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
api.argtypes = (wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD)
api.restype = wintypes.BOOL
peak, samples, query_errors, stop = 0, 0, 0, None
with (RUN / "tests_stdout.log").open("xb") as out, (RUN / "tests_stderr.log").open("xb") as err:
    child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
    while child.poll() is None:
        counters = MemoryCounters(); counters.cb = ctypes.sizeof(counters)
        if api(wintypes.HANDLE(int(child._handle)), ctypes.byref(counters), counters.cb):
            samples += 1; peak = max(peak, counters.PeakWorkingSetSize)
        else:
            query_errors += 1
        if peak >= 300 * 1024 * 1024 or time.monotonic() - started > 240:
            stop = "内存或240秒停止条件达到"
            child.kill()
            break
        time.sleep(0.05)
    native_rc = child.wait()
elapsed = time.monotonic() - started
checks = []
for mode in ("evidence", "inputs"):
    argv = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(MANIFEST)]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=30)
    (RUN / f"{mode}_stdout.log").write_bytes(result.stdout)
    (RUN / f"{mode}_stderr.log").write_bytes(result.stderr)
    checks.append({"mode": mode, "command_argv": argv, "native_exit_code": result.returncode, "status": "PASS" if result.returncode == 0 else "FAIL"})
assert before == {path: sha(ROOT / path) for path in SOURCES}
write("execution_receipt.json", {"review_status": "CHANGES_REQUIRED", "source_commit": baseline, "source_sha256": before, "command_argv": command, "native_exit_code": native_rc, "elapsed_seconds": elapsed, "resource": {"peak_working_set_bytes": peak, "samples": samples, "query_errors": query_errors, "sample_interval_seconds": 0.05, "budget_bytes": 300 * 1024 * 1024, "descendant_peak": "新导入子进程峰值未独立测量"}, "stop_reason": stop, "stage_checks": checks, "tool_versions": {"Python": platform.python_version()}, "test_path_isolation": {"T19": "两处tmp父目录重定向至本Run/scratch；其余原源码及判断不变", "T20": "TEST_PARENT设为本Run/scratch", "tempfile": "全部TEMP/TMP和tempfile.tempdir设为本Run/scratch"}, "hardware": {"status": "NOT_RUN", "calls": 0, "exit_code": None}, "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat()})
print(json.dumps({"native_exit_code": native_rc, "elapsed_seconds": elapsed, "peak_bytes": peak, "checks": checks}, ensure_ascii=False))
raise SystemExit(native_rc)
