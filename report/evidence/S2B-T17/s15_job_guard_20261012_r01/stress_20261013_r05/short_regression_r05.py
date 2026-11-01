"""短回归：时间与终态负例、JSONL消费者、样本持久化及Job闭合。"""
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path


candidate = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()
workspace = candidate.parents[4]
smoke_dir = evidence / "short_checks_r05"
if smoke_dir.exists():
    raise SystemExit(f"短回归目录已存在，拒绝覆盖：{smoke_dir}")
smoke_dir.mkdir()
sys.path.insert(0, str(candidate))

from job_guard import JobObject, process_identity
import consumer_worker
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


def _write_jsonl(path, records):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, allow_nan=True, separators=(",", ":")) + "\n")
        stream.flush()


def _status(sequence, published, stop=False):
    return {"sequence": sequence, "published_monotonic": published, "stop": stop}


def _expect_status_rejection(directory, name, records):
    path = directory / f"status_negative_{name}.jsonl"
    _write_jsonl(path, records)
    try:
        _latest_status(path, -1, None)
    except (OverflowError, TypeError, ValueError, json.JSONDecodeError):
        return {"case": name, "rejected": True}
    raise RuntimeError(f"状态负例被接受：{name}")


def _observation(event, observed, interval=None, maximum=0.0, sequence=-1,
                 freshness=0.5, stopping=False, error=None):
    return {
        "event": event,
        "observed_monotonic": observed,
        "consumer_interval_seconds": interval,
        "consumer_max_poll_gap_seconds": maximum,
        "status_sequence": sequence,
        "status_freshness_seconds": freshness,
        "status_stop": stopping,
        "error": error,
    }


def _expect_observation_rejection(directory, name, records):
    path = directory / f"observation_negative_{name}.jsonl"
    _write_jsonl(path, records)
    try:
        _latest_consumer_observation(path)
    except stress.GateBlocked:
        return {"case": name, "rejected": True}
    raise RuntimeError(f"父级消费者观察负例被接受：{name}")


