import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil
import guard

# 每个真实夹具都保留独立日志和原生码，清理只针对自有Popen句柄和已核身份子对象。
BASE = Path(__file__).absolute().parent
OUT = BASE / "selftest_final"
OUT.mkdir()
PLAN = BASE.parent / "s10_root_run_20261012_r01/resource_plan.json"
COMMIT = "1eed350c43aae4cdee1f8179a93ce87d75d9f2a8"
started = time.monotonic()
results = []
cleanup = []


def write(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def wait_file(path):
    deadline = time.monotonic() + 8
    while not path.is_file():
        if time.monotonic() > deadline:
            raise RuntimeError("夹具未产生ready：" + str(path))
        time.sleep(0.05)
    return json.loads(path.read_text(encoding="utf-8"))


def live(pid, birth):
    try:
        return psutil.Process(pid).create_time() == birth and psutil.Process(pid).is_running()
    except psutil.NoSuchProcess:
        return False


def one(name, mode, expected, mutation=None, threshold=None):
    directory = OUT / name
    directory.mkdir()
    unknown = directory / "outside"
    unknown.mkdir()
    fixture_out = (directory / "fixture.stdout.log").open("xb")
    fixture_err = (directory / "fixture.stderr.log").open("xb")
    process = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(BASE / "fixture.py"), "--mode", mode, "--ready", str(directory / "ready.json"), "--unknown-cwd", str(unknown)], cwd=directory, stdout=fixture_out, stderr=fixture_err)
    owned = []
    try:
        ready = wait_file(directory / "ready.json")
        actual = guard.identity(psutil.Process(process.pid))
        owned.append(actual)
        for pid in ready["children"]:
            wait_file(directory / ("child_ready.json" if pid == ready["children"][0] else "unknown_ready.json"))
            owned.append(guard.identity(psutil.Process(pid)))
        # mixed中仅根及正常child目录允许；outside是故意设置的本轮不确定对象。
        allowed = directory / "allowed"
        if mode == "mixed":
            # 测试实际cwd边界需根先在唯一允许目录启动，本函数稍后另做此案例。
            raise RuntimeError("mixed使用专用函数")
        binding = {k: actual[k] for k in ("pid", "create_time", "exe", "cwd")}
        binding.update({"allowed_run_dirs": [str(directory)], "source_commit": COMMIT, "run_id": name, "max_seconds": 8, "fixture_test": True})
        if mutation:
            mutation(binding)
        write(directory / "binding.json", binding)
        argv = [sys.executable, "-B", "-X", "utf8", str(BASE / "guard.py"), "--plan", str(PLAN), "--binding", str(directory / "binding.json"), "--output-dir", str(directory / "monitor")]
        if threshold is not None:
            argv += ["--fixture-tree-limit-bytes", str(threshold)]
        cp = subprocess.run(argv, capture_output=True, check=False, timeout=20)
        (directory / "guard.stdout.log").write_bytes(cp.stdout)
        (directory / "guard.stderr.log").write_bytes(cp.stderr)
        write(directory / "guard.native.json", {"command": argv, "native_exit_code": cp.returncode})
        receipt = json.loads((directory / "monitor/guard_receipt.json").read_text(encoding="utf-8"))
        was_live = [live(x["pid"], x["create_time"]) for x in owned]
        good = receipt["status"] == expected and cp.returncode == (0 if expected == "ROOT_EXITED" else 2 if expected == "STOPPED" else 3)
        if expected == "BLOCKED":
            good = good and all(was_live) and not receipt["stopped"]
        if expected == "STOPPED":
            good = good and not any(was_live) and {x["pid"] for x in receipt["stopped"]} == {x["pid"] for x in owned}
        results.append({"name": name, "pass": good, "actual_status": receipt["status"], "native_exit_code": cp.returncode, "reason": receipt["reason"], "objects_alive_after_guard": was_live, "identities": owned})
    finally:
        for item in reversed(owned):
            if live(item["pid"], item["create_time"]):
                current = guard.base_identity(psutil.Process(item["pid"]))
                if not guard.same_identity(current, item):
                    raise RuntimeError("自测清理身份变化，保留对象")
                psutil.Process(item["pid"]).terminate()
                psutil.Process(item["pid"]).wait(timeout=4)
                cleanup.append({"identity": current, "action": "FIXTURE_ONLY_TERMINATE"})
        process.wait(timeout=5)
        fixture_out.close()
        fixture_err.close()


