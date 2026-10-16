#!/usr/bin/env python3
"""在两个独立的自有Job中管理离线Vitis server与构建。"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import msvcrt
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "verification"
sys.path.insert(0, str(VERIFICATION))
import s15_job_guard as job_guard
from s2b_process_supervisor import GIB, _close_owned_handles, _wait_for_empty_job, supervise_process


SCHEMA_VERSION = 1
MANAGED_PORT_ENV = "S2B_MANAGED_VITIS_PORT"
STOP_FLOOR_BYTES = 2 * GIB
SAMPLE_INTERVAL_SECONDS = 0.25
MAX_SAMPLE_GAP_SECONDS = 1.0
SERVER_STARTUP_TIMEOUT_SECONDS = 90.0
SERVER_DRAIN_TIMEOUT_SECONDS = 10.0
SERVER_CLIENT_PROBE_TIMEOUT_SECONDS = 120.0


class ManagedVitisError(RuntimeError):
    """受控server启动、归属或清理失败。"""


class MIB_TCPROW_OWNER_PID(ctypes.Structure):
    _fields_ = [
        ("dwState", ctypes.c_ulong),
        ("dwLocalAddr", ctypes.c_ulong),
        ("dwLocalPort", ctypes.c_ulong),
        ("dwRemoteAddr", ctypes.c_ulong),
        ("dwRemotePort", ctypes.c_ulong),
        ("dwOwningPid", ctypes.c_ulong),
    ]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def snapshot_sources(run_dir: Path, source_rows: list[Path]) -> dict:
    """为新Run独占保存本次执行的四个项目源码快照。"""
    snapshot_root = run_dir / "source_snapshot"
    snapshot_root.mkdir(exist_ok=False)
    result = {}
    for source in source_rows:
        relative = source.relative_to(ROOT)
        target = snapshot_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        with target.open("xb") as stream:
            stream.write(data)
        digest = hashlib.sha256(data).hexdigest()
        result[relative.as_posix()] = {"path": str(target), "sha256": digest}
    return result


def read_tcp_listener_pids(port: int) -> list[int]:
    """读回本机IPv4监听端口的PID，后续必须全部属于本次server Job。"""
    iphlpapi = ctypes.WinDLL("iphlpapi", use_last_error=True)
    get_table = iphlpapi.GetExtendedTcpTable
    get_table.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_ulong,
    ]
    get_table.restype = ctypes.c_ulong
    size = ctypes.c_ulong(0)
    table_owner_pid_all = 5
    af_inet = 2
    result = get_table(None, ctypes.byref(size), 1, af_inet, table_owner_pid_all, 0)
    if result not in (0, 122) or size.value < ctypes.sizeof(ctypes.c_ulong):
        raise ManagedVitisError(f"GetExtendedTcpTable尺寸查询失败：{result}, size={size.value}")
    buffer = ctypes.create_string_buffer(size.value)
    result = get_table(buffer, ctypes.byref(size), 1, af_inet, table_owner_pid_all, 0)
    if result != 0:
        raise ManagedVitisError(f"GetExtendedTcpTable读回失败：{result}")
    count = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ulong)).contents.value
    row_size = ctypes.sizeof(MIB_TCPROW_OWNER_PID)
    if count > (size.value - ctypes.sizeof(ctypes.c_ulong)) // row_size:
        raise ManagedVitisError("TCP表行数超过返回缓冲区")
    rows = ctypes.cast(
        ctypes.addressof(buffer) + ctypes.sizeof(ctypes.c_ulong),
        ctypes.POINTER(MIB_TCPROW_OWNER_PID),
    )
    listening_state = 2
    pids = []
    for index in range(count):
        row = rows[index]
        local_port = socket.ntohs(int(row.dwLocalPort) & 0xFFFF)
        if row.dwState == listening_state and local_port == port:
            pids.append(int(row.dwOwningPid))
    return sorted(set(pids))


def choose_free_port() -> int:
    """从系统分配的临时端口中取值，并在启动前核验无人监听。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = int(probe.getsockname()[1])
    if read_tcp_listener_pids(port):
        raise ManagedVitisError(f"新分配端口已有监听者：{port}")
    return port


