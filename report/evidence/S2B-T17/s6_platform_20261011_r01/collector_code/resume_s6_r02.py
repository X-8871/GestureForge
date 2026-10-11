"""在首收集失败后只增续收集，兼容本轮原始和包装 MCP 结果。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
import re, zipfile, zlib

def first(pattern,text):
    """要求实际报告包含定位字段。"""
    values=re.findall(pattern,text,re.M)
    require(values,'缺少字段：'+pattern)
    return values[0].strip()

started=time.monotonic()
original_check()
require(read(REPORT / 's6_collection_collector.native.json')['native_exit_code']==1,'首次失败码不同')
code_dir=exact(REPORT / 'collector_code','directory')
for name in ('resume_s6_r02.py','run_resume_s6_r02.py','finalize_s6_r02.py','run_finalization_s6_r02.py'):
    rawcopy(WORK / name,code_dir / name)
source=read(REPORT / 's6_collection_source_binding.json')
native=read(REPORT / 's6_collection_native_mapping.json')
require(source['source_count']==38 and native['native_raw_copy_count']==94 and native['native_vds_count']==5,'已完成部分计数不同')
rows=read(PRE / 'source_before.json')['source_files']
after=read(PRE / 'source_after.json')
later={r['path']:r for r in after['source_files']}
freeze=exact(ROOT / after['source_freeze'])
sources=source['sources']
profile=read(ROOT / later['board/s2b_inference_platform.json']['snapshot'])
root_peak=read(REPORT / 's6_collection_root_log_binding.json')['root_session_cumulative_peak_mb']
generated=exact(REPORT / 'generated_inputs','directory')
genroot=exact(PROJECT / 's2b_inference_candidate.gen/sources_1/bd/s2b_inference','directory')
mcpdir=exact(REPORT / 'mcp_closed','directory')
rawcopy(CACHE / 'owned_idle_session_before_stop.json',mcpdir / 'owned_idle_session_before_stop.json')
history=[h for b in read(mcpdir / 'mcp_history.json')['content'] if b['type']=='text' for h in json.loads(b['text']).get('history',[])]
require([h['id'] for h in history]==list(range(1,10)),'实际history不是1–9')
paired=[]
for label,item in zip(('source','builder','setup','launch','wait','open','reports','query_xdc','close'),history):
    call=read(mcpdir / ('mcp_'+label+'.json'))
    wrapped='input' in call and 'result' in call
    if wrapped:
        require(call['input']['command']==item['command'],'MCP/history命令不同')
        result=call['result']
    else:
        require(label in ('source','builder') and 'content' in call,'未知MCP结构')
        result=call
    if label=='wait':
        require(result.get('isError') is True and '300s' in result['content'][0]['text'] and item['code']==0 and item['elapsed']==301.363,'客户端timeout/native不同')
    else:
        require(json.loads(result['content'][0]['text'])['exit_code']==item['code'],'MCP/native码不同')
    paired.append({'label':label,'client_record':binding(mcpdir / ('mcp_'+label+'.json')),'native_history':item,'client_wall_ms':call.get('wall_ms'),'saved_client_schema':'INPUT_RESULT_WRAPPER' if wrapped else 'RAW_CALL_TOOL_RESULT','client_input_captured':wrapped,'command_binding_basis':'已捕获input与同次history精确相等' if wrapped else '原client结果未保存input，实际命令由同会话关闭history给出；不伪称恢复client input。'})
byid={h['id']:h for h in history}
states=byid[8]['output']
require(states.count('status {synth_design Complete!} progress 100%')==5 and states.count('status {Not started} progress 0%')==5 and 'clock_period 20.000' in states,'真实run状态不同')
require('[Sun Oct 11 19:31:44 2026] Launched synth_1' in byid[4]['output'] and '[Sun Oct 11 19:37:30 2026] synth_1 finished' in byid[5]['output'],'launcher时刻不同')
products=(REPORT / 'products.tcldict').read_text(encoding='utf-8')
require('status FAIL code 0 raw PRODUCTS:OK' in products and 'WARNING emitted=-8 exported=2' in products and 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products,'products原FAIL不同')
save(REPORT / 's6_collection_mcp_history_binding.json',{'status':'CLOSED_HISTORY1_TO9_CLIENT_NATIVE_BOUND','paired_calls':paired,'mcp_execute_calls':9,'mcp_history_calls':1,'execute_plus_history_calls':10,'post_timeout_status_queries':1,'session_start_calls':1,'todo_update_calls':1,'all_host_tool_calls':None,'client_wait_is_error':True,'client_wait_timeout_seconds':300,'client_wait_wall_ms':read(mcpdir / 'mcp_wait.json')['wall_ms'],'native_wait_exit_code':0,'native_wait_elapsed_seconds':301.363,'launch_timestamp_local':'2026-10-11T19:31:44+08:00','native_wrapper_exit_local':'2026-10-11T19:37:26+08:00','launcher_finished_local':'2026-10-11T19:37:30+08:00','launch_to_native_wrapper_exit_seconds':342,'launch_to_launcher_finished_seconds':346,'whole_builder_native_exit_code':1,'whole_builder_native_elapsed_seconds':byid[2]['elapsed'],'products_native_exit_code':0,'products_capture_exit_code':1,'products_warning_counter_before':9,'products_warning_counter_after':1,'products_warning_emitted_delta':-8,'products_warning_exported_count':2,'products_repeated':False,'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'implementation_started':False,'implementation_strategy_list_only':states.split(' impl_strategies ',1)[1],'client_source_and_builder_input_not_captured':True,'source_json_serialization_failure':False})
owned=read(mcpdir / 'owned_idle_session_before_stop.json')
identity=json.loads(owned['output'])
stop=read(mcpdir / 'mcp_owned_idle_session_stop.json')
stopped=json.loads(stop['content'][0]['text'])
require(owned['exit_code']==0 and identity['ProcessId']==27932 and identity['ParentProcessId']==34492 and stopped['status']=='success' and stopped['message']=='Vivado closed','闲置session关闭证据不同')
save(REPORT / 's6_collection_owned_session_lifecycle.json',{'status':'PROJECT_CLOSED_THEN_OWNED_IDLE_SESSION_STOPPED','project_close_native_code':byid[9]['code'],'project_close_native_history':byid[9],'idle_identity_query':binding(mcpdir / 'owned_idle_session_before_stop.json'),'idle_identity':identity,'stop_result':binding(mcpdir / 'mcp_owned_idle_session_stop.json'),'stop_native_os_exit_code':None,'stop_result_status':'success','stop_is_design_execute':False,'immutable_log_predates_stop':True,'active_log_consumed':False,'post_stop_process_absence_raw_captured_in_this_package':False,'post_stop_process_absence_note':'总控另报告19:48:14 CIM宿主0/PID不存在，但此Collector未获得对应原始独立文件，未伪造绑定或现场查询。'})

prior=exact(ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01/s5_collection_delivery_manifest_r02.json')
old_classifier=exact(ROOT / 'report/evidence/S2B-T17/s5_platform_20261011_r01/s5_collection_classify_s5_sta.py')
classifier_path=code_dir / 'classify_s6_sta.py'
rawcopy(old_classifier,classifier_path)
save(REPORT / 's6_collection_sta_checker_binding.json',{'requested_identifier':'verification/check_s2b_inference_sta.py','requested_identifier_status':'TASK_MESSAGE_PATH_ERROR_NOT_PRESENT_NOT_RUN','requested_native_exit_code':None,'actual_classifier_original':binding(old_classifier),'actual_classifier_snapshot':binding(classifier_path),'reuse':'精确复用S5封存分类器，参数为S6报告和新输出目标，脚本历史S5注释原字节保留。'})
classifier=run_closed([sys.executable,'-B',str(classifier_path),'--report',str(REPORT / 'timing_summary_synth.rpt'),'--result',str(REPORT / 's6_collection_sta_result.json')],'s6_collection_sta')
require(classifier['native_exit_code']==2,'STA分类不是实际2')
copy_closed('s6_collection_sta')
sta=read(REPORT / 's6_collection_sta_result.json')
timing=sta['timing']
require((timing['wns_ns'],timing['tns_ns'],timing['setup_failing_endpoints'],timing['setup_total_endpoints'],timing['whs_ns'],timing['ths_ns'],timing['wpws_ns'],timing['tpws_ns'])==(-11.799,-3819.396,736,14767,0.037,0.0,8.870,0.0) and not any(sta['check_timing'].values()),'STA实际值不同')
util=(REPORT / 'utilization_flat_synth.rpt').read_text(encoding='utf-8')
resources={k:int(first(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',util)) for k,label in (('lut','Slice LUTs*'),('ff','Slice Registers'),('bram','Block RAM Tile'),('dsp','DSPs'),('latch','Register as Latch'))}
require(resources=={'lut':20078,'ff':3973,'bram':32,'dsp':145,'latch':0},'资源不同')
worst=(REPORT / 'timing_worst_synth.rpt').read_text(encoding='utf-8')
w={'source':first(r'^\s*Source:\s*(\S+)',worst),'destination':first(r'^\s*Destination:\s*(\S+)',worst),'logic_levels':int(first(r'^\s*Logic Levels:\s*(\d+)',worst)),'carry4':int(first(r'^\s*Logic Levels:.*?CARRY4=(\d+)',worst)),'dsp48e1':int(first(r'^\s*Logic Levels:.*?DSP48E1=(\d+)',worst)),'data_path_delay_ns':float(first(r'^\s*Data Path Delay:\s*([\d.]+)ns',worst)),'logic_delay_ns':float(first(r'^\s*Data Path Delay:.*?logic ([\d.]+)ns',worst)),'route_delay_ns':float(first(r'^\s*Data Path Delay:.*?route ([\d.]+)ns',worst))}
require(w['source'].endswith('u_route_engine/source0_end_latched_reg[6]/C') and w['destination'].endswith('u_route_engine/output_address_latched_reg[0]/CE') and (w['logic_levels'],w['carry4'],w['dsp48e1'],w['data_path_delay_ns'],w['logic_delay_ns'],w['route_delay_ns'])==(38,20,3,31.187,19.071,12.116),'最差路径不同')
xdc=(REPORT / 'constraints_synth.xdc').read_text(encoding='utf-8')
exceptions=re.findall(r'current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)',xdc)
require(len(exceptions)==2 and all('rst_fclk0/U0/EXT_LPF/' in scope and 'syncstages_ff_reg[0]' in command for scope,command in exceptions),'实际resetCDC例外不同')
require('create_clock -period 20.000 -name clk_fpga_0' in xdc and 'set_input_jitter clk_fpga_0 0.600' in xdc and 'No valid timing exceptions found.' in (REPORT / 'exceptions_synth.rpt').read_text(encoding='utf-8'),'约束报告不同')
save(REPORT / 's6_collection_constraints_binding.json',{'clock':sta['clock'],'input_jitter_ns':0.6,'check_timing':sta['check_timing'],'exported_reset_cdc_false_paths':[{'scope':scope,'command':command} for scope,command in exceptions],'exported_false_path_count':2,'report_exceptions_raw_statement':'No valid timing exceptions found.','interpretation':'check_timing零计数仅为无内部漏约束；两个scoped resetCDC例外与report_exceptions原文分别保留，不称零例外或时序收敛。'})
method=(REPORT / 'methodology_synth.rpt').read_text(encoding='utf-8')
drc=(REPORT / 'drc_synth.rpt').read_text(encoding='utf-8')
require(int(first(r'Checks found:\s*(\d+)',method))==736 and '| TIMING-16 | Warning' in method,'methodology不同')
drc_rules=[{'rule':a,'severity':b,'description':c.strip(),'count':int(d)} for a,b,c,d in re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(\w+)\s*\|([^|]+)\|\s*(\d+)\s*\|',drc,re.M)]
require(sum(r['count'] for r in drc_rules)==388,'DRC实际数不同')

old_xsa=exact(ROOT / 'report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa')
new_xsa=exact(REPORT / 's2b_inference_no_bit.xsa')
members=[]
psroot=exact(genroot / 'ip/s2b_inference_ps7_0','directory')
with zipfile.ZipFile(old_xsa) as old, zipfile.ZipFile(new_xsa) as new:
    require(not any(n.endswith('.bit') for n in new.namelist()),'XSA意外含bit')
    for name in ('ps7_init.c','ps7_init.h','ps7_init.html','ps7_init.tcl','ps7_init_gpl.c','ps7_init_gpl.h','s2b_inference.hwh'):
        a,b=old.read(name),new.read(name)
        require(zlib.crc32(a)==old.getinfo(name).CRC and zlib.crc32(b)==new.getinfo(name).CRC,'XSA CRC不同')
        row={'member':name,'old_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),'old_bytes':len(a),'new_bytes':len(b),'raw_equal':a==b,'old_crc32':old.getinfo(name).CRC,'new_crc32':new.getinfo(name).CRC}
        if name.startswith('ps7_init'):
            require((psroot / name).read_bytes()==b,'生成PSinit与XSA不同')
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
pstcl=(generated / 'ps7_init.tcl').read_text(encoding='utf-8')
post=[]
for revision in ('1_0','2_0','3_0'):
    body=first(r'proc ps7_post_config_'+revision+r' \{\} \{([^}]+)\}',pstcl)
    operations=[line.strip() for line in body.splitlines() if line.strip()]
    require(operations==['mwr -force 0XF8000008 0x0000DF0D','mask_write 0XF8000900 0x0000000F 0x0000000F','mask_write 0XF8000240 0xFFFFFFFF 0x00000000','mwr -force 0XF8000004 0x0000767B'],'生成postconfig表不同')
    post.append({'silicon_revision':revision,'official_generated_procedure':'ps7_post_config_'+revision,'operations':operations})
save(REPORT / 's6_collection_xsa_member_comparison.json',{'status':'SIX_PSINIT_BYTES_SAME_T13_AND_GENERATED_HWH_CHANGED_NO_BIT','old_xsa':binding(old_xsa),'new_xsa':binding(new_xsa),'members':members,'official_generated_postconfig_tables':post,'xsa_metadata':metadata,'elf_runtime_compatibility':'NOT_APPROVED','note':'六成员相等只证明成员字节，不批准旧BSP/ELF整体兼容；生成表未调用，XSA pre_synth无bit，STA单独记录。'})

blob,command,code=git_blob('verification/check_stage_delivery.py')
checker=REPORT / 's6_collection_stage_checker_snapshot.py'
allowed_target(checker)
with checker.open('xb') as dst:
    dst.write(blob)
save(REPORT / 's6_collection_stage_checker_binding.json',{'source_commit':BASELINE,'original_identifier':'verification/check_stage_delivery.py','snapshot':binding(checker),'git_native_command':command,'git_native_exit_code':code,'live_checker_consumed':False})
interfaces=read(prior)['interfaces']
for item in interfaces:
    require(sha(ROOT / item['path'])==item['sha256'],'正式接口文档漂移')
externals=[{'path':rel(p),'role':'input'} for p in (freeze,old_xsa,prior,old_classifier,PRE / 'source_before.json',PRE / 'source_after.json')]
externals += [{'path':r['snapshot'],'role':'source'} for r in rows] + [{'path':r['snapshot'],'role':'source'} for r in after['source_files']]
preflight=json.loads(read(mcpdir / 'resource_preflight.json')['native_query']['output'])
during=json.loads(read(mcpdir / 'resource_during_synthesis_01.json')['output'])
limitations=['仅收集S6已结束综合失败；独立证据审查尚未执行，G3/G4/G5未通过。','源码b0闭包38=31static+7额外；32GitRAW+6精确LF到CRLF，前后快照一致，原14不变；未消费live源码。','freeze含历史d5提交/G2 NOT_RUN原样保留，本次实际基线b0由Git及快照另绑。','builder1/products native0 capture1，WARNING9到1/emitted−8/exported2原FAIL保留，未重跑products。','客户端wait300s超时与nativewait0/301.363s分开；launch至native退出342s/launcherfinished346s分别记录。','infer synth164s/2175.812MB单进程，五job最大PS7 2210.242MB；root累计峰不是本次进程树峰，全树峰未测。','五jobOS子进程退出码未捕获为null；完成依据是日志、markers、historywait0与100%run状态。','50MHz STA FAIL_TIMING：WNS−11.799/TNS−3819.396，736/14767setup失败；ROUTE最差38级/20CARRY4/3DSP，31.187ns。','check_timing均0不代表零例外；两个resetCDC false_path与report_exceptions原No valid文字分别保留。','六PSinit与T13及本次生成相同，HWH变化；XSA pre_synth无bit；旧BSP/ELF整体兼容未批准。','指定STA脚本路径不存在，任务消息路径错误/NOT_RUN/null；总控批准复用已封存S5分类器，S6报告实际native2。','辅助UTF8预览宿主1，未独立捕获子进程native码为null、无完整原stdout/stderr；封存root原字节保全并仅提取ASCII数值。','首Collector实际native1/KeyError input，因source/builder原client返回无input包装；原脚本和关闭日志保留，r02续收集，命令由同次history1/2绑定，未伪称恢复clientinput。','实现/postroute/bit/cache/model/109/1000次/BOARD均NOT_RUN；物理候选0.1.1未冻结，visibility0。','9designexecute+1history，另计1status/1start/1todo及后续owned闲置stop；全部host调用、collector峰、进程树峰未测。','projectclosed/sourceafter/immutablelog在闲置sessionstop前封闭，stop不计designexecute；未消费active日志，未继承runtime预检为STA通过。','仅复制本轮消费原件，无DCP/cache/obj_dir/EXE/整SDK/历史测试复制；无重型运行/ROSS/设备操作。','CHECKS_OK仅包装通过，失败包通过包装不能代替STA、G2或物理验收。']
summary={'status':'COLLECTED_S6_FAIL_TIMING_PENDING_INDEPENDENT_EVIDENCE_REVIEW','source_commit':BASELINE,'source_count':38,'platform_static_source_count':31,'extra_binding_count':7,'compiled_rtl_count':18,'profile_version':profile['version'],'physical_interface':'s2b-physical-candidate/0.1.1','visibility':0,'original_raw_file_count':55,'original_raw_bytes':sum(r['bytes'] for r in original_check()),'original_raw_unchanged':True,'native_raw_copy_count':native['native_raw_copy_count'],'native_raw_copy_bytes':native['native_raw_copy_bytes'],'native_job_count':5,'native_vds_count':5,'native_wait_exit_code':0,'native_wait_elapsed_seconds':301.363,'mcp_wait_timeout':True,'launch_to_native_wrapper_exit_seconds':342,'launch_to_launcher_finished_seconds':346,'native_report_exit_code':byid[7]['code'],'native_report_elapsed_seconds':byid[7]['elapsed'],'native_classifier_exit_code':2,'timing':timing,'check_timing':sta['check_timing'],'resources':resources,'worst_path':w,'methodology':{'checks':736,'rule':'TIMING-16','severity':'Warning'},'drc':{'checks':388,'rules':drc_rules},'exported_reset_cdc_false_path_count':2,'external_inputs':externals,'resource_preflight':binding(mcpdir / 'resource_preflight.json'),'resource_during':binding(mcpdir / 'resource_during_synthesis_01.json'),'preflight_disk_free_bytes':preflight['c_free_bytes'],'preflight_memory_free_kib':preflight['free_physical_memory_kib'],'during_memory_free_kib':during['free_kib'],'infer_synth_elapsed_seconds':164,'infer_single_process_peak_mb':2175.812,'single_process_peak_max_mb':native['single_process_peak_max_mb'],'root_session_cumulative_peak_mb':root_peak,'root_peak_is_run_process_tree_peak':False,'threads':1,'jobs':1,'synthesis_execution_count':1,'products_execution_count':1,'mcp_execute_calls':9,'mcp_history_calls':1,'post_timeout_status_queries':1,'collector_attempt_count':2,'first_collector_native_exit_code':1,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'limitations':limitations,'created_at_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'collector_elapsed_so_far_seconds':time.monotonic()-started}
save(REPORT / 's6_collection_summary.json',summary)
checks=[{'name':'S6实际38快照及Gitb0核验','status':'PASS','command':' '.join(sources[0]['git_native_command']),'exit_code':0,'reason':'38实际Git命令/码在source_binding；32RAW+6精确EOL，原14不变。'},{'name':'五个原生综合完成','status':'PASS','command':byid[5]['command'],'exit_code':0,'reason':'history5原生0/301.363s，clienttimeout单独记录。'},{'name':'实际综合态STA报告生成','status':'PASS','command':byid[7]['command'],'exit_code':0},{'name':'50MHz综合态STA分类','status':'FAIL','command':' '.join(classifier['command']),'exit_code':2,'reason':'WNS−11.799/TNS−3819.396、736/14767setup失败，非postroute。'},{'name':'builder与products捕获原失败','status':'FAIL','command':byid[2]['command'],'exit_code':1,'reason':'builder1/products native0 capture1，WARNING9到1保留。'},{'name':'首版Collector原失败','status':'FAIL','command':' '.join(read(REPORT / 's6_collection_collector.native.json')['command']),'exit_code':1,'reason':'MCP原client结果无input导致KeyError；原件保留，r02续收集。'}]
for name in ('S6独立证据准确性审查','实现及postroute','bitstream生成','板上cache probe','板上模型及109样本','1000次板上任务','BOARD及G3验收'):
    checks.append({'name':name,'status':'NOT_RUN','command':None,'exit_code':None,'reason':'本Collector仅收集关闭原件，未执行该项。'})
manifest={'schema_version':1,'stage':'2B','task_id':'S2B-T17','run_id':'s6_platform_20261011_r01','source_commit':BASELINE,'evidence_dir':rel(REPORT),'interfaces':interfaces,'tool_versions':{'python':sys.version,'Vivado':'2026.1 Build6511674 原报告/日志','part':profile['vivado_part'],'profile':profile['version']},'files':manifest_files(externals),'checks':checks,'limitations':limitations}
manifest_path=REPORT / 's6_collection_delivery_manifest_r01.json'
save(manifest_path,manifest)
results={mode:run_closed([sys.executable,'-B',str(checker),'--mode',mode,'--manifest',str(manifest_path),'--project-root',str(ROOT)],'s6_collection_'+mode+'_r01') for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in results.items()}=={'evidence':0,'inputs':2},'包装实际码不同')
for mode in results:
    copy_closed('s6_collection_'+mode+'_r01')
save(REPORT / 's6_collection_packaging_r01.json',{'status':'EVIDENCE_PACKAGING_OK_INPUTS_ACTUAL_FAIL','checks':results,'policy':'evidence0仅包装；inputs2为候选未冻结/实际FAIL/NOT_RUN阻断。'})
original_check()
print(json.dumps({'status':summary['status'],'original_files':55,'native_copies':94,'native_raw_bytes':native['native_raw_copy_bytes'],'source_count':38,'compiled_rtl_count':18,'codes':{'sta':2,'evidence':0,'inputs':2},'collector_elapsed_seconds':time.monotonic()-started},ensure_ascii=False))
