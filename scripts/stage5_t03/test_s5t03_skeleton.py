#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线用例骨架：坐标映射 / 帧关联 / 异常与过期 / 长跑回归。

运行（真实退出码）：`python -B scripts/stage5_t03/test_s5t03_skeleton.py -v`
退出码：0 = 全部通过；1 = 存在失败/错误。

覆盖（对应 `CDX-20261022-014` §4/§5，全部**离线**）：
- 坐标映射：手算样例 + 冻结参考实现同源 + 越界裁剪/零面积 + 2 px 偶数线宽语义
- 帧关联：顺序 / 迟到 / 跳帧 / 重复 / 乱序，≥100 帧五元组按 `displayed_frame_id` 索引、语义唯一 B
- 异常与过期：`age==limit` 不过期、`limit+1` 过期、显式 `stale_flag`、每结果只计一次、
  零框 ≠ 过期、`TIMEOUT`/`ERROR`/`DROPPED` 分列、无效记录不绘制
- 长跑回归（离线虚拟时钟加速 ≥30 分钟）：每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算
- 契约完整性：`S5A-G0-v2` 未被改动、几何参考实现未分叉、既有合成源证据未被改写

硬边界：不碰硬件、不读 UART/JTAG、不跑 Vivado；结论只适用于**合成动态流**，不得升级为真实集成结论。
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
for entry in (str(REPO_ROOT), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

# 中文日志在 GBK 控制台重定向下会崩：入口统一 UTF-8（不依赖宿主 locale）
for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except (ValueError, OSError):   # pragma: no cover - 非文本流
            pass

import s5t03_display_pipeline as P  # noqa: E402
import s5t03_dynamic_stream as S  # noqa: E402

R = P.REFERENCE

PARAMS_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_offline_skeleton_params_v1.json"
CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5a_stage5_display_g0_fields.json"
BINDING_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_input_contract_binding_v1.json"
BASE_COMMIT = "654c72eb8e883b1a43fe8b6c3f073a9cb6f023b9"
UNTOUCHED_PATHS = ("report/evidence/S5-A", "report/evidence/S5-B",
                   "report/evidence/S5-C", "report/evidence/S5-T01")


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_params() -> dict:
    return json.loads(PARAMS_PATH.read_text(encoding="utf-8"))


PARAMS = load_params()
NEW = PARAMS["newly_frozen_for_skeleton_only"]
INHERIT = PARAMS["inherited_from_s5a_g0_v2"]["items"]

# 证据脚本在跑完本套件后读取的实测摘要（避免为收集数字重复跑长跑）
LAST_MIXED: dict = {}
LAST_LONG: dict = {}


def stream(mode: str, frames: int, *, seed: int | None = None, warmup: int = 0) -> list[dict]:
    return S.build_stream(mode, frames, params=PARAMS,
                          seed=NEW["seed"] if seed is None else seed,
                          frame_period_ns=NEW["long_run_virtual_frame_period_ns"],
                          warmup_frames=warmup)


def run(mode: str, frames: int, *, seed: int | None = None, warmup: int = 0):
    pipeline = P.DisplayPipeline(canvas_width=1280, canvas_height=720,
                                 input_scope_label="synthetic_dynamic_reference",
                                 params=PARAMS)
    summary = P.run_stream(pipeline, stream(mode, frames, seed=seed, warmup=warmup))
    commits = pipeline.log.commit_events()
    measured = {
        "mode": mode,
        "frames": frames,
        "seed": NEW["seed"] if seed is None else seed,
        "commit_events": summary["commit_events"],
        "events": summary["events"],
        "counters": dict(summary["counters"]),
        "virtual_elapsed_ns": (commits[-1]["overlay_commit_ns"] - commits[0]["overlay_commit_ns"]
                               if commits else 0),
    }
    if frames >= NEW["long_run_min_frames"]:
        LAST_LONG.update(measured)
    elif mode == "mixed":
        LAST_MIXED.update(measured)
    return pipeline, summary


class T01_ContractIntegrity(unittest.TestCase):
    """契约与参考实现未被改动（防止「顺手改指标」与「第二套几何」）。"""

    def test_g0_contract_bytes_unchanged(self):
        expected = PARAMS["inherited_from_s5a_g0_v2"]["contract_json_sha256"]
        self.assertEqual(sha256_file(CONTRACT_PATH), expected,
                         "S5A-G0-v2 JSON 字节被改动：本骨架不得改显示契约")

    def test_geometry_reference_not_forked(self):
        expected = PARAMS["inherited_from_s5a_g0_v2"]["geometry_reference_sha256"]
        reference_path = REPO_ROOT / PARAMS["inherited_from_s5a_g0_v2"]["geometry_reference_path"]
        self.assertEqual(sha256_file(reference_path), expected)
        self.assertIs(P.REFERENCE, R, "骨架必须直接引用冻结参考实现，不得另建几何模块")

    def test_inherited_thresholds_match_contract(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["contract_id"], "S5A-G0-v2")
        self.assertEqual(contract["stale_and_age"]["stale_age_limit_ns"], INHERIT["stale_age_limit_ns"])
        self.assertEqual(contract["overlay_layout"]["line_width_px_1080p"], INHERIT["display_line_width_px"])
        self.assertEqual(contract["scoring"]["max_outputs_per_image"], INHERIT["max_outputs_per_image"])
        self.assertEqual(contract["display_semantics"]["value"], INHERIT["display_semantics"])
        self.assertEqual(contract["overlay_layout"]["hud_fields"], INHERIT["hud_fields"])
        self.assertEqual(R.STALE_AGE_LIMIT_NS, INHERIT["stale_age_limit_ns"])
        self.assertEqual(R.STALE_AGE_LIMIT_NS, 200_000_000)
        self.assertFalse(R.is_stale(200_000_000), "age == limit 不得判过期")
        self.assertTrue(R.is_stale(200_000_001))

    def test_binding_json_declares_scope_labels(self):
        binding = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
        labels = binding["input_scope_labels"]["labels"]
        self.assertIn("camera_live_colour", labels)
        self.assertIn("camera_capture_replay_colour", labels)
        self.assertEqual(labels["camera_live_colour"]["stage4_source_kind"], "camera")
        self.assertEqual(labels["camera_capture_replay_colour"]["mapping_status"],
                         "PROPOSED_PENDING_STAGE4_G0_CONFIRMATION")
        self.assertEqual(binding["relation_to_frozen_contract"]["display_contract"], "S5A-G0-v2")
        self.assertIn("stale_age_limit_ns", binding["relation_to_frozen_contract"]["unchanged"])

    def test_existing_synthetic_evidence_untouched(self):
        command = ["git", "-C", str(REPO_ROOT), "diff", "--name-only", BASE_COMMIT, "--",
                   *UNTOUCHED_PATHS]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "",
                         f"既有合成源证据被改动：{completed.stdout.strip()}")


