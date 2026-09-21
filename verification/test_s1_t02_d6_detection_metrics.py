"""S1-T02-D6 离线检测指标的隔离夹具测试。"""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import ExitStack, contextmanager, redirect_stderr
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

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

    @contextmanager
    def _bind_fixture_manifest(self, fixture: dict[str, Path], counts: dict[str, int] | None = None):
        """将隔离夹具绑定为测试用批准快照。"""

        expected_counts = counts if counts is not None else {"train": 0, "val": 2, "test": 0}
        digest = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
        with patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", digest):
            with patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", expected_counts):
                yield metrics.create_evaluation_context(
                    fixture["manifest"], fixture["root"], fixture["labels"], "val"
                )

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
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            ground_truths = metrics.load_ground_truths(entries, context)
            bound = metrics.bind_predictions(prediction, entries, context)
            return metrics.evaluate_metrics(entries, ground_truths, bound, score_threshold, nms_iou, max_outputs, context)

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
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            bound = metrics.bind_predictions(prediction, entries, context)
            self.assertEqual(bound[entries[0].key][0].box, (0.3, 0.3, 0.7, 0.7))
            prediction.write_text(json.dumps({
                "coordinate_format": "xyxy_normalized",
                "records": [
                    {"filename": "images/a.jpg", "objects": [self._relative_object()]},
                    {"filename": "images/b.jpg", "objects": []},
                ],
            }), encoding="utf-8")
            with self.assertRaises(metrics.EvaluationError):
                metrics.bind_predictions(prediction, entries, context)
            prediction.write_text(json.dumps(self._records([{"name": "fist", "confidence": 0.9, "xyxy": [0.3, 0.3, 0.7, 0.7]}], [])), encoding="utf-8")
            with self.assertRaises(metrics.EvaluationError):
                metrics.bind_predictions(prediction, entries, context)

    def test_prediction_coordinates_clip_and_keep_raw_diagnostics(self) -> None:
        """有限正面积的预测框裁剪后参与评估，并保留 raw 坐标诊断。"""

        relative = self._relative_object(center_x=0.05, width=0.2)
        result = self._load_and_evaluate(self._records([relative], []))
        self.assertEqual(result["coordinate_policy"]["raw_out_of_range_box_count"], 1)
        self.assertEqual(result["coordinate_policy"]["clipped_box_count"], 1)
        prediction = next(iter(result["predictions_after_nms"].values()))[0]
        self.assertEqual(prediction.box, (0.0, 0.3, 0.15000000000000002, 0.7))
        self.assertEqual(prediction.raw_box, (-0.05, 0.3, 0.15000000000000002, 0.7))
        self.assertTrue(prediction.coordinate_clipped)

        wide = self._load_and_evaluate(self._records([self._relative_object(width=1.2)], []))
        self.assertEqual(wide["coordinate_policy"]["clipped_box_count"], 1)
        wide_prediction = next(iter(wide["predictions_after_nms"].values()))[0]
        self.assertTrue(wide_prediction.coordinate_clipped)

    def test_prediction_coordinates_reject_zero_area_after_clip_and_raw_non_positive(self) -> None:
        """完全在图像外或原始非正面积框不能被 clip 静默接受。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "bad_coordinates.json"
        cases = [
            self._records([{"name": "fist", "confidence": 0.9, "xyxy": [1.1, 0.2, 1.2, 0.3]}], []),
            self._records([{"name": "fist", "confidence": 0.9, "xyxy": [0.6, 0.2, 0.4, 0.3]}], []),
        ]
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            for records in cases:
                prediction.write_text(
                    json.dumps({"coordinate_format": "xyxy_normalized", "records": records}), encoding="utf-8"
                )
                with self.assertRaises(metrics.EvaluationError):
                    metrics.bind_predictions(prediction, entries, context)

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
        with self.assertRaises(metrics.EvaluationError):
            with self._bind_fixture_manifest(fixture) as context:
                entries = metrics.load_manifest(context)
                metrics.bind_predictions(prediction, entries, context)

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
        with self._bind_fixture_manifest(fixture):
            report = metrics.build_report(args)
        self.assertEqual(report["status"], "G0_PENDING")
        self.assertEqual(report["subsets"]["no_hand"]["false_positive_rate"], 0.0)
        self.assertEqual(report["subsets"]["non_target"]["status"], "NOT_EXECUTED")

    def test_binding_rejects_missing_duplicate_extra_wrong_order_and_invalid_class(self) -> None:
        """filename/frame_id 集合、顺序和类别错误均必须拒绝。"""

        fixture = self._fixture()
        cases = [
            self._records([], [])[:-1],
            [{"filename": "images/a.jpg", "objects": []}, {"filename": "images/a.jpg", "objects": []}],
            [{"filename": "images/a.jpg", "objects": []}, {"filename": "images/c.jpg", "objects": []}],
            [{"filename": "images/b.jpg", "frame_id": 1, "objects": []}, {"filename": "images/a.jpg", "frame_id": 2, "objects": []}],
            self._records([self._relative_object("not-a-class", 0.9)], []),
            self._records([self._relative_object("fist", 0.9, class_id=1)], []),
        ]
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            for index, records in enumerate(cases):
                with self.subTest(index=index):
                    prediction = fixture["root"] / f"bad_{index}.json"
                    prediction.write_text(json.dumps(records), encoding="utf-8")
                    with self.assertRaises(metrics.EvaluationError):
                        metrics.bind_predictions(prediction, entries, context)

    def test_label_and_prediction_numeric_validation_rejects_invalid_values(self) -> None:
        """标签和预测的非有限、越界及非法类别值不能静默接受。"""

        fixture = self._fixture(labels_a="5 0.5 0.5 0.4 0.4\n")
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            with self.assertRaises(metrics.EvaluationError):
                metrics.load_ground_truths(entries, context)
        fixture = self._fixture()
        prediction = fixture["root"] / "bad.json"
        prediction.write_text(json.dumps(self._records([self._relative_object(confidence=float("nan"))], [])), encoding="utf-8")
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            with self.assertRaises(metrics.EvaluationError):
                metrics.bind_predictions(prediction, entries, context)

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
        with self._bind_fixture_manifest(fixture):
            self.assertEqual(metrics.main(args), 0)
        generated = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(generated["status"], "G0_PENDING")
        self.assertEqual(generated["validation"]["errors"], [])
        policy = generated["sample_policy"]
        self.assertEqual(policy["decision_date"], "2026-09-18")
        self.assertEqual(policy["decision_document"]["sha256"], metrics.G0_POLICY_DOCUMENT_SHA256)
        self.assertEqual(
            policy["official_test"]["approved_manifest_sha256"],
            hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest(),
        )
        self.assertEqual(policy["official_test"]["required_image_count"], 25484)
        self.assertEqual(policy["official_test"]["runtime_binding_status"], "NOT_EVALUATED")
        self.assertEqual(policy["robustness"]["target_classes"], metrics.EXPECTED_CLASSES)
        self.assertEqual(policy["robustness"]["minimum_unique_images_per_class"], 100)
        self.assertEqual(policy["robustness"]["condition_bucket_minimum_unique_images"], metrics.ROBUSTNESS_CONDITION_BUCKETS)
        self.assertEqual(policy["robustness"]["dataset_binding_status"], "PENDING")
        self.assertIsNone(policy["robustness"]["observed_counts"])
        self.assertEqual(
            {item["id"] for item in generated["g0_open_items"]},
            {"complete_metric_policy_snapshot", "final_score_threshold", "map_acceptance_threshold", "per_class_precision_recall_thresholds", "robustness_dataset_and_isolation"},
        )
        self.assertEqual(policy["metric_policy_evidence"]["status"], "MISSING")
        self.assertIsNone(policy["metric_policy_evidence"]["binding"])
        self.assertTrue(summary_path.is_file())
        alias = fixture["root"] / "alias.json"
        base = args[:-6]
        with self._bind_fixture_manifest(fixture):
            self.assertEqual(metrics.main(base + ["--score-threshold", "0.25", "--report", str(alias), "--summary", str(alias)]), 2)
            self.assertEqual(metrics.main(base + ["--score-threshold", "0.25", "--report", str(predictions), "--summary", str(fixture["root"] / "other.md")]), 2)
        fixed_base = args[:args.index("--report")]
        with self._bind_fixture_manifest(fixture):
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

    def test_approved_policy_constants_match_the_reviewed_g0_document(self) -> None:
        """样本政策常量及决策文档哈希与正式 G0 文档一致。"""

        repository = Path(metrics.__file__).resolve().parent.parent
        document = repository / metrics.G0_POLICY_DOCUMENT_PATH
        text = document.read_text(encoding="utf-8")
        self.assertEqual(metrics.sha256_file(document), metrics.G0_POLICY_DOCUMENT_SHA256)
        self.assertIn(metrics.APPROVED_TEST_MANIFEST_SHA256, text.lower())
        self.assertIn("25,484", text)
        self.assertIn("fist,palm,one,two_up,three", text)
        self.assertIn("no_hand", text)
        self.assertIn("non-target", text)
        self.assertIn("多手", text)
        self.assertIn("遮挡", text)
        self.assertIn("小目标", text)
        self.assertEqual(metrics.ROBUSTNESS_MIN_IMAGES_PER_CLASS, 100)
        self.assertEqual(set(metrics.ROBUSTNESS_CONDITION_BUCKETS.values()), {100})
        self.assertEqual(
            metrics.APPROVED_SPLIT_IMAGE_COUNTS,
            {"train": 118001, "val": 15195, "test": 25484},
        )
        self.assertEqual(metrics.APPROVED_TEST_IMAGE_COUNT, metrics.APPROVED_SPLIT_IMAGE_COUNTS["test"])

    def test_full_manifest_snapshot_and_each_split_count_are_bound_together(self) -> None:
        """train/val/test 均使用同一完整 manifest 快照并校验全部分区计数。"""

        manifest_bytes = (
            b"image,label,split\n"
            b"images/train.jpg,labels/train.txt,train\n"
            b"images/val.jpg,labels/val.txt,val\n"
            b"images/test.jpg,labels/test.txt,test\n"
        )
        digest = hashlib.sha256(manifest_bytes).hexdigest()
        counts = {"train": 1, "val": 1, "test": 1}
        with patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", digest):
            with patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", counts):
                for split in ("train", "val", "test"):
                    self.assertEqual(metrics._validate_approved_manifest_binding(manifest_bytes, digest, split), 1)
                with self.assertRaisesRegex(metrics.EvaluationError, "SHA-256"):
                    changed_bytes = manifest_bytes + b"\n"
                    changed_digest = hashlib.sha256(changed_bytes).hexdigest()
                    metrics._validate_approved_manifest_binding(changed_bytes, changed_digest, "val")
            with patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 1, "val": 2, "test": 1}):
                for split in ("train", "val", "test"):
                    with self.subTest(split=split):
                        with self.assertRaisesRegex(metrics.EvaluationError, "图片数"):
                            metrics._validate_approved_manifest_binding(manifest_bytes, digest, split)

    def test_test_split_rejects_manifest_sha_or_test_count_mismatch_without_report(self) -> None:
        """test manifest SHA 或完整图片数不符时阻断，且不写成功产物。"""

        fixture = self._fixture()
        manifest_text = fixture["manifest"].read_text(encoding="utf-8").replace(",val,", ",test,")
        fixture["manifest"].write_text(manifest_text, encoding="utf-8")
        predictions = fixture["root"] / "predictions.json"
        predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
        report_path = fixture["root"] / "test_report.json"
        summary_path = fixture["root"] / "test_summary.md"
        cli_args = [
            "--manifest", str(fixture["manifest"]), "--data-root", str(fixture["root"]), "--labels-root", str(fixture["labels"]),
            "--predictions", str(predictions), "--class-names", str(fixture["names"]), "--split", "test",
            "--score-threshold", "0.25", "--report", str(report_path), "--summary", str(summary_path),
        ]

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(metrics.main(cli_args), 2)
        self.assertIn("D6_ERROR", stderr.getvalue())
        self.assertIn("SHA-256", stderr.getvalue())
        self.assertFalse(report_path.exists())
        self.assertFalse(summary_path.exists())

        matching_hash = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
        count_report = fixture["root"] / "count_report.json"
        count_summary = fixture["root"] / "count_summary.md"
        count_args = cli_args[:-4] + ["--report", str(count_report), "--summary", str(count_summary)]
        stderr = io.StringIO()
        with patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", matching_hash):
            with patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 0, "val": 0, "test": 3}):
                with redirect_stderr(stderr):
                    self.assertEqual(metrics.main(count_args), 2)
        self.assertIn("图片数", stderr.getvalue())
        self.assertFalse(count_report.exists())
        self.assertFalse(count_summary.exists())

    def test_test_and_robustness_fail_closed_without_metric_policy_evidence(self) -> None:
        """正式 test 与 robustness 即使样本绑定有效、阈值不同也在下游前阻断。"""

        downstream_functions = (
            "_read_class_names",
            "load_manifest",
            "parse_yolo_label",
            "load_ground_truths",
            "bind_predictions",
            "evaluate_metrics",
            "_summary_text",
            "_write_json",
        )
        for split in ("test", "robustness"):
            for threshold in ("0.25", "0.37", "0.50"):
                with self.subTest(split=split, threshold=threshold):
                    fixture = self._fixture()
                    manifest_text = fixture["manifest"].read_text(encoding="utf-8").replace(",val,", f",{split},")
                    fixture["manifest"].write_text(manifest_text, encoding="utf-8")
                    predictions = fixture["root"] / "predictions.json"
                    predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
                    report_path = fixture["root"] / "blocked_report.json"
                    summary_path = fixture["root"] / "blocked_summary.md"
                    cli_args = [
                        "--manifest", str(fixture["manifest"]), "--data-root", str(fixture["root"]), "--labels-root", str(fixture["labels"]),
                        "--predictions", str(predictions), "--class-names", str(fixture["names"]), "--split", split,
                        "--score-threshold", threshold, "--report", str(report_path), "--summary", str(summary_path),
                    ]
                    manifest_sha256 = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
                    stderr = io.StringIO()
                    with ExitStack() as stack:
                        sentinels = {
                            name: stack.enter_context(
                                patch.object(metrics, name, side_effect=AssertionError(f"下游调用不应发生: {name}"))
                            )
                            for name in downstream_functions
                        }
                        summary_writer = stack.enter_context(patch.object(Path, "write_text", autospec=True))
                        if split == "test":
                            stack.enter_context(patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", manifest_sha256))
                            stack.enter_context(patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 0, "val": 0, "test": 2}))
                        with redirect_stderr(stderr):
                            self.assertEqual(metrics.main(cli_args), 2)
                        self.assertIn("D6_ERROR", stderr.getvalue())
                        self.assertIn("G0 指标策略证据", stderr.getvalue())
                        for sentinel in sentinels.values():
                            sentinel.assert_not_called()
                        summary_writer.assert_not_called()
                    self.assertFalse(report_path.exists())
                    self.assertFalse(summary_path.exists())

    def test_direct_metric_apis_require_the_same_verified_context(self) -> None:
        """公共标签、预测和指标 API 只接受原样绑定的不可变验证上下文。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "predictions.json"
        prediction.write_text(json.dumps(self._records([], [])), encoding="utf-8")
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            ground_truths = {entry.key: [] for entry in entries}
            bound_predictions = {entry.key: [] for entry in entries}
            manual_context = replace(context, _seal=None)
            wrong_split_context = replace(context, split="train")
            wrong_sha_context = replace(context, manifest_sha256="0" * 64)
            locked_test_context = replace(context, split="test")
            locked_robustness_context = replace(context, split="robustness")
            with ExitStack() as stack:
                label_reader = stack.enter_context(patch.object(Path, "read_text", autospec=True))
                metric_runner = stack.enter_context(patch.object(metrics, "_match_predictions", side_effect=AssertionError("metric execution")))
                invalid_contexts = (None, manual_context, wrong_split_context, wrong_sha_context, locked_test_context, locked_robustness_context)
                for candidate in invalid_contexts:
                    with self.subTest(candidate=candidate.split if isinstance(candidate, metrics.EvaluationContext) else candidate):
                        with self.assertRaises(metrics.EvaluationError):
                            metrics.load_manifest(candidate)
                        with self.assertRaises(metrics.EvaluationError):
                            metrics.parse_yolo_label(entries[0], candidate)
                        with self.assertRaises(metrics.EvaluationError):
                            metrics.load_ground_truths(entries, candidate)
                        with self.assertRaises(metrics.EvaluationError):
                            metrics.bind_predictions(prediction, entries, candidate)
                        with self.assertRaises(metrics.EvaluationError):
                            metrics.evaluate_metrics(entries, ground_truths, bound_predictions, 0.25, 0.45, 15, candidate)
                        with self.assertRaises(metrics.EvaluationError):
                            metrics._load_prediction_records(prediction, candidate)
                label_reader.assert_not_called()
                metric_runner.assert_not_called()

    def test_direct_factory_blocks_test_and_robustness_before_labels_or_predictions(self) -> None:
        """直接上下文工厂在未批准策略下不返回 test/robustness 条目。"""

        fixture = self._fixture()
        test_text = fixture["manifest"].read_text(encoding="utf-8").replace(",val,", ",test,")
        fixture["manifest"].write_text(test_text, encoding="utf-8")
        test_digest = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
        test_predictions = fixture["root"] / "predictions.json"
        test_predictions.write_text(json.dumps(self._records([], [])), encoding="utf-8")
        with ExitStack() as stack:
            stack.enter_context(patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", test_digest))
            stack.enter_context(patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 0, "val": 0, "test": 2}))
            label_reader = stack.enter_context(patch.object(Path, "read_text", autospec=True))
            with self.assertRaisesRegex(metrics.EvaluationError, "G0 指标策略证据"):
                metrics.create_evaluation_context(fixture["manifest"], fixture["root"], fixture["labels"], "test")
            label_reader.assert_not_called()

        with ExitStack() as stack:
            manifest_reader = stack.enter_context(patch.object(Path, "read_bytes", autospec=True))
            label_reader = stack.enter_context(patch.object(Path, "read_text", autospec=True))
            with self.assertRaisesRegex(metrics.EvaluationError, "G0 指标策略证据"):
                metrics.create_evaluation_context(fixture["manifest"], fixture["root"], fixture["labels"], "robustness")
            manifest_reader.assert_not_called()
            label_reader.assert_not_called()

    def test_direct_api_rejects_relabelled_test_rows_and_keeps_approved_val_working(self) -> None:
        """改标 test 行的 manifest 在直接 API 入口失败，获批 val 链仍可计算。"""

        fixture = self._fixture()
        original = fixture["manifest"].read_text(encoding="utf-8").replace(
            "images/a.jpg,labels/a.txt,val,", "images/a.jpg,labels/a.txt,test,"
        )
        fixture["manifest"].write_text(original, encoding="utf-8")
        approved_test_snapshot_sha = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
        fixture["manifest"].write_text(original.replace(",test,", ",val,"), encoding="utf-8")
        predictions = fixture["root"] / "predictions.json"
        predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
        with ExitStack() as stack:
            stack.enter_context(patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", approved_test_snapshot_sha))
            stack.enter_context(patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 0, "val": 1, "test": 1}))
            label_reader = stack.enter_context(patch.object(Path, "read_text", autospec=True))
            with self.assertRaisesRegex(metrics.EvaluationError, "SHA-256"):
                metrics.create_evaluation_context(fixture["manifest"], fixture["root"], fixture["labels"], "val")
            label_reader.assert_not_called()

        val_fixture = self._fixture()
        val_predictions = val_fixture["root"] / "predictions.json"
        val_predictions.write_text(json.dumps(self._records([self._relative_object()], [])), encoding="utf-8")
        with self._bind_fixture_manifest(val_fixture) as context:
            entries = metrics.load_manifest(context)
            ground_truths = metrics.load_ground_truths(entries, context)
            bound = metrics.bind_predictions(val_predictions, entries, context)
            result = metrics.evaluate_metrics(entries, ground_truths, bound, 0.25, 0.45, 15, context)
        self.assertEqual(context.authorization_state, "VAL_ONLY_G0_PENDING")
        self.assertEqual(result["image_count"], 2)
        self.assertAlmostEqual(result["metrics"]["mAP@0.5"], 1.0)

    def test_noncanonical_split_values_are_rejected_before_manifest_read(self) -> None:
        """大小写与别名 split 在读取 manifest 或任何下游输入前拒绝。"""

        for split in ("TEST", "Test", "test_alt", "valid"):
            with self.subTest(split=split):
                fixture = self._fixture()
                prediction = fixture["root"] / "predictions.json"
                prediction.write_text(json.dumps(self._records([], [])), encoding="utf-8")
                report = fixture["root"] / "report.json"
                summary = fixture["root"] / "summary.md"
                args = [
                    "--manifest", str(fixture["manifest"]), "--data-root", str(fixture["root"]),
                    "--labels-root", str(fixture["labels"]), "--predictions", str(prediction),
                    "--class-names", str(fixture["names"]), "--split", split,
                    "--score-threshold", "0.37", "--report", str(report), "--summary", str(summary),
                ]
                stderr = io.StringIO()
                with ExitStack() as stack:
                    manifest_reader = stack.enter_context(patch.object(Path, "read_bytes", autospec=True))
                    downstream = {
                        name: stack.enter_context(patch.object(metrics, name, side_effect=AssertionError(name)))
                        for name in ("_read_class_names", "load_manifest", "load_ground_truths", "bind_predictions", "evaluate_metrics", "_write_json", "_summary_text")
                    }
                    with redirect_stderr(stderr):
                        self.assertEqual(metrics.main(args), 2)
                    self.assertIn("split 非规范", stderr.getvalue())
                    manifest_reader.assert_not_called()
                    for sentinel in downstream.values():
                        sentinel.assert_not_called()
                self.assertFalse(report.exists())
                self.assertFalse(summary.exists())

    def test_relabelled_test_rows_cannot_be_used_as_val_for_threshold_selection(self) -> None:
        """将 test 行重标为 val 会因完整快照 SHA 不同而在标签和预测读取前阻断。"""

        fixture = self._fixture()
        original = fixture["manifest"].read_text(encoding="utf-8").replace(
            "images/a.jpg,labels/a.txt,val,", "images/a.jpg,labels/a.txt,test,"
        )
        fixture["manifest"].write_text(original, encoding="utf-8")
        approved_hash_before_relabel = hashlib.sha256(fixture["manifest"].read_bytes()).hexdigest()
        relabelled = original.replace(",test,", ",val,")
        fixture["manifest"].write_text(relabelled, encoding="utf-8")
        prediction = fixture["root"] / "predictions.json"
        prediction.write_text(json.dumps(self._records([], [])), encoding="utf-8")
        report = fixture["root"] / "report.json"
        summary = fixture["root"] / "summary.md"
        args = [
            "--manifest", str(fixture["manifest"]), "--data-root", str(fixture["root"]),
            "--labels-root", str(fixture["labels"]), "--predictions", str(prediction),
            "--class-names", str(fixture["names"]), "--split", "val", "--score-threshold", "0.50",
            "--report", str(report), "--summary", str(summary),
        ]
        stderr = io.StringIO()
        with ExitStack() as stack:
            stack.enter_context(patch.object(metrics, "APPROVED_TEST_MANIFEST_SHA256", approved_hash_before_relabel))
            stack.enter_context(patch.object(metrics, "APPROVED_SPLIT_IMAGE_COUNTS", {"train": 0, "val": 1, "test": 1}))
            downstream = {
                name: stack.enter_context(patch.object(metrics, name, side_effect=AssertionError(name)))
                for name in ("_read_class_names", "load_manifest", "parse_yolo_label", "load_ground_truths", "bind_predictions", "evaluate_metrics", "_summary_text", "_write_json")
            }
            summary_writer = stack.enter_context(patch.object(Path, "write_text", autospec=True))
            with redirect_stderr(stderr):
                self.assertEqual(metrics.main(args), 2)
            self.assertIn("D6_ERROR", stderr.getvalue())
            self.assertIn("SHA-256", stderr.getvalue())
            for sentinel in downstream.values():
                sentinel.assert_not_called()
            summary_writer.assert_not_called()
        self.assertFalse(report.exists())
        self.assertFalse(summary.exists())

    def test_jsonl_and_score_threshold_boundary_are_supported(self) -> None:
        """JSONL 每行记录可读，等于阈值的预测保留。"""

        fixture = self._fixture()
        prediction = fixture["root"] / "predictions.jsonl"
        prediction.write_text(
            json.dumps(self._records([self._relative_object(confidence=0.25)], [] )[0]) + "\n" +
            json.dumps(self._records([], [])[1]) + "\n",
            encoding="utf-8",
        )
        with self._bind_fixture_manifest(fixture) as context:
            entries = metrics.load_manifest(context)
            bound = metrics.bind_predictions(prediction, entries, context)
        self.assertEqual(len(bound[entries[0].key]), 1)


if __name__ == "__main__":
    unittest.main()
