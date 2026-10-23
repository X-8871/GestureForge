#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线显示骨架：结果 → 帧关联 → 叠框决策 → 五元组 / HUD / 计数（纯离线参考逻辑）。

角色
====
本模块是**离线骨架**，不是板上实现，也不是阶段5 验收产物。它的用途是把 `CDX-20261022-014`
§4/§5 要求的四件事先在离线钉成可判定的形态，供 S5-T02（板上动态映射）镜像实现并留出对拍基线：

1. **坐标映射**：结果 `detections[].xyxy`（归一化原图坐标）→ 显示像素索引 → 2 px 偶数线宽居中边框。
   全部几何/取整/裁剪/边框像素**只从** `verification/s5_display_geometry_reference.py`（契约
   `S5A-G0-v2`）导入，禁止在本模块重写第二套逆映射（本模块不定义任何几何公式）。
2. **帧关联**：语义 B（最新到达结果叠加）下的 `(displayed_frame_id, result_frame_id, age_result_ns,
   age_frame_ns, display_semantics)` 五元组；关联键对齐阶段4 S4-B 草案
   `contract_result_key=(session_id, frame_id, result_seq)`。
3. **异常语义**：过期（`age_frame > 200 ms` 或 PS `stale` 标志，每结果只计一次）、零框（`NO_HAND`，
   合法、非过期）、`TIMEOUT`/`ERROR`/`DROPPED` 分别计数、无效记录不绘制；**重复/乱序/回退按阶段4 r04
   `frame_sequence_rules` 一律拒绝并记 FAIL**（只计数、不写已接受集合、不更新最新结果、不绘制）。
4. **可复算**：所有计数必须能由帧级事件日志完全复算；日志可落盘为紧凑 JSONL（`dump_jsonl`），
   离线长跑用虚拟时钟加速，不冒充板上运行。计数单位与时机见 `COUNTER_UNITS`。

诚实边界
========
- 输入一律是**合成流**（`synthetic_dynamic_reference`）：`capture_time_ns` 为**合成单调时钟值**，
  仅用于年龄算术演练，**不得**解释为真实采集时刻；非 camera 输入按阶段4 草案要求标
  `capture_time_available=false` + `unavailable_fields=["capture_time_ns"]`。
- 本模块不读摄像头、不读 UART、不开 JTAG、不跑 Vivado；不在本模块内做解码/NMS/阈值。
- 骨架 PASS **不等于**阶段5 通过，也不等于真实集成通过；板上结论必须另出证据。

退出码约定由调用方（测试/证据脚本）决定；本模块只抛异常。
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402

# ── 骨架角色：只导出冻结参考实现对象的引用，便于断言「未重写第二套几何」──────────
REFERENCE = R

CONTRACT_ID = R.CONTRACT_ID
STALE_AGE_LIMIT_NS = R.STALE_AGE_LIMIT_NS
DISPLAY_SEMANTICS = R.DISPLAY_SEMANTICS
CLASS_ORDER: tuple[str, ...] = R.CLASS_ORDER
HUD_FIELDS: tuple[str, ...] = R.__dict__.get("HUD_FIELDS", ()) or (
    "capture_fps", "inference_fps", "display_fps", "inference_time_ns", "age_result_ns",
    "age_frame_ns", "frame_id", "boxes", "stale_cleared", "dropped_frames", "timeouts",
    "warmup_state", "display_semantics",
)

RESULT_KEY_FIELDS = ("session_id", "frame_id", "result_seq")
EVENT_RESULT_SUBMIT = "result_submit"
EVENT_OVERLAY_COMMIT = "overlay_commit"

COUNTER_KEYS = (
    "frames_committed",
    "overlay_drawn_frames",
    "boxes_drawn",
    "warmup_frames",
    "dropped_frames",
    "timeouts",
    "error_results",
    "invalid_records",
    "stale_cleared",
    "duplicate_results",
    "out_of_order_results",
    "zero_hand_frames",
    "zero_area_dropped",
)

SUBMIT_OUTCOMES = ("accepted", "duplicate", "out_of_order", "invalid")

