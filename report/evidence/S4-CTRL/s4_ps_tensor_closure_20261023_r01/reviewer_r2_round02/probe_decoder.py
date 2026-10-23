import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(r'D:\codex-worktrees\w4')
sys.path.insert(0, str(ROOT))
from scripts.stage4_s4b import decode_s4b_ps_trace as d

EVID = ROOT / 'report/evidence/S4-B/s4b_ps_tensor_20261023_r11'
expected_source = json.loads((EVID / 'machine_result.json').read_text(encoding='utf-8'))['derived_app_sha256']
expected_seed = int(json.loads((EVID / 'run_config.json').read_text(encoding='utf-8'))['boot_seed'], 0)
SID = 0x53422400
UART = 77
BASE_FRAME = 100
INPUT_CRC = 0x1234ABCD
COPY_START = 0x0100
COPY_DONE = 0x0110

def pack_header(count, status, repeat_count, next_index, source=expected_source, seed=expected_seed):
    w = [0] * 36
    w[0], w[1], w[2], w[3], w[4], w[5] = d.TRACE_MAGIC, d.SCHEMA_VERSION, 144, 184, 1000, count
    w[6], w[7] = seed & 0xffffffff, (seed >> 32) & 0xffffffff
    w[8], w[9], w[10], w[11] = SID, SID + 10, SID + 1, 0
    w[17], w[18], w[19], w[20] = 0, status, SID, UART
    w[21], w[22], w[23], w[24] = BASE_FRAME, repeat_count, next_index, SID
    w[25], w[26] = 1, 1
    for i in range(8):
        w[27 + i] = int(source[i * 8:(i + 1) * 8], 16)
    w[35] = zlib.crc32(struct.pack('<35I', *w[:35])) & 0xffffffff
    return struct.pack('<36I', *w)

def pack_record(index, repeat, *, kind='success', actual_frame=None):
    requested_frame = BASE_FRAME + repeat
    frame = requested_frame if actual_frame is None else actual_frame
    w = [0] * 46
    w[0], w[1], w[2], w[3] = d.RECORD_MAGIC, d.SCHEMA_VERSION, 184, index
    w[4], w[5], w[6], w[7], w[8], w[9] = SID, requested_frame, repeat + 1, repeat, UART, INPUT_CRC
    w[10], w[11] = d.INPUT_BYTES, d.INPUT_FORMAT_INT8_CHW_416
    w[12], w[13], w[14] = 0, 0, d.UNAVAILABLE_CAPTURE_TIME | d.UNAPPROVED_INFERENCE_NS
    flags = d.EVENT_INPUT_WRITE_START | d.EVENT_INPUT_WRITE_DONE | d.EVENT_LOG_COMMIT
    w[15], w[16] = COPY_START & 0xffffffff, COPY_START >> 32
    w[17], w[18] = COPY_DONE & 0xffffffff, COPY_DONE >> 32
    ticks = 0x200 + index * 0x100
    include_start = kind != 'no_uart'
    observed = kind in ('success', 'error_safe', 'safe_timeout_mismatch', 'fault_timeout')
    safe = kind in ('success', 'error_safe', 'safe_timeout_mismatch')
    postprocess = kind == 'success'
    uart_sent = kind != 'no_uart'
    ack = kind in ('success', 'error_safe')
    if include_start:
        flags |= d.EVENT_START_COMMAND
        w[19], w[20] = ticks & 0xffffffff, ticks >> 32
        ticks += 10
    if observed:
        flags |= d.EVENT_TERMINAL_OBSERVED
        w[21], w[22] = ticks & 0xffffffff, ticks >> 32
        ticks += 10
    if safe:
        flags |= d.EVENT_TERMINAL_SAFE
    if postprocess:
        flags |= d.EVENT_POSTPROCESS_DONE
        w[23], w[24] = ticks & 0xffffffff, ticks >> 32
        ticks += 10
    w[25], w[26] = ticks & 0xffffffff, ticks >> 32
    ticks += 10
    if uart_sent:
        flags |= d.EVENT_UART_START | d.EVENT_UART_DONE
        w[27], w[28] = ticks & 0xffffffff, ticks >> 32
        ticks += 10
        w[29], w[30] = ticks & 0xffffffff, ticks >> 32
    if kind in ('success', 'safe_timeout_mismatch'):
        w[34] = d.CSR_DONE_SAFE | d.CSR_HEAD_VALID | d.CSR_SAFE_REUSE | d.CSR_TERMINAL
        w[35], w[37] = 0, 1
    elif kind == 'error_safe':
        w[34] = d.CSR_ERROR_SAFE | d.CSR_SAFE_REUSE | d.CSR_TERMINAL
        w[35], w[37] = 3, 1
    elif kind == 'fault_timeout':
        w[34] = d.CSR_FAULT_ISOLATED | d.CSR_TERMINAL
        w[35], w[37] = 9, 0
    else:
        w[34], w[35], w[37] = d.CSR_SAFE_REUSE, 0, 0
    w[31], w[32] = 8, 0
    w[33] = frame
    w[36] = 0
    w[38], w[39], w[40] = (0 if postprocess else 0xffffffff), (3 if postprocess else 0), (7 if postprocess else 0)
    w[41] = {'success': d.RESPONSE_OK, 'error_safe': d.RESPONSE_BOARD_ERROR,
             'safe_timeout_mismatch': d.RESPONSE_OBSERVE_TIMEOUT,
             'fault_timeout': d.RESPONSE_OBSERVE_TIMEOUT, 'no_uart': 5}[kind]
    w[42] = d.UART_SEND_SUCCEEDED if uart_sent else 0
    w[43] = d.ACK_SUCCEEDED if ack else d.ACK_NOT_ATTEMPTED
    if ack:
        flags |= d.EVENT_ACK_DONE
    w[44] = flags
    w[45] = zlib.crc32(struct.pack('<45I', *w[:45])) & 0xffffffff
    return struct.pack('<46I', *w)

