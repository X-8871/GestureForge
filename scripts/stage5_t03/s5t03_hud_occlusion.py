#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 HUD 遮挡量化：**差分栅格化**精确测量 HUD 面板覆盖了多少**框线像素**。

方法（不假设 HUD 几何，直接用真实渲染器）
==========================================
对同一决策：
1. `A` = 只画边框（`draw_hud=False, draw_labels=False`）的非背景像素集；
2. `B` = 画边框 + HUD（`draw_hud=True, draw_labels=False`）的非背景像素集；
3. **被遮挡框线像素** `occluded = A \\ B`（被 HUD 不透明面板覆盖后不再是框线色）；
4. `H` = 只画 HUD（无框）的非背景像素集（HUD 面板实际占用像素）；
5. 指标：`border_pixels_total=|A|`、`border_pixels_occluded=|occluded|`、`occlusion_ratio=|occluded|/|A|`、
   `hud_pixels=|H|`；并对每个用例给出 `WITHIN_LIMIT / EXCEEDS_LIMIT`。

口径与边界（重要）
==================
- 阈值 `limit=0.10` 是**本仓库离线渲染口径的告警阈值**（参数文件登记，便于审阅），**不是** Wong/阶段7 冻结的验收指标，
  也不代表任何板级指标；改阈值不改语义（只改判定串）。
- HUD 只报告**框线被覆盖**的像素；"标签文字是否被覆盖"不在本模块口径内（标签在 HUD 之前绘制，其位置由 `label_anchor` 决定）。
- 仍为**离线合成**输入；**真实回放接入 / 板上动态映射 / 摄像头 = NOT_RUN**；本模块不接板卡、不联网。
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
import scripts.stage5_t03.s5t03_multi_geometry_render as MG  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402

SCHEMA = "gestureforge_s5t03_hud_occlusion_v1"
INPUT_SCOPE_LABEL = "synthetic_replay"
STATUS_LABEL = "PRELIMINARY"
BACKGROUND_RGB = (9, 9, 9)
DEFAULT_LIMIT = 0.10
NOT_RUN = [
    "真实回放接入（无阶段4 冻结回放结果包）",
    "板上动态映射与绘制（本轮不接板卡）",
    "板级真彩目视下的 HUD 遮挡（须板上窗口）",
    "摄像头真实采集路径",
    "T5-10 板上回归",
]

# 布局：一条远离 HUD 面板（右下，期望 0 遮挡）、一条正落在 HUD 面板下（左上，期望 >0）、一条混合三条
LAYOUTS: tuple[dict[str, Any], ...] = (
    {"id": "far_bottom_right", "expect_zero": True,
     "boxes": [{"xyxy": [0.60, 0.62, 0.92, 0.95], "class_id": 1, "class_name": "one", "score": 0.90}]},
    {"id": "top_left_under_hud", "expect_zero": False,
     "boxes": [{"xyxy": [0.01, 0.01, 0.28, 0.20], "class_id": 0, "class_name": "fist", "score": 0.81}]},
    {"id": "mixed_three", "expect_zero": False,
     "boxes": [{"xyxy": [0.01, 0.02, 0.22, 0.16], "class_id": 3, "class_name": "two_up", "score": 0.77},
               {"xyxy": [0.40, 0.35, 0.62, 0.60], "class_id": 2, "class_name": "three", "score": 0.83},
               {"xyxy": [0.70, 0.72, 0.95, 0.96], "class_id": 4, "class_name": "palm", "score": 0.88}]},
)


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def load_params() -> dict[str, Any]:
    return json.loads(P.default_params_path().read_text(encoding="utf-8"))


def _pixel_set(image: Any) -> set[tuple[int, int]]:
    width, height = image.size
    pixels = image.load()
    return {(x, y) for x in range(width) for y in range(height) if pixels[x, y] != BACKGROUND_RGB}


