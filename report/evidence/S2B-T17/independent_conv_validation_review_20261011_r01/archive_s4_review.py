"""封装已完成的S4独立审查原件，只运行交付包装检查器。"""
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
TMP = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'report/evidence/S2B-T17/independent_conv_validation_review_20261011_r01'
REVIEW = ROOT / 'tmp/2B/S2B-T17/independent_conv_validation_review_20261011_r02'
HEAD = '90c87b773fe06684797f6bb3cca2da078a4d49aa'
RECEIPT_SHA = '83a9004a56bfe86089e6e7557715fb3f0e5cb3516f11e97eb947c4ad37a2beda'
RAW_SHA = '9b195e2aecb9ebddbd5ef0fcf82853652bb46a98728014fff308a19132f28bb1'
MANIFEST = 'report/evidence/S2B-T17/conv_validation_20261011_r15/delivery_manifest_r02.json'
MANIFEST_SHA = '0fcec217510cccca8e79ce9ff312ccfea60f8cf520c4fcd647857cae5080ed06'
FREEZE = 'report/evidence/S2B-T17/conv_validation_20261011_r15/source_freeze.json'
FREEZE_SHA = 'd8f2af3f6ac243267c12d9a8ca1b8559b0ff1e69054492b4eab50dcdee62a846'
STAGE_SHA = 'cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf'


def require(condition, message):
    """条件不符立即停止，不覆盖已有证据。"""
    if not condition:
        raise RuntimeError(message)


def rel(path):
    return path.relative_to(ROOT).as_posix()


def exact(path, kind='file'):
    """核验完整目标及路径全部父级，不接受符号链接。"""
    require(path.is_relative_to(ROOT), '路径越界：' + str(path))
    current = ROOT
    for component in path.relative_to(ROOT).parts:
        current = current / component
        require(current.exists() and not current.is_symlink(), '路径不存在或为链接：' + str(current))
    require(path.is_file() if kind == 'file' else path.is_dir(), '目标类型不符：' + str(path))
    return path


