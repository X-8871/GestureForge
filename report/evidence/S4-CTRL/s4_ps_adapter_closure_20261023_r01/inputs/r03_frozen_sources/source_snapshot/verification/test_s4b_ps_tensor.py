#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证PS旁路日志快照解码和冻结应用派生绑定。"""

from __future__ import annotations

import hashlib
import os
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from scripts.stage4_s4b import build_s4b_ps_tensor as builder
from scripts.stage4_s4b import decode_s4b_ps_trace as decoder


TEST_SOURCE_SHA256 = hashlib.sha256(b"explicit test derived PS source").hexdigest()
TEST_BOOT_SEED = 0x0000000120261023


def decode_dump(blob: bytes, *, expected_source: str = TEST_SOURCE_SHA256,
                expected_seed: int = TEST_BOOT_SEED) -> dict[str, object]:
    return decoder.decode_bytes(
        blob, expected_derived_source_sha256=expected_source,
        expected_boot_seed=expected_seed,
    )


def make_header(record_count: int, *, last_run_status: int = 1,
                repeat_count: int | None = None,
                next_repeat_index: int | None = None) -> bytes:
    words = [0] * decoder.TRACE_HEADER_WORDS
    words[0] = decoder.TRACE_MAGIC
    words[1] = decoder.SCHEMA_VERSION
    words[2] = decoder.TRACE_HEADER_BYTES
    words[3] = decoder.TRACE_RECORD_BYTES
    words[4] = decoder.TRACE_CAPACITY
    words[5] = record_count
    words[6] = TEST_BOOT_SEED & 0xFFFFFFFF
    words[7] = TEST_BOOT_SEED >> 32
    words[8] = 1
    words[9] = 100
    words[10] = 2
    words[11] = 0
    words[17] = 0
    words[18] = last_run_status
    if last_run_status == 0:
        words[10] = 1
    else:
        words[19] = 1
        words[20] = 15
        words[21] = 10
        words[22] = record_count if repeat_count is None else repeat_count
        words[23] = record_count if next_repeat_index is None else next_repeat_index
        words[24] = 1
    words[25] = 1
    words[26] = 1
    for index in range(8):
        words[27 + index] = int(TEST_SOURCE_SHA256[index * 8:index * 8 + 8], 16)
    words[35] = zlib.crc32(struct.pack("<35I", *words[:35])) & 0xFFFFFFFF
    return struct.pack("<36I", *words)


def make_record(index: int) -> bytes:
    words = [0] * decoder.TRACE_RECORD_WORDS
    words[0] = decoder.RECORD_MAGIC
    words[1] = decoder.SCHEMA_VERSION
    words[2] = decoder.TRACE_RECORD_BYTES
    words[3] = index
    words[4] = 1
    words[5] = 10 + index
    words[6] = index + 1
    words[7] = index
    words[8] = 15
    words[9] = 0x12345678
    words[10] = decoder.INPUT_BYTES
    words[11] = decoder.INPUT_FORMAT_INT8_CHW_416
    words[12] = 0
    words[13] = 0
    words[14] = decoder.UNAVAILABLE_CAPTURE_TIME | decoder.UNAPPROVED_INFERENCE_NS
    words[15] = 101
    words[17] = 111
    words[19] = 120 + index
    words[21] = 130 + index
    words[23] = 140 + index
    words[25] = 150 + index
    words[27] = 160 + index
    words[29] = 170 + index
    words[31] = 180 + index
    words[33] = 10 + index
    words[34] = (decoder.CSR_DONE_SAFE | decoder.CSR_HEAD_VALID |
                 decoder.CSR_SAFE_REUSE | decoder.CSR_TERMINAL)
    words[37] = 1
    words[38] = 0
    words[39] = 3
    words[40] = 7
    words[41] = 0
    words[42] = 2
    words[43] = 1
    words[44] = (
        decoder.EVENT_INPUT_WRITE_START
        | decoder.EVENT_INPUT_WRITE_DONE
        | decoder.EVENT_START_COMMAND
        | decoder.EVENT_TERMINAL_OBSERVED
        | decoder.EVENT_TERMINAL_SAFE
        | decoder.EVENT_POSTPROCESS_DONE
        | decoder.EVENT_LOG_COMMIT
        | decoder.EVENT_UART_START
        | decoder.EVENT_UART_DONE
        | decoder.EVENT_ACK_DONE
    )
    words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
    return struct.pack("<46I", *words)


def make_dump(record_count: int = 2, *, last_run_status: int = 1,
              repeat_count: int | None = None,
              next_repeat_index: int | None = None) -> bytes:
    records = b"".join(make_record(index) for index in range(record_count))
    records += bytes(decoder.TRACE_RECORD_BYTES * (decoder.TRACE_CAPACITY - record_count))
    snapshot = make_header(record_count, last_run_status=last_run_status,
                           repeat_count=repeat_count,
                           next_repeat_index=next_repeat_index) + records
    header = decoder.DUMP_HEADER.pack(
        decoder.DUMP_MAGIC,
        decoder.DUMP_VERSION,
        decoder.TRACE_HEADER_BYTES,
        decoder.TRACE_RECORD_BYTES,
        decoder.TRACE_CAPACITY,
        len(snapshot),
    )
    return header + snapshot + snapshot


def mutate_snapshot(blob: bytes, offset: int, value: int) -> bytes:
    result = bytearray(blob)
    snapshot_start = decoder.DUMP_HEADER.size
    result[snapshot_start + offset] = value
    result[snapshot_start + decoder.DUMP_HEADER.unpack_from(blob)[5] + offset] = value
    return bytes(result)


def repair_header_crc(blob: bytes) -> bytes:
    result = bytearray(blob)
    snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
    for snapshot_index in range(2):
        start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size
        header = bytearray(result[start:start + decoder.TRACE_HEADER_BYTES])
        words = list(struct.unpack("<36I", header))
        words[35] = zlib.crc32(header[:140]) & 0xFFFFFFFF
        result[start:start + decoder.TRACE_HEADER_BYTES] = struct.pack("<36I", *words)
    return bytes(result)


