"""补核实际路由报告、约束和原生日志，并冻结独立只读结论。"""
import hashlib,json,re,time
from pathlib import Path
ROOT=Path(__file__).parents[4]; W=Path(__file__).parent; F=ROOT/'report/evidence/S2B-T17/s11_implementation_20261012_r01'
T=time.monotonic(); result=json.loads((W/'review_result.json').read_text(encoding='utf-8')); used=result['used_inputs']; checks=[]
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def use(p,role='input'):
    if not p.is_file(): raise ValueError('目标类型错误：'+str(p))
    used[p.relative_to(ROOT).as_posix()]=role; return p
def read(p):return json.loads(use(p).read_text(encoding='utf-8'))
def ck(name,value,detail=None):checks.append(dict(name=name,passed=bool(value),detail=detail))
binding=read(F/'pnr_closed_binding.json'); mapping={r['original']['path']:r['saved']['path'] for r in binding['mapping']}
def saved(p):return ROOT/mapping.get(p,p)
base='tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/reports/'
def report(name):return use(saved(base+name),'log').read_text(encoding='utf-8')
route=report('route_status_postroute.rpt')
ck('全31073可路由网络已布线且错误0',re.search(r'routable nets[^\n]+31073',route) and re.search(r'fully routed nets[^\n]+31073',route) and re.search(r'routing errors[^\n]+\s0\s*:',route))
util=report('utilization_flat_postroute.rpt'); values={}
for name,expected in [('Slice LUTs',17920),('Slice Registers',4056),('Register as Latch',0),('Block RAM Tile',32),('DSPs',145)]:
    found=re.search(r'^\|\s*'+re.escape(name)+r'\s*\|\s*(\d+)\s*\|',util,re.M)
    values[name]=int(found[1]) if found else None; ck('postroute '+name,values[name]==expected)
drc=report('drc_postroute.rpt'); rows=re.findall(r'^\|\s*(\S+)\s*\|\s*(Warning|Error|Critical Warning)\s*\|[^\n]+\|\s*(\d+)\s*\|',drc,re.M)
ck('实际DRC395仅警告无硬错',rows==[('DPIP-1','Warning','117'),('DPOP-1','Warning','140'),('DPOP-2','Warning','136'),('PLBUFGOPT-1','Warning','2')] and 'Checks found: 395' in drc,rows)
method=report('methodology_postroute.rpt'); ck('实际methodology781未关闭','Checks found: 781' in method and re.search(r'\| TIMING-16\s*\| Warning\s*\| Large setup violation\s*\| 781',method))
xdc=report('constraints_postroute.xdc'); exceptions=report('exceptions_postroute.rpt')
ck('20ns与仅两原resetCDC例外',xdc.count('set_false_path')==2 and 'ACTIVE_HIGH_AUX.ACT_HI_AUX' in xdc and 'ACTIVE_LOW_EXT.ACT_LO_EXT' in xdc and xdc.count('syncstages_ff_reg[0]')==2 and 'create_clock -period 20.000' in xdc and not any(s in xdc for s in ('set_multicycle_path','set_clock_groups')))
ck('例外报告原文限制不改写','No valid timing exceptions found.' in exceptions)
native=F/'native_jobs/impl_native_s11_r01'; log=use(native/'runme.log','log').read_bytes()
ck('实现原生日志真实完成及单CPU',b'S11_IMPL_NATIVE_THREADS_1' in log and b'phys_opt_design completed successfully' in log and b'Exiting Vivado at Mon Oct 12 03:38:34 2026' in log and b'using a maximum of 1 CPUs' in log)
ck('六实现阶段原生end marker',all(use(native/('.'+step+'.end.rst'),'result').is_file() for step in ('init_design','opt_design','place_design','phys_opt_design','route_design','post_route_phys_opt_design')))
ck('DCP消费与源码分开保存',b'Reading design checkpoint' in log and b's2b_inference_infer_0.dcp' in log and b'link_design -top s2b_inference_wrapper -part xc7z020clg400-2' in log and binding['raw_native_job_os_exit_code'] is None)
synth=read(ROOT/'report/evidence/S2B-T17/s11_platform_20261012_r01/s11_source_binding.json'); freeze=read(ROOT/'report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json')
ck('继承实际综合18RTL集合',len(synth['compiled_rtl'])==18 and set(synth['compiled_rtl'])==set(freeze['active_rtl_sources']))
run=ROOT/'tmp/2B/S2B-T17/s11_impl_collection_run_20261012_r01'; final=read(run/'final_collection_receipt.json'); raw=use(run/'raw_manifest.jsonl')
rawrows=[json.loads(line) for line in raw.read_text(encoding='utf-8').splitlines()]
ck('作者27原件清单全SHA',len(rawrows)==27 and digest(raw)=='e635cca56c5b7cf2e6fe0120d8672ba12457abd952c17441d62cc4be7587fa92' and all((ROOT/r['path']).is_file() and digest(ROOT/r['path'])==r['sha256'] for r in rawrows))
ck('作者回执冻结SHA',digest(run/'final_collection_receipt.json')=='cad1b02e4763085d558fa9b8ff02e44110686ab62c94215b7ad415a67475cb7b')
for name,code in [('collect_r01',0),('initial_evidence_r01',0),('initial_inputs_r01',2),('final_evidence_r01',0),('final_inputs_r01',2)]:
    n=read(run/(name+'.native.json')); ck('作者实际原生 '+name,n['native_exit_code']==code)
    use(run/(name+'.stdout.log'),'log'); use(run/(name+'.stderr.log'),'log')
