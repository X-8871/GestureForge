"""阶段4真实PS诊断输入资格和关联关系测试。"""

from __future__ import annotations

import copy
import unittest

from verification.s6d_real_ps_trace_preflight import PreflightError, assess_diagnostic


class RealPsTracePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = {
            "status": "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED",
            "hardware_run_id": "s4b_ps_tensor_hw_20261027_r01",
            "complete_stage4_or_RGB_preprocess": "NOT_CLAIMED",
            "artifact_identity": {"session_first": 1396845568, "session_last": 1396846567},
            "trace_dump": {"record_count": 1,
                           "decoder_status": "PASS_DECODED_DOUBLE_READ_SNAPSHOT"},
            "trace_uart_join": {
                "status": "PASS_EXACT_TRACE_UART_JOIN",
                "matches": [{"session_id": 1396845568, "frame_id": 0,
                             "result_seq": 1, "repeat_index": 0,
                             "uart_sequence": 2, "input_crc32": 1064075869}],
            },
            "uart_receipts": [{
                "frame": 0, "index": 0, "sequence": 2, "epoch": 1,
                "input_crc32": 1064075869, "detection_count": 1,
                "meta": {"box_count": 1, "raw_candidate_count": 2,
                         "phys_status": 3588},
                "heads": {"head13": {"sha256": "a" * 64},
                          "head26": {"sha256": "b" * 64}},
            }],
        }
        self.events = [
            {"event": "OP_WEIGHTS", "sequence": 1},
            {"event": "OP_RUN_response", "sequence": 2, "frame": 0,
             "index": 0, "input_crc32": 1064075869},
        ]
        self.decoded = {
            "status": "PASS_DECODED_DOUBLE_READ_SNAPSHOT",
            "snapshot_stability": "two_full_region_reads_byte_identical",
            "record_count": 1,
            "header": {"active_session_id": 1396845568,
                       "last_assigned_session_id": 1396845568,
                       "active_uart_sequence": 2, "active_base_frame": 0},
            "records": [{
                "session_id": 1396845568, "frame_id": 0, "result_seq": 1,
                "repeat_index": 0, "uart_sequence": 2,
                "input_crc32": 1064075869, "capture_time_available": False,
                "capture_time_ns": 0, "detection_count": 1,
                "raw_candidate_count": 2, "epoch": 1,
                "terminal_status": 3588, "terminal_safe": True,
                "response_status": 0, "uart_send_status": 2, "ack_state": 1,
            }],
        }
        self.contract = {"status": "PASS"}

    def assess(self, adapter=None, events=None, decoded=None):
        return assess_diagnostic(
            adapter or copy.deepcopy(self.adapter),
            events or copy.deepcopy(self.events),
            decoded or copy.deepcopy(self.decoded),
            self.contract,
        )

    def test_exact_join_passes_but_real_ps_diagnostic_is_not_a_core_event(self) -> None:
        result = self.assess()
        self.assertEqual(result["status"], "DIAGNOSTIC_ONLY")
        self.assertEqual(result["stage6_core_eligibility"], "BLOCKED")
        self.assertEqual(result["observed_keys"]["ps_log_primary_key"], [1396845568, 1])
        self.assertEqual(result["observed_keys"]["uart_observable_key"], [0, 0, 2])
        self.assertFalse(result["uart_sequence_namespace_evidence"]["ps_result_seq_is_uart_sequence"])
        self.assertFalse(result["diagnostic_counts"]["box_geometry_present"])
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_receipt_cannot_alias_uart_sequence_as_result_seq(self) -> None:
        adapter = copy.deepcopy(self.adapter)
        adapter["trace_uart_join"]["matches"][0]["result_seq"] = 2
        with self.assertRaisesRegex(PreflightError, "join 与独立解码记录不一致"):
            self.assess(adapter=adapter)

    def test_wrong_uart_run_sequence_is_rejected(self) -> None:
        events = copy.deepcopy(self.events)
        events[1]["sequence"] = 1
        with self.assertRaisesRegex(PreflightError, "UART OP_RUN 事件与 PS trace 不一致"):
            self.assess(events=events)

    def test_session_mismatch_is_rejected(self) -> None:
        decoded = copy.deepcopy(self.decoded)
        decoded["records"][0]["session_id"] = 1396845569
        with self.assertRaisesRegex(PreflightError, "结果键不符"):
            self.assess(decoded=decoded)

    def test_count_mismatch_is_rejected(self) -> None:
        adapter = copy.deepcopy(self.adapter)
        adapter["uart_receipts"][0]["meta"]["box_count"] = 0
        with self.assertRaisesRegex(PreflightError, "计数在 PS trace 与 UART 回执间不一致"):
            self.assess(adapter=adapter)

    def test_missing_box_payload_and_time_fields_block_without_fresh_default(self) -> None:
        result = self.assess()
        self.assertEqual(result["stage6_core_eligibility"], "BLOCKED")
        self.assertEqual(result["diagnostic_counts"]["detection_count"], 1)
        self.assertFalse(result["diagnostic_counts"]["detections_payload_present"])
        self.assertFalse(result["time_fields"]["capture_time_available"])
        self.assertFalse(result["time_fields"]["stale_present"])
        self.assertFalse(result["time_fields"]["raw_ticks_converted_to_ns"])
        self.assertTrue(any("不得由计数或哈希推造框" in reason for reason in result["reasons"]))

    def test_trace_without_one_record_is_rejected(self) -> None:
        decoded = copy.deepcopy(self.decoded)
        decoded["record_count"] = 2
        with self.assertRaisesRegex(PreflightError, "固定单帧诊断应恰有一条 PS trace 记录"):
            self.assess(decoded=decoded)


if __name__ == "__main__":
    unittest.main()
