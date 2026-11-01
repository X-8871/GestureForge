import hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from datetime import datetime,timezone
work=Path(__file__).resolve().parent
binary=(work/"obj_dir"/"Vtb_s2a_conv_tile_unit.exe").resolve()
tool=Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
make_bin=tool/"usr"/"bin"; tool_bin=tool/"mingw64"/"bin"; root=tool/"mingw64"/"share"/"verilator"
verilator=tool_bin/"verilator_bin.exe"
env=os.environ.copy(); env["PATH"]=str(make_bin)+os.pathsep+str(tool_bin)+os.pathsep+env.get("PATH",""); env["VERILATOR_ROOT"]=str(root)
if not binary.is_file(): raise SystemExit(f"binary missing: {binary}")
if (work/"simulation.log").exists() or (work/"simulation_execution_record.json").exists(): raise SystemExit("refuse overwrite")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
version=subprocess.run([str(verilator),"--version"],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
compiler=shutil.which("g++",path=env["PATH"])
if not compiler or Path(compiler).resolve()!=(tool_bin/"g++.exe").resolve(): raise SystemExit(f"compiler path mismatch: {compiler}")
compile_record=json.loads((work/"compile_record.json").read_text(encoding="utf-8"))
record={"schema":"resopt01_clean_one_query_execution_v1","status":"RUNNING","top_module":"tb_s2a_conv_tile_unit","verilator_path":str(verilator.resolve()),"verilator_version":version,"generated_binary_path":str(binary),"generated_binary_sha256":sha(binary),"resolved_compiler_path":str(Path(compiler).resolve()),"PATH":env["PATH"],"VERILATOR_ROOT":str(root),"source_sha256":compile_record["source_sha256_after"],"compile_record":str((work/"compile_record.json").resolve()),"command":[str(binary)],"working_directory":str(work),"timeout_seconds":30,"started_utc":datetime.now(timezone.utc).isoformat()}
(work/"simulation_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
start=time.monotonic()
try:
    with (work/"simulation.log").open("xb") as f: result=subprocess.run([str(binary)],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=30,check=False)
    record["exit_code"]=result.returncode
    text=(work/"simulation.log").read_text(encoding="utf-8",errors="replace")
    marker="PASS TILE_ONE_QUERY queries=1 lane_checks=8"
    record["pass_marker_count"]=text.count(marker)
    record["fatal_marker_count"]=text.count("%Fatal:")
    record["observed_markers"]=[line for line in text.splitlines() if line.startswith(("PROBE ","PASS TILE_"))]
    record["log_text"]=text
    record["status"]="PASS_ONE_QUERY" if result.returncode==0 and record["pass_marker_count"]==1 and record["fatal_marker_count"]==0 else "FAILED_ONE_QUERY"
except subprocess.TimeoutExpired:
    text=(work/"simulation.log").read_text(encoding="utf-8",errors="replace")
    record["exit_code"]=None; record["log_text"]=text; record["status"]="TIMEOUT_ONE_QUERY"
record["duration_seconds"]=round(time.monotonic()-start,3);record["log_bytes"]=(work/"simulation.log").stat().st_size;record["log_sha256"]=sha(work/"simulation.log")
(work/"simulation_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record.get(k) for k in ("status","exit_code","duration_seconds","log_bytes","pass_marker_count","fatal_marker_count","observed_markers")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_ONE_QUERY" else 1)