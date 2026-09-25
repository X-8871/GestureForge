"""S2A-T23：逐值核查 M/Q 导出表、T16 摘要与冻结来源。"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from verification import s2a_conv_requant_table as table_module


ROOT = Path(__file__).resolve().parents[1]


class ConvRequantTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context, cls.t16 = table_module.build_context(ROOT)
        cls.table = table_module.materialize_table(cls.context, cls.t16)

    def assert_table_rejected(self, table) -> None:
        with self.assertRaises(table_module.RequantTableError):
            table_module.validate_parameter_table(table, self.context, self.t16)

    def test_complete_model_generation_matches_all_frozen_t16_digests(self) -> None:
        coverage = self.table["coverage"]
        self.assertEqual(coverage["convolution_layers"], 21)
        self.assertEqual(coverage["output_channels"], 3164)
        self.assertEqual(coverage["candidate_digest_layers_match"], 21)
        self.assertEqual(coverage["d2_digest_layers_match"], 21)
        self.assertEqual(coverage["signed_transition_comparisons"], 3164 * 254)
        self.assertEqual(coverage["int32_endpoint_comparisons"], 3164 * 2)
        self.assertEqual(self.table["status"], "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH")
        table_map = {item["layer_index"]: item for item in self.table["layers"]}
        for proof_row in self.context["proof"]["layers"]:
            row = table_map[proof_row["layer_index"]]
            self.assertEqual(row["candidate_parameter_sha256"], proof_row["candidate_parameter_sha256"])
            self.assertEqual(row["d2_threshold_and_endpoint_sha256"], proof_row["d2_threshold_and_endpoint_sha256"])
            self.assertEqual(row["target_threshold_sha256"], proof_row["target_threshold_sha256"])

    def test_linear_and_leaky_use_frozen_branch_rules(self) -> None:
        rows = {item["layer_index"]: item for item in self.table["layers"]}
        linear_layer = next(item for item in self.table["layers"] if item["activation"] == "linear")
        leaky_layer = next(item for item in self.table["layers"] if item["activation"] == "leaky")
        linear_channel = linear_layer["channels"][0]
        self.assertTrue(linear_channel["linear_shared_parameter"])
        self.assertEqual((linear_channel["positive_M"], linear_channel["positive_Q"]), (linear_channel["negative_M"], linear_channel["negative_Q"]))
        leaky_channel = leaky_layer["channels"][0]
        self.assertFalse(leaky_channel["linear_shared_parameter"])
        self.assertAlmostEqual(
            leaky_channel["parameter_source"]["ideal_negative_slope_float64"],
            leaky_channel["parameter_source"]["ideal_positive_slope_float64"] * 0.1,
            places=15,
        )
        self.assertEqual(rows[linear_layer["layer_index"]]["activation"], "linear")

    def test_required_source_hash_mutation_or_omission_fails_closed(self) -> None:
        records = copy.deepcopy(self.context["source_bindings"])
        target = next(item for item in records if item["path"] == table_module.T16_SCRIPT_PATH)
        target["sha256"] = "0" * 64
        with self.assertRaises(table_module.RequantTableError):
            table_module.validate_source_records(records, self.context["dynamic_source_bindings"])
        records = copy.deepcopy(self.context["source_bindings"])
        records = [item for item in records if item["path"] != table_module.T16_PROOF_PATH]
        with self.assertRaises(table_module.RequantTableError):
            table_module.validate_source_records(records, self.context["dynamic_source_bindings"])

    def test_d2_source_hash_mutation_fails_against_manifest_and_proof_binding(self) -> None:
        records = copy.deepcopy(self.context["source_bindings"])
        target = next(item for item in records if item.get("role") == "d2_numeric_reference")
        target["sha256"] = "0" * 64
        with self.assertRaises(table_module.RequantTableError):
            table_module.validate_source_records(records, self.context["dynamic_source_bindings"])

    def test_proof_coverage_and_failure_status_are_required(self) -> None:
        proof = copy.deepcopy(self.context["proof"])
        proof["coverage"]["output_channels_audited"] -= 1
        with self.assertRaises(table_module.RequantTableError):
            table_module._proof_layer_map(proof)
        proof = copy.deepcopy(self.context["proof"])
        proof["failures"] = [{"kind": "mutated_failure"}]
        with self.assertRaises(table_module.RequantTableError):
            table_module._proof_layer_map(proof)

    def test_layer_omission_or_reordering_is_rejected(self) -> None:
        table = copy.deepcopy(self.table)
        table["layers"].pop()
        self.assert_table_rejected(table)
        table = copy.deepcopy(self.table)
        table["layers"][0], table["layers"][1] = table["layers"][1], table["layers"][0]
        self.assert_table_rejected(table)

    def test_channel_omission_or_reordering_is_rejected(self) -> None:
        table = copy.deepcopy(self.table)
        table["layers"][0]["channels"].pop()
        self.assert_table_rejected(table)
        table = copy.deepcopy(self.table)
        table["layers"][0]["channels"][0], table["layers"][0]["channels"][1] = table["layers"][0]["channels"][1], table["layers"][0]["channels"][0]
        self.assert_table_rejected(table)

    def test_parameter_or_any_summary_digest_mutation_is_rejected(self) -> None:
        table = copy.deepcopy(self.table)
        table["layers"][0]["channels"][0]["positive_M"] += 1
        self.assert_table_rejected(table)
        table = copy.deepcopy(self.table)
        table["layers"][0]["candidate_parameter_sha256"] = "0" * 64
        self.assert_table_rejected(table)
        table = copy.deepcopy(self.table)
        table["layers"][0]["d2_threshold_and_endpoint_sha256"] = "0" * 64
        self.assert_table_rejected(table)

    def test_changed_manifest_scale_cannot_reproduce_the_frozen_layer_digest(self) -> None:
        layer = copy.deepcopy(next(item for item in self.context["manifest"]["layers"] if item.get("op") == "convolutional"))
        layer["weight_scale_per_output_channel"][0] *= 1.25
        with self.assertRaises(table_module.RequantTableError):
            table_module._materialize_layer(self.context, layer, self.t16)

    def test_export_contains_no_machine_specific_absolute_paths(self) -> None:
        serialized = json.dumps(self.table, ensure_ascii=False)
        self.assertNotIn("D:\\", serialized)
        self.assertNotIn("C:\\", serialized)
        self.assertNotIn("generated_at", self.table)
        self.assertEqual(self.table["statistics"]["hardware_multiplier_width"], "NOT_FROZEN; mathematical M bit length is reported separately")
        self.assertEqual(self.table["limitations"]["resource_estimation"], "NOT_PERFORMED")
        self.assertEqual(self.table["limitations"]["timing_analysis"], "NOT_PERFORMED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
