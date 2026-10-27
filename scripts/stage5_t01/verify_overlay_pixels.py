#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""显示缓冲**像素级**叠加对拍：期望边框像素由**冻结参考**按当前用例表重算。

与历史 `decode_mrd_rows.py` 的差别（2026-10-27 复审根因）：
  - 期望值**不再硬编码**（旧脚本的期望早于当前应用修订：期望红框 (64,64,255)、白角、平滑斜坡 252）；
    本脚本从 `s5_overlay_cases.h`（当前用例表）+ `verification/s5_display_geometry_reference.py` 现算；
  - 缓冲地址**不再硬编码**（由 `hw_buf_address.py` 从 UART 解析，见其文档字符串）；
  - 字节序**自动判定**（B,G,R 与 R,G,B 各试一次，报告判定结果；都不匹配即失败）。

用法：
    python -B scripts/stage5_t01/verify_overlay_pixels.py --dump <dump.txt> --case <id> \
        [--header <s5_overlay_cases.h>] [--source <s5_overlay.c>] [--json out.json]
退出码：0=全部通过；1=存在失败；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "verification"))
import s5_display_geometry_reference as R  # noqa: E402

CANVAS_W, CANVAS_H = 1280, 720
LINE_W = R.DISPLAY_LINE_WIDTH_PX
ROW_BEGIN = re.compile(r"S5_ROW_BEGIN\s+row=(\d+)\s+x=(\d+)")
WORD_LINE = re.compile(r"^\s*([0-9A-Fa-f]+)\s*:\s*((?:[0-9A-Fa-f]{8}\s*)+)$")


class InputError(RuntimeError):
    """输入不合法。"""


def parse_case_table(header: pathlib.Path) -> dict[int, list[dict]]:
    """从生成的用例头解析 `{x1,y1,x2,y2,cls,"label",...}` 与 S5_CASES 偏移。"""
    text = header.read_text(encoding="utf-8")
    boxes = []
    for m in re.finditer(r'\{\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(\d+),\s*"([^"]*)"', text):
        boxes.append({"rect": [int(m.group(i)) for i in range(1, 5)], "cls": int(m.group(5)),
                      "label": m.group(6)})
    cases: dict[int, list[dict]] = {}
    for m in re.finditer(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*"([^"]*)",\s*&S5_BOXES\[(\d+)\]', text):
        cid, nbox, _stale, _name, offset = (int(m.group(1)), int(m.group(2)), int(m.group(3)),
                                            m.group(4), int(m.group(5)))
        cases[cid] = boxes[offset:offset + nbox]
    return cases


def parse_class_colors(source: pathlib.Path) -> list[tuple[int, int, int]]:
    """从应用源码解析 S5_CLASS_COLOR（不另立第二套颜色定义）。"""
    text = source.read_text(encoding="utf-8")
    m = re.search(r"S5_CLASS_COLOR\[5\]\[3\]\s*=\s*\{(.*?)\};", text, re.S)
    if not m:
        raise InputError("未能从 s5_overlay.c 解析 S5_CLASS_COLOR")
    colors = []
    for triple in re.finditer(r"\{\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}", m.group(1)):
        colors.append(tuple(int(triple.group(i)) for i in range(1, 4)))
    if len(colors) != 5:
        raise InputError(f"S5_CLASS_COLOR 解析到 {len(colors)} 项，期望 5")
    return colors


def parse_hud_rect(source: pathlib.Path) -> tuple[int, int, int, int] | None:
    """HUD 面板矩形（应用最后绘制、会覆盖边框像素）；解析不到则返回 None 并如实报告。"""
    text = source.read_text(encoding="utf-8")
    names = {}
    for key in ("S5_HUD_X", "S5_HUD_Y", "S5_HUD_W", "S5_HUD_H"):
        m = re.search(rf"#define\s+{key}\s+(\d+)", text)
        if m:
            names[key] = int(m.group(1))
    if len(names) == 4:
        x, y, w, h = (names["S5_HUD_X"], names["S5_HUD_Y"], names["S5_HUD_W"], names["S5_HUD_H"])
        return x, y, x + w - 1, y + h - 1
    return None


