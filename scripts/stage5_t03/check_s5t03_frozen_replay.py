#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 冻结回放**独立对拍检查器**（不复用消费者的换算实现与判定结论）。

对拍口径
========
1. **逐框对拍**：消费者产物里每个 `detections[].xyxy_px` 必须等于检查器**现场**从
   冻结包原始检测（按产物 `source_ref` 解析回包内路径）重新换算出的像素索引。
   换算规则来自阶段5 冻结参考 `verification/s5_display_geometry_reference.py`
   （`clip_unit_box` → `original_norm_to_display_px`，只在最后取整一次）；
   画布尺寸由检查器**从冻结包**重新解析（回放帧取 `replay_frame.width/height`，
   门禁样本取 `positive_detection_gate.input_shape_bgr`），**不采信产物的画布声明**。
2. **标签对拍**：真实回放口径标签必须成立；出现 `synthetic` 标签即 FAIL（判别力用例）。
3. **时间口径对拍**：逐帧基准必须显式声明；`capture_time_ns` 为 0 哨兵（FILE_INJECTION）时
   `end_to_end_latency_ns` 必须不可定义；`injection_start_ns` 不得被当作采集时间。
4. **契约字段对拍**：字段清单从契约 JSON 现场读取（`result_contract.result_record`），不硬编码。

本检查器只读；不写任何上游目录。退出码：0 = 全部 PASS；1 = 存在 FAIL；2 = 环境错误。
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
from typing import Any, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
for _candidate in (str(REPO_ROOT), str(pathlib.Path(__file__).resolve().parent)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_freeze_integrity as FI  # noqa: E402

SCHEMA_VERSION = "gestureforge_s5t03_frozen_replay_crosscheck_v1"
REQUIRED_LABELS = {"input_kind": "stage4_frozen_replay", "consumption_mode": "replay_only",
                   "evidence_kind": "offline_replay"}
REQUIRED_STATEMENT = "离线主机回放；不代表 PL、实物或实时检测输出"
SYNTHETIC_RE = re.compile(r"synthetic", re.IGNORECASE)
# 说明性字段：允许出现 synthetic 字样（属拒绝/历史说明，不是被采纳的标签）
EXEMPT_KEYS = {"previous_label", "forbidden_claims", "synthetic_refusal_note", "synthetic_marker_note"}
PX_AXES = ("x1", "y1", "x2", "y2")
INDEX_RE = re.compile(r"^(?P<path>[^\[\]]+)\[(?P<index>\d+)\]$")


class CheckerEnvError(RuntimeError):
    """输入缺失/不可读（退出码 2）。"""


def resolve_in_package(package: Mapping[str, Any], source_ref: str) -> Any:
    """把产物里的 `source_ref`（如 `positive_detection_gate.d9_nms.predictions[0]`）解析回冻结包。"""
    match = INDEX_RE.match(source_ref)
    if match is None:
        raise CheckerEnvError(f"source_ref 形式不支持：{source_ref!r}")
    index = int(match.group("index"))
    node: Any = package
    for part in match.group("path").split("."):
        if not isinstance(node, Mapping) or part not in node:
            raise CheckerEnvError(f"source_ref 在冻结包中不存在：{source_ref!r}（缺 {part}）")
        node = node[part]
    if not isinstance(node, list) or index >= len(node):
        raise CheckerEnvError(f"source_ref 下标越界：{source_ref!r}")
    return node[index]


def canvas_for_source(package: Mapping[str, Any], source_ref: str,
                      package_dir: pathlib.Path | None = None) -> tuple[int, int]:
    """从冻结包自身解析该检测所属源的画布（= 源帧分辨率，fit=exact）。"""
    if source_ref.startswith("replay_frame"):
        replay = package["replay_frame"]
        return int(replay["width"]), int(replay["height"])
    if source_ref.startswith("positive_detection_gate"):
        gate = package["positive_detection_gate"]
        shape = [int(v) for v in (gate.get("input_shape_bgr") or [])]
        if len(shape) < 2 and package_dir is not None:
            bridge_path = pathlib.Path(package_dir) / "replay_forward_bridge_result.json"
            if bridge_path.is_file():                      # 同包冻结文件，仍属冻结输入
                bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
                checks = bridge.get("checks") or {}
                detail = ((checks.get("positive_detection_gate_forward_d9_nms") or {}).get("detail") or {})
                shape = [int(v) for v in (detail.get("input_shape_bgr") or [])]
        if len(shape) < 2:
            raise CheckerEnvError("门禁样本缺 input_shape_bgr（包与桥接结果均无），无法确定画布")
        return shape[1], shape[0]
    raise CheckerEnvError(f"未知检测来源：{source_ref!r}")


def independent_projection(xyxy: list[float], canvas_w: int, canvas_h: int) -> dict[str, Any]:
    """检查器自身的换算路径：规则取自冻结参考，算术独立复算一次并互证。"""
    clipped = R.clip_unit_box(list(xyxy))
    if clipped["zero_area"]:
        return {"zero_area": True, "px": None, "border_pixels": 0,
                "xyxy_clipped": [float(v) for v in clipped["xyxy"]]}
    px = R.original_norm_to_display_px(clipped["xyxy"], canvas_w, canvas_h)
    inline = {"x1": math.floor(float(clipped["xyxy"][0]) * (canvas_w - 1) + 0.5),
              "y1": math.floor(float(clipped["xyxy"][1]) * (canvas_h - 1) + 0.5),
              "x2": math.floor(float(clipped["xyxy"][2]) * (canvas_w - 1) + 0.5),
              "y2": math.floor(float(clipped["xyxy"][3]) * (canvas_h - 1) + 0.5)}
    arithmetic_agrees = all(int(px[axis]) == inline[axis] for axis in PX_AXES)
    border = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"], R.DISPLAY_LINE_WIDTH_PX,
                                 canvas_w, canvas_h)
    return {"zero_area": False, "px": {axis: int(px[axis]) for axis in PX_AXES},
            "inline_px": inline, "rule_arithmetic_agrees": arithmetic_agrees,
            "border_pixels": len(border), "xyxy_clipped": [float(v) for v in clipped["xyxy"]]}


