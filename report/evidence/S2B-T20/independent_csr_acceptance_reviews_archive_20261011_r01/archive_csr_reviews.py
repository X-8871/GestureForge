"""归档T20两轮独审原字节，保留软件审查与实板边界。"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = pathlib.Path(__file__).resolve().parent
ARCHIVE = ROOT / 'report/evidence/S2B-T20/independent_csr_acceptance_reviews_archive_20261011_r01'
REVIEW_BASE = ROOT / 'tmp/2B/S2B-T20'
SHA_R1 = '97f7479abe00e0d5463a7038b0fd0a7dd0a86e5288b27d1a5ba875e1d2b88b70'
SHA_R2 = '53a5f431120d9190f4682150c16ba8825d46d28627b1b19575c0fa4e7d3650ec'
SHA_MAIN = 'b13f49452e788e5ca6d7843addf0b2f9cba420edaa3cd79c189455740448379f'
SHA_STAGE = 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf'

def sha(path):
    """分块读取原字节，不转码或复制大数据。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def checked(path, expected):
    """核对真实完整路径、文件类型、范围及哈希。"""
    path = pathlib.Path(path)
    if not path.is_absolute():
        path = ROOT / path
    assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT), str(path)
    assert sha(path) == expected, str(path)
    return path

def save(path, data):
    """只创建新文件，禁止覆盖失败原件。"""
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def copy(source, target):
    assert source.is_file() and not source.is_symlink() and not target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.parent.is_symlink()
    shutil.copyfile(source, target)
    assert sha(source) == sha(target) and source.stat().st_size == target.stat().st_size

def bind(path, role):
    return {'path': rel(path), 'sha256': sha(path), 'role': role}

def packaging(manifest, prefix):
    """只执行固定包装检查器，不运行任何业务测试。"""
    stage = checked('verification/check_stage_delivery.py', SHA_STAGE)
    records = []
    for mode, expected in [('evidence', 0), ('inputs', 2)]:
        cmd = [sys.executable, '-X', 'utf8', '-B', str(stage), '--mode', mode, '--manifest', str(manifest), '--project-root', str(ROOT)]
        start = time.perf_counter()
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        logs = []
        for suffix, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
            p = TMP / f'{prefix}_{mode}.{suffix}.log'
            with p.open('xb') as f:
                f.write(raw)
            logs.append({'path': rel(p), 'sha256': sha(p), 'bytes': p.stat().st_size})
        parsed = json.loads(result.stdout.decode('utf-8'))
        assert result.returncode == expected, parsed
        if mode == 'evidence':
            assert parsed['errors'] == [] and parsed['warnings'] == []
        records.append({'command': cmd, 'native_exit_code': result.returncode, 'seconds': time.perf_counter() - start, 'closed_logs': logs, 'result': parsed})
    return records

