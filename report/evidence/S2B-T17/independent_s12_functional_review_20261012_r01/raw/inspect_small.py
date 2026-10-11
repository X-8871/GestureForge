import json
from pathlib import Path
base=Path('report/evidence/S2B-T17')
for name in ['s12_conv_cones_20261012_r03','s12_route_private_20261012_r01']:
 v=json.loads((base/name/'validation.json').read_text(encoding='utf-8'))
 for k in ('controlled_multidriven_diagnostics','new_production_forbidden_diagnostics','runs'):
  x=v.get(k);print(name,k, type(x).__name__,list(x) if isinstance(x,dict) else len(x) if isinstance(x,list) else x)
  if isinstance(x,dict):print(str(x)[:2200])
  if isinstance(x,list):print(str(x[:1])[:2200])
main=base/'s12_timing_cones_20261012_r01'
v=json.loads((main/'delivery_manifest_r02.json').read_text(encoding='utf-8'))
print('LASTFILES',v['files'][-9:])
print('RQRECEIPT',json.loads((main/'requant_narrow_review_raw/final_review_receipt.json').read_text(encoding='utf-8')))
print('NATIVE',json.loads((main/'execution_raw/delivery_repair_capture_r01/native_receipt.json').read_text(encoding='utf-8')) if (main/'execution_raw/delivery_repair_capture_r01/native_receipt.json').is_file() else 'notpath')
