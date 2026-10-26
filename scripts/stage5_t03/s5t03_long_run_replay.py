#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线**长跑回放**：虚拟时间 ≥30 分钟 × 渲染路径（检查点关键帧）+ 全量日志。

与 `s5t03_replay_display.py` 的关系
===================================
- 复用同一个显示管线（`DisplayPipeline`）与同一套几何/色/字号（`s5t03_render.py`）；
- 单独成模块的原因：长跑是**流式**的（106k+ 帧），不能把逐帧断言全量堆在内存里；而且
  已通过独立复审的短跑驱动哈希应保持冻结，长跑改动不与它混在一起。

长跑口径（沿用已冻结参数 `docs/stage5/s5t03_offline_skeleton_params_v1.json`）
================================================================================
- 帧周期 `16 890 000 ns`（板上实测 display frame period 的**离线虚拟步长**，非本轮板上测量）；
- 判据用**区间数**：`period_count = frames − 1`，`virtual_elapsed = period_count × period`；
- `21 572 × …` 口径见参数文件：要求 `virtual_elapsed ≥ 1 800 000 000 000 ns`（1800 s），余量 < 1 个周期；
- 不变量：每显示帧**恰好一次** overlay 提交事件（无漏提交 ⇒ 无死锁）、提交时间戳单调不减、
  在线计数可由帧级事件日志完全复算。

