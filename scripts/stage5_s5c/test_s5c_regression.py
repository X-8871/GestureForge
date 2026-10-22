#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-C 回归勾连检查器的自检（unittest）：正例与反例两条路径都必须走通。

覆盖：
- 全 109 样本 / 104 框：C1 字段级一致（离散全等、score/xyxy ≤1e-6 且逐字节相同）→ PASS
- C2 常量与契约/阶段4 权威一致、accepted 集合 ≡ 阶段4 框集合、显示路径无禁用 token
- C3 S4-B 三样本 geometry_letterbox 逐值一致 + 样本集 21 种几何三方一致 + 683×384 补充用例
- C4 像素往返 ≤1.0 px、边框像素展开逐像素一致、零面积框不产生边框像素（含正对照）
- C5 S4-B 三条 PS 记录与 S4-C 同 sample_id 逐字段一致、D9 追溯链（T29 SHA256）完整
- C6 八个篡改探针全部被检出（含 1 ULP 级只由位型门槛捕获）、阶段4 权威记录未被改动
- C7 消费字段名为 score、无「无依据」用词；分类规则单元检查
- CLI 真实退出码：未篡改正对照 0 / 篡改探针 1 / 输入缺失 2
- 抽样确定性（同种子同样本集合）与清单哈希绑定

运行：`python -B scripts/stage5_s5c/test_s5c_regression.py -v`（真实退出码 0 表示全部通过）。
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import check_s5c_stage4_regression as C  # noqa: E402

TMP_ROOT = REPO_ROOT / "tmp" / "5" / "S5-C" / "unittest"
SUBSET_LIMIT = 8
SUBSET_SEED = 20261021
_CACHE = {"full_report": None}


