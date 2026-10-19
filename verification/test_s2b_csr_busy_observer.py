"""T20 busy观测器离线回归：真实控制器/运输器加原生内存设备，不连接SDK或串口。"""
from pathlib import Path
import copy
import hashlib
import json
import os
import shutil
import struct
import tempfile
import unittest
import zlib

try:
    from . import s2b_csr_busy_observer as busy
    from .test_s2b_board_jtag import FakeSession, FakeTarget, elf_bytes
    from .test_s2b_csr_board_acceptance import snapshot
except ImportError:
    import s2b_csr_busy_observer as busy
    from test_s2b_board_jtag import FakeSession, FakeTarget, elf_bytes
    from test_s2b_csr_board_acceptance import snapshot

j, model, transport = busy.jtag, busy.model, busy.transport
AHB_AP_BUSY_WRITE_ERROR = (
    'TCF command exception:\n'
    'Command: Memory set "JTAG-jsn-JTAG-HS1-210512180081-4ba00477-0", 1136656392, 0, 4...\n'
    'Exception: Memory write error at 0x43C00008. AHB AP transaction error, DAP status 0xF0000021\n'
    'Error code: 1'
)


def ahb_ap_error(*, command_address=1136656392, error_address="0x43C00008", dap_status="0xF0000021", code=1):
    """构造原生DAP错误格式；参数变化用于证明分类器按精确签名拒绝。"""
    return (
        'TCF command exception:\n'
        f'Command: Memory set "JTAG-jsn-JTAG-HS1-210512180081-4ba00477-0", {command_address}, 0, 4...\n'
        f'Exception: Memory write error at {error_address}. AHB AP transaction error, DAP status {dap_status}\n'
        f'Error code: {code}'
    )
TEST_PARENT = busy.csr.ROOT / "tmp/2B/S2B-T20/busy_observer_offline"


def reply(request, epoch, heads, boxes, *, reject=0):
    """独立little-endian响应，不使用被测receipt的返回值制造成功。"""
    run = request.op == 2
    payload = struct.pack("<Q8I", epoch, 0xE04 if run else 0x400, 0, reject,
                          len(boxes) if run else 0, len(boxes) if run else 0, 0, 1, 0)
    if run:
        payload += heads
        for box in boxes:
            payload += struct.pack("<ii5d", box["class_id"], box["source_order"], box["score"], *box["xyxy"])
    prefix = struct.pack("<4sHH7I", b"S2BU", 1, request.op | 0x8000, request.sequence,
                         request.frame, request.width, request.height, request.repeat, len(payload), zlib.crc32(payload))
    return prefix + struct.pack("<I", zlib.crc32(prefix)) + payload


class NativeTarget(FakeTarget):
    """逐次真实方法调用产生mock响应；无需替换控制器方法或外部callback。"""
    def mrd(self, *args, address, size, word_size):
        s = self.session
        if address == j.CSR_BASE + 0x00C and size == 27 and s.busy_active:
            s.full_reads += 1
            if s.delayed_start:
                s.memory[j.CSR_BASE + 0x050] = 2
            if s.full_reads == 1 and s.start_state == 1:
                s.memory[j.CSR_BASE + 0x00C] = 0x101
                s.memory[j.CSR_BASE + 0x068] = 0
            else:
                s.memory[j.CSR_BASE + 0x00C] = 0x1102 if s.full_reads % 2 else 0x102
                s.memory[j.CSR_BASE + 0x068] = 7 if s.full_reads % 2 else 0
            if s.mutation is not None and s.rejected:
                offset, value = s.mutation
                s.memory[j.CSR_BASE + offset] = value
        if address == j.CSR_BASE + 0x054 and s.torn_epoch and s.busy_active:
            s.high_reads += 1
            return s.high_reads % 2
        return super().mrd(*args, address=address, size=size, word_size=word_size)

    def mwr(self, *args, address, size, word_size, words):
        s = self.session
        if (args, address, size, word_size, words) != (("--bypass_cache_synq",), j.CSR_BASE + 8, 1, 4, [1]):
            raise AssertionError("只允许本次DAP COMMAND=START")
        s.operations.append(("mwr", self._name, address, words))
        s.rejected = True
        s.memory[j.CSR_BASE + 0x064] = 1
        if s.finish_after_write:
            s.busy_active = False
            s.memory[j.CSR_BASE + 0x00C] = 0xE04
        if s.bus_error is not None:
            raise RuntimeError(s.bus_error)

    def stop(self):
        super().stop()
        s = self.session
        if s.fail_stop_native:
            raise RuntimeError("mock stop native failure")
        if s.finish_on_stop:
            s.busy_active = False
            s.memory[j.CSR_BASE + 0x00C] = 0xE04

    def con(self, *args, **kwargs):
        super().con(*args, **kwargs)
        s = self.session
        if s.fail_resume_native:
            raise RuntimeError("mock continue native failure")
        s.serial.complete()