def make_dump(records, *, status=1, repeat_count=None, next_index=None, source=expected_source, seed=expected_seed):
    count = len(records)
    repeat_count = count if repeat_count is None else repeat_count
    next_index = count if next_index is None else next_index
    snapshot = pack_header(count, status, repeat_count, next_index, source, seed)
    snapshot += b''.join(records)
    snapshot += bytes(184 * (1000 - count))
    header = d.DUMP_HEADER.pack(d.DUMP_MAGIC, d.DUMP_VERSION, 144, 184, 1000, len(snapshot))
    return header + snapshot + snapshot

def mutate_record(blob, index, changes):
    out = bytearray(blob)
    snap_size = d.DUMP_HEADER.unpack_from(blob)[5]
    for copy_index in range(2):
        pos = d.DUMP_HEADER.size + copy_index * snap_size + 144 + index * 184
        words = list(struct.unpack_from('<46I', out, pos))
        for key, value in changes.items():
            words[key] = value
        words[45] = zlib.crc32(struct.pack('<45I', *words[:45])) & 0xffffffff
        out[pos:pos + 184] = struct.pack('<46I', *words)
    return bytes(out)

def mutate_header(blob, changes):
    out = bytearray(blob)
    snap_size = d.DUMP_HEADER.unpack_from(blob)[5]
    for copy_index in range(2):
        pos = d.DUMP_HEADER.size + copy_index * snap_size
        words = list(struct.unpack_from('<36I', out, pos))
        for key, value in changes.items():
            words[key] = value
        words[35] = zlib.crc32(struct.pack('<35I', *words[:35])) & 0xffffffff
        out[pos:pos + 144] = struct.pack('<36I', *words)
    return bytes(out)

def accept(name, blob, **kwargs):
    result = d.decode_bytes(blob, expected_derived_source_sha256=expected_source, expected_boot_seed=expected_seed)
    print(f'ACCEPT {name}: count={result["record_count"]} incomplete={result["last_run_incomplete"]}')
    return result

def reject(name, blob, reason):
    try:
        d.decode_bytes(blob, expected_derived_source_sha256=expected_source, expected_boot_seed=expected_seed)
    except d.TraceDecodeError as exc:
        if reason not in str(exc):
            raise AssertionError(f'{name}: wrong reason {exc!s}')
        print(f'REJECT {name}: {exc!s}')
        return
    raise AssertionError(f'{name}: accepted unexpectedly')

success = make_dump([pack_record(0, 0), pack_record(1, 1)], status=1, repeat_count=2, next_index=2)
base = accept('success_two_repeats_shared_CPU_copy_ticks', success)
assert base['records'][0]['input_write_start_ticks'] == base['records'][1]['input_write_start_ticks'] == COPY_START
assert base['records'][0]['input_write_done_ticks'] == base['records'][1]['input_write_done_ticks'] == COPY_DONE
(EVID / 'machine_result.json').read_text(encoding='utf-8')
probe_dir = Path(__file__).resolve().parent
(probe_dir / 'valid_success.dump').write_bytes(success)

error_safe = make_dump([pack_record(0, 0, kind='error_safe')], status=1, repeat_count=1, next_index=1)
error_result = accept('ERROR_SAFE_sent_response_matched_ACK', error_safe)
assert error_result['records'][0]['terminal_safe'] and error_result['records'][0]['ack_state'] == d.ACK_SUCCEEDED

