"""只读必要结构样例，避免输出大清单。"""
import json
from pathlib import Path
R=Path(__file__).absolute().parents[4]
for base,name in [('s13_platform_20261012_r01',n) for n in ['s12_collection_summary.json','s12_native_mapping.json','s12_mcp_binding.json','s12_source_binding.json']]+[('s13_source_preflight_20261012_r01','source_before.json'),('s13_root_closure_20261012_r01','source_freeze_r01.json')]:
 d=json.loads((R/'report/evidence/S2B-T17'/base/name).read_text(encoding='utf-8'))
 print(name)
 for k,v in d.items():
  if isinstance(v,list): print(k,'LIST',len(v),json.dumps(v[:1],ensure_ascii=False)[:2400])
  elif isinstance(v,dict): print(k,'DICT',len(v),json.dumps(v,ensure_ascii=False)[:1800])
  else: print(k,str(v)[:500])
