"""回放r07真实ROSS调用并在隔离RunId运行S15监护器短回归。"""
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
RUN_ROOT = PROJECT_ROOT / "tmp" / "2B" / "S2B-T17" / "s15_ross_guard_r07_short_20261013_r01"
CAPTURE_ROOT = SCRIPT_ROOT / "real_ross_capture"
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, str(PROJECT_ROOT / "verification"))

import test_s15_ross_job_guard as regression
import s15_ross_job_guard as ross_guard


RUN_ID = RUN_ROOT.name
R06_INHERITED_CAPTURE_SHA256 = {
    "vivado_start.invocation.json": "1E19758FFF938B9F11B7401D52355C1DAE628BC4FB0EEBBB1F1B0EF8BB2BA2F4",
    "vivado_list_sessions.invocation.json": "662E47915625FB58F4C5D2AF76D187A329034D6265A18576B2BC75DABCCE9411",
    "psutil_identity_double_read.json": "007F93E70E9BFE352C216F67965AA589D2134D23BA75C0762FBD0F417234C084",
}
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


def _strict_json(path: Path) -> object:
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


def _load_simple_invocation(name: str, expected_tool: str) -> tuple[Path, dict]:
    path = CAPTURE_ROOT / f"{name}.invocation.json"
    capture = _strict_json(path)
    if type(capture) is not dict or set(capture) != {"tool", "arguments", "result"}:
        raise AssertionError(f"{path.name}必须恰含tool/arguments/result")
    if capture["tool"] != expected_tool:
        raise AssertionError(f"{path.name}实际tool字段不符")
    if type(capture["arguments"]) is not dict or type(capture["result"]) is not dict:
        raise AssertionError(f"{path.name}未保存原始arguments和CallToolResult")
    return path, capture


def _load_status_invocation(capture_id: str) -> tuple[Path, dict]:
    filenames = {
        "status_01": "vivado_status_01.invocation.json",
        "status_02": "vivado_status_02.invocation.json",
    }
    if capture_id not in filenames:
        raise AssertionError("status capture_id必须是预期的独立序号")
    path = CAPTURE_ROOT / filenames[capture_id]
    capture = _strict_json(path)
    expected_fields = {"capture_id", "tool", "tool_id", "arguments", "result"}
    if type(capture) is not dict or set(capture) != expected_fields:
        raise AssertionError(f"{path.name}必须恰含capture_id/tool/tool_id/arguments/result")
    if capture["capture_id"] != capture_id:
        raise AssertionError(f"{path.name}的capture_id序号不符")
    if capture["tool"] != "vivado_status":
        raise AssertionError(f"{path.name}的真实tool字段必须是vivado_status")
    if capture["tool_id"] != "mcp__vivado_ross__vivado_status":
        raise AssertionError(f"{path.name}的真实tool_id不符")
    if type(capture["arguments"]) is not dict or type(capture["result"]) is not dict:
        raise AssertionError(f"{path.name}未保存原始arguments和CallToolResult")
    return path, capture


def _content_text(result: dict, invocation_name: str) -> str:
    if type(result) is not dict or set(result) != {"content"}:
        raise AssertionError(f"{invocation_name} CallToolResult外层字段无效")
    blocks = result["content"]
    if type(blocks) is not list or len(blocks) != 1:
        raise AssertionError(f"{invocation_name}必须恰含一个content block")
    block = blocks[0]
    if type(block) is not dict or set(block) != {"type", "text"} or block["type"] != "text" or type(block["text"]) is not str:
        raise AssertionError(f"{invocation_name} content[0]必须是精确text block")
    return block["text"]


def _strict_json_text(text: str) -> dict:
    def reject_duplicate_keys(pairs):
        decoded = {}
        for key, value in pairs:
            if key in decoded:
                raise ValueError(f"重复JSON字段：{key}")
            decoded[key] = value
        return decoded

    def reject_nonfinite(value):
        raise ValueError(f"JSON非有限数不受支持：{value}")

    payload = json.loads(text, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_nonfinite)
    if type(payload) is not dict:
        raise AssertionError("ROSS text JSON顶层必须是对象")
    return payload


