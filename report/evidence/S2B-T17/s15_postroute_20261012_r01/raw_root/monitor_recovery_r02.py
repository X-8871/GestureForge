"""独立r02监护恢复准备及原生消费启动；不派发或重启实现任务。"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).parent
WORK = HERE.parents[3] / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02"
sys.path.insert(0, str(WORK))
import runtime_consumer as consumer


def sha(path):
    """绑定实际原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    """使用南京时间记录本轮观察。"""
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


def write(name, value):
    """只创建本轮明确新文件，不覆盖任何原件。"""
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def record(path):
    """核验真实文件再返回绑定。"""
    consumer.exact(str(path))
    return dict(path=str(path), sha256=sha(path))


def resource(binding):
    """恢复前只读ROOT六字段和当前非原子树采样；完整闭合由原guard执行。"""
    identity = consumer.identity(binding["pid"])
    assert consumer.same(identity, binding)
    root = consumer.psutil.Process(binding["pid"])
    rows = [dict(identity=consumer.identity(p.pid), rss_bytes=p.memory_info().rss)
            for p in root.children(recursive=True)]
    rss = root.memory_info().rss + sum(r["rss_bytes"] for r in rows)
    available = consumer.psutil.virtual_memory().available
    free = consumer.psutil.disk_usage("C:/").free
    assert rss < 6442450944 and available >= 536870912 and free >= 8589934592
    assert consumer.same(consumer.identity(binding["pid"]), binding)
    return dict(at_utc8=stamp(), root_identity=identity, descendants=rows,
                sampled_tree_rss_bytes=rss, available_ram_bytes=available,
                c_disk_free_bytes=free, limitation="仅当前离散非原子预核，完整活集合由guard真实闭合。")


