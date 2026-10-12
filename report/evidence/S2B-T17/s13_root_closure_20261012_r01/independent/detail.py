"""读取实际调用和终态的必要字段。"""
import json
from pathlib import Path
R=Path(__file__).absolute().parents[4]; B=R/'report/evidence/S2B-T17/s13_platform_20261012_r01/mcp_closed'
for name in ['history.tool.json','wait.tool.json','stop.tool.json','r04_runtime_activation.json','static_actual_closed.json']:
 d=json.loads((B/name).read_text(encoding='utf-8')); print(name,json.dumps(d,ensure_ascii=False)[:6000])
for i in range(1,5):
 for suffix in ['guard_guard_receipt.json','supervisor_receipt.json']:
  n=f'supervision_r0{i}_{suffix}'; d=json.loads((B/n).read_text(encoding='utf-8')); print(n,json.dumps(d,ensure_ascii=False)[:2200])
for base,name in [('s13_root_closure_20261012_r01','archive_mapping.json'),('s13_root_closure_20261012_r01','runtime_snapshot_mapping.json')]:
 d=json.loads((R/'report/evidence/S2B-T17'/base/name).read_text(encoding='utf-8')); print(name,json.dumps(d if isinstance(d,list) else d['files'],ensure_ascii=False)[:1200])
