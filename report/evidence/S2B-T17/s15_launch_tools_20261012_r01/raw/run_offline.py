"""顺序执行轻量G1回归，包装保存真正直接wait原生码；失败后停止当前轮。"""
import json
from pathlib import Path
import subprocess
import sys
import time

W=Path(__file__).parent
ROOT=W.parents[3]
commands=[
 ('s15_g1_regressions_r03',[str(W/'s15_regressions.py'),'r03'],0),
 ('s15_g1_final_checks_r02',[str(W/'final_checks.py'),'r02'],0),
]
results=[]
for label,args,expected in commands:
    argv=[sys.executable,'-X','utf8','-B',str(W/'native_capture.py'),label,sys.executable,'-X','utf8','-B',*args]
    start=time.monotonic()
    with (W/(label+'.outer.stdout.bin')).open('xb') as out,(W/(label+'.outer.stderr.bin')).open('xb') as err:
        code=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW,timeout=120).returncode
    receipt=json.loads((W/(label+'.native.json')).read_text(encoding='utf-8'))
    result=dict(label=label,command=argv,outer_native_exit_code=code,inner_native_exit_code=receipt['native_exit_code'],expected=expected,
                elapsed_seconds=time.monotonic()-start,status='PASS' if code==expected and receipt['native_exit_code']==expected else 'FAIL_PRESERVED')
    results.append(result)
    print(json.dumps(result,ensure_ascii=False),flush=True)
    if result['status']!='PASS':break
with (W/'offline_result_r07.json').open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(dict(status='PASS_G1_ONLY' if len(results)==len(commands) and all(r['status']=='PASS' for r in results) else 'FAIL_PRESERVED',runs=results),stream,ensure_ascii=False,indent=2);stream.write('\n')
raise SystemExit(0 if len(results)==len(commands) and all(r['status']=='PASS' for r in results) else 1)
