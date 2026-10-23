#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从冻结2B应用生成并交叉构建INT8_CHW诊断ELF，不生成平台或PL。"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RUN_ID_DEFAULT = "s4b_ps_tensor_20261023_r01"
BASE_APP_SHA256 = "9ed222a1d132d8cc836c362b4fbe453f833387bc66173dd5eb7d5388447e9a39"
BUNDLE_SHA256 = "50b5eb62968795413e03f4474dd98800c8e2c1f0ead04003ae53b47b83ea9436"
XSA_SHA256 = "ea52da1b143f15331a42ea8bdd27578f5d814368f77d7b779f7fa650f5cb0eb6"
MODEL_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
FREEZE_RECEIPT_SHA256 = "2687e87a9664d6415d17738a6f6ff10b8fe3e372696399eb710fa2d06d2778e1"
FREEZE_MANIFEST_SHA256 = "1eFC124B7C6281E453BA8A9D518D33223068AB1818D958ED9938144868E1AA66".lower()
BUNDLE_PATH = Path(
    r"D:\FPGA_Competition\w2b\report\evidence\S2B-T15\recovery_inputs_20261019_r02\recovery_bundle.zip"
)
BASE_APP_PATH = Path(r"D:\FPGA_Competition\w2b\vitis\s2b_inference_app.c")
FREEZE_RECEIPT_PATH = Path(
    r"D:\FPGA_Competition\w2b\report\evidence\S2B-T18\stage2b_freeze_receipt_20261022_r01\freeze_receipt.json"
)
FREEZE_MANIFEST_PATH = Path(
    r"D:\FPGA_Competition\w2b\report\evidence\S2B-T18\stage2b_freeze_20261022_r02\delivery_manifest.json"
)
XSA_PATH = Path(
    r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.xsa"
)
MODEL_PATH = Path(r"D:\FPGA_Competition\w2b\report\evidence\S2A-T01\tiny416_model_manifest.json")
TOOLCHAIN_BIN = Path(r"D:\Xilinx\2026.1\gnu\aarch32\nt\gcc-arm-none-eabi\bin")
GCC = TOOLCHAIN_BIN / "arm-none-eabi-gcc.exe"
OBJDUMP = TOOLCHAIN_BIN / "arm-none-eabi-objdump.exe"
NM = TOOLCHAIN_BIN / "arm-none-eabi-nm.exe"
SIZE = TOOLCHAIN_BIN / "arm-none-eabi-size.exe"
GCC_SHA256 = "5564b16b151c1c8d626531440c538866aa938bdcecd7460be03ab6a43377a72f"
OBJDUMP_SHA256 = "e3950ce4ea6c8986839f8533a35b1b86906887d0d974a5eb91450d7d06abcc69"
NM_SHA256 = "7ab9b8d31f486b20618fe3c3f96c9bab5efce82309dad91d1f1255098dadefb7"
SIZE_SHA256 = "9194dc657881a92e005fb8edb95eb5242725e109a7e7fbe96850281a7b27fbac"
HOST_GCC = Path(r"D:\mingw64\bin\gcc.exe")
APP_MEMORY_START = 0x00100000
APP_MEMORY_END = 0x01100000
ARENA_START = 0x10000000
ARENA_BYTES = 0x02000000
TRACE_HEADER_BYTES = 144
TRACE_RECORD_BYTES = 184
TRACE_CAPACITY = 1000
NETWORK_INPUT_BYTES = 519168


