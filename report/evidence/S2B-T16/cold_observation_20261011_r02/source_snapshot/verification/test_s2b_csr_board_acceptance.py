"""T20轻量mock回归；不创建SDK会话或串口，不计为任何实板任务。"""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import zlib

try:
    from . import s2b_csr_board_acceptance as csr
except ImportError:
    import s2b_csr_board_acceptance as csr

TEST_PARENT = csr.ROOT / "tmp/2B/S2B-T20/csr_acceptance_20261011_r03"
HEAD = "2a20b1d9b53c9cc49fafdb49b09d78c5ab4f4674"


def snapshot():
    """独立按T11寄存器表填写固定布局，不使用执行器生成期望值。"""
    row = {key: 0 for key in (0, 4) + tuple(range(0x00C, 0x078, 4))}
    row.update({0: 0x53324250, 4: 0x100, 0x00C: 0x400,
                0x01C: 519168, 0x020: 0x100000, 0x024: 5903100, 0x028: 100, 0x02C: 200,
                0x030: 0x10000000, 0x034: 0x2000000, 0x038: 0x1000000, 0x03C: 0x1ADADB8,
                0x040: 0x1A46100, 0x044: 5070, 0x048: 0x1AD5E80, 0x04C: 20280})
    return row


class FakeController:
    """独立仅实现被测CSR语义；没有网络、SDK或设备。"""
    def __init__(self):
        self.row = snapshot()
        self.failed = False
        self.record = {"calls": [], "readbacks": []}
        self.targets = {"apu": self}
        self.bindings = {"bit": {"path": "MOCK_ONLY", "sha256": "0" * 64}}
        self.states = {"cpu0": "Stopped", "cpu1": "Stopped"}
        self.unknown_bus = False
        self.mutate_rejection = None
        self.drift = False
        self.bad_code = None
        self.model_starts = 0
        self.valid_short_behavior = "safe"
        self.pending = None
        self.pending_reads = 0
        self.on_abort = None

    def state(self, label):
        """返回测试选定状态，不产生CPU动作。"""
        return self.states[label]

    def verify_bindings(self):
        """文件绑定真实性由独立preflight回归核对。"""

    def gate(self, both=True):
        """只模拟实际核状态检查。"""
        csr.require(self.states["cpu1"] == "Stopped" and (not both or self.states["cpu0"] == "Stopped"), "核状态错误")

    def full_csr(self):
        """保留每份原逐字快照。"""
        if self.pending == "safe":
            if self.pending_reads:
                self.pending_reads -= 1
            else:
                self.row[0x00C] = 0xC05; self.row[0x010] = 5; self.row[0x068] = 0
                self.pending = None
        if self.drift:
            self.row[0x06C] += 1
        result = copy.deepcopy(self.row)
        self.record["readbacks"].append(result)
        return result

    def stable_csr(self, label):
        """两份必须相等；mock不会吞掉drift。"""
        first, second = self.full_csr(), self.full_csr()
        csr.require(first == second, "mock观测drift:" + label)
        return first

    def call(self, name, function, *args, **kwargs):
        """真实调用测试对象并保存异常，标记MOCK_ONLY。"""
        record = {"api": name, "scope": "MOCK_ONLY", "args": args, "kwargs": kwargs}
        self.record["calls"].append(record)
        try:
            result = function(*args, **kwargs)
            record.update(status="RETURNED", return_repr=repr(result))
            return result
        except Exception as error:
            record.update(status="RAISED", exception_repr=repr(error))
            raise

    def reject(self, code):
        """明确SLVERR与泛化DAP错误必须区别处理。"""
        self.row[0x064] = code
        if self.mutate_rejection is not None:
            self.row[self.mutate_rejection] ^= 1
        raise RuntimeError("DAP write failed" if self.unknown_bus else "SLVERR")

    def mwr(self, option, *, address, size, word_size, words):
        """按正式优先序模拟范围/长度/参数，绝不调用原生mwr。"""
        if (option, size, word_size) != ("--bypass_cache_synq", 1, 4):
            raise AssertionError("DAP写格式不符")
        offset, value = address - 0x43C00000, words[0]
        if offset != 8:
            self.row[offset] = value
            return
        status = self.row[0x00C] & 7
        if value == 3:
            self.reject(5)
        if value == 1:
            if status != 0:
                self.reject(2 if status in (4, 5) else 1)
            current = self.row[0x050] | self.row[0x054] << 32
            current += 1
            self.row[0x050], self.row[0x054] = current & 0xFFFFFFFF, current >> 32
            self.row[0x058] = self.row[0x014]; self.row[0x064] = 0
            if self.row[0x018] != 0 or self.row[0x020] != 0x100000:
                code = 2
            elif self.row[0x01C] != 519168 or self.row[0x024] != 5903100:
                code = 3
            elif self.row[0x028] == 0 or self.row[0x02C] == 0:
                code = 1
            else:
                code = 5; self.model_starts += 1
                if self.valid_short_behavior == "isolate_forever":
                    self.row[0x00C] = 0x106; self.row[0x010] = 5; self.row[0x068] = 1
                    return
                if self.valid_short_behavior == "late_safe":
                    self.row[0x00C] = 0x106; self.row[0x010] = 5; self.row[0x068] = 1
                    self.pending = "safe"
                    self.pending_reads = 1
                    return
            self.row[0x00C] = 0xC05; self.row[0x010] = self.bad_code if self.bad_code is not None else code
            return
        if value == 4:
            if status not in (4, 5):
                self.reject(3)
            actual = self.row[0x050] | self.row[0x054] << 32
            proposed = self.row[0x05C] | self.row[0x060] << 32
            if actual != proposed:
                self.reject(4)
            self.row[0x00C] = 0x400; self.row[0x010] = self.row[0x064] = 0
            self.row[0x06C] = self.row[0x070] = self.row[0x074] = 0
            return
        if value == 2 and self.on_abort is not None:
            self.row[0x00C] = 0xC05; self.row[0x010] = 8; self.row[0x068] = 0
            self.on_abort()
            return
        raise AssertionError("测试未定义命令")

    def guarded(self, action):
        """mock只复用T16的ABORT动作，不执行真实fail-stop。"""
        return action()

    check_wire = csr.jtag.JtagController.check_wire
    dap_abort = csr.jtag.JtagController.dap_abort


