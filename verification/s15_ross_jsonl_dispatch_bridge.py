"""为S15 ROSS守护器提供真实外层MCP调用的单次JSONL派发桥。"""
from __future__ import annotations

import hashlib
import json
import math
import queue
import re
import threading
import time
import weakref
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Callable

import s15_ross_job_guard as ross_guard


PROTOCOL = "s15-ross-dispatch-jsonl-v1"
REQUEST_KIND = "ROSS_DISPATCH_PERMIT"
RESPONSE_KIND = "ROSS_DISPATCH_RESULT"
EXECUTE_TOOL = "vivado_execute"
EXECUTE_TOOL_ID = "mcp__vivado_ross__vivado_execute"
MAX_JSONL_BYTES = 8 * 1024 * 1024
GUARD_DEADLINE_SECONDS = float(ross_guard.DISPATCH_CALLBACK_TIMEOUT_SECONDS)
BRIDGE_DEADLINE_SECONDS = min(4.25, GUARD_DEADLINE_SECONDS - 0.5)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_OWNER_PERMIT_LOCK = threading.Lock()
_OWNER_USED_PERMITS = weakref.WeakKeyDictionary()

RECEIPT_FIELDS = frozenset(
    {
        "kind",
        "controller_id",
        "permit_nonce",
        "session_id",
        "sequence",
        "command",
        "command_sha256",
        "dcp_sha256",
        "output_path",
        "issued_monotonic",
        "claimed_monotonic",
        "mcp_call_required_by_outer_controller",
    }
)
WIRE_RECEIPT_FIELDS = frozenset(RECEIPT_FIELDS - {"kind"})
REQUEST_FIELDS = frozenset(
    {"kind", "protocol", "request_id", "tool", "tool_id", "receipt", "arguments"}
)
RESPONSE_FIELDS = frozenset(
    {
        "kind",
        "protocol",
        "request_id",
        "tool",
        "tool_id",
        "receipt",
        "arguments",
        "call_tool_result_json",
        "response_sha256",
    }
)

class DispatchBridgeError(RuntimeError):
    """JSONL派发协议拒绝或外层派发状态不确定。"""


class DispatchTimeout(DispatchBridgeError):
    """单次JSONL派发超过有限等待期限。"""


class DispatchEOF(DispatchBridgeError):
    """单次JSONL通道在收到唯一回执前关闭。"""


