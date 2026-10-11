"""原生Python监测器：保存真实退出码、stdout/stderr、耗时和单进程内存峰值。"""

import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import sys
import time

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]


class MemoryCounters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def execute(label, command):
    started = time.monotonic()
    with (RUN / (label + "_stdout.log")).open("xb") as out, (RUN / (label + "_stderr.log")).open("xb") as err:
        child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
        peak = 0
        stopped = None
        while child.poll() is None:
            counters = MemoryCounters()
            counters.cb = ctypes.sizeof(counters)
            if ctypes.windll.psapi.GetProcessMemoryInfo(wintypes.HANDLE(child._handle), ctypes.byref(counters), counters.cb):
                peak = max(peak, counters.PeakWorkingSetSize, counters.WorkingSetSize)
            if peak > 400 * 1024 * 1024 or time.monotonic() - started > 1200:
                stopped = "MEMORY_OR_TIME_BUDGET"
                child.terminate()
                break
            time.sleep(0.25)
        code = child.wait(timeout=20)
    meta = {"command": command, "native_exit_code": code, "elapsed_seconds": time.monotonic() - started,
            "peak_single_process_working_set_bytes": peak, "peak_process_tree_bytes": None,
            "budget_bytes": 400 * 1024 * 1024, "timeout_seconds": 1200, "stop_reason": stopped,
            "scope": "MOCK_ONLY_NO_HARDWARE"}
    with (RUN / (label + "_native.json")).open("x", encoding="utf-8") as stream:
        json.dump(meta, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(meta, ensure_ascii=False), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(execute("independent_r01", [sys.executable, "-B", str(RUN / "review_cases.py")]))
