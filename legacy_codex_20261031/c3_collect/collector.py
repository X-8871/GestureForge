#!/usr/bin/env python3
"""按既有 C3 CSV schema 采集单调事件计数器与 GT 读界。"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal


EVENT_KINDS = {
    "camera_sof",
    "vdma_s2mm_frame",
    "vdma_mm2s_readstore",
    "hdmi_vsync",
    "inference_done",
    "result_publish",
}
GT_MAX_VALUE = 2**64 - 1
CSV_COLUMNS = (
    "sample_index",
    "event_kind",
    "sample_kind",
    "counter_type",
    "counter_modulus",
    "counter_value",
    "clock_id",
    "gt_before",
    "gt_after",
)
Origin = Literal["synthetic", "host_callback_unverified"]


@dataclass(frozen=True)
class CollectorConfig:
    """描述单调计数器、GT 时钟和有界采集目标。"""

    event_kind: str
    counter_modulus: int
    clock_id: str
    min_duration_ticks: int
    min_event_count: int
    max_polls: int
    max_samples: int = 100_000
    max_gt_stall_polls: int = 8
    gt_hz: int | None = None
    gt_frequency_source: str | None = None

    def __post_init__(self) -> None:
        if self.event_kind not in EVENT_KINDS:
            raise ValueError(f"event_kind 不在既有 C3 schema 中：{self.event_kind!r}")
        if not self.clock_id.strip():
            raise ValueError("clock_id 不得为空")
        _require_config_int(self.counter_modulus, "counter_modulus", minimum=2)
        _require_config_int(self.min_duration_ticks, "min_duration_ticks", minimum=1)
        _require_config_int(self.min_event_count, "min_event_count", minimum=1)
        _require_config_int(self.max_polls, "max_polls", minimum=1)
        _require_config_int(self.max_samples, "max_samples", minimum=1)
        _require_config_int(self.max_gt_stall_polls, "max_gt_stall_polls", minimum=1)
        if self.gt_hz is not None:
            _require_config_int(self.gt_hz, "gt_hz", minimum=1)
        if self.gt_frequency_source is not None and not self.gt_frequency_source.strip():
            raise ValueError("gt_frequency_source 若提供则不得为空")


@dataclass(frozen=True)
class Snapshot:
    """一回计数器读取及围住它的 GT 读数。"""

    sample_index: int
    event_kind: str
    counter_modulus: int
    counter_value: int
    clock_id: str
    gt_before: int
    gt_after: int

    def as_csv_row(self) -> dict[str, str]:
        """转换为既有离线分析器可读取的行。"""
        return {
            "sample_index": str(self.sample_index),
            "event_kind": self.event_kind,
            "sample_kind": "counter_snapshot",
            "counter_type": "monotonic",
            "counter_modulus": str(self.counter_modulus),
            "counter_value": str(self.counter_value),
            "clock_id": self.clock_id,
            "gt_before": str(self.gt_before),
            "gt_after": str(self.gt_after),
        }


@dataclass(frozen=True)
class CollectionResult:
    """采集状态、原始样本和保守汇总；不代表测量验收。"""

    status: str
    origin: Origin
    source_identity: str
    config: CollectorConfig
    poll_count: int
    samples: tuple[Snapshot, ...]
    failure_phase: str | None = None
    error_type: str | None = None
    error_message: str | None = None

    @property
    def target_met(self) -> bool:
        return self.status == "TARGET_REACHED"

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    @property
    def cumulative_event_count(self) -> int:
        """返回首末计数差；不含首样本之前的绝对计数。"""
        if len(self.samples) < 2:
            return 0
        return self.samples[-1].counter_value - self.samples[0].counter_value

    @property
    def elapsed_gt_ticks(self) -> int:
        """返回首末 GT_before 的差，仅作为采样起点跨度附注。"""
        if len(self.samples) < 2:
            return 0
        return self.samples[-1].gt_before - self.samples[0].gt_before

    @property
    def elapsed_gt_bounds(self) -> dict[str, int]:
        """返回由首末读界得到的保守 GT 跨度范围。"""
        if not self.samples:
            return {"lower": 0, "upper": 0}
        first = self.samples[0]
        last = self.samples[-1]
        return {
            "lower": max(0, last.gt_before - first.gt_after),
            "upper": last.gt_after - first.gt_before,
        }

    @property
    def max_poll_gap_upper_ticks(self) -> int:
        """计算相邻快照读界之间的最大保守间隔上界。"""
        return max(
            (
                current.gt_after - previous.gt_before
                for previous, current in zip(self.samples, self.samples[1:])
            ),
            default=0,
        )

    def to_dict(self, include_samples: bool = True) -> dict[str, object]:
        """生成便于留存的机器可读摘要。"""
        if self.origin == "synthetic":
            gt_frequency_status = "SYNTHETIC_ONLY"
        elif self.config.gt_hz is None:
            gt_frequency_status = "NOT_PROVIDED"
        else:
            gt_frequency_status = "CALLER_SUPPLIED_UNVERIFIED"
        payload: dict[str, object] = {
            "schema_version": 1,
            "origin": self.origin,
            "source_identity": self.source_identity,
            "source_identity_status": "CALLER_SUPPLIED_UNVERIFIED",
            "event_kind": self.config.event_kind,
            "sample_kind": "counter_snapshot",
            "counter_type": "monotonic",
            "counter_modulus": self.config.counter_modulus,
            "clock_id": self.config.clock_id,
            "gt_hz": self.config.gt_hz,
            "gt_frequency_source": self.config.gt_frequency_source,
            "gt_frequency_status": gt_frequency_status,
            "min_duration_ticks": self.config.min_duration_ticks,
            "min_event_count": self.config.min_event_count,
            "max_polls": self.config.max_polls,
            "max_samples": self.config.max_samples,
            "max_gt_stall_polls": self.config.max_gt_stall_polls,
            "poll_count": self.poll_count,
            "sample_count": self.sample_count,
            "cumulative_event_count": self.cumulative_event_count,
            "event_count_scope": "last_counter_value - first_counter_value",
            "elapsed_gt_ticks": self.elapsed_gt_ticks,
            "elapsed_gt_ticks_basis": "last.gt_before - first.gt_before; start-to-start annotation only",
            "elapsed_gt_bounds": self.elapsed_gt_bounds,
            "max_poll_gap_upper_ticks": self.max_poll_gap_upper_ticks,
            "duration_target_reached": (
                self.elapsed_gt_bounds["lower"] >= self.config.min_duration_ticks
            ),
            "duration_target_basis": "elapsed_gt_bounds.lower",
            "count_target_reached": self.cumulative_event_count >= self.config.min_event_count,
            "target_met": self.target_met,
            "status": self.status,
            "measurement_claim": "COLLECTOR_OUTPUT_IS_NOT_T6_A03_ACCEPTANCE",
            "failure_phase": self.failure_phase,
            "error_type": self.error_type,
            "error_message": self.error_message,
        }
        if include_samples:
            payload["samples"] = [sample.as_csv_row() for sample in self.samples]
        return payload


class _CollectionError(Exception):
    """携带失败状态的采集校验异常。"""

    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status


def _require_config_int(value: object, field: str, minimum: int) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{field} 必须是大于等于 {minimum} 的整数")


def _require_read_int(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _CollectionError("INVALID_READ", f"{field} 回调必须返回整数")
    return value


class SnapshotCollector:
    """通过调用方注入的读取函数采集单调计数器快照。"""

    def __init__(
        self,
        config: CollectorConfig,
        read_counter: Callable[[], int],
        read_gt: Callable[[], int],
        source_identity: str,
        origin: Origin = "synthetic",
    ) -> None:
        if not callable(read_counter) or not callable(read_gt):
            raise ValueError("read_counter 和 read_gt 必须是可调用对象")
        if not source_identity.strip():
            raise ValueError("source_identity 不得为空")
        if origin not in {"synthetic", "host_callback_unverified"}:
            raise ValueError("origin 仅允许 synthetic 或 host_callback_unverified；不接受 captured")
        self.config = config
        self.read_counter = read_counter
        self.read_gt = read_gt
        self.source_identity = source_identity
        self.origin = origin

    def collect(self) -> CollectionResult:
        """有界轮询；失败时保留此前所有有效快照。"""
        samples: list[Snapshot] = []
        gt_stall_polls = 0

        def finish(
            status: str,
            poll_count: int,
            failure_phase: str | None = None,
            error: BaseException | None = None,
        ) -> CollectionResult:
            return CollectionResult(
                status=status,
                origin=self.origin,
                source_identity=self.source_identity,
                config=self.config,
                poll_count=poll_count,
                samples=tuple(samples),
                failure_phase=failure_phase,
                error_type=type(error).__name__ if error is not None else None,
                error_message=str(error) if error is not None else None,
            )

        for poll_index in range(self.config.max_polls):
            if len(samples) >= self.config.max_samples:
                return finish("SAMPLE_CAPACITY_REACHED", poll_index)
            phase = "gt_before"
            try:
                gt_before = _require_read_int(self.read_gt(), "GT_before")
                phase = "counter"
                counter_value = _require_read_int(self.read_counter(), "counter")
                phase = "gt_after"
                gt_after = _require_read_int(self.read_gt(), "GT_after")
            except _CollectionError as exc:
                return finish(exc.status, poll_index + 1, phase, exc)
            except Exception as exc:
                return finish("CALLBACK_ERROR", poll_index + 1, phase, exc)

            previous = samples[-1] if samples else None
            if (
                gt_before < 0
                or gt_after < 0
                or gt_before > GT_MAX_VALUE
                or gt_after > GT_MAX_VALUE
                or gt_after < gt_before
            ):
                error = _CollectionError(
                    "INVALID_GT_BRACKET",
                    "GT 读数必须位于 [0, 2^64-1] 且满足 gt_before <= gt_after",
                )
                return finish(error.status, poll_index + 1, phase, error)
            if previous is not None and gt_before < previous.gt_after:
                error = _CollectionError(
                    "GT_ROLLBACK",
                    "当前 GT_before 早于上一轮 GT_after；本采集器拒绝回退或回绕样本",
                )
                return finish(error.status, poll_index + 1, phase, error)
            if counter_value < 0 or counter_value >= self.config.counter_modulus:
                error = _CollectionError(
                    "INVALID_COUNTER_VALUE",
                    "counter_value 必须位于 [0, counter_modulus)",
                )
                return finish(error.status, poll_index + 1, "counter", error)
            if previous is not None and counter_value < previous.counter_value:
                error = _CollectionError(
                    "COUNTER_REGRESSION_OR_WRAP",
                    "单调计数器回退或回绕；该段不推断模差",
                )
                return finish(error.status, poll_index + 1, "counter", error)

            current = Snapshot(
                sample_index=len(samples),
                event_kind=self.config.event_kind,
                counter_modulus=self.config.counter_modulus,
                counter_value=counter_value,
                clock_id=self.config.clock_id,
                gt_before=gt_before,
                gt_after=gt_after,
            )
            samples.append(current)

            if previous is not None:
                if current.gt_after == previous.gt_after:
                    gt_stall_polls += 1
                else:
                    gt_stall_polls = 0

            result = finish("IN_PROGRESS", poll_index + 1)
            duration_reached = (
                result.elapsed_gt_bounds["lower"] >= self.config.min_duration_ticks
            )
            count_reached = result.cumulative_event_count >= self.config.min_event_count
            if duration_reached and count_reached:
                return finish("TARGET_REACHED", poll_index + 1)
            if gt_stall_polls >= self.config.max_gt_stall_polls:
                return finish(
                    "GT_NO_PROGRESS",
                    poll_index + 1,
                    "gt_after",
                    _CollectionError("GT_NO_PROGRESS", "GT_after 连续轮询无进展"),
                )

        return finish("MAX_POLLS_REACHED", self.config.max_polls)


def write_csv(result: CollectionResult, path: str | Path) -> Path:
    """以独占创建方式保存样本；目标已存在时绝不覆盖。"""
    output_path = Path(path)
    if not output_path.parent.is_dir():
        raise FileNotFoundError(f"CSV 父目录不存在：{output_path.parent}")
    with output_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for sample in result.samples:
            writer.writerow(sample.as_csv_row())
    return output_path


def _synthetic_demo() -> CollectionResult:
    """运行固定合成序列，不访问任何外部接口。"""
    state = {"gt": 0, "polls": 0}

    def read_gt() -> int:
        value = state["gt"]
        state["gt"] += 1
        return value

    def read_counter() -> int:
        state["polls"] += 1
        return state["polls"] // 5

    config = CollectorConfig(
        event_kind="camera_sof",
        counter_modulus=2**32,
        clock_id="zynq_gt_demo",
        min_duration_ticks=300,
        min_event_count=10,
        max_polls=200,
        max_samples=200,
        gt_hz=1_000_000,
        gt_frequency_source="synthetic-demo-only",
    )
    return SnapshotCollector(
        config,
        read_counter,
        read_gt,
        source_identity="synthetic-demo:constant-count-step",
        origin="synthetic",
    ).collect()


def main(argv: list[str] | None = None) -> int:
    """只提供明确合成演示的命令行入口。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="C3 单调计数器/GT 快照采集核心；CLI 仅运行合成演示，不连接硬件。"
    )
    parser.add_argument("--demo", action="store_true", help="运行固定合成演示")
    parser.add_argument("--csv", type=Path, help="以独占创建方式保存合成 CSV；已存在时拒绝覆盖")
    args = parser.parse_args(argv)
    if not args.demo:
        parser.error("本命令行只接受 --demo；真实采集需由后续集成方注入回调")

    result = _synthetic_demo()
    try:
        if args.csv is not None:
            write_csv(result, args.csv)
    except Exception as exc:
        report = {
            "cli_status": "OUTPUT_ERROR",
            "output_error_type": type(exc).__name__,
            "output_error": str(exc),
            "result": result.to_dict(include_samples=True),
        }
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 2

    report = result.to_dict(include_samples=args.csv is None)
    report["cli_status"] = "SYNTHETIC_DEMO_ONLY"
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if result.target_met else 1


if __name__ == "__main__":
    raise SystemExit(main())
