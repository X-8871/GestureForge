import hashlib
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
OUT=Path(__file__).resolve().parent
report=json.loads((OUT/'review_report.json').read_text(encoding='utf-8'))
native_records={}
for p in OUT.glob('*.native.json'):
    d=json.loads(p.read_text(encoding='utf-8'))
    assert d['direct_wait'] and d['native_child_wait']==0
    native_records[p.name]=d
assert 'finish_r01.native.json' in native_records
files=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name not in ['original_file_index.json','final_stop_receipt.json']:
        b=p.read_bytes()
        files.append({'path':str(p.relative_to(OUT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
index={'files':files,'count':len(files),'total_bytes':sum(x['bytes'] for x in files),'excluded_cache':[],'checkpoint_not_copied':'实际DCP仅在review_report/supplement_result中绑定完整路径、SHA和字节；本审查原件索引不声称包含DCP字节。'}
ip=OUT/'original_file_index.json'
assert not ip.exists()
ip.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt={'status':'PASS_PNR_STA_ONLY','stop':True,'reviewed_manifest':report['manifest'],'source_commit':report['source_commit'],'production_commit':report['production_commit'],'review_report_sha256':hashlib.sha256((OUT/'review_report.json').read_bytes()).hexdigest(),'original_file_index_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'original_file_count':len(files),'original_total_bytes':index['total_bytes'],'independent_actual_native_waits':native_records,'machine_checks':report['machine_checks'],'bit_input_decision':report['bit_input_decision'],'fixed_postroute_checkpoint':report['fixed_postroute_checkpoint'],'limits':report['limits'],'continuous_budget':'BLOCKED_NOT_PROVEN_CONTINUOUS','time_utc8':datetime.now(timezone(timedelta(hours=8))).isoformat(),'findings':[]}
rp=OUT/'final_stop_receipt.json'
assert not rp.exists()
rp.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'stop':True,'count':len(files),'bytes':index['total_bytes'],'index_sha256':receipt['original_file_index_sha256'],'receipt_sha256':hashlib.sha256(rp.read_bytes()).hexdigest()},ensure_ascii=False))
