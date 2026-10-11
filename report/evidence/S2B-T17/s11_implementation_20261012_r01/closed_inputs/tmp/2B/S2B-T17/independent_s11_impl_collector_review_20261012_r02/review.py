import argparse
import ast
import contextlib
import difflib
import hashlib
import io
import json
import math
import re
import subprocess
import sys
import time
from datetime import datetime,timedelta,timezone
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import psutil

# 独立复审仅使用AST和内存文件系统，禁止真实Git、source-after与collect。
ROOT=Path.cwd().resolve();OUT=Path(__file__).absolute().parent/(sys.argv[1] if len(sys.argv)>1 else '')
CAND=ROOT/'tmp/2B/S2B-T17/s11_impl_collection_20261012_r01'
COMMIT='a710ec431474841a81912a6055f861e811a151e3'
checks=[];seen={};commands=[];mockcases=[];started=time.monotonic()
hashes={'collector.py':'63def20a125a983a86a374bc7bc1eef8e375cb232a5222822c6f886f6a10cbe9','source_after_check.py':'15edba9468b8dd3c99dc55135913cbc98d2f625220d94a10f76b18601346b3a8','native_source_after.py':'8e9a12ce58f5ec045cd6c454d62936d918b6f6a47fa15d096243591855d57ddd','prepared_receipt_r03.json':'dc9d17810fcbbabbf51e14545b3fabe5fa3a29724fd6320bbc13fa2bd8443c04','tool_receipt_r03.json':'7e9217313f302ffc1d0b8fd64d6507a212e9243489741206e0e26888504d36c8','raw_manifest_r03.jsonl':'5bd67dd972646252da8a0207670f449c0a1a4aa25f024916a601f93b9da5ed95','source_diff_r03.patch':'0def9534adaf6f9bad98cb56cfcd14867c07b4512baadb28c4a69192ebab9ce4'}
def read(p,role='input'):
    b=p.read_bytes();key=p.relative_to(ROOT).as_posix();seen[key]={'path':key,'sha256':hashlib.sha256(b).hexdigest(),'role':role};return b
