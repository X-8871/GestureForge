#!/usr/bin/env python3
"""验证 T57 attempt09 的 console transcript 截取和 CRLF 解析。"""

from __future__ import annotations

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

    def test_accepts_the_exact_saved_attempt09_failure_snapshots(self) -> None:
        root = RUNNER.RUN_ROOT
        stage, stage_sha = RUNNER._read_json(root / "stage_status.json")
        process, process_sha = RUNNER._read_json(root / "process_status.json")
        summary, summary_sha = RUNNER._read_json(root / "run_summary.json")
        self.assertEqual(stage_sha, RUNNER.T57_ATTEMPT09_STAGE_FAIL_SHA256)
        self.assertEqual(process_sha, RUNNER.T57_ATTEMPT09_PROCESS_FAIL_SHA256)
        self.assertEqual(summary_sha, RUNNER.T57_ATTEMPT09_RUN_FAIL_SHA256)
        RUNNER._validate_recoverable_failure_shape(stage, process, summary)

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
