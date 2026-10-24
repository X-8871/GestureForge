"""S6-B builder 摘要与清单 evidence 结果的一致性回归。"""

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import s6b_build_evidence as builder
from s6b_build_evidence import (
    evidence_check_manifest_entry,
    format_inputs_summary_row,
    format_evidence_summary_rows,
    inputs_check_manifest_entry,
    update_inputs_summary_row,
    update_evidence_summary_rows,
    write_check_output,
)


class S6BEvidenceSummaryRegression(unittest.TestCase):
    """摘要明确区分首次预检与最终收敛检查。"""

    def test_iteration_zero_failure_and_final_pass_are_reported_separately(self):
        first_precheck = {
            "command_text": "python check_stage_delivery.py --mode evidence --iteration 0",
            "exit_code": 2,
        }
        final_run = {
            "command_text": "python check_stage_delivery.py --mode evidence",
            "exit_code": 0,
        }
        final_check = evidence_check_manifest_entry(final_run)
        initial_rows = format_evidence_summary_rows(None, None)
        summary = "\n".join(("| 步骤 | 命令 | 实测退出码 |", "|---|---|---|", *initial_rows, ""))

        updated = update_evidence_summary_rows(summary, first_precheck, final_check)
        rows = [line for line in updated.splitlines() if line.startswith("| 交付检查 evidence ")]

        self.assertEqual(len(rows), 2)
        self.assertIn("首次预检（fixpoint iteration 0）", rows[0])
        self.assertIn("--iteration 0", rows[0])
        self.assertIn("实测 2", rows[0])
        self.assertIn("最终收敛检查", rows[1])
        self.assertIn(final_check["command"], rows[1])
        self.assertIn(f"实测 {final_check['exit_code']}", rows[1])
        self.assertEqual(final_check["status"], "PASS")
        self.assertEqual(final_check["exit_code"], 0)

    def test_inputs_placeholder_is_filled_before_check_artifacts_are_bound(self):
        inputs_run = {
            "command_text": "python check_stage_delivery.py --mode inputs --manifest inputs.json",
            "exit_code": 0,
            "stdout": '{"status":"CHECKS_OK","mode":"inputs"}\n',
        }
        inputs_check = inputs_check_manifest_entry(inputs_run)
        initial_summary = "\n".join((
            "| 步骤 | 命令 | 实测退出码 |",
            "|---|---|---|",
            format_inputs_summary_row(None),
            *format_evidence_summary_rows(None, None),
            "",
        ))
        self.assertIn("__S6B_INPUTS_COMMAND_PENDING__", initial_summary)
        self.assertIn("__S6B_INPUTS_EXIT_PENDING__", initial_summary)

        summary = update_inputs_summary_row(initial_summary, inputs_check)
        self.assertNotIn("__S6B_INPUTS_COMMAND_PENDING__", summary)
        self.assertNotIn("__S6B_INPUTS_EXIT_PENDING__", summary)

        first_precheck = {
            "command_text": "python check_stage_delivery.py --mode evidence --iteration 0",
            "exit_code": 2,
        }
        final_run = {
            "command_text": "python check_stage_delivery.py --mode evidence",
            "exit_code": 0,
            "stdout": '{"status":"CHECKS_OK","mode":"evidence"}\n',
        }
        final_check = evidence_check_manifest_entry(final_run)
        summary = update_evidence_summary_rows(summary, first_precheck, final_check)
        input_row = next(line for line in summary.splitlines()
                         if line.startswith("| 交付检查 inputs |"))
        evidence_rows = [line for line in summary.splitlines()
                         if line.startswith("| 交付检查 evidence ")]

        self.assertIn(inputs_check["command"], input_row)
        self.assertIn(f"实测 {inputs_check['exit_code']}", input_row)
        self.assertEqual(inputs_check["status"], "PASS")
        self.assertIn("CHECKS_OK", inputs_run["stdout"])
        self.assertIn("首次预检（fixpoint iteration 0）", evidence_rows[0])
        self.assertIn("实测 2", evidence_rows[0])
        self.assertIn(final_check["command"], evidence_rows[1])
        self.assertIn(f"实测 {final_check['exit_code']}", evidence_rows[1])
        self.assertEqual(final_check["status"], "PASS")

        with tempfile.TemporaryDirectory() as tmp:
            inputs_out = Path(tmp) / "check_inputs_mode_output.txt"
            evidence_out = Path(tmp) / "check_evidence_mode_output.txt"
            write_check_output(inputs_out, inputs_run)
            write_check_output(evidence_out, final_run)
            self.assertEqual(inputs_out.read_text(encoding="utf-8"), inputs_run["stdout"])
            self.assertEqual(evidence_out.read_text(encoding="utf-8"), final_run["stdout"])
            self.assertIn("CHECKS_OK", evidence_out.read_text(encoding="utf-8"))


