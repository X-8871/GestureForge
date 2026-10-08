"""独立运行原构建器并记录原生退出与语义退出，不修改冻结源码。"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta


ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"
ARTIFACT = ROOT / "report/evidence/S2B-T06/b01"
VITIS = Path(r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat")


def digest(path):
    """绑定实际原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(name, value):
    """新建UTF-8审查证据，拒绝覆盖。"""
    with (REVIEW / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    """只启动本次离线构建，实物接口保持未运行。"""
    ps_command = r"$s2bP=Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'vivado|vitis|arm-none|hw_server|cs_server|xsdb|xelab|xsim|ninja|cmake|make|python' }; @{processes=@($s2bP | Select-Object Name,ProcessId,ParentProcessId,CommandLine);memory=(Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory)} | ConvertTo-Json -Depth 5"
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps_command], capture_output=True, check=False)
    preflight = {"command": ["powershell.exe", "-NoProfile", "-Command", ps_command], "exit_code": proc.returncode,
                 "raw_stdout": proc.stdout.decode("utf-8", errors="replace"), "raw_stderr": proc.stderr.decode("utf-8", errors="replace"),
                 "disk": dict(zip(("total", "used", "free"), shutil.disk_usage(ROOT))), "hardware_execution": "NOT_RUN"}
    write_new("preflight.json", preflight)
    if proc.returncode != 0:
        raise RuntimeError("进程/内存预检失败，未启动构建")
    argv = [str(VITIS), "-s", str(ROOT / "vitis/build_s2b_ps_smoke.py")]
    task_env = {"S2B_PS_SMOKE_MODE": "build", "S2B_PS_SMOKE_CONFIG": str(REVIEW / "build_config.json"), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    env = dict(os.environ, **task_env)
    started = time.monotonic()
    record = {"command": argv, "cwd": str(ROOT), "task_environment": task_env,
              "config_sha256": digest(REVIEW / "build_config.json"), "attempts": 1,
              "started_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "native_exit_code": None, "effective_exit_code": 1, "hardware_execution": "NOT_RUN",
              "full_process_tree_peak_memory": "NOT_MEASURED", "stop_condition": "异常或30分钟无控制台进度"}
    log = REVIEW / "rebuild_console.log"
    with log.open("xb") as stream:
        child = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        record["own_cli_pid"] = child.pid
        print(json.dumps({"started": argv, "pid": child.pid, "log": str(log)}, ensure_ascii=False), flush=True)
        previous_size = 0
        progress_at = time.monotonic()
        while child.poll() is None:
            size = log.stat().st_size
            if size != previous_size:
                progress_at = time.monotonic()
                previous_size = size
            if time.monotonic() - progress_at > 1800:
                stop = subprocess.run(["taskkill.exe", "/PID", str(child.pid), "/T", "/F"], capture_output=True, check=False)
                record["own_cli_timeout_stop"] = {"command": ["taskkill.exe", "/PID", str(child.pid), "/T", "/F"], "exit_code": stop.returncode,
                                                 "stdout": stop.stdout.decode("utf-8", errors="replace"), "stderr": stop.stderr.decode("utf-8", errors="replace")}
                child.wait()
                break
            time.sleep(2)
        record["native_exit_code"] = child.returncode
    details_path = ARTIFACT / "build_details.json"
    if details_path.is_file():
        details = json.loads(details_path.read_text(encoding="utf-8"))
        calls = {item["name"]: item for item in details.get("api_calls", []) if item["name"] in ("platform.build", "app.build", "initializer.build")}
        api_success = len(calls) == 3 and all(item.get("return_type") == "int" and item.get("return_repr") == "0" for item in calls.values())
        record.update(build_details_status=details.get("status"), build_details_sha256=digest(details_path), build_api_results=calls,
                      original_commands=details.get("commands", []), own_server_pid=details.get("own_server_pid"), own_server_cleanup=details.get("own_server_cleanup"))
        if record["native_exit_code"] == 0 and details.get("status") == "PASS_OFFLINE_BUILD_AND_LAYOUT" and api_success and b"S2B_PS_SMOKE_BUILD_OK hardware_execution=NOT_RUN" in log.read_bytes():
            record["effective_exit_code"] = 0
    record.update(elapsed_seconds=time.monotonic() - started, console_sha256=digest(log),
                  finished_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat())
    write_new("rebuild_receipt.json", record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record["effective_exit_code"]


if __name__ == "__main__":
    sys.exit(main())
