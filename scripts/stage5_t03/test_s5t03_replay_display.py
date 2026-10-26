#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线 replay/display 渲染路径测试（合成流；不接板卡、不联网）。

覆盖要点
========
1. 渲染**确定性**：同一决策两次栅格化必须字节一致（PNG SHA 相同）；
2. **单源几何**：边框像素集一律等于 `R.border_pixel_sets` 与流水线 `border_pixels`（禁止第二套几何）；
3. **语义不变量**：过期 ⇒ 不画框；`NO_HAND` 合法零框且非过期；零面积不绘制但计数；
4. **过期边界**：`age==limit` 不过期、`limit+1` 过期、显式 `stale_flag` 过期；
5. **标签锚点**：越界翻转/钳位规则在边界输入下成立；
6. **产物结构与诚实标注**：`results.json` 为权威、`not_run` 含真实回放、状态标 `PRELIMINARY`；
7. **输入帧绑定**：阶段3 绑定 JSON 的哈希不符必须抛错（不得静默用错帧）；
8. **无板卡/无串口依赖**：源码不引入 serial/串口/硬件会话。

运行：python -B -m unittest scripts.stage5_t03.test_s5t03_replay_display -v
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.s5t03_display_pipeline as P  # noqa: E402
import scripts.stage5_t03.s5t03_dynamic_stream as S  # noqa: E402
import scripts.stage5_t03.s5t03_render as RD  # noqa: E402
import scripts.stage5_t03.s5t03_replay_display as REP  # noqa: E402
import verification.s5_display_geometry_reference as R  # noqa: E402

PARAMS = REP.load_params()
PERIOD_NS = int(PARAMS["newly_frozen_for_skeleton_only"]["long_run_virtual_frame_period_ns"])
SEED = int(PARAMS["newly_frozen_for_skeleton_only"]["seed"])
STAGE3_BINDING = pathlib.Path(
    r"D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json")


def run_small(mode: str = "mixed", frames: int = 32, *, canvas: tuple[int, int] = (1280, 720),
              warmup: int = 0):
    """跑一个小流：返回 (pipeline, events, five_tuples)。"""
    steps = S.build_stream(mode, frames, params=PARAMS, seed=SEED, frame_period_ns=PERIOD_NS,
                           warmup_frames=warmup)
    pipeline = P.DisplayPipeline(canvas_width=canvas[0], canvas_height=canvas[1],
                                 input_scope_label=REP.INPUT_SCOPE_LABEL, params=PARAMS)
    events, five = [], []
    for step in steps:
        for record in step.get("results") or []:
            pipeline.submit_result(record)
        committed = pipeline.commit_frame(int(step["displayed_frame_id"]), int(step["overlay_commit_ns"]),
                                          warmup=bool(step.get("warmup", False)))
        events.append(committed["event"])
        five.append(committed["five_tuple"])
    pipeline.assert_recomputable()
    return pipeline, events, five