def _args(**overrides):
    base = {
        "run_id": "unittest",
        "out": None,
        "limit": None,
        "seed": None,
        "tamper_probe": "none",
        "golden": str(C.DEFAULT_GOLDEN),
        "s4b_dir": str(C.DEFAULT_S4B_DIR),
        "finalize_exit_codes": False,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


class SharedContext(unittest.TestCase):
    """共享上下文：只加载一次上游输入，避免每个用例重复读盘。"""

    ctx = None
    log = None

    @classmethod
    def setUpClass(cls):
        TMP_ROOT.mkdir(parents=True, exist_ok=True)
        cls.log = C.RunLog()
        cls.ctx = C.build_context(_args(), cls.log)
        cls.subset, cls.subset_selection = C.select_samples(
            cls.ctx["golden"], SUBSET_LIMIT, SUBSET_SEED, cls.log)


class TestFullDataset(SharedContext):
    def test_full_109_dataset_passes(self):
        if _CACHE["full_report"] is None:
            _CACHE["full_report"] = C.run_checks(self.ctx, _args(), {
                "rule": "full_all_samples", "available": 109, "selected": 109, "limit": None,
                "seed": None, "seed_source": "not_used_full_selection",
                "sample_ids": [s["sample_id"] for s in self.ctx["golden"]["samples"]]},
                list(self.ctx["golden"]["samples"]), self.log)
        report = _CACHE["full_report"]
        self.assertEqual(report["status"], "PASS", json.dumps(report["failures"], ensure_ascii=False))
        stats = report["statistics"]
        self.assertEqual(stats["samples_selected"], 109)
        self.assertEqual(stats["boxes_compared"], 104)
        self.assertEqual(stats["boxes_with_zero_detections"], 8)
        self.assertEqual(stats["max_score_abs_error"], 0.0)
        self.assertEqual(stats["max_xyxy_abs_error"], 0.0)
        self.assertEqual(stats["bit_identity_violations"], 0)
        self.assertLessEqual(stats["max_pixel_roundtrip_px"], 1.0)
        self.assertEqual(stats["geometries_checked"], 21)
        self.assertEqual(stats["s4b_records_checked"], 3)
        self.assertEqual(stats["s4b_records_skipped"], 0)
        for name in ("C1_field_consistency", "C2_no_second_semantics", "C3_geometry_crosscheck",
                     "C4_pixel_roundtrip", "C5_d9_traceability", "C7_wording_contract"):
            self.assertEqual(report["checks"][name]["status"], "PASS", f"{name} 未通过")
        self.assertEqual(report["checks"]["C1_field_consistency"]["field_values_compared"],
                         104 * 8 + 109 * 3)
        self.assertTrue(all(row["status"] == "PASS"
                            for row in report["checks"]["C1_field_consistency"]["per_sample"]))


class TestNoSecondSemantics(SharedContext):
    def test_constants_match_contract_and_s4a(self):
        report = C.run_checks(self.ctx, _args(), self.subset_selection, self.subset, self.log)
        c2 = report["checks"]["C2_no_second_semantics"]
        self.assertTrue(c2["checks"]["constants_match_contract_and_s4a"])
        for name, item in c2["constants"].items():
            self.assertTrue(item["match"], f"{name} 与契约/阶段4 权威不一致")

    def test_accepted_set_equals_stage4(self):
        report = C.run_checks(self.ctx, _args(), self.subset_selection, self.subset, self.log)
        self.assertTrue(report["checks"]["C2_no_second_semantics"]["checks"]
                        ["accepted_set_equals_stage4_boxes"])
        self.assertLessEqual(report["checks"]["C2_no_second_semantics"]["max_box_count"],
                             self.ctx["ref"].MAX_OUTPUTS_PER_IMAGE)

    def test_display_path_source_clean(self):
        source = C.display_path_source()
        self.assertNotIn("letterbox_geometry", source)
        self.assertNotIn("network_norm_to_original_norm", source)
        report = C.run_checks(self.ctx, _args(), self.subset_selection, self.subset, self.log)
        c2 = report["checks"]["C2_no_second_semantics"]
        self.assertEqual(c2["display_path_forbidden_tokens_hit"], [])
        self.assertEqual(c2["loaded_suspect_modules"], [])

    def test_alias_identity_of_consumed_objects(self):
        ref = self.ctx["ref"]
        consumer = C.DisplayConsumer(ref)
        for sample in self.subset[:3]:
            record = C.golden_to_stage4_record(sample)
            display = consumer.consume(record)
            self.assertIs(display["detections"], record["detections"])
            for a, b in zip(display["detections"], record["detections"]):
                self.assertIs(a, b)


class TestGeometry(SharedContext):
    def test_s4b_letterbox_matches_reference(self):
        report = C.check_c3(self.ctx, self.ctx["golden"], self.log)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["s4b_records"]), 3)
        for row in report["s4b_records"]:
            self.assertEqual(row["status"], "PASS")
            for comparison in row["comparisons"]:
                self.assertTrue(comparison["match"])

    def test_21_geometries_three_way_agree(self):
        report = C.check_c3(self.ctx, self.ctx["golden"], self.log)
        self.assertEqual(report["sample_set_geometry_count"], 21)
        self.assertTrue(all(row["agree"] for row in report["sample_set_geometries"]))
        self.assertTrue(all(not row["degenerate"] for row in report["sample_set_geometries"]))

    def test_asymmetric_padding_preserved_and_683x384_supplemental(self):
        report = C.check_c3(self.ctx, self.ctx["golden"], self.log)
        self.assertGreaterEqual(len(report["asymmetric_padding_cases"]), 1)
        for case in report["asymmetric_padding_cases"]:
            # 非对称补边事实：左右（或上下）补边不相等，禁止被对称化
            self.assertTrue(case["pad_right"] != case["offset_x"]
                            or case["pad_bottom"] != case["offset_y"], case["src_wh"])
        supplemental = report["supplemental_683x384"]
        self.assertFalse(supplemental["in_sample_set"])
        self.assertEqual(supplemental["reference"]["offset_y"], 91)
        self.assertEqual(supplemental["pad_bottom"], 92)
        self.assertTrue(supplemental["match_contract"])
        self.assertTrue(supplemental["agree_three_way"])

    def test_independent_recompute_matches_reference(self):
        ref = self.ctx["ref"]
        for src_w, src_h in ((1440, 1920), (1920, 1080), (640, 963), (1080, 2400), (1437, 1920)):
            geom = ref.letterbox_geometry(src_w, src_h)
            indep = C.independent_letterbox(src_w, src_h)
            for key in ("new_width", "new_height", "offset_x", "offset_y"):
                self.assertEqual(geom[key], indep[key], f"{src_w}x{src_h} {key}")


class TestPixelLayer(SharedContext):
    def test_pixel_roundtrip_and_border_expansion(self):
        report = C.check_c4(self.ctx["ref"], self.subset, C.DisplayConsumer(self.ctx["ref"]), self.log)
        self.assertEqual(report["status"], "PASS")
        self.assertLessEqual(report["max_pixel_roundtrip_px"], 1.0)
        for row in report["per_box"]:
            self.assertTrue(row["border_expansion_exact"])
            self.assertTrue(row["recovery_matches_geometry"])
            self.assertIn(row["recovery_status"], ("unique", "non_unique"))
            self.assertLessEqual(row["px_roundtrip_max_error_px"], 1.0)

    def test_zero_area_boxes_produce_no_border_pixels(self):
        report = C.check_c4(self.ctx["ref"], self.subset, C.DisplayConsumer(self.ctx["ref"]), self.log)
        probes = report["zero_area_probes"]
        self.assertEqual(len(probes), 4)
        for probe in probes:
            self.assertTrue(probe["zero_area"], probe["probe"])
            self.assertEqual(probe["display_border_pixels"], 0, probe["probe"])
            self.assertGreater(probe["raw_expansion_if_not_skipped"], 0, probe["probe"])
        self.assertEqual(report["positive_control"]["status"], "PASS")
        self.assertGreater(report["positive_control"]["border_pixel_count"], 0)


