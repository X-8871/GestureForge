"""修正审查harness的TemporaryDirectory位置参数隔离，原失败原件保留。"""
from pathlib import Path
import sys
import tempfile
import unittest
import time
import json
import ctypes
from unittest.mock import patch
folder = Path(__file__).parent
root = folder.parents[3]
sys.path.insert(0, str(root))
original = tempfile.mkdtemp
def isolated(suffix=None, prefix=None, dir=None):
    """接收全部标准位置参数并验证新目录仍在授权隔离目录。"""
    result = original(suffix=suffix, prefix=prefix, dir=folder)
    path = Path(result)
    assert path.parent == folder and path.is_dir() and not path.lstat().st_file_attributes & 1024
    return result
class Result(unittest.TextTestResult):
    """分别记录方法与子场景。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.cases = []
    def addSubTest(self, test, subtest, err):
        self.cases.append({"method": test.id(), "case": str(subtest), "status": "PASS" if err is None else "FAIL"})
        super().addSubTest(test, subtest, err)
started = time.monotonic()
with patch.object(tempfile, "mkdtemp", side_effect=isolated):
    suite = unittest.defaultTestLoader.loadTestsFromName("verification.test_s2b_csr_board_acceptance")
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
code = 0 if result.wasSuccessful() else 1
class Counters(ctypes.Structure):
    """当前进程工作集峰值。"""
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [(name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaNonPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
counter = Counters(); counter.cb = ctypes.sizeof(counter)
kernel = ctypes.WinDLL("kernel32", use_last_error=True); kernel.GetCurrentProcess.restype = ctypes.c_void_p
psapi = ctypes.WinDLL("psapi", use_last_error=True); psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
memory = counter.PeakWorkingSetSize if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counter), counter.cb) else None
record = {"native_exit_code": code, "methods": result.testsRun, "subcases": result.cases,
          "failures": len(result.failures), "errors": len(result.errors), "elapsed_seconds": time.monotonic()-started,
          "hardware_execution": "NOT_RUN", "single_process_peak_working_set_bytes": memory, "peak_process_tree_memory_bytes": None,
          "xsdb_loaded": "xsdb" in sys.modules, "serial_loaded": "serial" in sys.modules}
with (folder/"offline_suite_result_r02.json").open("x", encoding="utf-8") as out:
    json.dump(record, out, ensure_ascii=False, indent=2)
raise SystemExit(code)
