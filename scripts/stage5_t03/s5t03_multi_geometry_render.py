#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 多几何渲染验证：把同一组归一化框**在不同画布/分辨率**上渲染并**逐像素**对拍冻结参考。

覆盖（离线、合成、不接板卡）
============================
| 几何 id | 源分辨率 | 画布 | 映射函数（冻结参考） |
|---|---|---|---|
| `landscape_1280x720` | 1280×720 | 1280×720 | `R.original_norm_to_display_px`（fit=exact） |
| `portrait_720x1280` | 720×1280 | 720×1280 | 同上（非方形/竖屏画布） |
| `oddw_683x384` | 683×384 | 683×384 | 同上（奇数宽源；补边 91/92 非对称） |
| `canvas_683x384_k2_1920x1080` | 683×384 | 1920×1080 | `R.canvas_fit` + `R.original_norm_to_canvas_px`（整数倍 k=2 居中，不拉伸） |

判定
====
1. **逐像素**：只画边框（`draw_labels=False`/`draw_hud=False`）时，非背景像素集合必须**恰好等于**
   `R.border_pixel_sets(...)` 的并集——线宽/取整/钳位全部由冻结参考决定，禁止第二套几何；
2. **几何数值**：`R.letterbox_geometry(683, 384)` = 416×233 / offset (0,91) / 下补边 92 / `asymmetric_padding=true`；
   `R.canvas_fit(683, 384, 1920, 1080)` = k=2 / 1366×768 / offset (277,156)；
3. 画布-fit 路径**必须**用 `original_norm_to_canvas_px`（用 exact 映射会得到不同像素 ⇒ 有用例判别）。

诚实边界
========
- 输入仍是**合成**归一化坐标；本模块只验证**显示层几何与绘制**，不验证推理/采集。
- 画布 ≠ 源分辨率时属**画布适配**场景（整数倍不拉伸），不代表板级 HDMI 时序支持该分辨率。
- **真实回放接入 / 板上动态映射 / 摄像头路径 = NOT_RUN**；`G0/G1/G3/G4/G5` 均未通过。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_display_pipeline as P  # noqa: E402
import scripts.stage5_t03.s5t03_dynamic_stream as S  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402

SCHEMA = "gestureforge_s5t03_multi_geometry_render_v1"
INPUT_SCOPE_LABEL = "synthetic_replay"
STATUS_LABEL = "PRELIMINARY"
NOT_RUN = [
    "真实回放接入（无阶段4 冻结回放结果包）",
    "板上动态映射与绘制（本轮不接板卡）",
    "板级 HDMI 时序对非 1280×720 分辨率的支持（未做板上验证）",
    "摄像头真实采集路径",
    "T5-10 板上回归",
]

GEOMETRIES: tuple[dict[str, Any], ...] = (
    {"id": "landscape_1280x720", "source": [1280, 720], "canvas": [1280, 720], "mode": "pipeline_exact"},
    {"id": "portrait_720x1280", "source": [720, 1280], "canvas": [720, 1280], "mode": "pipeline_exact"},
    {"id": "oddw_683x384", "source": [683, 384], "canvas": [683, 384], "mode": "pipeline_exact"},
    {"id": "canvas_683x384_k2_1920x1080", "source": [683, 384], "canvas": [1920, 1080],
     "mode": "canvas_fit_render"},
)


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def load_params() -> dict[str, Any]:
    return json.loads(P.default_params_path().read_text(encoding="utf-8"))


def _decision_from_boxes(boxes_px: list[dict[str, Any]], canvas: tuple[int, int]) -> dict[str, Any]:
    """把已映射的像素框打包成 `display` 决策形状，供 `RD.render_to_png` 复用（不改渲染器）。"""
    return {"drawn": bool(boxes_px), "boxes": len(boxes_px), "zero_area_dropped": 0, "state": "OK",
            "stale_effective": False, "stale_reason": R.STALE_REASON_NONE, "skip_reason": "",
            "box_px": boxes_px}


