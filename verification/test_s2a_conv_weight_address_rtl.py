"""验证 G0 tiny416 GFINT8W1 卷积权重字节地址查询 RTL。"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_D2_REFERENCE_SHA256 = "c7e6c5282c7b9c24bc6cc82b9d84f7578d6d6d45670cd23a6425cc52382dc196"
_WEIGHT_PACKAGE_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
_RANDOM_SEED = 20260922
_EXPECTED_COUNTS = {
    "random_queries": 21000,
    "directed_cases": 336,
    "directed_weight_tap_queries": 331696,
    "layer_edge_queries": 84,
    "uint32_boundary_success": 1,
    "BAD_ARGUMENT": 6,
    "BAD_RANGE": 3,
}
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_FIELD_COUNT = 23


class XorShift32:
    """维护 T09 独立 weight-query 伪随机流。"""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        value = self.state
        value ^= (value << 13) & 0xFFFFFFFF
        value &= 0xFFFFFFFF
        value ^= value >> 17
        value &= 0xFFFFFFFF
        value ^= (value << 5) & 0xFFFFFFFF
        self.state = value & 0xFFFFFFFF
        return self.state

    def selector(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("T09 选择器上界必须为正数")
        return self.next_u32() % bound


def _sha256_bytes(data: bytes) -> str:
    """计算不可变原始字节的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _manifest_descriptors(manifest: dict, d2_evidence: dict) -> tuple[list[dict], dict]:
    """绑定 21 个卷积的 GF8 payload 描述符和 directed 黄金值。"""
    address_map = manifest["address_map"]["weight_package"]
    package_base = int(address_map["address"])
    package_length = int(address_map["length_bytes"])
    if (address_map.get("format") != "GFINT8W1" or
            address_map.get("sha256") != _WEIGHT_PACKAGE_SHA256 or
            package_length != int(d2_evidence["package"]["bytes"]) or
            address_map.get("sha256") != d2_evidence["package"]["sha256"] or
            d2_evidence["package"].get("format") != "GFINT8W1" or
            d2_evidence["package"].get("version") != 1):
        raise ValueError("G0/D2 GFINT8W1 package binding 不一致")
    if package_base != 0x00100000 or package_length != 5903100:
        raise ValueError("G0 weight package base/length 不符合冻结 tiny416")

    d2_layers = {int(layer["layer_index"]): layer for layer in d2_evidence["layers"]}
    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer.get("op") == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    if len(conv_layers) != 21:
        raise ValueError("G0 tiny416 convolution layer 数量变化")
    descriptors = []
    for layer in conv_layers:
        layer_index = int(layer["layer_index"])
        weight_layer_index = int(layer["weight_layer_index"])
        groups = int(layer["groups"])
        input_shape = layer["input_shape_nchw"]
        output_shape = layer["output_shape_nchw"]
        if (groups != 1 or weight_layer_index != layer_index or
                layer["layout"] != "NCHW" or layer["element_type"] != "int8_twos_complement" or
                input_shape[0] != 1 or output_shape[0] != 1):
            raise ValueError(f"G0 layer {layer_index} groups/layout/weight index 不支持 T09")
        input_channels = int(input_shape[1])
        output_channels = int(output_shape[1])
        kernel_height, kernel_width = map(int, layer["kernel_hw"])
        reduction_count = input_channels * kernel_height * kernel_width
        weight_bytes = output_channels * reduction_count
        offsets = layer["gf8_parameter_offsets"]
        weight_offset = int(offsets["quantized_weight_offset"])
        manifest_weight_bytes = int(offsets["quantized_weight_bytes"])
        d2_layer = d2_layers.get(layer_index)
        if (d2_layer is None or int(d2_layer["filters"]) != output_channels or
                int(d2_layer["input_channels"]) != input_channels or
                int(d2_layer["groups"]) != groups or int(d2_layer["size"]) != kernel_height or
                int(d2_layer["weight_count"]) != weight_bytes or
                kernel_height != kernel_width or manifest_weight_bytes != weight_bytes):
            raise ValueError(f"G0/D2 layer {layer_index} weight geometry/byte count mismatch")
        if weight_offset < 0 or weight_offset + weight_bytes > package_length:
            raise ValueError(f"G0 layer {layer_index} quantized weight payload exceeds GF8 package")
        descriptors.append({
            "layer_index": layer_index,
            "weight_layer_index": weight_layer_index,
            "groups": groups,
            "output_channels": output_channels,
            "input_channels": input_channels,
            "kernel_height": kernel_height,
            "kernel_width": kernel_width,
            "reduction_count": reduction_count,
            "quantized_weight_offset": weight_offset,
            "quantized_weight_bytes": manifest_weight_bytes,
            "package_base_address": package_base,
            "package_length_bytes": package_length,
        })

    ranges = sorted((d["quantized_weight_offset"],
                     d["quantized_weight_offset"] + d["quantized_weight_bytes"],
                     d["layer_index"]) for d in descriptors)
    if any(left[1] > right[0] for left, right in zip(ranges, ranges[1:])):
        raise ValueError("G0 卷积 GF8 quantized payload 区域重叠")
    if sum(d["quantized_weight_bytes"] for d in descriptors) != int(d2_evidence["model"]["weight_count"]):
        raise ValueError("G0/D2 全模型量化权重 byte count 不一致")
    return descriptors, address_map


