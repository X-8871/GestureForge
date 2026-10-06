"""测试 fixture harness 对 runner progress 失败语义的严格绑定。"""

from __future__ import annotations

import re
import unittest
from typing import Any

from verification import s2a_t68_recovery_manifest as recovery
from verification import verify_s2a_network_backend_golden as harness
from verification import verify_s2a_t68_snapshot_git_binding as snapshot


class ProgressFailureBindingTests(unittest.TestCase):
    """覆盖缩进变化、失败语义回归及 tooling 闭包边界。"""

    def test_current_runner_passes_fixture_harness_bindings(self) -> None:
        """现有 runner 的 progress 处理结构应通过完整 fixture harness 校验。"""
        result = harness.verify_harness_bindings()
        self.assertTrue(result["progress_watchdog_semantics"]["bad_marker_blocks_pass"])
        self.assertTrue(result["progress_watchdog_semantics"]["nonzero_runner_exit_preserved"])

    def test_failure_guards_allow_multiline_conditions_and_indentation(self) -> None:
        """换行、制表符和缩进变化不能破坏等价 PowerShell 语义检查。"""
        runner_text = (
            "if (\r\n"
            "\t$null -eq $progressMarker\r\n"
            ") {\r\n"
            "        $badProgressMarkerSeen = $true\r\n"
            "}\r\n"
            "if (\r\n"
            "    $runnerExitCode -ne 0\r\n"
            ") {\r\n"
            "\texit $runnerExitCode\r\n"
            "}\r\n"
        )
        harness.verify_progress_failure_bindings(runner_text)

    def test_failure_guards_reject_missing_bad_marker_and_exit_preservation(self) -> None:
        """坏 marker 赋值或非零退出码传播缺失时必须拒绝 runner。"""
        runner_text = harness.T68_RUNNER.read_text(encoding="utf-8-sig")
        marker_block_pattern = re.compile(
            r"(\bif\s*\(\s*\$null\s+-eq\s+\$progressMarker\s*\)\s*\{\s*"
            r"\$badProgressMarkerSeen\s*=\s*)\$true\b",
            re.I | re.S,
        )
        bad_marker_runner, replacements = marker_block_pattern.subn(r"\1$false", runner_text, count=1)
        self.assertEqual(replacements, 1)
        with self.assertRaisesRegex(ValueError, "坏 progress marker 未设置 badProgressMarkerSeen"):
            harness.verify_progress_failure_bindings(bad_marker_runner)
        with self.assertRaisesRegex(ValueError, "runner 未保留失败退出码"):
            harness.verify_progress_failure_bindings(
                runner_text.replace("if ($runnerExitCode -ne 0) { exit $runnerExitCode }", "if ($runnerExitCode -ne 0) { exit 0 }", 1)
            )

    def test_fixture_verifier_remains_group_bound_tooling(self) -> None:
        """允许 tooling 闭包变化，但跨组编译源闭包仍须相同。"""
        verifier_path = "verification/verify_s2a_network_backend_golden.py"
        self.assertIn(verifier_path, snapshot.COMPILE_TOOLING_PATHS)
        self.assertNotIn(verifier_path, snapshot.COMPILE_SOURCE_PATHS)

        shared_compile_sources: dict[str, Any] = {}
        for index, path in enumerate(snapshot.COMPILE_SOURCE_PATHS, start=1):
            shared_compile_sources[path] = {"sha256": f"{index:064x}", "bytes": index}
        old_sources = dict(shared_compile_sources)
        new_sources = dict(shared_compile_sources)
        old_sources[verifier_path] = {"sha256": "a" * 64, "bytes": 10}
        new_sources[verifier_path] = {"sha256": "b" * 64, "bytes": 20}

        recovery._require_same_compile_source_closures(
            {"sources": old_sources},
            {"sources": new_sources},
        )


if __name__ == "__main__":
    unittest.main()
