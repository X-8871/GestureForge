#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 阶段4 **冻结包消费者**：冻结回放结果包 → 阶段5 显示路径可用的逐帧输入（离线）。

角色与口径（不得自创）
======================
- 输入：阶段4 冻结回放包（`s4t26_gate_rerun_20261027_r04` 的 10 个文件）+ 冻结记录
  `s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json` + 共享结果契约
  `s4-shared-io` v1.3.0（`FROZEN_OFFLINE_ONLY`）。
- 消费前**必须**逐文件复算 sha256 与 bytes（`s5t03_freeze_integrity`），任一不符即拒绝消费；
  同时现场复算契约 `upstream_bindings` 漂移。
- 结果字段严格按契约 `result_contract.result_record.fields`；检测字段按
  `result_contract.result_record.detection_fields`（含 `xyxy_px`）；显示五元组按
  `result_contract.display_linkage`。字段名与 `scripts/stage5_t03/s5t03_dynamic_stream.py`
  的输入绑定结构一致，**不另立第二套语义**；几何换算只调用冻结参考
  `verification/s5_display_geometry_reference.py`（不重写逆映射）。

输入口径标签（本消费者产出，覆盖既有 `synthetic_replay`）
=========================================================
`input_kind="stage4_frozen_replay"`、`consumption_mode="replay_only"`、
`evidence_kind="offline_replay"`，并逐产物写明「离线主机回放；不代表 PL、实物或实时检测输出」。

时间口径（**注入陷阱**的处理，见 `resolve_timing`）
=================================================
- `camera`/真实回放：`capture_time_ns` 取冻结包**已文档化的真实抓取时刻**（非零），基准显式声明为
  `documented_stage3_wallclock_second_unix_epoch`（clock_domain=`replay_documented_wallclock`，
  秒级精度），**不是** PS 单调采集时刻。
- `FILE_INJECTION`：`capture_time_ns` 按 S4-A 约定为 **0 哨兵** ⇒ `end_to_end_latency_ns` **不可定义**；
  `injection_start_ns` **绝不**被当作实测采集时间（逐帧显式标注）。
- 本冻结包声明 `stale_evaluation=NOT_RUN_OFFLINE_REPLAY_HAS_NO_MONOTONIC_PUBLISH_CLOCK`
  ⇒ `result_time_ns`/`inference_time_ns`/`end_to_end_latency_ns`/`age_result_ns`/`age_frame_ns`
  一律 `null` + 逐字段基准说明；**不伪造**年龄或延迟。

诚实边界
========
只允许声明：离线回放口径下的数值一致性、task-27 结果包可被阶段5 消费。
禁止声明：板上行为/PL 真实运行、UART 实收/真帧、真实摄像头采集质量或颜色、P/4-D/G3/G4/G5 任一项通过、
把回放结果当实时结果。板上真实回放仍需硬件 OFFER/CLAIM + 八类门禁（当前 0/8）。
本模块不接板卡，不启动 vivado/xsdb/hw_server/vitis/xsim。

