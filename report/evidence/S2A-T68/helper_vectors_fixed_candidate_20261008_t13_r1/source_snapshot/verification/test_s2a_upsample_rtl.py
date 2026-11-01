"""按 G0 冻结清单和共享随机流验证 nearest-repeat 单点查询 RTL。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_SEED = 20260922
_MAX_PLANE_DIMENSION = 13


class XorShift32:
    """维护 G0 定义的一条共享 xorshift32 状态流。"""

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
    """按 cfg layer_index 提取真实卷积点积长度。"""
    layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths: list[int] = []
    for layer in layers:
        input_channels = layer["input_shape_nchw"][1]
        groups = layer["groups"]
        kernel_height, kernel_width = layer["kernel_hw"]
        if input_channels % groups:
            raise ValueError("G0 卷积输入通道不能被 groups 整除")
        lengths.append((input_channels // groups) * kernel_height * kernel_width)
    if len(lengths) != 21:
        raise ValueError("G0 tiny416 卷积层数量不再是 21")
    return lengths


def _advance_to_upsample(manifest: dict, rng: XorShift32) -> dict:
    """独立按 G0 case_order 推进 convolution、MAC、maxpool 和 route。"""
    plan = manifest["operator_test_plan"]
    cases = plan["random_cases_per_model_layer"]
    if (cases != 1000 or plan["shared_primitive_random_cases"] != 1000 or
            "ASCII order" not in plan["case_order"] or "int8_mac" not in plan["case_order"]):
        raise ValueError("G0 算子随机顺序或样本数发生变化")

    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    reduction_lengths = _conv_reduction_lengths(manifest)
    for layer, reduction_length in zip(conv_layers, reduction_lengths, strict=True):
        output_channels, output_height, output_width = layer["output_shape_nchw"][1:]
        for _ in range(cases):
            rng.selector(output_channels)
            rng.selector(output_height)
            rng.selector(output_width)
            for _ in range(reduction_length):
                rng.int8()
    state_after_convolution = rng.state

    for case_index in range(plan["shared_primitive_random_cases"]):
        reduction_length = reduction_lengths[case_index % len(reduction_lengths)]
        for _ in range(reduction_length):
            rng.int8()
        for _ in range(reduction_length):
            rng.int8()
        rng.int32()
    state_after_mac = rng.state

    pool_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "maxpool"),
        key=lambda layer: layer["layer_index"],
    )
    if [layer["layer_index"] for layer in pool_layers] != [9, 17, 25]:
        raise ValueError("G0 tiny416 maxpool 层顺序变化")
    for layer in pool_layers:
        channels, output_height, output_width = layer["output_shape_nchw"][1:]
        kernel_height, kernel_width = layer["kernel_hw"]
        for _ in range(cases):
            rng.selector(channels)
            rng.selector(output_height)
            rng.selector(output_width)
            for _ in range(kernel_height * kernel_width):
                rng.int8()
    state_after_maxpool = rng.state

    route_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "route"),
        key=lambda layer: layer["layer_index"],
    )
    if len(route_layers) != 11:
        raise ValueError("G0 tiny416 route 层数量不再是 11")
    route_layer_states = []
    for layer in route_layers:
        _, _, output_height, output_width = layer["output_shape_nchw"]
        ranges = layer["route_source_channel_ranges"]
        selected_channels = [end - start for start, end in ranges]
        if not ranges or any(start < 0 or end <= start for start, end in ranges):
            raise ValueError(f"G0 route {layer['layer_index']} 来源通道范围非法")
        state_before = rng.state
        for _ in range(cases):
            rng.selector(output_height)
            rng.selector(output_width)
            for source_channel_count in selected_channels:
                for _ in range(source_channel_count):
                    rng.int8()
        route_layer_states.append({
            "layer_index": layer["layer_index"],
            "selected_source_channels_per_case": selected_channels,
            "state_before_random": f"0x{state_before:08X}",
            "state_after_random": f"0x{rng.state:08X}",
        })
    state_after_route = rng.state
    return {
        "state_after_convolution": f"0x{state_after_convolution:08X}",
        "state_after_int8_mac": f"0x{state_after_mac:08X}",
        "state_after_maxpool": f"0x{state_after_maxpool:08X}",
        "state_after_route": f"0x{state_after_route:08X}",
        "state_before_upsample": f"0x{rng.state:08X}",
        "convolution_layers": len(conv_layers),
        "int8_mac_random_vectors": plan["shared_primitive_random_cases"],
        "maxpool_layers": len(pool_layers),
        "route_layers": len(route_layers),
        "route_layer_states": route_layer_states,
    }


def _pack_source_plane(values: list[int]) -> str:
    """将最多 169 个 row-major INT8 字节打包为低字节优先十六进制。"""
    if len(values) > _MAX_PLANE_DIMENSION * _MAX_PLANE_DIMENSION:
        raise ValueError("来源平面超过 13x13")
    packed = 0
    for index, value in enumerate(values):
        if value < -128 or value > 127:
            raise ValueError("来源平面值超出 INT8")
        packed |= (value & 0xFF) << (index * 8)
    return f"{packed:0338x}"


def _nchw_offset(channel: int, height: int, width: int,
                 source_y: int, source_x: int) -> int:
    """按冻结 NCHW INT8 byte order 计算线性偏移。"""
    return (channel * height + source_y) * width + source_x


def _query_record(
    vector_class: int,
    case_index: int,
    query_index: int,
    base_address: int,
    channels: int,
    input_height: int,
    input_width: int,
    stride: int,
    output_height: int,
    output_width: int,
    output_channel: int,
    output_y: int,
    output_x: int,
    source_channel: int,
    source_y: int,
    source_x: int,
    expected_value: int,
    source_plane: list[int],
    tensor_length_bytes: int,
) -> dict:
    """制作一条单查询激励与独立 NCHW 地址/复制值期望。"""
    if not (0 <= output_channel < channels and 0 <= source_channel < channels):
        raise ValueError("查询或来源通道超出模型通道数")
    if not (0 <= output_y < output_height and 0 <= output_x < output_width):
        raise ValueError("查询输出坐标超出输出平面")
    if not (0 <= source_y < input_height and 0 <= source_x < input_width):
        raise ValueError("来源坐标超出输入平面")
    if len(source_plane) != input_height * input_width:
        raise ValueError("source_plane 必须紧凑 row-major 保存当前通道")
    source_value = source_plane[source_y * input_width + source_x]
    if source_value != expected_value:
        raise ValueError("source plane 读值与冻结输出期望不匹配")
    if source_channel != output_channel:
        raise ValueError("nearest-repeat 不得改变通道索引")
    offset = _nchw_offset(source_channel, input_height, input_width, source_y, source_x)
    address = base_address + offset
    if offset >= tensor_length_bytes or address > 0xFFFFFFFF:
        raise ValueError("查询来源地址超出输入张量或 uint32 地址范围")
    return {
        "vector_class": vector_class,
        "case_index": case_index,
        "query_index": query_index,
        "base_address": base_address,
        "input_channels": channels,
        "input_height": input_height,
        "input_width": input_width,
        "stride": stride,
        "input_channel": output_channel,
        "output_y": output_y,
        "output_x": output_x,
        "output_height": output_height,
        "output_width": output_width,
        "source_channel": source_channel,
        "source_y": source_y,
        "source_x": source_x,
        "source_offset": offset,
        "source_address": address,
        "expected_value": expected_value,
        "error_code": 0,
        "source_plane_hex": _pack_source_plane(source_plane),
    }


def _write_vector(stream, vector: dict, digest) -> None:
    """写出一条查询记录并同步计算精确向量文件摘要。"""
    fields = [
        vector["vector_class"], vector["case_index"], vector["query_index"],
        vector["base_address"], vector["input_channels"], vector["input_height"],
        vector["input_width"], vector["stride"], vector["input_channel"],
        vector["output_y"], vector["output_x"], vector["output_height"],
        vector["output_width"], vector["source_channel"], vector["source_y"],
        vector["source_x"], vector["source_offset"], vector["source_address"],
        vector["expected_value"], vector["error_code"], vector["source_plane_hex"],
    ]
    line = (" ".join(str(value) for value in fields) + "\n").encode("ascii")
    stream.write(line.decode("ascii"))
    digest.update(line)


def _update_golden_digest(digest, vector: dict) -> None:
    """仅将期待输出尺寸、坐标、地址及复制值纳入黄金摘要。"""
    golden = {
        key: vector[key]
        for key in (
            "vector_class", "case_index", "query_index", "output_height",
            "output_width", "source_channel", "source_y", "source_x",
            "source_offset", "source_address", "expected_value", "error_code",
        )
    }
    digest.update(json.dumps(golden, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode("ascii"))
    digest.update(b"\n")


def _make_directed_plane(case: dict, query: dict,
                         channels: int, height: int, width: int) -> list[int]:
    """按 G0 directed source_tensor_rule 构造被查询通道的源平面。"""
    rule = case["source_tensor_rule"]
    default = case["source_tensor_default_int8"]
    source_channel, source_y, source_x = query["source_cyx"]
    plane_size = height * width
    if rule == "single_marker_else_zero":
        plane = [default] * plane_size
        plane[source_y * width + source_x] = query["source_value_int8"]
    elif rule == "zero_source":
        plane = [default] * plane_size
    elif rule == "positive_extreme_source":
        plane = [127] * plane_size
    elif rule == "negative_extreme_source":
        plane = [-127] * plane_size
    elif rule == "flat_nchw_even=-127_odd=+127":
        plane = [
            -127 if ((source_channel * plane_size + index) & 1) == 0 else 127
            for index in range(plane_size)
        ]
    else:
        raise ValueError(f"未识别的 G0 upsample source_tensor_rule：{rule}")
    return plane


def _materialize_vectors(manifest: dict, destination: Path) -> dict:
    """生成模型随机/定向查询和 2x2 fixture 的完整输出查询。"""
    plan = manifest["operator_test_plan"]
    rng = XorShift32(_RANDOM_SEED)
    prng = _advance_to_upsample(manifest, rng)
    state_before_upsample = rng.state
    upsample_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "upsample"),
        key=lambda layer: layer["layer_index"],
    )
    if [layer["layer_index"] for layer in upsample_layers] != [33]:
        raise ValueError("G0 tiny416 upsample 层必须仅含 layer 33")
    layer = upsample_layers[0]
    layer_by_index = {item["layer_index"]: item for item in manifest["layers"]}
    if layer["input_tensor_indices"] != [32]:
        raise ValueError("G0 upsample 输入 producer 索引不是 layer 32")
    producer = layer_by_index[32]
    if (producer["tensor_address"] != 27598336 or
            producer["tensor_length_bytes"] != 21632):
        raise ValueError("G0 layer 32 输入基址或长度与冻结交付规格不符")
    input_shape = layer["input_shape_nchw"]
    output_shape = layer["output_shape_nchw"]
    if (input_shape != [1, 128, 13, 13] or output_shape != [1, 128, 26, 26] or
            producer["output_shape_nchw"] != input_shape):
        raise ValueError("G0 upsample layer 33 shape 或 producer shape 变化")
    channels, input_height, input_width = input_shape[1:]
    output_channels, output_height, output_width = output_shape[1:]
    stride = 2
    if (output_channels != channels or output_height != input_height * stride or
            output_width != input_width * stride or
            layer["stride"] != stride or layer["method"] != "nearest_repeat" or
            layer["input_scale"] != layer["output_scale"]):
        raise ValueError("G0 upsample nearest-repeat shape 或 scale 变化")
    base_address = producer["tensor_address"]
    tensor_length_bytes = producer["tensor_length_bytes"]
    if tensor_length_bytes != channels * input_height * input_width:
        raise ValueError("G0 upsample producer INT8 byte length 不匹配")
    random_count = plan["random_cases_per_model_layer"]
    directed_plan = plan["directed_case_vectors"]["upsample"]["33"]
    if random_count != 1000 or len(directed_plan) != 16:
        raise ValueError("G0 upsample 随机或定向样本数变化")

    vector_digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    counts = {"model_random_queries": 0, "model_directed_cases": 0,
              "model_directed_queries": 0, "fixture_queries": 0}
    directed_case_counts: list[dict] = []
    with destination.open("w", encoding="ascii", newline="\n") as stream:
        for case_index in range(random_count):
            output_channel = rng.selector(output_channels)
            output_y = rng.selector(output_height)
            output_x = rng.selector(output_width)
            source_value = rng.int8()
            source_y = output_y // stride
            source_x = output_x // stride
            source_plane = [0] * (input_height * input_width)
            source_plane[source_y * input_width + source_x] = source_value
            oracle_value = source_plane[source_y * input_width + source_x]
            vector = _query_record(
                0, case_index, 0, base_address, channels, input_height, input_width,
                stride, output_height, output_width, output_channel, output_y,
                output_x, output_channel, source_y, source_x, oracle_value,
                source_plane, tensor_length_bytes,
            )
            _write_vector(stream, vector, vector_digest)
            _update_golden_digest(golden_digest, vector)
            counts["model_random_queries"] += 1

        state_after_random = rng.state
        for directed_case in directed_plan:
            case_index = directed_case["case_index"]
            queries = directed_case["queries"]
            if not queries or directed_case["stride"] != stride:
                raise ValueError("G0 upsample directed case 缺查询或 stride 不匹配")
            coordinates = [tuple(query["source_cyx"]) for query in queries]
            if directed_case["all_queries_share_source_coordinate"] and len(set(coordinates)) != 1:
                raise ValueError("G0 directed case 声明共享来源坐标但查询不同")
            for query_index, query in enumerate(queries):
                output_batch, output_channel, output_y, output_x = query["output_nchw"]
                if output_batch != 0:
                    raise ValueError("G0 upsample directed 查询 batch 必须为 0")
                if query["source_cyx"][0] != output_channel:
                    raise ValueError("G0 directed 来源通道与输出通道不一致")
                source_plane = _make_directed_plane(
                    directed_case, query, channels, input_height, input_width
                )
                source_channel, source_y, source_x = query["source_cyx"]
                expected_value = query["expected_output_int8"]
                if expected_value != query["source_value_int8"]:
                    raise ValueError("G0 directed 复制输出与冻结 marker 值不一致")
                vector = _query_record(
                    1, case_index, query_index, base_address, channels,
                    input_height, input_width, stride, output_height, output_width,
                    output_channel, output_y, output_x, source_channel, source_y,
                    source_x, expected_value, source_plane, tensor_length_bytes,
                )
                _write_vector(stream, vector, vector_digest)
                _update_golden_digest(golden_digest, vector)
                counts["model_directed_queries"] += 1
            counts["model_directed_cases"] += 1
            directed_case_counts.append({
                "case_index": case_index,
                "query_count": len(queries),
                "source_tensor_rule": directed_case["source_tensor_rule"],
            })
        if rng.state != state_after_random:
            raise ValueError("G0 directed vectors 不应消耗 PRNG 状态")

        fixture = plan["separate_unit_fixtures"]["upsample_nearest_repeat"]
        fixture_channels, fixture_height, fixture_width = fixture["input_shape_nchw"][1:]
        fixture_stride = fixture["stride"]
        fixture_input = fixture["input_int8_nchw"][0][0]
        fixture_expected = fixture["expected_output_nchw"][0][0]
        fixture_output_height = len(fixture_expected)
        fixture_output_width = len(fixture_expected[0])
        if (fixture["input_shape_nchw"] != [1, 1, 2, 2] or
                fixture_stride != 2 or len(fixture_input) != 2 or
                any(len(row) != 2 for row in fixture_input) or
                fixture_output_height != 4 or fixture_output_width != 4):
            raise ValueError("G0 2x2 nearest-repeat fixture 规格变化")
        fixture_plane = [value for row in fixture_input for value in row]
        fixture_length = fixture_channels * fixture_height * fixture_width
        for output_y in range(fixture_output_height):
            for output_x in range(fixture_output_width):
                source_y = output_y // fixture_stride
                source_x = output_x // fixture_stride
                expected_value = fixture_expected[output_y][output_x]
                if fixture_plane[source_y * fixture_width + source_x] != expected_value:
                    raise ValueError("G0 nearest-repeat fixture 值与来源位置不一致")
                vector = _query_record(
                    2, output_y * fixture_output_width + output_x, 0,
                    0, fixture_channels, fixture_height, fixture_width,
                    fixture_stride, fixture_output_height, fixture_output_width,
                    0, output_y, output_x, 0, source_y, source_x,
                    expected_value, fixture_plane, fixture_length,
                )
                _write_vector(stream, vector, vector_digest)
                _update_golden_digest(golden_digest, vector)
                counts["fixture_queries"] += 1

    if (counts != {"model_random_queries": 1000, "model_directed_cases": 16,
                   "model_directed_queries": 18, "fixture_queries": 16}):
        raise ValueError(f"G0 upsample 查询数量变化：{counts}")
    if rng.state == state_before_upsample:
        raise ValueError("upsample 随机样本没有推进共享 PRNG")
    vector_sha = _sha256_file(destination)
    golden_sha = golden_digest.hexdigest()
    if vector_sha == golden_sha:
        raise ValueError("向量刺激和输出黄金应分别摘要")
    return {
        "vector_sha256": vector_sha,
        "golden_output_sha256": golden_sha,
        "vector_file_bytes": destination.stat().st_size,
        "counts": counts,
        "directed_cases": directed_case_counts,
        "prng": {
            "seed": _RANDOM_SEED,
            **prng,
            "state_after_random_queries": f"0x{state_after_random:08X}",
            "state_after_upsample": f"0x{rng.state:08X}",
            "random_draw_order": "output_channel selector, output_y selector, output_x selector, then one INT8 source value",
        },
        "fixture_address_semantics": "fixture base_address=0 仅用于验证局部 NCHW byte offset，不表示模型或硬件地址映射",
    }


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float) -> tuple[int, str]:
    """在共享 600 秒截止时间内运行一个 Vivado 批处理阶段。"""
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


def _vivado_diagnostic_lines(output: str) -> list[str]:
    """提取 Vivado 输出中的 warning、error 和 fatal 诊断行。"""
    return [
        line for line in output.splitlines()
        if re.match(r"^\s*(?:WARNING|ERROR|FATAL(?:_ERROR)?)(?:\s*:|\s*\[)", line, re.IGNORECASE)
    ]


def _xsim_gate_failures(output: str, pass_marker: str) -> list[str]:
    """拒绝 XSim 失败标记与 fatal 输出，并要求唯一成功标记。"""
    failures = []
    if "FAIL:" in output:
        failures.append("xsim 输出包含 FAIL:")
    if re.search(r"\$fatal\b|\bFATAL(?:_ERROR)?\s*:", output, re.IGNORECASE):
        failures.append("xsim 输出包含 fatal 错误")
    marker_count = output.count(pass_marker)
    if marker_count != 1:
        failures.append(f"PASS marker 出现 {marker_count} 次，要求恰好一次")
    return failures


def _write_json(path: Path, value: dict) -> None:
    """以 UTF-8 格式写入 JSON 运行记录。"""
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


class TestS2AUpsampleQueryRtl(unittest.TestCase):
    """验证 layer33 nearest-repeat 查询、值复制和地址边界。"""

    def test_vivado_query_against_g0_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(manifest_sha, _MANIFEST_SHA256,
                         "G0 manifest 原始字节 SHA 变化，按停止条件中止")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        evidence_directory = Path(
            os.environ.get(
                "S2A_T05_UPSAMPLE_EVIDENCE_DIR",
                str(repository / "report/evidence/S2A-T05"),
            )
        ).resolve()
        evidence_directory.mkdir(parents=True, exist_ok=True)
        evidence_path = evidence_directory / "upsample_query_simulation.json"
        run_record_path = evidence_directory / "vivado_run_record.json"
        rtl_path = repository / "src/int8_upsample_query.sv"
        bench_path = repository / "sim/tb_s2a_upsample_query.sv"
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
        phase_codes: list[dict] = []
        work = Path(tempfile.mkdtemp(prefix="vivado_", dir=evidence_directory))
        run_started = time.monotonic()
        run_record = {
            "schema_version": "gestureforge_s2a_t05_upsample_vivado_run_v1",
            "result": "RUNNING",
            "repository": str(repository),
            "evidence_directory": str(evidence_directory),
            "work_directory": str(work),
            "manifest_path": str(manifest_path),
            "manifest_sha256": manifest_sha,
            "source_paths": {
                "rtl": str(rtl_path),
                "testbench": str(bench_path),
                "runner": str(script_path),
            },
            "source_hashes": source_hashes_before,
            "phase_records": phase_codes,
        }
        _write_json(run_record_path, run_record)
        try:
            vectors_path = work / "vectors.dat"
            vector_result = _materialize_vectors(manifest, vectors_path)
            self.assertGreater(vector_result["vector_file_bytes"], 0)
            run_record["vector_file"] = str(vectors_path)
            run_record["vector_sha256"] = vector_result["vector_sha256"]
            run_record["vector_file_bytes"] = vector_result["vector_file_bytes"]
            _write_json(run_record_path, run_record)

            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_upsample_query",
                           "-snapshot", "s2a_upsample_query_snapshot"]),
                ("xsim", ["-R", "s2a_upsample_query_snapshot"]),
            ]
            deadline = time.monotonic() + 600.0
            for name, arguments in phases:
                phase_started = time.monotonic()
                log_path = work / f"{name}.log"
                code, output = _run_tool(
                    tools[name], arguments, work, log_path, deadline
                )
                phase_record = {
                    "phase": name,
                    "exit_code": code,
                    "command": [str(tools[name]), *arguments],
                    "launcher": "cmd.exe /d /s /c",
                    "elapsed_seconds": round(time.monotonic() - phase_started, 6),
                    "log_path": str(log_path),
                    "log_sha256": _sha256_file(log_path),
                    "log_bytes": log_path.stat().st_size,
                }
                phase_codes.append(phase_record)
                run_record["phase_records"] = phase_codes
                _write_json(run_record_path, run_record)
                self.assertEqual(code, 0,
                                 f"{name} 退出码 {code}；临时日志尾部：\n{output[-5000:]}")
                diagnostics = _vivado_diagnostic_lines(output)
                self.assertEqual(
                    diagnostics, [],
                    f"{name} 输出包含 Vivado warning/error/fatal：\n" + "\n".join(diagnostics),
                )
                if name == "xsim":
                    pass_marker = (
                        "PASS: queries=1034 model_random=1000 model_directed_cases=16 "
                        "model_directed_queries=18 fixture_queries=16 bad_argument=9 "
                        "bad_range=2 boundary=1"
                    )
                    gate_failures = _xsim_gate_failures(output, pass_marker)
                    self.assertEqual(gate_failures, [], "; ".join(gate_failures))

            self.assertEqual([phase["exit_code"] for phase in phase_codes], [0, 0, 0])
            source_hashes_after = {
                "rtl_sha256": _sha256_file(rtl_path),
                "testbench_sha256": _sha256_file(bench_path),
                "runner_sha256": _sha256_file(script_path),
            }
            self.assertEqual(source_hashes_before, source_hashes_after,
                             "仿真过程中源文件发生变化")
            self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                             "仿真过程中 G0 manifest 原始字节发生变化")

            evidence = {
                "schema_version": "gestureforge_s2a_t05_upsample_query_simulation_v1",
                "result": "PASS",
                "scope": "tiny416 layer33 nearest-repeat 单查询映射、NCHW INT8 byte address 和精确值复制",
                "bindings": {
                    "repository": str(repository),
                    "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                    "manifest_sha256": manifest_sha,
                    **source_hashes_after,
                    "source_paths": {
                        "rtl": str(rtl_path),
                        "testbench": str(bench_path),
                        "runner": str(script_path),
                    },
                    "vector_sha256": vector_result["vector_sha256"],
                    "golden_output_sha256": vector_result["golden_output_sha256"],
                    "input_tensor_producer_layer": 32,
                    "input_base_address": 27598336,
                    "input_tensor_length_bytes": 21632,
                },
                "random_vectors": vector_result["prng"],
                "counts": vector_result["counts"],
                "vector_file_bytes": vector_result["vector_file_bytes"],
                "directed_cases": vector_result["directed_cases"],
                "invalid_assertions": {
                    "BAD_ARGUMENT_code_1": 9,
                    "BAD_RANGE_code_2": 2,
                    "maximum_uint32_boundary_success": 1,
                },
                "vivado": {
                    "bin": str(_XILINX_BIN),
                    "work_directory": str(work),
                    "run_record_path": str(run_record_path),
                    "total_elapsed_seconds": round(time.monotonic() - run_started, 6),
                    "phases": phase_codes,
                    "command_template": "python -B -m unittest verification.test_s2a_upsample_rtl -v",
                },
                "fixture_address_semantics": vector_result["fixture_address_semantics"],
                "limitations": [
                    "仅实现一个查询点和单个通道的紧凑来源平面，不发起 memory bus 事务。",
                    "输入平面最大支持 13x13；实测模型 layer33 13x13 与独立 2x2 stride2 fixture。",
                    "不代表完整 upsample layer engine、整网逐层黄金比对、综合、资源或时序通过。",
                ],
            }
            _write_json(evidence_path, evidence)
            run_record["result"] = "PASS"
            run_record["total_elapsed_seconds"] = round(time.monotonic() - run_started, 6)
            run_record["source_hashes_after"] = source_hashes_after
            _write_json(run_record_path, run_record)
        except Exception as error:
            run_record["result"] = "FAIL"
            run_record["failure"] = f"{type(error).__name__}: {error}"
            run_record["total_elapsed_seconds"] = round(time.monotonic() - run_started, 6)
            _write_json(run_record_path, run_record)
            raise

        print(
            "S2A-T05 manifest_sha256={} vector_sha256={} golden_sha256={} "
            "counts={} prng_before_upsample={} prng_after_upsample={} vivado={}".format(
                manifest_sha,
                vector_result["vector_sha256"],
                vector_result["golden_output_sha256"],
                vector_result["counts"],
                vector_result["prng"]["state_before_upsample"],
                vector_result["prng"]["state_after_upsample"],
                [phase["exit_code"] for phase in phase_codes],
            )
        )


if __name__ == "__main__":
    unittest.main()
