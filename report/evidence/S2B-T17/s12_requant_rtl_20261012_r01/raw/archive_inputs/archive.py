import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psutil

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent
PREP = ROOT / 'tmp/2B/S2B-T17/s12_requant_rtl_prepare_20261012_r01'
EVIDENCE = ROOT / 'report/evidence/S2B-T17/s12_requant_rtl_20261012_r01'
START = time.perf_counter()
SELF = psutil.Process()
PEAK = 0
MAPPING = []


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(data)
    return result.hexdigest()


def save(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def budget():
    global PEAK
    owned = [SELF] + SELF.children(recursive=True)
    current = 0
    for process in owned:
        try:
            current += process.memory_info().rss
        except psutil.NoSuchProcess:
            pass
    PEAK = max(PEAK, current)
    assert PEAK <= 256 * 1024**2
    assert time.perf_counter() - START < 180
    assert sum(path.stat().st_size for path in EVIDENCE.rglob('*') if path.is_file()) < 100 * 1024**2


def copy(source, destination, expected=None):
    assert source.is_file() and not source.is_symlink(), str(source)
    before = sha(source)
    if expected:
        assert before == expected, str(source)
    target = EVIDENCE / destination
    assert not target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    assert before == sha(target) == sha(source)
    MAPPING.append({'original_path': str(source), 'archive_path': target.relative_to(ROOT).as_posix(),
                    'sha256': before, 'bytes': target.stat().st_size, 'copy_mode': 'RAW_BYTE_COPY'})
    budget()
    return target


def files():
    rows = []
    for path in sorted(EVIDENCE.rglob('*')):
        if not path.is_file() or path.name == 'delivery_manifest_r02.json':
            continue
        role = 'source' if path.suffix in ('.py', '.sv') else 'log' if path.suffix in ('.log', '.jsonl') else 'input' if path.name == 'vectors.txt' else 'result'
        rows.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'role': role})
    return rows


def check(manifest, label):
    command = [sys.executable, '-B', '-X', 'utf8', str(ROOT / 'verification/check_stage_delivery.py'),
               '--mode', 'evidence', '--manifest', str(manifest)]
    stdout = HERE / (label + '.stdout.log')
    stderr = HERE / (label + '.stderr.log')
    began = time.perf_counter()
    with stdout.open('xb') as out, stderr.open('xb') as err:
        process = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
        while process.poll() is None:
            try:
                budget()
            except BaseException:
                process.kill()
                process.wait()
                raise
            time.sleep(0.02)
    receipt = {'command': command, 'cwd': str(ROOT), 'native_exit_code': process.returncode,
               'elapsed_seconds': time.perf_counter() - began,
               'stdout': {'path': str(stdout), 'sha256': sha(stdout)},
               'stderr': {'path': str(stderr), 'sha256': sha(stderr)},
               'manifest_sha256': sha(manifest)}
    save(HERE / (label + '.native.json'), receipt)
    return receipt


