"""只向自有夹具注入确定竞态；Guard.run返回值成为真实子程序原生码。"""
import json
from pathlib import Path
import sys
import time
import psutil
import guard

case = sys.argv[1]
work = Path(sys.argv[2])
objects = json.loads((work / "owned.json").read_text(encoding="utf-8"))
plan = json.loads((work / "plan.json").read_text(encoding="utf-8"))
binding = json.loads((work / "binding.json").read_text(encoding="utf-8"))
root, helper, leaf = objects

def naturally_exit(role, expected):
    (work / (role + "_exit")).touch(exist_ok=False)
    deadline = time.monotonic() + 4
    while guard.Guard.readback_member(monitor, expected)["status"] not in {"ABSENT", "ORIGINAL_PID_REUSED"}:
        if time.monotonic() > deadline:
            raise RuntimeError("自有自然退出超时")
        time.sleep(0.02)

class FixtureGuard(guard.Guard):
    def collect(self, current_root):
        if self.sample_count == 1 and case in {"A", "B_newborn", "D_exit", "D_unknown"}:
            naturally_exit("helper", helper)
            if case == "D_exit":
                naturally_exit("leaf", leaf)
            if case == "B_newborn":
                (work / "new_child").touch(exist_ok=False)
                deadline = time.monotonic() + 4
                while not (work / "newborn_ready.json").exists():
                    if time.monotonic() > deadline:
                        raise RuntimeError("新子对象未ready")
                    time.sleep(0.02)
        if case == "B_unknown" and self.sample_count == 0:
            naturally_exit("helper", helper)
            original = psutil.Process.children
            def injected(process, recursive=False):
                if process.pid == root["pid"]:
                    return [psutil.Process(leaf["pid"])]
                return original(process, recursive=recursive)
            psutil.Process.children = injected
        if case == "A" and self.sample_count == 3:
            self.overrides["tree_rss_bytes"] = 1
        if case == "D_race" and self.sample_count == 1:
            original = guard.identity
            fired = [False]
            def exit_during_read(process):
                if process.pid == leaf["pid"] and not fired[0]:
                    fired[0] = True
                    naturally_exit("leaf", leaf)
                    raise psutil.NoSuchProcess(process.pid, msg="自有候选读取期间真实自然退出")
                return original(process)
            guard.identity = exit_during_read
        if case.startswith("C_") and self.sample_count == 1:
            field = case[2:]
            original = self.readback_member
            def changed(expected):
                value = original(expected)
                if expected["pid"] == leaf["pid"] and value["status"] == "ALIVE":
                    if field == "create_time":
                        return {"expected": expected, "status": "ORIGINAL_PID_REUSED", "actual_create_time": expected[field] + 1, "new_object_untouched": True}
                    value["actual"][field] = ["模拟字段变化"] if field == "cmdline" else -1 if field in {"pid", "ppid"} else "模拟字段变化"
                    value["status"] = "IDENTITY_CHANGED"
                return value
            self.readback_member = changed
        if case == "D_unknown" and self.sample_count == 1:
            original = self.readback_member
            def unknown(expected):
                if expected["pid"] == leaf["pid"]:
                    return {"expected": expected, "status": "UNKNOWN", "error": "自有夹具注入AccessDenied"}
                return original(expected)
            self.readback_member = unknown
        return super().collect(current_root)

    def progress(self):
        if case == "D_root" and self.sample_count == 0:
            naturally_exit("root", root)
        return super().progress()

monitor = FixtureGuard(plan, binding, work / "monitor")
monitor.input_bindings = [{"path": str(work / name), "sha256": guard.hashlib.sha256((work / name).read_bytes()).hexdigest()} for name in ("plan.json", "binding.json")]
code = monitor.run()
(work / "component_return.json").write_text(json.dumps({"code": code, "known_lineage": list(monitor.known_lineage.values()), "seed": 20261012}), encoding="utf-8")
raise SystemExit(code)
