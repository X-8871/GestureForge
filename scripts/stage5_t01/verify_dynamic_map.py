#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T02 对拍校验器：**C 侧输出** vs **冻结参考重算**（S5A-G0-v2 + 渲染层 label_anchor/safe_area_px）。

判据（任务卡 §5）
================
1. 用例：板上（此轮＝C 在宿主执行）每框像素矩形与参考**逐像素一致**；若某框 ≤1 px 偏差则记为
   `within_1px` 并附说明（任务卡允许），否则 `pixel_mismatch`；
2. 三个过期边界（`age==limit` 不过期 / `limit+1` 过期且计数 +1 / 显式 stale_flag）逐例核对；
3. ≥100 帧五元组可按 `frame_id` 索引、语义唯一 `B_latest_result_overlay`、`displayed != result` 如实记录；
4. 故障计数（warm/drop/timeout/dup/ooo/stale/zero_area）逐项与调度模型一致；
5. HUD 13 字段逐项核对，`CAPTURE_FPS`/`INFERENCE_FPS` 必须为 `NA`（不得用 0 伪装）。

输出：机器可读 JSON 报告 + 退出码（0 = 全通过；1 = 存在违约；2 = 输入/环境错误）。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402

SCHEMA = "gestureforge_s5t02_dynamic_map_verification_v1"
HUD_REQUIRED_NA = ("CAPTURE_FPS", "INFERENCE_FPS")
HUD_FIELD_COUNT = 13


class InputError(Exception):
    pass


def parse_tsv(path: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """解析与 C 侧同语义的 TSV：F/B/D/E 行。"""
    frames: list[dict[str, Any]] = []
    counters = {"dropped_frames": 0}
    current: dict[str, Any] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split()
        kind = parts[0]
        if kind == "F":
            if current is not None and not current.get("closed"):
                frames.append(current)
            current = {
                "frame_index": int(parts[1]), "displayed_frame_id": int(parts[2]),
                "result_frame_id": int(parts[3]), "result_seq": int(parts[4]),
                "capture_time_ns": int(parts[5]), "result_time_ns": int(parts[6]),
                "overlay_commit_ns": int(parts[7]), "stale_flag": int(parts[8]),
                "warmup": int(parts[9]), "state": parts[10], "boxes": [], "closed": False,
            }
        elif kind == "B":
            if current is None:
                raise InputError("B 行出现在 F 行之前")
            current["boxes"].append({
                "class_id": int(parts[1]), "score": float(parts[2]),
                "xyxy": [float(parts[3]), float(parts[4]), float(parts[5]), float(parts[6])],
                "label_w": int(parts[7]), "label_h": int(parts[8]),
            })
        elif kind == "D":
            counters["dropped_frames"] += int(parts[1])
        elif kind == "E":
            if current is not None:
                current["closed"] = True
                frames.append(current)
                current = None
        else:
            raise InputError(f"未知行类型：{raw[:40]}")
    if current is not None:
        frames.append(current)
    return frames, counters


def expect_frame(frame: dict[str, Any], canvas: tuple[int, int],
                 counters: dict[str, int]) -> dict[str, Any]:
    """用冻结参考重算该帧的期望结果，并推进期望计数（与 C 侧同一顺序）。"""
    width, height = canvas
    expected: dict[str, Any] = {
        "frame_index": frame["frame_index"], "boxes": [], "boxes_drawn": 0, "zero_area_dropped": 0,
        "state": frame["state"], "warmup": frame["warmup"], "stale_flag": frame["stale_flag"],
    }
    counters["frames_committed"] += 1
    ages = R.compute_ages(frame["capture_time_ns"], frame["result_time_ns"], frame["overlay_commit_ns"])
    expected["age_result_ns"] = ages["age_result_ns"]
    expected["age_frame_ns"] = ages["age_frame_ns"]
    expected["display_semantics"] = ages["display_semantics"]
    stale = R.effective_stale(bool(frame["stale_flag"]), ages["age_frame_ns"])
    expected["stale_effective"] = stale["stale_effective"]
    expected["stale_reason"] = stale["reason"]

    if frame["state"] == "TIMEOUT":
        counters["timeouts"] += 1
        return expected
    if frame["state"] == "ERROR":
        counters["error_results"] += 1
        return expected
    if frame["state"] == "DUPLICATE":
        counters["duplicate_results"] += 1
        return expected
    if frame["state"] == "OUT_OF_ORDER":
        counters["out_of_order_results"] += 1
        return expected
    if frame["warmup"]:
        counters["warmup_frames"] += 1
        return expected
    if stale["stale_effective"]:
        counters["stale_cleared"] += 1
        return expected

    safe = RD.safe_area_px(height)
    for box in frame["boxes"]:
        clipped = R.clip_unit_box(box["xyxy"])
        if clipped["zero_area"]:
            counters["zero_area_dropped"] += 1
            expected["zero_area_dropped"] += 1
            continue
        px = R.original_norm_to_display_px(clipped["xyxy"], width, height)
        anchor_x, anchor_y, placement = RD.label_anchor(
            px, box["label_w"], box["label_h"], canvas_width=width, canvas_height=height, safe=safe)
        border = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"],
                                     R.DISPLAY_LINE_WIDTH_PX, width, height)
        expected["boxes"].append({
            "class_id": box["class_id"], "x1": px["x1"], "y1": px["y1"], "x2": px["x2"], "y2": px["y2"],
            "border_pixels": len(border), "label_x": anchor_x, "label_y": anchor_y,
            "label_placement": placement,
        })
        counters["boxes_drawn"] += 1
    expected["boxes_drawn"] = len(expected["boxes"])
    return expected


