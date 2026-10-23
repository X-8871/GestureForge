"""S4B 单通道 PL 预处理核的离线数值与ROM生成检查。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path


TASK = "S4B-PL-PREPROC-NUMERIC-01"
SEED = 20261023
MAX_RAW_BYTES = 11_059_200
MIN_WEIGHT_BITS = 0x3CA0000000000000
ONE_BITS = 0x3FF0000000000000
MAX_255_BITS = 0x406FE00000000000


def sha256(path: Path) -> str:
    """计算文件原字节SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def float_to_bits(value: float) -> int:
    """将Python binary64按小端位型编码。"""
    return struct.unpack("<Q", struct.pack("<d", value))[0]


def bits_to_float(bits: int) -> float:
    """将binary64位型解码为Python浮点数。"""
    return struct.unpack("<d", struct.pack("<Q", bits))[0]


def _decode_nonnegative_finite(bits: int) -> tuple[int, int] | None:
    """返回精确的分子和分母指数，拒绝负数及非规格化输入。"""
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7FF
    fraction = bits & ((1 << 52) - 1)
    if exponent == 0x7FF:
        raise ValueError("仅支持非负有限binary64操作数")
    if sign:
        if exponent == 0 and fraction == 0:
            return None
        raise ValueError("仅支持非负有限binary64操作数")
    if exponent == 0:
        if fraction == 0:
            return None
        raise ValueError("参考算术的操作数不支持非规格化数")
    significand = (1 << 52) | fraction
    return significand, exponent - 1023 - 52


def _ratio_to_bits(numerator: int, denominator: int) -> int:
    """将非负有理数按IEEE 754 binary64 RNE编码。"""
    if numerator < 0 or denominator <= 0:
        raise ValueError("binary64参考只接收非负有理数")
    if numerator == 0:
        return 0

    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        if numerator < (denominator << exponent):
            exponent -= 1
    elif (numerator << -exponent) < denominator:
        exponent -= 1

    shift = 52 - exponent
    scaled_numerator = numerator << shift if shift >= 0 else numerator
    scaled_denominator = denominator if shift >= 0 else denominator << -shift
    quotient, remainder = divmod(scaled_numerator, scaled_denominator)
    twice_remainder = remainder << 1
    if twice_remainder > scaled_denominator or (
        twice_remainder == scaled_denominator and (quotient & 1)
    ):
        quotient += 1

    if quotient == (1 << 53):
        quotient >>= 1
        exponent += 1
    if exponent < -1022 or exponent > 1023:
        raise ValueError("binary64参考结果下溢或溢出")
    if quotient < (1 << 52) or quotient >= (1 << 53):
        raise AssertionError("RNE规格化结果超出有效数范围")
    return ((exponent + 1023) << 52) | (quotient - (1 << 52))


def bits_to_ratio(bits: int) -> tuple[int, int]:
    """把支持域内的binary64转换为精确正有理数。"""
    decoded = _decode_nonnegative_finite(bits)
    if decoded is None:
        return 0, 1
    significand, exponent = decoded
    if exponent >= 0:
        return significand << exponent, 1
    return significand, 1 << -exponent


def fp64_add_bits(left_bits: int, right_bits: int) -> int:
    """执行独立整数binary64加法参考。"""
    left_n, left_d = bits_to_ratio(left_bits)
    right_n, right_d = bits_to_ratio(right_bits)
    return _ratio_to_bits(left_n * right_d + right_n * left_d, left_d * right_d)


def fp64_mul_bits(left_bits: int, right_bits: int) -> int:
    """执行独立整数binary64乘法参考。"""
    left_n, left_d = bits_to_ratio(left_bits)
    right_n, right_d = bits_to_ratio(right_bits)
    return _ratio_to_bits(left_n * right_n, left_d * right_d)


def coefficient_supported_bits(bits: int) -> bool:
    """判断D2 416几何支持域内的有限非负系数。"""
    magnitude = bits & ((1 << 63) - 1)
    exponent = (bits >> 52) & 0x7FF
    if magnitude == 0:
        return True
    if bits >> 63 or exponent == 0 or exponent == 0x7FF:
        return False
    return MIN_WEIGHT_BITS <= magnitude <= ONE_BITS


