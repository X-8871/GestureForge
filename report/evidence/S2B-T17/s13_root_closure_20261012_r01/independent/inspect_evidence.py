"""只读本轮结构字段及关键报告；不读取生产RAW或执行清单命令。"""
import json
from pathlib import Path
OUT=Path(__file__).absolute().parent; ROOT=OUT.parents[3]
REPORT=ROOT/'report/evidence/S2B-T17/s13_platform_20261012_r01'
PRE=ROOT/'report/evidence/S2B-T17/s13_source_preflight_20261012_r01'
CLOSURE=ROOT/'report/evidence/S2B-T17/s13_root_closure_20261012_r01'
result={}
for path in (REPORT/'s12_collection_summary.json',REPORT/'s12_sta_result.json',REPORT/'s12_native_mapping.json',REPORT/'s12_mcp_binding.json',REPORT/'s12_source_binding.json',REPORT/'s12_constraints_binding.json',PRE/'source_before.json',PRE/'source_after.json',CLOSURE/'source_freeze_r01.json',CLOSURE/'runtime_snapshot_mapping.json'):
    data=json.loads(path.read_text(encoding='utf-8')); view={}
    if isinstance(data,list):
        result[path.name]=data
        continue
    for key,value in data.items():
        if isinstance(value,list) and (len(value)>18 or key in ('paired_calls','original_raw_inventory','closed_input_mapping')):
            view[key]=dict(count=len(value),first_keys=list(value[0]) if value and isinstance(value[0],dict) else None)
        elif key in ('source_sha256','static_source_sha256','static_source_sha256_before','static_source_sha256_after'):
            view[key]=dict(count=len(value))
        else: view[key]=value
    result[path.name]=view
(OUT/'structure_inspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
