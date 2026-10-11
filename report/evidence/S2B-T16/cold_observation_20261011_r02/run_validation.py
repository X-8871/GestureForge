"""R2离线回归驱动：首轮同步保存日志、原生退出码与内存采样，不连接设备。"""

import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
SCRATCH = ROOT / "tmp/2B/S2B-T16" / RUN.name / "scratch"
BASELINE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
SOURCES = (
    "verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
    "verification/test_s2b_cold_observation.py", "vitis/run_s2b_visibility_probe.py",
    "verification/test_s2b_visibility_probe.py", "verification/s2b_board_transport.py",
    "verification/check_s2b_ps_smoke_layout.py", "verification/check_stage_delivery.py",
    "verification/s2b_csr_board_acceptance.py", "verification/test_s2b_csr_board_acceptance.py",
    "vitis/s2b_inference_app.c", "src/s2b_control_csr.sv")
INTERFACE = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
PLATFORM = "verification/check_s2b_inference_platform.py"


def sha(path):
    """对文件实际原字节计算SHA。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    """UTF-8创建新证据，拒绝覆盖旧运行。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def child_suite():
    """只重定向MOCK临时落点；既有生产门禁、断言和失败判断保持原样。"""
    sys.path.insert(0, str(ROOT))
    tempfile.tempdir = str(SCRATCH)
    import verification.test_s2b_board_jtag as original
    import verification.test_s2b_cold_observation as cold
    import verification.test_s2b_csr_board_acceptance as csr
    csr.TEST_PARENT = SCRATCH
    path = ROOT / "verification/test_s2b_visibility_probe.py"
    source = path.read_text(encoding="utf-8")
    needle = 'parent=REAL_ROOT/"tmp/2B/S2B-T19"'
    assert source.count(needle) == 2
    source = source.replace(needle, 'parent=Path(os.environ["COLD_R2_SCRATCH"])')
    visibility = types.ModuleType("verification.cold_r2_visibility_tests")
    visibility.__file__, visibility.__package__, visibility.os = str(path), "verification", os
    sys.modules[visibility.__name__] = visibility
    exec(compile(source, str(path), "exec"), visibility.__dict__)
    groups = [("T16_existing", original), ("T16_cold", cold), ("T19", visibility), ("T20", csr)]
    suites = [(name, unittest.defaultTestLoader.loadTestsFromModule(module)) for name, module in groups]
    counts = {name: suite.countTestCases() for name, suite in suites}
    assert counts == {"T16_existing": 56, "T16_cold": 17, "T19": 19, "T20": 33}, counts
    outcomes = []

    class Result(unittest.TextTestResult):
        """记录方法和subTest实际结果；不改变原生unittest执行语义。"""
        def addSuccess(self, test):
            super().addSuccess(test)
            outcomes.append({"id": test.id(), "kind": "method", "status": "PASS"})

        def addFailure(self, test, err):
            super().addFailure(test, err)
            outcomes.append({"id": test.id(), "kind": "method", "status": "FAIL"})

        def addError(self, test, err):
            super().addError(test, err)
            outcomes.append({"id": test.id(), "kind": "method", "status": "ERROR"})

        def addSubTest(self, test, subtest, err):
            super().addSubTest(test, subtest, err)
            outcomes.append({"id": subtest.id(), "kind": "subTest", "status": "PASS" if err is None else "FAIL"})

    sdk = visibility.p.sdk_source_closure()
    write(RUN / "sdk_source_inventory.json", {
        "scope": "仅只读SDK源文件闭包；未导入SDK，不是runtime兼容批准",
        "files": {name: {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}
                  for name, path in sdk.items()}})
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(
        unittest.TestSuite(suite for _, suite in suites))
    write(RUN / "test_case_outcomes.json", {"scope": "MOCK_ONLY_NOT_BOARD", "methods_by_group": counts,
          "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
          "outcomes": outcomes, "hardware_calls": 0})
    return 0 if result.wasSuccessful() else 1


if "--child" in sys.argv:
    raise SystemExit(child_suite())

assert ROOT.name == "FPGA_Competition" and SCRATCH.parent.is_dir() and not SCRATCH.exists()
SCRATCH.mkdir()
before = {name: sha(ROOT / name) for name in SOURCES + (INTERFACE,)}
head_before = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
for name in SOURCES + (PLATFORM,):
    target = RUN / "source_snapshot" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write((ROOT / name).read_bytes())
