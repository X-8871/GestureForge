import json
import sys
from pathlib import Path

# 只读输出冻结证据的结构，避免巨量全文遮蔽核查信息。
p = Path('report/evidence/S2B-T17/s3_platform_20261011_r01')
sys.stdout.reconfigure(encoding='utf-8')
def small(data):
    if isinstance(data, list) and len(data) > 5:
        return {'count': len(data), 'first': small(data[0]), 'last': small(data[-1])}
    if isinstance(data, dict):
        return {k: small(v) for k, v in data.items()}
    if isinstance(data, list):
        return [small(v) for v in data]
    return data
for name in []:
    data = json.loads((p / ('s3_collection_' + name + '.json')).read_text(encoding='utf-8'))
    print(name, json.dumps(small(data), ensure_ascii=False)[:22000])
q=Path('report/evidence/S2B-T17/s3_source_preflight_20261011_r01')
for name in ['source_before', 'source_after', 'root_mcp_calls_closed']:
    data=json.loads((q/(name+'.json')).read_text(encoding='utf-8'))
    if name=='root_mcp_calls_closed':
        print(name,'keys',list(data), 'calls',len(data['calls']), 'wait', data['calls'][4])
        for k,v in data.items():
            if k!='calls': print(k, str(v)[:200])
    else:
        print(name, json.dumps(small(data),ensure_ascii=False)[:15000])