def obj(p):return json.loads(read(p).decode('utf-8','strict'))
def check(n,ok,e=''):checks.append({'name':n,'status':'PASS' if ok else 'FAIL','evidence':e})
def save(n,j):
    with (OUT/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
texts={}
for name,digest in hashes.items():
    data=read(CAND/name,'source' if name.endswith('.py') else 'input');check('固定SHA：'+name,hashlib.sha256(data).hexdigest()==digest)
    if name.endswith('.py'):texts[name]=data.decode('utf-8','strict')
rows=[json.loads(s) for s in read(CAND/'raw_manifest_r03.jsonl').decode('utf-8').splitlines()]
def verify(r):
    b=(ROOT/r['path']).read_bytes();return hashlib.sha256(b).hexdigest()==r['sha256'] and ('bytes' not in r or len(b)==r['bytes'])
check('82原件逐项SHA/字段',len(rows)==82 and all(set(r)=={'path','sha256','role'} and verify(r) for r in rows))
prepared=obj(CAND/'prepared_receipt_r03.json');tool=obj(CAND/'tool_receipt_r03.json')
check('依赖和adapter绑定',all(verify(r) for r in prepared['dependencies']+prepared['source_after_scripts']) and verify(prepared['common']) and verify(prepared['collector']))
old=read(CAND/'collector_before_r03.py','source').decode('utf-8');source=texts['collector.py'];tree=ast.parse(source)
check('旧r02源精确保留',hashlib.sha256(old.encode('utf-8')).hexdigest()=='91bf09794a25e7135a047c1f1cece16f08f0945b1b625ff59fe2e8c1e135cebc')
actualdiff=''.join(difflib.unified_diff(old.splitlines(True),source.splitlines(True),fromfile='collector_before_r03.py',tofile='collector.py'))
check('diff精确对应实际源',actualdiff==read(CAND/'source_diff_r03.patch').decode('utf-8'))
def funcsrc(txt,name):
    return ast.get_source_segment(txt,next(n for n in ast.parse(txt).body if isinstance(n,ast.FunctionDef) and n.name==name))
for name in ['timing','save','validate_binding','permanent']:
    check('关键旧语义不变：'+name,funcsrc(old,name)==funcsrc(source,name))
freeze=obj(ROOT/'report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json')
before=obj(ROOT/'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_before.json')
binding=obj(ROOT/'report/evidence/S2B-T17/s11_platform_20261012_r01/s11_source_binding.json')
profile=obj(ROOT/'board/s2b_inference_platform.json')
check('冻结43/33/18/8/14',len(freeze['source_files'])==43 and len(freeze['active_rtl_sources'])==18 and len(freeze['frozen14'])==14 and binding['static_count']==33 and before['source_commit']==COMMIT and len(profile['source_derivation']['derived_sources'])==8)
check('当前43源实际SHA',all(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in freeze['source_files']))
def require(ok,msg):
    if not ok:raise ValueError(msg)

# 关闭门禁直接执行候选AST函数；所有历史和文件均由独立测试构造。
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['closed_gate','timing']]
store={};c=SimpleNamespace(require=require,read=lambda p:store[str(p)],mcp_json=lambda j:j)
ns={'c':c,'ROOT':OUT,'COMMIT':COMMIT,'re':re,'math':math}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(CAND/'collector.py'),'exec'),ns)
ns['validate_binding']=lambda row:OUT/row['path']
labels=['launch_invalid','launch','wait','open_run','reports','close'];cmds=['launch_runs impl_1 -to_step invalid -jobs 1','launch_runs impl_1 -jobs 1','wait_on_run impl_1','open_run impl_1','report_timing_summary -file x; report_route_status','close_project']
basehistory=[{'id':i+1,'code':1 if i==0 else 0,'command':v} for i,v in enumerate(cmds)]
basegate={'root_explicit_signal':'CLOSED_PNR_INPUTS_READY','project_closed':True,'owned_root_exited':True,'source_commit':COMMIT,'root_declared_implementation_execution_count':1,'additional_closed_files':[],'native_files':[]}
for k in ['source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission']:basegate[k]={'path':k+'.json','sha256':'SIMULATED','bytes':0}
basegate['design_mcp_records']=[{'id':i+1,'label':label,'path':'call'+str(i+1)+'.json','sha256':'SIMULATED','bytes':0} for i,label in enumerate(labels)]
def gatecase(name,mutate,should_reject):
    gate=json.loads(json.dumps(basegate));hist=json.loads(json.dumps(basehistory));calls={i+1:{'input':{'command':cmd},'exit_code':1 if i==0 else 0,'result':{'SIMULATED':True}} for i,cmd in enumerate(cmds)}
    mutate(gate,hist,calls)
    store.clear();store[str(OUT/'gate.json')]=gate;store[str(OUT/'mcp_history.json')]={'history':hist}
    for id,call in calls.items():store[str(OUT/('call'+str(id)+'.json'))]=call
    c.mcp_json=lambda j:{'exit_code':j['exit_code']} if 'exit_code' in j else j
    try:ns['closed_gate'](OUT/'gate.json');reject=False;reason=None
    except (ValueError,KeyError) as error:reject=True;reason=repr(error)
    record={'case':name,'SIMULATED_NOT_ACTUAL_PNR':True,'expected_reject':should_reject,'actual_reject':reject,'reason':reason};mockcases.append(record);check(name,reject==should_reject,record)
gatecase('完整六history接受',lambda g,h,c:None,False)
def duplicate(g,h,c):g['design_mcp_records'][3].update(id=3,path='call3.json')
gatecase('原P1重复waitid遗漏open_run拒绝',duplicate,True)
gatecase('未知id拒绝',lambda g,h,c:g['design_mcp_records'][3].update(id=9),True)
gatecase('缺历史拒绝',lambda g,h,c:h.pop(),True)
gatecase('重复原生id拒绝',lambda g,h,c:h[3].update(id=3),True)
gatecase('标签错配拒绝',lambda g,h,c:g['design_mcp_records'][3].update(label='reports'),True)
def swap(g,h,c):g['design_mcp_records'][3]['label']='reports';g['design_mcp_records'][4]['label']='open_run'
gatecase('唯一标签open/reports交换拒绝',swap,True)
gatecase('真实client命令不符拒绝',lambda g,h,c:c[4]['input'].update(command='wait_on_run impl_1'),True)
gatecase('client/native码不同拒绝',lambda g,h,c:c[4].update(exit_code=2),True)
gatecase('根未关闭拒绝',lambda g,h,c:g.update(owned_root_exited=False),True)
def extra(g,h,c):
    h.append({'id':7,'code':1,'command':'puts SIMULATED_EXTRA'});g['design_mcp_records'].append({'id':7,'label':'extra','path':'call7.json','sha256':'SIMULATED','bytes':0});c[7]={'input':{'command':'puts SIMULATED_EXTRA'},'exit_code':1}
