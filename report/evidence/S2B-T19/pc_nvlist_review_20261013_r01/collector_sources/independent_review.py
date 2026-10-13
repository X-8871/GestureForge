"""独立审查：仅调用官方函数的AST提取件和离线夹具，不导入真实SDK。"""
import ast
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).absolute().parents[4]
HERE = Path(__file__).absolute().parent
OUT = ROOT / "report/evidence/S2B-T19/pc_nvlist_review_20261013_r01"
if len(sys.argv) > 1:
    OUT = OUT / sys.argv[1]
    OUT.mkdir()
sys.path.insert(0, str(ROOT))
SOURCES = ["verification/s2b_board_jtag.py", "verification/test_s2b_board_jtag.py",
           "vitis/run_s2b_visibility_probe.py", "verification/test_s2b_visibility_probe.py"]
SDK = Path(r"D:\Xilinx\2026.1\Vitis\cli\xsdb\target.py")
BASELINE = "6019ed956f0008c4a97b42dc9e0aebb74f31f5c5"

def digest(path):
    """读取真实字节计算绑定，不修改输入。"""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name, value):
    """独占创建审查原件，避免覆盖已有Run。"""
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

before = {name: digest(ROOT / name) for name in SOURCES}
tree = ast.parse(SDK.read_text(encoding="utf-8"))
target = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Target")
function = next(node for node in target.body if isinstance(node, ast.FunctionDef) and node.name == "__print_regs")
function.name = "sdk_print_regs"
module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
scope = {}
exec(compile(module, str(SDK), "exec"), scope)
sdk_print_regs = scope["sdk_print_regs"]

from verification import test_s2b_board_jtag as fixture
from verification import test_s2b_visibility_probe as probe_fixture

class Context:
    """最小寄存器上下文，字段独立于被测helper。"""
    def __init__(self, value, error=None):
        self.value, self.error = value, error
    def get_context_data(self): return self
    def getName(self): return "pc"
    def getMemoryAddress(self): return None
    def getBitNumbers(self): return None
    def getSize(self): return 4
    def get_reg_value(self): return self.value
    def get_reg_error(self): return self.error

class IndependentCases(unittest.TestCase):
    """使用官方原函数建立独立返回语义依据。"""
    def test_official_ast_values_and_errors(self):
        for raw, error, expected in ((0, None, 0), (0xFFFFFF34, None, 0xFFFFFF34),
                                     (0xFFFFFFFF, None, 0xFFFFFFFF), (None, "native unavailable", "N/A"),
                                     (None, None, "")):
            with self.subTest(raw=raw, error=error):
                self.assertEqual(sdk_print_regs(None, {}, {1: Context(raw, error)}, {"nvlist": 1}), {"pc": expected})

    def test_official_ast_pc_with_async_output(self):
        case = fixture.JtagTests()
        case.setUp()
        try:
            case.controller.select_and_gate()
            def read(*args, reg):
                self.assertEqual((args, reg), (("--nvlist",), "pc"))
                print("Info: ARM Cortex-A9 MPCore #1 Stopped at 0xffffff34 (Suspended)")
                print("原始非结构化诊断", file=sys.stderr)
                return sdk_print_regs(None, {}, {1: Context(0xFFFFFF34)}, {"nvlist": 1})
            case.session.objects[12].rrd = read
            case.controller.system_reset_stop(case.bindings["interface"])
            self.assertEqual(case.controller.record["system_reset"]["after"]["cpu1_pc"], 0xFFFFFF34)
            self.assertIn("Suspended", case.controller.record["calls"][-2]["stdout"])
            self.assertIn("原始非结构化诊断", case.controller.record["calls"][-2]["stderr"])
        finally:
            case.tearDown()

    def test_official_ast_na_locks_before_reset(self):
        case = fixture.JtagTests()
        case.setUp()
        try:
            case.controller.select_and_gate()
            case.session.objects[12].rrd = lambda *args, reg: sdk_print_regs(None, {}, {1: Context(None, "unavailable")}, {"nvlist": 1})
            with self.assertRaisesRegex(fixture.j.JtagError, "PC结构化"):
                case.controller.system_reset_stop(case.bindings["interface"])
            self.assertTrue(case.controller.failed)
            self.assertEqual(case.session.operations, [])
        finally:
            case.tearDown()

fixtures = HERE / ("fixtures_" + sys.argv[1] if len(sys.argv) > 1 else "fixtures")
fixtures.mkdir()
original_temp = tempfile.TemporaryDirectory
def isolated_temp(*args, **kwargs):
    """所有回归临时写入限定在本次审查目录。"""
    kwargs["dir"] = str(fixtures)
    return original_temp(*args, **kwargs)

started = time.monotonic()
metadata = {"baseline": BASELINE, "source_sha256": before, "sdk_target_path": str(SDK),
            "sdk_target_sha256": digest(SDK), "python_version": sys.version,
            "python_sha256": digest(sys.executable), "command": [sys.executable, "-X", "utf8", "-B", str(Path(__file__).absolute())] + sys.argv[1:],
            "cwd": str(ROOT), "actual_hardware_calls": 0, "run_count": 1, "peak_memory_bytes": None,
            "scope": "G2_SOFTWARE_PC_NVLIST_ONLY", "fixture_directory": str(fixtures)}
save("run_metadata_before.json", metadata)
suite = unittest.TestSuite()
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentCases))
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(fixture))
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(probe_fixture))
with patch.object(tempfile, "TemporaryDirectory", isolated_temp):
    with (OUT / "unittest.log").open("x", encoding="utf-8", newline="\n") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
after = {name: digest(ROOT / name) for name in SOURCES}
status = "PASS" if result.wasSuccessful() and before == after else "CHANGES_REQUIRED"
metadata.update(status=status, exit_code=0 if status == "PASS" else 1,
                elapsed_seconds=time.monotonic() - started, tests_run=result.testsRun,
                failures=len(result.failures), errors=len(result.errors), after_source_sha256=after,
                log_sha256=digest(OUT / "unittest.log"), limitations=["未连接或操作真实板卡；不代表G3/G4/G5。", "峰值内存未测。", "已冻结生产源码仅只读；官方SDK仅AST函数，无模块执行。"])
save("run_result.json", metadata)
print(json.dumps({key: metadata[key] for key in ("status", "tests_run", "failures", "errors", "elapsed_seconds", "exit_code")}, ensure_ascii=False))
sys.exit(metadata["exit_code"])