def scan_labels(node: Any, path: str = "$") -> list[str]:
    """递归扫描被采纳字段里的 synthetic 标记（独立实现，不 import 消费者判定）。"""
    hits: list[str] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            if key in EXEMPT_KEYS:
                continue
            hits.extend(scan_labels(value, f"{path}.{key}"))
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            hits.extend(scan_labels(value, f"{path}[{index}]"))
    elif isinstance(node, str) and SYNTHETIC_RE.search(node):
        hits.append(f"{path}={node[:80]!r}")
    return hits


def check_labels(payloads: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    for name, payload in payloads.items():
        if not isinstance(payload, Mapping):
            continue
        for key, expected in REQUIRED_LABELS.items():
            if payload.get(key) != expected:
                problems.append(f"{name}.{key}={payload.get(key)!r} != {expected!r}")
        if payload.get("scope_statement") != REQUIRED_STATEMENT:
            problems.append(f"{name}.scope_statement 缺失或不等于冻结口径文本")
        for hit in scan_labels(payload, path=f"$.{name}"):
            problems.append(f"{name} 出现 synthetic 标记：{hit}")
    return {"verdict": "PASS" if not problems else "FAIL", "problems": problems,
            "required": REQUIRED_LABELS, "required_statement": REQUIRED_STATEMENT}


def check_frame_records(frames: list[Mapping[str, Any]], contract: Mapping[str, Any]) -> dict[str, Any]:
    required = list(contract["result_contract"]["result_record"]["fields"])
    detection_fields = list(contract["result_contract"]["result_record"]["detection_fields"])
    problems: list[str] = []
    per_frame: list[dict[str, Any]] = []
    for index, record in enumerate(frames):
        frame_problems: list[str] = []
        for field in required:
            if field not in record:
                frame_problems.append(f"缺契约字段 {field}")
        if record.get("detection_count") != len(record.get("detections") or []):
            frame_problems.append("detection_count 与 detections 长度不一致")
        if record.get("state") == "NO_HAND" and record.get("detections"):
            frame_problems.append("NO_HAND 必须零框")
        if record.get("state") not in ("OK", "NO_HAND", "TIMEOUT", "ERROR", "DROPPED"):
            frame_problems.append(f"未知 state={record.get('state')!r}")
        for box_index, det in enumerate(record.get("detections") or []):
            for field in detection_fields:
                if field not in det:
                    frame_problems.append(f"detections[{box_index}] 缺字段 {field}")
            if det.get("xyxy_px") is not None:
                for axis in PX_AXES:
                    if not isinstance((det.get("xyxy_px") or {}).get(axis), int):
                        frame_problems.append(f"detections[{box_index}].xyxy_px.{axis} 必须是整数")
        frame_problems.extend(check_timing_basis(record, where=f"frames[{index}]"))
        per_frame.append({"frame_id": record.get("frame_id"), "state": record.get("state"),
                          "detections": len(record.get("detections") or []),
                          "verdict": "PASS" if not frame_problems else "FAIL",
                          "problems": frame_problems})
        problems.extend(f"frames[{index}]: {p}" for p in frame_problems)
    return {"verdict": "PASS" if not problems else "FAIL", "required_fields": required,
            "required_detection_fields": detection_fields, "per_frame": per_frame, "problems": problems}


def check_timing_basis(record: Mapping[str, Any], *, where: str) -> list[str]:
    """时间基准口径检查（含 FILE_INJECTION 0 哨兵与 injection_start_ns 陷阱）。"""
    problems: list[str] = []
    basis = record.get("timing_basis")
    if not isinstance(basis, Mapping):
        return [f"{where} 缺 timing_basis（时间基准必须显式声明）"]
    capture = basis.get("capture_time_ns") or {}
    e2e = basis.get("end_to_end_latency_ns") or {}
    if not capture.get("basis"):
        problems.append(f"{where} 缺 capture_time_ns 基准声明")
    if basis.get("injection_start_ns_used_as_capture_time") is not False:
        problems.append(f"{where} 未显式声明 injection_start_ns 未被当作采集时间")
    injection_start = basis.get("injection_start_ns")
    if injection_start is not None and capture.get("value") == injection_start:
        problems.append(f"{where} capture_time_ns 等于 injection_start_ns（契约禁止）")
    sentinel = capture.get("basis") == "zero_sentinel_file_injection_contract" or capture.get("value") in (0, None)
    if sentinel:
        if record.get("capture_time_ns") not in (0, None):
            problems.append(f"{where} 哨兵口径下 capture_time_ns 必须是 0/None 哨兵值")
        if record.get("end_to_end_latency_ns") is not None or e2e.get("defined") is not False:
            problems.append(f"{where} FILE_INJECTION 0 哨兵下端到端延迟必须不可定义")
    else:
        if e2e.get("defined") is True and record.get("end_to_end_latency_ns") is None:
            problems.append(f"{where} 声明端到端延迟可定义却无值")
        if record.get("end_to_end_latency_ns") is not None and not e2e.get("basis"):
            problems.append(f"{where} 端到端延迟有值但缺基准声明")
    if not basis.get("age_frame_ns_basis"):
        problems.append(f"{where} 缺 age_frame_ns 基准声明")
    if record.get("result_time_ns") is None and (basis.get("result_time_ns") or {}).get("defined") is not False:
        problems.append(f"{where} result_time_ns 为空但未声明不可定义")
    return problems


def check_five_tuples(items: list[Mapping[str, Any]]) -> dict[str, Any]:
    problems: list[str] = []
    for index, item in enumerate(items):
        for field in ("displayed_frame_id", "result_frame_id", "age_result_ns", "age_frame_ns",
                      "display_semantics"):
            if field not in item:
                problems.append(f"five_tuples[{index}] 缺 {field}")
        if item.get("display_semantics") != R.DISPLAY_SEMANTICS:
            problems.append(f"five_tuples[{index}] display_semantics != {R.DISPLAY_SEMANTICS}")
        basis = item.get("age_basis")
        if not isinstance(basis, Mapping):
            problems.append(f"five_tuples[{index}] 缺 age_basis（年龄基准必须显式声明）")
            continue
        age_frame = basis.get("age_frame_ns") or {}
        if not age_frame.get("basis"):
            problems.append(f"five_tuples[{index}] 缺 age_frame_ns 基准")
        if basis.get("injection_start_ns_used_as_capture_time") is not False:
            problems.append(f"five_tuples[{index}] 未声明 injection_start_ns 未被当作采集时间")
        if item.get("age_frame_ns") is None and age_frame.get("defined") is not False:
            problems.append(f"five_tuples[{index}] age_frame_ns 为空但未声明不可定义")
    return {"verdict": "PASS" if not problems else "FAIL", "count": len(items), "problems": problems}


def crosscheck_boxes(*, frames: list[Mapping[str, Any]], gate_records: list[Mapping[str, Any]],
                     package: Mapping[str, Any],
                     package_dir: pathlib.Path | None = None) -> dict[str, Any]:
    """逐框对拍：产物 `xyxy_px` vs 检查器从冻结包现场重算的像素索引。"""
    verdicts: list[dict[str, Any]] = []
    problems: list[str] = []
    total_boxes = total_axes = mismatches = 0
    for group, records in (("frames", frames), ("gate_evidence_projection", gate_records)):
        for record_index, record in enumerate(records):
            detections = list(record.get("detections") or [])
            if not detections:
                verdicts.append({"group": group, "record_index": record_index,
                                 "source_ref": None, "verdict": "PASS_EMPTY",
                                 "boxes": 0, "axes": 0, "mismatches": 0,
                                 "note": "该记录零框（合法 NO_HAND/零结果），无框可对拍"})
                continue
            for box_index, det in enumerate(detections):
                source_ref = str(det.get("source_ref"))
                total_boxes += 1
                box_problems: list[str] = []
                try:
                    source = resolve_in_package(package, source_ref)
                    canvas_w, canvas_h = canvas_for_source(package, source_ref, package_dir)
                except CheckerEnvError as error:
                    verdicts.append({"group": group, "record_index": record_index,
                                     "source_ref": source_ref, "source_index": box_index,
                                     "verdict": "FAIL", "problems": [str(error)]})
                    problems.append(f"{group}[{record_index}].detections[{box_index}]: {error}")
                    continue
                source_xyxy = [float(v) for v in source["xyxy"]]
                if [float(v) for v in det.get("xyxy") or []] != source_xyxy:
                    box_problems.append("产物 xyxy 与冻结包原始 xyxy 不一致（被篡改或错配）")
                recomputed = independent_projection(source_xyxy, canvas_w, canvas_h)
                if not recomputed.get("rule_arithmetic_agrees", True):
                    box_problems.append("检查器内部：参考实现与独立算术不一致（规则实现异常）")
                artifact_px = det.get("xyxy_px")
                if artifact_px is None:
                    box_problems.append("产物 xyxy_px 缺失")
                    axis_verdicts: dict[str, Any] = {}
                else:
                    axis_verdicts = {}
                    for axis in PX_AXES:
                        total_axes += 1
                        expected = recomputed["px"][axis] if recomputed["px"] else None
                        actual = artifact_px.get(axis)
                        ok = (expected is not None) and (actual == expected)
                        axis_verdicts[axis] = {"artifact": actual, "recomputed": expected,
                                               "verdict": "PASS" if ok else "FAIL"}
                        if not ok:
                            box_problems.append(f"xyxy_px.{axis}: 产物 {actual} != 重算 {expected}")
                if det.get("border_pixels") != recomputed["border_pixels"]:
                    box_problems.append(f"border_pixels: 产物 {det.get('border_pixels')} != "
                                        f"重算 {recomputed['border_pixels']}")
                verdict = "PASS" if not box_problems else "FAIL"
                if verdict == "FAIL":
                    mismatches += 1
                    problems.extend(f"{group}[{record_index}].detections[{box_index}]: {p}"
                                    for p in box_problems)
                verdicts.append({"group": group, "record_index": record_index,
                                 "source_ref": source_ref, "source_index": box_index,
                                 "class_name": det.get("class_name"),
                                 "source_xyxy": source_xyxy,
                                 "canvas": [canvas_w, canvas_h],
                                 "artifact_xyxy_px": artifact_px,
                                 "recomputed_xyxy_px": recomputed["px"],
                                 "axis_verdicts": axis_verdicts,
                                 "border_pixels": {"artifact": det.get("border_pixels"),
                                                   "recomputed": recomputed["border_pixels"]},
                                 "verdict": verdict, "problems": box_problems})
    return {"verdict": "PASS" if mismatches == 0 else "FAIL",
            "boxes_checked": total_boxes, "axes_checked": total_axes, "box_mismatches": mismatches,
            "empty_records": sum(1 for v in verdicts if v["verdict"] == "PASS_EMPTY"),
            "verdicts": verdicts, "problems": problems,
            "rule": "阶段5 冻结参考 clip_unit_box → original_norm_to_display_px（画布由冻结包重解析）"}


def check_package_consistency(package: Mapping[str, Any]) -> dict[str, Any]:
    gate_nms = (package.get("positive_detection_gate") or {}).get("d9_nms") or {}
    predictions = list(gate_nms.get("predictions") or [])
    reference = list(gate_nms.get("t29_reference_predictions") or [])
    problems: list[str] = []
    if predictions != reference:
        problems.append("positive_detection_gate 的 predictions 与 t29_reference_predictions 不一致")
    if gate_nms.get("exact_t29_detection_match") is not True:
        problems.append("冻结包 exact_t29_detection_match 不为 true")
    replay = package["replay_frame"]["d9"]
    if replay.get("raw_candidate_count_before_stable_nms") != len(replay.get("decoded_predictions") or []):
        if int(replay.get("raw_candidate_count_before_stable_nms", 0)) != 0:
            problems.append("回放帧 raw_candidate_count 与 decoded_predictions 长度不一致")
    marking = package.get("marking") or {}
    if marking.get("replay_only") is not True or marking.get("evidence_kind") != "offline_replay":
        problems.append("冻结包 marking 不是 replay_only/offline_replay")
    return {"verdict": "PASS" if not problems else "FAIL", "problems": problems,
            "gate_predictions": len(predictions),
            "replay_frame_candidates": replay.get("raw_candidate_count_before_stable_nms"),
            "marking": marking}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 冻结回放独立对拍检查器（只读）")
    parser.add_argument("--artifacts", required=True, help="消费者产物目录")
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--freeze-record", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--skip-integrity", action="store_true")
    args = parser.parse_args(argv)
    artifacts_dir = pathlib.Path(args.artifacts)
    package_dir = pathlib.Path(args.package_dir)
    contract_path = pathlib.Path(args.contract)
    try:
        if not artifacts_dir.is_dir():
            raise CheckerEnvError(f"产物目录不存在：{artifacts_dir}")
        frames_path = artifacts_dir / "frames.json"
        gate_path = artifacts_dir / "gate_evidence_projection.json"
        report_path = artifacts_dir / "consumer_report.json"
        for required in (frames_path, gate_path, report_path):
            if not required.is_file():
                raise CheckerEnvError(f"缺产物文件：{required}")
        frames_payload = json.loads(frames_path.read_text(encoding="utf-8"))
        gate_payload = json.loads(gate_path.read_text(encoding="utf-8"))
        consumer_report = json.loads(report_path.read_text(encoding="utf-8"))
        package = json.loads((package_dir / "task27_replay_result_package.json").read_text(encoding="utf-8"))
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        integrity = None
        if not args.skip_integrity:
            integrity = FI.verify_all(freeze_record_path=pathlib.Path(args.freeze_record),
                                      package_dir=package_dir, contract_json=contract_path, drift=True)
    except (CheckerEnvError, FI.EnvironmentError5T03) as error:
        print(f"[crosscheck] 环境错误（退出码 2）：{error}")
        return 2

    frames = list(frames_payload.get("frames") or [])
    gate_records = list(gate_payload.get("records") or [])
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifacts_dir": str(artifacts_dir),
        "package_dir": str(package_dir),
        "freeze_record": str(args.freeze_record),
        "contract": str(contract_path),
        "integrity": None if integrity is None else {
            "consumable": integrity["consumable"],
            "file_integrity": f"{integrity['file_integrity']['ok']}/{integrity['file_integrity']['checked']}",
            "contract_binding_all_pass": integrity["contract_binding_check"]["all_pass"],
            "upstream_binding_drift": f"{integrity['upstream_binding_drift'].get('ok')}/"
                                      f"{integrity['upstream_binding_drift'].get('checked')}",
        },
        "labels": check_labels({"frames": frames_payload, "gate_evidence_projection": gate_payload,
                                "consumer_report": consumer_report}),
        "frame_records": check_frame_records(frames, contract),
        "five_tuples": check_five_tuples(
            [json.loads(line) for line in (artifacts_dir / "five_tuples.jsonl").read_text(
                encoding="utf-8").splitlines() if line.strip()]),
        "package_consistency": check_package_consistency(package),
        "box_crosscheck": crosscheck_boxes(frames=frames, gate_records=gate_records, package=package,
                                           package_dir=package_dir),
    }
    sections = ("labels", "frame_records", "five_tuples", "package_consistency", "box_crosscheck")
    failures = [name for name in sections if result[name]["verdict"] != "PASS"]
    if integrity is not None and not integrity["consumable"]:
        failures.append("integrity")
    result["checks"] = {"sections": {name: result[name]["verdict"] for name in sections},
                        "integrated_integrity": None if integrity is None else integrity["consumable"],
                        "failures": failures,
                        "passed": not failures}
    result["verdict"] = "PASS" if not failures else "FAIL"
    result["limits"] = [
        "对拍只覆盖离线回放口径的字段/标签/几何一致性；不代表板上行为、UART 实收、实时检测。",
        "回放帧本体零框，因此逐框对拍对象是冻结包中的阳性门禁样本检测（含 t29 参考列表），"
        "该样本 display_eligible=false、不进入显示流。",
        "检查器只读；未写上游工作树、未改任何证据目录。",
    ]
    if args.out:
        target = pathlib.Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    box = result["box_crosscheck"]
    print(f"[crosscheck] labels={result['labels']['verdict']} frames={result['frame_records']['verdict']} "
          f"five_tuples={result['five_tuples']['verdict']} package={result['package_consistency']['verdict']} "
          f"boxes={box['verdict']}({box['boxes_checked']} 框/{box['axes_checked']} 轴, "
          f"mismatch={box['box_mismatches']}) verdict={result['verdict']}")
    if failures:
        for name in failures:
            for problem in result[name].get("problems", [])[:10]:
                print(f"  FAIL {name}: {problem}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())