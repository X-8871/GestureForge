"""在M3原捕获前后验证本轮Job所有权并按租期截断超时。"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1] / "r03"))
import m3_pair
import owner_guard


def _real_owner_check(execution):
    """客户端通过只查询权限读取命名Job的活动进程。"""
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
    """以UTF-8独占创建捕获阶段门禁记录。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run_capture_phase(
    lease_file,
    phase,
    *,
    root=None,
    capture_fn=None,
    owner_check=None,
    now=None,
):
    """调用只读核心capture；依赖注入仅供无硬件mock测试使用。"""
    if phase not in {"before", "after"}:
        raise owner_guard.GuardError("phase只能是before或after")
    root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    capture_fn = capture_fn or m3_pair.capture
    owner_check = owner_check or _real_owner_check
    test_fixture_only = capture_fn is not m3_pair.capture
    execution = owner_guard.load_execution(lease_file, root, now=now)
    owner_guard.assert_protocol_transition(
        execution, phase, allow_test_fixtures=test_fixture_only
    )
    timeout = min(
        120,
        owner_guard.remaining_seconds(execution, reserve_seconds=30, now=now),
    )
    output_dir = execution.lease.run_dir / f"capture_{phase}"
    guard_path = execution.lease.run_dir / f"capture_{phase}_guard.json"
    if output_dir.exists() or output_dir.is_symlink() or guard_path.exists() or guard_path.is_symlink():
        raise owner_guard.GuardError("捕获阶段只允许执行一次；拒绝覆盖已有输出")

    proof_before = owner_check(execution)
    current_port, _, current_digest = owner_guard.parse_port_file(
        execution.lease.run_dir / "port.txt"
    )
    if current_port != execution.port or current_digest != execution.port_file_digest:
        raise owner_guard.GuardError("调用capture前端口或port.txt摘要发生变化")

    capture_result = None
    capture_error = None
    try:
        capture_result = capture_fn(
            out_text=str(output_dir),
            xsdb_text=str(m3_pair.OFFICIAL_XSDB),
            port=execution.port,
            window_id=execution.lease.window_id,
            phase=phase,
            event_id=execution.lease.event_id,
            authorization_file_text=str(execution.lease.authorization_file),
            context_file_text=str(execution.lease.context_file),
            timeout_seconds=timeout,
        )
    except Exception as exc:
        capture_error = f"{type(exc).__name__}: {exc}"

    proof_after = None
    post_error = None
    try:
        post_execution = owner_guard.load_execution(lease_file, root, now=now)
        proof_after = owner_check(post_execution)
    except Exception as exc:
        post_error = f"{type(exc).__name__}: {exc}"

    passed = (
        capture_result is not None
        and capture_result.get("status") == "CAPTURED"
        and capture_error is None
        and post_error is None
    )
    record = {
        "schema": owner_guard.CAPTURE_GUARD_SCHEMA,
        "phase": phase,
        "at_utc8": (now or datetime.now(owner_guard.UTC8)).astimezone(
            owner_guard.UTC8
        ).isoformat(timespec="seconds"),
        "lease_id": execution.lease.lease_id,
        "lease_file_path": str(execution.lease.path),
        "lease_file_sha256": execution.lease.digest,
        "run_dir": str(execution.lease.run_dir),
        "port": execution.port,
        "port_file_sha256": execution.port_file_digest,
        "job_name": execution.job_name,
        "timeout_seconds": timeout,
        "capture": capture_result,
        "test_fixture_only": test_fixture_only,
        "capture_error": capture_error,
        "owner_precheck": proof_before,
        "owner_postcheck": proof_after,
        "owner_postcheck_error": post_error,
        "status": "PASS_CAPTURE_WRAPPER" if passed else "FAIL_CAPTURE_WRAPPER",
        "meaning": "仅表示capture调用及前后所有权门禁结果，不单独证明M3保持或外部授权",
    }
    _write_json_new(guard_path, record)
    print(json.dumps(record, ensure_ascii=False))
    return 0 if passed else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lease-file", type=Path, required=True)
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    args = parser.parse_args(argv)
    try:
        return run_capture_phase(args.lease_file, args.phase)
    except (owner_guard.GuardError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