class NativeSession(FakeSession):
    """内存中模拟已部署且有界的PL动作，所有case均标记MOCK_ONLY。"""
    def __init__(self):
        super().__init__()
        self.objects = {row["target_id"]: NativeTarget(self, row) for row in self.rows.values()}
        self.memory.update({j.CSR_BASE + offset: value for offset, value in snapshot().items()})
        self.busy_active = self.rejected = self.torn_epoch = False
        self.full_reads = self.high_reads = 0
        self.mutation = None
        self.start_state = 2
        self.finish_on_stop = self.finish_on_send = False
        self.delayed_start = self.finish_after_write = False
        self.fail_stop_native = self.fail_resume_native = False
        self.stale_reject = False


class NativeSerial:
    """流式接收实际header/payload字节；只有mock CPU0继续后发布下一RUN响应。"""
    def __init__(self, session, heads, boxes):
        self.session, self.heads, self.boxes = session, heads, boxes
        self.pending, self.raw = bytearray(), bytearray()
        self.next_request = None
        self.response_fault = None

    def write(self, raw):
        self.pending.extend(raw)
        if len(self.pending) >= 40:
            request = transport.Header.unpack(bytes(self.pending[:40]))
            if len(self.pending) == 40 + request.length:
                payload = bytes(self.pending[40:]); self.pending.clear()
                if request.op == 1:
                    self.raw.extend(reply(request, self.session.memory[j.CSR_BASE + 0x050], self.heads, self.boxes))
                elif request.frame == 0:
                    epoch = self.session.memory[j.CSR_BASE + 0x050] + 1
                    self.raw.extend(reply(request, epoch, self.heads, self.boxes))
                    self.session.memory[j.CSR_BASE + 0x050] = epoch
                    self.session.memory[j.CSR_BASE + 0x05C] = epoch
                else:
                    s = self.session
                    self.next_request = request
                    core, drain = struct.unpack_from("<II", payload)
                    values = {0x00C: 0x100 | s.start_state, 0x014: request.frame, 0x050: 2,
                              0x058: request.frame, 0x028: core, 0x02C: drain,
                              0x064: 1 if s.stale_reject else 0}
                    s.memory.update({j.CSR_BASE + key: value for key, value in values.items()})
                    s.busy_active = True
                    if s.delayed_start:
                        s.memory[j.CSR_BASE + 0x00C] = 0x400
                        s.memory[j.CSR_BASE + 0x050] = 1
                    if s.finish_on_send:
                        s.busy_active = False
                        s.memory[j.CSR_BASE + 0x00C] = 0xE04
        return len(raw)

    def read(self, count):
        result = bytes(self.raw[:count]); del self.raw[:count]
        return result

    def complete(self):
        """明确注入错误头/框/CRC，所有错误仍走真实运输解析器。"""
        heads, boxes = self.heads, copy.deepcopy(self.boxes)
        if self.response_fault == "head":
            heads = bytes([130]) + heads[1:]
        if self.response_fault == "box":
            boxes[-1]["xyxy"][3] += .01
        if self.response_fault == "missing_box":
            boxes.pop()
        result = bytearray(reply(self.next_request, 3 if self.response_fault == "epoch" else 2,
                                 heads, boxes, reject=0 if self.response_fault == "reject" else 1))
        if self.response_fault == "header_crc":
            result[36] ^= 1
        if self.response_fault == "payload_crc":
            result[-1] ^= 1
        self.raw.extend(result)
        self.session.busy_active = False
        self.session.memory[j.CSR_BASE + 0x00C] = 0x400
        for offset in (0x068, 0x06C, 0x070, 0x074):
            self.session.memory[j.CSR_BASE + offset] = 0


