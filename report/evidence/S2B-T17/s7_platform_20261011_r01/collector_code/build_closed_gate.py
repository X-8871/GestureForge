"""核对总控关闭绑定并记录显式信号，不读取活动日志或调用 Git。"""
from collection_common import *

expected={
    'source_after':{'path':'report/evidence/S2B-T17/s7_source_preflight_20261011_r01/source_after.json','sha256':'4b190e95c16ec6b0d150774cec1fe7a833e5db1b37416279933d82efb724bfd9','bytes':19585},
    'static_source_closed':{'path':'tmp/2B/S2B-T17/s7_root_run_20261011_r01/static_actual_closed.json','sha256':'64298665657dbe6a709aecf210bdb61ef0c2d833a0f9fcfbad653889c39bd474','bytes':3517},
    'immutable_session_log':{'path':'tmp/2B/S2B-T17/s7_root_run_20261011_r01/root_session_snapshot.log','sha256':'da8b702cf5eaa08da7fa58b4cfe7364b3b9bed6b86765c3856c51a2740b2d1c9','bytes':65132},
    'mcp_history':{'path':'tmp/2B/S2B-T17/s7_root_run_20261011_r01/mcp_history.json','sha256':'c367439edf52e3958dd92d11d55a67c2fdb6fdc6b428e838c2588b029cd7f992','bytes':64087},
}
for label,row in expected.items():
    require(binding(ROOT/row['path'])==row,'总控闭合绑定不同：'+label)
snapshot_binding=CACHE/'root_session_snapshot_binding.json'
require(binding(snapshot_binding)=={'path':rel(snapshot_binding),'sha256':'4faf03d0b542340a7e402887cd7c565cb98061acbb193336fe493dde9d1912e3','bytes':626},'root快照绑定原件不同')
history=mcp_json(read(ROOT/expected['mcp_history']['path']))['history']
labels=('source','builder','setup','launch','wait','open_run','reports','query_xdc','close')
require(len(history)==9,'同次关闭history不是9')
records=[]
for label,item in zip(labels,history):
    matches=[]
    for path in sorted(CACHE.glob('mcp_*.json')):
        value=read(path)
        if value.get('input',{}).get('command')==item['command']:
            matches.append(path)
    require(len(matches)==1,'同次MCP命令匹配不唯一：'+label)
    record=read(matches[0])
    require(record['input']['session_id']=='vivado-20261011-205640-497a6a78','会话归属不同')
    require(mcp_json(record)['exit_code']==item['code'],'MCP/native码不同：'+label)
    records.append({'label':label,**binding(matches[0])})
require(history[4]['code']==0 and history[4]['elapsed']==241.088 and history[-1]['command']=='close_project' and history[-1]['code']==0,'实际wait/close不同')
names=('source_preflight.py','close_source_and_log.py','root_session_snapshot_binding.json','source_before.native.json','source_before.stdout.log','source_before.stderr.log','source_after.native.json','source_after.stdout.log','source_after.stderr.log','resource_preflight.json','resource_during_synthesis_01.json')
additional=[binding(CACHE/name) for name in names if (CACHE/name).is_file()]
gate={'root_explicit_signal':'CLOSED_INPUTS_READY','signal_source':'ROOT向本子代理的本次明确消息','source_commit':BASELINE,'project_closed':True,'root_session_id':'vivado-20261011-205640-497a6a78','root_main_pid':35136,**expected,'design_mcp_records':records,'additional_closed_files':additional,'auxiliary_mcp_call_counts':None,'design_execute_calls':9,'root_declared_synthesis_execution_count':1,'root_declared_products_execution_count':1,'native_wait_exit_code':0,'native_wait_elapsed_seconds':241.088,'active_log_consumed':False,'git_invoked_by_gate_builder':False,'sta_expected_from_root_for_crosscheck':{'status':'FAIL_TIMING','wns_ns':-7.986,'tns_ns':-2818.766,'setup_failing_endpoints':784,'setup_total_endpoints':14784},'limitations':['关闭信号只允许收集，不批准STA/部署/G3-G5；真实STA状态仍须从本轮报告独立分类。','资源和总host工具调用量只记录可获得原件，不把单次采样当进程树峰。']}
save(WORK/'closed_inputs.json',gate)
print(json.dumps({'status':'CLOSED_INPUTS_BOUND','closed_gate':binding(WORK/'closed_inputs.json'),'design_records':len(records),'additional_closed_files':len(additional),'source_after_count':len(read(ROOT/expected['source_after']['path'])['source_files']),'git_invoked':False},ensure_ascii=False))