def mixed():
    directory = OUT / "external_unknown"
    directory.mkdir()
    allowed = directory / "allowed"
    outside = directory / "outside"
    allowed.mkdir()
    outside.mkdir()
    with (directory / "fixture.stdout.log").open("xb") as stdout, (directory / "fixture.stderr.log").open("xb") as stderr:
        parent = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(BASE / "fixture.py"), "--mode", "mixed", "--ready", str(directory / "ready.json"), "--unknown-cwd", str(outside)], cwd=allowed, stdout=stdout, stderr=stderr)
        owned = []
        # 非本轮兄弟进程也必须继续存活，守卫不能广域枚举或停止它。
        external = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(BASE / "fixture.py"), "--mode", "child", "--ready", str(directory / "external_ready.json")], cwd=outside, stdout=stdout, stderr=stderr)
        try:
            ready = wait_file(directory / "ready.json")
            wait_file(directory / "external_ready.json")
            wait_file(directory / "child_ready.json")
            wait_file(directory / "unknown_ready.json")
            owned = [guard.identity(psutil.Process(pid)) for pid in [parent.pid] + ready["children"] + [external.pid]]
            b = {k: owned[0][k] for k in ("pid", "create_time", "exe", "cwd")}
            b.update({"allowed_run_dirs": [str(allowed)], "source_commit": COMMIT, "run_id": "external_unknown", "fixture_test": True, "max_seconds": 8})
            write(directory / "binding.json", b)
            argv = [sys.executable, "-B", "-X", "utf8", str(BASE / "guard.py"), "--plan", str(PLAN), "--binding", str(directory / "binding.json"), "--output-dir", str(directory / "monitor"), "--fixture-tree-limit-bytes", "1"]
            cp = subprocess.run(argv, capture_output=True, check=False, timeout=20)
            (directory / "guard.stdout.log").write_bytes(cp.stdout)
            (directory / "guard.stderr.log").write_bytes(cp.stderr)
            write(directory / "guard.native.json", {"command": argv, "native_exit_code": cp.returncode})
            receipt = json.loads((directory / "monitor/guard_receipt.json").read_text(encoding="utf-8"))
            alive = [live(x["pid"], x["create_time"]) for x in owned]
            results.append({"name": "external_unknown", "pass": receipt["status"] == "STOP_PARTIAL" and cp.returncode == 3 and alive == [True, False, True, True], "actual_status": receipt["status"], "native_exit_code": cp.returncode, "objects_alive_after_guard": alive, "identities": owned})
        finally:
            for item in reversed(owned):
                if live(item["pid"], item["create_time"]):
                    current = guard.base_identity(psutil.Process(item["pid"]))
                    if not guard.same_identity(current, item):
                        raise RuntimeError("自测清理身份变化，保留对象")
                    psutil.Process(item["pid"]).terminate()
                    psutil.Process(item["pid"]).wait(timeout=4)
                    cleanup.append({"identity": current, "action": "FIXTURE_ONLY_TERMINATE"})
            parent.wait(timeout=5)
            external.wait(timeout=5)


one("identity_mismatch", "child", "BLOCKED", lambda b: b.update(exe=str(PLAN)))
one("pid_reuse_simulation", "child", "BLOCKED", lambda b: b.update(create_time=b["create_time"] + 1))
one("normal_exit", "normal", "ROOT_EXITED")
one("rss_stop_tree", "tree", "STOPPED", threshold=1)
mixed()
write(OUT / "selftest_results.json", {"status": "PASS" if all(x["pass"] for x in results) else "FAIL", "cases": results, "cleanup": cleanup, "elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None, "limitations": ["PID复用用真实PID加错创建时间模拟，不声称OS实际发生复用", "低阈值fixture触发资源停止，未分配GiB或操作真实Vivado", "外部对象来自自有夹具，停止由自测清理且与守卫动作分列"]})
print(json.dumps({"status": "PASS" if all(x["pass"] for x in results) else "FAIL", "cases": [{"name": x["name"], "pass": x["pass"], "native_exit_code": x["native_exit_code"]} for x in results], "elapsed_seconds": time.monotonic() - started}, ensure_ascii=False))
raise SystemExit(0 if all(x["pass"] for x in results) else 2)
