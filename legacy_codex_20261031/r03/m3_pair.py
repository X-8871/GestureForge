#!/usr/bin/env python3
"""阶段四 M3 候选 DDR 区域只读成对取样工具。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable


DDR_START = 0x12000000
DDR_END = 0x12C08000
DDR_BYTES = DDR_END - DDR_START
DDR_WORDS = DDR_BYTES // 4
BASELINE_SHA256 = "41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf"
UTC8 = timezone(timedelta(hours=8))
HEX64_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
ERROR_RE = re.compile(r"\b(error|failed|failure)\b", re.IGNORECASE)
MANIFEST_NAME = "capture_manifest.json"
MANIFEST_HASH_NAME = "capture_manifest.sha256"
PAIR_MANIFEST_NAME = "pair_report.json"
PAIR_HASH_NAME = "pair_report.sha256"
READ_A_NAME = "read_a.bin"
READ_B_NAME = "read_b.bin"
OFFICIAL_XSDB = Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat")


class ToolError(Exception):
    """输入、环境或取样校验错误。"""


def now_utc8() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def hash_item(path: Path) -> dict[str, Any]:
    digest, size = sha256_file(path)
    return {"path": path.name, "bytes": size, "sha256": digest, "hash_basis": "worktree_disk"}


def write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8", newline="\n")


def write_manifest_with_checksum(path: Path, value: Any, checksum_path: Path) -> str:
    write_json(path, value)
    digest, size = sha256_file(path)
    checksum_path.write_text(
        f"sha256={digest}\nhash_basis=worktree_disk\nbytes={size}\n",
        encoding="utf-8",
        newline="\n",
    )
    return digest


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ToolError(f"无法读取 JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ToolError(f"JSON 顶层必须是对象: {path}")
    return value


def validate_new_output(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    parent = path.parent.resolve(strict=True)
    path = parent / path.name
    if path.exists():
        raise ToolError(f"输出目录必须不存在，拒绝覆盖: {path}")
    if not path.name or path.name in {".", ".."}:
        raise ToolError("输出目录名无效")
    return path


def validate_id(value: str, name: str) -> str:
    if not SAFE_ID_RE.fullmatch(value):
        raise ToolError(f"{name} 只允许 1–128 位字母、数字、下划线、点、冒号或连字符")
    return value


def load_context(path: Path, window_id: str, event_id: str) -> tuple[dict[str, Any], str, int]:
    if not path.is_file():
        raise ToolError(f"context 文件不存在或不是普通文件: {path}")
    context = read_json(path)
    required = (
        "window_id",
        "event_id",
        "lifecycle_id",
        "target",
        "filter",
        "bit_sha256",
        "init_elf_sha256",
        "app_elf_sha256",
        "cpu0_state",
        "cpu1_state",
        "masters_quiesced",
        "cache_basis",
    )
    missing = [key for key in required if key not in context]
    if missing:
        raise ToolError(f"context 缺少必填字段: {', '.join(missing)}")
    if context["window_id"] != window_id or context["event_id"] != event_id:
        raise ToolError("context 的 window_id/event_id 必须与命令行相同")
    validate_id(str(context["window_id"]), "window_id")
    validate_id(str(context["event_id"]), "event_id")
    validate_id(str(context["lifecycle_id"]), "lifecycle_id")
    for field in ("target", "filter", "cache_basis"):
        if not isinstance(context[field], str) or not context[field].strip():
            raise ToolError(f"context.{field} 必须是非空字符串")
    for field in ("bit_sha256", "init_elf_sha256", "app_elf_sha256"):
        if not isinstance(context[field], str) or not HEX64_RE.fullmatch(context[field]):
            raise ToolError(f"context.{field} 必须是 64 位 SHA-256 十六进制字符串")
        context[field] = context[field].lower()
    for field in ("cpu0_state", "cpu1_state"):
        if not isinstance(context[field], str) or context[field].strip().lower() not in {"stopped", "suspended"}:
            raise ToolError(f"context.{field} 必须记录 Stopped 或 Suspended")
    if context["masters_quiesced"] is not True:
        raise ToolError("context.masters_quiesced 必须严格为 true")
    context["cpu0_state"] = context["cpu0_state"].strip()
    context["cpu1_state"] = context["cpu1_state"].strip()
    digest, size = sha256_file(path)
    return context, digest, size


def tcl_quote(value: str) -> str:
    """将数据作为 Tcl 双引号字符串引用，拒绝换行以防止注入命令。"""
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ToolError("Tcl 参数包含不允许的换行或 NUL 字符")
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    escaped = escaped.replace("[", "\\[").replace("]", "\\]")
    return f'"{escaped}"'


def build_tcl(out_dir: Path, port: int, marker_prefix: str) -> str:
    file_a = tcl_quote(str(out_dir / READ_A_NAME))
    file_b = tcl_quote(str(out_dir / READ_B_NAME))
    return f'''# 本文件只连接、选择 Cortex-A9 #0、核验两核已停止并读取固定 DDR 区域。
proc m3_get_core_state {{filter core_label expected_name_pattern}} {{
    set matches [targets -target-properties -filter $filter]
    if {{[llength $matches] != 1}} {{error "M3_${{core_label}}_TARGET_COUNT_MISMATCH"}}
    set props [lindex $matches 0]
    set name [dict get $props name]
    if {{![string match $expected_name_pattern $name]}} {{error "M3_${{core_label}}_TARGET_NAME_MISMATCH"}}
    targets -set -filter $filter
    set core_state [string trim [state]]
    if {{$core_state eq ""}} {{error "M3_${{core_label}}_STATE_EMPTY"}}
    if {{![regexp -nocase {{^(stopped|suspended)(:|[[:space:]]|$)}} $core_state]}} {{error "M3_${{core_label}}_NOT_STOPPED_OR_SUSPENDED: $core_state"}}
    puts "{marker_prefix}_${{core_label}}_STATE=$core_state"
    puts "{marker_prefix}_${{core_label}}_STATE_OK"
    return $core_state
}}
proc m3_read_pair {{}} {{
puts "{marker_prefix}_BEGIN"
connect -url tcp:127.0.0.1:{port}
set cpu0_state [m3_get_core_state {{name =~ "*Cortex-A9*#0"}} CPU0 {{*Cortex-A9*#0}}]
set cpu1_state [m3_get_core_state {{name =~ "*Cortex-A9*#1"}} CPU1 {{*Cortex-A9*#1}}]
targets -set -filter {{name =~ "*Cortex-A9*#0"}}
set active_matches [targets -target-properties -filter {{name =~ "*Cortex-A9*#0"}}]
if {{[llength $active_matches] != 1}} {{error "M3_ACTIVE_TARGET_COUNT_MISMATCH"}}
puts "{marker_prefix}_TARGET_STATE_OK"
puts "{marker_prefix}_READ_A_BEGIN"
mrd -bin -file {file_a} 0x{DDR_START:08X} {DDR_WORDS}
puts "{marker_prefix}_READ_A_OK"
puts "{marker_prefix}_READ_B_BEGIN"
mrd -bin -file {file_b} 0x{DDR_START:08X} {DDR_WORDS}
puts "{marker_prefix}_READ_B_OK"
puts "{marker_prefix}_END"
}}
set m3_rc [catch {{m3_read_pair}} m3_error]
set m3_disconnect_rc [catch {{disconnect}} m3_disconnect_error]
if {{$m3_rc != 0}} {{
    puts stderr "ERROR: $m3_error"
    exit 2
}}
if {{$m3_disconnect_rc != 0}} {{
    puts stderr "ERROR: disconnect failed: $m3_disconnect_error"
    exit 2
}}
exit 0
'''


def expected_marker_lines(prefix: str) -> tuple[str, ...]:
    return tuple(
        f"{prefix}_{suffix}"
        for suffix in (
            "BEGIN",
            "CPU0_STATE_OK",
            "CPU1_STATE_OK",
        "TARGET_STATE_OK",
            "READ_A_BEGIN",
            "READ_A_OK",
            "READ_B_BEGIN",
            "READ_B_OK",
            "END",
        )
    )


def check_markers(stdout: bytes, stderr: bytes, prefix: str) -> tuple[str, str]:
    out_text = stdout.decode("utf-8", errors="replace")
    err_text = stderr.decode("utf-8", errors="replace")
    combined = out_text + "\n" + err_text
    lines = {line.strip() for line in combined.splitlines()}
    missing = [marker for marker in expected_marker_lines(prefix) if marker not in lines]
    if missing:
        raise ToolError(f"XSDB 缺少成功标记: {', '.join(missing)}")
    if ERROR_RE.search(combined):
        raise ToolError("XSDB stdout/stderr 含 error/failed/failure 文本")
    return out_text, err_text


def windows_launch_plan(argv: list[str], *, test_only_allow_mock: bool = False) -> dict[str, Any]:
    """将固定只读Tcl通过厂商bat与cmd -eval入口执行，拒绝裸exe及命令展开字符。"""
    if len(argv) != 3 or argv[1] != "-no-ini":
        raise ToolError("XSDB逻辑参数必须为厂商bat、-no-ini和固定Tcl路径")
    batch, script = Path(argv[0]), Path(argv[2])
    if batch.suffix.lower() != ".bat":
        raise ToolError("禁止裸xsdb.exe；必须使用已核验的厂商xsdb.bat")
    official = batch.resolve(strict=True) == OFFICIAL_XSDB.resolve(strict=True)
    if not official and not test_only_allow_mock:
        raise ToolError("真实取样必须使用固定官方xsdb.bat；禁止替换任意批处理")
    cmd = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/cmd.exe"
    for path in (batch, script, cmd):
        if any(character in str(path) for character in '"%!^&|<>{}\r\n'):
            raise ToolError("启动路径含cmd或Tcl不安全字符")
        if not path.is_file():
            raise ToolError(f"启动文件不存在或不是普通文件：{path}")
    expression = "source {" + script.as_posix() + "}"
    payload = f'""{batch}" -no-ini -eval "{expression}""'
    command_line = subprocess.list2cmdline([str(cmd), "/d", "/q", "/v:off", "/s", "/c"]) + " " + payload
    return {"application": str(cmd), "command_line": command_line,
            "logical_argv": argv, "tcl_expression": expression,
            "official_entry_verified": official,
            "batch_sha256": sha256_file(batch)[0]}


def _run_xsdb(argv: list[str], timeout: int, *, test_only_allow_mock: bool = False) -> subprocess.CompletedProcess[bytes]:
    """复用已独立审查的Windows Job收尾，超时也只清理本次子进程树。"""
    plan = windows_launch_plan(argv, test_only_allow_mock=test_only_allow_mock)
    launcher_path = Path(__file__).with_name("job_launcher.py").resolve(strict=True)
    spec = importlib.util.spec_from_file_location("m3_fixed_job_launcher", launcher_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cwd = Path(argv[2]).parent
    output = cwd / "launcher"
    record = module.run_job(plan["application"], plan["command_line"], cwd,
                            module.offline_environment(cwd), output, timeout)
    write_json(output / "launch_plan.json", plan)
    record["scope"] = "真实M3只读取样；独立校验M3标记，不使用离线patchlevel判据"
    record["official_entry_verified"] = plan["official_entry_verified"]
    record["test_fixture_only"] = not plan["official_entry_verified"]
    record["batch_sha256"] = plan["batch_sha256"]
    record["status"] = "PASS_PROCESS_ONLY" if (record.get("root_exit_code") == 0
        and record.get("cleanup_confirmed") and not record.get("errors") and not record.get("timed_out")) else "FAIL_PROCESS"
    write_json(output / "execution.json", record)
    stdout, stderr = (output / "stdout.bin").read_bytes(), (output / "stderr.bin").read_bytes()
    if record.get("timed_out"):
        raise subprocess.TimeoutExpired(argv, timeout, output=stdout, stderr=stderr)
    if record["status"] != "PASS_PROCESS_ONLY":
        stderr += ("\nERROR: " + json.dumps(record, ensure_ascii=False)).encode("utf-8")
    result = subprocess.CompletedProcess(argv, 0 if record["status"] == "PASS_PROCESS_ONLY" else 2, stdout, stderr)
    result.launcher_record = record
    return result


def capture(
    *,
    out_text: str,
    xsdb_text: str,
    port: int,
    window_id: str,
    phase: str,
    event_id: str,
    authorization_file_text: str,
    context_file_text: str,
    timeout_seconds: int = 120,
    runner: Callable[[list[str], int], subprocess.CompletedProcess[bytes]] = _run_xsdb,
) -> dict[str, Any]:
    if phase not in {"before", "after"}:
        raise ToolError("phase 只能是 before 或 after")
    if not 1 <= port <= 65535:
        raise ToolError("port 必须在 1–65535 范围")
    if not 1 <= timeout_seconds <= 600:
        raise ToolError("timeout_seconds 必须在 1–600 范围")
    validate_id(window_id, "window_id")
    validate_id(event_id, "event_id")
    out_dir = validate_new_output(out_text)
    xsdb = Path(xsdb_text).expanduser().resolve(strict=True)
    if not xsdb.is_file() or xsdb.suffix.lower() not in {".exe", ".bat"}:
        raise ToolError("--xsdb 必须指向已存在的精确 .exe 或 .bat 文件")
    if runner is _run_xsdb and xsdb != OFFICIAL_XSDB.resolve(strict=True):
        raise ToolError("真实capture仅允许固定官方xsdb.bat")
    context_path = Path(context_file_text).expanduser().resolve(strict=True)
    auth_path = Path(authorization_file_text).expanduser().resolve(strict=True)
    if not auth_path.is_file():
        raise ToolError("--authorization-file 必须指向已存在的普通文件")
    context, context_digest, context_size = load_context(context_path, window_id, event_id)
    auth_digest, auth_size = sha256_file(auth_path)

    out_dir.mkdir()
    (out_dir / "context.json").write_bytes(context_path.read_bytes())
    (out_dir / "authorization.md").write_bytes(auth_path.read_bytes())
    token = uuid.uuid4().hex
    prefix = f"M3PAIR_{token}"
    tcl_path = out_dir / "capture_readonly.tcl"
    tcl_text = build_tcl(out_dir, port, prefix)
    tcl_path.write_text(tcl_text, encoding="utf-8", newline="\n")
    stdout_path = out_dir / "xsdb.stdout.log"
    stderr_path = out_dir / "xsdb.stderr.log"
    # 禁用用户 XSDB 初始化脚本，并把 Tcl 文件作为位置参数传入。
    argv = [str(xsdb), "-no-ini", str(tcl_path)]
    start = now_utc8()
    monotonic_start = time.monotonic()
    result: subprocess.CompletedProcess[bytes]
    try:
        result = runner(argv, timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        stdout_raw = exc.stdout or b""
        stderr_raw = exc.stderr or b""
        if isinstance(stdout_raw, str):
            stdout_raw = stdout_raw.encode("utf-8", errors="replace")
        if isinstance(stderr_raw, str):
            stderr_raw = stderr_raw.encode("utf-8", errors="replace")
        stdout_path.write_bytes(stdout_raw)
        stderr_path.write_bytes(stderr_raw)
        raise ToolError(f"XSDB 整体运行超过 {timeout_seconds} 秒，保留部分日志与 Tcl，未判定为成功") from exc
    stdout_raw = result.stdout or b""
    stderr_raw = result.stderr or b""
    if isinstance(stdout_raw, str):
        stdout_raw = stdout_raw.encode("utf-8", errors="replace")
    if isinstance(stderr_raw, str):
        stderr_raw = stderr_raw.encode("utf-8", errors="replace")
    stdout_path.write_bytes(stdout_raw)
    stderr_path.write_bytes(stderr_raw)
    duration_seconds = round(time.monotonic() - monotonic_start, 3)
    if result.returncode != 0:
        raise ToolError(f"XSDB 退出码为 {result.returncode}")
    out_decoded, err_decoded = check_markers(stdout_raw, stderr_raw, prefix)

    read_a = out_dir / READ_A_NAME
    read_b = out_dir / READ_B_NAME
    for dump in (read_a, read_b):
        if not dump.is_file():
            raise ToolError(f"XSDB 未生成读取文件: {dump.name}")
        if dump.stat().st_size != DDR_BYTES:
            raise ToolError(f"{dump.name} 长度错误: {dump.stat().st_size}，应为 {DDR_BYTES}")
    digest_a, size_a = sha256_file(read_a)
    digest_b, size_b = sha256_file(read_b)
    if digest_a != digest_b:
        raise ToolError("同一次采样的 A/B 双读 SHA-256 不一致")
    end = now_utc8()
    launcher_record = getattr(result, "launcher_record", None)
    other_files = [hash_item(tcl_path), hash_item(stdout_path), hash_item(stderr_path),
                   hash_item(out_dir / "context.json"), hash_item(out_dir / "authorization.md")]
    if launcher_record is not None:
        (out_dir / "launcher/xsdb_entry.bat").write_bytes(xsdb.read_bytes())
        for rel in ("launcher/launch_plan.json", "launcher/execution.json", "launcher/stdout.bin", "launcher/stderr.bin", "launcher/xsdb_entry.bat"):
            entry = hash_item(out_dir / rel)
            entry["path"] = rel
            other_files.append(entry)
    manifest = {
        "schema": "gestureforge.m3_pair.capture.v2",
        "status": "CAPTURED",
        "hash_basis": "worktree_disk",
        "created_at_utc8": start,
        "captured_at_utc8": end,
        "duration_seconds": duration_seconds,
        "phase": phase,
        "window_id": window_id,
        "event_id": event_id,
        "lifecycle_id": context["lifecycle_id"],
        "address_start_inclusive": f"0x{DDR_START:08X}",
        "address_end_exclusive": f"0x{DDR_END:08X}",
        "bytes_required": DDR_BYTES,
        "words_required": DDR_WORDS,
        "context": context,
        "context_file": {"path": str(context_path), "bytes": context_size, "sha256": context_digest, "hash_basis": "worktree_disk"},
        "authorization_file": {
            "path": str(auth_path),
            "bytes": auth_size,
            "sha256": auth_digest,
            "hash_basis": "worktree_disk",
            "meaning": "仅记录输入文件身份摘要；本工具不验证其批准权限或有效性。",
        },
        "xsdb": {"path": str(xsdb), "argv": argv, "shell": False, "timeout_seconds": timeout_seconds, "returncode": result.returncode,
                 "launcher_record": launcher_record,
                 "argv_meaning": "逻辑参数；真实Windows调用由launcher/launch_plan.json记录cmd /c厂商bat -eval source入口"},
        "markers": list(expected_marker_lines(prefix)),
        "readouts": [
            {"path": READ_A_NAME, "bytes": size_a, "sha256": digest_a, "hash_basis": "worktree_disk"},
            {"path": READ_B_NAME, "bytes": size_b, "sha256": digest_b, "hash_basis": "worktree_disk"},
        ],
        "other_files": other_files,
        "stdout_utf8_replacement_decoded": out_decoded,
        "stderr_utf8_replacement_decoded": err_decoded,
        "interpretation": "CAPTURED 表示本机脚本/日志/文件校验通过，不代表 M3、硬件状态或阶段验收通过。",
    }
    manifest_path = out_dir / MANIFEST_NAME
    manifest_hash = write_manifest_with_checksum(manifest_path, manifest, out_dir / MANIFEST_HASH_NAME)
    return {"status": "CAPTURED", "directory": str(out_dir), "manifest_sha256": manifest_hash, "read_sha256": digest_a}


def verify_manifest_checksum(directory: Path, name: str, checksum_name: str) -> dict[str, Any]:
    manifest_path = directory / name
    checksum_path = directory / checksum_name
    if manifest_path.is_symlink() or checksum_path.is_symlink():
        raise ToolError(f"清单文件不能是符号链接: {directory}")
    if not manifest_path.is_file() or not checksum_path.is_file():
        raise ToolError(f"缺少清单或清单校验文件: {directory}")
    digest, size = sha256_file(manifest_path)
    checksum_text = checksum_path.read_text(encoding="utf-8")
    fields = dict(
        line.split("=", 1) for line in checksum_text.splitlines() if "=" in line
    )
    if fields.get("sha256") != digest or fields.get("hash_basis") != "worktree_disk" or fields.get("bytes") != str(size):
        raise ToolError(f"清单校验值不匹配或基座错误: {directory}")
    return read_json(manifest_path)


def verify_capture(directory: Path, expected_phase: str) -> tuple[dict[str, Any], bytes, str]:
    manifest = verify_manifest_checksum(directory, MANIFEST_NAME, MANIFEST_HASH_NAME)
    if manifest.get("schema") not in {"gestureforge.m3_pair.capture.v1", "gestureforge.m3_pair.capture.v2"} or manifest.get("status") != "CAPTURED":
        raise ToolError(f"capture manifest schema/status 无效: {directory}")
    if manifest.get("hash_basis") != "worktree_disk" or manifest.get("phase") != expected_phase:
        raise ToolError(f"capture phase 或 hash_basis 错误: {directory}")
    if manifest.get("address_start_inclusive") != f"0x{DDR_START:08X}" or manifest.get("address_end_exclusive") != f"0x{DDR_END:08X}":
        raise ToolError(f"capture 地址范围不匹配: {directory}")
    if manifest.get("bytes_required") != DDR_BYTES or manifest.get("words_required") != DDR_WORDS:
        raise ToolError(f"capture 长度元数据错误: {directory}")
    xsdb = manifest.get("xsdb")
    if (
        not isinstance(xsdb, dict)
        or xsdb.get("returncode") != 0
        or xsdb.get("shell") is not False
        or not isinstance(xsdb.get("timeout_seconds"), int)
        or not 1 <= xsdb["timeout_seconds"] <= 600
        or not isinstance(xsdb.get("argv"), list)
        or len(xsdb["argv"]) != 3
        or xsdb["argv"][0] != xsdb.get("path")
        or xsdb["argv"][1] != "-no-ini"
        or not isinstance(xsdb["argv"][2], str)
        or Path(xsdb["argv"][2]).name != "capture_readonly.tcl"
    ):
        raise ToolError(f"capture XSDB 执行元数据无效: {directory}")
    markers = manifest.get("markers")
    if not isinstance(markers, list) or len(markers) != len(expected_marker_lines("x")):
        raise ToolError(f"capture marker 列表无效: {directory}")
    suffixes = ("BEGIN", "CPU0_STATE_OK", "CPU1_STATE_OK", "TARGET_STATE_OK", "READ_A_BEGIN", "READ_A_OK", "READ_B_BEGIN", "READ_B_OK", "END")
    if not all(isinstance(marker, str) for marker in markers):
        raise ToolError(f"capture marker 格式无效: {directory}")
    prefix = markers[0].rsplit("_", 1)[0]
    if tuple(markers) != tuple(f"{prefix}_{suffix}" for suffix in suffixes):
        raise ToolError(f"capture marker 缺失、乱序或前缀不一致: {directory}")
    readouts = manifest.get("readouts")
    if not isinstance(readouts, list) or len(readouts) != 2:
        raise ToolError(f"capture readouts 清单无效: {directory}")
    expected_names = (READ_A_NAME, READ_B_NAME)
    actual_hashes: list[str] = []
    for item, expected_name in zip(readouts, expected_names, strict=True):
        if not isinstance(item, dict) or item.get("path") != expected_name or item.get("hash_basis") != "worktree_disk":
            raise ToolError(f"capture readout 条目无效: {directory}")
        path = directory / expected_name
        if path.is_symlink() or not path.is_file():
            raise ToolError(f"capture readout 文件缺失: {path}")
        digest, size = sha256_file(path)
        if size != DDR_BYTES or item.get("bytes") != size or item.get("sha256") != digest:
            raise ToolError(f"capture readout 长度或 SHA-256 不一致: {path}")
        actual_hashes.append(digest)
    if actual_hashes[0] != actual_hashes[1]:
        raise ToolError(f"capture 内部双读不一致: {directory}")
    other_files = manifest.get("other_files", [])
    if not isinstance(other_files, list):
        raise ToolError(f"capture other_files 清单无效: {directory}")
    allowed_other_names = {"capture_readonly.tcl", "xsdb.stdout.log", "xsdb.stderr.log"}
    if manifest["schema"].endswith(".v2"):
        allowed_other_names.update({"launcher/launch_plan.json", "launcher/execution.json", "launcher/stdout.bin", "launcher/stderr.bin", "launcher/xsdb_entry.bat", "context.json", "authorization.md"})
    if {item.get("path") for item in other_files if isinstance(item, dict)} != allowed_other_names:
        raise ToolError(f"capture 附属文件清单不完整或含未知路径: {directory}")
    logged: dict[str, str] = {}
    for item in other_files:
        if not isinstance(item, dict) or item.get("path") not in allowed_other_names or item.get("hash_basis") != "worktree_disk":
            raise ToolError(f"capture 其他文件 hash_basis 无效: {directory}")
        path = directory / str(item["path"])
        if path.is_symlink() or not path.is_file():
            raise ToolError(f"capture 附属文件缺失: {path}")
        digest, size = sha256_file(path)
        if digest != item.get("sha256") or size != item.get("bytes"):
            raise ToolError(f"capture 附属文件 SHA-256 或长度不一致: {path}")
        if item.get("path") in {"xsdb.stdout.log", "xsdb.stderr.log"}:
            logged[str(item["path"])] = path.read_text(encoding="utf-8", errors="replace")
    if set(logged) != {"xsdb.stdout.log", "xsdb.stderr.log"}:
        raise ToolError(f"capture 缺少 stdout/stderr 日志: {directory}")
    combined_log = logged["xsdb.stdout.log"] + "\n" + logged["xsdb.stderr.log"]
    log_lines = {line.strip() for line in combined_log.splitlines()}
    if any(marker not in log_lines for marker in markers) or ERROR_RE.search(combined_log):
        raise ToolError(f"capture 日志 marker/error 校验失败: {directory}")
    if manifest["schema"].endswith(".v2"):
        plan = read_json(directory / "launcher/launch_plan.json")
        record = read_json(directory / "launcher/execution.json")
        if record.get("test_fixture_only") is not False:
            raise ToolError("v2真实采样拒绝纯测试夹具或未声明来源的记录")
        if record != xsdb.get("launcher_record"):
            raise ToolError("真实Job记录与capture内联记录不一致")
        expected_cmd = str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/cmd.exe")
        expected_expression = "source {" + Path(xsdb["argv"][2]).as_posix() + "}"
        expected_payload = f'""{xsdb["path"]}" -no-ini -eval "{expected_expression}""'
        expected_line = subprocess.list2cmdline([expected_cmd, "/d", "/q", "/v:off", "/s", "/c"]) + " " + expected_payload
        if (Path(xsdb["path"]) != OFFICIAL_XSDB or plan.get("logical_argv") != xsdb["argv"]
                or plan.get("official_entry_verified") is not True or record.get("official_entry_verified") is not True
                or plan.get("application") != expected_cmd or record.get("application") != expected_cmd
                or plan.get("tcl_expression") != expected_expression or plan.get("command_line") != expected_line
                or record.get("command_line") != expected_line or not HEX64_RE.fullmatch(str(plan.get("batch_sha256", "")))):
            raise ToolError("真实官方cmd/bat/-eval入口绑定错误")
        if (sha256_file(directory / "launcher/xsdb_entry.bat")[0] != plan["batch_sha256"]
                or record.get("batch_sha256") != plan["batch_sha256"]):
            raise ToolError("官方bat快照与实际启动输入哈希不一致")
        if (record.get("root_exit_code") != 0 or record.get("status") != "PASS_PROCESS_ONLY"
                or record.get("cleanup_confirmed") is not True or record.get("errors") or record.get("timed_out")
                or not record.get("assigned") or not record.get("resumed") or not record.get("job_samples")
                or record["job_samples"][-1].get("ActiveProcesses") != 0):
            raise ToolError("真实Job执行或收尾未通过")
        if ((directory / "launcher/stdout.bin").read_bytes() != (directory / "xsdb.stdout.log").read_bytes()
                or (directory / "launcher/stderr.bin").read_bytes() != (directory / "xsdb.stderr.log").read_bytes()):
            raise ToolError("真实Job原始输出与capture输出不一致")
    if not isinstance(manifest.get("context"), dict):
        raise ToolError(f"capture context 缺失: {directory}")
    context = manifest["context"]
    if any(manifest.get(key) != context.get(key) for key in ("window_id", "event_id", "lifecycle_id")):
        raise ToolError(f"capture 顶层与 context 身份字段不一致: {directory}")
    if manifest["schema"].endswith(".v2"):
        verified_context, digest, size = load_context(directory / "context.json", manifest["window_id"], manifest["event_id"])
        if verified_context != context:
            raise ToolError("真实采样context快照与清单语义不一致")
        source_context = manifest.get("context_file", {})
        source_auth = manifest.get("authorization_file", {})
        auth_digest, auth_size = sha256_file(directory / "authorization.md")
        if (source_context.get("sha256") != digest or source_context.get("bytes") != size
                or source_auth.get("sha256") != auth_digest or source_auth.get("bytes") != auth_size):
            raise ToolError("context或授权原始输入身份不匹配")
    data = (directory / READ_A_NAME).read_bytes()
    timestamp = manifest.get("captured_at_utc8")
    if not isinstance(timestamp, str):
        raise ToolError(f"capture 时间戳缺失: {directory}")
    try:
        captured = datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ToolError(f"capture 时间戳格式错误: {directory}") from exc
    if captured.tzinfo is None:
        raise ToolError(f"capture 时间戳必须包含时区: {directory}")
    return manifest, data, captured.isoformat()


def context_identity(manifest: dict[str, Any]) -> dict[str, Any]:
    context = manifest["context"]
    keys = (
        "window_id",
        "event_id",
        "lifecycle_id",
        "target",
        "filter",
        "bit_sha256",
        "init_elf_sha256",
        "app_elf_sha256",
        "cpu0_state",
        "cpu1_state",
        "masters_quiesced",
        "cache_basis",
    )
    if any(key not in context for key in keys):
        raise ToolError("capture context schema 不完整")
    return {key: context[key] for key in keys}


def compare(before_text: str, after_text: str, out_text: str) -> tuple[dict[str, Any], int]:
    before_dir = Path(before_text).expanduser().resolve(strict=True)
    after_dir = Path(after_text).expanduser().resolve(strict=True)
    if not before_dir.is_dir() or not after_dir.is_dir():
        raise ToolError("before/after 必须是目录")
    if os.path.samefile(before_dir, after_dir):
        raise ToolError("before 与 after 不能指向同一目录")
    out_dir = validate_new_output(out_text)
    if out_dir == before_dir or out_dir == after_dir:
        raise ToolError("输出目录不能与输入目录相同")
    before, before_bytes, before_time = verify_capture(before_dir, "before")
    after, after_bytes, after_time = verify_capture(after_dir, "after")
    if context_identity(before) != context_identity(after):
        raise ToolError("before/after context 身份漂移")
    if before["schema"].endswith(".v2") and after["schema"].endswith(".v2"):
        if before["xsdb"]["launcher_record"]["batch_sha256"] != after["xsdb"]["launcher_record"]["batch_sha256"]:
            raise ToolError("before/after官方bat身份漂移")
    if before["window_id"] != after["window_id"] or before["event_id"] != after["event_id"] or before["lifecycle_id"] != after["lifecycle_id"]:
        raise ToolError("before/after window/event/lifecycle 不一致")
    before_dt = datetime.fromisoformat(before_time)
    after_dt = datetime.fromisoformat(after_time)
    if after_dt <= before_dt:
        raise ToolError("after 采样时间必须晚于 before")
    baseline_hash = hashlib.sha256(before_bytes).hexdigest()
    if baseline_hash != BASELINE_SHA256:
        raise ToolError(f"before 全区 SHA-256 不等于固定 baseline: {baseline_hash}")
    if len(before_bytes) != DDR_BYTES or len(after_bytes) != DDR_BYTES:
        raise ToolError("比较输入长度错误")

    changed_bytes = 0
    changed_bits = 0
    one_to_zero = 0
    zero_to_one = 0
    addresses: list[str] = []
    for offset, (old, new) in enumerate(zip(before_bytes, after_bytes, strict=True)):
        delta = old ^ new
        if delta:
            changed_bytes += 1
            changed_bits += delta.bit_count()
            one_to_zero += (old & ~new).bit_count()
            zero_to_one += (~old & new).bit_count()
            if len(addresses) < 1000:
                addresses.append(f"0x{DDR_START + offset:08X}")
    status = "PAIR_UNCHANGED" if changed_bytes == 0 else "REGION_CHANGED"
    report = {
        "schema": "gestureforge.m3_pair.comparison.v1",
        "status": status,
        "hardware_launcher_v2_bound": before["schema"].endswith(".v2") and after["schema"].endswith(".v2"),
        "legacy_scope": "v1仅作历史离线字节比较，不是本轮真实板级入口证明",
        "hash_basis": "worktree_disk",
        "compared_at_utc8": now_utc8(),
        "window_id": before["window_id"],
        "event_id": before["event_id"],
        "lifecycle_id": before["lifecycle_id"],
        "before_directory": str(before_dir),
        "after_directory": str(after_dir),
        "before_captured_at_utc8": before_time,
        "after_captured_at_utc8": after_time,
        "baseline_sha256_required": BASELINE_SHA256,
        "before_sha256": baseline_hash,
        "after_sha256": hashlib.sha256(after_bytes).hexdigest(),
        "address_start_inclusive": f"0x{DDR_START:08X}",
        "address_end_exclusive": f"0x{DDR_END:08X}",
        "bytes_compared": DDR_BYTES,
        "changed_bytes": changed_bytes,
        "changed_bits": changed_bits,
        "one_to_zero_bits": one_to_zero,
        "zero_to_one_bits": zero_to_one,
        "changed_address_count": changed_bytes,
        "changed_addresses": addresses,
        "changed_addresses_limit": 1000,
        "changed_addresses_truncated": changed_bytes > len(addresses),
        "interpretation": "本报告仅描述候选区两次离线取样差异；不自动判定预期写入、不执行恢复，也不代表 M3 或阶段验收通过。",
    }
    out_dir.mkdir()
    write_manifest_with_checksum(out_dir / PAIR_MANIFEST_NAME, report, out_dir / PAIR_HASH_NAME)
    return report, 0 if status == "PAIR_UNCHANGED" else 1


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="只读采集并比较固定 DDR 候选区的 M3 成对快照")
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture", help="使用 XSDB 对固定 DDR 区做双读取样")
    capture_parser.add_argument("--out", required=True, help="必须是全新的输出目录")
    capture_parser.add_argument("--xsdb", required=True, help="精确 XSDB .exe 或 .bat 路径")
    capture_parser.add_argument("--port", required=True, type=int, help="本机 hw_server 监听端口")
    capture_parser.add_argument("--window-id", required=True)
    capture_parser.add_argument("--phase", required=True, choices=("before", "after"))
    capture_parser.add_argument("--event-id", required=True)
    capture_parser.add_argument("--authorization-file", required=True, help="只记录文件 SHA-256，不验证审批有效性")
    capture_parser.add_argument("--context-file", required=True, help="含核/主设备/部署身份的 JSON")
    capture_parser.add_argument("--timeout-seconds", type=int, default=120, help="XSDB 整体超时，1–600 秒，默认 120")
    compare_parser = sub.add_parser("compare", help="校验并比较 before/after capture 目录")
    compare_parser.add_argument("--before", required=True)
    compare_parser.add_argument("--after", required=True)
    compare_parser.add_argument("--out", required=True, help="必须是全新的报告目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "capture":
            result = capture(
                out_text=args.out,
                xsdb_text=args.xsdb,
                port=args.port,
                window_id=args.window_id,
                phase=args.phase,
                event_id=args.event_id,
                authorization_file_text=args.authorization_file,
                context_file_text=args.context_file,
                timeout_seconds=args.timeout_seconds,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        report, status_code = compare(args.before, args.after, args.out)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return status_code
    except (ToolError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
