#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 合成动态流生成器（与阶段4 消费记录同 schema，逐处标注「合成，非阶段4 输出」）。

用途：给 `scripts/stage5_t03/s5t03_display_pipeline.py` 的离线骨架提供**确定性、可复现**的输入，
覆盖 `CDX-20261022-014` §4/§5 要求的序列形态：顺序、跳帧、迟到、重复/乱序、零框、多框、边缘框、
过期、超时/错误/丢帧与无效记录。

诚实边界
========
- 本模块产出的记录**不是阶段4 输出**：`source_kind="synthetic"`、`capture_time_available=false`、
  `unavailable_fields=["capture_time_ns"]`；其中 `capture_time_ns` 是**合成单调时钟值**，只用于年龄
  算术演练，**不得**解释为真实采集时刻，也不得用于任何采集 FPS / 端到端延迟结论。
- 随机性只用 `random.Random(seed)`；种子与样本数由
  `docs/stage5/s5t03_offline_skeleton_params_v1.json` 冻结。
- 不读硬件、不读 UART、不读阶段4 证据；不生成图片。

`mixed` 模式的固定节奏（`index % 32`，与冻结样本数 240 帧配合）：
    0..7 正常（1–3 框） | 8 重复结果键 | 9 乱序结果键（`frame_id` 回退 3） | 10 15 框 | 11 含裁剪后零面积框
    12..26 空档（无新结果 ⇒ 年龄增长 ⇒ 过期，且同一结果键只计一次）
    27 DROPPED | 28 NO_HAND 零框 | 29 TIMEOUT | 30 无效记录（NO_HAND 带框） | 31 ERROR

