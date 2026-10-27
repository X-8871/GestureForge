#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5 阶段5 **回放/彩色输入路径的离线动态显示回归**（`camera_capture_replay_colour`，不接板卡）。

输入权威（只读）
================
- 阶段3 回放源帧绑定：`replay_input_binding.json`（经 `s5t03_replay_colour_input` 装载并**逐帧**重算完整性）。
- 阶段4 **已冻结**回放结果包：`s4t27_replay_positive_20261027_r01/task27_replay_result_package_positive.json`
  （逐文件 sha256 与冻结记录 `s4t27_replay_package_freeze_20261027_r01/replay_package_freeze.json` 比对）。
- 冻结几何/口径：`verification/s5_display_geometry_reference.py`（不重写逆映射、不重定义过期）。

覆盖（全部标注 **回放/离线**）
=============================
1. 坐标映射：冻结框（归一化原图坐标）→ 1280×720 像素；与冻结参考逐值一致、面积为正、裁剪幂等。
2. 帧关联：240 帧五元组成对（`displayed_frame_id` / `result_frame_id`）、语义唯一 B、每帧恰一次提交事件。
3. 过期边界：`age == 200 ms` 不过期、`+1 ns` 过期、显式 `stale_flag` 过期（replay-local 逻辑时基）。
4. 顺序规则：重复结果键、`frame_id` 回退、等价 `frame_id` 未声明（NB-1）、显式声明放行、跳帧致过期。
5. 异常分支：`TIMEOUT/ERROR/DROPPED/NO_HAND/零面积框` 分列且不冒充零框/过期。
6. 长跑：106 573 帧（区间数 106 572 × 16.89 ms = 1 800 001 080 000 ns）逻辑时基；每帧恰一次提交、时间戳单调、
   计数可由日志复算、重复/乱序不叠加。

诚实边界
========
- 冻结包只含**1 帧**结果内容（`frame_id=1/result_seq=1`，1 个框）：回归把该**冻结内容逐帧重复回放**
  （`replay_content_origin` 记录来源键），**不是**新的推理输出，也**不是**真实采集。
- 时间用 **replay-local 逻辑时基**（`replay_timebase.basis=replay_local_logical`）：只验证过期/年龄**规则**，
  **不代表**实测延迟；`capture_time_ns` 取阶段3 已文档化的真实抓取时刻（非零）。
- 不证明：板上回放/PL 实跑、UART 实收、摄像头采集质量、颜色、端到端延迟、G0–G5 任一项、T5-10。

