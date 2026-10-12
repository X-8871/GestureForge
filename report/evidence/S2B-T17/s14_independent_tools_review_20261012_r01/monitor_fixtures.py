"""覆盖当前轮安全读回、消费阻断与独立原生时钟；不启动Vivado或硬件。"""
import copy
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
import guard
import runtime_consumer as consumer
import selftest
import supervisor

W = Path(__file__).absolute().parent
ROWS = []


def write(path, row):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(row, stream, ensure_ascii=False, indent=2); stream.write("\n")


def bound(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


class RoundSafety(unittest.TestCase):
    def test_final_six_fields_drift(self):
        for field, value in (("create_time", 99), ("exe", "其他.exe"), ("cwd", "其他"), ("cmdline", ["其他"]), ("ppid", 0)):
            w = selftest.World(); m, root = selftest.monitor(w)
            original = m.round_chain
            def change(item, root, table):
                result = original(item, root, table)
                w.nodes[200][field] = value
                return result
            m.round_chain = change
            with patch.object(guard.psutil, "Process", w.process):
                members, unknown, exits = m.collect(root)
            self.assertTrue(unknown or exits, field)
            if field == "create_time":
                self.assertTrue(exits)
                self.assertFalse(any(row["pid"] == 200 and row["create_time"] == 2 for row in members))
            else:
                self.assertFalse(m.collection_observation["closed"], field)
            ROWS.append({"case": "final_readback_"+field, "result": "PASS", "mock": True})

    def test_final_disappearance_confirmed(self):
        w = selftest.World(); m, root = selftest.monitor(w); original = m.round_chain
        def disappear(item, root, table):
            result = original(item, root, table); w.nodes.pop(200, None); return result
        m.round_chain = disappear
        with patch.object(guard.psutil, "Process", w.process):
            members, unknown, exits = m.collect(root)
        self.assertFalse(unknown); self.assertEqual(exits[0]["status"], "ABSENT")
        self.assertEqual([item["pid"] for item in members], [100])

    def test_final_ancestor_change(self):
        w = selftest.World(); w.make(300, 3, 200, 30); m, root = selftest.monitor(w); original = m.round_chain
        def change(item, root, table):
            result = original(item, root, table)
            if item["pid"] == 300: w.nodes[200]["ppid"] = 0
            return result
        m.round_chain = change
        with patch.object(guard.psutil, "Process", w.process):
            self.assertTrue(m.collect(root)[1])


class ConsumerSafety(unittest.TestCase):
    def good(self):
        row = dict(pid=100, create_time=1, exe="模拟", cwd="模拟", cmdline=["模拟"], ppid=0)
        journal = [{"kind": "READY", "guard_identity": row}, {"kind": "LIVE", "identity": row, "monotonic_seconds": time.monotonic()}]
        sample = {"members": [row], "alerts": [], "uncertain": [], "collection_observation": {"closed": True}, "sample_ended_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "tree_rss_bytes": 20, "available_ram_bytes": 512*1024**2, "c_disk_free_bytes": 8*1024**3}
        return journal, [sample], row, row, [{"mtime_age_seconds": 0}, {"mtime_age_seconds": 0}], 5

    def test_live_and_target_miss_not_hard_gap(self):
        args = list(self.good()); args[-1] = 5.02
        self.assertEqual(consumer.evaluate(*args), [])

    def test_hard_gap(self):
        args = list(self.good()); args[-1] = 10.0001
        self.assertIn("CONSUMER_GAP_GT_10S", consumer.evaluate(*args))

    def test_terminal_uncertain_unclosed(self):
        for mode in ("TERMINAL", "uncertain", "unclosed"):
            args = list(self.good())
            if mode == "TERMINAL": args[0].append({"kind": mode})
            elif mode == "uncertain": args[1][0]["uncertain"] = [{"reason": "UNKNOWN"}]
            else: args[1][0]["collection_observation"]["closed"] = False
            self.assertTrue(consumer.evaluate(*args), mode)

    def test_six_fields_and_pid_reuse(self):
        for key in consumer.KEYS:
            args = list(self.good()); args[0][-1]["identity"] = copy.deepcopy(args[3]); args[0][-1]["identity"][key] = "变化"
            self.assertIn("SUPERVISION_SIX_FIELD_IDENTITY_MISMATCH", consumer.evaluate(*args), key)

    def test_thresholds_unknown_and_stale(self):
        for field, value in (("tree_rss_bytes", 6*1024**3+1), ("available_ram_bytes", 512*1024**2-1), ("c_disk_free_bytes", 8*1024**3-1), ("tree_rss_bytes", None)):
            args = list(self.good()); args[1][0][field] = value
            self.assertTrue(consumer.evaluate(*args), field)
        args = list(self.good()); args[4][0]["mtime_age_seconds"] = 10.0001
        self.assertTrue(consumer.evaluate(*args))

    def test_stop_identity_unverifiable(self):
        row = self.good()[2]
        with patch.object(consumer, "identity", side_effect=guard.psutil.AccessDenied(100)):
            result = consumer.request_stop(row, row, str(W/"nonexistent"))
        self.assertEqual(result["status"], "STOP_REJECTED_IDENTITY_OR_PATH")
        self.assertEqual(result["heavy_terminal"], "UNKNOWN")

    def test_pending_source_refused(self):
        import compat_pins
        for pnr in (False, True):
            with self.assertRaisesRegex(ValueError, "缺ROOT最终commit"):
                compat_pins.require_ready(pnr)
        self.assertIsNone(compat_pins.SOURCE_COMMIT)
        self.assertFalse(compat_pins.PROJECT.exists())


def native_canary():
    directory = W/"native_consumer_canary_r03"; directory.mkdir()
    owned = []; handles = []; logs = []
    def launch(argv, name):
        so = (directory/(name+".stdout.bin")).open("xb"); se = (directory/(name+".stderr.bin")).open("xb"); logs.extend([so, se])
        child = subprocess.Popen(argv, cwd=W, stdout=so, stderr=se)
        handles.append(child); owned.append(supervisor.identity(child.pid)); return child
    try:
        root_child = launch([sys.executable, "-X", "utf8", "-B", "-c", "import time; time.sleep(40)"], "root")
        binding = dict(owned[-1], allowed_run_dirs=[str(W)], fixture_test=True, source_commit="467463757158aed80d6f75afadff6a8458614a29", run_id="s14_native_consumer_fixture", max_seconds=35)
        write(directory/"binding.json", binding); write(directory/"plan.json", consumer.LIMITS)
        sup_child = launch([sys.executable, "-X", "utf8", "-B", str(W/"fixture_supervision.py"), str(directory)], "supervisor")
        deadline = time.monotonic()+8
        journal_path = directory/"supervision"/"supervision.jsonl"
        ready = None
        while ready is None:
            if sup_child.poll() is not None or time.monotonic()>deadline: raise RuntimeError("轻量监督未READY")
            if journal_path.exists():
                raw = journal_path.read_bytes(); rows = [json.loads(x) for x in raw[:raw.rfind(b"\n")+1].splitlines() if x]
                ready = next((row for row in rows if row["kind"] == "READY"), None)
            time.sleep(.05)
        guard_owned = ready["guard_identity"]; owned.append(guard_owned)
        config = {"binding": bound(directory/"binding.json"), "plan": bound(directory/"plan.json"), "guard_identity": guard_owned,
                  "supervision_dir": str(directory/"supervision"), "output_dir": str(directory/"consumer"),
                  "tool_bindings": [bound(W/"guard.py"), bound(W/"supervisor.py"), bound(W/"runtime_consumer.py")]}
        write(directory/"config.json", config)
        child, handoff = consumer.launch(str(directory/"config.json"), str(directory/"consumer.stdout.bin"), str(directory/"consumer.stderr.bin"))
        handles.append(child); owned.append(handoff["identity"]); write(directory/"handoff.json", handoff)
        # 本夹具驱动线程阻塞11秒，消费进程仍按自身原生时钟运行。
        wait_started = time.monotonic(); time.sleep(11); wait_ended = time.monotonic()
        rows, _ = consumer.complete(str(directory/"consumer"/"consumption.jsonl"))
        assert len(rows)>=3 and all(row["status"] == "CONSUMED_LIVE_READY" for row in rows), rows
        assert rows[-1]["monotonic_seconds"] < wait_ended and rows[-1]["monotonic_seconds"] > wait_started
        stop = consumer.request_stop(guard_owned, binding, str(directory/"supervision"/"guard"))
        assert stop["status"] == "REQUEST_WRITTEN", stop
        sup_code = sup_child.wait(timeout=8); root_code = root_child.wait(timeout=3); consumer_code = child.wait(timeout=8)
        assert sup_code == 2 and consumer_code == 2
        receipt = json.loads((directory/"consumer"/"consumer_receipt.json").read_text(encoding="utf-8"))
        assert receipt["blocked_latched"] is True
        write(directory/"native_canary_result.json", {"status": "PASS_G1_FIXTURE_ONLY", "driver_wait_gap_seconds": wait_ended-wait_started,
              "live_consumption_rows_during_driver_wait": len(rows), "actual_gaps_seconds": [row["actual_gap_seconds"] for row in rows],
              "guard_native_exit_code": json.loads((directory/"supervision"/"supervisor_receipt.json").read_text(encoding="utf-8"))["child_native_exit_code"],
              "supervisor_native_exit_code": sup_code, "consumer_native_exit_code": consumer_code, "root_canary_native_exit_code": root_code,
              "stop_request": stop, "identities": owned, "actual_ross_wait_executed": False, "heavy_started": False, "hardware_started": False,
              "continuous_peak_bytes": None, "complete_tree_terminal": "NOT_PROVEN"})
    finally:
        for row in reversed(owned):
            try:
                current = supervisor.identity(row["pid"])
                if consumer.same(current, row):
                    process = guard.psutil.Process(row["pid"]); process.terminate(); process.wait(timeout=3)
            except guard.psutil.NoSuchProcess: pass
        for child in handles:
            if child.poll() is None: child.wait(timeout=3)
        for stream in logs: stream.close()
        observations = []
        for row in owned:
            try:
                actual = supervisor.identity(row["pid"]); observations.append({"expected": row, "same_identity_present": consumer.same(actual, row), "actual": actual})
            except guard.psutil.NoSuchProcess: observations.append({"expected": row, "same_identity_present": False, "status": "ABSENT"})
            except guard.psutil.Error as error: observations.append({"expected": row, "same_identity_present": None, "status": "UNKNOWN", "error": repr(error)})
        write(directory/"known_identity_terminal.json", {"observations": observations, "complete_tree_terminal": "NOT_PROVEN"})


if __name__ == "__main__":
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(RoundSafety), unittest.defaultTestLoader.loadTestsFromTestCase(ConsumerSafety)])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful(): raise SystemExit(1)
    native_canary()
    write(W/"monitor_fixture_result.json", {"status": "PASS_G1_ONLY", "mock_methods": result.testsRun, "additional_cases": ROWS, "native_consumer_canaries": 1,
          "real_resource_threshold_canary": "selftest.py:owned_threshold_canary", "ROSS_or_heavy_or_hardware_started": False, "continuous_peak_bytes": None})
