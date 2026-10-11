import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd().resolve()
RUN = HERE / 'runs/execute_r01'


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            result.update(chunk)
    return result.hexdigest()


def binding(path, role):
    assert path.is_file() and not path.is_symlink(), str(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size, 'role': role}


def main():
    prepared = json.loads((HERE / 'prepare_manifest.json').read_text(encoding='utf-8'))
    result = json.loads((RUN / 'result.json').read_text(encoding='utf-8'))
    outer = json.loads((HERE / 'execute_r01.outer.native.json').read_text(encoding='utf-8'))
    assert result['compile']['native_exit_code'] == result['simulation']['native_exit_code'] == outer['native_exit_code'] == 0
    assert outer['budget_breach'] is None
    assert outer['source_before_sha256'] == outer['source_after_sha256'] == 'c46ed3e1e8af0089b2a78434c0b34869a2b1f5cf11071688345828f4a9c28454'
    bindings = []
    for row in prepared['prepared_files']:
        path = HERE / row['path']
        assert sha(path) == row['sha256']
        bindings.append(binding(path, 'input' if path.name == 'vectors.txt' else 'source'))
    for row in prepared['sources']:
        path = Path(row['input'])
        assert sha(path) == row['input_raw_sha256']
        bindings.append(binding(path, 'source'))
    production = ROOT / 'src/s2b_conv_tile_engine.sv'
    assert sha(production) == outer['source_after_sha256']
    bindings.append(binding(production, 'source'))
    log = (RUN / 'simulation.stdout.log').read_text(encoding='utf-8')
    passes = re.findall(r'S12_REQUANT_FULL_RTL_PASS vectors=(\d+) mutants=7 mismatches=0', log)
    assert passes == [str(prepared['vectors'])]
    kills = re.findall(r'MUTANT_SEMANTIC_KILLED id=(\d+) count=(\d+)', log)
    witnesses = re.findall(r'MUTANT_SEMANTIC_WITNESS id=(\d+) case=(\d+) acc=([0-9a-f]+) mq=([0-9a-f]+) actual=([0-9a-f]+) oracle=([0-9a-f]+)', log)
    assert len(kills) == len(witnesses) == 7
    assert {int(row[0]) for row in kills} == {int(row[0]) for row in witnesses} == set(range(7))
    semantic = []
    for index, name in enumerate(prepared['mutants']):
        count = next(int(row[1]) for row in kills if int(row[0]) == index)
        row = next(row for row in witnesses if int(row[0]) == index)
        assert count > 0 and row[4] != row[5]
        semantic.append({'id': index, 'name': name, 'actual_rtl_mismatch_count': count,
                         'first_witness': {'case': int(row[1]), 'acc_hex': row[2], 'mq_hex': row[3], 'actual_hex': row[4], 'oracle_hex': row[5]},
                         'scope': '源绑定提取requant组合块，非全核心变异'})
    names = ['prepare_manifest.json', 'execution_plan.json', 'prepare_native_results.json',
             'execute_guard.py', 'collect_delivery.py', 'execute_guard.stdout.log', 'execute_guard.stderr.log',
             'execute_r01.outer.stdout.log', 'execute_r01.outer.stderr.log', 'execute_r01.outer.samples.jsonl', 'execute_r01.outer.native.json']
    for name in names:
        bindings.append(binding(HERE / name, 'source' if name.endswith('.py') else 'log' if name.endswith(('.log', '.jsonl')) else 'result'))
    for name in ['execution_plan.json', 'compile.stdout.log', 'compile.stderr.log', 'compile.native.json', 'compile.samples.jsonl',
                 'simulation.stdout.log', 'simulation.stderr.log', 'simulation.native.json', 'simulation.samples.jsonl', 'result.json']:
        bindings.append(binding(RUN / name, 'log' if name.endswith(('.log', '.jsonl')) else 'result'))
    binary = RUN / 'obj_dir/Vtb_s12_requant.exe'
    bindings.append(binding(binary, 'artifact'))
    compile_text = (RUN / 'compile.stdout.log').read_text(encoding='utf-8')
    version = re.search(r'Verilator 5\.050 2026-07-01(?: rev [^\r\n]+)?', compile_text)
    assert version
    scope_size = sum(path.stat().st_size for path in HERE.rglob('*') if path.is_file())
    assert scope_size <= 640 * 1024**2 and outer['sampled_owned_tree_rss_peak_bytes'] <= 1024**3
    delivery = {'schema': 's12_requant_whitebox_developer_delivery_v1',
                'status': 'PASS_G1_REQUANT_WHITEBOX_SUBCHECK_ONLY',
                'source_evidence_head': '891f750045ce141a8152c96025da559ff1d3a321',
                'original_full_engine_raw_sha256': prepared['sources'][0]['input_raw_sha256'],
                'candidate_full_engine_raw_sha256': prepared['sources'][1]['input_raw_sha256'],
                'full_engine_mode': '候选FROZEN_CONV_DESCRIPTOR=0；完整原模块/完整合并候选仅更名和LF转换',
                'vectors': prepared['vectors'], 'both_mq_branches_range_legal_vectors': prepared['both_branch_parameters_legal_vectors'],
                'random_seed': prepared['seed'], 'random_vectors': prepared['random_vectors'],
                'old_vs_sv_oracle_mismatches': 0, 'candidate_vs_sv_oracle_mismatches': 0,
                'sv_oracle_vs_python_expectation_mismatches': 0,
                'semantic_mutants': semantic, 'compile': result['compile'], 'simulation': result['simulation'],
                'inner_wrapper_native_exit_code': outer['native_exit_code'],
                'outer_guard_exec_native_exit_code': 0,
                'outer_guard_exec_basis': 'exec_command affed1/session21958最终b17708 exit0并打印REQUANT_GUARD_NATIVE_EXIT=0',
                'tool_versions': {'python': outer['python'], 'psutil': outer['psutil'], 'verilator': version.group(0)},
                'elapsed_seconds': outer['elapsed_seconds'],
                'sampled_guard_and_owned_tree_rss_peak_bytes': outer['sampled_owned_tree_rss_peak_bytes'],
                'absolute_tree_peak_bytes': None,
                'minimum_sampled_available_ram_bytes': outer['minimum_sampled_available_ram_bytes'],
                'minimum_sampled_c_disk_free_bytes': outer['minimum_sampled_c_disk_free_bytes'],
                'outer_samples': outer['samples'], 'scope_disk_bytes_at_collection': scope_size,
                'budget_breach': outer['budget_breach'], 'root_admission': outer['root_admission'],
                'heavy_runs': 1, 'repeat_runs': 0, 'bindings': bindings,
                'stale_prepare_limitations_in_original_result': 'result.json原样继承prepare_manifest的限制文本，其中mutants尚NOT_RUN等是准备时描述；本delivery记录真实执行结果并明确替代这些过期执行状态，不改写原件。',
                'limits_and_scope': ['仅二态白盒内部寄存器装载，非法M/q不声称公共FSM可达；X/Z未测',
                                     'BLKANDNBLK关闭只用于clk恒0的bench；不代表生产lint或公共FSM通过',
                                     '7 mutants由实际RTL输出与oracle差异击杀；不是SHA mismatch或全核心变异',
                                     '公共全trace、ARG/overflow/abort/reset与private=1数值由其他整体回归覆盖',
                                     '单job/threads1/640MiB/1GiB/600s；RAM512MiB、C盘8GiB运行停止线无触发',
                                     '离散自有树采样不证明连续绝对峰；缺测退出身份保留于原samples',
                                     '没有第二heavy、生产修改、Git、ROSS、设备探测或实板操作；本代理不提供自己的独立G2'],
                'completion': 'STOP_HEAVY_SLOT_RELEASED'}
    destination = RUN / 'developer_delivery.json'
    assert not destination.exists()
    destination.write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': delivery['status'], 'delivery_path': str(destination), 'delivery_sha256': sha(destination),
                      'vectors': delivery['vectors'], 'semantic_kills': 7, 'scope_bytes': scope_size,
                      'elapsed_seconds': delivery['elapsed_seconds']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
