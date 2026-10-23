from pathlib import Path
import hashlib
import re
import struct

root = Path(r"D:\codex-worktrees\w4")
frame_path = root / "src/s4b_preproc_frame.sv"
pixel_path = root / "src/s4b_preproc_pixel.sv"
frame = frame_path.read_text(encoding="utf-8")
pixel = pixel_path.read_text(encoding="utf-8")
frame_match = re.search(r"FP64_MIN_WEIGHT_MAG\s*=\s*63'h([0-9a-fA-F]+)", frame)
pixel_match = re.search(r"FP64_MIN_GEOMETRY_WEIGHT\s*=\s*64'h([0-9a-fA-F]+)", pixel)
assert frame_match and pixel_match
frozen_min = int(frame_match.group(1), 16)
pixel_min = int(pixel_match.group(1), 16)
assert frozen_min == 0x03ca000000000000
assert pixel_min == 0x3ca0000000000000
one = 0x3ff0000000000000

def accepts(bits: int, threshold: int) -> bool:
    magnitude = bits & ((1 << 63) - 1)
    exponent = (bits >> 52) & 0x7ff
    if magnitude == 0:
        return (bits >> 63) == 0
    return not ((bits >> 63) or exponent == 0 or exponent == 0x7ff or magnitude < threshold or magnitude > one)

cases = [
    ("positive_zero", 0, True),
    ("minimum_2^-53", pixel_min, True),
    ("nextafter_below_minimum", pixel_min - 1, False),
    ("2^-100", struct.unpack(">Q", struct.pack(">d", 2.0 ** -100))[0], False),
]
print(f"frame_source_sha256={hashlib.sha256(frame_path.read_bytes()).hexdigest()}")
print(f"upstream_pixel_source_sha256={hashlib.sha256(pixel_path.read_bytes()).hexdigest()}")
print(f"frame_threshold=0x{frozen_min:016x}")
print(f"upstream_contract_threshold=0x{pixel_min:016x}")
print("case | bits | exponent | frozen_check | contract_check")
false_accepts = []
for name, bits, expected in cases:
    actual = accepts(bits, frozen_min)
    contract = accepts(bits, pixel_min)
    print(f"{name} | 0x{bits:016x} | 0x{(bits >> 52) & 0x7ff:03x} | {actual} | {contract}")
    assert contract == expected, (name, contract, expected)
    if actual and not contract:
        false_accepts.append(name)
assert false_accepts == ["nextafter_below_minimum", "2^-100"], false_accepts
print(f"confirmed_false_accepts={','.join(false_accepts)}")
print("probe_result=CONFIRMED_THRESHOLD_MISMATCH")
