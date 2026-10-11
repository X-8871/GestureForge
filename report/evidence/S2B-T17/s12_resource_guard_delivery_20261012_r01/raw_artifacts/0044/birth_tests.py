"""复现r03首次观测反例，验证逐边出生门禁和删除门禁的语义mutant。"""
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import guard as new
from selftest import W, World, Fake, monitor

ROOT = W.parents[3]
OLD = ROOT / "tmp/2B/S2B-T17/s12_resource_guard_20261012_r01/guard.py"
CHECK = ROOT / "tmp/2B/S2B-T17/independent_s12_resource_guard_first_observation_review_20261012_r01/final_review_receipt.json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def case(module, label, second_level=False, equal=False, stable=False):
    w = World()
    w.make(100, 100, 0, 10)
    w.make(200, 120 if stable or equal else 150, 100, 20)
    if second_level:
        w.make(400, 120, 200, 40)
        w.make(300, 160, 400, 30)
    else:
        w.make(300, 120 if equal or not stable else 150, 200, 30)
    root = dict(w.nodes[100], parent=None)
    m = module.Guard({}, dict(root, allowed_run_dirs=[str(W)]), W / "unused_birth_mock")
    m.initial_root = root
    m.event = lambda kind, **values: m.events.append(dict(kind=kind, **values))
    with patch.object(module.psutil, "Process", w.process):
        candidate = module.identity(w.process(300))
        try:
            _, _, chain = m.verified_chain(candidate, root)
            accepted, error = True, None
        except RuntimeError as failure:
            accepted, error, chain = False, str(failure), []
        members, unknown, exits = m.collect(root)
    granted = any(x["pid"] == 300 and x["stoppable"] for x in members)
    registered = (300, candidate["create_time"]) in m.known_lineage
    expected = stable or equal or module is not new
    assert accepted == granted == registered == expected, (label, accepted, granted, registered, unknown)
    if not expected:
        assert unknown and "父出生时间晚于子对象" in error
    rows.append(dict(case=label, actual_nodes=w.nodes, verified_chain_accepted=accepted, collected_stoppable=granted,
                     candidate_known_lineage_registered=registered, uncertain=unknown, failure=error,
                     expected_rejection_failure_for_old_or_mutant=not (stable or equal) and module is not new, simulated_pids_only=True))


def stop_window(label, trigger):
    w = World()
    w.make(100, 100, 0, 10)
    w.make(200, 110, 100, 20)
    w.make(300, 120, 200, 30)
    m, root = monitor(w)
    actions = []
    class ActionFake(Fake):
        def terminate(self):
            actions.append("terminate")
            if trigger == "terminate":
                w.nodes[200]["create_time"] = 150
        def wait(self, timeout=None):
            raise new.psutil.TimeoutExpired(timeout, self.pid)
        def kill(self): actions.append("kill")
    def process(pid):
        if pid not in w.nodes:
            raise new.psutil.NoSuchProcess(pid)
        return ActionFake(w, pid)
    def event(kind, **values):
        m.events.append(dict(kind=kind, **values))
        if kind == trigger:
            w.nodes[200]["create_time"] = 150
    m.event = event
    with patch.object(new.psutil, "Process", process):
        candidate = new.identity(process(300))
        if trigger == "before_first_check":
            w.nodes[200]["create_time"] = 150
        result = m.stop_one(candidate, root, "模拟阈值")
    assert result["status"] == "BLOCKED" and "kill" not in actions, result
    assert actions == (["terminate"] if trigger in {"terminate", "PRE_KILL_VERIFIED"} else []), actions
    rows.append(dict(case=label, status=result["status"], result=result, mock_actions=actions,
                     old_child_ppid_unchanged=True, real_process_actions=False))


if __name__ == "__main__":
    assert sha(OLD) == "17d0d101b1946d2c47a48ce2e9050dea8822c5983b1c497c4ce5e799e159ec78"
    assert sha(CHECK) == "a51b043c65acfebb5790e72e2438cddb59ca6752dfb190caff17d481ffb22ec2"
    old = load("birth_old_r03", OLD)
    before, after = OLD.read_bytes(), (W / "guard.py").read_bytes()
    # UTF-8中文由文本构造为字节，删除门禁后必须逐字节恢复真实r03。
    added = '            if parent["create_time"] > current["create_time"]:\n                raise RuntimeError("父出生时间晚于子对象，拒绝复用父PID链")\n'.encode("utf-8")
    assert after.count(added) == 1 and after.replace(added, b"") == before
    mutant_path = W / "mutant_guard_without_birth_check.py"
    with mutant_path.open("xb") as f:
        f.write(after.replace(added, b""))
    mutant = load("birth_mutant_removed_gate", mutant_path)
    with (W / "source_diff_r03.patch").open("x", encoding="utf-8", newline="\n") as f:
        f.write("".join(difflib.unified_diff(before.decode("utf-8").splitlines(True), after.decode("utf-8").splitlines(True), fromfile=str(OLD), tofile=str(W / "guard.py"))))
    for module, version in [(old, "r03_actual_reproduction"), (mutant, "mutant_removed_gate"), (new, "r04_fixed")]:
        case(module, version+"_first_parent_later")
        case(module, version+"_second_ancestor_later", second_level=True)
    case(new, "r04_stable_legal_edges", stable=True)
    case(new, "r04_equal_birth_precision_boundary", equal=True)
    stop_window("r04_stop_first_check_parent_later", "before_first_check")
    stop_window("r04_stop_second_check_after_fsync_parent_later", "PRE_STOP_VERIFIED")
    stop_window("r04_pre_kill_first_check_parent_later", "terminate")
    stop_window("r04_pre_kill_second_check_after_fsync_parent_later", "PRE_KILL_VERIFIED")
    # 根以上launcher年龄不参与owned链的逐边出生门禁。
    w = World()
    w.make(999, 999, 0, 1)
    w.nodes[100]["ppid"] = 999
    m, root = monitor(w)
    with patch.object(new.psutil, "Process", w.process):
        root = new.identity(w.process(100))
        m.initial_root = root
        m.binding.update(root)
        _, _, chain = m.verified_chain(root, root)
        assert len(chain) == 1
    rows.append(dict(case="root_upstream_launcher_not_age_checked", result="PASS", chain_length=1))
    result = dict(status="PASS_BIRTH_GATE_G1_ONLY", cases=rows, tests=len(rows), guard_sha256=sha(W / "guard.py"),
                  original_r03_reproduced=True, removed_gate_mutant_reproduced=True, old_r03_not_reclassified=True,
                  source_diff_r03_sha256=sha(W / "source_diff_r03.patch"), mutant_sha256=sha(mutant_path),
                  limitations=["所有身份及停止动作均为mock；不声称真实OS PID复用。", "新增逐边出生门禁只检查candidate至owned ROOT，不纳入根以上launcher。", "前后动作窗口经同一verified_chain；现有保存parent及known_lineage拒绝也继续有效。", "时间相等允许精度边界；OS采样/停止仍非整树原子操作。"])
    with (W / "birth_test_result.json").open("x", encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(status=result["status"], tests=result["tests"], guard_sha256=result["guard_sha256"]),ensure_ascii=False))
