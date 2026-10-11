"""S2B-T18轻量mock回归；不打开串口、不调用SDK、不冒充实板证据。"""
from pathlib import Path
import copy
import json
import struct
import tempfile
import unittest
import zlib

try:
    from . import s2b_board_acceptance as acceptance
    from . import s2b_board_transport as transport
    from . import s2b_fixed_capture_check as checker
except ImportError:
    import s2b_board_acceptance as acceptance
    import s2b_board_transport as transport
    import s2b_fixed_capture_check as checker


class MockSerial:
    """只接收测试构造字节，短读/短写模拟普通驱动；永不操作设备。"""
    def __init__(self, raw=b""):
        self.raw, self.sent = bytearray(raw), bytearray()

    def read(self, count):
        count = min(count, 4096, len(self.raw))
        result = bytes(self.raw[:count]); del self.raw[:count]
        return result

    def write(self, raw):
        self.sent.extend(raw)
        return len(raw)


def response(request, *, epoch=1, index=0, frame=None, heads=None, boxes=(), status=0xE04):
    """显式构造little-endian协议帧，测试格式不声称模型计算正确。"""
    payload = struct.pack("<Q8I", epoch, status, 0, 0, len(boxes), len(boxes), index, request.repeat, 0)
    if request.op == transport.OP_RUN:
        payload += heads if heads is not None else bytes([129]) * 25350
        for box in boxes: payload += struct.pack("<ii5d", *box)
    prefix = struct.pack("<4sHH7I", b"S2BU", 1, request.op | 0x8000, request.sequence,
                         request.frame + index if frame is None else frame,
                         request.width, request.height, request.repeat, len(payload), zlib.crc32(payload))
    return prefix + struct.pack("<I", zlib.crc32(prefix)) + payload


