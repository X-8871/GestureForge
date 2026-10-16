import ast
import hashlib
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

root = Path(r'D:\FPGA_Competition\w2b')
sys.path.insert(0, str(root))
from verification import s2b_process_supervisor as supervisor

GIB = 1024 ** 3
expected_hashes = {
    'verification/s2b_process_supervisor.py': 'c1f1eb733675a0c316788198420940236f062363808648f84c5293caccc85ac3',
    'verification/test_s2b_process_supervisor.py': '5f9889891949b492dd87c0350c72844cabdb2cb7a721a31e0bf1e0886a0c04ed',
}
for relative, expected in expected_hashes.items():
    path = root / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, (relative, actual, expected)
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
print('AST_AND_SOURCE_HASHES PASS', json.dumps(expected_hashes, sort_keys=True))

manifest_path = root / 'report/evidence/S2B-T17/monitored_job_drain_20261016_r04/delivery_manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest_mismatches = []
for entry in manifest['files']:
    path = root / Path(entry['path'].replace('/', '\\'))
    if not path.is_file():
        manifest_mismatches.append((entry['path'], 'MISSING'))
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != entry['sha256']:
        manifest_mismatches.append((entry['path'], actual, entry['sha256']))
assert not manifest_mismatches, manifest_mismatches
print('R04_MANIFEST_FILE_HASHES PASS', len(manifest['files']))

invalid_cases = (
    ('slow_exit_code_gap_attack', {'max_sample_gap_seconds': 2.0}),
    ('oversized_drain_timeout_attack', {'drain_timeout_seconds': 20.0}),
    ('sample_interval_over_cap', {'sample_interval_seconds': 0.5}),
    ('stop_floor_below_hard_minimum', {'stop_floor_bytes': 2 * GIB - 1}),
    ('start_floor_below_stop_floor', {'start_floor_bytes': 2 * GIB - 1, 'stop_floor_bytes': 2 * GIB}),
)
for name, options in invalid_cases:
    memory_calls = []
    def memory_reader():
        memory_calls.append(True)
        raise AssertionError('invalid configuration reached memory query')
    with mock.patch.object(supervisor, '_load_job_guard') as load_guard:
        result = supervisor.supervise_process(
            name=name,
            command=[sys.executable, '-c', 'raise SystemExit(99)'],
            cwd=str(root),
            environment={},
            output_stream=io.StringIO(),
            timeout_seconds=30.0,
            memory_reader=memory_reader,
            **options,
        )
    assert result['status'] == 'FAIL_SUPERVISOR_CONFIG', (name, result['status'])
    assert not result['launch_attempted'], name
    assert not result['cleanup']['job_created'], name
    assert result['resource_monitor']['preflight'] is None, name
    assert not memory_calls, name
    load_guard.assert_not_called()
    print('REJECT_BEFORE_SIDE_EFFECT PASS', name, result['resource_monitor']['invalid_configuration_constraints'])

memory_calls = []
def boundary_memory_reader():
    memory_calls.append(True)
    raise OSError('stop at preflight after config acceptance')
with mock.patch.object(supervisor, '_load_job_guard') as load_guard:
    result = supervisor.supervise_process(
        name='exact_caps_boundary',
        command=[sys.executable, '-c', 'raise SystemExit(99)'],
        cwd=str(root),
        environment={},
        output_stream=io.StringIO(),
        timeout_seconds=30.0,
        memory_reader=boundary_memory_reader,
        sample_interval_seconds=0.25,
        max_sample_gap_seconds=1.0,
        drain_timeout_seconds=10.0,
        start_floor_bytes=2 * GIB,
        stop_floor_bytes=2 * GIB,
    )
assert result['status'] == 'FAIL_RESOURCE_PREFLIGHT_QUERY', result['status']
assert result['resource_monitor']['invalid_configuration_constraints'] == []
assert len(memory_calls) == 1
assert not result['launch_attempted'] and not result['cleanup']['job_created']
load_guard.assert_not_called()
print('EXACT_LIMITS_ACCEPTED PASS', result['status'])

class Clock:
    def __init__(self):
        self.value = 0.0
    def monotonic(self):
        return self.value
    def sleep(self, seconds):
        self.value += max(0.0, seconds)

class FakeJob:
    def __init__(self, clock, slow_query=False):
        self.clock = clock
        self.calls = 0
        self.slow_query = slow_query
    def pid_list(self):
        self.calls += 1
        if self.slow_query and self.calls == 4:
            self.clock.value = 5.1
        return []
    def accounting(self):
        return {'active_processes': 0, 'total_processes': 1}

class FakeGuard:
    WAIT_OBJECT_0 = 0
    WAIT_TIMEOUT = 258
    STILL_ACTIVE = 259
    def __init__(self, clock, slow_exit=False):
        self.clock = clock
        self.slow_exit = slow_exit
    def _api_wait(self, handle, milliseconds):
        return self.WAIT_OBJECT_0
    def _api_get_exit_code(self, handle):
        if self.slow_exit:
            self.clock.value = 5.1
        return 0

for attack in ('slow_final_exit_read_overall_deadline', 'slow_job_query_overall_deadline'):
    clock = Clock()
    job = FakeJob(clock, slow_query=attack == 'slow_job_query_overall_deadline')
    guard = FakeGuard(clock, slow_exit=attack == 'slow_final_exit_read_overall_deadline')
    with mock.patch.object(supervisor, '_load_job_guard', return_value=guard), \
         mock.patch.object(supervisor.time, 'monotonic', clock.monotonic), \
         mock.patch.object(supervisor.time, 'sleep', clock.sleep):
        try:
            supervisor._wait_for_empty_job(
                job,
                SimpleNamespace(process_handle=object()),
                10.0,
                allow_root_exit_drain=True,
                overall_deadline=5.0,
            )
        except supervisor._DrainWaitFailure as error:
            assert error.status == 'FAIL_TIMEOUT', (attack, error.status)
        else:
            raise AssertionError(attack + ' incorrectly passed')
    print('SLOW_OPERATION_DEADLINE_REJECTED PASS', attack, clock.value)
print('ALL_REVIEW_ATTACKS PASS')