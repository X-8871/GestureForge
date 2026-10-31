"""C3 单调计数器/GT 快照采集核心的离线测试。"""

from __future__ import annotations

import json
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from collector import (
    CollectorConfig,
    SnapshotCollector,
    _synthetic_demo,
    write_csv,
)


C3_DIR = Path(__file__).resolve().parents[1] / "c3"


def config(**overrides: object) -> CollectorConfig:
    values: dict[str, object] = {
        "event_kind": "camera_sof",
        "counter_modulus": 2**32,
        "clock_id": "test_gt",
        "min_duration_ticks": 10,
        "min_event_count": 2,
        "max_polls": 20,
        "max_samples": 20,
        "max_gt_stall_polls": 3,
        "gt_hz": 1_000_000,
        "gt_frequency_source": "test-only",
    }
    values.update(overrides)
    return CollectorConfig(**values)  # type: ignore[arg-type]


def advancing_gt(step: int = 1):
    state = {"value": 0}

    def read_gt() -> int:
        value = state["value"]
        state["value"] += step
        return value

    return read_gt


class SnapshotCollectorTests(unittest.TestCase):
    def test_constant_period_csv_is_readable_by_existing_analyzer(self) -> None:
        state = {"polls": 0}

        def read_counter() -> int:
            state["polls"] += 1
            return state["polls"]

        result = SnapshotCollector(
            config(
                min_duration_ticks=39,
                min_event_count=20,
                max_polls=30,
                max_samples=30,
            ),
            read_counter,
            advancing_gt(),
            "synthetic-test:period-8gt",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "TARGET_REACHED")
        self.assertEqual(result.cumulative_event_count, 20)
        self.assertEqual(result.elapsed_gt_ticks, 40)
        self.assertEqual(result.elapsed_gt_bounds["lower"], 39)
        self.assertEqual(result.max_poll_gap_upper_ticks, 3)
        self.assertEqual(result.samples[0].sample_index, 0)
        self.assertEqual(result.samples[-1].counter_value, 21)

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "samples.csv"
            write_csv(result, csv_path)
            analyzer = C3_DIR / "analyze_frame_period.py"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(analyzer),
                    str(csv_path),
                    "--gt-hz",
                    "1000000",
                    "--origin",
                    "synthetic",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["sample_kind"], "counter_snapshot")
        self.assertEqual(report["counter_type"], "monotonic")
        self.assertEqual(report["claim_status"], "SYNTHETIC_ONLY_NOT_MEASURED")
        self.assertAlmostEqual(report["observed_period_us"], 2.0)
        self.assertIsNone(report["measured_value_us"])

    def test_duration_and_count_both_gate_completion(self) -> None:
        for minimum_duration, minimum_count, expected_polls in (
            (4, 10, 11),
            (20, 2, 12),
        ):
            with self.subTest(minimum_duration=minimum_duration, minimum_count=minimum_count):
                state = {"polls": 0}

                def read_counter() -> int:
                    state["polls"] += 1
                    return state["polls"]

                result = SnapshotCollector(
                    config(
                        min_duration_ticks=minimum_duration,
                        min_event_count=minimum_count,
                    ),
                    read_counter,
                    advancing_gt(),
                    "synthetic-test:later-target",
                    origin="synthetic",
                ).collect()
                self.assertEqual(result.status, "TARGET_REACHED")
                self.assertEqual(result.poll_count, expected_polls)
                self.assertTrue(result.to_dict()["duration_target_reached"])
                self.assertTrue(result.to_dict()["count_target_reached"])

    def test_counter_backtrack_or_wrap_fails_and_keeps_valid_samples(self) -> None:
        values = iter((10, 11, 2))
        result = SnapshotCollector(
            config(min_duration_ticks=100, min_event_count=50),
            lambda: next(values),
            advancing_gt(),
            "host-test:unverified-counter",
            origin="host_callback_unverified",
        ).collect()
        self.assertEqual(result.status, "COUNTER_REGRESSION_OR_WRAP")
        self.assertEqual(result.sample_count, 2)
        self.assertEqual(result.cumulative_event_count, 1)
        self.assertEqual(result.origin, "host_callback_unverified")

    def test_invalid_gt_bracket_is_rejected_before_adding_sample(self) -> None:
        values = iter((10, 9))
        result = SnapshotCollector(
            config(),
            lambda: 0,
            lambda: next(values),
            "synthetic-test:invalid-bracket",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "INVALID_GT_BRACKET")
        self.assertEqual(result.sample_count, 0)

    def test_gt_value_must_fit_unsigned_64_bit_range(self) -> None:
        values = iter((0, 2**64))
        result = SnapshotCollector(
            config(),
            lambda: 0,
            lambda: next(values),
            "synthetic-test:gt-width",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "INVALID_GT_BRACKET")
        self.assertEqual(result.sample_count, 0)

    def test_counter_value_must_fit_declared_modulus_range(self) -> None:
        result = SnapshotCollector(
            config(counter_modulus=16),
            lambda: 16,
            advancing_gt(),
            "synthetic-test:counter-range",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "INVALID_COUNTER_VALUE")
        self.assertEqual(result.sample_count, 0)

    def test_configuration_limits_reject_bool_float_and_nan(self) -> None:
        for field, value in (
            ("max_polls", True),
            ("max_samples", 1.5),
            ("counter_modulus", False),
            ("min_duration_ticks", float("nan")),
            ("min_event_count", 1.0),
            ("max_gt_stall_polls", True),
            ("gt_hz", float("nan")),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    config(**{field: value})

    def test_read_callbacks_reject_bool_float_and_nan(self) -> None:
        invalid_values = (True, 1.0, float("nan"))
        for field in ("counter", "gt"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    gt_state = {"value": 0}

                    def read_gt() -> int:
                        gt_state["value"] += 1
                        if field == "gt":
                            return value  # type: ignore[return-value]
                        return gt_state["value"]

                    def read_counter() -> int:
                        return value if field == "counter" else 0  # type: ignore[return-value]

                    result = SnapshotCollector(
                        config(),
                        read_counter,
                        read_gt,
                        "synthetic-test:strict-read-types",
                        origin="synthetic",
                    ).collect()
                    self.assertEqual(result.status, "INVALID_READ")
                    self.assertEqual(result.sample_count, 0)

    def test_origin_defaults_to_synthetic(self) -> None:
        result = SnapshotCollector(
            config(min_duration_ticks=1, min_event_count=1),
            lambda: 1,
            advancing_gt(),
            "synthetic-test:default-origin",
        ).collect()
        self.assertEqual(result.origin, "synthetic")

    def test_gt_regression_is_rejected_and_keeps_prior_sample(self) -> None:
        values = iter((5, 6, 4, 7))
        result = SnapshotCollector(
            config(),
            lambda: 0,
            lambda: next(values),
            "synthetic-test:gt-regression",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "GT_ROLLBACK")
        self.assertEqual(result.sample_count, 1)

    def test_cross_bracket_gt_rollback_is_rejected_and_preserves_sample(self) -> None:
        gt_values = iter((100, 200, 150, 250))
        counter_values = iter((0, 1))
        result = SnapshotCollector(
            config(min_duration_ticks=1, min_event_count=1, max_polls=2),
            lambda: next(counter_values),
            lambda: next(gt_values),
            "synthetic-test:cross-bracket-rollback",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "GT_ROLLBACK")
        self.assertEqual(result.sample_count, 1)
        self.assertEqual(result.samples[0].counter_value, 0)

    def test_equal_previous_gt_after_is_valid(self) -> None:
        gt_values = iter((100, 200, 200, 300))
        counter_values = iter((0, 1))
        result = SnapshotCollector(
            config(min_duration_ticks=1000, min_event_count=1, max_polls=2),
            lambda: next(counter_values),
            lambda: next(gt_values),
            "synthetic-test:touching-gt-brackets",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "MAX_POLLS_REACHED")
        self.assertEqual(result.sample_count, 2)
        self.assertEqual(result.samples[1].gt_before, result.samples[0].gt_after)

    def test_duration_uses_bracket_lower_bound_not_start_to_start_span(self) -> None:
        gt_values = iter((0, 100, 110, 120, 130, 140))
        counter_values = iter((0, 1, 2))
        result = SnapshotCollector(
            config(
                min_duration_ticks=50,
                min_event_count=1,
                max_polls=3,
                max_samples=3,
            ),
            lambda: next(counter_values),
            lambda: next(gt_values),
            "synthetic-test:wide-first-bracket",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "MAX_POLLS_REACHED")
        self.assertEqual(result.elapsed_gt_ticks, 130)
        self.assertEqual(result.elapsed_gt_bounds["lower"], 30)
        self.assertFalse(result.to_dict()["duration_target_reached"])

    def test_failed_result_can_export_raw_partial_samples(self) -> None:
        state = {"polls": 0}

        def read_counter() -> int:
            state["polls"] += 1
            if state["polls"] == 3:
                raise OSError("synthetic callback fault")
            return state["polls"]

        result = SnapshotCollector(
            config(min_duration_ticks=1000, min_event_count=100),
            read_counter,
            advancing_gt(),
            "synthetic-test:failed-csv-export",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "CALLBACK_ERROR")
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "partial.csv"
            write_csv(result, csv_path)
            with csv_path.open("r", encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["sample_index"] for row in rows], ["0", "1"])

    def test_capacity_failure_keeps_all_retained_samples(self) -> None:
        result = SnapshotCollector(
            config(min_duration_ticks=1000, min_event_count=100, max_samples=2),
            lambda: 0,
            advancing_gt(),
            "synthetic-test:capacity",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "SAMPLE_CAPACITY_REACHED")
        self.assertEqual(result.sample_count, 2)
        self.assertEqual(result.poll_count, 2)

    def test_static_counter_exits_at_poll_limit_when_clock_advances(self) -> None:
        result = SnapshotCollector(
            config(min_duration_ticks=2, min_event_count=1, max_polls=4),
            lambda: 0,
            advancing_gt(),
            "synthetic-test:static-counter",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "MAX_POLLS_REACHED")
        self.assertEqual(result.sample_count, 4)
        self.assertEqual(result.cumulative_event_count, 0)

    def test_gt_stall_exits_with_preserved_samples(self) -> None:
        result = SnapshotCollector(
            config(min_duration_ticks=1, min_event_count=1, max_gt_stall_polls=2),
            lambda: 0,
            lambda: 0,
            "synthetic-test:static-clock",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "GT_NO_PROGRESS")
        self.assertEqual(result.sample_count, 3)
        self.assertEqual(result.elapsed_gt_ticks, 0)

    def test_callback_failure_is_bounded_and_preserves_prior_samples(self) -> None:
        state = {"polls": 0}

        def read_counter() -> int:
            state["polls"] += 1
            if state["polls"] == 3:
                raise OSError("synthetic callback fault")
            return state["polls"]

        result = SnapshotCollector(
            config(min_duration_ticks=1000, min_event_count=100),
            read_counter,
            advancing_gt(),
            "synthetic-test:callback-failure",
            origin="synthetic",
        ).collect()
        self.assertEqual(result.status, "CALLBACK_ERROR")
        self.assertEqual(result.failure_phase, "counter")
        self.assertEqual(result.error_type, "OSError")
        self.assertEqual(result.sample_count, 2)

    def test_existing_csv_is_never_overwritten(self) -> None:
        result = _synthetic_demo()
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "samples.csv"
            write_csv(result, csv_path)
            original = csv_path.read_bytes()
            with self.assertRaises(FileExistsError):
                write_csv(result, csv_path)
            self.assertEqual(csv_path.read_bytes(), original)

    def test_captured_origin_cannot_be_self_asserted(self) -> None:
        with self.assertRaisesRegex(ValueError, "不接受 captured"):
            SnapshotCollector(
                config(),
                lambda: 0,
                lambda: 0,
                "synthetic-test:origin-guard",
                origin="captured",  # type: ignore[arg-type]
            )

    def test_cli_only_runs_synthetic_demo_and_returns_samples(self) -> None:
        collector = Path(__file__).with_name("collector.py")
        completed = subprocess.run(
            [sys.executable, "-B", str(collector), "--demo"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["origin"], "synthetic")
        self.assertEqual(report["status"], "TARGET_REACHED")
        self.assertEqual(report["measurement_claim"], "COLLECTOR_OUTPUT_IS_NOT_T6_A03_ACCEPTANCE")
        self.assertGreater(report["sample_count"], 2)
        self.assertEqual(report["sample_count"], len(report["samples"]))


if __name__ == "__main__":
    unittest.main()
