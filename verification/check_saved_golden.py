"""只读核验磁盘黄金数据，防止先覆盖旧结果再宣称一致。"""
import json
from decimal import Decimal, ROUND_HALF_UP

import int8_mac_reference as ref


def check():
    """核对规格、全部样例字段、独立数值依据和双侧非法输入。"""
    payload = json.loads(ref.RESULT_PATH.read_text(encoding="utf-8"))
    expected_spec = {
        "lanes": 4, "data_width": 8, "product_width": 16,
        "acc_width": 18, "output_width": 8, "output_shift": 8,
        "bias": 0, "rounding": "对称的远离零点四舍五入",
        "saturation": "有符号 INT8 饱和到 [-128, 127]",
        "random_seed": 20260907,
    }
    if payload["spec"] != expected_spec:
        raise ValueError("磁盘规格与当前约定不同")
    if payload["sample_count"] != 25 or payload["random_sample_count"] != 20:
        raise ValueError("样例数量不符")
    expected = []
    for index, (a, b, category) in enumerate(ref.build_cases()):
        products = [int(x) * int(y) for x, y in zip(a, b)]
        total = sum(products)
        rounded = int((Decimal(total) / Decimal(256)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        expected.append({"a": a, "b": b, "products": products,
                         "acc_exact": total, "acc_hw": total, "shifted": rounded,
                         "output_int8": min(127, max(-128, rounded)),
                         "index": index, "category": category})
    if payload["results"] != expected:
        raise ValueError("磁盘黄金结果存在字段不匹配")
    for acc, result in [(65536, 127), (-65024, -128), (384, 2), (-384, -2), (0, 0)]:
        if ref.saturate_int8(ref.round_shift_8(acc)) != result:
            raise ValueError(f"边界不匹配：{acc}")
    invalid = [[0] * 3, [0] * 5, [128] * 4, [-129] * 4, [1.5] * 4, [True] * 4]
    for values in invalid:
        for left, right in [(values, [0] * 4), ([0] * 4, values)]:
            try:
                ref.mac_reference(left, right)
            except ValueError:
                continue
            raise ValueError("非法输入未被拒绝")
    return {"golden_cases": 25, "mismatches": 0, "boundary_checks": 5,
            "invalid_input_checks": 12, "source_modified": False}


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=True))