def sha(path):
    h = hashlib.sha256()
    with exact(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def checked(name, expected):
    path = exact(ROOT / name)
    require(sha(path) == expected, 'SHA不符：' + name)
    return path


def read(path):
    return json.loads(exact(path).read_text(encoding='utf-8'))


def save(path, data):
    """在授权目录独占创建UTF-8输出。"""
    require(path.is_relative_to(TMP) or path.is_relative_to(ARCHIVE), '输出越界')
    exact(path.parent, 'directory')
    require(not path.exists(), '输出已存在：' + str(path))
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def copy(source, destination):
    """逐字节复制到新路径，源和副本分别复核。"""
    exact(source)
    require(destination.is_relative_to(ARCHIVE) and not destination.exists(), '复制目标越界或存在')
    destination.parent.mkdir(parents=True, exist_ok=True)
    exact(destination.parent, 'directory')
    shutil.copyfile(source, destination)
    require(sha(source) == sha(destination) and source.stat().st_size == destination.stat().st_size, '复制字节不同')


def binding(path, role):
    return {'path': rel(path), 'sha256': sha(path), 'role': role}


def inventory(path):
    return {'path': rel(path), 'sha256': sha(path), 'bytes': path.stat().st_size}


def archive_files():
    """只枚举本次正式新目录，不扫描任何审查缓存。"""
    return sorted(p for p in ARCHIVE.rglob('*') if p.is_file())


def package(manifest, prefix):
    """读取固定检查器并保存真实原生返回码。"""
    stage = checked('verification/check_stage_delivery.py', STAGE_SHA)
    records = []
    for mode, expected in [('evidence', 0), ('inputs', 2)]:
        command = [sys.executable, '-X', 'utf8', '-B', str(stage), '--mode', mode, '--manifest', str(manifest), '--project-root', str(ROOT)]
        started = time.perf_counter()
        result = subprocess.run(command, cwd=ROOT, capture_output=True)
        logs = []
        for suffix, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
            path = TMP / f'{prefix}_{mode}.{suffix}.log'
            with path.open('xb') as stream:
                stream.write(content)
            logs.append(inventory(path))
        record = {'command': command, 'cwd': str(ROOT), 'native_exit_code': result.returncode, 'seconds': round(time.perf_counter() - started, 6), 'closed_logs': logs}
        save(TMP / f'{prefix}_{mode}.native.json', record)
        parsed = json.loads(result.stdout.decode('utf-8'))
        require(result.returncode == expected, '包装检查返回码不符：' + mode)
        if mode == 'evidence':
            require(parsed['errors'] == [] and parsed['warnings'] == [], '正式包装出现错误或警告')
        records.append(record)
    return records


def original_native_check(name, filename, status):
    original = read(REVIEW / filename)
    return {'name': name, 'status': status, 'command': subprocess.list2cmdline(original['command']), 'exit_code': original['exit_code'], 'reason': '原独立Reviewer的真实原生执行记录；本次只归档原件，不重跑该命令。'}


def collect():
    started = time.perf_counter()
    exact(ARCHIVE.parent, 'directory')
    require(not ARCHIVE.exists(), '正式RunId已存在')
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, check=True).stdout.decode('ascii').strip()
    require(head == HEAD, 'HEAD已漂移')
    receipt_path = checked(rel(REVIEW / 'review_receipt.json'), RECEIPT_SHA)
    raw_path = checked(rel(REVIEW / 'raw_delivery_manifest.json'), RAW_SHA)
    manifest_path = checked(MANIFEST, MANIFEST_SHA)
    freeze_path = checked(FREEZE, FREEZE_SHA)
    receipt, raw, main, freeze = map(read, [receipt_path, raw_path, manifest_path, freeze_path])
    require(receipt['status'] == raw['status'] == 'PASS_G2_ONLY', '独立回执状态不同')
    require(receipt['developer_delivery_manifest'] == {'path': MANIFEST, 'sha256': MANIFEST_SHA}, '回执G1绑定不同')
    require(receipt['developer_source_freeze'] == {'path': FREEZE, 'sha256': FREEZE_SHA}, '回执冻结绑定不同')
    require(receipt['observed_head'] == freeze['current_head'] == head, '源码入口HEAD不同')
    require(receipt['source_sha256'] == freeze['source_sha256'] and len(freeze['source_sha256']) == 37, '37源码绑定不同')
    require(len(main['files']) == len({row['path'] for row in main['files']}) == 197, '197份G1绑定不同')
    require(len(raw['files']) == len({row['path'] for row in raw['files']}) == 36, '36份Reviewer原件数量不同')
    require(sum(row['bytes'] for row in raw['files']) == raw['total_bytes'] == 474943, 'Reviewer原件字节数不同')
    dependencies = {}
    for row in main['files']:
        path = checked(row['path'], row['sha256'])
        dependencies[rel(path)] = binding(path, 'input')
    source_rows = []
    for name, expected in freeze['source_sha256'].items():
        path = checked(name, expected)
        require(name in dependencies and dependencies[name]['sha256'] == expected, 'G1未绑定已审源码：' + name)
        source_rows.append(inventory(path))
    for row in main['interfaces']:
        checked(row['path'], row['sha256'])
    dependencies[MANIFEST] = binding(manifest_path, 'input')
    stage = checked('verification/check_stage_delivery.py', STAGE_SHA)
    dependencies[rel(stage)] = binding(stage, 'input')
    g1_inventory = []
    for index in range(1, 16):
        run = exact(ROOT / f'report/evidence/S2B-T17/conv_validation_20261011_r{index:02d}', 'directory')
        rows = []
        for path in sorted(run.rglob('*')):
            if path.is_file():
                exact(path)
                require(rel(path) in dependencies, 'G1目录存在未绑定原件：' + rel(path))
                rows.append(inventory(path))
        require(bool(rows), 'G1目录为空：' + rel(run))
        g1_inventory.append({'run_id': run.name, 'files': rows, 'count': len(rows), 'bytes': sum(row['bytes'] for row in rows)})
    raw_rows = raw['files'] + [{'path': rel(raw_path), 'sha256': RAW_SHA, 'bytes': raw_path.stat().st_size}]
    prepared = []
    for row in raw_rows:
        inner = PurePosixPath(row['path'])
        require(not inner.is_absolute() and '..' not in inner.parts, '原件路径非法')
        require(inner.parts[:4] == ('tmp', '2B', 'S2B-T17', inner.parts[3]), '原件不在指定任务内')
        require(inner.parts[3] in {f'independent_conv_validation_review_20261011_r{i:02d}' for i in [1, 2, 3]}, '原件RunId越界')
        require('obj_dir' not in inner.parts and 'checker_fixture' not in inner.parts, '原清单包含排除缓存')
        source = checked(row['path'], row['sha256'])
        require(source.stat().st_size == row['bytes'], '原件长度不同')
        destination = ARCHIVE / 'raw' / Path(*inner.parts[3:])
        prepared.append((source, destination, row))
    ARCHIVE.mkdir()
    mapping = []
    for source, destination, row in prepared:
        copy(source, destination)
        mapping.append({'source': rel(source), 'copy': rel(destination), 'sha256': row['sha256'], 'bytes': row['bytes'], 'raw_bytes_equal': True})
    copy(TMP / 'archive_s4_review.py', ARCHIVE / 'archive_s4_review.py')
    copy(TMP / 'run_archive.py', ARCHIVE / 'run_archive.py')
    save(ARCHIVE / 'raw_copy_mapping.json', {'schema_version': 1, 'copies': mapping, 'count': len(mapping), 'bytes': sum(row['bytes'] for row in mapping), 'originals_retained': True, 'copied_manifest_itself': True, 'scratch_scanned': False})
    save(ARCHIVE / 'source_and_g1_inventory.json', {'schema_version': 1, 'head': head, 'source_files': source_rows, 'source_count': len(source_rows), 'developer_manifest_files': 197, 'developer_runs': g1_inventory, 'all_g1_run_files_bound': True, 'developer_manifest': inventory(manifest_path), 'source_freeze': inventory(freeze_path), 'originals_retained': True})
    compile_native = read(REVIEW / 'independent_compile_native.json')
    simulation_native = read(REVIEW / 'independent_simulation_native.json')
    save(ARCHIVE / 'archive_result.json', {
        'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'review_status': receipt['status'],
        'created_utc8': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'source_commit': head, 'review_receipt': inventory(receipt_path), 'source_files': 37, 'developer_files': 197,
        'raw_files': 36, 'raw_bytes': 474943, 'raw_copies_with_manifest': len(mapping), 'raw_bytes_with_manifest': sum(row['bytes'] for row in mapping),
        'review_evidence_checks': receipt['evidence_checks'], 'independent_rtl': receipt['independent_rtl'],
        'original_compile_native': compile_native, 'original_simulation_native': simulation_native,
        'maximum_cache_bytes_from_original_native_records': max(compile_native['cache_bytes'], simulation_native['cache_bytes']),
        'preserved_review_failure': receipt['preserved_review_failure'], 'original_limitations': receipt['limitations'],
        'reviewer_r01_native_exit_code': None, 'reviewer_r01_native_exit_limitation': '原回执明确未持久化该码；不推断或补造。原失败JSON和脚本逐字节保留。',
        'collector_bootstrap_diagnostics': [
            {'step': '首次shell参数未获得Git Bash', 'tool_exit_code': 1, 'native_child_exit_code': None, 'effect': 'pwd命令未识别，只读启动失败，未写文件。'},
            {'step': 'PowerShell调用Bash缺少调用运算符', 'tool_exit_code': 1, 'native_child_exit_code': None, 'effect': 'ParserError，仅命令解析失败，未启动Bash或写文件。'}
        ],
        's4_sta': 'NOT_RUN', 'new_109_full_network': 'NOT_RUN', 'csr_runtime_timer_whole_core': 'NOT_RUN',
        'postroute_bit_hardware': 'NOT_RUN', 'g3_g4_g5': 'NOT_RUN', 's3_sta_prior_result': 'FAIL_TIMING_WNS_MINUS_18.745_NS',
        'collector_peak_memory': 'NOT_MEASURED', 'scratch_scanned': False, 'review_or_model_rerun': False,
    })
    checks = [
        original_native_check('原独立审查r03核验', 'audit_r03_native.json', 'PASS'),
        original_native_check('原独立RTL编译', 'independent_compile_native.json', 'PASS'),
        original_native_check('原独立RTL仿真', 'independent_simulation_native.json', 'PASS'),
        original_native_check('原G1证据包装', 'delivery_evidence_native.json', 'PASS'),
        original_native_check('原G1输入检查真实未冻结失败', 'delivery_inputs_native.json', 'FAIL'),
        {'name': 'S4综合STA及CSR计时器整core、109新闭包、postroute、bit、G3', 'status': 'NOT_RUN', 'command': None, 'exit_code': None, 'reason': '本次仅封装已有G2；未冻结物理接口和旧S3时序失败保持。'},
    ]
    wrapper = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': ARCHIVE.name, 'source_commit': head, 'evidence_dir': rel(ARCHIVE), 'interfaces': main['interfaces'], 'files': list(dependencies.values()), 'checks': checks,
        'tool_versions': {'python': sys.version, 'stage_checker_sha256': STAGE_SHA, 'original_reviewer_verilator': main['tool_versions']['verilator']},
        'limitations': [
            '仅归档原件完整性PASS及原独立PASS_G2_ONLY；本Collector不是新独立审查。',
            '保留G1 r01至r15全部原件路径SHA；37源码与197项Developer绑定再次实读核验；旧G1 NOT_RUN文字是当时事实，不改原清单。',
            '36份Reviewer原件474943B及raw清单自身均复制；r01 bootstrap状态误期望失败和r02/r03成功完整保留。原r01退出码未持久化，不补造。',
            'physical0.1.1未冻结、50MHz目标不变，inputs原生2按FAIL记录；未执行项NOT_RUN且退出码null。',
            '未执行STA、109新闭包、CSR/runtime计时器整core、postroute、bit或实板；S3 WNS -18.745ns失败不关闭，G3/G4/G5不通过。',
            '仅复制原清单列出的轻量原件，不扫描scratch、obj_dir或checker_fixture；原编译峰659759104B不是本Collector峰值，最大缓存由原native记录297490447B得出。',
            '最终检查动态日志仅留本次tmp；封存已关闭初轮日志以避免清单自引用，正式文件清单含原清单自身。',
        ]}
    wrapper['files'] += [binding(path, 'source' if path.suffix in {'.py', '.sv'} else 'log' if path.suffix == '.log' else 'result') for path in archive_files()]
    save(ARCHIVE / 'delivery_manifest_r01.json', wrapper)
    records = package(ARCHIVE / 'delivery_manifest_r01.json', 'initial')
    save(TMP / 'collector_inner_result.json', {'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'seconds': time.perf_counter() - started, 'copies': len(mapping), 'raw_bytes_with_manifest': sum(row['bytes'] for row in mapping), 'commands': records})
    print(json.dumps({'status': 'PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'copies': len(mapping), 'seconds': time.perf_counter() - started}))


def seal():
    started = time.perf_counter()
    wrapper = read(ARCHIVE / 'delivery_manifest_r01.json')
    for row in wrapper['files'] + wrapper['interfaces']:
        checked(row['path'], row['sha256'])
    for name in ['collector.native.json', 'collector.stdout.log', 'collector.stderr.log', 'collector_inner_result.json'] + [f'initial_{mode}.{suffix}' for mode in ['evidence', 'inputs'] for suffix in ['stdout.log', 'stderr.log', 'native.json']]:
        copy(TMP / name, ARCHIVE / name)
    native = read(ARCHIVE / 'collector.native.json')
    require(native['native_exit_code'] == 0, 'Collector原生码非0')
    save(ARCHIVE / 'closed_archive_inventory.json', {'schema_version': 1, 'files': [inventory(path) for path in archive_files()], 'scope': '本清单生成前已关闭的正式文件，bytes单独记录；本清单自身和最终wrapper由最终清单绑定。'})
    wrapper['files'] = [row for row in wrapper['files'] if not row['path'].startswith(rel(ARCHIVE) + '/')] + [binding(path, 'source' if path.suffix in {'.py', '.sv'} else 'log' if path.suffix == '.log' else 'result') for path in archive_files()]
    wrapper['checks'].append({'name': '原字节归档Collector', 'status': 'PASS', 'command': subprocess.list2cmdline(native['command']), 'exit_code': 0, 'reason': '37份副本逐字节相同，37现行源码和197项G1绑定一致，全部15个G1运行目录原件绑定。'})
    for mode, status in [('evidence', 'PASS'), ('inputs', 'FAIL')]:
        record = read(ARCHIVE / f'initial_{mode}.native.json')
        wrapper['checks'].append({'name': 'Collector初轮包装_' + mode, 'status': status, 'command': subprocess.list2cmdline(record['command']), 'exit_code': record['native_exit_code'], 'reason': '保存真实原生检查码；evidence只证明包装，inputs2保留物理候选未冻结及未执行依赖阻断。'})
    final = ARCHIVE / 'delivery_manifest_r02.json'
    save(final, wrapper)
    commands = package(final, 'final')
    for row in wrapper['files'] + wrapper['interfaces']:
        checked(row['path'], row['sha256'])
    mapping = read(ARCHIVE / 'raw_copy_mapping.json')
    for row in mapping['copies']:
        source, destination = checked(row['source'], row['sha256']), checked(row['copy'], row['sha256'])
        require(source.stat().st_size == destination.stat().st_size == row['bytes'], '最终副本长度不同')
    receipt = read(REVIEW / 'review_receipt.json')
    for name, expected in receipt['source_sha256'].items():
        checked(name, expected)
    rows = [inventory(path) for path in archive_files()]
    result = {'status': 'STOP_PASS_ARCHIVE_RAW_INTEGRITY_ONLY', 'review_status': 'PASS_G2_ONLY', 'manifest': inventory(final), 'formal_files': rows, 'formal_file_count': len(rows), 'formal_total_bytes': sum(row['bytes'] for row in rows), 'manifest_files': len(wrapper['files']), 'manifest_interfaces': len(wrapper['interfaces']), 'total_bindings': len(wrapper['files']) + len(wrapper['interfaces']), 'raw_copy_count': mapping['count'], 'raw_copy_bytes': mapping['bytes'], 'source_count': 37, 'developer_files': 197, 'all_final_bindings_verified': True, 'all_raw_copies_equal': True, 'native_commands': commands, 'seconds': time.perf_counter() - started, 'collector_peak_memory': 'NOT_MEASURED', 'review_or_model_rerun': False, 'hardware': 'NOT_RUN'}
    save(TMP / 'final_status.json', result)
    print(json.dumps({key: value for key, value in result.items() if key not in {'formal_files', 'native_commands'}}, ensure_ascii=True))


if __name__ == '__main__':
    phase = sys.argv[1]
    try:
        {'collect': collect, 'seal': seal}[phase]()
    except BaseException as error:
        failure = TMP / f'{phase}_failure.json'
        if not failure.exists():
            save(failure, {'status': 'COLLECTOR_FAILURE_PRESERVED', 'error': repr(error)})
        raise
