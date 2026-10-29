from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time


DEFAULT_PROFILE = Path(r"D:\wb-out-r3\task_l0\profile.json")
TARGET_CYCLES = 50_000_000
MEASURED_MS = 11_821.0
MEASURED_CYCLES_100MHZ = 1_182_100_000
BUS_BYTES_PER_CYCLE = 8
BASELINE_TILE_H = 8
BASELINE_TILE_W = 8


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _load_layers(profile: dict) -> list[dict]:
    layers = profile["static"]["per_layer"]
    return [layer for layer in layers if layer["op"] == "conv"]


def _write_bytes(layers: list[dict]) -> int:
    return sum(
        layer["out_ch"] * layer["out_hw"][0] * layer["out_hw"][1]
        for layer in layers
        if layer["op"] != "yolo_view"
    )


def _compute_cycles(layers: list[dict], lanes: int) -> int:
    if lanes <= 0:
        raise ValueError("lane 数必须为正数")
    return sum(
        _ceil_div(layer["out_ch"], lanes)
        * layer["out_hw"][0]
        * layer["out_hw"][1]
        * layer["in_ch"]
        * layer["k"]
        for layer in layers
    )


def _weight_bytes(layers: list[dict], tile_h: int, tile_w: int) -> int:
    if tile_h <= 0 or tile_w <= 0:
        raise ValueError("空间 tile 尺寸必须为正数")
    return sum(
        _ceil_div(layer["out_hw"][0], tile_h)
        * _ceil_div(layer["out_hw"][1], tile_w)
        * layer["weight_bytes"]
        for layer in layers
    )


def _spatial_compute_cycles(
    layers: list[dict],
    output_lanes: int,
    tile_h: int,
    tile_w: int,
    points_per_cycle: int,
    cross_rows: bool,
) -> int:
    if min(output_lanes, tile_h, tile_w, points_per_cycle) <= 0:
        raise ValueError("并行度与tile尺寸必须为正数")
    cycles = 0
    for layer in layers:
        output_groups = _ceil_div(layer["out_ch"], output_lanes)
        for tile_y in range(0, layer["out_hw"][0], tile_h):
            height = min(tile_h, layer["out_hw"][0] - tile_y)
            for tile_x in range(0, layer["out_hw"][1], tile_w):
                width = min(tile_w, layer["out_hw"][1] - tile_x)
                point_groups = (
                    _ceil_div(height * width, points_per_cycle)
                    if cross_rows
                    else height * _ceil_div(width, points_per_cycle)
                )
                cycles += (
                    output_groups
                    * point_groups
                    * layer["in_ch"]
                    * layer["k"]
                )
    return cycles


def _weight_segments(layers: list[dict], lanes: int, tile_h: int, tile_w: int) -> Counter:
    segments = Counter()
    for layer in layers:
        tile_count = _ceil_div(layer["out_hw"][0], tile_h) * _ceil_div(layer["out_hw"][1], tile_w)
        for group_start in range(0, layer["out_ch"], lanes):
            channels = min(lanes, layer["out_ch"] - group_start)
            segment_bytes = channels * layer["in_ch"] * layer["k"]
            segments[segment_bytes] += tile_count
    return segments


def _output_segments(layers: list[dict], lanes: int, tile_h: int, tile_w: int) -> Counter:
    segments = Counter()
    for layer in layers:
        channels = layer["out_ch"]
        height, width = layer["out_hw"]
        if layer["op"] == "yolo_view":
            continue
        if layer["op"] != "conv":
            segments[height * width] += channels
            continue
        for tile_y in range(0, height, tile_h):
            tile_height = min(tile_h, height - tile_y)
            for tile_x in range(0, width, tile_w):
                tile_width = min(tile_w, width - tile_x)
                for group_start in range(0, channels, lanes):
                    group_channels = min(lanes, channels - group_start)
                    segments[tile_width] += group_channels * tile_height
    return segments


