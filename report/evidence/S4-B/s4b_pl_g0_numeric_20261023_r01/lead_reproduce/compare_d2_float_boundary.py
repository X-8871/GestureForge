
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

reference_path = Path(r'D:\codex-worktrees\w4\verification\s1_t02_d2_numeric_reference.py')
sys.path.insert(0, str(reference_path.parent))
import s1_t02_d2_numeric_reference as d2

source_path = Path(__file__)
source_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
reference_sha256 = hashlib.sha256(reference_path.read_bytes()).hexdigest()
rows = []
for m in range(1, 254, 2):
    source_row = [[m, m, m], [m + 1, m + 1, m + 1]] + [[m + 1, m + 1, m + 1] for _ in range(m - 1)]
    resized = d2._resize_bilinear_rgb_values([source_row], 255, 1)
    value = resized[0][1][0]
    normalized = value / 255.0
    scaled = normalized / d2.INPUT_SCALE
    exact_scaled = Fraction(m, 2)
    rows.append({
        'm': m,
        'exact_scaled': str(exact_scaled),
        'exact_q': (m + 1) // 2,
        'resize_value_hex': value.hex(),
        'scaled_hex': scaled.hex(),
        'd2_q': d2.quantize_symmetric(normalized, d2.INPUT_SCALE),
        'float_delta': str(Fraction.from_float(scaled) - exact_scaled),
    })

m = 201
row = [[m, m, m], [m + 1, m + 1, m + 1]] + [[m + 1, m + 1, m + 1] for _ in range(200)]
image = [row for _ in range(329)]
geometry = d2.letterbox_geometry(202, 329, 416, 416)
chw = d2.preprocess_rgb_uint8_to_chw_int8(image, 416, 416)
x = geometry['offset_x'] + 1
value = d2._resize_bilinear_rgb_values([row], 255, 1)[0][1][0]
normalized = value / 255.0
scaled = normalized / d2.INPUT_SCALE
target_case = {
    'src_width': 202,
    'src_height': 329,
    'dst_width': 416,
    'dst_height': 416,
    'geometry': geometry,
    'source_pair': [201, 202],
    'sample_xy': [x, 0],
    'resize_value_hex': value.hex(),
    'normalized_hex': normalized.hex(),
    'scaled_hex': scaled.hex(),
    'exact_scaled': str(Fraction(201, 2)),
    'exact_q': 101,
    'd2_q': chw[0][0][x],
}

result = {
    'schema_version': 1,
    'python_executable': sys.executable,
    'python_version': sys.version,
    'experiment_source_sha256': source_sha256,
    'd2_reference_path': str(reference_path),
    'd2_reference_sha256': reference_sha256,
    'sweep': {
        'case_count': len(rows),
        'm_values': [row['m'] for row in rows],
        'mismatch_count': sum(row['d2_q'] != row['exact_q'] for row in rows),
        'mismatch_m_values': [row['m'] for row in rows if row['d2_q'] != row['exact_q']],
        'below_half_count': sum(float.fromhex(row['scaled_hex']) < row['m'] / 2 for row in rows),
        'equal_half_count': sum(float.fromhex(row['scaled_hex']) == row['m'] / 2 for row in rows),
        'above_half_count': sum(float.fromhex(row['scaled_hex']) > row['m'] / 2 for row in rows),
        'cases': rows,
    },
    'target_416_case': target_case,
}
canonical = json.dumps(result, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
result_sha256 = hashlib.sha256(canonical).hexdigest()
result['canonical_result_sha256'] = result_sha256
result_path = source_path.with_name('result.json')
with result_path.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print('experiment_source_sha256=' + source_sha256)
print('d2_reference_sha256=' + reference_sha256)
print('canonical_result_sha256=' + result_sha256)
print('sweep_cases=' + str(len(rows)))
print('sweep_mismatches=' + str(result['sweep']['mismatch_count']))
print('sweep_mismatch_m_values=' + ','.join(str(value) for value in result['sweep']['mismatch_m_values']))
print('target_416_geometry=' + json.dumps(geometry, sort_keys=True))
print('target_416_exact_q=101 d2_q=' + str(target_case['d2_q']))