**B-2**：模式 8/9 注入的重复与乱序属于阶段4 r04 `frame_sequence_rules` 规定**必须拒绝并记 FAIL** 的输入；
骨架对两者同构处理（只计数、不采用、不绘制），因此这些记录**不会**成为后续帧的叠加内容来源。
"""

from __future__ import annotations

import random
from typing import Any

HERE_HELP = "本模块由调用方保证 sys.path 含 scripts/stage5_t03"

try:                                    # 作为脚本目录内模块导入（测试/证据脚本的用法）
    import s5t03_display_pipeline as P
except ModuleNotFoundError:             # pragma: no cover - 兼容以包路径导入
    import pathlib
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import s5t03_display_pipeline as P

# 源帧归一化坐标（原图 1280×720），确定性、正面积
DETECTION_BOXES: tuple[tuple[float, float, float, float], ...] = (
    (0.10, 0.10, 0.30, 0.35),
    (0.55, 0.20, 0.80, 0.50),
    (0.70, 0.60, 0.95, 0.90),
    (0.02, 0.88, 0.22, 0.99),
    (0.40, 0.02, 0.60, 0.12),
)
# 裁剪后零面积（部分越界且裁到边界上）
ZERO_AREA_BOX: tuple[float, float, float, float] = (-0.50, -0.50, 0.0, 0.40)
MIXED_MODULUS = 32


def make_detection(index: int, *, box: tuple[float, float, float, float] | None = None,
                   score: float | None = None) -> dict[str, Any]:
    """构造一条 detection（字段名与 S5A-G0-v2 §7 的 detection_fields 一致）。"""
    class_id = index % len(P.CLASS_ORDER)
    if box is None:
        box = DETECTION_BOXES[index % len(DETECTION_BOXES)]
    if score is None:
        score = 0.50 + 0.01 * (index % 10)
    return {
        "class_id": class_id,
        "class_name": P.CLASS_ORDER[class_id],
        "score": float(score),
        "xyxy": [float(v) for v in box],
        "source_order": int(index),
    }


def make_record(*, session_id: int, frame_id: int, result_seq: int, sequence: int,
                capture_time_ns: int, result_time_ns: int, inference_time_ns: int,
                state: str = "OK", stale: bool = False,
                detections: list[dict[str, Any]] | None = None,
                dropped_frames: int = 0, error_code: int = 0,
                source_kind: str = "synthetic",
                repeat_index: int = 1) -> dict[str, Any]:
    """按阶段4 消费记录 schema 构造一条**合成**记录（逐处可辨：source_kind=synthetic）。"""
    detections = list(detections or [])
    return {
        # ── 关联键（对齐阶段4 S4-B 草案 mapping_key_roles）────────────────
        "session_id": int(session_id),
        "frame_id": int(frame_id),
        "result_seq": int(result_seq),
        "repeat_index": int(repeat_index),
        "sequence": int(sequence),
        "source_kind": source_kind,
        # ── 范围声明：非 camera ⇒ 采集时间不可用（阶段4 草案要求）──────────
        "capture_time_available": False,
        "unavailable_fields": ["capture_time_ns"],
        "synthetic_clock_note": "capture_time_ns 为合成单调时钟值，不是真实采集时刻",
        # ── 消费字段（S5A-G0-v2 §7）──────────────────────────────────────
        "geometry": {"width": 1280, "height": 720},
        "state": state,
        "detection_count": len(detections),
        "detections": detections,
        "stale": bool(stale),
        "dropped_frames": int(dropped_frames),
        "capture_time_ns": int(capture_time_ns),
        "result_time_ns": int(result_time_ns),
        "inference_time_ns": int(inference_time_ns),
        "end_to_end_latency_ns": int(result_time_ns - capture_time_ns),
        "error_code": int(error_code),
    }


class _Factory:
    """流内递增序号 + 记录构造；保证同一次运行内 `(session_id, frame_id, result_seq)` 语义清晰。"""

    def __init__(self, *, session_id: int, frame_period_ns: int,
                 base_capture_ns: int) -> None:
        self.session_id = session_id
        self.period_ns = frame_period_ns
        self.base_capture_ns = base_capture_ns
        self.result_seq = 0
        self.sequence = 0

    def capture_ns(self, frame_id: int) -> int:
        return self.base_capture_ns + frame_id * self.period_ns

    def _bump(self) -> tuple[int, int]:
        self.result_seq += 1
        self.sequence += 1
        return self.result_seq, self.sequence

    def ok(self, *, frame_id: int, detections: list[dict[str, Any]]) -> dict[str, Any]:
        seq, sequence = self._bump()
        capture = self.capture_ns(frame_id)
        return make_record(session_id=self.session_id, frame_id=frame_id, result_seq=seq,
                           sequence=sequence, capture_time_ns=capture,
                           result_time_ns=capture + self.period_ns // 3,
                           inference_time_ns=self.period_ns // 2, state="OK",
                           detections=detections)

    def special(self, *, frame_id: int, state: str, detections: list[dict[str, Any]] | None = None,
                dropped_frames: int = 0, error_code: int = 0) -> dict[str, Any]:
        seq, sequence = self._bump()
        capture = self.capture_ns(frame_id)
        return make_record(session_id=self.session_id, frame_id=frame_id, result_seq=seq,
                           sequence=sequence, capture_time_ns=capture,
                           result_time_ns=capture + self.period_ns // 3,
                           inference_time_ns=self.period_ns // 2, state=state,
                           detections=list(detections or []), dropped_frames=dropped_frames,
                           error_code=error_code)

    def out_of_order(self, *, frame_id: int, detections: list[dict[str, Any]]) -> dict[str, Any]:
        """`frame_id` 回退、但结果键仍为新键的乱序输入（B-2）。

        该记录按阶段4 r04 `frame_sequence_rules`（`regressed_frame_id`）属于**必须拒绝并记 FAIL** 的输入：
        骨架据此不采用、不绘制，只计数并记录拒绝原因。这里只回退 `frame_id`、`result_seq` 仍取新值，
        以保证结果键 `(session_id, frame_id, result_seq)` 唯一、分类确定（不与该帧历史接受记录撞键）。
        """
        self.sequence += 1
        self.result_seq += 1
        capture = self.capture_ns(max(0, frame_id))
        return make_record(session_id=self.session_id, frame_id=max(0, frame_id),
                           result_seq=self.result_seq, sequence=self.sequence, capture_time_ns=capture,
                           result_time_ns=capture + self.period_ns // 3,
                           inference_time_ns=self.period_ns // 2, state="OK",
                           detections=detections)

    def equivalent(self, *, frame_id: int, detections: list[dict[str, Any]],
                   declared: bool) -> dict[str, Any]:
        """同 session **等价 frame_id** + 新 `result_seq`（NB-1）。

        - `declared=False`：未声明重复/重放（`repeat_index=1`）⇒ 按 r04 `duplicate_frame_id`
          必须**拒绝并记 FAIL**，不采用、不绘制；
        - `declared=True`：显式声明（`repeat_declared=true` 且 `repeat_index=2`）⇒ 走放行路径，
          用于证明"拒绝"不是无条件拒绝。
        """
        self.sequence += 1
        self.result_seq += 1
        capture = self.capture_ns(max(0, frame_id))
        record = make_record(session_id=self.session_id, frame_id=max(0, frame_id),
                             result_seq=self.result_seq, sequence=self.sequence, capture_time_ns=capture,
                             result_time_ns=capture + self.period_ns // 3,
                             inference_time_ns=self.period_ns // 2, state="OK",
                             detections=detections, repeat_index=2 if declared else 1)
        if declared:
            record["repeat_declared"] = True
        return record


def regressed_frame_id(index: int) -> int:
    """乱序注入用的回退帧号（B-2）：比当前显示帧小 3，必然小于上一已接受 frame_id。"""
    return max(0, index - 3)


def equivalent_frame_id(index: int) -> int:
    """NB-1 注入用的**等价**帧号：等于上一已接受 frame_id（不小、不新）。"""
    return max(0, index - 1)


def _normal_detections(index: int, *, count: int | None = None,
                       include_zero_area: bool = False,
                       rng: random.Random | None = None) -> list[dict[str, Any]]:
    """正常检测框；给了 `rng` 时按种子抖动分数（种子决定同一 RunId 的可复现输入）。"""
    n = count if count is not None else 1 + (index % 3)
    detections = [make_detection(i, score=(0.50 + 0.40 * rng.random()) if rng else None)
                  for i in range(n)]
    if include_zero_area:
        detections.append(make_detection(len(detections), box=ZERO_AREA_BOX, score=0.60))
    return detections


def build_stream(mode: str, frames: int, *, params: dict[str, Any], seed: int,
                 frame_period_ns: int, base_capture_ns: int = 1_000_000_000,
                 session_id: int = 7, warmup_frames: int = 0) -> list[dict[str, Any]]:
    """生成提交步骤序列：每步 = 一帧显示（先给 results，再提交该帧）。"""
    if mode not in {"sequential", "skip", "late", "dup", "ooo", "equiv", "mixed"}:
        raise P.SkeletonInputError(f"未知流模式 {mode!r}")
    rng = random.Random(seed)
    factory = _Factory(session_id=session_id, frame_period_ns=frame_period_ns,
                       base_capture_ns=base_capture_ns)
    steps: list[dict[str, Any]] = []
    last_record: dict[str, Any] | None = None
    skip_gap = range(frames // 3, frames // 3 + 16)   # 跳帧模式中段空档 ⇒ age_frame > 200 ms

    for index in range(frames):
        commit_ns = factory.capture_ns(index) + frame_period_ns // 2
        results: list[dict[str, Any]] = []
        if index < warmup_frames:
            steps.append({"displayed_frame_id": index, "overlay_commit_ns": commit_ns,
                          "results": results, "warmup": True})
            continue

        fresh = False
        if mode == "sequential":
            fresh = True
        elif mode == "skip":
            fresh = (index % 3 == 0) and index not in skip_gap
        elif mode == "late":
            fresh = index >= 2
            if fresh:
                record = factory.ok(frame_id=index - 2,
                                    detections=_normal_detections(index))
                results.append(record)
                last_record = record
                fresh = False
        elif mode in ("dup", "ooo"):
            fresh = True
        elif mode == "equiv":
            fresh = True
        elif mode == "mixed":
            pattern = index % MIXED_MODULUS
            if pattern in (8, 9):
                pass                                  # 先给重复/乱序键，再给正常新结果
            elif pattern == 10:
                pass
            elif pattern == 11:
                pass
            elif 12 <= pattern <= 26:
                fresh = False                          # 空档：复用上一条 ⇒ 过期
            elif pattern == 27:
                results.append(factory.special(frame_id=index, state="DROPPED", dropped_frames=1))
                last_record = results[-1]
                fresh = False
            elif pattern == 28:
                results.append(factory.special(frame_id=index, state="NO_HAND"))
                last_record = results[-1]
                fresh = False
            elif pattern == 29:
                results.append(factory.special(frame_id=index, state="TIMEOUT", error_code=4))
                last_record = results[-1]
                fresh = False
            elif pattern == 30:
                results.append(factory.special(frame_id=index, state="NO_HAND",
                                               detections=[make_detection(0)]))
                fresh = False
            elif pattern == 31:
                results.append(factory.special(frame_id=index, state="ERROR", error_code=3))
                last_record = results[-1]
                fresh = False
            else:
                fresh = True

            pattern = index % MIXED_MODULUS
            if pattern == 8 and last_record is not None:
                results.append(dict(last_record))      # 重复结果键：只计数、不更新最新结果
            elif pattern == 9 and last_record is not None:
                results.append(factory.out_of_order(frame_id=regressed_frame_id(index),
                                                    detections=_normal_detections(index)))
                last_record = results[-1]
            elif pattern == 10:
                fresh = True
            elif pattern == 11:
                fresh = True

        if mode == "dup" and index % 7 == 0 and last_record is not None:
            results.append(dict(last_record))
        if mode == "ooo" and index % 5 == 0 and last_record is not None:
            results.append(factory.out_of_order(frame_id=regressed_frame_id(index),
                                                detections=_normal_detections(index)))
            last_record = results[-1]
            fresh = False        # 该帧不产生新的已接受结果 ⇒ 可直接观察「拒绝不更新最新结果」
        if mode == "equiv" and index % 5 == 2 and index >= 2:
            declared = (index % 10 == 2)   # 每 10 帧一次走显式声明放行路径，其余为未声明 ⇒ 必拒绝
            results.append(factory.equivalent(frame_id=equivalent_frame_id(index),
                                              detections=_normal_detections(index),
                                              declared=declared))
            if not declared:
                last_record = results[-1]
                fresh = False              # 未声明等价帧被拒 ⇒ 本帧不产生新的已接受结果

        if fresh:
            count = 15 if (mode == "mixed" and index % MIXED_MODULUS == 10) else None
            include_zero_area = (mode == "mixed" and index % MIXED_MODULUS == 11)
            record = factory.ok(frame_id=index,
                                detections=_normal_detections(
                                    index, count=count, include_zero_area=include_zero_area,
                                    rng=rng if mode == "mixed" else None))
            results.append(record)
            last_record = record

        steps.append({"displayed_frame_id": index, "overlay_commit_ns": commit_ns,
                      "results": results, "warmup": False})
    return steps


def summarize_steps(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """流自身的元信息（不参与判定，仅供证据包登记）。"""
    submissions = sum(len(step["results"]) for step in steps)
    return {"steps": len(steps), "result_submissions": submissions,
            "warmup_steps": sum(1 for step in steps if step.get("warmup"))}