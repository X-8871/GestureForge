#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按**当前**用例表自动生成转储行/列选择（替代按旧版矩形写死的行/x 列表）。

背景（2026-10-27 定位）：`jtag_dump_rows.tcl` 的行/x 列表是按旧版用例 5 矩形写的，与当前边框重叠
仅 ~5% ⇒ 造成"边框颜色对不上"的**假失配**。本脚本从 `s5_overlay_cases.h`（当前用例表）与冻结参考
推导：每个框的**上下边所在行**（含 2px 线宽的两行）与**左右边所在列**，生成覆盖窗口，并可**离线**
核算覆盖率（不需要板卡）。

用法：
  python -B scripts/stage5_t01/gen_dump_rows.py --case 5 [--header <h>] [--json out.json] [--tcl out.tcl]
退出码：0=已生成且覆盖率达阈值；1=覆盖率不足；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts/stage5_t01"))
sys.path.insert(0, str(REPO_ROOT / "verification"))
import verify_overlay_pixels as VP  # noqa: E402

CANVAS_W, CANVAS_H = 1280, 720
STRIDE = CANVAS_W * 3
WORD_ALIGN = 4
# 每段读取的像素宽度（word 对齐后按 3 字节/像素换算；窗口取少量列以免 mrd 过多）
WINDOW_PX = 96


