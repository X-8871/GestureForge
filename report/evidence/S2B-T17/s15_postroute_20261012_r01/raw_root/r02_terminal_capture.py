"""只读闭合r02监护身份并绑定真实native原件；不停止任何对象。"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).parent
WORK = HERE.parents[3] / "tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02"
sys.path.insert(0, str(WORK))
import runtime_consumer as consumer


def binding(path):
    """精确原文件字节绑定。"""
    consumer.exact(str(path))
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def load(name):
    """读取真实原件，不修改。"""
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def observe(expected):
    """逐身份观察ABSENT/复用/仍活/未知；不把UNKNOWN改为已退出。"""
    row = dict(expected=expected, observed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
    try:
        actual = consumer.identity(expected["pid"])
        row["actual"] = actual
        if actual["create_time"] != expected["create_time"]:
            row["status"] = "ORIGINAL_ABSENT_PID_REUSED"
        elif consumer.same(actual, expected):
            row["status"] = "ALIVE_SAME_IDENTITY"
        else:
            row["status"] = "UNKNOWN_METADATA_DRIFT"
    except consumer.psutil.NoSuchProcess as error:
        row.update(status="ORIGINAL_ABSENT", error=repr(error))
    except (consumer.psutil.Error, RuntimeError, ValueError) as error:
        row.update(status="UNKNOWN", error=repr(error))
    return row


def main():
    """只写新的终态回执和完整索引，保留预算阻断和host差异。"""
    started = time.monotonic()
    for name in ("r02_terminal_receipt.json", "r02_terminal_index.json"):
        assert not (HERE / name).exists()
    handoff = load("monitor_recovery_handoff_r02.json")
    for item in handoff["frozen_recovery_files"] + handoff["unchanged_original_files"]:
        assert binding(Path(item["path"]))["sha256"] == item["sha256"]
    host = load("r02_terminal_host.tool.json")
    emitted = json.loads(host["result"]["output"])
    sup = load("supervision_r02/supervisor_receipt.json")
    guard = load("supervision_r02/guard/guard_receipt.json")
    consumed = load("native_consumer_r02/consumer_receipt.json")
    assert emitted["receipt_sha256"] == binding(HERE / "supervision_r02/supervisor_receipt.json")["sha256"]
    assert sup["child_native_exit_code"] == emitted["child_native_exit_code"] == 3
    assert sup["supervisor_exit_code"] == emitted["supervisor_exit_code"] == 2
    assert guard["status"] == "BLOCKED" and consumed["native_exit_code"] == 2
    identities = handoff["identities"]
    observations = {name: observe(identities[name]) for name in ("supervisor", "guard", "consumer", "root")}
    members = { (r["pid"], r["create_time"]): r for r in handoff["current_sample"]["members"] }
    for row in guard.get("confirmed_sample_exits", []):
        expected = row.get("expected")
        if expected:
            members[(expected["pid"], expected["create_time"])] = expected
    descendants = [observe(expected) for expected in members.values() if expected["pid"] != identities["root"]["pid"]]
    absent = ("ORIGINAL_ABSENT", "ORIGINAL_ABSENT_PID_REUSED")
    monitor_closed = all(observations[name]["status"] in absent for name in ("supervisor", "guard", "consumer"))
    names = ["r02_terminal_capture.py", "r02_terminal_host.tool.json", "r02_terminal_capture_first_failure.json", "monitor_recovery_handoff_r02.json",
        "monitor_recovery_r02.py", "owned_binding_r02.json", "consumer_config_r02.json",
        "monitor_recovery_r02.json", "products_admission_r02.json", "consumer_launch_r02.native.json",
        "recovery_admission_r02.native.json", "consumer_launcher_r02/handoff_receipt.json",
        "consumer_launcher_r02/stdout.bin", "consumer_launcher_r02/stderr.bin",
        "supervision_r02/supervisor_receipt.json", "supervision_r02/supervision.jsonl",
        "supervision_r02/stdout.log", "supervision_r02/stderr.log",
        "supervision_r02/guard/guard_receipt.json", "supervision_r02/guard/samples.jsonl",
        "supervision_r02/guard/events.jsonl", "native_consumer_r02/consumer_receipt.json",
        "native_consumer_r02/consumption.jsonl"]
    index = [binding(HERE / name) for name in names]
    for item in guard["files"]:
        assert binding(HERE / "supervision_r02/guard" / item["path"])["sha256"] == item["sha256"]
    assert binding(HERE / "native_consumer_r02/consumption.jsonl")["sha256"] == consumed["consumption_jsonl_sha256"]
    value = dict(status="MONITOR_ORIGINAL_IDENTITIES_ABSENT" if monitor_closed else "BLOCKED_MONITOR_IDENTITY_UNKNOWN_OR_ALIVE",
        at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(), source_commit=guard["source_commit"],
        supervisor_native_session_id=66802, host_tool_exit_code=host["result"]["exit_code"],
        supervisor_self_reported_exit_code=sup["supervisor_exit_code"],
        guard_direct_child_wait_exit_code=sup["child_native_exit_code"],
        consumer_terminal_self_reported_exit_code=consumed["native_exit_code"], consumer_direct_parent_wait="NOT_AVAILABLE",
        identity_observations=observations, known_descendant_observations=descendants,
        known_pnr_original_descendants_absent=all(row["status"] in absent for row in descendants),
        guard_status=guard["status"], guard_reason=guard["reason"], guard_terminal_at_utc8=guard["at_utc8"],
        guard_samples=guard["samples"], sampled_peak_tree_rss_bytes=guard["sampled_peak_tree_rss_bytes"],
        minimum_sampled_available_ram_bytes=guard["minimum_sampled_available_ram_bytes"],
        minimum_sampled_c_disk_free_bytes=guard["minimum_sampled_c_disk_free_bytes"],
        consumer_status=consumed["status"], consumer_samples=consumed["samples"],
        consumer_blocked_latched=consumed["blocked_latched"], consumer_reasons=consumed["last"]["reasons"],
        continuous_budget_status="BLOCKED_NOT_PROVEN_CONTINUOUS", absolute_tree_peak_bytes=None,
        implementation_sta_validation="NOT_IN_SCOPE", readonly_elapsed_seconds=time.monotonic()-started,
        original_file_index=index,
        limitations=["监护身份现在已退出不消除r01/r02预算缺口和UNKNOWN原件。",
            "ROOT close_project与STA由ROOT独立证据负责；本工具不执行ROSS或证明整树历史连续闭合。",
            "host返回1、SUP自报2、guard子wait3、consumer终态自报2按真实来源分列。",
            "仅观察原owned已知成员；PID复用对象和未知对象不动，无stop调用。"])
    with (HERE / "r02_terminal_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write("\n")
    for item in index:
        assert binding(Path(item["path"])) == item
    with (HERE / "r02_terminal_index.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(index + [binding(HERE / "r02_terminal_receipt.json")], stream, ensure_ascii=False, indent=2); stream.write("\n")
    print(json.dumps(dict(status=value["status"], monitor={name: row["status"] for name,row in observations.items()},
        descendants={str(row["expected"]["pid"]): row["status"] for row in descendants},
        guard_reason=guard["reason"], samples=guard["samples"], consumer_samples=consumed["samples"],
        receipt=binding(HERE / "r02_terminal_receipt.json"), index=binding(HERE / "r02_terminal_index.json")), ensure_ascii=False))


if __name__ == "__main__":
    main()
