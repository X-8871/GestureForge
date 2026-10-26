#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T02 合成动态流生成器：产出 C 侧可执行的 TSV（框架 + 6 用例 + 3 过期边界 + 120 帧流）。

产物
====
- `cases.tsv`      ：6 个必备用例（单框/四角/15 框/零框/边缘+补边带/过期）+ 3 个过期边界，每例一帧；
- `stream_120.tsv` ：120 帧五元组流（含 warmup/timeout/error/duplicate/out_of_order/NO_HAND/stale 与丢帧计数）；
- `cases_meta.json`：用例编号、意图、帧号、画布来源与标签尺寸口径（供证据与复核）。

纪律
====
- 画布取自 `scripts/stage5_t01/gen_overlay_cases.py` 的 `CANVAS_W/CANVAS_H`（**不假定** 1280×720，按任务卡 §7.1 从既有源核验）；
- 标签墨迹盒用**渲染层同一字体与同一 `_text_box`** 计算（UR-3 字号），保证标签锚点对拍可比；
- 输入为**合成**坐标，**非阶段4 输出**（逐处标注）。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402

DEFAULT_LIMIT_NS = R.STALE_AGE_LIMIT_NS
PERIOD_NS = 16_890_000                     # 与阶段5 显示帧周期口径一致（离线虚拟步长）
BASE_CAPTURE_NS = 1_000_000_000
CLASS_NAMES = {0: "fist", 1: "palm", 2: "one", 3: "two_up", 4: "three"}


def canvas_from_source() -> tuple[int, int]:
    """从既有 P1 生成器解析画布常量（不执行其代码）。"""
    text = (REPO_ROOT / "scripts/stage5_t01/gen_overlay_cases.py").read_text(encoding="utf-8")
    match = re.search(r"^CANVAS_W, CANVAS_H = (\d+), (\d+)", text, re.M)
    if not match:
        raise RuntimeError("未能从 gen_overlay_cases.py 解析 CANVAS_W/CANVAS_H")
    return int(match.group(1)), int(match.group(2))


def label_sizes(text: str, canvas_height: int) -> tuple[int, int, dict[str, Any]]:
    """标签墨迹盒（与渲染层同一字体/同一 `_text_box`）；缺 Pillow 时用确定性估算并标注。"""
    if not RD.PIL_AVAILABLE:
        return max(1, 6 * len(text)), 11, {"source": "estimate_no_pillow", "scaled": False}
    font, info = RD.load_font(RD.font_size_px(canvas_height))
    image = RD.Image.new("RGB", (8, 8))
    draw = RD.ImageDraw.Draw(image)
    width, height, _, _ = RD._text_box(draw, text, font)
    return int(width), int(height), dict(info, source="pillow_textbbox")


def box_record(index: int, class_id: int, score: float, xyxy: tuple[float, float, float, float],
               canvas_height: int) -> tuple[str, dict[str, Any]]:
    text = f"{CLASS_NAMES[class_id].upper()} {score:.2f}"
    width, height, info = label_sizes(text, canvas_height)
    line = (f"B {class_id} {score:.6f} {xyxy[0]:.6f} {xyxy[1]:.6f} {xyxy[2]:.6f} {xyxy[3]:.6f} "
            f"{width} {height}")
    return line, {"text": text, "label_w": width, "label_h": height, "label_source": info.get("source")}


def frame_lines(index: int, *, displayed_frame_id: int, result_frame_id: int, result_seq: int,
                capture_ns: int, result_ns: int, commit_ns: int, stale_flag: int, warmup: int,
                state: str, boxes: list[tuple[int, float, tuple[float, float, float, float]]],
                canvas_height: int, comment: str | None = None) -> list[str]:
    lines: list[str] = []
    if comment:
        lines.append(f"# {comment}")
    lines.append(f"F {index} {displayed_frame_id} {result_frame_id} {result_seq} {capture_ns} "
                 f"{result_ns} {commit_ns} {stale_flag} {warmup} {state} {len(boxes)}")
    for box_index, (class_id, score, xyxy) in enumerate(boxes):
        line, _ = box_record(box_index, class_id, score, xyxy, canvas_height)
        lines.append(line)
    lines.append("E")
    return lines


