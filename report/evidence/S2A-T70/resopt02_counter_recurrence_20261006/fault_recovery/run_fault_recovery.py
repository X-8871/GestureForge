import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

work = Path(__file__).resolve().parent
repo = Path(r"D:\FPGA_Competition")
tool = Path(r"D:\FPGA_S2A_MSYS2_20261001\env")
python = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
pwsh = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe")
runner = work / "run_backend_fault_recovery.ps1"
run_name = "protocol_directed12"
run_dir = work / run_name
if run_dir.exists():
    raise SystemExit("fault evidence target already exists")
env = os.environ.copy()
usr_bin = tool / "usr" / "bin"
mingw_bin = tool / "mingw64" / "bin"
env["PATH"] = str(usr_bin) + os.pathsep + str(mingw_bin) + os.pathsep + env.get("PATH", "")
env["VERILATOR_ROOT"] = str(mingw_bin / ".." / "share" / "verilator")
env["SHELL"] = str(usr_bin / "sh.exe")
posix_compiler = "/d/FPGA_S2A_MSYS2_20261001/env/mingw64/bin/g++.exe"
env["MAKEFLAGS"] = "PYTHON3='" + chr(34) + str(python) + chr(34) + "' CXX=" + posix_compiler + " LINK=" + posix_compiler
preflight_command = [
    str(pwsh), "-NoProfile", "-Command",
    "$ErrorActionPreference='Stop'; Get-Command Get-FileHash -ErrorAction Stop | Out-Null; where.exe uname; where.exe g++; where.exe make; g++.exe --version | Select-Object -First 1; Get-Command make.exe,g++.exe -CommandType Application | Select-Object Name,Source | ConvertTo-Json -Compress"
]
preflight_started = time.monotonic()
preflight = subprocess.run(preflight_command, cwd=repo, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, timeout=30, check=False)
record = {
    "schema": "s2a_resopt02_fault_runner_environment_v1",
    "runner": str(runner),
    "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
    "repo": str(repo),
    "python": str(python),
    "pwsh": str(pwsh),
    "toolchain": str(tool),
    "PATH": env["PATH"],
    "VERILATOR_ROOT": env["VERILATOR_ROOT"],
    "SHELL": env["SHELL"],
    "MAKEFLAGS": env["MAKEFLAGS"],
    "PSModulePath": env.get("PSModulePath"),
    "preflight_command": preflight_command,
    "preflight_exit_code": preflight.returncode,
    "preflight_output": preflight.stdout,
    "preflight_duration_seconds": round(time.monotonic() - preflight_started, 3),
}
(work / "toolchain_preflight.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
if preflight.returncode != 0:
    record["status"] = "FAILED_PREFLIGHT"
    (work / "launcher_execution_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(preflight.returncode)
command = [str(pwsh), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(runner),
           "-EvidenceRunName", run_name]
record["command"] = command
record["working_directory"] = str(repo)
record["timeout_seconds"] = 1800
started = time.monotonic()
result = subprocess.run(command, cwd=repo, env=env, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, timeout=1800, check=False)
record["status"] = "PASS_LAUNCHER" if result.returncode == 0 else "FAILED_LAUNCHER"
record["exit_code"] = result.returncode
record["duration_seconds"] = round(time.monotonic() - started, 3)
record["stdout"] = result.stdout
record["evidence_directory"] = str(run_dir)
(work / "launcher_execution_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: record[key] for key in ("status", "exit_code", "duration_seconds", "evidence_directory", "stdout")}, indent=2))
raise SystemExit(result.returncode)