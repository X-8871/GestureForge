"""实际独立CLI进程的原生码验证，仅停止本次自有轻量叶进程。"""
from pathlib import Path
import subprocess,sys,json,time,psutil,hashlib
ROOT=Path.cwd();WORK=Path(__file__).resolve().parent;DIRECTORY=WORK/'cli_fixture';DIRECTORY.mkdir();started=time.monotonic()
marker=DIRECTORY/'pid.json';proc=subprocess.Popen([sys.executable,'-X','utf8','-B',str(WORK/'fixture.py'),'leaf',str(marker)],cwd=DIRECTORY)
p=psutil.Process(proc.pid);expected={'pid':p.pid,'create_time':p.create_time(),'exe':p.exe(),'cwd':p.cwd()}
try:
    while not marker.exists():assert time.monotonic()-started<3;time.sleep(.01)
    binding={**expected,'allowed_run_dirs':[expected['cwd']],'run_id':'cli_owned_fixture','source_commit':'1eed350c43aae4cdee1f8179a93ce87d75d9f2a8','fixture_test':True}
    b=DIRECTORY/'binding.json';b.write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    source=ROOT/'tmp/2B/S2B-T17/s10_resource_guard_20261012_r02/guard.py';plan=ROOT/'tmp/2B/S2B-T17/s10_root_run_20261012_r01/resource_plan.json'
    cmd=[sys.executable,'-X','utf8','-B',str(source),'--plan',str(plan),'--binding',str(b),'--output-dir',str(DIRECTORY/'guard'),'--fixture-tree-limit-bytes','1']
    done=subprocess.run(cmd,cwd=WORK,capture_output=True);(DIRECTORY/'stdout.log').write_bytes(done.stdout);(DIRECTORY/'stderr.log').write_bytes(done.stderr)
    receipt=json.loads((DIRECTORY/'guard/guard_receipt.json').read_text(encoding='utf-8'));assert done.returncode==2 and receipt['status']=='STOPPED' and not p.is_running()
    r={'status':'PASS','command':subprocess.list2cmdline(cmd),'native_exit_code':done.returncode,'seconds':round(time.monotonic()-started,3),'root_absent_after':True,'guard_receipt_sha256':hashlib.sha256((DIRECTORY/'guard/guard_receipt.json').read_bytes()).hexdigest()}
    (WORK/'cli_validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
finally:
    if p.is_running():
        q=psutil.Process(p.pid);assert q.create_time()==expected['create_time'] and q.exe()==expected['exe'] and q.cwd()==expected['cwd'];q.terminate();q.wait(timeout=3)
