"""真实Vitis解释器纯导入门禁；不得创建Session、连接或打开串口。"""
import sys
sys.dont_write_bytecode=True
if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8",errors="strict")
from pathlib import Path
import importlib.util
import json
import hashlib
import time
import traceback
import ctypes

ROOT=Path.cwd();RUN=ROOT/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01"
config_path=RUN/"sdk_gate_only_config.json"
result={"hardware_execution":"NOT_RUN","scope":"SDK_GATE_ONLY","session_created":False,"connection_attempted":False,"serial_opened":False,"full_preflight":"NOT_RUN_NO_FORMAL_COMPAT_RECEIPT","python":sys.version}
started=time.monotonic();code=1
def globals_state():
    """观察SDK全局，不调用工厂。"""
    return {name:{"module_loaded":name in sys.modules,"session_is_none":getattr(sys.modules.get(name),key,None) is None} for name,key in (("xsdb","debug_session"),("xsdb.xsdb_debug_session","debug_session_int_obj"))}
result["globals_before"]=globals_state()
try:
    spec=importlib.util.spec_from_file_location("native_fix_entry",ROOT/"vitis/run_s2b_visibility_probe.py")
    entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
    raw=config_path.read_bytes();config=entry.strict_json(raw.decode("utf-8"))
    assert config["kind"]=="SDK_GATE_ONLY" and config["hardware_execution"]=="NOT_RUN"
    result["config_binding"]={"path":str(config_path),"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
    result["sdk_files_gate_count"]=len(entry.verify_sdk_files(config))
    result["serial_files_gate_count"]=len(entry.verify_serial_files(config))
    sdk,serial=entry._runtime(config)
    result["runtime_sources"]=entry.verify_runtime_sources(config)
    result["globals_after"]=globals_state()
    assert all(row["session_is_none"] for row in result["globals_before"].values())
    assert all(row["module_loaded"] and row["session_is_none"] for row in result["globals_after"].values())
    result["serial_version"]=serial.__version__
    result["status"]="PASS_ACTUAL_VITIS_SOURCE_GATE_ONLY";code=0
except BaseException as error:
    result.update(status="FAIL_ACTUAL_VITIS_SOURCE_GATE_ONLY",error=repr(error),traceback=traceback.format_exc(),globals_after=globals_state())
finally:
    class Counters(ctypes.Structure):
        """当前进程峰值，不代替进程树峰值。"""
        _fields_=[("cb",ctypes.c_ulong),("PageFaultCount",ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
    counter=Counters();counter.cb=ctypes.sizeof(counter)
    kernel=ctypes.WinDLL("kernel32",use_last_error=True);kernel.GetCurrentProcess.restype=ctypes.c_void_p
    psapi=ctypes.WinDLL("psapi",use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    result["single_process_peak_working_set_bytes"]=counter.PeakWorkingSetSize if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counter),counter.cb) else None
    result["peak_process_tree_memory_bytes"]=None
    result.update(inner_exit_code=code,elapsed_seconds=time.monotonic()-started)
    target=RUN/"actual_runtime_source_gate.json";assert target.parent.is_dir() and not target.exists()
    with target.open("x",encoding="utf-8",newline="\n") as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write("\n")
print(json.dumps({key:value for key,value in result.items() if key!="runtime_sources"},ensure_ascii=False))
raise SystemExit(code)