class BuildError(RuntimeError):
    """表示构建或输入绑定失败。"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def replace_once(source: str, anchor: str, replacement: str, label: str) -> str:
    count = source.count(anchor)
    if count != 1:
        raise BuildError(f"派生锚点数量错误 {label}: expected=1 actual={count}")
    return source.replace(anchor, replacement, 1)


def derive_source(source_bytes: bytes) -> tuple[bytes, str]:
    """只在已绑定原文及唯一锚点时派生应用，不触碰2B原件。"""
    if sha256_bytes(source_bytes) != BASE_APP_SHA256:
        raise BuildError("冻结2B app原始SHA不匹配，拒绝派生")
    try:
        original = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BuildError(f"冻结app不是UTF-8: {exc}") from exc
    newline = "\r\n" if "\r\n" in original else "\n"
    if "\r" in original.replace("\r\n", ""):
        raise BuildError("冻结app包含未识别的换行字节")
    source = original.replace("\r\n", "\n")

    source = replace_once(
        source,
        '#include "s2a_ps_decode_nms_reference.h"\n',
        '#include "s2a_ps_decode_nms_reference.h"\n'
        '#include "s4b_ps_trace.h"\n'
        '#include "s4b_ps_build_config.h"\n',
        "trace_headers",
    )
    source = replace_once(
        source,
        "static int diag_ack_pending;\n",
        "static int diag_ack_pending;\n"
        "static s4b_ps_trace_record *s4b_current_trace_record;\n",
        "trace_record_pointer",
    )
    source = replace_once(
        source,
        "static void barrier(void) { __asm__ volatile(\"dsb sy\" ::: \"memory\"); }\n",
        "static void barrier(void) { __asm__ volatile(\"dsb sy\" ::: \"memory\"); }\n"
        "static void s4b_trace_cache_flush(void *address, size_t length)\n"
        "{\n"
        "    Xil_DCacheFlushRange((INTPTR)(UINTPTR)address, (uint32_t)length);\n"
        "}\n"
        "static void s4b_trace_barrier(void) { barrier(); }\n",
        "trace_cache_callbacks",
    )
    source = replace_once(
        source,
        "csr_write(0x028U, core_timeout); csr_write(0x02CU, drain_timeout); barrier(); csr_write(0x008U, 1U);",
        "csr_write(0x028U, core_timeout); csr_write(0x02CU, drain_timeout); barrier(); "
        "if (s4b_current_trace_record != NULL) { "
        "s4b_ps_trace_mark_start_command(s4b_current_trace_record, ticks()); } "
        "csr_write(0x008U, 1U);",
        "start_command_timestamp",
    )

    trace_helpers = r'''static void s4b_trace_live_snapshot(s4b_ps_trace_record *record,
                                   terminal_snapshot *snap)
{
    snap->status = csr_read(0x00CU);
    snap->frame = csr_read(0x058U);
    snap->error = csr_read(0x010U);
    snap->reject = csr_read(0x064U);
    (void)read_epoch(&snap->epoch);
    s4b_ps_trace_mark_terminal(record, snap->epoch, snap->frame, snap->status,
                               snap->error, snap->reject, 0, 0, 0U);
}

static int s4b_trace_snapshot_is_safe(const terminal_snapshot *snap)
{
    uint32_t state = snap->status & 7U;
    if ((state != DONE_SAFE && state != ERROR_SAFE) ||
        (snap->status & (SAFE_REUSE | TERMINAL)) != (SAFE_REUSE | TERMINAL) ||
        (snap->status & (OWNER_PL | AXI_PENDING | FIRST_PENDING)) != 0U) return 0;
    return state == DONE_SAFE ? ((snap->status & HEAD_VALID) != 0U && snap->error == 0U) :
                               ((snap->status & HEAD_VALID) == 0U && snap->error != 0U);
}

static int s4b_trace_snapshot_has_terminal(const terminal_snapshot *snap)
{
    return (snap->status & TERMINAL) != 0U;
}

static int s4b_trace_commit_without_uart(s4b_ps_trace_record *record,
                                         uint32_t response_status)
{
    int committed;
    s4b_ps_trace_set_response(record, response_status, UINT32_MAX, 0U, 0U);
    committed = s4b_ps_trace_commit(record, ticks());
    s4b_current_trace_record = NULL;
    return committed;
}

static int s4b_trace_send_result(const wire_header *request,
                                 terminal_snapshot *snap, uint32_t index,
                                 uint32_t response_status, uint32_t decode_status,
                                 uint32_t detection_count, uint32_t raw_count,
                                 int include_heads, int ack_after_send,
                                 int success_path, s4b_ps_trace_record *record)
{
    uint64_t send_start, send_done;
    int sent, acked;

    s4b_ps_trace_set_response(record, response_status, decode_status,
                              detection_count, raw_count);
    if (!s4b_ps_trace_commit(record, ticks())) {
        s4b_current_trace_record = NULL;
        return 0;
    }
    send_start = ticks();
    sent = send_response(request, snap, index, response_status,
                         detection_count, raw_count, include_heads);
    send_done = ticks();
    s4b_ps_trace_mark_uart(record, send_start, send_done, sent);
    acked = 0;
    if (sent != 0 && ack_after_send != 0) {
        acked = acknowledge(snap);
        s4b_ps_trace_mark_ack(record, acked);
    }
    s4b_current_trace_record = NULL;
    return success_path != 0 ? acked : 0;
}

'''
    source = replace_once(
        source,
        "static int configure_start(uint32_t frame, uint32_t core_timeout, uint32_t drain_timeout, uint32_t input_bytes, uint64_t *expected)\n",
        trace_helpers
        + "static int configure_start(uint32_t frame, uint32_t core_timeout, uint32_t drain_timeout, uint32_t input_bytes, uint64_t *expected)\n",
        "trace_result_helpers",
    )

    infer_start = "static int infer_one(const wire_header *request, uint32_t index, uint32_t core_timeout, uint32_t drain_timeout)\n"
    infer_end = "static int diagnostic(const wire_header *request)\n"
    if source.count(infer_start) != 1 or source.count(infer_end) != 1:
        raise BuildError("infer_one边界锚点不唯一，拒绝派生")
    start = source.index(infer_start)
    end = source.index(infer_end, start)
    derived_infer = r'''static int infer_one(const wire_header *request, uint32_t index,
                     uint32_t core_timeout, uint32_t drain_timeout)
{
    terminal_snapshot snap = {0U,0U,0U,0U,0U};
    uint64_t epoch;
    size_t count = 0U, raw_count = 0U;
    uint32_t offset;
    int decoded;
    int safe_terminal;
    s4b_ps_trace_record *trace_record =
        s4b_ps_trace_begin_result(index, request->frame + index);

    if (trace_record == NULL) return 0;
    s4b_current_trace_record = trace_record;
    if (!is_idle()) {
        s4b_trace_live_snapshot(trace_record, &snap);
        (void)s4b_trace_commit_without_uart(trace_record, BAD_STATE);
        return 0;
    }
    prepare_cache();
    if (!configure_start(request->frame + index, core_timeout, drain_timeout,
                         INPUT_BYTES, &epoch)) {
        s4b_trace_live_snapshot(trace_record, &snap);
        (void)s4b_trace_commit_without_uart(trace_record, BAD_STATE);
        return 0;
    }
    if (!wait_safe(&snap, epoch, request->frame + index)) {
        int terminal_observed = s4b_trace_snapshot_has_terminal(&snap);
        safe_terminal = s4b_trace_snapshot_is_safe(&snap);
        s4b_ps_trace_mark_terminal(trace_record, snap.epoch, snap.frame,
                                   snap.status, snap.error, snap.reject,
                                   terminal_observed, safe_terminal, ticks());
        return s4b_trace_send_result(request, &snap, index, OBSERVE_TIMEOUT,
                                     UINT32_MAX, 0U, 0U, 0, 0, 0, trace_record);
    }
    s4b_ps_trace_mark_terminal(trace_record, snap.epoch, snap.frame,
                               snap.status, snap.error, snap.reject,
                               1, 1, ticks());
    feature_invalidate();
    if ((snap.status & 7U) != DONE_SAFE) {
        return s4b_trace_send_result(request, &snap, index, BOARD_ERROR,
                                     UINT32_MAX, 0U, 0U, 0, 1, 0, trace_record);
    }
    for (offset = 0U; offset < HEAD13_BYTES; ++offset) {
        logits13[offset] = (double)(int8_t)arena[0x01A46100U + offset] * S2B_HEAD13_SCALE;
    }
    for (offset = 0U; offset < HEAD26_BYTES; ++offset) {
        logits26[offset] = (double)(int8_t)arena[0x01AD5E80U + offset] * S2B_HEAD26_SCALE;
    }
    decoded = s2a_t62_decode_nms(logits13, HEAD13_BYTES, logits26, HEAD26_BYTES,
                                 request->width, request->height, 0.25,
                                 boxes, 15U, &count, &raw_count);
    s4b_ps_trace_mark_postprocess(trace_record, (uint32_t)decoded,
                                  (uint32_t)count, (uint32_t)raw_count, ticks());
    if (decoded != S2A_T62_OK) {
        return s4b_trace_send_result(request, &snap, index, DECODE_ERROR,
                                     (uint32_t)decoded, 0U, 0U, 0, 0, 0,
                                     trace_record);
    }
    return s4b_trace_send_result(request, &snap, index, RESPONSE_OK,
                                 (uint32_t)decoded, (uint32_t)count,
                                 (uint32_t)raw_count, 1, 1, 1, trace_record);
}

'''
    source = source[:start] + derived_infer + source[end:]

    service_anchor = (
        "    core = get32(staging); drain = get32(staging + 4U);\n"
        "    if (!weights_loaded || core == 0U || drain == 0U) {\n"
        "        (void)send_response(&request, &snap, 0U, BAD_PARAMETERS, 0U, 0U, 0); return 0;\n"
        "    }\n"
        "    memcpy(arena, staging + 8U, INPUT_BYTES); input_loaded = 1;\n"
        "    for (index = 0U; index < request.repeat; ++index) if (!infer_one(&request, index, core, drain)) return 0;\n"
        "    return 1;"
    )
    service_replacement = r'''    uint32_t session_id;
    uint64_t input_write_start, input_write_done;
    uint32_t input_crc32;
    int session_ready;

    core = get32(staging); drain = get32(staging + 4U);
    if (!weights_loaded || core == 0U || drain == 0U) {
        s4b_ps_trace_note_rejection(request.sequence, request.frame,
                                    S4B_PS_TRACE_REJECT_BAD_RUN);
        (void)send_response(&request, &snap, 0U, BAD_PARAMETERS, 0U, 0U, 0);
        return 0;
    }
    input_crc32 = crc32_ieee(staging + 8U, INPUT_BYTES);
    session_ready = s4b_ps_trace_begin_run(request.sequence, request.frame,
                                           request.repeat, input_crc32,
                                           INPUT_BYTES, &session_id);
    if (!session_ready) {
        snap.status = csr_read(0x00CU); snap.frame = csr_read(0x058U);
        snap.error = csr_read(0x010U); snap.reject = csr_read(0x064U);
        (void)read_epoch(&snap.epoch);
        (void)send_response(&request, &snap, 0U, BAD_STATE, 0U, 0U, 0);
        return 0;
    }
    (void)session_id;
    input_write_start = ticks();
    memcpy(arena, staging + 8U, INPUT_BYTES);
    input_write_done = ticks();
    s4b_ps_trace_set_input_write_ticks(input_write_start, input_write_done);
    input_loaded = 1;
    for (index = 0U; index < request.repeat; ++index) {
        if (!infer_one(&request, index, core, drain)) {
            (void)s4b_ps_trace_end_run(0);
            return 0;
        }
    }
    if (!s4b_ps_trace_end_run(1)) return 0;
    return 2;'''
    source = replace_once(source, service_anchor, service_replacement, "run_session_and_input_hooks")

    main_loop_anchor = (
        "    while (service_request()) publish(2U);\n"
        "    /* 失败保留所有权、账本和未ACK终态；不会复位PL或自动重新准入。 */\n"
    )
    main_loop_replacement = (
        "    for (;;) {\n"
        "        int service_status = service_request();\n"
        "        if (service_status == 0) break;\n"
        "        publish(2U);\n"
        "        if (service_status == 2) {\n"
        "            /* 成功RUN终态后不再读取后续请求，保持应用停泊。 */\n"
        "            for (;;) __asm__ volatile(\"wfe\" ::: \"memory\");\n"
        "        }\n"
        "    }\n"
        "    /* 失败保留所有权、账本和未ACK终态；不会复位PL或自动重新准入。 */\n"
    )
    source = replace_once(source, main_loop_anchor, main_loop_replacement,
                          "one_shot_successful_run_park")

    main_init_anchor = "    if (!initialise()) { publish(0xE001U); return 1; }\n"
    main_init_replacement = (
        main_init_anchor
        + "    if (!s4b_ps_trace_initialize(S4B_PS_BOOT_SEED, S4B_PS_SESSION_FIRST,\n"
        + "                                 S4B_PS_SESSION_LAST, S2B_C_SOURCE_SHA256,\n"
        + "                                 s4b_trace_cache_flush, s4b_trace_barrier)) {\n"
        + "        publish(0xE004U); return 1;\n"
        + "    }\n"
    )
    source = replace_once(source, main_init_anchor, main_init_replacement, "trace_runtime_initialization")
    banner_anchor = '"S2B-INFERENCE/1 READY SOURCE=%s XSA=%s MODEL=%s\\r\\n",'
    banner_replacement = (
        '"S2B-INFERENCE/1 READY SOURCE=%s XSA=%s MODEL=%s '
        'DIAG=s4b-ps-tensor/1 TRACE_ABI=1\\r\\n",'
    )
    source = replace_once(source, banner_anchor, banner_replacement, "derived_identity_banner")

    encoded = source.replace("\n", newline).encode("utf-8")
    return encoded, sha256_bytes(encoded)


def build_config_header(boot_seed: int, session_first: int, session_last: int) -> bytes:
    source = (
        "#ifndef S4B_PS_BUILD_CONFIG_H\n"
        "#define S4B_PS_BUILD_CONFIG_H\n"
        "#include <stdint.h>\n"
        f"#define S4B_PS_BOOT_SEED UINT64_C(0x{boot_seed:016x})\n"
        f"#define S4B_PS_SESSION_FIRST 0x{session_first:08x}U\n"
        f"#define S4B_PS_SESSION_LAST 0x{session_last:08x}U\n"
        "#endif\n"
    )
    return source.encode("utf-8")


def parse_u32(value: str) -> int:
    parsed = int(value, 0)
    if parsed < 0 or parsed > 0xFFFFFFFF:
        raise argparse.ArgumentTypeError("数值必须在u32范围内")
    return parsed


def parse_u64(value: str) -> int:
    parsed = int(value, 0)
    if parsed <= 0 or parsed > 0xFFFFFFFFFFFFFFFF:
        raise argparse.ArgumentTypeError("boot seed必须是非零u64")
    return parsed


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def exact_file(path: Path, expected_sha: str | None, label: str) -> dict[str, Any]:
    if not path.is_file():
        return {"label": label, "path": str(path), "exists": False, "sha256": None,
                "expected_sha256": expected_sha, "status": "MISSING"}
    actual = sha256_file(path)
    return {"label": label, "path": str(path), "exists": True, "bytes": path.stat().st_size,
            "sha256": actual, "expected_sha256": expected_sha,
            "status": "PASS" if expected_sha is None or actual == expected_sha else "FAIL"}


def validate_bundle_member(name: str) -> PurePosixPath:
    """只接受恢复包工作区下无歧义的相对POSIX文件名。"""
    if not isinstance(name, str) or not name or "\x00" in name:
        raise BuildError(f"恢复包成员路径格式无效: {name!r}")
    if "\\" in name or ":" in name:
        raise BuildError(f"恢复包成员含Windows路径分隔符或盘符: {name!r}")
    windows_path = PureWindowsPath(name)
    relative = PurePosixPath(name)
    if (windows_path.is_absolute() or windows_path.drive or windows_path.root or
            relative.is_absolute() or any(part in ("", ".", "..") for part in name.split("/"))):
        raise BuildError(f"恢复包成员不是安全相对路径: {name!r}")
    if not name.startswith("bundle/workspace/") or len(relative.parts) < 3:
        raise BuildError(f"恢复包成员不在bundle/workspace前缀内: {name!r}")
    if any(part.endswith((".", " ")) for part in relative.parts):
        raise BuildError(f"恢复包成员含Windows别名路径段: {name!r}")
    if relative.as_posix() != name:
        raise BuildError(f"恢复包成员路径未规范化: {name!r}")
    return relative


def bundle_members(bundle_path: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    if sha256_file(bundle_path) != BUNDLE_SHA256:
        raise BuildError("冻结恢复包SHA不匹配，拒绝解包")
    with zipfile.ZipFile(bundle_path, "r") as archive:
        validate_bundle_member("bundle/workspace/manifest.json")
        raw_manifest = archive.read("bundle/workspace/manifest.json")
        manifest = json.loads(raw_manifest.decode("utf-8"))
        entries: dict[str, bytes] = {}
        for item in manifest.get("files", []):
            validate_bundle_member(item["path"])
            content = archive.read(item["path"])
            if len(content) != item["bytes"] or sha256_bytes(content) != item["sha256"]:
                raise BuildError(f"恢复包成员校验失败: {item['path']}")
            entries[item["path"]] = content
        listed = set(entries)
        actual = set()
        for item in archive.infolist():
            if item.is_dir():
                continue
            validate_bundle_member(item.filename)
            if item.filename != "bundle/workspace/manifest.json":
                actual.add(item.filename)
        if actual != listed:
            raise BuildError("恢复包成员集合与冻结manifest不一致")
    return entries, manifest


def extract_members(entries: dict[str, bytes], destination: Path) -> None:
    root = destination.resolve(strict=False)
    planned: list[tuple[str, bytes, Path]] = []
    seen_targets: set[str] = set()
    for name, content in entries.items():
        relative = validate_bundle_member(name)
        target = destination.joinpath(*relative.parts)
        resolved = target.resolve(strict=False)
        if not resolved.is_relative_to(root) or resolved == root:
            raise BuildError(f"解包目标解析后越出新解包根: {name}")
        key = str(resolved).casefold()
        if key in seen_targets:
            raise BuildError(f"恢复包成员映射到重复目标: {name}")
        seen_targets.add(key)
        planned.append((name, content, target))

    for name, content, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.resolve(strict=False).is_relative_to(root):
            raise BuildError(f"解包目录创建后目标越出新解包根: {name}")
        target.write_bytes(content)


def tool_output(command: list[str], cwd: Path | None = None, timeout: int = 30,
                extra_env: dict[str, str] | None = None) -> tuple[int, bytes, bytes]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["LC_ALL"] = "C"
    if extra_env:
        env.update(extra_env)
    try:
        result = subprocess.run(command, cwd=str(cwd) if cwd else None, capture_output=True,
                                timeout=timeout, env=env, check=False)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else b""
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
        return 124, stdout, stderr + b"\nTIMEOUT\n"
    return result.returncode, result.stdout, result.stderr


def persist_command(evidence_dir: Path, name: str, command: list[str], cwd: Path,
                    timeout: int, results: list[dict[str, Any]],
                    extra_env: dict[str, str] | None = None) -> tuple[int, str, str]:
    started = time.perf_counter()
    code, stdout, stderr = tool_output(command, cwd, timeout, extra_env)
    elapsed = time.perf_counter() - started
    stdout_path = evidence_dir / f"{name}.stdout.txt"
    stderr_path = evidence_dir / f"{name}.stderr.txt"
    try:
        stdout_text = stdout.decode("utf-8", errors="strict")
        stderr_text = stderr.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        stdout_path.with_suffix(".stdout.bytes").write_bytes(stdout)
        stderr_path.with_suffix(".stderr.bytes").write_bytes(stderr)
        raise BuildError(f"命令输出不能严格UTF-8解码，原始bytes已保留: {name}: {exc}") from exc
    stdout_path.write_text(stdout_text, encoding="utf-8", newline="\n")
    stderr_path.write_text(stderr_text, encoding="utf-8", newline="\n")
    results.append({
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "exit_code": code,
        "elapsed_seconds": round(elapsed, 6),
        "stdout_path": stdout_path.name,
        "stdout_sha256": sha256_file(stdout_path),
        "stderr_path": stderr_path.name,
        "stderr_sha256": sha256_file(stderr_path),
    })
    return code, stdout_text, stderr_text


def parse_unittest_summary(output: str) -> int:
    """逐行解析unittest摘要，兼容LF/CRLF并支持单项测试语法。"""
    summaries = [
        re.fullmatch(r"Ran (\d+) tests? in .+", line)
        for line in output.splitlines()
    ]
    matches = [match for match in summaries if match is not None]
    if len(matches) != 1:
        raise BuildError(f"unittest摘要缺失或不唯一: matches={len(matches)}")
    return int(matches[0].group(1))


def run_host_tests(evidence_dir: Path, tmp_dir: Path,
                   results: list[dict[str, Any]]) -> dict[str, Any]:
    host_dir = tmp_dir / "host_tests"
    host_dir.mkdir()
    trace_source = ROOT / "vitis/stage4/ps/s4b_ps_trace.c"
    test_source = ROOT / "verification/test_s4b_ps_trace_api.c"
    executable = host_dir / "test_s4b_ps_trace_api.exe"
    host_command = [
        str(HOST_GCC), "-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic",
        "-Wconversion", "-Wshadow", "-Werror", "-I", str(trace_source.parent),
        str(trace_source), str(test_source), "-o", str(executable),
    ]
    code, _, stderr = persist_command(evidence_dir, "host_c_api_compile", host_command,
                                      host_dir, 60, results)
    if code != 0:
        raise BuildError(f"嚴格host C API构建失败，exit={code}: {stderr[-500:]}")

    code, output, stderr = persist_command(evidence_dir, "host_c_api_regression",
                                           [str(executable)], host_dir, 30, results)
    if code != 0 or "PASS trace_api" not in output:
        raise BuildError(f"host C API回归失败，exit={code}: {stderr[-500:]}")
    code, output, stderr = persist_command(
        evidence_dir, "host_c_api_session_exhaustion",
        [str(executable), "--range-exhaustion"], host_dir, 30, results,
    )
    if code != 0 or "PASS session_range_exhaustion" not in output:
        raise BuildError(f"host u32会话耗尽回归失败，exit={code}: {stderr[-500:]}")

    python_command = [str(Path(sys.executable)), "-B", "-m", "unittest",
                      "verification.test_s4b_ps_tensor", "-v"]
    path_probe_root = tmp_dir / "path_guard_probe"
    path_probe_root.mkdir()
    code, output, stderr = persist_command(evidence_dir, "python_unit_suite",
                                           python_command, ROOT, 90, results,
                                           {"S4B_PS_TEST_TMP_ROOT": str(path_probe_root)})
    combined_output = output + stderr
    python_test_count = parse_unittest_summary(combined_output)
    required_tests = (
        "test_network_input_range_matches_frozen_tensor_length",
        "test_network_input_range_rejects_short_arena",
        "test_bundle_paths_reject_windows_and_traversal_before_writes",
        "test_memory_map_reports_complete_exception_stacks",
        "test_decoder_rejects_crc_repaired_semantic_contradictions",
        "test_decoder_requires_expected_source_and_boot_identity",
        "test_decoder_accepts_initialized_empty_trace",
        "test_decoder_rejects_session_and_last_run_header_mismatch",
    )
    if (code != 0 or python_test_count <= 0 or "OK" not in combined_output.splitlines()
            or any(test_name not in combined_output for test_name in required_tests)):
        raise BuildError(f"Python测试套件失败，exit={code}: {stderr[-500:]}")
    return {
        "strict_host_c_compile": "PASS",
        "direct_c_api_regression": "PASS",
        "u32_session_exhaustion": "PASS",
        "python_unit_tests": python_test_count,
        "python_unit_status": "PASS",
        "host_c_test_executable_sha256": sha256_file(executable),
        "host_c_test_executable_bytes": executable.stat().st_size,
    }


def replace_embedded_source_sha(platform_header: bytes, derived_sha: str) -> bytes:
    text = platform_header.decode("utf-8")
    pattern = re.compile(r'(?m)(#define S2B_C_SOURCE_SHA256 ")[0-9a-f]{64}("\s*)')
    result, count = pattern.subn(lambda match: match.group(1) + derived_sha + match.group(2), text)
    if count != 1:
        raise BuildError(f"平台头SOURCE锚点数量错误: {count}")
    return result.encode("utf-8")


def parse_symbol_table(nm_text: str) -> dict[str, int]:
    symbols: dict[str, int] = {}
    for line in nm_text.splitlines():
        match = re.match(r"^([0-9a-fA-F]+)\s+\S\s+(\S+)$", line.strip())
        if match:
            symbols[match.group(2)] = int(match.group(1), 16)
    return symbols


def parse_sections(objdump_text: str) -> dict[str, tuple[int, int]]:
    sections: dict[str, tuple[int, int]] = {}
    for line in objdump_text.splitlines():
        match = re.match(r"^\s*\d+\s+(\S+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", line)
        if match:
            sections[match.group(1)] = (int(match.group(2), 16), int(match.group(3), 16))
    return sections


def network_input_region(tensor_start: int, tensor_end: int) -> tuple[int, int, int]:
    """按冻结输入长度计算并核验网络输入的半开地址范围。"""
    input_end = tensor_start + NETWORK_INPUT_BYTES
    if input_end - tensor_start != NETWORK_INPUT_BYTES:
        raise BuildError("网络输入区域长度与冻结519168B不一致")
    if input_end > tensor_end:
        raise BuildError("519168B INT8_CHW输入超出冻结tensor arena")
    return tensor_start, input_end, input_end - tensor_start


def verify_memory_map(nm_text: str, sections_text: str) -> dict[str, Any]:
    symbols = parse_symbol_table(nm_text)
    sections = parse_sections(sections_text)
    required = {
        "__bss_start", "__bss_end", "_heap_start", "_heap_end",
        "_stack_end", "_stack", "__stack", "_irq_stack_end", "__irq_stack",
        "_supervisor_stack_end", "__supervisor_stack", "_abort_stack_end", "__abort_stack",
        "_fiq_stack_end", "__fiq_stack", "_undef_stack_end", "__undef_stack",
        "__s2b_tensor_start", "__s2b_tensor_end", "s4b_ps_trace_header_data",
        "s4b_ps_trace_records", "staging",
    }
    missing = sorted(required - symbols.keys())
    if missing:
        raise BuildError("ELF缺少必要范围符号: " + ", ".join(missing))
    bss_start, bss_end = symbols["__bss_start"], symbols["__bss_end"]
    heap_start, heap_end = symbols["_heap_start"], symbols["_heap_end"]
    stack_start = symbols["_stack_end"]
    thread_stack_end = symbols["_stack"]
    stack_ranges = {
        "main": (stack_start, thread_stack_end, 65536),
        "IRQ": (symbols["_irq_stack_end"], symbols["__irq_stack"], 1024),
        "SVC": (symbols["_supervisor_stack_end"], symbols["__supervisor_stack"], 2048),
        "ABT": (symbols["_abort_stack_end"], symbols["__abort_stack"], 1024),
        "FIQ": (symbols["_fiq_stack_end"], symbols["__fiq_stack"], 1024),
        "UND": (symbols["_undef_stack_end"], symbols["__undef_stack"], 1024),
    }
    ordered_ranges = list(stack_ranges.items())
    for index, (name, (start, end, expected_size)) in enumerate(ordered_ranges):
        if end < start or end - start != expected_size:
            raise BuildError(f"{name}栈符号范围或大小不符合冻结linker script")
        if index > 0 and ordered_ranges[index - 1][1][1] != start:
            raise BuildError(f"{name}栈与前一栈不连续或顺序错误")
    full_stack_end = stack_ranges["UND"][1]
    full_stack_bytes = full_stack_end - stack_start
    if symbols["__stack"] != thread_stack_end:
        raise BuildError("主栈别名符号__stack与_stack不一致")
    if full_stack_bytes != 71680:
        raise BuildError("完整.stack范围不等于冻结的71680B")
    header_address = symbols["s4b_ps_trace_header_data"]
    records_address = symbols["s4b_ps_trace_records"]
    records_end = records_address + TRACE_CAPACITY * TRACE_RECORD_BYTES
    staging_start = symbols["staging"]
    staging_end = staging_start + 5903100
    tensor_start, tensor_end = symbols["__s2b_tensor_start"], symbols["__s2b_tensor_end"]
    if not (APP_MEMORY_START <= bss_start <= bss_end <= APP_MEMORY_END):
        raise BuildError(".bss超出PS app DDR区域")
    if not (APP_MEMORY_START <= heap_start <= heap_end <= stack_start < full_stack_end <= APP_MEMORY_END):
        raise BuildError("heap/stack范围越出PS app DDR或顺序错误")
    if not (bss_start <= header_address and header_address + TRACE_HEADER_BYTES <= bss_end):
        raise BuildError("旁路日志头未完整落在.bss")
    if not (bss_start <= records_address and records_end <= bss_end):
        raise BuildError("旁路记录数组未完整落在.bss")
    if not (bss_start <= staging_start and staging_end <= bss_end):
        raise BuildError("冻结权重/输入staging未完整落在.bss")
    if header_address < staging_end and staging_start < header_address + TRACE_HEADER_BYTES:
        raise BuildError("旁路日志头与staging重叠")
    if records_address < staging_end and staging_start < records_end:
        raise BuildError("旁路记录数组与staging重叠")
    header_end = header_address + TRACE_HEADER_BYTES
    if records_address < header_end and header_address < records_end:
        raise BuildError("旁路记录数组与日志头重叠")
    if not (tensor_start == ARENA_START and tensor_end - tensor_start == ARENA_BYTES):
        raise BuildError("冻结tensor arena地址或长度变化")
    input_start, network_input_end, input_size = network_input_region(tensor_start, tensor_end)
    if header_address < network_input_end and tensor_start < header_address + TRACE_HEADER_BYTES:
        raise BuildError("旁路日志头与519168B network_input_tensor区域重叠")
    if records_address < network_input_end and tensor_start < records_end:
        raise BuildError("旁路记录与519168B network_input_tensor区域重叠")
    if header_address < tensor_end and tensor_start < header_address + TRACE_HEADER_BYTES:
        raise BuildError("旁路日志头与完整s2b_tensor_arena区域重叠")
    if records_address < tensor_end and tensor_start < records_end:
        raise BuildError("旁路日志与s2b_tensor_arena区域重叠")
    if any(name not in sections for name in (".bss", ".heap", ".stack", ".s2b_tensor_ddr")):
        raise BuildError("ELF缺少.bss、.heap、.stack或.s2b_tensor_ddr段")
    if sections[".bss"] != (bss_end - bss_start, bss_start):
        raise BuildError(".bss段与边界符号不一致")
    if sections[".heap"] != (heap_end - heap_start, heap_start):
        raise BuildError(".heap段与边界符号不一致")
    if sections[".stack"] != (full_stack_bytes, stack_start):
        raise BuildError(".stack段未覆盖完整主栈和异常栈")
    for section_name in (".text", ".init", ".fini", ".rodata", ".data", ".mmu_tbl",
                         ".ARM.exidx", ".init_array", ".fini_array", ".drvcfg_sec", ".bss"):
        if section_name in sections:
            section_size, section_vma = sections[section_name]
            if section_size != 0 and not (
                APP_MEMORY_START <= section_vma and section_vma + section_size <= APP_MEMORY_END
            ):
                raise BuildError(f"{section_name}段越出PS app DDR区域")
            if section_name != ".bss" and section_size != 0:
                section_end = section_vma + section_size
                if (header_address < section_end and section_vma < header_address + TRACE_HEADER_BYTES) or (
                    records_address < section_end and section_vma < records_end
                ):
                    raise BuildError(f"旁路日志与{section_name}段重叠")
    tensor_section_size, tensor_section_vma = sections[".s2b_tensor_ddr"]
    if tensor_section_size != ARENA_BYTES or tensor_section_vma != ARENA_START:
        raise BuildError("ELF tensor段与冻结网络输入/arena区域不一致")
    if records_end > heap_start or header_address >= heap_start:
        raise BuildError("旁路日志与heap范围重叠")
    if records_end > stack_start or header_address >= stack_start:
        raise BuildError("旁路日志与stack范围重叠")
    return {
        "ps_app_arena": {"start": APP_MEMORY_START, "end_exclusive": APP_MEMORY_END,
                         "name": "ps_app_arena"},
        "bss": {"start": bss_start, "end_exclusive": bss_end,
                "size_bytes": bss_end - bss_start},
        "heap": {"start": heap_start, "end_exclusive": heap_end,
                 "size_bytes": heap_end - heap_start},
        "stack": {"start": stack_start, "end_exclusive": full_stack_end,
                  "size_bytes": full_stack_bytes},
        "thread_stack": {"start": stack_ranges["main"][0],
                         "end_exclusive": stack_ranges["main"][1],
                         "size_bytes": stack_ranges["main"][1] - stack_ranges["main"][0]},
        "exception_stacks": {
            name: {"start": bounds[0], "end_exclusive": bounds[1],
                   "size_bytes": bounds[1] - bounds[0]}
            for name, bounds in list(stack_ranges.items())[1:]
        },
        "trace_header": {"start": header_address,
                         "end_exclusive": header_address + TRACE_HEADER_BYTES,
                         "size_bytes": TRACE_HEADER_BYTES},
        "trace_records": {"start": records_address, "end_exclusive": records_end,
                          "size_bytes": TRACE_CAPACITY * TRACE_RECORD_BYTES,
                          "record_capacity": TRACE_CAPACITY, "record_bytes": TRACE_RECORD_BYTES},
        "staging": {"start": staging_start, "end_exclusive": staging_end,
                    "size_bytes": staging_end - staging_start},
        "network_input_tensor": {"start": input_start, "end_exclusive": network_input_end,
                                 "size_bytes": input_size, "name": "network_input_tensor"},
        "s2b_tensor_arena": {"start": tensor_start, "end_exclusive": tensor_end,
                             "size_bytes": tensor_end - tensor_start,
                             "name": "s2b_tensor_arena"},
        "elf_sections": {name: {"size_bytes": item[0], "vma": item[1]} for name, item in sections.items()},
    }


def expected_inputs() -> list[dict[str, Any]]:
    return [
        exact_file(BUNDLE_PATH, BUNDLE_SHA256, "2B恢复输入ZIP"),
        exact_file(BASE_APP_PATH, BASE_APP_SHA256, "冻结2B app源码"),
        exact_file(FREEZE_RECEIPT_PATH, FREEZE_RECEIPT_SHA256, "2B冻结回执"),
        exact_file(FREEZE_MANIFEST_PATH, FREEZE_MANIFEST_SHA256, "2B冻结交付清单"),
        exact_file(XSA_PATH, XSA_SHA256, "冻结XSA引用"),
        exact_file(MODEL_PATH, MODEL_SHA256, "冻结模型manifest"),
        exact_file(GCC, GCC_SHA256, "AArch32 GCC"),
        exact_file(OBJDUMP, OBJDUMP_SHA256, "AArch32 objdump"),
        exact_file(NM, NM_SHA256, "AArch32 nm"),
        exact_file(SIZE, SIZE_SHA256, "AArch32 size"),
        exact_file(HOST_GCC, None, "host GCC测试编译器；记录实际SHA"),
        exact_file(Path(sys.executable), None, "Python测试运行时；记录实际SHA"),
    ]


def verify_external_inputs_unchanged(before: list[dict[str, Any]]) -> list[dict[str, Any]]:
    after = expected_inputs()
    before_by_path = {item["path"].casefold(): item for item in before}
    after_by_path = {item["path"].casefold(): item for item in after}
    if before_by_path.keys() != after_by_path.keys():
        raise BuildError("构建前后外部输入路径集合变化")
    changed = [
        path for path in before_by_path
        if before_by_path[path]["status"] != "PASS" or
        after_by_path[path]["status"] != "PASS" or
        before_by_path[path]["sha256"] != after_by_path[path]["sha256"] or
        before_by_path[path]["bytes"] != after_by_path[path]["bytes"]
    ]
    if changed:
        labels = [after_by_path[path]["label"] for path in changed]
        raise BuildError("构建前后外部输入SHA/字节数发生变化: " + ", ".join(labels))
    return after


def build(args: argparse.Namespace) -> int:
    if args.boot_seed == 0 or args.session_first == 0 or args.session_last < args.session_first or args.session_last > 0xFFFFFFFE:
        raise BuildError("session range必须为非零、递增且不含回绕哨兵的u32闭区间")
    run_id = args.run_id
    evidence_rel = Path("report/evidence/S4-B") / run_id
    tmp_rel = Path("tmp/4/S4-B-REAL-01") / run_id
    evidence_dir = ROOT / evidence_rel
    tmp_dir = ROOT / tmp_rel
    if evidence_dir.exists() or tmp_dir.exists():
        raise BuildError("RunId或临时RunId已存在；拒绝覆盖旧证据")
    evidence_dir.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.parent.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir()
    tmp_dir.mkdir()

    command_results: list[dict[str, Any]] = []
    start_time = time.perf_counter()
    config = {
        "run_id": run_id,
        "boot_seed": f"0x{args.boot_seed:016x}",
        "session_first": f"0x{args.session_first:08x}",
        "session_last": f"0x{args.session_last:08x}",
        "session_allocation": "每个有效RUN递增分配一个u32 session_id；本次PS启动期间不回绕；再次启动必须使用未复用的boot_seed和互斥session区间。",
        "hardware_reservation_status": "BUILD_ONLY_NOT_RESERVED_FOR_HARDWARE",
        "run_id_unique_assertion": "本次构建使用新RunId；上板前由硬件任务负责人单独预留不重叠范围。",
    }
    write_json(evidence_dir / "run_config.json", config)
    inventory = {
        "schema_version": 1,
        "task_scope": "仅INT8_CHW_416网络推理与后处理诊断；不含RGB预处理、PL重建或硬件执行。",
        "external_inputs": expected_inputs(),
        "2b_frozen_commit": "07c3d3958578b9cc9d3b8eae3758711fe08724c2",
        "recovery_bundle_member_manifest": "bundle/workspace/manifest.json",
        "bsp_and_static_libraries": "只从已绑定恢复ZIP解包到本RunId的tmp；不复制进证据目录或Git。",
        "xsa_use": "只绑定冻结XSA的SHA作为硬件身份依据；本任务不调用平台生成器或重建XSA/PL。",
    }
    write_json(evidence_dir / "external_inputs_inventory.json", inventory)
    write_json(evidence_dir / "commands.json", {"commands": command_results})
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "RUNNING",
        "exit_code": None,
        "commands": command_results,
        "limitations": [
            "ARM ELF为冻结2B PS app的受控派生版本；不是原版2B ELF。",
            "只使用冻结恢复包中的BSP头文件/静态库/链接脚本；未运行Vitis平台重建，也未重建PL。",
            "旁路日志的时间戳为PS global timer原始ticks；首个安全终态观察时刻不是PL精确完成周期；timebase与ns换算未批准。",
            "capture_time_available=false、capture_time_ns=0；stale/timebase及正式inference_time_ns不作验收结论。",
            "真实板卡、UART、PL启动/完成、DDR导出、停止/恢复均NOT_RUN；RGB预处理BLOCKED_PENDING_G0。",
        ],
    }
    try:
        external = expected_inputs()
        write_json(evidence_dir / "external_inputs_inventory.json", {
            **inventory,
            "external_inputs": external,
        })
        failed_inputs = [item for item in external if item["status"] != "PASS"]
        if failed_inputs:
            raise BuildError("外部路径/哈希核验失败: " + ", ".join(item["label"] for item in failed_inputs))
        gcc_rc, gcc_out, gcc_err = persist_command(
            evidence_dir, "aarch32_gcc_version", [str(GCC), "--version"],
            ROOT, 30, command_results,
        )
        if gcc_rc != 0:
            raise BuildError(f"AArch32 GCC --version失败，exit={gcc_rc}: {gcc_err[-500:]}")
        host_rc, host_out, host_err = persist_command(
            evidence_dir, "host_gcc_version", [str(HOST_GCC), "--version"],
            ROOT, 30, command_results,
        )
        if host_rc != 0:
            raise BuildError(f"host GCC --version失败，exit={host_rc}: {host_err[-500:]}")
        host_test_result = run_host_tests(evidence_dir, tmp_dir, command_results)
        result["host_tests"] = host_test_result
        write_json(evidence_dir / "commands.json", {"commands": command_results})

        entries, bundle_manifest = bundle_members(BUNDLE_PATH)
        (tmp_dir / "bundle_extract").mkdir()
        extracted = tmp_dir / "bundle_extract"
        extract_members(entries, extracted)
        workspace = extracted / "bundle" / "workspace"
        source_rel = "bundle/workspace/infer/src/s2b_inference_app.c"
        source_bytes = entries[source_rel]
        if sha256_bytes(source_bytes) != BASE_APP_SHA256:
            raise BuildError("恢复包中的冻结app SHA不匹配")
        derived_bytes, derived_sha = derive_source(source_bytes)
        app_source_path = workspace / "infer/src/s2b_inference_app.c"
        app_source_path.write_bytes(derived_bytes)
        trace_header = ROOT / "vitis/stage4/ps/s4b_ps_trace.h"
        trace_source = ROOT / "vitis/stage4/ps/s4b_ps_trace.c"
        for source_path in (trace_header, trace_source):
            if not source_path.is_file():
                raise BuildError(f"本地PS诊断源码不存在: {source_path}")
        shutil.copyfile(trace_header, workspace / "infer/src/s4b_ps_trace.h")
        shutil.copyfile(trace_source, workspace / "infer/src/s4b_ps_trace.c")
        (workspace / "infer/src/s4b_ps_build_config.h").write_bytes(
            build_config_header(args.boot_seed, args.session_first, args.session_last)
        )
        old_platform = entries["bundle/workspace/infer/src/s2b_inference_platform.h"]
        (workspace / "infer/src/s2b_inference_platform.h").write_bytes(
            replace_embedded_source_sha(old_platform, derived_sha)
        )
        original_text = source_bytes.decode("utf-8").replace("\r\n", "\n")
        derived_text = derived_bytes.decode("utf-8").replace("\r\n", "\n")
        diff = difflib.unified_diff(
            original_text.splitlines(keepends=True), derived_text.splitlines(keepends=True),
            fromfile="frozen-2b-app.c", tofile="derived-s4b-ps-tensor-app.c",
        )
        (evidence_dir / "derived_source.patch").write_text("".join(diff), encoding="utf-8", newline="\n")
        (tmp_dir / "derived_app_sha256.txt").write_text(derived_sha + "\n", encoding="ascii", newline="\n")
        (tmp_dir / "derived_app_source.c").write_bytes(derived_bytes)
        write_json(tmp_dir / "bundle_manifest.json", bundle_manifest)

        app_build = tmp_dir / "infer_build"
        app_build.mkdir()
        src_dir = workspace / "infer/src"
        bsp_dir = workspace / "ps7/export/ps7/sw/cpu0"
        bsp_include = bsp_dir / "include"
        bsp_lib = bsp_dir / "lib"
        specs = bsp_dir / "Xilinx.spec"
        linker_script = src_dir / "lscript.ld"
        toolchain_root = Path(r"D:\Xilinx\2026.1\gnu\aarch32\nt\gcc-arm-none-eabi")
        gcc_root = toolchain_root / "x86_64-oesdk-mingw32/usr/lib/arm-xilinx-eabi/gcc/arm-xilinx-eabi/13.4.0"
        include_paths = [
            gcc_root / "include",
            gcc_root / "include-fixed",
            toolchain_root / "aarch32-xilinx-eabi/usr/include",
        ]
        for required_path in [bsp_include, bsp_lib, specs, linker_script, *include_paths]:
            if not required_path.exists():
                raise BuildError(f"AArch32/BSP输入路径不存在: {required_path}")
        flags = [
            "-DSDT", "-mcpu=cortex-a9", "-mfpu=vfpv3", "-mfloat-abi=hard",
            f"-specs={specs}", f"-I{bsp_include}", "-Wall", "-Wextra", "-Werror",
            "-O0", "-g3", "-std=gnu11", "-O2", "-ffunction-sections",
            "-fdata-sections", "-save-temps=obj", "-U__clang__",
        ]
        compile_flags = flags[:4] + [f"-I{src_dir}"]
        for include in include_paths:
            compile_flags.extend(["-isystem", str(include)])
        compile_flags.extend(flags[4:])
        source_names = [
            "s2a_ps_decode_nms_reference.c",
            "s2b_inference_app.c",
            "s4b_ps_trace.c",
        ]
        objects: list[Path] = []
        for index, name in enumerate(source_names):
            object_path = app_build / f"{Path(name).stem}.obj"
            command = [str(GCC), *compile_flags, "-o", str(object_path), "-c", str(src_dir / name)]
            code, _, _ = persist_command(evidence_dir, f"compile_{index:02d}_{Path(name).stem}",
                                         command, app_build, 180, command_results)
            write_json(evidence_dir / "commands.json", {"commands": command_results})
            if code != 0:
                raise BuildError(f"AArch32编译失败 {name}，exit={code}")
            objects.append(object_path)

        elf_path = app_build / "s4b_ps_tensor_diagnostic.elf"
        map_path = app_build / "s4b_ps_tensor_diagnostic.map"
        link_command = [
            str(GCC), *flags, f"-Wl,-Map={map_path},--cref,--gc-sections",
            *(str(item) for item in objects), "-o", str(elf_path),
            f"-L{bsp_lib}", "-Wl,-T", f"-Wl,{linker_script}",
            f"-L{src_dir}", f"-L{bsp_lib}", "-L/",
            "-Wl,--start-group,-lxilstandalone,-lxiltimer,-lxil,-lgcc,-lc,-lm",
            "-Wl,--end-group",
        ]
        code, _, _ = persist_command(evidence_dir, "link_s4b_ps_tensor", link_command,
                                     app_build, 180, command_results)
        write_json(evidence_dir / "commands.json", {"commands": command_results})
        if code != 0:
            raise BuildError(f"AArch32 ELF链接失败，exit={code}")

        for name, tool in (("elf_size", SIZE), ("elf_sections", OBJDUMP), ("elf_symbols", NM)):
            command = [str(tool), "--format=berkeley", str(elf_path)] if name == "elf_size" else (
                [str(tool), "-h", str(elf_path)] if name == "elf_sections" else
                [str(tool), "-n", str(elf_path)]
            )
            code, stdout, stderr = persist_command(evidence_dir, name, command,
                                                   app_build, 60, command_results)
            write_json(evidence_dir / "commands.json", {"commands": command_results})
            if code != 0:
                raise BuildError(f"ELF检查工具失败 {name}，exit={code}: {stderr[-500:]}")
        symbols_text = (evidence_dir / "elf_symbols.stdout.txt").read_text(encoding="utf-8")
        sections_text = (evidence_dir / "elf_sections.stdout.txt").read_text(encoding="utf-8")
        ranges = verify_memory_map(symbols_text, sections_text)
        write_json(evidence_dir / "memory_ranges.json", ranges)
        shutil.copyfile(elf_path, evidence_dir / "s4b_ps_tensor_diagnostic.elf")
        shutil.copyfile(map_path, evidence_dir / "s4b_ps_tensor_diagnostic.map")
        (evidence_dir / "derived_source_sha256.json").write_text(
            json.dumps({"frozen_2b_app_sha256": BASE_APP_SHA256,
                        "derived_s4b_ps_app_sha256": derived_sha,
                        "trace_header_sha256": sha256_file(trace_header),
                        "trace_source_sha256": sha256_file(trace_source),
                        "embedded_ps_source_identity_scope": "derived application C source only; final load identity also includes ELF SHA256",
                        "trace_log_abi": "s4b-ps-tensor/1",
                        "embedded_ready_banner":
                            f"S2B-INFERENCE/1 READY SOURCE={derived_sha} XSA={XSA_SHA256} "
                            f"MODEL={MODEL_SHA256} DIAG=s4b-ps-tensor/1 TRACE_ABI=1\\r\\n"},
            ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        external_after = verify_external_inputs_unchanged(external)
        write_json(evidence_dir / "external_inputs_inventory.json", {
            **inventory,
            "external_inputs_before_build": external,
            "external_inputs_after_build": external_after,
            "before_after_sha256_and_byte_count_equal": True,
        })
        result.update({
            "status": "PASS_BUILD_ONLY",
            "exit_code": 0,
            "derived_app_sha256": derived_sha,
            "elf_sha256": sha256_file(elf_path),
            "elf_bytes": elf_path.stat().st_size,
            "map_sha256": sha256_file(map_path),
            "memory_ranges": ranges,
            "elapsed_seconds": round(time.perf_counter() - start_time, 6),
            "bundle_manifest_source_commit": bundle_manifest.get("source_commit"),
            "xsa_sha256": XSA_SHA256,
            "model_manifest_sha256": MODEL_SHA256,
            "bsp_reused": True,
            "platform_rebuilt": False,
            "pl_rebuilt": False,
            "hardware_execution": "NOT_RUN",
            "external_inputs_unchanged_after_build": True,
            "derived_app_ready_identity": "SOURCE是派生app C源码SHA；DIAG与TRACE_ABI标识新增诊断ABI；最终装载身份还绑定ELF SHA。",
        })
        write_json(evidence_dir / "machine_result.json", result)
        write_json(evidence_dir / "commands.json", {"commands": command_results})
        return 0
    except Exception as exc:
        result.update({
            "status": "FAIL",
            "exit_code": 1,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_seconds": round(time.perf_counter() - start_time, 6),
        })
        write_json(evidence_dir / "machine_result.json", result)
        write_json(evidence_dir / "commands.json", {"commands": command_results})
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=RUN_ID_DEFAULT)
    parser.add_argument("--boot-seed", type=parse_u64, required=True)
    parser.add_argument("--session-first", type=parse_u32, required=True)
    parser.add_argument("--session-last", type=parse_u32, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"s4b_ps_tensor_20261023_r[0-9]{2,3}", args.run_id):
        parser.error("run-id需使用新的s4b_ps_tensor_20261023_rNN标识")
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