def repair_record_crc(blob: bytes, record_index: int) -> bytes:
    result = bytearray(blob)
    snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
    record_offset = decoder.TRACE_HEADER_BYTES + record_index * decoder.TRACE_RECORD_BYTES
    for snapshot_index in range(2):
        start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size + record_offset
        words = list(struct.unpack_from("<46I", result, start))
        words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
        result[start:start + decoder.TRACE_RECORD_BYTES] = struct.pack("<46I", *words)
    return bytes(result)


def mutate_record_words(blob: bytes, record_index: int,
                        changes: dict[int, int]) -> bytes:
    result = bytearray(blob)
    snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
    record_offset = decoder.TRACE_HEADER_BYTES + record_index * decoder.TRACE_RECORD_BYTES
    for snapshot_index in range(2):
        start = (decoder.DUMP_HEADER.size + snapshot_index * snapshot_size +
                 record_offset)
        words = list(struct.unpack_from("<46I", result, start))
        for word_index, value in changes.items():
            words[word_index] = value
        words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
        result[start:start + decoder.TRACE_RECORD_BYTES] = struct.pack("<46I", *words)
    return bytes(result)


class TraceDumpTests(unittest.TestCase):
    def test_decoder_accepts_initialized_empty_trace(self) -> None:
        records = bytes(decoder.TRACE_RECORD_BYTES * decoder.TRACE_CAPACITY)
        snapshot = make_header(0, last_run_status=0) + records
        header = decoder.DUMP_HEADER.pack(
            decoder.DUMP_MAGIC, decoder.DUMP_VERSION, decoder.TRACE_HEADER_BYTES,
            decoder.TRACE_RECORD_BYTES, decoder.TRACE_CAPACITY, len(snapshot),
        )
        result = decode_dump(header + snapshot + snapshot)
        self.assertEqual(result["record_count"], 0)
        self.assertFalse(result["last_run_incomplete"])

    def test_double_read_snapshot_decodes_with_separate_keys_and_times(self) -> None:
        result = decode_dump(make_dump())
        self.assertEqual(result["status"], "PASS_DECODED_DOUBLE_READ_SNAPSHOT")
        self.assertEqual(result["snapshot_stability"], "two_full_region_reads_byte_identical")
        self.assertEqual(result["record_count"], 2)
        self.assertEqual((result["records"][0]["session_id"], result["records"][0]["result_seq"]), (1, 1))
        self.assertEqual((result["records"][0]["session_id"], result["records"][0]["frame_id"],
                          result["records"][0]["repeat_index"]), (1, 10, 0))
        self.assertEqual(result["records"][0]["terminal_observation_ticks"], 130)
        self.assertEqual(result["records"][0]["capture_time_ns"], 0)
        self.assertTrue(result["uart_frame_count_is_not_inference_record_count"])

    def test_rejects_different_second_read(self) -> None:
        blob = bytearray(make_dump())
        blob[-1] = 1
        with self.assertRaisesRegex(decoder.TraceDecodeError, "snapshot_double_read_mismatch"):
            decode_dump(bytes(blob))

    def test_rejects_header_crc_damage(self) -> None:
        blob = mutate_snapshot(make_dump(), 6 * 4, 0x55)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "header_crc_mismatch"):
            decode_dump(blob)

    def test_rejects_active_run_snapshot(self) -> None:
        blob = mutate_snapshot(make_dump(), 17 * 4, 1)
        blob = repair_header_crc(blob)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "snapshot_run_active"):
            decode_dump(blob)

    def test_rejects_record_crc_damage(self) -> None:
        blob = mutate_snapshot(make_dump(), decoder.TRACE_HEADER_BYTES + 9 * 4, 0xFE)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "record_0_crc_mismatch"):
            decode_dump(blob)

    def test_rejects_uncommitted_record_even_with_valid_crc(self) -> None:
        blob = bytearray(make_dump())
        snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
        record_offset = decoder.TRACE_HEADER_BYTES
        for snapshot_index in range(2):
            start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size + record_offset
            words = list(struct.unpack_from("<46I", blob, start))
            words[44] &= ~decoder.EVENT_LOG_COMMIT
            words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
            blob[start:start + decoder.TRACE_RECORD_BYTES] = struct.pack("<46I", *words)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "record_0_not_committed"):
            decode_dump(bytes(blob))

    def test_rejects_capture_time_claim(self) -> None:
        blob = bytearray(make_dump())
        snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
        record_offset = decoder.TRACE_HEADER_BYTES
        for snapshot_index in range(2):
            start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size + record_offset
            words = list(struct.unpack_from("<46I", blob, start))
            words[12] = 1
            words[13] = 123
            words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
            blob[start:start + decoder.TRACE_RECORD_BYTES] = struct.pack("<46I", *words)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "record_0_capture_or_time_availability_mismatch"):
            decode_dump(bytes(blob))

    def test_rejects_nonzero_uncommitted_slot(self) -> None:
        blob = bytearray(make_dump())
        snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
        offset = decoder.TRACE_HEADER_BYTES + 2 * decoder.TRACE_RECORD_BYTES + 7
        for snapshot_index in range(2):
            start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size + offset
            blob[start] = 0xA5
        with self.assertRaisesRegex(decoder.TraceDecodeError, "uncommitted_record_slot_nonzero"):
            decode_dump(bytes(blob))

    def test_rejects_duplicate_ps_and_s4a_join_keys(self) -> None:
        blob = bytearray(make_dump())
        snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
        second_offset = decoder.TRACE_HEADER_BYTES + decoder.TRACE_RECORD_BYTES
        for snapshot_index in range(2):
            start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size + second_offset
            words = list(struct.unpack_from("<46I", blob, start))
            words[5] = 10
            words[6] = 1
            words[7] = 0
            words[33] = 10
            words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
            blob[start:start + decoder.TRACE_RECORD_BYTES] = struct.pack("<46I", *words)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "record_1_duplicate_key"):
            decode_dump(bytes(blob))

    def test_decoder_accepts_path_matrix_success_error_timeout_and_bad_state(self) -> None:
        error_status = (decoder.CSR_ERROR_SAFE | decoder.CSR_SAFE_REUSE |
                        decoder.CSR_TERMINAL)
        error_blob = mutate_record_words(make_dump(1, last_run_status=2), 0, {
            23: 0, 24: 0,
            34: error_status,
            35: 3,
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_BOARD_ERROR,
            44: (decoder.EVENT_INPUT_WRITE_START |
                 decoder.EVENT_INPUT_WRITE_DONE |
                 decoder.EVENT_START_COMMAND |
                 decoder.EVENT_TERMINAL_OBSERVED |
                 decoder.EVENT_TERMINAL_SAFE |
                 decoder.EVENT_LOG_COMMIT |
                 decoder.EVENT_UART_START |
                 decoder.EVENT_UART_DONE |
                 decoder.EVENT_ACK_DONE),
        })
        error_result = decode_dump(error_blob)
        self.assertEqual(error_result["records"][0]["ack_state"], decoder.ACK_SUCCEEDED)
        self.assertEqual(error_result["records"][0]["response_status"], decoder.RESPONSE_BOARD_ERROR)

        error_send_failed = mutate_record_words(error_blob, 0, {
            42: decoder.UART_SEND_FAILED,
            43: decoder.ACK_NOT_ATTEMPTED,
            44: struct.unpack("<46I", make_record(0))[44] &
                ~decoder.EVENT_POSTPROCESS_DONE &
                ~decoder.EVENT_ACK_DONE,
        })
        failed_error_result = decode_dump(error_send_failed)["records"][0]
        self.assertEqual(failed_error_result["uart_send_status"], decoder.UART_SEND_FAILED)
        self.assertEqual(failed_error_result["ack_state"], decoder.ACK_NOT_ATTEMPTED)

        decode_error = mutate_record_words(make_dump(1, last_run_status=2), 0, {
            38: (-2) & 0xFFFFFFFF,
            39: 0, 40: 0,
            41: decoder.RESPONSE_DECODE_ERROR,
            43: decoder.ACK_NOT_ATTEMPTED,
            44: (decoder.EVENT_INPUT_WRITE_START |
                 decoder.EVENT_INPUT_WRITE_DONE |
                 decoder.EVENT_START_COMMAND |
                 decoder.EVENT_TERMINAL_OBSERVED |
                 decoder.EVENT_TERMINAL_SAFE |
                 decoder.EVENT_POSTPROCESS_DONE |
                 decoder.EVENT_LOG_COMMIT |
                 decoder.EVENT_UART_START |
                 decoder.EVENT_UART_DONE),
        })
        decode_error_result = decode_dump(decode_error)["records"][0]
        self.assertEqual(decode_error_result["decode_status"], (-2) & 0xFFFFFFFF)
        self.assertEqual(decode_error_result["ack_state"], decoder.ACK_NOT_ATTEMPTED)

        timeout_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_START_COMMAND |
                         decoder.EVENT_LOG_COMMIT |
                         decoder.EVENT_UART_START |
                         decoder.EVENT_UART_DONE)
        timeout_blob = mutate_record_words(
            make_dump(1, last_run_status=2, repeat_count=2, next_repeat_index=1), 0,
            {21: 0, 22: 0, 23: 0, 24: 0, 34: 0, 37: 0,
             38: decoder.UINT32_MAX, 39: 0, 40: 0,
             41: decoder.RESPONSE_OBSERVE_TIMEOUT,
             43: decoder.ACK_NOT_ATTEMPTED, 44: timeout_flags},
        )
        timeout_result = decode_dump(timeout_blob)
        self.assertTrue(timeout_result["last_run_incomplete"])
        self.assertEqual(timeout_result["record_count"], 1)
        self.assertEqual(timeout_result["records"][0]["ack_state"], decoder.ACK_NOT_ATTEMPTED)

        control_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_LOG_COMMIT)
        bad_state_blob = mutate_record_words(make_dump(1, last_run_status=2), 0, {
            19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
            27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_BAD_STATE, 42: 0,
            43: decoder.ACK_NOT_ATTEMPTED, 44: control_flags,
        })
        bad_state_result = decode_dump(bad_state_blob)["records"][0]
        self.assertEqual(bad_state_result["response_status"], decoder.RESPONSE_BAD_STATE)
        self.assertEqual(bad_state_result["event_flags"], control_flags)

    def test_decoder_accepts_physical_safe_timeout_without_transaction_match(self) -> None:
        safe_done = (decoder.CSR_DONE_SAFE | decoder.CSR_HEAD_VALID |
                     decoder.CSR_SAFE_REUSE | decoder.CSR_TERMINAL)
        timeout_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_START_COMMAND |
                         decoder.EVENT_TERMINAL_OBSERVED |
                         decoder.EVENT_TERMINAL_SAFE |
                         decoder.EVENT_LOG_COMMIT |
                         decoder.EVENT_UART_START |
                         decoder.EVENT_UART_DONE)
        wrong_frame = mutate_record_words(
            make_dump(1, last_run_status=2, repeat_count=2, next_repeat_index=1), 0,
            {23: 0, 24: 0, 33: 999, 34: safe_done, 37: 1,
             38: decoder.UINT32_MAX, 39: 0, 40: 0,
             41: decoder.RESPONSE_OBSERVE_TIMEOUT,
             43: decoder.ACK_NOT_ATTEMPTED, 44: timeout_flags},
        )
        wrong_frame_result = decode_dump(wrong_frame)["records"][0]
        self.assertTrue(wrong_frame_result["terminal_safe"])
        self.assertEqual(wrong_frame_result["terminal_frame"], 999)
        self.assertEqual(wrong_frame_result["ack_state"], decoder.ACK_NOT_ATTEMPTED)
        self.assertEqual(wrong_frame_result["response_status"], decoder.RESPONSE_OBSERVE_TIMEOUT)

        raw_epoch = 0x12345678ABCDEF01
        same_frame_epoch_timeout = mutate_record_words(
            make_dump(1, last_run_status=2, repeat_count=2, next_repeat_index=1), 0,
            {23: 0, 24: 0, 31: raw_epoch & 0xFFFFFFFF,
             32: raw_epoch >> 32, 34: safe_done, 37: 1,
             38: decoder.UINT32_MAX, 39: 0, 40: 0,
             41: decoder.RESPONSE_OBSERVE_TIMEOUT,
             43: decoder.ACK_NOT_ATTEMPTED, 44: timeout_flags},
        )
        same_frame_result = decode_dump(same_frame_epoch_timeout)["records"][0]
        self.assertEqual(same_frame_result["terminal_frame"], same_frame_result["frame_id"])
        self.assertEqual(same_frame_result["epoch"], raw_epoch)
        self.assertTrue(same_frame_result["terminal_safe"])
        self.assertEqual(same_frame_result["ack_state"], decoder.ACK_NOT_ATTEMPTED)

    def test_decoder_accepts_uart_failure_and_ack_failure_attempts(self) -> None:
        default_flags = struct.unpack("<46I", make_record(0))[44]
        failed_send = mutate_record_words(make_dump(1, last_run_status=2), 0, {
            42: decoder.UART_SEND_FAILED,
            43: decoder.ACK_NOT_ATTEMPTED,
            44: default_flags & ~decoder.EVENT_ACK_DONE,
        })
        failed_result = decode_dump(failed_send)["records"][0]
        self.assertEqual(failed_result["uart_send_status"], decoder.UART_SEND_FAILED)
        self.assertEqual(failed_result["ack_state"], decoder.ACK_NOT_ATTEMPTED)

        failed_ack = mutate_record_words(
            make_dump(1, last_run_status=2), 0, {43: decoder.ACK_FAILED})
        failed_ack_result = decode_dump(failed_ack)["records"][0]
        self.assertEqual(failed_ack_result["uart_send_status"], decoder.UART_SEND_SUCCEEDED)
        self.assertEqual(failed_ack_result["ack_state"], decoder.ACK_FAILED)

    def test_decoder_accepts_committed_control_without_uart(self) -> None:
        control_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_LOG_COMMIT)
        blob = mutate_record_words(make_dump(1, last_run_status=2), 0, {
            19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
            27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_BAD_STATE, 42: 0,
            43: decoder.ACK_NOT_ATTEMPTED, 44: control_flags,
        })
        result = decode_dump(blob)
        self.assertEqual(result["record_count"], 1)
        self.assertEqual(result["records"][0]["uart_send_status"], 0)

    def test_decoder_requires_success_for_completed_runs_and_keeps_partial_failures(self) -> None:
        base = make_dump(1, last_run_status=2)
        default_flags = struct.unpack("<46I", make_record(0))[44]
        error_safe = (decoder.CSR_ERROR_SAFE | decoder.CSR_SAFE_REUSE |
                      decoder.CSR_TERMINAL)
        safe_done = (decoder.CSR_DONE_SAFE | decoder.CSR_HEAD_VALID |
                     decoder.CSR_SAFE_REUSE | decoder.CSR_TERMINAL)
        cases = {
            "bad_state_without_uart": {
                19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
                27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
                38: decoder.UINT32_MAX, 39: 0, 40: 0,
                41: decoder.RESPONSE_BAD_STATE, 42: 0,
                43: decoder.ACK_NOT_ATTEMPTED,
                44: (decoder.EVENT_INPUT_WRITE_START |
                     decoder.EVENT_INPUT_WRITE_DONE | decoder.EVENT_LOG_COMMIT),
            },
            "safe_but_wrong_frame_timeout": {
                23: 0, 24: 0, 33: 999, 34: safe_done, 37: 1,
                38: decoder.UINT32_MAX, 39: 0, 40: 0,
                41: decoder.RESPONSE_OBSERVE_TIMEOUT,
                43: decoder.ACK_NOT_ATTEMPTED,
                44: (decoder.EVENT_INPUT_WRITE_START |
                     decoder.EVENT_INPUT_WRITE_DONE | decoder.EVENT_START_COMMAND |
                     decoder.EVENT_TERMINAL_OBSERVED | decoder.EVENT_TERMINAL_SAFE |
                     decoder.EVENT_LOG_COMMIT | decoder.EVENT_UART_START |
                     decoder.EVENT_UART_DONE),
            },
            "board_error_with_ack": {
                23: 0, 24: 0, 34: error_safe, 35: 3,
                38: decoder.UINT32_MAX, 39: 0, 40: 0,
                41: decoder.RESPONSE_BOARD_ERROR,
                44: (default_flags & ~decoder.EVENT_POSTPROCESS_DONE),
            },
            "decode_error": {
                38: (-2) & 0xFFFFFFFF, 39: 0, 40: 0,
                41: decoder.RESPONSE_DECODE_ERROR,
                43: decoder.ACK_NOT_ATTEMPTED,
                44: default_flags & ~decoder.EVENT_ACK_DONE,
            },
            "response_uart_failure": {
                42: decoder.UART_SEND_FAILED,
                43: decoder.ACK_NOT_ATTEMPTED,
                44: default_flags & ~decoder.EVENT_ACK_DONE,
            },
            "response_ack_failure": {43: decoder.ACK_FAILED},
        }
        for name, changes in cases.items():
            with self.subTest(case=name):
                partial = mutate_record_words(base, 0, changes)
                partial_result = decode_dump(partial)
                self.assertTrue(partial_result["last_run_incomplete"])
                self.assertEqual(partial_result["record_count"], 1)
                completed = mutate_header_word(partial, 18, 1)
                with self.assertRaisesRegex(
                        decoder.TraceDecodeError,
                        "completed_run_contains_failed_attempt"):
                    decode_dump(completed)

    def test_decoder_rejects_failed_attempt_followed_by_more_records(self) -> None:
        control_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_LOG_COMMIT)
        failure_first = mutate_record_words(
            make_dump(2, last_run_status=2), 0, {
                19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
                27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
                38: decoder.UINT32_MAX, 39: 0, 40: 0,
                41: decoder.RESPONSE_BAD_STATE, 42: 0,
                43: decoder.ACK_NOT_ATTEMPTED, 44: control_flags,
            })
        with self.assertRaisesRegex(decoder.TraceDecodeError,
                                    "failed_attempt_not_terminal"):
            decode_dump(failure_first)

    def test_decoder_rejects_failed_nonlast_session_with_later_session_records(self) -> None:
        control_flags = (decoder.EVENT_INPUT_WRITE_START |
                         decoder.EVENT_INPUT_WRITE_DONE |
                         decoder.EVENT_LOG_COMMIT)
        failure_words = list(struct.unpack("<46I", make_record(0)))
        failure_words[19:25] = [0] * 6
        failure_words[27:31] = [0] * 4
        failure_words[37] = 0
        failure_words[38] = decoder.UINT32_MAX
        failure_words[39] = 0
        failure_words[40] = 0
        failure_words[41] = decoder.RESPONSE_BAD_STATE
        failure_words[42] = 0
        failure_words[43] = decoder.ACK_NOT_ATTEMPTED
        failure_words[44] = control_flags
        failure_words[45] = zlib.crc32(
            struct.pack("<45I", *failure_words[:45])) & 0xFFFFFFFF

        later_words = list(struct.unpack("<46I", make_record(0)))
        later_words[3] = 1
        later_words[4] = 2
        later_words[5] = 20
        later_words[8] = 16
        later_words[33] = 20
        later_words[45] = zlib.crc32(
            struct.pack("<45I", *later_words[:45])) & 0xFFFFFFFF

        header_words = list(struct.unpack(
            "<36I", make_header(2, repeat_count=1, next_repeat_index=1)))
        header_words[10] = 3
        header_words[19] = 2
        header_words[20] = 16
        header_words[21] = 20
        header_words[22] = 1
        header_words[23] = 1
        header_words[24] = 2
        header_words[35] = zlib.crc32(
            struct.pack("<35I", *header_words[:35])) & 0xFFFFFFFF
        snapshot = (
            struct.pack("<36I", *header_words) +
            struct.pack("<46I", *failure_words) +
            struct.pack("<46I", *later_words) +
            bytes(decoder.TRACE_RECORD_BYTES * (decoder.TRACE_CAPACITY - 2))
        )
        dump_header = decoder.DUMP_HEADER.pack(
            decoder.DUMP_MAGIC, decoder.DUMP_VERSION, decoder.TRACE_HEADER_BYTES,
            decoder.TRACE_RECORD_BYTES, decoder.TRACE_CAPACITY, len(snapshot),
        )
        stable_dump = dump_header + snapshot + snapshot
        partial = mutate_header_word(stable_dump, 18, 2)
        with self.assertRaisesRegex(decoder.TraceDecodeError,
                                    "failed_attempt_not_terminal"):
            decode_dump(partial)

    def test_decoder_accepts_successful_multi_repeat_completed_run(self) -> None:
        result = decode_dump(make_dump(3, last_run_status=1,
                                       repeat_count=3, next_repeat_index=3))
        self.assertFalse(result["last_run_incomplete"])
        self.assertEqual(result["record_count"], 3)
        for record in result["records"]:
            self.assertEqual(record["response_status"], decoder.RESPONSE_OK)
            self.assertEqual(record["uart_send_status"], decoder.UART_SEND_SUCCEEDED)
            self.assertEqual(record["ack_state"], decoder.ACK_SUCCEEDED)
            self.assertTrue(record["event_flags"] & decoder.EVENT_ACK_DONE)

    def test_decoder_rejects_crc_repaired_semantic_contradictions(self) -> None:
        cases = (
            ("terminal_fault_claimed_safe", {34: decoder.CSR_FAULT_ISOLATED |
                                              decoder.CSR_SAFE_REUSE | decoder.CSR_TERMINAL}),
            ("terminal_safe_wrong_frame", {33: 999}),
            ("ack_after_uart_failure", {42: decoder.UART_SEND_FAILED}),
            ("input_ticks_reverse", {15: 1000, 16: 0}),
            ("unknown_response_status", {41: 11}),
            ("unknown_terminal_status_bit", {34: decoder.CSR_DONE_SAFE | (1 << 7)}),
        )
        for name, changes in cases:
            with self.subTest(case=name):
                with self.assertRaises(decoder.TraceDecodeError):
                    decode_dump(mutate_record_words(
                        make_dump(last_run_status=2), 0, changes))

    def test_decoder_rejects_crc_repaired_response_matrix_mutations(self) -> None:
        default_flags = struct.unpack("<46I", make_record(0))[44]
        cases = (
            ("missing_start_command", {
                19: 0, 20: 0,
                44: default_flags & ~decoder.EVENT_START_COMMAND,
            }, "response_ok_required_event_missing"),
            ("missing_postprocess", {
                23: 0, 24: 0,
                44: default_flags & ~decoder.EVENT_POSTPROCESS_DONE,
            }, "response_ok_required_event_missing"),
            ("decode_status_99", {38: 99}, "response_ok_decode_status_invalid"),
            ("detection_count_16", {39: 16}, "response_ok_detection_candidate_bounds"),
            ("candidate_count_12676", {40: 12676}, "response_ok_detection_candidate_bounds"),
            ("detection_count_exceeds_candidates", {39: 8, 40: 7},
             "response_ok_detection_candidate_bounds"),
        )
        for name, changes, expected_error in cases:
            with self.subTest(case=name):
                with self.assertRaisesRegex(decoder.TraceDecodeError, expected_error):
                    decode_dump(mutate_record_words(
                        make_dump(1, last_run_status=2), 0, changes))

        timeout_postprocess_flags = (default_flags &
                                     ~decoder.EVENT_ACK_DONE)
        timeout_with_postprocess = mutate_record_words(
            make_dump(1, last_run_status=2), 0, {
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_OBSERVE_TIMEOUT,
            43: decoder.ACK_NOT_ATTEMPTED,
            44: timeout_postprocess_flags,
        })
        with self.assertRaisesRegex(decoder.TraceDecodeError, "timeout_event_matrix_invalid"):
            decode_dump(timeout_with_postprocess)

        error_safe = (decoder.CSR_ERROR_SAFE | decoder.CSR_SAFE_REUSE |
                      decoder.CSR_TERMINAL)
        board_with_postprocess = mutate_record_words(
            make_dump(1, last_run_status=2), 0, {
            34: error_safe, 35: 3,
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_BOARD_ERROR,
            42: decoder.UART_SEND_FAILED,
            44: (default_flags & ~decoder.EVENT_ACK_DONE) |
                decoder.EVENT_TERMINAL_OBSERVED | decoder.EVENT_TERMINAL_SAFE,
            43: decoder.ACK_NOT_ATTEMPTED,
        })
        with self.assertRaisesRegex(decoder.TraceDecodeError, "board_error_event_matrix_invalid"):
            decode_dump(board_with_postprocess)

        bad_state_with_start = mutate_record_words(
            make_dump(1, last_run_status=2), 0, {
            19: 120, 20: 0,
            21: 0, 22: 0,
            23: 0, 24: 0,
            27: 0, 28: 0, 29: 0, 30: 0,
            37: 0,
            38: decoder.UINT32_MAX, 39: 0, 40: 0,
            41: decoder.RESPONSE_BAD_STATE,
            42: 0, 43: decoder.ACK_NOT_ATTEMPTED,
            44: (decoder.EVENT_INPUT_WRITE_START |
                 decoder.EVENT_INPUT_WRITE_DONE |
                 decoder.EVENT_START_COMMAND |
                 decoder.EVENT_LOG_COMMIT),
        })
        with self.assertRaisesRegex(decoder.TraceDecodeError, "bad_state_event_matrix_invalid"):
            decode_dump(bad_state_with_start)

    def test_decoder_rejects_changed_uart_sequence_and_run_metadata(self) -> None:
        changed_sequence = mutate_record_words(make_dump(), 1, {8: 77})
        with self.assertRaisesRegex(decoder.TraceDecodeError, "uart_sequence_changed"):
            decode_dump(changed_sequence)
        changed_crc = mutate_record_words(make_dump(), 1, {9: 0xAAAAAAAA})
        with self.assertRaisesRegex(decoder.TraceDecodeError, "run_metadata_changed"):
            decode_dump(changed_crc)

    def test_decoder_rejects_session_and_last_run_header_mismatch(self) -> None:
        changed = bytearray(make_dump())
        snapshot_size = decoder.DUMP_HEADER.unpack_from(changed)[5]
        for snapshot_index in range(2):
            start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size
            words = list(struct.unpack_from("<36I", changed, start))
            words[10] = 3
            words[35] = zlib.crc32(struct.pack("<35I", *words[:35])) & 0xFFFFFFFF
            changed[start:start + decoder.TRACE_HEADER_BYTES] = struct.pack("<36I", *words)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "next_session_not_after_last_assigned"):
            decode_dump(bytes(changed))

        with self.assertRaisesRegex(decoder.TraceDecodeError, "completed_run_record_count_mismatch"):
            decode_dump(make_dump(1, last_run_status=1, repeat_count=2, next_repeat_index=2))

        interleaved_records = []
        record_specs = ((1, 10, 1, 0), (2, 20, 1, 0), (1, 11, 2, 1))
        for record_index, (session_id, frame_id, result_seq, repeat_index) in enumerate(record_specs):
            words = list(struct.unpack("<46I", make_record(0 if repeat_index == 0 else 1)))
            words[3] = record_index
            words[4] = session_id
            words[5] = frame_id
            words[6] = result_seq
            words[7] = repeat_index
            words[33] = frame_id
            words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
            interleaved_records.append(struct.pack("<46I", *words))
        header_words = list(struct.unpack("<36I", make_header(3)))
        header_words[10] = 3
        header_words[19] = 2
        header_words[21] = 20
        header_words[22] = 1
        header_words[23] = 1
        header_words[24] = 2
        header_words[35] = zlib.crc32(struct.pack("<35I", *header_words[:35])) & 0xFFFFFFFF
        interleaved_snapshot = (
            struct.pack("<36I", *header_words) + b"".join(interleaved_records) +
            bytes(decoder.TRACE_RECORD_BYTES * (decoder.TRACE_CAPACITY - len(interleaved_records)))
        )
        interleaved_dump_header = decoder.DUMP_HEADER.pack(
            decoder.DUMP_MAGIC, decoder.DUMP_VERSION, decoder.TRACE_HEADER_BYTES,
            decoder.TRACE_RECORD_BYTES, decoder.TRACE_CAPACITY, len(interleaved_snapshot),
        )
        with self.assertRaisesRegex(decoder.TraceDecodeError, "record_session_order_not_monotonic"):
            decode_dump(interleaved_dump_header + interleaved_snapshot + interleaved_snapshot)

    def test_decoder_requires_expected_source_and_boot_identity(self) -> None:
        changed_source = mutate_header_word(make_dump(), 27, 0xDEADBEEF)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "derived_source_sha256_mismatch"):
            decode_dump(changed_source)
        changed_seed = mutate_header_word(make_dump(), 6, (TEST_BOOT_SEED & 0xFFFFFFFF) + 1)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "boot_seed_mismatch"):
            decode_dump(changed_seed)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "derived_source_sha256_mismatch"):
            decode_dump(make_dump(), expected_source="f" * 64)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "boot_seed_mismatch"):
            decode_dump(make_dump(), expected_seed=TEST_BOOT_SEED + 1)
        zero_seed = mutate_header_word(make_dump(), 6, 0)
        zero_seed = mutate_header_word(zero_seed, 7, 0)
        with self.assertRaisesRegex(decoder.TraceDecodeError, "boot_seed_zero"):
            decode_dump(zero_seed)


