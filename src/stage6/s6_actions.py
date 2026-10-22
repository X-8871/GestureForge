"""阶段6 动作执行层（S6-B，与纯核心隔离）。

职责（对应 S6-A H-2/H-8 与 CDX-20261022-012 §3.2）：

* 接收核心给出的**动作请求**，向显示侧提交"设置到具名状态"的幂等动作；
* 返回 ``success/fail`` 与 ``observed/unobserved`` 两类结果，分别对应
  ``ACTION_SUBMITTED`` 与 ``ACTION_EFFECTIVE``（提交成功 ≠ 实际生效）；
* 日志保留 ``action_id`` 与来源帧（``source_frame_id``/``trigger_frame_id``），
  并对同一 ``(action_type, target_id)`` 在 ``T6-A02`` 内的重复提交去重，防止重复发送；
* 本层**不读摄像头/墙钟/HDMI 寄存器**：生效与否由外部观测（阶段5 回执）注入。

确定性测试用 ``OutcomePolicy`` 注入失败/未观察/重复回执场景（B28），
策略只影响本层回执，不改变核心判定。
"""

from __future__ import annotations

from typing import Any

from .s6_params import ParamPack

OUT_SUBMITTED = "ACTION_SUBMITTED"
OUT_EFFECTIVE = "ACTION_EFFECTIVE"
OUT_FAILED = "ACTION_FAILED"
OUT_UNOBSERVED = "ACTION_UNOBSERVED"
SUP_DEDUP = "S_DEDUP"


class OutcomePolicy:
    """确定性回执策略（测试注入用）。

    * ``fail_attempts``：第 N 次提交（1 起）返回 ``fail``；
    * ``unobserved_attempts``：第 N 次提交提交成功但未观察到生效；
    * ``duplicate_ack_attempts``：第 N 次提交额外产生一次重复 ACK（不改变计数）；
    """

    def __init__(
        self,
        fail_attempts: list[int] | None = None,
        unobserved_attempts: list[int] | None = None,
        duplicate_ack_attempts: list[int] | None = None,
    ) -> None:
        self.fail_attempts = set(fail_attempts or [])
        self.unobserved_attempts = set(unobserved_attempts or [])
        self.duplicate_ack_attempts = set(duplicate_ack_attempts or [])

    @property
    def is_empty(self) -> bool:
        return not (self.fail_attempts or self.unobserved_attempts or self.duplicate_ack_attempts)


class ActionLayer:
    """动作执行层：幂等提交 + 回执 + 去重日志。"""

    def __init__(self, pack: ParamPack, outcome_policy: OutcomePolicy | None = None) -> None:
        self.pack = pack
        self.a02_ns = pack.threshold_bundle()["a02_ns"]
        self.policy = outcome_policy or OutcomePolicy()
        self.active_display_state: str | None = None
        self.active_channel: str | None = None
        self.active_target_id: str | None = None
        self.next_action_id = 1
        self.attempt_count = 0
        self.records: list[dict[str, Any]] = []
        self.last_submit_ns_by_key: dict[tuple[str, str], int] = {}

    # ------------------------------------------------------------------ 观测
    def is_active(self, action_type: str, target_id: str) -> bool:
        """幂等性判定：同一 (action_type,target_id) 已处于该状态。"""
        if action_type == "A_SWITCH_UI":
            return self.active_display_state == target_id
        if action_type == "A_SWITCH_CHANNEL":
            return self.active_channel == target_id
        return self.active_target_id == target_id

    def _apply(self, action_type: str, target_id: str) -> None:
        if action_type == "A_SWITCH_UI":
            self.active_display_state = target_id
        elif action_type == "A_SWITCH_CHANNEL":
            self.active_channel = target_id
        self.active_target_id = target_id

    # ------------------------------------------------------------------ 提交
    def submit(self, request: dict[str, Any], t_now_ns: int) -> dict[str, Any]:
        """提交一次动作请求，返回回执记录（供核心 :meth:`note_action_ack` 消费）。"""
        action_type = str(request["action_type"])
        target_id = str(request["target_id"])
        key = (action_type, target_id)
        self.attempt_count += 1
        attempt = self.attempt_count

        record: dict[str, Any] = {
            "action_id": None,
            "action_type": action_type,
            "target_id": target_id,
            "class_id": request.get("class_id"),
            "class_name": request.get("class_name"),
            "source_frame_id": request.get("source_frame_id"),
            "trigger_frame_id": request.get("trigger_frame_id"),
            "acquisition_id": request.get("acquisition_id"),
            "t_trigger_ns": request.get("t_trigger_ns"),
            "t_submit_ns": None,
            "t_effective_ns": None,
            "submit_result": None,
            "effective_result": None,
            "already_active_before": self.is_active(action_type, target_id),
            "suppression": None,
            "duplicate_ack": False,
            "visible_state_change": False,
        }

        last_submit = self.last_submit_ns_by_key.get(key)
        if last_submit is not None and (t_now_ns - last_submit) < self.a02_ns:
            record["suppression"] = SUP_DEDUP
            record["reason"] = (
                f"同一 (action_type,target_id) 在 T6-A02={self.a02_ns} ns 内重复提交：抑制并记录"
            )
            self.records.append(record)
            return record

        record["action_id"] = f"ACT-{self.next_action_id:04d}"
        self.next_action_id += 1
        record["t_submit_ns"] = t_now_ns

        if attempt in self.policy.fail_attempts:
            record["submit_result"] = "fail"
            record["effective_result"] = "unobserved"
            record["reason"] = "执行层返回 fail：不产生 ACTION_SUBMITTED 成功、不更新冷却锚点"
            self.records.append(record)
            return record

        record["submit_result"] = "success"
        self.last_submit_ns_by_key[key] = t_now_ns
        already_active = record["already_active_before"]
        if attempt in self.policy.unobserved_attempts:
            record["effective_result"] = "unobserved"
            record["reason"] = "提交成功但未观察到生效：按 NOT_RUN 单列，不计成功（H-8）"
        else:
            self._apply(action_type, target_id)
            record["effective_result"] = "observed"
            record["t_effective_ns"] = t_now_ns
            record["visible_state_change"] = not already_active
            record["reason"] = (
                "提交成功且观察到目标状态：计入 ACTION_EFFECTIVE"
                + ("（原本已处于该状态：幂等，无额外可见变化）" if already_active else "")
            )
        if attempt in self.policy.duplicate_ack_attempts:
            record["duplicate_ack"] = True
            record["reason"] += "；收到重复 ACK（不重复计数）"
        self.records.append(record)
        return record

    # ------------------------------------------------------------------ 汇总
    def summary(self) -> dict[str, Any]:
        submitted = sum(1 for row in self.records if row["submit_result"] == "success")
        effective = sum(1 for row in self.records if row["effective_result"] == "observed")
        failed = sum(1 for row in self.records if row["submit_result"] == "fail")
        unobserved = sum(
            1 for row in self.records
            if row["submit_result"] == "success" and row["effective_result"] == "unobserved"
        )
        dedup = sum(1 for row in self.records if row["suppression"] == SUP_DEDUP)
        return {
            "attempts": self.attempt_count,
            "action_submitted": submitted,
            "action_effective": effective,
            "action_failed": failed,
            "action_unobserved": unobserved,
            "dedup_suppressed": dedup,
            "visible_state_changes": sum(1 for row in self.records if row["visible_state_change"]),
            "final_display_state": self.active_display_state,
            "final_channel": self.active_channel,
        }