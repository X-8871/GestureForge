"""运行前只读核对内存、磁盘和指定重型工具进程。"""
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys

import psutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
memory = psutil.virtual_memory()
names = {"vivado.exe", "vitis.exe", "xvlog.exe", "xelab.exe", "xsim.exe", "verilator_bin.exe", "cc1plus.exe"}
heavy = []
errors = []
for process in psutil.process_iter():
    try:
        name = process.name()
        if not isinstance(name, str) or not name:
            errors.append({"pid": process.pid, "error": "不可读取进程名"})
        elif name.lower() in names:
            heavy.append({"pid": process.pid, "name": name})
    except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
        errors.append({"pid": process.pid, "error": type(error).__name__})
disk = shutil.disk_usage(ROOT)
record = {"timestamp": datetime.now().astimezone().isoformat(), "available_ram_bytes": memory.available,
          "free_disk_bytes": disk.free, "heavy_processes": heavy, "enumeration_errors": errors,
          "scope": "指定进程名的只读快照，不证明其他会话生命周期或归属。"}
record["ready"] = memory.available >= int(4.5 * 1024**3) and disk.free >= 2 * 1024**3 and not heavy and not errors
with (RUN / "host_prelaunch.json").open("x", encoding="utf-8") as stream:
    stream.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(record, ensure_ascii=False))
sys.exit(0 if record["ready"] else 1)
