"""独立只读核对S13失败封包；只读取冻结快照和本轮必要原件。"""
import ast, hashlib, json, re, subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import psutil
OUT=Path(__file__).absolute().parent; ROOT=OUT.parents[3]
C=ROOT/'report/evidence/S2B-T17/s13_root_closure_20261012_r01'
P=ROOT/'report/evidence/S2B-T17/s13_platform_20261012_r01'
B=P/'mcp_closed'; PRE=ROOT/'report/evidence/S2B-T17/s13_source_preflight_20261012_r01'
SOURCE='701dc55af0c53a959e84dc0c470f136918f5bd50'
issues=[]; checks=[]; commands=[]; detail={}
def check(ok,name):
 checks.append({'name':name,'ok':bool(ok)})
 if not ok: issues.append(name)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def file(row):
 p=Path(row['path']); p=p if p.is_absolute() else ROOT/p
 check(p.is_file(), '文件存在:'+row['path'])
 if not p.is_file(): return
 raw=p.read_bytes(); check(sha(raw)==row['sha256'],'文件SHA:'+row['path'])
 if 'bytes' in row: check(len(raw)==row['bytes'],'文件字节:'+row['path'])
def native(label,command,input_raw=None):
 start=time.monotonic(); child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.PIPE if input_raw else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 try: birth=psutil.Process(child.pid).create_time()
 except psutil.Error: birth=None
 stdout,stderr=child.communicate(input_raw)
 (OUT/(label+'.stdout.bin')).write_bytes(stdout); (OUT/(label+'.stderr.bin')).write_bytes(stderr)
 commands.append({'label':label,'command':command,'pid':child.pid,'birth':birth,'wait_return':child.returncode,'elapsed_seconds':time.monotonic()-start,'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr),'internal_child_identity':'UNKNOWN'})
 return child.returncode,stdout
m=C/'delivery_manifest_r03.json'; manifest=read(m)
check(sha(m.read_bytes())=='3de5a79ba3395456b8c4e305f03869ac88369f007e34725104acc3e475706bb0','当前r03清单SHA')
check(manifest['source_commit']==SOURCE and len(manifest['files'])==400,'清单版本及400绑定')
check(len({r['path'] for r in manifest['files']})==400,'清单路径唯一')
for row in manifest['files']: file(row)
for row in manifest['interfaces']: file(row)
mapping=read(C/'archive_mapping.json')['files']; check(len(mapping)==33,'33归档映射')
for row in mapping:
 file(row['original']); file(row['saved']); check(row['original']['sha256']==row['saved']['sha256'],'归档原字节同SHA')
runtime=read(C/'runtime_snapshot_mapping.json')
for row in runtime:
 file(row['original']); file(row['saved']); check(row['original']['sha256']==row['saved']['sha256'],'运行流原字节同SHA')
summary=read(P/'s12_collection_summary.json'); nm=read(P/'s12_native_mapping.json'); sb=read(P/'s12_source_binding.json'); mb=read(P/'s12_mcp_binding.json')
for rows in [summary['closed_input_mapping'],nm['files']]:
 for row in rows:
  for key in ['original_path','saved_path']: file({'path':row[key],'sha256':row['sha256'],'bytes':row['bytes']})
for row in summary['original_raw_inventory']: file(row)
check(len(summary['closed_input_mapping'])==98 and len(nm['files'])==100,'98闭合原件及100native映射')
before=read(PRE/'source_before.json'); after=read(PRE/'source_after.json'); freeze=read(C/'source_freeze_r01.json')
check(before['source_commit']==after['source_commit']==freeze['source_commit']==SOURCE,'before/after/freeze来源')
check(before['source_sha256']==after['source_sha256']=={r['path']:r['sha256'] for r in freeze['source_files']},'前后44源哈希相同')
check(len(before['source_files'])==len(after['source_files'])==44 and len(before['static_source_sha256'])==33,'44源33静态集合')
check(before['static_source_sha256']==freeze['static_source_sha256']==read(B/'static_actual_closed.json')['source_sha256'],'静态实际闭合集合')
for snapshot in [before,after]:
 for row in snapshot['source_files']: file({'path':row['snapshot'],'sha256':row['sha256'],'bytes':row['bytes']})
check(before['frozen14_sha256']==freeze['frozen14']==sb['frozen14'] and len(freeze['frozen14'])==14,'原14冻结一致')
tree=ast.parse((PRE/'source_snapshot/verification/check_s2b_inference_platform.py').read_text(encoding='utf-8'))
fixed=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='FROZEN_CORE_SHA256' for t in n.targets))
check(fixed==freeze['frozen14'],'固定检查器原14常量独立AST读回')
for path,h in freeze['frozen14'].items(): check(before['source_sha256'][path]==h,'原14实际快照:'+path)
check(len(freeze['active_rtl_sources'])==18 and set(freeze['active_rtl_sources'])==set(nm['compiled_rtl'])==set(sb['compiled_rtl']),'18实际compiled与冻结集合')
check(before['profile_version']=='s2b-inference-platform/0.1.13' and before['clock_hz']==50000000 and before['visibility_parameter']==0 and freeze['tcl_builder_namespace_version']=='0.1.12','profile/时钟/visibility及实际Tcl版本')
check(sum(p.startswith('src/s2b_') for p in freeze['active_rtl_sources'])==12,'实际12个s2b活动RTL')
git=Path('C:/Program Files/Git/cmd/git.exe'); check(git.is_file(),'精确Git程序')
rc,raw=native('git44_batch',[str(git),'-c','core.longpaths=true','-c','maintenance.auto=false','cat-file','--batch'],''.join(SOURCE+':'+r['path']+'\n' for r in before['source_files']).encode('utf-8'))
check(rc==0,'批量Git实际wait0'); pos=0; raw_count=0; eol_count=0
for row in before['source_files']:
 end=raw.index(b'\n',pos); header=raw[pos:end].split(); size=int(header[2]); blob=raw[end+1:end+1+size]; pos=end+size+2
 check(header[1]==b'blob' and sha(blob)==row['git_blob_sha256'],'Git对象实际SHA:'+row['path'])
 snapshot=(ROOT/row['snapshot']).read_bytes()
 if snapshot==blob: raw_count+=1; check(row['git_relation']=='RAW_IDENTICAL','RAW relation:'+row['path'])
 else: eol_count+=1; check(b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==snapshot and row['git_relation']=='GIT_LF_TO_RAW_CRLF','精确EOL relation:'+row['path'])