def render_geometry(geometry: dict[str, Any], *, seed: int, params: dict[str, Any],
                    out_dir: pathlib.Path, detections: list[dict[str, Any]]) -> dict[str, Any]:
    canvas_w, canvas_h = (int(v) for v in geometry["canvas"])
    canvas = (canvas_w, canvas_h)
    width, height = canvas
    keyframes = out_dir / "keyframes"
    keyframes.mkdir(parents=True, exist_ok=True)
    background_rgb = (9, 9, 9)
    background = RD.Image.new("RGB", canvas, background_rgb) if RD.PIL_AVAILABLE else None
    font, font_info = RD.load_font(RD.font_size_px(height)) if RD.PIL_AVAILABLE else (None, {})
    item: dict[str, Any] = {"id": geometry["id"], "source": geometry["source"], "canvas": [width, height],
                            "mode": geometry["mode"], "boxes": [], "assertions": {}, "keyframes": {}}

    if geometry["mode"] == "pipeline_exact":
        pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height,
                                     input_scope_label=INPUT_SCOPE_LABEL, params=params)
        record = S.make_record(session_id=11, frame_id=0, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000, result_time_ns=1_001_000_000,
                               inference_time_ns=900_000, state="OK", detections=detections)
        pipeline.submit_result(record)
        committed = pipeline.commit_frame(0, 1_100_000_000)
        event = committed["event"]
        boxes_px = [{"class_id": b["class_id"], "class_name": b["class_name"], "score": b["score"],
                     "px": dict(b["px"]), "border_pixels": int(b["border_pixels"])}
                    for b in event["box_px"]]
        item["mapping_function"] = "R.original_norm_to_display_px (fit=exact)"
        item["hud"] = dict(committed["hud"])
        decision = event
    else:
        fit = R.canvas_fit(int(geometry["source"][0]), int(geometry["source"][1]), width, height)
        boxes_px = []
        for detection in detections:
            px = R.original_norm_to_canvas_px(detection["xyxy"], fit)
            border = R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]), int(px["y2"]),
                                         R.DISPLAY_LINE_WIDTH_PX, width, height)
            boxes_px.append({"class_id": detection["class_id"], "class_name": detection["class_name"],
                             "score": detection["score"], "px": px, "border_pixels": len(border)})
        item["mapping_function"] = "R.canvas_fit + R.original_norm_to_canvas_px (整数倍 k 居中)"
        item["fit"] = dict(fit)
        # 对照：同一框若误用 exact 映射，像素应不同（用于判别"用错映射函数"）
        wrong = R.original_norm_to_display_px(detections[0]["xyxy"], width, height)
        item["exact_mapping_would_be"] = dict(wrong)
        item["exact_vs_canvas_fit_differ"] = dict(wrong) != dict(boxes_px[0]["px"])
        # HUD 用管线的 13 字段口径（画布无关字段），保证关键帧可人工抽检
        hud_pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height, params=params)
        item["hud"] = hud_pipeline.hud({"state": "OK", "boxes": len(boxes_px), "age_result_ns": None,
                                        "age_frame_ns": None}, 0)
        decision = _decision_from_boxes(boxes_px, canvas)

    item["boxes"] = boxes_px

    # ── 逐像素断言：只画边框时，渲染像素 == 参考边框像素并集 ──────────────────────
    if RD.PIL_AVAILABLE:
        image, stats = RD.render_frame(decision, canvas_width=width, canvas_height=height,
                                       background=background, hud=None, font=font,
                                       draw_hud=False, draw_labels=False)
        pixels = image.load()
        rendered = {(x, y) for x in range(width) for y in range(height) if pixels[x, y] != background_rgb}
        expected: set[tuple[int, int]] = set()
        for box in boxes_px:
            px = box["px"]
            expected |= set(R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]), int(px["y2"]),
                                                R.DISPLAY_LINE_WIDTH_PX, width, height))
        item["assertions"]["rendered_pixels_equal_reference"] = (rendered == expected)
        item["assertions"]["rendered_pixels"] = len(rendered)
        item["assertions"]["reference_pixels"] = len(expected)
        item["assertions"]["missing_px"] = len(expected - rendered)
        item["assertions"]["extra_px"] = len(rendered - expected)
        item["assertions"]["render_stats"] = stats
        # 关键帧（带标签与 HUD，供人工抽检）
        keyframe = keyframes / f"{geometry['id']}_overlay.png"
        stats_full = RD.render_to_png(keyframe, decision, canvas_width=width, canvas_height=height,
                                      background=background, hud=item["hud"], font=font)
        item["keyframes"]["overlay"] = {"path": keyframe.relative_to(out_dir).as_posix(),
                                        "sha256": stats_full["png_sha256"], "bytes": stats_full["png_bytes"]}
        keyframe_border = keyframes / f"{geometry['id']}_border_only.png"
        stats_border = RD.render_to_png(keyframe_border, decision, canvas_width=width,
                                        canvas_height=height, background=background, hud=None,
                                        font=font)
        item["keyframes"]["border_only"] = {"path": keyframe_border.relative_to(out_dir).as_posix(),
                                            "sha256": stats_border["png_sha256"]}
        item["font"] = font_info
    else:
        item["assertions"]["render_not_run"] = "Pillow 不可用"
    return item