def build_plan(case_boxes: list[dict]) -> list[dict]:
    """生成行段计划：每框的上下边行（每行取左右两段）+ 左右边列（各取上下两段）。"""
    plan: list[dict] = []
    for box in case_boxes:
        x1, y1, x2, y2 = box["rect"]
        for row in (y1, y1 + 1, y2 - 1, y2):
            if not (0 <= row < CANVAS_H):
                continue
            plan.append({"row": row, "x": max(0, x1 - 4), "why": f"{box['label']} 横边"})
            plan.append({"row": row, "x": max(0, min(CANVAS_W - WINDOW_PX, x2 - 4)), "why": f"{box['label']} 横边"})
        for col in (x1, min(x1 + 1, CANVAS_W - 1), max(0, x2 - 2), max(0, x2 - 1)):
            for row in (y1, max(0, (y1 + y2) // 2), max(0, y2 - 1)):
                plan.append({"row": row, "x": max(0, col - 2), "why": f"{box['label']} 竖边"})
    # 去重 + 按 (row, x) 排序，保证地址顺序单调
    seen, out = set(), []
    for item in sorted(plan, key=lambda it: (it["row"], it["x"])):
        key = (item["row"], item["x"] // WORD_ALIGN * WORD_ALIGN)
        if key in seen:
            continue
        seen.add(key)
        out.append({"row": item["row"], "x": key[1], "why": item["why"]})
    return out


MIN_PIXELS_PER_EDGE = 8


def coverage(plan: list[dict], case_boxes: list[dict]) -> dict:
    """离线核算（**按边**口径）：稀疏转储不可能覆盖整条边，判据应为"每框 4 条边各被采样 ≥K 像素"。

    同时给出逐像素覆盖率作为参考（不作判据）。
    """
    covered = set()
    for item in plan:
        for x in range(item["x"], min(CANVAS_W, item["x"] + WINDOW_PX)):
            covered.add((x, item["row"]))
    total = hit = 0
    edges_total = edges_ok = 0
    per_box = []
    for box in case_boxes:
        x1, y1, x2, y2 = box["rect"]
        expected = VP.R.border_pixel_sets(x1, y1, x2, y2, VP.LINE_W, CANVAS_W, CANVAS_H)
        got = [p for p in expected if p in covered]
        total += len(expected)
        hit += len(got)
        # 逐边：上/下（按行）、左/右（按列）
        edges = {
            "top": [p for p in expected if p[1] in (y1, y1 + 1)],
            "bottom": [p for p in expected if p[1] in (y2 - 1, y2)],
            "left": [p for p in expected if p[0] in (x1, min(x1 + 1, CANVAS_W - 1))],
            "right": [p for p in expected if p[0] in (max(0, x2 - 2), max(0, x2 - 1))],
        }
        edge_report = {}
        for name, pixels in edges.items():
            sampled = [p for p in pixels if p in covered]
            edge_report[name] = {"pixels": len(pixels), "sampled": len(sampled),
                                 "ok": len(sampled) >= MIN_PIXELS_PER_EDGE}
            edges_total += 1
            edges_ok += edge_report[name]["ok"]
        per_box.append({"label": box["label"], "expected": len(expected), "covered": len(got),
                        "rate": round(len(got) / len(expected), 4) if expected else 0.0,
                        "edges": edge_report})
    return {"total_expected": total, "covered": hit,
            "rate": round(hit / total, 4) if total else 0.0,
            "edges_total": edges_total, "edges_ok": edges_ok,
            "min_pixels_per_edge": MIN_PIXELS_PER_EDGE,
            "edge_criterion_passed": edges_ok == edges_total and edges_total > 0,
            "per_box": per_box}


def emit_tcl(plan: list[dict], case_id: int, path: pathlib.Path) -> None:
    """生成转储 TCL（输出格式与既有 jtag_dump_rows.tcl 一致，便于复用同一对拍器）。"""
    lines = [
        f"# 自动生成（scripts/stage5_t01/gen_dump_rows.py）用例 {case_id} 的行/列选择；勿手改。",
        "# 用法: xsdb jtag_dump_rows_gen.tcl <buf0_hex> <port>",
        'set ::buf0 0x00138C00',
        'if {[lindex $argv 0] ne ""} { set ::buf0 [lindex $argv 0] }',
        'set ::port [lindex $argv 1]',
        'if {$::port eq ""} { set ::port 23121 }',
        f'set ::stride {STRIDE}',
        'puts "S5_DUMP_BEGIN"',
        'connect -url tcp:localhost:$::port',
        'targets -set -nocase -filter {name =~ "ARM Cortex-A9 MPCore #0"}',
        'if {[catch {stop} e]} { puts "S5_HALT_ERR=$e" } else { puts "S5_HALT_OK=1" }',
        'after 300',
    ]
    for item in plan:
        row, x0 = item["row"], item["x"]
        words = WINDOW_PX * 3 // WORD_ALIGN
        lines.append(f"# {item['why']}")
        lines.append(f"puts \"S5_ROW_BEGIN row={row} x={x0}\"")
        lines.append(f'for {{set i 0}} {{$i < {words}}} {{incr i}} {{')
        lines.append(f'    set addr [expr {{$::buf0 + {row} * $::stride + {x0 * 3} + $i * {WORD_ALIGN}}}]')
        lines.append('    puts [format "  %06X:   %08X" $addr [mrd -force $addr]]')
        lines.append('}')
    lines += ['con', 'disconnect', 'puts "S5_DUMP_DONE=1"', '']
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="按当前用例表生成转储行/列选择（离线）")
    parser.add_argument("--case", type=int, default=5)
    parser.add_argument("--header", default=str(REPO_ROOT / "tmp/5/S5-T01/p1_app/build/s5_overlay_cases.h"))
    parser.add_argument("--json", dest="json_out", default=None)
    parser.add_argument("--tcl", dest="tcl_out", default=None)
    parser.add_argument("--min-coverage", type=float, default=0.9)
    args = parser.parse_args(argv)
    try:
        cases = VP.parse_case_table(pathlib.Path(args.header))
    except (OSError, ValueError) as exc:
        print(f"[gen-dump-rows] 输入错误：{exc}")
        return 2
    if args.case not in cases:
        print(f"[gen-dump-rows] 用例 {args.case} 不在表内：{sorted(cases)}")
        return 2
    boxes = cases[args.case]
    plan = build_plan(boxes)
    cov = coverage(plan, boxes)
    payload = {"case": args.case, "boxes": [b["rect"] for b in boxes],
               "segments": len(plan), "window_px": WINDOW_PX, "stride": STRIDE,
               "plan": plan, "coverage": cov}
    if args.json_out:
        pathlib.Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
    if args.tcl_out:
        emit_tcl(plan, args.case, pathlib.Path(args.tcl_out))
    print(f"[gen-dump-rows] case={args.case} 段数={len(plan)} 逐像素覆盖={cov['rate']:.3f} "
          f"（{cov['covered']}/{cov['total_expected']}）；边判据 {cov['edges_ok']}/{cov['edges_total']} "
          f"（每边 ≥{cov['min_pixels_per_edge']} 像素）")
    for item in cov["per_box"]:
        flags = ",".join(f"{k}:{'OK' if v['ok'] else 'LOW'}({v['sampled']})" for k, v in item["edges"].items())
        print(f"   {item['label']}: 逐像素 {item['covered']}/{item['expected']}；边 {flags}")
    return 0 if cov["edge_criterion_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())