"""R2独立离线复核；验证产物仅写隔离目录，全部原件保持只读。"""
from dataclasses import replace
from pathlib import Path
import hashlib
import io
import json
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zlib

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT))
from verification import s2b_board_jtag as j
from verification import test_s2b_board_jtag as t

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

sources = ["verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py", "verification/s2b_board_transport.py"]
before = {p: sha(ROOT / p) for p in sources}
r1 = ROOT / "tmp/2B/S2B-T16/independent_review_20261011_r01/review_receipt.json"
r1_before = sha(r1)
(RUN / "fixtures").mkdir()
tempfile.tempdir = str(RUN / "fixtures")
started = time.monotonic()
with (RUN / "unittest.log").open("w", encoding="utf-8") as log:
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(t))
print("MOCK", result.testsRun, result.wasSuccessful(), flush=True)

def raw_response(request, epoch, status, error, code, data=b"", mutation=None):
    # 独立按40字节头和40字节诊断载荷编码，不使用Developer响应工厂。
    payload = struct.pack("<Q8I", epoch, status, error, 0, 0, 0, 0, 1, code) + data
    head = j.transport.Header(request.op | 0x8000, request.sequence, request.frame, request.width,
                              request.height, request.repeat, len(payload), zlib.crc32(payload))
    raw = head.pack() + payload
    return mutation(raw) if mutation else raw

def mutate_head(**kwargs):
    def mutate(raw):
        h = j.transport.Header.unpack(raw[:40])
        return replace(h, **kwargs).pack() + raw[40:]
    return mutate

def cache_wire(c, mutation=None, transition=None):
    def exchange(request, payload):
        phase, cpu, dap = struct.unpack("<III", payload)
        data = c.exchange(phase, cpu, dap)
        if transition: transition(c, phase)
        return raw_response(request, 0, 0x400, 0, 0, data, mutation)
    return j.JtagWireSession(t.FakeSerial(exchange), io.BytesIO(), io.BytesIO(), response_timeout=0.02)

def abort_wire(c, mutation=None, ready=True):
    c.session.memory.update({j.CSR_BASE + 0x050: 7, j.CSR_BASE + 0x00C: 0x102, j.CSR_BASE + 0x058: 19})
    def exchange(request, payload):
        first = raw_response(request, 7, 0x102, 0, 10) if ready else b""
        second = raw_response(request, 7, 0xC05, 8, 0, mutation=mutation)
        return first + second
    wire = j.JtagWireSession(t.FakeSerial(exchange), io.BytesIO(), io.BytesIO(), response_timeout=0.02)
    wire.epoch = 6
    payload = struct.pack("<III", 2, 1000, 1000)
    request, header = j.transport.make_request(j.transport.OP_DIAG, 1, 19, payload)
    wire.send(request, header, payload, {"kind": "independent_mock_bytes"})
    c.session.bus_error = None
    def transition():
        c.session.memory[j.CSR_BASE + 0x00C], c.session.memory[j.CSR_BASE + 0x010] = 0xC05, 8
    c.session.abort_transition = transition
    return wire, request

probes = []
def probe(name, action, success_expected=False):
    c = t.JtagTests(); c.setUp()
    try:
        c.ready(); c.controller.deploy()
        try:
            value = action(c)
            accepted, error = True, None
        except Exception as exc:
            accepted, error, value = False, repr(exc), None
        probes.append({"name": name, "accepted": accepted, "expected_accepted": success_expected,
                       "matched": accepted == success_expected, "error": error, "return": value,
                       "operations": c.session.operations, "record": c.controller.record})
        print(name, accepted, "MATCH" if accepted == success_expected else "MISMATCH", flush=True)
    finally:
        c.tearDown()

def bad_cache(c, status, epoch):
    c.session.memory[j.CSR_BASE + 0x00C], c.session.memory[j.CSR_BASE + 0x050] = status, epoch
    return c.controller.cache_probe(cache_wire(c), 1, 2)

probe("R1_RUN_epoch7", lambda c: bad_cache(c, 0x102, 7))
probe("R1_IDLE_epoch7", lambda c: bad_cache(c, 0x400, 7))
probe("R1_bool_final_removed", lambda c: c.controller.dap_abort(True, {"epoch": 7}))
probe("R1_wrong_UART_epoch999", lambda c: c.controller.dap_abort(*abort_wire(c, lambda r: r[:40] + struct.pack("<Q", 999) + r[48:])))
def unstable(c):
    wire, request = abort_wire(c)
    c.session.flip_final_error = True
    return c.controller.dap_abort(wire, request)
