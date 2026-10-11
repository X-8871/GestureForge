"""核对历史Git字节与当前原件的换行差异。"""
import hashlib, subprocess,json
from pathlib import Path
w=Path(__file__).resolve().parent;r=w.parents[3]
f=json.loads((r/'report/evidence/S2B-T17/route_specialization_20261011_r07/source_freeze.json').read_text(encoding='utf-8'))
for p,d in f['frozen14_sha256'].items():
    x=(r/p).read_bytes()
    rows=[]
    for commit in ['671f9cf494b92ce182b3f1542fefd0cfd4b209f5','5a676b700af4c27297977379417b1694dd64840e']:
        y=subprocess.check_output(['git','show',commit+':'+p],cwd=r)
        rows.append({'commit':commit,'sha':hashlib.sha256(y).hexdigest(),'bytes':len(y),'crlf':y.count(b'\r\n'),'lf_normalized_equal':x.replace(b'\r\n',b'\n')==y.replace(b'\r\n',b'\n')})
    print(p, {'actual_sha':hashlib.sha256(x).hexdigest(),'bytes':len(x),'crlf':x.count(b'\r\n'),'declared':d,'git':rows})
