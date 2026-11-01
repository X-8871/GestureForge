import hashlib
import json
import random
from pathlib import Path

root = Path(__file__).resolve().parents[4]
engine = root / "src" / "s2a_conv_tile_engine.sv"
rng = random.Random(0x2A20261006)
counts = {
    "shape_small_domain_cases": 0,
    "shape_full_width_random_cases": 0,
    "feature_scan_indices": 0,
    "feature_scan_boundary_indices": 0,
    "reduction_indices": 0,
    "output_point_indices": 0,
}
failures = []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def shape_old_bad(numerator, kernel, stride, output):
    if numerator < kernel or stride == 0 or output == 0:
        return True
    return ((numerator - kernel) // stride) + 1 != output

def shape_new_bad(numerator, kernel, stride, output):
    if numerator < kernel or stride == 0 or output == 0:
        return True
    span = numerator - kernel
    product = output * stride
    return product <= span or product > span + stride

def check_shape(numerator, kernel, stride, output, label):
    old = shape_old_bad(numerator, kernel, stride, output)
    new = shape_new_bad(numerator, kernel, stride, output)
    product = output * stride
    span = numerator - kernel
    if product > (1 << 64) - 1 or (numerator >= kernel and span + stride > (1 << 64) - 1):
        failures.append({"kind": "64_bit_bound", "case": label, "product": product, "span_plus_stride": span + stride})
    if old != new:
        failures.append({"kind": "shape_mismatch", "case": label, "n": numerator, "k": kernel, "s": stride, "o": output, "old_bad": old, "new_bad": new})

for numerator in range(0, 129):
    for kernel in range(1, 65):
        for stride in range(1, 17):
            span_nonnegative = max(numerator - kernel, 0)
            exact_output = span_nonnegative // stride + 1
            candidates = {0, 1, exact_output, exact_output + 1, max(1, exact_output - 1), 0xFFFFFFFF}
            for output in candidates:
                check_shape(numerator, kernel, stride, output, "small")
                counts["shape_small_domain_cases"] += 1
for _ in range(100000):
    numerator = rng.randrange(0, 3 * ((1 << 32) - 1) + 1)
    kernel = rng.randrange(1, 1 << 32)
    stride = rng.randrange(1, 1 << 32)
    output = rng.randrange(1, 1 << 32)
    check_shape(numerator, kernel, stride, output, "random32")
    counts["shape_full_width_random_cases"] += 1
edge = (1 << 32) - 1
for numerator, kernel, stride, output in [
    (3 * edge, 1, edge, edge),
    (3 * edge, edge, edge, edge),
    (edge, edge, 1, 1),
    (edge, 1, edge, 1),
    (2 * edge, edge, edge, 2),
    (0, 1, edge, 1),
]:
    check_shape(numerator, kernel, stride, output, "edge32")
    counts["shape_small_domain_cases"] += 1

def check_feature_shape(height, width, channels, field):
    channel = y = x = 0
    plane = height * width
    total = plane * channels
    for index in range(total):
        old = (index // plane, (index % plane) // width, index % width)
        if old != (channel, y, x):
            failures.append({"kind": field, "shape": [height, width, channels], "index": index,
                             "old": old, "new": [channel, y, x]})
        if index + 1 < total:
            if x + 1 >= width:
                x = 0
                if y + 1 >= height:
                    y = 0
                    channel += 1
                else:
                    y += 1
            else:
                x += 1
        counts[field] += 1

for height in range(1, 25):
    for width in range(1, 25):
        for channels in range(1, 9):
            check_feature_shape(height, width, channels, "feature_scan_indices")
for height, width, channels in [(1, 51200, 1), (51200, 1, 1), (40, 40, 32), (1, 1600, 32)]:
    if height * width * channels <= 51200:
        check_feature_shape(height, width, channels, "feature_scan_boundary_indices")

for channels in range(1, 33):
    for kernel_h in range(1, 10):
        for kernel_w in range(1, 10):
            reduction = channels * kernel_h * kernel_w
            if reduction > 8191:
                continue
            ch = ky = kx = 0
            for index in range(reduction):
                old = (index // (kernel_h * kernel_w),
                       (index % (kernel_h * kernel_w)) // kernel_w,
                       index % kernel_w)
                if old != (ch, ky, kx):
                    failures.append({"kind": "reduction_mismatch", "shape": [channels, kernel_h, kernel_w],
                                     "index": index, "old": old, "new": [ch, ky, kx]})
                counts["reduction_indices"] += 1
                if index + 1 < reduction:
                    if kx + 1 >= kernel_w:
                        kx = 0
                        if ky + 1 >= kernel_h:
                            ky = 0
                            ch += 1
                        else:
                            ky += 1
                    else:
                        kx += 1

for tile_h in range(1, 9):
    for tile_w in range(1, 9):
        y = x = 0
        for index in range(tile_h * tile_w):
            old = (index // tile_w, index % tile_w)
            if old != (y, x):
                failures.append({"kind": "output_point_mismatch", "shape": [tile_h, tile_w],
                                 "index": index, "old": old, "new": [y, x]})
            counts["output_point_indices"] += 1
            if index + 1 < tile_h * tile_w:
                if x + 1 >= tile_w:
                    x = 0
                    y += 1
                else:
                    x += 1

record = {
    "schema": "s2a_resopt02_equivalence_model_v1",
    "candidate_engine_sha256": sha(engine),
    "random_seed": "0x2A20261006",
    "counts": counts,
    "failed_assertions": len(failures),
    "first_failures": failures[:20],
    "status": "PASS" if not failures else "FAIL",
}
(root / "equivalence_model_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, indent=2))
raise SystemExit(0 if not failures else 1)