class FakeWire:
    """没有串口或原始UART，测试不发布板上结果。"""
    def __init__(self):
        self.epoch, self.failed = 0, False
        self.abort_pending = None
        self.receipt_attempts = []


class CsrTests(unittest.TestCase):
    """临时文件仅落本任务隔离目录，所有run保留至回归结束。"""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mock_", dir=TEST_PARENT)
        self.root = Path(self.temp.name)
        self.controller, self.wire = FakeController(), FakeWire()
        self.runner = csr._Runner(self.controller, self.wire, self.root, {"scope": "MOCK_ONLY_NOT_BOARD"}, scope="MOCK_ONLY_NOT_BOARD")

    def tearDown(self):
        if not self.runner.log.closed:
            self.runner.finish("MOCK_REGRESSION_ONLY")
        self.temp.cleanup()

    def binding(self, name, value):
        """UTF-8原件绑定测试。"""
        path = self.root / name
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        path.write_bytes(raw)
        return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}

    def test_complete_static_matrix(self):
        final = self.runner.static_matrix(100, 1000, 2000)
        self.assertEqual(final[0x00C], 0x400)
        self.assertEqual(csr.epoch(final), 8)
        self.assertEqual(self.controller.model_starts, 0)
        self.assertEqual(self.wire.epoch, 0)
        passed = [row["name"] for row in self.runner.record["scenarios"] if row["status"] == "PASS"]
        self.assertEqual(len(passed), 19)
        self.assertIn("range_over_length_argument", passed)
        self.assertIn("length_over_argument", passed)
        self.assertEqual(self.runner.record["scenarios"][-1]["status"], "BLOCKED")

    def test_last_reject_is_permitted_diagnostic(self):
        self.runner.reject_command("encoding", 3, 5)
        self.assertEqual(self.controller.row[0x064], 5)

    def test_unknown_bus_is_not_slverr(self):
        self.controller.unknown_bus = True
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "UNKNOWN"):
            self.runner.reject_command("encoding", 3, 5)

    def test_rejection_illegal_side_effects(self):
        for field in (0x050, 0x058, 0x010, 0x068, 0x018):
            with self.subTest(field=field):
                self.controller.row = snapshot(); self.controller.mutate_rejection = field
                with self.assertRaises(csr.CsrAcceptanceError):
                    self.runner.reject_command("negative", 3, 5)

    def test_drifting_readback_is_rejected(self):
        self.controller.drift = True
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "drift"):
            self.runner.snapshot("drift")

    def test_owner_ledger_head_gates(self):
        for field, value in ((0x00C, 0x500), (0x00C, 0x600), (0x068, 1), (0x074, 8), (0x010, 5)):
            with self.subTest(field=field, value=value):
                self.controller.row = snapshot(); self.controller.row[field] = value
                with self.assertRaises(csr.CsrAcceptanceError):
                    self.runner.parameters(1, 100, 200)
        self.assertFalse(self.controller.record["calls"])

    def test_wrong_error_priority_is_rejected(self):
        self.controller.bad_code = 3
        with self.assertRaises(csr.CsrAcceptanceError):
            self.runner.static_matrix(1, 100, 200)

    def test_short_timeout_safe_ack_but_hot_recovery_blocked(self):
        result = self.runner.short_deadline(17, 1, 100, 0.1)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["hot_golden_recovery"], "BLOCKED")
        self.assertEqual(self.wire.epoch, 0)
        self.assertEqual(self.controller.row[0x00C], 0x400)

    def test_forever_isolation_does_not_ack(self):
        self.controller.valid_short_behavior = "isolate_forever"
        result = self.runner.short_deadline(17, 1, 1, 0.003)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(result["isolated_seen"])
        self.assertEqual(self.controller.row[0x00C], 0x106)
        writes = [call["kwargs"]["words"] for call in self.controller.record["calls"]]
        self.assertNotIn([4], writes)

    def test_legal_late_drain_is_saved_and_safe_acknowledged(self):
        self.controller.valid_short_behavior = "late_safe"
        result = self.runner.short_deadline(17, 1, 1, 0.1)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["isolated_seen"])
        self.assertEqual(self.controller.row[0x00C], 0x400)

    def test_parameter_type_and_deadline_boundaries(self):
        for value in (True, -1, 0x100000000, 1.5):
            with self.subTest(value=value), self.assertRaises(csr.CsrAcceptanceError):
                self.runner.parameters(value, 100, 200)
        for seconds in (float("nan"), float("inf"), 0, 121, True):
            with self.subTest(seconds=seconds), self.assertRaises(csr.CsrAcceptanceError):
                self.runner.short_deadline(1, 1, 100, seconds)

    def test_complete_snapshot_schema(self):
        for mutate in (lambda row: row.pop(0x068), lambda row: row.update({0x078: 0}),
                       lambda row: row.update({0x034: 0x100000}), lambda row: row.update({0x054: True}),
                       lambda row: row.update({0x00C: 0x80000000}), lambda row: row.update({0x074: 32})):
            row = snapshot(); mutate(row)
            with self.assertRaises(csr.CsrAcceptanceError):
                csr.checked_snapshot(row)

    def test_bound_file_hash_path_schema(self):
        item = self.binding("bound.json", {"text": "中文"})
        self.assertEqual(csr.bound_json(item), {"text": "中文"})
        for bad in ({**item, "sha256": "0" * 64}, {**item, "path": item["path"] + "missing"},
                    {**item, "extra": 1}):
            with self.assertRaises((csr.CsrAcceptanceError, csr.jtag.JtagError)):
                csr.bound_json(bad)
        Path(item["path"]).write_bytes(b'{"x":1,"x":2}')
        item["sha256"] = hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest()
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "重复"):
            csr.bound_json(item)

    def config(self):
        """MOCK admission只用于验证门禁顺序，不能生成真实批准。"""
        scene = self.binding("scene.json", {"schema_version": 1, "kind": "s2b-csr-static-scene/1.0.0",
                                            "expected_snapshot": {str(k): v for k, v in snapshot().items()}})
        value = {"schema_version": 1, "source_commit": HEAD, "bindings": self.controller.bindings,
                 "build_details": "MOCK", "visibility_proof": "MOCK", "visibility_review": "MOCK",
                 "visibility_review_sha256": "a" * 64, "final_platform_manifest": "MOCK",
                 "final_review": "MOCK", "final_review_sha256": "b" * 64, "scene": scene}
        return value

    def admission(self, value):
        """替换类型与T18门禁仅发生在显式mock回归。"""
        item = self.binding("config_" + str(len(list(self.root.glob("config_*")))) + ".json", value)
        with mock.patch.object(csr.jtag, "JtagController", FakeController), \
             mock.patch.object(csr.jtag, "JtagWireSession", FakeWire), \
             mock.patch.object(csr.subprocess, "run", return_value=mock.Mock(returncode=0, stdout=HEAD + "\n")), \
             mock.patch.object(csr.model, "admit", return_value={"scope": "MOCK_ONLY_NOT_BOARD"}) as admitted:
            result = csr.preflight(self.controller, self.wire, item, static=True)
            self.assertEqual(admitted.call_count, 1)
            return result

    def test_preflight_borrows_frozen_gate(self):
        result = self.admission(self.config())
        self.assertEqual(result[2], snapshot())
        self.assertFalse(self.controller.record["calls"])

    def test_preflight_rejects_schema_binding_owner_epoch_drift(self):
        for mutate in (lambda value: value.update(schema_version=True),
                       lambda value: value.update(extra=1), lambda value: value.update(source_commit="0" * 40),
                       lambda value: value.update(bindings={})):
            value = self.config(); mutate(value)
            with self.assertRaises(csr.CsrAcceptanceError):
                self.admission(value)
        for field, val in ((0x050, 1), (0x00C, 0x500), (0x068, 1)):
            self.controller.row = snapshot(); self.controller.row[field] = val
            with self.assertRaises(csr.CsrAcceptanceError):
                self.admission(self.config())

    def test_cpu_must_be_stopped(self):
        self.controller.states["cpu0"] = "Running"
        with self.assertRaises(csr.CsrAcceptanceError):
            self.runner.parameters(1, 100, 200)
        self.assertFalse(self.controller.record["calls"])

    def test_failure_evidence_retains_raw_mock_calls(self):
        self.controller.unknown_bus = True
        with self.assertRaises(csr.CsrAcceptanceError):
            self.runner.reject_command("encoding", 3, 5)
        result = self.runner.finish("FAIL_MOCK_ONLY", "known mock failure")
        self.assertEqual(result["hardware_execution"], "MOCK_ONLY_NOT_BOARD")
        self.assertEqual(result["dap_calls"][0]["status"], "RAISED")
        self.assertTrue((self.root / "csr_result.json").is_file())


