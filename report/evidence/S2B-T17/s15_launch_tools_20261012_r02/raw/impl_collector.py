"""仅准备及关闭后归档S15单次PNR；不调用Vivado、硬件或真实进程查询。"""
import argparse,hashlib,importlib.util,json,math,re,sys,subprocess,time
from pathlib import Path
import compat_pins
ROOT=Path(__file__).parents[4]; WORK=Path(__file__).parent
CACHE=compat_pins.PNR_CACHE
PROJECT=compat_pins.PROJECT
REPORT=compat_pins.PNR_REPORT
COMMIT=compat_pins.SOURCE_COMMIT
APPROVED_LAUNCH='launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1'
EVIDENCE_HEAD_AT_PREPARATION=None
COMMON=WORK/'collector.py'
COMMON_SHA='5e58d32551fa3baf8f73e755defde178fc0a5f13cb03b8c018c619bbb4e1bc43'
assert hashlib.sha256(COMMON.read_bytes()).hexdigest()==COMMON_SHA
spec=importlib.util.spec_from_file_location('common',COMMON); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
FREEZE=compat_pins.SOURCE_FREEZE
FREEZE_SHA=compat_pins.SOURCE_FREEZE_SHA
SYNTH=compat_pins.SYNTH_MANIFEST
SYNTH_SHA=compat_pins.SYNTH_MANIFEST_SHA
REVIEW=compat_pins.TOOLS_G2
REVIEW_SHA=compat_pins.TOOLS_G2_SHA
GUARD=compat_pins.GUARD
GUARD_SHA=compat_pins.GUARD_SHA
SUP=compat_pins.SUP
SUP_SHA=compat_pins.SUP_SHA
def save(path,value):
 """只允许授权隔离目录或明确交接后的新正式文件，不覆盖。"""
 c.require(path.is_relative_to(WORK) or path.is_relative_to(REPORT),'写入越界')
 c.exact(path.parent,'directory'); c.require(not path.exists(),'目标已存在')
 with path.open('x',encoding='utf-8',newline='\n') as f: json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')
def validate_binding(row):
 """声明输入必须同时绑定路径、原字节SHA和长度。"""
 actual=c.binding(ROOT/row['path']); c.require(all(actual[k]==row[k] for k in actual),'输入漂移：'+row['path']); return ROOT/actual['path']
def permanent(path):
 """正式原件直接绑定；临时工具只从S15正式映射核原恢复路径/SHA。"""
 if path.is_relative_to(ROOT/'report'): return c.binding(path)
 return compat_pins.resolve_permanent(path)
def prepare(receipt):
 """只冻结依赖及关闭后所需输入，不读取live工程日志或宣称就绪终态。"""
 compat_pins.require_ready(pnr=True)
 for p,digest in ((FREEZE,FREEZE_SHA),(SYNTH,SYNTH_SHA),(REVIEW,REVIEW_SHA),(GUARD,GUARD_SHA),(SUP,SUP_SHA)):
  c.require(c.sha(p)==digest,'准备依赖SHA不同')
 freeze,hashes,static,profile=c.load_freeze(); c.require(len(freeze['active_rtl_sources'])==18 and len(freeze['frozen14'])==14,'冻结来源集合不同')
 for p in (PROJECT,CACHE,REPORT): c.exact(p,'directory')
 source_binding=SYNTH.parent/'s15_source_binding.json'; bound=c.read(source_binding)
 c.require(bound['source_count']==len(hashes) and bound['static_count']==len(static) and set(bound['compiled_rtl'])==set(freeze['active_rtl_sources']),'继承综合编译闭包不符')
 deps=[c.binding(FREEZE),c.binding(SYNTH),c.binding(source_binding),c.binding(compat_pins.FUNCTIONAL_G1),c.binding(compat_pins.FUNCTIONAL_G2),c.binding(compat_pins.SYNTH_G2),c.binding(WORK/'compat_pins.py'),compat_pins.runtime_config_binding(),permanent(REVIEW),permanent(GUARD),permanent(SUP)]
 # 收集公共函数源也必须在正式包中可恢复；准备阶段只核对，关闭后才复制。
 result=dict(status='PREPARED_NOT_EXECUTED_NOT_CLOSED',source_commit=COMMIT,evidence_head_at_preparation=EVIDENCE_HEAD_AT_PREPARATION,source_count=43,active_rtl_count=18,frozen14_count=14,profile='s2b-inference-platform/0.1.12',clock_hz=50000000,visibility=0,dependencies=deps,collector=c.binding(Path(__file__)),common=c.binding(COMMON),source_after_scripts=[c.binding(WORK/name) for name in ('source_after_check.py','native_source_after.py')],required_gate_fields=['root_explicit_signal=CLOSED_PNR_INPUTS_READY','project_closed=true','owned_root_exited=true','root_declared_implementation_execution_count=1','source_commit='+COMMIT,'source_before/source_after/source_before_native/source_after_native/mcp_history/immutable_session_log/guard_receipt/supervisor_receipt/owned_root_exit_proof/resource_admission bindings','design_mcp_records：每条原生history的id、label、path、sha256、bytes；声明id唯一且与history双射','additional_closed_files：入口拒绝、ROOT5秒监督消费、最终监测原件、必要恢复输入','native_files：实际impl_1原生日志/命令/marker逐项原字节绑定'],required_design_labels=['launch','wait','open_run','reports','close'],limits='6GiB树/512MiB可用RAM/8GiB磁盘/1秒；工具准备不批准实际预算',heavy_ross_hardware_or_process_query=False)
 result.update(source_count=len(hashes),static_count=len(static),profile=profile['version'])
 c.require(re.fullmatch(r'prepared_receipt(?:_r\d+)?\.json',receipt) is not None,'准备记录名不合法')
 save(WORK/receipt,result); print(json.dumps(result,ensure_ascii=False))
