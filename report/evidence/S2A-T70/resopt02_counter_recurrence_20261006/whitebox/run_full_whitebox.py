import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
binary=(work/"obj_dir"/"Vtb_s2a_conv_tile_unit.exe").resolve()
if not binary.is_file(): raise SystemExit(f"required generated executable is missing: {binary}")
log_path=work/"simulation.log"
record_path=work/"simulation_execution_record.json"
if log_path.exists() or record_path.exists(): raise SystemExit("refuse overwrite of simulation evidence")
tool=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
make_bin=tool/"usr"/"bin"; tool_bin=tool/"mingw64"/"bin"; root=tool/"mingw64"/"share"/"verilator"
verilator=tool_bin/"verilator_bin.exe"
env=os.environ.copy(); env["PATH"]=str(make_bin)+os.pathsep+str(tool_bin)+os.pathsep+env.get("PATH",""); env["VERILATOR_ROOT"]=str(root)
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""): h.update(block)
    return h.hexdigest()
compile_path=work/"compile_record.json"
if not compile_path.is_file(): raise SystemExit("compile_record.json missing")
compile_record=json.loads(compile_path.read_text(encoding="utf-8"))
if compile_record.get("status")!="PASS_COMPILE" or compile_record.get("exit_code")!=0: raise SystemExit("compile evidence is not PASS")
if not verilator.is_file() or not root.is_dir(): raise SystemExit("Verilator installation closure is incomplete")
version=subprocess.run([str(verilator),"--version"],cwd=work,env=env,capture_output=True,text=True,timeout=30,check=True).stdout.strip()
compiler=shutil.which("g++",path=env["PATH"])
if not compiler or Path(compiler).resolve()!=(tool_bin/"g++.exe").resolve(): raise SystemExit(f"compiler resolution mismatch: {compiler}")
compiler_version=subprocess.run([compiler,"--version"],cwd=work,env=env,capture_output=True,text=True,timeout=30,check=True).stdout.strip()
command=[str(binary)]
record={"schema":"resopt01_t70_full_whitebox_execution_v1","status":"RUNNING","top_module":"tb_s2a_conv_tile_unit","verilator_path":str(verilator.resolve()),"verilator_version":version,"generated_binary_path":str(binary),"generated_binary_sha256":sha(binary),"resolved_compiler_path":str(Path(compiler).resolve()),"compiler_version":compiler_version,"PATH":env["PATH"],"VERILATOR_ROOT":str(root),"source_sha256":compile_record["source_sha256_after"],"query_sha256":sha(work/"queries.bin"),"compile_record":str(compile_path.resolve()),"command":command,"working_directory":str(work),"timeout_seconds":1200,"started_utc":datetime.now(timezone.utc).isoformat()}
record_path.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
started=time.monotonic()
try:
    with log_path.open("xb") as f: result=subprocess.run(command,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1200,check=False)
    record["exit_code"]=result.returncode
except subprocess.TimeoutExpired:
    record["exit_code"]=None
    record["status"]="TIMEOUT_WHITEBOX"
text=log_path.read_text(encoding="utf-8",errors="replace") if log_path.exists() else ""
marker="PASS TILE_WHITEBOX queries=21336 lane_checks=169790"
record["pass_marker_count"]=text.count(marker)
record["fatal_marker_count"]=text.count("%Fatal:")
record["query_checkpoints"]=[line for line in text.splitlines() if line.startswith("CHECKPOINT TILE_WHITEBOX ")]
record["log_bytes"]=log_path.stat().st_size if log_path.exists() else 0
record["log_sha256"]=sha(log_path) if log_path.exists() else None
record["duration_seconds"]=round(time.monotonic()-started,3)
record["finished_utc"]=datetime.now(timezone.utc).isoformat()
if record.get("status")=="RUNNING": record["status"]="PASS_WHITEBOX_ARITHMETIC_ONLY" if record.get("exit_code")==0 and record["pass_marker_count"]==1 and record["fatal_marker_count"]==0 else "FAILED_WHITEBOX"
record_path.write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record.get(k) for k in ("status","exit_code","duration_seconds","pass_marker_count","fatal_marker_count","query_checkpoints","log_bytes","log_sha256","top_module","generated_binary_path","verilator_version","resolved_compiler_path")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_WHITEBOX_ARITHMETIC_ONLY" else (record.get("exit_code") or 1))