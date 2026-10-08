"""离线采集检查的独立手算夹具、异常回归与可复核随机验证。"""

from __future__ import annotations

import copy
import contextlib
import io
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from verification import s2b_fixed_capture_check as checker


RANDOM_SEED = 20261008
RANDOM_BYTE_CASES = 24
RANDOM_EMPTY_FRAMES = 8
INPUT_SHA256 = checker.sha256_bytes(bytes(3 * 416 * 416))


def write_json(path: Path, value: object) -> None:
    """测试只改写本次隔离目录内、由夹具创建的输入。"""

    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _activate(payload: bytearray, grid: int, row: int, col: int, classes: tuple[int, ...]) -> None:
    """在首个 anchor 的 entry-plane 中写零 logits，保留其他背景为 -127。"""

    spatial = grid * grid
    cell = row * grid + col
    for entry in tuple(range(5)) + tuple(5 + class_id for class_id in classes):
        payload[entry * spatial + cell] = 0


def _manual_detection(class_id: int, order: int, coordinates: list[float]) -> dict[str, object]:
    return {"class_id": class_id, "class_name": ("fist", "palm", "one", "two_up", "three")[class_id], "score": 0.25, "xyxy": coordinates, "source_order": order}


def write_fixture(directory: Path, names: tuple[str, ...] = ("single", "empty", "multiclass", "head26")) -> tuple[Path, Path]:
    """不调用 D9，按 sigmoid(0)=1/2、exp(0)=1 和 anchor 尺寸独立生成期望。"""

    reference_rows = []
    capture_rows = []
    source_rows = []
    for index, name in enumerate(names):
        head13 = bytearray([129] * 5070)
        head26 = bytearray([129] * 20280)
        # 网络尺寸 416；head13 的 (6+1/2)/13=1/2，mask[0] 是 81×82。
        coordinates = [335 / 832, 334 / 832, 497 / 832, 498 / 832]
        if name == "single":
            _activate(head13, 13, 6, 6, (0,))
            detections = [_manual_detection(0, 1260, coordinates)]
        elif name == "multiclass":
            _activate(head13, 13, 6, 6, (0, 1))
            detections = [_manual_detection(0, 1260, coordinates), _manual_detection(1, 1261, coordinates)]
        elif name == "head26":
            # (13+1/2)/26=27/52；mask[0] 是 23×27，中心像素为 216。
            _activate(head26, 26, 13, 13, (4,))
            detections = [_manual_detection(4, 2535 + (13 * 26 + 13) * 15 + 4, [409 / 832, 405 / 832, 455 / 832, 459 / 832])]
        elif name == "empty":
            # 所有 objectness/class logits 严格小于零，乘积分数严格小于 1/4。
            detections = []
        else:
            raise ValueError(f"未知手算夹具：{name}")
        row = {"frame_id": 0xFFFFFFFF - index, "sample_id": f"synthetic_{name}_{index}", "input": {"pl_input_sha256": INPUT_SHA256, "geometry_wh": [416, 416]}, "head_tensors": {}, "nms_output_box_count": len(detections), "detections": detections}
        capture = copy.deepcopy(row)
        source = copy.deepcopy(row)
        for head_name, payload in (("head13", head13), ("head26", head26)):
            golden_path = directory / f"{index}_{head_name}_golden.bin"
            capture_path = directory / f"{index}_{head_name}_capture.bin"
            golden_path.write_bytes(payload)
            capture_path.write_bytes(payload)
            binding = {"byte_length": len(payload), "tensor_sha256": checker.sha256_bytes(payload)}
            row["head_tensors"][head_name] = dict(binding, path=str(golden_path))
            capture["head_tensors"][head_name] = dict(binding, path=str(capture_path))
            source["head_tensors"][head_name] = binding
        reference_rows.append(row)
        capture_rows.append(capture)
        source_rows.append(source)
    basis_path = Path(__file__)
    source_path = directory / "golden_source.json"
    write_json(source_path, {"schema_version": 1, "kind": "s2b_synthetic_hand_computed", "model_manifest_sha256": checker.MODEL_SHA256, "basis": {"path": str(basis_path), "sha256": checker.sha256_bytes(basis_path.read_bytes()), "description": "独立手算：零logit的sigmoid为1/2、exp为1；中心、anchor宽高、mask和source_order直接按冻结公式计算。其他背景为-127，故score小于1/4。没有从捕获或运行D9取得期望。"}, "samples": source_rows})
    reference_path = directory / "reference.json"
    capture_path = directory / "capture.json"
    common = {"schema_version": 1, "model_manifest_sha256": checker.MODEL_SHA256}
    write_json(reference_path, dict(common, kind="s2b_fixed_reference", golden_source={"kind": "synthetic_hand_computed", "path": str(source_path), "sha256": checker.sha256_bytes(source_path.read_bytes())}, samples=reference_rows))
    write_json(capture_path, dict(common, kind="s2b_fixed_capture", samples=capture_rows))
    return reference_path, capture_path


class FixedCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="case_", dir=os.environ.get("S2B_TEST_TMPDIR"))
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.reference, self.capture = write_fixture(self.directory, ("single",))
        self.output = self.directory / "result.json"

    def load(self, path: Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))

    def change_capture(self, change) -> None:
        value = self.load(self.capture)
        change(value)
        write_json(self.capture, value)

    def check(self) -> dict[str, object]:
        return checker.check_capture(self.reference, self.capture)

    def cli(self) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = checker.main(["--reference", str(self.reference), "--capture", str(self.capture), "--report", str(self.output)])
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_rejected(self) -> None:
        code, stdout, stderr = self.cli()
        self.assertEqual(code, 2, (stdout, stderr))
        self.assertIn("ERROR_OFFLINE_CAPTURE_CHECK", stderr)
        self.assertFalse(self.output.exists())

    def update_source_hash(self) -> None:
        value = self.load(self.reference)
        source = Path(value["golden_source"]["path"])
        value["golden_source"]["sha256"] = checker.sha256_bytes(source.read_bytes())
        write_json(self.reference, value)

    def test_independent_manual_fixture_and_arbitrary_uint32_frame_id(self) -> None:
        report = self.check()
        self.assertEqual(report["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        frame = report["frames"][0]
        self.assertEqual(frame["capture_identity"]["frame_id"], 0xFFFFFFFF)
        self.assertLessEqual(frame["detections"]["max_coordinate_absolute_error"], 1e-15)
        self.assertEqual(frame["head_tensors"]["head13"]["checked_bytes"], 5070)

    def test_empty_multiclass_second_head_and_explicit_multi_frames(self) -> None:
        self.reference.unlink()
        self.capture.unlink()
        directory = self.directory / "multi"
        directory.mkdir()
        self.reference, self.capture = write_fixture(directory)
        report = self.check()
        self.assertEqual(report["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        self.assertEqual(report["reference_frame_count"], 4)
        self.assertEqual([row["nms_output_box_count"] for row in self.load(self.capture)["samples"]], [1, 0, 2, 1])

    def test_exact_absolute_tolerance_and_zero_relative_tolerance(self) -> None:
        # 这些值的浮点差恰为 1e-6；只测试比较公式，不把人工数值当作整网预测。
        golden = [_manual_detection(0, 0, [0.0, 0.0, 0.5, 0.5])]
        capture = copy.deepcopy(golden)
        capture[0]["xyxy"][0] = 1e-6
        result = checker.compare_detections(golden, capture)
        self.assertTrue(result["match"])
        self.assertEqual(result["max_coordinate_absolute_error"], 1e-6)
        self.change_capture(lambda value: value["samples"][0]["detections"][0].update(score=0.250001))
        report = self.check()
        self.assertEqual(report["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        self.assertEqual(report["relative_tolerance"], 0.0)

    def test_score_and_each_coordinate_over_tolerance(self) -> None:
        original = self.load(self.capture)
        for field in ("score", "x1", "y1", "x2", "y2"):
            value = copy.deepcopy(original)
            detection = value["samples"][0]["detections"][0]
            if field == "score":
                detection["score"] += 1.00001e-6
            else:
                detection["xyxy"][("x1", "y1", "x2", "y2").index(field)] += 1.00001e-6
            write_json(self.capture, value)
            with self.subTest(field=field):
                self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_relative_tolerance_does_not_relax_large_score(self) -> None:
        golden = [_manual_detection(0, 0, [0.0, 0.0, 0.5, 0.5])]
        golden[0]["score"] = 0.99999
        actual = copy.deepcopy(golden)
        actual[0]["score"] += 1.1e-6
        self.assertFalse(checker.compare_detections(golden, actual)["match"])

    def test_discrete_class_source_order_and_box_count(self) -> None:
        original = self.load(self.capture)
        for case in ("class", "source_order", "count"):
            value = copy.deepcopy(original)
            sample = value["samples"][0]
            if case == "class":
                sample["detections"][0].update(class_id=1, class_name="palm", source_order=1261)
            elif case == "source_order":
                sample["detections"][0]["source_order"] += 5
            else:
                sample["detections"] = []
                sample["nms_output_box_count"] = 0
            write_json(self.capture, value)
            with self.subTest(case=case):
                self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_output_order_and_frame_order_are_exact(self) -> None:
        directory = self.directory / "multi"
        directory.mkdir()
        self.reference, self.capture = write_fixture(directory, ("multiclass", "head26"))
        original = self.load(self.capture)
        value = copy.deepcopy(original)
        value["samples"][0]["detections"].reverse()
        write_json(self.capture, value)
        self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")
        original["samples"].reverse()
        write_json(self.capture, original)
        self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_missing_or_extra_explicit_frame_is_failure(self) -> None:
        directory = self.directory / "multi"
        directory.mkdir()
        self.reference, self.capture = write_fixture(directory, ("single", "empty"))
        value = self.load(self.capture)
        value["samples"].pop()
        write_json(self.capture, value)
        self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")
        reference = self.load(self.reference)
        reference["samples"].pop()
        write_json(self.reference, reference)
        directory2 = self.directory / "extra"
        directory2.mkdir()
        _, capture2 = write_fixture(directory2, ("single", "empty"))
        self.capture = capture2
        self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_frame_sample_input_hash_and_geometry_identity(self) -> None:
        original = self.load(self.capture)
        for case in ("frame_id", "sample_id", "input_hash", "geometry"):
            value = copy.deepcopy(original)
            row = value["samples"][0]
            if case == "frame_id":
                row["frame_id"] -= 1
            elif case == "sample_id":
                row["sample_id"] += "_changed"
            elif case == "input_hash":
                row["input"]["pl_input_sha256"] = "0" * 64
            else:
                row["input"]["geometry_wh"] = [417, 416]
            write_json(self.capture, value)
            with self.subTest(case=case):
                self.assertEqual(self.check()["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_byte_mismatch_at_each_head_tail_and_first_byte(self) -> None:
        original = self.load(self.capture)
        for name in checker.HEAD_LENGTHS:
            path = Path(original["samples"][0]["head_tensors"][name]["path"])
            payload = path.read_bytes()
            for offset in (0, len(payload) - 1):
                changed = bytearray(payload)
                changed[offset] = 130
                path.write_bytes(changed)
                value = copy.deepcopy(original)
                value["samples"][0]["head_tensors"][name]["tensor_sha256"] = checker.sha256_bytes(changed)
                write_json(self.capture, value)
                with self.subTest(head=name, offset=offset):
                    report = self.check()
                    self.assertEqual(report["status"], "FAIL_OFFLINE_CAPTURE_CHECK")
                    detail = report["frames"][0]["head_tensors"][name]
                    self.assertEqual(detail["mismatch_byte_count"], 1)
                    self.assertEqual(detail["first_mismatch_offset"], offset)
                    self.assertEqual(report["frames"][0]["detections"]["status"], "NOT_RUN_HEAD_MISMATCH")
                path.write_bytes(payload)
        write_json(self.capture, original)

    def test_truncated_extra_bytes_and_head13_word_padding_rejected(self) -> None:
        original = self.load(self.capture)
        for name in checker.HEAD_LENGTHS:
            path = Path(original["samples"][0]["head_tensors"][name]["path"])
            payload = path.read_bytes()
            for changed in (payload[:-1], payload + b"\0", payload + b"\0\0"):
                path.write_bytes(changed)
                value = copy.deepcopy(original)
                value["samples"][0]["head_tensors"][name]["tensor_sha256"] = checker.sha256_bytes(changed)
                write_json(self.capture, value)
                with self.subTest(head=name, length=len(changed)):
                    self.assert_rejected()
            path.write_bytes(payload)
        write_json(self.capture, original)

    def test_missing_json_head_or_golden_file(self) -> None:
        original = self.load(self.capture)
        for path in (self.capture, Path(original["samples"][0]["head_tensors"]["head13"]["path"]), Path(self.load(self.reference)["golden_source"]["path"])):
            payload = path.read_bytes()
            path.unlink()
            with self.subTest(path=path.name):
                self.assert_rejected()
            path.write_bytes(payload)

    def test_path_with_spaces_unicode_and_exact_name(self) -> None:
        value = self.load(self.capture)
        old_path = Path(value["samples"][0]["head_tensors"]["head13"]["path"])
        path = self.directory / "检测头 _13-测试.bin"
        path.write_bytes(old_path.read_bytes())
        value["samples"][0]["head_tensors"]["head13"]["path"] = str(path)
        write_json(self.capture, value)
        self.assertEqual(self.check()["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        value["samples"][0]["head_tensors"]["head13"]["path"] = str(self.directory / "检测头-13_测试.bin")
        write_json(self.capture, value)
        self.assert_rejected()

    def test_wrong_hash_model_or_golden_origin_cannot_pass(self) -> None:
        original = self.load(self.capture)
        for case in ("model", "head"):
            value = copy.deepcopy(original)
            if case == "model":
                value["model_manifest_sha256"] = "0" * 64
            else:
                value["samples"][0]["head_tensors"]["head26"]["tensor_sha256"] = "0" * 64
            write_json(self.capture, value)
            with self.subTest(case=case):
                self.assert_rejected()
        write_json(self.capture, original)
        reference = self.load(self.reference)
        reference["golden_source"]["sha256"] = "0" * 64
        write_json(self.reference, reference)
        self.assert_rejected()

    def test_reference_head_must_match_independent_source_record(self) -> None:
        reference = self.load(self.reference)
        reference["samples"][0]["head_tensors"]["head13"]["tensor_sha256"] = "0" * 64
        write_json(self.reference, reference)
        self.assert_rejected()

    def test_golden_raw_consistency_is_not_inferred_from_capture(self) -> None:
        reference = self.load(self.reference)
        source = Path(reference["golden_source"]["path"])
        record = self.load(source)
        record["samples"][0]["detections"][0]["score"] = 0.26
        reference["samples"][0]["detections"][0]["score"] = 0.26
        write_json(source, record)
        reference["golden_source"]["sha256"] = checker.sha256_bytes(source.read_bytes())
        write_json(self.reference, reference)
        self.change_capture(lambda value: value["samples"][0]["detections"][0].update(score=0.26))
        self.assert_rejected()

    def test_capture_and_golden_same_file_or_hard_link_rejected(self) -> None:
        reference = self.load(self.reference)
        original = self.load(self.capture)
        value = copy.deepcopy(original)
        golden = Path(reference["samples"][0]["head_tensors"]["head13"]["path"])
        for path in (golden, self.directory / "head13_alias.bin"):
            if path != golden:
                os.link(golden, path)
            value["samples"][0]["head_tensors"]["head13"]["path"] = str(path)
            write_json(self.capture, value)
            with self.subTest(path=path.name):
                self.assert_rejected()

    def test_reference_capture_same_json_rejected_before_schema(self) -> None:
        self.capture = self.reference
        self.assert_rejected()

    def test_fake_cpu_record_cannot_claim_frozen_origin(self) -> None:
        reference = self.load(self.reference)
        reference["golden_source"]["kind"] = "frozen_cpu_d9"
        write_json(self.reference, reference)
        self.assert_rejected()

    def test_genuine_frozen_cpu_record_and_crlf_lf_binding(self) -> None:
        files = []
        path = checker.REPO_ROOT / checker.CPU_D9_RECORD_PATH
        descriptor = {"kind": "frozen_cpu_d9", "path": str(path), "sha256": checker.sha256_bytes(path.read_bytes())}
        _, rows, metadata = checker._golden_source(descriptor, checker.REPO_ROOT, files)
        self.assertEqual(len(rows), 109)
        self.assertEqual(metadata["source_commit"], checker.CPU_D9_RECORD_COMMIT)
        self.assertEqual(metadata["git_lf_sha256"], checker.CPU_D9_RECORD_LF_SHA256)

    def test_malformed_json_duplicate_keys_invalid_utf8_and_nonfinite(self) -> None:
        original = self.capture.read_bytes()
        for payload in (b"{", b"[]", b"{\"schema_version\":1,\"schema_version\":1}", b"{\"nested\":{\"a\":1,\"a\":2}}", b"\xff", original.replace(b"0.25", b"NaN", 1), original.replace(b"0.25", b"Infinity", 1), original.replace(b"0.25", b"1e999", 1), original + b"null"):
            self.capture.write_bytes(payload)
            with self.subTest(payload=payload[:45]):
                self.assert_rejected()
        self.capture.write_bytes(original)

    def test_schema_missing_extra_wrong_kind_and_bad_type(self) -> None:
        original = self.load(self.capture)
        mutations = [lambda value: value.update(schema_version=True), lambda value: value.update(kind="other"), lambda value: value.update(unrecognized=1), lambda value: value["samples"][0].pop("detections"), lambda value: value.update(samples=[]), lambda value: value["samples"][0]["head_tensors"].update(head52={})]
        for index, change in enumerate(mutations):
            value = copy.deepcopy(original)
            change(value)
            write_json(self.capture, value)
            with self.subTest(index=index):
                self.assert_rejected()

    def test_bool_and_out_of_range_integers_are_rejected(self) -> None:
        original = self.load(self.capture)
        mutations = [lambda row: row.update(frame_id=True), lambda row: row.update(frame_id=-1), lambda row: row.update(frame_id=2**32), lambda row: row.update(nms_output_box_count=True), lambda row: row.update(nms_output_box_count=16), lambda row: row["input"].update(geometry_wh=[True, 416]), lambda row: row["input"].update(geometry_wh=[0, 416]), lambda row: row["detections"][0].update(class_id=True), lambda row: row["detections"][0].update(class_id=5), lambda row: row["detections"][0].update(source_order=True), lambda row: row["detections"][0].update(source_order=12675)]
        for index, change in enumerate(mutations):
            value = copy.deepcopy(original)
            change(value["samples"][0])
            write_json(self.capture, value)
            with self.subTest(index=index):
                self.assert_rejected()

    def test_bad_score_coordinate_and_zero_area_are_rejected(self) -> None:
        original = self.load(self.capture)
        for field, value in (("score", True), ("score", 0.24), ("score", 1.01), ("xyxy", [0, 0, 0, 1]), ("xyxy", [-1, 0, 1, 1]), ("xyxy", [0, 0, 1, True]), ("xyxy", [0, 1, 1]), ("xyxy", [0, 0, 1, 2])):
            capture = copy.deepcopy(original)
            capture["samples"][0]["detections"][0][field] = value
            write_json(self.capture, capture)
            with self.subTest(field=field, value=value):
                self.assert_rejected()

    def test_duplicate_frame_sample_and_detection_source_order(self) -> None:
        value = self.load(self.capture)
        value["samples"].append(copy.deepcopy(value["samples"][0]))
        write_json(self.capture, value)
        self.assert_rejected()
        value["samples"].pop()
        row = value["samples"][0]
        row["detections"].append(copy.deepcopy(row["detections"][0]))
        row["nms_output_box_count"] = 2
        write_json(self.capture, value)
        self.assert_rejected()

    def test_minus128_is_rejected(self) -> None:
        value = self.load(self.capture)
        binding = value["samples"][0]["head_tensors"]["head13"]
        path = Path(binding["path"])
        payload = bytearray(path.read_bytes())
        payload[-1] = 128
        path.write_bytes(payload)
        binding["tensor_sha256"] = checker.sha256_bytes(payload)
        write_json(self.capture, value)
        self.assert_rejected()

    def test_cli_success_fail_and_new_report_only(self) -> None:
        code, stdout, stderr = self.cli()
        self.assertEqual(code, 0, stderr)
        self.assertIn("PASS_OFFLINE_CAPTURE_CHECK", stdout)
        old_bytes = self.output.read_bytes()
        self.change_capture(lambda value: value["samples"][0]["detections"][0].update(score=0.3))
        code, stdout, stderr = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("旧文件不是本次结果", stderr)
        self.assertNotIn("PASS_OFFLINE_CAPTURE_CHECK", stdout)
        self.assertEqual(self.output.read_bytes(), old_bytes)
        self.output = self.directory / "fail.json"
        code, stdout, stderr = self.cli()
        self.assertEqual(code, 1, stderr)
        self.assertIn("FAIL_OFFLINE_CAPTURE_CHECK", stdout)
        self.assertEqual(self.load(self.output)["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_output_cannot_cover_input_or_missing_parent(self) -> None:
        for path in (self.reference, self.capture, Path(self.load(self.capture)["samples"][0]["head_tensors"]["head13"]["path"])):
            payload = path.read_bytes()
            self.output = path
            code, _, _ = self.cli()
            self.assertEqual(code, 2)
            self.assertEqual(path.read_bytes(), payload)
        self.output = self.directory / "missing" / "result.json"
        self.assert_rejected()

    def test_exclusive_output_creation_race_and_write_failure(self) -> None:
        self.output.write_text("old result", encoding="utf-8")
        with self.assertRaises(checker.CaptureCheckError):
            checker._write_report(self.output, {"status": "PASS_OFFLINE_CAPTURE_CHECK"})
        self.assertEqual(self.output.read_text(encoding="utf-8"), "old result")
        self.output = self.directory / "write_failure.json"
        with mock.patch.object(checker.os, "fsync", side_effect=OSError("模拟本次磁盘同步失败")):
            with self.assertRaises(checker.CaptureCheckError):
                checker._write_report(self.output, {"status": "PASS_OFFLINE_CAPTURE_CHECK"})
        self.assertFalse(self.output.exists())

    def test_same_bytes_concurrent_file_replacement_is_rejected(self) -> None:
        capture_head = Path(self.load(self.capture)["samples"][0]["head_tensors"]["head13"]["path"])
        original_compare = checker.compare_detections

        def replacing_compare(expected, actual, tolerance=checker.ABS_TOLERANCE):
            result = original_compare(expected, actual, tolerance)
            if tolerance == checker.ABS_TOLERANCE:
                replacement = self.directory / "replacement.bin"
                replacement.write_bytes(capture_head.read_bytes())
                os.replace(replacement, capture_head)
            return result

        with mock.patch.object(checker, "compare_detections", side_effect=replacing_compare):
            self.assert_rejected()

    def test_random_full_byte_checks_and_empty_heads(self) -> None:
        # 种子、样本数和检查口径为常量，证据运行会将它们写入统计结果。
        rng = random.Random(RANDOM_SEED)
        reference = self.load(self.reference)
        original = self.load(self.capture)
        for index in range(RANDOM_BYTE_CASES):
            name = rng.choice(tuple(checker.HEAD_LENGTHS))
            binding = original["samples"][0]["head_tensors"][name]
            path = Path(binding["path"])
            payload = path.read_bytes()
            changed = bytearray(payload)
            offset = rng.randrange(len(changed))
            changed[offset] = 130 if changed[offset] != 130 else 131
            path.write_bytes(changed)
            value = copy.deepcopy(original)
            value["samples"][0]["head_tensors"][name]["tensor_sha256"] = checker.sha256_bytes(changed)
            write_json(self.capture, value)
            with self.subTest(index=index, name=name, offset=offset):
                detail = self.check()["frames"][0]["head_tensors"][name]
                self.assertFalse(detail["match"])
                self.assertEqual(detail["first_mismatch_offset"], offset)
                self.assertEqual(detail["mismatch_byte_count"], 1)
            path.write_bytes(payload)
        # 每个随机 raw 值均在 [-127,-64]，因此所有 obj/class 的乘积严格低于阈值。
        directory = self.directory / "random_empty"
        directory.mkdir()
        self.reference, self.capture = write_fixture(directory, ("empty",) * RANDOM_EMPTY_FRAMES)
        reference = self.load(self.reference)
        capture = self.load(self.capture)
        source_path = Path(reference["golden_source"]["path"])
        source = self.load(source_path)
        for index, (golden, captured, source_row) in enumerate(zip(reference["samples"], capture["samples"], source["samples"])):
            golden["frame_id"] = captured["frame_id"] = source_row["frame_id"] = rng.randrange(2**32)
            for name, length in checker.HEAD_LENGTHS.items():
                payload = bytes((rng.randint(-127, -64) & 255) for _ in range(length))
                for row in (golden, captured):
                    Path(row["head_tensors"][name]["path"]).write_bytes(payload)
                    row["head_tensors"][name]["tensor_sha256"] = checker.sha256_bytes(payload)
                source_row["head_tensors"][name]["tensor_sha256"] = checker.sha256_bytes(payload)
        write_json(source_path, source)
        write_json(self.reference, reference)
        self.update_source_hash()
        write_json(self.capture, capture)
        self.assertEqual(self.check()["status"], "PASS_OFFLINE_CAPTURE_CHECK")

    def test_real_subprocess_cli_does_not_require_board_or_numpy(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(checker.REPO_ROOT / "verification/s2b_fixed_capture_check.py"), "--reference", str(self.reference), "--capture", str(self.capture), "--report", str(self.output)], capture_output=True, text=True, encoding="utf-8", timeout=15, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_OFFLINE_CAPTURE_CHECK", result.stdout)


if __name__ == "__main__":
    unittest.main()
