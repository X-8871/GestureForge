import json
import os
import subprocess
import sys
import time
from pathlib import Path


def append_record(path, value):
    with Path(path).open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, separators=(",", ":")) + "\n")
        stream.flush()


def error_record(scenario, operation, error):
    return {
        "scenario": scenario,
        "operation": operation,
        "exception_type": type(error).__name__,
        "exception_repr": repr(error),
        "errno": getattr(error, "errno", None),
        "winerror": getattr(error, "winerror", None),
        "filename": getattr(error, "filename", None),
    }


def reader(scenario, target, seconds, error_path):
    path = Path(target)
    deadline = time.monotonic() + seconds
    attempts = 0
    failures = 0
    while time.monotonic() < deadline:
        try:
            content = path.read_text(encoding="utf-8")
            if scenario == "status_replace":
                json.loads(content)
            else:
                lines = content.splitlines()
                if content and not content.endswith("\n") and lines:
                    lines = lines[:-1]
                if lines:
                    json.loads(lines[-1])
        except OSError as error:
            failures += 1
            append_record(error_path, error_record(scenario, "reader.read_text", error))
        except (TypeError, ValueError) as error:
            failures += 1
            append_record(error_path, error_record(scenario, "reader.parse", error))
        attempts += 1
        time.sleep(0.001)
    summary = {
        "scenario": scenario,
        "reader_attempts": attempts,
        "reader_failures": failures,
        "duration_seconds": seconds,
    }
    Path(error_path).with_name("reader_summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return 0


def run_scenario(base, scenario, seconds=5.0):
    directory = base / scenario
    if directory.exists():
        raise RuntimeError(f"诊断场景目录已存在，拒绝覆盖：{directory}")
    directory.mkdir()
    suffix = ".json" if scenario == "status_replace" else ".jsonl"
    target = directory / f"stress_status{suffix}"
    error_path = directory / "reader_errors.jsonl"
    writer_errors_path = directory / "writer_errors.jsonl"
    summary_path = directory / "scenario_summary.json"
    if target.exists() or error_path.exists() or writer_errors_path.exists() or summary_path.exists():
        raise RuntimeError(f"诊断产物目标已存在，拒绝覆盖：{directory}")
    if scenario == "status_replace":
        target.write_text(json.dumps({"sequence": -1, "published_monotonic": time.monotonic(), "stop": False}), encoding="utf-8")
    else:
        append_record(target, {"sequence": -1, "published_monotonic": time.monotonic(), "stop": False})
    child = subprocess.Popen(
        [sys.executable, "-u", str(Path(__file__).resolve()), "reader", scenario, str(target), str(seconds), str(error_path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "DETACHED_PROCESS", 8),
    )
    writer_failures = 0
    writer_error_records = []
    replacements = 0
    appends = 0
    deadline = time.monotonic() + seconds
    temp = target.with_suffix(target.suffix + ".tmp")
    sequence = 0
    try:
        while time.monotonic() < deadline:
            record = {"sequence": sequence, "published_monotonic": time.monotonic(), "stop": False}
            try:
                if scenario == "status_replace":
                    temp.write_text(json.dumps(record), encoding="utf-8")
                    os.replace(temp, target)
                    replacements += 1
                else:
                    append_record(target, record)
                    appends += 1
            except OSError as error:
                writer_failures += 1
                writer_error_records.append(error_record(scenario, "writer.os.replace" if scenario == "status_replace" else "writer.append", error))
                append_record(writer_errors_path, writer_error_records[-1])
            sequence += 1
            time.sleep(0.005)
    finally:
        child.wait(timeout=5.0)
    reader_summary = json.loads(directory.joinpath("reader_summary.json").read_text(encoding="utf-8"))
    summary = {
        "scenario": scenario,
        "duration_seconds": seconds,
        "writer_operation_count": replacements if scenario == "status_replace" else appends,
        "writer_failures": writer_failures,
        "writer_error_records": writer_error_records,
        "reader_exit_code": child.returncode,
        "reader_summary": reader_summary,
        "reader_error_records": [json.loads(line) for line in error_path.read_text(encoding="utf-8").splitlines()] if error_path.exists() else [],
    }
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return summary


if len(sys.argv) > 1 and sys.argv[1] == "reader":
    raise SystemExit(reader(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]))

base = Path(sys.argv[1]).resolve()
base.mkdir()
results = [
    run_scenario(base, "status_replace"),
    run_scenario(base, "status_append_only"),
]
result = {
    "run_id": "S15-T17-G1-STATUS-CONCURRENCY-20261013-r01",
    "python_executable": str(Path(sys.executable).resolve()),
    "python_version": sys.version,
    "scenarios": results,
}
(base / "concurrency_probe.result.json").write_text(
    json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
