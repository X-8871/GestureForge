"""静态验证 T57 attempt04 的仿真命令与 testbench 文件根目录绑定。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUN_ROOT = "D:/FPGA_Competition/report/evidence/S2A-T57/run09/attempt04"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class Attempt04BindingTests(unittest.TestCase):
    """确保 attempt04 的唯一输出目录经 Tcl 命令传到 testbench。"""

    def test_testbench_requires_exact_runtime_root_and_never_mentions_old_attempt(self) -> None:
        testbench = _read("sim/tb_s2a_conv_layer35_row21_all_channels.sv")
        self.assertIn(f'T57_EXPECTED_RUN_ROOT = "{EXPECTED_RUN_ROOT}"', testbench)
        self.assertIn('$value$plusargs("T57_RUN_ROOT=%s", t57_run_root)', testbench)
        self.assertIn("if (t57_run_root != T57_EXPECTED_RUN_ROOT)", testbench)
        self.assertIn('$fatal(1, "缺少 T57_RUN_ROOT testplusarg")', testbench)
        self.assertIn('$fatal(1, "T57_RUN_ROOT 与本轮 attempt04 不匹配: %s", t57_run_root)', testbench)
        self.assertNotIn("attempt02", testbench)
        self.assertNotIn("attempt03", testbench)

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
            self.assertRegex(
                testbench,
                rf'\$fopen\({variable},\s*"{re.escape(mode)}"\)',
            )
        fopen_arguments = re.findall(r'\$fopen\(([^,]+),\s*"([^"]+)"\)', testbench)
        self.assertEqual(
            set(fopen_arguments),
            {(variable, mode) for variable, (_, mode) in expected_paths.items()},
        )

    def test_xsim_plusarg_and_wrapper_are_bound_to_same_attempt04_root(self) -> None:
        runner = _read("verification/test_s2a_conv_layer35_row21_all_channels_rtl.py")
        self.assertIn('RUN_ROOT = EVIDENCE_ROOT / "run09" / "attempt04"', runner)
        self.assertIn('"verification/test_s2a_t57_attempt04_binding.py",', runner)
        self.assertIn('testplusarg_values = _option_values(simulate, "-testplusarg")', runner)
        self.assertIn('expected_testplusarg = f"T57_RUN_ROOT={RUN_ROOT.resolve().as_posix()}"', runner)
        self.assertIn("testplusarg_values == [expected_testplusarg]", runner)

        no_wave = _read("sim/s2a_t57_no_wave.tcl")
        self.assertIn('set t57_testplusarg "T57_RUN_ROOT=$t57_run_root_posix"', no_wave)
        self.assertIn('set t57_xsim_options "-testplusarg $t57_testplusarg"', no_wave)
        self.assertIn("set_property xsim.simulate.xsim.more_options $t57_xsim_options $t57_simset", no_wave)
        self.assertIn("get_property xsim.simulate.xsim.more_options $t57_simset", no_wave)

        project_tcl = _read("report/evidence/S2A-T57/run_project_sim.tcl")
        self.assertIn("set ::t57_run_root $run_directory", project_tcl)
        self.assertIn("set testplusarg_values [t57_option_values $simulate_command -testplusarg]", project_tcl)
        self.assertIn('set expected_testplusarg "T57_RUN_ROOT=$expected_run_root"', project_tcl)
        self.assertIn("[lindex $testplusarg_values 0] ne $expected_testplusarg", project_tcl)
        self.assertIn("run09\\attempt04", project_tcl)

        wrapper = _read("verification/run_s2a_t57_project_sim.ps1")
        self.assertIn('run09\\attempt04', wrapper)
        self.assertIn('"verification/test_s2a_t57_attempt04_binding.py",', wrapper)
        self.assertIn('"T57_RUN_ROOT=" + [IO.Path]::GetFullPath($RunDirectory).Replace([char]92, [char]47)', wrapper)
        self.assertIn('$testplusargMatches.Count -ne 1', wrapper)
        self.assertIn('$testplusargValue, $expectedRunRootArgument', wrapper)


if __name__ == "__main__":
    unittest.main()
