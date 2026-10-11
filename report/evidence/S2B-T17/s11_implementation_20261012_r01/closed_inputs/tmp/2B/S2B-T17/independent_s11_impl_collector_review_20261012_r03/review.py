import argparse
import ast
import difflib
import hashlib
import json
import math
import re
import stat
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
import psutil

# 当前兼容复审仅读取已关闭原件，所有变异均为内存模拟。
ROOT=Path.cwd().resolve();OUT=Path(__file__).absolute().parent
CAND=ROOT/'tmp/2B/S2B-T17/s11_impl_collection_20261012_r01'
CACHE=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01'
COMMIT='a710ec431474841a81912a6055f861e811a151e3'
APPROVED='launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1'
seen={};checks=[];commands=[];cases=[];started=time.monotonic()
def read(p,role='input'):
    b=p.read_bytes();k=p.relative_to(ROOT).as_posix();seen[k]={'path':k,'sha256':hashlib.sha256(b).hexdigest(),'role':role};return b
def obj(p):return json.loads(read(p).decode('utf-8','strict'))
def check(name,ok,e=''):checks.append({'name':name,'status':'PASS' if ok else 'FAIL','evidence':e})
def save(name,j):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
expected={'collector.py':'ee0e697b59d7a9b9b6de22bd44fc93c7fbedade1e1710dd7dfb909e1654a8d35','prepared_receipt_r04.json':'3288fd2d1b07d565fd3fdeb1fda779d99e0ad9607158d7652fe9223f6174d6cc','tool_receipt_r04.json':'d6003621449c0e6fb9ef10f7caf1f62c41a2fbe0780b8b2321c8bfe51166b103','raw_manifest_r04.jsonl':'b70fb90b81c2fa3f7a550c090a7b88ea8fe9b2aa69750636e6ba39797c67e47a','source_diff_r04.patch':'8c528d95737f4985a441826883880e212679d4d2866bbe00204be5f182c7a4d8','source_after_check.py':'15edba9468b8dd3c99dc55135913cbc98d2f625220d94a10f76b18601346b3a8','native_source_after.py':'8e9a12ce58f5ec045cd6c454d62936d918b6f6a47fa15d096243591855d57ddd'}
for name,digest in expected.items():check('固定SHA：'+name,hashlib.sha256(read(CAND/name,'source' if name.endswith('.py') else 'input')).hexdigest()==digest)
source=read(CAND/'collector.py','source').decode('utf-8');old=read(CAND/'collector_before_r04.py','source').decode('utf-8')
check('上一轮源保留',hashlib.sha256(old.encode('utf-8')).hexdigest()=='63def20a125a983a86a374bc7bc1eef8e375cb232a5222822c6f886f6a10cbe9')
actualdiff=''.join(difflib.unified_diff(old.splitlines(True),source.splitlines(True),fromfile='collector_before_r04.py',tofile='collector.py'))
check('diff实际源一致',actualdiff==read(CAND/'source_diff_r04.patch').decode('utf-8'))
prepared=obj(CAND/'prepared_receipt_r04.json');tool=obj(CAND/'tool_receipt_r04.json')
def verify(row):
    p=ROOT/row['path'];b=p.read_bytes();return hashlib.sha256(b).hexdigest()==row['sha256'] and ('bytes' not in row or len(b)==row['bytes'])
