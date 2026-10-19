#!/usr/bin/env python3
"""按当前 S2B RTL 与冻结 descriptor 计算 tiny416 逻辑访问量和 MAC 下界。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ENGINE_FILES = (
    "src/s2b_conv_tile_engine.sv",
    "src/s2b_maxpool_engine.sv",
    "src/s2b_route_engine.sv",
    "src/s2b_upsample_engine.sv",
    "src/s2b_hp0_word_adapter.sv",
    "src/s2a_network_descriptor_pkg.sv",
    "src/s2b_stage2b_core.sv",
    "src/s2a_runtime_shell.sv",
    "src/s2a_control_csr.sv",
    "src/s2b_inference_top.sv",
    "src/s2b_control_csr.sv",
    "vitis/s2b_inference_app.c",
)
OP_NAMES = {0: "convolutional", 1: "maxpool", 2: "route", 3: "upsample", 4: "yolo"}
ARRAYS = (
    "S2A_OP",
    "S2A_INPUT_COUNT",
    "S2A_INPUT_SOURCE_INDEX",
    "S2A_INPUT_N",
    "S2A_INPUT_C",
    "S2A_INPUT_H",
    "S2A_INPUT_W",
    "S2A_OUTPUT_N",
    "S2A_OUTPUT_C",
    "S2A_OUTPUT_H",
    "S2A_OUTPUT_W",
    "S2A_KERNEL_H",
    "S2A_KERNEL_W",
    "S2A_STRIDE_H",
    "S2A_STRIDE_W",
    "S2A_PADDING_LEFT",
    "S2A_PADDING_TOP",
    "S2A_GROUP_COUNT",
    "S2A_INPUT_ROUTE_CHANNEL_START",
    "S2A_INPUT_ROUTE_CHANNEL_END",
    "S2A_MAXPOOL_DARKNET_PADDING",
    "S2A_UPSAMPLE_STRIDE",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def parse_sv_array(source: str, name: str) -> list[int]:
    match = re.search(rf"\b{name}\s*\[[^;]*?=\s*'\{{(.*?)\}};", source, re.S)
    if not match:
        raise ValueError(f"SV 数组不存在或格式不支持: {name}")
    values = re.findall(r"\b\d+'([hHdDbB])([0-9a-fA-F_]+)", match.group(1))
    bases = {"h": 16, "d": 10, "b": 2}
    return [int(raw.replace("_", ""), bases[base.lower()]) for base, raw in values]


def nested(values: list[int], row: int, col: int, width: int = 2) -> int:
    return values[row * width + col]


def dims(values: list[int], layer: int) -> tuple[int, int, int, int]:
    offset = layer * 2
    return tuple(values[offset : offset + 4])  # type: ignore[return-value]


def valid_span(origin: int, span: int, limit: int) -> int:
    return max(0, min(origin + span, limit) - max(origin, 0))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "deadline_budget.json")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    # 每次复算使用新RunId，原结果和历史失败不得被覆盖。
    if output.parent.exists() or output.name != "deadline_budget.json":
        raise ValueError("输出必须是新RunId下的deadline_budget.json，拒绝覆盖已有目录")
    if output.parent.parent.resolve(strict=True) != (repo / "report/evidence/S2B-T07").resolve(strict=True):
        raise ValueError("输出必须位于当前S2B-T07证据目录")
    descriptor_path = repo / "src/s2a_network_descriptor_pkg.sv"
    source_text = descriptor_path.read_text(encoding="utf-8")
    arrays = {name: parse_sv_array(source_text, name) for name in ARRAYS}
    layers_count = 38
    if len(arrays["S2A_OP"]) != layers_count:
        raise ValueError("descriptor layer count is not 38")
    if any(len(value) != layers_count * 2 for name, value in arrays.items() if name in (
        "S2A_INPUT_SOURCE_INDEX", "S2A_INPUT_N", "S2A_INPUT_C", "S2A_INPUT_H", "S2A_INPUT_W",
        "S2A_INPUT_ROUTE_CHANNEL_START", "S2A_INPUT_ROUTE_CHANNEL_END")):
        raise ValueError("descriptor two-input array length mismatch")

    inputs_by_layer: list[list[tuple[int, int, int, int]]] = []
    rows: list[dict[str, Any]] = []
    totals = {"logical_reads": 0, "logical_writes": 0, "macs": 0, "conv_compute_cycles": 0}
    for layer in range(layers_count):
        op = arrays["S2A_OP"][layer]
        input_count = arrays["S2A_INPUT_COUNT"][layer]
        layer_inputs: list[tuple[int, int, int, int]] = []
        for slot in range(input_count):
            n, c, h, w = (nested(arrays[f"S2A_INPUT_{axis}"], layer, slot) for axis in ("N", "C", "H", "W"))
            layer_inputs.append((n, c, h, w))
        inputs_by_layer.append(layer_inputs)
        n, oc, oh, ow = (arrays[f"S2A_OUTPUT_{axis}"][layer] for axis in ("N", "C", "H", "W"))
        output_elements = n * oc * oh * ow
        reads = writes = macs = compute_cycles = conv_feature_reads = conv_weight_reads = 0
        groups = arrays["S2A_GROUP_COUNT"][layer]
        kernel_h, kernel_w = arrays["S2A_KERNEL_H"][layer], arrays["S2A_KERNEL_W"][layer]
        stride_h, stride_w = arrays["S2A_STRIDE_H"][layer], arrays["S2A_STRIDE_W"][layer]

        if op == 0:
            if len(layer_inputs) != 1 or groups != 1:
                raise ValueError(f"unsupported convolution input/groups at layer {layer}")
            _, ic, ih, iw = layer_inputs[0]
            if min(kernel_h, kernel_w, stride_h, stride_w) <= 0:
                raise ValueError(f"invalid convolution geometry at layer {layer}")
            tile_rows = math.ceil(oh / 8)
            tile_cols = math.ceil(ow / 8)
            for tile_y in range(tile_rows):
                extent_h = min(8, oh - tile_y * 8)
                patch_h = (extent_h - 1) * stride_h + kernel_h
                input_origin_y = tile_y * 8 * stride_h - arrays["S2A_PADDING_TOP"][layer]
                in_h = valid_span(input_origin_y, patch_h, ih)
                for tile_x in range(tile_cols):
                    extent_w = min(8, ow - tile_x * 8)
                    patch_w = (extent_w - 1) * stride_w + kernel_w
                    input_origin_x = tile_x * 8 * stride_w - arrays["S2A_PADDING_LEFT"][layer]
                    in_w = valid_span(input_origin_x, patch_w, iw)
                    conv_feature_reads += ic * in_h * in_w
            tile_count = tile_rows * tile_cols
            reduction = ic * kernel_h * kernel_w
            conv_weight_reads = tile_count * oc * reduction
            reads = conv_feature_reads + conv_weight_reads
            writes = output_elements
            macs = output_elements * reduction
            compute_cycles = oh * ow * math.ceil(oc / 8) * reduction
        elif op == 1:
            if len(layer_inputs) != 1:
                raise ValueError(f"unsupported maxpool input count at layer {layer}")
            # 当前 tiny416 maxpool 固定 2x2 窗口；描述符冻结实际 padding 和尺寸。
            if (kernel_h, kernel_w, stride_h, stride_w) != (2, 2, 2, 2):
                raise ValueError(f"unsupported maxpool geometry at layer {layer}")
            reads = output_elements * 4
            writes = output_elements
        elif op == 2:
            selected = 0
            for slot, (in_n, _in_c, in_h, in_w) in enumerate(layer_inputs):
                start = nested(arrays["S2A_INPUT_ROUTE_CHANNEL_START"], layer, slot)
                end = nested(arrays["S2A_INPUT_ROUTE_CHANNEL_END"], layer, slot)
                if end < start:
                    raise ValueError(f"route channel interval reversed at layer {layer}")
                selected += in_n * (end - start) * in_h * in_w
            reads = selected
            writes = output_elements
            if reads != output_elements:
                raise ValueError(f"route selected read count does not match output at layer {layer}")
        elif op == 3:
            if len(layer_inputs) != 1:
                raise ValueError(f"unsupported upsample input count at layer {layer}")
            reads = output_elements
            writes = output_elements
        elif op == 4:
            # YOLO 层为 descriptor alias，不访问 PL feature memory。
            reads = writes = 0
        else:
            raise ValueError(f"unknown op code {op} at layer {layer}")

        row = {
            "layer_index": layer,
            "op_code": op,
            "op": OP_NAMES[op],
            "input_shapes_nchw": [list(shape) for shape in layer_inputs],
            "output_shape_nchw": [n, oc, oh, ow],
            "groups": groups,
            "kernel_hw": [kernel_h, kernel_w],
            "stride_hw": [stride_h, stride_w],
            "logical_feature_reads_bytes": reads,
            "logical_feature_writes_bytes": writes,
            "conv_feature_patch_reads_bytes": conv_feature_reads,
            "conv_weight_reads_bytes": conv_weight_reads,
            "mac_operations": macs,
            "conv_compute_state_cycles": compute_cycles,
        }
        rows.append(row)
        totals["logical_reads"] += reads
        totals["logical_writes"] += writes
        totals["macs"] += macs
        totals["conv_compute_cycles"] += compute_cycles

    maximum_cycles = (1 << 32) - 1
    minimum_request_state_cycles = 2 * (totals["logical_reads"] + totals["logical_writes"])
    optimistic_core_lower_bound = totals["conv_compute_cycles"] + minimum_request_state_cycles
    remaining_cycles = maximum_cycles - optimistic_core_lower_bound
    clock_hz = 50_000_000
    input_bytes = 519168
    weight_bytes = 5903100
    feature_offset = 0x01000000
    feature_end = 0x01ADADB8
    arena_bytes = 0x02000000
    aligned_weight_bytes = (weight_bytes + 63) & ~63
    aligned_feature_end = (feature_end + 63) & ~63
    head13_start, head13_bytes = 0x01A46100, 5070
    head26_start, head26_bytes = 0x01AD5E80, 20280
    source_bindings = []
    for rel in ENGINE_FILES:
        path = repo / rel
        source_bindings.append({"path": rel.replace("\\", "/"), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest_path = repo / "report/evidence/S2A-T01/tiny416_model_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_t07_path = repo / "report/evidence/S2B-T07/physical_contract_20261009_r02/layout_result.json"
    old_t07 = json.loads(old_t07_path.read_text(encoding="utf-8"))
    if len(old_t07["layers"]) != layers_count:
        raise ValueError("historical T07 model projection layer count mismatch")
    # descriptor 是计算输入；旧 T07 layout 仅作层数/形状交叉核对。
    for row, old in zip(rows, old_t07["layers"], strict=True):
        if row["output_shape_nchw"] != old["output_shape_nchw"]:
            raise ValueError(f"descriptor/layout output shape mismatch at layer {row['layer_index']}")
        if row["op"] != old["op"]:
            raise ValueError(f"descriptor/layout operation mismatch at layer {row['layer_index']}")

    result = {
        "schema_version": "s2b_tiny416_deadline_budget_offline_v1",
        "status": "OFFLINE_COUNT_ONLY_NO_BOARD_OR_HP_LATENCY_CLAIM",
        "source_commit": git(repo, "rev-parse", "HEAD"),
        "working_tree_note": "计算仅读取 descriptor/source；如其他文件有未提交变更，不纳入本计算。",
        "model": {"model_id": manifest["model"]["model_id"], "input_wh": manifest["model"]["input_wh"], "layer_count": layers_count},
        "sources": source_bindings,
        "source_references": {
            "src/s2b_conv_tile_engine.sv": ["69-96: tile/lane constants and FSM states", "2268-2290: feature patch bounds", "2750-2767: patch dimensions and scan setup", "2778-2835: feature/weight byte requests", "2905-2968: ST_COMPUTE iteration and requant", "2964-3010: per-byte output writes"],
            "src/s2b_maxpool_engine.sv": ["65-78: FSM states", "404-410: four window taps", "414-459: read/write request and response states"],
            "src/s2b_route_engine.sv": ["340-377: selected-input read and output-write transaction states"],
            "src/s2b_upsample_engine.sv": ["190-229: nearest source read and output write transaction states"],
            "src/s2b_hp0_word_adapter.sv": ["98-112: logical request capture and response match", "195-245: AXI handshakes and response ledger"],
            "src/s2a_network_descriptor_pkg.sv": ["4-40: layer/op contract and serial dispatch", "61-81: op/input count/source arrays", "241-403: input tensor dimensions", "528-608: output tensor dimensions", "616-704: kernels/strides/padding/groups", "824-920: pool/upsample/route parameters"],
        },
        "s2a_s2b_counting_scope": "S2B counts above are computed from the S2B engine loops and current descriptor. S2A and S2B source files are distinct revisions; no S2A latency/cycle estimate is reused or asserted equivalent. Model-level transaction counts use successful-path logical byte operations, independent of extra S2B validation/recovery FSM cycles.",
        "count_inputs": [
            {"path": "src/s2a_network_descriptor_pkg.sv", "role": "当前 S2B core 使用的冻结 descriptor ROM；解析每层 op/shape/geometry/input references。", "sha256": sha256(descriptor_path)},
            {"path": "report/evidence/S2A-T01/tiny416_model_manifest.json", "role": "模型身份校验，不从 S2A 引擎估算 S2B 工作量。", "sha256": sha256(manifest_path)},
            {"path": "report/evidence/S2B-T07/physical_contract_20261009_r02/layout_result.json", "role": "历史 T07 层数/操作/输出形状交叉核对；不作为访问量来源。", "sha256": sha256(old_t07_path)},
        ],
        "parameters": {"conv_tile_edge_pixels": 8, "conv_output_lanes": 8, "counter_width_bits": 32, "counter_max_cycles": maximum_cycles, "candidate_clock_hz_for_conversion_only": clock_hz},
        "deadline_counter_reference": {
            "path": "src/s2a_control_csr.sv",
            "lines": "69-70, 171-172, 244-253",
            "fact": "被当前 s2b_stage2b_core 内嵌的 runtime shell 使用；timeout_cycles / elapsed_cycles 均为 32 位，elapsed_cycles 从 START 清零，活跃期间比较 elapsed+1 与配置阈值。32 位非零最大阈值为 4,294,967,295 cycles。",
            "interpretation": "这是可配置 watchdog 的最大可表达阈值（约 85.8993459 秒 @ 声明 50 MHz），不证明模型必定在此时限内成功完成。",
            "clock_reference": {"path": "src/s2b_inference_top.sv", "line": 8, "freq_hz": clock_hz},
            "counter_max_seconds_at_declared_clock": maximum_cycles / clock_hz,
            "drain_counter": {"path": "src/s2b_control_csr.sv", "lines": "62, 340-343", "fact": "另有独立 32 位饱和 drain_cycles 和 drain_timeout；其实际清账时间/HP 响应延迟本次未测。"},
        },
        "static_cache_memory_ranges": {
            "source": {"path": "vitis/s2b_inference_app.c", "lines": "31-35, 217-226, 260-261", "sha256": sha256(repo / "vitis/s2b_inference_app.c")},
            "arena": {"start": 0, "end_exclusive": arena_bytes, "bytes": arena_bytes, "unit": "byte"},
            "input_flush": {"start": 0, "end_exclusive": input_bytes, "bytes": input_bytes, "aligned_64": input_bytes % 64 == 0},
            "weight_flush": {"start": 0x00100000, "end_exclusive": 0x00100000 + aligned_weight_bytes, "bytes": aligned_weight_bytes, "source_payload_bytes": weight_bytes, "alignment": 64},
            "feature_flush_invalidate": {"start": feature_offset, "end_exclusive": aligned_feature_end, "bytes": aligned_feature_end - feature_offset, "logical_end_exclusive": feature_end, "alignment": 64},
            "head13": {"start": head13_start, "end_exclusive": head13_start + head13_bytes, "bytes": head13_bytes, "contained_in_feature_logical_range": feature_offset <= head13_start < head13_start + head13_bytes <= feature_end},
            "head26": {"start": head26_start, "end_exclusive": head26_start + head26_bytes, "bytes": head26_bytes, "contained_in_feature_logical_range": feature_offset <= head26_start < head26_start + head26_bytes <= feature_end},
            "arena_remaining_after_feature_end": arena_bytes - feature_end,
            "interpretation": "静态 cache maintenance 覆盖真实 input/weights/feature/head 地址范围；arena 剩余区不构成逐字节探针要求。109/1000 完成后用同一 ELF 的全模型实际访问和 golden 对部署 cache 路径作判断；本清单不因 256B 小探针缺少 32MiB 覆盖而新增要求。",
        },
        "formulas": {
            "conv_feature_reads_bytes": "sum_tiles(IC * valid_in_bounds_patch_height * valid_in_bounds_patch_width); patch=(tile_output_extent-1)*stride+kernel; tile_origin=tile_start*stride-pad_top/left",
            "conv_weight_reads_bytes": "tile_count * OC * (IC*KH*KW); S2B scans each output-channel lane and reduction byte for each spatial tile",
            "conv_macs": "N*OH*OW*OC*IC*KH*KW/groups; model groups=1",
            "conv_compute_state_cycles": "OH*OW*ceil(OC/8)*(IC*KH*KW), counting only ST_COMPUTE iterations; excludes setup, feature/weight scan, requant, output, requests, and stalls",
            "maxpool_reads_writes_bytes": "reads=4*N*OC*OH*OW for 2x2; writes=N*OC*OH*OW",
            "route_reads_writes_bytes": "reads=sum_inputs(N*C_selected*H*W), writes=N*OC*OH*OW; descriptor equality checked",
            "upsample_reads_writes_bytes": "one logical source byte and one output byte per output element",
            "yolo_reads_writes_bytes": "zero; descriptor alias only",
            "logical_request_cycle_lower_bound": "2 cycles per one-byte logical request (request-state acceptance plus response-state minimum); no backend/HP wait is included; this is an optimistic engine-state lower bound",
        },
        "totals": totals,
        "request_budget": {
            "logical_read_requests": totals["logical_reads"],
            "logical_write_requests": totals["logical_writes"],
            "logical_requests_total": totals["logical_reads"] + totals["logical_writes"],
            "minimum_request_state_cycles": minimum_request_state_cycles,
            "optimistic_core_cycle_lower_bound": optimistic_core_lower_bound,
            "counter_max_cycles": maximum_cycles,
            "optimistic_remaining_cycles_after_compute_and_minimum_request_states": remaining_cycles,
            "optimistic_average_extra_cycles_per_request_headroom": remaining_cycles / (totals["logical_reads"] + totals["logical_writes"]),
            "counter_max_seconds_at_candidate_clock": maximum_cycles / clock_hz,
            "optimistic_lower_bound_seconds_at_candidate_clock": optimistic_core_lower_bound / clock_hz,
        },
        "known_lower_bound_and_unmeasured": {
            "known": ["descriptor MAC 运算数", "conv ST_COMPUTE 状态迭代数", "模型级逻辑单字节读写数", "请求状态至少各经过 request/response 两状态的乐观周期下界"],
            "unmeasured": ["HP0 每个 AR/R/AW/W/B 分段实际等待周期", "adapter/backend stall 周期", "DRain/ledger-empty 周期", "任务从 START 到 DONE 的完整 PL cycle 数", "计时器在当前运行图像上的实际余量", "FPGA 端每个逻辑 byte 请求的实际物理总线占用分布"],
            "not_a_hard_upper_bound": "任何已收集 host elapsed 都仅能作为混合接收期观察值；若在 PL 启动后才起计，或重复帧间 PS/UART 处理未计时，不能覆盖完整 PL walltime。观察值和经验分位数不能证明 HP 延迟上界或 deadline 硬上界。",
        },
        "layers": rows,
    }
    output.parent.mkdir()
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    script_path = Path(__file__).resolve()
    manifest_path = output.parent / "artifact_manifest.json"
    manifest = {
        "schema_version": "s2b_tiny416_deadline_budget_manifest_v1",
        "status": "OFFLINE_COUNT_ONLY_NO_BOARD_OR_HP_LATENCY_CLAIM",
        "source_commit": result["source_commit"],
        "artifacts": [
            {"path": script_path.name, "role": "reproducible offline calculator", "sha256": sha256(script_path), "bytes": script_path.stat().st_size},
            {"path": output.name, "role": "per-layer counts, aggregate optimistic lower bound, source bindings and explicit unknowns", "sha256": sha256(output), "bytes": output.stat().st_size},
        ],
        "source_bindings": source_bindings,
        "execution": {
            "command": subprocess.list2cmdline([sys.executable, "-B", str(script_path), "--repo", str(repo), "--output", str(output)]),
            "exit_code": 0,
            "python_version": subprocess.check_output([str(Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")), "--version"], text=True, stderr=subprocess.STDOUT).strip(),
            "device_access": False,
        },
        "limitations": ["未运行 Vivado、XSDB、UART、JTAG 或板卡任务。", "未知 HP 分段延迟与 DRain 延迟保留为未测；计算结果不是实际 deadline 或硬上界。"],
    }
    with manifest_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "layers": len(rows), "totals": totals, "request_budget": result["request_budget"], "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
