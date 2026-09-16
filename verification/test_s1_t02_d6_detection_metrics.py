"""S1-T02-D6 离线检测指标的隔离夹具测试。"""

from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

try:
    import verification.s1_t02_d6_detection_metrics as metrics
except ModuleNotFoundError:
    import s1_t02_d6_detection_metrics as metrics


class DetectionMetricsTest(unittest.TestCase):
    """覆盖输入绑定、NMS、匹配、AP 和 G0 pending 语义。"""

    def _fixture(self, labels_a: str = "0 0.5 0.5 0.4 0.4\n", labels_b: str = "") -> dict[str, Path]:
        """创建不依赖外部数据的两图 val 夹具。"""

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "labels").mkdir()
        (root / "labels" / "a.txt").write_text(labels_a, encoding="utf-8")
        (root / "labels" / "b.txt").write_text(labels_b, encoding="utf-8")
        manifest = root / "manifest.csv"
        manifest.write_text(
            "image,label,split,session_id,person_id,source,license,is_real\n"
            "images/a.jpg,labels/a.txt,val,s1,p1,test,ok,1\n"
            "images/b.jpg,labels/b.txt,val,s2,p2,test,ok,1\n",
            encoding="utf-8",
        )
        names = root / "gesture.names"
        names.write_text("fist\npalm\none\ntwo_up\nthree\n", encoding="utf-8")
        return {"root": root, "manifest": manifest, "labels": root / "labels", "names": names}

    def _records(self, a_objects: list[dict], b_objects: list[dict]) -> list[dict]:
        """按 manifest 顺序构造 Darknet 风格数组记录。"""

        return [
            {"filename": "images/a.jpg", "frame_id": 1, "objects": a_objects},
            {"filename": "images/b.jpg", "frame_id": 2, "objects": b_objects},
        ]

    def _relative_object(self, name: str = "fist", confidence: float = 0.9, class_id: int | None = 0, **coords: float) -> dict:
        """构造带 relative_coordinates 的预测对象。"""

        value = {"name": name, "confidence": confidence, "relative_coordinates": {
            "center_x": coords.get("center_x", 0.5),
            "center_y": coords.get("center_y", 0.5),
            "width": coords.get("width", 0.4),
            "height": coords.get("height", 0.4),
        }}
        if class_id is not None:
            value["class_id"] = class_id
        return value

    def _load_and_evaluate(
        self,
        records: list[dict],
        labels_a: str = "0 0.5 0.5 0.4 0.4\n",
        labels_b: str = "",
        score_threshold: object = 0.25,
        nms_iou: object = 0.45,
        max_outputs: object = 15,
    ) -> dict:
        """加载夹具并运行纯函数评估。"""

        fixture = self._fixture(labels_a, labels_b)
        prediction = fixture["root"] / "predictions.json"
        prediction.write_text(json.dumps(records), encoding="utf-8")
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        ground_truths = metrics.load_ground_truths(entries)
        bound = metrics.bind_predictions(prediction, entries, fixture["root"])
        return metrics.evaluate_metrics(entries, ground_truths, bound, score_threshold, nms_iou, max_outputs)

    def test_perfect_prediction_has_hand_computable_map_and_empty_class_support(self) -> None:
        """完美框得到1.0，空 GT 类别保留 null 而不是静默计零。"""

        result = self._load_and_evaluate(self._records([self._relative_object()], []))
        self.assertEqual(result["image_count"], 2)
        self.assertEqual(result["ground_truth_box_count"], 1)
        self.assertAlmostEqual(result["metrics"]["mAP@0.5"], 1.0)
        self.assertAlmostEqual(result["metrics"]["mAP@0.5:0.95"], 1.0)
        self.assertEqual(result["metrics"]["per_class"]["fist"]["tp"], 1)
        self.assertEqual(result["metrics"]["per_class"]["fist"]["fn"], 0)
        self.assertIsNone(result["metrics"]["per_class"]["palm"]["ap_at_0_50"])

    def test_xyxy_requires_explicit_self_describing_format(self) -> None:
        """xyxy 必须自描述，不能根据数值猜格式。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "predictions.json"
        prediction.write_text(json.dumps({
            "coordinate_format": "xyxy_normalized",
            "records": [
                {"filename": "images/a.jpg", "objects": [{"name": "fist", "confidence": 0.9, "xyxy": [0.3, 0.3, 0.7, 0.7]}]},
                {"filename": "images/b.jpg", "objects": []},
            ],
        }), encoding="utf-8")
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        bound = metrics.bind_predictions(prediction, entries, fixture["root"])
        self.assertEqual(bound[entries[0].key][0].box, (0.3, 0.3, 0.7, 0.7))
        prediction.write_text(json.dumps({
            "coordinate_format": "xyxy_normalized",
            "records": [
                {"filename": "images/a.jpg", "objects": [self._relative_object()]},
                {"filename": "images/b.jpg", "objects": []},
            ],
        }), encoding="utf-8")
        with self.assertRaises(metrics.EvaluationError):
            metrics.bind_predictions(prediction, entries, fixture["root"])
        prediction.write_text(json.dumps(self._records([{"name": "fist", "confidence": 0.9, "xyxy": [0.3, 0.3, 0.7, 0.7]}], [])), encoding="utf-8")
        with self.assertRaises(metrics.EvaluationError):
            metrics.bind_predictions(prediction, entries, fixture["root"])

    def test_jsonl_coordinate_format_conflict_is_rejected(self) -> None:
        """JSONL 后续记录不能改变前序记录的坐标格式。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "conflict.jsonl"
        first, second = self._records([self._relative_object()], [])[0], self._records([], [])[1]
        second = {
            "filename": second["filename"],
            "frame_id": 2,
            "coordinate_format": "xyxy_normalized",
            "objects": [{"name": "fist", "confidence": 0.8, "xyxy": [0.3, 0.3, 0.7, 0.7]}],
        }
        prediction.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8")
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        with self.assertRaises(metrics.EvaluationError):
            metrics.bind_predictions(prediction, entries, fixture["root"])

    def test_pure_evaluate_metrics_rejects_invalid_fixed_and_score_configuration(self) -> None:
        """纯函数入口在切片前拒绝非法 max_outputs 和 score threshold。"""

        records = self._records([self._relative_object()], [])
        for value in (15.0, True, 14, 16):
            with self.subTest(max_outputs=value):
                with self.assertRaises(metrics.EvaluationError):
                    self._load_and_evaluate(records, max_outputs=value)
        for value in (0.0, 0.24, 0.51, 1.0, float("nan"), float("inf"), "0.30"):
            with self.subTest(score_threshold=value):
                with self.assertRaises(metrics.EvaluationError):
                    self._load_and_evaluate(records, score_threshold=value)

    def test_nms_is_classwise_score_filtered_and_stable_for_equal_scores(self) -> None:
        """同类重复框抑制，异类重叠框保留，同分保持输入顺序。"""

        first = self._relative_object("fist", 0.9)
        duplicate = self._relative_object("fist", 0.8)
        different = self._relative_object("palm", 0.8, class_id=1)
        kept = metrics.stable_nms(
            [metrics.Prediction("a", 0, "fist", 0.8, (0.1, 0.1, 0.2, 0.2), 0), metrics.Prediction("a", 0, "fist", 0.8, (0.3, 0.3, 0.4, 0.4), 1)],
            0.8,
            0.45,
            15,
        )
        self.assertEqual([item.source_order for item in kept], [0, 1])
        result = self._load_and_evaluate(self._records([first, duplicate, different], []))
        self.assertEqual(result["prediction_box_count_raw"], 3)
        self.assertEqual(result["prediction_box_count_after_score_nms"], 2)
        self.assertEqual(result["metrics"]["per_class"]["fist"]["fp"], 0)
        self.assertEqual(result["metrics"]["per_class"]["palm"]["fp"], 1)

    def test_iou_boundary_and_wrong_class_are_deterministic(self) -> None:
        """IoU 恰为0.5可匹配，略低于边界不能匹配，错类形成 FP/FN。"""

        self.assertAlmostEqual(metrics.box_iou((0, 0, 1, 1), (0.5, 0, 1, 1)), 0.5)
        result = self._load_and_evaluate(
            self._records(
                [
                    self._relative_object(
                        "fist", 0.9, center_x=0.75, width=0.5, height=1.0
                    )
                ],
                [],
            ),
            labels_a="0 0.5 0.5 1 1\n",
        )
        self.assertEqual(result["metrics"]["per_class"]["fist"]["tp"], 1)
        below = self._load_and_evaluate(
            self._records(
                [
                    self._relative_object(
                        "fist", 0.9, center_x=0.75000005, width=0.4999999, height=1.0
                    )
                ],
                [],
            ),
            labels_a="0 0.5 0.5 1 1\n",
        )
        self.assertEqual(below["metrics"]["per_class"]["fist"]["tp"], 0)
        wrong = self._relative_object("palm", 0.9, class_id=1)
        result = self._load_and_evaluate(self._records([wrong], []))
        self.assertEqual(result["metrics"]["per_class"]["fist"]["fn"], 1)
        self.assertEqual(result["metrics"]["per_class"]["palm"]["fp"], 1)

    def test_average_precision_101_point_known_examples(self) -> None:
        """验证101点 all-point 插值的完美和先误报后命中例子。"""

        self.assertEqual(metrics.average_precision([True], [False], 1), 1.0)
        self.assertAlmostEqual(metrics.average_precision([False, True], [True, False], 1), 0.5)
        self.assertIsNone(metrics.average_precision([], [], 0))

    def test_empty_label_no_hand_zero_prediction_and_bound_false_positive_rate(self) -> None:
        """空标签图可以评估，提供 subset 时零框率为0而不是未执行。"""

        result = self._load_and_evaluate(self._records([self._relative_object()], []))
        self.assertEqual(result["ground_truth_box_count"], 1)
        fixture = self._fixture()
        subset = fixture["root"] / "no_hand.list"
        subset.write_text("images/b.jpg\n", encoding="utf-8")
        predictions = fixture["root"] / "predictions.json"
        predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
        args = Namespace(
            manifest=fixture["manifest"], data_root=fixture["root"], labels_root=fixture["labels"], predictions=predictions,
            class_names=fixture["names"], split="val", score_threshold=0.25, nms_iou=0.45, max_outputs=15,
            no_hand_list=subset, non_target_list=None, report=fixture["root"] / "report.json", summary=fixture["root"] / "summary.md",
        )
        report = metrics.build_report(args)
        self.assertEqual(report["status"], "G0_PENDING")
        self.assertEqual(report["subsets"]["no_hand"]["false_positive_rate"], 0.0)
        self.assertEqual(report["subsets"]["non_target"]["status"], "NOT_EXECUTED")

    def test_binding_rejects_missing_duplicate_extra_wrong_order_and_invalid_class(self) -> None:
        """filename/frame_id 集合、顺序和类别错误均必须拒绝。"""

        fixture = self._fixture()
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        cases = [
            self._records([], [])[:-1],
            [{"filename": "images/a.jpg", "objects": []}, {"filename": "images/a.jpg", "objects": []}],
            [{"filename": "images/a.jpg", "objects": []}, {"filename": "images/c.jpg", "objects": []}],
            [{"filename": "images/b.jpg", "frame_id": 1, "objects": []}, {"filename": "images/a.jpg", "frame_id": 2, "objects": []}],
            self._records([self._relative_object("not-a-class", 0.9)], []),
            self._records([self._relative_object("fist", 0.9, class_id=1)], []),
        ]
        for index, records in enumerate(cases):
            with self.subTest(index=index):
                prediction = fixture["root"] / f"bad_{index}.json"
                prediction.write_text(json.dumps(records), encoding="utf-8")
                with self.assertRaises(metrics.EvaluationError):
                    metrics.bind_predictions(prediction, entries, fixture["root"])

    def test_label_and_prediction_numeric_validation_rejects_invalid_values(self) -> None:
        """标签和预测的非有限、越界及非法类别值不能静默接受。"""

        fixture = self._fixture(labels_a="5 0.5 0.5 0.4 0.4\n")
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        with self.assertRaises(metrics.EvaluationError):
            metrics.load_ground_truths(entries)
        fixture = self._fixture()
        prediction = fixture["root"] / "bad.json"
        prediction.write_text(json.dumps(self._records([self._relative_object(confidence=float("nan"))], [])), encoding="utf-8")
        with self.assertRaises(metrics.EvaluationError):
            metrics.bind_predictions(prediction, entries, fixture["root"])

    def test_cli_writes_g0_pending_report_and_rejects_output_aliases(self) -> None:
        """CLI 输出可解析且输入、报告、摘要同路径时返回2。"""

        fixture = self._fixture()
        predictions = fixture["root"] / "predictions.json"
        predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
        report_path = fixture["root"] / "report.json"
        summary_path = fixture["root"] / "summary.md"
        args = [
            "--manifest", str(fixture["manifest"]), "--data-root", str(fixture["root"]), "--labels-root", str(fixture["labels"]),
            "--predictions", str(predictions), "--class-names", str(fixture["names"]), "--split", "val",
            "--score-threshold", "0.25", "--report", str(report_path), "--summary", str(summary_path),
        ]
        self.assertEqual(metrics.main(args), 0)
        generated = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(generated["status"], "G0_PENDING")
        self.assertEqual(generated["validation"]["errors"], [])
        self.assertTrue(summary_path.is_file())
        alias = fixture["root"] / "alias.json"
        base = args[:-6]
        self.assertEqual(metrics.main(base + ["--score-threshold", "0.25", "--report", str(alias), "--summary", str(alias)]), 2)
        self.assertEqual(metrics.main(base + ["--score-threshold", "0.25", "--report", str(predictions), "--summary", str(fixture["root"] / "other.md")]), 2)
        fixed_base = args[:args.index("--report")]
        self.assertEqual(
            metrics.main(
                fixed_base
                + ["--nms-iou", "0.10", "--report", str(fixture["root"] / "bad_nms.json"), "--summary", str(fixture["root"] / "bad_nms.md")]
            ),
            2,
        )
        self.assertEqual(
            metrics.main(
                fixed_base
                + ["--max-outputs", "1", "--report", str(fixture["root"] / "bad_max.json"), "--summary", str(fixture["root"] / "bad_max.md")]
            ),
            2,
        )

    def test_jsonl_and_score_threshold_boundary_are_supported(self) -> None:
        """JSONL 每行记录可读，等于阈值的预测保留。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "predictions.jsonl"
        prediction.write_text(
            json.dumps(self._records([self._relative_object(confidence=0.25)], [] )[0]) + "\n" +
            json.dumps(self._records([], [])[1]) + "\n",
            encoding="utf-8",
        )
        entries = metrics.load_manifest(fixture["manifest"], fixture["root"], fixture["labels"], "val")
        bound = metrics.bind_predictions(prediction, entries, fixture["root"])
        self.assertEqual(len(bound[entries[0].key]), 1)


if __name__ == "__main__":
    unittest.main()
