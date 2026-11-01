import json
import subprocess
import sys
import time
from pathlib import Path


candidate = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()
workspace = candidate.parents[4]
smoke_dir = evidence / "short_checks"
if smoke_dir.exists():
    raise SystemExit("短回归目录已存在，拒绝覆盖")
smoke_dir.mkdir()
sys.path.insert(0, str(candidate))

from job_guard import JobObject, process_identity
from job_guard_stress import (
    DETACHED_PROCESS,
    _atomic_json,
    _fixture_code,
    _latest_consumer_observation,
    _read_response,
    _send_root,
    _start_line_reader,
    _wait_until,
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


consumer_status = smoke_dir / "consumer_status.json"
consumer_log = smoke_dir / "consumer_observations.jsonl"
consumer_stderr_path = smoke_dir / "consumer_stderr.log"
_atomic_json(consumer_status, {
    "sequence": -1,
    "published_monotonic": time.monotonic(),
    "stop": False,
})
consumer_stderr = consumer_stderr_path.open("w", encoding="utf-8")
consumer = subprocess.Popen(
    [sys.executable, "-u", str(candidate / "consumer_worker.py"), str(smoke_dir)],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=consumer_stderr,
    text=True,
    creationflags=DETACHED_PROCESS,
    cwd=str(workspace),
)
consumer_result = {}
try:
    deadline = time.monotonic() + 5.0
    ready = None
    while time.monotonic() < deadline:
        ready = _latest_consumer_observation(consumer_log)
        if ready is not None:
            break
        if consumer.poll() is not None:
            raise RuntimeError(f"consumer READY前退出：{consumer.returncode}")
        time.sleep(0.05)
    require(ready is not None and ready.get("event") == "READY", f"consumer未发READY：{ready!r}")
    require(ready.get("error") is None, f"consumer READY错误：{ready!r}")
    time.sleep(1.1)
    poll = _latest_consumer_observation(consumer_log)
    require(poll is not None and poll.get("event") == "POLL", f"consumer未追加POLL：{poll!r}")
    _atomic_json(consumer_status, {
        "sequence": 0,
        "published_monotonic": time.monotonic(),
        "stop": True,
    })
    consumer.wait(timeout=5.0)
    records = [json.loads(line) for line in consumer_log.read_text(encoding="utf-8").splitlines()]
    require(consumer.returncode == 0, f"consumer退出码不是0：{consumer.returncode}")
    require(records[0].get("event") == "READY", "consumer首行不是READY")
    require(records[-1].get("event") == "STOP", "consumer末行不是STOP")
    require(len(records) >= 3, f"append-only观察行不足：{len(records)}")
    consumer_result = {
        "status": "PASS",
        "exit_code": consumer.returncode,
        "record_count": len(records),
        "events": [records[0]["event"], records[-1]["event"]],
        "max_interval_seconds": max(
            float(record.get("consumer_interval_seconds") or 0.0) for record in records
        ),
        "replace_in_consumer_source": "os.replace" in (candidate / "consumer_worker.py").read_text(encoding="utf-8"),
    }
    require(not consumer_result["replace_in_consumer_source"], "consumer仍包含os.replace")
finally:
    if consumer.poll() is None:
        consumer.kill()
        consumer.wait(timeout=5.0)
    consumer_stderr.close()


root_stderr = (smoke_dir / "fixture_stderr.log").open("w", encoding="utf-8")
job = JobObject()
root = subprocess.Popen(
    [sys.executable, "-u", "-c", _fixture_code()],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=root_stderr,
    text=True,
    creationflags=DETACHED_PROCESS,
    cwd=str(workspace),
)
terminal = None
fixture_result = {}
try:
    lines = _start_line_reader(root.stdout)
    root_identity = process_identity(root.pid)
    session_id = "isolated-short-smoke-20261013-r03"
    ross_record = {
        "input": {"session_id": session_id},
        "result": {"content": [{"type": "text", "text": json.dumps({
            "session_id": session_id,
            "status": "idle",
            "active_command": None,
            "root_identity": root_identity,
        }, separators=(",", ":"))}]},
    }
    receipt, ready_token = job.attach_idle_root(ross_record)
    require(receipt.get("kind") == "READY", f"没有READY收据：{receipt!r}")
    previous_accounting = job.accounting()
    previous_pids = set(job.pid_list())
    previous_keys = set(job._baseline_keys)
    job.dispatch_after_ready(ready_token, root.stdin, "START_FIXTURE_HEAVY")
    started = _read_response(lines, timeout=5.0)
    require(started.get("event") == "STARTED", f"fixture未在READY后启动：{started!r}")
    helper_pid = int(started["helper_pid"])
    worker_pid = int(started["worker_pid"])
    sample_records = []
    previous_start = None
    for index in range(10):
        if previous_start is None:
            target = time.monotonic()
        else:
            target = previous_start + 0.8
        _wait_until(target)
        sample = job.sample(previous_start, previous_accounting, previous_pids, previous_keys)
        sample_records.append(sample)
        require(not sample["uncertainty"], f"短测采样不确定：{sample['uncertainty']!r}")
        require(
            sample["sample_gap_seconds"] is None or sample["sample_gap_seconds"] <= 1.0,
            f"短测采样间隔超限：{sample['sample_gap_seconds']}",
        )
        previous_start = sample["sample_start_monotonic"]
        previous_accounting = sample["accounting_after"]
        previous_pids = set(sample["job_pids_after"])
        previous_keys = {(item["pid"], item["birth_ticks"]) for item in sample["member_measurements"]}
        current_pids = set(sample["job_pids_after"])
        require(worker_pid in current_pids, "worker未持续属于候选Job")
        if helper_pid not in current_pids:
            break
    require(sample_records[-1]["job_pids_after"], "Job成员读回为空")
    require(helper_pid not in set(sample_records[-1]["job_pids_after"]), "短命helper未在短测中退出")
    require(worker_pid in set(sample_records[-1]["job_pids_after"]), "helper退出时worker也意外退出")
    exit_response = _send_root(root, lines, "EXIT")
    require(
        exit_response.get("event") == "EXITING" and exit_response.get("worker_exit_code") == 0,
        f"fixture正常退出回应异常：{exit_response!r}",
    )
    terminal = job.wait_empty_and_verify(timeout_seconds=30.0)
    root.wait(timeout=5.0)
    require(root.returncode == 0, f"fixture root退出码异常：{root.returncode}")
    fixture_result = {
        "status": "PASS",
        "receipt_kind": receipt.get("kind"),
        "fixture_start": started,
        "sample_count": len(sample_records),
        "max_sample_gap_seconds": max(
            float(item.get("sample_gap_seconds") or 0.0) for item in sample_records
        ),
        "helper_seen_exit": helper_pid not in set(sample_records[-1]["job_pids_after"]),
        "worker_stayed_until_cleanup": worker_pid in set(sample_records[-1]["job_pids_after"]),
        "terminal": terminal,
        "root_exit_code": root.returncode,
    }
finally:
    if job is not None:
        if not job.closed:
            try:
                if job.accounting()["active_processes"] > 0:
                    job.terminate_own_job(91)
                if terminal is None:
                    terminal = job.wait_empty_and_verify(timeout_seconds=30.0)
            except BaseException as error:
                fixture_result["cleanup_error"] = repr(error)
        job.close()
    if root.poll() is None:
        root.wait(timeout=5.0)
    root_stderr.close()

result = {
    "run_id": "S15-T17-G1-JOB-STRESS-20261013-r03-short",
    "consumer": consumer_result,
    "fixture": fixture_result,
    "terminal": terminal,
}
(smoke_dir / "short_regression.result.json").write_text(
    json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
