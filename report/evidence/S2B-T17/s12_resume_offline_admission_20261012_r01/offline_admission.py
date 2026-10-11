"""只读检查本机离线重型进程与可用资源，不访问设备。"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psutil


def main():
    """保留真实快照；遇到候选重型身份未知时拒绝准入。"""
    output = Path(sys.argv[1])
    if not output.parent.is_dir() or output.exists():
        raise RuntimeError("精确父目录缺失或输出已存在")
    names = {"vivado.exe", "vivado", "vivado_lab.exe", "xelab.exe", "xsim.exe",
             "verilator_bin.exe", "verilator_bin", "g++.exe", "cc1plus.exe"}
    heavy = []
    unknown = []
    for process in psutil.process_iter(["pid", "name"], ad_value=None):
        if (process.info.get("name") or "").lower() not in names:
            continue
        record = {"pid": process.pid, "name": process.info["name"]}
        try:
            record.update(create_time=process.create_time(), exe=process.exe(),
                          cmdline=process.cmdline(), cwd=process.cwd(),
                          rss_bytes=process.memory_info().rss)
            heavy.append(record)
        except psutil.NoSuchProcess:
            record["status"] = "CONFIRMED_EXIT_DURING_READ"
            unknown.append(record)
        except (psutil.Error, OSError) as error:
            record.update(status="IDENTITY_UNKNOWN", error=repr(error))
            unknown.append(record)
    ram = psutil.virtual_memory().available
    disk = psutil.disk_usage("C:\\").free
    allowed = not heavy and not unknown and ram >= 4831838208 and disk >= 8589934592
    result = {"status": "OFFLINE_ADMISSION_READY" if allowed else "BLOCKED",
              "at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "available_ram_bytes": ram, "c_disk_free_bytes": disk,
              "candidate_heavy_processes": heavy, "unknown_candidates": unknown,
              "python": sys.version, "psutil": psutil.__version__,
              "limitations": ["仅重型执行名快照，不保证未枚举的不同名称任务不存在",
                              "此时只读快照，不证明以后资源充足或任何硬件连接"]}
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
