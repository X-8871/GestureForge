"""S2A-T22：验证 manifest 派生的整网 dispatch contract 和 fail-closed 行为。"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from verification import s2a_network_dispatch_contract as contract_module


ROOT = Path(__file__).resolve().parents[1]


class NetworkDispatchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / contract_module.MANIFEST_PATH).read_text(encoding="utf-8"))
        cls.fixed_samples = json.loads((ROOT / contract_module.FIXED_SAMPLES_PATH).read_text(encoding="utf-8"))
        cls.t16_proof = json.loads((ROOT / contract_module.T16_PROOF_PATH).read_text(encoding="utf-8"))
        cls.source_bindings = contract_module.collect_source_bindings(ROOT)

    def build(self, manifest=None, fixed_samples=None, t16_proof=None, source_bindings=None):
        return contract_module.derive_contract(
            copy.deepcopy(self.manifest if manifest is None else manifest),
            copy.deepcopy(self.fixed_samples if fixed_samples is None else fixed_samples),
            copy.deepcopy(self.t16_proof if t16_proof is None else t16_proof),
            copy.deepcopy(self.source_bindings if source_bindings is None else source_bindings),
        )

    def assert_contract_rejected(self, **overrides) -> None:
        with self.assertRaises(contract_module.ContractError):
            self.build(**overrides)

    def test_true_manifest_produces_38_ordered_rows_and_exact_counts(self) -> None:
        contract = self.build()
        rows = contract["network_dispatch"]["layers"]
        self.assertEqual(len(rows), 38)
        self.assertEqual([row["layer_index"] for row in rows], list(range(38)))
        self.assertEqual([row["cfg_section"] for row in rows], list(range(1, 39)))
        self.assertEqual(
            contract["network_dispatch"]["operator_counts"],
            {"convolutional": 21, "maxpool": 3, "route": 11, "upsample": 1, "yolo": 2},
        )
        self.assertEqual(rows[0]["input_tensors_in_manifest_order"][0]["kind"], "network_input")
        self.assertEqual(rows[0]["input_tensors_in_manifest_order"][0]["source_index"], "network_input")
        self.assertEqual(rows[34]["input_tensors_in_manifest_order"][0]["source_index"], 33)
        self.assertEqual(rows[34]["input_tensors_in_manifest_order"][1]["source_index"], 23)

    def test_tensor_byte_ranges_and_109_sample_footprint_are_derived(self) -> None:
        contract = self.build()
        rows = contract["network_dispatch"]["layers"]
        independently_derived = sum(
            int(row["tensor_length_bytes"])
            for row in self.manifest["layers"]
            if row["op"] != "yolo"
        )
        self.assertEqual(independently_derived, 11_382_150)
        self.assertEqual(contract["network_dispatch"]["owned_feature_tensor_bytes_per_sample"], independently_derived)
        self.assertEqual(contract["network_dispatch"]["raw_unique_feature_tensor_bytes_for_fixed_samples"], independently_derived * 109)
        self.assertEqual(independently_derived * 109, 1_240_654_350)
        for manifest_row, contract_row in zip(self.manifest["layers"], rows):
            shape = manifest_row["output_shape_nchw"]
            expected_bytes = shape[0] * shape[1] * shape[2] * shape[3]
            output = contract_row["output_tensor"]
            self.assertEqual(output["length_bytes"], expected_bytes)
            self.assertEqual(output["byte_range_half_open"], [output["address"], output["address"] + expected_bytes])

    def test_yolo_rows_are_aliases_and_never_write_feature_memory(self) -> None:
        contract = self.build()
        rows = contract["network_dispatch"]["layers"]
        self.assertEqual(rows[30]["output_tensor"]["alias_of_layer_index"], 29)
        self.assertEqual(rows[37]["output_tensor"]["alias_of_layer_index"], 36)
        for index in (30, 37):
            self.assertEqual(rows[index]["output_tensor"]["memory_write_required"], False)
            self.assertEqual(rows[index]["output_tensor"]["allocation_kind"], "head_alias")
        self.assertEqual(rows[30]["output_tensor"]["byte_range_half_open"], rows[29]["output_tensor"]["byte_range_half_open"])
        self.assertEqual(rows[37]["output_tensor"]["byte_range_half_open"], rows[36]["output_tensor"]["byte_range_half_open"])

    def test_operator_specific_parameters_keep_padding_route_order_and_alias_contract(self) -> None:
        contract = self.build()
        rows = contract["network_dispatch"]["layers"]
        for row in rows:
            if row["op"] == "maxpool":
                params = row["operator_parameters"]
                self.assertEqual(params["darknet_padding_parameter"], 1)
                self.assertEqual(params["padding_lrtb_actual"], [0, 0, 0, 0])
            if row["op"] == "upsample":
                self.assertEqual(row["operator_parameters"]["method"], "nearest_repeat")
            if row["op"] == "route":
                source_refs = [item["source_index"] for item in row["input_tensors_in_manifest_order"]]
                self.assertEqual(source_refs, self.manifest["layers"][row["layer_index"]]["input_tensor_indices"])
        conv36 = rows[36]["operator_parameters"]["parameters"]
        self.assertEqual(conv36["gf8_weight"]["offset_bytes"], self.manifest["layers"][36]["gf8_parameter_offsets"]["quantized_weight_offset"])
        self.assertEqual(conv36["gf8_weight"]["length_bytes"], 7680)
        self.assertEqual(conv36["t16_requantization_source"]["channel_payload_materialized_in_proof_json"], False)
        self.assertTrue(conv36["t16_requantization_source"]["candidate_parameter_sha256"])
        self.assertIn("T23", conv36["t16_requantization_source"]["backend_dependency"])

    def test_route_uses_per_reference_scales_and_preserves_legacy_scalar(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][8]["input_scale"] = 0.987654321
        contract = self.build(manifest=manifest)
        route8 = contract["network_dispatch"]["layers"][8]
        self.assertEqual(route8["manifest_input_scale"], 0.987654321)
        self.assertIn("legacy generic", route8["manifest_input_scale_semantics"])
        self.assertEqual(
            [item["scale"] for item in route8["input_tensors_in_manifest_order"]],
            self.manifest["layers"][8]["input_scales"],
        )
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][8]["input_scales"].reverse()
        self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][3]["input_shape_nchw"][0][1] += 1
        self.assert_contract_rejected(manifest=manifest)

    def test_missing_cpu_layer_goldens_are_explicit_and_block_g4(self) -> None:
        contract = self.build()
        readiness = contract["golden_readiness"]
        self.assertEqual(readiness["fixed_input_sample_count"], 109)
        self.assertTrue(readiness["input_hashes_present"])
        self.assertEqual(readiness["cpu_per_layer_integer_tensor_goldens"], "MISSING")
        self.assertEqual(readiness["bytewise_full_network_run_for_109_samples"], "NOT_RUN")
        self.assertTrue(readiness["g4_blocker"])

    def test_changed_row_count_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"].pop()
        self.assert_contract_rejected(manifest=manifest)

    def test_changed_row_order_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][0], manifest["layers"][1] = manifest["layers"][1], manifest["layers"][0]
        self.assert_contract_rejected(manifest=manifest)

    def test_changed_cfg_section_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][12]["cfg_section"] += 1
        self.assert_contract_rejected(manifest=manifest)

    def test_changed_operator_manifest_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["operators"].remove("upsample")
        self.assert_contract_rejected(manifest=manifest)

    def test_dangling_forward_and_cast_external_references_are_rejected(self) -> None:
        for bad_ref in (37, "not_a_tensor"):
            manifest = copy.deepcopy(self.manifest)
            manifest["layers"][5]["input_tensor_indices"] = [bad_ref]
            self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][0]["input_tensor_indices"] = [0]
        self.assert_contract_rejected(manifest=manifest)

    def test_tensor_length_address_overlap_and_yolo_alias_mutations_are_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][4]["tensor_length_bytes"] += 1
        self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][4]["tensor_address"] = manifest["layers"][3]["tensor_address"]
        self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["layers"][30]["tensor_address"] += 64
        self.assert_contract_rejected(manifest=manifest)

    def test_g0_timeout_completion_priority_and_abort_invariants_fail_closed(self) -> None:
        for field in ("timeout", "priority"):
            manifest = copy.deepcopy(self.manifest)
            if field == "timeout":
                manifest["control_protocol"][field] = "timeout restarts for every layer"
            else:
                manifest["control_protocol"][field] = list(reversed(manifest["control_protocol"][field]))
            self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["control_protocol"]["operator_completion_event"]["handshake"] = "backpressured multi-cycle response"
        self.assert_contract_rejected(manifest=manifest)
        manifest = copy.deepcopy(self.manifest)
        manifest["memory_protocol"]["reset_abort"] = "pending writes may complete later"
        self.assert_contract_rejected(manifest=manifest)

    def test_required_source_bindings_cannot_be_removed_or_rehashed(self) -> None:
        records = copy.deepcopy(self.source_bindings)
        records = [record for record in records if record["path"] != contract_module.T16_PROOF_PATH]
        self.assert_contract_rejected(source_bindings=records)
        records = copy.deepcopy(self.source_bindings)
        next(record for record in records if record["path"] == contract_module.MANIFEST_PATH)["sha256"] = "0" * 64
        self.assert_contract_rejected(source_bindings=records)

    def test_t16_proof_channel_set_must_match_all_convolutions(self) -> None:
        proof = copy.deepcopy(self.t16_proof)
        proof["layers"].pop()
        self.assert_contract_rejected(t16_proof=proof)


if __name__ == "__main__":
    unittest.main(verbosity=2)
