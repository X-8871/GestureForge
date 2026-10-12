"""只读核对最后一次综合的已知进程身份和监护原件，不终止或重启进程。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import psutil

HERE = Path(__file__).resolve().parent


def read(path):
    """读取精确 UTF-8 原件。"""
    assert path.is_file() and not path.is_symlink()
    return json.loads(path.read_text(encoding="utf-8"))


def identities(value, result):
    """仅枚举原件内已取得出生时间的身份，不猜测未知 PID。"""
    if isinstance(value, dict):
        if isinstance(value.get("pid"), int) and isinstance(value.get("create_time"), (int, float)):
            result[(value["pid"], value["create_time"])] = value
        for child in value.values():
            identities(child, result)
    elif isinstance(value, list):
        for child in value:
            identities(child, result)


known = {}
rounds = []
for index in (1, 2, 3):
    directory = HERE / f"supervision_r{index:02}"
    sample_path = directory / "guard" / "samples.jsonl"
    raw = sample_path.read_bytes()
    assert raw.endswith(b"\n"), "结束后的样本文件仍有不完整行"
    samples = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line]
    identities(samples, known)
    guard = read(directory / "guard" / "guard_receipt.json")
    supervisor = read(directory / "supervisor_receipt.json")
    consumer = read(HERE / f"native_consumer_r{index:02}" / "consumer_receipt.json")
    identities([guard, supervisor, consumer], known)
    valid = [row for row in samples if isinstance(row.get("tree_rss_bytes"), int)]
    rounds.append({
        "round": index, "sample_count": len(samples),
        "guard_status": guard.get("status"), "guard_native_exit_code": supervisor.get("child_native_exit_code"),
        "supervisor_exit_code": supervisor.get("supervisor_exit_code"),
        "consumer_status": consumer.get("status"), "consumer_native_exit_code": consumer.get("native_exit_code"),
        "valid_tree_sample_count": len(valid), "unclosed_sample_count": len(samples) - len(valid),
        "sampled_valid_tree_peak_bytes": max((row["tree_rss_bytes"] for row in valid), default=None),
        "minimum_available_ram_bytes": min((row["available_ram_bytes"] for row in samples), default=None),
        "minimum_c_disk_free_bytes": min((row["c_disk_free_bytes"] for row in samples), default=None),
        "sample_start_gaps_above_target_1s": sum(row.get("actual_start_gap_seconds", 0) > 1 for row in samples),
        "alerts": [row["alerts"] for row in samples if row.get("alerts")],
        "sample_file": str(sample_path), "sample_sha256": hashlib.sha256(raw).hexdigest(),
        "first_at_utc8": samples[0]["at_utc8"], "last_at_utc8": samples[-1]["at_utc8"],
    })
binding = read(HERE / "owned_binding.json")
identities(binding, known)
observations = []
for (pid, birth), expected in sorted(known.items()):
    row = {"expected": expected}
    try:
        process = psutil.Process(pid)
        observed_birth = process.create_time()
        if observed_birth != birth:
            row.update(status="REUSED_OLD_IDENTITY_ABSENT", observed_create_time=observed_birth)
        else:
            current = {"pid": pid, "create_time": observed_birth, "exe": process.exe(),
                       "cwd": process.cwd(), "cmdline": process.cmdline(), "ppid": process.ppid()}
            row.update(status="SAME_BIRTH_LIVE", current=current,
                       six_fields_match=all(current.get(k) == expected.get(k) for k in current))
    except psutil.NoSuchProcess as error:
        row.update(status="ABSENT", original_error=repr(error))
    except Exception as error:
        row.update(status="UNKNOWN", original_error=repr(error))
    observations.append(row)
root = next(row for row in observations if row["expected"].get("pid") == binding["pid"]
            and row["expected"].get("create_time") == binding["create_time"])
assert root["status"] in ("ABSENT", "REUSED_OLD_IDENTITY_ABSENT"), "owned ROOT 未确认退出"
result = {
    "status": "CLOSED_ROOT_OBSERVED_ONLY", "created_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "source_commit": binding["source_commit"], "root_observation": root,
    "known_identity_observations": observations, "monitor_rounds": rounds,
    "sampled_valid_tree_peak_bytes": max((r["sampled_valid_tree_peak_bytes"] for r in rounds
                                         if r["sampled_valid_tree_peak_bytes"] is not None), default=None),
    "continuous_budget_status": "NOT_PROVEN_THREE_BLOCKED_GUARD_ROUNDS_AND_GAPS",
    "entire_os_tree_terminal": "NOT_PROVEN_BY_DISCRETE_KNOWN_IDENTITY_ENUMERATION",
    "five_native_job_os_exit_codes": None,
    "limits": {"tree_rss_bytes": 6442450944, "available_ram_bytes": 536870912, "c_disk_free_bytes": 8589934592},
    "current_available_ram_bytes": psutil.virtual_memory().available,
    "current_c_disk_free_bytes": psutil.disk_usage("C:\\").free,
    "hardware": "NOT_RUN", "implementation": "NOT_RUN", "new_synthesis": "NOT_RUN",
}
with (HERE / "closed_runtime_observation.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": result["status"], "root_status": root["status"],
                  "known_identity_count": len(observations), "rounds": rounds,
                  "continuous_budget_status": result["continuous_budget_status"]}, ensure_ascii=False))
