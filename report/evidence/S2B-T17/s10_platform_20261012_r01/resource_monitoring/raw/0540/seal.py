"""封存supervisor工具快审，明确替身与真实运行边界。"""
from pathlib import Path
import json,hashlib,subprocess,sys
WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[3];SOURCE=ROOT/'tmp/2B/S2B-T17/s10_guard_supervisor_20261012_r01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
r=load(WORK/'validation.json');assert r['status']=='PASS'
source=SOURCE/'supervisor.py';assert sha(source)=='d8c6e2e53b4b3012a139a2ab33969d0c308dc2a42e49976cad205b02ba8b578c'
inputs=[source,SOURCE/'native_receipt.json',SOURCE/'selftest_result.json',ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r02/guard.py']
assert sha(inputs[1])=='df11940812469f2a239ca9ea2dfbbd7f5f08e0c43a393c018ad2a3ae7245f1ed' and sha(inputs[2])=='b5fff90c2b324f68ce0001d1a3d67bc2c98efeb364a04e5fd15650cee1af1b9c'
receipt={'schema_version':1,'task_id':'S10-SUP','decision':'PASS','reviewer_stop':True,'source_commit':'1eed350c43aae4cdee1f8179a93ce87d75d9f2a8','supervisor_sha256':sha(source),'fixed_guard_sha256':sha(inputs[3]),'reviewed_native_receipt_sha256':sha(inputs[1]),'reviewed_selftest_result_sha256':sha(inputs[2]),'findings':[],
 'checks':[{'name':'independent_stub_audit','command':subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'review.py')]),'native_exit_code':0,'seconds':r['seconds'],'evidence':'validation.json'},{'name':'seal','command':subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(WORK/'seal.py')]),'native_exit_code':0}]+r['runs'],
 'code_review':{'fixed_entry':'main固定r02 guard路径/SHA，不提供生产guard替换参数；拒绝fixture绑定。','snapshots':'ROOT须独立核对计划/绑定snapshot SHA；main将当前输入SHA组成绑定，supervise47–49启动前逐项复核，独立漂移样例无child、READY false、supervisor native2。没有新增外部批准机制。','ready':'67–78只读取完整首行/index0，首个根pid/birth/exe/cwd及可选cmdline/ppid匹配，alerts/uncertain为空；READY前再次读guard活身份/出生/exe/cwd/cmdline并确认无终态。','watch':'60–66默认5秒重新读取自有guard身份并比较；任何退出/终态/身份失效进入终态。有效替身实际5秒跨度产生至少2条LIVE；身份失效路径为源码审读及绑定Developer自测，未声称OS真PID复用。','native':'guard真实原生0独立保留为child_native_exit_code0；supervisor终态始终native2关闭后续派发，子码7/2及未启动null同样独立保留。原stdout/stderr为二进制文件，中文CRLF原字节已独立验证。','closure':'ROOT_EXITED只覆盖guard已知成员，不声明整树安全。监督器不终止任何对象，异常guard可能仍活/未知，ROOT须消费终态及owned身份读回。'},
 'resources':{'seconds':r['seconds'],'peak_self_working_set_bytes':r['peak_self_working_set_bytes'],'peak_scope':'OS审查Python自身生命周期峰；非子树/系统峰。'},
 'limits':r['limitations']+['PASS仅supervisor工具代码/替身门禁行为；ROOT首样本门禁与长MCP wait消费/实际资源预算保护尚未执行。','所有替身均已由真实子退出码确认终态；无真实guard进程、PID11112探测、Vivado/硬件或其它窗口停止操作。','不修改生产/STATE/Git/被审文件或此前审查原件，无子代理提交。']}
out=WORK/'final_review_receipt.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':'input'} for p in inputs]
for p in WORK.rglob('*'):
    if not p.is_file() or p.name=='raw_manifest.jsonl':continue
    assert p.suffix.lower() not in ['.exe','.obj','.o','.dcp','.bit']
    role='source' if p.suffix=='.py' else 'log' if p.suffix in ['.log','.jsonl'] else 'input' if p.name.endswith('_snapshot.json') or p.name=='config.json' else 'result'
    rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role})
assert all(set(row)=={'path','sha256','role'} and row['role'] in ['source','input','result','log','diagnostic','artifact'] for row in rows)
raw=WORK/'raw_manifest.jsonl';raw.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in sorted(rows,key=lambda row:row['path'])),encoding='utf-8')
print(json.dumps({'decision':'PASS','reviewer_stop':True,'receipt_sha256':sha(out),'raw_manifest_sha256':sha(raw),'bindings':len(rows)},ensure_ascii=False))
