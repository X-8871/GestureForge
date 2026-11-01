"""验证M3执行租约、监听端口与本轮Windows Job的进程所有权。"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import socket
import struct
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable

UTC8 = timezone(timedelta(hours=8))
LEASE_SCHEMA = "codex.m3.execution_lease.v1"
START_SCHEMA = "codex.m3.server_start.v1"
STEP_RECEIPT_SCHEMA = "codex.m3.single_step.v2"
CAPTURE_GUARD_SCHEMA = "codex.m3.capture_phase_guard.v2"
LOCAL_GATE_MEANING = "仅为本地执行门禁，不代表外部板窗授权或初始就绪核验"
STEP_MARKERS = {
    "setup": "M3_SETUP_OK_APP_NOT_RUN",
    "restore": "M3_RESTORED_FROM_ORIGINAL_SNAPSHOT",
    "event": "M3_READONLY_EVENT_OK",
    "close": "M3_CLOSE_CORES_STOPPED",
}
LEASE_KEYS = {
    "schema",
    "lease_id",
    "starts_at_utc8",
    "ends_at_utc8",
    "max_seconds",
    "run_dir",
    "authorization_file_path",
    "authorization_file_sha256",
    "context_file",
    "context_file_sha256",
    "window_id",
    "event_id",
}
START_KEYS = {
    "schema",
    "lease_id",
    "run_dir",
    "lease_file_path",
    "lease_file_sha256",
    "authorization_file_path",
    "authorization_file_sha256",
    "context_file_path",
    "context_file_sha256",
    "port",
    "port_file_sha256",
    "job_name",
    "started_utc8",
    "budget_seconds",
    "lease_end_utc8",
    "execution_gate",
    "initial_readiness",
}
JOB_NAME_RE = re.compile(r"^Local\\M3_OWNER_[0-9a-f]{32}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^m3_pair_[0-9]{8}_r([0-9]{2,})$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class GuardError(RuntimeError):
    """表示门禁输入、运行身份或进程所有权未通过。"""


@dataclass(frozen=True)
class Lease:
    """已验证的租约文件及其精确绑定输入。"""

    path: Path
    digest: str
    lease_id: str
    starts_at: datetime
    ends_at: datetime
    max_seconds: int
    run_dir: Path
    authorization_file: Path
    authorization_digest: str
    context_file: Path
    context_digest: str
    window_id: str
    event_id: str


@dataclass(frozen=True)
class Execution:
    """已验证的server启动记录和当前剩余预算。"""

    lease: Lease
    start: dict[str, Any]
    started_at: datetime
    port: int
    job_name: str
    budget_seconds: int
    port_file_digest: str


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """拒绝JSON对象中的重复键。"""
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise GuardError(f"JSON含重复字段：{key}")
        value[key] = item
    return value


def _read_json(path: Path) -> dict[str, Any]:
    """以UTF-8严格读取单个JSON对象。"""
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GuardError(f"无法读取UTF-8 JSON：{path}：{exc}") from exc
    if not isinstance(value, dict):
        raise GuardError(f"JSON顶层必须是对象：{path}")
    return value


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise GuardError(f"{label}字段不匹配；缺少={missing}，多余={extra}")


def _aware_utc8(text: Any, label: str) -> datetime:
    if not isinstance(text, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\+08:00",
        text,
    ):
        raise GuardError(f"{label}必须是秒精度的明确UTC+8时间")
    try:
        result = datetime.fromisoformat(text)
    except ValueError as exc:
        raise GuardError(f"{label}不是有效时间：{text}") from exc
    if result.tzinfo is None or result.utcoffset() != timedelta(hours=8):
        raise GuardError(f"{label}必须带UTC+8时区")
    if result.isoformat(timespec="seconds") != text:
        raise GuardError(f"{label}时间格式必须保持精确")
    return result


def _validate_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value):
        raise GuardError(f"{label}必须由安全ASCII标识符组成")
    return value


def _absolute_regular_file(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value or "/" in value:
        raise GuardError(f"{label}必须是非空精确绝对路径")
    lexical = PureWindowsPath(value)
    raw_parts = re.split(r"[\\/]", value)
    if (
        not lexical.is_absolute()
        or not re.fullmatch(r"[A-Za-z]:", lexical.drive)
        or any(part in {".", ".."} for part in lexical.parts)
        or any(part in {".", ".."} for part in raw_parts)
    ):
        raise GuardError(f"{label}必须是无相对跳转的绝对路径")
    path = Path(value)
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GuardError(f"{label}路径不存在：{value}：{exc}") from exc
    if path.is_symlink() or not path.is_file():
        raise GuardError(f"{label}必须是非符号链接普通文件：{value}")
    if str(resolved).casefold() != str(path).casefold():
        raise GuardError(f"{label}路径经过重定向或规范化：{value}")
    return path


def _relative_run_dir(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or "\\" in value:
        raise GuardError("run_dir必须使用精确的正斜杠相对路径")
    relative = PurePosixPath(value)
    parts = relative.parts
    if (
        relative.is_absolute()
        or "/".join(parts) != value
        or len(parts) != 4
        or parts[:3] != ("report", "evidence", "R03-M3")
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise GuardError("run_dir必须位于w6/report/evidence/R03-M3/<RunId>")
    match = RUN_ID_RE.fullmatch(parts[3])
    if not match or int(match.group(1)) < 3:
        raise GuardError("RunId必须是受控的新M3运行目录，不能复用准备目录r01/r02")
    root_path = root.resolve(strict=True)
    candidate = root_path.joinpath(*parts)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise GuardError(f"run_dir不存在：{value}：{exc}") from exc
    if candidate.is_symlink() or not candidate.is_dir():
        raise GuardError("run_dir必须是普通目录")
    if str(resolved).casefold() != str(candidate).casefold():
        raise GuardError("run_dir路径经过重定向或规范化")
    return candidate


def _relative_context(run_dir: Path, value: Any) -> Path:
    if not isinstance(value, str) or "\\" in value:
        raise GuardError("context_file必须使用精确的正斜杠相对路径")
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or "/".join(relative.parts) != value
        or not relative.parts
        or any(
        part in {"", ".", ".."} for part in relative.parts
        )
    ):
        raise GuardError("context_file必须是run_dir内的相对文件")
    candidate = run_dir.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise GuardError(f"context_file不存在：{value}：{exc}") from exc
    if candidate.is_symlink() or not candidate.is_file():
        raise GuardError("context_file必须是run_dir内的普通文件")
    if str(resolved).casefold() != str(candidate).casefold():
        raise GuardError("context_file路径经过重定向或规范化")
    return candidate


def load_lease(
    lease_file: str | Path,
    root: str | Path,
    *,
    now: datetime | None = None,
) -> Lease:
    """验证本地执行门禁；不解释外部授权或板卡初始就绪。"""
    raw_path = Path(lease_file)
    raw_lease_text = str(lease_file)
    lexical_lease = PureWindowsPath(raw_lease_text)
    raw_lease_parts = re.split(r"[\\/]", raw_lease_text)
    if (
        not lexical_lease.is_absolute()
        or any(part in {".", ".."} for part in lexical_lease.parts)
        or any(part in {".", ".."} for part in raw_lease_parts)
        or raw_path.is_symlink()
        or not raw_path.is_file()
    ):
        raise GuardError("--lease-file必须指向存在的精确绝对普通文件")
    try:
        resolved_lease = raw_path.resolve(strict=True)
    except OSError as exc:
        raise GuardError(f"租约文件路径无效：{exc}") from exc
    if str(resolved_lease).casefold() != str(raw_path).casefold():
        raise GuardError("--lease-file路径经过重定向或规范化")
    lease_raw = raw_path.read_bytes()
    lease_data = _read_json(raw_path)
    _require_exact_keys(lease_data, LEASE_KEYS, "租约")
    if lease_data.get("schema") != LEASE_SCHEMA:
        raise GuardError("租约schema不受支持")
    lease_id = _validate_id(lease_data.get("lease_id"), "lease_id")
    starts_at = _aware_utc8(lease_data.get("starts_at_utc8"), "starts_at_utc8")
    ends_at = _aware_utc8(lease_data.get("ends_at_utc8"), "ends_at_utc8")
    if ends_at <= starts_at:
        raise GuardError("租约结束时间必须晚于开始时间")
    duration = (ends_at - starts_at).total_seconds()
    if duration > 9 * 60:
        raise GuardError("租约总时长不得超过9分钟")
    max_seconds = lease_data.get("max_seconds")
    if type(max_seconds) is not int or not 1 <= max_seconds <= 520:
        raise GuardError("max_seconds必须是1至520的整数")
    if max_seconds > duration:
        raise GuardError("max_seconds不得超过租约总时长")
    current = now or datetime.now(UTC8)
    if current.tzinfo is None or current.utcoffset() is None:
        raise GuardError("当前检查时间必须带时区")
    current = current.astimezone(UTC8)
    if current < starts_at or current >= ends_at:
        raise GuardError("当前时间不在租约有效区间内")
    run_dir = _relative_run_dir(Path(root), lease_data.get("run_dir"))

    authorization_file = _absolute_regular_file(
        lease_data.get("authorization_file_path"), "authorization_file_path"
    )
    auth_digest = lease_data.get("authorization_file_sha256")
    if not isinstance(auth_digest, str) or not SHA256_RE.fullmatch(auth_digest):
        raise GuardError("authorization_file_sha256必须是小写SHA-256")
    actual_auth_digest = _sha256(authorization_file.read_bytes())
    if actual_auth_digest != auth_digest:
        raise GuardError("授权文件SHA-256与租约声明不一致")
    if str(authorization_file).casefold() == str(raw_path).casefold():
        raise GuardError("租约文件不能充当授权文件")

    context_file = _relative_context(run_dir, lease_data.get("context_file"))
    context_digest = lease_data.get("context_file_sha256")
    if not isinstance(context_digest, str) or not SHA256_RE.fullmatch(context_digest):
        raise GuardError("context_file_sha256必须是小写SHA-256")
    actual_context_digest = _sha256(context_file.read_bytes())
    if actual_context_digest != context_digest:
        raise GuardError("context_file的SHA-256与租约声明不一致")

    return Lease(
        path=raw_path,
        digest=_sha256(lease_raw),
        lease_id=lease_id,
        starts_at=starts_at,
        ends_at=ends_at,
        max_seconds=max_seconds,
        run_dir=run_dir,
        authorization_file=authorization_file,
        authorization_digest=auth_digest,
        context_file=context_file,
        context_digest=context_digest,
        window_id=_validate_id(lease_data.get("window_id"), "window_id"),
        event_id=_validate_id(lease_data.get("event_id"), "event_id"),
    )


def parse_port_file(path: Path) -> tuple[int, bytes, str]:
    """只接受3121或3122及可选单个换行符。"""
    if path.is_symlink() or not path.is_file():
        raise GuardError("port.txt必须是普通文件")
    raw = path.read_bytes()
    match = re.fullmatch(rb"(3121|3122)(?:\r?\n)?", raw)
    if not match:
        raise GuardError("port.txt内容必须精确为3121或3122")
    return int(match.group(1)), raw, _sha256(raw)


def assert_requested_port(run_dir: Path, requested_port: int) -> tuple[int, str]:
    """核对holder显式端口与唯一配置文件。"""
    if type(requested_port) is not int or requested_port not in {3121, 3122}:
        raise GuardError("holder --port必须是3121或3122")
    configured, _, digest = parse_port_file(run_dir / "port.txt")
    if configured != requested_port:
        raise GuardError("--port与本轮port.txt不一致，拒绝启动")
    return configured, digest


def _read_start(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise GuardError("缺少server_start.json或其不是普通文件")
    value = _read_json(path)
    _require_exact_keys(value, START_KEYS, "server_start")
    if value.get("schema") != START_SCHEMA:
        raise GuardError("server_start schema不受支持")
    return value


def load_execution(
    lease_file: str | Path,
    root: str | Path,
    *,
    now: datetime | None = None,
) -> Execution:
    """重新绑定租约、启动记录、端口配置和当前时间。"""
    lease = load_lease(lease_file, root, now=now)
    server_dir = lease.run_dir / "server"
    if server_dir.is_symlink() or not server_dir.is_dir():
        raise GuardError("server目录不存在、不是普通目录或经过符号链接")
    close_path = server_dir / "server_close.json"
    if close_path.exists() or close_path.is_symlink():
        raise GuardError("server_close.json已存在，本轮Job已关闭或正在收窗")
    start = _read_start(server_dir / "server_start.json")
    if start.get("lease_id") != lease.lease_id:
        raise GuardError("server_start租约ID不一致")
    if start.get("run_dir") != str(lease.run_dir):
        raise GuardError("server_start运行目录与租约不一致")
    if start.get("lease_file_path") != str(lease.path):
        raise GuardError("server_start租约文件路径不一致")
    if start.get("lease_file_sha256") != lease.digest:
        raise GuardError("开窗后lease-file发生变化")
    if start.get("authorization_file_path") != str(lease.authorization_file):
        raise GuardError("server_start授权文件路径不一致")
    if start.get("authorization_file_sha256") != lease.authorization_digest:
        raise GuardError("server_start授权文件摘要不一致")
    if start.get("context_file_path") != str(lease.context_file):
        raise GuardError("server_start context路径不一致")
    if start.get("context_file_sha256") != lease.context_digest:
        raise GuardError("server_start context摘要不一致")
    if start.get("execution_gate") != LOCAL_GATE_MEANING:
        raise GuardError("server_start必须明确本地门禁不代表外部授权")
    if start.get("initial_readiness") != "由总控外部核对；本工具未作声明":
        raise GuardError("server_start初始就绪声明无效")

    started_at = _aware_utc8(start.get("started_utc8"), "server_start.started_utc8")
    current = now or datetime.now(UTC8)
    current = current.astimezone(UTC8)
    if started_at < lease.starts_at or started_at >= lease.ends_at or started_at > current:
        raise GuardError("server_start时间不在租期内或晚于当前时间")
    if start.get("lease_end_utc8") != lease.ends_at.isoformat(timespec="seconds"):
        raise GuardError("server_start租期结束时间与租约不一致")
    budget = start.get("budget_seconds")
    if type(budget) is not int or not 1 <= budget <= min(520, lease.max_seconds):
        raise GuardError("server_start budget_seconds越界")
    if budget > (lease.ends_at - started_at).total_seconds():
        raise GuardError("server_start预算越过租期结束时间")
    start_port = start.get("port")
    if type(start_port) is not int or start_port not in {3121, 3122}:
        raise GuardError("server_start端口无效")
    configured_port, _, port_digest = parse_port_file(lease.run_dir / "port.txt")
    if start_port != configured_port:
        raise GuardError("port.txt与server_start端口不一致")
    if start.get("port_file_sha256") != port_digest:
        raise GuardError("开窗后port.txt或其配置摘要发生变化")
    job_name = start.get("job_name")
    if not isinstance(job_name, str) or not JOB_NAME_RE.fullmatch(job_name):
        raise GuardError("server_start job_name无效")
    return Execution(
        lease=lease,
        start=start,
        started_at=started_at,
        port=start_port,
        job_name=job_name,
        budget_seconds=budget,
        port_file_digest=port_digest,
    )


def remaining_seconds(execution: Execution, *, reserve_seconds: int, now: datetime | None = None) -> int:
    """扣除已经历时间和收尾预留后返回可用整数秒。"""
    if type(reserve_seconds) is not int or reserve_seconds < 0:
        raise GuardError("reserve_seconds必须是非负整数")
    current = now or datetime.now(UTC8)
    if current.tzinfo is None or current.utcoffset() is None:
        raise GuardError("剩余时间检查必须使用带时区时间")
    elapsed = (current.astimezone(UTC8) - execution.started_at).total_seconds()
    remaining = int(execution.budget_seconds - elapsed - reserve_seconds)
    if remaining <= 0:
        raise GuardError("剩余租期不足以执行步骤并保留收尾时间")
    return remaining


def _path_present(path: Path) -> bool:
    """把普通文件、目录、符号链接和不可访问状态都视为运行痕迹。"""
    try:
        path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise GuardError(f"无法核验阶段痕迹路径：{path}：{exc}") from exc
    return True


def _stage_artifacts(run_dir: Path, stage: str) -> tuple[Path, ...]:
    """返回阶段执行时才会产生的路径，不把冻结Tcl目录算作已执行。"""
    if stage in STEP_MARKERS:
        directory = run_dir / stage
        return directory / "step_result.json", directory / "launcher"
    if stage in {"before", "after"}:
        return run_dir / f"capture_{stage}", run_dir / f"capture_{stage}_guard.json"
    raise GuardError(f"未知协议阶段：{stage}")


def _stage_has_artifacts(run_dir: Path, stage: str) -> bool:
    return any(_path_present(path) for path in _stage_artifacts(run_dir, stage))


def _require_stage_absent(run_dir: Path, stage: str) -> None:
    if _stage_has_artifacts(run_dir, stage):
        raise GuardError(f"{stage}阶段已有输出或失败半包，拒绝继续")


def _check_receipt_identity(execution: Execution, record: dict[str, Any], stage: str) -> None:
    """确认阶段凭据来自当前租约、RunId、配置端口和命名Job。"""
    expected = {
        "lease_id": execution.lease.lease_id,
        "lease_file_path": str(execution.lease.path),
        "lease_file_sha256": execution.lease.digest,
        "run_dir": str(execution.lease.run_dir),
        "port": execution.port,
        "port_file_sha256": execution.port_file_digest,
        "job_name": execution.job_name,
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise GuardError(f"{stage}阶段凭据身份字段不匹配：{key}")
    at = _aware_utc8(record.get("at_utc8"), f"{stage}.at_utc8")
    if at < execution.started_at or at >= execution.lease.ends_at:
        raise GuardError(f"{stage}阶段凭据时间超出本轮Job租期")
    for proof_name in ("owner_precheck", "owner_postcheck"):
        proof = record.get(proof_name)
        if not isinstance(proof, dict):
            raise GuardError(f"{stage}阶段凭据缺少{proof_name}")
        if (
            proof.get("job_name") != execution.job_name
            or proof.get("loopback_connected") is not True
            or proof.get("thread_alive") is not True
        ):
            raise GuardError(f"{stage}阶段凭据的{proof_name}Job或监听状态不匹配")
        pids = proof.get("listener_owning_pids")
        job_pids_before = proof.get("job_pids_before")
        job_pids_after = proof.get("job_pids_after")
        for values in (pids, job_pids_before, job_pids_after):
            if (
                not isinstance(values, list)
                or not values
                or any(type(pid) is not int or pid <= 0 for pid in values)
            ):
                raise GuardError(f"{stage}阶段凭据的{proof_name}PID无效")
        if (
            not set(pids).issubset(job_pids_before)
            or not set(pids).issubset(job_pids_after)
        ):
            raise GuardError(f"{stage}阶段凭据的{proof_name}监听PID不属于仍存活Job")


def _read_stage_record(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise GuardError(f"{label}阶段凭据缺失、不是普通文件或为符号链接")
    return _read_json(path)


def _validate_step_receipt(
    execution: Execution, stage: str, *, allow_test_fixtures: bool
) -> datetime:
    """只接受完整PASS单步凭据；失败或中断遗留不能推进协议。"""
    step_dir = execution.lease.run_dir / stage
    record_path = step_dir / "step_result.json"
    record = _read_stage_record(record_path, stage)
    if record.get("schema") != STEP_RECEIPT_SCHEMA or record.get("step") != stage:
        raise GuardError(f"{stage}阶段凭据schema或步骤名无效")
    _check_receipt_identity(execution, record, stage)
    if (
        record.get("status") != "PASS"
        or type(record.get("semantic_exit_code")) is not int
        or record.get("semantic_exit_code") != 0
        or type(record.get("process_exit_code")) is not int
        or record.get("process_exit_code") != 0
        or record.get("required_marker") != STEP_MARKERS[stage]
        or record.get("runner_error") is not None
        or record.get("owner_postcheck_error") is not None
    ):
        raise GuardError(f"{stage}阶段没有真实PASS凭据")
    if type(record.get("test_fixture_only")) is not bool:
        raise GuardError(f"{stage}阶段凭据缺少test_fixture_only标记")
    if record["test_fixture_only"] and not allow_test_fixtures:
        raise GuardError(f"{stage}阶段凭据仅为fixture，不得用于真实运行")
    pre = record["owner_precheck"].get("listener_owning_pids")
    post = record["owner_postcheck"].get("listener_owning_pids")
    if not set(pre).intersection(post):
        raise GuardError(f"{stage}阶段前后所有权凭据没有相同监听PID")

    launcher_path = step_dir / "launcher"
    if record["test_fixture_only"]:
        if _path_present(launcher_path):
            raise GuardError(f"{stage}阶段fixture凭据不应包含launcher输出")
    else:
        if launcher_path.is_symlink() or not launcher_path.is_dir():
            raise GuardError(f"{stage}阶段launcher输出缺失或不是普通目录")
        launcher_record_path = launcher_path / "execution.json"
        launcher_plan_path = launcher_path / "launch_plan.json"
        for name in ("stdout.bin", "stderr.bin"):
            output = launcher_path / name
            if output.is_symlink() or not output.is_file():
                raise GuardError(f"{stage}阶段launcher输出不完整：{name}")
        launcher_record = _read_stage_record(launcher_record_path, f"{stage}.launcher")
        _read_stage_record(launcher_plan_path, f"{stage}.launcher_plan")
        if (
            record.get("launcher_record") != launcher_record
            or launcher_record.get("status") != "PASS_PROCESS_ONLY"
            or launcher_record.get("root_exit_code") != 0
            or launcher_record.get("cleanup_confirmed") is not True
            or launcher_record.get("timed_out") is not False
            or launcher_record.get("errors") not in (None, [])
        ):
            raise GuardError(f"{stage}阶段launcher未证明进程及清理成功")
    return _aware_utc8(record["at_utc8"], f"{stage}.at_utc8")


def _validate_capture_receipt(
    execution: Execution, phase: str, *, allow_test_fixtures: bool
) -> datetime:
    """只接受当前身份下有完整清单校验的CAPTURED凭据。"""
    run_dir = execution.lease.run_dir
    guard_path = run_dir / f"capture_{phase}_guard.json"
    guard = _read_stage_record(guard_path, f"capture_{phase}_guard")
    if guard.get("schema") != CAPTURE_GUARD_SCHEMA or guard.get("phase") != phase:
        raise GuardError(f"capture_{phase}门禁凭据schema或phase无效")
    _check_receipt_identity(execution, guard, f"capture_{phase}")
    if (
        guard.get("status") != "PASS_CAPTURE_WRAPPER"
        or guard.get("capture_error") is not None
        or guard.get("owner_postcheck_error") is not None
        or type(guard.get("test_fixture_only")) is not bool
    ):
        raise GuardError(f"capture_{phase}阶段没有真实PASS凭据")
    if guard["test_fixture_only"] and not allow_test_fixtures:
        raise GuardError(f"capture_{phase}阶段凭据仅为fixture，不得用于真实运行")
    pre = guard["owner_precheck"].get("listener_owning_pids")
    post = guard["owner_postcheck"].get("listener_owning_pids")
    if not set(pre).intersection(post):
        raise GuardError(f"capture_{phase}阶段前后所有权凭据没有相同监听PID")

    capture = guard.get("capture")
    output_dir = run_dir / f"capture_{phase}"
    if (
        not isinstance(capture, dict)
        or capture.get("status") != "CAPTURED"
        or capture.get("directory") != str(output_dir)
        or not isinstance(capture.get("manifest_sha256"), str)
        or not SHA256_RE.fullmatch(capture["manifest_sha256"])
        or not isinstance(capture.get("read_sha256"), str)
        or not SHA256_RE.fullmatch(capture["read_sha256"])
    ):
        raise GuardError(f"capture_{phase}凭据未绑定完整CAPTURED结果")
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise GuardError(f"capture_{phase}输出缺失或不是普通目录")
    manifest_path = output_dir / "capture_manifest.json"
    checksum_path = output_dir / "capture_manifest.sha256"
    manifest = _read_stage_record(manifest_path, f"capture_{phase}.manifest")
    if (
        manifest.get("schema") not in {"gestureforge.m3_pair.capture.v1", "gestureforge.m3_pair.capture.v2"}
        or manifest.get("status") != "CAPTURED"
        or manifest.get("phase") != phase
        or _sha256(manifest_path.read_bytes()) != capture["manifest_sha256"]
    ):
        raise GuardError(f"capture_{phase}清单与CAPTURED凭据不一致")
    if checksum_path.is_symlink() or not checksum_path.is_file():
        raise GuardError(f"capture_{phase}缺少清单SHA-256旁证")
    checksum_fields = {}
    try:
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            key, value = line.split("=", 1)
            if key in checksum_fields:
                raise ValueError(f"重复字段：{key}")
            checksum_fields[key] = value
    except (OSError, UnicodeError, ValueError) as exc:
        raise GuardError(f"capture_{phase}清单SHA-256旁证无效：{exc}") from exc
    if checksum_fields != {
        "sha256": capture["manifest_sha256"],
        "hash_basis": "worktree_disk",
        "bytes": str(manifest_path.stat().st_size),
    }:
        raise GuardError(f"capture_{phase}清单SHA-256旁证与实际文件不匹配")
    return _aware_utc8(guard.get("at_utc8"), f"capture_{phase}.at_utc8")


def assert_protocol_transition(
    execution: Execution, stage: str, *, allow_test_fixtures: bool = False
) -> None:
    """在任何所有权查询或runner之前执行单调阶段门禁。"""
    valid = {"setup", "restore", "before", "event", "after", "close"}
    if stage not in valid:
        raise GuardError(f"未知协议阶段：{stage}")
    if stage == "close":
        _require_stage_absent(execution.lease.run_dir, "close")
        return
    _require_stage_absent(execution.lease.run_dir, "close")

    run_dir = execution.lease.run_dir
    if stage == "setup":
        for later in ("restore", "before", "event", "after"):
            _require_stage_absent(run_dir, later)
        _require_stage_absent(run_dir, "setup")
        return

    setup_at = _validate_step_receipt(
        execution, "setup", allow_test_fixtures=allow_test_fixtures
    )
    if stage == "restore":
        _require_stage_absent(run_dir, "restore")
        for later in ("before", "event", "after"):
            _require_stage_absent(run_dir, later)
        return

    restore_at = _validate_step_receipt(
        execution, "restore", allow_test_fixtures=allow_test_fixtures
    )
    if restore_at < setup_at:
        raise GuardError("restore记录时间早于setup，阶段顺序无效")
    if stage == "before":
        _require_stage_absent(run_dir, "before")
        for later in ("event", "after"):
            _require_stage_absent(run_dir, later)
        return

    before_at = _validate_capture_receipt(
        execution, "before", allow_test_fixtures=allow_test_fixtures
    )
    if before_at < restore_at:
        raise GuardError("before记录时间早于restore，阶段顺序无效")
    if stage == "event":
        _require_stage_absent(run_dir, "event")
        _require_stage_absent(run_dir, "after")
        return

    event_at = _validate_step_receipt(
        execution, "event", allow_test_fixtures=allow_test_fixtures
    )
    if event_at < before_at:
        raise GuardError("event记录时间早于before，阶段顺序无效")
    if stage == "after":
        _require_stage_absent(run_dir, "after")
        return
    raise GuardError(f"协议阶段判断未覆盖：{stage}")


def verify_owner(
    execution: Execution,
    *,
    thread_alive: Callable[[], bool],
    job_pids: Callable[[str], list[int]],
    listener_pids: Callable[[int], list[int]],
    loopback_connected: Callable[[int], bool],
) -> dict[str, Any]:
    """用Job活动PID与CIM监听PID交叉验证当前监听所有者。"""
    close_path = execution.lease.run_dir / "server" / "server_close.json"
    if close_path.exists() or close_path.is_symlink():
        raise GuardError("server_close.json已存在，拒绝继续")
    if not thread_alive():
        raise GuardError("本轮Job持有线程已退出")
    try:
        before_pids = sorted(set(job_pids(execution.job_name)))
    except Exception as exc:
        raise GuardError(f"无法以查询权限打开本轮Job：{exc}") from exc
    if not before_pids or any(type(pid) is not int or pid <= 0 for pid in before_pids):
        raise GuardError("本轮Job没有有效的活动进程")
    try:
        owners = sorted(set(listener_pids(execution.port)))
    except Exception as exc:
        raise GuardError(f"无法通过CIM查询监听PID：{exc}") from exc
    if not owners or any(type(pid) is not int or pid <= 0 for pid in owners):
        raise GuardError("目标端口没有有效的LISTEN OwningProcess")
    if not set(owners).issubset(before_pids):
        raise GuardError(f"端口监听PID不属于本轮Job：owners={owners} job={before_pids}")
    if not loopback_connected(execution.port):
        raise GuardError("目标端口未接受本机loopback连接")
    try:
        after_pids = sorted(set(job_pids(execution.job_name)))
    except Exception as exc:
        raise GuardError(f"监听核验后无法重新查询本轮Job：{exc}") from exc
    if not set(owners).issubset(after_pids):
        raise GuardError("监听所有者在核验期间已退出本轮Job")
    if not thread_alive():
        raise GuardError("端口核验期间本轮Job持有线程退出")
    if close_path.exists() or close_path.is_symlink():
        raise GuardError("端口核验期间server_close.json出现")
    return {
        "job_name": execution.job_name,
        "job_pids_before": before_pids,
        "listener_owning_pids": owners,
        "job_pids_after": after_pids,
        "loopback_connected": True,
        "thread_alive": True,
    }


def query_named_job_pids(job_name: str) -> list[int]:
    """以JOB_OBJECT_QUERY权限打开命名Job，读取活动PID后立即关闭句柄。"""
    if not JOB_NAME_RE.fullmatch(job_name):
        raise GuardError("拒绝打开格式无效的Job名称")
    if os.name != "nt":
        raise GuardError("命名Windows Job只支持Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    open_job = kernel32.OpenJobObjectW
    open_job.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_wchar_p]
    open_job.restype = ctypes.c_void_p
    query = kernel32.QueryInformationJobObject
    query.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    query.restype = ctypes.c_int
    close = kernel32.CloseHandle
    close.argtypes = [ctypes.c_void_p]
    close.restype = ctypes.c_int
    ctypes.set_last_error(0)
    handle = open_job(0x0004, False, job_name)
    if not handle:
        raise OSError(ctypes.get_last_error(), "OpenJobObjectW(JOB_OBJECT_QUERY)")
    result: list[int] | None = None
    operation_error: BaseException | None = None
    try:
        buffer = ctypes.create_string_buffer(8 + ctypes.sizeof(ctypes.c_size_t) * 1024)
        if not query(handle, 3, buffer, len(buffer), None):
            raise OSError(ctypes.get_last_error(), "QueryInformationJobObject(process_ids)")
        count = struct.unpack_from("<I", buffer.raw, 4)[0]
        if count > 1024:
            raise GuardError("本轮Job活动PID超过固定查询容量")
        values = (ctypes.c_size_t * count).from_buffer(buffer, 8)
        result = [int(values[index]) for index in range(count)]
    except BaseException as exc:
        operation_error = exc
    closed = bool(close(handle))
    if not closed:
        raise OSError(ctypes.get_last_error(), "CloseHandle(query-only Job)")
    if operation_error is not None:
        raise operation_error
    return result or []


def query_listener_pids(port: int) -> list[int]:
    """通过Windows Get-NetTCPConnection CIM对象取得LISTEN OwningProcess。"""
    if type(port) is not int or port not in {3121, 3122}:
        raise GuardError("CIM监听查询端口必须是3121或3122")
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    powershell = system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if not powershell.is_file():
        raise GuardError("找不到Windows PowerShell，无法核验CIM监听所有者")
    command = (
        "$ErrorActionPreference='Stop'; "
        "Get-Command Get-CimInstance -ErrorAction Stop | Out-Null; "
        "$pids=@(Get-CimInstance -Namespace root/StandardCimv2 "
        "-ClassName MSFT_NetTCPConnection "
        f'-Filter "State=2 AND LocalPort={port}" '
        "-ErrorAction Stop | Select-Object -ExpandProperty OwningProcess); "
        "if ($pids.Count -eq 0) { '[]' } "
        "else { ConvertTo-Json -InputObject $pids -Compress }"
    )
    try:
        result = subprocess.run(
            [str(powershell), "-NoProfile", "-NonInteractive", "-Command", command],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GuardError(f"Get-NetTCPConnection查询失败：{exc}") from exc
    if result.returncode != 0:
        raise GuardError(f"Get-NetTCPConnection退出码非零：{result.returncode} {result.stderr.strip()}")
    try:
        value = json.loads(result.stdout.strip())
    except json.JSONDecodeError as exc:
        raise GuardError("Get-NetTCPConnection返回不是有效JSON") from exc
    values = value if isinstance(value, list) else [value]
    if values == []:
        return []
    if any(type(pid) is not int or pid <= 0 for pid in values):
        raise GuardError("Get-NetTCPConnection返回了无效OwningProcess")
    return sorted(set(values))


def loopback_connected(port: int) -> bool:
    """仅探测本机loopback连通性，不据此推断监听所有权。"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def assert_port_free(port: int) -> None:
    """在启动前同时检查CIM监听记录与loopback连通性。"""
    owners = query_listener_pids(port)
    if owners:
        raise GuardError(f"端口已由进程监听，拒绝干扰：{owners}")
    if loopback_connected(port):
        raise GuardError("端口存在loopback连接，拒绝启动")


def close_succeeded(normal_stop: bool, result: dict[str, Any], thread_joined: bool) -> bool:
    """只有本轮Job清理有正证据时才允许报告正常收窗。"""
    return bool(
        normal_stop
        and thread_joined
        and result.get("cleanup_confirmed") is True
        and result.get("job_handle_closed") is True
        and result.get("root_wait_after_job_close") == 0
        and not result.get("timed_out")
        and not result.get("stop_error")
        and not result.get("errors")
    )
