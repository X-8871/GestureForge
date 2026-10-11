"""仅归档S3独审绑定原件；不执行源码测试或硬件。"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = pathlib.Path(__file__).resolve().parent
REVIEW = ROOT / 'tmp/2B/S2B-T17/independent_route_review_20261011_r01'
ARCHIVE = ROOT / 'report/evidence/S2B-T17/independent_route_review_20261011_r01'
RECEIPT_SHA = 'd0aefc1ae5c42a6dcb8c3c82ef6e5bfc0be801f2bb5b4cfb9ee895aa0280884a'
RAW_SHA = '73169deee0f4396022c62f7093779984ae234c1bd80a1d30e4b33a2ccabfc2f6'
FREEZE_SHA = 'b550628ca96fd193e571e7144efcc3bc1ad0f5c9123ff2ba40899edee6b52231'
MAIN_SHA = 'b6fa0a51eecd332635f5f189f1b80d18480a144fb7edde4cba515c802bbcf330'
STAGE_SHA = 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf'

def sha(path):
    """以固定小块读取原字节，不转码。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def checked(relative, expected):
    """严格核验完整路径、类型、范围和SHA。"""
    p = ROOT / relative
    assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT), str(p)
    assert sha(p) == expected, str(p)
    return p

def save(path, data):
    """所有输出采用新名称独占写入。"""
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def copy(source, target):
    assert source.is_file() and not source.is_symlink() and not target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.parent.is_symlink()
    shutil.copyfile(source, target)
    assert sha(source) == sha(target) and source.stat().st_size == target.stat().st_size

def binding(path, role):
    return {'path': rel(path), 'sha256': sha(path), 'role': role}

def package(manifest, suffix):
    """仅运行固定版本包装检查器，结果不解释为设计通过。"""
    stage = checked('verification/check_stage_delivery.py', STAGE_SHA)
    records = []
    for mode, expected in [('evidence', 0), ('inputs', 2)]:
        cmd = [sys.executable, '-X', 'utf8', '-B', str(stage), '--mode', mode, '--manifest', str(manifest), '--project-root', str(ROOT)]
        start = time.perf_counter()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        closed = []
        for name, data in [('stdout', r.stdout), ('stderr', r.stderr)]:
            p = TMP / f'{suffix}_{mode}.{name}.log'
            with p.open('xb') as f:
                f.write(data)
            closed.append({'path': rel(p), 'sha256': sha(p), 'bytes': p.stat().st_size})
        parsed = json.loads(r.stdout.decode('utf-8'))
        assert r.returncode == expected, parsed
        if mode == 'evidence':
            assert parsed['errors'] == [] and parsed['warnings'] == []
        records.append({'command': cmd, 'native_exit_code': r.returncode, 'seconds': time.perf_counter() - start, 'closed_logs': closed, 'result': parsed})
    return records

