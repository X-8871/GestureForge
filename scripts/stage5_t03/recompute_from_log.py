#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 独立复算器：只读帧级事件日志（紧凑 JSONL / JSONL.GZ）复算统计量（N-4）。

设计要点
========
- **独立实现**：本模块不导入 `s5t03_display_pipeline`，不复用其内存计数逻辑；它只按
  `docs/stage5/s5t03_offline_skeleton_params_v1.json::newly_frozen_for_skeleton_only.log_artifacts`
  声明的紧凑字段格式解析日志并复算。这样"统计量可由日志复算"才是可被第三方复核的事实，
  而不是复述流水线自己的计数。
- 计数单位与时机与 `counter_units` 完全一致（提交帧 / 结果键 / 提交次数 / 框数）。
- 不读硬件、不写仓库；只读日志文件与可选期望 JSON。

用法（真实退出码）
==================
    python -B scripts/stage5_t03/recompute_from_log.py --log <events.jsonl[.gz]> \
        [--expect <counters.json>] [--json-out <path>]

退出码：0 = 复算成功且（若给了期望）与期望逐项一致；1 = 不一致或日志不可解析；2 = 参数/文件错误。
"""

from __future__ import annotations

import argparse
import gzip
import json
import pathlib
import sys

COUNTER_KEYS = (
    "frames_committed",
    "overlay_drawn_frames",
    "boxes_drawn",
    "warmup_frames",
    "dropped_frames",
    "timeouts",
    "error_results",
    "invalid_records",
    "stale_cleared",
    "duplicate_results",
    "duplicate_frame_id_results",
    "out_of_order_results",
    "zero_hand_frames",
    "zero_area_dropped",
)

COMPACT_SUBMIT_FIELDS = ("t", "fid", "sid", "seq", "oc", "vf")
COMPACT_COMMIT_FIELDS = ("t", "dfid", "ts", "rfid", "sid", "seq", "st", "dr", "bx", "za", "se", "w")


def iter_events(path: pathlib.Path):
    """逐行读日志（支持 .gz）。"""
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"第 {line_number} 行不是合法 JSON：{error}") from error


def recompute(events) -> dict:
    """按 log_artifacts 格式复算；返回 counters + 可核验的日志事实。"""
    counters = {key: 0 for key in COUNTER_KEYS}
    stale_keys: set[tuple] = set()
    commit_count = 0
    submit_count = 0
    displayed_ids: list[int] = []
    timestamps: list[int] = []
    fail_submits = 0
    for event in events:
        kind = event.get("t")
        if kind == "sub":
            submit_count += 1
            outcome = event.get("oc")
            if outcome == "duplicate":
                counters["duplicate_results"] += 1
            elif outcome == "duplicate_frame_id":
                counters["duplicate_frame_id_results"] += 1
            elif outcome == "out_of_order":
                counters["out_of_order_results"] += 1
            elif outcome == "invalid":
                counters["invalid_records"] += 1
            if event.get("vf") == "FAIL":
                fail_submits += 1
        elif kind == "commit":
            commit_count += 1
            counters["frames_committed"] += 1
            if int(event.get("w", 0)):
                counters["warmup_frames"] += 1
            if int(event.get("dr", 0)):
                counters["overlay_drawn_frames"] += 1
            counters["boxes_drawn"] += int(event.get("bx", 0))
            counters["zero_area_dropped"] += int(event.get("za", 0))
            state = event.get("st")
            stale_effective = int(event.get("se", 0))
            if state == "DROPPED":
                counters["dropped_frames"] += 1
            elif state == "TIMEOUT":
                counters["timeouts"] += 1
            elif state == "ERROR":
                counters["error_results"] += 1
            elif state == "NO_HAND" and not stale_effective:
                counters["zero_hand_frames"] += 1
            if stale_effective:
                key = (event.get("sid"), event.get("rfid"), event.get("seq"))
                if key not in stale_keys:
                    stale_keys.add(key)
                    counters["stale_cleared"] += 1
            displayed_ids.append(event.get("dfid"))
            timestamps.append(int(event.get("ts", 0)))
        else:
            raise ValueError(f"未知事件类型 {kind!r}")
    monotonic = all(b >= a for a, b in zip(timestamps, timestamps[1:]))
    elapsed = (timestamps[-1] - timestamps[0]) if len(timestamps) >= 2 else 0
    return {
        "counters": counters,
        "commit_events": commit_count,
        "submit_events": submit_count,
        "unique_displayed_frames": len(set(displayed_ids)),
        "timestamps_monotonic": monotonic,
        "virtual_elapsed_ns": elapsed,
        "fail_submits": fail_submits,
        "stale_result_keys": len(stale_keys),
    }


def recompute_file(path: pathlib.Path) -> dict:
    return recompute(iter_events(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--expect", default="")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    log_path = pathlib.Path(args.log)
    if not log_path.is_file():
        print(f"[ERROR] 日志不存在：{log_path}", file=sys.stderr)
        return 2
    try:
        result = recompute_file(log_path)
    except ValueError as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 1

    verdict = "RECOMPUTED"
    code = 0
    if args.expect:
        expect_path = pathlib.Path(args.expect)
        if not expect_path.is_file():
            print(f"[ERROR] 期望文件不存在：{expect_path}", file=sys.stderr)
            return 2
        expected = json.loads(expect_path.read_text(encoding="utf-8"))
        expected_counters = expected.get("counters", expected)
        mismatches = {key: (expected_counters.get(key), result["counters"][key])
                      for key in COUNTER_KEYS
                      if expected_counters.get(key) != result["counters"][key]}
        if mismatches:
            verdict = "MISMATCH"
            code = 1
            result["mismatches"] = mismatches
        elif "virtual_elapsed_ns" in expected and expected["virtual_elapsed_ns"] != result["virtual_elapsed_ns"]:
            verdict = "MISMATCH"
            code = 1
            result["mismatches"] = {"virtual_elapsed_ns": (expected["virtual_elapsed_ns"],
                                                           result["virtual_elapsed_ns"])}
        else:
            verdict = "MATCHES_EXPECTED"
        result["expected_file"] = str(expect_path)
    result["verdict"] = verdict
    result["log"] = str(log_path)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())