class RunnerTests(unittest.TestCase):
    """使用独立手算全负logits空框来源调用真实checker，资源小于300MB。"""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s2b_t18_mock_")
        self.root = Path(self.tmp.name)
        self.rx = (self.root / "mock_uart_rx.bin").open("xb")
        self.tx = (self.root / "mock_uart_tx.bin").open("xb")
        self.serial = MockSerial()
        self.wire = transport.WireSession(self.serial, self.rx, self.tx, response_timeout=0.025)
        self.runner = acceptance.AcceptanceRunner(self.wire, self.root / "run", {"scope": "MOCK_ONLY"})
        basis = self.root / "basis.json"
        acceptance.save(basis, {"scope": "MOCK_ONLY", "reason": "INT8=-127，经冻结scale得到负logits，objectness低于0.25，故无框。"})
        input_path = self.root / "input.bin"
        input_path.write_bytes(bytes(transport.INPUT_BYTES))
        heads = {}
        for name, length in transport.HEAD_LENGTHS.items():
            path = self.root / (name + ".bin")
            path.write_bytes(bytes([129]) * length)
            heads[name] = {"path": str(path), "tensor_sha256": transport.digest(path.read_bytes()), "byte_length": length}
        row = {"frame_id": 0, "sample_id": "synthetic_mock_no_hand", "input": {"geometry_wh": [416, 416],
               "pl_input_sha256": transport.digest(input_path.read_bytes())}, "head_tensors": heads,
               "nms_output_box_count": 0, "detections": []}
        source = self.root / "synthetic_source.json"
        acceptance.save(source, {"schema_version": 1, "kind": "s2b_synthetic_hand_computed",
                        "model_manifest_sha256": transport.MODEL_SHA,
                        "basis": {**acceptance.binding(basis), "description": "独立手算全负logits空框；仅mock。"}, "samples": [row]})
        reference = self.root / "reference.json"
        acceptance.save(reference, {"schema_version": 1, "kind": "s2b_fixed_reference",
                        "model_manifest_sha256": transport.MODEL_SHA,
                        "golden_source": {"kind": "synthetic_hand_computed", **acceptance.binding(source)}, "samples": [row]})
        self.row = {"input": acceptance.binding(input_path), "reference": acceptance.binding(reference)}
        self.payload = struct.pack("<II", 0xFFFFFFFF, 17) + input_path.read_bytes()
        self.request, self.header = transport.make_request(2, 1, 109, self.payload, width=416, height=416, repeat=2)

    def tearDown(self):
        self.runner.log.close(); self.rx.close(); self.tx.close(); self.tmp.cleanup()

    def send(self, raw):
        self.serial.raw.extend(raw)
        self.wire.send(self.request, self.header, self.payload, {"scope": "MOCK_ONLY"})

    def test_empty_real_checker_and_continuous_epochs(self):
        self.send(response(self.request, epoch=1) + response(self.request, epoch=2, index=1))
        first = self.runner.receive(self.request, 0, self.row, "stress")
        second = self.runner.receive(self.request, 1, self.row, "stress")
        self.assertEqual((first["epoch"], second["epoch"]), (1, 2))
        self.assertEqual(self.wire.last_sequence, 1)
        result = json.loads((self.runner.run / "stress_00000110/result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["checker_identity_mapping"], {"actual_frame": 110, "frozen_reference_frame": 0,
                         "reason": "同固定输入repeat；协议身份由原UART独立核验"})
        report = json.loads((self.runner.run / "stress_00000110/capture_check.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS_OFFLINE_CAPTURE_CHECK")

    def test_duplicate_response_latches_and_preserves_raw(self):
        duplicate = response(self.request)
        self.send(duplicate + duplicate)
        self.runner.receive(self.request, 0, self.row, "stress")
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 1, self.row, "stress")
        self.assertTrue(self.runner.failed and self.wire.failed)
        self.assertEqual((self.runner.run / "stress_00000110/uart_response_raw.bin").read_bytes(), duplicate)
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 1, self.row, "stress")

    def test_missing_frame_is_not_recovered(self):
        skipped = response(self.request, epoch=2, index=1)
        self.send(skipped)
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "stress")
        self.assertEqual(self.wire.epoch, 0)
        self.assertEqual((self.runner.run / "stress_00000109/uart_response_raw.bin").read_bytes(), skipped)

    def test_wrong_head_retains_both_heads_and_checker_failure(self):
        heads = bytes([130]) + bytes([129]) * 25349
        self.send(response(self.request, heads=heads))
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "corpus")
        directory = self.runner.run / "corpus_00000109"
        self.assertEqual((directory / "head13.bin").read_bytes()[0], 130)
        self.assertEqual((directory / "head26.bin").stat().st_size, 20280)
        report = json.loads((directory / "capture_check.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "FAIL_OFFLINE_CAPTURE_CHECK")

    def test_all_multiple_boxes_preserved_before_golden_mismatch(self):
        boxes = [(0, 0, 0.9, .1, .1, .2, .2), (1, 1, .8, .5, .5, .7, .7)]
        self.send(response(self.request, boxes=boxes))
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "corpus")
        saved = json.loads((self.runner.run / "corpus_00000109/boxes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(saved), 2)
        self.assertEqual([item["source_order"] for item in saved], [0, 1])

    def test_full_multiple_box_comparison(self):
        boxes = [{"class_id": i, "class_name": transport.CLASS_NAMES[i], "score": .8,
                  "source_order": i, "xyxy": [.1, .1, .4, .4]} for i in range(3)]
        self.assertTrue(checker.compare_detections(boxes, copy.deepcopy(boxes))["match"])
        changed = copy.deepcopy(boxes); changed[-1]["xyxy"][3] += .01
        self.assertFalse(checker.compare_detections(boxes, changed)["match"])
        self.assertFalse(checker.compare_detections(boxes, boxes[:1])["match"])

    def test_wrong_golden_sha_latches_after_capture_saved(self):
        self.row["reference"]["sha256"] = "0" * 64
        self.send(response(self.request))
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "corpus")
        directory = self.runner.run / "corpus_00000109"
        self.assertTrue((directory / "head13.bin").is_file() and (directory / "boxes.json").is_file())
        self.assertTrue(self.wire.failed)

    def test_timeout_retains_partial_header_and_latches(self):
        self.send(response(self.request)[:13])
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "stress")
        self.assertEqual((self.runner.run / "stress_00000109/uart_response_raw.bin").stat().st_size, 13)
        self.assertTrue(self.wire.failed)

    def test_epoch_duplicate_is_rejected(self):
        self.send(response(self.request, epoch=1) + response(self.request, epoch=1, index=1))
        self.runner.receive(self.request, 0, self.row, "stress")
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 1, self.row, "stress")

    def test_owner_unsafe_is_rejected(self):
        self.send(response(self.request, status=0xF04))
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "corpus")
        self.assertTrue(self.wire.failed)

    def test_crc_failure_preserves_raw(self):
        raw = bytearray(response(self.request)); raw[-1] ^= 1
        self.send(raw)
        with self.assertRaises(transport.TransportError): self.runner.receive(self.request, 0, self.row, "corpus")
        self.assertEqual((self.runner.run / "corpus_00000109/uart_response_raw.bin").read_bytes(), raw)

    def test_fake_admission_is_blocked_before_uart_tx(self):
        before = bytes(self.serial.sent)
        with self.assertRaises(transport.TransportError):
            acceptance.execute(object(), self.wire, self.root / "missing.json", self.root / "blocked",
                               build_details=self.root / "missing_build.json", drain_timeout=1,
                               visibility_proof=True, review=True, review_sha256="0" * 64)
        self.assertEqual(bytes(self.serial.sent), before)
        result = json.loads((self.root / "blocked/acceptance_result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "BLOCKED_BEFORE_TX")
        self.assertEqual(result["hardware_execution"], "NOT_RUN")

    def test_runid_refuses_overwrite(self):
        with self.assertRaises(transport.TransportError): acceptance.AcceptanceRunner(self.wire, self.runner.run, {})

    def test_input_drift_rejected_before_send(self):
        input_path = Path(self.row["input"]["path"])
        input_path.write_bytes(bytes([1]) * transport.INPUT_BYTES)
        with self.assertRaises(transport.TransportError):
            self.runner.run_input(self.row, 1, 109, 2, 0xFFFFFFFF, 17, "stress")
        self.assertEqual(self.serial.sent, b"")

    def test_request_choreography_short_mock_corpus_and_stress(self):
        weight = self.root / "mock_weights.bin"
        weight.write_bytes(bytes(transport.WEIGHT_BYTES))
        plan = {"weights": acceptance.binding(weight), "rows": [self.row]}
        req1, _ = transport.make_request(1, 1, 0, weight.read_bytes())
        req2, _ = transport.make_request(2, 2, 0, self.payload, width=416, height=416)
        req3, _ = transport.make_request(2, 3, 1, self.payload, width=416, height=416, repeat=2)
        self.serial.raw.extend(response(req1, epoch=0, status=0x400) + response(req2, epoch=1) +
                               response(req3, epoch=2) + response(req3, epoch=3, index=1))
        self.runner.models(plan, 0xFFFFFFFF, 17, stress_count=2)
        self.assertEqual(self.runner.record["completed_corpus"], 1)
        self.assertEqual(self.runner.record["completed_stress"], 2)
        self.assertEqual((self.wire.last_sequence, self.wire.epoch), (3, 3))
        planned = json.loads((self.runner.run / "request_00000003.json").read_text(encoding="utf-8"))
        self.assertEqual((planned["repeat"], planned["core_timeout"], planned["drain_timeout"]), (2, 0xFFFFFFFF, 17))


if __name__ == "__main__":
    unittest.main()
