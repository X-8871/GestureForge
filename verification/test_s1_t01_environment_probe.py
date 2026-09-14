"""S1-T01 环境探针的严格通过条件回归测试。"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verification.s1_t01_environment_probe as environment_probe


class EnvironmentProbeTest(unittest.TestCase):
    """验证 PE、Darknet 输出和 CUDA 设备冒烟标记不能被省略。"""

    def test_invalid_darknet_file_cannot_pass(self) -> None:
        """非 PE 文件即使包含伪造成功输出也不能通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            darknet = root / "darknet.exe"
            smoke = root / "cuda_smoke.exe"
            darknet.write_text("not an executable", encoding="utf-8")
            report = {"checks": {}, "commands": []}
            with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "Darknet 9.9", "stderr": ""}):
                self.assertFalse(environment_probe._probe_darknet(darknet, report))
            self.assertIn("PE", report["checks"]["darknet"])

    def test_real_non_darknet_pe_cannot_pass(self) -> None:
        """有效 PE 没有提交绑定摘要时，伪造身份不能靠输出字符串通过。"""

        report = {"checks": {}, "commands": []}
        self.assertTrue(environment_probe._is_windows_pe(Path(sys.executable)))
        with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "Darknet 9.9", "stderr": ""}) as run:
            self.assertFalse(environment_probe._probe_darknet(Path(sys.executable), report))
        run.assert_not_called()
        self.assertIn("没有提交绑定", report["checks"]["darknet"])

    def test_fake_cuda_success_marker_cannot_pass(self) -> None:
        """非 PE 文件即使包含 CUDA 成功标记也不能通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            smoke = root / "cuda_smoke.exe"
            smoke.write_text("S1_T01_CUDA_SMOKE_PASS", encoding="utf-8")
            report = {"checks": {}, "commands": []}
            with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "S1_T01_CUDA_SMOKE_PASS", "stderr": ""}):
                self.assertFalse(environment_probe._probe_cuda_smoke(smoke, report))
            self.assertIn("PE", report["checks"]["cuda_device_smoke"])

    def test_valid_pe_fake_darknet_output_is_rejected(self) -> None:
        """结构有效的 PE 即使伪造 Darknet 输出，也必须先通过摘要绑定。"""

        report = {"checks": {}, "commands": []}
        with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "Darknet 9.9", "stderr": ""}) as run:
            self.assertFalse(environment_probe._probe_darknet(Path(sys.executable), report, "0" * 64))
        run.assert_not_called()
        self.assertIn("SHA-256", report["checks"]["darknet"])

    def test_valid_pe_fake_cuda_output_is_rejected(self) -> None:
        """结构有效的 PE 即使伪造 CUDA 成功标记，也必须先通过摘要绑定。"""

        report = {"checks": {}, "commands": []}
        with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "S1_T01_CUDA_SMOKE_PASS", "stderr": ""}) as run:
            self.assertFalse(environment_probe._probe_cuda_smoke(Path(sys.executable), report, "0" * 64))
        run.assert_not_called()
        self.assertIn("SHA-256", report["checks"]["cuda_device_smoke"])

    def test_matching_digest_is_required_before_darknet_execution(self) -> None:
        """仅测试注入的可信摘要匹配后才允许进入功能输出检查。"""

        report = {"checks": {}, "commands": []}
        expected = "a" * 64
        with patch.object(environment_probe, "_sha256", return_value=expected), patch.object(
            environment_probe,
            "_run_command",
            return_value={"command": ["darknet.exe", "--version"], "passed": True, "exit_code": 0, "stdout": "Darknet 9.9", "stderr": ""},
        ) as run:
            self.assertTrue(environment_probe._probe_darknet(Path(sys.executable), report, expected))
        run.assert_called_once()
        self.assertTrue(report["checks"]["darknet"].startswith("通过"))

    def test_unavailable_identity_manifest_cannot_pass(self) -> None:
        """清单保留不可用占位值时，不能被解释成任何可信身份。"""

        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "identity.txt"
            manifest.write_text(
                "identity.darknet_executable_sha256 UNAVAILABLE\n"
                "identity.cuda_smoke_executable_sha256 UNAVAILABLE\n",
                encoding="utf-8",
            )
            report = {}
            self.assertEqual(environment_probe._load_identity_manifest(manifest, report), {})
            self.assertIn("不可用占位值", report["identity_manifest_error"])


if __name__ == "__main__":
    unittest.main()
