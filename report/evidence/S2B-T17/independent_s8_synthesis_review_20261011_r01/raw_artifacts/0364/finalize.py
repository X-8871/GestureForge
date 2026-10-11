"""只封存本轮证据准确性回执，不批准STA或部署。"""
from pathlib import Path
import json,hashlib,sys,subprocess
ROOT=Path.cwd(); WORK=Path(__file__).resolve().parent
BASE=ROOT/'report/evidence/S2B-T17/s8_platform_20261011_r01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
validation=json.loads((WORK/'audit_result_r02.json').read_text(encoding='utf-8'))
assert validation['status']=='PASS_FAILED_EVIDENCE_ACCURACY_ONLY'
manifest=BASE/'s8_delivery_manifest_r02.json'; expected='a63839ea6e82b71fa28c6f9bd37223123ffeda3df5f122978b9b420c8c962e0e'
assert sha(manifest)==expected
original=json.loads(manifest.read_text(encoding='utf-8'))
for row in original['files']: assert sha(ROOT/row['path'])==row['sha256']
prior=ROOT/'tmp/2B/S2B-T17/independent_s8_maxpool_review_20261011_r01/final_review_receipt.json'
assert sha(prior)=='dbe37b505c8fa928404cea486555b2b0858769b228af9cb587ed875406153bd8'
g2_manifest=ROOT/'report/evidence/S2B-T17/independent_s8_maxpool_review_20261011_r01/delivery_manifest_r02.json'
g2=json.loads(g2_manifest.read_text(encoding='utf-8')); prior_rows=[r for r in g2['files'] if r['sha256']==sha(prior)]
assert prior_rows and all(sha(ROOT/r['path'])==sha(prior) for r in prior_rows)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(); assert head=='c9f423cddc74ea45071fdbb6a68e4505316babb1'
cmd=[sys.executable,'-X','utf8','-B',str(WORK/'audit.py')]
receipt={
 'schema_version':1,'status':'PASS','reviewer_stop':True,'scope':'S2B-T17-S8 实际综合失败证据准确性、完整性及可恢复性独立审查；不批准时序关闭',
 'source_commit':head,'reviewed_manifest':str(manifest.relative_to(ROOT)).replace('\\','/'),'reviewed_manifest_sha256':expected,'reviewed_file_bindings':318,
 'source_sha256':validation['source_sha256'],'source_freeze_sha256':'f1a70a6f0b703a1e062c479cbc18177b3800f337e06a9fe25dc7d07363ed8708',
 'source_review':{'total':41,'static':32,'extra':9,'RAW_IDENTICAL':35,'GIT_LF_TO_RAW_CRLF':6,'before_after_current_and_snapshots_equal':True,'frozen14_raw_unchanged':True,'activeRTL':18,'derived':8,'original':6,'outer':4,'actual_infer_native_tcl_registration_matches':True,'profile':'0.1.8','part':'xc7z020clg400-2','clock_hz':50000000,'clock_period_ns':20,'visibility':0},
 'prior_g2_receipt':{'path':prior.relative_to(ROOT).as_posix(),'sha256':sha(prior),'formal_archive_manifest':g2_manifest.relative_to(ROOT).as_posix(),'formal_archive_manifest_sha256':sha(g2_manifest),'scope':'此前MAXPOOL软件/RTL G2，不能继承新STA批准'},
 'execution_accuracy':{'design_mcp_commands':9,'native_history_exact_pairs':True,'products_count':1,'synthesis_launch_count':1,'products_native_exit_code':0,'products_capture_exit_code':1,'warning_counter_transition':'9→1','products_failure_preserved':True,'products_rerun':False,'wait_native_exit_code':0,'wait_seconds':251.126,'wait_client_timeout':False,'synth_completed_runs':5,'synth_progress':'100%','implementation_runs_not_started':5,'native_job_os_exit_code':None,'process_tree_memory_peak':None,'native_logs_vds_markers_bound':True,'closed_log_bytes':65140,'closed_log_sha256':'c8e5c5660203206a8df3421b0aaf4f96bd22ea91594b7d86e8d1887bb6b76a08','owned_pid':5236,'owned_pid_absent':True,'mcp_stop':'success'},
 'actual_sta':{'status':'FAIL_TIMING','native_exit_code':2,'design_state':'Synthesized','timing':validation['timing'],'clock':validation['clock'],'unconstrained_internal_endpoints':0,'worst_path':'CONV output_group_base_reg[4]/C→result_error_latched_reg[0]/D','data_path_ns':26.345,'logic_ns':18.635,'route_ns':7.710,'logic_levels':32,'CARRY4':16,'DSP48E1':5,'exported_reset_CDC_false_path_commands':2,'timing_exception_report':'No valid timing exceptions found.','exceptions_interpretation':'导出约束仅含两个rst_fclk0 reset CDC第一同步级命令；不把导出命令数伪称为有效时序例外数。','methodology_TIMING16_warnings':712,'drc_warnings':{'DPIP-1':114,'DPOP-1':142,'DPOP-2':141},'resources':validation['resources'],'speed_file':'-2 PRODUCTION 1.12 2019-11-22'},
 'xsa_review':{'crc_all_members_ok':True,'bit_present':False,'six_psinit_raw_equal':True,'hwh_raw_equal':False,'runtime_elf_bsp_compatibility':'NOT_APPROVED'},
 'packaging_accuracy':{'collector_native_exit_code':0,'seal_native_exit_code':0,'first_root_evidence_native_exit_code':2,'first_root_evidence_reason':'root_closed新增七文件后检查旧清单；真实未列入files错误完整保留。','r02_evidence_native_exit_code':0,'r02_inputs_native_exit_code':2,'inputs_meaning':'物理候选未冻结、实际STA失败及未执行依赖仍阻断，不能改判PASS。'},
 'checks':[{'name':'独立318绑定/41源码/Git/实际MCP/原生日志/STA/CRC/关闭记录断言','status':'PASS','command':subprocess.list2cmdline(cmd),'native_exit_code':0,'elapsed_seconds':validation['elapsed_seconds']},*validation['native_runs']],
 'reviewer_resources':{'sampled_self_rss_bytes':validation['sampled_self_rss_bytes'],'sample_type':'程序起止两点RSS，非峰值','peak_process_tree_rss_bytes':None,'heavy_tasks_started':0,'hardware_operations':0},
 'reviewer_original_failures':[{'path':(WORK/'audit_result.json').relative_to(ROOT).as_posix(),'sha256':sha(WORK/'audit_result.json'),'native_exit_code':1,'reason':'审查脚本首轮未允许Vivado Slice LUTs*星号注记；被审证据无此错误。原脚本/日志保留，r02修正后原生0。'},{'operation':'只读枚举','host_exit_code':1,'native_program_exit_code':None,'reason':'探索性owned_session_exit.json目标不存在，随后只读枚举确认真实名称为root_closed/owned_process_closed.json；未改写任何输入。'}],
 'findings':[],
 'manual_review':{'status':'COMPLETED','native_exit_code':None,'reason':'报告语义及批准边界人工审查不虚构执行码0。'},
 'limitations':['PASS只表示真实失败证据准确、绑定完整及源/步骤可恢复。实际50MHz STA明确FAIL_TIMING。','未重跑Vivado、重型仿真或修改被审生产/正式证据/STATE/Git。','综合态路线延迟来自估算，不是postroute；没有实现、bit、runtime、BOARD、109/1000或G3–G5批准。','六PSinit字节相同而HWH改变，不能继承旧ELF/BSP批准。','OS退出码及进程树峰值没有直接捕获，保留null；真实单进程日志峰分别核对。','318项哈希与精确闭包可恢复性不等于已执行新环境完整重建。','首次自身审查解析失败和原始ROOT包装失败均完整保留，未改写原件。'],
 'git_commit':'NOT_APPLICABLE_READ_ONLY_REVIEW','production_modified':False,'raw_manifest':(WORK/'raw_manifest.jsonl').relative_to(ROOT).as_posix()
}
(WORK/'final_review_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths={ROOT/p:'input' for p in json.loads((WORK/'direct_inputs_r02.json').read_text(encoding='utf-8'))}
paths.update({prior:'input',g2_manifest:'input'})
paths.update({ROOT/r['path']:'input' for r in prior_rows})
for p in WORK.rglob('*'):
    if p.is_file() and p.name!='raw_manifest.jsonl': paths[p]='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'
rows=[]
for p,role in sorted(paths.items()):
    if p.suffix.lower() in ['.exe','.dcp','.bit','.obj'] or any(part.endswith(('.runs','.gen','.srcs','.cache')) or part=='obj_dir' for part in p.parts): continue
    if p.suffix in ['.sv','.py','.tcl'] and p.is_relative_to(ROOT/'src') or p.is_relative_to(ROOT/'verification'): role='source'
    rows.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'role':role})
(WORK/'raw_manifest.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows),encoding='utf-8')
print(json.dumps({'status':'PASS_FAILED_EVIDENCE_ACCURACY_ONLY','receipt_sha256':sha(WORK/'final_review_receipt.json'),'raw_manifest_sha256':sha(WORK/'raw_manifest.jsonl'),'raw_count':len(rows),'audit_seconds':validation['elapsed_seconds'],'sampled_self_rss_bytes':validation['sampled_self_rss_bytes']},ensure_ascii=False))
