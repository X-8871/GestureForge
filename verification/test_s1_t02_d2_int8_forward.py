"""S1-T02-D2 整数前向参考器的确定性单元测试。"""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verification.s1_t02_d2_int8_forward import (
    INT8_MAX,
    INT8_MIN,
    PackageLayer,
    Tensor,
    conv_int8,
    rescale_tensor,
    round_away_array,
    saturate_array,
)


class Int8ForwardTest(unittest.TestCase):
    """覆盖舍入、重定标和卷积累加器语义。"""

    def test_rounding_and_saturation_are_symmetric(self) -> None:
        values = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5], dtype=np.float64)
        self.assertEqual(round_away_array(values).tolist(), [-3, -2, -1, 1, 2, 3])
        self.assertEqual(
            saturate_array(np.array([-1000, -127, 0, 127, 1000])).tolist(),
            [INT8_MIN, INT8_MIN, 0, INT8_MAX, INT8_MAX],
        )

    def test_route_rescale_uses_maximum_input_scale(self) -> None:
        source = Tensor(np.array([[[127, -127]]], dtype=np.int8), 0.5)
        result = rescale_tensor(source, 1.0)
        self.assertEqual(result.scale, 1.0)
        self.assertEqual(result.values.tolist(), [[[64, -64]]])


    def test_integer_convolution_tracks_accumulator_without_overflow(self) -> None:
        layer = PackageLayer(
            layer_index=0,
            filters=1,
            input_channels=1,
            groups=1,
            size=1,
            weight_count=1,
            weight_scales=np.array([0.5], dtype=np.float64),
            fused_biases=np.array([0.5], dtype=np.float64),
            quantized_weights=np.array([[[[2]]]], dtype=np.int8),
        )
        result, stats = conv_int8(Tensor(np.array([[[3]]], dtype=np.int8), 0.25), layer, 0.5, "linear", 1)
        self.assertEqual(result.values.tolist(), [[[3]]])
        self.assertEqual(stats["int32_overflow_count"], 0)
        self.assertEqual(stats["accumulator_with_bias_min"], 10)
