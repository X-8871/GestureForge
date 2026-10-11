"""独立审查真实解释器纯导入与门禁；不创建会话或操作硬件。"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import importlib.util
import json
import hashlib
import traceback
import time

root = Path.cwd()
folder = Path(__file__).parent
started = time.monotonic()
record = {"hardware_execution": "NOT_RUN", "session_created": False,
          "connection_attempted": False, "serial_opened": False,
          "python": sys.version, "executable": sys.executable}
code = 1
try:
    spec = importlib.util.spec_from_file_location("independent_probe", root / "vitis/run_s2b_visibility_probe.py")
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    closure = p.strict_json((root / "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/sdk_source_closure.json").read_text(encoding="utf-8"))
    baseline = p.strict_json((root / "report/evidence/S2B-T19/offline_probe_entry_20261011_r01/offline_result.json").read_text(encoding="utf-8"))
    package = next(x for x in baseline["pyserial_files"] if Path(x["path"]).name == "__init__.py" and Path(x["path"]).parent.name == "serial")
    config = {"sdk_files": closure["modules"], "bindings": {"pyserial_init": package, "sdk_init": closure["modules"]["xsdb"]}}
    sdk, serial = p._runtime(config)
    observed = p.verify_runtime_sources(config)
    assert sdk.debug_session is None
    assert sys.modules["xsdb.xsdb_debug_session"].debug_session_int_obj is None
    record.update(status="PASS_ACTUAL_RUNTIME_SOURCE_GATE_IMPORT_ONLY", modules=observed, serial_file=serial.__file__, serial_version=serial.__version__)
    code = 0
except BaseException as error:
    record.update(status="FAIL_ACTUAL_RUNTIME_SOURCE_GATE", error=repr(error), traceback=traceback.format_exc())
finally:
    record.update(elapsed_seconds=time.monotonic()-started, native_exit_code=code)
    with (folder / "actual_runtime_gate.json").open("x", encoding="utf-8") as out:
        json.dump(record, out, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(code)
