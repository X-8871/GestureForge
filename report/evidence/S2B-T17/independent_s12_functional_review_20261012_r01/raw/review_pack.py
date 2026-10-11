"""独立复核冻结交付原件、真实来源稳定性和受控TB诊断。"""
import json,hashlib,re,time,ctypes,sys
from pathlib import Path
ROOT=Path.cwd();MAIN=ROOT/'report/evidence/S2B-T17/s12_timing_cones_20261012_r01';OUT=ROOT/'tmp/2B/S2B-T17/independent_s12_functional_review_20261012_r01'
start=time.monotonic();checks=[];bindings=[];diagnostic_corrections=[]
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def check(ok,name,detail=None):
 assert ok,(name,detail)
 checks.append(dict(name=name,result='PASS',detail=detail))
def bind(path,expected):
 p=ROOT/path;check(p.is_file() and sha(p)==expected,'RAW绑定 '+str(path));bindings.append(dict(path=str(p),sha256=expected))
manifest=read(MAIN/'delivery_manifest_r02.json');old=read(MAIN/'delivery_manifest.json');summary=read(MAIN/'g1_summary.json');freeze=read(MAIN/'source_freeze.json')
bind(MAIN/'delivery_manifest_r02.json','2c8e3bd56c1c288333f168a767aadf8b7067f2450e97c25709f271553772ed54')
check(len(manifest['files'])==731,'731最终绑定数量')
for f in manifest['files']:bind(f['path'],f['sha256'])
for f in manifest['interfaces']:bind(f['path'],f['sha256'])
check(manifest['interfaces'][1]['frozen'] is False,'物理候选尚未冻结')
bind(MAIN/'delivery_manifest.json','e9a32360e12c2f80aa91189d2b353e6b4dd2e58a3efee864e0eecfd34488103d')
for run in summary['runs']:
 value=manifest['tool_versions'][run['stage']];check(isinstance(value,str) and value and json.loads(value)==old['tool_versions'][run['stage']],'九实际工具版本JSON往返 '+run['stage'])
check(manifest['source_commit']==freeze['source_commit']==summary['source_commit']=='891f750045ce141a8152c96025da559ff1d3a321','基线891角色保持')
restore_count=0
for mp in (MAIN/'raw_restore_mapping.json',MAIN/'manifest_schema_repair_r01/raw_restore_mapping.json'):
 for row in read(mp):
  archive=row.get('archived_path',row.get('restored_path'));original=row['original_path'];expected=row['sha256']
  bind(archive,expected);check((ROOT/archive).stat().st_size==row['bytes'],'恢复长度 '+str(archive))
  check((ROOT/original).is_file() and sha(ROOT/original)==expected,'恢复原件关系 '+str(original));restore_count+=1
