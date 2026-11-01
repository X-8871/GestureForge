"""归档入口未正常返回的真实超时，不制造最终入口收据或正常清理结论。"""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import subprocess

source = Path(__file__).absolute().parent
root = source.parents[3]
run = root / 'report/evidence/S2B-T19/cache_probe_20261013_r04'
folder = root / 'report/evidence/S2B-T19/cache_probe_execution_20261013_r04'
assert source.is_dir() and run.is_dir() and folder.parent.is_dir() and not folder.exists()
assert not (run / 'visibility_probe_result.json').exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
config = read(run / 'input_config.json')
jtag = read(run / 'jtag_result.json')
closed = read(source / 'server_close.json')
stopped = read(source / 'sdk_timeout_stop.json')
execution = read(source / 'vitis_execution.json')
assert jtag['status'] == 'FAILED' and jtag['error'] == "JtagError('目标数量或类型错误')"
assert closed['native_absent'] is True and closed['listeners'] == []
assert stopped['native_absent'] is True and stopped['native_exit_code'] == -1
folder.mkdir()
mapping = []
for p in sorted(source.iterdir()):
    if p.is_file():
        target = folder / p.name
        shutil.copyfile(p, target)
        assert sha(target) == sha(p)
        mapping.append({'source': str(p), 'target': str(target), 'sha256': sha(target), 'transformation': 'EXACT_BYTES'})
for name, key in (('vitis/run_s2b_visibility_probe.py', 'entry_source'), ('verification/s2b_board_jtag.py', 'tool_source')):
    data = subprocess.check_output(['git', 'show', config['source_commit'] + ':' + name], cwd=root)
    assert hashlib.sha256(data).hexdigest() == config['bindings'][key]['sha256']
    target = folder / 'source_snapshot' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    mapping.append({'source_commit': config['source_commit'], 'source': name, 'target': str(target),
                    'sha256': sha(target), 'transformation': 'GIT_EXACT_BYTES', 'limitation': '真实配置绑定的Git恢复版本，不冒充即时快照。'})
rows = [json.loads(line) for line in (run / 'entry_calls.jsonl').read_text(encoding='utf-8').splitlines()]
target_rows = [r for r in jtag['calls'] if r['api'] == 'session.targets.properties']
properties = ast.literal_eval(target_rows[-1]['return_repr'])
summary = {'status': 'FAILED_TARGET_TOPOLOGY_AND_UNLOAD_NO_PROGRESS', 'source_commit': config['source_commit'],
           'entry_final_result': 'NOT_WRITTEN', 'entry_logical_exit_code': None,
           'sdk_process_native_exit_code': stopped['native_exit_code'], 'launcher_exit_code': execution['native_exit_code'],
           'primary_error': jtag['error'], 'system_reset_observed': jtag['system_reset'],
           'target_topology': [{k:row.get(k) for k in ('name','target_id','target_ctx','parent_ctx','parent','level','jtag_cable_serial')} for row in properties.values()],
           'last_completed_entry_call': {k:rows[-1].get(k) for k in ('time_utc8','api','status')},
           'serial_close_returned': any(r['api'] == 'serial.close' and r['status'] == 'RETURNED' for r in rows),
           'controller_close_returned': any(r['api'] == 'controller.close' and r['status'] == 'RETURNED' for r in rows),
           'official_unload': 'NOT_RETURNED；内部递归TCF、MemoryMap.set或HSI.close卡点未知。',
           'sdk_normal_disconnect_dispose': 'NOT_RUN', 'owned_server_closed': closed, 'owned_sdk_terminated': stopped,
           'ps_init': 'NOT_RUN', 'pl_download': 'NOT_RUN', 'cache_probe': 'NOT_RUN', 'model': 'NOT_RUN',
           'limitations': ['真实串口已打开后关闭；未发模型或缓存操作。',
                           '两核停止与系统复位PC观察不证明统一cold生命周期。',
                           'SDK子进程异常终止并外部释放服务，不冒充正常unload/disconnect/dispose。']}
for name, data in (('summary.json', summary), ('source_mapping.json', mapping)):
    (folder / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for directory in (run, folder):
    manifest = directory / 'delivery_manifest.json'
    assert not manifest.exists()
    files = [{'path': p.relative_to(root).as_posix(), 'sha256': sha(p),
              'role': 'input' if p.name == 'input_config.json' else 'source' if p.suffix in ('.py','.ps1') else 'result',
              'keep_reason': '保存本轮目标拓扑失败、未正常返回、外部终止及自有服务闭合。'} for p in sorted(directory.rglob('*')) if p.is_file()]
    if directory == run:
        files.extend({'path': p.relative_to(root).as_posix(), 'sha256': sha(p), 'role': 'source',
                      'keep_reason': '从真实配置绑定Git精确恢复的执行源。'} for p in sorted((folder / 'source_snapshot').rglob('*.py')))
    data = {'schema_version':1, 'stage':'2B', 'task_id':'S2B-T19', 'run_id':directory.name,
            'source_commit':config['source_commit'], 'evidence_dir':directory.relative_to(root).as_posix(),
            'interfaces':[], 'interfaces_not_applicable_reason':'记录原批准visibility0探针的SDK目标拓扑及清理超时失败，不改变物理接口或验收条件。',
            'tool_versions':{'vitis':'2026.1','python_packager':'3.12.14'}, 'files':files,
            'checks':[{'name':'实际Vitis SDK子进程','status':'FAIL','command':subprocess.list2cmdline(execution['command']),
                       'exit_code':stopped['native_exit_code'],'reason':'目标数量拒绝后public unloadhw未返回，根控按精确身份终止；启动器0不是入口或实物通过。'},
                      {'name':'缓存及完整模型验收','status':'NOT_RUN','command':None,'exit_code':None,'reason':'尚未完成PS初始化/PL下载或缓存操作。'}],
            'limitations':summary['limitations']+['缺失最终入口文件是实际中断状态，不能虚构逻辑退出码。峰值内存未测。']}
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status':'PACKAGED_PARTIAL_TIMEOUT','entry_final_written':False,'sdk_native_exit_code':-1,'launcher_exit_code':execution['native_exit_code']}, ensure_ascii=False))
