"""独立模拟Windows映像查询异常，核对底层helper的拒绝行为。"""
from pathlib import Path
import sys
import ctypes
import types
import json
from unittest.mock import patch

folder = Path(__file__).parent
sys.path.insert(0, str(folder.parents[3]))
from verification.test_s2b_visibility_probe import p
names = ("xv_pycommontasks", "xv_hsmpytasks")
class Function:
    """可附加ctypes签名的fake函数，不调用真实DLL。"""
    def __init__(self, function):
        self.function = function
    def __call__(self, *args):
        return self.function(*args)
rows = []
for kind in ("positive", "missing", "duplicate_handle", "empty_path", "truncated_path"):
    def handle(name):
        """稳定的纯mock句柄。"""
        if kind == "missing":
            return 0
        if kind == "duplicate_handle":
            return 1
        return names.index(name.removesuffix(".pyd"))+1
    def filename(value, buffer, count):
        """纯mock填充，不查询操作系统。"""
        if kind == "empty_path":
            return 0
        if kind == "truncated_path":
            return count
        buffer.value = "D:\\review_only\\"+names[value-1]+".pyd"
        return len(buffer.value)
    fake = types.SimpleNamespace(GetModuleHandleW=Function(handle), GetModuleFileNameW=Function(filename))
    with patch.object(ctypes, "WinDLL", return_value=fake):
        try:
            result = p._loaded_native_images(names)
        except p.VisibilityProbeError as error:
            assert kind != "positive"
            rows.append({"case": kind, "status": "REJECTED", "error": repr(error)})
        else:
            assert kind == "positive", kind
            rows.append({"case": kind, "status": "ACCEPTED", "images": result})
assert "xsdb" not in sys.modules and "serial" not in sys.modules
record = {"native_exit_code": 0, "scope": "WINDOWS_API_MOCK_ONLY", "hardware_execution": "NOT_RUN", "rows": rows}
with (folder/"native_query_counterexamples.json").open("x", encoding="utf-8") as output:
    json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
