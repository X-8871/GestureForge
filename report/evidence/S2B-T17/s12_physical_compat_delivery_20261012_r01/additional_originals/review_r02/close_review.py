"""审查STOP后固定本次隔离原件索引，拒绝被审版本漂移。"""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).parent;ROOT=Path(__file__).parents[4]
WORK=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r02'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(65536),b''):h.update(block)
    return h.hexdigest()
assert sha(WORK/'final_draft_binding.json')=='8513ce1d1ea8a563fdc1e73f7ea57dca7be9bc63b81794d808a0d61af9f83562'
entry=json.loads((WORK/'final_draft_binding.json').read_text(encoding='utf-8'))
for row in entry['files']:assert sha(WORK/row['path'])==row['sha256']
receipt=OUT/'final_review_receipt.json'
assert sha(receipt)=='018c5773edf8a56c0fc6e2eaf068c164ef7f987244621e2720cc95ca777cc3dc'
rows=[]
for path in sorted(OUT.rglob('*')):
    if path.is_file():rows.append(dict(path=path.relative_to(OUT).as_posix(),absolute_path=str(path),sha256=sha(path),bytes=path.stat().st_size))
target=OUT/'raw_manifest.jsonl'
with target.open('x',encoding='utf-8',newline='\n') as stream:
    for row in rows:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(status='STOP_PASS_COMPAT_LOGIC_G2_ONLY',receipt_sha256=sha(receipt),raw_manifest_sha256=sha(target),files=len(rows),native_exit_code=0),ensure_ascii=False))
