import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil
import guard

# 只验证本轮STOP_REQUEST、正常持续采样和输出目录不覆盖。
base = Path(__file__).absolute().parent
directory = base / "stop_request_fixture"
directory.mkdir()
plan = base.parent / "s10_root_run_20261012_r01/resource_plan.json"
started = time.monotonic()
with (directory / "fixture.stdout.log").open("xb") as stdout, (directory / "fixture.stderr.log").open("xb") as stderr:
    parent = subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(base / "fixture.py"), "--mode", "tree", "--ready", str(directory / "ready.json")], cwd=directory, stdout=stdout, stderr=stderr)
    deadline = time.monotonic() + 8
    while not (directory / "child_ready.json").is_file():
        if time.monotonic() > deadline:
            raise RuntimeError("夹具ready超时")
        time.sleep(0.05)
    ready = json.loads((directory / "ready.json").read_text(encoding="utf-8"))
    owned = [guard.identity(psutil.Process(pid)) for pid in [parent.pid] + ready["children"]]
    b = {k: owned[0][k] for k in ("pid", "create_time", "exe", "cwd")}
    b.update({"allowed_run_dirs": [str(directory)], "source_commit": "3f24c94564d10103aaa00db07356f666b085f687", "run_id": "s10_resource_guard_20261012_r01", "fixture_test": True, "max_seconds": 8})
    guard.write_new(directory / "binding.json", b)
    argv = [sys.executable, "-B", "-X", "utf8", str(base / "guard.py"), "--plan", str(plan), "--binding", str(directory / "binding.json"), "--output-dir", str(directory / "monitor")]
    with (directory / "guard.stdout.log").open("xb") as gout, (directory / "guard.stderr.log").open("xb") as gerr:
        monitor = subprocess.Popen(argv, stdout=gout, stderr=gerr)
        while not (directory / "monitor/samples.jsonl").is_file():
            if time.monotonic() > deadline:
                raise RuntimeError("守卫启动超时")
            time.sleep(0.05)
        time.sleep(1.25)
        guard.write_new(directory / "monitor/STOP_REQUEST", {"reason": "SELFTEST_ONLY"})
        rc = monitor.wait(timeout=15)
    guard.write_new(directory / "guard.native.json", {"command": argv, "native_exit_code": rc})
    receipt = json.loads((directory / "monitor/guard_receipt.json").read_text(encoding="utf-8"))
    after = []
    for item in owned:
        try:
            current = guard.base_identity(psutil.Process(item["pid"]))
            after.append(current)
        except psutil.NoSuchProcess:
            after.append(None)
    parent.wait(timeout=4)
    before_hash = hashlib.sha256((directory / "monitor/guard_receipt.json").read_bytes()).hexdigest()
    cp = subprocess.run(argv, capture_output=True, check=False)
    (directory / "no_overwrite.stdout.log").write_bytes(cp.stdout)
    (directory / "no_overwrite.stderr.log").write_bytes(cp.stderr)
    guard.write_new(directory / "no_overwrite.native.json", {"command": argv, "native_exit_code": cp.returncode})
    good = rc == 2 and receipt["status"] == "STOPPED" and "STOP_REQUEST" in receipt["reason"] and receipt["samples"] >= 2 and after == [None, None] and cp.returncode == 1 and before_hash == hashlib.sha256((directory / "monitor/guard_receipt.json").read_bytes()).hexdigest()
    result = {"status": "PASS" if good else "FAIL", "guard_native_exit_code": rc, "no_overwrite_native_exit_code": cp.returncode, "samples": receipt["samples"], "objects_after": after, "elapsed_seconds": time.monotonic() - started, "source_sha256": hashlib.sha256((base / "guard.py").read_bytes()).hexdigest()}
    guard.write_new(base / "supplement_results.json", result)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if good else 2)