def _memory_sample() -> tuple[int, int]:
    available, total = job_guard._memory_status()
    if type(available) is not int or type(total) is not int or not 0 <= available <= total:
        raise ManagedVitisError("GlobalMemoryStatusEx返回无效内存值")
    return available, total


def _open_child_handles(log_path: Path):
    null_stream = log_stream = None
    stderr_fd = None
    changed = {}
    try:
        null_stream = open(os.devnull, "rb")
        log_stream = log_path.open("xb")
        stderr_fd = os.dup(log_stream.fileno())
        handles = [
            int(msvcrt.get_osfhandle(null_stream.fileno())),
            int(msvcrt.get_osfhandle(log_stream.fileno())),
            int(msvcrt.get_osfhandle(stderr_fd)),
        ]
        for handle in set(handles):
            inheritable = os.get_handle_inheritable(handle)
            changed[handle] = inheritable
            if not inheritable:
                os.set_handle_inheritable(handle, True)
        return null_stream, log_stream, stderr_fd, handles, changed
    except BaseException:
        try:
            _restore_child_handles(changed)
        except BaseException:
            pass
        for closer in (
            (lambda: os.close(stderr_fd)) if stderr_fd is not None else None,
            log_stream.close if log_stream is not None else None,
            null_stream.close if null_stream is not None else None,
        ):
            if closer is not None:
                try:
                    closer()
                except BaseException:
                    pass
        raise


def _restore_child_handles(changed: dict[int, bool]) -> None:
    for handle, was_inheritable in changed.items():
        if not was_inheritable:
            os.set_handle_inheritable(handle, False)


def _close_child_handles(null_stream, log_stream, stderr_fd) -> None:
    errors = []
    for label, closer in (
        ("server stderr fd", lambda: os.close(stderr_fd)),
        ("server log", log_stream.close),
        ("server stdin", null_stream.close),
    ):
        try:
            closer()
        except BaseException as error:
            errors.append(f"{label}: {error!r}")
    if errors:
        raise ManagedVitisError("server日志句柄关闭失败：" + "; ".join(errors))


def _terminate_job_and_prove_empty(job, root_process, record: dict) -> dict:
    """只终止本Run server Job，并复用supervisor的稳定空Job证明。"""
    record["termination"]["requested"] = True
    primary = None
    try:
        job.terminate_own_job(93)
        proof = _wait_for_empty_job(
            job,
            root_process,
            SERVER_DRAIN_TIMEOUT_SECONDS,
            allow_root_exit_drain=True,
            drain_record=record["termination"].setdefault("drain", {}),
        )
        record["termination"]["empty_job_proof"] = proof
        _close_owned_handles(job, root_process)
        record["termination"]["job_closed"] = job.closed
        record["termination"]["root_handles_closed"] = root_process.closed
        if not job.closed or not root_process.closed:
            raise ManagedVitisError("supervisor空Job证明后Job或root HANDLE未闭合")
        return proof
    except BaseException as error:
        primary = error
        try:
            _close_owned_handles(job, root_process)
            record["termination"]["kill_on_close_fallback"] = True
            record["termination"]["job_closed"] = job.closed
            record["termination"]["root_handles_closed"] = root_process.closed
        except BaseException as cleanup_error:
            record["termination"]["fallback_close_error"] = repr(cleanup_error)
        record["termination"]["error"] = repr(primary)
        raise primary


def _job_snapshot(job) -> dict:
    before = tuple(job.pid_list())
    accounting_before = job.accounting()
    after = tuple(job.pid_list())
    accounting_after = job.accounting()
    if before != after or accounting_before["active_processes"] != accounting_after["active_processes"]:
        raise ManagedVitisError("server Job采样期间成员集合变化")
    if accounting_after["active_processes"] != len(after):
        raise ManagedVitisError("server Job PID列表与active_processes不符")
    return {"pids": list(after), "accounting": accounting_after}


