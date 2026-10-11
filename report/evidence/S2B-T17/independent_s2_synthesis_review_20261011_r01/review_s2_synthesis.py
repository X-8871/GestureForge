"""只读独立核对S2综合证据；不读取变化中的S3工程源，不运行Vivado。"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,time,zipfile,tkinter
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parent;R=W.parents[3];P=R/'report/evidence/S2B-T17/s2_platform_20261011_r01';Q=R/'report/evidence/S2B-T17/s2_source_preflight_20261011_r01'
BASE='5a676b700af4c27297977379417b1694dd64840e';MANIFEST=P/'collection_fix_delivery_manifest_r04.json';started=time.monotonic()
report={'status':'CHANGES_REQUIRED','checks':[],'commands':[],'reviewed_source_commit':BASE,'scope':'仅S2固定source_before/after/snapshot、Git5a、最终671冻结源及实际已关闭原件；不读当前S3 RTL。','issues':[]}
def sha(p):
    """流式原字节hash。"""
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):
    """拒绝重复JSON键。"""
    def unique(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('重复键 '+k)
            d[k]=v
        return d
    return json.loads(p.read_text(encoding='utf-8'),object_pairs_hook=unique)
def check(name,good):
    """保存实际核查结果。"""
    report['checks'].append({'name':name,'passed':bool(good)})
    if not good:raise AssertionError(name)
def native(name,command,expected):
    """保存关闭后的原生stdout/stderr，绑定原生退出而非外层Shell。"""
    out=W/(name+'.stdout.log');err=W/(name+'.stderr.log');t=time.monotonic()
    with out.open('x',encoding='utf-8') as o,err.open('x',encoding='utf-8') as e:p=subprocess.run(command,cwd=R,stdout=o,stderr=e,timeout=120)
    report['commands'].append({'name':name,'command':command,'native_exit_code':p.returncode,'seconds':time.monotonic()-t,'stdout':out.relative_to(R).as_posix(),'stdout_sha256':sha(out),'stderr':err.relative_to(R).as_posix(),'stderr_sha256':sha(err),'peak_rss':'NOT_MEASURED'})
    check('原生命令 '+name,p.returncode==expected)
try:
    check('正式manifest固定SHA',sha(MANIFEST)=='21cb291264a6875e63ed75a9760802c700223d51846ddc0610b6aeccfe25d4a5')
    m=read(MANIFEST);check('193绑定',len(m['files'])==191 and len(m['interfaces'])==2 and len({x['path'] for x in m['files']})==191)
    for row in m['files']+m['interfaces']:
        p=R/row['path'];check('清单实际原字节 '+row['path'],p.is_file() and sha(p)==row['sha256'])
    report['manifest_sha256']=sha(MANIFEST);report['manifest_files']=191;report['interface_bindings']=2
    before=read(Q/'source_before.json');after=read(P/'source_after.json')
    check('28源码before/after同字节绑定',before['source_commit']==after['source_commit_at_build_start']==after['source_commit_at_check']==BASE and before['sources']==after['sources'] and len(before['sources'])==28)
    check('profile0.1.2/visibility0',before['platform_version']==after['platform_version']=='0.1.2' and before['visibility']==after['visibility']==0)
    source_rows=[]
    for row in before['sources']:
        p=Q/'source_snapshot'/row['path'];raw=p.read_bytes();blob=subprocess.check_output(['git','show',BASE+':'+row['path']],cwd=R)
        equal=raw==blob;crlf=not equal and b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw
        check('固定快照/Git '+row['path'],sha(p)==row['sha256'] and len(raw)==row['bytes'] and (equal or crlf))
        source_rows.append({**row,'snapshot_path':p.relative_to(R).as_posix(),'git_blob_sha256':hashlib.sha256(blob).hexdigest(),'git_raw_equal':equal,'exact_git_lf_to_snapshot_crlf':crlf,'git_native_exit_code':0})
    report['sources']=source_rows;check('24 raw同/4精确EOL',sum(x['git_raw_equal'] for x in source_rows)==24 and sum(x['exact_git_lf_to_snapshot_crlf'] for x in source_rows)==4)
    profile=read(Q/'source_snapshot/board/s2b_inference_platform.json');check('18实际源码闭包/物理候选未改变',len(profile['rtl_sources'])==18 and len(set(profile['rtl_sources']))==18 and profile['version']=='s2b-inference-platform/0.1.2' and profile['physical_interface']=='s2b-physical-candidate/0.1.1' and profile['clock_hz']==50000000 and profile['visibility_default']==0)
    frozen=[]
    for row in profile['source_derivation']['upstream_sources']:
        p=Q/'source_snapshot'/row['path'];blob=subprocess.check_output(['git','show','671f9cf494b92ce182b3f1542fefd0cfd4b209f5:'+row['path']],cwd=R);raw=p.read_bytes()
        check('最终671原14 '+row['path'],sha(p)==row['sha256'] and (raw==blob or (b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==raw)))
        frozen.append({**row,'git_blob_sha256':hashlib.sha256(blob).hexdigest()})
    check('原14完整',len(frozen)==14);report['frozen14']=frozen
    relocation=read(P/'collection_fix_native_relocation.json');oldroot=Path(relocation['source']);newroot=Path(relocation['target'])
    check('获批目录名称及9原件',oldroot.name=='synth_1' and newroot.name=='wrapper_native_s2_r01' and not oldroot.exists() and newroot.is_dir() and len(relocation['files'])==9)
    maps={}
    for row in relocation['files']:
        old=Path(row['old_path']);new=Path(row['new_path']);check('迁移原字节 '+row['internal_path'],old.relative_to(oldroot)==new.relative_to(newroot)==Path(row['internal_path']) and sha(new)==row['sha256'] and new.stat().st_size==row['bytes']);maps[old.relative_to(R).as_posix()]=new.relative_to(R).as_posix()
    original=read(P/'collection_fix_original_inventory.json')['files'];recheck=read(P/'collection_fix_original_recheck.json');check('146/137/9分类',len(original)==len(recheck['files'])==146 and recheck['path_unchanged_count']==137 and recheck['path_moved_count']==9 and recheck['raw_bytes_all_unchanged'])
    for row in original:
        actual=R/maps.get(row['path'],row['path']);check('原146实际不转码 '+row['path'],sha(actual)==row['sha256'] and actual.stat().st_size==row['bytes'])
    for row in recheck['files']:check('recheck映射闭合 '+row['original_path'],row['current_path']==maps.get(row['original_path'],row['original_path']) and sha(R/row['current_path'])==row['sha256'])
    report['native_relocation']={'original146':146,'unchanged_paths':137,'moved_paths':9,'mapping_sha256':sha(P/'collection_fix_native_relocation.json')}
    mapping=read(P/'collector_native_mapping.json');check('5job/44必要原件',len(mapping['jobs'])==5 and len(mapping['files'])==44)
    for row in mapping['files']:
        saved=R/maps.get(row['saved_path'],row['saved_path']);check('native复制原件 '+row['saved_path'],sha(saved)==row['sha256'] and saved.stat().st_size==row['bytes'])
    jobs=[]
    for job in mapping['jobs']:
        directory=P/'native_jobs'/('wrapper_native_s2_r01' if job['run']=='synth_1' else job['run']);raw=(directory/'runme.log').read_bytes();text=raw.decode('utf-8',errors='replace')
        check('job完成markers '+job['run'],(directory/'.vivado.begin.rst').is_file() and (directory/'.vivado.end.rst').is_file() and (directory/'__synthesis_is_complete__').is_file() and not (directory/'.vivado.error.rst').exists() and 'synth_design completed successfully' in text)
        peaks=[float(x) for x in re.findall(r'Memory \(MB\): peak = ([\d.]+)',text)];check('单job峰值来源 '+job['run'],max(peaks)==job['reported_single_process_peak_mb'] and job['raw_process_exit_code'] is None)
        jobs.append({'run':job['run'],'reported_single_process_peak_mb':max(peaks),'observed_os_exit_code':None,'runme_sha256':sha(directory/'runme.log')})
    report['jobs']=jobs
    infer=P/'native_jobs/s2b_inference_infer_0_synth_1';tcl=(infer/'s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
    block=re.search(r'read_verilog -library xil_defaultlib -sv \{(.*?)\}',tcl,re.S);paths=[Path(x).relative_to(R).as_posix() for x in block.group(1).split()]
    check('真实compiled18 SV闭包',len(paths)==18 and len(set(paths))==18 and set(paths)==set(profile['rtl_sources'])==set(mapping['actual_rtl_sources']))
    check('真实infer top与speed-2','synth_design -top s2b_inference_infer_0 -part xc7z020clg400-2' in tcl)
    ilog=(infer/'runme.log').read_bytes().decode('utf-8',errors='replace')
    for module in ('s2b_network_backend','s2b_maxpool_engine','s2a_route_engine','s2b_upsample_engine','s2a_conv_tile_engine','s2b_stage2b_core'):check('实际完整模块 '+module,"synthesizing module '"+module+"'" in ilog)
    wrapper=(P/'native_jobs/wrapper_native_s2_r01/runme.log').read_bytes().decode('utf-8',errors='replace')
    wrapper_paths=re.findall(r"synthesizing module 's2b_inference_wrapper' \[([^\]]+):\d+\]",wrapper)
    check('唯一import wrapper',len(wrapper_paths)==1 and '/imports/hdl/s2b_inference_wrapper.v' in wrapper_paths[0])
    report['compiled_rtl_sources']=paths
    root=read(P/'root_mcp_calls_final.json');history=[x for block in root['history_after_reports']['content'] if block['type']=='text' for x in json.loads(block['text']).get('history',[])]
    check('原history58..75',[x['id'] for x in history]==list(range(58,76)))
    selected=[x for x in history if x['id']>=67];wait=[x for x in selected if x['command'].startswith('wait_on_run synth_1')];prior=[x for x in history if x['id']<67 and x['command'].startswith('wait_on_run synth_1')]
    check('仅S2 wait72/0/381.939',len(wait)==1 and wait[0]['id']==72 and wait[0]['code']==0 and wait[0]['elapsed']==381.939)
    check('旧S1 wait62/.046排除',len(prior)==1 and prior[0]['id']==62 and prior[0]['elapsed']==0.046)
    report_entry=[x for x in selected if 'report_timing_summary' in x['command']];check('report命令实际native0',len(report_entry)==1 and report_entry[0]['id']==74 and report_entry[0]['code']==0)
    calls_text=json.dumps(root['calls'],ensure_ascii=False);check('MCP300s timeout原件仍在','300' in calls_text and ('timeout' in calls_text.lower() or 'timed out' in calls_text.lower()))
    classification=read(P/'collector_mcp_classification.json');check('MCP/native不同分类',classification['wait_native_exit_code']==0 and classification['wait_native_elapsed_seconds']==381.939 and classification['mcp_client_wait_timeout_seconds']==300 and classification['products_native_exit_code']==0 and classification['products_capture_exit_code']==1)
    report['s2_history_ids']=[x['id'] for x in selected];report['native_wait']={k:wait[0][k] for k in ('id','code','command','elapsed','timestamp')};report['excluded_prior_wait']={k:prior[0][k] for k in ('id','code','elapsed')}
    interp=tkinter.Tcl();products=(P/'products.tcldict').read_text(encoding='utf-8');d=interp.call('dict','get',products,'data')
    check('products native0/captureFAIL','FAIL'==interp.call('dict','get',d,'status') and int(interp.call('dict','get',d,'code'))==0 and int(interp.call('dict','get',d,'native_counts_before','WARNING'))==9 and int(interp.call('dict','get',d,'native_counts_after','WARNING'))==1 and int(interp.call('dict','get',d,'capture_options','-code'))==1)
    check('一次生成products证据',(P/'products.tcldict.native.log').read_bytes().count(b'generate_target')<=2)
    report['products']={'native':0,'capture':1,'whole_platform_entry':1,'warning_counters':[9,1]}
    text=(P/'timing_summary_synth.rpt').read_text(encoding='utf-8');section=text.split('| Design Timing Summary',1)[1].split('| Clock Summary',1)[0]
    lines=[line.split() for line in section.splitlines() if re.fullmatch(r'\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*',line)]
    check('唯一12项STA汇总',len(lines)==1);values=[float(x) for x in lines[0]]
    check('实际STA数值',values==[-62.174,-12041.195,811,14720,0.037,0.0,0,14720,8.87,0.0,0,4191] and 'Timing constraints are not met.' in text)
    clock=re.findall(r'^clk_fpga_0\s+\{([\d.]+)\s+([\d.]+)\}\s+([\d.]+)\s+([\d.]+)\s*$',text,re.M);check('真实50MHzclock',clock==[('0.000','10.000','20.000','50.000')])
    checks={k:set(re.findall(r'checking '+k+r' \((\d+)\)',text)) for k in ('no_clock','constant_clock','pulse_width_clock','unconstrained_internal_endpoints','no_input_delay','no_output_delay','multiple_clock','generated_clocks','loops','partial_input_delay','partial_output_delay','latch_loops')};check('12 check_timing均0',all(v=={'0'} for v in checks.values()))
    check('Synthesized/speed-2',bool(re.search(r'^\| Design State\s*:\s*Synthesized\s*$',text,re.M)) and bool(re.search(r'^\| Speed File\s*:\s*-2\s',text,re.M)))
    xdc=(P/'constraints_synth.xdc').read_text(encoding='utf-8');check('50MHz约束且无multicycle',re.findall(r'create_clock -period ([\d.]+)',xdc)==['20.000'] and 'set_multicycle_path' not in xdc and xdc.count('set_false_path')==2)
    check('无有效timing exceptions','No valid timing exceptions found.' in (P/'exceptions_synth.rpt').read_text(encoding='utf-8'))
    worst=(P/'timing_worst_synth.rpt').read_text(encoding='utf-8')
    first=lambda p:re.search(p,worst,re.M).group(1).strip()
    route={'source':first(r'^\s*Source:\s*(\S+)'),'destination':first(r'^\s*Destination:\s*(\S+)'),'logic_levels':int(first(r'^\s*Logic Levels:\s*(\d+)')),'carry4':int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)')),'data_path_delay_ns':float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns'))}
    check('真实最差ROUTE路径',route['source'].endswith('u_route_engine/groups_latched_reg[1]/C') and route['destination'].endswith('u_route_engine/output_address_latched_reg[0]/CE') and route['logic_levels']==323 and route['carry4']==305 and route['data_path_delay_ns']==81.562)
    util=(P/'utilization_flat_synth.rpt').read_text(encoding='utf-8');resources={}
    for key,label in (('lut','Slice LUTs*'),('ff','Slice Registers'),('bram','Block RAM Tile'),('dsp','DSPs')):
        found=re.findall(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util,re.M);check('资源唯一 '+key,len(found)==1);resources[key]=int(found[0])
    check('实际资源',resources=={'lut':35058,'ff':4027,'bram':32,'dsp':173});report['sta']={'status':'FAIL_TIMING','summary_values':values,'check_timing':{k:0 for k in checks},'worst_route':route,'resources':resources}
    sta=read(P/'collection_fix_sta_result_r02.json');check('classifier实际2/FAIL',sta['native_exit_code']==2 and sta['status']=='FAIL_TIMING' and read(P/'collection_fix_sta_native_r02.json')['native_exit_code']==2)
    for suffix,code,reason in (('',1,"KeyError('source_commit')"),('_r02',1,"RuntimeError('包装probe退出码不符')")):
        check('Collector失败保留 '+suffix,read(P/('collection_fix_collector_native'+suffix+'.json'))['native_exit_code']==code and read(P/('collection_fix_collector_failure'+suffix+'.json'))['error']==reason)
    check('首CRLF分类失败3保留',read(P/'collection_fix_sta_native.json')['native_exit_code']==3 and read(P/'collection_fix_sta_result.json')['status']=='FAIL_CLASSIFIER_INPUT')
    check('seal outer0独立内外时间',read(P/'collection_fix_seal_native.json')['native_exit_code']==0)
    check('原Root首次失败与r02成功保留','AssertionError' in (P/'collector_attempt_01.log').read_text(encoding='utf-8') and read(P/'collector_result.json')['native_exit_code']==0)
    historical=[]
    for name in ('collector_original_inventory.json','collector_original_inventory_r02.json'):
        inv=read(P/name);diff=[]
        for path,row in inv.items():
            actual=R/maps.get(path,path)
            if sha(actual)!=row['sha256'] or actual.stat().st_size!=row['bytes']:diff.append({'path':path,'historical':row,'closed_sha256':sha(actual),'closed_bytes':actual.stat().st_size})
        check('旧活动stdout历史分类 '+name,not diff if name.endswith('_r02.json') else len(diff)==1 and diff[0]['path']==(P/'collector_attempt_01.log').relative_to(R).as_posix() and diff[0]['historical']['bytes']==0)
        historical.append({'inventory':name,'differences':diff})
    report['historical_activity_mapping']=historical
    xsa=read(P/'collector_xsa_member_comparison.json');old=R/xsa['old_xsa_path'];new=R/xsa['new_xsa_path'];check('两XSA独立hash',sha(old)==xsa['old_xsa_sha256'] and sha(new)==xsa['new_xsa_sha256'])
    with zipfile.ZipFile(old) as a,zipfile.ZipFile(new) as b:
        check('ZIP完整CRC',a.testzip() is None and b.testzip() is None);members=[]
        for row in xsa['members']:
            aa=a.read(row['member']);bb=b.read(row['member']);check('实际XSA member '+row['member'],hashlib.sha256(aa).hexdigest()==row['old_sha256'] and hashlib.sha256(bb).hexdigest()==row['new_sha256'] and (aa==bb)==row['raw_equal'] and a.getinfo(row['member']).CRC==row['old_crc32'] and b.getinfo(row['member']).CRC==row['new_crc32']);members.append({'member':row['member'],'raw_equal':aa==bb})
    check('仅6PSinit相同/HWH不同',len(members)==7 and sum(x['raw_equal'] for x in members)==6 and not next(x['raw_equal'] for x in members if x['member'].endswith('.hwh')))
    report['xsa_member_comparison']=members
    check('DCP仅ignored缓存引用',len(mapping['dcp_references'])==5 and all(x['permanent'] is False for x in mapping['dcp_references']) and not any(p.suffix.lower()=='.dcp' for p in P.rglob('*')))
    report['dcp_references']=mapping['dcp_references'];report['cumulative_session_peak_mb']=classification['root_reported_cumulative_peak_mb'];check('session峰不冒充whole树',classification['process_tree_peak_memory']=='NOT_MEASURED' and mapping['process_tree_peak_memory']=='NOT_MEASURED')
    native('snapshot_static',[sys.executable,'-B',str(Q/'source_snapshot/verification/check_s2b_inference_platform.py'),'--root',str(Q/'source_snapshot')],0)
    for mode,code in (('evidence',0),('inputs',2)):native('packaging_'+mode,[sys.executable,'-B',str(R/'verification/check_stage_delivery.py'),'--mode',mode,'--manifest',str(MANIFEST)],code)
    native('actual_sta_classifier',[sys.executable,'-B',str(P/'collection_fix_classify_s2_sta_r02.py'),'--report',str(P/'timing_summary_synth.rpt'),'--result',str(W/'independent_classifier_result.json')],2)
    report['limitations']=['PASS仅证据准确性与固定源码恢复依据；FAIL_TIMING保持。','原18实际闭包为S2 profile0.1.2，S1/原平台/S3的资源报告不可混用。','native wait381.939秒不是严格综合总排队wall；各job单进程峰值和会话累计峰值分记，whole进程树与aggregate墙钟未测。','DCP为ignored缓存引用，不承诺永久恢复；冻结源、命令、原日志及报告可恢复。','XSA六PSinit相同但HWH不同，不批准旧ELF/runtime兼容性。','postroute、实现/bit、cache visibility、完整模型计算/G3均NOT_RUN；不批准G4/G5。','未运行Vivado/ROSS/SDK/serial/硬件/重型任务；当前S3源码未消费。']
    report['status']='PASS_EVIDENCE_INTEGRITY'
except Exception as exc:
    report['failure']=repr(exc);report['issues'].append({'location':report['checks'][-1]['name'] if report['checks'] else '审查入口','impact':'独立核验未全部完成','basis':repr(exc),'closure':'保留失败原件，补齐或修正明确失败字段后独立复审'})
report['seconds']=time.monotonic()-started;report['peak_memory']='NOT_MEASURED';report['whole_review_walltime']='NOT_MEASURED'
report['review_program_sha256']=sha(Path(__file__))
(W/'audit_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(report['checks']),'seconds':report['seconds'],'failure':report.get('failure')},ensure_ascii=False),flush=True)
raise SystemExit(0 if report['status']=='PASS_EVIDENCE_INTEGRITY' else 1)
