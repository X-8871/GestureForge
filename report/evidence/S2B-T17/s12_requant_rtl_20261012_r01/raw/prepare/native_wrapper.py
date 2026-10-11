import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psutil

HERE = Path(__file__).resolve().parent
TOOLCHAIN = Path(r'D:\FPGA_S2A_MSYS2_20261001\env')
MAX_DISK = 640 * 1024 * 1024
MAX_TREE = 1024 * 1024 * 1024
MAX_SECONDS = 600


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def tool_environment():
    bindir = TOOLCHAIN / 'mingw64/bin'
    makedir = TOOLCHAIN / 'usr/bin'
    for path in (bindir / 'verilator_bin.exe', bindir / 'g++.exe', makedir / 'make.exe'):
        assert path.is_file() and not path.is_symlink(), str(path)
    env = os.environ.copy()
    env['PATH'] = str(makedir) + os.pathsep + str(bindir) + os.pathsep + env.get('PATH', '')
    env['VERILATOR_ROOT'] = str(TOOLCHAIN / 'mingw64/share/verilator')
    env['PYTHONUTF8'] = '1'
    env['OMP_NUM_THREADS'] = '1'
    return bindir / 'verilator_bin.exe', env


def owned_tree_sample():
    owner = psutil.Process()
    processes = [owner] + owner.children(recursive=True)
    total = 0
    missing = []
    for process in processes:
        try:
            total += process.memory_info().rss
        except psutil.NoSuchProcess:
            # 刚退出的自有子进程只标离散采样缺失，不能填造绝对峰。
            missing.append(process.pid)
    return total, missing


def run(label, command, run, env, began, stats):
    stdout = run / (label + '.stdout.log')
    stderr = run / (label + '.stderr.log')
    assert not stdout.exists() and not stderr.exists()
    started = time.perf_counter()
    samples = []
    breach = None
    with stdout.open('wb') as out, stderr.open('wb') as err:
        child = subprocess.Popen(command, cwd=HERE, env=env, stdout=out, stderr=err)
        last_disk = 0.0
        try:
            while child.poll() is None:
                elapsed = time.perf_counter() - began
                rss, missing = owned_tree_sample()
                samples.append({'elapsed_seconds': elapsed, 'owned_tree_rss_bytes': rss, 'missing_exited_owned_pids': missing})
                stats['sampled_tree_rss_peak_bytes'] = max(stats['sampled_tree_rss_peak_bytes'], rss)
                if rss > MAX_TREE:
                    breach = 'OWNED_TREE_RSS_LIMIT'
                if elapsed > MAX_SECONDS:
                    breach = 'OVERALL_EXECUTION_TIMEOUT'
                if elapsed - last_disk >= 1:
                    last_disk = elapsed
                    size = sum(path.stat().st_size for path in HERE.rglob('*') if path.is_file())
                    stats['sampled_scope_disk_peak_bytes'] = max(stats['sampled_scope_disk_peak_bytes'], size)
                    if size > MAX_DISK:
                        breach = 'CACHE_AND_OUTPUT_DISK_LIMIT'
                if breach:
                    raise RuntimeError(breach)
                time.sleep(0.075)
        except BaseException:
            # 只终止当前Popen启动的自有编译/仿真子树；不枚举或操作其他任务。
            subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], stdout=err, stderr=err, timeout=30, check=False)
            child.wait(timeout=30)
            raise
        finally:
            record = {'command': command, 'native_exit_code': child.poll(), 'elapsed_seconds': time.perf_counter() - started,
                      'stdout': {'path': str(stdout), 'sha256': sha(stdout)},
                      'stderr': {'path': str(stderr), 'sha256': sha(stderr)}, 'budget_breach': breach,
                      'sampled_tree_rss_peak_bytes': stats['sampled_tree_rss_peak_bytes'], 'absolute_tree_peak_bytes': None,
                      'scope': '包装器与其recursive自有子树离散采样；不查询现有重型或实物进程'}
            write(run / (label + '.native.json'), record)
            sample_path = run / (label + '.samples.jsonl')
            assert not sample_path.exists()
            with sample_path.open('w', encoding='utf-8', newline='\n') as stream:
                for row in samples:
                    stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    if child.returncode != 0:
        raise RuntimeError(f'{label}: native_exit_code={child.returncode}')
    return record