class MemorySerial:
    """只传输内存原字节，无设备方法。"""
    def __init__(self):
        self.raw = bytearray()
        self.pending = bytearray()
        self.on_request = None
    def write(self, raw):
        """模拟成功发送，不存储重复大型payload。"""
        if self.on_request is not None:
            self.pending.extend(raw)
            if len(self.pending) >= 40:
                head = csr.transport.Header.unpack(bytes(self.pending[:40]))
                if len(self.pending) == 40 + head.length:
                    payload = bytes(self.pending[40:]); self.pending.clear()
                    self.on_request(head, payload)
        return len(raw)
    def read(self, count):
        """有界内存短读。"""
        result = bytes(self.raw[:count]); del self.raw[:count]
        return result


def raw_response(request, epoch, *, status=0x400, run=False, error=0, code=0):
    """独立结构化响应；负logits只作格式测试，不充当业务黄金。"""
    payload = struct.pack("<Q8I", epoch, status, error, 0, 0, 0, 0, 1, code)
    if run:
        payload += bytes([129]) * 25350
    prefix = struct.pack("<4sHH7I", b"S2BU", 1, request.op | 0x8000, request.sequence,
                         request.frame, request.width, request.height, 1, len(payload), zlib.crc32(payload))
    return prefix + struct.pack("<I", zlib.crc32(prefix)) + payload