@unittest.skipUnless(RD.PIL_AVAILABLE, f"Pillow 不可用：{RD.PIL_IMPORT_ERROR}")
class T_Render(unittest.TestCase):
    def test_01_render_is_deterministic(self) -> None:
        """同一决策两次渲染 → PNG 字节与 SHA 完全一致。"""
        _, events, _ = run_small()
        drawn = next(e for e in events if e["drawn"])
        font, _ = RD.load_font(RD.font_size_px(720))
        first = RD.png_bytes(RD.render_frame(drawn, canvas_width=1280, canvas_height=720, font=font)[0])
        second = RD.png_bytes(RD.render_frame(drawn, canvas_width=1280, canvas_height=720, font=font)[0])
        self.assertEqual(hashlib.sha256(first).hexdigest(), hashlib.sha256(second).hexdigest())

    def test_02_border_pixels_single_source(self) -> None:
        """渲染的边框像素集必须与冻结参考逐框一致（流水线 border_pixels 亦同源）。"""
        _, events, _ = run_small()
        checked = 0
        for event in events:
            for box in event.get("box_px") or []:
                px = box["px"]
                expected = R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]), int(px["y2"]),
                                               R.DISPLAY_LINE_WIDTH_PX, 1280, 720)
                self.assertEqual(len(expected), int(box["border_pixels"]))
                checked += 1
        self.assertGreater(checked, 0, "样本流必须至少绘制过一个框")

    def test_02b_rendered_pixels_exactly_equal_reference_border_sets(self) -> None:
        """**像素级**单源断言：只画边框时，非背景像素集合必须**恰好等于** `R.border_pixel_sets`。

        判别力（N1/复审 V1）：把渲染层换成自写线宽（例如 1 px）或自写取整，本用例必须失败。
        """
        _, events, _ = run_small()
        drawn = [e for e in events if e["drawn"]]
        self.assertTrue(drawn, "样本流必须有绘制帧")
        background_rgb = (7, 7, 7)
        font, _ = RD.load_font(RD.font_size_px(720))
        for event in drawn[:6]:
            background = RD.Image.new("RGB", (1280, 720), background_rgb)
            image, stats = RD.render_frame(event, canvas_width=1280, canvas_height=720,
                                           background=background, hud=None, font=font,
                                           draw_hud=False, draw_labels=False)
            self.assertEqual(stats["labels_drawn"], 0)
            pixels = image.load()
            rendered = {(x, y) for x in range(1280) for y in range(720) if pixels[x, y] != background_rgb}
            expected: set[tuple[int, int]] = set()
            for box in event["box_px"]:
                px = box["px"]
                expected |= set(R.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]),
                                                    int(px["y2"]), R.DISPLAY_LINE_WIDTH_PX, 1280, 720))
            self.assertEqual(rendered, expected,
                             f"渲染像素与冻结参考不一致：多 {len(rendered - expected)} px / 少 {len(expected - rendered)} px")

    def test_03b_font_identity_is_honest(self) -> None:
        """字体诚实标注（N1 判别力）：可用字体 ⇒ `scaled=true` 且尺寸正确；**无字体 ⇒ 必须 scaled=false**。"""
        size = RD.font_size_px(720)
        font, info = RD.load_font(size)
        if info["scaled"]:
            self.assertEqual(info["font_size_px"], size)
            self.assertIsNotNone(info["font_sha256"])
        else:
            self.assertIsNone(info["font_size_px"])
        original = RD.FONT_CANDIDATES
        try:
            RD.FONT_CANDIDATES = ()                      # 强制回退路径
            _, fallback = RD.load_font(size)
            self.assertFalse(fallback["scaled"], "回退字体不得声称 scaled=true")
            self.assertIsNone(fallback["font_size_px"], "回退字体不得声称满足字号规格")
            self.assertIn("note", fallback)
        finally:
            RD.FONT_CANDIDATES = original

    def test_03_render_stats_match_decision(self) -> None:
        """渲染统计必须与决策一致：框数、HUD 行数、类色表命中 UR-3。"""
        _, events, _ = run_small()
        font, info = RD.load_font(RD.font_size_px(720))
        self.assertIn("scaled", info)
        for event in events:
            hud = {"capture_fps": "UNAVAILABLE", "boxes": event["boxes"]}
            image, stats = RD.render_frame(event, canvas_width=1280, canvas_height=720, hud=hud, font=font)
            self.assertEqual(stats["boxes_drawn"], int(event["boxes"]))
            self.assertEqual(stats["hud_lines_drawn"], 2)      # 本用例只传 2 个字段（真实调用传 13）
            self.assertEqual(image.size, (1280, 720))
            for name in stats["classes_drawn"]:
                self.assertIn(name, RD.CLASS_COLORS_RGB)

    def test_04_stale_and_zero_hand_invariants(self) -> None:
        """过期 ⇒ 不画框；NO_HAND ⇒ 零框且非过期（不得把 NO_HAND 当过期）。"""
        _, events, _ = run_small()
        for event in events:
            if event["stale_effective"]:
                self.assertEqual(int(event["boxes"]), 0, "过期帧不得绘制边框")
                self.assertFalse(event["drawn"])
            if event["state"] == "NO_HAND" and not event["stale_effective"]:
                self.assertEqual(int(event["boxes"]), 0)
        zero_hand = [e for e in events if e["state"] == "NO_HAND" and not e["stale_effective"]]
        self.assertTrue(zero_hand, "mixed 流应包含合法零框帧")

    def test_05_boundary_cases(self) -> None:
        """三例过期边界：`==limit` 不过期、`limit+1` 过期、显式标志过期。"""
        for case in REP.boundary_cases():
            pipeline = P.DisplayPipeline(canvas_width=1280, canvas_height=720, params=PARAMS)
            pipeline.submit_result(case["record"])
            event = pipeline.commit_frame(0, case["commit_ns"])["event"]
            self.assertEqual(bool(event["stale_effective"]), bool(case["expect_stale"]), case["case_id"])
            self.assertEqual(int(event["age_frame_ns"]), int(case["expect_age_frame_ns"]), case["case_id"])

    def test_06_label_anchor_rules(self) -> None:
        """标签锚点：正常在框外上方；顶部越界翻到框内；再越界钳入安全区。"""
        safe = RD.safe_area_px(720)
        x, y, place = RD.label_anchor({"x1": 100, "y1": 100, "x2": 200, "y2": 200}, 60, 16,
                                      canvas_width=1280, canvas_height=720, safe=safe)
        self.assertEqual((x, y), (100, 100 - 16 - RD.LABEL_GAP_PX))
        self.assertEqual(place, "outside_top_left")
        _, y2, place2 = RD.label_anchor({"x1": 100, "y1": 0, "x2": 200, "y2": 50}, 60, 16,
                                        canvas_width=1280, canvas_height=720, safe=safe)
        self.assertTrue(place2.startswith("inside_top_left"))
        self.assertEqual(y2, 0 + RD.LABEL_GAP_PX)
        x3, y3, place3 = RD.label_anchor({"x1": 1275, "y1": 715, "x2": 1279, "y2": 719}, 60, 16,
                                         canvas_width=1280, canvas_height=720, safe=safe)
        self.assertLessEqual(x3 + 60, 1280 - safe)
        self.assertGreaterEqual(x3, safe)
        self.assertGreaterEqual(y3, safe)
        self.assertIn("clamped", place3)

    def test_07_keyframe_selection_bounded(self) -> None:
        """关键帧选择有界且必含首末帧。"""
        _, events, _ = run_small(frames=64)
        picked = REP.select_keyframes(events, keyframe_max=8)
        self.assertLessEqual(len(picked), 8)
        self.assertIn(0, picked)
        self.assertIn(len(events) - 1, picked)

    def test_08_five_tuple_and_semantics(self) -> None:
        """五元组齐全、语义唯一 B、displayed 与 result 可不同（如实记录）。"""
        _, events, five = run_small(frames=24)
        self.assertEqual(len(five), len(events))
        for item in five:
            self.assertEqual(set(item), {"displayed_frame_id", "result_frame_id", "age_result_ns",
                                         "age_frame_ns", "display_semantics"})
            self.assertEqual(item["display_semantics"], R.DISPLAY_SEMANTICS)
        self.assertTrue(all(e["age_frame_ns"] >= e["age_result_ns"] for e in events if e["age_frame_ns"]))


