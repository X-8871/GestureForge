import hashlib
import json
import math
import random
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path

pixel_path, fp64_path, d2_path, vector_path, output_path = map(Path, sys.argv[1:6])
expected_hashes = {
    "pixel": "4c4563433e9b5d868dde8c9232326afce1ddc4d4297bb548c7fc5252c6e284c1",
    "fp64": "137e7519e98af3e4a8577d3328716217c20722b9f5d7c0399eef4e1c375fd2d7",
    "d2": "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f",
    "vectors": "e31ca3da0993f1f9531f204445c8830b83dd712d40f6130a74cd2842234e1875",
}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
actual_hashes = {
    "pixel": sha(pixel_path), "fp64": sha(fp64_path),
    "d2": sha(d2_path), "vectors": sha(vector_path),
}
if actual_hashes != expected_hashes:
    raise AssertionError(f"输入哈希不匹配: {actual_hashes}")

def bits_to_float(bits):
    return struct.unpack(">d", bits.to_bytes(8, "big"))[0]
def float_to_bits(value):
    return int.from_bytes(struct.pack(">d", value), "big")

pixel_text = pixel_path.read_text(encoding="utf-8")
rom_pairs = [(int(i), int(v, 16)) for i, v in re.findall(
    r"7'd(\d+):\s*threshold_at\s*=\s*64'h([0-9a-fA-F]{16})", pixel_text
)]
if len(rom_pairs) != 127 or [i for i, _ in rom_pairs] != list(range(127)):
    raise AssertionError(f"ROM index/count invalid: {len(rom_pairs)}")
rom = [v for _, v in rom_pairs]
if not all(a < b for a, b in zip(rom, rom[1:])):
    raise AssertionError("ROM is not strictly increasing")

scale = 1.0 / 127.0
def d2_raw_to_int(bits):
    raw = bits_to_float(bits)
    if not math.isfinite(raw):
        raise ValueError("nonfinite")
    normalized = raw / 255.0
    normalized = max(0.0, min(1.0, normalized))
    scaled = normalized / scale
    rounded = math.floor(abs(scaled) + 0.5)
    return max(-127, min(127, rounded))

max_raw = float_to_bits(255.0)
derived = []
for target in range(1, 128):
    low, high = 0, max_raw
    while low < high:
        mid = (low + high) // 2
        if d2_raw_to_int(mid) >= target:
            high = mid
        else:
            low = mid + 1
    derived.append(low)
if derived != rom:
    first = next((i for i, (a, b) in enumerate(zip(derived, rom)) if a != b), None)
    raise AssertionError(f"ROM differs from independently derived D2 thresholds at {first}")
for target, threshold in enumerate(rom, start=1):
    if d2_raw_to_int(threshold) != target:
        raise AssertionError(f"threshold {target} maps incorrectly")
    if threshold > 0 and d2_raw_to_int(threshold - 1) != target - 1:
        raise AssertionError(f"threshold predecessor {target} maps incorrectly")
    if threshold < max_raw and d2_raw_to_int(threshold + 1) != target:
        raise AssertionError(f"threshold successor {target} maps incorrectly")
for code in range(256):
    for value in (float(code),) if code == 255 else (
        float(code), code + 0.5, math.nextafter(code + 0.5, -math.inf),
        math.nextafter(code + 0.5, math.inf)
    ):
        if d2_raw_to_int(float_to_bits(value)) != max(0, min(127, math.floor((max(0.0, min(1.0, value / 255.0)) / scale) + 0.5))):
            raise AssertionError(f"integer/half-integer quantization mismatch at {value.hex()}")
rng = random.Random(0x534232)
for _ in range(10000):
    value_bits = rng.randrange(0, max_raw + 1)
    value = bits_to_float(value_bits)
    if d2_raw_to_int(value_bits) != max(0, min(127, math.floor((max(0.0, min(1.0, value / 255.0)) / scale) + 0.5))):
        raise AssertionError(f"seeded quantization mismatch at {value.hex()}")

if rom[63] != float_to_bits(127.5) or d2_raw_to_int(rom[63]) != 64:
    raise AssertionError("code 64 threshold boundary is incorrect")
if d2_raw_to_int(rom[64]) != 65 or d2_raw_to_int(rom[64] - 1) != 64:
    raise AssertionError("code 65 threshold boundary is incorrect")

