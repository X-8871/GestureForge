"""重建app验收入口的离线绑定及准入单测，不操作硬件。"""
import unittest
import json
import hashlib
import io
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
from unittest import mock

from verification import s2b_rebuilt_app_acceptance as acceptance
from verification import s2b_board_jtag as jtag
from vitis import run_s2b_rebuilt_app_acceptance as production_runner


def safe_idle_snapshot():
    """按冻结寄存器表构造独立的PS安全空闲快照。"""
    row = {key: 0 for key in (0, 4) + tuple(range(0x00C, 0x078, 4))}
    row.update({0: 0x53324250, 4: 0x100, 0x00C: 0x400,
                0x01C: 519168, 0x020: 0x100000, 0x024: 5903100,
                0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                0x048: 0x01AD5E80, 0x04C: 20280})
    return row


class RebuiltAppAcceptanceTests(unittest.TestCase):
    """验证独立恢复scope的离线输入绑定及现场安全条件。"""

    class EntryController:
        """只模拟入口预检所需的XSDB返回，不访问设备。"""
        def __init__(self, states, pcs, snapshot=None, config_fields=None, eos=0):
            self.session = SimpleNamespace(targets=object())
            self.targets = {name: SimpleNamespace(stop=object()) for name in ("cpu0", "cpu1")}
            self.states = dict(states)
            self.pcs = dict(pcs)
            self.snapshot = safe_idle_snapshot() if snapshot is None else snapshot
            self.config_fields = config_fields or {
                "END OF STARTUP (EOS) STATUS": 0, "DONE INTERNAL SIGNAL STATUS": 0,
                "DONE PIN": 0, "GWE STATUS": 0, "GTS_CFG_B STATUS": 0,
                "CFG STARTUP STATE MACHINE PHASE": 0}
            self.eos = eos
            self.cpu0_touched = False
            self.record = {"configuration_observations": []}
            self.calls = []
            self.selected = None

        def verify_bindings(self):
            self.calls.append(("verify_bindings",))

        def call(self, name, function, *args, **kwargs):
            self.calls.append((name, args, kwargs))
            if name == "session.targets.properties.entry_preflight":
                return {"sdk_target_rows": True}
            if name.endswith(".stop.entry_preflight"):
                label = "cpu0" if name.startswith("cpu0.") else "cpu1"
                self.states[label] = "Stopped: (Suspended)"
                return None
            return None

        def refresh_targets(self, selected):
            self.selected = selected

        def state(self, label):
            return self.states[label]

        def pc(self, label="cpu0"):
            return self.pcs[label]

        def gate(self, both=True):
            if both:
                self.assert_stopped()

        def assert_stopped(self):
            if not all(value.startswith("Stopped") for value in self.states.values()):
                raise RuntimeError("fake gate: CPU未停止")

        def words(self, address, count):
            self.assert_stopped()
            return [0]

        def observe_config_status(self, phase, expected_eos):
            row = {"phase": phase, "status": "PASS" if self.eos == expected_eos else "FAILED",
                   "eos": self.eos,
                   "fields": [{"name": name, "value": value}
                              for name, value in self.config_fields.items()]}
            self.record["configuration_observations"].append(row)

        def stable_csr(self, label):
            self.assert_stopped()
            return self.snapshot

    @staticmethod
    def csr_map_for(controller):
        owner = {}
        helper = SimpleNamespace(register_csr_debug_map=mock.Mock(
            side_effect=lambda _cfg, _rec, _journal, _session, _controller, actual_owner:
                actual_owner.update(attempted=True)))
        return (helper, {"sdk_files": {}}, {"cleanup_errors": []}, controller.session, owner), owner

    def call_preflight(self, controller, csr_map):
        with mock.patch.object(acceptance.jtag, "validate_targets", return_value={"validated": True}):
            return acceptance._preflight_entry(controller, csr_map, journal=object())

    def test_entry_preflight_stops_running_cpu1_and_admits_bootrom_without_csr(self):
        controller = self.EntryController({"cpu0": "Stopped: (Suspended)", "cpu1": "Running"},
            {"cpu0": 0xFFFFFF28, "cpu1": 0xFFFFFF34})
        csr_map, owner = self.csr_map_for(controller)
        entry = self.call_preflight(controller, csr_map)
        self.assertEqual(entry["kind"], "bootrom")
        self.assertEqual(entry["evidence"]["status"], "PRE_RESET_BOOTROM_PL_UNCONFIGURED")
        self.assertEqual(entry["evidence"]["csr_read"], "NOT_READ_CSR_ABSENT")
        self.assertFalse(entry["csr_map_registered"])
        self.assertFalse(owner.get("attempted", False))
        self.assertTrue(any(call[0] == "cpu1.stop.entry_preflight" for call in controller.calls))
        self.assertTrue(all(value.startswith("Stopped") for value in controller.states.values()))

    def test_entry_preflight_rejects_bootrom_pc_when_eos_is_not_zero(self):
        controller = self.EntryController({"cpu0": "Stopped", "cpu1": "Stopped"},
            {"cpu0": 0xFFFFFF28, "cpu1": 0xFFFFFF34}, eos=1)
        csr_map, owner = self.csr_map_for(controller)
        with self.assertRaises(acceptance.RebuiltAppAcceptanceError):
            self.call_preflight(controller, csr_map)
        self.assertFalse(owner.get("attempted", False))

    def test_entry_preflight_rejects_unconfigured_bootrom_fields_even_at_eos_zero(self):
        fields = {"END OF STARTUP (EOS) STATUS": 0, "DONE INTERNAL SIGNAL STATUS": 1,
                  "DONE PIN": 0, "GWE STATUS": 0, "GTS_CFG_B STATUS": 0,
                  "CFG STARTUP STATE MACHINE PHASE": 0}
        controller = self.EntryController({"cpu0": "Stopped", "cpu1": "Stopped"},
            {"cpu0": 0xFFFFFF28, "cpu1": 0xFFFFFF34}, config_fields=fields)
        csr_map, owner = self.csr_map_for(controller)
        with self.assertRaises(acceptance.RebuiltAppAcceptanceError):
            self.call_preflight(controller, csr_map)
        self.assertFalse(owner.get("attempted", False))

    def test_entry_preflight_registers_map_and_rejects_unsafe_2b_csr(self):
        snapshot = safe_idle_snapshot()
        snapshot[0x068] = 1
        controller = self.EntryController({"cpu0": "Stopped", "cpu1": "Stopped"},
            {"cpu0": 0x100100, "cpu1": 0x100200}, snapshot=snapshot)
        csr_map, owner = self.csr_map_for(controller)
        with self.assertRaises(acceptance.csr.CsrAcceptanceError):
            self.call_preflight(controller, csr_map)
        self.assertTrue(owner.get("attempted"))
        csr_map[0].register_csr_debug_map.assert_called_once()

    def test_real_sample_runner_creates_its_directory_once(self):
        """使用真实验收器和文件系统，捕获预先建目录造成的重复创建。"""
        with tempfile.TemporaryDirectory(prefix="s2b_rebuilt_sample_") as temporary:
            run_dir = Path(temporary)
            wire = object()
            runner = acceptance._create_sample_runner(wire, run_dir, {"scope": "OFFLINE_ONLY"})
            try:
                self.assertEqual(runner.run, run_dir / "sample000")
                self.assertIs(runner.wire, wire)
                self.assertTrue((runner.run / "started.json").is_file())
                self.assertTrue(runner.capture_wire_receipts)
            finally:
                runner.log.close()

    def test_real_recovery_inputs_are_bound_without_claiming_board_or_old_g0(self):
        result = acceptance.verify_recovery_inputs()
        self.assertEqual(result["scope"], "OFFLINE_INPUTS_VERIFIED_ONLY_NOT_G0_OR_BOARD_ACCEPTANCE")
        self.assertEqual(result["new_app_elf"]["sha256"], acceptance.EXPECTED_NEW_APP_SHA256)
        self.assertEqual(result["new_app_elf"]["path"], str(acceptance.NEW_APP))
        self.assertNotEqual(result["new_app_elf"]["sha256"], result["original_r04_app_elf"]["sha256"])
        self.assertEqual(result["application_source"]["sha256"], acceptance.EXPECTED_SOURCE_SHA256)
        self.assertEqual(result["recovery_bundle"]["sha256"], acceptance.EXPECTED_BUNDLE_SHA256)

    def test_safe_idle_snapshot_admits_current_epoch_and_zero_ledger(self):
        result = acceptance.validate_pre_reset_snapshot(safe_idle_snapshot())
        self.assertEqual(result["owner"], "PS")
        self.assertEqual(result["epoch_before_system_reset"], 0)
        self.assertEqual(result["ledger"], {"pending": 0, "issued": 0, "completed": 0, "fault_detail": 0})

    def test_nonzero_pending_ledger_is_refused(self):
        snapshot = safe_idle_snapshot()
        snapshot[0x068] = 1
        with self.assertRaises(acceptance.csr.CsrAcceptanceError):
            acceptance.validate_pre_reset_snapshot(snapshot)

    def test_running_or_non_ps_status_is_refused(self):
        snapshot = safe_idle_snapshot()
        snapshot[0x00C] = 0x401
        with self.assertRaises(acceptance.csr.CsrAcceptanceError):
            acceptance.validate_pre_reset_snapshot(snapshot)

    def test_old_g0_elf_config_is_rejected_before_production_runtime(self):
        original = acceptance.ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r10_deployment/input_config.json"
        prior = json.loads(Path(original).read_text(encoding="utf-8"))
        config = {key: prior[key] for key in production_runner.CONFIG_KEYS}
        config["run_id"] = "rebuilt_app_acceptance_offline_fixture"
        config["source_commit"] = production_runner._current_commit()
        with self.assertRaises(production_runner.RebuiltAppRunnerError):
            production_runner.validate_config(config)

    def test_independent_config_accepts_only_rebuilt_elf_with_current_file_hashes(self):
        original = acceptance.ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r10_deployment/input_config.json"
        prior = json.loads(Path(original).read_text(encoding="utf-8"))
        config = {key: prior[key] for key in production_runner.CONFIG_KEYS}
        config["run_id"] = "rebuilt_app_acceptance_offline_fixture"
        config["source_commit"] = production_runner._current_commit()
        config["bindings"]["app_elf"] = {"path": str(acceptance.NEW_APP),
                                            "sha256": acceptance.EXPECTED_NEW_APP_SHA256}
        for item in config["bindings"].values():
            item["sha256"] = hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest()
        result = production_runner.validate_config(config)
        self.assertEqual(result["scope"], "REBUILT_APP_SINGLE_SAMPLE_AND_DDR256B_PROBE")
        self.assertEqual(result["old_g0_receipt"], "NOT_REUSED")
        self.assertEqual(result["new_app_elf"]["sha256"], acceptance.EXPECTED_NEW_APP_SHA256)

    def test_execute_requires_real_production_controller_and_uart_types(self):
        class NoHardware:
            """被拒绝的占位对象，故意没有任何设备方法。"""
            pass

        result = acceptance.execute(NoHardware(), NoHardware(), run_id="offline_fixture",
                                    source_sha256=acceptance.EXPECTED_SOURCE_SHA256,
                                    cold_basis={})
        self.assertEqual(result["status"], "FAILED_REBUILT_APP_ACCEPTANCE")
        self.assertIn("必须注入生产JtagController及JtagWireSession对象", result["error"])

    def test_wrapper_dispatches_positive_runid_deployment_directory_to_execute(self):
        run_id = "rebuilt_app_acceptance_wrapper_fixture"
        with tempfile.TemporaryDirectory(prefix="s2b_rebuilt_app_") as temporary:
            run_dir = Path(temporary) / run_id
            deployment_dir = run_dir / "deployment"
            deployment_dir.mkdir(parents=True)
            controller = SimpleNamespace(run=deployment_dir)
            wire = object()
            captured = {}

            def execute_mock(actual_controller, actual_wire, **kwargs):
                captured.update(controller=actual_controller, wire=actual_wire, **kwargs)
                return {"status": "MOCK_DISPATCH_ONLY"}

            result = production_runner._execute_acceptance(
                execute_mock, controller, wire, run_dir=run_dir, run_id=run_id,
                source_sha256=acceptance.EXPECTED_SOURCE_SHA256, cold_basis={"test": True},
                journal=None, csr_map=None)

        self.assertEqual(result["status"], "MOCK_DISPATCH_ONLY")
        self.assertIs(captured["controller"], controller)
        self.assertIs(captured["wire"], wire)
        self.assertEqual(captured["run_id"], run_id)
        self.assertEqual(controller.run.name, "deployment")
        self.assertEqual(controller.run.parent.name, run_id)

    def test_execute_accepts_runid_deployment_and_reaches_entry_preflight(self):
        """用真实controller/wire类型穿过execute目录门禁，在入口预检硬件动作前停止。"""
        original = acceptance.ROOT / "report/evidence/S2B-T18/formal_csr_recovery_20261019_r10_deployment/input_config.json"
        prior = json.loads(Path(original).read_text(encoding="utf-8"))
        bindings = prior["bindings"]
        bindings["app_elf"] = {"path": str(acceptance.NEW_APP), "sha256": acceptance.EXPECTED_NEW_APP_SHA256}
        for item in bindings.values():
            item["sha256"] = hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest()
        recovery = acceptance.verify_recovery_inputs()
        run_id = "rebuilt_app_acceptance_execute_fixture"

        class StopBeforeHardware(RuntimeError):
            pass

        with tempfile.TemporaryDirectory(prefix="s2b_execute_path_") as temporary:
            temp_root = Path(temporary)
            run_dir = temp_root / "report" / "evidence" / "S2B-T18" / run_id / "deployment"
            run_dir.mkdir(parents=True)
            controller = object.__new__(jtag.JtagController)
            controller.run = run_dir
            controller.bindings = bindings
            controller.binding_identity = json.dumps(bindings, ensure_ascii=False, sort_keys=True)
            controller.initialized = controller.configured = controller.app_running = controller.failed = False
            controller.log = io.StringIO()
            controller.fail_stop = mock.Mock()
            wire_stream = io.BytesIO()
            with (temp_root / "uart_rx.bin").open("w+b") as rx_file, \
                    (temp_root / "uart_tx.bin").open("w+b") as tx_file:
                wire = jtag.JtagWireSession(wire_stream, rx_file, tx_file)
                completed = subprocess.CompletedProcess(["git", "rev-parse", "HEAD"], 0,
                                                        stdout="0" * 40 + "\n", stderr="")
                with mock.patch.object(acceptance, "ROOT", temp_root), \
                        mock.patch.object(acceptance, "verify_recovery_inputs", return_value=recovery), \
                        mock.patch.object(acceptance.subprocess, "run", return_value=completed), \
                        mock.patch.object(acceptance, "_preflight_entry",
                                          side_effect=StopBeforeHardware("test boundary")) as entry_preflight:
                    result = acceptance.execute(controller, wire, run_id=run_id,
                        source_sha256=acceptance.EXPECTED_SOURCE_SHA256, cold_basis={})

            self.assertEqual(result["status"], "FAILED_REBUILT_APP_ACCEPTANCE")
            self.assertIn("test boundary", result["error"])
            entry_preflight.assert_called_once_with(controller, None, None)
            controller.fail_stop.assert_called_once_with()
            self.assertTrue((run_dir / "rebuilt_app_acceptance_result.json").is_file())


if __name__ == "__main__":
    unittest.main()