def load_c_output(path: pathlib.Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        record = json.loads(raw)
        if "summary" in record:
            summary = record["summary"]
        else:
            rows.append(record)
    return rows, summary


def compare(cases_path: pathlib.Path, stream_path: pathlib.Path, jsonl_path: pathlib.Path,
            canvas: tuple[int, int]) -> dict[str, Any]:
    frames, tsv_counters = parse_tsv(cases_path)
    stream_frames, stream_counters = parse_tsv(stream_path)
    all_frames = frames + stream_frames
    rows, summary = load_c_output(jsonl_path)
    if len(rows) != len(all_frames):
        raise InputError(f"C 输出帧数 {len(rows)} != 输入帧数 {len(all_frames)}")

    counters = {"frames_committed": 0, "warmup_frames": 0,
                "dropped_frames": tsv_counters["dropped_frames"] + stream_counters["dropped_frames"],
                "timeouts": 0, "error_results": 0, "duplicate_results": 0, "out_of_order_results": 0,
                "stale_cleared": 0, "zero_area_dropped": 0, "boxes_drawn": 0}
    failures: list[str] = []
    case_verdicts: list[dict[str, Any]] = []
    mismatch_counts: dict[str, int] = {}
    displayed_ne_result_recorded = 0
    seen_result_ids: set[int] = set()
    semantics = set()

    for position, (frame, row) in enumerate(zip(all_frames, rows)):
        is_stream = position >= len(frames)
        expected = expect_frame(frame, canvas, counters)
        semantics.add(row.get("display_semantics"))
        if frame["displayed_frame_id"] != frame["result_frame_id"]:
            displayed_ne_result_recorded += 1
            if row.get("displayed_frame_id") != frame["displayed_frame_id"] or \
                    row.get("result_frame_id") != frame["result_frame_id"]:
                failures.append(f"frame[{frame['frame_index']}].displayed/result 记录不符")
        key = row.get("result_frame_id")
        # 唯一性只在**长流**内检查（用例流与长流各自从 0 编号，跨流比较无意义）
        if is_stream:
            if key in seen_result_ids:
                failures.append(f"stream-frame[{frame['frame_index']}].result_frame_id 重复：{key}")
            seen_result_ids.add(key)

        # 逐值核对
        for name in ("age_result_ns", "age_frame_ns", "display_semantics", "boxes_drawn",
                     "zero_area_dropped", "stale_flag"):
            if row.get(name) != expected[name]:
                failures.append(f"frame[{frame['frame_index']}].{name}: {row.get(name)} != {expected[name]}")
        for name in ("stale_effective", "stale_reason"):
            if row.get(name) != expected.get(name):
                failures.append(f"frame[{frame['frame_index']}].{name}: {row.get(name)} != {expected.get(name)}")
        if row.get("state") != expected["state"]:
            failures.append(f"frame[{frame['frame_index']}].state: {row.get('state')} != {expected['state']}")

        # 逐框：矩形（允许 ≤1 px 但需记录）、边框像素数、标签锚点与 placement
        c_boxes = row.get("boxes") or []
        if len(c_boxes) != len(expected["boxes"]):
            failures.append(f"frame[{frame['frame_index']}].boxes 数量 {len(c_boxes)} != {len(expected['boxes'])}")
            case_verdicts.append({"frame_index": frame["frame_index"], "verdict": "box_count_mismatch"})
            continue
        verdict = "pixel_exact"
        notes: list[str] = []
        for index, (got, want) in enumerate(zip(c_boxes, expected["boxes"])):
            deltas = {axis: int(got.get(axis, 1 << 30)) - int(want[axis]) for axis in ("x1", "y1", "x2", "y2")}
            if any(delta != 0 for delta in deltas.values()):
                if all(abs(delta) <= 1 for delta in deltas.values()):
                    verdict = "within_1px"
                    notes.append(f"box[{index}] 矩形偏差 ≤1 px：{deltas}")
                else:
                    verdict = "pixel_mismatch"
                    failures.append(f"frame[{frame['frame_index']}].box[{index}] 矩形偏差 {deltas}")
            for name in ("border_pixels", "label_x", "label_y", "label_placement"):
                if got.get(name) != want[name]:
                    failures.append(f"frame[{frame['frame_index']}].box[{index}].{name}: "
                                    f"{got.get(name)} != {want[name]}")
                    verdict = "pixel_mismatch"
        mismatch_counts[verdict] = mismatch_counts.get(verdict, 0) + 1
        case_verdicts.append({"frame_index": frame["frame_index"], "verdict": verdict, "notes": notes})

        # HUD 13 字段
        hud = row.get("hud") or {}
        if len(hud) != HUD_FIELD_COUNT:
            failures.append(f"frame[{frame['frame_index']}].hud 字段数 {len(hud)} != {HUD_FIELD_COUNT}")
        for field in HUD_REQUIRED_NA:
            if hud.get(field) != "NA":
                failures.append(f"frame[{frame['frame_index']}].hud.{field} 必须为 NA（不得用 0 伪装）：{hud.get(field)!r}")

    # 计数逐项
    for name, want in counters.items():
        if summary.get(name) != want:
            failures.append(f"summary.{name}: {summary.get(name)} != {want}")
    if summary.get("canvas") != list(canvas):
        failures.append(f"summary.canvas: {summary.get('canvas')} != {list(canvas)}")
    if semantics != {R.DISPLAY_SEMANTICS}:
        failures.append(f"display_semantics 不唯一：{sorted(semantics)}")
    if len(stream_frames) >= 100 and seen_result_ids != set(range(len(stream_frames))):
        failures.append(f"长流 result_frame_id 未覆盖 0..{len(stream_frames) - 1}："
                        f"缺 {sorted(set(range(len(stream_frames))) - seen_result_ids)[:5]}")
    if displayed_ne_result_recorded == 0:
        failures.append("用例流中没有任何 displayed != result 帧（无法验证如实记录）")

    return {
        "schema_version": SCHEMA, "canvas": list(canvas),
        "frames_compared": len(all_frames), "case_verdicts": case_verdicts,
        "verdict_counts": mismatch_counts,
        "counters_expected": counters, "counters_from_c_summary": summary,
        "displayed_ne_result_frames": displayed_ne_result_recorded,
        "semantics_unique": sorted(semantics),
        "hud_field_count": HUD_FIELD_COUNT, "hud_na_required": list(HUD_REQUIRED_NA),
        "failures": failures, "passed": not failures,
        "limitations": [
            "本对拍证明 C 侧映射与冻结参考一致（宿主执行）；**不是**板上验证。",
            "输入为**合成**动态流，**非阶段4 输出**；阶段4 冻结结果接入后须复跑（另行 RunId）。",
            "HUD 的 CAPTURE_FPS/INFERENCE_FPS 在离线路径必然为 NA；板级实测仍 NOT_RUN。",
        ],
        "not_run": ["板上动态映射与绘制（B1–B10）", "真实回放接入（阶段4 契约未冻结）",
                    "摄像头采集路径", "30 分钟板上长跑（B6）", "T5-10 板上回归"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T02 对拍校验器（离线）")
    parser.add_argument("--cases", required=True)
    parser.add_argument("--stream", required=True)
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--canvas", default="1280x720")
    args = parser.parse_args(argv)
    canvas = tuple(int(value) for value in args.canvas.lower().split("x"))
    try:
        report = compare(pathlib.Path(args.cases), pathlib.Path(args.stream),
                         pathlib.Path(args.jsonl), canvas)
    except (InputError, FileNotFoundError, ValueError) as exc:
        print(f"[verify] 输入错误（退出码 2）：{exc}")
        return 2
    out = pathlib.Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[verify] frames={report['frames_compared']} verdicts={report['verdict_counts']} "
          f"failures={len(report['failures'])} passed={report['passed']}")
    for item in report["failures"][:10]:
        print(f"  - {item}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())