def validate_captured_real_binding() -> dict:
    start_path, start_call = _load_simple_invocation("vivado_start", "vivado_start")
    list_path, list_call = _load_simple_invocation("vivado_list_sessions", "vivado_list_sessions")
    status_first_path, status_first_call = _load_status_invocation("status_01")
    status_second_path, status_second_call = _load_status_invocation("status_02")
    identity_path = CAPTURE_ROOT / "psutil_identity_double_read.json"
    identity_document = _strict_json(identity_path)
    expected_identity_fields = {
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
    }
    if type(identity_document) is not dict or set(identity_document) != expected_identity_fields:
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
    if list_call["arguments"] != {}:
        raise AssertionError("真实vivado_list_sessions arguments必须是空对象")
    if status_first_call["arguments"] != status_second_call["arguments"]:
        raise AssertionError("两次真实vivado_status arguments必须稳定")

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
        status_first_call["arguments"],
        status_first_call["result"],
        status_second_call["arguments"],
        status_second_call["result"],
        identity_reader=captured_identity_reader,
    )
    status_first = _strict_json_text(_content_text(status_first_call["result"], "status_01"))
    status_second = _strict_json_text(_content_text(status_second_call["result"], "status_02"))
    stable_first = {key: value for key, value in status_first.items() if key != "task_progress"}
    stable_second = {key: value for key, value in status_second.items() if key != "task_progress"}
    if stable_first != stable_second:
        raise AssertionError("捕获的两次vivado_status除task_progress外不一致")
    if len(identity_reads) != 2 or identity_reads[0] is not read1 or identity_reads[1] is not read2:
        raise AssertionError("离线绑定未依次消费独立的read1/read2快照")

    capture_paths = (start_path, list_path, status_first_path, status_second_path, identity_path)
    capture_hashes = {path.relative_to(PROJECT_ROOT).as_posix(): sha256(path) for path in capture_paths}
    copied_r06_hashes = {}
    for filename, expected_hash in R06_INHERITED_CAPTURE_SHA256.items():
        path = CAPTURE_ROOT / filename
        captured_hash = sha256(path)
        if captured_hash != expected_hash:
            raise AssertionError(f"r07继承文件与r06冻结SHA256不一致：{filename}")
        copied_r06_hashes[filename] = captured_hash
    calls = {
        "vivado_start": (start_path, start_call),
        "vivado_list_sessions": (list_path, list_call),
        "vivado_status_first": (status_first_path, status_first_call),
        "vivado_status_second": (status_second_path, status_second_call),
    }
    replay_details = {}
    for name, (path, capture) in calls.items():
        response_text = _content_text(capture["result"], name)
        input_bytes = json.dumps(
            capture["arguments"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        details = {
            "capture_file": path.relative_to(PROJECT_ROOT).as_posix(),
            "capture_file_sha256": capture_hashes[path.relative_to(PROJECT_ROOT).as_posix()],
            "capture_id": capture.get("capture_id"),
            "tool": capture["tool"],
            "tool_id": capture.get("tool_id"),
            "arguments": capture["arguments"],
            "arguments_canonical_sha256": hashlib.sha256(input_bytes).hexdigest().upper(),
            "response_content_text_sha256": hashlib.sha256(response_text.encode("utf-8")).hexdigest().upper(),
        }
        replay_details[name] = details

    result = {
        "status": "PASS",
        "binding_mode": "offline replay of r07 captured CallToolResult envelopes and independent psutil snapshots",
        "replayed_invocations": replay_details,
        "raw_capture_file_sha256": capture_hashes,
        "r06_inherited_capture_sha256_verified": copied_r06_hashes,
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
            "status_summary": status_first["status_summary"],
            "is_command_running": status_first["is_command_running"],
            "queue_length": status_first["queue_length"],
            "process_running": status_first["process_running"],
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
    started = time.monotonic()
    try:
        result["real_capture_binding"] = validate_captured_real_binding()
        result["result"] = regression.run_short(RUN_ROOT)
        result["checks_count"] = len(result["result"]["checks"])
        result["status"] = "PASS"
        result["exit_code"] = 0
    except BaseException:
        result["status"] = "FAIL"
        result["traceback"] = traceback.format_exc()
    result["elapsed_seconds"] = time.monotonic() - started
    result["finished_local"] = datetime.now().astimezone().isoformat()
    (RUN_ROOT / "short_result.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                key: result[key]
                for key in ("run_id", "mode", "status", "exit_code", "checks_count", "elapsed_seconds")
                if key in result
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