class T_ReplayArtifacts(unittest.TestCase):
    def test_10_end_to_end_artifacts_and_labels(self) -> None:
        """端到端小跑：产物齐全、JSON 为权威、诚实标注（合成/初稿/真实回放 NOT_RUN）。"""
        with tempfile.TemporaryDirectory(prefix="s5t03_replay_") as tmp:
            out = pathlib.Path(tmp) / "run"
            code = REP.run_replay(out_dir=out, mode="mixed", frames=32, seed=SEED, canvas=(1280, 720),
                                  background_path=None, keyframe_max=6, want_demo=False)
            self.assertEqual(code, 0)
            for name in ("results.json", "frame_assertions.jsonl", "manifest.json"):
                self.assertTrue((out / name).is_file(), f"缺产物 {name}")
            results = json.loads((out / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(results["input_scope_label"], REP.INPUT_SCOPE_LABEL)
            self.assertEqual(results["status"], REP.STATUS_LABEL)
            self.assertTrue(results["recompute_matches_online"])
            self.assertTrue(results["checks"]["passed"], results["checks"]["failures"])
            self.assertTrue(any("真实回放" in item for item in results["not_run"]))
            self.assertTrue(any("合成" in item for item in results["limitations"]))
            self.assertEqual(len(results["hud_last"]), 13)
            lines = (out / "frame_assertions.jsonl").read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 32)
            first = json.loads(lines[0])
            for key in ("displayed_frame_id", "result_frame_id", "result_seq", "coordinate_mapping",
                        "seed", "deterministic_params", "checks", "input_scope_label"):
                self.assertIn(key, first)
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("geometry_reference", manifest["tools"])
            self.assertEqual(manifest["tools"]["geometry_reference"]["contract_id"], R.CONTRACT_ID)
            self.assertTrue(any(entry["path"].endswith("results.json") for entry in manifest["files"]))
            self.assertIn("scope_statement", manifest)

    def test_11_demo_is_marked_demo_only_or_not_run(self) -> None:
        """未请求 demo 时必须显式 NOT_RUN 且标 demo_only（不得静默缺失）。"""
        with tempfile.TemporaryDirectory(prefix="s5t03_replay_demo_") as tmp:
            out = pathlib.Path(tmp) / "run"
            REP.run_replay(out_dir=out, mode="sequential", frames=12, seed=SEED, canvas=(1280, 720),
                           background_path=None, keyframe_max=4, want_demo=False)
            results = json.loads((out / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(results["demo"]["status"], "NOT_RUN")
            self.assertTrue(results["demo"]["demo_only"])


    def test_12_reject_tags_match_actual_outcomes(self) -> None:
        """N2 判别力（端到端）：关键帧文件名里的 `rejected_<kind>` 必须对应**实际发生**的 FAIL 类型。

        复审 N2 的原始缺陷：本次 `duplicate_frame_id_results=0`，却出现 `…_rejected_duplicate_frame_id` 文件名。
        """
        with tempfile.TemporaryDirectory(prefix="s5t03_rej_") as tmp:
            out = pathlib.Path(tmp) / "run"
            code = REP.run_replay(out_dir=out, mode="mixed", frames=64, seed=SEED, canvas=(1280, 720),
                                  background_path=None, keyframe_max=24, want_demo=False)
            self.assertEqual(code, 0)
            results = json.loads((out / "results.json").read_text(encoding="utf-8"))
            fail_kinds = {str(v["outcome"]) for v in results["submit_verdicts"] if v["verdict"] == "FAIL"}
            self.assertTrue(fail_kinds, "mixed 流应存在真实被拒提交")
            self.assertNotIn("duplicate_frame_id", fail_kinds, "本流不应出现等价 frame_id 拒绝（用于判别误标）")
            tagged = {kind for name in sorted(q.name for q in (out / "keyframes").glob("*.png"))
                      for kind in re.findall(r"rejected_([a-z_]+?)(?:\+|\.png)", name)}
            for name in sorted(q.name for q in (out / "keyframes").glob("*.png")):
                for kind in re.findall(r"rejected_([a-z_]+?)(?:\+|\.png)", name):
                    self.assertIn(kind, fail_kinds, f"关键帧 {name} 标注了未发生的拒绝类型 {kind}")
            # 双向（复审观察 3）：实际发生的每种 FAIL 类型都必须在**某个**关键帧名里出现（有界采样下成立）
            if len(fail_kinds) <= 24:
                self.assertEqual(tagged, set(fail_kinds), f"漏标：发生了 {fail_kinds}，标注仅 {tagged}")

    def test_13_event_log_written_and_reject_reason_present(self) -> None:
        """N3：帧级事件日志必须落盘；FAIL 提交必须带非空 `reject_reason`（管线来源或显式标注派生）。"""
        with tempfile.TemporaryDirectory(prefix="s5t03_log_") as tmp:
            out = pathlib.Path(tmp) / "run"
            code = REP.run_replay(out_dir=out, mode="mixed", frames=64, seed=SEED, canvas=(1280, 720),
                                  background_path=None, keyframe_max=6, want_demo=False)
            self.assertEqual(code, 0)
            logs = sorted((out / "logs").glob("events_*.jsonl"))
            self.assertTrue(logs, "必须落盘帧级事件日志")
            lines = logs[0].read_text(encoding="utf-8").strip().splitlines()
            commits = sum(1 for line in lines if json.loads(line).get("t") == "commit")
            self.assertEqual(commits, 64, "每个显示帧必须恰好一条 commit 事件")
            results = json.loads((out / "results.json").read_text(encoding="utf-8"))
            fails = [v for v in results["submit_verdicts"] if v["verdict"] == "FAIL"]
            self.assertTrue(fails, "mixed 流应包含被拒提交")
            self.assertTrue(all(v.get("reject_reason") for v in fails), "FAIL 提交必须带 reject_reason")
            self.assertTrue(all(v.get("reject_reason_source") for v in fails), "必须标注原因来源")
            self.assertIn("logs", results)
            self.assertIn("font", json.loads((out / "manifest.json").read_text(encoding="utf-8"))["render"])


    def test_14_missing_pillow_is_reported_as_failure(self) -> None:
        """复审观察 1（fail-open 关闭）：缺渲染依赖时**不得**报 `passed=true`。"""
        original = RD.PIL_AVAILABLE
        try:
            RD.PIL_AVAILABLE = False
            with tempfile.TemporaryDirectory(prefix="s5t03_nopil_") as tmp:
                out = pathlib.Path(tmp) / "run"
                code = REP.run_replay(out_dir=out, mode="mixed", frames=16, seed=SEED, canvas=(1280, 720),
                                      background_path=None, keyframe_max=4, want_demo=False)
                results = json.loads((out / "results.json").read_text(encoding="utf-8"))
                self.assertEqual(code, 1, "缺 Pillow 必须 exit 1")
                self.assertFalse(results["checks"]["passed"], "不得把缺依赖报成通过")
                self.assertTrue(any("render_unavailable" in item for item in results["checks"]["failures"]),
                                results["checks"]["failures"])
        finally:
            RD.PIL_AVAILABLE = original


class T_Stage3Binding(unittest.TestCase):
    def test_20_binding_hash_mismatch_raises(self) -> None:
        """绑定 JSON 的固定帧哈希不符 ⇒ 必须抛错（不得静默用错帧）。"""
        if not STAGE3_BINDING.is_file():
            self.skipTest(f"阶段3 绑定 JSON 不存在：{STAGE3_BINDING}")
        binding = json.loads(STAGE3_BINDING.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="s5t03_bind_") as tmp:
            bad = dict(binding)
            bad["source_frame_sha256"] = "0" * 64
            path = pathlib.Path(tmp) / "bad_binding.json"
            path.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                REP.load_stage3_frame(path)

    def test_21_binding_loads_expected_frame(self) -> None:
        """正常绑定：装载出的图像尺寸与像素格式按绑定声明，且哈希与声明一致。"""
        if not STAGE3_BINDING.is_file():
            self.skipTest(f"阶段3 绑定 JSON 不存在：{STAGE3_BINDING}")
        if not RD.PIL_AVAILABLE:
            self.skipTest("Pillow 不可用")
        image, info = REP.load_stage3_frame(STAGE3_BINDING)
        self.assertEqual(list(image.size), [int(info["background_size"][0]), int(info["background_size"][1])])
        self.assertEqual(info["background"], "stage3_fixed_frame_input_only")
        self.assertEqual(info["input_scope"], "input_frame_only__results_are_synthetic")
        self.assertEqual(len(info["background_sha256"]), 64)


class T_NoHardwareDependency(unittest.TestCase):
    def test_30_no_board_or_serial_dependency(self) -> None:
        """渲染/驱动源码不得**引入**串口或硬件会话依赖（注释里提到板卡不算依赖）。"""
        for name in ("s5t03_render.py", "s5t03_replay_display.py"):
            source = (REPO_ROOT / "scripts/stage5_t03" / name).read_text(encoding="utf-8").lower()
            for forbidden_import in ("import serial", "import pyserial", "import pyvisa", "import usb"):
                self.assertNotIn(forbidden_import, source, f"{name} 不应引入 {forbidden_import}")
            for forbidden_call in ('["hw_server"', '["xsdb"', '["vivado"', '["xsct"', "'hw_server'", "'xsdb'"):
                self.assertNotIn(forbidden_call, source, f"{name} 不应调用硬件工具 {forbidden_call}")


if __name__ == "__main__":
    unittest.main(verbosity=2)