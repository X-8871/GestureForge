"""独立真实运输格式反例：成功权重被后续LOAD替换，不操作硬件。"""
from pathlib import Path
import sys
import struct
import hashlib
import json
from unittest.mock import patch

folder = Path(__file__).parent
sys.path.insert(0, str(folder.parents[3]))
from verification import test_s2b_csr_board_acceptance as fixture
csr = fixture.csr
rawdir = folder/"prior_replaced_model_mock"
rawdir.mkdir()
rx, tx = (rawdir/"rx.bin").open("xb"), (rawdir/"tx.bin").open("xb")
serial = fixture.MemorySerial()
wire = csr.jtag.JtagWireSession(serial, rx, tx, response_timeout=0.1)
weights = b"GFINT8W1" + b"A"*(5903100-8)
replacement = b"GFINT8W1" + b"B"*(5903100-8)
input_raw = b"I"*519168
plan = {"weights": {"kind": "MOCK_DESIRED"}, "rows": [{"input": {"kind": "MOCK_INPUT"}}]}
def exchange(op, seq, payload, epoch, run=False):
    """用JtagWireSession.send/receipt消费完整内存UART原字节。"""
    request, header = csr.transport.make_request(op, seq, 0, payload, width=640 if run else 0, height=480 if run else 0)
    wire.send(request, header, payload, {"scope": "MOCK_ONLY"})
    serial.raw.extend(fixture.raw_response(request, epoch, status=0xE04 if run else 0x400, run=run))
    wire.receipt(request)
exchange(1, 1, weights, 0)
exchange(1, 2, replacement, 0)
exchange(2, 3, struct.pack("<II", 1000, 2000)+input_raw, 1, run=True)
with patch.object(csr.model, "read_bound", side_effect=lambda item: (rawdir, weights if item["kind"] == "MOCK_DESIRED" else input_raw)):
    csr.prior_model_success(wire, plan)
record = {"native_exit_code": 0, "scope": "REAL_TRANSPORT_PARSER_MOCK_UART_ONLY", "hardware_execution": "NOT_RUN",
          "observed": "ACCEPTED_SUPERSEDED_WEIGHTS_LOAD", "desired_weights_sha256": hashlib.sha256(weights).hexdigest(),
          "last_accepted_weights_sha256": hashlib.sha256(replacement).hexdigest(), "run_sequence": 3,
          "wire_epoch": wire.epoch, "receipt_attempts": [{k:v for k,v in row.items() if k != "request_payload_hex"} for row in wire.receipt_attempts]}
rx.close(); tx.close()
with (folder/"prior_state_counterexample.json").open("x", encoding="utf-8") as out:
    json.dump(record, out, ensure_ascii=False, indent=2)
print(json.dumps({k:v for k,v in record.items() if k != "receipt_attempts"}))