gatecase('额外真实失败history精确绑定接受',extra,False)
def extraomit(g,h,c):h.append({'id':7,'code':1,'command':'puts SIMULATED_EXTRA'})
gatecase('额外history遗漏拒绝',extraomit,True)
def clienterror(g,h,c):c[3]['result']={'isError':True,'SIMULATED':'client300s'}
gatecase('provider错误与native分列接受',clienterror,False)

# adapter主入口在完整43源内存文件系统中执行，Git调用全部为独立mock。
vfiles={};vdirs=set()
class VPath(PurePosixPath):
    def exists(self):return str(self) in vfiles or str(self) in vdirs
    def is_dir(self):return str(self) in vdirs
    def is_file(self):return str(self) in vfiles
    def mkdir(self,parents=False,exist_ok=False):
        if self.exists() and not exist_ok:raise FileExistsError(str(self))
        if parents:
            for p in self.parents:vdirs.add(str(p))
        vdirs.add(str(self))
    def iterdir(self):return iter([VPath(p) for p in vfiles.keys()|vdirs if VPath(p).parent==self and VPath(p)!=self])
    def read_bytes(self):return vfiles[str(self)]
    def open(self,mode,encoding=None,newline=None):
        if 'x' in mode and self.exists():raise FileExistsError(str(self))
        path=str(self);binary='b' in mode
        class Sink(io.BytesIO if binary else io.StringIO):
            def close(self):
                data=self.getvalue();vfiles[path]=data if binary else data.encode('utf-8');super().close()
        return Sink()
    def stat(self):return SimpleNamespace(st_size=len(self.read_bytes()))
adapter=texts['source_after_check.py'];atree=ast.parse(adapter)
anodes=[n for n in atree.body if isinstance(n,ast.FunctionDef) and n.name in ['compare_raw','main']]
compare={};exec(compile(ast.Module(body=[n for n in anodes if n.name=='compare_raw'],type_ignores=[]),'compare','exec'),compare)
for name,blob,raw,expected in [('raw',b'a\n',b'a\n','RAW_IDENTICAL'),('eol',b'a\nb\n',b'a\r\nb\r\n','GIT_LF_TO_RAW_CRLF'),('mixed',b'a\r\nb\n',b'a\r\nb\r\n',None),('missing_final',b'a\n',b'a',None),('bareCR',b'a\n',b'a\r',None),('semantic',b'a\n',b'b\n',None)]:
    try:actual=compare['compare_raw'](blob,raw)
    except ValueError:actual=None
    check('独立字节比较：'+name,actual==expected)
