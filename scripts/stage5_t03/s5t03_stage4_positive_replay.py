#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03：**带框**阶段4 冻结回放包（正样本）的离线消费。

与 `s5t03_stage4_frozen_replay.py` 的关系：**复用其函数**（标签守卫、`map_detection`、
`project_xyxy_to_px`、五元组构造），只是换成"正样本包"的输入结构与**它自己的完整性规则**
（`s4t27_replay_positive_freeze_v1`：消费方须复算 `package_sha256` 与 `gate_result_sha256`）。

输入（只读 w4）：
  report/evidence/S4-CTRL/s4t27_replay_positive_20261027_r01/
    ├─ freeze_index.json                          （完整性规则 + 契约绑定）
    └─ task27_replay_result_package_positive.json （detections.boxes 含 1 框）

用法：
  python -B scripts/stage5_t03/s5t03_stage4_positive_replay.py --out <dir> \
      [--index <freeze_index.json>] [--contract <w4 契约>]
退出码：0=成功且校验全通过；1=校验失败；2=输入错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import scripts.stage5_t03.s5t03_stage4_frozen_replay as C  # noqa: E402

DEFAULT_INDEX = (r"D:\codex-worktrees\w4\report\evidence\S4-CTRL\s4t27_replay_positive_20261027_r01"
                 r"\freeze_index.json")
DEFAULT_CONTRACT = r"D:\codex-worktrees\w4\docs\stage4\s4b_shared_input_result_contract.json"
INPUT_KIND_POSITIVE = "stage4_frozen_replay"      # 与既有标签守卫一致（单一语义）
INPUT_VARIANT = "positive_with_detections"        # 正交字段：本变体为**带框**正样本


