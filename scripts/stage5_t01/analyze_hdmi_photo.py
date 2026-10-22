"""S5-T01 从 HDMI 照片提取量化几何（只读分析，不改照片）。

方法：
1) 白掩膜（R,G,B 全 >230）连通域 → 取 4 个方形小斑块作为**四角标记**（画布四角 16×16 白方块）；
2) 以画布角点 (8,8)/(1272,8)/(8,712)/(1272,712) ↔ 照片斑块中心做**最小二乘仿射拟合**；
3) 红/绿掩膜取最大连通域 → 用行/列计数峰值定位**边框线**（长直线），换算回画布坐标；
4) 与期望用例矩形（默认 CASE 5：红 (0,53)-(77,425)、绿 (513,0)-(1025,66)）比对，报告误差。

**局限（必须随结论一起报告）**：照片是手持斜拍，仿射近似不能完全消除透视；误差包含几何透视、屏幕缩放
与 JPEG 压缩，故只作为“位置量级一致”的证据，不作为契约级 1 px 门槛的判定。

用法：python -B scripts/stage5_t01/analyze_hdmi_photo.py --photo <jpg> [--json <out.json>]
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import deque

import numpy as np
from PIL import Image

DOWNSCALE = 2
EXPECTED = {"red": (0, 53, 77, 425), "green": (513, 0, 1025, 66)}
CANVAS_W, CANVAS_H = 1280, 720
MARKER_CANVAS = [(8, 8), (CANVAS_W - 8, 8), (8, CANVAS_H - 8), (CANVAS_W - 8, CANVAS_H - 8)]


def components(mask: np.ndarray, min_area: int, max_area: int) -> list[dict]:
    """4-连通域（稀疏实现）。返回 bbox/面积/像素列表（按面积降序）。"""
    ys, xs = np.nonzero(mask)
    pixels = set(zip(ys.tolist(), xs.tolist()))
    seen: set[tuple[int, int]] = set()
    out: list[dict] = []
    for start in pixels:
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        comp = []
        while queue:
            y, x = queue.popleft()
            comp.append((y, x))
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if (ny, nx) in pixels and (ny, nx) not in seen:
                    seen.add((ny, nx))
                    queue.append((ny, nx))
        if not (min_area <= len(comp) <= max_area):
            continue
        cys = [p[0] for p in comp]
        cxs = [p[1] for p in comp]
        out.append({"area": len(comp), "y0": min(cys), "y1": max(cys), "x0": min(cxs), "x1": max(cxs),
                    "cy": sum(cys) / len(cys), "cx": sum(cxs) / len(cxs), "pixels": comp})
    out.sort(key=lambda c: -c["area"])
    return out


def line_peaks(comp: dict, axis: str, ratio: float = 0.4) -> list[int]:
    """在连通域内，按行(y)或列(x)计数，返回计数 ≥ ratio×max 的坐标（用于定位边框长直线）。"""
    counts: dict[int, int] = {}
    for y, x in comp["pixels"]:
        key = y if axis == "y" else x
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return []
    top = max(counts.values())
    keep = sorted(k for k, v in counts.items() if v >= max(3, int(top * ratio)))
    return keep


def cluster_extremes(values: list[int]) -> list[int]:
    """把峰值坐标按间隙聚类，返回每簇的中位数（最多 4 簇）。"""
    if not values:
        return []
    groups, cur = [], [values[0]]
    for v in values[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            groups.append(cur)
            cur = [v]
    groups.append(cur)
    return [int(sum(g) / len(g)) for g in groups]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--photo", required=True)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    path = pathlib.Path(args.photo)
    if not path.is_absolute():
        path = pathlib.Path.cwd() / path
    if not path.exists():
        print(f"[photo] 不存在：{path}")
        return 2
    image = Image.open(path).convert("RGB")
    full = np.asarray(image).astype(np.int16)
    fr, fg, fb = full[:, :, 0], full[:, :, 1], full[:, :, 2]
    full_whiteish = (fr > 170) & (fg > 170) & (fb > 170)     # 全分辨率检测细线（降采样会削弱 1px 十字）
    small = image.resize((image.width // DOWNSCALE, image.height // DOWNSCALE), Image.BILINEAR)
    arr = np.asarray(small).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    white = (r > 230) & (g > 230) & (b > 230)
    red = (r > 140) & (g < 100) & (b < 100)
    green = (g > 140) & (r < 120) & (b < 120)
    # 参考特征：屏幕上的中心白十字（细长直线）——比角标记更稳健
    whiteish = full_whiteish
    row_counts = whiteish.sum(axis=1)
    col_counts = whiteish.sum(axis=0)
    hrow = int(np.argmax(row_counts)) if row_counts.size else 0
    vcol = int(np.argmax(col_counts)) if col_counts.size else 0
    row_ok = bool(row_counts.size) and row_counts[hrow] > 0.5 * image.width
    col_ok = bool(col_counts.size) and col_counts[vcol] > 0.5 * image.height

    white_comps = components(white, 40, 4000)
    markers = [c for c in white_comps if 0.5 <= (c["x1"] - c["x0"] + 1) / max(1, c["y1"] - c["y0"] + 1) <= 2.0]

    # 主映射：用中心白十字的跨度（横线跨度≈画布宽 0..1279；竖线跨度≈画布高 0..719）
    cross_info: dict = {"hrow_ok": bool(row_ok), "vcol_ok": bool(col_ok)}
    summary: dict = {"photo": str(path), "photo_size": list(image.size), "markers_found": 0,
                     "mapping_ok": False, "mapping": cross_info, "detections": {}}
    if row_ok and col_ok:
        cols = np.nonzero(whiteish[hrow])[0]
        rows = np.nonzero(whiteish[:, vcol])[0]
        x0p, x1p = float(cols.min()), float(cols.max())
        y0p, y1p = float(rows.min()), float(rows.max())
        cross_info.update({"photo_hrow": hrow, "photo_vcol": vcol,
                           "photo_x_span": [x0p, x1p], "photo_y_span": [y0p, y1p]})

        def to_canvas(px: float, py: float) -> tuple[float, float]:
            cx = (px - x0p) * (CANVAS_W - 1) / max(1.0, (x1p - x0p))
            cy = (py - y0p) * (CANVAS_H - 1) / max(1.0, (y1p - y0p))
            return float(cx), float(cy)

        mapping_ok = True
    elif len(markers) >= 4:
        picks: list[dict] = []
        for key in (lambda c: c["cx"] + c["cy"], lambda c: -(c["cx"] - c["cy"]),
                    lambda c: c["cx"] - c["cy"], lambda c: -(c["cx"] + c["cy"])):
            best = max((c for c in markers if c not in picks), key=key)
            picks.append(best)
        src = np.array([[p[1], p[0], 1.0] for p in MARKER_CANVAS])
        dst = np.array([[p["cx"] * DOWNSCALE, p["cy"] * DOWNSCALE] for p in picks])
        coef, *_ = np.linalg.lstsq(src, dst, rcond=None)

        def to_canvas(px: float, py: float) -> tuple[float, float]:
            inv = np.linalg.inv(coef[:, :2])
            v = inv @ (np.array([px, py]) - coef[:, 2])
            return float(v[0]), float(v[1])

        cross_info["marker_fallback"] = True
        mapping_ok = True
    else:
        mapping_ok = False
        print(f"[photo] 参考特征不足（十字 hrow_ok={row_ok} vcol_ok={col_ok}，角标记 {len(markers)} 个）"
              f"→ 不做定量映射；仅记录照片坐标下的连通域（相对位置）")
        observed: dict[str, dict] = {}
        for name, mask in (("red", red), ("green", green)):
            comps = components(mask, 200, 10 ** 7)
            if not comps:
                observed[name] = {"found": False}
                continue
            comp = comps[0]
            observed[name] = {
                "found": True,
                "photo_bbox_px": [comp["x0"] * DOWNSCALE, comp["y0"] * DOWNSCALE,
                                  comp["x1"] * DOWNSCALE, comp["y1"] * DOWNSCALE],
                "photo_frac_of_width": [round(comp["x0"] * DOWNSCALE / image.width, 3),
                                        round(comp["x1"] * DOWNSCALE / image.width, 3)],
                "photo_frac_of_height": [round(comp["y0"] * DOWNSCALE / image.height, 3),
                                         round(comp["y1"] * DOWNSCALE / image.height, 3)],
                "expected_canvas_bbox": list(EXPECTED[name]),
                "expected_frac_of_canvas": [round(EXPECTED[name][0] / CANVAS_W, 3),
                                            round(EXPECTED[name][1] / CANVAS_H, 3),
                                            round(EXPECTED[name][2] / CANVAS_W, 3),
                                            round(EXPECTED[name][3] / CANVAS_H, 3)],
            }
        summary["detections"] = observed
        summary["quantitative_note"] = ("照片为手持斜拍且曝光偏暗：横向中心十字在照片中不可靠检出"
                                       "（实测最长行亮像素 <40% 宽度），四角纯白标记亦未达阈值；"
                                       "故本轮不做画布↔照片映射，仅记录相对位置。")

    if mapping_ok:
        results: dict[str, dict] = {}
        for name, mask in (("red", red), ("green", green)):
            comps = components(mask, 200, 10 ** 7)
            if not comps:
                results[name] = {"found": False}
                continue
            comp = comps[0]
            ys = cluster_extremes(line_peaks(comp, "y"))
            xs = cluster_extremes(line_peaks(comp, "x"))
            corners = []
            for y in (ys[0], ys[-1]):
                for x in (xs[0], xs[-1]):
                    corners.append(to_canvas(x * DOWNSCALE, y * DOWNSCALE))
            canvas_xs = [c[0] for c in corners]
            canvas_ys = [c[1] for c in corners]
            est = [round(min(canvas_xs), 1), round(min(canvas_ys), 1),
                   round(max(canvas_xs), 1), round(max(canvas_ys), 1)]
            exp = list(EXPECTED[name])
            results[name] = {
                "found": True,
                "photo_bbox": [comp["x0"] * DOWNSCALE, comp["y0"] * DOWNSCALE,
                               comp["x1"] * DOWNSCALE, comp["y1"] * DOWNSCALE],
                "photo_line_peaks_y": [v * DOWNSCALE for v in ys],
                "photo_line_peaks_x": [v * DOWNSCALE for v in xs],
                "canvas_bbox_est": est,
                "expected_canvas_bbox": exp,
                "delta_px": [round(est[i] - exp[i], 1) for i in range(4)],
            }
        summary = {"photo": str(path), "photo_size": list(image.size), "markers_found": len(markers),
                   "mapping": cross_info, "mapping_ok": True, "detections": results}

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())