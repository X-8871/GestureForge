"""封存已关闭collector日志，并只创建最终归档清单。"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[4]
TMP = pathlib.Path(__file__).resolve().parent
ARCHIVE = ROOT / 'report/evidence/S2B-T17/independent_s2_synthesis_review_20261011_r01'
STAGE_SHA = 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf'

def sha(p):
    """分块读取原字节。"""
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()

def save(p, data):
    """新名称独占写入，保留全部旧清单。"""
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def main():
    start = time.perf_counter()
    assert ARCHIVE.is_dir() and not ARCHIVE.is_symlink()
    for name in ['seal_archive.py', 'collector_native.json', 'collector.stdout.log', 'collector.stderr.log', 'collector_inner_result.json']:
        source = TMP / name
        target = ARCHIVE / name
        assert source.is_file() and not source.is_symlink() and not target.exists()
        shutil.copyfile(source, target)
        assert sha(source) == sha(target) and source.stat().st_size == target.stat().st_size
    m = json.loads((ARCHIVE / 'delivery_manifest_r01.json').read_text(encoding='utf-8'))
    m['files'] = [x for x in m['files'] if not x['path'].startswith(ARCHIVE.relative_to(ROOT).as_posix() + '/')]
    for p in sorted(ARCHIVE.iterdir()):
        assert p.is_file() and not p.is_symlink()
        role = 'source' if p.name in ['collect_archive.py', 'seal_archive.py'] else 'log' if p.suffix == '.log' else 'result'
        m['files'].append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'role': role})
    native = json.loads((ARCHIVE / 'collector_native.json').read_text(encoding='utf-8'))
    assert native['native_exit_code'] == 0
    m['checks'].append({'name': '原字节归档Collector', 'status': 'PASS', 'command': subprocess.list2cmdline(native['command']), 'exit_code': native['native_exit_code'], 'reason': '15份原字节精确复制，源原件保留；峰值内存未测。'})
    target = ARCHIVE / 'delivery_manifest_r02.json'
    save(target, m)
    stage = ROOT / 'verification/check_stage_delivery.py'
    outputs = []
    for mode, expected in [('evidence', 0), ('inputs', 2)]:
        assert stage.is_file() and sha(stage) == STAGE_SHA
        cmd = [sys.executable, '-B', str(stage), '--mode', mode, '--manifest', str(target), '--project-root', str(ROOT)]
        begin = time.perf_counter()
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        logs = []
        for suffix, raw in [('stdout', r.stdout), ('stderr', r.stderr)]:
            p = TMP / f'final_{mode}.{suffix}.log'
            with p.open('xb') as f:
                f.write(raw)
            logs.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size})
        result = json.loads(r.stdout.decode('utf-8'))
        assert r.returncode == expected, result
        if mode == 'evidence':
            assert result['errors'] == [] and result['warnings'] == []
        outputs.append({'command': cmd, 'native_exit_code': r.returncode, 'seconds': time.perf_counter() - begin, 'closed_logs': logs, 'result': result})
    for row in m['files']:
        p = ROOT / row['path']
        assert p.is_file() and not p.is_symlink() and sha(p) == row['sha256'], row['path']
    for row in m['interfaces']:
        assert sha(ROOT / row['path']) == row['sha256']
    mapping = json.loads((ARCHIVE / 'raw_copy_mapping.json').read_text(encoding='utf-8'))
    for row in mapping['copies']:
        assert sha(ROOT / row['source']) == sha(ROOT / row['copy']) == row['sha256']
        assert (ROOT / row['source']).stat().st_size == (ROOT / row['copy']).stat().st_size == row['bytes']
    files = list(ARCHIVE.iterdir())
    summary = {'status': 'STOP_PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'manifest': target.relative_to(ROOT).as_posix(), 'manifest_sha256': sha(target),
               'manifest_files': len(m['files']), 'manifest_interfaces': len(m['interfaces']), 'total_bindings': len(m['files']) + len(m['interfaces']),
               'archive_files': len(files), 'archive_bytes': sum(p.stat().st_size for p in files), 'raw_copy_count': mapping['count'], 'raw_copy_bytes': mapping['bytes'],
               'all_raw_copies_equal': True, 'all_final_bindings_verified': True, 'root_file_list': sorted(p.name for p in files),
               'commands': outputs, 'seconds': time.perf_counter() - start, 'peak_memory': 'NOT_MEASURED', 'sta_status': 'FAIL_TIMING',
               'hardware': 'NOT_RUN', 'runtime_compatibility': 'NOT_APPROVED'}
    save(TMP / 'final_status.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'commands'}, ensure_ascii=True))

if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        p = TMP / 'seal_failure.json'
        if not p.exists():
            save(p, {'exception_type': type(exc).__name__, 'exception': str(exc)})
        raise
