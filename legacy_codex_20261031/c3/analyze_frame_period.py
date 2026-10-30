#!/usr/bin/env python3
"""离线分析按事件/计数器采集的 GT 时间区间。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from decimal import Decimal, DecimalException, InvalidOperation, ROUND_CEILING
from fractions import Fraction
from pathlib import Path
from typing import Iterable


EVENT_KINDS = {
    "camera_sof",
    "vdma_s2mm_frame",
    "vdma_mm2s_readstore",
    "hdmi_vsync",
    "inference_done",
    "result_publish",
}
SAMPLE_KINDS = {"counter_snapshot", "event_bracket"}
COUNTER_TYPES = {"monotonic", "cyclic_pointer"}
CSV_COLUMNS = {
    "sample_index",
    "event_kind",
    "sample_kind",
    "counter_type",
    "counter_modulus",
    "counter_value",
    "clock_id",
    "gt_before",
    "gt_after",
}


@dataclass(frozen=True)
class Sample:
    sample_index: int
    event_kind: str
    sample_kind: str
    counter_type: str
    counter_modulus: int
    counter_value: int
    clock_id: str
    gt_before: int
    gt_after: int


def _parse_int(value: str, field: str, line: int) -> int:
    text = value.strip()
    if not text:
        raise ValueError(f"CSV 第 {line} 行字段 {field} 为空")
    try:
        return int(text, 0) if text.lower().startswith("0x") else int(text, 10)
    except ValueError as exc:
        raise ValueError(f"CSV 第 {line} 行字段 {field} 不是十进制或 0x 十六进制整数") from exc


def read_csv(path: Path) -> list[Sample]:
    """读取 UTF-8 CSV；每行表示一次计数器观测或一个带时间界的事件。"""
    samples: list[Sample] = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = set(reader.fieldnames or [])
        missing = sorted(CSV_COLUMNS - headers)
        if missing:
            raise ValueError("CSV 缺少列：" + ", ".join(missing))
        for line, row in enumerate(reader, start=2):
            event_kind = (row.get("event_kind") or "").strip()
            sample_kind = (row.get("sample_kind") or "").strip()
            counter_type = (row.get("counter_type") or "").strip()
            clock_id = (row.get("clock_id") or "").strip()
            if event_kind not in EVENT_KINDS:
                raise ValueError(f"CSV 第 {line} 行 event_kind 不支持：{event_kind!r}")
            if sample_kind not in SAMPLE_KINDS:
                raise ValueError(f"CSV 第 {line} 行 sample_kind 不支持：{sample_kind!r}")
            if counter_type not in COUNTER_TYPES:
                raise ValueError(f"CSV 第 {line} 行 counter_type 不支持：{counter_type!r}")
            if not clock_id:
                raise ValueError(f"CSV 第 {line} 行 clock_id 为空")
            sample = Sample(
                sample_index=_parse_int(row["sample_index"], "sample_index", line),
                event_kind=event_kind,
                sample_kind=sample_kind,
                counter_type=counter_type,
                counter_modulus=_parse_int(row["counter_modulus"], "counter_modulus", line),
                counter_value=_parse_int(row["counter_value"], "counter_value", line),
                clock_id=clock_id,
                gt_before=_parse_int(row["gt_before"], "gt_before", line),
                gt_after=_parse_int(row["gt_after"], "gt_after", line),
            )
            samples.append(sample)
    if not samples:
        raise ValueError("CSV 没有数据行")
    return samples


def _parse_positive_finite_decimal(value: str) -> Decimal:
    """解析有限正小数，供 argparse 在分析开始前拒绝无效周期界。"""
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("必须是有限正数") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise argparse.ArgumentTypeError("必须是有限正数")
    return parsed


def _counter_delta(previous: Sample, current: Sample) -> int:
    modulus = previous.counter_modulus
    if previous.counter_type == "monotonic":
        if current.counter_value < previous.counter_value:
            raise ValueError(
                f"单调计数器回退或回绕：样本 {previous.sample_index}→{current.sample_index}；"
                "本工具不推断回绕次数，请从回绕前后分别开始采集"
            )
        return current.counter_value - previous.counter_value
    return (current.counter_value - previous.counter_value) % modulus


def _round_number(value: Fraction, places: int = 6) -> float:
    quantum = Decimal(1).scaleb(-places)
    decimal_value = Decimal(value.numerator) / Decimal(value.denominator)
    return float(decimal_value.quantize(quantum))


def _ticks_to_us(value: Fraction, gt_hz: int) -> float:
    return _round_number(value * Fraction(1_000_000, gt_hz))


def _common_fields(samples: list[Sample]) -> tuple[str, str, str, int, str]:
    fields = {
        (s.event_kind, s.sample_kind, s.counter_type, s.counter_modulus, s.clock_id)
        for s in samples
    }
    if len(fields) != 1:
        raise ValueError("一个 CSV 只能包含同一事件、样本类型、计数器类型、模数和时钟")
    event_kind, sample_kind, counter_type, modulus, clock_id = next(iter(fields))
    if modulus < 2:
        raise ValueError("counter_modulus 必须至少为 2")
    if not (0 <= samples[0].counter_value < modulus):
        raise ValueError("counter_value 必须位于 [0, counter_modulus)")
    return event_kind, sample_kind, counter_type, modulus, clock_id


def analyze_samples(
    samples: Iterable[Sample],
    gt_hz: int,
    origin: str,
    min_event_period_us: Decimal | None = None,
) -> dict[str, object]:
    """按样本语义计算平均周期及区间；不把估计自动升级为验收结论。"""
    ordered = list(samples)
    if gt_hz <= 0:
        raise ValueError("gt_hz 必须为正整数")
    if origin not in {"captured", "synthetic"}:
        raise ValueError("origin 必须为 captured 或 synthetic")
    if len(ordered) < 2:
        raise ValueError("至少需要 2 行样本")
    event_kind, sample_kind, counter_type, modulus, clock_id = _common_fields(ordered)

    for index, sample in enumerate(ordered):
        if sample.sample_index < 0 or sample.counter_value < 0:
            raise ValueError("样本序号和计数器值不得为负数")
        if sample.counter_modulus != modulus or not (0 <= sample.counter_value < modulus):
            raise ValueError(f"样本 {sample.sample_index} 的计数值超出模数")
        if sample.gt_before < 0 or sample.gt_after < sample.gt_before:
            raise ValueError(f"样本 {sample.sample_index} 的 GT 区间无效")
        if index > 0:
            previous = ordered[index - 1]
            if sample.sample_index <= previous.sample_index:
                raise ValueError("sample_index 必须严格递增")
            if sample.gt_before < previous.gt_before or sample.gt_after < previous.gt_after:
                raise ValueError("GT 样本顺序回退；本工具不处理跨 GT 回绕或乱序")
            if sample.gt_after < previous.gt_before:
                raise ValueError("相邻 GT 区间倒序")

    deltas = [_counter_delta(a, b) for a, b in zip(ordered, ordered[1:])]
    if sample_kind == "event_bracket":
        for previous, current, delta in zip(ordered, ordered[1:], deltas):
            if delta != 1:
                raise ValueError(
                    f"event_bracket 必须逐事件采样且相邻计数增量为 1；"
                    f"样本 {previous.sample_index}→{current.sample_index} 的增量为 {delta}"
                )
    zero_delta_spans = sum(delta == 0 for delta in deltas)
    max_read_gap_upper = max(
        (current.gt_after - previous.gt_before for previous, current in zip(ordered, ordered[1:])),
        default=0,
    )
    min_event_period_ticks: int | None = None
    alias_checked = False
    alias_status = "不适用（单调计数器）"
    if min_event_period_us is not None:
        if not min_event_period_us.is_finite() or min_event_period_us <= 0:
            raise ValueError("min_event_period_us 必须为有限正数")
        min_event_period_ticks = int(
            (min_event_period_us * Decimal(gt_hz) / Decimal(1_000_000)).to_integral_value(
                rounding=ROUND_CEILING
            )
        )
    if counter_type == "cyclic_pointer":
        alias_checked = (
            sample_kind == "counter_snapshot"
            and min_event_period_ticks is not None
            and max_read_gap_upper < min_event_period_ticks
        )
        alias_status = (
            "CONDITIONAL_NO_ALIAS_BOUND"
            if alias_checked
            else "UNRESOLVED_CYCLIC_ALIAS"
        )
        if alias_checked:
            for previous, current, delta in zip(ordered, ordered[1:], deltas):
                if delta > 1:
                    raise ValueError(
                        "循环指针增量与独立最短事件周期/最大采样间隔界矛盾："
                        f"样本 {previous.sample_index}→{current.sample_index} 的模差为 {delta}，"
                        "但该界最多允许一个事件；拒绝推断唯一回绕"
                    )

    total_delta = sum(deltas)
    interval_rows: list[dict[str, object]] = []
    if sample_kind == "event_bracket":
        for previous, current, delta in zip(ordered, ordered[1:], deltas):
            if delta == 0:
                interval_rows.append(
                    {
                        "from_sample": previous.sample_index,
                        "to_sample": current.sample_index,
                        "counter_delta": 0,
                        "status": "COUNTER_DID_NOT_ADVANCE_OR_CYCLIC_ALIAS",
                    }
                )
                continue
            dt_lower = max(0, current.gt_before - previous.gt_after)
            dt_upper = current.gt_after - previous.gt_before
            if dt_upper < 0:
                raise ValueError("事件区间次序与样本序号不一致")
            dt_mid = Fraction(
                current.gt_before + current.gt_after
                - previous.gt_before
                - previous.gt_after,
                2,
            )
            interval_rows.append(
                {
                    "from_sample": previous.sample_index,
                    "to_sample": current.sample_index,
                    "counter_delta": delta,
                    "mean_period_us": _ticks_to_us(dt_mid / delta, gt_hz),
                    "mean_period_interval_us": {
                        "lower": _ticks_to_us(Fraction(dt_lower, delta), gt_hz),
                        "upper": _ticks_to_us(Fraction(dt_upper, delta), gt_hz),
                    },
                    "status": "BRACKETED",
                }
            )
        if total_delta > 0 and zero_delta_spans == 0:
            first, last = ordered[0], ordered[-1]
            elapsed_mid = Fraction(
                last.gt_before + last.gt_after - first.gt_before - first.gt_after,
                2,
            )
            elapsed_lower = max(0, last.gt_before - first.gt_after)
            elapsed_upper = last.gt_after - first.gt_before
            point_ticks = elapsed_mid / total_delta
            period_lower_ticks = Fraction(elapsed_lower, total_delta)
            period_upper_ticks = Fraction(elapsed_upper, total_delta)
            interval_method = "事件时间区间之差 / 计数增量"
        else:
            point_ticks = None
            period_lower_ticks = None
            period_upper_ticks = None
            interval_method = "不可计算：事件计数未推进或存在循环指针别名"
    else:
        first, last = ordered[0], ordered[-1]
        elapsed_mid = Fraction(
            last.gt_before + last.gt_after - first.gt_before - first.gt_after,
            2,
        )
        elapsed_lower = max(0, last.gt_before - first.gt_after)
        elapsed_upper = last.gt_after - first.gt_before
        if counter_type == "cyclic_pointer" and not alias_checked:
            point_ticks = elapsed_mid / total_delta if total_delta > 0 else None
            period_lower_ticks = None
            period_upper_ticks = None
            interval_method = "仅按观测到的指针变化数；完整帧数未知，区间不可用"
        elif total_delta > 0:
            point_ticks = elapsed_mid / total_delta
            if total_delta > 1:
                period_lower_ticks = Fraction(elapsed_lower, total_delta + 1)
                period_upper_ticks = Fraction(elapsed_upper, total_delta - 1)
            else:
                period_lower_ticks = Fraction(elapsed_lower, total_delta + 1)
                period_upper_ticks = None
            interval_method = "读计数器首末时刻区间；周期边界相位按 ±1 周期保守包络"
        else:
            point_ticks = None
            period_lower_ticks = None
            period_upper_ticks = None
            interval_method = "计数增量为 0"
        interval_rows = [
            {
                "from_sample": previous.sample_index,
                "to_sample": current.sample_index,
                "counter_delta": delta,
                "read_gap_upper_ticks": current.gt_after - previous.gt_before,
            }
            for previous, current, delta in zip(ordered, ordered[1:], deltas)
        ]

    if (
        counter_type == "cyclic_pointer"
        and sample_kind == "counter_snapshot"
        and alias_checked
        and min_event_period_ticks is not None
        and period_upper_ticks is not None
        and period_upper_ticks < min_event_period_ticks
    ):
        alias_checked = False
        alias_status = "CONFLICTING_MIN_EVENT_PERIOD"

    if point_ticks is None:
        observed_period_us = None
    else:
        observed_period_us = _ticks_to_us(point_ticks, gt_hz)
    if period_lower_ticks is None or period_upper_ticks is None:
        period_interval_us = None
    else:
        period_interval_us = {
            "lower": _ticks_to_us(period_lower_ticks, gt_hz),
            "upper": _ticks_to_us(period_upper_ticks, gt_hz),
        }

    trustworthy_count = (
        total_delta > 0
        and (counter_type == "monotonic" or alias_checked)
        and (sample_kind != "event_bracket" or zero_delta_spans == 0)
    )
    if origin == "synthetic":
        claim_status = "SYNTHETIC_ONLY_NOT_MEASURED"
        measured_value_us = None
        measured_interval_us = None
    elif not trustworthy_count or observed_period_us is None:
        claim_status = "CAPTURED_BUT_PERIOD_NOT_ESTABLISHED"
        measured_value_us = None
        measured_interval_us = None
    else:
        claim_status = "CAPTURED_ESTIMATE_REQUIRES_SOURCE_REVIEW"
        measured_value_us = observed_period_us
        measured_interval_us = period_interval_us

    return {
        "schema_version": 1,
        "origin": origin,
        "claim_status": claim_status,
        "event_kind": event_kind,
        "sample_kind": sample_kind,
        "counter_type": counter_type,
        "counter_modulus": modulus,
        "clock_id": clock_id,
        "gt_hz": gt_hz,
        "sample_count": len(ordered),
        "first_sample_index": ordered[0].sample_index,
        "last_sample_index": ordered[-1].sample_index,
        "observed_counter_delta": total_delta,
        "zero_delta_spans": zero_delta_spans,
        "max_read_gap_upper_ticks": max_read_gap_upper,
        "min_event_period_ticks_for_alias_check": min_event_period_ticks,
        "alias_status": alias_status,
        "interval_method": interval_method,
        "observed_period_us": observed_period_us,
        "observed_period_interval_us": period_interval_us,
        "measured_value_us": measured_value_us,
        "measured_interval_us": measured_interval_us,
        "intervals": interval_rows,
        "caveats": [
            "此程序只计算给定计数器/GT 样本；不能证明 event_kind 真正对应物理 SOF、HDMI VSYNC 或推理完成。",
            "cyclic_pointer 若未用最短事件周期约束最大轮询间隔，双缓冲指针可能漏掉偶数个切换沿。",
            "GT 频率误差按输入 gt_hz 线性传到周期结果；程序不校准 GT 时钟。",
            "合成输入永远不输出 measured_value_us；captured 标签由调用方提供，仍须审查采集来源。",
        ],
    }


def _demo_samples() -> list[Sample]:
    """生成明确标成合成的演示数据。"""
    samples: list[Sample] = []
    for index in range(10):
        event_tick = 100_000 + index * 16_667
        samples.append(
            Sample(
                sample_index=index,
                event_kind="camera_sof",
                sample_kind="event_bracket",
                counter_type="monotonic",
                counter_modulus=2**32,
                counter_value=index,
                clock_id="zynq_gt_demo",
                gt_before=event_tick - 2,
                gt_after=event_tick + 2,
            )
        )
    return samples


class _StructuredArgumentParser(argparse.ArgumentParser):
    """参数错误也以机器可读的未测量结果返回。"""

    def error(self, message: str) -> None:
        payload = {
            "schema_version": 1,
            "origin": None,
            "claim_status": "INVALID_INPUT_NOT_MEASURED",
            "measured_value_us": None,
            "error": message,
        }
        self._print_message(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
            sys.stderr,
        )
        self.exit(2)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = _StructuredArgumentParser(
        description="离线计算事件计数器相对 GT 的周期估计与区间，不接板、不操作硬件。"
    )
    parser.add_argument("csv", nargs="?", help="UTF-8 CSV 输入；与 --demo 二选一")
    parser.add_argument("--gt-hz", type=int, required=True, help="GT 计数频率，Hz；需由独立证据确认")
    parser.add_argument("--origin", choices=("captured", "synthetic"), help="输入来源标记")
    parser.add_argument(
        "--min-event-period-us",
        type=_parse_positive_finite_decimal,
        help="循环指针防漏沿检查所需的已知最短事件周期；必须为有限正数",
    )
    parser.add_argument("--demo", action="store_true", help="运行合成演示；结果明确不是实测")
    args = parser.parse_args(argv)
    try:
        if args.demo:
            if args.csv:
                raise ValueError("--demo 不得与 CSV 路径同时使用")
            samples = _demo_samples()
            origin = "synthetic"
            input_sha256 = None
            input_name = None
        else:
            if not args.csv:
                raise ValueError("必须提供 CSV 路径或 --demo")
            if args.origin is None:
                raise ValueError("读取 CSV 时必须显式提供 --origin captured 或 --origin synthetic")
            path = Path(args.csv)
            raw_bytes = path.read_bytes()
            input_sha256 = hashlib.sha256(raw_bytes).hexdigest()
            samples = read_csv(path)
            origin = args.origin
            input_name = path.name
        report = analyze_samples(samples, args.gt_hz, origin, args.min_event_period_us)
        report["input_name"] = input_name
        report["input_sha256"] = input_sha256
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        if origin == "synthetic":
            return 0
        return 0 if report["measured_value_us"] is not None else 1
    except (OSError, UnicodeError, csv.Error, ValueError, DecimalException, OverflowError) as exc:
        print(f"输入错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