def main():
    assert sys.version_info[:3] == (3, 12, 10) and psutil.__version__ == '7.2.2'
    assert ROOT == Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
    assert EVIDENCE.parent.is_dir() and not EVIDENCE.exists()
    assert PREP.is_dir() and HERE.parent.is_dir()
    EVIDENCE.mkdir()
    pins = {'prepare_manifest.json': '300667b4874605630f3dc5bcf301ac63a0f011591d897638366c6dd1ae69527a',
            'execution_plan.json': '5c54ec6a5ee8d80edda3000dbdaaebc22d360643b247666a238c11e1b0116226',
            'runs/execute_r01/developer_delivery.json': '8fdd983af602674da44734d34adec66c600ac3fc0ba65f5987c6b51c1ceef173',
            'runs/execute_r01/result.json': 'f6b0a246819b1c31de3181f2fd9f2218e1106c1836263575986b68ce923ee391'}
    for name, expected in pins.items():
        assert sha(PREP / name) == expected
    prepared = json.loads((PREP / 'prepare_manifest.json').read_text(encoding='utf-8'))
    delivery = json.loads((PREP / 'runs/execute_r01/developer_delivery.json').read_text(encoding='utf-8'))
    assert delivery['status'] == 'PASS_G1_REQUANT_WHITEBOX_SUBCHECK_ONLY'
    # 验证原交付绑定，包括仅保留哈希、不会复制的可重建可执行文件。
    for row in delivery['bindings']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    for row in prepared['prepared_files']:
        assert sha(PREP / row['path']) == row['sha256']
    for path in sorted(PREP.iterdir()):
        if path.is_file():
            copy(path, 'raw/prepare/' + path.name, pins.get(path.name))
    run = PREP / 'runs/execute_r01'
    for path in sorted(run.iterdir()):
        if path.is_file():
            copy(path, 'raw/execute_r01/' + path.name, pins.get('runs/execute_r01/' + path.name))
    transforms = []
    for index, row in enumerate(prepared['sources']):
        source = Path(row['input'])
        copy(source, 'raw/full_source/' + ('original' if index == 0 else 'candidate') + '.sv', row['input_raw_sha256'])
        module = 'rq_original_engine' if index == 0 else 'rq_candidate_engine'
        normalized = source.read_bytes().decode('utf-8').replace('\r\n', '\n')
        assert normalized.count('module s2b_conv_tile_engine') == 1
        assert normalized.replace('module s2b_conv_tile_engine', 'module ' + module, 1) == (PREP / row['prepared_file']).read_bytes().decode('utf-8')
        transforms.append({'input_sha256': row['input_raw_sha256'], 'prepared_sha256': row['prepared_sha256'],
                           'operation': 'UTF8解码、CRLF转LF、唯一模块名替换；完整文本逐字符等同', 'verified': True})
    descriptor = ROOT / 'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_snapshot/src/s2a_network_descriptor_pkg.sv'
    copy(descriptor, 'raw/full_source/s2a_network_descriptor_pkg.sv', prepared['descriptor_raw_sha256'])
    production = ROOT / 'src/s2b_conv_tile_engine.sv'
    assert sha(production) == prepared['sources'][1]['input_raw_sha256']
    admission = ROOT / 'tmp/2B/S2B-T17/s12_root_run_20261012_r01'
    copy(admission / 'offline_admission_before_requant_r01.json', 'raw/admission/offline_admission_before_requant_r01.json', '2403aa3bf916ccda7e29e8346f0db1e62c05fcd1a658f8fffd605e3838b26a0f')
    copy(admission / 'offline_admission_before_requant_r01.tool.json', 'raw/admission/offline_admission_before_requant_r01.tool.json', '5f07f4a3a174b564557b7ca25291d76319dcb3aaa4c98c342d6b536b8815e5e4')
    supplement_path = ROOT / 'tmp/2B/S2B-T17/s12_requant_draft_20261012_r01/failure_supplement.json'
    supplement = json.loads(supplement_path.read_text(encoding='utf-8'))
    copy(supplement_path, 'raw/early_limits/failure_supplement.json')
    for row in supplement['new_transcriptions'] + supplement['existing_artifacts_rechecked_unchanged']:
        source = ROOT / row['path']
        copy(source, 'raw/early_limits/' + source.parent.name + '/' + source.name, row['sha256'])
    for source in [ROOT / 'verification/check_stage_delivery.py', ROOT / 'report/README.md', Path(__file__)]:
        copy(source, 'raw/archive_inputs/' + source.name)
    interfaces = []
    for name, version, frozen, relative in [
        ('tiny416冻结模型数值及逻辑接口', 'S2A-T01/G0', True, 'docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md'),
        ('阶段2B物理接口候选', 's2b-physical-candidate/0.1.1', False, 'docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md')]:
        source = ROOT / relative
        assert source.is_file()
        interfaces.append({'name': name, 'version': version, 'frozen': frozen, 'path': relative, 'sha256': sha(source)})
        copy(source, 'raw/interface_context/' + source.name)
    # 历史候选profile仅作版本上下文；不注册或冻结新平台。
    for name in ['s2b_inference_platform.json', 's2b_inference_platform.md']:
        source = ROOT / 'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_snapshot/board' / name
        copy(source, 'raw/platform_context/' + name)
    limits = ['仅G1两态白盒requant子检查PASS；本Developer不提供自己代码的G2结论。',
              'X/Z、G2、STA、G3、公开FSM完整trace、ARG/overflow/abort/reset、private=1均未在本Run执行。',
              '7个mutants为精确源绑定提取组合块；真实RTL输出与oracle差异击杀，不是全核心变异。',
              'clk恒0并内部装载；BLKANDNBLK仅fixture豁免；非法参数向量不声明公开FSM可达。',
              '原prepare/result中的NOT_RUN准备期文案原字节保留；developer_delivery原件明确澄清真实执行结果。',
              '早期Python启动失败native未知、组合工具码0；草稿CRLF失败native1；只有tool_return_transcription，缺原始stderr及失败脚本字节，不称闭合。',
              '不复制obj_dir、exe、编译缓存；原binary仅哈希绑定，可从完整源码重建。',
              '模型既有冻结只作上游背景，不表示本候选平台或物理0.1.1被冻结；历史候选profile0.1.11不注册。',
              'source_commit为证据HEAD891；原功能来源a710；准备原件自己记载HEAD891；候选未提交源码以RAW SHA绑定。',
              '采样峰不是连续绝对峰；编译警告与原失败事实保留；不执行重型或设备探测。']
    summary = {'schema': 's12_requant_archive_summary_v1', 'status': delivery['status'],
               'evidence_head': '891f750045ce141a8152c96025da559ff1d3a321',
               'original_functional_commit': 'a710ec431474841a81912a6055f861e811a151e3',
               'prepare_reported_head': prepared['source_evidence_head'],
               'candidate_production_raw_sha256': sha(production), 'source_transformations': transforms,
               'vectors': delivery['vectors'], 'seed': delivery['random_seed'], 'random_vectors': delivery['random_vectors'],
               'semantic_mutants': delivery['semantic_mutants'], 'tool_versions': delivery['tool_versions'],
               'original_result_clarification': delivery['stale_prepare_limitations_in_original_result'],
               'oracle_location': 'raw/prepare/prepare.py内divmod；raw/prepare/tb_s12_requant.sv内256bit除法及余数；原vectors.txt完整保留',
               'fixture_query_location': 'tb_s12_requant.sv内部寄存器装载/输出读取；没有独立query文件',
               'not_run': ['G2', 'STA', 'G3', 'public_FSM', 'private1', 'X/Z'],
               'binary_not_copied': [row for row in delivery['bindings'] if '/obj_dir/' in row['path']],
               'limitations': limits}
    save(EVIDENCE / 'archive_summary.json', summary)
    save(EVIDENCE / 'restore_mapping.json', {'schema': 'raw_restore_mapping_v1', 'rows': MAPPING, 'original_files_rechecked_unchanged': True})
    checks = []
    native = json.loads((PREP / 'prepare_native_results.json').read_text(encoding='utf-8'))
    for label in ['prepare', 'plan']:
        checks.append({'name': 'REQUANT_' + label, 'status': 'PASS', 'command': native[label]['command'], 'exit_code': native[label]['native_exit_code']})
    for label in ['compile', 'simulation']:
        checks.append({'name': 'REQUANT_' + label, 'status': 'PASS', 'command': subprocess.list2cmdline(delivery[label]['command']), 'exit_code': delivery[label]['native_exit_code']})
    for label in ['G2', 'STA', 'G3', 'public_FSM', 'private1', 'X/Z']:
        checks.append({'name': label, 'status': 'NOT_RUN', 'command': None, 'exit_code': None, 'reason': '本REQUANT白盒Run未执行；不得继承为独审、时序、公开状态机或实物结论。'})
    manifest = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T17', 'run_id': EVIDENCE.name,
                'source_commit': summary['evidence_head'], 'evidence_dir': EVIDENCE.relative_to(ROOT).as_posix(),
                'interfaces': interfaces, 'tool_versions': {**delivery['tool_versions'], 'archive_python': sys.version.split()[0], 'archive_psutil': psutil.__version__},
                'files': files(), 'checks': checks, 'limitations': limits}
    save(EVIDENCE / 'delivery_manifest.json', manifest)
    initial = check(EVIDENCE / 'delivery_manifest.json', 'evidence_initial')
    for suffix in ['stdout.log', 'stderr.log', 'native.json']:
        copy(HERE / ('evidence_initial.' + suffix), 'raw/pack_check/evidence_initial.' + suffix)
    save(EVIDENCE / 'restore_mapping_pack_checks.json', {'schema': 'raw_restore_mapping_v1',
                                                       'rows': MAPPING[-3:], 'original_files_rechecked_unchanged': True})
    # 新版清单绑定初版和包装检查原件；最终检查原件留在隔离包装目录防止自引用。
    receipt = {'status': 'RAW_ARCHIVE_CREATED', 'initial_evidence_native_exit_code': initial['native_exit_code'],
               'copied_raw_files': len(MAPPING), 'elapsed_seconds_so_far': time.perf_counter() - START,
               'sampled_owned_tree_rss_peak_bytes': PEAK, 'absolute_tree_peak_bytes': None,
               'command': [sys.executable, '-B', '-X', 'utf8', str(Path(__file__))],
               'cwd': str(ROOT), 'limits': {'evidence_bytes': 100 * 1024**2, 'tree_bytes': 256 * 1024**2, 'seconds': 180},
               'final_evidence_check_receipt': str(HERE / 'evidence_final.native.json'), 'completion': '最终检查完成后STOP'}
    save(EVIDENCE / 'archive_native_receipt.json', receipt)
    manifest['files'] = files()
    manifest['checks'].append({'name': '初版归档evidence包装', 'status': 'PASS' if initial['native_exit_code'] == 0 else 'FAIL',
                               'command': subprocess.list2cmdline(initial['command']), 'exit_code': initial['native_exit_code'],
                               'reason': '只验证清单与文件绑定，不代表G2或部署。'})
    save(EVIDENCE / 'delivery_manifest_r02.json', manifest)
    final = check(EVIDENCE / 'delivery_manifest_r02.json', 'evidence_final')
    budget()
    for row in MAPPING:
        assert sha(Path(row['original_path'])) == sha(ROOT / row['archive_path']) == row['sha256']
    result = {'status': 'ARCHIVE_COMPLETE_STOP' if initial['native_exit_code'] == final['native_exit_code'] == 0 else 'ARCHIVE_CHECK_FAILED_STOP',
              'native_exit_code': final['native_exit_code'], 'initial_evidence_native_exit_code': initial['native_exit_code'],
              'final_evidence_native_exit_code': final['native_exit_code'], 'manifest_path': str(EVIDENCE / 'delivery_manifest_r02.json'),
              'manifest_sha256': sha(EVIDENCE / 'delivery_manifest_r02.json'), 'copied_raw_files': len(MAPPING),
              'archive_files': sum(path.is_file() for path in EVIDENCE.rglob('*')),
              'evidence_bytes': sum(path.stat().st_size for path in EVIDENCE.rglob('*') if path.is_file()),
              'elapsed_seconds': time.perf_counter() - START, 'sampled_owned_tree_rss_peak_bytes': PEAK,
              'absolute_tree_peak_bytes': None, 'source_unchanged': True, 'final_check': final}
    save(HERE / 'final_archive_receipt.json', result)
    print(json.dumps(result, ensure_ascii=False))
    return result['native_exit_code']


if __name__ == '__main__':
    sys.exit(main())
