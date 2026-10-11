"""纯导入读取模块规格及当前进程已加载DLL来源，不操作硬件。"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json
import ctypes
import hashlib
import xsdb

folder = Path(__file__).parent
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
kernel.GetModuleHandleW.restype = ctypes.c_void_p
kernel.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong]
rows = {}
for name in ("xv_pycommontasks", "xv_hsmpytasks"):
    module = sys.modules[name]
    spec = getattr(module, "__spec__", None)
    handle = kernel.GetModuleHandleW(name+".pyd")
    path = ctypes.create_unicode_buffer(32768)
    assert handle and kernel.GetModuleFileNameW(handle, path, len(path))
    raw = Path(path.value).read_bytes()
    rows[name] = {"module_object_id": id(module), "module_name": module.__name__, "file": module.__file__,
                  "spec_name": getattr(spec, "name", None), "spec_origin": getattr(spec, "origin", None),
                  "loader": repr(getattr(spec, "loader", None)), "loader_path": getattr(getattr(spec, "loader", None), "path", None),
                  "loaded_binary_path": path.value, "loaded_binary_sha256": hashlib.sha256(raw).hexdigest()}
assert xsdb.debug_session is None
assert sys.modules["xsdb.xsdb_debug_session"].debug_session_int_obj is None
record = {"hardware_execution": "NOT_RUN", "session_created": False, "connection_attempted": False, "serial_opened": False,
          "same_module_object": sys.modules["xv_pycommontasks"] is sys.modules["xv_hsmpytasks"], "origins": rows}
with (folder / "native_origins.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps(record))