def collect():
    start = time.perf_counter()
    assert ARCHIVE.parent.is_dir() and not ARCHIVE.parent.is_symlink() and not ARCHIVE.exists()
    reviews = []
    for index, expected, count, status in [(1, SHA_R1, 39, 'CHANGES_REQUIRED'), (2, SHA_R2, 60, 'PASS')]:
        review = REVIEW_BASE / f'independent_csr_acceptance_review_20261011_r0{index}'
        assert review.is_dir() and not review.is_symlink()
        rp = checked(review / 'review_receipt.json', expected)
        receipt = json.loads(rp.read_text(encoding='utf-8'))
        assert receipt['status'] == status and receipt['reviewer_write_state'] == 'STOP_AFTER_RECEIPT'
        assert len(receipt['artifacts']) == count
        reviews.append((index, review, rp, receipt))
    r1 = reviews[0][3]
    r2 = reviews[1][3]
    assert r2['approval_scope'] == 'SOFTWARE_G2_ONLY' and r2['previous_review_preserved']['sha256'] == SHA_R1
    mainp = checked('report/evidence/S2B-T20/csr_acceptance_20261011_r03/delivery_manifest_r02.json', SHA_MAIN)
    main = json.loads(mainp.read_text(encoding='utf-8'))
    oldrelative = 'report/evidence/S2B-T20/csr_acceptance_20261011_r01/delivery_manifest_r03.json'
    oldp = checked(oldrelative, r1['frozen_raw_sha256'][oldrelative])
    old = json.loads(oldp.read_text(encoding='utf-8'))
    deps = {}
    historical = []
    for x in old['files']:
        if x['path'] in ['verification/s2b_csr_board_acceptance.py', 'verification/test_s2b_csr_board_acceptance.py']:
            p = checked(oldp.parent / 'source_snapshot' / pathlib.Path(x['path']).name, x['sha256'])
            historical.append({'old_source_path': x['path'], 'old_sha256': x['sha256'], 'preserved_snapshot': rel(p), 'raw_snapshot_equal': True, 'current_source_required_to_match_old': False})
        else:
            p = checked(x['path'], x['sha256'])
        deps[rel(p)] = bind(p, 'input')
    for x in main['files']:
        p = checked(x['path'], x['sha256'])
        deps[rel(p)] = bind(p, 'input')
    for p in [mainp, oldp, checked('verification/check_stage_delivery.py', SHA_STAGE)]:
        deps[rel(p)] = bind(p, 'input')
    for x in main['interfaces']:
        checked(x['path'], x['sha256'])
    for path, expected in r2['frozen_raw_sha256'].items():
        checked(path, expected)
    prep = r2['actual_prepared_assets']['preparation']
    p = checked(prep['path'], prep['sha256'])
    assert prep['sha256'] == '3d87b85e2e46becde90be7a071eb094d6dfb6b559d0301ece6333460a3a502cb' and p.stat().st_size == prep['bytes']
    deps[rel(p)] = bind(p, 'input')
    ARCHIVE.mkdir()
    mapping = []
    for index, review, rp, receipt in reviews:
        rows = receipt['artifacts'] + [{'path': str(rp), 'sha256': sha(rp), 'bytes': rp.stat().st_size}]
        seen = set()
        for x in rows:
            path = pathlib.Path(x['path'])
            source = checked(path if path.is_absolute() else review / path, x['sha256'])
            assert source.resolve().is_relative_to(review) and source.stat().st_size == x['bytes']
            inner = source.relative_to(review)
            assert 'obj_dir' not in inner.parts and inner not in seen
            seen.add(inner)
            dest = ARCHIVE / f'r0{index}' / inner
            copy(source, dest)
            mapping.append({'round': index, 'source': rel(source), 'copy': rel(dest), 'sha256': x['sha256'], 'bytes': x['bytes'], 'raw_bytes_equal': True})
    copy(TMP / 'archive_csr_reviews.py', ARCHIVE / 'archive_csr_reviews.py')
    save(ARCHIVE / 'raw_copy_mapping.json', {'schema_version': 1, 'copies': mapping, 'count': len(mapping), 'bytes': sum(x['bytes'] for x in mapping), 'originals_retained': True, 'unbound_mock_or_build_cache_copied': False})
    save(ARCHIVE / 'historical_source_binding.json', {'policy': 'R1旧源码原字节按已冻结snapshot核验；R2源码按新SHA核验。', 'historical_sources': historical, 'r2_source_bindings': r2['frozen_raw_sha256'], 'developer_manifest': {'path': rel(mainp), 'sha256': SHA_MAIN}})
    save(ARCHIVE / 'archive_result.json', {'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'approval_scope': 'SOFTWARE_G2_ONLY',
        'rounds': [{'round': index, 'receipt': rel(rp), 'sha256': sha(rp), 'status': receipt['status'], 'native_commands': receipt['native_commands'], 'limitations': receipt['limitations']} for index, review, rp, receipt in reviews],
        'r1_failures_preserved': True, 'copies': len(mapping), 'raw_copy_bytes': sum(x['bytes'] for x in mapping),
        'r2_actual_prepared_assets': r2['actual_prepared_assets'], 'r2_original_resources': r2['resources'],
        'collector_peak_memory': 'NOT_MEASURED', 'board': 'NOT_RUN', 'busy': 'BLOCKED', 'same_wire_hot_recovery': 'BLOCKED',
        'visibility_fullcompat_cache_g3': 'NOT_APPROVED', 'large_prepared_assets_recopied_or_reverified': False})
    m = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T20', 'run_id': ARCHIVE.name, 'source_commit': main['source_commit'],
         'evidence_dir': rel(ARCHIVE), 'interfaces': main['interfaces'], 'files': list(deps.values()),
         'tool_versions': {'python': sys.version, 'stage_checker_sha256': SHA_STAGE}, 'checks': [
             {'name': 'R2原实际软件回归', 'status': 'PASS', 'command': subprocess.list2cmdline(r2['native_commands']['suite']['command']), 'exit_code': r2['native_commands']['suite']['native_exit_code'], 'reason': '仅原33mock方法/30subcase，11独立历史与非空手算另在原收据；不重跑。'},
             {'name': '原G1历史失败', 'status': 'FAIL', 'command': 'python -B report/evidence/S2B-T20/csr_acceptance_20261011_r01/run_mock_regression.py', 'exit_code': 1, 'reason': '原清单实际历史失败保留，不改判。'},
             {'name': '实物/visibility/fullcompat/G3', 'status': 'NOT_RUN', 'command': None, 'exit_code': None, 'reason': '原R2仅软件G2，不批准实物或运行兼容性。'},
             {'name': 'busy与旧wire热恢复', 'status': 'BLOCKED', 'command': None, 'exit_code': None, 'reason': '原明确阻断保持；归档不执行设备操作。'}],
         'limitations': ['R1 CHANGES_REQUIRED与R2 SOFTWARE_G2_ONLY均原样保留；包装CHECKS_OK仅文件完整性。', 'R1旧两源只绑定原snapshot，不误要求当前R2源码等于R1；原main与依赖均input绑定，不改任何原目录。', '仅复制receipt已绑定39+60原件及两收据，不扫未绑定mock/buildcache。真实T18 preparation仅按原SHA绑定，不重复制大资产或声称实板。', 'collector峰内存未测；R2套件243068928B是原Reviewer测量，不是Collector峰。', '最终动态stdout在隔离tmp关闭后核验；物理候选未冻结，inputs2不得称inputs通过。']}
    for p in sorted(ARCHIVE.rglob('*')):
        if p.is_file():
            m['files'].append(bind(p, 'source' if p.name == 'archive_csr_reviews.py' else 'log' if p.suffix == '.log' else 'result'))
    save(ARCHIVE / 'delivery_manifest_r01.json', m)
    commands = packaging(ARCHIVE / 'delivery_manifest_r01.json', 'initial')
    save(TMP / 'initial_packaging_result.json', {'commands': commands})
    save(TMP / 'collector_inner_result.json', {'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'copies': len(mapping), 'bytes': sum(x['bytes'] for x in mapping), 'seconds': time.perf_counter() - start})
    print(json.dumps({'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'copies': len(mapping), 'seconds': time.perf_counter() - start}))

def seal():
    start = time.perf_counter()
    for name in ['collector_native.json', 'collector.stdout.log', 'collector.stderr.log', 'collector_inner_result.json', 'initial_packaging_result.json', 'initial_evidence.stdout.log', 'initial_evidence.stderr.log', 'initial_inputs.stdout.log', 'initial_inputs.stderr.log']:
        copy(TMP / name, ARCHIVE / name)
    m = json.loads((ARCHIVE / 'delivery_manifest_r01.json').read_text(encoding='utf-8'))
    m['files'] = [x for x in m['files'] if not x['path'].startswith(rel(ARCHIVE) + '/')]
    native = json.loads((ARCHIVE / 'collector_native.json').read_text(encoding='utf-8'))
    assert native['native_exit_code'] == 0
    m['checks'].append({'name': '实际原字节Collector', 'status': 'PASS', 'command': subprocess.list2cmdline(native['command']), 'exit_code': 0, 'reason': '101原件逐文件SHA和长度一致，不复制未绑定缓存。'})
    for p in sorted(ARCHIVE.rglob('*')):
        if p.is_file():
            m['files'].append(bind(p, 'source' if p.name == 'archive_csr_reviews.py' else 'log' if p.suffix == '.log' else 'result'))
    mp = ARCHIVE / 'delivery_manifest_r02.json'
    save(mp, m)
    commands = packaging(mp, 'final')
    for x in m['files'] + m['interfaces']:
        checked(x['path'], x['sha256'])
    mapping = json.loads((ARCHIVE / 'raw_copy_mapping.json').read_text(encoding='utf-8'))
    for x in mapping['copies']:
        source = checked(x['source'], x['sha256'])
        dest = checked(x['copy'], x['sha256'])
        assert source.stat().st_size == dest.stat().st_size == x['bytes']
    files = [p for p in ARCHIVE.rglob('*') if p.is_file()]
    result = {'status': 'STOP_PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'scope': 'SOFTWARE_G2_ONLY', 'manifest': rel(mp), 'manifest_sha256': sha(mp),
              'files_bindings': len(m['files']), 'interface_bindings': len(m['interfaces']), 'total_bindings': len(m['files']) + len(m['interfaces']),
              'archive_files': len(files), 'archive_bytes': sum(p.stat().st_size for p in files), 'raw_copies': mapping['count'], 'raw_copy_bytes': mapping['bytes'],
              'all_raw_copies_equal': True, 'all_final_bindings_verified': True, 'commands': commands, 'seconds': time.perf_counter() - start,
              'collector_peak_memory': 'NOT_MEASURED', 'root_file_list': sorted(p.relative_to(ARCHIVE).as_posix() for p in files), 'hardware': 'NOT_RUN'}
    save(TMP / 'final_status.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['commands', 'root_file_list']}))

if __name__ == '__main__':
    phase = sys.argv[1]
    try:
        {'collect': collect, 'seal': seal}[phase]()
    except BaseException as exc:
        p = TMP / f'{phase}_failure.json'
        if not p.exists():
            save(p, {'exception_type': type(exc).__name__, 'exception': str(exc)})
        raise
