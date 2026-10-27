"""阶段6核心状态与动作回执缺口的隔离回归。"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage6.s6_core import (
    EV_FRAME_ERROR,
    EV_FRAME_RESULT,
    EV_TICK,
    CoreInputError,
    GestureInteractionCore,
)
from src.stage6.s6_params import ParamPack
from verification.s6b_run_cases import run_case


class S6BCoreRegressionTests(unittest.TestCase):
    """验证当前批准行为中的 IDLE 丢失和重复 ACK 语义。"""

    @classmethod
    def setUpClass(cls):
        cls.pack = ParamPack(
            ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
            project_root=ROOT,
        )

    @staticmethod
    def _target_event(frame_id, timestamp):
        return {
            "kind": EV_FRAME_RESULT,
            "session_id": "regression-session",
            "frame_id": frame_id,
            "state": "OK",
            "t_input_ns": timestamp,
            "detections": [{
                "class_id": 0,
                "score": 0.9,
                "xyxy": [0.2, 0.2, 0.6, 0.6],
                "source_order": 0,
            }],
        }

    def test_idle_target_expires_at_l02_then_reacquires_with_new_id(self):
        core = GestureInteractionCore(self.pack)
        first = core.step(self._target_event(1, 0))
        self.assertEqual(first["log"]["to_state"], "IDLE")
        self.assertIsNotNone(core.current_target)

        l02_ns = self.pack.threshold_bundle()["l02_ns"]
        expired = core.step({
            "kind": EV_TICK,
            "session_id": "regression-session",
            "t_input_ns": l02_ns,
        })
        self.assertEqual(expired["log"]["transition"], "M10")
        self.assertEqual(core.state, "LOST")

        completed = core.step({
            "kind": EV_TICK,
            "session_id": "regression-session",
            "t_input_ns": l02_ns + 1,
        })
        self.assertEqual(completed["log"]["transition"], "M11")
        self.assertEqual(core.state, "IDLE")
        self.assertIsNone(core.current_target)
        self.assertEqual(core.acquisition_id, 1)

        reacquired = core.step(self._target_event(2, l02_ns + 2))
        self.assertEqual(reacquired["log"]["transition"], None)
        self.assertEqual(core.state, "IDLE")
        self.assertEqual(core.acquisition_id, 1)
        self.assertEqual(core.current_target["acquisition_id"], 1)

    def test_duplicate_ack_policy_replays_one_ack_without_double_count(self):
        events = [self._target_event(index, (index - 1) * 100_000_000)
                  for index in range(1, 14)]
        case = {
            "case_id": "regression-duplicate-ack",
            "matrix_class": "B28 duplicate ACK 判别力",
            "outcome_policy": {"duplicate_ack_attempts": [1]},
            "events": events,
            "expected": {},
        }
        observed = run_case(case, self.pack)

        self.assertEqual(observed["action_summary"]["action_submitted"], 1)
        self.assertEqual(observed["action_summary"]["action_effective"], 1)
        self.assertEqual(observed["core_counters"]["action_submitted"], 1)
        self.assertEqual(observed["core_counters"]["action_effective"], 1)
        ack_rows = [row for row in observed["logs"] if row.get("kind") == "action_ack"]
        duplicate_rows = [row for row in observed["logs"]
                          if row.get("kind") == "action_ack_duplicate"]
        self.assertEqual(len(ack_rows), 1)
        self.assertEqual(len(duplicate_rows), 1)
        self.assertTrue(duplicate_rows[0]["duplicate_ack_ignored"])
        self.assertEqual(sum(1 for value in observed["transitions"] if value == "M6"), 1)
        self.assertEqual(
            sum(1 for row in observed["action_records"]
                if row.get("submit_result") == "success"),
            1,
        )

    def test_b22_ignores_receive_time_and_transport_context_only(self):
        core = GestureInteractionCore(self.pack)
        original = self._target_event(7, 0)
        core.step(original)
        before = (core.state, core.current_target, dict(core.counters))

        replay = self._target_event(7, 25_000_000)
        replay["age_result_ns"] = 25_000_000
        replay["age_frame_ns"] = 50_000_000
        replay["dropped_frames"] = 3
        observed = core.step(replay)

        self.assertEqual(observed["log"]["event_kind"], "E_FRAME_DUPLICATE")
        self.assertEqual(observed["log"]["age_result_ns"], 25_000_000)
        self.assertEqual(observed["log"]["age_frame_ns"], 50_000_000)
        self.assertEqual(observed["log"]["frame_content_sha256"], core.last_frame_business_sha256)
        self.assertIsNone(observed["action_request"])
        self.assertEqual(core.state, before[0])
        self.assertEqual(core.current_target, before[1])
        self.assertEqual(core.counters["duplicate_frames"], before[2]["duplicate_frames"] + 1)
        for key, value in before[2].items():
            if key != "duplicate_frames":
                self.assertEqual(core.counters[key], value, key)

    def test_b22_conflicts_on_stale_state_detection_and_error_content_changes(self):
        mutations = (
            ("stale", self._target_event(9, 0), lambda event: event.update(stale=True)),
            ("state", self._target_event(9, 0), lambda event: event.update(state="ERROR")),
            ("detection", self._target_event(9, 0),
             lambda event: event["detections"][0].update(score=0.8)),
            ("event kind", self._target_event(9, 0),
             lambda event: event.update(kind=EV_FRAME_ERROR)),
            ("error payload", {
                "kind": EV_FRAME_ERROR,
                "session_id": "regression-session",
                "frame_id": 9,
                "t_input_ns": 0,
                "error_code": "E_A",
            }, lambda event: event.update(error_code="E_B")),
        )
        for label, original, mutate in mutations:
            with self.subTest(field=label):
                core = GestureInteractionCore(self.pack)
                core.step(original)
                before_state = core.state
                before_target = None if core.current_target is None else core.current_target.copy()
                changed = dict(original)
                changed["t_input_ns"] = 1
                if "detections" in changed:
                    changed["detections"] = [dict(item) for item in changed["detections"]]
                mutate(changed)

                observed = core.step(changed)

                self.assertEqual(observed["log"]["event_kind"], "E_FRAME_CONFLICT")
                self.assertNotEqual(
                    observed["log"]["previous_frame_content_sha256"],
                    observed["log"]["received_frame_content_sha256"],
                )
                self.assertEqual(core.state, before_state)
                self.assertEqual(core.current_target, before_target)
                self.assertEqual(core.counters["conflict_frames"], 1)
                self.assertEqual(core.counters["invalid"], 0)

    @classmethod
    def _ack_core(cls):
        core = GestureInteractionCore(cls.pack)
        core.session_id = "ack-session"
        core.state = "TRIGGERED"
        core.current_target = {"class_id": 0}
        return core

    def test_suppression_without_action_id_is_valid_and_not_deduplicated(self):
        core = self._ack_core()
        ack = {"suppression": "S_DEDUP", "reason": "动作层去重"}

        first = core.note_action_ack(ack)
        second = core.note_action_ack(ack)

        self.assertEqual(first["suppression_events"], ["S_DEDUP"])
        self.assertEqual(second["suppression_events"], ["S_DEDUP"])
        self.assertFalse(first.get("duplicate_ack_ignored", False))
        self.assertFalse(second.get("duplicate_ack_ignored", False))
        self.assertEqual(core._seen_action_ack_ids, set())
        self.assertEqual(core.counters["action_submitted"], 0)

    def test_unknown_or_nonstring_suppression_is_rejected_transactionally(self):
        invalid_suppressions = (
            ("truthy bool", True),
            ("truthy integer", 7),
            ("truthy list", ["S_DEDUP"]),
            ("truthy object", {"value": "S_DEDUP"}),
            ("falsey integer", 0),
            ("falsey bool", False),
            ("falsey list", []),
            ("falsey object", {}),
            ("empty string", ""),
            ("core-only suppression", "S_COOLDOWN"),
            ("unknown string", "S_NOT_DEFINED"),
        )
        for index, (label, suppression) in enumerate(invalid_suppressions):
            with self.subTest(suppression=label):
                core = self._ack_core()
                core.acquisition_triggered = True
                before = self._ack_snapshot(core)
                action_id = f"malformed-suppression-{index}"
                ack = {
                    "suppression": suppression,
                    "reason": "畸形 suppression 必须拒绝",
                    # 携带真实成功 ACK 字段，确保 falsey 畸形值不能落入真实提交路径。
                    "action_id": action_id,
                    "submit_result": "success",
                    "effective_result": "observed",
                    "t_submit_ns": 10,
                    "t_effective_ns": 11,
                }

                with self.assertRaises(CoreInputError):
                    core.note_action_ack(ack)

                self.assertEqual(self._ack_snapshot(core), before)
                self.assertNotIn(action_id, core._seen_action_ack_ids)

    def test_real_success_and_fail_ack_require_nonempty_string_id(self):
        invalid_ids = (None, "", " \t ", 7, [], {})
        for submit_result in ("success", "fail"):
            for action_id in invalid_ids:
                with self.subTest(submit_result=submit_result, action_id=action_id):
                    core = self._ack_core()
                    ack = {
                        "action_id": action_id,
                        "submit_result": submit_result,
                        "effective_result": "observed" if submit_result == "success" else "unobserved",
                        "t_submit_ns": 12,
                    }
                    before_state = core.state
                    with self.assertRaises(CoreInputError):
                        core.note_action_ack(ack)
                    self.assertEqual(core.state, before_state)
                    self.assertEqual(core.counters["action_submitted"], 0)
                    self.assertEqual(core.counters["false_actions"], 0)
                    self.assertIsNone(core.t_last_submit_ns)
                    self.assertEqual(core._seen_action_ack_ids, set())
                    self.assertEqual(core.action_log, [])

    @staticmethod
    def _ack_snapshot(core):
        return (
            core.state,
            dict(core.counters),
            core.t_last_submit_ns,
            set(core._seen_action_ack_ids),
            list(core.action_log),
            core.acquisition_triggered,
        )

    def test_invalid_ack_timestamps_and_result_combinations_are_transactional(self):
        invalid_acks = (
            ("success missing submit time", {
                "action_id": "bad-success-submit-missing", "submit_result": "success",
                "effective_result": "observed", "t_effective_ns": 10,
            }),
            ("success None submit time", {
                "action_id": "bad-success-submit-none", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": None, "t_effective_ns": 10,
            }),
            ("success bool submit time", {
                "action_id": "bad-success-submit-bool", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": True, "t_effective_ns": 10,
            }),
            ("success float submit time", {
                "action_id": "bad-success-submit-float", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": 1.0, "t_effective_ns": 10,
            }),
            ("success string submit time", {
                "action_id": "bad-success-submit-string", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": "10", "t_effective_ns": 10,
            }),
            ("success unknown effective result", {
                "action_id": "bad-success-effective-unknown", "submit_result": "success",
                "effective_result": "maybe", "t_submit_ns": 10,
            }),
            ("success observed missing effective time", {
                "action_id": "bad-success-effective-missing", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": 10,
            }),
            ("success observed bool effective time", {
                "action_id": "bad-success-effective-bool", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": 10, "t_effective_ns": True,
            }),
            ("success observed float effective time", {
                "action_id": "bad-success-effective-float", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": 10, "t_effective_ns": 10.0,
            }),
            ("success observed earlier effective time", {
                "action_id": "bad-success-effective-order", "submit_result": "success",
                "effective_result": "observed", "t_submit_ns": 10, "t_effective_ns": 9,
            }),
            ("success unobserved carries effective time", {
                "action_id": "bad-success-unobserved-time", "submit_result": "success",
                "effective_result": "unobserved", "t_submit_ns": 10, "t_effective_ns": 10,
            }),
            ("fail missing submit time", {
                "action_id": "bad-fail-submit-missing", "submit_result": "fail",
                "effective_result": "unobserved",
            }),
            ("fail bool submit time", {
                "action_id": "bad-fail-submit-bool", "submit_result": "fail",
                "effective_result": "unobserved", "t_submit_ns": True,
            }),
            ("fail missing effective result", {
                "action_id": "bad-fail-effective-missing", "submit_result": "fail",
                "t_submit_ns": 10,
            }),
            ("fail unknown effective result", {
                "action_id": "bad-fail-effective-unknown", "submit_result": "fail",
                "effective_result": "error", "t_submit_ns": 10,
            }),
            ("fail observed result", {
                "action_id": "bad-fail-observed", "submit_result": "fail",
                "effective_result": "observed", "t_submit_ns": 10, "t_effective_ns": 10,
            }),
            ("fail unobserved carries effective time", {
                "action_id": "bad-fail-unobserved-time", "submit_result": "fail",
                "effective_result": "unobserved", "t_submit_ns": 10, "t_effective_ns": 10,
            }),
        )
        for label, ack in invalid_acks:
            with self.subTest(case=label):
                core = self._ack_core()
                before = self._ack_snapshot(core)
                with self.assertRaises(CoreInputError):
                    core.note_action_ack(ack)
                self.assertEqual(self._ack_snapshot(core), before)

    def test_invalid_duplicate_ack_is_rejected_before_dedup_side_effects(self):
        core = self._ack_core()
        valid = {
            "action_id": "duplicate-transaction-1",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 11,
        }
        core.note_action_ack(valid)
        before = self._ack_snapshot(core)

        with self.assertRaises(CoreInputError):
            core.note_action_ack({**valid, "effective_result": "unknown"})

        self.assertEqual(self._ack_snapshot(core), before)

    def test_missing_new_submit_time_preserves_existing_cooldown_anchor(self):
        core = self._ack_core()
        core.note_action_ack({
            "action_id": "anchor-existing",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 10,
        })
        core.state = "TRIGGERED"
        before = self._ack_snapshot(core)
        malformed = {
            "action_id": "anchor-missing-time",
            "submit_result": "success",
            "effective_result": "unobserved",
        }

        with self.assertRaises(CoreInputError):
            core.note_action_ack(malformed)

        self.assertEqual(self._ack_snapshot(core), before)
        self.assertNotIn("anchor-missing-time", core._seen_action_ack_ids)

    def test_new_ack_cannot_move_cooldown_anchor_backwards(self):
        core = self._ack_core()
        core.note_action_ack({
            "action_id": "anchor-first",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 10,
        })
        core.state = "TRIGGERED"
        before = self._ack_snapshot(core)

        with self.assertRaises(CoreInputError):
            core.note_action_ack({
                "action_id": "anchor-regression",
                "submit_result": "success",
                "effective_result": "observed",
                "t_submit_ns": 9,
                "t_effective_ns": 9,
            })

        self.assertEqual(self._ack_snapshot(core), before)

    def test_late_valid_duplicate_ack_is_ignored_after_a_later_anchor(self):
        core = self._ack_core()
        first = {
            "action_id": "late-duplicate-first",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 10,
        }
        core.note_action_ack(first)
        core.state = "TRIGGERED"
        core.note_action_ack({
            "action_id": "late-duplicate-second",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 20,
            "t_effective_ns": 20,
        })

        duplicate = core.note_action_ack(first)

        self.assertTrue(duplicate["duplicate_ack_ignored"])
        self.assertEqual(core.counters["action_submitted"], 2)
        self.assertEqual(core.t_last_submit_ns, 20)

    def test_opaque_legacy_action_id_is_accepted(self):
        core = self._ack_core()
        result = core.note_action_ack({
            "action_id": "legacy/custom id #7",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 11,
        })
        self.assertEqual(result["transition"], "M6")
        self.assertEqual(core.t_last_submit_ns, 10)

    def test_duplicate_success_ack_does_not_repeat_m6_or_move_cooldown_anchor(self):
        core = self._ack_core()
        ack = {
            "action_id": "success-ack-1",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 100,
            "t_effective_ns": 101,
        }
        first = core.note_action_ack(ack)
        duplicate = core.note_action_ack({**ack, "t_submit_ns": 999, "t_effective_ns": 1000})

        self.assertEqual(first["transition"], "M6")
        self.assertTrue(duplicate["duplicate_ack_ignored"])
        self.assertIsNone(duplicate["transition"])
        self.assertEqual(core.state, "COOLDOWN")
        self.assertEqual(core.t_last_submit_ns, 100)
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.counters["action_effective"], 1)

    def test_duplicate_fail_ack_does_not_repeat_false_action_or_set_cooldown(self):
        core = self._ack_core()
        ack = {
            "action_id": "fail-ack-1",
            "submit_result": "fail",
            "effective_result": "unobserved",
            "t_submit_ns": 200,
        }
        core.note_action_ack(ack)
        duplicate = core.note_action_ack(ack)

        self.assertTrue(duplicate["duplicate_ack_ignored"])
        self.assertEqual(core.state, "STABLE")
        self.assertEqual(core.counters["false_actions"], 1)
        self.assertEqual(core.counters["action_submitted"], 0)
        self.assertIsNone(core.t_last_submit_ns)

    def test_duplicate_unobserved_ack_counts_once_and_preserves_anchor(self):
        core = self._ack_core()
        ack = {
            "action_id": "unobserved-ack-1",
            "submit_result": "success",
            "effective_result": "unobserved",
            "t_submit_ns": 300,
        }
        first = core.note_action_ack(ack)
        duplicate = core.note_action_ack({**ack, "t_submit_ns": 777})

        self.assertEqual(first["transition"], "M6")
        self.assertTrue(duplicate["duplicate_ack_ignored"])
        self.assertEqual(core.state, "COOLDOWN")
        self.assertEqual(core.t_last_submit_ns, 300)
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.counters["action_effective"], 0)
        self.assertEqual(core.counters["unobserved"], 1)
        self.assertEqual(core.counters["false_actions"], 1)

    def test_action_ack_dedup_scope_resets_with_new_session(self):
        core = self._ack_core()
        ack = {
            "action_id": "reused-by-new-session",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 1,
            "t_effective_ns": 1,
        }
        core.note_action_ack(ack)
        reset = core.step({
            "kind": EV_TICK,
            "session_id": "next-session",
            "t_input_ns": 1,
        })
        self.assertEqual(reset["log"]["transition"], "RESET")
        core.state = "TRIGGERED"
        core.current_target = {"class_id": 0}

        next_session = core.note_action_ack({**ack, "t_submit_ns": 2, "t_effective_ns": 2})

        self.assertNotIn("duplicate_ack_ignored", next_session)
        self.assertEqual(core.session_id, "next-session")
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.t_last_submit_ns, 2)


if __name__ == "__main__":
    unittest.main()