check(pos==len(raw) and (raw_count,eol_count)==(38,6),'Git38RAW+6精确EOL')
timing=(P/'timing_summary_synth.rpt').read_text(encoding='utf-8'); nums=re.search(r'^\s*(-2\.453)\s+(-137\.746)\s+(102)\s+(14702)\s+(0\.037)\s+(0\.000)\s+(0)\s+(14702)\s+(8\.870)\s+(0\.000)\s+(0)\s+(4193)\s*$',timing,re.M)
check(nums is not None,'原报告完整时序统计行')
check('Synthesized' in timing and '-2  PRODUCTION 1.12 2019-11-22' in timing and re.search(r'clk_fpga_0\s+\{0\.000 10\.000\}\s+20\.000\s+50\.000',timing) is not None,'综合态-2及50MHz实际报告')
util=(P/'utilization_synth.rpt').read_text(encoding='utf-8'); top=next(l for l in util.splitlines() if '| s2b_inference_wrapper ' in l); cells=[x.strip() for x in top.split('|')][1:-1]
check([int(x) for x in cells[2:]]==[21732,21635,96,1,4030,32,0,144],'实际层级top资源')
check(summary['resources']=={'lut':21732.0,'ff':4030.0,'bram':32.0,'dsp':144.0,'latch':0.0} and summary['timing']['status']=='FAIL_TIMING','资源及STA失败分类未提高范围')
check(summary['sta_native_exit_code']==2 and summary['implementation']==summary['postroute']==summary['hardware']=='NOT_RUN','STA2及PNR硬件未执行')
constraints=(P/'constraints_synth.xdc').read_text(encoding='utf-8') if (P/'constraints_synth.xdc').is_file() else None
check(constraints is not None and constraints.count('set_false_path -to')==2 and 'create_clock -period 20.000 -name clk_fpga_0' in constraints and 'ACTIVE_HIGH_AUX.ACT_HI_AUX' in constraints and 'ACTIVE_LOW_EXT.ACT_LO_EXT' in constraints,'50MHz及两reset falsepath导出原件')
check('No valid timing exceptions found' in (P/'exceptions_synth.rpt').read_text(encoding='utf-8'),'actual有效exceptions为空与导出两reset路径分列')
detail['constraint_files']=[r['path'] for r in manifest['files'] if 'constraint' in r['path'] or 'exception' in r['path']]
history=read(B/'history.tool.json'); history=json.loads(history['content'][0]['text'])['history']; paired=mb['paired_calls']
check(len(history)==len(paired)==9 and len({r['id'] for r in history})==9,'九真实历史调用唯一')
for row in paired:
 h=row['native_history']; check(h==next(x for x in history if x['id']==h['id']),'native history原件:'+row['label']); file(row['client_record'])
 client=read(ROOT/row['client_record']['path']); check(client['input']['command']==h['command'],'客户端命令等于history:'+row['label'])
