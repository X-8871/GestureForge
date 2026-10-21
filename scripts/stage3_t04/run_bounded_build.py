#!/usr/bin/env python3
"""监督单次已授权构建，只能终止本脚本启动的进程树。"""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time


class MemoryStatus(ctypes.Structure):
    """Windows 提供的物理内存与提交空间状态。"""

    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                ("physical_total", ctypes.c_ulonglong), ("physical_free", ctypes.c_ulonglong),
                ("commit_total", ctypes.c_ulonglong), ("commit_free", ctypes.c_ulonglong),
                ("virtual_total", ctypes.c_ulonglong), ("virtual_free", ctypes.c_ulonglong),
                ("extended_virtual_free", ctypes.c_ulonglong)]


def memory() -> dict:
    """只查询系统内存，不调整其他进程。"""
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx 失败")
    return {"physical_free_mb": status.physical_free // 2**20, "commit_free_mb": status.commit_free // 2**20}


def main() -> int:
    """新日志目录拒绝覆盖；超时/持续资源压力仅停止自己的构建。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True, type=Path)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-seconds", type=int, default=3600)
    parser.add_argument("--idle-seconds", type=int, default=900)
    options = parser.parse_args()
    root = options.worktree.resolve(strict=True)
    output = options.output.absolute()
    if output.exists() or not output.parent.is_dir() or not output.resolve().is_relative_to(root):
        parser.error("输出必须是工作树内且父目录已存在的新目录")
    import re
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}", options.run_name):
        parser.error("运行名称只能包含英文字母、数字、下划线与连字符")
    if options.max_seconds <= 0 or options.idle_seconds <= 0:
        parser.error("时限必须为正数")
    run = root / "tmp/s3r06" / options.run_name
    if run.exists():
        parser.error("运行目录已存在，不能覆盖")
    before = memory()
    if before["physical_free_mb"] < 2048 or before["commit_free_mb"] < 8192:
        print(json.dumps({"status": "RESOURCE_BLOCKED", **before}))
        return 75
    command = ["C:/Program Files/Git/bin/bash.exe", "--noprofile", "--norc",
               str(root / "scripts/stage3_t04/run_t04_camera_display_bluefix_build.sh"), options.run_name]
    output.mkdir()
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    environment["S3_MIN_AVAILABLE_MB"] = "2048"
    environment["S3_BUILD_JOBS"] = "1"
    start = time.monotonic()
    progress = start
    pressure_since = None
    fingerprint = None
    observations = []
    stop_reason = None
    with (output / "launcher.txt").open("wb") as log:
        process = subprocess.Popen(command, cwd=root, env=environment, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        print(json.dumps({"pid": process.pid, "command": command, "output": str(output), "memory_before": before}), flush=True)
        while process.poll() is None:
            now = time.monotonic()
            sample = {"elapsed_seconds": round(now - start, 1), **memory()}
            observations.append(sample)
            paths = [output / "launcher.txt", run / "vivado.log"]
            paths += list((run / "project/ov5640_single.runs").glob("*/runme.log"))
            current = tuple((str(path), path.stat().st_size, path.stat().st_mtime_ns) for path in paths if path.is_file())
            if current != fingerprint:
                fingerprint = current
                progress = now
            pressure = sample["physical_free_mb"] < 384 or sample["commit_free_mb"] < 2048
            pressure_since = (pressure_since or now) if pressure else None
            if now - start > options.max_seconds:
                stop_reason = "TOTAL_TIMEOUT"
            elif now - progress > options.idle_seconds:
                stop_reason = "NO_PROGRESS_TIMEOUT"
            elif pressure_since is not None and now - pressure_since > 60:
                stop_reason = "SUSTAINED_MEMORY_PRESSURE"
            if stop_reason:
                # PID 来自尚未结束的本次 Popen，不查找或停止其他任务。
                kill = subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                (output / "termination.txt").write_bytes(kill.stdout + kill.stderr)
                if kill.returncode:
                    raise RuntimeError(f"停止本次进程树失败，PID={process.pid}，退出码={kill.returncode}")
                process.wait(timeout=30)
                break
            time.sleep(5)
    actual_rc = process.returncode
    result = {"command": command, "pid": process.pid, "exit_code": actual_rc,
              "stop_reason": stop_reason, "elapsed_seconds": round(time.monotonic() - start, 2),
              "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
              "observations": observations,
              "max_seconds": options.max_seconds, "idle_seconds": options.idle_seconds,
              "limits": "物理空余低于384MiB或提交空余低于2GiB持续60s则停止本次任务"}
    (output / "supervisor.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "observations"}, ensure_ascii=False), flush=True)
    return actual_rc if not stop_reason else 124


if __name__ == "__main__":
    raise SystemExit(main())