def load_d2(reference_path: Path):
    """从显式冻结文件路径加载D2数值参考。"""
    spec = importlib.util.spec_from_file_location("s1_t02_d2_numeric_reference", reference_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法从显式路径加载D2参考")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if Path(module.__file__).resolve(strict=True) != reference_path.resolve(strict=True):
        raise RuntimeError("D2实际导入路径与显式路径不一致")
    return module


def d2_resize_axis_weights(source_dim: int, target_dim: int, coordinate: int) -> tuple[float, float]:
    """按D2端点规则生成单轴的binary64双线性系数。"""
    if source_dim <= 0 or target_dim <= 0 or not 0 <= coordinate < target_dim:
        raise ValueError("几何输入越界")
    if target_dim == 1 or coordinate == target_dim - 1:
        return 1.0, 0.0
    scale = (source_dim - 1) / (target_dim - 1)
    source_position = coordinate * scale
    source_index = int(source_position)
    fraction = source_position - source_index
    return 1.0 - fraction, fraction


def pixel_integer_reference(
    pixels: tuple[int, int, int, int], weights: tuple[int, int, int, int]
) -> int:
    """以独立有理数RNE逐操作复现D2九次运算。"""
    p00, p01, p10, p11 = pixels
    wx0, wx1, wy0, wy1 = weights
    pbits = tuple(float_to_bits(float(value)) for value in pixels)
    products = (
        fp64_mul_bits(wx0, pbits[0]),
        fp64_mul_bits(wx1, pbits[1]),
        fp64_mul_bits(wx0, pbits[2]),
        fp64_mul_bits(wx1, pbits[3]),
    )
    row0 = fp64_add_bits(products[0], products[1])
    row1 = fp64_add_bits(products[2], products[3])
    weighted0 = fp64_mul_bits(wy0, row0)
    weighted1 = fp64_mul_bits(wy1, row1)
    return fp64_add_bits(weighted0, weighted1)


def pixel_python_float_reference(
    pixels: tuple[int, int, int, int], weights: tuple[int, int, int, int]
) -> int:
    """以Python binary64逐操作计算D2顺序，用于交叉核对整数参考。"""
    p00, p01, p10, p11 = pixels
    wx0, wx1, wy0, wy1 = (bits_to_float(value) for value in weights)
    top = wx0 * float(p00) + wx1 * float(p01)
    bottom = wx0 * float(p10) + wx1 * float(p11)
    result = wy0 * top + wy1 * bottom
    return float_to_bits(result)


def _d2_quantize_resized_value(d2, value: float) -> int:
    """执行冻结D2插值结果的归一化、夹紧和量化。"""
    normalized = max(0.0, min(1.0, d2._finite(value, "resized_rgb") / 255.0))
    return d2.quantize_symmetric(normalized, d2.INPUT_SCALE)


def generate_thresholds(d2) -> list[int]:
    """以有序binary64位型二分冻结D2的127条最小跳变边界。"""
    low_bits = float_to_bits(0.0)
    high_bits = float_to_bits(255.0)
    thresholds: list[int] = []
    for output_code in range(1, 128):
        left, right = low_bits, high_bits
        while left < right:
            middle = (left + right) // 2
            if _d2_quantize_resized_value(d2, bits_to_float(middle)) >= output_code:
                right = middle
            else:
                left = middle + 1
        if _d2_quantize_resized_value(d2, bits_to_float(left)) != output_code:
            raise AssertionError(f"D2输出码{output_code}没有唯一下界")
        if _d2_quantize_resized_value(d2, bits_to_float(left - 1)) != output_code - 1:
            raise AssertionError(f"D2输出码{output_code}前一位型不是前一码")
        thresholds.append(left)
    if len(thresholds) != 127 or thresholds != sorted(set(thresholds)):
        raise AssertionError("D2阈值表不是127个严格递增边界")
    return thresholds


def threshold_quantize_bits(bits: int, thresholds: list[int]) -> int:
    """对D2非负插值值按ROM执行量化；负值夹到零，非有限值拒绝。"""
    sign = bits >> 63
    exponent = (bits >> 52) & 0x7FF
    fraction = bits & ((1 << 52) - 1)
    if exponent == 0x7FF:
        raise ValueError("D2有限输入要求拒绝NaN和Inf")
    if sign:
        if (bits & ((1 << 63) - 1)) == 0:
            return 0
        return 0
    if exponent == 0 and fraction == 0:
        return 0
    if bits >= MAX_255_BITS:
        return 127
    low, high = 0, len(thresholds)
    while low < high:
        middle = (low + high) // 2
        if thresholds[middle] <= bits:
            low = middle + 1
        else:
            high = middle
    return low


def parse_rtl_thresholds(pixel_rtl: Path) -> list[int]:
    """解析RTL case ROM并返回按索引排序的边界。"""
    text = pixel_rtl.read_text(encoding="utf-8")
    pairs = [(int(index), int(value, 16)) for index, value in re.findall(
        r"7'd(\d+):\s*threshold_at\s*=\s*64'h([0-9a-fA-F]{16})", text
    )]
    if [index for index, _ in pairs] != list(range(127)):
        raise AssertionError("RTL阈值ROM索引不完整或有重复")
    return [value for _, value in pairs]


def _axis_vector(d2, source_width: int, source_height: int, target_width: int,
                 target_height: int, x: int, y: int,
                 pixels: tuple[int, int, int, int]) -> tuple[tuple[int, ...], tuple[int, ...], float]:
    """构建D2端点系数及四邻点向量。"""
    wx0, wx1 = d2_resize_axis_weights(source_width, target_width, x)
    wy0, wy1 = d2_resize_axis_weights(source_height, target_height, y)
    weights = tuple(float_to_bits(value) for value in (wx0, wx1, wy0, wy1))
    value_bits = pixel_integer_reference(pixels, weights)
    direct_bits = pixel_python_float_reference(pixels, weights)
    if value_bits != direct_bits:
        raise AssertionError("整数binary64参考与Python binary64参考不一致")
    return weights, pixels, bits_to_float(value_bits)


def _direct_d2_function_pixel(d2, source_width: int, source_height: int,
                             target_width: int, target_height: int,
                             x: int, y: int,
                             pixels: tuple[int, int, int, int]) -> float:
    """调用冻结D2整幅resize函数取得指定通道结果。"""
    if source_width < 2 or source_height < 2:
        raise ValueError("直接D2函数回归需要2x2以上源图")
    image = [[[0, 0, 0] for _ in range(source_width)] for _ in range(source_height)]
    p00, p01, p10, p11 = pixels
    image[0][0] = [p00, p00, p00]
    image[0][1] = [p01, p01, p01]
    image[1][0] = [p10, p10, p10]
    image[1][1] = [p11, p11, p11]
    resized = d2._resize_bilinear_rgb_values(image, target_width, target_height)
    return resized[y][x][0]


def _make_vector_line(expected: int, pixels: tuple[int, int, int, int],
                      weights: tuple[int, int, int, int]) -> str:
    """生成XSim testbench读取的一行十六进制测试向量。"""
    fields = [f"{expected:02x}", *(f"{value:02x}" for value in pixels),
              *(f"{value:016x}" for value in weights)]
    return " ".join(fields)


def _normal_bits(exponent_field: int, fraction: int) -> int:
    """组装正规格化binary64位型。"""
    if not 1 <= exponent_field <= 2046 or not 0 <= fraction < (1 << 52):
        raise ValueError("规格化binary64字段越界")
    return (exponent_field << 52) | fraction


def build_fp64_vector_cases(per_op: int = 256) -> tuple[list[dict[str, int | str]], dict[str, object]]:
    """构造独立整数RNE参考的FP64运算和拒绝用例。"""
    if per_op < 64:
        raise ValueError("每种运算至少需要64条用例以容纳固定边界类别")
    rng = random.Random(SEED ^ 0xF6402B)
    cases: list[dict[str, int | str]] = []

    add_specs: list[tuple[str, int, int]] = [
        ("add_zero_zero", 0, 0),
        ("add_zero_identity", 0, ONE_BITS),
        ("add_identity_zero", ONE_BITS, 0),
        ("add_equal_exponent", _normal_bits(1022, 0x0123456789ABC),
         _normal_bits(1022, 0x76543210FEDCB)),
        ("add_halfway_even_down", ONE_BITS, 0x3CA0000000000000),
        ("add_halfway_even_up", 0x3FF0000000000001, 0x3CA0000000000000),
        ("add_sticky_round_up", ONE_BITS, 0x3CA8000000000000),
        ("add_normalize_carry", 0x3FF8000000000000, 0x3FF8000000000000),
        ("add_round_carry", 0x3FFFFFFFFFFFFFFF, 0x3CA0000000000000),
    ]
    for gap in (1, 2, 52, 53, 54, 55, 56, 57, 60, 100, 500, 1022):
        high_exp = 1023
        low_exp = high_exp - gap
        add_specs.append((f"add_exponent_gap_{gap}", ONE_BITS,
                          _normal_bits(low_exp, rng.getrandbits(52))))
    add_cases: list[tuple[str, int, int]] = add_specs[:]
    while len(add_cases) < per_op:
        category = len(add_cases) % 5
        if category == 0:
            exponent = rng.randrange(1, 1023)
            left = _normal_bits(exponent, rng.getrandbits(52))
            right = _normal_bits(exponent, rng.getrandbits(52))
        elif category == 1:
            high_exp = rng.randrange(53, 1024)
            gap = rng.choice((1, 2, 52, 53, 54, 55, 56, 60, 100, 500, high_exp - 1))
            gap = min(gap, high_exp - 1)
            left = _normal_bits(high_exp, rng.getrandbits(52))
            right = _normal_bits(high_exp - gap, rng.getrandbits(52))
        elif category == 2:
            left = _normal_bits(rng.randrange(1, 1023), rng.getrandbits(52))
            right = 0
        elif category == 3:
            left = 0
            right = _normal_bits(rng.randrange(1, 1023), rng.getrandbits(52))
        else:
            left = _normal_bits(rng.randrange(1, 1023), rng.getrandbits(52))
            right = _normal_bits(rng.randrange(1, 1023), rng.getrandbits(52))
        add_cases.append((f"add_seeded_{len(add_cases):03d}", left, right))

    mul_specs: list[tuple[str, int, int]] = [
        ("mul_zero_zero", 0, 0),
        ("mul_zero_identity", 0, ONE_BITS),
        ("mul_identity_zero", ONE_BITS, 0),
        ("mul_identity", ONE_BITS, ONE_BITS),
        ("mul_normalize_high", 0x3FF8000000000000, 0x3FF8000000000000),
        ("mul_normalize_low", ONE_BITS, ONE_BITS),
        ("mul_tie_even", 0x3FF8000000000000, 0x3FF0000000000001),
        ("mul_round_carry", 0x3FF6A09E667F37CD, 0x3FF6A09E667F3FCC),
    ]
    mul_cases: list[tuple[str, int, int]] = mul_specs[:]
    while len(mul_cases) < per_op:
        if len(mul_cases) % 4 == 0:
            # 固定指数和，让乘积最高位在归一化边界两侧变化。
            left_exp = 1022
            right_exp = 1024
        elif len(mul_cases) % 4 == 1:
            left_exp = rng.randrange(1, 1024)
            min_right = max(1, 1024 - left_exp)
            max_right = min(2046, 2045 - left_exp)
            if min_right > max_right:
                continue
            right_exp = rng.randrange(min_right, max_right + 1)
        elif len(mul_cases) % 4 == 2:
            left_exp = rng.randrange(1, 1024)
            right_exp = 1023
        else:
            left_exp = 1023
            right_exp = rng.randrange(1, 1024)
        left = _normal_bits(left_exp, rng.getrandbits(52))
        right = _normal_bits(right_exp, rng.getrandbits(52))
        mul_cases.append((f"mul_seeded_{len(mul_cases):03d}", left, right))

    expected_result = 0

    def append_success(name: str, is_add: bool, left: int, right: int) -> None:
        nonlocal expected_result
        integer_result = fp64_add_bits(left, right) if is_add else fp64_mul_bits(left, right)
        host_left, host_right = bits_to_float(left), bits_to_float(right)
        host_value = host_left + host_right if is_add else host_left * host_right
        if float_to_bits(host_value) != integer_result:
            raise AssertionError(f"整数RNE与Python binary64不一致：{name}")
        expected_result = integer_result
        cases.append({
            "name": name, "is_add": int(is_add), "a": left, "b": right,
            "expected_error": 0, "expected_code": 0, "expected_result": expected_result,
        })

    for name, left, right in add_cases:
        append_success(name, True, left, right)
    for name, left, right in mul_cases:
        append_success(name, False, left, right)

    invalid_operands = (
        0x8000000000000000, 0xBFF0000000000000,
        0x0000000000000001, 0x000FFFFFFFFFFFFF,
        0x7FF0000000000000, 0xFFF0000000000000,
        0x7FF8000000000001, 0x7FF0000000000001,
    )
    for operation in (True, False):
        for operand_position in (0, 1):
            for invalid in invalid_operands:
                left, right = (invalid, ONE_BITS) if operand_position == 0 else (ONE_BITS, invalid)
                cases.append({
                    "name": f"invalid_input_{len(cases):03d}", "is_add": int(operation),
                    "a": left, "b": right, "expected_error": 1,
                    "expected_code": 1, "expected_result": expected_result,
                })

    result_domain_cases = (
        ("add_result_overflow", True, 0x7FEFFFFFFFFFFFFF, 0x7FEFFFFFFFFFFFFF),
        ("mul_result_underflow", False, 0x0010000000000000, 0x3FE0000000000000),
        ("mul_result_overflow", False, 0x7FEFFFFFFFFFFFFF, 0x4000000000000000),
    )
    for name, is_add, left, right in result_domain_cases:
        try:
            value = fp64_add_bits(left, right) if is_add else fp64_mul_bits(left, right)
        except ValueError:
            cases.append({
                "name": name, "is_add": int(is_add), "a": left, "b": right,
                "expected_error": 2, "expected_code": 2, "expected_result": expected_result,
            })
        else:
            raise AssertionError(f"应拒绝超出FP64结果域的用例：{name} => {value:016x}")

    metadata = {
        "seed": SEED ^ 0xF6402B,
        "normal_or_zero_add_count": len(add_cases),
        "normal_or_zero_multiply_count": len(mul_cases),
        "invalid_input_error_count": len(invalid_operands) * 4,
        "result_domain_error_count": len(result_domain_cases),
        "total_count": len(cases),
        "coverage_classes": [
            "正规格化数与正零加法/乘法", "相同指数和指数差1/52/53/54/55/56/57/60/100/500/1022",
            "tie-to-even偶/奇保留位", "乘积归一化最高位两种状态", "乘法尾数舍入进位至2.0", "GRS sticky与大指数差",
            "负零/负有限/非规格数/NaN/Inf输入拒绝", "加法溢出及乘法上下溢拒绝",
        ],
        "result_policy": "每条逐位比较64位result、done、error和error_code；error时result必须保持最近一次成功值。",
    }
    return cases, metadata


def run_checks(reference_path: Path, pixel_rtl: Path, output_dir: Path) -> dict[str, object]:
    """生成RTL ROM向量并完成轻量独立数值检查。"""
    reference_path = reference_path.resolve(strict=True)
    pixel_rtl = pixel_rtl.resolve(strict=True)
    output_dir = output_dir.resolve(strict=True)
    d2 = load_d2(reference_path)
    thresholds = generate_thresholds(d2)
    if parse_rtl_thresholds(pixel_rtl) != thresholds:
        raise AssertionError("RTL阈值ROM与冻结D2重新生成结果不同")

    rng = random.Random(SEED)
    fp_ops = 20_000
    for _ in range(fp_ops):
        exp_a = rng.randrange(970, 1024)
        exp_b = rng.randrange(970, 1024)
        left = (exp_a << 52) | rng.getrandbits(52)
        right = (exp_b << 52) | rng.getrandbits(52)
        left_float, right_float = bits_to_float(left), bits_to_float(right)
        if fp64_add_bits(left, right) != float_to_bits(left_float + right_float):
            raise AssertionError("整数RNE加法与IEEE binary64结果不一致")
        if fp64_mul_bits(left, right) != float_to_bits(left_float * right_float):
            raise AssertionError("整数RNE乘法与IEEE binary64结果不一致")

    one = ONE_BITS
    half_ulp = float_to_bits(2.0 ** -53)
    tie_even_cases = {
        "add_halfway_even_down": (fp64_add_bits(one, half_ulp), one),
        "add_halfway_even_up": (
            fp64_add_bits(one, float_to_bits(3.0 * 2.0 ** -53)),
            float_to_bits(1.0 + 2.0 ** -51),
        ),
    }
    for name, (actual, expected) in tie_even_cases.items():
        if actual != expected:
            raise AssertionError(f"RNE舍入中点样例错误：{name}")
    explicit_rne_cases = {
        "multiply_exact_midpoint_even": (
            False, 0x3FF8000000000000, 0x3FF8000000000002, 0x4002000000000002,
        ),
        "multiply_normalize_carry": (
            False, 0x3FF8000000000000, 0x3FF8000000000000, 0x4002000000000000,
        ),
        "add_normalize_carry": (
            True, 0x3FF8000000000000, 0x3FF8000000000000, 0x4008000000000000,
        ),
        "add_tie_even_down": (
            True, 0x3FF0000000000000, 0x3CA0000000000000, 0x3FF0000000000000,
        ),
        "add_sticky_round_up": (
            True, 0x3FF0000000000000, 0x3CA8000000000000, 0x3FF0000000000001,
        ),
        "add_large_exponent_gap": (
            True, 0x3FF0000000000000, 0x0010000000000000, 0x3FF0000000000000,
        ),
    }
    for name, (is_add, left, right, expected) in explicit_rne_cases.items():
        actual = fp64_add_bits(left, right) if is_add else fp64_mul_bits(left, right)
        host_left, host_right = bits_to_float(left), bits_to_float(right)
        host_result = float_to_bits(host_left + host_right if is_add else host_left * host_right)
        if actual != expected or host_result != expected:
            raise AssertionError(f"RNE手算样例错误：{name}")

    threshold_checks = 0
    for index, threshold in enumerate(thresholds, start=1):
        for bits in (threshold - 1, threshold, threshold + 1):
            expected = _d2_quantize_resized_value(d2, bits_to_float(bits))
            actual = threshold_quantize_bits(bits, thresholds)
            if actual != expected:
                raise AssertionError(f"阈值相邻位型不等价：{bits:016x}")
            threshold_checks += 1
    for code in range(256):
        probes = (float(code),) if code == 255 else (
            float(code), code + 0.5,
            math.nextafter(code + 0.5, -math.inf),
            math.nextafter(code + 0.5, math.inf),
        )
        for value in probes:
            bits = float_to_bits(value)
            if threshold_quantize_bits(bits, thresholds) != _d2_quantize_resized_value(d2, value):
                raise AssertionError(f"整数/半整数量化路径不等价：{value.hex()}")
            threshold_checks += 1
    for _ in range(10_000):
        value_bits = rng.randrange(float_to_bits(0.0), float_to_bits(255.0) + 1)
        value = bits_to_float(value_bits)
        if threshold_quantize_bits(value_bits, thresholds) != _d2_quantize_resized_value(d2, value):
            raise AssertionError("固定种子随机阈值检查不等价")
        threshold_checks += 1

    if threshold_quantize_bits(0x8000000000000000, thresholds) != 0:
        raise AssertionError("负零必须量化为0")
    if threshold_quantize_bits(float_to_bits(-0.5), thresholds) != 0:
        raise AssertionError("D2夹紧路径中的有限负值必须量化为0")
    if threshold_quantize_bits(float_to_bits(256.0), thresholds) != 127:
        raise AssertionError("有限大于255的值必须饱和到127")
    for invalid in (0x7FF0000000000000, 0xFFF0000000000000, 0x7FF8000000000001):
        try:
            threshold_quantize_bits(invalid, thresholds)
        except ValueError:
            pass
        else:
            raise AssertionError("量化参考必须拒绝非有限输入")

    vector_cases: list[tuple[str, tuple[int, int, int, int], tuple[int, int, int, int], int]] = []

    # D2 的202x329到255x416样例在x=1处跨越有理数101的量化边界。
    pixels = (201, 202, 201, 202)
    weights, _, value = _axis_vector(d2, 202, 329, 255, 416, 1, 0, pixels)
    direct_quantized = _d2_quantize_resized_value(d2, value)
    direct_function_value = _direct_d2_function_pixel(d2, 202, 329, 255, 416, 1, 0, pixels)
    if float_to_bits(direct_function_value) != float_to_bits(value):
        raise AssertionError("D2整幅resize函数与独立逐操作参考不一致")
    if value.hex() != float.fromhex("0x1.93952a54a952ap+7").hex() or direct_quantized != 100:
        raise AssertionError("D2 202x329 半边界回归样例发生变化")
    d2_scaled = value / 255.0 / d2.INPUT_SCALE
    if float_to_bits(d2_scaled) != float_to_bits(math.nextafter(100.5, -math.inf)):
        raise AssertionError("半边界样例必须落在D2 binary64 100.5阈值下方")
    exact_rational_scaled = Fraction(201 * 127, 254)
    if exact_rational_scaled != Fraction(201, 2):
        raise AssertionError("手算理想rational样例不是101/2")
    vector_cases.append(("d2_202x329_boundary_100", pixels, weights, direct_quantized))

    # 全零、全255和端点复制覆盖两个快速零乘及饱和路径。
    one_zero = (ONE_BITS, 0, ONE_BITS, 0)
    vector_cases.append(("zero", (0, 0, 0, 0), one_zero, 0))
    vector_cases.append(("max255", (255, 255, 255, 255), one_zero, 127))
    end_weights, _, end_value = _axis_vector(d2, 5, 3, 7, 5, 6, 4, (11, 99, 21, 201))
    vector_cases.append(("last_row_column", (11, 99, 21, 201), end_weights,
                         _d2_quantize_resized_value(d2, end_value)))
    signed_zero_weights = (ONE_BITS, 0x8000000000000000, ONE_BITS, 0)
    vector_cases.append(("signed_zero_coeff", (42, 12, 42, 12), signed_zero_weights, 21))

    pixel_rng = random.Random(SEED ^ 0x534242)
    for vector_index in range(5):
        source_width = pixel_rng.randrange(2, 1921)
        source_height = pixel_rng.randrange(2, 1921)
        target_width = pixel_rng.randrange(2, 417)
        target_height = pixel_rng.randrange(2, 417)
        x = pixel_rng.randrange(0, target_width - 1)
        y = pixel_rng.randrange(0, target_height - 1)
        random_pixels = tuple(pixel_rng.randrange(256) for _ in range(4))
        random_weights, _, random_value = _axis_vector(
            d2, source_width, source_height, target_width, target_height,
            x, y, random_pixels,
        )
        if not all(coefficient_supported_bits(value) for value in random_weights):
            raise AssertionError("固定种子随机几何系数不在PL支持域")
        vector_cases.append((f"seeded_geometry_{vector_index}", random_pixels,
                             random_weights, _d2_quantize_resized_value(d2, random_value)))

    vector_lines: list[str] = []
    direct_vectors = []
    for name, pixels, weights, expected in vector_cases:
        integer_bits = pixel_integer_reference(pixels, weights)
        python_bits = pixel_python_float_reference(pixels, weights)
        if integer_bits != python_bits:
            raise AssertionError(f"测试向量双重参考不一致：{name}")
        direct_expected = _d2_quantize_resized_value(d2, bits_to_float(integer_bits))
        if direct_expected != expected:
            raise AssertionError(f"测试向量量化结果与冻结D2不一致：{name}")
        vector_lines.append(_make_vector_line(expected, pixels, weights))
        direct_vectors.append({
            "name": name,
            "pixels": list(pixels),
            "weights_hex": [f"0x{value:016x}" for value in weights],
            "interpolation_hex": f"0x{integer_bits:016x}",
            "expected_int8": expected,
        })

    # 归一化补边0.5直接量化为64；raw像素核心只接收0..255插值单位。
    padding_normalized = 0.5
    padding_quantized = d2.quantize_symmetric(padding_normalized, d2.INPUT_SCALE)
    raw_half_quantized = _d2_quantize_resized_value(d2, 0.5)
    if padding_quantized != 64 or raw_half_quantized != 0:
        raise AssertionError("归一化补边与raw像素量化单位混淆")

    min_nonzero_weight = float("inf")
    geometry_samples = 0
    source_dims = (1, 2, 3, 202, 329, 1920, 3_686_400)
    for source_dim in source_dims:
        for target_dim in (1, 2, 3, 255, 416):
            if target_dim <= 0:
                continue
            coords = {0, target_dim - 1, min(1, target_dim - 1), max(0, target_dim // 2)}
            for coordinate in coords:
                weights = d2_resize_axis_weights(source_dim, target_dim, coordinate)
                for weight in weights:
                    if weight:
                        bits = float_to_bits(weight)
                        if bits < MIN_WEIGHT_BITS:
                            raise AssertionError("合法几何系数低于支持域下界2^-53")
                        min_nonzero_weight = min(min_nonzero_weight, weight)
                geometry_samples += 1

    coeff_bound_proof = (
        "原始RGB最大帧字节数11059200且三通道8-bit，任一源边<=3686400；输出边<=416。"
        "newdim==1或最后坐标的D2系数为0/1。其余位置t*(N-1)/(D)的精确非整数分数部分及补数至少1/415；"
        "N<=3686400,D<=415,t<=414。binary64先做一次除法再做一次乘法，按每步最大0.5ULP、"
        "中间位置小于2^31计算，累计绝对误差小于2^-20，远小于1/415，故任何非零权重都大于2^-53。"
        "像素乘积最小2^-53、第二级加权乘积最小2^-106，均为normal；行和<=510、末级和<=1020。"
    )

    vector_path = output_dir / "preproc_vectors.hex"
    if vector_path.exists():
        raise FileExistsError(f"拒绝覆盖测试向量：{vector_path}")
    vector_path.write_text("\n".join(vector_lines) + "\n", encoding="ascii", newline="\n")

    fp64_cases, fp64_metadata = build_fp64_vector_cases()
    fp64_vector_path = output_dir / "fp64_vectors.hex"
    if fp64_vector_path.exists():
        raise FileExistsError(f"拒绝覆盖FP64测试向量：{fp64_vector_path}")
    fp64_lines = [str(len(fp64_cases))]
    for case in fp64_cases:
        fp64_lines.append(" ".join((
            f"{case['is_add']:x}", f"{case['a']:016x}", f"{case['b']:016x}",
            f"{case['expected_result']:016x}", f"{case['expected_error']:x}",
            f"{case['expected_code']:x}",
        )))
    fp64_vector_path.write_text("\n".join(fp64_lines) + "\n", encoding="ascii", newline="\n")

    result: dict[str, object] = {
        "schema_version": 1,
        "task": TASK,
        "status": "OFFLINE_NUMERIC_REFERENCE_PASS_RTL_SIM_PENDING",
        "hardware": "NOT_RUN",
        "synthesis": "NOT_RUN",
        "sources": {
            "d2_reference": {"path": str(reference_path), "sha256": sha256(reference_path)},
            "fp64_rtl": {"path": str((pixel_rtl.parent / "s4b_preproc_fp64.sv").resolve()),
                         "sha256": sha256((pixel_rtl.parent / "s4b_preproc_fp64.sv").resolve(strict=True))},
            "pixel_rtl": {"path": str(pixel_rtl), "sha256": sha256(pixel_rtl)},
        },
        "quantizer_rom": {
            "threshold_count": len(thresholds),
            "threshold_hex_bits": [f"0x{value:016x}" for value in thresholds],
            "source_semantics": "冻结D2 binary64 v/255 -> clamp[0,1] -> 除以binary64(1/127) -> floor(abs(x)+0.5) -> 饱和[-127,127]",
            "binary_search_domain": "非负有限binary64位型[0.0,255.0]",
            "monotonicity_basis": "正binary64有序位型随实数单调；D2的除法、正scale除法、floor与饱和对非负输入单调；每一码由全序位型二分取得最小跳变点。",
            "boundary_neighbor_checks": threshold_checks,
            "direct_d2_resize_function": {
                "sample": "202x329 -> resize255x416 at x=1,y=0, channel0",
                "value_hex": f"0x{float_to_bits(direct_function_value):016x}",
                "quantized": direct_quantized,
                "exact_rational_scaled": str(exact_rational_scaled),
                "exact_rational_round_away": 101,
                "frozen_d2_binary64_scaled_hex": f"0x{float_to_bits(d2_scaled):016x}",
            },
            "rtl_rom_matches_rederived_d2": True,
            "finite_negative_and_signed_zero": "D2末端夹紧映射0；像素核对外系数负值显式报错，支持域内插值结果不能为负。",
            "finite_above_255": 127,
            "nonfinite": "拒绝",
        },
        "fp64_reference": {
            "rounding": "精确整数有理数RNE， ties-to-even",
            "operation_count": fp_ops,
            "seed": SEED,
            "add_tie_cases": {name: {"actual": f"0x{actual:016x}", "expected": f"0x{expected:016x}"}
                              for name, (actual, expected) in tie_even_cases.items()},
            "explicit_mul_add_cases": {
                name: {"operation": "add" if is_add else "multiply",
                       "a": f"0x{left:016x}", "b": f"0x{right:016x}",
                       "expected": f"0x{expected:016x}"}
                for name, (is_add, left, right, expected) in explicit_rne_cases.items()
            },
            "unsupported_operands": "负数、NaN/Inf、subnormal显式拒绝；正零支持",
            "rtl_vector_suite": fp64_metadata,
        },
        "geometry_domain": {
            "minimum_weight_bits": f"0x{MIN_WEIGHT_BITS:016x}",
            "minimum_nonzero_weight_sampled": min_nonzero_weight,
            "sampled_source_dimensions": list(source_dims),
            "sampled_geometry_cases": geometry_samples,
            "bound_reasoning": coeff_bound_proof,
            "input_coefficient_policy": "正零、负零、[2^-53,1]；其他负数、非有限数、subnormal或更小正数显式报错。",
        },
        "vectors": direct_vectors,
        "seeded_pixel_vectors": {
            "seed": SEED ^ 0x534242,
            "count": 5,
            "basis": "固定种子随机合法源/目标维度、目标坐标、8-bit四邻像素；D2端点规则生成binary64权重。",
        },
        "padding": {
            "normalized_input": 0.5,
            "expected_int8": padding_quantized,
            "raw_pixel_value_0_255_unit": 0.5,
            "raw_pixel_unit_quantized_int8": raw_half_quantized,
            "interpretation": "补边在归一化域直接产生64，不得将raw 0.5送入插值/阈值ROM。",
        },
        "estimated_cycles": {
            "six_53_iterative_multiplications": 6 * 54,
            "three_fp64_additions_upper_estimate": 3 * 5,
            "top_state_and_quantizer_estimate_per_channel": 32,
            "estimated_cycles_per_channel": 6 * 54 + 3 * 5 + 32,
            "basis": "结构估算，等待XSim周期测量；未综合、未测Fmax、资源和板上吞吐。",
        },
        "artifacts": {
            "vectors": str(vector_path), "vectors_sha256": sha256(vector_path),
            "fp64_vectors": str(fp64_vector_path),
            "fp64_vectors_sha256": sha256(fp64_vector_path),
        },
    }
    result_path = output_dir / "numeric_reference_result.json"
    if result_path.exists():
        raise FileExistsError(f"拒绝覆盖数值结果：{result_path}")
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


def main() -> int:
    """执行离线参考检查并生成XSim输入向量。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--pixel-rtl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = run_checks(args.reference, args.pixel_rtl, args.output_dir)
    except Exception as exc:
        print(f"NUMERIC_REFERENCE_FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": result["status"],
        "thresholds": result["quantizer_rom"]["threshold_count"],
        "fp64_reference_operations": result["fp64_reference"]["operation_count"],
        "vectors": len(result["vectors"]),
        "fp64_vectors": result["fp64_reference"]["rtl_vector_suite"]["total_count"],
        "evidence": result["artifacts"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
