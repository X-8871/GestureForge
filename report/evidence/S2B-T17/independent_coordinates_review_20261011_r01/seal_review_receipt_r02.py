"""保存首版回执，修正重定向日志在首次封存后追加的自绑定问题。"""
from pathlib import Path
import json,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
W=Path(__file__).resolve().parent;R=W.parents[3]
def sha(p):
    """读取原始字节。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((W/'receipt.json').read_text(encoding='utf-8'));changed=[]
for row in data['files']:
    p=R/row['path']
    if sha(p)!=row['sha256']:
        changed.append(row['path'])
assert changed==[(W/'seal_stdout.log').relative_to(R).as_posix()]
data['receipt_revision']={'supersedes':'receipt.json','sha256':sha(W/'receipt.json'),'reason':'首版回执将当时仍为空的seal_stdout.log纳入，随后打印导致日志追加；原回执保留，本版封存已结束日志。','only_changed_prior_binding':changed}
evidence=[p for p in W.rglob('*') if p.is_file() and 'obj_dir' not in p.relative_to(W).parts and 'checker_fixture' not in p.relative_to(W).parts]
data['files']=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(evidence)]
assert not (W/'receipt_r02.json').exists()
(W/'receipt_r02.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for row in data['files']: assert sha(R/row['path'])==row['sha256']
print(json.dumps({'status':'PASS','receipt_sha256':sha(W/'receipt_r02.json'),'bound_files':len(data['files'])},ensure_ascii=False))
