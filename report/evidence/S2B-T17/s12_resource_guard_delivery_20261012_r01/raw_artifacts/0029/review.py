"""独立核验出生时间门禁及固定监督器；真实进程仅自有轻量替身。"""
import ast,hashlib,importlib.util,json,re,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;D=ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02';T=time.monotonic();checks=[];used=[]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):
    assert p.is_file();used.append(p);return json.loads(p.read_text(encoding='utf-8'))
def ck(name,condition,detail=None):checks.append(dict(name=name,passed=bool(condition),detail=detail))
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for name,digest in [('guard.py','a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac'),('supervisor.py','193416f869463c38065e257545720032438ab12c7bbe30beec6bc8c53d8f9ca0'),('tool_receipt_r04_r02.json','36aec3823a06e410782e39d6dec7619431c85a7b1502fa21f0a57e98c4f5d1de'),('raw_manifest_r04_r02.jsonl','9a80fd53c5b64dfa2cb5dedf886d0c4e74388fa543290f368ed2779e80e4bb83')]:used.append(D/name);ck('冻结'+name,sha(D/name)==digest)
raw=[json.loads(x) for x in (D/'raw_manifest_r04_r02.jsonl').read_text(encoding='utf-8').splitlines()];ck('全部203原件绑定',len(raw)==203 and all((D/r['path']).is_file() and sha(D/r['path'])==r['sha256'] and (D/r['path']).stat().st_size==r['bytes'] for r in raw))
oldp=ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r01/guard.py';olds=ROOT/'tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r02/supervisor.py';used.extend([oldp,olds])
newtext=(D/'guard.py').read_text(encoding='utf-8');oldtext=oldp.read_text(encoding='utf-8');gate='            if parent["create_time"] > current["create_time"]:\n                raise RuntimeError("父出生时间晚于子对象，拒绝复用父PID链")\n'
ck('guard严格仅增加两行门禁',newtext.count(gate)==1 and newtext.replace(gate,'')==oldtext)
suptext=(D/'supervisor.py').read_text(encoding='utf-8');olds_text=olds.read_text(encoding='utf-8')
ck('supervisor严格仅两处pin',suptext.replace('s12_resource_guard_20261012_r02/guard.py','s11_resource_guard_20261012_r02/guard.py').replace('a2f5c581b79a40116bf59c240a7b8c0fe35bac4db7b26a79ce5ba14c451a18ac','eca5338aeb738b86dbf77a0ae881c8dec5068b89bb4553719e8deba2423cb700')==olds_text)
g=module(D/'guard.py','independent_r04');old=module(oldp,'independent_r03');mutant=type(sys)('independent_mutant');mutant.__file__=str(D/'guard.py');exec(compile(newtext.replace(gate,''),'own_birth_mutant','exec'),mutant.__dict__)
# 复用本独审先前自写替身定义；不导入作者测试或执行先前canary。
fixturep=ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_review_20261012_r01/review.py';used.append(fixturep)
tree=ast.parse(fixturep.read_text(encoding='utf-8'));nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('World','Fake','fixture')];exec(compile(ast.Module(body=nodes,type_ignores=[]),'independent_fixture','exec'))
def birth_test(mod,name,kind,should_accept):
    global g
    g=mod;w=World();w.nodes[10]['create_time']=100;w.nodes[20]['create_time']=150;w.make(30,120,20,37)
    if kind=='grandparent':w.nodes[20]['create_time']=150;w.make(40,120,20,41);w.nodes[30].update(create_time=160,ppid=40)
    if kind=='normal':w.nodes[20]['create_time']=110;w.nodes[30]['create_time']=120
    if kind=='equal':w.nodes[20]['create_time']=w.nodes[30]['create_time']=120
    if kind=='above_root':w.nodes[20]['create_time']=110;w.nodes[30]['create_time']=120;w.make(99,500,0,1);w.nodes[10]['ppid']=99
    m,r=fixture(w)
    with patch.object(mod.psutil,'Process',w.proc):
        r=mod.identity(w.proc(10));m.binding=dict(r,allowed_run_dirs=[str(W)]);m.initial_root=r;candidate=mod.identity(w.proc(30));accepted=False
        try:_,leaf,chain=m.verified_chain(candidate,r);accepted=True
        except RuntimeError:pass
        live,u,e=m.collect(r);granted=any(x['pid']==30 and x['stoppable'] for x in live)
    ck(name,accepted==should_accept and granted==should_accept,dict(accepted=accepted,collected_stoppable=granted,unknown=u,mock_only=True))
for mod,label in [(old,'旧r03'),(mutant,'删除出生门禁mutant')]:
    birth_test(mod,label+'首次反例实际复现','direct',True);birth_test(mod,label+'二级祖先反例实际复现','grandparent',True)
new=module(D/'guard.py','independent_r04_fresh')
for kind,accept in [('direct',False),('grandparent',False),('normal',True),('equal',True),('above_root',True)]:birth_test(new,'r04 '+kind,kind,accept)
g=new
for timing in ('before_action','after_first_action_check'):
    w=World();m,r=fixture(w)
    with patch.object(g.psutil,'Process',w.proc):
        live,u,e=m.collect(r);candidate=next(x for x in live if x['pid']==20)
        if timing=='before_action':w.nodes[10]['create_time']=3
        else:m.event=lambda kind,**kw:w.nodes[10].update(create_time=3) if kind=='PRE_STOP_VERIFIED' else None
        outcome=m.stop_one(candidate,r,'mock_birth_race');ck('动作窗口 '+timing,outcome['status']=='BLOCKED' and not w.stops,outcome)