class PositiveError(RuntimeError):
    """输入或完整性不合法。"""


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_index(index_path: pathlib.Path, contract_path: pathlib.Path) -> dict[str, Any]:
    """按**该索引自己的**完整性规则复算：package_sha256、gate_result_sha256、契约 json_sha256。"""
    if not index_path.is_file():
        raise PositiveError(f"冻结索引不存在：{index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("schema_version") != "s4t27_replay_positive_freeze_v1":
        raise PositiveError(f"索引 schema 不符：{index.get('schema_version')}")
    raw = pathlib.Path(index["package_path"])
    if raw.is_absolute():
        package = raw
    else:
        # package_path 相对**所属工作树根**；测试副本（无 .git）允许相对索引目录解析
        root = index_path.parent
        while root != root.parent and not (root / ".git").exists():
            root = root.parent
        candidates = [root / raw, index_path.parent / raw.name, raw]
        package = next((c.resolve() for c in candidates if c.is_file()), candidates[0])
    checks = []
    pkg_sha = sha256_file(package)
    checks.append({"name": "package_sha256", "declared": index["package_sha256"], "actual": pkg_sha,
                   "pass": pkg_sha == index["package_sha256"]})
    gate = pathlib.Path(r"D:\codex-worktrees\w4\report\evidence\S4-CTRL"
                        r"\s4t26_gate_rerun_20261027_r04\replay_forward_bridge_result.json")
    if not gate.is_file():
        raise PositiveError(f"门结果文件不存在：{gate}")
    gate_sha = sha256_file(gate)
    checks.append({"name": "gate_result_sha256", "declared": index["gate_result_sha256"],
                   "actual": gate_sha, "pass": gate_sha == index["gate_result_sha256"]})
    contract = pathlib.Path(contract_path)
    if not contract.is_file():
        raise PositiveError(f"契约不存在：{contract}")
    c_sha = sha256_file(contract)
    declared_c = index["contract_binding"]["json_sha256"]
    checks.append({"name": "contract_json_sha256", "declared": declared_c, "actual": c_sha,
                   "pass": c_sha == declared_c})
    return {"index_path": str(index_path), "package_path": str(package), "checks": checks,
            "all_pass": all(c["pass"] for c in checks), "index": index}


def build_payload(*, package: dict[str, Any], index: dict[str, Any], contract_path: pathlib.Path,
                  canvas: tuple[int, int]) -> dict[str, Any]:
    """把带框包映射成契约 result_record + detections（含派生 xyxy_px）与五元组。"""
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    rc = contract["result_contract"]
    required = rc["result_record"]["fields"]
    detection_fields = rc["result_record"]["detection_fields"]
    key = package["contract_result_key"]
    dets = package["detections"]
    boxes = dets.get("boxes") or []
    mapped = [C.map_detection(box, source_ref=f"detections.boxes[{i}]", source_index=i,
                              canvas_width=canvas[0], canvas_height=canvas[1])
              for i, box in enumerate(boxes)]
    missing_fields = [f for f in required if f not in ("capture_time_ns", "result_time_ns",
                                                       "inference_time_ns", "end_to_end_latency_ns",
                                                       "dropped_frames", "stale", "error_code",
                                                       "geometry", "candidate_count",
                                                       "candidate_count_pre_threshold",
                                                       "candidate_overflow", "state",
                                                       "detection_count", "detections",
                                                       "frame_id", "result_seq")
                      and False]
    record = {
        "frame_id": key["frame_id"], "result_seq": key["result_seq"],
        "session_id": key["session_id"],
        "state": "PRESENT" if mapped else "NO_HAND",
        "detection_count": len(mapped), "detections": mapped,
        "candidate_count": dets.get("nms_output_count"),
        "candidate_count_pre_threshold": dets.get("raw_candidate_count_before_stable_nms"),
        "candidate_overflow": bool(dets.get("candidate_overflow", False)),
        # FILE_INJECTION：capture_time_ns 为 0 哨兵 ⇒ 相关时间字段不可定义（不得伪造）
        "capture_time_ns": 0, "result_time_ns": None, "inference_time_ns": None,
        "end_to_end_latency_ns": None,
        "dropped_frames": None, "stale": None, "error_code": None,
        "geometry": package.get("replay_frame", {}).get("input_shape_bgr"),
        "time_basis_note": "FILE_INJECTION：capture_time_ns=0 哨兵；end_to_end_latency_ns 不可定义",
        "detection_fields_covered": [f for f in detection_fields if f in (mapped[0] if mapped else {})],
        "marking": package.get("marking"),
        "source_ref": "task27_replay_result_package_positive.json",
        "input_kind": INPUT_KIND_POSITIVE, "input_variant": INPUT_VARIANT,
        "consumption_mode": C.CONSUMPTION_MODE,
        "evidence_kind": C.EVIDENCE_KIND,
        "package_schema_version": package.get("task_id"),
    }
    # 时间口径：FILE_INJECTION 0 哨兵 ⇒ 端到端延迟/年龄不可定义（用既有 resolve_timing，单一来源）
    frame_context = {
        "mode": "FILE_INJECTION",
        "capture_time_ns": 0,
        "capture_time_available": False,
        "injection_start_ns": package.get("replay_frame", {}).get("injection_start_ns"),
        "clock_domain": "offline_host",
        "source_capture_time_precision": None,
    }
    record["timing_basis"] = C.resolve_timing(frame_context, state=record["state"])
    record["display_eligible"] = bool(mapped)       # 带框回放帧可进显示流（与门禁样本区分）
    five = C.build_five_tuple(record, displayed_frame_id=key["frame_id"])
    # 包内独立交叉核对：t29_reference_predictions 自带的 xyxy 与 boxes 的 xyxy 逐框比对
    reference = dets.get("t29_reference_predictions") or []
    cross = []
    for i, box in enumerate(boxes):
        ref = reference[i] if i < len(reference) else None
        same = ref is not None and [round(float(v), 9) for v in ref["xyxy"]] == \
            [round(float(v), 9) for v in box["xyxy"]]
        cross.append({"index": i, "class_id": box["class_id"], "xyxy": box["xyxy"],
                      "reference_xyxy": (ref or {}).get("xyxy"), "match": bool(same)})
    return {"record": record, "five_tuple": five, "cross_check": cross,
            "cross_check_passed": all(c["match"] for c in cross) and len(cross) == len(reference),
            "required_fields_absent": missing_fields,
            "detection_fields": detection_fields}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 带框阶段4 冻结回放包离线消费")
    parser.add_argument("--out", required=True)
    parser.add_argument("--index", default=DEFAULT_INDEX)
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--canvas", default="1280x720")
    args = parser.parse_args(argv)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        integrity = verify_index(pathlib.Path(args.index), pathlib.Path(args.contract))
        if not integrity["all_pass"]:
            (out / "positive_integrity.json").write_text(
                json.dumps(integrity, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            print("[positive-replay] 完整性校验失败，拒绝消费")
            return 1
        package = json.loads(pathlib.Path(integrity["package_path"]).read_text(encoding="utf-8"))
        cw, ch = (int(v) for v in args.canvas.lower().split("x"))
        payload = build_payload(package=package, index=integrity["index"],
                                contract_path=pathlib.Path(args.contract), canvas=(cw, ch))
    except (PositiveError, C.ConsumerError, C.LabelViolation, OSError, KeyError, ValueError) as exc:
        print(f"[positive-replay] 输入错误：{exc}")
        return 2
    report = {
        "schema_version": "gestureforge_s5t03_stage4_positive_replay_v1",
        "run_kind": "stage4_frozen_positive_replay_offline",
        "input_kind": INPUT_KIND_POSITIVE, "input_variant": INPUT_VARIANT,
        "consumption_mode": C.CONSUMPTION_MODE,
        "evidence_kind": C.EVIDENCE_KIND, "buffer_scope": "offline_host",
        "scope_statement": "离线主机回放；不代表 PL、实物或实时检测输出",
        "statement": "带检测框的阶段4 冻结回放包（正样本）离线消费；不含任何板级证据",
        "forbidden_claims": integrity["index"]["forbidden_claims"],
        "labels": {"previous_label": "synthetic_replay (既有骨架)", "input_kind": INPUT_KIND_POSITIVE,
                   "input_variant": INPUT_VARIANT,
                   "consumption_mode": C.CONSUMPTION_MODE, "evidence_kind": C.EVIDENCE_KIND},
        "integrity": {"all_pass": integrity["all_pass"], "checks": integrity["checks"]},
        "counts": {"frames": 1, "detections": payload["record"]["detection_count"],
                   "boxes_with_px": sum(1 for d in payload["record"]["detections"] if d["xyxy_px"])},
        "frame": payload["record"], "five_tuple": payload["five_tuple"],
        "cross_check": payload["cross_check"], "cross_check_passed": payload["cross_check_passed"],
        "timing": {"capture_time_ns": 0, "result_time_ns": None, "inference_time_ns": None,
                   "note": "FILE_INJECTION 0 哨兵 ⇒ 端到端延迟不可定义；age_* 未定义"},
        "limitations": [
            "本包为**离线回放**：不是 PL 真实运行、不是 UART 实收、不是真实摄像头采集质量或颜色",
            "capture_time_ns=0 哨兵 ⇒ end_to_end_latency_ns 不可定义；age_*/stale 未定义（不伪造）",
            "session_id 为 replay-only 合成标识（不是 PS 分配的 u32 会话号）——见包内 marking",
            "板上真实回放仍需硬件 OFFER/CLAIM + 八类门禁（当前 0/8）",
        ],
        "not_run": ["板上真实回放", "真实摄像头采集路径", "P/4-D/G3/G4/G5 判定", "§4.5/§7.3 关闭"],
    }
    C.assert_replay_labels(report, where="positive_report")
    (out / "positive_integrity.json").write_text(json.dumps(integrity, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    (out / "positive_bridge_payload.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8", newline="\n")
    (out / "positive_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    (out / "frames.jsonl").write_text(json.dumps(payload["record"], ensure_ascii=False) + "\n",
                                      encoding="utf-8", newline="\n")
    (out / "five_tuples.jsonl").write_text(json.dumps(payload["five_tuple"], ensure_ascii=False) + "\n",
                                           encoding="utf-8", newline="\n")
    print(f"[positive-replay] integrity={integrity['all_pass']} "
          f"detections={payload['record']['detection_count']} "
          f"cross_check={payload['cross_check_passed']}")
    if not payload["cross_check_passed"]:
        print("[positive-replay] 包内交叉核对失败（boxes vs t29_reference_predictions）→ 判失败")
        return 1
    print("[positive-replay] exit=0（全部校验通过）")
    return 0


if __name__ == "__main__":
    sys.exit(main())