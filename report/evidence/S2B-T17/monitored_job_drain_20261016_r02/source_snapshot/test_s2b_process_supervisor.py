#!/usr/bin/env python3
"""用微型父子进程验证S2B Job与资源监督的失败关闭行为。"""
from __future__ import annotations

import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import s2b_process_supervisor as supervisor
import test_s2b_control_csr_rtl as runner


GIB = 1024 ** 3


@unittest.skipUnless(os.name == "nt", "真实Job Object进程夹具仅在Windows运行")
class S2BProcessSupervisorTests(unittest.TestCase):
    """验证本Run进程树归属、RAM门槛与失败状态映射。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="s2b-job-test-")
        self.root = Path(self.temp.name)
        self.log_path = self.root / "supervisor.log"
        self.log_stream = self.log_path.open("w", encoding="utf-8")

    def tearDown(self):
        self.log_stream.close()
        self.temp.cleanup()

    def _memory_high(self):
        return 12 * GIB, 16 * GIB

    def _run(self, command, memory_reader=None, **kwargs):
        timeout_seconds = kwargs.pop("timeout_seconds", 2.0)
        sample_interval_seconds = kwargs.pop("sample_interval_seconds", 0.05)
        max_sample_gap_seconds = kwargs.pop("max_sample_gap_seconds", 1.0)
        drain_timeout_seconds = kwargs.pop("drain_timeout_seconds", 2.0)
        return supervisor.supervise_process(
            name="fixture", command=command, cwd=str(self.root),
            environment=os.environ.copy(), output_stream=self.log_stream,
            timeout_seconds=timeout_seconds, memory_reader=memory_reader or self._memory_high,
            sample_interval_seconds=sample_interval_seconds,
            max_sample_gap_seconds=max_sample_gap_seconds,
            drain_timeout_seconds=drain_timeout_seconds, **kwargs)

    def test_normal_parent_child_finishes_and_job_is_empty(self):
        child = "import time; time.sleep(0.10)"
        parent = "import subprocess,sys; p=subprocess.Popen([sys.executable,'-c',sys.argv[1]]); sys.exit(p.wait())"
        result = self._run([sys.executable, "-c", parent, child])
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["cleanup_confirmed"])
        proof = result["cleanup"]["empty_job_proof"]
        self.assertEqual([], proof["job_pids_before"])
        self.assertEqual([], proof["job_pids_after"])
        self.assertEqual(0, proof["accounting_after"]["active_processes"])
        self.assertTrue(proof["root_signaled"])
        self.assertGreaterEqual(proof["accounting_after"]["total_processes"], 2)

    def test_child_naturally_exits_during_monitored_root_exit_drain(self):
        child = "import time; time.sleep(0.55)"
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); sys.exit(0)"
        samples = {"count": 0}

        def memory_reader():
            samples["count"] += 1
            return self._memory_high()

        result = self._run([sys.executable, "-c", parent, child],
            memory_reader=memory_reader, timeout_seconds=3.0,
            sample_interval_seconds=0.05, drain_timeout_seconds=1.5)
        self.assertEqual("PASS", result["status"], result)
        drain = result["cleanup"]["natural_drain"]
        self.assertEqual("PASS_EMPTY_JOB", drain["status"])
        self.assertGreaterEqual(drain["elapsed_seconds"], 0.25)
        self.assertGreater(drain["resource_samples_at_end"], drain["resource_samples_at_start"])
        self.assertGreaterEqual(samples["count"], 3)
        proof = result["cleanup"]["empty_job_proof"]
        self.assertEqual([], proof["job_pids_before"])
        self.assertEqual([], proof["job_pids_after"])
        self.assertEqual(0, proof["accounting_after"]["active_processes"])
        self.assertTrue(proof["root_signaled"])

    def test_persistent_child_times_out_then_only_own_job_is_terminated(self):
        child = "import time; time.sleep(30)"
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); sys.exit(0)"
        result = self._run([sys.executable, "-c", parent, child],
            timeout_seconds=3.0, sample_interval_seconds=0.05,
            drain_timeout_seconds=0.25)
        self.assertEqual("FAIL_JOB_NOT_EMPTY", result["status"], result)
        self.assertTrue(result["cleanup"]["termination_requested"])
        self.assertTrue(result["cleanup_confirmed"])
        drain = result["cleanup"]["natural_drain"]
        self.assertEqual("FAIL_JOB_NOT_EMPTY", drain["status"])
        self.assertTrue(drain["last_job_pids"])
        proof = result["cleanup"]["empty_job_proof"]
        self.assertEqual([], proof["job_pids_after"])
        self.assertEqual(0, proof["accounting_after"]["active_processes"])

    def test_low_memory_during_natural_drain_fails_closed(self):
        drain_started = {"value": False}
        original_wait = supervisor._wait_for_empty_job
        child = "import time; time.sleep(30)"
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); sys.exit(0)"
        samples = {"count": 0}

        def memory_reader():
            samples["count"] += 1
            if drain_started["value"]:
                return GIB, 16 * GIB
            return self._memory_high()

        def mark_natural_drain(*args, **options):
            if options.get("allow_root_exit_drain"):
                drain_started["value"] = True
            return original_wait(*args, **options)

        with mock.patch.object(supervisor, "_wait_for_empty_job", side_effect=mark_natural_drain):
            result = self._run([sys.executable, "-c", parent, child],
                memory_reader=memory_reader, timeout_seconds=3.0,
                sample_interval_seconds=0.05, drain_timeout_seconds=1.0)
        self.assertEqual("FAIL_RESOURCE_STOP", result["status"], result)
        self.assertEqual("FAIL_RESOURCE_STOP", result["cleanup"]["natural_drain"]["status"])
        self.assertTrue(result["cleanup"]["termination_requested"])
        self.assertTrue(result["cleanup_confirmed"])
        self.assertGreaterEqual(samples["count"], 2)

    def test_memory_query_error_during_natural_drain_fails_closed(self):
        drain_started = {"value": False}
        original_wait = supervisor._wait_for_empty_job
        child = "import time; time.sleep(30)"
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); sys.exit(0)"

        def memory_reader():
            if drain_started["value"]:
                raise OSError("模拟自然排空期间的内存查询错误")
            return self._memory_high()

        def mark_natural_drain(*args, **options):
            if options.get("allow_root_exit_drain"):
                drain_started["value"] = True
            return original_wait(*args, **options)

        with mock.patch.object(supervisor, "_wait_for_empty_job", side_effect=mark_natural_drain):
            result = self._run([sys.executable, "-c", parent, child],
                memory_reader=memory_reader, timeout_seconds=3.0,
                sample_interval_seconds=0.05, drain_timeout_seconds=1.0)
        self.assertEqual("FAIL_RESOURCE_QUERY", result["status"], result)
        self.assertEqual("FAIL_RESOURCE_QUERY", result["cleanup"]["natural_drain"]["status"])
        self.assertTrue(result["cleanup"]["termination_requested"])
        self.assertTrue(result["cleanup_confirmed"])

    def test_overall_wall_timeout_bounds_natural_drain(self):
        child = "import time; time.sleep(30)"
        parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); time.sleep(0.5); sys.exit(0)"
        result = self._run([sys.executable, "-c", parent, child],
            timeout_seconds=2.0, sample_interval_seconds=0.05,
            drain_timeout_seconds=5.0)
        self.assertEqual("FAIL_TIMEOUT", result["status"], result)
        self.assertTrue(result["timed_out"])
        self.assertEqual("FAIL_TIMEOUT", result["cleanup"]["natural_drain"]["status"])
        self.assertTrue(result["cleanup"]["termination_requested"])
        self.assertTrue(result["cleanup_confirmed"])

    def test_low_memory_terminates_own_job_and_preserves_external_sentinel(self):
        marker = self.root / "child-started.txt"
        sentinel = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        samples = {"count": 0}

        def memory_reader():
            samples["count"] += 1
            if marker.exists():
                return GIB, 16 * GIB
            return self._memory_high()

        child = "import time; time.sleep(30)"
        parent = "import subprocess,sys; from pathlib import Path; subprocess.Popen([sys.executable,'-c',sys.argv[1]]); Path(sys.argv[2]).write_text('ready',encoding='utf-8'); time.sleep(30)"
        parent = "import time; " + parent
        try:
            result = self._run([sys.executable, "-c", parent, child, str(marker)],
                memory_reader=memory_reader)
            self.assertEqual("FAIL_RESOURCE_STOP", result["status"])
            self.assertTrue(result["cleanup_confirmed"])
            self.assertTrue(result["cleanup"]["termination_requested"])
            self.assertIsNone(sentinel.poll())
            self.assertGreaterEqual(samples["count"], 2)
            self.assertFalse(runner.run_succeeded(result))
        finally:
            if sentinel.poll() is None:
                sentinel.terminate()
                sentinel.wait(timeout=5)

    def test_memory_query_exception_fails_closed(self):
        calls = {"count": 0}

        def memory_reader():
            calls["count"] += 1
            if calls["count"] == 1:
                return self._memory_high()
            raise OSError("模拟GlobalMemoryStatusEx查询错误")

        result = self._run([sys.executable, "-c", "import time; time.sleep(30)"],
            memory_reader=memory_reader)
        self.assertEqual("FAIL_RESOURCE_QUERY", result["status"])
        self.assertTrue(result["cleanup_confirmed"])
        self.assertFalse(runner.run_succeeded(result))

    def test_delayed_memory_sample_fails_closed(self):
        calls = {"count": 0}

        def memory_reader():
            calls["count"] += 1
            if calls["count"] == 1:
                return self._memory_high()
            time.sleep(0.20)
            return self._memory_high()

        result = self._run([sys.executable, "-c", "import time; time.sleep(30)"],
            memory_reader=memory_reader, max_sample_gap_seconds=0.10)
        self.assertEqual("FAIL_RESOURCE_SAMPLE_GAP", result["status"])
        self.assertTrue(result["cleanup_confirmed"])
        self.assertFalse(runner.run_succeeded(result))

    def test_low_preflight_never_launches_root(self):
        marker = self.root / "must-not-exist.txt"
        result = self._run([sys.executable, "-c",
            "from pathlib import Path; Path(sys.argv[1]).write_text('started')", str(marker)],
            memory_reader=lambda: (9 * GIB, 16 * GIB))
        self.assertEqual("BLOCKED_RESOURCE_PREFLIGHT", result["status"])
        self.assertFalse(result["launch_attempted"])
        self.assertFalse(marker.exists())
        self.assertEqual("BLOCKED", runner.manifest_run_status(result))

    def test_nonfinite_time_parameters_fail_before_job_creation(self):
        parameter_names = (
            "timeout_seconds", "sample_interval_seconds",
            "max_sample_gap_seconds", "drain_timeout_seconds",
        )
        invalid_values = (math.nan, math.inf, -math.inf)
        for parameter_name in parameter_names:
            for invalid_value in invalid_values:
                with self.subTest(parameter=parameter_name, value=repr(invalid_value)):
                    memory_reader = mock.Mock(
                        side_effect=AssertionError("配置校验前不应查询内存"))
                    command = [sys.executable, "-c", "raise SystemExit(99)"]
                    with mock.patch.object(supervisor, "_load_job_guard") as load_guard:
                        result = self._run(
                            command, memory_reader=memory_reader,
                            **{parameter_name: invalid_value})
                    self.assertEqual("FAIL_SUPERVISOR_CONFIG", result["status"])
                    self.assertFalse(result["launch_attempted"])
                    self.assertFalse(result["cleanup"]["job_created"])
                    self.assertIsNone(result["resource_monitor"]["preflight"])
                    self.assertEqual([parameter_name],
                        result["resource_monitor"]["invalid_time_parameters"])
                    self.assertEqual(0, memory_reader.call_count)
                    load_guard.assert_not_called()

    def test_caller_specific_thresholds_are_recorded(self):
        result = self._run([sys.executable, "-c", "print('threshold fixture')"],
            memory_reader=lambda: (6 * GIB, 16 * GIB),
            start_floor_bytes=4 * GIB, stop_floor_bytes=2 * GIB)
        self.assertEqual("PASS", result["status"])
        self.assertEqual(4 * GIB, result["resource_monitor"]["start_floor_bytes"])
        self.assertEqual(2 * GIB, result["resource_monitor"]["stop_floor_bytes"])

    def test_manifest_never_trusts_exit_code_zero_alone(self):
        base = {"status": "PASS", "exit_code": 0, "timed_out": False,
            "cleanup_confirmed": True}
        self.assertEqual("PASS", runner.manifest_run_status(base))
        for record in (
            {**base, "status": "FAIL_EXIT"},
            {**base, "timed_out": True},
            {**base, "cleanup_confirmed": False},
        ):
            self.assertEqual("FAIL", runner.manifest_run_status(record), record)

    def test_timeout_is_never_pass_even_when_cleanup_is_confirmed(self):
        result = self._run([sys.executable, "-c", "import time; time.sleep(30)"],
            timeout_seconds=0.15)
        self.assertEqual("FAIL_TIMEOUT", result["status"])
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["cleanup_confirmed"])
        self.assertEqual("FAIL", runner.manifest_run_status(result))
        self.assertFalse(runner.run_succeeded(result))

    def test_unconfirmed_cleanup_after_timeout_cannot_pass(self):
        with mock.patch.object(supervisor, "_wait_for_empty_job",
                               side_effect=supervisor.SupervisorError("模拟Job清空读回失败")):
            result = self._run([sys.executable, "-c", "import time; time.sleep(30)"],
                timeout_seconds=0.15)
        self.assertEqual("FAIL_TIMEOUT_CLEANUP_UNCONFIRMED", result["status"], result)
        self.assertTrue(result["timed_out"])
        self.assertFalse(result["cleanup_confirmed"])
        self.assertEqual("FAIL", runner.manifest_run_status(result))
        self.assertFalse(runner.run_succeeded(result))


if __name__ == "__main__":
    unittest.main()
