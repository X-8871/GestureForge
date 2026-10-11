"""只读补核S4独审归档副本，不重跑原独审或任何业务验证。"""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
FORMAL = ROOT / 'report/evidence/S2B-T17/independent_s4_synthesis_review_20261011_r01'
MAIN = ROOT / 'report/evidence/S2B-T17/s4_platform_20261011_r01'
EXPECTED = '4668a68f88f031a32738a6d396d1eb1c562158a2c8a7e211cd0b1e9672288123'
START = time.perf_counter()
COMMANDS = []


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def exact(path):
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT), '精确文件目标错误：' + str(path))
    return path


def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))


def bound(row):
    raw = exact(ROOT / row['path']).read_bytes()
    need(sha(raw) == row['sha256'], '绑定SHA错误：' + row['path'])
    return raw


def save(path, value):
    need(path.parent == OUT and not path.exists(), '新输出越界或已存在')
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def audit():
    manifest_path = FORMAL / 'delivery_manifest_r02.json'
    need(sha(exact(manifest_path).read_bytes()) == EXPECTED, '被审新wrapper版本改变')
    manifest = read(manifest_path)
    need(len(manifest['files']) == len({r['path'] for r in manifest['files']}) == 329, '329绑定数量错误')
    for row in manifest['files'] + manifest['interfaces']:
        bound(row)
    need(manifest['source_commit'] == 'f96d3e225fd6d92fd33c0407e20c9585c997c870', '源基线漂移')
    need(sha((MAIN / 's4_collection_delivery_manifest_r02.json').read_bytes()) == 'cc638501782ed0bf95a63e97cf0128b91fcb629754095201d0feb4e26979a535', 'S4main改变')
    binding_path = FORMAL / 'archive_binding.json'
    need(sha(exact(binding_path).read_bytes()) == '5d40d5d430eec78751b3533c45db127f105d043c2c422aac5c2d8bffa8ba50de', '归档mapping改变')
    mapping = read(binding_path)
    raw_manifest = json.loads(bound(mapping['raw_manifest']))
    receipt = json.loads(bound(mapping['receipt']))
    need(mapping['raw_manifest']['sha256'] == 'e7d3410e0a078af7b3bda3da0a8a3848c92c5300ad070e576aed5e539e7889e8'
         and mapping['receipt']['sha256'] == '36c002f6169e53e815e4c01e3ecfe7ee010aa123aff4cf18a5fb928a315ea742', '原独审版本绑定错误')
    need(raw_manifest['status'] == receipt['status'] == 'PASS_EVIDENCE_INTEGRITY_ONLY', '复制升级了独审范围')
    expected_rows = {row['path']: row['sha256'] for row in raw_manifest['files']}
    need(len(expected_rows) == 40, '原40条RAW清单错误')
    expected_rows[mapping['raw_manifest']['path']] = mapping['raw_manifest']['sha256']
    need(len(mapping['files']) == mapping['raw_file_count'] == 41, '复制41数量错误')
    total = 0
    for row in mapping['files']:
        original = exact(ROOT / row['original'])
        copy_path = exact(ROOT / row['copy'])
        need(copy_path == FORMAL / 'raw_artifacts' / row['original'], '镜像相对路径改变')
        raw = original.read_bytes()
        need(copy_path.read_bytes() == raw and sha(raw) == row['sha256'] == expected_rows[row['original']], 'RAW副本不同')
        need(row['bytes'] == len(raw), '复制字节统计错误')
        total += len(raw)
    need(set(expected_rows) == {r['original'] for r in mapping['files']} and total == mapping['raw_bytes'] == 240754, '复制集合/总字节不符')
    need(sha((FORMAL / 'delivery_manifest.json').read_bytes()) == '06699524a737218c7317511031a1f60cff47c2146bf963bb583d85cb6a847ab8', '首wrapper原件被覆盖')
    formal_paths = {p.relative_to(ROOT).as_posix() for p in FORMAL.rglob('*') if p.is_file()}
    listed = {r['path'] for r in manifest['files']}
    need(formal_paths - {manifest_path.relative_to(ROOT).as_posix()} <= listed, 'formal出现未绑定文件')
    config = read(FORMAL / 'input_config.json')
    need(config['review_status'] == receipt['status'] and config['reviewed_manifest'] == mapping['reviewed_manifest']
         and config['receipt'] == mapping['receipt'] and config['raw_manifest'] == mapping['raw_manifest'], '配置与实际版本不符')
    checks = {r['name']: r for r in manifest['checks']}
    by_original = {r['original']: r for r in mapping['files']}
    checked_native = []
    for row in config['native_checks']:
        native = read(ROOT / by_original[row['path']]['copy'])
        check = checks[row['name']]
        need(native['native_exit_code'] == row['expected_exit_code'] == check['exit_code']
             and check['command'] == subprocess.list2cmdline(native['command'])
             and check['status'] == ('PASS' if native['native_exit_code'] == 0 else 'FAIL'), '配置伪造了原生调用')
        checked_native.append({'name': row['name'], 'native_exit_code': native['native_exit_code']})
    original_checks = {r['name']: r for r in read(MAIN / 's4_collection_delivery_manifest_r02.json')['checks']}
    for name in config['include_reviewed_checks']:
        need(checks[name] == original_checks[name], '原FAIL/NOT_RUN被改变')
    need(checks['50MHz综合态STA分类']['status'] == 'FAIL' and checks['50MHz综合态STA分类']['exit_code'] == 2, 'STA升级通过')
    for name in ['实现及postroute', 'bitstream生成', '板上模型及109样本', '1000次板上任务', 'BOARD及G3验收']:
        need(checks[name]['status'] == 'NOT_RUN', '未执行范围升级')
    historical = []
    for mode, expected_code in [('evidence', 0), ('inputs', 2)]:
        native = read(FORMAL / ('root_archive_' + mode + '.native.json'))
        need(native['native_exit_code'] == expected_code, '首checker原生码错误')
        need(native['command'][native['command'].index('--manifest') + 1] == str(FORMAL / 'delivery_manifest.json'), '首checker目标错误')
        for row in native['closed_logs']:
            original = exact(ROOT / row['path'])
            saved = exact(FORMAL / ('root_archive_' + Path(row['path']).name))
            need(original.read_bytes() == saved.read_bytes() and sha(saved.read_bytes()) == row['sha256'], '首checker日志RAW不同')
        result = read(FORMAL / ('root_archive_' + mode + '.stdout.log'))
        need(result['status'] == ('CHECKS_OK' if expected_code == 0 else 'CHECKS_FAILED'), '首checker输出/退出码矛盾')
        check = checks['root归档首清单' + mode + '原生检查']
        need(check['command'] == subprocess.list2cmdline(native['command']) and check['exit_code'] == expected_code, '首checker调用元数据伪造')
        historical.append({'mode': mode, 'native_exit_code': expected_code, 'output_status': result['status']})
    archive = (FORMAL / 'archive_reviewed_evidence.py').read_text(encoding='utf-8')
    seal = (FORMAL / 'seal_s4_archive.py').read_text(encoding='utf-8')
    need('shutil.copyfile(source, target)' in archive and 'target.read_bytes() == raw' in archive
         and 'native["native_exit_code"] == item["expected_exit_code"]' in archive, '归档脚本不验证真实原件')
    need('result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)' in seal
         and 'result.returncode == expected' in seal and 'result.returncode' in seal
         and 'with path.open("x", encoding="utf-8"' in seal, '封存脚本存在伪造/覆盖调用')
    checker = MAIN / 's4_collection_stage_checker_snapshot.py'
    need(sha(checker.read_bytes()) == 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf', '固定checker版本改变')
    for mode, expected_code in [('evidence', 0), ('inputs', 2)]:
        command = [sys.executable, '-B', '-X', 'utf8', str(checker), '--mode', mode, '--manifest', str(manifest_path), '--project-root', str(ROOT)]
        started = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, timeout=60)
        logs = []
        for suffix, raw in [('stdout.log', result.stdout), ('stderr.log', result.stderr)]:
            p = OUT / (mode + '.' + suffix)
            need(not p.exists(), '新补核日志禁止覆盖')
            p.write_bytes(raw)
            logs.append({'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(raw), 'bytes': len(raw)})
        COMMANDS.append({'command': command, 'native_exit_code': result.returncode,
                         'elapsed_seconds': time.perf_counter() - started, 'closed_logs': logs})
        need(result.returncode == expected_code, '新包装真实原生码错误')
    return {'copied_files': 41, 'copied_bytes': total, 'manifest_bindings': 329,
            'config_native_checks': checked_native, 'historical_checker': historical,
            'current_checker': {'evidence': 0, 'inputs': 2}, 'formal_files': len(formal_paths)}


def main():
    try:
        details = audit()
        status, code = 'PASS_COPY_INTEGRITY', 0
    except Exception as error:
        details = {'error': repr(error)}
        status, code = 'CHANGES_REQUIRED', 2
    receipt = {'status': status, 'reviewed_manifest': (FORMAL / 'delivery_manifest_r02.json').relative_to(ROOT).as_posix(),
               'reviewed_manifest_sha256': EXPECTED, 'details': details, 'native_commands': COMMANDS,
               'elapsed_seconds': time.perf_counter() - START,
               'created_at_utc8': datetime.now(timezone(timedelta(hours=8))).isoformat(),
               'peak_memory_bytes': None, 'peak_reason': '本轻量复制补核未测峰值。',
               'limitations': ['仅批准复制完整性，原PASS_EVIDENCE_INTEGRITY_ONLY范围不变；STA仍FAIL_TIMING。',
                               '未重跑原独审、综合、实现、仿真或硬件动作；没有消费S5 live源。',
                               '新输出仅在隔离r03；正式包、项目代码、Git/STATE未改。']}
    save(OUT / 'receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
