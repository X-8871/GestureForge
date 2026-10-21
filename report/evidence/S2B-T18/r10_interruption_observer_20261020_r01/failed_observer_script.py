"""服务重建后只读观察板卡，使用显式APU原始读避免隐式缓存同步。"""
import faulthandler
import importlib.util
import json
import struct
import sys
from pathlib import Path
ROOT = Path(r"D:\FPGA_Competition\w2b")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("s2b_interruption_observer_runtime", ROOT / "vitis/run_s2b_model_acceptance.py")
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)
config = r.strict_json((ROOT / "report/evidence/S2B-T18/formal_online_20261018_r01/model_config_csr_20261019_r10.json").read_bytes())
config["hw_server"] = {"process_id": 33672, "executable_path": r"D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe",
                       "creation_time_filetime_utc": "134368991556843770"}
output = ROOT / "report/evidence/S2B-T18/r10_interruption_observer_20261020_r01"
assert output.parent.is_dir()
output.mkdir()
r.save_json_new(output / "observer_config.json", config)
journal = r.Journal(output / "observer_calls.jsonl")
runtime = r.ProductionRuntime()
apis = r.load_apis("csr")

class RawObserver(apis.jtag.JtagController):
    """仅读原始物理字；不使用本对象执行下载、复位或命令写入。"""
    def words(self, address, count):
        value = self.call("apu.mrd.raw_observer", self.targets["apu"].mrd,
                          "--value", "--bypass_cache_synq", address=address, size=count, word_size=4)
        rows = [value] if count == 1 else value
        assert type(rows) is list and len(rows) == count and all(type(v) is int and 0 <= v <= 0xFFFFFFFF for v in rows)
        self.record.setdefault("readbacks", []).append({"address": address, "words": rows,
                                                       "raw_le_hex": struct.pack("<" + "I" * count, *rows).hex()})
        return rows

record = {"scope": "READ_ONLY_DIAGNOSTIC", "hardware_commands": "NO_START_ACK_RESET_DOW_CON_STOP",
          "read_mode": "APU --bypass_cache_synq", "status": "IN_PROGRESS", "cleanup_errors": []}
xsdb = session = channel = controller = None
owner = {}
helper, _ = r.load_pinned_csr_map_helper()
hc = {"sdk_files": config["runtime"]["sdk_files"]}
hr = {"verified_inputs": {"compat_artifacts": {"implemented_xsa": config["bindings"]["xsa"]}}, "cleanup_errors": []}
stack = (output / "observer_stack.log").open("xb")
faulthandler.dump_traceback_later(20, repeat=False, file=stack)
try:
    record["identity"] = runtime.identity(config)
    xsdb, serial = runtime.modules(config)
    session, channel = runtime.session(xsdb, serial, config, journal, lambda value: None)
    controller = RawObserver(session, config["bindings"], output)
    controller.select_and_gate()
    record["cpu0_state"] = controller.state("cpu0")
    record["cpu1_state"] = controller.state("cpu1")
    record["cpu0_pc"] = controller.pc()
    record["cpu1_pc"] = controller.pc("cpu1")
    helper.register_csr_debug_map(hc, hr, journal, session, controller, owner)
    record["csr"] = controller.stable_csr("after_r10_interruption")
    apis.csr_flow.csr.checked_snapshot(record["csr"])
    record["status"] = "OBSERVATIONS_SAVED_NOT_ACCEPTANCE"
except BaseException as error:
    record.update(status="FAILED_READ_ONLY_OBSERVER", error=repr(error))
finally:
    if controller is not None:
        controller.close()
    if session is not None and owner.get("attempted"):
        helper.clear_csr_debug_map(hc, hr, journal, session, owner)
    if session is not None:
        session.disconnect(**({"chan": channel} if channel is not None else {}))
    if xsdb is not None:
        xsdb.dispose()
    journal.close()
    faulthandler.cancel_dump_traceback_later()
    stack.close()
    r.save_json_new(output / "observation.json", record)
print(json.dumps({key: record.get(key) for key in ("status", "error", "cpu0_state", "cpu1_state", "cpu0_pc", "csr")}, ensure_ascii=False))
raise SystemExit(0 if record["status"] == "OBSERVATIONS_SAVED_NOT_ACCEPTANCE" else 2)
