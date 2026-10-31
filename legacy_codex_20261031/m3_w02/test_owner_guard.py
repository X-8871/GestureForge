"""覆盖M3租约、端口所有权、步骤和捕获门禁的隔离mock测试。"""

import io
import ctypes
import hashlib
import json
import struct
import subprocess
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

import capture_phase
import hold_hw_server
import owner_guard
import run_step


class Fixture:
    """在系统临时目录中构造不连接硬件的租约与启动记录。"""

    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="m3_owner_guard_")
        self.root = Path(self.temp.name)
        self.run_dir = self.root / "report" / "evidence" / "R03-M3" / "m3_pair_20261031_r03"
        self.run_dir.mkdir(parents=True)
        self.authorization = self.root / "external_approval.txt"
        self.authorization.write_text("外部记录仅作为精确哈希输入。\n", encoding="utf-8")
        self.context = self.run_dir / "context.json"
        self.context.write_text("{}", encoding="utf-8")
        self.lease_file = self.root / "lease.json"
        self.port_bytes = b"3121\n"
        (self.run_dir / "port.txt").write_bytes(self.port_bytes)
        self.starts = "2026-10-31T13:00:00+08:00"
        self.ends = "2026-10-31T13:09:00+08:00"
        self.now = datetime.fromisoformat("2026-10-31T13:01:00+08:00")
        self.lease_data = {
            "schema": owner_guard.LEASE_SCHEMA,
            "lease_id": "M3-20261031-R03",
            "starts_at_utc8": self.starts,
            "ends_at_utc8": self.ends,
            "max_seconds": 520,
            "run_dir": "report/evidence/R03-M3/m3_pair_20261031_r03",
            "authorization_file_path": str(self.authorization),
            "authorization_file_sha256": self.hash_file(self.authorization),
            "context_file": "context.json",
            "context_file_sha256": self.hash_file(self.context),
            "window_id": "window-mock-01",
            "event_id": "event-mock-01",
        }
        self.write_lease()
        self.server_dir = self.run_dir / "server"
        self.server_dir.mkdir()
        self.job_name = "Local\\M3_OWNER_" + ("a" * 32)
        self.started = "2026-10-31T13:00:30+08:00"
        self.start_data = {
            "schema": owner_guard.START_SCHEMA,
            "lease_id": self.lease_data["lease_id"],
            "run_dir": str(self.run_dir),
            "lease_file_path": str(self.lease_file),
            "lease_file_sha256": self.hash_file(self.lease_file),
            "authorization_file_path": str(self.authorization),
            "authorization_file_sha256": self.hash_file(self.authorization),
            "context_file_path": str(self.context),
            "context_file_sha256": self.hash_file(self.context),
            "port": 3121,
            "port_file_sha256": hashlib.sha256(self.port_bytes).hexdigest(),
            "job_name": self.job_name,
            "started_utc8": self.started,
            "budget_seconds": 500,
            "lease_end_utc8": self.ends,
            "execution_gate": owner_guard.LOCAL_GATE_MEANING,
            "initial_readiness": "由总控外部核对；本工具未作声明",
        }
        self.write_start()

    @staticmethod
    def hash_file(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_lease(self):
        self.lease_data["authorization_file_sha256"] = self.hash_file(self.authorization)
        self.lease_data["context_file_sha256"] = self.hash_file(self.context)
        self.lease_file.write_text(
            json.dumps(self.lease_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def write_start(self):
        self.start_data["lease_file_sha256"] = self.hash_file(self.lease_file)
        self.start_data["port_file_sha256"] = self.hash_file(self.run_dir / "port.txt")
        self.start_data["authorization_file_sha256"] = self.hash_file(self.authorization)
        self.start_data["context_file_sha256"] = self.hash_file(self.context)
        (self.server_dir / "server_start.json").write_text(
            json.dumps(self.start_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def execution(self, now=None):
        return owner_guard.load_execution(
            self.lease_file,
            self.root,
            now=now or self.now,
        )

    def close(self):
        self.temp.cleanup()


class OwnerGuardTests(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()

    def tearDown(self):
        self.fx.close()

    def check_owner(self, execution, *, pids=(101,), listeners=(101,), alive=True):
        return owner_guard.verify_owner(
            execution,
            thread_alive=lambda: alive,
            job_pids=lambda _name: list(pids),
            listener_pids=lambda _port: list(listeners),
            loopback_connected=lambda _port: True,
        )

    def owner_proof(self, _execution=None):
        return {
            "job_name": self.fx.job_name,
            "job_pids_before": [101],
            "listener_owning_pids": [101],
            "job_pids_after": [101],
            "loopback_connected": True,
            "thread_alive": True,
        }

    def run_step_fixture(self, step, *, owner_check=None, now=None):
        step_dir = self.fx.run_dir / step
        step_dir.mkdir(exist_ok=True)
        script = step_dir / f"{step}.tcl"
        if not script.exists():
            script.write_text("puts mock\n", encoding="utf-8")

        def runner(argv, _timeout):
            return subprocess.CompletedProcess(
                argv,
                0,
                run_step.MARKERS[step] + b"\n",
                b"",
            )

        return run_step.execute_step(
            step,
            self.fx.lease_file,
            root=self.fx.root,
            runner=runner,
            owner_check=owner_check or self.owner_proof,
            now=now or self.fx.now,
        )

    def capture_fixture(self, phase, *, owner_check=None, now=None):
        def capture_fn(**kwargs):
            out_dir = Path(kwargs["out_text"])
            out_dir.mkdir()
            manifest_path = out_dir / "capture_manifest.json"
            manifest = {
                "schema": "gestureforge.m3_pair.capture.v2",
                "status": "CAPTURED",
                "phase": kwargs["phase"],
            }
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            digest = Fixture.hash_file(manifest_path)
            (out_dir / "capture_manifest.sha256").write_text(
                f"sha256={digest}\nhash_basis=worktree_disk\nbytes={manifest_path.stat().st_size}\n",
                encoding="utf-8",
            )
            return {
                "status": "CAPTURED",
                "directory": str(out_dir),
                "manifest_sha256": digest,
                "read_sha256": "a" * 64,
            }

        return capture_phase.run_capture_phase(
            self.fx.lease_file,
            phase,
            root=self.fx.root,
            capture_fn=capture_fn,
            owner_check=owner_check or self.owner_proof,
            now=now or self.fx.now,
        )

    def prepare_before_window(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        self.assertEqual(self.run_step_fixture("restore"), 0)

    def test_valid_lease_and_owner_positive_control(self):
        execution = self.fx.execution()
        proof = self.check_owner(execution)
        self.assertEqual(execution.port, 3121)
        self.assertEqual(proof["listener_owning_pids"], [101])

    def test_port_argument_mismatch_rejected_by_start_binding(self):
        (self.fx.run_dir / "port.txt").write_bytes(b"3122\n")
        with self.assertRaisesRegex(owner_guard.GuardError, "端口"):
            self.fx.execution()

    def test_holder_argument_must_match_port_file(self):
        with self.assertRaisesRegex(owner_guard.GuardError, "--port"):
            owner_guard.assert_requested_port(self.fx.run_dir, 3122)
        self.assertEqual(
            owner_guard.assert_requested_port(self.fx.run_dir, 3121)[0],
            3121,
        )

    def test_port_configuration_hash_change_rejected(self):
        (self.fx.run_dir / "port.txt").write_bytes(b"3121\r\n")
        with self.assertRaisesRegex(owner_guard.GuardError, "摘要"):
            self.fx.execution()

    def test_dead_holder_thread_rejected(self):
        with self.assertRaisesRegex(owner_guard.GuardError, "线程"):
            self.check_owner(self.fx.execution(), alive=False)

    def test_job_open_failure_rejected(self):
        def unavailable(_name):
            raise OSError("mock OpenJobObjectW denied")

        with self.assertRaisesRegex(owner_guard.GuardError, "无法以查询权限打开"):
            owner_guard.verify_owner(
                self.fx.execution(),
                thread_alive=lambda: True,
                job_pids=unavailable,
                listener_pids=lambda _port: [101],
                loopback_connected=lambda _port: True,
            )

    def test_port_takeover_by_foreign_pid_rejected(self):
        with self.assertRaisesRegex(owner_guard.GuardError, "不属于本轮Job"):
            self.check_owner(self.fx.execution(), pids=(101,), listeners=(202,))

    def test_job_exit_during_listener_check_rejected(self):
        samples = iter(([101], []))
        with self.assertRaisesRegex(owner_guard.GuardError, "核验期间"):
            owner_guard.verify_owner(
                self.fx.execution(),
                thread_alive=lambda: True,
                job_pids=lambda _name: next(samples),
                listener_pids=lambda _port: [101],
                loopback_connected=lambda _port: True,
            )

    def test_server_close_race_during_owner_check_rejected(self):
        def listener(_port):
            (self.fx.server_dir / "server_close.json").write_text("{}", encoding="utf-8")
            return [101]

        with self.assertRaisesRegex(owner_guard.GuardError, "server_close"):
            owner_guard.verify_owner(
                self.fx.execution(),
                thread_alive=lambda: True,
                job_pids=lambda _name: [101],
                listener_pids=listener,
                loopback_connected=lambda _port: True,
            )

    def test_server_close_record_blocks_clients(self):
        (self.fx.server_dir / "server_close.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(owner_guard.GuardError, "server_close"):
            self.fx.execution()

    def test_authorization_hash_change_rejected(self):
        self.fx.authorization.write_text("授权文件被替换。\n", encoding="utf-8")
        with self.assertRaisesRegex(owner_guard.GuardError, "授权文件SHA-256"):
            self.fx.execution()

    def test_authorization_path_must_be_local_absolute_path(self):
        with self.assertRaisesRegex(owner_guard.GuardError, "无相对跳转的绝对路径"):
            owner_guard._absolute_regular_file(
                r"\\server\share\approval.md",
                "authorization_file_path",
            )

    def test_context_hash_change_rejected(self):
        self.fx.context.write_text('{"changed":true}', encoding="utf-8")
        with self.assertRaisesRegex(owner_guard.GuardError, "context_file的SHA-256"):
            self.fx.execution()

    def test_lease_mutation_after_start_rejected(self):
        self.fx.lease_data["event_id"] = "event-mock-02"
        self.fx.write_lease()
        with self.assertRaisesRegex(owner_guard.GuardError, "lease-file发生变化"):
            self.fx.execution()

    def test_tool_cannot_claim_external_initial_readiness(self):
        self.fx.start_data["initial_readiness"] = "就绪"
        self.fx.write_start()
        with self.assertRaisesRegex(owner_guard.GuardError, "初始就绪声明"):
            self.fx.execution()

    def test_expired_window_and_overlong_lease_rejected(self):
        expired = datetime.fromisoformat("2026-10-31T13:09:00+08:00")
        with self.assertRaisesRegex(owner_guard.GuardError, "有效区间"):
            owner_guard.load_lease(self.fx.lease_file, self.fx.root, now=expired)
        self.fx.lease_data["max_seconds"] = 521
        self.fx.write_lease()
        with self.assertRaisesRegex(owner_guard.GuardError, "520"):
            owner_guard.load_lease(self.fx.lease_file, self.fx.root, now=self.fx.now)

    def test_lease_duration_over_nine_minutes_rejected(self):
        self.fx.lease_data["ends_at_utc8"] = "2026-10-31T13:09:01+08:00"
        self.fx.write_lease()
        with self.assertRaisesRegex(owner_guard.GuardError, "9分钟"):
            owner_guard.load_lease(self.fx.lease_file, self.fx.root, now=self.fx.now)

    def test_naive_or_non_utc8_lease_time_rejected(self):
        self.fx.lease_data["starts_at_utc8"] = "2026-10-31T13:00:00"
        self.fx.write_lease()
        with self.assertRaisesRegex(owner_guard.GuardError, "明确UTC\\+8"):
            owner_guard.load_lease(self.fx.lease_file, self.fx.root, now=self.fx.now)

    def test_lease_must_not_use_r02_preparation_run(self):
        self.fx.lease_data["run_dir"] = "report/evidence/R03-M3/m3_pair_20261031_r02"
        self.fx.write_lease()
        with self.assertRaisesRegex(owner_guard.GuardError, "r01/r02"):
            owner_guard.load_lease(self.fx.lease_file, self.fx.root, now=self.fx.now)

    def test_cleanup_failure_is_not_reported_as_success(self):
        bad = {
            "cleanup_confirmed": False,
            "job_handle_closed": False,
            "root_wait_after_job_close": 258,
        }
        good = {
            "cleanup_confirmed": True,
            "job_handle_closed": True,
            "root_wait_after_job_close": 0,
        }
        self.assertFalse(owner_guard.close_succeeded(True, bad, True))
        self.assertTrue(owner_guard.close_succeeded(True, good, True))
        good_with_error = {**good, "errors": ["mock cleanup diagnostic"]}
        self.assertFalse(owner_guard.close_succeeded(True, good_with_error, True))

    def test_close_record_write_oserror_fails_but_preserves_cleanup_result(self):
        result = {
            "cleanup_confirmed": True,
            "job_handle_closed": True,
            "root_wait_after_job_close": 0,
        }
        output = io.StringIO()
        with (
            patch.object(
                hold_hw_server,
                "_write_json_new",
                side_effect=OSError("mock disk full"),
            ),
            redirect_stdout(output),
        ):
            exit_code, close_status = hold_hw_server._finish_close(
                self.fx.server_dir,
                result,
                True,
                True,
            )
        reported = json.loads(output.getvalue())
        self.assertEqual(exit_code, 2)
        self.assertEqual(close_status, "FAILED_CLOSE")
        self.assertEqual(reported["status"], "FAILED_CLOSE")
        self.assertEqual(reported["cleanup_status"], "CLEANUP_CONFIRMED")
        self.assertIs(reported["cleanup_confirmed"], True)
        self.assertEqual(reported["close_record_write_status"], "FAILED")
        self.assertIn("mock disk full", reported["close_record_write_error"])
        self.assertNotIn("CLOSED_BY_REQUEST", output.getvalue())

    def test_named_job_query_uses_query_only_access_and_closes_handle(self):
        calls = {}

        class FakeFunction:
            def __init__(self, function):
                self.function = function
                self.argtypes = None
                self.restype = None

            def __call__(self, *args):
                return self.function(*args)

        class FakeKernel:
            pass

        def open_job(access, inherit, name):
            calls["access"] = access
            calls["inherit"] = inherit
            calls["name"] = name
            return 77

        def query_job(handle, info_class, buffer, size, returned):
            calls["query"] = (handle, info_class, size)
            payload = struct.pack("<IIQQ", 2, 2, 101, 202)
            ctypes.memmove(buffer, payload, len(payload))
            return 1

        def close_handle(handle):
            calls["closed"] = handle
            return 1

        fake = FakeKernel()
        fake.OpenJobObjectW = FakeFunction(open_job)
        fake.QueryInformationJobObject = FakeFunction(query_job)
        fake.CloseHandle = FakeFunction(close_handle)
        with patch.object(owner_guard.ctypes, "WinDLL", return_value=fake):
            pids = owner_guard.query_named_job_pids(self.fx.job_name)
        self.assertEqual(pids, [101, 202])
        self.assertEqual(calls["access"], 0x0004)
        self.assertIs(calls["inherit"], False)
        self.assertEqual(calls["name"], self.fx.job_name)
        self.assertEqual(calls["query"][1], 3)
        self.assertEqual(calls["closed"], 77)

    def test_holder_refuses_existing_named_job(self):
        calls = {}

        class FakeKernel:
            def CreateJobObjectW(self, security_attributes, name):
                calls["name"] = name
                return 88

            def CloseHandle(self, handle):
                calls["closed"] = handle
                return 1

        job_name = "Local\\M3_OWNER_" + ("b" * 32)
        named = hold_hw_server.NamedKernel(FakeKernel(), job_name)
        with (
            patch.object(hold_hw_server.ctypes, "set_last_error"),
            patch.object(hold_hw_server.ctypes, "get_last_error", return_value=183),
        ):
            with self.assertRaises(FileExistsError):
                named.CreateJobObjectW(None, None)
        self.assertEqual(calls["name"], job_name)
        self.assertEqual(calls["closed"], 88)

    def test_cim_query_returns_empty_list_for_free_port(self):
        completed = subprocess.CompletedProcess(
            ["powershell.exe"],
            0,
            stdout="[]\n",
            stderr="",
        )
        with patch.object(owner_guard.subprocess, "run", return_value=completed) as invoke:
            self.assertEqual(owner_guard.query_listener_pids(3121), [])
        command = invoke.call_args.args[0][-1]
        self.assertIn("Get-NetTCPConnection", command)
        self.assertIn("-State Listen -LocalPort 3121", command)

    def test_step_uses_bound_port_and_mock_runner(self):
        setup_dir = self.fx.run_dir / "setup"
        setup_dir.mkdir()
        (setup_dir / "setup.tcl").write_text("puts mock\n", encoding="utf-8")
        calls = []

        def runner(argv, timeout):
            calls.append((argv, timeout))
            return subprocess.CompletedProcess(
                argv,
                0,
                run_step.MARKERS["setup"] + b"\n",
                b"",
            )

        rc = run_step.execute_step(
            "setup",
            self.fx.lease_file,
            root=self.fx.root,
            runner=runner,
            owner_check=self.owner_proof,
            now=self.fx.now,
        )
        record = json.loads((setup_dir / "step_result.json").read_text(encoding="utf-8"))
        self.assertEqual(rc, 0)
        self.assertEqual(record["port"], 3121)
        self.assertEqual(record["timeout_seconds"], 90)
        self.assertEqual(len(calls), 1)

    def test_step_postcheck_failure_downgrades_result(self):
        setup_dir = self.fx.run_dir / "setup"
        setup_dir.mkdir()
        (setup_dir / "setup.tcl").write_text("puts mock\n", encoding="utf-8")
        proofs = iter(({"listener_owning_pids": [101]}, RuntimeError("mock Job died")))

        def owner_check(_execution):
            value = next(proofs)
            if isinstance(value, Exception):
                raise value
            return value

        result = subprocess.CompletedProcess(
            [],
            0,
            run_step.MARKERS["setup"] + b"\n",
            b"",
        )
        rc = run_step.execute_step(
            "setup",
            self.fx.lease_file,
            root=self.fx.root,
            runner=lambda _argv, _timeout: result,
            owner_check=owner_check,
            now=self.fx.now,
        )
        record = json.loads((setup_dir / "step_result.json").read_text(encoding="utf-8"))
        self.assertEqual(rc, 2)
        self.assertEqual(record["status"], "FAIL")
        self.assertIn("mock Job died", record["owner_postcheck_error"])

    def test_capture_wrapper_checks_owner_before_and_after_mock_capture(self):
        self.prepare_before_window()
        rc = self.capture_fixture("before")
        record = json.loads(
            (self.fx.run_dir / "capture_before_guard.json").read_text(encoding="utf-8")
        )
        self.assertEqual(rc, 0)
        self.assertEqual(record["port"], 3121)
        self.assertEqual(record["timeout_seconds"], 120)
        self.assertEqual(record["status"], "PASS_CAPTURE_WRAPPER")
        self.assertTrue(record["test_fixture_only"])

    def test_capture_postcheck_failure_downgrades_result(self):
        self.prepare_before_window()
        self.assertEqual(self.capture_fixture("before"), 0)
        self.assertEqual(self.run_step_fixture("event"), 0)
        proofs = iter(({"listener_owning_pids": [101]}, RuntimeError("mock port takeover")))

        def owner_check(_execution):
            value = next(proofs)
            if isinstance(value, Exception):
                raise value
            return value

        rc = capture_phase.run_capture_phase(
            self.fx.lease_file,
            "after",
            root=self.fx.root,
            capture_fn=lambda **kwargs: self._capture_output(kwargs),
            owner_check=owner_check,
            now=self.fx.now,
        )
        record = json.loads(
            (self.fx.run_dir / "capture_after_guard.json").read_text(encoding="utf-8")
        )
        self.assertEqual(rc, 2)
        self.assertEqual(record["status"], "FAIL_CAPTURE_WRAPPER")
        self.assertIn("mock port takeover", record["owner_postcheck_error"])

    def test_capture_reserves_close_budget(self):
        self.prepare_before_window()
        near_end = datetime.fromisoformat("2026-10-31T13:08:40+08:00")
        called = []
        with self.assertRaisesRegex(owner_guard.GuardError, "剩余租期"):
            capture_phase.run_capture_phase(
                self.fx.lease_file,
                "before",
                root=self.fx.root,
                capture_fn=lambda **_kwargs: called.append(True),
                owner_check=lambda _execution: {"listener_owning_pids": [101]},
                now=near_end,
            )
        self.assertEqual(called, [])

    def test_protocol_positive_control_setup_restore_before_event_after(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        self.assertEqual(self.run_step_fixture("restore"), 0)
        self.assertEqual(self.capture_fixture("before"), 0)
        self.assertEqual(self.run_step_fixture("event"), 0)
        self.assertEqual(self.capture_fixture("after"), 0)
        for path in (
            self.fx.run_dir / "setup" / "step_result.json",
            self.fx.run_dir / "restore" / "step_result.json",
            self.fx.run_dir / "capture_before_guard.json",
            self.fx.run_dir / "event" / "step_result.json",
            self.fx.run_dir / "capture_after_guard.json",
        ):
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(record["test_fixture_only"])

    def test_before_requires_setup_and_restore_before_owner_or_capture(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "restore.*缺失"):
            capture_phase.run_capture_phase(
                self.fx.lease_file,
                "before",
                root=self.fx.root,
                capture_fn=lambda **_kwargs: calls.append("capture"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "capture_before").exists())
        self.assertFalse((self.fx.run_dir / "capture_before_guard.json").exists())

    def test_restore_rejects_before_output_directory_even_without_guard(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        (self.fx.run_dir / "capture_before").mkdir()
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "before.*已有输出"):
            run_step.execute_step(
                "restore",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())

    def test_restore_rejects_failed_partial_before_guard(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        (self.fx.run_dir / "capture_before_guard.json").write_text(
            '{"status":"FAIL_CAPTURE_WRAPPER"', encoding="utf-8"
        )
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "before.*已有输出"):
            run_step.execute_step(
                "restore",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())

    def test_event_requires_before_and_after_must_wait_for_event(self):
        self.prepare_before_window()
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "before.*缺失"):
            run_step.execute_step(
                "event",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertEqual(self.capture_fixture("before"), 0)
        with self.assertRaisesRegex(owner_guard.GuardError, "event.*缺失"):
            capture_phase.run_capture_phase(
                self.fx.lease_file,
                "after",
                root=self.fx.root,
                capture_fn=lambda **_kwargs: calls.append("capture"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "capture_after").exists())
        self.assertFalse((self.fx.run_dir / "capture_after_guard.json").exists())

    def test_setup_rejects_any_later_phase_artifact_before_owner(self):
        (self.fx.run_dir / "capture_after").mkdir()
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "after.*已有输出"):
            run_step.execute_step(
                "setup",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "setup" / "step_result.json").exists())

    def test_predecessor_receipt_job_identity_mismatch_rejected(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        path = self.fx.run_dir / "setup" / "step_result.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["job_name"] = "Local\\M3_OWNER_" + ("c" * 32)
        path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "job_name"):
            run_step.execute_step(
                "restore",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())

    def test_predecessor_receipt_all_execution_identity_fields_are_bound(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        path = self.fx.run_dir / "setup" / "step_result.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        wrong_values = {
            "lease_id": "M3-other-lease",
            "lease_file_path": str(self.fx.root / "other-lease.json"),
            "lease_file_sha256": "0" * 64,
            "run_dir": str(self.fx.root / "other-run"),
            "port": 3122,
            "port_file_sha256": "f" * 64,
            "job_name": "Local\\M3_OWNER_" + ("d" * 32),
        }
        calls = []
        for field, wrong in wrong_values.items():
            with self.subTest(field=field):
                record = {**original, field: wrong}
                path.write_text(json.dumps(record) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(owner_guard.GuardError, field):
                    run_step.execute_step(
                        "restore",
                        self.fx.lease_file,
                        root=self.fx.root,
                        runner=lambda *_args: calls.append("runner"),
                        owner_check=lambda _execution: calls.append("owner"),
                        now=self.fx.now,
                    )
                self.assertEqual(calls, [])
                self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())
        path.write_text(json.dumps(original) + "\n", encoding="utf-8")

    def test_failed_setup_receipt_cannot_authorize_restore(self):
        self.assertEqual(self.run_step_fixture("setup", owner_check=lambda _execution: {
            "job_name": self.fx.job_name,
            "job_pids_before": [101],
            "listener_owning_pids": [101],
            "job_pids_after": [101],
            "loopback_connected": True,
            "thread_alive": True,
        }), 0)
        setup_path = self.fx.run_dir / "setup" / "step_result.json"
        setup = json.loads(setup_path.read_text(encoding="utf-8"))
        setup["status"] = "FAIL"
        setup["semantic_exit_code"] = 2
        setup_path.write_text(json.dumps(setup) + "\n", encoding="utf-8")
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "setup.*真实PASS"):
            run_step.execute_step(
                "restore",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())

    def test_fixture_receipt_never_unlocks_real_runner(self):
        self.assertEqual(self.run_step_fixture("setup"), 0)
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "仅为fixture"):
            run_step.execute_step(
                "restore",
                self.fx.lease_file,
                root=self.fx.root,
                runner=run_step.m3_pair._run_xsdb,
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "restore" / "step_result.json").exists())
        with self.assertRaisesRegex(owner_guard.GuardError, "仅为fixture"):
            capture_phase.run_capture_phase(
                self.fx.lease_file,
                "before",
                root=self.fx.root,
                capture_fn=capture_phase.m3_pair.capture,
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "capture_before").exists())

    def test_capture_receipt_identity_mismatch_blocks_event_before_owner(self):
        self.prepare_before_window()
        self.assertEqual(self.capture_fixture("before"), 0)
        path = self.fx.run_dir / "capture_before_guard.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["lease_file_sha256"] = "0" * 64
        path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "lease_file_sha256"):
            run_step.execute_step(
                "event",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "event" / "step_result.json").exists())

    def test_event_rejects_after_half_package_before_owner(self):
        self.prepare_before_window()
        self.assertEqual(self.capture_fixture("before"), 0)
        (self.fx.run_dir / "capture_after").mkdir()
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "after.*已有输出"):
            run_step.execute_step(
                "event",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])
        self.assertFalse((self.fx.run_dir / "event" / "step_result.json").exists())

    def test_close_is_available_for_cleanup_at_any_stage(self):
        self.assertEqual(self.run_step_fixture("close"), 0)
        calls = []
        with self.assertRaisesRegex(owner_guard.GuardError, "close.*已有输出"):
            run_step.execute_step(
                "setup",
                self.fx.lease_file,
                root=self.fx.root,
                runner=lambda *_args: calls.append("runner"),
                owner_check=lambda _execution: calls.append("owner"),
                now=self.fx.now,
            )
        self.assertEqual(calls, [])

    def _capture_output(self, kwargs):
        out_dir = Path(kwargs["out_text"])
        out_dir.mkdir()
        manifest_path = out_dir / "capture_manifest.json"
        manifest = {
            "schema": "gestureforge.m3_pair.capture.v2",
            "status": "CAPTURED",
            "phase": kwargs["phase"],
        }
        manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
        digest = Fixture.hash_file(manifest_path)
        (out_dir / "capture_manifest.sha256").write_text(
            f"sha256={digest}\nhash_basis=worktree_disk\nbytes={manifest_path.stat().st_size}\n",
            encoding="utf-8",
        )
        return {
            "status": "CAPTURED",
            "directory": str(out_dir),
            "manifest_sha256": digest,
            "read_sha256": "a" * 64,
        }


if __name__ == "__main__":
    unittest.main(verbosity=2)
