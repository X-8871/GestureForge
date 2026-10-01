"""T68 D9 输出绑定函数的离线单元回归。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification import verify_s2a_network_backend_golden as fixture_verifier
from verification import verify_s2a_t68_d9_outputs as d9_verifier


class T68D9OutputTests(unittest.TestCase):
    """验证 head 字节解释、静态导出闭包和 D9 数值/离散比较门。"""

    def test_harness_exports_real_backend_head_bytes(self) -> None:
        result = fixture_verifier.verify_harness_bindings()
        self.assertEqual(result["source_count"], 11)
        self.assertTrue(result["verilator_native_capture_contract"])

    def test_native_capture_counts_retained_warning_and_rejects_error(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t68-native-capture-") as temporary:
            sample_dir = Path(temporary)
            stdout_path = sample_dir / "stdout.txt"
            stderr_path = sample_dir / "stderr.txt"
            console_path = sample_dir / "console.txt"
            stdout_raw = b"Verilator 5.x\n"
            stderr_raw = b"%Warning-WIDTH: retained warning\n"
            console_raw = stdout_raw + b"--- STDERR ---\n" + stderr_raw
            stdout_path.write_bytes(stdout_raw)
            stderr_path.write_bytes(stderr_raw)
            console_path.write_bytes(console_raw)
            record = {
                "warning_text_retained": True,
                "warning_count": 1,
                "error_count": 0,
                "stdout_path": str(stdout_path),
                "stdout_sha256": d9_verifier.sha256_file(stdout_path),
                "stderr_path": str(stderr_path),
                "stderr_sha256": d9_verifier.sha256_file(stderr_path),
                "console_path": str(console_path),
                "console_sha256": d9_verifier.sha256_file(console_path),
            }
            checked = d9_verifier.verify_captured_native_logs(sample_dir, record, "unit compile")
            self.assertEqual(checked, {"warning_count": 1, "error_count": 0})

            record["warning_count"] = 0
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.verify_captured_native_logs(sample_dir, record, "unit compile")

            record["warning_count"] = 1
            record["error_count"] = 1
            stderr_raw = b"%Warning-WIDTH: retained warning\n%Error: fatal diagnostics\n"
            console_raw = stdout_raw + b"--- STDERR ---\n" + stderr_raw
            stderr_path.write_bytes(stderr_raw)
            console_path.write_bytes(console_raw)
            record["stderr_sha256"] = d9_verifier.sha256_file(stderr_path)
            record["console_sha256"] = d9_verifier.sha256_file(console_path)
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.verify_captured_native_logs(sample_dir, record, "unit compile")

    def test_signed_int8_dequantization_uses_frozen_shape_and_scale(self) -> None:
        head13 = bytes([0xFF]) * d9_verifier.HEAD_SPECS["head13"]["bytes"]
        head26 = bytes([0x80]) * d9_verifier.HEAD_SPECS["head26"]["bytes"]
        decoded = d9_verifier.decode_heads(head13, head26, 0.5, 0.25)
        self.assertEqual(decoded["13x13"].shape, (3, 10, 13, 13))
        self.assertEqual(decoded["26x26"].shape, (3, 10, 26, 26))
        self.assertEqual(decoded["13x13"].dtype, np.float64)
        self.assertTrue(np.all(decoded["13x13"] == -0.5))
        self.assertTrue(np.all(decoded["26x26"] == -32.0))

    def test_d9_comparator_accepts_absolute_error_inside_tolerance(self) -> None:
        expected = [{"class_id": 2, "class_name": "one", "source_order": 15, "score": 0.75, "xyxy": [0.1, 0.2, 0.7, 0.8]}]
        observed = [SimpleNamespace(
            class_id=2,
            name="one",
            source_order=15,
            image_key="fixed_sample",
            confidence=0.7500005,
            box=(0.1000005, 0.2, 0.7, 0.8),
        )]
        compared = d9_verifier.compare_d9_rows(expected, observed, "fixed_sample", 1, 1)
        self.assertLessEqual(compared["max_score_abs_error"], 1e-6)
        self.assertLessEqual(compared["max_xyxy_abs_error"], 1e-6)
        self.assertEqual(compared["relative_tolerance"], 0.0)

    def test_d9_comparator_rejects_discrete_field_or_raw_count_mismatch(self) -> None:
        expected = [{"class_id": 2, "class_name": "one", "source_order": 15, "score": 0.75, "xyxy": [0.1, 0.2, 0.7, 0.8]}]
        observed = [SimpleNamespace(
            class_id=1,
            name="palm",
            source_order=15,
            image_key="fixed_sample",
            confidence=0.75,
            box=(0.1, 0.2, 0.7, 0.8),
        )]
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.compare_d9_rows(expected, observed, "fixed_sample", 1, 1)
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.compare_d9_rows(expected, observed, "fixed_sample", 2, 1)

    def test_d9_comparator_rejects_error_over_absolute_tolerance(self) -> None:
        expected = [{"class_id": 2, "class_name": "one", "source_order": 15, "score": 0.75, "xyxy": [0.1, 0.2, 0.7, 0.8]}]
        observed = [SimpleNamespace(
            class_id=2,
            name="one",
            source_order=15,
            image_key="fixed_sample",
            confidence=0.750002,
            box=(0.1, 0.2, 0.7, 0.8),
        )]
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.compare_d9_rows(expected, observed, "fixed_sample", 1, 1)


if __name__ == "__main__":
    unittest.main()
