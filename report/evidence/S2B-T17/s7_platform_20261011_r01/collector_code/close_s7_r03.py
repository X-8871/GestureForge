"""补齐实际批量命令绑定，保留前清单并形成最终只增闭包。"""
from collection_common import *
from datetime import datetime, timezone, timedelta

started=time.monotonic()
closed_gate()
original_check()
previous=REPORT/'s7_collection_delivery_manifest_r02.json'
manifest=read(previous)
require(sha(previous)=='a9ce5173c54647fb712471d46c378b2baac224b04547c7538e72e8fb6bf7270c','前清单漂移')
code_dir=exact(REPORT/'collector_code','directory')
for name in ('close_s7_r03.py','run_close_s7_r03.py'):
    rawcopy(WORK/name,code_dir/name)
prior_validation=[]
for prefix in ('s7_final_evidence','s7_final_inputs','s7_finalization'):
    for suffix in ('stdout.log','stderr.log','native.json'):
        prior_validation.append(rawcopy(WORK/(prefix+'.'+suffix),REPORT/('s7_closed_r02_'+prefix+'.'+suffix)))
rawcopy(WORK/'final_status.json',REPORT/'s7_closed_r02_final_status.json')
mcp=read(REPORT/'s7_collection_mcp_history_binding.json')
reports=next(row['native_history'] for row in mcp['paired_calls'] if row['label']=='reports')
matches=[row for row in manifest['checks'] if row['name']=='非预期锁存器']
require(len(matches)==1,'锁存器核验条目不唯一')
before=dict(matches[0])
matches[0]['command']=reports['command']
matches[0]['exit_code']=reports['code']
matches[0]['reason']='实际完整batch reports命令及原生码绑定；Register as Latch=0来自同次utilization_flat_synth.rpt，不以简写替代实际执行命令。'
save(REPORT/'s7_collection_command_binding_correction.json',{'status':'EXACT_NATIVE_REPORT_BATCH_COMMAND_BOUND','previous_manifest':binding(previous),'previous_check_row':before,'corrected_check_row':matches[0],'native_history_id':reports['id'],'native_history_timestamp':reports['timestamp'],'original_reports_and_manifests_unchanged':True})
summary=read(REPORT/'s7_collection_summary_final.json')
summary.update(final_timestamp_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),packaging_manifest_count=3,stage_checker_execution_count=6,prior_final_checks_preserved_formally=True,command_binding_correction=rel(REPORT/'s7_collection_command_binding_correction.json'),gate_builder_command_clarification=rel(REPORT/'s7_collection_gate_builder_command_correction.json'))
save(REPORT/'s7_collection_summary_final_r03.json',summary)
receipt={'status':'STOP_S7_FAIL_TIMING_EVIDENCE_PENDING_INDEPENDENT_REVIEW','source_commit':BASELINE,'prior_formal_execution_receipt':binding(REPORT/'s7_collection_execution_receipt.json'),'prior_manifest':binding(previous),'prior_real_validation_raw_mapping':prior_validation,'command_correction':binding(REPORT/'s7_collection_command_binding_correction.json'),'source_count':39,'static_count':31,'extra_count':8,'compiled_rtl_count':18,'git_raw_count':33,'exact_eol_count':6,'native_raw_count':summary['native_raw_copy_count'],'native_raw_bytes':summary['native_raw_copy_bytes'],'vds_count':5,'collector_native_exit_code':0,'native_classifier_exit_code':2,'sta_status':'FAIL_TIMING','prior_final_evidence_exit_code':read(WORK/'s7_final_evidence.native.json')['native_exit_code'],'prior_final_inputs_exit_code':read(WORK/'s7_final_inputs.native.json')['native_exit_code'],'original_raw_unchanged':True,'no_git_write_state_ross_or_hardware_mutation':True,'independent_review':'NOT_RUN','source_snapshot_and_prior_checker_output_formal_recovery_available':True}
save(REPORT/'s7_collection_execution_receipt_r03.json',receipt)
formal=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
save(REPORT/'s7_collection_closed_inventory_r03.json',{'status':'CLOSED_FORMAL_FILES_BEFORE_R03_FINAL_MANIFEST','file_count':len(formal),'total_bytes':sum(r['bytes'] for r in formal),'files':formal,'note':'本库存不自引用；本身由最终r03清单绑定，最终清单由外部最终记录绑定。'})
manifest['files']=manifest_files(summary['external_inputs'])
manifest['limitations'] += ['r01/r02锁存器check行曾用报告命令简写；r03绑定同次history完整实际batch命令，旧清单原件保留。','门禁辅助command为人工转录且多反斜杠，已明确原生argv/native码未捕获；仅宿主0。该转录不参与collector及checker真实subprocess命令/码依据。']
final=REPORT/'s7_collection_delivery_manifest_r03.json'
save(final,manifest)
checks={mode:run_closed([sys.executable,'-B',str(REPORT/'s7_collection_stage_checker_snapshot.py'),'--mode',mode,'--manifest',str(final),'--project-root',str(ROOT)],'s7_r03_final_'+mode) for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in checks.items()}=={'evidence':0,'inputs':2},'r03最终包装码不同')
actual=read(WORK/'s7_r03_final_evidence.stdout.log')
require(actual['status']=='CHECKS_OK' and not actual['errors'] and not actual['warnings'],'r03包装有错误或警告')
for row in manifest['files']+manifest['interfaces']:
    require(sha(ROOT/row['path'])==row['sha256'],'最终绑定漂移：'+row['path'])
original_check()
inventory=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
record={'status':receipt['status'],'source_commit':BASELINE,'final_manifest':binding(final),'formal_execution_receipt':binding(REPORT/'s7_collection_execution_receipt_r03.json'),'file_bindings':len(manifest['files']),'interface_bindings':len(manifest['interfaces']),'formal_report_files':len(inventory),'formal_report_bytes':sum(r['bytes'] for r in inventory),'original_raw_files':55,'original_raw_unchanged':True,'native_raw_copy_count':summary['native_raw_copy_count'],'native_raw_copy_bytes':summary['native_raw_copy_bytes'],'native_vds_count':5,'source_count':39,'platform_static_source_count':31,'compiled_rtl_count':18,'git_raw_same_count':33,'exact_eol_count':6,'sta_status':'FAIL_TIMING','collector_native_exit_code':0,'collector_elapsed_seconds':summary['collector_elapsed_seconds'],'native_classifier_exit_code':2,'final_checks':checks,'close_elapsed_seconds':time.monotonic()-started,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'git_write_or_state_modified':False,'hardware_or_ross_touched':False,'temporary_inputs_needed_to_recheck_final_manifest':False}
save(WORK/'final_status_r03.json',record)
print(json.dumps(record,ensure_ascii=False))
