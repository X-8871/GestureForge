"""S1-T02-D2 权重量化参考的隔离单元测试。"""

from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

import s1_t02_d2_int8_weight_reference as reference


class Int8WeightReferenceTest(unittest.TestCase):
    """覆盖 cfg 布局、Darknet 权重顺序、BN 折叠和 CLI 输出。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.cfg = self.root / "fixture.cfg"
        self.weights = self.root / "fixture.weights"
        self.cfg.write_text(
            """[net]
width=2
height=2
channels=3

[convolutional]
filters=2
size=1
stride=1
pad=0
batch_normalize=1
activation=linear

[convolutional]
filters=1
size=1
stride=1
pad=0
batch_normalize=0
activation=linear
""",
            encoding="utf-8",
        )
        values = [
            1.0,
            -2.0,
            2.0,
            0.5,
            0.5,
            -1.0,
            3.0,
            4.0,
            1.0,
            -2.0,
            3.0,
            4.0,
            0.5,
            -0.25,
            0.25,
            2.0,
            -1.0,
        ]
        self.weights.write_bytes(struct.pack("<3iq", 0, 2, 5, 10) + struct.pack(f"<{len(values)}f", *values))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_parse_and_quantize_folds_bn_and_keeps_darknet_layout(self) -> None:
        """BN 折叠和每输出通道量化应与手算结果一致。"""

        spec, header, layers = reference.parse_and_quantize(self.cfg, self.weights)
        self.assertEqual((spec.width, spec.height, spec.channels), (2, 2, 3))
        self.assertEqual(header, (0, 2, 5, 10))
        self.assertEqual(len(spec.convolutions), 2)
        self.assertEqual([layer.spec.weight_count for layer in layers], [6, 2])
        first = layers[0]
        expected_factor = 2.0 / math.sqrt(3.0 + reference.BN_EPSILON)
        self.assertAlmostEqual(first.fused_biases[0], 1.0 - 0.5 * expected_factor, places=6)
        self.assertAlmostEqual(first.scales[0], 3.0 * expected_factor / 127.0, places=6)
        decoded = [value if value < 128 else value - 256 for value in first.quantized_weights]
        self.assertEqual(decoded, [42, -85, 127, 127, 16, -8])
        self.assertEqual(layers[1].statistics["saturated_values"], 1)

    def test_cli_writes_deterministic_package_report_and_summary(self) -> None:
        """CLI 应写出绑定输入、输出哈希和未执行激活校准状态。"""

        calibration = self.root / "calibration.list"
        calibration.write_text("train/a.jpg\ntrain/b.jpg\n", encoding="utf-8")
        output = self.root / "weights.gf8"
        report = self.root / "report.json"
        summary = self.root / "summary.md"
        exit_code = reference.main(
            [
                "--cfg",
                str(self.cfg),
                "--weights",
                str(self.weights),
                "--output",
                str(output),
                "--report",
                str(report),
                "--summary",
                str(summary),
                "--darknet-source-commit",
                "a" * 40,
                "--calibration-list",
                str(calibration),
            ]
        )
        self.assertEqual(exit_code, 0)
        generated = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(generated["status"], "INT8_WEIGHT_REFERENCE_GENERATED_ACTIVATION_SCALE_PENDING")
        self.assertEqual(generated["inputs"]["calibration"]["nonempty_line_count"], 2)
        self.assertEqual(generated["activation_calibration"]["status"], "NOT_EXECUTED")
        self.assertEqual(generated["package"]["sha256"], reference.sha256_file(output))
        self.assertIn("不代表 INT8 整网", summary.read_text(encoding="utf-8"))
        self.assertEqual(output.read_bytes()[:8], reference.PACKAGE_MAGIC)

    def test_truncated_weights_fail_closed(self) -> None:
        """截断权重不得生成可被误用的量化结果。"""

        self.weights.write_bytes(self.weights.read_bytes()[:-1])
        with self.assertRaises(reference.Int8WeightReferenceError):
            reference.parse_and_quantize(self.cfg, self.weights)


if __name__ == "__main__":
    unittest.main()