def build_cases(canvas_height: int) -> tuple[list[str], list[dict[str, Any]]]:
    """6 个必备用例 + 3 个过期边界（每例一帧）。"""
    lines: list[str] = ["# S5-T02 合成用例（非阶段4 输出）"]
    meta: list[dict[str, Any]] = []
    index = 0

    def add(case_id: str, intent: str, **kwargs: Any) -> None:
        nonlocal index
        lines.extend(frame_lines(index, canvas_height=canvas_height, comment=f"{case_id}: {intent}", **kwargs))
        meta.append({"case_id": case_id, "intent": intent, "frame_index": index})
        index += 1

    base = BASE_CAPTURE_NS
    age_fresh = 1_000_000                                  # 1 ms：不过期
    add("single_box", "单框居中",
        displayed_frame_id=0, result_frame_id=0, result_seq=1,
        capture_ns=base, result_ns=base + 500_000, commit_ns=base + 500_000 + age_fresh,
        stale_flag=0, warmup=0, state="OK",
        boxes=[(1, 0.91, (0.40, 0.40, 0.62, 0.66))])
    add("four_corners", "四角各一框（检验逐边钳位）",
        displayed_frame_id=1, result_frame_id=1, result_seq=2,
        capture_ns=base + PERIOD_NS, result_ns=base + PERIOD_NS + 500_000,
        commit_ns=base + PERIOD_NS + 500_000 + age_fresh, stale_flag=0, warmup=0, state="OK",
        boxes=[(0, 0.80, (0.001, 0.001, 0.10, 0.12)), (2, 0.82, (0.90, 0.001, 0.999, 0.12)),
               (3, 0.84, (0.001, 0.88, 0.10, 0.999)), (4, 0.86, (0.90, 0.88, 0.999, 0.999))])
    add("boxes_15", "15 框上限、稳定顺序不重排",
        displayed_frame_id=2, result_frame_id=2, result_seq=3,
        capture_ns=base + 2 * PERIOD_NS, result_ns=base + 2 * PERIOD_NS + 500_000,
        commit_ns=base + 2 * PERIOD_NS + 500_000 + age_fresh, stale_flag=0, warmup=0, state="OK",
        boxes=[(i % 5, 0.50 + 0.03 * i, (0.02 + 0.06 * i, 0.05 + 0.05 * (i % 4),
                                        0.02 + 0.06 * i + 0.05, 0.05 + 0.05 * (i % 4) + 0.10))
               for i in range(15)])
    add("zero_boxes", "无手势 ⇒ boxes=0（**非过期**）",
        displayed_frame_id=3, result_frame_id=3, result_seq=4,
        capture_ns=base + 3 * PERIOD_NS, result_ns=base + 3 * PERIOD_NS + 500_000,
        commit_ns=base + 3 * PERIOD_NS + 500_000 + age_fresh, stale_flag=0, warmup=0,
        state="NO_HAND", boxes=[])
    add("edge_padding_band", "贴边 + 奇数补边带（含越界裁剪）",
        displayed_frame_id=4, result_frame_id=4, result_seq=5,
        capture_ns=base + 4 * PERIOD_NS, result_ns=base + 4 * PERIOD_NS + 500_000,
        commit_ns=base + 4 * PERIOD_NS + 500_000 + age_fresh, stale_flag=0, warmup=0, state="OK",
        boxes=[(1, 0.77, (0.0, 0.0, 0.25, 0.25)), (2, 0.78, (-0.02, 0.115, 0.20, 0.28)),
               (3, 0.79, (0.80, 0.83, 1.02, 1.0)), (4, 0.75, (0.0, 0.125, 1.0, 0.13))])
    add("stale_case", "显式 stale_flag ⇒ 不绘制、stale_cleared+1",
        displayed_frame_id=5, result_frame_id=5, result_seq=6,
        capture_ns=base + 5 * PERIOD_NS, result_ns=base + 5 * PERIOD_NS + 500_000,
        commit_ns=base + 5 * PERIOD_NS + 500_000 + age_fresh, stale_flag=1, warmup=0, state="OK",
        boxes=[(0, 0.70, (0.30, 0.30, 0.50, 0.55))])

    # 三个过期边界：age == limit（不过期）/ limit+1（过期）/ 显式标志（age 很小）
    limit = DEFAULT_LIMIT_NS
    # 注意：过期判据用的是 age_frame = overlay_commit − capture（不是 age_result）
    add("edge_age_equals_limit", "age_frame==limit 不过期（严格 >）",
        displayed_frame_id=6, result_frame_id=6, result_seq=7,
        capture_ns=base + 6 * PERIOD_NS, result_ns=base + 6 * PERIOD_NS + 500_000,
        commit_ns=base + 6 * PERIOD_NS + limit, stale_flag=0, warmup=0, state="OK",
        boxes=[(1, 0.88, (0.35, 0.35, 0.55, 0.60))])
    add("edge_age_limit_plus_one", "age_frame==limit+1 过期且计数 +1",
        displayed_frame_id=7, result_frame_id=7, result_seq=8,
        capture_ns=base + 7 * PERIOD_NS, result_ns=base + 7 * PERIOD_NS + 500_000,
        commit_ns=base + 7 * PERIOD_NS + limit + 1, stale_flag=0, warmup=0, state="OK",
        boxes=[(1, 0.88, (0.35, 0.35, 0.55, 0.60))])
    add("edge_explicit_stale_flag", "显式 stale_flag（age 很小）过期",
        displayed_frame_id=8, result_frame_id=8, result_seq=9,
        capture_ns=base + 8 * PERIOD_NS, result_ns=base + 8 * PERIOD_NS + 500_000,
        commit_ns=base + 8 * PERIOD_NS + 500_000 + age_fresh, stale_flag=1, warmup=0, state="OK",
        boxes=[(1, 0.88, (0.35, 0.35, 0.55, 0.60))])
    return lines, meta


