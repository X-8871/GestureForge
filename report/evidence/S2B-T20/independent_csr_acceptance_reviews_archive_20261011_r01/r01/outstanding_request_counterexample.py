"""前置RUN后实际发送新LOAD未消费响应，独立核验gate是否错误接受。"""
from pathlib import Path
import sys
import struct
import json
from unittest.mock import patch
folder = Path(__file__).parent
sys.path.insert(0, str(folder.parents[3]))
from verification import test_s2b_csr_board_acceptance as fixture
csr = fixture.csr
rawdir = folder/"outstanding_request_mock"; rawdir.mkdir()
rx, tx = (rawdir/"rx.bin").open("xb"), (rawdir/"tx.bin").open("xb")
serial = fixture.MemorySerial(); wire = csr.jtag.JtagWireSession(serial, rx, tx, response_timeout=0.1)
weights = b"GFINT8W1" + b"A"*(5903100-8); replacement = b"GFINT8W1" + b"B"*(5903100-8); input_raw = b"I"*519168
plan = {"weights": {"kind": "MOCK_DESIRED"}, "rows": [{"input": {"kind": "MOCK_INPUT"}}]}
for op, seq, payload, epoch in ((1, 1, weights, 0), (2, 2, struct.pack("<II", 1000, 2000)+input_raw, 1), (1, 3, replacement, 1)):
    request, header = csr.transport.make_request(op, seq, 0, payload, width=640 if op == 2 else 0, height=480 if op == 2 else 0)
    wire.send(request, header, payload, {"scope": "MOCK_ONLY"})
    if seq != 3:
        serial.raw.extend(fixture.raw_response(request, epoch, status=0xE04 if op == 2 else 0x400, run=op == 2)); wire.receipt(request)
with patch.object(csr.model, "read_bound", side_effect=lambda item: (rawdir, weights if item["kind"] == "MOCK_DESIRED" else input_raw)):
    csr.prior_model_success(wire, plan)
record = {"native_exit_code": 0, "scope": "REAL_TRANSPORT_PARSER_MOCK_UART_ONLY", "hardware_execution": "NOT_RUN",
          "observed": "ACCEPTED_WITH_OUTSTANDING_LATER_WEIGHTS_REQUEST", "last_receipt_sequence": 2, "last_sent_sequence": wire.last_sequence,
          "wire_epoch": wire.epoch, "receipt_count": len(wire.receipt_attempts)}
rx.close(); tx.close()
with (folder/"outstanding_request_counterexample.json").open("x", encoding="utf-8") as out:
    json.dump(record, out, ensure_ascii=False, indent=2)
print(json.dumps(record))
