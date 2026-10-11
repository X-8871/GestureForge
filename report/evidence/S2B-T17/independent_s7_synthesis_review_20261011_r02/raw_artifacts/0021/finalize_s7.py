"""封闭S7实际清单与库存，最终检查日志留隔离目录避免自引用。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
started=time.monotonic()
closed_gate()
original=original_check()
collector=read(REPORT/'s7_collection_collector.native.json')
require(collector['native_exit_code']==0,'Collector原生失败')
summary=read(REPORT/'s7_collection_summary.json')
pack=read(REPORT/'s7_collection_packaging_r01.json')
require({k:r['native_exit_code'] for k,r in pack['checks'].items()}=={'evidence':0,'inputs':2},'包装实际码不同')
summary.update(collector_native_exit_code=0,collector_command=collector['command'],collector_elapsed_seconds=collector['elapsed_seconds'],closed_packaging_codes={k:r['native_exit_code'] for k,r in pack['checks'].items()},final_timestamp_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),final_validation_log_policy='正式包绑定关闭的分类器/包装/Collector源码与真实输出；最终自引用检查只写隔离tmp，不作为最终重建输入。')
save(REPORT/'s7_collection_summary_final.json',summary)
receipt={'status':'STOP_S7_'+summary['sta_status']+'_EVIDENCE_PENDING_INDEPENDENT_REVIEW','source_commit':BASELINE,'collector':binding(REPORT/'s7_collection_collector.native.json'),'packaging':binding(REPORT/'s7_collection_packaging_r01.json'),'source_count':39,'static_count':31,'extra_count':8,'compiled_rtl_count':18,'git_raw_count':33,'exact_eol_count':6,'native_raw_count':summary['native_raw_copy_count'],'native_raw_bytes':summary['native_raw_copy_bytes'],'vds_count':5,'source_snapshots_are_external_formal_evidence':True,'collector_native_exit_code':0,'native_classifier_exit_code':summary['native_classifier_exit_code'],'sta_status':summary['sta_status'],'evidence_exit_code':0,'inputs_exit_code':2,'original_raw_unchanged':True,'no_git_state_ross_or_hardware_mutation':True,'independent_review':'NOT_RUN'}
save(REPORT/'s7_collection_execution_receipt.json',receipt)
formal=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
save(REPORT/'s7_collection_closed_inventory.json',{'status':'CLOSED_FORMAL_FILES_BEFORE_FINAL_MANIFEST','file_count':len(formal),'total_bytes':sum(r['bytes'] for r in formal),'files':formal,'note':'库存不自引用，本身由最终清单绑定；最终清单由外部最后记录绑定。'})
manifest=read(REPORT/'s7_collection_delivery_manifest_r01.json')
manifest['files']=manifest_files(summary['external_inputs'])
manifest['checks'] += [{'name':'S7实际证据Collector执行','status':'PASS','command':' '.join(collector['command']),'exit_code':0,'reason':'仅收集/核验闭合原件，独立STA状态单列。'},{'name':'已关闭evidence包装检查','status':'PASS','command':' '.join(pack['checks']['evidence']['command']),'exit_code':0,'reason':'只证明目录/hash包装。'},{'name':'已关闭inputs依赖检查','status':'FAIL','command':' '.join(pack['checks']['inputs']['command']),'exit_code':2,'reason':'物理候选未冻结/真实失败/NOT_RUN等输入阻断保留。'}]
final=REPORT/'s7_collection_delivery_manifest_r02.json'
save(final,manifest)
checks={mode:run_closed([sys.executable,'-B',str(REPORT/'s7_collection_stage_checker_snapshot.py'),'--mode',mode,'--manifest',str(final),'--project-root',str(ROOT)],'s7_final_'+mode) for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in checks.items()}=={'evidence':0,'inputs':2},'最终包装实际码不同')
actual=read(WORK/'s7_final_evidence.stdout.log')
require(actual['status']=='CHECKS_OK' and not actual['errors'] and not actual['warnings'],'最终包装有错误/警告')
for row in manifest['files']+manifest['interfaces']:
    require(sha(ROOT/row['path'])==row['sha256'],'最终绑定漂移：'+row['path'])
original_check()
inventory=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
record={'status':receipt['status'],'source_commit':BASELINE,'final_manifest':binding(final),'formal_execution_receipt':binding(REPORT/'s7_collection_execution_receipt.json'),'file_bindings':len(manifest['files']),'interface_bindings':len(manifest['interfaces']),'formal_report_files':len(inventory),'formal_report_bytes':sum(r['bytes'] for r in inventory),'original_raw_files':len(original),'original_raw_unchanged':True,'native_raw_copy_count':summary['native_raw_copy_count'],'native_raw_copy_bytes':summary['native_raw_copy_bytes'],'native_vds_count':5,'source_count':39,'platform_static_source_count':31,'compiled_rtl_count':18,'git_raw_same_count':33,'exact_eol_count':6,'sta_status':summary['sta_status'],'collector_native_exit_code':0,'collector_elapsed_seconds':collector['elapsed_seconds'],'native_classifier_exit_code':summary['native_classifier_exit_code'],'final_checks':checks,'finalize_elapsed_seconds':time.monotonic()-started,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'git_or_state_modified':False,'hardware_or_ross_touched':False,'temporary_inputs_needed_to_recheck_final_manifest':False}
save(WORK/'final_status.json',record)
print(json.dumps(record,ensure_ascii=False))
