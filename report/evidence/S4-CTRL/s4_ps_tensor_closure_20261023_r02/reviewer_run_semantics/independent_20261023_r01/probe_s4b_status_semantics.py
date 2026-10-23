import struct
import sys
import zlib

sys.path.insert(0, r"D:\codex-worktrees\w4")

from scripts.stage4_s4b import decode_s4b_ps_trace as decoder
from verification import test_s4b_ps_tensor as fixtures

EXPECTED_SOURCE = "1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436"
EXPECTED_SEED = 0x5342424F4F543132
fixtures.TEST_SOURCE_SHA256 = EXPECTED_SOURCE
fixtures.TEST_BOOT_SEED = EXPECTED_SEED

def decode(blob):
    return decoder.decode_bytes(
        blob,
        expected_derived_source_sha256=EXPECTED_SOURCE,
        expected_boot_seed=EXPECTED_SEED,
    )

def accept(name, blob):
    result = decode(blob)
    print("ACCEPT", name, "count=" + str(result["record_count"]),
          "status=" + str(result["header"]["last_run_status"]))
    return result

def reject(name, blob, expected):
    try:
        decode(blob)
    except decoder.TraceDecodeError as exc:
        if expected and expected not in str(exc):
            raise AssertionError(name + " wrong rejection: " + str(exc))
        print("REJECT", name, "reason=" + str(exc))
    else:
        raise AssertionError(name + " was accepted")

def repair_record(words):
    words[45] = zlib.crc32(struct.pack("<45I", *words[:45])) & 0xFFFFFFFF
    return struct.pack("<46I", *words)

def make_cross_session_failure_prefix():
    failure = list(struct.unpack("<46I", fixtures.make_record(0)))
    failure[19:25] = [0] * 6
    failure[27:31] = [0] * 4
    failure[37] = 0
    failure[38] = decoder.UINT32_MAX
    failure[39] = 0
    failure[40] = 0
    failure[41] = decoder.RESPONSE_BAD_STATE
    failure[42] = 0
    failure[43] = decoder.ACK_NOT_ATTEMPTED
    failure[44] = (
        decoder.EVENT_INPUT_WRITE_START |
        decoder.EVENT_INPUT_WRITE_DONE |
        decoder.EVENT_LOG_COMMIT
    )
    failure_blob = repair_record(failure)

    later = list(struct.unpack("<46I", fixtures.make_record(0)))
    later[3] = 1
    later[4] = 2
    later[5] = 20
    later[6] = 1
    later[7] = 0
    later[8] = 16
    later[33] = 20
    later_blob = repair_record(later)

    header = list(struct.unpack(
        "<36I", fixtures.make_header(2, repeat_count=1, next_repeat_index=1)))
    header[10] = 3
    header[19] = 2
    header[20] = 16
    header[21] = 20
    header[22] = 1
    header[23] = 1
    header[24] = 2
    header[35] = zlib.crc32(struct.pack("<35I", *header[:35])) & 0xFFFFFFFF
    snapshot = (
        struct.pack("<36I", *header) +
        failure_blob + later_blob +
        bytes(decoder.TRACE_RECORD_BYTES * (decoder.TRACE_CAPACITY - 2))
    )
    dump_header = decoder.DUMP_HEADER.pack(
        decoder.DUMP_MAGIC, decoder.DUMP_VERSION,
        decoder.TRACE_HEADER_BYTES, decoder.TRACE_RECORD_BYTES,
        decoder.TRACE_CAPACITY, len(snapshot),
    )
    blob = dump_header + snapshot + snapshot
    return fixtures.mutate_header_word(blob, 18, 2)

baseline = accept("legal_completed_identity_baseline", fixtures.make_dump(2))
assert baseline["header"]["derived_source_sha256"] == EXPECTED_SOURCE
assert baseline["header"]["boot_seed"] == EXPECTED_SEED
accept("legal_completed_three_repeats", fixtures.make_dump(
    3, last_run_status=1, repeat_count=3, next_repeat_index=3))

partial_empty = fixtures.make_dump(
    0, last_run_status=2, repeat_count=15, next_repeat_index=1)
accept("legal_partial_empty_last_run_reserved_uncommitted", partial_empty)
accept("legal_partial_success_prefix", fixtures.make_dump(
    1, last_run_status=2, repeat_count=3, next_repeat_index=1))

repeated_blob = fixtures.make_dump(
    3, last_run_status=1, repeat_count=3, next_repeat_index=3)
repeated = accept("legal_completed_shared_cpu_memcpy_ticks", repeated_blob)
starts = {record["input_write_start_ticks"] for record in repeated["records"]}
dones = {record["input_write_done_ticks"] for record in repeated["records"]}
assert len(starts) == 1 and len(dones) == 1
print("ASSERT_SHARED_INPUT_COPY_TICKS", "start=" + str(next(iter(starts))),
      "done=" + str(next(iter(dones))))
