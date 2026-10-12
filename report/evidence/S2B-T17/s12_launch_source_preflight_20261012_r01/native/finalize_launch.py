"""保留首清单包装失败，只新增正确的最终交付清单。"""
import json
from pathlib import Path
import subprocess
import sys
import launch_prepare as launch

HERE, ROOT, PRE = launch.HERE, launch.ROOT, launch.PRE

def main():
    """直接核验最终门禁原生退出后封存本轮小型证据。"""
    command = [sys.executable, '-X', 'utf8', '-B', '-c',
        'import sys; sys.path.insert(0, '+repr(str(HERE))+'); import launch_prepare as m; old=m.write; m.write=lambda p,v: old(p.with_name("launch_pins_test_receipt_r02.json") if p.name=="launch_pins_test_receipt.json" else p,v); m.pin_tests()']
    launch.run('pins_final', command)
    rawdir = PRE/'native'; rawdir.mkdir()
    for path in sorted(HERE.iterdir()):
        if path.is_file() and (path.name.endswith(('.native.json', '.stdout.bin', '.stderr.bin')) or path.name in ('git_batch_request.txt', 'finalize_launch.py', 'launch_pins_test_receipt_r02.json')):
            launch.put(rawdir/path.name, path.read_bytes())
    launch.write(PRE/'packaging_correction.json', {'status': 'CORRECTED_MANIFEST_ONLY',
        'initial_failure': launch.bind(HERE/'precheck_evidence.native.json'),
        'reason': '首清单误标tmp为当前evidence artifact、command用了数组且缺result/log角色；最终清单按实际位置及字符串命令修正。',
        'unchanged': ['43生产RAW', 'source_freeze.json', '六运行工具', '真正source-before', 'prepared_receipt.json'],
        'new_native_pins_check': launch.bind(HERE/'pins_final.native.json'),
        'heavy_hardware': 'NOT_RUN'})
    files = []
    for path in sorted(PRE.rglob('*')):
        if path.is_file() and path.name != 'delivery_manifest.json':
            role = 'source' if 'source_snapshot' in path.parts else 'log' if path.name.endswith(('.stdout.bin', '.stderr.bin')) else 'result' if path.name in ('author_receipt.json', 'prepared_receipt.json', 'launch_pins_test_receipt_r02.json', 'packaging_correction.json') else 'artifact'
            files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=launch.sha(path.read_bytes()), role=role,
                keep_reason='本次真实启动绑定、源码快照及小型原生记录；首包装失败保留，未执行综合或实物。'))
    freeze = json.loads((HERE/'source_freeze.json').read_text(encoding='utf-8'))
    inputs = [launch.OLDPRE/'delivery_manifest_r05.json', launch.OLDPRE/'source_freeze.json', ROOT/freeze['functional_g1']['path'], ROOT/freeze['functional_g2']['path']]
    for path in inputs:
        files.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=launch.sha(launch.exact(path).read_bytes()), role='input', keep_reason='必要外部冻结输入按SHA引用，未复制历史包。'))
    checks = []
    for name in ('git_batch', 'source_before', 'prepare', 'pins_final'):
        native = json.loads((HERE/(name+'.native.json')).read_text(encoding='utf-8'))
        assert native['direct_wait_exit_code'] == native['native_exit_code'] == 0
        checks.append({'name': name, 'status': 'PASS', 'command': subprocess.list2cmdline(native['command']), 'exit_code': native['native_exit_code'], 'reason': '真实原生退出0；具体源码、门禁和进程绑定见本轮native原件。'})
    checks.append({'name': '真实Vivado综合、PNR与板上验证', 'status': 'NOT_RUN', 'command': None, 'exit_code': None,
        'reason': '仅离线启动输入已准备，综合由ROOT独审后派发；PNR仍缺真实综合G1/G2。'})
    launch.write(PRE/'delivery_manifest.json', {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': PRE.name,
        'source_commit': launch.HEAD, 'evidence_dir': PRE.relative_to(ROOT).as_posix(), 'interfaces': [],
        'interfaces_not_applicable_reason': '本次仅重绑当前源码HEAD及运行目录，沿用已核实平台业务候选和功能G1/G2，没有新增物理接口冻结。',
        'files': files, 'checks': checks, 'tool_versions': {'python': sys.version, 'psutil': launch.psutil.__version__, 'git': (HERE/'git_version.stdout.bin').read_text(encoding='utf-8').strip()},
        'limitations': ['独立G2、综合、PNR、硬件及G3至G5均未执行；不能当作全流程PASS。',
                        '首包装失败保留于precheck清单和原生输出，最终清单只修正包装格式。',
                        '直接子进程PID/create_time/wait有实际记录；collector内部Git PID/create_time及峰值内存明确UNKNOWN。',
                        '旧完整门禁证据按原manifest SHA复用；freeze旧快照和Git RAW没有重复复制。']})
    manifest = str(PRE/'delivery_manifest.json')
    py = [sys.executable, '-X', 'utf8', '-B', str(ROOT/'verification/check_stage_delivery.py')]
    launch.run('final_evidence', py+['--mode', 'evidence', '--manifest', manifest])
    launch.run('final_inputs', py+['--mode', 'inputs', '--manifest', manifest], expected=2)
    print(json.dumps({'status': 'STOP_LAUNCH_PINS_G1_ONLY', 'runtime': str(HERE), 'source_pre': str(PRE),
        'freeze': launch.bind(HERE/'source_freeze.json'), 'helper': launch.bind(HERE/'compat_pins.py'),
        'tool_binding': launch.bind(HERE/'tool_binding.json'), 'manifest': launch.bind(PRE/'delivery_manifest.json'),
        'source_count': 43, 'git_raw': 37, 'git_eol': 6, 'runtime_prepared': True, 'evidence_exit': 0, 'inputs_exit': 2,
        'synth_pnr_hardware': 'NOT_RUN'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
