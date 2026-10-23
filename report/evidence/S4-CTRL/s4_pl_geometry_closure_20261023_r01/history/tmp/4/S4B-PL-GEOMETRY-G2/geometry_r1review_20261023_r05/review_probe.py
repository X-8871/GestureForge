from __future__ import annotations
import ast, copy, hashlib, importlib.util, json, math, os, platform, struct, subprocess, sys, zlib, __future__
from fractions import Fraction
from pathlib import Path

ROOT = Path(r'D:\codex-worktrees\w4')
RUN = Path(os.environ['REVIEW_RUN'])
TMP = Path(os.environ['TEMP'])
MANIFEST = ROOT / 'report/evidence/S4-B/s4b_pl_geometry_g2_20261023_r02/frozen_sources.json'
GEN = ROOT / 'scripts/stage4_s4b/build_s4b_preproc_geometry.py'
TEST = ROOT / 'verification/test_s4b_preproc_geometry.py'
D2 = ROOT / 'verification/s1_t02_d2_numeric_reference.py'
EXPECTED = {
    MANIFEST: '28479466f6d2613e10a9820639daaf825536d0532b04ff918f9c74a06d7a00dc',
    GEN: '8b0d1692b3609c9da255133169bc74c2d141c3b34a37e82549e771bebfde70ef',
    TEST: '383bbae3d716a7288f2acd3e6f57b89858d918150d616d0d155e02fe6fdc9211',
    D2: '6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f',
}
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def f64(bits: str) -> float:
    return struct.unpack('>d', int(bits[2:], 16).to_bytes(8, 'big'))[0]

before = {str(path): sha(path) for path in EXPECTED}
assert before == {str(k): v for k,v in EXPECTED.items()}, before
assert TMP.is_dir() and TMP.is_absolute() and RUN in TMP.parents
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
assert manifest['baseline_commit'] == 'b7aceb8e81fe297511d0581d43c08aabf7df46f9'
assert manifest['repair_round'] == 1
manifest_sources = {item['source_path']: (item['sha256'], item['bytes']) for item in manifest['sources']}
assert manifest_sources == {
    'scripts/stage4_s4b/build_s4b_preproc_geometry.py': (EXPECTED[GEN], GEN.stat().st_size),
    'verification/test_s4b_preproc_geometry.py': (EXPECTED[TEST], TEST.stat().st_size),
}
# Import only after checking all frozen raw-byte hashes.
spec = importlib.util.spec_from_file_location('geometry_repair_r1_review', GEN)
assert spec is not None and spec.loader is not None
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
ref_funcs, ref_sha = geometry.load_verified_d2_geometry_functions(D2)
assert ref_sha == EXPECTED[D2] and set(ref_funcs) == {'letterbox_geometry'}

# Extract needed D2 functions only after checking its full SHA.
tree = ast.parse(D2.read_bytes().decode('utf-8', errors='strict'), filename=str(D2))
function_names = {'_resize_bilinear_rgb_values', '_finite', 'round_away_from_zero', 'saturate_int8', 'quantize_symmetric'}
functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in function_names}
assert set(functions) == function_names and all(not node.decorator_list for node in functions.values())
module = ast.Module(body=[functions[n] for n in sorted(function_names)], type_ignores=[])
ast.fix_missing_locations(module)
namespace = {'__builtins__': {'TypeError':TypeError, 'ValueError':ValueError, 'abs':abs, 'float':float, 'int':int, 'len':len, 'list':list, 'max':max, 'min':min, 'range':range, 'type':type}, 'math':math, 'INT8_MIN':-127, 'INT8_MAX':127}
exec(compile(module, str(D2), 'exec', flags=__future__.annotations.compiler_flag, dont_inherit=True), namespace, namespace)

