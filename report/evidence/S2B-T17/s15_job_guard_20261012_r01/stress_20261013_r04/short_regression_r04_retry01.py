"""短回归：并发JSONL消费者、失败样本持久化及隔离Job终态闭合。"""
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path


candidate = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()
workspace = candidate.parents[4]
smoke_dir = evidence / "short_checks_r04_retry01"
if smoke_dir.exists():
    raise SystemExit(f"短回归目录已存在，拒绝覆盖：{smoke_dir}")
smoke_dir.mkdir()
sys.path.insert(0, str(candidate))

from job_guard import JobObject, process_identity
from consumer_worker import _latest_status
import job_guard_stress as stress
from job_guard_stress import (
    DETACHED_PROCESS,
    _append_jsonl,
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


result = {
    "run_id": "S15-T17-G1-JOB-STRESS-20261013-r04-short-retry01",
    "status": "FAIL",
    "consumer": {},
    "sample_order": {},
    "fixture": {},
}
consumer = None
consumer_stderr = None
job = None
root = None
root_stderr = None
terminal = None
try:
    status_path = smoke_dir / "stress_status.jsonl"
    consumer_log = smoke_dir / "consumer_observations.jsonl"
    consumer_stderr_path = smoke_dir / "consumer_stderr.log"
    _append_jsonl(status_path, {
        "sequence": -1,
        "published_monotonic": time.monotonic(),
        "stop": False,
    })
    consumer_stderr = consumer_stderr_path.open("x", encoding="utf-8")
    consumer = subprocess.Popen(
        [sys.executable, "-u", str(candidate / "consumer_worker.py"), str(smoke_dir)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=consumer_stderr,
        text=True,
        creationflags=DETACHED_PROCESS,
        cwd=str(workspace),
    )
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
    require(ready.get("error") is None, f"consumer READY读取失败：{ready!r}")

    # 并发追加多个完整序号，消费者保持独立进程轮询共享JSONL。
    for sequence in range(5):
        _append_jsonl(status_path, {
            "sequence": sequence,
            "published_monotonic": time.monotonic(),
            "stop": False,
        })
        time.sleep(0.25)
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        observed = _latest_consumer_observation(consumer_log)
        if observed is not None and observed.get("status_sequence", -1) >= 4:
            break
        if consumer.poll() is not None:
            raise RuntimeError(f"consumer在采纳新序号前退出：{consumer.returncode}")
        time.sleep(0.05)
    observed = _latest_consumer_observation(consumer_log)
    require(observed is not None and observed.get("status_sequence") == 4, f"consumer未采纳新状态：{observed!r}")
    _append_jsonl(status_path, {
        "sequence": 4,
        "published_monotonic": time.monotonic(),
        "stop": True,
    })
    consumer.wait(timeout=5.0)
    records = [json.loads(line) for line in consumer_log.read_text(encoding="utf-8").splitlines()]
    require(consumer.returncode == 0, f"consumer退出码不是0：{consumer.returncode}")
    require(records[0].get("event") == "READY", "consumer首行不是READY")
    require(records[-1].get("event") == "STOP", "consumer末行不是STOP")
    require(all(record.get("error") is None for record in records), "consumer并发读取出现错误")
    seen_sequences = [int(record["status_sequence"]) for record in records]
    require(seen_sequences == sorted(seen_sequences), f"consumer状态序号倒退：{seen_sequences!r}")
    require("os.replace" not in (candidate / "consumer_worker.py").read_text(encoding="utf-8"), "consumer源仍调用os.replace")
    result["consumer"] = {
        "status": "PASS",
        "exit_code": consumer.returncode,
        "record_count": len(records),
        "events": [records[0]["event"], records[-1]["event"]],
        "observed_sequences": seen_sequences,
        "max_poll_gap_seconds": max(float(record.get("consumer_interval_seconds") or 0.0) for record in records),
        "max_freshness_seconds": max(float(record["status_freshness_seconds"]) for record in records),
        "error_count": sum(record.get("error") is not None for record in records),
    }
    consumer_stderr.close()
    consumer_stderr = None

    # 不完整尾行不可成为消费者采纳状态，也不影响上一条完整记录。
    tail_path = smoke_dir / "incomplete_tail.jsonl"
    complete_record = {"sequence": 7, "published_monotonic": time.monotonic(), "stop": False}
    _append_jsonl(tail_path, complete_record)
    with tail_path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write('{"sequence":8')
        stream.flush()
    latest = _latest_status(tail_path, -1, None)
    require(latest == complete_record, f"不完整尾行被采纳或完整记录丢失：{latest!r}")

    # 让验证函数在调用瞬间确认失败样本已经完成JSONL追加与flush。
    sample_path = smoke_dir / "sample_persist_before_gate.jsonl"
    raw_sample = {"sequence": 41, "uncertainty": ["synthetic_failure"]}
    original_validate = stress._validate_sample

    def verify_sample_is_persisted(sample, no_progress_seconds):
        content = sample_path.read_text(encoding="utf-8")
        require(content.endswith("\n"), "门禁评估前样本尾行尚未flush")
        persisted = [json.loads(line) for line in content.splitlines()]
        require(persisted == [raw_sample], f"门禁评估前未看到原始样本：{persisted!r}")
        return ["SYNTHETIC_GATE_STOP"]

    stress._validate_sample = verify_sample_is_persisted
    try:
        alerts = stress._persist_sample_then_validate(sample_path, raw_sample, 0.0)
    finally:
        stress._validate_sample = original_validate
    require(alerts == ["SYNTHETIC_GATE_STOP"], f"合成门禁返回异常：{alerts!r}")
    result["sample_order"] = {
        "status": "PASS",
        "persisted_before_gate": True,
        "row_count": 1,
        "synthetic_stop_alerts": alerts,
        "incomplete_tail_ignored": True,
    }

    root_stderr = (smoke_dir / "fixture_stderr.log").open("x", encoding="utf-8")
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
    lines = _start_line_reader(root.stdout)
    root_identity = process_identity(root.pid)
    session_id = "isolated-short-smoke-20261013-r04"
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
    for _ in range(10):
        target = time.monotonic() if previous_start is None else previous_start + 0.8
        _wait_until(target)
        sample = job.sample(previous_start, previous_accounting, previous_pids, previous_keys)
        sample_records.append(sample)
        require(not sample["uncertainty"], f"短测采样不确定：{sample['uncertainty']!r}")
        require(sample["sample_gap_seconds"] is None or sample["sample_gap_seconds"] <= 1.0, "短测采样间隔超限")
        previous_start = sample["sample_start_monotonic"]
        previous_accounting = sample["accounting_after"]
        previous_pids = set(sample["job_pids_after"])
        previous_keys = {(item["pid"], item["birth_ticks"]) for item in sample["member_measurements"]}
        current_pids = set(sample["job_pids_after"])
        require(worker_pid in current_pids, "worker未持续属于候选Job")
        if helper_pid not in current_pids:
            break
    require(helper_pid not in set(sample_records[-1]["job_pids_after"]), "短命helper未退出")
    require(worker_pid in set(sample_records[-1]["job_pids_after"]), "helper退出时worker也意外退出")
    exit_response = _send_root(root, lines, "EXIT")
    require(exit_response.get("event") == "EXITING" and exit_response.get("worker_exit_code") == 0, f"fixture正常退出异常：{exit_response!r}")
    terminal = job.wait_empty_and_verify(timeout_seconds=30.0)
    root.wait(timeout=5.0)
    require(root.returncode == 0, f"fixture root退出码异常：{root.returncode}")
    require(terminal.get("active_processes") == 0 and not terminal.get("job_pids"), f"Job终态仍有活动成员：{terminal!r}")
    result["fixture"] = {
        "status": "PASS",
        "ready_receipt": receipt,
        "fixture_start": started,
        "sample_count": len(sample_records),
        "max_sample_gap_seconds": max(float(item.get("sample_gap_seconds") or 0.0) for item in sample_records),
        "helper_seen_exit": True,
        "worker_stayed_until_cleanup": True,
        "terminal": terminal,
        "root_exit_code": root.returncode,
    }
    result["status"] = "PASS"
except BaseException as error:
    result["error"] = repr(error)
    result["exception_type"] = type(error).__name__
    result["traceback"] = traceback.format_exc()
finally:
    if consumer is not None and consumer.poll() is None:
        consumer.kill()
        consumer.wait(timeout=5.0)
    if consumer_stderr is not None:
        consumer_stderr.close()
    if job is not None:
        if not job.closed:
            try:
                if job.accounting()["active_processes"] > 0:
                    job.terminate_own_job(91)
                if terminal is None:
                    terminal = job.wait_empty_and_verify(timeout_seconds=30.0)
            except BaseException as error:
                result["fixture_cleanup_error"] = repr(error)
        job.close()
    if root is not None and root.poll() is None:
        try:
            root.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            result["fixture_root_still_live_after_job_close"] = True
    if root_stderr is not None:
        root_stderr.close()
    result["consumer_exit_code"] = None if consumer is None else consumer.returncode
    result["fixture_root_exit_code"] = None if root is None else root.returncode
    result["terminal_after_cleanup"] = terminal
    result_path = smoke_dir / "short_regression.result.json"
    with result_path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()

print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
raise SystemExit(0 if result["status"] == "PASS" else 1)
