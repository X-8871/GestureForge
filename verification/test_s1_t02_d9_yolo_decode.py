"""S1-T02-D9 检测头参考解码器的合成黄金测例。"""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import verification.s1_t02_d9_yolo_decode as decoder
except ModuleNotFoundError:
    import s1_t02_d9_yolo_decode as decoder


def _empty_heads() -> dict[str, list[float]]:
    """建立两个全低分、符合 Darknet entry-plane 布局的头。"""

    return {
        spec.name: [-100.0] * (3 * decoder.ENTRY_COUNT * spec.grid_width * spec.grid_height)
        for spec in decoder.HEAD_SPECS
    }


def _set_value(
    heads: dict[str, list[float]],
    head_name: str,
    local_anchor: int,
    entry: int,
    row: int,
    col: int,
    value: float,
) -> None:
    """按 Darknet entry_index 的平面顺序写入一个 raw logit。"""

    spec = next(item for item in decoder.HEAD_SPECS if item.name == head_name)
    spatial = spec.grid_width * spec.grid_height
    index = (local_anchor * decoder.ENTRY_COUNT + entry) * spatial + row * spec.grid_width + col
    heads[head_name][index] = value


def _as_anchor_entry_tensor(flat: list[float], head_name: str) -> list[list[list[list[float]]]]:
    """将 Darknet 一维扁平布局重排为 [anchor,entry,row,col]。"""

    spec = next(item for item in decoder.HEAD_SPECS if item.name == head_name)
    spatial = spec.grid_width * spec.grid_height
    return [
        [
            [
                [flat[(anchor * decoder.ENTRY_COUNT + entry) * spatial + row * spec.grid_width + col]
                 for col in range(spec.grid_width)]
                for row in range(spec.grid_height)
            ]
            for entry in range(decoder.ENTRY_COUNT)
        ]
        for anchor in range(3)
    ]


def _activate(
    heads: dict[str, list[float]],
    head_name: str = "13x13",
    local_anchor: int = 0,
    row: int = 6,
    col: int = 6,
    tx: float = 0.0,
    ty: float = 0.0,
    tw: float = 0.0,
    th: float = 0.0,
    obj: float = 0.0,
    classes: dict[int, float] | None = None,
) -> None:
    """在背景低分张量中开启一个指定 anchor/cell。"""

    _set_value(heads, head_name, local_anchor, 0, row, col, tx)
    _set_value(heads, head_name, local_anchor, 1, row, col, ty)
    _set_value(heads, head_name, local_anchor, 2, row, col, tw)
    _set_value(heads, head_name, local_anchor, 3, row, col, th)
    _set_value(heads, head_name, local_anchor, 4, row, col, obj)
    for class_id, logit in (classes or {0: 0.0}).items():
        _set_value(heads, head_name, local_anchor, 5 + class_id, row, col, logit)


