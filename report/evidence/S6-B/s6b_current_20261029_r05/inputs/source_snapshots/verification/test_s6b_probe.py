"""S6-B 判别力探针的隔离回归测试。"""

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import s6b_probe
from s6b_probe import validate_baseline


def make_baseline(count: int = 26) -> tuple[dict, dict]:
    """构造临时基线矩阵及与之对应的通过报告。"""
    cases = [{"case_id": f"C{index:02d}"} for index in range(count)]
    report_cases = [{"case_id": case["case_id"], "status": "PASS"} for case in cases]
    return (
        {"cases": cases},
        {"status": "PASS", "case_count": count, "cases": report_cases},
    )


class ValidateBaselineTests(unittest.TestCase):
    """验证基线数量与所有用例结果均受实际报告约束。"""

    def test_26_case_baseline_is_reported_from_matrix_and_run(self) -> None:
        matrix, report = make_baseline(26)

        result = validate_baseline(matrix, report, 0)

        self.assertTrue(result["passed"], result["reason"])
        self.assertEqual(result["expected_case_count"], 26)
        self.assertEqual(result["actual_case_count"], 26)
        self.assertEqual(result["reported_case_count"], 26)

    def test_different_actual_count_cannot_pass(self) -> None:
        matrix, report = make_baseline(26)
        report["cases"].pop()
        report["case_count"] = 25

        result = validate_baseline(matrix, report, 0)

        self.assertFalse(result["passed"])
        self.assertEqual(result["expected_case_count"], 26)
        self.assertEqual(result["actual_case_count"], 25)

    def test_failed_case_cannot_pass_with_zero_driver_exit(self) -> None:
        matrix, report = make_baseline(26)
        report["cases"][7]["status"] = "FAIL"

        result = validate_baseline(matrix, report, 0)

        self.assertFalse(result["passed"])
        self.assertEqual(result["failed_case_ids"], ["C07"])


class MainFlowTests(unittest.TestCase):
    """验证 main 实际写入的摘要使用本次基线报告计数。"""

    def test_main_summary_persists_actual_26_case_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "evidence" / "isolated_probe_run"
            cases_path = run_dir / "cases" / "case_matrix.json"
            cases_path.parent.mkdir(parents=True)
            cases = [{
                "case_id": f"C{index:02d}",
                "expected": {"final_state": "COOLDOWN"},
            } for index in range(26)]
            cases_path.write_text(json.dumps({"cases": cases}), encoding="utf-8")
            (run_dir / "expected_freeze.json").write_text("{}\n", encoding="utf-8")
            driver = root / "verification" / "s6b_run_cases.py"
            driver.parent.mkdir(parents=True)
            driver.write_text("# 临时占位驱动\n", encoding="utf-8")
            behavior = root / "docs" / "stage6" / "s6a_stage6_g0_behavior_v1.json"
            behavior.parent.mkdir(parents=True)
            behavior.write_text(json.dumps({"parameters": [{"id": "T6-S01"}]}), encoding="utf-8")

            calls = 0

            def fake_driver(_driver, _root, child_run_dir, child_cases, extra=None):
                nonlocal calls
                call_index = calls
                calls += 1
                if call_index == 0:
                    matrix = json.loads(Path(child_cases).read_text(encoding="utf-8"))
                    report_cases = [
                        {"case_id": case["case_id"], "status": "PASS"}
                        for case in matrix["cases"]
                    ]
                    report = {
                        "status": "PASS",
                        "case_count": len(report_cases),
                        "cases": report_cases,
                    }
                    (Path(child_run_dir) / "run_report.json").write_text(
                        json.dumps(report), encoding="utf-8"
                    )
                    return subprocess.CompletedProcess([], 0, stdout="baseline complete\n", stderr="")
                expected_exits = [2, 0, 1, 0, 1]
                return subprocess.CompletedProcess(
                    [], expected_exits[call_index - 1], stdout=f"fake probe {call_index}\n", stderr=""
                )

            output = io.StringIO()
            with patch.object(s6b_probe, "run_driver", side_effect=fake_driver):
                with contextlib.redirect_stdout(output):
                    exit_code = s6b_probe.main([
                        "--run-dir", str(Path("evidence") / run_dir.name),
                        "--project-root", str(root),
                    ])

            summary = json.loads((run_dir / "probe_summary.json").read_text(encoding="utf-8"))
            baseline = summary["results"][0]
            self.assertEqual(exit_code, 0)
            self.assertEqual(calls, 6)
            self.assertIn("矩阵 26 例，报告 26 例", baseline["note"])
            self.assertNotIn("23", baseline["note"])
            self.assertEqual(baseline["validation"]["expected_case_count"], 26)
            self.assertEqual(baseline["validation"]["actual_case_count"], 26)
            self.assertEqual(baseline["verdict"], "AS_EXPECTED")


if __name__ == "__main__":
    unittest.main()
