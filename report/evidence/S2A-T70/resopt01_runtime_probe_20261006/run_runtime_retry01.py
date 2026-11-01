import hashlib,json,os,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
binary=(work/"obj_dir"/"Vtb_runtime.exe").resolve()
tool=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
make_bin=tool/"usr"/"bin"
tool_bin=tool/"mingw64"/"bin"
verilator=tool_bin/"verilator_bin.exe"
env=os.environ.copy()
env["PATH"]=str(make_bin)+os.pathsep+str(tool_bin)+os.pathsep+env.get("PATH","")
env["VERILATOR_ROOT"]=str(tool/"mingw64"/"share"/"verilator")
if not binary.is_file(): raise SystemExit(f"binary 不存在: {binary}")
if (work/"simulation_retry01.log").exists() or (work/"runtime_execution_retry01.json").exists(): raise SystemExit("拒绝覆盖")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
version=subprocess.run([str(verilator),"--version"],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
record={"schema":"resopt01_minimal_runtime_execution_v1","status":"RUNNING","top_module":"tb_runtime","verilator_path":str(verilator.resolve()),"verilator_version":version,"generated_binary_path":str(binary),"generated_binary_sha256":sha(binary),"source_path":str((work/"tb_runtime.sv").resolve()),"source_sha256":sha(work/"tb_runtime.sv"),"PATH":env["PATH"],"VERILATOR_ROOT":env["VERILATOR_ROOT"],"simulation_command":[str(binary)],"working_directory":str(work),"timeout_seconds":10,"started_utc":datetime.now(timezone.utc).isoformat()}
(work/"runtime_execution_retry01.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
start=time.monotonic()
try:
    with (work/"simulation_retry01.log").open("xb") as f: result=subprocess.run([str(binary)],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=10,check=False)
    record["exit_code"]=result.returncode
    output=(work/"simulation_retry01.log").read_text(encoding="utf-8",errors="replace")
    record["log_text"]=output
    record["pass_marker_count"]=output.count("PASS RUNTIME_PROBE")
    record["status"]="PASS_RUNTIME_PROBE" if result.returncode==0 and record["pass_marker_count"]==1 else "FAILED_RUNTIME_PROBE"
except subprocess.TimeoutExpired:
    record["exit_code"]=None
    record["status"]="TIMEOUT_RUNTIME_PROBE"
record["duration_seconds"]=round(time.monotonic()-start,3)
record["log_sha256"]=sha(work/"simulation_retry01.log")
(work/"runtime_execution_retry01.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record.get(k) for k in ("status","verilator_version","generated_binary_path","exit_code","duration_seconds","log_text","pass_marker_count")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_RUNTIME_PROBE" else 1)