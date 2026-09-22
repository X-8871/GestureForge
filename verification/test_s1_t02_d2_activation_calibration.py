"""S1-T02-D2 激活 scale 校准报告器的定向测试。"""

from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

try:
    from s1_t02_d2_activation_calibration import ActivationCalibrationError, calibrate
except ModuleNotFoundError:
    from verification.s1_t02_d2_activation_calibration import ActivationCalibrationError, calibrate


class ActivationCalibrationTest(unittest.TestCase):
    """覆盖完整统计、重复样本和缺失层的 fail-closed 语义。"""

    def _fixture(self, root: Path) -> tuple[Path, Path, Path, Path, Path]:
        cfg = root / "model.cfg"
        cfg.write_text(
            "\n".join(
                [
                    "[net]",
                    "width=4",
                    "height=4",
                    "channels=3",
                    "[convolutional]",
                    "filters=2",
                    "size=1",
                    "stride=1",
                    "activation=leaky",
                    "[convolutional]",
                    "filters=1",
                    "size=1",
                    "stride=1",
                    "activation=linear",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        weights = root / "weights.bin"
        weights.write_bytes(b"weights")
        calibration_list = root / "calibration.list"
        calibration_list.write_text("\n".join(f"image_{i:03d}.jpg" for i in range(512)) + "\n", encoding="utf-8")
        executable = root / "darknet.exe"
        executable.write_bytes(b"MZfixture")
        stats = root / "stats.csv"
        with stats.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "sample_index",
                    "layer_index",
                    "layer_type",
                    "output_count",
                    "minimum",
                    "maximum",
                    "sum",
                    "sumsq",
                    "nonfinite",
                ],
            )
            writer.writeheader()
            for sample_index in range(512):
                writer.writerow(
                    {
                        "sample_index": sample_index,
                        "layer_index": 0,
                        "layer_type": "CONVOLUTIONAL",
                        "output_count": 32,
                        "minimum": -2.0,
                        "maximum": 3.0,
                        "sum": 0.0,
                        "sumsq": 1.0,
                        "nonfinite": 0,
                    }
                )
                writer.writerow(
                    {
                        "sample_index": sample_index,
                        "layer_index": 1,
                        "layer_type": "CONVOLUTIONAL",
                        "output_count": 16,
                        "minimum": -1.0,
                        "maximum": 1.0,
                        "sum": 0.0,
                        "sumsq": 1.0,
                        "nonfinite": 0,
                    }
                )
        return cfg, weights, calibration_list, stats, executable

    def test_complete_stats_generate_scales(self) -> None:
        """完整 512 张统计应生成逐层 scale。"""

        with tempfile.TemporaryDirectory() as directory:
            cfg, weights, calibration_list, stats, executable = self._fixture(Path(directory))
            report = calibrate(
                cfg=cfg,
                weights=weights,
                calibration_list=calibration_list,
                stats_csv=stats,
                darknet_executable=executable,
                activation_hook_source=None,
                darknet_source_commit="59596d7880f6504768df41d6daa586f5cb2b932f",
            )
            self.assertEqual(report["status"], "ACTIVATION_SCALE_CALIBRATION_COMPLETE_INTEGER_FORWARD_PENDING")
            self.assertEqual(report["inputs"]["calibration_sample_count"], 512)
            self.assertAlmostEqual(report["layers"]["0"]["activation_scale"], 3.0 / 127.0)
            self.assertAlmostEqual(report["layers"]["1"]["activation_scale"], 1.0 / 127.0)

    def test_duplicate_sample_fails_closed(self) -> None:
        """重复 sample/layer 记录必须拒绝。"""

        with tempfile.TemporaryDirectory() as directory:
            cfg, weights, calibration_list, stats, executable = self._fixture(Path(directory))
            text = stats.read_text(encoding="utf-8")
            first_data = text.splitlines()[1]
            stats.write_text(text + first_data + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ActivationCalibrationError, "重复 sample_index"):
                calibrate(
                    cfg=cfg,
                    weights=weights,
                    calibration_list=calibration_list,
                    stats_csv=stats,
                    darknet_executable=executable,
                    activation_hook_source=None,
                    darknet_source_commit="59596d7880f6504768df41d6daa586f5cb2b932f",
                )

    def test_missing_layer_fails_closed(self) -> None:
        """缺失任意卷积层的统计必须拒绝。"""

        with tempfile.TemporaryDirectory() as directory:
            cfg, weights, calibration_list, stats, executable = self._fixture(Path(directory))
            lines = stats.read_text(encoding="utf-8").splitlines()
            stats.write_text("\n".join([lines[0]] + [line for line in lines[1:] if ",1," not in line]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ActivationCalibrationError, "卷积层 1 样本集合不完整"):
                calibrate(
                    cfg=cfg,
                    weights=weights,
                    calibration_list=calibration_list,
                    stats_csv=stats,
                    darknet_executable=executable,
                    activation_hook_source=None,
                    darknet_source_commit="59596d7880f6504768df41d6daa586f5cb2b932f",
                )


if __name__ == "__main__":
    unittest.main()
