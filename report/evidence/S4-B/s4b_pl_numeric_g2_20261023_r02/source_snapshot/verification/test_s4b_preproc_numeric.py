"""S4B PL数值核的独立离线参考单元检查。"""

from __future__ import annotations

import math
import random
import sys
import unittest
from pathlib import Path
from fractions import Fraction


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
import run_s4b_preproc_numeric as numeric


REFERENCE = ROOT / "report" / "evidence" / "S4-B" / "s4b_pl_preproc_numeric_20261023_r01" / "source_snapshot" / "s1_t02_d2_numeric_reference.py"
PIXEL_RTL = ROOT / "src" / "s4b_preproc_pixel.sv"
EXPECTED_REFERENCE_SHA256 = "6a3453d5bd60ab122c236667fbc9bcb5aa161d14b76bc7115b602743d5cbe54f"


class S4BPreprocNumericTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d2 = numeric.load_d2(REFERENCE.resolve(strict=True))
        cls.thresholds = numeric.generate_thresholds(cls.d2)

    def test_frozen_d2_binding_and_rom(self):
        self.assertEqual(numeric.sha256(REFERENCE), EXPECTED_REFERENCE_SHA256)
        self.assertEqual(numeric.parse_rtl_thresholds(PIXEL_RTL), self.thresholds)
        self.assertEqual(len(self.thresholds), 127)
        self.assertEqual(self.thresholds, sorted(set(self.thresholds)))

    def test_integer_rne_matches_ieee_binary64(self):
        rng = random.Random(numeric.SEED)
        for _ in range(5000):
            left = (rng.randrange(970, 1024) << 52) | rng.getrandbits(52)
            right = (rng.randrange(970, 1024) << 52) | rng.getrandbits(52)
            left_float = numeric.bits_to_float(left)
            right_float = numeric.bits_to_float(right)
            self.assertEqual(
                numeric.fp64_add_bits(left, right),
                numeric.float_to_bits(left_float + right_float),
            )
            self.assertEqual(
                numeric.fp64_mul_bits(left, right),
                numeric.float_to_bits(left_float * right_float),
            )

    def test_rne_ties_and_zero(self):
        one = numeric.ONE_BITS
        self.assertEqual(
            numeric.fp64_add_bits(one, numeric.float_to_bits(2.0 ** -53)), one
        )
        self.assertEqual(
            numeric.fp64_add_bits(one, numeric.float_to_bits(3.0 * 2.0 ** -53)),
            numeric.float_to_bits(1.0 + 2.0 ** -51),
        )
        self.assertEqual(numeric.fp64_add_bits(0, one), one)
        self.assertEqual(numeric.fp64_mul_bits(0x8000000000000000, one), 0)

    def test_rne_multiply_tie_add_carry_sticky_and_large_gap(self):
        self.assertEqual(
            numeric.fp64_mul_bits(0x3FF8000000000000, 0x3FF8000000000002),
            0x4002000000000002,
        )
        self.assertEqual(
            numeric.fp64_mul_bits(0x3FF8000000000000, 0x3FF8000000000000),
            0x4002000000000000,
        )
        self.assertEqual(
            numeric.fp64_add_bits(0x3FF8000000000000, 0x3FF8000000000000),
            0x4008000000000000,
        )
        self.assertEqual(
            numeric.fp64_add_bits(0x3FF0000000000000, 0x0010000000000000),
            0x3FF0000000000000,
        )
        self.assertEqual(
            numeric.fp64_add_bits(0x3FF0000000000000, 0x3CA8000000000000),
            0x3FF0000000000001,
        )

    def test_seeded_fp64_rtl_vectors_bind_each_result_and_error(self):
        cases, metadata = numeric.build_fp64_vector_cases()
        self.assertEqual(metadata["seed"], numeric.SEED ^ 0xF6402B)
        self.assertEqual(metadata["normal_or_zero_add_count"], 256)
        self.assertEqual(metadata["normal_or_zero_multiply_count"], 256)
        self.assertEqual(metadata["invalid_input_error_count"], 32)
        self.assertEqual(metadata["result_domain_error_count"], 3)
        self.assertEqual(metadata["total_count"], 547)
        self.assertEqual(cases, numeric.build_fp64_vector_cases()[0])

        last_successful_result = 0
        names = {str(case["name"]) for case in cases}
        for gap in (1, 52, 53, 54, 55, 56, 57, 60, 100, 500, 1022):
            self.assertIn(f"add_exponent_gap_{gap}", names)
        self.assertIn("add_halfway_even_down", names)
        self.assertIn("add_halfway_even_up", names)
        self.assertIn("mul_normalize_high", names)
        self.assertIn("mul_normalize_low", names)
        self.assertIn("mul_round_carry", names)
        carry_case = next(case for case in cases if case["name"] == "mul_round_carry")
        carry_a, carry_b = int(carry_case["a"]), int(carry_case["b"])
        carry_a_num, carry_a_den = numeric.bits_to_ratio(carry_a)
        carry_b_num, carry_b_den = numeric.bits_to_ratio(carry_b)
        self.assertLess(carry_a_num * carry_b_num, 2 * carry_a_den * carry_b_den)
        self.assertEqual(int(carry_case["expected_result"]), 0x4000000000000000)

        for case in cases:
            left, right = int(case["a"]), int(case["b"])
            is_add = bool(case["is_add"])
            expected_error = int(case["expected_error"])
            expected_code = int(case["expected_code"])
            expected_result = int(case["expected_result"])
            if expected_error == 0:
                reference = (
                    numeric.fp64_add_bits(left, right)
                    if is_add else numeric.fp64_mul_bits(left, right)
                )
                self.assertEqual(expected_code, 0)
                self.assertEqual(expected_result, reference)
                host_left, host_right = numeric.bits_to_float(left), numeric.bits_to_float(right)
                host_result = numeric.float_to_bits(
                    host_left + host_right if is_add else host_left * host_right
                )
                self.assertEqual(expected_result, host_result)
                last_successful_result = expected_result
            else:
                self.assertEqual(expected_result, last_successful_result)
                self.assertIn(expected_code, (1, 2))
                if expected_code == 1:
                    def rtl_input_supported(bits: int) -> bool:
                        exponent = (bits >> 52) & 0x7FF
                        fraction = bits & ((1 << 52) - 1)
                        return not (bits >> 63) and exponent != 0x7FF and (exponent != 0 or fraction == 0)

                    self.assertTrue(not rtl_input_supported(left) or not rtl_input_supported(right))
                else:
                    with self.assertRaises(ValueError):
                        numeric.fp64_add_bits(left, right) if is_add else numeric.fp64_mul_bits(left, right)

    def test_pixel_reference_preserves_202_by_329_boundary(self):
        pixels = (201, 202, 201, 202)
        weights = tuple(numeric.float_to_bits(value) for value in (
            *numeric.d2_resize_axis_weights(202, 255, 1),
            *numeric.d2_resize_axis_weights(329, 416, 0),
        ))
        actual_bits = numeric.pixel_integer_reference(pixels, weights)
        self.assertEqual(actual_bits, 0x40693952A54A952A)
        value = numeric.bits_to_float(actual_bits)
        direct_value = numeric._direct_d2_function_pixel(
            self.d2, 202, 329, 255, 416, 1, 0, pixels
        )
        self.assertEqual(numeric.float_to_bits(direct_value), actual_bits)
        self.assertEqual(
            numeric.float_to_bits(value / 255.0 / self.d2.INPUT_SCALE),
            numeric.float_to_bits(math.nextafter(100.5, -math.inf)),
        )
        self.assertEqual(Fraction(201 * 127, 254), Fraction(201, 2))
        self.assertEqual(numeric._d2_quantize_resized_value(self.d2, value), 100)

    def test_rom_neighbors_and_final_domain(self):
        checked = 0
        for code, threshold in enumerate(self.thresholds, start=1):
            self.assertEqual(
                numeric.threshold_quantize_bits(threshold - 1, self.thresholds), code - 1
            )
            self.assertEqual(
                numeric.threshold_quantize_bits(threshold, self.thresholds), code
            )
            for bits in (threshold - 1, threshold, threshold + 1):
                value = numeric.bits_to_float(bits)
                self.assertEqual(
                    numeric.threshold_quantize_bits(bits, self.thresholds),
                    numeric._d2_quantize_resized_value(self.d2, value),
                )
                checked += 1
        self.assertEqual(numeric.threshold_quantize_bits(0x8000000000000000, self.thresholds), 0)
        self.assertEqual(
            numeric.threshold_quantize_bits(numeric.float_to_bits(-0.5), self.thresholds), 0
        )
        self.assertEqual(numeric.threshold_quantize_bits(numeric.float_to_bits(256.0), self.thresholds), 127)
        for bits in (0x7FF0000000000000, 0xFFF0000000000000, 0x7FF8000000000001):
            with self.assertRaises(ValueError):
                numeric.threshold_quantize_bits(bits, self.thresholds)
        self.assertEqual(checked, 381)

    def test_geometry_coefficient_domain_and_padding_units(self):
        self.assertTrue(numeric.coefficient_supported_bits(0))
        self.assertTrue(numeric.coefficient_supported_bits(0x8000000000000000))
        self.assertTrue(numeric.coefficient_supported_bits(numeric.MIN_WEIGHT_BITS))
        self.assertTrue(numeric.coefficient_supported_bits(numeric.ONE_BITS))
        for bits in (
            numeric.MIN_WEIGHT_BITS - 1,
            0x0000000000000001,
            0xBFE0000000000000,
            0x4000000000000000,
            0x7FF0000000000000,
            0x7FF8000000000001,
        ):
            self.assertFalse(numeric.coefficient_supported_bits(bits))

        for source_dim in (1, 2, 202, 329, 1920, 3_686_400):
            for target_dim in (1, 2, 3, 255, 416):
                for coordinate in {0, target_dim - 1, min(1, target_dim - 1), target_dim // 2}:
                    for weight in numeric.d2_resize_axis_weights(source_dim, target_dim, coordinate):
                        if weight:
                            self.assertGreaterEqual(numeric.float_to_bits(weight), numeric.MIN_WEIGHT_BITS)

        self.assertEqual(self.d2.quantize_symmetric(0.5, self.d2.INPUT_SCALE), 64)
        self.assertEqual(numeric._d2_quantize_resized_value(self.d2, 0.5), 0)

    def test_d2_endpoint_coefficients(self):
        self.assertEqual(numeric.d2_resize_axis_weights(202, 1, 0), (1.0, 0.0))
        self.assertEqual(numeric.d2_resize_axis_weights(202, 255, 254), (1.0, 0.0))
        self.assertEqual(numeric.d2_resize_axis_weights(1, 416, 1), (1.0, 0.0))

    def test_fixed_seed_geometry_and_pixel_vectors(self):
        rng = random.Random(numeric.SEED ^ 0x534242)
        d2 = self.d2
        for _ in range(5):
            source_width = rng.randrange(2, 1921)
            source_height = rng.randrange(2, 1921)
            target_width = rng.randrange(2, 417)
            target_height = rng.randrange(2, 417)
            x = rng.randrange(0, target_width - 1)
            y = rng.randrange(0, target_height - 1)
            pixels = tuple(rng.randrange(256) for _ in range(4))
            weights = tuple(numeric.float_to_bits(value) for value in (
                *numeric.d2_resize_axis_weights(source_width, target_width, x),
                *numeric.d2_resize_axis_weights(source_height, target_height, y),
            ))
            self.assertTrue(all(numeric.coefficient_supported_bits(value) for value in weights))
            integer_result = numeric.pixel_integer_reference(pixels, weights)
            python_result = numeric.pixel_python_float_reference(pixels, weights)
            self.assertEqual(integer_result, python_result)
            self.assertEqual(
                numeric.threshold_quantize_bits(integer_result, self.thresholds),
                numeric._d2_quantize_resized_value(d2, numeric.bits_to_float(integer_result)),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