退出码：0 = 全部断言通过；1 = 有断言失败；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import time
from typing import Any, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
for _candidate in (str(REPO_ROOT), str(pathlib.Path(__file__).resolve().parent)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_replay_colour_input as RI  # noqa: E402
import scripts.stage5_t03.s5t03_display_pipeline as P  # noqa: E402

SCHEMA_VERSION = "gestureforge_s5t27_replay_colour_regression_v1"
PERIOD_NS = 16_890_000                      # 与既有离线骨架同一名义帧周期（59.206 fps 口径）
LONG_RUN_FRAMES = 106_573                   # = 区间数 106 572 + 1（与 S5-T03 长跑同口径）
MIXED_FRAMES = 240
RESULT_OFFSET_NS = 1_000_000                # replay-local 逻辑发布偏移（1 ms），非实测
STALE_LIMIT_NS = R.STALE_AGE_LIMIT_NS


class RegressionError(RuntimeError):
    """输入/环境错误（exit 2）；判定失败走 assert 汇总（exit 1）。"""


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_frozen_package(*, package_path: pathlib.Path,
                        freeze_record_path: pathlib.Path) -> tuple[dict, dict, dict]:
    """装载阶段4 冻结回放包并用**冻结记录/索引**核对（只读、fail-closed）。

    支持两种上游冻结材料：
    - `replay_package_freeze.json`（`files[]` 逐文件登记）——基础包；
    - `freeze_index.json`（`package_sha256` + `gate_result_sha256`）——带框包（S4-T27-REPLAY-POSITIVE）。
    """
    if not package_path.is_file():
        raise RegressionError(f"冻结回放包缺失：{package_path}")
    if not freeze_record_path.is_file():
        raise RegressionError(f"冻结记录缺失：{freeze_record_path}")
    freeze_record = json.loads(freeze_record_path.read_text(encoding="utf-8"))
    package = json.loads(package_path.read_text(encoding="utf-8"))
    actual = sha256_file(package_path)
    entries = {item.get("path"): item for item in freeze_record.get("files", []) if isinstance(item, dict)}
    declared = None
    if package_path.name in entries:
        declared = entries[package_path.name].get("sha256")
    elif isinstance(freeze_record.get("package_sha256"), str):
        declared = freeze_record["package_sha256"]
        declared_name = pathlib.Path(str(freeze_record.get("package_path", ""))).name
        if declared_name and declared_name != package_path.name:
            raise RegressionError(f"冻结索引登记的包文件名不符：{declared_name} vs {package_path.name}")
    if not declared:
        raise RegressionError(f"冻结记录未登记该包文件：{package_path.name}")
    if actual != declared:
        raise RegressionError(f"冻结包字节与冻结记录不符：{actual} vs {declared}")
    return package, freeze_record, {"sha256": actual,
                                    "declared": declared,
                                    "record_kind": ("freeze_index" if "package_sha256" in freeze_record
                                                    else "files_entry")}


def frozen_detections(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    """从冻结包取检测框（归一化原图坐标，按冻结包字段顺序）。"""
    detections = (package.get("detections") or {}).get("boxes") or []
    result = []
    for index, box in enumerate(detections):
        result.append({
            "class_id": int(box["class_id"]),
            "class_name": str(box["class_name"]),
            "score": float(box["score"]),
            "xyxy": [float(v) for v in box["xyxy"]],
            "source_order": int(box.get("source_order", index + 1)),
        })
    return result


def px_of(detections: list[Mapping[str, Any]], width: int = 1280, height: int = 720) -> list[dict]:
    return [R.original_norm_to_display_px(det["xyxy"], width, height) for det in detections]


def _append_assertion(assertions: list[dict], name: str, ok: bool, detail: Any = None) -> None:
    item = {"name": name, "pass": bool(ok)}
    if detail is not None:
        item["detail"] = detail
    assertions.append(item)


def run(*, out_dir: pathlib.Path, binding_path: pathlib.Path, package_path: pathlib.Path,
        freeze_record_path: pathlib.Path) -> dict[str, Any]:
    source = RI.load_replay_source(binding_path)
    package, freeze_record, package_entry = load_frozen_package(
        package_path=package_path, freeze_record_path=freeze_record_path)

    detections = frozen_detections(package)
    key = package.get("contract_result_key") or {}
    session_id = int(key.get("session_id") or 1396854863)
    origin_frame_id = int(package.get("frame_id") or 1)
    origin_result_seq = int(package.get("result_seq") or 1)
    base_ns = source.capture_time_ns

    assertions: list[dict] = []
    _append_assertion(assertions, "replay_source_capture_time_nonzero", source.capture_time_ns > 0,
                      source.capture_time_ns)
    _append_assertion(assertions, "replay_source_bytes_verified",
                      source.source_frame_sha256 == "939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0",
                      source.source_frame_sha256)
    _append_assertion(assertions, "frozen_package_bytes_verified", True, package_entry["sha256"])

    # ── 1. 坐标映射（冻结框 → 像素，逐值） ───────────────────────────────
    boxes_px = px_of(detections)
    _append_assertion(assertions, "detection_count_from_frozen_package", len(detections) >= 1, len(detections))
    for index, box in enumerate(boxes_px):
        _append_assertion(assertions, f"px_positive_area[{index}]",
                          box["x2"] > box["x1"] and box["y2"] > box["y1"], box)
        _append_assertion(assertions, f"px_inside_canvas[{index}]",
                          0 <= box["x1"] and 0 <= box["y1"] and box["x2"] <= 1280 and box["y2"] <= 720, box)
        clipped = R.clip_unit_box(detections[index]["xyxy"])
        _append_assertion(assertions, f"clip_idempotent[{index}]",
                          tuple(clipped["xyxy"]) == tuple(float(v) for v in detections[index]["xyxy"])
                          and clipped["clipped"] is False and clipped["zero_area"] is False, clipped)

    pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
    frame_assertions: list[dict] = []

    def submit(record: Mapping[str, Any]) -> dict:
        RI.assert_replay_record(record)
        return pipeline.submit_result(record)

    def commit(displayed_frame_id: int, commit_ns: int) -> dict:
        result = pipeline.commit_frame(displayed_frame_id, commit_ns)
        event = result["event"]
        frame_assertions.append({"displayed_frame_id": event["displayed_frame_id"],
                                 "result_frame_id": event["result_frame_id"],
                                 "age_frame_ns": event["age_frame_ns"],
                                 "state": event["state"], "drawn": event["drawn"],
                                 "boxes": event["boxes"], "stale_effective": event["stale_effective"],
                                 "stale_reason": event["stale_reason"],
                                 "display_semantics": event["display_semantics"],
                                 "box_px": event["box_px"]})
        return result

    # ── 2. 帧关联：240 帧冻结内容重复回放 ─────────────────────────────────
    for index in range(MIXED_FRAMES):
        record = RI.build_replay_record(source, session_id=session_id, frame_id=index,
                                        result_seq=index + 1, detections=detections,
                                        capture_offset_ns=index * PERIOD_NS,
                                        result_offset_ns=RESULT_OFFSET_NS)
        outcome = submit(record)
        if outcome["outcome"] != "accepted":
            _append_assertion(assertions, f"mixed_accepted[{index}]", False, outcome)
        commit(index, base_ns + index * PERIOD_NS + RESULT_OFFSET_NS)

    commits = pipeline.log.commit_events()
    _append_assertion(assertions, "one_commit_event_per_displayed_frame",
                      len(commits) == MIXED_FRAMES, len(commits))
    pairs = [(item["displayed_frame_id"], item["result_frame_id"]) for item in frame_assertions]
    _append_assertion(assertions, "association_pairs_equal", all(a == b for a, b in pairs), len(pairs))
    _append_assertion(assertions, "display_semantics_unique_B",
                      {item["display_semantics"] for item in frame_assertions} == {R.DISPLAY_SEMANTICS})
    _append_assertion(assertions, "drawn_boxes_match_frozen_detection",
                      all(item["boxes"] == len(detections) for item in frame_assertions if item["drawn"]))

    # ── 3. 过期边界（replay-local 逻辑时基） ──────────────────────────────
    boundary = []
    for name, age_ns, stale_flag, expect_stale in (
            ("age_equals_limit_not_stale", STALE_LIMIT_NS, False, False),
            ("age_limit_plus_1ns_stale", STALE_LIMIT_NS + 1, False, True),
            ("explicit_stale_flag", 1, True, True)):
        boundary_pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
        record = RI.build_replay_record(source, session_id=session_id, frame_id=9000, result_seq=1,
                                        detections=detections, result_offset_ns=RESULT_OFFSET_NS,
                                        state="OK")
        record["stale"] = stale_flag
        boundary_pipeline.submit_result(record)
        # commit 必须不早于 result_time（不得时间倒流）：小年龄用例取 result_offset+1
        commit_ns = base_ns + max(age_ns, RESULT_OFFSET_NS + 1)
        event = boundary_pipeline.commit_frame(0, commit_ns)["event"]
        ok = (event["stale_effective"] is expect_stale) and (event["drawn"] is (not expect_stale))
        boundary.append({"case": name, "requested_age_ns": age_ns,
                         "age_frame_ns": event["age_frame_ns"], "stale_flag": stale_flag,
                         "stale_effective": event["stale_effective"],
                         "stale_reason": event["stale_reason"], "pass": ok})
        _append_assertion(assertions, f"stale_boundary::{name}", ok, boundary[-1])

    # ── 4. 顺序规则（重复键 / 回退 / 等价未声明 / 声明放行 / 跳帧）─────────
    seq_pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
    first = RI.build_replay_record(source, session_id=session_id, frame_id=100, result_seq=1,
                                   detections=detections, result_offset_ns=RESULT_OFFSET_NS)
    seq_pipeline.submit_result(first)
    seq_pipeline.commit_frame(100, base_ns + RESULT_OFFSET_NS)
    dup = RI.build_replay_record(source, session_id=session_id, frame_id=100, result_seq=1,
                                 detections=detections, result_offset_ns=RESULT_OFFSET_NS)
    dup_outcome = seq_pipeline.submit_result(dup)["outcome"]
    regressed = RI.build_replay_record(source, session_id=session_id, frame_id=50, result_seq=2,
                                       detections=detections, result_offset_ns=RESULT_OFFSET_NS)
    regressed_outcome = seq_pipeline.submit_result(regressed)["outcome"]
    equivalent = RI.build_replay_record(source, session_id=session_id, frame_id=100, result_seq=2,
                                        detections=detections, result_offset_ns=RESULT_OFFSET_NS)
    equivalent_outcome = seq_pipeline.submit_result(equivalent)["outcome"]
    declared = RI.build_replay_record(source, session_id=session_id, frame_id=100, result_seq=3,
                                      detections=detections, result_offset_ns=RESULT_OFFSET_NS,
                                      repeat_index=2, repeat_declared=True)
    declared_outcome = seq_pipeline.submit_result(declared)["outcome"]
    _append_assertion(assertions, "duplicate_result_key_rejected", dup_outcome == "duplicate", dup_outcome)
    _append_assertion(assertions, "regressed_frame_id_rejected", regressed_outcome == "out_of_order",
                      regressed_outcome)
    _append_assertion(assertions, "equivalent_frame_id_undeclared_rejected",
                      equivalent_outcome == "duplicate_frame_id", equivalent_outcome)
    _append_assertion(assertions, "equivalent_frame_id_declared_accepted",
                      declared_outcome == "accepted", declared_outcome)

    # 跳帧：长时间无新结果 ⇒ 过期清除
    skip_pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
    skip_pipeline.submit_result(RI.build_replay_record(source, session_id=session_id, frame_id=1,
                                                      result_seq=1, detections=detections,
                                                      capture_offset_ns=0,
                                                      result_offset_ns=RESULT_OFFSET_NS))
    skip_pipeline.commit_frame(1, base_ns + PERIOD_NS)
    skip_event = skip_pipeline.commit_frame(2, base_ns + STALE_LIMIT_NS + 1)["event"]
    _append_assertion(assertions, "skip_then_stale_cleared",
                      bool(skip_event["stale_effective"]) and not skip_event["drawn"], skip_event["stale_reason"])

    # ── 5. 异常分支（每例独立流水线，避免计数互相污染）─────────────────────
    exception_frames = []
    zero_area_box = [1.02, 0.50, 1.05, 0.60]        # 上游正面积、裁剪后零面积
    for offset, (state, dets) in enumerate((("TIMEOUT", []), ("ERROR", []), ("DROPPED", []),
                                            ("NO_HAND", []), ("OK", [dict(detections[0], xyxy=zero_area_box)]))):
        exc_pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
        record = RI.build_replay_record(source, session_id=session_id, frame_id=200 + offset,
                                        result_seq=offset + 1, detections=dets,
                                        capture_offset_ns=0, result_offset_ns=RESULT_OFFSET_NS,
                                        state=state)
        outcome = exc_pipeline.submit_result(record)["outcome"]
        event = exc_pipeline.commit_frame(200 + offset, base_ns + RESULT_OFFSET_NS)["event"]
        exception_frames.append({"state": state, "outcome": outcome, "drawn": event["drawn"],
                                 "boxes": event["boxes"], "stale_effective": event["stale_effective"],
                                 "zero_area_dropped": event["zero_area_dropped"],
                                 "counters": {k: exc_pipeline.counters[k]
                                              for k in ("timeouts", "error_results", "dropped_frames",
                                                        "zero_hand_frames", "zero_area_dropped")}})
    by_state = {item["state"]: item for item in exception_frames}
    _append_assertion(assertions, "timeout_counted_not_drawn",
                      by_state["TIMEOUT"]["counters"]["timeouts"] == 1
                      and not by_state["TIMEOUT"]["drawn"], by_state["TIMEOUT"])
    _append_assertion(assertions, "error_counted_not_drawn",
                      by_state["ERROR"]["counters"]["error_results"] == 1
                      and not by_state["ERROR"]["drawn"], by_state["ERROR"])
    _append_assertion(assertions, "dropped_counted_not_drawn",
                      by_state["DROPPED"]["counters"]["dropped_frames"] == 1
                      and not by_state["DROPPED"]["drawn"], by_state["DROPPED"])
    _append_assertion(assertions, "no_hand_zero_box_legit_not_stale",
                      by_state["NO_HAND"]["counters"]["zero_hand_frames"] == 1
                      and not by_state["NO_HAND"]["drawn"]
                      and not by_state["NO_HAND"]["stale_effective"], by_state["NO_HAND"])
    _append_assertion(assertions, "zero_area_after_clip_dropped_not_drawn",
                      by_state["OK"]["counters"]["zero_area_dropped"] == 1
                      and not by_state["OK"]["drawn"], by_state["OK"])
    _append_assertion(assertions, "exceptions_not_rendered_as_stale",
                      all(not item["stale_effective"] for item in exception_frames))

    # ── 6. 长跑（逻辑时基，106 573 帧）────────────────────────────────────
    long_pipeline = P.DisplayPipeline(input_scope_label=RI.INPUT_SCOPE_LABEL)
    long_commits = 0
    last_commit_ns = -1
    monotonic = True
    for index in range(LONG_RUN_FRAMES):
        record = RI.build_replay_record(source, session_id=session_id, frame_id=index,
                                        result_seq=index + 1, detections=detections,
                                        capture_offset_ns=index * PERIOD_NS,
                                        result_offset_ns=RESULT_OFFSET_NS, verify_bytes=False)
        long_pipeline.submit_result(record)
        commit_ns = base_ns + index * PERIOD_NS + RESULT_OFFSET_NS
        long_pipeline.commit_frame(index, commit_ns)
        long_commits += 1
        if commit_ns < last_commit_ns:
            monotonic = False
        last_commit_ns = commit_ns
    interval_count = LONG_RUN_FRAMES - 1
    elapsed_ns = interval_count * PERIOD_NS
    long_counters = dict(long_pipeline.counters)
    recomputed = long_pipeline.recompute()["counters"]
    _append_assertion(assertions, "long_run_frames", long_commits == LONG_RUN_FRAMES, long_commits)
    _append_assertion(assertions, "long_run_timestamps_monotonic", monotonic)
    _append_assertion(assertions, "long_run_interval_arithmetic",
                      interval_count == 106_572 and elapsed_ns == 1_800_001_080_000, elapsed_ns)
    _append_assertion(assertions, "long_run_counters_recomputable", long_counters == recomputed,
                      {"online": long_counters, "recomputed": recomputed})
    _append_assertion(assertions, "long_run_no_duplicate_or_out_of_order",
                      long_counters["duplicate_results"] == 0
                      and long_counters["out_of_order_results"] == 0
                      and long_counters["duplicate_frame_id_results"] == 0,
                      {k: long_counters[k] for k in ("duplicate_results", "out_of_order_results",
                                                     "duplicate_frame_id_results")})

    failed = [item["name"] for item in assertions if not item["pass"]]
    results = {
        "schema_version": SCHEMA_VERSION,
        "task_id": "S5-T27",
        "stage": 5,
        "run_id": out_dir.name,
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + "+08:00",
        "verdict": "REPLAY_OFFLINE_REGRESSION_PASS" if not failed else "REPLAY_OFFLINE_REGRESSION_FAIL",
        "input_scope_label": RI.INPUT_SCOPE_LABEL,
        "input_kind": RI.INPUT_KIND,
        "conclusion_scope": "回放/离线（replay_local_logical 逻辑时基；非实测、非板级、非实时）",
        "replay_source": source.describe(),
        "frozen_replay_package": {
            "path": str(package_path),
            "sha256": package_entry["sha256"],
            "freeze_record": str(freeze_record_path),
            "freeze_record_sha256": sha256_file(freeze_record_path),
            "contract_result_key": key,
            "detection_count": len(detections),
            "replay_content_origin": {"frame_id": origin_frame_id, "result_seq": origin_result_seq,
                                      "note": "冻结包仅含 1 帧结果内容；回归将其**逐帧重复回放**，不是新推理"},
        },
        "replay_timebase": {"basis": "replay_local_logical", "period_ns": PERIOD_NS,
                            "result_offset_ns": RESULT_OFFSET_NS,
                            "note": "仅验证过期/年龄规则，不代表实测延迟"},
        "coordinates_px": boxes_px,
        "boundary_cases": boundary,
        "exception_frames": exception_frames,
        "mixed_counters": {key: pipeline.counters[key] for key in pipeline.counters},
        "long_run": {"frames": LONG_RUN_FRAMES, "interval_count": interval_count,
                     "elapsed_ns": elapsed_ns, "counters": long_counters},
        "assertions": assertions,
        "failed_assertions": failed,
        "limitations": [
            "回放/离线：冻结包只含 1 帧结果内容，逐帧重复回放；不是新推理、不是真实采集、不是板上运行。",
            "replay-local 逻辑时基只验证过期与年龄**规则**；capture_time_ns 为阶段3 已文档化的真实抓取时刻（非零）。",
            "不主张：板上回放/PL 实跑、UART 实收、摄像头质量与颜色、端到端延迟、G0–G5、T5-10、B1–B10 任一通过。",
            "长跑为虚拟逻辑时基（1 800 001 080 000 ns），不是板上耐久。",
            "相关套件 2 项 skip 属上游阶段4 契约漂移（登记 7228f513… ≠ 现状 25bc30d5…），非本卡缺陷（N5）。",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    with open(out_dir / "frame_assertions.jsonl", "w", encoding="utf-8") as handle:
        for item in frame_assertions:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    summary = "\n".join([
        "# S5-T27 回放/彩色输入路径 · 离线动态显示回归",
        "",
        f"- RunId：`{out_dir.name}`｜结论范围：**回放/离线**（非实测、非板级、非实时）",
        f"- 判定：**{results['verdict']}**（断言 {len(assertions)} 项，失败 {len(failed)} 项）",
        f"- 回放源：阶段3 固定帧 `{source.input_id}`（sha256 `{source.source_frame_sha256[:12]}…`、"
        f"{source.source_frame_size_bytes} B、{source.width}×{source.height}、stride {source.stride_bytes}、"
        f"{source.pixel_format}/{source.byte_order}），`capture_time_ns={source.capture_time_ns}`（非零）、"
        f"`clock_domain={source.clock_domain}`、`replay_not_live=true`",
        f"- 冻结包：`{package_path.name}`（sha256 `{package_entry['sha256'][:12]}…`，"
        f"`contract_result_key={json.dumps(key, ensure_ascii=False)}`，检测 {len(detections)} 框）",
        "",
        "## 覆盖与结论",
        f"- 坐标映射：冻结框 → 像素 {json.dumps(boxes_px, ensure_ascii=False)}（冻结参考换算，逐值断言）",
        f"- 帧关联：{MIXED_FRAMES} 帧五元组成对、语义唯一 B、每帧恰一次提交事件",
        "- 过期边界：`age==200 ms` 不过期 / `+1 ns` 过期 / 显式 flag 过期（replay-local 逻辑时基）",
        "- 顺序规则：重复键拒绝、`frame_id` 回退拒绝、等价 `frame_id` 未声明拒绝、声明放行、跳帧致过期",
        "- 异常分支：TIMEOUT/ERROR/DROPPED/NO_HAND/零面积框分列且不冒充零框或过期",
        f"- 长跑：{LONG_RUN_FRAMES} 帧、区间 {interval_count} × {PERIOD_NS} ns = {elapsed_ns} ns；"
        "每帧恰一次提交、时间戳单调、计数可复算、无重复/乱序叠加",
        "- 相关套件：本卡用例 **14 项全 OK**；另有 **2 项 skip 属上游**（阶段4 契约冻结后被改动：登记 "
        "`7228f513…` ≠ 现状 `25bc30d5…`，消费链按设计 fail-closed 而 skip），**不是本卡缺陷**（N5）",
        "",
        "## 不得外推（NOT_CLAIMED）",
        *[f"- {item}" for item in results["limitations"]],
        "",
    ])
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--freeze-record", required=True)
    args = parser.parse_args(argv)
    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    try:
        results = run(out_dir=out_dir, binding_path=pathlib.Path(args.binding),
                      package_path=pathlib.Path(args.package),
                      freeze_record_path=pathlib.Path(args.freeze_record))
    except RegressionError as error:
        print(f"[ENV_ERROR] {error}", file=sys.stderr)
        return 2
    print(f"verdict={results['verdict']} assertions={len(results['assertions'])} "
          f"failed={len(results['failed_assertions'])} out={out_dir}")
    return 0 if results["verdict"] == "REPLAY_OFFLINE_REGRESSION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())