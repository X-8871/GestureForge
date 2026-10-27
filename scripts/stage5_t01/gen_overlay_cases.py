"""S5-T01 P1 叠框用例生成器（宿主端，离线）：把注入用例算成**像素矩形 + 笔画字体数据**，产出 C 头文件。

设计要点（避免板上出现第二套几何）：
- 框的像素矩形由 `verification/s5_display_geometry_reference.py`（S5A-G0-v2 冻结实现）计算：
  网络归一化 → 反补边/反缩放 → 原图归一化 → 画布像素（round-half-up）→ 边框像素集合。
- C 侧只把预计算的矩形/标签画进送显缓冲，**不含任何逆映射/取整逻辑**。
- 文本用紧凑**笔画字体**（线段集合），由本脚本生成 C 数组；可用 `--selftest` 渲染 ASCII 图形核对可读性。

用法：
  python -B scripts/stage5_t01/gen_overlay_cases.py --emit-c tmp/5/S5-T01/p1_app/s5_overlay_cases.h
  python -B scripts/stage5_t01/gen_overlay_cases.py --selftest
"""

from __future__ import annotations

import argparse
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
import verification.s5_display_geometry_reference as R  # noqa: E402

CANVAS_W, CANVAS_H = 1280, 720          # HDMI 实测模式（HSIZE 0xF00 = 1280×3）
SOURCE_W, SOURCE_H = 1280, 720          # 阶段3 采集/源几何（非方形）
LINE_W = R.DISPLAY_LINE_WIDTH_PX        # 2
LABEL_SCALE = 2                         # 笔画字体放大倍数
STALE_AGE_LIMIT_NS = R.STALE_AGE_LIMIT_NS

# ── 紧凑笔画字体：坐标为 5×7 网格（x:0..4, y:0..6），每字形若干线段 ─────────────────
FONT: dict[str, list[tuple[int, int, int, int]]] = {
    " ": [],
    ".": [(2, 6, 2, 6)],
    "_": [(0, 6, 4, 6)],
    "/": [(4, 0, 0, 6)],
    "-": [(0, 3, 4, 3)],
    "=": [(0, 2, 4, 2), (0, 4, 4, 4)],
    "0": [(0, 0, 0, 6), (0, 0, 4, 0), (4, 0, 4, 6), (0, 6, 4, 6), (0, 0, 4, 6)],
    "1": [(1, 1, 2, 0), (2, 0, 2, 6)],
    "2": [(0, 0, 4, 0), (4, 0, 4, 3), (4, 3, 0, 3), (0, 3, 0, 6), (0, 6, 4, 6)],
    "3": [(0, 0, 4, 0), (4, 0, 4, 6), (0, 6, 4, 6), (4, 3, 0, 3)],
    "4": [(0, 0, 0, 3), (0, 3, 4, 3), (4, 0, 4, 6)],
    "5": [(4, 0, 0, 0), (0, 0, 0, 3), (0, 3, 4, 3), (4, 3, 4, 6), (4, 6, 0, 6)],
    "6": [(4, 0, 0, 0), (0, 0, 0, 6), (0, 6, 4, 6), (4, 6, 4, 3), (4, 3, 0, 3)],
    "7": [(0, 0, 4, 0), (4, 0, 2, 6)],
    "8": [(0, 0, 4, 0), (4, 0, 4, 6), (0, 6, 4, 6), (0, 0, 0, 6), (0, 3, 4, 3)],
    "9": [(4, 3, 0, 3), (0, 3, 0, 0), (0, 0, 4, 0), (4, 0, 4, 6), (4, 6, 0, 6)],
    "A": [(0, 6, 2, 0), (2, 0, 4, 6), (0, 4, 4, 4)],
    "B": [(0, 0, 0, 6), (0, 0, 3, 0), (3, 0, 4, 1), (4, 1, 4, 2), (4, 2, 3, 3), (0, 3, 3, 3),
          (3, 3, 4, 4), (4, 4, 4, 5), (4, 5, 3, 6), (0, 6, 3, 6)],
    "C": [(4, 0, 0, 0), (0, 0, 0, 6), (0, 6, 4, 6)],
    "D": [(0, 0, 0, 6), (0, 0, 3, 0), (3, 0, 4, 2), (4, 2, 4, 4), (4, 4, 3, 6), (3, 6, 0, 6)],
    "G": [(4, 0, 0, 0), (0, 0, 0, 6), (0, 6, 4, 6), (4, 6, 4, 3), (4, 3, 2, 3)],
    "Y": [(0, 0, 2, 3), (4, 0, 2, 3), (2, 3, 2, 6)],
    "E": [(4, 0, 0, 0), (0, 0, 0, 6), (0, 6, 4, 6), (0, 3, 3, 3)],
    "F": [(4, 0, 0, 0), (0, 0, 0, 6), (0, 3, 3, 3)],
    "H": [(0, 0, 0, 6), (4, 0, 4, 6), (0, 3, 4, 3)],
    "I": [(1, 0, 3, 0), (2, 0, 2, 6), (1, 6, 3, 6)],
    "L": [(0, 0, 0, 6), (0, 6, 4, 6)],
    "M": [(0, 6, 0, 0), (0, 0, 2, 3), (2, 3, 4, 0), (4, 0, 4, 6)],
    "N": [(0, 6, 0, 0), (0, 0, 4, 6), (4, 6, 4, 0)],
    "O": [(0, 0, 4, 0), (4, 0, 4, 6), (0, 6, 4, 6), (0, 0, 0, 6)],
    "P": [(0, 6, 0, 0), (0, 0, 4, 0), (4, 0, 4, 3), (4, 3, 0, 3)],
    "R": [(0, 6, 0, 0), (0, 0, 4, 0), (4, 0, 4, 3), (4, 3, 0, 3), (0, 3, 4, 6)],
    "S": [(4, 0, 0, 0), (0, 0, 0, 3), (0, 3, 4, 3), (4, 3, 4, 6), (4, 6, 0, 6)],
    "T": [(0, 0, 4, 0), (2, 0, 2, 6)],
    "U": [(0, 0, 0, 6), (0, 6, 4, 6), (4, 6, 4, 0)],
    "W": [(0, 0, 0, 6), (0, 6, 2, 3), (2, 3, 4, 6), (4, 6, 4, 0)],
    "X": [(0, 0, 4, 6), (4, 0, 0, 6)],
    "Z": [(0, 0, 4, 0), (4, 0, 0, 6), (0, 6, 4, 6)],
}
GLYPH_W, GLYPH_H, GLYPH_ADV = 5, 7, 6