platform_before = sha(RUN / "source_snapshot" / PLATFORM)
review = ROOT / "tmp/2B/S2B-T16/independent_cold_observation_review_20261011_r01/review_receipt.json"
assert sha(review) == "e5ea9e4b9c86c0207a103ed0ac6d42270acf1e7351bf0a67fbd3f2705d910d77"
with (RUN / "r1_review_receipt.json").open("xb") as stream:
    stream.write(review.read_bytes())
free_bytes = shutil.disk_usage(ROOT).free
assert free_bytes > 256 * 1024 * 1024, "离线回归可用空间不足256MiB"
command = [sys.executable, "-B", str(Path(__file__).absolute()), "--child"]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
           COLD_R2_SCRATCH=str(SCRATCH), TEMP=str(SCRATCH), TMP=str(SCRATCH))


class MemoryCounters(ctypes.Structure):
    """Windows原生峰值工作集统计。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
        "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]


api = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
api.argtypes = (wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD)
api.restype = wintypes.BOOL
started = time.monotonic()
peak, samples, errors, stop_reason = 0, 0, 0, None
with (RUN / "unittest_stdout.log").open("xb") as stdout, (RUN / "unittest_stderr.log").open("xb") as stderr:
    child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    while child.poll() is None:
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if api(wintypes.HANDLE(int(child._handle)), ctypes.byref(counters), counters.cb):
            samples += 1
            peak = max(peak, counters.PeakWorkingSetSize)
        else:
            errors += 1
        if peak >= 300 * 1024 * 1024 or time.monotonic() - started > 240:
            stop_reason = "RSS达到300MiB预算或240秒运行期限"
            child.kill()
            break
        time.sleep(0.05)
    native_rc = child.wait()
elapsed = time.monotonic() - started
after = {name: sha(ROOT / name) for name in before}
head_after = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
diff_command = ["git", "diff", "--check", "--", *SOURCES[:5]]
diff = subprocess.run(diff_command, cwd=ROOT, capture_output=True)
for label, raw in (("stdout", diff.stdout), ("stderr", diff.stderr)):
    with (RUN / ("diff_check_" + label + ".log")).open("xb") as stream:
        stream.write(raw)
drift = [name for name in before if before[name] != after[name]]
record = {"status": "PASS" if native_rc == diff.returncode == 0 and not drift else "FAIL",
          "scope": "MOCK_ONLY_NOT_BOARD", "source_baseline": BASELINE,
          "observed_head_before": head_before, "observed_head_after": head_after,
          "head_note": "根总控仅提交S3证据与STATE/attrs；本任务基线仍为6d3fd856，记录观测HEAD不冒称源码已提交。",
          "command_argv": command, "cwd": str(ROOT), "native_exit_code": native_rc,
          "elapsed_seconds": elapsed, "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
          "source_sha256_before": before, "source_sha256_after": after, "source_drift": drift,
          "platform_checker": {"snapshot_sha256": platform_before, "after_sha256": sha(ROOT / PLATFORM),
                               "note": "S4维护的只读快照；T19 fixture沿用既有mock check_static，不证明真实平台通过。"},
          "diff_command_argv": diff_command, "diff_native_exit_code": diff.returncode,
          "tool_versions": {"Python": platform.python_version(), "XSDB_source": "Vitis2026.1源码只读，未导入SDK"},
          "resource": {"peak_working_set_bytes": peak, "samples": samples, "query_errors": errors,
                       "sample_interval_seconds": 0.05, "budget_bytes": 314572800,
                       "free_disk_bytes_before": free_bytes, "descendant_peak": "短暂纯Python导入子进程峰值未单独测量"},
          "stop_reason": stop_reason, "hardware_calls": 0, "run_count": 1,
          "limitations": ["本轮候选待独立G2；BOARD及完整runtime兼容和真实cache均未执行。",
                          "cold_lifecycle_proven始终false；没有修改epoch、失败锁或控制器标志绕过门禁。"]}
write(RUN / "validation_result.json", record)
print(json.dumps({key: record[key] for key in ("status", "native_exit_code", "elapsed_seconds", "resource")}, ensure_ascii=False))
raise SystemExit(native_rc or diff.returncode or (1 if drift else 0))
