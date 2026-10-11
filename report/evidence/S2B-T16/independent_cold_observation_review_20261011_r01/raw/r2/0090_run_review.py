"""R2独立审查驱动；只写隔离目录并保留原生退出码、内存和原始日志。"""
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta, timezone
import difflib
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
BASELINE = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
EXPECTED_HEAD = "90c87b773fe06684797f6bb3cca2da078a4d49aa"
SDK = Path("D:/Xilinx/2026.1/Vitis/cli/xsdb/target.py")
MANIFEST = ROOT / "report/evidence/S2B-T16/cold_observation_20261011_r02/delivery_manifest.json"
EXPECTED = {
    "verification/s2b_board_jtag.py": "1ce01c810715e6c20f2952d3488ebb6ce8f7792861075e1a25bbc1f91db7651b",
    "verification/test_s2b_board_jtag.py": "c35a08dce67c761596d36296c0abb89c08fcb98f9bfde46160f6e6cfa1a30c3f",
    "verification/test_s2b_cold_observation.py": "ce1af9db23fcd6a07c2c31df0b3c1f9186aaf1f756e34af68d2323f5cb0a38f1",
    "vitis/run_s2b_visibility_probe.py": "bc9c94b0d49769ea08941d0cda252038c2b5390f342439d960dcede690c52aa2",
    "verification/test_s2b_visibility_probe.py": "84d04910efc9e4f051c6439550349a21910c0a77d22720f5afed3e2a998b7e4d",
}


def sha(path):
    """绑定文件原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    """仅创建当前Run的新文件，禁止覆盖。"""
    target = RUN / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def raw(name, data):
    """保持原字节并拒绝覆盖。"""
    target = RUN / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(data)


def execute_suite():
    """仅重定向测试临时目录，原断言和生产实现保持不变。"""
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(RUN))
    tempfile.tempdir = str(RUN / "scratch")
    import verification.test_s2b_board_jtag as original
    import verification.test_s2b_cold_observation as cold
    import verification.test_s2b_csr_board_acceptance as csr
    import independent_cases
    import independent_extra
    csr.TEST_PARENT = RUN / "scratch"
    path = ROOT / "verification/test_s2b_visibility_probe.py"
    code = path.read_text(encoding="utf-8")
    needle = 'parent=REAL_ROOT/"tmp/2B/S2B-T19"'
    assert code.count(needle) == 2
    code = code.replace(needle, 'parent=Path(os.environ["COLD_REVIEW_RUN"])/"scratch"')
    visibility = types.ModuleType("verification.independent_visibility_tests")
    visibility.__file__, visibility.__package__, visibility.os = str(path), "verification", os
    sys.modules[visibility.__name__] = visibility
    exec(compile(code, str(path), "exec"), visibility.__dict__)
    independent_extra.visibility = visibility
    groups = [("T16_original", original), ("T16_cold", cold), ("T19_visibility", visibility),
              ("T20_CSR", csr), ("independent_R1_closure", independent_cases), ("independent_R2_extra", independent_extra)]
    suites = [(name, unittest.defaultTestLoader.loadTestsFromModule(module)) for name, module in groups]
    counts = {name: suite.countTestCases() for name, suite in suites}
    assert [counts[name] for name in ("T16_original", "T16_cold", "T19_visibility", "T20_CSR")] == [56, 17, 19, 33]
    outcomes = []
    class Result(unittest.TextTestResult):
        """记录方法与子用例真实结果。"""
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
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(unittest.TestSuite(suite for _, suite in suites))
    forbidden = [name for name in sys.modules if name == "serial" or name == "xsdb" or name.startswith(("xsdb.", "tcf."))]
    write("test_outcomes.json", {"scope": "MOCK_ONLY_NOT_BOARD", "methods_by_group": counts,
          "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
          "outcomes": outcomes, "remaining_hardware_modules": forbidden, "hardware_calls": 0})
    return 0 if result.wasSuccessful() and not forbidden else 1


if "--child" in sys.argv:
    raise SystemExit(execute_suite())

assert ROOT.name == "FPGA_Competition" and SDK.is_file() and MANIFEST.is_file()
assert sha(MANIFEST) == "f69b69e711259afc6de4fc033a0845a71ba86468b51f99a84a995a6ffb223ce4"
assert {name: sha(ROOT / name) for name in EXPECTED} == EXPECTED
head_before = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
assert head_before == EXPECTED_HEAD
(RUN / "scratch").mkdir()
os.environ.update(COLD_REVIEW_RUN=str(RUN), PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
                  TEMP=str(RUN / "scratch"), TMP=str(RUN / "scratch"))
free_bytes = shutil.disk_usage(ROOT).free
assert free_bytes > 256 * 1024 * 1024
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
bindings = [{"path": row["path"], "expected": row["sha256"], "actual": sha(ROOT / row["path"]),
             "keys_exact": set(row) == {"path", "sha256", "role"}} for row in manifest["files"]]
assert all(row["expected"] == row["actual"] and row["keys_exact"] for row in bindings)
assert all(row["exit_code"] is None for row in manifest["checks"] if row["status"] in ("NOT_RUN", "BLOCKED"))
r1 = ROOT / "tmp/2B/S2B-T16/independent_cold_observation_review_20261011_r01/review_receipt.json"
assert sha(r1) == "e5ea9e4b9c86c0207a103ed0ac6d42270acf1e7351bf0a67fbd3f2705d910d77"
write("binding_audit.json", {"source_baseline": BASELINE, "observed_head": head_before,
      "manifest_sha256": sha(MANIFEST), "files": bindings, "sdk_target_sha256": sha(SDK),
      "r1_receipt_sha256": sha(r1), "source_sha256": EXPECTED,
      "platform_checker": {"scope": "仅核验G1实际快照；该源由S4维护，不归入本任务变更",
      "snapshot_sha256": sha(MANIFEST.parent / "source_snapshot/verification/check_s2b_inference_platform.py")}})
for name in EXPECTED:
    raw("source_snapshot/" + name, (ROOT / name).read_bytes())
    earlier = ROOT / "report/evidence/S2B-T16/cold_observation_20261011_r01/source_snapshot" / name
    if earlier.is_file():
        previous = earlier.read_text(encoding="utf-8")
        previous_label = "R1_snapshot"
    else:
        prior = subprocess.run(["git", "show", BASELINE + ":" + name], cwd=ROOT, capture_output=True)
        raw("source_diffs/" + name.replace("/", "__") + ".git_show.stderr.log", prior.stderr)
        if prior.returncode == 0:
            previous = prior.stdout.decode("utf-8")
            previous_label = "Git_baseline"
        else:
            assert name == "verification/test_s2b_cold_observation.py" and prior.returncode == 128
            previous, previous_label = "", "Git_baseline_absent_new_file"
        write("source_diffs/" + name.replace("/", "__") + ".basis.json",
              {"basis": previous_label, "native_exit_code": prior.returncode,
               "r1_source_bytes": "未提供，不将基线差异声称R1源码差异"})

    difference = "".join(difflib.unified_diff(previous.splitlines(True), (ROOT / name).read_text(encoding="utf-8").splitlines(True),
                                              fromfile=previous_label + "/" + name, tofile="R2/" + name))
    raw("source_diffs/" + name.replace("/", "__") + ".diff", difference.encode("utf-8"))
sdk_lines = SDK.read_text(encoding="utf-8").splitlines()
raw("sdk_excerpt.txt", ("\n".join(f"{i + 1}: {sdk_lines[i]}" for i in range(4596, 4671)) + "\n").encode("utf-8"))
checks = []
for label, argv in [("baseline_diff", ["git", "diff", BASELINE, "--", *EXPECTED]),
                    ("diff_check", ["git", "diff", "--check", "--", *EXPECTED])]:
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=30)
    raw(label + "_stdout.log", result.stdout)
    raw(label + "_stderr.log", result.stderr)
    checks.append({"name": label, "command_argv": argv, "native_exit_code": result.returncode,
                   "status": "PASS" if result.returncode == 0 else "FAIL"})
assert all(row["native_exit_code"] == 0 for row in checks)
command = [sys.executable, "-B", str(Path(__file__).absolute()), "--child"]


class MemoryCounters(ctypes.Structure):
    """Windows原生峰值工作集，不把峰值累加。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
        "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]


api = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
api.argtypes = (wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD)
api.restype = wintypes.BOOL
started = time.monotonic()
peak, samples, errors, stop_reason = 0, 0, 0, None
with (RUN / "tests_stdout.log").open("xb") as out, (RUN / "tests_stderr.log").open("xb") as err:
    child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
    while child.poll() is None:
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if api(wintypes.HANDLE(int(child._handle)), ctypes.byref(counters), counters.cb):
            samples += 1
            peak = max(peak, counters.PeakWorkingSetSize)
        else:
            errors += 1
        if peak >= 300 * 1024 * 1024 or time.monotonic() - started > 240:
            stop_reason = "达到300MiB预算或240秒上限"
            child.kill()
            break
        time.sleep(0.05)
    native_rc = child.wait()
elapsed = time.monotonic() - started
for mode in ("evidence", "inputs"):
    argv = [sys.executable, "-B", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(MANIFEST)]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=30)
    raw(mode + "_stdout.log", result.stdout)
    raw(mode + "_stderr.log", result.stderr)
    checks.append({"name": "stage_" + mode, "command_argv": argv, "native_exit_code": result.returncode,
                   "status": "PASS" if result.returncode == 0 else "FAIL"})
after = {name: sha(ROOT / name) for name in EXPECTED}
assert after == EXPECTED
write("execution_receipt.json", {"source_commit": BASELINE, "observed_head_before": head_before,
      "observed_head_after": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
      "source_sha256_before": EXPECTED, "source_sha256_after": after, "command_argv": command,
      "native_exit_code": native_rc, "elapsed_seconds": elapsed, "run_count": 1,
      "resource": {"peak_working_set_bytes": peak, "samples": samples, "query_errors": errors,
                   "budget_bytes": 314572800, "sample_interval_seconds": 0.05, "free_disk_bytes_before": free_bytes,
                   "descendant_peak": "短暂纯Python导入子进程峰值未独立测量"},
      "stop_reason": stop_reason, "checks": checks, "tool_versions": {"Python": platform.python_version()},
      "hardware": {"status": "NOT_RUN", "calls": 0, "exit_code": None},
      "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat()})
print(json.dumps({"native_exit_code": native_rc, "elapsed_seconds": elapsed, "peak_working_set_bytes": peak,
                  "checks": checks}, ensure_ascii=False))
raise SystemExit(native_rc)
