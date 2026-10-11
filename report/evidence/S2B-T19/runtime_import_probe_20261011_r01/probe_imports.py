"""只检查真实Vitis解释器导入；不创建调试会话、不连接服务、不打开串口。"""
import sys
sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
import hashlib
import importlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import traceback

root = Path.cwd()
folder = root / "report/evidence/S2B-T19/runtime_import_probe_20261011_r01"
assert folder.is_dir()
result = {"schema_version": 1, "status": "FAILED", "hardware_execution": "NOT_RUN",
          "started_at_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
          "python_executable": sys.executable, "python_version": sys.version,
          "vitis_environment_version": os.environ.get("XILINX_VITIS_VERSION"),
          "session_created": False, "connection_attempted": False, "serial_opened": False,
          "peak_process_tree_memory_bytes": None, "loaded_modules": []}
try:
    offline = json.loads((root / "report/evidence/S2B-T19/offline_probe_entry_20261011_r01/offline_result.json").read_text(encoding="utf-8"))
    serial_items = offline["pyserial_files"]
    for item in serial_items:
        source = Path(item["path"])
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == item["sha256"]
    package = next(Path(item["path"]) for item in serial_items if Path(item["path"]).name == "__init__.py" and Path(item["path"]).parent.name == "serial")
    sys.path.insert(0, str(package.parent.parent))
    xsdb = importlib.import_module("xsdb")
    serial = importlib.import_module("serial")
    assert Path(xsdb.__file__) == Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\__init__.py")
    assert Path(serial.__file__) == package and serial.__version__ == "3.5"
    assert xsdb.debug_session is None
    assert xsdb.xsdb_debug_session.debug_session_int_obj is None
    for name, module in sorted(sys.modules.items()):
        if name == "xsdb" or name.startswith("xsdb.") or name == "tcf" or name.startswith("tcf.") or name == "serial" or name.startswith("serial.") or name.startswith("hsi"):
            path = getattr(module, "__file__", None)
            row = {"name": name, "file": path, "sha256": None}
            if path is not None:
                source = Path(path)
                assert source.is_file()
                row["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            result["loaded_modules"].append(row)
    result.update(status="PASS_RUNTIME_IMPORT_ONLY", pyserial_version=serial.__version__)
except BaseException as error:
    result.update(error=repr(error), traceback=traceback.format_exc())
    raise
finally:
    result["finished_at_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    with (folder / "runtime_result.json").open("x", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
print(json.dumps({"status": result["status"], "modules": len(result["loaded_modules"]), "hardware_execution": "NOT_RUN"}, ensure_ascii=False))
