from __future__ import annotations
import ast, copy, hashlib, importlib.util, json, math, os, platform, struct, subprocess, sys, zlib, __future__
from fractions import Fraction
from pathlib import Path

ROOT = Path(os.environ['W4_ROOT'])
RUN = Path(os.environ['REVIEW_RUN'])
TMP = Path(os.environ['TEMP'])
MANIFEST = ROOT / 'report/evidence/S4-B/s4b_pl_geometry_g2_20261023_r01/frozen_sources.json'
GEN = ROOT / 'scripts/stage4_s4b/build_s4b_preproc_geometry.py'
TEST = ROOT / 'verification/test_s4b_preproc_geometry.py'
D2 = ROOT / 'verification/s1_t02_d2_numeric_reference.py'
DEV_EVIDENCE = ROOT / 'report/evidence/S4-B/s4b_pl_geometry_20261023_r02/geometry_run_evidence.json'
EXPECTED = {
    str(MANIFEST): '544cd0ab3044661113116fc492edc8fab82aebdfa0afcd73521d9231dc757a76',
    str(GEN): 'c3d8029c3c4bbbdac3a299166c3324a48e595076673a1013d34cfeb881ec0140',
    str(TEST): 'd2bb38a7e9ad048e05a3a3d058360af84cd3b342b680589041dc0acb1a21c8f2',
    str(D2): '6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f',
}
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def f64(bits: str) -> float:
    return struct.unpack('>d', int(bits, 16).to_bytes(8, 'big'))[0]

before = {p: sha(Path(p)) for p in EXPECTED}
assert before == EXPECTED, f'frozen SHA mismatch: {before}'
assert TMP.is_dir() and TMP.is_absolute() and RUN in TMP.parents
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
assert manifest['baseline_commit'] == 'b7aceb8e81fe297511d0581d43c08aabf7df46f9'
assert {x['source_path']: x['sha256'] for x in manifest['sources']} == {
    'scripts/stage4_s4b/build_s4b_preproc_geometry.py': EXPECTED[str(GEN)],
    'verification/test_s4b_preproc_geometry.py': EXPECTED[str(TEST)],
}
# Import after raw-byte hashes for all frozen sources and D2 match.
spec = importlib.util.spec_from_file_location('frozen_geometry_review_target', GEN)
assert spec is not None and spec.loader is not None
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
refs, ref_sha = geometry.load_verified_d2_geometry_functions(D2)
assert ref_sha == EXPECTED[str(D2)] and set(refs) == {'letterbox_geometry'}

# Extract only D2 functions after verifying the full reference file SHA.
tree = ast.parse(D2.read_bytes().decode('utf-8', errors='strict'), filename=str(D2))
names = {'_finite', 'round_away_from_zero', 'saturate_int8', 'quantize_symmetric', '_resize_bilinear_rgb_values'}
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
assert {n.name for n in nodes} == names and all(not n.decorator_list for n in nodes)
mod = ast.Module(body=nodes, type_ignores=[])
ast.fix_missing_locations(mod)
ns = {'__builtins__': {'ValueError': ValueError, 'TypeError': TypeError, 'float': float, 'int': int, 'abs': abs, 'max': max, 'min': min, 'len': len, 'list': list, 'range': range}, 'math': math, 'INT8_MIN': -127, 'INT8_MAX': 127}
exec(compile(mod, str(D2), 'exec', flags=__future__.annotations.compiler_flag, dont_inherit=True), ns, ns)