wait=next(x for x in history if x['command']=='wait_on_run synth_1'); client=read(B/'wait.tool.json')
check(wait['code']==0 and wait['elapsed']==625.116 and client['result']['isError'] is True and 'after 300s' in client['result']['content'][0]['text'] and 'exit_code' not in client['result'],'WAIT客户端300s错误与native0/625.116分列')
check(sum(x['command']=='launch_runs synth_1 -jobs 1' for x in history)==1 and sum(x['command']=='wait_on_run synth_1' for x in history)==1,'唯一launch/wait')
check([x['code'] for x in history]==[0,1,0,0,0,0,0,0,0],'九native控制码含products capture1')
products=(P/'products.tcldict').read_text(encoding='utf-8'); check('status FAIL code 0 raw PRODUCTS:OK' in products and 'WARNING 9' in products and 'WARNING 1' in products and 'capture_error {CAPTURE_FAIL:' in products,'products原生0 capture1及计数倒退原件')
check(summary['products_native_exit_code']==0 and summary['products_capture_exit_code']==1 and mb['products_repeated'] is False,'products不重跑及双码')
logs=[]
for job in nm['jobs']:
 rows=[r for r in nm['files'] if Path(r['original_path']).name=='runme.log' and Path(r['original_path']).parent.name==job['run']]
 check(len(rows)==1,'真实run目录映射唯一:'+job['run']); d=(ROOT/rows[0]['saved_path']).parent; log=(d/'runme.log').read_text(encoding='utf-8',errors='replace'); logs.append(log)
 check((d/'.vivado.end.rst').is_file() and not (d/'.vivado.error.rst').exists() and 'synth_design completed successfully' in log,'任务真实日志和end marker:'+job['run'])
 check(job['raw_os_process_exit_code'] is None and job['process_tree_peak_memory_bytes'] is None and job['final_diagnostics']['errors']==0,'原生任务未知OS码/树峰不补0:'+job['run'])
infer_tcl=next(r for r in nm['files'] if Path(r['saved_path']).name=='s2b_inference_infer_0.tcl')
tcl=(ROOT/infer_tcl['saved_path']).read_text(encoding='utf-8'); rtlblock=re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\}',tcl,re.S).group(1)
actual_rtl=[p.strip().split('/FPGA_Competition/')[1] for p in rtlblock.splitlines() if p.strip()]
check(actual_rtl==nm['compiled_rtl'],'实际执行Tcl read_verilog精确18列表')
for source in nm['compiled_rtl']:
 check(Path(source).name in '\n'.join(logs) or source=='src/s2a_network_descriptor_pkg.sv' and source in actual_rtl,'native日志或已执行Tcl package:'+source)
