import json
from pathlib import Path
p=Path('report/evidence/S2B-T17/s12_timing_cones_20261012_r01')
s=json.loads((p/'g1_summary.json').read_text(encoding='utf-8'))
for r in s['runs']:
 print(r['stage'],r['status'],r['native_returncode'],r['actual_fields'])
m=json.loads(Path('report/evidence/S2A-T01/tiny416_model_manifest.json').read_text(encoding='utf-8'))
print(list(m)); print(m['layers'][0].keys())
print({k:v for k,v in m['layers'][0].items() if not isinstance(v,list)})
print([(i,l.get('type'),l.get('op'), l.get('input_layers'),l.get('input_shapes_nchw')) for i,l in enumerate(m['layers'])])
