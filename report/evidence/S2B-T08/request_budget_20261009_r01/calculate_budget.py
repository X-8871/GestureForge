"""从当前 RTL 常量和冻结元数据计算正常完成任务的静态请求预算。"""

import hashlib
import json
import math
import platform
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
START = time.perf_counter()


def digest(path):
    """绑定实际文件原始字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    """只在首次运行的新证据目录创建 UTF-8 产物。"""
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


descriptor = ROOT / "src/s2a_network_descriptor_pkg.sv"
text = descriptor.read_text(encoding="utf-8")


def array(name, slots=1):
    """只解析本次消费的显式十六进制 RTL 常量数组。"""
    match = re.search(r"\b" + re.escape(name) + r"\s+\[0:37\](?:\[0:1\])?\s*=\s*'\{(.*?)\};", text, re.S)
    if not match:
        raise ValueError(name)
    values = [int(value, 16) for value in re.findall(r"\d+'h([0-9A-Fa-f]+)", match[1])]
    if len(values) != 38 * slots:
        raise ValueError((name, len(values)))
    return [values[i:i + slots] for i in range(0, len(values), slots)] if slots > 1 else values


scalar_names = [
    "OP", "OUTPUT_N", "OUTPUT_C", "OUTPUT_H", "OUTPUT_W", "OUTPUT_ADDRESS",
    "OUTPUT_LENGTH_BYTES", "OUTPUT_MEMORY_WRITE_REQUIRED", "KERNEL_H", "KERNEL_W",
    "STRIDE_H", "STRIDE_W", "PADDING_LEFT", "PADDING_RIGHT", "PADDING_TOP",
    "PADDING_BOTTOM", "GROUP_COUNT", "GF8_WEIGHT_OFFSET", "GF8_WEIGHT_BYTES",
    "GF8_RECORD_OFFSET", "GF8_WEIGHT_SCALE_OFFSET", "GF8_BIAS_OFFSET",
    "MAXPOOL_DARKNET_PADDING", "INPUT_COUNT", "T23_MQ_BASE", "T23_MQ_CHANNEL_COUNT",
]
arrays = {name: array("S2A_" + name) for name in scalar_names}
arrays.update({name: array("S2A_" + name, 2) for name in [
    "INPUT_N", "INPUT_C", "INPUT_H", "INPUT_W", "INPUT_SOURCE_INDEX",
    "ROUTE_CHANNEL_START", "ROUTE_CHANNEL_END",
]})
manifest_path = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
layout_path = ROOT / "report/evidence/S2B-T07/physical_contract_20261009_r02/layout_result.json"
layout = json.loads(layout_path.read_text(encoding="utf-8"))
projection = {
    "original_path": manifest_path.relative_to(ROOT).as_posix(),
    "original_sha256": digest(manifest_path),
    "status": manifest["status"],
    "model": manifest["model"],
    "address_map": manifest["address_map"],
    "gf8_package_metadata_only": manifest["bindings"]["gf8_package"],
    "layers": [{key: value for key, value in layer.items() if key in [
        "layer_index", "op", "input_tensor_indices", "input_shape_nchw", "output_shape_nchw",
        "kernel_hw", "stride_hw", "padding_lrtb", "groups", "gf8_parameter_offsets",
        "darknet_padding_parameter", "tensor_address", "tensor_length_bytes",
    ]} for layer in manifest["layers"]],
    "descriptor_sha256": digest(descriptor),
    "consumed_descriptor_arrays": arrays,
}
save("consumed_input_projection.json", projection)


def patch_axis(output_size, input_size, kernel, stride, pad):
    """扫描每个 tile 的连续 patch，保留边缘裁切和 tile 间重复。"""
    rows = []
    for start in range(0, output_size, 8):
        size = min(8, output_size - start)
        span = (size - 1) * stride + kernel
        origin = start * stride - pad
        valid = max(0, min(input_size, origin + span) - max(0, origin))
        rows.append({"tile_output_start": start, "tile_output_size": size,
                     "patch_origin": origin, "patch_span": span, "in_bounds_span": valid})
    return rows


rows = []
ops = ["convolutional", "maxpool", "route", "upsample", "yolo"]
for i in range(38):
    op = ops[arrays["OP"][i]]
    output_shape = [arrays[name][i] for name in ["OUTPUT_N", "OUTPUT_C", "OUTPUT_H", "OUTPUT_W"]]
    n, co, ho, wo = output_shape
    outputs = math.prod(output_shape)
    original = manifest["layers"][i]
    layout_row = layout["layers"][i]
    if (original["layer_index"] != i or original["op"] != op or
            original["output_shape_nchw"] != output_shape or n != 1 or
            original["tensor_length_bytes"] != outputs or
            original["tensor_address"] != arrays["OUTPUT_ADDRESS"][i] or
            layout_row["output_shape_nchw"] != output_shape or
            layout_row["tensor_length_bytes"] != outputs):
        raise ValueError(("shape/layout binding", i))
    ci, hi, wi = [arrays[name][i][0] for name in ["INPUT_C", "INPUT_H", "INPUT_W"]]
    row = {"layer_index": i, "op": op, "input_shape_nchw": [1, ci, hi, wi],
           "output_shape_nchw": output_shape, "feature_reads": 0, "weight_reads": 0,
           "writes": outputs if op != "yolo" else 0, "padding_scan_no_request": 0,
           "compute_reduction_cycles": 0, "requant_cycles": 0}
    if op == "convolutional":
        kh, kw, sy, sx, pt, pl = [arrays[name][i] for name in [
            "KERNEL_H", "KERNEL_W", "STRIDE_H", "STRIDE_W", "PADDING_TOP", "PADDING_LEFT"]]
        if original["input_shape_nchw"] != [1, ci, hi, wi] or arrays["GROUP_COUNT"][i] != 1:
            raise ValueError(("conv shape/groups", i))
        if original["kernel_hw"] != [kh, kw] or original["stride_hw"] != [sy, sx]:
            raise ValueError(("conv kernel/stride", i))
        if original["padding_lrtb"] != [pl, arrays["PADDING_RIGHT"][i], pt, arrays["PADDING_BOTTOM"][i]]:
            raise ValueError(("conv padding", i))
        offsets = original["gf8_parameter_offsets"]
        for key, name in [("record_offset", "GF8_RECORD_OFFSET"), ("weight_scale_offset", "GF8_WEIGHT_SCALE_OFFSET"),
                          ("fused_bias_offset", "GF8_BIAS_OFFSET"), ("quantized_weight_offset", "GF8_WEIGHT_OFFSET"),
                          ("quantized_weight_bytes", "GF8_WEIGHT_BYTES")]:
            if offsets[key] != arrays[name][i]:
                raise ValueError(("GF8 metadata", i, key))
        y_axis = patch_axis(ho, hi, kh, sy, pt)
        x_axis = patch_axis(wo, wi, kw, sx, pl)
        tile_count = len(y_axis) * len(x_axis)
        reduction = ci * kh * kw
        if co * reduction != arrays["GF8_WEIGHT_BYTES"][i]:
            raise ValueError(("weight extent", i))
        feature_reads = ci * sum(a["in_bounds_span"] for a in y_axis) * sum(a["in_bounds_span"] for a in x_axis)
        patch_scans = ci * sum(a["patch_span"] for a in y_axis) * sum(a["patch_span"] for a in x_axis)
        row.update(feature_reads=feature_reads, weight_reads=tile_count * co * reduction,
                   padding_scan_no_request=patch_scans - feature_reads, tile_count=tile_count,
                   output_channel_group_count=(co + 7) // 8, last_group_lane_count=((co - 1) % 8) + 1,
                   reduction_count=reduction, unique_weight_bytes=co * reduction,
                   gf8_parameter_offsets=offsets, patch_axis_y=y_axis, patch_axis_x=x_axis,
                   compute_reduction_cycles=((co + 7) // 8) * ho * wo * reduction,
                   requant_cycles=outputs, rom_bias_mq_prefetch_cycles=tile_count * co)
    elif op == "maxpool":
        kh, kw, sy, sx, pad = [arrays[name][i] for name in [
            "KERNEL_H", "KERNEL_W", "STRIDE_H", "STRIDE_W", "MAXPOOL_DARKNET_PADDING"]]
        valid_y = sum(0 <= y * sy - pad // 2 + ky < hi for y in range(ho) for ky in range(kh))
        valid_x = sum(0 <= x * sx - pad // 2 + kx < wi for x in range(wo) for kx in range(kw))
        if kh != 2 or kw != 2 or co != ci or valid_y * valid_x != 4 * ho * wo:
            raise ValueError(("frozen pool all four taps valid", i))
        row.update(feature_reads=4 * outputs, taps_per_output=4, padded_taps=0)
    elif op in ["route", "upsample"]:
        row.update(feature_reads=outputs)
        if op == "route":
            slices = []
            for slot in range(arrays["INPUT_COUNT"][i]):
                start = arrays["ROUTE_CHANNEL_START"][i][slot]
                end = arrays["ROUTE_CHANNEL_END"][i][slot]
                slices.append({"source_slot": slot, "source_layer_index": arrays["INPUT_SOURCE_INDEX"][i][slot],
                               "channel_start": start, "channel_end_exclusive": end,
                               "reads": (end - start) * ho * wo})
            if sum(s["reads"] for s in slices) != outputs:
                raise ValueError(("route slice total", i))
            row["source_slices"] = slices
        else:
            row["source_repeat_factor"] = outputs // (ci * hi * wi)
    elif op == "yolo" and arrays["OUTPUT_MEMORY_WRITE_REQUIRED"][i] != 0:
        raise ValueError(("YOLO alias unexpectedly writes", i))
    row["reads"] = row["feature_reads"] + row["weight_reads"]
    row["requests"] = row["reads"] + row["writes"]
    rows.append(row)

keys = ["feature_reads", "weight_reads", "reads", "writes", "requests", "padding_scan_no_request",
        "compute_reduction_cycles", "requant_cycles"]
totals = {key: sum(row[key] for row in rows) for key in keys}
by_op = {op: {key: sum(row[key] for row in rows if row["op"] == op) for key in keys} for op in ops}
request_count = totals["requests"]
deadline = (1 << 32) - 1
frequency = 50_000_000
# 每次请求的 master 入队周期及 network 注册响应周期不属于公开 mem_valid 服务区间。
nonservice_lower = 2 * request_count + totals["compute_reduction_cycles"] + totals["requant_cycles"] + totals["padding_scan_no_request"]
result = {
    "status": "STATIC_SUCCESS_PATH_REQUEST_COUNT_COMPLETE_DEPLOYMENT_NOT_PROVEN",
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    "count_scope": "单次正常完整38层任务；全部合法请求成功且无取消/超时/算术错误；失败时仅执行前缀",
    "totals": totals, "by_operator": by_op, "layers": rows,
    "physical_candidate": {
        "version": "s2b-physical-candidate/0.1.1", "frozen": False, "adapter_implemented": False,
        "AR_transactions": totals["reads"], "R_beats": totals["reads"],
        "AW_transactions": totals["writes"], "W_beats": totals["writes"], "B_responses": totals["writes"],
        "read_size": 0, "write_size": 2, "read_selected_bytes": totals["reads"],
        "write_selected_bytes": totals["writes"], "write_declared_transfer_bytes": totals["writes"] * 4,
        "data_channel_64bit_beat_slot_bytes": request_count * 8,
        "selected_data_fraction_of_data_slots": 0.125,
        "logical_request_to_axi_transaction_ratio": 1,
        "note": "读one-hot只需要一个size0子读；写size2单beat、one-hot WSTRB，无读改写；总线slot字节不等于DDR实际物理访问字节",
    },
    "deadline": {
        "max_cycles": deadline, "candidate_frequency_hz": frequency, "max_seconds_at_candidate_frequency": deadline / frequency,
        "service_definition": "公开mem_valid连续有效至mem_valid&&mem_ready握手的周期数，包含握手周期，最小1；包含adapter/HP/DDR/backpressure，但非HP独立实测延迟",
        "nonservice_cycles_lower_bound": nonservice_lower,
        "nonservice_lower_bound_parts": {"master_enqueue_and_network_registered_response": 2 * request_count,
                                         "conv_compute": totals["compute_reduction_cycles"],
                                         "conv_requant": totals["requant_cycles"],
                                         "conv_padding_scan": totals["padding_scan_no_request"]},
        "necessary_average_service_upper_cycles_ignoring_nonservice": deadline / request_count,
        "necessary_average_service_upper_cycles_with_nonservice_lower_bound": (deadline - nonservice_lower) / request_count,
        "condition": "Nread*average_read_service+Nwrite*average_write_service+Cnonservice+margin <= 4294967295；Cnonservice >= 本报告严格下界；此条件的下界满足不是充分条件",
        "sensitivity_lower_bounds": [{"assumed_uniform_logical_service_cycles": latency,
                                       "cycles_lower_bound": nonservice_lower + request_count * latency,
                                       "seconds_lower_bound_at_50MHz": (nonservice_lower + request_count * latency) / frequency,
                                       "necessary_condition_already_fails": nonservice_lower + request_count * latency > deadline}
                                      for latency in [1, 8, 16, 32, 48, 64, 80, 96, 128]],
        "normal_timeout_deployment_value": "NOT_MEASURED", "drain_timeout_deployment_value": "NOT_MEASURED",
    },
    "manual_anchors": {
        "layer0": {"feature_axis_sum": "25*17+16=441", "feature_reads": "3*441*441=583443",
                   "weight_reads": "26*26*32*27=584064", "writes": "32*208*208=1384448", "total": 2551955},
        "stride1_3x3_104": {"first_last_inbounds_axis": "9/9", "interior_tile_count": 11,
                            "axis_sum": "9+11*10+9=128", "padding_skips_per_channel": "130*130-128*128=516"},
        "13x13_1x1_tail30_channels": {"tiles": "2*2=4", "group_lanes": [8, 8, 8, 6],
                                     "feature_reads_per_input_channel": "(8+5)*(8+5)=169", "weight_reads_per_reduction": "4*30=120"},
        "26x26_1x1_layer36": {"feature_reads": "256*26*26=173056", "weight_reads": "16*30*256=122880",
                              "writes": "30*26*26=20280", "total": 316216},
        "pool9": {"read_taps": "128*52*52*4=1384448", "writes": "128*52*52=346112"},
        "upsample33": {"read_same_source_again": "每源byte重复4次，每个输出再次读1次，无跨输出缓存"},
    },
    "limitations": [
        "仅静态元数据计算；未运行RTL/软件测试、综合、完整仿真或硬件；非109样本/100样本/1000连续任务验收",
        "未读取外部GF8原件或真实样本；模型/参数包身份继承已冻结manifest，仅核对元数据与RTL",
        "请求数为成功路径精确值；内层deadline不足、错误或取消会截断，不代表当前物理平台可完成",
        "HP独立延迟、adapter固定延迟、DDR竞争、时序收敛、实际Cnonservice与任务耗时未测；无正常或排空deadline部署值",
        "非服务周期仅严格下界，遗漏其他scan、状态切换、MQ prefetch、逐输出dispatch、控制开销和余量；不可作为完成周期预测",
        "物理候选未冻结、adapter未实现；选中字节与64-bit通道slot不等于DRAM实际带宽或访问量",
        "DDR stall必须计入原32-bit全局计时，不暂停、不逐层重启、不延长内层期限、不降低100/1000指标",
    ],
    "execution": {"python": platform.python_version(), "duration_seconds": time.perf_counter() - START,
                  "calculation_runs": 1, "peak_memory": "NOT_MEASURED", "tool_calls": "NOT_MEASURED"},
}
save("request_budget_result.json", result)
print(json.dumps({"status": result["status"], "totals": totals, "by_operator": by_op,
                  "necessary_average_service_upper_cycles": result["deadline"]["necessary_average_service_upper_cycles_with_nonservice_lower_bound"],
                  "nonservice_lower_bound": nonservice_lower, "duration_seconds": result["execution"]["duration_seconds"]}, ensure_ascii=False, indent=2))
