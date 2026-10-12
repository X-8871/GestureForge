"""模拟采样闭合和安全拒绝，并仅运行自行创建的轻量父子夹具。"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

import guard

W = Path(__file__).resolve().parent
ROOT = W.parents[3]
OLD = ROOT / "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/guard.py"
SUP = ROOT / "tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/supervisor.py"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ROWS = []


class World:
    def __init__(self):
        self.nodes = {}
        self.scans = 0
        self.enumerated = []
        self.hook = None
        self.fail = {}
        self.make(100, 1, 0, 10)
        self.make(200, 2, 100, 20)

    def make(self, pid, birth, ppid, rss):
        self.nodes[pid] = dict(pid=pid, create_time=birth, exe="模拟.exe", cwd=str(W),
                               cmdline=["模拟", str(pid)], ppid=ppid, rss_bytes=rss, status="running")

    def process(self, pid=None):
        if pid not in self.nodes:
            raise guard.psutil.NoSuchProcess(pid)
        return Fake(self, pid)


class Fake:
    def __init__(self, world, pid):
        self.world, self.pid = world, pid

    def value(self, key):
        error = self.world.fail.get((self.pid, key))
        if error:
            raise error
        if self.pid not in self.world.nodes:
            raise guard.psutil.NoSuchProcess(self.pid)
        return self.world.nodes[self.pid][key]

    def create_time(self): return self.value("create_time")
    def exe(self): return self.value("exe")
    def cwd(self): return self.value("cwd")
    def cmdline(self): return self.value("cmdline")
    def ppid(self): return self.value("ppid")
    def status(self): return self.value("status")
    def memory_info(self): return type("Memory", (), {"rss": self.value("rss_bytes")})()
    def is_running(self): return self.pid in self.world.nodes

    def children(self, recursive=False):
        self.world.enumerated.append(self.pid)
        if self.pid == 100:
            self.world.scans += 1
        pids, frontier = set(), {self.pid}
        while frontier:
            found = {p for p, row in self.world.nodes.items() if row["ppid"] in frontier} - pids
            pids.update(found)
            if not recursive:
                break
            frontier = found
        result = [Fake(self.world, p) for p in sorted(pids)]
        if self.world.hook:
            self.world.hook(self.world, self.pid)
        return result


def monitor(world):
    row = dict(world.nodes[100], parent=None)
    m = guard.Guard({}, dict(row, allowed_run_dirs=[str(W)]), W / "mock_unused")
    m.initial_root = row
    m.event = lambda kind, **values: m.events.append(dict(kind=kind, **values))
    return m, row


def mock_case(function):
    def run(self):
        w = World()
        m, root = monitor(w)
        with patch.object(guard.psutil, "Process", w.process):
            function(self, w, m, root)
        ROWS.append(dict(case=function.__name__, result="PASS", actual_target_process_queries=False))
    return run


class Semantics(unittest.TestCase):
    @mock_case
    def test_stable_live(self, w, m, root):
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertFalse(exits)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 30)
        self.assertEqual(m.collection_observation["scans"], 2)

    @mock_case
    def test_confirmed_exit_and_next_sample(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        del w.nodes[200]
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertEqual([x["rss_bytes"] for x in members], [10])
        self.assertEqual(exits[0]["status"], "ABSENT")
        self.assertNotIn("rss_bytes", exits[0])
        self.assertEqual(m.collect(root)[2], [])

    @mock_case
    def test_exit_during_candidate_read(self, w, m, root):
        def hook(world, pid):
            if world.scans == 1:
                world.nodes.pop(200, None)
        w.hook = hook
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 10)
        self.assertEqual(len(exits), 1)

    @mock_case
    def test_new_child_after_first_enumeration(self, w, m, root):
        w.hook = lambda world, pid: world.make(300, 3, 100, 30) if world.scans == 1 else None
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 60)
        self.assertEqual(m.collection_observation["scans"], 3)

    @mock_case
    def test_continuous_churn_blocked(self, w, m, root):
        w.hook = lambda world, pid: world.make(300 + world.scans, 30 + world.scans, 100, 1)
        members, unknown, exits = m.collect(root)
        self.assertEqual(unknown[-1]["reason"], "TREE_RESCAN_NOT_CLOSED")
        self.assertFalse(m.collection_observation["closed"])
        self.assertEqual(w.scans, 3)

    @mock_case
    def test_alive_access_denied(self, w, m, root):
        w.fail[(200, "rss_bytes")] = guard.psutil.AccessDenied(200)
        self.assertTrue(m.collect(root)[1])
        self.assertNotIn((200, 2), m.retired_members)

    @mock_case
    def test_known_alive_unknown(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        w.fail[(200, "cwd")] = guard.psutil.AccessDenied(200)
        self.assertTrue(m.collect(root)[1])
        self.assertFalse(m.confirmed_sample_exits)

    @mock_case
    def test_fields_drift(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        w.nodes[200]["cmdline"] = ["漂移"]
        self.assertTrue(m.collect(root)[1])

    @mock_case
    def test_ppid_drift(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        w.nodes[200]["ppid"] = 0
        self.assertTrue(m.collect(root)[1])

    @mock_case
    def test_old_pid_reused_not_enumerated(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        w.make(200, 22, 0, 999)
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 10)
        self.assertEqual(exits[0]["status"], "ORIGINAL_PID_REUSED")
        self.assertNotIn(200, w.enumerated)

    @mock_case
    def test_independently_owned_new_pid(self, w, m, root):
        m.last_members[(200, 2)] = dict(w.nodes[200])
        w.make(200, 22, 100, 40)
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        self.assertEqual(sum(x["rss_bytes"] for x in members), 50)
        self.assertIn((200, 22), m.known_lineage)
        self.assertEqual(exits[0]["status"], "ORIGINAL_PID_REUSED")

    @mock_case
    def test_known_orphan_historical_rss(self, w, m, root):
        w.make(300, 3, 200, 30)
        initial, unknown, exits = m.collect(root)
        m.last_members = {(x["pid"], x["create_time"]): x for x in initial}
        del w.nodes[200]
        members, unknown, exits = m.collect(root)
        self.assertFalse(unknown)
        orphan = next(x for x in members if x["pid"] == 300)
        self.assertFalse(orphan["stoppable"])
        self.assertEqual(orphan["lineage_mode"], "HISTORICAL_CHAIN")
        self.assertEqual(sum(x["rss_bytes"] for x in members), 40)

    @mock_case
    def test_new_unknown_orphan_blocked(self, w, m, root):
        w.make(300, 3, 200, 30)
        initial, _, _ = m.collect(root)
        m.last_members = {(x["pid"], x["create_time"]): x for x in initial}
        del w.nodes[200]
        w.make(400, 4, 300, 40)
        self.assertTrue(m.collect(root)[1])

    @mock_case
    def test_reused_parent_blocked(self, w, m, root):
        w.make(300, 3, 200, 30)
        initial, _, _ = m.collect(root)
        m.last_members = {(x["pid"], x["create_time"]): x for x in initial}
        w.make(200, 22, 100, 40)
        members, unknown, exits = m.collect(root)
        self.assertTrue(unknown)
        self.assertFalse(any(x["pid"] == 300 for x in members))
        self.assertNotIn(200, w.enumerated)

    @mock_case
    def test_ancestor_alive_denied_blocked(self, w, m, root):
        w.make(300, 3, 200, 30)
        initial, _, _ = m.collect(root)
        m.last_members = {(x["pid"], x["create_time"]): x for x in initial}
        w.fail[(200, "exe")] = guard.psutil.AccessDenied(200)
        self.assertTrue(m.collect(root)[1])

    @mock_case
    def test_root_exit_orphan_retained(self, w, m, root):
        m.last_members = {(100, 1): root, (200, 2): dict(w.nodes[200])}
        del w.nodes[100]
        m.finish = lambda status, reason, **values: (status, values)
        status, values = m.root_terminal("ROOT_MISSING", None)
        self.assertEqual(status, "ROOT_EXITED_WITH_REMAINING")
        self.assertEqual(values["retained"][0]["expected"]["pid"], 200)

    @mock_case
    def test_parent_nosuch_alive_candidate_not_retired(self, w, m, root):
        w.make(300, 3, 888, 30)
        m.last_members[(300, 3)] = dict(w.nodes[300])
        self.assertTrue(m.collect(root)[1])
        self.assertNotIn((300, 3), m.retired_members)

    @mock_case
    def test_action_stable_ancestor_chain_allowed(self, w, m, root):
        w.make(300, 3, 200, 30)
        members, unknown, _ = m.collect(root)
        candidate = next(x for x in members if x["pid"] == 300)
        process, current, chain = m.verified_chain(candidate, root)
        self.assertEqual([x["pid"] for x in chain], [300, 200, 100])

    @mock_case
    def test_action_after_collect_parent_reuse_rejected(self, w, m, root):
        w.make(300, 3, 200, 30)
        members, _, _ = m.collect(root)
        candidate = next(x for x in members if x["pid"] == 300)
        w.make(200, 22, 100, 20)
        result = m.stop_one(candidate, root, "模拟阈值")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(any(x["kind"] == "TERMINATE_SENT" for x in m.events))

    @mock_case
    def test_action_between_first_and_second_check_reuse_rejected(self, w, m, root):
        w.make(300, 3, 200, 30)
        members, _, _ = m.collect(root)
        candidate = next(x for x in members if x["pid"] == 300)
        def event(kind, **values):
            m.events.append(dict(kind=kind, **values))
            if kind == "PRE_STOP_VERIFIED":
                w.make(200, 22, 100, 20)
        m.event = event
        result = m.stop_one(candidate, root, "模拟阈值")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any(x["kind"] == "PRE_STOP_VERIFIED" for x in m.events))
        self.assertFalse(any(x["kind"] == "TERMINATE_SENT" for x in m.events))

    @mock_case
    def test_action_saved_grandparent_reuse_rejected(self, w, m, root):
        w.make(300, 3, 200, 30)
        w.make(400, 4, 300, 40)
        members, _, _ = m.collect(root)
        candidate = next(x for x in members if x["pid"] == 400)
        w.make(200, 22, 100, 20)
        with self.assertRaisesRegex(RuntimeError, "祖先链身份变化|父出生时间晚于子对象"):
            m.verified_chain(candidate, root)

    @mock_case
    def test_owned_root_upstream_not_bound(self, w, m, root):
        w.make(999, 9, 0, 1)
        w.nodes[100]["ppid"] = 999
        root = guard.identity(w.process(100))
        m.initial_root = root
        m.binding.update(root)
        del w.nodes[999]
        # 上游缺失仍由现有get_root处理；本补丁不比较ROOT保存的上游birth。
        m.get_root = lambda: ("MATCH", dict(root, parent=None))
        with patch.object(guard, "identity", lambda p: dict(w.nodes[p.pid], parent=None)):
            self.assertEqual(len(m.verified_chain(root, root)[2]), 1)


def canary(label, stop):
    directory = W / label
    directory.mkdir()
    owned = []
    commands = []
    def launch(code):
        argv = [sys.executable, "-B", "-X", "utf8", "-c", code]
        p = subprocess.Popen(argv, cwd=directory, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        owned.append((p, p.pid, guard.psutil.Process(p.pid).create_time()))
        commands.append(argv)
        return p
    try:
        unrelated = launch("import time; time.sleep(30)")
        code = "import subprocess,sys,time,json; from pathlib import Path; p=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(30)'],creationflags=subprocess.CREATE_NO_WINDOW); Path('ready.json').write_text(json.dumps({'pid':p.pid}),encoding='utf-8'); time.sleep(30)" if stop else "import time; time.sleep(2.5)"
        parent = launch(code)
        if stop:
            deadline = time.monotonic() + 5
            while not (directory / "ready.json").exists():
                if time.monotonic() > deadline:
                    raise RuntimeError("自有夹具未就绪")
                time.sleep(.02)
            child = json.loads((directory / "ready.json").read_text(encoding="utf-8"))["pid"]
            owned.append((None, child, guard.psutil.Process(child).create_time()))
        ident = guard.identity(guard.psutil.Process(parent.pid))
        binding = dict(ident, allowed_run_dirs=[str(directory)], source_commit="932051cdacdf02f729d6a7554b07118d05e96aa4", run_id=label, fixture_test=True, max_seconds=10)
        plan = dict(resource_sample_interval_seconds=1, new_run_tree_rss_limit_bytes=6*1024**3,
                    new_run_available_ram_stop_bytes=512*1024**2, minimum_c_disk_free_before_dispatch_bytes=8*1024**3)
        guard.write_new(directory / "plan.json", plan)
        guard.write_new(directory / "binding.json", binding)
        argv = [sys.executable,"-B","-X","utf8",str(W / "guard.py"),"--plan",str(directory / "plan.json"),"--binding",str(directory / "binding.json"),"--output-dir",str(directory / "guard")]
        if stop:
            argv += ["--fixture-tree-limit-bytes", "1"]
        began = time.monotonic()
        with (directory / "stdout.log").open("xb") as so, (directory / "stderr.log").open("xb") as se:
            completed = subprocess.run(argv, cwd=directory, stdout=so, stderr=se, timeout=20)
        native = dict(command=argv, native_exit_code=completed.returncode, elapsed_seconds=time.monotonic()-began, fixture_commands=commands)
        guard.write_new(directory / "native.json", native)
        receipt = json.loads((directory / "guard/guard_receipt.json").read_text(encoding="utf-8"))
        assert completed.returncode == (2 if stop else 0), native
        assert receipt["status"] == ("STOPPED" if stop else "ROOT_EXITED"), receipt
        assert unrelated.poll() is None
        assert receipt["absolute_peak_memory_bytes"] is None
        samples = [json.loads(x) for x in (directory / "guard/samples.jsonl").read_text(encoding="utf-8").splitlines()]
        assert all(x["collection_observation"]["closed"] for x in samples)
        assert all(x["tree_rss_bytes"] == sum(v["rss_bytes"] for v in x["members"]) for x in samples)
        if stop:
            assert {x["pid"] for x in receipt["stopped"]} == {parent.pid, child}
            assert unrelated.pid not in {x["pid"] for x in receipt["stopped"]}
        else:
            assert len(samples) >= 2
            assert samples[1]["actual_start_gap_seconds"] > .9
        ROWS.append(dict(case=label, result="PASS", guard_native_exit_code=completed.returncode, unrelated_owned_sibling_retained=True))
    finally:
        # 清理仅本函数实际启动且创建时间仍匹配的自有夹具，不按旧PID追杀。
        for p, pid, birth in reversed(owned):
            try:
                proc = guard.psutil.Process(pid)
                if proc.create_time() == birth:
                    proc.terminate()
                    proc.wait(timeout=3)
            except guard.psutil.NoSuchProcess:
                pass
            if p is not None:
                p.wait(timeout=3)


if __name__ == "__main__":
    assert sha(OLD) == "a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac"
    assert sha(SUP) == "193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0"
    import difflib
    before, after = OLD.read_text(encoding="utf-8"), (W / "guard.py").read_text(encoding="utf-8")
    for name, following in [("readback_member", "root_terminal"), ("root_terminal", "event"), ("historical_member", "stop_tree"), ("stop_one", "progress")]:
        part = lambda source: source.split("    def " + name + "(", 1)[1].split("    def " + following + "(", 1)[0]
        assert part(before) == part(after), name
    with (W / "source_diff_fixture_r02.patch").open("x", encoding="utf-8", newline="\n") as f:
        f.write("".join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(OLD),tofile=str(W / "guard.py"))))
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Semantics))
    if not result.wasSuccessful():
        raise SystemExit(1)
    canary("owned_threshold_canary", True)
    canary("one_second_cadence_canary", False)
    report = dict(status="PASS_G1_ONLY", cases=ROWS, mock_tests=result.testsRun, actual_canaries=2,
                  guard_sha256=sha(W / "guard.py"), supervisor_sha256=sha(W / "supervisor.py"), terminate_kill_kernel_unchanged=True,
                  action_ancestor_identity_fail_closed_strengthened=True,
                  declared_semantics="规定节拍离散监测执行通过", absolute_tree_peak_bytes=None,
                  old_s11_budget_reclassified=False, hardware_or_vivado_started=False,
                  limitations=["模拟不证明真实OS PID复用；所有canary仅为本任务自有轻量进程。", "连续绝对峰及未采短命对象未知；闭合活集合RSS是离散非原子合计。", "仅G1，未独立审查；不能用于Vivado重型派发或继承旧S11预算PASS。"])
    guard.write_new(W / "selftest_result.json", report)
    print(guard.encode(dict(status=report["status"], tests=len(ROWS), guard_sha256=report["guard_sha256"])))
