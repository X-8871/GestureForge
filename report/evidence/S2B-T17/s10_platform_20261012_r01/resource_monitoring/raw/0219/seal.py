"""封存S10-RG2阻断审查，不改被审工具或既有产品审查原件。"""
from pathlib import Path
import hashlib,json,sys,subprocess,time
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;SOURCE=ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r01';PLAN=ROOT/'tmp/2B/S2B-T17/s10_root_run_20261012_r01/resource_plan.json';started=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
r=load(WORK/'attempt_r02/validation.json');assert r['status']=='PASS_TARGETED_REPRODUCTIONS'
assert sha(SOURCE/'guard.py')=='a6135186733a07b3257ad4f6a36d6ee57b8799b70c0d5fbc6c04abfc51035416'
review_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'review.py')]);seal_command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'seal.py')])
receipt={'schema_version':1,'task_id':'S10-RG2','decision':'CHANGES_REQUIRED','reviewer_stop':True,'source_commit':'3f24c94564d10103aaa00db07356f666b085f687','guard_sha256':sha(SOURCE/'guard.py'),'tool_receipt_sha256':sha(SOURCE/'tool_receipt.json'),'reviewed_raw_manifest_sha256':sha(SOURCE/'raw_manifest.jsonl'),'resource_plan_sha256':sha(PLAN),'scope':'新资源guard工具正确性/实际预算保护/身份与退出处理，不审批S10功能G2、真实Vivado准入或STA/硬件。',
 'findings':[
 {'id':'RG2-1','priority':'P1','file':'tmp/2B/S2B-T17/s10_resource_guard_20261012_r01/guard.py','lines':[221,223,380,382],'problem':'EXITED_DURING_SAMPLE进入uncertain，未超预算的正常短命helper退出也立即BLOCKED/native3并停止监测；已核根仍继续运行。','evidence':'attempt_r02/race/guard/guard_receipt.json及samples.jsonl，真实枚举保存后子对象自然退出，guard native3，root实际alive。','impact':'之后的6GiB树RSS/512MiB freeRAM/8GiB freeDisk不再采样或执行停止；当前入口未绑定ROOT如何即时读取guard终态并阻止继续派发/持续失守。未知对象保持正确，不代表预算保护完整。','close_condition':'区分已证实消失对象与身份/父链未核对象；确认已退出应记录事件、说明漏采峰并持续监测/重采，不把缺测写零。其它uncertain需持续监测或明确failclosed调用协议：ROOT实时读取guard进程exit/终态，无可用守卫时阻止新的重型派发，并按已核身份处置或报告当前运行；追加短命helper竞态后持续多次采样及后续越限仍触发的独立回归。'},
 {'id':'RG2-2','priority':'P1','file':'tmp/2B/S2B-T17/s10_resource_guard_20261012_r01/guard.py','lines':[305,321,341,344],'problem':'ROOT_MISSING直接ROOT_EXITED/native0，未核对此前采样的子对象，retained默认为[]；last_members仅stop_tree更新，正常采样退出路径没有残留读回。','evidence':'attempt_r02/orphan/guard/guard_receipt.json：3次已核采样后根自然退出，guard native0/retained=[]，此前已采集自有子PID仍存活。','impact':'只能证明绑定根缺失，不能证明运行树退出。子对象可能继续重型工作且失去预算保护，空retained掩盖该恢复边界；tool_receipt说明code0未证明设计成功，仍不足以表示残留树已核。','close_condition':'每次采样保存已核成员与出生/父链来源；根退出/复用后按pid/create_time/exe/cwd只读核对此前对象，明确报告已退出/仍存活/身份未知，不追杀失去可证实父链的孤儿。只有有证据时可称已监控树已退出，残留/未知不能以空retained正常完成表示；ROOT须消费此终态作为运行未闭合/受阻，增加真实根先退出子仍存活以及成员PID复用/读回受限用例。'}],
 'checks':[{'name':'exact_inputs_binding','status':'PASS','command':review_command,'native_exit_code':0,'evidence':'三个冻结主输入与plan SHA逐字匹配；未递归重读191份旧原件。'},{'name':'targeted_reproductions','status':'PASS','command':review_command,'native_exit_code':0,'seconds':r['seconds'],'cases':r['cases']},{'name':'review_fixture_r01_failure','status':'FAIL','command':review_command,'native_exit_code':1,'seconds':1.160004,'script_sha256':sha(WORK/'review_r01_original.py'),'reason':'审查自身把psutil.Process类替换为函数，isinstance类型检查失败；原脚本/validation_r01/race原件保留，修正为只替换children方法并用全新attempt_r02。'},{'name':'seal','status':'PASS','command':seal_command,'native_exit_code':0}],
 'code_review':{'pid_reuse':'get_root比较birth并对初始绑定pid/exe/cwd；停止前verified_chain重复读取身份、实际祖先与目录；未知/不一致对象保持。','current_exe_cwd':'身份每次读取真实exe/cwd，不用oneshot；动作前fsync事件之后再读一次，OS仍无跨树原子事务。','fsync_before_stop':'样本368–370、PRE_STOP_VERIFIED266与event101–103均flush/fsync后才terminate271；kill277事件后278重读再kill279。STOP_REQUEST自有夹具实际事件顺序验证。','unknown_objects':'collect/stop_tree/stop_one身份无法证明时保留对象和根；本次未对真实未知外部对象发信号。身份字段错误真实夹具拒绝且根不动。','output':'STOP_REQUEST仅本输出目录普通非symlink文件；run拒绝旧输出覆盖，本次实际抛FileExistsError且保存原receipt。','root_supervisor':'仅收到resource_plan/guard入口，未绑定守卫终态实时消费与失败闭合实现，不能补旧值或假设保护仍持续。'},
 'resource':{'self_peak_working_set_bytes':r['peak_self_working_set_bytes'],'scope':'OS审查Python自身生命周期峰，不是进程树/全系统峰；仅数个轻量Python夹具。','cleanup':r['cleanup']},
 'limits':['所有审查自有对象完成身份复核清理或实际ABSENT，未启动Vivado/ROSS/硬件，未停止其它窗口进程。','未实际压低RAM/C盘或分配GiB，没有900秒进度等待；本次证明关键失守路径，不替代真实平台准入。','退出竞态用真实枚举成员的确定性调度；未声称OS实际PID复用。','仅新6GiB/512MiB/8GiB/1秒计划，S9旧4GiB预算BLOCKED不变，工具自测不能批准S10 STA/部署/109/1000/G3–G5。','未改guard/plan/Developer证据/S10产品G2 receipt或raw；子代理不提交。']}
out=WORK/'final_review_receipt.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[]
for p in [SOURCE/'guard.py',SOURCE/'tool_receipt.json',SOURCE/'raw_manifest.jsonl',PLAN]:rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'input'})
for p in WORK.rglob('*'):
    if not p.is_file() or p.name=='raw_manifest.jsonl':continue
    assert p.suffix.lower() not in ['.exe','.o','.dcp','.bit','.gch']
    role='source' if p.suffix=='.py' else 'log' if p.suffix=='.jsonl' else 'input' if p.name.endswith('_binding.json') else 'result'
    rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role})
assert all(set(x)=={'path','sha256','role'} and x['role'] in ['source','input','result','log','diagnostic','artifact'] for x in rows)
manifest=WORK/'raw_manifest.jsonl';manifest.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in sorted(rows,key=lambda x:x['path'])),encoding='utf-8')
print(json.dumps({'decision':'CHANGES_REQUIRED','reviewer_stop':True,'receipt_sha256':sha(out),'raw_manifest_sha256':sha(manifest),'bindings':len(rows),'seconds':round(time.monotonic()-started,3)},ensure_ascii=False))
