"""按 G0 冻结描述与 D2 卷积规则验证单 tap 几何和逻辑地址。"""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_RANDOM_SEED = 20260922
_EXPECTED_RANDOM_FINAL_STATE = 0x2DC4F9F4
_UINT32_LIMIT = 1 << 32
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")


class XorShift32:
    """维护 G0 指定的共享 xorshift32 状态。"""

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
            raise ValueError("G0 selector 上界必须为正")
        return self.next_u32() % bound

    def int8(self) -> int:
        return (self.next_u32() & 0xFF) % 255 - 127


def _sha256_bytes(data: bytes) -> str:
    """计算字节序列的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _layers_by_index(manifest: dict) -> dict[int, dict]:
    """建立 G0 layer_index 到冻结描述符的只读映射。"""
    layers = manifest["layers"]
    result = {int(layer["layer_index"]): layer for layer in layers}
    if len(result) != len(layers):
        raise ValueError("G0 layer_index 重复")
    return result


def _descriptor_for_conv(layer: dict, manifest: dict,
                         by_index: dict[int, dict]) -> dict:
    """从卷积层及其输入生产者提取完整单 batch 描述符。"""
    if layer["op"] != "convolutional":
        raise ValueError("仅允许冻结 convolutional layer")
    if layer["layout"] != "NCHW" or layer["element_type"] != "int8_twos_complement":
        raise ValueError("G0 卷积输入必须为 NCHW INT8")
    if layer["groups"] != 1:
        raise ValueError(f"卷积 groups 超出本任务范围：layer {layer['layer_index']}")
    input_shape = list(layer["input_shape_nchw"])
    output_shape = list(layer["output_shape_nchw"])
    if len(input_shape) != 4 or len(output_shape) != 4 or input_shape[0] != 1 or output_shape[0] != 1:
        raise ValueError("本任务只实现 G0 单 batch 卷积几何")
    references = layer["input_tensor_indices"]
    if len(references) != 1:
        raise ValueError("G0 卷积必须引用一个输入张量")
    reference = references[0]
    if reference == "network_input":
        source = manifest["address_map"]["input"]
        if list(source["shape_nchw"]) != input_shape:
            raise ValueError("network_input shape 与冻结卷积输入 shape 不一致")
        input_base = int(source["address"])
        input_length = int(source["length_bytes"])
    else:
        producer_index = int(reference)
        if producer_index not in by_index:
            raise ValueError(f"G0 输入 producer 不存在：{reference}")
        producer = by_index[producer_index]
        if list(producer["output_shape_nchw"]) != input_shape:
            raise ValueError(f"layer {layer['layer_index']} 输入 shape 与 producer 输出不一致")
        input_base = int(producer["tensor_address"])
        input_length = int(producer["tensor_length_bytes"])

    _, input_channels, input_height, input_width = input_shape
    _, output_channels, output_height, output_width = output_shape
    kernel_height, kernel_width = map(int, layer["kernel_hw"])
    stride_y, stride_x = map(int, layer["stride_hw"])
    pad_left, pad_right, pad_top, pad_bottom = map(int, layer["padding_lrtb"])
    padding_value = int(layer["padding_value_int8"])
    if min(input_channels, input_height, input_width, output_channels,
           output_height, output_width, kernel_height, kernel_width,
           stride_y, stride_x) <= 0:
        raise ValueError("G0 卷积尺寸、kernel 与 stride 必须为正")
    if min(pad_left, pad_right, pad_top, pad_bottom) < 0:
        raise ValueError("G0 卷积 padding 不得为负")
    expected_height = (input_height + pad_top + pad_bottom - kernel_height) // stride_y + 1
    expected_width = (input_width + pad_left + pad_right - kernel_width) // stride_x + 1
    if (expected_height, expected_width) != (output_height, output_width):
        raise ValueError(f"layer {layer['layer_index']} 的 D2 输出几何与 G0 不符")
    if input_length != input_channels * input_height * input_width:
        raise ValueError(f"layer {layer['layer_index']} 输入对象长度不等于 NCHW INT8 元素数")
    if input_base < 0 or input_base + input_length > _UINT32_LIMIT:
        raise ValueError(f"layer {layer['layer_index']} 输入对象超出 uint32 地址空间")
    return {
        "layer_index": int(layer["layer_index"]),
        "input_base_address": input_base,
        "input_length_bytes": input_length,
        "input_batch_count": 1,
        "input_channels": input_channels,
        "input_height": input_height,
        "input_width": input_width,
        "output_batch_count": 1,
        "output_channels": output_channels,
        "output_height": output_height,
        "output_width": output_width,
        "kernel_height": kernel_height,
        "kernel_width": kernel_width,
        "stride_y": stride_y,
        "stride_x": stride_x,
        "pad_left": pad_left,
        "pad_right": pad_right,
        "pad_top": pad_top,
        "pad_bottom": pad_bottom,
        "padding_value_int8": padding_value,
        "groups": 1,
        "reduction_count": input_channels * kernel_height * kernel_width,
    }


def _oracle_tap(descriptor: dict, output_batch: int, output_channel: int,
                output_y: int, output_x: int, reduction_index: int) -> tuple[int, ...]:
    """独立按 NCHW/OIHW 公式重算一个 tap 的坐标和地址。"""
    count = descriptor["reduction_count"]
    if (output_batch != 0 or output_batch >= descriptor["output_batch_count"] or
            not 0 <= output_channel < descriptor["output_channels"] or
            not 0 <= output_y < descriptor["output_height"] or
            not 0 <= output_x < descriptor["output_width"] or
            not 0 <= reduction_index < count):
        raise ValueError("oracle 收到越界的合法向量")
    kernel_area = descriptor["kernel_height"] * descriptor["kernel_width"]
    input_channel = reduction_index // kernel_area
    kernel_y = (reduction_index // descriptor["kernel_width"]) % descriptor["kernel_height"]
    kernel_x = reduction_index % descriptor["kernel_width"]
    input_y = output_y * descriptor["stride_y"] + kernel_y - descriptor["pad_top"]
    input_x = output_x * descriptor["stride_x"] + kernel_x - descriptor["pad_left"]
    is_padding = not (
        0 <= input_channel < descriptor["input_channels"] and
        0 <= input_y < descriptor["input_height"] and
        0 <= input_x < descriptor["input_width"]
    )
    if is_padding:
        offset = 0
        address = 0
    else:
        offset = ((input_channel * descriptor["input_height"] + input_y) *
                  descriptor["input_width"] + input_x)
        address = descriptor["input_base_address"] + offset
        if (offset >= descriptor["input_length_bytes"] or
                address > 0xFFFFFFFF):
            raise ValueError("oracle 地址越过 G0 输入对象或 uint32 范围")
    return (input_channel, kernel_y, kernel_x, input_y, input_x,
            int(is_padding), offset, address)


def _tap_digest_update(digest, vector_class: int, descriptor: dict,
                       case_index: int, output_batch: int,
                       output_channel: int, output_y: int, output_x: int) -> tuple[int, int]:
    """按 tap 顺序更新逐项几何黄金摘要并统计 padding。"""
    padding_count = 0
    for reduction_index in range(descriptor["reduction_count"]):
        (input_channel, kernel_y, kernel_x, input_y, input_x,
         is_padding, offset, address) = _oracle_tap(
            descriptor, output_batch, output_channel, output_y, output_x,
            reduction_index,
        )
        digest.update(struct.pack(
            "<B12iBII",
            vector_class,
            descriptor["layer_index"], case_index, output_batch,
            output_channel, output_y, output_x, reduction_index,
            input_channel, kernel_y, kernel_x, input_y, input_x,
            is_padding, offset, address,
        ))
        padding_count += is_padding
    return descriptor["reduction_count"], padding_count


def _encode_vector(vector_class: int, descriptor: dict, case_index: int,
                   output_channel: int, output_y: int, output_x: int) -> bytes:
    """编码一个输出点及其完整、不可变几何描述符。"""
    fields = [
        vector_class, descriptor["layer_index"], case_index,
        0, output_channel, output_y, output_x,
        f'{descriptor["input_base_address"]:08x}',
        descriptor["input_length_bytes"], descriptor["input_batch_count"],
        descriptor["input_channels"], descriptor["input_height"],
        descriptor["input_width"], descriptor["output_batch_count"],
        descriptor["output_channels"], descriptor["output_height"],
        descriptor["output_width"], descriptor["kernel_height"],
        descriptor["kernel_width"], descriptor["stride_y"],
        descriptor["stride_x"], descriptor["pad_left"],
        descriptor["pad_right"], descriptor["pad_top"],
        descriptor["pad_bottom"], descriptor["padding_value_int8"],
        descriptor["groups"], descriptor["reduction_count"],
    ]
    return (" ".join(str(value) for value in fields) + "\n").encode("ascii")


def _advance_shared_before_convolution(plan: dict, rng: XorShift32) -> dict:
    """确认卷积位于 G0 ASCII 算子顺序首段并读取指定随机协议。"""
    case_order = plan["case_order"]
    if (plan["random_cases_per_model_layer"] != 1000 or
            plan["directed_cases_per_model_layer"] != 16 or
            "operator name ASCII order" not in case_order or
            "int8_mac" not in case_order or
            "cfg layer_index ascending" not in case_order or
            sorted(("convolutional", "int8_mac"))[0] != "convolutional"):
        raise ValueError("G0 case_order 或卷积随机/定向用例数量变化")
    return {"state_before_convolution": f"0x{rng.state:08X}"}


def _materialize_vectors(manifest: dict, destination: Path) -> dict:
    """生成真实层随机/定向向量及零填充 3x3 fixture。"""
    plan = manifest["operator_test_plan"]
    rng = XorShift32(_RANDOM_SEED)
    shared_state = _advance_shared_before_convolution(plan, rng)
    by_index = _layers_by_index(manifest)
    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: int(layer["layer_index"]),
    )
    if len(conv_layers) != 21:
        raise ValueError(f"G0 tiny416 卷积层数变化：{len(conv_layers)}")
    directed_by_layer = plan["directed_case_vectors"]["convolutional"]
    if sorted(map(int, directed_by_layer)) != [int(layer["layer_index"]) for layer in conv_layers]:
        raise ValueError("G0 directed convolutional layer 列表与模型层不一致")

    counts = {"random_output_points": 0, "directed_cases": 0, "fixture_output_points": 0}
    taps = {"random": 0, "directed": 0, "fixture": 0, "padding": 0, "valid": 0}
    layers_evidence: list[dict] = []
    vector_file_hash = hashlib.sha256()
    golden_hash = hashlib.sha256()
    activation_hash = hashlib.sha256()
    activation_draws = 0

    with destination.open("wb") as vector_stream:
        for layer in conv_layers:
            descriptor = _descriptor_for_conv(layer, manifest, by_index)
            before_random = rng.state
            layer_random_taps = 0
            layer_directed_taps = 0
            for case_index in range(plan["random_cases_per_model_layer"]):
                output_channel = rng.selector(descriptor["output_channels"])
                output_y = rng.selector(descriptor["output_height"])
                output_x = rng.selector(descriptor["output_width"])
                for _ in range(descriptor["reduction_count"]):
                    activation = rng.int8()
                    activation_hash.update(bytes((activation & 0xFF,)))
                    activation_draws += 1
                encoded = _encode_vector(
                    0, descriptor, case_index, output_channel, output_y, output_x,
                )
                vector_stream.write(encoded)
                vector_file_hash.update(encoded)
                vector_taps, vector_padding = _tap_digest_update(
                    golden_hash, 0, descriptor, case_index, 0,
                    output_channel, output_y, output_x,
                )
                layer_random_taps += vector_taps
                taps["random"] += vector_taps
                taps["padding"] += vector_padding
                taps["valid"] += vector_taps - vector_padding
                counts["random_output_points"] += 1

            after_random = rng.state
            directed_vectors = directed_by_layer[str(descriptor["layer_index"])]
            if len(directed_vectors) != plan["directed_cases_per_model_layer"]:
                raise ValueError(f"layer {descriptor['layer_index']} directed 数量不是 16")
            for expected_case_index, directed in enumerate(directed_vectors):
                case_index = int(directed["case_index"])
                if case_index != expected_case_index:
                    raise ValueError("G0 directed case_index 必须按规范升序且无缺项")
                target = directed["target_output_nchw"]
                if len(target) != 4 or target[0] != 0:
                    raise ValueError("G0 directed target 必须是 batch 0 的 NCHW 输出元素")
                output_batch, output_channel, output_y, output_x = map(int, target)
                if directed["reduction_order"] != "local_input_channel, kernel_y, kernel_x; flattened index=((channel*kernel_h)+kernel_y)*kernel_w+kernel_x":
                    raise ValueError("G0 directed reduction order 与冻结规则不一致")
                if (int(directed["input_channel_base"]) != 0 or
                        int(directed["input_channel_count_per_group"]) != descriptor["input_channels"]):
                    raise ValueError("G0 groups=1 directed 输入通道切片不匹配")
                if list(map(int, directed["padding_lrtb"])) != [
                    descriptor["pad_left"], descriptor["pad_right"],
                    descriptor["pad_top"], descriptor["pad_bottom"],
                ]:
                    raise ValueError("G0 directed padding 与 layer 描述符不匹配")
                if int(directed["padding_value_int8"]) != descriptor["padding_value_int8"]:
                    raise ValueError("G0 directed padding value 与 layer 描述符不匹配")
                origin = list(map(int, directed["input_patch_origin_yx"]))
                formula_origin = [
                    output_y * descriptor["stride_y"] - descriptor["pad_top"],
                    output_x * descriptor["stride_x"] - descriptor["pad_left"],
                ]
                if origin != formula_origin:
                    raise ValueError("D2 directed receptive-field origin 与冻结坐标不一致")
                expected_values = directed["source_reduction_values_int8"]
                if len(expected_values) != descriptor["reduction_count"]:
                    raise ValueError("G0 directed source_reduction_values_int8 长度与 K 不符")
                for reduction_index, expected_value in enumerate(expected_values):
                    oracle = _oracle_tap(
                        descriptor, output_batch, output_channel, output_y,
                        output_x, reduction_index,
                    )
                    if (expected_value is None) != bool(oracle[5]):
                        raise ValueError(
                            f"layer {descriptor['layer_index']} directed case {case_index} "
                            f"k={reduction_index}: null 与 padding 标志不一致"
                        )
                    if expected_value is not None and not -127 <= int(expected_value) <= 127:
                        raise ValueError("G0 directed INT8 来源值超出对称量化域")
                encoded = _encode_vector(
                    1, descriptor, case_index, output_channel, output_y, output_x,
                )
                vector_stream.write(encoded)
                vector_file_hash.update(encoded)
                vector_taps, vector_padding = _tap_digest_update(
                    golden_hash, 1, descriptor, case_index, output_batch,
                    output_channel, output_y, output_x,
                )
                layer_directed_taps += vector_taps
                taps["directed"] += vector_taps
                taps["padding"] += vector_padding
                taps["valid"] += vector_taps - vector_padding
                counts["directed_cases"] += 1
            if rng.state != after_random:
                raise ValueError("G0 directed vectors不应消耗共享 PRNG")
            layers_evidence.append({
                "layer_index": descriptor["layer_index"],
                "input_producer": layer["input_tensor_indices"][0],
                "input_shape_nchw": layer["input_shape_nchw"],
                "input_base_address": descriptor["input_base_address"],
                "input_length_bytes": descriptor["input_length_bytes"],
                "output_shape_nchw": layer["output_shape_nchw"],
                "kernel_hw": [descriptor["kernel_height"], descriptor["kernel_width"]],
                "stride_hw": [descriptor["stride_y"], descriptor["stride_x"]],
                "padding_lrtb": [descriptor["pad_left"], descriptor["pad_right"],
                                  descriptor["pad_top"], descriptor["pad_bottom"]],
                "groups": descriptor["groups"],
                "reduction_count": descriptor["reduction_count"],
                "random_taps": layer_random_taps,
                "directed_taps": layer_directed_taps,
                "state_before_random": f"0x{before_random:08X}",
                "state_after_random": f"0x{after_random:08X}",
            })

        fixture = plan["separate_unit_fixtures"]["conv_zero_padding_3x3"]
        fixture_shape = list(map(int, fixture["input_shape_nchw"]))
        fixture_kernel = [3, 3]
        if (fixture_shape != [1, 1, 3, 3] or
                list(map(int, fixture["stride_hw"])) != [1, 1] or
                list(map(int, fixture["padding_lrtb"])) != [1, 1, 1, 1] or
                int(fixture["padding_value_int8"]) != 0):
            raise ValueError("G0 zero-padding convolution fixture 规格变化")
        if len(fixture["input_int8_nchw"][0][0]) != 3 or len(fixture["expected_accumulator_nchw"][0][0]) != 3:
            raise ValueError("G0 convolution fixture 矩阵尺寸不是 3x3")
        fixture_descriptor = {
            "layer_index": -1,
            "input_base_address": 0xF0000000,
            "input_length_bytes": 9,
            "input_batch_count": 1,
            "input_channels": 1,
            "input_height": 3,
            "input_width": 3,
            "output_batch_count": 1,
            "output_channels": 1,
            "output_height": 3,
            "output_width": 3,
            "kernel_height": fixture_kernel[0],
            "kernel_width": fixture_kernel[1],
            "stride_y": 1,
            "stride_x": 1,
            "pad_left": 1,
            "pad_right": 1,
            "pad_top": 1,
            "pad_bottom": 1,
            "padding_value_int8": 0,
            "groups": 1,
            "reduction_count": 9,
        }
        for output_y in range(fixture_descriptor["output_height"]):
            for output_x in range(fixture_descriptor["output_width"]):
                case_index = output_y * fixture_descriptor["output_width"] + output_x
                encoded = _encode_vector(2, fixture_descriptor, case_index, 0, output_y, output_x)
                vector_stream.write(encoded)
                vector_file_hash.update(encoded)
                vector_taps, vector_padding = _tap_digest_update(
                    golden_hash, 2, fixture_descriptor, case_index, 0, 0,
                    output_y, output_x,
                )
                taps["fixture"] += vector_taps
                taps["padding"] += vector_padding
                taps["valid"] += vector_taps - vector_padding
                counts["fixture_output_points"] += 1

    if rng.state != _EXPECTED_RANDOM_FINAL_STATE:
        raise ValueError(
            f"G0 卷积随机 PRNG 终态不匹配：0x{rng.state:08X}，"
            f"期望 0x{_EXPECTED_RANDOM_FINAL_STATE:08X}"
        )
    expected_counts = {
        "random_output_points": 21000,
        "directed_cases": 336,
        "fixture_output_points": 9,
    }
    if counts != expected_counts:
        raise ValueError(f"G0 卷积 vector 数量变化：{counts}")
    expected_taps = {"random": 20731000, "directed": 331696, "fixture": 81}
    if {key: taps[key] for key in expected_taps} != expected_taps:
        raise ValueError(f"G0 卷积 tap 总数变化：{taps}")
    return {
        "vector_sha256": _sha256_file(destination),
        "golden_output_sha256": golden_hash.hexdigest(),
        "random_activation_draw_sha256": activation_hash.hexdigest(),
        "vector_file_bytes": destination.stat().st_size,
        "random_activation_draws": activation_draws,
        "counts": counts,
        "tap_counts": taps,
        "layers": layers_evidence,
        "shared_prng": {
            "seed": _RANDOM_SEED,
            **shared_state,
            "state_after_convolution": f"0x{rng.state:08X}",
            "expected_state_after_convolution": f"0x{_EXPECTED_RANDOM_FINAL_STATE:08X}",
            "draw_order": "每个模型卷积层按 cfg layer_index；每个随机输出点先抽 channel,row,column，再按 input_channel,kernel_y,kernel_x 消耗 K 个 INT8 activation；directed 与 fixture 不消耗随机流",
        },
        "fixture_address_semantics": "base_address=0xF0000000 仅为不重叠的本地 synthetic fixture 地址；测试相对 NCHW byte offset，不代表模型或硬件映射地址",
    }


def _run_vivado(tool: Path, arguments: list[str], cwd: Path,
                log_path: Path, deadline: float) -> tuple[int, str]:
    """在已隔离工作目录运行一个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    working_directory = cwd.resolve(strict=True)
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    repository_root = Path(__file__).resolve().parents[1]
    if (not working_directory.is_relative_to(temporary_root) or
            working_directory == repository_root):
        raise RuntimeError(f"Vivado cwd 不在系统临时目录：{working_directory}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Vivado 三阶段达到 600 秒停止条件")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    process = subprocess.run(
        f'cmd.exe /d /s /c "{command}"',
        cwd=working_directory,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=remaining,
    )
    output = process.stdout + process.stderr
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return process.returncode, output