def _start_owned_server(vitis_bat: Path, port: int, run_dir: Path, record: dict):
    server_bat = vitis_bat.parent / "vitis-server.bat"
    if not server_bat.is_file():
        raise ManagedVitisError(f"Vitis server启动器精确路径不存在：{server_bat}")
    cmd = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
    if not cmd.is_file():
        raise ManagedVitisError(f"cmd.exe精确路径不存在：{cmd}")
    environment = dict(os.environ)
    environment["XILINX_VITIS"] = str(vitis_bat.parent.parent)
    command = [str(cmd), "/d", "/c", "call", str(server_bat), "-p", str(port)]
    record["server"] = {
        "path": str(server_bat),
        "sha256": sha256(server_bat),
        "command": command,
        "port": port,
        "host": "127.0.0.1",
        "status": "STARTING",
        "job": {"created": False, "pid": None, "job_pids": [], "accounting": None},
        "startup_timeout_seconds": SERVER_STARTUP_TIMEOUT_SECONDS,
        "sample_interval_seconds": SAMPLE_INTERVAL_SECONDS,
        "stop_floor_bytes": STOP_FLOOR_BYTES,
        "samples": [],
        "termination": {"kind": "OWN_SERVER_JOB_TERMINATE", "requested": False, "empty_job_proof": None},
    }
    job = job_guard.JobObject(kill_on_close=True)
    record["server"]["job"]["created"] = True
    null_stream = log_stream = None
    stderr_fd = None
    changed = {}
    root_process = None
    succeeded = False
    try:
        null_stream, log_stream, stderr_fd, std_handles, changed = _open_child_handles(run_dir / "vitis-server.stdout.log")
        root_process = job_guard.launch_suspended_root(
            job,
            str(cmd),
            command,
            cwd=str(vitis_bat.parent.parent),
            std_handles=std_handles,
            environment=environment,
        )
        _restore_child_handles(changed)
        changed.clear()
        record["server"]["job"].update(pid=root_process.pid, birth_ticks=root_process.birth_ticks)
        deadline = time.monotonic() + SERVER_STARTUP_TIMEOUT_SECONDS
        previous_sample_start = None
        minimum_available = None
        while time.monotonic() < deadline:
            sample_start = time.monotonic()
            if previous_sample_start is not None:
                gap = sample_start - previous_sample_start
                record["server"].setdefault("maximum_sample_gap_seconds", 0.0)
                record["server"]["maximum_sample_gap_seconds"] = max(record["server"]["maximum_sample_gap_seconds"], gap)
                if gap > MAX_SAMPLE_GAP_SECONDS:
                    raise ManagedVitisError(f"server资源采样间隔超限：{gap:.3f}s")
            previous_sample_start = sample_start
            available, total = _memory_sample()
            minimum_available = available if minimum_available is None else min(minimum_available, available)
            snapshot = _job_snapshot(job)
            sample = {
                "monotonic_seconds": sample_start,
                "available_ram_bytes": available,
                "total_ram_bytes": total,
                **snapshot,
            }
            record["server"]["samples"].append(sample)
            record["server"].update(
                sample_count=len(record["server"]["samples"]),
                minimum_available_ram_bytes=minimum_available,
            )
            if available < STOP_FLOOR_BYTES:
                raise ManagedVitisError(f"server启动期间可用内存低于2GiB停止线：{available}")
            if not snapshot["pids"] or snapshot["accounting"]["active_processes"] <= 0:
                raise ManagedVitisError("server启动Job意外清空")
            owner_pids = read_tcp_listener_pids(port)
            if owner_pids:
                job_pids = set(snapshot["pids"])
                if not set(owner_pids) <= job_pids:
                    raise ManagedVitisError(f"选定端口监听者不全属于本次server Job：owners={owner_pids}, job={sorted(job_pids)}")
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    pass
                record["server"].update(status="READY", listener_owner_pids=owner_pids)
                record["server"]["job"].update(job_pids=snapshot["pids"], accounting=snapshot["accounting"])
                succeeded = True
                return job, root_process, null_stream, log_stream, stderr_fd
            if job_guard._api_wait(root_process.process_handle, 0) == job_guard.WAIT_OBJECT_0:
                raise ManagedVitisError("server launcher在监听端口ready前退出")
            time.sleep(SAMPLE_INTERVAL_SECONDS)
        raise ManagedVitisError("server在有限启动期限内未建立自有Job监听端口")
    except BaseException as primary:
        cleanup_error = None
        if changed:
            try:
                _restore_child_handles(changed)
            except BaseException as error:
                cleanup_error = error
        if root_process is not None and not job.closed:
            try:
                _terminate_job_and_prove_empty(job, root_process, record["server"])
            except BaseException as error:
                cleanup_error = error if cleanup_error is None else ManagedVitisError(f"{cleanup_error!r}; {error!r}")
        elif not job.closed:
            try:
                job.close()
            except BaseException as error:
                cleanup_error = error if cleanup_error is None else ManagedVitisError(f"{cleanup_error!r}; {error!r}")
        if cleanup_error is not None:
            record["server"]["startup_cleanup_error"] = repr(cleanup_error)
            record["server"]["status"] = "FAIL_STARTUP_CLEANUP"
            raise ManagedVitisError(f"server启动失败且清理未完整闭合：primary={primary!r}; cleanup={cleanup_error!r}") from primary
        record["server"]["status"] = "CLOSED_AFTER_START_FAILURE"
        raise
    finally:
        if null_stream is not None and not succeeded:
            _close_child_handles(null_stream, log_stream, stderr_fd)


