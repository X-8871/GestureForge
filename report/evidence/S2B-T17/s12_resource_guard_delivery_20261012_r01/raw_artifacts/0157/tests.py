"""只核验两处pin、生产入口拒绝、身份门禁及自有替身5秒监督节拍。"""
import ast
import contextlib
import difflib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import psutil

W = Path(__file__).resolve().parent
BASE = W.parent
ROOT = BASE.parents[3]
OLD = ROOT / "tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r02/supervisor.py"
NEW = BASE / "supervisor.py"
spec = importlib.util.spec_from_file_location("s12_pin_supervisor", NEW)
sup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sup)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = []
def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def native(label, arguments, wanted):
    argv = [sys.executable, "-B", "-X", "utf8", str(NEW)] + arguments
    started = time.monotonic()
    with (W / (label+".stdout.log")).open("xb") as so, (W / (label+".stderr.log")).open("xb") as se:
        result = subprocess.run(argv, cwd=W, stdout=so, stderr=se, timeout=10)
    row = dict(case=label, command=argv, native_exit_code=result.returncode, elapsed_seconds=time.monotonic()-started)
    write_new(W / (label+".native.json"), row)
    assert result.returncode == wanted, row
    rows.append(row)


def verify_pin():
    before = OLD.read_bytes()
    assert sha(OLD) == "bbe74e023603ee686a746b92d7dc5c2cb8066b3554eb5e65176bb1f6af88b9f9"
    replacements = [(b'GUARD=ROOT/"tmp/2B/S2B-T17/s11_resource_guard_20261012_r02/guard.py"', b'GUARD=ROOT/"tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/guard.py"'),
                    (b'GUARD_SHA="eca5338aeb738b86dbf77a0ae881c8dec5068b89bb4553719e8deba2423cb700"', b'GUARD_SHA="a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac"')]
    expected = before
    for old, new in replacements:
        assert before.count(old) == 1
        expected = expected.replace(old, new)
    assert NEW.read_bytes() == expected
    assert sup.GUARD == BASE / "guard.py" and sha(sup.GUARD) == sup.GUARD_SHA
    def stripped(source):
        tree = ast.parse(source)
        tree.body = [x for x in tree.body if not isinstance(x, ast.Assign) or not any(isinstance(t, ast.Name) and t.id in {"GUARD", "GUARD_SHA"} for t in x.targets)]
        return ast.dump(tree, include_attributes=False)
    assert stripped(before.decode("utf-8")) == stripped(expected.decode("utf-8"))
    with (W / "source_diff.patch").open("x", encoding="utf-8", newline="\n") as f:
        f.write("".join(difflib.unified_diff(before.decode("utf-8").splitlines(True),expected.decode("utf-8").splitlines(True),fromfile=str(OLD),tofile=str(NEW))))
    rows.append(dict(case="exact_two_pin_lines_and_ast_rest_unchanged", result="PASS", supervisor_sha256=sha(NEW)))


class Clock:
    def __init__(self): self.t = 0.0
    def monotonic(self): return self.t
    def sleep(self, duration): self.t += duration


def mock_supervision(label, root_drift=None, guard_drift=None, input_drift=False, terminal_before_ready=False, after_ready=False):
    out = W / label
    clock = Clock()
    binding = dict(pid=700100, create_time=1.0, exe="模拟root.exe", cwd=str(W), cmdline=["模拟root"], ppid=700000)
    command = [sys.executable, "模拟替身"]
    ident = dict(pid=700200, create_time=2.0, exe=command[0], cwd=binding["cwd"], cmdline=command)
    started = []
    identities = []
    class Child:
        pid = 700200
        def poll(self): return 7 if clock.t >= (6 if after_ready else .3) else None
        def wait(self, timeout=None): clock.t = max(clock.t, 6 if after_ready else .3); return 7
    def launch(cmd, **kwargs):
        started.append(cmd)
        folder = out / "guard"
        folder.mkdir()
        actual = dict(binding)
        if root_drift:
            actual[root_drift] = ["漂移"] if root_drift == "cmdline" else -1 if root_drift in {"pid", "ppid", "create_time"} else "漂移"
        (folder / "samples.jsonl").write_text(json.dumps(dict(index=0, members=[actual], alerts=[], uncertain=[]))+"\n", encoding="utf-8")
        if terminal_before_ready:
            write_new(folder / "guard_receipt.json", dict(status="BLOCKED", reason="模拟终态"))
        return Child()
    def identity(pid):
        assert pid == Child.pid
        identities.append(pid)
        actual = dict(ident)
        if guard_drift and len(identities) >= (3 if after_ready else 2):
            actual[guard_drift] = ["漂移"] if guard_drift == "cmdline" else -1 if guard_drift in {"pid", "create_time"} else "漂移"
        return actual
    inputs = [dict(path=str(W / "valid_plan.json"), sha256="0"*64)] if input_drift else []
    output = io.StringIO()
    with patch.object(sup, "time", clock), patch.object(sup.subprocess, "Popen", launch), patch.object(sup, "identity", identity), contextlib.redirect_stdout(output):
        code = sup.supervise(command, binding, out, inputs)
    (W / (label+".emitted.log")).write_text(output.getvalue(), encoding="utf-8")
    receipt = json.loads((out / "supervisor_receipt.json").read_text(encoding="utf-8"))
    assert code == 2 and receipt["supervisor_exit_code"] == 2
    assert receipt["ready"] == after_ready
    if input_drift:
        assert not started and "输入SHA漂移" in receipt["reason"] and receipt["child_native_exit_code"] is None
    else:
        assert started and receipt["child_native_exit_code"] == 7
    if guard_drift:
        journal = [json.loads(x) for x in (out / "supervision.jsonl").read_text(encoding="utf-8").splitlines()]
        assert any(x["kind"] == "READY" for x in journal) == after_ready
        if after_ready:
            assert "guard身份失效" in receipt["reason"]
    rows.append(dict(case=label, result="PASS", supervisor_exit_code=code, child_native_exit_code=receipt["child_native_exit_code"], simulated_pids_only=True))


