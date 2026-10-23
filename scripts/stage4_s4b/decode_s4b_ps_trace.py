#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验并解析双读稳定快照格式的S4B PS旁路日志。"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from pathlib import Path
from typing import Any


DUMP_MAGIC = b"S4BPSDMP"
DUMP_VERSION = 1
DUMP_HEADER = struct.Struct("<8sIIIII")
TRACE_HEADER_BYTES = 144
TRACE_RECORD_BYTES = 184
TRACE_CAPACITY = 1000
TRACE_HEADER_WORDS = 36
TRACE_RECORD_WORDS = 46
TRACE_MAGIC = 0x53345054
RECORD_MAGIC = 0x53345243
SCHEMA_VERSION = 1
INPUT_BYTES = 519168
INPUT_FORMAT_INT8_CHW_416 = 1
UNAVAILABLE_CAPTURE_TIME = 1 << 0
UNAPPROVED_INFERENCE_NS = 1 << 1
EVENT_INPUT_WRITE_START = 1 << 0
EVENT_INPUT_WRITE_DONE = 1 << 1
EVENT_START_COMMAND = 1 << 2
EVENT_TERMINAL_OBSERVED = 1 << 3
EVENT_TERMINAL_SAFE = 1 << 4
EVENT_POSTPROCESS_DONE = 1 << 5
EVENT_LOG_COMMIT = 1 << 6
EVENT_UART_START = 1 << 7
EVENT_UART_DONE = 1 << 8
EVENT_ACK_DONE = 1 << 9
EVENT_KNOWN_MASK = (1 << 10) - 1

# 以下CSR位和终态值来自冻结2B s2b_inference_app.c的status定义。
CSR_STATE_MASK = 0x7
CSR_OWNER_PL = 1 << 8
CSR_HEAD_VALID = 1 << 9
CSR_SAFE_REUSE = 1 << 10
CSR_TERMINAL = 1 << 11
CSR_AXI_PENDING = 1 << 12
CSR_FIRST_PENDING = 1 << 13
CSR_DONE_SAFE = 4
CSR_ERROR_SAFE = 5
CSR_FAULT_ISOLATED = 6
CSR_KNOWN_MASK = (CSR_STATE_MASK | CSR_OWNER_PL | CSR_HEAD_VALID | CSR_SAFE_REUSE |
                  CSR_TERMINAL | CSR_AXI_PENDING | CSR_FIRST_PENDING)
CSR_MAX_STATE = CSR_FAULT_ISOLATED

RESPONSE_OK = 0
RESPONSE_BAD_STATE = 5
RESPONSE_BOARD_ERROR = 7
RESPONSE_OBSERVE_TIMEOUT = 8
RESPONSE_DECODE_ERROR = 9
RESPONSE_RUN_STATUSES = {
    RESPONSE_OK, RESPONSE_BAD_STATE, RESPONSE_BOARD_ERROR,
    RESPONSE_OBSERVE_TIMEOUT, RESPONSE_DECODE_ERROR,
}
DECODE_STATUS_OK = 0
DECODE_ERROR_STATUSES = {
    (-1) & 0xFFFFFFFF,
    (-2) & 0xFFFFFFFF,
    (-3) & 0xFFFFFFFF,
    (-4) & 0xFFFFFFFF,
}
UINT32_MAX = 0xFFFFFFFF
S2A_T62_MAX_OUTPUTS = 15
S2A_T62_MAX_CANDIDATES = 12675
UART_SEND_FAILED = 1
UART_SEND_SUCCEEDED = 2
ACK_NOT_ATTEMPTED = 0
ACK_SUCCEEDED = 1
ACK_FAILED = 2


class TraceDecodeError(ValueError):
    """表示快照不稳定、格式错误或记录损坏。"""


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def _expected_identity(source_sha256: str, boot_seed: int) -> tuple[str, int]:
    if not isinstance(source_sha256, str) or re.fullmatch(r"[0-9a-fA-F]{64}", source_sha256) is None:
        raise TraceDecodeError("expected_source_sha256_invalid")
    if isinstance(boot_seed, bool) or not isinstance(boot_seed, int) or not 0 < boot_seed <= 0xFFFFFFFFFFFFFFFF:
        raise TraceDecodeError("expected_boot_seed_invalid")
    return source_sha256.lower(), boot_seed


