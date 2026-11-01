"""为S2B短期工具进程提供资源门槛和Job Object隔离。"""
from __future__ import annotations

import math
import os
import subprocess
import time
from datetime import datetime
from typing import Callable


GIB = 1024 ** 3
START_FLOOR_BYTES = 10 * GIB
STOP_FLOOR_BYTES = 2 * GIB
SAMPLE_INTERVAL_SECONDS = 0.25
MAX_SAMPLE_INTERVAL_SECONDS = 0.25
MAX_SAMPLE_GAP_SECONDS = 1.0
JOB_DRAIN_TIMEOUT_SECONDS = 10.0
MAX_DRAIN_TIMEOUT_SECONDS = 10.0
SUPERVISOR_VERSION = "s2b-job-supervisor/1.0"


class SupervisorError(RuntimeError):
    """资源监视或本任务Job闭合失败。"""


class _DrainWaitFailure(SupervisorError):
    """携带自然排空阶段失败状态。"""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def _finite_positive_seconds(value):
    """验证时间预算为有限正数，并返回统一的浮点秒数。"""
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(seconds) or seconds <= 0:
        return None
    return seconds


def _load_job_guard():
    """加载项目已有的Windows Job Object实现。"""
    try:
        from . import s15_job_guard as job_guard
    except ImportError:
        import s15_job_guard as job_guard
    return job_guard


def _read_memory_status():
    """读取可用物理内存和总物理内存。"""
    return _load_job_guard()._memory_status()


def _validated_memory_sample(memory_reader):
    available, total = memory_reader()
    if type(available) is not int or type(total) is not int:
        raise SupervisorError("GlobalMemoryStatusEx返回非整数内存值")
    if available < 0 or total <= 0 or available > total:
        raise SupervisorError("GlobalMemoryStatusEx返回越界内存值")
    return available, total


def _wait_for_empty_job(
    job,
    root_process,
    timeout_seconds,
    *,
    allow_root_exit_drain=False,
    overall_deadline=None,
    poll_callback=None,
    drain_record=None,
):
    """用Job PID列表、Accounting及root原始HANDLE证明终态。"""
    job_guard = _load_job_guard()
    drain_started = time.monotonic()
    deadline = drain_started + float(timeout_seconds)
    if overall_deadline is not None:
        deadline = min(deadline, overall_deadline)
    stable_reads = 0
    last = None
    if drain_record is not None:
        drain_record.update({
            "status": "RUNNING",
            "elapsed_seconds": 0.0,
            "poll_count": 0,
            "start_job_pids": None,
            "last_job_pids": None,
            "last_active_processes": None,
            "stable_empty_reads": 0,
            "error": None,
        })

    def finish_drain(status, error=None):
        if drain_record is not None:
            drain_record["status"] = status
            drain_record["elapsed_seconds"] = round(time.monotonic() - drain_started, 3)
            drain_record["stable_empty_reads"] = stable_reads
            drain_record["error"] = error

    def check_deadlines(context):
        now = time.monotonic()
        if overall_deadline is not None and now >= overall_deadline:
            message = f"整体wall timeout在{context}到期"
            if allow_root_exit_drain:
                raise _DrainWaitFailure("FAIL_TIMEOUT", message)
            raise SupervisorError(message)
        if now >= deadline:
            message = f"Job自然排空期限在{context}到期"
            if allow_root_exit_drain:
                raise _DrainWaitFailure("FAIL_JOB_NOT_EMPTY", message)
            raise SupervisorError(message)

    while time.monotonic() < deadline:
        if poll_callback is not None:
            poll_callback()
        check_deadlines("Job成员采样前")

        pids_before = tuple(job.pid_list())
        accounting_before = job.accounting()
        root_wait = None
        if root_process is not None:
            root_wait = job_guard._api_wait(root_process.process_handle, 0)
            if root_wait not in (job_guard.WAIT_OBJECT_0, job_guard.WAIT_TIMEOUT):
                raise SupervisorError(f"root HANDLE等待状态未知：{root_wait}")
        pids_after = tuple(job.pid_list())
        accounting_after = job.accounting()
        root_ended = root_process is None or root_wait == job_guard.WAIT_OBJECT_0
        empty = (
            not pids_before and not pids_after
            and accounting_before["active_processes"] == 0
            and accounting_after["active_processes"] == 0
            and root_ended
        )
        last = {
            "job_pids_before": list(pids_before),
            "job_pids_after": list(pids_after),
            "accounting_before": accounting_before,
            "accounting_after": accounting_after,
            "root_signaled": root_ended,
        }
        if drain_record is not None:
            drain_record["poll_count"] += 1
            if drain_record["start_job_pids"] is None:
                drain_record["start_job_pids"] = list(pids_before)
            drain_record["last_job_pids"] = list(pids_after)
            drain_record["last_active_processes"] = accounting_after["active_processes"]
        if empty:
            stable_reads += 1
            if stable_reads >= 2:
                if poll_callback is not None:
                    poll_callback()
                check_deadlines("最终资源采样后")
                if root_process is not None:
                    root_exit_code = job_guard._api_get_exit_code(root_process.process_handle)
                    if root_exit_code == job_guard.STILL_ACTIVE:
                        raise SupervisorError("root已signal但退出码仍为STILL_ACTIVE")
                    last["root_exit_code"] = root_exit_code
                if poll_callback is not None:
                    poll_callback()
                check_deadlines("PASS提交前")
                last["stable_empty_reads"] = stable_reads
                finish_drain("PASS_EMPTY_JOB")
                return last
        else:
            stable_reads = 0
            if root_process is not None and root_ended and not allow_root_exit_drain:
                raise SupervisorError(f"root已退出但本任务Job仍有成员：{last!r}")
        if drain_record is not None:
            drain_record["stable_empty_reads"] = stable_reads
        time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))

    now = time.monotonic()
    if overall_deadline is not None and now >= overall_deadline:
        raise _DrainWaitFailure("FAIL_TIMEOUT", f"整体wall timeout到期，Job未稳定清空：{last!r}")
    if allow_root_exit_drain:
        raise _DrainWaitFailure("FAIL_JOB_NOT_EMPTY", f"Job未在自然排空期限内稳定清空：{last!r}")
    raise SupervisorError(f"Job未在期限内稳定清空：{last!r}")


