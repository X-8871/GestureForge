from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import sys
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(r"D:\FPGA_Competition")
sys.path.insert(0, str(REPO_ROOT))

from verification import s2a_network_descriptor_rom as rom


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_temp_on_task_drive() -> None:
    expected_root = REPO_ROOT / "report" / "evidence" / "S2A-T63"
    for name in ("TEMP", "TMP", "TMPDIR"):
        value = os.environ.get(name)
        if not value:
            raise AssertionError(f"{name} 未设置为任务临时目录")
        resolved = Path(value).resolve()
        if resolved != expected_root.resolve():
            raise AssertionError(f"{name} 不在任务指定 D 盘目录")


class NetworkDescriptorRomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _assert_temp_on_task_drive()
        cls.frozen = rom.load_frozen_inputs(REPO_ROOT, verify_upstream=True)
        cls.data = rom.build_rom_data(
            cls.frozen["manifest"],
            cls.frozen["contract"],
            cls.frozen["table"],
            cls.frozen["hashes"],
        )
        cls.package = rom.render_sv_package(cls.data)

    def test_render_is_deterministic(self) -> None:
        second_data = rom.build_rom_data(
            self.frozen["manifest"],
            self.frozen["contract"],
            self.frozen["table"],
            self.frozen["hashes"],
        )
        self.assertEqual(self.package, rom.render_sv_package(second_data))
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            hashlib.sha256(rom.render_sv_package(second_data)).hexdigest(),
        )

    def test_all_layers_match_manifest_and_t22_in_dispatch_order(self) -> None:
        manifest_layers = self.frozen["manifest"]["layers"]
        t22_layers = self.frozen["contract"]["network_dispatch"]["layers"]
        self.assertEqual(len(self.data["layers"]), 38)
        self.assertEqual(self.data["operator_counts"], rom.OP_COUNTS)
        for index, descriptor in enumerate(self.data["layers"]):
            manifest_row = manifest_layers[index]
            contract_row = t22_layers[index]
            self.assertEqual(descriptor["layer_index"], index)
            self.assertEqual(descriptor["cfg_section"], index + 1)
            self.assertEqual(descriptor["op"], manifest_row["op"])
            self.assertEqual(descriptor["op"], contract_row["op"])
            self.assertEqual(len(descriptor["inputs"]), len(manifest_row["input_tensor_indices"]))
            for position, input_descriptor in enumerate(descriptor["inputs"]):
                contract_input = contract_row["input_tensors_in_manifest_order"][position]
                self.assertEqual(input_descriptor["address"], contract_input["address"])
                self.assertEqual(input_descriptor["length_bytes"], contract_input["length_bytes"])
                self.assertEqual(input_descriptor["shape_nchw"], contract_input["shape_nchw"])
            self.assertEqual(descriptor["output"]["address"], manifest_row["tensor_address"])
            self.assertEqual(descriptor["output"]["length_bytes"], manifest_row["tensor_length_bytes"])
            self.assertEqual(descriptor["output"]["shape_nchw"], manifest_row["output_shape_nchw"])

    def test_every_t23_channel_is_flattened_in_order_and_digest_bound(self) -> None:
        table_layers = self.frozen["table"]["layers"]
        self.assertEqual(len(self.data["channels"]), rom.TOTAL_MQ_CHANNELS)
        cursor = 0
        for table_row in table_layers:
            descriptor = self.data["layers"][table_row["layer_index"]]
            self.assertEqual(descriptor["mq_base"], cursor)
            self.assertEqual(descriptor["mq_count"], table_row["channel_count"])
            channels = table_row["channels"]
            self.assertEqual(
                rom._canonical_channel_digest(channels),
                table_row["candidate_parameter_sha256"],
            )
            for channel_index, t23_channel in enumerate(channels):
                flat = self.data["channels"][cursor + channel_index]
                self.assertEqual(flat["layer_index"], table_row["layer_index"])
                self.assertEqual(flat["channel"], channel_index)
                self.assertEqual(flat["positive_M"], t23_channel["positive_M"])
                self.assertEqual(flat["positive_Q"], t23_channel["positive_Q"])
                self.assertEqual(flat["negative_M"], t23_channel["negative_M"])
                self.assertEqual(flat["negative_Q"], t23_channel["negative_Q"])
                self.assertLessEqual(flat["positive_M"], 0xFFFFFFFF)
                self.assertLessEqual(flat["negative_M"], 0xFFFFFFFF)
                self.assertLessEqual(flat["positive_Q"], 65)
                self.assertLessEqual(flat["negative_Q"], 65)
            cursor += len(channels)
        self.assertEqual(cursor, 3164)

    def test_yolo_rows_are_zero_write_aliases_of_their_source_tensors(self) -> None:
        aliases = {30: 29, 37: 36}
        for layer_index, source_index in aliases.items():
            descriptor = self.data["layers"][layer_index]
            manifest_row = self.frozen["manifest"]["layers"][layer_index]
            source = self.data["layers"][source_index]["output"]
            output = descriptor["output"]
            self.assertEqual(manifest_row["output_tensor_index"], source_index)
            self.assertEqual(output["tensor_index"], source_index)
            self.assertEqual(output["alias_of_layer_index"], source_index)
            self.assertFalse(output["memory_write_required"])
            self.assertEqual(output["address"], source["address"])
            self.assertEqual(output["length_bytes"], source["length_bytes"])
            self.assertEqual(output["shape_nchw"], source["shape_nchw"])
            self.assertEqual(output["scale_bits"], source["scale_bits"])
            self.assertEqual(descriptor["inputs"][0]["source_index"], source_index)

    def test_tensor_geometry_and_packed_fields_fit_declared_widths(self) -> None:
        for descriptor in self.data["layers"]:
            for tensor in [*descriptor["inputs"], descriptor["output"]]:
                self.assertGreater(tensor["address"], -1)
                self.assertLessEqual(tensor["address"], 0xFFFFFFFF)
                self.assertGreater(tensor["length_bytes"], 0)
                self.assertLessEqual(tensor["length_bytes"], 0xFFFFFFFF)
                self.assertEqual(tensor["length_bytes"], math.prod(tensor["shape_nchw"]))
                self.assertTrue(0 <= tensor["scale_bits"] <= 0xFFFFFFFFFFFFFFFF)
                self.assertTrue(all(0 < extent <= 0xFFFF for extent in tensor["shape_nchw"]))
            if descriptor["op"] == "route":
                self.assertEqual(
                    len(descriptor["parameters"]["route_source_channel_ranges"]),
                    len(descriptor["inputs"]),
                )
                for input_descriptor, channel_range in zip(
                    descriptor["inputs"], descriptor["parameters"]["route_source_channel_ranges"]
                ):
                    self.assertTrue(0 <= channel_range[0] < channel_range[1] <= input_descriptor["shape_nchw"][1])
            if descriptor["op"] == "convolutional":
                offsets = descriptor["parameters"]["gf8_parameter_offsets"]
                self.assertEqual(descriptor["mq_count"], descriptor["output"]["shape_nchw"][1])
                self.assertLessEqual(offsets["quantized_weight_offset"] + offsets["quantized_weight_bytes"], self.data["weight_package"]["length_bytes"])
                self.assertLessEqual(offsets["weight_scale_offset"] + descriptor["mq_count"] * 4, self.data["weight_package"]["length_bytes"])
                self.assertLessEqual(offsets["fused_bias_offset"] + descriptor["mq_count"] * 4, self.data["weight_package"]["length_bytes"])

    def test_global_dispatch_deadline_and_existing_control_boundary_are_encoded(self) -> None:
        self.assertTrue(self.data["serial_dispatch"])
        self.assertTrue(self.data["global_timeout_one_deadline"])
        self.assertFalse(self.data["per_layer_timeout_restart"])
        self.assertFalse(self.data["ps_visible_csr_changed"])
        self.assertEqual(self.data["memory_outstanding_limit"], 1)
        self.assertIn("S2A_TIMEOUT_SCOPE_GLOBAL = 1'b1", self.package.decode("utf-8"))
        self.assertIn("S2A_PS_VISIBLE_CSR_CHANGED = 1'b0", self.package.decode("utf-8"))
        self.assertIn("S2A_T23_MQ_ROM", self.package.decode("utf-8"))
        self.assertIn("S2A_CONV_BIAS_ACCUMULATOR_INT32", self.package.decode("utf-8"))

    def test_tampered_input_reference_or_address_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.frozen["manifest"])
        manifest["layers"][0]["tensor_address"] += 64
        with self.assertRaises(rom.DescriptorRomError):
            rom.build_rom_data(manifest, self.frozen["contract"], self.frozen["table"], self.frozen["hashes"])

        contract = copy.deepcopy(self.frozen["contract"])
        contract["network_dispatch"]["layers"][34]["input_tensors_in_manifest_order"][1]["source_index"] = 22
        with self.assertRaises(rom.DescriptorRomError):
            rom.build_rom_data(self.frozen["manifest"], contract, self.frozen["table"], self.frozen["hashes"])

    def test_tampered_candidate_channel_or_input_hash_is_rejected(self) -> None:
        table = copy.deepcopy(self.frozen["table"])
        table["layers"][0]["channels"][0]["positive_M"] += 1
        with self.assertRaises(rom.DescriptorRomError):
            rom.build_rom_data(self.frozen["manifest"], self.frozen["contract"], table, self.frozen["hashes"])

        bad_hashes = dict(self.frozen["hashes"])
        bad_hashes[rom.T23_PATH] = "0" * 64
        with self.assertRaises(rom.DescriptorRomError):
            rom.build_rom_data(self.frozen["manifest"], self.frozen["contract"], self.frozen["table"], bad_hashes)

    def test_package_contains_only_read_only_package_constants(self) -> None:
        text = self.package.decode("utf-8")
        self.assertTrue(text.startswith("// S2A-T63"))
        self.assertIn("package s2a_network_descriptor_pkg;", text)
        self.assertIn("endpackage", text)
        self.assertNotIn("module ", text)
        self.assertNotIn("csr_valid", text)
        self.assertIn("S2A_CONV_FUSED_BIAS_FLOAT32_BITS", text)
        self.assertIn("S2A_CONV_WEIGHT_SCALE_BITS", text)


