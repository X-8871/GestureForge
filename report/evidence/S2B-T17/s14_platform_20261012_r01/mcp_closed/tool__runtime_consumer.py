"""原生独立消费监督流；阻断永久锁存，只向当前精确自有守卫请求停止。"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from supervisor import exact, identity, KEYS, GUARD, GUARD_SHA

TARGET_SECONDS = 5
FRESHNESS_SECONDS = 10
LIMITS = {"new_run_tree_rss_limit_bytes": 6*1024**3,
          "new_run_available_ram_stop_bytes": 512*1024**2,
          "minimum_c_disk_free_before_dispatch_bytes": 8*1024**3,
          "resource_sample_interval_seconds": 1,
          "supervisor_live_interval_seconds": 5}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def same(left, right):
    return isinstance(left, dict) and isinstance(right, dict) and all(k in left and k in right and left[k] == right[k] for k in KEYS)


def stamp():
    return datetime.now(timezone(timedelta(hours=8))).isoformat()


def load_bound(row):
    path = exact(row["path"])
    raw = path.read_bytes()
    if sha(raw) != row["sha256"]:
        raise ValueError("当前绑定原字节漂移")
    return json.loads(raw)


def complete(path):
    path = exact(path)
    raw = path.read_bytes()
    end = raw.rfind(b"\n") + 1
    rows = [json.loads(line) for line in raw[:end].splitlines() if line]
    if not rows:
        raise ValueError("没有完整JSONL记录")
    return rows, {"path": str(path), "bytes": len(raw), "sha256": sha(raw), "complete_bytes": end,
                  "trailing_bytes": len(raw)-end, "mtime_age_seconds": time.time()-path.stat().st_mtime}


def evaluate(journal, samples, binding, guard_expected, stream_info, gap):
    """纯判定保持既有10秒硬门槛；目标5秒迟延单独透明记录。"""
    reasons = []
    ready = next((row for row in journal if row.get("kind") == "READY"), None)
    terminal = next((row for row in journal if row.get("kind") == "TERMINAL"), None)
    last, sample = journal[-1], samples[-1]
    if gap is not None and gap > FRESHNESS_SECONDS:
        reasons.append("CONSUMER_GAP_GT_10S")
    if not ready or terminal:
        reasons.append("NOT_READY_OR_TERMINAL")
    expected = None if ready is None else ready.get("guard_identity")
    current = last.get("identity") if last.get("kind") == "LIVE" else last.get("guard_identity") if last.get("kind") == "READY" else None
    if not same(current, expected) or not same(expected, guard_expected):
        reasons.append("SUPERVISION_SIX_FIELD_IDENTITY_MISMATCH")
    if not sample.get("members") or not same(sample["members"][0], binding):
        reasons.append("ROOT_SIX_FIELD_IDENTITY_MISMATCH")
    if any(info["mtime_age_seconds"] < 0 or info["mtime_age_seconds"] > FRESHNESS_SECONDS for info in stream_info):
        reasons.append("STREAM_FRESHNESS_GT_10S_OR_CLOCK_CHANGE")
    try:
        sample_age = time.time()-datetime.fromisoformat(sample["sample_ended_at_utc8"]).timestamp()
        live_age = time.monotonic()-last["monotonic_seconds"]
        if not 0 <= sample_age <= FRESHNESS_SECONDS or not 0 <= live_age <= FRESHNESS_SECONDS:
            reasons.append("RECORD_FRESHNESS_GT_10S_OR_CLOCK_CHANGE")
    except (KeyError, TypeError, ValueError):
        reasons.append("RECORD_TIMESTAMP_UNKNOWN")
    if sample.get("alerts") != [] or sample.get("uncertain") != [] or sample.get("collection_observation", {}).get("closed") is not True:
        reasons.append("GUARD_ALERT_UNCERTAIN_OR_NOT_CLOSED")
    for field, limit, direction in (("tree_rss_bytes", 6*1024**3, "high"), ("available_ram_bytes", 512*1024**2, "low"), ("c_disk_free_bytes", 8*1024**3, "low")):
        value = sample.get(field)
        if type(value) is not int or value < 0 or (value > limit if direction == "high" else value < limit):
            reasons.append("RESOURCE_UNKNOWN_OR_LIMIT:"+field)
    return reasons


def request_stop(guard_expected, root_expected, guard_dir):
    """仅写精确拥有身份的请求；不终止进程，不声称heavy已结束。"""
    try:
        before_guard = identity(guard_expected["pid"])
        before_root = identity(root_expected["pid"])
        if not same(before_guard, guard_expected) or not same(before_root, root_expected):
            raise RuntimeError("停止请求前六字段身份变化")
        command = guard_expected["cmdline"]
        if command.count("--output-dir") != 1 or command[command.index("--output-dir")+1] != guard_dir or guard_expected["cwd"] != root_expected["cwd"]:
            raise RuntimeError("STOP目录或ROOT/guard的精确归属不符")
        directory = exact(guard_dir, True)
        path = directory/"STOP_REQUEST"
        if path.exists():
            raise FileExistsError("已有STOP_REQUEST不覆盖")
        # 写入前第二次完整读回，保留与守卫动作相同的保守原则。
        if not same(identity(guard_expected["pid"]), guard_expected) or not same(identity(root_expected["pid"]), root_expected):
            raise RuntimeError("停止请求动作前身份变化")
        row = {"kind": "OWNED_STOP_REQUEST", "at_utc8": stamp(), "guard_identity": before_guard, "root_identity": before_root,
               "heavy_terminal": "NOT_PROVEN", "consumer_identity": identity(os.getpid())}
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(row, ensure_ascii=False)+"\n"); stream.flush(); os.fsync(stream.fileno())
        return {"status": "REQUEST_WRITTEN", "path": str(path), "sha256": sha(path.read_bytes()), "heavy_terminal": "NOT_PROVEN"}
    except (OSError, ValueError, RuntimeError, psutil.Error) as error:
        return {"status": "STOP_REJECTED_IDENTITY_OR_PATH", "error": repr(error), "heavy_terminal": "UNKNOWN"}


def run(config, config_binding):
    binding = load_bound(config["binding"])
    plan = load_bound(config["plan"])
    if any(plan.get(k) != v for k, v in LIMITS.items()):
        raise ValueError("固定采样或资源阈值不同")
    if not all(k in binding for k in KEYS) or not same(identity(binding["pid"]), binding):
        raise ValueError("ROOT启动六字段身份未知或不同")
    supervision = exact(config["supervision_dir"], True)
    guard_expected = config["guard_identity"]
    if not same(identity(guard_expected["pid"]), guard_expected):
        raise ValueError("guard启动六字段身份不同")
    expected_command = [sys.executable, "-X", "utf8", "-B", str(exact(str(GUARD))), "--plan", config["plan"]["path"], "--binding", config["binding"]["path"], "--output-dir", str(supervision/"guard")]
    if sha(GUARD.read_bytes()) != GUARD_SHA or guard_expected["cmdline"] != expected_command or guard_expected["cwd"] != binding["cwd"]:
        raise ValueError("固定guard/SHA/启动argv/当前cwd不同")
    for row in config["tool_bindings"]:
        if sha(exact(row["path"]).read_bytes()) != row["sha256"]:
            raise ValueError("工具SHA漂移")
    out = Path(config["output_dir"])
    exact(out.parent, True)
    if out.exists():
        raise FileExistsError("新consumer目录已存在")
    out.mkdir()
    began = time.monotonic(); next_tick = began; previous = None; index = 0; blocked = False
    own = identity(os.getpid()); final = None
    with (out/"consumption.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
        while True:
            tick = time.monotonic(); gap = None if previous is None else tick-previous
            row = {"index": index, "at_utc8": stamp(), "monotonic_seconds": tick, "actual_gap_seconds": gap,
                   "target_interval_seconds": TARGET_SECONDS, "freshness_limit_seconds": FRESHNESS_SECONDS,
                   "deadline_delay_seconds": max(0, tick-next_tick), "target_deadline_missed": gap is not None and gap>TARGET_SECONDS,
                   "consumer_identity": own}
            reasons = []
            try:
                if load_bound(config_binding) != config or load_bound(config["binding"]) != binding or load_bound(config["plan"]) != plan:
                    raise ValueError("配置或当前binding漂移")
                for bound in config["tool_bindings"]:
                    if sha(exact(bound["path"]).read_bytes()) != bound["sha256"]:
                        raise ValueError("运行中工具SHA漂移")
                if not same(identity(own["pid"]), own) or not same(identity(guard_expected["pid"]), guard_expected) or not same(identity(binding["pid"]), binding):
                    raise RuntimeError("现时六字段身份变化")
                journal, ji = complete(str(supervision/"supervision.jsonl"))
                samples, si = complete(str(supervision/"guard"/"samples.jsonl"))
                reasons = evaluate(journal, samples, binding, guard_expected, [ji, si], gap)
                if (supervision/"guard"/"guard_receipt.json").exists() or (supervision/"supervisor_receipt.json").exists():
                    reasons.append("TERMINAL_RECEIPT_PRESENT")
                row.update(stream_bindings=[ji, si], latest_sample=samples[-1], last_supervision=journal[-1])
            except (OSError, ValueError, KeyError, TypeError, RuntimeError, psutil.Error) as error:
                reasons.append("READ_OR_IDENTITY_UNKNOWN:"+repr(error))
            blocked = blocked or bool(reasons)
            row.update(status="BLOCKED_RUNTIME_MONITOR" if blocked else "CONSUMED_LIVE_READY", blocked_latched=blocked, reasons=reasons)
            if blocked:
                row["stop_request"] = request_stop(guard_expected, binding, str(supervision/"guard"))
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+"\n"); stream.flush(); os.fsync(stream.fileno())
            index += 1; previous = tick
            if blocked:
                final = row; break
            next_tick += TARGET_SECONDS
            time.sleep(max(0, next_tick-time.monotonic()))
    raw = (out/"consumption.jsonl").read_bytes()
    receipt = {"status": "BLOCKED_RUNTIME_MONITOR", "native_exit_code": 2, "blocked_latched": True, "last": final,
               "samples": index, "elapsed_seconds": time.monotonic()-began, "consumer_identity": own,
               "consumption_jsonl_sha256": sha(raw), "consumption_jsonl_bytes": len(raw),
               "heavy_terminal": "NOT_PROVEN", "absolute_tree_peak_bytes": None,
               "limitations": ["原生独立进程不依赖ROSS等待，但调度不是固定5秒；所有实际gap保留。", "STOP_REQUEST不是heavy结束证明；终态及连续峰须另行实际核验。"]}
    with (out/"consumer_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write("\n")
    return 2


def launch(config_path, stdout_path, stderr_path):
    """供ROOT单次原生启动后移交MCP等待；返回实际consumer六字段身份。"""
    path = exact(config_path)
    command = [sys.executable, "-X", "utf8", "-B", str(Path(__file__).absolute()), "--config", str(path)]
    exact(Path(stdout_path).parent, True); exact(Path(stderr_path).parent, True)
    with Path(stdout_path).open("xb") as so, Path(stderr_path).open("xb") as se:
        child = subprocess.Popen(command, cwd=os.getcwd(), stdout=so, stderr=se, creationflags=subprocess.CREATE_NO_WINDOW)
    actual = identity(child.pid)
    if actual["cmdline"] != command:
        raise RuntimeError("consumer原生启动身份不同")
    return child, {"command": command, "identity": actual, "direct_child_poll": child.poll(), "handoff": "NATIVE_BACKGROUND_RUNNING" if child.poll() is None else "TERMINAL_BEFORE_HANDOFF"}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--config", required=True); args = parser.parse_args()
    path = exact(args.config); raw = path.read_bytes(); binding = {"path": str(path), "sha256": sha(raw)}
    return run(json.loads(raw), binding)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, psutil.Error) as error:
        print(json.dumps({"status": "BLOCKED_STARTUP", "error": repr(error), "heavy_terminal": "UNKNOWN"}, ensure_ascii=False)); raise SystemExit(2)