def _wait_for_observation(path, process, count, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            raw = path.read_text(encoding="utf-8")
            lines = raw.splitlines()
            if len(lines) >= count and (not raw or raw.endswith("\n")):
                return [json.loads(line) for line in lines]
        if process.poll() is not None:
            raise RuntimeError(f"负例consumer提前退出：{process.returncode}")
        time.sleep(0.05)
    raise RuntimeError(f"负例consumer观察记录未达到{count}条")


result = {
    "run_id": "S15-T17-G1-JOB-STRESS-20261013-r05-short",
    "status": "FAIL",
    "negative_status_direct": {},
    "negative_status_process": {},
    "negative_parent_observations": {},
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
    negative_dir = smoke_dir / "negative_cases"
    negative_dir.mkdir()
    base_time = time.monotonic() - 60.0
    status_negative_records = {
        "future_publish": [_status(-1, time.monotonic() + 60.0)],
        "nan_publish": [_status(-1, float("nan"))],
        "infinite_publish": [_status(-1, float("inf"))],
        "negative_publish": [_status(-1, -1.0)],
        "string_publish": [_status(-1, "123.0")],
        "stop_then_higher_false": [
            _status(-1, base_time), _status(0, base_time + 1.0, True), _status(1, base_time + 2.0, False)
        ],
        "stop_then_same_false": [
            _status(-1, base_time), _status(0, base_time + 1.0, True), _status(0, base_time + 2.0, False)
        ],
        "sequence_descending": [
            _status(-1, base_time), _status(0, base_time + 1.0), _status(1, base_time + 2.0),
            _status(0, base_time + 3.0)
        ],
        "sequence_out_of_range": [_status(-1, base_time), _status(602, base_time + 1.0)],
        "sequence_boolean": [_status(-1, base_time), _status(True, base_time + 1.0)],
        "sequence_gap": [_status(-1, base_time), _status(1, base_time + 1.0)],
        "publish_time_descending": [_status(-1, base_time), _status(0, base_time - 1.0)],
        "stop_field_invalid": [{"sequence": -1, "published_monotonic": base_time, "stop": 0}],
    }
    direct_status_results = [
        _expect_status_rejection(negative_dir, name, records)
        for name, records in status_negative_records.items()
    ]
    valid_status_path = negative_dir / "status_valid_controls.jsonl"
    _write_jsonl(valid_status_path, [
        _status(-1, base_time), _status(0, base_time + 1.0), _status(1, base_time + 2.0)
    ])
    valid_status = _latest_status(valid_status_path, -1, None)
    require(valid_status["sequence"] == 1 and valid_status["stop"] is False, "合法状态正例未通过")
    valid_stop_path = negative_dir / "status_valid_terminal_stop.jsonl"
    _write_jsonl(valid_stop_path, [
        _status(-1, base_time), _status(0, base_time + 1.0), _status(0, base_time + 2.0, True)
    ])
    valid_stop = _latest_status(valid_stop_path, -1, None)
    require(valid_stop["sequence"] == 0 and valid_stop["stop"] is True, "合法终态STOP正例未通过")
    result["negative_status_direct"] = {
        "status": "PASS",
        "rejected_cases": direct_status_results,
        "valid_status_control": valid_status,
        "valid_stop_control": valid_stop,
    }

    process_negative_names = (
        "future_publish", "nan_publish", "infinite_publish", "stop_then_higher_false",
        "sequence_descending", "sequence_out_of_range", "negative_publish"
    )
    process_negative_results = []
    for name in process_negative_names:
        case_dir = negative_dir / f"consumer_{name}"
        case_dir.mkdir()
        status_file = case_dir / "stress_status.jsonl"
        _write_jsonl(status_file, status_negative_records[name])
        stderr_path = case_dir / "consumer_stderr.log"
        with stderr_path.open("x", encoding="utf-8") as stderr_stream:
            process = subprocess.Popen(
                [sys.executable, "-u", str(candidate / "consumer_worker.py"), str(case_dir)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=stderr_stream,
                text=True,
                creationflags=DETACHED_PROCESS,
                cwd=str(workspace),
            )
            observations = _wait_for_observation(case_dir / "consumer_observations.jsonl", process, 2)
            events = [record["event"] for record in observations]
            require(events[0] == "READY_ERROR" and events[1] == "ERROR", f"非法状态未持续报告错误：{name} {events!r}")
            require(
                all(record.get("error") and record.get("status_sequence") == -1 for record in observations),
                f"非法状态意外推进消费者序号：{name} {observations!r}",
            )
            require(
                not any(event in {"READY", "POLL", "STOP"} for event in events),
                f"非法状态被报告为可用状态：{name} {events!r}",
            )
            process.kill()
            process.wait(timeout=5.0)
        process_negative_results.append({
            "case": name,
            "events": events,
            "usable_ready_state": False,
            "process_stopped_by_harness": True,
        })
    result["negative_status_process"] = {
        "status": "PASS",
        "cases": process_negative_results,
    }

    observation_base = time.monotonic() - 60.0
    ready_observation = _observation("READY", observation_base)
    poll_observation = _observation(
        "POLL", observation_base + 1.0, interval=1.0, maximum=1.0, sequence=0, freshness=0.25
    )
    parent_observation_cases = {
        "future_observed": [_observation("READY", time.monotonic() + 60.0)],
        "nan_observed": [_observation("READY", float("nan"))],
        "infinite_observed": [_observation("READY", float("inf"))],
        "negative_observed": [_observation("READY", -1.0)],
        "observed_wrong_type": [_observation("READY", "monotonic")],
        "negative_interval": [ready_observation, _observation("POLL", observation_base + 1.0, interval=-1.0, maximum=0.0, sequence=0)],
        "nan_interval": [ready_observation, _observation("POLL", observation_base + 1.0, interval=float("nan"), maximum=0.0, sequence=0)],
        "infinite_interval": [ready_observation, _observation("POLL", observation_base + 1.0, interval=float("inf"), maximum=0.0, sequence=0)],
        "interval_over_limit": [ready_observation, _observation("POLL", observation_base + 6.0, interval=6.0, maximum=6.0, sequence=0)],
        "interval_mismatch": [ready_observation, _observation("POLL", observation_base + 1.0, interval=0.5, maximum=0.5, sequence=0)],
        "sequence_out_of_range": [_observation("READY", observation_base, sequence=602)],
        "sequence_boolean": [_observation("READY", observation_base, sequence=True)],
        "sequence_negative": [_observation("READY", observation_base, sequence=-2)],
        "sequence_descending": [ready_observation, poll_observation, _observation("POLL", observation_base + 2.0, interval=1.0, maximum=1.0, sequence=-1)],
        "nan_freshness": [_observation("READY", observation_base, freshness=float("nan"))],
        "infinite_freshness": [_observation("READY", observation_base, freshness=float("inf"))],
        "negative_freshness": [_observation("READY", observation_base, freshness=-0.1)],
        "freshness_over_limit": [_observation("READY", observation_base, freshness=10.1)],
        "nan_max_interval": [_observation("READY", observation_base, maximum=float("nan"))],
        "infinite_max_interval": [_observation("READY", observation_base, maximum=float("inf"))],
        "max_interval_over_limit": [_observation("READY", observation_base, maximum=5.1)],
        "status_stop_not_bool": [_observation("READY", observation_base, stopping=1)],
        "ready_with_error": [_observation("READY", observation_base, error="bad")],
        "stop_without_terminal_flag": [_observation("STOP", observation_base, stopping=False)],
        "stop_then_poll": [
            _observation("READY", observation_base),
            _observation("STOP", observation_base + 1.0, interval=1.0, maximum=1.0, sequence=0, stopping=True),
            _observation("POLL", observation_base + 2.0, interval=1.0, maximum=1.0, sequence=1),
        ],
        "observation_time_descending": [ready_observation, _observation("POLL", observation_base - 1.0, interval=1.0, maximum=1.0, sequence=0)],
    }
    direct_parent_results = [
        _expect_observation_rejection(negative_dir, name, records)
        for name, records in parent_observation_cases.items()
    ]
    parent_control_path = negative_dir / "observation_valid_control.jsonl"
    _write_jsonl(parent_control_path, [ready_observation, poll_observation])
    parent_control = _latest_consumer_observation(parent_control_path)
    require(parent_control["event"] == "POLL" and parent_control["status_sequence"] == 0, "合法父级观察正例未通过")
    result["negative_parent_observations"] = {
        "status": "PASS",
        "rejected_cases": direct_parent_results,
        "valid_observation_control": parent_control,
    }

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
    complete_record = {"sequence": -1, "published_monotonic": time.monotonic(), "stop": False}
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
    session_id = "isolated-short-smoke-20261013-r05"
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
