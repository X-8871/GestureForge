"""独立只读恢复核查及阻断问题记录，不启动或停止实际进程。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import psutil

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[3]
RUN=ROOT/'tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01'
DIAG=ROOT/'tmp/2B/S2B-T17/s12_guard_diag_20261012_r01'
def sha(path):
    """真实原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    """只读UTF8文件。"""
    return json.loads(path.read_text(encoding='utf-8'))
def bind(path):
    """返回相对路径及原件绑定。"""
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
bindings=[]
for path,digest in [(DIAG/'owned_binding_current.json','e78e1245be71bfceec3f4f367d011831ba1d1c32e02b143bbed2915260e9c627'),(DIAG/'recovery_receipt.json','97a707dc37a8bf983a8a2425d9d442859615baa0fb71ac8fd56b097f3c5e56a4'),(RUN/'runtime_consumer.mjs','687da3a29e8e8679da2bc2580360f5f93c3c6a9b115610df734c548d1b13275c'),(ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/guard.py','a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac'),(ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02/supervisor.py','193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0')]:
    assert path.is_file() and sha(path)==digest
    bindings.append(bind(path))
recovery=load(DIAG/'recovery_receipt.json'); current=load(DIAG/'owned_binding_current.json'); old=load(RUN/'owned_binding.json')
assert recovery['monitoring_gap']=='NOT_RECOVERED' and len(recovery['samples'])==5
assert recovery['cwd_literal_differences']==[dict(index=0,old='C',current='c')]
for key in ('root_directory_identity','prep_directory_identity'):
    item=recovery[key]
    assert os.path.samefile(item['old']['path'],item['current']['path'])
    for name in ('old','current'):
        path=Path(item[name]['path']); stat=path.stat()
        assert path.is_dir() and not path.is_symlink() and not path.is_junction()
        assert stat.st_dev==item[name]['st_dev'] and stat.st_ino==item[name]['st_ino']
assert all(current[k]==old[k] for k in ('pid','create_time','exe','cmdline','ppid','source_commit','run_id'))
assert current['cwd'][0]=='c' and current['cwd'][1:]==old['cwd'][1:]
assert all(all(s['root_match'].values()) and s['keys']==[[5832,1791766374.8010526]] for s in recovery['samples'])
assert sha(Path(recovery['old_members_supplement']['path']))==recovery['old_members_supplement']['sha256']
supplement=load(DIAG/'supplement_readback.json')
assert all(x['state']=='ABSENT' for x in supplement['old_members'])
assert not supplement['same_supervisor_command_alive'] and not supplement['python_inventory_unknown']
native=load(DIAG/'recovery.native.json')
assert native['native_exit_code']==native['direct_wait_exit_code']==0
assert sha(DIAG/'recovery.stdout.bin')==native['stdout_sha256'] and sha(DIAG/'recovery.stderr.bin')==native['stderr_sha256']
old_guard=load(RUN/'supervision/guard/guard_receipt.json')
assert old_guard['status'].startswith('BLOCKED')
journal=[json.loads(line) for line in (RUN/'supervision_r02/supervision.jsonl').read_text(encoding='utf-8').splitlines()]
ready=[r for r in journal if r.get('kind')=='READY']
assert len(ready)==1 and ready[0]['guard_identity']['pid']==24184 and ready[0]['guard_identity']['create_time']==1791767427.2851894
assert ready[0]['first_sample_sha256']=='92b19e8b904935d1e1d51a001979efe68717fa8b1f8bbba807873bcb9738ae61'
assert not any(r.get('kind')=='TERMINAL' for r in journal)
for expected in (current,ready[0]['guard_identity']):
    p=psutil.Process(expected['pid'])
    actual=dict(pid=p.pid,create_time=p.create_time(),exe=p.exe(),cwd=p.cwd(),cmdline=p.cmdline())
    assert all(actual[k]==expected[k] for k in actual)
    assert p.is_running() and psutil.Process(p.pid).create_time()==actual['create_time']
cases=load(HERE/'consumer_cases.json'); assert not cases['pass']
bad=[r for r in cases['results'] if r['actual']!=r['expected']]
assert len(bad)==4
command=['C:/Program Files/Git/bin/git.exe','-c','core.longpaths=true','-c','maintenance.auto=false','rev-parse','HEAD']
with (HERE/'head.stdout.bin').open('xb') as out,(HERE/'head.stderr.bin').open('xb') as err:
    p=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
    try:birth=psutil.Process(p.pid).create_time()
    except psutil.Error:birth='UNKNOWN'
    code=p.wait(timeout=30)
assert code==0 and (HERE/'head.stdout.bin').read_text(encoding='ascii').strip()=='467463757158aed80d6f75afadff6a8458614a29'
value=dict(status='CHANGES_REQUIRED',source_commit='467463757158aed80d6f75afadff6a8458614a29',frozen_inputs=bindings,
    reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),recovery_semantics='PASS_BINDING_RECOVERY_ONLY',
    cases=cases,old_gap='NOT_RECOVERED',current_ready='VERIFIED_READONLY_SNAPSHOT',
    finding=dict(priority=1,file=bind(RUN/'runtime_consumer.mjs'),line=32,
        problem='缺少alerts/uncertain或类型错误时 !field?.length 为true，使未知监测状态错误CONSUMED_LIVE_READY。',
        closure='要求两个字段明确为数组且长度为0，并以四个独立反例证明拒绝。'),
    native_node_exit_code=0,node_assertion_semantics='四个反例结果证明实现拒绝条件失败；Node执行本身原生0。',
    head_native=dict(command=command,pid=p.pid,create_time=birth,direct_wait_exit_code=code),
    limits=['保护恢复绑定及现时READY成立；仍须ROOT在实际launch前重新消费。','旧失败、GAP及未知旧SUP身份保留，不验收整products资源监控或G3。','只创建本隔离目录，不改生产/被审文件/HEAD，不调用Vivado或硬件。'])
with (HERE/'final_review_receipt.json').open('x',encoding='utf-8') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps(dict(status=value['status'],receipt=bind(HERE/'final_review_receipt.json')),ensure_ascii=False))
