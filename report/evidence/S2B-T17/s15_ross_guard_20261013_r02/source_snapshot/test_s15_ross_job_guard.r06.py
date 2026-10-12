"""离线回归ROSS canonical适配、固定命令许可和Windows Job监护。"""
from __future__ import annotations

import argparse
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
            evidence_root=EVIDENCE_ROOT,
        )
        self.session_id = session_id
        self.child_pid = None

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
            receipt = self.controller.claim_dispatch(permit)
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
        first = fixture.controller.claim_dispatch(permit)
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
        receipt = fixture.controller.claim_dispatch(permit)
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
        checks.append("success-ready-two-command-stop-terminal-close")
        return {
            "ready": ready,
            "sample": sample,
            "permits": receipts,
            "terminal": final,
            "metrics": fixture.controller.metrics(),
        }
    finally:
        fixture.cleanup()


def run_short(run_root: Path) -> dict:
    checks: list[str] = []
    _test_adapter_negatives(checks)
    _test_initial_record_failures(run_root, checks)
    _test_command_failure(run_root, checks)
    _test_lost_heartbeat_and_no_progress(run_root, checks)
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