def mutate_header_word(blob: bytes, word_index: int, value: int) -> bytes:
    result = bytearray(blob)
    snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
    for snapshot_index in range(2):
        start = decoder.DUMP_HEADER.size + snapshot_index * snapshot_size
        words = list(struct.unpack_from("<36I", result, start))
        words[word_index] = value
        words[35] = zlib.crc32(struct.pack("<35I", *words[:35])) & 0xFFFFFFFF
        result[start:start + decoder.TRACE_HEADER_BYTES] = struct.pack("<36I", *words)
    return bytes(result)


class DerivationBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entries, cls.manifest = builder.bundle_members(builder.BUNDLE_PATH)
        cls.base_source = cls.entries["bundle/workspace/infer/src/s2b_inference_app.c"]

    def test_derives_only_from_exact_frozen_source_and_updates_identity(self) -> None:
        derived, derived_sha = builder.derive_source(self.base_source)
        self.assertEqual(hashlib.sha256(derived).hexdigest(), derived_sha)
        text = derived.decode("utf-8")
        self.assertIn("DIAG=s4b-ps-tensor/1 TRACE_ABI=1", text)
        self.assertIn("s4b_ps_trace_begin_run", text)
        platform = self.entries["bundle/workspace/infer/src/s2b_inference_platform.h"]
        updated = builder.replace_embedded_source_sha(platform, derived_sha).decode("utf-8")
        self.assertIn(f'#define S2B_C_SOURCE_SHA256 "{derived_sha}"', updated)

    def test_successful_run_parks_without_accepting_a_second_request(self) -> None:
        derived, _ = builder.derive_source(self.base_source)
        text = derived.decode("utf-8")
        main = text[text.rfind("int main(void)"):]
        self.assertIn("if (!s4b_ps_trace_end_run(1)) return 0;\n    return 2;", text)
        self.assertEqual(main.count("service_request()"), 1)
        self.assertIn("if (service_status == 2)", main)
        self.assertIn('for (;;) __asm__ volatile("wfe" ::: "memory");', main)
        self.assertNotIn("while (service_request())", main)

    def test_rejects_changed_frozen_source_sha(self) -> None:
        altered = bytearray(self.base_source)
        altered[-1] ^= 1
        with self.assertRaisesRegex(builder.BuildError, "冻结2B app原始SHA不匹配"):
            builder.derive_source(bytes(altered))

    def test_rejects_missing_unique_anchor_after_source_hash_binding(self) -> None:
        anchor = b'#include "s2a_ps_decode_nms_reference.h"\n'
        altered = self.base_source.replace(anchor, b'#include "different_decode_header.h"\n', 1)
        self.assertEqual(altered.count(anchor), 0)
        old_sha = builder.BASE_APP_SHA256
        builder.BASE_APP_SHA256 = hashlib.sha256(altered).hexdigest()
        try:
            with self.assertRaisesRegex(builder.BuildError, "派生锚点数量错误 trace_headers"):
                builder.derive_source(altered)
        finally:
            builder.BASE_APP_SHA256 = old_sha