def main():
    parser = argparse.ArgumentParser(description='S12 requant仅计划或ROOT批准后的单job完整RTL/组合块变异核验')
    parser.add_argument('--mode', choices=('plan', 'execute'), default='plan')
    parser.add_argument('--root-heavy-slot-granted', action='store_true')
    parser.add_argument('--run-id', default='execute_r01')
    args = parser.parse_args()
    assert sys.version_info[:3] == (3, 12, 10) and psutil.__version__ == '7.2.2'
    assert re.fullmatch(r'[a-zA-Z0-9_-]+', args.run_id)
    prepared = json.loads((HERE / 'prepare_manifest.json').read_text(encoding='utf-8'))
    for row in prepared['prepared_files']:
        assert sha(HERE / row['path']) == row['sha256'], row['path']
    verilator, env = tool_environment()
    run_dir = HERE / 'runs' / args.run_id
    command = [str(verilator), '--binary', '--timing', '--timescale', '1ns/1ps', '-Wall', '-Wno-fatal',
               '-Wno-BLKANDNBLK', '-j', '1', '--threads', '1', '--output-split', '10000', '--output-split-cfuncs', '100',
               '--top-module', 'tb_s12_requant', '--Mdir', str(run_dir / 'obj_dir'),
               '-MAKEFLAGS', 'PYTHON3=\"' + sys.executable + '\"', '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0 -O0',
               's2a_network_descriptor_pkg.sv', 'rq_original_engine.sv', 'rq_candidate_engine.sv',
               'requant_mutants.sv', 'tb_s12_requant.sv']
    binary = run_dir / 'obj_dir/Vtb_s12_requant.exe'
    plan = {'mode': args.mode, 'compile': command, 'simulation': [str(binary)], 'cwd': str(HERE),
            'python': sys.version, 'psutil': psutil.__version__,
            'full_module_inputs': prepared['sources'], 'vectors': prepared['vectors'], 'mutants': prepared['mutants'],
            'logs': [str(run_dir / (step + suffix)) for step in ('compile', 'simulation')
                     for suffix in ('.stdout.log', '.stderr.log', '.native.json', '.samples.jsonl')],
            'budgets': {'scope_bytes': MAX_DISK, 'owned_tree_bytes': MAX_TREE, 'overall_seconds': MAX_SECONDS},
            'compile_status': 'NOT_RUN', 'simulation_status': 'NOT_RUN', 'root_heavy_slot_required': True,
            'warnings_scope': '白盒用bench装载内部寄存器，clk恒0；仅关闭BLKANDNBLK诊断允许bench与原always_ff共存，未改生产FF或RTL逻辑。实际编译与全部oracle比较仍必须通过。',
            'limitations': prepared['limitations']}
    if args.mode == 'plan':
        destination = HERE / 'execution_plan.json'
        write(destination, plan)
        print(json.dumps({'status': 'PLAN_ONLY_NOT_COMPILED', 'vectors': prepared['vectors'], 'mutants': 7,
                          'plan_path': str(destination), 'plan_sha256': sha(destination)}, ensure_ascii=False))
        return
    assert args.root_heavy_slot_granted, 'ROOT_HEAVY_SLOT_REQUIRED'
    assert not run_dir.exists(), 'RUN_ID_EXISTS_DO_NOT_OVERWRITE'
    run_dir.mkdir(parents=True)
    began = time.perf_counter()
    stats = {'sampled_tree_rss_peak_bytes': 0, 'sampled_scope_disk_peak_bytes': 0}
    write(run_dir / 'execution_plan.json', plan)
    try:
        compile_record = run('compile', command, run_dir, env, began, stats)
        assert binary.is_file(), str(binary)
        simulation_record = run('simulation', [str(binary)], run_dir, env, began, stats)
        stdout = (run_dir / 'simulation.stdout.log').read_text(encoding='utf-8')
        matches = re.findall(r'S12_REQUANT_FULL_RTL_PASS vectors=(\d+) mutants=7 mismatches=0', stdout)
        assert matches == [str(prepared['vectors'])], matches
        kills = re.findall(r'MUTANT_SEMANTIC_KILLED id=(\d+) count=(\d+)', stdout)
        assert len(kills) == 7 and {int(index) for index, _ in kills} == set(range(7))
        assert all(int(count) > 0 for _, count in kills)
        assert len(re.findall(r'MUTANT_SEMANTIC_WITNESS id=', stdout)) == 7
        disk = sum(path.stat().st_size for path in HERE.rglob('*') if path.is_file())
        assert disk <= MAX_DISK and time.perf_counter() - began < MAX_SECONDS
        write(run_dir / 'result.json', {'status': 'PASS_FULL_RTL_REQUANT_WHITEBOX_AND_EXTRACTED_MUTANTS_ONLY',
                                      'compile': compile_record, 'simulation': simulation_record, 'semantic_kills': kills,
                                      'vectors': prepared['vectors'], 'disk_bytes': disk, 'stats': stats,
                                      'absolute_tree_peak_bytes': None, 'elapsed_seconds': time.perf_counter() - began,
                                      'limitations': prepared['limitations']})
    except BaseException as error:
        write(run_dir / 'wrapper_failure.json', {'status': 'FAIL', 'exception': repr(error), 'stats': stats,
                                                'elapsed_seconds': time.perf_counter() - began,
                                                'limitations': '保留所有原日志，不覆盖RunId；异常不是独审PASS或G1完成'})
        raise


if __name__ == '__main__':
    main()
