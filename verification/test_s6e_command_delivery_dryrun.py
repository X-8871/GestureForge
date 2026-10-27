"""S6-E dry-run 计划的拒绝路径回归。"""

from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from s6e_command_delivery_dryrun import (
    _load_json_strict,
    _write_new_plan,
    build_dry_run_plan,
    main,
    validate_dry_run_plan,
)


ROOT = Path(__file__).resolve().parents[1]


class S6ECommandDeliveryDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = build_dry_run_plan(ROOT, "s6e_command_delivery_20261027_r01")

    def test_plan_covers_frozen_cases_without_dispatch(self) -> None:
        errors = validate_dry_run_plan(ROOT, self.plan)
        self.assertEqual([], errors)
        self.assertEqual(26, len(self.plan["cases"]))
        self.assertFalse(self.plan["commands_issued"])
        self.assertFalse(self.plan["hardware_touched"])
        self.assertEqual("NOT_RUN", self.plan["execution_status"])

    def test_real_inference_and_capture_cases_are_blocked(self) -> None:
        for row in self.plan["cases"]:
            if row["evidence_class"] in {"REAL_INFERENCE_REQUIRED", "REAL_CAPTURE_REQUIRED"}:
                self.assertEqual("BLOCKED_REAL_EVIDENCE_REQUIRED", row["disposition"])
                self.assertIsNone(row["command"])
                self.assertIsNone(row["result"])
                self.assertEqual("NOT_RUN", row["execution_status"])

    def test_replay_cannot_replace_real_evidence_or_claim_acceptance(self) -> None:
        row = next(row for row in self.plan["cases"] if row["case_id"] == "ACT-01")
        row["evidence_class"] = "REPLAY_ONLY"
        self.assertTrue(any("evidence_class" in error for error in validate_dry_run_plan(ROOT, self.plan)))

    def test_synthetic_substitution_cannot_be_enabled(self) -> None:
        row = next(row for row in self.plan["cases"] if row["case_id"] == "REC-07")
        row["synthetic_substitution_allowed"] = True
        self.assertTrue(any("合成替代许可" in error for error in validate_dry_run_plan(ROOT, self.plan)))

    def test_action_and_recovery_results_are_rejected_in_dry_run(self) -> None:
        for case_id in ("ACT-01", "UNK-01", "REC-08"):
            plan = copy.deepcopy(self.plan)
            row = next(row for row in plan["cases"] if row["case_id"] == case_id)
            row["result"] = {"status": "PASS"}
            self.assertTrue(any("不得含执行结果" in error for error in validate_dry_run_plan(ROOT, plan)))

    def test_missing_case_and_unknown_case_are_rejected(self) -> None:
        missing = copy.deepcopy(self.plan)
        missing["cases"].pop()
        self.assertTrue(any("用例 ID 集合" in error for error in validate_dry_run_plan(ROOT, missing)))
        extra = copy.deepcopy(self.plan)
        extra["cases"][0]["case_id"] = "ACT-99"
        self.assertTrue(any("用例 ID 集合" in error for error in validate_dry_run_plan(ROOT, extra)))
        malformed_id = copy.deepcopy(self.plan)
        malformed_id["cases"][0]["case_id"] = []
        self.assertTrue(any("case_id" in error for error in validate_dry_run_plan(ROOT, malformed_id)))

    def test_missing_source_field_and_command_dispatch_are_rejected(self) -> None:
        no_digest = copy.deepcopy(self.plan)
        del no_digest["source"]["sha256"]
        self.assertTrue(any("source.sha256" in error for error in validate_dry_run_plan(ROOT, no_digest)))
        no_source = copy.deepcopy(self.plan)
        del no_source["source"]
        self.assertTrue(any("source 必须为对象" in error for error in validate_dry_run_plan(ROOT, no_source)))
        has_command = copy.deepcopy(self.plan)
        has_command["cases"][0]["command"] = ["vivado", "program_hw"]
        self.assertTrue(any("可执行命令" in error for error in validate_dry_run_plan(ROOT, has_command)))

    def test_missing_or_forged_fields_fail_closed(self) -> None:
        self.assertTrue(any("根节点必须为对象" in error for error in validate_dry_run_plan(ROOT, [])))
        missing_run_id = copy.deepcopy(self.plan)
        missing_run_id["run_id"] = " "
        self.assertTrue(any("run_id" in error for error in validate_dry_run_plan(ROOT, missing_run_id)))
        changed_timeout = copy.deepcopy(self.plan)
        changed_timeout["cases"][0]["timeout_s"] = -1
        self.assertTrue(any("timeout_s" in error for error in validate_dry_run_plan(ROOT, changed_timeout)))
        duplicate_gate = copy.deepcopy(self.plan)
        duplicate_gate["board_window_gates"][-1] = copy.deepcopy(duplicate_gate["board_window_gates"][0])
        self.assertTrue(any("门禁集合" in error for error in validate_dry_run_plan(ROOT, duplicate_gate)))
        malformed_gate = copy.deepcopy(self.plan)
        malformed_gate["board_window_gates"][0]["gate"] = {}
        self.assertTrue(any("门禁集合" in error for error in validate_dry_run_plan(ROOT, malformed_gate)))
        forged_gate = copy.deepcopy(self.plan)
        forged_gate["board_window_gates"][0]["acceptance_status"] = "PASS"
        self.assertTrue(any("门禁计划项包含未批准字段" in error
                            for error in validate_dry_run_plan(ROOT, forged_gate)))

    def test_unknown_top_level_and_case_fields_are_rejected(self) -> None:
        for field, value in (("acceptance_status", "PASS"), ("real_inference_completed", True)):
            plan = copy.deepcopy(self.plan)
            plan[field] = value
            self.assertTrue(any(field in error for error in validate_dry_run_plan(ROOT, plan)))

        plan = copy.deepcopy(self.plan)
        plan["cases"][0]["real_inference_completed"] = True
        self.assertTrue(any("用例计划项包含未批准字段" in error
                            for error in validate_dry_run_plan(ROOT, plan)))
        missing = copy.deepcopy(self.plan)
        del missing["cases"][0]["reason"]
        self.assertTrue(any("用例计划项缺少字段" in error
                            for error in validate_dry_run_plan(ROOT, missing)))

        forged_scope = copy.deepcopy(self.plan)
        forged_scope["scope_note"] = "真实推理已完成，S6-E 已通过。"
        self.assertTrue(any("scope_note" in error for error in validate_dry_run_plan(ROOT, forged_scope)))
        forged_reason = copy.deepcopy(self.plan)
        forged_reason["cases"][0]["reason"] = "已完成真实验收并通过。"
        self.assertTrue(any("reason 不得添加" in error
                            for error in validate_dry_run_plan(ROOT, forged_reason)))

    def _run_validate_json(self, root: Path, plan_text: str) -> tuple[int, str]:
        plan_path = root / "candidate_plan.json"
        plan_path.write_text(plan_text, encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["validate", "--project-root", str(ROOT), "--plan", str(plan_path)])
        return result, output.getvalue()

    def test_validate_cli_rejects_duplicate_top_level_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = json.dumps(self.plan, ensure_ascii=False, indent=2)
            duplicate = text.replace('"acceptance_claim": false,',
                                      '"acceptance_claim": false,\n  "acceptance_claim": true,', 1)
            self.assertNotEqual(text, duplicate)
            code, output = self._run_validate_json(root, duplicate)
            self.assertEqual(2, code)
            self.assertIn("重复键", output)

    def test_validate_cli_rejects_duplicate_nested_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = json.dumps(self.plan, ensure_ascii=False, indent=2)
            duplicate = text.replace('"min": 10,', '"min": 10,\n          "min": 999,', 1)
            self.assertNotEqual(text, duplicate)
            code, output = self._run_validate_json(root, duplicate)
            self.assertEqual(2, code)
            self.assertIn("重复键", output)

    def test_plan_builder_rejects_duplicate_key_in_frozen_case_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            cases_path = root / "docs/stage6/s6e_stage6_acceptance_cases_v1.json"
            text = cases_path.read_text(encoding="utf-8")
            duplicate = text.replace('"task_id": "S6-E",',
                                     '"task_id": "S6-E",\n  "task_id": "S6-X",', 1)
            self.assertNotEqual(text, duplicate)
            cases_path.write_text(duplicate, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "重复键"):
                build_dry_run_plan(root, "s6e_command_delivery_20261027_r95")

    def test_validate_cli_rejects_overflow_float_at_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = json.dumps(self.plan, ensure_ascii=False, indent=2)
            overflow = text.replace('"schema_version": 1,', '"schema_version": 1e999,', 1)
            self.assertNotEqual(text, overflow)
            code, output = self._run_validate_json(root, overflow)
            self.assertEqual(2, code)
            self.assertIn("有限浮点范围", output)

    def test_validate_cli_rejects_overflow_float_in_nested_case(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = json.dumps(self.plan, ensure_ascii=False, indent=2)
            overflow = text.replace('"min": 10,', '"min": 1e999,', 1)
            self.assertNotEqual(text, overflow)
            code, output = self._run_validate_json(root, overflow)
            self.assertEqual(2, code)
            self.assertIn("有限浮点范围", output)

    def test_plan_cli_rejects_overflow_input_without_leaving_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            cases_path = root / "docs/stage6/s6e_stage6_acceptance_cases_v1.json"
            text = cases_path.read_text(encoding="utf-8")
            overflow = text.replace('"timeout_s": 30,', '"timeout_s": 1e999,', 1)
            self.assertNotEqual(text, overflow)
            cases_path.write_text(overflow, encoding="utf-8")
            run_id = "s6e_command_delivery_20261027_r96"
            self.assertEqual(2, self._run_plan_cli(root, run_id))
            self.assertFalse((root / "report/evidence/S6-E" / run_id).exists())

    def test_nonfinite_plan_serialization_fails_before_creating_run_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            run_id = "s6e_command_delivery_20261027_r97"
            plan = build_dry_run_plan(root, run_id)
            plan["cases"][0]["expected"] = float("inf")
            out = f"report/evidence/S6-E/{run_id}/dry_run_plan.json"
            with self.assertRaises(ValueError):
                _write_new_plan(root, run_id, out, plan)
            self.assertFalse((root / "report/evidence/S6-E" / run_id).exists())

    def test_strict_parser_accepts_normal_finite_floats(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "finite.json"
            path.write_text('{"ratio": 0.9, "nested": {"value": 1.25}}\n', encoding="utf-8")
            self.assertEqual({"ratio": 0.9, "nested": {"value": 1.25}}, _load_json_strict(path))

    def _temporary_project(self, temp_root: Path) -> Path:
        root = temp_root / "project"
        (root / "docs/stage6").mkdir(parents=True)
        (root / "report/evidence/S6-E").mkdir(parents=True)
        shutil.copyfile(ROOT / "docs/stage6/s6e_stage6_acceptance_cases_v1.json",
                        root / "docs/stage6/s6e_stage6_acceptance_cases_v1.json")
        return root

    def _run_plan_cli(self, root: Path, run_id: str, out: str | None = None) -> int:
        argv = ["plan", "--project-root", str(root), "--run-id", run_id]
        if out is not None:
            argv.extend(["--out", out])
        with contextlib.redirect_stdout(io.StringIO()):
            return main(argv)

    def test_output_must_be_the_canonical_new_run_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            run_id = "s6e_command_delivery_20261027_r91"
            source = root / "docs/stage6/s6e_stage6_acceptance_cases_v1.json"
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            rc = self._run_plan_cli(root, run_id, "docs/stage6/s6e_stage6_acceptance_cases_v1.json")
            self.assertEqual(2, rc)
            self.assertEqual(before, hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertFalse((root / "report/evidence/S6-E" / run_id).exists())

            external = str(Path(temp) / "outside.json")
            rc = self._run_plan_cli(root, run_id, external)
            self.assertEqual(2, rc)
            self.assertFalse(Path(external).exists())

            traversal = f"report/evidence/S6-E/{run_id}/../../../../outside.json"
            rc = self._run_plan_cli(root, run_id, traversal)
            self.assertEqual(2, rc)
            self.assertFalse((Path(temp) / "outside.json").exists())

    def test_run_id_must_match_the_s6e_run_id_grammar(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            self.assertEqual(2, self._run_plan_cli(root, "../escape"))
            self.assertEqual(2, self._run_plan_cli(root, "s6e_command_delivery_20260230_r01"))
            self.assertFalse(any((root / "report/evidence/S6-E").iterdir()))

    def test_output_is_created_once_and_repeated_run_preserves_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            run_id = "s6e_command_delivery_20261027_r92"
            expected = root / "report/evidence/S6-E" / run_id / "dry_run_plan.json"
            self.assertEqual(0, self._run_plan_cli(root, run_id))
            before = hashlib.sha256(expected.read_bytes()).hexdigest()
            self.assertEqual(2, self._run_plan_cli(root, run_id))
            self.assertEqual(before, hashlib.sha256(expected.read_bytes()).hexdigest())

    def test_existing_output_and_run_directory_are_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            run_id = "s6e_command_delivery_20261027_r93"
            run_dir = root / "report/evidence/S6-E" / run_id
            run_dir.mkdir()
            target = run_dir / "dry_run_plan.json"
            target.write_text("sentinel\n", encoding="utf-8")
            before = hashlib.sha256(target.read_bytes()).hexdigest()
            self.assertEqual(2, self._run_plan_cli(root, run_id))
            self.assertEqual(before, hashlib.sha256(target.read_bytes()).hexdigest())

    def test_symlink_or_junction_evidence_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = self._temporary_project(Path(temp))
            evidence_root = root / "report/evidence/S6-E"
            run_id = "s6e_command_delivery_20261027_r94"
            real_link_detector = "s6e_command_delivery_dryrun._is_linklike"
            with patch(real_link_detector, side_effect=lambda path: Path(path) == evidence_root):
                self.assertEqual(2, self._run_plan_cli(root, run_id))
            self.assertFalse((evidence_root / run_id).exists())

    def test_gate_status_cannot_be_claimed_from_offline_plan(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["board_window_gates"][0]["status"] = "PASS"
        self.assertTrue(any("门禁" in error for error in validate_dry_run_plan(ROOT, plan)))

    def test_plan_rejects_modified_source_digest(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["source"]["sha256"] = "0" * 64
        self.assertTrue(any("source.sha256" in error for error in validate_dry_run_plan(ROOT, plan)))


if __name__ == "__main__":
    unittest.main()