class T02_CoordinateMapping(unittest.TestCase):
    """坐标映射：手算样例 + 参考同源 + 裁剪/零面积 + 线宽语义。"""

    def test_hand_computed_cases_match_reference(self):
        for case in NEW["coordinate_cases"]:
            px = R.original_norm_to_display_px(case["xyxy"], 1280, 720)
            self.assertEqual(px, case["hand_computed_px"],
                             f"{case['id']}: 参考实现 {px} 与手算 {case['hand_computed_px']} 不一致")

    def test_pipeline_uses_reference_mapping(self):
        case = NEW["coordinate_cases"][1]          # C2-quarter
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        record = S.make_record(session_id=1, frame_id=3, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000,
                               result_time_ns=1_000_000_100,
                               inference_time_ns=1_000_000, state="OK",
                               detections=[S.make_detection(0, box=tuple(case["xyxy"]))])
        self.assertEqual(R.validate_result_record(record), [])
        pipeline.submit_result(record)
        event = pipeline.commit_frame(3, 1_000_000_200)["event"]
        self.assertTrue(event["drawn"])
        self.assertEqual(event["box_px"][0]["px"], case["hand_computed_px"])

    def test_geometry_resolutions_and_odd_padding(self):
        for width, height in NEW["geometry_resolutions"]:
            geom = R.letterbox_geometry(width, height, 416, 416)
            self.assertTrue(geom["new_width"] >= 1 and geom["new_height"] >= 1)
        odd = R.letterbox_geometry(683, 384, 416, 416)
        self.assertEqual((odd["new_width"], odd["new_height"]), (416, 233))
        self.assertEqual(odd["offset_y"], 91, "奇数总补边不得对称化/重新居中")
        self.assertEqual(odd["pad_bottom"], 92, "下侧补边差必须原样保留（91/92）")

    def test_edge_and_degenerate_cases(self):
        e1 = R.clip_unit_box([-0.1, -0.2, 1.1, 1.2])
        self.assertTrue(e1["clipped"] and not e1["zero_area"])
        self.assertEqual(e1["xyxy"], (0.0, 0.0, 1.0, 1.0))
        e2 = R.clip_unit_box([-0.5, -0.5, 0.0, 0.5])
        self.assertTrue(e2["clipped"] and e2["zero_area"], "裁剪后零面积必须判零面积且不绘制")
        with self.assertRaises(R.ContractViolation):
            R.clip_unit_box([0.6, 0.6, 0.4, 0.4])

    def test_border_line_width_semantics(self):
        pixels = R.border_pixel_sets(10, 10, 20, 20, R.DISPLAY_LINE_WIDTH_PX, 1280, 720)
        self.assertEqual(len(pixels), len(set(pixels)))
        self.assertEqual(list(pixels), sorted(pixels))
        for x, y in ((9, 10), (10, 10), (9, 20), (10, 20), (20, 10), (19, 10)):
            self.assertIn((x, y), pixels, "偶数线宽居中：几何线 p 占 {p-1, p}")
        clipped = R.border_pixel_sets(0, 0, 5, 5, R.DISPLAY_LINE_WIDTH_PX, 1280, 720)
        for x, y in clipped:
            self.assertTrue(0 <= x < 1280 and 0 <= y < 720, "边框像素必须钳到画布内")
        self.assertNotIn((-1, 0), clipped)

    def test_zero_area_box_not_drawn_but_counted(self):
        pipeline, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        self.assertGreaterEqual(summary["counters"]["zero_area_dropped"], 1)
        for event in pipeline.log.commit_events():
            if event["zero_area_dropped"]:
                self.assertGreaterEqual(event["boxes"], 1)