def build_stream(canvas_height: int, frames: int = 120) -> tuple[list[str], dict[str, Any]]:
    """≥100 帧五元组流：含预热/超时/错误/等价/乱序/无手势/过期与丢帧计数。"""
    lines: list[str] = ["# S5-T02 合成动态流（非阶段4 输出）：五元组 + 故障计数 + HUD 13 字段"]
    dropped = 4
    lines.append(f"D {dropped}")
    plan = {
        "warmup": {0, 1, 2},
        "timeout": {40, 41},
        "error": {60},
        "duplicate": {70, 71},
        "out_of_order": {80, 81},
        "no_hand": {20, 21, 22},
        "stale": {100, 101},
    }
    for index in range(frames):
        capture = BASE_CAPTURE_NS + index * PERIOD_NS
        result_ns = capture + 500_000
        commit = result_ns + 1_000_000
        state = "OK"
        stale_flag = 0
        warmup = 1 if index in plan["warmup"] else 0
        boxes: list[tuple[int, float, tuple[float, float, float, float]]] = []
        if index in plan["timeout"]:
            state = "TIMEOUT"
        elif index in plan["error"]:
            state = "ERROR"
        elif index in plan["duplicate"]:
            state = "DUPLICATE"
        elif index in plan["out_of_order"]:
            state = "OUT_OF_ORDER"
        elif index in plan["no_hand"]:
            state = "NO_HAND"
        else:
            if index in plan["stale"]:
                stale_flag = 1
            count = 1 + (index % 3)
            for k in range(count):
                x = 0.05 + 0.07 * ((index + k) % 10)
                y = 0.08 + 0.06 * ((index + 2 * k) % 8)
                boxes.append((k % 5, 0.55 + 0.02 * k, (x, y, min(0.999, x + 0.12), min(0.999, y + 0.16))))
        lines.extend(frame_lines(index, displayed_frame_id=(index - 1 if index in (50, 51) else index),
                                 result_frame_id=index,
                                 result_seq=index + 1, capture_ns=capture, result_ns=result_ns,
                                 commit_ns=commit, stale_flag=stale_flag, warmup=warmup, state=state,
                                 boxes=boxes, canvas_height=canvas_height))
    meta = {"frames": frames, "dropped_frames": dropped, "plan": {k: sorted(v) for k, v in plan.items()},
            "frame_period_ns": PERIOD_NS, "note": "合成动态流；非阶段4 输出"}
    return lines, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T02 合成动态流生成器")
    parser.add_argument("--out", required=True, help="输出目录（隔离到新 RunId）")
    parser.add_argument("--frames", type=int, default=120)
    args = parser.parse_args(argv)
    out = pathlib.Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    width, height = canvas_from_source()
    case_lines, case_meta = build_cases(height)
    stream_lines, stream_meta = build_stream(height, frames=args.frames)
    (out / "cases.tsv").write_text("\n".join(case_lines) + "\n", encoding="utf-8", newline="\n")
    (out / "stream_120.tsv").write_text("\n".join(stream_lines) + "\n", encoding="utf-8", newline="\n")
    meta = {
        "schema_version": "gestureforge_s5t02_dynamic_stream_v1",
        "canvas": [width, height],
        "canvas_source": "scripts/stage5_t01/gen_overlay_cases.py:CANVAS_W, CANVAS_H（HDMI 实测模式）",
        "label_source": "scripts/stage5_t03/s5t03_render.py 的同一字体与 _text_box（UR-3 字号）",
        "stale_age_limit_ns": DEFAULT_LIMIT_NS,
        "cases": case_meta,
        "stream": stream_meta,
        "input_scope": "synthetic_dynamic_stream_not_stage4_output",
        "contract_id": R.CONTRACT_ID,
    }
    (out / "cases_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
    print(f"[gen] canvas={width}x{height} cases={len(case_meta)} stream_frames={stream_meta['frames']} "
          f"out={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())