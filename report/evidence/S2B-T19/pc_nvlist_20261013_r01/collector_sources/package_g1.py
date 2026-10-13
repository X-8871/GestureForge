"""绑定PC结构化读取修复的离线原件；不运行SDK或操作板卡。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

root = Path.cwd()
run = root / 'report/evidence/S2B-T19/pc_nvlist_20261013_r01'
assert run.is_dir()
assert not (run / 'delivery_manifest.json').exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
final = json.loads((run / 'final_r03/run_result.json').read_text(encoding='utf-8'))
consumers = json.loads((run / 'consumers_dependencies_r05/run_result.json').read_text(encoding='utf-8'))
assert final['exit_code'] == consumers['exit_code'] == 0
assert final['after_source_sha256'] == consumers['after_source_sha256']
for path, expected in final['after_source_sha256'].items():
    assert sha(root / path) == expected
    assert sha(run / 'final_r03' / ('after_' + Path(path).name)) == expected
assert subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip() == final['baseline']
collector = run / 'collector_sources'
collector.mkdir(exist_ok=False)
for name in ('run_regression.py', 'run_representative.py', 'package_g1.py'):
    source = root / 'tmp/2B/S2B-T19/pc_nvlist_20261013_r01' / name
    assert source.is_file()
    shutil.copyfile(source, collector / name)
prepare = root / 'tmp/2B/S2B-T19/board_prepare_20261013_r01'
for name in ('prepare_visibility_config.py', 'prepare_visibility_config_nvlist.py', 'derive_nvlist_config.py', 'config_nvlist_derivation.json'):
    source = prepare / name
    assert source.is_file()
    shutil.copyfile(source, collector / name)
checks = []
for label in ('', 'retry_permissions_r02', 'final_r03', 'consumers_r04', 'consumers_dependencies_r05'):
    data = json.loads((run / label / 'run_result.json').read_text(encoding='utf-8'))
    checks.append({'name': label or 'initial_r01', 'status': 'PASS' if data['exit_code'] == 0 else 'FAIL',
                   'command': subprocess.list2cmdline(data['command']), 'exit_code': data['exit_code']})
checks.append({'name': '实板结构化PC与缓存', 'status': 'NOT_RUN', 'command': None, 'exit_code': None,
               'reason': '本包仅离线修复验证，等待独立审查后使用全新RunId上板。'})
files = []
for p in sorted(run.rglob('*')):
    if p.is_file():
        role = 'source' if p.suffix == '.py' else 'input' if p.name == 'actual_cpu1_rrd_r02.json' else 'result'
        files.append({'path': p.relative_to(root).as_posix(), 'sha256': sha(p), 'role': role,
                      'keep_reason': '保存真实回归、失败、源码快照及实际PC故障输入；不代表G3。'})
manifest = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T19', 'run_id': run.name,
            'source_commit': final['baseline'], 'evidence_dir': run.relative_to(root).as_posix(),
            'interfaces': [], 'interfaces_not_applicable_reason': '仅修复现有visibility0调试PC读取；不改变已批准的总线、UART、模型或物理平台语义。',
            'tool_versions': {'python': final['python_version'], 'vitis_sdk_source': '2026.1，官方源码只读绑定，实际硬件API调用为0'},
            'files': files, 'checks': checks,
            'limitations': ['最终89方法及79消费者方法为离线检查，不代表真实PC读取或缓存通过。',
                            'consumers_r04缺cv2环境ERROR保留；r05沿用bundled Python，显式借用已安装Python312依赖。',
                            'collector_sources为本轮归档时脚本版本，不冒充旧Run即时快照。',
                            '独立审查另行执行；峰值内存未测，未批准visibility1。']}
(run / 'delivery_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'files': len(files), 'manifest_sha256': sha(run / 'delivery_manifest.json')}, ensure_ascii=False))