sx = 1 * ((202 - 1) / (255 - 1))
dx = sx - math.floor(sx)
top = (1.0 - dx) * 201.0 + dx * 202.0
bottom = (1.0 - dx) * 201.0 + dx * 202.0
dy = 0.0
value = (1.0 - dy) * top + dy * bottom
scaled = (value / 255.0) / scale
sample = {
    "value_hex": f"0x{float_to_bits(value):016x}",
    "scaled_hex": f"0x{float_to_bits(scaled):016x}",
    "quantized": math.floor(abs(scaled) + 0.5),
    "exact_rational_scaled": str(Fraction(201 * 127, 254)),
}
if sample["value_hex"] != "0x40693952a54a952a" or sample["quantized"] != 100:
    raise AssertionError(f"known binary64 boundary changed: {sample}")
if Fraction(201 * 127, 254) != Fraction(201, 2):
    raise AssertionError("exact rational comparison is not 100.5")
padding_scaled = 0.5 / scale
padding_quantized = math.floor(abs(padding_scaled) + 0.5)
raw_half_quantized = d2_raw_to_int(float_to_bits(0.5))
if padding_quantized != 64 or raw_half_quantized != 0:
    raise AssertionError("normalized pad and raw pixel units were confused")

def supported(bits):
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7ff
    fraction = bits & ((1 << 52) - 1)
    return sign == 0 and exponent != 0x7ff and (exponent != 0 or fraction == 0)
def is_zero(bits):
    return (bits & ((1 << 63) - 1)) == 0
rows = vector_path.read_text(encoding="ascii").splitlines()
count = int(rows[0])
if count != 547 or len(rows) != count + 1:
    raise AssertionError(f"unexpected vector count/length {count}/{len(rows)}")
last_success = 0
domain_counts = {"success": 0, "input_error": 0, "result_error": 0}
for row_index, line in enumerate(rows[1:]):
    fields = line.split()
    if len(fields) != 6:
        raise AssertionError(f"bad vector row {row_index}")
    op, a, b, expected_result, expected_error, expected_code = (
        int(fields[0], 16), int(fields[1], 16), int(fields[2], 16),
        int(fields[3], 16), int(fields[4], 16), int(fields[5], 16)
    )
    if not supported(a) or not supported(b):
        error, code = 1, 1
    else:
        af, bf = bits_to_float(a), bits_to_float(b)
        if op:
            value = (0.0 if is_zero(a) else bf) if is_zero(a) else ((0.0 if is_zero(b) else af) if is_zero(b) else af + bf)
            if is_zero(a):
                value = 0.0 if is_zero(b) else bf
            elif is_zero(b):
                value = af
            result_bits = float_to_bits(value)
        else:
            value = 0.0 if is_zero(a) or is_zero(b) else af * bf
            result_bits = float_to_bits(value)
        exponent = (result_bits >> 52) & 0x7ff
        fraction = result_bits & ((1 << 52) - 1)
        underflow_to_zero = value == 0.0 and not (op and (is_zero(a) or is_zero(b))) and not (not op and (is_zero(a) or is_zero(b)))
        if exponent == 0x7ff or (exponent == 0 and fraction != 0) or underflow_to_zero:
            error, code = 1, 2
        else:
            error, code = 0, 0
            last_success = result_bits
    if error:
        domain_counts["input_error" if code == 1 else "result_error"] += 1
        result_bits = last_success
    else:
        domain_counts["success"] += 1
    if error == 0:
        exact_a = Fraction.from_float(bits_to_float(a))
        exact_b = Fraction.from_float(bits_to_float(b))
        exact_value = exact_a + exact_b if op else exact_a * exact_b
        if float_to_bits(float(exact_value)) != result_bits:
            raise AssertionError(f"exact-rational FP64 mismatch at vector {row_index}")
    if (error, code, result_bits) != (int(expected_error != 0), expected_code, expected_result):
        raise AssertionError("FP64 vector %d: oracle %r vector %r" % (
            row_index, (error, code, hex(result_bits)),
            (expected_error, expected_code, hex(expected_result))
        ))

result = {
    "status": "PASS",
    "hashes": actual_hashes,
    "thresholds": {
        "count": len(rom), "independently_rederived": len(derived),
        "predecessor_threshold_successor_checks": 381,
        "integer_half_integer_checks": sum(1 if c == 255 else 4 for c in range(256)),
        "seeded_checks": 10000,
        "code64_threshold_hex": f"0x{rom[63]:016x}",
        "code65_threshold_hex": f"0x{rom[64]:016x}",
    },
    "d2_boundary_case": sample,
    "padding_boundary": {
        "normalized_pad_value": 0.5,
        "normalized_pad_quantized": padding_quantized,
        "raw_pixel_half_quantized": raw_half_quantized,
    },
    "fp64_vectors_independently_checked_against_python_ieee754_and_fraction": {
        "rows": count, "classes": domain_counts,
        "scope": "重新验证向量期望与独立宿主binary64及输入/结果域策略一致；不等同于执行RTL"
    },
}
output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
