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
        """真实执行一个非 Darknet PE 时，伪造身份不能靠输出字符串通过。"""

        report = {"checks": {}, "commands": []}
        self.assertTrue(environment_probe._is_windows_pe(Path(sys.executable)))
        self.assertFalse(environment_probe._probe_darknet(Path(sys.executable), report))
        self.assertIn("未返回可识别 Darknet 输出", report["checks"]["darknet"])

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

    def test_fake_darknet_output_is_not_a_real_execution_evidence(self) -> None:
        """模拟 Darknet 输出不能代替实际可执行文件，当前仅记录边界而不宣称通过。"""

        report = {"checks": {}, "commands": []}
        fake = Path(tempfile.gettempdir()) / "s1_t01_fake_darknet.exe"
        fake.write_text("MZ PE Darknet 9.9", encoding="utf-8")
        try:
            with patch.object(environment_probe, "_run_command", return_value={"passed": True, "exit_code": 0, "stdout": "Darknet 9.9", "stderr": ""}):
                self.assertFalse(environment_probe._probe_darknet(fake, report))
        finally:
            fake.unlink(missing_ok=True)
        self.assertIn("PE", report["checks"]["darknet"])


if __name__ == "__main__":
    unittest.main()
