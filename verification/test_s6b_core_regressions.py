"""阶段6核心状态与动作回执缺口的隔离回归。"""

import copy
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
from src.stage6.s6_actions import ActionLayer, SUP_DEDUP
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
    def _target_event(frame_id, timestamp, session_id="regression-session"):
        return {
            "kind": EV_FRAME_RESULT,
            "session_id": session_id,
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

    def test_action_ack_dedup_persists_within_action_layer_lifetime(self):
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
        self.assertEqual(reset["log"]["session_id"], "next-session")
        self.assertEqual(reset["log"]["acquisition_id"], 0)
        self.assertEqual(reset["log"]["counters"]["action_submitted"], 0)
        self.assertEqual(reset["log"]["timers"]["t_last_submit_ns"], 1)
        self.assertEqual(core.t_last_submit_ns, 1)
        self.assertEqual(core.last_t_ns, 1)
        self.assertEqual(core.state, "IDLE")
        self.assertIsNone(core.current_target)

        duplicate = core.note_action_ack(ack)
        self.assertTrue(duplicate["duplicate_ack_ignored"])
        self.assertEqual(core.counters["action_submitted"], 0)

        core.state = "TRIGGERED"
        core.current_target = {"class_id": 0}

        next_session = core.note_action_ack({
            **ack,
            "action_id": "new-session-action",
            "t_submit_ns": 2,
            "t_effective_ns": 2,
        })

        self.assertNotIn("duplicate_ack_ignored", next_session)
        self.assertEqual(core.session_id, "next-session")
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.t_last_submit_ns, 2)

    def test_first_session_and_explicit_reset_preserve_global_time_anchors(self):
        core = GestureInteractionCore(self.pack)
        first = core.step(self._target_event(1, 100, "first-session"))
        self.assertIsNone(first["log"]["transition"])
        self.assertEqual(core.session_id, "first-session")
        self.assertEqual(core.last_t_ns, 100)

        core.state = "TRIGGERED"
        core.note_action_ack({
            "action_id": "first-session-action",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 100,
            "t_effective_ns": 100,
        })
        core.jitter_frames = 3
        core.jitter_exhausted = True
        core.counters["invalid"] = 2
        reset = core.reset_session("explicit-second-session")

        self.assertEqual(core.session_id, "explicit-second-session")
        self.assertEqual(core.state, "IDLE")
        self.assertIsNone(core.current_target)
        self.assertEqual(core.last_t_ns, 100)
        self.assertEqual(core.t_last_submit_ns, 100)
        self.assertEqual(core.counters["action_submitted"], 0)
        self.assertIsNone(reset["action_request"])
        self.assertEqual(reset["log"]["event_kind"], "E_SESSION_RESET_SUSPECTED")
        self.assertEqual(reset["log"]["previous_session_id"], "first-session")
        self.assertEqual(reset["log"]["session_id"], "explicit-second-session")
        self.assertEqual(reset["log"]["from_state"], "COOLDOWN")
        self.assertEqual(reset["log"]["to_state"], "IDLE")
        self.assertEqual(reset["log"]["transition"], "RESET")
        self.assertEqual(reset["log"]["counters"], core.counters)
        self.assertEqual(reset["log"]["counters"]["invalid"], 0)
        self.assertEqual(reset["log"]["timers"]["last_t_ns"], 100)
        self.assertEqual(reset["log"]["timers"]["t_last_submit_ns"], 100)
        self.assertEqual(reset["log"]["timers"]["jitter_frames"], 0)
        self.assertFalse(reset["log"]["timers"]["jitter_exhausted"])
        self.assertEqual(core._seen_action_ack_ids, {"first-session-action"})
        self.assertEqual(reset["log"]["acquisition_id"], 0)

        equal_time = core.step(self._target_event(1, 100, "explicit-second-session"))
        self.assertIsNone(equal_time["log"]["transition"])
        self.assertEqual(core.last_t_ns, 100)

    def test_session_reset_reacquisition_obeys_global_cooldown_and_equal_boundary(self):
        core = GestureInteractionCore(self.pack)
        core.step(self._target_event(1, 0, "first-session"))
        core.state = "TRIGGERED"
        core.note_action_ack({
            "action_id": "cooldown-anchor-action",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 0,
            "t_effective_ns": 0,
        })

        reset = core.step({
            "kind": EV_TICK,
            "session_id": "second-session",
            "t_input_ns": 1,
        })
        self.assertEqual(reset["log"]["transition"], "RESET")
        self.assertEqual(core.t_last_submit_ns, 0)

        k01_ns = self.pack.threshold_bundle()["k01_ns"]
        interval_ns = 50_000_000
        before_boundary = None
        frame_id = 1
        timestamp = 2
        while timestamp < k01_ns:
            before_boundary = core.step(
                self._target_event(frame_id, timestamp, "second-session")
            )
            frame_id += 1
            timestamp = 2 + (frame_id - 1) * interval_ns

        self.assertEqual(core.state, "STABLE")
        self.assertIsNotNone(before_boundary)
        self.assertIn("S_COOLDOWN", before_boundary["log"]["suppression_events"])
        self.assertIsNone(before_boundary["action_request"])
        self.assertLess(core.last_t_ns, k01_ns)

        at_boundary = core.step(
            self._target_event(frame_id, k01_ns, "second-session")
        )
        self.assertEqual(at_boundary["log"]["transition"], "M5")
        self.assertEqual(core.state, "TRIGGERED")
        self.assertIsNotNone(at_boundary["action_request"])
        self.assertEqual(at_boundary["log"]["timers"]["t_last_submit_ns"], 0)

    def test_global_cooldown_boundary_minus_equal_plus_one_ns(self):
        k01_ns = self.pack.threshold_bundle()["k01_ns"]

        def stable_reacquisition():
            core = GestureInteractionCore(self.pack)
            core.step(self._target_event(1, 0, "first-session"))
            core.state = "TRIGGERED"
            core.note_action_ack({
                "action_id": "cooldown-edge-anchor",
                "submit_result": "success",
                "effective_result": "observed",
                "t_submit_ns": 0,
                "t_effective_ns": 0,
            })
            core.step({
                "kind": EV_TICK,
                "session_id": "second-session",
                "t_input_ns": 1,
            })

            frame_id = 1
            timestamp = 2
            while timestamp < k01_ns - 100_000_000:
                core.step(self._target_event(frame_id, timestamp, "second-session"))
                frame_id += 1
                timestamp = 2 + (frame_id - 1) * 50_000_000

            self.assertEqual(core.state, "STABLE")
            return core, frame_id

        for offset_ns, should_trigger in ((-1, False), (0, True), (1, True)):
            with self.subTest(k01_offset_ns=offset_ns):
                core, frame_id = stable_reacquisition()
                before = core.step(
                    self._target_event(frame_id, k01_ns - 1, "second-session")
                )
                self.assertIsNone(before["action_request"])
                self.assertIn("S_COOLDOWN", before["log"]["suppression_events"])
                self.assertEqual(core.state, "STABLE")

                if offset_ns == -1:
                    continue

                at_or_after = core.step(
                    self._target_event(frame_id + 1, k01_ns + offset_ns, "second-session")
                )
                self.assertEqual(at_or_after["log"]["transition"], "M5")
                self.assertEqual(core.state, "TRIGGERED")
                self.assertEqual(at_or_after["action_request"] is not None, should_trigger)

    def test_backwards_time_on_session_change_is_transactional(self):
        core = GestureInteractionCore(self.pack)
        core.step(self._target_event(1, 100, "first-session"))
        core.state = "TRIGGERED"
        core.note_action_ack({
            "action_id": "transaction-anchor",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 100,
            "t_effective_ns": 100,
        })
        before = (
            core.session_id,
            core.state,
            dict(core.counters),
            core.last_t_ns,
            core.t_last_submit_ns,
            None if core.current_target is None else dict(core.current_target),
            core.last_frame_id,
            core.last_frame_business_sha256,
            core.acquisition_id,
            core.window_match_count,
            core.window_start_ns,
            set(core._seen_action_ack_ids),
            list(core.action_log),
        )

        with self.assertRaisesRegex(CoreInputError, "单调时钟倒退"):
            core.step({
                "kind": EV_TICK,
                "session_id": "backwards-session",
                "t_input_ns": 99,
            })

        after = (
            core.session_id,
            core.state,
            dict(core.counters),
            core.last_t_ns,
            core.t_last_submit_ns,
            None if core.current_target is None else dict(core.current_target),
            core.last_frame_id,
            core.last_frame_business_sha256,
            core.acquisition_id,
            core.window_match_count,
            core.window_start_ns,
            set(core._seen_action_ack_ids),
            list(core.action_log),
        )
        self.assertEqual(after, before)

    def test_action_layer_dedup_scope_survives_core_session_reset(self):
        core = GestureInteractionCore(self.pack)
        layer = ActionLayer(self.pack)
        request = {
            "action_type": "A_SWITCH_UI",
            "target_id": "MAIN",
            "class_id": 0,
            "class_name": "class-0",
            "source_frame_id": 1,
            "trigger_frame_id": 1,
            "t_trigger_ns": 100,
        }
        first = layer.submit(request, 100)
        self.assertEqual(first["submit_result"], "success")

        core.reset_session("next-session")
        a02_ns = self.pack.threshold_bundle()["a02_ns"]
        before_boundary = layer.submit(request, 100 + a02_ns - 1)
        at_boundary = layer.submit(request, 100 + a02_ns)

        self.assertEqual(before_boundary["suppression"], SUP_DEDUP)
        self.assertEqual(at_boundary["submit_result"], "success")
        self.assertEqual(at_boundary["action_id"], "ACT-0002")

    @staticmethod
    def _step_snapshot(core):
        return (
            core.session_id,
            core.state,
            dict(core.counters),
            core.last_t_ns,
            core.t_last_submit_ns,
            copy.deepcopy(core.current_target),
            core.last_frame_id,
            core.last_frame_business_sha256,
            core.acquisition_id,
            core.acquisition_triggered,
            core.candidate_streak,
            core.window_match_count,
            core.window_start_ns,
            core.jitter_frames,
            core.jitter_exhausted,
            core.window_complete_ns,
            tuple(core.anomaly_history),
            list(core.result_history),
            list(core.action_log),
            set(core._seen_action_ack_ids),
            core.step_anomaly,
        )

    def test_jitter_exhaustion_is_cleared_by_explicit_and_implicit_session_reset(self):
        for reset_mode in ("explicit", "implicit"):
            with self.subTest(reset_mode=reset_mode):
                core = GestureInteractionCore(self.pack)
                for frame_id, score in ((1, 0.9), (2, 0.9), (3, 0.28), (4, 0.28)):
                    event = self._target_event(
                        frame_id,
                        (frame_id - 1) * 10_000_000,
                        "jitter-session",
                    )
                    event["detections"][0]["score"] = score
                    result = core.step(event)

                self.assertEqual(core.state, "CANDIDATE")
                self.assertTrue(core.jitter_exhausted)
                self.assertIsNone(result["log"]["transition"])
                self.assertTrue(core.result_history)

                if reset_mode == "explicit":
                    core.reset_session("explicit-reset-session")
                    expected_last_t_ns = 30_000_000
                    expected_session_id = "explicit-reset-session"
                else:
                    reset = core.step({
                        "kind": EV_TICK,
                        "session_id": "implicit-reset-session",
                        "t_input_ns": 40_000_000,
                    })
                    self.assertEqual(reset["log"]["transition"], "RESET")
                    expected_last_t_ns = 40_000_000
                    expected_session_id = "implicit-reset-session"

                self.assertEqual(
                    {
                        "session_id": core.session_id,
                        "state": core.state,
                        "current_target": core.current_target,
                        "last_frame_id": core.last_frame_id,
                        "acquisition_id": core.acquisition_id,
                        "acquisition_triggered": core.acquisition_triggered,
                        "candidate_streak": core.candidate_streak,
                        "candidate_dwell_start_ns": core.candidate_dwell_start_ns,
                        "window_match_count": core.window_match_count,
                        "window_start_ns": core.window_start_ns,
                        "window_last_match_center": core.window_last_match_center,
                        "jitter_frames": core.jitter_frames,
                        "jitter_exhausted": core.jitter_exhausted,
                        "window_complete_ns": core.window_complete_ns,
                        "result_history": core.result_history,
                        "anomaly_history": tuple(core.anomaly_history),
                        "last_t_ns": core.last_t_ns,
                    },
                    {
                        "session_id": expected_session_id,
                        "state": "IDLE",
                        "current_target": None,
                        "last_frame_id": None,
                        "acquisition_id": 0,
                        "acquisition_triggered": False,
                        "candidate_streak": 0,
                        "candidate_dwell_start_ns": None,
                        "window_match_count": 0,
                        "window_start_ns": None,
                        "window_last_match_center": None,
                        "jitter_frames": 0,
                        "jitter_exhausted": False,
                        "window_complete_ns": None,
                        "result_history": [],
                        "anomaly_history": (),
                        "last_t_ns": expected_last_t_ns,
                    },
                )

    def test_unknown_kind_is_transactional_for_same_and_new_session(self):
        for session_id in ("current-session", "new-session"):
            with self.subTest(session_id=session_id):
                core = GestureInteractionCore(self.pack)
                core.step(self._target_event(1, 100, "current-session"))
                core.state = "STABLE"
                core.window_match_count = 4
                core.step_anomaly = True
                before = self._step_snapshot(core)

                with self.assertRaisesRegex(CoreInputError, "未知事件类型"):
                    core.step({
                        "kind": "E_UNRECOGNIZED",
                        "session_id": session_id,
                        "t_input_ns": 101,
                    })

                self.assertEqual(self._step_snapshot(core), before)

    def test_malformed_step_envelopes_are_transactional_before_session_reset(self):
        malformed_events = (
            ("boolean frame_id", {
                "kind": EV_FRAME_RESULT, "frame_id": True, "state": "OK",
                "detections": [], "stale": False,
            }),
            ("unknown result state", {
                "kind": EV_FRAME_RESULT, "frame_id": 2, "state": "BROKEN",
                "detections": [], "stale": False,
            }),
            ("nonboolean stale", {
                "kind": EV_FRAME_RESULT, "frame_id": 2, "state": "OK",
                "detections": [], "stale": "false",
            }),
            ("nonlist detections", {
                "kind": EV_FRAME_RESULT, "frame_id": 2, "state": "OK",
                "detections": {}, "stale": False,
            }),
            ("unconvertible dropped_frames", {
                "kind": EV_FRAME_ERROR, "frame_id": 2,
                "dropped_frames": "unknown",
            }),
            ("boolean monotonic timestamp", {
                "kind": EV_TICK, "t_input_ns": True,
            }),
        )
        for label, malformed in malformed_events:
            for session_id in ("current-session", "new-session"):
                with self.subTest(case=label, session_id=session_id):
                    core = GestureInteractionCore(self.pack)
                    core.step(self._target_event(1, 100, "current-session"))
                    core.state = "STABLE"
                    core.window_match_count = 4
                    core.step_anomaly = True
                    before = self._step_snapshot(core)
                    event = {**malformed, "session_id": session_id}
                    if "t_input_ns" not in event:
                        event["t_input_ns"] = 101

                    with self.assertRaises(CoreInputError):
                        core.step(event)

                    self.assertEqual(self._step_snapshot(core), before)

    def test_nonmapping_step_input_is_rejected_without_state_change(self):
        core = GestureInteractionCore(self.pack)
        core.step(self._target_event(1, 100, "current-session"))
        core.step_anomaly = True
        before = self._step_snapshot(core)

        with self.assertRaisesRegex(CoreInputError, "事件必须为对象"):
            core.step(None)

        self.assertEqual(self._step_snapshot(core), before)

    def test_invalid_detection_scalars_are_counted_without_throwing(self):
        events = (
            ("unrepresentably large score", lambda event: event["detections"][0].update(score=10 ** 5000)),
            ("unconvertible source_order", lambda event: event["detections"][0].update(source_order="unknown")),
        )
        for label, mutate in events:
            with self.subTest(field=label):
                core = GestureInteractionCore(self.pack)
                event = self._target_event(1, 100, "current-session")
                mutate(event)

                result = core.step(event)

                self.assertEqual(result["log"]["input_state"], "INVALID")
                self.assertEqual(core.counters["invalid"], 1)
                self.assertIsNone(core.current_target)

    def test_source_order_enforces_nonnegative_int32_domain(self):
        for source_order in (0, 0x7FFFFFFF):
            with self.subTest(source_order=source_order):
                core = GestureInteractionCore(self.pack)
                event = self._target_event(1, 100, "current-session")
                event["detections"][0]["source_order"] = source_order

                result = core.step(event)

                self.assertEqual(result["log"]["input_state"], "OK")
                self.assertEqual(core.counters["invalid"], 0)

        for label, source_order in (
            ("boolean", True),
            ("float", 1.0),
            ("string", "1"),
            ("negative", -1),
            ("past signed int32 maximum", 0x80000000),
            ("large integer", 10 ** 5000),
        ):
            with self.subTest(case=label):
                core = GestureInteractionCore(self.pack)
                event = self._target_event(1, 100, "current-session")
                event["detections"][0]["source_order"] = source_order

                result = core.step(event)

                self.assertEqual(result["log"]["input_state"], "INVALID")
                self.assertEqual(core.counters["invalid"], 1)
                self.assertIsNone(core.current_target)

    def test_frame_id_enforces_stage4_uint32_domain(self):
        for frame_id in (0, 0xFFFFFFFE, 0xFFFFFFFF):
            with self.subTest(frame_id=frame_id):
                core = GestureInteractionCore(self.pack)
                result = core.step(self._target_event(frame_id, 100, "current-session"))

                self.assertEqual(result["log"]["input_state"], "OK")
                self.assertEqual(core.last_frame_id, frame_id)
                self.assertEqual(core.counters["invalid"], 0)

        for label, frame_id in (
            ("negative", -1),
            ("past uint32 maximum", 0x1_0000_0000),
            ("boolean", True),
            ("float", 1.0),
            ("huge integer", 10 ** 5000),
        ):
            with self.subTest(case=label):
                core = GestureInteractionCore(self.pack)
                core.step(self._target_event(1, 100, "current-session"))
                before = self._step_snapshot(core)

                with self.assertRaisesRegex(CoreInputError, "frame_id 非法（需为 uint32）"):
                    core.step(self._target_event(frame_id, 101, "current-session"))

                self.assertEqual(self._step_snapshot(core), before)

    def test_huge_score_duplicate_still_uses_b22_conflict_classification(self):
        core = GestureInteractionCore(self.pack)
        first = self._target_event(1, 100, "current-session")
        core.step(first)

        conflicting_duplicate = self._target_event(1, 101, "current-session")
        conflicting_duplicate["detections"][0]["score"] = 10 ** 5000
        result = core.step(conflicting_duplicate)

        self.assertEqual(result["log"]["event_kind"], "E_FRAME_CONFLICT")
        self.assertEqual(core.counters["conflict_frames"], 1)
        self.assertEqual(core.counters["invalid"], 0)


if __name__ == "__main__":
    unittest.main()