class TestS2AConvTapGeometryRtl(unittest.TestCase):
    """在真实 Vivado 仿真器中核对 tiny416 卷积 tap 几何。"""

    def test_conv_taps_against_g0_and_d2(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(manifest_sha, _MANIFEST_SHA256,
                         "G0 manifest SHA 变化，按停止条件中止")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        formal_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
        d2_path = repository / "verification/s1_t02_d2_int8_forward.py"
        rtl_path = repository / "src/int8_conv_tap_geometry.sv"
        bench_path = repository / "sim/tb_s2a_conv_tap_geometry.sv"
        runner_path = Path(__file__).resolve()
        evidence_directory = repository / "report/evidence/S2A-T07"
        evidence_path = evidence_directory / "conv_tap_geometry_simulation.json"
        for path in (formal_path, d2_path, rtl_path, bench_path, runner_path):
            self.assertTrue(path.is_file(), f"缺少正式依据或实现文件：{path}")
        tool_paths = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
        for tool in tool_paths.values():
            self.assertTrue(tool.is_file(), f"缺少 Vivado 工具：{tool}")
        source_hashes_before = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(runner_path),
        }
        document_hashes = {
            "g0_document_sha256": _sha256_file(formal_path),
            "d2_reference_sha256": _sha256_file(d2_path),
        }
        started = time.monotonic()
        deadline = started + 600.0
        phase_codes: list[dict] = []
        with tempfile.TemporaryDirectory(prefix="s2a_t07_conv_tap_geometry_") as temporary:
            work = Path(temporary).resolve()
            self.assertTrue(work.is_dir(), "Vivado 隔离临时目录不存在")
            vectors_path = work / "vectors.dat"
            vector_result = _materialize_vectors(manifest, vectors_path)
            self.assertEqual(vector_result["counts"], {
                "random_output_points": 21000,
                "directed_cases": 336,
                "fixture_output_points": 9,
            })
            self.assertEqual(vector_result["shared_prng"]["state_after_convolution"], "0x2DC4F9F4")
            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_conv_tap_geometry",
                           "-snapshot", "s2a_conv_tap_geometry_snapshot"]),
                ("xsim", ["-R", "s2a_conv_tap_geometry_snapshot"]),
            ]
            for name, arguments in phases:
                code, output = _run_vivado(
                    tool_paths[name], arguments, work, work / f"{name}.log", deadline,
                )
                phase_codes.append({"phase": name, "exit_code": code})
                self.assertEqual(code, 0,
                                 f"{name} 退出码 {code}；隔离日志尾部：\n{output[-5000:]}")
                if name == "xsim":
                    self.assertIn(
                        "PASS: random_taps=20731000 directed_taps=331696 fixture_taps=81 random_points=21000 directed_cases=336 fixture_points=9 bad_argument=23 bad_range=3 boundary=1 pad_success=1",
                        output,
                    )

        self.assertEqual([item["exit_code"] for item in phase_codes], [0, 0, 0])
        source_hashes_after = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(runner_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真期间实现/测试文件发生变化")
        self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                         "G0 manifest 在验证期间发生变化")
        evidence = {
            "schema_version": "gestureforge_s2a_t07_conv_tap_geometry_simulation_v1",
            "result": "PASS",
            "scope": "tiny416 卷积单输出点的全部 reduction tap 坐标、padding 标志和 NCHW INT8 逻辑字节地址",
            "bindings": {
                "g0_manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "g0_manifest_sha256": manifest_sha,
                **document_hashes,
                **source_hashes_after,
                "stimulus_vector_sha256": vector_result["vector_sha256"],
                "geometry_golden_sha256": vector_result["golden_output_sha256"],
                "random_activation_draw_sha256": vector_result["random_activation_draw_sha256"],
            },
            "randomness": vector_result["shared_prng"],
            "counts": vector_result["counts"],
            "tap_counts": vector_result["tap_counts"],
            "random_activation_draws": vector_result["random_activation_draws"],
            "vector_file_bytes": vector_result["vector_file_bytes"],
            "model_layers": vector_result["layers"],
            "error_assertions": {
                "BAD_ARGUMENT_code_1": 23,
                "BAD_RANGE_code_2": 3,
                "maximum_uint32_last_byte_success": 1,
                "padding_success_without_address": 1,
            },
            "vivado": {
                "bin": str(_XILINX_BIN),
                "phases": phase_codes,
                "command_template": "python -B -m unittest verification.test_s2a_conv_tap_geometry_rtl -v",
            },
            "fixture_address_semantics": vector_result["fixture_address_semantics"],
            "limitations": [
                "仅查询卷积输入 tap 几何，不计算权重地址、MAC、输出量化或访存事务。",
                "groups 仅支持 G0 实际冻结为 1 的卷积层。",
                "零填充 3x3 fixture 使用本地 synthetic 地址；不代表模型张量映射。",
                "不代表完整网络逐层黄金比对、PS 解码/NMS、综合、资源估算、时序或板上验证通过。",
            ],
        }
        evidence_directory.mkdir(parents=True, exist_ok=True)
        evidence_bytes = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.assertFalse(evidence_bytes.startswith(b"\xef\xbb\xbf"), "证据 JSON 不得含 UTF-8 BOM")
        self.assertNotIn(b"\r", evidence_bytes, "证据 JSON 必须使用 LF")
        evidence_path.write_bytes(evidence_bytes)
        print(
            "S2A-T07 manifest_sha256={} vectors_sha256={} golden_sha256={} "
            "counts={} prng_final={} vivado={}".format(
                manifest_sha,
                vector_result["vector_sha256"],
                vector_result["golden_output_sha256"],
                vector_result["counts"],
                vector_result["shared_prng"]["state_after_convolution"],
                [item["exit_code"] for item in phase_codes],
            )
        )


if __name__ == "__main__":
    unittest.main()
