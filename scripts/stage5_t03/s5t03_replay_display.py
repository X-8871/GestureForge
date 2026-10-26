#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线 replay/display 骨架驱动：合成结果流 → 显示管线 → 离线渲染 → 三层产物。

产物（Wong 2026-10-26 指定形态）
================================
- `results.json`           机器验收**主证据**（权威）
- `frame_assertions.jsonl` 逐帧断言（frame_id / result_frame_id / result_seq / 矩形 / 类别 /
                           分数 / 坐标映射 / stale 与年龄 / 输入帧 SHA / PNG SHA / 种子 / 确定性参数）
- `keyframes/*.png`        仅关键帧（首/末/每类代表/零框/过期边界/被拒/长跑检查点/HUD 代表）
- `demo.mp4`               **仅演示**（`demo_only`；无 ffmpeg 时记 NOT_RUN）
- `manifest.json`          哈希/输入/版本/限制/NOT_RUN

诚实边界
========
- 输入是**合成流**（`synthetic_replay`）：`capture_time_ns` 是合成单调时钟，不是真实采集时刻。
- **真实回放接入 = NOT_RUN**：工作区当前没有可消费的阶段4 冻结「回放结果包」（阶段4 契约 r06 仍
  `DRAFT_PENDING_REVIEW`，task-26 BLOCKED）。阶段3 固定帧只作**输入帧**，不是推理结果。
- 本驱动不接板卡/摄像头/UART/JTAG；产物不代表板上绘制，也不代表 G0/G1/G3/G4/G5 通过。
- PNG/MP4 不是验收依据（JSON 才是）；MP4 一律标 `demo_only`。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402
import scripts.stage5_t03.s5t03_display_pipeline as P  # noqa: E402
import scripts.stage5_t03.s5t03_dynamic_stream as S  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402

SCHEMA = "gestureforge_s5t03_replay_display_v1"
INPUT_SCOPE_LABEL = "synthetic_replay"
STATUS_LABEL = "PRELIMINARY"
NOT_RUN = [
    "真实回放接入（无阶段4 冻结回放结果包；契约 r06=DRAFT_PENDING_REVIEW / task-26 BLOCKED）",
    "板上动态映射与绘制（板级 SUSPENDED_BOARD_DETACHED；本轮不接板卡）",
    "真实采集路径（摄像头未到货）",
    "真实集成的 30 分钟联调与 T5-10 板上回归",
]
DEMO_ONLY_NOTE = "demo.mp4 仅用于演示（demo_only），不是验收证据；机器验收以 results.json 为准。"


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


def load_params() -> dict[str, Any]:
    path = P.default_params_path()
    return json.loads(path.read_text(encoding="utf-8"))


def boundary_cases() -> list[dict[str, Any]]:
    """三例过期边界（离线）：`age==limit` 不过期、`limit+1` 过期、显式 `stale_flag`。"""
    limit = int(R.STALE_AGE_LIMIT_NS)
    base = 1_000_000_000
    cases: list[dict[str, Any]] = []
    for case_id, commit_offset, stale_flag in (("age_equals_limit_not_stale", limit, False),
                                               ("age_limit_plus_one_stale", limit + 1, False),
                                               ("explicit_stale_flag", 5_000_000, True)):
        record = S.make_record(session_id=9, frame_id=0, result_seq=1, sequence=1,
                               capture_time_ns=base, result_time_ns=base + 1_000_000,
                               inference_time_ns=900_000, state="OK", stale=stale_flag,
                               detections=[S.make_detection(0)])
        cases.append({"case_id": case_id, "record": record, "commit_ns": base + commit_offset,
                      "expect_stale": case_id != "age_equals_limit_not_stale",
                      "expect_age_frame_ns": commit_offset})
    return cases