def run_main_fixture(inputs_exit=0, final_evidence_exit=0, closing_evidence_exit=0):
    """在一次性临时项目中驱动 main，并返回落盘产物快照。"""
    with tempfile.TemporaryDirectory(prefix="s6b-main-flow-") as temporary:
        root = Path(temporary).resolve()
        run_rel = Path("report/evidence/S6-B/fixture_r01")
        run_dir = root / run_rel
        cases = run_dir / "cases/case_matrix.json"
        cases.parent.mkdir(parents=True)
        cases.write_text("{}\n", encoding="utf-8")

        for relative in builder.SOURCES:
            source = root / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            if relative == "src/stage6/s6_params.py":
                source.write_text(
                    "class ParamPack:\n"
                    "    def __init__(self, behavior, project_root=None):\n"
                    "        self.data = {'artifact_version': 'S6A-G0-v1.8'}\n"
                    "        self.behavior_sha256 = 'a' * 64\n"
                    "    def snapshot(self):\n"
                    "        return {'fixture': True}\n"
                    "    def threshold_bundle(self):\n"
                    "        return {'a02_ns': 1, 'k01_ns': 2}\n",
                    encoding="utf-8",
                )
            elif source.suffix == ".json":
                source.write_text("{}\n", encoding="utf-8")
            else:
                source.write_text("fixture source\n", encoding="utf-8")

        labels = []
        evidence_calls = []
        inputs_stdout = ('{"status":"CHECKS_OK","mode":"inputs"}\n' if inputs_exit == 0
                         else '{"status":"CHECKS_FAILED","mode":"inputs"}\n')
        stale_stdout = '{"status":"STALE_PRECHECK","mode":"evidence"}\n'
        final_stdout = ('{"status":"CHECKS_OK","mode":"evidence"}\n'
                        if final_evidence_exit == 0
                        else '{"status":"CHECKS_FAILED","mode":"evidence"}\n')
        closing_failure_stdout = (
            '{"status":"CHECKS_FAILED","mode":"evidence","phase":"closing"}\n'
        )

        def result(command, exit_code, stdout=""):
            return {
                "command_text": subprocess.list2cmdline(command),
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": "",
            }

        def fake_run_command(command, project_root):
            command = list(command)
            command_name = Path(command[2]).name
            if command_name == "s6b_run_cases.py" and "--freeze-only" in command:
                labels.append("freeze")
                (run_dir / "expected_freeze.json").write_text(
                    '{"fixture":"frozen"}\n', encoding="utf-8")
                return result(command, 0, "freeze ok\n")
            if command_name == "s6b_run_cases.py":
                labels.append("cases")
                (run_dir / "run_report.json").write_text(json.dumps({
                    "case_count": 1,
                    "cases": [{"case_id": "fixture-case", "matrix_class": "A",
                               "status": "PASS"}],
                    "status": "PASS",
                }), encoding="utf-8")
                return result(command, 0, "cases ok\n")
            if command_name == "s6b_probe.py":
                labels.append("probe")
                return result(command, 0, "probe ok\n")
            if command_name == "check_stage_delivery.py":
                mode = command[command.index("--mode") + 1]
                labels.append(mode)
                if mode == "inputs":
                    return result(command, inputs_exit, inputs_stdout)
                if mode == "evidence":
                    evidence_calls.append(command)
                    if len(evidence_calls) == 1:
                        return result(command, 2, stale_stdout)
                    if len(evidence_calls) == 2 and final_evidence_exit != 0:
                        return result(command, final_evidence_exit, final_stdout)
                    if len(evidence_calls) == 5 and closing_evidence_exit != 0:
                        return result(command, closing_evidence_exit, closing_failure_stdout)
                    return result(command, 0, final_stdout)
            raise AssertionError(f"unexpected builder child command: {command}")

        def fake_git_run(command, **kwargs):
            if command[-2:] == ["rev-parse", "HEAD"]:
                output = "fixture-commit\n"
            elif command[-1:] == ["--version"]:
                output = "git version fixture\n"
            else:
                raise AssertionError(f"unexpected subprocess command: {command}")
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")

        previous_sys_path = list(sys.path)
        previous_src_modules = {
            name: module for name, module in sys.modules.items()
            if name == "src" or name.startswith("src.")
        }
        for name in previous_src_modules:
            sys.modules.pop(name, None)
        output = io.StringIO()
        try:
            with mock.patch.object(builder, "run_command", side_effect=fake_run_command), \
                    mock.patch.object(builder.subprocess, "run", side_effect=fake_git_run), \
                    contextlib.redirect_stdout(output):
                exit_code = builder.main([
                    "--run-dir", run_rel.as_posix(),
                    "--project-root", str(root),
                    "--cases", str(cases),
                ])
        finally:
            sys.path[:] = previous_sys_path
            for name in tuple(sys.modules):
                if name == "src" or name.startswith("src."):
                    sys.modules.pop(name, None)
            sys.modules.update(previous_src_modules)

        def read_text(name):
            path = run_dir / name
            return path.read_text(encoding="utf-8") if path.is_file() else None

        def read_bytes(name):
            path = run_dir / name
            return path.read_bytes() if path.is_file() else None

        manifest_text = read_text("delivery_manifest.json")
        return {
            "exit_code": exit_code,
            "stdout": output.getvalue(),
            "labels": labels,
            "evidence_calls": evidence_calls,
            "manifest": json.loads(manifest_text) if manifest_text else None,
            "summary": read_text("s6b_run_summary.md"),
            "inputs_output": read_text("check_inputs_mode_output.txt"),
            "evidence_output": read_text("check_evidence_mode_output.txt"),
            "inputs_output_bytes": read_bytes("check_inputs_mode_output.txt"),
            "evidence_output_bytes": read_bytes("check_evidence_mode_output.txt"),
            "hashes": read_text("hashes_sha256.txt"),
        }


