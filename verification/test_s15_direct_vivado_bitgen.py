"""验证冻结DCP direct bitgen runner的本机Win32生命周期门禁。"""
import ctypes
import datetime
import json
import os
import secrets
import struct
import sys
import time
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

    def test_cmd_batch_fixture_preserves_arguments_exit_code_and_job_descendant_closure(self):
        run_dir = _new_run_dir("cmd_batch_fixture")
        fake_bin = run_dir / "fixture_vivado_bin"
        fake_bin.mkdir()
        batch_path = fake_bin / "fixture_launcher.bat"
        args_receipt = run_dir / "batch_args.receipt"
        cwd_after_pushd = run_dir / "cwd_after_pushd.receipt"
        cwd_after_restore = run_dir / "cwd_after_restore.receipt"
        cwd_after_popd = run_dir / "cwd_after_popd.receipt"
        python_executable = str(Path(sys.executable).resolve())
        batch_arguments = [
            "-mode",
            "batch",
            "-log",
            str(run_dir / "fixture.log"),
            "-tclargs",
            "approved-token-alpha",
            "approved-token-beta",
        ]
        script = (
            "@echo off\r\n"
            "setlocal EnableExtensions DisableDelayedExpansion\r\n"
            'set "_RDI_CWD=%cd%"\r\n'
            'pushd "%~dp0"\r\n'
            f'> "{cwd_after_pushd}" echo(%cd%\r\n'
            'cd /d "%_RDI_CWD%"\r\n'
            f'> "{cwd_after_restore}" echo(%cd%\r\n'
            f'> "{args_receipt}" echo(%*\r\n'
            f'"{python_executable}" -c "import time; time.sleep(0.8)"\r\n'
            "popd\r\n"
            f'> "{cwd_after_popd}" echo(%cd%\r\n'
            "exit /b 37\r\n"
        )
        batch_path.write_text(script, encoding="utf-8", newline="")
        cmd_argv, command = controller._build_cmd_batch_argv(
            controller.CMD_EXE,
            str(batch_path),
            batch_arguments,
        )
        source_appdata = run_dir / "fixture_source_appdata"
        source_appdata.mkdir()
        license_file = run_dir / "fixture_license.lic"
        license_file.write_bytes(b"fixture license metadata only\n")
        with mock.patch.dict(
            os.environ,
            {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": str(license_file)},
            clear=False,
        ):
            environment, isolated_appdata, license_audit = controller._child_environment(run_dir)
        self.assertNotEqual(str(source_appdata), isolated_appdata)
        self.assertEqual(str(run_dir / "isolated_appdata"), environment["APPDATA"])
        self.assertEqual(str(license_file), environment["XILINXD_LICENSE_FILE"])
        self.assertTrue(license_audit["usable"])
        self.assertEqual(" ".join(batch_arguments), command[len("call ") + len(str(batch_path)) + 1 :])
        self.assertEqual([controller.CMD_EXE, "/D", "/S", "/V:OFF", "/C", command], cmd_argv)
        verified_batch, working_directory = controller._verified_vivado_batch_paths(str(batch_path))
        self.assertEqual(str(batch_path), verified_batch)
        self.assertEqual(str(fake_bin), working_directory)

        locks = [
            controller.InputReadLock(controller.CMD_EXE),
            controller.InputReadLock(str(batch_path)),
            controller.InputReadLock(python_executable),
        ]
        job = job_guard.JobObject(kill_on_close=True)
        child = None
        observed_python = {}
        root_identity_samples = []
        root_field_change_counts = {field: 0 for field in job_guard.ROSS_IDENTITY_FIELDS}
        sample_uncertainty_counts = {}
        closure = None
        try:
            child = job_guard.launch_suspended_root(
                job,
                controller.CMD_EXE,
                cmd_argv,
                cwd=working_directory,
                environment=environment,
            )
            root_identity = json.loads(json.dumps(child.identity))
            self.assertEqual(
                os.path.normcase(os.path.abspath(controller.CMD_EXE)),
                os.path.normcase(os.path.abspath(child.identity["exe"])),
            )
            self.assertEqual(cmd_argv, child.identity["cmdline"])
            self.assertEqual(
                os.path.normcase(os.path.abspath(working_directory)),
                os.path.normcase(os.path.abspath(child.identity["cwd"])),
            )
            self.assertTrue(any(row.get("event") == "PRE_RESUME_CLOSED" for row in child.events))

            deadline = time.monotonic() + 10.0
            while time.monotonic() < deadline:
                sample = job.sample()
                root_rows = [
                    member for member in sample["member_measurements"]
                    if member["pid"] == child.pid
                ]
                root_wait = job_guard._api_wait(child.process_handle, 0)
                self.assertIn(root_wait, (job_guard.WAIT_OBJECT_0, job_guard.WAIT_TIMEOUT))
                if root_wait == job_guard.WAIT_TIMEOUT:
                    self.assertEqual(1, len(root_rows), "root仍运行时该样本必须读回root六字段")
                for root_row in root_rows:
                    identity = root_row["identity"]
                    changed_fields = [
                        field for field in job_guard.ROSS_IDENTITY_FIELDS
                        if identity.get(field) != root_identity.get(field)
                    ]
                    for field in changed_fields:
                        root_field_change_counts[field] += 1
                    self.assertEqual([], changed_fields, "root六字段相对挂起前身份发生漂移")
                    root_identity_samples.append({
                        "sample_start_monotonic": sample["sample_start_monotonic"],
                        "identity": identity,
                        "uncertainty": list(sample["uncertainty"]),
                    })
                for uncertainty in sample["uncertainty"]:
                    category = uncertainty.split(":", 1)[0]
                    sample_uncertainty_counts[category] = sample_uncertainty_counts.get(category, 0) + 1
                for member in sample["member_measurements"]:
                    identity = member["identity"]
                    if os.path.normcase(os.path.abspath(identity["exe"])) == os.path.normcase(os.path.abspath(python_executable)):
                        key = (member["pid"], member["birth_ticks"])
                        observed_python[key] = {
                            "pid": member["pid"],
                            "birth_ticks": member["birth_ticks"],
                            "exe": identity["exe"],
                            "cmdline": identity["cmdline"],
                        }
                pids = job.pid_list()
                accounting = job.accounting()
                if root_wait == job_guard.WAIT_OBJECT_0 and not pids and accounting["active_processes"] == 0:
                    closure = child.wait_and_close(timeout_seconds=2.0)
                    child = None
                    break
                time.sleep(0.04)
            self.assertIsNotNone(closure, "cmd/bat/后代未在期限内闭合")
            args_text = args_receipt.read_text(encoding="utf-8").strip()
            cwd_receipts = {
                "after_pushd": cwd_after_pushd.read_text(encoding="utf-8").strip(),
                "after_restore": cwd_after_restore.read_text(encoding="utf-8").strip(),
                "after_popd": cwd_after_popd.read_text(encoding="utf-8").strip(),
            }
            expected_cwd = os.path.normcase(os.path.abspath(working_directory))
            self.assertTrue(root_identity_samples, "Job采样没有读回root六字段")
            self.assertTrue(all(count == 0 for count in root_field_change_counts.values()))
            self.assertTrue(all(
                os.path.normcase(os.path.abspath(path)) == expected_cwd
                for path in cwd_receipts.values()
            ), f"fixture批处理pushd/恢复/popd CWD不在fake bin：{cwd_receipts!r}")
            final = closure["final"]
            receipt = {
                "status": "PASS_CMD_BATCH_ARGUMENTS_EXIT_AND_JOB_CLOSURE",
                "cmd_command_line": job_guard.subprocess.list2cmdline(cmd_argv),
                "batch_path": str(batch_path),
                "working_directory": working_directory,
                "cwd_receipts": cwd_receipts,
                "root_identity_before_resume": root_identity,
                "root_identity_sample_count": len(root_identity_samples),
                "root_field_change_counts": root_field_change_counts,
                "root_identity_samples": root_identity_samples,
                "sample_uncertainty_counts": sample_uncertainty_counts,
                "sampling_note": "仅要求root身份每样本稳定；短命后代在样本边界退出可能产生成员集合不确定性并如实记录。",
                "expected_batch_arguments": batch_arguments,
                "batch_argument_receipt": args_text,
                "cmd_root_identity": root_identity,
                "cmd_exit_code": final["root_native_handle_exit_code"],
                "short_descendant_observations": list(observed_python.values()),
                "job_final_closure": final,
            }
            self.assertEqual(" ".join(batch_arguments), args_text)
            self.assertEqual(37, final["root_native_handle_exit_code"])
            self.assertTrue(observed_python, "Job采样未观察到由bat启动的Python短命后代")
            self.assertEqual([], final["job_pids"])
            self.assertEqual(0, final["active_processes"])
            self.assertTrue(all(row["status"] == "EXITED" for row in final["member_readbacks"]))
            self.assertTrue(all(
                job_guard._identity_equal(root_identity, row["identity"])
                for row in root_identity_samples
            ))
            final_member_keys = {
                (row["pid"], row["birth_ticks"])
                for row in final["member_readbacks"]
            }
            self.assertIn(
                (final["root_native_handle_pid"], final["root_native_handle_birth_ticks"]),
                final_member_keys,
            )
            self.assertTrue(set(observed_python).issubset(final_member_keys))
            _write_json(run_dir / "fixture_result.json", receipt)
        finally:
            if child is not None:
                try:
                    controller._kill_and_close(child, "FIXTURE_CLEANUP")
                except BaseException:
                    if not job.closed:
                        job.close()
            elif not job.closed:
                job.close()
            for lock in reversed(locks):
                lock.close()

    def test_rdi_verbose_is_disabled_and_sensitive_license_never_reaches_logs_or_manifest(self):
        run_dir = _new_run_dir("rdi_verbose_redaction")
        batch_path = run_dir / "fixture_verbose_loader.bat"
        source_appdata = run_dir / "fixture_source_appdata"
        source_appdata.mkdir()
        marker = "SENSITIVE_LICENSE_" + secrets.token_hex(16)
        license_path = run_dir / f"{marker}.lic"
        license_path.write_bytes(b"fixture-only-license-metadata\n")
        env_receipt = run_dir / "child_license_env_sha256.receipt"
        python_executable = str(Path(sys.executable).resolve())
        child_code = (
            "import hashlib,os,pathlib,sys,time; "
            "pathlib.Path(sys.argv[1]).write_text("
            "hashlib.sha256(os.environ['XILINXD_LICENSE_FILE'].encode('utf-8')).hexdigest().upper(), "
            "encoding='ascii'); time.sleep(0.25)"
        )
        script = (
            "@echo off\r\n"
            "setlocal EnableExtensions DisableDelayedExpansion\r\n"
            f'"{python_executable}" -c "{child_code}" "{env_receipt}"\r\n'
            'if /I "%RDI_VERBOSE%"=="True" echo XILINXD_LICENSE_FILE=%XILINXD_LICENSE_FILE%\r\n'
            "echo CHILD_RDI_VERBOSE=%RDI_VERBOSE%\r\n"
            "exit /b 0\r\n"
        )
        batch_path.write_text(script, encoding="utf-8", newline="")
        cmd_argv, command = controller._build_cmd_batch_argv(controller.CMD_EXE, str(batch_path), [])
        patched_environment = {
            "APPDATA": str(source_appdata),
            "XILINXD_LICENSE_FILE": str(license_path),
            "RDI_VERBOSE": "True",
        }
        with mock.patch.dict(os.environ, patched_environment, clear=False):
            environment, isolated_appdata, license_audit = controller._child_environment(run_dir)
            self.assertEqual("True", os.environ["RDI_VERBOSE"])
            self.assertEqual("False", environment["RDI_VERBOSE"])
            self.assertEqual(str(license_path), environment["XILINXD_LICENSE_FILE"])
            self.assertEqual("explicit_environment", license_audit["mode"])

            locks = [
                controller.InputReadLock(controller.CMD_EXE),
                controller.InputReadLock(str(batch_path)),
                controller.InputReadLock(python_executable),
            ]
            job = job_guard.JobObject(kill_on_close=True)
            child = None
            std_handles = None
            std_streams = ()
            writer = None
            try:
                std_handles, std_streams = controller._open_stdio_handles(run_dir)
                child = job_guard.launch_suspended_root(
                    job,
                    controller.CMD_EXE,
                    cmd_argv,
                    cwd=str(run_dir),
                    std_handles=std_handles,
                    environment=environment,
                )
                root_identity = child.identity
                controller._close_stdio(std_handles, std_streams)
                std_handles, std_streams = None, ()
                previous_sample_start = None
                previous_accounting = None
                previous_pids = None
                previous_keys = set()
                observed_child_identities = set()
                closure = None
                deadline = time.monotonic() + 10.0
                while time.monotonic() < deadline:
                    sample = job.sample(
                        previous_sample_start=previous_sample_start,
                        previous_accounting=previous_accounting,
                        previous_pids=previous_pids,
                        previous_keys=previous_keys,
                    )
                    previous_sample_start = sample["sample_start_monotonic"]
                    previous_accounting = sample["accounting_after"]
                    previous_pids = set(sample["job_pids_after"])
                    previous_keys = {
                        (row["pid"], row["birth_ticks"])
                        for row in sample["member_measurements"]
                    }
                    observed_child_identities.update(
                        (row["pid"], row["birth_ticks"])
                        for row in sample["member_measurements"]
                        if os.path.normcase(os.path.abspath(row["identity"].get("exe", "")))
                        == os.path.normcase(os.path.abspath(python_executable))
                    )
                    root_wait = job_guard._api_wait(child.process_handle, 0)
                    pids = job.pid_list()
                    accounting = job.accounting()
                    if root_wait == job_guard.WAIT_OBJECT_0 and not pids and accounting["active_processes"] == 0:
                        closure = child.wait_and_close(timeout_seconds=2.0)
                        child = None
                        break
                    time.sleep(0.04)
                self.assertIsNotNone(closure, "cmd/bat/许可环境fixture的Job成员未闭合")
                child = None

                stdout = (run_dir / "stdout.log").read_text(encoding="utf-8", errors="replace")
                stderr = (run_dir / "stderr.log").read_text(encoding="utf-8", errors="replace")
                self.assertIn("CHILD_RDI_VERBOSE=False", stdout)
                self.assertNotIn(marker, stdout)
                self.assertNotIn(str(license_path), stdout)
                self.assertNotIn(marker, stderr)
                self.assertNotIn(str(license_path), stderr)
                self.assertEqual(
                    controller.hashlib.sha256(str(license_path).encode("utf-8")).hexdigest().upper(),
                    env_receipt.read_text(encoding="ascii").strip(),
                )
                self.assertEqual(0, closure["final"]["root_native_handle_exit_code"])
                self.assertEqual([], closure["final"]["job_pids"])
                self.assertTrue(all(row["status"] == "EXITED" for row in closure["final"]["member_readbacks"]))
                final_member_keys = {
                    (row["pid"], row["birth_ticks"])
                    for row in closure["final"]["member_readbacks"]
                }
                self.assertTrue(observed_child_identities)
                self.assertTrue(observed_child_identities.issubset(final_member_keys))

                manifest = {
                    "schema": "s15-direct-frozen-dcp-bitgen/2.0.0",
                    "status": "PASS_RDI_VERBOSE_SECRET_REDACTION",
                    "input_paths_and_hashes": {"license_environment_audit": license_audit},
                    "process_launch": {
                        "argv": cmd_argv,
                        "batch_command": command,
                        "windows_command_line": job_guard.subprocess.list2cmdline(cmd_argv),
                        "root_identity": root_identity,
                        "lifecycle_events": closure["events"],
                        "job_final_closure": closure["final"],
                        "isolated_appdata_path": isolated_appdata,
                        "rdi_verbose_forced_off": environment["RDI_VERBOSE"] == "False",
                    },
                    "artifacts": {
                        "stdout": {"size_bytes": len(stdout.encode("utf-8")), "sha256": controller.hashlib.sha256(stdout.encode("utf-8")).hexdigest().upper()},
                        "stderr": {"size_bytes": len(stderr.encode("utf-8")), "sha256": controller.hashlib.sha256(stderr.encode("utf-8")).hexdigest().upper()},
                    },
                }
                writer = controller.ManifestWriter(run_dir, manifest)
                writer.close()
                writer = None
                serialized_manifest = (run_dir / "manifest.json").read_text(encoding="utf-8")
                self.assertNotIn(marker, serialized_manifest)
                self.assertNotIn(str(license_path), serialized_manifest)
                self.assertNotIn(marker, json.dumps(license_audit, ensure_ascii=False))
                self.assertNotIn(str(license_path), json.dumps(license_audit, ensure_ascii=False))
                _write_json(
                    run_dir / "fixture_result.json",
                    {
                        "status": "PASS_RDI_VERBOSE_SECRET_REDACTION",
                        "stdout_contains_secret": False,
                        "manifest_contains_secret": False,
                        "license_child_environment_sha256_verified": True,
                        "native_cmd_exit_code": closure["final"]["root_native_handle_exit_code"],
                    },
                )
            finally:
                if writer is not None:
                    writer.close()
                if child is not None:
                    controller._kill_and_close(child, "FIXTURE_CLEANUP")
                elif not job.closed:
                    job.close()
                if std_handles is not None:
                    controller._close_stdio(std_handles, std_streams)
                for lock in reversed(locks):
                    lock.close()

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
    def test_manifest_schema_marks_batch_launcher_revision(self):
        source = (ROOT / "verification" / "s15_direct_vivado_bitgen.py").read_text(encoding="utf-8")
        self.assertIn('"schema": "s15-direct-frozen-dcp-bitgen/2.0.0"', source)

    def test_cmd_batch_arguments_reject_cmd_metacharacters_and_whitespace(self):
        run_dir = _new_run_dir("cmd_argument_boundaries")
        batch_path = run_dir / "fixture_launcher.bat"
        unsafe = (
            "contains space",
            "& whoami",
            "|more",
            "<input",
            ">output",
            "^escape",
            "(group)",
            "%PATH%",
            "!variable!",
            "quoted\"value",
            "line\nbreak",
            "semicolon;command",
        )
        rejected = []
        for value in unsafe:
            with self.subTest(value=value), self.assertRaises(controller.ControllerError):
                controller._build_cmd_batch_argv(controller.CMD_EXE, str(batch_path), ["-tclargs", value])
            rejected.append(value)
        with self.assertRaises(controller.ControllerError):
            controller._build_cmd_batch_argv("cmd.exe", str(batch_path), [])
        with self.assertRaises(controller.ControllerError):
            controller._build_cmd_batch_argv(controller.CMD_EXE, str(batch_path), "-mode batch")
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_CMD_ARGUMENT_BOUNDARIES", "rejected_arguments": rejected},
        )

    def test_batch_launcher_inherits_appdata_and_license_environment(self):
        run_dir = _new_run_dir("environment_inheritance")
        expected = {"APPDATA": str(run_dir), "XILINXD_LICENSE_FILE": "27000@fixture-license.invalid", "LM_LICENSE_FILE": "fixture-license-file.lic"}
        with mock.patch.dict(os.environ, expected, clear=False):
            environment, isolated_appdata, audit = controller._child_environment(run_dir)
        self.assertNotEqual(expected["APPDATA"], isolated_appdata)
        self.assertEqual(str(run_dir / "isolated_appdata"), environment["APPDATA"])
        self.assertTrue(audit["usable"])
        self.assertEqual("explicit_environment", audit["mode"])
        for name in controller.LICENSE_ENVIRONMENT_NAMES:
            self.assertEqual(expected[name], environment[name])
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_PRIVATE_APPDATA_AND_LICENSE_ENVIRONMENT_INHERITANCE",
                "isolated_appdata": isolated_appdata,
                "license_variables": list(controller.LICENSE_ENVIRONMENT_NAMES),
                "license_audit": audit,
            },
        )

    def test_private_appdata_excludes_user_tcl_init_scripts(self):
        run_dir = _new_run_dir("private_appdata_user_init")
        source_appdata = run_dir / "source_appdata"
        version_dir = source_appdata / "Xilinx" / "Vivado" / controller.EXPECTED_VIVADO_VERSION
        version_dir.mkdir(parents=True)
        marker = run_dir / "user_init_executed.marker"
        script = version_dir / "Vivado_init.tcl"
        script.write_text(f"set handle [open {{{marker}}} w]; puts $handle executed; close $handle\n", encoding="utf-8")
        license_file = run_dir / "fixture_license.lic"
        license_file.write_bytes(b"fixture license metadata only\n")
        with mock.patch.dict(
            os.environ,
            {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": str(license_file)},
            clear=False,
        ):
            audit = controller._audit_user_init_scripts(source_appdata)
            environment, isolated_appdata, _license_audit = controller._child_environment(run_dir)
        self.assertTrue(audit["source_scripts"][0]["exists"])
        self.assertFalse(audit["copied_to_child_appdata"])
        self.assertFalse((Path(isolated_appdata) / "Xilinx" / "Vivado" / controller.EXPECTED_VIVADO_VERSION / "Vivado_init.tcl").exists())
        self.assertEqual(isolated_appdata, environment["APPDATA"])
        self.assertFalse(marker.exists())
        self.assertNotIn(str(source_appdata), json.dumps(audit, ensure_ascii=False))
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_USER_TCL_EXCLUDED_BY_PRIVATE_APPDATA", "script_audit": audit, "isolated_appdata": isolated_appdata},
        )

    def test_license_audit_preserves_nonempty_values_without_network_probe(self):
        run_dir = _new_run_dir("license_value_audit")
        appdata = run_dir / "fixture_appdata"
        appdata.mkdir()
        value = "27000@fixture-license.invalid;C:\\licenses\\node_locked.lic"
        environment = {"XILINXD_LICENSE_FILE": value}
        with mock.patch("socket.socket", side_effect=AssertionError("不应进行网络探测")):
            audit = controller._audit_license_configuration(environment, appdata)
        self.assertTrue(audit["usable"])
        self.assertEqual("explicit_environment", audit["mode"])
        self.assertEqual(
            controller.hashlib.sha256(value.encode("utf-8")).hexdigest().upper(),
            audit["variables"][0]["value_sha256"],
        )
        serialized = json.dumps(audit, ensure_ascii=False)
        self.assertNotIn(value, serialized)
        self.assertNotIn("fixture-license.invalid", serialized)
        _write_json(run_dir / "fixture_result.json", {"status": "PASS_REDACTED_LICENSE_ENV_AUDIT", "audit": audit})

    def test_default_license_fallback_requires_exactly_one_file_and_redacts_parent_path(self):
        run_dir = _new_run_dir("default_license_fallback")
        source_appdata = run_dir / "source_appdata"
        license_dir = source_appdata / "XilinxLicense"
        license_dir.mkdir(parents=True)
        license_file = license_dir / "single_fixture.lic"
        license_file.write_bytes(b"fixture license bytes are not copied\n")
        environment = {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": ""}
        with mock.patch.dict(os.environ, environment, clear=False):
            audit = controller._audit_license_configuration(environment, source_appdata)
            child_environment, isolated_appdata, child_audit = controller._child_environment(run_dir)
        self.assertTrue(audit["usable"])
        self.assertTrue(audit["default_license_used"])
        self.assertEqual(str(license_file), child_environment["XILINXD_LICENSE_FILE"])
        self.assertEqual(str(run_dir / "isolated_appdata"), isolated_appdata)
        self.assertEqual(audit, child_audit)
        self.assertNotIn(str(source_appdata), json.dumps(audit, ensure_ascii=False))
        self.assertFalse((Path(isolated_appdata) / "XilinxLicense" / license_file.name).exists())

        second_license = license_dir / "second_fixture.lic"
        second_license.write_bytes(b"second fixture license bytes\n")
        multiple_audit = controller._audit_license_configuration(environment, source_appdata)
        self.assertFalse(multiple_audit["usable"])
        self.assertFalse(multiple_audit["default_license_used"])
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_SINGLE_DEFAULT_LICENSE_ONLY",
                "single_file_audit": audit,
                "multiple_file_audit": multiple_audit,
                "isolated_appdata": isolated_appdata,
            },
        )

    def test_default_license_recheck_failures_are_redacted_in_production_manifest(self):
        run_dir = _new_run_dir("default_license_recheck_redaction")
        source_appdata = run_dir / "source_appdata"
        license_dir = source_appdata / "XilinxLicense"
        license_dir.mkdir(parents=True)
        marker = "SENSITIVE_LICENSE_PATH_" + secrets.token_hex(8)
        license_file = license_dir / f"{marker}.lic"
        license_file.write_bytes(b"fixture-only license metadata\n")
        environment = {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": ""}
        with mock.patch.dict(os.environ, environment, clear=False):
            audit = controller._audit_license_configuration(environment, source_appdata)
        self.assertTrue(audit["default_license_used"])
        self.assertNotIn(marker, json.dumps(audit, ensure_ascii=False))
        self.assertNotIn(str(source_appdata), json.dumps(audit, ensure_ascii=False))

        injected_failures = []
        for failure_kind in ("path_chain", "iterdir"):
            failure_run = _new_run_dir(f"default_license_recheck_{failure_kind}")
            manifest = {
                "schema": "s15-direct-frozen-dcp-bitgen/2.0.0",
                "status": "PREPARED_NOT_STARTED",
                "run_id": failure_run.name,
                "run_directory": str(failure_run),
                "input_paths_and_hashes": {
                    "license_environment_audit": audit,
                },
                "stop_reason": None,
            }
            writer = controller.ManifestWriter(failure_run, manifest)
            raw_text = f"injected {failure_kind} failure {license_file} {marker}"
            try:
                if failure_kind == "path_chain":
                    real_assert = controller._assert_path_chain

                    def fail_license_path(path, expected_kind):
                        if os.path.normcase(os.path.abspath(str(path))) == os.path.normcase(os.path.abspath(str(license_file))):
                            raise OSError(raw_text)
                        return real_assert(path, expected_kind)

                    patcher = mock.patch.object(controller, "_assert_path_chain", side_effect=fail_license_path)
                else:
                    real_iterdir = Path.iterdir

                    def fail_license_iterdir(path):
                        if os.path.normcase(os.path.abspath(str(path))) == os.path.normcase(os.path.abspath(str(license_dir))):
                            raise OSError(raw_text)
                        return real_iterdir(path)

                    patcher = mock.patch.object(Path, "iterdir", new=fail_license_iterdir)
                with patcher:
                    with self.assertRaises(controller.ControllerError) as raised:
                        controller._resolve_single_default_license_path(source_appdata, audit)
                self.assertIsNone(raised.exception.__cause__)
                self.assertNotIn(marker, str(raised.exception))
                self.assertNotIn(str(source_appdata), str(raised.exception))
                self.assertNotIn(raw_text, str(raised.exception))
                reason = controller._record_controller_exception(manifest, raised.exception)
                self.assertEqual("CONTROLLER_EXCEPTION_REDACTED", reason)
                writer.write()
                writer.close()
                serialized = (failure_run / "manifest.json").read_text(encoding="utf-8")
                self.assertIn('"schema": "s15-direct-frozen-dcp-bitgen/2.0.0"', serialized)
                self.assertEqual("FAILED_OR_INCOMPLETE", manifest["status"])
                self.assertEqual("CONTROLLER_EXCEPTION_REDACTED", manifest["stop_reason"])
                self.assertEqual(
                    {
                        "category": "CONTROLLER_EXCEPTION",
                        "details_redacted": True,
                        "message": "原始异常文本已省略",
                    },
                    manifest["controller_exception"],
                )
                self.assertNotIn(marker, serialized)
                self.assertNotIn(str(source_appdata), serialized)
                self.assertNotIn(str(license_file), serialized)
                self.assertNotIn(raw_text, serialized)
                injected_failures.append(failure_kind)
            finally:
                if not writer.stream.closed:
                    writer.close()

        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_DEFAULT_LICENSE_RECHECK_EXCEPTION_REDACTION",
                "injected_failures": injected_failures,
                "production_manifest_schema": "s15-direct-frozen-dcp-bitgen/2.0.0",
                "license_audit_contains_path_or_marker": False,
            },
        )

    def test_vivado_vendor_batch_call_chain_is_present_and_hashed(self):
        run_dir = _new_run_dir("vendor_batch_chain")
        paths = {
            "vivado.bat": controller.VIVADO_BAT,
            **controller.VIVADO_BATCH_SUPPORT,
        }
        call_chain = controller._verify_vivado_batch_chain(paths)
        hashes = {name: controller._sha256(path) for name, path in paths.items()}
        self.assertEqual(set(paths), set(hashes))
        self.assertEqual({"vivado.bat", "loader.bat", "rdiArgs.bat"}, set(call_chain))
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_STATIC_VIVADO_BATCH_CHAIN", "paths": paths, "sha256": hashes, "calls": call_chain},
        )

    def test_success_requires_observed_vivado_job_member_exit_zero(self):
        observation = {
            "pid": 123,
            "birth_ticks": 456,
            "create_time": 789,
            "exe": controller.VIVADO_EXE,
            "cmdline": [controller.VIVADO_EXE, "-mode", "batch"],
            "first_observed_monotonic_seconds": 1.0,
            "last_observed_monotonic_seconds": 2.0,
        }
        valid_closure = {
            "final": {
                "member_readbacks": [
                    {"pid": 123, "birth_ticks": 456, "status": "EXITED", "exit_code": 0}
                ]
            }
        }
        self.assertTrue(controller._vivado_member_closure([observation], valid_closure)["valid"])
        nonzero = {
            "final": {
                "member_readbacks": [
                    {"pid": 123, "birth_ticks": 456, "status": "EXITED", "exit_code": 1}
                ]
            }
        }
        self.assertFalse(controller._vivado_member_closure([observation], nonzero)["valid"])
        self.assertFalse(controller._vivado_member_closure([], valid_closure)["valid"])
        self.assertFalse(controller._vivado_member_closure([observation], {"final": {"member_readbacks": []}})["valid"])

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
            "vivado_batch_path": controller.VIVADO_BAT,
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

    def test_production_working_directory_is_verified_vivado_batch_parent(self):
        run_dir = _new_run_dir("working_directory_binding")
        fake_bin = run_dir / "fake_vivado_bin"
        fake_bin.mkdir()
        batch_path = fake_bin / "vivado.bat"
        batch_path.write_text("@echo off\r\n", encoding="utf-8", newline="")

        verified_batch, working_directory = controller._verified_vivado_batch_paths(str(batch_path))

        self.assertEqual(str(batch_path), verified_batch)
        self.assertEqual(str(fake_bin), working_directory)
        self.assertNotEqual(str(run_dir), working_directory)
        source = (ROOT / "verification" / "s15_direct_vivado_bitgen.py").read_text(encoding="utf-8")
        self.assertIn(
            "vivado_batch, vivado_working_directory = _verified_vivado_batch_paths(VIVADO_BAT)",
            source,
        )
        self.assertIn('"working_directory": facts["vivado_working_directory"]', source)
        self.assertIn('cwd=facts["vivado_working_directory"]', source)
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_PRODUCTION_WORKING_DIRECTORY_BIN_BINDING",
                "verified_batch_path": verified_batch,
                "selected_working_directory": working_directory,
                "expected_working_directory": str(fake_bin),
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