class RawWireTests(unittest.TestCase):
    """使用真实运输解析器核验成功前置的原UART，不调用SDK。"""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="wire_mock_", dir=TEST_PARENT)
        self.root = Path(self.temp.name)
        self.rx, self.tx = (self.root / "rx.bin").open("xb"), (self.root / "tx.bin").open("xb")
        self.serial = MemorySerial()
        self.wire = csr.jtag.JtagWireSession(self.serial, self.rx, self.tx, response_timeout=0.1)
        self.weights, self.input_raw = b"W" * 5903100, b"I" * 519168
        self.plan = {"weights": {"kind": "MOCK_WEIGHTS"}, "rows": [{"input": {"kind": "MOCK_INPUT"}}]}

    def tearDown(self):
        self.rx.close(); self.tx.close(); self.temp.cleanup()

    def send_receive(self, op, seq, payload, *, epoch, run=False):
        """真实WireSession发送/receipt解析内存流。"""
        request, header = csr.transport.make_request(op, seq, 0, payload, width=640 if run else 0, height=480 if run else 0)
        self.wire.send(request, header, payload, {"kind": "MOCK_ONLY"})
        self.serial.raw.extend(raw_response(request, epoch, status=0xE04 if run else 0x400, run=run))
        return self.wire.receipt(request)

    def prior(self):
        """测试文件读取替身仅代表显式小型MOCK，不替代冻结模型核验。"""
        def read_bound(item):
            return self.root, self.weights if item["kind"] == "MOCK_WEIGHTS" else self.input_raw
        with mock.patch.object(csr.model, "read_bound", side_effect=read_bound):
            return csr.prior_model_success(self.wire, self.plan)

    def seed(self):
        """创建一次LOAD与一次真实格式完整RUN响应。"""
        self.send_receive(1, 1, self.weights, epoch=0)
        self.send_receive(2, 2, struct.pack("<II", 1000, 2000) + self.input_raw, epoch=1, run=True)

    def test_prior_complete_raw_receipts(self):
        self.seed(); self.prior()

    def test_replaced_successful_weights_rejects_historical_load(self):
        self.send_receive(1, 1, self.weights, epoch=0)
        self.send_receive(1, 2, b"R" * len(self.weights), epoch=0)
        self.send_receive(2, 3, struct.pack("<II", 1000, 2000) + self.input_raw, epoch=1, run=True)
        with self.assertRaises(csr.CsrAcceptanceError):
            self.prior()

    def test_later_unconsumed_actual_load_is_rejected(self):
        self.seed()
        payload = b"R" * len(self.weights)
        request, header = csr.transport.make_request(1, 3, 0, payload)
        self.wire.send(request, header, payload, {"kind": "MOCK_ONLY"})
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "未消费"):
            self.prior()

    def test_restored_weights_then_new_seed_is_accepted(self):
        self.send_receive(1, 1, b"R" * len(self.weights), epoch=0)
        self.send_receive(1, 2, self.weights, epoch=0)
        self.send_receive(2, 3, struct.pack("<II", 1000, 2000) + b"X" * len(self.input_raw), epoch=1, run=True)
        self.send_receive(2, 4, struct.pack("<II", 1000, 2000) + self.input_raw, epoch=2, run=True)
        self.prior()

    def test_last_consumed_input_or_load_after_seed_is_rejected(self):
        self.seed()
        self.send_receive(2, 3, struct.pack("<II", 1000, 2000) + b"X" * len(self.input_raw), epoch=2, run=True)
        with self.assertRaises(csr.CsrAcceptanceError):
            self.prior()
        self.send_receive(1, 4, self.weights, epoch=2)
        with self.assertRaises(csr.CsrAcceptanceError):
            self.prior()

    def test_receipt_order_duplicate_and_interleaved_events_are_rejected(self):
        self.seed()
        attempts, events = list(self.wire.receipt_attempts), list(self.wire.events)
        for changed in (list(reversed(attempts)), attempts + attempts[:1]):
            with self.subTest(receipt_count=len(changed)):
                self.wire.receipt_attempts = changed
                with self.assertRaises((csr.CsrAcceptanceError, csr.transport.TransportError)):
                    self.prior()
        self.wire.receipt_attempts = attempts
        self.wire.events = [events[0], events[2], events[1], events[3]]
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "事件"):
            self.prior()

    def test_actual_pipelined_sends_before_receipts_are_rejected(self):
        for seq in (1, 2):
            request, header = csr.transport.make_request(1, seq, 0, self.weights)
            self.wire.send(request, header, self.weights, {"kind": "MOCK_ONLY"})
            self.serial.raw.extend(raw_response(request, 0))
        for seq in (1, 2):
            self.wire.receipt(self.wire.sent_requests[seq][0])
        self.send_receive(2, 3, struct.pack("<II", 1000, 2000) + self.input_raw, epoch=1, run=True)
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "事件"):
            self.prior()

    def test_existing_cache_probe_before_model_load_is_supported(self):
        payload = struct.pack("<III", 1, 0x13579BDF, 0x2468ACE0)
        request, header = csr.transport.make_request(4, 1, 0, payload)
        self.wire.send(request, header, payload, {"kind": "MOCK_ONLY"})
        body = struct.pack("<Q8I", 0, 0x400, 0, 0, 0, 0, 0, 1, 0) + bytes(range(256))
        response = csr.transport.Header(0x8004, 1, 0, 0, 0, 1, len(body), zlib.crc32(body))
        self.serial.raw.extend(response.pack() + body); self.wire.receipt(request)
        self.send_receive(1, 2, self.weights, epoch=0)
        self.send_receive(2, 3, struct.pack("<II", 1000, 2000) + self.input_raw, epoch=1, run=True)
        self.prior()

    def test_receipt_payload_header_and_raw_substitutions_are_rejected(self):
        self.seed()
        original = dict(self.wire.receipt_attempts[-1])
        request = csr.transport.Header.unpack(bytes.fromhex(original["request_header_hex"]))
        for key, value in (("request_payload_hex", "00"),
                           ("request_header_hex", csr.transport.Header(request.op, request.sequence,
                            1, request.width, request.height, request.repeat, request.length, request.payload_crc).pack().hex()),
                           ("raw_received_hex", self.wire.receipt_attempts[0]["raw_received_hex"]),
                           ("abort_ready", True)):
            with self.subTest(field=key):
                self.wire.receipt_attempts[-1] = {**original, key: value}
                with self.assertRaises((csr.CsrAcceptanceError, csr.transport.TransportError)):
                    self.prior()
        self.wire.receipt_attempts[-1] = original

    def test_failed_native_receipt_cannot_become_success_by_clearing_latch(self):
        self.seed()
        payload = struct.pack("<II", 1000, 2000) + self.input_raw
        request, header = csr.transport.make_request(2, 3, 0, payload, width=640, height=480)
        self.wire.send(request, header, payload, {"kind": "MOCK_ONLY"})
        self.serial.raw.extend(raw_response(request, 1, code=2))
        with self.assertRaises(csr.transport.TransportError):
            self.wire.receipt(request)
        self.wire.failed = False
        with self.assertRaises(csr.transport.TransportError):
            self.prior()

    def test_native_tx_event_and_disk_identity_are_required(self):
        self.seed()
        original = dict(self.wire.events[0])
        for key, value in (("sent_bytes", 40), ("sent_sha256", "0" * 64), ("status", "FAILED"),
                           ("payload_sha256", "0" * 64), ("frame", 1)):
            with self.subTest(field=key):
                self.wire.events[0] = {**original, key: value}
                with self.assertRaises(csr.CsrAcceptanceError):
                    self.prior()
        self.wire.events[0] = original
        self.tx.write(b"extra")
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "TX磁盘"):
            self.prior()

    def test_unbound_rx_prefix_is_rejected_but_real_banner_is_accepted(self):
        prefix = ("S2B-INFERENCE/1 READY SOURCE=" + "1" * 64 + " XSA=" + "2" * 64 +
                  " MODEL=" + csr.transport.MODEL_SHA + "\r\n").encode("ascii")
        self.rx.write(prefix); self.wire.rx_chunks.append(prefix)
        self.seed(); self.prior()
        actual = self.rx.tell()
        self.rx.seek(0); self.rx.write(b"X" + prefix[1:]); self.rx.seek(actual)
        self.wire.rx_chunks[0] = b"X" + prefix[1:]
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "banner"):
            self.prior()

    def test_sent_requests_without_receipt_are_rejected(self):
        self.seed(); self.wire.receipt_attempts.clear()
        with self.assertRaises(csr.CsrAcceptanceError):
            self.prior()

    def test_raw_disk_drift_is_rejected(self):
        self.seed(); self.rx.write(b"unexpected")
        with self.assertRaisesRegex(csr.CsrAcceptanceError, "原字节"):
            self.prior()

    def test_epoch_or_input_identity_drift_is_rejected(self):
        self.seed(); self.wire.epoch = 2
        with self.assertRaises(csr.transport.TransportError):
            self.prior()
        self.wire.epoch = 1; self.input_raw = b"X" * 519168
        with self.assertRaises(csr.CsrAcceptanceError):
            self.prior()

    def test_abort_ack_golden_recovery_uses_real_transport_and_t16(self):
        weights = self.root / "weights.bin"; weights.write_bytes(self.weights)
        input_path = self.root / "input.bin"; input_path.write_bytes(self.input_raw)
        basis = self.root / "basis.json"
        csr.transport.write_json_new(basis, {"scope": "MOCK_ONLY", "basis": "全负logits使objectness低于0.25，独立手算无框。"})
        tensors = {}
        for name, count in (("head13", 5070), ("head26", 20280)):
            path = self.root / (name + ".bin"); path.write_bytes(bytes([129]) * count)
            tensors[name] = {"path": str(path), "tensor_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "byte_length": count}
        row = {"frame_id": 0, "sample_id": "synthetic_mock_no_hand", "input": {"geometry_wh": [640, 480],
               "pl_input_sha256": hashlib.sha256(self.input_raw).hexdigest()}, "head_tensors": tensors,
               "nms_output_box_count": 0, "detections": []}
        source = self.root / "synthetic_source.json"
        csr.transport.write_json_new(source, {"schema_version": 1, "kind": "s2b_synthetic_hand_computed",
            "model_manifest_sha256": csr.transport.MODEL_SHA,
            "basis": {**csr.model.binding(basis), "description": "仅mock的独立全负logits空框"}, "samples": [row]})
        reference = self.root / "reference.json"
        csr.transport.write_json_new(reference, {"schema_version": 1, "kind": "s2b_fixed_reference",
            "model_manifest_sha256": csr.transport.MODEL_SHA,
            "golden_source": {"kind": "synthetic_hand_computed", **csr.model.binding(source)}, "samples": [row]})
        plan = {"weights": csr.model.binding(weights), "rows": [{"input": csr.model.binding(input_path), "reference": csr.model.binding(reference)}]}
        prep = self.root / "preparation.json"; csr.transport.write_json_new(prep, plan)
        self.seed()
        controller = FakeController(); controller.states["cpu0"] = "Running"; controller.app_running = True
        controller.row[0x050] = 1
        def respond(request, payload):
            if request.op == 3 and struct.unpack_from("<I", payload)[0] == 2:
                controller.row[0x00C] = 0x102; controller.row[0x058] = request.frame; controller.row[0x050] = 2
                self.serial.raw.extend(raw_response(request, 2, status=0x102, code=10))
                controller.on_abort = lambda: self.serial.raw.extend(raw_response(request, 2, status=0xC05, error=8))
            elif request.op == 3 and struct.unpack_from("<I", payload)[0] == 3:
                controller.row[0x00C] = 0x400; controller.row[0x010] = 0
                self.serial.raw.extend(raw_response(request, 2))
            elif request.op == 2:
                controller.row[0x050] = 3
                self.serial.raw.extend(raw_response(request, 3, status=0xE04, run=True))
            else:
                raise AssertionError("非预期UART请求")
        self.serial.on_request = respond
        runner_dir = self.root / "abort_run"; runner_dir.mkdir()
        runner = csr._Runner(controller, self.wire, runner_dir, {"scope": "MOCK_ONLY_NOT_BOARD"}, scope="MOCK_ONLY_NOT_BOARD")
        def execute(_controller, _wire, _config, _run, action, *, static):
            self.assertFalse(static)
            return action(runner)
        try:
            with mock.patch.object(csr, "_execute", side_effect=execute), mock.patch.object(csr.model, "validate_plan", return_value=None):
                result = csr.execute_abort_recovery(controller, self.wire, {"scope": "MOCK_ONLY"}, csr.model.binding(prep), runner_dir,
                                                    frame=10, core_timeout=1000, drain_timeout=2000)
            self.assertEqual(result["golden_epoch"], 3)
            self.assertEqual(result["abort_epoch"], 2)
            self.assertIsNone(self.wire.abort_pending)
            report = json.loads((runner_dir / "golden_sample000/recovery_00000011/capture_check.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS_OFFLINE_CAPTURE_CHECK")
        finally:
            runner.finish("MOCK_ONLY_NOT_BOARD")


if __name__ == "__main__":
    unittest.main()