# Reproduce the specified legal output coordinate with the frozen D2 resize and quantizer.
meta = geometry.build_s4b_preproc_geometry(202,329,416,416)
d2g = ref_funcs['letterbox_geometry'](202,329,416,416)
assert (d2g['new_width'],d2g['new_height'],d2g['offset_x'],d2g['offset_y']) == (255,416,80,0)
entry = meta['axes']['x']['entries'][1]
pixels = [[[0,0,0] for _ in range(202)] for _ in range(329)]
pixels[0][0][0] = 201
pixels[0][1][0] = 202
d2_pixels = namespace['_resize_bilinear_rgb_values'](pixels,255,416)
observed = d2_pixels[0][1][0]
weights_sample = f64(entry['w0bits'])*pixels[0][0][0] + f64(entry['w1bits'])*pixels[0][1][0]
wy0=f64(meta['axes']['y']['entries'][0]['w0bits']); wy1=f64(meta['axes']['y']['entries'][0]['w1bits'])
metadata_sample = wy0*weights_sample + wy1*(f64(meta['axes']['y']['entries'][0]['w0bits'])*pixels[0][0][0] + f64(meta['axes']['y']['entries'][0]['w1bits'])*pixels[1][0][0])
code = namespace['quantize_symmetric'](observed/255.0,1.0/127.0)
assert (meta['padding']['left']+1,meta['padding']['top']) == (81,0)
assert struct.pack('>d',observed) == struct.pack('>d',metadata_sample)
assert struct.pack('>d',observed).hex() == '40693952a54a952a'
assert code == 100
exact=Fraction(201,1)+Fraction(201,254)
exact_q=exact*Fraction(127,255)
assert exact_q == Fraction(201,2) and math.floor(exact_q+Fraction(1,2)) == 101

# Exercise source_length > 1, new_length == 1 outside same-size-copy mode.
small = geometry.build_s4b_preproc_geometry(3,2,2,1)
xe=small['axes']['x']['entries'][0]; ye=small['axes']['y']['entries'][0]
assert small['resize_semantics']['same_size'] is False
assert (xe['i0'],xe['i1'],xe['fracbits']) == (2,2,'0x0000000000000000')
assert (ye['i0'],ye['i1'],ye['fracbits']) == (1,1,'0x0000000000000000')
small_pixels=[[[1,2,3],[4,5,6],[7,8,9]],[[10,11,12],[13,14,15],[16,17,18]]]
small_d2=namespace['_resize_bilinear_rgb_values'](small_pixels,1,1)
assert small_d2 == [[[16.0,17.0,18.0]]]

# Recompute integrity and verify writer rejects rehashed false status/scope/schema/provenance/geometry.
write_cases=[]
original=geometry.build_s4b_preproc_geometry(3,3,5,5)
mutations={
 'status': lambda x:x.__setitem__('status','HARDWARE_READY'),
 'scope': lambda x:x.__setitem__('scope','pixel_processing'),
 'schema': lambda x:x.__setitem__('schema_version',2),
 'reference_sha': lambda x:x['provenance'].__setitem__('reference_sha256','0'*64),
 'generator_sha': lambda x:x['provenance'].__setitem__('generator_sha256','0'*64),
 'geometry': lambda x:x['axes']['x']['entries'][0].__setitem__('i0',2),
}
for label,mutate in mutations.items():
    changed=copy.deepcopy(original); mutate(changed); geometry._attach_integrity(changed)
    out=str(RUN/f'forged_{label}.json')
    try:
        geometry.write_s4b_preproc_geometry(changed,out)
        outcome='accepted'
    except Exception as exc:
        outcome=f'rejected:{type(exc).__name__}'
    write_cases.append({'case':label,'outcome':outcome,'file_created':os.path.lexists(out)})
assert all(x['outcome'].startswith('rejected:') and not x['file_created'] for x in write_cases)

