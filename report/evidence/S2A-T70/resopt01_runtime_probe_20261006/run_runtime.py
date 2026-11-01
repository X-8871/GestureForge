import hashlib,json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
binary=(work/"obj_dir"/"Vtb_runtime.exe").resolve()
verilator=Path(r"D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe")
source=work/"tb_runtime.sv"
if not binary.is_file(): raise SystemExit(f"精确 runtime binary 不存在: {binary}")
if not source.is_file(): raise SystemExit("runtime source 缺失")
if (work/"runtime_execution_record.json").exists() or (work/"simulation.log").exists(): raise SystemExit("拒绝覆盖既有运行证据")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
version=subprocess.run([str(verilator),"--version"],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
record={"schema":"resopt01_minimal_runtime_execution_v1","status":"RUNNING","top_module":"tb_runtime","verilator_path":str(verilator.resolve()),"verilator_version":version,"generated_binary_path":str(binary),"generated_binary_sha256":sha(binary),"source_path":str(source.resolve()),"source_sha256":sha(source),"verilator_compile_command":[str(verilator),"--binary","--timing","-Wno-fatal","-j","1","--threads","1","--top-module","tb_runtime","--Mdir","obj_dir"],"simulation_command":[str(binary)],"working_directory":str(work),"timeout_seconds":10,"started_utc":datetime.now(timezone.utc).isoformat()}
(work/"runtime_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
start=time.monotonic()
try:
    with (work/"simulation.log").open("xb") as output: result=subprocess.run([str(binary)],cwd=work,stdout=output,stderr=subprocess.STDOUT,timeout=10,check=False)
    record["exit_code"]=result.returncode
    record["duration_seconds"]=round(time.monotonic()-start,3)
    output_text=(work/"simulation.log").read_text(encoding="utf-8",errors="replace")
    record["log_text"]=output_text
    record["pass_marker_count"]=output_text.count("PASS RUNTIME_PROBE")
    record["status"]="PASS_RUNTIME_PROBE" if result.returncode==0 and record["pass_marker_count"]==1 else "FAILED_RUNTIME_PROBE"
except subprocess.TimeoutExpired:
    record["duration_seconds"]=round(time.monotonic()-start,3)
    record["status"]="TIMEOUT_RUNTIME_PROBE"
    record["exit_code"]=None
record["log_sha256"]=sha(work/"simulation.log")
(work/"runtime_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record.get(k) for k in ("status","top_module","verilator_version","generated_binary_path","exit_code","duration_seconds","log_text")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_RUNTIME_PROBE" else 1)