check(restore_count>0,'恢复映射逐原件核验数量',restore_count)
source_final={e['path']:e['sha256'] for e in freeze['source_files']}
native_records=[];diagnostics=[]
for run in summary['runs']:
 stage=run['stage'];v=read(ROOT/run['validation_path']);n=read(ROOT/run['native_path'])
 check(v['source_sha256_pre']==v['source_sha256_post'],'inner来源稳定 '+stage,len(v['source_sha256_pre']))
 check(n['source_pre']==n['source_post'] and n['source_stable'] is True and len(n['source_pre'])==43,'outer43来源稳定 '+stage)
 check(n['native_returncode']==0 and n['supervisor_stop'] is None,'原生执行无监督终止 '+stage)
 drifts={p:dict(tested=h,final=source_final[p]) for p,h in n['source_pre'].items() if h!=source_final[p]}
 check(drifts==({ 'verification/test_s2b_conv_validation_rtl.py': {'tested':'d8bac010c08c01b4bf466405c8140cb9735aed769819da966131ae9e049e926c','final':'cdf680a67d7bf08407ee3a3993d62032ff33b1aa468d483600861fa217965c2d'}} if stage=='pool' else {}),'跨run漂移显式限定 '+stage,drifts)
 for p,h in v['source_sha256_pre'].items():check(h==n['source_pre'][p],'inner实际闭包来自outer '+stage+'/'+p)
 native_records.append(dict(stage=stage,native_returncode=n['native_returncode'],inner=len(v['source_sha256_pre']),outer=len(n['source_pre']),elapsed=n['elapsed_seconds'],peak=n['sampled_tree_peak_rss_bytes']))
 rdir=(ROOT/run['validation_path']).parent
 for exe in run['runs']:
  if 'compile' not in exe['name'] and 'lint' not in exe['name']:continue
  log=(ROOT/exe['log']).read_text(encoding='utf-8')
  check(not re.search(r'%Warning-(LATCH|UNOPTFLAT):',log),'禁新组合诊断 '+stage+'/'+exe['name'])
  blocks=re.split(r'(?=%Warning-)',log)
  md=[b for b in blocks if b.startswith('%Warning-MULTIDRIVEN:')]
  for block in md:
   signal=re.search(r"other process.*?: '(\w+)'",block)
   if not signal:signal=re.search(r"driven.*?: '(\w+)'",block,re.I)
   instance=re.search(r"In instance '[^']*\.(\w+)'",block)
   loc=re.findall(r'(tb_[^\s:]+\.sv):(\d+)(?::\d+)?: .*Location of other write',block)
   check(bool(signal and instance and loc),'MULTIDRIVEN可定位 '+stage+'/'+exe['name'])
   tbname,line=loc[0];sig=signal[1];inst=instance[1];p=rdir/tbname
   check(p.is_file(),'TB原件存在 '+str(p))
   lines=p.read_text(encoding='utf-8').splitlines();actual=lines[int(line)-1]
   target=re.escape(inst)+r'\.'+re.escape(sig)
   assignment=re.search(r'\b'+target+r'(?:\s*\[.*?\])?\s*=',actual)
   casting=re.search(r'\$cast\(\s*'+target+r'\s*,',actual)
   releasing=re.search(r'\brelease\s+'+target+r'\s*;',actual)
   if releasing:
    force_lines=[i+1 for i,l in enumerate(lines) if re.search(r'\bforce\s+'+target+r'\s*=',l)]
    check(bool(force_lines),'TB release对应真实force '+stage+'/'+inst+'.'+sig,force_lines)
   if not assignment and not casting and not releasing:
    generic_target=r'\bu_generic\.'+re.escape(sig)+r'(?:\s*\[.*?\])?\s*='
    check(stage=='cones' and inst=='u_private' and re.search(generic_target,actual),'仅cones工具private来源定位合并错配',dict(stage=stage,instance=inst,signal=sig,line=line,actual=actual))
    cast_lines=[i+1 for i,l in enumerate(lines) if re.search(r'\$cast\(\s*'+target+r'\s*,',l) or re.search(r'\b'+target+r'(?:\s*\[.*?\])?\s*=',l)]
    if sig=='state':check(cast_lines==[1985,1989,1993,1997,2001],'实际private五处cast写入')
    else:check(len(cast_lines)==1,'实际private唯一TB写入 '+sig,cast_lines)
    check('logic clk=0' in '\n'.join(lines) or 'logic clk = 0' in '\n'.join(lines),'cones时钟恒0')
    diagnostic_corrections.append(dict(stage=stage,execution=exe['name'],signal=sig,raw_reported_instance=inst,raw_reported_otherwrite_line=int(line),raw_reported_otherwrite_instance='u_generic',actual_instance=inst,actual_write_lines=cast_lines,scope='仅二态组合域TB；生产源未豁免，原工具及原登记错配保存。'))
   else:check(True,'MULTIDRIVEN实际TB写入 '+stage+'/'+inst+'.'+sig,dict(tb=str(p),line=int(line),text=actual))
   production=re.search(r'%Warning-MULTIDRIVEN:\s+([^\s:]+\.sv):(\d+):',block)
   check(production is not None,'MULTIDRIVEN生产位置可定位')
   source_name=production[1].replace('\\','/').split('/')[-1]
   candidates=[rdir/source_name,rdir/'source_snapshot/src'/source_name,rdir/'source_snapshot'/source_name]
   candidates.extend(ROOT/e['snapshot'] for e in freeze['source_files'] if Path(e['path']).name==source_name)
   available=[q for q in candidates if q.is_file()];check(bool(available),'诊断源原件存在 '+source_name)
   pline=available[0].read_text(encoding='utf-8').splitlines()[int(production[2])-1]
   check(re.search(r'\b'+re.escape(sig)+r'\b',pline) is not None,'诊断源行及signal相符 '+source_name+'/'+sig)
   diagnostics.append(dict(stage=stage,execution=exe['name'],instance=inst,signal=sig,tb=str(p),raw_otherwrite_line=int(line),source=str(available[0]),source_line=int(production[2])))
  if stage=='cones':
   declared=v['controlled_multidriven_diagnostics'][exe['name']]
   check(len(md)==len(declared),'cones诊断登记未漏项 '+exe['name'],len(md))
   for d in declared:
    check(d['raw'] in log and d['tb_drivers'],'cones登记真实raw/'+exe['name'])