# Verify geometry, exact D2 binary64 order, and the specified quantization boundary.
meta = geometry.build_s4b_preproc_geometry(202, 329, 416, 416)
d2geom = refs['letterbox_geometry'](202, 329, 416, 416)
assert meta['status'] == 'DRAFT_GEOMETRY_ONLY_NOT_FOR_HARDWARE'
assert (d2geom['new_width'], d2geom['new_height'], d2geom['offset_x'], d2geom['offset_y']) == (255, 416, 80, 0)
assert meta['new_size'] == {'width': 255, 'height': 416}
assert meta['padding']['left'] == 80 and meta['padding']['right'] == 81
entry = meta['axes']['x']['entries'][1]
scale = (202 - 1) / (255 - 1)
sx = 1 * scale
i0 = int(sx)
frac = sx - i0
w0 = 1.0 - frac
w1 = frac
assert (entry['i0'], entry['i1']) == (0, 1)
assert entry['fracbits'] == f'0x{struct.unpack(">Q", struct.pack(">d", frac))[0]:016x}'
assert entry['w0bits'] == f'0x{struct.unpack(">Q", struct.pack(">d", w0))[0]:016x}'
assert entry['w1bits'] == f'0x{struct.unpack(">Q", struct.pack(">d", w1))[0]:016x}'
# One synthetic row suffices: D2 uses the same x scale at legal output (81,0).
pixels = [[[201, 0, 0], [202, 0, 0]] + [[0, 0, 0] for _ in range(200)]]
d2_pixels = ns['_resize_bilinear_rgb_values'](pixels, 255, 1)
d2_value = d2_pixels[0][1][0]
metadata_value = f64(entry['w0bits']) * 201 + f64(entry['w1bits']) * 202
assert metadata_value == d2_value
normalized = max(0.0, min(1.0, d2_value / 255.0))
d2_code = ns['quantize_symmetric'](normalized, 1.0 / 127.0)
ideal_value = Fraction(201) + Fraction(201, 254)
ideal_code_value = ideal_value * Fraction(127, 255)
assert ideal_code_value == Fraction(201, 2)
ideal_away_code = math.floor(float(ideal_code_value) + 0.5)
assert d2_code == 100 and ideal_away_code == 101

