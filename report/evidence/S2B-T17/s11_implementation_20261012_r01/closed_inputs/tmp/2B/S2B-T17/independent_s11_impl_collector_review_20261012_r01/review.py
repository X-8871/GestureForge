import ast
import hashlib
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
import psutil

# 仅检查冻结源和纯模拟闭合门禁，不导入或执行实际collect。
ROOT=Path.cwd().resolve();OUT=Path(__file__).absolute().parent/(sys.argv[1] if len(sys.argv)>1 else '')
CAND=ROOT/'tmp/2B/S2B-T17/s11_impl_collection_20261012_r01'
SOURCE=CAND/'collector.py';COMMIT='a710ec431474841a81912a6055f861e811a151e3'
checks=[];seen={};cases=[];commands=[];started=time.monotonic()
def read(p,role='input'):
    p=Path(p);b=p.read_bytes();k=p.relative_to(ROOT).as_posix();seen[k]={'path':k,'sha256':hashlib.sha256(b).hexdigest(),'role':role};return b
def obj(p):return json.loads(read(p).decode('utf-8','strict'))
def check(n,b,e=''):checks.append({'name':n,'status':'PASS' if b else 'FAIL','evidence':e})
def save(n,j):
    with (OUT/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
source=read(SOURCE,'source').decode('utf-8');tree=ast.parse(source)
check('collector固定SHA',seen[SOURCE.relative_to(ROOT).as_posix()]['sha256']=='91bf09794a25e7135a047c1f1cece16f08f0945b1b625ff59fe2e8c1e135cebc')
prepared=obj(CAND/'prepared_receipt_r02.json');precheck=obj(CAND/'precheck_result_r02.json')
check('固定prepared/precheck',hashlib.sha256(read(CAND/'prepared_receipt_r02.json')).hexdigest()=='b8bde0c7cb5a321dcaf29b1f6fd1383234a3e72a8a0046dbd81ce1364f4a885b' and hashlib.sha256(read(CAND/'precheck_result_r02.json')).hexdigest()=='f19f23d427ec16ae8ba17a6e4a77887fa6800f093486b3970e45882bb04123bf')
rawmanifest=CAND/'raw_manifest_r02.jsonl'
check('raw43固定SHA',hashlib.sha256(read(rawmanifest)).hexdigest()=='7830a57681b8234cb9aa4baa39edf225c4d3276b02a95db737d12178e559a86f')
rows=[json.loads(s) for s in read(rawmanifest).decode('utf-8').splitlines()]
def verify(r):
    p=ROOT/r['path'];b=p.read_bytes()
    return hashlib.sha256(b).hexdigest()==r['sha256'] and ('bytes' not in r or len(b)==r['bytes'])
check('43原件及依赖实际SHA',len(rows)==43 and all(set(r)=={'path','sha256','role'} and verify(r) for r in rows) and all(verify(r) for r in prepared['dependencies']))
common=ROOT/prepared['common']['path'];check('common实际绑定',verify(prepared['common']),prepared['common']);read(common,'source')
freeze=obj(ROOT/'report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json')
binding=obj(ROOT/'report/evidence/S2B-T17/s11_platform_20261012_r01/s11_source_binding.json')
check('43/33/18/原14/profile',len(freeze['source_files'])==43 and len(freeze['active_rtl_sources'])==18 and len(freeze['frozen14'])==14 and binding['static_count']==33 and set(binding['compiled_rtl'])==set(freeze['active_rtl_sources']) and prepared['profile']=='s2b-inference-platform/0.1.11' and prepared['clock_hz']==50000000 and prepared['visibility']==0)
gitrows=[]
for r in freeze['source_files']:
    p=ROOT/r['path'];b=read(p,'source');cp=subprocess.run(['git','show',COMMIT+':'+r['path']],cwd=ROOT,capture_output=True)
    good=cp.returncode==0 and hashlib.sha256(b).hexdigest()==r['sha256'] and (cp.stdout==b or (b'\r\n' not in cp.stdout and cp.stdout.replace(b'\n',b'\r\n')==b))
    check('实际43源/Git：'+r['path'],good)
    gitrows.append({'command':['git','show',COMMIT+':'+r['path']],'native_exit_code':cp.returncode,'stdout_sha256':hashlib.sha256(cp.stdout).hexdigest(),'match':good})
save('source_git.native.json',gitrows)
check('准备范围未声称真实终态',precheck['actual_collect_executed'] is False and precheck['actual_pnr_terminal_consumed'] is False and prepared['status']=='PREPARED_NOT_EXECUTED_NOT_CLOSED')

# 使用原AST函数本体、独立内存文件表；所有PID/终态均为模拟。
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'closed_gate','timing','save'}]
def require(ok,message):
    if not ok:raise ValueError(message)