def collect():
    start = time.perf_counter()
    assert REVIEW.is_dir() and not REVIEW.is_symlink()
    assert ARCHIVE.parent.is_dir() and not ARCHIVE.parent.is_symlink() and not ARCHIVE.exists()
    rp = checked(rel(REVIEW / 'review_receipt.json'), RECEIPT_SHA)
    rawp = checked(rel(REVIEW / 'raw_artifact_manifest.json'), RAW_SHA)
    receipt = json.loads(rp.read_text(encoding='utf-8'))
    raw = json.loads(rawp.read_text(encoding='utf-8'))
    assert receipt['role'] == 'INDEPENDENT_REVIEWER' and receipt['status'] == 'PASS'
    assert receipt['g2_only'] is True and receipt['checks'] == 412 and receipt['independent_query_cases'] == 408
    assert raw['review_receipt_sha256'] == RECEIPT_SHA and raw['source_freeze_sha256'] == FREEZE_SHA
    assert len(raw['files']) == 20 and len({x['path'] for x in raw['files']}) == 20
    assert any(x['path'] == 'review_receipt.json' for x in raw['files'])
    fp = checked(receipt['freeze_path'], FREEZE_SHA)
    freeze = json.loads(fp.read_text(encoding='utf-8'))
    assert freeze['source_sha256'] == receipt['source_sha256'] and freeze['changed_files'] == receipt['changed_files']
    assert len(freeze['changed_files']) == 10
    mainp = checked('report/evidence/S2B-T17/route_specialization_20261011_r07/delivery_manifest.json', MAIN_SHA)
    assert receipt['developer_delivery_manifest_sha256'] == MAIN_SHA and receipt['freeze_sha256'] == FREEZE_SHA
    main = json.loads(mainp.read_text(encoding='utf-8'))
    deps = {}
    for x in main['files']:
        p = checked(x['path'], x['sha256'])
        deps[rel(p)] = binding(p, 'input')
    for path, expected in freeze['source_sha256'].items():
        p = checked(path, expected)
        deps[rel(p)] = binding(p, 'input')
    for p in [fp, mainp, checked('verification/check_stage_delivery.py', STAGE_SHA)]:
        deps[rel(p)] = binding(p, 'input')
    for x in main['interfaces']:
        checked(x['path'], x['sha256'])
    ARCHIVE.mkdir()
    rows = raw['files'] + [{'path': rawp.name, 'sha256': RAW_SHA, 'bytes': rawp.stat().st_size}]
    mapping = []
    for x in rows:
        inner = pathlib.PurePosixPath(x['path'])
        assert not inner.is_absolute() and '..' not in inner.parts and 'obj_dir' not in inner.parts
        source = checked(rel(REVIEW / pathlib.Path(*inner.parts)), x['sha256'])
        assert source.resolve().is_relative_to(REVIEW) and source.stat().st_size == x['bytes']
        dest = ARCHIVE / pathlib.Path(*inner.parts)
        copy(source, dest)
        mapping.append({'source': rel(source), 'copy': rel(dest), 'sha256': x['sha256'], 'bytes': x['bytes'], 'raw_bytes_equal': True})
    copy(TMP / 'archive_route_review.py', ARCHIVE / 'archive_route_review.py')
    save(ARCHIVE / 'raw_copy_mapping.json', {'schema_version': 1, 'count': len(mapping), 'bytes': sum(x['bytes'] for x in mapping), 'copies': mapping, 'originals_retained': True, 'obj_dir_copied': False})
    save(ARCHIVE / 'collector_read_schema_diagnostic.json', {'kind': 'READ_ONLY_INSPECTION_FAILURE_RETAINED', 'actual_command_native_exit_code': 1, 'exception_type': 'TypeError', 'exception': "object of type 'int' has no len()", 'cause': '初次只读摘要把receipt.checks整数当列表；后续按真实schema读取412，不修改原件。', 'design_failure': False, 'scope': '仅此前只读结构检查，不是归档Collector或仿真失败。'})
    save(ARCHIVE / 'archive_result.json', {
        'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'review_scope': 'PASS_G2_ONLY', 'original_receipt_status': receipt['status'],
        'review_checks': receipt['checks'], 'independent_query_cases': receipt['independent_query_cases'], 'source_freeze_path': rel(fp), 'source_freeze_sha256': FREEZE_SHA,
        'developer_manifest_path': rel(mainp), 'developer_manifest_sha256': MAIN_SHA, 'changed_files': receipt['changed_files'],
        'original_commands': receipt['commands'], 'original_reviewer_diagnostics': receipt['reviewer_diagnostics'], 'original_resource': receipt['resource'],
        'original_limitations': receipt['limitations'], 'copies': len(mapping), 'raw_copy_bytes': sum(x['bytes'] for x in mapping),
        'cache_excluded': {'path': rel(REVIEW / 'obj_dir'), 'bytes_as_recorded_by_reviewer': receipt['resource']['cache_bytes'], 'inspected_or_copied': False},
        'new_sta': 'NOT_RUN', 'full_109_model': 'NOT_RUN', 'hardware': 'NOT_RUN', 'collector_peak_memory': 'NOT_MEASURED'})
    m = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': ARCHIVE.name, 'source_commit': main['source_commit'],
         'evidence_dir': rel(ARCHIVE), 'interfaces': main['interfaces'], 'tool_versions': {'python': sys.version, 'stage_checker_sha256': STAGE_SHA},
         'files': list(deps.values()), 'checks': [
             {'name': '原独立S3实际仿真', 'status': 'PASS', 'command': subprocess.list2cmdline(next(x['command'] for x in receipt['commands'] if x['name'] == 'simulation')), 'exit_code': 0, 'reason': '原receipt批准固定ROM可达域G2，仅保存408query原结果，不重跑。'},
             {'name': '新闭包STA/实现/109/bit/G3', 'status': 'NOT_RUN', 'command': None, 'exit_code': None, 'reason': '本归档不执行源码测试或硬件；旧S2时序失败未关闭。'}],
         'limitations': ['PASS仅归档完整性及原G2候选范围，不批准STA、109整网、部署或G3/G4/G5。', '固定source_freeze原SHA；HEAD变化不代替源码SHA。原Developer包和源码只作为input绑定，不修改或复制。', '保留两次Reviewer自身失败原件；20bound中已含receipt，另复制rawmanifest为21份，不归档obj_dir缓存。', '归档Collector峰值内存未测；原Reviewer957407232B编译峰值仅原运行测量，不是本次Collector峰值。', '最终动态stdout在tmp关闭后核验，不自绑定动态日志；物理候选未冻结，inputs为2。']}
    for p in sorted(ARCHIVE.rglob('*')):
        if p.is_file():
            m['files'].append(binding(p, 'source' if p.name == 'archive_route_review.py' else 'log' if p.suffix == '.log' else 'result'))
    save(ARCHIVE / 'delivery_manifest_r01.json', m)
    commands = package(ARCHIVE / 'delivery_manifest_r01.json', 'initial')
    save(TMP / 'initial_packaging_result.json', {'commands': commands})
    save(TMP / 'collector_inner_result.json', {'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'seconds': time.perf_counter() - start, 'copies': len(mapping), 'bytes': sum(x['bytes'] for x in mapping)})
    print(json.dumps({'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'copies': len(mapping), 'seconds': time.perf_counter() - start}))

def seal():
    start = time.perf_counter()
    for name in ['collector_native.json', 'collector.stdout.log', 'collector.stderr.log', 'collector_inner_result.json', 'initial_packaging_result.json', 'initial_evidence.stdout.log', 'initial_evidence.stderr.log', 'initial_inputs.stdout.log', 'initial_inputs.stderr.log']:
        copy(TMP / name, ARCHIVE / name)
    m = json.loads((ARCHIVE / 'delivery_manifest_r01.json').read_text(encoding='utf-8'))
    m['files'] = [x for x in m['files'] if not x['path'].startswith(rel(ARCHIVE) + '/')]
    native = json.loads((ARCHIVE / 'collector_native.json').read_text(encoding='utf-8'))
    assert native['native_exit_code'] == 0
    m['checks'].append({'name': '实际Collector原件归档', 'status': 'PASS', 'command': subprocess.list2cmdline(native['command']), 'exit_code': 0, 'reason': '21份绑定原件raw相同，所有失败保留，obj_dir未复制。'})
    for p in sorted(ARCHIVE.rglob('*')):
        if p.is_file():
            m['files'].append(binding(p, 'source' if p.name == 'archive_route_review.py' else 'log' if p.suffix == '.log' else 'result'))
    mp = ARCHIVE / 'delivery_manifest_r02.json'
    save(mp, m)
    commands = package(mp, 'final')
    for x in m['files'] + m['interfaces']:
        checked(x['path'], x['sha256'])
    mapping = json.loads((ARCHIVE / 'raw_copy_mapping.json').read_text(encoding='utf-8'))
    for x in mapping['copies']:
        source = checked(x['source'], x['sha256'])
        target = checked(x['copy'], x['sha256'])
        assert source.stat().st_size == target.stat().st_size == x['bytes']
    allfiles = [p for p in ARCHIVE.rglob('*') if p.is_file()]
    result = {'status': 'STOP_PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'scope': 'PASS_G2_ONLY', 'manifest': rel(mp), 'manifest_sha256': sha(mp),
              'files_bindings': len(m['files']), 'interface_bindings': len(m['interfaces']), 'total_bindings': len(m['files']) + len(m['interfaces']),
              'archive_files': len(allfiles), 'archive_bytes': sum(p.stat().st_size for p in allfiles), 'copies': mapping['count'], 'raw_copy_bytes': mapping['bytes'],
              'copies_raw_equal': True, 'all_final_bindings_verified': True, 'commands': commands, 'seconds': time.perf_counter() - start,
              'collector_peak_memory': 'NOT_MEASURED', 'root_file_list': sorted(p.relative_to(ARCHIVE).as_posix() for p in allfiles), 'sta_or_hardware_run': False}
    save(TMP / 'final_status.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['commands', 'root_file_list']}))

if __name__ == '__main__':
    phase = sys.argv[1]
    try:
        {'collect': collect, 'seal': seal}[phase]()
    except BaseException as exc:
        p = TMP / f'{phase}_failure.json'
        if not p.exists():
            save(p, {'exception_type': type(exc).__name__, 'exception': str(exc)})
        raise
