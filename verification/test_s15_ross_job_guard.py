"""离线回归ROSS canonical适配、固定命令许可和Windows Job监护。"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import secrets
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import psutil
import s15_job_guard as job_guard
import s15_ross_job_guard as ross_guard


EVIDENCE_ROOT = Path(__file__).resolve().parents[1] / Path(ross_guard.EXPECTED_EVIDENCE_RELATIVE)
SESSION_ID = "ross-offline-fixture-session-r01"
WORKER_SOURCE = (
    "import pathlib,subprocess,sys,time\n"
    "ready=pathlib.Path(sys.argv[1])\n"
    "child_request=pathlib.Path(sys.argv[2])\n"
    "child_done=pathlib.Path(sys.argv[3])\n"
    "child_pid=pathlib.Path(sys.argv[4])\n"
    "exit_request=pathlib.Path(sys.argv[5])\n"
    "ready.write_text('ready',encoding='utf-8')\n"
    "while not exit_request.exists():\n"
    " if child_request.exists() and not child_done.exists():\n"
    "  child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(3600)'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))\n"
    "  child_pid.write_text(str(child.pid),encoding='ascii')\n"
    "  child_done.write_text('done',encoding='ascii')\n"
    " time.sleep(0.02)\n"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _write_json(path: Path, value: object) -> None:
    with path.open("xb") as stream:
        stream.write((json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())


def _make_run_dir(run_id: str) -> Path:
    if not run_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for ch in run_id):
        raise ValueError("RunId只能包含ASCII字母、数字、下划线和连字符")
    target = EVIDENCE_ROOT / run_id
    target.mkdir(parents=False, exist_ok=False)
    return target


class FixtureSession:
    """启动真实Windows进程树，供同一生产Job guard代码接管。"""

    def __init__(self, artifact_root: Path, session_id: str = SESSION_ID):
        self.control_dir = Path(artifact_root) / f"fixture_{secrets.token_hex(5)}"
        self.control_dir.mkdir(parents=False, exist_ok=False)
        self.ready_path = self.control_dir / "ready.txt"
        self.child_request_path = self.control_dir / "child.request"
        self.child_done_path = self.control_dir / "child.done"
        self.child_pid_path = self.control_dir / "child.pid"
        self.exit_request_path = self.control_dir / "exit.request"
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        if not pythonw.is_file():
            raise RuntimeError(f"隔离fixture缺少同目录pythonw.exe：{pythonw}")
        self.process = subprocess.Popen(
            [str(pythonw), "-c", WORKER_SOURCE, str(self.ready_path), str(self.child_request_path), str(self.child_done_path), str(self.child_pid_path), str(self.exit_request_path)],
            cwd=str(Path(__file__).resolve().parents[1]),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        ready_deadline = time.monotonic() + 5.0
        while not self.ready_path.exists() and self.process.poll() is None and time.monotonic() < ready_deadline:
            time.sleep(0.02)
        if not self.ready_path.is_file() or self.process.poll() is not None:
            self.process.kill()
            self.process.wait(timeout=5)
            raise RuntimeError("pythonw fixture没有在5秒内写入READY文件")
        self.job = job_guard.JobObject(kill_on_close=True)
        self.controller = ross_guard.RossJobGuardController(
            self.job,
            expected_session_id=session_id,
            evidence_root=artifact_root,
        )
        self.session_id = session_id
        self.child_pid = None
        self.dispatch_events = []

    def identity(self) -> dict:
        return job_guard.process_identity(self.process.pid)

    def initial_record(self, **overrides) -> dict:
        now = time.monotonic()
        value = {
            "schema": ross_guard.SCHEMA,
            "session_id": self.session_id,
            "deployment_type": "local",
            "clock_domain": "host_monotonic",
            "event": "HEARTBEAT",
            "session_state": "idle",
            "active_command_sha256": None,
            "completed_command_sha256": None,
            "completed_exit_code": None,
            "root_identity": self.identity(),
            "heartbeat_sequence": 0,
            "observed_monotonic": now,
            "published_monotonic": now,
            "progress_counter": 0,
            "progress_monotonic": now,
        }
        value.update(overrides)
        return value

    def start(self, **overrides) -> dict:
        return self.controller.start(self.initial_record(**overrides))

    def publish(
        self,
        *,
        event: str = "HEARTBEAT",
        state: str = "idle",
        active_sha: str | None = None,
        completed_sha: str | None = None,
        exit_code: int | None = None,
        advance_progress: bool = True,
        progress_monotonic: float | None = None,
        identity: dict | None = None,
        session_id: str | None = None,
        observed_monotonic: float | None = None,
        published_monotonic: float | None = None,
    ) -> int:
        now = time.monotonic()
        if progress_monotonic is None:
            if advance_progress or self.controller.progress_monotonic is None:
                progress_monotonic = now
            else:
                progress_monotonic = self.controller.progress_monotonic
        if observed_monotonic is None:
            observed_monotonic = now
        if published_monotonic is None:
            published_monotonic = max(now, observed_monotonic)
        progress_counter = 0 if self.controller.progress_counter is None else self.controller.progress_counter
        if advance_progress and self.controller.progress_counter is not None:
            progress_counter += 1
        record = {
            "schema": ross_guard.SCHEMA,
            "session_id": self.session_id if session_id is None else session_id,
            "deployment_type": "local",
            "clock_domain": "host_monotonic",
            "event": event,
            "session_state": state,
            "active_command_sha256": active_sha,
            "completed_command_sha256": completed_sha,
            "completed_exit_code": exit_code,
            "root_identity": self.identity() if identity is None else identity,
            "heartbeat_sequence": self.controller.sequence + 1,
            "observed_monotonic": observed_monotonic,
            "published_monotonic": published_monotonic,
            "progress_counter": progress_counter,
            "progress_monotonic": progress_monotonic,
        }
        self.controller.publish_fixture_or_bridge_heartbeat(record)
        return self.controller.sequence

    def dispatch_two_commands(self, stop: bool = True) -> list[dict]:
        receipts = []
        for command_index in range(2):
            permit = self.controller.issue_dispatch_permit()
            ready_receipt = self.controller.ready_receipt if command_index == 0 else None
            receipt = self.controller.claim_dispatch(permit, self._dispatch_callback, ready_receipt=ready_receipt)
            receipts.append(receipt)
            self.publish(
                state="active",
                active_sha=receipt["command_sha256"],
                completed_sha=self.controller.last_completed_sha256,
                exit_code=0 if self.controller.last_completed_sha256 is not None else None,
            )
            self.publish(
                state="idle",
                completed_sha=receipt["command_sha256"],
                exit_code=0,
            )
        if stop:
            self.publish(
                event="STOP",
                state="closed",
                completed_sha=self.controller.last_completed_sha256,
                exit_code=0,
            )
        return receipts

    def _dispatch_callback(self, receipt: dict):
        if not self.controller._dispatch_lease_active:
            raise AssertionError("dispatch callback没有处于controller状态锁与跨进程租约窗口")
        hook = getattr(self, "before_ack_hook", None)
        if hook is not None:
            hook(receipt)
        self.dispatch_events.append(
            {
                "sequence": receipt["sequence"],
                "controller_state": self.controller.state,
                "nonce_consumed": self.controller._expected_permit_nonce is None,
            }
        )
        response = {
            "kind": "fixture_mcp_acceptance",
            "session_id": receipt["session_id"],
            "sequence": receipt["sequence"],
            "command_sha256": receipt["command_sha256"],
        }
        response_sha = hashlib.sha256(
            json.dumps(response, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return ross_guard.DispatchAck(
            owner=self.controller,
            controller_id=receipt["controller_id"],
            permit_nonce=receipt["permit_nonce"],
            session_id=receipt["session_id"],
            sequence=receipt["sequence"],
            command=receipt["command"],
            command_sha256=receipt["command_sha256"],
            output_path=receipt["output_path"],
            dcp_sha256=receipt["dcp_sha256"],
            outcome="ACCEPTED",
            response_sha256=response_sha,
            acknowledged_monotonic=time.monotonic(),
        )

    def spawn_child(self) -> int:
        self.child_request_path.touch(exist_ok=False)
        deadline = time.monotonic() + 5.0
        while not self.child_pid_path.is_file() and self.process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        if not self.child_pid_path.is_file():
            raise RuntimeError("fixture root没有按请求创建child")
        self.child_pid = int(self.child_pid_path.read_text(encoding="ascii"))
        return self.child_pid

    def ask_root_exit(self) -> None:
        if self.process.poll() is None:
            self.exit_request_path.touch(exist_ok=True)

    def cleanup(self) -> None:
        self.ask_root_exit()
        if not self.job.closed:
            self.job.close()
        for anchor_name in ("_output_anchor", "_evidence_anchor"):
            anchor = getattr(self.controller, anchor_name, None)
            if anchor is not None:
                anchor.close()
                setattr(self.controller, anchor_name, None)
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def _expect_rejection(name: str, callback, checks: list[str]) -> None:
    try:
        callback()
    except (ross_guard.RossGuardError, job_guard.JobGuardError, OSError, ValueError):
        checks.append(name)
        return
    raise AssertionError(f"负例未fail closed：{name}")


def _test_handle_pid_reuse(run_root: Path, checks: list[str]) -> None:
    for case in ("handle-pid-mismatch", "handle-birth-time-mismatch"):
        fixture = FixtureSession(run_root)
        expected = fixture.identity()
        fake_handle = 0x5A5A
        original = {
            name: getattr(job_guard, name)
            for name in ("_api_open_process", "_api_process_id", "_api_creation_ticks", "_api_process_identity", "_api_assign_process", "_api_close_handle")
        }
        identity_calls = 0
        assignments = []
        closed_fake_handles = []

        def fake_identity(pid):
            nonlocal identity_calls
            identity_calls += 1
            value = dict(expected)
            if case == "handle-birth-time-mismatch" and identity_calls >= 2:
                value["create_time"] += 1.0
            return value

        def fake_creation_ticks(handle):
            seconds = expected["create_time"]
            return int(seconds * 10000000.0 + 116444736000000000)

        def fake_close(handle):
            if handle == fake_handle:
                closed_fake_handles.append(handle)
                return True
            return bool(original["_api_close_handle"](handle))

        job_guard._api_open_process = lambda pid, access: fake_handle
        job_guard._api_process_id = lambda handle: expected["pid"] + (1 if case == "handle-pid-mismatch" else 0)
        job_guard._api_creation_ticks = fake_creation_ticks
        job_guard._api_process_identity = fake_identity
        job_guard._api_assign_process = lambda job_handle, process_handle: assignments.append((job_handle, process_handle)) or True
        job_guard._api_close_handle = fake_close
        try:
            _expect_rejection(
                case,
                lambda: fixture.job.attach_idle_root(ross_guard._mcp_record_for_frozen_guard(SESSION_ID, expected)),
                checks,
            )
            if assignments:
                raise AssertionError(f"{case}错误地执行了AssignProcessToJobObject")
            if not closed_fake_handles:
                raise AssertionError(f"{case}未关闭未绑定的fake HANDLE")
            if fixture.process.poll() is not None or not psutil.pid_exists(fixture.process.pid):
                raise AssertionError(f"{case}错误终止了原始fixture PID")
        finally:
            for name, value in original.items():
                setattr(job_guard, name, value)
            fixture.cleanup()
        checks.append(f"{case}-no-assign-no-wrong-process-termination")


def _test_process_snapshot_close_failure(checks: list[str]) -> None:
    fake_snapshot = 0x5A5A
    original = {
        name: getattr(job_guard, name)
        for name in (
            "_api_process_snapshot",
            "_api_process32_first",
            "_api_process32_next",
            "_api_close_handle",
        )
    }
    close_calls = []

    def fake_first(snapshot, entry):
        if snapshot != fake_snapshot:
            raise AssertionError("process_table没有使用被注入的Toolhelp快照")
        ctypes.set_last_error(87)
        return False

    def fake_close(handle):
        close_calls.append(handle)
        ctypes.set_last_error(5)
        return False

    job_guard._api_process_snapshot = lambda: fake_snapshot
    job_guard._api_process32_first = fake_first
    job_guard._api_process32_next = lambda snapshot, entry: False
    job_guard._api_close_handle = fake_close
    try:
        try:
            job_guard.process_table()
        except job_guard.GateBlocked as error:
            message = str(error)
            required = (
                "Process32FirstW",
                "WinError 87",
                "CloseHandle(Toolhelp process snapshot)",
                "WinError 5",
            )
            if not all(token in message for token in required):
                raise AssertionError(f"快照主错误或CloseHandle错误未完整保留：{message}")
        else:
            raise AssertionError("快照句柄关闭失败没有令process_table失败")
        if close_calls != [fake_snapshot]:
            raise AssertionError(f"失败快照句柄被盲目重复关闭：{close_calls!r}")
        checks.append("toolhelp-snapshot-close-failure-winerror-primary-preserved-single-attempt")
    finally:
        for name, value in original.items():
            setattr(job_guard, name, value)


def _test_unseen_status_invalidates_permit(run_root: Path, checks: list[str]) -> None:
    for state_name in ("active", "stop"):
        fixture = FixtureSession(run_root)
        try:
            fixture.start()
            permit = fixture.controller.issue_dispatch_permit()
            now = time.monotonic()
            if state_name == "active":
                record = {
                    "schema": ross_guard.SCHEMA,
                    "session_id": SESSION_ID,
                    "deployment_type": "local",
                    "clock_domain": "host_monotonic",
                    "event": "HEARTBEAT",
                    "session_state": "active",
                    "active_command_sha256": permit.command_sha256,
                    "completed_command_sha256": None,
                    "completed_exit_code": None,
                    "root_identity": fixture.identity(),
                    "heartbeat_sequence": fixture.controller.sequence + 1,
                    "observed_monotonic": now,
                    "published_monotonic": now,
                    "progress_counter": fixture.controller.progress_counter,
                    "progress_monotonic": now,
                }
            else:
                record = {
                    "schema": ross_guard.SCHEMA,
                    "session_id": SESSION_ID,
                    "deployment_type": "local",
                    "clock_domain": "host_monotonic",
                    "event": "STOP",
                    "session_state": "closed",
                    "active_command_sha256": None,
                    "completed_command_sha256": None,
                    "completed_exit_code": None,
                    "root_identity": fixture.identity(),
                    "heartbeat_sequence": fixture.controller.sequence + 1,
                    "observed_monotonic": now,
                    "published_monotonic": now,
                    "progress_counter": fixture.controller.progress_counter,
                    "progress_monotonic": now,
                }
            fixture.controller.channel.publish(record)
            callbacks = []
            _expect_rejection(
                f"stale-permit-after-unseen-{state_name}",
                lambda: fixture.controller.claim_dispatch(
                    permit,
                    lambda receipt: callbacks.append(receipt),
                    ready_receipt=fixture.controller.ready_receipt,
                ),
                checks,
            )
            if callbacks or fixture.controller.state != "FAILED" or fixture.controller._ready_consumed:
                raise AssertionError(f"未采样的{state_name}状态没有令旧许可失效并保持READY不可用")
        finally:
            fixture.cleanup()


def _test_permit_and_ready_receipts(run_root: Path, checks: list[str]) -> None:
    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        altered = replace(permit, nonce=b"\x00" * len(permit.nonce))
        called = []
        _expect_rejection(
            "dispatch-nonce-tamper",
            lambda: fixture.controller.claim_dispatch(altered, lambda receipt: called.append(receipt), fixture.controller.ready_receipt),
            checks,
        )
        if called or fixture.controller._ready_consumed:
            raise AssertionError("篡改permit nonce后callback或READY token仍可用")
    finally:
        fixture.cleanup()

    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        forged_ready = replace(fixture.controller.ready_receipt, nonce=b"\xFF" * len(fixture.controller.ready_receipt.nonce))
        called = []
        _expect_rejection(
            "ready-nonce-forgery",
            lambda: fixture.controller.claim_dispatch(permit, lambda receipt: called.append(receipt), forged_ready),
            checks,
        )
        if called or fixture.controller._ready_consumed:
            raise AssertionError("伪造READY token后callback或READY token仍可用")
    finally:
        fixture.cleanup()

    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        fixture.controller._clock = lambda: permit.issued_monotonic + ross_guard.HEARTBEAT_FRESHNESS_SECONDS + 1.0
        called = []
        _expect_rejection(
            "dispatch-permit-expired",
            lambda: fixture.controller.claim_dispatch(permit, lambda receipt: called.append(receipt), fixture.controller.ready_receipt),
            checks,
        )
        if called or fixture.controller._ready_consumed:
            raise AssertionError("过期permit触发callback或消费READY token")
    finally:
        fixture.cleanup()

    first = FixtureSession(run_root)
    second = FixtureSession(run_root)
    try:
        first.start()
        second.start()
        permit = first.controller.issue_dispatch_permit()
        called = []
        _expect_rejection(
            "dispatch-permit-cross-controller",
            lambda: second.controller.claim_dispatch(permit, lambda receipt: called.append(receipt), second.controller.ready_receipt),
            checks,
        )
        if called or second.controller._ready_consumed:
            raise AssertionError("跨controller permit被派发或消费READY")
    finally:
        first.cleanup()
        second.cleanup()

    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        receipt = fixture.controller.claim_dispatch(permit, fixture._dispatch_callback, fixture.controller.ready_receipt)
        if not fixture.controller._ready_consumed or fixture.dispatch_events != [{"sequence": 0, "controller_state": "WAIT_COMMAND", "nonce_consumed": True}]:
            raise AssertionError("READY token未在锁内派发路径一次性消费")
        _expect_rejection(
            "dispatch-permit-replay",
            lambda: fixture.controller.claim_dispatch(permit, fixture._dispatch_callback, fixture.controller.ready_receipt),
            checks,
        )
        if len(fixture.dispatch_events) != 1 or receipt["sequence"] != 0:
            raise AssertionError("许可重放再次触发了外层callback")
    finally:
        fixture.cleanup()


def _test_output_directory_anchor(run_root: Path, checks: list[str]) -> None:
    fixture = FixtureSession(run_root)
    moved_path = None
    output_path = None
    try:
        fixture.start()
        first = fixture.controller.issue_dispatch_permit()
        fixture.controller.claim_dispatch(first, fixture._dispatch_callback, fixture.controller.ready_receipt)
        fixture.publish(state="active", active_sha=first.command_sha256)
        fixture.publish(state="idle", completed_sha=first.command_sha256, exit_code=0)
        permit = fixture.controller.issue_dispatch_permit()
        output_dir = fixture.controller._output_directory
        output_path = fixture.controller._output_path
        moved_path = output_dir.with_name(output_dir.name + "_replacement_probe")
        callbacks = []
        try:
            os.rename(output_dir, moved_path)
        except OSError as error:
            if getattr(error, "winerror", None) not in (5, 32):
                raise
            if moved_path.exists() or not output_dir.is_dir():
                raise AssertionError("目录替换拒绝后路径状态意外变化") from error
            checks.append("output-parent-rename-blocked-by-held-no-delete-share")
        else:
            output_dir.mkdir()
            _expect_rejection(
                "output-parent-identity-replacement",
                lambda: fixture.controller.claim_dispatch(permit, lambda receipt: callbacks.append(receipt)),
                checks,
            )
            output_dir.rmdir()
            os.rename(moved_path, output_dir)
        if output_path.exists() or output_path.is_symlink() or callbacks:
            raise AssertionError("父目录替换探测写出了bitstream或触发dispatch")
        checks.append("output-parent-replacement-no-escaped-output")
    finally:
        if moved_path is not None and moved_path.exists() and not fixture.controller.state == "FAILED":
            if fixture.controller._output_anchor is not None:
                fixture.controller._output_anchor.close()
                fixture.controller._output_anchor = None
            if fixture.controller._evidence_anchor is not None:
                fixture.controller._evidence_anchor.close()
                fixture.controller._evidence_anchor = None
            if fixture.controller._output_directory is not None and fixture.controller._output_directory.exists():
                fixture.controller._output_directory.rmdir()
            os.rename(moved_path, fixture.controller._output_directory)
        fixture.cleanup()


def _test_directory_anchor_chain(run_root: Path, checks: list[str]) -> None:
    """逐级验证租约期间祖先不可改名/删除，租约外恢复可操作。"""
    component_names = ("Users", "profile", "repo")
    for index, component in enumerate(component_names):
        base = run_root / f"anchor_rename_{component}"
        paths = []
        cursor = base
        for name in component_names:
            cursor = cursor / name
            cursor.mkdir(parents=True, exist_ok=True)
            paths.append(cursor)
        anchor = ross_guard.DirectoryAnchor(paths[-1])
        moved = paths[index].with_name(paths[index].name + "_moved")
        try:
            output = paths[-1] / "output.fixture"
            output.write_bytes(b"directory-lease-output")
            if output.read_bytes() != b"directory-lease-output":
                raise AssertionError("路径租约持有期间子文件写入/读回失败")
            try:
                os.rename(paths[index], moved)
            except OSError as error:
                if getattr(error, "winerror", None) != 32:
                    raise AssertionError(f"{component}改名未以WinError32被拒绝：{error!r}") from error
            else:
                raise AssertionError(f"{component}祖先在链租约持有期间仍可改名")
            if moved.exists() or not paths[index].is_dir():
                raise AssertionError(f"{component}改名失败后路径状态改变")
            checks.append(f"directory-anchor-rename-blocked-{component}")
        finally:
            anchor.close()
        os.rename(paths[index], moved)
        os.rename(moved, paths[index])
        checks.append(f"directory-anchor-rename-restored-{component}")

    for index, component in enumerate(component_names):
        base = run_root / f"anchor_delete_{component}"
        paths = []
        cursor = base
        for name in component_names[: index + 1]:
            cursor = cursor / name
            cursor.mkdir(parents=True, exist_ok=True)
            paths.append(cursor)
        target = paths[-1]
        anchor = ross_guard.DirectoryAnchor(target)
        try:
            try:
                os.rmdir(target)
            except OSError as error:
                if getattr(error, "winerror", None) != 32:
                    raise AssertionError(f"{component}删除未以WinError32被拒绝：{error!r}") from error
            else:
                raise AssertionError(f"{component}目录在链租约持有期间仍可删除")
            if not target.is_dir():
                raise AssertionError(f"{component}删除失败后目标已消失")
            checks.append(f"directory-anchor-delete-blocked-{component}")
        finally:
            anchor.close()
        os.rmdir(target)
        checks.append(f"directory-anchor-delete-restored-{component}")

    alias_target = run_root / "anchor_alias" / "Users" / "profile" / "repo"
    alias_target.mkdir(parents=True, exist_ok=False)
    aliases = (
        str(alias_target.parent) + r"\.\repo",
        str(alias_target.parent) + r"\..\repo",
        r"\\server\share\repo",
    )
    for alias in aliases:
        _expect_rejection(
            f"directory-anchor-reject-alias-{hashlib.sha256(alias.encode('utf-8')).hexdigest()[:8]}",
            lambda value=alias: ross_guard._directory_chain(value),
            checks,
        )

    real_identity = ross_guard._api_directory_identity
    reparse_target = alias_target.parent

    def injected_reparse_identity(handle):
        value = real_identity(handle)
        if ross_guard._api_directory_final_path(handle) == str(reparse_target):
            value["attributes"] |= ross_guard._FILE_ATTRIBUTE_REPARSE_POINT
        return value

    ross_guard._api_directory_identity = injected_reparse_identity
    try:
        _expect_rejection(
            "directory-anchor-reparse-component",
            lambda: ross_guard.DirectoryAnchor(alias_target),
            checks,
        )
    finally:
        ross_guard._api_directory_identity = real_identity

    anchor = ross_guard.DirectoryAnchor(alias_target)
    chosen_handle = anchor.entries[-1]["handle"]
    original_close = job_guard._api_close_handle
    failed = set()

    def injected_close(handle):
        if handle == chosen_handle and handle not in failed:
            failed.add(handle)
            ctypes.set_last_error(5)
            return False
        return bool(original_close(handle))

    job_guard._api_close_handle = injected_close
    try:
        _expect_rejection("directory-anchor-closehandle-failure", anchor.close, checks)
        if anchor.closed or not anchor.entries:
            raise AssertionError("目录句柄关闭失败后锚点被误报为closed")
    finally:
        job_guard._api_close_handle = original_close
        anchor.close()


def _test_dispatch_ack_fail_closed(run_root: Path, checks: list[str]) -> None:
    for case in ("unknown-response", "callback-break", "ack-command-tamper", "ack-future"):
        fixture = FixtureSession(run_root)
        try:
            fixture.start()
            permit = fixture.controller.issue_dispatch_permit()
            called = []

            def callback(receipt):
                called.append(receipt)
                if case == "unknown-response":
                    return {"content": [{"type": "text", "text": "unmapped tool response"}]}
                if case == "callback-break":
                    raise OSError("fixture MCP response pipe broke")
                valid = fixture._dispatch_callback(receipt)
                if case == "ack-command-tamper":
                    return replace(valid, command_sha256="0" * 64)
                return replace(valid, acknowledged_monotonic=time.monotonic() + 1.0)

            _expect_rejection(
                f"dispatch-lease-{case}",
                lambda: fixture.controller.claim_dispatch(
                    permit, callback, ready_receipt=fixture.controller.ready_receipt
                ),
                checks,
            )
            if not called or fixture.controller.state != "FAILED":
                raise AssertionError(f"{case}没有在未知响应/中断后fail closed")
            if case == "unknown-response":
                if fixture.controller._last_ack_binding is not None or fixture.controller.pending_permit is not None:
                    raise AssertionError("未知MCP响应被误记为已ACK或保留了可消费许可")
                _expect_rejection(
                    "dispatch-unknown-response-terminal-state",
                    fixture.controller.issue_dispatch_permit,
                    checks,
                )
        finally:
            fixture.cleanup()


def _test_dispatch_timeout_and_late_ack(run_root: Path, checks: list[str]) -> None:
    fixture = FixtureSession(run_root)
    original_timeout = ross_guard.DISPATCH_CALLBACK_TIMEOUT_SECONDS
    callback_entered = threading.Event()
    release_callback = threading.Event()
    late_acks = []
    publisher = None
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        now = time.monotonic()
        active_record = fixture.initial_record(
            session_state="active",
            active_command_sha256=permit.command_sha256,
            completed_command_sha256=None,
            completed_exit_code=None,
            heartbeat_sequence=fixture.controller.sequence + 1,
            observed_monotonic=now,
            published_monotonic=now,
            progress_monotonic=fixture.controller.progress_monotonic,
        )
        marker = run_root / f"timeout_publisher_{secrets.token_hex(4)}.done"
        publisher_source = (
            "import base64,msvcrt,os,pathlib,sys\n"
            "path=pathlib.Path(sys.argv[1]); marker=pathlib.Path(sys.argv[2])\n"
            "raw=base64.b64decode(sys.argv[3])\n"
            "with path.open('r+b',buffering=0) as stream:\n"
            " stream.seek(0); msvcrt.locking(stream.fileno(),msvcrt.LK_LOCK,1)\n"
            " try:\n"
            "  stream.seek(0,os.SEEK_END); stream.write(raw+b'\\n'); os.fsync(stream.fileno())\n"
            " finally:\n"
            "  stream.seek(0); msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)\n"
            "marker.write_text('released',encoding='ascii')\n"
        )
        encoded_record = __import__("base64").b64encode(
            json.dumps(active_record, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).decode("ascii")

        def blocked_callback(receipt):
            if not fixture.controller._dispatch_lease_active:
                raise AssertionError("超时callback启动时没有持有dispatch租约")
            callback_entered.set()
            if not release_callback.wait(4.0):
                raise TimeoutError("fixture没有释放阻塞callback")
            late = ross_guard.DispatchAck(
                owner=fixture.controller,
                controller_id=receipt["controller_id"],
                permit_nonce=receipt["permit_nonce"],
                session_id=receipt["session_id"],
                sequence=receipt["sequence"],
                command=receipt["command"],
                command_sha256=receipt["command_sha256"],
                output_path=receipt["output_path"],
                dcp_sha256=receipt["dcp_sha256"],
                outcome="ACCEPTED",
                response_sha256=hashlib.sha256(b"late fixture ack").hexdigest(),
                acknowledged_monotonic=time.monotonic(),
            )
            late_acks.append(late)
            return late

        ross_guard.DISPATCH_CALLBACK_TIMEOUT_SECONDS = 0.25
        call_started = time.monotonic()
        _expect_rejection(
            "dispatch-callback-timeout-result-uncertain",
            lambda: fixture.controller.claim_dispatch(
                permit, blocked_callback, ready_receipt=fixture.controller.ready_receipt
            ),
            checks,
        )
        elapsed = time.monotonic() - call_started
        if elapsed > 2.0 or not callback_entered.is_set():
            raise AssertionError(f"callback timeout没有在有界窗口内触发：elapsed={elapsed:.6f}s")
        controller = fixture.controller
        if controller.state != "FAILED" or not fixture.job.closed:
            raise AssertionError("callback timeout未立即关闭本Job并进入FAILED")
        if (
            controller.uncertain_dispatch is None
            or controller.uncertain_dispatch["result"] != "UNCERTAIN"
            or controller.pending_command is None
            or controller.pending_command.get("dispatch_outcome") != "UNCERTAIN"
            or controller.pending_permit is not None
            or controller._expected_permit_nonce is not None
            or controller._pending_permit_binding is not None
            or controller._pending_ack_nonce is not None
        ):
            raise AssertionError("超时未记录不确定结果或未撤销本地许可/ACK nonce")
        if "结果不确定" not in (controller.failure or "") or "不保证取消" not in (controller.failure or ""):
            raise AssertionError("超时错误没有明确记录远端结果不确定及无取消保证")

        publisher = subprocess.Popen(
            [sys.executable, "-c", publisher_source, str(controller.channel.path), str(marker), encoded_record],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        stdout, stderr = publisher.communicate(timeout=3.0)
        if publisher.returncode != 0 or not marker.is_file():
            raise AssertionError(f"超时后append lease没有释放：exit={publisher.returncode}, stdout={stdout!r}, stderr={stderr!r}")
        lines = controller.channel.path.read_bytes().splitlines()
        if len(lines) != 2 or json.loads(lines[-1].decode("utf-8"))["heartbeat_sequence"] != 1:
            raise AssertionError("超时后外部publisher记录未完整追加到状态通道")

        worker = controller._dispatch_worker
        release_callback.set()
        if worker is None:
            raise AssertionError("超时后没有保留用于观测迟到ACK的callback线程句柄")
        worker.join(timeout=3.0)
        if worker.is_alive() or len(late_acks) != 1:
            raise AssertionError("fixture迟到ACK线程未在释放后退出")
        if controller.state != "FAILED" or controller._last_ack_binding is not None:
            raise AssertionError("迟到ACK恢复/污染了FAILED状态或被消费为成功")
        if controller._pending_ack_nonce is not None or controller.uncertain_dispatch["late_ack_policy"] != "DISCARD":
            raise AssertionError("迟到ACK没有被撤销并标记为丢弃")
        checks.append("dispatch-timeout-bounded-job-closed-lease-released-late-ack-discarded")
    finally:
        release_callback.set()
        if publisher is not None and publisher.poll() is None:
            publisher.kill()
            publisher.wait(timeout=3.0)
        worker = fixture.controller._dispatch_worker
        if worker is not None:
            worker.join(timeout=3.0)
        ross_guard.DISPATCH_CALLBACK_TIMEOUT_SECONDS = original_timeout
        fixture.cleanup()


def _test_dispatch_publisher_linearization(run_root: Path, checks: list[str]) -> None:
    """用独立进程证明状态publisher无法插入claim到ACK租约窗口。"""
    fixture = FixtureSession(run_root)
    worker = None
    try:
        fixture.start()
        permit = fixture.controller.issue_dispatch_permit()
        now = time.monotonic()
        active_record = fixture.initial_record(
            session_state="active",
            active_command_sha256=permit.command_sha256,
            completed_command_sha256=None,
            completed_exit_code=None,
            heartbeat_sequence=fixture.controller.sequence + 1,
            observed_monotonic=now,
            published_monotonic=now,
            progress_monotonic=fixture.controller.progress_monotonic,
        )
        marker = run_root / f"external_publisher_{secrets.token_hex(4)}.done"
        worker_source = (
            "import base64,json,msvcrt,os,pathlib,sys\n"
            "path=pathlib.Path(sys.argv[1]); marker=pathlib.Path(sys.argv[2])\n"
            "raw=base64.b64decode(sys.argv[3])\n"
            "with path.open('r+b',buffering=0) as stream:\n"
            " stream.seek(0); msvcrt.locking(stream.fileno(),msvcrt.LK_LOCK,1)\n"
            " try:\n"
            "  stream.seek(0,os.SEEK_END); stream.write(raw+b'\\n'); os.fsync(stream.fileno())\n"
            " finally:\n"
            "  stream.seek(0); msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)\n"
            "marker.write_text('released',encoding='ascii')\n"
        )
        encoded = __import__("base64").b64encode(
            json.dumps(active_record, separators=(",", ":"), allow_nan=False).encode("utf-8")
        ).decode("ascii")
        observations = {}

        def launch_external_publisher(receipt):
            nonlocal worker
            worker = subprocess.Popen(
                [sys.executable, "-c", worker_source, str(fixture.controller.channel.path), str(marker), encoded],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            time.sleep(0.25)
            observations["blocked_before_ack"] = not marker.exists() and worker.poll() is None
            if not observations["blocked_before_ack"]:
                output, error = worker.communicate(timeout=5)
                raise AssertionError(
                    f"跨进程publisher在dispatch ACK前未保持阻塞：exit={worker.returncode}, "
                    f"stdout={output!r}, stderr={error!r}, marker={marker.exists()}"
                )

        fixture.before_ack_hook = launch_external_publisher
        fixture.controller.claim_dispatch(
            permit, fixture._dispatch_callback, ready_receipt=fixture.controller.ready_receipt
        )
        if worker is None:
            raise AssertionError("外部publisher fixture没有启动")
        stdout, stderr = worker.communicate(timeout=5)
        if worker.returncode != 0 or not marker.is_file():
            raise AssertionError(f"ACK后外部publisher未成功完成：{worker.returncode}, {stderr!r}")
        if fixture.controller.process_new_heartbeats() != 1 or fixture.controller.state != "ACTIVE":
            raise AssertionError("租约释放后的ACTIVE没有按序被消费者接收")
        if not observations.get("blocked_before_ack"):
            raise AssertionError("没有观察到外部状态发布被ACK租约阻塞")
        checks.append("dispatch-lease-cross-process-publisher-blocked-until-ack")
    finally:
        if worker is not None and worker.poll() is None:
            worker.kill()
            worker.wait(timeout=5)
        fixture.cleanup()


def _test_close_handle_failures(run_root: Path, checks: list[str]) -> None:
    for target in ("job", "member", "primary-preserved"):
        fixture = FixtureSession(run_root)
        original_close = job_guard._api_close_handle
        failed_handles = set()
        job_handle = fixture.job.handle
        member_handles = {member["handle"] for member in fixture.job.member_handles.values()}

        def injected_close(handle):
            should_fail = handle == job_handle if target == "job" else handle in member_handles
            if should_fail and handle not in failed_handles:
                failed_handles.add(handle)
                ctypes.set_last_error(5)
                return False
            return bool(original_close(handle))

        try:
            fixture.start()
            job_handle = fixture.job.handle
            member_handles = {member["handle"] for member in fixture.job.member_handles.values()}
            job_guard._api_close_handle = injected_close
            if target == "primary-preserved":
                try:
                    fixture.controller.abort("primary injected failure")
                except ross_guard.RossJobGuardError as error:
                    if "primary injected failure" not in str(error) or "关闭自有Job失败" not in str(error):
                        raise AssertionError("清理失败覆盖了主异常或没有进入failure记录")
                    checks.append("close-failure-preserves-primary-exception")
                else:
                    raise AssertionError("注入的主异常未被保留")
            else:
                try:
                    fixture.job.close()
                except job_guard.GateBlocked:
                    checks.append(f"closehandle-{target}-failure-is-guard-failure")
                else:
                    raise AssertionError(f"CloseHandle({target})失败未被报告")
                if not fixture.job.cleanup_errors:
                    raise AssertionError(f"CloseHandle({target})错误没有持久记录")
            if fixture.job.closed:
                raise AssertionError(f"CloseHandle({target})失败后Job被误标为closed")
        finally:
            job_guard._api_close_handle = original_close
            if not fixture.job.closed:
                fixture.job.close()
            fixture.cleanup()


def _test_adapter_negatives(checks: list[str]) -> None:
    adapter = ross_guard.StrictCanonicalAdapter()
    now = time.monotonic()
    baseline = {
        "schema": ross_guard.SCHEMA,
        "session_id": SESSION_ID,
        "deployment_type": "local",
        "clock_domain": "host_monotonic",
        "event": "HEARTBEAT",
        "session_state": "idle",
        "active_command_sha256": None,
        "completed_command_sha256": None,
        "completed_exit_code": None,
        "root_identity": {
            "pid": os.getpid(),
            "create_time": 1.0,
            "exe": sys.executable,
            "cwd": str(Path.cwd()),
            "cmdline": [sys.executable],
            "ppid": os.getpid(),
        },
        "heartbeat_sequence": 0,
        "observed_monotonic": now,
        "published_monotonic": now,
        "progress_counter": 0,
        "progress_monotonic": now,
    }
    for label, field, value in (
        ("future-observed", "observed_monotonic", now + 20.0),
        ("future-published", "published_monotonic", now + 20.0),
        ("nan-observed", "observed_monotonic", float("nan")),
        ("infinite-published", "published_monotonic", float("inf")),
        ("published-before-observed", "published_monotonic", now - 1.0),
    ):
        candidate = dict(baseline)
        candidate[field] = value
        if label == "future-observed":
            candidate["published_monotonic"] = value
        if label == "published-before-observed":
            candidate["observed_monotonic"] = now
        _expect_rejection(
            f"adapter-{label}",
            lambda candidate=candidate: adapter.decode(candidate, SESSION_ID, time.monotonic()),
            checks,
        )
    _expect_rejection(
        "adapter-wrong-session",
        lambda: adapter.decode(baseline, "other-session", time.monotonic()),
        checks,
    )
    _expect_rejection(
        "raw-mcp-schema-unbound",
        lambda: adapter.decode_raw_mcp_result("vivado_list_sessions", {}, {"content": []}),
        checks,
    )


def _mcp_text_result(payload: object) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}]}


def _real_mcp_fixture() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict, dict]:
    """使用2026-10-13原始ROSS文本schema构造隔离夹具。"""
    session_id = ross_guard.EXPECTED_REAL_SESSION_ID
    process_id = ross_guard.EXPECTED_REAL_PROCESS_ID
    working_dir = ross_guard.EXPECTED_REAL_WORKING_DIR
    log_file = ross_guard.EXPECTED_REAL_LOG_FILE
    webserver_url = ross_guard.EXPECTED_REAL_WEBSERVER_URL
    start = {
        "log_file": log_file,
        "message": (
            "Vivado started successfully in TCL mode (no GUI) with webserver at http://localhost:8088.\n\n"
            f"Process ID: {process_id}\nWorking directory: {working_dir}\n"
            f"Log file: {log_file} (unique per session)\n\n"
            "Use vivado_execute to run commands. Use vivado_stop to close Vivado."
        ),
        "mode": "tcl",
        "process_id": process_id,
        "session_id": session_id,
        "status": "success",
        "webserver_url": webserver_url,
        "working_dir": working_dir,
    }
    session = {
        "deployment_type": "local",
        "gui_surface": "none",
        "hostname": "HAO",
        "log_file": log_file,
        "process_id": process_id,
        "process_running": True,
        "proxy_addr": "127.0.0.1:7763",
        "session_id": session_id,
        "session_type": "general",
        "uptime_seconds": 5,
        "vivado_version": "2026.1",
        "webserver_healthy": True,
        "webserver_url": webserver_url,
        "working_dir": working_dir,
    }
    listed = {
        "non_recoverable_sessions": None,
        "sessions": {session_id: session},
    }
    status = {
        "deployment_type": "local",
        "hostname": "HAO",
        "is_command_running": False,
        "last_completed_code": None,
        "last_completed_elapsed": None,
        "last_completed_seconds_ago": None,
        "log_file": log_file,
        "process_id": process_id,
        "process_running": True,
        "queue_length": 0,
        "server_log": r"C:\Users\22061\.vivado-ai\server_HAO.log",
        "session_type": "general",
        "status_summary": "Idle",
        "webserver_healthy": True,
        "webserver_url": webserver_url,
        "working_dir": working_dir,
    }
    status_second = dict(status)
    status_second["task_progress"] = "1/5: 受控生成bitstream与离线部署包 (active)"
    identity = {
        "pid": process_id,
        "create_time": 1791838635.5140712,
        "exe": ross_guard.EXPECTED_REAL_VIVADO_EXE,
        "cwd": working_dir,
        "cmdline": [
            "D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe",
            "-mode",
            "tcl",
            "-log",
            r".vivado-ai\vivado_38634180_babcd0b6.log",
            "-journal",
            r".vivado-ai\vivado_38634180_babcd0b6.jou",
            "-notrace",
            "-source",
            r".vivado-ai\init_38634180_babcd0b6.tcl",
        ],
        "ppid": 24864,
    }
    start_input = {
        "working_dir": working_dir,
        "session_type": "general",
        "gui_mode": False,
        "link_todos": True,
    }
    status_input = {"session_id": session_id, "action": "session"}
    return (
        start_input,
        _mcp_text_result(start),
        {},
        _mcp_text_result(listed),
        status_input,
        _mcp_text_result(status),
        dict(status_input),
        _mcp_text_result(status_second),
        identity,
    )


def _test_real_mcp_schema_binding(run_root: Path, checks: list[str]) -> None:
    adapter = ross_guard.StrictCanonicalAdapter()
    start_input, start_result, list_input, list_result, status_input, status_result, status_input_second, status_result_second, identity = _real_mcp_fixture()
    identity_calls = []

    def read_identity(pid: int) -> dict:
        if pid != identity["pid"]:
            raise AssertionError(f"身份读取器收到非预期PID：{pid}")
        identity_calls.append(pid)
        return dict(identity, cmdline=list(identity["cmdline"]))

    canonical = adapter.decode_vivado_idle_observation(
        start_input,
        start_result,
        list_input,
        list_result,
        status_input,
        status_result,
        status_input_second,
        status_result_second,
        identity_reader=read_identity,
    )
    if set(canonical) != ross_guard.OBSERVATION_FIELDS:
        raise AssertionError("真实ROSS回执未生成字段精确的canonical观察")
    if canonical["session_id"] != ross_guard.EXPECTED_REAL_SESSION_ID or canonical["session_state"] != "idle":
        raise AssertionError("真实ROSS回执未绑定预期session或idle状态")
    if canonical["root_identity"] != identity or identity_calls != [identity["pid"], identity["pid"]]:
        raise AssertionError("真实ROSS PID的psutil六字段双读没有完全一致")
    malformed_start_inputs = (
        None,
        {key: value for key, value in start_input.items() if key != "link_todos"},
        dict(start_input, unexpected=True),
        dict(start_input, working_dir=r"C:\\other\\path"),
        dict(start_input, session_type="project"),
        dict(start_input, gui_mode=True),
        dict(start_input, link_todos=False),
    )
    for bad_start_input in malformed_start_inputs:
        try:
            adapter.decode_vivado_idle_observation(
                bad_start_input,
                start_result,
                list_input,
                list_result,
                status_input,
                status_result,
                status_input_second,
                status_result_second,
                identity_reader=read_identity,
            )
        except ross_guard.RossGuardError:
            continue
        else:
            raise AssertionError("vivado_start的缺失或合成tool_input没有fail closed")
    try:
        adapter.decode_vivado_idle_observation(
            start_result,
            list_input,
            list_result,
            status_input,
            status_result,
            status_input_second,
            status_result_second,
            identity_reader=read_identity,
        )
    except TypeError:
        pass
    else:
        raise AssertionError("缺少vivado_start tool_input时接口未拒绝调用")
    checks.append("real-start-input-list-two-idle-statuses-double-psutil-identity-binding")

    def reject(label: str, *, st=None, li=None, lr=None, si=None, sr=None, si2=None, sr2=None, reader=read_identity) -> None:
        _expect_rejection(
            f"real-mcp-{label}",
            lambda: adapter.decode_vivado_idle_observation(
                start_input,
                start_result if st is None else st,
                list_input if li is None else li,
                list_result if lr is None else lr,
                status_input if si is None else si,
                status_result if sr is None else sr,
                status_input_second if si2 is None else si2,
                status_result_second if sr2 is None else sr2,
                identity_reader=reader,
            ),
            checks,
        )

    listed = json.loads(list_result["content"][0]["text"])
    status = json.loads(status_result["content"][0]["text"])
    started = json.loads(start_result["content"][0]["text"])
    session_id = ross_guard.EXPECTED_REAL_SESSION_ID

    fixture = FixtureSession(run_root)
    try:
        history_values = (
            ("last_completed_code", 0),
            ("last_completed_elapsed", 0.25),
            ("last_completed_seconds_ago", 1.0),
        )
        status_second = json.loads(status_result_second["content"][0]["text"])
        for status_index in ("first", "second"):
            for field, value in history_values:
                first_observation = dict(status)
                second_observation = dict(status_second)
                if status_index == "first":
                    first_observation[field] = value
                else:
                    second_observation[field] = value
                first_result = _mcp_text_result(first_observation)
                second_result = _mcp_text_result(second_observation)

                def decode_then_start() -> dict:
                    canonical = adapter.decode_vivado_idle_observation(
                        start_input,
                        start_result,
                        list_input,
                        list_result,
                        status_input,
                        first_result,
                        status_input_second,
                        second_result,
                        identity_reader=read_identity,
                    )
                    return fixture.controller.start(canonical)

                _expect_rejection(
                    f"real-mcp-ready-rejects-{status_index}-idle-history-{field}",
                    decode_then_start,
                    checks,
                )
                if fixture.controller.state != "NEW" or fixture.controller.ready_receipt is not None:
                    raise AssertionError(f"非空历史字段 {status_index}.{field} 被canonical化并产生READY")
                if fixture.job.pid_list():
                    raise AssertionError(f"非空历史字段 {status_index}.{field} 在拒绝前已加入Job")
    finally:
        fixture.cleanup()
    checks.append("real-mcp-idle-history-rejected-before-ready")

    multi = json.loads(json.dumps(listed))
    multi["sessions"]["other-session"] = dict(multi["sessions"][session_id])
    reject("multiple-sessions", lr=_mcp_text_result(multi))

    for label, field, bad_value in (
        ("start-not-success", "status", "failed"),
        ("start-not-tcl", "mode", "gui"),
        ("start-wrong-session", "session_id", "other-session"),
        ("start-wrong-pid", "process_id", ross_guard.EXPECTED_REAL_PROCESS_ID + 1),
        ("start-wrong-working-dir", "working_dir", r"C:\other\path"),
    ):
        candidate = dict(started)
        candidate[field] = bad_value
        reject(label, st=_mcp_text_result(candidate))
    candidate = dict(started, unexpected=True)
    reject("start-extra-field", st=_mcp_text_result(candidate))
    candidate = dict(started)
    candidate.pop("mode")
    reject("start-missing-field", st=_mcp_text_result(candidate))

    for label, field, bad_value in (
        ("remote-deployment", "deployment_type", "ssh"),
        ("wrong-session-key", "session_id", "other-session"),
        ("wrong-version", "vivado_version", "2026.2"),
        ("wrong-working-dir", "working_dir", r"C:\other\path"),
        ("wrong-gui-surface", "gui_surface", "on-screen"),
        ("not-running", "process_running", False),
    ):
        candidate = json.loads(json.dumps(listed))
        candidate["sessions"][session_id][field] = bad_value
        reject(label, lr=_mcp_text_result(candidate))

    for label, field, bad_value in (
        ("command-running", "is_command_running", True),
        ("queue-not-empty", "queue_length", 1),
        ("status-not-idle", "status_summary", "Busy"),
        ("status-wrong-pid", "process_id", ross_guard.EXPECTED_REAL_PROCESS_ID + 1),
        ("status-wrong-working-dir", "working_dir", r"C:\other\path"),
    ):
        candidate = dict(status)
        candidate[field] = bad_value
        reject(label, sr=_mcp_text_result(candidate))

    for label, bad_input in (
        ("list-input-extra", {"unexpected": True}),
        ("status-input-session-mismatch", {"session_id": "other-session", "action": "session"}),
        ("status-input-action-mismatch", {"session_id": session_id, "action": "health"}),
        ("status-input-extra", {"session_id": session_id, "action": "session", "extra": 1}),
    ):
        if label == "list-input-extra":
            reject(label, li=bad_input)
        else:
            reject(label, si=bad_input)

    def wrong_identity(field: str, value: object) -> None:
        candidate = dict(identity, cmdline=list(identity["cmdline"]))
        candidate[field] = value

        def reader(pid: int) -> dict:
            return candidate

        reject(f"psutil-{field}-mismatch", reader=reader)

    wrong_identity("pid", ross_guard.EXPECTED_REAL_PROCESS_ID + 1)
    wrong_identity("exe", r"D:\other\vivado.exe")
    wrong_identity("cwd", r"C:\other\path")
    wrong_identity("cmdline", [identity["cmdline"][0], "-mode", "gui"])

    unstable_reads = [dict(identity, cmdline=list(identity["cmdline"])), dict(identity, cmdline=list(identity["cmdline"]))]
    unstable_reads[1]["create_time"] += 0.001

    def unstable_reader(pid: int) -> dict:
        if not unstable_reads:
            raise AssertionError("测试读取次数超过双读范围")
        return unstable_reads.pop(0)

    reject("psutil-double-read-drift", reader=unstable_reader)

    for label, mutate in (
        ("list-root-extra", lambda value: value.update(extra=True)),
        ("list-root-missing", lambda value: value.pop("sessions")),
    ):
        candidate = json.loads(json.dumps(listed))
        mutate(candidate)
        reject(label, lr=_mcp_text_result(candidate))

    candidate = json.loads(json.dumps(listed))
    candidate["sessions"][session_id]["unexpected"] = True
    reject("session-extra-field", lr=_mcp_text_result(candidate))
    candidate = json.loads(json.dumps(listed))
    candidate["sessions"][session_id].pop("proxy_addr")
    reject("session-missing-field", lr=_mcp_text_result(candidate))
    candidate = dict(status, unexpected=True)
    reject("status-extra-field", sr=_mcp_text_result(candidate))
    candidate = dict(status)
    candidate.pop("queue_length")
    reject("status-missing-field", sr=_mcp_text_result(candidate))
    candidate = dict(status, task_progress=None)
    reject("status-progress-invalid", sr=_mcp_text_result(candidate))
    candidate = dict(status, hostname="OTHER")
    reject("status-session-cross-mismatch", sr=_mcp_text_result(candidate))
    candidate = json.loads(status_result_second["content"][0]["text"])
    candidate["queue_length"] = 1
    reject("second-status-busy", sr2=_mcp_text_result(candidate))
    reject("second-status-input-mismatch", si2={"session_id": session_id, "action": "health"})
    reject("malformed-json", lr={"content": [{"type": "text", "text": "{"}]})
    reject("missing-content", lr={})
    reject("multiple-content-blocks", lr={"content": [{"type": "text", "text": "{}"}, {"type": "text", "text": "{}"}]})
    reject("wrong-content-type", lr={"content": [{"type": "image", "text": "{}"}]})
    reject("outer-extra-field", lr={"content": [{"type": "text", "text": "{}"}], "isError": False})
    reject("content-block-extra-field", lr={"content": [{"type": "text", "text": "{}", "annotations": {}}]})
    duplicate_json = '{"non_recoverable_sessions":null,"sessions":{},"sessions":{}}'
    reject("duplicate-json-key", lr={"content": [{"type": "text", "text": duplicate_json}]})


def _test_initial_record_failures(run_root: Path, checks: list[str]) -> None:
    cases = (
        ("wrong-session", {"session_id": "different-session"}),
        ("wrong-state", {"session_state": "active", "active_command_sha256": "a" * 64}),
        ("wrong-identity", None),
        ("unauthorized-completion", {"completed_command_sha256": "b" * 64, "completed_exit_code": 0}),
    )
    for name, overrides in cases:
        fixture = FixtureSession(run_root)
        try:
            values = {} if overrides is None else dict(overrides)
            if name == "wrong-identity":
                identity = fixture.identity()
                identity["ppid"] += 100000
                values["root_identity"] = identity
            _expect_rejection(name, lambda: fixture.start(**values), checks)
            if fixture.controller.state != "FAILED":
                raise AssertionError(f"{name}后状态没有fail closed")
        finally:
            fixture.cleanup()


def _test_command_failure(run_root: Path, checks: list[str]) -> None:
    fixture = FixtureSession(run_root)
    try:
        ready = fixture.start()
        if ready["kind"] != "READY" or fixture.job.pid_list() != (fixture.process.pid,):
            raise AssertionError("READY没有精确绑定唯一root Job成员")
        permit = fixture.controller.issue_dispatch_permit()
        first = fixture.controller.claim_dispatch(permit, fixture._dispatch_callback, ready_receipt=fixture.controller.ready_receipt)
        _expect_rejection(
            "wrong-command-sha",
            lambda: fixture.publish(state="active", active_sha="0" * 64),
            checks,
        )
        if fixture.controller.state != "FAILED":
            raise AssertionError("错误命令SHA未令guard进入FAILED")
        if not fixture.job.closed:
            raise AssertionError("错误命令SHA后未关闭KILL_ON_JOB_CLOSE Job句柄")
        deadline = time.monotonic() + 5.0
        while psutil.pid_exists(fixture.process.pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        if psutil.pid_exists(fixture.process.pid):
            raise AssertionError("错误命令SHA后本Job成员未退出")
        if first["session_id"] != SESSION_ID or first["command_sha256"] != permit.command_sha256:
            raise AssertionError("许可session/命令SHA绑定不一致")
    finally:
        fixture.cleanup()


def _test_lost_heartbeat_and_no_progress(run_root: Path, checks: list[str]) -> None:
    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        _expect_rejection(
            "lost-heartbeat",
            lambda: fixture.controller._assert_fresh(time.monotonic() + ross_guard.HANDOFF_LIMIT_SECONDS + 1.0),
            checks,
        )
    finally:
        fixture.cleanup()
    fixture = FixtureSession(run_root)
    try:
        old_progress = max(0.0, time.monotonic() - ross_guard.NO_PROGRESS_LIMIT_SECONDS - 1.0)
        fixture.start(progress_monotonic=old_progress)
        permit = fixture.controller.issue_dispatch_permit()
        receipt = fixture.controller.claim_dispatch(permit, fixture._dispatch_callback, ready_receipt=fixture.controller.ready_receipt)
        _expect_rejection(
            "no-progress-900s",
            lambda: fixture.publish(
                state="active",
                active_sha=receipt["command_sha256"],
                completed_sha=None,
                exit_code=None,
                advance_progress=False,
                progress_monotonic=old_progress,
            ),
            checks,
        )
    finally:
        fixture.cleanup()


def _test_stop_reset_and_terminal_member(run_root: Path, checks: list[str]) -> dict:
    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        fixture.dispatch_two_commands(stop=True)
        if fixture.controller.state != "STOPPED":
            raise AssertionError("合法固定命令序列没有进入STOPPED")
        _expect_rejection(
            "stop-terminal-reset",
            lambda: fixture.publish(state="idle", completed_sha=fixture.controller.last_completed_sha256, exit_code=0),
            checks,
        )
        if fixture.controller.state != "FAILED":
            raise AssertionError("STOP复位尝试后状态没有fail closed")
    finally:
        fixture.cleanup()

    fixture = FixtureSession(run_root)
    try:
        fixture.start()
        child_pid = fixture.spawn_child()
        if child_pid not in fixture.job.pid_list():
            raise AssertionError("子进程没有自动继承本次inner Job")
        fixture.dispatch_two_commands(stop=True)
        fixture.ask_root_exit()
        fixture.process.wait(timeout=5)
        _expect_rejection(
            "terminal-member-remains",
            lambda: fixture.controller.verify_terminal(timeout_seconds=0.25),
            checks,
        )
        deadline = time.monotonic() + 5.0
        while psutil.pid_exists(child_pid) and time.monotonic() < deadline:
            time.sleep(0.05)
        if psutil.pid_exists(child_pid):
            raise AssertionError("拒绝残留成员后未通过本Job关闭清理fixture child")
        return {"child_pid": child_pid, "job_closed": fixture.job.closed, "child_gone_after_fail_closed": True}
    finally:
        fixture.cleanup()


def _test_success_flow(run_root: Path, checks: list[str]) -> dict:
    fixture = FixtureSession(run_root)
    try:
        ready = fixture.start()
        sample = fixture.controller.sample_once()
        receipts = fixture.dispatch_two_commands(stop=True)
        if fixture.controller.state != "STOPPED" or len(receipts) != 2:
            raise AssertionError("READY→两条固定命令→STOP状态机没有完成")
        fixture.ask_root_exit()
        fixture.process.wait(timeout=5)
        final = fixture.controller.verify_terminal(timeout_seconds=5.0)
        if fixture.controller.state != "CLOSED" or final["job_pids"] or final["unknown_members"]:
            raise AssertionError("合法终态没有闭合Job成员和身份句柄")
        if [item["sequence"] for item in fixture.dispatch_events] != [0, 1]:
            raise AssertionError("两条命令没有通过锁内dispatch callback顺序派发")
        if not fixture.controller.job.closed or not fixture.controller._ready_consumed:
            raise AssertionError("Job句柄或READY token没有正确关闭/消费")
        checks.append("success-ready-two-command-stop-terminal-close")
        permit_summaries = []
        for index, receipt in enumerate(receipts):
            summary = {
                key: receipt[key]
                for key in (
                    "session_id",
                    "sequence",
                    "command",
                    "command_sha256",
                    "dcp_sha256",
                    "output_path",
                    "issued_monotonic",
                    "claimed_monotonic",
                    "mcp_call_required_by_outer_controller",
                    "acknowledgement",
                )
            }
            summary.update(
                {
                    "controller_id_type": type(receipt["controller_id"]).__name__,
                    "controller_id_length": len(receipt["controller_id"]),
                    "permit_nonce_type": type(receipt["permit_nonce"]).__name__,
                    "permit_nonce_length": len(receipt["permit_nonce"]),
                    "controller_state_at_callback": fixture.dispatch_events[index]["controller_state"],
                    "permit_nonce_consumed_at_callback": fixture.dispatch_events[index]["nonce_consumed"],
                }
            )
            permit_summaries.append(summary)
        return {
            "ready": ready,
            "sample": sample,
            "permits": permit_summaries,
            "terminal": final,
            "metrics": fixture.controller.metrics(),
        }
    finally:
        fixture.cleanup()


def run_short(run_root: Path) -> dict:
    checks: list[str] = []
    _test_adapter_negatives(checks)
    _test_real_mcp_schema_binding(run_root, checks)
    _test_handle_pid_reuse(run_root, checks)
    _test_initial_record_failures(run_root, checks)
    _test_command_failure(run_root, checks)
    _test_lost_heartbeat_and_no_progress(run_root, checks)
    _test_unseen_status_invalidates_permit(run_root, checks)
    _test_permit_and_ready_receipts(run_root, checks)
    _test_output_directory_anchor(run_root, checks)
    _test_directory_anchor_chain(run_root, checks)
    _test_dispatch_ack_fail_closed(run_root, checks)
    _test_dispatch_timeout_and_late_ack(run_root, checks)
    _test_dispatch_publisher_linearization(run_root, checks)
    _test_close_handle_failures(run_root, checks)
    _test_process_snapshot_close_failure(checks)
    terminal_case = _test_stop_reset_and_terminal_member(run_root, checks)
    success = _test_success_flow(run_root, checks)
    return {"status": "PASS", "checks": checks, "terminal_member_case": terminal_case, "success_flow": success}


def _resource_preflight() -> dict:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    forbidden = []
    for process in psutil.process_iter(attrs=["pid", "name"]):
        try:
            name = (process.info.get("name") or "").casefold()
            if name in {"vivado.exe", "vitis.exe", "vitis_hls.exe", "xsct.exe"}:
                forbidden.append({"pid": process.info["pid"], "name": process.info["name"]})
        except psutil.Error:
            continue
    result = {
        "available_ram_bytes": int(memory.available),
        "c_disk_free_bytes": int(disk.free),
        "heavy_vendor_processes": forbidden,
        "ram_floor_bytes": job_guard.RAM_FLOOR_BYTES,
        "disk_floor_bytes": job_guard.DISK_FLOOR_BYTES,
    }
    if memory.available < job_guard.RAM_FLOOR_BYTES or disk.free < job_guard.DISK_FLOOR_BYTES or forbidden:
        raise RuntimeError(f"长测启动资源/进程预检未通过：{result}")
    return result


def run_stress(run_root: Path, duration_seconds: float = 600.0) -> dict:
    preflight = _resource_preflight()
    fixture = FixtureSession(run_root)
    producer_errors: list[str] = []
    sampler_errors: list[str] = []
    publisher_stop = threading.Event()
    abort_event = threading.Event()
    sampler_done = threading.Event()
    sample_lock = threading.Lock()
    producer_start = time.monotonic()
    sample_results: list[dict] = []
    sample_thread_id = None
    publisher_thread_id = None
    try:
        fixture.start()
        nominal_period = 1.0
        scheduler_margin = 0.1
        scheduled_period = nominal_period - scheduler_margin
        interval_count = math.ceil(duration_seconds / scheduled_period)
        start_anchor = time.monotonic()

        def wait_until(deadline: float) -> None:
            """按绝对deadline等待；异常时可由abort_event立即打断。"""
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0.0:
                    return
                if abort_event.wait(min(remaining, 0.05)):
                    return

        def producer() -> None:
            nonlocal publisher_thread_id
            publisher_thread_id = threading.get_native_id()
            index = 1
            while not publisher_stop.is_set():
                deadline = start_anchor + float(index) * scheduled_period
                if deadline > start_anchor + duration_seconds + scheduled_period:
                    return
                wait_until(deadline)
                if publisher_stop.is_set() or abort_event.is_set():
                    return
                try:
                    now = time.monotonic()
                    record = {
                        "schema": ross_guard.SCHEMA,
                        "session_id": SESSION_ID,
                        "deployment_type": "local",
                        "clock_domain": "host_monotonic",
                        "event": "HEARTBEAT",
                        "session_state": "idle",
                        "active_command_sha256": None,
                        "completed_command_sha256": None,
                        "completed_exit_code": None,
                        "root_identity": fixture.identity(),
                        "heartbeat_sequence": index,
                        "observed_monotonic": now,
                        "published_monotonic": now,
                        "progress_counter": 0,
                        "progress_monotonic": fixture.controller.progress_monotonic,
                    }
                    fixture.controller.channel.publish(record)
                    index += 1
                except BaseException:
                    producer_errors.append(traceback.format_exc())
                    abort_event.set()
                    return

        def sampler() -> None:
            nonlocal sample_thread_id
            sample_thread_id = threading.get_native_id()
            first_start = None
            index = 0
            try:
                while True:
                    anchor = start_anchor if first_start is None else first_start
                    wait_until(anchor + float(index) * scheduled_period)
                    if abort_event.is_set():
                        return
                    sample = fixture.controller.sample_once()
                    with sample_lock:
                        sample_results.append(sample)
                    if first_start is None:
                        first_start = sample["sample_start_monotonic"]
                    if sample["sample_start_monotonic"] - first_start >= duration_seconds:
                        sampler_done.set()
                        return
                    index += 1
            except BaseException:
                sampler_errors.append(traceback.format_exc())
                abort_event.set()
            finally:
                sampler_done.set()

        publisher = threading.Thread(target=producer, name="ross-guard-fixture-publisher", daemon=True)
        sampler_thread = threading.Thread(target=sampler, name="ross-job-guard-sampler", daemon=True)
        publisher.start()
        sampler_thread.start()
        while not sampler_done.wait(0.25):
            if producer_errors or sampler_errors:
                break
        if producer_errors:
            raise RuntimeError(producer_errors[-1])
        if sampler_errors:
            raise RuntimeError(sampler_errors[-1])
        with sample_lock:
            captured_samples = list(sample_results)
        publisher_stop.set()
        publisher.join(timeout=5)
        sampler_thread.join(timeout=5)
        if publisher.is_alive():
            raise TimeoutError("heartbeat fixture publisher未按时退出")
        if sampler_thread.is_alive():
            raise TimeoutError("独立Job采样线程未按时退出")
        if len(captured_samples) != interval_count + 1:
            raise AssertionError(f"独立采样线程样本数不符：expected={interval_count + 1}, actual={len(captured_samples)}")
        sample_results = captured_samples
        fixture.controller.process_new_heartbeats()
        elapsed = sample_results[-1]["sample_start_monotonic"] - sample_results[0]["sample_start_monotonic"]
        if elapsed < duration_seconds:
            raise AssertionError(f"采样未覆盖计划闭区间：planned={duration_seconds}, elapsed={elapsed}, samples={len(sample_results)}")
        gaps = [sample_results[i]["sample_start_monotonic"] - sample_results[i - 1]["sample_start_monotonic"] for i in range(1, len(sample_results))]
        if any(not math.isfinite(gap) or gap > job_guard.SAMPLE_GAP_LIMIT_SECONDS for gap in gaps):
            raise AssertionError(f"出现超1秒采样间隔：max={max(gaps)}")
        if any(sample["uncertainty_count"] != 0 for sample in sample_results):
            raise AssertionError("压力测出现uncertainty")
        if any(sample["tree_rss_bytes"] is None or sample["tree_rss_bytes"] > job_guard.RSS_LIMIT_BYTES for sample in sample_results):
            raise AssertionError("压力测树RSS缺失或越过6GiB")
        if any(sample["available_ram_bytes"] is None or sample["available_ram_bytes"] < job_guard.RAM_FLOOR_BYTES for sample in sample_results):
            raise AssertionError("压力测可用RAM低于512MiB或unknown")
        if any(sample["c_disk_free_bytes"] is None or sample["c_disk_free_bytes"] < job_guard.DISK_FLOOR_BYTES for sample in sample_results):
            raise AssertionError("压力测C盘余量低于8GiB或unknown")
        if any(sample["ross_status_freshness_seconds"] > ross_guard.HEARTBEAT_FRESHNESS_SECONDS for sample in sample_results):
            raise AssertionError("压力测ROSS状态freshness超过10秒")
        if any(sample["supervisor_handoff_seconds"] > ross_guard.HANDOFF_LIMIT_SECONDS for sample in sample_results):
            raise AssertionError("压力测监督handoff超过5秒")
        receipts = fixture.dispatch_two_commands(stop=True)
        fixture.ask_root_exit()
        fixture.process.wait(timeout=5)
        terminal = fixture.controller.verify_terminal(timeout_seconds=5.0)
        if terminal["job_pids"] or terminal["active_processes"] or terminal["live_members"] or terminal["unknown_members"]:
            raise AssertionError("长测后的Job终态成员未闭合")
        rss_values = [sample["tree_rss_bytes"] for sample in sample_results]
        return {
            "status": "PASS",
            "preflight": preflight,
            "planned_duration_seconds": duration_seconds,
            "nominal_sample_period_seconds": nominal_period,
            "scheduled_sample_period_seconds": scheduled_period,
            "windows_scheduler_lead_seconds": scheduler_margin,
            "independent_sampler_thread": True,
            "sampler_native_thread_id": sample_thread_id,
            "publisher_native_thread_id": publisher_thread_id,
            "measured_sample_window_seconds": elapsed,
            "sample_count": len(sample_results),
            "sample_interval_count": len(gaps),
            "max_sample_start_gap_seconds": max(gaps),
            "max_consumer_handoff_age_seconds": max(item["supervisor_handoff_seconds"] for item in sample_results),
            "max_ross_status_freshness_seconds": max(item["ross_status_freshness_seconds"] for item in sample_results),
            "max_supervisor_handoff_seconds": max(item["supervisor_handoff_seconds"] for item in sample_results),
            "max_tree_rss_bytes": max(rss_values),
            "min_available_ram_bytes": min(item["available_ram_bytes"] for item in sample_results),
            "min_c_disk_free_bytes": min(item["c_disk_free_bytes"] for item in sample_results),
            "uncertainty_total": sum(item["uncertainty_count"] for item in sample_results),
            "terminal": terminal,
            "post_stress_permits": receipts,
            "metrics": fixture.controller.metrics(),
            "publisher_errors": producer_errors,
            "wall_elapsed_seconds": time.monotonic() - producer_start,
        }
    except BaseException:
        publisher_stop.set()
        abort_event.set()
        if "publisher" in locals():
            publisher.join(timeout=5)
        if "sampler_thread" in locals():
            sampler_thread.join(timeout=5)
        raise
    finally:
        publisher_stop.set()
        abort_event.set()
        fixture.cleanup()


def _runtime_identity() -> dict:
    return {
        "python_executable": str(Path(sys.executable).resolve()),
        "python_sha256": _sha256(Path(sys.executable).resolve()),
        "python_version": sys.version,
        "psutil_version": psutil.__version__,
        "psutil_path": str(Path(psutil.__file__).resolve()),
        "psutil_sha256": _sha256(Path(psutil.__file__).resolve()),
        "platform": sys.platform,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("short", "cadence-smoke", "stress"), required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run_root = _make_run_dir(args.run_id)
    log_path = run_root / "stdout.log"
    summary_path = run_root / "result.json"
    result = {
        "run_id": args.run_id,
        "mode": args.mode,
        "started_utc8": datetime.now().astimezone().isoformat(),
        "runtime": _runtime_identity(),
        "head": subprocess.run(["git", "-C", str(Path(__file__).resolve().parents[1]), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip(),
        "source_sha256": {
            "job_guard.py": _sha256(Path(job_guard.__file__).resolve()),
            "s15_ross_job_guard.py": _sha256(Path(ross_guard.__file__).resolve()),
            "test_s15_ross_job_guard.py": _sha256(Path(__file__).resolve()),
        },
        "command": [sys.executable, str(Path(__file__).resolve()), "--mode", args.mode, "--run-id", args.run_id],
        "exit_code": 1,
    }
    try:
        with log_path.open("x", encoding="utf-8", newline="\n") as log:
            from contextlib import redirect_stderr, redirect_stdout

            with redirect_stdout(log), redirect_stderr(log):
                print(f"mode={args.mode} run_id={args.run_id}")
                if args.mode == "short":
                    output = run_short(run_root)
                elif args.mode == "cadence-smoke":
                    output = run_stress(run_root, duration_seconds=12.0)
                else:
                    output = run_stress(run_root, duration_seconds=600.0)
                result["result"] = output
                result["status"] = "PASS"
                result["exit_code"] = 0
                print(json.dumps(output, ensure_ascii=False, sort_keys=True, allow_nan=False))
    except BaseException:
        result["status"] = "FAIL"
        result["traceback"] = traceback.format_exc()
        try:
            with log_path.open("a", encoding="utf-8", newline="\n") as log:
                log.write(result["traceback"] + "\n")
        except FileNotFoundError:
            pass
    result["finished_utc8"] = datetime.now().astimezone().isoformat()
    _write_json(summary_path, result)
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
