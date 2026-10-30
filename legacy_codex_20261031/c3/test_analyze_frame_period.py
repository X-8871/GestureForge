"""帧周期离线分析器的定向单元测试。"""

import json
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from analyze_frame_period import Sample, analyze_samples


class AnalyzeFramePeriodTests(unittest.TestCase):
    def test_event_bracket_interval_preserves_timestamp_uncertainty(self) -> None:
        samples = [
            Sample(0, "camera_sof", "event_bracket", "monotonic", 2**32, 10, "gt", 100, 102),
            Sample(1, "camera_sof", "event_bracket", "monotonic", 2**32, 11, "gt", 10_100, 10_102),
            Sample(2, "camera_sof", "event_bracket", "monotonic", 2**32, 12, "gt", 20_100, 20_102),
        ]
        result = analyze_samples(samples, 1_000_000, "captured")
        self.assertEqual(result["claim_status"], "CAPTURED_ESTIMATE_REQUIRES_SOURCE_REVIEW")
        self.assertAlmostEqual(result["measured_value_us"], 10_000.0, places=6)
        self.assertEqual(result["measured_interval_us"], {"lower": 9999.0, "upper": 10001.0})
        self.assertEqual(
            result["intervals"][0]["mean_period_interval_us"],
            {"lower": 9998.0, "upper": 10002.0},
        )

    def test_event_bracket_rejects_skipped_event_counter(self) -> None:
        samples = [
            Sample(0, "camera_sof", "event_bracket", "monotonic", 16, 10, "gt", 100, 102),
            Sample(1, "camera_sof", "event_bracket", "monotonic", 16, 12, "gt", 40_100, 40_102),
        ]
        with self.assertRaisesRegex(ValueError, "event_bracket.*增量为 2"):
            analyze_samples(samples, 1_000_000, "captured")

    def test_monotonic_counter_wrap_is_rejected_instead_of_modulo_inferred(self) -> None:
        samples = [
            Sample(0, "camera_sof", "counter_snapshot", "monotonic", 16, 14, "gt", 0, 2),
            Sample(1, "camera_sof", "counter_snapshot", "monotonic", 16, 2, "gt", 40_000, 40_002),
        ]
        with self.assertRaisesRegex(ValueError, "单调计数器回退或回绕"):
            analyze_samples(samples, 1_000_000, "captured")

    def test_cyclic_pointer_delta_conflicting_with_unique_edge_bound_is_rejected(self) -> None:
        samples = [
            Sample(0, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 16, 14, "gt", 0, 2),
            Sample(1, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 16, 2, "gt", 39_998, 40_002),
        ]
        with self.assertRaisesRegex(ValueError, "最多允许一个事件"):
            analyze_samples(samples, 1_000_000, "captured", Decimal("50000"))

    def test_cli_rejects_nonfinite_period_as_structured_nonmeasurement(self) -> None:
        analyzer = Path(__file__).with_name("analyze_frame_period.py")
        for value in ("NaN", "Infinity"):
            with self.subTest(value=value):
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(analyzer),
                        "--demo",
                        "--gt-hz",
                        "1000000",
                        "--min-event-period-us",
                        value,
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertNotIn("Traceback", completed.stderr)
                report = json.loads(completed.stderr)
                self.assertEqual(report["claim_status"], "INVALID_INPUT_NOT_MEASURED")
                self.assertIsNone(report["measured_value_us"])

    def test_monotonic_snapshot_uses_full_count_span_and_phase_bound(self) -> None:
        samples = [
            Sample(0, "camera_sof", "counter_snapshot", "monotonic", 2**32, 0, "gt", 100, 102),
            Sample(1, "camera_sof", "counter_snapshot", "monotonic", 2**32, 500, "gt", 500_100, 500_102),
            Sample(2, "camera_sof", "counter_snapshot", "monotonic", 2**32, 1000, "gt", 1_000_100, 1_000_102),
        ]
        result = analyze_samples(samples, 1_000_000, "captured")
        self.assertEqual(result["observed_counter_delta"], 1000)
        self.assertAlmostEqual(result["measured_value_us"], 1000.0, places=6)
        bounds = result["measured_interval_us"]
        self.assertLess(bounds["lower"], 1000.0)
        self.assertGreater(bounds["upper"], 1000.0)

    def test_cyclic_pointer_requires_an_alias_bound(self) -> None:
        samples = [
            Sample(0, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 0, "gt", 0, 2),
            Sample(1, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 0, "gt", 5_000, 5_002),
            Sample(2, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 1, "gt", 10_000, 10_002),
            Sample(3, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 1, "gt", 15_000, 15_002),
            Sample(4, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 0, "gt", 20_000, 20_002),
        ]
        unresolved = analyze_samples(samples, 1_000_000, "captured")
        self.assertEqual(unresolved["alias_status"], "UNRESOLVED_CYCLIC_ALIAS")
        self.assertIsNone(unresolved["measured_value_us"])
        bounded = analyze_samples(samples, 1_000_000, "captured", Decimal("8000"))
        self.assertEqual(bounded["alias_status"], "CONDITIONAL_NO_ALIAS_BOUND")
        self.assertAlmostEqual(bounded["measured_value_us"], 10_000.0, places=6)

    def test_same_cyclic_value_cannot_distinguish_no_edge_from_two_missed_edges(self) -> None:
        samples = [
            Sample(0, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 0, "gt", 0, 2),
            Sample(1, "vdma_mm2s_readstore", "counter_snapshot", "cyclic_pointer", 2, 0, "gt", 20_000, 20_002),
        ]
        result = analyze_samples(samples, 1_000_000, "captured")
        self.assertEqual(result["observed_counter_delta"], 0)
        self.assertIsNone(result["measured_value_us"])
        self.assertEqual(result["claim_status"], "CAPTURED_BUT_PERIOD_NOT_ESTABLISHED")

    def test_cyclic_alias_bound_must_not_conflict_with_observed_period(self) -> None:
        samples = [
            Sample(
                index,
                "vdma_mm2s_readstore",
                "counter_snapshot",
                "cyclic_pointer",
                2,
                index % 2,
                "gt",
                index * 1000,
                index * 1000 + 2,
            )
            for index in range(101)
        ]
        result = analyze_samples(samples, 1_000_000, "captured", Decimal("2000"))
        self.assertEqual(result["alias_status"], "CONFLICTING_MIN_EVENT_PERIOD")
        self.assertIsNone(result["measured_value_us"])

    def test_synthetic_origin_never_populates_measured_value(self) -> None:
        samples = [
            Sample(0, "camera_sof", "event_bracket", "monotonic", 2**32, 0, "gt-demo", 100, 102),
            Sample(1, "camera_sof", "event_bracket", "monotonic", 2**32, 1, "gt-demo", 16_767, 16_769),
        ]
        result = analyze_samples(samples, 1_000_000, "synthetic")
        self.assertEqual(result["claim_status"], "SYNTHETIC_ONLY_NOT_MEASURED")
        self.assertIsNone(result["measured_value_us"])
        self.assertAlmostEqual(result["observed_period_us"], 16_667.0, places=6)

    def test_invalid_gt_bracket_is_rejected(self) -> None:
        samples = [
            Sample(0, "camera_sof", "event_bracket", "monotonic", 2**32, 0, "gt", 102, 100),
            Sample(1, "camera_sof", "event_bracket", "monotonic", 2**32, 1, "gt", 16_767, 16_769),
        ]
        with self.assertRaisesRegex(ValueError, "GT 区间无效"):
            analyze_samples(samples, 1_000_000, "captured")


if __name__ == "__main__":
    unittest.main()
