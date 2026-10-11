import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil
import guard

# 针对两项P1保存真实stdout/stderr/native，清理只限自有夹具身份。
BASE = Path(__file__).absolute().parent
PLAN = BASE.parent / "s10_root_run_20261012_r01/resource_plan.json"
results = []
started = time.monotonic()


def wait_file(path):
    deadline = time.monotonic() + 6
    while not path.is_file():
        if time.monotonic() > deadline:
            raise RuntimeError("自测ready超时")
        time.sleep(0.03)
    return json.loads(path.read_text(encoding="utf-8"))


def alive(item):
    try:
        return psutil.Process(item["pid"]).create_time() == item["create_time"]
    except psutil.NoSuchProcess:
        return False


for case, mode, expected in [("race", "race", "STOPPED"), ("orphan", "orphan", "ROOT_EXITED_WITH_REMAINING"), ("parent_nosuch", "orphan", "BLOCKED")]:
    directory = BASE / ("p1_final_" + case)
    directory.mkdir()
    owned = []
    with (directory / "fixture.stdout.log").open("xb") as stdout, (directory / "fixture.stderr.log").open("xb") as stderr:
        parent = subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(BASE / "target_fixture.py"), mode, str(directory / "ready.json")], cwd=directory, stdout=stdout, stderr=stderr)
        try:
            ready = wait_file(directory / "ready.json")
            wait_file(directory / "long.json")
            if case == "race":
                wait_file(directory / "short.json")
            owned = [guard.identity(psutil.Process(pid)) for pid in [parent.pid] + ready["children"]]
            binding = {k: owned[0][k] for k in ("pid", "create_time", "exe", "cwd")}
            binding.update({"allowed_run_dirs": [str(directory)], "run_id": directory.name, "source_commit": "3f24c94564d10103aaa00db07356f666b085f687", "fixture_test": True, "max_seconds": 10})
            guard.write_new(directory / "binding.json", binding)
            argv = [sys.executable, "-B", "-X", "utf8", str(BASE / "target_runner.py"), case, str(directory / "binding.json"), str(PLAN), str(directory / "monitor")]
            if case == "race":
                argv += ["--short-pid", str(owned[2]["pid"])]
            cp = subprocess.run(argv, capture_output=True, check=False, timeout=15)
            (directory / "guard.stdout.log").write_bytes(cp.stdout)
            (directory / "guard.stderr.log").write_bytes(cp.stderr)
            guard.write_new(directory / "guard.native.json", {"command": argv, "native_exit_code": cp.returncode})
            receipt = json.loads((directory / "monitor/guard_receipt.json").read_text(encoding="utf-8"))
            samples = [json.loads(x) for x in (directory / "monitor/samples.jsonl").read_text(encoding="utf-8").splitlines()]
            events = [json.loads(x) for x in (directory / "monitor/events.jsonl").read_text(encoding="utf-8").splitlines()]
            good = receipt["status"] == expected and cp.returncode == (2 if expected == "STOPPED" else 3)
            after = [alive(x) for x in owned]
            if case == "race":
                good = good and len(samples) >= 2 and bool(samples[0]["confirmed_exits"]) and samples[0]["tree_rss_bytes"] is None and not samples[0]["uncertain"] and any(x["kind"] == "HELPER_EXIT_CONFIRMED_CONTINUE" for x in events) and after == [False, False, False]
            elif case == "orphan":
                good = good and after == [False, True] and any(x["status"] == "ALIVE" and x["expected"]["pid"] == owned[1]["pid"] for x in receipt["retained"])
            else:
                good = good and after == [True, True] and samples[0]["uncertain"][0]["reason"] == "CANDIDATE_ALIVE_OR_UNKNOWN_PARENT_CHAIN" and not samples[0]["confirmed_exits"] and not receipt["stopped"]
            results.append({"name": case, "pass": good, "native_exit_code": cp.returncode, "status": receipt["status"], "samples": len(samples), "alive_after_guard": after, "retained": receipt["retained"], "guard_sha256": receipt["guard_sha256"], "identities": owned})
        finally:
            for item in reversed(owned):
                if alive(item):
                    current = guard.base_identity(psutil.Process(item["pid"]))
                    if not guard.same_identity(current, item):
                        raise RuntimeError("自有清理身份变化，保持对象")
                    psutil.Process(item["pid"]).terminate()
                    psutil.Process(item["pid"]).wait(timeout=4)
            parent.wait(timeout=4)
            assert not any(alive(x) for x in owned)
guard.write_new(BASE / "target_final_results.json", {"status": "PASS" if all(x["pass"] for x in results) else "FAIL", "cases": results, "elapsed_seconds": time.monotonic() - started, "guard_sha256": hashlib.sha256((BASE / "guard.py").read_bytes()).hexdigest(), "limitations": ["真实已退出短命候选旧枚举调度注入，次样本fixture限1B触发真实父子停止", "父NoSuch为异常出口模拟，候选PID/出生和活状态真实读回", "根自然退出/child仍活为真实进程行为；孤儿只由自测已核身份清理"]})
print(json.dumps({"status": "PASS" if all(x["pass"] for x in results) else "FAIL", "cases": [{k: x[k] for k in ("name", "pass", "native_exit_code", "samples")} for x in results]}, ensure_ascii=False))
raise SystemExit(0 if all(x["pass"] for x in results) else 2)