adaptercases=[]
def adaptercase(case,expected_error=None):
    vfiles.clear();vdirs.clear();r=VPath('/MEMORY_REVIEW');cache=r/'cache';cache.mkdir(parents=True);common=r/'common.py';vfiles[str(common)]=b'MOCK_COMMON'
    names=['source/'+str(i)+'.sv' for i in range(43)];blobs={p:('wire n'+str(i)+';\n').encode('utf-8') for i,p in enumerate(names)}
    raws={p:(b.replace(b'\n',b'\r\n') if i<6 else b) for i,(p,b) in enumerate(blobs.items())}
    hs={p:hashlib.sha256(b).hexdigest() for p,b in raws.items()};static={k:hs[k] for k in names[:33]};frozen={k:hs[k] for k in names[:14]}
    for p,b in raws.items():vfiles[str(r/p)]=b
    before={'source_commit':COMMIT,'source_files':[{'path':p,'sha256':hs[p]} for p in names],'frozen14_sha256':frozen}
    vfiles[str(r/'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_before.json')]=json.dumps(before).encode('utf-8')
    profile={'rtl_sources':names[:18],'source_derivation':{'derived_sources':names[:8]},'version':'s2b-inference-platform/0.1.11'};freeze={'frozen14':frozen}
    out=cache/'source_after_check_r1';head='932051cdacdf02f729d6a7554b07118d05e96aa4';calls=[];heads=0
    if case=='overwrite':out.mkdir();vfiles[str(out/'source_after.json')]=b'ORIGINAL'
    if case=='raw_before_drift':vfiles[str(r/names[0])]=b'DRIFT'
    def exact(p,kind='file'):
        require(p.is_dir() if kind=='directory' else p.is_file(),'mock精确类型错误');return p
    def sha(p):
        if case=='raw_after_drift' and str(p)==str(r/names[0]):return 'DRIFT'
        return hashlib.sha256(p.read_bytes()).hexdigest()
    def binding(p):return {'path':p.relative_to(r).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())}
    def load():
        if case=='bad_count':return freeze,{k:hs[k] for k in names[:42]},static,profile
        return freeze,hs,static,profile
    cm=SimpleNamespace(require=require,exact=exact,binding=binding,load_freeze=load,read=lambda p:json.loads(p.read_bytes().decode('utf-8')),sha=sha,rel=lambda p:p.relative_to(r).as_posix(),FREEZE=r/'freeze.json',FREEZE_SHA='SIMULATED')
    def run(args,**kwargs):
        nonlocal heads
        assert args[:3]==['git','-C',str(r)];calls.append(args)
        if args[3:]==['rev-parse','HEAD']:
            heads+=1;h='0'*40 if case=='head_before' or (case=='head_after' and heads==2) else head;return SimpleNamespace(returncode=0,stdout=(h+'\n').encode('ascii'),stderr=b'')
        assert args[3]=='show' and args[4].startswith(COMMIT+':')
        p=args[4].split(':',1)[1]
        if case=='git_fail' and p==names[1]:return SimpleNamespace(returncode=7,stdout=b'',stderr=b'MOCK_GIT_FAILURE_RAW')
        return SimpleNamespace(returncode=0,stdout=b'DIFFERENT' if case=='blob_drift' and p==names[0] else blobs[p],stderr=b'')
    spec=SimpleNamespace(loader=SimpleNamespace(exec_module=lambda m:None))
    il=SimpleNamespace(util=SimpleNamespace(spec_from_file_location=lambda *a:spec,module_from_spec=lambda s:cm))
    sub=SimpleNamespace(run=run,list2cmdline=subprocess.list2cmdline)
    ans={'ROOT':r,'WORK':r,'CACHE':cache,'COMMON':common,'COMMON_SHA':hashlib.sha256(b'MOCK_COMMON').hexdigest(),'COMMIT':COMMIT,'argparse':argparse,'Path':VPath,'hashlib':hashlib,'importlib':il,'json':json,'re':re,'subprocess':sub,'sys':sys,'datetime':datetime,'timedelta':timedelta,'timezone':timezone}
    exec(compile(ast.Module(body=anodes,type_ignores=[]),str(CAND/'source_after_check.py'),'exec'),ans)
    originalargv=sys.argv;sys.argv=['SIMULATED_SOURCE_AFTER','--expected-head',head,'--output-dir',str(out)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):ans['main']()
        error=None
    except (ValueError,FileExistsError,AssertionError) as e:error=str(e)
    finally:sys.argv=originalargv
    record=None
    if str(out/'source_after.json') in vfiles and case!='overwrite':record=json.loads(vfiles[str(out/'source_after.json')].decode('utf-8'))
    if expected_error is None:ok=error is None and record['source_commit']==COMMIT and record['actual_head_at_check']==record['actual_head_after_check']==head and len(record['source_files'])==43 and len(calls)==45 and sum(x['git_relation']=='GIT_LF_TO_RAW_CRLF' for x in record['source_files'])==6
    else:ok=error is not None and expected_error in error and record is None
    if case=='git_fail':ok=ok and any(b==b'MOCK_GIT_FAILURE_RAW' for b in vfiles.values()) and any(b'"native_exit_code": 7' in b for b in vfiles.values())
    if case=='overwrite':ok=ok and vfiles[str(out/'source_after.json')]==b'ORIGINAL' and len(calls)==0
    summary={'case':case,'SIMULATED_IN_MEMORY_NOT_GIT':True,'mock_git_calls':len(calls),'error':error,'passed':ok,'record':record if case=='normal' else None};adaptercases.append(summary);check('adapter独立模拟：'+case,ok,{k:v for k,v in summary.items() if k!='record'})