def _expected(descriptor: dict, query: dict, byte_known: int = 0,
              weight_value: int = 0, error: int = 0) -> tuple[int, int, int, int, int, int, int]:
    """由输出 filter 连续 K 字节规则计算独立 golden tuple。"""
    reduction_index = ((query["input_channel"] * descriptor["kernel_height"] +
                        query["kernel_y"]) * descriptor["kernel_width"] +
                       query["kernel_x"])
    layer_offset = query["output_channel"] * descriptor["reduction_count"] + reduction_index
    package_offset = descriptor["quantized_weight_offset"] + layer_offset
    address = descriptor["package_base_address"] + package_offset
    return (reduction_index, layer_offset, package_offset, address,
            byte_known, weight_value & 0xFF, error)


def _record(vector_class: int, descriptor: dict, query: dict,
            expected: tuple[int, int, int, int, int, int, int] | None = None) -> list[int]:
    """构建 testbench 输入及其期望偏移、地址和可选 directed 字节。"""
    if expected is None:
        expected = _expected(descriptor, query)
    fields = [
        vector_class,
        descriptor["layer_index"],
        descriptor["weight_layer_index"],
        descriptor["groups"],
        descriptor["output_channels"],
        descriptor["input_channels"],
        descriptor["kernel_height"],
        descriptor["kernel_width"],
        descriptor["quantized_weight_offset"],
        descriptor["quantized_weight_bytes"],
        descriptor["package_base_address"],
        descriptor["package_length_bytes"],
        query["output_channel"],
        query["input_channel"],
        query["kernel_y"],
        query["kernel_x"],
        *expected,
    ]
    if len(fields) != _FIELD_COUNT or any(not 0 <= value <= 0xFFFFFFFF for value in fields):
        raise ValueError("T09 vector field count/uint32 range invalid")
    return fields


def _emit(stream, fields: list[int], vector_digest, stimulus_digest,
          golden_digest, directed_weight_digest, descriptor: dict,
          case_index: int | None = None) -> None:
    """写出稳定向量并绑定输入、输出及 directed INT8 黄金字节。"""
    stream.write(" ".join(f"{value:08X}" for value in fields) + "\n")
    vector_digest.update(struct.pack("<23I", *fields))
    stimulus_digest.update(struct.pack("<16I", *fields[:16]))
    golden_digest.update(struct.pack("<7I", *fields[16:]))
    if fields[20]:
        signed_value = fields[21] if fields[21] < 128 else fields[21] - 256
        directed_weight_digest.update(struct.pack(
            "<IIIb", descriptor["layer_index"], fields[12],
            fields[17], signed_value,
        ))


