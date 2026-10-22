"""S5-B 离线渲染/叠框自测工具的单元测试（unittest）。

覆盖范围（每个用例组 ≥1 个专门测试类）：
- T5-01 非方形/补边/画布不拉伸；T5-02 边缘框/越界/裁剪零面积/退化几何；
- T5-03 多框与零框；T5-04 过期清除；T5-05 S4-C 台账五元组；
- ≥3 个**手算样例**（算式写在注释里，并与十进制字面量交叉核对）；
- 冻结 `border_pixel_sets` 的独立手算对拍；
- 库内端到端：CLI 退出码 0/1/2、RunId 保护、双 pass 确定性、用词扫描零命中。

测试只写入 `tmp/5/S5-B/unittest/**`，不触碰 `report/evidence/**`（那由 run_s5b_evidence.py 产生）。
"""

from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import render_s5b_overlay as R  # noqa: E402

REFERENCE = R.load_python_module(REPO_ROOT / R.REFERENCE_REL, "s5_reference_ut")
D2 = R.load_python_module(REPO_ROOT / R.D2_REFERENCE_REL, "s1_t02_d2_ut")
CONTRACT = json.loads((REPO_ROOT / R.CONTRACT_REL).read_text(encoding="utf-8"))

TMP_ROOT = REPO_ROOT / "tmp" / "5" / "S5-B" / "unittest"

# 禁用 token 在测试源码内同样以拆分拼接构造，避免测试文件自触发扫描
FORBIDDEN_TOKENS = tuple(R.FORBIDDEN_SCORE_TOKENS) + tuple(R.FORBIDDEN_CLAIM_TOKENS)


def case_by_id(case_id: str) -> dict:
    for spec in R.case_table():
        if spec["case_id"] == case_id:
            return spec
    raise KeyError(case_id)


class TestT5_00ContractIdentity(unittest.TestCase):
    """契约身份与冻结常量一致性（所有用例组的前置）。"""

    def test_contract_id_and_status(self):
        self.assertEqual(REFERENCE.CONTRACT_ID, "S5A-G0-v2")
        self.assertEqual(REFERENCE.CONTRACT_ID, CONTRACT["contract_id"])
        self.assertEqual(CONTRACT["geometry"]["rounding_rule_id"], REFERENCE.ROUNDING_RULE)

    def test_hud_fields_and_thresholds_single_source(self):
        self.assertEqual(tuple(CONTRACT["overlay_layout"]["hud_fields"]), R.REQUIRED_HUD_FIELDS)
        self.assertEqual(REFERENCE.HUD_FIELDS, R.REQUIRED_HUD_FIELDS)
        self.assertEqual(CONTRACT["scoring"]["score_threshold"], REFERENCE.SCORE_THRESHOLD)
        self.assertEqual(CONTRACT["scoring"]["nms_iou"], REFERENCE.NMS_IOU)
        self.assertEqual(CONTRACT["scoring"]["max_outputs_per_image"], REFERENCE.MAX_OUTPUTS_PER_IMAGE)
        self.assertEqual(tuple(CONTRACT["scoring"]["class_order"]), REFERENCE.CLASS_ORDER)
        self.assertEqual(CONTRACT["overlay_layout"]["line_width_px_1080p"],
                         REFERENCE.DISPLAY_LINE_WIDTH_PX)

    def test_stale_limit_single_source(self):
        self.assertEqual(CONTRACT["stale_and_age"]["stale_age_limit_ns"],
                         REFERENCE.STALE_AGE_LIMIT_NS)
        self.assertEqual(REFERENCE.STALE_AGE_LIMIT_NS, 200_000_000)

    def test_display_semantics_single_value(self):
        self.assertEqual(CONTRACT["display_semantics"]["value"], REFERENCE.DISPLAY_SEMANTICS)
        self.assertEqual(REFERENCE.DISPLAY_SEMANTICS, "B_latest_result_overlay")

    def test_every_case_group_has_dedicated_test_class(self):
        groups = {spec["group"] for spec in R.case_table()}
        class_names = [name for name in globals() if name.startswith("Test")]
        for group in sorted(groups):
            prefix = "Test" + group.replace("-", "_")
            with self.subTest(group=group):
                self.assertTrue(any(name.startswith(prefix) for name in class_names),
                                f"{group} 缺少专门测试类（前缀 {prefix}）：{sorted(class_names)}")


