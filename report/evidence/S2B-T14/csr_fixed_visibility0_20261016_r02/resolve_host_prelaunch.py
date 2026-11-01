"""以Windows原生完整进程名快照补充psutil空名称观测，不放宽启动条件。"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import psutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
OUTPUT = RUN / "host_native_prelaunch.json"
RAW = RUN / "host_native_inventory.raw.json"
STDERR = RUN / "host_native_inventory.stderr.raw"
if OUTPUT.exists() or RAW.exists() or STDERR.exists():
    raise RuntimeError("原生启动快照已存在，禁止覆盖")
previous = json.loads((RUN / "host_prelaunch.json").read_text(encoding="utf-8"))
powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
if not powershell.is_file():
    raise RuntimeError("精确原生查询程序路径不存在")
script = r"""$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[System.Text.Encoding]::UTF8
$items=@(Get-Process -ErrorAction Stop | ForEach-Object {
    [PSCustomObject]@{pid=[int]$_.Id;name=[string]$_.ProcessName}
})
ConvertTo-Json -InputObject $items -Compress -Depth 3
"""
names = {"vivado", "vitis", "xvlog", "xelab", "xsim", "verilator_bin", "cc1plus"}
record = {"ready": False, "timestamp": None, "native_return_code": None, "inventory_count": 0,
          "native_timed_out": False,
          "heavy_processes": [], "errors": [], "previous_unknown_resolution": [],
          "scope": "Windows原生完整PID/进程名快照，不读取命令行，不证明其他会话生命周期或归属。",
          "native_program": str(powershell),
          "native_program_sha256": hashlib.sha256(powershell.read_bytes()).hexdigest()}


def preserve_native_output(stdout, stderr):
    """保留正常或超时返回的原始输出，无输出时明确保存空文件。"""
    with RAW.open("xb") as stream:
        stream.write(stdout or b"")
    with STDERR.open("xb") as stream:
        stream.write(stderr or b"")


try:
    try:
        completed = subprocess.run([str(powershell), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, check=False)
    except subprocess.TimeoutExpired as error:
        record["native_timed_out"] = True
        preserve_native_output(error.stdout, error.stderr)
        raise
    record["native_return_code"] = completed.returncode
    preserve_native_output(completed.stdout, completed.stderr)
    if completed.returncode != 0 or completed.stderr.strip():
        raise RuntimeError("原生枚举返回非零或stderr非空")
    inventory = json.loads(completed.stdout.decode("utf-8-sig"))
    if not isinstance(inventory, list) or not inventory:
        raise RuntimeError("原生进程快照不是非空列表")
    seen = {}
    for entry in inventory:
        pid, name = entry["pid"], entry["name"]
        if type(pid) is not int or pid < 0 or not isinstance(name, str) or not name.strip() or pid in seen:
            raise RuntimeError("原生快照存在PID/名称缺失或重复")
        seen[pid] = name
        if name.lower().removesuffix(".exe") in names:
            record["heavy_processes"].append(entry)
    record["inventory_count"] = len(inventory)
    for error in previous["enumeration_errors"]:
        record["previous_unknown_resolution"].append({"pid": error["pid"],
            "native_name_now": seen.get(error["pid"]), "present_in_fresh_snapshot": error["pid"] in seen})
    record["available_ram_bytes"] = psutil.virtual_memory().available
    record["free_disk_bytes"] = shutil.disk_usage(ROOT).free
    record["ready"] = (record["available_ram_bytes"] >= int(4.5 * 1024**3)
                       and record["free_disk_bytes"] >= 2 * 1024**3 and not record["heavy_processes"])
except Exception as error:
    record["errors"].append(f"{type(error).__name__}: {error}")
record["timestamp"] = datetime.now().astimezone().isoformat()
with OUTPUT.open("x", encoding="utf-8") as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(record, ensure_ascii=False))
sys.exit(0 if record["ready"] else 1)
