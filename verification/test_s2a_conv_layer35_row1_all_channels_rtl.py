"""S2A-T37：逐值验证 tiny416 layer35 的 y=1 全行和全部输出通道。"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "386d47322dafce2223af0fadafc05781a0d9da98"
T17_BASE = "f0b7791d2db7b0a13126d3a0d3db586a01a294b1"
MANIFEST_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T16_PATH = ROOT / "report/evidence/S2A-T16/conv_requant_proof.json"
T17_PATH = ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json"
T20_PATH = ROOT / "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
WEIGHT_REPORT_PATH = ROOT / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
T16_SCRIPT_PATH = ROOT / "verification/s2a_conv_requant_proof.py"
D2_FORWARD_PATH = ROOT / "verification/s1_t02_d2_int8_forward.py"
T01_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T16_SHA = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
T17_SHA = "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"
T20_SHA = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
T23_SHA = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
G0_SHA = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
T16_SCRIPT_SHA = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
D2_FORWARD_SHA = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
WEIGHT_REPORT_SHA = "d867cd5dc7497f0de9db5c4e0643afd2e52d4c1e77632852487e8afceaa0dd80"
GF8_SHA = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
GF8_BYTES = 5903100
INPUT_BASE = 27706496
INPUT_BYTES = 259584
OUTPUT_BASE = 27966080
OUTPUT_BYTES = 173056
OUTPUT_SIZE = 26
OUTPUT_PIXELS = OUTPUT_SIZE * OUTPUT_SIZE
INPUT_CHANNELS = 384
OUTPUT_CHANNELS = 256
KERNEL_AREA = 9
REDUCTION = INPUT_CHANNELS * KERNEL_AREA
WEIGHT_BASE = 0x00100000
WEIGHT_OFFSET = 5010412
WEIGHT_LAYER_BYTES = OUTPUT_CHANNELS * REDUCTION
POINTS = tuple((1, x) for x in range(OUTPUT_SIZE))
SEED = 20260922
STALL_SEQUENCE = (0, 1, 2, 7, 3)
MAX_INT32 = (1 << 31) - 1
MIN_INT32 = -(1 << 31)
XILINX_BIN_DEFAULT = Path(r"D:\Xilinx\2026.1\Vivado\bin")
SOURCE_PATHS = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row1_all_channels.sv",
)
T17_SOURCE_HASHES = {
    "src/s2a_conv_engine.sv": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "sim/tb_s2a_conv_engine.sv": "2b642eb47cded4644e4e9ba3a1e3fa60d484cf795ec6e51dd8d4cfcc97d2f001",
    "verification/test_s2a_conv_engine_rtl.py": "adbb7e2574c50fd8e702e386a0898d27a0e4a16aebfc782436e386d56c768357",
    "src/int8_conv_tap_geometry.sv": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
}
EVIDENCE_PATH = ROOT / "report/evidence/S2A-T37/layer35_row1_all_channels.json"


class T37Error(RuntimeError):
    """报告冻结绑定、预检或工具运行失败。"""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"JSON 根节点不是对象：{path}")
    return value, _sha256(data)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T37Error(message)


def _signed_byte(value: int) -> int:
    return value if value < 128 else value - 256


def _round_half_away(value: float) -> int:
    rounded = math.floor(abs(value) + 0.5)
    return -rounded if value < 0.0 else rounded


class _XorShift32:
    """按 T17 固定 xorshift32 规则生成 INT8 输入 fixture。"""

    def __init__(self, seed: int) -> None:
        _require(0 < seed <= 0xFFFF_FFFF, "fixture seed 不在非零 uint32 范围")
        self.state = seed
        self.draws = 0

    def next_u32(self) -> int:
        value = self.state
        value = (value ^ ((value << 13) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        value ^= value >> 17
        value = (value ^ ((value << 5) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        self.state = value
        self.draws += 1
        return value

    def next_int8_byte(self) -> int:
        return (((self.next_u32() & 255) % 255) - 127) & 255


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise T37Error(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()



def _verify_t35_synthesis_reuse() -> dict[str, Any]:
    """只在 T35 综合输入、工具产物和摘要均逐项吻合时复用资源报告。"""
    evidence_path = ROOT / "report/evidence/S2A-T35/layer35_channel_probe.json"
    t35, evidence_sha = _json(evidence_path)
    _require(t35.get("status") == "PASS", "T35 证据不是 PASS，不能复用综合")
    synth = t35.get("synthesis", {})
    _require(synth.get("status") == "PASS" and
             synth.get("part") == "xc7z020clg400-1" and
             synth.get("top") == "s2a_conv_layer35_channel_probe" and
             synth.get("xdc") == "NOT_PROVIDED" and
             synth.get("phase", {}).get("exit_code") == 0,
             "T35 综合关键信息与当前 wrapper 不符")
    source_hashes = t35.get("bindings", {}).get("T35_source_hashes", {})
    synth_sources = SOURCE_PATHS[:5]
    for relative in synth_sources:
        expected = source_hashes.get(relative)
        _require(expected is not None and _sha_file(ROOT / relative) == expected,
                 f"T35 综合 RTL 源码哈希不匹配：{relative}")
    for relative, expected in source_hashes.items():
        _require((ROOT / relative).is_file() and _sha_file(ROOT / relative) == expected,
                 f"T35 绑定源文件已变化：{relative}")

    run_dir = Path(t35.get("paths", {}).get("run_dir", ""))
    phase_log = Path(synth.get("phase", {}).get("log_path", ""))
    artifact_table = t35.get("simulation", {}).get("artifacts", {})
    checked = {
        "synth.tcl": run_dir / "synth.tcl",
        "utilization.rpt": run_dir / "utilization.rpt",
        "vivado_synth.log": run_dir / "vivado_synth.log",
        "vivado_synth.jou": run_dir / "vivado_synth.jou",
        "vivado.stdout.log": phase_log,
    }
    artifacts: dict[str, dict[str, Any]] = {}
    for name, path in checked.items():
        expected = artifact_table.get(name)
        _require(path.is_file() and expected is not None and
                 path.stat().st_size == expected.get("bytes") and
                 _sha_file(path) == expected.get("sha256"),
                 f"T35 综合工件缺失或哈希不符：{path}")
        artifacts[name] = {"path": str(path), "bytes": path.stat().st_size,
                            "sha256": _sha_file(path)}

    tcl_text = checked["synth.tcl"].read_text(encoding="utf-8")
    read_sources = re.findall(r"^read_verilog -sv \{([^{}]+)\}$", tcl_text, re.MULTILINE)
    expected_sources = [str(ROOT / relative) for relative in synth_sources]
    _require(read_sources == expected_sources, "T35 synth.tcl RTL 清单或顺序不匹配")
    _require("synth_design -top s2a_conv_layer35_channel_probe -part xc7z020clg400-1 -flatten_hierarchy none"
             in tcl_text, "T35 synth.tcl top/part 不匹配")
    resources = _utilization(checked["utilization.rpt"])
    _require(resources == synth.get("resources"), "T35 utilization 报告与证据资源数不一致")
    return {
        "reuse_code": "REUSED_EXACT_RTL_SYNTHESIS_FROM_T35",
        "status": "PASS",
        "evidence": {"path": str(evidence_path), "sha256": evidence_sha},
        "part": synth["part"], "top": synth["top"],
        "xdc": "NOT_PROVIDED", "timing_conclusion": "N/A; standalone synthesis has no XDC",
        "resources": resources,
        "artifacts": artifacts,
        "source_hashes": {relative: source_hashes[relative] for relative in synth_sources},
        "phase": synth["phase"],
    }

def _load_frozen_inputs() -> dict[str, Any]:
    synthesis_reuse = _verify_t35_synthesis_reuse()
    head = _git("rev-parse", "HEAD")
    _require(_git("merge-base", "--is-ancestor", BASE_HEAD, head) == "",
             f"当前 HEAD 不是 T37 冻结基线后代：{head}")
    _require(_git("merge-base", "--is-ancestor", T17_BASE, head) == "",
             f"当前 HEAD 不是 T17 基线后代：{head}")
    manifest, manifest_sha = _json(MANIFEST_PATH)
    t16, t16_sha = _json(T16_PATH)
    t17, t17_sha = _json(T17_PATH)
    t20, t20_sha = _json(T20_PATH)
    t23, t23_sha = _json(T23_PATH)
    _require(manifest_sha == T01_SHA, "T01 manifest SHA-256 与冻结值不符")
    _require(t16_sha == T16_SHA, "T16 proof SHA-256 与冻结值不符")
    _require(t17_sha == T17_SHA and t17.get("result") == "PASS" and
             t17.get("baseline_head") == T17_BASE, "T17 证据冻结绑定不符")
    _require(t20_sha == T20_SHA and t20.get("result") == "PASS",
             "T20 证据冻结绑定不符")
    _require(t23_sha == T23_SHA and
             t23.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH",
             "T23 证据冻结绑定不符")
    _require(t17.get("bindings", {}).get("t01_manifest_sha256") == T01_SHA and
             t17.get("bindings", {}).get("t16_proof_sha256") == T16_SHA,
             "T17 内部冻结证据绑定不符")
    _require(_sha_file(G0_PATH) == G0_SHA, "S2A-T01 G0 冻结规格 SHA-256 不符")
    _require(_sha_file(T16_SCRIPT_PATH) == T16_SCRIPT_SHA,
             "T16 proof 脚本 SHA-256 不符")
    _require(_sha_file(D2_FORWARD_PATH) == D2_FORWARD_SHA,
             "D2 前向参考脚本 SHA-256 不符")
    weight_report, weight_report_sha = _json(WEIGHT_REPORT_PATH)
    _require(weight_report_sha == WEIGHT_REPORT_SHA, "阶段一权重报告 SHA-256 不符")
    for relative, expected in T17_SOURCE_HASHES.items():
        _require(_sha_file(ROOT / relative) == expected,
                 f"T17 冻结源 SHA-256 不符：{relative}")
    for binding in t23.get("source_bindings", []) + t23.get("tooling_bindings", []):
        bound_path = Path(str(binding["path"]))
        if not bound_path.is_absolute():
            bound_path = ROOT / bound_path
        _require(_sha_file(bound_path) == str(binding["sha256"]).lower(),
                 f"T23 来源绑定 SHA-256 不符：{binding['path']}")

    layers = {int(row["layer_index"]): row for row in manifest.get("layers", [])}
    _require(34 in layers and 35 in layers, "T01 manifest 缺少 layer34/35")
    layer34, layer35 = layers[34], layers[35]
    _require(layer34.get("op") == "route" and
             layer34.get("output_shape_nchw") == [1, 384, 26, 26] and
             layer34.get("tensor_address") == INPUT_BASE and
             layer34.get("tensor_length_bytes") == INPUT_BYTES,
             "T01 layer34 输入地址/shape/长度不符")
    _require(layer35.get("cfg_section") == 36 and
             layer35.get("op") == "convolutional" and
             layer35.get("input_tensor_indices") == [34] and
             layer35.get("input_shape_nchw") == [1, 384, 26, 26] and
             layer35.get("output_shape_nchw") == [1, 256, 26, 26] and
             layer35.get("tensor_address") == OUTPUT_BASE and
             layer35.get("tensor_length_bytes") == OUTPUT_BYTES and
             layer35.get("kernel_hw") == [3, 3] and
             layer35.get("stride_hw") == [1, 1] and
             layer35.get("padding_lrtb") == [1, 1, 1, 1] and
             layer35.get("padding_value_int8") == 0 and
             layer35.get("activation") == "leaky" and
             layer35.get("layout") == "NCHW" and
             layer35.get("accumulator_bits") == 32 and
             layer35.get("weight_layer_index") == 35,
             "T01 layer35 G0 卷积规格不符")
    offsets = layer35.get("gf8_parameter_offsets", {})
    _require(offsets.get("quantized_weight_offset") == WEIGHT_OFFSET and
             offsets.get("quantized_weight_bytes") == WEIGHT_LAYER_BYTES and
             offsets.get("fused_bias_offset") is not None,
             "T01 layer35 GF8 权重/融合偏置区间不符")
    _require(len(layer35.get("bias_accumulator_int32_per_output_channel", [])) == OUTPUT_CHANNELS and
             len(layer35.get("weight_scale_per_output_channel", [])) == OUTPUT_CHANNELS and
             len(layer35.get("fused_bias_float32_per_output_channel", [])) == OUTPUT_CHANNELS,
             "T01 layer35 逐通道 bias/scale/bias 长度不是256")
    _require(layer35.get("input_scale", 0) > 0 and layer35.get("output_scale", 0) > 0,
             "T01 layer35 输入或输出 scale 非正")
    frozen_protocol_vectors = manifest.get("operator_test_plan", {}).get("protocol_vectors", {})
    _require(frozen_protocol_vectors.get("memory_stall_cycles") == list(STALL_SEQUENCE),
             "T01 G0 memory stall 序列不等于 [0,1,2,7,3]")
    _require("exactly N cycles" in frozen_protocol_vectors["memory_stall_repeat"] and
             "first following ready-high edge" in frozen_protocol_vectors["memory_stall_repeat"],
             "T01 G0 memory stall 语义无法确认")

    t16_layer = next((row for row in t16.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    t23_layer = next((row for row in t23.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    _require(t16_layer is not None and t23_layer is not None and
             t16_layer.get("candidate_parameter_sha256") ==
             t23_layer.get("candidate_parameter_sha256"),
             "T16/T23 layer35 全通道参数摘要不一致")
    channels = t23_layer.get("channels", [])
    _require(len(channels) == OUTPUT_CHANNELS, "T23 layer35 通道数不是256")
    digest = hashlib.sha256()
    for channel_index, channel in enumerate(channels):
        _require(int(channel.get("channel", -1)) == channel_index,
                 "T23 layer35 输出通道编号不连续")
        digest.update((f"{channel_index},{int(channel['positive_Q'])},{int(channel['positive_M'])},"
                       f"{int(channel['negative_Q'])},{int(channel['negative_M'])}\n").encode("ascii"))
    _require(digest.hexdigest() == t16_layer.get("candidate_parameter_sha256"),
             "T23 全通道 M/Q 重算摘要与 T16 proof 不符")

    package_value = manifest["bindings"]["gf8_package"]
    package_path = Path(str(package_value["path"]))
    _require(package_path.is_absolute() and package_path.is_file(),
             f"GF8 精确路径不可读：{package_path}")
    package = package_path.read_bytes()
    _require(len(package) == GF8_BYTES and _sha256(package) == GF8_SHA and
             weight_report.get("package", {}).get("sha256") == GF8_SHA and
             weight_report.get("package", {}).get("bytes") == GF8_BYTES and
             t17.get("bindings", {}).get("gfint8w1_package_sha256") == GF8_SHA,
             "GF8 权重包与阶段一/T17 冻结摘要不符")
    weight_bytes = package[WEIGHT_OFFSET:WEIGHT_OFFSET + WEIGHT_LAYER_BYTES]
    _require(len(weight_bytes) == WEIGHT_LAYER_BYTES, "GF8 layer35 权重切片长度不符")
    fused_offset = int(offsets["fused_bias_offset"])
    fused_bytes = package[fused_offset:fused_offset + 4 * OUTPUT_CHANNELS]
    _require(len(fused_bytes) == 4 * OUTPUT_CHANNELS, "GF8 layer35 float32 融合偏置区间截断")
    fused_values = struct.unpack("<256f", fused_bytes)
    _require(fused_values == tuple(float(value) for value in
                                   layer35["fused_bias_float32_per_output_channel"]),
             "GF8/T01 layer35 float32 融合偏置逐通道不匹配")
    biases = tuple(int(value) for value in layer35["bias_accumulator_int32_per_output_channel"])
    _require(all(MIN_INT32 <= value <= MAX_INT32 for value in biases),
             "T01 layer35 INT32 bias 超范围")
    mq_values = []
    for row in channels:
        values = (int(row["positive_M"]), int(row["positive_Q"]),
                  int(row["negative_M"]), int(row["negative_Q"]))
        _require(0 < values[0] <= 0x3FFF_FFFF and 0 <= values[1] <= 47 and
                 0 < values[2] <= 0x3FFF_FFFF and 0 <= values[3] <= 47,
                 "T23 M/Q 参数超出 T17 engine 合法范围")
        mq_values.append(values)
    bindings = {
        "T01_manifest": {"path": str(MANIFEST_PATH), "sha256": manifest_sha},
        "G0_specification": {"path": str(G0_PATH), "sha256": G0_SHA},
        "T16_proof": {"path": str(T16_PATH), "sha256": t16_sha},
        "T17_engine_evidence": {"path": str(T17_PATH), "sha256": t17_sha},
        "T20_scheduler_evidence": {"path": str(T20_PATH), "sha256": t20_sha},
        "T23_parameter_table": {"path": str(T23_PATH), "sha256": t23_sha},
        "T16_script": {"path": str(T16_SCRIPT_PATH), "sha256": T16_SCRIPT_SHA},
        "D2_forward_reference": {"path": str(D2_FORWARD_PATH), "sha256": D2_FORWARD_SHA},
        "weight_report": {"path": str(WEIGHT_REPORT_PATH), "sha256": weight_report_sha},
        "GF8_package": {"path": str(package_path), "bytes": len(package), "sha256": GF8_SHA},
        "T17_source_hashes": T17_SOURCE_HASHES,
        "T37_baseline": {"commit": BASE_HEAD, "current_head": head},
        "T35_synthesis_evidence": synthesis_reuse["evidence"],
    }
    return {
        "manifest": manifest,
        "layer35": layer35,
        "channels": channels,
        "biases": biases,
        "mq_values": tuple(mq_values),
        "weight_bytes": weight_bytes,
        "weight_sha256": _sha256(weight_bytes),
        "bindings": bindings,
        "package_path": package_path,
        "layer35_weight_offset": WEIGHT_OFFSET,
        "fused_bias_offset": fused_offset,
        "synthesis_reuse": synthesis_reuse,
    }


def _expected_transfers(valid_taps: int) -> dict[str, Any]:
    transfer_counts = {"feature": valid_taps, "weight": valid_taps, "output": OUTPUT_CHANNELS * len(POINTS)}
    result: dict[str, Any] = {
        "output_cases": OUTPUT_CHANNELS * len(POINTS),
        "raw_int32_compares": OUTPUT_CHANNELS * len(POINTS),
        "quantized_int8_compares": OUTPUT_CHANNELS * len(POINTS),
        "feature_reads": valid_taps,
        "weight_reads": valid_taps,
        "output_writes": OUTPUT_CHANNELS * len(POINTS),
        "stall_sequence": list(STALL_SEQUENCE),
    }
    for name, transfers in transfer_counts.items():
        slots = [transfers // len(STALL_SEQUENCE) + int(slot < transfers % len(STALL_SEQUENCE))
                 for slot in range(len(STALL_SEQUENCE))]
        result[f"{name}_transfers"] = transfers
        result[f"{name}_slot_counts"] = slots
        result[f"{name}_stall_cycles"] = sum(count * STALL_SEQUENCE[slot]
                                              for slot, count in enumerate(slots))
    result["all_kernel_taps"] = OUTPUT_CHANNELS * len(POINTS) * REDUCTION
    result["padding_taps"] = result["all_kernel_taps"] - valid_taps
    result["point_valid_taps_per_input_channel"] = sum(
        sum(1 for ky in range(3) for kx in range(3)
            if 0 <= y + ky - 1 < OUTPUT_SIZE and 0 <= x + kx - 1 < OUTPUT_SIZE)
        for y, x in POINTS
    )
    result["point_padding_taps_per_input_channel"] = len(POINTS) * KERNEL_AREA - result["point_valid_taps_per_input_channel"]
    result["total_request_stall_cycles"] = sum(result[f"{name}_stall_cycles"]
                                               for name in transfer_counts)
    return result


def _build_oracle(inputs: dict[str, Any], progress: bool) -> dict[str, Any]:
    rng = _XorShift32(SEED)
    feature = bytes(rng.next_int8_byte() for _ in range(INPUT_BYTES))
    _require(len(feature) == INPUT_BYTES and 128 not in feature,
             "feature fixture 长度错误或含 -128")
    layer = inputs["layer35"]
    input_scale = float(layer["input_scale"])
    output_scale = float(layer["output_scale"])
    weight_scales = tuple(float(value) for value in layer["weight_scale_per_output_channel"])
    _require(len(weight_scales) == OUTPUT_CHANNELS, "T01 weight_scale 通道数错误")
    raw_values: list[int] = []
    quantized_values: list[int] = []
    vectors: list[tuple[int, int, int, int, int, int, int, int]] = []
    valid_taps = 0
    padding_taps = 0
    for oc in range(OUTPUT_CHANNELS):
        oc_bias = inputs["biases"][oc]
        pos_m, pos_q, neg_m, neg_q = inputs["mq_values"][oc]
        oc_weight_base = oc * REDUCTION
        real_scale = input_scale * weight_scales[oc]
        for y, x in POINTS:
            accumulator = oc_bias
            for channel in range(INPUT_CHANNELS):
                feature_channel_base = channel * OUTPUT_PIXELS
                weight_channel_base = oc_weight_base + channel * KERNEL_AREA
                for ky in range(3):
                    iy = y + ky - 1
                    for kx in range(3):
                        ix = x + kx - 1
                        if not (0 <= iy < OUTPUT_SIZE and 0 <= ix < OUTPUT_SIZE):
                            padding_taps += 1
                            continue
                        input_byte = feature[feature_channel_base + iy * OUTPUT_SIZE + ix]
                        weight_byte = inputs["weight_bytes"][weight_channel_base + ky * 3 + kx]
                        accumulator += _signed_byte(input_byte) * _signed_byte(weight_byte)
                        valid_taps += 1
            _require(MIN_INT32 <= accumulator <= MAX_INT32,
                     f"Python oracle INT32 overflow oc={oc} y={y} x={x}: {accumulator}")
            scaled = float(accumulator) * real_scale
            scaled = scaled / output_scale
            if scaled < 0.0:
                scaled *= 0.1
            d2_value = max(-127, min(127, _round_half_away(scaled)))
            negative = accumulator < 0
            multiplier, shift = (neg_m, neg_q) if negative else (pos_m, pos_q)
            product = abs(accumulator) * multiplier
            rounded = ((product + (1 << (shift - 1))) >> shift) if shift else product
            fixed_value = max(-127, min(127, -rounded if negative else rounded))
            _require(d2_value == fixed_value,
                     f"D2/T23 M/Q 不一致 oc={oc} y={y} x={x}: {d2_value} != {fixed_value}")
            raw_values.append(accumulator)
            quantized_values.append(d2_value)
            vectors.append((oc, y, x, oc_bias, pos_m, pos_q, neg_m, neg_q))
        if progress and ((oc + 1) % 32 == 0 or oc == OUTPUT_CHANNELS - 1):
            print(f"CPU_ORACLE channel={oc + 1}/{OUTPUT_CHANNELS} outputs={len(raw_values)}/{OUTPUT_CHANNELS * len(POINTS)}",
                  flush=True)
    valid_per_channel_per_input = sum(
        1 for y, x in POINTS for ky in range(3) for kx in range(3)
        if 0 <= y + ky - 1 < OUTPUT_SIZE and 0 <= x + kx - 1 < OUTPUT_SIZE)
    expected_valid = OUTPUT_CHANNELS * INPUT_CHANNELS * valid_per_channel_per_input
    expected_padding = OUTPUT_CHANNELS * len(POINTS) * REDUCTION - expected_valid
    _require(valid_taps == expected_valid and padding_taps == expected_padding,
             f"Python oracle 几何 tap 数错误 valid={valid_taps}/{expected_valid} "
             f"pad={padding_taps}/{expected_padding}")
    raw_bytes = b"".join(struct.pack("<i", value) for value in raw_values)
    quantized_bytes = bytes(value & 255 for value in quantized_values)
    combined = raw_bytes + quantized_bytes
    fixture = {
        "generator": "T17 xorshift32; INT8=((next_u32&255)%255)-127",
        "seed": SEED,
        "draw_count": rng.draws,
        "final_state": rng.state,
        "bytes": len(feature),
        "minimum_int8": min(_signed_byte(value) for value in feature),
        "maximum_int8": max(_signed_byte(value) for value in feature),
        "minus_128_count": 0,
        "sha256": _sha256(feature),
    }
    oracle = {
        "algorithm": "独立 Python INT32 NCHW 卷积 + D2 float64 舍入交叉核验 T23 M/Q",
        "reduction_order": "k=ic*9+ky*3+kx; feature=base+ic*676+iy*26+ix; weight=oc*3456+k",
        "raw_int32_count": len(raw_values),
        "quantized_int8_count": len(quantized_values),
        "raw_int32_min": min(raw_values),
        "raw_int32_max": max(raw_values),
        "valid_taps": valid_taps,
        "padding_taps": padding_taps,
        "d2_t23_match_count": len(quantized_values),
        "raw_int32_le_sha256": _sha256(raw_bytes),
        "quantized_int8_sha256": _sha256(quantized_bytes),
        "combined_golden_sha256": _sha256(combined),
    }
    return {
        "feature": feature,
        "vectors": vectors,
        "raw_values": raw_values,
        "quantized_values": quantized_values,
        "raw_bytes": raw_bytes,
        "quantized_bytes": quantized_bytes,
        "combined_golden": combined,
        "fixture": fixture,
        "oracle": oracle,
        "expected_counts": _expected_transfers(valid_taps),
    }


def _prepare(progress: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = _load_frozen_inputs()
    oracle = _build_oracle(inputs, progress=progress)
    return inputs, oracle


def _new_run_dir(path: Path) -> None:
    _require(path.is_absolute() and not path.exists(), f"TEMP 运行目录已存在或不是绝对路径：{path}")
    temp_root = Path(tempfile.gettempdir()).resolve()
    _require(Path(os.path.commonpath((str(temp_root), str(path.resolve())))) == temp_root,
             "运行目录必须位于系统 TEMP 下")
    _require(path.parent.is_dir(), f"运行目录的精确父目录不存在：{path.parent}")


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha_file(path)}


def _write_run_inputs(run_dir: Path, inputs: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    _write_new(run_dir / "feature_input.bin", oracle["feature"])
    _write_new(run_dir / "layer35_weights.bin", inputs["weight_bytes"])
    _write_new(run_dir / "golden.bin", oracle["combined_golden"])
    _write_vectors(run_dir / "vectors.txt", oracle["vectors"])
    fixture = dict(oracle["fixture"])
    fixture.update({
        "feature_path": str(run_dir / "feature_input.bin"),
        "weights_path": str(run_dir / "layer35_weights.bin"),
        "vectors_path": str(run_dir / "vectors.txt"),
        "golden_path": str(run_dir / "golden.bin"),
    })
    return fixture


def _run_static(args: argparse.Namespace) -> int:
    """在系统 TEMP 生成固定输入并执行 xvlog/xelab，不启动 xsim。"""
    run_dir = Path(args.run_dir)
    _new_run_dir(run_dir)
    _ensure_evidence_path()
    run_dir.mkdir()
    inputs, oracle = _prepare(progress=True)
    fixture = _write_run_inputs(run_dir, inputs, oracle)
    tool_bin = Path(args.xilinx_bin)
    _require(tool_bin.is_absolute() and tool_bin.is_dir(), f"Vivado bin 目录无效：{tool_bin}")
    source_paths = [ROOT / relative for relative in SOURCE_PATHS]
    phases = [
        _run_tool("xvlog", ["-sv", *map(str, source_paths)], run_dir, tool_bin, 600),
        _run_tool("xelab", ["-top", "tb_s2a_conv_layer35_row1_all_channels",
                            "-snapshot", "s2a_t37_snapshot"], run_dir, tool_bin, 600),
    ]
    source_hashes = {relative: _sha_file(ROOT / relative) for relative in
                     (*SOURCE_PATHS, Path(__file__).relative_to(ROOT).as_posix())}
    artifacts = {name: _artifact_record(run_dir / name) for name in
                 ("feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
                  "xvlog.stdout.log", "xelab.stdout.log")}
    static_record = {
        "schema": "GestureForge-S2A-T37-static-preflight-v1",
        "status": "PASS",
        "baseline": inputs["bindings"]["T37_baseline"],
        "xilinx_bin": str(tool_bin),
        "top": "tb_s2a_conv_layer35_row1_all_channels",
        "snapshot": "s2a_t37_snapshot",
        "source_hashes": source_hashes,
        "fixture": fixture,
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "phases": phases,
        "artifacts": artifacts,
    }
    with (run_dir / "static_preflight.json").open("x", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(static_record, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"result": "PASS", "static_preflight": str(run_dir / "static_preflight.json"),
                      "run_dir": str(run_dir), "tool_exit_codes":
                      {record["phase"]: record["exit_code"] for record in phases}},
                     ensure_ascii=False, indent=2), flush=True)
    return 0


def _reuse_static_preflight(run_dir: Path, args: argparse.Namespace,
                            inputs: dict[str, Any], oracle: dict[str, Any]) -> list[dict[str, Any]]:
    """核对静态阶段来源、fixture 和日志后返回可复用的 xvlog/xelab 记录。"""
    temp_root = Path(tempfile.gettempdir()).resolve()
    _require(run_dir.is_absolute() and run_dir.is_dir() and
             Path(os.path.commonpath((str(temp_root), str(run_dir.resolve())))) == temp_root,
             "静态运行目录必须是系统 TEMP 下的既有目录")
    record_path = run_dir / "static_preflight.json"
    record, _ = _json(record_path)
    _require(record.get("schema") == "GestureForge-S2A-T37-static-preflight-v1" and
             record.get("status") == "PASS" and
             record.get("baseline") == inputs["bindings"]["T37_baseline"] and
             Path(record.get("xilinx_bin", "")).resolve() == Path(args.xilinx_bin).resolve() and
             record.get("top") == "tb_s2a_conv_layer35_row1_all_channels" and
             record.get("snapshot") == "s2a_t37_snapshot",
             "静态预检与本次冻结基线/工具/top 不一致")
    expected_sources = (*SOURCE_PATHS, Path(__file__).relative_to(ROOT).as_posix())
    expected_hashes = {relative: _sha_file(ROOT / relative) for relative in expected_sources}
    _require(record.get("source_hashes") == expected_hashes,
             "静态预检后 RTL/testbench/runner 源码发生变化")
    expected_fixture = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": ("".join(" ".join(str(value) for value in row) + "\n"
                                  for row in oracle["vectors"])).encode("ascii"),
    }
    artifact_table = record.get("artifacts", {})
    for name, data in expected_fixture.items():
        path = run_dir / name
        expected = artifact_table.get(name, {})
        _require(path.is_file() and path.read_bytes() == data and
                 expected.get("bytes") == len(data) and expected.get("sha256") == _sha256(data),
                 f"静态预检 fixture/golden 不同：{name}")
    phases = record.get("phases", [])
    _require([phase.get("phase") for phase in phases] == ["xvlog", "xelab"] and
             all(phase.get("exit_code") == 0 for phase in phases),
             "静态 xvlog/xelab 阶段缺失或失败")
    for phase in phases:
        log_path = Path(phase["log_path"])
        expected = artifact_table.get(log_path.name, {})
        _require(log_path == run_dir / f"{phase['phase']}.stdout.log" and
                 log_path.is_file() and _sha_file(log_path) == expected.get("sha256"),
                 f"静态 {phase['phase']} 日志缺失或哈希不符")
    return phases


def _ensure_evidence_path() -> None:
    _require(not EVIDENCE_PATH.exists(), f"T37 证据路径已存在，拒绝覆盖：{EVIDENCE_PATH}")
    _require(EVIDENCE_PATH.parent.parent.is_dir(),
             f"T37 证据精确上级目录不存在：{EVIDENCE_PATH.parent.parent}")
    _require(not EVIDENCE_PATH.parent.exists() or EVIDENCE_PATH.parent.is_dir(),
             f"T37 证据父路径不是目录：{EVIDENCE_PATH.parent}")


def _write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)


def _quote(value: str) -> str:
    _require("\n" not in value and "\r" not in value, "命令参数包含换行")
    if any(ch in value for ch in " &()^"):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _run_tool(name: str, args: list[str], work: Path, tool_bin: Path,
              timeout_seconds: float, no_progress_seconds: float = 300.0,
              progress_re: re.Pattern[str] | None = None) -> dict[str, Any]:
    tool = tool_bin / f"{name}.bat"
    _require(tool.is_file(), f"找不到 Vivado 工具：{tool}")
    command = " ".join(_quote(value) for value in [str(tool), *args])
    full_command = f'cmd.exe /d /s /c "{command}"'
    log_path = work / f"{name}.stdout.log"
    started = time.monotonic()
    print(f"START {name} cwd={work} command={command}", flush=True)
    process = subprocess.Popen(
        full_command, cwd=work, shell=False, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def _read_lines() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            lines.put(line)
        lines.put(None)

    reader = threading.Thread(target=_read_lines, daemon=True)
    reader.start()
    last_progress = time.monotonic()
    seen_end = False
    output_tail: list[str] = []
    with log_path.open("x", encoding="utf-8", newline="\n") as log:
        while not seen_end or process.poll() is None:
            if time.monotonic() - started > timeout_seconds:
                process.kill()
                raise T37Error(f"{name} 整体超时；日志：{log_path}")
            try:
                line = lines.get(timeout=1.0)
            except queue.Empty:
                if name == "xsim" and time.monotonic() - last_progress > no_progress_seconds:
                    process.kill()
                    raise T37Error(f"xsim 连续 {no_progress_seconds:.0f}s 无进度；日志：{log_path}")
                continue
            if line is None:
                seen_end = True
                continue
            log.write(line)
            log.flush()
            output_tail.append(line)
            if len(output_tail) > 80:
                output_tail.pop(0)
            if progress_re is not None and progress_re.search(line):
                last_progress = time.monotonic()
                print(line.rstrip(), flush=True)
    reader.join(timeout=5)
    exit_code = process.wait()
    output = "".join(output_tail)
    elapsed = round(time.monotonic() - started, 3)
    _require(exit_code == 0 and "ERROR:" not in output and "FATAL:" not in output,
             f"{name} exit={exit_code}；日志：{log_path}；末尾：{output[-2000:]}")
    version = next((line.strip() for line in output.splitlines()
                    if any(tag in line.lower() for tag in ("xvlog v", "xelab v", "xsim v", "vivado v"))),
                   "unknown")
    print(f"END {name} exit={exit_code} seconds={elapsed} log={log_path}", flush=True)
    return {"phase": name, "command": [str(tool), *args], "exit_code": exit_code,
            "tool_version": version, "seconds": elapsed, "log_path": str(log_path)}


def _parse_summary(text: str) -> dict[str, int]:
    rows = re.findall(r"^PASS T37 (.+)$", text, re.MULTILINE)
    _require(len(rows) == 1, f"xsim 缺少唯一 PASS T37 摘要，条数={len(rows)}")
    return {key: int(value) for key, value in re.findall(r"([a-z0-9_]+)=([0-9]+)", rows[0])}


def _validate_summary(summary: dict[str, int], expected: dict[str, Any]) -> None:
    fields = {
        "outputs": expected["output_cases"],
        "raw": expected["raw_int32_compares"],
        "feature_reads": expected["feature_reads"],
        "weight_reads": expected["weight_reads"],
        "output_writes": expected["output_writes"],
        "padding": expected["padding_taps"],
        "taps": expected["all_kernel_taps"],
        "request_stalls": expected["total_request_stall_cycles"],
    }
    for class_name in ("feature", "weight", "output"):
        fields[f"{class_name}_transfers"] = expected[f"{class_name}_transfers"]
        fields[f"{class_name}_stall_cycles"] = expected[f"{class_name}_stall_cycles"]
        for slot, count in enumerate(expected[f"{class_name}_slot_counts"]):
            fields[f"{class_name}_slot{slot}"] = count
    for key, value in fields.items():
        _require(summary.get(key) == value,
                 f"xsim 计数不符 {key}: {summary.get(key)} != {value}")
    _require(summary.get("error_mask") == 0x46 and summary.get("fault_responses") == 3,
             "错误响应 smoke 未覆盖 feature/weight/output 或 error code mask 不符")
    _require(summary.get("abort_cancel") >= 1 and summary.get("reset_cancel") >= 1 and
             summary.get("recovery") == 1, "abort/reset/cancel/recovery smoke 不完整")


def _utilization(path: Path) -> dict[str, int]:
    report = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "lut": r"^\|\s*Slice LUTs\*?\s*\|\s*([\d,]+)",
        "ff": r"^\|\s*Slice Registers\s*\|\s*([\d,]+)",
        "bram_tile": r"^\|\s*Block RAM Tile\s*\|\s*([\d,]+)",
        "dsp": r"^\|\s*DSPs\s*\|\s*([\d,]+)",
    }
    values: dict[str, int] = {}
    for key, pattern in patterns.items():
        found = re.search(pattern, report, re.MULTILINE | re.IGNORECASE)
        _require(found is not None, f"utilization.rpt 缺少资源项：{key}")
        values[key] = int(found.group(1).replace(",", ""))
    return values


def _evidence_bindings(inputs: dict[str, Any], oracle: dict[str, Any]) -> dict[str, Any]:
    layer = inputs["layer35"]
    return {
        **inputs["bindings"],
        "T37_source_hashes": {relative: _sha_file(ROOT / relative)
                              for relative in (*SOURCE_PATHS, Path(__file__).relative_to(ROOT).as_posix())},
        "weight_layer35": {"byte_offset": inputs["layer35_weight_offset"],
                           "bytes": len(inputs["weight_bytes"]),
                           "sha256": inputs["weight_sha256"]},
        "model": {"name": "tiny416", "cfg_section": layer["cfg_section"],
                  "input_tensor": {"base": INPUT_BASE, "bytes": INPUT_BYTES,
                                   "shape_nchw": [1, 384, 26, 26]},
                  "output_tensor": {"base": OUTPUT_BASE, "bytes": OUTPUT_BYTES,
                                    "shape_nchw": [1, 256, 26, 26]},
                  "kernel_hw": [3, 3], "stride_hw": [1, 1], "padding_lrtb": [1, 1, 1, 1],
                  "padding_int8": 0, "layout": "NCHW", "accumulator_bits": 32,
                  "activation": "leaky", "input_scale": layer["input_scale"],
                  "output_scale": layer["output_scale"],
                  "weight_scale_per_output_channel_sha256": _sha256(json.dumps(
                      layer["weight_scale_per_output_channel"], separators=(",", ":")).encode("ascii"))},
        "fixture": oracle["fixture"],
        "fixed_points_yx": [list(point) for point in POINTS],
        "parameter_map": "T01 int32 bias[oc] 与 T23 正/负 M/Q[oc]，由仿真向量逐项驱动 wrapper 可见输入",
    }


def _write_vectors(path: Path, vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> None:
    with path.open("x", encoding="ascii", newline="\n") as output:
        for row in vectors:
            output.write(" ".join(str(value) for value in row) + "\n")


def _synth_tcl(run_dir: Path, source_paths: list[Path]) -> str:
    def braced(path: Path) -> str:
        value = str(path)
        _require("{" not in value and "}" not in value and "\n" not in value,
                 "Vivado Tcl 路径含无法安全引用字符")
        return "{" + value + "}"

    sources = "\n".join(f"read_verilog -sv {braced(path)}" for path in source_paths[:5])
    utilization = run_dir / "utilization.rpt"
    return "\n".join((sources,
                       "synth_design -top s2a_conv_layer35_channel_probe -part xc7z020clg400-1 -flatten_hierarchy none",
                       f"report_utilization -file {braced(utilization)}", "exit", ""))


def _run_full(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    _ensure_evidence_path()
    if args.reuse_static:
        temp_root = Path(tempfile.gettempdir()).resolve()
        _require(run_dir.is_absolute() and run_dir.is_dir() and
                 Path(os.path.commonpath((str(temp_root), str(run_dir.resolve())))) == temp_root,
                 "复用静态编译时运行目录必须是系统 TEMP 下的既有目录")
    else:
        _new_run_dir(run_dir)
        run_dir.mkdir()

    inputs, oracle = _prepare(progress=True)
    phases = (_reuse_static_preflight(run_dir, args, inputs, oracle)
              if args.reuse_static else [])
    static_preflight = None
    if args.reuse_static:
        static_record_path = run_dir / "static_preflight.json"
        static_record, static_record_sha = _json(static_record_path)
        static_preflight = {"path": str(static_record_path), "sha256": static_record_sha,
                            "status": static_record["status"]}

    evidence: dict[str, Any] = {
        "schema": "GestureForge-S2A-T37-layer35-row1-all-channels-v1",
        "task_id": "S2A-T37",
        "status": "RUNNING",
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=1, x=0..25; not full layer or network",
        "bindings": _evidence_bindings(inputs, oracle),
        "fixture": oracle["fixture"],
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "simulation": {"status": "NOT_RUN", "phases": phases,
                       "static_preflight": static_preflight},
        "synthesis": {**inputs["synthesis_reuse"],
                       "status": "REUSED_EXACT_RTL_SYNTHESIS_FROM_T35"},
        "paths": {"run_dir": str(run_dir), "evidence_path": str(EVIDENCE_PATH)},
    }
    try:
        if args.reuse_static:
            evidence["fixture"].update({
                "feature_path": str(run_dir / "feature_input.bin"),
                "weights_path": str(run_dir / "layer35_weights.bin"),
                "vectors_path": str(run_dir / "vectors.txt"),
                "golden_path": str(run_dir / "golden.bin"),
            })
        else:
            evidence["fixture"] = _write_run_inputs(run_dir, inputs, oracle)
        tool_bin = Path(args.xilinx_bin)
        _require(tool_bin.is_absolute() and tool_bin.is_dir(), f"Vivado bin 目录无效：{tool_bin}")
        source_paths = [ROOT / relative for relative in SOURCE_PATHS]
        if not args.reuse_static:
            phases.append(_run_tool("xvlog", ["-sv", *map(str, source_paths)], run_dir,
                                    tool_bin, 600))
            phases.append(_run_tool("xelab", ["-top", "tb_s2a_conv_layer35_row1_all_channels",
                                               "-snapshot", "s2a_t37_snapshot"], run_dir,
                                    tool_bin, 600))
        phases.append(_run_tool("xsim", ["-R", "s2a_t37_snapshot"], run_dir,
                                tool_bin, args.overall_timeout, args.no_progress_seconds,
                                re.compile(r"PROGRESS T37 outputs=")))
        xsim_output = (run_dir / "xsim.stdout.log").read_text(encoding="utf-8", errors="replace")
        summary = _parse_summary(xsim_output)
        _validate_summary(summary, oracle["expected_counts"])
        raw_observed = (run_dir / "observed_raw.bin").read_bytes()
        quantized_observed = (run_dir / "observed_output.bin").read_bytes()
        _require(raw_observed == oracle["raw_bytes"], "RTL raw INT32 输出逐值与 Python oracle 不同")
        _require(quantized_observed == oracle["quantized_bytes"],
                 "RTL INT8 输出逐值与 Python/D2 oracle 不同")
        evidence["simulation"] = {
            "status": "PASS",
            "phases": phases,
            "static_preflight": static_preflight,
            "xsim_summary": summary,
            "raw_int32_compares": len(oracle["raw_values"]),
            "quantized_int8_compares": len(oracle["quantized_values"]),
            "observed_raw_int32_le_sha256": _sha256(raw_observed),
            "observed_quantized_int8_sha256": _sha256(quantized_observed),
            "memory_stall": {"source": "T01 manifest protocol_vectors.memory_stall_cycles",
                             "sequence": list(STALL_SEQUENCE),
                             "classes": {name: {"transfers": summary[f"{name}_transfers"],
                                                "slot_counts": [summary[f"{name}_slot{i}"] for i in range(5)],
                                                "stall_cycles": summary[f"{name}_stall_cycles"]}
                                         for name in ("feature", "weight", "output")},
                             "expected_counts_match": True},
            "address_checks": "PASS; feature NCHW, channel-major oc*3456 weights, output NCHW, aligned word/lane/strobe and stable pending request fields",
            "smoke": {"memory_error_codes": {"feature": "PASS", "weight": "PASS", "output": "PASS"},
                      "abort_pending_read": "PASS", "reset_pending_read": "PASS",
                      "abort_pending_output_write_no_side_effect": "PASS",
                      "post_smoke_full_probe_recovery": "PASS"},
            "progress_checkpoints": "PROGRESS T37 one checkpoint per completed output channel: 26/6656 ... 6656/6656",
        }
        evidence["simulation"]["artifacts"] = {
            path.name: _artifact_record(path) for path in sorted(run_dir.iterdir()) if path.is_file()
        }
        evidence["status"] = "PASS"
        evidence["completed_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
        EVIDENCE_PATH.parent.mkdir(exist_ok=True)
        with EVIDENCE_PATH.open("xb") as output:
            output.write((json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(json.dumps({"result": "PASS", "evidence_path": str(EVIDENCE_PATH),
                          "run_dir": str(run_dir),
                          "tool_exit_codes": {record["phase"]: record["exit_code"] for record in phases},
                          "raw_compares": len(oracle["raw_values"]),
                          "int8_compares": len(oracle["quantized_values"]),
                          "stall_counts": evidence["simulation"]["memory_stall"]["classes"],
                          "resources": inputs["synthesis_reuse"]["resources"]},
                         ensure_ascii=False, indent=2), flush=True)
        return 0
    except Exception as exc:
        evidence["status"] = "FAIL"
        evidence["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        evidence["simulation"]["status"] = "FAIL"
        evidence["simulation"]["phases"] = phases
        evidence["completed_utc8"] = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
        print(f"FAIL T37 {type(exc).__name__}: {exc}", flush=True)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="tiny416 layer35 y=1 全行、全部输出通道 RTL 仿真")
    parser.add_argument("--preflight-only", action="store_true", help="仅核冻结绑定并运行 CPU oracle")
    parser.add_argument("--static-only", action="store_true", help="在 TEMP 执行 xvlog/xelab，不启动 xsim")
    parser.add_argument("--reuse-static", action="store_true", help="复用已核验的静态预检目录并只执行一次 xsim")
    parser.add_argument("--run-dir", help="系统 TEMP 下的新运行目录；复用时为静态预检目录")
    parser.add_argument("--xilinx-bin", default=str(XILINX_BIN_DEFAULT), help="Vivado bin 目录")
    parser.add_argument("--overall-timeout", type=float, default=7200.0)
    parser.add_argument("--no-progress-seconds", type=float, default=300.0)
    args = parser.parse_args(argv)
    try:
        _require(sum((args.preflight_only, args.static_only, args.reuse_static)) <= 1,
                 "preflight/static/reuse 选项不能同时使用")
        if args.preflight_only:
            inputs, oracle = _prepare(progress=True)
            print(json.dumps({"result": "PASS", "baseline": inputs["bindings"]["T37_baseline"],
                              "bindings": inputs["bindings"], "fixture": oracle["fixture"],
                              "oracle": oracle["oracle"], "expected_counts": oracle["expected_counts"]},
                             ensure_ascii=False, indent=2), flush=True)
            return 0
        _require(args.run_dir is not None, "full/static 模式必须提供 --run-dir")
        _require(args.overall_timeout > 0 and args.no_progress_seconds > 0,
                 "timeout 与 no-progress 时间必须大于0")
        if args.static_only:
            return _run_static(args)
        return _run_full(args)
    except Exception as exc:
        print(f"FAIL T37 {type(exc).__name__}: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