def actual_canary():
    out = W / "actual_5s_supervision"
    argv = [sys.executable, "-B", "-X", "utf8", "-c", "import time; time.sleep(30)"]
    root = subprocess.Popen(argv, cwd=W, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    birth = psutil.Process(root.pid).create_time()
    cleanup = None
    try:
        proc = psutil.Process(root.pid)
        binding = dict(sup.identity(root.pid), ppid=proc.ppid())
        bound = W / "actual_binding.json"
        write_new(bound, binding)
        command = [sys.executable, "-B", "-X", "utf8", str(W / "standin.py"), str(bound), str(out)]
        input_rows = [dict(path=str(p), sha256=sha(p)) for p in (W / "standin.py", bound)]
        emitted = io.StringIO()
        began = time.monotonic()
        with contextlib.redirect_stdout(emitted):
            code = sup.supervise(command, binding, out, input_rows)
        with (W / "actual_5s.emitted.log").open("x", encoding="utf-8") as f:
            f.write(emitted.getvalue())
        elapsed = time.monotonic()-began
        journal = [json.loads(x) for x in (out / "supervision.jsonl").read_text(encoding="utf-8").splitlines()]
        live = [x for x in journal if x["kind"] == "LIVE"]
        receipt = json.loads((out / "supervisor_receipt.json").read_text(encoding="utf-8"))
        assert elapsed >= 10 and len(live) >= 3
        gaps = [b["elapsed_seconds"]-a["elapsed_seconds"] for a,b in zip(live,live[1:])]
        assert all(4.9 <= x <= 6 for x in gaps), gaps
        assert receipt["ready"] and code == 2 and receipt["child_native_exit_code"] == 7
        assert [x["kind"] for x in journal if x["kind"] in {"READY", "TERMINAL"}] == ["READY", "TERMINAL"]
        assert root.poll() is None
        rows.append(dict(case="actual_owned_standin_5s_live_ready_terminal", result="PASS", command=command,
                         supervisor_return_code=code, child_native_exit_code=7, elapsed_seconds=elapsed,
                         live_samples=len(live), actual_live_gaps_seconds=gaps, own_root_retained_alive=True,
                         production_cli_standin_supported=False, heavy_integration=False))
    finally:
        # 只清理本函数启动且birth仍一致的root，监督器本身不发送任何停止动作。
        current = psutil.Process(root.pid)
        assert current.create_time() == birth
        root.terminate()
        cleanup = root.wait(timeout=3)
        write_new(W / "actual_root_cleanup.json", dict(command=argv, pid=root.pid, create_time=birth, own_native_exit_code=cleanup))


if __name__ == "__main__":
    verify_pin()
    native("help", ["--help"], 0)
    native("cli_missing_required", [], 2)
    native("cli_guard_override_rejected", ["--guard", str(W / "standin.py")], 2)
    write_new(W / "valid_plan.json", {})
    write_new(W / "fixture_binding.json", dict(cwd=str(W), fixture_test=True))
    arguments = ["--plan", str(W / "valid_plan.json"), "--binding", str(W / "fixture_binding.json"), "--output-dir", str(W / "fixture_cli_not_started")]
    native("cli_fixture_rejected", arguments, 2)
    assert not (W / "fixture_cli_not_started").exists()
    native("cli_invalid_path_rejected", ["--plan", str(W / "does_not_exist.json"), "--binding", str(W / "fixture_binding.json"), "--output-dir", str(W / "invalid_cli_not_started")], 2)
    assert not (W / "invalid_cli_not_started").exists()
    mock_supervision("input_sha_drift_prelaunch", input_drift=True)
    mock_supervision("terminal_before_ready", terminal_before_ready=True)
    for field in ("pid", "create_time", "exe", "cwd", "cmdline", "ppid"):
        mock_supervision("root_sample_drift_"+field, root_drift=field)
    for field in sup.KEYS:
        mock_supervision("guard_identity_drift_"+field, guard_drift=field)
        mock_supervision("guard_identity_after_ready_drift_"+field, guard_drift=field, after_ready=True)
    actual_canary()
    report = dict(status="PASS_SUPERVISOR_PIN_G1_ONLY", tests=len(rows), cases=rows,
                  supervisor_sha256=sha(NEW), pinned_guard_sha256=sup.GUARD_SHA, exact_changed_lines=2,
                  limitations=["真实替身仅经import注入；生产CLI固定guard并禁止fixture，未运行Vivado重型任务。", "root身份漂移测试覆盖首次样本门禁，实际root后续身份由固定guard负责；本次替身不证明heavy期间root监测集成。", "监督器不终止对象；所有终态退出2阻止后续派发，保留真实child码。", "身份漂移及PID复用为mock，不证明真实OS复用；5秒LIVE节拍有实际轻量观测。"])
    write_new(W / "test_result.json", report)
    print(json.dumps(dict(status=report["status"], tests=report["tests"], supervisor_sha256=report["supervisor_sha256"]),ensure_ascii=False))