def _unpack_header(data: bytes) -> tuple[dict[str, int], tuple[int, ...]]:
    if len(data) != TRACE_HEADER_BYTES:
        raise TraceDecodeError("header_size_mismatch")
    words = struct.unpack("<36I", data)
    if words[0] != TRACE_MAGIC:
        raise TraceDecodeError("header_magic_mismatch")
    if words[1] != SCHEMA_VERSION or words[2] != TRACE_HEADER_BYTES:
        raise TraceDecodeError("header_schema_or_size_mismatch")
    if words[3] != TRACE_RECORD_BYTES or words[4] != TRACE_CAPACITY:
        raise TraceDecodeError("record_layout_mismatch")
    if words[5] > TRACE_CAPACITY:
        raise TraceDecodeError("record_count_out_of_range")
    boot_seed = (words[7] << 32) | words[6]
    if boot_seed == 0:
        raise TraceDecodeError("boot_seed_zero")
    if words[17] != 0:
        raise TraceDecodeError("snapshot_run_active")
    if words[35] != crc32(data[:140]):
        raise TraceDecodeError("header_crc_mismatch")
    if words[25] != 1 or words[26] != 1:
        raise TraceDecodeError("diagnostic_kind_or_timebase_mismatch")
    header = {
        "record_count": words[5],
        "boot_seed": boot_seed,
        "derived_source_sha256": "".join(f"{word:08x}" for word in words[27:35]),
        "session_first": words[8],
        "session_last": words[9],
        "next_session_id": words[10],
        "session_range_exhausted": words[11],
        "rejected_request_count": words[12],
        "log_full_reject_count": words[13],
        "last_rejected_sequence": words[14],
        "last_rejected_frame": words[15],
        "last_rejected_reason": words[16],
        "last_run_status": words[18],
        "active_session_id": words[19],
        "active_uart_sequence": words[20],
        "active_base_frame": words[21],
        "active_repeat_count": words[22],
        "active_next_repeat_index": words[23],
        "last_assigned_session_id": words[24],
        "header_crc32": words[35],
    }
    if header["session_first"] == 0 or header["session_last"] < header["session_first"]:
        raise TraceDecodeError("session_range_invalid")
    if header["session_last"] > 0xFFFFFFFE or header["session_range_exhausted"] not in (0, 1):
        raise TraceDecodeError("session_range_or_exhaustion_invalid")
    if header["session_range_exhausted"] != 0:
        if header["next_session_id"] != 0:
            raise TraceDecodeError("exhausted_session_range_has_next_id")
    elif not header["session_first"] <= header["next_session_id"] <= header["session_last"]:
        raise TraceDecodeError("next_session_id_outside_range")
    if header["last_assigned_session_id"] == 0:
        if header["session_range_exhausted"] != 0 or header["next_session_id"] != header["session_first"]:
            raise TraceDecodeError("unassigned_session_header_inconsistent")
    elif not header["session_first"] <= header["last_assigned_session_id"] <= header["session_last"]:
        raise TraceDecodeError("last_assigned_session_outside_range")
    elif header["session_range_exhausted"] != 0:
        if header["last_assigned_session_id"] != header["session_last"]:
            raise TraceDecodeError("exhausted_session_last_id_mismatch")
    elif header["next_session_id"] != header["last_assigned_session_id"] + 1:
        raise TraceDecodeError("next_session_not_after_last_assigned")
    if header["last_run_status"] not in (0, 1, 2):
        raise TraceDecodeError("last_run_status_invalid")
    return header, words


