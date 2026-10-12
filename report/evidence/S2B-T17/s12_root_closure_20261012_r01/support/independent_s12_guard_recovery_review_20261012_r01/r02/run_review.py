"""仅复审两个数组拒绝条件，复跑原12反例并保留原失败。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import psutil

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[4]
RUN=ROOT/'tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01'
DIAG=ROOT/'tmp/2B/S2B-T17/s12_guard_diag_20261012_r01'
def sha(path):
    """真实原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def bind(path):
    """绑定本次真实文件。"""
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
consumer=RUN/'runtime_consumer.mjs'
assert sha(consumer)=='a0f5b3503ad0c6c5da58d1525d508a39c6189ff2f5563addf959986e7449dbc6'
raw=consumer.read_bytes()
new=b'Array.isArray(sample?.alerts) && sample.alerts.length === 0 &&\n        Array.isArray(sample?.uncertain) && sample.uncertain.length === 0 &&'
old=b'!sample?.alerts?.length && !sample?.uncertain?.length &&'
assert raw.count(new)==1
assert hashlib.sha256(raw.replace(new,old)).hexdigest()=='687da3a29e8e8679da2bc2580360f5f93c3c6a9b115610df734c548d1b13275c'
assert sha(HERE/'consumer_cases.mjs')==sha(HERE.parent/'consumer_cases.mjs')
for path,digest in [(DIAG/'owned_binding_current.json','e78e1245be71bfceec3f4f367d011831ba1d1c32e02b143bbed2915260e9c627'),(DIAG/'recovery_receipt.json','97a707dc37a8bf983a8a2425d9d442859615baa0fb71ac8fd56b097f3c5e56a4')]:
    assert sha(path)==digest
command=['C:/Program Files/nodejs/node.exe',str(HERE/'consumer_cases.mjs'),str(consumer)]
start=time.monotonic()
with (HERE/'node.stdout.bin').open('xb') as out,(HERE/'node.stderr.bin').open('xb') as err:
    child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
    try:birth=psutil.Process(child.pid).create_time()
    except psutil.Error:birth='UNKNOWN'
    code=child.wait(timeout=30)
assert code==0
cases=json.loads((HERE/'consumer_cases.json').read_text(encoding='utf-8'))
assert cases['pass'] and len(cases['results'])==12
journal=[json.loads(line) for line in (RUN/'supervision_r02/supervision.jsonl').read_text(encoding='utf-8').splitlines()]
ready=next(row for row in journal if row['kind']=='READY')
assert not any(row['kind']=='TERMINAL' for row in journal)
guard=ready['guard_identity']; p=psutil.Process(guard['pid'])
assert guard['pid']==24184 and guard['create_time']==1791767427.2851894 and p.create_time()==guard['create_time']
sample=json.loads((RUN/'supervision_r02/guard/samples.jsonl').read_text(encoding='utf-8').splitlines()[-1])
assert type(sample['alerts']) is list and not sample['alerts'] and type(sample['uncertain']) is list and not sample['uncertain'] and sample['collection_observation']['closed'] is True
assert sha(consumer)=='a0f5b3503ad0c6c5da58d1525d508a39c6189ff2f5563addf959986e7449dbc6'
value=dict(status='PASS_RECOVERY_G2_ONLY',reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    reviewed_consumer=bind(consumer),prior_review=bind(HERE.parent/'final_review_receipt.json'),
    cases=cases,change_scope='只替换两个数组条件；回替字节与R1原SHA完全一致。',
    direct_native=dict(command=command,cwd=str(ROOT),pid=child.pid,create_time=birth,native_exit_code=code,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-start,stdout=bind(HERE/'node.stdout.bin'),stderr=bind(HERE/'node.stderr.bin')),
    unchanged_recovery_bindings=[bind(DIAG/'owned_binding_current.json'),bind(DIAG/'recovery_receipt.json')],guard_identity=guard,sample_index=sample['index'],
    limitations=['仅关闭R1 P1及恢复G2；ROOT实际launch前必须再次消费现时LIVE保护。','旧BLOCKED/GAP保留，不追认products全过程保护或OS原子整树关闭。','未执行Vivado/综合/硬件，未改被审文件或HEAD。'])
with (HERE/'final_review_receipt.json').open('x',encoding='utf-8') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps(dict(status=value['status'],receipt=bind(HERE/'final_review_receipt.json')),ensure_ascii=False))
