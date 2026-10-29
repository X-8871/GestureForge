"""阶段6动作 ACK 边界：只把已产生的回执交给纯状态核心。"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import threading
from typing import Any

from .s6_core import GestureInteractionCore


class ActionReceiptBoundaryError(RuntimeError):
    """ACK 边界拒绝无法安全归属或排序的输入。"""


class ReceiptClockError(ActionReceiptBoundaryError):
    """调用方未提供有效的显式单调接收时刻。"""


class ConflictingActionAckError(ActionReceiptBoundaryError):
    """同一 action_id 收到不同业务回执。"""


class UntrackedActionAckError(ActionReceiptBoundaryError):
    """核心已见 action_id，但边界没有其原始回执指纹。"""


class ActionReceiptBoundary:
    """对 ACK 做同 ID 冲突检查，再调用核心既有 ``note_action_ack``。

    这是可离线验证的内部边界，不规定真实 transport、动作后端或显示观测接口。
    必须在核心处理首个 ACK 前创建，并通过本边界的 ``reset_session`` 复位；
    这样可保留核心复位时仍保留的全局 action_id 去重历史。每次 ACK 处理前，
    本边界会校验核心 ACK 日志与已见 ID 账本没有被其他调用方改写或追加。
    所有 ACK 字段均作为业务内容比较；每次接收时刻单独通过 ``received_at_ns``
    传入，不进入 ACK 指纹。这里不读取系统时钟，也不生成 ACTION_SUBMITTED /
    ACTION_EFFECTIVE。该检查能发现串行旁路调用，但无法锁住核心公开方法，不能
    消除与其他 ``note_action_ack`` 调用并发写入的竞态；集成时本边界必须是 ACK
    日志与计数的唯一写入入口。
    """

    def __init__(self, core: GestureInteractionCore) -> None:
        if not isinstance(core, GestureInteractionCore):
            raise TypeError("core 必须是 GestureInteractionCore 实例")
        if core.action_log or core._seen_action_ack_ids:
            raise ActionReceiptBoundaryError(
                "边界必须在核心处理首个 ACK 前创建；已有 ACK 历史不能安全重建业务指纹"
            )
        self._core = core
        self._business_by_action_id: dict[str, bytes] = {}
        self._last_received_at_ns: int | None = None
        self._lock = threading.Lock()
        self.delivery_log: list[dict[str, Any]] = []
        self._expected_core_history = self._snapshot_core_action_log()

    @property
    def last_received_at_ns(self) -> int | None:
        """返回最近一次通过时钟检查的 transport 接收时刻。"""
        return self._last_received_at_ns

    @staticmethod
    def _canonical_business_ack(ack: dict[str, Any]) -> bytes:
        """按完整 ACK 对象生成确定指纹；不接受非 JSON 值或非有限数。"""
        if type(ack) is not dict:
            raise ActionReceiptBoundaryError("ack 必须是 dict")

        def validate_json_value(value: Any, path: str) -> None:
            if value is None or type(value) in (bool, int, str):
                return
            if type(value) is float:
                if not math.isfinite(value):
                    raise ActionReceiptBoundaryError(f"{path} 不得包含 NaN 或无穷值")
                return
            if type(value) is list:
                for index, item in enumerate(value):
                    validate_json_value(item, f"{path}[{index}]")
                return
            if type(value) is dict:
                for key, item in value.items():
                    if type(key) is not str:
                        raise ActionReceiptBoundaryError(
                            f"{path} 的对象键必须全部为字符串"
                        )
                    validate_json_value(item, f"{path}.{key}")
                return
            raise ActionReceiptBoundaryError(
                f"{path} 含非 JSON 值类型 {type(value).__name__}"
            )

        try:
            validate_json_value(ack, "ack")
        except RecursionError as exc:
            raise ActionReceiptBoundaryError("ack 包含循环引用或嵌套过深") from exc
        try:
            text = json.dumps(
                ack,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            return text.encode("utf-8")
        except (TypeError, ValueError, RecursionError, UnicodeError) as exc:
            raise ActionReceiptBoundaryError(
                f"ack 不是有限、可规范序列化的 JSON 业务对象：{exc}"
            ) from exc

    def _snapshot_core_action_log(
        self,
        rows: list[dict[str, Any]] | None = None,
    ) -> tuple[int, bytes]:
        """给核心 ACK 日志做完整、顺序敏感的快照指纹。"""
        if rows is None:
            rows = self._core.action_log
        if type(rows) is not list:
            raise UntrackedActionAckError("核心 action_log 类型异常；拒绝继续处理")
        digest = hashlib.sha256()
        try:
            for row in rows:
                encoded = self._canonical_business_ack(row)
                digest.update(len(encoded).to_bytes(8, "big"))
                digest.update(encoded)
        except (ActionReceiptBoundaryError, OverflowError) as exc:
            raise UntrackedActionAckError(
                f"核心 action_log 含不可核验记录：{exc}"
            ) from exc
        return len(rows), digest.digest()

    @staticmethod
    def _core_log_business_payload(row: dict[str, Any]) -> dict[str, Any]:
        """移除核心仅在重复日志上添加的内部标记。"""
        payload = dict(row)
        if payload.get("duplicate_ack_ignored") is True:
            payload.pop("duplicate_ack_ignored")
        return payload

    def _assert_core_history_unchanged(self) -> tuple[int, bytes]:
        """发现 ACK 旁路、账本改写或日志截断时，在本边界调用核心前拒绝。"""
        rows = self._core.action_log
        if type(rows) is not list:
            raise UntrackedActionAckError("核心 action_log 类型异常；拒绝继续处理")
        expected_count, _ = self._expected_core_history
        if len(rows) > expected_count:
            for row in rows[expected_count:]:
                if not isinstance(row, dict):
                    continue
                action_id = row.get("action_id")
                if not isinstance(action_id, str) or action_id not in self._business_by_action_id:
                    continue
                try:
                    row_fingerprint = self._canonical_business_ack(
                        self._core_log_business_payload(row)
                    )
                except ActionReceiptBoundaryError:
                    row_fingerprint = None
                qualifier = (
                    "相同业务内容"
                    if row_fingerprint == self._business_by_action_id[action_id]
                    else "不同或不可核验的业务内容"
                )
                raise UntrackedActionAckError(
                    f"核心 action_log 出现边界外的已跟踪 action_id {action_id!r}：{qualifier}"
                )
            raise UntrackedActionAckError(
                "核心 action_log 出现边界外 ACK 记录；拒绝继续处理"
            )
        if len(rows) < expected_count:
            raise UntrackedActionAckError(
                "核心 action_log 被截断或复位未经过边界；拒绝继续处理"
            )

        actual_history = self._snapshot_core_action_log(rows)
        if actual_history != self._expected_core_history:
            raise UntrackedActionAckError(
                "核心 action_log 中既有 ACK 记录被修改；拒绝继续处理"
            )
        seen_ids = self._core._seen_action_ack_ids
        if type(seen_ids) is not set or seen_ids != set(self._business_by_action_id):
            raise UntrackedActionAckError(
                "核心已见 action_id 账本与边界账本不一致；拒绝继续处理"
            )
        return actual_history

    def _verify_own_core_append(
        self,
        before: tuple[int, bytes],
        expected_entry: dict[str, Any],
        expected_seen_ids: set[str],
    ) -> tuple[int, bytes]:
        """确认核心调用只追加了本次预期记录，避免吸收并发旁路写入。"""
        rows = self._core.action_log
        before_count = before[0]
        if type(rows) is not list or len(rows) != before_count + 1:
            raise UntrackedActionAckError(
                "核心 ACK 调用期间 action_log 出现非预期追加或截断；拒绝确认交付"
            )
        prefix = self._snapshot_core_action_log(rows[:before_count])
        if prefix != before:
            raise UntrackedActionAckError(
                "核心 ACK 调用期间既有 action_log 被并发改写；拒绝确认交付"
            )
        expected_payload = self._canonical_business_ack(expected_entry)
        actual_payload = self._canonical_business_ack(
            self._core_log_business_payload(rows[-1])
        )
        if actual_payload != expected_payload:
            raise UntrackedActionAckError(
                "核心 ACK 调用追加的 action_log 与本次边界输入不一致"
            )
        seen_ids = self._core._seen_action_ack_ids
        if type(seen_ids) is not set or seen_ids != expected_seen_ids:
            raise UntrackedActionAckError(
                "核心 ACK 调用后的已见 ID 账本含非预期变更"
            )
        return self._snapshot_core_action_log(rows)

    def reset_session(self, session_id: str) -> dict[str, Any]:
        """经边界复位核心，并保留 ACK 指纹与核心全局去重账本。"""
        with self._lock:
            self._assert_core_history_unchanged()
            log = self._core.reset_session(session_id)
            self._expected_core_history = self._snapshot_core_action_log()
            self._assert_core_history_unchanged()
            return copy.deepcopy(log)

    def deliver(
        self,
        ack: dict[str, Any],
        *,
        received_at_ns: int | None = None,
    ) -> dict[str, Any]:
        """验证传输时钟与重复 ACK 一致性，然后调用核心；不代表动作已生效。

        核心日志/账本的旁路核验在接收时钟更新前执行，检测到旁路时本调用不变更
        核心或边界状态。有效接收时刻会在核心校验 ACK 前记录；若核心拒绝业务
        输入，边界时钟仍表示已接收该传输事件。相同 ID、相同 ACK 会交由核心按
        既有幂等规则记录为重复；同 ID 业务字段冲突则在调用核心前拒绝。无 ID
        的抑制回执仍按核心既有规则逐条处理。
        """
        with self._lock:
            before = self._assert_core_history_unchanged()
            if type(received_at_ns) is not int or received_at_ns < 0:
                raise ReceiptClockError(
                    "received_at_ns 必须由调用方显式提供为非负整数纳秒"
                )
            if (self._last_received_at_ns is not None
                    and received_at_ns < self._last_received_at_ns):
                raise ReceiptClockError(
                    "received_at_ns 早于此前接收时刻；拒绝倒序 transport 事件"
                )

            canonical = self._canonical_business_ack(ack)
            if "duplicate_ack_ignored" in ack:
                raise ActionReceiptBoundaryError(
                    "duplicate_ack_ignored 是核心日志保留字段，不可由 ACK 输入提供"
                )
            owned_ack = json.loads(canonical.decode("utf-8"))
            action_id = owned_ack.get("action_id")
            suppression = owned_ack.get("suppression")
            prior: bytes | None = None
            conflict = False

            if suppression is None and isinstance(action_id, str) and action_id.strip():
                prior = self._business_by_action_id.get(action_id)
                if prior is not None and prior != canonical:
                    conflict = True
                if prior is None and action_id in self._core._seen_action_ack_ids:
                    raise UntrackedActionAckError(
                        f"核心已记录 action_id {action_id!r}，但边界无其业务指纹"
                    )

            # 收窄直接调用核心的竞态窗口；更强的并发互斥需核心本身提供共享锁。
            before = self._assert_core_history_unchanged()
            self._last_received_at_ns = received_at_ns
            if conflict:
                raise ConflictingActionAckError(
                    f"action_id {action_id!r} 的重复 ACK 业务字段冲突；未调用核心"
                )

            expected_seen_ids = set(self._business_by_action_id)
            if suppression is None and prior is None and isinstance(action_id, str) and action_id.strip():
                expected_seen_ids.add(action_id)

            core_log = self._core.note_action_ack(owned_ack)
            expected_entry = owned_ack
            if suppression is not None:
                status = "CORE_SUPPRESSION_ACK_RECORDED"
            elif core_log.get("duplicate_ack_ignored"):
                status = "CORE_ACK_DUPLICATE_IGNORED"
            else:
                status = "CORE_ACK_RECORDED"
            observed_after = self._verify_own_core_append(
                before,
                expected_entry,
                expected_seen_ids,
            )
            if status == "CORE_ACK_RECORDED" and isinstance(action_id, str) and action_id.strip():
                self._business_by_action_id[action_id] = canonical
            self._expected_core_history = observed_after

            delivery = {
                "status": status,
                "received_at_ns": received_at_ns,
                "ack_sha256": hashlib.sha256(canonical).hexdigest(),
                "core_log": copy.deepcopy(core_log),
            }
            self.delivery_log.append(copy.deepcopy(delivery))
            return delivery