# Exercise the exact prior path problems and Windows alias spellings, without touching non-probe paths.
existing=RUN/'existing.json'; existing.write_bytes(b'review-owned\n')
new_target=RUN/'not_created.json'
path_cases={
 'new_trailing_dot':str(new_target)+'.',
 'existing_trailing_dot':str(existing)+'.',
 'existing_trailing_space':str(existing)+' ',
 'existing_ads':str(existing)+':review_probe',
 'duplicate_separator':str(RUN)+r'\\double_separator.json',
 'dot_segment':str(RUN)+r'\..\escape.json',
 'device_namespace':r'\\.\D:\codex-worktrees\w4\tmp\4\S4B-PL-GEOMETRY-G2\device_probe.json',
}
path_results={}
for label,raw in path_cases.items():
    row={'raw':raw}
    try:
        geometry._validate_absolute_output_path(raw); row['validator']='accepted'
    except Exception as exc:
        row['validator']=f'rejected:{type(exc).__name__}'
    if label != 'device_namespace':
        try:
            geometry.write_s4b_preproc_geometry(original,raw); row['writer']='accepted'
        except Exception as exc:
            row['writer']=f'rejected:{type(exc).__name__}'
    else:
        row['writer']='not_called'
    path_results[label]=row
assert all(row['validator'].startswith('rejected:') for row in path_results.values())
assert path_results['existing_ads']['writer'].startswith('rejected:')
assert existing.read_bytes()==b'review-owned\n'
assert not os.path.lexists(str(existing)+':review_probe')
assert not os.path.lexists(str(new_target))

# Reserved DOS device basenames: validator must reject; do not attempt writes.
reserved={}
for name in ('CON','NUL','AUX','PRN','COM1','LPT9','CON.json','NUL.json'):
    raw=str(RUN/name)
    try:
        geometry._validate_absolute_output_path(raw); reserved[name]='accepted'
    except Exception as exc:
        reserved[name]=f'rejected:{type(exc).__name__}'

# Run frozen test file under explicit isolated TEMP/TMP.
child_env=os.environ.copy(); child_env['TEMP']=str(TMP); child_env['TMP']=str(TMP)
unit=subprocess.run([sys.executable,'-B',str(TEST),'-v'],cwd=str(ROOT),env=child_env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
(RUN/'unit.stdout.txt').write_text(unit.stdout,encoding='utf-8',newline='\n')
(RUN/'unit.stderr.txt').write_text(unit.stderr,encoding='utf-8',newline='\n')

after={str(path):sha(path) for path in EXPECTED}
assert after=={str(k):v for k,v in EXPECTED.items()}, after
result={
 'run_id':RUN.name,'python':sys.executable,'python_version':platform.python_version(),'TEMP':str(TMP),'TMP':str(TMP),
 'frozen_hashes_before':before,'frozen_hashes_after':after,
 'manifest_baseline':manifest['baseline_commit'],'manifest_repair_round':manifest['repair_round'],
 'd2_sha_verified_before_ast':ref_sha,
 'counterexample':{'output_xy':[81,0],'source_neighbor_values':[201,202],'d2_float_hex':observed.hex(),'d2_quantized_code':code,'metadata_float_hex':metadata_sample.hex(),'exact_rational_quantized':str(exact_q),'ideal_tie_away_code':101},
 'new_dimension_one':{'new_size':small['new_size'],'x_indices':[xe['i0'],xe['i1']],'y_indices':[ye['i0'],ye['i1']],'d2_pixel':small_d2[0][0]},
 'writer_rehashed_mutations':write_cases,'path_cases':path_results,'reserved_dos_names':reserved,
 'unit_tests':{'exit':unit.returncode,'run_line':next((l.strip() for l in unit.stderr.splitlines() if l.strip().startswith('Ran ')),None),'result_line':next((l.strip() for l in unit.stderr.splitlines() if l.strip()=='OK' or l.strip().startswith('FAILED')),None)}
}
(RUN/'review_results.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
print('REVIEW_PROBE_EXIT=0')
print(f'UNIT_TEST_EXIT={unit.returncode}')