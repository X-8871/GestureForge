"""只运行T20轻量回归，记录子进程原生退出码及Windows内存峰值。"""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).absolute().parents[4]
output = root / "report/evidence/S2B-T20/csr_acceptance_20261011_r01"
assert root.is_dir() and output.is_dir()
assert not (output / "unittest_r04.log").exists() and not (output / "validation_result.json").exists()
class Counters(ctypes.Structure):
    """Windows原生PROCESS_MEMORY_COUNTERS_EX字段。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t)]
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel.OpenProcess.restype = wintypes.HANDLE
kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
psapi.GetProcessMemoryInfo.argtypes = (wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD)
command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_csr_board_acceptance", "-v"]
started = time.monotonic()
observed = []
with (output / "unittest_r04.log").open("x", encoding="utf-8", newline="\n") as log:
    process = subprocess.Popen(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
    handle = kernel.OpenProcess(0x0410, False, process.pid)
    assert handle, "子进程内存句柄打开失败"
    try:
        while True:
            counters = Counters(); counters.cb = ctypes.sizeof(counters)
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                observed.append((int(counters.PeakWorkingSetSize), int(counters.PeakPagefileUsage)))
            if process.poll() is not None:
                break
            if time.monotonic() - started > 60:
                process.kill(); process.wait()
                raise RuntimeError("T20轻量回归超过60秒停止条件")
            time.sleep(0.01)
    finally:
        kernel.CloseHandle(handle)
record = {"schema_version": 1, "status": "PASS_MOCK_ONLY" if process.returncode == 0 else "FAIL",
          "command": command, "cwd": str(root), "native_exit_code": process.returncode,
          "elapsed_seconds": time.monotonic() - started, "tests": 22, "runs_including_preserved_attempts": 4,
          "hardware_execution": "NOT_RUN", "python_version": sys.version,
          "peak_working_set_bytes": max(item[0] for item in observed),
          "peak_pagefile_usage_bytes": max(item[1] for item in observed), "memory_samples": len(observed),
          "memory_scope": "Windows测试子进程原生高水位；无SDK/串口/工具子进程，父进程及全机峰值未测。",
          "source_baseline": "5a676b700af4c27297977379417b1694dd64840e",
          "limitations": ["22项mock不代表任何实板通过。", "busy START及短deadline同旧PS热恢复仍BLOCKED。",
                          "r02序列化失败原日志和当时两源码原件保留；r01/r03原结果也保留。"]}
record["memory_budget_ok"] = max(record["peak_working_set_bytes"], record["peak_pagefile_usage_bytes"]) < 300 * 1024 * 1024
with (output / "validation_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2); stream.write("\n")
print(json.dumps(record, ensure_ascii=False))
sys.exit(process.returncode if record["memory_budget_ok"] else 2)