class TestT5_01NonSquareGeometry(unittest.TestCase):
    """T5-01：非方形/竖屏/奇数宽/方形无补边/画布整数倍不拉伸。"""

    def test_landscape_and_portrait_geometry(self):
        landscape = REFERENCE.letterbox_geometry(1280, 720, 416, 416)
        self.assertEqual((landscape["new_width"], landscape["new_height"]), (416, 234))
        self.assertEqual((landscape["offset_x"], landscape["offset_y"]), (0, 91))
        self.assertEqual((landscape["pad_right"], landscape["pad_bottom"]), (0, 91))
        portrait = REFERENCE.letterbox_geometry(720, 1280, 416, 416)
        self.assertEqual((portrait["new_width"], portrait["new_height"]), (234, 416))
        self.assertEqual((portrait["offset_x"], portrait["offset_y"]), (91, 0))

    def test_square_640_no_padding(self):
        geom = REFERENCE.letterbox_geometry(640, 640, 416, 416)
        self.assertEqual((geom["new_width"], geom["new_height"]), (416, 416))
        self.assertEqual((geom["offset_x"], geom["offset_y"], geom["pad_right"],
                          geom["pad_bottom"]), (0, 0, 0, 0))
        self.assertFalse(geom["asymmetric_padding"])

    def test_odd_width_683x384_asymmetric_padding_preserved(self):
        geom = REFERENCE.letterbox_geometry(683, 384, 416, 416)
        self.assertEqual((geom["new_width"], geom["new_height"]), (416, 233))
        self.assertEqual(geom["offset_y"], 91)
        self.assertEqual(geom["pad_bottom"], 92)
        self.assertTrue(geom["asymmetric_padding"])
        # 未被对称化：上 91 / 下 92，且 91 + 233 + 92 = 416
        self.assertNotEqual(geom["offset_y"], geom["pad_bottom"])
        self.assertEqual(geom["offset_y"] + geom["new_height"] + geom["pad_bottom"], 416)
        # 与 D2 冻结几何逐值一致（显示层与 D2 同源）
        d2_geom = D2.letterbox_geometry(683, 384, 416, 416)
        for key in ("new_width", "new_height", "offset_x", "offset_y"):
            self.assertEqual(geom[key], d2_geom[key], key)

    def test_all_case_geometries_match_hand_and_d2(self):
        for spec in R.case_table():
            if spec["kind"] != "synthetic" or spec["expects_degenerate"]:
                continue
            with self.subTest(case=spec["case_id"]):
                geom = REFERENCE.letterbox_geometry(spec["src_w"], spec["src_h"], 416, 416)
                hand = R.hand_geometry(spec["src_w"], spec["src_h"])
                d2_geom = D2.letterbox_geometry(spec["src_w"], spec["src_h"], 416, 416)
                for key in ("new_width", "new_height", "offset_x", "offset_y", "pad_right",
                            "pad_bottom", "asymmetric_padding"):
                    self.assertEqual(geom[key], hand[key], key)
                for key in ("new_width", "new_height", "offset_x", "offset_y"):
                    self.assertEqual(geom[key], d2_geom[key], key)

    def test_canvas_fit_integer_multiple_no_stretch(self):
        fit = REFERENCE.canvas_fit(683, 384, 1920, 1080)
        self.assertEqual(fit, {"scale_k": 2, "drawn_width": 1366, "drawn_height": 768,
                               "offset_x": 277, "offset_y": 156})
        k = fit["scale_k"]
        self.assertEqual(fit["drawn_width"] / 683, k)
        self.assertEqual(fit["drawn_height"] / 384, k)
        fit1 = REFERENCE.canvas_fit(1280, 720, 1920, 1080)
        self.assertEqual(fit1, {"scale_k": 1, "drawn_width": 1280, "drawn_height": 720,
                                "offset_x": 320, "offset_y": 180})

    def test_canvas_fit_refuses_when_smaller_than_source(self):
        # 竖屏 720×1280 放不进 1920×1080（整数倍 k=0）：必须显式报错而不是偷偷拉伸
        with self.assertRaises(REFERENCE.ContractViolation):
            REFERENCE.canvas_fit(720, 1280, 1920, 1080)

    def test_letterbox_image_geometry_same_source_from_d2(self):
        """正向 letterbox 图像只用 D2 冻结实现；补边常量 128、四角端点对齐、scale 同源。"""
        src_w, src_h = 683, 384
        geometry = REFERENCE.letterbox_geometry(src_w, src_h, 416, 416)
        source = R.synth_frame(src_w, src_h, R.DEFAULT_SEED, 2)
        rgb = [[[int(px) for px in source[y, x]] for x in range(src_w)] for y in range(src_h)]
        boxed = D2.letterbox_rgb_uint8(rgb, 416, 416)
        new_w, new_h = geometry["new_width"], geometry["new_height"]
        off_x, off_y = geometry["offset_x"], geometry["offset_y"]
        for y in range(416):
            for x in range(416):
                inside = off_y <= y < off_y + new_h and off_x <= x < off_x + new_w
                if not inside:
                    self.assertEqual(boxed[y][x], [128.0, 128.0, 128.0], (x, y))
        self.assertEqual(boxed[off_y][off_x], [float(v) for v in source[0, 0]])
        self.assertEqual(boxed[off_y + new_h - 1][off_x + new_w - 1],
                         [float(v) for v in source[src_h - 1, src_w - 1]])
        w_scale_d2 = (src_w - 1) / (new_w - 1)
        for ix in (0, 1, new_w // 2, new_w - 1):
            continuous = (ix / 416 * 416 - off_x) * geometry["w_scale"]
            self.assertAlmostEqual(continuous, ix * w_scale_d2, places=12)


class TestT5_01HandComputedSamples(unittest.TestCase):
    """≥3 个手算样例：算式写在注释里，并与十进制字面量交叉核对（容限 1e-9）。"""

    def test_HS1_683x384_odd_padding(self):
        # 手算推导（683×384 → new 416×233、offset (0, 91)）：
        #   x_r = u*416 - off_x；x_px = x_r*(683-1)/(416-1)；u_orig = x_px/(683-1) = x_r/(416-1)
        #   逐分量：x1 = (0.25*416 - 0)/415；y1 = (0.50*416 - 91)/232；
        #           x2 = (0.75*416 - 0)/415；y2 = (0.75*416 - 91)/232
        expected = ((0.25 * 416 - 0) / (416 - 1), (0.50 * 416 - 91) / (233 - 1),
                    (0.75 * 416 - 0) / (416 - 1), (0.75 * 416 - 91) / (233 - 1))
        literals = (0.2506024096385542, 0.5043103448275862, 0.7518072289156626,
                    0.9525862068965517)
        geom = REFERENCE.letterbox_geometry(683, 384, 416, 416)
        self.assertEqual((geom["new_width"], geom["new_height"], geom["offset_x"],
                          geom["offset_y"]), (416, 233, 0, 91))
        got = REFERENCE.network_norm_to_original_norm((0.25, 0.50, 0.75, 0.75), geom)
        for index, (value, literal) in enumerate(zip(got, literals)):
            self.assertAlmostEqual(value, literal, places=9, msg=f"分量 {index}")
            self.assertAlmostEqual(value, expected[index], places=9, msg=f"算式 {index}")

    def test_HS2_1280x720_network_boundary(self):
        # 手算（1280×720 → new 416×234、offset (0, 91)）：
        #   x1 = (0.0*416 - 0)/415 = 0
        #   y1 = (0.25*416 - 91)/233 = 13/233
        #   x2 = (1.0*416 - 0)/415 = 416/415 ≈ 1.0024096…（端点对齐下略超 1，显示层必须裁剪）
        #   y2 = (0.75*416 - 91)/233 = 221/233
        expected = ((0.0 * 416 - 0) / 415, (0.25 * 416 - 91) / 233,
                    (1.0 * 416 - 0) / 415, (0.75 * 416 - 91) / 233)
        literals = (0.0, 0.055793991416309012, 1.0024096385542168, 0.9484978540772532)
        geom = REFERENCE.letterbox_geometry(1280, 720, 416, 416)
        got = REFERENCE.network_norm_to_original_norm((0.0, 0.25, 1.0, 0.75), geom)
        for index, (value, literal) in enumerate(zip(got, literals)):
            self.assertAlmostEqual(value, literal, places=9, msg=f"分量 {index}")
            self.assertAlmostEqual(value, expected[index], places=9, msg=f"算式 {index}")
        self.assertGreater(got[2], 1.0)          # 网络边界反算略超 1
        clipped = REFERENCE.clip_unit_box(got)
        self.assertTrue(clipped["clipped"])
        self.assertFalse(clipped["zero_area"])
        self.assertEqual(clipped["xyxy"][2], 1.0)

    def test_HS3_1440x1920_no_early_rounding(self):
        # 手算（1440×1920 → new 312×416、offset (52, 0)）：
        #   x1 = (0.50*416 - 52)/311 = 156/311；y1 = (0.10*416 - 0)/415 = 41.6/415
        #   x2 = (0.60*416 - 52)/311 = 197.6/311；y2 = (0.20*416 - 0)/415 = 83.2/415
        # 其中 41.6、197.6、83.2 为非整数：若提前取整即与手算不符
        expected = ((0.50 * 416 - 52) / (312 - 1), (0.10 * 416 - 0) / (416 - 1),
                    (0.60 * 416 - 52) / (312 - 1), (0.20 * 416 - 0) / (416 - 1))
        literals = (0.5016077170418006, 0.10024096385542168, 0.6353697749196141,
                    0.20048192771084338)
        geom = REFERENCE.letterbox_geometry(1440, 1920, 416, 416)
        self.assertEqual((geom["new_width"], geom["new_height"], geom["offset_x"]),
                         (312, 416, 52))
        got = REFERENCE.network_norm_to_original_norm((0.50, 0.10, 0.60, 0.20), geom)
        for index, (value, literal) in enumerate(zip(got, literals)):
            self.assertAlmostEqual(value, literal, places=9, msg=f"分量 {index}")
            self.assertAlmostEqual(value, expected[index], places=9, msg=f"算式 {index}")
        # 不提前取整：y1 连续像素坐标为 41.6（而非 42）
        self.assertAlmostEqual(got[1] * 415, 41.6, places=9)
        self.assertGreater(abs(got[1] * 415 - 42.0), 0.3)

    def test_hand_samples_registry_consistent(self):
        samples = R.hand_computed_samples()
        self.assertGreaterEqual(len(samples), 3)
        for row in samples:
            with self.subTest(sample=row["sample_id"]):
                geom = REFERENCE.letterbox_geometry(row["src_width"], row["src_height"], 416, 416)
                for key, value in row["geometry"].items():
                    self.assertEqual(geom[key], value, key)
                got = REFERENCE.network_norm_to_original_norm(row["network_box"], geom)
                for value, literal in zip(got, row["expected_literals"]):
                    self.assertAlmostEqual(value, literal, places=9)


class TestT5_02EdgeClipDegenerate(unittest.TestCase):
    """T5-02：贴边/四角/部分越界/裁剪后零面积/letterbox 补边带/退化几何。"""

    def test_edge_flush_clipped_to_unit_box(self):
        geom = REFERENCE.letterbox_geometry(640, 640, 416, 416)
        left = REFERENCE.network_norm_to_original_norm((0.0, 0.0, 0.5, 0.25), geom)
        right = REFERENCE.network_norm_to_original_norm((0.5, 0.75, 1.0, 1.0), geom)
        clip_left = REFERENCE.clip_unit_box(left)
        clip_right = REFERENCE.clip_unit_box(right)
        self.assertEqual(clip_left["xyxy"][0], 0.0)
        self.assertTrue(clip_right["clipped"])
        self.assertEqual(clip_right["xyxy"][2], 1.0)
        self.assertEqual(clip_right["xyxy"][3], 1.0)
        self.assertFalse(clip_right["zero_area"])

    def test_partial_out_of_bounds_counted_as_clipped(self):
        for box in ((-0.10, -0.05, 0.30, 0.40), (0.70, 0.80, 1.15, 1.05)):
            with self.subTest(box=box):
                clip = REFERENCE.clip_unit_box(box)
                self.assertTrue(clip["clipped"])
                self.assertFalse(clip["zero_area"])

    def test_fully_outside_is_zero_area(self):
        clip = REFERENCE.clip_unit_box((1.20, 0.20, 1.40, 0.40))
        self.assertTrue(clip["clipped"])
        self.assertTrue(clip["zero_area"])
        self.assertEqual(clip["xyxy"], (1.0, 0.2, 1.0, 0.4))

    def test_boxes_inside_letterbox_padding_become_zero_area(self):
        # 1280×720 的上补边带：off_y=91 ⇒ 网络归一化 y < 91/416 ≈ 0.21875 落在补边内
        geom = REFERENCE.letterbox_geometry(1280, 720, 416, 416)
        padded = REFERENCE.network_norm_to_original_norm((0.30, 0.02, 0.70, 0.20), geom)
        self.assertLess(padded[1], 0.0)
        clip = REFERENCE.clip_unit_box(padded)
        self.assertTrue(clip["zero_area"])
        inside = REFERENCE.network_norm_to_original_norm((0.30, 0.35, 0.70, 0.60), geom)
        self.assertFalse(REFERENCE.clip_unit_box(inside)["zero_area"])

    def test_renderer_skips_zero_area_boxes(self):
        spec = case_by_id("t5_02_clip_zero_area")
        geom = REFERENCE.letterbox_geometry(spec["src_w"], spec["src_h"], 416, 416)
        drawn = []
        for _, _, xyxy, _ in spec["boxes"]:
            clip = REFERENCE.clip_unit_box(xyxy)
            if not clip["zero_area"]:
                drawn.append(REFERENCE.original_norm_to_display_px(clip["xyxy"], spec["src_w"],
                                                                   spec["src_h"]))
        self.assertEqual(len(drawn), 1)
        self.assertEqual(len(spec["boxes"]) - len(drawn), 1)

    def test_degenerate_geometry_raises_for_narrow_sources(self):
        for src_w, src_h in ((1, 300), (300, 1), (2, 500)):
            with self.subTest(size=(src_w, src_h)):
                geom = REFERENCE.letterbox_geometry(src_w, src_h, 416, 416)
                self.assertLessEqual(min(geom["new_width"], geom["new_height"]), 1)
                with self.assertRaises(REFERENCE.DegenerateGeometryError) as ctx:
                    REFERENCE.network_norm_to_original_norm((0.1, 0.1, 0.2, 0.2), geom)
                self.assertIn("原图坐标字段", str(ctx.exception))

    def test_degenerate_case_records_fallback(self):
        spec = case_by_id("t5_02_degenerate_new_w_1")
        self.assertTrue(spec["expects_degenerate"])
        geom = REFERENCE.letterbox_geometry(spec["src_w"], spec["src_h"], 416, 416)
        self.assertEqual(geom["new_width"], 1)
        self.assertEqual(geom["w_scale"], 0.0)

    def test_clip_rejects_non_positive_area_upstream(self):
        with self.assertRaises(REFERENCE.ContractViolation):
            REFERENCE.clip_unit_box((0.5, 0.5, 0.5, 0.9))


class TestT5_03MultiAndZeroBox(unittest.TestCase):
    """T5-03：15 框上限、零框 NO_HAND 与稳定顺序。"""

    def test_multi_case_has_exactly_fifteen_boxes(self):
        spec = case_by_id("t5_03_multi_15")
        self.assertEqual(len(spec["boxes"]), 15)
        self.assertEqual(len(spec["boxes"]), REFERENCE.MAX_OUTPUTS_PER_IMAGE)
        orders = [box[3] for box in spec["boxes"]]
        self.assertEqual(len(set(orders)), 15, "source_order 必须唯一，便于稳定顺序审计")
        scores = [box[1] for box in spec["boxes"]]
        self.assertEqual(scores, sorted(scores, reverse=True), "多框按分数降序给出")

    def test_record_with_sixteen_boxes_violates_contract(self):
        spec = case_by_id("t5_03_multi_15")
        boxes = list(spec["boxes"]) + [R._box(0, 0.3, (0.1, 0.1, 0.2, 0.2), 9999)]
        ledger = R.synth_clock(1)
        record = R._record_from_boxes(1, 640, 640, boxes, "OK", ledger, False, 33_000_000)
        problems = REFERENCE.validate_result_record(record)
        self.assertTrue(any("冻结上限" in problem for problem in problems), problems)

    def test_no_hand_record_is_valid_and_zero_box(self):
        ledger = R.synth_clock(2)
        record = R._record_from_boxes(2, 640, 640, [], "NO_HAND", ledger, False, 33_000_000)
        self.assertEqual(REFERENCE.validate_result_record(record), [])
        self.assertEqual(record["detection_count"], 0)
        self.assertEqual(record["state"], "NO_HAND")

    def test_no_hand_with_boxes_is_rejected(self):
        ledger = R.synth_clock(3)
        record = R._record_from_boxes(3, 640, 640, [R._box(0, 0.5, (0.1, 0.1, 0.2, 0.2), 1)],
                                      "NO_HAND", ledger, False, 33_000_000)
        problems = REFERENCE.validate_result_record(record)
        self.assertTrue(any("NO_HAND" in problem for problem in problems), problems)

    def test_zero_box_not_counted_as_stale(self):
        # 零框（NO_HAND）：无框不等于过期；本用例年龄未越限、PS 标志 false
        ledger = R.synth_clock(4)
        ages = REFERENCE.compute_ages(ledger["capture_time_ns"], ledger["result_time_ns"],
                                      ledger["overlay_commit_ns"])
        stale = REFERENCE.effective_stale(False, ages["age_frame_ns"])
        self.assertFalse(stale["stale_effective"])
        self.assertEqual(stale["reason"], REFERENCE.STALE_REASON_NONE)


class TestT5_04StaleClearing(unittest.TestCase):
    """T5-04：过期边界、原因合并、每结果只计一次、不静默丢。"""

    def test_boundary_strictly_greater(self):
        limit = REFERENCE.STALE_AGE_LIMIT_NS
        self.assertFalse(REFERENCE.is_stale(limit))
        self.assertTrue(REFERENCE.is_stale(limit + 1))
        self.assertFalse(REFERENCE.is_stale(limit - 1))

    def test_reason_matrix(self):
        limit = REFERENCE.STALE_AGE_LIMIT_NS
        cases = [
            (False, 1_000, False, REFERENCE.STALE_REASON_NONE),
            (True, 1_000, True, REFERENCE.STALE_REASON_FLAG),
            (False, limit + 1, True, REFERENCE.STALE_REASON_AGE),
            (True, limit + 1, True, REFERENCE.STALE_REASON_BOTH),
            (False, limit, False, REFERENCE.STALE_REASON_NONE),
        ]
        for flag, age, effective, reason in cases:
            with self.subTest(flag=flag, age=age):
                info = REFERENCE.effective_stale(flag, age)
                self.assertEqual(info["stale_effective"], effective)
                self.assertEqual(info["reason"], reason)
                self.assertEqual(info["limit_ns"], limit)

    def test_case_table_covers_required_stale_scenarios(self):
        expected = {
            "t5_04_age_equal_limit": (False, REFERENCE.STALE_REASON_NONE),
            "t5_04_age_limit_plus_1": (True, REFERENCE.STALE_REASON_AGE),
            "t5_04_stale_flag_small_age": (True, REFERENCE.STALE_REASON_FLAG),
            "t5_04_stale_both": (True, REFERENCE.STALE_REASON_BOTH),
        }
        for case_id, (effective, reason) in expected.items():
            with self.subTest(case=case_id):
                spec = case_by_id(case_id)
                age = REFERENCE.STALE_AGE_LIMIT_NS if case_id == "t5_04_age_equal_limit" \
                    else (spec["age_frame_ns"] or 15_000_000)
                info = REFERENCE.effective_stale(spec["stale_flag"], age)
                self.assertEqual(info["stale_effective"], effective)
                self.assertEqual(info["reason"], reason)

    def test_age_identity_and_no_time_reversal(self):
        ledger = R.synth_clock(10, 200_000_001, 1)
        ages = REFERENCE.compute_ages(ledger["capture_time_ns"], ledger["result_time_ns"],
                                      ledger["overlay_commit_ns"])
        self.assertEqual(ages["age_frame_ns"],
                         ages["age_result_ns"] + ledger["result_time_ns"] - ledger["capture_time_ns"])
        self.assertEqual(ages["display_semantics"], REFERENCE.DISPLAY_SEMANTICS)
        with self.assertRaises(REFERENCE.ContractViolation):
            REFERENCE.compute_ages(0, 100, 50)

    def test_synth_clock_reaches_equal_limit_exactly(self):
        ledger = R.synth_clock(20, REFERENCE.STALE_AGE_LIMIT_NS, 1)
        self.assertEqual(ledger["overlay_commit_ns"] - ledger["capture_time_ns"],
                         REFERENCE.STALE_AGE_LIMIT_NS)
        self.assertGreaterEqual(ledger["result_time_ns"], ledger["capture_time_ns"])
        self.assertLessEqual(ledger["result_time_ns"], ledger["overlay_commit_ns"])
        self.assertEqual(ledger["displayed_frame_id"], 21)


class TestT5_05GoldenLedger(unittest.TestCase):
    """T5-05：S4-C golden 109 帧台账可按 frame_id 索引、语义唯一。"""

    @classmethod
    def setUpClass(cls):
        contract_paths = R.resolve_upstream_inputs(CONTRACT, {})
        cls.golden_path = Path(contract_paths.get("s4c_golden109", ""))
        if not cls.golden_path.is_file():
            raise unittest.SkipTest(f"只读 S4-C golden 不可用：{cls.golden_path}")
        cls.golden = json.loads(cls.golden_path.read_text(encoding="utf-8"))

    def test_frame_count_and_unique_ids(self):
        samples = self.golden["samples"]
        self.assertGreaterEqual(len(samples), 100)
        frame_ids = [int(sample["frame_id"]) for sample in samples]
        self.assertEqual(len(set(frame_ids)), len(frame_ids))
        self.assertEqual(self.golden["status"], "PASS")

    def test_ledger_rows_are_indexable_and_unique_semantics(self):
        samples = self.golden["samples"]
        rows = []
        for sample in samples:
            clock = R.synth_clock(int(sample["frame_id"]))
            ages = REFERENCE.compute_ages(clock["capture_time_ns"], clock["result_time_ns"],
                                          clock["overlay_commit_ns"])
            rows.append([clock["displayed_frame_id"], int(sample["frame_id"]),
                         ages["age_result_ns"], ages["age_frame_ns"], ages["display_semantics"]])
        indexed = {row[1]: row for row in rows}
        self.assertEqual(len(indexed), len(rows))
        self.assertEqual({row[4] for row in rows}, {REFERENCE.DISPLAY_SEMANTICS})
        self.assertTrue(all(row[0] != row[1] for row in rows))

    def test_zero_box_samples_exist_and_use_no_hand(self):
        zero = [sample for sample in self.golden["samples"] if not sample["detections_actual"]]
        self.assertGreaterEqual(len(zero), 1)
        for sample in zero:
            with self.subTest(sample=sample["sample_id"]):
                ledger = R.synth_clock(int(sample["frame_id"]))
                record = R._record_from_boxes(int(sample["frame_id"]),
                                              int(sample["geometry_wh"][0]),
                                              int(sample["geometry_wh"][1]), [], "NO_HAND",
                                              ledger, False, 33_000_000)
                self.assertEqual(REFERENCE.validate_result_record(record), [])

    def test_all_geometries_pass_seeded_round_trip(self):
        geodes = sorted({tuple(sample["geometry_wh"]) for sample in self.golden["samples"]})
        self.assertGreaterEqual(len(geodes), 10)
        for src_w, src_h in geodes:
            with self.subTest(size=(src_w, src_h)):
                geom = REFERENCE.letterbox_geometry(src_w, src_h, 416, 416)
                try:
                    rng = __import__("random").Random(R.DEFAULT_SEED)
                    worst = 0.0
                    for _ in range(R.RANDOM_BOX_N):
                        x1, x2 = sorted((rng.random(), rng.random()))
                        y1, y2 = sorted((rng.random(), rng.random()))
                        net_box = (x1, y1, x2, y2)
                        back = REFERENCE.original_norm_to_network_norm(
                            REFERENCE.network_norm_to_original_norm(net_box, geom), geom)
                        worst = max(worst, max(abs(a - b) for a, b in zip(back, net_box)))
                    self.assertLessEqual(worst, R.RANDOM_ROUND_TRIP_TOL)
                except REFERENCE.DegenerateGeometryError:
                    continue


class TestRoundTripAndPixels(unittest.TestCase):
    """数值层：round-trip、显示像素层、冻结边框像素集与独立手算对拍。"""

    def test_seeded_random_round_trip_all_case_geometries(self):
        for spec in R.case_table():
            if spec["kind"] != "synthetic" or spec["expects_degenerate"]:
                continue
            with self.subTest(case=spec["case_id"]):
                geom = REFERENCE.letterbox_geometry(spec["src_w"], spec["src_h"], 416, 416)
                rng = __import__("random").Random(R.DEFAULT_SEED)
                worst = 0.0
                for _ in range(R.RANDOM_BOX_N):
                    x1, x2 = sorted((rng.random(), rng.random()))
                    y1, y2 = sorted((rng.random(), rng.random()))
                    net_box = (x1, y1, x2, y2)
                    back = REFERENCE.original_norm_to_network_norm(
                        REFERENCE.network_norm_to_original_norm(net_box, geom), geom)
                    worst = max(worst, max(abs(a - b) for a, b in zip(back, net_box)))
                self.assertLessEqual(worst, R.RANDOM_ROUND_TRIP_TOL)

    def test_display_pixel_rounding_within_one_pixel(self):
        geom = REFERENCE.letterbox_geometry(683, 384, 416, 416)
        for network_box in ((0.05, 0.30, 0.45, 0.80), (0.60, 0.40, 0.95, 0.90), (0.5, 0.5, 0.6, 0.6)):
            with self.subTest(box=network_box):
                clip = REFERENCE.clip_unit_box(
                    REFERENCE.network_norm_to_original_norm(network_box, geom))
                px = REFERENCE.original_norm_to_display_px(clip["xyxy"], 683, 384)
                float64 = R.float64_display_continuous(clip["xyxy"], 683, 384)
                for axis in ("x1", "y1", "x2", "y2"):
                    self.assertLessEqual(abs(px[axis] - float64[axis]), R.DISPLAY_PX_TOL)
                    self.assertLessEqual(abs(px[axis] - float64[axis]), 0.5)

    def test_canvas_pixel_rounding_within_one_pixel(self):
        fit = REFERENCE.canvas_fit(683, 384, 1920, 1080)
        clip = REFERENCE.clip_unit_box((0.21, 0.33, 0.77, 0.91))
        px = REFERENCE.original_norm_to_canvas_px(clip["xyxy"], fit)
        float64 = R.float64_canvas_continuous(clip["xyxy"], fit)
        for axis in ("x1", "y1", "x2", "y2"):
            self.assertLessEqual(abs(px[axis] - float64[axis]), R.DISPLAY_PX_TOL)

    def test_border_pixel_sets_hand_derivation(self):
        # 手算推导（frame 内框 x∈[1,4]、y∈[1,3]，线宽 2 ⇒ 偏移 {-1, 0}，偶数线宽居中）：
        #   上/下边：x 取 1..4；y ∈ {y1-1, y1, y2-1, y2} = {0, 1, 2, 3}
        #       x=1..4 → 每列 4 个像素，共 16 个
        #   左/右边：y 取 1..3；x ∈ {x1-1, x1, x2-1, x2} = {0, 1, 3, 4}
        #       y=1..3 → 每行 4 个像素，共 12 个
        #   合并（无重复，因 y=0 行只有上/下边贡献）：
        #       y=0: x ∈ {1,2,3,4}           → 4
        #       y=1,2,3: x ∈ {0,1,2,3,4}     → 各 5，共 15
        #   合计 19 个像素
        expected = ([(x, 0) for x in (1, 2, 3, 4)]
                    + [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3, 4)])
        got = [tuple(pixel) for pixel in REFERENCE.border_pixel_sets(1, 1, 4, 3, 2, 16, 16)]
        self.assertEqual(len(expected), 19)
        self.assertEqual(sorted(expected), sorted(got))
        # 逐边钳到画布内：画布只有 3×3 时超界像素必须被丢弃
        clipped = [tuple(pixel) for pixel in REFERENCE.border_pixel_sets(1, 1, 4, 3, 2, 3, 3)]
        self.assertTrue(all(0 <= x < 3 and 0 <= y < 3 for x, y in clipped))
        self.assertLess(len(clipped), len(got))

    def test_border_pixel_sets_rejects_odd_width(self):
        for width in (0, -2, 3, 1):
            with self.subTest(width=width):
                with self.assertRaises(REFERENCE.ContractViolation):
                    REFERENCE.border_pixel_sets(1, 1, 4, 3, width, 16, 16)

    def test_label_anchor_rule(self):
        # 框左上外侧；越界翻转框内左上；仍越界则钳入安全区
        outside = R.place_label(100, 100, 40, 12, 640, 480, 16)
        self.assertEqual((outside["x"], outside["y"]), (100, 87))
        self.assertFalse(outside["flipped_inside"])
        near_top = R.place_label(100, 8, 40, 12, 640, 480, 16)
        self.assertTrue(near_top["flipped_inside"])
        self.assertGreaterEqual(near_top["x"], 16)
        self.assertGreaterEqual(near_top["y"], 16)
        tiny = R.place_label(2, 2, 600, 12, 640, 480, 16)
        self.assertLessEqual(tiny["x"] + tiny["width"], 640)
        self.assertGreaterEqual(tiny["x"], 0)


