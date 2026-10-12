"""隔离原生包装；记录实际等待码及直接子身份，不追查外部进程。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

OUT=Path(__file__).absolute().parent
ROOT=OUT.parents[3]
def identity(pid):
    process=psutil.Process(pid); birth=process.create_time()
    row=dict(pid=pid,create_time=birth,exe=process.exe(),cwd=process.cwd(),cmdline=process.cmdline(),ppid=process.ppid())
    if not process.is_running() or psutil.Process(pid).create_time()!=birth: raise RuntimeError('直接子身份变化')
    return row

rows=[]
for label,arguments in [('independent_review',[str(OUT/'review.py')]),('evidence',[str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(ROOT/'report/evidence/S2B-T17/s13_launch_tools_20261012_r01/delivery_manifest_r02.json')])]:
    command=[sys.executable,'-X','utf8','-B',*arguments]; began=time.monotonic(); unknown=None
    stdout=OUT/(label+'.stdout.bin'); stderr=OUT/(label+'.stderr.bin')
    with stdout.open('xb') as so,stderr.open('xb') as se:
        child=subprocess.Popen(command,cwd=ROOT,stdout=so,stderr=se)
        try: before=identity(child.pid)
        except (psutil.Error,RuntimeError) as error: before=None; unknown=repr(error)
        code=child.wait(timeout=60)
    row=dict(label=label,command=command,actual_wait_exit_code=code,child_identity=before,identity_unknown=unknown,elapsed_seconds=time.monotonic()-began,stdout_sha256=hashlib.sha256(stdout.read_bytes()).hexdigest(),stderr_sha256=hashlib.sha256(stderr.read_bytes()).hexdigest(),entire_tree_terminal='UNKNOWN_NOT_ENUMERATED')
    try: row['same_direct_child_exists']=psutil.Process(child.pid).create_time()==before['create_time'] if before else None
    except psutil.NoSuchProcess: row['same_direct_child_exists']=False
    rows.append(row)
(OUT/'native_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))
raise SystemExit(0 if all(row['actual_wait_exit_code']==0 for row in rows) else 1)
