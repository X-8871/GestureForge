from __future__ import annotations

import json
import random
from pathlib import Path


LANES = 4
DATA_WIDTH = 8
PRODUCT_WIDTH = 2 * DATA_WIDTH
ACC_WIDTH = PRODUCT_WIDTH + 2
OUTPUT_WIDTH = 8
OUTPUT_SHIFT = 8
RANDOM_SEED = 20260907
RESULT_PATH = Path(__file__).parent / "sim_results" / "int8_mac_golden.json"


def signed_range(width: int) -> tuple[int, int]:
    minimum = -(1 << (width - 1))
    maximum = (1 << (width - 1)) - 1
    return minimum, maximum


def wrap_signed(value: int, width: int) -> int:
    mask = (1 << width) - 1
    wrapped = value & mask
    sign_bit = 1 << (width - 1)
    if wrapped & sign_bit:
        wrapped -= 1 << width
    return wrapped


def round_shift_signed(value: int, shift: int) -> int:
    if shift == 0:
        return value
    if shift < 0:
        raise ValueError("移位量不能为负数")

    half = 1 << (shift - 1)
    if value >= 0:
        return (value + half) >> shift
    return -((-value + half) >> shift)


def saturate_signed(value: int, width: int) -> int:
    minimum, maximum = signed_range(width)
    return max(minimum, min(maximum, value))


def check_input(value: int, name: str) -> None:
    minimum, maximum = signed_range(DATA_WIDTH)
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name}={value} 超出有符号 INT8 范围")


def dot4(a: list[int], b: list[int]) -> int:
    # 按本轮共同编写的循环逐项累加，偏置固定为零。
    acc = 0
    for i in range(4):
        acc = acc + a[i] * b[i]
    return acc


def round_shift_8(acc: int) -> int:
    # 先对绝对值舍入，再恢复符号，避免负数整除向下取整的偏差。
    if acc >= 0:
        return (acc + 128) // 256
    return -((-acc + 128) // 256)


def saturate_int8(value: int) -> int:
    if value > 127:
        return 127
    elif value < -128:
        return -128
    return value


def mac_reference(a: list[int], b: list[int]) -> dict[str, object]:
    if len(a) != LANES or len(b) != LANES:
        raise ValueError(f"输入必须各包含 {LANES} 个元素")

    for index, value in enumerate(a):
        check_input(value, f"a[{index}]")
    for index, value in enumerate(b):
        check_input(value, f"b[{index}]")

    products = [left * right for left, right in zip(a, b)]
    acc_exact = dot4(a, b)
    acc_hw = wrap_signed(acc_exact, ACC_WIDTH)
    shifted = round_shift_8(acc_hw)
    output_int8 = saturate_int8(shifted)

    return {
        "a": a,
        "b": b,
        "products": products,
        "acc_exact": acc_exact,
        "acc_hw": acc_hw,
        "shifted": shifted,
        "output_int8": output_int8,
    }


def build_cases() -> list[tuple[list[int], list[int], str]]:
    cases = [
        ([-128, -128, -128, -128], [-128, -128, -128, -128], "最大正乘积累加边界"),
        ([127, 127, 127, 127], [127, 127, 127, 127], "正数边界"),
        ([-128, -128, -128, -128], [127, 127, 127, 127], "负数边界"),
        ([-128, 127, -1, 0], [127, -128, -1, 100], "混合符号"),
        ([0, 0, 0, 0], [127, -128, 1, -1], "零输入"),
    ]

    generator = random.Random(RANDOM_SEED)
    minimum, maximum = signed_range(DATA_WIDTH)
    for index in range(20):
        a = [generator.randint(minimum, maximum) for _ in range(LANES)]
        b = [generator.randint(minimum, maximum) for _ in range(LANES)]
        cases.append((a, b, f"随机样例 {index + 1:02d}"))
    return cases


def verify_cases(cases: list[tuple[list[int], list[int], str]]) -> list[dict[str, object]]:
    results = []
    acc_min, acc_max = signed_range(ACC_WIDTH)
    output_min, output_max = signed_range(OUTPUT_WIDTH)

    for index, (a, b, category) in enumerate(cases):
        result = mac_reference(a, b)
        expected_exact = sum(left * right for left, right in zip(a, b))
        if result["acc_exact"] != expected_exact:
            raise AssertionError(f"样例 {index} 的精确累加结果错误")
        if not acc_min <= result["acc_hw"] <= acc_max:
            raise AssertionError(f"样例 {index} 的累加器结果超出 18 位范围")
        if not output_min <= result["output_int8"] <= output_max:
            raise AssertionError(f"样例 {index} 的 INT8 输出超出范围")

        result["index"] = index
        result["category"] = category
        results.append(result)
    return results


def main() -> None:
    cases = build_cases()
    results = verify_cases(cases)
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "spec": {
            "lanes": LANES,
            "data_width": DATA_WIDTH,
            "product_width": PRODUCT_WIDTH,
            "acc_width": ACC_WIDTH,
            "output_width": OUTPUT_WIDTH,
            "output_shift": OUTPUT_SHIFT,
            "bias": 0,
            "rounding": "对称的远离零点四舍五入",
            "saturation": "有符号 INT8 饱和到 [-128, 127]",
            "random_seed": RANDOM_SEED,
        },
        "sample_count": len(results),
        "random_sample_count": 20,
        "results": results,
    }
    RESULT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"INT8 MAC Python 参考验证通过：{len(results)} 组样例")
    print(f"固定随机种子：{RANDOM_SEED}")
    print(f"结果文件：{RESULT_PATH}")
    for result in results:
        print(
            f"[{result['index']:02d}] {result['category']}: "
            f"acc={result['acc_exact']}, output_int8={result['output_int8']}"
        )


if __name__ == "__main__":
    main()