@dataclass
class _Transaction:
    """保存唯一待处理回执及其单次响应队列。"""

    request_line: bytes
    request: dict[str, Any]
    response: queue.Queue = field(default_factory=lambda: queue.Queue(maxsize=1))
    served: bool = False
    served_thread_id: int | None = None
    dispatch_claimed: bool = False
    response_delivered: bool = False


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """拒绝重复JSON键，避免不同解析器对同一回执作出不同解释。"""
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DispatchBridgeError(f"JSON对象含重复字段：{key}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    """拒绝JSON标准之外的NaN和Infinity常量。"""
    raise DispatchBridgeError(f"JSON含非标准数值：{value}")


def _parse_jsonl_frame(frame: bytes, frame_name: str) -> dict[str, Any]:
    """解析只含一行、UTF-8编码且不含重复键的JSONL消息。"""
    if type(frame) is not bytes:
        raise DispatchBridgeError(f"{frame_name}必须是UTF-8 JSONL字节")
    if not frame or len(frame) > MAX_JSONL_BYTES:
        raise DispatchBridgeError(f"{frame_name}为空或超过大小上限")
    if not frame.endswith(b"\n") or frame.count(b"\n") != 1 or b"\r" in frame:
        raise DispatchBridgeError(f"{frame_name}必须恰含一条以LF结尾的JSONL记录")
    try:
        text = frame[:-1].decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except DispatchBridgeError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise DispatchBridgeError(f"{frame_name}不是严格UTF-8 JSON：{error}") from error
    if type(value) is not dict:
        raise DispatchBridgeError(f"{frame_name}顶层必须是JSON对象")
    return value


def _jsonl_bytes(value: dict[str, Any]) -> bytes:
    """将经过校验的消息编码为唯一一行UTF-8 JSONL。"""
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        encoded = text.encode("utf-8", errors="strict") + b"\n"
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise DispatchBridgeError(f"JSONL消息不能严格编码：{error}") from error
    if len(encoded) > MAX_JSONL_BYTES:
        raise DispatchBridgeError("JSONL消息超过大小上限")
    return encoded


def _is_sha256(value: object) -> bool:
    """检查小写十六进制SHA256。"""
    return type(value) is str and SHA256_RE.fullmatch(value) is not None


def _strict_json_equal(left: object, right: object) -> bool:
    """递归比较JSON值并要求每个节点的Python类型完全相同。"""
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            _strict_json_equal(left[key], right[key]) for key in left
        )
    if type(left) is list:
        return len(left) == len(right) and all(
            _strict_json_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _claim_owner_permit_once(owner: object, permit_nonce: object) -> None:
    """按guard实例身份跨bridge原子地消费同一permit nonce。"""
    if type(owner) is not ross_guard.RossJobGuardController:
        raise DispatchBridgeError("permit owner不是真实S15 guard controller")
    if type(permit_nonce) is not bytes or len(permit_nonce) != 32:
        raise DispatchBridgeError("跨bridge permit nonce类型或长度错误")
    with _OWNER_PERMIT_LOCK:
        try:
            used_nonces = _OWNER_USED_PERMITS.get(owner)
            if used_nonces is None:
                used_nonces = set()
                _OWNER_USED_PERMITS[owner] = used_nonces
        except TypeError as error:
            raise DispatchBridgeError("guard owner不支持安全的弱身份登记") from error
        if permit_nonce in used_nonces:
            raise DispatchBridgeError("同一guard owner/permit nonce已由另一路径消费")
        used_nonces.add(permit_nonce)


def _finite_number(value: object, field_name: str) -> float:
    """检查receipt中的单调时钟数值，不接受bool或非有限数。"""
    if type(value) not in (int, float) or not math.isfinite(value):
        raise DispatchBridgeError(f"receipt {field_name}不是有限单调时钟数值")
    return float(value)


def _normalize_receipt(receipt: object, expected_sequence: int) -> dict[str, Any]:
    """严格核验guard给出的唯一permit callback receipt。"""
    if type(receipt) is not dict or set(receipt) != RECEIPT_FIELDS:
        raise DispatchBridgeError("ROSS_DISPATCH_PERMIT字段缺失、多余或容器类型错误")
    if receipt["kind"] != REQUEST_KIND:
        raise DispatchBridgeError("permit kind不符")
    if type(receipt["controller_id"]) is not bytes or len(receipt["controller_id"]) != 32:
        raise DispatchBridgeError("controller_id必须是32字节身份值")
    if type(receipt["permit_nonce"]) is not bytes or len(receipt["permit_nonce"]) != 32:
        raise DispatchBridgeError("permit_nonce必须是32字节单次nonce")
    if type(receipt["session_id"]) is not str or not receipt["session_id"]:
        raise DispatchBridgeError("session_id为空或类型错误")
    if type(receipt["sequence"]) is not int or receipt["sequence"] not in (0, 1):
        raise DispatchBridgeError("permit sequence越界或类型错误")
    if receipt["sequence"] != expected_sequence:
        raise DispatchBridgeError("permit sequence重复或乱序")
    if type(receipt["command"]) is not str or not receipt["command"]:
        raise DispatchBridgeError("permit command为空或类型错误")
    if "\n" in receipt["command"] or "\r" in receipt["command"] or "\x00" in receipt["command"]:
        raise DispatchBridgeError("permit command含JSONL控制字符")
    try:
        command_bytes = receipt["command"].encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        raise DispatchBridgeError("permit command不是有效UTF-8文本") from error
    if not _is_sha256(receipt["command_sha256"]):
        raise DispatchBridgeError("command_sha256格式错误")
    if hashlib.sha256(command_bytes).hexdigest() != receipt["command_sha256"]:
        raise DispatchBridgeError("command_sha256与receipt原文不符")
    if receipt["sequence"] == 0:
        if receipt["dcp_sha256"] != ross_guard.DCP_SHA256 or receipt["output_path"] is not None:
            raise DispatchBridgeError("sequence 0的DCP或输出路径绑定不符")
    else:
        if receipt["dcp_sha256"] is not None:
            raise DispatchBridgeError("sequence 1不允许携带DCP SHA")
        if type(receipt["output_path"]) is not str or not receipt["output_path"]:
            raise DispatchBridgeError("sequence 1必须绑定唯一输出路径")
    issued = _finite_number(receipt["issued_monotonic"], "issued_monotonic")
    claimed = _finite_number(receipt["claimed_monotonic"], "claimed_monotonic")
    if claimed < issued:
        raise DispatchBridgeError("receipt claim时间早于permit签发时间")
    if receipt["mcp_call_required_by_outer_controller"] is not True:
        raise DispatchBridgeError("permit未要求外层MCP调用")
    return dict(receipt)


def _verify_live_guard_owner(owner: object, receipt: dict[str, Any]) -> None:
    """确认receipt仍对应guard callback线程正在消费的真实permit。"""
    if type(owner) is not ross_guard.RossJobGuardController:
        raise DispatchBridgeError("owner不是当前S15 RossJobGuardController实例")
    if (
        type(owner._controller_id) is not bytes
        or type(owner.expected_session_id) is not str
        or type(owner._pending_ack_nonce) is not bytes
        or type(owner.command_index) is not int
        or type(owner.state) is not str
    ):
        raise DispatchBridgeError("guard owner的活动身份字段类型不符")
    if (
        not _strict_json_equal(owner._controller_id, receipt["controller_id"])
        or not _strict_json_equal(owner.expected_session_id, receipt["session_id"])
        or not _strict_json_equal(owner._pending_ack_nonce, receipt["permit_nonce"])
        or owner._dispatch_lease_active is not True
        or owner.state != "WAIT_COMMAND"
        or not _strict_json_equal(owner.command_index, receipt["sequence"])
    ):
        raise DispatchBridgeError("receipt未绑定当前guard活动session/permit/派发租约")
    pending = owner.pending_command
    pending_fields = {"sequence", "command", "sha256", "claimed_monotonic", "active_seen"}
    if type(pending) is not dict or set(pending) != pending_fields:
        raise DispatchBridgeError("guard没有唯一严格格式的活动命令")
    if (
        type(pending["sequence"]) is not int
        or type(pending["command"]) is not str
        or type(pending["sha256"]) is not str
        or type(pending["active_seen"]) is not bool
    ):
        raise DispatchBridgeError("guard活动命令字段类型不符")
    if (
        not _strict_json_equal(pending["sequence"], receipt["sequence"])
        or not _strict_json_equal(pending["command"], receipt["command"])
        or not _strict_json_equal(pending["sha256"], receipt["command_sha256"])
        or not _strict_json_equal(pending["claimed_monotonic"], receipt["claimed_monotonic"])
        or pending["active_seen"] is not False
    ):
        raise DispatchBridgeError("receipt命令与guard当前唯一活动命令不符")
    if receipt["sequence"] == 0:
        if (
            type(owner._command_texts) is not list
            or len(owner._command_texts) != 1
            or owner._command_texts[0] != receipt["command"]
            or receipt["dcp_sha256"] != ross_guard.DCP_SHA256
            or receipt["output_path"] is not None
        ):
            raise DispatchBridgeError("sequence 0命令或冻结DCP没有匹配guard批准内容")
    else:
        output_path = owner._output_path
        if output_path is None:
            raise DispatchBridgeError("sequence 1缺少guard批准的bitstream输出路径")
        expected_output = str(output_path)
        expected_command = f"write_bitstream -force {{{output_path.as_posix()}}}"
        if (
            receipt["output_path"] != expected_output
            or receipt["command"] != expected_command
            or receipt["dcp_sha256"] is not None
        ):
            raise DispatchBridgeError("sequence 1命令或输出路径没有匹配guard批准内容")


def _wire_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """将进程内byte身份以十六进制原样表示在线路receipt中。"""
    return {
        "controller_id": receipt["controller_id"].hex(),
        "permit_nonce": receipt["permit_nonce"].hex(),
        "session_id": receipt["session_id"],
        "sequence": receipt["sequence"],
        "command": receipt["command"],
        "command_sha256": receipt["command_sha256"],
        "dcp_sha256": receipt["dcp_sha256"],
        "output_path": receipt["output_path"],
        "issued_monotonic": receipt["issued_monotonic"],
        "claimed_monotonic": receipt["claimed_monotonic"],
        "mcp_call_required_by_outer_controller": True,
    }


def _receipt_from_wire(value: object, expected_sequence: int) -> dict[str, Any]:
    """严格解析线路receipt并还原进程内身份字节。"""
    if type(value) is not dict or set(value) != WIRE_RECEIPT_FIELDS:
        raise DispatchBridgeError("线路receipt字段缺失或多余")
    controller_hex = value["controller_id"]
    nonce_hex = value["permit_nonce"]
    if type(controller_hex) is not str or type(nonce_hex) is not str:
        raise DispatchBridgeError("线路receipt身份字段类型错误")
    if re.fullmatch(r"[0-9a-f]{64}", controller_hex) is None or re.fullmatch(r"[0-9a-f]{64}", nonce_hex) is None:
        raise DispatchBridgeError("线路receipt身份字段不是规范32字节十六进制")
    receipt = {"kind": REQUEST_KIND, **value}
    receipt["controller_id"] = bytes.fromhex(controller_hex)
    receipt["permit_nonce"] = bytes.fromhex(nonce_hex)
    return _normalize_receipt(receipt, expected_sequence)


def build_dispatch_request(receipt: object, expected_sequence: int) -> tuple[dict[str, Any], bytes]:
    """按guard receipt生成严格、唯一的vivado_execute请求行。"""
    normalized = _normalize_receipt(receipt, expected_sequence)
    arguments = {"session_id": normalized["session_id"], "command": normalized["command"]}
    request = {
        "kind": REQUEST_KIND,
        "protocol": PROTOCOL,
        "request_id": normalized["permit_nonce"].hex(),
        "tool": EXECUTE_TOOL,
        "tool_id": EXECUTE_TOOL_ID,
        "receipt": _wire_receipt(normalized),
        "arguments": arguments,
    }
    return request, _jsonl_bytes(request)


def _validate_request(value: object, expected_sequence: int | None = None) -> dict[str, Any]:
    """核验broker准备派发给MCP的单条permit请求。"""
    if type(value) is not dict or set(value) != REQUEST_FIELDS:
        raise DispatchBridgeError("ROSS_DISPATCH_PERMIT请求字段缺失或多余")
    if value["kind"] != REQUEST_KIND or value["protocol"] != PROTOCOL:
        raise DispatchBridgeError("permit请求kind或协议版本不符")
    if value["tool"] != EXECUTE_TOOL or value["tool_id"] != EXECUTE_TOOL_ID:
        raise DispatchBridgeError("permit请求不是指定的vivado_execute工具")
    receipt_seq = value.get("receipt", {}).get("sequence") if type(value.get("receipt")) is dict else None
    if expected_sequence is None:
        if type(receipt_seq) is not int:
            raise DispatchBridgeError("permit请求sequence格式错误")
        expected_sequence = receipt_seq
    receipt = _receipt_from_wire(value["receipt"], expected_sequence)
    expected_request_id = receipt["permit_nonce"].hex()
    if type(value["request_id"]) is not str or value["request_id"] != expected_request_id:
        raise DispatchBridgeError("request_id与permit nonce不符")
    expected_arguments = {"session_id": receipt["session_id"], "command": receipt["command"]}
    if type(value["arguments"]) is not dict or value["arguments"] != expected_arguments:
        raise DispatchBridgeError("MCP arguments没有逐字段等于permit receipt")
    canonical_request, _ = build_dispatch_request(receipt, expected_sequence)
    if value != canonical_request:
        raise DispatchBridgeError("permit请求不是规范线路表示")
    return value


def _assert_json_value(value: object, path: str = "result") -> None:
    """只接受无损JSON树，拒绝隐式对象转字符串或非标准数值。"""
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise DispatchBridgeError(f"{path}包含非有限数值")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _assert_json_value(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise DispatchBridgeError(f"{path}含非字符串JSON字段名")
            _assert_json_value(item, f"{path}.{key}")
        return
    raise DispatchBridgeError(f"{path}含不可无损编码的对象：{type(value).__name__}")


def _call_tool_result_json(result: object) -> bytes:
    """把完整CallToolResult序列化为实际在线路上传送并计算SHA的UTF-8字节。"""
    if isinstance(result, Mapping):
        payload = dict(result)
    else:
        model_dump = getattr(result, "model_dump", None)
        if not callable(model_dump):
            raise DispatchBridgeError("MCP返回值不是CallToolResult映射或支持model_dump的对象")
        try:
            payload = model_dump(mode="json", by_alias=True, exclude_none=False)
        except BaseException as error:
            raise DispatchBridgeError(f"CallToolResult不能导出完整JSON：{error!r}") from error
    if type(payload) is not dict or type(payload.get("content")) is not list:
        raise DispatchBridgeError("MCP响应缺少完整CallToolResult.content列表")
    if "isError" in payload and type(payload["isError"]) is not bool:
        raise DispatchBridgeError("CallToolResult.isError不是布尔值")
    _assert_json_value(payload)
    try:
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode(
            "utf-8", errors="strict"
        )
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise DispatchBridgeError(f"完整CallToolResult不能编码为UTF-8 JSON：{error}") from error
    if len(encoded) > MAX_JSONL_BYTES // 2:
        raise DispatchBridgeError("完整CallToolResult超过线路结果大小上限")
    return encoded


def encode_dispatch_result(
    request: dict[str, Any],
    actual_tool_id: str,
    actual_arguments: Mapping[str, Any],
    call_tool_result: object,
) -> bytes:
    """把外层实际MCP调用及其完整CallToolResult封装成一条回执行。"""
    request = _validate_request(request)
    result_bytes = _call_tool_result_json(call_tool_result)
    response = {
        "kind": RESPONSE_KIND,
        "protocol": PROTOCOL,
        "request_id": request["request_id"],
        "tool": request["tool"],
        "tool_id": actual_tool_id,
        "receipt": request["receipt"],
        "arguments": dict(actual_arguments),
        "call_tool_result_json": result_bytes.decode("utf-8"),
        "response_sha256": hashlib.sha256(result_bytes).hexdigest(),
    }
    return _jsonl_bytes(response)


def handle_one_jsonl_request(
    request_line: bytes,
    invoke_mcp: Callable[[str, dict[str, Any]], object],
    bridge: JsonlDispatchBridge | None = None,
) -> bytes:
    """处理一条bridge permit，并只经绑定broker的pending transaction调用外层MCP。"""
    request = _validate_request(_parse_jsonl_frame(request_line, "permit请求"))
    if not callable(invoke_mcp):
        raise DispatchBridgeError("外层MCP调用器不可调用")
    if type(bridge) is not JsonlDispatchBridge:
        raise DispatchBridgeError("直接处理permit必须提供真实JsonlDispatchBridge owner")
    bridge._authorize_outer_invocation(request)
    result = bridge._dispatch_via_bound_broker(request, invoke_mcp)
    arguments = dict(request["arguments"])
    return encode_dispatch_result(request, request["tool_id"], arguments, result)


def _validate_dispatch_response(
    response_line: bytes,
    request: dict[str, Any],
) -> tuple[dict[str, Any], bytes, dict[str, Any]]:
    """逐字段比对回执与permit，并核验完整MCP结果内容和字节哈希。"""
    response = _parse_jsonl_frame(response_line, "MCP结果回执")
    if set(response) != RESPONSE_FIELDS:
        raise DispatchBridgeError("MCP结果回执字段缺失或多余")
    if response["kind"] != RESPONSE_KIND or response["protocol"] != PROTOCOL:
        raise DispatchBridgeError("MCP结果回执kind或协议版本不符")
    for field_name in ("request_id", "tool", "tool_id", "receipt", "arguments"):
        if not _strict_json_equal(response[field_name], request[field_name]):
            raise DispatchBridgeError(f"MCP结果回执{field_name}与唯一permit不符")
    raw_result = response["call_tool_result_json"]
    if type(raw_result) is not str:
        raise DispatchBridgeError("回执没有完整CallToolResult JSON文本")
    try:
        result_bytes = raw_result.encode("utf-8", errors="strict")
    except UnicodeEncodeError as error:
        raise DispatchBridgeError("CallToolResult回执不是有效UTF-8") from error
    if not _is_sha256(response["response_sha256"]):
        raise DispatchBridgeError("response_sha256格式错误")
    digest = hashlib.sha256(result_bytes).hexdigest()
    if digest != response["response_sha256"]:
        raise DispatchBridgeError("response_sha256与完整CallToolResult UTF-8字节不符")
    try:
        result = json.loads(
            raw_result,
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except DispatchBridgeError:
        raise
    except (json.JSONDecodeError, UnicodeError) as error:
        raise DispatchBridgeError(f"CallToolResult文本不是严格JSON：{error}") from error
    if type(result) is not dict or type(result.get("content")) is not list:
        raise DispatchBridgeError("回执不是完整CallToolResult对象")
    if "isError" in result and type(result["isError"]) is not bool:
        raise DispatchBridgeError("CallToolResult.isError不是布尔值")
    if result.get("isError") is True:
        raise DispatchBridgeError("MCP CallToolResult标记isError=true")
    return response, result_bytes, result


class JsonlDispatchBroker:
    """在线程间用单请求、单回执JSONL服务外层实际MCP工具调用。"""

    def __init__(self):
        self._lock = threading.Lock()
        self._requests: queue.Queue = queue.Queue(maxsize=1)
        self._pending: _Transaction | None = None
        self._next_sequence = 0
        self._used_request_ids: set[str] = set()
        self._closed = False
        self._poisoned = False
        self._bridge: JsonlDispatchBridge | None = None

    def _bind_bridge(self, bridge: JsonlDispatchBridge) -> None:
        """将broker一次性绑定到创建它的唯一真实bridge。"""
        if type(bridge) is not JsonlDispatchBridge:
            raise DispatchBridgeError("broker只能绑定真实JsonlDispatchBridge")
        with self._lock:
            if self._bridge is not None and self._bridge is not bridge:
                self._poisoned = True
                raise DispatchBridgeError("broker已绑定其他bridge owner")
            if self._pending is not None or self._closed or self._poisoned:
                self._poisoned = True
                raise DispatchBridgeError("broker状态不允许绑定bridge owner")
            self._bridge = bridge

    def exchange(self, request_line: bytes, timeout_seconds: float) -> bytes:
        """由guard callback提交唯一JSONL请求并等待结果行，超时后永久封闭。"""
        request = _validate_request(_parse_jsonl_frame(request_line, "permit请求"), self._next_sequence)
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise DispatchTimeout("JSONL派发期限无效")
        with self._lock:
            if self._closed:
                raise DispatchEOF("外层JSONL broker已EOF关闭")
            if self._poisoned:
                raise DispatchBridgeError("外层JSONL broker已失败封闭")
            if self._pending is not None:
                raise DispatchBridgeError("外层JSONL broker已有未完成请求")
            if request["request_id"] in self._used_request_ids:
                self._poisoned = True
                raise DispatchBridgeError("permit request_id重复")
            transaction = _Transaction(request_line, request)
            self._pending = transaction
            try:
                self._requests.put_nowait(transaction)
            except queue.Full as error:
                self._poisoned = True
                raise DispatchBridgeError("JSONL broker请求队列非空，拒绝重排") from error
        try:
            response = transaction.response.get(timeout=float(timeout_seconds))
        except queue.Empty as error:
            with self._lock:
                self._poisoned = True
            raise DispatchTimeout("等待MCP JSONL回执超时，禁止重发") from error
        if isinstance(response, BaseException):
            with self._lock:
                self._poisoned = True
            raise response
        if type(response) is not bytes:
            with self._lock:
                self._poisoned = True
            raise DispatchBridgeError("broker回执不是JSONL字节")
        return response

    def serve_one(
        self,
        invoke_mcp: Callable[[str, dict[str, Any]], object],
        timeout_seconds: float = BRIDGE_DEADLINE_SECONDS,
    ) -> dict[str, Any]:
        """由外层总控调用一次：读permit、精确调用MCP并送回完整CallToolResult。"""
        if not callable(invoke_mcp):
            raise DispatchBridgeError("外层MCP调用器不可调用")
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise DispatchTimeout("broker等待期限无效")
        with self._lock:
            if self._bridge is None:
                self._poisoned = True
                raise DispatchBridgeError("broker没有绑定真实JsonlDispatchBridge，拒绝读取/派发MCP命令")
            if self._closed:
                raise DispatchEOF("外层JSONL broker已EOF关闭")
            if self._poisoned:
                raise DispatchBridgeError("外层JSONL broker已失败封闭")
        try:
            transaction = self._requests.get(timeout=float(timeout_seconds))
        except queue.Empty as error:
            raise DispatchTimeout("未在期限内收到ROSS_DISPATCH_PERMIT") from error
        if transaction is None:
            raise DispatchEOF("外层JSONL broker在permit前EOF")
        with self._lock:
            if self._closed or self._poisoned or transaction is not self._pending:
                self._poisoned = True
                raise DispatchBridgeError("permit请求已经过期、重复或不再是唯一待处理项")
            if transaction.served:
                self._poisoned = True
                raise DispatchBridgeError("permit请求已被重复读取")
            try:
                request = _validate_request(
                    _parse_jsonl_frame(transaction.request_line, "permit请求"), self._next_sequence
                )
            except BaseException:
                self._poisoned = True
                raise
            if request != transaction.request:
                self._poisoned = True
                raise DispatchBridgeError("排队的permit JSONL与待处理对象不一致")
            if request["request_id"] in self._used_request_ids:
                self._poisoned = True
                raise DispatchBridgeError("permit request_id重复或乱序")
            transaction.served = True
            transaction.served_thread_id = threading.get_ident()
        try:
            response_line = handle_one_jsonl_request(
                transaction.request_line,
                invoke_mcp,
                bridge=self._bridge,
            )
        except BaseException as error:
            with self._lock:
                self._poisoned = True
                try:
                    transaction.response.put_nowait(error)
                except queue.Full:
                    pass
            raise
        with self._lock:
            if self._closed or self._poisoned or self._pending is not transaction:
                self._poisoned = True
                raise DispatchBridgeError("MCP返回时permit已超时或JSONL通道已关闭；结果不确认、不重发")
            transaction.response_delivered = True
            try:
                transaction.response.put_nowait(response_line)
            except queue.Full as error:
                self._poisoned = True
                raise DispatchBridgeError("同一permit已有回执，拒绝重复送达") from error
        return request

    def _invoke_current_pending(
        self,
        bridge: JsonlDispatchBridge,
        request: dict[str, Any],
        invoke_mcp: Callable[[str, dict[str, Any]], object],
    ) -> object:
        """与close/abort共用锁，线性化当前serve线程对pending命令的唯一派发权。"""
        if type(bridge) is not JsonlDispatchBridge or not callable(invoke_mcp):
            raise DispatchBridgeError("最终派发claim缺少真实bridge或MCP调用器")
        with self._lock:
            transaction = self._pending
            if (
                self._closed
                or self._poisoned
                or self._bridge is not bridge
                or transaction is None
                or self._pending is not transaction
                or not transaction.served
                or transaction.served_thread_id != threading.get_ident()
                or transaction.dispatch_claimed
                or not _strict_json_equal(request, transaction.request)
            ):
                self._poisoned = True
                raise DispatchBridgeError("broker关闭、状态漂移或重复claim，拒绝调用MCP")
            transaction.dispatch_claimed = True
        return invoke_mcp(request["tool_id"], dict(request["arguments"]))

    def finish(self, request_id: str, accepted: bool) -> None:
        """仅在bridge验证完整回执后释放本次请求并允许下一序号。"""
        with self._lock:
            transaction = self._pending
            if transaction is None or transaction.request["request_id"] != request_id:
                self._poisoned = True
                raise DispatchBridgeError("finish没有对应的唯一活动permit")
            if accepted is not True:
                self._poisoned = True
                self._pending = None
                return
            if not transaction.served or not transaction.dispatch_claimed or not transaction.response_delivered:
                self._poisoned = True
                raise DispatchBridgeError("permit尚未完成原子派发claim、一次MCP调用和回执送达")
            self._used_request_ids.add(request_id)
            self._next_sequence += 1
            self._pending = None

    def abort(self) -> None:
        """永久封闭失败桥，丢弃迟到回执且不再接受重发。"""
        with self._lock:
            self._poisoned = True
            transaction = self._pending
            if transaction is not None and not transaction.response_delivered:
                try:
                    transaction.response.put_nowait(DispatchEOF("dispatch桥已封闭"))
                except queue.Full:
                    pass

    def close(self) -> None:
        """关闭单会话broker并唤醒等待中的permit callback。"""
        with self._lock:
            self._closed = True
            transaction = self._pending
            if transaction is not None and not transaction.response_delivered:
                try:
                    transaction.response.put_nowait(DispatchEOF("JSONL broker EOF"))
                except queue.Full:
                    pass
            try:
                self._requests.put_nowait(None)
            except queue.Full:
                pass


class JsonlDispatchBridge:
    """把guard callback receipt变成实际MCP回执绑定的DispatchAck。"""

    def __init__(
        self,
        owner: object,
        broker: JsonlDispatchBroker,
        clock: Callable[[], float] = time.monotonic,
        timeout_seconds: float = BRIDGE_DEADLINE_SECONDS,
    ):
        if type(owner) is not ross_guard.RossJobGuardController or not callable(getattr(broker, "exchange", None)):
            raise ValueError("bridge需要guard owner和JSONL broker")
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds):
            raise ValueError("bridge timeout必须是有限数值")
        if timeout_seconds <= 0 or timeout_seconds >= GUARD_DEADLINE_SECONDS:
            raise ValueError("bridge timeout必须严格短于guard五秒期限")
        if not callable(clock):
            raise ValueError("bridge clock不可调用")
        self.owner = owner
        self.broker = broker
        self.clock = clock
        self.timeout_seconds = float(timeout_seconds)
        self.expected_sequence = 0
        self._active_lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._poisoned = False
        self._dispatch_active = False
        self._invocation_claimed = False
        self._active_request: dict[str, Any] | None = None
        self.last_call_tool_result_json: str | None = None
        self.last_call_tool_result: dict[str, Any] | None = None
        bind_bridge = getattr(self.broker, "_bind_bridge", None)
        if callable(bind_bridge):
            bind_bridge(self)

    def _authorize_outer_invocation(self, request: dict[str, Any]) -> None:
        """只准当前callback已发布的准确permit通过一次外层MCP派发。"""
        try:
            with self._state_lock:
                if self._poisoned:
                    raise DispatchBridgeError("bridge已失败封闭")
                if not self._dispatch_active or self._active_request is None:
                    raise DispatchBridgeError("当前没有活动permit callback")
                canonical = _validate_request(request, self.expected_sequence)
                if not _strict_json_equal(canonical, self._active_request):
                    raise DispatchBridgeError("外层MCP请求不是当前callback发布的准确permit")
                receipt = _receipt_from_wire(canonical["receipt"], self.expected_sequence)
                _verify_live_guard_owner(self.owner, receipt)
                if self._invocation_claimed:
                    raise DispatchBridgeError("当前permit已被另一路径领取，拒绝重复调用MCP")
                _claim_owner_permit_once(self.owner, receipt["permit_nonce"])
                self._invocation_claimed = True
        except BaseException:
            self._poisoned = True
            abort = getattr(self.broker, "abort", None)
            if callable(abort):
                abort()
            raise

    def _dispatch_via_bound_broker(
        self,
        request: dict[str, Any],
        invoke_mcp: Callable[[str, dict[str, Any]], object],
    ) -> object:
        """要求当前bridge经唯一绑定broker的活动pending事务完成原子派发。"""
        try:
            with self._state_lock:
                if (
                    self._poisoned
                    or not self._dispatch_active
                    or self._active_request is None
                    or not self._invocation_claimed
                    or not _strict_json_equal(request, self._active_request)
                ):
                    raise DispatchBridgeError("handler请求没有对应的bridge活动permit")
            if type(self.broker) is not JsonlDispatchBroker or self.broker._bridge is not self:
                raise DispatchBridgeError("handler未绑定真实JsonlDispatchBroker owner")
            return self.broker._invoke_current_pending(self, request, invoke_mcp)
        except BaseException:
            self._poisoned = True
            abort = getattr(self.broker, "abort", None)
            if callable(abort):
                abort()
            raise

    def __call__(self, receipt: object) -> ross_guard.DispatchAck:
        """一次性接收guard receipt并返回逐字段绑定的DispatchAck。"""
        if not self._active_lock.acquire(blocking=False):
            raise DispatchBridgeError("bridge已有未完成的permit请求")
        request_id: str | None = None
        try:
            if self._poisoned:
                raise DispatchBridgeError("bridge已失败封闭，不允许重发")
            normalized = _normalize_receipt(receipt, self.expected_sequence)
            _verify_live_guard_owner(self.owner, normalized)
            request, request_line = build_dispatch_request(normalized, self.expected_sequence)
            request_id = request["request_id"]
            with self._state_lock:
                if self._dispatch_active:
                    raise DispatchBridgeError("bridge已有活动permit callback")
                self._dispatch_active = True
                self._invocation_claimed = False
                self._active_request = request
            if self.timeout_seconds >= GUARD_DEADLINE_SECONDS:
                raise DispatchBridgeError("bridge期限不短于guard callback期限")
            exchange_result: queue.Queue = queue.Queue(maxsize=1)

            def exchange_once() -> None:
                try:
                    exchange_result.put((True, self.broker.exchange(request_line, self.timeout_seconds)))
                except BaseException as error:
                    exchange_result.put((False, error))

            exchange_worker = threading.Thread(
                target=exchange_once,
                name=f"s15-jsonl-exchange-{normalized['sequence']}",
                daemon=True,
            )
            exchange_worker.start()
            try:
                succeeded, exchange_value = exchange_result.get(timeout=self.timeout_seconds)
            except queue.Empty as error:
                raise DispatchTimeout("JSONL派发桥超过有限等待期限，禁止重发") from error
            if not succeeded:
                raise exchange_value
            exchange_worker.join(timeout=0.05)
            if exchange_worker.is_alive():
                raise DispatchBridgeError("JSONL exchange返回后工作线程未在有限窗口退出")
            response_line = exchange_value
            response, result_bytes, result = _validate_dispatch_response(response_line, request)
            acknowledged = self.clock()
            acknowledged_float = _finite_number(acknowledged, "acknowledged_monotonic")
            if acknowledged_float < float(normalized["claimed_monotonic"]):
                raise DispatchBridgeError("MCP回执接收时间早于permit claim")
            ack = ross_guard.DispatchAck(
                owner=self.owner,
                controller_id=normalized["controller_id"],
                permit_nonce=normalized["permit_nonce"],
                session_id=normalized["session_id"],
                sequence=normalized["sequence"],
                command=normalized["command"],
                command_sha256=normalized["command_sha256"],
                output_path=normalized["output_path"],
                dcp_sha256=normalized["dcp_sha256"],
                outcome="ACCEPTED",
                response_sha256=hashlib.sha256(result_bytes).hexdigest(),
                acknowledged_monotonic=acknowledged_float,
            )
            finish = getattr(self.broker, "finish", None)
            if callable(finish):
                finish(request_id, True)
            self.expected_sequence += 1
            with self._state_lock:
                self._dispatch_active = False
                self._active_request = None
            self.last_call_tool_result_json = response["call_tool_result_json"]
            self.last_call_tool_result = result
            return ack
        except BaseException:
            self._poisoned = True
            abort = getattr(self.broker, "abort", None)
            if callable(abort):
                abort()
            else:
                finish = getattr(self.broker, "finish", None)
                if callable(finish) and request_id is not None:
                    try:
                        finish(request_id, False)
                    except BaseException:
                        pass
            raise
        finally:
            self._active_lock.release()


STATUS_SUPERVISION_BLOCKER = (
    "当前已观测的ROSS vivado_status字段没有活动/完成命令的session级ID、命令SHA、许可序号或服务器单调"
    "进度计数；因此此bridge只证明单次vivado_execute结果，不产生持续监督heartbeat或命令完成证明。"
)
