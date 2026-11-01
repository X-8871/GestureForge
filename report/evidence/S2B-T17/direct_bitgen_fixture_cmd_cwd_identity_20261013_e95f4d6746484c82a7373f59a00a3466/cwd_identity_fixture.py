import json
import os
import sys
import time
import traceback
from pathlib import Path


REPOSITORY = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
sys.path.insert(0, str(REPOSITORY / "verification"))
import s15_job_guard as job_guard
import s15_direct_vivado_bitgen as controller


EVIDENCE_DIR = Path(__file__).resolve().parent
IDENTITY_FIELDS = ("pid", "create_time", "exe", "cwd", "cmdline", "ppid")
PYTHON_EXE = str(Path(sys.executable).resolve())


def _write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write("\n")


def _scenario(name, initial_cwd_mode):
    scenario_dir = EVIDENCE_DIR / name
    scenario_dir.mkdir()
    fake_bin = scenario_dir / "fixture_vivado_bin"
    fake_bin.mkdir()
    child_script = scenario_dir / "short_child.py"
    child_receipt = scenario_dir / "short_child_receipt.json"
    batch_path = fake_bin / "fixture_launcher.bat"
    stdout_path = scenario_dir / "stdout.log"
    stderr_path = scenario_dir / "stderr.log"
    child_script.write_text(
        "import json,os,pathlib,sys,time\n"
        "time.sleep(0.6)\n"
        "pathlib.Path(sys.argv[1]).write_text(json.dumps({'cwd':os.getcwd(),'pid':os.getpid(),'ppid':os.getppid()}),encoding='utf-8')\n",
        encoding="utf-8",
        newline="\n",
    )
    batch_path.write_text(
        "@echo off\r\n"
        "setlocal EnableExtensions DisableDelayedExpansion\r\n"
        "set \"_S15_ORIGINAL_CWD=%CD%\"\r\n"
        "pushd \"%~dp0\"\r\n"
        "set \"_S15_BATCH_CWD=%CD%\"\r\n"
        "for /l %%N in (1,1,20000) do @set \"_S15_SPIN=%%N\"\r\n"
        "cd /d \"%_S15_ORIGINAL_CWD%\"\r\n"
        f'"{PYTHON_EXE}" "{child_script}" "{child_receipt}"\r\n'
        "set \"_S15_CHILD_EXIT=%errorlevel%\"\r\n"
        "popd\r\n"
        "exit /b 37\r\n",
        encoding="utf-8",
        newline="",
    )
    initial_cwd = scenario_dir if initial_cwd_mode == "run_directory" else fake_bin
    argv, command = controller._build_cmd_batch_argv(
        controller.CMD_EXE,
        str(batch_path),
        [str(child_receipt)],
    )
    identity_trace = []
    real_identity_reader = job_guard._api_process_identity

    def traced_identity_reader(pid):
        identity = real_identity_reader(pid)
        identity_trace.append({"monotonic_seconds": time.monotonic(), "identity": identity})
        return identity

    job = job_guard.JobObject(kill_on_close=True)
    child = None
    std_handles = None
    std_streams = ()
    locks = []
    original_api_reader = job_guard._api_process_identity
    closure = None
    sample_records = []
    result = {
        "scenario": name,
        "initial_cwd_mode": initial_cwd_mode,
        "initial_cwd": str(initial_cwd),
        "batch_directory": str(fake_bin),
        "argv": argv,
        "batch_command": command,
        "identity_fields": list(IDENTITY_FIELDS),
        "identity_trace": identity_trace,
        "samples": sample_records,
    }
    try:
        locks = [
            controller.InputReadLock(controller.CMD_EXE),
            controller.InputReadLock(str(batch_path)),
            controller.InputReadLock(str(child_script)),
            controller.InputReadLock(PYTHON_EXE),
        ]
        std_handles, std_streams = controller._open_stdio_handles(scenario_dir)
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        job_guard._api_process_identity = traced_identity_reader
        child = job_guard.launch_suspended_root(
            job,
            controller.CMD_EXE,
            argv,
            cwd=str(initial_cwd),
            std_handles=std_handles,
            environment=environment,
        )
        result["root_identity"] = child.identity
        result["launch_events"] = list(child.events)
        controller._close_stdio(std_handles, std_streams)
        std_handles, std_streams = None, ()
        previous_sample_start = None
        previous_accounting = None
        previous_pids = None
        previous_keys = set()
        deadline = time.monotonic() + 15.0
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
            sample_records.append(
                {
                    "sample_start_monotonic": sample["sample_start_monotonic"],
                    "sample_end_monotonic": sample["sample_end_monotonic"],
                    "uncertainty": sample["uncertainty"],
                    "job_pids_before": sample["job_pids_before"],
                    "job_pids_after": sample["job_pids_after"],
                    "accounting_before": sample["accounting_before"],
                    "accounting_after": sample["accounting_after"],
                    "member_measurements": sample["member_measurements"],
                    "tree_rss_bytes": sample["tree_rss_bytes"],
                }
            )
            root_wait = job_guard._api_wait(child.process_handle, 0)
            current_pids = job.pid_list()
            current_accounting = job.accounting()
            if (
                root_wait == job_guard.WAIT_OBJECT_0
                and not current_pids
                and current_accounting["active_processes"] == 0
            ):
                closure = child.wait_and_close(timeout_seconds=5.0)
                child = None
                break
            if root_wait not in (job_guard.WAIT_OBJECT_0, job_guard.WAIT_TIMEOUT):
                raise RuntimeError(f"未知root wait状态：{root_wait}")
            time.sleep(0.01)
        if closure is None:
            raise TimeoutError("cmd/bat/短命子代fixture未在限时内闭合")
        result["closure"] = closure
        result["child_receipt_exists"] = child_receipt.exists()
        if child_receipt.exists():
            result["child_receipt"] = json.loads(child_receipt.read_text(encoding="utf-8"))
        baseline = result["root_identity"]
        root_trace = [
            row["identity"] for row in identity_trace
            if row["identity"].get("pid") == baseline["pid"]
        ]
        field_values = {
            field: sorted(
                {json.dumps(identity.get(field), ensure_ascii=False, sort_keys=True) for identity in root_trace}
            )
            for field in IDENTITY_FIELDS
        }
        result["root_field_values"] = field_values
        result["root_field_change_counts_vs_create_suspended"] = {
            field: sum(identity.get(field) != baseline.get(field) for identity in root_trace)
            for field in IDENTITY_FIELDS
        }
        result["sample_count"] = len(sample_records)
        result["sample_uncertain_count"] = sum(bool(row["uncertainty"]) for row in sample_records)
        result["samples_after_expected_cwd_restore_clean"] = any(
            not row["uncertainty"]
            and any(member["pid"] == baseline["pid"] for member in row["member_measurements"])
            for row in sample_records
        )
        result["status"] = "PASS_FIXTURE_CLOSED" if closure["final"]["root_native_handle_exit_code"] == 37 else "FAIL_ROOT_EXIT"
        return result
    except BaseException as error:
        result["status"] = "FIXTURE_ERROR"
        result["error"] = repr(error)
        result["traceback"] = traceback.format_exc()
        if child is not None:
            try:
                result["cleanup"] = controller._kill_and_close(child, "FIXTURE_ERROR")
                child = None
            except BaseException as cleanup_error:
                result["cleanup_error"] = repr(cleanup_error)
        return result
    finally:
        job_guard._api_process_identity = original_api_reader
        if child is not None:
            try:
                controller._kill_and_close(child, "FIXTURE_FINAL_CLEANUP")
            except BaseException:
                pass
        elif not job.closed:
            try:
                job.close()
            except BaseException:
                pass
        if std_handles is not None:
            try:
                controller._close_stdio(std_handles, std_streams)
            except BaseException:
                pass
        for lock in reversed(locks):
            if not lock.closed:
                lock.close()


def main():
    results = [
        _scenario("initial_cwd_run_directory", "run_directory"),
        _scenario("initial_cwd_fixture_bin", "fixture_bin"),
    ]
    _write_json(EVIDENCE_DIR / "fixture_result.json", {"status": "FIXTURE_RESULTS", "scenarios": results})
    for result in results:
        print(
            json.dumps(
                {
                    "scenario": result["scenario"],
                    "status": result["status"],
                    "sample_uncertain_count": result.get("sample_uncertain_count"),
                    "root_field_change_counts_vs_create_suspended": result.get("root_field_change_counts_vs_create_suspended"),
                    "root_native_exit_code": result.get("closure", {}).get("final", {}).get("root_native_handle_exit_code"),
                },
                ensure_ascii=False,
            )
        )
    return 0 if all(row["status"] == "PASS_FIXTURE_CLOSED" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
