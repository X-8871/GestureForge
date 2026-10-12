"""将独审索引补齐为真正JSONL，旧JSON索引及旧回执原样保留。"""
import hashlib
import json
from pathlib import Path
W=Path(__file__).resolve().parent
ROOT=W.parents[3]
old=json.loads((W/'raw_manifest.jsonl').read_text(encoding='utf-8'))
target=W/'raw_manifest_r02.jsonl'
with target.open('x',encoding='utf-8',newline='\n') as stream:
    for row in old['files']:
        path=ROOT/row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        stream.write(json.dumps(row,ensure_ascii=False)+'\n')
receipt=json.loads((W/'final_review_receipt.json').read_text(encoding='utf-8'))
receipt['raw_manifest']=dict(path=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size)
receipt['packaging_correction']='r01 raw_manifest扩展名JSONL实际为JSON对象；r02新增真正逐行JSONL，旧索引及receipt保留，不改变工具G2或测试结论。'
output=W/'final_review_receipt_r02.json'
with output.open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status=receipt['status'],path=output.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),raw_manifest_sha256=receipt['raw_manifest']['sha256']),ensure_ascii=False))
