"""验证冻结DCP direct bitgen runner的本机Win32生命周期门禁。"""
import ctypes
import datetime
import json
import os
import secrets
import struct
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PARENT = ROOT / "report" / "evidence" / "S2B-T17"
EVIDENCE_ROOT_ENV = "S15_DIRECT_BITGEN_EVIDENCE_ROOT"
sys.path.insert(0, str(ROOT / "verification"))

if os.name == "nt":
    import s15_job_guard as job_guard
    import s15_direct_vivado_bitgen as controller
else:
    job_guard = None
    controller = None


def _effective_fixture_evidence_parent():
    override = os.environ.get(EVIDENCE_ROOT_ENV)
    parent = Path(override) if override else EVIDENCE_PARENT
    parent.mkdir(parents=True, exist_ok=True)
    return parent


def _new_run_dir(label):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_parent = _effective_fixture_evidence_parent()
    for _ in range(32):
        target = evidence_parent / f"direct_bitgen_fixture_{label}_{stamp}_{secrets.token_hex(4)}"
        try:
            target.mkdir()
        except FileExistsError:
            continue
        return target
    raise RuntimeError("不能为fixture分配唯一证据目录")


def _write_json(path, payload):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def _fixture_argv(marker_path, exit_code):
    source = (
        "import os,pathlib,sys,time; "
        "pathlib.Path(sys.argv[1]).write_text('RESUMED:'+os.environ.get('S15_FIXTURE_ENV','missing'),encoding='utf-8'); "
        "time.sleep(0.15); "
        "raise SystemExit(int(sys.argv[2]))"
    )
    executable = str(Path(sys.executable).resolve())
    return executable, [executable, "-c", source, str(marker_path), str(exit_code)]


