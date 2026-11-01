from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
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
        self.assertIn("$ErrorActionPreference = 'Continue'", runner)
        self.assertIn("Out-File -LiteralPath $ConsoleLogPath -Encoding utf8 -NoClobber -ErrorAction Stop", runner)
        self.assertIn("[System.IO.FileMode]::CreateNew", runner)
        self.assertIn("Get-T63ProtectedProcessAllowlist", runner)
        self.assertIn("Assert-T63XilinxProcessSnapshot", runner)
        self.assertIn("Invoke-T63GuardedStage", runner)
        self.assertIn("-Phase 'immediately_before_xelab'", runner)
        self.assertIn("'vivado_lab.exe'", runner)
        self.assertIn("'xvhdl.exe'", runner)
        self.assertIn("$freeRamMb -lt 2048 -or $freeDiskMb -lt 2048", runner)
        self.assertIn("minimum_free_ram_mb = 2048", runner)
        self.assertIn("minimum_free_d_drive_mb = 2048", runner)
        self.assertIn("immediately_before_xsim", runner)
        self.assertIn("$env:XILINX_VIVADO = 'D:\\Xilinx\\2026.1\\Vivado'", runner)
        self.assertIn("$env:TEMP = $tempRoot", runner)
        self.assertIn("$env:TMP = $tempRoot", runner)
        self.assertIn("$env:TMPDIR = $tempRoot", runner)
        self.assertIn("$env:XILINX_LOCAL_USER_DATA = $userDataRoot", runner)
        self.assertIn("process_snapshots = @($processSnapshots)", runner)
        self.assertIn("resource_snapshots = @($resourceSnapshots)", runner)
        self.assertIn("execution = @($executionLog)", runner)
        self.assertNotIn("$activeTools = Get-CimInstance", runner)
        self.assertNotIn("New-Item -Force", runner)
        self.assertNotIn("Set-Content -LiteralPath", runner)

    def test_runner_splits_console_and_native_logs_and_binds_each_stage(self) -> None:
        binding_path = verifier.RUN_DIR / verifier.MANIFEST_NAME
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
        contract = binding.get("native_log_contract", {})
        self.assertEqual(
            contract,
            {
                "schema_version": "s2a_t63_stage_log_binding_v1",
                "native_log_precreated": False,
                "record_fields": [
                    "exit_code",
                    "console_log.path",
                    "console_log.sha256",
                    "native_log.path",
                    "native_log.sha256",
                ],
                "simulation_stages": {
                    "xvlog": {
                        "console_log": "xvlog.console.log",
                        "native_log": "xvlog.log",
                        "stage_result": "stage_xvlog_result.json",
                    },
                    "xelab": {
                        "console_log": "xelab.console.log",
                        "native_log": "xelab.log",
                        "stage_result": "stage_xelab_result.json",
                    },
                    "xsim": {
                        "console_log": "xsim.console.log",
                        "native_log": "xsim.log",
                        "stage_result": "stage_xsim_result.json",
                    },
                },
            },
        )
        runner = (verifier.RUN_DIR / verifier.RUNNER_NAME).read_text(encoding="utf-8-sig")
        self.assertIn("console_log = $consoleBinding", runner)
        self.assertIn("native_log = $nativeBinding", runner)
        self.assertIn("stage_result_path = $stageResultPath", runner)
        self.assertIn("Write-NewUtf8Text -Path $stageResultPath", runner)
        self.assertIn('("stage_" + $StageName + "_result.json")', runner)
        self.assertIn("Assert-NewOutputPath -Path $NativeLogPath -AllowedRoot $workRoot", runner)
        self.assertIn("控制台捕获与工具原生日志必须使用不同路径", runner)
        self.assertNotIn("Out-File -LiteralPath $NativeLogPath", runner)
        for stage, paths in contract["simulation_stages"].items():
            self.assertIn(f"-StageName '{stage}'", runner)
            self.assertIn(f"'{paths['console_log']}'", runner)
            self.assertIn(f"'{paths['native_log']}'", runner)
            self.assertEqual(paths["stage_result"], f"stage_{stage}_result.json")
        self.assertIn("$xsimLogPath = Join-Path $workRoot 'xsim.log'", runner)

    def test_process_guard_hash_and_ps51_ps7_positive_negative_cases(self) -> None:
        binding_path = verifier.RUN_DIR / verifier.MANIFEST_NAME
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
        entry = binding.get("process_guard_test", {})
        helper_path = verifier.RUN_DIR / "test_s2a_t63_process_guard.ps1"
        self.assertEqual(
            entry,
            {
                "path": f"{verifier.RUN_REL}/test_s2a_t63_process_guard.ps1",
                "sha256": hashlib.sha256(helper_path.read_bytes()).hexdigest(),
            },
        )
        baseline = binding.get("process_guard_baseline", {})
        self.assertEqual(
            baseline.get("source"),
            "Win32_Process.CreationDate -> DateTime.ToUniversalTime().ToString(o, InvariantCulture)",
        )
        self.assertRegex(baseline.get("captured_at_utc8", ""), r"^2026-10-01 .+ \+08:00$")
        self.assertEqual(
            [
                (
                    item["process_id"],
                    item["parent_process_id"],
                    item["name"],
                    item["executable_path"],
                    item["command_line"],
                    item["creation_date_utc"],
                )
                for item in baseline.get("identities", [])
            ],
            [
                (
                    8712,
                    10724,
                    "vivado.exe",
                    r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe",
                    r'"D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe"   -mode tcl -source D:\FPGA_Competition\report\evidence\S2A-T60\run06\mcp_server_instance\start_mcp.tcl',
                    "2026-09-29T18:07:06.1577890Z",
                ),
                (
                    22488,
                    8712,
                    "xsimk.exe",
                    r"D:\FPGA_Competition\report\evidence\S2A-T60\run06\isolated_project\s2a_t60_run06.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row24_all_channels_behav\xsimk.exe",
                    "xsim.dir/tb_s2a_conv_layer35_row24_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row24_all_channels_behav.wdb -simrunnum 0 -socket 8295",
                    "2026-09-29T18:13:11.5972630Z",
                ),
                (
                    13156,
                    8712,
                    "xsimk.exe",
                    r"D:\FPGA_Competition\report\evidence\S2A-T61\run04\isolated_project\s2a_t61_run04.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row25_all_channels_behav\xsimk.exe",
                    "xsim.dir/tb_s2a_conv_layer35_row25_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row25_all_channels_behav.wdb -simrunnum 0 -socket 12375",
                    "2026-09-29T19:39:52.1132030Z",
                ),
            ],
        )
        runner_path = verifier.RUN_DIR / verifier.RUNNER_NAME
        for executable in ("powershell.exe", "pwsh.exe"):
            resolved = shutil.which(executable)
            self.assertIsNotNone(resolved, f"缺少要求的 PowerShell：{executable}")
            result = subprocess.run(
                [
                    str(resolved),
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(helper_path),
                    "-RunnerPath",
                    str(runner_path),
                    "-BindingPath",
                    str(binding_path),
                ],
                cwd=str(verifier.RUN_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
                check=False,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"{executable} guard 测试失败：stdout={result.stdout[-1500:]!r} stderr={result.stderr[-1500:]!r}",
            )
            match = re.search(
                r"PASS process_guard_tests=(\d+) native_log_binding_tests=(\d+)",
                result.stdout,
            )
            self.assertIsNotNone(match)
            self.assertEqual(int(match.group(1)), 14)
            self.assertEqual(int(match.group(2)), 4)

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