退出码：0 = 消费成功且自检通过；1 = 判定失败；2 = 环境/输入缺失。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Iterable, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
for _candidate in (str(REPO_ROOT), str(pathlib.Path(__file__).resolve().parent)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_freeze_integrity as FI  # noqa: E402

SCHEMA_VERSION = "gestureforge_s5t03_stage4_frozen_replay_v1"

# ── 输入口径标签（必须从 synthetic_replay 改为真实回放）──────────────────────
INPUT_KIND = "stage4_frozen_replay"
CONSUMPTION_MODE = "replay_only"
EVIDENCE_KIND = "offline_replay"
BUFFER_SCOPE = "offline_host"
SCOPE_STATEMENT = "离线主机回放；不代表 PL、实物或实时检测输出"
FORBIDDEN_CLAIMS = [
    "板上行为 / PL 真实运行",
    "UART 实收 / S2BU 真帧",
    "真实摄像头采集质量或颜色",
    "P / 4-D / G3 / G4 / G5 任一项通过",
    "把回放结果当实时结果",
]
SYNTHETIC_MARKERS = ("synthetic", "synthetic_replay", "synthetic_dynamic_reference")

# ── 时间基准常量（逐帧显式声明，禁止冒用 injection_start_ns）────────────────
CAPTURE_BASIS_DOCUMENTED = "documented_stage3_wallclock_second_unix_epoch"
CAPTURE_BASIS_ZERO_SENTINEL = "zero_sentinel_file_injection_contract"
PUBLISH_BASIS_UNAVAILABLE = "UNAVAILABLE_OFFLINE_REPLAY_NO_MONOTONIC_PUBLISH_CLOCK"
INFERENCE_BASIS_UNAVAILABLE = "UNAVAILABLE_OFFLINE_HOST_CPU_ELAPSED_IS_NOT_PS_INFERENCE_TIME"
E2E_BASIS_UNAVAILABLE = "UNAVAILABLE_NO_PUBLISH_INSTANT_IN_SAME_CLOCK_DOMAIN_AS_CAPTURE"
E2E_BASIS_INJECTION_SENTINEL = "UNAVAILABLE_CAPTURE_TIME_NS_IS_ZERO_SENTINEL_FILE_INJECTION"
AGE_FRAME_BASIS_UNAVAILABLE = (
    "UNAVAILABLE: 回放无单调发布时钟，t_overlay_commit 与 t_capture 无可比同域时间；"
    "基准声明=documented_stage3_wallclock_second_unix_epoch，绝不使用 injection_start_ns 冒充实测采集时间"
)
STALE_EVALUATION_NOT_RUN = "NOT_RUN_OFFLINE_REPLAY_HAS_NO_MONOTONIC_PUBLISH_CLOCK"
NOT_DECLARED = "NOT_DECLARED_IN_FROZEN_PACKAGE"

DEFAULT_PACKAGE_DIR = pathlib.Path(
    r"D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t26_gate_rerun_20261027_r04")
DEFAULT_FREEZE_RECORD = pathlib.Path(
    r"D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t27_replay_package_freeze_20261027_r01"
    r"\replay_package_freeze.json")
DEFAULT_CONTRACT = pathlib.Path(r"D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json")

NOT_RUN = [
    "板上真实回放接入（需硬件 OFFER/CLAIM + 八类门禁；当前记录 0/8）",
    "真实采集路径（摄像头未到货）与真实连续帧周期",
    "PS 单调发布时刻 / 结果年龄 / 端到端延迟（冻结包声明 stale_evaluation=NOT_RUN）",
    "P / 4-D / G3 / G4 / G5 关口判定（不归本任务）",
]


class LabelViolation(RuntimeError):
    """输入口径标签不合规（例如被改回 synthetic）⇒ 拒绝产出/消费。"""


class ConsumerError(RuntimeError):
    """输入结构不满足冻结包/契约（不静默降级）。"""


def _looks_synthetic(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(marker in lowered for marker in SYNTHETIC_MARKERS)


# 允许出现 synthetic 字样的位置（均为「说明/拒绝」用途，不是被采纳的标签）
SYNTHETIC_EXEMPT_KEYS = ("previous_label", "synthetic_refusal_note", "forbidden_claims",
                         "synthetic_marker_note")


def scan_synthetic_markers(node: Any, *, path: str = "$") -> list[str]:
    """递归扫描被采纳的标签值里是否出现 synthetic（说明性字段置于豁免键下）。"""
    found: list[str] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            child = f"{path}.{key}"
            if key in SYNTHETIC_EXEMPT_KEYS:
                continue
            found.extend(scan_synthetic_markers(value, path=child))
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            found.extend(scan_synthetic_markers(value, path=f"{path}[{index}]"))
    elif _looks_synthetic(node):
        found.append(f"{path}={node!r}")
    return found


def label_problems(payload: Mapping[str, Any]) -> list[str]:
    """返回标签问题列表（空＝合规则）；供消费者断言与独立检查器共用同一判据。"""
    problems: list[str] = []
    if payload.get("input_kind") != INPUT_KIND:
        problems.append(f"input_kind={payload.get('input_kind')!r} != {INPUT_KIND!r}")
    if payload.get("consumption_mode") != CONSUMPTION_MODE:
        problems.append(f"consumption_mode={payload.get('consumption_mode')!r} != {CONSUMPTION_MODE!r}")
    if payload.get("evidence_kind") != EVIDENCE_KIND:
        problems.append(f"evidence_kind={payload.get('evidence_kind')!r} != {EVIDENCE_KIND!r}")
    if payload.get("scope_statement") != SCOPE_STATEMENT:
        problems.append("scope_statement 缺失或与冻结口径文本不一致")
    for hit in scan_synthetic_markers(payload):
        problems.append(f"synthetic 标记出现在被采纳字段：{hit}")
    return problems


def assert_replay_labels(payload: Mapping[str, Any], *, where: str) -> None:
    """标签守卫：必须是真实回放口径，且不得出现 synthetic 标签（fail-closed）。"""
    problems = label_problems(payload)
    if problems:
        raise LabelViolation(f"{where} 标签不合规：" + "；".join(problems))


def load_frozen_package(*, package_dir: pathlib.Path, freeze_record_path: pathlib.Path,
                        contract_json: pathlib.Path, drift: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    """先复算完整性（逐文件 sha256+bytes、契约绑定、漂移），再加载冻结包。"""
    integrity = FI.verify_all(freeze_record_path=freeze_record_path, package_dir=package_dir,
                              contract_json=contract_json, drift=drift)
    FI.require_consumable(integrity)
    package_path = pathlib.Path(package_dir) / "task27_replay_result_package.json"
    if not package_path.is_file():
        raise ConsumerError(f"冻结包缺 task27_replay_result_package.json：{package_path}")
    package = json.loads(package_path.read_text(encoding="utf-8"))
    return package, integrity


# ── 几何换算：只走冻结参考实现 ──────────────────────────────────────────────
def project_xyxy_to_px(xyxy: Iterable[float], canvas_width: int, canvas_height: int) -> dict[str, Any]:
    """归一化原图坐标 → 画布像素索引（先裁剪、最后一次性取整；规则来自冻结参考）。"""
    clipped = R.clip_unit_box(list(xyxy))
    if clipped["zero_area"]:
        return {"xyxy": [float(v) for v in clipped["xyxy"]], "clipped": bool(clipped["clipped"]),
                "zero_area": True, "px": None, "border_pixels": 0}
    px = R.original_norm_to_display_px(clipped["xyxy"], canvas_width, canvas_height)
    border = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"], R.DISPLAY_LINE_WIDTH_PX,
                                 canvas_width, canvas_height)
    return {"xyxy": [float(v) for v in clipped["xyxy"]], "clipped": bool(clipped["clipped"]),
            "zero_area": False, "px": {axis: int(px[axis]) for axis in ("x1", "y1", "x2", "y2")},
            "border_pixels": len(border)}


def map_detection(prediction: Mapping[str, Any], *, source_ref: str, source_index: int,
                  canvas_width: int, canvas_height: int) -> dict[str, Any]:
    """按契约 `detection_fields` 映射一条检测，并派生 `xyxy_px`（冻结参考换算）。"""
    xyxy = [float(v) for v in prediction["xyxy"]]
    projection = project_xyxy_to_px(xyxy, canvas_width, canvas_height)
    return {
        "class_id": int(prediction["class_id"]),
        "class_name": str(prediction["class_name"]),
        "score": float(prediction["score"]),
        "xyxy": xyxy,
        "xyxy_px": projection["px"],
        "source_order": int(prediction["source_order"]),
        # ── 溯源与几何中间量（便于独立对拍，不改变契约语义）──────────────────
        "source_ref": source_ref,
        "source_index": int(source_index),
        "xyxy_clipped": projection["xyxy"],
        "xyxy_clipped_flag": projection["clipped"],
        "zero_area": projection["zero_area"],
        "border_pixels": int(projection["border_pixels"]),
        "xyxy_px_rule": f"{R.ROUNDING_RULE} via R.original_norm_to_display_px(fit=exact)",
        "xyxy_px_canvas": [int(canvas_width), int(canvas_height)],
    }


# ── 时间口径 ────────────────────────────────────────────────────────────────
def resolve_timing(frame: Mapping[str, Any], *, state: str) -> dict[str, Any]:
    """解析逐帧时间基准；`FILE_INJECTION` 的 0 哨兵一律使端到端延迟不可定义。"""
    mode = str(frame.get("mode") or "")
    capture_available = bool(frame.get("capture_time_available", False))
    capture_value = frame.get("capture_time_ns")
    injection_start = frame.get("injection_start_ns")
    sentinel = (mode == "FILE_INJECTION") or (capture_value in (0, None)) or (not capture_available)
    basis: dict[str, Any] = {
        "capture_time_ns": {
            "value": capture_value,
            "defined": not sentinel,
            "basis": CAPTURE_BASIS_ZERO_SENTINEL if sentinel else CAPTURE_BASIS_DOCUMENTED,
            "clock_domain": frame.get("clock_domain"),
            "precision": frame.get("source_capture_time_precision"),
            "text": frame.get("source_capture_time_text"),
            "is_measured_capture_clock": False,
            "note": ("FILE_INJECTION 0 哨兵：不得当作实测采集时间" if sentinel else
                     "已文档化的真实抓取时刻（秒级、墙钟口径），不是 PS 单调采集计数"),
        },
        "result_time_ns": {
            "value": None, "defined": False, "basis": PUBLISH_BASIS_UNAVAILABLE,
            "note": f"冻结包声明 stale_evaluation={STALE_EVALUATION_NOT_RUN}",
        },
        "inference_time_ns": {
            "value": None, "defined": False, "basis": INFERENCE_BASIS_UNAVAILABLE,
            "offline_host_elapsed_ms": frame.get("offline_host_elapsed_ms"),
            "note": "offline_host_elapsed_ms 是离线主机 CPU 墙钟耗时，不是 PS 推理时间，不得填作 inference_time_ns",
        },
        "end_to_end_latency_ns": {
            "value": None, "defined": False,
            "basis": E2E_BASIS_INJECTION_SENTINEL if sentinel else E2E_BASIS_UNAVAILABLE,
            "note": ("FILE_INJECTION 下 capture_time_ns 为 0 哨兵 ⇒ 端到端延迟不可定义" if sentinel else
                     "回放无与采集同域的发布时刻 ⇒ 端到端延迟不可定义"),
        },
        "injection_start_ns": injection_start,
        "injection_start_ns_used_as_capture_time": False,
        "stale_evaluation": str(frame.get("stale_evaluation") or STALE_EVALUATION_NOT_RUN),
        "age_frame_ns_basis": AGE_FRAME_BASIS_UNAVAILABLE,
        "state_for_timing": state,
    }
    if injection_start is not None and capture_value == injection_start:
        raise ConsumerError("injection_start_ns 被当作 capture_time_ns：契约禁止，拒绝消费")
    return basis


# ── 逐帧输入记录 ────────────────────────────────────────────────────────────
class FrameSpec:
    """一条待投影的冻结结果（帧或门禁样本），显式区分归属。"""

    def __init__(self, *, attribution: str, source_ref: str, frame_id: int, result_seq: int,
                 session_id: int, repeat_index: int, sequence: int, source_kind: str,
                 width: int, height: int, stride_bytes: int, detections: list[dict[str, Any]],
                 raw_candidate_count: int, nms_output_count: int, timing_source: Mapping[str, Any],
                 display_eligible: bool, sample_id: str | None, notes: str) -> None:
        self.attribution = attribution
        self.source_ref = source_ref
        self.frame_id = frame_id
        self.result_seq = result_seq
        self.session_id = session_id
        self.repeat_index = repeat_index
        self.sequence = sequence
        self.source_kind = source_kind
        self.width = width
        self.height = height
        self.stride_bytes = stride_bytes
        self.detections = detections
        self.raw_candidate_count = raw_candidate_count
        self.nms_output_count = nms_output_count
        self.timing_source = timing_source
        self.display_eligible = display_eligible
        self.sample_id = sample_id
        self.notes = notes


def gate_sample_shape(package: Mapping[str, Any], bridge_doc: Mapping[str, Any] | None) -> list[int]:
    """门禁样本原图尺寸：先取冻结包字段，缺则取同包 `replay_forward_bridge_result.json` 的明细；
    两者都没有即拒绝（不得猜尺寸）。"""
    gate = package.get("positive_detection_gate") or {}
    shape = gate.get("input_shape_bgr")
    if not shape and bridge_doc:
        checks = bridge_doc.get("checks") or {}
        detail = ((checks.get("positive_detection_gate_forward_d9_nms") or {}).get("detail") or {})
        shape = detail.get("input_shape_bgr")
    if not shape:
        raise ConsumerError("阳性门禁样本缺 input_shape_bgr（冻结包与桥接结果均无）⇒ 无法确定画布，拒绝消费")
    return [int(v) for v in shape]


def extract_frame_specs(package: Mapping[str, Any],
                        bridge_doc: Mapping[str, Any] | None = None) -> list[FrameSpec]:
    """从冻结包提取逐帧/逐样本规格（字段名以冻结包实际内容为准，不凭猜）。"""
    key = package["contract_result_key"]
    session_id, frame_id, result_seq = int(key["session_id"]), int(key["frame_id"]), int(key["result_seq"])
    replay = package["replay_frame"]
    d9 = replay["d9"]
    predictions = list(d9.get("decoded_predictions") or [])
    specs = [FrameSpec(
        attribution="frozen_replay_frame_result",
        source_ref="replay_frame.d9.decoded_predictions",
        frame_id=frame_id, result_seq=result_seq, session_id=session_id,
        repeat_index=1, sequence=1, source_kind=str(replay.get("source_kind")),
        width=int(replay["width"]), height=int(replay["height"]), stride_bytes=int(replay["stride_bytes"]),
        detections=predictions,
        raw_candidate_count=int(d9.get("raw_candidate_count_before_stable_nms", 0)),
        nms_output_count=len(predictions),
        timing_source=replay, display_eligible=True, sample_id=None,
        notes="冻结回放帧本体（dbdf 阶段3 frame_full.bin 的离线回放结果）；无候选 ⇒ 合法 NO_HAND 零框",
    )]
    gate = package.get("positive_detection_gate") or {}
    gate_nms = gate.get("d9_nms") or {}
    gate_predictions = list(gate_nms.get("predictions") or [])
    t29_predictions = list(gate_nms.get("t29_reference_predictions") or [])
    gate_shape = gate_sample_shape(package, bridge_doc)
    gate_w, gate_h = gate_shape[1], gate_shape[0]
    gate_timing = dict(replay)
    gate_timing["source_capture_time_text"] = None
    gate_timing["capture_time_ns"] = 0                     # 门禁样本未声明抓取时刻 ⇒ 0 哨兵口径
    gate_timing["capture_time_available"] = False
    gate_timing["mode"] = "GATE_SAMPLE_NOT_A_REPLAY_FRAME"
    for label, preds in (("d9_nms.predictions", gate_predictions),
                         ("d9_nms.t29_reference_predictions", t29_predictions)):
        specs.append(FrameSpec(
            attribution="gate_evidence_sample_not_replay_frame",
            source_ref=f"positive_detection_gate.{label}",
            frame_id=frame_id, result_seq=result_seq, session_id=session_id,
            repeat_index=1, sequence=1, source_kind=str(replay.get("source_kind")),
            width=gate_w, height=gate_h, stride_bytes=None, detections=preds,
            raw_candidate_count=int(gate_nms.get("raw_candidate_count_before_stable_nms", 0)),
            nms_output_count=int(gate_nms.get("nms_output_count", len(preds))),
            timing_source=gate_timing, display_eligible=False, sample_id=gate.get("sample_id"),
            notes=("阳性检测门禁样本的检测几何（独立对拍用）；**不属于**回放帧，"
                   "不进入显示流，也不代表回放帧检出目标"),
        ))
    return specs


def derive_state(detections: list[dict[str, Any]], raw_candidate_count: int) -> str:
    if detections:
        return "OK"
    return "NO_HAND"          # 合法零框（契约：NO_HAND 必须零框、非过期）


def build_frame_record(spec: FrameSpec) -> dict[str, Any]:
    """按契约 result_record 构造一条阶段5 可用输入记录（含逐帧时间基准声明）。"""
    detections = [map_detection(pred, source_ref=f"{spec.source_ref}[{index}]", source_index=index,
                                canvas_width=spec.width, canvas_height=spec.height)
                  for index, pred in enumerate(spec.detections)]
    state = derive_state(detections, spec.raw_candidate_count)
    timing = resolve_timing(spec.timing_source, state=state)
    record: dict[str, Any] = {
        # ── 关联键（对齐阶段4 S4-B mapping_key_roles）─────────────────────
        "session_id": spec.session_id,
        "frame_id": spec.frame_id,
        "result_seq": spec.result_seq,
        "repeat_index": spec.repeat_index,
        "sequence": spec.sequence,
        "source_kind": spec.source_kind,
        # ── 消费字段（契约 result_record.fields）─────────────────────────
        "geometry": {
            "width": spec.width, "height": spec.height,
            "stride_bytes": spec.stride_bytes,
            "stride_bytes_basis": ("replay_frame.stride_bytes" if spec.stride_bytes is not None
                                   else NOT_DECLARED),
            "pixel_format": "BGR888", "byte_order": "BGR", "coordinate_origin": "top_left",
            "source_ref": spec.source_ref,
            "display_canvas": [spec.width, spec.height], "display_fit": "exact",
            "mapping_function": "R.original_norm_to_display_px (fit=exact)",
            "rounding_rule": R.ROUNDING_RULE,
        },
        "state": state,
        "detection_count": len(detections),
        "detections": detections,
        "candidate_count": spec.nms_output_count,
        "candidate_count_pre_threshold": spec.raw_candidate_count,
        "candidate_overflow": None,
        "capture_time_ns": timing["capture_time_ns"]["value"],
        "result_time_ns": timing["result_time_ns"]["value"],
        "inference_time_ns": timing["inference_time_ns"]["value"],
        "end_to_end_latency_ns": timing["end_to_end_latency_ns"]["value"],
        "dropped_frames": None,
        "stale": None,
        "error_code": 0,
        # ── 口径标签（真实回放；覆盖既有 synthetic_replay）─────────────────
        "input_kind": INPUT_KIND,
        "consumption_mode": CONSUMPTION_MODE,
        "evidence_kind": EVIDENCE_KIND,
        "buffer_scope": BUFFER_SCOPE,
        "scope_statement": SCOPE_STATEMENT,
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        # ── 逐帧时间/字段基准（显式声明，禁止默认值）──────────────────────
        "timing_available": False,
        "timing_basis": timing,
        "field_bases": {
            "candidate_overflow": NOT_DECLARED,
            "dropped_frames": NOT_DECLARED,
            "stale": NOT_DECLARED + "（冻结包只给 stale_evaluation=" + STALE_EVALUATION_NOT_RUN + "）",
            "error_code": "derived_from_frozen_bridge_run_status（离线回放无 PS error_code）",
            "inference_time_ns": INFERENCE_BASIS_UNAVAILABLE,
        },
        # ── 归属（防止把门禁样本冒充回放帧检出）──────────────────────────
        "attribution": spec.attribution,
        "is_replay_frame": spec.attribution == "frozen_replay_frame_result",
        "display_eligible": spec.display_eligible,
        "sample_id": spec.sample_id,
        "attribution_note": spec.notes,
    }
    assert_replay_labels(record, where=f"frame_record[{spec.source_ref}]")
    problems = R.validate_result_record(record)
    if problems:
        raise ConsumerError(f"产出记录未通过冻结参考校验（{spec.source_ref}）：{problems}")
    return record


def build_five_tuple(record: Mapping[str, Any], *, displayed_frame_id: int) -> dict[str, Any]:
    """显示五元组：两个年龄**显式声明基准**；无单调发布时钟 ⇒ 值不可定义（null）。"""
    timing = record["timing_basis"]
    return {
        "displayed_frame_id": int(displayed_frame_id),
        "result_frame_id": int(record["frame_id"]),
        "age_result_ns": None,
        "age_frame_ns": None,
        "display_semantics": R.DISPLAY_SEMANTICS,
        "age_basis": {
            "age_result_ns": {"defined": False, "basis": PUBLISH_BASIS_UNAVAILABLE},
            "age_frame_ns": {"defined": False, "basis": AGE_FRAME_BASIS_UNAVAILABLE,
                             "capture_basis": timing["capture_time_ns"]["basis"],
                             "capture_time_ns": timing["capture_time_ns"]["value"]},
            "t_overlay_commit": None,
            "injection_start_ns": timing["injection_start_ns"],
            "injection_start_ns_used_as_capture_time": False,
        },
        "stale_evaluation": timing["stale_evaluation"],
        "display_eligible": bool(record.get("display_eligible")),
        "input_kind": INPUT_KIND,
        "consumption_mode": CONSUMPTION_MODE,
        "evidence_kind": EVIDENCE_KIND,
        "scope_statement": SCOPE_STATEMENT,
    }


def build_artifacts(*, package: Mapping[str, Any], package_dir: pathlib.Path,
                    integrity: Mapping[str, Any]) -> dict[str, Any]:
    bridge_path = pathlib.Path(package_dir) / "replay_forward_bridge_result.json"
    bridge_doc = json.loads(bridge_path.read_text(encoding="utf-8")) if bridge_path.is_file() else None
    specs = extract_frame_specs(package, bridge_doc)
    records: list[dict[str, Any]] = []
    five_tuples: list[dict[str, Any]] = []
    gate_projections: list[dict[str, Any]] = []
    for spec in specs:
        record = build_frame_record(spec)
        if spec.display_eligible:
            records.append(record)
            five_tuples.append(build_five_tuple(record, displayed_frame_id=record["frame_id"]))
        else:
            gate_projections.append(record)
    bridge = None
    if bridge_doc is not None:
        bridge = {"checker": bridge_doc.get("checker"), "checker_version": bridge_doc.get("checker_version"),
                  "status": bridge_doc.get("status"), "exit_code": bridge_doc.get("exit_code"),
                  "hardware_execution": bridge_doc.get("hardware_execution"),
                  "generated_utc8": bridge_doc.get("generated_utc8")}
    frames_payload = {
        "schema_version": SCHEMA_VERSION,
        "run_kind": "stage4_frozen_replay_consumption",
        "input_kind": INPUT_KIND, "consumption_mode": CONSUMPTION_MODE,
        "evidence_kind": EVIDENCE_KIND, "buffer_scope": BUFFER_SCOPE,
        "scope_statement": SCOPE_STATEMENT,
        "not_real_time_statement": "本流为离线主机回放产物；不代表实时检测输出。",
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "source_package": {
            "package_dir": str(package_dir),
            "task_id": package.get("task_id"),
            "contract_result_key": package.get("contract_result_key"),
            "marking": package.get("marking"),
        },
        "frames": records,
        "frame_count": len(records),
    }
    assert_replay_labels(frames_payload, where="frames_payload")
    counts = {
        "frames": len(records),
        "detections_total": sum(record["detection_count"] for record in records),
        "boxes_with_px": sum(1 for record in records for det in record["detections"] if det["xyxy_px"]),
        "five_tuples": len(five_tuples),
        "gate_projection_records": len(gate_projections),
        "gate_projection_boxes": sum(len(record["detections"]) for record in gate_projections),
        "gate_projection_axes": 4 * sum(len(record["detections"]) for record in gate_projections),
    }
    return {"frames_payload": frames_payload, "frames": records, "five_tuples": five_tuples,
            "gate_projections": gate_projections, "bridge": bridge, "counts": counts,
            "specs": specs}


def consumer_report(*, package: Mapping[str, Any], package_dir: pathlib.Path,
                    freeze_record_path: pathlib.Path, contract_json: pathlib.Path,
                    integrity: Mapping[str, Any], artifacts: Mapping[str, Any]) -> dict[str, Any]:
    counts = dict(artifacts["counts"])
    report = {
        "schema_version": SCHEMA_VERSION,
        "run_kind": "stage4_frozen_replay_consumption",
        "input_kind": INPUT_KIND, "consumption_mode": CONSUMPTION_MODE,
        "evidence_kind": EVIDENCE_KIND, "buffer_scope": BUFFER_SCOPE,
        "scope_statement": SCOPE_STATEMENT,
        "statement": "离线主机回放；不代表 PL、实物或实时检测输出",
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "source": {
            "package_dir": str(package_dir),
            "freeze_record_path": str(freeze_record_path),
            "freeze_record_run_id": integrity.get("freeze_record_run_id"),
            "contract_json_path": str(contract_json),
            "contract_sha256": integrity.get("contract_binding_check", {}).get("json_actual_sha256"),
            "contract_id": integrity.get("contract_binding_check", {}).get("declared_contract_id"),
            "contract_version": integrity.get("contract_binding_check", {}).get("declared_contract_version"),
            "contract_status": integrity.get("contract_binding_check", {}).get("declared_status"),
            "contract_result_key": package.get("contract_result_key"),
            "package_marking": package.get("marking"),
            "frozen_bridge_run": artifacts.get("bridge"),
        },
        "preconditions": {
            "file_integrity_all_pass": bool(integrity["file_integrity"]["all_pass"]),
            "file_integrity_ok": f"{integrity['file_integrity']['ok']}/{integrity['file_integrity']['checked']}",
            "contract_binding_all_pass": bool(integrity["contract_binding_check"]["all_pass"]),
            "upstream_binding_drift_all_pass": bool(integrity["upstream_binding_drift"]["all_pass"]),
            "upstream_binding_drift_ok": f"{integrity['upstream_binding_drift'].get('ok')}/"
                                         f"{integrity['upstream_binding_drift'].get('checked')}",
        },
        "counts": counts,
        "labels": {"previous_label": "synthetic_replay (既有骨架)",
                   "input_kind": INPUT_KIND, "consumption_mode": CONSUMPTION_MODE,
                   "evidence_kind": EVIDENCE_KIND,
                   "reason": "本产物消费阶段4 冻结回放结果包，必须按真实回放口径标注，不得沿用合成流标签"},
        "timing": {
            "capture_time_ns_basis": CAPTURE_BASIS_DOCUMENTED,
            "result_time_ns_defined": False,
            "end_to_end_latency_ns_defined": False,
            "age_defined": False,
            "stale_evaluation": STALE_EVALUATION_NOT_RUN,
            "injection_start_ns_used_as_capture_time": False,
            "note": "冻结包无 PS 单调发布时钟；不伪造年龄/延迟，不以 injection_start_ns 冒充采集时间",
        },
        "geometry": {
            "rule_source": "verification/s5_display_geometry_reference.py",
            "rounding_rule": R.ROUNDING_RULE,
            "fit": "exact（画布=源帧分辨率）",
            "crosscheck_target": "detections[].xyxy_px（由消费者按冻结参考派生）",
        },
        "display_path_compatibility": {
            "contract_fields": "PASS（逐帧记录通过冻结参考 validate_result_record）",
            "geometry_fit_exact": "PASS（clip_unit_box → original_norm_to_display_px → border_pixel_sets）",
            "frame_linkage_fields": "PASS（session_id/frame_id/result_seq/repeat_index 与五元组字段齐备）",
            "timing_dependent_paths": ("REQUIRES_MONOTONIC_PUBLISH_INSTANT_NOT_PRESENT_IN_FROZEN_PACKAGE"
                                       "（age_result_ns / age_frame_ns / stale 判定 = NOT_RUN）"),
            "note": ("既有 DisplayPipeline 的年龄/过期路径需要 result_time_ns；本包按冻结件口径置 null"
                     "（不伪造时间戳），故未用其跑年龄/stale —— 不另立替代口径；"
                     "若阶段4 补 PS 单调发布时刻，须重绑契约后重跑。"),
        },
        "limitations": [
            "只允许离线回放口径的数值一致性结论；不代表板上行为、UART 实收或实时检测。",
            "回放帧本体无候选（raw_candidate_count=0 ⇒ NO_HAND 零框）；阳性检测门禁样本不属于回放帧，"
            "仅用于 xyxy→像素换算对拍，display_eligible=false。",
            "时间字段一律不可定义（无单调发布时钟）；若阶段4 补发布时刻，需重绑后重跑。",
            "输入为非连续单帧；无真实帧周期证据。",
            "G0/G1/G3/G4/G5 均未通过；P/4-D NOT_RUN。",
        ],
        "not_run": list(NOT_RUN),
        "hardware_boundary": ("板上真实回放接入仍需硬件 OFFER/CLAIM + 八类门禁（当前记录 0/8）；"
                              "本次离线接入不构成板上真实回放通过的证据。"),
    }
    assert_replay_labels(report, where="consumer_report")
    return report


def write_artifacts(*, out_dir: pathlib.Path, package: Mapping[str, Any], package_dir: pathlib.Path,
                    freeze_record_path: pathlib.Path, contract_json: pathlib.Path,
                    integrity: Mapping[str, Any], artifacts: Mapping[str, Any]) -> dict[str, Any]:
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = consumer_report(package=package, package_dir=package_dir,
                             freeze_record_path=freeze_record_path, contract_json=contract_json,
                             integrity=integrity, artifacts=artifacts)
    frames_payload = artifacts["frames_payload"]
    (out_dir / "frames.json").write_text(json.dumps(frames_payload, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8")
    with (out_dir / "frames.jsonl").open("w", encoding="utf-8") as handle:
        for record in frames_payload["frames"]:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    with (out_dir / "five_tuples.jsonl").open("w", encoding="utf-8") as handle:
        for item in artifacts["five_tuples"]:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    gate_payload = {
        "schema_version": SCHEMA_VERSION,
        "run_kind": "gate_evidence_geometry_projection",
        "input_kind": INPUT_KIND, "consumption_mode": CONSUMPTION_MODE,
        "evidence_kind": EVIDENCE_KIND, "scope_statement": SCOPE_STATEMENT,
        "display_eligible": False,
        "attribution_note": ("阳性检测门禁样本（test_fist_000）的检测几何投影，用于 xyxy→像素换算独立对拍；"
                             "**不是**回放帧检出，不进入显示流。"),
        "records": artifacts["gate_projections"],
        "box_count": sum(len(record["detections"]) for record in artifacts["gate_projections"]),
    }
    assert_replay_labels(gate_payload, where="gate_evidence_projection")
    (out_dir / "gate_evidence_projection.json").write_text(
        json.dumps(gate_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "consumer_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    (out_dir / "freeze_integrity.json").write_text(json.dumps(integrity, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    return {"report": report, "files": ["frames.json", "frames.jsonl", "five_tuples.jsonl",
                                        "gate_evidence_projection.json", "consumer_report.json",
                                        "freeze_integrity.json"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 阶段4 冻结包消费者（离线回放；不接板卡）")
    parser.add_argument("--out", required=True, help="产物输出目录")
    parser.add_argument("--package-dir", default=str(DEFAULT_PACKAGE_DIR))
    parser.add_argument("--freeze-record", default=str(DEFAULT_FREEZE_RECORD))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--no-drift", action="store_true")
    args = parser.parse_args(argv)
    out_dir = pathlib.Path(args.out)
    package_dir = pathlib.Path(args.package_dir)
    freeze_record_path = pathlib.Path(args.freeze_record)
    contract_json = pathlib.Path(args.contract)
    console = out_dir / "console"
    console.mkdir(parents=True, exist_ok=True)
    try:
        package, integrity = load_frozen_package(package_dir=package_dir,
                                                 freeze_record_path=freeze_record_path,
                                                 contract_json=contract_json, drift=not args.no_drift)
        artifacts = build_artifacts(package=package, package_dir=package_dir, integrity=integrity)
        written = write_artifacts(out_dir=out_dir, package=package, package_dir=package_dir,
                                  freeze_record_path=freeze_record_path, contract_json=contract_json,
                                  integrity=integrity, artifacts=artifacts)
    except (FI.EnvironmentError5T03, FI.FrozenPackageRejected) as error:
        (console / "consumer_failure.txt").write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        print(f"[frozen-replay] 拒绝消费（退出码 2）：{type(error).__name__}: {error}")
        return 2
    except (ConsumerError, LabelViolation) as error:
        (console / "consumer_failure.txt").write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        print(f"[frozen-replay] 产出失败（退出码 1）：{type(error).__name__}: {error}")
        return 1
    counts = written["report"]["counts"]
    print(f"[frozen-replay] exit=0 out={out_dir} frames={counts['frames']} "
          f"detections={counts['detections_total']} gate_boxes={counts['gate_projection_boxes']} "
          f"labels={INPUT_KIND}/{CONSUMPTION_MODE}/{EVIDENCE_KIND}")
    return 0


if __name__ == "__main__":
    sys.exit(main())