def build_detections() -> list[dict[str, Any]]:
    """一组归一化框（覆盖中心/左上/右下/贴边），用合成流工厂保证字段形态与契约一致。"""
    return [S.make_detection(index) for index in range(3)]


def run(*, out_dir: pathlib.Path, seed: int) -> int:
    console = out_dir / "console"
    console.mkdir(parents=True, exist_ok=True)
    params = load_params()
    detections = build_detections()
    failures: list[str] = []
    geometry_items: list[dict[str, Any]] = []
    for geometry in GEOMETRIES:
        item = render_geometry(geometry, seed=seed, params=params, out_dir=out_dir, detections=detections)
        geometry_items.append(item)
        if item["assertions"].get("rendered_pixels_equal_reference") is not True:
            failures.append(f"{geometry['id']}.rendered_pixels_equal_reference")
        if geometry["mode"] == "canvas_fit_render" and not item.get("exact_vs_canvas_fit_differ"):
            failures.append(f"{geometry['id']}.exact_vs_canvas_fit_must_differ")

    # 冻结几何数值断言（含奇数补边与整数倍画布）
    odd = R.letterbox_geometry(683, 384)
    fit = R.canvas_fit(683, 384, 1920, 1080)
    numeric_checks = {
        "oddw_new_416x233": (odd["new_width"], odd["new_height"]) == (416, 233),
        "oddw_offset_0_91": (odd["offset_x"], odd["offset_y"]) == (0, 91),
        "oddw_pad_bottom_92": odd["pad_bottom"] == 92,
        "oddw_asymmetric": odd["asymmetric_padding"] is True,
        "canvas_fit_k2": fit["scale_k"] == 2,
        "canvas_fit_1366x768": (fit["drawn_width"], fit["drawn_height"]) == (1366, 768),
        "canvas_fit_offset_277_156": (fit["offset_x"], fit["offset_y"]) == (277, 156),
    }
    for name, ok in numeric_checks.items():
        if not ok:
            failures.append(f"numeric[{name}]")

    if not RD.PIL_AVAILABLE:
        failures.append(f"render_unavailable:Pillow 不可用（{RD.PIL_IMPORT_ERROR}）")

    results = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "source_commit": git_head(), "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "purpose": "多几何（非方形/竖屏/奇数宽/整数倍画布）在**渲染层**的逐像素对拍；T5-01/T5-07 显示侧补充",
        "geometries": geometry_items,
        "numeric_checks": numeric_checks,
        "odd_padding": {k: odd[k] for k in ("src_width", "src_height", "new_width", "new_height",
                                            "offset_x", "offset_y", "pad_right", "pad_bottom",
                                            "asymmetric_padding")},
        "canvas_fit": dict(fit),
        "render": {"pillow_version": RD.PILLOW_VERSION,
                   "line_width_px": R.DISPLAY_LINE_WIDTH_PX, "rounding_rule": R.ROUNDING_RULE,
                   "font_base_px_at_720": RD.FONT_BASE_PX_AT_720,
                   "class_colors_rgb": {k: "#%02X%02X%02X" % v for k, v in RD.CLASS_COLORS_RGB.items()}},
        "checks": {"failures": failures, "passed": not failures},
        "limitations": ["输入为合成归一化坐标；只验证显示层几何与绘制，不验证采集/推理。",
                        "画布 ≠ 源分辨率时为**画布适配**（整数倍不拉伸）；**不代表**板级 HDMI 时序支持该分辨率。",
                        "画布-fit 路径不含管线决策（用冻结 `R.canvas_fit` + `R.original_norm_to_canvas_px` 直接映射）——已在 §geometries 标注。",
                        "关键帧 PNG 供人工抽检；JSON 为权威。G0/G1/G3/G4/G5 均未通过。"],
        "not_run": NOT_RUN,
    }
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")

    manifest = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": results["generated_utc8"], "source_commit": results["source_commit"],
        "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "goal_reached": "MULTI_GEOMETRY_RENDER_PIXEL_EXACT_VS_FROZEN_REFERENCE",
        "checks": results["checks"], "numeric_checks": numeric_checks,
        "tools": {
            "multi_geometry_render": {"path": "scripts/stage5_t03/s5t03_multi_geometry_render.py",
                                      "sha256": sha256_file(pathlib.Path(__file__))},
            "render": {"path": "scripts/stage5_t03/s5t03_render.py",
                       "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_render.py")},
            "pipeline": {"path": "scripts/stage5_t03/s5t03_display_pipeline.py",
                         "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_display_pipeline.py")},
            "dynamic_stream": {"path": "scripts/stage5_t03/s5t03_dynamic_stream.py",
                               "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_dynamic_stream.py")},
            "geometry_reference": {"path": "verification/s5_display_geometry_reference.py",
                                   "sha256": sha256_file(REPO_ROOT / "verification/s5_display_geometry_reference.py"),
                                   "contract_id": R.CONTRACT_ID},
            "params": {"path": P.default_params_path().relative_to(REPO_ROOT).as_posix(),
                       "sha256": sha256_file(P.default_params_path())},
        },
        "files": [{"path": p.relative_to(out_dir).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                  for p in sorted(x for x in out_dir.rglob("*") if x.is_file() and x.name != "manifest.json")],
        "limitations": results["limitations"], "not_run": NOT_RUN,
        "scope_statement": "本清单只证明多几何渲染与像素级绑定；不代表接口语义正确、独立审查通过或 G0/G4/G5。",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    (console / "run.txt").write_text(
        f"geometries={len(geometry_items)} failures={failures} pillow={RD.PILLOW_VERSION}\n", encoding="utf-8")
    return 0 if not failures else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 多几何渲染验证（离线；不接板卡）")
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    params = load_params()
    seed = args.seed or int(params["newly_frozen_for_skeleton_only"]["seed"])
    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        code = run(out_dir=out_dir, seed=seed)
    except Exception as exc:
        (out_dir / "console").mkdir(parents=True, exist_ok=True)
        (out_dir / "console" / "failure.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"[multigeom] FAILED {type(exc).__name__}: {exc}")
        return 1
    print(f"[multigeom] exit={code} out={out_dir}")
    return code


if __name__ == "__main__":
    sys.exit(main())