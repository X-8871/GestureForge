"""直接保存原生Python子进程退出码，避免外层Shell退出状态混淆。"""
from pathlib import Path
import subprocess,json,time,sys,hashlib
W=Path(__file__).resolve().parent;R=W.parents[3];records=[]
for name,argv in [('static',['verification/check_s2b_inference_platform.py']),('evidence',['verification/check_stage_delivery.py','--mode','evidence','--manifest','report/evidence/S2B-T17/coordinates_20261011_r04/delivery_manifest.json']),('inputs',['verification/check_stage_delivery.py','--mode','inputs','--manifest','report/evidence/S2B-T17/coordinates_20261011_r04/delivery_manifest.json'])]:
    cmd=[sys.executable,'-B',*argv];p=W/(name+'_native.log');start=time.monotonic()
    with p.open('x',encoding='utf-8') as f: result=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
    records.append({'name':name,'command':cmd,'native_exit_code':result.returncode,'seconds':time.monotonic()-start,'log':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'peak_memory':'NOT_MEASURED'})
(W/'checker_native_receipt.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(records))
assert [row['native_exit_code'] for row in records]==[0,0,2]
