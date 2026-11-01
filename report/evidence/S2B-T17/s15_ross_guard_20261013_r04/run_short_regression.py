"""在当前RunId执行S15 ROSS监护器短回归并写入独立结果摘要。"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import psutil


SCRIPT_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_ROOT.parents[3]
RUN_ROOT = PROJECT_ROOT / "tmp" / "2B" / "S2B-T17" / "s15_ross_guard_r06_short_20261013_r01"
CAPTURE_ROOT = PROJECT_ROOT / "report" / "evidence" / "S2B-T17" / "s15_ross_guard_20261013_r06" / "real_ross_capture"
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, str(PROJECT_ROOT / "verification"))

import test_s15_ross_job_guard as regression
import s15_ross_job_guard as ross_guard


RUN_ID = RUN_ROOT.name
if RUN_ROOT.exists():
    raise FileExistsError(f"隔离短回归目标必须事先不存在：{RUN_ROOT}")
RUN_ROOT.mkdir(parents=True, exist_ok=False)
ross_guard.EXPECTED_EVIDENCE_RELATIVE = RUN_ROOT.relative_to(PROJECT_ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _strict_json_file(path: Path) -> object:
    def reject_duplicate_keys(pairs):
        decoded = {}
        for key, value in pairs:
            if key in decoded:
                raise ValueError(f"重复JSON字段：{key}")
            decoded[key] = value
        return decoded

    def reject_nonfinite(value):
        raise ValueError(f"JSON非有限数不受支持：{value}")

    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite,
    )


def validate_captured_real_binding() -> dict:
    invocation_specs = {
        "vivado_start": ("vivado_start.invocation.json", "vivado_start"),
        "vivado_list_sessions": ("vivado_list_sessions.invocation.json", "vivado_list_sessions"),
        "vivado_status_first": ("vivado_status_01.invocation.json", "vivado_status_01"),
        "vivado_status_second": ("vivado_status_02.invocation.json", "vivado_status_02"),
    }
    invocation_paths = {
        name: CAPTURE_ROOT / filename for name, (filename, _) in invocation_specs.items()
    }
    invocations = {}
    for name, (filename, expected_tool) in invocation_specs.items():
        path = invocation_paths[name]
        capture = _strict_json_file(path)
        if type(capture) is not dict or set(capture) != {"tool", "arguments", "result"}:
            raise AssertionError(f"{filename}必须恰含tool/arguments/result")
        if capture["tool"] != expected_tool:
            raise AssertionError(f"{filename}的工具标记与捕获项不符")
        if type(capture["arguments"]) is not dict or type(capture["result"]) is not dict:
            raise AssertionError(f"{filename}必须保存原始arguments对象与CallToolResult对象")
        invocations[name] = capture

    identity_path = CAPTURE_ROOT / "psutil_identity_double_read.json"
    identity_document = _strict_json_file(identity_path)
    if set(identity_document) != {
        "exit_code",
        "identities_equal",
        "python_executable",
        "python_version",
        "psutil_version",
        "pid",
        "read1_utc",
        "read2_utc",
        "read1",
        "read2",
    }:
        raise AssertionError("psutil双读capture字段集合不符")
    if identity_document["exit_code"] != 0 or identity_document["identities_equal"] is not True:
        raise AssertionError("psutil双读capture未确认成功且一致")
    if identity_document["pid"] != ross_guard.EXPECTED_REAL_PROCESS_ID:
        raise AssertionError("psutil双读capture PID与预期不符")
    if type(identity_document["read1_utc"]) is not str or type(identity_document["read2_utc"]) is not str:
        raise AssertionError("psutil双读capture时间字段无效")
    read1 = identity_document["read1"]
    read2 = identity_document["read2"]
    if type(read1) is not dict or type(read2) is not dict or read1 is read2 or read1 != read2:
        raise AssertionError("psutil双读必须是分离存储且六字段值相同的两个快照")
    start_call = invocations["vivado_start"]
    list_call = invocations["vivado_list_sessions"]
    status_call_first = invocations["vivado_status_first"]
    status_call_second = invocations["vivado_status_second"]
    status_first = status_call_first["result"]
    status_second = status_call_second["result"]
    if list_call["arguments"] != {}:
        raise AssertionError("真实vivado_list_sessions arguments必须是空对象")
    if status_call_first["arguments"] != status_call_second["arguments"]:
        raise AssertionError("两次真实vivado_status arguments必须稳定")
    decoded = {
        "status_first": json.loads(status_first["content"][0]["text"]),
        "status_second": json.loads(status_second["content"][0]["text"]),
    }
    identity_reads = []

    def captured_identity_reader(pid: int) -> dict:
        if pid != identity_document["pid"]:
            raise AssertionError("离线绑定读取器收到的PID与捕获身份不同")
        if len(identity_reads) == 0:
            snapshot = read1
        elif len(identity_reads) == 1:
            snapshot = read2
        else:
            raise AssertionError("离线绑定读取次数超过捕获的双读")
        identity_reads.append(snapshot)
        return snapshot

    canonical = ross_guard.StrictCanonicalAdapter().decode_vivado_idle_observation(
        start_call["arguments"],
        start_call["result"],
        list_call["arguments"],
        list_call["result"],
        status_call_first["arguments"],
        status_first,
        status_call_second["arguments"],
        status_second,
        identity_reader=captured_identity_reader,
    )
    stable_first = {key: value for key, value in decoded["status_first"].items() if key != "task_progress"}
    stable_second = {key: value for key, value in decoded["status_second"].items() if key != "task_progress"}
    if stable_first != stable_second:
        raise AssertionError("捕获的两次vivado_status除task_progress外不一致")
    if len(identity_reads) != 2 or identity_reads[0] is not read1 or identity_reads[1] is not read2:
        raise AssertionError("离线绑定未依次消费独立的read1/read2快照")
    capture_hashes = {
        path.relative_to(PROJECT_ROOT).as_posix(): sha256(path)
        for path in (*invocation_paths.values(), identity_path)
    }
    replay_details = {}
    for name, capture in invocations.items():
        response_text = capture["result"]["content"][0]["text"]
        input_bytes = json.dumps(
            capture["arguments"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        replay_details[name] = {
            "capture_file": invocation_paths[name].relative_to(PROJECT_ROOT).as_posix(),
            "capture_file_sha256": capture_hashes[invocation_paths[name].relative_to(PROJECT_ROOT).as_posix()],
            "tool_marker": capture["tool"],
            "arguments": capture["arguments"],
            "arguments_canonical_sha256": hashlib.sha256(input_bytes).hexdigest().upper(),
            "response_content_text_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest().upper(),
        }
    result = {
        "status": "PASS",
        "binding_mode": "offline replay of captured CallToolResult envelopes and independent psutil snapshots",
        "replayed_invocations": replay_details,
        "raw_capture_file_sha256": capture_hashes,
        "identity_capture_file": identity_path.relative_to(PROJECT_ROOT).as_posix(),
        "identity_snapshot_consumption": {
            "order": ["read1", "read2"],
            "separate_snapshot_objects": identity_reads[0] is not identity_reads[1],
            "read_count": len(identity_reads),
            "pid_arguments": [identity_document["pid"], identity_document["pid"]],
        },
        "status_comparison": {
            "ignored_dynamic_field": "task_progress",
            "stable_fields_equal": True,
            "status_summary": decoded["status_first"]["status_summary"],
            "is_command_running": decoded["status_first"]["is_command_running"],
            "queue_length": decoded["status_first"]["queue_length"],
            "process_running": decoded["status_first"]["process_running"],
        },
        "identity_capture_metadata": {
            key: identity_document[key]
            for key in (
                "exit_code",
                "identities_equal",
                "python_executable",
                "python_version",
                "psutil_version",
                "pid",
                "read1_utc",
                "read2_utc",
            )
        },
        "canonical_observation": canonical,
    }
    (RUN_ROOT / "real_binding_result.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    source_paths = (
        PROJECT_ROOT / "verification" / "s15_ross_job_guard.py",
        PROJECT_ROOT / "verification" / "test_s15_ross_job_guard.py",
        Path(__file__).resolve(),
    )
    result = {
        "run_id": RUN_ID,
        "mode": "short",
        "started_local": datetime.now().astimezone().isoformat(),
        "python_executable": str(Path(sys.executable).resolve()),
        "python_version": sys.version,
        "psutil_version": psutil.__version__,
        "head": subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        "source_sha256": {path.name: sha256(path) for path in source_paths},
        "command": [str(Path(sys.executable).resolve()), "-B", str(Path(__file__).resolve())],
        "exit_code": 1,
    }
    start = time.monotonic()
    try:
        result["real_capture_binding"] = validate_captured_real_binding()
        result["result"] = regression.run_short(RUN_ROOT)
        result["checks_count"] = len(result["result"]["checks"])
        result["status"] = "PASS"
        result["exit_code"] = 0
    except BaseException:
        result["status"] = "FAIL"
        result["traceback"] = traceback.format_exc()
    result["elapsed_seconds"] = time.monotonic() - start
    result["finished_local"] = datetime.now().astimezone().isoformat()
    (RUN_ROOT / "short_result.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({key: result[key] for key in ("run_id", "mode", "status", "exit_code", "checks_count", "elapsed_seconds") if key in result}, ensure_ascii=False, sort_keys=True))
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
