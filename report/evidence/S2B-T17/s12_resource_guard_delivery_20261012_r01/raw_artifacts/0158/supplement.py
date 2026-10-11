"""补充run层RSS/null语义及已核孤儿安全保留，不访问实际目标PID。"""
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import guard
from selftest import W, World, monitor, mock_case, ROWS, sha


class Supplement(unittest.TestCase):
    @mock_case
    def test_exited_after_measured_excluded_final(self, w, m, root):
        def hook(world, pid):
            if world.scans == 2:
                world.nodes.pop(200, None)
        w.hook = hook
        members, uncertain, exits = m.collect(root)
        self.assertFalse(uncertain)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 10)
        self.assertEqual(exits[0]["status"], "ABSENT")
        self.assertEqual(m.collection_observation["scans"], 3)

    @mock_case
    def test_three_scan_exit_not_closed(self, w, m, root):
        def hook(world, pid):
            if world.scans == 1:
                world.make(300, 3, 100, 30)
            if world.scans == 3:
                world.nodes.pop(200, None)
        w.hook = hook
        self.assertEqual(m.collect(root)[1][-1]["reason"], "TREE_RESCAN_NOT_CLOSED")

    @mock_case
    def test_historical_orphan_threshold_retained(self, w, m, root):
        w.make(300, 3, 200, 30)
        members, _, _ = m.collect(root)
        m.last_members.update({(x["pid"], x["create_time"]): x for x in members})
        del w.nodes[200]
        members, uncertain, _ = m.collect(root)
        status, stopped, retained = m.stop_tree(root, members, uncertain, ["模拟阈值"])
        self.assertEqual(status, "BLOCKED")
        self.assertEqual(stopped, [])
        self.assertTrue(any(x["reason"] == "ROOT_RETAINED_FOR_UNCERTAIN_DESCENDANTS" for x in retained))
        self.assertFalse(any(x["kind"] == "TERMINATE_SENT" for x in m.events))

    @mock_case
    def test_root_access_denied_scan_blocked(self, w, m, root):
        w.fail[(100, "exe")] = guard.psutil.AccessDenied(100)
        members, uncertain, _ = m.collect(root)
        self.assertEqual(uncertain[0]["reason"], "TREE_ENUMERATION_FAILED")
        self.assertFalse(m.collection_observation["closed"])

    def run_sample(self, label, denied):
        w = World()
        m, root = monitor(w)
        m.output = W / label
        m.binding.update(source_commit="932051cdacdf02f729d6a7554b07118d05e96aa4", run_id=label, max_seconds=0)
        m.plan = dict(resource_sample_interval_seconds=1, new_run_tree_rss_limit_bytes=6*1024**3,
                      new_run_available_ram_stop_bytes=512*1024**2, minimum_c_disk_free_before_dispatch_bytes=8*1024**3)
        m.last_members[(200, 2)] = dict(w.nodes[200])
        m.validate = lambda: None
        if denied:
            w.fail[(200, "rss_bytes")] = guard.psutil.AccessDenied(200)
        else:
            del w.nodes[200]
        with patch.object(guard.psutil, "Process", w.process), patch.object(guard.psutil,"virtual_memory",lambda: SimpleNamespace(available=4*1024**3)), patch.object(guard.psutil,"disk_usage",lambda path: SimpleNamespace(free=16*1024**3)):
            code = m.run()
        self.assertEqual(code, 3)
        sample = json.loads((m.output / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0])
        receipt = json.loads((m.output / "guard_receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(sample["tree_rss_bytes"], None if denied else 10)
        self.assertEqual(sample["live_measured_rss_sum"], None if denied else 10)
        self.assertEqual(receipt["sampled_peak_tree_rss_bytes"], None if denied else 10)
        self.assertIsNone(receipt["absolute_peak_memory_bytes"])
        self.assertEqual(receipt["reason"], "INCOMPLETE_TREE_IDENTITY" if denied else "GUARD_OBSERVATION_LIMIT_NO_TASK_STOP")
        self.assertEqual(len(sample["confirmed_exits"]), 0 if denied else 1)
        ROWS.append(dict(case=label, result="PASS", simulated_run_native_semantics=code))

    def test_run_confirmed_exit_live_sum_not_null(self):
        self.run_sample("mock_run_confirmed_exit", False)

    def test_run_alive_unknown_null_and_blocked(self):
        self.run_sample("mock_run_alive_unknown", True)

    @mock_case
    def test_readback_immutable_fields_drift(self, w, m, root):
        expected = dict(w.nodes[200])
        for field in ("exe", "cwd", "cmdline", "ppid"):
            old = w.nodes[200][field]
            w.nodes[200][field] = ["漂移"] if field == "cmdline" else 999 if field == "ppid" else "漂移"
            self.assertEqual(m.readback_member(expected)["status"], "IDENTITY_CHANGED")
            w.nodes[200][field] = old

    @mock_case
    def test_birth_success_nosuch_still_same_birth_unknown(self, w, m, root):
        w.fail[(200, "rss_bytes")] = guard.psutil.NoSuchProcess(200)
        result = m.readback_member(dict(w.nodes[200]))
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["confirmation"], "FRESH_PID_STILL_SAME_BIRTH")


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Supplement))
    guard.write_new(W / "supplement_result.json", dict(status="PASS_G1_ONLY" if result.wasSuccessful() else "FAIL",
                    tests=result.testsRun, cases=ROWS, guard_sha256=sha(W / "guard.py"), actual_target_queries=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
