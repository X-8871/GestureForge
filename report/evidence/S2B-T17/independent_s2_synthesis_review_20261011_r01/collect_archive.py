"""仅归档已停止审查的原字节，并绑定实际S2输入。"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = pathlib.Path(__file__).resolve().parent
REVIEW = ROOT / 'tmp/2B/S2B-T17/independent_s2_synthesis_review_20261011_r01'
ARCHIVE = ROOT / 'report/evidence/S2B-T17/independent_s2_synthesis_review_20261011_r01'
RECEIPT_SHA = 'c5350f163f1b1aa7d16b4ed04ec53118759c77e01099e7e7e2c0d323bfcaf745'
STAGE_SHA = 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf'

def digest(path):
    """分块读取原字节，避免载入大文件。"""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def checked(relative, expected):
    """精确核验路径、类型与哈希，不修正名称。"""
    p = ROOT / relative
    assert p.is_file() and not p.is_symlink(), str(p)
    assert p.resolve().is_relative_to(ROOT), str(p)
    assert digest(p) == expected, str(p)
    return p

def save(path, data):
    """只创建新文件，不覆盖原件。"""
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def rel(path):
    return path.relative_to(ROOT).as_posix()

def binding(path, role):
    return {'path': rel(path), 'sha256': digest(path), 'role': role}

def main():
    start = time.perf_counter()
    assert ARCHIVE.parent.is_dir() and not ARCHIVE.parent.is_symlink()
    assert not ARCHIVE.exists(), str(ARCHIVE)
    rp = checked(rel(REVIEW / 'receipt.json'), RECEIPT_SHA)
    receipt = json.loads(rp.read_text(encoding='utf-8'))
    assert receipt['status'] == 'PASS_EVIDENCE_INTEGRITY' and receipt['stop'] is True
    assert len(receipt['checks']) == 654 and all(x['passed'] is True for x in receipt['checks'])
    records = receipt['closed_raw_review_files']
    assert len(records) == 14
    approved = receipt['bound_original_manifest']
    mp = checked(approved['path'], approved['sha256'])
    m = json.loads(mp.read_text(encoding='utf-8'))
    assert len(m['files']) == approved['file_bindings'] == 191
    assert len(m['interfaces']) == approved['interface_bindings'] == 2
    assert m['source_commit'] == receipt['reviewed_source_commit'] == '5a676b700af4c27297977379417b1694dd64840e'
    deps = {}
    for item in m['files']:
        p = checked(item['path'], item['sha256'])
        deps[item['path']] = binding(p, 'input')
    deps[rel(mp)] = binding(mp, 'input')
    for item in receipt['sources']:
        p = checked(item['snapshot_path'], item['sha256'])
        deps[rel(p)] = binding(p, 'input')
    for item in m['interfaces']:
        checked(item['path'], item['sha256'])
    stage = checked('verification/check_stage_delivery.py', STAGE_SHA)
    assert deps[rel(stage)]['sha256'] == STAGE_SHA
    assert sorted(p.name for p in REVIEW.iterdir()) == sorted(['receipt.json'] + [pathlib.Path(x['path']).name for x in records])
    ARCHIVE.mkdir()
    mappings = []
    for item in records + [{'path': rel(rp), 'sha256': RECEIPT_SHA, 'bytes': rp.stat().st_size}]:
        source = checked(item['path'], item['sha256'])
        assert source.parent == REVIEW and source.stat().st_size == item['bytes']
        dest = ARCHIVE / source.name
        assert not dest.exists()
        shutil.copyfile(source, dest)
        assert digest(dest) == item['sha256'] and dest.stat().st_size == item['bytes']
        mappings.append({'source': item['path'], 'copy': rel(dest), 'sha256': item['sha256'], 'bytes': item['bytes'], 'raw_bytes_equal': True})
    for source_name in ['collect_archive.py']:
        source = TMP / source_name
        dest = ARCHIVE / source_name
        assert not dest.exists()
        shutil.copyfile(source, dest)
        assert digest(source) == digest(dest)
    save(ARCHIVE / 'raw_copy_mapping.json', {'schema_version': 1, 'copies': mappings, 'count': len(mappings), 'bytes': sum(x['bytes'] for x in mappings), 'originals_retained': True})
    save(ARCHIVE / 'archive_result.json', {
        'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'review_status': receipt['status'],
        'review_checks': len(receipt['checks']), 'raw_copies': len(mappings),
        'bound_main_manifest': approved, 'review_commands': receipt['commands'],
        'review_execution': receipt['review_execution'], 'supplement_checks': receipt['supplement_checks'],
        'sta': receipt['sta'], 'relocation': receipt['native_relocation'],
        'elapsed_seconds_before_packaging': time.perf_counter() - start,
        'peak_memory': 'NOT_MEASURED', 'hardware': 'NOT_RUN', 'runtime_compatibility': 'NOT_APPROVED',
        'limitations': ['PASS仅限原件归档完整性；STA仍FAIL_TIMING，不证明部署、实板或阶段通过。', 'main/preflight未重复复制；冻结S2快照按原SHA绑定，未读取当前S3工程源。', '原137路径未改、9路径曾获准迁移；其原字节保持，旧失败与旧路径清单原样保留。', '全进程树峰值与全审查wall未测；不得混同原native wait381.939秒。']
    })
    checks = [
        {'name': '独立审查原执行', 'status': 'PASS', 'command': subprocess.list2cmdline(receipt['review_execution']['command']), 'exit_code': receipt['review_execution']['native_exit_code'], 'reason': '原收据仅PASS_EVIDENCE_INTEGRITY；不重跑审查。'},
        {'name': '原独立STA分类', 'status': 'FAIL', 'command': subprocess.list2cmdline(receipt['commands'][3]['command']), 'exit_code': 2, 'reason': 'WNS−62.174/TNS−12041.195，811/14720setup失败；原分类器实际2。'},
        {'name': '实物/实现/位流/运行兼容性', 'status': 'NOT_RUN', 'command': None, 'exit_code': None, 'reason': '本归档不执行工具SDK或实物，不批准runtime兼容性。'}
    ]
    manifest = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': ARCHIVE.name,
                'source_commit': m['source_commit'], 'evidence_dir': rel(ARCHIVE),
                'interfaces': m['interfaces'], 'tool_versions': {'python': sys.version, 'stage_checker_sha256': STAGE_SHA},
                'files': list(deps.values()), 'checks': checks,
                'limitations': ['完整性归档PASS不代表STA/G2设计/部署/G3/G5通过。物理候选接口未冻结，inputs应为2。', '保留全部失败历史；主包和快照仅input绑定，无当前S3源码消费。', '封存检查的最终stdout在隔离tmp关闭后核验，不自绑定动态stdout。']}
    for p in sorted(ARCHIVE.iterdir()):
        manifest['files'].append(binding(p, 'source' if p.name == 'collect_archive.py' else 'log' if p.suffix == '.log' else 'result'))
    save(ARCHIVE / 'delivery_manifest_r01.json', manifest)
    commands = []
    for mode, expected in [('evidence', 0), ('inputs', 2)]:
        assert digest(stage) == STAGE_SHA
        cmd = [sys.executable, '-B', str(stage), '--mode', mode, '--manifest', str(ARCHIVE / 'delivery_manifest_r01.json'), '--project-root', str(ROOT)]
        st = time.perf_counter()
        result = subprocess.run(cmd, capture_output=True, cwd=ROOT)
        for suffix, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
            target = ARCHIVE / f'packaging_{mode}_r01.{suffix}.log'
            with target.open('xb') as f:
                f.write(raw)
        parsed = json.loads(result.stdout.decode('utf-8'))
        assert result.returncode == expected, (mode, result.returncode, parsed)
        if mode == 'evidence':
            assert parsed['errors'] == [] and parsed['warnings'] == []
        commands.append({'mode': mode, 'command': cmd, 'native_exit_code': result.returncode, 'seconds': time.perf_counter() - st, 'result': parsed})
    save(ARCHIVE / 'packaging_result_r01.json', {'commands': commands, 'peak_memory': 'NOT_MEASURED'})
    save(TMP / 'collector_inner_result.json', {'native_business_status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'seconds': time.perf_counter() - start, 'raw_copies': len(mappings), 'raw_bytes': sum(x['bytes'] for x in mappings)})
    print(json.dumps({'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'copies': len(mappings), 'seconds': time.perf_counter() - start}))

if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        target = TMP / 'collector_failure.json'
        if not target.exists():
            save(target, {'exception_type': type(exc).__name__, 'exception': str(exc)})
        raise
