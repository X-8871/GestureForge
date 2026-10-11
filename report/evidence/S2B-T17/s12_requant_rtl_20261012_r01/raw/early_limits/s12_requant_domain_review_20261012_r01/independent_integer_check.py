import hashlib
import json
import random
import time
from pathlib import Path


# 独立建模原RTL的65位取负、64位赋值和8位结果。
U64 = (1 << 64) - 1


def signed(value, width):
    value &= (1 << width) - 1
    return value - (1 << width) if value >> (width - 1) else value


def magnitude_path(acc, multiplier, shift):
    magnitude = ((~(acc & 0xFFFFFFFF) + 1) & 0xFFFFFFFF) if acc < 0 else acc
    product = (magnitude * multiplier) & U64
    addition = (1 << (shift - 1)) & U64 if shift else 0
    result = ((product + addition) & U64) >> shift
    return product, addition, result


def baseline(acc, multiplier, shift):
    _, _, result = magnitude_path(acc, multiplier, shift)
    value65 = (-result if acc < 0 else result) & ((1 << 65) - 1)
    value64 = signed(value65, 64)
    return min(127, max(-127, value64))


def candidate(acc, multiplier, shift):
    _, _, result = magnitude_path(acc, multiplier, shift)
    if result >> 7:
        return -127 if acc < 0 else 127
    return signed(-signed(result & 0xFF, 8) if acc < 0 else result & 0xFF, 8)


def oracle(acc, multiplier, shift):
    # 使用欧几里得商余数独立定义half-away-from-zero。
    numerator = abs(acc) * multiplier
    divisor = 1 << shift
    quotient, remainder = divmod(numerator, divisor)
    rounded = quotient + int(2 * remainder >= divisor)
    return (-1 if acc < 0 else 1) * min(127, rounded)


def main():
    started = time.perf_counter()
    root = Path.cwd()
    source = root / 'src/s2b_conv_tile_engine.sv'
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == '51b76623b29a852ebf66cb818ef947d932c14055e4acbb20bd8fe811bb32d555'
    base = (root / 'src/s2a_conv_tile_engine.sv').read_text(encoding='utf-8')
    current = raw.decode('utf-8').replace('\r\n', '\n')
    def block(text):
        start = text.index('        requant_parameter = 80\'d0;')
        end = text.index('        mapped_response_error = INTERNAL;', start)
        return text[start:end]
    assert block(base) == block(current)
    accumulators = sorted({-(1 << 31), -(1 << 31) + 1, -(1 << 30), -65536,
                          -257, -256, -255, -129, -128, -127, -126, -3, -2, -1,
                          0, 1, 2, 3, 126, 127, 128, 129, 255, 256, 257, 65536,
                          1 << 30, (1 << 31) - 2, (1 << 31) - 1})
    multipliers = sorted({0, 1, 2, 3, 127, 128, 255, 256, 65535, 65536,
                         (1 << 30) - 1, 1 << 30, (1 << 31) - 1,
                         1 << 31, (1 << 32) - 2, (1 << 32) - 1})
    checked = legal_checked = 0
    max_product = max_addition = max_sum = max_result = 0
    def check(acc, multiplier, shift):
        nonlocal checked, legal_checked, max_product, max_addition, max_sum, max_result
        product, addition, result = magnitude_path(acc, multiplier, shift)
        assert product < 1 << 63
        assert product + addition < 1 << 64
        assert result < 1 << 63
        expected = oracle(acc, multiplier, shift)
        assert baseline(acc, multiplier, shift) == expected
        assert candidate(acc, multiplier, shift) == expected
        checked += 1
        legal_checked += int(1 <= multiplier <= 0x3FFFFFFF and shift <= 47)
        max_product = max(max_product, product)
        max_addition = max(max_addition, addition)
        max_sum = max(max_sum, product + addition)
        max_result = max(max_result, result)
    for acc in accumulators:
        for multiplier in multipliers:
            for shift in range(256):
                check(acc, multiplier, shift)
    rng = random.Random(20261012012)
    for _ in range(50000):
        check(rng.randrange(-(1 << 31), 1 << 31), rng.randrange(1 << 32), rng.randrange(256))
    for _ in range(50000):
        check(rng.randrange(-(1 << 31), 1 << 31), rng.randrange(1, 1 << 30), rng.randrange(48))
    manual = [(0, 0x3FFFFFFF, 0, 0), (-1, 1, 1, -1), (1, 1, 1, 1),
              (-127, 1, 0, -127), (-128, 1, 0, -127), (128, 1, 0, 127),
              (-(1 << 31), (1 << 32) - 1, 0, -127),
              (-(1 << 31), (1 << 32) - 1, 63, -1),
              (-(1 << 31), (1 << 32) - 1, 64, 0),
              (-(1 << 31), (1 << 32) - 1, 65, 0)]
    for acc, multiplier, shift, expected in manual:
        assert baseline(acc, multiplier, shift) == expected
        assert candidate(acc, multiplier, shift) == expected
    # 每个反例单独给出易被错误改法破坏的结果。
    mutant_witnesses = [
        {'mutant': '删除rounding', 'input': [1, 1, 1], 'expected': 1, 'mutated': 0},
        {'mutant': '负饱和改为-128', 'input': [-128, 1, 0], 'expected': -127, 'mutated': -128},
        {'mutant': '高位检测从bit8开始', 'input': [128, 1, 0], 'expected': 127, 'mutated': -128},
        {'mutant': 'product截为32位', 'input': [65536, 65536, 0], 'expected': 127, 'mutated': 0},
        {'mutant': '由rounded[63]恢复符号', 'input': [-1, 1, 0], 'expected': -1, 'mutated': 1},
        {'mutant': '按shift低6位回绕', 'input': [-(1 << 31), (1 << 32) - 1, 64], 'expected': 0, 'mutated': -127},
    ]
    output = {'status': 'PASS_G0_MATH', 'source_raw_sha256': digest,
              'head': '932051cdacdf02f729d6a7554b07118d05e96aa4',
              'original_s2a_requant_block_exact_text_equal': True,
              'checks': checked, 'legal_domain_checks': legal_checked,
              'random_seed': 20261012012, 'random_samples': 100000,
              'full_shift_grid': '0..255',
              'max_product': max_product, 'max_rounding_add': max_addition,
              'max_sum_before_shift': max_sum, 'max_rounded': max_result,
              'manual': [{'acc': a, 'multiplier': m, 'shift': q, 'expected': e}
                         for a, m, q, e in manual],
              'mutant_witnesses': mutant_witnesses,
              'elapsed_seconds': time.perf_counter() - started,
              'limits': ['仅二值整数域数学审查；没有编译或RTL仿真',
                         '没有STA、完整网络、实板或G1/G2验收',
                         'mutants记录为手算反例，未执行RTL变异测试',
                         '峰值内存未测']}
    destination = Path(__file__).with_name('integer_check_result.json')
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
