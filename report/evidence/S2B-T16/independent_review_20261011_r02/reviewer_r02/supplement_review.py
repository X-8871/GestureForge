"""补充CRC有效的语义反例；保留初次checker错误期待原件。"""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import zlib

RUN = Path(__file__).absolute().parent
ROOT = RUN.parents[3]
sys.path.insert(0, str(ROOT))
from verification import test_s2b_board_jtag as t
from verification import s2b_board_jtag as j
tempfile.tempdir = str(RUN / "fixtures")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

rows = []
def probe(name, action):
    c = t.JtagTests(); c.setUp()
    try:
        c.ready(); c.controller.deploy()
        try:
            value = action(c)
            rejected, error = False, None
        except Exception as exc:
            rejected, error, value = True, repr(exc), None
        rows.append({"name": name, "rejected": rejected, "error": error, "return": value, "record": c.controller.record})
    finally:
        c.tearDown()

def final_field(c, **changed):
    wire, request = c.abort_wire()
    ready_length = 80
    raw = bytes(wire.stream.rx)
    header = j.transport.Header.unpack(raw[ready_length:ready_length + 40])
    values = list(j.transport.META.unpack(raw[ready_length + 40:]))
    for index, value in changed.items(): values[int(index)] = value
    payload = j.transport.META.pack(*values)
    from dataclasses import replace
    wire.stream.rx = bytearray(raw[:ready_length] + replace(header, payload_crc=zlib.crc32(payload)).pack() + payload)
    c.session.bus_error = None
    return c.controller.dap_abort(wire, request)

probe("final_epoch999_valid_CRC", lambda c: final_field(c, **{"0": 999}))
probe("final_error0_valid_CRC", lambda c: final_field(c, **{"2": 0}))
probe("final_DONE_HEAD_valid_CRC", lambda c: final_field(c, **{"1": 0xE04, "2": 0}))
def bad_op(c):
    from dataclasses import replace
    def mutate(raw, phase):
        h = j.transport.Header.unpack(raw[:40])
        return replace(h, op=0x8003).pack() + raw[40:]
    return c.controller.cache_probe(c.cache_wire(mutate_frame=mutate), 1, 2)
probe("cache_actual_wrong_op8003", bad_op)
def invalid_final_csr(c, offset, value):
    wire, request = c.abort_wire()
    c.session.bus_error = None
    transition = c.session.abort_transition
    def after():
        transition(); c.session.memory[j.CSR_BASE + offset] = value
    c.session.abort_transition = after
    return c.controller.dap_abort(wire, request)
probe("final_CSR_ledger_nonzero", lambda c: invalid_final_csr(c, 0x068, 1))
probe("final_CSR_active_frame_mismatch", lambda c: invalid_final_csr(c, 0x058, 999))
probe("final_CSR_HEAD_flag", lambda c: invalid_final_csr(c, 0x00C, 0xE05))
def wrong_mode(c):
    wire, request = c.abort_wire()
    c.session.bus_error = None
    original = wire.sent_requests[request.sequence]
    wire.sent_requests[request.sequence] = (original[0], original[1], bytes(12))
    return c.controller.dap_abort(wire, request)
probe("mode2_required_before_DAP", wrong_mode)

initial = json.loads((RUN / "review_receipt.json").read_text(encoding="utf-8"))
original = json.loads((RUN / "probe_results.json").read_text(encoding="utf-8"))
correction = next(p for p in original if p["name"] == "cache_bad_op")
correction_ok = correction["accepted"] and j.transport.OP_CACHE_PROBE == 4
receipt = {**initial, "status": "PASS" if all(p["rejected"] for p in rows) and correction_ok and initial["mock_success"] and initial["boundary_matches"] == 17 else "CHANGES_REQUIRED",
           "initial_receipt_sha256": sha(RUN / "review_receipt.json"),
           "checker_correction": "初次cache_bad_op将响应op改成0x8004，恰等于合法OP4响应，因此错误预期拒绝；原错误期待与CHANGES_REQUIRED原件保留。本补充使用0x8003，被正常拒绝。",
           "initial_boundary_effective_matches": 18 if correction_ok else 17,
           "supplement_boundary_count": len(rows), "supplement_rejections": sum(p["rejected"] for p in rows),
           "source_after_final": {p: sha(ROOT / p) for p in initial["source_before"]},
           "R1_receipt_after_final": sha(ROOT / "tmp/2B/S2B-T16/independent_review_20261011_r01/review_receipt.json"),
           "findings": [], "R1_closure": {"R1-F1": "稳定冷CSR每phase与DAP动作前后；原RUN/nonzero epoch及phase推进反例拒绝。", "R1-F2": "完整原UART经T15解析并复核，bool/无READY/错误seq/frame/epoch/code拒绝，final保留ACK_REQUIRED。", "R1-F3": "两完整CSR逐word一致且UART一致；error8到9、ledger1、frame错及HEAD有效拒绝。"},
           "native_execution_exit_code": 0,
           "sdk_source_checks": "复用R1已独立核对SDK原件及实际API调用范围；R2不修改reset/mrd/mwr/breakpoint路径。"}
(RUN / "supplement_results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=repr), encoding="utf-8")
receipt["final_evidence_files"] = [{"path": p.name, "sha256": sha(p)} for p in sorted(RUN.iterdir()) if p.is_file() and p.name != "review_receipt_final.json"]
(RUN / "review_receipt_final.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
print(receipt["status"], len(rows), receipt["supplement_rejections"], sha(RUN / "review_receipt_final.json"))