fault = make_dump([pack_record(0, 0, kind='fault_timeout')], status=2, repeat_count=2, next_index=1)
fault_result = accept('FAULT_ISOLATED_OBSERVE_TIMEOUT_no_ACK_partial_RUN', fault)
assert fault_result['last_run_incomplete'] and fault_result['records'][0]['ack_state'] == d.ACK_NOT_ATTEMPTED

no_uart = make_dump([pack_record(0, 0, kind='no_uart')], status=2, repeat_count=1, next_index=1)
no_uart_result = accept('BAD_STATE_no_UART_no_ACK_partial_RUN', no_uart)
assert no_uart_result['records'][0]['uart_send_status'] == 0

safe_mismatch = make_dump([pack_record(0, 0, kind='safe_timeout_mismatch', actual_frame=BASE_FRAME + 1)], status=2, repeat_count=1, next_index=1)
(probe_dir / 'safe_terminal_frame_mismatch_timeout.dump').write_bytes(safe_mismatch)
reject('program_path_safe_terminal_frame_mismatch_timeout', safe_mismatch, 'terminal_safe_status_or_frame_mismatch')
safe_epoch_mismatch = mutate_record(safe_mismatch, 0, {33: BASE_FRAME})
reject('program_path_safe_terminal_epoch_mismatch_timeout_frame_matches', safe_epoch_mismatch, 'timeout_claims_safe_terminal')
missing_post_flags = struct.unpack_from('<46I', success, d.DUMP_HEADER.size + 144)[44] & ~d.EVENT_POSTPROCESS_DONE
missing_post = mutate_record(success, 0, {23: 0, 24: 0, 44: missing_post_flags})
accept('FALSE_ACCEPT_RESPONSE_OK_without_POSTPROCESS_event', missing_post)
missing_start_flags = struct.unpack_from('<46I', success, d.DUMP_HEADER.size + 144)[44] & ~d.EVENT_START_COMMAND
missing_start = mutate_record(success, 0, {19: 0, 20: 0, 44: missing_start_flags})
accept('FALSE_ACCEPT_RESPONSE_OK_without_START_COMMAND_event', missing_start)
accept('FALSE_ACCEPT_RESPONSE_OK_with_nonzero_decode_status', mutate_record(success, 0, {38: 99}))
accept('FALSE_ACCEPT_RESPONSE_OK_with_detection_count_over_15', mutate_record(success, 0, {39: 16}))
source_bad = mutate_header(success, {27: 0xDEADBEEF})
reject('CRC_repaired_wrong_expected_SOURCE', source_bad, 'derived_source_sha256_mismatch')
seed_bad = mutate_header(success, {6: (expected_seed & 0xffffffff) + 1})
reject('CRC_repaired_wrong_expected_seed', seed_bad, 'boot_seed_mismatch')
seed_zero = mutate_header(success, {6: 0, 7: 0})
reject('CRC_repaired_zero_seed', seed_zero, 'boot_seed_zero')
ack_bad = mutate_record(success, 0, {42: d.UART_SEND_FAILED})
reject('ACK_claim_after_UART_send_failure', ack_bad, 'ack_without_sent_safe_response')
timeout_ack = mutate_record(fault, 0, {43: d.ACK_SUCCEEDED, 44: struct.unpack_from('<46I', fault, d.DUMP_HEADER.size + 144)[44] | d.EVENT_ACK_DONE})
reject('FAULT_timeout_with_ACK_claim', timeout_ack, 'ack_without_sent_safe_response')
reject('reversed_present_event_tick_order', mutate_record(success, 0, {23: 1, 24: 0}), 'event_tick_order_invalid')
reject('same_session_input_CRC_changed', mutate_record(success, 1, {9: 0xDEADBEEF}), 'run_metadata_changed')
reject('same_session_input_length_changed', mutate_record(success, 1, {10: d.INPUT_BYTES - 1}), 'input_contract_mismatch')
reject('same_session_input_format_changed', mutate_record(success, 1, {11: d.INPUT_FORMAT_INT8_CHW_416 + 1}), 'input_contract_mismatch')
reject('same_session_CPU_copy_ticks_changed', mutate_record(success, 1, {15: COPY_START + 1}), 'run_metadata_changed')
reject('same_session_UART_sequence_changed', mutate_record(success, 1, {8: UART + 1}), 'uart_sequence_changed')
print(f'IDENTITY expected_source={expected_source} expected_seed=0x{expected_seed:016x}')
print('RESULT targeted false-rejection observed: actual generated timeout path with physically safe but frame-mismatched terminal is rejected after correct expected identity and valid CRCs')