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

def identify(blob, source=SOURCE, seed=SEED):
    out = bytearray(blob)
    size = d.DUMP_HEADER.unpack_from(blob)[5]
    for index in range(2):
        start = d.DUMP_HEADER.size + index * size
        words = list(struct.unpack_from("<36I", out, start))
        words[6], words[7] = seed & 0xFFFFFFFF, seed >> 32
        for part in range(8):
            words[27 + part] = int(source[part * 8:(part + 1) * 8], 16)
        words[35] = zlib.crc32(struct.pack("<35I", *words[:35])) & 0xFFFFFFFF
        out[start:start + d.TRACE_HEADER_BYTES] = struct.pack("<36I", *words)
    return bytes(out)

def decode(blob):
    return d.decode_bytes(blob, expected_derived_source_sha256=SOURCE,
                          expected_boot_seed=SEED)

def reject(label, blob):
    try:
        decode(blob)
    except d.TraceDecodeError as error:
        print(f"REJECT {label}: {error}")
        return
    raise AssertionError(f"{label} unexpectedly accepted")

valid = identify(make_dump(1))
decoded = decode(valid)
assert decoded["derived_source_sha256"] == SOURCE
assert decoded["boot_seed"] == SEED
print("ACCEPT r12_identity_legal_success_baseline")
reject("crc_repaired_source_mismatch", identify(make_dump(1), source="0" * 64))
reject("crc_repaired_nonzero_seed_mismatch", identify(make_dump(1), seed=SEED ^ 1))
reject("crc_repaired_zero_seed", identify(make_dump(1), seed=0))

default = struct.unpack("<46I", make_record(0))[44]
edge = mutate_record_words(valid, 0, {39: 15, 40: 12675})
assert decode(edge)["records"][0]["detection_count"] == 15
assert decode(edge)["records"][0]["raw_candidate_count"] == 12675
print("ACCEPT response_ok_detection_15_candidates_12675")
reject("response_ok_detection_16", mutate_record_words(valid, 0, {39: 16}))
reject("response_ok_candidates_12676", mutate_record_words(valid, 0, {39: 0, 40: 12676}))
print("PROBE_PASS cases=8 expected_source=" + SOURCE + " expected_boot_seed=0x%016X" % SEED)
