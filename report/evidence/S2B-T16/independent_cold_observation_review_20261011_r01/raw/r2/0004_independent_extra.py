"""R2额外独立反例：完整位覆盖、官方格式化代码与T19精确来源拒绝。"""
import ast
import copy
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from types import SimpleNamespace
import unittest

from verification import s2b_board_jtag as j
from verification import test_s2b_board_jtag as fixture
import independent_cases as prior

RUN = Path(os.environ["COLD_REVIEW_RUN"])
ROOT = RUN.parents[3]
visibility = None


def complete(word):
    """按独立逐位整除构造完整metadata，与被审位段算法分离。"""
    fields = [f"{j.EOS_NAME if bit == 4 else 'INDEPENDENT_' + str(bit)}(Bits [{bit}]):{word // (2 ** bit) % 2}"
              for bit in range(32)]
    return f"CONFIG_STATUS: {word}\n" + "\n".join(fields) + "\n"


class ParserExtra(unittest.TestCase):
    """逐位反例与官方SDK输出代码，不导入或调用真实TCF。"""
    def test_each_of_32_missing_bits_rejected_for_zero_and_allones(self):
        for word in (0, 4294967295):
            for missing in range(32):
                lines = complete(word).splitlines()
                del lines[missing + 1]
                with self.subTest(word=word, missing=missing), self.assertRaises(j.JtagError):
                    j.parse_config_status(None, "\n".join(lines) + "\n", "")

    def test_each_of_32_wrong_values_duplicate_overlap_rejected(self):
        word = 0xA5A51234
        for bit in range(32):
            lines = complete(word).splitlines()
            lines[bit + 1] = lines[bit + 1][:-1] + str(1 - (word // (2 ** bit) % 2))
            with self.subTest(bit=bit, kind="错值"), self.assertRaises(j.JtagError):
                j.parse_config_status(None, "\n".join(lines) + "\n", "")
            duplicate = complete(word) + complete(word).splitlines()[bit + 1] + "\n"
            with self.subTest(bit=bit, kind="重复范围"), self.assertRaises(j.JtagError):
                j.parse_config_status(None, duplicate, "")

    def test_wrong_eos_bit_with_complete_coverage_rejected(self):
        for wrong in (0, 3, 5, 31):
            text = complete(0).replace(j.EOS_NAME, "FORMER_EOS").replace("INDEPENDENT_" + str(wrong) + "(", j.EOS_NAME + "(")
            with self.subTest(wrong=wrong), self.assertRaises(j.JtagError):
                j.parse_config_status(None, text, "")
        for name in ("EOS", "END OF STARTUP (EOS)", "UNKNOWN", "end of startup (eos) status"):
            with self.subTest(name=name), self.assertRaises(j.JtagError):
                j.parse_config_status(None, complete(0).replace(j.EOS_NAME, name), "")

    def test_state_words_never_replace_observed_metadata(self):
        for text in ("FPGA is configured.\n", "FPGA is not configured.\n", complete(16) + "FPGA is configured.\n"):
            with self.subTest(text=text), self.assertRaises(j.JtagError):
                j.parse_config_status(None, text, "")

    def test_official_formatter_ast_native_shape_and_handchecked_values(self):
        sdk = Path("D:/Xilinx/2026.1/Vitis/cli/xsdb/target.py")
        tree = ast.parse(sdk.read_text(encoding="utf-8"))
        target = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Target")
        fpga = next(node for node in target.body if isinstance(node, ast.FunctionDef) and node.name == "fpga")
        block = next(node for node in fpga.body if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "optcnt")
        self.assertEqual((block.lineno, block.end_lineno), (4609, 4671))
        fn = ast.parse("def native_format():\n    pass\n").body[0]
        fn.body = [copy.deepcopy(block)]
        compiled = compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(sdk), "exec")
        names = ["OPAQUE_LOW"] * 4 + ["END OF STARTUP (EOS) STATUS"] + ["OPAQUE_HIGH"] * 27
        values = [0, 16, 0x80000008, 0xFFFFFFFF, 0x1A2B3C10] + [1 << bit for bit in range(32)]
        rng = random.Random(0x2B16C02)
        values.extend(rng.randrange(1 << 32) for _ in range(64))
        captures = []
        for word in values:
            data = (32, word, ",".join(names))
            calls = []
            def mocked_get_config(context):
                calls.append(context)
                return data
            env = {"optcnt": 1, "parsed_args": SimpleNamespace(config_status=True), "jtag_ctx": "INDEPENDENT_MOCK_NO_HARDWARE",
                   "tcf_xicom": SimpleNamespace(xicom_get_config_status=mocked_get_config), "exec_in_dispatch_thread": lambda fn, arg: fn(arg)}
            exec(compiled, env)
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                returned = env["native_format"]()
            parsed = j.parse_config_status(returned, stdout.getvalue(), stderr.getvalue())
            with self.subTest(word=word):
                self.assertIsNone(returned)
                self.assertEqual(calls, ["INDEPENDENT_MOCK_NO_HARDWARE"])
                self.assertEqual(parsed["status_word"], word)
                self.assertEqual(parsed["eos"], word // 16 % 2)
                self.assertEqual([row["value"] for row in parsed["fields"]], [word % 16, word // 16 % 2, word // 32])
            captures.append({"input_word": word, "stdout": stdout.getvalue(), "stderr": stderr.getvalue(), "return_type": type(returned).__name__, "parsed": parsed})
        with (RUN / "sdk_formatter_captures.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump({"scope": "官方原版格式化分支AST加明确MOCK TCF返回；未导入SDK", "sdk_path": str(sdk),
                       "sdk_sha256": hashlib.sha256(sdk.read_bytes()).hexdigest(), "line_start": block.lineno,
                       "line_end": block.end_lineno, "random_seed": 0x2B16C02, "count": len(captures), "captures": captures}, stream, ensure_ascii=False, indent=2)
            stream.write("\n")

    def test_old_git_pin_changed_bytes_and_actual_path_rejected(self):
        fx = visibility.PreflightTests()
        fx.setUp()
        captures = []
        try:
            fx.check()
            baseline = "6d3fd8567b579a51d4042667d47af7d94f2f5a97"
            old = subprocess.check_output(["git", "show", baseline + ":verification/s2b_board_jtag.py"], cwd=ROOT)
            self.assertEqual(hashlib.sha256(old).hexdigest(), "91bbf5bc8ac5ef9bee37ce6491627a6ac8f38a53b7bba113d1b83447b2ecddf0")
            current = Path(j.__file__).read_bytes()
            for name, blob, message in (("old_git", old, "固定T16候选精确版本"),
                                        ("drift", current + b"\n", "固定T16候选精确版本"),
                                        ("same_bytes_wrong_path", current, "实际运行来源未绑定")):
                path = fx.directory / (name + ".py")
                with path.open("xb") as stream:
                    stream.write(blob)
                fx.cfg["bindings"]["tool_source"] = visibility.bind(path)
                with self.subTest(name=name), self.assertRaises(visibility.p.VisibilityProbeError) as cm:
                    fx.check()
                captures.append({"case": name, "sha256": hashlib.sha256(blob).hexdigest(), "error": str(cm.exception)})
                self.assertIn(message, str(cm.exception))
            self.assertNotIn("xsdb", sys.modules)
            self.assertNotIn("serial", sys.modules)
        finally:
            fx.tearDown()
        with (RUN / "independent_pin_results.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump({"scope": "明确UNIT fixture，未创建实际runtime兼容批准", "cases": captures}, stream, ensure_ascii=False, indent=2)
            stream.write("\n")


class ControllerExtra(unittest.TestCase):
    """使用R1独立raw捕获封装，只借用基础mock会话。"""
    setUp = prior.IndependentCases.setUp
    tearDown = prior.IndependentCases.tearDown
    reset = prior.IndependentCases.reset
    rejected = prior.IndependentCases.rejected

    def test_deploy_without_system_stop_does_no_download(self):
        self.controller.select_and_gate()
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected()
        self.assertFalse(self.session.operations)

    def test_reset_raw_eos1_rejects_before_init(self):
        self.session.raw["after_reset"] = (complete(16), "", None)
        with self.assertRaises(j.JtagError):
            self.reset()
        self.rejected()
        self.assertFalse(any(row[0] == "dow" for row in self.session.operations))

    def test_postbit_full_metadata_eos0_rejects_before_app(self):
        self.reset()
        self.session.raw["after_bit"] = (complete(0), "", None)
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected(initialized=True)
        self.assertTrue(self.session.full_bit)
        self.assertEqual(len([row for row in self.session.operations if row[0] == "dow"]), 1)

    def test_missing31_postbit_preserves_raw_and_actual_init(self):
        self.reset()
        text = complete(16).rsplit("\n", 2)[0] + "\n"
        self.session.raw["after_bit"] = (text, "", None)
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected(initialized=True)
        row = next(row for row in self.controller.record["calls"] if row["api"] == "fpga.config_status.after_full_bit")
        self.assertEqual((row["stdout"], row["stderr"], row["return_type"]), (text, "", "NoneType"))


def ddrc_case(mode):
    """每个模式生成独立控制器，避免复用已失败状态。"""
    def test(self):
        self.reset()
        self.session.memory[0xF8006054] = 0x125A0000 | mode
        with self.assertRaises(j.JtagError):
            self.controller.deploy()
        self.rejected(initialized=True)
        self.assertFalse(self.session.full_bit)
        self.assertEqual(self.controller.record["ddrc_observation"]["word"], 0x125A0000 | mode)
        self.assertEqual(len([row for row in self.session.operations if row[0] == "dow"]), 1)
    return test


for mode in (0, 2, 3, 4, 5, 6, 7):
    setattr(ControllerExtra, "test_ddrc_mode_" + str(mode) + "_blocks_bit_and_app", ddrc_case(mode))
