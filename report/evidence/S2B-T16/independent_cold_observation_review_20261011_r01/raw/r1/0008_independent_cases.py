"""独立软件审查反例；所有mock与日志仅在本轮隔离目录。"""
import json
import os
from pathlib import Path
import sys
import unittest

from verification import s2b_board_jtag as j
from verification import test_s2b_board_jtag as f

RUN = Path(os.environ["COLD_REVIEW_RUN"])


class RawTarget(f.FakeTarget):
    """独立控制原生stdout、stderr与返回值，不复用Developer目标包装。"""
    def fpga(self, *args, **kwargs):
        if args == ("--config_status",):
            self.session.operations.append(("config_status", args))
            phase = "after_bit" if self.session.full_bit else "after_reset"
            out, err, result = self.session.raw[phase]
            print(out, end="")
            print(err, end="", file=sys.stderr)
            if isinstance(result, BaseException):
                raise result
            return result
        self.session.full_bit = True
        return super().fpga(*args, **kwargs)

    def mrd(self, *args, **kwargs):
        if kwargs["address"] == 0xF8006054:
            self.session.operations.append(("ddrc_mode", kwargs["address"]))
        return super().mrd(*args, **kwargs)


class IndependentCases(unittest.TestCase):
    """独立构造错误与运行顺序；保持人工关闭条件和原始调用。"""
    def setUp(self):
        f.JtagTests.setUp(self)
        self.session.objects = {row["target_id"]: RawTarget(self.session, row) for row in self.session.rows.values()}
        self.session.full_bit = False
        self.session.raw = {
            "after_reset": ("CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n", "", None),
            "after_bit": ("CONFIG_STATUS: 16\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n", "", None),
        }

    def tearDown(self):
        self.controller.close()
        capture = RUN / "independent_raw" / self._testMethodName
        capture.mkdir(parents=True, exist_ok=False)
        for path in self.run.iterdir():
            if path.is_file():
                (capture / path.name).write_bytes(path.read_bytes())
        (capture / "operations.json").write_text(json.dumps(self.session.operations, ensure_ascii=False, default=repr, indent=2) + "\n", encoding="utf-8")
        self.temp.cleanup()

    def reset(self):
        self.controller.select_and_gate()
        self.controller.system_reset_stop(self.bindings["interface"])

    def rejected(self, initialized=False):
        self.assertTrue(self.controller.failed)
        self.assertEqual(self.controller.initialized, initialized)
        self.assertFalse(self.controller.configured)
        self.assertFalse(self.controller.app_running)
        self.assertFalse(self.session.objects[11].running)
        self.assertFalse(self.session.objects[12].running)
        self.assertEqual(set(self.session._bptable), {1})
        operations = list(self.session.operations)
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.assertEqual(operations, self.session.operations)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])

    def test_signed_large_and_noncanonical_decimal_rejected(self):
        for word in ("+0", "-0", "00", "016", " 0", "0 ", "4294967296", "9" * 4000, "1e1", "16.0", "0x10"):
            with self.subTest(word=word), self.assertRaises((j.JtagError, ValueError)):
                j.parse_config_status(None, "CONFIG_STATUS: " + word + "\nEND OF STARTUP (EOS) STATUS(Bits [4]):0\n", "")

    def test_field_number_name_width_overlap_and_duplicate_rejected(self):
        rows = [
            "END OF STARTUP (EOS) STATUS(Bits [04]):0",
            "END OF STARTUP (EOS) STATUS(Bits [+4]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):+0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):00",
            "END OF STARTUP (EOS) STATUS(Bits [31]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4:3]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):2",
            "END OF STARTUP (EOS) STATUS(Bits [4]):1",
            "END OF STARTUP (EOS) STATUS(Bits [4]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):0\nMETA(Bits [31:0]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):0\nMETA(Bits [32]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):0\nMETA(Bits [0:3]):0",
            "END OF STARTUP (EOS) STATUS(Bits [4]):0\nMETA(Bits [1]):0\nMETA(Bits [1]):0",
            "unknown(Bits [4]):0", "FPGA is not configured.", "",
        ]
        for row in rows:
            with self.subTest(row=row), self.assertRaises(j.JtagError):
                j.parse_config_status(None, "CONFIG_STATUS: 0\n" + row + "\n", "")

    def test_max_u32_and_exact_eos_bit_independent_handcalculation(self):
        raw = "CONFIG_STATUS: 4294967295\nLOW(Bits [3:0]):15\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\nUPPER(Bits [31:5]):134217727\n"
        value = j.parse_config_status(None, raw, "")
        self.assertEqual(value["status_word"], 0xFFFFFFFF)
        self.assertEqual(value["eos"], 1)
        self.assertEqual(len(value["fields"]), 3)

    def test_truncated_metadata_must_not_be_accepted(self):
        for word, eos in ((0, 0), (16, 1)):
            with self.subTest(word=word), self.assertRaises(j.JtagError):
                j.parse_config_status(None, f"CONFIG_STATUS: {word}\nEND OF STARTUP (EOS) STATUS(Bits [4]):{eos}\n", "")

    def test_hole_in_metadata_must_not_be_accepted(self):
        raw = "CONFIG_STATUS: 16\nLOW(Bits [2:0]):0\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\nUPPER(Bits [31:5]):0\n"
        with self.assertRaises(j.JtagError):
            j.parse_config_status(None, raw, "")

    def test_returned_value_and_stderr_block_reset_downloads(self):
        self.session.raw["after_reset"] = (self.session.raw["after_reset"][0], "warning", 0)
        with self.assertRaises(j.JtagError):
            self.reset()
        self.rejected()
        self.assertFalse(self.session.full_bit)
        self.assertFalse(any(row[0] == "dow" for row in self.session.operations))
        row = self.controller.record["calls"][-1]
        self.assertEqual((row["return_repr"], row["stderr"]), ("0", "warning"))

    def test_ddrc_powerdown_fail_latches_after_actual_init(self):
        self.reset()
        self.session.memory[0xF8006054] = 0x80000002
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected(initialized=True)
        self.assertFalse(self.session.full_bit)
        self.assertEqual(self.controller.record["ddrc_observation"]["operating_mode"], 2)

    def test_postbit_rawstatus_mismatch_blocks_app_and_retains_outputs(self):
        self.reset()
        self.session.raw["after_bit"] = ("CONFIG_STATUS: 0\nEND OF STARTUP (EOS) STATUS(Bits [4]):1\n", "", None)
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected(initialized=True)
        self.assertTrue(self.session.full_bit)
        self.assertEqual(len([row for row in self.session.operations if row[0] == "dow"]), 1)
        row = next(row for row in self.controller.record["calls"] if row["api"] == "fpga.config_status.after_full_bit")
        self.assertEqual(row["stdout"], self.session.raw["after_bit"][0])

    def test_actual_download_failure_preserves_confirmed_configuration(self):
        self.reset()
        original = self.session.objects[11].dow
        def fail_app(**kwargs):
            if kwargs["file"] == self.bindings["app_elf"]["path"]:
                raise RuntimeError("独立app下载失败")
            return original(**kwargs)
        self.session.objects[11].dow = fail_app
        with self.assertRaises(RuntimeError):
            self.controller.deploy()
        self.assertTrue(self.controller.failed)
        self.assertTrue(self.controller.initialized)
        self.assertTrue(self.controller.configured)
        self.assertFalse(self.controller.app_running)
        self.assertEqual(set(self.session._bptable), {1})
        self.assertFalse(self.session.objects[12].running)

    def test_exact_order_statusfacts_and_cpu1_static(self):
        self.reset()
        self.session.memory[0xF8006054] = 0xFFFFFFF9
        self.controller.deploy()
        self.assertEqual([row[0] for row in self.session.operations], ["rst", "config_status", "dow", "con", "ddrc_mode", "fpga", "config_status", "dow", "con"])
        self.assertEqual(self.controller.record["ddrc_observation"]["operating_mode"], 1)
        self.assertTrue(self.controller.initialized and self.controller.configured and self.controller.app_running)
        self.assertFalse(self.controller.record["cold_lifecycle_proven"])
        self.assertFalse(self.session.objects[12].running)


if __name__ == "__main__":
    unittest.main()