store={};c=SimpleNamespace(require=require,read=lambda p:store[str(p)],mcp_json=lambda j:j)
ns={'c':c,'ROOT':OUT,'COMMIT':COMMIT,'re':re,'math':math,'WORK':OUT,'REPORT':OUT/'simulated_report','json':json}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(SOURCE),'exec'),ns)
ns['validate_binding']=lambda row:OUT/row['path']
labels=['launch_invalid','launch','wait','open_run','reports','close']
commands_native=['launch_runs impl_1 -to_step route_design','launch_runs impl_1 -jobs 1','wait_on_run impl_1','open_run impl_1','report_timing_summary -file x','close_project']
history=[{'id':i+1,'code':1 if i==0 else 0,'command':cmd,'output':'SIMULATED','elapsed':.1} for i,cmd in enumerate(commands_native)]
gate={'root_explicit_signal':'CLOSED_PNR_INPUTS_READY','project_closed':True,'owned_root_exited':True,'source_commit':COMMIT,'root_declared_implementation_execution_count':1,'additional_closed_files':[],'native_files':[]}
for k in ['source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission']:gate[k]={'path':k+'.json','sha256':'SIMULATED','bytes':0}
gate['design_mcp_records']=[]
for i,label in enumerate(labels):
    row={'id':i+1,'label':label,'path':'call'+str(i+1)+'.json','sha256':'SIMULATED','bytes':0};gate['design_mcp_records'].append(row)
    store[str(OUT/row['path'])]={'input':{'command':commands_native[i]},'result':{'SIMULATED':True},'exit_code':history[i]['code']}
c.mcp_json=lambda j:{'exit_code':j['exit_code']} if 'exit_code' in j else j
store[str(OUT/'mcp_history.json')]={'history':history}
gatepath=OUT/'simulated_gate.json'
def testgate(name,modify,expect_reject):
    g=json.loads(json.dumps(gate));modify(g);store[str(gatepath)]=g
    try:ns['closed_gate'](gatepath); rejected=False;error=None
    except (ValueError,KeyError) as e:rejected=True;error=repr(e)
    cases.append({'name':name,'simulated_not_real_pnr':True,'expected_reject':expect_reject,'actual_reject':rejected,'error':error})
    check(name,rejected==expect_reject,cases[-1])
testgate('正常完整门禁接受',lambda g:None,False)
testgate('未关闭门禁拒绝',lambda g:g.update(project_closed=False),True)
testgate('history数量不足拒绝',lambda g:g['design_mcp_records'].pop(),True)
testgate('源码基线不同拒绝',lambda g:g.update(source_commit='wrong'),True)
def duplicate(g):
    g['design_mcp_records'][3]['id']=3;g['design_mcp_records'][3]['path']='call3.json'
testgate('重复id遗漏原open_run必须拒绝',duplicate,True)
save('simulated_history_gate.json',{'simulated_not_actual_pnr':True,'history':history,'gate':store[str(gatepath)],'missing_native_history_id':4,'duplicate_declared_id':3})
base='| Design State : Routed\n| Design Timing Summary\n 1.000 0.000 0 10 0.100 0.000 0 10 8.000 0.000 0 10\n| Clock Summary\nclk_fpga_0 {0.000 10.000} 20.000 50.000\n'+''.join('checking '+k+' (0)\n' for k in ['no_clock','constant_clock','pulse_width_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay','multiple_clock','generated_clocks','loops','partial_input_delay','partial_output_delay','latch_loops'])
for name,data,expected in [('模拟已路由满足',base,'NUMERIC_TIMING_MET_PENDING_REVIEW'),('模拟已路由失败',base.replace('1.000 0.000 0 10','-1.000 -3.000 2 10')+'Timing constraints are not met.\n','FAIL_TIMING'),('综合态不能冒充PNR',base.replace('Routed','Synthesized'),None),('缺时钟拒绝',base.replace('clk_fpga_0','other'),None),('缺检查拒绝',base.replace('checking loops (0)\n',''),None)]:
    try:r=ns['timing'](data);actual=r['status']
    except ValueError:actual=None
    check(name,actual==expected,{'expected':expected,'actual':actual,'SIMULATED':True})
