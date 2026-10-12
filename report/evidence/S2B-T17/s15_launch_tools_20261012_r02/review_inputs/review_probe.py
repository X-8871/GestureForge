"""独立只读工具审查；夹具和原生原件仅写入本审查目录。"""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

HERE = Path(__file__).parent
ROOT = HERE.parents[3]
WORK = ROOT / 'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01'
PACKAGE = ROOT / 'report/evidence/S2B-T17/s15_launch_tools_20261012_r01'
sys.path.insert(0, str(WORK))
import collector as c
import guard
import native_capture as n
import selftest
import runtime_consumer as consumer
import compat_pins as pins

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')

results = {'baseline_head': subprocess.check_output(['git', '-c', 'core.longpaths=true', 'rev-parse', 'HEAD'], cwd=ROOT).decode('ascii').strip(), 'checks': []}
def result(name, passed, **details):
    results['checks'].append(dict(name=name, passed=passed, **details))

manifest_path = PACKAGE / 'delivery_manifest.json'
receipt_path = PACKAGE / 'g1_receipt.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
results['frozen_inputs'] = [{'path': str(p), 'sha256': digest(p)} for p in (manifest_path, receipt_path)]
bad = []
for row in manifest['files']:
    p = c.exact(ROOT / row['path'])
    if digest(p) != row['sha256']:
        bad.append(row['path'])
result('formal_manifest_all_hashes', not bad, count=len(manifest['files']), mismatches=bad)
bad = []
for row in receipt['tools'] + receipt['diffs']:
    p = c.exact(ROOT / row['path'])
    if digest(p) != row['sha256'] or p.stat().st_size != row['bytes']:
        bad.append(row['path'])
result('frozen_original_tools_and_diffs', not bad, count=len(receipt['tools']) + len(receipt['diffs']), mismatches=bad)
results['developer_results_summary'] = {key: {k: value[k] for k in ('status', 'methods', 'mock_tests', 'actual_canaries') if k in value} for key, value in receipt['test_results'].items()}

# 独立序列证明退出对象不额外否决，但出生变化与未知始终阻断。
for label, rounds, expected_closed, expected_scans in [
    ('same_alive_with_confirmed_exit', [([(100, 1)], [], []), ([(100, 1)], [], [{'status': 'ABSENT'}])], True, 2),
    ('previous_alive_exit_three_rounds', [([(100, 1), (200, 2)], [], []), ([(100, 1)], [], [{'status': 'ABSENT'}]), ([(100, 1)], [], [])], True, 3),
    ('continuous_birth_three_rounds', [([(100, 1), (200, 2)], [], []), ([(100, 1), (200, 2), (300, 3)], [], []), ([(100, 1), (200, 2), (300, 3), (400, 4)], [], [])], False, 3),
    ('same_pid_changed_birth', [([(100, 1), (200, 2)], [], []), ([(100, 1), (200, 3)], [], []), ([(100, 1), (200, 4)], [], [])], False, 3),
    ('second_round_unknown', [([(100, 1)], [], []), ([(100, 1)], [{'reason': 'UNKNOWN'}], [])], False, 2),
]:
    monitor, root = selftest.monitor(selftest.World())
    iterator = iter(rounds)
    def scan(*args):
        identities, uncertain, exited = next(iterator)
        return [dict(pid=pid, create_time=birth) for pid, birth in identities], uncertain, exited
    monitor.collect_round = scan
    members, unknown, exits = monitor.collect(root)
    observation = monitor.collection_observation
    result(label, observation['closed'] == expected_closed and observation['scans'] == expected_scans and bool(unknown) != expected_closed, observation=observation)

# 六字段、出生复用和未知必须独立区分，不能从父退出推断子退出。
for field, value in [('exe', 'different.exe'), ('cwd', 'different'), ('cmdline', ['different']), ('ppid', 888)]:
    world = selftest.World()
    monitor, root = selftest.monitor(world)
    with patch.object(guard.psutil, 'Process', world.process):
        old = guard.base_identity(world.process(200))
        world.nodes[200][field] = value
        actual = monitor.readback_member(old)
    result('readback_drift_' + field, actual['status'] == 'IDENTITY_CHANGED', actual=actual)
world = selftest.World()
monitor, root = selftest.monitor(world)
with patch.object(guard.psutil, 'Process', world.process):
    old = guard.base_identity(world.process(200))
    world.make(200, 42, 100, 20)
    actual = monitor.readback_member(old)
result('readback_original_reuse', actual['status'] == 'ORIGINAL_PID_REUSED' and actual['new_object_untouched'], actual=actual)

