"""验证冻结DCP direct bitgen runner的本机Win32生命周期门禁。"""
import ctypes
import datetime
import gc
import inspect
import json
import os
import secrets
import struct
import sys
import tempfile
import time
import traceback
import unittest
import weakref
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


def _new_private_temp_root(test_case):
    """在工作区测试隔离目录下创建短TemporaryDirectory并由addCleanup回收。"""
    root_parent = _effective_fixture_evidence_parent() / f"s15_test_parent_{secrets.token_hex(8)}"
    current_user_sid, _groups = controller._current_process_token_sids()
    controller._create_private_profile_directory(root_parent, current_user_sid)

    def cleanup_parent():
        if list(root_parent.iterdir()):
            raise AssertionError(f"测试私有父目录未清空，保留路径：{str(root_parent)!r}")
        root_parent.rmdir()

    test_case.addCleanup(cleanup_parent)
    temporary_directory = tempfile.TemporaryDirectory(prefix="s15t_", dir=str(root_parent))
    test_case.addCleanup(temporary_directory.cleanup)
    return Path(temporary_directory.name)


def _child_environment_fixture(run_dir, temporary_root):
    """用短的厂商相对路径运行child environment隔离测试。"""
    with mock.patch.object(controller, "_vendor_tclstore_relative_files", return_value=["fixture.tcl"]):
        return controller._child_environment(run_dir, temporary_root=temporary_root)


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
    executable = str(Path(getattr(sys, "_base_executable", None) or sys.executable).resolve())
    return executable, [executable, "-I", "-S", "-c", source, str(marker_path), str(exit_code)]


def _minimal_fixture_environment():
    environment = {
        name: os.environ[name]
        for name in ("SystemRoot", "WINDIR", "PATH", "TEMP", "TMP")
        if os.environ.get(name)
    }
    environment["S15_FIXTURE_ENV"] = "unicode-环境-value"
    return environment


def _fixture_readback_or_error(reader):
    try:
        return reader()
    except BaseException as error:
        return {"diagnostic_read_error": repr(error)}


def _wait_close_failure_receipt(run_dir, executable, argv, environment, job, child, error):
    return {
        "status": "REAL_WIN32_LIFECYCLE_WAIT_AND_CLOSE_FAILED",
        "run_directory": str(run_dir),
        "platform": sys.platform,
        "interpreter": {
            "executable": sys.executable,
            "base_executable": getattr(sys, "_base_executable", None),
            "version": sys.version,
            "implementation": sys.implementation.name,
            "flags": {
                "isolated": sys.flags.isolated,
                "ignore_environment": sys.flags.ignore_environment,
                "no_site": sys.flags.no_site,
                "safe_path": getattr(sys.flags, "safe_path", None),
            },
        },
        "child": {
            "executable": executable,
            "argv": argv,
            "pid": child.pid,
            "birth_ticks": child.birth_ticks,
            "identity": child.identity,
            "closed": child.closed,
        },
        "child_environment_keys": sorted(environment),
        "filtered_parent_python_environment_names": sorted(
            name for name in os.environ if name.upper().startswith("PYTHON")
        ),
        "job": {
            "accounting": _fixture_readback_or_error(job.accounting),
            "pids": _fixture_readback_or_error(job.pid_list),
            "cached_member_handle_keys": [
                {"pid": int(pid), "birth_ticks": int(ticks)}
                for pid, ticks in sorted(job.member_handles)
            ],
        },
        "exception_type": type(error).__name__,
        "exception": repr(error),
        "traceback": traceback.format_exc(),
    }


