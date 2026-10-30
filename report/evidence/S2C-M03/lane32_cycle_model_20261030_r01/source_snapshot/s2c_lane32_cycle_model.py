from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_PROFILE = Path(r"D:\wb-out-r3\task_l0\profile.json")
DEFAULT_REPO = Path(r"D:\FPGA_Competition\w2c")
EXPECTED_BUDGET = {
    "conv_iterations": 424_506_368,
    "weight_reread_bytes": 69_732_736,
    "logical_write_bytes": 11_382_150,
    "lower_bound_cycles": 616_778_290,
}
LANE_COUNT = 32
TILE_EDGE = 16
SEED = 0x11C02026
STALL_PATTERN = (0, 1, 2, 7, 3)


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sv_array(text: str, name: str) -> list[int]:
    match = re.search(rf"\b{name}\b[^=]*=\s*'\{{(.*?)\}};", text, re.S)
    _need(match is not None, f"descriptor 数组缺失：{name}")
    values = re.findall(r"(?:\d+'[hH][0-9a-fA-F_]+|\d+)", match.group(1))
    result = []
    for value in values:
        if "'h" in value.lower():
            result.append(int(value.lower().split("'h", 1)[1].replace("_", ""), 16))
        else:
            result.append(int(value))
    return result


class _BulkDelay:
    def __init__(self) -> None:
        self.state = SEED
        self.commands = 0
        self.delay_cycles = 0

    def next(self) -> int:
        delay = self.state & 3
        self.state = ((self.state << 1) & 0xFFFFFFFF) | (
            ((self.state >> 31) ^ (self.state >> 21) ^ (self.state >> 1) ^ self.state) & 1
        )
        self.commands += 1
        self.delay_cycles += delay
        return delay


