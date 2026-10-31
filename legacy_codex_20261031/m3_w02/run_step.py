"""在租约预算内执行单步XSDB，并在前后验证本轮Job监听所有权。"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "r03"))
import m3_pair
import owner_guard

STEP_LIMITS = {"setup": 90, "restore": 130, "event": 20, "close": 20}
STEP_RESERVES = {"setup": 30, "restore": 30, "event": 30, "close": 5}
MARKERS = {
    name: marker.encode("ascii")
    for name, marker in owner_guard.STEP_MARKERS.items()
}


def _real_owner_check(execution):
    """在客户端进程内查询命名Job及其当前监听PID。"""
    def job_pids(job_name):
        return owner_guard.query_named_job_pids(job_name)

    return owner_guard.verify_owner(
        execution,
        thread_alive=lambda: bool(job_pids(execution.job_name)),
        job_pids=job_pids,
        listener_pids=owner_guard.query_listener_pids,
        loopback_connected=owner_guard.loopback_connected,
    )


def _write_json_new(path, value):
    """以UTF-8独占创建单步结果，拒绝覆盖旧结果。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def execute_step(
    step,
    lease_file,
    *,
    root=None,
    runner=None,
    owner_check=None,
    xsdb_path=None,
    now=None,
):
    """执行已配置单步；runner和owner_check仅供隔离mock测试注入。"""
    if step not in STEP_LIMITS:
        raise owner_guard.GuardError("step无效")
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    runner = runner or m3_pair._run_xsdb
    owner_check = owner_check or _real_owner_check
    test_fixture_only = runner is not m3_pair._run_xsdb
    execution = owner_guard.load_execution(lease_file, root, now=now)
    owner_guard.assert_protocol_transition(
        execution, step, allow_test_fixtures=test_fixture_only
    )
    timeout = min(
        STEP_LIMITS[step],
        owner_guard.remaining_seconds(
            execution, reserve_seconds=STEP_RESERVES[step], now=now
        ),
    )
    step_dir = execution.lease.run_dir / step
    script = step_dir / f"{step}.tcl"
    if (
        step_dir.is_symlink()
        or not step_dir.is_dir()
        or script.is_symlink()
        or not script.is_file()
    ):
        raise owner_guard.GuardError(f"步骤Tcl不存在或不是普通文件：{script}")
    script = script.resolve(strict=True)
    if str(script.parent).casefold() != str(step_dir.resolve(strict=True)).casefold():
        raise owner_guard.GuardError("步骤Tcl路径经过重定向")
    target = script.parent / "step_result.json"
    launcher = script.parent / "launcher"
    if target.exists() or target.is_symlink() or launcher.exists() or launcher.is_symlink():
        raise owner_guard.GuardError("单步骤只允许运行一次；失败后不得覆盖RunId重试")

    proof_before = owner_check(execution)
    current_port, _, current_digest = owner_guard.parse_port_file(
        execution.lease.run_dir / "port.txt"
    )
    if current_port != execution.port or current_digest != execution.port_file_digest:
        raise owner_guard.GuardError("调用XSDB前端口或port.txt摘要发生变化")
    result = None
    error_text = None
    try:
        if xsdb_path is not None:
            selected_xsdb = Path(xsdb_path)
        elif runner is m3_pair._run_xsdb:
            selected_xsdb = m3_pair.OFFICIAL_XSDB.resolve(strict=True)
        else:
            selected_xsdb = m3_pair.OFFICIAL_XSDB
        result = runner(
            [
                str(selected_xsdb),
                "-no-ini",
                str(script),
            ],
            timeout,
        )
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"

    post_proof = None
    post_error = None
    try:
        post_execution = owner_guard.load_execution(lease_file, root, now=now)
        post_proof = owner_check(post_execution)
    except Exception as exc:
        post_error = f"{type(exc).__name__}: {exc}"

    stdout = result.stdout if result is not None else b""
    stderr = result.stderr if result is not None else b""
    text = (stdout + stderr).decode("utf-8", "replace")
    passed = (
        result is not None
        and result.returncode == 0
        and MARKERS[step] in stdout
        and not m3_pair.ERROR_RE.search(text)
        and error_text is None
        and post_error is None
    )
    at = (now or datetime.now(owner_guard.UTC8)).astimezone(owner_guard.UTC8)
    record = {
        "schema": owner_guard.STEP_RECEIPT_SCHEMA,
        "step": step,
        "at_utc8": at.isoformat(timespec="seconds"),
        "timeout_seconds": timeout,
        "run_dir": str(execution.lease.run_dir),
        "port": execution.port,
        "job_name": execution.job_name,
        "lease_id": execution.lease.lease_id,
        "lease_file_path": str(execution.lease.path),
        "lease_file_sha256": execution.lease.digest,
        "port_file_sha256": execution.port_file_digest,
        "owner_precheck": proof_before,
        "owner_postcheck": post_proof,
        "owner_postcheck_error": post_error,
        "runner_error": error_text,
        "process_exit_code": result.returncode if result is not None else None,
        "semantic_exit_code": 0 if passed else 2,
        "required_marker": MARKERS[step].decode("ascii"),
        "test_fixture_only": test_fixture_only,
        "status": "PASS" if passed else "FAIL",
        "meaning": "单步检查，不自动宣称M3成对保持通过",
    }
    if result is not None:
        record["launcher_record"] = getattr(result, "launcher_record", None)
    _write_json_new(target, record)
    if result is not None:
        sys.stdout.write(text)
    print(json.dumps(record, ensure_ascii=False))
    return record["semantic_exit_code"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", choices=tuple(STEP_LIMITS), required=True)
    parser.add_argument("--lease-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        return execute_step(args.step, args.lease_file)
    except (owner_guard.GuardError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
