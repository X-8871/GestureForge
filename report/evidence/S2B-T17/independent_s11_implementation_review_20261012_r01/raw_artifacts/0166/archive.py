import ctypes
import hashlib
import json
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path.cwd().resolve()
SCRATCH = Path(__file__).resolve().parent
ORIGIN = ROOT / 'tmp/2B/S2B-T17/independent_s11_implementation_review_20261012_r01'
MAIN = ROOT / 'report/evidence/S2B-T17/s11_implementation_20261012_r01'
ARCHIVE = ROOT / 'report/evidence/S2B-T17/independent_s11_implementation_review_20261012_r01'
SOURCE_COMMIT = 'a710ec431474841a81912a6055f861e811a151e3'
EVIDENCE_HEAD = '932051cdacdf02f729d6a7554b07118d05e96aa4'
DISK_LIMIT = 80 * 1024 * 1024
TREE_LIMIT = 256 * 1024 * 1024
TIME_LIMIT = 180
START = time.perf_counter()
OBSERVED_RSS_MAX = 0
ROWS = []
FILES = {}
STORED = {}


def relative(path):
    return path.relative_to(ROOT).as_posix()


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def size_total():
    return sum(path.stat().st_size for directory in (SCRATCH, ARCHIVE)
               for path in directory.rglob('*') if path.is_file())


class MemoryCounters(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
        'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
        'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]


KERNEL = ctypes.WinDLL('kernel32', use_last_error=True)
PSAPI = ctypes.WinDLL('psapi', use_last_error=True)
KERNEL.GetCurrentProcess.restype = wintypes.HANDLE
KERNEL.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
KERNEL.OpenProcess.restype = wintypes.HANDLE
KERNEL.CloseHandle.argtypes = [wintypes.HANDLE]
PSAPI.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]


def rss(handle):
    counters = MemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    if not PSAPI.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
        raise OSError(ctypes.get_last_error())
    return counters.WorkingSetSize


def budget(child=None):
    global OBSERVED_RSS_MAX
    observed = rss(KERNEL.GetCurrentProcess())
    if child is not None and child.poll() is None:
        handle = KERNEL.OpenProcess(0x0400 | 0x0010, False, child.pid)
        if handle:
            try:
                observed += rss(handle)
            finally:
                KERNEL.CloseHandle(handle)
    OBSERVED_RSS_MAX = max(OBSERVED_RSS_MAX, observed)
    assert observed <= TREE_LIMIT, ('OWNED_RSS_LIMIT', observed)
    assert size_total() <= DISK_LIMIT, ('DISK_LIMIT', size_total())
    assert time.perf_counter() - START <= TIME_LIMIT, 'TIME_LIMIT'


def exact_file(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    assert path.resolve().is_relative_to(ROOT), str(path)
    return path


def add(path, expected=None, role='input', purpose='原字节恢复'):
    exact_file(path)
    actual = sha(path)
    if expected is not None:
        assert actual == expected, str(path)
    if actual in STORED:
        destination = STORED[actual]
    else:
        destination = ARCHIVE / 'raw_artifacts' / f'{len(STORED):04d}' / path.name
        destination.parent.mkdir(parents=True, exist_ok=False)
        assert not destination.exists()
        shutil.copyfile(path, destination)
        assert sha(destination) == actual
        STORED[actual] = destination
    archive_role = 'source' if role == 'source' or path.suffix == '.py' else role
    entry = {'path': relative(destination), 'sha256': actual, 'role': archive_role}
    previous = FILES.get(entry['path'])
    if previous is None or archive_role == 'source':
        FILES[entry['path']] = entry
    ROWS.append({'original_path': relative(path), 'archive_path': relative(destination),
                 'sha256': actual, 'bytes': path.stat().st_size, 'original_role': role,
                 'purpose': purpose})
    budget()
    return destination


def local_entry(path, role):
    return {'path': relative(path), 'sha256': sha(path), 'role': role}


def run_check(mode, manifest, label):
    # 只运行只读交付检查器；不执行任何RTL、Vivado、模型或实物任务。
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'verification/check_stage_delivery.py'),
               '--mode', mode, '--project-root', str(ROOT), '--manifest', str(manifest)]
    stdout_path = SCRATCH / f'{label}.stdout.log'
    stderr_path = SCRATCH / f'{label}.stderr.log'
    native_path = SCRATCH / f'{label}.native.json'
    assert not stdout_path.exists() and not stderr_path.exists() and not native_path.exists()
    started = time.perf_counter()
    with stdout_path.open('wb') as output, stderr_path.open('wb') as error:
        child = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=error)
        try:
            while child.poll() is None:
                budget(child)
                time.sleep(0.05)
        except BaseException:
            child.terminate()
            child.wait(timeout=10)
            raise
    result = {'command': command, 'native_exit_code': child.returncode,
              'elapsed_seconds': time.perf_counter() - started,
              'stdout': local_entry(stdout_path, 'log'), 'stderr': local_entry(stderr_path, 'log'),
              'tool_version': sys.version, 'sampled_self_and_direct_child_rss_peak_bytes': OBSERVED_RSS_MAX,
              'absolute_process_tree_peak_bytes': None}
    write_json(native_path, result)
    assert child.returncode == (0 if mode == 'evidence' else 2), result
    return result, (stdout_path, stderr_path, native_path)


