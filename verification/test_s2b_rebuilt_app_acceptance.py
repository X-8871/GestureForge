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

    def test_execute_accepts_runid_deployment_and_reaches_first_hardware_gate(self):
        """用真实controller/wire类型穿过execute目录门禁，在任何硬件方法前停止。"""
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
            controller.select_and_gate = mock.Mock(side_effect=StopBeforeHardware("test boundary"))
            controller.fail_stop = mock.Mock()
            wire_stream = io.BytesIO()
            with (temp_root / "uart_rx.bin").open("w+b") as rx_file, \
                    (temp_root / "uart_tx.bin").open("w+b") as tx_file:
                wire = jtag.JtagWireSession(wire_stream, rx_file, tx_file)
                completed = subprocess.CompletedProcess(["git", "rev-parse", "HEAD"], 0,
                                                        stdout="0" * 40 + "\n", stderr="")
                with mock.patch.object(acceptance, "ROOT", temp_root), \
                        mock.patch.object(acceptance, "verify_recovery_inputs", return_value=recovery), \
                        mock.patch.object(acceptance.subprocess, "run", return_value=completed):
                    result = acceptance.execute(controller, wire, run_id=run_id,
                        source_sha256=acceptance.EXPECTED_SOURCE_SHA256, cold_basis={})

            self.assertEqual(result["status"], "FAILED_REBUILT_APP_ACCEPTANCE")
            self.assertIn("test boundary", result["error"])
            controller.select_and_gate.assert_called_once_with()
            controller.fail_stop.assert_called_once_with()
            self.assertTrue((run_dir / "rebuilt_app_acceptance_result.json").is_file())


if __name__ == "__main__":
    unittest.main()
