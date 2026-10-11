"""S10-RG2独立针对性轻量夹具，证据只写本新审查目录。"""
from pathlib import Path
import importlib.util,subprocess,sys,time,json,hashlib,traceback,os,psutil
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;SOURCE=ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r01';PLAN=ROOT/'tmp/2B/S2B-T17/s10_root_run_20261012_r01/resource_plan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(name,v):(WORK/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(SOURCE/'guard.py')=='a6135186733a07b3257ad4f6a36d6ee57b8799b70c0d5fbc6c04abfc51035416'
assert sha(SOURCE/'tool_receipt.json')=='936fad74fc5f3c0f9184238afef8d1563e6458fa7e9fcce667fda4cded1b4c00'
assert sha(SOURCE/'raw_manifest.jsonl')=='a1cf069cbce778af949d148173102ec705dacd413723225cb9fdf0a36aa093be'
tool=load(SOURCE/'tool_receipt.json');assert sha(PLAN)==tool['plan_sha256']
spec=importlib.util.spec_from_file_location('reviewed_guard',SOURCE/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
plan=load(PLAN);owned={};cases=[];started=time.monotonic();results={'status':'RUNNING'}
def remember(pid):
    p=psutil.Process(pid);value=g.base_identity(p);owned[pid]=value;return p
def cleanup():
    """仅处置自有创建对象，exe/cwd/birth逐项再查；从未枚举或停止其它窗口。"""
    records=[]
    for pid,expected in reversed(list(owned.items())):
        try:
            p=psutil.Process(pid);current=g.base_identity(p)
            assert all(current[k]==expected[k] for k in ['pid','create_time','exe','cwd'])
            p.terminate();code=p.wait(timeout=3);records.append({'pid':pid,'native_exit_code':code,'status':'OWNED_CLEANUP'})
        except psutil.NoSuchProcess:records.append({'pid':pid,'status':'ABSENT'})
    return records
def fixture(name,mode):
    directory=WORK/name;directory.mkdir();marker=directory/'pid.json'
    command=[sys.executable,'-X','utf8','-B',str(WORK/'fixture.py'),mode,str(marker)]
    proc=subprocess.Popen(command,cwd=directory,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);root=remember(proc.pid)
    deadline=time.monotonic()+3
    while not marker.exists():assert time.monotonic()<deadline;time.sleep(.01)
    child_pid=load(marker)['child_pid'];child=remember(child_pid) if child_pid else None
    actual=g.identity(root);binding={k:actual[k] for k in ['pid','create_time','exe','cwd']};binding.update(allowed_run_dirs=[actual['cwd']],run_id=name,source_commit='3f24c94564d10103aaa00db07356f666b085f687')
    save(name+'_binding.json',binding)
    return directory,proc,root,child,binding,command
try:
    directory,proc,root,child,binding,command=fixture('race','race')
    initial=root.children(recursive=True);assert child.pid in [p.pid for p in initial];child.wait(timeout=3)
    original_factory=psutil.Process
    class RaceView:
        """以真实枚举对象重现枚举后自然退出的竞态，不模拟PID或出生时间。"""
        def __init__(self,p):self.p=p
        def __getattr__(self,n):return getattr(self.p,n)
        def children(self,recursive=False):return initial
    def race_factory(pid=None):
        p=original_factory(pid)
        return RaceView(p) if p.pid==root.pid else p
    psutil.Process=race_factory
    try:
        guard=g.Guard(plan,binding,directory/'guard');native=guard.run()
    finally:psutil.Process=original_factory
    receipt=load(directory/'guard/guard_receipt.json');alive=root.is_running()
    assert native==3 and receipt['status']=='BLOCKED' and receipt['reason']=='INCOMPLETE_TREE_IDENTITY' and alive
    assert any(x['reason']=='EXITED_DURING_SAMPLE' for x in receipt['retained'])
    cases.append({'name':'real_helper_exits_after_enumeration','guard_native_exit_code':native,'guard_status':receipt['status'],'heavy_root_still_alive':alive,'fixture_command':subprocess.list2cmdline(command),'evidence':'race/guard/guard_receipt.json','determinism':'注入真实旧枚举列表；子对象已自然退出，其余身份/预算/guard run不模拟。'})
    changed=dict(binding);changed['create_time']-=1
    assert g.Guard(plan,changed,directory/'unused').get_root()[0]=='PID_REUSED' and root.is_running()
    changed=dict(binding);changed['cwd']=str(WORK)
    assert g.Guard(plan,changed,directory/'unused2').get_root()[0]=='IDENTITY_MISMATCH' and root.is_running()
    cases.append({'name':'wrong_birth_and_cwd_rejected','root_untouched':True,'status':'PASS'})
    directory,proc,root,child,binding,command=fixture('orphan','orphan')
    native=g.Guard(plan,binding,directory/'guard').run();receipt=load(directory/'guard/guard_receipt.json');alive=child.is_running()
    assert native==0 and receipt['status']=='ROOT_EXITED' and alive and receipt['retained']==[]
    cases.append({'name':'normal_root_exit_child_remains','guard_native_exit_code':native,'guard_status':receipt['status'],'owned_child_still_alive':alive,'retained_count':len(receipt['retained']),'samples':receipt['samples'],'fixture_command':subprocess.list2cmdline(command),'evidence':'orphan/guard/guard_receipt.json'})
    directory,proc,root,child,binding,command=fixture('stop_request','leaf')
    class StopRequest(g.Guard):
        """启动事件落盘后创建唯一授权STOP_REQUEST，仅作用自有夹具。"""
        def event(self,kind,**values):
            super().event(kind,**values)
            if kind=='START':(self.output/'STOP_REQUEST').write_text('停止自有审查夹具\n',encoding='utf-8')
    native=StopRequest(plan,binding,directory/'guard').run();assert native==2 and not root.is_running()
    events=[json.loads(line) for line in (directory/'guard/events.jsonl').read_text(encoding='utf-8').splitlines()];kinds=[e['kind'] for e in events];assert kinds.index('PRE_STOP_VERIFIED')<kinds.index('TERMINATE_SENT')<kinds.index('POST_STOP_READBACK')
    try:g.Guard(plan,binding,directory/'guard').run()
    except FileExistsError:overwrite='REJECTED'
    else:raise AssertionError('输出覆盖未拒绝')
    cases.append({'name':'stop_request_and_no_overwrite','guard_native_exit_code':native,'event_order':kinds,'overwrite':overwrite,'fixture_command':subprocess.list2cmdline(command)})
    results={'status':'PASS_TARGETED_REPRODUCTIONS','cases':cases,'seconds':round(time.monotonic()-started,3),'peak_self_working_set_bytes':getattr(psutil.Process().memory_info(),'peak_wset',None),'limitations':['只运行自有轻量Python夹具，没有真实Vivado或低RAM/低磁盘压力测试。','helper竞态用真实退出子对象+保存枚举列表作确定性调度；OS未声称实际PID复用。','未复跑Developer191份历史原件，当前三主输入SHA及计划SHA逐字绑定。']}
except Exception:results={'status':'FAIL','cases':cases,'traceback':traceback.format_exc()}
finally:results['cleanup']=cleanup();save('validation.json',results)
print(json.dumps(results,ensure_ascii=False));raise SystemExit(0 if results['status']=='PASS_TARGETED_REPRODUCTIONS' else 1)
