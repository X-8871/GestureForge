"""S10-RG2独立针对性轻量夹具，证据只写本新审查目录。"""
from pathlib import Path
import importlib.util,subprocess,sys,time,json,hashlib,traceback,os,psutil
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;FIXTURE=WORK/'fixture.py';WORK=WORK/'attempt_r01';WORK.mkdir();SOURCE=ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r02';PLAN=ROOT/'tmp/2B/S2B-T17/s10_root_run_20261012_r01/resource_plan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(name,v):(WORK/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(SOURCE/'guard.py')=='be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4'
assert sha(SOURCE/'tool_receipt.json')=='a1be1dd5c53bebf8bdc82a63e1d7710301c5012eed8ca7d9d33a898d874ce893'
assert sha(SOURCE/'raw_manifest.jsonl')=='b24802ea14b5791dcea4177bfb7b4ca1ea328f5069c6a65422585776634dfadc'
assert sha(PLAN)=='0f1cf5fb7382bb4e014cd3c4f8210e05d2d7d6f9b72a539abaaa4112d3b2c3f6'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='1eed350c43aae4cdee1f8179a93ce87d75d9f2a8'
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
    command=[sys.executable,'-X','utf8','-B',str(FIXTURE),mode,str(marker)]
    proc=subprocess.Popen(command,cwd=directory,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);root=remember(proc.pid)
    deadline=time.monotonic()+3
    while not marker.exists():assert time.monotonic()<deadline;time.sleep(.01)
    child_pid=load(marker)['child_pid'];child=remember(child_pid) if child_pid else None
    actual=g.identity(root);binding={k:actual[k] for k in ['pid','create_time','exe','cwd']};binding.update(allowed_run_dirs=[actual['cwd']],run_id=name,source_commit='3f24c94564d10103aaa00db07356f666b085f687')
    binding['source_commit']='1eed350c43aae4cdee1f8179a93ce87d75d9f2a8';binding['fixture_test']=True
    save(name+'_binding.json',binding)
    return directory,proc,root,child,binding,command
try:
    directory,proc,root,child,binding,command=fixture('race','race')
    initial=root.children(recursive=True);assert child.pid in [p.pid for p in initial];child.wait(timeout=3)
    original_children=psutil.Process.children
    delivered=False
    def race_children(p,recursive=False):
        """只给真实夹具根返回已捕获的枚举列表，其余psutil类保持原样。"""
        global delivered
        if p.pid==root.pid and not delivered:delivered=True;return initial
        return original_children(p,recursive=recursive)
    class LaterLimit(g.Guard):
        """前两次正常采样后，把fixture阈值降为1B；资源值保持OS真实采集。"""
        def limits(self):
            if self.sample_count>=2:self.overrides={'tree_rss_bytes':1}
            return super().limits()
    psutil.Process.children=race_children
    try:
        guard=LaterLimit(plan,binding,directory/'guard');native=guard.run()
    finally:psutil.Process.children=original_children
    receipt=load(directory/'guard/guard_receipt.json');alive=root.is_running()
    samples=[json.loads(s) for s in (directory/'guard/samples.jsonl').read_text(encoding='utf-8').splitlines()]
    assert native==2 and receipt['status']=='STOPPED' and not alive and receipt['samples']>=3
    assert receipt['confirmed_sample_exits'] and samples[0]['tree_rss_bytes'] is None and not samples[0]['uncertain'] and samples[1]['tree_rss_bytes']>0 and 'OWNED_TREE_RSS_GT_LIMIT' in samples[-1]['alerts']
    cases.append({'name':'helper_exit_continue_then_real_limit_stop','guard_native_exit_code':native,'guard_status':receipt['status'],'samples':receipt['samples'],'fixture_tree_threshold_last_bytes':1,'measured_rss_last_bytes':samples[-1]['verified_subset_rss_bytes'],'root_after_stop_alive':alive,'fixture_command':subprocess.list2cmdline(command),'evidence':'race/guard/guard_receipt.json','determinism':'首次注入真实已退出枚举列表，随后使用真实树；第三次fixture阈值1B比较真实RSS。'})
    directory,proc,root,child,binding,command=fixture('identity','leaf')
    changed=dict(binding);changed['create_time']-=1
    assert g.Guard(plan,changed,directory/'unused').get_root()[0]=='PID_REUSED' and root.is_running()
    changed=dict(binding);changed['cwd']=str(WORK)
    assert g.Guard(plan,changed,directory/'unused2').get_root()[0]=='IDENTITY_MISMATCH' and root.is_running()
    cases.append({'name':'wrong_birth_and_cwd_rejected','root_untouched':True,'status':'PASS'})
    directory,proc,root,child,binding,command=fixture('orphan','orphan')
    native=g.Guard(plan,binding,directory/'guard').run();receipt=load(directory/'guard/guard_receipt.json');alive=child.is_running()
    assert native==3 and receipt['status']=='ROOT_EXITED_WITH_REMAINING' and alive and receipt['retained'] and receipt['known_members_count']>=2
    cases.append({'name':'normal_root_exit_child_remains','guard_native_exit_code':native,'guard_status':receipt['status'],'owned_child_still_alive':alive,'retained_count':len(receipt['retained']),'samples':receipt['samples'],'fixture_command':subprocess.list2cmdline(command),'evidence':'orphan/guard/guard_receipt.json'})
    directory,proc,root,child,binding,command=fixture('ancestor','ancestor');mid=remember(load(directory/'pid.json')['parent_pid']);initial=root.children(recursive=True);assert child.pid in [p.pid for p in initial];mid.wait(timeout=3)
    expected=g.base_identity(child);root_snapshot=g.identity(root);original_children=psutil.Process.children
    def ancestor_children(p,recursive=False):return [child] if p.pid==root.pid else original_children(p,recursive=recursive)
    guard=g.Guard(plan,binding,directory/'audit')
    with (directory/'ancestor_events.jsonl').open('x',encoding='utf-8') as guard.event_file:
        psutil.Process.children=ancestor_children
        try:members,uncertain,exited=guard.collect(root_snapshot)
        finally:psutil.Process.children=original_children
        assert child.is_running() and not exited and uncertain and uncertain[0]['reason']=='CANDIDATE_ALIVE_OR_UNKNOWN_PARENT_CHAIN'
        outcome=guard.stop_one(expected,root_snapshot,'真实中间祖先已退出')
        assert outcome['status']=='BLOCKED' and child.is_running() and root.is_running()
    save('ancestor_readback.json',{'collect_uncertain':uncertain,'stop_outcome':outcome})
    cases.append({'name':'real_parent_missing_candidate_alive','candidate_still_alive':True,'stop_status':outcome['status'],'collect_classification':uncertain[0]['reason'],'fixture_command':subprocess.list2cmdline(command),'scope':'祖先真实自然退出，候选真实存活；仅以已采到候选列表确定性重现枚举竞态。'})
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
    results={'status':'PASS_TARGETED_REPRODUCTIONS','cases':cases,'seconds':round(time.monotonic()-started,3),'peak_self_working_set_bytes':getattr(psutil.Process().memory_info(),'peak_wset',None),'limitations':['只运行自有轻量Python夹具，没有真实Vivado或低RAM/低磁盘压力测试。','helper竞态用真实退出子对象+保存枚举列表作确定性调度；OS未声称实际PID复用。','未复跑Developer248份历史原件，当前三主输入SHA及计划SHA逐字绑定。','ROOT首样本/guard PID门禁和长wait每5秒终态消费是待实际执行集成，工具G2不能批准实际运行预算。']}
except Exception:results={'status':'FAIL','cases':cases,'traceback':traceback.format_exc()}
finally:results['cleanup']=cleanup();save('validation.json',results)
print(json.dumps(results,ensure_ascii=False));raise SystemExit(0 if results['status']=='PASS_TARGETED_REPRODUCTIONS' else 1)
