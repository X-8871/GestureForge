import hashlib
import json
from pathlib import Path
ROOT=Path(r'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition')
OUT=Path(__file__).resolve().parent
P=ROOT/'report/evidence/S2B-T17/s15_postroute_20261012_r01'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((OUT/'audit_result.json').read_text(encoding='utf-8'))
s=json.loads((OUT/'supplement_result.json').read_text(encoding='utf-8'))
assert not a['errors'] and not s['errors']
m=json.loads((P/'delivery_manifest_r03.json').read_text(encoding='utf-8'))
assert digest(P/'delivery_manifest_r03.json')=='4f7456caead3fd099db0c939953073641c46ee1d2c556e47f3f923a47779a9ff'
assert all(digest(ROOT/x['path'])==x['sha256'] for x in m['files'])
assert all(digest(ROOT/x['path'])==x['sha256'] for x in a['facts']['source_rows'])
assert digest(Path(s['facts']['fixed_postroute_checkpoint']['path']))==s['facts']['fixed_postroute_checkpoint']['sha256']
worst=(P/'timing_worst_pnr.rpt').read_text(encoding='utf-8')
assert 'required time                         21.843' in worst and 'arrival time                         -21.836' in worst
assert abs((21.843-21.836)-.007)<1e-9
report={
 'status':'PASS_PNR_STA_ONLY',
 'source_commit':'926c2fd382069e68e6c5ec533b7d3b6a87fbb363',
 'production_commit':'5492928349e5e5c0b72dab10c136dab8c549cea2',
 'manifest':{'path':str(P/'delivery_manifest_r03.json'),'sha256':digest(P/'delivery_manifest_r03.json'),'binding_count':637,'final_rehash_all_637':True},
 'timing':{'state':'Physopt postRoute','part':'xc7z020clg400-2','period_ns':20,'clock_mhz':50,'wns_ns':.007,'tns_ns':0,'setup_failing':0,'setup_endpoints':15425,'whs_ns':.087,'ths_ns':0,'hold_failing':0,'hold_endpoints':15425,'wpws_ns':8.870,'tpws_ns':0,'pulse_failing':0,'pulse_endpoints':4534,'check_timing_count':12,'all_check_timing_zero':True,'standalone_methodology_checks':0,'routable_nets':33918,'fully_routed_nets':33918,'routing_error_nets':0},
 'worst_path':{'source':a['facts']['worst_paths'][0]['source'],'destination':a['facts']['worst_paths'][0]['destination'],'requirement_ns':20,'data_delay_ns':19.297,'logic_delay_ns':6.155,'route_delay_ns':13.142,'logic_levels':29,'required_time_ns':21.843,'arrival_time_ns':21.836,'hand_subtraction_slack_ns':.007},
 'constraints':'独立全行比较综合与PNR时序XDC完全一致：20ns/输入jitter0.600，仅已有两reset同步首级falsepath，无multicycle或其他放宽；exceptions.rpt显示No valid timing exceptions found，不能解释为XDC不存在两falsepath。报告含内部DSP起点的inf路径，与12项检查零和约束检查分列。',
 'resources':a['facts']['resources'],
 'dsp_drc':{'severity':'Warning','DPIP-1':113,'DPOP-1':142,'DPOP-2':140,'total':395,'waiver_or_suppression_added':False},
 'source':{'count':46,'static_count':33,'frozen14_count':14,'active_rtl_count':18,'profile':'s2b-inference-platform/0.1.15','tcl_namespace':'0.1.12','visibility':0,'before_after_actual_identical':True,'independent_git_commands':48,'all_native_wait':0,'git_relations':a['facts']['git_relations'],'rows':a['facts']['source_rows'],'capture_before':{'child':0,'wrapper':2,'unknown':28},'capture_after':{'child':0,'wrapper':2,'unknown':37}},
 'actual_mcp':{'history_commands':8,'all_code':0,'implementation_launch_count':1,'launch':'launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1','threads':1,'client_wait_timeout_seconds':300,'native_wait_code':0,'native_wait_elapsed_seconds':1274.19,'closed_project_code':0,'stop_status':'success','known_identities_absent':14,'entire_os_tree_guarantee':False,'worker_os_exit_code':None},
 'monitor':s['facts']['monitor_statistics'],
 'launch_to_r02_first_sample_gap_seconds':s['facts']['launch_to_r02_first_sample_gap_seconds'],
 'monitor_status':'BLOCKED_NOT_PROVEN_CONTINUOUS',
 'monitor_exit_semantics':'两轮guard直接childwait3/SUP自述2/consumer自述2；r02 host tool1分别保留，consumer直接父wait未知。r01最后sample早于launch。缺口及身份UNKNOWN不由本审查关闭。',
 'tool_single_process_reported_peak_mb':a['facts']['tool_reported_single_process_peak_mb'],
 'original_paired_mapping_count':s['facts']['original_paired_mapping_count'],
 'packaging':{'r01_native':2,'r01_reason':'files含非schema字段bytes','r02_native':2,'r02_reason':'包外result/log role错误','r03_root_native':0,'r03_independent_native':0,'failed_originals_preserved':True},
 'collector':'实际prepared_receipt_r04和prepare0及classify0；旧硬编码collect/seal未调用，不承认旧seal成功。',
 'fixed_postroute_checkpoint':s['facts']['fixed_postroute_checkpoint'],
 'bit_input_decision':'从源码、真实PNR闭合及STA数值范围，允许此固定检查点作为生成bit的输入；下游必须核对本SHA并绑定，执行预算须另行满足既有门禁，本结论不授予新heavy预算。',
 'limits':{'continuous_budget':'NOT_PASSED','bit':'NOT_RUN','full_xsa_runtime_compatibility':'NOT_PASSED','hardware':'NOT_RUN','G3':'NOT_PASSED','G4':'NOT_PASSED','G5':'NOT_PASSED','synthesis_chances_remaining':2},
 'independent_work':'独立read/hash/解析与现有evidence checker；未运行测试、综合实现、ROSS或硬件；未修改被审源码/正式637文件/分支，无Git提交。',
 'machine_checks':len(a['checks'])+len(s['checks']),
 'review_blocking_findings':[],
}
(OUT/'review_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'machine_checks':report['machine_checks'],'final_rehash':637,'wns_ns':.007,'budget':'NOT_PASSED','checkpoint_sha256':s['facts']['fixed_postroute_checkpoint']['sha256']},ensure_ascii=False))
