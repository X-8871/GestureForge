"""M3 工具离线单元测试；不启动 XSDB，也不连接硬件。"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import m3_pair as tool


def context_value(window: str = "w-1", event: str = "e-1", lifecycle: str = "life-1") -> dict:
    return {
        "window_id": window,
        "event_id": event,
        "lifecycle_id": lifecycle,
        "target": "Cortex-A9 MPCore #0",
        "filter": "name =~ *Cortex-A9*#0",
        "bit_sha256": "1" * 64,
        "init_elf_sha256": "2" * 64,
        "app_elf_sha256": "3" * 64,
        "cpu0_state": "Stopped",
        "cpu1_state": "Suspended",
        "masters_quiesced": True,
        "cache_basis": "test-cache-protocol",
    }


def marker_output(prefix: str) -> bytes:
    lines = list(tool.expected_marker_lines(prefix))
    lines.extend((f"{prefix}_CPU0_STATE=Stopped: (Vector Catch)", f"{prefix}_CPU1_STATE=Stopped: (Vector Catch)"))
    return ("\n".join(lines) + "\n").encode("utf-8")


def make_capture(directory: Path, phase: str, data: bytes, *, ctx: dict | None = None, captured: str | None = None) -> None:
    directory.mkdir()
    read_a = directory / tool.READ_A_NAME
    read_b = directory / tool.READ_B_NAME
    read_a.write_bytes(data)
    read_b.write_bytes(data)
    prefix = "M3PAIR_fixture"
    stdout = directory / "xsdb.stdout.log"
    stderr = directory / "xsdb.stderr.log"
    stdout.write_bytes(marker_output(prefix))
    stderr.write_bytes(b"")
    tcl = directory / "capture_readonly.tcl"
    tcl.write_text("puts fixture\n", encoding="utf-8", newline="\n")
    m_hash_a, size_a = tool.sha256_file(read_a)
    m_hash_b, size_b = tool.sha256_file(read_b)
    assert m_hash_a == m_hash_b
    manifest = {
        "schema": "gestureforge.m3_pair.capture.v1",
        "status": "CAPTURED",
        "hash_basis": "worktree_disk",
        "phase": phase,
        "window_id": (ctx or context_value())["window_id"],
        "event_id": (ctx or context_value())["event_id"],
        "lifecycle_id": (ctx or context_value())["lifecycle_id"],
        "address_start_inclusive": f"0x{tool.DDR_START:08X}",
        "address_end_exclusive": f"0x{tool.DDR_END:08X}",
        "bytes_required": tool.DDR_BYTES,
        "words_required": tool.DDR_WORDS,
        "captured_at_utc8": captured or ("2026-10-30T10:00:00+08:00" if phase == "before" else "2026-10-30T10:01:00+08:00"),
        "context": ctx or context_value(),
        "xsdb": {"path": "xsdb.exe", "returncode": 0, "shell": False, "timeout_seconds": 120, "argv": ["xsdb.exe", "-no-ini", str(tcl)]},
        "markers": list(tool.expected_marker_lines(prefix)),
        "readouts": [
            {"path": tool.READ_A_NAME, "bytes": size_a, "sha256": m_hash_a, "hash_basis": "worktree_disk"},
            {"path": tool.READ_B_NAME, "bytes": size_b, "sha256": m_hash_b, "hash_basis": "worktree_disk"},
        ],
        "other_files": [tool.hash_item(tcl), tool.hash_item(stdout), tool.hash_item(stderr)],
    }
    tool.write_manifest_with_checksum(directory / tool.MANIFEST_NAME, manifest, directory / tool.MANIFEST_HASH_NAME)


class M3PairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.xsdb = self.root / "xsdb.exe"
        self.xsdb.write_bytes(b"mock only")
        self.auth = self.root / "authorization.txt"
        self.auth.write_text("approval receipt fixture", encoding="utf-8")
        self.context_path = self.root / "context.json"
        self.write_context(context_value())

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_context(self, value: dict) -> None:
        self.context_path.write_text(json.dumps(value), encoding="utf-8")

    def fake_runner(self, payload_a: bytes, payload_b: bytes | None = None, *, stdout: bytes | None = None, suffix: bytes = b"", returncode: int = 0):
        def run(argv: list[str], timeout: int) -> subprocess.CompletedProcess[bytes]:
            self.assertEqual(argv[1], "-no-ini")
            self.assertEqual(len(argv), 3)
            self.assertEqual(timeout, 120)
            tcl_path = Path(argv[2])
            out_dir = tcl_path.parent
            script = tcl_path.read_text(encoding="utf-8")
            self.assertIn("mrd -bin -file", script)
            (out_dir / tool.READ_A_NAME).write_bytes(payload_a)
            (out_dir / tool.READ_B_NAME).write_bytes(payload_a if payload_b is None else payload_b)
            prefix_match = re.search(r'(?m)^puts "(M3PAIR_[0-9a-f]+)_BEGIN"$', script)
            self.assertIsNotNone(prefix_match)
            prefix = prefix_match.group(1)
            printed = (marker_output(prefix) + suffix) if stdout is None else stdout
            return subprocess.CompletedProcess(argv, returncode, printed, b"")

        return run

    def capture_call(self, out: Path, runner, **overrides):
        args = {
            "out_text": str(out),
            "xsdb_text": str(self.xsdb),
            "port": 3121,
            "window_id": "w-1",
            "phase": "before",
            "event_id": "e-1",
            "authorization_file_text": str(self.auth),
            "context_file_text": str(self.context_path),
            "runner": runner,
        }
        args.update(overrides)
        return tool.capture(**args)

    def test_fixed_address_math(self) -> None:
        self.assertEqual(tool.DDR_BYTES, 12_615_680)
        self.assertEqual(tool.DDR_WORDS, 3_153_920)
        self.assertEqual(tool.DDR_END - tool.DDR_START, tool.DDR_BYTES)

    def test_valid_context_and_capture(self) -> None:
        out = self.root / "capture"
        result = self.capture_call(out, self.fake_runner(bytes(tool.DDR_BYTES)))
        self.assertEqual(result["status"], "CAPTURED")
        self.assertTrue((out / tool.MANIFEST_NAME).is_file())
        manifest = json.loads((out / tool.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["authorization_file"]["sha256"], hashlib.sha256(self.auth.read_bytes()).hexdigest())
        self.assertIn("不验证", manifest["authorization_file"]["meaning"])

    def test_capture_records_worktree_disk_hash_basis(self) -> None:
        out = self.root / "capture"
        self.capture_call(out, self.fake_runner(bytes(tool.DDR_BYTES)))
        manifest = json.loads((out / tool.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["hash_basis"], "worktree_disk")
        self.assertTrue(all(row["hash_basis"] == "worktree_disk" for row in manifest["readouts"] + manifest["other_files"]))

    def test_capture_uses_no_ini_and_positional_tcl_argument(self) -> None:
        out = self.root / "capture"
        self.capture_call(out, self.fake_runner(bytes(tool.DDR_BYTES)))
        manifest = json.loads((out / tool.MANIFEST_NAME).read_text(encoding="utf-8"))
        self.assertEqual(manifest["xsdb"]["argv"], [str(self.xsdb.resolve()), "-no-ini", str(out / "capture_readonly.tcl")])

    def test_compare_rejects_xsdb_without_no_ini(self) -> None:
        before, after = self.make_compare_pair()
        manifest_path = before / tool.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["xsdb"]["argv"] = ["xsdb.exe", str(before / "capture_readonly.tcl")]
        tool.write_manifest_with_checksum(manifest_path, manifest, before / tool.MANIFEST_HASH_NAME)
        with self.assertRaisesRegex(tool.ToolError, "XSDB 执行元数据无效"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_compare_rejects_xsdb_file_option(self) -> None:
        before, after = self.make_compare_pair()
        manifest_path = before / tool.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["xsdb"]["argv"] = ["xsdb.exe", "-file", str(before / "capture_readonly.tcl")]
        tool.write_manifest_with_checksum(manifest_path, manifest, before / tool.MANIFEST_HASH_NAME)
        with self.assertRaisesRegex(tool.ToolError, "XSDB 执行元数据无效"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_context_missing_required_field_rejected(self) -> None:
        context = context_value()
        del context["cache_basis"]
        self.write_context(context)
        with self.assertRaises(tool.ToolError):
            self.capture_call(self.root / "capture", self.fake_runner(b""))

    def test_context_window_mismatch_rejected(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "window_id/event_id"):
            self.capture_call(self.root / "capture", self.fake_runner(b""), window_id="other")

    def test_context_event_mismatch_rejected(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "window_id/event_id"):
            self.capture_call(self.root / "capture", self.fake_runner(b""), event_id="other")

    def test_context_running_core_rejected(self) -> None:
        context = context_value()
        context["cpu1_state"] = "Running"
        self.write_context(context)
        with self.assertRaisesRegex(tool.ToolError, "cpu1_state"):
            self.capture_call(self.root / "capture", self.fake_runner(b""))

    def test_capture_existing_output_rejected(self) -> None:
        out = self.root / "exists"
        out.mkdir()
        with self.assertRaisesRegex(tool.ToolError, "必须不存在"):
            self.capture_call(out, self.fake_runner(bytes(tool.DDR_BYTES)))

    def test_exit_zero_with_error_text_rejected(self) -> None:
        out = self.root / "capture"
        with self.assertRaisesRegex(tool.ToolError, "含 error"):
            self.capture_call(out, self.fake_runner(bytes(tool.DDR_BYTES), suffix=b"ERROR: mock\n"))

    def test_nonzero_exit_rejected(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "退出码"):
            self.capture_call(self.root / "capture", self.fake_runner(bytes(tool.DDR_BYTES), returncode=1))

    def test_missing_target_marker_rejected(self) -> None:
        markers = list(tool.expected_marker_lines("M3PAIR_fixture"))
        markers.remove("M3PAIR_fixture_TARGET_STATE_OK")
        with self.assertRaisesRegex(tool.ToolError, "缺少成功标记"):
            self.capture_call(self.root / "capture", self.fake_runner(bytes(tool.DDR_BYTES), stdout=("\n".join(markers)).encode()))

    def test_short_dump_rejected(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "长度错误"):
            self.capture_call(self.root / "capture", self.fake_runner(b"short"))

    def test_long_dump_rejected(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "长度错误"):
            self.capture_call(self.root / "capture", self.fake_runner(bytes(tool.DDR_BYTES + 1)))

    def test_two_reads_must_match(self) -> None:
        with self.assertRaisesRegex(tool.ToolError, "A/B 双读"):
            self.capture_call(self.root / "capture", self.fake_runner(bytes(tool.DDR_BYTES), b"x" * tool.DDR_BYTES))

    def test_generated_tcl_is_read_only_and_distinct_paths(self) -> None:
        script = tool.build_tcl(self.root, 3131, "M3PAIR_x")
        self.assertIn("Cortex-A9*#0", script)
        self.assertIn("Cortex-A9*#1", script)
        self.assertIn("M3PAIR_x_TARGET_STATE_OK", script)
        self.assertIn("set core_state [string trim [state]]", script)
        self.assertNotIn("dict get $props state", script)
        self.assertIn("M3PAIR_x_${core_label}_STATE=$core_state", script)
        self.assertIn("(stopped|suspended)(:|[[:space:]]|$)", script)
        self.assertIn('puts "M3PAIR_x_${core_label}_STATE_OK"', script)
        self.assertIn('puts "M3PAIR_x_${core_label}_STATE=$core_state"', script)
        self.assertIn("0x12000000 3153920", script)
        self.assertIn("read_a.bin", script)
        self.assertIn("read_b.bin", script)
        self.assertNotRegex(script, r"(?m)^\s*(?:reset|init|dow|con|mwr|stop)\b")
        self.assertNotEqual(self.root / tool.READ_A_NAME, self.root / tool.READ_B_NAME)

    def test_readme_execution_template_points_to_this_release(self) -> None:
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        tool_lines = [line for line in readme.splitlines() if line.startswith("$tool = ")]
        self.assertEqual(len(tool_lines), 1)
        raw_value = tool_lines[0].split("=", 1)[1].strip()
        self.assertTrue(raw_value.startswith("'") and raw_value.endswith("'"))
        declared_tool = Path(raw_value[1:-1]).resolve(strict=True)
        canonical_tool = Path(__file__).with_name("m3_pair.py").resolve(strict=True)
        self.assertEqual(declared_tool, canonical_tool)
        self.assertNotIn("m3_pair_tool_20261030_r01", str(declared_tool))
        self.assertNotIn("m3_pair_tool_20261030_r02", str(declared_tool))
        self.assertEqual(declared_tool.read_bytes(), Path(tool.__file__).resolve(strict=True).read_bytes())

    def make_compare_pair(self, *, before_ctx=None, after_ctx=None, before_time=None, after_time=None, before_data=None, after_data=None):
        before_dir = self.root / "before"
        after_dir = self.root / "after"
        data = bytes(tool.DDR_BYTES) if before_data is None else before_data
        make_capture(before_dir, "before", data, ctx=before_ctx, captured=before_time)
        make_capture(after_dir, "after", data if after_data is None else after_data, ctx=after_ctx, captured=after_time)
        return before_dir, after_dir

    def test_compare_unchanged_pair(self) -> None:
        data = bytes(tool.DDR_BYTES)
        baseline = hashlib.sha256(data).hexdigest()
        before, after = self.make_compare_pair()
        with patch.object(tool, "BASELINE_SHA256", baseline):
            report, code = tool.compare(str(before), str(after), str(self.root / "report"))
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "PAIR_UNCHANGED")
        self.assertEqual(report["changed_bits"], 0)

    def test_compare_six_bit_change_counts_and_exit_one(self) -> None:
        before_buffer = bytearray(tool.DDR_BYTES)
        before_buffer[0] = 0b11110000
        before_data = bytes(before_buffer)
        after_buffer = bytearray(before_data)
        after_buffer[0] = 0b11001101
        after_buffer[3] = 0b00000010
        before, after = self.make_compare_pair(before_data=before_data, after_data=bytes(after_buffer))
        baseline = hashlib.sha256(before_data).hexdigest()
        with patch.object(tool, "BASELINE_SHA256", baseline):
            report, code = tool.compare(str(before), str(after), str(self.root / "report"))
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "REGION_CHANGED")
        self.assertEqual(report["changed_bytes"], 2)
        self.assertEqual(report["changed_bits"], 6)
        self.assertEqual(report["zero_to_one_bits"], 4)
        self.assertEqual(report["one_to_zero_bits"], 2)

    def test_compare_context_drift_rejected(self) -> None:
        before_ctx = context_value()
        after_ctx = context_value()
        after_ctx["bit_sha256"] = "f" * 64
        before, after = self.make_compare_pair(before_ctx=before_ctx, after_ctx=after_ctx)
        with patch.object(tool, "BASELINE_SHA256", hashlib.sha256(bytes(tool.DDR_BYTES)).hexdigest()):
            with self.assertRaisesRegex(tool.ToolError, "context 身份漂移"):
                tool.compare(str(before), str(after), str(self.root / "report"))

    def test_compare_same_input_directory_rejected(self) -> None:
        before, _ = self.make_compare_pair()
        with self.assertRaisesRegex(tool.ToolError, "同一目录"):
            tool.compare(str(before), str(before), str(self.root / "report"))

    def test_compare_wrong_phase_rejected(self) -> None:
        before, after = self.make_compare_pair()
        manifest_path = after / tool.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["phase"] = "before"
        tool.write_manifest_with_checksum(manifest_path, manifest, after / tool.MANIFEST_HASH_NAME)
        with self.assertRaisesRegex(tool.ToolError, "phase"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_compare_lifecycle_mismatch_rejected(self) -> None:
        before_ctx = context_value()
        after_ctx = context_value(lifecycle="life-2")
        before, after = self.make_compare_pair(before_ctx=before_ctx, after_ctx=after_ctx)
        with self.assertRaisesRegex(tool.ToolError, "context 身份漂移"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_compare_reversed_time_rejected(self) -> None:
        before, after = self.make_compare_pair(
            before_time="2026-10-30T10:02:00+08:00",
            after_time="2026-10-30T10:01:00+08:00",
        )
        with self.assertRaisesRegex(tool.ToolError, "时间必须晚于"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_capture_manifest_tampering_rejected(self) -> None:
        before, after = self.make_compare_pair()
        manifest_path = before / tool.MANIFEST_NAME
        manifest_path.write_text(manifest_path.read_text(encoding="utf-8").replace("CAPTURED", "ALTERED"), encoding="utf-8")
        with self.assertRaisesRegex(tool.ToolError, "清单校验值"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_capture_dump_tampering_rejected(self) -> None:
        before, after = self.make_compare_pair()
        with (before / tool.READ_A_NAME).open("r+b") as stream:
            stream.seek(0)
            stream.write(b"\x01")
        with self.assertRaisesRegex(tool.ToolError, "readout 长度或 SHA"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_missing_capture_marker_rejected_even_if_manifest_rehashed(self) -> None:
        before, after = self.make_compare_pair()
        manifest_path = before / tool.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["markers"].pop(1)
        tool.write_manifest_with_checksum(manifest_path, manifest, before / tool.MANIFEST_HASH_NAME)
        with self.assertRaisesRegex(tool.ToolError, "marker 列表无效"):
            tool.compare(str(before), str(after), str(self.root / "report"))

    def test_compare_existing_output_rejected(self) -> None:
        before, after = self.make_compare_pair()
        out = self.root / "report"
        out.mkdir()
        with self.assertRaisesRegex(tool.ToolError, "必须不存在"):
            tool.compare(str(before), str(after), str(out))

    def test_before_must_match_fixed_baseline(self) -> None:
        before, after = self.make_compare_pair()
        with self.assertRaisesRegex(tool.ToolError, "固定 baseline"):
            tool.compare(str(before), str(after), str(self.root / "report"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
