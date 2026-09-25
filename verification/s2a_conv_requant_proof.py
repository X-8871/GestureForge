"""对 S2A 卷积 D2 浮点重定标的全域整数阈值等价性进行审计。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import struct
import subprocess
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification.s1_t02_d2_int8_forward import round_away_array, saturate_array


MANIFEST_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
EXPECTED_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1
ABSENT_POSITIVE_THRESHOLD = INT32_MAX + 1
LEVELS = np.arange(-126, 128, dtype=np.int64)
MAGNITUDE_LEVELS = np.arange(1, 128, dtype=np.int64)
MAX_Q_SHIFT = 65


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bound_file(manifest: dict[str, Any], key: str) -> tuple[Path, str]:
    binding = manifest["bindings"][key]
    path = ROOT / Path(binding["path"])
    declared = str(binding["sha256"]).lower()
    actual = _sha256(path)
    if actual != declared:
        raise ValueError(f"{key} SHA-256 与 T01 清单绑定不符: {actual} != {declared}")
    return path, actual


def _round_half_away_scaled(values: np.ndarray) -> np.ndarray:
    """复用 D2 的舍入函数，并在 int64 安全范围内返回整数舍入值。"""

    values = np.asarray(values, dtype=np.float64)
    if np.any(~np.isfinite(values)) or np.any(np.abs(values) >= float((1 << 63) - 1024)):
        raise ValueError("D2 重定标值超出有限 int64 安全映射范围")
    return round_away_array(values)


def _signed_rounded_predicate(
    accumulators: np.ndarray,
    real_scales: np.ndarray,
    output_scale: float,
    activation: str,
) -> np.ndarray:
    """按 D2 的运算顺序计算舍入后是否达到各有符号转移值。"""

    scaled = accumulators.astype(np.float64) * real_scales[:, None]
    scaled = scaled / output_scale
    if activation == "leaky":
        scaled = np.where(scaled >= 0.0, scaled, scaled * 0.1)
    elif activation != "linear":
        raise ValueError(f"不支持的卷积激活: {activation}")
    rounded = np.where(
        scaled >= 0.0,
        np.floor(np.abs(scaled) + 0.5),
        -np.floor(np.abs(scaled) + 0.5),
    )
    return rounded >= LEVELS[None, :]


def _d2_endpoints(
    real_scales: np.ndarray,
    output_scale: float,
    activation: str,
    accumulator: int,
) -> np.ndarray:
    """调用冻结 D2 的舍入、饱和函数计算一个域端点。"""

    scaled = np.asarray([accumulator], dtype=np.int64).astype(np.float64) * real_scales
    scaled = scaled / output_scale
    if activation == "leaky":
        scaled = np.where(scaled >= 0.0, scaled, scaled * 0.1)
    rounded = _round_half_away_scaled(scaled)
    return saturate_array(rounded).astype(np.int64)


def _d2_thresholds(
    real_scales: np.ndarray,
    output_scale: float,
    activation: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """二分查找每个输出通道对全部 254 个有符号转移值的首个累加器。"""

    channel_count = int(real_scales.size)
    low_endpoint = _d2_endpoints(real_scales, output_scale, activation, INT32_MIN)
    high_endpoint = _d2_endpoints(real_scales, output_scale, activation, INT32_MAX)
    low_predicate = low_endpoint[:, None] >= LEVELS[None, :]
    high_predicate = high_endpoint[:, None] >= LEVELS[None, :]
    active = (~low_predicate) & high_predicate
    low = np.full((channel_count, LEVELS.size), INT32_MIN, dtype=np.int64)
    high = np.full((channel_count, LEVELS.size), INT32_MAX, dtype=np.int64)

    # 区间宽度小于 2**32，32 轮二分即可确定唯一最小值。
    for _ in range(32):
        middle = (low + high) // 2
        query = np.where(active, middle, 0)
        reached = _signed_rounded_predicate(query, real_scales, output_scale, activation)
        move_high = active & reached
        move_low = active & (~reached)
        high = np.where(move_high, middle, high)
        low = np.where(move_low, middle, low)

    thresholds = np.where(
        low_predicate,
        INT32_MIN,
        np.where(high_predicate, high, ABSENT_POSITIVE_THRESHOLD),
    )
    if np.any(np.diff(thresholds, axis=1) < 0):
        raise AssertionError("D2 量化映射阈值不单调")
    normal = (thresholds > INT32_MIN) & (thresholds <= INT32_MAX)
    before = np.where(normal, thresholds - 1, INT32_MIN)
    reached_before = _signed_rounded_predicate(
        before, real_scales, output_scale, activation
    )
    reached_at = _signed_rounded_predicate(
        np.where(normal, thresholds, INT32_MIN), real_scales, output_scale, activation
    )
    if np.any(normal & reached_before) or np.any(normal & (~reached_at)):
        raise AssertionError("D2 二分阈值未满足前一点未达、阈值点已达")
    if np.any(low_predicate & (~reached_at)) or np.any(
        (~high_predicate) & _signed_rounded_predicate(
            np.full_like(thresholds, INT32_MAX), real_scales, output_scale, activation
        )
    ):
        raise AssertionError("D2 首尾端点与阈值哨兵不一致")
    return thresholds, low_endpoint, high_endpoint


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def _magnitude_threshold_interval(
    thresholds: list[int], domain_max: int
) -> tuple[Fraction, Fraction | None, tuple[int, int | None], tuple[int, int | None]]:
    """由量化阈值求出可复现目标映射的全部实数斜率区间。"""

    lower: Fraction | None = None
    upper: Fraction | None = None
    lower_witness: tuple[int, int | None] = (0, 0)
    upper_witness: tuple[int, int | None] | None = None
    for level, transition in enumerate(thresholds, start=1):
        boundary = 2 * level - 1
        if transition == -1:
            candidate_upper = Fraction(boundary, 2 * domain_max)
            if upper is None or candidate_upper < upper:
                upper = candidate_upper
                upper_witness = (level, None)
            continue
        if transition < 1 or transition > domain_max:
            raise AssertionError(f"幅值阈值越界: {transition} / {domain_max}")
        candidate_lower = Fraction(boundary, 2 * transition)
        if lower is None or candidate_lower > lower:
            lower = candidate_lower
            lower_witness = (level, transition)
        if transition > 1:
            candidate_upper = Fraction(boundary, 2 * (transition - 1))
            if upper is None or candidate_upper < upper:
                upper = candidate_upper
                upper_witness = (level, transition - 1)
    if lower is None:
        lower = Fraction(0, 1)
    return lower, upper, lower_witness, upper_witness or (0, None)


def _integer_multiplier_bounds(
    lower: Fraction, upper: Fraction | None, q_shift: int
) -> tuple[int, int | None]:
    """把严格实数区间精确投影到 M / 2**Q 的整数乘数上。"""

    unit = 1 << q_shift
    minimum = _ceil_div(lower.numerator * unit, lower.denominator)
    maximum = None if upper is None else _ceil_div(upper.numerator * unit, upper.denominator) - 1
    return minimum, maximum


def _round_away_positive_float(value: float) -> int:
    magnitude = math.floor(abs(value) + 0.5)
    return magnitude if value >= 0.0 else -magnitude


def _candidate_magnitude_threshold(multiplier: int, q_shift: int, level: int, domain_max: int) -> int:
    if multiplier <= 0:
        return -1
    numerator = (2 * level - 1) * (1 << q_shift)
    threshold = _ceil_div(numerator, 2 * multiplier)
    return threshold if threshold <= domain_max else -1


def _candidate_magnitude_output(magnitude: int, multiplier: int, q_shift: int) -> int:
    if multiplier == 0:
        return 0
    divisor = 1 << q_shift
    rounded = (2 * magnitude * multiplier + divisor) // (2 * divisor)
    return min(127, rounded)


def _find_candidate(
    thresholds: list[int],
    domain_max: int,
    ideal_scale: float,
) -> dict[str, Any]:
    lower, upper, lower_witness, upper_witness = _magnitude_threshold_interval(
        thresholds, domain_max
    )
    if upper is not None and lower >= upper:
        return {
            "status": "no_real_fixed_scale",
            "q_shifts_examined": 0,
            "lower": [lower.numerator, lower.denominator],
            "upper": [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
        }

    for q_shift in range(MAX_Q_SHIFT + 1):
        minimum, maximum = _integer_multiplier_bounds(lower, upper, q_shift)
        if maximum is not None and minimum > maximum:
            continue
        nominal = _round_away_positive_float(math.ldexp(ideal_scale, q_shift))
        multiplier = max(minimum, nominal)
        if maximum is not None:
            multiplier = min(multiplier, maximum)
        actual = [
            _candidate_magnitude_threshold(multiplier, q_shift, level, domain_max)
            for level in range(1, 128)
        ]
        if actual != thresholds:
            raise AssertionError(
                f"候选乘数的阈值区间推导与整数复核不一致: Q={q_shift}, M={multiplier}"
            )
        return {
            "status": "exact",
            "q_shifts_examined": q_shift + 1,
            "q_shift": q_shift,
            "multiplier": multiplier,
            "multiplier_bits": max(1, multiplier.bit_length()),
            "nominal_multiplier": nominal,
            "feasible_min_multiplier": minimum,
            "feasible_max_multiplier": maximum,
            "slope_lower": [lower.numerator, lower.denominator],
            "slope_upper_exclusive": None if upper is None else [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
        }
    return {
        "status": "no_dyadic_scale_through_q65",
        "q_shifts_examined": MAX_Q_SHIFT + 1,
        "lower": [lower.numerator, lower.denominator],
        "upper": None if upper is None else [upper.numerator, upper.denominator],
        "lower_witness": list(lower_witness),
        "upper_witness": list(upper_witness),
    }


def _candidate_signed_thresholds(
    positive: dict[str, Any], negative: dict[str, Any]
) -> list[int]:
    """从两个幅值分支的整数阈值精确重建 254 个有符号转移点。"""

    result: list[int] = []
    for level in LEVELS.tolist():
        if level >= 1:
            candidate = _candidate_magnitude_threshold(
                positive["multiplier"], positive["q_shift"], int(level), INT32_MAX
            )
            result.append(ABSENT_POSITIVE_THRESHOLD if candidate == -1 else candidate)
        else:
            magnitude_level = 1 - int(level)
            candidate = _candidate_magnitude_threshold(
                negative["multiplier"], negative["q_shift"], magnitude_level, 1 << 31
            )
            result.append(INT32_MIN if candidate == -1 else 1 - candidate)
    return result


def _candidate_endpoint_output(candidate: dict[str, Any], magnitude: int, negative: bool) -> int:
    value = _candidate_magnitude_output(
        magnitude, candidate["multiplier"], candidate["q_shift"]
    )
    return -value if negative else value


def _first_threshold_mismatch(expected: list[int], actual: list[int]) -> dict[str, int] | None:
    for level, (target, candidate) in zip(LEVELS.tolist(), zip(expected, actual)):
        if target != candidate:
            return {"transition_level": int(level), "d2_threshold": int(target), "candidate_threshold": int(candidate)}
    return None


def _layer_digest(thresholds: np.ndarray, low_endpoint: np.ndarray, high_endpoint: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.asarray(low_endpoint, dtype="<i8").tobytes())
    digest.update(np.asarray(high_endpoint, dtype="<i8").tobytes())
    digest.update(np.asarray(thresholds, dtype="<i8").tobytes())
    return digest.hexdigest()


def _candidate_digest(rows: list[tuple[int, dict[str, Any], dict[str, Any]]]) -> str:
    digest = hashlib.sha256()
    for channel, positive, negative in rows:
        digest.update(
            (
                f"{channel},{positive['q_shift']},{positive['multiplier']},"
                f"{negative['q_shift']},{negative['multiplier']}\n"
            ).encode("ascii")
        )
    return digest.hexdigest()


def _branch_magnitude_thresholds(row: np.ndarray) -> tuple[list[int], list[int]]:
    positive: list[int] = []
    negative: list[int] = []
    for level in range(1, 128):
        signed_positive = int(row[int(level) - int(LEVELS[0])])
        positive.append(-1 if signed_positive == ABSENT_POSITIVE_THRESHOLD else signed_positive)
        signed_negative_level = 1 - level
        signed_negative = int(row[signed_negative_level - int(LEVELS[0])])
        negative.append(-1 if signed_negative == INT32_MIN else 1 - signed_negative)
    return positive, negative


def _find_linear_joint_candidate(
    positive_thresholds: list[int],
    negative_thresholds: list[int],
    ideal_scale: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pos_lower, pos_upper, pos_lw, pos_uw = _magnitude_threshold_interval(positive_thresholds, INT32_MAX)
    neg_lower, neg_upper, neg_lw, neg_uw = _magnitude_threshold_interval(negative_thresholds, 1 << 31)
    lower = max(pos_lower, neg_lower)
    finite_uppers = [item for item in (pos_upper, neg_upper) if item is not None]
    upper = min(finite_uppers) if finite_uppers else None
    lower_witness = pos_lw if pos_lower >= neg_lower else neg_lw
    upper_witness = pos_uw if pos_upper is not None and (neg_upper is None or pos_upper <= neg_upper) else neg_uw
    if upper is not None and lower >= upper:
        conflict = {
            "status": "no_real_fixed_scale",
            "q_shifts_examined": 0,
            "lower": [lower.numerator, lower.denominator],
            "upper": [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
        }
        return dict(conflict), dict(conflict)

    for q_shift in range(MAX_Q_SHIFT + 1):
        minimum, maximum = _integer_multiplier_bounds(lower, upper, q_shift)
        if maximum is not None and minimum > maximum:
            continue
        nominal = _round_away_positive_float(math.ldexp(ideal_scale, q_shift))
        multiplier = max(minimum, nominal)
        if maximum is not None:
            multiplier = min(multiplier, maximum)
        positive_actual = [
            _candidate_magnitude_threshold(multiplier, q_shift, level, INT32_MAX)
            for level in range(1, 128)
        ]
        negative_actual = [
            _candidate_magnitude_threshold(multiplier, q_shift, level, 1 << 31)
            for level in range(1, 128)
        ]
        if positive_actual != positive_thresholds or negative_actual != negative_thresholds:
            raise AssertionError("线性分支共享乘数未通过整数阈值复核")
        shared = {
            "status": "exact",
            "q_shifts_examined": q_shift + 1,
            "q_shift": q_shift,
            "multiplier": multiplier,
            "multiplier_bits": max(1, multiplier.bit_length()),
            "nominal_multiplier": nominal,
            "feasible_min_multiplier": minimum,
            "feasible_max_multiplier": maximum,
            "slope_lower": [lower.numerator, lower.denominator],
            "slope_upper_exclusive": None if upper is None else [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
            "shared_linear_parameter": True,
        }
        return dict(shared), dict(shared)
    return (
        {
            "status": "no_dyadic_scale_through_q65",
            "q_shifts_examined": MAX_Q_SHIFT + 1,
            "lower": [lower.numerator, lower.denominator],
            "upper": None if upper is None else [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
        },
        {
            "status": "no_dyadic_scale_through_q65",
            "q_shifts_examined": MAX_Q_SHIFT + 1,
            "lower": [lower.numerator, lower.denominator],
            "upper": None if upper is None else [upper.numerator, upper.denominator],
            "lower_witness": list(lower_witness),
            "upper_witness": list(upper_witness),
        },
    )


def _first_magnitude_mismatch(
    expected: list[int], multiplier: int, q_shift: int, domain_max: int
) -> dict[str, int] | None:
    for level, target in enumerate(expected, start=1):
        candidate = _candidate_magnitude_threshold(multiplier, q_shift, level, domain_max)
        if target != candidate:
            return {
                "magnitude_transition": level,
                "d2_threshold_magnitude": int(target),
                "candidate_threshold_magnitude": int(candidate),
            }
    return None


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _channel_records(
    layer: dict[str, Any],
    thresholds: np.ndarray,
    low_endpoint: np.ndarray,
    high_endpoint: np.ndarray,
    real_scales: np.ndarray,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    activation = str(layer["activation"])
    branch_hashes = {
        "target_threshold_sha256": hashlib.sha256(),
        "candidate_parameter_sha256": hashlib.sha256(),
    }
    q_counts_positive: Counter[int] = Counter()
    q_counts_negative: Counter[int] = Counter()
    q_checks_positive = 0
    q_checks_negative = 0
    coefficient_rows: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    failures: list[dict[str, Any]] = []
    first_shift_counterexample: dict[str, dict[str, Any]] = {}
    channel_count = int(thresholds.shape[0])
    exact_channels = 0
    max_multiplier_bits = 0
    max_q_shift = 0

    for channel in range(channel_count):
        target_row = [int(value) for value in thresholds[channel].tolist()]
        pos_targets, neg_targets = _branch_magnitude_thresholds(thresholds[channel])
        ideal_positive = float(real_scales[channel]) / float(layer["output_scale"])
        ideal_negative = ideal_positive if activation == "linear" else ideal_positive * 0.1
        if activation == "linear":
            positive, negative = _find_linear_joint_candidate(
                pos_targets, neg_targets, ideal_positive
            )
        else:
            positive = _find_candidate(
                pos_targets,
                INT32_MAX,
                ideal_positive,
            )
            negative = _find_candidate(
                neg_targets,
                1 << 31,
                ideal_negative,
            )

        if positive["status"] == "exact" and negative["status"] == "exact":
            if activation == "linear":
                q_checks_positive += int(positive["q_shift"]) + 1
                q_checks_negative += int(positive["q_shift"]) + 1
            else:
                q_checks_positive += int(positive["q_shift"]) + 1
                q_checks_negative += int(negative["q_shift"]) + 1
            candidate_thresholds = _candidate_signed_thresholds(positive, negative)
            mismatch = _first_threshold_mismatch(target_row, candidate_thresholds)
            candidate_low = _candidate_endpoint_output(negative, 1 << 31, True)
            candidate_high = _candidate_endpoint_output(positive, INT32_MAX, False)
            target_low = int(low_endpoint[channel])
            target_high = int(high_endpoint[channel])
            if mismatch is not None or candidate_low != target_low or candidate_high != target_high:
                failures.append(
                    {
                        "layer_index": int(layer["layer_index"]),
                        "channel": channel,
                        "kind": "candidate_verification_mismatch",
                        "first_threshold_mismatch": mismatch,
                        "domain_endpoints": {
                            "int32_min": {"d2": target_low, "candidate": candidate_low},
                            "int32_max": {"d2": target_high, "candidate": candidate_high},
                        },
                    }
                )
            else:
                exact_channels += 1
                q_counts_positive[int(positive["q_shift"])] += 1
                q_counts_negative[int(negative["q_shift"])] += 1
                probe_branches = [
                    ("positive", positive, pos_targets, INT32_MAX, ideal_positive),
                    ("negative", negative, neg_targets, 1 << 31, ideal_negative),
                ]
                for branch_name, selected, branch_targets, domain_max, ideal in probe_branches:
                    if int(selected["q_shift"]) == 0 or branch_name in first_shift_counterexample:
                        continue
                    failed_q = int(selected["q_shift"]) - 1
                    nominal = _round_away_positive_float(math.ldexp(ideal, failed_q))
                    counterexample = _first_magnitude_mismatch(
                        branch_targets, nominal, failed_q, domain_max
                    )
                    if counterexample is None:
                        raise AssertionError(
                            f"Q={failed_q} 存在未被斜率区间发现的精确候选: layer={layer['layer_index']} channel={channel} branch={branch_name}"
                        )
                    first_shift_counterexample[branch_name] = {
                        "layer_index": int(layer["layer_index"]),
                        "channel": channel,
                        "branch": branch_name,
                        "q_shift": failed_q,
                        "nominal_multiplier": nominal,
                        "first_mismatch": counterexample,
                        "meaning": "该移位下最近理想斜率乘数的首个转移点不匹配；更粗移位是否可行由精确整数乘数区间逐 Q 判定。",
                    }
                max_q_shift = max(max_q_shift, int(positive["q_shift"]), int(negative["q_shift"]))
                max_multiplier_bits = max(
                    max_multiplier_bits,
                    int(positive["multiplier_bits"]),
                    int(negative["multiplier_bits"]),
                )
                coefficient_rows.append((channel, positive, negative))
        else:
            q_checks_positive += int(positive.get("q_shifts_examined", 0))
            q_checks_negative += int(negative.get("q_shifts_examined", 0))
            failures.append(
                {
                    "layer_index": int(layer["layer_index"]),
                    "channel": channel,
                    "kind": "no_exact_multiplier_shift",
                    "positive": positive,
                    "negative": negative,
                }
            )

        branch_hashes["target_threshold_sha256"].update(struct.pack("<I", channel))
        branch_hashes["target_threshold_sha256"].update(struct.pack("<ii", int(low_endpoint[channel]), int(high_endpoint[channel])))
        branch_hashes["target_threshold_sha256"].update(np.asarray(target_row, dtype="<i8").tobytes())

    for channel, positive, negative in coefficient_rows:
        branch_hashes["candidate_parameter_sha256"].update(
            (
                f"{channel},{positive['q_shift']},{positive['multiplier']},"
                f"{negative['q_shift']},{negative['multiplier']}\n"
            ).encode("ascii")
        )

    summary = {
        "layer_index": int(layer["layer_index"]),
        "cfg_section": int(layer["cfg_section"]),
        "activation": activation,
        "output_channels_audited": channel_count,
        "channels_with_exact_candidate": exact_channels,
        "positive_branch_q_shift_histogram": {str(q): q_counts_positive[q] for q in sorted(q_counts_positive)},
        "negative_branch_q_shift_histogram": {str(q): q_counts_negative[q] for q in sorted(q_counts_negative)},
        "maximum_q_shift": max_q_shift,
        "maximum_multiplier_bits": max_multiplier_bits,
        "q_feasibility_checks": {
            "positive_branch": q_checks_positive,
            "negative_branch": q_checks_negative,
            "interpretation": "每个 Q 检查可行乘数区间；linear 两个分支共享同一 Q，分别计入正、负域约束。空实数区间以精确矛盾直接排除所有 Q，不重复遍历。",
            "coarser_q_rejections_before_selected_shift": sum(q * count for q, count in q_counts_positive.items())
            + sum(q * count for q, count in q_counts_negative.items()),
        },
        "first_shift_counterexamples": first_shift_counterexample,
        **{key: digest.hexdigest() for key, digest in branch_hashes.items()},
    }
    return summary, failures


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"冻结清单不存在: {MANIFEST_PATH}")
    manifest_sha = _sha256(MANIFEST_PATH)
    if manifest_sha != EXPECTED_MANIFEST_SHA256:
        raise ValueError(
            f"tiny416 T01 冻结清单 SHA-256 不符: {manifest_sha} != {EXPECTED_MANIFEST_SHA256}"
        )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    d2_forward_path, d2_forward_sha = _bound_file(manifest, "d2_int8_forward_reference")
    d2_numeric_path, d2_numeric_sha = _bound_file(manifest, "d2_numeric_reference")
    if d2_forward_path.resolve() != (ROOT / "verification/s1_t02_d2_int8_forward.py").resolve():
        raise ValueError("T01 forward reference 路径与本审计实现的 D2 调用目标不一致")

    layers = [layer for layer in manifest["layers"] if layer.get("op") == "convolutional"]
    if args.layer_index:
        selected = set(args.layer_index)
        layers = [layer for layer in layers if int(layer["layer_index"]) in selected]
        missing = selected - {int(layer["layer_index"]) for layer in layers}
        if missing:
            raise ValueError(f"请求的卷积层不在 T01 清单: {sorted(missing)}")
    failures: list[dict[str, Any]] = []
    layer_summaries: list[dict[str, Any]] = []
    total_channels = 0
    total_exact = 0

    for layer in layers:
        weight_scales = np.asarray(layer["weight_scale_per_output_channel"], dtype=np.float64)
        if args.channels is not None:
            weight_scales = weight_scales[: args.channels]
        if weight_scales.size == 0:
            raise ValueError(f"卷积层 {layer['layer_index']} 没有待审通道")
        input_scale = float(layer["input_scale"])
        output_scale = float(layer["output_scale"])
        if not (math.isfinite(input_scale) and input_scale > 0.0 and math.isfinite(output_scale) and output_scale > 0.0):
            raise ValueError(f"卷积层 {layer['layer_index']} 的张量 scale 非法")
        if np.any(~np.isfinite(weight_scales)) or np.any(weight_scales <= 0.0):
            raise ValueError(f"卷积层 {layer['layer_index']} 的权重 scale 非法")
        real_scales = np.float64(input_scale) * weight_scales
        # D2 会先转换为 int64 再做 half-away；拒绝源算法无法安全表达的极端值。
        maximum_scaled = float(np.max(real_scales)) * (1 << 31) / output_scale
        if not math.isfinite(maximum_scaled) or maximum_scaled >= float((1 << 63) - 1024):
            raise ValueError(f"卷积层 {layer['layer_index']} 的 D2 舍入超出 int64 安全范围")
        thresholds, low_endpoint, high_endpoint = _d2_thresholds(
            real_scales, output_scale, str(layer["activation"])
        )
        summary, layer_failures = _channel_records(
            layer, thresholds, low_endpoint, high_endpoint, real_scales
        )
        total_channels += int(summary["output_channels_audited"])
        total_exact += int(summary["channels_with_exact_candidate"])
        summary["d2_threshold_and_endpoint_sha256"] = _layer_digest(
            thresholds, low_endpoint, high_endpoint
        )
        layer_summaries.append(summary)
        failures.extend(layer_failures)

    complete = not args.layer_index and args.channels is None
    return {
        "schema": "GestureForge-S2A-T16-requant-proof-v1",
        "status": "EXACT_FIXED_POINT_FOUND" if total_exact == total_channels and not failures else "EXACT_FIXED_POINT_NOT_ESTABLISHED",
        "coverage": {
            "complete_tiny416_convolution_model": complete,
            "convolution_layers_audited": len(layers),
            "output_channels_audited": total_channels,
            "output_channels_with_exact_candidate": total_exact,
            "failures": len(failures),
        },
        "binding": {
            "git_head_at_run": _git_head(),
            "audit_script": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                "sha256": _sha256(Path(__file__).resolve()),
            },
            "manifest": {
                "path": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": manifest_sha,
            },
            "d2_int8_forward_reference": {
                "path": str(d2_forward_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": d2_forward_sha,
            },
            "d2_numeric_reference": {
                "path": str(d2_numeric_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": d2_numeric_sha,
            },
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numpy": np.__version__,
            "working_directory": os.getcwd(),
            "command_argv": sys.argv,
            "bytecode_writes_disabled": sys.dont_write_bytecode,
            "random_seed": None,
            "randomness": "无随机过程；所有转移点以确定性二分查找获得。",
        },
        "semantics": {
            "accumulator_domain": [INT32_MIN, INT32_MAX],
            "d2_order": "float64(acc) * (input_scale * weight_scale)，再除 output_scale；leaky 且结果为负时再乘 binary64 0.1；half-away-from-zero；饱和到 [-127,127]。",
            "bias": "累加器输入视为已经包含 D2 的 INT32 bias；不重复加 bias。",
            "candidate": "非负幅值使用精确整数 round_half_away(magnitude * M / 2**Q)，再对符号和 [-127,127] 饱和；linear 两侧共享 M/Q，leaky 两侧允许独立 M/Q。",
            "transition_values": LEVELS.tolist(),
            "absent_transition_sentinel": {
                "no_transition_in_domain": ABSENT_POSITIVE_THRESHOLD,
                "transition_already_true_at_int32_min": INT32_MIN,
            },
            "proof": "D2 与候选映射均单调。对每个 k=-126..127，相同的最小 acc 满足 output>=k，再加两端点输出相同，可确定 [-127,127] 有限输出域内的每个累加器输入输出相同。候选阈值由整数不等式精确计算；斜率可行区间使用 Fraction 精确交集，并逐个检查 Q=0..65。",
            "q_search_bound": MAX_Q_SHIFT,
            "q_bound_reason": "任一非空区间端点的分母至多 2**32；不同有理端点间的非零间隔至少 2**-64，故 2**-65 dyadic 网格必含区间内一点。若实数区间为空，则任何 Q 均无候选。",
        },
        "layers": layer_summaries,
        "failures": failures,
        "limitations": [
            "此项只证明累加器重定标的数学等价性，不证明 MAC/卷积 RTL、张量逐值比对、PS/PL 协议、G1/G2/G4 或阶段 2A 验收。",
            "定点乘数位宽及乘法器资源/时序尚未约束；Q 搜索覆盖的是任意精度整数乘数。",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="全域审计 tiny416 卷积 D2 重定标的整数乘数/移位等价性")
    parser.add_argument("--layer-index", type=int, action="append", help="只计算指定卷积层，可重复；用于算法试跑")
    parser.add_argument("--channels", type=int, help="每个所选层仅计算前 N 个输出通道；用于算法试跑")
    parser.add_argument("--no-write", action="store_true", help="只输出摘要，不写证据文件")
    parser.add_argument("--output", type=Path, default=ROOT / "report/evidence/S2A-T16/conv_requant_proof.json", help="证据 JSON 路径")
    args = parser.parse_args()
    if args.channels is not None and args.channels <= 0:
        parser.error("--channels 必须为正数")
    result = run_audit(args)
    if not args.no_write:
        destination = args.output if args.output.is_absolute() else ROOT / args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        json.dumps(
            {
                "status": result["status"],
                "coverage": result["coverage"],
                "git_head_at_run": result["binding"]["git_head_at_run"],
                "evidence": None if args.no_write else str((args.output if args.output.is_absolute() else ROOT / args.output)),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if result["coverage"]["failures"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
