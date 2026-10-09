"""只运行新的离线候选构建，保存原生退出码和实际构建结果。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
RUN = sys.argv[1] if len(sys.argv) > 1 else "ps_uart_clock_fix_20261009_171959_r01"
EVIDENCE = ROOT / "report/evidence/S2B-T06" / RUN
CACHE = ROOT / "tmp/2B/S2B-T06" / (sys.argv[2] if len(sys.argv) > 2 else RUN)
BASELINE = "117911e63cd7468418f11847ffedc9293dbca075"
VITIS = Path(r"D:\Xilinx\2026.1\Vitis\bin\vitis.bat")

def digest(path):
    """计算原始字节的绑定哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(name, value):
    """仅创建UTF-8证据，不覆盖任何原件。"""
    with (EVIDENCE / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

def main():
    """复用原构建器、固定XSA和上游依赖，仅新建本次产物。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "vitis"))
    from build_s2b_ps_smoke import exact_path
    for path, kind in ((ROOT, "directory"), (CACHE, "directory"), (EVIDENCE, "directory"),
                       (VITIS, "file"), (Path(__file__).absolute(), "file")):
        exact_path(path, kind)
    inputs = json.loads((ROOT / "report/evidence/S2B-T06/ps_smoke_20261008_r01/inputs_manifest_r03.json").read_text(encoding="utf-8"))
    inputs.update(run_id=RUN, source_commit=BASELINE, evidence_dir=(EVIDENCE.relative_to(ROOT).as_posix()))
    inputs["limitations"] = ["此清单仅复用已批准的同一PS平台离线输入。", "新版软件尚未独立审查或上板，不沿用旧版实测。", "不修改正式冻结，不执行任何硬件连接或初始化。"]
    write_new("inputs_manifest.json", inputs)
    argv = [str(VITIS), "-s", str(ROOT / "vitis/build_s2b_ps_smoke.py")]
    task_env = {"S2B_PS_SMOKE_MODE": "build", "S2B_PS_SMOKE_CONFIG": str(EVIDENCE / "build_config.json"), "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    config = {"schema_version": 1, "source_commit": BASELINE, "xsa": str(ROOT / inputs["files"][0]["path"]),
              "xsa_sha256": inputs["files"][0]["sha256"], "xsa_source_commit": "90652b45ef31e763bd3e6f7527e2fd080ece61a8",
              "inputs_manifest": str(EVIDENCE / "inputs_manifest.json"), "inputs_manifest_sha256": digest(EVIDENCE / "inputs_manifest.json"),
              "workspace": str(CACHE / "workspace"), "artifact_dir": str(EVIDENCE / "build"), "command": json.dumps({"argv": argv, "cwd": str(ROOT), "env": task_env}, ensure_ascii=False)}
    write_new("build_config.json", config)
    preflight_cmd = ["powershell.exe", "-NoProfile", "-Command", "$s2bPreflight=Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'vivado|vitis|arm-none|hw_server|xsdb|xelab|xsim|ninja|cmake|make|python' }; @{processes=@($s2bPreflight | Select-Object Name,ProcessId,ParentProcessId,CommandLine);memory=(Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory)} | ConvertTo-Json -Depth 5"]
    pre = subprocess.run(preflight_cmd, capture_output=True, check=False)
    write_new("preflight.json", {"command": preflight_cmd, "exit_code": pre.returncode,
              "stdout": pre.stdout.decode("utf-8", errors="replace"), "stderr": pre.stderr.decode("utf-8", errors="replace"),
              "disk_bytes": dict(zip(("total", "used", "free"), shutil.disk_usage(ROOT))), "hardware_execution": "NOT_RUN"})
    if pre.returncode != 0:
        raise RuntimeError("预检未完成，未启动构建")
    snapshot = EVIDENCE / "run_build.py"
    with snapshot.open("xb") as stream:
        stream.write(Path(__file__).read_bytes())
    started = time.monotonic()
    record = {"command": argv, "cwd": str(ROOT), "task_environment": task_env, "attempts": 1,
              "started_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(), "hardware_execution": "NOT_RUN",
              "peak_process_tree_memory": "NOT_MEASURED", "stop_condition": "构建异常或30分钟无日志进度", "driver_sha256": digest(snapshot),
              "native_exit_code": None, "effective_exit_code": 1}
    log = EVIDENCE / "build_console.log"
    with log.open("xb") as stream:
        child = subprocess.Popen(argv, cwd=ROOT, env=dict(os.environ, **task_env), stdout=stream, stderr=subprocess.STDOUT)
        record["own_cli_pid"] = child.pid
        print(json.dumps({"command": argv, "pid": child.pid, "log": str(log)}, ensure_ascii=False), flush=True)
        progress_at = time.monotonic()
        previous_size = 0
        while child.poll() is None:
            size = log.stat().st_size
            if size != previous_size:
                progress_at = time.monotonic()
                previous_size = size
            if time.monotonic() - progress_at > 1800:
                stop = subprocess.run(["taskkill.exe", "/PID", str(child.pid), "/T", "/F"], capture_output=True, check=False)
                record["timeout_stop_exit_code"] = stop.returncode
                child.wait()
                break
            time.sleep(2)
        record["native_exit_code"] = child.returncode
    details_path = EVIDENCE / "build/build_details.json"
    if details_path.is_file():
        details = json.loads(details_path.read_text(encoding="utf-8"))
        calls = {item["name"]: item for item in details.get("api_calls", []) if item["name"] in ("platform.build", "app.build", "initializer.build")}
        record.update(build_details_sha256=digest(details_path), status=details.get("status"), build_api_results=calls,
                      own_server_pid=details.get("own_server_pid"), own_server_cleanup=details.get("own_server_cleanup"))
        if child.returncode == 0 and details.get("status") == "PASS_OFFLINE_BUILD_AND_LAYOUT" and len(calls) == 3 and all(item.get("return_type") == "int" and item.get("return_repr") == "0" for item in calls.values()) and b"S2B_PS_SMOKE_BUILD_OK hardware_execution=NOT_RUN" in log.read_bytes():
            record["effective_exit_code"] = 0
    record.update(elapsed_seconds=time.monotonic() - started, finished_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(), console_sha256=digest(log))
    write_new("build_receipt.json", record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record["effective_exit_code"]

if __name__ == "__main__":
    sys.exit(main())