ck('四个实际terminate/kill复核窗口均使用同一门禁',newtext[newtext.index('    def stop_one'):newtext.index('    def progress')].count('self.verified_chain(')==4)
for field in ('create_time','cwd','rss_bytes'):
    w=World();m,r=fixture(w);w.errors[20,field]=g.psutil.AccessDenied(20)
    with patch.object(g.psutil,'Process',w.proc):live,u,e=m.collect(r)
    ck('UNKNOWN保留 '+field,bool(u) and not e)
receipt=read(D/'tool_receipt_r04_r02.json');clar=read(D/'native_command_clarification_r02.json');first=read(D/'r04_native_receipt.json');success=read(D/'r04_native_receipt_r02.json')
ck('首轮1及成功0真实保留',first['native_exit_code']==1 and success['native_exit_code']==0 and clar['actual_outer_exit_codes']==[1,0])
ck('flags澄清分列而不冒充原生argv',all(cmd[0]==sys.executable and cmd[1:4]==['-B','-X','utf8'] for cmd in clar['actual_outer_commands_from_tool_invocations']) and '非执行时sys.orig_argv' in clar['evidence_source'])
ck('阈值/旧预算/绝对峰不退化',receipt['thresholds']==dict(sample_interval_seconds=1,owned_tree_rss_bytes=6442450944,available_ram_bytes=536870912,c_disk_free_bytes=8589934592,logs_no_change_seconds=900,external_supervision_seconds=5) and receipt['continuous_absolute_tree_peak_bytes'] is None and receipt['old_s11_budget_pass'] is False)
s=module(D/'supervisor.py','independent_supervisor');plan=W/'plan.json';bind=W/'fixture_binding.json'
for p,val in [(plan,{}),(bind,dict(cwd=str(W),fixture_test=True))]:
    with p.open('x',encoding='utf-8') as f:json.dump(val,f)
def cli_attempt(name,changed=False):
    args=['supervisor','--plan',str(plan),'--binding',str(bind),'--output-dir',str(W/name)];called=[]
    def forbidden(*a,**k):called.append(True);raise AssertionError('不得启动')
    with patch.object(sys,'argv',args),patch.object(s.subprocess,'Popen',forbidden):
        try:s.main();rejected=False
        except ValueError:rejected=True
    ck('CLI启动前拒绝 '+name,rejected and not called and not (W/name).exists())
cli_attempt('fixture_reject')
changed=W/'changed_guard.py'
with changed.open('x',encoding='utf-8') as f:f.write(newtext+'\n')
with patch.object(s,'GUARD',changed):cli_attempt('sha_reject',True)
# 监督替身只经import接口注入，不给生产CLI任何替换能力。
standin=W/'owned_standin.py'
with standin.open('x',encoding='utf-8') as f:f.write('import json,sys,time\nfrom pathlib import Path\nb=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"));o=Path(sys.argv[2]);(o/"guard").mkdir();\n(o/"guard"/"samples.jsonl").write_text(json.dumps(dict(index=0,members=[b],alerts=[],uncertain=[]))+"\\n",encoding="utf-8");time.sleep(10.2);\n(o/"guard"/"guard_receipt.json").write_text(json.dumps(dict(status="SELFTEST_TERMINAL")),encoding="utf-8");sys.exit(7)\n')
rootp=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(30)'],cwd=W);rootbirth=g.psutil.Process(rootp.pid).create_time()
try:
    actual=g.identity(g.psutil.Process(rootp.pid));binding=W/'owned_root_binding.json'
    with binding.open('x',encoding='utf-8') as f:json.dump(actual,f)
    output=W/'owned_5s_supervision';command=[sys.executable,'-B','-X','utf8',str(standin),str(binding),str(output)]
    code=s.supervise(command,actual,output,[dict(path=str(standin),sha256=sha(standin)),dict(path=str(binding),sha256=sha(binding))])
    terminal=read(output/'supervisor_receipt.json');journal=[json.loads(line) for line in (output/'supervision.jsonl').read_text(encoding='utf-8').splitlines()];live=[x for x in journal if x['kind']=='LIVE'];gaps=[b['elapsed_seconds']-a['elapsed_seconds'] for a,b in zip(live,live[1:])]
    ck('真实READY/LIVE约5秒/终态child7 sup2',code==2 and terminal['child_native_exit_code']==7 and terminal['supervisor_exit_code']==2 and terminal['ready'] is True and any(x['kind']=='READY' for x in journal) and journal[-1]['kind']=='TERMINAL' and len(live)>=3 and all(4.9<=x<=5.5 for x in gaps),dict(gaps=gaps,child_native=terminal['child_native_exit_code'],supervisor_native=code))
    ck('退出终态非0不授予下一派发',code!=0 and terminal['kind']=='TERMINAL' and rootp.poll() is None)
finally:
    p=g.psutil.Process(rootp.pid)
    if p.create_time()==rootbirth:p.terminate();p.wait(timeout=3)
    rootp.wait(timeout=3)
result=dict(status='PASS' if all(x['passed'] for x in checks) else 'CHANGES_REQUIRED',checks=checks,elapsed_seconds=time.monotonic()-T,used_inputs=[p.relative_to(ROOT).as_posix() for p in used],limitations=['出生时间及动作竞争为独立mock，不声称OS真实PID复用。','约5秒监督真实canary仅import注入自有替身；生产CLI拒fixture及SHA变化已独立验证，不证明ROOT heavy集成。','原r03/P1及旧S11预算BLOCKED保持；离散/非原子RSS不等于连续绝对峰。','实际终态非0支持禁派发协议；ROOT未来派发方须消费READY/LIVE/TERMINAL并关闭后续派发。'])
with (W/'review_result.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(status=result['status'],checks=len(checks),failed=[x['name'] for x in checks if not x['passed']],elapsed_seconds=result['elapsed_seconds']),ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 2)