def prepare():
    """保留r01终态和缺口，建立同ROOT身份的新监护轮次绑定。"""
    consumer.exact(str(HERE), True)
    for name in ("owned_binding_r02.json", "consumer_config_r02.json", "supervision_r02",
                 "consumer_launcher_r02", "native_consumer_r02", "monitor_recovery_r02.json"):
        assert not (HERE / name).exists(), name
    original = json.loads((HERE / "owned_binding.json").read_text(encoding="utf-8"))
    plan = json.loads((HERE / "resource_plan.json").read_text(encoding="utf-8"))
    assert original["pid"] == 25304 and original["create_time"] == 1791787378.2947657
    assert original["source_commit"] == "926c2fd382069e68e6c5ec533b7d3b6a87fbb363"
    assert (plan["new_run_tree_rss_limit_bytes"], plan["new_run_available_ram_stop_bytes"],
            plan["minimum_c_disk_free_before_dispatch_bytes"], plan["resource_sample_interval_seconds"],
            plan["supervisor_live_interval_seconds"]) == (6442450944, 536870912, 8589934592, 1, 5)
    pre = resource(original)
    log = WORK / "project_s15_r01/s2b_inference_candidate.runs/impl_1/runme.log"
    consumer.exact(str(log))
    assert log.stat().st_size > 0
    old = []
    for name in ("owned_binding.json", "resource_plan.json", "consumer_config.json", "launch.tool.json",
                 "supervision_r01/supervisor_receipt.json", "supervision_r01/supervision.jsonl",
                 "supervision_r01/guard/guard_receipt.json", "supervision_r01/guard/samples.jsonl",
                 "supervision_r01/guard/events.jsonl", "native_consumer_r01/consumer_receipt.json",
                 "native_consumer_r01/consumption.jsonl", "consumer_launcher_r01/handoff_receipt.json"):
        old.append(record(HERE / name))
    terminal = json.loads((HERE / "supervision_r01/guard/guard_receipt.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "BLOCKED" and terminal["reason"] == "INCOMPLETE_TREE_IDENTITY"
    assert "[Mon Oct 12 14:49:06 2026] Launched impl_1" in (HERE / "launch.tool.json").read_text(encoding="utf-8")
    binding = dict(original)
    binding["run_id"] = "s15_postroute_monitor_20261012_r02"
    binding["actual_heavy_run_id"] = original["run_id"]
    binding["captured_at_utc8"] = stamp()
    binding["progress_logs"] = [*original["progress_logs"], str(log)]
    write("owned_binding_r02.json", binding)
    write("monitor_recovery_r02.json", dict(status="RECOVERY_PREPARED_NOT_READY", at_utc8=stamp(),
        root_identity=pre["root_identity"], resource_precheck=pre, original_files=old,
        new_binding=record(HERE / "owned_binding_r02.json"), unchanged_plan=record(HERE / "resource_plan.json"),
        r01_guard_status=terminal["status"], r01_guard_reason=terminal["reason"],
        r01_guard_terminal_at_utc8=terminal["at_utc8"], actual_impl_launch_at_utc8="2026-10-12T14:49:06+08:00",
        launch_after_monitor_terminal=True, gap_status="BLOCKED_NOT_PROVEN_CONTINUOUS",
        limitation="本r02仅恢复后离散监护，不追认原派发连续预算，不重启impl，不证明STA或G2/G3/G5。"))
    print(json.dumps(dict(status="RECOVERY_PREPARED_NOT_READY", resource=pre), ensure_ascii=False))


def config():
    """只接受真实READY和当前存活guard，再生成新消费配置。"""
    supervision = HERE / "supervision_r02"
    assert not (supervision / "supervisor_receipt.json").exists()
    assert not (supervision / "guard/guard_receipt.json").exists()
    rows, _ = consumer.complete(str(supervision / "supervision.jsonl"))
    ready = [row for row in rows if row["kind"] == "READY"]
    assert len(ready) == 1
    actual = consumer.identity(ready[0]["guard_identity"]["pid"])
    assert consumer.same(actual, ready[0]["guard_identity"])
    old = json.loads((HERE / "consumer_config.json").read_text(encoding="utf-8"))
    for item in old["tool_bindings"]:
        assert record(Path(item["path"])) == item
    old["binding"] = record(HERE / "owned_binding_r02.json")
    old["supervision_dir"] = str(supervision)
    old["guard_identity"] = actual
    old["output_dir"] = str(HERE / "native_consumer_r02")
    write("consumer_config_r02.json", old)
    print(json.dumps(dict(status="CONFIG_BOUND_TO_REAL_READY", guard_identity=actual, at_utc8=stamp()), ensure_ascii=False))


def launch():
    """真实等待已审launcher，再由原只读准入程序验证当前离散消费。"""
    command = [sys.executable, "-X", "utf8", "-B", str(WORK / "launch_monitor.py"),
               "--config", str(HERE / "consumer_config_r02.json"),
               "--output-dir", str(HERE / "consumer_launcher_r02")]
    started = time.monotonic()
    with (HERE / "consumer_launch_r02.stdout.bin").open("xb") as out, (HERE / "consumer_launch_r02.stderr.bin").open("xb") as err:
        proc = subprocess.Popen(command, cwd=str(HERE), stdout=out, stderr=err,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        pid = proc.pid
        code = proc.wait(timeout=15)
    write("consumer_launch_r02.native.json", dict(command=command, pid=pid, direct_wait=True,
        native_exit_code=code, elapsed_seconds=time.monotonic()-started, at_utc8=stamp(),
        logs=[record(HERE / "consumer_launch_r02.stdout.bin"), record(HERE / "consumer_launch_r02.stderr.bin")]))
    assert code == 0
    command = [sys.executable, "-X", "utf8", "-B", str(HERE / "check_ready.py"),
               "--receipt", "products_admission_r02.json", "--config", "consumer_config_r02.json"]
    result = subprocess.run(command, cwd=str(HERE), capture_output=True, timeout=15,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    with (HERE / "recovery_admission_r02.stdout.bin").open("xb") as out:
        out.write(result.stdout)
    with (HERE / "recovery_admission_r02.stderr.bin").open("xb") as out:
        out.write(result.stderr)
    write("recovery_admission_r02.native.json", dict(command=command, direct_wait=True,
        native_exit_code=result.returncode, at_utc8=stamp(),
        logs=[record(HERE / "recovery_admission_r02.stdout.bin"), record(HERE / "recovery_admission_r02.stderr.bin")]))
    print(result.stdout.decode("utf-8"), end="")
    assert result.returncode == 0


def finalize():
    """保存当前真实后台身份与native会话入口，原缺口继续阻断连续预算。"""
    previous = json.loads((HERE / "monitor_recovery_r02.json").read_text(encoding="utf-8"))
    for item in previous["original_files"]:
        assert record(Path(item["path"])) == item
    cfg = json.loads((HERE / "consumer_config_r02.json").read_text(encoding="utf-8"))
    binding = consumer.load_bound(cfg["binding"])
    journal, ji = consumer.complete(str(HERE / "supervision_r02/supervision.jsonl"))
    samples, si = consumer.complete(str(HERE / "supervision_r02/guard/samples.jsonl"))
    rows, ri = consumer.complete(str(HERE / "native_consumer_r02/consumption.jsonl"))
    assert rows and all(row["status"] == "CONSUMED_LIVE_READY" and not row["blocked_latched"] for row in rows)
    assert time.monotonic() - rows[-1]["monotonic_seconds"] <= 10
    assert consumer.evaluate(journal, samples, binding, cfg["guard_identity"], [ji, si], rows[-1]["actual_gap_seconds"]) == []
    identities = dict(root=consumer.identity(binding["pid"]),
        guard=consumer.identity(cfg["guard_identity"]["pid"]),
        supervisor=consumer.identity(cfg["guard_identity"]["ppid"]),
        consumer=consumer.identity(rows[-1]["consumer_identity"]["pid"]))
    for key, expected in (("root", binding), ("guard", cfg["guard_identity"]),
                          ("consumer", rows[-1]["consumer_identity"])):
        assert consumer.same(identities[key], expected)
    for target in ("supervision_r02/supervisor_receipt.json", "supervision_r02/guard/guard_receipt.json",
                   "native_consumer_r02/consumer_receipt.json"):
        assert not (HERE / target).exists()
    receipt = dict(status="READY_CURRENT_DISCRETE_RECOVERY", at_utc8=stamp(),
        identities=identities, supervisor_native_session_id=66802,
        supervisor_native_exit_code=None, guard_native_exit_code=None, consumer_native_exit_code=None,
        consumer_launcher_native=json.loads((HERE / "consumer_launch_r02.native.json").read_text(encoding="utf-8")),
        native_admission=json.loads((HERE / "recovery_admission_r02.native.json").read_text(encoding="utf-8")),
        current_sample=samples[-1], latest_consumption=rows[-1], sample_count=len(samples), consumption_count=len(rows),
        current_stream_bindings=[ji, si, ri],
        frozen_recovery_files=[record(HERE / name) for name in (
            "monitor_recovery_r02.py", "owned_binding_r02.json", "consumer_config_r02.json",
            "monitor_recovery_r02.json", "consumer_launch_r02.native.json", "recovery_admission_r02.native.json",
            "products_admission_r02.json", "consumer_launcher_r02/handoff_receipt.json")],
        unchanged_original_files=previous["original_files"], original_gap_status="BLOCKED_NOT_PROVEN_CONTINUOUS",
        limitation="保持r02后台监护；仅本次恢复后的离散READY，不追认r01缺口、实际launch前准入或绝对峰；native未结束值保持null。")
    write("monitor_recovery_handoff_r02.json", receipt)
    print(json.dumps(dict(status=receipt["status"], at_utc8=receipt["at_utc8"], identities=identities,
        samples=len(samples), consumption_rows=len(rows), current_sample=samples[-1],
        receipt=record(HERE / "monitor_recovery_handoff_r02.json")), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "config", "launch", "finalize"))
    args = parser.parse_args()
    {"prepare": prepare, "config": config, "launch": launch, "finalize": finalize}[args.mode]()
