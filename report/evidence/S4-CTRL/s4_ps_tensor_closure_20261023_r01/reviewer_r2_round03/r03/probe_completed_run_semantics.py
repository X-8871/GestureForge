import struct
import zlib
from pathlib import Path
import sys

ROOT = Path(r"D:\codex-worktrees\w4")
sys.path.insert(0, str(ROOT))
from scripts.stage4_s4b import decode_s4b_ps_trace as d
from verification.test_s4b_ps_tensor import make_dump, make_record, mutate_record_words

SOURCE = "1be7a551e26f61be1327cdb56672b08d86d17d16433ac405ebd263d5f35bf436"
SEED = 0x5342424F4F543132

def identify(blob):
    out = bytearray(blob)
    size = d.DUMP_HEADER.unpack_from(blob)[5]
    for index in range(2):
        start = d.DUMP_HEADER.size + index * size
        words = list(struct.unpack_from("<36I", out, start))
        words[6], words[7] = SEED & 0xFFFFFFFF, SEED >> 32
        for part in range(8):
            words[27 + part] = int(SOURCE[part * 8:(part + 1) * 8], 16)
        words[35] = zlib.crc32(struct.pack("<35I", *words[:35])) & 0xFFFFFFFF
        out[start:start + d.TRACE_HEADER_BYTES] = struct.pack("<36I", *words)
    return bytes(out)

def decode(blob):
    return d.decode_bytes(blob, expected_derived_source_sha256=SOURCE,
                          expected_boot_seed=SEED)

def mutate(blob, changes):
    return mutate_record_words(blob, 0, changes)

def confirm_status1_accepts_failure(name, blob):
    result = decode(blob)
    header = result["header"]
    record = result["records"][0]
    assert header["last_run_status"] == 1
    print("ACCEPT_IMPOSSIBLE_COMPLETED_RUN", name,
          "response_status=%d uart_status=%d ack_state=%d" %
          (record["response_status"], record["uart_send_status"], record["ack_state"]))

base = identify(make_dump(1))
base_result = decode(base)
assert base_result["header"]["last_run_status"] == 1
assert base_result["records"][0]["response_status"] == d.RESPONSE_OK
assert base_result["records"][0]["uart_send_status"] == d.UART_SEND_SUCCEEDED
assert base_result["records"][0]["ack_state"] == d.ACK_SUCCEEDED
print("ACCEPT legal_completed_success_baseline")

flags = struct.unpack("<46I", make_record(0))[44]
confirm_status1_accepts_failure("response_ok_uart_failure", mutate(base, {
    42: d.UART_SEND_FAILED, 43: d.ACK_NOT_ATTEMPTED,
    44: flags & ~d.EVENT_ACK_DONE,
}))
confirm_status1_accepts_failure("response_ok_ack_failure", mutate(base, {
    43: d.ACK_FAILED,
}))
error_status = d.CSR_ERROR_SAFE | d.CSR_SAFE_REUSE | d.CSR_TERMINAL
confirm_status1_accepts_failure("error_safe_ack_success", mutate(base, {
    23: 0, 24: 0, 34: error_status, 35: 3, 37: 1,
    38: d.UINT32_MAX, 39: 0, 40: 0,
    41: d.RESPONSE_BOARD_ERROR,
    44: flags & ~d.EVENT_POSTPROCESS_DONE,
}))
confirm_status1_accepts_failure("decode_error", mutate(base, {
    38: (-2) & 0xFFFFFFFF, 39: 0, 40: 0,
    41: d.RESPONSE_DECODE_ERROR, 43: d.ACK_NOT_ATTEMPTED,
    44: flags & ~d.EVENT_ACK_DONE,
}))
partial = identify(make_dump(1, last_run_status=2, repeat_count=2,
                             next_repeat_index=1))
partial = mutate(partial, {
    42: d.UART_SEND_FAILED, 43: d.ACK_NOT_ATTEMPTED,
    44: flags & ~d.EVENT_ACK_DONE,
})
partial_result = decode(partial)
assert partial_result["header"]["last_run_status"] == 2
assert partial_result["last_run_incomplete"] is True
print("ACCEPT legal_partial_run_uart_failure_control")
print("FINDING_CONFIRMED completed_status1_accepts_failed_attempts")