def _test_summary(result: unittest.result.TestResult) -> bytes:
    root = REPO_ROOT.resolve()
    package_path = root.joinpath(*rom.PACKAGE_PATH.split("/"))
    binding_path = root.joinpath(*rom.BINDING_REPORT_PATH.split("/"))
    generator_path = root / "verification" / "s2a_network_descriptor_rom.py"
    test_path = root / "verification" / "test_s2a_network_descriptor_rom.py"
    failures = [test.id() for test, _ in result.failures]
    errors = [test.id() for test, _ in result.errors]
    report = {
        "schema_version": "gestureforge_s2a_network_descriptor_rom_test_v1",
        "task_id": "S2A-T63",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": failures,
        "errors": errors,
        "test_source_sha256": _sha256(test_path),
        "generator_source_sha256": _sha256(generator_path),
        "generated_package_sha256": _sha256(package_path) if package_path.is_file() else None,
        "binding_report_sha256": _sha256(binding_path) if binding_path.is_file() else None,
        "execution_scope": "static Python tests; Vivado and XSim were not run",
    }
    return (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _write_test_summary(result: unittest.result.TestResult) -> None:
    path = REPO_ROOT / "report" / "evidence" / "S2A-T63" / "descriptor_rom_test_summary.json"
    if not path.parent.is_dir():
        raise OSError(f"测试摘要父目录不存在: {path.parent}")
    encoded = _test_summary(result)
    if path.exists():
        if path.read_bytes() != encoded:
            raise OSError(f"拒绝覆盖与本次结果不同的测试摘要: {path}")
        return
    with path.open("xb") as handle:
        handle.write(encoded)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(NetworkDescriptorRomTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    try:
        _write_test_summary(outcome)
    except OSError as exc:
        print(f"无法写入 T63 测试摘要: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
