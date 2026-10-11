"""收集已结束的 S6 综合失败，仅消费封存快照和明确 Git 基线。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
import re, xml.etree.ElementTree as ET, zipfile, zlib

def first(pattern, text):
    """要求实际报告中存在定位字段。"""
    values = re.findall(pattern, text, re.M)
    require(values, '缺少字段：' + pattern)
    return values[0].strip()

started = time.monotonic()
original_check()
rawcopy(WORK / 'initial_inventory.json', REPORT / 's6_collection_original_inventory.json')
code_dir = mkdir_new(REPORT / 'collector_code')
for name in ('collection_common.py','collect_s6.py','run_collection.py','finalize_s6.py','run_finalization.py','inspect_s6.py','inspect_values.py'):
    rawcopy(WORK / name, code_dir / name)
save(REPORT / 's6_collection_preview_diagnostic.json', {'status':'FAIL_AUXILIARY_PREVIEW_UTF8_DECODE','script':binding(code_dir / 'inspect_values.py'),'host_tool_exit_code':1,'native_exit_code':None,'native_exit_code_reason':'预览通过 PowerShell/Git Bash 宿主调用，仅获得宿主 exit_code=1，未另行捕获子进程 returncode，不伪填原生码。','exception':'UnicodeDecodeError: utf-8 cannot decode byte 0xc3 in position 3676: invalid continuation byte','stdout_raw_complete':False,'stderr_raw_complete':False,'raw_log_modified':False,'collector_effect':'只读预览失败，正式收集按原字节保存日志并对 ASCII 字段使用 bytes 正则。','specified_sta_path':'verification/check_s2b_inference_sta.py','specified_sta_path_status':'TASK_MESSAGE_PATH_ERROR_NOT_PRESENT_NOT_RUN','specified_sta_native_exit_code':None})
root_log = REPORT / 's6_collection_root_session_snapshot.log'
rawcopy(CACHE / 'root_session_snapshot.log', root_log)
require(sha(root_log) == '5c27e90921ee6dd1670959f0b0dabdad64992efc0f1b06da4e2273a448f1ce23' and root_log.stat().st_size == 65467, '关闭日志快照不同')
root_raw = root_log.read_bytes()
root_peak = max(map(float, re.findall(rb'peak = ([0-9.]+)', root_raw)))
try:
    root_raw.decode('utf-8')
    root_utf8 = True
except UnicodeDecodeError:
    root_utf8 = False
save(REPORT / 's6_collection_root_log_binding.json', {'snapshot':binding(root_log),'original_snapshot_binding':binding(CACHE / 'root_session_snapshot_binding.json'),'active_log_consumed':False,'raw_utf8_decodable':root_utf8,'raw_bytes_preserved':True,'ascii_peak_extraction_only':True,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False})

before, after, static = read(PRE / 'source_before.json'), read(PRE / 'source_after.json'), read(CACHE / 'static_actual_closed.json')
require(sha(PRE / 'source_before.json') == '1031972cab9e1ae69405923ed5b2cf50e887297841a588742b91ef5ab046d09a', 'before哈希不同')
require(sha(PRE / 'source_after.json') == 'f9af1b301a95ff1072da244ed3c67de3786c9576c33d41ae72255aeb11f6b4fb', 'after哈希不同')
require(sha(CACHE / 'static_actual_closed.json') == '3f2f5d1724a025578c52f15433d6c53fac16fdf4057508b00d7295ce77ff6974', 'static封存不同')
require(before['source_commit'] == after['source_commit'] == static['source_commit'] == BASELINE, '基线不同')
rows = before['source_files']
later = {r['path']:r for r in after['source_files']}
require(len(rows) == len(later) == 38 and static['source_count'] == len(static['source_sha256']) == 31, '实际闭包计数不同')
freeze = exact(ROOT / before['source_freeze'])
require(sha(freeze) == before['source_freeze_sha256'] == after['source_freeze_sha256'] == '37ed95bb84166a406589ebcba4a23c262e6d390dd1551c446988bcd222ea832b', 'freeze字节不同')
frozen = read(freeze)
extra = sorted(set(later) - set(static['source_sha256']))
require(len(extra) == 7 and set(extra) == set(frozen['extra_bindings_beyond_static']) and set(static['source_sha256']) < set(later), '31+7闭包不同')
sources = []
for row in rows:
    old, new = exact(ROOT / row['snapshot']), exact(ROOT / later[row['path']]['snapshot'])
    require(sha(old) == sha(new) == row['sha256'] == later[row['path']]['sha256'] and old.stat().st_size == new.stat().st_size == row['bytes'] == later[row['path']]['bytes'], '前后快照漂移：' + row['path'])
    blob, command, code = git_blob(row['path'])
    same = blob == old.read_bytes()
    eol = not same and b'\r\n' not in blob and blob.replace(b'\n',b'\r\n') == old.read_bytes()
    require(hashlib.sha256(blob).hexdigest() == row['git_blob_sha256'] and (same or eol), 'Git原字节或精确EOL不同')
    require(row['git_relation'] == ('RAW_IDENTICAL' if same else 'GIT_LF_TO_RAW_CRLF'), '原关系标签不同')
    if row['path'] in static['source_sha256']:
        require(row['sha256'] == static['source_sha256'][row['path']], '静态哈希不同')
    sources.append({**row,'snapshot_after':rel(new),'git_native_command':command,'git_native_exit_code':code,'git_raw_same':same,'exact_git_lf_to_snapshot_crlf':eol,'live_source_consumed':False})
require(sum(r['git_raw_same'] for r in sources) == 32 and sum(r['exact_git_lf_to_snapshot_crlf'] for r in sources) == 6, '不是32RAW+6EOL')
require(frozen['source_sha256'] == {r['path']:r['sha256'] for r in rows}, 'freeze与实际38不同')
require(before['frozen14_sha256'] == after['frozen14_sha256'] == frozen['frozen14_sha256'] and len(frozen['frozen14_sha256']) == 14, '原14绑定不同')
for name, expected in frozen['frozen14_sha256'].items():
    require(later[name]['sha256'] == expected, '原14快照漂移')
profile = read(ROOT / later['board/s2b_inference_platform.json']['snapshot'])
require(profile['version'] == 's2b-inference-platform/0.1.6' and profile['clock_hz'] == 50000000 and profile['visibility_default'] == 0 and profile['vivado_part'] == 'xc7z020clg400-2', 'profile不同')
save(REPORT / 's6_collection_source_binding.json', {'status':'S6_ACTUAL38_BEFORE_AFTER_IDENTICAL_GIT_B0_BOUND','source_commit':BASELINE,'source_before':binding(PRE / 'source_before.json'),'source_after':binding(PRE / 'source_after.json'),'static_actual':binding(CACHE / 'static_actual_closed.json'),'source_freeze':binding(freeze),'source_count':38,'platform_static_source_count':31,'extra_bindings':extra,'sources':sources,'git_raw_same_count':32,'exact_eol_count':6,'frozen14_unchanged':True,'frozen14_sha256':frozen['frozen14_sha256'],'live_source_consumed':False,'note':'源码标识 path 不代表消费 live 文件；快照和明确 Git b0 对象是本次依据。freeze 历史提交及 G2 NOT_RUN 原样保留，不以字段覆盖实际综合源码基线。'})

native_root = mkdir_new(REPORT / 'native_jobs')
run_root = exact(PROJECT / 's2b_inference_candidate.runs','directory')
directories = sorted(p for p in run_root.iterdir() if p.is_dir() and p.name != '.jobs')
require(len(directories) == 5, '实际job数不同')
mapping, jobs = [], []
for directory in directories:
    target = mkdir_new(native_root / ('wrapper_native_s6_r01' if directory.name == 'synth_1' else directory.name))
    log = exact(directory / 'runme.log').read_text(encoding='utf-8')
    require('synth_design completed successfully' in log and '0 Critical Warnings and 0 Errors encountered' in log, '原生综合未完成')
    require((directory / '__synthesis_is_complete__').is_file() and (directory / '.vivado.end.rst').is_file() and not (directory / '.vivado.error.rst').exists(), '原生marker不同')
    for path in sorted(directory.iterdir()):
        if path.is_file() and (path.suffix in ('.tcl','.log','.jou','.vds','.xdc','.rpt','.rst','.js','.sh','.bat','.xml') or path.name in ('htr.txt','__synthesis_is_complete__')):
            mapping.append(rawcopy(path,target / path.name))
    process = ET.fromstring((directory / '.vivado.begin.rst').read_bytes()).find('Process')
    require(process is not None, 'launcher缺失')
    elapsed = re.search(r'synth_design:.*?elapsed = (\d+):(\d+):(\d+)',log)
    require(elapsed, '综合耗时缺失')
    start, end = first(r'Start of session at:\s*([^\r\n]+)',log), first(r'Exiting Vivado at ([^\r\n]+)',log).removesuffix('...')
    diag = re.findall(r'(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered',log)
    jobs.append({'run':directory.name,'saved_directory':rel(target),'status':'NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS','actual_vivado_job_pid':int(first(r'Process ID\s*:\s*(\d+)',log)),'launcher_pid_from_begin_rst':int(process.attrib['Pid']),'launcher_command':process.attrib['Command'],'session_start_local':start,'session_end_local':end,'timezone_context':'UTC+8','session_wall_seconds_from_native_timestamps':(datetime.strptime(end,'%a %b %d %H:%M:%S %Y')-datetime.strptime(start,'%a %b %d %H:%M:%S %Y')).total_seconds(),'synth_design_elapsed_seconds':int(elapsed[1])*3600+int(elapsed[2])*60+int(elapsed[3]),'reported_single_process_peak_mb':max(map(float,re.findall(r'peak = ([0-9.]+)',log))),'peak_unit':'Vivado日志MB；单进程，非进程树峰','final_diagnostics':dict(zip(('infos','warnings','critical_warnings','errors'),map(int,diag[-1]))),'raw_os_process_exit_code':None,'os_exit_code_reason':'未直接捕获OS子进程退出码；完成依据为原生日志/marker/同次nativewait0/实际run100%。'})
infer = next(j for j in jobs if j['run'] == 's2b_inference_infer_0_synth_1')
require(infer['synth_design_elapsed_seconds'] == 164 and infer['reported_single_process_peak_mb'] == 2175.812, '核心实际值不同')
single_peak = max(j['reported_single_process_peak_mb'] for j in jobs)
require(single_peak == 2210.242, '最大单进程峰不同')
tcl = (native_root / 's2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8')
block = first(r'read_verilog -library xil_defaultlib -sv \{([^}]+)\}',tcl)
compiled = [Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
require(len(compiled) == len(set(compiled)) == 18 and set(compiled) == set(profile['rtl_sources']), '实际编译18不同')
generated = mkdir_new(REPORT / 'generated_inputs')
genroot = exact(PROJECT / 's2b_inference_candidate.gen/sources_1/bd/s2b_inference','directory')
constraints = sorted(genroot.rglob('*.xdc')) + sorted(run_root.rglob('*_propImpl.xdc'))
require(len(constraints) == 7 and len({p.name for p in constraints}) == 7, '生成约束实际数不同')
for path in constraints:
    mapping.append(rawcopy(path,generated / path.name))
wrapper = exact(PROJECT / 's2b_inference_candidate.srcs/sources_1/imports/hdl/s2b_inference_wrapper.v')
genwrapper = exact(genroot / 'hdl/s2b_inference_wrapper.v')
require(sha(wrapper) == sha(genwrapper), 'import/generated wrapper不同')
mapping.append(rawcopy(wrapper,generated / wrapper.name))
for path in (exact(genroot / 'synth/s2b_inference.v'),exact(genroot / 'ip/s2b_inference_infer_0/synth/s2b_inference_infer_0.sv')):
    mapping.append(rawcopy(path,generated / path.name))
require(wrapper.as_posix() in (native_root / 'wrapper_native_s6_r01/s2b_inference_wrapper.tcl').read_text(encoding='utf-8'), '真实wrapper编译路径缺失')
require('wrapper ' + wrapper.as_posix() + ' top s2b_inference_wrapper' in (REPORT / 'setup_synthesis.tcldict').read_text(encoding='utf-8'), 'setup唯一wrapper不同')
save(REPORT / 's6_collection_native_mapping.json', {'files':mapping,'jobs':jobs,'native_job_count':5,'native_raw_copy_count':len(mapping),'native_raw_copy_bytes':sum(r['bytes'] for r in mapping),'native_vds_count':sum(Path(r['saved_path']).suffix=='.vds' for r in mapping),'actual_compiled_rtl_sources':compiled,'actual_compiled_source_count':18,'actual_compiled_source_snapshots':[{'source_identifier':name,'source_snapshot':later[name]['snapshot'],'sha256':later[name]['sha256']} for name in compiled],'source_binding':rel(REPORT / 's6_collection_source_binding.json'),'wrapper_import':binding(wrapper),'wrapper_generated_original':binding(genwrapper),'unique_registered_wrapper_count_from_setup':1,'generated_wrapper_raw_equals_imported':True,'single_process_peak_max_mb':single_peak,'process_tree_peak_memory_bytes':None,'excluded_cache_policy':'仅必要native脚本/日志/VDS/marker/生成约束；DCP/PB/WDF/obj_dir/EXE/cache/整工程或旧SDK不复制。VDS是本次文本日志。'})

mcpdir = mkdir_new(REPORT / 'mcp_closed')
for name in sorted(p.name for p in CACHE.glob('mcp_*.json')) + ['resource_preflight.json','resource_during_synthesis_01.json','static_actual_closed.json','source_preflight.py','close_source_and_log.py','root_session_snapshot_binding.json','source_before.native.json','source_before.stdout.log','source_before.stderr.log','source_after.native.json','source_after.stdout.log','source_after.stderr.log']:
    rawcopy(CACHE / name,mcpdir / name)
history = [h for b in read(mcpdir / 'mcp_history.json')['content'] if b['type']=='text' for h in json.loads(b['text']).get('history',[])]
require([h['id'] for h in history] == list(range(1,10)), '实际history不是1–9')
paired = []
for label,item in zip(('source','builder','setup','launch','wait','open','reports','query_xdc','close'),history):
    call = read(mcpdir / ('mcp_' + label + '.json'))
    require(call['input']['command'] == item['command'], 'MCP/history命令不匹配')
    if label=='wait':
        require(call['result'].get('isError') is True and '300s' in call['result']['content'][0]['text'] and item['code']==0 and item['elapsed']==301.363,'客户端timeout/native事实不同')
    else:
        require(json.loads(call['result']['content'][0]['text'])['exit_code']==item['code'],'MCP/native码不同')
    paired.append({'label':label,'client_record':binding(mcpdir / ('mcp_'+label+'.json')),'native_history':item,'client_wall_ms':call.get('wall_ms')})
byid = {h['id']:h for h in history}
states = byid[8]['output']
require(states.count('status {synth_design Complete!} progress 100%')==5 and states.count('status {Not started} progress 0%')==5 and 'clock_period 20.000' in states,'真实run状态不同')
require('[Sun Oct 11 19:31:44 2026] Launched synth_1' in byid[4]['output'] and '[Sun Oct 11 19:37:30 2026] synth_1 finished' in byid[5]['output'],'launcher时刻不同')
products = (REPORT / 'products.tcldict').read_text(encoding='utf-8')
require('status FAIL code 0 raw PRODUCTS:OK' in products and 'WARNING emitted=-8 exported=2' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products,'products原FAIL不同')
save(REPORT / 's6_collection_mcp_history_binding.json', {'status':'CLOSED_HISTORY1_TO9_CLIENT_NATIVE_BOUND','paired_calls':paired,'mcp_execute_calls':9,'mcp_history_calls':1,'execute_plus_history_calls':10,'post_timeout_status_queries':1,'session_start_calls':1,'todo_update_calls':1,'all_host_tool_calls':None,'client_wait_is_error':True,'client_wait_timeout_seconds':300,'client_wait_wall_ms':read(mcpdir / 'mcp_wait.json')['wall_ms'],'native_wait_exit_code':0,'native_wait_elapsed_seconds':301.363,'launch_timestamp_local':'2026-10-11T19:31:44+08:00','native_wrapper_exit_local':'2026-10-11T19:37:26+08:00','launcher_finished_local':'2026-10-11T19:37:30+08:00','launch_to_native_wrapper_exit_seconds':342,'launch_to_launcher_finished_seconds':346,'whole_builder_native_exit_code':1,'whole_builder_native_elapsed_seconds':byid[2]['elapsed'],'products_native_exit_code':0,'products_capture_exit_code':1,'products_warning_counter_before':9,'products_warning_counter_after':1,'products_warning_emitted_delta':-8,'products_warning_exported_count':2,'products_repeated':False,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'implementation_started':False,'implementation_strategy_list_only':states.split(' impl_strategies ',1)[1],'source_json_serialization_failure':False})

prior = exact(ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01/s5_collection_delivery_manifest_r02.json')
old_classifier = exact(ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01/s5_collection_classify_s5_sta.py')
classifier_path = code_dir / 'classify_s6_sta.py'
rawcopy(old_classifier,classifier_path)
save(REPORT / 's6_collection_sta_checker_binding.json', {'requested_identifier':'verification/check_s2b_inference_sta.py','requested_identifier_status':'TASK_MESSAGE_PATH_ERROR_NOT_PRESENT_NOT_RUN','requested_native_exit_code':None,'actual_classifier_original':binding(old_classifier),'actual_classifier_snapshot':binding(classifier_path),'reuse':'精确复用S5已封存分类器，S6参数为本轮timing_summary_synth.rpt与新输出目标；脚本内历史S5注释原字节保留。'})
classifier = run_closed([sys.executable,'-B',str(classifier_path),'--report',str(REPORT / 'timing_summary_synth.rpt'),'--result',str(REPORT / 's6_collection_sta_result.json')],'s6_collection_sta')
require(classifier['native_exit_code']==2,'STA分类不是实际2')
copy_closed('s6_collection_sta')
sta = read(REPORT / 's6_collection_sta_result.json')
timing = sta['timing']
require((timing['wns_ns'],timing['tns_ns'],timing['setup_failing_endpoints'],timing['setup_total_endpoints'],timing['whs_ns'],timing['ths_ns'],timing['wpws_ns'],timing['tpws_ns'])==(-11.799,-3819.396,736,14767,0.037,0.0,8.870,0.0) and not any(sta['check_timing'].values()),'STA实际值不同')
util = (REPORT / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
resources = {k:int(first(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util)) for k,label in (('lut','Slice LUTs*'),('ff','Slice Registers'),('bram','Block RAM Tile'),('dsp','DSPs'),('latch','Register as Latch'))}
require(resources=={'lut':20078,'ff':3973,'bram':32,'dsp':145,'latch':0},'资源不同')
worst = (REPORT / 'timing_worst_synth.rpt').read_text(encoding='utf-8')
w = {'source':first(r'^\s*Source:\s*(\S+)',worst),'destination':first(r'^\s*Destination:\s*(\S+)',worst),'logic_levels':int(first(r'^\s*Logic Levels:\s*(\d+)',worst)),'carry4':int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)',worst)),'dsp48e1':int(first(r'^\s*Logic Levels:.*?DSP48E1=(\d+)',worst)),'data_path_delay_ns':float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns',worst)),'logic_delay_ns':float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns',worst)),'route_delay_ns':float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns',worst))}
require(w['source'].endswith('u_route_engine/source0_end_latched_reg[6]/C') and w['destination'].endswith('u_route_engine/output_address_latched_reg[0]/CE') and (w['logic_levels'],w['carry4'],w['dsp48e1'],w['data_path_delay_ns'],w['logic_delay_ns'],w['route_delay_ns'])==(38,20,3,31.187,19.071,12.116),'最差路径不同')
xdc = (REPORT / 'constraints_synth.xdc').read_text(encoding='utf-8')
exceptions = re.findall(r'current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)',xdc)
require(len(exceptions)==2 and all('rst_fclk0/U0/EXT_LPF/' in scope and 'syncstages_ff_reg[0]' in command for scope,command in exceptions),'实际resetCDC例外不同')
require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc and 'No valid timing exceptions found.' in (REPORT / 'exceptions_synth.rpt').read_text(encoding='utf-8'),'约束报告不同')
save(REPORT / 's6_collection_constraints_binding.json', {'clock':sta['clock'],'input_jitter_ns':0.6,'check_timing':sta['check_timing'],'exported_reset_cdc_false_paths':[{'scope':scope,'command':command} for scope,command in exceptions],'exported_false_path_count':2,'report_exceptions_raw_statement':'No valid timing exceptions found.','interpretation':'check_timing零计数仅为本次无内部漏约束；write_xdc两个scoped resetCDC false_path与原report_exceptions文字分别保留，不称零例外或时序收敛。'})
method = (REPORT / 'methodology_synth.rpt').read_text(encoding='utf-8')
drc = (REPORT / 'drc_synth.rpt').read_text(encoding='utf-8')
require(int(first(r'Checks found:\s*(\d+)',method))==736 and '| TIMING-16 | Warning' in method,'methodology不同')
drc_rules = [{'rule':a,'severity':b,'description':c.strip(),'count':int(d)} for a,b,c,d in re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|([^|]+)\|\s*(\d+)\s*\|',drc,re.M)]
require(sum(r['count'] for r in drc_rules)==388,'DRC实际数不同')

old_xsa = exact(ROOT / 'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa')
new_xsa = exact(REPORT / 's2b_inference_no_bit.xsa')
members = []
psroot = exact(genroot / 'ip/s2b_inference_ps7_0','directory')
with zipfile.ZipFile(old_xsa) as old, zipfile.ZipFile(new_xsa) as new:
    require(not any(n.endswith('.bit') for n in new.namelist()),'XSA意外含bit')
    for name in ('ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h','s2b_inference.hwh'):
        a,b = old.read(name),new.read(name)
        require(zlib.crc32(a)==old.getinfo(name).CRC and zlib.crc32(b)==new.getinfo(name).CRC,'XSA CRC不同')
        row = {'member':name,'old_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),'old_bytes':len(a),'new_bytes':len(b),'raw_equal':a==b,'old_crc32':old.getinfo(name).CRC,'new_crc32':new.getinfo(name).CRC}
        if name.startswith('ps7_init'):
            require((psroot / name).read_bytes()==b,'PSinit生成原件与XSA不同')
            row['generated_original']=binding(psroot / name)
            row['saved_copy']=rawcopy(psroot / name,generated / name)
        members.append(row)
    require(all(r['raw_equal'] for r in members[:6]) and not members[6]['raw_equal'],'PSinit/HWH关系不同')
    metadata={'xsa_json':json.loads(new.read('xsa.json')),'hwdef_xml':new.read('hwdef.xml').decode('utf-8'),'xsa_xml':new.read('xsa.xml').decode('utf-8')}
    require(metadata['xsa_json']['platformState']=='pre_synth' and metadata['xsa_json']['devices'][0]['part']['name']=='xc7z020clg400-2','XSA元数据不同')
    for name in ('hwdef.xml','xsa.json','xsa.xml','s2b_inference.hwh'):
        allowed_target(generated / name)
        with (generated / name).open('xb') as dst:
            dst.write(new.read(name))
pstcl = (generated / 'ps7_init.tcl').read_text(encoding='utf-8')
post=[]
for revision in ('1_0','2_0','3_0'):
    body=first(r'proc ps7_post_config_'+revision+r' \{\} \{([^}]+)\}',pstcl)
    operations=[line.strip() for line in body.splitlines() if line.strip()]
    require(operations==['mwr -force 0XF8000008 0x0000DF0D','mask_write 0XF8000900 0x0000000F 0x0000000F','mask_write 0XF8000240 0xFFFFFFFF 0x00000000','mwr -force 0XF8000004 0x0000767B'],'生成postconfig表不同')
    post.append({'silicon_revision':revision,'official_generated_procedure':'ps7_post_config_'+revision,'operations':operations})
save(REPORT / 's6_collection_xsa_member_comparison.json', {'status':'SIX_PSINIT_BYTES_SAME_T13_AND_GENERATED_HWH_CHANGED_NO_BIT','old_xsa':binding(old_xsa),'new_xsa':binding(new_xsa),'members':members,'official_generated_postconfig_tables':post,'xsa_metadata':metadata,'elf_runtime_compatibility':'NOT_APPROVED','note':'六成员相等仅证明成员原字节；不批准旧BSP/ELF整体兼容。生成表未调用；XSA为pre_synth无bit，后续综合STA单独记录。'})

blob,command,code = git_blob('verification/check_stage_delivery.py')
checker = REPORT / 's6_collection_stage_checker_snapshot.py'
allowed_target(checker)
with checker.open('xb') as dst:
    dst.write(blob)
save(REPORT / 's6_collection_stage_checker_binding.json', {'source_commit':BASELINE,'original_identifier':'verification/check_stage_delivery.py','snapshot':binding(checker),'git_native_command':command,'git_native_exit_code':code,'live_checker_consumed':False})
interfaces=read(prior)['interfaces']
for item in interfaces:
    require(sha(ROOT / item['path'])==item['sha256'],'正式接口文档漂移')
externals=[{'path':rel(p),'role':'input'} for p in (freeze,old_xsa,prior,old_classifier,PRE / 'source_before.json',PRE / 'source_after.json')]
externals += [{'path':r['snapshot'],'role':'source'} for r in rows] + [{'path':r['snapshot'],'role':'source'} for r in after['source_files']]
preflight = json.loads(read(mcpdir / 'resource_preflight.json')['native_query']['output'])
during = json.loads(read(mcpdir / 'resource_during_synthesis_01.json')['output'])
limitations=['仅收集S6已结束真实综合失败；独立证据审查尚未执行，G3/G4/G5未通过。','源码b0闭包38=31static+7额外；32GitRAW+6精确LF到CRLF，前后快照一致，原14不变，未消费live源码。','freeze含历史d5提交/G2 NOT_RUN原样保留；本次实际运行基线b0另由Git/快照绑定。','builder1/products native0 capture1，WARNING9到1、emitted−8/exported2的原FAIL保留，未重跑products。','MCP客户端wait300秒超时/isError与同次nativewait0/301.363秒区分；launch至native退出342秒、launcherfinished346秒分别记。','infer synth164秒/单进程峰2175.812MB；五job最大单进程PS7 2210.242MB；root累计峰不能当进程树峰，全树峰未测。','五jobOS子进程退出码未直接捕获为null；原生日志、markers、historywait0与100%状态支持完成。','50MHz综合态STA FAIL_TIMING，WNS−11.799/TNS−3819.396，736/14767setup失败；ROUTE最差38级/20CARRY4/3DSP，31.187ns。','check_timing均0仅为无内部漏约束；write_xdc两个resetCDC false_path与report_exceptions原No valid文字分别保留。','六PSinit同T13及本次生成，HWH变化；XSA pre_synth无bit；旧BSP/ELF整体兼容仍未批准。','指定verification/check_s2b_inference_sta.py路径不存在，为任务消息路径错误/NOT_RUN/null，按总控批准精确复用S5分类器在S6报告实际返回2。','辅助日志UTF8预览失败仅获得宿主1，子进程原生码未独立捕获为null；无完整stdout/stderr原字节。root封存日志原字节保全，ASCII peak独立提取。','实现/postroute/bit/cache/model/109/1000次/BOARD均NOT_RUN；物理候选0.1.1未冻结，visibility0。','9execute+1history另计1status/1sessionstart/1todo；全部host调用、collector峰及进程树峰未测；资源前检和期间采样不是峰值。','不复制DCP/cache/obj_dir/EXE/整SDK/未消费旧测试资料，不重型运行、不调用ROSS、不触碰设备。','CHECKS_OK仅表示包装/哈希检查，通过的失败证据包不能替代STA、G2或物理验收。']
summary={'status':'COLLECTED_S6_FAIL_TIMING_PENDING_INDEPENDENT_EVIDENCE_REVIEW','source_commit':BASELINE,'source_count':38,'platform_static_source_count':31,'extra_binding_count':7,'compiled_rtl_count':18,'profile_version':profile['version'],'physical_interface':'s2b-physical-candidate/0.1.1','visibility':0,'original_raw_file_count':55,'original_raw_bytes':sum(r['bytes'] for r in original_check()),'original_raw_unchanged':True,'native_raw_copy_count':len(mapping),'native_raw_copy_bytes':sum(r['bytes'] for r in mapping),'native_job_count':5,'native_vds_count':5,'native_wait_exit_code':0,'native_wait_elapsed_seconds':301.363,'mcp_wait_timeout':True,'launch_to_native_wrapper_exit_seconds':342,'launch_to_launcher_finished_seconds':346,'native_report_exit_code':byid[7]['code'],'native_report_elapsed_seconds':byid[7]['elapsed'],'native_classifier_exit_code':2,'timing':timing,'check_timing':sta['check_timing'],'resources':resources,'worst_path':w,'methodology':{'checks':736,'rule':'TIMING-16','severity':'Warning'},'drc':{'checks':388,'rules':drc_rules},'exported_reset_cdc_false_path_count':2,'external_inputs':externals,'resource_preflight':binding(mcpdir / 'resource_preflight.json'),'resource_during':binding(mcpdir / 'resource_during_synthesis_01.json'),'preflight_disk_free_bytes':preflight['c_free_bytes'],'preflight_memory_free_kib':preflight['free_physical_memory_kib'],'during_memory_free_kib':during['free_kib'],'infer_synth_elapsed_seconds':164,'infer_single_process_peak_mb':2175.812,'single_process_peak_max_mb':single_peak,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'threads':1,'jobs':1,'synthesis_execution_count':1,'products_execution_count':1,'mcp_execute_calls':9,'mcp_history_calls':1,'post_timeout_status_queries':1,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'limitations':limitations,'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'collector_elapsed_so_far_seconds':time.monotonic()-started}
save(REPORT / 's6_collection_summary.json',summary)
checks=[{'name':'S6实际38快照及Gitb0核验','status':'PASS','command':' '.join(sources[0]['git_native_command']),'exit_code':0,'reason':'38条真实Git命令/码在source_binding；32RAW+6精确EOL，原14未变。'},{'name':'五个原生综合完成','status':'PASS','command':byid[5]['command'],'exit_code':0,'reason':'history5原生0/301.363秒，客户端超时单独记录。'},{'name':'实际综合态STA报告生成','status':'PASS','command':byid[7]['command'],'exit_code':0},{'name':'50MHz综合态STA分类','status':'FAIL','command':' '.join(classifier['command']),'exit_code':2,'reason':'WNS−11.799/TNS−3819.396，736/14767setup失败，非postroute。'},{'name':'builder与products捕获原失败','status':'FAIL','command':byid[2]['command'],'exit_code':1,'reason':'builder1/products native0 capture1，WARNING9到1保留原FAIL。'}]
for name in ('S6独立证据准确性审查','实现及postroute','bitstream生成','板上cache probe','板上模型及109样本','1000次板上任务','BOARD及G3验收'):
    checks.append({'name':name,'status':'NOT_RUN','command':None,'exit_code':None,'reason':'本Collector仅收集关闭原件，未执行该项。'})
manifest={'schema_version':1,'stage':'2B','task_id':'S2B-T17','run_id':'s6_platform_20261011_r01','source_commit':BASELINE,'evidence_dir':rel(REPORT),'interfaces':interfaces,'tool_versions':{'python':sys.version,'Vivado':'2026.1 Build6511674 原报告/日志','part':profile['vivado_part'],'profile':profile['version']},'files':manifest_files(externals),'checks':checks,'limitations':limitations}
manifest_path=REPORT / 's6_collection_delivery_manifest_r01.json'
save(manifest_path,manifest)
results={mode:run_closed([sys.executable,'-B',str(checker),'--mode',mode,'--manifest',str(manifest_path),'--project-root',str(ROOT)],'s6_collection_'+mode+'_r01') for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in results.items()}=={'evidence':0,'inputs':2},'包装实际码不同')
for mode in results:
    copy_closed('s6_collection_'+mode+'_r01')
save(REPORT / 's6_collection_packaging_r01.json',{'status':'EVIDENCE_PACKAGING_OK_INPUTS_ACTUAL_FAIL','checks':results,'policy':'evidence0仅包装；inputs2含未冻结/实际FAIL/NOT_RUN，不改门禁。'})
original_check()
print(json.dumps({'status':summary['status'],'original_files':55,'native_copies':len(mapping),'source_count':38,'compiled_rtl_count':18,'codes':{'sta':2,'evidence':0,'inputs':2},'collector_elapsed_seconds':time.monotonic()-started},ensure_ascii=False))