rawrows=[json.loads(line) for line in read(CAND/'raw_manifest_r04.jsonl').decode('utf-8').splitlines()]
check('55原件逐项SHA/三字段',len(rawrows)==55 and all(set(r)=={'path','sha256','role'} and verify(r) for r in rawrows))
check('准备所有依赖与adapter绑定',all(verify(r) for r in prepared['dependencies']+prepared['source_after_scripts']) and verify(prepared['common']) and verify(prepared['collector']))
common=read(ROOT/prepared['common']['path'],'source').decode('utf-8')
ctree=ast.parse(common);names={'require','exact','rel','sha','binding','read','mcp_json'}
cn={'ROOT':ROOT,'Path':Path,'json':json,'stat':stat,'hashlib':hashlib}
exec(compile(ast.Module(body=[n for n in ctree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'FROZEN_COMMON_READONLY','exec'),cn)
c=SimpleNamespace(**{name:cn[name] for name in names})
tree=ast.parse(source);ns={'ROOT':ROOT,'WORK':OUT,'REPORT':OUT/'unused_report','COMMIT':COMMIT,'APPROVED_LAUNCH':APPROVED,'c':c,'re':re,'math':math,'json':json,'time':time,'sys':sys,'argparse':argparse,'Path':Path}
fnames={'validate_binding','closed_gate','timing','save','main'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in fnames],type_ignores=[]),str(CAND/'collector.py'),'exec'),ns)
g2path=CACHE/'closed_gate_actual_r02.json';g3path=CACHE/'closed_gate_actual_r03.json'
g2=obj(g2path);g3=obj(g3path)
check('固定r02/r03关闭gate',hashlib.sha256(read(g2path)).hexdigest()=='ef02e12d3afe016464acb21cbfdac2fc938920dff29e96528bf3a1f1e83ca917' and len(read(g2path))==62478 and hashlib.sha256(read(g3path)).hexdigest()=='c35a183a41dd120c12a8bb74510031aad924c74deddf6cb19096ebdc02cc9ed9' and len(read(g3path))==64642)
check('r03关键gate不变/仅追加原件',{k:v for k,v in g2.items() if k!='additional_closed_files'}=={k:v for k,v in g3.items() if k!='additional_closed_files'} and g3['additional_closed_files'][:len(g2['additional_closed_files'])]==g2['additional_closed_files'])
paired_results={};declarations=[]
for name,path in [('r02',g2path),('r03',g3path)]:
    gate,paired=ns['closed_gate'](path);paired_results[name]=paired
    decl=[gate[k] for k in ['source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission']]+gate['design_mcp_records']+gate['additional_closed_files']+gate['native_files']+[gate['timing_summary']]
    for row in decl:ns['validate_binding'](row)
    check('实际关闭gate全部精确组件/SHA：'+name,len(paired)==13,{'binding_rows':len(decl),'unique_binding_paths':len({r['path'] for r in decl})})
    declarations.extend(decl)
tags={x['label']:x for x in paired_results['r03']}
check('实际id4非法1/id6唯一合法0/id7wait0/id13close0',tags['launch_invalid']['history']['id']==4 and tags['launch_invalid']['history']['code']==1 and tags['launch']['history']['id']==6 and tags['launch']['history']['code']==0 and tags['launch']['history']['command']==APPROVED and tags['wait']['history']['id']==7 and tags['wait']['history']['code']==0 and tags['close']['history']['id']==13 and tags['close']['history']['code']==0)
save('actual_history_pairs.json',[{'id':r['history']['id'],'label':r['label'],'command':r['history']['command'],'history_code':r['history']['code'],'client_error':r['client_timeout_or_error'],'client_exit_code':r['client_exit_code'],'raw_binding':r['raw_binding']} for r in paired_results['r03']])
for row in g3['design_mcp_records']:read(ROOT/row['path'])
read(ROOT/g3['mcp_history']['path'],'log')
before=obj(ROOT/g3['source_before']['path']);after=obj(ROOT/g3['source_after']['path']);freeze=obj(ROOT/'report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json');profile=obj(ROOT/'board/s2b_inference_platform.json')
check('实际before/after43/原14/static33/18/8',before['source_commit']==after['source_commit']==COMMIT and before['source_sha256']==after['source_sha256']=={r['path']:r['sha256'] for r in freeze['source_files']} and len(after['source_files'])==43 and len(after['static_source_sha256'])==33 and after['frozen14_sha256']==freeze['frozen14'] and len(profile['rtl_sources'])==18 and len(profile['source_derivation']['derived_sources'])==8)
check('实际源码HEAD字段分列',after['actual_head_at_check']==after['actual_head_after_check']=='932051cdacdf02f729d6a7554b07118d05e96aa4' and after['source_commit']==COMMIT)
check('当前43/前后snap实际SHA',all(verify(r) and hashlib.sha256((ROOT/r['snapshot']).read_bytes()).hexdigest()==r['sha256'] for r in after['source_files']) and all(hashlib.sha256((ROOT/r['snapshot']).read_bytes()).hexdigest()==r['sha256'] for r in before['source_files']))
reportpath=ROOT/g3['timing_summary']['path'];report=read(reportpath,'log').decode('utf-8','strict');sta=ns['timing'](report)
check('真实Physopt postRoute/50MHz仍FAIL',sta['design_state']=='Physopt postRoute' and sta['status']=='FAIL_TIMING' and sta['clock']['frequency_mhz']==50 and sta['timing']['wns_ns']==-3.201 and sta['timing']['tns_ns']==-2123.755 and sta['timing']['setup_failing_endpoints']==908 and sta['timing']['hold_failing_endpoints']==0,sta)
save('actual_report_parsed.json',sta)

