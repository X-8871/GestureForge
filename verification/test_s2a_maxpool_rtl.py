"""按 G0 冻结清单生成 maxpool 窗口向量并运行 Vivado xsim。"""

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


class XorShift32:
    """维护按 G0 定义的共享 xorshift32 状态。"""

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
            raise ValueError("选择器上界必须为正数")
        return self.next_u32() % bound

    def int8(self) -> int:
        return (self.next_u32() & 0xFF) % 255 - 127

    def int32(self) -> int:
        value = self.next_u32()
        return value if value < 0x80000000 else value - 0x100000000


def _conv_reduction_lengths(manifest: dict) -> list[int]:
    """从模型卷积层规格计算按 layer_index 排列的 reduction 长度。"""
    layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths = []
    for layer in layers:
        input_channels = layer["input_shape_nchw"][1]
        groups = layer["groups"]
        kernel_h, kernel_w = layer["kernel_hw"]
        if input_channels % groups:
            raise ValueError("卷积输入通道不能被 groups 整除")
        lengths.append((input_channels // groups) * kernel_h * kernel_w)
    if len(lengths) != 21:
        raise ValueError("G0 tiny416 卷积层数不再是 21")
    return lengths


def _advance_before_maxpool(manifest: dict, rng: XorShift32) -> list[int]:
    """严格消费 case_order 中 maxpool 之前的随机选择器和数值。"""
    plan = manifest["operator_test_plan"]
    cases_per_layer = plan["random_cases_per_model_layer"]
    if cases_per_layer != 1000 or plan["shared_primitive_random_cases"] != 1000:
        raise ValueError("G0 冻结的随机样本数量发生变化")

    convolution_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    reduction_lengths = _conv_reduction_lengths(manifest)
    for layer, reduction_length in zip(convolution_layers, reduction_lengths, strict=True):
        channels, height, width = layer["output_shape_nchw"][1:]
        for _ in range(cases_per_layer):
            rng.selector(channels)
            rng.selector(height)
            rng.selector(width)
            for _ in range(reduction_length):
                rng.int8()

    for case_index in range(plan["shared_primitive_random_cases"]):
        k = reduction_lengths[case_index % len(reduction_lengths)]
        for _ in range(k):
            rng.int8()
        for _ in range(k):
            rng.int8()
        rng.int32()
    return reduction_lengths


def _write_record(writer, vector_class: int, layer_index: int, case_index: int,
                  count: int, expected_value: int, candidates: list[int]) -> None:
    """输出固定 9 字节槽位的 RTL 仿真记录。"""
    if count not in (4, 9) or len(candidates) != count:
        raise ValueError("maxpool 记录的 tap 数量与冻结规格不一致")
    if any(value < -127 or value > 127 for value in candidates):
        raise ValueError("maxpool 有效候选超出对称 INT8 范围")
    padded = candidates + [0] * (9 - count)
    writer.write(
        "{} {} {} {} 0 {} {}\n".format(
            vector_class, layer_index, case_index, count,
            expected_value, " ".join(str(value) for value in padded)
        )
    )


def _materialize_vectors(manifest: dict, destination: Path) -> dict:
    """生成三层随机/定向向量及通用 padding fixture 的全部输出窗口。"""
    plan = manifest["operator_test_plan"]
    rng = XorShift32(_RANDOM_SEED)
    reduction_lengths = _advance_before_maxpool(manifest, rng)
    prng_state_before_pool = rng.state
    digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    counts = {"random": 0, "directed": 0, "fixture": 0}
    result_ranges = {key: [128, -128] for key in counts}
    layer_counts = []

    class HashingWriter:
        """同步写出 UTF-8/LF 字节并累积稳定摘要。"""

        def __init__(self, stream) -> None:
            self.stream = stream

        def write(self, value: str) -> int:
            encoded = value.encode("utf-8")
            digest.update(encoded)
            self.stream.write(value)
            return len(value)

    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        writer = HashingWriter(stream)
        pool_layers = sorted(
            (layer for layer in manifest["layers"] if layer["op"] == "maxpool"),
            key=lambda layer: layer["layer_index"],
        )
        if [layer["layer_index"] for layer in pool_layers] != [9, 17, 25]:
            raise ValueError("G0 tiny416 maxpool 层索引变化")

        directed_by_layer = plan["directed_case_vectors"]["maxpool"]
        for layer in pool_layers:
            layer_index = layer["layer_index"]
            kernel_h, kernel_w = layer["kernel_hw"]
            tap_count = kernel_h * kernel_w
            if (layer["layout"] != "NCHW" or tap_count != 4 or
                    layer["stride_hw"] != [2, 2] or
                    layer["darknet_padding_parameter"] != 1 or
                    layer["window_origin_yx_at_output_0"] != [0, 0] or
                    layer["padding_lrtb_actual"] != [0, 0, 0, 0] or
                    layer["pad_value_int8"] != -127):
                raise ValueError(f"G0 maxpool layer {layer_index} 几何或 padding 规格变化")
            channels, height, width = layer["output_shape_nchw"][1:]

            for case_index in range(plan["random_cases_per_model_layer"]):
                rng.selector(channels)
                rng.selector(height)
                rng.selector(width)
                candidates = [rng.int8() for _ in range(tap_count)]
                expected = max(candidates)
                record = "0 {} {} {} 0 {} {}\n".format(
                    layer_index, case_index, tap_count, expected,
                    " ".join(str(value) for value in candidates + [0] * (9 - tap_count))
                )
                writer.write(record)
                golden_digest.update(
                    f"0 {layer_index} {case_index} 0 {expected}\n".encode("utf-8")
                )
                counts["random"] += 1
                result_ranges["random"][0] = min(result_ranges["random"][0], expected)
                result_ranges["random"][1] = max(result_ranges["random"][1], expected)

            directed = directed_by_layer[str(layer_index)]
            if len(directed) != plan["directed_cases_per_model_layer"] or len(directed) != 16:
                raise ValueError(f"G0 maxpool layer {layer_index} 定向向量数量变化")
            for vector in directed:
                candidates = vector["candidate_values_int8"]
                expected = vector["expected_output_int8"]
                if vector["case_index"] < 0 or len(candidates) != tap_count:
                    raise ValueError("G0 maxpool 定向候选与模型窗口规格不匹配")
                _write_record(writer, 1, layer_index, vector["case_index"],
                              tap_count, expected, candidates)
                golden_digest.update(
                    f"1 {layer_index} {vector['case_index']} 0 {expected}\n".encode("utf-8")
                )
                counts["directed"] += 1
                result_ranges["directed"][0] = min(result_ranges["directed"][0], expected)
                result_ranges["directed"][1] = max(result_ranges["directed"][1], expected)

            layer_counts.append({"layer_index": layer_index, "random": 1000,
                                 "directed": 16, "total": 1016})

        fixture = plan["separate_unit_fixtures"]["maxpool_darknet_padding"]
        image = fixture["input_int8_nchw"][0][0]
        expected_image = fixture["expected_output_nchw"][0][0]
        kernel_h, kernel_w = fixture["kernel_hw"]
        stride_h, stride_w = fixture["stride_hw"]
        origin_y, origin_x = fixture["window_origin_yx_at_output_0"]
        pad_value = fixture["pad_value_int8"]
        if (fixture["input_shape_nchw"] != [1, 1, 4, 4] or
                [kernel_h, kernel_w] != [3, 3] or
                [stride_h, stride_w] != [1, 1] or
                fixture["padding_lrtb_actual"] != [1, 1, 1, 1] or
                pad_value != -127 or origin_y != -1 or origin_x != -1):
            raise ValueError("G0 maxpool 通用 padding fixture 规格变化")
        output_h = len(expected_image)
        output_w = len(expected_image[0])
        for output_y in range(output_h):
            for output_x in range(output_w):
                candidates = []
                for kernel_y in range(kernel_h):
                    for kernel_x in range(kernel_w):
                        input_y = origin_y + output_y * stride_h + kernel_y
                        input_x = origin_x + output_x * stride_w + kernel_x
                        if 0 <= input_y < len(image) and 0 <= input_x < len(image[0]):
                            candidates.append(image[input_y][input_x])
                        else:
                            candidates.append(pad_value)
                expected = expected_image[output_y][output_x]
                case_index = output_y * output_w + output_x
                _write_record(writer, 2, -1, case_index, 9, expected, candidates)
                golden_digest.update(
                    f"2 -1 {case_index} 0 {expected}\n".encode("utf-8")
                )
                counts["fixture"] += 1
                result_ranges["fixture"][0] = min(result_ranges["fixture"][0], expected)
                result_ranges["fixture"][1] = max(result_ranges["fixture"][1], expected)

    if counts != {"random": 3000, "directed": 48, "fixture": 16}:
        raise ValueError(f"规范向量数量错误：{counts}")
    if destination.stat().st_size == 0:
        raise ValueError("规范向量文件为空")
    return {
        "vector_sha256": digest.hexdigest(),
        "golden_output_sha256": golden_digest.hexdigest(),
        "vector_bytes": destination.stat().st_size,
        "counts": counts,
        "layer_counts": layer_counts,
        "prng_state_before_pool": f"0x{prng_state_before_pool:08X}",
        "prng_state_after_pool": f"0x{rng.state:08X}",
        "result_ranges": {
            name: {"minimum": bounds[0], "maximum": bounds[1]}
            for name, bounds in result_ranges.items()
        },
    }


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float) -> tuple[int, str]:
    """在共享 600 秒截止时间内运行一个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Vivado 仿真总耗时达到 600 秒停止条件")
    command = " ".join(f'"{argument}"' if " " in argument else argument
                       for argument in [str(tool), *arguments])
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


def _sha256(path: Path) -> str:
    """计算指定文件的原始字节 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestS2AMaxpoolRtl(unittest.TestCase):
    """验证 maxpool RTL 与阶段 2A G0 冻结整数向量。"""

    def test_vivado_simulation_against_frozen_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        self.assertEqual(manifest_sha256, _MANIFEST_SHA256,
                         "G0 manifest 原始字节发生变化，停止并重新核对规格")
        manifest = json.loads(manifest_bytes.decode("utf-8"))

        with tempfile.TemporaryDirectory(prefix="s2a_t03_maxpool_") as temporary:
            work = Path(temporary)
            vectors = work / "vectors.dat"
            vector_summary = _materialize_vectors(manifest, vectors)
            self.assertEqual(vector_summary["vector_bytes"], vectors.stat().st_size)
            rtl = repository / "src/int8_maxpool_window.sv"
            testbench = repository / "sim/tb_s2a_maxpool_window.sv"
            self.assertTrue(rtl.is_file(), "缺少 maxpool RTL")
            self.assertTrue(testbench.is_file(), "缺少 maxpool 仿真 testbench")

            tools = {
                "xvlog": _XILINX_BIN / "xvlog.bat",
                "xelab": _XILINX_BIN / "xelab.bat",
                "xsim": _XILINX_BIN / "xsim.bat",
            }
            phases = [
                ("xvlog", ["-sv", str(rtl), str(testbench)]),
                ("xelab", ["-top", "tb_s2a_maxpool_window",
                           "-snapshot", "s2a_maxpool_snapshot"]),
                ("xsim", ["-R", "s2a_maxpool_snapshot"]),
            ]
            deadline = time.monotonic() + 600
            exit_codes = {}
            simulation_output = ""
            for name, arguments in phases:
                code, output = _run_tool(
                    tools[name], arguments, work, work / f"{name}.log", deadline
                )
                exit_codes[name] = code
                self.assertEqual(code, 0,
                                 f"{name} 退出码 {code}；日志尾部：\n{output[-6000:]}")
                if name == "xsim":
                    simulation_output = output
            expected_summary = (
                "PASS: model_vectors=3048 random=3000 directed=48 "
                "fixture=16 invalid=4 mismatches=0"
            )
            self.assertIn(expected_summary, simulation_output)

            evidence = {
                "schema_version": "s2a-t03-maxpool-window-simulation-v1",
                "status": "PASS",
                "scope": "tiny416 maxpool 单窗口 4-tap/9-tap 有符号 INT8 最大值归约",
                "bindings": {
                    "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                    "manifest_sha256": manifest_sha256,
                    "rtl_path": "src/int8_maxpool_window.sv",
                    "rtl_sha256": _sha256(rtl),
                    "testbench_path": "sim/tb_s2a_maxpool_window.sv",
                    "testbench_sha256": _sha256(testbench),
                    "test_script_path": "verification/test_s2a_maxpool_rtl.py",
                    "test_script_sha256": _sha256(Path(__file__).resolve()),
                    "random_seed": _RANDOM_SEED,
                    "shared_prng_state_before_pool": vector_summary["prng_state_before_pool"],
                    "shared_prng_state_after_pool": vector_summary["prng_state_after_pool"],
                    "materialized_vector_sha256": vector_summary["vector_sha256"],
                    "golden_output_sha256": vector_summary["golden_output_sha256"],
                    "materialized_vector_bytes": vector_summary["vector_bytes"],
                },
                "counts": {
                    "model_layers": vector_summary["layer_counts"],
                    "model_random": vector_summary["counts"]["random"],
                    "model_directed": vector_summary["counts"]["directed"],
                    "model_comparisons": 3048,
                    "padding_fixture": {
                        "name": "maxpool_darknet_padding",
                        "windows": vector_summary["counts"]["fixture"],
                        "taps_per_window": 9,
                        "pad_value_int8": -127,
                    },
                    "invalid_assertions": [
                        "BAD_ARGUMENT(1): candidate_count=0",
                        "BAD_ARGUMENT(1): candidate_count=5",
                        "BAD_ARGUMENT(1): candidate_count=10",
                        "BAD_ARGUMENT(1): selected candidate=-128 with candidate_count=4",
                    ],
                    "invalid_assertion_count": 4,
                    "error_code_semantics": {"success": 0, "BAD_ARGUMENT": 1},
                    "unselected_minus_128_ignored": True,
                    "all_rtl_comparisons": 3064,
                },
                "result_statistics": {
                    "mismatches": 0,
                    "golden_ranges": vector_summary["result_ranges"],
                    "comparison": "有符号整数逐字节完全相等",
                },
                "vivado": {
                    "tool_directory": str(_XILINX_BIN),
                    "exit_codes": exit_codes,
                    "xsim_pass_summary": expected_summary,
                    "total_timeout_seconds": 600,
                },
                "limitations": [
                    "仅实现单窗口候选最大值归约，不含 layer window geometry、坐标生成或访存地址引擎。",
                    "通用 padding fixture 将冻结坐标几何生成的 16 个 tap 组送入 RTL；只验证候选归约与 -127 padding 映射。",
                    "未验证完整 maxpool layer、整网 RTL、逐层张量比对、综合资源或板上行为。",
                ],
            }
            evidence_path = repository / "report/evidence/S2A-T03/maxpool_window_simulation.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(
                json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            evidence_bytes = evidence_path.read_bytes()
            self.assertFalse(evidence_bytes.startswith(b"\xef\xbb\xbf"),
                             "证据 JSON 不能带 UTF-8 BOM")
            self.assertNotIn(b"\r", evidence_bytes, "证据 JSON 必须使用 LF")
            self.assertEqual(hashlib.sha256(evidence_bytes).hexdigest(),
                             _sha256(evidence_path))
            print(
                "S2A-T03 manifest_sha256={} vector_sha256={} golden_sha256={} "
                "vivado_exit_codes={}".format(
                    manifest_sha256,
                    vector_summary["vector_sha256"],
                    vector_summary["golden_output_sha256"],
                    exit_codes,
                )
            )


if __name__ == "__main__":
    unittest.main()