@lru_cache(maxsize=None)
def _burst_bounds(segment_bytes: int, burst_bytes: int) -> tuple[int, int]:
    max_beats = burst_bytes // BUS_BYTES_PER_CYCLE
    if segment_bytes <= 0 or burst_bytes < BUS_BYTES_PER_CYCLE or burst_bytes > 128 or burst_bytes % BUS_BYTES_PER_CYCLE:
        raise ValueError("AXI3 burst 必须为8至128字节且是8字节整数倍")
    counts = []
    for start_in_4k in range(4096):
        first_lane = start_in_4k % BUS_BYTES_PER_CYCLE
        total_beats = _ceil_div(first_lane + segment_bytes, BUS_BYTES_PER_CYCLE)
        page_beats = 4096 // BUS_BYTES_PER_CYCLE - start_in_4k // BUS_BYTES_PER_CYCLE
        first_page_beats = min(total_beats, page_beats)
        bursts = _ceil_div(first_page_beats, max_beats)
        if total_beats > page_beats:
            bursts += _ceil_div(total_beats - page_beats, max_beats)
        counts.append(bursts)
    return min(counts), max(counts)


def _segment_summary(segments: Counter, burst_bytes: int) -> dict:
    count = sum(segments.values())
    byte_total = sum(length * repetitions for length, repetitions in segments.items())
    minimum = 0
    maximum = 0
    for length, repetitions in segments.items():
        low, high = _burst_bounds(length, burst_bytes)
        minimum += repetitions * low
        maximum += repetitions * high
    return {
        "segment_count": count,
        "segment_bytes": byte_total,
        "axi3_transactions_min_by_alignment": minimum,
        "axi3_transactions_max_by_alignment": maximum,
    }


def _candidate(
    all_layers: list[dict],
    conv_layers: list[dict],
    activation_read_bytes: int,
    output_write_bytes: int,
    baseline_residual_cycles: int,
    baseline_requests: int,
    lanes: int,
    tile_h: int,
    tile_w: int,
    burst_bytes: int,
    clock_hz: int,
    compute_cycles_override: int | None = None,
    compute_parallelism: str | None = None,
    cross_row_compute_cycles: int | None = None,
) -> dict:
    weights = _weight_bytes(conv_layers, tile_h, tile_w)
    traffic_bytes = weights + activation_read_bytes + output_write_bytes
    weight_transactions = _segment_summary(
        _weight_segments(conv_layers, lanes, tile_h, tile_w), burst_bytes
    )
    output_transactions = _segment_summary(
        _output_segments(all_layers, lanes, tile_h, tile_w), burst_bytes
    )
    activation_transactions = {
        "axi3_transactions_min_if_all_bytes_coalesce": _ceil_div(activation_read_bytes, burst_bytes),
        "axi3_transactions_max_if_byte_requests_remain": activation_read_bytes,
    }
    transactions_min = (
        weight_transactions["axi3_transactions_min_by_alignment"]
        + output_transactions["axi3_transactions_min_by_alignment"]
        + activation_transactions["axi3_transactions_min_if_all_bytes_coalesce"]
    )
    transactions_max = (
        weight_transactions["axi3_transactions_max_by_alignment"]
        + output_transactions["axi3_transactions_max_by_alignment"]
        + activation_transactions["axi3_transactions_max_if_byte_requests_remain"]
    )
    burst_payload_cycles = _ceil_div(traffic_bytes, BUS_BYTES_PER_CYCLE)
    uncoalesced_payload_cycles = (
        _ceil_div(weights + output_write_bytes, BUS_BYTES_PER_CYCLE)
        + activation_read_bytes
    )
    fitted_cycles_per_request = baseline_residual_cycles / baseline_requests
    compute_cycles = (
        _compute_cycles(conv_layers, lanes)
        if compute_cycles_override is None
        else compute_cycles_override
    )
    optimistic_cycles = (
        compute_cycles
        + burst_payload_cycles
        + baseline_residual_cycles * transactions_min / baseline_requests
    )
    conservative_cycles = (
        compute_cycles
        + uncoalesced_payload_cycles
        + baseline_residual_cycles * transactions_max / baseline_requests
    )
    residual_unscaled_cycles = (
        compute_cycles + uncoalesced_payload_cycles + baseline_residual_cycles
    )
    cross_row_optimistic_cycles = None
    cross_row_conservative_cycles = None
    if cross_row_compute_cycles is not None:
        cross_row_optimistic_cycles = optimistic_cycles - compute_cycles + cross_row_compute_cycles
        cross_row_conservative_cycles = conservative_cycles - compute_cycles + cross_row_compute_cycles
    return {
        "lanes": lanes,
        "compute_parallelism": compute_parallelism or f"{lanes} output channels",
        "tile_hw": [tile_h, tile_w],
        "burst_bytes": burst_bytes,
        "clock_hz": clock_hz,
        "compute_cycles": compute_cycles,
        "weight_reread_bytes": weights,
        "activation_read_bytes_assumed": activation_read_bytes,
        "output_write_bytes": output_write_bytes,
        "logical_traffic_bytes": traffic_bytes,
        "transactions_by_category": {
            "weight_segments": weight_transactions,
            "output_write_segments": output_transactions,
            "activation_reads_unknown_segmentation": activation_transactions,
            "total_min": transactions_min,
            "total_max": transactions_max,
        },
        "payload_cycles_if_all_traffic_bursted": burst_payload_cycles,
        "payload_cycles_if_activation_reads_stay_bytewise": uncoalesced_payload_cycles,
        "residual_scaling_sensitivity": {
            "baseline_residual_cycles": baseline_residual_cycles,
            "fitted_residual_cycles_per_baseline_request": fitted_cycles_per_request,
            "optimistic_all_residual_scales_with_transactions_cycles": optimistic_cycles,
            "conservative_segmenting_and_activation_bytewise_cycles": conservative_cycles,
            "sensitivity_if_residual_does_not_shrink_cycles": residual_unscaled_cycles,
            "range_is_not_a_confidence_interval": True,
        },
        "estimated_cycles": conservative_cycles,
        "estimated_seconds_per_frame": conservative_cycles / clock_hz,
        "estimated_fps": clock_hz / conservative_cycles,
        "optimistic_seconds_per_frame": optimistic_cycles / clock_hz,
        "optimistic_fps": clock_hz / optimistic_cycles,
        "residual_unscaled_seconds_per_frame": residual_unscaled_cycles / clock_hz,
        "compute_only_seconds": compute_cycles / clock_hz,
        "cross_row_optimistic_compute_cycles": cross_row_compute_cycles,
        "cross_row_optimistic_seconds_per_frame": (
            cross_row_optimistic_cycles / clock_hz
            if cross_row_optimistic_cycles is not None
            else None
        ),
        "cross_row_conservative_sensitivity_seconds_per_frame": (
            cross_row_conservative_cycles / clock_hz
            if cross_row_conservative_cycles is not None
            else None
        ),
    }