def select_keyframes(events: list[dict[str, Any]], *, keyframe_max: int) -> dict[int, list[str]]:
    """关键帧选择（有界）：首/末、每类首个、零框、被拒、过期、长跑检查点。"""
    picked: dict[int, list[str]] = {}

    def mark(index: int, tag: str) -> None:
        picked.setdefault(index, [])
        if tag not in picked[index]:
            picked[index].append(tag)

    if events:
        mark(0, "first")
        mark(len(events) - 1, "last")
    seen_class: set[str] = set()
    seen_reject: set[str] = set()
    stale_marked = zero_marked = hud_marked = False
    for index, event in enumerate(events):
        for box in event.get("box_px") or []:
            name = str(box.get("class_name"))
            if name not in seen_class:
                seen_class.add(name)
                mark(index, f"class_{name}")
        if event.get("state") == "NO_HAND" and not event.get("stale_effective") and not zero_marked:
            zero_marked = True
            mark(index, "zero_box")
        if event.get("stale_effective") and not stale_marked:
            stale_marked = True
            mark(index, "stale_first")
        if int(event.get("boxes") or 0) >= 3 and not hud_marked:
            hud_marked = True
            mark(index, "hud_multi_box")
        for reject in ("duplicate", "duplicate_frame_id", "out_of_order"):
            if reject not in seen_reject:
                key = (event.get("session_id"), event.get("result_frame_id"), event.get("result_seq"))
                if key in (event.get("rejected_keys") or []):
                    seen_reject.add(reject)
                    mark(index, f"rejected_{reject}")
    if len(events) > 8:
        step = max(1, len(events) // 4)
        for index in range(step, len(events), step):
            mark(index, "checkpoint")
    if len(picked) > keyframe_max:                        # 有界：**必保首末**，其余按序采样
        ordered = sorted(picked)
        keep = {ordered[0], ordered[-1]}
        budget = max(0, keyframe_max - len(keep))
        interior = ordered[1:-1]
        if budget and interior:
            stride = max(1, (len(interior) + budget - 1) // budget)
            keep.update(interior[::stride][:budget])
        picked = {i: picked[i] for i in sorted(keep)}
    return picked


def load_stage3_frame(binding_path: pathlib.Path) -> tuple[Any, dict[str, Any]]:
    """按阶段3 绑定 JSON 装载**裸 BGR888 输入帧**；哈希不符即抛（绝不静默用错帧）。

    注意：这只是**输入帧**（背景），**不是**推理结果；阶段4 冻结回放结果包当前不存在，
    因此"真实回放接入"仍记 `NOT_RUN`（本函数不改变这一点）。
    """
    if not RD.PIL_AVAILABLE:
        raise RD.RenderUnavailableError(RD.PIL_IMPORT_ERROR)
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    frame_path = pathlib.Path(str(binding["source_worktree"])) / str(binding["source_frame_path"])
    if not frame_path.is_file():
        raise FileNotFoundError(f"阶段3 输入帧不存在：{frame_path}")
    actual = sha256_file(frame_path)
    if actual != str(binding["source_frame_sha256"]):
        raise ValueError(f"阶段3 输入帧哈希不符：实测 {actual[:12]}… vs 绑定 {str(binding['source_frame_sha256'])[:12]}…")
    width, height = int(binding["width"]), int(binding["height"])
    stride = int(binding["stride_bytes"])
    if str(binding.get("pixel_format")) != "BGR888":
        raise ValueError(f"未支持的像素格式：{binding.get('pixel_format')!r}")
    raw = frame_path.read_bytes()
    if len(raw) != stride * height:
        raise ValueError(f"输入帧字节数 {len(raw)} != stride×height {stride * height}")
    image = RD.Image.frombytes("RGB", (width, height), raw, "raw", "BGR", stride)
    info = {"background": "stage3_fixed_frame_input_only", "background_path": str(frame_path),
            "background_sha256": actual, "background_size": [width, height],
            "binding_path": str(binding_path), "binding_sha256": sha256_file(binding_path),
            "input_frame_id": binding.get("source_frame_id"), "pixel_format": "BGR888",
            "stride_bytes": stride, "documented_capture_time_ns": binding.get("capture_time_ns"),
            "input_scope": "input_frame_only__results_are_synthetic",
            "note": "阶段3 固定帧仅作**输入帧/背景**；推理结果为合成流 ⇒ 真实回放接入仍 NOT_RUN"}
    return image, info


def run_replay(*, out_dir: pathlib.Path, mode: str, frames: int, seed: int, canvas: tuple[int, int],
               background_path: pathlib.Path | None, keyframe_max: int, want_demo: bool,
               stage3_binding: pathlib.Path | None = None) -> int:
    console = out_dir / "console"
    console.mkdir(parents=True, exist_ok=True)
    keyframes = out_dir / "keyframes"
    params = load_params()
    frozen = params["newly_frozen_for_skeleton_only"]
    period_ns = int(frozen["long_run_virtual_frame_period_ns"])
    width, height = canvas

    background = None
    background_info: dict[str, Any] = {"background": "uniform_rgb", "background_sha256": None}
    if stage3_binding is not None:
        background, background_info = load_stage3_frame(stage3_binding)
    elif background_path is not None:
        if not RD.PIL_AVAILABLE:
            raise RD.RenderUnavailableError(RD.PIL_IMPORT_ERROR)
        background = RD.Image.open(background_path).convert("RGB")
        background_info = {"background": "provided_input_frame", "background_path": str(background_path),
                           "background_sha256": sha256_file(background_path),
                           "background_size": list(background.size)}

    steps = S.build_stream(mode, frames, params=params, seed=seed, frame_period_ns=period_ns,
                           warmup_frames=0)
    pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height,
                                 input_scope_label=INPUT_SCOPE_LABEL, params=params)
    font, font_info = RD.load_font(RD.font_size_px(height)) if RD.PIL_AVAILABLE else (None, {})

    events: list[dict[str, Any]] = []
    five_tuples: list[dict[str, Any]] = []
    hud_last: Mapping[str, Any] | None = None
    rejected_keys: set[tuple] = set()
    submit_verdicts: list[dict[str, Any]] = []
    for step in steps:
        for record in step.get("results") or []:
            outcome = pipeline.submit_result(record)
            submit_verdicts.append({"outcome": outcome.get("outcome"), "verdict": outcome.get("verdict"),
                                    "frame_id": record.get("frame_id"), "result_seq": record.get("result_seq"),
                                    "reject_reason": outcome.get("reject_reason")})
            if outcome.get("verdict") == P.VERDICT_FAIL:
                rejected_keys.add((record.get("session_id"), record.get("frame_id"), record.get("result_seq")))
        committed = pipeline.commit_frame(int(step["displayed_frame_id"]), int(step["overlay_commit_ns"]),
                                          warmup=bool(step.get("warmup", False)))
        event = committed["event"]
        event["rejected_keys"] = sorted(rejected_keys)
        events.append(event)
        five_tuples.append(committed["five_tuple"])
        hud_last = committed["hud"]
    pipeline.assert_recomputable()

    picked = select_keyframes(events, keyframe_max=keyframe_max)
    assertions: list[dict[str, Any]] = []
    keyframe_records: list[dict[str, Any]] = []
    failures: list[str] = []
    for index, event in enumerate(events):
        hud = pipeline.hud(event, int(event["displayed_frame_id"]))
        entry: dict[str, Any] = {
            "frame_index": index,
            "displayed_frame_id": event["displayed_frame_id"],
            "result_frame_id": event["result_frame_id"],
            "result_seq": event["result_seq"],
            "session_id": event["session_id"],
            "state": event["state"],
            "drawn": bool(event["drawn"]),
            "boxes": int(event["boxes"]),
            "zero_area_dropped": int(event["zero_area_dropped"]),
            "stale_effective": bool(event["stale_effective"]),
            "stale_reason": event["stale_reason"],
            "skip_reason": event["skip_reason"],
            "age_result_ns": event["age_result_ns"],
            "age_frame_ns": event["age_frame_ns"],
            "display_semantics": event["display_semantics"],
            "overlay_commit_ns": event["overlay_commit_ns"],
            "coordinate_mapping": {
                "rule": R.ROUNDING_RULE,
                "span_minus_one": {"x": width - 1, "y": height - 1},
                "boxes_px": [{"class_name": b["class_name"], "score": b["score"], "px": b["px"],
                              "border_pixels": b["border_pixels"]} for b in event.get("box_px") or []],
            },
            "input_scope_label": INPUT_SCOPE_LABEL,
            "input_frame_sha256": background_info.get("background_sha256"),
            "seed": seed,
            "deterministic_params": {"canvas": [width, height], "line_width_px": R.DISPLAY_LINE_WIDTH_PX,
                                     "font_size_px": RD.font_size_px(height),
                                     "safe_area_px": RD.safe_area_px(height),
                                     "rounding_rule": R.ROUNDING_RULE},
            "hud": dict(hud),
            "checks": {"stale_implies_no_box": (not event["stale_effective"]) or int(event["boxes"]) == 0,
                       "hud_13_fields": len(hud) == 13},
            "png_sha256": None,
            "png_path": None,
        }
        if index in picked:
            if RD.PIL_AVAILABLE:
                tag = "+".join(picked[index])
                png_path = keyframes / f"{index:05d}_fid{int(event['displayed_frame_id']):05d}_{tag}.png"
                stats = RD.render_to_png(png_path, event, canvas_width=width, canvas_height=height,
                                         background=background, hud=hud, font=font)
                entry["png_path"] = stats["png_path"].replace(str(REPO_ROOT), "").lstrip("/\\")
                entry["png_sha256"] = stats["png_sha256"]
                entry["png_bytes"] = stats["png_bytes"]
                entry["render"] = stats
                entry["checks"]["boxes_drawn_matches"] = int(stats["boxes_drawn"]) == int(event["boxes"])
                entry["checks"]["border_pixels_match"] = all(
                    int(b["border_pixels"]) == len(R.border_pixel_sets(int(b["px"]["x1"]), int(b["px"]["y1"]),
                                                                      int(b["px"]["x2"]), int(b["px"]["y2"]),
                                                                      R.DISPLAY_LINE_WIDTH_PX, width, height))
                    for b in event.get("box_px") or [])
                entry["checks"]["hud_lines_13"] = int(stats.get("hud_lines_drawn", 0)) == 13
                keyframe_records.append({"frame_index": index, "tags": picked[index],
                                         "png_path": entry["png_path"], "png_sha256": entry["png_sha256"]})
            else:
                entry["checks"]["render_not_run"] = True
        for name, ok in entry["checks"].items():
            if ok is False:
                failures.append(f"frame[{index}].{name}")
        assertions.append(entry)

    boundary_results: list[dict[str, Any]] = []
    for case in boundary_cases():
        mini = P.DisplayPipeline(canvas_width=width, canvas_height=height,
                                 input_scope_label="synthetic_replay_boundary", params=params)
        mini.submit_result(case["record"])
        committed = mini.commit_frame(0, case["commit_ns"])
        event = committed["event"]
        hud = committed["hud"]
        ok = bool(event["stale_effective"]) == bool(case["expect_stale"]) and \
            int(event["age_frame_ns"]) == int(case["expect_age_frame_ns"])
        if not ok:
            failures.append(f"boundary[{case['case_id']}]")
        result = {"case_id": case["case_id"], "expect_stale": case["expect_stale"],
                  "stale_effective": bool(event["stale_effective"]), "stale_reason": event["stale_reason"],
                  "age_frame_ns": event["age_frame_ns"], "age_result_ns": event["age_result_ns"],
                  "boxes": event["boxes"], "drawn": bool(event["drawn"]), "pass": ok, "png_path": None,
                  "png_sha256": None}
        if RD.PIL_AVAILABLE:
            png_path = keyframes / f"boundary_{case['case_id']}.png"
            stats = RD.render_to_png(png_path, event, canvas_width=width, canvas_height=height,
                                     background=background, hud=hud, font=font)
            result["png_path"] = stats["png_path"].replace(str(REPO_ROOT), "").lstrip("/\\")
            result["png_sha256"] = stats["png_sha256"]
        boundary_results.append(result)

    (out_dir / "frame_assertions.jsonl").write_text(
        "\n".join(json.dumps(entry, ensure_ascii=False, sort_keys=True) for entry in assertions) + "\n",
        encoding="utf-8")

    demo_info: dict[str, Any] = {"requested": bool(want_demo), "status": "NOT_RUN", "demo_only": True,
                                 "note": DEMO_ONLY_NOTE}
    if want_demo:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            demo_info["reason"] = "ffmpeg 不在 PATH ⇒ 不生成 demo（记 NOT_RUN，不冒充产物）"
        elif not keyframes.exists() or not list(keyframes.glob("*.png")):
            demo_info["reason"] = "无关键帧可编码"
        else:
            out_mp4 = out_dir / "demo.mp4"
            pngs = sorted(keyframes.glob("*.png"))
            listing = keyframes / "concat_list.txt"
            listing.write_text("".join(f"file '{p.as_posix()}'\nduration 0.25\n" for p in pngs),
                               encoding="utf-8")
            logs: list[str] = []
            for encoder in ("libx264", "mpeg4"):
                cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-r", "4", "-i", str(listing),
                       "-c:v", encoder, "-pix_fmt", "yuv420p", str(out_mp4)]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                logs.append(f"$ {' '.join(cmd)}\n[exit code: {proc.returncode}]\n"
                            f"{proc.stdout[-3000:]}\n{proc.stderr[-3000:]}\n")
                if proc.returncode == 0 and out_mp4.exists():
                    demo_info.update({"status": "GENERATED", "exit_code": proc.returncode,
                                      "encoder": encoder, "cmd": " ".join(cmd), "path": "demo.mp4",
                                      "sha256": sha256_file(out_mp4),
                                      "source_keyframes": len(pngs),
                                      "concat_list": "keyframes/concat_list.txt"})
                    break
                demo_info.update({"status": "FAILED", "exit_code": proc.returncode, "encoder": encoder,
                                  "cmd": " ".join(cmd),
                                  "reason": "ffmpeg 编码失败；demo 仅为可选演示，不影响 JSON 主证据"})
            (console / "ffmpeg_demo.txt").write_text("".join(logs), encoding="utf-8")

    recomputed = pipeline.recompute()
    results = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "source_commit": git_head(), "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "stream": {"mode": mode, "frames": frames, "seed": seed,
                   "frame_period_ns": period_ns, "canvas": [width, height],
                   "params_id": params.get("params_id"), "params_path": str(P.default_params_path().relative_to(REPO_ROOT))},
        "input": background_info,
        "display_semantics": R.DISPLAY_SEMANTICS,
        "counters": dict(pipeline.counters),
        "recomputed_counters": recomputed["counters"],
        "recompute_matches_online": recomputed["counters"] == pipeline.counters,
        "five_tuples_head": five_tuples[:5], "five_tuple_count": len(five_tuples),
        "hud_last": dict(hud_last or {}),
        "submit_verdicts": submit_verdicts,
        "boundary_cases": boundary_results,
        "keyframes": keyframe_records, "keyframe_count": len(keyframe_records),
        "render": {"pillow_version": RD.PILLOW_VERSION, "font": font_info,
                   "class_colors_rgb": {k: "#%02X%02X%02X" % v for k, v in RD.CLASS_COLORS_RGB.items()},
                   "ur3_decision_doc": RD.UR3_DECISION_DOC,
                   "line_width_px": R.DISPLAY_LINE_WIDTH_PX, "rounding_rule": R.ROUNDING_RULE,
                   "font_base_px_at_720": RD.FONT_BASE_PX_AT_720},
        "demo": demo_info,
        "checks": {"frames": len(events), "assertions": len(assertions), "failures": failures,
                   "passed": not failures},
        "artifacts": {"results_json": "results.json", "frame_assertions_jsonl": "frame_assertions.jsonl",
                      "keyframes_dir": "keyframes/", "manifest": "manifest.json"},
        "limitations": ["输入为合成流；capture_time_ns 为合成单调时钟值，不是真实采集时刻。",
                        "真实回放接入 NOT_RUN（无可消费阶段4 冻结结果包）。",
                        "PNG/MP4 不是验收依据；机器验收以 results.json + frame_assertions.jsonl 为准。",
                        "离线渲染不代表板上绘制；G0/G1/G3/G4/G5 均未通过。"],
        "not_run": NOT_RUN,
    }
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")

    manifest = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": results["generated_utc8"], "source_commit": results["source_commit"],
        "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "goal_reached": "OFFLINE_REPLAY_DISPLAY_SKELETON_RENDERED_JSON_PRIMARY_KEYFRAMES_DEMO_OPTIONAL",
        "tools": {
            "replay_display": {"path": "scripts/stage5_t03/s5t03_replay_display.py",
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
            "params": {"path": str(P.default_params_path().relative_to(REPO_ROOT)),
                       "sha256": sha256_file(P.default_params_path())},
        },
        "counters": results["counters"], "recompute_matches_online": results["recompute_matches_online"],
        "checks": results["checks"], "keyframe_count": results["keyframe_count"],
        "demo": demo_info,
        "files": [{"path": p.relative_to(out_dir).as_posix(), "sha256": sha256_file(p),
                   "bytes": p.stat().st_size}
                  for p in sorted(x for x in out_dir.rglob("*") if x.is_file() and x.name != "manifest.json")],
        "limitations": results["limitations"], "not_run": NOT_RUN,
        "scope_statement": "本清单只证明离线骨架的渲染路径与文件绑定；不代表测试语义正确、独立审查通过或 G0/G4/G5。",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    return 0 if not failures else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 离线 replay/display 骨架驱动（合成流；不接板卡）")
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", default="mixed",
                        choices=["sequential", "skip", "late", "dup", "ooo", "equiv", "mixed"])
    parser.add_argument("--frames", type=int, default=0, help="0=用参数文件对应模式的样本数")
    parser.add_argument("--seed", type=int, default=0, help="0=用参数文件冻结种子")
    parser.add_argument("--canvas", default="1280x720")
    parser.add_argument("--background-png", default=None)
    parser.add_argument("--stage3-binding", default=None,
                        help="阶段3 输入帧绑定 JSON（replay_input_binding.json）；用作**背景输入帧**，"
                             "不改变「推理结果为合成、真实回放 NOT_RUN」")
    parser.add_argument("--keyframe-max", type=int, default=24)
    parser.add_argument("--demo-mp4", action="store_true")
    args = parser.parse_args(argv)

    params = load_params()
    frozen = params["newly_frozen_for_skeleton_only"]
    frames = args.frames or int(frozen["stream_samples"].get(f"{args.mode}_frames", 120))
    seed = args.seed or int(frozen["seed"])
    canvas = tuple(int(v) for v in args.canvas.lower().split("x"))
    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    background = pathlib.Path(args.background_png) if args.background_png else None
    stage3_binding = pathlib.Path(args.stage3_binding) if args.stage3_binding else None
    started = time.time()
    try:
        code = run_replay(out_dir=out_dir, mode=args.mode, frames=frames, seed=seed, canvas=canvas,
                          background_path=background, keyframe_max=args.keyframe_max,
                          want_demo=bool(args.demo_mp4), stage3_binding=stage3_binding)
    except Exception as exc:  # 失败也要留痕，不静默
        (out_dir / "console").mkdir(parents=True, exist_ok=True)
        (out_dir / "console" / "failure.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"[replay] FAILED {type(exc).__name__}: {exc}")
        return 1
    elapsed = time.time() - started
    (out_dir / "console" / "run.txt").write_text(
        f"mode={args.mode} frames={frames} seed={seed} canvas={canvas} elapsed_s={elapsed:.3f}\n", encoding="utf-8")
    print(f"[replay] exit={code} out={out_dir} elapsed={elapsed:.2f}s")
    return code


if __name__ == "__main__":
    sys.exit(main())