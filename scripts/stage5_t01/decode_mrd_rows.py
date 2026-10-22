"""S5-T01 把 xsdb `mrd` 的字转储解码成**逐像素**并做几何断言。

输入：jtag_dump_rows.tcl 的输出（含 `S5_ROW_BEGIN row=<y> x=<x0>[ buf1|buf2]` 分段标记 + mrd 行）。
方法：mrd 以 32 位字打印（地址按行起始对齐），把每个字按小端拆成 4 字节，按 3 字节/像素重组；
      像素 x = x0 + (字节偏移)/3。断言用**冻结参考实现**给出的用例 5 期望矩形。

用法：python -B scripts/stage5_t01/decode_mrd_rows.py --log <dump.txt> [--json <out.json>]
退出码：0=全部断言通过；1=有断言失败；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# 期望值（来自 verification/s5_display_geometry_reference.py 对用例 5 的计算；见 case_photo_evidence.json）
EXPECT = {
    "red_bbox": (0, 53, 77, 425),        # FIST 类色 (r=255,g=64,b=64) → DDR 字节 B,G,R = 40,40,FF
    "green_bbox": (513, 0, 1025, 66),    # PALM 类色 (r=64,g=255,b=64) → 40,FF,40
}
RED = (0x40, 0x40, 0xFF)      # (B,G,R)
GREEN = (0x40, 0xFF, 0x40)
WHITE = (0xFF, 0xFF, 0xFF)
LINE_W = 2

WORD_RE = re.compile(r"^\s*([0-9A-Fa-f]+):\s+(.*)$")
ROW_RE = re.compile(r"^S5_ROW_BEGIN row=(\d+) x=(\d+)(?:\s+(\w+))?\s*$")


def parse(log_text: str) -> dict[tuple[int, int, str], dict[int, tuple[int, int, int]]]:
    """返回 {(row, x0, tag): {x: (B,G,R)}}"""
    rows: dict[tuple[int, int, str], dict[int, bytes]] = {}
    current: tuple[int, int, str] | None = None
    for line in log_text.splitlines():
        match = ROW_RE.match(line.strip())
        if match:
            current = (int(match.group(1)), int(match.group(2)), match.group(3) or "buf0")
            rows[current] = {}
            continue
        word = WORD_RE.match(line)
        if word and current is not None:
            addr = int(word.group(1), 16)
            for index, token in enumerate(word.group(2).split()):
                if len(token) != 8:
                    continue
                value = int(token, 16)
                chunk = value.to_bytes(4, "little")
                for byte_index, byte in enumerate(chunk):
                    rows[current][addr + index * 4 + byte_index] = byte
    # 字节映射 → 像素
    out: dict[tuple[int, int, str], dict[int, tuple[int, int, int]]] = {}
    for key, byte_map in rows.items():
        row, x0, tag = key
        base = min(byte_map) if byte_map else 0
        pixels: dict[int, tuple[int, int, int]] = {}
        for offset in sorted(byte_map):
            if offset - base + 2 >= 3 * 100000:
                pass
            rel = offset - base
            pixel_index = rel // 3
            if rel % 3 != 0:
                continue
            trio = [byte_map.get(offset + i) for i in range(3)]
            if any(t is None for t in trio):
                continue
            pixels[x0 + pixel_index] = (trio[0], trio[1], trio[2])
        out[key] = pixels
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()
    path = pathlib.Path(args.log)
    if not path.exists():
        print(f"[decode] 不存在：{path}")
        return 2
    pixels_by_row = parse(path.read_text(encoding="utf-8", errors="replace"))
    if not pixels_by_row:
        print("[decode] 未解析到任何像素（检查 S5_ROW_BEGIN 标记与 mrd 输出）")
        return 2

    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    # 1) 行 0 白角标记（x 0..15 全白）
    key = (0, 0, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        got = [px.get(x) for x in range(0, 16)]
        ok = all(v == WHITE for v in got)
        add("row0_x0_15_white_corner", ok, f"x0..15={got[:4]}...{'全部白' if ok else '存在非白'}")

    # 2) 行 53：红框顶边在 HUD 覆盖带**左侧**的部分（HUD 置顶，x 23..123 被 HUD 面板覆盖）
    key = (53, 0, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        red_span = [x for x in range(0, 85) if px.get(x) == RED]
        ok = bool(red_span) and min(red_span) == 0 and max(red_span) >= 20
        add("row53_red_top_border_left_of_hud", ok,
            f"红色像素 x 范围=[{min(red_span) if red_span else '无'}..{max(red_span) if red_span else '无'}]"
            f"（x 23..123 为 HUD 面板，置顶覆盖；期望可见部分自 x=0 起）")
        outside = [px.get(x) for x in (80, 82, 84)]
        add("row53_x80_84_background", all(v is not None and v != RED for v in outside),
            f"x=80,82,84 取值={outside}（应为斜坡背景，非红）")

    # 2b) 行 200：红框右边界列 77,78（该行不在 HUD/标签覆盖带内）
    key = (200, 64, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        add("row200_red_right_border_77_78",
            px.get(77) == RED and px.get(78) == RED,
            f"x=77,78 取值=[{px.get(77)}, {px.get(78)}]，期望 (64,64,255)")
        add("row200_x100_background", px.get(100) != RED, f"x=100 取值={px.get(100)}")
    key = (200, 0, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        add("row200_red_left_border_0_1", px.get(0) == RED and px.get(1) == RED,
            f"x=0,1 取值=[{px.get(0)}, {px.get(1)}]")

    # 3) 行 53：绿框左边界列 513,514（x0=512 段）
    key = (53, 512, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        green_span = sorted(x for x, v in px.items() if v == GREEN)
        ok = green_span[:2] == [513, 514] if len(green_span) >= 2 else False
        add("row53_green_left_border_513_514", bool(ok), f"绿色像素 x={green_span} 期望起始 513,514")
        add("row53_green_inside_is_background", px.get(560) != GREEN, f"x=560 取值={px.get(560)}")

    # 4) 行 66：绿框底边（应有连续绿色像素）
    key = (66, 512, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        green_span = sorted(x for x, v in px.items() if v == GREEN)
        add("row66_green_bottom_border_present", len(green_span) >= 40,
            f"绿色像素数={len(green_span)}（行 66 为绿框底边，应近乎连续）")

    # 5) 行 359：红框左边界列 0,1
    key = (359, 0, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        left = [px.get(0), px.get(1)]
        add("row359_red_left_border_0_1", all(v == RED for v in left), f"x=0,1 取值={left}")

    # 6) 行 359 x=1256 段：该处**不是**角标记（角标记只在画布四角），应等于斜坡值 floor(x*255/1279)
    key = (359, 1256, "buf0")
    if key in pixels_by_row:
        px = pixels_by_row[key]
        expect_v = int(1264 * 255 / 1279)
        got = px.get(1264)
        add("row359_x1264_smooth_ramp_value",
            got is not None and abs(got[0] - expect_v) <= 1 and got[0] == got[1] == got[2],
            f"x=1264 取值={got}，期望灰度 ≈{expect_v}（D-1 平滑斜坡；该行无角标记）")

    # 7) 三块送显缓冲首字一致（buf1/buf2 段只 dump 了前 8 字）
    for tag in ("buf1", "buf2"):
        key = (0, 0, tag)
        if key in pixels_by_row:
            px = pixels_by_row[key]
            first = [px.get(x) for x in range(0, 4)]
            add(f"{tag}_row0_white_corner", all(v == WHITE for v in first), f"x0..3={first}")

    failed = [c for c in checks if c["status"] == "FAIL"]
    summary = {"log": str(path), "rows_parsed": [f"row={k[0]} x={k[1]} {k[2]}" for k in pixels_by_row],
               "checks": checks, "passed": len(checks) - len(failed), "failed": len(failed)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[decode] PASS={summary['passed']} FAIL={summary['failed']}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())