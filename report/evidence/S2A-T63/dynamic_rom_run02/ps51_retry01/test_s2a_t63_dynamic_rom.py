from __future__ import annotations

import ast
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_s2a_t63_dynamic_rom as verifier


class DynamicRomFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest, cls.contract, cls.table, cls.input_hashes = verifier._check_root_and_sources()
        cls.layer_records, cls.channel_records, cls.operator_counts = verifier._build_expected(
            cls.manifest, cls.contract, cls.table
        )

    def test_freeze_hashes_and_upstream_counts(self) -> None:
        self.assertEqual(len(self.input_hashes), 4)
        self.assertEqual(len(self.layer_records), 38)
        self.assertEqual(len(self.channel_records), 3164)
        self.assertEqual(
            self.operator_counts,
            {"convolutional": 21, "maxpool": 3, "route": 11, "upsample": 1, "yolo": 2},
        )

    def test_rom_fields_are_fully_bound_to_the_hdl_testbench(self) -> None:
        scope = verifier._check_hdl_scope()
        self.assertEqual(scope["layer_fields_per_record"], 104)
        self.assertEqual(scope["layer_record_bits"], 2605)
        self.assertEqual(scope["channel_fields_per_record"], 6)
        self.assertEqual(scope["channel_record_bits"], 230)
        self.assertGreaterEqual(scope["package_array_count"], 1)

    def test_independent_fixture_values_match_every_package_array(self) -> None:
        result = verifier.cross_check_package_literals(self.layer_records, self.channel_records)
        self.assertEqual(result["array_count"], 84)
        self.assertGreater(result["array_element_count"], 4000)

    def test_yolo_aliases_have_the_frozen_sources(self) -> None:
        layers = self.manifest["layers"]
        self.assertEqual(layers[30]["input_tensor_indices"], [29])
        self.assertEqual(layers[37]["input_tensor_indices"], [36])
        self.assertEqual(layers[30]["mask"], [3, 4, 5])
        self.assertEqual(layers[37]["mask"], [1, 2, 3])
        self.assertEqual(layers[30]["anchors_wh"], verifier.EXPECTED_ANCHORS)
        self.assertEqual(layers[37]["anchors_wh"], verifier.EXPECTED_ANCHORS)

    def test_memory_fixture_encoding_is_fixed_width_and_mutation_sensitive(self) -> None:
        layer_bytes = verifier._hex_lines(self.layer_records, verifier.LAYER_MEMORY_BITS)
        channel_bytes = verifier._hex_lines(self.channel_records, verifier.CHANNEL_MEMORY_BITS)
        self.assertEqual(len(layer_bytes.splitlines()), 38)
        self.assertEqual(len(channel_bytes.splitlines()), 3164)
        self.assertTrue(all(len(line) == verifier.LAYER_MEMORY_BITS // 4 for line in layer_bytes.splitlines()))
        self.assertTrue(all(len(line) == verifier.CHANNEL_MEMORY_BITS // 4 for line in channel_bytes.splitlines()))
        self.assertTrue(all(record >> verifier.LAYER_RECORD_BITS == 0 for record in self.layer_records))
        self.assertTrue(all(record >> verifier.CHANNEL_RECORD_BITS == 0 for record in self.channel_records))
        self.assertEqual(
            verifier._hex_lines([1 << (verifier.LAYER_RECORD_BITS - 1)], verifier.LAYER_MEMORY_BITS),
            ("1" + "0" * (verifier.LAYER_MEMORY_BITS // 4 - 1) + "\n").encode("ascii"),
        )
        self.assertEqual(
            verifier._hex_lines([1 << (verifier.CHANNEL_RECORD_BITS - 1)], verifier.CHANNEL_MEMORY_BITS),
            ("2" + "0" * (verifier.CHANNEL_MEMORY_BITS // 4 - 1) + "\n").encode("ascii"),
        )
        self.assertEqual(int(layer_bytes.splitlines()[0], 16), self.layer_records[0])
        self.assertEqual(int(channel_bytes.splitlines()[0], 16), self.channel_records[0])
        mutated = bytearray(channel_bytes)
        mutated[0] = ord("F") if mutated[0] != ord("F") else ord("E")
        with self.assertRaises(verifier.DynamicRomError):
            verifier.check_fixture_bytes(
                bytes(mutated),
                verifier._hex_lines(self.channel_records, verifier.CHANNEL_MEMORY_BITS),
                "mutated channel fixture",
            )

    def test_output_create_new_refuses_overwrite_and_prefix_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t63_new_output_", dir=verifier.RUN_DIR) as temporary:
            allowed_root = Path(temporary)
            target = allowed_root / "fixture.bin"
            verifier._write_new_bytes(target, b"first", allowed_root)
            with self.assertRaises(verifier.DynamicRomError):
                verifier._write_new_bytes(target, b"second", allowed_root)
            self.assertEqual(target.read_bytes(), b"first")
            sibling_target = allowed_root.parent / (allowed_root.name + "_sibling") / "fixture.bin"
            with self.assertRaises(verifier.DynamicRomError):
                verifier._write_new_bytes(sibling_target, b"outside", allowed_root)

    def test_runner_has_fail_closed_path_and_log_guards(self) -> None:
        runner = (verifier.RUN_DIR / verifier.RUNNER_NAME).read_text(encoding="utf-8-sig")
        self.assertIn("GetFullPath", runner)
        self.assertIn("Assert-PathWithin", runner)
        self.assertIn("Assert-NoReparsePathChain", runner)
        self.assertIn("[System.IO.FileAttributes]::ReparsePoint", runner)
        self.assertIn("New-IsolatedDirectory", runner)
        self.assertIn("Out-File -LiteralPath $LogPath -Encoding utf8 -NoClobber", runner)
        self.assertIn("[System.IO.FileMode]::CreateNew", runner)
        self.assertNotIn("New-Item -Force", runner)
        self.assertNotIn("Set-Content -LiteralPath", runner)

    def test_python_sources_parse_without_generating_bytecode(self) -> None:
        for name in (verifier.VERIFIER_NAME, verifier.TEST_NAME):
            source = (verifier.RUN_DIR / name).read_text(encoding="utf-8")
            ast.parse(source, filename=name)

    def test_prepared_files_match_frozen_json_reconstruction(self) -> None:
        result = verifier.validate()
        self.assertEqual(result["status"], "OFFLINE_FIXTURE_VALID")
        self.assertFalse(result["vivado_run"])
        self.assertFalse(result["xvlog_run"])
        self.assertFalse(result["xelab_run"])
        self.assertFalse(result["xsim_run"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
