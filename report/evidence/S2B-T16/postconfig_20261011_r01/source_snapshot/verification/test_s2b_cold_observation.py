"""统一初始化观测的独立离线反例；不导入SDK或打开串口。"""

import ast
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile

from verification import s2b_board_jtag as j
from verification import test_s2b_board_jtag as fixture


class ObservedTarget(fixture.FakeTarget):
    """使用实际SDK None/stdout接口形状，单独控制前后两次观测。"""
    def fpga(self, *args, **kwargs):
        if args == ("--config_status",):
            self.session.operations.append(("fpga", args, kwargs))
            phase = "bit" if self.session.bit_attempted else "reset"
            out, err, value = self.session.outputs[phase]
            print(out, end="")
            print(err, end="", file=sys.stderr)
            if isinstance(value, BaseException):
                raise value
            return value
        self.session.bit_attempted = True
        return super().fpga(*args, **kwargs)

    def mrd(self, *args, **kwargs):
        if kwargs["address"] == j.DDRC_MODE_STATUS:
            self.session.operations.append(("ddrc_read", kwargs["address"]))
        return super().mrd(*args, **kwargs)


class ColdObservationTests(unittest.TestCase):
    """只借用ELF及会话夹具，每个场景独立验证门禁与失败锁止。"""
    def setUp(self):
        fixture.JtagTests.setUp(self)
        self.session.objects = {row["target_id"]: ObservedTarget(self.session, row) for row in self.session.rows.values()}
        self.session.outputs = {
            "reset": ("CONFIG_STATUS: 0\nMOCK_LOWER(Bits [3:0]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nMOCK_UPPER(Bits [31:5]):0\n", "", None),
            "bit": ("CONFIG_STATUS: 16\nMOCK_LOWER(Bits [3:0]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\nMOCK_UPPER(Bits [31:5]):0\n", "", None)}
        self.session.bit_attempted = False

    def tearDown(self):
        fixture.JtagTests.tearDown(self)

    def ready(self):
        fixture.JtagTests.ready(self)

    def assert_failed_locked(self, initialized=False):
        self.assertTrue(self.controller.failed)
        self.assertEqual(self.controller.initialized, initialized)
        self.assertFalse(self.controller.configured)
        self.assertFalse(self.controller.app_running)
        self.assertFalse(self.session.objects[11].running)
        self.assertEqual(set(self.session._bptable), {1})
        before = list(self.session.operations)
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.assertEqual(before, self.session.operations)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])

    def test_reset_eos1_blocks_all_downloads(self):
        self.session.outputs["reset"] = self.session.outputs["bit"]
        with self.assertRaises(j.JtagError): self.ready()
        self.assert_failed_locked()
        self.assertFalse(any(row[0] == "dow" for row in self.session.operations))
        self.assertIn("system_reset", self.controller.record)
        self.assertEqual(self.controller.record["configuration_observations"][0]["eos"], 1)

    def test_reset_unknown_metadata_blocks_all_downloads(self):
        self.session.outputs["reset"] = (self.session.outputs["reset"][0].replace(j.EOS_NAME, "MOCK_UNKNOWN"), "", None)
        with self.assertRaises(j.JtagError): self.ready()
        self.assert_failed_locked()
        self.assertFalse(self.session.bit_attempted)
        self.assertFalse(any(row[0] == "dow" for row in self.session.operations))

    def test_post_bit_eos0_blocks_app_and_preserves_init(self):
        self.ready()
        self.session.outputs["bit"] = self.session.outputs["reset"]
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assert_failed_locked(initialized=True)
        self.assertTrue(self.session.bit_attempted)
        self.assertEqual(len([row for row in self.session.operations if row[0] == "dow"]), 1)
        self.assertEqual(self.controller.record["initialization"]["return_code"], 0)
        self.assertEqual(self.controller.record["ddrc_observation"]["operating_mode"], 1)

    def test_post_bit_native_exception_retained_and_blocks_app(self):
        self.ready()
        self.session.outputs["bit"] = ("partial output\n", "native diagnostic\n", RuntimeError("native status failure"))
        with self.assertRaises(RuntimeError): self.controller.deploy()
        self.assert_failed_locked(initialized=True)
        call = next(row for row in self.controller.record["calls"] if row["api"] == "fpga.config_status.after_full_bit")
        self.assertEqual((call["stdout"], call["stderr"], call["status"]), ("partial output\n", "native diagnostic\n", "RAISED"))

    def test_ddrc_each_nonnormal_mode_blocks_bit_app_and_cleans_bps(self):
        self.ready()
        # 每个子场景重新构造控制器，防止复用已失败对象。
        for mode in (0, 2, 3, 4, 5, 6, 7):
            with self.subTest(mode=mode):
                if mode != 0:
                    self.tearDown(); self.setUp(); self.ready()
                self.session.memory[j.DDRC_MODE_STATUS] = 0x12345000 | mode
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assert_failed_locked(initialized=True)
                self.assertFalse(self.session.bit_attempted)
                self.assertEqual(self.controller.record["ddrc_observation"]["word"], 0x12345000 | mode)
                self.assertEqual(self.controller.record["ddrc_observation"]["status"], "FAILED")

    def test_normal_fullword_and_exact_native_order(self):
        self.ready()
        self.session.memory[j.DDRC_MODE_STATUS] = 0x12345001
        self.controller.deploy()
        self.assertEqual([row[0] for row in self.session.operations],
                         ["rst", "fpga", "dow", "con", "ddrc_read", "fpga", "fpga"] + ["postconfig_mwr"] * 4 + ["dow", "con"])
        self.assertEqual(self.controller.record["ddrc_observation"]["word_hex"], "0x12345001")
        self.assertEqual([row["eos"] for row in self.controller.record["configuration_observations"]], [0, 1])
        self.assertTrue(self.controller.initialized and self.controller.configured and self.controller.app_running)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])
        self.controller.close()
        calls = [json.loads(row) for row in (self.run / "jtag_calls.jsonl").read_text(encoding="utf-8").splitlines()]
        eos_calls = [row for row in calls if row["api"].startswith("fpga.config_status.")]
        self.assertEqual(len(eos_calls), 2)
        self.assertTrue(all(row["return_type"] == "NoneType" and row["stdout"] for row in eos_calls))

    def test_parse_independent_complete_sdk_shape(self):
        text = ("CONFIG_STATUS: 439041040\n"  # 独立十六进制原字0x1A2B3C10。
                "         MOCK_LOWER(Bits [3:0]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n"
                "         MOCK_UPPER(Bits [31:5]):13720032\n")
        result = j.parse_config_status(None, text, "")
        self.assertEqual(result["status_word_hex"], "0x1A2B3C10")
        self.assertEqual(result["eos"], 1)

    def test_parse_rejects_eos_only_metadata(self):
        for word, eos in ((0, 0), (16, 1)):
            text = f"CONFIG_STATUS: {word}\nEND OF STARTUP (EOS) STATUS(Bits [4]):{eos}\n"
            with self.subTest(word=word), self.assertRaisesRegex(j.JtagError, "未完整覆盖"):
                j.parse_config_status(None, text, "")

    def test_parse_rejects_missing_bit3_or_high31(self):
        for phase in ("reset", "bit"):
            complete = self.session.outputs[phase][0]
            for original, missing in (("[3:0]", "[2:0]"), ("[31:5]", "[30:5]")):
                with self.subTest(phase=phase, missing=missing), self.assertRaisesRegex(j.JtagError, "未完整覆盖"):
                    j.parse_config_status(None, complete.replace(original, missing), "")

    def test_parse_rejects_complete_overlapping_or_conflicting_metadata(self):
        text = self.session.outputs["bit"][0]
        invalid = (
            (text + "MOCK_DUPLICATE(Bits [3]):0\n", "重叠"),
            (text.replace("[31:5]):0", "[31:4]):1"), "重叠"),
            (text.replace("[3:0]):0", "[3:0]):1"), "原字不一致"),
            (text.replace("[31:5]):0", "[31:5]):1"), "原字不一致"),
            (text.replace("[4]):1", "[4]):0"), "原字不一致"),
            (text.replace("[3:0]):0", "[3:0]):16"), "位宽"))
        for raw, reason in invalid:
            with self.subTest(raw=raw), self.assertRaisesRegex(j.JtagError, reason):
                j.parse_config_status(None, raw, "")

    def test_parse_accepts_fullword_bounds_and_unknown_non_eos_fields(self):
        # 独立手算低四位、EOS和高27位，未知非EOS字段允许改名和重排。
        for word, low, eos, high in ((0, 0, 0, 0), (4294967295, 15, 1, 134217727),
                                     (2147483656, 8, 0, 67108864)):
            raw = (f"CONFIG_STATUS: {word}\nMOCK_FUTURE_FIELD(Bits [31:5]):{high}\n"
                   f"END OF STARTUP (EOS) STATUS(Bits [4]):{eos}\nMOCK_OTHER_FIELD(Bits [3:0]):{low}\n")
            with self.subTest(word=word):
                result = j.parse_config_status(None, raw, "")
                self.assertEqual((result["status_word"], result["eos"]), (word, eos))
                self.assertEqual(len(result["fields"]), 3)

    def test_parse_rejects_replacement_eos_name_with_complete_metadata(self):
        for name in ("EOS", "END OF STARTUP (EOS)", "end of startup (eos) status", "MOCK_UNKNOWN"):
            with self.subTest(name=name), self.assertRaisesRegex(j.JtagError, "唯一EOS"):
                j.parse_config_status(None, self.session.outputs["reset"][0].replace(j.EOS_NAME, name), "")

    def test_truncated_or_hole_metadata_blocks_reset_downloads(self):
        for index, kind in enumerate(("eos_only", "bit3", "bit31")):
            with self.subTest(kind=kind):
                if index:
                    self.tearDown(); self.setUp()
                raw = self.session.outputs["reset"][0]
                raw = ("CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n" if kind == "eos_only"
                       else raw.replace("[3:0]", "[2:0]") if kind == "bit3" else raw.replace("[31:5]", "[30:5]"))
                self.session.outputs["reset"] = (raw, "", None)
                with self.assertRaisesRegex(j.JtagError, "未完整覆盖"):
                    self.ready()
                self.assert_failed_locked()
                self.assertFalse(self.session.objects[12].running)
                self.assertFalse(any(row[0] == "dow" for row in self.session.operations))
                call = next(row for row in self.controller.record["calls"] if row["api"] == "fpga.config_status.after_system_reset")
                self.assertEqual((call["stdout"], call["stderr"], call["return_type"]), (raw, "", "NoneType"))

    def test_truncated_or_hole_metadata_blocks_post_bit_app(self):
        for index, kind in enumerate(("eos_only", "bit3", "bit31")):
            with self.subTest(kind=kind):
                if index:
                    self.tearDown(); self.setUp()
                self.ready()
                raw = self.session.outputs["bit"][0]
                raw = ("CONFIG_STATUS: 16\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n" if kind == "eos_only"
                       else raw.replace("[3:0]", "[2:0]") if kind == "bit3" else raw.replace("[31:5]", "[30:5]"))
                self.session.outputs["bit"] = (raw, "", None)
                with self.assertRaisesRegex(j.JtagError, "未完整覆盖"):
                    self.controller.deploy()
                self.assert_failed_locked(initialized=True)
                self.assertFalse(self.session.objects[12].running)
                self.assertTrue(self.session.bit_attempted)
                self.assertEqual(len([row for row in self.session.operations if row[0] == "dow"]), 1)
                self.assertEqual(self.controller.record["initialization"]["return_code"], 0)
                self.assertEqual(self.controller.record["ddrc_observation"]["operating_mode"], 1)
                call = next(row for row in self.controller.record["calls"] if row["api"] == "fpga.config_status.after_full_bit")
                self.assertEqual((call["stdout"], call["stderr"], call["return_type"]), (raw, "", "NoneType"))

    def test_parse_rejects_missing_duplicate_wrong_bit_width_raw_mismatch_and_unknown(self):
        invalid = (
            "CONFIG_STATUS: 0\n", "FPGA is not configured.\n",
            "CONFIG_STATUS: 0\nOTHER(Bits [4]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [5]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [5:4]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):2\n",
            "CONFIG_STATUS: 16\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n",
            "CONFIG_STATUS: -1\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n",
            "CONFIG_STATUS: 4294967296\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n",
            "CONFIG_STATUS: 0x0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nunknown warning\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nOTHER(Bits [5:3]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nOTHER(Bits [32]):0\n",
            "CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\nOTHER(Bits [2:3]):0\n")
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(j.JtagError):
                j.parse_config_status(None, text, "")

    def test_parse_rejects_return_and_stderr_type_errors(self):
        text = self.session.outputs["reset"][0]
        for value, stdout, stderr in ((False, text, ""), (0, text, ""), ({}, text, ""),
                                      (None, text, "warning"), (None, text.encode(), ""), (None, text, None)):
            with self.subTest(value=value, stderr=stderr), self.assertRaises(j.JtagError):
                j.parse_config_status(value, stdout, stderr)

    def test_fresh_import_has_no_sdk_or_serial_dependency(self):
        script = ("import sys; import verification.s2b_board_jtag; "
                  "assert not any(name == 'serial' or name.startswith(('xsdb', 'vitis', 'tcf')) for name in sys.modules)")
        completed = subprocess.run([sys.executable, "-B", "-c", script], cwd=Path(j.__file__).resolve().parents[1],
                                   capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        tree = ast.parse(Path(j.__file__).read_text(encoding="utf-8"))
        self.assertFalse(any(isinstance(node, ast.Constant) and node.value == "--state" for node in ast.walk(tree)))


class PostconfigTests(unittest.TestCase):
    """独立手算四动作、原生异常及清理边界；不导入SDK、不操作板卡。"""
    def setUp(self):
        fixture.JtagTests.setUp(self)

    def tearDown(self):
        fixture.JtagTests.tearDown(self)

    def ready(self):
        fixture.JtagTests.ready(self)

    def fresh(self):
        self.tearDown(); self.setUp(); self.ready()

    def assert_blocked(self):
        self.assertTrue(self.controller.failed)
        self.assertFalse(self.controller.postconfigured or self.controller.app_running)
        self.assertFalse(self.session.objects[11].running or self.session.objects[12].running)
        self.assertEqual(set(self.session._bptable), {1})
        self.assertFalse(any(row[0] == "dow" and Path(row[2]).name == "app_elf" for row in self.session.operations))
        self.assertFalse(any(row[0] == "con" and not row[2] for row in self.session.operations))
        before = copy.deepcopy(self.session.operations)
        with self.assertRaises(j.JtagError): self.controller.deploy()
        self.assertEqual(before, self.session.operations)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])

    def test_four_actual_writes_full_reset_and_preserved_upper_level_bits(self):
        self.ready(); self.controller.deploy()
        operations = [row for row in self.session.operations if row[0] == "postconfig_mwr"]
        self.assertEqual([(row[2], row[5]) for row in operations],
                         [(0xF8000008, [0xDF0D]), (0xF8000900, [0x1234000F]), (0xF8000240, [0]), (0xF8000004, [0x767B])])
        self.assertTrue(all(row[1] == ("--bypass_cache_synq",) and row[3:5] == (1, 4) for row in operations))
        observation = self.controller.record["postconfiguration"]
        self.assertEqual(observation["before"], {"locksta": 1, "level_shifter": 0x12340000, "fpga_reset": 0xFFFFFFFF})
        self.assertEqual(observation["silicon"], {"address": 0xF8007080, "word": 0x21234567, "nibble": 2, "branch": "3_0"})
        self.assertEqual([row["label"] for row in observation["clock_observations"]], ["before_unlock", "after_lock"])
        self.assertEqual(observation["status"], "PASS")
        calls = self.controller.record["calls"]
        eos = next(i for i, row in enumerate(calls) if row["api"] == "fpga.config_status.after_full_bit")
        writes = [i for i, row in enumerate(calls) if row["api"].startswith("apu.mwr.postconfig.")]
        app = next(i for i, row in enumerate(calls) if row["api"] == "cpu0.dow.app")
        csr = [i for i, row in enumerate(calls) if row["api"] == "apu.mrd" and row["kwargs"]["address"] == 0x43C0000C]
        self.assertTrue(eos < min(writes) < max(writes) < min(csr) < max(csr) < app)
        self.assertEqual(len(csr), 2)
        self.assertFalse(any(row["kwargs"].get("address") in (0xF8000004, 0xF8000008) for row in calls if row["api"] == "apu.mrd"))

    def test_revision_all_generated_branches_and_raw_low_bits(self):
        self.ready()
        for index, (nibble, branch) in enumerate(((0, "1_0"), (1, "2_0"), (2, "3_0"), (15, "3_0"))):
            with self.subTest(nibble=nibble):
                if index: self.fresh()
                raw = (nibble << 28) | 0x1234567
                self.session.memory[0xF8007080] = raw
                self.controller.deploy()
                self.assertEqual(self.controller.record["postconfiguration"]["silicon"],
                                 {"address": 0xF8007080, "word": raw, "nibble": nibble, "branch": branch})

    def test_initial_lock_clock_pll_and_revision_type_fail_before_unlock(self):
        self.ready()
        cases = ((0xF800000C, 0), (0xF8000170, 0x00600610), (0xF8000170, 0x00700600),
                 (0xF800010C, 0), (0xF800010C, 1), (0xF800010C, 3), (0xF800010C, 6),
                 (0xF8007080, True), (0xF8007080, "0x2"), (0xF8007080, -1), (0xF8007080, 1 << 32))
        for index, (address, raw) in enumerate(cases):
            with self.subTest(address=address, raw=raw):
                if index: self.fresh()
                self.session.memory[address] = raw
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assert_blocked()
                self.assertFalse(any(row[0] == "postconfig_mwr" for row in self.session.operations))

    def test_locksta_and_complete_rmw_readbacks_reject_and_relock(self):
        self.ready()
        for index, fault in enumerate(("unlock", "level", "reset", "lock")):
            with self.subTest(fault=fault):
                if index: self.fresh()
                apu = self.session.objects[10]; original = apu.mwr
                def wrong(*args, **kwargs):
                    address = kwargs["address"]
                    original(*args, **kwargs)
                    if address == {"unlock": 0xF8000008, "level": 0xF8000900, "reset": 0xF8000240, "lock": 0xF8000004}[fault]:
                        self.session.memory[0xF800000C if fault in ("unlock", "lock") else address] = (1 if fault == "unlock" else 0 if fault == "lock" else 0x1235000F if fault == "level" else 0x100)
                apu.mwr = wrong
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assert_blocked()
                cleanup = self.controller.record["postconfiguration"]["cleanup"][0]
                self.assertEqual(cleanup["status"], "ALREADY_LOCKED" if fault == "unlock" else "FAILED" if fault == "lock" else "RELOCKED")
                writes = [row for row in self.session.operations if row[0] == "postconfig_mwr"]
                self.assertEqual(sum(row[2] == 0xF8000008 for row in writes), 1)

    def test_cold_csr_identity_abi_state_ledger_and_stability(self):
        self.ready()
        for index, (offset, value) in enumerate(((0, 0), (4, 0x101), (0xC, 0x102), (0x10, 1), (0x50, 1), (0x54, 1), (0x58, 1), (0x68, 1))):
            with self.subTest(offset=offset):
                if index: self.fresh()
                self.session.memory[0x43C00000 + offset] = value
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assert_blocked()
                self.assertEqual(self.session.memory[0xF800000C], 1)
                self.assertEqual(self.controller.record["postconfiguration"]["cleanup"][0]["status"], "ALREADY_LOCKED")
        self.fresh()
        original = self.session.objects[10].mrd
        def unstable(*args, **kwargs):
            value = original(*args, **kwargs)
            if kwargs["address"] == 0x43C0000C:
                self.session.memory[0x43C00074] += 1
            return value
        self.session.memory[0x43C00074] = 0
        self.session.objects[10].mrd = unstable
        with self.assertRaisesRegex(j.JtagError, "正在变化"): self.controller.deploy()
        self.assert_blocked()

    def test_every_postconfig_native_call_exception_locks_and_keeps_original(self):
        self.ready(); self.controller.deploy()
        calls = self.controller.record["calls"]
        begin = next(i for i, row in enumerate(calls) if row["api"] == "fpga.config_status.after_full_bit") + 1
        end = next(i for i, row in enumerate(calls) if row["api"] == "cpu0.dow.app") - 4
        # 覆盖所有动态身份/状态/BOOT/寄存器/四写/两CSR调用，不采样跳过中间步骤。
        for offset in range(end - begin):
            with self.subTest(offset=offset, api=calls[begin + offset]["api"]):
                self.fresh()
                original = self.controller.call; count = 0
                def throwing(name, function, *args, **kwargs):
                    nonlocal count
                    if "postconfiguration" in self.controller.record and self.controller.record["postconfiguration"]["status"] == "IN_PROGRESS":
                        current = count; count += 1
                        if current == offset:
                            def native_failure(*args, **kwargs):
                                raise RuntimeError("独立逐调用异常 " + str(offset))
                            return original(name, native_failure, *args, **kwargs)
                    return original(name, function, *args, **kwargs)
                self.controller.call = throwing
                with self.assertRaisesRegex(RuntimeError, "独立逐调用异常"): self.controller.deploy()
                self.assert_blocked()
                self.assertIn("独立逐调用异常", self.controller.record["error"])
                self.assertLessEqual(sum(row[0] == "postconfig_mwr" and row[2] == 0xF8000008 for row in self.session.operations), 1)

    def test_midsequence_peer_target_boot_cpu_or_file_drift_blocks_cleanup_write(self):
        self.ready()
        for index, fault in enumerate(("peer", "target", "boot", "cpu0", "cpu1", "file")):
            with self.subTest(fault=fault):
                if index: self.fresh()
                apu = self.session.objects[10]; original = apu.mwr
                def mutate(*args, **kwargs):
                    original(*args, **kwargs)
                    if kwargs["address"] == 0xF8000008:
                        if fault == "peer": self.session._curchan_obj.remote_peer.attrs["Port"] = "3122"
                        if fault == "target": self.session.rows["cpu0"]["target_ctx"] = "changed"
                        if fault == "boot": self.session.memory[0xF800025C] = 1
                        if fault in ("cpu0", "cpu1"): self.session.objects[11 if fault == "cpu0" else 12].running = True
                        if fault == "file": Path(self.bindings["bit"]["path"]).write_bytes("独立漂移".encode("utf-8"))
                apu.mwr = mutate
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assertTrue(self.controller.failed)
                self.assertFalse(self.controller.app_running)
                writes = [row for row in self.session.operations if row[0] == "postconfig_mwr"]
                self.assertEqual([(row[2], row[5]) for row in writes], [(0xF8000008, [0xDF0D])])
                self.assertEqual(self.controller.record["postconfiguration"]["cleanup"][0]["status"], "FAILED")
                self.assertTrue(self.controller.record["cleanup_errors"])
                self.assertFalse(any(row[0] == "con" and not row[2] for row in self.session.operations))

    def test_exception_after_unlock_side_effect_relocks_but_preserves_original_and_cleanup_failure(self):
        self.ready()
        for index, cleanup_fail in enumerate((False, True)):
            with self.subTest(cleanup_fail=cleanup_fail):
                if index: self.fresh()
                apu = self.session.objects[10]; original = apu.mwr
                def throws(*args, **kwargs):
                    address = kwargs["address"]
                    original(*args, **kwargs)
                    if address == 0xF8000008: raise RuntimeError("原解锁部分成功异常")
                    if cleanup_fail and address == 0xF8000004: raise RuntimeError("重锁清理异常")
                apu.mwr = throws
                with self.assertRaisesRegex(RuntimeError, "原解锁部分成功异常"): self.controller.deploy()
                self.assert_blocked()
                cleanup = self.controller.record["postconfiguration"]["cleanup"][0]
                self.assertEqual(cleanup["status"], "FAILED" if cleanup_fail else "RELOCKED")
                self.assertIn("原解锁部分成功异常", self.controller.record["error"])
                if cleanup_fail: self.assertIn("重锁清理异常", self.controller.record["cleanup_errors"][0])

    def test_generated_xsa_tables_header_and_hwh_drift_rejected_before_init(self):
        raw = fixture.xsa_bytes()
        self.assertEqual(j.postconfig_basis(raw)["tables"]["1_0"]["clock"][2:], (0x03F03F30, 0x00600600))
        for member, before, after in (("ps7_init.c", b"0xFFFFFFFFU", b"0x0000000FU"),
                                       ("ps7_init.c", b"0xDF0DU", b"0xDF0CU"),
                                       ("ps7_init.c", b"0x00600600U", b"0x00600500U"),
                                       ("ps7_init.c", b"ps7_post_config_2_0[]", b"ps7_post_config_1_0[]"),
                                       ("ps7_init.c", b"0xF0000000", b"0xE0000000"),
                                       ("ps7_init.h", b"VERSION_2 1", b"VERSION_2 2"),
                                       ("unit.hwh", b'50000000', b'100000000'),
                                       ("unit.hwh", b'cold_resetn', b'resetn')):
            with self.subTest(member=member, before=before):
                self.fresh()
                output = io.BytesIO()
                with zipfile.ZipFile(io.BytesIO(raw)) as source, zipfile.ZipFile(output, "w") as changed:
                    for name in source.namelist():
                        data = source.read(name)
                        changed.writestr(name, data.replace(before, after) if name == member else data)
                path = Path(self.bindings["xsa"]["path"])
                path.write_bytes(output.getvalue())
                # 固定新fixture字节后重建控制器，使错误来自生成语义而非SHA漂移。
                self.controller.close(); self.run = self.directory / ("run_" + hashlib.sha256(output.getvalue()).hexdigest()[:8]); self.run.mkdir()
                self.bindings["xsa"]["sha256"] = hashlib.sha256(output.getvalue()).hexdigest()
                self.controller = j.JtagController(self.session, self.bindings, self.run); self.ready()
                with self.assertRaises(j.JtagError): self.controller.deploy()
                self.assert_blocked()
                self.assertFalse(any(row[0] == "dow" for row in self.session.operations))


if __name__ == "__main__":
    unittest.main()
