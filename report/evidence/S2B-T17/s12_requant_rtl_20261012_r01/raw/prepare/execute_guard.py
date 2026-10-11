import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psutil

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
SELF = psutil.Process()
EXPECTED_SOURCE = 'c46ed3e1e8af0089b2a78434c0b34869a2b1f5cf11071688345828f4a9c28454'
ADMISSION = ROOT / 'tmp/2B/S2B-T17/s12_root_run_20261012_r01/offline_admission_before_requant_r01.json'


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            value.update(chunk)
    return value.hexdigest()


def write(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    assert sys.version_info[:3] == (3, 12, 10) and psutil.__version__ == '7.2.2'
    assert ADMISSION.is_file() and sha(ADMISSION) == '2403aa3bf916ccda7e29e8346f0db1e62c05fcd1a658f8fffd605e3838b26a0f'
    admission = json.loads(ADMISSION.read_text(encoding='utf-8'))
    assert admission['status'] == 'OFFLINE_ADMISSION_READY'
    assert admission['candidate_heavy_processes'] == [] and admission['unknown_candidates'] == []
    assert sha(HERE / 'prepare_manifest.json') == '300667b4874605630f3dc5bcf301ac63a0f011591d897638366c6dd1ae69527a'
    assert sha(HERE / 'execution_plan.json') == '5c54ec6a5ee8d80edda3000dbdaaebc22d360643b247666a238c11e1b0116226'
    assert (ROOT / 'src/s2b_conv_tile_engine.sv').is_file() and sha(ROOT / 'src/s2b_conv_tile_engine.sv') == EXPECTED_SOURCE
    prepared = json.loads((HERE / 'prepare_manifest.json').read_text(encoding='utf-8'))
    for row in prepared['prepared_files']:
        assert sha(HERE / row['path']) == row['sha256'], row['path']
    assert not (HERE / 'runs/execute_r01').exists()
    assert psutil.virtual_memory().available >= 2 * 1024**3
    assert shutil.disk_usage('C:\\').free >= 8 * 1024**3
    command = [sys.executable, '-B', '-X', 'utf8',
               'tmp/2B/S2B-T17/s12_requant_rtl_prepare_20261012_r01/native_wrapper.py',
               '--mode', 'execute', '--root-heavy-slot-granted', '--run-id', 'execute_r01']
    stdout = HERE / 'execute_r01.outer.stdout.log'
    stderr = HERE / 'execute_r01.outer.stderr.log'
    samples_path = HERE / 'execute_r01.outer.samples.jsonl'
    for path in (stdout, stderr, samples_path, HERE / 'execute_r01.outer.native.json'):
        assert not path.exists(), str(path)
    started = time.perf_counter()
    peak = 0
    minimum_ram = minimum_disk = None
    breach = None
    sample_count = 0
    with stdout.open('wb') as out, stderr.open('wb') as err, samples_path.open('w', encoding='utf-8', newline='\n') as stream:
        child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
        child_identity = psutil.Process(child.pid).create_time()
        try:
            while child.poll() is None:
                elapsed = time.perf_counter() - started
                total_rss = 0
                missing = []
                for process in [SELF] + SELF.children(recursive=True):
                    try:
                        total_rss += process.memory_info().rss
                    except psutil.NoSuchProcess:
                        missing.append(process.pid)
                ram = psutil.virtual_memory().available
                disk = shutil.disk_usage('C:\\').free
                size = sum(path.stat().st_size for path in HERE.rglob('*') if path.is_file())
                peak = max(peak, total_rss)
                minimum_ram = ram if minimum_ram is None else min(minimum_ram, ram)
                minimum_disk = disk if minimum_disk is None else min(minimum_disk, disk)
                row = {'elapsed_seconds': elapsed, 'owned_tree_rss_bytes': total_rss, 'available_ram_bytes': ram,
                       'c_disk_free_bytes': disk, 'scope_disk_bytes': size, 'exited_owned_pid_sample_missing': missing}
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
                stream.flush()
                sample_count += 1
                if ram < 512 * 1024**2:
                    breach = 'AVAILABLE_RAM_BELOW_512MIB'
                elif disk < 8 * 1024**3:
                    breach = 'C_DISK_BELOW_8GIB'
                elif total_rss > 1024**3:
                    breach = 'OWNED_TREE_ABOVE_1GIB'
                elif size > 640 * 1024**2:
                    breach = 'SCOPE_ABOVE_640MIB'
                elif elapsed > 600:
                    breach = 'OVERALL_600_SECONDS'
                if breach:
                    raise RuntimeError(breach)
                time.sleep(0.075)
        except BaseException:
            # 只终止此包装器创建、出生时间核对相同的唯一自有子树。
            if child.poll() is None and psutil.Process(child.pid).create_time() == child_identity:
                subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], stdout=err, stderr=err, timeout=30, check=False)
                child.wait(timeout=30)
            raise
        finally:
            record = {'command': command, 'cwd': str(ROOT), 'native_exit_code': child.poll(),
                      'elapsed_seconds': time.perf_counter() - started,
                      'sampled_owned_tree_rss_peak_bytes': peak, 'absolute_tree_peak_bytes': None,
                      'minimum_sampled_available_ram_bytes': minimum_ram, 'minimum_sampled_c_disk_free_bytes': minimum_disk,
                      'samples': sample_count, 'budget_breach': breach,
                      'root_admission': {'path': str(ADMISSION), 'sha256': sha(ADMISSION)},
                      'source_before_sha256': EXPECTED_SOURCE,
                      'source_after_sha256': sha(ROOT / 'src/s2b_conv_tile_engine.sv'),
                      'stdout': {'path': str(stdout), 'sha256': sha(stdout)},
                      'stderr': {'path': str(stderr), 'sha256': sha(stderr)},
                      'samples_path': str(samples_path),
                      'sample_bytes_before_final_flush_sha_not_claimed': True,
                      'python': sys.version, 'psutil': psutil.__version__,
                      'limitations': ['仅二態白盒完整引擎requant及提取组合块mutants；公共FSM与X/Z结论另行验证',
                                      '仅当前Python及其自有子树离散采样；没有枚举重型、设备或其他任务PID',
                                      '没有自动启动第二重型任务、覆盖RunId或修改生产']}
            write(HERE / 'execute_r01.outer.native.json', record)
    assert sha(ROOT / 'src/s2b_conv_tile_engine.sv') == EXPECTED_SOURCE
    if child.returncode != 0:
        raise RuntimeError('INNER_NATIVE_EXIT=' + str(child.returncode))
    result = HERE / 'runs/execute_r01/result.json'
    assert result.is_file(), 'SEMANTIC_RESULT_MISSING'
    print(json.dumps({'status': 'EXECUTION_RETURNED_NATIVE0', 'result_path': str(result), 'result_sha256': sha(result),
                      'elapsed_seconds': time.perf_counter() - started, 'sampled_owned_tree_rss_peak_bytes': peak}, ensure_ascii=False))


if __name__ == '__main__':
    main()
