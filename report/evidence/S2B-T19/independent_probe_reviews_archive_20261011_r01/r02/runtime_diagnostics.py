"""官方SDK纯导入后记录真实来源及分步门禁；没有会话或连接。"""
import sys
sys.dont_write_bytecode = True
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="strict")
from pathlib import Path
import importlib
import importlib.util
import json
import hashlib
import traceback
import time
from unittest.mock import patch

root = Path.cwd()
folder = Path(__file__).parent
record = {"hardware_execution": "NOT_RUN", "session_created": False, "connection_attempted": False, "serial_opened": False, "python": sys.version}
started = time.monotonic()
try:
    spec = importlib.util.spec_from_file_location("review_probe", root / "vitis/run_s2b_visibility_probe.py")
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    closure = p.strict_json((root / "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/sdk_source_closure.json").read_text(encoding="utf-8"))["modules"]
    old = p.strict_json((root / "report/evidence/S2B-T19/offline_probe_entry_20261011_r01/offline_result.json").read_text(encoding="utf-8"))
    serial = next(x for x in old["pyserial_files"] if Path(x["path"]).name == "__init__.py" and Path(x["path"]).parent.name == "serial")
    sys.path.insert(0, str(Path(serial["path"]).parent.parent))
    sdk = importlib.import_module("xsdb")
    importlib.import_module("serial")
    origins = {}
    corrected = dict(closure)
    for name in ("xv_pycommontasks", "xv_hsmpytasks"):
        actual = Path(sys.modules[name].__file__)
        origins[name] = {"actual": {"path": str(actual), "sha256": hashlib.sha256(actual.read_bytes()).hexdigest()}, "declared": closure[name]}
        corrected[name] = origins[name]["actual"]
    record["native_origins"] = origins
    for label, config in (("as_delivered", {"sdk_files": closure}), ("diagnostic_actual_pyd_bindings_only", {"sdk_files": corrected})):
        try:
            rows = p.verify_runtime_sources(config)
            record[label] = {"status": "PASS_IMPORT_ONLY", "modules": rows}
        except BaseException as error:
            record[label] = {"status": "FAIL", "error": repr(error), "traceback": traceback.format_exc()}
    assert sdk.debug_session is None
    assert sys.modules["xsdb.xsdb_debug_session"].debug_session_int_obj is None
finally:
    record["elapsed_seconds"] = time.monotonic()-started
    with (folder / "runtime_diagnostics.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
print(json.dumps(record, ensure_ascii=False))
