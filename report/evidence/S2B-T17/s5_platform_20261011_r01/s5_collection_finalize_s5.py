"""封闭库存与最终机器清单，核验结果仅写隔离tmp避免自引用。"""
from collection_common import *
from datetime import datetime, timezone, timedelta
started = time.monotonic()
original = original_check()
collector = read(REPORT / 's5_collection_collector.native.json')
require(collector['native_exit_code'] == 0, 'Collector原生失败')
summary = read(REPORT / 's5_collection_summary.json')
pack = read(REPORT / 's5_collection_packaging_r01.json')
require({k:r['native_exit_code'] for k,r in pack['checks'].items()} == {'evidence':0,'inputs':2}, '关闭包装码不同')
summary.update(collector_native_exit_code=0, collector_command=collector['command'], collector_elapsed_seconds=collector['elapsed_seconds'], closed_packaging_codes={k:r['native_exit_code'] for k,r in pack['checks'].items()}, final_timestamp_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(), final_validation_log_policy='最终检查只写隔离tmp；正式包绑定此前已关闭检查与Collector输出，无活动日志自绑定。')
save(REPORT / 's5_collection_summary_final.json', summary)
formal = [binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
save(REPORT / 's5_collection_closed_inventory.json', {'status':'CLOSED_FORMAL_FILES_BEFORE_FINAL_MANIFEST','file_count':len(formal),'total_bytes':sum(r['bytes'] for r in formal),'files':formal,'note':'本索引不自绑定；自身与最终manifest由最终清单/外部最终记录绑定。初始56原件另逐项核验。'})
manifest = read(REPORT / 's5_collection_delivery_manifest_r01.json')
manifest['files'] = manifest_files(summary['external_inputs'])
manifest['checks'] += [{'name':'S5失败证据Collector执行','status':'PASS','command':' '.join(collector['command']),'exit_code':0,'reason':'只读核验/封装关闭原件，STA2和builder1保留；不是综合时序通过。'},{'name':'已关闭evidence包装检查','status':'PASS','command':' '.join(pack['checks']['evidence']['command']),'exit_code':0,'reason':'只代表目录/hash包装通过，不代表STA、接口冻结或G3/G4/G5。'},{'name':'已关闭inputs依赖检查','status':'FAIL','command':' '.join(pack['checks']['inputs']['command']),'exit_code':2,'reason':'实际FAIL、候选未冻结及NOT_RUN阻断。'}]
final = REPORT / 's5_collection_delivery_manifest_r02.json'
save(final, manifest)
checks = {mode:run_closed([sys.executable,'-B',str(REPORT / 's5_collection_stage_checker_snapshot.py'),'--mode',mode,'--manifest',str(final),'--project-root',str(ROOT)],'s5_final_' + mode) for mode in ('evidence','inputs')}
require({k:r['native_exit_code'] for k,r in checks.items()} == {'evidence':0,'inputs':2}, '最终包装码不同')
actual = read(WORK / 's5_final_evidence.stdout.log')
require(actual['status'] == 'CHECKS_OK' and not actual['errors'] and not actual['warnings'], '最终包装仍有错误或警告')
for row in manifest['files'] + manifest['interfaces']:
    require(sha(ROOT / row['path']) == row['sha256'], '最终绑定漂移：' + row['path'])
original_check()
inventory = [binding(p) for p in sorted(REPORT.rglob('*')) if p.is_file()]
initial_names = {r['path'] for r in original}
record = {'status':'STOP_S5_FAIL_TIMING_EVIDENCE_PENDING_INDEPENDENT_REVIEW','source_commit':BASELINE,'final_manifest':binding(final),'file_bindings':len(manifest['files']),'interface_bindings':len(manifest['interfaces']),'formal_report_files':len(inventory),'formal_report_bytes':sum(r['bytes'] for r in inventory),'original_raw_files':len(original),'original_raw_unchanged':True,'new_formal_files':[r for r in inventory if r['path'] not in initial_names],'new_formal_directories':[rel(p) for p in sorted(REPORT.rglob('*')) if p.is_dir()],'native_raw_copy_count':summary['native_raw_copy_count'],'source_count':38,'platform_static_source_count':31,'compiled_rtl_count':18,'git_raw_same_count':32,'exact_eol_count':6,'collector_native_exit_code':0,'collector_elapsed_seconds':collector['elapsed_seconds'],'native_classifier_exit_code':2,'final_checks':checks,'finalize_elapsed_seconds':time.monotonic()-started,'collector_peak_memory_bytes':None,'process_tree_peak_memory_bytes':None,'git_or_state_modified':False,'hardware_or_ross_touched':False}
save(WORK / 'final_status.json', record)
print(json.dumps({k:v for k,v in record.items() if k not in ('new_formal_files','new_formal_directories')}, ensure_ascii=False))
