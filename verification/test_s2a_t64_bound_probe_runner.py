import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\FPGA_Competition")
RUNNER = ROOT / "verification" / "run_s2a_t64_layer0_probe_bound.ps1"
EVIDENCE_ROOT = ROOT / "report" / "evidence" / "S2A-T64"
RUN_DIRECTORY = EVIDENCE_ROOT / "sim_run12"
POWERSHELL_HOSTS = [
    path
    for path in (shutil.which("powershell.exe"), shutil.which("pwsh.exe"))
    if path
]

KNOWN_PROCESSES = [
    {
        "process_id": 8712,
        "parent_process_id": 10724,
        "name": "vivado.exe",
        "executable_path": r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe",
        "command_line": r'"D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe"   -mode tcl -source D:\FPGA_Competition\report\evidence\S2A-T60\run06\mcp_server_instance\start_mcp.tcl',
        "creation_date_utc": "2026-09-29T18:07:06.1577890Z",
        "executable_sha256": "3a4e9e3f03d20cd1994dc2eff44566af7a10eaaae04429e9d460bffe3b0e86e4",
    },
    {
        "process_id": 22488,
        "parent_process_id": 8712,
        "name": "xsimk.exe",
        "executable_path": r"D:\FPGA_Competition\report\evidence\S2A-T60\run06\isolated_project\s2a_t60_run06.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row24_all_channels_behav\xsimk.exe",
        "command_line": "xsim.dir/tb_s2a_conv_layer35_row24_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row24_all_channels_behav.wdb -simrunnum 0 -socket 8295",
        "creation_date_utc": "2026-09-29T18:13:11.5972630Z",
        "executable_sha256": "dd50783b44e1e44d89cc61080f376515db8e618a6fd96425048f26960242d0b0",
    },
    {
        "process_id": 13156,
        "parent_process_id": 8712,
        "name": "xsimk.exe",
        "executable_path": r"D:\FPGA_Competition\report\evidence\S2A-T61\run04\isolated_project\s2a_t61_run04.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row25_all_channels_behav\xsimk.exe",
        "command_line": "xsim.dir/tb_s2a_conv_layer35_row25_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row25_all_channels_behav.wdb -simrunnum 0 -socket 12375",
        "creation_date_utc": "2026-09-29T19:39:52.1132030Z",
        "executable_sha256": "5107d47f770b4c4d19c8dbf4a8066b6792cf73e844c4cb61274691faf8293905",
    },
]


class BoundProbeRunnerTests(unittest.TestCase):
    def write_fixture(self, directory, processes):
        fixture = directory / "process_fixture.json"
        fixture.write_text(
            json.dumps({"processes": processes}, ensure_ascii=False), encoding="utf-8"
        )
        return fixture

    def run_preflight(self, host, fixture, simulation=False):
        command = [
            host,
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
        ]
        if Path(host).name.lower().startswith("powershell"):
            command.extend(["-ExecutionPolicy", "Bypass"])
        command.extend(["-File", str(RUNNER)])
        if not simulation:
            command.append("-PreflightOnly")
        command.extend(["-ProcessFixturePath", str(fixture)])
        return subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_valid_protected_identities_and_natural_absence_are_accepted(self):
        self.assertTrue(POWERSHELL_HOSTS, "No PowerShell host was found")
        self.assertFalse(RUN_DIRECTORY.exists(), "sim_run12 must remain a unique new directory")
        with tempfile.TemporaryDirectory(
            prefix="t64_run12_guard_", dir=str(EVIDENCE_ROOT)
        ) as temporary:
            temporary_path = Path(temporary)
            for host in POWERSHELL_HOSTS:
                for processes in (KNOWN_PROCESSES, [], KNOWN_PROCESSES[:2]):
                    fixture = self.write_fixture(temporary_path, processes)
                    result = self.run_preflight(host, fixture)
                    self.assertEqual(
                        result.returncode,
                        0,
                        f"host={host}; process_count={len(processes)}\n{result.stdout}",
                    )
                    self.assertIn("PREFLIGHT_READY", result.stdout)
                    self.assertNotIn("RUN_STATUS=", result.stdout)
        self.assertFalse(RUN_DIRECTORY.exists(), "preflight must not create sim_run12")

    def test_reused_pid_and_image_hash_mismatch_fail_closed(self):
        cases = []
        reused_pid = [dict(item) for item in KNOWN_PROCESSES[:1]]
        reused_pid[0]["creation_date_utc"] = "2026-10-01T00:00:00.0000000Z"
        cases.append(reused_pid)
        bad_hash = [dict(item) for item in KNOWN_PROCESSES[:1]]
        bad_hash[0]["executable_sha256"] = "0" * 64
        cases.append(bad_hash)
        bad_command = [dict(item) for item in KNOWN_PROCESSES[:1]]
        bad_command[0]["command_line"] += " -project changed.xpr"
        cases.append(bad_command)
        extra_xsim = [dict(item) for item in KNOWN_PROCESSES]
        extra_xsim.append(
            {
                "process_id": 45678,
                "parent_process_id": 1,
                "name": "xsim.exe",
                "executable_path": r"D:\unexpected\xsim.exe",
                "command_line": "xsim.exe other_snapshot -R",
                "creation_date_utc": "2026-10-01T00:00:00.0000000Z",
                "executable_sha256": "0" * 64,
            }
        )
        cases.append(extra_xsim)

        with tempfile.TemporaryDirectory(
            prefix="t64_run12_negative_", dir=str(EVIDENCE_ROOT)
        ) as temporary:
            temporary_path = Path(temporary)
            for host in POWERSHELL_HOSTS:
                for processes in cases:
                    fixture = self.write_fixture(temporary_path, processes)
                    result = self.run_preflight(host, fixture)
                    self.assertEqual(
                        result.returncode,
                        96,
                        f"host={host}; process_count={len(processes)}\n{result.stdout}",
                    )
                    self.assertIn("PREFLIGHT_FAILED", result.stdout)
        self.assertFalse(RUN_DIRECTORY.exists(), "negative preflight must not create sim_run12")

    def test_fixture_cannot_be_used_for_a_simulation_run(self):
        with tempfile.TemporaryDirectory(
            prefix="t64_run12_no_launch_", dir=str(EVIDENCE_ROOT)
        ) as temporary:
            fixture = self.write_fixture(Path(temporary), [])
            result = self.run_preflight(POWERSHELL_HOSTS[0], fixture, simulation=True)
            self.assertEqual(result.returncode, 96, result.stdout)
            self.assertIn("only with -PreflightOnly", result.stdout)
        self.assertFalse(RUN_DIRECTORY.exists(), "fixture misuse must not create sim_run12")

    def test_runner_keeps_the_run12_boundary_and_no_plusarg_plan(self):
        text = RUNNER.read_text(encoding="utf-8-sig")
        self.assertIn("$RunDirectory = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T64\\sim_run12'", text)
        self.assertIn("Get-ReferenceCommandLines -SourcePaths $sourcePaths", text)
        self.assertIn("compile_artifacts_reverified_before_xsim", text)
        self.assertIn("xsim_mem_runtime_delta", text)
        self.assertNotIn("AllowConcurrentProtectedProcesses", text)
        self.assertIn("ProcessFixturePath -and -not $PreflightOnly", text)
        self.assertFalse(RUN_DIRECTORY.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
