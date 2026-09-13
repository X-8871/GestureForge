"""S1-T01 环境探针的严格通过条件回归测试。"""

from __future__ import annotations

import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verification.s1_t01_environment_probe as environment_probe


class EnvironmentProbeTest(unittest.TestCase):
    """验证 PE、Darknet 输出和 CUDA 设备冒烟标记不能被省略。"""

    @staticmethod
    def _write_pe(path: Path) -> None:
        """写入仅用于模拟文件格式检查的最小 PE 标识。"""

        data = bytearray(128)
        data[:2] = b"MZ"
        struct.pack_into("<I", data, 0x3C, 64)
        data[64:68] = b"PE\0\0"
        path.write_bytes(data)

    @staticmethod
    def _command_result(command: list[str], stdout: str = "") -> dict:
        """构造模拟的成功命令结果。"""

        return {
            "command": command,
            "available": True,
            "exit_code": 0,
            "stdout": stdout,
            "stderr": "",
            "passed": True,
        }

    def _patch_common(self):
        """构造所有环境探针外部依赖的模拟补丁。"""

        return (
            patch.object(environment_probe.importlib.util, "find_spec", side_effect=lambda name: object() if name == "numpy" else None),
            patch.object(environment_probe.shutil, "which", side_effect=lambda name: f"C:\\tools\\{name}.exe"),
        )

    def test_invalid_darknet_file_cannot_pass(self) -> None:
        """非 PE 文件即使命令被模拟为成功也不能通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            darknet = root / "darknet.exe"
            smoke = root / "cuda_smoke.exe"
            darknet.write_text("not an executable", encoding="utf-8")
            smoke.write_text("smoke", encoding="utf-8")
            patches = self._patch_common()
            with patches[0], patches[1], patch.object(environment_probe, "_run_command", return_value=self._command_result(["mock"], "Darknet S1_T01_CUDA_SMOKE_PASS")):
                report = environment_probe.probe_environment(darknet_executable=darknet, cuda_smoke_executable=smoke)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("PE", report["checks"]["darknet"])

    def test_cuda_smoke_marker_is_required(self) -> None:
        """没有固定 CUDA 成功标记时不能把设备运算视为通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            darknet = root / "darknet.exe"
            smoke = root / "cuda_smoke.exe"
            self._write_pe(darknet)
            smoke.write_text("smoke", encoding="utf-8")

            def run_command(command: list[str], timeout_seconds: float = 10.0) -> dict:
                """为探针返回无 CUDA 成功标记的模拟结果。"""

                output = "Darknet 1.0" if command[0] == str(darknet) else "device ran"
                return self._command_result(command, output)

            patches = self._patch_common()
            with patches[0], patches[1], patch.object(environment_probe, "_run_command", side_effect=run_command):
                report = environment_probe.probe_environment(darknet_executable=darknet, cuda_smoke_executable=smoke)
            self.assertEqual(report["status"], "FAIL")
            self.assertIn("固定成功标记", report["checks"]["cuda_device_smoke"])

    def test_valid_darknet_and_cuda_smoke_can_pass(self) -> None:
        """有效 PE、Darknet 输出和 CUDA 成功标记齐全时才允许通过。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            darknet = root / "darknet.exe"
            smoke = root / "cuda_smoke.exe"
            self._write_pe(darknet)
            smoke.write_text("smoke", encoding="utf-8")

            def run_command(command: list[str], timeout_seconds: float = 10.0) -> dict:
                """为探针返回完整成功条件的模拟结果。"""

                if command[0] == str(darknet):
                    output = "Darknet 1.0"
                elif command[0] == str(smoke):
                    output = "S1_T01_CUDA_SMOKE_PASS"
                else:
                    output = "tool ok"
                return self._command_result(command, output)

            patches = self._patch_common()
            with patches[0], patches[1], patch.object(environment_probe, "_run_command", side_effect=run_command):
                report = environment_probe.probe_environment(darknet_executable=darknet, cuda_smoke_executable=smoke)
            self.assertEqual(report["status"], "PASS")
            self.assertIn("Darknet", report["darknet_version"])
            self.assertEqual(report["checks"]["cuda_device_smoke"], "通过：固定设备运算返回成功标记")


if __name__ == "__main__":
    unittest.main()
