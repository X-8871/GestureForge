"""执行真实unittest并记录方法、子例、原生退出；不载入硬件模块。"""
from pathlib import Path
import ctypes
import json
import os
import sys
import time
import unittest

ROOT=Path(__file__).absolute().parents[4]
sys.path.insert(0,str(ROOT))

class Result(unittest.TextTestResult):
    """子例逐项记录；不能把方法数称为全部场景数。"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.subcases=[]
    def addSubTest(self,test,subtest,err):
        self.subcases.append({"method":test.id(),"case":str(subtest),"status":"PASS" if err is None else "FAIL"})
        super().addSubTest(test,subtest,err)

class Counters(ctypes.Structure):
    """Windows当前单进程内存计数，不能代替全进程树峰值。"""
    _fields_=[("cb",ctypes.c_ulong),("PageFaultCount",ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]

started=time.monotonic()
suite=unittest.defaultTestLoader.loadTestsFromName("verification.test_s2b_visibility_probe")
result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
code=0 if result.wasSuccessful() else 1
memory=None
if os.name=="nt":
    native=ctypes.WinDLL("kernel32",use_last_error=True)
    native.GetCurrentProcess.restype=ctypes.c_void_p
    psapi=ctypes.WinDLL("psapi",use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    counter=Counters();counter.cb=ctypes.sizeof(counter)
    if psapi.GetProcessMemoryInfo(native.GetCurrentProcess(),ctypes.byref(counter),counter.cb):memory=counter.PeakWorkingSetSize
record={"status":"PASS_OFFLINE_MOCK_ONLY" if code==0 else "FAIL_OFFLINE_TESTS","native_exit_code":code,"methods":result.testsRun,"subcases":result.subcases,"failures":len(result.failures),"errors":len(result.errors),"elapsed_seconds":time.monotonic()-started,"single_process_peak_working_set_bytes":memory,"peak_process_tree_memory_bytes":None,"hardware_execution":"NOT_RUN","xsdb_loaded":"xsdb" in sys.modules,"serial_loaded":"serial" in sys.modules}
assert not record["xsdb_loaded"] and not record["serial_loaded"]
output=Path(sys.argv[1]);assert output.parent.is_dir() and not output.exists()
with output.open("x",encoding="utf-8",newline="\n") as out:json.dump(record,out,ensure_ascii=False,indent=2);out.write("\n")
raise SystemExit(code)