def build_model(profile: dict) -> dict:
    all_layers = profile["static"]["per_layer"]
    layers = _load_layers(profile)
    frozen = profile["frozen_budget_t07"]
    requests = int(frozen["requests_total"])
    writes_frozen = int(frozen["logical_write_bytes"])
    writes = _write_bytes(all_layers)
    reads = int(frozen["logical_read_bytes"])
    weight8 = _weight_bytes(layers, BASELINE_TILE_H, BASELINE_TILE_W)
    activation_reads = reads - weight8
    baseline_compute = _compute_cycles(layers, 8)
    baseline_payload_cycles = requests
    baseline_residual_cycles = MEASURED_CYCLES_100MHZ - baseline_compute - baseline_payload_cycles
    fixed_cycles_per_transaction = baseline_residual_cycles / requests
    reproduced_cycles = baseline_compute + baseline_payload_cycles + baseline_residual_cycles
    reproduced_ms = reproduced_cycles / 100_000.0

    scenarios = [
        _candidate(all_layers, layers, activation_reads, writes, baseline_residual_cycles, requests, 32, 32, 8, 16, 100_000_000),
        _candidate(all_layers, layers, activation_reads, writes, baseline_residual_cycles, requests, 128, 32, 8, 128, 100_000_000),
        _candidate(all_layers, layers, activation_reads, writes, baseline_residual_cycles, requests, 128, 32, 16, 128, 100_000_000),
        _candidate(
            all_layers,
            layers,
            activation_reads,
            writes,
            baseline_residual_cycles,
            requests,
            8,
            16,
            16,
            128,
            100_000_000,
            _spatial_compute_cycles(layers, 8, 16, 16, 16, False),
            "8 output channels x 16 spatial points",
            _spatial_compute_cycles(layers, 8, 16, 16, 16, True),
        ),
    ]

    return {
        "status": "MODEL_ONLY_NOT_CYCLE_SIMULATION",
        "source_frozen_commit": profile["target"]["frozen_commit_2b"],
        "source_frozen_clock_mhz": profile["target"]["frozen_fclk_mhz"],
        "target_frame_cycles_at_100mhz": TARGET_CYCLES,
        "measured_frame_ms_user_supplied": MEASURED_MS,
        "measured_cycles_assuming_100mhz": MEASURED_CYCLES_100MHZ,
        "frozen_budget_reproduced": {
            "conv_iterations": baseline_compute,
            "weight_reread_bytes": weight8,
            "output_write_bytes_independent_layer_sum": writes,
            "output_write_bytes_l0": writes_frozen,
            "logical_read_bytes": reads,
            "logical_requests": requests,
            "lower_bound_cycles": baseline_compute + 2 * requests,
        },
        "calibration_100mhz": {
            "baseline_lanes": 8,
            "baseline_tile_hw": [8, 8],
            "baseline_single_byte_transactions": requests,
            "baseline_payload_beats": baseline_payload_cycles,
            "baseline_residual_cycles": baseline_residual_cycles,
            "fixed_cycles_per_transaction_fitted": fixed_cycles_per_transaction,
            "reproduced_baseline_cycles": reproduced_cycles,
            "reproduced_baseline_ms": reproduced_ms,
            "user_measurement_residual_pct": (reproduced_ms - MEASURED_MS) / MEASURED_MS * 100.0,
            "clock_basis_note": "基线每个单字节AXI请求按至少1个64-bit payload beat计；剩余周期残差包含DDR往返、route/upsample状态机和PS观察，不能辨识其哪些部分随事务数缩减。冻结2B平台记录为50MHz，11,821ms按100MHz换算只用于敏感性模型。",
        },
        "lane_compute_only": {
            str(lanes): {
                "cycles": _compute_cycles(layers, lanes),
                "seconds_at_100mhz": _compute_cycles(layers, lanes) / 100_000_000,
            }
            for lanes in (8, 16, 32, 64, 96, 128, 160, 192, 220)
        },
        "spatial_tile_weight_bytes": {
            f"{height}x{width}": _weight_bytes(layers, height, width)
            for height, width in ((8, 8), (16, 8), (16, 16), (32, 8), (32, 16))
        },
        "scenarios": scenarios,
        "limitations": [
            "权重与输出写事务按层/tile/输出组或连续平面分段，并对4KiB内起始对齐逐字节枚举；激活读取L0未提供逐层地址映射，只给全部连续聚合下界与每字节一请求上界。",
            "候选字节载荷按traffic/8拍；单字节基线每个AXI请求按1个payload beat计。burst实际响应间隙、背压及各通路是否并发尚未验证。",
            "基线单点残差含DDR往返、route/upsample状态机和PS观察，不能辨识其随事务数缩减的比例；结果同时列出全缩放与完全不缩减敏感性，二者不是置信区间。",
            "激活读取量固定为L0逻辑读减8x8权重重读，假设扩大空间tile不改变总激活读取量。",
            "仅基线拟合残差为零；候选帧时间尚无周期仿真或实测，±20%预测精度未验证。",
            "未计层调度、BRAM端口冲突、tile预取、输出量化、PS解码/NMS和帧输入等待。",
            "大tile和128 lane资源数、100MHz时序均未综合；模型预测不是板上帧率。",
        ],
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _manifest_item(path: Path, label: str, committed: bool) -> dict:
    return {
        "path": str(path),
        "label": label,
        "sha256": _sha256(path),
        "hash_basis": "worktree_disk",
        "committed": committed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="依据L0冻结统计拟合离线推理吞吐候选")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--result-output", type=Path)
    parser.add_argument("--manifest-output", type=Path)
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()
    started = time.perf_counter()
    profile = json.loads(args.profile.read_text(encoding="utf-8"))
    result = build_model(profile)
    frozen = result["frozen_budget_reproduced"]
    expected = {
        "conv_iterations": 424_506_368,
        "weight_reread_bytes": 69_732_736,
        "output_write_bytes_independent_layer_sum": 11_382_150,
        "output_write_bytes_l0": 11_382_150,
        "lower_bound_cycles": 616_778_290,
    }
    for field, value in expected.items():
        if frozen[field] != value:
            raise SystemExit(f"冻结预算不匹配：{field}={frozen[field]}，期望{value}")
    cycles = result["lane_compute_only"]
    if cycles["96"]["cycles"] != 50_402_560 or cycles["128"]["cycles"] != 38_851_072:
        raise SystemExit("lane 分组计算不匹配独立复算锚点")
    if result["scenarios"][3]["cross_row_optimistic_compute_cycles"] != 26_907_840:
        raise SystemExit("8输出通道×16空间点跨行计算不匹配独立复算锚点")
    if result["scenarios"][3]["compute_cycles"] != 31_575_232:
        raise SystemExit("8输出通道×16空间点逐行计算不匹配独立复算锚点")
    expected_write_bytes = frozen["output_write_bytes_independent_layer_sum"]
    for scenario in result["scenarios"]:
        if scenario["transactions_by_category"]["weight_segments"]["segment_bytes"] != scenario["weight_reread_bytes"]:
            raise SystemExit("权重连续段字节数不等于tile模型权重重读数")
        if scenario["transactions_by_category"]["output_write_segments"]["segment_bytes"] != expected_write_bytes:
            raise SystemExit("逐层/tile输出写连续段不等于独立写量")
    if bool(args.result_output) != bool(args.manifest_output):
        raise SystemExit("--result-output 与 --manifest-output 必须同时提供")
    encoded_result = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.result_output:
        if args.result_output.exists() or args.manifest_output.exists():
            raise SystemExit("证据目标已存在；不得覆盖 RunId 产物")
        args.result_output.parent.mkdir(parents=True, exist_ok=True)
        args.result_output.write_text(encoded_result, encoding="utf-8", newline="\n")
        source_root = Path(__file__).resolve().parents[1]
        script = Path(__file__).resolve()
        design_doc = source_root / "docs" / "obsidian-project" / "02-方案设计" / "s2c_throughput_feasibility_20261029.md"
        artifacts = [
            _manifest_item(script, "模型脚本；新工作树未提交文件", False),
            _manifest_item(design_doc, "模型设计说明；新工作树未提交文件", False),
            _manifest_item(args.profile.resolve(), "L0模型输入；外部只读文件", False),
            _manifest_item(Path(r"D:\wb-out-r3\task_l0\REPORT.md"), "L0报告输入；外部只读文件", False),
            _manifest_item(args.result_output.resolve(), "模型运行结果", False),
        ]
        prior_failure_manifest = source_root / "report" / "evidence" / "S2C-M01" / "model_20261029_r01" / "manifest.json"
        artifacts.append(_manifest_item(prior_failure_manifest, "先前r01失败运行记录", False))
        manifest = {
            "schema_version": "s2c-model-evidence/1.0.0",
            "task_id": "S2C-M01",
            "run_id": args.run_id,
            "status": "MODEL_ONLY_NOT_CYCLE_SIMULATION",
            "source_identity": {
                "frozen_2b_commit": result["source_frozen_commit"],
                "worktree_head": "07c3d3958578b9cc9d3b8eae3758711fe08724c2",
                "branch": "codex/stage2c-throughput",
            },
            "hash_basis_policy": "每个hash条目显式标记worktree_disk；新工作树文件未提交，不能声明commit_blob。",
            "artifacts": artifacts,
            "prior_failed_run": {
                "run_id": "model_20261029_r01",
                "status": "FAILED",
                "exit_code": 1,
                "failure_summary": "输出连续段断言引用了main作用域外的writes变量；未生成result，详见r01 manifest和FAILURE_NOTE.md。",
            },
            "execution": {
                "command_argv": [sys.executable, "-B", str(script), *sys.argv[1:]],
                "exit_code": 0,
                "elapsed_seconds": round(time.perf_counter() - started, 6),
                "peak_memory_bytes": None,
                "logs_manifested": False,
            },
            "limitations": result["limitations"],
        }
        args.manifest_output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        print(encoded_result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