def _decode_record(data: bytes, index: int) -> dict[str, Any]:
    if len(data) != TRACE_RECORD_BYTES:
        raise TraceDecodeError(f"record_{index}_size_mismatch")
    words = struct.unpack("<46I", data)
    if words[0] != RECORD_MAGIC:
        raise TraceDecodeError(f"record_{index}_magic_mismatch")
    if words[1] != SCHEMA_VERSION or words[2] != TRACE_RECORD_BYTES:
        raise TraceDecodeError(f"record_{index}_schema_or_size_mismatch")
    if words[3] != index:
        raise TraceDecodeError(f"record_{index}_index_mismatch")
    if words[45] != crc32(data[:180]):
        raise TraceDecodeError(f"record_{index}_crc_mismatch")
    if words[10] != INPUT_BYTES or words[11] != INPUT_FORMAT_INT8_CHW_416:
        raise TraceDecodeError(f"record_{index}_input_contract_mismatch")
    if words[12] != 0 or words[13] != 0 or words[14] != (
        UNAVAILABLE_CAPTURE_TIME | UNAPPROVED_INFERENCE_NS
    ):
        raise TraceDecodeError(f"record_{index}_capture_or_time_availability_mismatch")
    input_write_start_seen = (words[44] & EVENT_INPUT_WRITE_START) != 0
    input_write_done_seen = (words[44] & EVENT_INPUT_WRITE_DONE) != 0
    if input_write_start_seen != input_write_done_seen:
        raise TraceDecodeError(f"record_{index}_input_write_event_mismatch")
    if words[44] & ~EVENT_KNOWN_MASK:
        raise TraceDecodeError(f"record_{index}_unknown_event_flags")
    if (words[44] & EVENT_LOG_COMMIT) == 0:
        raise TraceDecodeError(f"record_{index}_not_committed")
    input_copy_events = EVENT_INPUT_WRITE_START | EVENT_INPUT_WRITE_DONE
    if (words[44] & input_copy_events) != input_copy_events:
        raise TraceDecodeError(f"record_{index}_input_copy_events_required")
    if words[37] not in (0, 1):
        raise TraceDecodeError(f"record_{index}_terminal_safe_invalid")
    terminal_observed_seen = (words[44] & EVENT_TERMINAL_OBSERVED) != 0
    terminal_safe_seen = (words[44] & EVENT_TERMINAL_SAFE) != 0
    if bool(words[37]) != terminal_safe_seen:
        raise TraceDecodeError(f"record_{index}_terminal_safe_flag_mismatch")
    if terminal_safe_seen and not terminal_observed_seen:
        raise TraceDecodeError(f"record_{index}_terminal_observation_mismatch")
    state = words[34] & CSR_STATE_MASK
    if words[34] & ~CSR_KNOWN_MASK or state > CSR_MAX_STATE:
        raise TraceDecodeError(f"record_{index}_terminal_status_unknown_bits_or_state")
    if words[41] not in RESPONSE_RUN_STATUSES:
        raise TraceDecodeError(f"record_{index}_response_status_out_of_range")
    if terminal_observed_seen and (words[34] & CSR_TERMINAL) == 0:
        raise TraceDecodeError(f"record_{index}_terminal_observation_status_mismatch")
    if terminal_safe_seen:
        safe_required = CSR_SAFE_REUSE | CSR_TERMINAL
        unsafe_flags = CSR_OWNER_PL | CSR_AXI_PENDING | CSR_FIRST_PENDING
        if (state not in (CSR_DONE_SAFE, CSR_ERROR_SAFE) or
                (words[34] & safe_required) != safe_required or
                (words[34] & unsafe_flags) != 0):
            raise TraceDecodeError(f"record_{index}_terminal_safe_status_invalid")
        if state == CSR_DONE_SAFE and (
                (words[34] & CSR_HEAD_VALID) == 0 or words[35] != 0):
            raise TraceDecodeError(f"record_{index}_done_safe_status_invalid")
        if state == CSR_ERROR_SAFE and (
                (words[34] & CSR_HEAD_VALID) != 0 or words[35] == 0):
            raise TraceDecodeError(f"record_{index}_error_safe_status_invalid")
    uart_start_seen = (words[44] & EVENT_UART_START) != 0
    uart_done_seen = (words[44] & EVENT_UART_DONE) != 0
    if uart_start_seen != uart_done_seen:
        raise TraceDecodeError(f"record_{index}_uart_event_mismatch")
    ack_done_seen = (words[44] & EVENT_ACK_DONE) != 0
    if not uart_done_seen and words[42] != 0:
        raise TraceDecodeError(f"record_{index}_uart_status_without_event")
    if uart_done_seen and words[42] not in (UART_SEND_FAILED, UART_SEND_SUCCEEDED):
        raise TraceDecodeError(f"record_{index}_uart_send_status_invalid")
    if not ack_done_seen and words[43] != ACK_NOT_ATTEMPTED:
        raise TraceDecodeError(f"record_{index}_ack_event_mismatch")
    if ack_done_seen and words[43] not in (ACK_SUCCEEDED, ACK_FAILED):
        raise TraceDecodeError(f"record_{index}_ack_state_invalid")
    if ack_done_seen and (
            not uart_done_seen or words[42] != UART_SEND_SUCCEEDED or
            not terminal_safe_seen or words[33] != words[5] or
            words[41] not in (RESPONSE_OK, RESPONSE_BOARD_ERROR)):
        raise TraceDecodeError(f"record_{index}_ack_without_sent_safe_response")
    if (uart_done_seen and words[42] == UART_SEND_SUCCEEDED and
            words[41] in (RESPONSE_OK, RESPONSE_BOARD_ERROR) and not ack_done_seen):
        raise TraceDecodeError(f"record_{index}_sent_safe_response_missing_ack_attempt")
    if words[41] == RESPONSE_OBSERVE_TIMEOUT and ack_done_seen:
        raise TraceDecodeError(f"record_{index}_timeout_ack_forbidden")

    response_status = words[41]
    event_flags = words[44]
    base_required = input_copy_events | EVENT_LOG_COMMIT
    if (event_flags & base_required) != base_required:
        raise TraceDecodeError(f"record_{index}_base_event_matrix_incomplete")
    terminal_pair = EVENT_TERMINAL_OBSERVED | EVENT_TERMINAL_SAFE
    common_started = EVENT_START_COMMAND | EVENT_UART_START | EVENT_UART_DONE
    postprocess_seen = (event_flags & EVENT_POSTPROCESS_DONE) != 0
    if response_status == RESPONSE_OK:
        required = base_required | common_started | terminal_pair | EVENT_POSTPROCESS_DONE
        if (event_flags & required) != required:
            raise TraceDecodeError(f"record_{index}_response_ok_required_event_missing")
        if not terminal_safe_seen or state != CSR_DONE_SAFE:
            raise TraceDecodeError(f"record_{index}_response_ok_without_done_safe")
        if words[33] != words[5]:
            raise TraceDecodeError(f"record_{index}_response_terminal_frame_mismatch")
        if words[38] != DECODE_STATUS_OK:
            raise TraceDecodeError(f"record_{index}_response_ok_decode_status_invalid")
        if (words[39] > S2A_T62_MAX_OUTPUTS or
                words[40] > S2A_T62_MAX_CANDIDATES or words[39] > words[40]):
            raise TraceDecodeError(f"record_{index}_response_ok_detection_candidate_bounds")
    elif response_status == RESPONSE_BOARD_ERROR:
        required = base_required | common_started | terminal_pair
        if (event_flags & required) != required or postprocess_seen:
            raise TraceDecodeError(f"record_{index}_board_error_event_matrix_invalid")
        if not terminal_safe_seen or state != CSR_ERROR_SAFE:
            raise TraceDecodeError(f"record_{index}_board_error_without_error_safe")
        if words[33] != words[5]:
            raise TraceDecodeError(f"record_{index}_response_terminal_frame_mismatch")
        if words[38] != UINT32_MAX or words[39] != 0 or words[40] != 0:
            raise TraceDecodeError(f"record_{index}_board_error_result_fields_invalid")
    elif response_status == RESPONSE_OBSERVE_TIMEOUT:
        required = base_required | common_started
        if (event_flags & required) != required or postprocess_seen:
            raise TraceDecodeError(f"record_{index}_timeout_event_matrix_invalid")
        if words[38] != UINT32_MAX or words[39] != 0 or words[40] != 0:
            raise TraceDecodeError(f"record_{index}_timeout_result_fields_invalid")
        # 物理终态可安全，但它与请求事务的epoch或frame不匹配时仍是观测超时；
        # expected epoch不在记录中，保留原始epoch/frame，不推导或改写匹配值。
    elif response_status == RESPONSE_DECODE_ERROR:
        required = base_required | common_started | terminal_pair | EVENT_POSTPROCESS_DONE
        if (event_flags & required) != required:
            raise TraceDecodeError(f"record_{index}_decode_error_required_event_missing")
        if not terminal_safe_seen or state != CSR_DONE_SAFE:
            raise TraceDecodeError(f"record_{index}_decode_error_without_done_safe")
        if words[33] != words[5]:
            raise TraceDecodeError(f"record_{index}_response_terminal_frame_mismatch")
        if (words[38] not in DECODE_ERROR_STATUSES or
                words[39] != 0 or words[40] != 0):
            raise TraceDecodeError(f"record_{index}_decode_error_result_fields_invalid")
    elif response_status == RESPONSE_BAD_STATE:
        allowed = base_required
        if event_flags != allowed or postprocess_seen:
            raise TraceDecodeError(f"record_{index}_bad_state_event_matrix_invalid")
        if words[38] != UINT32_MAX or words[39] != 0 or words[40] != 0:
            raise TraceDecodeError(f"record_{index}_bad_state_result_fields_invalid")

    event_ticks = [
        (EVENT_INPUT_WRITE_START, 15, "input_write_start"),
        (EVENT_INPUT_WRITE_DONE, 17, "input_write_done"),
        (EVENT_START_COMMAND, 19, "start_command"),
        (EVENT_TERMINAL_OBSERVED, 21, "terminal_observation"),
        (EVENT_POSTPROCESS_DONE, 23, "postprocess_done"),
        (EVENT_LOG_COMMIT, 25, "log_commit"),
        (EVENT_UART_START, 27, "uart_start"),
        (EVENT_UART_DONE, 29, "uart_done"),
    ]
    observed_ticks: list[tuple[int, str]] = []
    for event_flag, low_word, label in event_ticks:
        ticks = (words[low_word + 1] << 32) | words[low_word]
        if words[44] & event_flag:
            observed_ticks.append((ticks, label))
        elif ticks != 0:
            raise TraceDecodeError(f"record_{index}_{label}_tick_without_event")
    for (previous_ticks, previous_name), (current_ticks, current_name) in zip(
            observed_ticks, observed_ticks[1:]):
        if previous_ticks > current_ticks:
            raise TraceDecodeError(
                f"record_{index}_event_tick_order_invalid_{previous_name}_after_{current_name}")
    if words[4] == 0 or words[6] != words[7] + 1:
        raise TraceDecodeError(f"record_{index}_key_invalid")
    return {
        "record_index": words[3],
        "session_id": words[4],
        "frame_id": words[5],
        "result_seq": words[6],
        "repeat_index": words[7],
        "uart_sequence": words[8],
        "input_crc32": words[9],
        "input_length": words[10],
        "input_format": "INT8_CHW_416",
        "capture_time_available": False,
        "capture_time_ns": 0,
        "unavailable_fields_mask": words[14],
        "input_write_start_ticks": (words[16] << 32) | words[15],
        "input_write_done_ticks": (words[18] << 32) | words[17],
        "start_command_ticks": (words[20] << 32) | words[19],
        "terminal_observation_ticks": (words[22] << 32) | words[21],
        "postprocess_done_ticks": (words[24] << 32) | words[23],
        "log_commit_ticks": (words[26] << 32) | words[25],
        "uart_send_start_ticks": (words[28] << 32) | words[27],
        "uart_send_done_ticks": (words[30] << 32) | words[29],
        "epoch": (words[32] << 32) | words[31],
        "terminal_frame": words[33],
        "terminal_status": words[34],
        "terminal_error": words[35],
        "terminal_reject": words[36],
        "terminal_safe": bool(words[37]),
        "decode_status": words[38],
        "detection_count": words[39],
        "raw_candidate_count": words[40],
        "response_status": words[41],
        "uart_send_status": words[42],
        "ack_state": words[43],
        "event_flags": words[44],
        "record_crc32": words[45],
    }


