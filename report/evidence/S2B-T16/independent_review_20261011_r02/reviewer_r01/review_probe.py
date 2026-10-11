"""只读独立审查：全部离线产物写入当前隔离目录。"""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import time
import unittest

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT))
from verification import test_s2b_board_jtag as t
from verification import s2b_board_jtag as j

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

paths = [ROOT / "verification/s2b_board_jtag.py", ROOT / "verification/test_s2b_board_jtag.py"]
before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
(RUN / "fixtures").mkdir()
tempfile.tempdir = str(RUN / "fixtures")
started = time.monotonic()
with (RUN / "unittest.log").open("w", encoding="utf-8") as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t))
probes = []

def probe(name, setup, action):
    case = t.JtagTests()
    case.setUp()
    try:
        case.ready()
        setup(case)
        try:
            value = action(case)
            accepted, error = True, None
        except Exception as exc:
            value, accepted, error = None, False, repr(exc)
        probes.append({"name": name, "unsafe_or_unproved_input_accepted": accepted, "return": value, "error": error,
                       "operations": case.session.operations, "record": case.controller.record})
    finally:
        case.tearDown()

def cache_setup(case, status=0x102, epoch=7):
    case.controller.deploy()
    case.session.memory[j.CSR_BASE + 0x00C] = status
    case.session.memory[j.CSR_BASE + 0x050] = epoch

probe("cache_probe_during_RUN_epoch7", cache_setup,
      lambda c: c.controller.cache_probe(c.exchange, 1, 2))
probe("cache_probe_IDLE_nonzero_epoch7", lambda c: cache_setup(c, 0x400, 7),
      lambda c: c.controller.cache_probe(c.exchange, 1, 2))

def abort_setup(c):
    c.session.bus_error = None
    c.session.memory[j.CSR_BASE + 0x050] = 7
    c.session.memory[j.CSR_BASE + 0x00C] = 0x102

def final_value(c, value):
    c.session.memory[j.CSR_BASE + 0x00C] = 0xC05
    c.session.memory[j.CSR_BASE + 0x010] = 8
    return value

probe("abort_without_WAIT_DAP_ABORT_boolean_final", abort_setup,
      lambda c: c.controller.dap_abort(7, wait_final=lambda: final_value(c, True)))
probe("abort_wrong_UART_epoch_and_error", abort_setup,
      lambda c: c.controller.dap_abort(7, wait_final=lambda: final_value(c, {"epoch": 999, "error_code": 0, "phys_status": 0xE04})))

def unstable_final(c):
    final_value(c, None)
    apu = c.session.objects[10]
    original = apu.mrd
    def mrd(*args, **kwargs):
        value = original(*args, **kwargs)
        if kwargs["address"] == j.CSR_BASE + 0x010:
            c.session.memory[j.CSR_BASE + 0x010] = 9
        return value
    apu.mrd = mrd
    return {"epoch": 7, "error_code": 8, "phys_status": 0xC05}

probe("abort_final_CSR_changes_after_first_error_read", abort_setup,
      lambda c: c.controller.dap_abort(7, wait_final=lambda: unstable_final(c)))
after = {str(p.relative_to(ROOT)): sha(p) for p in paths}
receipt = {"status": "CHANGES_REQUIRED", "baseline": "3700b9a61de41375138ad8c9633788fd73b3960f",
           "source_before": before, "source_after": after, "unchanged": before == after,
           "mock_tests": result.testsRun, "mock_success": result.wasSuccessful(), "mock_failures": len(result.failures),
           "mock_errors": len(result.errors), "boundary_count": len(probes),
           "boundary_unproved_acceptances": sum(p["unsafe_or_unproved_input_accepted"] for p in probes),
           "elapsed_seconds": time.monotonic() - started,
           "hardware": "NOT_RUN", "peak_memory": "NOT_MEASURED"}
(RUN / "probe_results.json").write_text(json.dumps(probes, ensure_ascii=False, indent=2, default=repr), encoding="utf-8")
(RUN / "review_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False))
for p in probes:
    print(p["name"], "ACCEPTED" if p["unsafe_or_unproved_input_accepted"] else "REJECTED", p["error"])