def main():
    assert SCRATCH.is_dir() and ARCHIVE.is_dir() and ORIGIN.is_dir()
    assert not list(ARCHIVE.iterdir())
    pinned = {'final_review_receipt.json': '5bbaaa083f904b557a33da5afe250fdff334f31ef0419507199a744e8bf63522',
              'raw_manifest.jsonl': '8fc1f8da9fe6d3f18f530d6f20d1120f6582f7fb57e5cf96a5402143208ad827'}
    for name, expected in pinned.items():
        assert sha(exact_file(ORIGIN / name)) == expected
    assert sha(exact_file(MAIN / 'delivery_manifest_r02.json')) == 'a760ec030d6f858cfa508e533ab907d139078458879462e0ee2f2738ed610035'
    review = json.loads((ORIGIN / 'final_review_receipt.json').read_text(encoding='utf-8'))
    main_manifest = json.loads((MAIN / 'delivery_manifest_r02.json').read_text(encoding='utf-8'))
    assert review['status'] == 'PASS' and review['checks_count'] == 59
    assert review['actual_sta_status'] == 'FAIL' and review['budget_status'] == 'BLOCKED'
    assert review['source_commit'] == SOURCE_COMMIT and review['actual_evidence_head'] == EVIDENCE_HEAD
    raw = [json.loads(line) for line in (ORIGIN / 'raw_manifest.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(raw) == 177 and len({row['path'] for row in raw}) == 177
    source_binding = json.loads((MAIN / 's11_implementation_source_binding.json').read_text(encoding='utf-8'))
    closed_binding = json.loads((MAIN / 'pnr_closed_binding.json').read_text(encoding='utf-8'))
    assert source_binding['source_commit'] == SOURCE_COMMIT and source_binding['source_count'] == 43
    assert source_binding['clock_hz'] == 50000000 and source_binding['visibility'] == 0
    original_files = {relative(path): sha(path) for path in ORIGIN.iterdir() if path.is_file()}
    extra_sources = [(ROOT / row['snapshot'], row['sha256']) for row in source_binding['source_files']]
    estimated = sum((ROOT / row['path']).stat().st_size for row in raw) + sum(path.stat().st_size for path, _ in extra_sources)
    # 先按已知哈希去重评估上限，再复制；保留6MiB用于清单及包装日志。
    unique_sizes = {}
    for row in raw:
        unique_sizes.setdefault(row['sha256'], (ROOT / row['path']).stat().st_size)
    for path, expected in extra_sources:
        unique_sizes.setdefault(expected, path.stat().st_size)
    for path in ORIGIN.iterdir():
        if path.is_file():
            unique_sizes.setdefault(sha(path), path.stat().st_size)
    assert sum(unique_sizes.values()) + size_total() + 6 * 1024 * 1024 < DISK_LIMIT
    restoration_verified = 0
    for entry in closed_binding['mapping']:
        old, saved = entry['original'], entry['saved']
        assert old['sha256'] == saved['sha256'] and old['bytes'] == saved['bytes']
        saved_path = exact_file(ROOT / saved['path'])
        assert saved_path.stat().st_size == saved['bytes'] and sha(saved_path) == saved['sha256']
        restoration_verified += 1
        budget()
    assert restoration_verified == 509
    for row in raw:
        add(ROOT / row['path'], row['sha256'], row['role'], '177项原独审输入与结果绑定')
    represented = {row['original_path'] for row in ROWS}
    for path in sorted(ORIGIN.iterdir()):
        if path.is_file() and relative(path) not in represented:
            add(path, original_files[relative(path)], 'source' if path.suffix == '.py' else 'log' if path.suffix == '.log' else 'result', '独审脚本、原回执、raw索引及两轮native1异常原件')
    source_recovery = []
    for row in source_binding['source_files']:
        snapshot = exact_file(ROOT / row['snapshot'])
        assert snapshot.stat().st_size == row['bytes'] and sha(snapshot) == row['sha256']
        destination = add(snapshot, row['sha256'], 'source', '43源RAW快照恢复绑定')
        source_recovery.append({'production_path': row['path'], 'original_snapshot': row['snapshot'],
                                'archive_path': relative(destination), 'raw_sha256': row['sha256'], 'bytes': row['bytes']})
    add(Path(__file__).resolve(), role='source', purpose='本次归档脚本与命令来源')
    add(SCRATCH / 'inspect.py', role='source', purpose='归档前轻量体积核验脚本')
    mapping_path = ARCHIVE / 'archive_mapping.json'
    write_json(mapping_path, {'schema_version': 1, 'source_commit': SOURCE_COMMIT, 'actual_evidence_head': EVIDENCE_HEAD,
                              'mapping': ROWS, 'source_recovery': source_recovery,
                              'verified_original_restoration_count': restoration_verified,
                              'storage_policy': '相同SHA共用一份原字节；按mapping恢复精确原路径；不是复制整个509历史闭包'})
    FILES[relative(mapping_path)] = local_entry(mapping_path, 'result')
    receipt_path = ARCHIVE / 'archive_receipt.json'
    write_json(receipt_path, {'status': 'PASS_ARCHIVE_BINDING_ONLY', 'review_status': review['status'],
                              'review_scope': review['scope'], 'checks_count': 59,
                              'source_commit': SOURCE_COMMIT, 'actual_evidence_head': EVIDENCE_HEAD,
                              'profile': source_binding['profile'], 'physical_interface_version': '0.1.1',
                              'physical_interface_frozen': False, 'actual_sta_status': 'FAIL', 'budget_status': 'BLOCKED',
                              'original_manifest_entries': 177, 'source_recovery_count': 43,
                              'original_restoration_verified': restoration_verified,
                              'mapping_count': len(ROWS), 'physical_raw_copies': len(STORED),
                              'payload_bytes': sum(path.stat().st_size for path in STORED.values()),
                              'command': [sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve())],
                              'python': sys.version, 'elapsed_at_archive_seconds': time.perf_counter() - START,
                              'sampled_self_and_direct_child_rss_peak_bytes': OBSERVED_RSS_MAX,
                              'absolute_process_tree_peak_bytes': None,
                              'limits': {'disk_bytes': DISK_LIMIT, 'tree_bytes': TREE_LIMIT, 'seconds': TIME_LIMIT},
                              'limitations': ['独审仅59项失败事实准确性；业务STA FAIL和预算BLOCKED未改变',
                                              '保留两轮review native1原stderr与脚本快照；不重跑审查',
                                              '内存采样仅包装器及直接checker；短暂Git只读子进程与绝对整树峰未测',
                                              'bundled Python无psutil探针native1；没有安装依赖或操作实际任务PID',
                                              '没有Git提交、RTL、Vivado、ROSS或实物操作']})
    FILES[relative(receipt_path)] = local_entry(receipt_path, 'result')
    checks = [{'name': '独审59项失败事实准确性', 'status': 'PASS', 'command': subprocess.list2cmdline(review['commands'][2]['command']), 'exit_code': 0,
               'reason': '仅采用原独审实际native0与固定原回执，不批准STA或部署'},
              {'name': '实际PNR STA业务状态', 'status': 'FAIL', 'command': 'verification/check_s2b_synth_timing.py --mode implementation', 'exit_code': 2,
               'reason': '原独审确认分类器实际native2；WNS -3.201ns、908 setup失败，不因归档改判'},
              {'name': '实际重型全程预算覆盖', 'status': 'BLOCKED', 'command': None, 'exit_code': None,
               'reason': review['budget_reason']},
              {'name': 'bit runtime及板上验收', 'status': 'NOT_RUN', 'command': None, 'exit_code': None,
               'reason': '没有bit部署、实板G3/G4/G5或阶段2B完成批准'}]
    # 业务FAIL命令采用原主清单中真实分类命令，避免重构命令。
    classifier = [row for row in main_manifest['checks'] if row['status'] == 'FAIL' and row['exit_code'] == 2 and 'timing' in (row['command'] or '')]
    assert classifier
    checks[1]['command'] = classifier[0]['command']
    manifest = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17',
                'run_id': ARCHIVE.name, 'source_commit': SOURCE_COMMIT, 'evidence_dir': relative(ARCHIVE),
                'interfaces': main_manifest['interfaces'], 'tool_versions': {'python': sys.version, 'archive': 'Python标准库原字节复制/SHA256'},
                'files': list(FILES.values()), 'checks': checks,
                'limitations': receipt_path.read_text(encoding='utf-8') and json.loads(receipt_path.read_text(encoding='utf-8'))['limitations']}
    first_manifest = ARCHIVE / 'delivery_manifest.json'
    write_json(first_manifest, manifest)
    evidence, evidence_paths = run_check('evidence', first_manifest, 'initial_evidence')
    inputs, inputs_paths = run_check('inputs', first_manifest, 'initial_inputs')
    for path in (*evidence_paths, *inputs_paths):
        add(path, role='log' if path.suffix == '.log' else 'result', purpose='本归档首版真实包装命令与日志')
    FILES[relative(first_manifest)] = local_entry(first_manifest, 'input')
    manifest['files'] = list(FILES.values())
    for name, result in (('归档首版evidence机器核验', evidence), ('归档首版inputs机器核验', inputs)):
        manifest['checks'].append({'name': name, 'status': 'PASS' if result['native_exit_code'] == 0 else 'FAIL',
                                   'command': subprocess.list2cmdline(result['command']), 'exit_code': result['native_exit_code'],
                                   'reason': '只读包装检查；inputs2由物理接口未冻结及业务FAIL/BLOCKED保持阻断'})
    final_manifest = ARCHIVE / 'delivery_manifest_r02.json'
    write_json(final_manifest, manifest)
    final_evidence, final_evidence_paths = run_check('evidence', final_manifest, 'final_evidence')
    final_inputs, final_inputs_paths = run_check('inputs', final_manifest, 'final_inputs')
    for original, expected in original_files.items():
        assert sha(exact_file(ROOT / original)) == expected
    for row in ROWS:
        assert sha(exact_file(ROOT / row['archive_path'])) == row['sha256']
    budget()
    summary = {'status': 'PASS_ARCHIVE_BINDING_ONLY', 'source_commit': SOURCE_COMMIT,
               'actual_evidence_head': EVIDENCE_HEAD, 'manifest': local_entry(final_manifest, 'result'),
               'original_entries_verified': 177, 'original_restoration_verified': restoration_verified,
               'source_recovery_count': 43, 'original_directory_files_unchanged': len(original_files),
               'copied_unique_raw_files': len(STORED), 'mapping_count': len(ROWS),
               'payload_bytes': sum(path.stat().st_size for path in STORED.values()),
               'archive_and_scratch_bytes': size_total(), 'elapsed_seconds': time.perf_counter() - START,
               'sampled_self_and_direct_child_rss_peak_bytes': OBSERVED_RSS_MAX,
               'absolute_process_tree_peak_bytes': None,
               'final_evidence': final_evidence, 'final_inputs': final_inputs,
               'final_native_records': [local_entry(path, 'input') for path in (*final_evidence_paths, *final_inputs_paths)],
               'limits': {'disk_bytes': DISK_LIMIT, 'tree_bytes': TREE_LIMIT, 'seconds': TIME_LIMIT},
               'own_reruns': 0, 'heavy_runs': 0, 'status_sta': 'FAIL', 'status_budget': 'BLOCKED',
               'limitations': json.loads(receipt_path.read_text(encoding='utf-8'))['limitations']}
    write_json(SCRATCH / 'wrapper_receipt.json', summary)
    print(json.dumps({key: summary[key] for key in ('status', 'manifest', 'copied_unique_raw_files', 'mapping_count', 'archive_and_scratch_bytes', 'elapsed_seconds', 'sampled_self_and_direct_child_rss_peak_bytes')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