# 计数单位与时机（N-3）：避免把「注入结果数」误读为「发生帧数」
COUNTER_UNITS = {
    "frames_committed": "每显示帧 1（含 warmup）",
    "overlay_drawn_frames": "每显示帧 1（仅当真的绘制了边框）",
    "boxes_drawn": "每个被绘制的框 1（逐帧累加）",
    "warmup_frames": "每预热显示帧 1",
    "dropped_frames": "每个状态为 DROPPED 的提交帧 1（结果会被后续无新结果的帧继续复用 ⇒ 计数 ≥ 注入结果数）",
    "timeouts": "每个状态为 TIMEOUT 的提交帧 1（同上）",
    "error_results": "每个状态为 ERROR 的提交帧 1（同上）",
    "invalid_records": "每次提交被判 schema 违规 1（不采用、不绘制）",
    "stale_cleared": "按结果键 (session_id, frame_id, result_seq) 去重后 1（同一过期结果跨帧复用只计一次）",
    "duplicate_results": "每次提交命中已接受结果键 1（拒绝、不更新最新结果）",
    "out_of_order_results": "每次提交发生 frame_id/result_seq 回退 1（拒绝、记 FAIL、不更新最新结果）",
    "zero_hand_frames": "每个 NO_HAND 且非过期的提交帧 1（合法零框，不绘制但不计过期）",
    "zero_area_dropped": "每个被丢弃的零面积框 1（逐帧、逐框累加）",
}

VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"


class SkeletonInputError(ValueError):
    """骨架输入不满足契约时抛出（不静默降级）。"""


def load_json(path: str | pathlib.Path) -> Any:
    """UTF-8 读取 JSON；失败即抛，不返回空默认值。"""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def result_key(record: Mapping[str, Any]) -> tuple:
    """共享契约结果键 `(session_id, frame_id, result_seq)`；缺字段即输入错误。"""
    missing = [key for key in RESULT_KEY_FIELDS if record.get(key) is None]
    if missing:
        raise SkeletonInputError(f"结果记录缺少关联键字段：{missing}")
    return tuple(record[key] for key in RESULT_KEY_FIELDS)


