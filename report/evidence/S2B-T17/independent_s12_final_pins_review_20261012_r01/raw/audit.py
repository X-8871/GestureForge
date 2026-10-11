"""独立核对最终pins、恢复映射、源码对象和只读门禁反例。"""
import ast
import hashlib
import importlib
import json
import pathlib
import subprocess
import sys
from unittest.mock import patch

OUT = pathlib.Path(__file__).absolute().parent
ROOT = OUT.parents[3]
WORK = ROOT / 'tmp/2B/S2B-T17/s12_physical_final_prepare_20261012_r02'
PACK = ROOT / 'report/evidence/S2B-T17/s12_source_preflight_20261012_r02'
COMMIT = '09b4c6f60fb74c2fda1b56d2f316ca374dfae7cf'
EXPECTED = {
    'delivery_manifest.json': 'e312b08f61bc1b0a3afe6a52a8a3b80df804b72434c15a498508a03edaff70be',
    'source_freeze.json': '0de84aeabee7b87c5246bba57624e108b8fe32cb0aa5b49a8eb55af7ced3d2a4',
    'source_before.json': '1a70511ecc4587424294458f6073eda6bca81dbae1051d4c2f5806631c597360',
    'tool_binding.json': '66751c4d2fc73bfebf8d067b532fad484808bc175f05b9fad4c40112ccdc28cf',
    'execution_plan_final.json': 'd19551c42c600c307b9459afb205403decc63f928f31d13b34ee4a86a88bec68',
    'author_receipt.json': '7a5cc7dbb5478780b999d5fa4eca6e97cd9f18e460a6fad6fba352fb753e8b74',
    'raw_manifest.jsonl': '3d6d757954e2306fc2d6b67cf92c01654fcf16563d0de8d5967bb7df38413938',
    'recovery_entry.json': '00f9b33ae467c89cf9f06778d80db7baa7cf2e1037be763cd7c9792d4a53f844',
}

