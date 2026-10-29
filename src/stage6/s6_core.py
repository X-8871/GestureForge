"""阶段6 交互状态机纯核心（S6-B，契约 S6A-G0-v1.6，对应 S6-A r07）。

设计边界（对应 S6-A 硬不变量 H-1/H-3/H-7 与 CDX-20261022-012 §3）：

* 输入：一条事件（结果/超时/错误/丢帧/时钟推进）＋ 显式单调时间 ＋ ``session_id``；
  核心不读摄像头、不读系统墙钟、不读 HDMI/硬件寄存器，也不 import 任何 IO 模块。
* 输出：状态转移、动作**请求**、抑制事件与逐帧日志；动作的提交与回执由
  :mod:`src.stage6.s6_actions` 的独立动作层负责，核心只登记 ``t_last_submit``。
* 阈值全部来自 :class:`src.stage6.s6_params.ParamPack`（行为表 JSON，保持 PENDING_APPROVAL）；
  本模块不出现任何阶段6 阈值字面量。

本实现逐条对齐 v1.6 契约（关键点：

* H-4：窗口**序列**由 ``state ∈ {OK, NO_HAND}``、``stale=false``、非重复、非倒序的结果推进；
  **匹配计数只由 WINDOW_MATCH 推进**；``NO_HAND`` 推进时间与结果计数、不推进匹配计数、
  不得完成稳定窗口。
* H-10：冷却为**全局门**——``t_now − t_last_submit < T6-K01`` 时任何状态/任何获取都不得提交；
  展示状态 ``COOLDOWN`` 提前退出不解除该门；被抑制或失败的尝试不更新锚点。
* M3/M10 绑定：``M3`` 只按 ``WINDOW_MATCH`` 计帧（低分目标不得进入 STABLE）；
  ``M10`` 只按 ``TARGET_CONTINUES`` 判丢失（低分但几何连续仍维持）。
* STABLE 锁存（``stable_latching``，U6-16）：进入 STABLE 后不因窗口中断/分数下跌/抖动耗尽
  退回 ``CANDIDATE``；离开 STABLE 只有 M2（异常）/M10（丢失）/M5（触发，且本帧为窗口推进帧）。
* 一次获取只触发一次（``ONCE_PER_ACQUISITION``）；二次触发只允许来自新的获取且门已结束。

实现决策集中记录在 :meth:`GestureInteractionCore.decision_notes`。
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from typing import Any

from .s6_params import ParamPack

# ------------------------------------------------------------------ 事件与输出常量
EV_FRAME_RESULT = "E_FRAME_RESULT"
EV_FRAME_TIMEOUT = "E_FRAME_TIMEOUT"
EV_FRAME_ERROR = "E_FRAME_ERROR"
EV_FRAME_DROPPED = "E_FRAME_DROPPED"
EV_FRAME_DUPLICATE = "E_FRAME_DUPLICATE"
EV_FRAME_CONFLICT = "E_FRAME_CONFLICT"
EV_TICK = "E_TICK"


SUP_COOLDOWN = "S_COOLDOWN"
SUP_TARGET_HELD = "S_TARGET_HELD"
SUP_JITTER = "S_JITTER_TOLERATED"
SUP_WINDOW_TIMEOUT = "S_WINDOW_TIMEOUT"
# 动作层 ACK 的 suppression 只允许 ActionLayer 实际输出的 S_DEDUP。
ACTION_ACK_SUPPRESSIONS = frozenset({"S_DEDUP"})

NON_ADVANCING_KINDS = (EV_FRAME_TIMEOUT, EV_FRAME_ERROR, EV_FRAME_DROPPED)

#: 判定核心使用的期望契约版本（可被构造参数覆盖，但不允许静默跟随上游改版）。
EXPECTED_CONTRACT_VERSION = "S6A-G0-v1.8"


class CoreInputError(RuntimeError):
    """输入不满足核心契约（调用方按输入错误处理，退出码 2）。"""


def _finite(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        return False


def _is_ns_timestamp(value: Any) -> bool:
    """纳秒时间戳按整数解释，拒绝 bool 与浮点近似值。"""
    return isinstance(value, int) and not isinstance(value, bool)


def _stable_json_value(value: Any, *, integers_as_hex: bool = False) -> Any:
    """把事件值转为类型稳定、键顺序稳定的 JSON 值。"""
    if isinstance(value, float):
        return {"$float64": value.hex()}
    if isinstance(value, dict):
        if all(isinstance(key, str) for key in value):
            return {
                key: _stable_json_value(value[key], integers_as_hex=integers_as_hex)
                for key in sorted(value)
            }
        ordered = sorted(value.items(), key=lambda item: (type(item[0]).__name__, repr(item[0])))
        return {"$mapping": [[_stable_json_value(key, integers_as_hex=integers_as_hex),
                              _stable_json_value(item, integers_as_hex=integers_as_hex)]
                             for key, item in ordered]}
    if isinstance(value, list):
        return {"$list": [_stable_json_value(item, integers_as_hex=integers_as_hex)
                           for item in value]}
    if isinstance(value, tuple):
        return {"$tuple": [_stable_json_value(item, integers_as_hex=integers_as_hex)
                            for item in value]}
    if isinstance(value, int) and not isinstance(value, bool) and integers_as_hex:
        return {"$int_hex": format(value, "x")}
    if value is None or isinstance(value, (str, bool, int)):
        return value
    return {"$unsupported_type": f"{type(value).__module__}.{type(value).__qualname__}",
            "$repr": repr(value)}


def _business_frame_digest(event: dict[str, Any]) -> str:
    """按 B22 计算业务内容身份，并排除已核验不影响重复帧处理的上下文。

    ``session_id``/``frame_id`` 是比较作用域与身份键，不属于同一帧的载荷；
    ``t_input_ns`` 是接收时刻；年龄字段只写入日志；``dropped_frames`` 仅在
    新帧的缺帧统计中读取，而重复帧分支先于该统计，因此这些字段不改变重复帧结果。
    ``kind``、``state``、``stale``、检测内容以及其他事件字段均保留在指纹中。
    """
    transport_fields = {
        "session_id", "frame_id", "t_input_ns", "age_result_ns", "age_frame_ns",
        "dropped_frames",
    }
    business_fields = {key: value for key, value in event.items() if key not in transport_fields}
    canonical_value = _stable_json_value(business_fields)
    try:
        canonical = json.dumps(
            canonical_value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except ValueError:
        # 大整数的十进制转换可能超过 Python JSON 的位数上限；用十六进制重试，
        # 保证 B22 仍能区分原始业务内容，再由 B19 将非法分数计为 INVALID。
        canonical = json.dumps(
            _stable_json_value(business_fields, integers_as_hex=True),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _safe_repr(value: Any) -> str:
    """为异常输入生成不会因超大整数而再次失败的简短描述。"""
    try:
        return repr(value)
    except Exception:  # noqa: BLE001
        if isinstance(value, int) and not isinstance(value, bool):
            return f"<int:{value.bit_length()} bits>"
        return f"<{type(value).__module__}.{type(value).__qualname__}>"


class GestureInteractionCore:
    """纯核心状态机：一条事件进，状态/动作请求/日志出。"""

    #: 实现决策（行为表未逐字规定处的取舍，供独立评审逐条核对）
    decision_notes = (
        "D1: 获取帧（首次选为该目标的那一帧）若满足 WINDOW_MATCH 条件（score ≥ T6-P02、无前序窗口帧则跳过位移检查）"
        "即计为第 1 个 WINDOW_MATCH 帧；窗口起点 = 该帧的显式输入时刻。",
        "D2: 抖动容忍只累积不满足 WINDOW_MATCH 的**窗口推进帧**；达到 T6-J01+1 立即重置窗口证据"
        "（帧计数归零、窗口起点清空），容忍期内保留原有帧计数。",
        "D3: 目标切换（新目标 != 当前目标）视为当前获取结束：清空稳定窗口证据、分配新的 acquisition_id，"
        "并重新按 §8 选择目标；切换后不继承旧目标的窗口。",
        "D4: 异常/丢失/触发均按 v1.6 求值序 P1(M2/M13) → P2(M10) → P3(状态推进) → P4(M1) → P5(M12)，"
        "同一帧首次命中即停。",
        "D5: 时间条件使用显式输入时刻；E_TICK 只推进时间，用于「无新结果但时间持续前进」。",
        "D6: 语义上无法由核心判定的未知场景（合法五类内的误识别）不做拒绝判定（H-6）；"
        "class_id ∉ {0..4} 按 E_FRAME_INVALID 处理并计入异常。",
        "D7（N-05/BLK-r02-1/BLK-r03-1，已按实测修正）：**凡结束一次获取的转移都分配新的 acquisition_id**——"
        "M11（丢失确认→IDLE）、M4（抖动超时→IDLE）、M8（COOLDOWN→IDLE 目标丢失出口）、M2（进入 UNKNOWN_RECOVER）、"
        "M12（恢复出口）与目标切换（D3）各 +1；M13 只是恢复态内再入，不结束获取、不递增；"
        "会话/重启复位（RESET）由 _init_state 归零；M1 建立候选不递增。同一获取内 M5 至多触发一次（B11/B15）；"
        "动作记录、逐帧日志与 action_ack 日志都带该 id，可由交付证据逐获取核对。",
        "D8（修复前已知偏差）：IDLE 可保留 current_target；M10 修复已在任意有目标状态求值。",
        "D9（N-04/NB-04 登记）：§4 的 transition_candidates / S_CONFLICT_RESOLVED 未实现——每帧只输出单一 transition；"
        "相关常量与分支已移除，并已在 limitations_not_executed.json 的 not_implemented 中登记（NB-04）。",
    )

    def __init__(self, pack: ParamPack) -> None:
        self.pack = pack
        self.th = pack.threshold_bundle()
        version = pack.data.get("artifact_version")
        if version != EXPECTED_CONTRACT_VERSION:
            raise CoreInputError(
                f"契约版本不符：核心按 {EXPECTED_CONTRACT_VERSION} 编写，实际 {version!r}"
            )
        self.session_id: str | None = None
        self._init_state()

    # ------------------------------------------------------------------ 会话与内部状态
    def reset_session(self, session_id: str) -> dict[str, Any]:
        """全量复位并返回 B25 显式复位日志，保留全局时间与冷却锚点。"""
        previous_session_id = self.session_id
        previous_state = self.state
        self._init_state()
        self.session_id = session_id
        log: dict[str, Any] = {
            "session_id": session_id,
            "previous_session_id": previous_session_id,
            "frame_id": None,
            "event_kind": "E_SESSION_RESET_SUSPECTED",
            "input_state": None,
            "from_state": previous_state,
            "to_state": self.state,
            "transition": "RESET",
            "reason": "显式会话复位：全量复位到 IDLE（B25）",
            "timers": {
                "last_t_ns": self.last_t_ns,
                "t_last_submit_ns": self.t_last_submit_ns,
                "jitter_frames": self.jitter_frames,
                "jitter_exhausted": self.jitter_exhausted,
            },
            "suppression_events": [],
            "action_id": None,
            "trigger_frame_id": None,
            "t_submit_ns": None,
            "t_effective_ns": None,
            "window_complete_ns": None,
            "warmup": False,
        }
        return self._finish(log)

    def _init_state(self) -> None:
        """初始化会话状态，保留全局时间锚、冷却锚与 ACK 幂等记录。"""
        last_t_ns = getattr(self, "last_t_ns", None)
        t_last_submit_ns = getattr(self, "t_last_submit_ns", None)
        seen_action_ack_ids = getattr(self, "_seen_action_ack_ids", set()).copy()
        self.state = "IDLE"
        self.counters = {
            "invalid": 0, "error": 0, "dropped": 0, "timeout": 0, "stale": 0, "false_actions": 0,
            "no_hand_frames": 0, "unknown_class_frames": 0, "no_hand_with_detections": 0,
            "ok_frames": 0,
            "duplicate_frames": 0, "conflict_frames": 0,
            "out_of_order_frames": 0, "missing_frames": 0,
            "action_submitted": 0, "action_effective": 0, "unobserved": 0,
        }
        self.last_frame_id: int | None = None
        self.last_frame_business_sha256: str | None = None
        self.last_t_ns: int | None = last_t_ns
        self.current_target: dict[str, Any] | None = None
        self.acquisition_id = 0
        self.acquisition_triggered = False
        self.t_last_submit_ns: int | None = t_last_submit_ns
        self.t_last_target_continues_ns: int | None = None
        self.continues_false_streak = 0
        self.candidate_streak = 0
        self.candidate_dwell_start_ns: int | None = None
        self.window_match_count = 0
        self.window_start_ns: int | None = None
        self.window_last_match_center: tuple[float, float] | None = None
        self.jitter_frames = 0
        self.jitter_exhausted = False
        self.window_complete_ns: int | None = None
        self.legal_streak = 0
        self.step_anomaly = False
        self.anomaly_history: deque[int] = deque(maxlen=self.th["u00_w"])
        self.result_history: list[str] = []
        self.action_log: list[dict[str, Any]] = []
        self._seen_action_ack_ids: set[str] = seen_action_ack_ids
        self.suppressions: list[str] = []

    # ------------------------------------------------------------------ 几何
    @staticmethod
    def _center(box: list[float]) -> tuple[float, float]:
        return ((float(box[0]) + float(box[2])) / 2.0, (float(box[1]) + float(box[3])) / 2.0)

    @classmethod
    def _disp(cls, a: list[float], b: list[float]) -> float:
        ax, ay = cls._center(a)
        bx, by = cls._center(b)
        return max(abs(ax - bx), abs(ay - by))

    @staticmethod
    def _iou(a: list[float], b: list[float]) -> float:
        x1 = max(float(a[0]), float(b[0]))
        y1 = max(float(a[1]), float(b[1]))
        x2 = min(float(a[2]), float(b[2]))
        y2 = min(float(a[3]), float(b[3]))
        inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area_a = max(0.0, float(a[2]) - float(a[0])) * max(0.0, float(a[3]) - float(a[1]))
        area_b = max(0.0, float(b[2]) - float(b[0])) * max(0.0, float(b[3]) - float(b[1]))
        union = area_a + area_b - inter
        return 0.0 if union <= 0.0 else inter / union

    def _target_continues_for(self, target: dict[str, Any] | None, det: dict[str, Any]) -> bool:
        """TARGET_CONTINUES：同类别 且（IoU ≥ T6-P03 或 归一化中心位移 ≤ T6-P04）；不含 score。"""
        if target is None:
            return False
        if int(det["class_id"]) != int(target["class_id"]):
            return False
        return (
            self._iou(target["xyxy"], det["xyxy"]) >= self.th["p03"]
            or self._disp(target["xyxy"], det["xyxy"]) <= self.th["p04"]
        )

    def _target_continues(self, det: dict[str, Any]) -> bool:
        return self._target_continues_for(self.current_target, det)

    # ------------------------------------------------------------------ 输入校验与选择
    def _validate(self, event: dict[str, Any]) -> str | None:
        dets = event.get("detections") or []
        if not isinstance(dets, list):
            return "detections 非列表"
        if len(dets) > self.th["boxes_max"]:
            return f"框数 {len(dets)} 超过 {self.th['boxes_max']}"
        for det in dets:
            if not isinstance(det, dict):
                return "检测项非对象"
            class_id = det.get("class_id")
            if isinstance(class_id, bool) or not isinstance(class_id, int):
                return f"class_id 非整数：{class_id!r}"
            if class_id not in self.th["class_ids"]:
                return f"class_id 越界：{class_id}"
            if not _finite(det.get("score")):
                return f"score 非 finite：{_safe_repr(det.get('score'))}"
            if "source_order" in det:
                source_order = det["source_order"]
                if (type(source_order) is not int
                        or not 0 <= source_order <= 0x7FFFFFFF):
                    return f"source_order 非法：{_safe_repr(source_order)}"
            box = det.get("xyxy")
            if not isinstance(box, (list, tuple)) or len(box) != 4 or not all(_finite(v) for v in box):
                return f"xyxy 非法：{box!r}"
            x1, y1, x2, y2 = (float(v) for v in box)
            if not (0.0 <= x1 <= x2 <= 1.0 and 0.0 <= y1 <= y2 <= 1.0):
                return f"xyxy 越界或非规范化：{box!r}"
        return None

    def _select(self, dets: list[dict[str, Any]], log: dict[str, Any]) -> dict[str, Any] | None:
        """§8 多框选择：维持优先（TARGET_CONTINUES）→ 分数优先（≥ T6-P01）→ 平票按 source_order。"""
        if self.current_target is not None:
            continuing = [det for det in dets if self._target_continues(det)]
            if continuing:
                det = max(continuing, key=lambda item: float(item["score"]))
                higher_other = [
                    other for other in dets
                    if float(other["score"]) > float(det["score"])
                    and int(other["class_id"]) != int(det["class_id"])
                ]
                if higher_other:
                    self.suppressions.append(SUP_TARGET_HELD)
                    log["suppression_events"].append(SUP_TARGET_HELD)
                    log["held_candidates"] = [
                        {"class_id": int(other["class_id"]), "score": float(other["score"])}
                        for other in higher_other
                    ]
                return det
        eligible = [det for det in dets if float(det["score"]) >= self.th["p01"]]
        if not eligible:
            return None
        best_score = max(float(det["score"]) for det in eligible)
        tied = [det for det in eligible if float(det["score"]) == best_score]
        if len(tied) > 1:
            tied.sort(key=lambda det: (int(det.get("source_order", 0)), int(det["class_id"])))
            log["tie_resolved"] = "source_order"
        tied.sort(key=lambda det: int(det.get("source_order", 0)))
        return tied[0]

    # ------------------------------------------------------------------ 窗口与证据
    def _clear_window_evidence(self) -> None:
        self.window_match_count = 0
        self.window_start_ns = None
        self.window_last_match_center = None
        self.jitter_frames = 0
        self.jitter_exhausted = False
        self.window_complete_ns = None

    def _register_window_interrupt(self, log: dict[str, Any]) -> None:
        """窗口推进帧不满足 WINDOW_MATCH：≤ T6-J01 容忍并记 S_JITTER_TOLERATED；超过即重置窗口证据。"""
        self.jitter_frames += 1
        if self.jitter_frames <= self.th["j01_frames"]:
            self.suppressions.append(SUP_JITTER)
            log["suppression_events"].append(SUP_JITTER)
            log["window_reset_reason"] = None
        else:
            log["window_reset_reason"] = (
                f"抖动中断 {self.jitter_frames} 帧 > T6-J01={self.th['j01_frames']}：立即重置窗口证据"
            )
            self._clear_window_evidence()
            # 置位放在清空之后：清空会复位 jitter_exhausted，M4 需要本帧看到"容忍已耗尽"
            self.jitter_exhausted = True

    def _window_satisfied(self) -> bool:
        if self.window_match_count < self.th["s02_frames"] or self.window_start_ns is None:
            return False
        return True  # 时长条件在 M3 内与当前时刻一并判定

    # ------------------------------------------------------------------ 冷却门
    def _gate_open(self, t_now_ns: int) -> bool:
        if self.t_last_submit_ns is None:
            return True
        return (t_now_ns - self.t_last_submit_ns) >= self.th["k01_ns"]

    def _cooldown_ended(self, t_now_ns: int) -> bool:
        return self._gate_open(t_now_ns)

    # ------------------------------------------------------------------ 主入口
    def step(self, event: dict[str, Any]) -> dict[str, Any]:
        """处理一条事件，返回 ``{"log": ..., "action_request": ...}``。"""
        if not isinstance(event, dict):
            raise CoreInputError(f"事件必须为对象：{type(event).__name__}")

        t_now_ns = event.get("t_input_ns")
        if isinstance(t_now_ns, bool) or not isinstance(t_now_ns, int):
            raise CoreInputError(f"缺少显式单调时间 t_input_ns：{t_now_ns!r}")
        if self.last_t_ns is not None and t_now_ns < self.last_t_ns:
            raise CoreInputError(f"单调时钟倒退：{t_now_ns} < {self.last_t_ns}")

        kind = event.get("kind")
        if kind not in (EV_FRAME_RESULT, *NON_ADVANCING_KINDS, EV_TICK):
            raise CoreInputError(f"未知事件类型：{kind!r}")

        session_id = event.get("session_id", self.session_id)
        frame_id = None
        frame_digest = None
        dropped_frames = 0
        if kind != EV_TICK:
            frame_id = event.get("frame_id")
            # 阶段4共享契约 r07 将 frame_id 定义为 uint32；这是字段类型边界，不是行为参数。
            if (isinstance(frame_id, bool) or not isinstance(frame_id, int)
                    or not 0 <= frame_id <= 0xFFFFFFFF):
                raise CoreInputError(
                    f"frame_id 非法（需为 uint32）：{_safe_repr(frame_id)}"
                )
            try:
                dropped_frames = int(event.get("dropped_frames", 0))
            except (TypeError, ValueError, OverflowError) as exc:
                raise CoreInputError(
                    f"dropped_frames 非法：{event.get('dropped_frames')!r}"
                ) from exc
            replayed_frame = (
                self.session_id is not None
                and session_id == self.session_id
                and self.last_frame_id is not None
                and frame_id <= self.last_frame_id
            )
            if kind == EV_FRAME_RESULT and not replayed_frame:
                state_value = event.get("state")
                if state_value not in ("OK", "NO_HAND"):
                    raise CoreInputError(f"结果状态非法：{state_value!r}")
                if "stale" in event and not isinstance(event["stale"], bool):
                    raise CoreInputError(f"stale 必须为布尔值：{event['stale']!r}")
                if "detections" in event and not isinstance(event["detections"], list):
                    raise CoreInputError("detections 必须为列表")
            try:
                frame_digest = _business_frame_digest(event)
            except Exception as exc:  # noqa: BLE001
                raise CoreInputError(f"事件业务字段无法建立稳定指纹：{exc}") from exc

        log: dict[str, Any] = {
            "session_id": session_id,
            "frame_id": event.get("frame_id"),
            "event_kind": kind,
            "input_state": event.get("state"),
            "age_result_ns": event.get("age_result_ns"),
            "age_frame_ns": event.get("age_frame_ns"),
            "from_state": self.state,
            "to_state": self.state,
            "transition": None,
            "reason": None,
            "timers": {},
            "suppression_events": [],
            "action_id": None,
            "trigger_frame_id": None,
            "t_submit_ns": None,
            "t_effective_ns": None,
            "window_complete_ns": None,
            "counters": dict(self.counters),
            "warmup": False,
        }
        self.step_anomaly = False
        self.last_t_ns = t_now_ns

        if self.session_id is None:
            # 首个事件只建立会话，不视为会话切换
            self.session_id = session_id
            log["reason"] = "会话建立（首个事件）"
        elif session_id != self.session_id:
            log["from_state"] = self.state
            self._init_state()
            self.session_id = session_id
            log["reason"] = "会话切换：全量复位到 IDLE（B25）"
            log["to_state"] = self.state
            log["transition"] = "RESET"
            log["timers"] = {"t_last_submit_ns": self.t_last_submit_ns}
            return self._finish(log)

        if kind == EV_TICK:
            log["reason"] = "时钟推进（无新结果）"
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)

        # frame_id 归类（重复/倒序）——不推进窗口序列
        duplicate = frame_id == self.last_frame_id
        out_of_order = self.last_frame_id is not None and frame_id < self.last_frame_id
        missing = (
            self.last_frame_id is not None and frame_id > self.last_frame_id + 1
            and dropped_frames == 0
        )
        if missing:
            gap = frame_id - self.last_frame_id - 1
            self.counters["missing_frames"] += int(gap)
            log["reason"] = f"缺少 {gap} 帧（由后续结果时间戳推进时间，B24）"

        if duplicate:
            if frame_digest == self.last_frame_business_sha256:
                self.counters["duplicate_frames"] += 1
                log["event_kind"] = EV_FRAME_DUPLICATE
                log["input_state"] = "DUPLICATE"
                log["frame_content_sha256"] = frame_digest
                log["reason"] = "重复 frame_id 且业务内容哈希相同：幂等丢弃，不推进状态机（B22）"
            else:
                self.counters["conflict_frames"] += 1
                log["event_kind"] = EV_FRAME_CONFLICT
                log["input_state"] = "CONFLICT"
                log["previous_frame_content_sha256"] = self.last_frame_business_sha256
                log["received_frame_content_sha256"] = frame_digest
                log["reason"] = "重复 frame_id 但业务内容哈希不同：作为 E_FRAME_CONFLICT 丢弃（B22）"
            return self._finish(log)
        if out_of_order:
            self.counters["out_of_order_frames"] += 1
            log["input_state"] = "OUT_OF_ORDER"
            log["reason"] = "倒序 frame_id：不推进窗口，计异常（B23）"
            self._anomaly(log, advancing=False)
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)

        self.last_frame_id = frame_id
        self.last_frame_business_sha256 = frame_digest

        if kind != EV_FRAME_RESULT:
            # TIMEOUT / ERROR / DROPPED：无动作、推进时间、计异常、不推进窗口与匹配计数（B21/H-4）
            key = {"E_FRAME_TIMEOUT": "timeout", "E_FRAME_ERROR": "error", "E_FRAME_DROPPED": "dropped"}[kind]
            self.counters[key] += 1
            log["reason"] = f"{kind}：无动作、推进时间、不推进匹配计数（B21）"
            self._anomaly(log, advancing=False)
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)

        # E_FRAME_RESULT
        state_value = event.get("state")
        stale = bool(event.get("stale", False))
        # N-07：state=NO_HAND 却携带 detections 属非法输入（§11.3），计非法并丢弃该帧证据，
        # 不静默忽略（与 class_id 越界同一处理路径）。
        if state_value == "NO_HAND" and event.get("detections"):
            self.counters["invalid"] += 1
            self.counters["no_hand_with_detections"] += 1
            log["input_state"] = "INVALID"
            log["reason"] = ("E_FRAME_INVALID：state=NO_HAND 却携带 detections（§11.3）；"
                             "丢弃该帧证据并计异常（N-07）")
            self._anomaly(log, advancing=False)
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)
        invalid_reason = self._validate(event)
        if invalid_reason is not None:
            self.counters["invalid"] += 1
            if invalid_reason.startswith("class_id 越界"):
                self.counters["unknown_class_frames"] += 1
            log["input_state"] = "INVALID"
            log["reason"] = f"E_FRAME_INVALID：丢弃该帧证据并计异常（B19）：{invalid_reason}"
            self._anomaly(log, advancing=False)
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)
        if stale:
            self.counters["stale"] += 1
            log["reason"] = "stale=true：不得触发、不得作为 WINDOW_MATCH 帧，仅推进时间（B18）"
            self._evaluate(t_now_ns, advancing=False, log=log)
            return self._finish(log)

        # 合法窗口推进帧
        self.result_history.append(state_value)
        self.anomaly_history.append(0)
        log["window_advance"] = True
        if state_value == "NO_HAND":
            self.counters["no_hand_frames"] += 1
            # NB-r03-05：删除无意义自赋值（原为 current_target 的自比较，无实际作用）
            self._on_advancing_no_target(log)
        else:
            self.counters["ok_frames"] += 1
            self._on_advancing_with_dets(event, t_now_ns, log)
        self._evaluate(t_now_ns, advancing=True, log=log)
        return self._finish(log)

    # ------------------------------------------------------------------ 推进帧处理
    def _on_advancing_no_target(self, log: dict[str, Any]) -> None:
        """NO_HAND：推进时间与结果计数，不推进匹配计数、不得完成稳定窗口（H-4/B17）。"""
        if self.state == "UNKNOWN_RECOVER":
            # §11.6：恢复期帧不得计入稳定窗口，也不保留旧目标
            self.legal_streak += 1
            return
        if self.current_target is not None:
            self.continues_false_streak += 1
            self._register_window_interrupt(log)
        self.candidate_streak = 0
        self.legal_streak += 1

    def _on_advancing_with_dets(self, event: dict[str, Any], t_now_ns: int, log: dict[str, Any]) -> None:
        dets = event.get("detections") or []
        if self.state == "UNKNOWN_RECOVER":
            # §11.6：恢复期禁止保留旧目标触发、恢复期帧不得计入稳定窗口
            self.legal_streak += 1
            return
        selected = self._select(dets, log)
        if selected is None:
            # 本帧无目标（全部低于 T6-P01 或零框）：不推进匹配计数，计入 TARGET_CONTINUES 不成立
            if self.current_target is not None:
                self.continues_false_streak += 1
                self._register_window_interrupt(log)
            self.candidate_streak = 0
            self.legal_streak += 1
            return

        previous = self.current_target
        continues = self._target_continues_for(previous, selected)
        if not continues and previous is not None:
            # 目标切换：当前获取结束、清空窗口证据、分配新 acquisition（D3）
            self.acquisition_id += 1
            self.acquisition_triggered = False
            self._clear_window_evidence()
            self.candidate_dwell_start_ns = t_now_ns
        if previous is None:
            self.candidate_dwell_start_ns = t_now_ns
        xyxy = [float(v) for v in selected["xyxy"]]
        self.current_target = {
            "class_id": int(selected["class_id"]),
            "xyxy": xyxy,
            "score": float(selected["score"]),
            "frame_id": event.get("frame_id"),
            "acquisition_id": self.acquisition_id,
        }
        self.continues_false_streak = 0
        self.t_last_target_continues_ns = t_now_ns
        self.candidate_streak = self.candidate_streak + 1 if continues else 1
        self._apply_window_match(xyxy, float(selected["score"]), t_now_ns, log)
        self.legal_streak += 1

    def _apply_window_match(self, xyxy: list[float], score: float, t_now_ns: int,
                            log: dict[str, Any]) -> None:
        """WINDOW_MATCH：TARGET_CONTINUES 且 score ≥ T6-P02 且与前一个 WINDOW_MATCH 帧位移 ≤ T6-P05。"""
        window_match = score >= self.th["p02"]
        if window_match and self.window_last_match_center is not None:
            cx, cy = self._center(xyxy)
            px, py = self.window_last_match_center
            if max(abs(cx - px), abs(cy - py)) > self.th["p05"]:
                window_match = False
        if window_match:
            if self.window_match_count == 0:
                self.window_start_ns = t_now_ns
            self.window_match_count += 1
            self.jitter_frames = 0
            self.jitter_exhausted = False
            self.window_last_match_center = self._center(xyxy)
            # N-r05-04：window_complete 不在「计数满足」时写，而是在 M3 成立帧（计数与时长取较晚）写
        else:
            self._register_window_interrupt(log)
        log["window_match"] = window_match
        log["window_match_count"] = self.window_match_count

    # ------------------------------------------------------------------ 异常与求值
    def _anomaly(self, log: dict[str, Any], advancing: bool) -> None:
        self.step_anomaly = True
        self.anomaly_history.append(1)
        self.result_history.append("ANOMALY")
        self.legal_streak = 0

    def _anomaly_fires(self) -> bool:
        return sum(self.anomaly_history) >= self.th["u00_n"] and len(self.anomaly_history) >= self.th["u00_w"]

    def _loss_confirmed(self, t_now_ns: int) -> bool:
        if self.current_target is None and self.t_last_target_continues_ns is None:
            return False
        if self.continues_false_streak >= self.th["l01_frames"]:
            return True
        if self.t_last_target_continues_ns is not None:
            return (t_now_ns - self.t_last_target_continues_ns) >= self.th["l02_ns"]
        return False

    def _evaluate(self, t_now_ns: int, advancing: bool, log: dict[str, Any]) -> None:
        """按 v1.8 求值序逐级判定，首次命中即停（BLK-r03-1：结束获取的 M11/M4/M8/M2/M12 都分配新 acquisition_id）。"""
        previous = self.state

        # P1 异常
        if self.state == "UNKNOWN_RECOVER":
            if self.step_anomaly:
                self.anomaly_history.clear()
                self._transition(log, "M13", "恢复期再次异常：重置计数起点")
                return
        elif self._anomaly_fires():
            self._transition(log, "M2", f"最近 {self.th['u00_w']} 条结果内异常数 ≥ {self.th['u00_n']}")
            return

        # P2 丢失确认（任何有目标状态）
        if (self.current_target is not None
                and self.state in ("IDLE", "CANDIDATE", "STABLE", "TRIGGERED", "COOLDOWN")
                and self._loss_confirmed(t_now_ns)):
            self._transition(log, "M10", "连续推进帧 TARGET_CONTINUES 不成立或距上次成立超时")
            return

        # P3 当前状态推进
        if self.state == "STABLE":
            # STABLE 锁存：只由 M5（本帧为窗口推进帧且门已开且本次获取未触发）离开
            if advancing and not self.acquisition_triggered and self._gate_open(t_now_ns):
                self.acquisition_triggered = True
                self._transition(log, "M5", "锁存 STABLE 且本帧为窗口推进帧、全局冷却门已结束")
                return
            if advancing and not self.acquisition_triggered and not self._gate_open(t_now_ns):
                self.suppressions.append(SUP_COOLDOWN)
                log["suppression_events"].append(SUP_COOLDOWN)
                log["reason"] = "全局冷却门未结束：M5 被 H-10 抑制，状态停留 STABLE"
            return

        if self.state == "CANDIDATE":
            if (self.window_match_count >= self.th["s02_frames"] and self.window_start_ns is not None
                    and (t_now_ns - self.window_start_ns) >= self.th["s01_ns"]):
                # N-r05-04：完成帧 = 计数与时长同时满足的第一帧（T6-S03 取较晚）；
                # 30fps（P=33.3 ms）下由时长支配 → 第 8 帧 233.1 ms，而不是第 6 帧 166.5 ms。
                self.window_complete_ns = t_now_ns
                log["window_complete_ns"] = t_now_ns
                self._transition(log, "M3", "连续 WINDOW_MATCH 帧数 ≥ T6-S02 且窗口时长 ≥ T6-S01（取较晚）")
                return
            dwell_ok = (
                self.candidate_dwell_start_ns is not None
                and (t_now_ns - self.candidate_dwell_start_ns) >= self.th["s04_ns"]
            )
            if self.jitter_exhausted and dwell_ok:
                self.suppressions.append(SUP_WINDOW_TIMEOUT)
                log["suppression_events"].append(SUP_WINDOW_TIMEOUT)
                self._transition(log, "M4", "抖动容忍耗尽且候选停留 ≥ T6-S04（M10 未命中）")
            return

        if self.state == "COOLDOWN":
            if not self._cooldown_ended(t_now_ns):
                return
            continues = self.current_target is not None and self.continues_false_streak == 0
            if not continues:
                self._transition(log, "M8", "冷却结束且当前目标 TARGET_CONTINUES 不成立/已丢失")
                return
            window_ok = (
                self.window_match_count >= self.th["s02_frames"] and self.window_start_ns is not None
                and (t_now_ns - self.window_start_ns) >= self.th["s01_ns"]
            )
            if window_ok:
                self._transition(log, "M9", "冷却结束、同一目标仍 TARGET_CONTINUES 且窗口再次满足（维持态，不再触发）")
            else:
                self._transition(log, "M15", "冷却结束、目标仍 TARGET_CONTINUES 但窗口未满足（不触发）")
            return

        if self.state == "TRIGGERED":
            # M6 由动作层回执驱动（note_action_ack）；此处不自动迁移
            return

        if self.state == "LOST":
            self._transition(log, "M11", "丢失确认后清空当前目标与稳定证据")
            return

        if self.state == "UNKNOWN_RECOVER":
            if self.legal_streak >= self.th["u01_frames"]:
                self._transition(log, "M12", f"连续 {self.th['u01_frames']} 条合法结果且无未知类别")
            return

        # P4 获取（IDLE）
        if self.state == "IDLE" and self.current_target is not None:
            if self.candidate_streak >= self.th["c01_frames"]:
                if self.candidate_dwell_start_ns is None:  # NB-r03-08：显式判空（避免 t=0 时被 or 改写）
                    self.candidate_dwell_start_ns = t_now_ns
                self._transition(log, "M1", f"连续 {self.th['c01_frames']} 条窗口推进帧为同一目标（TARGET_CONTINUES）")

        _ = previous

    def _transition(self, log: dict[str, Any], mid: str, reason: str) -> None:
        self.jitter_exhausted = False
        self.state = {
            "M1": "CANDIDATE", "M2": "UNKNOWN_RECOVER", "M3": "STABLE", "M4": "IDLE",
            "M5": "TRIGGERED", "M6": "COOLDOWN", "M8": "IDLE", "M9": "STABLE", "M10": "LOST",
            "M11": "IDLE", "M12": "IDLE", "M13": "UNKNOWN_RECOVER", "M15": "CANDIDATE",
        }[mid]
        if mid in ("M11", "M4", "M8"):
            # BLK-r03-1（终审 B，按 (a) 修）：**凡结束一次获取的转移都分配新的 acquisition_id**。
            # M8 = COOLDOWN→IDLE 的目标丢失出口（并非会话复位；复位是 RESET，由 _init_state 归零），同样结束获取。
            self.acquisition_id += 1
            self.current_target = None
            self._clear_window_evidence()
            self.continues_false_streak = 0
            self.t_last_target_continues_ns = None
            self.candidate_streak = 0
            self.candidate_dwell_start_ns = None
            self.acquisition_triggered = False
        if mid == "M12":
            # BLK-r03-1：恢复出口同样结束该轮获取（恢复期不保留旧目标）→ 分配新 id
            self.acquisition_id += 1
        if mid == "M15":
            self._clear_window_evidence()
            self.candidate_streak = 1
            self.candidate_dwell_start_ns = self.last_t_ns
        if mid == "M6":
            # §4：进入 COOLDOWN 保留当前目标标识、重置稳定窗口证据
            self._clear_window_evidence()
        if mid == "M9":
            self._clear_window_evidence()
        if mid == "M2":
            # §11.6：进入恢复态时清空目标与稳定证据，恢复期帧不计入窗口
            # BLK-r03-1：M2 同样结束一次获取 → 分配新 id（M13 只是恢复态内再入，不结束获取、不递增）
            self.acquisition_id += 1
            self.current_target = None
            self._clear_window_evidence()
            self.continues_false_streak = 0
            self.t_last_target_continues_ns = None
            self.candidate_streak = 0
            self.candidate_dwell_start_ns = None
            self.legal_streak = 0
            self.acquisition_triggered = False
        log["transition"] = mid
        log["reason"] = reason
        log["to_state"] = self.state
        log["timers"] = {
            "window_match_count": self.window_match_count,
            "window_start_ns": self.window_start_ns,
            "jitter_frames": self.jitter_frames,
            "continues_false_streak": self.continues_false_streak,
            "t_last_target_continues_ns": self.t_last_target_continues_ns,
            "t_last_submit_ns": self.t_last_submit_ns,
            "candidate_streak": self.candidate_streak,
        }

    def _finish(self, log: dict[str, Any]) -> dict[str, Any]:
        log["acquisition_id"] = self.acquisition_id  # BLK-r02-1/2：日志与动作记录同口径
        log["to_state"] = self.state
        log["counters"] = dict(self.counters)
        request = None
        if log.get("transition") == "M5" and self.state == "TRIGGERED":
            mapping = self.pack.class_action_map[int(self.current_target["class_id"])]
            request = {
                "action_type": mapping["action_type"],
                "target_id": mapping["target_id"],
                "class_id": int(mapping["class_id"]),
                "class_name": mapping["class_name"],
                "acquisition_id": self.acquisition_id,  # N-04：动作记录含获取级 id
                "source_frame_id": log.get("frame_id"),
                "trigger_frame_id": log.get("frame_id"),
                "t_trigger_ns": self.last_t_ns,
                "acquisition_id": self.acquisition_id,
                "expected_display": self.pack.data["actions"].get("proposed_display_fields"),
            }
            log["trigger_frame_id"] = log.get("frame_id")
        return {"log": log, "action_request": request}

    # ------------------------------------------------------------------ 动作回执
    def note_action_ack(self, ack: dict[str, Any]) -> dict[str, Any]:
        """动作层回执：提交 ACK 按非空不透明 ID 幂等；无 ID 抑制回执不去重。"""
        action_id = ack.get("action_id")
        suppression = ack.get("suppression")
        log: dict[str, Any] = {
            "session_id": self.session_id,
            "from_state": self.state,
            "to_state": self.state,
            "transition": None,
            "reason": None,
            "suppression_events": [],
            "action_id": action_id,
            "submit_result": ack.get("submit_result"),
            "effective_result": ack.get("effective_result"),
            "t_submit_ns": ack.get("t_submit_ns"),
            "t_effective_ns": ack.get("t_effective_ns"),
            "counters": dict(self.counters),
        }
        if suppression is not None:
            if (not isinstance(suppression, str)
                    or suppression not in ACTION_ACK_SUPPRESSIONS):
                raise CoreInputError(f"动作回执 suppression 非法：{suppression!r}")
            if (action_id is not None or ack.get("submit_result") is not None
                    or ack.get("effective_result") is not None
                    or ack.get("t_submit_ns") is not None
                    or ack.get("t_effective_ns") is not None):
                raise CoreInputError("抑制回执不得包含动作 ID、提交/生效结果或时间戳")
        else:
            if not isinstance(action_id, str) or not action_id.strip():
                raise CoreInputError(f"真实动作回执缺少合法 action_id：{action_id!r}")
            submit_result = ack.get("submit_result")
            effective_result = ack.get("effective_result")
            t_submit_ns = ack.get("t_submit_ns")
            t_effective_ns = ack.get("t_effective_ns")
            if submit_result not in ("success", "fail"):
                raise CoreInputError(f"真实动作回执 submit_result 非法：{submit_result!r}")
            if not _is_ns_timestamp(t_submit_ns):
                raise CoreInputError(f"真实动作回执 t_submit_ns 必须为整数纳秒：{t_submit_ns!r}")
            if submit_result == "success":
                if effective_result == "observed":
                    if not _is_ns_timestamp(t_effective_ns):
                        raise CoreInputError(
                            f"observed 回执必须带整数 t_effective_ns：{t_effective_ns!r}"
                        )
                    if t_effective_ns < t_submit_ns:
                        raise CoreInputError("observed 回执 t_effective_ns 不得早于 t_submit_ns")
                elif effective_result == "unobserved":
                    if t_effective_ns is not None:
                        raise CoreInputError("unobserved 回执不得带 t_effective_ns")
                else:
                    raise CoreInputError(
                        f"success 回执 effective_result 非法：{effective_result!r}"
                    )
            else:
                if effective_result != "unobserved":
                    raise CoreInputError("fail 回执必须报告 effective_result=unobserved")
                if t_effective_ns is not None:
                    raise CoreInputError("fail 回执不得带 t_effective_ns")
        if suppression is None and action_id in self._seen_action_ack_ids:
            log["duplicate_ack_ignored"] = True
            log["reason"] = "重复 action_id 回执：幂等忽略，不重复计数或迁移状态"
            self.action_log.append({**ack, "duplicate_ack_ignored": True})
            return log
        if suppression is None:
            if (self.t_last_submit_ns is not None
                    and ack["t_submit_ns"] < self.t_last_submit_ns):
                raise CoreInputError("新动作回执 t_submit_ns 早于已记录的冷却锚点")
            self._seen_action_ack_ids.add(action_id)
        if suppression is not None:
            log["suppression_events"].append(suppression)
            log["reason"] = str(ack.get("reason"))
            self.acquisition_triggered = False
            self.state = "STABLE" if self.current_target is not None else "IDLE"
        elif ack.get("submit_result") == "success":
            self.counters["action_submitted"] += 1
            self.t_last_submit_ns = ack.get("t_submit_ns")
            if ack.get("effective_result") == "observed":
                self.counters["action_effective"] += 1
            else:
                self.counters["unobserved"] += 1
                self.counters["false_actions"] += 1
            if self.state == "TRIGGERED":
                self._transition(log, "M6", "动作提交事件落盘（TRIGGERED → COOLDOWN）")
                log["reason"] = "动作提交事件落盘（M6）"
        else:
            self.counters["false_actions"] += 1
            log["reason"] = "动作提交失败：不产生 ACTION_SUBMITTED、不更新 t_last_submit"
            self.acquisition_triggered = False
            self.state = "STABLE" if self.current_target is not None else "IDLE"
        self.action_log.append(dict(ack))
        log["to_state"] = self.state
        log["counters"] = dict(self.counters)
        return log