def timing(text):
 """只解析实际报告数值，未知设计状态不补旧值，不把包装0当时序批准。"""
 section=text.split('| Design Timing Summary',1); c.require(len(section)==2,'缺少时序汇总')
 rows=[line.split() for line in section[1].split('| Clock Summary',1)[0].splitlines() if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*',line)]
 c.require(len(rows)==1,'时序数值不唯一')
 names=('wns_ns','tns_ns','setup_failing_endpoints','setup_total_endpoints','whs_ns','ths_ns','hold_failing_endpoints','hold_total_endpoints','wpws_ns','tpws_ns','pulse_failing_endpoints','pulse_total_endpoints')
 values={k:float(v) if k.endswith('_ns') else int(v) for k,v in zip(names,rows[0])}
 c.require(all(math.isfinite(v) for v in values.values()),'时序非有限值')
 clocks=re.findall(r'^clk_fpga_0\s+\{([\d.]+)\s+([\d.]+)\}\s+([\d.]+)\s+([\d.]+)\s*$',text,re.M); c.require(len(clocks)==1,'时钟不唯一')
 rise,fall,period,hz=map(float,clocks[0]); c.require(period==20 and hz==50,'不是50MHz')
 checks={}
 for key in ('no_clock','constant_clock','pulse_width_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay','multiple_clock','generated_clocks','loops','partial_input_delay','partial_output_delay','latch_loops'):
  found=set(re.findall('checking '+key+r' \((\d+)\)',text)); c.require(len(found)==1,'缺失/冲突时序检查：'+key); checks[key]=int(next(iter(found)))
 state=re.findall(r'^\| Design State\s*:\s*(.+)$',text,re.M); c.require(len(state)==1,'设计状态缺失/冲突')
 c.require(state[0].strip() in ('Routed','Fully Routed','Physopt postRoute'),'不是已路由设计状态；不推断缺失状态')
 failing=any(v<0 for k,v in values.items() if k.endswith('_ns')) or any(values[k]>0 for k in ('setup_failing_endpoints','hold_failing_endpoints','pulse_failing_endpoints')) or any(checks.values())
 c.require(('Timing constraints are not met.' in text)==failing,'时序文字数值冲突')
 return dict(status='FAIL_TIMING' if failing else 'NUMERIC_TIMING_MET_PENDING_REVIEW',timing=values,clock=dict(period_ns=period,frequency_mhz=hz,rise_ns=rise,fall_ns=fall),check_timing=checks,design_state=state[0].strip(),independent_pnr_review='NOT_RUN',hardware='NOT_RUN')
def closed_gate(path):
 """缺门禁时在任何正式写入前拒绝；终态必须由ROOT真实关闭证据支持。"""
 compat_pins.require_ready(pnr=True)
 gate=c.read(path)
 c.require(gate.get('root_explicit_signal')=='CLOSED_PNR_INPUTS_READY' and gate.get('project_closed') is True and gate.get('owned_root_exited') is True and gate.get('source_commit')==COMMIT and gate.get('root_declared_implementation_execution_count')==1,'ROOT关闭门禁未成立')
 keys=('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission','runtime_config')
 for key in keys: validate_binding(gate[key])
 c.require(gate['runtime_config']==compat_pins.runtime_config_binding(),'ROOT关闭配置与当前原字节不同')
 for key in ('design_mcp_records','additional_closed_files','native_files'):
  for row in gate[key]: validate_binding(row)
 if gate.get('timing_summary'): validate_binding(gate['timing_summary'])
 labels=[r['label'] for r in gate['design_mcp_records']]
 c.require(all(labels.count(k)==1 for k in ('launch','wait','open_run','reports','close')),'必需PNR标签缺失或重复')
 history=c.mcp_json(c.read(ROOT/gate['mcp_history']['path']))['history']; byid={r['id']:r for r in history}
 c.require(len(byid)==len(history)==len(gate['design_mcp_records']),'必须保留完整原生history闭包')
 declared_ids=[r['id'] for r in gate['design_mcp_records']]
 c.require(len(declared_ids)==len(set(declared_ids)) and set(declared_ids)==set(byid),'声明history id必须唯一且与真实history形成双射')
 command_patterns=dict(launch_invalid=r'launch_runs\s+impl_1\s+.*-to_step(?:\s+.*)?',launch=r'launch_runs\s+impl_1(?:\s+[^;\r\n]+)?',wait=r'wait_on_run impl_1',open_run=r'open_run impl_1',reports=r'report_(?:timing_summary|timing|utilization|clocks|exceptions|methodology|drc|route_status|power)\b[\s\S]*',close=r'close_project')
 paired=[]
 for row in gate['design_mcp_records']:
  item=byid[row['id']]; call=c.read(ROOT/row['path']); result=call.get('result',call)
  c.require(call['input']['command']==item['command'],'命令输入/history不同')
  if row['label'] in command_patterns: c.require(re.fullmatch(command_patterns[row['label']],item['command']) is not None,'PNR标签与原生命令类型不同：'+row['label'])
  client=c.client_pair(item,row['label'],call,allow_error=True)
  paired.append(dict(label=row['label'],history=item,raw_binding=row,**client))
 tags={r['label']:r['history'] for r in paired}
 c.require(all(type(tags[label]['code']) is int and tags[label]['code']==0 for label in ('launch','wait','open_run','reports','close')),'五必需PNR命令原生码必须严格int0')
 c.require(labels.count('launch_invalid')<=1,'实际invalid失败记录重复')
 if 'launch_invalid' in tags:
  invalid=tags['launch_invalid']
  c.require(type(invalid['code']) is int and invalid['code']!=0 and invalid['command']=='launch_runs impl_1 -to_step post_route_phys_opt_design -jobs 1','可选历史invalid必须是真实非0精确失败原件')
 c.require(tags['launch']['code']==0 and tags['launch']['command']==APPROVED_LAUNCH,'合法launch不是本轮精确批准的Post-Route终点')
 c.require(sum(r['command'].startswith('launch_runs impl_1') and type(r['code']) is int and r['code']==0 for r in history)==1,'合法impl启动不是一次')
 c.require(tags['wait']['command']=='wait_on_run impl_1','wait不是独立原生命令')
 c.require(tags['close']['command']=='close_project' and tags['close']['code']==0,'工程关闭失败')
 return gate,paired
def collect(gate_path):
 """仅真实关闭后单次归档；不改原件，不复制DCP/bit或cache。"""
 compat_pins.require_ready(pnr=True)
 gate,paired=closed_gate(gate_path); prepared=c.read(WORK/'prepared_receipt.json')
 for row in prepared['dependencies']: validate_binding(row)
 for row in prepared['source_after_scripts']: validate_binding(row)
 c.require(c.binding(Path(__file__))==prepared['collector'] and c.binding(COMMON)==prepared['common'],'收集器准备后漂移')
 before=c.read(ROOT/gate['source_before']['path']); after=c.read(ROOT/gate['source_after']['path']); freeze=c.read(FREEZE)
 frozen={r['path']:r['sha256'] for r in freeze['source_files']}
 for record,key in ((before,'source_before_native'),(after,'source_after_native')):
  c.require(record['source_commit']==COMMIT and {r['path']:r['sha256'] for r in record['source_files']}==frozen,'实际源前后漂移')
  c.require(record['frozen14_sha256']==freeze['frozen14'] and record['static_source_sha256']==c.read(SYNTH.parent/'mcp_closed'/'static_actual_closed.json')['source_sha256'],'原14/static实际绑定不同')
  c.require(all(r['git_relation'] in ('RAW_IDENTICAL','GIT_LF_TO_RAW_CRLF') for r in record['source_files']),'实际Git RAW/EOL关系缺失或漂移')
  native=c.read(ROOT/gate[key]['path']); c.require(native['native_exit_code']==0 and bool(native['command']),'源码原生核验不是0')
  for r in record['source_files']: c.require(c.sha(ROOT/r['snapshot'])==r['sha256'],'实际源码快照漂移')
 guard=c.read(ROOT/gate['guard_receipt']['path']); sup=c.read(ROOT/gate['supervisor_receipt']['path'])
 c.require(guard['guard_sha256']==GUARD_SHA and sup['supervisor_sha256']==SUP_SHA,'实际工具绑定不同')
 c.require(guard['status'] not in ('RUNNING','READY') and sup['child_native_exit_code'] is not None,'监测未终态')
 c.require(not any((REPORT/name).exists() for name in ('closed_inputs','collector_code','pnr_closed_binding.json','delivery_manifest.json','original_inventory.json')),'整理产物已存在，拒绝重跑覆盖')
 initial=[c.binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
 save(REPORT/'original_inventory.json',dict(files=initial))
 original=[]; mapping=[]
 declarations=[gate[k] for k in ('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission')]+gate['design_mcp_records']+gate['additional_closed_files']+gate['native_files']
 if gate.get('timing_summary'): declarations.append(gate['timing_summary'])
 for record in (before,after): declarations.extend(c.binding(ROOT/r['snapshot']) for r in record['source_files'] if not (ROOT/r['snapshot']).is_relative_to(ROOT/'report'))
 for row in declarations:
  p=validate_binding(row); c.require(p.suffix.lower() not in ('.exe','.dcp','.bit','.pb','.wdf','.o','.obj','.a','.lib','.dll','.pdb','.wdb','.pdi','.elf','.bin','.pyc') and '__pycache__' not in p.parts,'缓存/二进制不能归档')
  original.append(c.binding(p))
  if p.is_relative_to(REPORT): mapping.append(dict(original=row,saved=c.binding(p))); continue
  target=REPORT/'native_jobs'/'impl_native_s15_r01'/p.name if p.is_relative_to(PROJECT) else REPORT/'closed_inputs'/Path(row['path'])
  if target.exists(): c.require(c.sha(target)==row['sha256'],'重复输入不同'); continue
  target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f: f.write(p.read_bytes())
  mapping.append(dict(original=row,saved=c.binding(target)))
 for p in (Path(__file__),COMMON,WORK/'prepared_receipt.json',gate_path,WORK/'source_after_check.py',WORK/'native_source_after.py',WORK/'compat_pins.py'):
  target=REPORT/'collector_code'/('s15_synthesis_collector_common.py' if p==COMMON else p.name); target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f: f.write(p.read_bytes())
 timing_binding=gate.get('timing_summary'); sta=dict(status='BLOCKED_MISSING_ACTUAL_TIMING',timing=None,design_state=None); classifier=None
 if timing_binding:
  command=[sys.executable,'-X','utf8','-B',str(Path(__file__)),'classify','--report',str(validate_binding(timing_binding)),'--result',str(REPORT/'pnr_sta_result.json')]
  start=time.monotonic(); process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45)
  for name,data in (('stdout',process.stdout),('stderr',process.stderr)):
   with (REPORT/('pnr_classifier.'+name+'.log')).open('xb') as f: f.write(data)
  classifier=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=process.returncode,elapsed_seconds=time.monotonic()-start,peak_memory_bytes=None)
  save(REPORT/'pnr_classifier.native.json',classifier); sta=c.read(REPORT/'pnr_sta_result.json')
 save(REPORT/'pnr_closed_binding.json',dict(source_commit=COMMIT,source_count=len(frozen),profile=freeze['profile'],paired_calls=paired,mapping=mapping,original_bindings=original,timing=sta,guard_status=guard['status'],guard_native_exit_code=sup['child_native_exit_code'],supervisor_native_exit_code=sup['supervisor_exit_code'],sampled_tree_peak_bytes=guard.get('sampled_peak_tree_rss_bytes'),absolute_tree_peak_bytes=None,raw_native_job_os_exit_code=None,budget_status='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW',limitations=['原生worker日志/marker不伪作OS返回码。','ROOT_EXITED只已知成员；新旧预算缺测不追补。','非法to_step native1与入口MCP/auto-review失败原件保留；未知字段null。','只读PNR证据，独立PNR审查/bit/硬件/G3仍NOT_RUN。']))
 interfaces=c.read(SYNTH)['interfaces']; files=[]
 for p in sorted(REPORT.rglob('*')):
  if p.is_file(): files.append(dict(path=c.rel(p),sha256=c.sha(p),role='source' if p.suffix in ('.py','.tcl','.sv','.v','.xdc') else 'log' if p.suffix in ('.log','.rpt','.vds','.jou') else 'result'))
 files += [dict(path=r['path'],sha256=r['sha256'],role='input') for r in prepared['dependencies']]
 for record in (before,after):
  for r in record['source_files']:
   if (ROOT/r['snapshot']).is_relative_to(ROOT/'report') and r['snapshot'] not in {f['path'] for f in files}: files.append(dict(path=r['snapshot'],sha256=r['sha256'],role='source'))
 checks=[dict(name='原生PNR：'+r['label'],status='PASS' if r['history']['code']==0 else 'FAIL',command=r['history']['command'],exit_code=r['history']['code'],reason='真实history码；不代表STA或独立G2批准。') for r in paired]
 inherited=next(r for r in c.read(SYNTH)['checks'] if r['name']=='50MHz综合态STA分类')
 checks += [dict(name='实际全程预算覆盖',status='BLOCKED',command=None,exit_code=None,reason='需独立Reviewer核对ROOT监督消费、样本/缺测与归属。'),dict(name='继承S15综合STA',status=inherited['status'],command=inherited['command'],exit_code=inherited['exit_code'],reason='继承本轮真实综合STA状态，不由包装0关闭。')]
 if classifier: checks.append(dict(name='实际PNR STA数值分类',status='PASS' if classifier['native_exit_code']==0 else 'FAIL',command=classifier['windows_command'],exit_code=classifier['native_exit_code'],reason=sta['status']+'；原生分类不替代独立时序关闭审查。'))
 else: checks.append(dict(name='实际PNR STA',status='BLOCKED',command=None,exit_code=None,reason='没有实际报告，不补综合旧值。'))
 for name in ('独立PNR证据审查','bit/runtime/G3/109/1000'): checks.append(dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason='整理器不授予批准。'))
 manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17',run_id=REPORT.name,source_commit=COMMIT,evidence_dir=c.rel(REPORT),interfaces=interfaces,files=files,checks=checks,tool_versions=dict(python=sys.version,profile=freeze['profile'],Vivado='实际原件保留，不执行新查询'),limitations=['实际PNR时序只在pnr_closed_binding中从实际报告解析；独立审查前不宣称关闭。','源码基线与证据提交分别记录；准备期HEAD未冻结，不用旧证据HEAD替代本轮源码基线。'])
 for r in initial: c.require(c.binding(ROOT/r['path'])==r,'ROOT初始原件在整理时漂移')
 save(REPORT/'delivery_manifest.json',manifest); print(json.dumps(dict(status='COLLECTED_PNR_PENDING_INDEPENDENT_REVIEW',manifest=c.binding(REPORT/'delivery_manifest.json')),ensure_ascii=False))
def main():
 """prepare与collect分离，未释放关闭门禁时不触碰报告目录。"""
 parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=('prepare','collect','classify')); parser.add_argument('--gate',type=Path); parser.add_argument('--report',type=Path); parser.add_argument('--result',type=Path); parser.add_argument('--receipt',default='prepared_receipt.json')
 args=parser.parse_args()
 if args.mode=='prepare': return prepare(args.receipt)
 if args.mode=='classify':
  c.require(args.report is not None and args.result is not None,'分类必须真实报告与新结果')
  start=time.monotonic()
  try: result=timing(c.exact(args.report).read_text(encoding='utf-8')); code=2 if result['status']=='FAIL_TIMING' else 0
  except (ValueError,OSError,UnicodeError,IndexError) as error: result=dict(status='FAIL_CLASSIFIER_INPUT',error=repr(error)); code=3
  result.update(native_exit_code=code,elapsed_seconds=time.monotonic()-start,report=c.binding(args.report)); save(args.result,result); print(json.dumps(result,ensure_ascii=False)); return code
 c.require(args.gate is not None,'必须传入ROOT真实关闭门禁'); return collect(args.gate)
if __name__=='__main__': raise SystemExit(main())