def sha(path):
    """流式哈希，只读取明确文件。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    """UTF8读取声明。"""
    return json.loads(path.read_text(encoding='utf-8'))

def save(name, value):
    """独立目录只创建新文件。"""
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def main():
    """执行串行Git与独立门禁，拒绝调用正式写入成功路径。"""
    result = {'frozen': [], 'cases': [], 'git_commands': []}
    for name, expected in EXPECTED.items():
        assert sha(PACK / name) == expected, name
        result['frozen'].append({'path': str(PACK / name), 'sha256': expected})
    manifest = read(PACK / 'delivery_manifest.json')
    for row in manifest['files']:
        path = ROOT / row['path']
        assert path.is_file() and sha(path) == row['sha256'], row['path']
        if 'bytes' in row:
            assert path.stat().st_size == row['bytes'], row['path']
    result['manifest_bindings'] = len(manifest['files'])
    mapping = [json.loads(line) for line in (PACK / 'raw_manifest.jsonl').read_text(encoding='utf-8').splitlines()]
    saved = set()
    for row in mapping:
        original = ROOT / row['original_repo_path']
        archive = ROOT / row['archived_repo_path']
        assert str(original) == row['original_absolute_path'], row
        assert original.stat().st_size == archive.stat().st_size == row['bytes'], row
        assert sha(original) == sha(archive) == row['sha256'], row
        saved.add(row['archived_repo_path'])
    assert len(mapping) == 458 and len(saved) == 202
    result['restore_rows'] = len(mapping)
    result['restore_objects'] = len(saved)
    sys.path.insert(0, str(WORK))
    import compat_pins as p
    import collector as c
    import source_after_check as a
    import impl_collector as impl
    p.require_ready()
    freeze, hashes, static, profile = c.load_freeze()
    assert len(hashes) == 43 and len(static) == 33 and len(freeze['frozen14']) == 14
    assert len(profile['rtl_sources']) == 18 and len(profile['source_derivation']['derived_sources']) == 8
    assert profile['version'] == 's2b-inference-platform/0.1.12'
    assert profile['clock_hz'] == 50000000 and profile['visibility_default'] == 0
    assert sha(p.SOURCE_FREEZE) == EXPECTED['source_freeze.json']
    assert p.SOURCE_PRE == PACK and p.SOURCE_COMMIT == COMMIT
    before = read(PACK / 'source_before.json')
    assert before['source_commit'] == before['actual_head_at_check'] == COMMIT
    assert before['source_sha256'] == hashes and before['static_source_sha256'] == freeze['static_source_sha256']
    assert before['frozen14_sha256'] == freeze['frozen14']
    assert read(p.FUNCTIONAL_G2)['status'] == 'PASS'
    original_freeze = read(ROOT / freeze['functional_precommit_freeze']['path'])
    assert {r['path']: r['sha256'] for r in original_freeze['source_files']} == hashes
    gitdir = OUT / 'git_raw'
    gitdir.mkdir()
    def git(*args):
        command = ['git', '-c', 'core.longpaths=true', '-c', 'maintenance.auto=false', *args]
        process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        number = len(result['git_commands'])
        for suffix, data in (('stdout', process.stdout), ('stderr', process.stderr)):
            (gitdir / (str(number).zfill(2) + '.' + suffix + '.log')).write_bytes(data)
        result['git_commands'].append({'command': command, 'native_exit_code': process.returncode})
        assert process.returncode == 0, (command, process.stderr)
        return process.stdout
    assert git('rev-parse', 'HEAD').decode('ascii').strip() == COMMIT
    relations = {'RAW_IDENTICAL': 0, 'GIT_LF_TO_RAW_CRLF': 0}
    source_checks = []
    for row in before['source_files']:
        path = ROOT / row['path']
        snapshot = ROOT / row['snapshot']
        raw = path.read_bytes()
        assert sha(path) == sha(snapshot) == hashes[row['path']]
        assert path.stat().st_size == snapshot.stat().st_size == row['bytes']
        blob = git('show', COMMIT + ':' + row['path'])
        relation = a.compare_raw(blob, raw)
        assert relation == row['git_relation']
        assert hashlib.sha256(blob).hexdigest() == row['git_blob_sha256']
        relations[relation] += 1
        source_checks.append({'path': row['path'], 'sha256': hashes[row['path']], 'relation': relation})
    assert relations == {'RAW_IDENTICAL': 37, 'GIT_LF_TO_RAW_CRLF': 6}
    assert not git('diff', '--cached', '--name-only').strip()
    assert git('rev-parse', 'HEAD').decode('ascii').strip() == COMMIT
    result['source_checks'] = source_checks
    result['git_relations'] = relations
    binding = read(PACK / 'tool_binding.json')
    oldwork = ROOT / 'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r02'
    for row in binding['tools']:
        path = WORK / row['path']
        assert sha(path) == sha(PACK / 'tools' / row['path']) == row['sha256']
        assert sha(oldwork / row['path']) == row['baseline_sha256']
        if row['path'] != 'compat_pins.py':
            assert path.read_bytes() == (oldwork / row['path']).read_bytes()
    old = ast.parse((oldwork / 'compat_pins.py').read_text(encoding='utf-8'))
    new = ast.parse((WORK / 'compat_pins.py').read_text(encoding='utf-8'))
    functions = lambda tree: [ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert functions(old) == functions(new)
    assert a.COMMON_SHA == impl.COMMON_SHA == binding['common_sha'] == sha(WORK / 'collector.py')
    result['unchanged_functions'] = len(functions(new))
    result['tools'] = binding['tools']
    def case(name, action, reject=False):
        try:
            value = action()
        except (ValueError, AssertionError) as error:
            assert reject, (name, str(error))
            result['cases'].append({'name': name, 'status': 'REJECTED_EXPECTED', 'exception': str(error)})
        else:
            assert not reject, name + '误接受'
            result['cases'].append({'name': name, 'status': 'ACCEPTED', 'detail': value})
    case('实际SYNTH pins', p.require_ready)
    case('PNR None/PENDING', lambda: p.require_ready(pnr=True), True)
    other = '891f750045ce141a8152c96025da559ff1d3a321'
    case('同RAW异source CLI', lambda: c.source(other, 'before'), True)
    case('同RAW异collect CLI', lambda: c.collect(other, OUT / 'missing_gate.json'), True)
    case('同RAW异seal CLI', lambda: c.seal(other, OUT / 'missing_gate.json'), True)
    with patch.object(c, 'git', return_value=(other.encode('ascii'), [])):
        case('实际HEAD不同于固定源', lambda: c.source(COMMIT, 'before'), True)
    original_sha = c.sha
    first = ROOT / next(iter(hashes))
    with patch.object(c, 'sha', side_effect=lambda path: 'f' * 64 if pathlib.Path(path) == first else original_sha(path)):
        case('源SHA漂移', c.load_freeze, True)
    case('固定freeze SHA漂移', lambda: p.pinned(p.SOURCE_FREEZE, '0' * 64), True)
    case('guard实际恢复', lambda: p.resolve_permanent(p.GUARD, p.GUARD_SHA))
    case('supervisor实际恢复', lambda: p.resolve_permanent(p.SUP, p.SUP_SHA))
    case('固定guard SHA漂移', lambda: p.resolve_permanent(p.GUARD, '0' * 64), True)
    case('固定supervisor SHA漂移', lambda: p.resolve_permanent(p.SUP, '0' * 64), True)
    with patch.object(p, 'FUNCTIONAL_G1_SHA', '0' * 64):
        case('功能G1 SHA漂移', p.require_ready, True)
    with patch.object(p, 'FUNCTIONAL_G2_SHA', '0' * 64):
        case('功能G2 SHA漂移', p.require_ready, True)
    with patch.object(p, 'FUNCTIONAL_G2_EXPECTED_STATUS', 'CHANGES_REQUIRED'):
        case('功能G2不是PASS', p.require_ready, True)
    with patch.object(p, 'PNR_CACHE', p.SYNTH_CACHE):
        case('六Run落点重复', p.require_ready, True)
    case('完整RAW接受', lambda: a.compare_raw(b'A\n', b'A\n'))
    case('完整CRLF接受', lambda: a.compare_raw(b'A\nB\n', b'A\r\nB\r\n'))
    case('非EOL拒绝', lambda: a.compare_raw(b'A\n', b'B\r\n'), True)
    case('部分EOL拒绝', lambda: a.compare_raw(b'A\nB\n', b'A\r\nB\n'), True)
    psha = p.sha
    with patch.object(p, 'sha', side_effect=lambda path: '0' * 64 if pathlib.Path(path) == pathlib.Path(p.__file__) else psha(path)):
        case('已加载helper漂移', p.require_ready, True)
    plan = read(PACK / 'execution_plan_final.json')
    assert plan['source_commit'] == COMMIT and plan['actual_session_created'] is False
    assert plan['source_after'] is None and plan['old_s11_budget'] == 'BLOCKED'
    for key in ('sta', 'g3', 'g5', 'actual_budget'):
        assert plan[key] == 'NOT_RUN'
    for phase in ('synth', 'pnr'):
        assert plan[phase]['execution'] == 'NOT_RUN'
        for command in plan[phase]['commands']:
            assert command['executable'] is False and command['execution_status'].startswith('NOT_RUN')
    result['plan_resources'] = plan['resources']
    result['plan_contract'] = plan['required_frozen_contract']
    result['admission_sample'] = plan['resource_admission_actual_sample']
    author = read(PACK / 'author_receipt.json')
    result['author_native'] = [{k: v for k, v in row.items() if k in ('command', 'native_exit_code', 'elapsed_seconds', 'sampled_owned_tree_peak_bytes', 'unknown_samples', 'absolute_tree_peak_bytes', 'continuous_tree_peak_bytes')} for row in author['native_records']]
    result['status'] = 'PASS_INDEPENDENT_RAW_AST_GIT_AND_NEGATIVES'
    save('audit_result.json', result)
    print(json.dumps({'status': result['status'], 'bindings': result['manifest_bindings'], 'restore_rows': len(mapping), 'restore_objects': len(saved), 'source_count': len(hashes), 'git_relations': relations, 'git_calls': len(result['git_commands']), 'cases': len(result['cases'])}, ensure_ascii=False))

if __name__ == '__main__':
    main()