@unittest.skipUnless(os.name == "nt", "非Windows环境：显式SKIP，不能声称本机Win32 fixture通过")
class DirectSpawnFixtureTests(unittest.TestCase):
    def test_handle_list_value_owner_lives_until_attribute_list_delete(self):
        handles = (0x101, 0x202, 0x303)
        expected_size = len(handles) * ctypes.sizeof(job_guard.wintypes.HANDLE)
        original_cast = ctypes.cast
        original_delete = job_guard.kernel32.DeleteProcThreadAttributeList

        for update_succeeds in (True, False):
            captured = {}
            owner_ref = None

            def capture_cast(value, target):
                if (
                    isinstance(value, ctypes.Array)
                    and getattr(type(value), "_type_", None) == job_guard.wintypes.HANDLE
                    and ctypes.sizeof(value) == expected_size
                ):
                    captured["weak_owner"] = weakref.ref(value)
                    captured["address"] = ctypes.addressof(value)
                return original_cast(value, target)

            def update_attribute(pointer, flags, attribute, value, size, previous, returned_size):
                captured["value_address"] = int(value.value or 0)
                captured["value_size"] = int(size)
                if not update_succeeds:
                    ctypes.set_last_error(job_guard.ERROR_ACCESS_DENIED)
                return update_succeeds

            def delete_attribute_list(pointer):
                self.assertIn("weak_owner", captured)
                self.assertIsNotNone(captured["weak_owner"]())
                values = (job_guard.wintypes.HANDLE * len(handles)).from_address(
                    captured["value_address"],
                )
                self.assertEqual(handles, tuple(int(value or 0) for value in values))
                result = original_delete(pointer)
                captured["deleted"] = True
                return result

            with (
                mock.patch.object(job_guard.ctypes, "cast", side_effect=capture_cast),
                mock.patch.object(job_guard.kernel32, "UpdateProcThreadAttribute",
                                  side_effect=update_attribute),
                mock.patch.object(job_guard.kernel32, "DeleteProcThreadAttributeList",
                                  side_effect=delete_attribute_list),
            ):
                if update_succeeds:
                    buffer, pointer, value_owner = job_guard._initialize_handle_list(handles)
                    owner_ref = captured["weak_owner"]
                    try:
                        self.assertEqual(expected_size, captured["value_size"])
                        self.assertEqual(captured["address"], captured["value_address"])
                        gc.collect()
                        self.assertIs(value_owner, owner_ref())
                        same_size_allocations = [
                            (job_guard.wintypes.HANDLE * len(handles))(
                                0xA000 + index, 0xB000 + index, 0xC000 + index,
                            )
                            for index in range(32)
                        ]
                        self.assertEqual(len(handles), len(value_owner))
                        self.assertEqual(expected_size, ctypes.sizeof(value_owner))
                        self.assertEqual(handles, tuple(int(value or 0) for value in value_owner))
                        self.assertEqual(32, len(same_size_allocations))
                        job_guard._close_attribute_list(buffer, pointer, value_owner)
                        self.assertTrue(captured["deleted"])
                    finally:
                        if not captured.get("deleted"):
                            job_guard._close_attribute_list(buffer, pointer, value_owner)
                    owner_ref = captured["weak_owner"]
                    del value_owner
                else:
                    with self.assertRaises(job_guard.JobGuardError):
                        job_guard._initialize_handle_list(handles)
                    self.assertTrue(captured["deleted"])
                    owner_ref = captured["weak_owner"]
            gc.collect()
            self.assertIsNotNone(owner_ref)
            self.assertIsNone(owner_ref())

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

    def test_constructor_query_failure_and_bad_size_close_job_without_launch(self):
        run_dir = _new_run_dir("job_constructor_query_cleanup")
        original_create_job = job_guard.kernel32.CreateJobObjectW
        original_close = job_guard._api_close_handle
        cases = (
            ("api_failure", job_guard.JobGuardError),
            ("size_mismatch", job_guard.GateBlocked),
        )
        receipts = []
        for label, expected_error in cases:
            created_handles = []
            closed_handles = []

            def create_job(*args):
                handle = original_create_job(*args)
                created_handles.append(int(handle))
                return handle

            def close_job(handle):
                result = bool(original_close(handle))
                closed_handles.append({"handle": int(handle), "closed": result})
                return result

            def query_failure_or_bad_size(handle, info_class, info, size, returned):
                self.assertIn(int(handle), created_handles)
                self.assertEqual(job_guard.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, info_class)
                value = ctypes.cast(
                    returned, ctypes.POINTER(job_guard.wintypes.DWORD),
                ).contents
                if label == "api_failure":
                    ctypes.set_last_error(job_guard.ERROR_ACCESS_DENIED)
                    return False
                value.value = int(size) - 1
                return True

            try:
                with (
                    mock.patch.object(job_guard.kernel32, "CreateJobObjectW", side_effect=create_job),
                    mock.patch.object(job_guard.kernel32, "QueryInformationJobObject",
                                      side_effect=query_failure_or_bad_size),
                    mock.patch.object(job_guard, "_api_close_handle", side_effect=close_job),
                    mock.patch.object(job_guard, "_api_create_process") as create_process,
                    mock.patch.object(job_guard, "_api_resume_thread") as resume_thread,
                ):
                    with self.assertRaises(expected_error) as caught:
                        job_guard.JobObject(kill_on_close=True)
                    create_process.assert_not_called()
                    resume_thread.assert_not_called()
            finally:
                for handle in created_handles:
                    if not any(row["handle"] == handle and row["closed"] for row in closed_handles):
                        original_close(handle)

            self.assertEqual(1, len(created_handles))
            self.assertEqual(
                [{"handle": created_handles[0], "closed": True}], closed_handles,
            )
            receipts.append({
                "case": label,
                "exception": type(caught.exception).__name__,
                "created_job_handle": created_handles[0],
                "closed_handles": closed_handles,
                "process_create_called": False,
                "resume_thread_called": False,
            })
        _write_json(run_dir / "fixture_result.json", {
            "status": "PASS_JOB_CONSTRUCTOR_QUERY_FAILURE_CLEANUP",
            "run_directory": str(run_dir),
            "cases": receipts,
        })

    def test_real_create_suspended_assign_resume_and_exit_closure(self):
        run_dir = _new_run_dir("real_lifecycle")
        marker = run_dir / "resumed.marker"
        executable, argv = _fixture_argv(marker, 23)
        job = job_guard.JobObject(kill_on_close=True)
        environment = _minimal_fixture_environment()
        child = None
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
            try:
                closure = child.wait_and_close(timeout_seconds=10.0)
            except BaseException as error:
                receipt = _wait_close_failure_receipt(
                    run_dir, executable, argv, environment, job, child, error
                )
                try:
                    child._close_all()
                    receipt["cleanup_after_diagnostic"] = "OK"
                except BaseException as cleanup_error:
                    receipt["cleanup_after_diagnostic"] = repr(cleanup_error)
                _write_json(run_dir / "fixture_result.json", receipt)
                raise
            receipt = {
                "status": "PASS_REAL_WIN32_LIFECYCLE",
                "run_directory": str(run_dir),
                "platform": sys.platform,
                "executable": executable,
                "argv": argv,
                "python_version": sys.version,
                "child_environment_keys": sorted(environment),
                "filtered_parent_python_environment_names": sorted(
                    name for name in os.environ if name.upper().startswith("PYTHON")
                ),
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
            if child is not None and not child.closed:
                try:
                    child._close_all()
                except BaseException:
                    pass
            elif not job.closed:
                job.close()

    def test_suspended_root_ignores_pid_only_historical_descendants(self):
        run_dir = _new_run_dir("suspended_root_stale_ppid")
        environment = _minimal_fixture_environment()
        cases = (
            ("historical_pid", {"return_value": {26112}}),
            ("access_denied", {"side_effect": job_guard.JobGuardError(
                "OpenProcess(pid=26112) 失败：WinError 5")}),
        )
        receipts = []
        for label, descendants_behavior in cases:
            marker = run_dir / f"{label}.marker"
            executable, argv = _fixture_argv(marker, 0)
            job = job_guard.JobObject(kill_on_close=True)
            child = None
            try:
                with mock.patch.object(
                    job_guard, "descendants", **descendants_behavior,
                ) as descendants:
                    child = job_guard.launch_suspended_root(
                        job, executable, argv, cwd=str(ROOT), environment=environment,
                    )
                    descendants.assert_not_called()
                pre_resume = next(
                    row for row in child.events
                    if row.get("event") == "PRE_RESUME_CLOSED"
                )
                proof = pre_resume["suspended_root_membership"]
                self.assertEqual([child.pid], proof["first"]["job_pids"])
                self.assertEqual([child.pid], proof["second"]["job_pids"])
                self.assertEqual(1, proof["first"]["active_processes"])
                self.assertEqual(1, proof["second"]["active_processes"])
                self.assertEqual(2, proof["stable_singleton_reads"])
                closure = child.wait_and_close(timeout_seconds=10.0)
                child = None
                self.assertEqual(0, closure["final"]["active_processes"])
                self.assertEqual(0, closure["final"]["root_native_handle_exit_code"])
                self.assertTrue(marker.exists())
                receipts.append({"case": label, "proof": proof, "closure": closure})
            finally:
                if child is not None and not child.closed:
                    try:
                        child._close_all()
                    except BaseException:
                        pass
                elif not job.closed:
                    job.close()
        _write_json(run_dir / "fixture_result.json", {
            "status": "PASS_SUSPENDED_ROOT_PID_ONLY_DESCENDANT_ISOLATION",
            "run_directory": str(run_dir),
            "cases": receipts,
        })

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
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(
            os.environ,
            {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": str(license_file)},
            clear=False,
        ):
            environment, isolated_appdata, license_audit, appdata_profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
        self.assertNotEqual(str(source_appdata), isolated_appdata)
        self.assertEqual(isolated_appdata, environment["APPDATA"])
        self.assertEqual(isolated_appdata, appdata_profile_audit["path"])
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
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(os.environ, patched_environment, clear=False):
            environment, isolated_appdata, license_audit, _profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
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

        def fail_membership(_self, *_args):
            raise job_guard.GateBlocked("fixture注入稳定成员集合不闭合")

        with mock.patch.object(job_guard.JobObject, "_verify_suspended_root_membership", fail_membership):
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
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(os.environ, expected, clear=False):
            environment, isolated_appdata, audit, profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
        self.assertNotEqual(expected["APPDATA"], isolated_appdata)
        self.assertEqual(isolated_appdata, environment["APPDATA"])
        self.assertTrue(audit["usable"])
        self.assertEqual("explicit_environment", audit["mode"])
        self.assertEqual(run_dir.name, profile_audit["run_id"])
        self.assertEqual(isolated_appdata, profile_audit["path"])
        self.assertLessEqual(profile_audit["path_length_audit"]["longest_destination_path_utf16_chars"], 259)
        self.assertNotIn(expected["XILINXD_LICENSE_FILE"], json.dumps(profile_audit, ensure_ascii=False))
        self.assertNotIn(expected["LM_LICENSE_FILE"], json.dumps(profile_audit, ensure_ascii=False))
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

    def test_private_appdata_profile_is_short_unique_canonical_and_writable(self):
        run_dir = _new_run_dir("private_appdata_profile_path")
        temporary_root = _new_private_temp_root(self)
        vendor_files = ["apps/short_name.tcl", "catalogs/example/catalog.xml"]
        first_path, first_audit = controller._create_private_appdata_profile(
            run_dir.name,
            temporary_root=temporary_root,
            vendor_relative_files=vendor_files,
        )
        second_path, second_audit = controller._create_private_appdata_profile(
            run_dir.name,
            temporary_root=temporary_root,
            vendor_relative_files=vendor_files,
        )
        self.assertNotEqual(first_path, second_path)
        self.assertEqual(run_dir.name, first_audit["run_id"])
        self.assertEqual(str(temporary_root.resolve(strict=True)), first_audit["profile_parent_path"])
        self.assertEqual(str(Path(first_path).resolve(strict=True)), first_audit["canonical_path"])
        self.assertEqual(first_audit["path"], controller._assert_path_chain(first_path, "directory"))
        self.assertEqual(
            os.path.normcase(os.path.abspath(str(temporary_root))),
            os.path.normcase(os.path.abspath(first_path).rsplit(os.sep + "s15_appdata_", 1)[0]),
        )
        self.assertLessEqual(first_audit["path_utf16_chars"], 259)
        self.assertLessEqual(first_audit["path_length_audit"]["longest_destination_path_utf16_chars"], 259)
        profile_acl = first_audit["profile_security_audit"]
        self.assertTrue(profile_acl["owner_matches_current_user"])
        self.assertTrue(profile_acl["dacl_protected"])
        self.assertTrue(profile_acl["only_expected_principals_with_full_control"])
        self.assertEqual(3, profile_acl["ace_count"])
        self.assertEqual(
            {"CURRENT_USER", "SYSTEM", "ADMINISTRATORS"},
            {ace["principal"] for ace in profile_acl["aces"]},
        )
        self.assertEqual(
            {controller.FILE_ALL_ACCESS},
            {ace["mask"] for ace in profile_acl["aces"]},
        )
        self.assertEqual(
            {controller.OBJECT_INHERIT_ACE | controller.CONTAINER_INHERIT_ACE},
            {ace["inherit_flags"] for ace in profile_acl["aces"]},
        )
        parent_acl = first_audit["parent_security_audit"]
        self.assertFalse(parent_acl["parent_mutable_by_nontrusted_principal"])
        self.assertEqual("EXPLICIT_TEST_ROOT", first_audit["profile_parent_source"])
        current_user_sid, _groups = controller._current_process_token_sids()
        inherited_directory = Path(first_path) / "Xilinx" / "Vivado" / controller.EXPECTED_VIVADO_VERSION
        inherited_directory.mkdir(parents=True)
        inherited_acl = controller._inspect_directory_security(
            inherited_directory,
            current_user_sid,
            require_inherited_profile_dacl=True,
        )
        self.assertFalse(inherited_acl["dacl_protected"])
        self.assertEqual(3, inherited_acl["ace_count"])
        self.assertEqual(
            {controller.OBJECT_INHERIT_ACE | controller.CONTAINER_INHERIT_ACE | controller.INHERITED_ACE},
            {ace["inherit_flags"] for ace in inherited_acl["aces"]},
        )
        inherited_directory.rmdir()
        inherited_directory.parent.rmdir()
        inherited_directory.parent.parent.rmdir()
        self.assertEqual([], list(Path(first_path).iterdir()))
        self.assertEqual([], list(Path(second_path).iterdir()))
        self.assertEqual("PASS_CREATED_AND_REMOVED_EMPTY_FILE", first_audit["write_delete_probe"])
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_PRIVATE_APPDATA_PROFILE_PATH_AND_EXCLUSIVE_CREATION",
                "first_profile": first_audit,
                "second_profile": second_audit,
            },
        )

    def test_private_profile_parent_acl_checks_all_principals_and_user_documents_source(self):
        run_dir = _new_run_dir("private_appdata_parent_acl")
        user_sid = "S-1-5-21-1000-2000-3000-4000"
        unknown_sid = "S-1-5-21-5000-6000-7000-8000"
        appcontainer_sid = "S-1-15-2-1"
        trusted_aces = [
            {"ace_type": controller.ACCESS_ALLOWED_ACE_TYPE, "sid": user_sid, "mask": controller.FILE_ALL_ACCESS},
            {
                "ace_type": controller.ACCESS_ALLOWED_ACE_TYPE,
                "sid": controller.SYSTEM_SID,
                "mask": controller.FILE_ALL_ACCESS,
            },
            {
                "ace_type": controller.ACCESS_ALLOWED_ACE_TYPE,
                "sid": controller.ADMINISTRATORS_SID,
                "mask": controller.FILE_ALL_ACCESS,
            },
            {
                "ace_type": controller.ACCESS_ALLOWED_ACE_TYPE,
                "sid": controller.OWNER_RIGHTS_SID,
                "mask": controller.FILE_ALL_ACCESS,
            },
        ]
        for principal_sid in (unknown_sid, appcontainer_sid):
            with self.subTest(principal_sid=principal_sid):
                with self.assertRaisesRegex(controller.ControllerError, "非受信任主体具有写入或替换权限"):
                    controller._audit_private_profile_parent_acl(
                        user_sid,
                        user_sid,
                        trusted_aces
                        + [
                            {
                                "ace_type": controller.ACCESS_ALLOWED_ACE_TYPE,
                                "sid": principal_sid,
                                "mask": controller.FILE_DELETE_CHILD,
                            }
                        ],
                    )
        allowed_audit = controller._audit_private_profile_parent_acl(
            user_sid,
            user_sid,
            trusted_aces
            + [
                {
                    "ace_type": controller.ACCESS_ALLOWED_ACE_TYPE,
                    "sid": unknown_sid,
                    "mask": controller.FILE_READ_CONTROL,
                }
            ],
        )
        self.assertEqual("CURRENT_USER", allowed_audit["owner_role"])
        self.assertFalse(allowed_audit["parent_mutable_by_nontrusted_principal"])
        self.assertEqual(1, allowed_audit["nontrusted_readonly_ace_count"])
        for trusted_owner_sid, expected_role in (
            (controller.SYSTEM_SID, "SYSTEM"),
            (controller.ADMINISTRATORS_SID, "ADMINISTRATORS"),
        ):
            with self.subTest(owner_role=expected_role):
                with self.assertRaisesRegex(controller.ControllerError, "非受信任主体具有写入或替换权限"):
                    controller._audit_private_profile_parent_acl(
                        user_sid,
                        trusted_owner_sid,
                        trusted_aces,
                        allowed_owner_sids=(controller.SYSTEM_SID, controller.ADMINISTRATORS_SID),
                    )
        for trusted_owner_sid, expected_role in (
            (controller.SYSTEM_SID, "SYSTEM"),
            (controller.ADMINISTRATORS_SID, "ADMINISTRATORS"),
        ):
            with self.subTest(owner_role=expected_role):
                role_audit = controller._audit_private_profile_parent_acl(
                    user_sid,
                    trusted_owner_sid,
                    trusted_aces[:-1],
                    allowed_owner_sids=(controller.SYSTEM_SID, controller.ADMINISTRATORS_SID),
                )
                self.assertEqual(expected_role, role_audit["owner_role"])
                self.assertFalse(role_audit["parent_mutable_by_nontrusted_principal"])
        with self.assertRaisesRegex(controller.ControllerError, "owner不属于明确允许"):
            controller._audit_private_profile_parent_acl(
                user_sid,
                unknown_sid,
                trusted_aces,
                allowed_owner_sids=(controller.SYSTEM_SID, controller.ADMINISTRATORS_SID),
            )
        with self.assertRaisesRegex(controller.ControllerError, "owner不属于明确允许"):
            controller._audit_private_profile_parent_acl(
                user_sid,
                controller.SYSTEM_SID,
                trusted_aces,
            )
        with self.assertRaisesRegex(controller.ControllerError, "非允许或无法安全评估的ACE"):
            controller._audit_private_profile_parent_acl(
                user_sid,
                user_sid,
                [{"ace_type": 5, "sid": unknown_sid, "mask": controller.FILE_READ_CONTROL}],
            )

        temporary_root = _new_private_temp_root(self)
        user_profile = temporary_root / "fake_user_profile"
        documents = user_profile / "Documents"
        documents.mkdir(parents=True)
        current_user_sid, _groups = controller._current_process_token_sids()
        with mock.patch.dict(os.environ, {"USERPROFILE": str(user_profile)}, clear=False):
            default_root = controller._user_documents_profile_root(current_user_sid)
        self.assertEqual(str(documents.resolve(strict=True)), default_root)
        with mock.patch.object(controller, "_user_documents_profile_root", return_value=str(temporary_root)):
            _profile_path, default_profile_audit = controller._create_private_appdata_profile(
                "user_documents_default_source_fixture",
                profile_nonce="33333333444444445555555566666666",
                vendor_relative_files=["fixture.tcl"],
            )
        self.assertEqual("USER_DOCUMENTS", default_profile_audit["profile_parent_source"])
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_ALL_PARENT_ACES_AUDITED_AND_USER_DOCUMENTS_SOURCE_DERIVED",
                "unknown_mutate_rejected": True,
                "appcontainer_mutate_rejected": True,
                "unknown_readonly_allowed": True,
                "non_allowed_ace_rejected": True,
                "documents_root": default_root,
                "default_profile_parent_source": default_profile_audit["profile_parent_source"],
            },
        )

    def test_real_user_documents_parent_acl_is_read_only_and_summarized(self):
        run_dir = _new_run_dir("real_user_documents_parent_acl")
        user_profile = os.environ.get("USERPROFILE")
        self.assertTrue(user_profile)
        current_user_sid, _groups = controller._current_process_token_sids()
        profile_audits = []
        original_verify = controller._verify_private_profile_parent

        def record_profile_audit(path, current_sid, allowed_owner_sids=None):
            audit = original_verify(
                path,
                current_sid,
                allowed_owner_sids=allowed_owner_sids,
            )
            profile_audits.append(audit)
            return audit

        with mock.patch.object(
            controller,
            "_verify_private_profile_parent",
            side_effect=record_profile_audit,
        ):
            documents_root = controller._user_documents_profile_root(current_user_sid)

        self.assertEqual(1, len(profile_audits))
        profile_audit = profile_audits[0]
        self.assertIn(profile_audit["owner_role"], {"CURRENT_USER", "SYSTEM", "ADMINISTRATORS"})
        self.assertFalse(profile_audit["parent_mutable_by_nontrusted_principal"])
        documents_audit = original_verify(documents_root, current_user_sid)
        self.assertTrue(documents_audit["owner_matches_current_user"])
        self.assertFalse(documents_audit["parent_mutable_by_nontrusted_principal"])
        summary = {
            "production_root_selection_succeeded": True,
            "profile_parent": {
                "owner_role": profile_audit["owner_role"],
                "owner_matches_current_user": profile_audit["owner_matches_current_user"],
                "ace_count": profile_audit["parent_acl_ace_count"],
                "nontrusted_readonly_ace_count": profile_audit[
                    "nontrusted_readonly_ace_count"
                ],
                "parent_mutable_by_nontrusted_principal": profile_audit[
                    "parent_mutable_by_nontrusted_principal"
                ],
            },
            "documents_parent": {
                "owner_matches_current_user": documents_audit["owner_matches_current_user"],
                "ace_count": documents_audit["parent_acl_ace_count"],
                "nontrusted_readonly_ace_count": documents_audit[
                    "nontrusted_readonly_ace_count"
                ],
                "parent_mutable_by_nontrusted_principal": documents_audit[
                    "parent_mutable_by_nontrusted_principal"
                ],
            },
            "documents_contents_changed": False,
            "private_profile_created": False,
        }
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_READ_ONLY_REAL_USERPROFILE_AND_DOCUMENTS_ACL_AUDIT",
                "acl_summary": summary,
            },
        )

    def test_missing_userprofile_rejects_without_touching_shared_temp(self):
        run_dir = _new_run_dir("missing_userprofile_no_temp_fallback")
        shared_temp_root = _new_private_temp_root(self)
        before = tuple(sorted(entry.name for entry in shared_temp_root.iterdir()))

        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("USERPROFILE", None)
            os.environ["TEMP"] = str(shared_temp_root)
            os.environ["TMP"] = str(shared_temp_root)
            with self.assertRaisesRegex(controller.ControllerError, "USERPROFILE未定义"):
                controller._create_private_appdata_profile(
                    "missing_userprofile_default",
                    profile_nonce="55555555666666667777777788888888",
                    vendor_relative_files=["fixture.tcl"],
                )

        after = tuple(sorted(entry.name for entry in shared_temp_root.iterdir()))
        self.assertEqual(before, after)
        self.assertFalse(
            any(name.startswith("s15_appdata_") for name in set(after) - set(before))
        )
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_MISSING_USERPROFILE_FAILS_CLOSED_WITHOUT_TEMP_FALLBACK",
                "temp_contents_unchanged": before == after,
                "before_entry_count": len(before),
                "after_entry_count": len(after),
            },
        )

    def test_private_appdata_profile_length_guard_accepts_259_and_rejects_260(self):
        run_dir = _new_run_dir("private_appdata_path_length")
        appdata = run_dir / "p"
        store_root = appdata / "Xilinx" / "Vivado" / controller.EXPECTED_VIVADO_VERSION / "XilinxTclStore"
        needed_component_length = 259 - controller._windows_path_utf16_chars(store_root) - 1
        self.assertGreater(needed_component_length, 0)
        self.assertLessEqual(needed_component_length + 1, 255)
        accepted = controller._private_appdata_path_length_audit(
            appdata,
            ["x" * needed_component_length],
        )
        self.assertEqual(259, accepted["longest_destination_path_utf16_chars"])
        with self.assertRaisesRegex(controller.ControllerError, "超过259 UTF-16字符"):
            controller._private_appdata_path_length_audit(
                appdata,
                ["x" * (needed_component_length + 1)],
            )
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_PRIVATE_APPDATA_PATH_LENGTH_BOUNDARY", "accepted_chars": 259, "rejected_chars": 260},
        )

    def test_user_documents_profile_path_fits_deepest_installed_tclstore_destination(self):
        run_dir = _new_run_dir("user_documents_tclstore_path_length")
        user_profile = os.environ.get("USERPROFILE")
        self.assertTrue(user_profile)
        documents_root = str(Path(user_profile) / "Documents")
        run_id = "documents_tclstore_path_length"
        profile_digest = controller.hashlib.sha256(run_id.encode("ascii")).hexdigest()[:8].upper()
        profile_path = Path(documents_root) / f"s15_appdata_{profile_digest}_{'0' * 32}"
        vendor_files = controller._vendor_tclstore_relative_files()
        audit = controller._private_appdata_path_length_audit(profile_path, vendor_files)
        self.assertGreater(audit["vendor_file_count"], 0)
        self.assertLessEqual(audit["longest_destination_path_utf16_chars"], 259)
        self.assertTrue(audit["all_destination_paths_within_limit"])
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_USER_DOCUMENTS_DEEPEST_TCLSTORE_PATH_WITHIN_259_UTF16_CHARS",
                "vendor_file_count": audit["vendor_file_count"],
                "longest_vendor_relative_path": audit["longest_vendor_relative_path"],
                "longest_destination_path_utf16_chars": audit["longest_destination_path_utf16_chars"],
                "documents_root": documents_root,
            },
        )

    def test_private_appdata_profile_refuses_existing_path_without_reuse(self):
        run_dir = _new_run_dir("private_appdata_profile_reuse")
        temporary_root = _new_private_temp_root(self)
        nonce = "0123456789abcdef0123456789abcdef"
        profile_path, _audit = controller._create_private_appdata_profile(
            run_dir.name,
            profile_nonce=nonce,
            temporary_root=temporary_root,
            vendor_relative_files=["one.tcl"],
        )
        with self.assertRaisesRegex(controller.ControllerError, "拒绝复用已存在APPDATA profile路径"):
            controller._create_private_appdata_profile(
                run_dir.name,
                profile_nonce=nonce,
                temporary_root=temporary_root,
                vendor_relative_files=["one.tcl"],
            )
        self.assertTrue(Path(profile_path).is_dir())
        self.assertEqual([], list(Path(profile_path).iterdir()))
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_EXISTING_PRIVATE_APPDATA_PATH_REJECTED", "profile_path": profile_path},
        )

    def test_private_appdata_profile_rolls_back_own_empty_directory_after_probe_failure(self):
        run_dir = _new_run_dir("private_appdata_profile_probe_rollback")
        temporary_root = _new_private_temp_root(self)
        nonce = "11111111222222223333333344444444"
        profile_id = f"{controller.hashlib.sha256(run_dir.name.encode('ascii')).hexdigest()[:8].upper()}_{nonce}"
        expected_profile = temporary_root / f"s15_appdata_{profile_id}"
        with mock.patch.object(controller.os, "open", side_effect=OSError("injected probe create failure")):
            with self.assertRaisesRegex(OSError, "injected probe create failure"):
                controller._create_private_appdata_profile(
                    run_dir.name,
                    profile_nonce=nonce,
                    temporary_root=temporary_root,
                    vendor_relative_files=["one.tcl"],
                )
        self.assertFalse(expected_profile.exists())
        _write_json(
            run_dir / "fixture_result.json",
            {"status": "PASS_PRIVATE_PROFILE_OWN_EMPTY_DIRECTORY_ROLLED_BACK", "profile_path_absent": True},
        )

    def test_private_appdata_profile_preserves_unowned_content_on_rollback(self):
        run_dir = _new_run_dir("private_appdata_profile_rollback_preserve")
        temporary_root = _new_private_temp_root(self)
        nonce = "22222222333333334444444455555555"
        profile_id = f"{controller.hashlib.sha256(run_dir.name.encode('ascii')).hexdigest()[:8].upper()}_{nonce}"
        expected_profile = temporary_root / f"s15_appdata_{profile_id}"
        unexpected = expected_profile / "unexpected.marker"
        original_open = controller.os.open

        def fail_after_adding_unexpected_content(path, flags, mode=0o777):
            if Path(path) == expected_profile / ".s15_write_delete_probe":
                unexpected.write_text("test-owned injected entry", encoding="utf-8")
                raise OSError("injected unowned entry")
            return original_open(path, flags, mode)

        with mock.patch.object(controller.os, "open", side_effect=fail_after_adding_unexpected_content):
            with self.assertRaisesRegex(controller.ControllerError, "保留路径") as raised:
                controller._create_private_appdata_profile(
                    run_dir.name,
                    profile_nonce=nonce,
                    temporary_root=temporary_root,
                    vendor_relative_files=["one.tcl"],
                )
        self.assertIn(expected_profile.name, str(raised.exception))
        self.assertTrue(expected_profile.is_dir())
        self.assertTrue(unexpected.is_file())
        unexpected.unlink()
        expected_profile.rmdir()
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_PRIVATE_PROFILE_UNKNOWN_CONTENT_PRESERVED",
                "profile_preserved_until_test_removed_its_exact_injected_file": True,
            },
        )

    def test_inherited_setup_environment_overrides_are_rejected_before_any_vivado_job(self):
        run_dir = _new_run_dir("setup_env_hook_rejected")
        rejected = []
        rejection_reasons = {}
        for name in controller.VIVADO_SETUP_ENVIRONMENT_VARIABLES:
            with mock.patch.dict(os.environ, {name: "PARENT_INJECTED_VALUE"}, clear=False):
                with mock.patch.object(controller.job_guard, "JobObject") as job_factory:
                    with mock.patch.object(controller.job_guard, "launch_suspended_root") as launch_root:
                        with mock.patch.object(controller, "_run_prelaunch_check") as redist_precheck:
                            with mock.patch.object(controller, "_create_unique_run_dir") as create_run_dir:
                                with self.assertRaisesRegex(
                                    controller.ControllerError,
                                    rf"Vivado setupEnv环境覆盖拒绝：.*{name}",
                                ) as raised:
                                    controller.run_frozen_bitgen()
                                self.assertIn(name, str(raised.exception))
                                rejection_reasons[name] = str(raised.exception)
                                job_factory.assert_not_called()
                                launch_root.assert_not_called()
                                redist_precheck.assert_not_called()
                                create_run_dir.assert_not_called()
                                rejected.append(name)
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_SETUP_ENVIRONMENT_OVERRIDES_REJECTED_BEFORE_ANY_PROCESS_LAUNCH",
                "injected_environment_variables": rejected,
                "preflight_rejections": rejection_reasons,
                "vivado_job_object_calls": 0,
                "vivado_root_launch_calls": 0,
                "redist_precheck_calls": 0,
                "run_directory_creation_calls": 0,
            },
        )

    def test_child_environment_scrubs_setupenv_path_and_hook_overrides(self):
        run_dir = _new_run_dir("setup_env_overrides_scrubbed")
        source_appdata = run_dir / "source_appdata"
        source_appdata.mkdir()
        license_file = run_dir / "fixture_license.lic"
        license_file.write_bytes(b"fixture-only license metadata\n")
        injected = {
            "APPDATA": str(source_appdata),
            "XILINXD_LICENSE_FILE": str(license_file),
            "RDI_SETUP_ENV_FUNCTION": "PARENT_INJECTED_LABEL",
            "RDI_BINROOT": r"D:\\attacker\\bin",
            "RDI_APPROOT": r"D:\\attacker",
        }
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(os.environ, injected, clear=False):
            environment, _isolated_appdata, _license_audit, _profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
        for name in controller.VIVADO_SETUP_ENVIRONMENT_VARIABLES:
            self.assertNotIn(name, environment)
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_SETUP_ENVIRONMENT_OVERRIDES_REMOVED_FROM_CHILD",
                "injected_variables": ["RDI_SETUP_ENV_FUNCTION", "RDI_BINROOT", "RDI_APPROOT"],
                "child_override_variables_absent": list(controller.VIVADO_SETUP_ENVIRONMENT_VARIABLES),
            },
        )

    def test_xvcredist_link_validator_accepts_only_exact_relative_target(self):
        run_dir = _new_run_dir("xvcredist_link_target_guard")
        link_directory = Path(controller.XVCREDIST_LINK_DIRECTORY)
        resolved_target = Path(controller.XVCREDIST_RESOLVED_ROOT)
        with self.assertRaisesRegex(controller.ControllerError, "链接文本目标"):
            controller._validate_xvcredist_link_observation(link_directory, r"..\other", resolved_target)
        with self.assertRaisesRegex(controller.ControllerError, "严格解析目标"):
            controller._validate_xvcredist_link_observation(link_directory, r"..\tps", resolved_target / "elsewhere")
        accepted = controller._validate_xvcredist_link_observation(
            link_directory,
            r"..\tps",
            resolved_target,
        )
        self.assertEqual(r"..\tps", accepted["link_target"])
        self.assertEqual(
            os.path.normcase(os.path.abspath(controller.XVCREDIST_RESOLVED_ROOT)),
            os.path.normcase(os.path.abspath(accepted["resolved_target_path"])),
        )
        actual_executable, actual_link = controller._resolve_xvcredist_executable()
        self.assertEqual(controller.XVCREDIST_LINK_TARGET, actual_link["link_target"])
        self.assertEqual(controller.XVCREDIST_RESOLVED_ROOT, actual_link["resolved_target_path"])
        self.assertEqual(
            os.path.normcase(os.path.abspath(controller.XVCREDIST_RESOLVED_ROOT)),
            os.path.normcase(os.path.abspath(Path(actual_executable).parents[1])),
        )
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "PASS_XVCREDIST_LINK_TARGET_GUARD",
                "rejected_link_target": r"..\other",
                "rejected_resolved_target": str(resolved_target / "elsewhere"),
                "accepted_link_target": accepted["link_target"],
                "accepted_resolved_target": accepted["resolved_target_path"],
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
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(
            os.environ,
            {"APPDATA": str(source_appdata), "XILINXD_LICENSE_FILE": str(license_file)},
            clear=False,
        ):
            audit = controller._audit_user_init_scripts(source_appdata)
            environment, isolated_appdata, _license_audit, profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
        self.assertTrue(audit["source_scripts"][0]["exists"])
        self.assertFalse(audit["copied_to_child_appdata"])
        self.assertFalse((Path(isolated_appdata) / "Xilinx" / "Vivado" / controller.EXPECTED_VIVADO_VERSION / "Vivado_init.tcl").exists())
        self.assertEqual(isolated_appdata, environment["APPDATA"])
        self.assertEqual(isolated_appdata, profile_audit["path"])
        self.assertNotIn(str(source_appdata), json.dumps(profile_audit, ensure_ascii=False))
        self.assertLessEqual(profile_audit["path_length_audit"]["longest_destination_path_utf16_chars"], 259)
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
        private_temp_root = _new_private_temp_root(self)
        with mock.patch.dict(os.environ, environment, clear=False):
            audit = controller._audit_license_configuration(environment, source_appdata)
            child_environment, isolated_appdata, child_audit, _profile_audit = _child_environment_fixture(
                run_dir, private_temp_root
            )
        self.assertTrue(audit["usable"])
        self.assertTrue(audit["default_license_used"])
        self.assertEqual(str(license_file), child_environment["XILINXD_LICENSE_FILE"])
        self.assertEqual(isolated_appdata, child_environment["APPDATA"])
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
        self.assertEqual({"vivado.bat", "loader.bat", "rdiArgs.bat", "setupEnv.bat"}, set(call_chain))
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
        runner_source = inspect.getsource(controller.run_frozen_bitgen)
        precheck_source = inspect.getsource(controller._run_prelaunch_check)
        prepare_index = runner_source.index("input_locks = _prepare_run_inputs(run_dir, facts)")
        profile_index = runner_source.index("child_environment, isolated_appdata, license_audit, appdata_profile_audit = _child_environment(run_dir)")
        profile_record_index = runner_source.index('manifest["process_launch"]["private_appdata_profile"] = appdata_profile_audit')
        precheck_index = runner_source.index("redist_check = _run_prelaunch_check(")
        job_index = runner_source.index("job = job_guard.JobObject(kill_on_close=True)")
        launch_index = runner_source.index("child = job_guard.launch_suspended_root(")
        self.assertLess(prepare_index, launch_index)
        self.assertLess(prepare_index, precheck_index)
        self.assertLess(prepare_index, profile_index)
        self.assertLess(profile_index, profile_record_index)
        self.assertLess(profile_record_index, precheck_index)
        self.assertIn('"private_appdata_profile": None', runner_source)
        self.assertLess(precheck_index, launch_index)
        self.assertLess(precheck_index, job_index)
        self.assertEqual(1, runner_source.count("child = job_guard.launch_suspended_root("))
        self.assertIn("job_guard.launch_suspended_root(", precheck_source)

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


