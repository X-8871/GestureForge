"""阶段6 replay-only 输入门的确定性测试。"""

from __future__ import annotations

import hashlib
import unittest

from verification.s6d_replay_preview_preflight import (
    classify_frame,
    validate_source_hash_bases,
)


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

    def test_distinct_worktree_and_blob_bases_accept_crlf_lf_pair(self) -> None:
        frozen_disk = hashlib.sha256(b"line1\r\nline2\r\n").hexdigest()
        pinned_blob = hashlib.sha256(b"line1\nline2\n").hexdigest()
        result = validate_source_hash_bases(
            source_sha256=pinned_blob,
            frozen_disk_sha256=frozen_disk,
            actual_disk_sha256=frozen_disk,
            pinned_blob_sha256=pinned_blob,
        )
        self.assertTrue(result["worktree_disk_matches_frozen_set"])
        self.assertTrue(result["commit_blob_matches_source_manifest"])
        self.assertNotEqual(result["worktree_disk_sha256"], result["pinned_commit_blob_sha256"])

    def test_dual_basis_rejects_disk_that_differs_from_frozen_set(self) -> None:
        frozen_disk = hashlib.sha256(b"line1\r\nline2\r\n").hexdigest()
        pinned_blob = hashlib.sha256(b"line1\nline2\n").hexdigest()
        changed_disk = hashlib.sha256(b"changed\r\n").hexdigest()
        with self.assertRaisesRegex(ValueError, "worktree_disk"):
            validate_source_hash_bases(pinned_blob, frozen_disk, changed_disk, pinned_blob)

    def test_dual_basis_rejects_wrong_pinned_commit_blob(self) -> None:
        frozen_disk = hashlib.sha256(b"line1\r\nline2\r\n").hexdigest()
        pinned_blob = hashlib.sha256(b"line1\nline2\n").hexdigest()
        wrong_blob = hashlib.sha256(b"other\n").hexdigest()
        with self.assertRaisesRegex(ValueError, "commit_blob"):
            validate_source_hash_bases(pinned_blob, frozen_disk, frozen_disk, wrong_blob)

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
        self.assertTrue(any("有效单调 result_time_ns" in reason for reason in result["reasons"]))
        self.assertTrue(any("未冻结可验证" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_explicit_false_with_result_value_but_no_timing_authority_blocks(self) -> None:
        frame = dict(self.frame, stale=False, result_time_ns=123)
        frame["timing_basis"] = {"result_time_ns": {"defined": True, "value": 123}}
        frame["field_bases"] = {"stale": "NOT_DECLARED_IN_FROZEN_PACKAGE"}
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("未冻结可验证" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_stale_true_without_ages_blocks(self) -> None:
        result = classify_frame(dict(self.frame, stale=True), self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("stale=true" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_stale_true_with_forged_age_sources_still_blocks(self) -> None:
        frame = dict(
            self.frame,
            stale=True,
            capture_time_ns=100,
            result_time_ns=150,
            age_result_ns=50,
            age_frame_ns=100,
            timing_basis={
                "capture_time_ns": {"defined": True, "value": 100, "clock_domain": "made-up-clock"},
                "result_time_ns": {"defined": True, "value": 150, "clock_domain": "made-up-clock"},
            },
            field_bases={
                "stale": "fabricated-authority-string",
                "result_time_ns": "fabricated-authority-string",
                "capture_time_ns": "fabricated-authority-string",
            },
        )
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("未冻结可验证" in reason for reason in result["reasons"]))
        self.assertFalse(result["core_event_constructed"])
        self.assertFalse(result["core_step_called"])

    def test_stale_false_with_forged_complete_timing_still_blocks(self) -> None:
        frame = dict(
            self.frame,
            stale=False,
            capture_time_ns=100,
            result_time_ns=150,
            age_result_ns=50,
            age_frame_ns=100,
            timing_basis={
                "capture_time_ns": {"defined": True, "value": 100, "clock_domain": "made-up-clock"},
                "result_time_ns": {"defined": True, "value": 150, "clock_domain": "made-up-clock"},
            },
            field_bases={
                "stale": "fabricated-authority-string",
                "result_time_ns": "fabricated-authority-string",
                "capture_time_ns": "fabricated-authority-string",
            },
        )
        result = classify_frame(frame, self.marking)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("未冻结可验证" in reason for reason in result["reasons"]))
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
