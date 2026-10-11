"""只读机器包装检查和已审COMPAT来源核对，逐项保留原生命令。"""
import ast
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import zipfile
import psutil

OUT = pathlib.Path(__file__).absolute().parent
ROOT = OUT.parents[3]
PACK = ROOT / 'report/evidence/S2B-T17/s12_source_preflight_20261012_r02'
WORK = ROOT / 'tmp/2B/S2B-T17/s12_physical_final_prepare_20261012_r02'

def read(path):
    """UTF8读取固定源。"""
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    """轻量流式绑定。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

result = {'native_records': []}
for mode, expected in (('evidence', 0), ('inputs', 2)):
    command = [sys.executable, '-X', 'utf8', '-B', str(ROOT / 'verification/check_stage_delivery.py'), '--mode', mode, '--manifest', str(PACK / 'delivery_manifest.json'), '--project-root', str(ROOT)]
    start = time.monotonic()
    peak = samples = unknown = 0
    with (OUT / ('checker_' + mode + '.stdout.log')).open('xb') as stdout, (OUT / ('checker_' + mode + '.stderr.log')).open('xb') as stderr:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
        process = psutil.Process(child.pid)
        while child.poll() is None:
            rss = 0
            try:
                members = [process] + process.children(recursive=True)
                for member in members:
                    try:
                        rss += member.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        unknown += 1
                samples += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                unknown += 1
            peak = max(peak, rss)
            if peak > 268435456 or time.monotonic() - start > 120:
                child.kill()
                raise RuntimeError('只读checker超过256MiB/120秒')
            time.sleep(0.02)
        code = child.wait()
    native = {'command': command, 'cwd': str(ROOT), 'native_exit_code': code, 'expected_exit_code': expected, 'elapsed_seconds': time.monotonic() - start, 'sampled_owned_tree_peak_bytes': peak, 'unknown_samples': unknown, 'samples': samples, 'sample_interval_seconds': 0.02, 'absolute_tree_peak_bytes': None}
    result['native_records'].append(native)
    with (OUT / ('checker_' + mode + '.native.json')).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(native, f, ensure_ascii=False, indent=2)
        f.write('\n')
    assert code == expected, native
    stdout_text = (OUT / ('checker_' + mode + '.stdout.log')).read_text(encoding='utf-8')
    assert ('CHECKS_OK' if mode == 'evidence' else 'CHECKS_FAILED') in stdout_text

compat = ROOT / 'report/evidence/S2B-T17/s12_physical_compat_delivery_20261012_r01'
result['compat_manifest_sha256'] = sha(compat / 'delivery_manifest.json')
assert result['compat_manifest_sha256'].startswith('94814f466')
with zipfile.ZipFile(compat / 'review_r02.zip') as z:
    name = 'tmp/2B/S2B-T17/independent_s12_physical_compat_review_20261012_r02/final_review_receipt.json'
    raw = z.read(name)
    review = json.loads(raw.decode('utf-8'))
    result['compat_review_receipt_sha256'] = hashlib.sha256(raw).hexdigest()
    assert result['compat_review_receipt_sha256'].startswith('018c5773')
    assert review['status'] == 'PASS_COMPAT_LOGIC_G2_ONLY'
    result['compat_review_status'] = review['status']
    for row in review['reviewed_files']:
        if row['path'] != 'compat_pins.py':
            assert sha(WORK / row['path']) == row['sha256']

plan = read(PACK / 'execution_plan_final.json')
resources = plan['resources']
expected_resources = {'launch_jobs': 1, 'general_maxThreads': 1, 'simultaneous_heavy': 1, 'tree_rss_limit_bytes': 6442450944, 'minimum_available_ram_before_owned_session_bytes': 4831838208, 'available_ram_stop_bytes': 536870912, 'c_disk_free_stop_and_admission_bytes': 8589934592, 'guard_interval_seconds': 1, 'no_log_progress_stop_seconds': 900, 'supervisor_live_interval_seconds': 5}
for k, v in expected_resources.items():
    assert resources[k] == v, (k, resources[k])
result['resources_verified'] = expected_resources
contract = plan['required_frozen_contract']
assert contract['part'] == 'xc7z020clg400-2' and contract['clock_hz'] == 50000000
oldwork = ROOT / 'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r02'
def assignments(path):
    """只比较顶层赋值AST，函数已由独立主脚本逐字结构核对。"""
    output = {}
    for node in ast.parse(path.read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            output[node.targets[0].id] = ast.dump(node.value, include_attributes=False)
    return output
old = assignments(oldwork / 'compat_pins.py')
new = assignments(WORK / 'compat_pins.py')
result['changed_top_level_assignments'] = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
assert set(result['changed_top_level_assignments']) == {'SOURCE_COMMIT', 'SOURCE_FREEZE', 'SOURCE_FREEZE_SHA', 'FUNCTIONAL_G1', 'FUNCTIONAL_G1_SHA', 'FUNCTIONAL_G2', 'FUNCTIONAL_G2_SHA', 'FUNCTIONAL_G2_EXPECTED_STATUS', 'SOURCE_PRE', 'SYNTH_CACHE', 'PNR_CACHE', 'PROJECT', 'SYNTH_REPORT', 'PNR_REPORT'}
first = ROOT / 'tmp/2B/S2B-T17/s12_physical_final_prepare_20261012_r01'
generation = read(first / 'generation.native.json')
wrapper = read(first / 'source_before_wrapper_failure.json')
assert generation['native_exit_code'] == 1
assert 'profile["version"] == "0.1.12"' in (first / 'generation.stderr.bin').read_text(encoding='utf-8')
assert wrapper['outer_shell_exit_code'] == 1 and wrapper['child_native_exit_code'] is None
source_native = read(WORK / 'source_before.native.json')
assert source_native['native_exit_code'] == 0 and source_native['sampled_owned_tree_peak_bytes'] == 128966656
assert source_native['unknown_samples'] == 1 and source_native['absolute_tree_peak_bytes'] is None
test = read(PACK / 'final_pins_test_receipt.json')
assert test['case_count'] == len(test['cases']) == 19 and test['status'] == 'PASS_FINAL_PINS_LOGIC_G1_ONLY'
test_native = read(WORK / 'logic_tests.native.json')
assert test_native['native_exit_code'] == 0
result['developer_tests'] = {'cases': 19, 'native_exit_code': 0, 'elapsed_seconds': test_native['elapsed_seconds'], 'source_before_native_exit_code': 0, 'source_before_elapsed_seconds': source_native['elapsed_seconds'], 'source_before_unknown_samples': 1}
result['historical_failures'] = {'first_profile_generation_native_exit_code': 1, 'first_128MiB_wrapper_exit_code': 1, 'first_child_native_exit_code': None, 'reclassified_as_pass': False}
result['status'] = 'PASS_READONLY_WRAPPING_PROVENANCE_AND_PLAN'
with (OUT / 'supplement_result.json').open('x', encoding='utf-8', newline='\n') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(result, ensure_ascii=False))
