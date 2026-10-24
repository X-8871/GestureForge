"""阶段6门禁修复的定向判别力测试；所有变异只写入系统临时目录。"""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from s6e_acceptance_check import BEHAVIOR, CASES, DOC, REAL_CASE_CLASSES, evaluate
from tool_self_tests import claim_normal_ok


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