class TestD9Traceability(SharedContext):
    def test_s4b_records_link_to_s4c(self):
        report = C.check_c5(self.ctx["ref"], self.ctx, self.ctx["golden"], self.log)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["records"]), 3)
        self.assertEqual(report["skips"], [])
        self.assertEqual(report["mismatch_count"], 0)
        for row in report["records"]:
            self.assertTrue(row["found_in_s4c"])
            self.assertEqual(row["status"], "PASS")

    def test_d9_chain_and_t29_hash(self):
        report = C.check_c5(self.ctx["ref"], self.ctx, self.ctx["golden"], self.log)
        chain = report["d9_traceability_chain"]
        self.assertTrue(chain["chain_ok"])
        self.assertTrue(chain["t29_file"]["exists"])
        self.assertTrue(chain["t29_file"]["match"], "T29 独立 SHA256 与 S4-C 绑定不一致")
        for row in chain["per_sample"]:
            self.assertEqual(row["s4c_status"], "PASS")
            self.assertEqual(row["s4c_mismatch_count"], 0)
            self.assertTrue(row["head13_tensor_sha256_match_t29"])
            self.assertTrue(row["head26_tensor_sha256_match_t29"])

    def test_skip_is_explicit_not_silent(self):
        """sample_id 对不上时必须显式 SKIP 并带理由。"""
        golden = json.loads(json.dumps(self.ctx["golden"]))
        golden["samples"] = [s for s in golden["samples"] if s["sample_id"] != "test_one_056"]
        ctx = dict(self.ctx)
        ctx["golden"] = golden
        report = C.check_c5(self.ctx["ref"], ctx, golden, self.log)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(len(report["skips"]), 1)
        self.assertEqual(report["skips"][0]["sample_id"], "test_one_056")
        self.assertTrue(report["skips"][0]["reason"])


class TestWordingContract(SharedContext):
    def test_consumed_field_name_and_no_unjustified_usage(self):
        report = C.check_c7(self.ctx["ref"], self.ctx, self.log)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["checks"]["consumed_field_name_is_score"])
        self.assertTrue(report["checks"]["no_confidence_field_consumed"])
        self.assertEqual(report["unjustified"], [])
        self.assertGreater(report["finding_count"], 0)

    def test_classification_rule(self):
        self.assertEqual(C.classify_occurrence("字段 confidence ≡ 本文 score", False)[0],
                         "EQUIVALENCE_DECLARATION")
        self.assertEqual(C.classify_occurrence("禁止称置信度", False)[0],
                         "PROHIBITION_DECLARATION")
        self.assertEqual(C.classify_occurrence("本帧置信度 0.83 已显示", False)[0], "UNJUSTIFIED")
        self.assertEqual(C.classify_occurrence("本帧置信度 0.83 已显示", True)[0],
                         "FILE_POLICY_DECLARATION")


class TestTamperProbes(SharedContext):
    def _probe(self, kind):
        args = _args(run_id=f"unittest_{kind}", tamper_probe=kind)
        return C.run_tamper_probe(self.ctx, args, self.subset, self.log)

    def test_required_probes_detected(self):
        for kind in C.PROBE_REQUIRED:
            with self.subTest(kind=kind):
                result = self._probe(kind)
                self.assertTrue(result["detected"], f"探针 {kind} 未被检出")
                self.assertEqual(result["status"], "FAIL")
                self.assertGreater(result["violation_count"], 0)
                self.assertTrue(result["authority_unchanged"])

    def test_one_ulp_probe_only_caught_by_bit_identity(self):
        result = self._probe("score_ulp")
        self.assertTrue(result["detected"])
        self.assertFalse(result["gate_a_violated"], "1 ULP 改动不应超过 1e-6 容差")
        self.assertTrue(result["gate_d_bit_identity_violated"])

    def test_tolerance_probe_caught_by_both_gates(self):
        result = self._probe("score_tol")
        self.assertTrue(result["gate_a_violated"])
        self.assertTrue(result["gate_d_bit_identity_violated"])

    def test_all_extra_probes_detected(self):
        for kind in ("score_tol", "xyxy_tol", "frame_id", "identity_rebuild"):
            with self.subTest(kind=kind):
                self.assertTrue(self._probe(kind)["detected"])

    def test_authority_snapshot_unchanged(self):
        args = _args(run_id="unittest_authority", tamper_probe="box_count")
        before = C.authority_snapshot(self.subset)
        C.run_tamper_probe(self.ctx, args, self.subset, self.log)
        self.assertEqual(before, C.authority_snapshot(self.subset))


