"""只读审查移交工具与固定before原件，在隔离目录执行代表反例。"""
import ast
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import psutil

HERE=Path(__file__).absolute().parent
ROOT=HERE.parents[3]
NEW=ROOT/'tmp/2B/S2B-T17/s12_handoff_collection_20261012_r01'
OLD=ROOT/'tmp/2B/S2B-T17/s12_launch_prepare_20261012_r01'
WAIT=ROOT/'tmp/2B/S2B-T17/s12_physical_launch_root_20261012_r01/wait.tool.json'
HEAD='467463757158aed80d6f75afadff6a8458614a29'
CASES=[];RUNS=[]
def sha(path):
    """按原字节计算。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):
    """只读UTF8。"""
    return json.loads(path.read_text(encoding='utf-8'))
def bind(path):
    """返回原件绑定。"""
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size)
def write(name,value):
    """仅创建本目录新证据。"""
    with (HERE/name).open('x',encoding='utf-8') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
def run(label,command,expected):
    """保存真实直接子进程码及身份。"""
    start=time.monotonic()
    with (HERE/(label+'.stdout.bin')).open('xb') as out,(HERE/(label+'.stderr.bin')).open('xb') as err:
        child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err)
        try:birth=psutil.Process(child.pid).create_time()
        except psutil.Error:birth='UNKNOWN'
        code=child.wait(timeout=30)
    row=dict(command=command,pid=child.pid,create_time=birth,native_exit_code=child.returncode,direct_wait_exit_code=code,elapsed_seconds=time.monotonic()-start,stdout=bind(HERE/(label+'.stdout.bin')),stderr=bind(HERE/(label+'.stderr.bin')))
    write(label+'.native.json',row);RUNS.append(row)
    assert code==child.returncode==expected
    return row
def reject(name,callback):
    """反例只读，不能覆盖实际原件。"""
    try:callback()
    except (ValueError,KeyError,TypeError) as error:CASES.append(dict(name=name,status='REJECTED_EXPECTED',message=str(error),fixture_only=True))
    else:raise AssertionError('意外通过：'+name)

expected={NEW/'collector.py':'fc7371e3fef0a3385bf34750b5222988469d629e32948366207fd2841d833c2c',NEW/'native.py':'b2c80abb52d14a636dc8d28f0f9a9f5f917b915553ee9fdcfff8616be715fdbc',NEW/'compat_pins.py':'be1805dfa74678252a2ecf35d7e428c5ef9c72037b8a12cda99105a985e51e7e',NEW/'g1_receipt.json':'bbc2e13399196f39de23e46692abef36065e2877b05a4b3acba6b1fe67ef57f5'}
for path,digest in expected.items():assert path.is_file() and sha(path)==digest
assert (NEW/'native.py').read_bytes()==(OLD/'native.py').read_bytes()
old=ast.parse((OLD/'collector.py').read_text(encoding='utf-8')).body
new=ast.parse((NEW/'collector.py').read_text(encoding='utf-8')).body
oldmap={x.name:x for x in old if isinstance(x,ast.FunctionDef)}
newmap={x.name:x for x in new if isinstance(x,ast.FunctionDef)}
assert set(newmap)-set(oldmap)=={'wait_client_handoff','prepared_source_before'}
changed=[name for name in oldmap if ast.dump(oldmap[name])!=ast.dump(newmap[name])]
assert changed==['collect','seal']
assert [ast.dump(x) for x in old if not isinstance(x,ast.FunctionDef)]==[ast.dump(x) for x in new if not isinstance(x,ast.FunctionDef)]
oldp=ast.parse((OLD/'compat_pins.py').read_text(encoding='utf-8')).body
newp=ast.parse((NEW/'compat_pins.py').read_text(encoding='utf-8')).body
assert len(oldp)==len(newp)
assert [x.targets[0].id for x,y in zip(oldp,newp) if ast.dump(x)!=ast.dump(y)]==['WORK']
sys.path.insert(0,str(NEW));import collector as c;import compat_pins as p
p.require_ready();freeze,hashes,static,profile=c.load_freeze()
before_path,before_native=c.prepared_source_before(HEAD)
assert c.WORK==NEW and p.WORK==OLD and len(hashes)==43
g1=load(NEW/'g1_receipt.json')
assert bind(WAIT)==g1['actual_wait_original']
for native in g1['commands']:
    for key in ('stdout','stderr'):assert bind(ROOT/native[key]['path'])==native[key]
assert len(g1['negative_cases'])==32 and all(x['status']=='REJECTED' for x in g1['negative_cases'])
actual=load(WAIT)
history=dict(command='wait_on_run synth_1',code=0,output='INDEPENDENT_FIXTURE_ONLY')
accepted=c.wait_client_handoff(actual,history,'wait')
assert accepted['client_pending_handoff'] is True
CASES.append(dict(name='真实running客户端+明确fixture终态正例',status='PASS',fixture_only=True))
def test(name,mutation):
    """构造彼此独立的污染反例。"""
    call=copy.deepcopy(actual);item=copy.deepcopy(history);client=c.mcp_json(call)
    mutation(call,client,item)
    call['result']['content'][0]['text']=json.dumps(client)
    reject(name,lambda:c.wait_client_handoff(call,item,'wait'))
test('history未完成',lambda a,b,h:h.update(code=None))
test('history失败',lambda a,b,h:h.update(code=2))
test('history bool伪零',lambda a,b,h:h.update(code=False))
test('客户端终态码污染',lambda a,b,h:b.update(exit_code=0))
test('移交客户端错误污染',lambda a,b,h:a['result'].update(isError=True))
test('客户端session错源',lambda a,b,h:b.update(session_id='wrong'))
test('输入命令错源',lambda a,b,h:a['input'].update(command='close_project'))
test('history命令错源',lambda a,b,h:h.update(command='close_project'))
for label in ('source','builder','launch','close'):reject('非WAIT移交'+label,lambda label=label:c.wait_client_handoff(actual,history,label))
for key,value in [('command',['wrong']),('direct_wait_exit_code',1),('terminal_state','RUNNING'),('pid',None)]:
    bad=copy.deepcopy(before_native);bad[key]=value
    real=c.read
    with patch.object(c,'read',side_effect=lambda path,bad=bad:bad if path==before_path else real(path)):
        reject('before错误来源/状态'+key,lambda:c.prepared_source_before(HEAD))
reject('before错误commit',lambda:c.prepared_source_before('0'*40))
with patch.object(c,'sha',return_value='0'*64):reject('before原件SHA漂移',lambda:c.prepared_source_before(HEAD))
cache=HERE/'native_cache';cache.mkdir()
code="import sys,runpy;from pathlib import Path;sys.path.insert(0,"+repr(str(NEW))+");import collector;collector.CACHE=Path("+repr(str(cache))+");sys.argv=['native.py','--prefix','s12_independent_badcommit','--','source','--commit','"+'0'*40+"','--phase','after'];runpy.run_path("+repr(str(NEW/'native.py'))+",run_name='__main__')"
run('new_native_rejection',[sys.executable,'-X','utf8','-B','-c',code],1)
wrapper=load(cache/'s12_independent_badcommit.native.json')
assert wrapper['native_exit_code']==1 and wrapper['command'][4]==str(NEW/'collector.py')
assert 'SOURCE_COMMIT' in (cache/'s12_independent_badcommit.stderr.log').read_text(encoding='utf-8')
git=['C:/Program Files/Git/bin/git.exe','-c','core.longpaths=true','-c','maintenance.auto=false','rev-parse','HEAD']
run('head',git,0)
assert (HERE/'head.stdout.bin').read_text(encoding='ascii').strip()==HEAD
for path,digest in expected.items():assert sha(path)==digest
value=dict(status='PASS_TOOL_G2_ONLY',source_commit=HEAD,reviewed_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    reviewed_inputs=[bind(path) for path in expected],ast_changed_functions=changed,ast_added_functions=sorted(set(newmap)-set(oldmap)),helper_change='WORK only',
    actual_wait=bind(WAIT),before_original=bind(before_path),cases=CASES,native_runs=RUNS,new_native_wrapper=bind(cache/'s12_independent_badcommit.native.json'),
    limitations=['正例history0明确fixture，仅审接口，不宣称真实九条history或综合/STA通过。','未执行collect/seal/source-after，仅隔离badcommit实际新native调用，拒绝native1符合预期。','完整旧绑定G2沿用固定原件，本轮43RAW轻量只读重新核验。','不改生产/HEAD/PRE/被审文件，不调用Vivado或硬件；旧资源GAP保留。'])
write('final_review_receipt.json',value)
print(json.dumps(dict(status=value['status'],receipt=bind(HERE/'final_review_receipt.json'),independent_cases=len(CASES)),ensure_ascii=False))
