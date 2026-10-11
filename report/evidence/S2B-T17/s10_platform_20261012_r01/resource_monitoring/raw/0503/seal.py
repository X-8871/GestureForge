"""封存R2工具G2复审，只读旧阻断原件；不批准实际预算运行。"""
from pathlib import Path
import hashlib,json,sys,subprocess
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;SOURCE=ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r02';PLAN=ROOT/'tmp/2B/S2B-T17/s10_root_run_20261012_r01/resource_plan.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
r=load(WORK/'attempt_r01/validation.json');cli=load(WORK/'cli_validation.json');assert r['status']=='PASS_TARGETED_REPRODUCTIONS' and cli['status']=='PASS'
cases=[]
for value in r['cases']:
    item=dict(value)
    if 'guard_native_exit_code' in item:item['guard_run_return_code']=item.pop('guard_native_exit_code')
    cases.append(item)
inputs=[SOURCE/'guard.py',SOURCE/'tool_receipt.json',SOURCE/'raw_manifest.jsonl',PLAN,ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r01/guard.py',ROOT/'tmp/2B/S2B-T17/independent_s10_resource_guard_review_20261012_r01/final_review_receipt.json']
assert sha(inputs[0])=='be8d51ba18cf331458e1d747578f332c4e5cc4b72604a3fb6d09e15030abb4d4' and sha(inputs[1])=='a1be1dd5c53bebf8bdc82a63e1d7710301c5012eed8ca7d9d33a898d874ce893' and sha(inputs[2])=='b24802ea14b5791dcea4177bfb7b4ca1ea328f5069c6a65422585776634dfadc'
assert sha(inputs[5])=='d05272a5785583c020b4faec6f9947eec26abf2fe33de7691d09bb72e0d7066a'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='1eed350c43aae4cdee1f8179a93ce87d75d9f2a8'
commands=[]
for name in ['review.py','cli_probe.py','seal.py']:
    commands.append({'name':name,'command':subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/name)]),'native_exit_code':0,'script_sha256':sha(WORK/name)})
commands[0]['seconds']=r['seconds'];commands[1]['seconds']=cli['seconds']
receipt={'schema_version':1,'task_id':'S10-RG2-R2','decision':'PASS','reviewer_stop':True,'scope':'仅修复版资源guard工具G2；实际ROOT集成/真实运行预算尚未执行，不声明预算PASS。','current_project_commit':'1eed350c43aae4cdee1f8179a93ce87d75d9f2a8','guard_developer_baseline':'3f24c94564d10103aaa00db07356f666b085f687','guard_sha256':sha(inputs[0]),'tool_receipt_sha256':sha(inputs[1]),'reviewed_raw_manifest_sha256':sha(inputs[2]),'resource_plan_sha256':sha(PLAN),'findings':[],
 'closed_findings':[{'id':'RG2-1','closure':'collect253–264对候选独立读回，已确认ABSENT/原PID复用仅记缺测事件并继续；本次短命helper后第2样本真实RSS，第3样本真实1B自测阈值STOPPED，3次样本/已核根停止。','evidence':'attempt_r01/race/guard/guard_receipt.json'},{'id':'RG2-2','closure':'初始及每次采样保存pid/birth成员；root_terminal117–124只读此前对象，活/未知子对象ROOT_EXITED_WITH_REMAINING非零且retained；本次3样本根退出，活child保留、retained1，未追杀。','evidence':'attempt_r01/orphan/guard/guard_receipt.json'}],
 'ancestor_no_such':'真实中间父对象自然退出，而已采grandchild仍活。collect归类CANDIDATE_ALIVE_OR_UNKNOWN_PARENT_CHAIN，stop_one332–338读回候选并BLOCKED，候选和根均不动。新对象复用只读birth差异后ORIGINAL_PID_REUSED并明确untouched，未声称实际OS发生PID复用。',
 'independent_cases':cases,'commands':commands+[cli],'return_code_scope':'review.py中guard_native_exit_code为直接Guard.run函数的CLI等价返回值，非独立guard OS进程码；本receipt统一guard_run_return_code。cli_probe实际guard子程序OS native2另列，审查driver及probe自身OS native0。',
 'safety_review':{'identity':'root_match与same_identity仍逐字段验证，action前重建当前真实祖先链/exe/cwd/birth/cmdline/ppid；身份未知保留。','persistence':'PRE_STOP_VERIFIED事件flush/fsync后重复核验才terminate；PRE_KILL_VERIFIED后同理kill。独立STOP_REQUEST事件先后顺序与输出覆盖拒绝再次通过。','unobserved_members':'root_terminal事件和receipt明确仅已知采样成员，未采到的新生对象未知，不声称整树闭合。','budget':'原计划6GiB树/512MiB可用RAM/8GiB C盘/1秒不变，1B只为已标记fixture阈值；不能修改S9旧4GiB BLOCKED。'},
 'resources':{'seconds':r['seconds'],'os_peak_self_working_set_bytes':r['peak_self_working_set_bytes'],'peak_scope':'审查Python自身生命周期峰，不是子树或系统峰。','cleanup':r['cleanup']},
 'limitations':r['limitations']+['ROOT拟定首样本+native PID确认门禁以及长MCP wait每5秒并行消费guard进程/终态，异常关闭后续派发、owned身份闭合；本轮未执行该集成，工具PASS不批准busy Tcl处置或实际预算保护。','未触及r01工具/旧CHANGES_REQUIRED或S10产品G2原件，未修改生产/Git/STATE，不操作Vivado/硬件/其他窗口对象。','使用未来新Run时必须绑定实际source commit和所有允许目录/进度日志；当前1eed产品提交不把旧guard baseline或prepared plan字段伪称已实际运行。']}
out=WORK/'final_review_receipt.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'input'} for p in inputs]
for p in WORK.rglob('*'):
    if not p.is_file() or p.name=='raw_manifest.jsonl':continue
    assert p.suffix.lower() not in ['.exe','.obj','.o','.dcp','.bit','.gch']
    role='source' if p.suffix=='.py' else 'log' if p.suffix in ['.jsonl','.log'] else 'input' if p.name.endswith('_binding.json') or p.name=='binding.json' else 'result'
    rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role})
assert all(set(row)=={'path','sha256','role'} for row in rows)
raw=WORK/'raw_manifest.jsonl';raw.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in sorted(rows,key=lambda row:row['path'])),encoding='utf-8')
print(json.dumps({'decision':'PASS','reviewer_stop':True,'receipt_sha256':sha(out),'raw_manifest_sha256':sha(raw),'bindings':len(rows)},ensure_ascii=False))
