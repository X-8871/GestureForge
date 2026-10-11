"""显式闭合门禁后收集 S7 实际结果，时序值与状态均来自本轮。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
import re, xml.etree.ElementTree as ET, zipfile, zlib

def first(pattern,text):
    """要求实际报告存在定位字段。"""
    values=re.findall(pattern,text,re.M)
    require(values,'缺少字段：'+pattern)
    return values[0].strip()

def numeric(pattern,text):
    """保持整数资源为整数，半片资源保留实际小数。"""
    value=float(first(pattern,text))
    return int(value) if value.is_integer() else value

started=time.monotonic()
gate=closed_gate()
initial=[binding(p) for p in sorted(exact(REPORT,'directory').rglob('*')) if p.is_file()]
save(WORK/'initial_inventory.json',{'files':initial,'file_count':len(initial),'total_bytes':sum(r['bytes'] for r in initial)})
rawcopy(WORK/'initial_inventory.json',REPORT/'s7_collection_original_inventory.json')
rawcopy(WORK/'closed_inputs.json',REPORT/'s7_collection_closed_inputs.json')
code_dir=mkdir_new(REPORT/'collector_code')
for name in ('collection_common.py','classify_s7_sta.py','prepare_s7.py','run_preparation.py','collect_s7.py','run_collection.py','finalize_s7.py','run_finalization.py'):
    rawcopy(WORK/name,code_dir/name)
for name in ('prepared_receipt.json','preparation.stdout.log','preparation.stderr.log','preparation.native.json'):
    rawcopy(WORK/name,code_dir/name)
mcpdir=mkdir_new(REPORT/'mcp_closed')
closed_copies=[]
targets=set()
source_paths=[p for p in sorted(exact(CACHE,'directory').glob('mcp_*.json')) if p.is_file()]
source_paths += [ROOT/gate[name]['path'] for name in ('static_source_closed','mcp_history')]
source_paths += [ROOT/row['path'] for row in gate.get('additional_closed_files',[])]
for path in source_paths:
    if path.name in targets:
        require(any(row['original_path']==rel(path) for row in closed_copies),'关闭文件同名来源冲突')
        continue
    row=next((r for r in gate.get('additional_closed_files',[]) if r['path']==rel(path)),None)
    if row is not None:
        require(sha(path)==row['sha256'],'声明的关闭文件漂移')
    closed_copies.append(rawcopy(path,mcpdir/path.name))
    targets.add(path.name)
root_source=exact(ROOT/gate['immutable_session_log']['path'])
root_log=REPORT/'s7_collection_immutable_session_log.log'
rawcopy(root_source,root_log)
raw=root_log.read_bytes()
peaks=re.findall(rb'peak = ([0-9.]+)',raw)
root_peak=max(map(float,peaks)) if peaks else None
try:
    raw.decode('utf-8')
    raw_utf8=True
except UnicodeDecodeError:
    raw_utf8=False
save(REPORT/'s7_collection_root_log_binding.json',{'snapshot':binding(root_log),'root_declared_binding':gate['immutable_session_log'],'raw_bytes_preserved':True,'raw_utf8_decodable':raw_utf8,'ascii_numeric_extraction_only':True,'active_log_consumed':False,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False})
save(REPORT/'s7_collection_closed_input_mapping.json',{'files':closed_copies,'count':len(closed_copies),'bytes':sum(r['bytes'] for r in closed_copies),'scope':'仅总控显式关闭后本轮mcp与声明原件；不读取活动累计log。'})

before_path=exact(PRE/'source_before.json')
after_path=exact(ROOT/gate['source_after']['path'])
static_path=exact(ROOT/gate['static_source_closed']['path'])
require(sha(before_path)==BEFORE_SHA and sha(FREEZE)==FREEZE_SHA,'已知before/freeze哈希不同')
before,after,static=read(before_path),read(after_path),read(static_path)
require(before['source_commit']==after['source_commit']==static['source_commit']==BASELINE,'实际源码基线不同')
rows=before['source_files']
later={r['path']:r for r in after['source_files']}
frozen=read(FREEZE)
require(len(rows)==len(later)==39 and static['source_count']==len(static['source_sha256'])==31,'39/31闭包不同')
extra=sorted(set(later)-set(static['source_sha256']))
require(len(extra)==8 and set(extra)==set(frozen['extra_bindings_beyond_static']) and set(static['source_sha256'])<set(later),'31+8闭包不同')
require(before['source_freeze']==after['source_freeze']==rel(FREEZE) and before['source_freeze_sha256']==after['source_freeze_sha256']==FREEZE_SHA,'冻结入口不同')
sources=[]
for row in rows:
    old,new=exact(ROOT/row['snapshot']),exact(ROOT/later[row['path']]['snapshot'])
    require(sha(old)==sha(new)==row['sha256']==later[row['path']]['sha256'] and old.stat().st_size==new.stat().st_size==row['bytes']==later[row['path']]['bytes'],'前后源码快照漂移：'+row['path'])
    blob,command,code=git_blob(row['path'])
    same=blob==old.read_bytes()
    eol=not same and b'\r\n' not in blob and blob.replace(b'\n',b'\r\n')==old.read_bytes()
    require(hashlib.sha256(blob).hexdigest()==row['git_blob_sha256'] and (same or eol),'Git原字节或精确EOL不同')
    require(row['git_relation']==('RAW_IDENTICAL' if same else 'GIT_LF_TO_RAW_CRLF'),'原关系标签不同')
    if row['path'] in static['source_sha256']:
        require(row['sha256']==static['source_sha256'][row['path']],'静态源码哈希不同')
    sources.append({**row,'snapshot_after':rel(new),'git_native_command':command,'git_native_exit_code':code,'git_raw_same':same,'exact_git_lf_to_snapshot_crlf':eol,'live_source_consumed':False})
require(sum(r['git_raw_same'] for r in sources)==33 and sum(r['exact_git_lf_to_snapshot_crlf'] for r in sources)==6,'实际不是33RAW+6EOL')
require(frozen['source_sha256']=={r['path']:r['sha256'] for r in rows},'freeze与实际39不同')
require(len(frozen['frozen14_sha256'])==14 and before['frozen14_sha256']==after['frozen14_sha256']==frozen['frozen14_sha256'],'原14绑定不同')
for path,expected in frozen['frozen14_sha256'].items():
    require(later[path]['sha256']==expected,'原14快照变化')
profile=read(ROOT/later['board/s2b_inference_platform.json']['snapshot'])
require(profile['version']=='s2b-inference-platform/0.1.7' and profile['clock_hz']==50000000 and profile['visibility_default']==0 and profile['vivado_part']=='xc7z020clg400-2','本轮profile不同')
save(REPORT/'s7_collection_source_binding.json',{'status':'ACTUAL39_BEFORE_AFTER_GIT_A5_BOUND','source_commit':BASELINE,'source_before':binding(before_path),'source_after':binding(after_path),'static_source_closed':binding(static_path),'source_freeze':binding(FREEZE),'source_count':39,'platform_static_source_count':31,'extra_bindings':extra,'sources':sources,'git_raw_same_count':33,'exact_eol_count':6,'frozen14_unchanged':True,'frozen14_sha256':frozen['frozen14_sha256'],'live_source_consumed':False,'note':'历史freeze提交与G2字段不改写；实际综合源码a5由Git对象与前后快照另行绑定。'})

native_root=mkdir_new(REPORT/'native_jobs')
run_root=exact(PROJECT/'s2b_inference_candidate.runs','directory')
directories=sorted(p for p in run_root.iterdir() if p.is_dir() and p.name!='.jobs')
require(len(directories)==5,'实际job不是5')
mapping,jobs=[],[]
for directory in directories:
    target=mkdir_new(native_root/('wrapper_native_s7_r01' if directory.name=='synth_1' else directory.name))
    log=exact(directory/'runme.log').read_text(encoding='utf-8')
    require('synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log,'原生综合未成功完成')
    require((directory/'__synthesis_is_complete__').is_file() and (directory/'.vivado.end.rst').is_file() and not (directory/'.vivado.error.rst').exists(),'原生结束marker不同')
    for path in sorted(directory.iterdir()):
        if path.is_file() and (path.suffix in ('.tcl','.log','.jou','.vds','.xdc','.rpt','.rst','.js','.sh','.bat','.xml') or path.name in ('htr.txt','__synthesis_is_complete__')):
            mapping.append(rawcopy(path,target/path.name))
    process=ET.fromstring(exact(directory/'.vivado.begin.rst').read_bytes()).find('Process')
    require(process is not None,'原生launcher元数据缺失')
    elapsed=re.search(r'synth_design:.*?elapsed = (\d+):(\d+):(\d+)',log)
    require(elapsed,'原生synth耗时缺失')
    start=first(r'Start of session at:\s*([^\r\n]+)',log)
    end=first(r'Exiting Vivado at ([^\r\n]+)',log).removesuffix('...')
    diag=re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered',log)
    peaks=re.findall(r'peak = ([0-9.]+)',log)
    jobs.append({'run':directory.name,'saved_directory':rel(target),'status':'NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS','actual_vivado_job_pid':int(first(r'Process ID\s*:\s*(\d+)',log)),'launcher_pid_from_begin_rst':int(process.attrib['Pid']),'launcher_command':process.attrib['Command'],'session_start_local':start,'session_end_local':end,'timezone_context':'UTC+8','session_wall_seconds_from_native_timestamps':(datetime.strptime(end,'%a %b %d %H:%M:%S %Y')-datetime.strptime(start,'%a %b %d %H:%M:%S %Y')).total_seconds(),'synth_design_elapsed_seconds':int(elapsed[1])*3600+int(elapsed[2])*60+int(elapsed[3]),'reported_single_process_peak_mb':max(map(float,peaks)) if peaks else None,'peak_unit':'Vivado原生日志MB，单进程，不是进程树峰','final_diagnostics':dict(zip(('infos','warnings','critical_warnings','errors'),map(int,diag[-1]))),'raw_os_process_exit_code':None,'os_exit_code_reason':'未直接捕获OS子进程退出码；完成由原日志/marker及同次history/run状态核查。'})
infer=next(j for j in jobs if j['run']=='s2b_inference_infer_0_synth_1')
tcl=(native_root/'s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
block=first(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}',tcl)
compiled=[Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
require(len(compiled)==len(set(compiled))==18 and set(compiled)==set(profile['rtl_sources']),'实际编译18不同')
generated=mkdir_new(REPORT/'generated_inputs')
genroot=exact(PROJECT/'s2b_inference_candidate.gen/sources_1/bd/s2b_inference','directory')
constraints=sorted(genroot.rglob('*.xdc'))+sorted(run_root.rglob('*_propImpl.xdc'))
require(constraints and len({p.name for p in constraints})==len(constraints),'生成约束同名冲突或缺失')
for path in constraints:
    mapping.append(rawcopy(path,generated/path.name))
wrapper=exact(PROJECT/'s2b_inference_candidate.srcs/sources_1/imports/hdl/s2b_inference_wrapper.v')
genwrapper=exact(genroot/'hdl/s2b_inference_wrapper.v')
require(sha(wrapper)==sha(genwrapper),'import/generated wrapper不同')
mapping.append(rawcopy(wrapper,generated/wrapper.name))
for path in (exact(genroot/'synth/s2b_inference.v'),exact(genroot/'ip/s2b_inference_infer_0/synth/s2b_inference_infer_0.sv')):
    mapping.append(rawcopy(path,generated/path.name))
require(wrapper.as_posix() in (native_root/'wrapper_native_s7_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8'),'native唯一wrapper路径缺失')
require('wrapper '+wrapper.as_posix()+' top s2b_inference_wrapper' in (REPORT/'setup_synthesis.tcldict').read_text(encoding='utf-8'),'setup唯一wrapper不同')
require(sum(Path(r['saved_path']).suffix=='.vds' for r in mapping)==5,'实际VDS不是5')
known_peaks=[j['reported_single_process_peak_mb'] for j in jobs if j['reported_single_process_peak_mb'] is not None]
single_peak=max(known_peaks) if known_peaks else None
save(REPORT/'s7_collection_native_mapping.json',{'files':mapping,'jobs':jobs,'native_job_count':len(jobs),'native_raw_copy_count':len(mapping),'native_raw_copy_bytes':sum(r['bytes'] for r in mapping),'native_vds_count':5,'generated_xdc_count':len(constraints),'actual_compiled_rtl_sources':compiled,'actual_compiled_source_count':18,'actual_compiled_source_snapshots':[{'source_identifier':name,'source_snapshot':later[name]['snapshot'],'sha256':later[name]['sha256']} for name in compiled],'source_binding':rel(REPORT/'s7_collection_source_binding.json'),'wrapper_import':binding(wrapper),'wrapper_generated_original':binding(genwrapper),'unique_registered_wrapper_count_from_setup':1,'generated_wrapper_raw_equals_imported':True,'single_process_peak_max_mb':single_peak,'process_tree_peak_memory_bytes':None,'excluded_cache_policy':'仅本轮必要native日志/VDS/脚本/marker/生成约束；不复制DCP/PB/WDF/cache/obj_dir/EXE/整SDK/未消费旧测试文件。'})

history=mcp_json(read(ROOT/gate['mcp_history']['path']))['history']
labels=('source','builder','setup','launch','wait','open_run','reports','query_xdc','close')
require(len(history)==9 and len({h['id'] for h in history})==9,'实际design history不是9')
require([r['label'] for r in gate['design_mcp_records']]==list(labels),'关闭命令记录顺序不同')
paired=[]
for label,item,declared in zip(labels,history,gate['design_mcp_records']):
    path=exact(ROOT/declared['path'])
    require(sha(path)==declared['sha256'],'关闭MCP绑定漂移')
    call=read(path)
    result=mcp_result(call)
    captured='input' in call
    if captured:
        require(call['input']['command']==item['command'],'client/history实际命令不同')
    else:
        require(label in ('source','builder'),'缺少必须client input包装')
    timeout=result.get('isError') is True and any('300s' in b.get('text','') for b in result['content'])
    if timeout:
        require(label=='wait','非wait发生未处理timeout')
        code=None
    else:
        code=mcp_json(call)['exit_code']
        require(code==item['code'],'client/native码不同')
    paired.append({'label':label,'client_record':binding(mcpdir/path.name),'native_history':item,'client_input_captured':captured,'saved_client_schema':'INPUT_RESULT_WRAPPER' if captured else 'RAW_CALL_TOOL_RESULT','client_wall_ms':call.get('wall_ms'),'client_timeout':timeout,'client_returned_exit_code':code,'command_binding_basis':'client input与同次关闭history精确核对' if captured else '原client input未保存，同次关闭history绑定实际命令，不伪称恢复client input'})
bylabel={r['label']:r for r in paired}
states=bylabel['query_xdc']['native_history']['output']
require(states.count('status {synth_design Complete!} progress 100%')==5 and states.count('status {Not started} progress 0%')==5 and 'clock_period 20.000' in states,'实际run状态不同')
wait=bylabel['wait']
require(wait['native_history']['code']==0 and bylabel['close']['native_history']['command']=='close_project' and bylabel['close']['native_history']['code']==0,'wait/close原生状态不同')
launch=first(r'\[([^\]]+)\] Launched synth_1',bylabel['launch']['native_history']['output'])
finished=first(r'\[([^\]]+)\] synth_1 finished',wait['native_history']['output'])
wrapper_job=next(j for j in jobs if j['run']=='synth_1')
parse_time=lambda value:datetime.strptime(value,'%a %b %d %H:%M:%S %Y')
products=(REPORT/'products.tcldict').read_text(encoding='utf-8')
require('status FAIL code 0 raw PRODUCTS:OK' in products and 'WARNING emitted=-8 exported=2' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products,'本轮products原FAIL不同')
require(bylabel['builder']['native_history']['code']==1,'builder原失败不同')
mcpbinding={'status':'CLOSED_S7_CLIENT_NATIVE_HISTORY_BOUND','paired_calls':paired,'mcp_execute_calls':len(history),'mcp_history_calls':1,'execute_plus_history_calls':len(history)+1,'all_host_tool_calls':None,'client_wait_is_error':mcp_result(read(ROOT/gate['design_mcp_records'][4]['path'])).get('isError',False),'client_wait_timeout':wait['client_timeout'],'client_wait_timeout_seconds':300 if wait['client_timeout'] else None,'client_wait_wall_ms':wait['client_wall_ms'],'native_wait_exit_code':wait['native_history']['code'],'native_wait_elapsed_seconds':wait['native_history']['elapsed'],'launch_timestamp_native_local':launch,'native_wrapper_exit_local':wrapper_job['session_end_local'],'launcher_finished_local':finished,'timezone_context':'UTC+8','launch_to_native_wrapper_exit_seconds':(parse_time(wrapper_job['session_end_local'])-parse_time(launch)).total_seconds(),'launch_to_launcher_finished_seconds':(parse_time(finished)-parse_time(launch)).total_seconds(),'whole_builder_native_exit_code':1,'whole_builder_native_elapsed_seconds':bylabel['builder']['native_history']['elapsed'],'products_native_exit_code':0,'products_capture_exit_code':1,'products_warning_counter_before':9,'products_warning_counter_after':1,'products_warning_emitted_delta':-8,'products_warning_exported_count':2,'products_repeated':False,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'implementation_started':False,'implementation_strategy_list_only':states.split(' impl_strategies ',1)[1] if ' impl_strategies ' in states else None,'root_auxiliary_mcp_call_counts':gate.get('auxiliary_mcp_call_counts'),'scope':'后续idle sessionstop与runtime预检不计9designexecute，也不作为STA通过依据。'}
save(REPORT/'s7_collection_mcp_history_binding.json',mcpbinding)

classifier=run_closed([sys.executable,'-B',str(code_dir/'classify_s7_sta.py'),'--report',str(REPORT/'timing_summary_synth.rpt'),'--result',str(REPORT/'s7_collection_sta_result.json')],'s7_collection_sta')
copy_closed('s7_collection_sta')
require(classifier['native_exit_code'] in (0,2),'分类器输入失败，原件和真实码保留')
sta=read(REPORT/'s7_collection_sta_result.json')
require(sta['native_exit_code']==classifier['native_exit_code'],'分类器自报/捕获码不同')
util=(REPORT/'utilization_flat_synth.rpt').read_text(encoding='utf-8')
resources={k:numeric(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+(?:\.\d+)?)\s*\|',util) for k,label in (('lut','Slice LUTs*'),('ff','Slice Registers'),('bram','Block RAM Tile'),('dsp','DSPs'),('latch','Register as Latch'))}
worst=(REPORT/'timing_worst_synth.rpt').read_text(encoding='utf-8')
levels=first(r'^\s*Logic Levels:\s*(.+)',worst)
component_counts={a:int(b) for a,b in re.findall(r'(\w+)=(\d+)',levels)}
w={'source':first(r'^\s*Source:\s*(\S+)',worst),'destination':first(r'^\s*Destination:\s*(\S+)',worst),'logic_levels':int(first(r'^(\d+)',levels)),'carry4':component_counts.get('CARRY4',0),'dsp48e1':component_counts.get('DSP48E1',0),'component_counts':component_counts,'data_path_delay_ns':float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns',worst)),'logic_delay_ns':float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns',worst)),'route_delay_ns':float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns',worst))}
xdc=(REPORT/'constraints_synth.xdc').read_text(encoding='utf-8')
exceptions=re.findall(r'current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)',xdc)
require(len(exceptions)==2 and all('rst_fclk0/U0/EXT_LPF/' in scope and 'syncstages_ff_reg[0]' in command for scope,command in exceptions),'resetCDC实际例外不同')
require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc,'实际时钟约束不同')
exception_report=(REPORT/'exceptions_synth.rpt').read_text(encoding='utf-8')
save(REPORT/'s7_collection_constraints_binding.json',{'clock':sta['clock'],'input_jitter_ns':0.6,'check_timing':sta['check_timing'],'exported_reset_cdc_false_paths':[{'scope':scope,'command':command} for scope,command in exceptions],'exported_false_path_count':len(exceptions),'report_exceptions_no_valid_statement_present':'No valid timing exceptions found.' in exception_report,'report_exceptions':binding(REPORT/'exceptions_synth.rpt'),'interpretation':'实际check_timing计数与两个resetCDC false_path分别记录；不以report_exceptions文字抹去write_xdc中的例外。'})
method=(REPORT/'methodology_synth.rpt').read_text(encoding='utf-8')
drc=(REPORT/'drc_synth.rpt').read_text(encoding='utf-8')
method_rules=[{'rule':a,'severity':b,'description':c.strip(),'count':int(d)} for a,b,c,d in re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|([^|]+)\|\s*(\d+)\s*\|',method,re.M)]
drc_rules=[{'rule':a,'severity':b,'description':c.strip(),'count':int(d)} for a,b,c,d in re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|([^|]+)\|\s*(\d+)\s*\|',drc,re.M)]
method_count=int(first(r'Checks found:\s*(\d+)',method))
drc_count=int(first(r'Checks found:\s*(\d+)',drc))
require(sum(r['count'] for r in method_rules)==method_count and sum(r['count'] for r in drc_rules)==drc_count,'methodology/DRC汇总与规则计数不同')

old_xsa=exact(ROOT/'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa')
new_xsa=exact(REPORT/'s2b_inference_no_bit.xsa')
psroot=exact(genroot/'ip/s2b_inference_ps7_0','directory')
members=[]
with zipfile.ZipFile(old_xsa) as old,zipfile.ZipFile(new_xsa) as new:
    require(not any(n.endswith('.bit') for n in new.namelist()),'XSA意外含bit')
    for name in ('ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h','s2b_inference.hwh'):
        a,b=old.read(name),new.read(name)
        require(zlib.crc32(a)==old.getinfo(name).CRC and zlib.crc32(b)==new.getinfo(name).CRC,'XSA CRC不同')
        row={'member':name,'old_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),'old_bytes':len(a),'new_bytes':len(b),'raw_equal':a==b,'old_crc32':old.getinfo(name).CRC,'new_crc32':new.getinfo(name).CRC}
        if name.startswith('ps7_init'):
            require(exact(psroot/name).read_bytes()==b,'生成PSinit与XSA不同')
            row['generated_original']=binding(psroot/name)
            row['saved_copy']=rawcopy(psroot/name,generated/name)
        members.append(row)
    require(all(r['raw_equal'] for r in members[:6]) and not members[6]['raw_equal'],'PSinit/HWH实际关系不同')
    metadata={'xsa_json':json.loads(new.read('xsa.json')),'hwdef_xml':new.read('hwdef.xml').decode('utf-8'),'xsa_xml':new.read('xsa.xml').decode('utf-8')}
    require(metadata['xsa_json']['platformState']=='pre_synth' and metadata['xsa_json']['devices'][0]['part']['name']=='xc7z020clg400-2','XSA元数据不同')
    for name in ('hwdef.xml','xsa.json','xsa.xml','s2b_inference.hwh'):
        new_target(generated/name)
        with (generated/name).open('xb') as stream:
            stream.write(new.read(name))
pstcl=(generated/'ps7_init.tcl').read_text(encoding='utf-8')
post=[]
for revision in ('1_0','2_0','3_0'):
    body=first(r'proc ps7_post_config_'+revision+r' \{\} \{([^}]+)\}',pstcl)
    operations=[line.strip() for line in body.splitlines() if line.strip()]
    require(operations==['mwr -force 0XF8000008 0x0000DF0D','mask_write 0XF8000900 0x0000000F 0x0000000F','mask_write 0XF8000240 0xFFFFFFFF 0x00000000','mwr -force 0XF8000004 0x0000767B'],'生成postconfig表不同')
    post.append({'silicon_revision':revision,'official_generated_procedure':'ps7_post_config_'+revision,'operations':operations})
save(REPORT/'s7_collection_xsa_member_comparison.json',{'status':'SIX_PSINIT_BYTES_SAME_T13_AND_GENERATED_HWH_CHANGED_NO_BIT','old_xsa':binding(old_xsa),'new_xsa':binding(new_xsa),'members':members,'official_generated_postconfig_tables':post,'xsa_metadata':metadata,'elf_runtime_compatibility':'NOT_APPROVED','note':'六成员相等仅证明成员原字节，不批准旧BSP/ELF整体兼容；生成表未调用，无bit平台不代表部署。'})

blob,command,code=git_blob('verification/check_stage_delivery.py')
checker=REPORT/'s7_collection_stage_checker_snapshot.py'
new_target(checker)
with checker.open('xb') as stream:
    stream.write(blob)
save(REPORT/'s7_collection_stage_checker_binding.json',{'source_commit':BASELINE,'original_identifier':'verification/check_stage_delivery.py','snapshot':binding(checker),'git_native_command':command,'git_native_exit_code':code,'live_checker_consumed':False})
prior=exact(ROOT/'report/evidence/S2B-T17/s6_platform_20261011_r01/s6_collection_delivery_manifest_r02.json')
interfaces=read(prior)['interfaces']
for row in interfaces:
    require(sha(ROOT/row['path'])==row['sha256'],'正式接口文档漂移')
externals=[{'path':rel(p),'role':'input'} for p in (FREEZE,old_xsa,prior,before_path,after_path)]
externals += [{'path':r['snapshot'],'role':'source'} for r in rows]+[{'path':r['snapshot'],'role':'source'} for r in after['source_files']]
limitations=['仅收集S7已关闭实际结果，独立证据审查尚未执行，G3/G4/G5未批准。','39源码闭包/31static+8extra、33GitRAW+6精确EOL、前后快照与原14实际核验；不消费live源码。','builder1/products native0 capture1与WARNING9到1/emitted−8/exported2原FAIL保留，不重跑products。','客户端wait状态/timeout与实际history native码、耗时分开；launch至native退出和launcherfinished分别记录。','STA状态与各数值来自S7本轮综合态实际报告，无降频；不是postroute或板上证明。','五jobOS子进程原生码未直接捕获为null；日志、marker、historywait0及run100%支持实际完成。','单进程峰/核心耗时由各native日志读取；root累计峰不是进程树峰，collector峰/全树峰/全部host工具量未测。','check_timing与两个resetCDC false_path分别保留，不抹去实际例外。','六PSinit实际同T13与本次生成、HWH变化；XSA pre_synth无bit，旧BSP/ELF整体兼容未批准。','物理候选0.1.1未冻结，visibility0；实现/postroute/bit/cache/model/109/1000次/BOARD NOT_RUN。','未读取活动log、未改ROOT关闭原件；仅本轮消费资料，无DCP/cache/obj_dir/EXE/整SDK/旧大测试复制。','闭合门禁只允许收集，不批准G1/G2/STA/部署；CHECKS_OK仅包装/hash，inputs未冻结及失败仍阻断。']
summary={'status':'COLLECTED_S7_'+sta['status']+'_PENDING_INDEPENDENT_EVIDENCE_REVIEW','sta_status':sta['status'],'source_commit':BASELINE,'source_count':39,'platform_static_source_count':31,'extra_binding_count':8,'compiled_rtl_count':18,'profile_version':profile['version'],'physical_interface':'s2b-physical-candidate/0.1.1','visibility':0,'original_raw_file_count':len(initial),'original_raw_bytes':sum(r['bytes'] for r in initial),'original_raw_unchanged':True,'native_raw_copy_count':len(mapping),'native_raw_copy_bytes':sum(r['bytes'] for r in mapping),'native_job_count':5,'native_vds_count':5,'native_wait_exit_code':wait['native_history']['code'],'native_wait_elapsed_seconds':wait['native_history']['elapsed'],'mcp_wait_timeout':wait['client_timeout'],'launch_to_native_wrapper_exit_seconds':mcpbinding['launch_to_native_wrapper_exit_seconds'],'launch_to_launcher_finished_seconds':mcpbinding['launch_to_launcher_finished_seconds'],'native_report_exit_code':bylabel['reports']['native_history']['code'],'native_report_elapsed_seconds':bylabel['reports']['native_history']['elapsed'],'native_classifier_exit_code':classifier['native_exit_code'],'timing':sta['timing'],'clock':sta['clock'],'check_timing':sta['check_timing'],'resources':resources,'worst_path':w,'methodology':{'checks':method_count,'rules':method_rules},'drc':{'checks':drc_count,'rules':drc_rules},'exported_reset_cdc_false_path_count':2,'external_inputs':externals,'infer_synth_elapsed_seconds':infer['synth_design_elapsed_seconds'],'infer_single_process_peak_mb':infer['reported_single_process_peak_mb'],'single_process_peak_max_mb':single_peak,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'threads':1,'jobs':1,'synthesis_execution_count':1,'products_execution_count':1,'mcp_execute_calls':len(history),'mcp_history_calls':1,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'limitations':limitations,'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'collector_elapsed_so_far_seconds':time.monotonic()-started}
save(REPORT/'s7_collection_summary.json',summary)
checks=[{'name':'S7实际39源码及Gita5绑定','status':'PASS','command':' '.join(sources[0]['git_native_command']),'exit_code':0,'reason':'其余38条实际Git命令/码在source_binding，33RAW+6EOL，原14未变。'},{'name':'五个原生综合完成','status':'PASS','command':wait['native_history']['command'],'exit_code':wait['native_history']['code'],'reason':'客户端结果与nativewait分别绑定。'},{'name':'综合态实际STA报告生成','status':'PASS' if bylabel['reports']['native_history']['code']==0 else 'FAIL','command':bylabel['reports']['native_history']['command'],'exit_code':bylabel['reports']['native_history']['code']},{'name':'50MHz综合态STA分类','status':'PASS' if classifier['native_exit_code']==0 else 'FAIL','command':' '.join(classifier['command']),'exit_code':classifier['native_exit_code'],'reason':sta['status']+'；实际数值在绑定报告和sta_result。'},{'name':'builder及products原捕获失败','status':'FAIL','command':bylabel['builder']['native_history']['command'],'exit_code':1,'reason':'native products0/capture1与warning计数变化原FAIL保留。'},{'name':'非预期锁存器','status':'PASS' if resources['latch']==0 else 'FAIL','command':'report_utilization -file utilization_flat_synth.rpt','exit_code':bylabel['reports']['native_history']['code'],'reason':'实际Register as Latch='+str(resources['latch'])+'；命令为本次批量reports的一部分。'}]
for name in ('S7独立证据准确性审查','实现及postroute','bitstream生成','板上cache probe','板上模型及109样本','1000次板上任务','BOARD及G3验收'):
    checks.append({'name':name,'status':'NOT_RUN','command':None,'exit_code':None,'reason':'本Collector仅收集关闭原件，未执行该项。'})
manifest={'schema_version':1,'stage':'2B','task_id':'S2B-T17','run_id':'s7_platform_20261011_r01','source_commit':BASELINE,'evidence_dir':rel(REPORT),'interfaces':interfaces,'tool_versions':{'python':sys.version,'Vivado':'2026.1 Build6511674 本次原报告/日志','part':profile['vivado_part'],'profile':profile['version']},'files':manifest_files(externals),'checks':checks,'limitations':limitations}
manifest_path=REPORT/'s7_collection_delivery_manifest_r01.json'
save(manifest_path,manifest)
results={mode:run_closed([sys.executable,'-B',str(checker),'--mode',mode,'--manifest',str(manifest_path),'--project-root',str(ROOT)],'s7_collection_'+mode+'_r01') for mode in ('evidence','inputs')}
for mode in results:
    copy_closed('s7_collection_'+mode+'_r01')
require({k:r['native_exit_code'] for k,r in results.items()}=={'evidence':0,'inputs':2},'实际包装码不同，关闭失败原件已保存')
save(REPORT/'s7_collection_packaging_r01.json',{'status':'EVIDENCE_PACKAGING_OK_INPUTS_ACTUAL_FAIL','checks':results,'policy':'0/2仅包装与输入门禁，不将真实STA状态改判。'})
original_check()
closed_gate()
print(json.dumps({'status':summary['status'],'sta_status':sta['status'],'original_files':len(initial),'native_copies':len(mapping),'native_raw_bytes':sum(r['bytes'] for r in mapping),'source_count':39,'compiled_rtl_count':18,'codes':{'sta':classifier['native_exit_code'],'evidence':0,'inputs':2},'collector_elapsed_seconds':time.monotonic()-started},ensure_ascii=False))
