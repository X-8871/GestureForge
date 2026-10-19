"""离线核验CPU BRESP host的分类门禁，不连接SDK、JTAG或UART。"""

from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
import hashlib
import json
from unittest import mock

try:
    from . import s2b_cpu_bresp_experiment as host
except ImportError:
    import s2b_cpu_bresp_experiment as host


def accepted_mailbox() -> list[int]:
    """构造只用于隔离单测的合成mailbox。"""
    words = [0] * 64
    words[0] = host.MAGIC_SLVERR
    words[14] = host.STATE_RUN | host.OWNER_PL | host.AXI_PENDING
    words[15] = 0
    words[16] = 7
    words[17] = 2
    words[18] = 0
    words[19] = 0x1888
    words[22] = 0xC344
    words[23] = 0xE5801000
    words[24] = host.CSR_BASE + 8
    words[25] = host.STATE_RUN | host.OWNER_PL | host.AXI_PENDING
    words[26] = 7
    words[27] = 2
    words[28] = 0
    words[29] = 1
    words[30] = 3
    return words


def snapshot(status: int) -> dict[int, int]:
    """构造符合既有CSR ABI的隔离快照。"""
    values = {offset: 0 for offset in host.csr.OFFSETS}
    values.update({0: 0x53324250, 4: 0x100, 0x00C: status,
                   0x01C: 519168, 0x020: 0x00100000, 0x024: 5903100,
                   0x030: 0x10000000, 0x034: 0x02000000, 0x038: 0x01000000,
                   0x03C: 0x01ADADB8, 0x040: 0x01A46100, 0x044: 5070,
                   0x048: 0x01AD5E80, 0x04C: 20280, 0x050: 5, 0x058: 1})
    return values


class FakeTarget:
    """只模拟CPU0的原生下载、继续和寄存器读取接口。"""
    def __init__(self, owner):
        self.owner = owner

    def dow(self, *, file, auto_stop, set_entry):
        self.owner.operations.append(("dow", file, auto_stop, set_entry))
        self.owner.cpu0_pc = 0xC020 if "bresp" in file else 0x100000

    def con(self, *args, **kwargs):
        self.owner.operations.append(("con", args, kwargs))
        self.owner.snapshot = snapshot(0xC04)
        self.owner.snapshot[0x050] = 6
        self.owner.snapshot[0x058] = 0

    def rrd(self, *args, **kwargs):
        return {"cpsr": 0}


class FakeController:
    """模拟现成控制器表面，所有调用只写入Python列表。"""
    def __init__(self, run):
        self.run = run
        self.targets = {"cpu0": FakeTarget(self), "cpu1": FakeTarget(self)}
        self.bindings = {"app_elf": {"path": "fake-infer.elf", "sha256": host.APP_ELF_SHA256}}
        self.cpu0_pc = 0x100100
        self.snapshot = snapshot(0x400)
        self.operations = []
        self.record = {"calls": [], "readbacks": []}

    def verify_bindings(self):
        return None

    def gate(self, both=True):
        return None

    def state(self, label):
        return "Stopped: (Suspended)"

    def pc(self, label="cpu0"):
        return 0xFFFFFF34 if label == "cpu1" else self.cpu0_pc

    def stable_csr(self, label):
        return self.snapshot

    def words(self, address, count):
        if address == 0xF8000910:
            return [0x18]
        if address == host.MAILBOX_BASE:
            if count != 64:
                raise AssertionError("mailbox只读取64个ABI字，不能用fake隐藏生产长度错误")
            return accepted_mailbox()
        if address == 0x100010:
            return [0x13121110, 0x17161514, 0x1B1A1918, 0x1F1E1D1C][:count]
        if address == 0x100000:
            return [0x03020100, 0x07060504, 0x0B0A0908, 0x0F0E0D0C][:count]
        return [0] * count

    def call(self, name, function, *args, **kwargs):
        self.record["calls"].append({"api": name})
        return function(*args, **kwargs)

    def fail_stop(self):
        self.operations.append(("fail_stop",))