class T03_FrameAssociation(unittest.TestCase):
    """帧关联：五元组、语义唯一、显示帧号与结果帧号如实记录。"""

    def _five_tuples(self, pipeline):
        return pipeline.log.five_tuples()

    def test_sequential_120_frames(self):
        pipeline, summary = run("sequential", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        self.assertGreaterEqual(len(five), NEW["frame_association_min_frames_required"])
        for index, entry in enumerate(five):
            self.assertEqual(entry["displayed_frame_id"], index, "五元组必须可按 displayed_frame_id 索引")
            self.assertEqual(entry["result_frame_id"], index)
            self.assertEqual(entry["display_semantics"], "B_latest_result_overlay")
        self.assertEqual(len({entry["display_semantics"] for entry in five}), 1,
                         "单一证据包内 display_semantics 必须唯一")
        self.assertEqual(summary["counters"]["frames_committed"],
                         NEW["frame_association_sample_frames"])

    def test_late_results_recorded_truthfully(self):
        pipeline, _ = run("late", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        mismatches = 0
        for entry in five:
            if entry["displayed_frame_id"] >= 2:
                self.assertEqual(entry["result_frame_id"], entry["displayed_frame_id"] - 2,
                                 "结果显示 frame_id 不得被改写成显示帧号以掩盖错配")
                mismatches += 1
        self.assertEqual(mismatches, NEW["frame_association_sample_frames"] - 2)
        self.assertGreater(five[10]["age_frame_ns"], 0)

    def test_skip_mode_ages_grow_and_stale_occurs(self):
        pipeline, summary = run("skip", NEW["frame_association_sample_frames"])
        five = self._five_tuples(pipeline)
        self.assertEqual(len(five), NEW["frame_association_sample_frames"])
        self.assertGreaterEqual(summary["counters"]["stale_cleared"], 1, "空档必须触发过期且被计数")
        self.assertGreater(max(e["age_frame_ns"] for e in five), R.STALE_AGE_LIMIT_NS)

    def test_duplicate_and_out_of_order_counted(self):
        pipeline_dup, summary_dup = run("dup", NEW["stream_samples"]["dup_frames"])
        self.assertGreaterEqual(summary_dup["counters"]["duplicate_results"], 1,
                                "重复结果必须计数")
        self.assertEqual(summary_dup["counters"]["frames_committed"],
                         NEW["stream_samples"]["dup_frames"])
        pipeline_ooo, summary_ooo = run("ooo", NEW["stream_samples"]["ooo_frames"])
        self.assertGreaterEqual(summary_ooo["counters"]["out_of_order_results"], 1,
                                "乱序结果必须计数")
        self.assertEqual(len(self._five_tuples(pipeline_ooo)),
                         NEW["stream_samples"]["ooo_frames"])

    def test_duplicate_does_not_update_latest_result(self):
        """重复结果不更新最新结果：重复帧的绘制内容必须与前一帧完全相同。"""
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        record = S.make_record(session_id=1, frame_id=5, result_seq=1, sequence=1,
                               capture_time_ns=1_000_000_000, result_time_ns=1_000_000_100,
                               inference_time_ns=1_000_000, state="OK",
                               detections=[S.make_detection(0)])
        pipeline.submit_result(record)
        first = pipeline.commit_frame(5, 1_010_000_000)["event"]
        duplicate = pipeline.submit_result(dict(record))
        self.assertEqual(duplicate["outcome"], "duplicate")
        second = pipeline.commit_frame(6, 1_020_000_000)["event"]
        self.assertEqual(first["box_px"], second["box_px"], "重复结果不得改变叠加内容")
        self.assertEqual(pipeline.counters["duplicate_results"], 1)


class T04_StaleAndExceptions(unittest.TestCase):
    """过期边界与异常分列。"""

    def _pipeline_with(self, *, age_frame_ns: int, stale_flag: bool):
        pipeline = P.DisplayPipeline(input_scope_label="synthetic_dynamic_reference")
        capture = 1_000_000_000
        record = S.make_record(session_id=9, frame_id=11, result_seq=1, sequence=1,
                               capture_time_ns=capture, result_time_ns=capture,
                               inference_time_ns=1_000_000, state="OK", stale=stale_flag,
                               detections=[S.make_detection(0)])
        self.assertEqual(R.validate_result_record(record), [])
        pipeline.submit_result(record)
        return pipeline, capture

    def test_age_equals_limit_not_stale(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=R.STALE_AGE_LIMIT_NS, stale_flag=False)
        event = pipeline.commit_frame(11, capture + R.STALE_AGE_LIMIT_NS)["event"]
        self.assertFalse(event["stale_effective"], "age == limit 不得判过期")
        self.assertEqual(event["stale_reason"], R.STALE_REASON_NONE)
        self.assertTrue(event["drawn"])
        self.assertEqual(pipeline.counters["stale_cleared"], 0)

    def test_age_limit_plus_one_stale_and_counted_once(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=R.STALE_AGE_LIMIT_NS + 1, stale_flag=False)
        for frame_id in (11, 12, 13, 14, 15):
            event = pipeline.commit_frame(frame_id, capture + R.STALE_AGE_LIMIT_NS + 1)["event"]
            self.assertTrue(event["stale_effective"])
            self.assertFalse(event["drawn"])
            self.assertEqual(event["boxes"], 0)
        self.assertEqual(pipeline.counters["stale_cleared"], 1, "同一结果键只计一次")
        self.assertEqual(pipeline.counters["stale_cleared"],
                         pipeline.recompute()["counters"]["stale_cleared"])

    def test_explicit_stale_flag_with_small_age(self):
        pipeline, capture = self._pipeline_with(age_frame_ns=0, stale_flag=True)
        event = pipeline.commit_frame(11, capture + 1_000_000)["event"]
        self.assertTrue(event["stale_effective"])
        self.assertEqual(event["stale_reason"], R.STALE_REASON_FLAG)
        self.assertFalse(event["drawn"])

    def test_mixed_stream_exception_counters(self):
        pipeline, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        counters = summary["counters"]
        for key in ("zero_hand_frames", "timeouts", "error_results", "dropped_frames",
                    "invalid_records", "stale_cleared", "zero_area_dropped"):
            self.assertGreaterEqual(counters[key], 1, f"{key} 必须被计数（不得隐藏异常）")
        for event in pipeline.log.commit_events():
            if event["state"] == "NO_HAND" and not event["stale_effective"]:
                self.assertEqual(event["boxes"], 0, "NO_HAND 必须 boxes=0")
                self.assertFalse(event["drawn"], "零框是合法结果，不得绘制、也不得与过期混淆")
            if event["state"] in ("TIMEOUT", "ERROR", "DROPPED"):
                self.assertFalse(event["drawn"])
                self.assertNotEqual(event["state"], "NO_HAND", "超时/错误不得冒充零框")
        invalid_expected = len([i for i in range(NEW["stream_samples"]["mixed_frames"])
                                if i % S.MIXED_MODULUS == 30])
        self.assertEqual(counters["invalid_records"], invalid_expected,
                         "无效记录数必须与注入数一致")
        self.assertEqual(counters, pipeline.recompute()["counters"], "计数必须可由事件日志复算")

    def test_hud_thirteen_fields_and_unavailable_marked(self):
        _, summary = run("mixed", NEW["stream_samples"]["mixed_frames"])
        hud = summary["hud_last"]
        self.assertEqual(sorted(hud), sorted(INHERIT["hud_fields"]))
        self.assertEqual(len(hud), 13)
        for key in ("capture_fps", "inference_fps", "display_fps"):
            self.assertEqual(hud[key], "UNAVAILABLE", f"{key} 无实测时必须标 UNAVAILABLE，不得用 0 伪装")
        self.assertEqual(hud["display_semantics"], "B_latest_result_overlay")


class T05_LongRunVirtual(unittest.TestCase):
    """长跑回归：离线虚拟时钟加速 ≥30 分钟（**不是**板上耐久）。"""

    def test_long_run_virtual_30min_no_deadlock(self):
        frames = NEW["long_run_min_frames"]
        pipeline, summary = run("mixed", frames)
        commits = pipeline.log.commit_events()
        self.assertEqual(len(commits), frames, "每显示帧必须恰好一条提交事件（缺事件即死锁）")
        self.assertEqual(summary["commit_events"], frames)
        self.assertEqual(len(pipeline.log.five_tuples()), frames)
        first, last = commits[0]["overlay_commit_ns"], commits[-1]["overlay_commit_ns"]
        elapsed = last - first
        self.assertGreaterEqual(elapsed, NEW["long_run_virtual_duration_ns"],
                                f"虚拟时长 {elapsed} ns 未达 30 分钟")
        previous = None
        for event in commits:
            if previous is not None:
                self.assertGreaterEqual(event["overlay_commit_ns"], previous,
                                        "提交时间戳必须单调不减")
            previous = event["overlay_commit_ns"]
        self.assertEqual(summary["counters"]["frames_committed"], frames)
        self.assertEqual(summary["counters"], pipeline.recompute()["counters"],
                         "长跑计数必须可由事件日志完全复算")
        self.assertGreaterEqual(summary["counters"]["overlay_drawn_frames"], 1)
        self.assertEqual(pipeline.counters["duplicate_results"],
                         pipeline.log.recompute()["counters"]["duplicate_results"])


class T06_StreamSchema(unittest.TestCase):
    """合成流自身必须符合被消费记录 schema（除刻意注入的无效记录）。"""

    def test_all_modes_conform_except_injected_invalid(self):
        for mode, frames in (("sequential", NEW["frame_association_sample_frames"]),
                             ("skip", NEW["stream_samples"]["skip_frames"]),
                             ("late", NEW["stream_samples"]["late_frames"]),
                             ("dup", NEW["stream_samples"]["dup_frames"]),
                             ("ooo", NEW["stream_samples"]["ooo_frames"])):
            for step in stream(mode, frames):
                for record in step["results"]:
                    self.assertEqual(R.validate_result_record(record), [],
                                     f"{mode}: 合成流记录必须通过冻结 schema 校验")
                    self.assertEqual(record["source_kind"], "synthetic")
                    self.assertFalse(record["capture_time_available"])
                    self.assertIn("capture_time_ns", record["unavailable_fields"])
        invalid_seen = 0
        for step in stream("mixed", NEW["stream_samples"]["mixed_frames"]):
            for record in step["results"]:
                problems = R.validate_result_record(record)
                if problems:
                    invalid_seen += 1
                    self.assertEqual(record["state"], "NO_HAND")
        self.assertEqual(invalid_seen,
                         len([i for i in range(NEW["stream_samples"]["mixed_frames"])
                              if i % S.MIXED_MODULUS == 30]))

    def test_stream_is_deterministic_for_seed(self):
        first = stream("mixed", 64)
        second = stream("mixed", 64)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        other = stream("mixed", 64, seed=NEW["seed"] + 1)
        self.assertNotEqual(json.dumps(first, sort_keys=True), json.dumps(other, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)