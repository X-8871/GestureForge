"""封闭 r02 续收集后的正式库存与最终清单。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
started=time.monotonic()
original=original_check()
collector=read(REPORT / 's6_collection_collector_r02.native.json')
require(collector['native_exit_code']==0,'续Collector原生失败')
summary=read(REPORT / 's6_collection_summary.json')
pack=read(REPORT / 's6_collection_packaging_r01.json')
require({k:r['native_exit_code'] for k,r in pack['checks'].items()}=={'evidence':0,'inputs':2},'包装码不同')
summary.update(collector_native_exit_code=0,collector_command=collector['command'],collector_elapsed_seconds=collector['elapsed_seconds'],first_collector_elapsed_seconds=read(REPORT / 's6_collection_collector.native.json')['elapsed_seconds'],closed_packaging_codes={k:r['native_exit_code'] for k,r in pack['checks'].items()},final_timestamp_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),final_validation_log_policy='正式包绑定已关闭分类器/包装/Collector日志；最终自引用检查仅写隔离tmp，不作为重建依赖。')
save(REPORT / 's6_collection_summary_final.json',summary)
receipt={'status':'STOP_S6_FAIL_TIMING_EVIDENCE_PENDING_INDEPENDENT_REVIEW','source_commit':BASELINE,'collector':binding(REPORT / 's6_collection_collector_r02.native.json'),'first_collector':binding(REPORT / 's6_collection_collector.native.json'),'packaging':binding(REPORT / 's6_collection_packaging_r01.json'),'source_count':38,'static_count':31,'compiled_rtl_count':18,'git_raw_count':32,'exact_eol_count':6,'native_raw_count':summary['native_raw_copy_count'],'native_raw_bytes':summary['native_raw_copy_bytes'],'vds_count':5,'source_snapshots_are_external_formal_evidence':True,'first_collector_native_exit_code':1,'final_collector_native_exit_code':0,'native_classifier_exit_code':2,'evidence_exit_code':0,'inputs_exit_code':2,'original_raw_unchanged':True,'no_git_state_ross_or_hardware_mutation':True,'independent_review':'NOT_RUN'}
save(REPORT / 's6_collection_execution_receipt.json',receipt)
formal=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
save(REPORT / 's6_collection_closed_inventory.json',{'status':'CLOSED_FORMAL_FILES_BEFORE_FINAL_MANIFEST','file_count':len(formal),'total_bytes':sum(r['bytes'] for r in formal),'files':formal,'note':'库存不自引用，库存本身由最终清单绑定，最终清单由外部记录绑定。'})
manifest=read(REPORT / 's6_collection_delivery_manifest_r01.json')
manifest['files']=manifest_files(summary['external_inputs'])
manifest['checks'] += [{'name':'S6失败证据r02Collector执行','status':'PASS','command':' '.join(collector['command']),'exit_code':0,'reason':'只读失败证据核验/续封装，首native1保留，不是时序通过。'},{'name':'已关闭evidence包装检查','status':'PASS','command':' '.join(pack['checks']['evidence']['command']),'exit_code':0,'reason':'仅目录/hash包装，不代表STA或验收。'},{'name':'已关闭inputs依赖检查','status':'FAIL','command':' '.join(pack['checks']['inputs']['command']),'exit_code':2,'reason':'物理未冻结、真实STAFAIL、NOT_RUN仍阻断。'}]
final=REPORT / 's6_collection_delivery_manifest_r02.json'
save(final,manifest)
checks={mode:run_closed([sys.executable,'-B',str(REPORT / 's6_collection_stage_checker_snapshot.py'),'--mode',mode,'--manifest',str(final),'--project-root',str(ROOT)],'s6_final_'+mode) for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in checks.items()}=={'evidence':0,'inputs':2},'最终包装码不同')
actual=read(WORK / 's6_final_evidence.stdout.log')
require(actual['status']=='CHECKS_OK' and not actual['errors'] and not actual['warnings'],'最终包装错误或警告')
for row in manifest['files']+manifest['interfaces']:
    require(sha(ROOT / row['path'])==row['sha256'],'最终绑定漂移：'+row['path'])
original_check()
inventory=[binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
record={'status':receipt['status'],'source_commit':BASELINE,'final_manifest':binding(final),'formal_execution_receipt':binding(REPORT / 's6_collection_execution_receipt.json'),'file_bindings':len(manifest['files']),'interface_bindings':len(manifest['interfaces']),'formal_report_files':len(inventory),'formal_report_bytes':sum(r['bytes'] for r in inventory),'original_raw_files':55,'original_raw_unchanged':True,'native_raw_copy_count':summary['native_raw_copy_count'],'native_raw_copy_bytes':summary['native_raw_copy_bytes'],'native_vds_count':5,'source_count':38,'platform_static_source_count':31,'compiled_rtl_count':18,'git_raw_same_count':32,'exact_eol_count':6,'first_collector_native_exit_code':1,'collector_native_exit_code':0,'collector_elapsed_seconds':collector['elapsed_seconds'],'native_classifier_exit_code':2,'final_checks':checks,'finalize_elapsed_seconds':time.monotonic()-started,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'git_or_state_modified':False,'hardware_or_ross_touched':False,'temporary_inputs_needed_to_recheck_final_manifest':False}
save(WORK / 'final_status.json',record)
print(json.dumps(record,ensure_ascii=False))
