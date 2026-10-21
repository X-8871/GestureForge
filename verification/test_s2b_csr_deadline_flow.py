"""T20 deadline流程离线协议回归；不创建SDK会话或串口。"""
from pathlib import Path
import json
import tempfile
import unittest
import zlib

try:
    from . import s2b_board_jtag as jtag
    from . import s2b_board_transport as transport
    from . import s2b_csr_deadline_flow as flow
except ImportError:
    import s2b_board_jtag as jtag
    import s2b_board_transport as transport
    import s2b_csr_deadline_flow as flow


class FakeSerial:
    """仅提供确定性内存字节流，不接触系统串口。"""
    def __init__(self, response):
        self.incoming = bytearray()
        self.response = response
        self.responded = False
        self.outgoing = bytearray()

    @property
    def in_waiting(self):
        return len(self.incoming)

    def write(self, raw):
        self.outgoing.extend(raw)
        if not self.responded:
            self.incoming.extend(self.response)
            self.responded = True
        return len(raw)

    def read(self, length):
        count = min(length, len(self.incoming))
        raw = bytes(self.incoming[:count])
        del self.incoming[:count]
        return raw


class FakeController:
    """模拟CPU0 resume调用门禁，供DIAG解码路径离线测试。"""
    def __init__(self):
        self.cpu0_state = "Stopped"
        self.cpu1_state = "Stopped"
        self.stop_fails = False
        self.targets = {"cpu0": type("Cpu", (), {"con": lambda _self: None,
                                                    "stop": lambda _self: self._stop_cpu0()})()}
        self.calls = []

    def _stop_cpu0(self):
        if self.stop_fails:
            raise RuntimeError("mock CPU0 stop failure")
        self.cpu0_state = "Stopped"

    def gate(self, *, both):
        return None

    def call(self, name, function, *args, **kwargs):
        self.calls.append(name)
        result = function(*args, **kwargs)
        if name.endswith("resume_for_mode0_epoch_diag"):
            self.cpu0_state = "Running"
        return result

    def state(self, label):
        return self.cpu0_state if label == "cpu0" else self.cpu1_state


def diag_response(epoch, sequence=1, frame=0):
    """构造带真实协议CRC的mode0 IDLE应答原字节。"""
    payload = transport.META.pack(epoch, 0x400, 0, 0, 0, 0, 0, 1, 0)
    header = transport.Header(transport.OP_DIAG | 0x8000, sequence, frame, 0, 0, 1,
                              len(payload), zlib.crc32(payload)).pack()
    return header + payload


