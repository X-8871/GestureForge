"""核对实际MCP退出与时间口径，并封存所有已关闭日志，避免活动stdout自绑定。"""
from pathlib import Path
import hashlib,json,sys,time
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parent;R=W.parents[3];P=R/'report/evidence/S2B-T17/s2_platform_20261011_r01'
def read(p):
    """读取UTF8机器记录。"""
    return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    """绑定原始字节。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
a=read(W/'audit_result.json');assert a['status']=='PASS_EVIDENCE_INTEGRITY';root=read(P/'root_mcp_calls_final.json')
calls={x['step']:x for x in root['calls']}
def result(step):
    """消费真实返回块。"""
    rows=[json.loads(x['text']) for x in calls[step]['result']['content'] if x['type']=='text'];assert len(rows)==1;return rows[0]
assert result('construct_full_s2_visibility0_platform')['exit_code']==1
assert result('launch_s2_synthesis_jobs1')['exit_code']==0
assert result('capture_s2_synth_sta_resource_constraint_reports')['exit_code']==0
assert result('open_s2_synthesized_design')['exit_code']==0
assert result('close_ended_s2_project_before_s3_development')['exit_code']==0
waittext='\n'.join(x['text'] for x in calls['wait_s2_synthesis_jobs1']['result']['content'] if x['type']=='text')
assert '300' in waittext and ('timeout' in waittext.lower() or 'timed out' in waittext.lower())
summary=read(P/'collection_fix_summary_r02.json')
assert summary['original_paths_all_unchanged'] is False
sta_outer=read(P/'collection_fix_sta_native_r02.json');sta_inner=read(P/'collection_fix_sta_result_r02.json')
seal=read(P/'collection_fix_seal_native.json')
assert round(sta_outer['elapsed_seconds'],3)==0.141 and round(sta_inner['elapsed_seconds'],3)==0.063 and round(seal['elapsed_seconds'],3)==1.187
a['supplement_checks']={'actual_whole_platform_entry_native_exit_code':1,'launch_native_exit_code':0,'report_generation_native_exit_code':0,'open_synthesized_native_exit_code':0,'close_ended_s2_native_exit_code':0,'mcp_wait_timeout_retained':True,'original_paths_all_unchanged':False,
 'classifier_outer_seconds':sta_outer['elapsed_seconds'],'classifier_inner_seconds':sta_inner['elapsed_seconds'],'seal_outer_seconds':seal['elapsed_seconds'],'collector_inner_seconds':summary['collector_elapsed_seconds'],
 'timing_scope':'wait381.939不是严格综合总wall；classifier外/内、collector外/内、seal外/内分别保留，不相互替代。'}
assert all(row['passed'] for row in a['checks'])
files=[p for p in W.rglob('*') if p.is_file()]
assert sum(p.stat().st_size for p in files)<314572800
manifest=P/'collection_fix_delivery_manifest_r04.json'
bindings=read(manifest)['files']+read(manifest)['interfaces']
for row in bindings:assert sha(R/row['path'])==row['sha256']
a['bound_original_manifest']={'path':manifest.relative_to(R).as_posix(),'sha256':sha(manifest),'file_bindings':191,'interface_bindings':2}
a['closed_raw_review_files']=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)]
a['review_execution']={'command':[sys.executable,'-B',str(W/'review_s2_synthesis.py')],'native_exit_code':0,'program_inner_seconds':a['seconds'],'outer_exec_wall_seconds':2.8181989,'peak_rss':'NOT_MEASURED','whole_review_wall_seconds':'NOT_MEASURED'}
a['current_head_context']='2a20b1d9b53c9cc49fafdb49b09d78c5ab4f4674只作为根代理上下文，不作为S2编译输入；S3活动源码未读取。'
a['stop']=True
assert not (W/'receipt.json').exists()
(W/'receipt.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for row in a['closed_raw_review_files']:assert sha(R/row['path'])==row['sha256']
print(json.dumps({'status':a['status'],'checks':len(a['checks']),'receipt_sha256':sha(W/'receipt.json'),'files':len(files),'native_commands':[{k:r[k] for k in ('name','native_exit_code','seconds')} for r in a['commands']]},ensure_ascii=False))
