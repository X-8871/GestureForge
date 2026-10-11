#!/usr/bin/env python3
"""仅启动同目录数学probe，保存真实原生码、日志、耗时和峰值内存。"""
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[3]


class Counters(ctypes.Structure):
    """Windows进程内存计数器原布局。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def main():
    """限制20秒和256MiB，只读取自身子进程内存；不启动重型工具。"""
    assert ROOT == Path.cwd().resolve()
    argv = [sys.executable, "-X", "utf8", "-B", str(WORK / "math_probe.py")]
    started = time.monotonic()
    peak = 0
    stop = None
    psapi = ctypes.WinDLL("psapi")
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    with (WORK / "stdout_r02.log").open("xb") as out, (WORK / "stderr_r02.log").open("xb") as err:
        child = subprocess.Popen(argv, cwd=ROOT, stdout=out, stderr=err)
        while child.poll() is None:
            memory = Counters()
            memory.cb = ctypes.sizeof(memory)
            if psapi.GetProcessMemoryInfo(wintypes.HANDLE(int(child._handle)), ctypes.byref(memory), memory.cb):
                peak = max(peak, memory.PeakWorkingSetSize)
            if time.monotonic()-started > 20 or peak > 256*1024*1024:
                stop = "TIMEOUT_20S_OR_RSS_256MIB"
                child.kill()
                break
            time.sleep(0.02)
        code = child.wait()
    record = {"command": subprocess.list2cmdline(argv), "argv": argv, "cwd": str(ROOT),
              "native_exit_code": code, "elapsed_seconds": time.monotonic()-started,
              "peak_child_working_set_bytes": peak, "stop_reason": stop,
              "python_version": sys.version, "run_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for name in ("math_probe.py", "stdout_r02.log", "stderr_r02.log", "result_r02.json"):
        path = WORK / name
        if path.is_file():
            record[name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
    with (WORK / "native_capture_r02.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(record, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
