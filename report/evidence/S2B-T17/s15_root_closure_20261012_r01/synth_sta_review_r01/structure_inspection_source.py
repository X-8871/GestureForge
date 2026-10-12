"""仅读取本次声明证据的结构，避免输出完整大型日志。"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4]
FORMAL=ROOT/'report/evidence/S2B-T17/s15_platform_20261012_r01'
def structure(value,depth=0):
    """输出有限结构以确定独立解析入口。"""
    if isinstance(value,dict):
        return {k:structure(v,depth+1) for k,v in value.items()} if depth<1 else {'keys':list(value),'status':value.get('status'),'code':value.get('code'),'count':value.get('count')}
    if isinstance(value,list):return {'length':len(value),'first':structure(value[0],depth+1) if value else None}
    return str(value)[:400]
for name in ('s15_source_binding.json','s15_native_mapping.json','s15_mcp_binding.json','s15_constraints_binding.json','s15_sta_result.json','s15_xsa_comparison.json','mcp_closed/source_before.json','mcp_closed/source_after.json','mcp_closed/history_full.tool.json','mcp_closed/closed_runtime_observation.json','raw_root/additional_synthesis_count.json','native_capture_closed/closed_gate_synth_r01.json','native_capture_closed/source_freeze_r01.json','mcp_closed/source_admission_r01.json'):
    value=json.loads((FORMAL/name).read_text(encoding='utf-8'))
    print(name,json.dumps(structure(value),ensure_ascii=False),flush=True)