def _boxes_px_for(geometry: dict[str, Any], layout: dict[str, Any], params: dict[str, Any]) -> tuple[list[dict], dict]:
    """把布局里的框映射到该几何画布像素（exact 用管线；canvas-fit 用冻结映射）。

    注意：检测框必须用 `S.make_detection` 构造（契约字段齐全），再覆盖 `xyxy` 坐标；
    手写字典会被管线按 schema 校验拒收（曾导致 `border_pixels_total=0` 的假通过）。
    """
    width, height = (int(v) for v in geometry["canvas"])
    detections = [S.make_detection(index, box=tuple(float(v) for v in box["xyxy"]),
                                   score=float(box["score"]))
                  for index, box in enumerate(layout["boxes"])]
    if geometry["mode"] == "pipeline_exact":
        pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height,
                                     input_scope_label=INPUT_SCOPE_LABEL, params=params)
        record = S.make_record(session_id=13, frame_id=0, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000, result_time_ns=1_001_000_000,
                               inference_time_ns=900_000, state="OK", detections=detections)
        pipeline.submit_result(record)
        committed = pipeline.commit_frame(0, 1_100_000_000)
        event = committed["event"]
        boxes = [{"class_id": b["class_id"], "class_name": b["class_name"], "score": b["score"],
                  "px": dict(b["px"]), "border_pixels": int(b["border_pixels"])} for b in event["box_px"]]
        if not boxes:
            raise RuntimeError(f"管线未绘制任何框（geometry={geometry['id']} layout={layout['id']}）；"
                               "遮挡量化不能建立在 0 框之上")
        return boxes, dict(committed["hud"])
    fit = R.canvas_fit(int(geometry["source"][0]), int(geometry["source"][1]), width, height)
    boxes = []
    for detection in detections:
        px = R.original_norm_to_canvas_px(detection["xyxy"], fit)
        border = R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]), int(px["y2"]),
                                     R.DISPLAY_LINE_WIDTH_PX, width, height)
        boxes.append({"class_id": detection["class_id"], "class_name": detection["class_name"],
                      "score": detection["score"], "px": px, "border_pixels": len(border)})
    hud_pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height, params=params)
    return boxes, hud_pipeline.hud({"state": "OK", "boxes": len(boxes), "age_result_ns": None,
                                    "age_frame_ns": None}, 0)


def measure(geometry: dict[str, Any], layout: dict[str, Any], *, params: dict[str, Any],
            font: Any, limit: float) -> dict[str, Any]:
    width, height = (int(v) for v in geometry["canvas"])
    boxes, hud = _boxes_px_for(geometry, layout, params)
    decision = MG._decision_from_boxes(boxes, (width, height))
    background = RD.Image.new("RGB", (width, height), BACKGROUND_RGB)
    image_a, stats_a = RD.render_frame(decision, canvas_width=width, canvas_height=height,
                                       background=background, hud=None, font=font,
                                       draw_hud=False, draw_labels=False)
    image_b, _ = RD.render_frame(decision, canvas_width=width, canvas_height=height,
                                 background=background, hud=hud, font=font,
                                 draw_hud=True, draw_labels=False)
    image_h, stats_h = RD.render_frame(MG._decision_from_boxes([], (width, height)),
                                       canvas_width=width, canvas_height=height, background=background,
                                       hud=hud, font=font, draw_hud=True, draw_labels=False)
    border_only = _pixel_set(image_a)
    with_hud_set = _pixel_set(image_b)
    hud_only = _pixel_set(image_h)
    # **正确口径**：逐个框线像素比较"画 HUD 后颜色是否仍是原来的框线色"。
    # 曾用 `A \ B` 是错的：HUD 不透明面板的颜色同样"非背景"，被覆盖的框线像素仍留在 B 里 ⇒ 严重低估遮挡。
    pixels_a = image_a.load()
    pixels_b = image_b.load()
    occluded = {p for p in border_only if pixels_b[p] != pixels_a[p]}
    # 结构交叉核验：HUD 面板是**不透明矩形**，被覆盖的框线像素必须恰好等于"面板矩形内的框线像素"。
    panel = stats_h.get("hud_panel_px") or {"x2": -1, "y2": -1}
    inside_panel = {p for p in border_only if p[0] <= panel["x2"] and p[1] <= panel["y2"]}
    consistent = occluded == inside_panel
    # 信息项（不判据）：`A ∩ HUD 像素集` 在个别像素上会比面板法少（HUD 通道后个别像素回到背景色），
    # 实测 landscape 例为 1470 vs 1473（差 3 px），故仅记录、不用于判定。
    occluded_via_intersection = border_only & hud_only
    visible = border_only - occluded
    total = len(border_only)
    ratio = (len(occluded) / total) if total else 0.0
    verdict = "WITHIN_LIMIT" if ratio <= limit else "EXCEEDS_LIMIT"
    expected_ok = (ratio == 0.0) if layout["expect_zero"] else (len(occluded) > 0)
    return {
        "geometry": geometry["id"], "layout": layout["id"], "canvas": [width, height],
        "boxes": len(boxes), "border_pixels_total": total, "border_pixels_occluded": len(occluded),
        "border_pixels_visible": len(visible), "occlusion_ratio": round(ratio, 6),
        "hud_pixels": len(hud_only), "hud_panel_px": panel,
        "occlusion_method": "per_pixel_color_diff(A vs A+HUD)",
        "panel_method_pixels": len(inside_panel),
        "intersection_method_pixels": len(occluded_via_intersection),
        "methods_consistent": consistent,
        "limit": limit, "verdict": verdict, "expect_zero_occlusion": bool(layout["expect_zero"]),
        "expectation_met": bool(expected_ok and consistent), "render_stats_border_only": stats_a,
        "sample_occluded_px": sorted(occluded)[:8],
    }