class TestRendererEndToEnd(unittest.TestCase):
    """库级端到端：逐用例 JSON 语义、HUD 13 字段、双 pass 字节一致、退出码语义。"""

    @classmethod
    def setUpClass(cls):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)
        TMP_ROOT.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP_ROOT, ignore_errors=True)

    def _render(self, run_id: str, cases: str) -> int:
        return R.run_main(["--out", str(TMP_ROOT), "--run-id", run_id,
                           "--seed", str(R.DEFAULT_SEED), "--cases", cases])

    def test_subset_render_passes_and_semantics(self):
        code = self._render("ut_a", "T5-01")
        self.assertEqual(code, R.EXIT_PASS)
        run_dir = TMP_ROOT / "ut_a"
        logs = [json.loads(path.read_text(encoding="utf-8"))
                for path in sorted((run_dir / "logs").glob("*.json"))]
        self.assertGreaterEqual(len(logs), 5)
        semantics = set()
        for log in logs:
            with self.subTest(case=log["case_id"]):
                # 从磁盘读回的 JSON 键序已被 sort_keys 规范化，故按集合与长度校验字段完整性
                self.assertEqual(sorted(log["hud"].keys()), sorted(R.REQUIRED_HUD_FIELDS))
                self.assertEqual(len(log["hud"]), len(R.REQUIRED_HUD_FIELDS))
                self.assertEqual(len(log["five_tuple"]), 5)
                self.assertEqual(log["five_tuple"][4], REFERENCE.DISPLAY_SEMANTICS)
                self.assertNotEqual(log["five_tuple"][0], log["five_tuple"][1])
                semantics.add(log["five_tuple"][4])
                self.assertEqual(log["status"], "PASS")
                self.assertTrue((run_dir / log["png"]["name"]).is_file())
        self.assertEqual(semantics, {REFERENCE.DISPLAY_SEMANTICS})
        manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["exit_code"], R.EXIT_PASS)
        self.assertEqual(manifest["determinism"]["status"], "NOT_RUN_SINGLE_PASS")
        scan = R.scan_paths(sorted((run_dir / "logs").glob("*.json"))
                            + sorted((run_dir / "cases").glob("*.png"))
                            + [run_dir / "run_manifest.json", run_dir / "summary.md"])
        self.assertEqual(scan["hit_total"], 0)

    def test_double_pass_byte_identical(self):
        first = self._render("ut_det_a", "T5-01,T5-04")
        second = self._render("ut_det_b", "T5-01,T5-04")
        self.assertEqual((first, second), (R.EXIT_PASS, R.EXIT_PASS))
        dir_a, dir_b = TMP_ROOT / "ut_det_a", TMP_ROOT / "ut_det_b"
        png_a = {path.name: R.sha256_file(path) for path in sorted((dir_a / "cases").glob("*.png"))}
        png_b = {path.name: R.sha256_file(path) for path in sorted((dir_b / "cases").glob("*.png"))}
        json_a = {path.name: R.sha256_file(path) for path in sorted((dir_a / "logs").glob("*.json"))}
        json_b = {path.name: R.sha256_file(path) for path in sorted((dir_b / "logs").glob("*.json"))}
        self.assertEqual(png_a, png_b)
        self.assertEqual(json_a, json_b)
        self.assertGreater(len(png_a), 0)

    def test_degenerate_case_renders_and_passes(self):
        code = self._render("ut_degenerate", "t5_02_degenerate_new_w_1")
        self.assertEqual(code, R.EXIT_PASS)
        log = json.loads((TMP_ROOT / "ut_degenerate" / "logs"
                          / "t5_02_degenerate_new_w_1.json").read_text(encoding="utf-8"))
        self.assertEqual(log["degenerate"]["raised"], "DegenerateGeometryError")
        self.assertIn("原图坐标字段", log["degenerate"]["fallback"])
        self.assertEqual(log["boxes_drawn"], 0)

    def test_run_id_protection_refuses_overwrite(self):
        self.assertEqual(self._render("ut_guard", "T5-04"), R.EXIT_PASS)
        self.assertEqual(self._render("ut_guard", "T5-04"), R.EXIT_ERROR)

    def test_tamper_probe_must_fail_with_exit_one(self):
        # 反例探针：篡改独立手算的期望像素集 ⇒ 断言必须 FAIL ⇒ 退出码 1（不得静默通过）
        with mock.patch.object(R, "HAND_BORDER_PIXELS", [(0, 0)]):
            code = self._render("ut_tamper", "T5-04")
        self.assertEqual(code, R.EXIT_FAIL)

    def test_missing_upstream_input_must_be_exit_two(self):
        code = R.run_main(["--out", str(TMP_ROOT), "--run-id", "ut_env",
                           "--cases", "t5_05_s4c_golden109_frame_ledger",
                           "--s4c-golden", str(TMP_ROOT / "not_exists.json")])
        self.assertEqual(code, R.EXIT_ERROR)

    def test_driver_refuses_existing_run_id_without_touching_it(self):
        import run_s5b_evidence as drv

        guard_dir = TMP_ROOT / "drv_guard_a"
        shutil.rmtree(guard_dir, ignore_errors=True)
        (guard_dir / "cases").mkdir(parents=True, exist_ok=True)
        sentinel = guard_dir / "run_manifest.json"
        sentinel.write_text('{"exit_code": 0, "status": "PASS", "sentinel": true}\n',
                            encoding="utf-8")
        before = sorted(p.relative_to(guard_dir).as_posix()
                        for p in guard_dir.rglob("*") if p.is_file())
        code = drv.main(["--out", str(TMP_ROOT), "--run-id", "drv_guard", "--skip-unittest"])
        self.assertEqual(code, drv.EXIT_ERROR)
        after = sorted(p.relative_to(guard_dir).as_posix()
                       for p in guard_dir.rglob("*") if p.is_file())
        self.assertEqual(before, after, "拒绝时必须不改写目标 RunId 目录（含 console）")
        self.assertEqual(json.loads(sentinel.read_text(encoding="utf-8"))["sentinel"], True)

    def test_selfcheck_passes(self):
        self.assertEqual(R.run_main(["--selfcheck"]), R.EXIT_PASS)


