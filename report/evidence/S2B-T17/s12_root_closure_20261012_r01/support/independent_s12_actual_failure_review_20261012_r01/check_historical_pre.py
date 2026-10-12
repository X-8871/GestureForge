"""独立核查历史PRE清单现时包装失败，不改旧清单或补写历史成功。"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[3]
PRE=ROOT/'report/evidence/S2B-T17/s12_launch_source_preflight_20261012_r01'
def bind(path):
    """原字节绑定。"""
    raw=path.read_bytes();return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
manifest=PRE/'delivery_manifest.json'
assert bind(manifest)['sha256']=='516a37bb63dd2b9d0adaf4ae5489215eb9fa232a79313eef308363f44acdd189'
command=[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(manifest)]
start=time.monotonic()
with (HERE/'historical_pre_evidence.stdout.bin').open('xb') as out,(HERE/'historical_pre_evidence.stderr.bin').open('xb') as err:
    child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
    try:birth=psutil.Process(child.pid).create_time()
    except psutil.Error:birth='UNKNOWN'
    code=child.wait(timeout=30)
assert code==2
result=json.loads((HERE/'historical_pre_evidence.stdout.bin').read_text(encoding='utf-8'))
assert result['status']=='CHECKS_FAILED' and result['mode']=='evidence'
errors=result['errors']
assert any('source_after.json' in error for error in errors)
assert any('source_snapshot_after' in error for error in errors)
value=dict(status='PASS_EVIDENCE_INTEGRITY_ONLY',scope='补充历史PRE清单现时失败的真实原因；不引用未来ROOT总清单。',main_review=bind(HERE/'final_review_receipt.json'),historical_pre_manifest=bind(manifest),
    native=dict(command=command,pid=child.pid,create_time=birth,native_exit_code=code,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-start,stdout=bind(HERE/'historical_pre_evidence.stdout.bin'),stderr=bind(HERE/'historical_pre_evidence.stderr.bin')),
    error_count=len(errors),errors=errors,reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    reason='旧PRE清单原字节未改；新增真实source_after及source_snapshot_after未被旧清单收录，因此现时evidence2。旧冻结时evidence0不能继承到扩大后的目录。43源前后immutable快照/Git对象一致已由主receipt独立核查。',
    limitations=['实际S12 STA FAIL及三段保护GAP仍未通过；本PASS仅失败证据准确性。','主业务s12_delivery_manifest现时evidence0/inputs2与历史PRE现时evidence2分别保留。','未执行新综合、PNR、硬件或生产RAW读取。'])
path=HERE/'historical_pre_supplement_receipt.json'
with path.open('x',encoding='utf-8') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps(dict(status=value['status'],receipt=bind(path),native_code=code,error_count=len(errors)),ensure_ascii=False))
