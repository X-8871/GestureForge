"""按 G0 与 D2 参考验证 maxpool 窗口几何和 NCHW 地址。"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_SEED = 20260922
_PAD_VALUE = -127


class XorShift32:
    """维护 G0 定义的共享 xorshift32 随机状态。"""

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
            raise ValueError("G0 随机选择器上界必须大于零")
        return self.next_u32() % bound

    def int8(self) -> int:
        return (self.next_u32() & 0xFF) % 255 - 127

    def int32(self) -> int:
        value = self.next_u32()
        return value if value < 0x80000000 else value - 0x100000000


def _sha256_bytes(data: bytes) -> str:
    """计算不可变字节的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _conv_reduction_lengths(manifest: dict) -> list[int]:
    """读取按 cfg layer_index 排序的真实卷积 reduction 长度。"""
    layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths: list[int] = []
    for layer in layers:
        input_channels = layer["input_shape_nchw"][1]
        groups = layer["groups"]
        kernel_h, kernel_w = layer["kernel_hw"]
        if input_channels % groups:
            raise ValueError("G0 卷积通道不能被 groups 整除")
        lengths.append((input_channels // groups) * kernel_h * kernel_w)
    if len(lengths) != 21:
        raise ValueError("G0 tiny416 卷积层数量不再是 21")
    return lengths


def _advance_before_maxpool(manifest: dict, rng: XorShift32) -> dict:
    """按 G0 case_order 消费卷积和共享 MAC 的全部随机抽样。"""
    plan = manifest["operator_test_plan"]
    if (plan["random_cases_per_model_layer"] != 1000 or
            plan["shared_primitive_random_cases"] != 1000 or
            "ASCII order" not in plan["case_order"] or
            "int8_mac" not in plan["case_order"]):
        raise ValueError("G0 随机样本数或算子顺序约定变化")

    convolution_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths = _conv_reduction_lengths(manifest)
    for layer, reduction_length in zip(convolution_layers, lengths, strict=True):
        channels, height, width = layer["output_shape_nchw"][1:]
        for _ in range(plan["random_cases_per_model_layer"]):
            rng.selector(channels)
            rng.selector(height)
            rng.selector(width)
            for _ in range(reduction_length):
                rng.int8()
    state_after_convolution = rng.state

    for case_index in range(plan["shared_primitive_random_cases"]):
        reduction_length = lengths[case_index % len(lengths)]
        for _ in range(reduction_length):
            rng.int8()
        for _ in range(reduction_length):
            rng.int8()
        rng.int32()

    return {
        "state_after_convolution": f"0x{state_after_convolution:08X}",
        "state_before_maxpool": f"0x{rng.state:08X}",
        "convolution_layers": len(convolution_layers),
        "mac_random_vectors": plan["shared_primitive_random_cases"],
    }


def _d2_output_size(input_size: int, padding: int, kernel: int, stride: int) -> int:
    """按 D2 Darknet maxpool 公式计算一维输出大小。"""
    return (input_size + padding - kernel) // stride + 1


def _d2_reference_coordinates(
    channel: int,
    output_y: int,
    output_x: int,
    kernel_height: int,
    kernel_width: int,
    stride_y: int,
    stride_x: int,
    padding_parameter: int,
) -> list[tuple[int, int, int]]:
    """按 D2 `maxpool` 的 origin 和 row-major tap 顺序给出来源坐标。"""
    origin_y = -(padding_parameter // 2)
    origin_x = -(padding_parameter // 2)
    first_y = origin_y + output_y * stride_y
    first_x = origin_x + output_x * stride_x
    return [
        (channel, first_y + kernel_y, first_x + kernel_x)
        for kernel_y in range(kernel_height)
        for kernel_x in range(kernel_width)
    ]


def _tap_records(
    coordinates: list[tuple[int, int, int]],
    channels: int,
    height: int,
    width: int,
    base_address: int,
    tensor_length_bytes: int,
) -> tuple[int, list[dict]]:
    """将参考坐标转换为有效位、NCHW 偏移和 uint32 地址。"""
    mask = 0
    taps: list[dict] = []
    if len(coordinates) not in (4, 9):
        raise ValueError("G0 maxpool tap 数量必须为 4 或 9")
    for tap_index, (channel, source_y, source_x) in enumerate(coordinates):
        valid = (0 <= channel < channels and 0 <= source_y < height and
                 0 <= source_x < width)
        if valid:
            offset = (channel * height + source_y) * width + source_x
            address = base_address + offset
            if offset >= tensor_length_bytes:
                raise ValueError("参考 NCHW 偏移超出来源张量长度")
            if address > 0xFFFFFFFF:
                raise ValueError("G0 模型输入地址在 uint32 内越界")
            mask |= 1 << tap_index
        else:
            offset = 0
            address = 0
        taps.append({
            "valid": int(valid),
            "channel": channel,
            "y": source_y,
            "x": source_x,
            "offset": offset,
            "address": address,
        })
    taps.extend({
        "valid": 0, "channel": 0, "y": 0, "x": 0, "offset": 0, "address": 0
    } for _ in range(9 - len(taps)))
    return mask, taps


def _golden_digest_update(digest, record: dict) -> None:
    """仅以期望几何输出更新逐 tap 黄金摘要。"""
    golden = {
        key: record[key]
        for key in (
            "vector_class", "layer_index", "case_index", "output_height",
            "output_width", "tap_count", "tap_mask", "error_code",
        )
    }
    golden["taps"] = [
        {
            key: tap[key]
            for key in ("valid", "channel", "y", "x", "offset", "address")
        }
        for tap in record["taps"]
    ]
    encoded = json.dumps(golden, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    digest.update(encoded)
    digest.update(b"\n")


def _write_vector(stream, vector: dict) -> None:
    """写出一条文件头和九条逐 tap 期望记录。"""
    header = [
        vector["vector_class"], vector["layer_index"], vector["case_index"],
        vector["base_address"], vector["input_channels"], vector["input_height"],
        vector["input_width"], vector["kernel_height"], vector["kernel_width"],
        vector["stride_y"], vector["stride_x"], vector["padding_parameter"],
        vector["input_channel"], vector["output_y"], vector["output_x"],
        vector["output_height"], vector["output_width"], vector["tap_count"],
        vector["tap_mask"], vector["error_code"], *vector["draw_values_int8"],
    ]
    stream.write(" ".join(str(value) for value in header) + "\n")
    for tap in vector["taps"]:
        stream.write("{} {} {} {} {} {}\n".format(
            tap["valid"], tap["channel"], tap["y"], tap["x"],
            tap["offset"], tap["address"],
        ))


def _model_vector(
    vector_class: int,
    layer: dict,
    case_index: int,
    output_y: int,
    output_x: int,
    coordinates: list[tuple[int, int, int]],
    draw_values: list[int],
    layer_by_index: dict[int, dict],
) -> dict:
    """绑定模型输入生产层的真实地址并构造一个窗口向量。"""
    input_indices = layer["input_tensor_indices"]
    if len(input_indices) != 1:
        raise ValueError(f"maxpool {layer['layer_index']} 输入引用数量变化")
    producer = layer_by_index[input_indices[0]]
    input_shape = layer["input_shape_nchw"]
    if producer["output_shape_nchw"] != input_shape:
        raise ValueError("maxpool 输入 shape 与生产层输出不一致")
    batch, channels, height, width = input_shape
    if batch != 1 or len(draw_values) != 4:
        raise ValueError("G0 tiny416 maxpool batch 或 tap 抽样数量变化")
    kernel_height, kernel_width = layer["kernel_hw"]
    stride_y, stride_x = layer["stride_hw"]
    padding = layer["darknet_padding_parameter"]
    expected_h = _d2_output_size(height, padding, kernel_height, stride_y)
    expected_w = _d2_output_size(width, padding, kernel_width, stride_x)
    if [expected_h, expected_w] != layer["output_shape_nchw"][2:]:
        raise ValueError(f"maxpool {layer['layer_index']} D2 输出尺寸与 G0 不符")
    base_address = producer["tensor_address"]
    tensor_length = producer["tensor_length_bytes"]
    if tensor_length != channels * height * width:
        raise ValueError("maxpool 来源张量字节长度与 NCHW INT8 不符")
    mask, taps = _tap_records(
        coordinates, channels, height, width, base_address, tensor_length
    )
    if len(coordinates) != kernel_height * kernel_width:
        raise ValueError("maxpool 参考 tap 数量与层 kernel 不符")
    return {
        "vector_class": vector_class,
        "layer_index": layer["layer_index"],
        "case_index": case_index,
        "base_address": base_address,
        "input_channels": channels,
        "input_height": height,
        "input_width": width,
        "kernel_height": kernel_height,
        "kernel_width": kernel_width,
        "stride_y": stride_y,
        "stride_x": stride_x,
        "padding_parameter": padding,
        "input_channel": coordinates[0][0],
        "output_y": output_y,
        "output_x": output_x,
        "output_height": expected_h,
        "output_width": expected_w,
        "tap_count": len(coordinates),
        "tap_mask": mask,
        "error_code": 0,
        "draw_values_int8": draw_values,
        "taps": taps,
    }


def _materialize_vectors(manifest: dict, destination: Path) -> dict:
    """生成模型 1000+16 向量和完整 4x4 padding fixture。"""
    plan = manifest["operator_test_plan"]
    rng = XorShift32(_RANDOM_SEED)
    stream_states = _advance_before_maxpool(manifest, rng)
    state_before_pool = rng.state
    vector_digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    counts = {"random": 0, "directed": 0, "fixture_windows": 0}
    tap_counts = {"model": 0, "fixture": 0, "valid": 0, "padding": 0}
    layer_counts: list[dict] = []
    layer_by_index = {layer["layer_index"]: layer for layer in manifest["layers"]}
    pool_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "maxpool"),
        key=lambda layer: layer["layer_index"],
    )
    if [layer["layer_index"] for layer in pool_layers] != [9, 17, 25]:
        raise ValueError("G0 tiny416 maxpool 层索引变化")
    if plan["random_cases_per_model_layer"] != 1000 or plan["directed_cases_per_model_layer"] != 16:
        raise ValueError("G0 maxpool 随机/定向用例数量变化")

    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        for layer in pool_layers:
            layer_index = layer["layer_index"]
            channels, input_height, input_width = layer["input_shape_nchw"][1:]
            output_height, output_width = layer["output_shape_nchw"][2:]
            kernel_height, kernel_width = layer["kernel_hw"]
            stride_y, stride_x = layer["stride_hw"]
            if (layer["layout"] != "NCHW" or [kernel_height, kernel_width] != [2, 2] or
                    [stride_y, stride_x] != [2, 2] or
                    layer["darknet_padding_parameter"] != 1 or
                    layer["window_origin_yx_at_output_0"] != [0, 0] or
                    layer["padding_lrtb_actual"] != [0, 0, 0, 0] or
                    layer["pad_value_int8"] != _PAD_VALUE):
                raise ValueError(f"G0 maxpool {layer_index} 模型几何或 padding 变化")

            before_layer = rng.state
            for case_index in range(plan["random_cases_per_model_layer"]):
                input_channel = rng.selector(channels)
                output_y = rng.selector(output_height)
                output_x = rng.selector(output_width)
                draw_values = [rng.int8() for _ in range(kernel_height * kernel_width)]
                coordinates = _d2_reference_coordinates(
                    input_channel, output_y, output_x,
                    kernel_height, kernel_width, stride_y, stride_x,
                    layer["darknet_padding_parameter"],
                )
                vector = _model_vector(
                    0, layer, case_index, output_y, output_x,
                    coordinates, draw_values, layer_by_index,
                )
                _write_vector(stream, vector)
                _golden_digest_update(golden_digest, vector)
                vector_digest.update(json.dumps(
                    vector, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii") + b"\n")
                counts["random"] += 1
                tap_counts["model"] += vector["tap_count"]
                tap_counts["valid"] += sum(tap["valid"] for tap in vector["taps"][:vector["tap_count"]])
                tap_counts["padding"] += vector["tap_count"] - sum(
                    tap["valid"] for tap in vector["taps"][:vector["tap_count"]]
                )

            state_after_random = rng.state
            directed_vectors = plan["directed_case_vectors"]["maxpool"][str(layer_index)]
            if len(directed_vectors) != 16:
                raise ValueError(f"G0 maxpool {layer_index} 定向向量数量变化")
            for directed in directed_vectors:
                case_index = directed["case_index"]
                target = directed["target_output_nchw"]
                if target[0] != 0:
                    raise ValueError("G0 maxpool directed batch 必须为 0")
                input_channel, output_y, output_x = target[1:]
                coordinates = [tuple(item) for item in directed["input_coordinates_cyx"]]
                if len(coordinates) != kernel_height * kernel_width:
                    raise ValueError("冻结 directed 输入坐标与 kernel tap 数不符")
                if len(directed["candidate_values_int8"]) != kernel_height * kernel_width:
                    raise ValueError("冻结 directed 候选值与 kernel tap 数不符")
                vector = _model_vector(
                    1, layer, case_index, output_y, output_x,
                    coordinates, directed["candidate_values_int8"][:4],
                    layer_by_index,
                )
                if vector["input_channel"] != input_channel:
                    raise ValueError("G0 directed channel 与冻结坐标不一致")
                if vector["taps"][:4] and [
                    (tap["channel"], tap["y"], tap["x"])
                    for tap in vector["taps"][:4]
                ] != coordinates:
                    raise ValueError("G0 directed 来源坐标未原样保留")
                if directed["input_window_origin_yx"] != [
                    coordinates[0][1], coordinates[0][2]
                ]:
                    raise ValueError("G0 directed 窗口原点与首个冻结坐标不符")
                _write_vector(stream, vector)
                _golden_digest_update(golden_digest, vector)
                vector_digest.update(json.dumps(
                    vector, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii") + b"\n")
                counts["directed"] += 1
                tap_counts["model"] += vector["tap_count"]
                tap_counts["valid"] += sum(tap["valid"] for tap in vector["taps"][:vector["tap_count"]])
                tap_counts["padding"] += vector["tap_count"] - sum(
                    tap["valid"] for tap in vector["taps"][:vector["tap_count"]]
                )
            if rng.state != state_after_random:
                raise ValueError("G0 定向向量意外消耗共享 PRNG 状态")
            layer_counts.append({
                "layer_index": layer_index,
                "random": plan["random_cases_per_model_layer"],
                "directed": len(directed_vectors),
                "total": plan["random_cases_per_model_layer"] + len(directed_vectors),
                "state_before_random": f"0x{before_layer:08X}",
                "state_after_random": f"0x{state_after_random:08X}",
            })

        fixture = plan["separate_unit_fixtures"]["maxpool_darknet_padding"]
        fixture_image = fixture["input_int8_nchw"][0][0]
        expected_image = fixture["expected_output_nchw"][0][0]
        fixture_channels, fixture_height, fixture_width = fixture["input_shape_nchw"][1:]
        kernel_height, kernel_width = fixture["kernel_hw"]
        stride_y, stride_x = fixture["stride_hw"]
        padding = fixture["darknet_padding_parameter"]
        origin_y, origin_x = fixture["window_origin_yx_at_output_0"]
        if (fixture["input_shape_nchw"] != [1, 1, 4, 4] or
                [kernel_height, kernel_width] != [3, 3] or
                [stride_y, stride_x] != [1, 1] or
                fixture["padding_lrtb_actual"] != [1, 1, 1, 1] or
                [origin_y, origin_x] != [-1, -1] or
                fixture["pad_value_int8"] != _PAD_VALUE):
            raise ValueError("G0 maxpool padding fixture 规格变化")
        expected_fixture_height = len(expected_image)
        expected_fixture_width = len(expected_image[0])
        if (_d2_output_size(fixture_height, padding, kernel_height, stride_y) != expected_fixture_height or
                _d2_output_size(fixture_width, padding, kernel_width, stride_x) != expected_fixture_width):
            raise ValueError("D2 maxpool 公式与冻结 padding fixture 输出形状不符")
        fixture_length = fixture_channels * fixture_height * fixture_width
        for output_y in range(expected_fixture_height):
            for output_x in range(expected_fixture_width):
                coordinates = [
                    (0, origin_y + output_y * stride_y + kernel_y,
                     origin_x + output_x * stride_x + kernel_x)
                    for kernel_y in range(kernel_height)
                    for kernel_x in range(kernel_width)
                ]
                draw_values = []
                for _, source_y, source_x in coordinates[:4]:
                    if 0 <= source_y < fixture_height and 0 <= source_x < fixture_width:
                        draw_values.append(fixture_image[source_y][source_x])
                    else:
                        draw_values.append(fixture["pad_value_int8"])
                mask, taps = _tap_records(
                    coordinates, fixture_channels, fixture_height, fixture_width,
                    0, fixture_length,
                )
                case_index = output_y * expected_fixture_width + output_x
                vector = {
                    "vector_class": 2,
                    "layer_index": -1,
                    "case_index": case_index,
                    "base_address": 0,
                    "input_channels": fixture_channels,
                    "input_height": fixture_height,
                    "input_width": fixture_width,
                    "kernel_height": kernel_height,
                    "kernel_width": kernel_width,
                    "stride_y": stride_y,
                    "stride_x": stride_x,
                    "padding_parameter": padding,
                    "input_channel": 0,
                    "output_y": output_y,
                    "output_x": output_x,
                    "output_height": expected_fixture_height,
                    "output_width": expected_fixture_width,
                    "tap_count": kernel_height * kernel_width,
                    "tap_mask": mask,
                    "error_code": 0,
                    "draw_values_int8": draw_values,
                    "taps": taps,
                }
                if vector["tap_count"] != 9 or len(expected_image[output_y]) != expected_fixture_width:
                    raise ValueError("G0 fixture 输出或 tap 数量变化")
                _write_vector(stream, vector)
                _golden_digest_update(golden_digest, vector)
                vector_digest.update(json.dumps(
                    vector, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii") + b"\n")
                counts["fixture_windows"] += 1
                tap_counts["fixture"] += vector["tap_count"]
                tap_counts["valid"] += sum(tap["valid"] for tap in vector["taps"][:vector["tap_count"]])
                tap_counts["padding"] += vector["tap_count"] - sum(
                    tap["valid"] for tap in vector["taps"][:vector["tap_count"]]
                )

    expected_counts = {"random": 3000, "directed": 48, "fixture_windows": 16}
    if counts != expected_counts:
        raise ValueError(f"G0 maxpool 向量数量不符：{counts}")
    if rng.state == state_before_pool:
        raise ValueError("maxpool 随机流未按 G0 消耗")
    return {
        "vector_sha256": _sha256_file(destination),
        "logical_vector_sha256": vector_digest.hexdigest(),
        "golden_output_sha256": golden_digest.hexdigest(),
        "vector_file_bytes": destination.stat().st_size,
        "counts": counts,
        "tap_counts": tap_counts,
        "layers": layer_counts,
        "shared_prng": {
            "seed": _RANDOM_SEED,
            **stream_states,
            "state_before_maxpool": f"0x{state_before_pool:08X}",
            "state_after_maxpool": f"0x{rng.state:08X}",
            "draws_per_model_random_case": "channel selector, output row selector, output column selector, then four INT8 candidate values",
        },
        "fixture_address_semantics": "base_address=0 仅用于验证相对 NCHW byte offset，不表示模型或硬件地址映射",
    }


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float) -> tuple[int, str]:
    """在共享 600 秒截止时间内调用一个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Vivado 仿真总耗时达到 600 秒停止条件")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    process = subprocess.run(
        f'cmd.exe /d /s /c "{command}"',
        cwd=cwd,
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


class TestS2AMaxpoolGeometryRtl(unittest.TestCase):
    """验证 G0 模型池化窗口、padding fixture 和非法地址边界。"""

    def test_vivado_geometry_against_g0_coordinates(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(
            manifest_sha, _MANIFEST_SHA256,
            "G0 manifest 原始字节 SHA 变化，按停止条件中止",
        )
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        evidence_directory = repository / "report/evidence/S2A-T04"
        evidence_path = evidence_directory / "maxpool_geometry_simulation.json"
        rtl_path = repository / "src/int8_maxpool_geometry.sv"
        bench_path = repository / "sim/tb_s2a_maxpool_geometry.sv"
        script_path = Path(__file__).resolve()
        for source in (rtl_path, bench_path, script_path):
            self.assertTrue(source.is_file(), f"缺少验证源文件：{source}")
        tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"未找到 Vivado 工具：{tool}")

        source_hashes_before = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        start_time = time.monotonic()
        deadline = start_time + 600.0
        phase_codes: list[dict] = []
        with tempfile.TemporaryDirectory(prefix="s2a_t04_maxpool_geometry_") as temporary:
            work = Path(temporary)
            vectors_path = work / "vectors.dat"
            vector_result = _materialize_vectors(manifest, vectors_path)
            self.assertGreater(vector_result["vector_file_bytes"], 0)
            self.assertEqual(vector_result["counts"], {
                "random": 3000, "directed": 48, "fixture_windows": 16,
            })

            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_maxpool_geometry",
                           "-snapshot", "s2a_maxpool_geometry_snapshot"]),
                ("xsim", ["-R", "s2a_maxpool_geometry_snapshot"]),
            ]
            for name, arguments in phases:
                code, output = _run_tool(
                    tools[name], arguments, work, work / f"{name}.log", deadline
                )
                phase_codes.append({"phase": name, "exit_code": code})
                self.assertEqual(
                    code, 0,
                    f"{name} 退出码 {code}；临时日志尾部：\n{output[-5000:]}",
                )
                if name == "xsim":
                    self.assertIn(
                        "PASS: records=3064 model_random=3000 model_directed=48 fixture_windows=16 model_taps=12192 fixture_taps=144 bad_argument=11 bad_range=2 boundary=1",
                        output,
                    )

        self.assertEqual([item["exit_code"] for item in phase_codes], [0, 0, 0])
        source_hashes_after = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真过程中源文件发生变化")
        manifest_sha_after = _sha256_file(manifest_path)
        self.assertEqual(manifest_sha_after, _MANIFEST_SHA256,
                         "仿真过程中 G0 manifest 原始字节发生变化")

        evidence = {
            "schema_version": "gestureforge_s2a_t04_maxpool_geometry_simulation_v1",
            "result": "PASS",
            "scope": "单输出窗口 maxpool 几何、逐 tap 坐标、有效掩码、NCHW 逻辑 byte offset 与地址",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": manifest_sha,
                **source_hashes_after,
                "vector_sha256": vector_result["vector_sha256"],
                "logical_vector_sha256": vector_result["logical_vector_sha256"],
                "golden_output_sha256": vector_result["golden_output_sha256"],
            },
            "random_vectors": vector_result["shared_prng"],
            "counts": vector_result["counts"],
            "tap_counts": vector_result["tap_counts"],
            "vector_file_bytes": vector_result["vector_file_bytes"],
            "error_assertions": {
                "BAD_ARGUMENT_code_1": 11,
                "BAD_RANGE_code_2": 2,
                "maximum_uint32_boundary_success": 1,
            },
            "model_layers": vector_result["layers"],
            "vivado": {
                "bin": str(_XILINX_BIN),
                "phases": phase_codes,
                "command_template": "python -B -m unittest verification.test_s2a_maxpool_geometry_rtl -v",
            },
            "fixture_address_semantics": vector_result["fixture_address_semantics"],
            "limitations": [
                "不发起内存读写事务，不实现完整 maxpool layer engine。",
                "仅支持冻结 tiny416 2x2 模型窗口和独立 3x3 padding fixture；拒绝其他 kernel。",
                "不代表完整网络逐层黄金比对、PS 解码/NMS、Vivado 综合、资源估算或时序通过。",
            ],
        }
        evidence_directory.mkdir(parents=True, exist_ok=True)
        evidence_bytes = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        evidence_path.write_bytes(evidence_bytes)
        print(
            "S2A-T04 manifest_sha256={} vector_sha256={} golden_sha256={} "
            "counts={} prng_before_pool={} prng_after_pool={} vivado={}".format(
                manifest_sha,
                vector_result["vector_sha256"],
                vector_result["golden_output_sha256"],
                vector_result["counts"],
                vector_result["shared_prng"]["state_before_maxpool"],
                vector_result["shared_prng"]["state_after_maxpool"],
                [item["exit_code"] for item in phase_codes],
            )
        )


if __name__ == "__main__":
    unittest.main()
