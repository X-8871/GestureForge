"""S5-A 自检：阶段5 显示契约（S5A-G0-v2）与冻结参考实现的内部一致性与边界行为。

覆盖：
- 正向几何与 D2 冻结实现逐值对拍（禁止第二套 resize）
- 逆映射**手算样例**（算式写在断言旁，独立于模块实现）
- 原图→网络→原图 round-trip 与种子化随机框
- 奇数总补边的非对称补边保留（683×384 → off_y=91 / 下侧 92）
- 退化几何（new_w==1 或 new_h==1）必须抛 DegenerateGeometryError
- 过期判定边界（age == limit 不过期；age = limit+1 过期）与原因分类
- 边框像素语义（偶数线宽居中）逐像素断言
- 非方形入不同画布：整数倍等比居中、不拉伸
- 契约 JSON ↔ 参考实现常量逐项一致（防止两处漂移）
- `validate_result_record` 正/反例

运行：`python -B -m unittest verification.test_s5_display_geometry_reference -v`
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import random
import sys
import unittest
from fractions import Fraction

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verification.s5_display_geometry_reference as R  # noqa: E402

CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5a_stage5_display_g0_fields.json"

# V1 基线草案表（S5 v1 §3.1）中由冻结公式推导的几何，用于回归
DRAFT_GEOMETRY_TABLE = {
    (1280, 720): (416, 234, 0, 91),
    (720, 1280): (234, 416, 91, 0),
    (1920, 1080): (416, 234, 0, 91),
    (640, 640): (416, 416, 0, 0),
    (800, 600): (416, 312, 0, 52),
    (640, 360): (416, 234, 0, 91),
    (683, 384): (416, 233, 0, 91),
}


def _load_d2_module():
    spec = importlib.util.spec_from_file_location(
        "s1_t02_d2_numeric_reference", REPO_ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGeometryFrozenParity(unittest.TestCase):
    def test_letterbox_matches_d2_reference(self):
        d2 = _load_d2_module()
        for (src_w, src_h), _ in DRAFT_GEOMETRY_TABLE.items():
            with self.subTest(src=(src_w, src_h)):
                mine = R.letterbox_geometry(src_w, src_h)
                frozen = d2.letterbox_geometry(src_w, src_h, 416, 416)
                for key in ("new_width", "new_height", "offset_x", "offset_y"):
                    self.assertEqual(mine[key], frozen[key], msg=f"{key} 与 D2 冻结实现不一致")

    def test_draft_table_values(self):
        for (src_w, src_h), (new_w, new_h, off_x, off_y) in DRAFT_GEOMETRY_TABLE.items():
            with self.subTest(src=(src_w, src_h)):
                geom = R.letterbox_geometry(src_w, src_h)
                self.assertEqual(
                    (geom["new_width"], geom["new_height"], geom["offset_x"], geom["offset_y"]),
                    (new_w, new_h, off_x, off_y),
                )

    def test_odd_asymmetric_padding_is_preserved(self):
        geom = R.letterbox_geometry(683, 384)
        self.assertEqual((geom["offset_y"], geom["pad_bottom"]), (91, 92))
        self.assertTrue(geom["asymmetric_padding"])
        # 镜像用例：奇数总补边在右侧
        geom_x = R.letterbox_geometry(384, 683)
        self.assertEqual((geom_x["offset_x"], geom_x["pad_right"]), (91, 92))

    def test_degenerate_geometry_raises(self):
        # 极窄源：1×300 → new_w = (1*416)//300 = 1（退化）；300×1 → new_h = 1（退化）
        geom_narrow = R.letterbox_geometry(1, 300)
        self.assertEqual(geom_narrow["new_width"], 1)
        with self.assertRaises(R.DegenerateGeometryError):
            R.network_norm_to_original_norm((0.0, 0.0, 1.0, 1.0), geom_narrow)
        geom_flat = R.letterbox_geometry(300, 1)
        self.assertEqual(geom_flat["new_height"], 1)
        with self.assertRaises(R.DegenerateGeometryError):
            R.network_norm_to_original_norm((0.0, 0.0, 1.0, 1.0), geom_flat)
        # 正向与逆向共用同一退化守卫：new_w==1 时正向不得 ZeroDivisionError
        with self.assertRaises(R.DegenerateGeometryError):
            R.original_norm_to_network_norm((0.0, 0.0, 1.0, 1.0), geom_narrow)
        # 源尺寸本身 <=1 像素：两向都无定义（1×1 源 → new=416×416，但无有效采样点）
        geom_src = R.letterbox_geometry(1, 1)
        for target in (R.network_norm_to_original_norm, R.original_norm_to_network_norm):
            with self.subTest(func=target.__name__):
                with self.assertRaises(R.DegenerateGeometryError):
                    target((0.0, 0.0, 1.0, 1.0), geom_src)


class TestInverseMappingHandComputed(unittest.TestCase):
    """手算样例：所有期望值用独立算式（Fraction/显式乘除）写出，不调用被测模块。"""

    def test_hand_computed_1280x720(self):
        # 网络归一化坐标相对 **416×416** 网络输入画布（不是补边后的 416×234）。
        # 源 1280×720 → new=416×234、off=(0,91)、w_scale=1279/415、h_scale=719/233
        # u=0.5：x_r = 0.5*416 - 0 = 208；x_px = 208*1279/415；u_orig = x_px/1279 = 208/415
        # v=0.5：y_r = 0.5*416 - 91 = 117；y_px = 117*719/233；v_orig = y_px/719 = 117/233
        geom = R.letterbox_geometry(1280, 720)
        x1, y1, _, _ = R.network_norm_to_original_norm((0.5, 0.5, 0.5, 0.5), geom)
        self.assertLess(abs(x1 - float(Fraction(208, 415))), 1e-15)
        self.assertLess(abs(y1 - float(Fraction(117, 233))), 1e-15)

    def test_hand_computed_portrait_720x1280(self):
        # 源 720×1280 → new=234×416、off=(91,0)、w_scale=719/233
        # u=0.25：x_r = 0.25*416 - 91 = 104 - 91 = 13；x_px = 13*719/233；u_orig = x_px/719 = 13/233
        geom = R.letterbox_geometry(720, 1280)
        x1, _, _, _ = R.network_norm_to_original_norm((0.25, 0.0, 0.25, 0.0), geom)
        self.assertLess(abs(x1 - float(Fraction(13, 233))), 1e-15)

    def test_hand_computed_endpoint_alignment_1920(self):
        # v1 §3.2 引用的端点对齐例子：源宽 1920、x_r=415 → x_px = 415*(1919/415) = 1919.00
        geom = R.letterbox_geometry(1920, 1080)
        self.assertLess(abs(415 * geom["w_scale"] - 1919.0), 1e-9)
        # 且中间量不得提前取整：u=415/416 时必须给出 1919/1919 的原图归一化端点
        x1, _, _, _ = R.network_norm_to_original_norm((415 / 416, 0.0, 415 / 416, 1.0), geom)
        self.assertLess(abs(x1 - 1.0), 1e-12)

    def test_asymmetric_offset_used_verbatim(self):
        # 683×384：new=416×233、off_y=91、下侧补边 92、h_scale=(384-1)/(233-1)=383/232
        # v=1.0：y_r = 1.0*416 - 91 = 325；y_px = 325*383/232；v_orig = y_px/383 = 325/232 > 1
        # （超出原图下边界 ⇒ 后续必须裁剪，正说明底部补边确实存在）
        geom = R.letterbox_geometry(683, 384)
        _, y1, _, y2 = R.network_norm_to_original_norm((0.0, 0.0, 1.0, 1.0), geom)
        # v=0.0：y_r = 0 - 91 = -91；y_px = -91*383/232；v_orig = y_px/383 = -91/232 < 0
        self.assertLess(abs(y1 - float(Fraction(-91, 232))), 1e-15)
        self.assertLess(y1, 0.0)
        self.assertLess(abs(y2 - float(Fraction(325, 232))), 1e-15)
        self.assertGreater(y2, 1.0)
        # 反例：若误按上下各 91.5 对称处理（对称化）会得到 324.5/232，必须与实测值不同
        self.assertNotAlmostEqual(y2, float(Fraction(3245, 2320)), places=12)
        clipped = R.clip_unit_box((0.0, 0.5, 1.0, y2))
        self.assertTrue(clipped["clipped"])
        self.assertFalse(clipped["zero_area"])


class TestRoundTripAndRandom(unittest.TestCase):
    def test_round_trip_all_draft_geometries(self):
        for src_w, src_h in DRAFT_GEOMETRY_TABLE:
            with self.subTest(src=(src_w, src_h)):
                geom = R.letterbox_geometry(src_w, src_h)
                if geom["new_width"] <= 1 or geom["new_height"] <= 1:
                    continue
                box = (0.13, 0.27, 0.61, 0.83)
                back = R.original_norm_to_network_norm(R.network_norm_to_original_norm(box, geom), geom)
                self.assertLess(max(abs(a - b) for a, b in zip(box, back)), 1e-12)

    def test_seeded_random_boxes(self):
        seed = 20261021
        rng = random.Random(seed)
        geometries = [R.letterbox_geometry(w, h) for w, h in DRAFT_GEOMETRY_TABLE]
        checked = 0
        max_err = 0.0
        for _ in range(64):
            geom = geometries[rng.randrange(len(geometries))]
            if geom["new_width"] <= 1 or geom["new_height"] <= 1:
                continue
            x1 = rng.random() * 0.6
            y1 = rng.random() * 0.6
            box = (x1, y1, x1 + rng.random() * 0.4, y1 + rng.random() * 0.4)
            back = R.original_norm_to_network_norm(R.network_norm_to_original_norm(box, geom), geom)
            max_err = max(max_err, max(abs(a - b) for a, b in zip(box, back)))
            checked += 1
        self.assertEqual(checked, 64)
        self.assertLess(max_err, 1e-12)


class TestClipAndBorder(unittest.TestCase):
    def test_clip_partial_and_zero_area(self):
        clipped = R.clip_unit_box((-0.2, 0.5, 0.3, 0.9))
        self.assertTrue(clipped["clipped"])
        self.assertFalse(clipped["zero_area"])
        self.assertEqual(clipped["xyxy"], (0.0, 0.5, 0.3, 0.9))
        zero = R.clip_unit_box((-0.2, 0.5, 0.0, 0.9))
        self.assertTrue(zero["zero_area"])
        with self.assertRaises(R.ContractViolation):
            R.clip_unit_box((0.5, 0.5, 0.5, 0.9))   # 上游非正面积

    def test_border_even_width_semantics(self):
        # 线宽 2：几何线 y=1 → {0,1}；y=3 → {2,3}；x=1 → {0,1}；x=3 → {2,3}
        pixels = set(R.border_pixel_sets(1, 1, 3, 3, 2, 10, 10))
        expected = {(x, y) for x in range(1, 4) for y in range(4)} | {
            (x, y) for x in range(4) for y in range(1, 4)
        }
        self.assertEqual(pixels, expected)
        self.assertEqual(len(pixels), 15)
        # 奇数线宽必须拒绝（G0 只固定偶数语义）
        with self.assertRaises(R.ContractViolation):
            R.border_pixel_sets(1, 1, 3, 3, 3, 10, 10)

    def test_border_pixels_clamped(self):
        pixels = R.border_pixel_sets(0, 0, 5, 5, 2, 6, 6)
        self.assertTrue(all(0 <= x < 6 and 0 <= y < 6 for x, y in pixels))
        self.assertIn((0, 0), pixels)


class TestDisplayCanvasAndStale(unittest.TestCase):
    def test_display_px_round_half_up(self):
        # 原图归一化 0.5、画布宽 5 → 0.5*(5-1) = 2.0 → 2；0.3*(5-1)=1.2 → 1；0.4*(5-1)=1.6 → 2
        px = R.original_norm_to_display_px((0.3, 0.4, 0.5, 0.5), 5, 5)
        self.assertEqual(px, {"x1": 1, "y1": 2, "x2": 2, "y2": 2})

    def test_canvas_fit_no_stretch(self):
        fit = R.canvas_fit(1280, 720, 1920, 1080)
        self.assertEqual(fit, {"scale_k": 1, "drawn_width": 1280, "drawn_height": 720,
                               "offset_x": 320, "offset_y": 180})
        fit2 = R.canvas_fit(640, 480, 1920, 1080)
        self.assertEqual(fit2["scale_k"], 2)
        # 端点语义：u=1.0 映射到最后一个源像素（640-1），再乘整数倍并加偏移
        box = R.original_norm_to_canvas_px((0.0, 0.0, 1.0, 1.0), fit2)
        self.assertEqual(box, {"x1": 320, "y1": 60, "x2": 1598, "y2": 1018})
        self.assertGreaterEqual(box["x1"], fit2["offset_x"])
        self.assertLess(box["x2"], fit2["offset_x"] + fit2["drawn_width"])
        with self.assertRaises(R.ContractViolation):
            R.canvas_fit(1280, 720, 640, 480)      # 画布小于源帧

    def test_stale_boundary_and_reasons(self):
        self.assertFalse(R.is_stale(R.STALE_AGE_LIMIT_NS))
        self.assertTrue(R.is_stale(R.STALE_AGE_LIMIT_NS + 1))
        self.assertEqual(R.effective_stale(False, R.STALE_AGE_LIMIT_NS)["reason"], R.STALE_REASON_NONE)
        self.assertEqual(R.effective_stale(True, 1)["reason"], R.STALE_REASON_FLAG)
        self.assertEqual(R.effective_stale(False, R.STALE_AGE_LIMIT_NS + 1)["reason"], R.STALE_REASON_AGE)
        self.assertEqual(R.effective_stale(True, R.STALE_AGE_LIMIT_NS + 1)["reason"], R.STALE_REASON_BOTH)

    def test_compute_ages_and_no_time_travel(self):
        ages = R.compute_ages(capture_time_ns=1_000, result_time_ns=3_000, overlay_commit_ns=5_000)
        self.assertEqual(ages["age_result_ns"], 2_000)
        self.assertEqual(ages["age_frame_ns"], 4_000)
        self.assertEqual(ages["display_semantics"], R.DISPLAY_SEMANTICS)
        with self.assertRaises(R.ContractViolation):
            R.compute_ages(1_000, 5_000, 4_000)


class TestRecordValidation(unittest.TestCase):
    def _record(self, **overrides):
        # 2026-10-27（S5-T04 冻结轮）：result 契约已要求 session_id/result_seq/repeat_index（r04 join-key），
        # 本夹具补上这三个必需字段（仅测试夹具，不改任何判定语义）。
        record = {
            "session_id": 7, "frame_id": 7, "result_seq": 1, "repeat_index": 1,
            "geometry": {"width": 1280, "height": 720}, "state": "OK",
            "detection_count": 1,
            "detections": [{"class_id": 0, "class_name": "fist", "score": 0.83,
                            "xyxy": [0.1, 0.2, 0.3, 0.4], "source_order": 1}],
            "stale": False, "dropped_frames": 0, "capture_time_ns": 100, "result_time_ns": 200,
            "inference_time_ns": 50, "end_to_end_latency_ns": 100, "error_code": 0,
        }
        record.update(overrides)
        return record

    def test_valid_record_passes(self):
        self.assertEqual(R.validate_result_record(self._record()), [])

    def test_missing_field_detected(self):
        record = self._record()
        del record["stale"]
        self.assertTrue(any("stale" in p for p in R.validate_result_record(record)))

    def test_no_hand_with_boxes_rejected(self):
        record = self._record(state="NO_HAND")
        self.assertTrue(any("NO_HAND" in p for p in R.validate_result_record(record)))

    def test_count_mismatch_and_bad_class(self):
        record = self._record(detection_count=3)
        self.assertTrue(any("detection_count" in p for p in R.validate_result_record(record)))
        bad = self._record()
        bad["detections"][0]["class_name"] = "palm"
        self.assertTrue(any("class_name" in p for p in R.validate_result_record(bad)))


class TestContractJsonConsistency(unittest.TestCase):
    """契约 JSON 与参考实现常量必须逐项一致，防止两处漂移。"""

    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_scoring_constants(self):
        scoring = self.contract["scoring"]
        self.assertEqual(scoring["score_threshold"], R.SCORE_THRESHOLD)
        self.assertEqual(scoring["nms_iou"], R.NMS_IOU)
        self.assertEqual(scoring["max_outputs_per_image"], R.MAX_OUTPUTS_PER_IMAGE)
        self.assertEqual(tuple(scoring["class_order"]), R.CLASS_ORDER)
        self.assertEqual(scoring["score_text_tolerance"], 0.001)
        self.assertEqual(scoring["display_word"], "score")

    def test_gate_constants(self):
        gate = self.contract["coordinate_gate"]
        self.assertEqual(gate["A_numeric_chain"]["score_abs_tolerance"], 1e-06)
        self.assertEqual(gate["A_numeric_chain"]["xyxy_abs_tolerance"], 1e-06)
        self.assertEqual(gate["A_numeric_chain"]["relative_tolerance"], 0)
        self.assertEqual(gate["B_display_pixel_layer"]["inverse_mapping_vs_float64_reference_px"], 1.0)
        self.assertEqual(gate["B_display_pixel_layer"]["draw_fidelity_px"], 1.0)
        self.assertEqual(gate["B_display_pixel_layer"]["line_width_half_pixel_px"], 0.5)

    def test_layout_and_reference_binding(self):
        layout = self.contract["overlay_layout"]
        self.assertEqual(layout["line_width_px_1080p"], R.DISPLAY_LINE_WIDTH_PX)
        self.assertEqual(layout["safe_area_px_1080p"], R.SAFE_AREA_PX_1080P)
        self.assertEqual(tuple(layout["hud_fields"]), R.HUD_FIELDS)
        self.assertEqual(self.contract["geometry"]["rounding_rule_id"], R.ROUNDING_RULE)
        self.assertEqual(self.contract["geometry"]["network_input"]["width"], R.NETWORK_INPUT_W)
        self.assertEqual(self.contract["display_semantics"]["value"], R.DISPLAY_SEMANTICS)
        self.assertEqual(self.contract["stale_and_age"]["stale_age_limit_ns"], R.STALE_AGE_LIMIT_NS)
        self.assertEqual(self.contract["reference_implementation"]["path"],
                         "verification/s5_display_geometry_reference.py")
        self.assertEqual(self.contract["reference_implementation"]["rounding_rule"], R.ROUNDING_RULE)

    def test_consumed_field_lists(self):
        consumed = self.contract["consumed_stage4_record"]
        self.assertEqual(tuple(consumed["required_fields"]), R.CONSUMED_STAGE4_FIELDS)
        self.assertEqual(tuple(consumed["detection_fields"]), R.DETECTION_FIELDS)
        self.assertEqual(consumed["mode"], "方案 B：显示层只消费 PS 侧记录")

    def test_test_case_ids_and_status_honesty(self):
        cases = {case["id"]: case["status"] for case in self.contract["test_cases"]}
        self.assertEqual(set(cases), {f"T5-{i:02d}" for i in range(1, 13)})
        self.assertIn("NOT_RUN_NEEDS_HARDWARE", cases["T5-09"])
        self.assertIn("NOT_RUN", cases["T5-09"])
        self.assertEqual(self.contract["status"], "STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)