诚实边界
========
- 输入是**合成流**（`synthetic_replay`），`status=PRELIMINARY`；虚拟时间**不是**墙上时间；
- **真实回放接入 / 板上动态映射 / 摄像头路径仍 NOT_RUN**；本模块不接板卡、不联网；
- 关键帧 PNG 供人工抽检，**JSON/日志才是验收依据**；`demo.mp4` 一律 `demo_only`。
"""

from __future__ import annotations

import argparse
import gzip
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
import scripts.stage5_t03.s5t03_replay_display as SHORT  # noqa: E402

SCHEMA = "gestureforge_s5t03_long_run_replay_v1"
INPUT_SCOPE_LABEL = "synthetic_replay"
STATUS_LABEL = "PRELIMINARY"
NOT_RUN = [
    "真实回放接入（无阶段4 冻结回放结果包）",
    "板上动态映射与绘制（本轮不接板卡）",
    "摄像头真实采集路径",
    "真实推理 30 分钟联调（本长跑只覆盖显示/叠加路径；inference_fps=NA）",
    "T5-10 板上回归",
]


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip()


def load_params() -> dict[str, Any]:
    return json.loads(P.default_params_path().read_text(encoding="utf-8"))


def _compact_assertion(index: int, event: Mapping[str, Any], *, seed: int, input_sha: str | None,
                       canvas: tuple[int, int]) -> dict[str, Any]:
    """长跑用的紧凑逐帧断言（不含逐框像素列表；像素级细节只保留在关键帧条目里）。"""
    return {
        "frame_index": index,
        "displayed_frame_id": event["displayed_frame_id"],
        "result_frame_id": event["result_frame_id"],
        "result_seq": event["result_seq"],
        "state": event["state"],
        "drawn": bool(event["drawn"]),
        "boxes": int(event["boxes"]),
        "boxes_px_count": len(event.get("box_px") or []),
        "zero_area_dropped": int(event["zero_area_dropped"]),
        "stale_effective": bool(event["stale_effective"]),
        "stale_reason": event["stale_reason"],
        "skip_reason": event["skip_reason"],
        "age_result_ns": event["age_result_ns"],
        "age_frame_ns": event["age_frame_ns"],
        "display_semantics": event["display_semantics"],
        "overlay_commit_ns": event["overlay_commit_ns"],
        "rejects_this_frame": event.get("rejects_this_frame") or [],
        "input_scope_label": INPUT_SCOPE_LABEL,
        "input_frame_sha256": input_sha,
        "seed": seed,
        "canvas": list(canvas),
        "assertion_mode": "compact",
    }


def run_long(*, out_dir: pathlib.Path, frames: int, seed: int, canvas: tuple[int, int],
             stage3_binding: pathlib.Path | None, keyframe_max: int, want_demo: bool,
             stream_mode: str, warmup_frames: int) -> int:
    console = out_dir / "console"
    logs_dir = out_dir / "logs"
    keyframes_dir = out_dir / "keyframes"
    for path in (console, logs_dir, keyframes_dir):
        path.mkdir(parents=True, exist_ok=True)
    params = load_params()
    frozen = params["newly_frozen_for_skeleton_only"]
    period_ns = int(frozen["long_run_virtual_frame_period_ns"])
    required_ns = int(frozen["long_run_virtual_duration_ns"])
    width, height = canvas

    background = None
    input_info: dict[str, Any] = {"background": "uniform_rgb", "background_sha256": None}
    if stage3_binding is not None:
        background, input_info = SHORT.load_stage3_frame(stage3_binding)
    font, font_info = RD.load_font(RD.font_size_px(height)) if RD.PIL_AVAILABLE else (None, {})

    steps = S.build_stream(stream_mode, frames, params=params, seed=seed, frame_period_ns=period_ns,
                           warmup_frames=warmup_frames)
    pipeline = P.DisplayPipeline(canvas_width=width, canvas_height=height,
                                 input_scope_label=INPUT_SCOPE_LABEL, params=params)

    checkpoint_stride = max(1, frames // max(1, keyframe_max))
    hits: dict[int, list[str]] = {}
    full_entries: list[dict[str, Any]] = []
    failure_list: list[str] = []
    monotonic = True
    last_commit: int | None = None
    first_stale = first_zero = first_reject = False
    assertions_path = out_dir / "frame_assertions.jsonl.gz"
    assertion_count = 0
    t0 = time.time()
    with gzip.open(assertions_path, "wt", encoding="utf-8") as assertions:
        for index, step in enumerate(steps):
            step_rejects: list[str] = []
            for record in step.get("results") or []:
                outcome = pipeline.submit_result(record)
                if outcome.get("verdict") == P.VERDICT_FAIL:
                    step_rejects.append(str(outcome.get("outcome")))
            commit_ns = int(step["overlay_commit_ns"])
            committed = pipeline.commit_frame(int(step["displayed_frame_id"]), commit_ns,
                                              warmup=bool(step.get("warmup", False)))
            event = committed["event"]
            event["rejects_this_frame"] = step_rejects
            if last_commit is not None and commit_ns < last_commit:
                monotonic = False
            last_commit = commit_ns

            tags: list[str] = []
            if index == 0:
                tags.append("first")
            if index == frames - 1:
                tags.append("last")
            if index % checkpoint_stride == 0:
                tags.append("checkpoint")
            if event["stale_effective"] and not first_stale:
                first_stale = True
                tags.append("stale_first")
            if event["state"] == "NO_HAND" and not event["stale_effective"] and not first_zero:
                first_zero = True
                tags.append("zero_box")
            if step_rejects and not first_reject:
                first_reject = True
                tags.append("rejected_" + "+".join(sorted(set(step_rejects))))
            if tags:
                hits[index] = tags

            entry = _compact_assertion(index, event, seed=seed,
                                       input_sha=input_info.get("background_sha256"), canvas=canvas)
            assertions.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
            assertion_count += 1

            if tags and RD.PIL_AVAILABLE:
                hud = pipeline.hud(event, int(event["displayed_frame_id"]))
                png_path = keyframes_dir / f"{index:06d}_fid{int(event['displayed_frame_id']):06d}_{'+'.join(tags)}.png"
                stats = RD.render_to_png(png_path, event, canvas_width=width, canvas_height=height,
                                         background=background, hud=hud, font=font)
                full_entries.append({"frame_index": index, "tags": tags,
                                     "png_path": png_path.relative_to(out_dir).as_posix(),
                                     "png_sha256": stats["png_sha256"], "boxes": int(event["boxes"]),
                                     "stale_effective": bool(event["stale_effective"]),
                                     "coordinate_mapping": {
                                         "rule": R.ROUNDING_RULE,
                                         "boxes_px": [{"class_name": b["class_name"], "score": b["score"],
                                                       "px": b["px"], "border_pixels": b["border_pixels"]}
                                                      for b in event.get("box_px") or []]},
                                     "hud": dict(hud), "render": stats, "font": font_info,
                                     "input_frame_sha256": input_info.get("background_sha256")})
    elapsed = time.time() - t0
    pipeline.assert_recomputable()

    # 事件日志（紧凑、gzip）：长跑全量可复算
    events_gz = logs_dir / f"events_{stream_mode}_{frames}.jsonl.gz"
    with gzip.open(events_gz, "wt", encoding="utf-8") as handle:
        for event in pipeline.log.events:
            handle.write(json.dumps(pipeline.log.compact_event(event), ensure_ascii=False, sort_keys=True) + "\n")

    period_count = frames - 1
    virtual_elapsed_ns = period_count * period_ns
    margin_ns = virtual_elapsed_ns - required_ns

    # 过期边界三例（渲染路径，独立小管线）
    boundary: list[dict[str, Any]] = []
    for case in SHORT.boundary_cases():
        mini = P.DisplayPipeline(canvas_width=width, canvas_height=height, params=params)
        mini.submit_result(case["record"])
        committed = mini.commit_frame(0, case["commit_ns"])
        event = committed["event"]
        ok = bool(event["stale_effective"]) == bool(case["expect_stale"]) and \
            int(event["age_frame_ns"]) == int(case["expect_age_frame_ns"])
        if not ok:
            failure_list.append(f"boundary[{case['case_id']}]")
        item = {"case_id": case["case_id"], "expect_stale": case["expect_stale"],
                "stale_effective": bool(event["stale_effective"]), "stale_reason": event["stale_reason"],
                "age_frame_ns": event["age_frame_ns"], "boxes": event["boxes"], "pass": ok,
                "png_path": None, "png_sha256": None}
        if RD.PIL_AVAILABLE:
            path = keyframes_dir / f"boundary_{case['case_id']}.png"
            stats = RD.render_to_png(path, event, canvas_width=width, canvas_height=height,
                                     background=background, hud=committed["hud"], font=font)
            item["png_path"] = path.relative_to(out_dir).as_posix()
            item["png_sha256"] = stats["png_sha256"]
        boundary.append(item)

    demo: dict[str, Any] = {"requested": bool(want_demo), "status": "NOT_RUN", "demo_only": True,
                            "note": SHORT.DEMO_ONLY_NOTE}
    if want_demo:
        ffmpeg = shutil.which("ffmpeg")
        pngs = sorted(keyframes_dir.glob("*.png"))
        if not ffmpeg or not pngs:
            demo["reason"] = "无 ffmpeg 或无关键帧"
        else:
            listing = keyframes_dir / "concat_list.txt"
            listing.write_text("".join(f"file '{p.as_posix()}'\nduration 0.5\n" for p in pngs), encoding="utf-8")
            mp4 = out_dir / "demo.mp4"
            logs: list[str] = []
            for encoder in ("libx264", "mpeg4"):
                cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-r", "2", "-i", str(listing),
                       "-c:v", encoder, "-pix_fmt", "yuv420p", str(mp4)]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                logs.append(f"$ {' '.join(cmd)}\n[exit code: {proc.returncode}]\n{proc.stderr[-2000:]}\n")
                if proc.returncode == 0 and mp4.exists():
                    demo.update({"status": "GENERATED", "encoder": encoder, "path": "demo.mp4",
                                 "sha256": sha256_file(mp4), "source_keyframes": len(pngs),
                                 "exit_code": 0, "cmd": " ".join(cmd)})
                    break
                demo.update({"status": "FAILED", "encoder": encoder, "exit_code": proc.returncode})
            (console / "ffmpeg_demo.txt").write_text("".join(logs), encoding="utf-8")

    recomputed = pipeline.recompute()
    canonical = frames >= int(frozen["long_run_min_frames"])
    hard_invariants = {
        "one_commit_event_per_frame": len(pipeline.log.commit_events()) == frames,
        "commit_timestamps_monotonic": monotonic,
        "recompute_matches_online": recomputed["counters"] == pipeline.counters,
        "no_deadlock": assertion_count == frames,
    }
    soft_invariants = {
        "required_duration_met": virtual_elapsed_ns >= required_ns,
        "margin_within_one_period": (0 <= margin_ns < period_ns) if canonical else None,
    }
    invariants = {
        "period_count": period_count,
        "period_ns": period_ns,
        "virtual_elapsed_ns": virtual_elapsed_ns,
        "virtual_elapsed_s": round(virtual_elapsed_ns / 1e9, 3),
        "required_ns": required_ns,
        "margin_ns": margin_ns,
        "canonical_long_run": canonical,
        "min_frames_for_canonical": int(frozen["long_run_min_frames"]),
        **hard_invariants, **soft_invariants,
    }
    for name, ok in hard_invariants.items():
        if not ok:
            failure_list.append(f"invariant[{name}]")
    if canonical:                                   # 规范长跑才强制 ≥30 分钟与余量口径
        for name, ok in soft_invariants.items():
            if ok is not True:
                failure_list.append(f"invariant[{name}]")

    results = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "source_commit": git_head(), "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "stream": {"mode": stream_mode, "frames": frames, "seed": seed, "warmup_frames": warmup_frames,
                   "frame_period_ns": period_ns, "canvas": list(canvas),
                   "params_id": params.get("params_id"),
                   "virtual_time_note": "虚拟时间步长＝板上实测 display frame period 的离线步长；不是墙上时间"},
        "input": input_info, "display_semantics": R.DISPLAY_SEMANTICS,
        "counters": dict(pipeline.counters), "recomputed_counters": recomputed["counters"],
        "invariants": invariants,
        "keyframes": full_entries, "keyframe_count": len(full_entries),
        "boundary_cases": boundary,
        "render": {"pillow_version": RD.PILLOW_VERSION, "font": font_info,
                   "class_colors_rgb": {k: "#%02X%02X%02X" % v for k, v in RD.CLASS_COLORS_RGB.items()},
                   "line_width_px": R.DISPLAY_LINE_WIDTH_PX, "rounding_rule": R.ROUNDING_RULE},
        "artifacts": {"results_json": "results.json", "frame_assertions_jsonl_gz": "frame_assertions.jsonl.gz",
                      "events_jsonl_gz": f"logs/{events_gz.name}", "keyframes_dir": "keyframes/",
                      "manifest": "manifest.json"},
        "assertion_mode": "compact", "assertion_count": assertion_count,
        "process_seconds": round(elapsed, 3),
        "demo": demo,
        "checks": {"failures": failure_list, "passed": not failure_list},
        "limitations": ["输入为合成流；虚拟时间不是墙上时间，capture_time_ns 是合成单调时钟值。",
                        "本长跑只覆盖**显示/叠加路径**；inference_fps=NA，不得据此声称推理 30 分钟无死锁。",
                        "真实回放接入 / 板上绘制 / 摄像头路径 NOT_RUN。",
                        "逐帧断言为 compact（不含逐框像素表）；像素级细节在关键帧条目与事件日志中。",
                        "PNG/MP4 不是验收依据（JSON/日志为权威）；G0/G1/G3/G4/G5 均未通过。"],
        "not_run": NOT_RUN,
    }
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")

    manifest = {
        "schema_version": SCHEMA, "run_id": out_dir.name, "task_id": "S5-T03",
        "generated_utc8": results["generated_utc8"], "source_commit": results["source_commit"],
        "status": STATUS_LABEL, "input_scope_label": INPUT_SCOPE_LABEL,
        "goal_reached": "OFFLINE_LONG_RUN_REPLAY_GE_30MIN_VIRTUAL_WITH_CHECKPOINT_KEYFRAMES_AND_FULL_LOGS",
        "invariants": invariants, "counters": results["counters"],
        "checks": results["checks"], "assertion_count": assertion_count,
        "keyframe_count": len(full_entries), "demo": demo,
        "tools": {
            "long_run_replay": {"path": "scripts/stage5_t03/s5t03_long_run_replay.py",
                                "sha256": sha256_file(pathlib.Path(__file__))},
            "short_replay_display": {"path": "scripts/stage5_t03/s5t03_replay_display.py",
                                     "sha256": sha256_file(REPO_ROOT / "scripts/stage5_t03/s5t03_replay_display.py")},
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
        "files": [{"path": p.relative_to(out_dir).as_posix(), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                  for p in sorted(x for x in out_dir.rglob("*") if x.is_file() and x.name != "manifest.json")],
        "limitations": results["limitations"], "not_run": NOT_RUN,
        "scope_statement": "本清单只证明离线长跑回放的文件绑定与不变量；不代表接口语义正确、独立审查通过或 G0/G4/G5。",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    (console / "run.txt").write_text(
        f"frames={frames} mode={stream_mode} seed={seed} period_ns={period_ns} "
        f"virtual_elapsed_s={invariants['virtual_elapsed_s']} assertions={assertion_count} "
        f"keyframes={len(full_entries)} failures={failure_list} process_s={elapsed:.1f}\n", encoding="utf-8")
    return 0 if not failure_list else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 离线长跑回放（虚拟时间；不接板卡）")
    parser.add_argument("--out", required=True)
    parser.add_argument("--frames", type=int, default=0, help="0=用参数文件 long_run_min_frames")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--canvas", default="1280x720")
    parser.add_argument("--stage3-binding", default=None)
    parser.add_argument("--keyframe-max", type=int, default=16)
    parser.add_argument("--warmup-frames", type=int, default=0)
    parser.add_argument("--stream-mode", default=None)
    parser.add_argument("--demo-mp4", action="store_true")
    args = parser.parse_args(argv)

    params = load_params()
    frozen = params["newly_frozen_for_skeleton_only"]
    frames = args.frames or int(frozen["long_run_min_frames"])
    seed = args.seed or int(frozen["seed"])
    stream_mode = args.stream_mode or str(frozen["long_run_stream_mode"])
    canvas = tuple(int(v) for v in args.canvas.lower().split("x"))
    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        code = run_long(out_dir=out_dir, frames=frames, seed=seed, canvas=canvas,
                        stage3_binding=pathlib.Path(args.stage3_binding) if args.stage3_binding else None,
                        keyframe_max=args.keyframe_max, want_demo=bool(args.demo_mp4),
                        stream_mode=stream_mode, warmup_frames=args.warmup_frames)
    except Exception as exc:
        (out_dir / "console").mkdir(parents=True, exist_ok=True)
        (out_dir / "console" / "failure.txt").write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        print(f"[long] FAILED {type(exc).__name__}: {exc}")
        return 1
    print(f"[long] exit={code} out={out_dir}")
    return code


if __name__ == "__main__":
    sys.exit(main())