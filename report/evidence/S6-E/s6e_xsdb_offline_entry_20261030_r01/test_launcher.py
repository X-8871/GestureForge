"""只运行当前Python的纯本机Job回归，不启动任何厂商工具。"""

import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

import launcher as L

TMP = Path(r"D:\codex-worktrees\w6\tmp\stage6\s6e_xsdb_offline_entry_20261030_r01")
RUN = TMP / ("selftest_" + time.strftime("%Y%m%d_%H%M%S"))
RESULTS = []


class AssignFailure(L.Native):
    def assign(self, job, process):
        raise OSError("injected assignment failure before ResumeThread")


class CleanupFailure(L.Native):
    def __init__(self):
        super().__init__()
        self.handles = []
        self.k.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
        self.k.OpenProcess.restype = W.HANDLE

    def terminate_job(self, job):
        # 仅对Job报告的本轮PID打开只读同步句柄；不使用PID进行结束操作。
        for pid in self.pids(job):
            handle = self.checked(self.k.OpenProcess(0x100000, False, pid), "OpenProcess(test observation)")
            self.handles.append(handle)
        raise OSError("injected TerminateJobObject failure; last-handle-close must kill tree")


class LauncherTests(unittest.TestCase):
    def run_case(self, name, fixture="ok", timeout=3, api=None):
        argv = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--fixture", fixture]
        result = L.run_argv(argv, RUN, RUN / name, timeout, api=api)
        RESULTS.append({"case": name, "result": result})
        return result

    def test_01_static_and_exact_probe(self):
        before = dict(os.environ)
        plan = L.offline_plan(L.HERE)
        self.assertEqual(before, dict(os.environ))
        self.assertIn("/v:off", plan["argv"])
        self.assertEqual(L.PROBE.read_bytes(), L.PROBE_BYTES)
        self.assertTrue(all(item["hash_basis"] == "worktree_disk" for item in plan["tool_bindings"]))
        self.assertNotIn("connect", L.PROBE.read_text(encoding="utf-8"))
        self.assertNotIn("PATH", L.offline_environment(RUN)["PATH"])

    def test_02_success(self):
        result = self.run_case("success")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["root_exit_code"], 0)
        self.assertTrue(result["assigned"] and result["resumed"])
        self.assertEqual(result["job_samples"][-1]["ActiveProcesses"], 0)

    def test_03_nonzero(self):
        result = self.run_case("nonzero", "nonzero")
        self.assertEqual(result["status"], "NONZERO_EXIT")
        self.assertEqual(result["root_exit_code"], 7)

    def test_04_marker_missing(self):
        result = self.run_case("missing_marker", "missing")
        self.assertEqual(result["status"], "PATCHLEVEL_MARKER_MISSING")

    def test_05_timeout_descendants(self):
        result = self.run_case("timeout_tree", "tree", timeout=1)
        self.assertEqual(result["status"], "TIMEOUT")
        self.assertGreaterEqual(result["job_samples"][-1]["TotalProcesses"], 3)
        self.assertEqual(result["job_samples"][-1]["ActiveProcesses"], 0)
        self.assertEqual(result["root_exit_code_after_cleanup"], 124)
        self.assertLess(result["elapsed_seconds"], 5)

    def test_06_assignment_failure_never_resumes(self):
        result = self.run_case("assignment_failure", api=AssignFailure())
        self.assertEqual(result["status"], "LAUNCH_OR_CLEANUP_ERROR")
        self.assertFalse(result["resumed"])
        self.assertFalse(result["assigned"])
        self.assertEqual((RUN / "assignment_failure/stdout.bin").read_bytes(), b"")
        self.assertEqual(result["root_exit_code_after_cleanup"], 125)
        self.assertTrue(result["cleanup_confirmed"])

    def test_07_cleanup_error_fail_closed_and_last_handle_kills(self):
        api = CleanupFailure()
        result = self.run_case("cleanup_failure", "tree", timeout=1, api=api)
        self.assertEqual(result["status"], "CLEANUP_UNCONFIRMED")
        self.assertTrue(result["job_handle_closed"])
        self.assertGreaterEqual(len(api.handles), 3)
        try:
            for handle in api.handles:
                self.assertEqual(api.k.WaitForSingleObject(handle, 1000), L.WAIT_OBJECT_0)
        finally:
            for handle in api.handles:
                api.k.CloseHandle(handle)
        result["test_only_all_observed_handles_terminated"] = True

    def test_08_early_root_exit_still_kills_child(self):
        result = self.run_case("early_root", "early")
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["job_samples"][-1]["TotalProcesses"], 2)
        self.assertEqual(result["job_samples"][-1]["ActiveProcesses"], 0)

    def test_09_cleanup_failure_overrides_other_success(self):
        result = {"cleanup_confirmed": False, "errors": [], "timed_out": False, "root_exit_code": 0}
        self.assertEqual(L.classify(result, b"8.6.17\n"), "CLEANUP_UNCONFIRMED")

    def test_10_cmd_quoting_with_spaces(self):
        batch = RUN / "mock entry with spaces.bat"
        script = RUN / "mock probe with spaces.txt"
        script.write_text("纯本机占位参数\n", encoding="utf-8")
        batch.write_text('@echo off\n"' + sys.executable + '" -B -X utf8 "' +
                         str(Path(__file__).resolve()) + '" --fixture ok\nexit /b %ERRORLEVEL%\n', encoding="utf-8")
        plan = L.controlled_cmd_plan(batch, script, RUN)
        result = L.run_job(plan["application"], plan["command_line"], RUN,
                           L.offline_environment(RUN), RUN / "cmd_quoting", 3)
        RESULTS.append({"case": "cmd_quoting", "plan": plan, "result": result})
        self.assertEqual(result["status"], "PASS")
        self.assertGreaterEqual(result["job_samples"][-1]["TotalProcesses"], 2)

    def test_11_cmd_metacharacters_rejected(self):
        for character in '%!^&|<>"\r\n':
            with self.assertRaises(ValueError):
                L.controlled_cmd_plan(Path(str(L.BAT) + character), L.PROBE, RUN)

    def test_12_timeout_bounds(self):
        for timeout in (0, -1, 40.01, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                L.run_job(sys.executable, "", RUN, {}, RUN / "invalid", timeout)


def fixture(name):
    if name == "leaf":
        print("leaf", flush=True)
        time.sleep(60)
    elif name in ("tree", "middle", "early"):
        child_kind = "middle" if name == "tree" else "leaf"
        subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()),
                          "--fixture", child_kind])
        print("8.6.17", flush=True)
        if name != "early":
            time.sleep(60)
    elif name == "nonzero":
        print("8.6.17", flush=True)
        return 7
    elif name == "missing":
        print("no patchlevel", flush=True)
    else:
        print("8.6.17", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--fixture":
        sys.exit(fixture(sys.argv[2]))
    RUN.mkdir(exist_ok=False)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LauncherTests)
    with open(RUN / "unittest.log", "x", encoding="utf-8") as stream:
        report = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    summary = {"status": "PASS" if report.wasSuccessful() else "FAIL", "tests_run": report.testsRun,
               "failures": len(report.failures), "errors": len(report.errors), "run_dir": str(RUN),
               "argv": sys.orig_argv, "cwd": os.getcwd(), "vendor_programs_executed": False,
               "hardware_calls_executed": False, "cases": RESULTS}
    (L.HERE / "selftest_result.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    sys.exit(0 if report.wasSuccessful() else 1)
