import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

work = Path(__file__).resolve().parent
sim = work / "sim"
source_dir = work / "source"
fixture = work / "fixture"
tool = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
tool_bin = tool / "mingw64" / "bin"
make_bin = tool / "usr" / "bin"
verilator = tool_bin / "verilator_bin.exe"
compiler = tool_bin / "g++.exe"
make = make_bin / "make.exe"
verilator_root = tool_bin / ".." / "share" / "verilator"
python = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
binary = sim / "obj_dir" / "Vtb_s2a_t66_layer0_tile.exe"
sources = [source_dir / name for name in (
    "s2a_network_descriptor_pkg.sv", "s2a_conv_tile_engine.sv", "tb_s2a_t66_layer0_tile.sv")]
fixture_files = [fixture / name for name in (
    "sample0_input_chw_int8.bin", "sample0_layer0_gf8_weights.bin", "sample0_layer0_expected_nchw_int8.bin")]

def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

for path in [sim, source_dir, fixture, verilator, compiler, make, *sources, *fixture_files]:
    if not path.exists():
        raise SystemExit("required path missing: " + str(path))
if binary.exists() or (sim / "obj_dir").exists():
    raise SystemExit("T66 obj_dir already exists; refusing reuse")
env = os.environ.copy()
env["PATH"] = str(make_bin) + os.pathsep + str(tool_bin) + os.pathsep + env.get("PATH", "")
env["VERILATOR_ROOT"] = str(verilator_root.resolve())
py = str(python)
posix_compiler = "/d/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/g++.exe"
makeflags = "PYTHON3='" + chr(34) + py + chr(34) + "' CXX=" + posix_compiler + " LINK=" + posix_compiler
command = [str(verilator), "--binary", "--timing", "-Wno-fatal", "-j", "1", "--threads", "1",
           "--top-module", "tb_s2a_t66_layer0_tile", "--Mdir", "obj_dir",
           "-MAKEFLAGS", makeflags, "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0",
           *[str(path.resolve()) for path in sources]]
record = {
    "schema": "s2a_resopt02_t66_compile_record_v1",
    "status": "COMPILING",
    "source_sha256": {str(path): sha(path) for path in sources},
    "fixture_sha256": {str(path): sha(path) for path in fixture_files},
    "verilator": str(verilator.resolve()),
    "compiler": str(compiler.resolve()),
    "make": str(make.resolve()),
    "VERILATOR_ROOT": env["VERILATOR_ROOT"],
    "PATH": env["PATH"],
    "MAKEFLAGS": makeflags,
    "command": command,
    "working_directory": str(sim),
    "timeout_seconds": 900,
}
(work / "compile_environment.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
started = time.monotonic()
with (work / "compile.log").open("xb") as log:
    compile_result = subprocess.run(command, cwd=sim, env=env, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=900, check=False)
record["exit_code"] = compile_result.returncode
record["duration_seconds"] = round(time.monotonic() - started, 3)
record["status"] = "PASS_COMPILE" if compile_result.returncode == 0 else "FAILED_COMPILE"
record["compile_log_sha256"] = sha(work / "compile.log")
record["source_sha256_after"] = {str(path): sha(path) for path in sources}
record["source_unchanged"] = record["source_sha256"] == record["source_sha256_after"]
(work / "compile_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": record["status"], "exit_code": record["exit_code"],
                  "duration_seconds": record["duration_seconds"], "log": str(work / "compile.log")}, indent=2))
if compile_result.returncode != 0:
    raise SystemExit(compile_result.returncode)
if not binary.is_file():
    raise SystemExit("exact T66 generated binary missing: " + str(binary))
simulation_record = {
    "schema": "s2a_resopt02_t66_full_layer0_simulation_v1",
    "status": "RUNNING",
    "top_module": "tb_s2a_t66_layer0_tile",
    "source_sha256": record["source_sha256_after"],
    "fixture_sha256": record["fixture_sha256"],
    "binary_path": str(binary.resolve()),
    "binary_sha256": sha(binary),
    "command": [str(binary.resolve())],
    "working_directory": str(sim),
    "timeout_seconds": 1800,
}
(work / "simulation_execution_record.json").write_text(json.dumps(simulation_record, indent=2) + "\n", encoding="utf-8")
started = time.monotonic()
try:
    with (work / "simulation.log").open("xb") as log:
        simulation_result = subprocess.run([str(binary.resolve())], cwd=sim, env=env,
                                           stdout=log, stderr=subprocess.STDOUT,
                                           timeout=1800, check=False)
    simulation_record["exit_code"] = simulation_result.returncode
    simulation_record["status"] = "PASS" if simulation_result.returncode == 0 else "FAILED"
except subprocess.TimeoutExpired:
    simulation_record["exit_code"] = None
    simulation_record["status"] = "TIMEOUT_30_MINUTES"
simulation_record["duration_seconds"] = round(time.monotonic() - started, 3)
simulation_record["log_sha256"] = sha(work / "simulation.log")
simulation_log = (work / "simulation.log").read_text(encoding="utf-8", errors="replace")
simulation_record["pass_marker_count"] = simulation_log.count("PASS: T66 sample0 layer0 full tensor matched T25")
simulation_record["fatal_marker_count"] = simulation_log.count("%Fatal") + simulation_log.count("$fatal")
simulation_record["progress_markers"] = [line for line in simulation_log.splitlines()
                                         if "T66_PROGRESS" in line or "progress" in line.lower()]
simulation_record["final_pass_line"] = next((line for line in simulation_log.splitlines()
                                              if line.startswith("PASS: T66 sample0 layer0 full tensor")), None)
(work / "simulation_execution_record.json").write_text(json.dumps(simulation_record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(simulation_record, indent=2))
raise SystemExit(simulation_record["exit_code"] if simulation_record["exit_code"] is not None else 124)