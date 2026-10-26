#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线 replay/display 骨架：把 `DisplayPipeline` 的逐帧决策**栅格化**为离线显示帧。

角色
====
本模块补上 S5-T03 骨架原先缺失的**实现层渲染路径**（此前 `NOT_RUN`）：把已判定的
`box_px` / HUD / 状态画成位图，供人工抽检与差异定位。它**只消费**决策结果，不重新判定任何
阈值（过期/预热/拒收全部由 `s5t03_display_pipeline.py` 决定）。

单一来源
========
几何与取整**只从** `verification/s5_display_geometry_reference.py`（`S5A-G0-v2`）导入：
- 边框像素集：`R.border_pixel_sets`（2 px 偶数线宽居中、逐边钳到画布内）——本模块不写第二套；
- 字号：UR-3 决策 `round_half_up(16 × canvas_height / 720)`；
- 安全区：`round_half_up(16 × canvas_height / 1080)`（`SAFE_AREA_PX_1080P` 的相对缩放）；
- 类别色：UR-3 决策（`fist #0072B2` / `palm #E69F00` / `one #009E73` / `two_up #CC79A7` / `three #D55E00`）。

诚实边界
========
- 输入仍是**合成流**（`synthetic_replay`）；本模块**不接**板卡/摄像头/UART/JTAG，不读真实回放结果包。
- 渲染产物是**离线位图**，不代表板上绘制、不代表 G0/G1/G3/G4/G5 通过。
- 文本渲染依赖宿主字体：字体身份与 SHA 由 `load_font()` 返回并须写入清单；取不到可缩放字体时
  退回 Pillow 内置位图字体并显式标 `scaled=false`（不假装满足了 16 px 规格）。