class BusyObserverTests(unittest.TestCase):
    """独立手算两框黄金，真实磁盘/TX/RX/receipt与原生SDK包装贯穿正反例。"""
    def setUp(self):
        TEST_PARENT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="case_", dir=TEST_PARENT)
        self.root = Path(self.temp.name)
        self.session = NativeSession()
        self.bindings = {}
        for name in ("init_elf", "app_elf", "xsa", "bit", "csr_source", "interface", "sdk_target"):
            path = self.root / name
            path.write_bytes(elf_bytes(app=name == "app_elf") if name.endswith("elf") else b"MOCK_ONLY")
            self.bindings[name] = model.binding(path)
        for key, name in (("tool_source", "s2b_board_jtag.py"), ("elf_parser", "check_s2b_ps_smoke_layout.py"),
                          ("delivery_parser", "check_stage_delivery.py"), ("transport_source", "s2b_board_transport.py")):
            self.bindings[key] = model.binding(Path(j.__file__).parent / name)
        controller_dir = self.root / "controller"; controller_dir.mkdir()
        self.controller = j.JtagController(self.session, self.bindings, controller_dir)
        self.controller.select_and_gate()
        self.controller.app_running = self.controller.configured = True
        self.controller.targets["cpu0"].running = True
        self.heads = bytearray([129]) * 25350
        self.boxes = []
        for row, col, class_id in ((4, 3, 1), (6, 6, 0)):
            cell = row * 13 + col
            for entry in (0, 1, 2, 3, 4, 5 + class_id):
                self.heads[entry * 169 + cell] = 0
            cx, cy = (col + .5) * 32, (row + .5) * 32
            self.boxes.append({"class_id": class_id, "class_name": transport.CLASS_NAMES[class_id],
                "score": .25, "source_order": cell * 15 + class_id,
                "xyxy": [(cx - 40.5) / 416, (cy - 41 - 52) / 312,
                         (cx + 40.5) / 416, (cy + 41 - 52) / 312]})
        self.heads = bytes(self.heads)
        self.serial = NativeSerial(self.session, self.heads, self.boxes)
        self.session.serial = self.serial
        self.rx = (self.root / "rx.bin").open("xb")
        self.tx = (self.root / "tx.bin").open("xb")
        self.wire = j.JtagWireSession(self.serial, self.rx, self.tx, response_timeout=.05)
        input_path, weight_path = self.root / "input.bin", self.root / "weights.bin"
        input_path.write_bytes(b"I" * 519168); weight_path.write_bytes(b"W" * 5903100)
        tensors = {}
        for name, start, size in (("head13", 0, 5070), ("head26", 5070, 20280)):
            path = self.root / (name + ".bin"); path.write_bytes(self.heads[start:start + size])
            tensors[name] = {"path": str(path), "byte_length": size, "tensor_sha256": transport.digest(path.read_bytes())}
        self.geometry = [1440, 1920] if self._testMethodName == "test_busy_request_uses_frozen_sample_geometry" else [640, 480]
        sample = {"frame_id": 0, "sample_id": "synthetic_busy_two_boxes", "input": {
            "geometry_wh": self.geometry, "pl_input_sha256": transport.digest(input_path.read_bytes())},
            "head_tensors": tensors, "nms_output_box_count": 2, "detections": self.boxes}
        basis = self.root / "basis.json"
        model.save(basis, {"scope": "MOCK_ONLY", "method": "两个head13 anchor0位置的xywh/object/class为0，其余INT8=-127；sigmoid(0)^2=0.25。anchor81×82，416×312加上下52，直接算出两框；不同类别不互相NMS。"})
        source = self.root / "golden_source.json"
        model.save(source, {"schema_version": 1, "kind": "s2b_synthetic_hand_computed", "model_manifest_sha256": transport.MODEL_SHA,
            "basis": {**model.binding(basis), "description": "独立手算两个非空合法框，仅mock"}, "samples": [sample]})
        reference = self.root / "reference.json"
        self.reference_path = reference
        model.save(reference, {"schema_version": 1, "kind": "s2b_fixed_reference", "model_manifest_sha256": transport.MODEL_SHA,
            "golden_source": {"kind": "synthetic_hand_computed", **model.binding(source)}, "samples": [sample]})
        self.row = {"input": model.binding(input_path), "reference": model.binding(reference)}
        self.plan = {"weights": model.binding(weight_path), "rows": [self.row]}
        self.send_receipt(1, 1, weight_path.read_bytes())
        self.send_receipt(2, 2, struct.pack("<II", 0xFFFFFFFF, 50000000) + input_path.read_bytes())
        self.initial = {offset: self.session.memory[j.CSR_BASE + offset] for offset in busy.csr.OFFSETS}
        self.run = self.root / "observer"; self.run.mkdir()
        self.observer = busy._Observer(self.controller, self.wire, self.run, {"scope": "MOCK_ONLY_NOT_BOARD"},
                                      self.initial, scope="MOCK_ONLY_NOT_BOARD")

    def tearDown(self):
        if not self.observer.log.closed:
            self.observer.finish("MOCK_ONLY_NOT_EXECUTED")
        self.controller.log.close(); self.rx.close(); self.tx.close()
        # 仅显式选定的代表性证据持久化；其余独占临时目录由TemporaryDirectory回收。
        destination = os.environ.get("S2B_BUSY_FIXTURE_OUTPUT")
        if destination and self._testMethodName in ("test_progress_change_nonempty_gold_success", "test_unknown_native_response_blocks"):
            parent = transport.exact_path(destination, "directory")
            target = parent / self._testMethodName
            shutil.copytree(self.run, target)
            archived = target / "fixture_originals"; archived.mkdir()
            index = []
            for name in ("input.bin", "head13.bin", "head26.bin", "reference.json", "golden_source.json",
                         "basis.json", "rx.bin", "tx.bin"):
                original = self.root / name
                shutil.copyfile(original, archived / name)
                index.append({"original_path": str(original), "archived_path": str(archived / name),
                              "sha256": hashlib.sha256(original.read_bytes()).hexdigest()})
            model.save(archived / "index.json", {"scope": "MOCK_ONLY_NOT_BOARD", "files": index,
                "reason": "保留临时夹具的逐字原件及路径映射，不改写原checker记录；可用测试源码重建夹具。",
                "weights": {"generation": "ASCII W重复5903100次", **self.plan["weights"]}})
        self.temp.cleanup()

    def send_receipt(self, op, sequence, payload):
        """严格有序的真实发送与消费，禁止伪造receipt历史。"""
        request, header = transport.make_request(op, sequence, 0, payload,
            width=self.geometry[0] if op == 2 else 0, height=self.geometry[1] if op == 2 else 0)
        self.wire.send(request, header, payload, {"scope": "MOCK_ONLY"})
        return self.wire.receipt(request)

    def execute(self):
        request, header, payload = busy._request(self.wire, self.plan)
        return self.observer.execute(request, header, payload, self.row, observation_seconds=.1, poll_seconds=.001)

    def result(self):
        return json.loads((self.run / "busy_result.json").read_text(encoding="utf-8"))

    def assert_failure(self, kind=Exception):
        with self.assertRaises(kind):
            self.execute()
        self.assertTrue(self.controller.failed and self.wire.failed)
        self.assertFalse(self.controller.targets["cpu0"].running)
        operations = self.session.operations
        self.assertFalse(any(row[0] in ("con", "stop", "rst") and row[1] == j.NAMES[2] for row in operations))
        self.assertNotEqual(self.result()["status"], "PASS_BUSY_START_REJECTION_AND_GOLD")

    def test_progress_change_nonempty_gold_success(self):
        result = self.execute()
        self.assertEqual(result["status"], "PASS_BUSY_START_REJECTION_AND_GOLD")
        before, after = result["rejection"]["before"], result["rejection"]["after"]
        self.assertNotEqual(before[0x068], after[0x068])
        self.assertEqual((before[0x064], after[0x064]), (0, 1))
        self.assertEqual((self.wire.epoch, self.wire.last_sequence), (2, 3))
        boxes = json.loads((self.run / "same_run_golden/boxes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(boxes), 2)
        self.assertEqual((self.run / "same_run_golden/head13.bin").read_bytes(), self.heads[:5070])
        self.assertEqual((self.run / "same_run_golden/head26.bin").read_bytes(), self.heads[5070:])
        self.assertEqual(len(self.wire.receipt_attempts), 3)
        self.assertEqual([row[0] for row in self.session.operations], ["stop", "mwr", "con"])
        self.assertIn('"kind": "observation"', (self.run / "busy_events.jsonl").read_text(encoding="utf-8"))

    def test_exact_ahb_ap_error_only_claims_gold_with_bresp_unresolved(self):
        self.session.bus_error = AHB_AP_BUSY_WRITE_ERROR
        result = self.execute()
        self.assertEqual(result["status"], "BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED")
        rejection = result["rejection"]
        self.assertEqual(rejection["native_response"], "UNKNOWN")
        self.assertEqual(rejection["classification"], "AHB_AP_TRANSACTION_ERROR_BRESP_UNRESOLVED")
        self.assertEqual((rejection["expected_bresp"], rejection["observed_bresp"]),
                         ("SLVERR", "NOT_OBSERVED"))
        self.assertEqual(rejection["exception_text"], AHB_AP_BUSY_WRITE_ERROR)
        self.assertEqual((rejection["before"][0x064], rejection["after"][0x064]), (0, 1))
        for snapshot in (rejection["before"], rejection["after"]):
            self.assertIn(snapshot[0x00C], (0x102, 0x1102))
            self.assertEqual((snapshot[0x050], snapshot[0x058]), (2, 1))
        allowed = (0x00C, 0x064, 0x068)
        self.assertTrue(all(rejection["before"][key] == rejection["after"][key]
                            for key in busy.csr.OFFSETS if key not in allowed))
        self.assertEqual(result["golden"]["status"], "PASS_SAME_RUN_RECEIPT_AND_GOLD")
        self.assertEqual(result["ack_idle"][0x00C], 0x400)
        self.assertEqual((busy.csr.epoch(result["ack_idle"]), result["ack_idle"][0x058]), (2, 1))
        self.assertEqual([row[0] for row in self.session.operations], ["stop", "mwr", "con"])

    def test_ahb_ap_error_at_other_address_is_not_accepted(self):
        self.session.bus_error = ahb_ap_error(error_address="0x43C0000C")
        self.assert_failure()
        self.assertEqual(self.result()["rejection"]["native_response"], "UNKNOWN")
        self.assertNotIn("classification", self.result()["rejection"])
        self.assertFalse(any(row[0] == "con" for row in self.session.operations))

    def test_ahb_ap_error_does_not_hide_same_run_golden_failure(self):
        self.session.bus_error = AHB_AP_BUSY_WRITE_ERROR
        self.serial.response_fault = "head"
        self.assert_failure()
        self.assertNotEqual(self.result()["status"], "BUSY_REJECTION_AND_GOLD_BRESP_UNRESOLVED")
        golden = json.loads((self.run / "same_run_golden/result.json").read_text(encoding="utf-8"))
        self.assertEqual(golden["status"], "FAIL_LATCHED")
        self.assertEqual((self.run / "same_run_golden/head13.bin").read_bytes()[0], 130)

    def test_busy_request_uses_frozen_sample_geometry(self):
        request, _, _ = busy._request(self.wire, self.plan)
        self.assertEqual((request.width, request.height), (1440, 1920))

    def test_arming_to_run_is_legal(self):
        self.session.start_state = 1
        self.assertEqual(self.execute()["status"], "PASS_BUSY_START_REJECTION_AND_GOLD")

    def test_initial_idle_to_run_crossing_is_reobserved(self):
        self.session.delayed_start = True
        self.assertEqual(self.execute()["status"], "PASS_BUSY_START_REJECTION_AND_GOLD")
        observations = [json.loads(line) for line in (self.run / "busy_events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertGreaterEqual(sum(row["kind"] == "observation" and row["value"]["label"] == "await_busy"
                                    for row in observations), 2)

    def test_run_to_arming_regression_fails(self):
        self.session.mutation = (0x00C, 0x101)
        self.assert_failure()

    def test_terminal_after_write_does_not_prove_busy_rejection(self):
        self.session.finish_after_write = True
        self.assert_failure(busy.BusyWindowUnavailable)
        self.assertTrue(self.result()["dap_start_attempted"])
        self.assertFalse(any(row[0] == "con" for row in self.session.operations))

    def test_unknown_native_response_blocks(self):
        self.session.bus_error = "DAP write failed"
        self.assert_failure()
        self.assertEqual(self.result()["rejection"]["native_response"], "UNKNOWN")
        self.assertFalse(any(row[0] == "con" for row in self.session.operations))

    def test_okay_is_not_rejection(self):
        self.session.bus_error = None
        self.assert_failure()

    def test_decerr_is_not_slverr(self):
        self.session.bus_error = "DECERR"
        self.assert_failure()
        self.assertEqual(self.result()["rejection"]["observed_bresp"], "DECERR")

    def test_stale_reject_one_cannot_pass(self):
        self.session.stale_reject = True
        self.assert_failure()
        self.assertFalse(self.result()["dap_start_attempted"])

    def test_configuration_mutation_fails(self):
        self.session.mutation = (0x018, 4)
        self.assert_failure()

    def test_epoch_mutation_fails(self):
        self.session.mutation = (0x050, 3)
        self.assert_failure()

    def test_frame_mutation_fails(self):
        self.session.mutation = (0x058, 2)
        self.assert_failure()

    def test_owner_mutation_fails(self):
        self.session.mutation = (0x00C, 2)
        self.assert_failure()

    def test_first_error_pending_fails(self):
        self.session.mutation = (0x00C, 0x2102)
        self.assert_failure()

    def test_fault_address_is_not_dynamic_progress(self):
        self.session.mutation = (0x06C, 0x100)
        self.assert_failure()

    def test_torn_epoch_fails(self):
        self.session.torn_epoch = True
        self.assert_failure()

    def test_terminal_before_stop_is_not_executed_busy(self):
        self.session.finish_on_send = True
        self.assert_failure(busy.BusyWindowUnavailable)
        self.assertEqual(self.result()["status"], "NOT_EXECUTED_IN_BUSY")
        self.assertFalse(self.result()["dap_start_attempted"])

    def test_terminal_after_stop_is_not_executed_busy(self):
        self.session.finish_on_stop = True
        self.assert_failure(busy.BusyWindowUnavailable)
        self.assertFalse(self.result()["dap_start_attempted"])
        self.assertFalse(any(row[0] == "con" for row in self.session.operations))

    def test_stop_failure_never_resumes(self):
        self.session.fail_stop_native = True
        self.assert_failure()
        self.assertFalse(any(row[0] in ("con", "mwr") for row in self.session.operations))

    def test_resume_failure_stops_running_cpu0(self):
        self.session.fail_resume_native = True
        self.assert_failure()
        self.assertEqual([row[0] for row in self.session.operations], ["stop", "mwr", "con", "stop"])

    def test_wrong_head_retained_and_rejected(self):
        self.serial.response_fault = "head"
        self.assert_failure()
        self.assertEqual((self.run / "same_run_golden/head13.bin").read_bytes()[0], 130)

    def test_wrong_last_box_retained_and_rejected(self):
        self.serial.response_fault = "box"
        self.assert_failure()
        self.assertEqual(len(json.loads((self.run / "same_run_golden/boxes.json").read_text(encoding="utf-8"))), 2)

    def test_missing_box_rejected(self):
        self.serial.response_fault = "missing_box"
        self.assert_failure()

    def test_header_crc_failure_retains_uart(self):
        self.serial.response_fault = "header_crc"
        self.assert_failure()
        self.assertGreaterEqual((self.run / "same_run_golden/uart_response_raw.bin").stat().st_size, 40)

    def test_payload_crc_failure_retains_uart(self):
        self.serial.response_fault = "payload_crc"
        self.assert_failure()
        self.assertGreater((self.run / "same_run_golden/uart_response_raw.bin").stat().st_size, 25350)

    def test_response_epoch_is_bound(self):
        self.serial.response_fault = "epoch"
        self.assert_failure()

    def test_response_reject_must_still_be_one(self):
        self.serial.response_fault = "reject"
        self.assert_failure()

    def test_changed_load_history_blocks_request(self):
        self.send_receipt(1, 3, b"R" * 5903100)
        self.send_receipt(2, 4, struct.pack("<II", 100, 200) + b"I" * 519168)
        with self.assertRaisesRegex(busy.csr.CsrAcceptanceError, "最后有效LOAD"):
            busy._request(self.wire, self.plan)

    def test_unconsumed_request_blocks_request(self):
        request, header = transport.make_request(1, 3, 0, b"W" * 5903100)
        self.wire.send(request, header, b"W" * 5903100, {"scope": "MOCK_ONLY"})
        with self.assertRaisesRegex(busy.csr.CsrAcceptanceError, "未消费"):
            busy._request(self.wire, self.plan)

    def test_wrong_seed_geometry_blocks_request(self):
        payload = struct.pack("<II", 100, 200) + b"I" * 519168
        request, header = transport.make_request(2, 3, 0, payload, width=416, height=416)
        self.wire.send(request, header, payload, {"scope": "MOCK_ONLY"})
        self.serial.raw.clear()
        self.serial.raw.extend(reply(request, 2, self.heads, self.boxes))
        self.wire.receipt(request)
        with self.assertRaisesRegex(busy.csr.CsrAcceptanceError, "sample000"):
            busy._request(self.wire, self.plan)

    def test_tx_disk_drift_blocks_request(self):
        self.tx.write(b"unexpected"); self.tx.flush()
        with self.assertRaisesRegex(busy.csr.CsrAcceptanceError, "TX磁盘"):
            busy._request(self.wire, self.plan)

    def test_receipt_history_crc_drift_blocks_request(self):
        raw = bytearray.fromhex(self.wire.receipt_attempts[-1]["raw_received_hex"])
        raw[36] ^= 1
        self.wire.receipt_attempts[-1]["raw_received_hex"] = raw.hex()
        with self.assertRaises(Exception):
            busy._request(self.wire, self.plan)

    def test_real_public_type_gate_rejects_bool_or_dict(self):
        with self.assertRaisesRegex(busy.csr.CsrAcceptanceError, "真实T16"):
            busy.csr.preflight({}, True, {}, static=False)

    def test_incomplete_plan_is_not_accepted(self):
        with self.assertRaises((KeyError, transport.TransportError)):
            model.validate_plan(self.plan)

    def test_invalid_seconds_are_rejected(self):
        for value in (True, 0, -1, float("inf"), float("nan"), 121):
            with self.subTest(value=value), self.assertRaises(busy.csr.CsrAcceptanceError):
                busy._seconds(value, "观察期限", 120)


if __name__ == "__main__":
    unittest.main()
