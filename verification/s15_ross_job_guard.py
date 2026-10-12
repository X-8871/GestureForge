"""为S15离线ROSS状态适配与一次性bitgen许可提供故障关闭门禁。"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import msvcrt
import ntpath
import os
import queue
import re
import secrets
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from ctypes import wintypes

import s15_job_guard as job_guard


SCHEMA = "s15-ross-canonical-observation-v1"
EXPECTED_RUN_ID = "S15-T17-G1-ROSS-GUARD-20261013-r02"
EXPECTED_EVIDENCE_RELATIVE = "report/evidence/S2B-T17/s15_ross_guard_20261013_r02"
DCP_RELATIVE = (
    "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02/project_s15_r01/"
    "s2b_inference_candidate.runs/impl_1/s2b_inference_wrapper_postroute_physopt.dcp"
)
DCP_SHA256 = "DB2AAF706C99121EADA307FEC80B4D69B362F1232FF17FCF65F4DD5C0015AD83"
IDENTITY_FIELDS = tuple(job_guard.ROSS_IDENTITY_FIELDS)
OBSERVATION_FIELDS = frozenset(
    {
        "schema",
        "session_id",
        "deployment_type",
        "clock_domain",
        "event",
        "session_state",
        "active_command_sha256",
        "completed_command_sha256",
        "completed_exit_code",
        "root_identity",
        "heartbeat_sequence",
        "observed_monotonic",
        "published_monotonic",
        "progress_counter",
        "progress_monotonic",
    }
)
HEARTBEAT_FRESHNESS_SECONDS = job_guard.CONSUMER_FRESHNESS_LIMIT_SECONDS
HANDOFF_LIMIT_SECONDS = job_guard.SUPERVISOR_HANDOFF_LIMIT_SECONDS
DISPATCH_CALLBACK_TIMEOUT_SECONDS = HANDOFF_LIMIT_SECONDS
NO_PROGRESS_LIMIT_SECONDS = job_guard.NO_PROGRESS_LIMIT_SECONDS
STOP_EVENTS = frozenset({"STOP"})
RUN_EVENTS = frozenset({"HEARTBEAT"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", job_guard.FILETIME),
        ("ftLastAccessTime", job_guard.FILETIME),
        ("ftLastWriteTime", job_guard.FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]


_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_kernel32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
_kernel32.CreateFileW.restype = wintypes.HANDLE
_kernel32.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(BY_HANDLE_FILE_INFORMATION)]
_kernel32.GetFileInformationByHandle.restype = wintypes.BOOL
_kernel32.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
_kernel32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_FILE_LIST_DIRECTORY = 0x00000001
_FILE_SHARE_READ = 0x00000001
_FILE_SHARE_WRITE = 0x00000002
_OPEN_EXISTING = 3
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
_FILE_ATTRIBUTE_DIRECTORY = 0x00000010


def _api_open_directory_handle(path: str):
    """只列目录打开并拒绝共享删除，从而固定该路径组件。"""
    ctypes.set_last_error(0)
    handle = _kernel32.CreateFileW(
        str(path),
        _FILE_LIST_DIRECTORY,
        _FILE_SHARE_READ | _FILE_SHARE_WRITE,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT,
        None,
    )
    if not handle or handle == _INVALID_HANDLE_VALUE:
        raise RossGuardError(f"CreateFileW(directory anchor)失败：{path}，WinError={ctypes.get_last_error()}")
    return handle


def _api_directory_identity(handle) -> dict:
    info = BY_HANDLE_FILE_INFORMATION()
    ctypes.set_last_error(0)
    if not _kernel32.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise RossGuardError(f"GetFileInformationByHandle(directory)失败：WinError={ctypes.get_last_error()}")
    return {
        "attributes": int(info.dwFileAttributes),
        "volume_serial": int(info.dwVolumeSerialNumber),
        "file_index": (int(info.nFileIndexHigh) << 32) | int(info.nFileIndexLow),
        "creation_ticks": (int(info.ftCreationTime.dwHighDateTime) << 32) | int(info.ftCreationTime.dwLowDateTime),
    }


def _api_directory_final_path(handle) -> str:
    """读取目录句柄的规范DOS路径，并保留组件大小写供逐字节核验。"""
    buffer = ctypes.create_unicode_buffer(32768)
    ctypes.set_last_error(0)
    length = int(_kernel32.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0))
    if length <= 0 or length >= len(buffer):
        raise RossGuardError(f"GetFinalPathNameByHandleW(directory)失败：WinError={ctypes.get_last_error()}")
    value = buffer.value
    if value.startswith("\\\\?\\"):
        value = value[4:]
    return value


def _directory_chain(path: str | Path) -> tuple[Path, ...]:
    """只接受规范本地绝对路径，生成C:\\根以下的逐级路径链。"""
    raw = os.fspath(path)
    if type(raw) is not str or not raw or raw.startswith(("\\\\", "//")) or "/" in raw:
        raise RossGuardError("目录租约只接受反斜线本地路径，拒绝UNC/设备/混合分隔符")
    drive, tail = ntpath.splitdrive(raw)
    if not re.fullmatch(r"[A-Za-z]:", drive) or not tail.startswith("\\"):
        raise RossGuardError(f"目录租约路径不是本地盘符绝对路径：{raw!r}")
    components = tail[1:].split("\\") if tail[1:] else []
    if any(part in {"", ".", ".."} for part in components):
        raise RossGuardError(f"目录租约路径含空、点或父级分量：{raw!r}")
    normalized = str(Path(raw))
    if normalized != raw:
        raise RossGuardError(f"目录租约路径不是规范字面路径：{raw!r} -> {normalized!r}")
    paths = []
    cursor = Path(drive + "\\")
    for component in components:
        child = cursor / component
        if child.parent != cursor:
            raise RossGuardError(f"目录租约路径链不连续：{cursor} -> {child}")
        paths.append(child)
        cursor = child
    if not paths:
        raise RossGuardError("C:\\盘符根不是可租约输出目录")
    return tuple(paths)


class DirectoryAnchor:
    """逐级固定C:\\根以下所有祖先，保持输出路径不可重定向。"""

    def __init__(self, path: Path):
        raw_path = os.fspath(path)
        self.component_paths = _directory_chain(raw_path)
        self.path = Path(raw_path)
        if not self.path.is_absolute() or not self.path.is_dir():
            raise RossGuardError(f"目录租约目标不存在或不是绝对目录：{self.path}")
        self.entries: list[dict] = []
        self.closed = False
        try:
            for component_path in self.component_paths:
                handle = _api_open_directory_handle(str(component_path))
                try:
                    identity = _api_directory_identity(handle)
                    final_path = _api_directory_final_path(handle)
                    self._verify_component(component_path, identity, final_path)
                    self.entries.append({"path": component_path, "handle": handle,
                                         "identity": identity, "final_path": final_path})
                except BaseException:
                    job_guard._checked_close_handle(handle, f"失败目录组件 {component_path}")
                    raise
            self._verify_all_components()
        except BaseException as primary:
            try:
                self.close()
            except BaseException as cleanup:
                raise RossGuardError(f"目录祖先链核验失败：{primary!r}；关闭句柄失败：{cleanup!r}") from primary
            raise

    @property
    def handle(self):
        """兼容只读诊断接口，返回叶子目录句柄。"""
        return self.entries[-1]["handle"] if self.entries else None

    @property
    def identity(self) -> dict:
        """返回叶子目录身份快照。"""
        return self.entries[-1]["identity"] if self.entries else {}

    @staticmethod
    def _verify_component(path: Path, identity: dict, final_path: str) -> None:
        if not identity["attributes"] & _FILE_ATTRIBUTE_DIRECTORY:
            raise RossGuardError(f"路径组件不是目录：{path}")
        if identity["attributes"] & _FILE_ATTRIBUTE_REPARSE_POINT:
            raise RossGuardError(f"目录祖先链包含reparse point：{path}")
        if final_path != str(path):
            raise RossGuardError(f"目录句柄最终路径与逐字批准路径不符：{path} -> {final_path}")

    def _verify_all_components(self) -> None:
        if self.closed or len(self.entries) != len(self.component_paths):
            raise RossGuardError("目录祖先链句柄不完整或已关闭")
        for entry in self.entries:
            held_identity = _api_directory_identity(entry["handle"])
            held_final = _api_directory_final_path(entry["handle"])
            self._verify_component(entry["path"], held_identity, held_final)
            if held_identity != entry["identity"] or held_final != entry["final_path"]:
                raise RossGuardError(f"持有的目录组件HANDLE身份漂移：{entry['path']}")
        opened = []
        try:
            for entry in self.entries:
                handle = _api_open_directory_handle(str(entry["path"]))
                opened.append(handle)
                current = _api_directory_identity(handle)
                final_path = _api_directory_final_path(handle)
                self._verify_component(entry["path"], current, final_path)
                if current != entry["identity"] or final_path != entry["final_path"]:
                    raise RossGuardError(f"目录祖先链重开后身份/final path变化：{entry['path']}")
        finally:
            close_errors = []
            for handle in reversed(opened):
                try:
                    job_guard._checked_close_handle(handle, "目录祖先链复读")
                except BaseException as error:
                    close_errors.append(repr(error))
            if close_errors:
                raise RossGuardError("目录祖先链复读句柄关闭失败：" + "; ".join(close_errors))

    def verify_path(self) -> None:
        self._verify_all_components()

    def close(self) -> None:
        failures = []
        remaining = []
        for entry in reversed(self.entries):
            handle = entry.get("handle")
            if not handle:
                continue
            try:
                job_guard._checked_close_handle(handle, f"目录锚点 {entry['path']}")
                entry["handle"] = None
            except BaseException as error:
                failures.append(f"{entry['path']}: {error!r}")
                remaining.append(entry)
        self.entries = list(reversed(remaining))
        self.closed = not self.entries
        if failures:
            raise RossGuardError("关闭目录祖先链句柄失败：" + "; ".join(failures))


class RossGuardError(RuntimeError):
    """ROSS规范、任务序列或监护证据无法证明时拒绝继续。"""


class SchemaUnbound(RossGuardError):
    """真实MCP响应schema尚未绑定到本地规范。"""


class RossJobGuardError(RossGuardError):
    """控制器进入FAILED时返回的确定性拒绝异常。"""


class AppendOnlyJsonl:
    """以单写者、追加并刷盘的JSONL传递canonical心跳。"""

    def __init__(self, path: Path):
        self.path = Path(path)
        if self.path.exists() or self.path.is_symlink():
            raise RossGuardError(f"状态通道已存在，拒绝覆盖：{self.path}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("xb"):
            pass
        self._read_count = 0
        self._lock = threading.RLock()

    @contextmanager
    def consume_lease(self):
        """锁住append通道到EOF快照及受控dispatch callback结束。"""
        with self._lock:
            with self.path.open("r+b", buffering=0) as stream:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    stream.seek(0, os.SEEK_END)
                    end = stream.tell()
                    stream.seek(0)
                    data = stream.read(end)
                    lines = data.splitlines(keepends=True)
                    complete = []
                    for line in lines:
                        if not line.endswith(b"\n"):
                            break
                        complete.append(line)
                    if self._read_count > len(complete):
                        raise RossGuardError("append-only状态文件行数倒退")
                    result = []
                    for line in complete[self._read_count :]:
                        try:
                            value = json.loads(line.decode("utf-8"))
                        except (UnicodeDecodeError, json.JSONDecodeError) as error:
                            raise RossGuardError(f"已落盘的完整JSONL行不可解析：{error!r}") from error
                        result.append(value)
                    yield result
                    self._read_count = len(complete)
                finally:
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    def publish(self, record: dict) -> None:
        """先追加完整行并flush，再由消费者解析和评估。"""
        raw = json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=True)
        with self._lock:
            with self.path.open("r+b", buffering=0) as stream:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    stream.seek(0, os.SEEK_END)
                    stream.write((raw + "\n").encode("utf-8"))
                    os.fsync(stream.fileno())
                finally:
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    def read_new(self) -> list[dict]:
        """只返回完整JSONL行；部分尾行留待下一轮，不读取未来字节。"""
        with self.consume_lease() as result:
            return list(result)


class StrictCanonicalAdapter:
    """验证由外层ROSS桥接器按固定字段组装的canonical记录。"""

    def decode(self, record: object, expected_session_id: str, now: float) -> dict:
        if type(record) is not dict or set(record) != OBSERVATION_FIELDS:
            raise RossGuardError("canonical ROSS记录字段集合缺失或多余")
        if record["schema"] != SCHEMA:
            raise RossGuardError("canonical ROSS schema版本不匹配")
        if type(expected_session_id) is not str or not expected_session_id:
            raise RossGuardError("调用方原样session_id无效")
        if type(record["session_id"]) is not str or record["session_id"] != expected_session_id:
            raise RossGuardError("ROSS session_id与调用方原样session_id不符")
        if record["deployment_type"] != "local":
            raise RossGuardError("只接受同机本地ROSS进程身份")
        if record["clock_domain"] != "host_monotonic":
            raise RossGuardError("ROSS观察时间不在守护进程同一单调时钟域")
        if type(record["event"]) is not str or record["event"] not in RUN_EVENTS | STOP_EVENTS:
            raise RossGuardError("ROSS心跳事件类型不受支持")
        if type(record["session_state"]) is not str or record["session_state"] not in {"idle", "active", "closed"}:
            raise RossGuardError("ROSS会话状态必须是精确枚举值")
        sequence = record["heartbeat_sequence"]
        if type(sequence) is not int or sequence < 0:
            raise RossGuardError("ROSS心跳序号必须为非负整数")
        observed = _finite_time(record["observed_monotonic"], "observed_monotonic")
        if observed > now:
            raise RossGuardError("ROSS心跳观察时间位于未来")
        age = now - observed
        if age > HEARTBEAT_FRESHNESS_SECONDS:
            raise RossGuardError(f"ROSS心跳已过期：{age:.6f}s")
        published = _finite_time(record["published_monotonic"], "published_monotonic")
        if published < observed:
            raise RossGuardError("状态通道发布时间早于ROSS观察时间")
        if published > now:
            raise RossGuardError("状态通道发布时间位于未来")
        handoff_age = now - published
        if handoff_age > HANDOFF_LIMIT_SECONDS:
            raise RossGuardError(f"ROSS状态handoff已超过门槛：{handoff_age:.6f}s")
        progress_time = _finite_time(record["progress_monotonic"], "progress_monotonic")
        if progress_time > observed:
            raise RossGuardError("进度时间晚于对应心跳观察时间")
        progress_counter = record["progress_counter"]
        if type(progress_counter) is not int or progress_counter < 0:
            raise RossGuardError("进度计数必须为非负整数")
        identity = _validate_identity(record["root_identity"])
        active_sha = record["active_command_sha256"]
        completed_sha = record["completed_command_sha256"]
        exit_code = record["completed_exit_code"]
        if active_sha is not None and (type(active_sha) is not str or not SHA256_RE.fullmatch(active_sha)):
            raise RossGuardError("active command SHA256格式无效")
        if completed_sha is not None and (type(completed_sha) is not str or not SHA256_RE.fullmatch(completed_sha)):
            raise RossGuardError("completed command SHA256格式无效")
        if exit_code is not None and type(exit_code) is not int:
            raise RossGuardError("命令退出码必须为整数或null")
        if record["event"] == "STOP":
            if record["session_state"] != "closed" or active_sha is not None:
                raise RossGuardError("STOP必须对应closed且无活动命令")
        elif record["session_state"] == "closed":
            raise RossGuardError("closed状态必须以STOP作为终态事件")
        if record["session_state"] == "active" and active_sha is None:
            raise RossGuardError("active状态缺少活动命令SHA256")
        if record["session_state"] != "active" and active_sha is not None:
            raise RossGuardError("非active状态不得携带活动命令SHA256")
        return dict(record, root_identity=identity, age_seconds=age, handoff_age_seconds=handoff_age)

    def decode_raw_mcp_result(self, tool_name: str, tool_input: object, result: object) -> dict:
        """当前MCP声明没有身份返回schema，禁止猜字段并fail closed。"""
        del tool_name, tool_input, result
        raise SchemaUnbound("ROSS MCP响应的PID/creation time/exe/cwd/cmdline/ppid字段映射未冻结")


def _finite_time(value: object, field: str) -> float:
    if type(value) not in (int, float):
        raise RossGuardError(f"{field}必须是有限单调时间")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise RossGuardError(f"{field}不是有限非负单调时间")
    return result


def _validate_identity(identity: object) -> dict:
    if type(identity) is not dict or set(identity) != set(IDENTITY_FIELDS):
        raise RossGuardError("root identity必须恰含六个绑定字段")
    pid = identity["pid"]
    if type(pid) is not int or pid <= 0:
        raise RossGuardError("root PID无效")
    created = identity["create_time"]
    if type(created) not in (int, float) or not math.isfinite(float(created)) or float(created) <= 0:
        raise RossGuardError("root creation time不是正的有限数")
    for field in ("exe", "cwd"):
        if type(identity[field]) is not str or not identity[field]:
            raise RossGuardError(f"root {field}必须是非空原样字符串")
    if type(identity["cmdline"]) is not list or not all(type(item) is str for item in identity["cmdline"]):
        raise RossGuardError("root cmdline必须是字符串数组")
    if type(identity["ppid"]) is not int or identity["ppid"] < 0:
        raise RossGuardError("root ppid无效")
    return {field: identity[field] for field in IDENTITY_FIELDS}


def _same_identity(left: dict, right: dict) -> bool:
    return all(left.get(field) == right.get(field) for field in IDENTITY_FIELDS)


def _mcp_record_for_frozen_guard(session_id: str, identity: dict) -> dict:
    """只将已验证canonical状态映射到冻结R05守护器自身的输入格式。"""
    payload = {
        "session_id": session_id,
        "status": "idle",
        "active_command": None,
        "root_identity": identity,
    }
    return {
        "input": {"session_id": session_id},
        "result": {"content": [{"type": "text", "text": json.dumps(payload, separators=(",", ":"))}]},
    }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _no_reparse_components(path: Path) -> None:
    """拒绝DCP和证据输出路径中任一Windows重解析点。"""
    if os.name != "nt":
        raise RossGuardError("ROSS bitgen guard仅支持Windows")
    get_attributes = ctypes.WinDLL("kernel32", use_last_error=True).GetFileAttributesW
    get_attributes.argtypes = [ctypes.c_wchar_p]
    get_attributes.restype = ctypes.c_uint32
    parts = [Path(path), *Path(path).parents]
    for part in reversed(parts):
        attributes = int(get_attributes(str(part)))
        if attributes == 0xFFFFFFFF:
            raise RossGuardError(f"无法读取路径属性：{part}，WinError={ctypes.get_last_error()}")
        if attributes & 0x00000400:
            raise RossGuardError(f"路径包含reparse point：{part}")


@dataclass(frozen=True)
class ReadyReceipt:
    """不可变、一次性绑定实际Job READY token的控制器凭据。"""

    owner: object
    controller_id: bytes
    nonce: bytes
    session_id: str
    identity_items: tuple
    issued_monotonic: float
    heartbeat_sequence: int
    job_token: object


@dataclass(frozen=True)
class DispatchPermit:
    """不可变的单次许可，绑定命令、状态版本、输出与DCP身份。"""

    owner: object
    controller_id: bytes
    nonce: bytes
    session_id: str
    sequence: int
    command: str
    command_sha256: str
    issued_monotonic: float
    heartbeat_sequence: int
    output_path: str | None
    dcp_sha256: str | None


@dataclass(frozen=True)
class DispatchAck:
    """将外层MCP调用响应绑定到本次唯一派发许可。"""

    owner: object
    controller_id: bytes
    permit_nonce: bytes
    session_id: str
    sequence: int
    command: str
    command_sha256: str
    output_path: str | None
    dcp_sha256: str | None
    outcome: str
    response_sha256: str
    acknowledged_monotonic: float


class RossJobGuardController:
    """READY、两条固定Tcl命令、heartbeat监督及Job终态闭合。"""

    def __init__(self, job, expected_session_id: str, evidence_root: Path, run_id: str = EXPECTED_RUN_ID, adapter=None):
        if os.name != "nt":
            raise RossGuardError("真实ROSS进程监护候选仅支持Windows")
        if run_id != EXPECTED_RUN_ID:
            raise RossGuardError("RunId与本候选冻结RunId不符")
        if type(expected_session_id) is not str or not expected_session_id:
            raise RossGuardError("必须绑定ROSS调用端原样session_id")
        self.repo_root = Path(__file__).resolve().parents[1]
        self.expected_evidence_root = self.repo_root / Path(EXPECTED_EVIDENCE_RELATIVE)
        provided = Path(evidence_root)
        resolved_expected = self.expected_evidence_root.resolve(strict=True)
        resolved_provided = provided.resolve(strict=True)
        if resolved_provided != resolved_expected and resolved_expected not in resolved_provided.parents:
            raise RossGuardError("证据运行目录不在本候选唯一批准根目录下")
        self.evidence_root = resolved_provided
        self._lock = threading.RLock()
        self._clock = time.monotonic
        self._controller_id = secrets.token_bytes(32)
        self._expected_permit_nonce = None
        self._pending_permit_binding = None
        self._pending_ack_nonce = None
        self._last_ack_binding = None
        self._ready_nonce = None
        self._job_ready_token = None
        self._ready_consumed = False
        self._evidence_anchor = DirectoryAnchor(self.evidence_root)
        self._output_anchor = None
        self.run_id = run_id
        self.expected_session_id = expected_session_id
        self.job = job
        self.adapter = adapter or StrictCanonicalAdapter()
        self.channel = AppendOnlyJsonl(self.evidence_root / f"ross_heartbeat_{secrets.token_hex(6)}.jsonl")
        self.sample_log = AppendOnlyJsonl(self.evidence_root / f"job_samples_{secrets.token_hex(6)}.jsonl")
        self.dcp_path = self.repo_root / Path(DCP_RELATIVE)
        self.identity = None
        self.latest = None
        self.sequence = -1
        self.progress_counter = None
        self.progress_monotonic = None
        self.last_progress_token = None
        self.last_ingest_monotonic = None
        self.ready_receipt = None
        self.pending_permit = None
        self.pending_command = None
        self.command_index = 0
        self.last_completed_sha256 = None
        self.last_completed_exit_code = None
        self.state = "NEW"
        self.failure = None
        self.uncertain_dispatch = None
        self._dispatch_lease_active = False
        self._dispatch_worker = None
        self.max_heartbeat_age = 0.0
        self.max_handoff_seconds = 0.0
        self.max_sample_gap_seconds = 0.0
        self._previous_sample_start = None
        self._previous_accounting = None
        self._previous_pids = None
        self._previous_keys = None
        self._last_journal_record_count = 0
        self._output_directory = None
        self._output_path = None
        self._command_texts = None

    def _fail(self, message: str):
        self.failure = message
        self.state = "FAILED"
        cleanup_failures = []
        if self.job is not None and not self.job.closed:
            try:
                self.job.close()
            except BaseException as close_error:
                cleanup_failures.append(f"关闭自有Job失败：{close_error!r}")
        for anchor_name in ("_output_anchor", "_evidence_anchor"):
            anchor = getattr(self, anchor_name, None)
            if anchor is not None:
                try:
                    anchor.close()
                    setattr(self, anchor_name, None)
                except BaseException as close_error:
                    cleanup_failures.append(f"关闭{anchor_name}失败：{close_error!r}")
        if cleanup_failures:
            self.failure += "；" + "；".join(cleanup_failures)
        raise RossJobGuardError(self.failure)

    def _verify_dcp_and_command(self) -> str:
        try:
            _no_reparse_components(self.dcp_path)
            if not self.dcp_path.is_file():
                self._fail(f"冻结DCP不是普通文件：{self.dcp_path}")
            actual_sha = _file_sha256(self.dcp_path)
        except RossJobGuardError:
            raise
        except BaseException as error:
            self._fail(f"冻结DCP读取/哈希失败：{error!r}")
        if actual_sha != DCP_SHA256:
            self._fail(f"冻结DCP SHA256不符：actual={actual_sha}")
        return f"open_checkpoint {{{self.dcp_path}}}"

    def start(self, record: dict) -> dict:
        """先落盘首个idle观察，再逐字段核验并创建READY。"""
        with self._lock:
            if self.state != "NEW":
                self._fail("控制器只允许启动一次")
            self.channel.publish(record)
            self.process_new_heartbeats()
            if self.state != "READY_OPEN":
                self._fail("首条canonical记录未形成READY")
            return {
                "kind": "READY",
                "run_id": self.run_id,
                "session_id": self.expected_session_id,
                "root_identity": self.identity,
                "job_limit_flags": self.job.flags,
                "job_pids": list(self.job.pid_list()),
                "active_processes": self.job.accounting()["active_processes"],
                "dcp_path": str(self.dcp_path),
                "dcp_sha256": DCP_SHA256,
                "heartbeat_sequence": self.sequence,
                "observed_monotonic": self.latest["observed_monotonic"],
                "ready_receipt_nonce_sha256": hashlib.sha256(self._ready_nonce).hexdigest(),
            }

    def _accept_record(self, raw: object) -> None:
        if self.state in {"FAILED", "STOPPED", "CLOSED"}:
            self._fail("STOP/失败之后拒绝任何状态复位或追加记录")
        now = time.monotonic()
        try:
            record = self.adapter.decode(raw, self.expected_session_id, now)
        except BaseException as error:
            self._fail(f"ROSS canonical记录拒绝：{error!r}")
        sequence = record["heartbeat_sequence"]
        expected_sequence = 0 if self.sequence < 0 else self.sequence + 1
        if sequence != expected_sequence:
            self._fail(f"ROSS heartbeat序号不连续：expected={expected_sequence}, actual={sequence}")
        if self.latest is not None and record["observed_monotonic"] <= self.latest["observed_monotonic"]:
            self._fail("ROSS观察时间没有严格递增")
        progress = record["progress_counter"]
        progress_time = record["progress_monotonic"]
        if self.progress_counter is not None:
            if progress < self.progress_counter:
                self._fail("进度计数倒退")
            if progress == self.progress_counter and progress_time != self.progress_monotonic:
                self._fail("无新进度时进度时间戳发生漂移")
            if progress > self.progress_counter and progress_time <= self.progress_monotonic:
                self._fail("进度增加但进度时间没有递增")
        if self.identity is not None and not _same_identity(record["root_identity"], self.identity):
            self._fail("ROSS六字段root identity相对READY发生漂移")
        if record["event"] in RUN_EVENTS:
            try:
                local = job_guard.process_identity(record["root_identity"]["pid"])
            except BaseException as error:
                self._fail(f"WinAPI/本地进程身份读回失败：{error!r}")
            if not _same_identity(record["root_identity"], local):
                self._fail("ROSS canonical六字段与本机进程身份逐字段不符")
        elif self.identity is not None and not _same_identity(record["root_identity"], self.identity):
            self._fail("STOP identity与已绑定root不符")
        if self.state == "NEW":
            if record["event"] != "HEARTBEAT" or record["session_state"] != "idle" or record["active_command_sha256"] is not None:
                self._fail("首次会话记录必须是idle且无活动命令")
            if record["completed_command_sha256"] is not None or record["completed_exit_code"] is not None:
                self._fail("首次会话记录不得携带未授权命令完成回执")
            if self.job.pid_list() or self.job.accounting()["active_processes"] != 0 or self.job.accounting()["total_processes"] != 0:
                self._fail("新建Job在READY前已有成员")
            expected_open = self._verify_dcp_and_command()
            self.identity = dict(record["root_identity"])
            try:
                _, ready_token = self.job.attach_idle_root(_mcp_record_for_frozen_guard(self.expected_session_id, self.identity))
            except BaseException as error:
                self._fail(f"Job加入ROSS root/后代闭合READY失败：{error!r}")
            if self.job.session_id != self.expected_session_id or not _same_identity(self.job.root_identity, self.identity):
                self._fail("冻结Job READY读回与canonical session/root不符")
            if not (self.job.flags & job_guard.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE):
                self._fail("Job未启用KILL_ON_JOB_CLOSE")
            if self.job.flags & (0x00000800 | 0x00001000):
                self._fail("Job允许breakaway")
            if self.job.pid_list() != (self.identity["pid"],) or self.job.accounting()["active_processes"] != 1:
                self._fail("READY时Job成员不是唯一root")
            self._job_ready_token = ready_token
            self._ready_nonce = secrets.token_bytes(32)
            identity_items = tuple(
                (field, tuple(self.identity[field]) if field == "cmdline" else self.identity[field])
                for field in IDENTITY_FIELDS
            )
            self.ready_receipt = ReadyReceipt(
                self,
                self._controller_id,
                self._ready_nonce,
                self.expected_session_id,
                identity_items,
                now,
                sequence,
                ready_token,
            )
            self._command_texts = [expected_open]
            self.state = "READY_OPEN"
        else:
            self._apply_transition(record, now)
        self.latest = record
        self.sequence = sequence
        self.progress_counter = progress
        self.progress_monotonic = progress_time
        self.last_progress_token = progress
        self.last_ingest_monotonic = time.monotonic()
        self.max_heartbeat_age = max(self.max_heartbeat_age, record["age_seconds"])
        handoff = record["handoff_age_seconds"]
        self.max_handoff_seconds = max(self.max_handoff_seconds, handoff)
        if handoff > HANDOFF_LIMIT_SECONDS:
            self._fail(f"ROSS heartbeat处理handoff超过门槛：{handoff:.6f}s")

    def _apply_transition(self, record: dict, now: float) -> None:
        if record["event"] == "STOP":
            if self.command_index != 2 or self.pending_command is not None or self.state != "CLOSE_REQUIRED":
                self._fail("只能在两条固定命令成功后接受STOP")
            if record["completed_command_sha256"] != self.last_completed_sha256 or record["completed_exit_code"] != 0:
                self._fail("STOP未绑定成功的最后bitstream命令回执")
            self.state = "STOPPED"
            return
        if self.state == "NEW":
            self._fail("canonical会话记录状态机错误")
        active_sha = record["active_command_sha256"]
        complete_sha = record["completed_command_sha256"]
        exit_code = record["completed_exit_code"]
        if self.pending_command is not None:
            pending = self.pending_command
            if record["session_state"] == "active":
                if active_sha != pending["sha256"]:
                    self._fail("ROSS active command SHA与唯一许可不符")
                expected_previous_sha = self.last_completed_sha256
                if complete_sha != expected_previous_sha or exit_code != (0 if expected_previous_sha is not None else None):
                    self._fail("活动命令heartbeat的前序完成回执不符")
                if now - pending["claimed_monotonic"] > HANDOFF_LIMIT_SECONDS and not pending["active_seen"]:
                    self._fail("命令启动handoff超过5秒")
                pending["active_seen"] = True
                if now - record["progress_monotonic"] >= NO_PROGRESS_LIMIT_SECONDS:
                    self._fail("ROSS命令无进度达到900秒")
                self.state = "ACTIVE"
                return
            if record["session_state"] != "idle" or active_sha is not None:
                self._fail("等待命令完成时ROSS状态非法")
            if complete_sha != pending["sha256"] or exit_code != 0:
                self._fail("命令完成SHA/exit code与派发许可不符")
            self.last_completed_sha256 = complete_sha
            self.last_completed_exit_code = exit_code
            self.pending_command = None
            self.command_index += 1
            self.state = "READY_BITGEN" if self.command_index == 1 else "CLOSE_REQUIRED"
            return
        if record["session_state"] == "active":
            self._fail("没有有效的一次性许可却观测到活动命令")
        if record["session_state"] != "idle" or active_sha is not None:
            self._fail("无活动许可时会话必须保持idle")
        if self.command_index == 0:
            if complete_sha is not None or exit_code is not None:
                self._fail("open_checkpoint派发前出现未授权命令回执")
        elif complete_sha != self.last_completed_sha256 or exit_code != 0:
            self._fail("空闲heartbeat未重复绑定最近一次成功命令")

    def _assert_fresh(self, now: float) -> None:
        if self.latest is None:
            self._fail("尚无已接受的ROSS心跳")
        age = now - self.latest["observed_monotonic"]
        if not math.isfinite(age) or age < 0.0 or age > HEARTBEAT_FRESHNESS_SECONDS:
            self._fail(f"最近ROSS心跳过期/未来：age={age!r}")
        handoff = now - self.latest["published_monotonic"]
        if not math.isfinite(handoff) or handoff < 0.0 or handoff > HANDOFF_LIMIT_SECONDS:
            self._fail(f"监督器至ROSS消费者handoff超时：age={handoff!r}")
        if self.latest["session_state"] == "active":
            no_progress = now - self.latest["progress_monotonic"]
            if no_progress >= NO_PROGRESS_LIMIT_SECONDS:
                self._fail(f"运行中会话无进度达到900秒：{no_progress:.6f}s")
        try:
            local = job_guard.process_identity(self.identity["pid"])
        except BaseException as error:
            self._fail(f"root六字段身份重新读取失败：{error!r}")
        if not _same_identity(self.identity, local):
            self._fail("root PID/create_time/exe/cwd/cmdline/ppid身份重读漂移")

    def issue_dispatch_permit(self) -> DispatchPermit:
        """只生成固定命令许可；由外层总控按receipt串行调用ROSS MCP。"""
        with self._lock:
            with self.channel.consume_lease() as records:
                self._consume_records_locked(records)
            if self.pending_permit is not None:
                self._fail("当前已有未消费派发许可")
            if self.state not in {"READY_OPEN", "READY_BITGEN"} or self.pending_command is not None:
                self._fail(f"当前状态不允许派发：{self.state}")
            now = self._clock()
            self._assert_fresh(now)
            if self.latest["session_state"] != "idle" or self.latest["active_command_sha256"] is not None:
                self._fail("派发前ROSS会话不处于idle")
            if self.command_index == 0:
                command = self._command_texts[0]
                output_path = None
                dcp_sha = DCP_SHA256
            elif self.command_index == 1:
                if self._output_directory is None:
                    self._evidence_anchor.verify_path()
                    token = secrets.token_hex(8)
                    output_dir = self.evidence_root / f"bitgen_{self.run_id}_{token}"
                    if output_dir.exists() or output_dir.is_symlink():
                        self._fail("bitgen输出目录已存在，拒绝复用")
                    output_dir.mkdir(mode=0o700)
                    _no_reparse_components(output_dir)
                    if output_dir.resolve(strict=True).parent != self.evidence_root:
                        self._fail("bitgen输出目录解析后逃逸批准证据目录")
                    output = output_dir / "s2b_inference_wrapper.bit"
                    if output.exists() or output.is_symlink():
                        self._fail("bitstream输出目标已经存在")
                    self._output_anchor = DirectoryAnchor(output_dir)
                    self._output_anchor.verify_path()
                    self._output_directory = output_dir
                    self._output_path = output
                command = f"write_bitstream -force {{{self._output_path.as_posix()}}}"
                output_path = str(self._output_path)
                dcp_sha = None
                if not command.startswith("write_bitstream -force {") or not command.endswith("}"):
                    self._fail("bitstream Tcl命令生成不符合固定模板")
            else:
                self._fail("命令序列超出两条批准命令")
            nonce = secrets.token_bytes(32)
            digest = hashlib.sha256(command.encode("utf-8")).hexdigest()
            permit = DispatchPermit(
                self,
                self._controller_id,
                nonce,
                self.expected_session_id,
                self.command_index,
                command,
                digest,
                now,
                self.sequence,
                output_path,
                dcp_sha,
            )
            self._expected_permit_nonce = nonce
            self._pending_permit_binding = self._permit_binding(permit)
            self.pending_permit = permit
            return permit

    @staticmethod
    def _permit_binding(permit: DispatchPermit) -> tuple:
        return (
            permit.owner,
            permit.controller_id,
            permit.nonce,
            permit.session_id,
            permit.sequence,
            permit.command,
            permit.command_sha256,
            permit.issued_monotonic,
            permit.heartbeat_sequence,
            permit.output_path,
            permit.dcp_sha256,
        )

    def _consume_records_locked(self, records: list[dict]) -> None:
        for record in records:
            self._accept_record(record)

    def _record_uncertain_dispatch(self, permit: DispatchPermit, claimed: float, reason: str) -> None:
        """记录远端回执未知并撤销本地许可；不声称取消已派发的远端命令。"""
        observed = self._clock()
        record = {
            "event": "DISPATCH_RESULT_UNCERTAIN",
            "session_id": permit.session_id,
            "sequence": permit.sequence,
            "command_sha256": permit.command_sha256,
            "claimed_monotonic": claimed,
            "observed_monotonic": observed,
            "result": "UNCERTAIN",
            "late_ack_policy": "DISCARD",
            "remote_cancel_guarantee": "NONE",
            "reason": reason,
        }
        self.uncertain_dispatch = record
        if self.pending_command is not None:
            self.pending_command["dispatch_outcome"] = "UNCERTAIN"
        self.pending_permit = None
        self._expected_permit_nonce = None
        self._pending_permit_binding = None
        self._pending_ack_nonce = None
        try:
            self.sample_log.publish(record)
        except BaseException as error:
            record["evidence_write_error"] = repr(error)
        message = (
            "外层MCP调用结果不确定；本地等待已超时/失败，许可已撤销，迟到ACK一律丢弃，"
            "不保证取消已开始的远端执行；" + reason
        )
        if "evidence_write_error" in record:
            message += "; 不确定结果证据写入失败=" + record["evidence_write_error"]
        self._fail(message)

    def _dispatch_with_deadline(self, callback, receipt: dict, permit: DispatchPermit, claimed: float):
        """在守护线程中调用外层适配器，等待有硬上限且只由本线程消费ACK。"""
        responses = queue.Queue(maxsize=1)

        def invoke() -> None:
            try:
                responses.put((True, callback(receipt)))
            except BaseException as error:
                responses.put((False, error))

        worker = threading.Thread(
            target=invoke,
            name=f"s15-ross-dispatch-{permit.sequence}",
            daemon=True,
        )
        self._dispatch_worker = worker
        self._dispatch_lease_active = True
        try:
            worker.start()
        except BaseException as error:
            self._dispatch_lease_active = False
            self._dispatch_worker = None
            self._fail(f"callback工作线程启动失败，未调用外层派发器：{error!r}")
        try:
            succeeded, value = responses.get(timeout=DISPATCH_CALLBACK_TIMEOUT_SECONDS)
        except queue.Empty:
            self._dispatch_lease_active = False
            self._record_uncertain_dispatch(
                permit,
                claimed,
                f"callback等待超过{DISPATCH_CALLBACK_TIMEOUT_SECONDS:.3f}s",
            )
        self._dispatch_lease_active = False
        if not succeeded:
            self._record_uncertain_dispatch(permit, claimed, f"callback异常：{value!r}")
        worker.join(timeout=0.1)
        if worker.is_alive():
            self._fail("callback已返回但本地工作线程未能在有限清理窗口退出")
        self._dispatch_worker = None
        return value

    def claim_dispatch(self, permit: DispatchPermit, dispatch_callback=None, ready_receipt=None):
        """持有状态通道跨进程租约到外层响应ACK验证结束。"""
        if not callable(dispatch_callback):
            self._fail("claim_dispatch必须通过同一串行入口执行dispatch callback")
        with self._lock:
            try:
                with self.channel.consume_lease() as records:
                    self._consume_records_locked(records)
                    now = self._clock()
                    if (
                        type(permit) is not DispatchPermit
                        or permit.owner is not self
                        or permit.controller_id != self._controller_id
                        or permit is not self.pending_permit
                        or self._expected_permit_nonce is None
                        or permit.nonce != self._expected_permit_nonce
                        or self._permit_binding(permit) != self._pending_permit_binding
                        or permit.sequence != self.command_index
                        or permit.session_id != self.expected_session_id
                        or permit.heartbeat_sequence != self.sequence
                    ):
                        self._fail("派发许可nonce、controller/session/命令序号或heartbeat版本无效")
                    age = now - permit.issued_monotonic
                    if not math.isfinite(age) or age < 0.0 or age > HEARTBEAT_FRESHNESS_SECONDS:
                        self._fail(f"派发receipt过期/未来：age={age!r}")
                    self._assert_fresh(now)
                    if self.latest["session_state"] != "idle" or self.latest["active_command_sha256"] is not None:
                        self._fail("claim dispatch时ROSS状态已非idle")
                    if self.job is None or self.job.closed:
                        self._fail("派发前Job Object已关闭")
                    root_handle = self.job.member_handles.get((self.job.root_pid, self.job.root_birth_ticks))
                    if root_handle is None:
                        self._fail("派发前缺少已绑定root身份句柄")
                    try:
                        job_guard._assert_handle_identity(
                            root_handle["handle"],
                            self.job.root_pid,
                            self.job.root_birth_ticks,
                            self.identity,
                        )
                    except BaseException as error:
                        self._fail(f"派发前root HANDLE/PID身份复核失败：{error!r}")
                    if permit.sequence == 0:
                        command = self._verify_dcp_and_command()
                        if command != permit.command or permit.dcp_sha256 != DCP_SHA256 or permit.output_path is not None:
                            self._fail("open_checkpoint命令/DCP SHA在receipt后发生漂移")
                        self._consume_ready_receipt(ready_receipt, permit)
                    elif permit.sequence == 1:
                        if self._output_path is None or self._output_anchor is None:
                            self._fail("bitstream唯一输出目录缺少固定身份锚点")
                        try:
                            self._evidence_anchor.verify_path()
                            self._output_anchor.verify_path()
                        except BaseException as error:
                            self._fail(f"bitstream输出父目录身份/reparse复核失败：{error!r}")
                        if permit.output_path != str(self._output_path) or permit.dcp_sha256 is not None:
                            self._fail("write_bitstream输出路径或DCP字段在receipt后发生漂移")
                        if self._output_path.exists() or self._output_path.is_symlink():
                            self._fail("bitstream单次输出目标已经存在")
                        expected = f"write_bitstream -force {{{self._output_path.as_posix()}}}"
                        if permit.command != expected:
                            self._fail("write_bitstream输出路径与本次唯一目标不符")
                        if ready_receipt is not None:
                            self._fail("READY凭据只能绑定并消费第一条派发")
                    else:
                        self._fail("派发序列越界")
                    actual_sha = hashlib.sha256(permit.command.encode("utf-8")).hexdigest()
                    if actual_sha != permit.command_sha256:
                        self._fail("许可中的命令SHA256不符")
                    receipt = {
                        "kind": "ROSS_DISPATCH_PERMIT",
                        "controller_id": self._controller_id,
                        "permit_nonce": permit.nonce,
                        "session_id": self.expected_session_id,
                        "sequence": permit.sequence,
                        "command": permit.command,
                        "command_sha256": permit.command_sha256,
                        "dcp_sha256": DCP_SHA256 if permit.sequence == 0 else None,
                        "output_path": str(self._output_path) if permit.sequence == 1 else None,
                        "issued_monotonic": permit.issued_monotonic,
                        "claimed_monotonic": now,
                        "mcp_call_required_by_outer_controller": True,
                    }
                    self._expected_permit_nonce = None
                    self._pending_permit_binding = None
                    self.pending_permit = None
                    self.pending_command = {
                        "sequence": permit.sequence,
                        "command": permit.command,
                        "sha256": permit.command_sha256,
                        "claimed_monotonic": now,
                        "active_seen": False,
                    }
                    self.state = "WAIT_COMMAND"
                    self._pending_ack_nonce = permit.nonce
                    try:
                        ack = self._dispatch_with_deadline(dispatch_callback, receipt, permit, now)
                        self._consume_dispatch_ack(ack, permit, now)
                    except BaseException as error:
                        self._dispatch_lease_active = False
                        if isinstance(error, RossJobGuardError):
                            raise
                        self._fail(f"外层单次dispatch callback拒绝/失败：{error!r}")
                    self._pending_ack_nonce = None
                    self._last_ack_binding = self._ack_binding(ack)
                    receipt["acknowledgement"] = {
                        "outcome": ack.outcome,
                        "response_sha256": ack.response_sha256,
                        "acknowledged_monotonic": ack.acknowledged_monotonic,
                    }
                    return receipt
            except RossJobGuardError:
                raise
            except BaseException as error:
                self._fail(f"锁内许可消费/派发callback失败：{error!r}")

    @staticmethod
    def _ack_binding(ack: DispatchAck) -> tuple:
        return (
            ack.owner,
            ack.controller_id,
            ack.permit_nonce,
            ack.session_id,
            ack.sequence,
            ack.command,
            ack.command_sha256,
            ack.output_path,
            ack.dcp_sha256,
            ack.outcome,
            ack.response_sha256,
            ack.acknowledged_monotonic,
        )

    def _consume_dispatch_ack(self, ack: object, permit: DispatchPermit, claimed: float) -> None:
        """消费与permit逐字段绑定、及时且唯一的外层响应ACK。"""
        if type(ack) is not DispatchAck:
            self._fail("外层MCP响应缺少严格绑定的DispatchAck，拒绝报告派发成功")
        if (
            ack.owner is not self
            or ack.controller_id != self._controller_id
            or self._pending_ack_nonce is None
            or ack.permit_nonce != self._pending_ack_nonce
            or ack.permit_nonce != permit.nonce
            or ack.session_id != permit.session_id
            or ack.sequence != permit.sequence
            or ack.command != permit.command
            or ack.command_sha256 != permit.command_sha256
            or ack.output_path != permit.output_path
            or ack.dcp_sha256 != permit.dcp_sha256
            or ack.outcome != "ACCEPTED"
            or type(ack.response_sha256) is not str
            or not SHA256_RE.fullmatch(ack.response_sha256)
        ):
            self._fail("外层MCP ACK身份、命令、输出、DCP、结果或nonce绑定不匹配")
        acknowledged = _finite_time(ack.acknowledged_monotonic, "dispatch_ack_monotonic")
        if acknowledged < claimed:
            self._fail("外层MCP ACK时间早于许可claim")
        now = self._clock()
        if acknowledged > now:
            self._fail("外层MCP ACK时间位于未来")
        if acknowledged - claimed > HANDOFF_LIMIT_SECONDS:
            self._fail("外层MCP响应ACK超过5秒handoff门槛")
        if self._last_ack_binding == self._ack_binding(ack):
            self._fail("外层MCP DispatchAck被重复消费")

    def _consume_ready_receipt(self, ready_receipt, permit) -> None:
        if (
            type(ready_receipt) is not ReadyReceipt
            or ready_receipt.owner is not self
            or ready_receipt.controller_id != self._controller_id
            or ready_receipt is not self.ready_receipt
            or self._ready_nonce is None
            or ready_receipt.nonce != self._ready_nonce
            or self._ready_consumed
            or ready_receipt.session_id != self.expected_session_id
            or ready_receipt.identity_items
            != tuple((field, tuple(self.identity[field]) if field == "cmdline" else self.identity[field]) for field in IDENTITY_FIELDS)
            or ready_receipt.heartbeat_sequence != permit.heartbeat_sequence
            or ready_receipt.job_token is not self._job_ready_token
        ):
            self._fail("READY receipt伪造、跨controller/session、nonce篡改或已消费")
        age = time.monotonic() - ready_receipt.issued_monotonic
        if not math.isfinite(age) or age < 0.0 or age > HEARTBEAT_FRESHNESS_SECONDS:
            self._fail(f"READY receipt过期/未来：age={age!r}")
        try:
            self.job.consume_ready_token(ready_receipt.job_token, self.expected_session_id, self.identity)
        except BaseException as error:
            self._fail(f"Job READY token实际消费失败：{error!r}")
        self._ready_consumed = True

    def process_new_heartbeats(self) -> int:
        """消费已经append+flush的完整记录；每一条都按顺序检查。"""
        with self._lock:
            with self.channel.consume_lease() as records:
                self._consume_records_locked(records)
                return len(records)

    def publish_fixture_or_bridge_heartbeat(self, record: dict) -> int:
        """供外层桥接器写入已按canonical schema组装的观察，不解析原始MCP。"""
        with self._lock:
            self.channel.publish(record)
            return self.process_new_heartbeats()

    def sample_once(self) -> dict:
        """一秒监护采样先落盘再评估资源、成员闭合和新鲜度。"""
        with self._lock:
            return self._sample_once_locked()

    def _sample_once_locked(self) -> dict:
        if self.state in {"FAILED", "STOPPED", "CLOSED"}:
            self._fail(f"终态后拒绝继续采样：{self.state}")
        start = time.monotonic()
        self.process_new_heartbeats()
        self._assert_fresh(time.monotonic())
        no_progress = 0.0
        if self.latest["session_state"] == "active":
            no_progress = time.monotonic() - self.latest["progress_monotonic"]
        sample = self.job.sample(
            self._previous_sample_start,
            self._previous_accounting,
            self._previous_pids,
            self._previous_keys,
        )
        sample["sequence"] = self._last_journal_record_count
        sample["ross_session_id"] = self.expected_session_id
        sample["ross_heartbeat_sequence"] = self.sequence
        sample["ross_status_freshness_seconds"] = time.monotonic() - self.latest["observed_monotonic"]
        sample["supervisor_handoff_seconds"] = time.monotonic() - self.latest["published_monotonic"]
        sample["no_progress_seconds"] = no_progress
        sample["mcp_session_state"] = self.latest["session_state"]
        sample["pending_command_sha256"] = None if self.pending_command is None else self.pending_command["sha256"]
        sample["terminal_event"] = self.latest["event"] == "STOP"
        self.sample_log.publish(sample)
        self._last_journal_record_count += 1
        alerts = self.job.evaluate(sample, no_progress)
        gap = sample["sample_gap_seconds"]
        if gap is not None:
            self.max_sample_gap_seconds = max(self.max_sample_gap_seconds, gap)
            if gap > job_guard.SAMPLE_GAP_LIMIT_SECONDS:
                alerts.append("SAMPLE_GAP_GT_1S")
        if sample["ross_status_freshness_seconds"] > HEARTBEAT_FRESHNESS_SECONDS:
            alerts.append("ROSS_HEARTBEAT_STALE")
        if sample["supervisor_handoff_seconds"] > HANDOFF_LIMIT_SECONDS:
            alerts.append("ROSS_SUPERVISOR_HANDOFF_GT_5S")
        if alerts or sample["uncertainty_count"] != 0:
            self._fail(f"Job监护样本失败：alerts={alerts}, uncertainty={sample['uncertainty']!r}")
        self._previous_sample_start = sample["sample_start_monotonic"]
        self._previous_accounting = sample["accounting_after"]
        self._previous_pids = set(sample["job_pids_after"])
        self._previous_keys = set(self.job.member_handles)
        return sample

    def mark_stop(self, record: dict) -> None:
        """STOP记录必须已落盘、递增且所有受控命令均完成。"""
        self.publish_fixture_or_bridge_heartbeat(record)
        if self.state != "STOPPED":
            self._fail("ROSS STOP未成为终态")

    def verify_terminal(self, timeout_seconds: float = 30.0) -> dict:
        """在STOP之后等待Job成员列表、句柄和root身份句柄全部闭合。"""
        with self._lock:
            if self.state != "STOPPED":
                self._fail("未见ROSS STOP终态，拒绝验收进程树")
            try:
                final = self.job.wait_empty_and_verify(timeout_seconds=timeout_seconds, root_must_exit=True)
            except BaseException as error:
                self._fail(f"ROSS root/Job终态闭合失败：{error!r}")
            if final["job_pids"] or final["active_processes"] != 0 or final["live_members"] or final["unknown_members"]:
                self._fail("终态Job成员集合非空或存在unknown")
            try:
                self.job.close()
                if self._output_anchor is not None:
                    self._output_anchor.close()
                    self._output_anchor = None
                self._evidence_anchor.close()
                self._evidence_anchor = None
            except BaseException as error:
                self._fail(f"终态关闭Job/成员/目录锚点句柄失败：{error!r}")
            self.state = "CLOSED"
            return final

    def abort(self, reason: str) -> None:
        """异常时关闭本候选Job句柄，由KILL_ON_JOB_CLOSE终止本Job成员。"""
        self._fail(reason)

    def metrics(self) -> dict:
        return {
            "max_heartbeat_freshness_seconds": self.max_heartbeat_age,
            "max_supervisor_handoff_seconds": self.max_handoff_seconds,
            "max_sample_start_gap_seconds": self.max_sample_gap_seconds,
            "heartbeat_records": self.sequence + 1,
            "job_samples": self._last_journal_record_count,
            "state": self.state,
            "failure": self.failure,
            "command_index": self.command_index,
            "last_completed_command_sha256": self.last_completed_sha256,
            "bitgen_output_path": None if self._output_path is None else str(self._output_path),
            "ready_token_consumed": self._ready_consumed,
            "pending_permit_nonce": self._expected_permit_nonce is not None,
            "job_cleanup_errors": [] if self.job is None else list(self.job.cleanup_errors),
        }