reject("repeat_input_copy_ticks_mismatch", fixtures.mutate_record_words(
    repeated_blob, 1, {15: 102}), "run_metadata_changed")

max_bounds = fixtures.mutate_record_words(fixtures.make_dump(1), 0, {
    39: 15, 40: 12675,
})
accept("legal_t62_detection15_candidate12675", max_bounds)
reject("response_ok_detection16", fixtures.mutate_record_words(
    fixtures.make_dump(1), 0, {39: 16, 40: 12676}),
    "response_ok_detection_candidate_bounds")
reject("response_ok_candidate12676", fixtures.mutate_record_words(
    fixtures.make_dump(1), 0, {39: 1, 40: 12676}),
    "response_ok_detection_candidate_bounds")
reject("response_ok_decode_status99", fixtures.mutate_record_words(
    fixtures.make_dump(1), 0, {38: 99}),
    "response_ok_decode_status_invalid")

default_flags = struct.unpack("<46I", fixtures.make_record(0))[44]
reject("response_ok_missing_start", fixtures.mutate_record_words(
    fixtures.make_dump(1), 0, {
        19: 0, 20: 0,
        44: default_flags & ~decoder.EVENT_START_COMMAND,
    }), "response_ok_required_event_missing")
reject("response_ok_missing_postprocess", fixtures.mutate_record_words(
    fixtures.make_dump(1), 0, {
        23: 0, 24: 0,
        44: default_flags & ~decoder.EVENT_POSTPROCESS_DONE,
    }), "response_ok_required_event_missing")

error_safe = (decoder.CSR_ERROR_SAFE | decoder.CSR_SAFE_REUSE |
              decoder.CSR_TERMINAL)
board_error = fixtures.mutate_record_words(
    fixtures.make_dump(1, last_run_status=2), 0, {
        23: 0, 24: 0,
        34: error_safe, 35: 3,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_BOARD_ERROR,
        44: default_flags & ~decoder.EVENT_POSTPROCESS_DONE,
    })
accept("legal_partial_error_safe_board_error_ack", board_error)

decode_error = fixtures.mutate_record_words(
    fixtures.make_dump(1, last_run_status=2), 0, {
        38: (-2) & 0xFFFFFFFF, 39: 0, 40: 0,
        41: decoder.RESPONSE_DECODE_ERROR,
        43: decoder.ACK_NOT_ATTEMPTED,
        44: default_flags & ~decoder.EVENT_ACK_DONE,
    })
accept("legal_partial_decode_error_no_ack", decode_error)

uart_failed = fixtures.mutate_record_words(
    fixtures.make_dump(1, last_run_status=2), 0, {
        42: decoder.UART_SEND_FAILED,
        43: decoder.ACK_NOT_ATTEMPTED,
        44: default_flags & ~decoder.EVENT_ACK_DONE,
    })
accept("legal_partial_response_uart_failure", uart_failed)

ack_failed = fixtures.mutate_record_words(
    fixtures.make_dump(1, last_run_status=2), 0, {43: decoder.ACK_FAILED})
accept("legal_partial_response_ack_failure", ack_failed)

base_flags = (decoder.EVENT_INPUT_WRITE_START |
              decoder.EVENT_INPUT_WRITE_DONE |
              decoder.EVENT_LOG_COMMIT)
bad_state = fixtures.mutate_record_words(
    fixtures.make_dump(1, last_run_status=2), 0, {
        19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
        27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_BAD_STATE, 42: 0,
        43: decoder.ACK_NOT_ATTEMPTED, 44: base_flags,
    })
accept("legal_partial_bad_state_without_uart", bad_state)

timeout_flags = (
    decoder.EVENT_INPUT_WRITE_START |
    decoder.EVENT_INPUT_WRITE_DONE |
    decoder.EVENT_START_COMMAND |
    decoder.EVENT_TERMINAL_OBSERVED |
    decoder.EVENT_TERMINAL_SAFE |
    decoder.EVENT_LOG_COMMIT |
    decoder.EVENT_UART_START |
    decoder.EVENT_UART_DONE
)
done_safe = (decoder.CSR_DONE_SAFE | decoder.CSR_HEAD_VALID |
             decoder.CSR_SAFE_REUSE | decoder.CSR_TERMINAL)
wrong_frame = fixtures.mutate_record_words(
    fixtures.make_dump(
        1, last_run_status=2, repeat_count=2, next_repeat_index=1),
    0, {
        23: 0, 24: 0, 33: 999, 34: done_safe, 37: 1,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_OBSERVE_TIMEOUT,
        43: decoder.ACK_NOT_ATTEMPTED, 44: timeout_flags,
    })
wrong_frame_result = accept("legal_partial_safe_wrong_frame_timeout", wrong_frame)
assert wrong_frame_result["records"][0]["terminal_safe"]
assert wrong_frame_result["records"][0]["terminal_frame"] != wrong_frame_result["records"][0]["frame_id"]