class DeadlineFlowTests(unittest.TestCase):
    def test_epoch_causality_full_sequence_uses_unique_real_files(self):
        """以真实临时目录重放三个阶段写入，防止exclusive创建重名失败。"""
        filenames = (
            "deadline_epoch_causality_after_normal_start.json",
            "deadline_epoch_causality_after_core_timeout.json",
            "deadline_epoch_causality_after_drain_limit.json",
        )
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            causality = {
                "seed_uart_epoch": 1,
                "normal_start_terminal_epoch": 2,
                "uart_epoch_after_normal_start": 1,
                "after_normal_ack_csr_epoch": 2,
            }
            flow._save_epoch_causality(run_dir, "after_normal_start", causality)

            causality.update(core_timeout_terminal_epoch=3,
                             after_core_ack_csr_epoch=3,
                             next_drain_start_expected_epoch=4)
            flow._save_epoch_causality(run_dir, "after_core_timeout", causality)

            causality.update(drain_timeout_terminal_epoch=4,
                             after_drain_ack_csr_epoch=4)
            flow._save_epoch_causality(run_dir, "after_drain_limit", causality)

            self.assertEqual({path.name for path in run_dir.iterdir()}, set(filenames))
            self.assertEqual(json.loads((run_dir / filenames[0]).read_text(encoding="utf-8"))
                             ["after_normal_ack_csr_epoch"], 2)
            self.assertEqual(json.loads((run_dir / filenames[1]).read_text(encoding="utf-8"))
                             ["after_core_ack_csr_epoch"], 3)
            final = json.loads((run_dir / filenames[2]).read_text(encoding="utf-8"))
            self.assertEqual(final["next_drain_start_expected_epoch"], 4)
            self.assertEqual(final["after_drain_ack_csr_epoch"], 4)

    def test_real_done_safe_fixture_with_head_valid_is_accepted(self):
        fixture_path = (flow.ROOT / "report/evidence/S2B-T18/"
                        "r10_interruption_observer_20261020_r02/observation.json")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        terminal = {int(key): value for key, value in fixture["csr"].items()}
        self.assertEqual(fixture["status"], "OBSERVATIONS_SAVED_NOT_ACCEPTANCE")
        self.assertEqual(terminal[0x00C], 0xE04)
        self.assertEqual(flow._normal_start_phase(terminal, expected_epoch=2, frame=1), 4)

        before = dict(terminal)
        before.update({0x00C: 0x400, 0x050: 1, 0x054: 0, 0x058: 0,
                       0x010: 0, 0x068: 0, 0x06C: 0, 0x070: 0, 0x074: 0})
        after_ack = dict(terminal)
        after_ack.update({0x00C: 0x400, 0x010: 0, 0x064: 0,
                          0x068: 0, 0x06C: 0, 0x070: 0, 0x074: 0})

        class FixtureRunner:
            def __init__(self):
                self.writes = []

            def snapshot(self, label, *, stable):
                if label.endswith(":before"):
                    return before
                if label.endswith(":done_safe"):
                    return terminal
                if label.endswith(":after_ack"):
                    return after_ack
                return terminal

            def parameters(self, frame, core, drain):
                return {"frame": frame, "core": core, "drain": drain}

            def event(self, kind, value):
                pass

            def write(self, offset, value):
                self.writes.append((offset, value))

        runner = FixtureRunner()
        result = flow._measure_normal_start(
            runner, frame=1, clock_profile={"hwh_clock_hz": flow.EXPECTED_PL_CLOCK_HZ})
        self.assertEqual(result["status"], "PASS_DONE_SAFE_MEASURED_ACKED")
        self.assertEqual(result["terminal"][0x00C], 0xE04)
        self.assertEqual(runner.writes, [(0x008, 1), (0x05C, 2), (0x060, 0), (0x008, 4)])

    def test_normal_start_active_phase_still_rejects_early_head_valid(self):
        snapshot = {offset: 0 for offset in flow.csr.OFFSETS}
        snapshot.update({0: 0x53324250, 4: 0x100, 0x00C: 0x201,
                        0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                        0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                        0x048: 0x01AD5E80, 0x04C: 20280,
                        0x050: 2, 0x058: 1})
        with self.assertRaisesRegex(transport.TransportError, "HEAD_VALID提前置位"):
            flow._normal_start_phase(snapshot, expected_epoch=2, frame=1)

    def test_diag_reconciles_epoch_only_after_raw_response_validation(self):
        external_epoch, prior_epoch = 17, 12
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = FakeSerial(diag_response(external_epoch))
            with (root / "rx.bin").open("w+b") as rx, (root / "tx.bin").open("w+b") as tx:
                wire = jtag.JtagWireSession(stream, rx, tx, response_timeout=1.0)
                wire.epoch = prior_epoch
                controller = FakeController()
                result = flow._manual_mode0_diag(controller, wire, external_epoch)

                self.assertEqual(wire.epoch, external_epoch)
                self.assertEqual(result["status"], "PASS_REAL_DIAG_MODE0_EPOCH_RECONCILIATION")
                self.assertEqual(result["prior_uart_epoch"], prior_epoch)
                self.assertEqual(result["response"]["meta"]["epoch"], external_epoch)
                self.assertEqual(result["response"]["raw_uart_binding"]["bytes"],
                                 transport.HEADER.size + transport.META.size)
                self.assertEqual(len(wire.receipt_attempts), 1)
                self.assertEqual(wire.receipt_attempts[0]["raw_received_hex"],
                                 diag_response(external_epoch).hex())
                self.assertEqual(stream.in_waiting, 0)
                self.assertEqual(controller.state("cpu0"), "Running")

    def test_diag_epoch_mismatch_preserves_old_wire_epoch(self):
        prior_epoch, expected_epoch = 12, 17
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = FakeSerial(diag_response(expected_epoch - 1))
            with (root / "rx.bin").open("w+b") as rx, (root / "tx.bin").open("w+b") as tx:
                wire = jtag.JtagWireSession(stream, rx, tx, response_timeout=1.0)
                wire.epoch = prior_epoch
                controller = FakeController()
                with self.assertRaises(transport.TransportError) as raised:
                    flow._manual_mode0_diag(controller, wire, expected_epoch)

                self.assertEqual(wire.epoch, prior_epoch)
                self.assertTrue(wire.failed)
                self.assertTrue(controller.failed)
                self.assertEqual(controller.state("cpu0"), "Stopped")
                self.assertEqual(wire.receipt_attempts, [])
                self.assertEqual(rx.tell(), transport.HEADER.size + transport.META.size)
                self.assertEqual(stream.in_waiting, 0)
                self.assertTrue(raised.exception.deadline_cpu_stop_cleanup["wire_epoch_unchanged"])
                self.assertEqual(controller.calls[-1], "t20.csr_deadline.cpu0.stop_after_diag_failure")

    def test_diag_bad_crc_preserves_bytes_stops_cpu_and_keeps_epoch(self):
        prior_epoch, expected_epoch = 12, 17
        response = bytearray(diag_response(expected_epoch))
        response[-1] ^= 0x01
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = FakeSerial(bytes(response))
            with (root / "rx.bin").open("w+b") as rx, (root / "tx.bin").open("w+b") as tx:
                wire = jtag.JtagWireSession(stream, rx, tx, response_timeout=1.0)
                wire.epoch = prior_epoch
                controller = FakeController()
                with self.assertRaises(transport.TransportError):
                    flow._manual_mode0_diag(controller, wire, expected_epoch)

                self.assertEqual(wire.epoch, prior_epoch)
                self.assertTrue(wire.failed)
                self.assertTrue(controller.failed)
                self.assertEqual(controller.state("cpu0"), "Stopped")
                rx.seek(0)
                self.assertEqual(rx.read(), bytes(response))
                self.assertEqual(len(wire.sent_requests), 1)
                self.assertEqual(wire.sent_requests[1][0].op, transport.OP_DIAG)
                self.assertEqual(wire.receipt_attempts, [])

    def test_diag_truncated_response_keeps_partial_raw_and_stop_failure_is_recorded(self):
        prior_epoch, expected_epoch = 12, 17
        complete = diag_response(expected_epoch)
        truncated = complete[:transport.HEADER.size + 7]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stream = FakeSerial(truncated)
            with (root / "rx.bin").open("w+b") as rx, (root / "tx.bin").open("w+b") as tx:
                wire = jtag.JtagWireSession(stream, rx, tx, response_timeout=0.02)
                wire.epoch = prior_epoch
                controller = FakeController()
                controller.stop_fails = True
                with self.assertRaises(transport.TransportError) as raised:
                    flow._manual_mode0_diag(controller, wire, expected_epoch)

                self.assertEqual(wire.epoch, prior_epoch)
                self.assertTrue(wire.failed)
                self.assertTrue(controller.failed)
                self.assertEqual(controller.state("cpu0"), "Running")
                rx.seek(0)
                self.assertEqual(rx.read(), truncated)
                cleanup = raised.exception.deadline_cpu_stop_cleanup
                self.assertEqual(cleanup["status"], "FAIL_CPU_STOP_UNCONFIRMED")
                self.assertEqual(cleanup["stop_api"], "RAISED")
                self.assertTrue(cleanup["cpu1_stopped"])
                self.assertTrue(cleanup["wire_epoch_unchanged"])
                self.assertEqual(len(wire.sent_requests), 1)

    def test_normal_measurement_unsafe_state_does_not_ack_or_start_again(self):
        class FakeRunner:
            def __init__(self):
                self.writes = []
                self.observe = self_snapshot()
                self.observe.update({0x00C: 0x406, 0x050: 1, 0x058: 1})

            def snapshot(self, label, *, stable):
                return self_snapshot() if label.endswith(":before") else self.observe

            def parameters(self, frame, core, drain):
                return self_snapshot()

            def event(self, kind, value):
                return None

            def write(self, offset, value):
                self.writes.append((offset, value))

        def self_snapshot():
            row = {offset: 0 for offset in flow.csr.OFFSETS}
            row.update({0: 0x53324250, 4: 0x100, 0x00C: 0x400,
                        0x01C: 519168, 0x020: 0x00100000, 0x024: 5903100,
                        0x028: 0xFFFFFFFF, 0x02C: 0xFFFFFFFF,
                        0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                        0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                        0x048: 0x01AD5E80, 0x04C: 20280})
            return row

        runner = FakeRunner()
        profile = {"hwh_clock_hz": flow.EXPECTED_PL_CLOCK_HZ}
        with self.assertRaises(transport.TransportError):
            flow._measure_normal_start(runner, frame=1, clock_profile=profile)
        self.assertEqual(runner.writes, [(0x008, 1)])

    def test_recovery_files_are_in_output_bindings_and_delivery_manifest(self):
        with tempfile.TemporaryDirectory(dir=flow.ROOT / "tmp") as directory:
            root = Path(directory)
            run_dir = root / "main_run"
            outputs = []
            run_dir.mkdir()
            recovery_dir = flow._fresh_run(outputs, root, "offline", "csr_deadline_sample000_recovery")
            recovery_dir.mkdir()
            (run_dir / "acceptance_result.json").write_bytes(b"{}\n")
            (recovery_dir / "started.json").write_bytes(b"started\n")
            (recovery_dir / "progress.jsonl").write_bytes(b"progress\n")
            (recovery_dir / "head13.bin").write_bytes(b"head13")

            output_bindings = flow._collect_output_bindings(outputs)
            manifest_files = flow._manifest_file_entries(run_dir, output_bindings)
            paths = {item["path"]: item["sha256"] for item in manifest_files}
            for path in recovery_dir.rglob("*"):
                if path.is_file():
                    relative = path.relative_to(flow.ROOT).as_posix()
                    self.assertEqual(paths[relative], transport.digest(path.read_bytes()))

            self.assertEqual({item["path"] for item in output_bindings},
                             {str(path) for path in recovery_dir.rglob("*") if path.is_file()})


if __name__ == "__main__":
    unittest.main()
