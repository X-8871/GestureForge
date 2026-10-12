"""为S15离线ROSS状态适配与一次性bitgen许可提供故障关闭门禁。"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import re
import secrets
import time
from pathlib import Path

import s15_job_guard as job_guard


SCHEMA = "s15-ross-canonical-observation-v1"
EXPECTED_RUN_ID = "S15-T17-G1-ROSS-GUARD-20261013-r01"
EXPECTED_EVIDENCE_RELATIVE = "report/evidence/S2B-T17/s15_ross_guard_20261013_r01"
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
NO_PROGRESS_LIMIT_SECONDS = job_guard.NO_PROGRESS_LIMIT_SECONDS
STOP_EVENTS = frozenset({"STOP"})
RUN_EVENTS = frozenset({"HEARTBEAT"})
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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

    def publish(self, record: dict) -> None:
        """先追加完整行并flush，再由消费者解析和评估。"""
        raw = json.dumps(record, ensure_ascii=False, separators=(",", ":"), allow_nan=True)
        with self.path.open("ab", buffering=0) as stream:
            stream.write((raw + "\n").encode("utf-8"))
            os.fsync(stream.fileno())

    def read_new(self) -> list[dict]:
        """只返回完整JSONL行；部分尾行留待下一轮，不读取未来字节。"""
        data = self.path.read_bytes()
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
        self._read_count = len(complete)
        return result


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


class ReadyReceipt:
    """READY后单个控制器实例的不可替代能力对象。"""

    __slots__ = ("owner", "nonce", "session_id", "identity", "issued_monotonic", "used")

    def __init__(self, owner, session_id, identity, issued_monotonic):
        self.owner = owner
        self.nonce = secrets.token_bytes(32)
        self.session_id = session_id
        self.identity = dict(identity)
        self.issued_monotonic = issued_monotonic
        self.used = False


class DispatchPermit:
    """由控制器生成、只可消费一次且限时有效的精确命令许可。"""

    __slots__ = (
        "owner",
        "nonce",
        "sequence",
        "command",
        "command_sha256",
        "issued_monotonic",
        "heartbeat_sequence",
        "used",
    )

    def __init__(self, owner, sequence, command, issued_monotonic, heartbeat_sequence):
        self.owner = owner
        self.nonce = secrets.token_bytes(32)
        self.sequence = sequence
        self.command = command
        self.command_sha256 = hashlib.sha256(command.encode("utf-8")).hexdigest()
        self.issued_monotonic = issued_monotonic
        self.heartbeat_sequence = heartbeat_sequence
        self.used = False


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
        if provided.resolve(strict=True) != self.expected_evidence_root.resolve(strict=True):
            raise RossGuardError("证据根目录不是本候选唯一批准目录")
        self.evidence_root = self.expected_evidence_root.resolve(strict=True)
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
        if self.job is not None and not self.job.closed:
            try:
                self.job.close()
            except BaseException as close_error:
                self.failure += f"；关闭自有Job失败：{close_error!r}"
        raise RossJobGuardError(message)

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
            self.ready_receipt = ReadyReceipt(self, self.expected_session_id, self.identity, now)
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
        if self.state not in {"READY_OPEN", "READY_BITGEN"} or self.pending_command is not None:
            self._fail(f"当前状态不允许派发：{self.state}")
        now = time.monotonic()
        self._assert_fresh(now)
        if self.latest["session_state"] != "idle" or self.latest["active_command_sha256"] is not None:
            self._fail("派发前ROSS会话不处于idle")
        if self.command_index == 0:
            command = self._command_texts[0]
        elif self.command_index == 1:
            if self._output_directory is None:
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
                self._output_directory = output_dir
                self._output_path = output
            command = f"write_bitstream -force {{{self._output_path.as_posix()}}}"
            if not command.startswith("write_bitstream -force {") or not command.endswith("}"):
                self._fail("bitstream Tcl命令生成不符合固定模板")
        else:
            self._fail("命令序列超出两条批准命令")
        permit = DispatchPermit(self, self.command_index, command, now, self.sequence)
        self.pending_permit = permit
        return permit

    def claim_dispatch(self, permit: DispatchPermit) -> dict:
        """烧掉receipt并只返回本轮精确命令，不调用MCP。"""
        now = time.monotonic()
        if (
            type(permit) is not DispatchPermit
            or permit.owner is not self
            or permit is not self.pending_permit
            or permit.used
            or permit.sequence != self.command_index
            or permit.heartbeat_sequence != self.sequence
        ):
            self._fail("派发许可不是当前session的唯一未用receipt")
        age = now - permit.issued_monotonic
        if not math.isfinite(age) or age < 0.0 or age > HEARTBEAT_FRESHNESS_SECONDS:
            self._fail(f"派发receipt过期/未来：age={age!r}")
        self._assert_fresh(now)
        if self.latest["session_state"] != "idle" or self.latest["active_command_sha256"] is not None:
            self._fail("claim dispatch时ROSS状态已非idle")
        if permit.sequence == 0:
            command = self._verify_dcp_and_command()
            if command != permit.command:
                self._fail("open_checkpoint命令在receipt后发生漂移")
        elif permit.sequence == 1:
            if self._output_path is None or self._output_path.exists() or self._output_path.is_symlink():
                self._fail("bitstream单次输出目标已存在或丢失")
            expected = f"write_bitstream -force {{{self._output_path.as_posix()}}}"
            if permit.command != expected:
                self._fail("write_bitstream输出路径与本次唯一目标不符")
        else:
            self._fail("派发序列越界")
        actual_sha = hashlib.sha256(permit.command.encode("utf-8")).hexdigest()
        if actual_sha != permit.command_sha256:
            self._fail("许可中的命令SHA256不符")
        permit.used = True
        self.pending_command = {
            "sequence": permit.sequence,
            "command": permit.command,
            "sha256": permit.command_sha256,
            "claimed_monotonic": now,
            "active_seen": False,
        }
        self.state = "WAIT_COMMAND"
        return {
            "kind": "ROSS_DISPATCH_PERMIT",
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

    def process_new_heartbeats(self) -> int:
        """消费已经append+flush的完整记录；每一条都按顺序检查。"""
        records = self.channel.read_new()
        for record in records:
            self._accept_record(record)
        return len(records)

    def publish_fixture_or_bridge_heartbeat(self, record: dict) -> int:
        """供外层桥接器写入已按canonical schema组装的观察，不解析原始MCP。"""
        self.channel.publish(record)
        return self.process_new_heartbeats()

    def sample_once(self) -> dict:
        """一秒监护采样先落盘再评估资源、成员闭合和新鲜度。"""
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
        if self.state != "STOPPED":
            self._fail("未见ROSS STOP终态，拒绝验收进程树")
        try:
            final = self.job.wait_empty_and_verify(timeout_seconds=timeout_seconds, root_must_exit=True)
        except BaseException as error:
            self._fail(f"ROSS root/Job终态闭合失败：{error!r}")
        if final["job_pids"] or final["active_processes"] != 0 or final["live_members"] or final["unknown_members"]:
            self._fail("终态Job成员集合非空或存在unknown")
        self.job.close()
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
        }
