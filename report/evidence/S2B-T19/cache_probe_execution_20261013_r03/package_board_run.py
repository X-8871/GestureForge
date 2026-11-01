"""保存已结束实板Run及自有服务闭合，不把启动器零码当作实物验收。"""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys

root = Path.cwd()
suffix = sys.argv[1]
assert re.fullmatch(r'r[0-9]{2}', suffix)
temporary = root / ('tmp/2B/S2B-T19/board_run_20261013_' + suffix)
run = root / ('report/evidence/S2B-T19/cache_probe_20261013_' + suffix)
archive = root / ('report/evidence/S2B-T19/cache_probe_execution_20261013_' + suffix)
assert temporary.is_dir() and run.is_dir() and archive.parent.is_dir() and not archive.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
config = read(run / 'input_config.json')
result = read(run / 'visibility_probe_result.json')
closed = read(temporary / 'server_close.json')
execution = read(temporary / 'vitis_execution.json')
assert result['native_exit_code'] in (0, 2) and closed['status'] == 'OWNED_SERVER_CLOSED'
assert closed['native_absent'] is True and closed['listeners'] == []
archive.mkdir()
mapping = []
for path in sorted(temporary.iterdir()):
    if path.is_file():
        target = archive / path.name
        shutil.copyfile(path, target)
        assert sha(target) == sha(path)
        mapping.append({'source': str(path), 'target': str(target), 'sha256': sha(target), 'transformation': 'EXACT_BYTES'})
shutil.copyfile(Path(__file__), archive / 'package_board_run.py')
for name, key in (('vitis/run_s2b_visibility_probe.py', 'entry_source'), ('verification/s2b_board_jtag.py', 'tool_source')):
    data = subprocess.check_output(['git', 'show', config['source_commit'] + ':' + name])
    assert hashlib.sha256(data).hexdigest() == config['bindings'][key]['sha256']
    target = archive / 'source_snapshot' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    mapping.append({'source_commit': config['source_commit'], 'source': name, 'target': str(target),
                    'sha256': sha(target), 'transformation': 'GIT_EXACT_BYTES', 'limitation': '按真实配置从Git恢复，不冒充即时快照。'})
targets = [row for row in result['calls'] if row['api'] == 'session.initial_targets']
properties = ast.literal_eval(targets[0]['return_repr']) if targets else {}
summary = {'status': result['status'], 'source_commit': config['source_commit'],
           'entry_exit_code': result['native_exit_code'], 'launcher_exit_code': execution['native_exit_code'],
           'elapsed_seconds': result['elapsed_seconds'], 'error': result.get('error'),
           'target_names': [row.get('name') for row in properties.values()],
           'cleanup_errors': result['cleanup_errors'], 'server_closed': closed,
           'serial_closed': result.get('serial_closed'), 'cache_observation': result.get('cache_probe'),
           'cold_lifecycle_proven': result['cold_lifecycle_proven'],
           'model_acceptance': 'NOT_RUN', 'meaning': '仅保存实际API观察与外部服务闭合；不是独立实物审批或2B验收。'}
for name, value in (('summary.json', summary), ('source_mapping.json', mapping)):
    (archive / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for directory in (run, archive):
    manifest = directory / 'delivery_manifest.json'
    assert not manifest.exists()
    files = [{'path': p.relative_to(root).as_posix(), 'sha256': sha(p),
              'role': 'input' if p.name == 'input_config.json' else 'source' if p.suffix in ('.py', '.ps1') else 'result',
              'keep_reason': '保留真实板上操作、失败或观察、服务释放及执行版本。'}
             for p in sorted(directory.rglob('*')) if p.is_file()]
    if directory == run:
        files.extend({'path': p.relative_to(root).as_posix(), 'sha256': sha(p), 'role': 'source',
                      'keep_reason': '按实际配置绑定恢复的执行版本。'} for p in sorted((archive / 'source_snapshot').rglob('*.py')))
    checks = [{'name': '实际缓存探针入口', 'status': 'PASS' if result['native_exit_code'] == 0 else 'FAIL',
               'command': subprocess.list2cmdline(execution['command']), 'exit_code': result['native_exit_code'],
               'reason': '原生入口结果与启动器码分别保存：' + result['status'] + '; ' + str(result.get('error', '观察待独立验收'))},
              {'name': '完整模型与2B实物验收', 'status': 'NOT_RUN', 'command': None, 'exit_code': None,
               'reason': 'visibility0探针范围不批准模型或visibility1平台，独立实物审查仍需完成。'}]
    data = {'schema_version': 1, 'stage': '2B', 'task_id': 'S2B-T19', 'run_id': directory.name,
            'source_commit': config['source_commit'], 'evidence_dir': directory.relative_to(root).as_posix(),
            'interfaces': [], 'interfaces_not_applicable_reason': '记录已批准visibility0入口的实际观察，沿用原运行兼容收据；不改变业务或物理接口。',
            'tool_versions': {'vitis': '2026.1', 'python_packager': sys.version}, 'files': files, 'checks': checks,
            'limitations': ['完整模型/109样本/1000压力/恢复验收未执行，不代表G3–G5。',
                            '入口owned_hw_server_released=false为进程内事实，服务随后由根控外部闭合，两原件均保留。',
                            'Git恢复源码不是即时快照；收集器为归档当前版本。峰值内存未测。']}
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': 'PACKAGED', 'run': suffix, 'entry_exit_code': result['native_exit_code'],
                  'target_names': summary['target_names'], 'server_closed_pid': closed['native_pid']}, ensure_ascii=False))