def decode_bytes(blob: bytes, *, expected_derived_source_sha256: str,
                 expected_boot_seed: int) -> dict[str, Any]:
    """解码两份全量一致的日志区快照；格式为小端字节序。"""
    expected_source, expected_seed = _expected_identity(
        expected_derived_source_sha256, expected_boot_seed)
    if len(blob) < DUMP_HEADER.size:
        raise TraceDecodeError("dump_header_truncated")
    magic, version, header_bytes, record_bytes, capacity, snapshot_bytes = DUMP_HEADER.unpack_from(blob)
    if magic != DUMP_MAGIC or version != DUMP_VERSION:
        raise TraceDecodeError("dump_magic_or_version_mismatch")
    if header_bytes != TRACE_HEADER_BYTES or record_bytes != TRACE_RECORD_BYTES or capacity != TRACE_CAPACITY:
        raise TraceDecodeError("dump_layout_mismatch")
    expected_snapshot_bytes = header_bytes + record_bytes * capacity
    if snapshot_bytes != expected_snapshot_bytes:
        raise TraceDecodeError("dump_snapshot_size_mismatch")
    expected_total = DUMP_HEADER.size + 2 * snapshot_bytes
    if len(blob) != expected_total:
        raise TraceDecodeError("dump_total_size_mismatch")
    first = blob[DUMP_HEADER.size:DUMP_HEADER.size + snapshot_bytes]
    second = blob[DUMP_HEADER.size + snapshot_bytes:]
    if first != second:
        raise TraceDecodeError("snapshot_double_read_mismatch")

    header_data = first[:header_bytes]
    records_data = first[header_bytes:]
    header, _ = _unpack_header(header_data)
    if header["derived_source_sha256"] != expected_source:
        raise TraceDecodeError("derived_source_sha256_mismatch")
    if header["boot_seed"] != expected_seed:
        raise TraceDecodeError("boot_seed_mismatch")
    count = header["record_count"]
    records: list[dict[str, Any]] = []
    result_keys: set[tuple[int, int]] = set()
    join_keys: set[tuple[int, int, int]] = set()
    per_session: dict[int, list[dict[str, Any]]] = {}
    for index in range(count):
        start = index * record_bytes
        record = _decode_record(records_data[start:start + record_bytes], index)
        result_key = (record["session_id"], record["result_seq"])
        join_key = (record["session_id"], record["frame_id"], record["repeat_index"])
        if result_key in result_keys or join_key in join_keys:
            raise TraceDecodeError(f"record_{index}_duplicate_key")
        result_keys.add(result_key)
        join_keys.add(join_key)
        per_session.setdefault(record["session_id"], []).append(record)
        records.append(record)
    trailing = records_data[count * record_bytes:]
    if any(trailing):
        raise TraceDecodeError("uncommitted_record_slot_nonzero")
    last_session = 0
    observed_session_order: list[int] = []
    previous_record_session = 0
    for record in records:
        current_session = record["session_id"]
        if current_session != previous_record_session:
            if current_session <= previous_record_session:
                raise TraceDecodeError("record_session_order_not_monotonic")
            observed_session_order.append(current_session)
            previous_record_session = current_session
    for session_id, session_records in per_session.items():
        if session_id < header["session_first"] or session_id > header["last_assigned_session_id"]:
            raise TraceDecodeError(f"session_{session_id}_outside_assigned_range")
        if session_id <= last_session:
            raise TraceDecodeError("session_order_not_monotonic")
        last_session = session_id
        session_records.sort(key=lambda record: record["record_index"])
        if len({record["uart_sequence"] for record in session_records}) != 1:
            raise TraceDecodeError(f"session_{session_id}_uart_sequence_changed")
        record_indices = [record["record_index"] for record in session_records]
        if record_indices != list(range(record_indices[0], record_indices[0] + len(record_indices))):
            raise TraceDecodeError(f"session_{session_id}_record_indices_not_contiguous")
        immutable_run_fields = {
            (record["uart_sequence"], record["input_crc32"], record["input_length"],
             record["input_format"], record["input_write_start_ticks"],
             record["input_write_done_ticks"],
             bool(record["event_flags"] & EVENT_INPUT_WRITE_START),
             bool(record["event_flags"] & EVENT_INPUT_WRITE_DONE))
            for record in session_records
        }
        if len(immutable_run_fields) != 1:
            raise TraceDecodeError(f"session_{session_id}_run_metadata_changed")
        first_frame = session_records[0]["frame_id"]
        for repeat_index, record in enumerate(session_records):
            if record["repeat_index"] != repeat_index or record["result_seq"] != repeat_index + 1:
                raise TraceDecodeError(f"session_{session_id}_repeat_order_invalid")
            if record["frame_id"] != first_frame + repeat_index:
                raise TraceDecodeError(f"session_{session_id}_frame_order_invalid")
    last_assigned = header["last_assigned_session_id"]
    if header["last_run_status"] == 0:
        if (last_assigned != 0 or count != 0 or header["active_session_id"] != 0 or
                header["active_uart_sequence"] != 0 or header["active_base_frame"] != 0 or
                header["active_repeat_count"] != 0 or header["active_next_repeat_index"] != 0):
            raise TraceDecodeError("no_run_header_state_inconsistent")
    elif last_assigned == 0 or header["active_session_id"] != last_assigned:
        raise TraceDecodeError("last_run_session_header_inconsistent")
    elif header["active_repeat_count"] == 0 or header["active_next_repeat_index"] > header["active_repeat_count"]:
        raise TraceDecodeError("last_run_repeat_header_invalid")
    if last_assigned != 0:
        last_records = per_session.get(last_assigned, [])
        if last_records and any(
                record["uart_sequence"] != header["active_uart_sequence"]
                for record in last_records):
            raise TraceDecodeError("last_run_uart_sequence_header_mismatch")
        if header["active_next_repeat_index"] < len(last_records):
            raise TraceDecodeError("last_run_attempt_count_header_too_small")
        if last_records and last_records[0]["frame_id"] != header["active_base_frame"]:
            raise TraceDecodeError("last_run_base_frame_header_mismatch")
        if header["last_run_status"] == 1 and (
                len(last_records) != header["active_repeat_count"] or
                header["active_next_repeat_index"] != header["active_repeat_count"]):
            raise TraceDecodeError("completed_run_record_count_mismatch")
        if header["last_run_status"] == 2 and len(last_records) > header["active_repeat_count"]:
            raise TraceDecodeError("partial_run_record_count_exceeds_repeat_count")

    def attempt_succeeded(record: dict[str, Any]) -> bool:
        return (
            record["response_status"] == RESPONSE_OK and
            record["uart_send_status"] == UART_SEND_SUCCEEDED and
            (record["event_flags"] & EVENT_ACK_DONE) != 0 and
            record["ack_state"] == ACK_SUCCEEDED
        )

    # 派生app中infer_one失败会使service_request返回0，主服务循环随即停止；
    # 因此失败attempt只能是日志最后一条，且必须属于最后分配的session。
    failed_records = [record for record in records if not attempt_succeeded(record)]
    if header["last_run_status"] == 1 and failed_records:
        raise TraceDecodeError("completed_run_contains_failed_attempt")
    if failed_records and (
            len(failed_records) != 1 or failed_records[0] is not records[-1] or
            failed_records[0]["session_id"] != last_assigned):
        raise TraceDecodeError("failed_attempt_not_terminal")
    return {
        "schema_version": 1,
        "status": "PASS_DECODED_DOUBLE_READ_SNAPSHOT",
        "snapshot_stability": "two_full_region_reads_byte_identical",
        "header": header,
        "record_count": count,
        "records": records,
        "last_run_incomplete": header["last_run_status"] == 2,
        "uart_frame_count_is_not_inference_record_count": True,
        "notes": [
            "日志只记录成功进入推理路径的各个结果尝试；UART重量装载响应和其他控制响应不计作推理记录。",
            "PL完成字段是PS首次观察到安全终态的global timer原始ticks，不表示PL精确完成周期。",
            "terminal_safe只表示记录中的物理CSR快照满足DONE_SAFE或ERROR_SAFE条件；OBSERVE_TIMEOUT仍可保留此值，因为请求epoch/frame匹配失败时不会把物理safe改写成非safe。",
            "input_write_*只测CPU从staging复制到arena的代码区间，不表示flush完成或DDR/PL已可见。",
            "本格式不把raw ticks换算为ns；capture_time不可用且为0。",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path, help="完整双读快照文件")
    parser.add_argument("--expected-source-sha256", required=True,
                        help="本次构建清单中受信的派生应用C源码SHA-256")
    parser.add_argument("--expected-boot-seed", required=True, type=lambda value: int(value, 0),
                        help="本次构建配置中的非零u64 boot seed")
    parser.add_argument("--output", type=Path, help="JSON输出路径；默认写标准输出")
    args = parser.parse_args()
    try:
        result = decode_bytes(args.dump.read_bytes(),
                              expected_derived_source_sha256=args.expected_source_sha256,
                              expected_boot_seed=args.expected_boot_seed)
    except (OSError, TraceDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
