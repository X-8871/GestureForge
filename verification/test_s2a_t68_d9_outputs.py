"""T68 D9 输出绑定函数的离线单元回归。"""

from __future__ import annotations

import copy
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

    def test_project_rules_sha_drift_is_normalized_and_reported(self) -> None:
        frozen_sha256 = "0b0925c21c7f7cbb664c971649ba1051d1873736855bb4e417303cd4cc1c3945"
        current_sha256 = "848a8af0f68de6440a9538c321937d43c52ab7026b42b420de27fc0815c10ac3"
        frozen = {
            "source_bindings": [
                {"path": "AGENTS.md", "role": "project_rules", "sha256": frozen_sha256},
                {"path": "verification/s2a_decode_nms_reference.py", "role": "t29_generator", "sha256": "a" * 64},
            ]
        }
        regenerated = {
            "source_bindings": [
                {"path": "AGENTS.md", "role": "project_rules", "sha256": current_sha256},
                {"path": "verification/s2a_decode_nms_reference.py", "role": "t29_generator", "sha256": "a" * 64},
            ]
        }

        frozen_normalized, regenerated_normalized, report = d9_verifier.normalize_t29_project_rules_binding(
            frozen, regenerated
        )

        self.assertEqual(frozen_normalized["source_bindings"], regenerated_normalized["source_bindings"])
        self.assertEqual(regenerated["source_bindings"][0]["sha256"], current_sha256)
        self.assertEqual(report["field"], "source_bindings[role=project_rules].sha256")
        self.assertEqual(report["path"], "AGENTS.md")
        self.assertEqual(report["frozen_sha256"], frozen_sha256)
        self.assertEqual(report["current_sha256"], current_sha256)
        self.assertFalse(report["same"])
        self.assertTrue(report["normalization_applied"])

        reconstruction_metadata = d9_verifier.t29_reconstruction_metadata(report)
        self.assertEqual(
            reconstruction_metadata["status"],
            "PASS_T29_REGENERATION_EXCEPT_RUNTIME_VERSION_FIELDS_AND_PROJECT_RULES_SHA_METADATA",
        )
        self.assertEqual(
            reconstruction_metadata["ignored_fields"],
            [
                "runtime.python",
                "runtime.zlib_compile",
                "runtime.zlib_runtime",
                "source_bindings[role=project_rules].sha256",
            ],
        )
        self.assertEqual(reconstruction_metadata["project_rules_source_binding"], report)

    def test_non_project_source_binding_drift_is_rejected(self) -> None:
        frozen = {
            "source_bindings": [
                {"path": "AGENTS.md", "role": "project_rules", "sha256": "b" * 64},
                {"path": "verification/t29.py", "role": "t29_generator", "sha256": "a" * 64},
            ]
        }
        regenerated = {
            "source_bindings": [
                {"path": "AGENTS.md", "role": "project_rules", "sha256": "c" * 64},
                {"path": "verification/t29.py", "role": "t29_generator", "sha256": "d" * 64},
            ]
        }

        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.normalize_t29_project_rules_binding(frozen, regenerated)

    def test_final_normalized_canonical_hashes_are_reported_and_must_match(self) -> None:
        frozen_normalized = {
            "runtime": {"python": None, "zlib_compile": None, "zlib_runtime": None},
            "source_bindings": [
                {"path": "AGENTS.md", "role": "project_rules", "sha256": "a" * 64}
            ],
            "samples": [{"sample_id": "unit", "output": []}],
        }
        regenerated_normalized = copy.deepcopy(frozen_normalized)

        report = d9_verifier.compare_t29_normalized_canonical(
            frozen_normalized, regenerated_normalized
        )
        expected_sha256 = d9_verifier.sha256_bytes(
            d9_verifier.t29._canonical_evidence_bytes(frozen_normalized)
        )
        self.assertEqual(report["frozen_normalized_canonical_sha256"], expected_sha256)
        self.assertEqual(report["regenerated_normalized_canonical_sha256"], expected_sha256)
        self.assertTrue(report["normalized_canonical_match"])

        regenerated_normalized["samples"][0]["output"].append("unexpected")
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.compare_t29_normalized_canonical(frozen_normalized, regenerated_normalized)

    def test_project_rules_binding_requires_one_valid_agents_hash(self) -> None:
        valid_binding = {"path": "AGENTS.md", "role": "project_rules", "sha256": "a" * 64}
        duplicate = {
            "source_bindings": [valid_binding, dict(valid_binding)]
        }
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.normalize_t29_project_rules_binding(duplicate, duplicate)

        wrong_path = {"source_bindings": [{**valid_binding, "path": "OTHER.md"}]}
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.normalize_t29_project_rules_binding(wrong_path, wrong_path)

        wrong_hash = {"source_bindings": [{**valid_binding, "sha256": "not-a-sha256"}]}
        with self.assertRaises(d9_verifier.D9VerificationError):
            d9_verifier.normalize_t29_project_rules_binding(wrong_hash, wrong_hash)

    def test_progress_markers_recover_from_sha_bound_console_preserving_crlf(self) -> None:
        marker_bytes = (
            b"S2A_PROGRESS sample=7 phase=init cycle=10\r\n"
            b"S2A_PROGRESS sample=7 phase=running cycle=20\r\n"
            b"S2A_PROGRESS sample=7 phase=complete cycle=30\r\n"
        )
        console_bytes = b"Verilator output\r\n" + marker_bytes + b"simulation complete\r\n"
        observed_marker_bytes = b"S2A_PROGRESS sample=7 phase=running cycle=20\r\n"
        expected_marker_sha256 = d9_verifier.sha256_bytes(marker_bytes)
        console_sha256 = d9_verifier.sha256_bytes(console_bytes)

        recovered, report = d9_verifier.bind_progress_marker_bytes(
            observed_marker_bytes,
            expected_marker_sha256,
            3,
            7,
            console_bytes,
            console_sha256,
        )

        self.assertEqual(recovered, marker_bytes)
        self.assertTrue(report["recovered_from_sha_bound_console"])
        self.assertEqual(report["observed_marker_sha256"], d9_verifier.sha256_bytes(observed_marker_bytes))
        self.assertEqual(report["expected_marker_sha256"], expected_marker_sha256)
        self.assertEqual(report["recovered_marker_sha256"], expected_marker_sha256)
        self.assertEqual(report["console_sha256"], console_sha256)
        self.assertEqual(report["count"], 3)

    def test_direct_progress_marker_binding_keeps_original_bytes(self) -> None:
        marker_bytes = (
            b"S2A_PROGRESS sample=2 phase=running cycle=20\n"
            b"S2A_PROGRESS sample=2 phase=complete cycle=30\r\n"
        )
        console_bytes = b"simulation console\n"
        expected_marker_sha256 = d9_verifier.sha256_bytes(marker_bytes)
        console_sha256 = d9_verifier.sha256_bytes(console_bytes)

        validated, report = d9_verifier.bind_progress_marker_bytes(
            marker_bytes,
            expected_marker_sha256,
            2,
            2,
            console_bytes,
            console_sha256,
        )

        self.assertEqual(validated, marker_bytes)
        self.assertFalse(report["recovered_from_sha_bound_console"])
        self.assertEqual(report["observed_marker_sha256"], expected_marker_sha256)
        self.assertEqual(report["expected_marker_sha256"], expected_marker_sha256)
        self.assertIsNone(report["recovered_marker_sha256"])
        self.assertEqual(report["console_sha256"], console_sha256)
        self.assertEqual(report["count"], 2)

    def test_progress_marker_recovery_rejects_cross_sample_count_hash_and_console_drift(self) -> None:
        marker_rows = (
            b"S2A_PROGRESS sample=7 phase=running cycle=20\r\n"
            b"S2A_PROGRESS sample=7 phase=complete cycle=30\r\n"
        )
        wrong_sample_rows = (
            b"S2A_PROGRESS sample=8 phase=running cycle=20\r\n"
            b"S2A_PROGRESS sample=8 phase=complete cycle=30\r\n"
        )
        observed_marker_bytes = b"stale marker bytes\r\n"
        console_bytes = b"prefix\r\n" + marker_rows
        console_sha256 = d9_verifier.sha256_bytes(console_bytes)

        with self.subTest("wrong sample index"):
            wrong_sample_console = b"prefix\r\n" + wrong_sample_rows
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.bind_progress_marker_bytes(
                    observed_marker_bytes,
                    d9_verifier.sha256_bytes(wrong_sample_rows),
                    2,
                    7,
                    wrong_sample_console,
                    d9_verifier.sha256_bytes(wrong_sample_console),
                )

        with self.subTest("wrong marker count"):
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.bind_progress_marker_bytes(
                    observed_marker_bytes,
                    d9_verifier.sha256_bytes(marker_rows),
                    3,
                    7,
                    console_bytes,
                    console_sha256,
                )

        with self.subTest("wrong expected marker sha"):
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.bind_progress_marker_bytes(
                    observed_marker_bytes,
                    "f" * 64,
                    2,
                    7,
                    console_bytes,
                    console_sha256,
                )

        with self.subTest("console sha mismatch"):
            with self.assertRaises(d9_verifier.D9VerificationError):
                d9_verifier.bind_progress_marker_bytes(
                    observed_marker_bytes,
                    d9_verifier.sha256_bytes(marker_rows),
                    2,
                    7,
                    console_bytes,
                    "0" * 64,
                )

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
