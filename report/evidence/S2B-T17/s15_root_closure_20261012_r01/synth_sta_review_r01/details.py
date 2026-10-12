"""抽取有限历史和原生状态字段，未执行任何设计工具。"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4];F=ROOT/'report/evidence/S2B-T17/s15_platform_20261012_r01'
def read(name):return json.loads((F/name).read_text(encoding='utf-8'))
def short(value):
    """只打印必要身份和返回码字段。"""
    if isinstance(value,dict):return {k:short(v) for k,v in value.items() if k not in ('stdout','stderr','traceback','output','samples','source_sha256','source_files')}
    if isinstance(value,list):return [short(v) for v in value[:40]]
    return str(value)[:250] if isinstance(value,str) else value
for n in ('mcp_closed/history_design.tool.json','mcp_closed/history_full.tool.json'):
    h=read(n);payload=json.loads(h.get('result',h)['content'][0]['text']);print(n,'payload keys',list(payload))
    print(short(payload))
for n in ('native_capture_closed/s15_runtime_collect_r1.native.json','native_capture_closed/root_collect_launch_r01.native.json','native_capture_closed/s15_runtime_source_before_r1.native.json','native_capture_closed/s15_runtime_source_after_r1.native.json'):
    j=read(n);print(n,'keys',list(j));print(short(j))
obs=read('mcp_closed/closed_runtime_observation.json');print('monitor rounds',short(obs['monitor_rounds']))
for n in ('mcp_closed/builder.tool.json','mcp_closed/close.tool.json','platform_readback.tcldict','setup_synthesis.tcldict'):
    print(n,(F/n).read_text(encoding='utf-8')[:2600])