class FrameEventLog:
    """帧级事件日志（帧号 + 事件类型 + 时间戳），所有统计量必须由它复算。"""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def append(self, event: Mapping[str, Any]) -> dict[str, Any]:
        entry = dict(event)
        self.events.append(entry)
        return entry

    def commit_events(self) -> list[dict[str, Any]]:
        return [e for e in self.events if e.get("event_type") == EVENT_OVERLAY_COMMIT]

    def submit_events(self) -> list[dict[str, Any]]:
        return [e for e in self.events if e.get("event_type") == EVENT_RESULT_SUBMIT]

    def five_tuples(self) -> list[dict[str, Any]]:
        return [
            {
                "displayed_frame_id": e["displayed_frame_id"],
                "result_frame_id": e["result_frame_id"],
                "age_result_ns": e["age_result_ns"],
                "age_frame_ns": e["age_frame_ns"],
                "display_semantics": e["display_semantics"],
            }
            for e in self.commit_events()
        ]

    def recompute(self) -> dict[str, Any]:
        """由日志复算全部计数与五元组（与在线计数逐项比较用；复算器亦可用于落盘日志）。"""
        counters = {key: 0 for key in COUNTER_KEYS}
        stale_keys: set[tuple] = set()
        for event in self.submit_events():
            outcome = event.get("outcome")
            if outcome == "duplicate":
                counters["duplicate_results"] += 1
            elif outcome == "out_of_order":
                counters["out_of_order_results"] += 1
            elif outcome == "invalid":
                counters["invalid_records"] += 1
        for event in self.commit_events():
            counters["frames_committed"] += 1
            if event.get("warmup"):
                counters["warmup_frames"] += 1
            if event.get("drawn"):
                counters["overlay_drawn_frames"] += 1
            counters["boxes_drawn"] += int(event.get("boxes", 0))
            counters["zero_area_dropped"] += int(event.get("zero_area_dropped", 0))
            state = event.get("state")
            if state == "DROPPED":
                counters["dropped_frames"] += 1
            elif state == "TIMEOUT":
                counters["timeouts"] += 1
            elif state == "ERROR":
                counters["error_results"] += 1
            elif state == "NO_HAND" and not event.get("stale_effective"):
                counters["zero_hand_frames"] += 1
            if event.get("stale_effective"):
                key = (event.get("session_id"), event.get("result_frame_id"), event.get("result_seq"))
                if key not in stale_keys:
                    stale_keys.add(key)
                    counters["stale_cleared"] += 1
        return {"counters": counters, "five_tuples": self.five_tuples(), "stale_result_keys": len(stale_keys)}

    # ── 落盘（N-4）：紧凑 JSONL，供独立复算器在不导入本模块内存状态的情况下复算 ──
    COMPACT_SUBMIT_FIELDS = ("t", "fid", "sid", "seq", "oc", "vf")
    COMPACT_COMMIT_FIELDS = ("t", "dfid", "ts", "rfid", "sid", "seq", "st", "dr", "bx", "za", "se", "w")

    def compact_event(self, event: Mapping[str, Any]) -> dict[str, Any]:
        """把一条事件压成复算所需的最小字段集（格式见 docs/stage5/s5t03_offline_skeleton_params_v1.json::log_artifacts）。"""
        if event.get("event_type") == EVENT_RESULT_SUBMIT:
            return {"t": "sub", "fid": event.get("frame_id"), "sid": event.get("session_id"),
                    "seq": event.get("result_seq"), "oc": event.get("outcome"),
                    "vf": event.get("verdict")}
        return {"t": "commit", "dfid": event.get("displayed_frame_id"), "ts": event.get("overlay_commit_ns"),
                "rfid": event.get("result_frame_id"), "sid": event.get("session_id"),
                "seq": event.get("result_seq"), "st": event.get("state"),
                "dr": 1 if event.get("drawn") else 0, "bx": int(event.get("boxes", 0)),
                "za": int(event.get("zero_area_dropped", 0)),
                "se": 1 if event.get("stale_effective") else 0,
                "w": 1 if event.get("warmup") else 0}

    def dump_jsonl(self, path: str | pathlib.Path, *, compact: bool = True) -> dict[str, Any]:
        """写帧级事件日志（`*.jsonl` 或 `*.jsonl.gz`）；返回落盘统计。"""
        import gzip
        target = pathlib.Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for event in self.events:
            payload = self.compact_event(event) if compact else dict(event)
            lines.append(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        blob = ("\n".join(lines) + "\n").encode("utf-8")
        if target.name.endswith(".gz"):
            with gzip.open(target, "wb") as handle:
                handle.write(blob)
        else:
            target.write_bytes(blob)
        return {"path": str(target), "events": len(self.events), "compact": compact,
                "bytes": target.stat().st_size, "uncompressed_bytes": len(blob)}


class DisplayPipeline:
    """语义 B（最新**已接受**结果叠加）离线骨架：提交结果 → 提交显示帧。

    判定规则（全部来自 `S5A-G0-v2` + 阶段4 r04 `frame_sequence_rules`，本类不新增阈值）：
    - 记录先过冻结 `validate_result_record`；有问题 ⇒ `invalid_records+1`、记 FAIL，不采用、不绘制；
    - 结果键 `(session_id, frame_id, result_seq)` 重复 ⇒ `duplicate_results+1`、记 FAIL，**不**更新最新结果；
    - **乱序/回退**（同 session 的 `frame_id` 或 `result_seq` 小于上一已接受值）⇒ `out_of_order_results+1`、
      记 FAIL 与原因，**拒绝**：不写入已接受集合、不更新最新结果、不绘制（B-2：采用上游强制行为，
      与重复同构；不再"按到达序采用"）；
    - 过期 = `PS stale 标志 OR age_frame > 200 ms`，每结果只计一次；
    - `NO_HAND` = 合法零框（非过期）；`TIMEOUT`/`ERROR`/`DROPPED` 分别计数，不冒充零框；
    - 每显示帧恰好产生一条 `overlay_commit` 事件（缺事件即视为死锁，由长跑断言检出）。
    计数单位与时机见 `COUNTER_UNITS`（N-3）。
    """

    def __init__(self, *, canvas_width: int = 1280, canvas_height: int = 720,
                 input_scope_label: str = "synthetic_dynamic_reference",
                 params: Mapping[str, Any] | None = None) -> None:
        self.canvas_width = int(canvas_width)
        self.canvas_height = int(canvas_height)
        self.input_scope_label = input_scope_label
        self.params = dict(params or {})
        self.log = FrameEventLog()
        self.latest: dict[str, Any] | None = None
        self.accepted_keys: set[tuple] = set()
        self.stale_counted_keys: set[tuple] = set()
        self.last_result_seq: dict[Any, int] = {}
        self.last_frame_id: dict[Any, int] = {}
        self.counters = {key: 0 for key in COUNTER_KEYS}
        self.frames_committed = 0

    # ── 提交结果 ──────────────────────────────────────────────────────────
    def submit_result(self, record: Mapping[str, Any]) -> dict[str, Any]:
        """校验并登记一条结果；返回本次提交的判定（含 outcome）。"""
        problems = R.validate_result_record(record)
        key: tuple | None = None
        try:
            key = result_key(record)
        except SkeletonInputError as error:
            problems = list(problems) + [str(error)]

        event: dict[str, Any] = {
            "event_type": EVENT_RESULT_SUBMIT,
            "frame_id": record.get("frame_id"),
            "session_id": record.get("session_id"),
            "result_seq": record.get("result_seq"),
            "source_kind": record.get("source_kind"),
            "input_scope_label": self.input_scope_label,
            "problems": list(problems),
        }

        if problems:
            self.counters["invalid_records"] += 1
            event["outcome"] = "invalid"
            event["verdict"] = VERDICT_FAIL
            event["reject_reason"] = "schema_violation"
            self.log.append(event)
            return {"outcome": "invalid", "verdict": VERDICT_FAIL, "problems": list(problems), "key": key}

        session = record["session_id"]
        seq = int(record["result_seq"])
        frame_id = int(record["frame_id"])
        if key in self.accepted_keys:
            self.counters["duplicate_results"] += 1
            event["outcome"] = "duplicate"
            event["verdict"] = VERDICT_FAIL
            event["reject_reason"] = "duplicate_result_key"
            self.log.append(event)
            return {"outcome": "duplicate", "verdict": VERDICT_FAIL, "key": key}

        # B-2：采用阶段4 r04 frame_sequence_rules 的强制行为——重复/乱序/回退一律拒绝并记 FAIL
        reasons: list[str] = []
        if session in self.last_frame_id and frame_id < self.last_frame_id[session]:
            reasons.append("regressed_frame_id")
        if session in self.last_result_seq and seq < self.last_result_seq[session]:
            reasons.append("regressed_result_seq")
        if reasons:
            self.counters["out_of_order_results"] += 1
            event["outcome"] = "out_of_order"
            event["verdict"] = VERDICT_FAIL
            event["reject_reason"] = "+".join(reasons)
            event["previous_frame_id"] = self.last_frame_id.get(session)
            event["previous_result_seq"] = self.last_result_seq.get(session)
            event["rejected"] = True
            self.log.append(event)
            # 拒绝：不写 accepted_keys、不更新 latest、不绘制
            return {"outcome": "out_of_order", "verdict": VERDICT_FAIL, "reject_reason": event["reject_reason"],
                    "key": key, "problems": []}

        event["outcome"] = "accepted"
        event["verdict"] = VERDICT_PASS
        self.accepted_keys.add(key)
        self.last_result_seq[session] = max(seq, self.last_result_seq.get(session, seq))
        self.last_frame_id[session] = max(frame_id, self.last_frame_id.get(session, frame_id))
        self.latest = dict(record)
        self.log.append(event)
        return {"outcome": "accepted", "verdict": VERDICT_PASS, "key": key, "problems": []}

    # ── 提交显示帧 ────────────────────────────────────────────────────────
    def commit_frame(self, displayed_frame_id: int, overlay_commit_ns: int,
                     *, warmup: bool = False) -> dict[str, Any]:
        """提交一帧显示；返回该帧的叠框决策 + 五元组 + HUD（并发一条事件）。"""
        commit_ns = int(overlay_commit_ns)
        decision = self._decide(commit_ns, warmup=warmup)
        event: dict[str, Any] = {
            "event_type": EVENT_OVERLAY_COMMIT,
            "displayed_frame_id": int(displayed_frame_id),
            "frame_id": int(displayed_frame_id),
            "overlay_commit_ns": commit_ns,
            "warmup": bool(warmup),
            "input_scope_label": self.input_scope_label,
            "display_semantics": DISPLAY_SEMANTICS,
            "drawn": bool(decision["drawn"]),
            "boxes": int(decision["boxes"]),
            "zero_area_dropped": int(decision["zero_area_dropped"]),
            "box_px": decision["box_px"],
            "state": decision["state"],
            "stale_effective": bool(decision["stale_effective"]),
            "stale_reason": decision["stale_reason"],
            "skip_reason": decision["skip_reason"],
            "result_frame_id": decision["result_frame_id"],
            "session_id": decision["session_id"],
            "result_seq": decision["result_seq"],
            "age_result_ns": decision["age_result_ns"],
            "age_frame_ns": decision["age_frame_ns"],
        }
        self.log.append(event)
        self.counters["frames_committed"] += 1
        self.frames_committed += 1
        if event["warmup"]:
            self.counters["warmup_frames"] += 1
        if event["drawn"]:
            self.counters["overlay_drawn_frames"] += 1
        self.counters["boxes_drawn"] += event["boxes"]
        self.counters["zero_area_dropped"] += event["zero_area_dropped"]
        if event["stale_effective"]:
            key = (event["session_id"], event["result_frame_id"], event["result_seq"])
            if key not in self.stale_counted_keys:
                self.stale_counted_keys.add(key)
                self.counters["stale_cleared"] += 1
        if event["state"] == "DROPPED":
            self.counters["dropped_frames"] += 1
        elif event["state"] == "TIMEOUT":
            self.counters["timeouts"] += 1
        elif event["state"] == "ERROR":
            self.counters["error_results"] += 1
        elif event["state"] == "NO_HAND" and not event["stale_effective"]:
            self.counters["zero_hand_frames"] += 1
        return {
            "event": event,
            "five_tuple": {
                "displayed_frame_id": event["displayed_frame_id"],
                "result_frame_id": event["result_frame_id"],
                "age_result_ns": event["age_result_ns"],
                "age_frame_ns": event["age_frame_ns"],
                "display_semantics": event["display_semantics"],
            },
            "hud": self.hud(decision, displayed_frame_id),
        }

    # ── 内部：单帧决策 ────────────────────────────────────────────────────
    def _decide(self, commit_ns: int, *, warmup: bool) -> dict[str, Any]:
        blank = {
            "drawn": False, "boxes": 0, "zero_area_dropped": 0, "box_px": [],
            "state": "NO_RESULT", "stale_effective": False, "stale_reason": R.STALE_REASON_NONE,
            "result_frame_id": None, "session_id": None, "result_seq": None,
            "age_result_ns": None, "age_frame_ns": None, "skip_reason": "no_result_yet",
        }
        if warmup:
            blank["state"] = "WARMUP"
            blank["skip_reason"] = "warmup"
            return blank
        record = self.latest
        if record is None:
            return blank

        capture_ns = int(record["capture_time_ns"])
        result_ns = int(record["result_time_ns"])
        ages = R.compute_ages(capture_ns, result_ns, commit_ns)
        stale_info = R.effective_stale(bool(record["stale"]), ages["age_frame_ns"])
        decision = {
            "drawn": False, "boxes": 0, "zero_area_dropped": 0, "box_px": [],
            "state": record["state"],
            "stale_effective": bool(stale_info["stale_effective"]),
            "stale_reason": stale_info["reason"],
            "result_frame_id": int(record["frame_id"]),
            "session_id": record["session_id"],
            "result_seq": int(record["result_seq"]),
            "age_result_ns": int(ages["age_result_ns"]),
            "age_frame_ns": int(ages["age_frame_ns"]),
            "skip_reason": "",
        }
        if decision["stale_effective"]:
            decision["skip_reason"] = f"stale_cleared:{stale_info['reason']}"
            return decision
        if record["state"] != "OK":
            # TIMEOUT/ERROR/DROPPED/NO_HAND：不绘制；NO_HAND 是合法零框（非过期）
            decision["skip_reason"] = f"state:{record['state']}"
            return decision
        for detection in record["detections"]:
            clipped = R.clip_unit_box(detection["xyxy"])
            if clipped["zero_area"]:
                decision["zero_area_dropped"] += 1
                continue
            px = R.original_norm_to_display_px(clipped["xyxy"], self.canvas_width, self.canvas_height)
            border = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"],
                                         R.DISPLAY_LINE_WIDTH_PX, self.canvas_width, self.canvas_height)
            decision["box_px"].append({
                "class_id": detection["class_id"], "class_name": detection["class_name"],
                "score": float(detection["score"]), "px": px, "border_pixels": len(border),
            })
        decision["boxes"] = len(decision["box_px"])
        decision["drawn"] = decision["boxes"] > 0
        if not decision["drawn"]:
            decision["skip_reason"] = "all_zero_area_or_no_box"
        return decision

    # ── HUD ──────────────────────────────────────────────────────────────
    def hud(self, decision: Mapping[str, Any], displayed_frame_id: int) -> dict[str, Any]:
        """HUD 13 字段；不可用量显式标 UNAVAILABLE，**不得**用 0 伪装（S5A-G0-v2 §3/§6）。"""
        return {
            "capture_fps": "UNAVAILABLE",
            "inference_fps": "UNAVAILABLE",
            "display_fps": "UNAVAILABLE",
            "inference_time_ns": (int(self.latest["inference_time_ns"]) if self.latest else "UNAVAILABLE"),
            "age_result_ns": decision["age_result_ns"] if decision["age_result_ns"] is not None else "UNAVAILABLE",
            "age_frame_ns": decision["age_frame_ns"] if decision["age_frame_ns"] is not None else "UNAVAILABLE",
            "frame_id": int(displayed_frame_id),
            "boxes": int(decision["boxes"]),
            "stale_cleared": int(self.counters["stale_cleared"]),
            "dropped_frames": int(self.counters["dropped_frames"]),
            "timeouts": int(self.counters["timeouts"]),
            "warmup_state": bool(decision["state"] == "WARMUP"),
            "display_semantics": DISPLAY_SEMANTICS,
        }

    # ── 复算与不变量 ──────────────────────────────────────────────────────
    def recompute(self) -> dict[str, Any]:
        return self.log.recompute()

    def assert_recomputable(self) -> None:
        """在线计数必须与日志复算逐项相等；不等即抛（不静默）。"""
        recomputed = self.recompute()
        if recomputed["counters"] != self.counters:
            diff = {k: (self.counters[k], recomputed["counters"][k])
                    for k in COUNTER_KEYS if self.counters[k] != recomputed["counters"][k]}
            raise AssertionError(f"计数不可复算：在线 vs 复算 {diff}")