class MemoryRangeTests(unittest.TestCase):
    def test_network_input_range_matches_frozen_tensor_length(self) -> None:
        start, end, size = builder.network_input_region(
            builder.ARENA_START,
            builder.ARENA_START + builder.ARENA_BYTES,
        )
        self.assertEqual(end - start, 519168)
        self.assertEqual(size, 519168)
        self.assertEqual(end, 0x1007EC00)

    def test_network_input_range_rejects_short_arena(self) -> None:
        with self.assertRaisesRegex(builder.BuildError, "超出冻结tensor arena"):
            builder.network_input_region(builder.ARENA_START, builder.ARENA_START + 519167)


def synthetic_memory_map() -> tuple[str, str, dict[str, int]]:
    symbols = {
        "__bss_start": 0x00110000,
        "__bss_end": 0x00700000,
        "_heap_start": 0x00700000,
        "_heap_end": 0x00800000,
        "_stack_end": 0x00800000,
        "_stack": 0x00810000,
        "__stack": 0x00810000,
        "_irq_stack_end": 0x00810000,
        "__irq_stack": 0x00810400,
        "_supervisor_stack_end": 0x00810400,
        "__supervisor_stack": 0x00810C00,
        "_abort_stack_end": 0x00810C00,
        "__abort_stack": 0x00811000,
        "_fiq_stack_end": 0x00811000,
        "__fiq_stack": 0x00811400,
        "_undef_stack_end": 0x00811400,
        "__undef_stack": 0x00811800,
        "__s2b_tensor_start": 0x10000000,
        "__s2b_tensor_end": 0x12000000,
        "s4b_ps_trace_header_data": 0x006EFEC0,
        "s4b_ps_trace_records": 0x006C3000,
        "staging": 0x00120000,
    }
    nm_text = "\n".join(f"{address:08x} B {name}" for name, address in symbols.items())
    sections = {
        ".text": (0x1000, 0x00100000),
        ".bss": (symbols["__bss_end"] - symbols["__bss_start"], symbols["__bss_start"]),
        ".heap": (symbols["_heap_end"] - symbols["_heap_start"], symbols["_heap_start"]),
        ".stack": (71680, symbols["_stack_end"]),
        ".s2b_tensor_ddr": (0x02000000, 0x10000000),
    }
    section_text = "\n".join(
        f" 1 {name} {size:08x} {vma:08x} {vma:08x}"
        for name, (size, vma) in sections.items()
    )
    return nm_text, section_text, symbols


