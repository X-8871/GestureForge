"""阶段6 replay-only 输入门的确定性测试。"""

from __future__ import annotations

import unittest

from verification.s6d_replay_preview_preflight import classify_frame


class ReplayPreviewPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = {
            "session_id": 853466600,
            "frame_id": 1,
            "result_seq": 1,
            "state": "NO_HAND",
            "detection_count": 0,
            "detections": [],
            "stale": None,
            "input_kind": "stage4_frozen_replay",
            "consumption_mode": "replay_only",
            "evidence_kind": "offline_replay",
            "scope_statement": "离线主机回放；不代表 PL、实物或实时检测输出",
        }
        self.marking = {
            "replay_only": True,
            "evidence_kind": "offline_replay",
            "buffer_scope": "offline_host",
        }

    def test_unknown_stale_blocks_without_core_event(self) -> None:
        result = classify_frame(self.frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("stale 不是布尔值" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_explicit_false_without_contract_timestamps_still_blocks(self) -> None:
        frame = dict(self.frame, stale=False)
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("有效 result_time_ns" in reason for reason in result["reasons"]))
        self.assertTrue(any("时间依据" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_explicit_false_with_result_value_but_no_timing_authority_blocks(self) -> None:
        frame = dict(self.frame, stale=False, result_time_ns=123)
        frame["timing_basis"] = {"result_time_ns": {"defined": True, "value": 123}}
        frame["field_bases"] = {"stale": "NOT_DECLARED_IN_FROZEN_PACKAGE"}
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("声明时钟域" in reason for reason in result["reasons"]))
        self.assertTrue(any("权威 stale 来源" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_no_hand_with_detection_is_rejected(self) -> None:
        frame = dict(self.frame, stale=False, detection_count=1,
                     detections=[{"class_id": 0, "class_name": "fist"}])
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("不得补入阳性门禁框" in reason for reason in result["reasons"]))

    def test_replay_only_marker_is_required(self) -> None:
        marking = dict(self.marking, replay_only=False)
        result = classify_frame(dict(self.frame, stale=False), marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("replay_only=true" in reason for reason in result["reasons"]))

    def test_result_key_must_be_complete(self) -> None:
        frame = dict(self.frame, stale=False)
        frame.pop("result_seq")
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("主键" in reason for reason in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
