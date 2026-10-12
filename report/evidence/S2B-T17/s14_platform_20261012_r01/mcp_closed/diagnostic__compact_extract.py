"""从已绑定只读摘录生成精简诊断字段。"""
import json
from pathlib import Path
W=Path(__file__).resolve().parent
data=json.loads((W/'actual_guard_extract.json').read_text(encoding='utf-8'))
for run in data['runs']:
    print('RUN',run['label'])
    print('guard',json.dumps(run['guard_receipt'],ensure_ascii=False))
    for sample in run['last_samples']:
        fields=sample['fields']
        print('SAMPLE',sample['line'],json.dumps({k:fields.get(k) for k in ['index','sample_started_at_utc8','sample_ended_at_utc8','sample_elapsed_seconds','actual_start_gap_seconds','collection_observation','tree_rss_bytes','verified_subset_rss_bytes','uncertain','alerts']},ensure_ascii=False), 'PIDS', [r['pid'] for r in sample['members']], 'EXITS',[(r['expected']['pid'],r['status']) for r in fields['confirmed_exits']])
    for event in run['final_events']:
        row=event['event']
        if row['kind'] in ['START','ROOT_BOUND']:continue
        leaf=row.get('leaf',{})
        print('EVENT',event['line'],row['kind'],row['at_utc8'],leaf.get('pid'),leaf.get('exe'),row.get('first_verified_sample'),row.get('uncertain'),row.get('status'))
    print('SUP',run['supervisor'])
    print('CONSUMER',run['consumer'])
    print('CONSUMPTION',[(r['line'],r['row']['status'],r['row'].get('reasons')) for r in run['last_consumption']])
