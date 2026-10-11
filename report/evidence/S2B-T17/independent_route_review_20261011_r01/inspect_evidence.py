"""只读摘要开发证据，避免打印重复源码绑定。"""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[4]
base = root / 'report/evidence/S2B-T17'
m = json.loads((base/'route_specialization_20261011_r07/delivery_manifest.json').read_text(encoding='utf-8'))
print(json.dumps({k:v for k,v in m.items() if k!='files'}, ensure_ascii=False, indent=2))
print('files',len(m['files']), m['files'][:2])
for rid in ('route_specialization_20261011_r08','route_specialization_20261011_r05','route_specialization_20261011_r06','coordinates_20261011_r04'):
    d=json.loads((base/rid/'validation.json').read_text(encoding='utf-8'))
    print(rid, list(d))
    print(json.dumps({k:v for k,v in d.items() if k in ('status','simulation_counts','trace_rows','trace_equivalence','coverage','public_entries','outside_profile_witnesses','model_manifest','route_math')},ensure_ascii=False))