def run(*, out_dir: pathlib.Path, limit: float, geometries: tuple[dict[str, Any], ...]) -> int:
    console = out_dir / "console"
    keyframes = out_dir / "keyframes"
    console.mkdir(parents=True, exist_ok=True)
    keyframes.mkdir(parents=True, exist_ok=True)
    params = load_params()
    failures: list[str] = []
    cases: list[dict[str, Any]] = []
    font: Any = None
    font_info: dict[str, Any] = {}
    if not RD.PIL_AVAILABLE:
        # fail-closed：缺渲染依赖时**不做任何测量**（也不抛异常），直接记为失败，
        # 避免"没有渲染却 passed=true"的假通过。
        failures.append(f"render_unavailable:Pillow 不可用 ⇒ 遮挡量化 NOT_RUN（{RD.PIL_IMPORT_ERROR}）")
    for geometry in (() if failures else geometries):
        width, height = (int(v) for v in geometry["canvas"])
        font, font_info = RD.load_font(RD.font_size_px(height)) if RD.PIL_AVAILABLE else (None, {})
        for layout in LAYOUTS:
            case = measure(geometry, layout, params=params, font=font, limit=limit)
            cases.append(case)
            if not case["expectation_met"]:
                failures.append(f"{geometry['id']}/{layout['id']}.expectation")
            if RD.PIL_AVAILABLE and layout["id"] == "top_left_under_hud":
                boxes, hud = _boxes_px_for(geometry, layout, params)
                decision = MG._decision_from_boxes(boxes, (width, height))
                background = RD.Image.new("RGB", (width, height), BACKGROUND_RGB)
                for tag, want_hud in (("nohud", False), ("hud", True)):
                    path = keyframes / f"{geometry['id']}_{layout['id']}_{tag}.png"
                    stats = RD.render_to_png(path, decision, canvas_width=width, canvas_height=height,
                                             background=background, hud=hud if want_hud else None,
                                             font=font)
                    case.setdefault("keyframes", {})[tag] = {
                        "path": path.relative_to(out_dir).as_posix(), "sha256": stats["png_sha256"]}
    if not RD.PIL_AVAILABLE and not any("render_unavailable" in item for item in failures):
        failures.append(f"render_unavailable:Pillow 不可用 ⇒ 遮挡量化 NOT_RUN（{RD.PIL_IMPORT_ERROR}）")

    ratios = [c["occlusion_ratio"] for c in cases]
    results = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "source_commit": git_head(), "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "purpose": "量化 HUD 不透明面板对**框线像素**的遮挡（差分栅格化），供显示侧边界评估",
        "method": "A=仅边框像素集；B=边框+HUD 像素集；occluded=A\\B；HUD 像素=H（无框渲染）；ratio=|occluded|/|A|",
        "limit": {"value": limit, "semantics": "本仓库离线渲染**告警阈值**（非 Wong/阶段7 冻结的验收指标，也不代表板级指标）",
                  "verdict_rule": "ratio <= limit ⇒ WITHIN_LIMIT；否则 EXCEEDS_LIMIT"},
        "geometries": [g["id"] for g in geometries],
        "layouts": [dict(layout) for layout in LAYOUTS],
        "cases": cases,
        "summary": {"cases": len(cases), "max_occlusion_ratio": max(ratios) if ratios else None,
                    "mean_occlusion_ratio": round(sum(ratios) / len(ratios), 6) if ratios else None,
                    "exceeds_limit": sorted({c["geometry"] for c in cases if c["verdict"] == "EXCEEDS_LIMIT"}),
                    "zero_occlusion_cases": sorted({c["layout"] for c in cases if c["occlusion_ratio"] == 0.0})},
        "render": {"pillow_version": RD.PILLOW_VERSION, "font": font_info,
                   "class_colors_rgb": {k: "#%02X%02X%02X" % v for k, v in RD.CLASS_COLORS_RGB.items()},
                   "line_width_px": R.DISPLAY_LINE_WIDTH_PX, "rounding_rule": R.ROUNDING_RULE},
        "checks": {"failures": failures, "passed": not failures},
        "limitations": ["输入为合成归一化坐标；只量化**框线像素**被 HUD 覆盖的比例，不含标签文字覆盖口径。",
                        f"阈值 {limit} 为本仓库离线告警口径，**不是**验收指标；改阈值只改判定串不改语义。",
                        "板级真彩目视下的 HUD 遮挡须板上窗口验证（NOT_RUN）。",
                        "PNG 供人工抽检；JSON 为权威。G0/G1/G3/G4/G5 均未通过。"],
        "not_run": NOT_RUN,
    }
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": results["generated_utc8"], "source_commit": results["source_commit"],
        "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "goal_reached": "HUD_OCCLUSION_QUANTIFIED_DIFFERENTIAL_RASTERIZATION_OFFLINE",
        "limit": results["limit"], "summary": results["summary"], "checks": results["checks"],
        "tools": {
            "hud_occlusion": {"path": "scripts/stage5_t03/s5t03_hud_occlusion.py",
                              "sha256": sha256_file(pathlib.Path(__file__))},
            "render": {"path": "scripts/stage5_t03/s5t03_render.py",
                       "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_render.py")},
            "multi_geometry_render": {"path": "scripts/stage5_t03/s5t03_multi_geometry_render.py",
                                      "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_multi_geometry_render.py")},
            "pipeline": {"path": "scripts/stage5_t03/s5t03_display_pipeline.py",
                         "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_display_pipeline.py")},
            "dynamic_stream": {"path": "scripts/stage5_t03/s5t03_dynamic_stream.py",
                               "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_dynamic_stream.py")},
            "geometry_reference": {"path": "verification/s5_display_geometry_reference.py",
                                   "contract_id": R.CONTRACT_ID,
                                   "sha256": sha256_file(REPO_ROOT / "verification/s5_display_geometry_reference.py")},
            "params": {"path": P.default_params_path().relative_to(REPO_ROOT).as_posix(),
                       "sha256": sha256_file(P.default_params_path())},
        },
        "files": [{"path": p.relative_to(out_dir).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                  for p in sorted(x for x in out_dir.rglob("*") if x.is_file() and x.name != "manifest.json")],
        "limitations": results["limitations"], "not_run": NOT_RUN,
        "scope_statement": "本清单只证明离线遮挡量化与像素级绑定；不代表接口语义正确、独立审查通过或 G0/G4/G5。",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
    (console / "run.txt").write_text(
        f"cases={len(cases)} limit={limit} max_ratio={results['summary']['max_occlusion_ratio']} "
        f"failures={failures}\n", encoding="utf-8", newline="\n")
    return 0 if not failures else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 HUD 遮挡量化（离线；不接板卡）")
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=float, default=DEFAULT_LIMIT)
    parser.add_argument("--geometries", default="landscape,portrait,oddw",
                        help="逗号分隔：landscape,portrait,oddw,canvasfit（默认前三，canvasfit 可选）")
    args = parser.parse_args(argv)
    wanted = {name.strip() for name in args.geometries.split(",") if name.strip()}
    mapping = {"landscape": MG.GEOMETRIES[0], "portrait": MG.GEOMETRIES[1], "oddw": MG.GEOMETRIES[2],
               "canvasfit": MG.GEOMETRIES[3]}
    geometries = tuple(mapping[name] for name in ("landscape", "portrait", "oddw", "canvasfit")
                       if name in wanted)
    if not geometries:
        print("[hud] 输入错误：--geometries 未匹配任何几何")
        return 2
    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        code = run(out_dir=out_dir, limit=args.limit, geometries=geometries)
    except Exception as exc:
        (out_dir / "console").mkdir(parents=True, exist_ok=True)
        (out_dir / "console" / "failure.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"[hud] FAILED {type(exc).__name__}: {exc}")
        return 1
    print(f"[hud] exit={code} out={out_dir}")
    return code


if __name__ == "__main__":
    sys.exit(main())