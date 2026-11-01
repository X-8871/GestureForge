"""静态核验 T57 attempt05 的 XSim plusarg 写法与运行时目录绑定。"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUN_ROOT = "D:/FPGA_Competition/report/evidence/S2A-T57/run09/attempt05"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class Attempt05BindingTests(unittest.TestCase):
    """检查 property 安全设置、实际命令门禁和 TB 文件路径来源。"""

    def test_property_value_is_passed_explicitly_and_cannot_be_parsed_as_option(self) -> None:
        no_wave = _read("sim/s2a_t57_no_wave.tcl")
        self.assertIn('set t57_xsim_options "-testplusarg $t57_testplusarg"', no_wave)
        self.assertRegex(
            no_wave,
            r"(?m)^set_property -name \{xsim\.simulate\.xsim\.more_options\} "
            r"-value \$t57_xsim_options -objects \$t57_simset$",
        )
        self.assertNotRegex(
            no_wave,
            r"(?m)^set_property xsim\.simulate\.xsim\.more_options\s+\$t57_xsim_options",
        )
        self.assertIn("get_property xsim.simulate.xsim.more_options $t57_simset", no_wave)

    def test_runtime_xsim_signature_requires_one_exact_attempt05_plusarg(self) -> None:
        runner_path = ROOT / "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py"
        spec = importlib.util.spec_from_file_location("t57_attempt05_runner_test", runner_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        expected = f"T57_RUN_ROOT={EXPECTED_RUN_ROOT}"
        correct = (
            f"{module.TOP}_behav -key Behavioral:{module.SIMSET}:Functional:{module.TOP} "
            f"-tclbatch {EXPECTED_RUN_ROOT}/xsim_run.tcl -testplusarg {expected}"
        )
        self.assertEqual(module._option_values(correct, "-testplusarg"), [expected])
        self.assertEqual(
            module._option_values(correct + f" -testplusarg {expected}", "-testplusarg"),
            [expected, expected],
        )
        wrong = correct.replace("attempt05", "attempt04")
        self.assertNotEqual(
            module._option_values(wrong, "-testplusarg"), [expected],
        )

        runner = runner_path.read_text(encoding="utf-8")
        self.assertIn('RUN_ROOT = EVIDENCE_ROOT / "run09" / "attempt05"', runner)
        self.assertIn('testplusarg_values = _option_values(simulate, "-testplusarg")', runner)
        self.assertIn("testplusarg_values == [expected_testplusarg]", runner)
        self.assertIn('"verification/test_s2a_t57_attempt05_binding.py",', runner)

    def test_project_tcl_wrapper_and_tb_share_attempt05_root(self) -> None:
        project_tcl = _read("report/evidence/S2A-T57/run_project_sim.tcl")
        self.assertIn("run09\\attempt05", project_tcl)
        self.assertIn("set testplusarg_values [t57_option_values $simulate_command -testplusarg]", project_tcl)
        self.assertIn('set expected_testplusarg "T57_RUN_ROOT=$expected_run_root"', project_tcl)
        self.assertIn("[llength $testplusarg_values] != 1", project_tcl)
        self.assertIn("[lindex $testplusarg_values 0] ne $expected_testplusarg", project_tcl)

        wrapper = _read("verification/run_s2a_t57_project_sim.ps1")
        self.assertIn('run09\\attempt05', wrapper)
        self.assertIn('"verification/test_s2a_t57_attempt05_binding.py",', wrapper)
        self.assertIn('$testplusargMatches.Count -ne 1', wrapper)
        self.assertIn('$testplusargValue, $expectedRunRootArgument', wrapper)

        testbench = _read("sim/tb_s2a_conv_layer35_row21_all_channels.sv")
        self.assertIn(f'T57_EXPECTED_RUN_ROOT = "{EXPECTED_RUN_ROOT}"', testbench)
        self.assertIn('$value$plusargs("T57_RUN_ROOT=%s", t57_run_root)', testbench)
        self.assertIn("if (t57_run_root != T57_EXPECTED_RUN_ROOT)", testbench)
        self.assertNotIn("attempt02", testbench)
        self.assertNotIn("attempt03", testbench)
        self.assertNotIn("attempt04", testbench)

        expected_paths = {
            "feature_input_path": ("fixture/feature_input.bin", "rb"),
            "weight_input_path": ("fixture/layer35_weights.bin", "rb"),
            "golden_input_path": ("fixture/golden.bin", "rb"),
            "vectors_input_path": ("fixture/vectors.txt", "r"),
            "raw_output_path": ("observed_raw.bin", "wb"),
            "int8_output_path": ("observed_output.bin", "wb"),
        }
        for variable, (suffix, mode) in expected_paths.items():
            self.assertIn(
                f'{variable} = $sformatf("%s/{suffix}", t57_run_root);',
                testbench,
            )
            self.assertRegex(testbench, rf'\$fopen\({variable},\s*"{re.escape(mode)}"\)')
        fopen_arguments = re.findall(r'\$fopen\(([^,]+),\s*"([^"]+)"\)', testbench)
        self.assertEqual(
            set(fopen_arguments),
            {(variable, mode) for variable, (_, mode) in expected_paths.items()},
        )


if __name__ == "__main__":
    unittest.main()
