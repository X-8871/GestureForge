import unittest

try:
    import s1_t02_d2_numeric_reference as ref
except ModuleNotFoundError:
    from verification import s1_t02_d2_numeric_reference as ref


class NumericReferenceTests(unittest.TestCase):
    def test_rounding_half_away_from_zero(self):
        values = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]
        self.assertEqual([ref.round_away_from_zero(value) for value in values], [-3, -2, -1, 1, 2, 3])

    def test_saturation_uses_project_range(self):
        self.assertEqual([ref.saturate_int8(value) for value in [-1000, -127, 0, 127, 1000]], [-127, -127, 0, 127, 127])

    def test_rgb_chw_order_and_input_scale(self):
        chw = ref.rgb_to_chw_255([[[255, 0, 128]]])
        self.assertEqual(chw[0][0][0], 1.0)
        self.assertEqual(chw[1][0][0], 0.0)
        self.assertAlmostEqual(chw[2][0][0], 128 / 255)
        self.assertEqual(ref.quantize_symmetric(0.5, ref.INPUT_SCALE), 64)

    def test_letterbox_odd_geometry_and_pad(self):
        geometry = ref.letterbox_geometry(4, 3, 7, 7)
        self.assertEqual((geometry["new_width"], geometry["new_height"]), (7, 5))
        self.assertEqual((geometry["offset_x"], geometry["offset_y"]), (0, 1))
        boxed = ref.letterbox_rgb_normalized([[[255, 0, 0]] * 4 for _ in range(3)], 7, 7)
        self.assertEqual(boxed[0][0], [0.5, 0.5, 0.5])

    def test_end_to_end_preprocess_without_and_with_padding(self):
        letterboxed_uint8 = ref.letterbox_rgb_uint8([[[255, 0, 0]], [[255, 0, 0]]], 4, 4)
        self.assertEqual(letterboxed_uint8[0][0], [128.0, 128.0, 128.0])
        self.assertEqual(ref.letterbox_rgb_normalized([[[255, 0, 0]], [[255, 0, 0]]], 4, 4)[0][0], [0.5, 0.5, 0.5])
        no_pad = ref.preprocess_rgb_uint8_to_chw_int8([[[255, 0, 128]]], 1, 1)
        self.assertEqual(no_pad, [[[127]], [[0]], [[64]]])
        with_pad = ref.preprocess_rgb_uint8_to_chw_int8([[[255, 0, 0]], [[255, 0, 0]]], 4, 4)
        self.assertEqual(with_pad[0][0][0], 64)
        self.assertEqual(with_pad[0][0][1], 127)
        self.assertEqual(with_pad[0][0][3], 64)
        self.assertEqual(with_pad[0][1][1], 127)
        self.assertEqual(with_pad[1][0][0], 64)
        self.assertEqual(with_pad[2][0][0], 64)

    def test_darknet_source_endpoint_for_one_by_one_resize(self):
        rgb = [
            [[5, 10, 15], [25, 30, 35]],
            [[45, 50, 55], [115, 120, 125]],
        ]
        resized = ref._resize_bilinear_rgb_values(rgb, 1, 1)
        self.assertEqual(resized, [[[115, 120, 125]]])
        self.assertEqual(
            ref.preprocess_rgb_uint8_to_chw_int8(rgb, 1, 1),
            [[[57]], [[60]], [[62]]],
        )

    def test_endpoint_is_used_in_padded_end_to_end_path(self):
        rgb = [[[5, 10, 15], [115, 120, 125]]]
        result = ref.preprocess_rgb_uint8_to_chw_int8(rgb, 3, 3)
        self.assertEqual(result[0][1], [2, 30, 57])
        self.assertEqual(result[1][1], [5, 32, 60])
        self.assertEqual(result[2][1], [7, 35, 62])
        self.assertEqual(result[0][0][0], 64)

    def test_per_channel_weights_and_per_layer_activation(self):
        quantized, scales = ref.quantize_weights_per_output_channel([[-2.0, 0.0, 2.0], [-0.5, 0.25, 0.5]])
        self.assertEqual(quantized[0], [-127, 0, 127])
        self.assertEqual(quantized[1], [-127, 64, 127])
        self.assertEqual(scales, [2.0 / 127, 0.5 / 127])
        activation, scale = ref.quantize_activation([0.0, -2.0, 1.0])
        self.assertEqual(activation, [0, -127, 64])
        self.assertEqual(scale, 2.0 / 127)
        zero, zero_scale = ref.quantize_activation([0.0, 0.0])
        self.assertEqual((zero, zero_scale), ([0, 0], ref.INPUT_SCALE))

    def test_bias_requant_and_accumulator_checks(self):
        weight_scale = 2.0 / 127
        self.assertEqual(ref.bias_to_accumulator([0.5], ref.INPUT_SCALE, [weight_scale]), [4032])
        self.assertEqual(ref.requantize_accumulator(64, ref.INPUT_SCALE, weight_scale, ref.INPUT_SCALE), 1)
        self.assertEqual(ref.int32_accumulate([1, -2, 3], bias=4), 6)
        self.assertEqual(ref.int64_dot([0], [0], bias=ref.INT64_MAX), ref.INT64_MAX)
        with self.assertRaises(OverflowError):
            ref.checked_int64(ref.INT64_MAX + 1)
        with self.assertRaises(OverflowError):
            ref.int64_dot([127, 1], [1, 1], bias=ref.INT64_MAX)
        with self.assertRaises(OverflowError):
            ref.checked_int32(ref.INT32_MAX + 1)

    def test_accumulator_inputs_reject_invalid_int8_values(self):
        for bad in [-128, 1.9, True]:
            with self.assertRaises((ValueError, TypeError, OverflowError)):
                ref.int64_dot([bad], [1])
            with self.assertRaises((ValueError, TypeError, OverflowError)):
                ref.int32_accumulate([bad])
        self.assertEqual(ref.int64_dot([-127, -2], [2, -3]), -248)

    def test_rejects_nonfinite_and_invalid_scale(self):
        with self.assertRaises(ValueError):
            ref.round_away_from_zero(float("nan"))
        with self.assertRaises(ValueError):
            ref.quantize_symmetric(1.0, 0.0)
        with self.assertRaises(ValueError):
            ref.rgb_to_chw_255([[[float("inf"), 0, 0]]])


if __name__ == "__main__":
    unittest.main()
