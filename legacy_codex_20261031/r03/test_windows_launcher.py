"""仅以本地占位bat验证cmd引用、Job收尾和超时边界，不连接板卡。"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import job_launcher
import m3_pair
from test_m3_pair import make_capture


class WindowsLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.batch = self.root / "mock xsdb entry.bat"
        self.batch.write_text('@echo off\necho ARGS=%*\nexit /b 0\n', encoding="utf-8")
        self.script = self.root / "capture with space.tcl"
        self.script.write_text("# 纯本机占位，绝不交给真实XSDB\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_actual_cmd_batch_eval_and_job_cleanup(self):
        result = m3_pair._run_xsdb([str(self.batch), "-no-ini", str(self.script)], 120, test_only_allow_mock=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"-no-ini -eval", result.stdout)
        self.assertIn(b"source {", result.stdout)
        record = result.launcher_record
        self.assertTrue(record["cleanup_confirmed"])
        self.assertEqual(record["job_samples"][-1]["ActiveProcesses"], 0)
        self.assertEqual(record["status"], "PASS_PROCESS_ONLY")
        self.assertFalse(record["official_entry_verified"])

    def test_arbitrary_batch_rejected_in_real_mode(self):
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.windows_launch_plan([str(self.batch), "-no-ini", str(self.script)])

    def test_bare_executable_rejected(self):
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.windows_launch_plan([sys.executable, "-no-ini", str(self.script)])

    def test_expansion_and_tcl_delimiters_rejected(self):
        for character in '%!^&|<>{}"\r\n':
            with self.subTest(character=repr(character)), self.assertRaises(m3_pair.ToolError):
                m3_pair.windows_launch_plan([str(self.batch), "-no-ini", str(self.script) + character])

    def test_job_timeout_invalid_before_launch(self):
        for timeout in (0, -1, 600.01, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                job_launcher.run_job(sys.executable, "", self.root, {}, self.root / "bad", timeout)

    def make_v2_fixture(self):
        """构造显式离线夹具，仅验证记录绑定，不冒充真实执行。"""
        directory = self.root / "fixture"
        make_capture(directory, "before", bytes(m3_pair.DDR_BYTES))
        manifest = m3_pair.read_json(directory / m3_pair.MANIFEST_NAME)
        argv = [str(m3_pair.OFFICIAL_XSDB.resolve()), "-no-ini", str(directory / "capture_readonly.tcl")]
        plan = m3_pair.windows_launch_plan(argv)
        record = {"application": plan["application"], "command_line": plan["command_line"],
                  "official_entry_verified": True, "root_exit_code": 0, "status": "PASS_PROCESS_ONLY",
                  "cleanup_confirmed": True, "errors": [], "timed_out": False, "assigned": True,
                  "resumed": True, "job_samples": [{"ActiveProcesses": 0}], "test_fixture_only": False,
                  "batch_sha256": plan["batch_sha256"]}
        launcher = directory / "launcher"
        launcher.mkdir()
        m3_pair.write_json(launcher / "launch_plan.json", plan)
        m3_pair.write_json(launcher / "execution.json", record)
        (launcher / "stdout.bin").write_bytes((directory / "xsdb.stdout.log").read_bytes())
        (launcher / "stderr.bin").write_bytes((directory / "xsdb.stderr.log").read_bytes())
        (launcher / "xsdb_entry.bat").write_bytes(m3_pair.OFFICIAL_XSDB.read_bytes())
        manifest["schema"] = "gestureforge.m3_pair.capture.v2"
        manifest["xsdb"].update(path=argv[0], argv=argv, launcher_record=record)
        m3_pair.write_json(directory / "context.json", manifest["context"])
        (directory / "authorization.md").write_text("仅为离线夹具，不提供板卡授权\n", encoding="utf-8")
        manifest["context_file"] = m3_pair.hash_item(directory / "context.json")
        manifest["authorization_file"] = m3_pair.hash_item(directory / "authorization.md")
        for rel in ("launcher/launch_plan.json", "launcher/execution.json", "launcher/stdout.bin", "launcher/stderr.bin", "launcher/xsdb_entry.bat", "context.json", "authorization.md"):
            item = m3_pair.hash_item(directory / rel)
            item["path"] = rel
            manifest["other_files"].append(item)
        m3_pair.write_manifest_with_checksum(directory / m3_pair.MANIFEST_NAME, manifest, directory / m3_pair.MANIFEST_HASH_NAME)
        return directory, manifest

    def test_v2_complete_record_binding(self):
        directory, _ = self.make_v2_fixture()
        manifest, _, _ = m3_pair.verify_capture(directory, "before")
        self.assertFalse(manifest["xsdb"]["launcher_record"]["test_fixture_only"])

    def test_v2_explicit_fixture_rejected(self):
        directory, manifest = self.make_v2_fixture()
        record = manifest["xsdb"]["launcher_record"]
        record["test_fixture_only"] = True
        m3_pair.write_json(directory / "launcher/execution.json", record)
        for item in manifest["other_files"]:
            if item["path"] == "launcher/execution.json":
                item.update(sha256=m3_pair.sha256_file(directory / item["path"])[0], bytes=(directory / item["path"]).stat().st_size)
        m3_pair.write_manifest_with_checksum(directory / m3_pair.MANIFEST_NAME, manifest, directory / m3_pair.MANIFEST_HASH_NAME)
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.verify_capture(directory, "before")

    def test_v2_missing_inline_record_rejected(self):
        directory, manifest = self.make_v2_fixture()
        del manifest["xsdb"]["launcher_record"]
        m3_pair.write_manifest_with_checksum(directory / m3_pair.MANIFEST_NAME, manifest, directory / m3_pair.MANIFEST_HASH_NAME)
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.verify_capture(directory, "before")

    def test_v2_running_context_rejected_even_if_consistently_rehashed(self):
        directory, manifest = self.make_v2_fixture()
        manifest["context"].update(cpu0_state="Running", masters_quiesced=False)
        m3_pair.write_json(directory / "context.json", manifest["context"])
        entry = m3_pair.hash_item(directory / "context.json")
        manifest["context_file"] = entry
        for item in manifest["other_files"]:
            if item["path"] == "context.json":
                item.update(entry)
        m3_pair.write_manifest_with_checksum(directory / m3_pair.MANIFEST_NAME, manifest, directory / m3_pair.MANIFEST_HASH_NAME)
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.verify_capture(directory, "before")

    def test_v2_job_log_tampering_rejected(self):
        directory, _ = self.make_v2_fixture()
        (directory / "launcher/stdout.bin").write_bytes(b"forged")
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.verify_capture(directory, "before")

    def test_v2_cleanup_false_rejected_even_if_rehashed(self):
        directory, manifest = self.make_v2_fixture()
        record = manifest["xsdb"]["launcher_record"]
        record["cleanup_confirmed"] = False
        m3_pair.write_json(directory / "launcher/execution.json", record)
        for item in manifest["other_files"]:
            if item["path"] == "launcher/execution.json":
                item.update(sha256=m3_pair.sha256_file(directory / item["path"])[0], bytes=(directory / item["path"]).stat().st_size)
        m3_pair.write_manifest_with_checksum(directory / m3_pair.MANIFEST_NAME, manifest, directory / m3_pair.MANIFEST_HASH_NAME)
        with self.assertRaises(m3_pair.ToolError):
            m3_pair.verify_capture(directory, "before")

    def test_timeout_kills_only_owned_python_tree(self):
        child = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);time.sleep(60)"
        argv = [sys.executable, "-c", child]
        record = job_launcher.run_job(sys.executable, subprocess.list2cmdline(argv), self.root,
                    job_launcher.offline_environment(self.root), self.root / "timeout", 1)
        self.assertTrue(record["timed_out"] and record["cleanup_confirmed"])
        self.assertEqual(record["job_samples"][-1]["ActiveProcesses"], 0)
        self.assertGreaterEqual(record["job_samples"][-1]["TotalProcesses"], 2)


if __name__ == "__main__":
    unittest.main()
