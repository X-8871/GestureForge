"""静态核验 T57 attempt08 的 Tcl 选项、Windows 路径比较与本轮目录绑定。"""

from __future__ import annotations

import importlib.util
import re
import sys
import tkinter
import unittest
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RUN_ROOT = "D:/FPGA_Competition/report/evidence/S2A-T57/run09/attempt08"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _load_runner():
    runner_path = ROOT / "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py"
    spec = importlib.util.spec_from_file_location("t57_attempt08_runner_test", runner_path)
    if spec is None or spec.loader is None:
        raise AssertionError("无法导入 T57 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Attempt08BindingTests(unittest.TestCase):
    """确保本轮 Tcl 参数不被误解析，路径和所有观测文件绑定 attempt08。"""

    def test_property_uses_named_options_and_runtime_command_has_one_plusarg(self) -> None:
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

        module = _load_runner()
        expected = f"T57_RUN_ROOT={EXPECTED_RUN_ROOT}"
        command = (
            f"{module.TOP}_behav -key Behavioral:{module.SIMSET}:Functional:{module.TOP} "
            f"-tclbatch {EXPECTED_RUN_ROOT}/xsim_run.tcl -testplusarg {expected}"
        )
        self.assertEqual(module._option_values(command, "-testplusarg"), [expected])
        self.assertEqual(
            module._option_values(command + f" -testplusarg {expected}", "-testplusarg"),
            [expected, expected],
        )
        self.assertNotEqual(
            module._option_values(command.replace("attempt08", "attempt05"), "-testplusarg"),
            [expected],
        )

        runner = _read("verification/test_s2a_conv_layer35_row21_all_channels_rtl.py")
        self.assertIn('RUN_ROOT = EVIDENCE_ROOT / "run09" / "attempt08"', runner)
        self.assertIn('"verification/test_s2a_t57_attempt08_binding.py",', runner)
        self.assertIn('T57_CUSTOM_TCL_SENTINEL=run09_attempt08', runner)

    def test_tcl_wrapper_and_testbench_share_attempt08_root(self) -> None:
        project_tcl = _read("report/evidence/S2A-T57/run_project_sim.tcl")
        self.assertIn("run09\\attempt08", project_tcl)
        self.assertIn(
            "set testplusarg_values [t57_option_values $simulate_command -testplusarg]",
            project_tcl,
        )
        self.assertIn('set expected_testplusarg "T57_RUN_ROOT=$expected_run_root"', project_tcl)
        self.assertIn("[llength $testplusarg_values] != 1", project_tcl)
        self.assertIn("[lindex $testplusarg_values 0] ne $expected_testplusarg", project_tcl)
        self.assertIn("run09_attempt08", project_tcl)

        wrapper = _read("verification/run_s2a_t57_project_sim.ps1")
        self.assertIn("run09\\attempt08", wrapper)
        self.assertIn('"verification/test_s2a_t57_attempt08_binding.py",', wrapper)
        self.assertIn("$testplusargMatches.Count -ne 1", wrapper)
        self.assertIn("$testplusargValue, $expectedRunRootArgument", wrapper)
        self.assertIn("run09_attempt08", wrapper)

        testbench = _read("sim/tb_s2a_conv_layer35_row21_all_channels.sv")
        self.assertIn(f'T57_EXPECTED_RUN_ROOT = "{EXPECTED_RUN_ROOT}"', testbench)
        self.assertIn('$value$plusargs("T57_RUN_ROOT=%s", t57_run_root)', testbench)
        self.assertIn("if (t57_run_root != T57_EXPECTED_RUN_ROOT)", testbench)
        for stale_attempt in ("attempt02", "attempt03", "attempt04", "attempt05", "attempt06", "attempt07"):
            self.assertNotIn(stale_attempt, testbench)

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

    def test_tcl_slash_style_matches_only_the_same_absolute_windows_xpr(self) -> None:
        module = _load_runner()
        expected = PureWindowsPath(
            r"D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt08"
            r"\isolated_project\s2a_t57_row21_isolated.xpr"
        )
        tcl_style = "D:/FPGA_Competition/report/evidence/S2A-T57/run09/attempt08/"
        tcl_style += "isolated_project/s2a_t57_row21_isolated.xpr"
        self.assertTrue(module._same_absolute_windows_path(tcl_style, expected))
        self.assertTrue(module._same_absolute_windows_path(str(expected), tcl_style))

        invalid_paths = (
            tcl_style.replace("D:/", "E:/", 1),
            tcl_style.replace("attempt08", "attempt05"),
            tcl_style.replace("attempt08", "attempt06"),
            tcl_style.replace("attempt08", "attempt07"),
            tcl_style.replace("isolated_project/", "other_project/"),
            tcl_style.replace("s2a_t57_row21_isolated.xpr", "s2a_t57_row20_isolated.xpr"),
            "report/evidence/S2A-T57/run09/attempt08/isolated_project/s2a_t57_row21_isolated.xpr",
        )
        for invalid_path in invalid_paths:
            with self.subTest(invalid_path=invalid_path):
                self.assertFalse(module._same_absolute_windows_path(invalid_path, expected))

    def test_snapshot_paths_use_independent_fields_for_both_executables(self) -> None:
        """实际执行 Tcl proc，覆盖六个快照字段并检查互不覆盖。"""
        module = _load_runner()
        project_tcl = _read("report/evidence/S2A-T57/run_project_sim.tcl")
        match = re.search(
            r"(?ms)^proc t57_record_snapshot_path \{[^}]+\} \{.*?^\}",
            project_tcl,
        )
        self.assertIsNotNone(match)
        proc_source = match.group(0)
        self.assertIn("switch -- $executable", proc_source)
        self.assertIn("elaborate {set kind elaborate}", proc_source)
        self.assertIn("simulate {set kind simulate}", proc_source)
        self.assertIn("default {error", proc_source)
        self.assertNotIn('executable eq "xelab"', proc_source)

        interpreter = tkinter.Tcl()
        interpreter.eval(proc_source)
        recorded_fields: dict[str, str] = {}
        for snapshot_stage in ("before_compile", "after_compile", "after_elaborate"):
            elaborate_field = f"::t57_elaborate_{snapshot_stage}_batch_path"
            simulate_field = f"::t57_simulate_{snapshot_stage}_batch_path"
            elaborate_path = (
                f"{EXPECTED_RUN_ROOT}/isolated_project/elaborate.{snapshot_stage}.bat"
            )
            simulate_path = f"{EXPECTED_RUN_ROOT}/isolated_project/simulate.{snapshot_stage}.bat"

            interpreter.call(
                "t57_record_snapshot_path", snapshot_stage, "elaborate", elaborate_path,
            )
            self.assertTrue(
                module._same_absolute_windows_path(
                    interpreter.getvar(elaborate_field), elaborate_path,
                )
            )
            with self.assertRaises(tkinter.TclError):
                interpreter.getvar(simulate_field)

            interpreter.call(
                "t57_record_snapshot_path", snapshot_stage, "simulate", simulate_path,
            )
            self.assertTrue(
                module._same_absolute_windows_path(
                    interpreter.getvar(elaborate_field), elaborate_path,
                )
            )
            self.assertTrue(
                module._same_absolute_windows_path(
                    interpreter.getvar(simulate_field), simulate_path,
                )
            )

            refreshed_elaborate_path = elaborate_path + ".refresh"
            interpreter.call(
                "t57_record_snapshot_path", snapshot_stage, "elaborate",
                refreshed_elaborate_path,
            )
            self.assertTrue(
                module._same_absolute_windows_path(
                    interpreter.getvar(elaborate_field), refreshed_elaborate_path,
                )
            )
            self.assertTrue(
                module._same_absolute_windows_path(
                    interpreter.getvar(simulate_field), simulate_path,
                )
            )
            recorded_fields[elaborate_field] = interpreter.getvar(elaborate_field)
            recorded_fields[simulate_field] = interpreter.getvar(simulate_field)

        self.assertEqual(len(recorded_fields), 6)
        with self.assertRaises(tkinter.TclError):
            interpreter.call(
                "t57_record_snapshot_path", "before_compile", "xelab",
                f"{EXPECTED_RUN_ROOT}/unexpected.bat",
            )


if __name__ == "__main__":
    unittest.main()