probe("R1_error8_to9", unstable)
probe("missing_WAIT_frame", lambda c: c.controller.dap_abort(*abort_wire(c, ready=False)))
for label, mutation in (("sequence", mutate_head(sequence=999)), ("frame", mutate_head(frame=999)),
                         ("op", mutate_head(op=0x8004)), ("crc", lambda r: r[:-1] + bytes([r[-1] ^ 1]))):
    probe("abort_bad_" + label, lambda c, m=mutation: c.controller.dap_abort(*abort_wire(c, m)))
    probe("cache_bad_" + label, lambda c, m=mutation: c.controller.cache_probe(cache_wire(c, m), 1, 2))
def phase_move(c, phase):
    if phase == 0:
        c.session.memory[j.CSR_BASE + 0x050], c.session.memory[j.CSR_BASE + 0x00C] = 1, 0x102
probe("cache_epoch_transition_between_phases", lambda c: c.controller.cache_probe(cache_wire(c, transition=phase_move), 1, 2))
def used_wire(c):
    wire = cache_wire(c)
    payload = struct.pack("<III", 0, 1, 2)
    req, head = j.transport.make_request(j.transport.OP_CACHE_PROBE, 1, 0, payload)
    wire.send(req, head, payload, {})
    return c.controller.cache_probe(wire, 1, 2)
probe("cache_previous_wire_send_rejected", used_wire)
probe("cache_cold_stable_success", lambda c: c.controller.cache_probe(cache_wire(c), 1, 2), True)
def success_abort(c):
    wire, req = abort_wire(c)
    event = c.controller.dap_abort(wire, req)
    if wire.abort_pending["phase"] != "ACK_REQUIRED": raise AssertionError("终态未保留")
    if sum(op[0] == "mwr" for op in c.session.operations) != 1: raise AssertionError("存在隐式ACK")
    if c.session.memory[j.CSR_BASE + 0x00C] != 0xC05: raise AssertionError("终态被清除")
    return event
probe("abort_strict_final_success_no_implicit_ACK", success_abort, True)

checks = []
manifest = "report/evidence/S2B-T16/jtag_offline_20261011_r03/delivery_manifest.json"
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", manifest]
    checked = subprocess.run(command, cwd=ROOT, capture_output=True)
    (RUN / (mode + "_stdout.log")).write_bytes(checked.stdout)
    (RUN / (mode + "_stderr.log")).write_bytes(checked.stderr)
    checks.append({"command": command, "native_exit_code": checked.returncode})
after = {p: sha(ROOT / p) for p in sources}
receipt = {"status": "PASS" if result.wasSuccessful() and all(p["matched"] for p in probes) and before == after else "CHANGES_REQUIRED",
           "baseline": "18c0c34f9da885b5f35869c282dc0c2ed50d720e", "source_before": before, "source_after": after,
           "source_unchanged": before == after, "R1_receipt_before": r1_before, "R1_receipt_after": sha(r1),
           "mock_tests": result.testsRun, "mock_success": result.wasSuccessful(), "boundary_count": len(probes),
           "boundary_matches": sum(p["matched"] for p in probes), "checks": checks, "manifest_sha256": sha(ROOT / manifest),
           "elapsed_seconds": time.monotonic() - started, "hardware": "NOT_RUN", "peak_memory": "NOT_MEASURED",
           "closed_findings": ["R1-F1", "R1-F2", "R1-F3"], "limitations": ["仅G2离线工具审查，非G3/G4/G5。", "system-stop不证明POR或旧AXI生命周期结束，保持NOT_PROVEN。", "不得覆盖正在诊断的时序/硬件部署阻碍。"]}
(RUN / "probe_results.json").write_text(json.dumps(probes, ensure_ascii=False, indent=2, default=repr), encoding="utf-8")
receipt["evidence_files"] = [{"path": p.name, "sha256": sha(p)} for p in sorted(RUN.iterdir()) if p.is_file() and p.name != "review_receipt.json"]
(RUN / "review_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False), flush=True)