# 实际分类只复用候选AST主入口，结果目录边界改为本隔离目录；返回2保存为组件原码。
argv=sys.argv;sys.argv=['ISOLATED_AST_CLASSIFIER','classify','--report',str(reportpath),'--result',str(OUT/'actual_classifier_result.json')]
try:code=ns['main']()
finally:sys.argv=argv
save('actual_classifier.native.json',{'command':['ISOLATED_AST_CLASSIFIER','classify','--report',str(reportpath),'--result',str(OUT/'actual_classifier_result.json')],'native_component_return_code':code,'candidate_main_ast_unchanged':True,'output_boundary':'独立审查目录','actual_vivado_or_collect_executed':False})
check('真实报告分类组件2',code==2 and obj(OUT/'actual_classifier_result.json')['native_exit_code']==2)
snapshotc=c;originalread=c.read;originalmcp=c.mcp_json;originalvalidate=ns['validate_binding']
basehistory=[dict(x['history']) for x in paired_results['r03']];basecalls={r['id']:obj(ROOT/r['path']) for r in g3['design_mcp_records']}
def mockcase(name,change,expect_reject):
    gate=json.loads(json.dumps(g3));hist=json.loads(json.dumps(basehistory));calls=json.loads(json.dumps(basecalls));calls={int(k):v for k,v in calls.items()}
    change(gate,hist,calls)
    store={str(OUT/'MOCK.json'):gate,str(ROOT/gate['mcp_history']['path']):{'history':hist}}
    for row in gate['design_mcp_records']:
        if row['id'] in calls:store[str(ROOT/row['path'])]=calls[row['id']]
    c.read=lambda path:store[str(path)]
    c.mcp_json=lambda value:value if 'history' in value else originalmcp(value)
    ns['validate_binding']=lambda row:ROOT/row['path']
    try:ns['closed_gate'](OUT/'MOCK.json');reject=False;error=None
    except (ValueError,KeyError) as e:reject=True;error=repr(e)
    finally:c.read=originalread;c.mcp_json=originalmcp;ns['validate_binding']=originalvalidate
    record={'case':name,'SIMULATED_NOT_VIVADO':True,'expected_reject':expect_reject,'actual_reject':reject,'error':error};cases.append(record);check(name,reject==expect_reject,record)
def launchchange(cmd):
    def apply(g,h,calls):
        next(x for x in h if x['id']==6)['command']=cmd;calls[6]['input']['command']=cmd
    return apply
mockcase('精确实际PostRoute终点接受',lambda g,h,c:None,False)
for name,cmd in [('旧无to_step命令拒绝','launch_runs impl_1 -jobs 1'),('未路由终点拒绝','launch_runs impl_1 -to_step place_design -jobs 1'),('route但非批准physopt拒绝','launch_runs impl_1 -to_step route_design -jobs 1'),('jobs2拒绝',APPROVED.replace('-jobs 1','-jobs 2')),('大小写改变拒绝',APPROVED.replace('Post-Route','post-route')),('附带命令拒绝',APPROVED+'; puts EXTRA')]:mockcase(name,launchchange(cmd),True)
def second(g,h,calls):
    h.append({'id':14,'command':APPROVED,'code':0});g['design_mcp_records'].append(dict(id=14,label='extra_launch',path='MOCK14',sha256='SIMULATED',bytes=0));calls[14]={'input':{'command':APPROVED},'result':{'content':[{'type':'text','text':'{"exit_code":0}'}]}}
mockcase('第二成功launch拒绝',second,True)
def duplicate(g,h,calls):
    row=next(x for x in g['design_mcp_records'] if x['label']=='open_run');row.update(id=7,path=next(x['path'] for x in g['design_mcp_records'] if x['id']==7))
mockcase('原P1重复id仍拒绝',duplicate,True)
mockcase('history缺一条拒绝',lambda g,h,c:h.pop(5),True)
for state in ['Routed','Fully Routed','Physopt postRoute','Synthesized','Placed','Physopt preRoute','Physopt postroute','Unknown']:
    text=re.sub(r'(?m)^\| Design State\s*:\s*.+$',lambda m:'| Design State : '+state,report)
    try:value=ns['timing'](text);accepted=True
    except ValueError:accepted=False
    check('状态严格白名单：'+state,accepted==(state in ['Routed','Fully Routed','Physopt postRoute']))