@unittest.skipUnless(os.name == "nt", "非Windows环境：显式SKIP，不能声称本机Win32 fixture通过")
class DirectSpawnFixtureTests(unittest.TestCase):
    def test_job_pid_decoder_handles_both_ulong_ptr_widths_and_count_boundaries(self):
        for width, format_code, values in (
            (4, "I", (0xFFFFFFFF, 0x10203)),
            (8, "Q", (0x100001234, 0x200005678)),
        ):
            exact = struct.pack("<II", 2, 2) + struct.pack("<" + format_code * 2, *values)
            self.assertEqual(tuple(sorted(values)), job_guard._decode_job_pid_list(exact, width))
            self.assertEqual((), job_guard._decode_job_pid_list(struct.pack("<II", 0, 0), width))
            too_small = struct.pack("<II", 2, 2) + struct.pack("<" + format_code, values[0])
            with self.assertRaises(job_guard.GateBlocked):
                job_guard._decode_job_pid_list(too_small, width)
            mismatch = struct.pack("<II", 2, 1) + struct.pack("<" + format_code, values[0])
            with self.assertRaises(job_guard.GateBlocked):
                job_guard._decode_job_pid_list(mismatch, width)
            duplicate = struct.pack("<II", 2, 2) + struct.pack("<" + format_code * 2, values[0], values[0])
            with self.assertRaises(job_guard.GateBlocked):
                job_guard._decode_job_pid_list(duplicate, width)
        with self.assertRaises(job_guard.GateBlocked):
            job_guard._decode_job_pid_list(struct.pack("<II", 0, 0), 16)

    def test_real_create_suspended_assign_resume_and_exit_closure(self):
        run_dir = _new_run_dir("real_lifecycle")
        marker = run_dir / "resumed.marker"
        executable, argv = _fixture_argv(marker, 23)
        job = job_guard.JobObject(kill_on_close=True)
        environment = dict(os.environ)
        environment["S15_FIXTURE_ENV"] = "unicode-环境-value"
        try:
            try:
                child = job_guard.launch_suspended_root(job, executable, argv, cwd=str(ROOT), environment=environment)
            except job_guard.SuspendedRootError as error:
                receipt = {
                    "status": "REAL_ASSIGN_BLOCKED_FAIL_CLOSED" if "AssignProcessToJobObject" in repr(error.primary_error) else "REAL_LIFECYCLE_FAILED",
                    "platform": sys.platform,
                    "executable": executable,
                    "argv": argv,
                    "primary_error": repr(error.primary_error),
                    "events": error.events,
                    "cleanup_errors": error.cleanup_errors,
                    "marker_exists": marker.exists(),
                }
                _write_json(run_dir / "fixture_result.json", receipt)
                self.assertFalse(any(row.get("event") == "RESUME_THREAD" for row in error.events))
                self.assertFalse(marker.exists())
                self.assertEqual([], error.cleanup_errors)
                if receipt["status"] == "REAL_ASSIGN_BLOCKED_FAIL_CLOSED":
                    self.skipTest(f"本机外层Job拒绝嵌套Assign；真实错误及fail-closed清理保留于 {run_dir}")
                self.fail(f"实际Win32生命周期未完成，原异常保留于 {run_dir}: {error!r}")
            closure = child.wait_and_close(timeout_seconds=10.0)
            receipt = {
                "status": "PASS_REAL_WIN32_LIFECYCLE",
                "platform": sys.platform,
                "executable": executable,
                "argv": argv,
                "pid": child.pid,
                "identity": child.identity,
                "events": closure["events"],
                "final": closure["final"],
                "marker_text": marker.read_text(encoding="utf-8"),
            }
            _write_json(run_dir / "fixture_result.json", receipt)
            self.assertEqual(23, closure["final"]["root_native_handle_exit_code"])
            self.assertEqual("RESUMED:unicode-环境-value", receipt["marker_text"])
            self.assertEqual([child.pid], [row["pid"] for row in receipt["final"]["member_readbacks"]])
            self.assertTrue(any(row.get("event") == "PRE_RESUME_CLOSED" for row in closure["events"]))
            self.assertTrue(any(row.get("event") == "RESUME_THREAD" for row in closure["events"]))
        finally:
            if not job.closed:
                job.close()

    def test_injected_assign_failure_never_resumes_and_reaps_root(self):
        run_dir = _new_run_dir("assign_failure")
        marker = run_dir / "resumed.marker"
        executable, argv = _fixture_argv(marker, 0)
        job = job_guard.JobObject(kill_on_close=True)

        def fail_assign(_job_handle, _process_handle):
            ctypes.set_last_error(job_guard.ERROR_ACCESS_DENIED)
            return False

        with mock.patch.object(job_guard, "_api_assign_process", side_effect=fail_assign):
            with self.assertRaises(job_guard.SuspendedRootError) as caught:
                job_guard.launch_suspended_root(job, executable, argv, cwd=str(ROOT))
        error = caught.exception
        receipt = {
            "status": "PASS_INJECTED_ASSIGN_FAILURE_FAIL_CLOSED",
            "primary_error": repr(error.primary_error),
            "events": error.events,
            "cleanup_errors": error.cleanup_errors,
            "marker_exists": marker.exists(),
            "job_closed": job.closed,
        }
        _write_json(run_dir / "fixture_result.json", receipt)
        self.assertFalse(any(row.get("event") == "RESUME_THREAD" for row in error.events))
        self.assertTrue(any(row.get("event") == "ROOT_REAPED" for row in error.events))
        self.assertFalse(marker.exists())
        self.assertEqual([], error.cleanup_errors)
        self.assertTrue(job.closed)


    def test_member_closure_failure_terminates_assigned_suspended_root(self):
        run_dir = _new_run_dir("member_closure_failure")
        marker = run_dir / "resumed.marker"
        executable, argv = _fixture_argv(marker, 0)
        job = job_guard.JobObject(kill_on_close=True)

        def fail_membership(_self):
            raise job_guard.GateBlocked("fixture注入稳定成员集合不闭合")

        with mock.patch.object(job_guard.JobObject, "_verify_ready_membership", fail_membership):
            with self.assertRaises(job_guard.SuspendedRootError) as caught:
                job_guard.launch_suspended_root(job, executable, argv, cwd=str(ROOT))
        error = caught.exception
        receipt = {
            "status": "PASS_INJECTED_MEMBER_FAILURE_FAIL_CLOSED",
            "primary_error": repr(error.primary_error),
            "events": error.events,
            "cleanup_errors": error.cleanup_errors,
            "marker_exists": marker.exists(),
            "job_closed": job.closed,
        }
        _write_json(run_dir / "fixture_result.json", receipt)
        self.assertFalse(any(row.get("event") == "RESUME_THREAD" for row in error.events))
        self.assertTrue(any(row.get("event") == "JOB_REAPED" for row in error.events))
        self.assertFalse(marker.exists())
        self.assertEqual([], error.cleanup_errors)
        self.assertTrue(job.closed)


