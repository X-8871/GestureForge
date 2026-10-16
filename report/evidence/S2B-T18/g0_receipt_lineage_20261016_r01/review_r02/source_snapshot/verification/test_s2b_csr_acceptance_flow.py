"""T18固定CSR流程的离线顺序与失败门测试。"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

from verification import s2b_csr_acceptance_flow as flow


class FixedCsrFlowOrderTests(unittest.TestCase):
    def test_busy_frame1_then_new_sequence_frame0_precedes_abort(self):
        with tempfile.TemporaryDirectory(prefix="s2b_csr_flow_order_") as temp:
            root = Path(temp)
            t20 = root / "report/evidence/S2B-T20"
            t20.mkdir(parents=True)
            run_dir = root / "report/evidence/S2B-T18/run"
            run_dir.parent.mkdir(parents=True)
            trace = []
            wire = SimpleNamespace(last_sequence=0, last_run_frame=None, failed=False, abort_pending=None)

            class Controller:
                bindings = {}
                failed = False

                def stable_csr(self, label):
                    trace.append("scene:" + label)
                    return {offset: 0 for offset in flow.csr.OFFSETS}

                def gate(self, both):
                    trace.append("gate:" + str(both))

                def state(self, cpu):
                    return "Stopped"

            controller = Controller()
            request_counter = {"value": 0}

            class AcceptanceRunner:
                def __init__(self, session, directory, admission):
                    self.wire, self.run = session, directory
                    self.run.mkdir()
                    self.record = {"status": "IN_PROGRESS"}

                def send(self, request, header, payload, source):
                    self.wire.last_sequence = request.sequence

                def receive(self, request, index):
                    pass

                def run_input(self, row, sequence, frame, repeat, core, drain, phase):
                    self.wire.last_sequence = sequence
                    self.wire.last_run_frame = frame
                    trace.append((phase, sequence, frame))

                def finish(self, status):
                    result = {"status": status}
                    (self.run / "acceptance_result.json").write_text("{}", encoding="utf-8")
                    return result

            def make_request(op, sequence, frame, payload, **kwargs):
                request_counter["value"] += 1
                return SimpleNamespace(op=op, sequence=sequence, frame=frame), b"header"

            def busy_stage(_controller, session, binding, run_path, **kwargs):
                self.assertEqual(session.last_run_frame, 0)
                self.assertEqual(session.last_sequence, 2)
                trace.append(("busy_observer", session.last_sequence + 1, 1))
                session.last_sequence += 1
                session.last_run_frame = 1
                run_path.mkdir()
                (run_path / "busy_result.json").write_text("{}", encoding="utf-8")
                return {"status": "PASS_BUSY_START_REJECTION_AND_GOLD"}

            def abort_stage(_controller, session, binding, preparation, run_path, **kwargs):
                self.assertEqual(session.last_run_frame, 0)
                self.assertEqual(session.last_sequence, 4)
                self.assertEqual([row for row in trace if isinstance(row, tuple)][-1],
                                 ("csr_reaccept", 4, 0))
                trace.append("abort_after_frame0")
                run_path.mkdir()
                (run_path / "csr_result.json").write_text("{}", encoding="utf-8")
                return ({"status": "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE"}, {"status": "PASS"})

            def static_stage(_controller, session, binding, run_path, **kwargs):
                self.assertLess(trace.index("abort_after_frame0"),
                                trace.index("scene:t18.csr_scope.before_static_matrix"))
                trace.append("static_last")
                run_path.mkdir()
                (run_path / "csr_result.json").write_text("{}", encoding="utf-8")
                rows = [{"name": "parameter", "status": "PASS"},
                        {"name": "busy_start", "status": "BLOCKED"}]
                return ({"status": "SCENARIO_RESULTS_SAVED_NOT_STAGE_ACCEPTANCE", "scenarios": rows},
                        {offset: 0 for offset in flow.csr.OFFSETS})

            config = {
                "run_id": "order_test", "source_commit": "a" * 40,
                "preparation": {"path": "prep.json", "sha256": "1" * 64},
                "build_details": {"path": "build.json", "sha256": "2" * 64},
                "visibility_proof": {"path": "proof.json", "sha256": "3" * 64},
                "visibility_review": {"path": "review.json", "sha256": "4" * 64},
                "final_platform_manifest": {"path": "manifest.json", "sha256": "5" * 64},
                "final_review": {"path": "final.json", "sha256": "6" * 64},
                "core_timeout": 100, "drain_timeout": 200,
            }
            checked = {"run_dir": run_dir}
            apis = SimpleNamespace(acceptance=SimpleNamespace(), transport=flow.transport)
            plan = {"weights": {"path": "weights.bin", "sha256": "7" * 64},
                    "rows": [{"input": {"path": "input.bin", "sha256": "8" * 64},
                              "reference": {"path": "reference.json", "sha256": "9" * 64}}]}
            def read_bound(item):
                if item == config["preparation"]:
                    import json
                    return Path("prep.json"), json.dumps(plan).encode("utf-8")
                return Path("weights.bin"), b"weights"

            with mock.patch.object(flow, "ROOT", root), \
                    mock.patch.object(flow.transport, "exact_path", side_effect=lambda path, kind="file": Path(path)), \
                    mock.patch.object(flow.transport, "make_request", side_effect=make_request), \
                    mock.patch.object(flow.model, "read_bound", side_effect=read_bound), \
                    mock.patch.object(flow.model, "validate_plan"), \
                    mock.patch.object(flow.model, "AcceptanceRunner", AcceptanceRunner), \
                    mock.patch.object(flow.csr, "checked_snapshot", side_effect=lambda snapshot: snapshot), \
                    mock.patch.object(flow.csr, "idle"), \
                    mock.patch.object(flow.busy, "execute_busy_start", side_effect=busy_stage), \
                    mock.patch.object(flow.csr, "execute_abort_recovery", side_effect=abort_stage), \
                    mock.patch.object(flow.csr, "execute_static_matrix", side_effect=static_stage):
                result = flow.execute(controller, wire, config, checked, apis, {"status": "ADMITTED"})

            self.assertEqual(result["status"], "PASS_CSR_RECOVERY_SCOPE_ONLY")
            frames = [row for row in trace if isinstance(row, tuple)]
            self.assertEqual(frames, [("csr_seed", 2, 0), ("busy_observer", 3, 1),
                                      ("csr_reaccept", 4, 0)])
            self.assertLess(trace.index(("busy_observer", 3, 1)), trace.index(("csr_reaccept", 4, 0)))
            self.assertLess(trace.index(("csr_reaccept", 4, 0)), trace.index("abort_after_frame0"))
            self.assertEqual([row["name"] for row in result["stages"]], [
                "sample000_seed_frame0", "real_busy_start_slverr_last_reject",
                "sample000_reaccept_frame0", "wait_final_ack_sample000_recovery",
                "static_csr_negative_matrix"])

    def test_busy_failure_preserves_t20_output_and_writes_failed_index(self):
        import json

        with tempfile.TemporaryDirectory(prefix="s2b_csr_flow_failure_") as temp:
            root = Path(temp)
            t20 = root / "report/evidence/S2B-T20"
            t20.mkdir(parents=True)
            run_dir = root / "report/evidence/S2B-T18/failure_run"
            run_dir.parent.mkdir(parents=True)
            wire = SimpleNamespace(last_sequence=0, last_run_frame=None, failed=False, abort_pending=None)

            class Controller:
                bindings = {}
                failed = False

                def stable_csr(self, label):
                    return {offset: 0 for offset in flow.csr.OFFSETS}

            class AcceptanceRunner:
                def __init__(self, session, directory, admission):
                    self.wire, self.run = session, directory
                    self.run.mkdir()
                    self.record = {}

                def send(self, request, header, payload, source):
                    self.wire.last_sequence = request.sequence

                def receive(self, request, index):
                    pass

                def run_input(self, row, sequence, frame, repeat, core, drain, phase):
                    self.wire.last_sequence = sequence
                    self.wire.last_run_frame = frame

                def finish(self, status):
                    (self.run / "acceptance_result.json").write_text("{}", encoding="utf-8")
                    return {"status": status}

            plan = {"weights": {"path": "weights.bin", "sha256": "7" * 64},
                    "rows": [{"input": {"path": "input.bin", "sha256": "8" * 64},
                              "reference": {"path": "reference.json", "sha256": "9" * 64}}]}
            config = {"run_id": "failure_test", "source_commit": "a" * 40,
                      "preparation": {"path": "prep.json", "sha256": "1" * 64},
                      "build_details": {"path": "build.json", "sha256": "2" * 64},
                      "visibility_proof": {"path": "proof.json", "sha256": "3" * 64},
                      "visibility_review": {"path": "review.json", "sha256": "4" * 64},
                      "final_platform_manifest": {"path": "manifest.json", "sha256": "5" * 64},
                      "final_review": {"path": "final.json", "sha256": "6" * 64},
                      "core_timeout": 100, "drain_timeout": 200}

            def read_bound(item):
                if item == config["preparation"]:
                    return Path("prep.json"), json.dumps(plan).encode("utf-8")
                return Path("weights.bin"), b"weights"

            def make_request(op, sequence, frame, payload, **kwargs):
                return SimpleNamespace(op=op, sequence=sequence, frame=frame), b"header"

            def failed_busy(_controller, session, binding, run_path, **kwargs):
                session.last_sequence += 1
                session.last_run_frame = 1
                run_path.mkdir()
                raw_path = run_path / "busy_result.json"
                raw_path.write_text('{"status":"FAIL_LATCHED"}', encoding="utf-8")
                raise RuntimeError("injected busy observer failure")

            apis = SimpleNamespace(acceptance=SimpleNamespace(), transport=flow.transport)
            with mock.patch.object(flow, "ROOT", root), \
                    mock.patch.object(flow.transport, "exact_path", side_effect=lambda path, kind="file": Path(path)), \
                    mock.patch.object(flow.transport, "make_request", side_effect=make_request), \
                    mock.patch.object(flow.model, "read_bound", side_effect=read_bound), \
                    mock.patch.object(flow.model, "validate_plan"), \
                    mock.patch.object(flow.model, "AcceptanceRunner", AcceptanceRunner), \
                    mock.patch.object(flow.csr, "checked_snapshot", side_effect=lambda snapshot: snapshot), \
                    mock.patch.object(flow.csr, "idle"), \
                    mock.patch.object(flow.busy, "execute_busy_start", side_effect=failed_busy):
                result = flow.execute(Controller(), wire, config, {"run_dir": run_dir}, apis,
                                      {"status": "ADMITTED"})

            busy_result = t20 / "failure_test_csr_busy_observer/busy_result.json"
            self.assertEqual(result["status"], "FAILED_CSR_RECOVERY_SCOPE_ONLY")
            self.assertEqual(result["error"], "RuntimeError('injected busy observer failure')")
            self.assertTrue((run_dir / "acceptance_result.json").is_file())
            self.assertTrue((run_dir / "delivery_manifest.json").is_file())
            binding = next(item for item in result["t20_outputs"] if Path(item["path"]) == busy_result)
            self.assertEqual(binding["sha256"], flow.transport.digest(busy_result.read_bytes()))
            manifest = json.loads((run_dir / "delivery_manifest.json").read_text(encoding="utf-8"))
            row = next(item for item in manifest["files"] if item["path"].endswith("/busy_result.json"))
            self.assertEqual(row["sha256"], binding["sha256"])
            self.assertEqual(manifest["checks"][0]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