class BundlePathTests(unittest.TestCase):
    def test_bundle_paths_reject_windows_and_traversal_before_writes(self) -> None:
        probe_root = Path(os.environ.get(
            "S4B_PS_TEST_TMP_ROOT", builder.ROOT / "tmp/4/S4-B-REAL-01"
        ))
        probe_root.mkdir(parents=True, exist_ok=True)
        invalid_names = (
            "..\\escape.bin",
            "C:/escape.bin",
            "\\\\server\\share\\escape.bin",
            "/absolute.bin",
            "bundle/workspace/../../escape.bin",
            "bundle/workspace/C:/escape.bin",
        )
        with tempfile.TemporaryDirectory(dir=probe_root, prefix="path_preflight_") as temp:
            root = Path(temp)
            for index, name in enumerate(invalid_names):
                destination = root / f"extract_{index}"
                with self.subTest(member=name):
                    with self.assertRaises(builder.BuildError):
                        builder.extract_members({
                            "bundle/workspace/safe.txt": b"safe",
                            name: b"must-not-write",
                        }, destination)
                    self.assertFalse(destination.exists())
            destination = root / "valid_extract"
            builder.extract_members(
                {"bundle/workspace/nested/safe.txt": b"safe"}, destination
            )
            self.assertEqual(
                (destination / "bundle/workspace/nested/safe.txt").read_bytes(), b"safe"
            )