"""

from __future__ import annotations

import hashlib
import pathlib
import sys
from typing import Any, Mapping, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402

try:  # Pillow 为渲染依赖；缺失时必须在调用点显式失败，不静默跳过
    from PIL import Image, ImageDraw, ImageFont, __version__ as PILLOW_VERSION
    PIL_AVAILABLE = True
    PIL_IMPORT_ERROR = None
except Exception as _exc:  # pragma: no cover - 环境缺 Pillow 时走这里
    Image = ImageDraw = ImageFont = None  # type: ignore[assignment]
    PILLOW_VERSION = None
    PIL_AVAILABLE = False
    PIL_IMPORT_ERROR = str(_exc)

# ── UR-3 决策（2026-10-25；Wong 授权 Codex 项目总控确定数值与显示参数）──────────
UR3_DECISION_DOC = "docs/stage5/s5a_g0_ur3_decision_20261025_r01.md"
CLASS_COLORS_RGB: dict[str, tuple[int, int, int]] = {
    "fist": (0x00, 0x72, 0xB2),
    "palm": (0xE6, 0x9F, 0x00),
    "one": (0x00, 0x9E, 0x73),
    "two_up": (0xCC, 0x79, 0xA7),
    "three": (0xD5, 0x5E, 0x00),
}
FONT_BASE_PX_AT_720 = 16
BACKGROUND_RGB = (24, 24, 24)
HUD_BG_RGB = (0, 0, 0)
HUD_FG_RGB = (235, 235, 235)
LABEL_GAP_PX = 2

# 字体候选（按序尝试；记录实际使用者与 SHA，仍在缺失时退回内置位图字体）
FONT_CANDIDATES: tuple[str, ...] = (
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Program Files/Git/mingw64/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


class RenderUnavailableError(RuntimeError):
    """渲染依赖（Pillow）不可用：调用方必须显式记录 NOT_RUN，不得静默产出空图。"""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(path.read_bytes())


def font_size_px(canvas_height: int) -> int:
    """UR-3：基准 1280×720 用 16 px，其他画布按 `round_half_up(16 × h / 720)`。"""
    return R.round_half_up(FONT_BASE_PX_AT_720 * int(canvas_height) / 720)


def safe_area_px(canvas_height: int) -> int:
    """安全区：`SAFE_AREA_PX_1080P` 按输出高度相对缩放（与 S5-B 渲染同口径）。"""
    return max(1, R.round_half_up(R.SAFE_AREA_PX_1080P * int(canvas_height) / 1080))


def load_font(size: int) -> tuple[Any, dict[str, Any]]:
    """加载可缩放字体；返回 (font, info)。info 须写入清单，供复核确定性来源。"""
    if not PIL_AVAILABLE:
        raise RenderUnavailableError(f"Pillow 不可用：{PIL_IMPORT_ERROR}")
    for candidate in FONT_CANDIDATES:
        path = pathlib.Path(candidate)
        if path.is_file():
            return (ImageFont.truetype(str(path), size),
                    {"font_id": path.name, "font_path": str(path), "font_sha256": sha256_file(path),
                     "font_size_px": int(size), "scaled": True})
    font = ImageFont.load_default()
    return font, {"font_id": "PIL_default_bitmap", "font_path": None, "font_sha256": None,
                  "font_size_px": None, "scaled": False,
                  "note": "未找到可缩放字体，退回内置位图字体；本渲染不满足 UR-3 字号规格"}


def _text_box(draw: Any, text: str, font: Any) -> tuple[int, int, int, int]:
    """返回墨迹盒 (width, height, x0, y0)：绘制时用 (x - x0, y - y0) 使墨迹左上角正落在锚点。"""
    box = draw.textbbox((0, 0), text, font=font)
    return int(box[2] - box[0]), int(box[3] - box[1]), int(box[0]), int(box[1])


def label_anchor(box_px: Mapping[str, int], text_width: int, text_height: int, *,
                 canvas_width: int, canvas_height: int, safe: int) -> tuple[int, int, str]:
    """标签锚点（冻结规则）：框左上外侧 → 越界翻转到框内左上 → 仍越界则钳入安全区。"""
    x1, y1 = int(box_px["x1"]), int(box_px["y1"])
    x2 = int(box_px["x2"])
    placement = "outside_top_left"
    x, y = x1, y1 - text_height - LABEL_GAP_PX
    if y < safe:                                     # 上方越界 ⇒ 翻转到框内左上
        placement = "inside_top_left"
        y = y1 + LABEL_GAP_PX
    if y + text_height > canvas_height - safe:       # 仍越界 ⇒ 钳入下安全边
        placement = f"{placement}+clamped_bottom"
        y = max(safe, canvas_height - safe - text_height)
    max_x = max(safe, canvas_width - safe - text_width)
    if x < safe or x > max_x or x2 > canvas_width - safe:
        if x != min(max(x, safe), max_x):
            placement = f"{placement}+clamped_x"
        x = min(max(x, safe), max_x)
    return int(x), int(y), placement


def render_frame(decision: Mapping[str, Any], *, canvas_width: int, canvas_height: int,
                 background: Any = None, hud: Mapping[str, Any] | None = None,
                 font: Any = None, draw_hud: bool = True, draw_labels: bool = True) -> tuple[Any, dict[str, Any]]:
    """把一帧决策栅格化；返回 (PIL.Image, stats)。

    `decision` 即 `DisplayPipeline.commit_frame()["event"]`：只读消费 `box_px`/`state`/`stale_effective`；
    边框像素集一律取自 `R.border_pixel_sets`，本模块不重算几何。
    `draw_labels=False` 用于**像素级精确断言**（只画边框，便于与参考像素集逐点比对）。
    """
    if not PIL_AVAILABLE:
        raise RenderUnavailableError(f"Pillow 不可用：{PIL_IMPORT_ERROR}")
    width, height = int(canvas_width), int(canvas_height)
    if background is not None:
        if (background.width, background.height) != (width, height):
            raise ValueError(f"背景尺寸 {background.size} 与画布 {(width, height)} 不一致")
        image = background.copy()
        background_used = "provided"
    else:
        image = Image.new("RGB", (width, height), BACKGROUND_RGB)
        background_used = "uniform_rgb"
    draw = ImageDraw.Draw(image)

    stats: dict[str, Any] = {"background": background_used, "boxes_drawn": 0, "border_pixels_drawn": 0,
                             "labels_drawn": 0, "label_placements": {}, "classes_drawn": [],
                             "hud_lines_drawn": 0, "zero_area_dropped": int(decision.get("zero_area_dropped", 0)),
                             "state": decision.get("state"), "drawn": bool(decision.get("drawn")),
                             "stale_effective": bool(decision.get("stale_effective"))}
    safe = safe_area_px(height)
    if font is None:
        font, stats["font"] = load_font(font_size_px(height))
    else:
        stats["font"] = {"font_id": "caller_provided", "scaled": None}

    for box in decision.get("box_px") or []:
        px = box["px"]
        color = CLASS_COLORS_RGB.get(str(box.get("class_name")), (255, 255, 255))
        pixels = R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]), int(px["y2"]),
                                     R.DISPLAY_LINE_WIDTH_PX, width, height)
        for (x, y) in pixels:
            image.putpixel((x, y), color)
        stats["boxes_drawn"] += 1
        stats["border_pixels_drawn"] += len(pixels)
        stats["classes_drawn"].append(str(box.get("class_name")))

        text = f"{str(box.get('class_name', '')).upper()} {float(box['score']):.2f}"
        if not draw_labels:
            continue
        text_w, text_h, ink_x0, ink_y0 = _text_box(draw, text, font)
        lx, ly, placement = label_anchor(px, text_w, text_h, canvas_width=width,
                                         canvas_height=height, safe=safe)
        draw.text((lx - ink_x0, ly - ink_y0), text, font=font, fill=color)
        stats["labels_drawn"] += 1
        stats["label_placements"][placement] = stats["label_placements"].get(placement, 0) + 1

    if draw_hud and hud:
        lines = [f"{key}={('NA' if hud.get(key) == 'UNAVAILABLE' else hud.get(key))}" for key in sorted(hud)]
        if lines:
            widths = [_text_box(draw, line, font)[0] for line in lines]
            line_h = max(1, _text_box(draw, "Wg", font)[1]) + 2
            pad = 2
            panel_w = min(width, max(widths) + 2 * pad) if widths else 0
            panel_h = min(height, line_h * len(lines) + 2 * pad)
            draw.rectangle([0, 0, panel_w, panel_h], fill=HUD_BG_RGB)
            for index, line in enumerate(lines):
                _, _, hud_x0, hud_y0 = _text_box(draw, line, font)
                draw.text((pad - hud_x0, pad + index * line_h - hud_y0), line, font=font, fill=HUD_FG_RGB)
            stats["hud_lines_drawn"] = len(lines)
            stats["hud_panel_px"] = {"x1": 0, "y1": 0, "x2": int(panel_w), "y2": int(panel_h)}
    return image, stats


def png_bytes(image: Any, *, optimize: bool = True) -> bytes:
    import io

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=optimize)
    return buffer.getvalue()


def render_to_png(path: pathlib.Path, decision: Mapping[str, Any], *, canvas_width: int,
                  canvas_height: int, background: Any = None, hud: Mapping[str, Any] | None = None,
                  font: Any = None) -> dict[str, Any]:
    """栅格化并落盘 PNG；返回 stats（含 PNG SHA256 与字节数）。"""
    image, stats = render_frame(decision, canvas_width=canvas_width, canvas_height=canvas_height,
                                background=background, hud=hud, font=font)
    payload = png_bytes(image)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    stats["png_path"] = str(path)
    stats["png_sha256"] = sha256_bytes(payload)
    stats["png_bytes"] = len(payload)
    return stats