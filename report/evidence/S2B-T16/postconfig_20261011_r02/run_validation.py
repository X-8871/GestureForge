"""冻结快照后的必要mock回归；采样子进程峰值，原生状态原样保存。"""
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
RUN = ROOT / "report/evidence/S2B-T16/postconfig_20261011_r02"
assert RUN.is_dir()
target = RUN / Path(__file__).name
assert not target.exists(); shutil.copyfile(Path(__file__), target)
binding = json.loads((RUN / "source_binding.json").read_text(encoding="utf-8"))
command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_board_jtag",
           "verification.test_s2b_cold_observation", "verification.test_s2b_visibility_probe", "-v"]


class Counters(ctypes.Structure):
    """仅查询本次Python子进程；不查询或改动任何设备会话。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
        (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
        "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]


query = ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo
query.argtypes = (wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD)
query.restype = wintypes.BOOL
started = time.monotonic()
peak = samples = query_errors = 0
stop_reason = None
with (RUN / "unittest_stdout.log").open("xb") as output, (RUN / "unittest_stderr.log").open("xb") as errors:
    child = subprocess.Popen(command, cwd=ROOT, stdout=output, stderr=errors,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    while child.poll() is None:
        counters = Counters(); counters.cb = ctypes.sizeof(counters)
        if query(wintypes.HANDLE(int(child._handle)), ctypes.byref(counters), counters.cb):
            samples += 1; peak = max(peak, counters.PeakWorkingSetSize)
        else: query_errors += 1
        if peak >= 400 * 1024 * 1024 or time.monotonic() - started > 1200:
            stop_reason = "本次Python子进程RSS>=400MiB或总耗时>1200秒"
            child.kill(); break
        time.sleep(0.1)
    native = child.wait()
drift = [name for name, sha in binding["source_sha256"].items() if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
value = {"command": command, "cwd": str(ROOT), "native_exit_code": native,
         "elapsed_seconds": time.monotonic() - started, "finished_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "source_drift": drift, "peak_working_set_bytes": peak, "samples": samples, "sampling_interval_seconds": 0.1,
         "query_errors": query_errors, "stop_reason": stop_reason, "total_deadline_seconds": 1200,
         "RSS_budget_bytes": 400 * 1024 * 1024, "resource_scope": "仅本次unittest主Python子进程；短暂纯导入/--help后代未单独采样。",
         "real_sdk_calls": 0, "ross_calls": 0, "hardware_execution": "NOT_RUN", "tool_call_count": "exec调用量留在会话；mock API总数未逐测试累计。"}
with (RUN / "native_run_result.json").open("x", encoding="utf-8", newline="\n") as output:
    json.dump(value, output, ensure_ascii=False, indent=2); output.write("\n")
print(json.dumps(value, ensure_ascii=False))
sys.exit(native if native else 2 if drift else 0)