savepath=OUT/'simulated_save.json'
c.exact=lambda p,kind:p if p.is_dir() else (_ for _ in ()).throw(ValueError('父目录不存在'))
ns['save'](savepath,{'SIMULATED':True})
try:ns['save'](savepath,{'overwritten':True});overwrite=True
except ValueError:overwrite=False
check('写入拒绝覆盖',not overwrite and obj(savepath)=={'SIMULATED':True})
for label,args,expected in [('help',[str(SOURCE),'--help'],0),('missing_gate',[str(SOURCE),'collect'],1)]:
    argv=[sys.executable,'-B','-X','utf8']+args;t=time.monotonic();cp=subprocess.run(argv,cwd=ROOT,capture_output=True)
    for suffix,data in [('stdout.log',cp.stdout),('stderr.log',cp.stderr)]:
        with (OUT/(label+'.'+suffix)).open('xb') as f:f.write(data)
    cmd={'command':argv,'native_exit_code':cp.returncode,'elapsed_seconds':time.monotonic()-t};commands.append(cmd);save(label+'.native.json',cmd);check('独立入口：'+label,cp.returncode==expected)
nodes={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
collectsrc=ast.get_source_segment(source,nodes['collect'])
check('分类器stdout/stderr/native失败保留路径',all(x in collectsrc for x in ['process.stdout','process.stderr','process.returncode','pnr_classifier.native.json']))
check('全程预算固定BLOCKED而不追认',"budget_status='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW'" in collectsrc and "name='实际全程预算覆盖',status='BLOCKED',command=None,exit_code=None" in collectsrc)
finding={'priority':'P1','file':str(SOURCE),'start':83,'end':96,'problem':'design_mcp_records未要求id唯一及与原history形成双射；数量相等和标签唯一不足。','reproduction':'独立模拟6条history，open_run映射改为id3/call3（wait），保留reports/close等。collector接受；history id4真实open_run未被任何client映射。','impact':'可能封包遗漏实际MCP返回/失败记录，并将错误命令赋给stage标签，不能证明完整history闭包。','closure':'在任何归档写入前要求record id唯一、其集合与history id完全相同；验证open_run/reports等标签的实际命令对应，并新增重复id/遗漏id/阶段错配负向测试。'}
result={'status':'CHANGES_REQUIRED' if any(x['status']=='FAIL' for x in checks) else 'PASS','scope':'S11 PNR collector准备工具独立只读G2；无实际PNR终态消费或时序批准','source_commit':COMMIT,'reviewed_source_hashes':{SOURCE.relative_to(ROOT).as_posix():hashlib.sha256(source.encode('utf-8')).hexdigest()},'reviewer_stop':'STOP_READONLY_S11_PNR_COLLECTOR_PRECHECK','checks':checks,'checks_count':len(checks),'findings':[finding] if any(x['name']=='重复id遗漏原open_run必须拒绝' and x['status']=='FAIL' for x in checks) else [],'simulated_cases':cases,'commands':commands,'elapsed_seconds':time.monotonic()-started,'sampled_self_rss_bytes':psutil.Process().memory_info().rss,'absolute_peak_memory_bytes':None,'limitations':['仅AST函数本体与纯模拟门禁/报告解析、真实help及缺gate入口；没有实际collect/prepare/classify正式写入。','当前PNR/真实进程/ROSS/Vivado/设备/端口未访问；用户拔板约束保持。','预算只证明工具记录BLOCKED语义；未消费真实终态、samples或5秒ROOT监督，不能判全程覆盖。','分类器原生日志保留路径存在；脚本不运行stage checker，后续真实封包checker失败仍须ROOT另存并绑定，不由准备通过替代。','旧正式依赖和43候选源实际SHA核验，不复制历史包；未重跑RTL/综合/实现。']}
save('review_result.json',result);save('review_inputs.json',list(seen.values()));save('mock_cases.json',cases)
print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[x for x in checks if x['status']=='FAIL'],'seconds':result['elapsed_seconds'],'sampled_rss':result['sampled_self_rss_bytes']},ensure_ascii=False))
raise SystemExit(2 if result['status']=='CHANGES_REQUIRED' else 0)
