"""独立验证有界活集合采样与停止身份门禁；真实动作只限自有轻量夹具。"""
import ast,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;D=ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r01'
START=time.monotonic();rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'guard.py')=='17d0d101b1946d2c47a48ce2e9050dea8822c5983b1c497c4ce5e799e159ec78'
spec=importlib.util.spec_from_file_location('candidate_guard',D/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
def ck(name,value,detail=None):
    rows.append(dict(name=name,passed=bool(value),detail=detail))
def methods(p):
    text=p.read_text(encoding='utf-8');tree=ast.parse(text);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Guard')
    return {n.name:ast.get_source_segment(text,n) for n in cls.body if isinstance(n,ast.FunctionDef)}
old=ROOT/'tmp/2B/S2B-T17/s11_resource_guard_20261012_r02/guard.py';sup=ROOT/'tmp/2B/S2B-T17/s11_guard_supervisor_20261012_r02/supervisor.py'
oldm,newm=methods(old),methods(D/'guard.py')
ck('身份/实际停止内核原字节保持',all(oldm[k]==newm[k] for k in ('readback_member','root_terminal','stop_one','stop_tree','historical_member','event','limits','validate','progress')))
ck('supervisor5秒原件保持',sha(sup)=='bbe74e023603ee686a746b92d7dc5c2cb8066b3554eb5e65176bb1f6af88b9f9')
for n,digest in [('tool_receipt.json','7288e4d49315b2fd23503d55727eb33fa40f58734f77a48a43f9e9ed5154860a'),('source_diff.patch','9e8ea21ff0f1860d9ddffc9a0bfb2b4edb7027c155a7e597b8ae471db8684417'),('raw_manifest_final.jsonl','4c6e4e49556fb66302e5a34cc21ab6d5091c80c9349fa9289046c7b19a21e46a')]:ck('作者冻结'+n,sha(D/n)==digest)
raw=[json.loads(x) for x in (D/'raw_manifest_final.jsonl').read_text(encoding='utf-8').splitlines()]
ck('作者40绑定全部SHA',len(raw)==40 and all((ROOT/r['path']).is_file() and sha(ROOT/r['path'])==r['sha256'] for r in raw))
class World:
    """独立替身只表达调度与身份变化，不声称真实OS复用。"""
    def __init__(self):self.nodes={};self.scan=0;self.hook=None;self.errors={};self.stops=[];self.make(10,1,0,11);self.make(20,2,10,23)
    def make(self,p,b,parent,rss):self.nodes[p]=dict(pid=p,create_time=b,ppid=parent,rss_bytes=rss,exe='fixture.exe',cwd=str(W),cmdline=['fixture',str(p)],status='running')
    def proc(self,p):
        if p not in self.nodes:raise g.psutil.NoSuchProcess(p)
        return Fake(self,p)
class Fake:
    def __init__(self,w,p):self.w=w;self.pid=p
    def val(self,k):
        if (self.pid,k) in self.w.errors:raise self.w.errors[self.pid,k]
        if self.pid not in self.w.nodes:raise g.psutil.NoSuchProcess(self.pid)
        return self.w.nodes[self.pid][k]
    def create_time(self):return self.val('create_time')
    def exe(self):return self.val('exe')
    def cwd(self):return self.val('cwd')
    def cmdline(self):return self.val('cmdline')
    def ppid(self):return self.val('ppid')
    def status(self):return self.val('status')
    def memory_info(self):return type('Memory',(),{'rss':self.val('rss_bytes')})()
    def is_running(self):return self.pid in self.w.nodes
    def terminate(self):self.w.stops.append(self.pid);self.w.nodes.pop(self.pid,None)
    def children(self,recursive=False):
        if self.pid==10:self.w.scan+=1
        found=set();front={self.pid}
        while front:
            nxt={p for p,r in self.w.nodes.items() if r['ppid'] in front}-found
            found|=nxt;front=nxt if recursive else set()
        result=[Fake(self.w,p) for p in sorted(found)]
        if self.w.hook:self.w.hook(self.w,self.pid)
        return result
def fixture(w):
    root=dict(w.nodes[10],parent=None);m=g.Guard({},dict(root,allowed_run_dirs=[str(W)]),W/'unused')
    m.initial_root=root;m.event=lambda kind,**kw:m.events.append(dict(kind=kind,**kw));return m,root
def case(name,func):
    w=World();m,root=fixture(w)
    with patch.object(g.psutil,'Process',w.proc):func(w,m,root)
    ck(name,True)
def stable(w,m,r):
    live,u,e=m.collect(r);assert not u and not e and m.collection_observation['scans']==2 and sum(x['rss_bytes'] for x in live)==34
case('稳定两轮真实活RSS',stable)
def dead(w,m,r):
    m.last_members[(20,2)]=dict(w.nodes[20]);del w.nodes[20]
    live,u,e=m.collect(r);assert not u and len(e)==1 and e[0]['status']=='ABSENT' and sum(x['rss_bytes'] for x in live)==11 and 'rss_bytes' not in e[0]
    assert not m.collect(r)[2]
case('确认退出不填零继续采样',dead)
def new(w,m,r):
    w.hook=lambda w,p:w.make(30,3,10,37) if p==10 and w.scan==1 else None
    live,u,e=m.collect(r);assert not u and sum(x['rss_bytes'] for x in live)==71 and m.collection_observation['scans']==3
case('首次枚举后新活后代重扫发现',new)
def late(w,m,r):
    w.hook=lambda w,p:w.make(30+w.scan,30+w.scan,10,1) if p==10 else None
    _,u,_=m.collect(r);assert u and not m.collection_observation['closed'] and m.collection_observation['scans']==3
case('三轮持续变化不闭合BLOCKED',late)
def denied(w,m,r):
    w.errors[20,'rss_bytes']=g.psutil.AccessDenied(20)
    _,u,e=m.collect(r);assert u and not e and (20,2) not in m.retired_members
case('活RSS访问失败保留UNKNOWN',denied)
def orphan(w,m,r):
    w.make(30,3,20,37);live,u,_=m.collect(r);m.last_members.update({(x['pid'],x['create_time']):x for x in live});del w.nodes[20]
    live,u,e=m.collect(r);assert not u and any(x['pid']==30 and not x['stoppable'] for x in live)
    w.make(40,4,30,41);_,u,_=m.collect(r);assert u
case('已知孤儿只监控新未知孤儿拒绝',orphan)
def parentreuse(w,m,r):
    w.make(30,3,20,37);live,u,_=m.collect(r);m.last_members.update({(x['pid'],x['create_time']):x for x in live});w.nodes[20]['create_time']=222
    _,u,_=m.collect(r);assert u and not w.stops
case('旧成员父PID复用拒绝',parentreuse)
def eventrace(w,m,r):
    w.make(30,3,20,37);live,_,_=m.collect(r);leaf=next(x for x in live if x['pid']==30)
    m.event=lambda kind,**kw:w.nodes[20].update(create_time=222) if kind=='PRE_STOP_VERIFIED' else None
    out=m.stop_one(leaf,r,'fixture');assert out['status']=='BLOCKED' and not w.stops
case('fsync事件后第二次父身份复核',eventrace)
def secondancestor(w,m,r):
    w.make(30,3,20,37);w.make(40,4,30,41);live,_,_=m.collect(r);leaf=next(x for x in live if x['pid']==40);w.nodes[20]['cmdline']=['changed']
    out=m.stop_one(leaf,r,'fixture');assert out['status']=='BLOCKED' and not w.stops
case('动作前二级祖先字段漂移拒绝',secondancestor)
def unknownparent(w,m,r):
    w.make(30,3,20,37);live,_,_=m.collect(r);leaf=next(x for x in live if x['pid']==30);w.errors[20,'cwd']=g.psutil.AccessDenied(20)
    out=m.stop_one(leaf,r,'fixture');assert out['status']=='BLOCKED' and not w.stops
case('动作前祖先AccessDenied拒绝',unknownparent)
def changed(w,m,r):
    live,_,_=m.collect(r);m.last_members.update({(x['pid'],x['create_time']):x for x in live});w.nodes[20]['ppid']=0
    _,u,e=m.collect(r);assert u and not e
case('活成员ppid漂移不是退出',changed)
canary=W/'owned_fixture.py'
with canary.open('x',encoding='utf-8') as f:f.write('import subprocess,sys,time\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,"-B","-c","import time;time.sleep(60)"])\nPath(sys.argv[1]).write_text(str(p.pid),encoding="utf-8")\ntime.sleep(60)\n')
external=subprocess.Popen([sys.executable,'-B','-c','import time;time.sleep(60)'],cwd=W)
rootp=subprocess.Popen([sys.executable,'-B',str(canary),str(W/'child_pid.txt')],cwd=W);owned=[];canary_result={}
try:
    extbirth=g.psutil.Process(external.pid).create_time();rootbirth=g.psutil.Process(rootp.pid).create_time()
    until=time.monotonic()+5
    while not (W/'child_pid.txt').is_file() and time.monotonic()<until:time.sleep(.02)
    childpid=int((W/'child_pid.txt').read_text(encoding='utf-8'));childbirth=g.psutil.Process(childpid).create_time();owned=[(rootp.pid,rootbirth),(childpid,childbirth)]
    actual=g.identity(g.psutil.Process(rootp.pid));m=g.Guard({},dict(actual,allowed_run_dirs=[str(W)]),W/'canary_unused');m.initial_root=actual;m.event=lambda kind,**kw:m.events.append(dict(kind=kind,**kw))
    live,u,e=m.collect(actual);assert not u and {x['pid'] for x in live}=={rootp.pid,childpid}
    fixture_limit=1;assert sum(x['rss_bytes'] for x in live)>fixture_limit
    status,stopped,retained=m.stop_tree(actual,live,u,'INDEPENDENT_OWNED_RSS_FIXTURE')
    assert status=='STOPPED' and not retained and external.poll() is None and g.psutil.Process(external.pid).create_time()==extbirth
    canary_result=dict(status=status,owned_identities=owned,stopped=stopped,retained=retained,unrelated_owned_sibling_preserved=True,fixture_limit_bytes=fixture_limit,measured_owned_tree_rss_bytes=sum(x['rss_bytes'] for x in live),events=m.events)
    ck('真实自有父子停止且同cwd兄弟保留',True)
finally:
    for pid,birth in owned+[(external.pid,extbirth)]:
        try:
            p=g.psutil.Process(pid)
            if p.create_time()==birth:p.terminate();p.wait(timeout=3)
        except g.psutil.NoSuchProcess:pass
    rootp.wait(timeout=3);external.wait(timeout=3)
value=dict(status='PASS' if all(x['passed'] for x in rows) else 'CHANGES_REQUIRED',checks=rows,canary=canary_result,elapsed_seconds=time.monotonic()-START,sampled_self_rss_bytes=g.psutil.Process().memory_info().rss,absolute_peak_memory_bytes=None,limitations=['身份复用/漂移是独立mock，不声称真实OS复用。','真实canary仅独立collect与stop_tree小阈值动作，不声称完整CLI/重型/5秒ROOT集成已执行。','旧S11真实null和预算BLOCKED不改；离散集合闭合不是连续或原子峰。'])
with (W/'review_result.json').open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:value[k] for k in ('status','elapsed_seconds','sampled_self_rss_bytes')},ensure_ascii=False))
raise SystemExit(0 if value['status']=='PASS' else 2)