@unittest.skipUnless(os.name == "nt", "终态Job读回单元测试依赖Windows JobObject状态常量")
class TerminalExitRaceReconciliationTests(unittest.TestCase):
    """验证退出沿采样不确定性只在完整Job终态闭合后收敛。"""

    class FakeJob:
        def __init__(self, total_processes=2):
            self.total_processes = total_processes
            self.pid_calls = 0
            self.accounting_calls = 0

        def pid_list(self):
            self.pid_calls += 1
            return []

        def accounting(self):
            self.accounting_calls += 1
            return {
                "total_processes": self.total_processes,
                "active_processes": 0,
                "terminated_processes": 0,
                "exited_processes": self.total_processes,
                "page_faults": 0,
            }

    class FakeChild:
        def __init__(self, closure, wait_error=None, close_on_wait=True):
            self.pid = 25308
            self.birth_ticks = 9001
            self.closure = closure
            self.wait_error = wait_error
            self.close_on_wait = close_on_wait
            self.closed = False
            self.wait_calls = 0

        def wait_and_close(self, timeout_seconds=30.0):
            self.wait_calls += 1
            if self.wait_error is not None:
                raise self.wait_error
            if self.close_on_wait:
                self.closed = True
            return self.closure

    @staticmethod
    def _no_such_process_readback(pid, message="process PID not found"):
        error = job_guard.psutil.NoSuchProcess(pid=pid, msg=message)
        wrapped = job_guard.GateBlocked(f"六字段无法读取：{error!r}")
        return f"MEMBER_READBACK_FAILED:{pid}:{wrapped!r}"

    @staticmethod
    def _terminal_fixture(total_processes=2, root_exit_code=0):
        root_key = (25308, 9001)
        vivado_key = (472, 7002)
        readbacks = [
            {
                "pid": pid,
                "birth_ticks": ticks,
                "status": "EXITED",
                "exit_code": root_exit_code if pid == root_key[0] else 0,
            }
            for pid, ticks in (root_key, vivado_key)
        ]
        closure = {
            "final": {
                "job_pids": [],
                "active_processes": 0,
                "total_processes": total_processes,
                "total_terminated_processes": 0,
                "exited_processes": total_processes,
                "root_handle_signaled": True,
                "root_native_handle_exit_code": root_exit_code,
                "root_native_handle_pid": root_key[0],
                "root_native_handle_birth_ticks": root_key[1],
                "member_readbacks": readbacks,
                "live_members": [],
                "unknown_members": [],
            }
        }
        sample = {
            "uncertainty": [
                TerminalExitRaceReconciliationTests._no_such_process_readback(root_key[0]),
                TerminalExitRaceReconciliationTests._no_such_process_readback(vivado_key[0]),
                "PID_LIST_CHANGED_DURING_SAMPLE",
                "JOB_PROCESS_COUNTER_CHANGED_DURING_SAMPLE",
            ],
            "job_pids_before": [root_key[0], vivado_key[0]],
            "job_pids_after": [],
            "accounting_before": {
                "total_processes": 2,
                "active_processes": 2,
                "terminated_processes": 0,
                "exited_processes": 0,
            },
            "accounting_after": {
                "total_processes": 2,
                "active_processes": 0,
                "terminated_processes": 0,
                "exited_processes": 2,
            },
            "member_measurements": [],
            "tree_rss_bytes": 0,
        }
        previous_keys = {root_key, vivado_key}
        previous_accounting = {"total_processes": 2, "exited_processes": 0}
        observations = [{"pid": vivado_key[0], "birth_ticks": vivado_key[1]}]
        return sample, previous_keys, previous_accounting, observations, closure

    def _run_reconciliation(
        self, label, *, alerts=None, root_wait=None, root_exit_code=0, final_total=2, closure_total=None
    ):
        sample, previous_keys, previous_accounting, observations, closure = self._terminal_fixture(
            final_total if closure_total is None else closure_total, root_exit_code
        )
        job = self.FakeJob(total_processes=final_total)
        child = self.FakeChild(closure)
        result = controller._reconcile_terminal_exit_race(
            job,
            child,
            sample,
            ["SAMPLE_UNCERTAIN"] if alerts is None else alerts,
            previous_keys,
            previous_accounting,
            job_guard.WAIT_OBJECT_0 if root_wait is None else root_wait,
            root_exit_code,
            observations,
        )
        receipt_dir = _new_run_dir(label)
        _write_json(
            receipt_dir / "fixture_result.json",
            {
                "status": "PASS_TERMINAL_RACE_RECONCILED" if result["reconciled"] else "HARD_STOP_TERMINAL_RACE_REJECTED",
                "result": result,
                "job_pid_read_count": job.pid_calls,
                "job_accounting_read_count": job.accounting_calls,
                "child_wait_and_close_calls": child.wait_calls,
                "child_closed": child.closed,
            },
        )
        return result, job, child, receipt_dir

    def test_terminal_exit_race_reconciles_after_complete_closure(self):
        result, job, child, receipt_dir = self._run_reconciliation("terminal_race_reconciled")
        self.assertTrue(result["reconciled"], result["reason"])
        self.assertEqual(2, job.pid_calls)
        self.assertEqual(2, job.accounting_calls)
        self.assertEqual(1, child.wait_calls)
        self.assertTrue(child.closed)
        self.assertEqual("PASS_TERMINAL_RACE_RECONCILED", json.loads((receipt_dir / "fixture_result.json").read_text(encoding="utf-8"))["status"])

    def test_exact_process_pid_not_found_readback_is_supported(self):
        for message in ("process PID not found", "process no longer exists"):
            with self.subTest(message=message):
                sample, previous_keys, previous_accounting, _observations, closure = self._terminal_fixture()
                sample["uncertainty"][0] = self._no_such_process_readback(25308, message)
                self.assertTrue(
                    controller._NO_SUCH_PROCESS_READBACK.fullmatch(sample["uncertainty"][0]),
                    sample["uncertainty"][0],
                )
                accepted, reason = controller._terminal_exit_sample_is_reconcilable(
                    sample,
                    ["SAMPLE_UNCERTAIN"],
                    previous_keys,
                    previous_accounting,
                    self.FakeChild(closure),
                )
                self.assertTrue(accepted, reason)

    def test_untracked_transient_child_count_mismatch_remains_hard_stop(self):
        result, job, child, receipt_dir = self._run_reconciliation(
            "terminal_race_untracked_count", final_total=2, closure_total=3
        )
        self.assertFalse(result["reconciled"])
        self.assertIn("数量与Job total_processes不一致", result["reason"])
        self.assertEqual(1, child.wait_calls)
        self.assertTrue(child.closed)
        self.assertEqual(2, len(result["closure"]["final"]["member_readbacks"]))
        self.assertEqual(3, result["closure"]["final"]["total_processes"])
        transition = controller._terminal_exit_race_runner_transition(
            ["SAMPLE_UNCERTAIN"], result
        )
        self.assertFalse(transition["reconciled"])
        self.assertTrue(transition["release_child"])
        self.assertIs(transition["closure"], result["closure"])
        self.assertTrue(transition["stop_reason"].startswith("HARD_STOP:"))
        receipt = json.loads((receipt_dir / "fixture_result.json").read_text(encoding="utf-8"))
        self.assertEqual("HARD_STOP_TERMINAL_RACE_REJECTED", receipt["status"])

    def test_resource_and_no_progress_alerts_remain_hard_stop(self):
        for alert in ("AVAILABLE_RAM_LT_512_MIB", "C_DISK_FREE_LT_8_GIB", "NO_PROGRESS_GE_900S"):
            with self.subTest(alert=alert):
                result, job, child, _receipt_dir = self._run_reconciliation(
                    "terminal_race_alert_" + alert.lower(),
                    alerts=["SAMPLE_UNCERTAIN", alert],
                )
                self.assertFalse(result["reconciled"])
                self.assertIn("alerts不是单独的SAMPLE_UNCERTAIN", result["reason"])
                self.assertEqual(0, job.pid_calls)
                self.assertEqual(0, child.wait_calls)

    def test_access_denied_and_other_member_errors_remain_hard_stop(self):
        for label, error in (
            (
                "access_denied",
                "MEMBER_READBACK_FAILED:25308:GateBlocked(\"六字段无法读取：psutil.AccessDenied(pid=25308)\")",
            ),
            (
                "pid_reused_message",
                "MEMBER_READBACK_FAILED:25308:GateBlocked(\"六字段无法读取：psutil.NoSuchProcess(pid=25308, msg='process no longer exists and its PID has been reused')\")",
            ),
            ("other_error", "MEMBER_READBACK_FAILED:25308:GateBlocked(\"六字段无法读取：OSError(5)\")"),
            ("untyped_error", "MEMBER_READBACK_FAILED:25308:exited during sample"),
        ):
            with self.subTest(label=label):
                sample, _keys, _accounting, _observations, _closure = self._terminal_fixture()
                sample["uncertainty"][0] = error
                self._assert_sample_rejected(label, sample)

    def _assert_sample_rejected(self, label, sample):
        _unused_sample, previous_keys, previous_accounting, observations, closure = self._terminal_fixture()
        sample.pop("tree_rss_bytes", None) if label == "rss_absent" else None
        job = self.FakeJob()
        child = self.FakeChild(closure)
        result = controller._reconcile_terminal_exit_race(
            job,
            child,
            sample,
            ["SAMPLE_UNCERTAIN"],
            previous_keys,
            previous_accounting,
            job_guard.WAIT_OBJECT_0,
            0,
            observations,
        )
        self.assertFalse(result["reconciled"], label)
        self.assertEqual(0, job.pid_calls, label)
        self.assertEqual(0, child.wait_calls, label)

    def test_missing_or_over_limit_tree_rss_remains_hard_stop(self):
        sample, *_unused = self._terminal_fixture()
        sample["tree_rss_bytes"] = None
        self._assert_sample_rejected("rss_missing", sample)

        sample, *_unused = self._terminal_fixture()
        sample.pop("tree_rss_bytes")
        self._assert_sample_rejected("rss_absent", sample)

        sample, *_unused = self._terminal_fixture()
        sample["tree_rss_bytes"] = -1
        self._assert_sample_rejected("rss_negative", sample)

        sample, *_unused = self._terminal_fixture()
        sample["tree_rss_bytes"] = job_guard.RSS_LIMIT_BYTES + 1
        self._assert_sample_rejected("rss_over_limit", sample)

    def test_job_sample_reports_terminal_empty_rss_and_keeps_unproven_sample_unavailable(self):
        job = job_guard.JobObject(kill_on_close=True)
        try:
            with (
                mock.patch.object(job_guard, "_memory_status", return_value=(1024, 2048)),
                mock.patch.object(job_guard, "_disk_free_c", return_value=4096),
            ):
                empty_sample = job.sample()
            self.assertEqual([], empty_sample["job_pids_after"])
            self.assertEqual(0, empty_sample["tree_rss_bytes"])
            self.assertIn("exited_processes=total_processes", empty_sample["rss_metric"])

            disappearing_pid = 48123
            job.root_pid = disappearing_pid
            readback_error = job_guard.psutil.NoSuchProcess(
                pid=disappearing_pid, msg="process PID not found"
            )
            accounting_before = {
                "total_processes": 1,
                "active_processes": 1,
                "terminated_processes": 0,
                "exited_processes": 0,
            }
            accounting_terminal = {
                "total_processes": 1,
                "active_processes": 0,
                "terminated_processes": 0,
                "exited_processes": 1,
            }
            with (
                mock.patch.object(job, "pid_list", side_effect=[[disappearing_pid], []]),
                mock.patch.object(job, "accounting", side_effect=[accounting_before, accounting_terminal]),
                mock.patch.object(job, "_remember_process", side_effect=readback_error),
                mock.patch.object(job_guard, "_memory_status", return_value=(1024, 2048)),
                mock.patch.object(job_guard, "_disk_free_c", return_value=4096),
            ):
                terminal_sample = job.sample()
            self.assertEqual(0, terminal_sample["tree_rss_bytes"])
            self.assertIn("MEMBER_READBACK_FAILED:", terminal_sample["uncertainty"][0])

            accounting_not_terminal = dict(accounting_terminal, exited_processes=0)
            with (
                mock.patch.object(job, "pid_list", side_effect=[[disappearing_pid], []]),
                mock.patch.object(job, "accounting", side_effect=[accounting_before, accounting_not_terminal]),
                mock.patch.object(job, "_remember_process", side_effect=readback_error),
                mock.patch.object(job_guard, "_memory_status", return_value=(1024, 2048)),
                mock.patch.object(job_guard, "_disk_free_c", return_value=4096),
            ):
                uncertain_sample = job.sample()
            self.assertIsNone(uncertain_sample["tree_rss_bytes"])
        finally:
            job.close()

    def test_final_closure_rejects_root_birth_and_observed_vivado_identity_mismatch(self):
        for label, mutate in (
            (
                "root_birth_mismatch",
                lambda closure: closure["final"].__setitem__("root_native_handle_birth_ticks", 9002),
            ),
            (
                "observed_vivado_birth_mismatch",
                lambda closure: closure["final"]["member_readbacks"][1].__setitem__("birth_ticks", 7003),
            ),
        ):
            with self.subTest(label=label):
                sample, previous_keys, previous_accounting, observations, closure = self._terminal_fixture()
                mutate(closure)
                job = self.FakeJob()
                child = self.FakeChild(closure)
                result = controller._reconcile_terminal_exit_race(
                    job,
                    child,
                    sample,
                    ["SAMPLE_UNCERTAIN"],
                    previous_keys,
                    previous_accounting,
                    job_guard.WAIT_OBJECT_0,
                    0,
                    observations,
                )
                self.assertFalse(result["reconciled"], result["reason"])
                self.assertIn(
                    "精确root句柄" if label == "root_birth_mismatch" else "此前样本观察到的Job成员身份",
                    result["reason"],
                )

    def test_runner_reconciled_branch_skips_cleanup_but_nonzero_exit_stays_failed(self):
        for exit_code, expected_reason in ((0, None), (1, "NATIVE_CMD_ROOT_EXIT_NONZERO_1")):
            with self.subTest(exit_code=exit_code):
                sample, previous_keys, previous_accounting, observations, closure = self._terminal_fixture(
                    root_exit_code=exit_code
                )
                job = self.FakeJob()
                child = self.FakeChild(closure)
                with mock.patch.object(controller, "_kill_and_close") as kill_and_close:
                    runner_result = controller._resolve_terminal_exit_race_for_runner(
                        job,
                        child,
                        sample,
                        ["SAMPLE_UNCERTAIN"],
                        previous_keys,
                        previous_accounting,
                        job_guard.WAIT_OBJECT_0,
                        exit_code,
                        observations,
                    )
                result = runner_result["reconciliation"]
                transition = runner_result["transition"]
                self.assertTrue(result["reconciled"], result["reason"])
                kill_and_close.assert_not_called()
                self.assertIsNone(runner_result["child"])
                self.assertIsNone(runner_result["cleanup_record"])
                self.assertIs(closure, runner_result["closure"])
                cleanup = mock.Mock()
                if transition["stop_reason"]:
                    cleanup(transition["stop_reason"])
                cleanup.assert_not_called()
                self.assertTrue(transition["release_child"])
                self.assertIsNone(transition["stop_reason"])
                final_reason = controller._ensure_native_exit_diagnostic(
                    transition["closure"], exit_code, transition["stop_reason"]
                )
                self.assertEqual(expected_reason, final_reason)

                digest = "A" * 64
                manifest = {
                    "process_launch": {
                        "vivado_member_observations": [{"pid": 472, "birth_ticks": 7002}]
                    },
                    "input_paths_and_hashes": {},
                }
                writer = mock.Mock()
                writer.manifest = manifest
                input_facts = {
                    "dcp_path": "fixture-dcp",
                    "dcp_copy_path": "fixture-dcp-copy",
                    "dcp_sha256": digest,
                    "tcl_source_path": "fixture-tcl",
                    "tcl_copy_path": "fixture-tcl-copy",
                    "tcl_source_sha256": digest,
                    "vivado_executable_path": "fixture-vivado",
                    "vivado_executable_sha256": digest,
                    "toolchain_files": {"vivado.exe": {"path": "fixture-vivado.exe", "sha256": digest}},
                    "controller_source_path": "fixture-controller",
                    "controller_source_sha256": digest,
                }
                outputs = {
                    name: "fixture-" + name
                    for name in (
                        "vivado_log",
                        "vivado_journal",
                        "stdout",
                        "stderr",
                        "tcl_progress",
                        "bitstream",
                        "monitor",
                    )
                }
                progress = [
                    {"event": "vivado_version", "detail": controller.EXPECTED_VIVADO_VERSION},
                    {"event": "checkpoint_opened", "detail": controller.EXPECTED_PART},
                    {"event": "write_bitstream_complete", "detail": "5"},
                ]
                artifact = {"exists": True, "size_bytes": 5, "sha256": digest}
                with (
                    mock.patch.object(controller, "_read_progress", return_value=progress),
                    mock.patch.object(controller, "_read_monitor", return_value=[{"event": "sample"}]),
                    mock.patch.object(controller, "_artifact_record", return_value=artifact),
                    mock.patch.object(controller, "_sha256_if_present", return_value=digest),
                    mock.patch.object(controller, "_validate_success_artifacts", return_value={"valid": True}),
                ):
                    finalized = controller._finalize_manifest(
                        writer,
                        "fixture-run",
                        input_facts,
                        outputs,
                        {},
                        exit_code,
                        final_reason,
                        runner_result["closure"],
                        [],
                    )
                self.assertEqual(
                    "BITGEN_COMPLETE_SOFTWARE_ONLY" if exit_code == 0 else "FAILED_OR_INCOMPLETE",
                    finalized["status"],
                )
                self.assertEqual(expected_reason, finalized["stop_reason"])

        for label, child_kwargs in (
            ("closure_exception", {"wait_error": RuntimeError("fixture closure failure")}),
            ("closure_not_closed", {"close_on_wait": False}),
        ):
            with self.subTest(label=label):
                sample, previous_keys, previous_accounting, observations, closure = self._terminal_fixture()
                child = self.FakeChild(closure, **child_kwargs)
                job = self.FakeJob()
                cleanup_record = {
                    "closure": None,
                    "root_native_exit_code": None,
                    "reason": "fixture cleanup",
                }
                with mock.patch.object(
                    controller, "_kill_and_close", return_value=cleanup_record
                ) as kill_and_close:
                    runner_result = controller._resolve_terminal_exit_race_for_runner(
                        job,
                        child,
                        sample,
                        ["SAMPLE_UNCERTAIN"],
                        previous_keys,
                        previous_accounting,
                        job_guard.WAIT_OBJECT_0,
                        0,
                        observations,
                    )
                self.assertFalse(runner_result["transition"]["reconciled"])
                self.assertTrue(runner_result["transition"]["stop_reason"].startswith("HARD_STOP:"))
                self.assertIsNone(runner_result["child"])
                self.assertIs(cleanup_record, runner_result["cleanup_record"])
                kill_and_close.assert_called_once_with(
                    child, runner_result["transition"]["stop_reason"]
                )

    def test_root_live_or_unknown_remains_hard_stop(self):
        for root_wait in (job_guard.WAIT_TIMEOUT, 0xFFFFFFFF):
            with self.subTest(root_wait=root_wait):
                result, job, child, _receipt_dir = self._run_reconciliation(
                    "terminal_race_root_wait_" + str(root_wait), root_wait=root_wait
                )
                self.assertFalse(result["reconciled"])
                self.assertIn("root原生句柄仍活动或等待状态未知", result["reason"])
                self.assertEqual(0, job.pid_calls)
                self.assertEqual(0, child.wait_calls)

        result, job, child, _receipt_dir = self._run_reconciliation(
            "terminal_race_root_still_active", root_exit_code=job_guard.STILL_ACTIVE
        )
        self.assertFalse(result["reconciled"])
        self.assertEqual(0, job.pid_calls)
        self.assertEqual(0, child.wait_calls)

    def test_nonzero_native_exit_keeps_failed_diagnostic_reason(self):
        run_dir = _new_run_dir("terminal_race_nonzero_root_exit")
        closure = {"final": {"root_native_handle_exit_code": 1}}
        no_prior_stop = controller._ensure_native_exit_diagnostic(closure, 1, None)
        hard_stop = controller._ensure_native_exit_diagnostic(closure, 1, "HARD_STOP:SAMPLE_UNCERTAIN")
        zero_exit = controller._ensure_native_exit_diagnostic(closure, 0, None)
        self.assertEqual("NATIVE_CMD_ROOT_EXIT_NONZERO_1", no_prior_stop)
        self.assertEqual("HARD_STOP:SAMPLE_UNCERTAIN:NATIVE_CMD_ROOT_EXIT_NONZERO_1", hard_stop)
        self.assertIsNone(zero_exit)
        _write_json(
            run_dir / "fixture_result.json",
            {
                "status": "FAILED_OR_INCOMPLETE",
                "native_root_exit_code": 1,
                "stop_reason": no_prior_stop,
                "hard_stop_with_diagnostic": hard_stop,
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
