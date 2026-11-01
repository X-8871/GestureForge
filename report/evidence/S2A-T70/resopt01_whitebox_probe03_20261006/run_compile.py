import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

work = Path(__file__).resolve().parent
toolchain = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
tool_bin = toolchain / "mingw64" / "bin"
make_bin = toolchain / "usr" / "bin"
verilator = tool_bin / "verilator_bin.exe"
compiler = tool_bin / "g++.exe"
make = make_bin / "make.exe"
verilator_root = toolchain / "mingw64" / "share" / "verilator"
queries = work / "queries.bin"
sources = [work / "source" / name for name in (
    "s2a_network_descriptor_pkg.sv", "s2a_conv_tile_engine.sv", "tb_s2a_conv_tile_unit.sv")]

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

expected_queries = "676e4feba5c21feac52547ddaea7288dca0a9278d83922dff017fa1d8356bedf"
if sha(queries) != expected_queries:
    raise SystemExit("查询数据摘要不符")
for path in [verilator, compiler, make, *sources]:
    if not path.is_file():
        raise SystemExit(f"文件缺失: {path}")
if not verilator_root.is_dir():
    raise SystemExit(f"Verilator 数据目录缺失: {verilator_root}")
env = os.environ.copy()
env["PATH"] = str(make_bin) + os.pathsep + str(tool_bin) + os.pathsep + env.get("PATH", "")
env["VERILATOR_ROOT"] = str(verilator_root)
resolved_compiler = shutil.which("g++", path=env["PATH"])
resolved_make = shutil.which("make", path=env["PATH"])
versions = {}
for key, executable in (("verilator", str(verilator)), ("compiler", resolved_compiler), ("make", resolved_make)):
    if not executable:
        raise SystemExit(f"工具未解析: {key}")
    result = subprocess.run([executable, "--version"], cwd=work, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=30, check=False)
    versions[key] = {"path": str(Path(executable).resolve()), "exit_code": result.returncode,
                     "output": result.stdout.strip()}
    if result.returncode:
        raise SystemExit(f"读取工具版本失败: {key} exit={result.returncode} {result.stdout}")
py = r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
makeflags = "PYTHON3='" + chr(34) + py + chr(34) + "'"
command = [str(verilator), "--binary", "--timing", "-Wno-fatal", "-j", "1", "--threads", "1",
           "--top-module", "tb_s2a_conv_tile_unit", "--Mdir", "obj_dir", "-MAKEFLAGS", makeflags,
           "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0", *[str(Path("source") / p.name) for p in sources]]
record = {"status": "RUNNING", "work": str(work), "python": sys.executable, "toolchain": str(toolchain),
          "verilator_root": str(verilator_root), "verilator_root_exists": verilator_root.is_dir(),
          "PATH": env["PATH"], "CC": env.get("CC"), "CXX": env.get("CXX"),
          "resolved_compiler": versions["compiler"], "resolved_make": versions["make"],
          "verilator": versions["verilator"], "makeflags": makeflags, "command": command,
          "query_sha256": sha(queries), "source_sha256": {p.name: sha(p) for p in sources},
          "tool_sha256": {str(p): sha(p) for p in (verilator, compiler, make)},
          "timeout_seconds": 1200}
(work / "compile_environment.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
started = time.monotonic()
with (work / "compile.log").open("xb") as log:
    result = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT,
                            timeout=1200, check=False)
record["status"] = "PASS_COMPILE" if result.returncode == 0 else "FAILED_COMPILE"
record["exit_code"] = result.returncode
record["duration_seconds"] = round(time.monotonic() - started, 3)
record["source_sha256_after"] = {p.name: sha(p) for p in sources}
record["source_unchanged"] = record["source_sha256"] == record["source_sha256_after"]
record["compile_log_sha256"] = sha(work / "compile.log")
record["compile_log"] = str(work / "compile.log")
(work / "compile_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: record[k] for k in ("status", "exit_code", "duration_seconds", "resolved_compiler", "makeflags", "compile_log")}, indent=2))
raise SystemExit(result.returncode)