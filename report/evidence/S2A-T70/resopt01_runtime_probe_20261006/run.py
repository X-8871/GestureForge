import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
tool=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
bin_dir=tool/"mingw64"/"bin"
make_dir=tool/"usr"/"bin"
verilator=bin_dir/"verilator_bin.exe"
gxx=bin_dir/"g++.exe"
make=make_dir/"make.exe"
root=tool/"mingw64"/"share"/"verilator"
source=work/"tb_runtime.sv"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
env=os.environ.copy()
env["PATH"]=str(make_dir)+os.pathsep+str(bin_dir)+os.pathsep+env.get("PATH","")
env["VERILATOR_ROOT"]=str(root)
py=r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
makeflags="PYTHON3='"+chr(34)+py+chr(34)+"'"
command=[str(verilator),"--binary","--timing","-Wno-fatal","-j","1","--threads","1","--top-module","tb_runtime","--Mdir","obj_dir","-MAKEFLAGS",makeflags,"-CFLAGS","-D_GLIBCXX_USE_CXX11_ABI=0",str(source)]
rec={"status":"RUNNING","python":sys.executable,"source_sha256":sha(source),"command":command,"PATH":env["PATH"],"CC":env.get("CC"),"CXX":env.get("CXX"),"VERILATOR_ROOT":str(root),"resolved_compiler":shutil.which("g++",path=env["PATH"]),"resolved_make":shutil.which("make",path=env["PATH"]),"tool_versions":{}}
for key,path in (("verilator",verilator),("compiler",Path(rec["resolved_compiler"])),("make",Path(rec["resolved_make"]))):
    rec["tool_versions"][key]=subprocess.run([str(path),"--version"],capture_output=True,text=True,timeout=30).stdout.strip()
start=time.monotonic()
with (work/"compile.log").open("xb") as f:
    compiled=subprocess.run(command,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,check=False)
rec["compile_exit_code"]=compiled.returncode
rec["compile_seconds"]=round(time.monotonic()-start,3)
if compiled.returncode:
    rec["status"]="FAILED_COMPILE"
else:
    binary=work/"obj_dir"/"tb_runtime.exe"
    rec["binary_sha256"]=sha(binary)
    start=time.monotonic()
    try:
        with (work/"simulation.log").open("xb") as f:
            simulated=subprocess.run([str(binary)],cwd=work,stdout=f,stderr=subprocess.STDOUT,timeout=10,check=False)
        rec["simulation_exit_code"]=simulated.returncode
        rec["simulation_seconds"]=round(time.monotonic()-start,3)
        text=(work/"simulation.log").read_text(encoding="utf-8",errors="replace")
        rec["simulation_log"]=text
        rec["status"]="PASS_RUNTIME_PROBE" if simulated.returncode==0 and text.count("PASS RUNTIME_PROBE")==1 else "FAILED_RUNTIME_PROBE"
    except subprocess.TimeoutExpired:
        rec["status"]="TIMEOUT_RUNTIME_PROBE"
        rec["simulation_seconds"]=round(time.monotonic()-start,3)
rec["compile_log_sha256"]=sha(work/"compile.log")
(work/"record.json").write_text(json.dumps(rec,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:rec.get(k) for k in ("status","compile_exit_code","compile_seconds","simulation_exit_code","simulation_seconds","simulation_log","resolved_compiler","tool_versions")},indent=2))
raise SystemExit(0 if rec["status"]=="PASS_RUNTIME_PROBE" else 1)