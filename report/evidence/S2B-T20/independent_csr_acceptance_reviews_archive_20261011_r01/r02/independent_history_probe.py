"""独立按真实WireSession构造成功与异常历史，闭环确认R1两反例拒绝。"""
from pathlib import Path
import gc
import hashlib
import json
import struct
import sys
import time
from unittest.mock import patch

OUT = Path(__file__).absolute().parent
ROOT = OUT.parents[3]
sys.path.insert(0, str(ROOT))
from verification import test_s2b_csr_board_acceptance as fixture
csr = fixture.csr
desired = b'GFINT8W1' + b'A' * (5903100 - 8)
replacement = b'GFINT8W1' + b'B' * (5903100 - 8)
input_raw = b'I' * 519168
run_payload = struct.pack('<II', 1000, 2000) + input_raw
plan = {'weights': {'kind': 'MOCK_DESIRED'}, 'rows': [{'input': {'kind': 'MOCK_INPUT'}}]}
outcomes = []
started = time.perf_counter()

for scenario in ('normal', 'replaced_load_r1', 'outstanding_load_r1', 'restored_load',
                 'failed_latch', 'partial_receipt', 'abort_ready', 'replayed_receipt',
                 'reordered_receipts', 'asynchronous_tx', 'wrong_final_frame'):
    folder = OUT / ('raw_' + scenario); folder.mkdir()
    rx = (folder / 'rx.bin').open('xb'); tx = (folder / 'tx.bin').open('xb')
    serial = fixture.MemorySerial()
    wire = csr.jtag.JtagWireSession(serial, rx, tx, response_timeout=0.01)
    def send(op, payload, *, consume=True, frame=0, partial=False):
        """真实send与receipt，仅UART读写为内存替身。"""
        request, header = csr.transport.make_request(op, wire.last_sequence + 1, frame, payload,
            width=640 if op == 2 else 0, height=480 if op == 2 else 0)
        wire.send(request, header, payload, {'scope': 'MOCK_ONLY'})
        if consume:
            raw = fixture.raw_response(request, wire.epoch + (op == 2), status=0xE04 if op == 2 else 0x400, run=op == 2)
            serial.raw.extend(raw[:53] if partial else raw)
            wire.receipt(request)
        return request
    send(1, desired)
    if scenario in ('replaced_load_r1', 'restored_load'):
        send(1, replacement)
        if scenario == 'restored_load': send(1, desired)
    if scenario == 'asynchronous_tx':
        load_request = send(1, desired, consume=False)
        run_request = send(2, run_payload, consume=False)
        for request in (load_request, run_request):
            serial.raw.extend(fixture.raw_response(request, request.op == 2, status=0xE04 if request.op == 2 else 0x400, run=request.op == 2))
            wire.receipt(request)
    else:
        send(2, run_payload, frame=1 if scenario == 'wrong_final_frame' else 0)
    if scenario == 'outstanding_load_r1': send(1, replacement, consume=False)
    if scenario == 'failed_latch': wire.failed = True
    if scenario == 'partial_receipt':
        try: send(1, desired, partial=True)
        except csr.transport.TransportError: pass
        # 即使有人错误清除锁存，也不能把实际截断消费伪称完整成功。
        wire.failed = False
    if scenario == 'abort_ready': wire.receipt_attempts[-1]['abort_ready'] = True
    if scenario == 'replayed_receipt': wire.receipt_attempts.append(dict(wire.receipt_attempts[-1]))
    if scenario == 'reordered_receipts': wire.receipt_attempts.reverse()
    expected = 'ACCEPTED' if scenario in ('normal', 'restored_load') else 'REJECTED'
    try:
        with patch.object(csr.model, 'read_bound', side_effect=lambda item: (folder, desired if item['kind'] == 'MOCK_DESIRED' else input_raw)):
            csr.prior_model_success(wire, plan)
        observed, error = 'ACCEPTED', None
    except Exception as exc:
        observed, error = 'REJECTED', repr(exc)
    rx.close(); tx.close()
    record = {'scenario': scenario, 'expected': expected, 'observed': observed, 'error': error,
              'wire_epoch': wire.epoch, 'last_sequence': wire.last_sequence,
              'receipts': len(wire.receipt_attempts), 'events': len(wire.events),
              'raw_rx_sha256': hashlib.sha256((folder / 'rx.bin').read_bytes()).hexdigest(),
              'raw_tx_sha256': hashlib.sha256((folder / 'tx.bin').read_bytes()).hexdigest()}
    (folder / 'raw_receipt_summary.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    outcomes.append(record)
    assert observed == expected, record
    del wire, serial
    gc.collect()

(OUT / 'independent_history_result.json').write_text(json.dumps({
    'scope': 'REAL_WIRESESSION_PARSER_MOCK_ONLY', 'hardware_execution': 'NOT_RUN',
    'native_exit_code': 0, 'elapsed_seconds': time.perf_counter() - started,
    'desired_sha256': hashlib.sha256(desired).hexdigest(), 'replacement_sha256': hashlib.sha256(replacement).hexdigest(),
    'outcomes': outcomes}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(outcomes, ensure_ascii=False))
