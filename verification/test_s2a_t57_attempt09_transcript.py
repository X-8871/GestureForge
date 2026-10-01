#!/usr/bin/env python3
"""验证 T57 attempt09 的 console transcript 截取和 CRLF 解析。"""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py"
SPEC = importlib.util.spec_from_file_location("s2a_t57_attempt09_runner", RUNNER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("无法加载 T57 attempt09 runner")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

ACTUAL_PASS_LINE = (
    "PASS T57 outputs=6656 raw=6656 feature_reads=22413312 weight_reads=22413312 "
    "output_writes=6656 padding=589824 taps=23003136 feature_lanes=15 weight_lanes=15 "
    "output_lanes=15 error_mask=70 fault_responses=3 abort_cancel=2 reset_cancel=1 "
    "recovery=1 request_stalls=116566517 feature_transfers=22413312 "
    "feature_stall_cycles=58274607 feature_slot0=4482663 feature_slot1=4482663 "
    "feature_slot2=4482662 feature_slot3=4482662 feature_slot4=4482662 "
    "weight_transfers=22413312 weight_stall_cycles=58274607 weight_slot0=4482663 "
    "weight_slot1=4482663 weight_slot2=4482662 weight_slot3=4482662 weight_slot4=4482662 "
    "output_transfers=6656 output_stall_cycles=17303 output_slot0=1332 output_slot1=1331 "
    "output_slot2=1331 output_slot3=1331 output_slot4=1331"
)


class T57Attempt09TranscriptTests(unittest.TestCase):
    def _console(self) -> bytes:
        lines = [
            "INFO: Vivado 回显 report/evidence/S2A-T57/run_project_sim.tcl",
            "# 此处是无关 Tcl 源码，包含 wdb 与 log_wave 字样",
            "set note {wdb is disabled by the project configuration}",
            'puts "T57_CUSTOM_TCL_SENTINEL=run09_attempt09"',
            "INFO: start xsim custom Tcl",
            "T57_CUSTOM_TCL_SENTINEL=run09_attempt09",
        ]
        lines.extend(f"PROGRESS T57 outputs={count}/6656" for count in range(26, 6657, 26))
        lines.extend((
            ACTUAL_PASS_LINE,
            "$finish called at time : 2971541060 ns",
            "INFO: Vivado may continue with unrelated Tcl cleanup",
        ))
        return ("\r\n".join(lines) + "\r\n").encode("utf-8")

    def test_extracts_crlf_transcript_and_ignores_echoed_wdb_source(self) -> None:
        console = self._console()
        self.assertIn(b"wdb", console)
        segment, facts = RUNNER._extract_xsim_transcript(console)
        self.assertNotIn(b"wdb", segment)
        self.assertIn(b"\r\n", segment)
        self.assertTrue(segment.startswith(b"T57_CUSTOM_TCL_SENTINEL=run09_attempt09\r\n"))
        self.assertTrue(segment.endswith(b"$finish called at time : 2971541060 ns\r\n"))
        self.assertEqual(facts["progress_checkpoint_count"], 256)
        self.assertEqual(facts["finish_time_ns"], 2_971_541_060)
        pass_line, values, progress, finish = RUNNER._verify_xsim_transcript_text(
            segment.decode("utf-8"))
        self.assertEqual(pass_line, ACTUAL_PASS_LINE)
        self.assertEqual(values["outputs"], 6656)
        self.assertEqual(values["raw"], 6656)
        self.assertNotIn("int8", values)
        self.assertEqual(len(progress), 256)
        self.assertEqual(finish, 2_971_541_060)
        self.assertTrue(pass_line.startswith("PASS T57 outputs=6656"))

    def test_rejects_duplicate_sentinel_and_missing_finish(self) -> None:
        console = self._console()
        duplicate = console.replace(
            b"T57_CUSTOM_TCL_SENTINEL=run09_attempt09\r\n",
            b"T57_CUSTOM_TCL_SENTINEL=run09_attempt09\r\nT57_CUSTOM_TCL_SENTINEL=run09_attempt09\r\n",
            1)
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._extract_xsim_transcript(duplicate)
        missing_finish = console.replace(b"$finish called at time : 2971541060 ns\r\n", b"")
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._extract_xsim_transcript(missing_finish)

    def test_rejects_error_inside_xsim_transcript(self) -> None:
        console = self._console().replace(
            b"PROGRESS T57 outputs=26/6656\r\n",
            b"ERROR: injected transcript error\r\nPROGRESS T57 outputs=26/6656\r\n",
            1)
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._extract_xsim_transcript(console)

    def _recoverable_failure(self) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        failure = (
            "XSim transcript 提取失败：Python transcript extractor 返回非零：1；"
            "FAIL T57 T57Error: XSim transcript PASS 字段解析失败; "
            "缺少运行证据：xsim_simulate_transcript.log; "
            "Vivado/XSim transcript 不完整：custom= pass= progress= finish= errors="
        )
        extraction_failure = (
            "Python transcript extractor 返回非零：1；"
            "FAIL T57 T57Error: XSim transcript PASS 字段解析失败"
        )
        stage: dict[str, object] = {
            "status": "SIMULATION_FLOW_FAIL",
            "compile_exit_code": 0,
            "elaboration_exit_code": 0,
            "vivado_process_exit_code": 0,
            "simulate_step_tcl_code": None,
            "xsim_exit_code": None,
            "xsim_exit_code_captured": False,
            "wdb_generated": False,
            "failure": failure,
            "simulate_log_extraction_failure": extraction_failure,
            "wrapper_finalization": {
                "original_status": "SIMULATION_FLOW_RUNNING",
                "terminal_status": "SIMULATION_FLOW_FAIL",
                "transcript_extraction_exit_code": 1,
                "transcript_extraction_failure": extraction_failure,
            },
        }
        process: dict[str, object] = {
            "failure": failure,
            "cleanup_failure": None,
        }
        run_summary: dict[str, object] = {
            "overall_status": "FAIL",
            "simulation_flow_status": "SIMULATION_FLOW_FAIL",
            "data_verification_status": "NOT_RUN",
            "failure": "Simulation-flow gate 未通过；未执行 data verify-only。",
            "verify_only": {"exit_code": None, "report": None, "log": None},
        }
        return stage, process, run_summary

    def test_accepts_only_the_saved_old_pass_parser_failure_shape(self) -> None:
        RUNNER._validate_recoverable_failure_shape(*self._recoverable_failure())

    def _load_original_failure_snapshots(self):
        record, _ = RUNNER._read_json(RUNNER.RECOVERY_RECORD)
        self.assertEqual(record.get("schema"), "GestureForge-S2A-T57-attempt09-recovery-v1")
        self.assertEqual(record.get("task_id"), "S2A-T57")
        self.assertEqual(record.get("attempt_root"), str(RUNNER.RUN_ROOT.resolve()))
        self.assertEqual(record.get("status"), "RECOVERY_PASS")

        expected = {
            "stage_status.json": (
                RUNNER.STAGE_STATUS, RUNNER.T57_ATTEMPT09_STAGE_FAIL_SHA256),
            "process_status.json": (
                RUNNER.PROCESS_STATUS, RUNNER.T57_ATTEMPT09_PROCESS_FAIL_SHA256),
            "run_summary.json": (
                RUNNER.RUN_SUMMARY, RUNNER.T57_ATTEMPT09_RUN_FAIL_SHA256),
        }
        snapshots = record.get("original_snapshots")
        self.assertIsInstance(snapshots, dict)
        self.assertEqual(set(snapshots), set(expected))

        original_values = {}
        original_bytes = {}
        for name, (path, expected_sha256) in expected.items():
            snapshot = snapshots[name]
            data, parsed = RUNNER._decode_json_snapshot(snapshot, path)
            self.assertEqual(snapshot.get("sha256"), expected_sha256)
            self.assertEqual(RUNNER._sha256(data), expected_sha256)
            self.assertEqual(snapshot.get("bytes"), len(data))
            original_bytes[name] = data
            original_values[name] = parsed

        RUNNER._validate_recoverable_failure_shape(
            original_values["stage_status.json"],
            original_values["process_status.json"],
            original_values["run_summary.json"],
        )
        original_states = record.get("original_states", {})
        self.assertEqual(original_states.get("stage_status"),
                         original_values["stage_status.json"].get("status"))
        self.assertEqual(original_states.get("process_failure"),
                         original_values["process_status.json"].get("failure"))
        self.assertEqual(original_states.get("run_summary"),
                         original_values["run_summary.json"].get("overall_status"))
        self.assertEqual(original_states.get("data_verification"),
                         original_values["run_summary.json"].get(
                             "data_verification_status"))
        return record, original_values, original_bytes

    def _assert_recovery_source_bindings(self, record, preparation) -> None:
        source_bindings = record.get("source_bindings", {})
        prepared_hashes = source_bindings.get("prepared_sha256")
        current_hashes = source_bindings.get("current_sha256")
        current_snapshot = source_bindings.get("current_snapshot")
        expected_paths = set(RUNNER.T57_SOURCE_PATHS)
        self.assertIsInstance(prepared_hashes, dict)
        self.assertIsInstance(current_hashes, dict)
        self.assertIsInstance(current_snapshot, dict)
        self.assertEqual(set(prepared_hashes), expected_paths)
        self.assertEqual(set(current_hashes), expected_paths)
        self.assertEqual(set(current_snapshot), expected_paths)

        prepared_manifest_hashes = preparation.get("bindings", {}).get(
            "T57_source_hashes")
        self.assertIsInstance(prepared_manifest_hashes, dict)
        self.assertEqual(set(prepared_manifest_hashes), expected_paths)
        self.assertEqual(prepared_hashes, prepared_manifest_hashes)

        for relative in RUNNER.T57_SOURCE_PATHS:
            snapshot = current_snapshot[relative]
            expected_path = str((RUNNER.ROOT / relative).resolve())
            self.assertEqual(snapshot.get("path"), expected_path)
            self.assertIs(type(snapshot.get("bytes")), int)
            self.assertGreater(snapshot["bytes"], 0)
            snapshot_sha = snapshot.get("sha256")
            self.assertIsInstance(snapshot_sha, str)
            self.assertEqual(len(snapshot_sha), 64)
            self.assertEqual(snapshot_sha, snapshot_sha.lower())
            self.assertTrue(all(char in "0123456789abcdef" for char in snapshot_sha))
            self.assertEqual(snapshot_sha, current_hashes[relative])

        allowed_delta = sorted((
            *RUNNER.T57_RECOVERY_DELTA_PATHS,
            RUNNER.T57_RECOVERY_CONTROLLER_RELATIVE,
        ))
        actual_delta = sorted(
            relative for relative in RUNNER.T57_SOURCE_PATHS
            if str(prepared_hashes[relative]).lower() !=
            str(current_hashes[relative]).lower()
        )
        self.assertEqual(actual_delta, allowed_delta)
        self.assertEqual(source_bindings.get("delta_paths"), allowed_delta)
        self.assertEqual(source_bindings.get("parser_fix_checkpoint"), {
            "runner_sha256": RUNNER.T57_PARSER_FIX_RUNNER_SHA256,
            "transcript_test_sha256": RUNNER.T57_PARSER_FIX_TEST_SHA256,
            "contract": (
                "PASS 行只要求 outputs/raw；INT8 由 observed 文件长度与 "
                "verify-only golden 比对证明。"
            ),
        })

        validated_hashes = RUNNER._validate_recovery_source_delta(
            prepared_hashes, current_hashes)
        self.assertEqual(validated_hashes, {
            relative: str(current_hashes[relative]).lower()
            for relative in RUNNER.T57_SOURCE_PATHS
        })

    def _load_recovery_source_bindings(self):
        record, _ = RUNNER._read_json(RUNNER.RECOVERY_RECORD)
        preparation, preparation_sha256 = RUNNER._read_json(RUNNER.PREPARE_REPORT)
        self.assertEqual(preparation_sha256, RUNNER.T57_ATTEMPT09_PREPARE_SHA256)
        self.assertEqual(record.get("prepare_summary_sha256"),
                         RUNNER.T57_ATTEMPT09_PREPARE_SHA256)
        self._assert_recovery_source_bindings(record, preparation)
        return record, preparation

    def _assert_current_recovery_contract(
            self, record, original_values, stage, stage_sha, process, process_sha,
            summary, summary_sha, report, report_sha) -> None:
        original_stage = original_values["stage_status.json"]
        original_process = original_values["process_status.json"]
        self.assertEqual(record.get("new_states"), {
            "stage_status": "SIMULATION_FLOW_PASS",
            "process_status": "RECOVERY_PASS",
            "data_verification": "PASS_AFTER_VERIFY_ONLY",
        })

        self.assertEqual(stage.get("status"), "SIMULATION_FLOW_PASS")
        self.assertEqual(stage.get("failure"), None)
        self.assertEqual(stage.get("recovery_previous_failure"),
                         original_stage.get("failure"))
        self.assertTrue(stage.get("simulate_log_complete"))
        self.assertEqual(stage.get("simulate_log_extraction_status"), "PASS")
        self.assertEqual(stage.get("simulate_step_tcl_code"), None)
        self.assertEqual(stage.get("xsim_exit_code"), None)
        self.assertIs(stage.get("xsim_exit_code_captured"), False)
        stage_provenance = stage.get("recovery_provenance", {})
        self.assertEqual(stage_provenance.get("record_path"),
                         str(RUNNER.RECOVERY_RECORD.resolve()))
        self.assertEqual(stage_provenance.get("original_status"), "SIMULATION_FLOW_FAIL")
        self.assertEqual(stage_provenance.get("terminal_status"), "SIMULATION_FLOW_PASS")

        self.assertEqual(process.get("mode"), "recover")
        self.assertEqual(process.get("failure"), None)
        self.assertEqual(process.get("cleanup_failure"), None)
        self.assertEqual(process.get("recovery_previous_failure"),
                         original_process.get("failure"))
        self.assertEqual(process.get("stage_status_sha256"), stage_sha)
        self.assertTrue(process.get("xpr_unchanged"))
        self.assertTrue(process.get("cleanup_verified"))
        self.assertEqual(process.get("unrelated_processes_before"), [])
        self.assertEqual(process.get("unrelated_processes_after"), [])
        process_provenance = process.get("recovery_provenance", {})
        self.assertEqual(process_provenance.get("record_path"),
                         str(RUNNER.RECOVERY_RECORD.resolve()))
        self.assertIs(process_provenance.get("vivado_or_xsim_started_by_recovery"), False)

        self.assertEqual(summary.get("overall_status"), "PASS")
        self.assertEqual(summary.get("simulation_flow_status"), "SIMULATION_FLOW_PASS")
        self.assertEqual(summary.get("data_verification_status"), "PASS")
        self.assertEqual(summary.get("failure"), None)
        self.assertEqual(summary.get("stage_status", {}).get("path"),
                         str(RUNNER.STAGE_STATUS.resolve()))
        self.assertEqual(summary.get("stage_status", {}).get("sha256"), stage_sha)
        self.assertEqual(summary.get("stage_status", {}).get("terminal_status"),
                         "SIMULATION_FLOW_PASS")
        self.assertEqual(summary.get("process_status", {}).get("path"),
                         str(RUNNER.PROCESS_STATUS.resolve()))
        self.assertEqual(summary.get("process_status", {}).get("sha256"), process_sha)
        self.assertEqual(record.get("run_summary_after_recovery", {}).get("path"),
                         str(RUNNER.RUN_SUMMARY.resolve()))
        self.assertEqual(record.get("run_summary_after_recovery", {}).get("sha256"),
                         summary_sha)
        self.assertEqual(summary.get("recovery_record", {}).get("path"),
                         str(RUNNER.RECOVERY_RECORD.resolve()))
        self.assertEqual(summary.get("recovery_record", {}).get("provenance"),
                         "RECOVERED_FROM_EXISTING_ATTEMPT09_CONSOLE")

        verify = summary.get("verify_only", {})
        recorded_verify = record.get("verify_only", {})
        self.assertEqual(verify.get("exit_code"), 0)
        self.assertEqual(verify.get("failure"), None)
        self.assertEqual(recorded_verify.get("exit_code"), 0)
        self.assertEqual(verify.get("report"), recorded_verify.get("report"))
        self.assertEqual(verify.get("log"), recorded_verify.get("log"))
        self.assertEqual(verify.get("log", {}).get("path"),
                         str(RUNNER.VERIFY_ONLY_LOG.resolve()))
        self.assertEqual(RUNNER._sha_file(RUNNER.VERIFY_ONLY_LOG),
                         verify.get("log", {}).get("sha256"))

        report_binding = verify.get("report", {})
        self.assertEqual(report_binding.get("path"), str(RUNNER.FINAL_REPORT.resolve()))
        self.assertEqual(report_binding.get("sha256"), report_sha)
        self.assertEqual(report_binding.get("bytes"), RUNNER.FINAL_REPORT.stat().st_size)
        self.assertEqual(report_binding.get("raw_int32_compares"), RUNNER.RAW_COUNT)
        self.assertEqual(report_binding.get("int8_compares"), RUNNER.INT8_COUNT)
        self.assertEqual(report_binding.get("raw_mismatch_bytes"), 0)
        self.assertEqual(report_binding.get("int8_mismatch_bytes"), 0)
        self.assertEqual(report.get("status"), "PASS_SIMULATION_DATA_ONLY")
        self.assertEqual(report.get("acceptance_status"), "NOT_REVIEWED")
        self.assertEqual(report.get("scope"),
                         "tiny416 cfg section36 layer35; all 256 output channels at y=21, "
                         "x=0..25; not full layer or network")
        simulation = report.get("simulation", {})
        self.assertEqual(simulation.get("raw_int32_compares"), RUNNER.RAW_COUNT)
        self.assertEqual(simulation.get("int8_compares"), RUNNER.INT8_COUNT)
        self.assertEqual(simulation.get("raw_mismatch_bytes"), 0)
        self.assertEqual(simulation.get("int8_mismatch_bytes"), 0)
        self.assertIs(simulation.get("raw_byte_identical_to_independent_golden"), True)
        self.assertIs(simulation.get("int8_byte_identical_to_independent_golden"), True)

    def _read_current_recovery_evidence(self):
        stage, stage_sha = RUNNER._read_json(RUNNER.STAGE_STATUS)
        process, process_sha = RUNNER._read_json(RUNNER.PROCESS_STATUS)
        summary, summary_sha = RUNNER._read_json(RUNNER.RUN_SUMMARY)
        report, report_sha = RUNNER._read_json(RUNNER.FINAL_REPORT)
        return stage, stage_sha, process, process_sha, summary, summary_sha, report, report_sha

    def test_accepts_original_failure_snapshots_from_recovery_record(self) -> None:
        self._load_original_failure_snapshots()

    def test_rejects_original_snapshot_sha_drift(self) -> None:
        record, _, _ = self._load_original_failure_snapshots()
        snapshot = dict(record["original_snapshots"]["stage_status.json"])
        snapshot["sha256"] = "0" * 64
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._decode_json_snapshot(snapshot, RUNNER.STAGE_STATUS)

        corrupted = dict(record["original_snapshots"]["stage_status.json"])
        encoded = corrupted["base64"]
        corrupted["base64"] = ("A" if encoded[0] != "A" else "B") + encoded[1:]
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._decode_json_snapshot(corrupted, RUNNER.STAGE_STATUS)

    def test_binds_recovery_to_current_pass_and_verify_only_evidence(self) -> None:
        record, original_values, _ = self._load_original_failure_snapshots()
        current = self._read_current_recovery_evidence()
        self._assert_current_recovery_contract(record, original_values, *current)

    def test_binds_recovery_source_maps_to_fixed_prepare_manifest(self) -> None:
        self._load_recovery_source_bindings()

    def test_rejects_missing_or_altered_current_source_binding(self) -> None:
        record, preparation = self._load_recovery_source_bindings()
        missing = copy.deepcopy(record)
        del missing["source_bindings"]["current_sha256"][RUNNER.T57_SOURCE_PATHS[0]]
        with self.assertRaises(AssertionError):
            self._assert_recovery_source_bindings(missing, preparation)

        altered = copy.deepcopy(record)
        relative = RUNNER.T57_SOURCE_PATHS[0]
        altered["source_bindings"]["current_sha256"][relative] = "0" * 64
        with self.assertRaises(AssertionError):
            self._assert_recovery_source_bindings(altered, preparation)

    def test_rejects_out_of_allowlist_recovery_source_delta(self) -> None:
        record, _ = self._load_recovery_source_bindings()
        source_bindings = record["source_bindings"]
        prepared_hashes = copy.deepcopy(source_bindings["prepared_sha256"])
        current_hashes = dict(source_bindings["current_sha256"])
        relative = "src/int8_mac_accumulator.sv"
        current_hashes[relative] = "0" * 64
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._validate_recovery_source_delta(prepared_hashes, current_hashes)

    def test_rejects_current_verify_only_mismatch_claim(self) -> None:
        record, original_values, _ = self._load_original_failure_snapshots()
        current = list(self._read_current_recovery_evidence())
        bad_summary = copy.deepcopy(current[4])
        bad_summary["verify_only"]["report"]["int8_mismatch_bytes"] = 1
        current[4] = bad_summary
        with self.assertRaises(AssertionError):
            self._assert_current_recovery_contract(record, original_values, *current)

    def test_rejects_an_additional_or_different_failure(self) -> None:
        stage, process, summary = self._recoverable_failure()
        stage["failure"] = str(stage["failure"]) + "; scratch cleanup failed"
        process["failure"] = stage["failure"]
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._validate_recoverable_failure_shape(stage, process, summary)

    def test_refuses_existing_recovery_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            collision = Path(directory) / "attempt09_recovery.json"
            collision.write_text("existing", encoding="utf-8")
            with self.assertRaises(RUNNER.T57Error):
                RUNNER._assert_recovery_outputs_absent((collision,))

    def test_preserves_original_json_snapshot_bytes_and_sha(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "stage_status.json"
            original = b'{"status":"SIMULATION_FLOW_FAIL"}\r\n'
            source.write_bytes(original)
            snapshot = RUNNER._capture_json_snapshot(source)
            restored, parsed = RUNNER._decode_json_snapshot(snapshot, source)
            self.assertEqual(restored, original)
            self.assertEqual(RUNNER._sha256(restored), snapshot["sha256"])
            self.assertEqual(parsed["status"], "SIMULATION_FLOW_FAIL")

    def test_rejects_source_binding_outside_exact_delta_allowlist(self) -> None:
        prepared = {relative: "a" * 64 for relative in RUNNER.T57_SOURCE_PATHS}
        prepared[RUNNER.T57_RUNNER_RELATIVE] = RUNNER.T57_PREPARED_RUNNER_SHA256
        prepared[RUNNER.T57_TRANSCRIPT_TEST_RELATIVE] = \
            RUNNER.T57_PREPARED_TRANSCRIPT_TEST_SHA256
        prepared[RUNNER.T57_RECOVERY_CONTROLLER_RELATIVE] = \
            RUNNER.T57_PREPARED_WRAPPER_SHA256
        current = dict(prepared)
        for relative in (RUNNER.T57_RUNNER_RELATIVE,
                         RUNNER.T57_TRANSCRIPT_TEST_RELATIVE,
                         RUNNER.T57_RECOVERY_CONTROLLER_RELATIVE):
            current[relative] = "b" * 64
        RUNNER._validate_recovery_source_delta(prepared, current)
        current["src/int8_conv_tap_geometry.sv"] = "c" * 64
        with self.assertRaises(RUNNER.T57Error):
            RUNNER._validate_recovery_source_delta(prepared, current)


if __name__ == "__main__":
    unittest.main()