for case,error in [('normal',None),('head_before','实际HEAD不同'),('head_after','真实HEAD变化'),('raw_before_drift','RAW漂移'),('raw_after_drift','RAW变化'),('blob_drift','Git blob与RAW'),('git_fail','真实Git命令失败'),('bad_count','43/33/18/8闭包不同'),('overwrite','输出已存在')]:adaptercase(case,error)
save('adapter_inmemory_cases.json',adaptercases);save('history_mock_cases.json',mockcases)
collect=funcsrc(source,'collect')
check('adapter进入正式闭包且校验preparedr03',"prepared_receipt_r03.json" in collect and "prepared['source_after_scripts']" in collect and "WORK/'source_after_check.py',WORK/'native_source_after.py'" in collect)
check('预算/失败保留不改变',"budget_status='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW'" in collect and 'process.stdout' in collect and 'process.stderr' in collect and 'process.returncode' in collect)
native=texts['native_source_after.py'];ast.parse(native)
check('nativewrapper仅自有child与日志',all(x in native for x in ['not out.exists()','child=subprocess.Popen','psutil.Process(child.pid)','native_exit_code=child.returncode','wrapper_exit_code=child.returncode if failure is None else 3','absolute_peak_bytes=None',"out/'stdout.log'","out/'stderr.log'","out/'native_receipt.json'"]))
for script in ['collector.py','source_after_check.py','native_source_after.py']:
    argv=[sys.executable,'-B','-X','utf8',str(CAND/script),'--help'];t=time.monotonic();cp=subprocess.run(argv,cwd=ROOT,capture_output=True)
    name=script.removesuffix('.py')+'_help'
    for suffix,data in [('stdout.log',cp.stdout),('stderr.log',cp.stderr)]:
        with (OUT/(name+'.'+suffix)).open('xb') as f:f.write(data)
    command={'command':argv,'native_exit_code':cp.returncode,'elapsed_seconds':time.monotonic()-t};commands.append(command);save(name+'.native.json',command);check('独立help：'+script,cp.returncode==0)
result={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'CHANGES_REQUIRED','scope':'S11 PNR collector修复及source-after adapter工具准备独立G2；不批准实际STA/预算/G3','source_commit':COMMIT,'reviewed_source_hashes':{n:hashes[n] for n in ['collector.py','source_after_check.py','native_source_after.py']},'reviewer_stop':'STOP_READONLY_PNR_COLLECTOR_REPAIR_REVIEW','checks_count':len(checks),'checks':checks,'findings':[x for x in checks if x['status']=='FAIL'],'commands':commands,'elapsed_seconds':time.monotonic()-started,'sampled_self_rss_bytes':psutil.Process().memory_info().rss,'absolute_peak_memory_bytes':None,'actual_git_queries':0,'actual_source_after_or_collect_executed':False,'history_mock_count':len(mockcases),'adapter_mock_count':len(adaptercases),'limitations':['adapter内存模型执行原AST的main/compare_raw，43源/33static/18RTL/8派生/14集合为独立模拟；HEAD与Git全部mock，未执行真实source-after。','源码提交a710与实际HEAD字段分列；真实时点、45个Git返回及RAW关系只能ROOT实际运行后核验。','原P1独立复现现被拒绝；额外history及client错误保持精确绑定。','nativewrapper只静态核自有child/超限及日志语义，未运行真实adapter或查询真实任务PID。','预算仍BLOCKED待实际独立coverage审查；当前PNR WNS及STA/部署/G3不属工具准备批准。','原旧collector/首轮失败/旧Reviewer CHANGES_REQUIRED保留；本审查不修改生产、正式证据、Git/STATE或硬件。']}
save('review_result.json',result);save('review_inputs.json',list(seen.values()))
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':result['findings'],'seconds':result['elapsed_seconds'],'rss':result['sampled_self_rss_bytes']},ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 2)
