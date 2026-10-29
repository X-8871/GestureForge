"""生成 8x16 ASCII 点阵字库头文件（离线，一次性产物；构建时不依赖字体）。

依据与做法：
  · 只用 ASCII 0x20..0x7E（95 个可见字符），与 G0 冻结的“8x16 点阵”口径一致；
  · 用 DejaVu Sans Mono（matplotlib 随附，Bitstream Vera 派生，许可宽松）在 8x16 单元内
    栅格化，阈值 50% 二值化；等宽字体保证每个字符 advance 一致、不会越界；
  · 位序：bit7 = 最左列（与经典 VGA 8x16 字库一致），每个字符 16 字节；
  · 产物是纯 C 表，编译/链接阶段不读取任何系统字体，可复现（仅依赖本脚本 + 字体文件）。

用法：
  python tools/gen_font8x16.py --out src/s5_font8x16.h
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FIRST = 0x20
LAST = 0x7E
CELL_W = 8
CELL_H = 16
THRESHOLD = 128


def find_font() -> Path:
    """定位 DejaVu Sans Mono（优先 matplotlib 随附副本，避免依赖系统字体目录）。"""
    candidates = []
    try:
        import matplotlib

        candidates.append(Path(matplotlib.get_data_path()) / "fonts" / "ttf" / "DejaVuSansMono.ttf")
    except Exception:
        pass
    candidates.append(Path(r"C:\Windows\Fonts\DejaVuSansMono.ttf"))
    for c in candidates:
        if c.is_file():
            return c
    raise SystemExit("找不到 DejaVuSansMono.ttf；请安装 matplotlib 或指定字体路径")


def render_cell(font: ImageFont.FreeTypeFont, ch: str, baseline: int) -> list[int]:
    """把一个字符栅格化成 16 字节（每字节一行，bit7 在最左）。"""
    img = Image.new("L", (CELL_W, CELL_H), 0)
    draw = ImageDraw.Draw(img)
    # anchor="ls" = 左对齐 + 基线对齐，等宽字体下水平位置固定
    draw.text((0, baseline), ch, fill=255, font=font, anchor="ls")
    rows = []
    for y in range(CELL_H):
        byte = 0
        for x in range(CELL_W):
            if img.getpixel((x, y)) >= THRESHOLD:
                byte |= 1 << (7 - x)
        rows.append(byte)
    return rows


def pick_size(font_path: Path) -> tuple[int, int]:
    """选择“能在 8x16 内放下且清晰”的最大字号，返回 (字号, 基线行)。

    判据（避免相邻字符粘连、避免顶部/底部被裁）：
      · 字体 ascent+descent 必须 ≤ 15 行，基线放在第 1 行之下；
      · 所有字符的墨迹宽度 ≤ 7 列（右侧留 1 列空白，等宽字体下即字符间 1px 间隙）；
      · 墨迹不得高于第 0 行、不得低于第 15 行。
    """
    for size in range(16, 7, -1):
        font = ImageFont.truetype(str(font_path), size)
        ascent, descent = font.getmetrics()
        if ascent + descent > CELL_H - 1:
            continue
        baseline = 1 + ascent
        ok = True
        for code in range(FIRST, LAST + 1):
            img = Image.new("L", (CELL_W, CELL_H), 0)
            ImageDraw.Draw(img).text((0, baseline), chr(code), fill=255, font=font, anchor="ls")
            bbox = img.getbbox()
            if bbox is None:
                continue  # 空格
            left, top, right, bottom = bbox
            if right > 7 or left < 0 or bottom > CELL_H or top < 0:
                ok = False
                break
        if ok:
            return size, baseline
    return 8, 9


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="src/s5_font8x16.h")
    args = ap.parse_args()

    font_path = find_font()
    size, baseline = pick_size(font_path)
    font = ImageFont.truetype(str(font_path), size)

    glyphs = []
    for code in range(FIRST, LAST + 1):
        glyphs.append(render_cell(font, chr(code), baseline))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("/* 自动生成：tools/gen_font8x16.py —— 请勿手工编辑。")
    lines.append(f" * 字库来源：DejaVu Sans Mono，字号 {size}px，基线 {baseline}，8x16 单元，阈值 {THRESHOLD}。")
    lines.append(" * 许可：DejaVu 字体为 Bitstream Vera 派生（宽松许可）；本表为栅格化产物，随源码自带。")
    lines.append(" * 覆盖 ASCII 0x20..0x7E（95 字符），每字符 16 字节，bit7=最左列（同经典 VGA 8x16 字库）。")
    lines.append(" */")
    lines.append("#ifndef S5_FONT8X16_H")
    lines.append("#define S5_FONT8X16_H")
    lines.append("")
    lines.append("#include <stdint.h>")
    lines.append("")
    lines.append("#define S5_FONT_W 8")
    lines.append("#define S5_FONT_H 16")
    lines.append(f"#define S5_FONT_FIRST 0x{FIRST:02X}u")
    lines.append(f"#define S5_FONT_LAST  0x{LAST:02X}u")
    lines.append("")
    lines.append("static const uint8_t s5_font8x16[95][16] = {")
    for i, g in enumerate(glyphs):
        ch = chr(FIRST + i)
        label = "space" if ch == " " else (ch if ch.isprintable() else "?")
        body = ", ".join(f"0x{b:02X}" for b in g)
        lines.append(f"    {{ {body} }},  /* 0x{FIRST + i:02X} '{label}' */")
    lines.append("};")
    lines.append("")
    lines.append("#endif /* S5_FONT8X16_H */")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # 自检图：用生成的位图拼一行字样，便于人工确认可读性
    preview = Image.new("L", (8 * 40, 16 * 3), 0)
    sample = ["S5 DISPLAY 1280x720  FPS 30.0", "FRAME 012345 LAT 16 AGE 25", "AGE OK  VDMA RUN  CAM OK"]
    for li, text in enumerate(sample):
        for ci, ch in enumerate(text):
            code = ord(ch)
            if not (FIRST <= code <= LAST):
                continue
            g = glyphs[code - FIRST]
            for y in range(CELL_H):
                for x in range(CELL_W):
                    if g[y] & (1 << (7 - x)):
                        preview.putpixel((ci * 8 + x, li * 16 + y), 255)
    preview.save(Path("build") / "font_preview.png")
    print(f"字体：{font_path}  字号={size} 基线={baseline}")
    print(f"输出：{out}")
    print(f"预览：build/font_preview.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())