def _close_owned_handles(job, root_process):
    """关闭本任务Job及launcher返回的root/thread句柄。"""
    job_guard = _load_job_guard()
    errors = []
    if job is not None and not job.closed:
        try:
            job.close()
        except BaseException as error:
            errors.append(f"JobObject.close失败：{error!r}")
    if root_process is not None:
        for name, attribute in (("root thread", "hThread"), ("root process", "hProcess")):
            handle = getattr(root_process.process_info, attribute)
            if not handle:
                continue
            try:
                job_guard._checked_close_handle(handle, name)
            except BaseException as error:
                errors.append(f"CloseHandle({name})失败：{error!r}")
            else:
                setattr(root_process.process_info, attribute, None)
        root_process.closed = not errors
    if errors:
        raise SupervisorError("自有Job/root句柄清理失败：" + "; ".join(errors))


def _checkpoint(callback, payload):
    if callback is not None:
        callback(payload)


def supervise_process(
    *,
    name: str,
    command: list[str],
    cwd: str,
    environment: dict[str, str],
    output_stream,
    timeout_seconds: float,
    memory_reader: Callable[[], tuple[int, int]] | None = None,
    checkpoint_callback: Callable[[dict], None] | None = None,
    sample_interval_seconds: float = SAMPLE_INTERVAL_SECONDS,
    max_sample_gap_seconds: float = MAX_SAMPLE_GAP_SECONDS,
    drain_timeout_seconds: float = JOB_DRAIN_TIMEOUT_SECONDS,
    start_floor_bytes: int = START_FLOOR_BYTES,
    stop_floor_bytes: int = STOP_FLOOR_BYTES,
) -> dict:
    """在独立Job中启动一个root，监视可用RAM并失败关闭。"""
    requested_times = {
        "timeout_seconds": timeout_seconds,
        "sample_interval_seconds": sample_interval_seconds,
        "max_sample_gap_seconds": max_sample_gap_seconds,
        "drain_timeout_seconds": drain_timeout_seconds,
    }
    validated_times = {
        name: _finite_positive_seconds(value)
        for name, value in requested_times.items()
    }
    invalid_time_parameters = [
        name for name, value in validated_times.items() if value is None
    ]
    record_times = {
        name: (validated_times[name] if validated_times[name] is not None
               else repr(requested_times[name]))
        for name in requested_times
    }
    started_wall = datetime.now().astimezone().isoformat(timespec="milliseconds")
    started = time.monotonic()
    record = {
        "name": name,
        "command": list(command),
        "working_directory": str(cwd),
        "timeout_seconds": record_times["timeout_seconds"],
        "exit_code": None,
        "timed_out": False,
        "status": "RUNNING",
        "process_id": None,
        "started_at": started_wall,
        "launch_attempted": False,
        "cleanup_confirmed": False,
        "resource_monitor": {
            "supervisor_version": SUPERVISOR_VERSION,
            "sample_interval_seconds": record_times["sample_interval_seconds"],
            "max_sample_gap_seconds": record_times["max_sample_gap_seconds"],
            "drain_timeout_seconds": record_times["drain_timeout_seconds"],
            "invalid_time_parameters": invalid_time_parameters,
            "invalid_configuration_constraints": [],
            "start_floor_bytes": start_floor_bytes,
            "stop_floor_bytes": stop_floor_bytes,
            "preflight": None,
            "sample_count": 0,
            "minimum_available_ram_bytes": None,
            "total_ram_bytes": None,
            "maximum_sample_gap_seconds": 0.0,
            "last_sample_monotonic": None,
            "failure": None,
        },
        "cleanup": {
            "job_created": False,
            "termination_requested": False,
            "termination_exit_code": None,
            "empty_job_proof": None,
            "job_closed": False,
            "root_process_handle_closed": False,
            "root_thread_handle_closed": False,
            "confirmed": False,
            "natural_drain_failure": None,
            "natural_drain": {
                "status": "NOT_STARTED",
                "timeout_seconds": record_times["drain_timeout_seconds"],
                "resource_samples_at_start": None,
                "resource_samples_at_end": None,
                "wall_timeout_seconds_remaining": None,
            },
            "errors": [],
            "verification_scope": "双次读取Job PID列表为空且Accounting active_processes为0，并确认root原始HANDLE已signal；不要求保留所有短命子进程HANDLE。",
        },
    }
    memory_reader = memory_reader or _read_memory_status
    job_guard = None
    job = None
    root_process = None
    owned_null_stream = None
    owned_stderr_fd = None
    inheritable_handles = []
    original_inheritable = {}
    primary_failure = None

    try:
        configuration_violations = []
        if invalid_time_parameters:
            configuration_violations.extend(
                f"{name}必须为有限正数" for name in invalid_time_parameters)
        if (validated_times["sample_interval_seconds"] is not None
                and validated_times["sample_interval_seconds"] > MAX_SAMPLE_INTERVAL_SECONDS):
            configuration_violations.append(
                f"sample_interval_seconds不能大于{MAX_SAMPLE_INTERVAL_SECONDS:.2f}秒")
        if (validated_times["max_sample_gap_seconds"] is not None
                and validated_times["max_sample_gap_seconds"] > MAX_SAMPLE_GAP_SECONDS):
            configuration_violations.append(
                f"max_sample_gap_seconds不能大于{MAX_SAMPLE_GAP_SECONDS:.1f}秒")
        if (validated_times["drain_timeout_seconds"] is not None
                and validated_times["drain_timeout_seconds"] > MAX_DRAIN_TIMEOUT_SECONDS):
            configuration_violations.append(
                f"drain_timeout_seconds不能大于{MAX_DRAIN_TIMEOUT_SECONDS:.1f}秒")
        if type(stop_floor_bytes) is not int or stop_floor_bytes < STOP_FLOOR_BYTES:
            configuration_violations.append(
                f"stop_floor_bytes不能低于{STOP_FLOOR_BYTES}字节")
        if type(start_floor_bytes) is not int or (
                type(stop_floor_bytes) is int and start_floor_bytes < stop_floor_bytes):
            configuration_violations.append(
                "start_floor_bytes必须是整数且不低于stop_floor_bytes")
        if configuration_violations:
            record["status"] = "FAIL_SUPERVISOR_CONFIG"
            record["resource_monitor"]["invalid_configuration_constraints"] = (
                configuration_violations)
            record["resource_monitor"]["failure"] = (
                "监督器硬约束配置无效：" + "；".join(configuration_violations))
            return record
        timeout_seconds = validated_times["timeout_seconds"]
        sample_interval_seconds = validated_times["sample_interval_seconds"]
        max_sample_gap_seconds = validated_times["max_sample_gap_seconds"]
        drain_timeout_seconds = validated_times["drain_timeout_seconds"]
        try:
            available, total = _validated_memory_sample(memory_reader)
        except Exception as error:
            record["status"] = "FAIL_RESOURCE_PREFLIGHT_QUERY"
            record["resource_monitor"]["failure"] = f"{type(error).__name__}: {error}"
            return record
        preflight = {
            "available_ram_bytes": available,
            "total_ram_bytes": total,
            "meets_start_floor": available >= start_floor_bytes,
            "monotonic_seconds": time.monotonic(),
        }
        record["resource_monitor"]["preflight"] = preflight
        if available < start_floor_bytes:
            record["status"] = "BLOCKED_RESOURCE_PREFLIGHT"
            record["resource_monitor"]["failure"] = (
                f"启动前可用物理内存低于{start_floor_bytes}字节门槛；未创建Job或启动子进程。")
            return record

        if os.name != "nt":
            record["status"] = "FAIL_JOB_UNSUPPORTED_PLATFORM"
            record["error"] = "S2B进程监督要求Windows Job Object"
            return record

        import msvcrt

        job_guard = _load_job_guard()
        try:
            job = job_guard.JobObject(kill_on_close=True)
            record["cleanup"]["job_created"] = True
        except Exception as error:
            record["status"] = "FAIL_JOB_CREATE"
            record["error"] = f"{type(error).__name__}: {error}"
            return record

        owned_null_stream = open(os.devnull, "rb")
        owned_stderr_fd = os.dup(output_stream.fileno())
        stdin_handle = int(msvcrt.get_osfhandle(owned_null_stream.fileno()))
        stdout_handle = int(msvcrt.get_osfhandle(output_stream.fileno()))
        stderr_handle = int(msvcrt.get_osfhandle(owned_stderr_fd))
        inheritable_handles = [stdin_handle, stdout_handle, stderr_handle]
        for handle in {stdin_handle, stdout_handle, stderr_handle}:
            original_inheritable[handle] = os.get_handle_inheritable(handle)
            if not original_inheritable[handle]:
                os.set_handle_inheritable(handle, True)

        record["launch_attempted"] = True
        try:
            root_process = job_guard.launch_suspended_root(
                job,
                command[0],
                command,
                cwd=cwd,
                std_handles=inheritable_handles,
                environment=environment,
            )
            record["process_id"] = root_process.pid
            record["cleanup"]["root_pid"] = root_process.pid
            _checkpoint(checkpoint_callback, {
                "event": "started",
                "message": "root已在本任务Job中完成身份核验并恢复运行",
                "process_id": root_process.pid,
                "elapsed_seconds": time.monotonic() - started,
                "resource_monitor": dict(record["resource_monitor"]),
            })
        except Exception as error:
            primary_failure = "FAIL_JOB_LAUNCH"
            record["error"] = f"{type(error).__name__}: {error}"

        for handle, inheritable in original_inheritable.items():
            if not inheritable:
                os.set_handle_inheritable(handle, False)
        original_inheritable.clear()

        if root_process is not None:
            deadline = started + float(timeout_seconds)
            last_sample = time.monotonic()
            next_checkpoint = started + 15.0
            exit_seen = False
            observed_exit_code = None
            while primary_failure is None:
                now = time.monotonic()
                if now >= deadline:
                    record["timed_out"] = True
                    primary_failure = "FAIL_TIMEOUT"
                    break
                try:
                    available, total = _validated_memory_sample(memory_reader)
                except Exception as error:
                    primary_failure = "FAIL_RESOURCE_QUERY"
                    record["resource_monitor"]["failure"] = f"{type(error).__name__}: {error}"
                    break
                sample_end = time.monotonic()
                if last_sample is not None:
                    gap = sample_end - last_sample
                    monitor = record["resource_monitor"]
                    monitor["maximum_sample_gap_seconds"] = max(monitor["maximum_sample_gap_seconds"], gap)
                    if gap > max_sample_gap_seconds:
                        primary_failure = "FAIL_RESOURCE_SAMPLE_GAP"
                        monitor["failure"] = f"资源采样间隔{gap:.3f}s超过{max_sample_gap_seconds:.3f}s上限"
                        break
                last_sample = sample_end
                monitor = record["resource_monitor"]
                monitor["sample_count"] += 1
                monitor["last_sample_monotonic"] = sample_end
                monitor["total_ram_bytes"] = total
                prior_minimum = monitor["minimum_available_ram_bytes"]
                monitor["minimum_available_ram_bytes"] = available if prior_minimum is None else min(prior_minimum, available)
                try:
                    accounting = job.accounting()
                    pids = list(job.pid_list())
                except Exception as error:
                    primary_failure = "FAIL_JOB_SAMPLE"
                    monitor["failure"] = f"Job成员/Accounting查询失败：{type(error).__name__}: {error}"
                    break
                if available < stop_floor_bytes:
                    primary_failure = "FAIL_RESOURCE_STOP"
                    monitor["failure"] = f"可用物理内存低于{stop_floor_bytes}字节停止线"
                    break
                now = time.monotonic()
                if now >= deadline:
                    record["timed_out"] = True
                    primary_failure = "FAIL_TIMEOUT"
                    break
                try:
                    job_wait = job_guard._api_wait(root_process.process_handle, 0)
                    if job_wait == job_guard.WAIT_OBJECT_0:
                        observed_exit_code = job_guard._api_get_exit_code(root_process.process_handle)
                        if observed_exit_code == job_guard.STILL_ACTIVE:
                            primary_failure = "FAIL_ROOT_EXIT_READBACK"
                            record["error"] = "root已signal但退出码仍为STILL_ACTIVE"
                            break
                        exit_seen = True
                        break
                    if job_wait != job_guard.WAIT_TIMEOUT:
                        primary_failure = "FAIL_ROOT_WAIT"
                        record["error"] = f"root HANDLE等待状态未知：{job_wait}"
                        break
                except Exception as error:
                    primary_failure = "FAIL_ROOT_WAIT"
                    record["error"] = f"{type(error).__name__}: {error}"
                    break
                if now >= deadline:
                    record["timed_out"] = True
                    primary_failure = "FAIL_TIMEOUT"
                    break
                if now >= next_checkpoint:
                    _checkpoint(checkpoint_callback, {
                        "event": "running",
                        "message": "运行中",
                        "process_id": root_process.pid,
                        "elapsed_seconds": now - started,
                        "available_ram_bytes": available,
                        "job_pids": pids,
                        "job_accounting": accounting,
                        "resource_sample_count": monitor["sample_count"],
                    })
                    next_checkpoint += 15.0
                time.sleep(min(float(sample_interval_seconds), max(0.0, deadline - time.monotonic())))

            if exit_seen and primary_failure is None:
                record["exit_code"] = observed_exit_code
                if observed_exit_code != 0:
                    primary_failure = "FAIL_EXIT"
                natural_drain = record["cleanup"]["natural_drain"]
                natural_drain["resource_samples_at_start"] = record["resource_monitor"]["sample_count"]
                natural_drain["wall_timeout_seconds_remaining"] = max(0.0, deadline - time.monotonic())
                natural_drain_started = time.monotonic()

                def sample_drain_resources():
                    nonlocal last_sample
                    monitor = record["resource_monitor"]
                    now = time.monotonic()
                    if last_sample is not None and now - last_sample > max_sample_gap_seconds:
                        gap = now - last_sample
                        monitor["maximum_sample_gap_seconds"] = max(
                            monitor["maximum_sample_gap_seconds"], gap)
                        monitor["failure"] = (
                            f"自然排空资源采样间隔{gap:.3f}s超过"
                            f"{max_sample_gap_seconds:.3f}s上限")
                        raise _DrainWaitFailure("FAIL_RESOURCE_SAMPLE_GAP", monitor["failure"])
                    if last_sample is not None and now - last_sample < sample_interval_seconds:
                        return
                    try:
                        available, total = _validated_memory_sample(memory_reader)
                    except Exception as error:
                        monitor["failure"] = f"{type(error).__name__}: {error}"
                        raise _DrainWaitFailure("FAIL_RESOURCE_QUERY", monitor["failure"]) from error
                    sample_end = time.monotonic()
                    gap = sample_end - last_sample if last_sample is not None else 0.0
                    monitor["maximum_sample_gap_seconds"] = max(
                        monitor["maximum_sample_gap_seconds"], gap)
                    if last_sample is not None and gap > max_sample_gap_seconds:
                        monitor["failure"] = (
                            f"自然排空资源采样间隔{gap:.3f}s超过"
                            f"{max_sample_gap_seconds:.3f}s上限")
                        raise _DrainWaitFailure("FAIL_RESOURCE_SAMPLE_GAP", monitor["failure"])
                    last_sample = sample_end
                    monitor["sample_count"] += 1
                    monitor["last_sample_monotonic"] = sample_end
                    monitor["total_ram_bytes"] = total
                    prior_minimum = monitor["minimum_available_ram_bytes"]
                    monitor["minimum_available_ram_bytes"] = (
                        available if prior_minimum is None else min(prior_minimum, available))
                    if available < stop_floor_bytes:
                        monitor["failure"] = f"可用物理内存低于{stop_floor_bytes}字节停止线"
                        raise _DrainWaitFailure("FAIL_RESOURCE_STOP", monitor["failure"])

                try:
                    proof = _wait_for_empty_job(
                        job, root_process, drain_timeout_seconds,
                        allow_root_exit_drain=True,
                        overall_deadline=deadline,
                        poll_callback=sample_drain_resources,
                        drain_record=natural_drain,
                    )
                    record["cleanup"]["empty_job_proof"] = proof
                except _DrainWaitFailure as error:
                    record["cleanup"]["natural_drain_failure"] = f"{type(error).__name__}: {error}"
                    natural_drain["status"] = error.status
                    natural_drain["error"] = str(error)
                    natural_drain["elapsed_seconds"] = round(time.monotonic() - natural_drain_started, 3)
                    if error.status == "FAIL_TIMEOUT":
                        record["timed_out"] = True
                    primary_failure = error.status
                except Exception as error:
                    record["cleanup"]["natural_drain_failure"] = f"{type(error).__name__}: {error}"
                    natural_drain["status"] = "FAIL_JOB_NOT_EMPTY"
                    natural_drain["error"] = f"{type(error).__name__}: {error}"
                    natural_drain["elapsed_seconds"] = round(time.monotonic() - natural_drain_started, 3)
                    primary_failure = "FAIL_JOB_NOT_EMPTY"
                finally:
                    natural_drain["resource_samples_at_end"] = record["resource_monitor"]["sample_count"]

        if primary_failure is not None and job is not None and not job.closed:
            record["cleanup"]["termination_requested"] = True
            record["cleanup"]["termination_exit_code"] = 91
            try:
                job.terminate_own_job(91)
            except Exception as error:
                record["cleanup"]["errors"].append(f"TerminateJobObject(own Job)失败：{type(error).__name__}: {error}")
            if root_process is not None:
                try:
                    if job_guard._api_wait(root_process.process_handle, 0) == job_guard.WAIT_OBJECT_0:
                        record["exit_code"] = job_guard._api_get_exit_code(root_process.process_handle)
                except Exception as error:
                    record["cleanup"]["errors"].append(f"root退出码收尾读回失败：{type(error).__name__}: {error}")
            try:
                proof = _wait_for_empty_job(job, root_process, drain_timeout_seconds)
                record["cleanup"]["empty_job_proof"] = proof
            except Exception as error:
                record["cleanup"]["errors"].append(f"终止后Job清空核验失败：{type(error).__name__}: {error}")

        if job is not None:
            try:
                _close_owned_handles(job, root_process)
            except Exception as error:
                record["cleanup"]["errors"].append(f"{type(error).__name__}: {error}")
            record["cleanup"]["job_closed"] = bool(job.closed)
            if root_process is not None:
                record["cleanup"]["root_process_handle_closed"] = not bool(root_process.process_info.hProcess)
                record["cleanup"]["root_thread_handle_closed"] = not bool(root_process.process_info.hThread)

        proof = record["cleanup"]["empty_job_proof"]
        handles_closed = (
            job is not None and job.closed
            and (root_process is None or (
                record["cleanup"]["root_process_handle_closed"]
                and record["cleanup"]["root_thread_handle_closed"]
            ))
        )
        record["cleanup_confirmed"] = bool(proof is not None and handles_closed and not record["cleanup"]["errors"])
        record["cleanup"]["confirmed"] = record["cleanup_confirmed"]
        if not record["cleanup_confirmed"] and primary_failure is None:
            primary_failure = "FAIL_CLEANUP_UNCONFIRMED"
        if primary_failure is not None:
            if primary_failure == "FAIL_TIMEOUT" and not record["cleanup_confirmed"]:
                record["status"] = "FAIL_TIMEOUT_CLEANUP_UNCONFIRMED"
            else:
                record["status"] = primary_failure
        elif record["exit_code"] == 0 and record["cleanup_confirmed"]:
            record["status"] = "PASS"
        else:
            record["status"] = "FAIL_EXIT"
        try:
            _checkpoint(checkpoint_callback, {
                "event": "finished",
                "message": record["status"],
                "process_id": record["process_id"],
                "elapsed_seconds": time.monotonic() - started,
                "exit_code": record["exit_code"],
                "cleanup_confirmed": record["cleanup_confirmed"],
            })
        except Exception as error:
            record["status"] = "FAIL_FINAL_CHECKPOINT"
            record["error"] = f"{type(error).__name__}: {error}"
        return record
    except Exception as error:
        if record["status"] in ("RUNNING", "PASS"):
            record["status"] = "FAIL_SUPERVISOR_EXCEPTION"
        record["error"] = f"{type(error).__name__}: {error}"
        if job is not None and not job.closed:
            try:
                record["cleanup"]["termination_requested"] = True
                record["cleanup"]["termination_exit_code"] = 91
                job.terminate_own_job(91)
                proof = _wait_for_empty_job(job, root_process, drain_timeout_seconds)
                record["cleanup"]["empty_job_proof"] = proof
            except Exception as cleanup_error:
                record["cleanup"]["errors"].append(f"异常后Job收尾失败：{type(cleanup_error).__name__}: {cleanup_error}")
            try:
                _close_owned_handles(job, root_process)
            except Exception as cleanup_error:
                record["cleanup"]["errors"].append(f"异常后句柄关闭失败：{type(cleanup_error).__name__}: {cleanup_error}")
            record["cleanup"]["job_closed"] = bool(job.closed)
            if root_process is not None:
                record["cleanup"]["root_process_handle_closed"] = not bool(root_process.process_info.hProcess)
                record["cleanup"]["root_thread_handle_closed"] = not bool(root_process.process_info.hThread)
            proof = record["cleanup"]["empty_job_proof"]
            record["cleanup_confirmed"] = bool(
                proof is not None and job.closed and not record["cleanup"]["errors"]
                and (root_process is None or (
                    record["cleanup"]["root_process_handle_closed"]
                    and record["cleanup"]["root_thread_handle_closed"]
                ))
            )
            record["cleanup"]["confirmed"] = record["cleanup_confirmed"]
        return record
    finally:
        for handle, inheritable in original_inheritable.items():
            try:
                os.set_handle_inheritable(handle, inheritable)
            except OSError:
                pass
        if owned_null_stream is not None:
            owned_null_stream.close()
        if owned_stderr_fd is not None:
            os.close(owned_stderr_fd)
        record["seconds"] = round(time.monotonic() - started, 3)
        record["finished_at"] = datetime.now().astimezone().isoformat(timespec="milliseconds")