class TestEvidenceDriver(unittest.TestCase):
    """证据驱动（一键命令）端到端：双 pass 比对、manifest 规范键、最终判定文件。

    使用 `--skip-unittest` 避免驱动再递归调用整个测试套件；跳过会被如实记为
    `unittest_SKIPPED_BY_FLAG` 并导致驱动退出码 1（证据包不完整），这是有意为之。
    """

    def test_driver_end_to_end_subset(self):
        import run_s5b_evidence as drv

        run_id = "drv_ut"
        shutil.rmtree(TMP_ROOT / f"{run_id}_a", ignore_errors=True)
        shutil.rmtree(TMP_ROOT / f"{run_id}_b", ignore_errors=True)
        code = drv.main(["--out", str(TMP_ROOT), "--run-id", run_id,
                         "--seed", str(R.DEFAULT_SEED), "--cases", "T5-03", "--skip-unittest"])
        self.assertEqual(code, drv.EXIT_FAIL)
        dir_a = TMP_ROOT / f"{run_id}_a"
        dir_b = TMP_ROOT / f"{run_id}_b"
        manifest = json.loads((dir_a / "run_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["determinism"]["status"], "PASS")
        self.assertTrue(manifest["determinism"]["png_identical"])
        self.assertTrue(manifest["determinism"]["json_identical"])
        for key in ("png_set_digest", "json_stats_digest", "png_set_digest_a",
                    "json_stats_digest_a", "png_sha256_a", "json_stats_a"):
            self.assertIn(key, manifest["determinism"])
        self.assertEqual(manifest["replica"]["run_id"], dir_b.name)
        self.assertEqual(manifest["unittest"]["status"], "SKIPPED")
        verdict = json.loads((dir_a / "console" / "final_verdict.json").read_text(encoding="utf-8"))
        self.assertEqual(verdict["exit_code"], drv.EXIT_FAIL)
        self.assertIn("unittest_SKIPPED_BY_FLAG", verdict["reasons"])
        self.assertEqual(verdict["determinism_status"], "PASS")
        for name in ("run_a_stdout.txt", "run_a_stderr.txt", "run_a_exit_code.txt",
                     "run_b_stdout.txt", "run_b_exit_code.txt", "driver_stdout.txt",
                     "driver_exit_code.txt", "shell_invocation.txt", "determinism_compare.txt",
                     "hash_recheck.txt", "wording_scan.txt", "wording_scan.json"):
            with self.subTest(console_file=name):
                self.assertTrue((dir_a / "console" / name).is_file(), name)
        self.assertEqual(manifest["hash_recheck"]["status"], "PASS")
        self.assertGreater(manifest["hash_recheck"]["checked"], 0)
        self.assertEqual((dir_a / "console" / "run_a_exit_code.txt").read_text(
            encoding="utf-8").strip(), "0")
        self.assertIn("PASS", (dir_a / "summary.md").read_text(encoding="utf-8"))
        scan = json.loads((dir_a / "console" / "wording_scan.json").read_text(encoding="utf-8"))
        self.assertEqual(scan["hit_total"], 0)
        self.assertGreater(scan["artifacts_scanned"], 0)


class TestWordingDiscipline(unittest.TestCase):
    """用词纪律：本工具源码与产物不得出现禁用称谓（字段名统一 score）。"""

    def test_library_and_test_sources_are_clean(self):
        for path in (SCRIPT_DIR / "render_s5b_overlay.py", SCRIPT_DIR / "run_s5b_evidence.py",
                     SCRIPT_DIR / "test_s5b_overlay.py"):
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN_TOKENS:
                with self.subTest(path=path.name, codepoints=" ".join(f"U+{ord(c):04X}"
                                                                      for c in token)):
                    self.assertNotIn(token, text)

    def test_scan_tokens_are_split_so_source_never_triggers(self):
        table = R.build_scan_token_table()
        self.assertEqual(len(table), len(FORBIDDEN_TOKENS))
        for entry in table:
            with self.subTest(token_id=entry["token_id"]):
                self.assertGreater(entry["length"], 0)
                self.assertEqual(len(entry["sha256"]), 64)

    def test_score_is_the_only_score_field_name(self):
        """产物内分数一律以 `score` 命名；无框用例不出现任何分数称谓字段。"""
        run_dir = TMP_ROOT / "ut_words"
        shutil.rmtree(run_dir, ignore_errors=True)
        self.assertEqual(R.run_main(["--out", str(TMP_ROOT), "--run-id", "ut_words",
                                     "--cases", "T5-03"]), R.EXIT_PASS)
        expected_count = 0
        for path in sorted((run_dir / "logs").glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for box in payload.get("boxes", []):
                self.assertIn("score", box)
                expected_count += 1
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                for token in FORBIDDEN_TOKENS:
                    self.assertNotIn(token, text)
        self.assertGreater(expected_count, 0, "至少应有一个被绘制的框以校验字段命名")


if __name__ == "__main__":
    unittest.main(verbosity=2)