class S6BBuilderFlowRegression(unittest.TestCase):
    """真实 main 编排把成功与失败检查绑定到临时证据包。"""

    def test_main_runs_inputs_before_fixpoint_and_binds_final_outputs(self):
        result = run_main_fixture()
        self.assertEqual(result["exit_code"], 0, result["stdout"])
        self.assertLess(result["labels"].index("inputs"), result["labels"].index("evidence"))
        self.assertGreaterEqual(len(result["evidence_calls"]), 4)
        self.assertIn("[CLOSING] run-dir 无未声明文件、清单一致", result["stdout"])

        checks = {row["name"]: row for row in result["manifest"]["checks"]}
        inputs_check = checks["check_stage_delivery.py --mode inputs"]
        evidence_check = checks["check_stage_delivery.py --mode evidence"]
        self.assertEqual((inputs_check["status"], inputs_check["exit_code"]), ("PASS", 0))
        self.assertEqual((evidence_check["status"], evidence_check["exit_code"]), ("PASS", 0))

        inputs_row = next(line for line in result["summary"].splitlines()
                          if line.startswith("| 交付检查 inputs |"))
        evidence_rows = [line for line in result["summary"].splitlines()
                         if line.startswith("| 交付检查 evidence ")]
        self.assertIn(inputs_check["command"], inputs_row)
        self.assertIn("实测 0 (PASS)", inputs_row)
        self.assertIn("首次预检（fixpoint iteration 0）", evidence_rows[0])
        self.assertIn("实测 2 (FAIL)", evidence_rows[0])
        self.assertIn("最终收敛检查", evidence_rows[1])
        self.assertIn(evidence_check["command"], evidence_rows[1])
        self.assertIn("实测 0 (PASS)", evidence_rows[1])
        self.assertIn('{"status":"CHECKS_OK","mode":"inputs"}', result["inputs_output"])
        self.assertIn('{"status":"CHECKS_OK","mode":"evidence"}', result["evidence_output"])

    def test_nonzero_inputs_check_is_persisted_and_stops_builder(self):
        result = run_main_fixture(inputs_exit=2)
        self.assertEqual(result["exit_code"], 1, result["stdout"])
        checks = {row["name"]: row for row in result["manifest"]["checks"]}
        inputs_check = checks["check_stage_delivery.py --mode inputs"]
        evidence_check = checks["check_stage_delivery.py --mode evidence"]
        self.assertEqual((inputs_check["status"], inputs_check["exit_code"]), ("FAIL", 2))
        self.assertIn("--mode inputs", inputs_check["command"])
        self.assertEqual(evidence_check["status"], "NOT_RUN")
        self.assertIn("NOT_RUN", result["evidence_output"])
        inputs_row = next(line for line in result["summary"].splitlines()
                          if line.startswith("| 交付检查 inputs |"))
        self.assertIn(inputs_check["command"], inputs_row)
        self.assertIn("实测 2 (FAIL)", inputs_row)
        self.assertIn("构建状态：FAIL", result["summary"])
        self.assertIn("CHECKS_FAILED", result["inputs_output"])
        entry = next(row for row in result["manifest"]["files"]
                     if row["path"].endswith("check_inputs_mode_output.txt"))
        raw = result["inputs_output_bytes"]
        normalized_digest = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        raw_digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(entry["sha256"], normalized_digest)
        self.assertIn(f"{raw_digest}  check_inputs_mode_output.txt", result["hashes"])
        self.assertEqual(len(result["evidence_calls"]), 0)

    def test_nonzero_final_evidence_check_is_persisted_and_stops_builder(self):
        result = run_main_fixture(final_evidence_exit=3)
        self.assertEqual(result["exit_code"], 1, result["stdout"])
        checks = {row["name"]: row for row in result["manifest"]["checks"]}
        evidence_check = checks["check_stage_delivery.py --mode evidence"]
        self.assertEqual((evidence_check["status"], evidence_check["exit_code"]), ("FAIL", 3))
        self.assertIn("--mode evidence", evidence_check["command"])
        evidence_rows = [line for line in result["summary"].splitlines()
                         if line.startswith("| 交付检查 evidence ")]
        self.assertIn(evidence_check["command"], evidence_rows[1])
        self.assertIn("实测 3 (FAIL)", evidence_rows[1])
        self.assertIn("构建状态：FAIL", result["summary"])
        self.assertIn("CHECKS_FAILED", result["evidence_output"])
        entry = next(row for row in result["manifest"]["files"]
                     if row["path"].endswith("check_evidence_mode_output.txt"))
        raw = result["evidence_output_bytes"]
        normalized_digest = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        raw_digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(entry["sha256"], normalized_digest)
        self.assertIn(f"{raw_digest}  check_evidence_mode_output.txt", result["hashes"])

    def test_nonzero_closing_check_replaces_previous_pass_and_is_persisted(self):
        result = run_main_fixture(closing_evidence_exit=4)
        self.assertEqual(result["exit_code"], 1, result["stdout"])
        self.assertEqual(len(result["evidence_calls"]), 5)

        checks = {row["name"]: row for row in result["manifest"]["checks"]}
        evidence_check = checks["check_stage_delivery.py --mode evidence"]
        self.assertEqual((evidence_check["status"], evidence_check["exit_code"]), ("FAIL", 4))
        self.assertIn("--mode evidence", evidence_check["command"])

        evidence_rows = [line for line in result["summary"].splitlines()
                         if line.startswith("| 交付检查 evidence ")]
        self.assertIn(evidence_check["command"], evidence_rows[1])
        self.assertIn("实测 4 (FAIL)", evidence_rows[1])
        self.assertNotIn("实测 0 (PASS)", evidence_rows[1])
        self.assertIn("构建状态：FAIL", result["summary"])
        self.assertIn('"phase":"closing"', result["evidence_output"])

        entry = next(row for row in result["manifest"]["files"]
                     if row["path"].endswith("check_evidence_mode_output.txt"))
        raw = result["evidence_output_bytes"]
        normalized_digest = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
        raw_digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(entry["sha256"], normalized_digest)
        self.assertIn(f"{raw_digest}  check_evidence_mode_output.txt", result["hashes"])


if __name__ == "__main__":
    unittest.main()
