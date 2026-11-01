import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
binary=(work/"obj_dir"/"Vtb_s2a_conv_tile_unit.exe").resolve()
tool=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
make_bin=tool/"usr"/"bin"
tool_bin=tool/"mingw64"/"bin"
verilator=tool_bin/"verilator_bin.exe"
verilator_root=tool/"mingw64"/"share"/"verilator"
env=os.environ.copy()
env["PATH"]=str(make_bin)+os.pathsep+str(tool_bin)+os.pathsep+env.get("PATH","")
env["VERILATOR_ROOT"]=str(verilator_root)
if not binary.is_file(): raise SystemExit(f"精确 binary 不存在: {binary}")
if (work/"simulation_retry01.log").exists() or (work/"simulation_retry01_record.json").exists(): raise SystemExit("拒绝覆盖既有 retry")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
version=subprocess.run([str(verilator),"--version"],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
compiler=shutil.which("g++",path=env["PATH"])
if not compiler or Path(compiler).resolve()!= (tool_bin/"g++.exe").resolve(): raise SystemExit(f"compiler PATH 不符: {compiler}")
record={"schema":"resopt01_one_query_execution_v1","status":"RUNNING","top_module":"tb_s2a_conv_tile_unit","verilator_path":str(verilator.resolve()),"verilator_version":version,"generated_binary_path":str(binary),"generated_binary_sha256":sha(binary),"resolved_compiler_path":str(Path(compiler).resolve()),"PATH":env["PATH"],"VERILATOR_ROOT":str(verilator_root),"source_sha256":json.loads((work/"compile_record.json").read_text(encoding="utf-8"))["source_sha256_after"],"compile_record":str((work/"compile_record.json").resolve()),"simulation_command":[str(binary)],"working_directory":str(work),"timeout_seconds":30,"started_utc":datetime.now(timezone.utc).isoformat()}
(work/"simulation_retry01_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
start=time.monotonic()
try:
    with (work/"simulation_retry01.log").open("xb") as output: result=subprocess.run([str(binary)],cwd=work,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=30,check=False)
    record["exit_code"]=result.returncode
    text=(work/"simulation_retry01.log").read_text(encoding="utf-8",errors="replace")
    record["log_text"]=text
    record["status"]="PASS_FIRST_QUERY" if result.returncode==0 and text.count("PASS TILE_FIRST_QUERY")==1 else "FAILED_FIRST_QUERY"
except subprocess.TimeoutExpired:
    text=(work/"simulation_retry01.log").read_text(encoding="utf-8",errors="replace")
    record["exit_code"]=None
    record["log_text"]=text
    record["status"]="TIMEOUT_FIRST_QUERY"
record["duration_seconds"]=round(time.monotonic()-start,3)
record["log_bytes"]=(work/"simulation_retry01.log").stat().st_size
record["log_sha256"]=sha(work/"simulation_retry01.log")
record["observed_markers"]=[line for line in text.splitlines() if line.startswith(("PROBE ","PASS TILE_FIRST_QUERY"))]
(work/"simulation_retry01_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record.get(k) for k in ("status","exit_code","duration_seconds","log_bytes","observed_markers","log_text")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_FIRST_QUERY" else 1)