"""保存provenance补充的原始输出与独立三字段索引。"""
import hashlib,json,subprocess,sys,time
from pathlib import Path
W=Path(__file__).parent;ROOT=W.parents[3];t=time.monotonic();command=[sys.executable,'-B','-X','utf8',str(W/'provenance.py')];p=subprocess.run(command,capture_output=True,cwd=W)
for name,data in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
    with (W/name).open('xb') as f:f.write(data)
n=dict(command=command,native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-t,peak_memory_bytes=None)
with (W/'native_receipt.json').open('x',encoding='utf-8') as f:json.dump(n,f,ensure_ascii=False,indent=2)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_r04_review_20261012_r01'/n for n in ('final_review_receipt.json','raw_manifest.jsonl')]+[ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02'/n for n in ('guard.py','supervisor.py','tool_receipt_r04_r02.json')]
rows=[dict(path=f.relative_to(ROOT).as_posix(),sha256=sha(f),role='source' if f.suffix=='.py' else 'log' if f.suffix=='.log' else 'input' if f in inputs else 'result') for f in inputs+list(W.iterdir()) if f.is_file()]
with (W/'raw_manifest.jsonl').open('x',encoding='utf-8') as f:
    for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(p.stdout.decode('utf-8'));print(p.stderr.decode('utf-8'));print(json.dumps(dict(native=n,supplement_sha256=sha(W/'provenance_supplement.json') if (W/'provenance_supplement.json').exists() else None,raw_sha256=sha(W/'raw_manifest.jsonl'),raw_rows=len(rows)),ensure_ascii=False));raise SystemExit(p.returncode)
