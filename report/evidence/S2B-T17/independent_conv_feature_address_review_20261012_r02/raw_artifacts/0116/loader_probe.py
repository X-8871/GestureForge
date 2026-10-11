"""保留补充仿真未继承工具DLL路径的真实启动失败。"""
from pathlib import Path
import subprocess,sys,json,time,hashlib
WORK=Path(__file__).resolve().parent
cmd=[str(WORK/'build/Vtb_combined.exe'),'+VECTOR_PATH='+str(WORK/'feature_vectors_consumed_r01.txt').replace('\\','/')]
started=time.monotonic();done=subprocess.run(cmd,cwd=WORK,capture_output=True)
log=WORK/'simulation_loader_failure.log';log.write_bytes(done.stdout+done.stderr)
record={'command':subprocess.list2cmdline(cmd),'native_exit_code':done.returncode,'elapsed_seconds':round(time.monotonic()-started,3),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'reason':'补充脚本未继承MSYS2 DLL路径；只重现启动失败，原compile/首仿真成功原件不改。','original_finalize_native_exit_code':1,'original_child_native_exit_code':None}
(WORK/'loader_failure.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False));assert done.returncode!=0