bad=report.replace('Timing constraints are not met.','Timing constraints are met.')
try:ns['timing'](bad);conflict_accepted=True
except ValueError:conflict_accepted=False
check('STA数值与文字冲突拒绝',not conflict_accepted)
failure=obj(CAND/'compatibility_r04.native.json');stderr=read(CAND/'compatibility_r04.stderr.log','log').decode('utf-8');trans=obj(CAND/'first_driver_failure_r04_transcription.json')
check('首轮..精确路径失败1原件保留',failure['native_exit_code']==1 and ('..' in stderr or '精确名称不存在' in stderr) and trans['original_tool_return_bytes_saved'] is False and trans['original_tool_return_sha256'] is None)
for name in ['compatibility_r04b.native.json','classify_actual_r04.native.json','prepare_overwrite_r04.native.json']:
    n=obj(CAND/name);check('作者真实原生记录：'+name,n['native_exit_code']==({'classify_actual_r04.native.json':2,'prepare_overwrite_r04.native.json':1}.get(name,0)),n['native_exit_code'])
check('实际工具仍不批准budget/STA',tool['actual_collect_executed'] is False and tool['actual_source_after_executed'] is False and "budget_status='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW'" in source)
for label,args,expectedcode in [('help',['--help'],0),('missing_gate',['collect'],1)]:
    command=[sys.executable,'-B','-X','utf8',str(CAND/'collector.py')]+args;t=time.monotonic();cp=subprocess.run(command,cwd=ROOT,capture_output=True)
    for suffix,data in [('stdout.log',cp.stdout),('stderr.log',cp.stderr)]:
        with (OUT/(label+'.'+suffix)).open('xb') as f:f.write(data)
    record={'command':command,'native_exit_code':cp.returncode,'elapsed_seconds':time.monotonic()-t};commands.append(record);save(label+'.native.json',record);check('独立真实入口：'+label,cp.returncode==expectedcode)
save('mock_cases.json',cases)
result={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'CHANGES_REQUIRED','scope':'S11 collector第三轮实际输入兼容工具G2；仅关闭原件读取/严格命令和状态兼容，不批准STA或预算/G3','source_commit':COMMIT,'evidence_head_at_preparation':'932051cdacdf02f729d6a7554b07118d05e96aa4','reviewer_stop':'STOP_READONLY_S11_COLLECTOR_R04_REVIEW','reviewed_source_hashes':{name:expected[name] for name in ['collector.py','source_after_check.py','native_source_after.py']},'final_gate_sha256':'c35a183a41dd120c12a8bb74510031aad924c74deddf6cb19096ebdc02cc9ed9','checks_count':len(checks),'checks':checks,'findings':[x for x in checks if x['status']=='FAIL'],'commands':commands,'actual_classifier_component_return_code':code,'elapsed_seconds':time.monotonic()-started,'sampled_self_rss_bytes':psutil.Process().memory_info().rss,'absolute_peak_memory_bytes':None,'actual_git_queries':0,'actual_collect_or_source_after_executed':False,'limitations':['真实Physopt postRoute报告WNS−3.201/TNS−2123.755/908仍FAIL，独立隔离AST classifier组件返回2；工具兼容PASS不是时序批准。','ROOT真实关闭gate r02/r03逐组件与SHA验证，13history双射；r03只新增审批timeout/拒绝原件及r02绑定，不由UI todo推断设计通过。','源43/33/18/8/14由冻结与当前RAW/前后snap核验，HEAD字段来自已关闭source-after，不执行本轮Git查询。','source-after两个adapter SHA与上一独立G2完全相同，本轮不重跑adapter或源after。','全程预算保持BLOCKED待实际coverage审查；没有读取live PID/操作ROSS/Vivado/硬件或执行collect。','作者..门禁首失败native1及stderr保留；driver错误只转录非原工具字节。','r03旧源与原失败记录保留，本审查仅写新隔离目录，不改生产、被审脚本、正式证据、Git或STATE。']}
save('review_result.json',result);save('review_inputs.json',list(seen.values()))
print(json.dumps({'status':result['status'],'checks':len(checks),'findings':result['findings'],'seconds':result['elapsed_seconds'],'rss':result['sampled_self_rss_bytes']},ensure_ascii=False))
raise SystemExit(0 if result['status']=='PASS' else 2)
