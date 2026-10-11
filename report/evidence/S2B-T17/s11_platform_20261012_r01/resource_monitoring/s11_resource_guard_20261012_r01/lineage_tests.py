"""串行自有三成员夹具；原生退出、原字节日志、身份清理均留原件。"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
import guard

base = Path(__file__).resolve().parent
out = base / (sys.argv[1] if len(sys.argv) > 1 else "lineage_tests_r01")
out.mkdir()
plan = json.loads((base.parent / "s10_root_run_20261012_r01/resource_plan.json").read_text(encoding="utf-8"))
rows = []
peak = 0
start = time.monotonic()

def wait_json(path):
    deadline = time.monotonic() + 5
    while not path.exists():
        if time.monotonic() > deadline:
            raise RuntimeError("ready超时：" + str(path))
        time.sleep(0.02)
    return json.loads(path.read_text(encoding="utf-8"))

cases = ["A", "B_unknown", "B_newborn"] + ["C_" + x for x in guard.IDENTITY_KEYS] + ["D_exit", "D_race", "D_unknown", "D_root"]
for case in cases:
    work = out / case
    work.mkdir()
    owned = []
    with (work / "fixture.stdout.log").open("xb") as fo, (work / "fixture.stderr.log").open("xb") as fe:
        fixture = subprocess.Popen([sys.executable, "-S", "-B", "-X", "utf8", str(base / "lineage_fixture.py"), "root"], cwd=work, stdout=fo, stderr=fe)
        try:
            owned = [guard.identity(psutil.Process(wait_json(work / (role + "_ready.json"))["pid"])) for role in ("root", "helper", "leaf")]
            assert all(x["pid"] != 11112 for x in owned)
            (work / "owned.json").write_text(json.dumps(owned, ensure_ascii=False), encoding="utf-8")
            (work / "plan.json").write_text(json.dumps(plan), encoding="utf-8")
            b = {k: owned[0][k] for k in ("pid", "create_time", "exe", "cwd")}
            b.update(allowed_run_dirs=[str(work)], source_commit="1eed350c43aae4cdee1f8179a93ce87d75d9f2a8", run_id=case, fixture_test=True, max_seconds=4)
            (work / "binding.json").write_text(json.dumps(b), encoding="utf-8")
            argv = [sys.executable, "-B", "-X", "utf8", str(base / "lineage_native.py"), case, str(work)]
            with (work / "guard.stdout.log").open("xb") as so, (work / "guard.stderr.log").open("xb") as se:
                child = subprocess.Popen(argv, cwd=work, stdout=so, stderr=se)
                while child.poll() is None:
                    try:
                        tree = [psutil.Process().memory_info().rss] + [p.memory_info().rss for p in psutil.Process().children(recursive=True)]
                        peak = max(peak, sum(tree))
                    except psutil.Error:
                        pass
                    if time.monotonic() - start > 150:
                        raise RuntimeError("自有测试总时限")
                    time.sleep(0.025)
            (work / "native.json").write_text(json.dumps({"command": subprocess.list2cmdline(argv), "native_exit_code": child.returncode}), encoding="utf-8")
            r = json.loads((work / "monitor/guard_receipt.json").read_text(encoding="utf-8"))
            samples = [json.loads(x) for x in (work / "monitor/samples.jsonl").read_text(encoding="utf-8").splitlines()]
            assert child.returncode == 3, (case, r)
            if case == "A":
                h = [s for s in samples if any(m.get("lineage_mode") == "HISTORICAL_CHAIN" for m in s["members"])]
                assert len(h) >= 2 and all(m["stoppable"] is False for s in h for m in s["members"] if m.get("lineage_mode") == "HISTORICAL_CHAIN")
                assert samples[-1]["alerts"] == ["OWNED_TREE_RSS_GT_LIMIT"] and not r["stopped"] and r["retained"]
                assert guard.base_identity(psutil.Process(owned[2]["pid"]))["create_time"] == owned[2]["create_time"]
                assert all(s["verified_subset_rss_bytes"] == sum(m["rss_bytes"] for m in s["members"]) for s in h)
            elif case.startswith("B_") or case.startswith("C_") and case != "C_create_time" or case == "D_unknown":
                assert r["status"] == "BLOCKED" and not r["stopped"] and any(s["uncertain"] for s in samples)
            elif case in {"D_exit", "D_race"}:
                assert any(s["confirmed_exits"] and s["tree_rss_bytes"] is None for s in samples)
                assert len(samples) >= 3 and not samples[-1]["uncertain"]
            elif case == "D_root":
                assert r["status"] == "ROOT_EXITED_WITH_REMAINING" and len(r["retained"]) >= 2
            rows.append({"case": case, "native_exit_code": child.returncode, "status": r["status"], "samples": len(samples), "pass": True})
        finally:
            if (work / "newborn_ready.json").exists():
                owned.append(guard.base_identity(psutil.Process(wait_json(work / "newborn_ready.json")["pid"])))
            clean = []
            for expected in reversed(owned):
                try:
                    current = guard.base_identity(psutil.Process(expected["pid"]))
                except psutil.NoSuchProcess:
                    clean.append({"expected": expected, "status": "ABSENT"})
                    continue
                assert guard.same_identity(current, expected), "自有清理身份改变，保留"
                psutil.Process(current["pid"]).terminate()
                code = psutil.Process(current["pid"]).wait(timeout=4)
                clean.append({"identity": current, "native_exit_code": code, "scope": "FIXTURE_OWNED_ONLY"})
            fixture.wait(timeout=4)
            (work / "cleanup.json").write_text(json.dumps(clean, ensure_ascii=False), encoding="utf-8")
result = {"status": "PASS", "cases": rows, "seed": 20261012, "elapsed_seconds": time.monotonic()-start, "sampled_self_tree_rss_peak_bytes": peak, "limits": "单组自有轻量夹具；未运行Vivado/硬件/实际PID11112；身份变化/复用/UNKNOWN为显式注入，不称OS实际复用"}
(out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