def _bulk_segments(length: int, address: int, cap: int, delay: _BulkDelay) -> tuple[int, int, int]:
    bulk_bytes = 0
    bulk_commands = 0
    scalar_bytes = 0
    cursor = 0
    while cursor < length:
        current = address + cursor
        remaining = length - cursor
        chunk = min((remaining // 8) * 8, cap) if current % 8 == 0 else 0
        if chunk >= 8:
            bulk_bytes += chunk
            bulk_commands += 1
            delay.next()
            cursor += chunk
        else:
            scalar_bytes += 1
            cursor += 1
    return bulk_bytes, bulk_commands, scalar_bytes


def _feature_patch(
    layer: dict[str, Any], input_base: int, pad_left: int, pad_top: int,
    tile_x: int, tile_y: int, tile_w: int, tile_h: int, burst: int,
    delay: _BulkDelay,
) -> dict[str, int]:
    before_delay = delay.delay_cycles
    stride_y, stride_x = layer["stride"]
    kernel = math.isqrt(layer["k"])
    _need(kernel * kernel == layer["k"], f"layer {layer['layer']} conv kernel area is not square")
    patch_h = (tile_h - 1) * stride_y + kernel
    patch_w = (tile_w - 1) * stride_x + kernel
    in_h, in_w = layer["in_hw"]
    in_ch = layer["in_ch"]
    origin_y = tile_y * stride_y - pad_top
    origin_x = tile_x * stride_x - pad_left
    padding = 0
    scalar = 0
    bulk_bytes = 0
    bulk_commands = 0
    for channel in range(in_ch):
        plane = channel * in_h * in_w
        for py in range(patch_h):
            iy = origin_y + py
            if iy < 0 or iy >= in_h:
                padding += patch_w
                continue
            px = 0
            while px < patch_w:
                ix = origin_x + px
                if ix < 0 or ix >= in_w:
                    padding += 1
                    px += 1
                    continue
                run = min(patch_w - px, in_w - ix)
                address = input_base + plane + iy * in_w + ix
                run_bulk, run_commands, run_scalar = _bulk_segments(run, address, burst, delay)
                bulk_bytes += run_bulk
                bulk_commands += run_commands
                scalar += run_scalar
                px += run
    _need(bulk_bytes + scalar + padding == patch_h * patch_w * in_ch,
          f"layer {layer['layer']} feature patch 字节账本不闭合")
    return {
        "patch_h": patch_h,
        "patch_w": patch_w,
        "patch_bytes": patch_h * patch_w * in_ch,
        "padding_bytes": padding,
        "feature_read_bytes": bulk_bytes + scalar,
        "feature_bulk_bytes": bulk_bytes,
        "feature_bulk_commands": bulk_commands,
        "feature_delay_cycles": delay.delay_cycles - before_delay,
        "feature_legacy_requests": scalar,
    }


def _tile_axis(length: int) -> list[tuple[int, int]]:
    return [(start, min(TILE_EDGE, length - start)) for start in range(0, length, TILE_EDGE)]


def _conv_layer(
    layer: dict[str, Any], descriptor: dict[str, list[int]], burst: int,
    delay: _BulkDelay,
) -> dict[str, Any]:
    index = layer["layer"]
    out_ch = layer["out_ch"]
    out_h, out_w = layer["out_hw"]
    in_ch = layer["in_ch"]
    kernel_area = layer["k"]
    kernel = math.isqrt(kernel_area)
    _need(kernel * kernel == kernel_area, f"layer {index} conv kernel area is not square")
    reduction = in_ch * kernel_area
    stride_y, stride_x = layer["stride"]
    input_base = descriptor["S2A_INPUT_ADDRESS"][index * 2]
    weight_address = descriptor["S2A_GF8_WEIGHT_ADDRESS"][index]
    output_base = descriptor["S2A_OUTPUT_ADDRESS"][index]
    pad_left = descriptor["S2A_PADDING_LEFT"][index]
    pad_top = descriptor["S2A_PADDING_TOP"][index]
    tile_xs = _tile_axis(out_w)
    tile_ys = _tile_axis(out_h)
    totals: Counter[str] = Counter()
    first_tile = None
    for tile_y, tile_h in tile_ys:
        for tile_x, tile_w in tile_xs:
            feature = _feature_patch(
                layer, input_base, pad_left, pad_top,
                tile_x, tile_y, tile_w, tile_h, burst, delay,
            )
            totals.update(feature)
            tile_points = tile_w * tile_h
            totals["tile_count"] += 1
            totals["cycles_tile_prep"] += 1
            totals["cycles_feature_scan"] += (
                feature["padding_bytes"]
                + 3 * feature["feature_legacy_requests"]
                + feature["feature_bulk_bytes"]
                + 3 * feature["feature_bulk_commands"]
                + feature["feature_delay_cycles"]
            )
            totals["cycles_feature_terminal"] += 1
            for group_base in range(0, out_ch, LANE_COUNT):
                lanes = min(LANE_COUNT, out_ch - group_base)
                totals["output_groups"] += 1
                totals["cycles_weight_prep"] += 1
                weight_group_start = weight_address + group_base * reduction
                group_weight_bytes = lanes * reduction
                before_delay = delay.delay_cycles
                weight_bulk, weight_commands, weight_scalar = _bulk_segments(
                    group_weight_bytes, weight_group_start, burst, delay
                )
                weight_delay = delay.delay_cycles - before_delay
                totals["weight_read_bytes"] += group_weight_bytes
                totals["weight_bulk_bytes"] += weight_bulk
                totals["weight_bulk_commands"] += weight_commands
                totals["weight_legacy_requests"] += weight_scalar
                totals["cycles_weight_scan"] += (
                    3 * weight_scalar + weight_bulk + 3 * weight_commands + weight_delay
                )
                totals["weight_delay_cycles"] += weight_delay
                totals["cycles_weight_lane_terminal"] += lanes + 1
                totals["cycles_mq_prefetch"] += lanes
                totals["conv_iterations"] += tile_points * lanes * reduction
                totals["quantization_events"] += tile_points * lanes
                totals["pure_mac_lane_slot_cycles"] += tile_points * reduction
                totals["requant_cycles"] += tile_points * lanes
                totals["pointprep_cycles"] += tile_points
                totals["cycles_compute"] += (
                    tile_points * reduction + tile_points * lanes + tile_points
                )
                totals["weight_scan_events"] += weight_scalar + weight_commands + lanes + 1

                group_output_bulk = 0
                group_output_commands = 0
                group_output_scalar = 0
                before_delay = delay.delay_cycles
                for local_lane in range(lanes):
                    channel = group_base + local_lane
                    channel_base = output_base + channel * out_h * out_w
                    for row in range(tile_h):
                        global_y = tile_y + row
                        row_base = channel_base + global_y * out_w + tile_x
                        b, c, s = _bulk_segments(tile_w, row_base, burst, delay)
                        group_output_bulk += b
                        group_output_commands += c
                        group_output_scalar += s
                output_delay = delay.delay_cycles - before_delay
                totals["output_write_bytes"] += lanes * tile_points
                totals["output_bulk_bytes"] += group_output_bulk
                totals["output_bulk_commands"] += group_output_commands
                totals["output_legacy_requests"] += group_output_scalar
                totals["cycles_output_scan"] += (
                    3 * group_output_scalar + group_output_bulk
                    + 3 * group_output_commands + output_delay + lanes + 1
                )
                totals["output_scan_events"] += group_output_scalar + group_output_commands + lanes + 1
                totals["output_delay_cycles"] += output_delay
                totals["cycles_advance"] += 1
            if first_tile is None:
                first_tile = dict(totals)
                first_tile["cycles_total"] = sum(
                    value for key, value in first_tile.items() if key.startswith("cycles_")
                )
    totals["cycles_engine_start_validate_result"] += 3
    totals["cycles_total"] = sum(
        value for key, value in totals.items() if key.startswith("cycles_")
    )
    return {"layer": index, "totals": dict(totals), "first_tile": first_tile}


def _nonconv_workload(layers: list[dict[str, Any]]) -> dict[str, int]:
    totals = Counter()
    for layer in layers:
        op = layer["op"]
        output_bytes = layer["out_ch"] * math.prod(layer["out_hw"])
        if op == "route":
            totals["estimated_route_read_requests"] += output_bytes
            totals["estimated_route_write_requests"] += output_bytes
        elif op == "maxpool":
            taps = layer["k"]
            totals["estimated_maxpool_read_requests"] += output_bytes * taps
            totals["estimated_maxpool_write_requests"] += output_bytes
        elif op == "upsample":
            totals["estimated_upsample_read_requests"] += output_bytes
            totals["estimated_upsample_write_requests"] += output_bytes
    totals["estimated_nonconv_requests"] = sum(totals.values())
    return dict(totals)


def _stall_sum(request_count: int, first_index: int = 0) -> int:
    full, remainder = divmod(request_count, len(STALL_PATTERN))
    cycles = full * sum(STALL_PATTERN)
    cycles += sum(STALL_PATTERN[(first_index + offset) % len(STALL_PATTERN)] for offset in range(remainder))
    return cycles


def build_model(profile_path: Path, repo: Path, burst: int) -> dict[str, Any]:
    _need(8 <= burst <= 128 and burst % 8 == 0, "burst 大小须为 8..128 且 8 对齐")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    package_text = (repo / "src" / "s2a_network_descriptor_pkg.sv").read_text(encoding="utf-8")
    names = (
        "S2A_INPUT_ADDRESS", "S2A_OUTPUT_ADDRESS", "S2A_PADDING_LEFT", "S2A_PADDING_TOP",
        "S2A_GF8_WEIGHT_ADDRESS", "S2A_OP", "S2A_OUTPUT_LENGTH_BYTES",
    )
    descriptor = {name: _sv_array(package_text, name) for name in names}
    layers = profile["static"]["per_layer"]
    _need(len(layers) == 38, "L0 descriptor 层数不是 38")
    _need(sum(1 for x in layers if x["op"] == "conv") == 21, "L0 卷积层数不是 21")
    _need(descriptor["S2A_OP"] == [0 if x["op"] == "conv" else 1 if x["op"] == "maxpool" else 2 if x["op"] == "route" else 3 if x["op"] == "upsample" else 4 for x in layers],
          "RTL descriptor op 类型与 L0 层不一致")
    _need(len(descriptor["S2A_INPUT_ADDRESS"]) == 76, "descriptor 输入地址数组长度错误")
    delay = _BulkDelay()
    conv_results = []
    for layer in layers:
        if layer["op"] == "conv":
            conv_results.append(_conv_layer(layer, descriptor, burst, delay))
    conv = Counter()
    for result in conv_results:
        conv.update(result["totals"])
    _need(conv["conv_iterations"] == profile["static"]["total_macs"], "lane32 逐层MAC事件数与L0总MAC不符")
    _need(conv["pure_mac_lane_slot_cycles"] == 106_126_592, "lane32 纯MAC lane-slot周期数不符")
    _need(conv["requant_cycles"] == 6_147_206, "lane32 requant 周期数不符")
    _need(conv["pointprep_cycles"] == 192_153, "lane32 pointprep 周期数不符")
    _need(
        conv["cycles_compute"]
        == conv["pure_mac_lane_slot_cycles"] + conv["requant_cycles"] + conv["pointprep_cycles"]
        == 112_465_951,
        "lane32 compute 周期分解不闭合",
    )
    lane8_iterations = sum(
        math.ceil(layer["out_ch"] / 8) * math.prod(layer["out_hw"])
        * layer["in_ch"] * layer["k"]
        for layer in layers if layer["op"] == "conv"
    )
    lane8_weight_bytes = sum(
        math.ceil(layer["out_hw"][0] / 8) * math.ceil(layer["out_hw"][1] / 8)
        * layer["out_ch"] * layer["in_ch"] * layer["k"]
        for layer in layers if layer["op"] == "conv"
    )
    expected_writes = sum(
        layer["out_ch"] * math.prod(layer["out_hw"])
        for layer in layers if layer["op"] != "yolo_view"
    )
    _need(lane8_iterations == EXPECTED_BUDGET["conv_iterations"], "冻结 8 lane conv 迭代数复算错误")
    _need(lane8_weight_bytes == 69_732_736, "冻结 8x8 tile 权重重读数复算错误")
    _need(conv["weight_read_bytes"] != lane8_weight_bytes, "16x16 tile 模型异常复用了冻结8x8权重预算")
    _need(expected_writes == EXPECTED_BUDGET["logical_write_bytes"], "冻结逻辑写字节数复算错误")
    _need(conv["output_write_bytes"] == sum(
        x["out_ch"] * math.prod(x["out_hw"]) for x in layers if x["op"] == "conv"
    ), "卷积输出写量复算错误")
    _need(conv["weight_bulk_bytes"] + conv["weight_legacy_requests"] == conv["weight_read_bytes"], "卷积权重bulk/legacy字节不闭合")
    _need(conv["feature_bulk_bytes"] + conv["feature_legacy_requests"] == conv["feature_read_bytes"], "卷积feature bulk/legacy字节不闭合")
    _need(conv["output_bulk_bytes"] + conv["output_legacy_requests"] == conv["output_write_bytes"], "卷积output bulk/legacy字节不闭合")
    _need(
        conv["feature_delay_cycles"] + conv["weight_delay_cycles"] + conv["output_delay_cycles"]
        == delay.delay_cycles,
        "bulk LFSR 命令延迟总账不闭合",
    )

    frozen = profile["frozen_budget_t07"]
    _need(frozen["conv_iterations"] == EXPECTED_BUDGET["conv_iterations"], "冻结 conv 预算与指定值不同")
    _need(frozen["logical_write_bytes"] == EXPECTED_BUDGET["logical_write_bytes"], "冻结写预算与指定值不同")
    _need(frozen["lower_bound_cycles"] == EXPECTED_BUDGET["lower_bound_cycles"], "冻结下界与指定值不同")
    _need(frozen["requests_total"] == 96_135_961, "冻结请求数与指定值不同")
    budget_reproduced = {
        "conv_iterations_8lane": lane8_iterations,
        "weight_reread_bytes_8lane": lane8_weight_bytes,
        "logical_write_bytes": expected_writes,
        "lower_bound_cycles": frozen["conv_iterations"] + 2 * frozen["requests_total"],
        "lane32_total_macs": conv["conv_iterations"],
        "pure_mac_lane_slot_cycles": conv["pure_mac_lane_slot_cycles"],
        "requant_cycles": conv["requant_cycles"],
        "pointprep_cycles": conv["pointprep_cycles"],
        "cycles_compute": conv["cycles_compute"],
        "lane32_weight_reread_bytes_16x16_tile": conv["weight_read_bytes"],
    }
    _need(budget_reproduced["lower_bound_cycles"] == EXPECTED_BUDGET["lower_bound_cycles"], "冻结下界公式不闭合")

    nonconv = _nonconv_workload(layers)
    conv_legacy = {
        "input_read": sum(
            result["totals"].get("feature_legacy_requests", 0)
            for result in conv_results if result["layer"] == 0
        ),
        "weight_read": conv["weight_legacy_requests"],
        "feature_read": conv["feature_legacy_requests"] - sum(
            result["totals"].get("feature_legacy_requests", 0)
            for result in conv_results if result["layer"] == 0
        ),
        "feature_write": conv["output_legacy_requests"],
    }
    nonconv_reads = nonconv["estimated_nonconv_requests"] - sum(
        nonconv.get(key, 0) for key in ("estimated_route_write_requests", "estimated_maxpool_write_requests", "estimated_upsample_write_requests")
    )
    nonconv_writes = nonconv["estimated_nonconv_requests"] - nonconv_reads
    legacy_classes = {
        "input_read": conv_legacy["input_read"],
        "weight_read": conv_legacy["weight_read"],
        "feature_read": conv_legacy["feature_read"] + nonconv_reads,
        "feature_write": conv_legacy["feature_write"] + nonconv_writes,
    }
    class_order = ("input_read", "weight_read", "feature_read", "feature_write")
    class_stalls = {}
    for name in class_order:
        count = legacy_classes[name]
        class_stalls[name] = _stall_sum(count)
    total_legacy_stall = sum(class_stalls.values())
    conv_cycles = conv["cycles_total"]
    time_low_s = conv_cycles / 100_000_000
    time_high_s = (conv_cycles + nonconv["estimated_nonconv_requests"] * 4 + total_legacy_stall) / 100_000_000
    first_tile_cycles = conv_results[0]["first_tile"]["cycles_total"]
    first_tile_check = {
        "layer": conv_results[0]["layer"],
        "model_cycles": first_tile_cycles,
        "rtl08_measured_reference_cycles": 35_019,
        "rtl08_noncomparable_delta_percent": round((first_tile_cycles / 35_019 - 1) * 100, 3),
        "rtl10_physical_cycles": 36_993,
        "rtl10_noncomparable_delta_percent": round((first_tile_cycles / 36_993 - 1) * 100, 3),
        "note": "RTL08首tile参考为实测35019 cycles，其TB使用seed32B01C08并随机化cmd/r/w延迟、注入done stall；当前模型对应RTL11 TB seed11C02026。TB刺激与FSM/内存时序不同，不能用来校准±20%误差。RTL10物理参考36993 cycles的模型差异更大。此处只作非同条件健全性参考，不构成整网校准，也不表示板级帧率。",
    }
    result = {
        "model": "32 lane, 16x16 tile, local feature read 1 byte/cycle, single-outstanding RTL11 bulk memory model",
        "burst_bytes": burst,
        "frequency_mhz_for_time_conversion_only": 100,
        "frozen_budget_reproduction": budget_reproduced,
        "conv_layer_count": len(conv_results),
        "conv_layer_cycles_and_events": conv_results,
        "conv_total": dict(conv),
        "rtl11_bulk_delay_cycles": delay.delay_cycles,
        "nonconv_estimate": nonconv,
        "conv_legacy_requests": conv_legacy,
        "legacy_request_classes_for_T68_stall_model": legacy_classes,
        "T68_stall_cycles_by_class_estimate": class_stalls,
        "first_tile_sanity_reference": first_tile_check,
        "predictive_range": {
            "low_cycles_structural_conv_only": conv_cycles,
            "high_cycles_adds_estimated_nonconv_4cycles_per_request_and_T68_stalls": conv_cycles + nonconv["estimated_nonconv_requests"] * 4 + total_legacy_stall,
            "low_seconds_at_100mhz": time_low_s,
            "high_seconds_at_100mhz": time_high_s,
            "low_fps_at_100mhz": 1 / time_high_s if time_high_s else None,
            "high_fps_at_100mhz": 1 / time_low_s if time_low_s else None,
            "status": "未校准的结构模型；该范围是卷积核心模型与显式非卷积请求估算的场景括号，不是统计置信区间，也不保证覆盖实际整网周期。首tile只作为健全性核对，不能宣称整帧±20%精度。",
        },
        "limitations": [
            "非卷积层读取按算子语义估算请求量；route 映射、maxpool 填充/重复 tap 和 backend dispatch 周期未从整网周期实测校准。",
            "对conv，tile/权重组/feature row/output row上的bulk边界、每字节局部流与首Tile FSM状态计数均显式计算；T68 bulk延迟按固定seed LFSR序列计数。",
            "该测试平台单 outstanding、bulk每个命令逐字节每周期；DDR AXI桥吞吐、DDR读写时延及PS观察未由此模型表示。",
            "没有运行 RTL 仿真、综合或硬件；本模型输出不能替代整网RTL cycles、100MHz时序、功能等价或板级达标判定。",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 lane32 16x16 bulk 整帧周期结构预测")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--burst-bytes", type=int, action="append", default=[])
    args = parser.parse_args()
    bursts = args.burst_bytes or [128]
    results = [build_model(args.profile, args.repo, burst) for burst in bursts]
    print(json.dumps({"scenarios": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"模型错误：{exc}")
        raise SystemExit(2)
