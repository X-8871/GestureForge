#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T27 回放/彩色输入路径与离线动态回归的用例（每项都有**能失败**的负例）。

覆盖：
1. 输入路径实现：源身份、逐帧 `frame_integrity`、`replay_source_*` 传递、非零 `capture_time_ns`、
   `replay_not_live` 标记、5 类拒收负例（含**篡改源字节**、`capture_time_ns=0`、`source_kind=synthetic`）。
2. 离线动态回归：坐标/帧关联/过期边界/顺序规则/异常/长跑断言全部通过，且失败时会真的非零。
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
for _candidate in (str(REPO_ROOT), str(HERE)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import scripts.stage5_t03.s5t03_replay_colour_input as RI  # noqa: E402

BINDING = pathlib.Path("D:/codex-worktrees/dbdf/report/evidence/S3-T05/"
                       "t05_replay_binding_20261025_r01/replay_input_binding.json")
PACKAGE = pathlib.Path("D:/codex-worktrees/w4/report/evidence/S4-CTRL/"
                       "s4t27_replay_positive_20261027_r01/task27_replay_result_package_positive.json")
FREEZE_INDEX = pathlib.Path("D:/codex-worktrees/w4/report/evidence/S4-CTRL/"
                            "s4t27_replay_positive_20261027_r01/freeze_index.json")
REGRESSION = HERE / "s5t03_replay_colour_regression.py"
HOST_INPUTS_PRESENT = all(path.is_file() for path in (BINDING, PACKAGE, FREEZE_INDEX))

DETECTION = {"class_id": 0, "class_name": "fist", "score": 0.77,
             "xyxy": [0.25, 0.37, 0.35, 0.44], "source_order": 1}


@unittest.skipUnless(HOST_INPUTS_PRESENT, "宿主侧回放输入/冻结包缺失（跨树只读引用不可用）")
class T01_ReplayInputPath(unittest.TestCase):
    """实现层：逐帧完整性、replay_source_*、非零 capture_time、replay_not_live、拒收负例。"""

    @classmethod
    def setUpClass(cls):
        cls.source = RI.load_replay_source(BINDING)

    def test_source_identity_matches_declared(self):
        self.assertEqual(self.source.source_frame_sha256,
                         "939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0")
        self.assertEqual(self.source.source_frame_size_bytes, 2_764_800)
        self.assertEqual((self.source.width, self.source.height), (1280, 720))
        self.assertEqual(self.source.stride_bytes, 3840)
        self.assertEqual(self.source.pixel_format, "BGR888")
        self.assertEqual(self.source.byte_order, "BGR")
        self.assertGreater(self.source.capture_time_ns, 0, "回放源 capture_time_ns 必须非零")
        self.assertEqual(self.source.timing_claim_scope, "replay_only")
        self.assertTrue(self.source.replay_not_live)

    def test_record_carries_replay_binding_and_nonzero_capture(self):
        record = RI.build_replay_record(self.source, session_id=1396854863, frame_id=1,
                                        result_seq=1, detections=[DETECTION])
        RI.assert_replay_record(record)
        for field in RI.REPLAY_SOURCE_FIELDS:
            self.assertIn(field, record, f"结果记录缺少 {field}")
        self.assertEqual(record["input_scope_label"], RI.INPUT_SCOPE_LABEL)
        self.assertIs(record["replay_not_live"], True)
        self.assertGreater(record["capture_time_ns"], 0)
        self.assertEqual(record["source_capture_time_ns"], self.source.capture_time_ns)
        self.assertEqual(record["frame_integrity"]["value"], self.source.source_frame_sha256)
        self.assertIsNone(record["result_time_ns"], "证据模式不得伪造发布时间")
        self.assertEqual(record["replay_source_stride_bytes"], 3840)

    def test_frame_integrity_is_recomputed_not_trusted(self):
        computed = RI.frame_integrity_of(self.source)
        self.assertEqual(computed["value"], self.source.source_frame_sha256)
        self.assertEqual(computed["length_bytes"], self.source.source_frame_size_bytes)
        with self.assertRaises(RI.ReplayInputError):
            RI.validate_frame_integrity({"algorithm": "sha256", "value": "0" * 64,
                                         "length_bytes": computed["length_bytes"]}, computed)
        with self.assertRaises(RI.ReplayInputError):
            RI.validate_frame_integrity({"algorithm": "sha256", "value": computed["value"],
                                         "length_bytes": computed["length_bytes"] + 1}, computed)

    def _mutated_binding(self, **overrides) -> pathlib.Path:
        binding = json.loads(BINDING.read_text(encoding="utf-8"))
        binding.update(overrides)
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(binding, handle, ensure_ascii=False)
        handle.close()
        path = pathlib.Path(handle.name)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def test_zero_capture_time_rejected(self):
        path = self._mutated_binding(capture_time_ns=0)
        with self.assertRaises(RI.ReplayInputError):
            RI.load_replay_source(path)

    def test_synthetic_kind_rejected(self):
        path = self._mutated_binding(source_kind="synthetic")
        with self.assertRaises(RI.ReplayInputError):
            RI.load_replay_source(path)

    def test_unavailable_capture_rejected(self):
        path = self._mutated_binding(capture_time_available=False)
        with self.assertRaises(RI.ReplayInputError):
            RI.load_replay_source(path)

    def test_label_guard_rejects_replay_not_live_false(self):
        record = RI.build_replay_record(self.source, session_id=7, frame_id=1, result_seq=1,
                                        detections=[DETECTION])
        record["replay_not_live"] = False
        with self.assertRaises(RI.ReplayInputError):
            RI.assert_replay_record(record)

    def test_missing_replay_source_field_rejected(self):
        record = RI.build_replay_record(self.source, session_id=7, frame_id=1, result_seq=1,
                                        detections=[DETECTION])
        record.pop("replay_source_file_sha256")
        with self.assertRaises(RI.ReplayInputError):
            RI.assert_replay_record(record)

    def test_tampered_source_bytes_rejected(self):
        """篡改源帧字节（换工作树指向临时副本）⇒ 装载即拒收（逐帧完整性不是声明值）。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = pathlib.Path(tmp)
            frame = tmp_dir / "frame_full.bin"
            shutil.copyfile(self.source.source_frame_path, frame)
            with open(frame, "r+b") as handle:                 # 翻转 1 字节
                handle.seek(0)
                first = handle.read(1)
                handle.seek(0)
                handle.write(bytes([first[0] ^ 0xFF]))
            binding = json.loads(BINDING.read_text(encoding="utf-8"))
            binding["source_worktree"] = str(tmp_dir)
            path = tmp_dir / "binding.json"
            path.write_text(json.dumps(binding, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(RI.ReplayInputError):
                RI.load_replay_source(path)


@unittest.skipUnless(HOST_INPUTS_PRESENT, "宿主侧回放输入/冻结包缺失（跨树只读引用不可用）")
class T02_ReplayOfflineRegression(unittest.TestCase):
    """离线动态显示回归：判定 PASS、断言齐全、失败可被检出（判别力）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="s5t27_regression_")
        cls.out = pathlib.Path(cls.tmp) / "run"
        cls.result = subprocess.run([sys.executable, "-B", str(REGRESSION),
                                     "--out", str(cls.out), "--binding", str(BINDING),
                                     "--package", str(PACKAGE), "--freeze-record", str(FREEZE_INDEX)],
                                    capture_output=True, text=True, encoding="utf-8", errors="replace")
        cls.results = (json.loads((cls.out / "results.json").read_text(encoding="utf-8"))
                       if (cls.out / "results.json").is_file() else {})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_regression_exit_zero_and_verdict_pass(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr[-800:])
        self.assertEqual(self.results.get("verdict"), "REPLAY_OFFLINE_REGRESSION_PASS")

    def test_conclusion_labelled_replay_offline(self):
        self.assertIn("回放/离线", self.results.get("conclusion_scope", ""))
        self.assertEqual(self.results.get("input_scope_label"), RI.INPUT_SCOPE_LABEL)

    def test_core_coverage_assertions_present_and_passing(self):
        names = {item["name"] for item in self.results["assertions"] if item["pass"]}
        for required in ("px_positive_area[0]", "association_pairs_equal",
                         "one_commit_event_per_displayed_frame",
                         "stale_boundary::age_equals_limit_not_stale",
                         "stale_boundary::age_limit_plus_1ns_stale",
                         "duplicate_result_key_rejected", "regressed_frame_id_rejected",
                         "equivalent_frame_id_undeclared_rejected",
                         "equivalent_frame_id_declared_accepted",
                         "zero_area_after_clip_dropped_not_drawn",
                         "long_run_timestamps_monotonic", "long_run_counters_recomputable"):
            self.assertIn(required, names, f"缺少断言：{required}")

    def test_long_run_matches_frozen_arithmetic(self):
        long_run = self.results["long_run"]
        self.assertEqual(long_run["frames"], 106_573)
        self.assertEqual(long_run["interval_count"], 106_572)
        self.assertEqual(long_run["elapsed_ns"], 1_800_001_080_000)

    def test_regression_detects_injected_failure(self):
        """判别力：篡改冻结包字节 ⇒ 驱动必须拒收（exit 2），证明回归不是恒真。"""
        with tempfile.TemporaryDirectory() as tmp:
            bad_package = pathlib.Path(tmp) / PACKAGE.name
            payload = json.loads(PACKAGE.read_text(encoding="utf-8"))
            payload["detections"]["boxes"][0]["score"] = 0.123456
            bad_package.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run([sys.executable, "-B", str(REGRESSION),
                                        "--out", str(pathlib.Path(tmp) / "bad"), "--binding", str(BINDING),
                                        "--package", str(bad_package), "--freeze-record", str(FREEZE_INDEX)],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(completed.returncode, 2,
                             f"篡改冻结包应被拒收（exit 2），实际 {completed.returncode}")


if __name__ == "__main__":
    unittest.main(verbosity=2)