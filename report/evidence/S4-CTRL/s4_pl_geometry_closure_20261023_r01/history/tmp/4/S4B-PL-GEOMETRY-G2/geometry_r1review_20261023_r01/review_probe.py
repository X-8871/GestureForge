from __future__ import annotations
import ast, copy, hashlib, importlib.util, json, math, os, platform, struct, subprocess, sys, zlib
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

before = {p: sha(Path(p)) for p in EXPECTED}
assert before == EXPECTED, f'frozen SHA mismatch: {before}'
assert TMP.is_dir() and TMP.is_absolute() and RUN in TMP.parents
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
assert manifest['baseline_commit'] == 'b7aceb8e81fe297511d0581d43c08aabf7df46f9'
assert {x['source_path']: x['sha256'] for x in manifest['sources']} == {
    'scripts/stage4_s4b/build_s4b_preproc_geometry.py': EXPECTED[str(GEN)],
    'verification/test_s4b_preproc_geometry.py': EXPECTED[str(TEST)],
}
# Import only after the generator, test, manifest, and D2 raw-byte hashes match.
spec = importlib.util.spec_from_file_location('frozen_geometry_review_target', GEN)
assert spec is not None and spec.loader is not None
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
refs, ref_sha = geometry.load_verified_d2_geometry_functions(D2)
assert ref_sha == EXPECTED[str(D2)] and set(refs) == {'letterbox_geometry'}

# Extract only specific D2 functions after verifying the raw file hash.
d2_bytes = D2.read_bytes()
tree = ast.parse(d2_bytes.decode('utf-8', errors='strict'), filename=str(D2))
names = {'_finite', 'round_away_from_zero', 'saturate_int8', 'quantize_symmetric', '_resize_bilinear_rgb_values'}
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
assert {n.name for n in nodes} == names and all(not n.decorator_list for n in nodes)
mod = ast.Module(body=nodes, type_ignores=[])
ast.fix_missing_locations(mod)
ns = {'__builtins__': {'ValueError': ValueError, 'TypeError': TypeError, 'float': float, 'int': int, 'abs': abs, 'max': max, 'min': min, 'len': len, 'list': list, 'range': range}, 'math': math, 'INT8_MIN': -127, 'INT8_MAX': 127}
exec(compile(mod, str(D2), 'exec', flags=0, dont_inherit=True), ns, ns)