def parse_dump(dump: pathlib.Path) -> dict[tuple[int, int], tuple[int, int, int]]:
    """解析 mrd 转储为 {(x,y): (b0,b1,b2)}。

    口径（与历史 `decode_mrd_rows.py` 一致）：mrd 以**32 位字**逐行打印，地址按行起始对齐；
    必须把一个**行段**内所有行按地址顺序拼成一条字节流，再按 **3 字节/像素** 重组，
    像素 x = x0 + (字节偏移)/3。**逐行重置 x 基准是错的**（会把每行都映射到 x0，只得到 1 像素/行）。
    """
    text = dump.read_text(encoding="utf-8", errors="replace")
    pixels: dict[tuple[int, int], tuple[int, int, int]] = {}
    row_y: int | None = None
    row_x0 = 0
    stream = bytearray()

    def flush() -> None:
        if row_y is None:
            return
        for offset in range(0, len(stream) - 2, 3):
            pixels[(row_x0 + offset // 3, row_y)] = (stream[offset], stream[offset + 1], stream[offset + 2])

    for line in text.splitlines():
        m = ROW_BEGIN.search(line)
        if m:
            flush()
            row_y, row_x0, stream = int(m.group(1)), int(m.group(2)), bytearray()
            continue
        m = WORD_LINE.match(line)
        if m and row_y is not None:
            for word in re.findall(r"[0-9A-Fa-f]{8}", m.group(2)):
                stream += bytes.fromhex(word)       # 字内小端
    flush()
    return pixels


ADDR_LINE = re.compile(r"^\s*([0-9A-Fa-f]+)\s*:\s*((?:[0-9A-Fa-f]{8}\s*)+)$")


def parse_dump_by_address(dump: pathlib.Path, buf0: int, stride: int) -> dict[tuple[int, int], tuple[int, int, int]]:
    """按 mrd **实际地址**重建像素（精确；不受行段起点是否像素对齐影响）。

    对每个 32 位字：从地址得到全局字节偏移 off；逐字节写入 (y=off//stride, x=(off%stride)//3) 的
    3 字节槽（槽内位置 off%3）；槽满后成为该像素值（不足/不完整则跳过并在 limits 中说明）。
    """
    text = dump.read_text(encoding="utf-8", errors="replace")
    slots: dict[tuple[int, int], list[int | None]] = {}
    for line in text.splitlines():
        m = ADDR_LINE.match(line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        word_bytes = b"".join(bytes.fromhex(w) for w in re.findall(r"[0-9A-Fa-f]{8}", m.group(2)))
        for index, value in enumerate(word_bytes):
            off = addr - buf0 + index
            if off < 0:
                continue
            y, x, pos = off // stride, (off % stride) // 3, off % 3
            slot = slots.setdefault((x, y), [None, None, None])
            slot[pos] = value
    pixels: dict[tuple[int, int], tuple[int, int, int]] = {}
    for key, slot in slots.items():
        if all(v is not None for v in slot):
            pixels[key] = (slot[0], slot[1], slot[2])
    return pixels


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="显示缓冲像素级叠加对拍（期望由冻结参考现算）")
    parser.add_argument("--dump", required=True)
    parser.add_argument("--case", type=int, required=True)
    parser.add_argument("--header", default=str(REPO_ROOT / "tmp/5/S5-T01/p1_app/build/s5_overlay_cases.h"))
    parser.add_argument("--source", default=str(REPO_ROOT / "scripts/stage5_t01/p1_app/s5_overlay.c"))
    parser.add_argument("--json", dest="json_out", default=None)
    parser.add_argument("--hud-rect", default=None,
                        help="HUD 面板矩形 x1,y1,x2,y2（最后绘制会覆盖边框）；如 14,14,318,296")
    parser.add_argument("--buf0", default="0x00138C00",
                        help="显示缓冲基地址（须与当轮应用 S5_P1_BUF0 一致）")
    parser.add_argument("--stride", type=int, default=3840, help="行字节跨度（1280*3）")
    parser.add_argument("--mode", choices=("address", "declared-x"), default="declared-x",
                        help="address=按 mrd 地址精确重建（推荐）；declared-x=按段声明 x 分组（旧口径）")
    parser.add_argument("--min-coverage", type=float, default=0.5,
                        help="部分行转储时的最低覆盖率（默认 0.5；板上定行转储可调低，颜色仍须全对）")
    args = parser.parse_args(argv)

    try:
        cases = parse_case_table(pathlib.Path(args.header))
        colors = parse_class_colors(pathlib.Path(args.source))
        hud = parse_hud_rect(pathlib.Path(args.source))
        if args.hud_rect:
            parts = [int(v) for v in args.hud_rect.split(",")]
            if len(parts) != 4:
                raise InputError("--hud-rect 需 x1,y1,x2,y2 四个整数")
            hud = tuple(parts)
        if args.mode == "address":
            pixels = parse_dump_by_address(pathlib.Path(args.dump), int(args.buf0, 16), int(args.stride))
        else:
            pixels = parse_dump(pathlib.Path(args.dump))
    except (InputError, OSError) as exc:
        print(f"[overlay-pixels] 输入错误：{exc}")
        return 2
    if args.case not in cases:
        print(f"[overlay-pixels] 用例 {args.case} 不在表内：{sorted(cases)}")
        return 2
    if not pixels:
        print("[overlay-pixels] 转储未解析到任何像素（格式或地址不符）")
        return 1

    boxes = cases[args.case]
    failures: list[str] = []
    per_box = []
    for index, box in enumerate(boxes):
        x1, y1, x2, y2 = box["rect"]
        expected_pixels = R.border_pixel_sets(x1, y1, x2, y2, LINE_W, CANVAS_W, CANVAS_H)
        visible = [p for p in expected_pixels
                   if p in pixels and not (hud and hud[0] <= p[0] <= hud[2] and hud[1] <= p[1] <= hud[3])]
        bgr = colors[box["cls"] % 5]        # 应用注释：DDR 内为 B,G,R
        rgb = (bgr[2], bgr[1], bgr[0])
        match_bgr = sum(1 for p in visible if tuple(pixels[p]) == bgr)
        match_rgb = sum(1 for p in visible if tuple(pixels[p]) == rgb)
        order = "BGR" if match_bgr >= match_rgb else "RGB"
        matched = max(match_bgr, match_rgb)
        coverage = (len(visible) / len(expected_pixels)) if expected_pixels else 0.0
        per_box.append({"index": index, "rect": box["rect"], "label": box["label"],
                        "expected_pixels": len(expected_pixels), "visible_in_dump": len(visible),
                        "coverage": round(coverage, 4), "matched_color": matched, "order": order,
                        "class_color_bgr": list(bgr)})
        if not visible:
            failures.append(f"box {index}: 期望边框像素**一个都没出现在转储里**（覆盖 0）")
        elif matched != len(visible):
            failures.append(f"box {index}: 边框颜色不符 {len(visible) - matched}/{len(visible)} 像素"
                            f"（判定字节序={order}）")
        elif coverage < args.min_coverage:
            failures.append(f"box {index}: 覆盖过低 {coverage:.2f}（转储未覆盖该框多数边框）")

    out = {"schema_version": "gestureforge_s5t01_overlay_pixel_verify_v1",
           "dump": str(args.dump), "case": args.case,
           "canvas": [CANVAS_W, CANVAS_H], "line_width": LINE_W,
           "hud_rect_excluded": hud, "pixels_parsed": len(pixels),
           "reconstruction_mode": args.mode, "buf0": args.buf0, "stride": int(args.stride),
           "boxes": per_box, "failures": failures, "passed": not failures,
           "min_coverage": args.min_coverage,
           "limitations": ["转储仅覆盖部分行；覆盖率低于 --min-coverage 即失败（默认 0.5）",
                           "HUD 面板区域按其绘制顺序排除（HUD 最后绘制会覆盖边框）"]}
    if args.json_out:
        pathlib.Path(args.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
    print(f"[overlay-pixels] case={args.case} boxes={len(boxes)} pixels={len(pixels)} "
          f"failures={len(failures)} passed={out['passed']}")
    for f in failures[:6]:
        print("  -", f)
    return 0 if out["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())