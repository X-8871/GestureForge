"""阶段6动作 ACK 边界的离线回归。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage6.s6_core import EV_TICK, CoreInputError, GestureInteractionCore
from src.stage6.s6_params import ParamPack
from src.stage6.s6_receipts import (
    ActionReceiptBoundary,
    ActionReceiptBoundaryError,
    ConflictingActionAckError,
    ReceiptClockError,
    UntrackedActionAckError,
)


class S6CReceiptBoundaryTests(unittest.TestCase):
    """覆盖 ACK 去重、冲突、显式时钟和异常边界。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.pack = ParamPack(
            ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
            project_root=ROOT,
        )

    @classmethod
    def _ack_core(cls) -> GestureInteractionCore:
        core = GestureInteractionCore(cls.pack)
        core.session_id = "s6c-ack-session"
        core.state = "TRIGGERED"
        core.current_target = {"class_id": 0}
        return core

    @staticmethod
    def _observed_ack(action_id: str = "opaque-action-1") -> dict:
        return {
            "action_id": action_id,
            "action_type": "A_SWITCH_UI",
            "target_id": "UI_MENU",
            "submit_result": "success",
            "effective_result": "observed",
            "t_submit_ns": 10,
            "t_effective_ns": 11,
            "visible_state_change": True,
        }

    def test_exact_duplicate_ignores_external_receive_time_only(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = self._observed_ack()

        first = boundary.deliver(ack, received_at_ns=100)
        duplicate = boundary.deliver(dict(reversed(list(ack.items()))), received_at_ns=105)

        self.assertEqual(first["status"], "CORE_ACK_RECORDED")
        self.assertEqual(duplicate["status"], "CORE_ACK_DUPLICATE_IGNORED")
        self.assertTrue(duplicate["core_log"]["duplicate_ack_ignored"])
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.counters["action_effective"], 1)
        self.assertEqual(core.t_last_submit_ns, 10)
        self.assertEqual(boundary.last_received_at_ns, 105)

    def test_same_action_id_business_conflict_fails_before_core_mutation(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        boundary.deliver(self._observed_ack(), received_at_ns=100)
        before = (dict(core.counters), core.state, core.t_last_submit_ns, len(core.action_log))

        conflict = self._observed_ack()
        conflict["effective_result"] = "unobserved"
        conflict.pop("t_effective_ns")
        with self.assertRaises(ConflictingActionAckError):
            boundary.deliver(conflict, received_at_ns=101)

        self.assertEqual(
            (dict(core.counters), core.state, core.t_last_submit_ns, len(core.action_log)),
            before,
        )
        self.assertEqual(boundary.last_received_at_ns, 101)

    def test_unobserved_success_is_not_promoted_to_effective_on_duplicate(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = {
            "action_id": "unobserved-1",
            "submit_result": "success",
            "effective_result": "unobserved",
            "t_submit_ns": 20,
            "t_effective_ns": None,
        }

        first = boundary.deliver(ack, received_at_ns=200)
        duplicate = boundary.deliver(ack, received_at_ns=201)

        self.assertEqual(first["status"], "CORE_ACK_RECORDED")
        self.assertEqual(duplicate["status"], "CORE_ACK_DUPLICATE_IGNORED")
        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertEqual(core.counters["action_effective"], 0)
        self.assertEqual(core.counters["unobserved"], 1)
        self.assertEqual(core.counters["false_actions"], 1)
        self.assertIsNone(core.action_log[0].get("t_effective_ns"))

    def test_failed_submission_does_not_set_cooldown_and_duplicate_counts_once(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = {
            "action_id": "failed-1",
            "submit_result": "fail",
            "effective_result": "unobserved",
            "t_submit_ns": 30,
            "t_effective_ns": None,
        }

        boundary.deliver(ack, received_at_ns=300)
        duplicate = boundary.deliver(ack, received_at_ns=301)

        self.assertEqual(duplicate["status"], "CORE_ACK_DUPLICATE_IGNORED")
        self.assertEqual(core.counters["action_submitted"], 0)
        self.assertEqual(core.counters["false_actions"], 1)
        self.assertIsNone(core.t_last_submit_ns)

    def test_missing_receive_clock_is_rejected_without_core_call(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)

        with self.assertRaises(ReceiptClockError):
            boundary.deliver(self._observed_ack())

        self.assertEqual(core.counters["action_submitted"], 0)
        self.assertEqual(core.action_log, [])
        self.assertIsNone(boundary.last_received_at_ns)

    def test_out_of_order_receive_clock_is_rejected_without_core_call(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        boundary.deliver(self._observed_ack(), received_at_ns=400)
        second = self._observed_ack("opaque-action-2")

        with self.assertRaises(ReceiptClockError):
            boundary.deliver(second, received_at_ns=399)

        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertNotIn("opaque-action-2", core._seen_action_ack_ids)
        self.assertEqual(boundary.last_received_at_ns, 400)
        boundary.deliver(second, received_at_ns=401)
        self.assertEqual(core.counters["action_submitted"], 2)

    def test_core_rejects_missing_business_clock_without_poisoning_action_id(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        malformed = self._observed_ack("clock-missing")
        malformed.pop("t_submit_ns")

        with self.assertRaises(CoreInputError):
            boundary.deliver(malformed, received_at_ns=500)

        self.assertNotIn("clock-missing", core._seen_action_ack_ids)
        self.assertEqual(core.counters["action_submitted"], 0)
        corrected = self._observed_ack("clock-missing")
        boundary.deliver(corrected, received_at_ns=501)
        self.assertIn("clock-missing", core._seen_action_ack_ids)
        self.assertEqual(core.counters["action_effective"], 1)

    def test_core_rejects_observed_ack_without_effective_time(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        malformed = self._observed_ack("effective-clock-missing")
        malformed.pop("t_effective_ns")

        with self.assertRaises(CoreInputError):
            boundary.deliver(malformed, received_at_ns=550)

        self.assertNotIn("effective-clock-missing", core._seen_action_ack_ids)
        self.assertEqual(core.counters["action_submitted"], 0)

    def test_non_finite_payload_is_rejected_before_core_call(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        malformed = self._observed_ack("non-finite")
        malformed["diagnostic"] = float("nan")

        with self.assertRaises(ActionReceiptBoundaryError):
            boundary.deliver(malformed, received_at_ns=600)

        self.assertEqual(core.action_log, [])
        self.assertEqual(core.counters["action_submitted"], 0)
        self.assertNotIn("non-finite", core._seen_action_ack_ids)

        malformed_text = self._observed_ack("invalid-unicode")
        malformed_text["diagnostic"] = chr(0xD800)
        with self.assertRaises(ActionReceiptBoundaryError):
            boundary.deliver(malformed_text, received_at_ns=601)
        self.assertEqual(core.action_log, [])
        self.assertNotIn("invalid-unicode", core._seen_action_ack_ids)

    def test_non_string_nested_key_and_cycle_are_rejected(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        valid = self._observed_ack("nested-key")
        valid["context"] = {"1": "value"}
        boundary.deliver(valid, received_at_ns=650)

        aliased = self._observed_ack("nested-key")
        aliased["context"] = {1: "value"}
        with self.assertRaises(ActionReceiptBoundaryError):
            boundary.deliver(aliased, received_at_ns=651)

        cyclic = self._observed_ack("cyclic")
        cycle: list[object] = []
        cycle.append(cycle)
        cyclic["diagnostic"] = cycle
        with self.assertRaises(ActionReceiptBoundaryError):
            boundary.deliver(cyclic, received_at_ns=652)

        self.assertEqual(core.counters["action_submitted"], 1)
        self.assertNotIn("cyclic", core._seen_action_ack_ids)

    def test_suppression_ack_without_id_is_not_deduplicated_by_boundary(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = {
            "action_id": None,
            "suppression": "S_DEDUP",
            "submit_result": None,
            "effective_result": None,
            "t_submit_ns": None,
            "t_effective_ns": None,
            "reason": "离线验证的幂等抑制",
        }

        first = boundary.deliver(ack, received_at_ns=700)
        second = boundary.deliver(ack, received_at_ns=701)

        self.assertEqual(first["status"], "CORE_SUPPRESSION_ACK_RECORDED")
        self.assertEqual(second["status"], "CORE_SUPPRESSION_ACK_RECORDED")
        self.assertEqual(len(core.action_log), 2)
        self.assertEqual(core.counters["action_submitted"], 0)

    def test_boundary_retains_action_id_fingerprint_across_core_session_reset(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = self._observed_ack("persistent-action-id")
        boundary.deliver(ack, received_at_ns=800)

        reset_log = boundary.reset_session("next-session")
        self.assertEqual(reset_log["log"]["transition"], "RESET")
        duplicate = boundary.deliver(ack, received_at_ns=801)
        self.assertEqual(duplicate["status"], "CORE_ACK_DUPLICATE_IGNORED")
        self.assertEqual(core.counters["action_submitted"], 0)

        conflict = dict(ack)
        conflict["target_id"] = "UI_STATS"
        with self.assertRaises(ConflictingActionAckError):
            boundary.deliver(conflict, received_at_ns=802)
        self.assertEqual(core.counters["action_submitted"], 0)

    def test_direct_reset_bypass_fails_closed_without_boundary_mutation(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        boundary.deliver(self._observed_ack("reset-bypass"), received_at_ns=810)

        core.reset_session("bypassed-reset")
        core_after_bypass = (
            dict(core.counters), core.state, core.session_id, core.last_t_ns,
            core.t_last_submit_ns, list(core.action_log), set(core._seen_action_ack_ids),
        )
        boundary_after_bypass = (
            boundary.last_received_at_ns, list(boundary.delivery_log),
            dict(boundary._business_by_action_id), boundary._expected_core_history,
        )

        with self.assertRaisesRegex(UntrackedActionAckError, "截断或复位"):
            boundary.deliver(self._observed_ack("after-reset-bypass"), received_at_ns=811)

        self.assertEqual(
            (
                dict(core.counters), core.state, core.session_id, core.last_t_ns,
                core.t_last_submit_ns, list(core.action_log), set(core._seen_action_ack_ids),
            ),
            core_after_bypass,
        )
        self.assertEqual(
            (
                boundary.last_received_at_ns, list(boundary.delivery_log),
                dict(boundary._business_by_action_id), boundary._expected_core_history,
            ),
            boundary_after_bypass,
        )

    def test_direct_same_payload_ack_bypass_is_detected_transactionally(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = self._observed_ack("same-payload-bypass")
        boundary.deliver(ack, received_at_ns=820)

        core.note_action_ack(ack)
        core_after_bypass = (
            dict(core.counters), core.state, core.t_last_submit_ns,
            list(core.action_log), set(core._seen_action_ack_ids),
        )
        boundary_after_bypass = (
            boundary.last_received_at_ns, list(boundary.delivery_log),
            dict(boundary._business_by_action_id), boundary._expected_core_history,
        )

        with self.assertRaisesRegex(UntrackedActionAckError, "相同业务内容"):
            boundary.deliver(ack, received_at_ns=821)

        self.assertEqual(
            (
                dict(core.counters), core.state, core.t_last_submit_ns,
                list(core.action_log), set(core._seen_action_ack_ids),
            ),
            core_after_bypass,
        )
        self.assertEqual(
            (
                boundary.last_received_at_ns, list(boundary.delivery_log),
                dict(boundary._business_by_action_id), boundary._expected_core_history,
            ),
            boundary_after_bypass,
        )

    def test_direct_conflicting_payload_ack_bypass_is_detected_transactionally(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        ack = self._observed_ack("different-payload-bypass")
        boundary.deliver(ack, received_at_ns=830)

        bypass = dict(ack)
        bypass["target_id"] = "UI_STATS"
        core.note_action_ack(bypass)
        core_after_bypass = (
            dict(core.counters), core.state, core.t_last_submit_ns,
            list(core.action_log), set(core._seen_action_ack_ids),
        )
        boundary_after_bypass = (
            boundary.last_received_at_ns, list(boundary.delivery_log),
            dict(boundary._business_by_action_id), boundary._expected_core_history,
        )

        with self.assertRaisesRegex(UntrackedActionAckError, "不同或不可核验"):
            boundary.deliver(ack, received_at_ns=831)

        self.assertEqual(
            (
                dict(core.counters), core.state, core.t_last_submit_ns,
                list(core.action_log), set(core._seen_action_ack_ids),
            ),
            core_after_bypass,
        )
        self.assertEqual(
            (
                boundary.last_received_at_ns, list(boundary.delivery_log),
                dict(boundary._business_by_action_id), boundary._expected_core_history,
            ),
            boundary_after_bypass,
        )

    def test_non_ack_core_log_noise_does_not_look_like_ack_bypass(self) -> None:
        core = self._ack_core()
        boundary = ActionReceiptBoundary(core)
        boundary.deliver(self._observed_ack("before-tick-noise"), received_at_ns=840)

        core.step({"kind": EV_TICK, "session_id": core.session_id, "t_input_ns": 12})
        self.assertEqual(len(core.action_log), 1)
        accepted = boundary.deliver(
            self._observed_ack("after-tick-noise"),
            received_at_ns=841,
        )

        self.assertEqual(accepted["status"], "CORE_ACK_RECORDED")
        self.assertEqual(core.counters["action_submitted"], 2)
        self.assertEqual(len(core.action_log), 2)

    def test_constructor_rejects_late_attach_and_untracked_core_ack(self) -> None:
        core = self._ack_core()
        core.note_action_ack(self._observed_ack("preexisting-action"))
        with self.assertRaises(ActionReceiptBoundaryError):
            ActionReceiptBoundary(core)

        fresh_core = self._ack_core()
        boundary = ActionReceiptBoundary(fresh_core)
        fresh_core.note_action_ack(self._observed_ack("bypassed-action"))
        with self.assertRaises(UntrackedActionAckError):
            boundary.deliver(
                self._observed_ack("bypassed-action"),
                received_at_ns=900,
            )
        self.assertEqual(fresh_core.counters["action_submitted"], 1)


if __name__ == "__main__":
    unittest.main()
