from decimal import Decimal, ROUND_HALF_UP
import unittest

import int8_mac_reference as ref


class ReferenceTests(unittest.TestCase):
    def test_rounding_and_saturation(self):
        # 遍历四项点积的整个整数范围，用十进制舍入独立核对。
        for acc in range(-65024, 65537):
            expected = int((Decimal(acc) / Decimal(256)).quantize(
                Decimal(1), rounding=ROUND_HALF_UP))
            self.assertEqual(ref.round_shift_8(acc), expected, acc)
            self.assertEqual(ref.saturate_int8(expected),
                             min(127, max(-128, expected)), acc)

    def test_golden_cases(self):
        cases = ref.build_cases()
        self.assertEqual(cases, ref.build_cases())
        self.assertEqual(len(cases), 25)
        for a, b, category in cases:
            result = ref.mac_reference(a, b)
            expected = sum(a[i] * b[i] for i in range(4))
            self.assertEqual(result['acc_exact'], expected, category)
            self.assertEqual(result['acc_hw'], expected, category)
        self.assertEqual(ref.mac_reference([-128] * 4, [-128] * 4)['acc_exact'], 65536)
        self.assertEqual(ref.mac_reference([-128] * 4, [127] * 4)['acc_exact'], -65024)

    def test_wrap_boundaries(self):
        for value, expected in [(128, -128), (129, -127), (-129, 127), (-130, 126)]:
            self.assertEqual(ref.wrap_signed(value, 8), expected)

    def test_invalid_input(self):
        for a in [[0] * 3, [128] * 4, [-129] * 4, [1.5] * 4, [True] * 4]:
            with self.assertRaises(ValueError):
                ref.mac_reference(a, [0] * 4)


if __name__ == '__main__':
    unittest.main()