class YoloDecodeTest(unittest.TestCase):
    """验证手算坐标、D8 两头映射、筛选与异常输入。"""

    def test_hand_computable_scale_anchor_score_and_letterbox_golden(self) -> None:
        """手算 x/y scale、D8 anchor mask、乘积分数与奇数 padding 逆变换。"""

        heads = _empty_heads()
        _activate(heads, tx=math.log(3.0), ty=-math.log(3.0), obj=0.0, classes={0: 0.0})
        found = decoder.decode_yolov4_tiny416(
            heads, "golden.jpg", 200, 99, score_threshold=0.25
        )

        self.assertEqual(len(found), 1)
        prediction = found[0]
        self.assertEqual((prediction.class_id, prediction.name), (0, "fist"))
        self.assertAlmostEqual(prediction.confidence, 0.5 * 0.5, places=15)
        self.assertEqual(prediction.source_order, ((6 * 13 + 6) * 3) * 5)
        expected = (1759 / 4160, 268 / 1025, 2569 / 4160, 678 / 1025)
        for actual, manual in zip(prediction.box, expected):
            self.assertAlmostEqual(actual, manual, places=14)

    def test_second_head_uses_its_configured_anchor_mask_and_grid(self) -> None:
        """26×26 头 local anchor 0 按 D8 mask=1 映射到 23×27 anchor。"""

        heads = _empty_heads()
        _activate(heads, head_name="26x26", local_anchor=0, row=13, col=13)
        found = decoder.decode_yolov4_tiny416(
            heads, "fine.jpg", 416, 416, score_threshold=0.25
        )
        tensor_heads = {
            name: _as_anchor_entry_tensor(values, name)
            for name, values in heads.items()
        }
        tensor_found = decoder.decode_yolov4_tiny416(
            tensor_heads, "fine.jpg", 416, 416, score_threshold=0.25
        )

        self.assertEqual(len(found), 1)
        self.assertEqual(tensor_found, found)
        prediction = found[0]
        self.assertAlmostEqual(prediction.box[2] - prediction.box[0], 23 / 416)
        self.assertAlmostEqual(prediction.box[3] - prediction.box[1], 27 / 416)

    def test_empty_and_below_threshold_inputs_return_no_predictions(self) -> None:
        """全低分 raw logits 不会生成 D6 Prediction。"""

        found = decoder.decode_yolov4_tiny416(
            _empty_heads(), "empty.jpg", 416, 416, score_threshold=0.25
        )
        self.assertEqual(found, [])

    def test_same_class_overlap_is_suppressed_but_other_class_is_kept(self) -> None:
        """同一框的同类低分候选被压制，异类相同框保留。"""

        heads = _empty_heads()
        _activate(heads, local_anchor=0, obj=2.0, classes={0: 2.0, 1: 0.0})
        _activate(
            heads,
            local_anchor=1,
            obj=0.0,
            tw=math.log(81 / 135),
            th=math.log(82 / 169),
            classes={0: 2.0},
        )
        found = decoder.decode_yolov4_tiny416(
            heads, "nms.jpg", 416, 416, score_threshold=0.25
        )

        self.assertEqual([item.class_id for item in found], [0, 1])
        self.assertEqual(found[0].box, found[1].box)

    def test_output_limit_is_fifteen(self) -> None:
        """16 个彼此低重叠的候选按 D6 每图上限截为 15 个。"""

        heads = _empty_heads()
        for row in range(3, 7):
            for col in range(3, 7):
                _activate(
                    heads,
                    local_anchor=0,
                    row=row,
                    col=col,
                    obj=2.0,
                    classes={0: 2.0},
                )
        found = decoder.decode_yolov4_tiny416(
            heads, "limit.jpg", 416, 416, score_threshold=0.25
        )
        self.assertEqual(len(found), 15)

    def test_floor_padding_clips_boxes_and_drops_padding_only_boxes(self) -> None:
        """99×200 图像的 211 像素横向补边按左侧 floor=105 逆变换。"""

        heads = _empty_heads()
        _activate(heads, local_anchor=0, row=6, col=0)
        _activate(heads, local_anchor=0, row=6, col=3)
        found = decoder.decode_yolov4_tiny416(
            heads, "padding.jpg", 99, 200, score_threshold=0.25
        )

        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].box[0], 0.0)
        self.assertAlmostEqual(found[0].box[2], 47.5 / 205, places=14)
        self.assertTrue(0.0 <= found[0].box[1] < found[0].box[3] <= 1.0)

    def test_odd_padding_uses_d2_floor_not_darknet_half_pixel(self) -> None:
        """奇数总 pad 时，D2 105 px 与 Darknet C 105.5 px 的边界差为半像素。"""

        heads = _empty_heads()
        _activate(heads, local_anchor=0, row=6, col=3)
        found = decoder.decode_yolov4_tiny416(
            heads, "odd-padding.jpg", 99, 200, score_threshold=0.25
        )

        self.assertEqual(len(found), 1)
        d2_right = 47.5 / 205
        darknet_c_right = 47.0 / 205
        self.assertAlmostEqual(found[0].box[2], d2_right, places=14)
        self.assertAlmostEqual(found[0].box[2] - darknet_c_right, 0.5 / 205, places=14)

    def test_threshold_boundary_uses_d6_greater_or_equal_semantics(self) -> None:
        """obj×class 恰为阈值时 D6 保留，区别于 Darknet 源码 strict greater-than。"""

        heads = _empty_heads()
        _activate(heads, obj=0.0, classes={0: 0.0})
        at_boundary = decoder.decode_yolov4_tiny416(
            heads, "threshold.jpg", 416, 416, score_threshold=0.25
        )
        above_boundary = decoder.decode_yolov4_tiny416(
            heads, "threshold.jpg", 416, 416, score_threshold=0.2500000001
        )

        self.assertEqual(len(at_boundary), 1)
        self.assertEqual(at_boundary[0].confidence, 0.25)
        self.assertEqual(above_boundary, [])

    def test_rejects_wrong_heads_shapes_and_image_dimensions(self) -> None:
        """拒绝缺头、多头、错误扁平长度、错误张量形状及非法原图尺寸。"""

        heads = _empty_heads()
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416({"13x13": heads["13x13"]}, "x", 416, 416, score_threshold=0.25)
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416({**heads, "extra": []}, "x", 416, 416, score_threshold=0.25)
        malformed = dict(heads)
        malformed["13x13"] = heads["13x13"][:-1]
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416(malformed, "x", 416, 416, score_threshold=0.25)
        malformed = dict(heads)
        malformed["26x26"] = [[0.0] * 1]
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416(malformed, "x", 416, 416, score_threshold=0.25)
        for width, height in ((0, 416), (416, -1), (True, 416)):
            with self.subTest(width=width, height=height), self.assertRaises(decoder.DecodeError):
                decoder.decode_yolov4_tiny416(heads, "x", width, height, score_threshold=0.25)

    def test_rejects_invalid_fixed_anchor_mask(self) -> None:
        """配置中重复或越界的 mask 不得静默映射到错误 anchor。"""

        heads = _empty_heads()
        invalid = (
            decoder.HEAD_SPECS[0],
            decoder.HeadSpec("26x26", 26, 26, (1, 3, 6)),
        )
        with patch.object(decoder, "HEAD_SPECS", invalid):
            with self.assertRaisesRegex(decoder.DecodeError, "anchor mask"):
                decoder.decode_yolov4_tiny416(heads, "mask.jpg", 416, 416, score_threshold=0.25)

    def test_evidence_sources_review_and_artifact_hashes_are_consistent(self) -> None:
        """从仓库内核对配置来源、D2/D6 源文件及审查/产物哈希。"""

        repository = Path(__file__).resolve().parents[1]
        evidence_path = repository / "report" / "evidence" / "S1-T02" / "20260917_s1_t02_d9_yolo_decode_r1.json"
        with evidence_path.open("r", encoding="utf-8") as stream:
            evidence = json.load(stream)

        binding = evidence["configuration_binding"]
        self.assertEqual(binding["decoder_input_size"], [416, 416])
        self.assertEqual(binding["class_count"], 5)
        self.assertEqual(binding["scale_x_y"], 1.05)
        sources = {item["id"]: item for item in binding["config_sources"]}
        self.assertEqual(len(sources), len(binding["config_sources"]))
        self.assertEqual(len(sources), 5)
        expected_masks = [[3, 4, 5], [1, 2, 3]]
        expected_sources = {
            "d8_tiny416_formal": (
                True,
                "formal_project_config",
                "5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376",
                [416, 416],
                "runs/s1_t02_d8_tiny416_formal_r1/configs/gesture_yolov4_tiny_416_d8_formal.cfg",
            ),
            "d4_tiny416_formal": (
                True,
                "formal_project_config",
                "5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376",
                [416, 416],
                "runs/s1_t02_d4_float_baseline_r1/configs/gesture_yolov4_tiny_416_d4_formal.cfg",
            ),
            "d4_tiny320_formal": (
                True,
                "formal_project_config",
                "92135520eeed9c77460dde4bab5bd4fd99a171cdba9849cc484bd3c02161fb94",
                [320, 320],
                "runs/s1_t02_d4_float_baseline_r1/configs/gesture_yolov4_tiny_320_d4_formal.cfg",
            ),
            "darknet_upstream_tiny": (
                False,
                "upstream_reference",
                "a6415c2e303f7b3647913a7bb3675f0fe7234049d8875ae7d75c01b8e4dcb854",
                [416, 416],
                "darknet/cfg/yolov4-tiny.cfg",
            ),
        }
        for source_id, (is_formal, expected_type, expected_sha, expected_size, expected_path_suffix) in expected_sources.items():
            with self.subTest(source=source_id):
                source = sources[source_id]
                normalized_path = source["path"].replace("\\", "/")
                self.assertEqual(source["formal"], is_formal)
                self.assertEqual(source["source_type"], expected_type)
                self.assertEqual(source["sha256"], expected_sha)
                self.assertEqual(source["input_size"], expected_size)
                self.assertEqual(source["head_masks"], expected_masks)
                self.assertTrue(normalized_path.endswith(expected_path_suffix))

        nonformal = sources["d4_seeded_custom_nonformal"]
        self.assertFalse(nonformal["formal"])
        self.assertEqual(nonformal["source_type"], "nonformal_seeded_custom_cfg")
        self.assertTrue(
            nonformal["path"].replace("\\", "/").endswith(
                "runs/s1_t02_d4_float_baseline_r1/official_darknet_seeded/cfg/yolov4-tiny-custom.cfg"
            )
        )
        self.assertEqual(
            nonformal["sha256"],
            "4996aceacba657fb8390ac976ed0cf7cdc96085a18bd4827f05f5f2c7f300b8e",
        )
        self.assertEqual(nonformal["head_masks"], [[3, 4, 5], [0, 1, 2]])
        self.assertTrue(nonformal["excluded_from_formal_comparison"])
        self.assertTrue(binding["formal_comparison"]["all_formal_masks_match"])
        self.assertTrue(binding["formal_comparison"]["d8_d4_tiny416_sha256_equal"])
        self.assertEqual(binding["formal_comparison"]["formal_masks"], expected_masks)
        self.assertTrue(binding["formal_comparison"]["nonformal_custom_excluded"])

        expected_basis = {
            "d2_preprocessing": (
                "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
                "df95a8438eaa2d451b54ca3f1927c454eaef022c1f8f31a18874980f69702e57",
            ),
            "d6_metrics": (
                "verification/s1_t02_d6_detection_metrics.py",
                "e2294aef39e51e0e3f4f11efbb527be81b6b38744f34de2fbfa8f3cc1c01346f",
            ),
        }
        for basis_id, (expected_path, expected_sha) in expected_basis.items():
            with self.subTest(source_basis=basis_id):
                basis = evidence["source_basis"][basis_id]
                self.assertEqual(basis["file"], expected_path)
                self.assertEqual(basis["sha256"], expected_sha)
                actual_sha = hashlib.sha256((repository / basis["file"]).read_bytes()).hexdigest()
                self.assertEqual(basis["sha256"], actual_sha)

        review = evidence["review"]
        self.assertEqual(review["initial_frozen_version_status"], "CHANGES_REQUIRED")
        self.assertTrue(review["initial_pass_withdrawn"])
        self.assertEqual(review["review_history"][0]["candidate_number"], 1)
        self.assertEqual(review["review_history"][0]["candidate_status"], "CHANGES_REQUIRED")
        self.assertEqual(review["review_history"][1]["candidate_number"], 2)
        self.assertEqual(review["review_history"][1]["candidate_status"], "CHANGES_REQUIRED")
        self.assertEqual(review["current_repair_iteration"], 2)
        self.assertEqual(review["current_candidate_number"], 3)
        self.assertEqual(review["current_candidate_review_status"], "PASS")
        self.assertTrue(review["current_repair_candidate_is_final_pass"])
        reviewer = review["reviewer"]
        self.assertEqual(reviewer["name"], "Herschel")
        self.assertEqual(reviewer["role"], "multi-agent independent Reviewer")
        self.assertEqual(reviewer["verdict"], "PASS")
        self.assertEqual(
            reviewer["output_directory"],
            r"C:\Users\22061\AppData\Local\Temp\GestureForge_D9_C3_Review_330779624f394a839f2b5d9422b0848a",
        )
        self.assertEqual(
            reviewer["reviewed_candidate_sha256"],
            {
                "verification/s1_t02_d9_yolo_decode.py": "0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6",
                "verification/test_s1_t02_d9_yolo_decode.py": "65cbdea3ef4ef03723fa0757efe57de6d886948d0cedba73786ae5686c544157",
                "report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1.json": "bb7f2b038be0b5a992f332d4173066a6d4efb1ec8ff4c1e34b5f50aa12325a3e",
                "report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1_summary.md": "aad555c2dc4e9ca796daad0979b7f98bf7efdf98412f01946b3e7bea3d546e57",
            },
        )
        self.assertEqual(review["post_review_metadata_recheck"]["status"], "PENDING")
        self.assertFalse(review["post_review_metadata_recheck"]["completed"])

        implementation = evidence["implementation"]
        self.assertEqual(implementation["decoder_file"], "verification/s1_t02_d9_yolo_decode.py")
        self.assertEqual(implementation["test_file"], "verification/test_s1_t02_d9_yolo_decode.py")
        self.assertEqual(
            implementation["summary_file"],
            "report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1_summary.md",
        )
        for file_key, hash_key in (
            ("decoder_file", "decoder_sha256"),
            ("test_file", "test_sha256"),
            ("summary_file", "summary_sha256"),
        ):
            with self.subTest(implementation=file_key):
                source_path = repository / implementation[file_key]
                actual_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
                self.assertEqual(implementation[hash_key], actual_sha)

    def test_rejects_nonfinite_values_and_exponential_overflow(self) -> None:
        """即使低分通道也检查 NaN/Inf，并拒绝有限但导致 exp 溢出的 tw。"""

        heads = _empty_heads()
        _set_value(heads, "26x26", 2, 9, 4, 5, float("nan"))
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416(heads, "nan.jpg", 416, 416, score_threshold=0.25)

        heads = _empty_heads()
        _set_value(heads, "13x13", 0, 2, 6, 6, 1000.0)
        with self.assertRaisesRegex(decoder.DecodeError, "exp 溢出"):
            decoder.decode_yolov4_tiny416(heads, "overflow.jpg", 416, 416, score_threshold=0.25)

        heads = _empty_heads()
        _set_value(heads, "13x13", 1, 4, 1, 1, float("inf"))
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416(heads, "inf.jpg", 416, 416, score_threshold=0.25)

    def test_rejects_invalid_threshold_and_image_key(self) -> None:
        """阈值范围含端点且必填；image_key 需要非空文本。"""

        heads = _empty_heads()
        for threshold in (0.249, 0.501, float("nan"), True):
            with self.subTest(threshold=threshold), self.assertRaises(decoder.DecodeError):
                decoder.decode_yolov4_tiny416(heads, "x", 416, 416, score_threshold=threshold)
        with self.assertRaises(decoder.DecodeError):
            decoder.decode_yolov4_tiny416(heads, "", 416, 416, score_threshold=0.25)


if __name__ == "__main__":
    unittest.main()