class CpuBrespExperimentTests(unittest.TestCase):
    """检查纯函数严格区分预期BRESP和不确定现场。"""

    def test_exact_synchronous_external_write_is_slverr(self):
        result = host.classify_mailbox(accepted_mailbox(), 0xC344)
        self.assertEqual(result["classification"], "SLVERR")

    def test_unknown_abort_magic_does_not_become_slverr(self):
        words = accepted_mailbox()
        words[0] = host.MAGIC_UNKNOWN
        self.assertEqual(host.classify_mailbox(words, 0xC344)["classification"], "UNKNOWN")

    def test_wrong_opcode_is_unknown(self):
        words = accepted_mailbox()
        words[23] ^= 4
        self.assertEqual(host.classify_mailbox(words, 0xC344)["classification"], "UNKNOWN")

    def test_decerr_is_unknown(self):
        words = accepted_mailbox()
        words[19] &= ~(1 << 12)
        self.assertEqual(host.classify_mailbox(words, 0xC344)["classification"], "UNKNOWN")

    def test_epoch_change_is_unknown(self):
        words = accepted_mailbox()
        words[26] += 1
        self.assertEqual(host.classify_mailbox(words, 0xC344)["classification"], "UNKNOWN")

    def test_bad_mailbox_shape_is_rejected(self):
        with self.assertRaises(host.CpuBrespExperimentError):
            host.classify_mailbox([0] * 63, 0xC344)

    def test_frozen_r05_layout_is_readable_offline(self):
        path = host.DIAG_DIR / "s2b_bresp_diag.elf"
        layout, _ = host._diag_static_layout({"path": str(path), "sha256": host.DIAG_ELF_SHA256})
        self.assertEqual(layout["entry"], 0xC020)
        self.assertEqual(layout["busy_store_pc"], 0xC344)

    def test_r08_real_result_provenance_offline(self):
        path = host.ROOT / "report" / "evidence" / "S2B-T18" / \
            "formal_csr_recovery_20261019_r08" / "acceptance_result.json"
        raw = path.read_bytes()
        result = json.loads(raw.decode("utf-8"))
        binding = {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
        recovery_dir = Path(result["stages"][-1]["evidence_dir"])
        recovery = json.loads((recovery_dir / "csr_result.json").read_text(encoding="utf-8"))
        provenance = host._validate_r08_result(binding, recovery["admission"]["deployment_bindings"])
        self.assertEqual(provenance["ack_api"], "t20.wire.abort.explicit_ack")
        self.assertEqual(provenance["golden_epoch"], 5)
        self.assertEqual(provenance["golden_frame"], 1)

    def test_fake_execute_waits_for_safe_then_reloads_app_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            evidence_parent = root / "report" / "evidence" / "S2B-T20"
            run = evidence_parent / "fake_cpu_bresp"
            run.mkdir(parents=True)
            app_raw = bytes(range(64))
            app_elf = {"entry": 0x100000,
                       "programs": [{"type": 1, "flags": 1, "offset": 0, "file_size": 64,
                                     "memory_size": 64, "virtual": 0x100000, "physical": 0x100000}],
                       "sections": [{"flags": 4, "type": 1, "size": 64, "address": 0x100000,
                                     "offset": 0, "name": ".text"}]}
            controller = FakeController(run)
            original_root = host.ROOT
            try:
                with (mock.patch.object(host, "ROOT", root),
                      mock.patch.object(host.jtag, "JtagController", FakeController),
                      mock.patch.object(host.jtag, "bound_bytes", return_value=app_raw),
                      mock.patch.object(host, "parse_elf", return_value=app_elf),
                      mock.patch.object(host, "_diag_layout", return_value={
                          "path": "s2b_bresp_diag.elf", "sha256": host.DIAG_ELF_SHA256,
                          "entry": 0xC020, "busy_store_pc": 0xC344,
                          "loads": [], "mailbox": [host.MAILBOX_BASE, host.MAILBOX_BASE + host.MAILBOX_BYTES]}),
                      mock.patch.object(host, "_validate_r08_result", return_value={"r08": "bound", "golden_epoch": 5, "golden_frame": 1})):
                    controller.cpu0_pc = 0x100010
                    result = host.execute_cpu_bresp_experiment(
                        controller, {"path": "r08.json", "sha256": "0" * 64},
                        {"path": "diag.elf", "sha256": host.DIAG_ELF_SHA256},
                        {"path": "review.json", "sha256": "1" * 64}, run)
                    result_exists = (run / "cpu_bresp_result.json").is_file()
            finally:
                host.ROOT = original_root
        self.assertEqual(result["status"], "SAFE_TERMINAL_APP_RELOADED_AT_ENTRY")
        self.assertTrue(result["recovery_ready"])
        self.assertEqual([row[0] for row in controller.operations], ["dow", "con", "dow"])
        self.assertEqual(controller.cpu0_pc, app_elf["entry"])
        self.assertFalse(any(row[0] in ("ack", "reset", "retry") for row in controller.operations))
        self.assertTrue(result_exists)


if __name__ == "__main__":
    unittest.main()
