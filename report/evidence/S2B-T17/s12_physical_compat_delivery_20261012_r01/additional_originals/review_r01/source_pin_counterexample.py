"""独立来源commit门禁反例，全部Git返回合成且不启动Git。"""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import psutil

OUT=Path(__file__).parent
ROOT=Path(__file__).parents[4]
WORK=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
sys.path.insert(0,str(WORK))
import compat_pins as p
spec=importlib.util.spec_from_file_location('source_pin_test',WORK/'collector.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
base=OUT/'source_pin_counterexample';base.mkdir()
names=['synthetic_source_'+str(i)+'.txt' for i in range(43)]
raw={name:('合成来源文件'+str(i)+'\n').encode('utf-8') for i,name in enumerate(names)}
for name,data in raw.items():
    with (base/name).open('xb') as stream:stream.write(data)
hashes={name:hashlib.sha256(data).hexdigest() for name,data in raw.items()}
freeze=dict(source_commit='a'*40,frozen14={name:hashes[name] for name in names[:14]})
static={name:hashes[name] for name in names[:33]}
profile=dict(version='s2b-inference-platform/0.1.12')
c.ROOT=base;c.PRE=base/'pre';c.PROJECT=base/'project';c.REPORT=base/'report';c.FREEZE=base/'freeze.json'
c.FREEZE_SHA='f'*64
c.load_freeze=lambda:(freeze,hashes,static,profile)
old_ready=p.require_ready;old_commit=p.SOURCE_COMMIT
p.SOURCE_COMMIT='a'*40
p.require_ready=lambda pnr=False:None
calls=[]
def git_mock(*args):
    """模拟另一实际HEAD B，与已pin源码commit A不同，但字节完全相同。"""
    calls.append(args)
    if args==('rev-parse','HEAD'):return (('b'*40+'\n').encode('ascii'),list(args))
    if args==('diff','--cached','--name-only'):return b'',list(args)
    assert args[0]=='show' and args[1].startswith('b'*40+':')
    return raw[args[1].split(':',1)[1]],list(args)
c.git=git_mock
original_save=c.save
def synthetic_save(path,value):
    """明确标为模拟，不让PASS记录成为真实source证据。"""
    value=dict(value,fixture_test=True,actual_git_calls=0)
    if 'status' in value:value['synthetic_expected_status']=value.pop('status');value['status']='SYNTHETIC_TEST_ONLY'
    original_save(path,value)
c.save=synthetic_save
started=time.monotonic()
try:
    with contextlib.redirect_stdout(io.StringIO()):c.source('b'*40,'before')
    outcome='ACCEPTED_BAD_SYNTHETIC_COMMIT'
    record=json.loads((c.PRE/'source_before.json').read_text(encoding='utf-8'))
    assert record['source_commit']=='b'*40 and record['source_count']==43
    assert all(hashlib.sha256((base/r['snapshot']).read_bytes()).hexdigest()==r['sha256'] for r in record['source_files'])
except ValueError as error:
    outcome='REJECTED';record=dict(exception=str(error))
finally:
    p.require_ready=old_ready;p.SOURCE_COMMIT=old_commit
result=dict(outcome=outcome,pinned_source_commit='a'*40,supplied_and_mock_actual_commit='b'*40,source_count=43,synthetic_git_calls=len(calls),actual_git_calls=0,fixture_ready_and_static_replaced=True,source_raw_bytes_and_snapshot_hashes_real=True,elapsed_seconds=time.monotonic()-started,sampled_self_rss_bytes=psutil.Process().memory_info().rss,absolute_peak_bytes=None,record=record)
with (OUT/'source_pin_result.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='record'},ensure_ascii=False))