# 有效区间（由冻结逆映射推得，写进用例以避免无意落在补边带）：
#   x: u ∈ [0, 415/416]（off_x=0、w_scale=(1279)/415）；y: v ∈ [91/416, 324/416]（off_y=91、new_h=234）
U_MAX = 415 / 416
V_MIN = 91 / 416
V_MAX = 324 / 416

# ── 用例：框用**网络归一化坐标**（由冻结实现逆映射），文本用 ASCII ─────────────────
CASES = [
    {"id": 1, "name": "C1 SINGLE FIST 0.83", "class_name": "FIST", "score_text": "0.83", "stale": False,
     "boxes": [{"cls": 0, "score": 0.83, "uv": (0.40, 0.35, 0.60, 0.70)}]},
    {"id": 2, "name": "C2 CORNERS INSIDE", "class_name": "PALM", "score_text": "0.55", "stale": False,
     "boxes": [{"cls": 1, "score": 0.55, "uv": (0.00, V_MIN, 0.12, 0.35)},
               {"cls": 2, "score": 0.51, "uv": (0.88, V_MIN, U_MAX, 0.35)},
               {"cls": 3, "score": 0.47, "uv": (0.00, 0.65, 0.12, V_MAX)},
               {"cls": 4, "score": 0.44, "uv": (0.88, 0.65, U_MAX, V_MAX)}]},
    {"id": 3, "name": "C3 MULTI 15", "class_name": "ONE", "score_text": "0.42", "stale": False,
     "boxes": [{"cls": i % 5, "score": 0.30 + 0.01 * i,
                "uv": (0.01 + 0.17 * (i % 6), V_MIN + 0.17 * (i // 6),
                       0.01 + 0.17 * (i % 6) + 0.12, V_MIN + 0.17 * (i // 6) + 0.13)}
               for i in range(15)]},
    {"id": 4, "name": "C4 ZERO BOX", "class_name": "NONE", "score_text": "0.00", "stale": False, "boxes": []},
    {"id": 5, "name": "C5 EDGE CLIP PLUS PAD", "class_name": "TWO_UP", "score_text": "0.66", "stale": False,
     "boxes": [{"cls": 0, "score": 0.66, "uv": (0.00, 0.26, 0.06, 0.55)},          # 左边缘贴边
               {"cls": 1, "score": 0.62, "uv": (0.40, V_MIN, 0.80, 0.27)},          # 上边缘贴边
               {"cls": 2, "score": 0.60, "uv": (0.45, 0.02, 0.60, 0.10)}]},         # 落在上补边带 => 期望丢弃
    {"id": 6, "name": "C6 STALE CLEAR", "class_name": "THREE", "score_text": "0.58", "stale": True,
     "boxes": [{"cls": 3, "score": 0.58, "uv": (0.25, 0.35, 0.45, 0.65)}]},
]
CLASS_ORDER = R.CLASS_ORDER


def label_for(box: dict) -> str:
    return f"{CLASS_ORDER[box['cls']].upper()} {box['score']:.2f}"


def compute_case(case: dict, geom: dict) -> dict:
    """用冻结实现把网络归一化框算成画布像素矩形与标签位置。"""
    clipped_out, dropped = [], []
    for box in case["boxes"]:
        orig = R.network_norm_to_original_norm(box["uv"], geom)          # 反补边 + 反缩放（float64）
        clip = R.clip_unit_box(orig)
        entry = {"cls": box["cls"], "score": box["score"], "xyxy": orig, "clipped": clip["clipped"]}
        if clip["zero_area"]:
            entry["zero_area"] = True
            dropped.append(entry)
            continue
        px = R.original_norm_to_display_px(clip["xyxy"], CANVAS_W, CANVAS_H)
        pixels = R.border_pixel_sets(px["x1"], px["y1"], px["x2"], px["y2"], LINE_W, CANVAS_W, CANVAS_H)
        entry.update({"px": px, "border_pixels": len(pixels), "label": label_for(box)})
        clipped_out.append(entry)
    drawn = [] if case["stale"] else clipped_out
    return {"id": case["id"], "name": case["name"], "class_name": case["class_name"],
            "score_text": case["score_text"], "stale": case["stale"],
            "drawn": drawn, "dropped_zero_area": dropped,
            "hud": [f"CASE {case['id']}", f"BOXES {len(drawn)}", "SEM B",
                    ("STALE" if case["stale"] else "FRESH")]}


def emit_c(cases: list[dict], path: pathlib.Path) -> None:
    extra_words = ["CASE", "BOXES", "SEM B", "FRESH", "STALE", "FPS", "MS", "COUNT", "NA", "WARM", "STEADY"]
    hud_fields = ["CAPTURE_FPS", "INFERENCE_FPS", "DISPLAY_FPS", "INFERENCE_TIME_NS", "AGE_RESULT_NS",
                  "AGE_FRAME_NS", "FRAME_ID", "BOXES", "STALE_CLEARED", "DROPPED_FRAMES", "TIMEOUTS",
                  "WARMUP_STATE", "DISPLAY_SEMANTICS"]
    chars = sorted({ch for text in extra_words for ch in text}
                   | {ch for name in hud_fields for ch in name}
                   | {ch for meta in cases for text in [meta["name"], *meta["hud"]] for ch in text}
                   | {ch for meta in cases for box in meta["drawn"] for ch in box["label"]})
    lines = ["/* 自动生成（scripts/stage5_t01/gen_overlay_cases.py）：勿手改。",
             " * 几何来自 verification/s5_display_geometry_reference.py（S5A-G0-v2 冻结实现）；",
             " * C 侧默认只绘制预计算的像素矩形与笔画（不做逆映射/取整）；\n"
             " * 另附原图归一化 xyxy（nx1..ny2）供 -DS5_DYNAMIC_MAP=1 的板上动态映射路径使用。 */",
             "#ifndef S5_OVERLAY_CASES_H", "#define S5_OVERLAY_CASES_H", "",
             f"#define S5_CANVAS_W {CANVAS_W}", f"#define S5_CANVAS_H {CANVAS_H}",
             f"#define S5_LINE_W {LINE_W}", f"#define S5_LABEL_SCALE {LABEL_SCALE}",
             f"#define S5_NUM_CASES {len(cases)}",
             f"#define S5_GLYPH_W {GLYPH_W}", f"#define S5_GLYPH_H {GLYPH_H}", f"#define S5_GLYPH_ADV {GLYPH_ADV}",
             f"#define S5_STALE_LIMIT_NS {STALE_AGE_LIMIT_NS}U", "",
             "typedef struct { char ch; unsigned char nseg; signed char seg[12][4]; } s5_glyph_t;",
             "typedef struct { short x1, y1, x2, y2; unsigned char cls; const char *label;",
             "                 float nx1, ny1, nx2, ny2; } s5_box_t;  /* nx1..ny2 = 原图归一化（板上动态映射输入） */",
             "typedef struct { unsigned char id; unsigned char nbox; unsigned char stale;",
             "                 const char *name; const s5_box_t *boxes; const char *hud[4]; } s5_case_t;", "",
             "static const s5_glyph_t S5_GLYPHS[] = {"]
    for ch in chars:
        strokes = FONT.get(ch.upper() if ch.isalpha() else ch, [])
        if ch == " " or not strokes:
            continue
        segs = ",".join("{%d,%d,%d,%d}" % s for s in strokes)
        lines.append("    {'%s', %d, {%s}}," % ("'" if ch == "'" else ch, len(strokes), segs))
    lines += ["};", f"#define S5_GLYPH_COUNT {len([c for c in chars if FONT.get(c.upper() if c.isalpha() else c)])}",
              "", "/* HUD 13 字段名（§5.4；值在板上运行时格式化，缺失值用 NA，不得用 0 伪装） */",
              f"#define S5_HUD_FIELD_COUNT {len(hud_fields)}",
              "static const char *S5_HUD_FIELDS[S5_HUD_FIELD_COUNT] = {"]
    for name in hud_fields:
        lines.append(f'    "{name}",')
    lines += ["};", "", "static const s5_box_t S5_BOXES[] = {"]
    offset = 0
    for case in cases:
        for box in case["drawn"]:
            px = box["px"]
            ny = box["xyxy"]
            lines.append('    {%d, %d, %d, %d, %d, "%s", %.6ff, %.6ff, %.6ff, %.6ff},'
                         % (px["x1"], px["y1"], px["x2"], px["y2"], box["cls"], box["label"],
                            ny[0], ny[1], ny[2], ny[3]))
    lines += ["};", "", "static const s5_case_t S5_CASES[] = {"]
    offset = 0
    for case, meta in zip(CASES, cases):
        hud = ", ".join('"%s"' % t for t in meta["hud"])
        lines.append('    {%d, %d, %d, "%s", &S5_BOXES[%d], {%s}},' % (
            case["id"], len(meta["drawn"]), 1 if case["stale"] else 0, meta["name"], offset, hud))
        offset += len(meta["drawn"])
    lines += ["};", "", "#endif /* S5_OVERLAY_CASES_H */", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[gen] wrote {path} cases={len(cases)} boxes={sum(len(c['drawn']) for c in cases)} glyphs={len(chars)}")


def ascii_render(text: str, scale: int = 1) -> list[str]:
    """把文本用笔画字体渲染成 ASCII 图（自检可读性）。"""
    grid_h, grid_w = GLYPH_H * scale + 2, (GLYPH_ADV * scale) * len(text) + 2
    canvas = [[" "] * grid_w for _ in range(grid_h)]

    def put(x, y):
        if 0 <= y < grid_h and 0 <= x < grid_w:
            canvas[y][x] = "#"

    def line(x1, y1, x2, y2):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for i in range(steps + 1):
            x = x1 + (x2 - x1) * i // steps
            y = y1 + (y2 - y1) * i // steps
            for dy in range(scale):
                for dx in range(scale):
                    put(x + dx, y + dy)

    for index, ch in enumerate(text):
        strokes = FONT.get(ch.upper() if ch.isalpha() else ch, [])
        ox = 1 + index * GLYPH_ADV * scale
        for (x1, y1, x2, y2) in strokes:
            line(ox + x1 * scale, 1 + y1 * scale, ox + x2 * scale, 1 + y2 * scale)
    return ["".join(row) for row in canvas]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-c", default=None)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    geom = R.letterbox_geometry(SOURCE_W, SOURCE_H)
    cases = [compute_case(case, geom) for case in CASES]
    if args.selftest:
        print(f"[selftest] geometry={ {k: geom[k] for k in ('new_width','new_height','offset_x','offset_y')} }")
        for case in cases:
            print(f"[selftest] case {case['id']}: drawn={len(case['drawn'])} dropped_zero={len(case['dropped_zero_area'])} "
                  f"hud={case['hud']}")
            for box in case["drawn"]:
                print(f"    {box['label']:<12} px={box['px']} border_px={box['border_pixels']} clipped={box['clipped']}")
        for text in ("CASE 3", "BOXES 15", "FIST 0.83", "STALE", "TWO_UP"):
            print(f"[selftest] render {text!r}:")
            for row in ascii_render(text, scale=1):
                print("    " + row)
    if args.emit_c:
        emit_c(cases, pathlib.Path(args.emit_c))
    if args.json:
        import json
        print(json.dumps(cases, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())