check(len(diagnostics)>0,'全部受控MD逐条TB验证',len(diagnostics))
rq=MAIN/'requant_narrow_review_raw/final_review_receipt.json';rqreceipt=read(rq)
check(rqreceipt['status']=='PASS' and rqreceipt['reviewer_stop']=='STOP_NO_FURTHER_WRITES','REQUANT独审STOP范围')
rqmanifest=ROOT/'report/evidence/S2B-T17/s12_requant_rtl_20261012_r01/delivery_manifest_r02.json';bind(rqmanifest,'00358f98fe4d2584b5a0d2275fc3f9249b7caeb8d06229145234dc53392fca2d')
for f in read(rqmanifest)['files']:bind(f['path'],f['sha256'])
check(rqreceipt['reviewed_source_hashes']['src/s2b_conv_tile_engine.sv']==source_final['src/s2b_conv_tile_engine.sv'],'REQUANT当前候选RAW一致')
check(rqreceipt['independent_integer_vectors']==138791 and rqreceipt['semantic_rtl_mutant_counts']==[2080,10649,490,11210,12378,44710,9914] and rqreceipt['actual_rtl_compile_native_exit_code']==rqreceipt['actual_rtl_simulation_native_exit_code']==0,'REQUANT真实数值及七RTL变体范围')
check(any('256bit' in c['name'] and c['passed'] for c in rqreceipt['checks']) and any('商余数' in c['name'] and c['passed'] for c in rqreceipt['checks']),'REQUANT独立商余数方法')
repair=ROOT/'tmp/2B/S2B-T17/s12_remaining_prepare_20261012_r01/delivery_repair_capture_r01/native_receipt.json';bind(repair,'a8db24ed7e1e1a36e3a530c391fd64fa98ecde75e4fe006c457378ec146d1e23')
print('REPAIR',read(repair))
receipt=dict(status='PASS_FROZEN_PACK_AND_RAW_CHECKS',checks=checks,bindings=bindings,restore_original_checks=restore_count,diagnostics=diagnostics,diagnostic_corrections=diagnostic_corrections,native_records=native_records,requant_scope=rqreceipt['scope'],seconds=time.monotonic()-start,python=sys.version,argv=sys.argv,limitations=['仅原始绑定与数学/契约功能审查；CHECKS_OK不代表STA/G3。','原生日志的真实执行由原receipt绑定，本独审未新编译或重跑大型仿真。','cones u_private原工具otherwrite和原登记定位为u_generic，独审按全部实际private写入补核；state另核五处cast，原错配保留。'])
(OUT/'pack_raw_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=receipt['status'],checks=len(checks),bindings=len(bindings),restore=restore_count,controlled_multidriven=len(diagnostics),seconds=receipt['seconds']),ensure_ascii=False))