gate=read(F/'collector_code/closed_gate_actual_r04.json'); owned=read(saved(gate['owned_root_exit_proof']['path']))
ck('ROOT及10已知身份实际ABSENT',len(owned['readback'])==10 and all(r['status']=='ABSENT' for r in owned['readback']),len(owned['readback']))
supervision=use(saved('tmp/2B/S2B-T17/s11_impl_guard_actual_20261012_r01/supervision.jsonl'),'log'); kinds={}; live=0; first=None; last=None
with supervision.open(encoding='utf-8') as f:
    for line in f:
        row=json.loads(line); kinds[row['kind']]=kinds.get(row['kind'],0)+1
        if row['kind']=='LIVE':live+=1;first=first or row['elapsed_seconds'];last=row['elapsed_seconds']
ck('监督器原始终态保留',kinds.get('TERMINAL')==1 and live>1,dict(kinds=kinds,first_live_elapsed=first,last_live_elapsed=last))
events=use(saved('tmp/2B/S2B-T17/s11_impl_guard_actual_20261012_r01/guard/events.jsonl'),'log')
event_count=sum(1 for _ in events.open(encoding='utf-8'))
manifest=read(F/'delivery_manifest_r02.json')
ck('阶段范围未批准',any(r['status']=='BLOCKED' and r['exit_code'] is None for r in manifest['checks']) and any(r['status']=='NOT_RUN' and 'G3' in r['name'] for r in manifest['checks']))
allchecks=result['checks']+checks; failures=[r['name'] for r in allchecks if not r['passed']]
receipt=dict(status='CHANGES_REQUIRED' if failures else 'PASS',scope='S11实际PNR失败事实准确性和保存原字节可恢复性；不批准STA、完整资源预算覆盖、bit/runtime/G3/G4/G5或阶段2B完成。',source_commit='a710ec431474841a81912a6055f861e811a151e3',actual_evidence_head='932051cdacdf02f729d6a7554b07118d05e96aa4',reviewed_manifest_hash=digest(F/'delivery_manifest_r02.json'),reviewer_stop='STOP_READ_ONLY_NO_FURTHER_WRITES',checks_count=len(allchecks),binding_count=586,source_binding_count=43,checks=allchecks,failures=failures,resource=result['resource'],budget_status='BLOCKED',budget_reason='真实3个RSS缺测样本保留null，最大间隔2.782秒；监督器LIVE是自身轮询，不能替代ROOT消费及完整全程对象证明。已知成员闭合不证明未采对象；绝对峰未知。',actual_sta_status='FAIL',sta=dict(wns_ns=-3.201,tns_ns=-2123.755,failing_setup_endpoints=908,total_setup_endpoints=15082,whs_ns=.037,hold_failing=0),postroute_utilization=values,commands=[read(W/('review_r0'+str(i)+'.native.json')) for i in (1,2,3)]+[read(W/(mode+'.native.json')) for mode in ('evidence','inputs')],actual_collection_native=final['collect'],own_elapsed_seconds=result['elapsed_seconds']+time.monotonic()-T,own_sampled_self_rss_bytes=result['sampled_self_rss_bytes'],own_absolute_peak_memory_bytes=None,limitations=['未执行Git/source-after/collect/仿真/综合/Vivado/ROSS/设备或真实任务PID读回。','before明示继承02:01实际源码预检，during不冒充before；after实际HEAD932与sourcea710分列。','工程目标-2只说明实际报告；不改变AX7020实物-1基线。','report_exceptions原文No valid timing exceptions found与XDC两reset CDC逐项分列，方法学781警告未关闭。','原生worker OS码未知null；marker与日志完成不伪作其OS退出码。','作者和本独审失败原件保留；本审初两轮代码路径/空值处理错误native1不归为设计错误。','较早工具只读路径读失败是工具显示转录，未预先另封原stdout，不声称恢复字节。','仅核当前依赖；不复制586/27全部原件为重复包。'],resource_events_line_count=event_count)
with (W/'final_review_receipt.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
for p in W.iterdir():
    if p.is_file() and p.name!='raw_manifest.jsonl':used[p.relative_to(ROOT).as_posix()]='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'
rows=[dict(path=p,sha256=digest(ROOT/p),role=role) for p,role in sorted(used.items())]
with (W/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as f:
    for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(status=receipt['status'],checks=len(allchecks),failures=failures,receipt_sha256=digest(W/'final_review_receipt.json'),raw_manifest_sha256=digest(W/'raw_manifest.jsonl'),raw_lines=len(rows)),ensure_ascii=False))
raise SystemExit(2 if failures else 0)