class FrozenTclStaticTests(unittest.TestCase):
    def test_tcl_only_opens_frozen_checkpoint_and_writes_one_exact_bit_target(self):
        source = (ROOT / "verification" / "s15_frozen_dcp_bitgen.tcl").read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertEqual(1, source.count("open_checkpoint $dcp"))
        self.assertEqual(1, source.count("write_bitstream $bitfile"))
        for forbidden in ("set_part ", "launch_runs", "synth_design", "opt_design", "place_design", "route_design", "write_checkpoint", "-force"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("xc7z020clg400-2", source)
        self.assertIn("s2b_inference_wrapper_postroute_physopt.bit", source)
        self.assertIn("[file join $inputs_dir $expected_dcp_name]", source)
        self.assertIn("[file normalize [info script]]", source)
        self.assertIn("[file dirname $run_dir]", source)


@unittest.skipUnless(os.name == "nt", "Win32输入锁测试仅支持Windows")
class ControllerSafetyUnitTests(unittest.TestCase):
    def test_input_copy_lock_blocks_write_replace_delete_without_launch(self):
        run_dir = _new_run_dir("input_share_lock")
        dcp_source = run_dir / "approved_source.dcp"
        tcl_source = run_dir / "approved_source.tcl"
        original_dcp = b"approved-frozen-dcp-bytes"
        with dcp_source.open("xb") as stream:
            stream.write(original_dcp)
        with tcl_source.open("xb") as stream:
            stream.write(b"approved Tcl source bytes\n")
        facts = {
            "dcp_path": str(dcp_source),
            "dcp_sha256": controller._sha256(dcp_source),
            "tcl_source_path": str(tcl_source),
            "tcl_source_sha256": controller._sha256(tcl_source),
        }
        locks = []
        input_path = None
        renamed_path = None
        failures = {}
        with mock.patch.object(controller.job_guard, "launch_suspended_root") as launch:
            locks = controller._prepare_run_inputs(run_dir, facts)
            input_path = Path(facts["dcp_copy_path"])
            tcl_copy = Path(facts["tcl_copy_path"])
            renamed_path = input_path.with_name("unexpected_rename.bin")
            self.assertEqual(facts["dcp_sha256"], controller._sha256(input_path))
            self.assertEqual(facts["tcl_source_sha256"], controller._sha256(tcl_copy))
            try:
                for name, action in (
                    ("write_open", lambda: os.open(input_path, os.O_WRONLY)),
                    ("replace", lambda: os.replace(input_path, renamed_path)),
                    ("delete", lambda: os.unlink(input_path)),
                ):
                    try:
                        result = action()
                    except OSError as error:
                        failures[name] = {"type": type(error).__name__, "winerror": getattr(error, "winerror", None), "message": str(error)}
                    else:
                        if name == "write_open":
                            os.close(result)
                        elif name == "replace" and renamed_path.exists():
                            os.replace(renamed_path, input_path)
                        elif name == "delete" and not input_path.exists():
                            with input_path.open("xb") as stream:
                                stream.write(original_dcp)
                        failures[name] = {"unexpected_success": True}
                launch.assert_not_called()
            finally:
                for input_lock in reversed(locks):
                    input_lock.close()
        receipt = {
            "status": "PASS_WIN32_INPUT_READ_LOCK" if all(not item.get("unexpected_success") for item in failures.values()) else "FAIL_WIN32_INPUT_READ_LOCK",
            "target": str(input_path),
            "share_mode": "FILE_SHARE_READ only; write/delete sharing omitted",
            "mutation_attempts": failures,
            "input_exists_after_lock": input_path.exists(),
            "input_sha256_after_lock": controller._sha256(input_path),
            "vivado_launch_calls": launch.call_count,
        }
        _write_json(run_dir / "fixture_result.json", receipt)
        self.assertEqual({"write_open", "replace", "delete"}, set(failures))
        self.assertTrue(all(not item.get("unexpected_success") for item in failures.values()))
        self.assertTrue(receipt["input_exists_after_lock"])
        launch.assert_not_called()

    def test_only_vivado_log_or_journal_growth_resets_no_progress(self):
        helper_activity = {
            "stdout": {"appended_bytes": 11},
            "stderr": {"appended_bytes": 7},
            "tcl_progress": {"appended_bytes": 32},
        }
        self.assertFalse(controller._has_real_log_progress(helper_activity))
        self.assertTrue(controller._has_real_log_progress({"vivado_log": {"appended_bytes": 1}}))
        self.assertTrue(controller._has_real_log_progress({"vivado_journal": {"appended_bytes": 1}}))

    def test_success_requires_all_artifacts_and_rejects_each_missing_entry(self):
        required = ("vivado_log", "vivado_journal", "stdout", "stderr", "monitor", "tcl_progress", "bitstream")
        empty_sha = controller.hashlib.sha256(b"").hexdigest().upper()
        artifacts = {
            name: {
                "exists": True,
                "size_bytes": 1 if name not in ("stdout", "stderr") else 0,
                "sha256": empty_sha if name in ("stdout", "stderr") else "A" * 64,
            }
            for name in required
        }
        progress = [{"event": "write_bitstream_complete", "detail": "1"}]
        monitor = [{"event": "sample"}]
        self.assertTrue(controller._validate_success_artifacts(artifacts, progress, monitor)["valid"])
        for name in required:
            missing = dict(artifacts)
            missing.pop(name)
            result = controller._validate_success_artifacts(missing, progress, monitor)
            self.assertFalse(result["valid"], name)
            self.assertIn(f"missing:{name}", result["issues"])
        empty_bit = dict(artifacts)
        empty_bit["bitstream"] = dict(artifacts["bitstream"], size_bytes=0)
        self.assertFalse(controller._validate_success_artifacts(empty_bit, progress, monitor)["valid"])

    def test_cleanup_lock_and_manifest_failures_force_nonzero_exit(self):
        class FixtureLock:
            def __init__(self, error=None):
                self.error = error

            def close(self):
                if self.error is not None:
                    raise self.error

        class FixtureWriter:
            def __init__(self, manifest, fail_writes=0):
                self.manifest = manifest
                self.fail_writes = fail_writes
                self.write_calls = 0
                self.close_calls = 0

            def write(self):
                self.write_calls += 1
                if self.write_calls <= self.fail_writes:
                    raise OSError("injected final manifest write failure")

            def close(self):
                self.close_calls += 1

        run_dir = _new_run_dir("final_cleanup_failures")
        receipt = {}

        lock_manifest = {"status": "BITGEN_COMPLETE_SOFTWARE_ONLY", "stop_reason": None}
        lock_writer = FixtureWriter(lock_manifest)
        lock_exit = controller._finish_controller_cleanup(
            lock_writer,
            lock_manifest,
            [FixtureLock(OSError("injected input lock close failure"))],
            0,
        )
        receipt["lock_close_failure"] = {
            "run_exit_code": lock_exit,
            "status": lock_manifest["status"],
            "stop_reason": lock_manifest["stop_reason"],
            "lock_errors": lock_manifest["input_copy_lock_release_errors"],
            "manifest_write_calls": lock_writer.write_calls,
        }
        self.assertEqual(1, lock_exit)
        self.assertEqual("FAILED_OR_INCOMPLETE", lock_manifest["status"])
        self.assertIn("INPUT_COPY_LOCK_RELEASE_FAILED", lock_manifest["stop_reason"])
        self.assertEqual(1, lock_writer.write_calls)

        write_manifest = {"status": "BITGEN_COMPLETE_SOFTWARE_ONLY", "stop_reason": None}
        write_writer = FixtureWriter(write_manifest, fail_writes=2)
        write_exit = controller._finish_controller_cleanup(write_writer, write_manifest, [], 0)
        receipt["final_manifest_write_failure"] = {
            "run_exit_code": write_exit,
            "status": write_manifest["status"],
            "stop_reason": write_manifest["stop_reason"],
            "finalization_errors": write_manifest["finalization_errors"],
            "manifest_write_calls": write_writer.write_calls,
        }
        self.assertEqual(1, write_exit)
        self.assertEqual("FAILED_OR_INCOMPLETE", write_manifest["status"])
        self.assertIn("FINAL_MANIFEST_WRITE_FAILED", write_manifest["stop_reason"])
        self.assertEqual(2, write_writer.write_calls)

        success_manifest = {"status": "BITGEN_COMPLETE_SOFTWARE_ONLY", "stop_reason": None}
        success_writer = FixtureWriter(success_manifest)
        success_exit = controller._finish_controller_cleanup(success_writer, success_manifest, [FixtureLock()], 0)
        receipt["success_control"] = {
            "run_exit_code": success_exit,
            "status": success_manifest["status"],
            "manifest_write_calls": success_writer.write_calls,
        }
        self.assertEqual(0, success_exit)
        self.assertEqual("BITGEN_COMPLETE_SOFTWARE_ONLY", success_manifest["status"])
        self.assertEqual(1, success_writer.write_calls)

        receipt["status"] = "PASS_FAIL_CLOSED_FINAL_CLEANUP_CONTRACT"
        _write_json(run_dir / "fixture_result.json", receipt)

    def test_input_copy_uses_injected_evidence_root_and_precedes_vivado(self):
        expected_root = os.path.normcase(os.path.abspath(str(_effective_fixture_evidence_parent())))
        self.assertEqual(expected_root, os.path.normcase(controller._effective_evidence_root()))
        base_run = _new_run_dir("evidence_override_base")
        isolated_root = base_run / "reviewer_isolated_root"
        isolated_root.mkdir()
        with mock.patch.dict(os.environ, {EVIDENCE_ROOT_ENV: str(isolated_root)}):
            self.assertEqual(
                os.path.normcase(os.path.abspath(str(isolated_root))),
                os.path.normcase(controller._effective_evidence_root()),
            )
            _run_id, injected_run = controller._create_unique_run_dir(str(isolated_root))
            self.assertEqual(isolated_root, injected_run.parent)
        run_dir = _new_run_dir("argv_copy_paths")
        facts = {
            "vivado_executable_path": str(ROOT / "fixture-vivado.exe"),
            "tcl_copy_path": str(run_dir / "inputs" / controller.TCL_COPY_NAME),
            "dcp_copy_path": str(run_dir / "inputs" / controller.DCP_COPY_NAME),
            "evidence_root": str(run_dir.parent),
        }
        argv, _outputs = controller._expected_argv(run_dir, facts)
        self.assertEqual(facts["tcl_copy_path"], argv[argv.index("-source") + 1])
        tclargs = argv.index("-tclargs") + 1
        self.assertEqual(facts["dcp_copy_path"], argv[tclargs])
        self.assertEqual(facts["evidence_root"], argv[tclargs + 3])
        source = (ROOT / "verification" / "s15_direct_vivado_bitgen.py").read_text(encoding="utf-8")
        prepare_index = source.index("input_locks = _prepare_run_inputs(run_dir, facts)")
        launch_index = source.index("child = job_guard.launch_suspended_root(")
        self.assertLess(prepare_index, launch_index)


if __name__ == "__main__":
    unittest.main(verbosity=2)