def _materialize_vectors(manifest: dict, d2_evidence: dict,
                         destination: Path) -> dict:
    """生成独立随机、全部 directed tap、边界和错误向量。"""
    descriptors, package = _manifest_descriptors(manifest, d2_evidence)
    plan = manifest["operator_test_plan"]
    if (plan.get("random_cases_per_model_layer") != 1000 or
            plan.get("directed_cases_per_model_layer") != 16 or
            "1000 cases per cfg convolution layer" not in plan.get("convolutional", "") or
            "input_channel then kernel_y then kernel_x" not in plan.get("tensor_order", "")):
        raise ValueError("G0 convolution sample count or reduction order changed")
    directed_by_layer = plan["directed_case_vectors"]["convolutional"]
    rng = XorShift32(_RANDOM_SEED)
    vector_digest = hashlib.sha256()
    stimulus_digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    directed_weight_digest = hashlib.sha256()
    counts = {key: 0 for key in _EXPECTED_COUNTS}
    per_layer = []
    directed_case_hashes = []

    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        for descriptor in descriptors:
            layer_index = descriptor["layer_index"]
            state_before = rng.state
            for _ in range(1000):
                query = {
                    "output_channel": rng.selector(descriptor["output_channels"]),
                    "input_channel": rng.selector(descriptor["input_channels"]),
                    "kernel_y": rng.selector(descriptor["kernel_height"]),
                    "kernel_x": rng.selector(descriptor["kernel_width"]),
                }
                _emit(stream, _record(0, descriptor, query), vector_digest,
                      stimulus_digest, golden_digest, directed_weight_digest, descriptor)
                counts["random_queries"] += 1
            state_after_random = rng.state

            cases = directed_by_layer.get(str(layer_index))
            if not isinstance(cases, list) or len(cases) != 16:
                raise ValueError(f"G0 layer {layer_index} directed case count changed")
            layer_directed_taps = 0
            for expected_case_index, case in enumerate(cases):
                if case.get("case_index") != expected_case_index:
                    raise ValueError("G0 directed case_index order changed")
                if (case.get("reduction_order") !=
                        "local_input_channel, kernel_y, kernel_x; flattened index=((channel*kernel_h)+kernel_y)*kernel_w+kernel_x" or
                        case.get("input_channel_base") != 0 or
                        case.get("input_channel_count_per_group") != descriptor["input_channels"]):
                    raise ValueError(f"G0 layer {layer_index} directed group/order changed")
                target = case["target_output_nchw"]
                if len(target) != 4 or target[0] != 0:
                    raise ValueError("G0 directed target must be batch 0 NCHW")
                output_channel = int(target[1])
                weights = case["weight_reduction_int8"]
                if (not 0 <= output_channel < descriptor["output_channels"] or
                        len(weights) != descriptor["reduction_count"] or
                        any(not -127 <= int(value) <= 127 for value in weights)):
                    raise ValueError(f"G0 layer {layer_index} directed weight tuple invalid")
                case_digest = hashlib.sha256()
                for reduction_index, value in enumerate(weights):
                    channels_per_kernel = descriptor["kernel_height"] * descriptor["kernel_width"]
                    input_channel = reduction_index // channels_per_kernel
                    kernel_y = (reduction_index // descriptor["kernel_width"]) % descriptor["kernel_height"]
                    kernel_x = reduction_index % descriptor["kernel_width"]
                    query = {
                        "output_channel": output_channel,
                        "input_channel": input_channel,
                        "kernel_y": kernel_y,
                        "kernel_x": kernel_x,
                    }
                    expected = _expected(
                        descriptor, query, 1, int(value), 0,
                    )
                    fields = _record(1, descriptor, query, expected)
                    _emit(stream, fields, vector_digest, stimulus_digest,
                          golden_digest, directed_weight_digest, descriptor,
                          case_index=expected_case_index)
                    case_digest.update(struct.pack(
                        "<IIIb", output_channel, reduction_index, fields[18], int(value),
                    ))
                    layer_directed_taps += 1
                    counts["directed_weight_tap_queries"] += 1
                directed_case_hashes.append({
                    "layer_index": layer_index,
                    "case_index": expected_case_index,
                    "output_channel": output_channel,
                    "tap_count": len(weights),
                    "golden_sha256": case_digest.hexdigest(),
                })
                counts["directed_cases"] += 1

            if rng.state != state_after_random:
                raise ValueError("G0 directed cases must not consume T09 random state")

            edge_queries = (
                (0, 0, 0, 0),
                (0, descriptor["input_channels"] - 1,
                 descriptor["kernel_height"] - 1, descriptor["kernel_width"] - 1),
                (descriptor["output_channels"] - 1, 0, 0, 0),
                (descriptor["output_channels"] - 1,
                 descriptor["input_channels"] - 1,
                 descriptor["kernel_height"] - 1, descriptor["kernel_width"] - 1),
            )
            for output_channel, input_channel, kernel_y, kernel_x in edge_queries:
                query = {"output_channel": output_channel,
                         "input_channel": input_channel,
                         "kernel_y": kernel_y, "kernel_x": kernel_x}
                _emit(stream, _record(2, descriptor, query), vector_digest,
                      stimulus_digest, golden_digest, directed_weight_digest, descriptor)
                counts["layer_edge_queries"] += 1

            per_layer.append({
                "layer_index": layer_index,
                "output_channels": descriptor["output_channels"],
                "input_channels": descriptor["input_channels"],
                "groups": descriptor["groups"],
                "kernel_hw": [descriptor["kernel_height"], descriptor["kernel_width"]],
                "reduction_count_k": descriptor["reduction_count"],
                "quantized_weight_offset": descriptor["quantized_weight_offset"],
                "quantized_weight_bytes": descriptor["quantized_weight_bytes"],
                "random_queries": 1000,
                "directed_cases": len(cases),
                "directed_weight_tap_queries": layer_directed_taps,
                "edge_queries": len(edge_queries),
                "random_state_before": f"0x{state_before:08X}",
                "random_state_after": f"0x{state_after_random:08X}",
            })

        first = descriptors[0]
        invalid_query = {"output_channel": 0, "input_channel": 0,
                         "kernel_y": 0, "kernel_x": 0}
        argument_cases = []
        for key, bad_value in (
                ("output_channels", first["output_channels"]),
                ("input_channels", first["input_channels"]),
                ("kernel_height", first["kernel_height"]),
                ("kernel_width", first["kernel_width"])):
            query = dict(invalid_query)
            query_key = {"output_channels": "output_channel",
                         "input_channels": "input_channel",
                         "kernel_height": "kernel_y",
                         "kernel_width": "kernel_x"}[key]
            query[query_key] = bad_value
            argument_cases.append((first, query))
        wrong_groups = dict(first)
        wrong_groups["groups"] = 2
        argument_cases.append((wrong_groups, invalid_query))
        wrong_weight_layer = dict(first)
        wrong_weight_layer["weight_layer_index"] += 1
        argument_cases.append((wrong_weight_layer, invalid_query))
        for descriptor, query in argument_cases:
            expected = (0, 0, 0, 0, 0, 0, 1)
            _emit(stream, _record(4, descriptor, query, expected), vector_digest,
                  stimulus_digest, golden_digest, directed_weight_digest, descriptor)
            counts["BAD_ARGUMENT"] += 1

        bad_offset = dict(first)
        bad_offset["quantized_weight_offset"] = bad_offset["package_length_bytes"] - 1
        for descriptor in (bad_offset,):
            _emit(stream, _record(5, descriptor, invalid_query,
                  (0, 0, 0, 0, 0, 0, 2)), vector_digest, stimulus_digest,
                  golden_digest, directed_weight_digest, descriptor)
            counts["BAD_RANGE"] += 1
        bad_size = dict(first)
        bad_size["quantized_weight_bytes"] -= 1
        _emit(stream, _record(5, bad_size, invalid_query,
              (0, 0, 0, 0, 0, 0, 2)), vector_digest, stimulus_digest,
              golden_digest, directed_weight_digest, bad_size)
        counts["BAD_RANGE"] += 1
        bad_base = dict(first)
        bad_base["package_base_address"] = 0xFFFFFFFF
        _emit(stream, _record(5, bad_base, invalid_query,
              (0, 0, 0, 0, 0, 0, 2)), vector_digest, stimulus_digest,
              golden_digest, directed_weight_digest, bad_base)
        counts["BAD_RANGE"] += 1

        last = descriptors[-1]
        boundary = dict(last)
        boundary["package_base_address"] = 0x100000000 - boundary["package_length_bytes"]
        last_query = {
            "output_channel": boundary["output_channels"] - 1,
            "input_channel": boundary["input_channels"] - 1,
            "kernel_y": boundary["kernel_height"] - 1,
            "kernel_x": boundary["kernel_width"] - 1,
        }
        _emit(stream, _record(3, boundary, last_query), vector_digest,
              stimulus_digest, golden_digest, directed_weight_digest, boundary)
        counts["uint32_boundary_success"] += 1

    if counts != _EXPECTED_COUNTS:
        raise ValueError(f"T09 vector count mismatch: {counts}")
    if sum(item["reduction_count_k"] for item in per_layer) != 20731:
        raise ValueError("T09 convolution K aggregate changed")
    return {
        "counts": counts,
        "total_records": (
            counts["random_queries"] + counts["directed_weight_tap_queries"] +
            counts["layer_edge_queries"] + counts["uint32_boundary_success"] +
            counts["BAD_ARGUMENT"] + counts["BAD_RANGE"]
        ),
        "vector_file_bytes": destination.stat().st_size,
        "vector_sha256": _sha256_file(destination),
        "stimulus_vector_sha256": stimulus_digest.hexdigest(),
        "golden_output_sha256": golden_digest.hexdigest(),
        "directed_weight_bytes_sha256": directed_weight_digest.hexdigest(),
        "randomness": {
            "seed": _RANDOM_SEED,
            "scope": "T09 独立 weight-byte query 流，不推进或改写 G0 全局 operator PRNG",
            "draw_order": "按 conv layer_index 升序；每个 random tuple 依次选择 output_channel、input_channel、kernel_y、kernel_x；directed/edge queries 不消耗该流",
            "state_after_random_queries": f"0x{rng.state:08X}",
            "per_layer": per_layer,
        },
        "directed_case_goldens": directed_case_hashes,
        "per_layer": per_layer,
        "weight_offset_formula": "package_offset + (((output_channel * input_channels + input_channel) * kernel_height + kernel_y) * kernel_width + kernel_x)",
        "address_formula": "weight_package_base_address + package_byte_offset",
        "golden_byte_source": "G0 manifest directed_case_vectors.convolutional[*].weight_reduction_int8; 不读取外部 GFINT8W1 大文件",
    }


def _assert_temporary_cwd(cwd: Path, repository: Path) -> None:
    """禁止 Vivado 在仓库或系统临时目录之外创建构建文件。"""
    temp_root = Path(tempfile.gettempdir()).resolve()
    resolved = cwd.resolve()
    if (not resolved.is_dir() or resolved == repository or
            os.path.commonpath([str(temp_root), str(resolved)]) != str(temp_root) or
            repository in resolved.parents):
        raise RuntimeError(f"拒绝在非系统临时目录运行 Vivado：{resolved}")


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float, repository: Path) -> tuple[int, str]:
    """在已核实的系统临时 cwd 运行单个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    _assert_temporary_cwd(cwd, repository)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("S2A-T09 Vivado 总运行时间超过 600 秒停止条件")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    process = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=cwd, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=remaining,
    )
    output = process.stdout + process.stderr
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return process.returncode, output


class TestS2AConvWeightAddressRtl(unittest.TestCase):
    """验证 tiny416 GFINT8W1 的 INT8 卷积权重字节映射。"""

    def test_vivado_weight_address_against_g0(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        g0_doc_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
        d2_doc_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md"
        d2_source_path = repository / "verification/s1_t02_d2_int8_weight_reference.py"
        delivery_source_path = repository / "verification/s2a_model_delivery.py"
        d2_evidence_path = repository / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
        rtl_path = repository / "src/int8_conv_weight_address.sv"
        bench_path = repository / "sim/tb_s2a_conv_weight_address.sv"
        script_path = Path(__file__).resolve()
        required = (manifest_path, g0_doc_path, d2_doc_path, d2_source_path,
                    delivery_source_path, d2_evidence_path, rtl_path,
                    bench_path, script_path)
        for path in required:
            self.assertTrue(path.is_file(), f"缺少绑定输入或测试源文件：{path}")

        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(manifest_sha, _MANIFEST_SHA256,
                         "G0 manifest 原始 SHA 变化，按任务停止条件中止")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        d2_evidence_bytes = d2_evidence_path.read_bytes()
        d2_evidence_sha = _sha256_bytes(d2_evidence_bytes)
        d2_evidence = json.loads(d2_evidence_bytes.decode("utf-8"))
        self.assertEqual(d2_evidence.get("status"),
                         "INT8_WEIGHT_REFERENCE_GENERATED_ACTIVATION_SCALE_PENDING")
        self.assertEqual(d2_evidence.get("code", {}).get("sha256"), _D2_REFERENCE_SHA256)
        self.assertEqual(_sha256_file(d2_source_path), _D2_REFERENCE_SHA256)
        self.assertEqual(d2_evidence.get("package", {}).get("sha256"), _WEIGHT_PACKAGE_SHA256)
        self.assertEqual(manifest.get("address_map", {}).get("weight_package", {}).get("sha256"),
                         _WEIGHT_PACKAGE_SHA256)

        tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"未找到 Vivado 工具：{tool}")
        source_hashes_before = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
            "delivery_source_sha256": _sha256_file(delivery_source_path),
        }
        phase_codes = []
        with tempfile.TemporaryDirectory(prefix="s2a_t09_conv_weight_") as temporary:
            work = Path(temporary).resolve()
            _assert_temporary_cwd(work, repository)
            vector_path = work / "vectors.dat"
            vector_result = _materialize_vectors(manifest, d2_evidence, vector_path)
            self.assertEqual(vector_result["counts"], _EXPECTED_COUNTS)

            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_conv_weight_address",
                           "-snapshot", "s2a_conv_weight_address_snapshot"]),
                ("xsim", ["-R", "s2a_conv_weight_address_snapshot"]),
            ]
            deadline = time.monotonic() + 600.0
            for name, arguments in phases:
                code, output = _run_tool(
                    tools[name], arguments, work, work / f"{name}.log",
                    deadline, repository,
                )
                phase_codes.append({"phase": name, "exit_code": code})
                self.assertEqual(code, 0,
                                 f"{name} 退出码 {code}；临时日志尾部：\n{output[-5000:]}")
                if name == "xsim":
                    self.assertIn(
                        "PASS: total=352790 random=21000 directed=331696 directed_values=331696 layer_edges=84 uint32_boundary=1 bad_argument=6 bad_range=3",
                        output,
                    )

        self.assertEqual([phase["exit_code"] for phase in phase_codes], [0, 0, 0])
        source_hashes_after = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
            "delivery_source_sha256": _sha256_file(delivery_source_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真期间 T09 source files changed")
        self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                         "仿真期间 G0 manifest 原始 SHA 变化")
        self.assertEqual(_sha256_file(d2_source_path), _D2_REFERENCE_SHA256)
        self.assertEqual(_sha256_file(d2_evidence_path), d2_evidence_sha)
        self.assertEqual(source_hashes_before["delivery_source_sha256"],
                         source_hashes_after["delivery_source_sha256"],
                         "仿真期间 D2 delivery source changed")

        evidence = {
            "schema_version": "gestureforge_s2a_t09_conv_weight_address_simulation_v1",
            "result": "PASS",
            "scope": "tiny416 GFINT8W1 单个卷积 INT8 权重 byte offset/address 查询",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": manifest_sha,
                "g0_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
                "g0_spec_sha256": _sha256_file(g0_doc_path),
                "d2_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
                "d2_spec_sha256": _sha256_file(d2_doc_path),
                "d2_reference_source_sha256": _sha256_file(d2_source_path),
                "d2_delivery_source_sha256": _sha256_file(delivery_source_path),
                "d2_weight_evidence_sha256": d2_evidence_sha,
                "gf8_package_sha256_from_manifest": _WEIGHT_PACKAGE_SHA256,
                **source_hashes_after,
                "vector_file_sha256": vector_result["vector_sha256"],
                "stimulus_vector_sha256": vector_result["stimulus_vector_sha256"],
                "golden_output_sha256": vector_result["golden_output_sha256"],
                "directed_weight_bytes_sha256": vector_result["directed_weight_bytes_sha256"],
            },
            "weight_layout": {
                "package_format": "GFINT8W1 v1",
                "package_base_address": manifest["address_map"]["weight_package"]["address"],
                "package_length_bytes": manifest["address_map"]["weight_package"]["length_bytes"],
                "weights_per_filter": "Cin*Kh*Kw contiguous bytes; output-channel-major",
                "weight_offset_formula": vector_result["weight_offset_formula"],
                "address_formula": vector_result["address_formula"],
                "groups_supported": [1],
                "external_package_read": False,
            },
            "randomness": vector_result["randomness"],
            "counts": vector_result["counts"],
            "total_records": vector_result["total_records"],
            "vector_file_bytes": vector_result["vector_file_bytes"],
            "per_layer": vector_result["per_layer"],
            "directed_case_goldens": vector_result["directed_case_goldens"],
            "invalid_assertions": {
                "BAD_ARGUMENT_code_1": vector_result["counts"]["BAD_ARGUMENT"],
                "BAD_RANGE_code_2": vector_result["counts"]["BAD_RANGE"],
                "uint32_maximum_byte_success": vector_result["counts"]["uint32_boundary_success"],
            },
            "vivado": {
                "bin": str(_XILINX_BIN),
                "phases": phase_codes,
                "command_template": "python -B -m unittest verification.test_s2a_conv_weight_address_rtl -v",
            },
            "limitations": [
                "仅计算单个量化权重的 byte offset/address，不读取权重、不包含 bias/scale/乘加或 memory transaction。",
                "directed 字节黄金来自 G0 manifest；随机查询验证索引和地址公式，不冒充实际包字节读取。",
                "不代表完整卷积、整网逐层比较、Vivado 综合、资源估算或时序通过。",
                "地址为 G0 逻辑仿真 byte address，不代表 Zynq DDR 实际映射。",
            ],
        }
        evidence_path = repository / "report/evidence/S2A-T09/conv_weight_address_simulation.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_bytes(
            (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        print(
            "S2A-T09 manifest_sha256={} vector_sha256={} stimulus_sha256={} golden_sha256={} "
            "directed_bytes_sha256={} counts={} random_state_final={} vivado={}".format(
                manifest_sha,
                vector_result["vector_sha256"],
                vector_result["stimulus_vector_sha256"],
                vector_result["golden_output_sha256"],
                vector_result["directed_weight_bytes_sha256"],
                vector_result["counts"],
                vector_result["randomness"]["state_after_random_queries"],
                [phase["exit_code"] for phase in phase_codes],
            )
        )


if __name__ == "__main__":
    unittest.main()