def _stop_owned_server(job, root_process, null_stream, log_stream, stderr_fd, record: dict) -> None:
    if job is None or job.closed:
        return
    primary = None
    try:
        _terminate_job_and_prove_empty(job, root_process, record["server"])
        record["server"]["status"] = "CLOSED_BY_OWN_JOB_TERMINATION"
    except BaseException as error:
        primary = error
    try:
        _close_child_handles(null_stream, log_stream, stderr_fd)
    except BaseException as error:
        if primary is None:
            primary = error
        else:
            record["server"]["termination"]["log_handle_close_error"] = repr(error)
    if primary is not None:
        raise primary


def _managed_probe_source() -> str:
    """构造固定SDK版本的真实client连接、fallback屏蔽与关闭脚本。"""
    return """import hashlib
import json
import os
import sys

import vitis
from vitis import _server

expected_sdk_sha = "2dc671f21afcaefa3223c125c5a1cdcdbebdd9fda4360b4e38bd99c92214e368"
result_path = os.environ["S2B_MANAGED_VITIS_PROBE_RESULT"]
record = {"status": "FAIL", "mode": "OWN_SERVER_JOB", "port": int(os.environ["S2B_MANAGED_VITIS_PORT"]), "connect_called": False, "connected": False, "client_close_called": False, "dispose_called": False, "channel_closed": False, "sdk_owned_server_pid": None}
client = None
server_class = _server.Server
original_channel = server_class.channel
original_start_server = server_class.startServer
preconnected_channel = None
shim_installed = False
try:
    sdk_source_sha = hashlib.sha256(open(_server.__file__, "rb").read()).hexdigest()
    record["sdk_server_source"] = _server.__file__
    record["sdk_server_source_sha256"] = sdk_source_sha
    if sdk_source_sha != expected_sdk_sha or original_channel is not None or len(server_class._instances) != 0:
        raise RuntimeError("Vitis SDK源码或server singleton状态不满足受控shim前提")
    preconnected_channel = _server.grpc.insecure_channel("127.0.0.1:" + str(record["port"]))
    _server.grpc.channel_ready_future(preconnected_channel).result(10)
    server_class.channel = preconnected_channel
    def reject_sdk_server_start(instance):
        raise RuntimeError("managed server连接断开，禁止SDK创建非本Run server")
    server_class.startServer = reject_sdk_server_start
    shim_installed = True
    client = vitis.create_client(port=record["port"], host="127.0.0.1", workspace=os.environ["S2B_MANAGED_VITIS_WORKSPACE"])
    record["connect_called"] = True
    server = client._serverObj
    record["connected"] = server.verify() is True and server.serverPort == record["port"] and server.host == "127.0.0.1"
    record["sdk_owned_server_pid"] = None if server.cp is None else server.cp.pid
    if not record["connected"] or server.cp is not None:
        raise RuntimeError("连接未落到本Run外部server")
finally:
    if shim_installed:
        server_class.channel = original_channel
        server_class.startServer = original_start_server
    if preconnected_channel is not None:
        preconnected_channel.close()
    if client is not None:
        try:
            record["channel_closed"] = client.close() is True
            record["client_close_called"] = True
        except BaseException as error:
            record["client_close_error"] = repr(error)
    try:
        vitis.dispose()
        record["dispose_called"] = True
    except BaseException as error:
        record["dispose_error"] = repr(error)
    record["status"] = "PASS_SERVER_CLIENT_DISPOSE" if record["connected"] and record["client_close_called"] and record["dispose_called"] and record["channel_closed"] and record["sdk_owned_server_pid"] is None else "FAIL"
    with open(result_path, "x", encoding="utf-8", newline="\\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\\n")
if record["status"] != "PASS_SERVER_CLIENT_DISPOSE":
    sys.exit(1)
"""