check(not re.search(r'\binferred latch\b', '\n'.join(logs),re.I),'native日志无推断latch文本')
guards=[]
for i in range(1,5):
 guard=read(B/f'supervision_r0{i}_guard_guard_receipt.json'); sup=read(B/f'supervision_r0{i}_supervisor_receipt.json'); cons=read(B/f'native_consumer_r0{i}_consumer_receipt.json')
 check(guard['status']=='BLOCKED' and sup['child_native_exit_code']==3,'r0'+str(i)+'实际guard BLOCKED/native3')
 check(cons['native_exit_code']==2 and cons['status']=='BLOCKED_RUNTIME_MONITOR','r0'+str(i)+'consumer实际终态2')
 guards.append({'round':i,'guard_status':guard['status'],'reason':guard['reason'],'at_utc8':guard['at_utc8'],'consumer_status':cons.get('status'),'consumer_exit_code':cons.get('native_exit_code'),'sampled_peak_tree_rss_bytes':guard['sampled_peak_tree_rss_bytes']})
 check(guard['limits']=={'tree_rss_bytes':6442450944,'available_ram_bytes':536870912,'c_disk_free_bytes':8589934592},'r0'+str(i)+'原运行阈值')
check(read(B/'r04_runtime_activation.json')['status']=='R04_CURRENT_LIVE_READY_REPORT_CLOSE_ONLY','r04明确仅reports/close')
native_codes={}
for prefix,expected in [('s13_prepare_r01',0),('s13_source_before_r01',0),('s13_source_after_r01',0),('s13_collect_r01',1),('s13_collect_r02',0)]:
 rec=read(C/(prefix+'.native.json')); native_codes[prefix]=rec['native_exit_code']; check(rec['native_exit_code']==expected and rec['direct_child_wait_returned'] is True,'实际native等待:'+prefix)
 file(rec['stdout']); file(rec['stderr']); check(isinstance(rec['direct_child_identity']['pid'],int) and isinstance(rec['direct_child_identity']['create_time'],(float,int)),'实际child PID/birth:'+prefix)
testnames={r['name']:r for r in manifest['checks']}; check(testnames['连续资源监护']['status']=='BLOCKED' and testnames['旧seal入口']['status']=='NOT_RUN','清单保留监护BLOCKED及seal未运行')
check(json.loads(read(B/'stop.tool.json')['content'][0]['text'])['status']=='success','真实Vivado关闭返回')
try:
 proc=psutil.Process(24504); status='PID_REUSED' if proc.create_time()!=1791771659.354538 else 'SAME_INSTANCE_LIVE'
except psutil.NoSuchProcess: status='ABSENT'
except psutil.Error as exc: status='UNKNOWN:'+type(exc).__name__
check(status in ('ABSENT','PID_REUSED'),'唯一owned旧实例已不存在')
detail.update({'manifest_sha256':sha(m.read_bytes()),'source_commit':SOURCE,'source_snapshots':44,'git_raw':raw_count,'git_exact_eol':eol_count,'archive_mappings':len(mapping),'runtime_mappings':len(runtime),'closed_mappings':98,'native_mappings':100,'guards':guards,'native_codes':native_codes,'owned_old_instance':status,'history':[{'id':x['id'],'code':x['code'],'elapsed':x['elapsed'],'command':x['command'][:160]} for x in history]})
result={'status':'PASS_INDEPENDENT_AUDIT' if not issues else 'CHANGES_REQUIRED','at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks':checks,'issues':issues,'detail':detail,'native_commands':commands}
(OUT/'audit_result_r02.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'issues':issues,'detail':detail},ensure_ascii=False)); sys.exit(1 if issues else 0)
