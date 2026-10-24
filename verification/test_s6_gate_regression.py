"""阶段6门禁修复的定向判别力测试；所有变异只写入系统临时目录。"""

import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from s6e_acceptance_check import BEHAVIOR, CASES, DOC, REAL_CASE_CLASSES, evaluate
import tool_self_tests
from tool_self_tests import (
    _normalize_run_rel,
    _normalize_s6a_run_rel,
    _resolve_confined_path,
    _resolve_run_dir,
    claim_normal_ok,
    main as tool_self_tests_main,
    make_temp_copy,
    prepare_clean_snapshot_fixture,
)


class GateRegression(unittest.TestCase):
    """正常与异常两侧必须同时成立。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        source = Path(__file__).resolve().parents[1]
        for relative in (BEHAVIOR, CASES, DOC):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)

    def load(self, relative):
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def save(self, relative, data):
        (self.root / relative).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_real_cases_each_reject_wrong_classes_and_synthetic(self):
        baseline = self.load(CASES)
        self.assertEqual(evaluate(self.root), [])
        for cid, required in REAL_CASE_CLASSES.items():
            for wrong in ("REPLAY_ONLY", "OFFLINE_SELFCHECK",
                          "REAL_CAPTURE_REQUIRED" if required == "REAL_INFERENCE_REQUIRED" else "REAL_INFERENCE_REQUIRED"):
                with self.subTest(cid=cid, wrong=wrong):
                    data = copy.deepcopy(baseline)
                    next(c for c in data["cases"] if c["id"] == cid)["evidence_class"] = wrong
                    self.save(CASES, data)
                    self.assertTrue(any(e.startswith("E7:") for e in evaluate(self.root)))
            for synthetic in (True, None, "false"):
                with self.subTest(cid=cid, synthetic=synthetic):
                    data = copy.deepcopy(baseline)
                    next(c for c in data["cases"] if c["id"] == cid)["synthetic_substitution_allowed"] = synthetic
                    self.save(CASES, data)
                    self.assertTrue(any(e.startswith("E7:") for e in evaluate(self.root)))
        self.save(CASES, baseline)
        self.assertEqual(evaluate(self.root), [])

    def test_each_parameter_requires_approved_status_and_reference(self):
        baseline = self.load(BEHAVIOR)
        for index in range(24):
            for status in (None, "REJECTED", "UNKNOWN", "PENDING_APPROVAL", "APPROVED"):
                with self.subTest(index=index, status=status):
                    data = copy.deepcopy(baseline)
                    if status is None:
                        data["parameters"][index].pop("approval_status")
                    else:
                        data["parameters"][index]["approval_status"] = status
                    self.save(BEHAVIOR, data)
                    self.assertTrue(any(e.startswith("E4:") for e in evaluate(self.root)))
            data = copy.deepcopy(baseline)
            data["parameters"][index]["approval_ref"] = "unapproved.md"
            self.save(BEHAVIOR, data)
            self.assertTrue(any(e.startswith("E4:") for e in evaluate(self.root)))
        self.save(BEHAVIOR, baseline)
        self.assertEqual(evaluate(self.root), [])

    def test_duplicate_parameter_records_never_hide_bad_status(self):
        baseline = self.load(BEHAVIOR)
        rejected = copy.deepcopy(baseline["parameters"][0])
        rejected["approval_status"] = "REJECTED"
        for ordering in ("rejected_before_approved", "approved_before_rejected"):
            with self.subTest(ordering=ordering):
                data = copy.deepcopy(baseline)
                if ordering == "rejected_before_approved":
                    data["parameters"].insert(0, rejected)
                else:
                    data["parameters"].append(rejected)
                self.save(BEHAVIOR, data)
                errors = evaluate(self.root)
                self.assertTrue(any(error.startswith("E4:") for error in errors))
                self.assertTrue(any("重复" in error for error in errors))
                self.assertTrue(any("approval_status" in error for error in errors))
        self.save(BEHAVIOR, baseline)
        self.assertEqual(evaluate(self.root), [])

    def test_extra_unknown_wrong_reference_parameter_is_rejected(self):
        baseline = self.load(BEHAVIOR)
        cases = self.load(CASES)
        extra = copy.deepcopy(baseline["parameters"][0])
        extra["id"] = "UNKNOWN-PARAM"
        extra["approval_ref"] = "report/evidence/unapproved_receipt.md"
        baseline["parameters"].append(extra)
        cases["approval_binding"]["approved_parameter_ids"].append("UNKNOWN-PARAM")
        self.save(BEHAVIOR, baseline)
        self.save(CASES, cases)
        errors = evaluate(self.root)
        self.assertTrue(any(error.startswith("E4:") for error in errors))
        self.assertTrue(any("UNKNOWN-PARAM" in error for error in errors))
        self.assertTrue(any("approval_ref" in error for error in errors))

    def test_duplicate_approved_parameter_id_is_rejected(self):
        baseline = self.load(CASES)
        baseline["approval_binding"]["approved_parameter_ids"].append(
            baseline["approval_binding"]["approved_parameter_ids"][0])
        self.save(CASES, baseline)
        errors = evaluate(self.root)
        self.assertTrue(any(error.startswith("E4:") for error in errors))
        self.assertTrue(any("重复 ID" in error for error in errors))

    def test_parameter_ids_must_match_the_formal_set(self):
        behavior = self.load(BEHAVIOR)
        cases = self.load(CASES)
        behavior["parameters"][0]["id"] = "UNKNOWN-PARAM"
        approved = cases["approval_binding"]["approved_parameter_ids"]
        approved[approved.index("T6-A01")] = "UNKNOWN-PARAM"
        for case in cases["cases"]:
            case["binds_parameters"] = [
                "UNKNOWN-PARAM" if pid == "T6-A01" else pid
                for pid in case["binds_parameters"]
            ]
        self.save(BEHAVIOR, behavior)
        self.save(CASES, cases)
        errors = evaluate(self.root)
        self.assertTrue(any(error.startswith("E4:") for error in errors))
        self.assertTrue(any("正式 24 项" in error for error in errors))

    def test_parameter_id_must_be_a_string(self):
        behavior = self.load(BEHAVIOR)
        behavior["parameters"][0]["id"] = 17
        self.save(BEHAVIOR, behavior)
        errors = evaluate(self.root)
        self.assertTrue(any("参数 ID 必须为字符串" in error for error in errors))

    def test_approved_parameter_ids_must_all_be_strings(self):
        cases = self.load(CASES)
        cases["approval_binding"]["approved_parameter_ids"][0] = 17
        self.save(CASES, cases)
        errors = evaluate(self.root)
        self.assertTrue(any("approved_parameter_ids 第 1 项必须为字符串" in error for error in errors))

    def test_claim_real_exit_and_all_claim_results(self):
        good = {"count_ok": True, "claims_declared": 1, "claims_recorded": 2,
                "verdict": "ALL_CLAIMS_VERIFIED", "claims": [
                    {"claim_id": "normal", "verdict": "VERIFIED", "exit_code": 0, "expected_exit": 0},
                    {"claim_id": "self_test_false_claim", "verdict": "VERIFIED", "exit_code": 1}]}
        self.assertTrue(claim_normal_ok(0, good))
        self.assertFalse(claim_normal_ok(1, good))
        for mutate in (
            lambda d: d.__setitem__("verdict", "NOT_ALL_VERIFIED"),
            lambda d: d["claims"][0].__setitem__("exit_code", 1),
            lambda d: d["claims"][0].__setitem__("verdict", "NOT_VERIFIED"),
            lambda d: d["claims"][0].__setitem__("readonly_violation", ["input.json"]),
            lambda d: d["claims"][1].pop("exit_code"),
            lambda d: d.__setitem__("claims", []),
        ):
            data = copy.deepcopy(good)
            mutate(data)
            self.assertFalse(claim_normal_ok(0, data))


class SnapshotFixturePathRegression(unittest.TestCase):
    """快照正例的源路径和复制目标必须保持在各自根目录内。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

    def _snapshot_repo(self, state_text: str = "") -> tuple[Path, Path]:
        root = self.base / "source_project"
        run_dir = root / "report/evidence/S6-A/valid_run"
        run_dir.mkdir(parents=True)
        (run_dir / "run_marker.txt").write_text("fixture source\n", encoding="utf-8")
        state = root / ".codex/STATE.md"
        state.parent.mkdir(parents=True)
        state.write_text(state_text, encoding="utf-8")
        verification = root / "verification"
        verification.mkdir()
        (verification / "tool_self_tests.py").write_text("# fixture\n", encoding="utf-8")
        (verification / "hash_convention_check.py").write_text("# fixture\n", encoding="utf-8")
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "snapshot-test@local"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "snapshot-test"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "snapshot fixture"], check=True)
        return root, run_dir

    @staticmethod
    def _snapshot(path: Path):
        stat = path.stat()
        return path.read_bytes(), stat.st_mtime_ns

    def test_traversal_and_absolute_run_ids_reject_before_clone_or_outside_write(self):
        root, _ = self._snapshot_repo()
        fixture_parent = self.base / "fixture_parent"
        fixture_parent.mkdir()
        source_escape = self.base / "run_escape"
        source_escape.mkdir()
        (source_escape / "source_marker.txt").write_text("source sentinel", encoding="utf-8")
        outside_target = fixture_parent / "run_escape"
        outside_target.mkdir()
        outside_marker = outside_target / "outside_marker.txt"
        outside_marker.write_text("must remain unchanged", encoding="utf-8")
        before = self._snapshot(outside_marker)

        invalid_paths = (
            "report/evidence/S6-A/../../../../run_escape",
            "../../run_escape",
            "C:/outside/run_escape",
            "//server/share/run_escape",
        )
        for invalid_path in invalid_paths:
            with self.subTest(invalid_path=invalid_path):
                with self.assertRaises(ValueError):
                    prepare_clean_snapshot_fixture(root, invalid_path, fixture_parent)
                self.assertFalse((fixture_parent / "project").exists())
                self.assertEqual(self._snapshot(outside_marker), before)

    def test_traversal_state_reference_rejects_before_clone_or_outside_write(self):
        bad_reference = "report/evidence/S6-A/../../../../state_escape"
        root, _ = self._snapshot_repo(f"`{bad_reference}`\n")
        fixture_parent = self.base / "fixture_parent"
        fixture_parent.mkdir()
        source_escape = self.base / "state_escape"
        source_escape.mkdir()
        (source_escape / "source_marker.txt").write_text("source sentinel", encoding="utf-8")
        outside_target = fixture_parent / "state_escape"
        outside_target.mkdir()
        outside_marker = outside_target / "outside_marker.txt"
        outside_marker.write_text("must remain unchanged", encoding="utf-8")
        before = self._snapshot(outside_marker)

        with self.assertRaisesRegex(ValueError, "STATE 证据引用"):
            prepare_clean_snapshot_fixture(root, "valid_run", fixture_parent)
        self.assertFalse((fixture_parent / "project").exists())
        self.assertEqual(self._snapshot(outside_marker), before)

    def test_relative_run_path_positive_and_destination_symlink_rejection(self):
        root, run_dir = self._snapshot_repo()
        run_rel = _normalize_s6a_run_rel("report/evidence/S6-A/valid_run")
        resolved = _resolve_confined_path(root, run_rel, "正例 S6-A RunId", must_exist=True)
        self.assertEqual(run_rel, "report/evidence/S6-A/valid_run")
        self.assertEqual(resolved, run_dir.resolve())

        fixture_root = self.base / "fixture_project"
        fixture_root.mkdir()
        outside = self.base / "outside_destination"
        outside.mkdir()
        link = fixture_root / "report"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt":
                self.skipTest(f"当前环境不允许创建目录符号链接：{exc}")
            junction = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(link), str(outside)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if junction.returncode != 0:
                self.skipTest(f"当前环境不允许创建目录符号链接或联接点：{junction.stdout}{junction.stderr}")
        self.addCleanup(self._remove_link, link)
        with self.assertRaises(ValueError):
            _resolve_confined_path(fixture_root, "report/evidence/copied.json",
                                   "符号链接目标", must_exist=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_make_temp_copy_and_main_reject_run_dir_traversal_drive_and_unc(self):
        root, _ = self._snapshot_repo()
        fixture_parent = self.base / "copy_parent"
        fixture_parent.mkdir()
        source_escape = self.base / "run_escape"
        source_escape.mkdir()
        (source_escape / "source_marker.txt").write_text("source sentinel", encoding="utf-8")
        outside_target = fixture_parent / "run_escape"
        outside_target.mkdir()
        outside_marker = outside_target / "outside_marker.txt"
        outside_marker.write_text("must remain unchanged", encoding="utf-8")
        outside_before = self._snapshot(outside_marker)
        invalid_paths = (
            "report/evidence/S6-A/../../../../run_escape",
            "../../run_escape",
            "C:/outside/run_escape",
            "//server/share/run_escape",
        )

        for invalid_path in invalid_paths:
            with self.subTest(api="make_temp_copy", invalid_path=invalid_path):
                with self.assertRaises(ValueError):
                    make_temp_copy(root, invalid_path, fixture_parent)
                self.assertFalse((fixture_parent / "copy").exists())
                self.assertEqual(self._snapshot(outside_marker), outside_before)
            with self.subTest(api="main", invalid_path=invalid_path):
                exit_code = tool_self_tests_main([
                    "--project-root", str(root), "--run-dir", invalid_path,
                    "--package", "s6a", "--out", "tmp/6/unsafe-output.json",
                ])
                self.assertEqual(exit_code, 2)
                self.assertFalse((root / "tmp").exists())
                self.assertEqual(self._snapshot(outside_marker), outside_before)

    def test_make_temp_copy_and_main_reject_state_reference_traversal(self):
        bad_reference = "report/evidence/S6-A/../../../../state_escape"
        root, _ = self._snapshot_repo(f"`{bad_reference}`\n")
        fixture_parent = self.base / "copy_parent"
        fixture_parent.mkdir()
        source_escape = self.base / "state_escape"
        source_escape.mkdir()
        (source_escape / "source_marker.txt").write_text("source sentinel", encoding="utf-8")
        outside_target = fixture_parent / "state_escape"
        outside_target.mkdir()
        outside_marker = outside_target / "outside_marker.txt"
        outside_marker.write_text("must remain unchanged", encoding="utf-8")
        outside_before = self._snapshot(outside_marker)

        with self.assertRaisesRegex(ValueError, "STATE 证据引用"):
            make_temp_copy(root, "report/evidence/S6-A/valid_run", fixture_parent)
        self.assertFalse((fixture_parent / "copy").exists())
        self.assertEqual(self._snapshot(outside_marker), outside_before)

        exit_code = tool_self_tests_main([
            "--project-root", str(root), "--run-dir", "report/evidence/S6-A/valid_run",
            "--package", "s6a", "--out", "tmp/6/unsafe-output.json",
        ])
        self.assertEqual(exit_code, 2)
        self.assertFalse((root / "tmp").exists())
        self.assertEqual(self._snapshot(outside_marker), outside_before)

    def test_make_temp_copy_valid_relative_run_and_state_reference(self):
        state_reference = "report/evidence/S6-A/valid_run/run_marker.txt"
        root, run_dir = self._snapshot_repo(f"`{state_reference}`\n")
        fixture_parent = self.base / "copy_parent"
        fixture_parent.mkdir()
        copy_root = make_temp_copy(root, "report/evidence/S6-A/valid_run", fixture_parent)
        copied_run = copy_root / "report/evidence/S6-A/valid_run"
        self.assertEqual((copied_run / "run_marker.txt").read_text(encoding="utf-8"), "fixture source\n")
        self.assertEqual((copy_root / state_reference).read_text(encoding="utf-8"), "fixture source\n")
        self.assertTrue((copy_root / ".codex/STATE.md").is_file())
        self.assertEqual(copy_root.parent, fixture_parent.resolve())

    def test_main_rejects_absolute_drive_unc_and_traversal_s6a_s6b_and_out(self):
        root, _ = self._snapshot_repo()
        outside_s6a = self.base / "outside_s6a"
        outside_s6b = self.base / "outside_s6b"
        outside_s6a.mkdir()
        outside_s6b.mkdir()
        outside_output = self.base / "outside_output.json"
        for path in (outside_s6a / "marker.txt", outside_s6b / "marker.txt"):
            path.write_text("must remain unchanged", encoding="utf-8")
        outside_output.write_text("must remain unchanged", encoding="utf-8")
        sentinels = (outside_s6a / "marker.txt", outside_s6b / "marker.txt", outside_output)
        before = {path: self._snapshot(path) for path in sentinels}
        invalid_values = {
            "--s6a-run": ("../outside_s6a", "/absolute/outside_s6a",
                           "C:/outside/s6a", "//server/share/s6a"),
            "--s6b-run": ("../outside_s6b", "/absolute/outside_s6b",
                           "C:/outside/s6b", "//server/share/s6b"),
            "--out": ("../outside_output.json", "/absolute/output.json",
                      "C:/outside/output.json", "//server/share/output.json"),
        }

        for option, paths in invalid_values.items():
            for invalid_value in paths:
                with self.subTest(option=option, invalid_value=invalid_value):
                    argv = ["--project-root", str(root), "--run-dir",
                            "report/evidence/S6-A/valid_run", "--package", "s6a",
                            "--out", "tmp/6/positive.json", option, invalid_value]
                    self.assertEqual(tool_self_tests_main(argv), 2)
                    self.assertFalse((root / "tmp").exists())
                    self.assertEqual({path: self._snapshot(path) for path in sentinels}, before)

        s6a_rel, s6a_dir = _resolve_run_dir(root, "report/evidence/S6-A/valid_run", "正例 --s6a-run")
        s6b_dir = root / "report/evidence/S6-B/valid_run"
        s6b_dir.mkdir(parents=True)
        s6b_rel, s6b_resolved = _resolve_run_dir(root, "report/evidence/S6-B/valid_run", "正例 --s6b-run")
        out_rel = _normalize_run_rel("tmp/6/positive.json", "正例 --out")
        out_path = _resolve_confined_path(root, out_rel, "正例 --out", must_exist=False)
        self.assertEqual(s6a_rel, "report/evidence/S6-A/valid_run")
        self.assertEqual(s6b_rel, "report/evidence/S6-B/valid_run")
        self.assertEqual(s6a_dir, (root / s6a_rel).resolve())
        self.assertEqual(s6b_resolved, s6b_dir.resolve())
        self.assertEqual(out_path, (root / out_rel).resolve())

    def test_main_rejects_verification_junction_before_any_child_or_output(self):
        root, _ = self._snapshot_repo()
        verification = root / "verification"
        shutil.move(str(verification), str(root / "verification_saved"))
        outside = self.base / "outside_verification"
        outside.mkdir()
        marker = outside / "export_selfproof.py"
        marker.write_text("must remain unchanged", encoding="utf-8")
        before = self._snapshot(marker)
        self._make_directory_link(verification, outside)
        calls = []
        original_run = tool_self_tests.run

        def run_spy(argv, cwd):
            calls.append(list(argv))
            return original_run(argv, cwd)

        with mock.patch.object(tool_self_tests, "run", side_effect=run_spy):
            exit_code = tool_self_tests_main([
                "--project-root", str(root), "--run-dir", "report/evidence/S6-A/valid_run",
                "--package", "s6a", "--out", "tmp/6/verification_link.json",
            ])
        self.assertEqual(exit_code, 2)
        self.assertEqual(calls, [])
        self.assertFalse((root / "tmp").exists())
        self.assertEqual(self._snapshot(marker), before)

    def test_main_rejects_out_and_fixed_child_output_parent_junctions(self):
        root, _ = self._snapshot_repo()
        temp_dir = root / "tmp"
        temp_dir.mkdir()
        outside = self.base / "outside_output_parent"
        outside.mkdir()
        marker = outside / "sentinel.txt"
        marker.write_text("must remain unchanged", encoding="utf-8")
        before = self._snapshot(marker)
        self._make_directory_link(temp_dir / "6", outside)
        cases = (
            ("--out parent", "tmp/6/unsafe_output.json"),
            ("fixed child output parent", "tmp/7/final_output.json"),
        )
        for label, out_value in cases:
            with self.subTest(label=label):
                calls = []
                original_run = tool_self_tests.run

                def run_spy(argv, cwd):
                    calls.append(list(argv))
                    return original_run(argv, cwd)

                with mock.patch.object(tool_self_tests, "run", side_effect=run_spy):
                    exit_code = tool_self_tests_main([
                        "--project-root", str(root), "--run-dir", "report/evidence/S6-A/valid_run",
                        "--package", "s6a", "--out", out_value,
                    ])
                self.assertEqual(exit_code, 2)
                self.assertEqual(calls, [])
                self.assertEqual(self._snapshot(marker), before)
                self.assertEqual(list(outside.iterdir()), [marker])
                self.assertFalse((root / "tmp/6/self_test_delivery.json").exists())
                self.assertFalse((root / "tmp/6/self_test_snapshot.json").exists())

    def test_main_rejects_nested_delivery_s6a_and_s6b_links_before_verification_child(self):
        root, _ = self._snapshot_repo()
        s6a_delivery = root / "report/evidence/S6-A/delivery_run"
        s6b_delivery = root / "report/evidence/S6-B/delivery_run"
        s6a_delivery.mkdir(parents=True)
        s6b_delivery.mkdir(parents=True)
        (s6a_delivery / "run_marker.txt").write_text("fixture source", encoding="utf-8")
        (s6b_delivery / "run_marker.txt").write_text("fixture source", encoding="utf-8")
        outside_a = self.base / "outside_delivery_a"
        outside_b = self.base / "outside_delivery_b"
        outside_a.mkdir()
        outside_b.mkdir()
        marker_a = outside_a / "marker.txt"
        marker_b = outside_b / "marker.txt"
        marker_a.write_text("must remain unchanged", encoding="utf-8")
        marker_b.write_text("must remain unchanged", encoding="utf-8")
        before = {marker_a: self._snapshot(marker_a), marker_b: self._snapshot(marker_b)}
        self._make_directory_link(s6a_delivery / "linked_tree", outside_a)
        self._make_directory_link(s6b_delivery / "linked_tree", outside_b)
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True, encoding="utf-8").stdout.strip()

        common = ["--project-root", str(root), "--run-dir", "report/evidence/S6-A/valid_run",
                  "--package", "s6a", "--s6a-run", "report/evidence/S6-A/valid_run",
                  "--delivery-commit", head, "--out", "tmp/6/delivery_link.json"]
        selected_pairs = (
            ("report/evidence/S6-A/delivery_run", "report/evidence/S6-B/delivery_run"),
            ("report/evidence/S6-A/valid_run", "report/evidence/S6-B/delivery_run"),
        )
        for delivery_s6a, delivery_s6b in selected_pairs:
            calls = []
            original_run = tool_self_tests.run

            def run_spy(argv, cwd):
                calls.append(list(argv))
                return original_run(argv, cwd)

            with self.subTest(delivery_s6a=delivery_s6a, delivery_s6b=delivery_s6b):
                with mock.patch.object(tool_self_tests, "run", side_effect=run_spy):
                    exit_code = tool_self_tests_main(common + [
                        "--delivery-s6a-run", delivery_s6a,
                        "--delivery-s6b-run", delivery_s6b,
                    ])
                self.assertEqual(exit_code, 2)
                self.assertTrue(calls)
                # 候选提交解析只运行只读的 git rev-parse，可在最终交付 RunId 子树检查前发生。
                self.assertTrue(all(argv and argv[0] == "git" for argv in calls))
                self.assertFalse((root / "tmp").exists())
                self.assertEqual({marker: self._snapshot(marker) for marker in before}, before)

    def _make_directory_link(self, link: Path, target: Path):
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt":
                self.skipTest(f"当前环境不允许创建目录符号链接：{exc}")
            junction = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if junction.returncode != 0:
                self.skipTest(f"当前环境不允许创建目录符号链接或联接点：{junction.stdout}{junction.stderr}")
        self.addCleanup(self._remove_link, link)

    @staticmethod
    def _remove_link(path: Path):
        if path.is_symlink():
            path.unlink(missing_ok=True)
        elif path.exists():
            path.rmdir()


if __name__ == "__main__":
    unittest.main(verbosity=2)