def _run_connection_probe(vitis_bat: Path, port: int, run_dir: Path, record: dict) -> dict:
    """用真实Vitis Python完成公开端口连接、dispose与channel关闭探针。"""
    temp_parent = ROOT / "tmp" / "2B" / "S2B-T15"
    if not temp_parent.is_dir():
        raise ManagedVitisError(f"Vitis probe临时父目录不存在：{temp_parent}")
    workspace = temp_parent / f"{run_dir.name}_managed_vitis_probe"
    if workspace.exists():
        raise ManagedVitisError(f"拒绝复用已有probe workspace：{workspace}")
    probe_path = run_dir / "managed_vitis_connection_probe.py"
    result_path = run_dir / "managed_vitis_connection_probe.json"
    wrapper_path = run_dir / "managed_vitis_connection_probe.cmd"
    log_path = run_dir / "vitis-probe.stdout.log"
    if any(path.exists() for path in (probe_path, result_path, wrapper_path, log_path)):
        raise ManagedVitisError("probe输出文件已经存在")
    probe_source = _managed_probe_source()
    with probe_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(probe_source)
    cmd_text = '@echo off\r\ncall "' + str(vitis_bat) + '" -s "' + str(probe_path) + '"\r\nexit /b %errorlevel%\r\n'
    with wrapper_path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(cmd_text)
    environment = dict(os.environ)
    environment[MANAGED_PORT_ENV] = str(port)
    environment["S2B_MANAGED_VITIS_PROBE_RESULT"] = str(result_path)
    environment["S2B_MANAGED_VITIS_WORKSPACE"] = str(workspace)
    cmd = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
    with log_path.open("xb") as output_stream:
        job = supervise_process(
            name="vitis_managed_server_client_probe",
            command=[str(cmd), "/d", "/c", str(wrapper_path)],
            cwd=str(ROOT),
            environment=environment,
            output_stream=output_stream,
            timeout_seconds=SERVER_CLIENT_PROBE_TIMEOUT_SECONDS,
            sample_interval_seconds=SAMPLE_INTERVAL_SECONDS,
            max_sample_gap_seconds=MAX_SAMPLE_GAP_SECONDS,
            start_floor_bytes=STOP_FLOOR_BYTES,
            stop_floor_bytes=STOP_FLOOR_BYTES,
        )
    record["connection_probe"] = {
        "script": str(probe_path),
        "script_sha256": sha256(probe_path),
        "result_path": str(result_path),
        "workspace": str(workspace),
        "job": job,
        "timeout_seconds": SERVER_CLIENT_PROBE_TIMEOUT_SECONDS,
        "status": "RUNNING",
    }
    if job.get("status") != "PASS" or job.get("exit_code") != 0 or not job.get("cleanup_confirmed"):
        raise ManagedVitisError(f"真实Vitis client probe Job未PASS：{job.get('status')}")
    if not result_path.is_file():
        raise ManagedVitisError("真实Vitis client probe没有写结果文件")
    probe_result = json.loads(result_path.read_text(encoding="utf-8"))
    record["connection_probe"]["result"] = probe_result
    record["connection_probe"]["status"] = probe_result.get("status")
    if probe_result.get("status") != "PASS_SERVER_CLIENT_DISPOSE":
        raise ManagedVitisError(f"真实Vitis client probe状态不通过：{probe_result}")
    return probe_result