raw_epoch = 0x12345678ABCDEF01
same_frame_epoch = fixtures.mutate_record_words(
    fixtures.make_dump(
        1, last_run_status=2, repeat_count=2, next_repeat_index=1),
    0, {
        23: 0, 24: 0,
        31: raw_epoch & 0xFFFFFFFF, 32: raw_epoch >> 32,
        34: done_safe, 37: 1,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_OBSERVE_TIMEOUT,
        43: decoder.ACK_NOT_ATTEMPTED, 44: timeout_flags,
    })
same_frame_result = accept("legal_partial_safe_same_frame_wrong_epoch_timeout", same_frame_epoch)
assert same_frame_result["records"][0]["terminal_frame"] == same_frame_result["records"][0]["frame_id"]
assert same_frame_result["records"][0]["epoch"] == raw_epoch

fault_flags = (
    decoder.EVENT_INPUT_WRITE_START |
    decoder.EVENT_INPUT_WRITE_DONE |
    decoder.EVENT_START_COMMAND |
    decoder.EVENT_TERMINAL_OBSERVED |
    decoder.EVENT_LOG_COMMIT |
    decoder.EVENT_UART_START |
    decoder.EVENT_UART_DONE
)
fault_timeout = fixtures.mutate_record_words(
    fixtures.make_dump(
        1, last_run_status=2, repeat_count=2, next_repeat_index=1),
    0, {
        23: 0, 24: 0,
        34: decoder.CSR_FAULT_ISOLATED | decoder.CSR_TERMINAL,
        35: 3, 37: 0,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_OBSERVE_TIMEOUT,
        43: decoder.ACK_NOT_ATTEMPTED, 44: fault_flags,
    })
fault_result = accept("legal_partial_fault_isolated_timeout_no_ack", fault_timeout)
assert not fault_result["records"][0]["terminal_safe"]

for name, blob in (
    ("response_uart_failure", uart_failed),
    ("response_ack_failure", ack_failed),
    ("board_error_with_ack", board_error),
    ("decode_error", decode_error),
    ("bad_state_without_uart", bad_state),
    ("safe_wrong_frame_timeout", wrong_frame),
    ("safe_wrong_epoch_timeout", same_frame_epoch),
    ("fault_timeout_no_ack", fault_timeout),
):
    reject("completed_" + name, fixtures.mutate_header_word(blob, 18, 1),
           "completed_run_contains_failed_attempt")

same_session_prefix = fixtures.mutate_record_words(
    fixtures.make_dump(2, last_run_status=2,
                       repeat_count=2, next_repeat_index=2),
    0, {
        19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0,
        27: 0, 28: 0, 29: 0, 30: 0, 37: 0,
        38: decoder.UINT32_MAX, 39: 0, 40: 0,
        41: decoder.RESPONSE_BAD_STATE, 42: 0,
        43: decoder.ACK_NOT_ATTEMPTED, 44: base_flags,
    })
reject("partial_failed_prefix_followed_by_same_session_record",
       same_session_prefix, "failed_attempt_not_terminal")
reject("partial_failure_followed_by_later_session_record",
       make_cross_session_failure_prefix(), "failed_attempt_not_terminal")

partial_failure_suffix = fixtures.mutate_record_words(
    fixtures.make_dump(2, last_run_status=2,
                       repeat_count=2, next_repeat_index=2),
    1, {
        42: decoder.UART_SEND_FAILED,
        43: decoder.ACK_NOT_ATTEMPTED,
        44: default_flags & ~decoder.EVENT_ACK_DONE,
    })
partial_suffix_result = accept("legal_partial_success_then_terminal_failure",
                               partial_failure_suffix)
assert partial_suffix_result["records"][0]["response_status"] == decoder.RESPONSE_OK
assert partial_suffix_result["records"][1]["uart_send_status"] == decoder.UART_SEND_FAILED

wrong_source = fixtures.mutate_header_word(fixtures.make_dump(1), 27, 0xDEADBEEF)
reject("crc_repaired_wrong_source_identity", wrong_source,
       "derived_source_sha256_mismatch")
wrong_seed = fixtures.mutate_header_word(
    fixtures.make_dump(1), 6, (EXPECTED_SEED & 0xFFFFFFFF) + 1)
reject("crc_repaired_wrong_boot_seed", wrong_seed, "boot_seed_mismatch")
zero_seed = fixtures.mutate_header_word(
    fixtures.mutate_header_word(fixtures.make_dump(1), 6, 0), 7, 0)
reject("zero_boot_seed", zero_seed, "boot_seed_zero")

print("PROBE_PASS", "cases=34",
      "expected_source=" + EXPECTED_SOURCE,
      "expected_boot_seed=0x" + format(EXPECTED_SEED, "016X"))