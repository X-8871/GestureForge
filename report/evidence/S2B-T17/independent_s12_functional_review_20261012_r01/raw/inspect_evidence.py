"""精简显示证据结构供独审。"""
import json
from pathlib import Path
main=Path('report/evidence/S2B-T17/s12_timing_cones_20261012_r01')
summary=json.loads((main/'g1_summary.json').read_text(encoding='utf-8'))
for r in summary['runs']:
 v=json.loads(Path(r['validation_path']).read_text(encoding='utf-8'));n=json.loads(Path(r['native_path']).read_text(encoding='utf-8'))
 print(r['stage'],'VALKEYS',list(v),'NATIVEKEYS',list(n))
 for k in v:
  if any(t in k for t in ('warn','waiv','diagnostic','artifact','binding','source','memory','cpu','oracle','proof','contract')):
   value=v[k]
   print(k, type(value).__name__,len(value) if isinstance(value,(dict,list)) else value)
   if isinstance(value,dict):print('SUBKEYS',list(value))
 if r['stage'] in ('cones','private_route'):print('WARN',str(v.get('diagnostics',v.get('warning_review')))[:1800])
print('RQ',list(json.loads(Path('report/evidence/S2B-T17/s12_requant_rtl_20261012_r01/delivery_manifest_r02.json').read_text(encoding='utf-8'))))
