"""独立真实Vitis来源门禁及内存篡改反例；不构造会话或操作硬件。"""
import sys
sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
from pathlib import Path
import importlib.util
import json
import time
import traceback
import copy
import types
import ctypes
from unittest.mock import patch

root = Path.cwd()
folder = Path(__file__).parent
started = time.monotonic()
record = {"hardware_execution": "NOT_RUN", "scope": "PRODUCTION_SOURCE_GATE_IMPORT_ONLY", "session_created": False,
          "connection_attempted": False, "serial_opened": False, "full_preflight": "NOT_RUN_NO_FORMAL_COMPAT_RECEIPT",
          "python": sys.version, "rows": []}
code = 1
try:
    spec = importlib.util.spec_from_file_location("review_r03_entry", root/"vitis/run_s2b_visibility_probe.py")
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    config_path = root/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/sdk_gate_only_config.json"
    config = p.strict_json(config_path.read_text(encoding="utf-8"))
    assert config["kind"] == "SDK_GATE_ONLY" and config["hardware_execution"] == "NOT_RUN"
    record["sdk_count"] = len(p.verify_sdk_files(config))
    record["serial_count"] = len(p.verify_serial_files(config))
    sdk, serial = p._runtime(config)
    record["runtime_sources"] = p.verify_runtime_sources(config)
    record["serial_version"] = serial.__version__
    record["native_actual"] = p.verify_native_alias(config["sdk_files"])
    def rejection(label, function):
        """反例必须被生产门禁拒绝，正常返回即审查失败。"""
        try:
            function()
        except (p.VisibilityProbeError, p.helpers()[0].JtagError) as error:
            record["rows"].append({"label": label, "status": "REJECTED", "error": repr(error)})
        else:
            raise AssertionError("门禁接受了反例："+label)
    native = sys.modules["xv_pycommontasks"]
    with patch.object(native, "__name__", "review_wrong_native"):
        rejection("native_module_name_drift", lambda: p.verify_native_alias(config["sdk_files"]))
    with patch.dict(sys.modules, {"xv_pycommontasks": types.ModuleType("vivado")}):
        rejection("native_shared_identity_drift", lambda: p.verify_native_alias(config["sdk_files"]))
    with patch.object(native.__spec__, "origin", config["sdk_files"]["xv_pycommontasks"]["path"]):
        rejection("native_spec_origin_drift", lambda: p.verify_native_alias(config["sdk_files"]))
    with patch.object(native.__spec__.loader, "path", config["sdk_files"]["xv_pycommontasks"]["path"]):
        rejection("native_loader_path_drift", lambda: p.verify_native_alias(config["sdk_files"]))
    changed = copy.deepcopy(config["sdk_files"])
    changed["xv_pycommontasks"]["sha256"] = "0"*64
    rejection("native_supplier_hash_drift", lambda: p.verify_native_alias(changed))
    changed = copy.deepcopy(config)
    changed["sdk_files"]["xv_pycommontasks"] = changed["sdk_files"]["xv_hsmpytasks"]
    rejection("duplicate_native_physical_binding", lambda: p.verify_sdk_files(changed))
    images = p._loaded_native_images(("xv_pycommontasks", "xv_hsmpytasks"))
    images["xv_pycommontasks"]["path"] = images["xv_hsmpytasks"]["path"]
    with patch.object(p, "_loaded_native_images", return_value=images):
        rejection("loaded_image_physical_path_drift", lambda: p.verify_native_alias(config["sdk_files"]))
    for name in ("Session", "Target"):
        cls = getattr(sys.modules["xsdb."+name.lower()], name)
        with patch.object(cls, "__module__", "review_wrong_class_origin"):
            rejection(name+"_class_origin_r02_counterexample", lambda: p.verify_runtime_sources(config))
    with patch.object(sys.modules["xsdb.xsdb_debug_session"], "Session", object):
        rejection("dispatch_session_alias_drift", lambda: p.verify_runtime_sources(config))
    with patch.object(sys.modules["xsdb.session"], "Target", object):
        rejection("session_target_alias_drift", lambda: p.verify_runtime_sources(config))
    with patch.object(sys.modules["xsdb.session"], "__file__", config["sdk_files"]["xsdb.target"]["path"]):
        rejection("ordinary_module_origin_still_strict", lambda: p.verify_runtime_sources(config))
    with patch.object(sys.modules["xsdb.session"].Session, "connect", lambda: None):
        rejection("official_method_code_drift", lambda: p.verify_runtime_sources(config))
    assert sdk.debug_session is None and sys.modules["xsdb.xsdb_debug_session"].debug_session_int_obj is None
    record["post_adversarial_gate"] = p.verify_runtime_sources(config)
    record["status"] = "PASS_ACTUAL_SOURCE_GATE_AND_13_ADVERSARIAL_REJECTIONS"
    code = 0
except BaseException as error:
    record.update(status="FAIL", error=repr(error), traceback=traceback.format_exc())
finally:
    class Counters(ctypes.Structure):
        """单进程峰值；进程树峰值另保留未测。"""
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [(name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counter = Counters()
    counter.cb = ctypes.sizeof(counter)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    record["single_process_peak_working_set_bytes"] = counter.PeakWorkingSetSize if psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counter), counter.cb) else None
    record["peak_process_tree_memory_bytes"] = None
    record.update(inner_exit_code=code, elapsed_seconds=time.monotonic()-started)
    with (folder/"actual_runtime_gate.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps({k: v for k, v in record.items() if k not in ("runtime_sources", "post_adversarial_gate")}, ensure_ascii=False))
raise SystemExit(code)