class FullMemoryMapTests(unittest.TestCase):
    def test_memory_map_reports_complete_exception_stacks(self) -> None:
        nm_text, section_text, _ = synthetic_memory_map()
        ranges = builder.verify_memory_map(nm_text, section_text)
        self.assertEqual(ranges["stack"]["size_bytes"], 71680)
        self.assertEqual(ranges["thread_stack"]["size_bytes"], 65536)
        self.assertEqual(
            {name: item["size_bytes"] for name, item in ranges["exception_stacks"].items()},
            {"IRQ": 1024, "SVC": 2048, "ABT": 1024, "FIQ": 1024, "UND": 1024},
        )

    def test_memory_map_rejects_missing_stack_symbol(self) -> None:
        nm_text, section_text, _ = synthetic_memory_map()
        nm_text = "\n".join(line for line in nm_text.splitlines() if not line.endswith("__irq_stack"))
        with self.assertRaisesRegex(builder.BuildError, "__irq_stack"):
            builder.verify_memory_map(nm_text, section_text)

    def test_memory_map_rejects_stack_overlap_and_out_of_bounds(self) -> None:
        nm_text, section_text, symbols = synthetic_memory_map()
        overlap_nm = nm_text.replace(
            f"{symbols['_supervisor_stack_end']:08x} B _supervisor_stack_end",
            f"{symbols['_irq_stack_end']:08x} B _supervisor_stack_end",
        )
        with self.assertRaisesRegex(builder.BuildError, "SVC栈|连续或顺序"):
            builder.verify_memory_map(overlap_nm, section_text)

        delta = 0x02000000
        shifted_symbols = dict(symbols)
        stack_names = (
            "_stack_end", "_stack", "__stack", "_irq_stack_end", "__irq_stack",
            "_supervisor_stack_end", "__supervisor_stack", "_abort_stack_end",
            "__abort_stack", "_fiq_stack_end", "__fiq_stack", "_undef_stack_end",
            "__undef_stack",
        )
        shifted_nm = "\n".join(
            f"{(address + delta if name in stack_names else address):08x} B {name}"
            for name, address in shifted_symbols.items()
        )
        shifted_sections = section_text.replace(
            f"{symbols['_stack_end']:08x} {symbols['_stack_end']:08x}",
            f"{symbols['_stack_end'] + delta:08x} {symbols['_stack_end'] + delta:08x}",
        )
        with self.assertRaisesRegex(builder.BuildError, "heap/stack范围越出"):
            builder.verify_memory_map(shifted_nm, shifted_sections)

    def test_memory_map_rejects_log_array_overlap(self) -> None:
        nm_text, section_text, symbols = synthetic_memory_map()
        overlap_nm = nm_text.replace(
            f"{symbols['s4b_ps_trace_header_data']:08x} B s4b_ps_trace_header_data",
            f"{symbols['s4b_ps_trace_records']:08x} B s4b_ps_trace_header_data",
        )
        with self.assertRaisesRegex(builder.BuildError, "日志头与staging重叠|记录数组与日志头重叠"):
            builder.verify_memory_map(overlap_nm, section_text)


class UnittestSummaryTests(unittest.TestCase):
    def test_parses_actual_test_summary_with_lf(self) -> None:
        output = "Ran 14 tests in 0.020s\n\nOK\n"
        self.assertEqual(builder.parse_unittest_summary(output), 14)

    def test_parses_actual_test_summary_with_crlf(self) -> None:
        output = "test_case ... ok\r\n\r\nRan 14 tests in 0.020s\r\n\r\nOK\r\n"
        self.assertEqual(builder.parse_unittest_summary(output), 14)

    def test_parses_singular_test_summary(self) -> None:
        output = "Ran 1 test in 0.001s\n\nOK\n"
        self.assertEqual(builder.parse_unittest_summary(output), 1)

    def test_rejects_missing_test_summary(self) -> None:
        with self.assertRaisesRegex(builder.BuildError, "摘要缺失或不唯一"):
            builder.parse_unittest_summary("OK\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