# Independently recompute the canonical digest and its source bindings.
canonical_payload = {k: v for k, v in meta.items() if k != 'integrity'}
canonical = json.dumps(canonical_payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
ind_sha = hashlib.sha256(canonical).hexdigest()
ind_crc = f'0x{zlib.crc32(canonical) & 0xffffffff:08x}'
assert meta['integrity']['canonical_sha256'] == ind_sha
assert meta['integrity']['canonical_crc32'] == ind_crc
assert meta['provenance']['reference_sha256'] == EXPECTED[str(D2)]
assert meta['provenance']['generator_sha256'] == EXPECTED[str(GEN)]

# Verify the developer's exact CLI artifact if it still exists.
dev = json.loads(DEV_EVIDENCE.read_text(encoding='utf-8'))
cli_path = Path(dev['generated_cli_output']['path'])
cli_check = {'path': str(cli_path), 'exists': cli_path.is_file()}
if cli_path.is_file():
    cli_bytes = cli_path.read_bytes()
    cli_meta = json.loads(cli_bytes.decode('utf-8'))
    cli_check.update({'sha256': hashlib.sha256(cli_bytes).hexdigest(), 'expected_sha256': dev['generated_cli_output']['sha256'], 'status': cli_meta.get('status'), 'reference_sha256': cli_meta.get('provenance', {}).get('reference_sha256'), 'generator_sha256': cli_meta.get('provenance', {}).get('generator_sha256'), 'integrity_valid': geometry.verify_metadata_integrity(cli_meta), 'bytes': len(cli_bytes)})
    assert cli_check['sha256'] == cli_check['expected_sha256']
    assert cli_check['status'] == 'DRAFT_GEOMETRY_ONLY_NOT_FOR_HARDWARE'
    assert cli_check['reference_sha256'] == EXPECTED[str(D2)]
    assert cli_check['generator_sha256'] == EXPECTED[str(GEN)]
    assert cli_check['integrity_valid']

# Probe overwrite aliases only inside this disposable review RunId.
probe_meta = geometry.build_s4b_preproc_geometry(3, 3, 5, 5)
canonical_path = RUN / 'existing.json'
geometry.write_s4b_preproc_geometry(probe_meta, str(canonical_path))
original_bytes = canonical_path.read_bytes()
alias_paths = {
    'case_variant': str(canonical_path.parent).upper() + '\\' + canonical_path.name.upper(),
    'trailing_dot': str(canonical_path) + '.',
    'repeated_separator': str(canonical_path.parent) + '\\\\' + canonical_path.name,
    'alternate_data_stream': str(canonical_path) + ':review_probe',
}
alias_results = {}
for label, alias in alias_paths.items():
    row = {'input': alias}
    try:
        geometry._validate_absolute_output_path(alias)
        row['validator'] = 'accepted'
        try:
            geometry.write_s4b_preproc_geometry(probe_meta, alias)
            row['writer'] = 'accepted'
        except Exception as exc:
            row['writer'] = f'rejected:{type(exc).__name__}:{exc}'
    except Exception as exc:
        row['validator'] = f'rejected:{type(exc).__name__}:{exc}'
        row['writer'] = 'not_called'
    try:
        row['lexists_after'] = os.path.lexists(alias)
    except OSError as exc:
        row['lexists_after'] = f'error:{type(exc).__name__}'
    try:
        row['samefile_as_existing'] = os.path.samefile(alias, canonical_path) if os.path.lexists(alias) else False
    except OSError:
        row['samefile_as_existing'] = None
    alias_results[label] = row
assert canonical_path.read_bytes() == original_bytes

# Check whether the public writer enforces the draft-only status invariant.
tampered = copy.deepcopy(probe_meta)
tampered['status'] = 'HARDWARE_READY'
geometry._attach_integrity(tampered)
status_path = RUN / 'status_tamper_probe.json'
status_writer = 'rejected'
try:
    geometry.write_s4b_preproc_geometry(tampered, str(status_path))
    status_writer = 'accepted'
except Exception as exc:
    status_writer = f'rejected:{type(exc).__name__}:{exc}'

# Run frozen unit tests with explicit TEMP/TMP under this RunId.
child_env = os.environ.copy()
child_env['TEMP'] = str(TMP)
child_env['TMP'] = str(TMP)
unit = subprocess.run([sys.executable, '-B', str(TEST), '-v'], cwd=str(ROOT), env=child_env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
(RUN / 'unit.stdout.txt').write_text(unit.stdout, encoding='utf-8', newline='\n')
(RUN / 'unit.stderr.txt').write_text(unit.stderr, encoding='utf-8', newline='\n')

result = {
    'run_id': RUN.name,
    'python': sys.executable,
    'python_version': platform.python_version(),
    'TEMP': str(TMP),
    'TMP': str(TMP),
    'frozen_hashes_before': before,
    'frozen_hashes_after': {p: sha(Path(p)) for p in EXPECTED},
    'manifest_baseline': manifest['baseline_commit'],
    'd2_reference_sha_verified_before_ast': ref_sha,
    'd2_edge': {'output_xy': [81, 0], 'offset': [80, 0], 'local_xy': [1, 0], 'scale_x': scale.hex(), 'sample_position': sx.hex(), 'frac': frac.hex(), 'd2_binary64_value': d2_value.hex(), 'metadata_binary64_value': metadata_value.hex(), 'normalized_binary64': normalized.hex(), 'd2_quantized_code': d2_code, 'exact_rational_value': str(ideal_value), 'exact_rational_quantized_value': str(ideal_code_value), 'ideal_tie_away_code': ideal_away_code},
    'canonical_integrity_independent': {'sha256': ind_sha, 'crc32': ind_crc, 'matches_metadata': True, 'reference_binding': meta['provenance']['reference_sha256'], 'generator_binding': meta['provenance']['generator_sha256']},
    'developer_cli_artifact': cli_check,
    'overwrite_alias_probes': alias_results,
    'recomputed_status_mutation_writer_result': status_writer,
    'unit_tests': {'returncode': unit.returncode, 'passed_line': next((x for x in unit.stderr.splitlines() if 'Ran ' in x), None), 'result_line': next((x for x in unit.stderr.splitlines() if x.strip() in {'OK'} or x.strip().startswith('FAILED')), None)},
}
assert result['frozen_hashes_after'] == EXPECTED
(RUN / 'review_results.json').write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
print(f'UNIT_TEST_EXIT={unit.returncode}')
print(f'UNIT_TEST_STDERR={RUN / "unit.stderr.txt"}')