def run_stream(pipeline: DisplayPipeline, steps: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """按步骤驱动骨架：先提交该帧的结果，再提交该帧。返回汇总（含五元组与 HUD 末帧）。"""
    five_tuples: list[dict[str, Any]] = []
    hud_last: dict[str, Any] | None = None
    last_commit_ns: int | None = None
    for step in steps:
        for record in step.get("results", []):
            pipeline.submit_result(record)
        outcome = pipeline.commit_frame(int(step["displayed_frame_id"]),
                                       int(step["overlay_commit_ns"]),
                                       warmup=bool(step.get("warmup", False)))
        five_tuples.append(outcome["five_tuple"])
        hud_last = outcome["hud"]
        if last_commit_ns is not None and int(step["overlay_commit_ns"]) < last_commit_ns:
            raise AssertionError("提交时间戳回退：显示提交时刻必须单调不减")
        last_commit_ns = int(step["overlay_commit_ns"])
    pipeline.assert_recomputable()
    return {
        "five_tuples": five_tuples,
        "hud_last": hud_last,
        "counters": dict(pipeline.counters),
        "events": len(pipeline.log.events),
        "commit_events": len(pipeline.log.commit_events()),
    }


def default_params_path() -> pathlib.Path:
    return REPO_ROOT / "docs" / "stage5" / "s5t03_offline_skeleton_params_v1.json"