class TestSelectionAndManifest(SharedContext):
    def test_seeded_subset_is_deterministic(self):
        first, sel_first = C.select_samples(self.ctx["golden"], SUBSET_LIMIT, SUBSET_SEED, self.log)
        second, sel_second = C.select_samples(self.ctx["golden"], SUBSET_LIMIT, SUBSET_SEED, self.log)
        self.assertEqual(sel_first["sample_ids"], sel_second["sample_ids"])
        self.assertEqual([s["sample_id"] for s in first], [s["sample_id"] for s in second])
        self.assertEqual(sel_first["seed"], SUBSET_SEED)
        self.assertEqual(sel_first["rule"], "seeded_random_subset")

    def test_manifest_binds_hashes(self):
        report = C.run_checks(self.ctx, _args(), self.subset_selection, self.subset, self.log)
        manifest = C.build_manifest(_args(), self.ctx, self.subset_selection, report, self.log,
                                    time.time())
        self.assertEqual(manifest["imported_modules"][0]["sha256"], self.ctx["ref_sha256"])
        self.assertEqual(manifest["imported_modules"][1]["sha256"], self.ctx["d2_sha256"])
        self.assertEqual(manifest["upstream_inputs"][0]["sha256"], self.ctx["golden_sha256"])
        self.assertTrue(manifest["scripts"][0]["sha256"])
        self.assertEqual(manifest["exit_code"], 0)
        self.assertEqual(manifest["statistics"]["seed"], SUBSET_SEED)


class TestCliExitCodes(SharedContext):
    def _run_cli(self, extra, expect, name):
        out_dir = pathlib.Path(tempfile.mkdtemp(prefix=f"{name}-", dir=str(TMP_ROOT)))
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        command = [sys.executable, "-B", str(HERE / "check_s5c_stage4_regression.py"),
                   "--run-id", name, "--out", str(out_dir)] + extra
        completed = subprocess.run(command, capture_output=True, encoding="utf-8",
                                   errors="replace", env=env, cwd=str(REPO_ROOT), timeout=900)
        self.assertEqual(completed.returncode, expect,
                         f"{name} 退出码 {completed.returncode} != {expect}\n{completed.stdout[-2000:]}")
        return out_dir, completed

    def test_pristine_cli_exit_zero(self):
        out_dir, completed = self._run_cli(
            ["--limit", str(SUBSET_LIMIT), "--seed", str(SUBSET_SEED)], 0, "pristine_subset")
        report = json.loads((out_dir / "regression_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["statistics"]["samples_selected"], SUBSET_LIMIT)
        self.assertEqual(report["checks"]["C6_tamper_probe"]["status"], "NOT_APPLICABLE_THIS_RUN")
        self.assertIn("EXIT", (out_dir / "console" / "seeded_subset.log.txt").read_text(encoding="utf-8"))

    def test_tamper_cli_exit_one(self):
        out_dir, _ = self._run_cli(
            ["--limit", str(SUBSET_LIMIT), "--seed", str(SUBSET_SEED), "--tamper-probe", "box_count"],
            1, "tamper_box_count")
        evidence = json.loads((out_dir / "tamper" / "tamper_box_count_before_after.json")
                              .read_text(encoding="utf-8"))
        self.assertTrue(evidence["detected"])
        self.assertTrue(evidence["authority_unchanged"])

    def test_missing_input_exit_two(self):
        out_dir = pathlib.Path(tempfile.mkdtemp(prefix="missing-", dir=str(TMP_ROOT)))
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        command = [sys.executable, "-B", str(HERE / "check_s5c_stage4_regression.py"),
                   "--run-id", "missing", "--out", str(out_dir),
                   "--golden", str(out_dir / "not_exists.json")]
        completed = subprocess.run(command, capture_output=True, encoding="utf-8",
                                   errors="replace", env=env, cwd=str(REPO_ROOT), timeout=300)
        self.assertEqual(completed.returncode, 2, (completed.stdout or "")[-2000:])

    def test_existing_run_dir_not_overwritten(self):
        out_dir = pathlib.Path(tempfile.mkdtemp(prefix="guard-", dir=str(TMP_ROOT)))
        (out_dir / "regression_report.json").write_text("{}", encoding="utf-8")
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        command = [sys.executable, "-B", str(HERE / "check_s5c_stage4_regression.py"),
                   "--run-id", "guard", "--out", str(out_dir), "--limit", "2"]
        completed = subprocess.run(command, capture_output=True, encoding="utf-8",
                                   errors="replace", env=env, cwd=str(REPO_ROOT), timeout=300)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual((out_dir / "regression_report.json").read_text(encoding="utf-8"), "{}")


if __name__ == "__main__":
    unittest.main(verbosity=2)