# 流新鲜度与10秒硬间隔边界；5秒目标迟延必须在原件透明报告。
now = time.time()
identity = dict(pid=100, create_time=1, exe='fixture', cwd='fixture', cmdline=['fixture'], ppid=0)
guard_id = dict(identity, pid=200, ppid=100, create_time=2)
live = dict(kind='LIVE', identity=guard_id, monotonic_seconds=time.monotonic())
ready = dict(kind='READY', guard_identity=guard_id)
sample = dict(members=[identity], sample_ended_at_utc8=guard.now(), alerts=[], uncertain=[], collection_observation=dict(closed=True), tree_rss_bytes=6*1024**3, available_ram_bytes=512*1024**2, c_disk_free_bytes=8*1024**3)
for label, gap, age, expected in [('exact_limits', 10, 10, False), ('gap_exceeded', 10.001, 0, True), ('stream_stale', 5, 10.001, True), ('clock_future', 5, -0.001, True)]:
    reasons = consumer.evaluate([ready, live], [sample], identity, guard_id, [dict(mtime_age_seconds=age)], gap)
    result('consumer_' + label, bool(reasons) == expected, reasons=reasons)

# 构造拥有新绑定哈希的错误原生记录，验证门禁不能只凭浅层字段接受。
cache = HERE / 'native_gate_counterexamples'
cache.mkdir()
command = [sys.executable, '-X', 'utf8', '-B', str(WORK / 'collector.py'), 'collect', '--commit', 'b'*40, '--gate', str(HERE / 'gate.json')]
variants = [
    ('missing_identity_and_tool_metadata', {}),
    ('wrong_parent_birth', {'launcher_identity': dict(identity, pid=100, create_time=100), 'direct_child_identity': dict(guard_id, pid=200, create_time=1, ppid=999)}),
    ('tool_hash_changed', {'tool_bindings_before': [{'path': 'collector.py', 'sha256': 'a'*64}], 'tool_bindings_after': [{'path': 'collector.py', 'sha256': 'c'*64}]}),
    ('budget_stop_with_child_rc0', {'budget_stop': 'ELAPSED_GT_120_SECONDS', 'unknown_count': 1, 'unknown_samples': [{'phase': 'descendant_enumeration'}]}),
    ('wrong_collect_commit_gate', {'command': command[:6] + ['--commit', 'c'*40, '--gate', str(HERE / 'other_gate.json')]}),
]
for label, modifications in variants:
    prefix = 's15_runtime_' + label
    logs = []
    for suffix in ('stdout.bin', 'stderr.bin'):
        path = cache / (prefix + '.' + suffix)
        path.write_bytes(b'fixture\n')
        logs.append(c.binding(path))
    path = cache / (prefix + '.native.json')
    row = dict(mode='collect', prefix=prefix, native_exit_code=0, command=copy.deepcopy(command), direct_child_wait_returned=True, closed_logs=logs, stdout=logs[0], stderr=logs[1], fixture_test=True)
    row.update(modifications)
    save(path, row)
    try:
        with patch.object(c, 'CACHE', cache):
            accepted = c.runtime_native_records(dict(native_wrappers=[c.binding(path)]))
        result('reject_' + label, False, unexpected_accept=True, record_binding=c.binding(path), accepted_count=len(accepted))
    except (ValueError, KeyError, TypeError) as error:
        result('reject_' + label, True, rejection=repr(error))

# 实际原生轻量子仅打印并退出；记录直接wait和未知项，不启动工程或实物。
with patch.object(n, 'HERE', HERE), patch.object(n, 'ROOT', ROOT), patch.object(sys, 'argv', [str(WORK / 'native_capture.py'), 'review_native_canary', sys.executable, '-X', 'utf8', '-B', '-c', 'import time; print("独立审查轻量原生"); time.sleep(0.2)']), contextlib.redirect_stdout(io.StringIO()):
    native_code = n.main(dict(mode='collect', prefix='review_native_canary'))
native = json.loads((HERE / 'review_native_canary.native.json').read_text(encoding='utf-8'))
result('actual_native_wait_canary', native_code == 0 and native['native_exit_code'] == 0 and native['direct_child_wait_returned'], native_exit_code=native['native_exit_code'], direct_child_wait_returned=native['direct_child_wait_returned'], unknown_count=native['unknown_count'], known_terminal=native['known_descendants_same_identity_absent_at_observation'], elapsed_seconds=native['elapsed_seconds'], sampled_owned_tree_peak_bytes=native['sampled_owned_tree_peak_bytes'], entire_os_tree_terminal=native['entire_os_tree_terminal'])

results['production_files_modified'] = False
results['vivado_ross_hardware_executed'] = False
results['status'] = 'CHANGES_REQUIRED' if any(not row['passed'] for row in results['checks']) else 'PASS_TOOL_G2_ONLY'
save(HERE / 'review_probe_result.json', results)
print(json.dumps(dict(status=results['status'], checks=len(results['checks']), failures=[row['name'] for row in results['checks'] if not row['passed']], native_code=native_code), ensure_ascii=False))