def run(run_dir: Path, vitis_bat: Path, timeout_seconds: float = 600.0, probe_only: bool = False) -> dict:
    if os.name != "nt":
        raise ManagedVitisError("受控Vitis生命周期只支持Windows")
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0 or timeout_seconds > 600.0:
        raise ManagedVitisError("Vitis构建wall timeout必须是(0, 600]秒有限值")
    run_dir = run_dir.resolve(strict=True)
    if not run_dir.is_dir() or not run_dir.is_relative_to(ROOT / "report" / "evidence" / "S2B-T15"):
        raise ManagedVitisError("Run目录必须是report/evidence/S2B-T15下已存在的独立目录")
    config_path = run_dir / "config.json"
    if not config_path.is_file():
        raise ManagedVitisError("Run目录缺少config.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    artifact_dir = Path(config.get("artifact_dir", "")).resolve(strict=False)
    if not artifact_dir.is_relative_to(ROOT / "report" / "evidence" / "S2B-T15"):
        raise ManagedVitisError("配置中的artifact_dir超出S2B-T15证据目录")
    if not vitis_bat.is_file() or vitis_bat.name.lower() != "vitis.bat":
        raise ManagedVitisError("必须提供精确存在的vitis.bat文件路径")
    vitis_bat = vitis_bat.resolve(strict=True)
    build_script = ROOT / "vitis" / "build_s2b_inference.py"
    guard_script = VERIFICATION / "s15_job_guard.py"
    supervisor_script = VERIFICATION / "s2b_process_supervisor.py"
    helper_script = Path(__file__).resolve(strict=True)
    source_rows = [build_script, guard_script, supervisor_script, helper_script]
    source_hashes = {str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path) for path in source_rows}
    preflight_paths = [run_dir / "launcher_record.json", run_dir / "launcher_record.tmp",
                       run_dir / "source_snapshot", run_dir / "vitis.stdout.log",
                       run_dir / "vitis-server.stdout.log", run_dir / "build.cmd"]
    if probe_only:
        preflight_paths.extend((run_dir / "managed_vitis_connection_probe.py",
                                run_dir / "managed_vitis_connection_probe.json",
                                run_dir / "managed_vitis_connection_probe.cmd",
                                run_dir / "vitis-probe.stdout.log"))
    existing = [str(path) for path in preflight_paths if path.exists()]
    if existing:
        raise ManagedVitisError(f"拒绝复用已有Run输出路径：{existing}")
    source_snapshots = snapshot_sources(run_dir, source_rows)
    if {name: row["sha256"] for name, row in source_snapshots.items()} != source_hashes:
        raise ManagedVitisError("Run源码快照与启动时源码哈希不一致")
    started_monotonic = time.monotonic()
    record = {
        "schema_version": SCHEMA_VERSION,
        "status": "RUNNING",
        "hardware_execution": "NOT_RUN",
        "run_directory": str(run_dir),
        "config_path": str(config_path),
        "config_sha256": sha256(config_path),
        "vitis_launcher": {"path": str(vitis_bat), "sha256": sha256(vitis_bat)},
        "sources": source_hashes,
        "source_snapshots": source_snapshots,
        "server": None,
        "build_job": None,
        "started_at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "timeout_seconds": timeout_seconds,
        "probe_only": probe_only,
        "limitations": [
            "外部Vitis server在客户端dispose后由本Run专属Job强制终止；没有shutdown RPC，不代表优雅协议关闭。",
            "本流程只执行离线候选构建，不访问板卡。",
        ],
    }
    record_path = run_dir / "launcher_record.json"
    record_temp_path = run_dir / "launcher_record.tmp"
    if record_path.exists() or record_temp_path.exists():
        raise ManagedVitisError("拒绝覆盖已有launcher记录或临时记录")

    def persist_record() -> None:
        with record_temp_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(record_temp_path, record_path)

    write_json(record_path, record)
    server_job = server_root = server_null = server_log = server_stderr = None
    primary_error = None
    try:
        output_paths = [run_dir / "vitis.stdout.log", run_dir / "vitis-server.stdout.log", run_dir / "build.cmd"]
        if probe_only:
            output_paths.extend((
                run_dir / "managed_vitis_connection_probe.py",
                run_dir / "managed_vitis_connection_probe.json",
                run_dir / "managed_vitis_connection_probe.cmd",
                run_dir / "vitis-probe.stdout.log",
            ))
        for path in output_paths:
            if path.exists():
                raise ManagedVitisError(f"拒绝覆盖已有Run文件：{path}")
        port = choose_free_port()
        record["managed_connection"] = {"mode": "OWN_SERVER_JOB", "host": "127.0.0.1", "port": port, "port_environment": MANAGED_PORT_ENV}
        server_job, server_root, server_null, server_log, server_stderr = _start_owned_server(
            vitis_bat, port, run_dir, record)
        persist_record()
        if probe_only:
            _run_connection_probe(vitis_bat, port, run_dir, record)
            record["status"] = "PASS_MANAGED_VITIS_LIFECYCLE_PROBE_ONLY"
            return record
        environment = dict(os.environ)
        environment["S2B_INFERENCE_CONFIG"] = str(config_path)
        environment[MANAGED_PORT_ENV] = str(port)
        vitis_cmd = '@echo off\r\ncall "' + str(vitis_bat) + '" -s "' + str(build_script) + '"\r\nexit /b %errorlevel%\r\n'
        with (run_dir / "build.cmd").open("x", encoding="utf-8", newline="") as stream:
            stream.write(vitis_cmd)
        cmd = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
        with (run_dir / "vitis.stdout.log").open("xb") as output_stream:
            build_job = supervise_process(
                name="vitis_candidate_build_managed_server",
                command=[str(cmd), "/d", "/c", str(run_dir / "build.cmd")],
                cwd=str(ROOT),
                environment=environment,
                output_stream=output_stream,
                timeout_seconds=timeout_seconds,
                sample_interval_seconds=SAMPLE_INTERVAL_SECONDS,
                max_sample_gap_seconds=MAX_SAMPLE_GAP_SECONDS,
                start_floor_bytes=int(4.5 * GIB),
                stop_floor_bytes=STOP_FLOOR_BYTES,
            )
        record["build_job"] = build_job
        if not (build_job.get("status") == "PASS" and build_job.get("exit_code") == 0
                and not build_job.get("timed_out") and build_job.get("cleanup_confirmed")):
            raise ManagedVitisError(f"Vitis build Job未自然排空或返回非零：{build_job.get('status')}")
        details_path = artifact_dir / "build_details.json"
        if not details_path.is_file():
            raise ManagedVitisError("构建结束但缺少build_details.json")
        details = json.loads(details_path.read_text(encoding="utf-8"))
        if details.get("status") not in {"PASS_OFFLINE_FULL_XSA_BUILD", "PASS_UNIT_ONLY_PS_XSA_BUILD"}:
            raise ManagedVitisError(f"builder内部状态未通过：{details.get('status')}")
        if details.get("vitis_connection", {}).get("port") != port:
            raise ManagedVitisError("build_details未绑定本Run自有server端口")
        if details.get("vitis_connection", {}).get("mode") != "OWN_SERVER_JOB":
            raise ManagedVitisError("build_details未声明受控server连接模式")
        if details.get("own_server_cleanup") != "DISPOSE_CALLED":
            raise ManagedVitisError("builder未记录vitis.dispose调用")
        if details.get("managed_channel_closed") is not True:
            raise ManagedVitisError("builder未确认公开client.close关闭channel")
        if details.get("hardware_execution") != "NOT_RUN":
            raise ManagedVitisError("离线构建声明意外包含实板执行")
        for relative, expected in source_hashes.items():
            if sha256(ROOT / relative) != expected:
                raise ManagedVitisError(f"运行期间源码变化：{relative}")
        record["status"] = "PASS_OFFLINE_CANDIDATE_BUILD_ONLY"
    except BaseException as error:
        primary_error = error
        record["status"] = "FAIL"
        record["error"] = f"{type(error).__name__}: {error}"
    finally:
        if server_job is not None:
            try:
                _stop_owned_server(server_job, server_root, server_null, server_log, server_stderr, record)
            except BaseException as error:
                record["status"] = "FAIL"
                record["server_cleanup_error"] = f"{type(error).__name__}: {error}"
        record["finished_at"] = datetime.now().astimezone().isoformat(timespec="milliseconds")
        record["elapsed_seconds"] = time.monotonic() - started_monotonic
        persist_record()
    if primary_error is not None:
        raise primary_error
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--vitis-bat", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args(argv)
    result = run(args.run_dir, args.vitis_bat, args.timeout_seconds, args.probe_only)
    print(json.dumps({"status": result["status"], "run_directory": result["run_directory"]}, ensure_ascii=False))
    return 0 if result["status"] in {"PASS_OFFLINE_CANDIDATE_BUILD_ONLY", "PASS_MANAGED_VITIS_LIFECYCLE_PROBE_ONLY"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
