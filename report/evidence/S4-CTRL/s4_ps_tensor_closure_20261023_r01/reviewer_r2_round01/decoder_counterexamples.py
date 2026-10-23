from __future__ import annotations
import struct
import zlib
from scripts.stage4_s4b import decode_s4b_ps_trace as decoder
from verification.test_s4b_ps_tensor import make_dump


def rewrite_word(blob: bytes, word_index: int, value: int, *, header: bool, record_index: int = 0) -> bytes:
    result = bytearray(blob)
    snapshot_size = decoder.DUMP_HEADER.unpack_from(blob)[5]
    for snap_index in range(2):
        base = decoder.DUMP_HEADER.size + snap_index * snapshot_size
        if header:
            off = base + word_index * 4
            struct.pack_into('<I', result, off, value)
            h = bytes(result[base:base + decoder.TRACE_HEADER_BYTES])
            struct.pack_into('<I', result, base + 35 * 4, zlib.crc32(h[:140]) & 0xFFFFFFFF)
        else:
            off = base + decoder.TRACE_HEADER_BYTES + record_index * decoder.TRACE_RECORD_BYTES + word_index * 4
            struct.pack_into('<I', result, off, value)
            rec = bytes(result[base + decoder.TRACE_HEADER_BYTES + record_index * decoder.TRACE_RECORD_BYTES:base + decoder.TRACE_HEADER_BYTES + (record_index + 1) * decoder.TRACE_RECORD_BYTES])
            struct.pack_into('<I', result, base + decoder.TRACE_HEADER_BYTES + record_index * decoder.TRACE_RECORD_BYTES + 45 * 4, zlib.crc32(rec[:180]) & 0xFFFFFFFF)
    return bytes(result)


def report(name: str, blob: bytes) -> None:
    try:
        result = decoder.decode_bytes(blob)
        print(f'{name}=ACCEPTED records={result["record_count"]} header_keys={sorted(result["header"].keys())}')
    except decoder.TraceDecodeError as exc:
        print(f'{name}=REJECTED reason={exc}')


base = make_dump()
report('baseline', base)
report('different_derived_sha_word_crc_repaired', rewrite_word(base, 27, 0xDEADBEEF, header=True))
zero_seed = rewrite_word(base, 6, 0, header=True)
zero_seed = rewrite_word(zero_seed, 7, 0, header=True)
report('zero_boot_seed_crc_repaired', zero_seed)
report('fault_isolated_status_with_safe_and_ack_claims', rewrite_word(base, 34, 6, header=False))
report('input_write_start_after_done', rewrite_word(base, 15, 1000, header=False))
report('second_repeat_different_uart_sequence', rewrite_word(base, 8, 0xDEADBEEF, header=False, record_index=1))
report('uart_failed_but_ack_succeeded', rewrite_word(rewrite_word(base, 42, 1, header=False), 43, 1, header=False))
