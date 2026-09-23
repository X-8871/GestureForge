"""为阶段 2A 共享 INT8 MAC 生成冻结向量并运行 Vivado xsim 自检。"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")


class XorShift32:
    """按 G0 冻结规则维护全程共享的 xorshift32 状态。"""

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
    """从模型层真实几何计算按 layer_index 排序的 reduction 长度。"""
    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths = []
    for layer in conv_layers:
        input_channels = layer["input_shape_nchw"][1]
        groups = layer["groups"]
        kernel_h, kernel_w = layer["kernel_hw"]
        if input_channels % groups:
            raise ValueError("卷积输入通道不能被 groups 整除")
        lengths.append((input_channels // groups) * kernel_h * kernel_w)
    return lengths


def _advance_conv_random_stream(manifest: dict, rng: XorShift32) -> tuple[int, list[int]]:
    """按冻结卷积随机用例消费选择器与 activation 抽样，随后返回 MAC K 列表。"""
    layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    per_layer = manifest["operator_test_plan"]["random_cases_per_model_layer"]
    lengths = _conv_reduction_lengths(manifest)
    if len(lengths) != 21 or per_layer != 1000:
        raise ValueError("G0 冻结的 tiny416 卷积层数量或随机样本数不匹配")

    for layer, reduction_length in zip(layers, lengths, strict=True):
        output_channels = layer["output_shape_nchw"][1]
        output_height = layer["output_shape_nchw"][2]
        output_width = layer["output_shape_nchw"][3]
        for _ in range(per_layer):
            rng.selector(output_channels)
            rng.selector(output_height)
            rng.selector(output_width)
            for _ in range(reduction_length):
                rng.int8()

    return rng.state, lengths


def _checked_dot(activations: list[int], weights: list[int], bias: int) -> tuple[int, int]:
    """按逐项有符号 INT32 检查计算期望错误码和结果。"""
    accumulator = bias
    for activation, weight in zip(activations, weights, strict=True):
        if activation == -128 or weight == -128:
            return 1, 0
        candidate = accumulator + activation * weight
        if candidate < -0x80000000 or candidate > 0x7FFFFFFF:
            return 7, 0
        accumulator = candidate
    return 0, accumulator


def _write_vector(stream, vector_class: int, case_index: int, k: int,
                  bias: int, error: int, result: int,
                  activations: list[int], weights: list[int]) -> None:
    stream.write(f"{vector_class} {case_index} {k} {bias} {error} {result}\n")
    for activation, weight in zip(activations, weights, strict=True):
        stream.write(f"{activation} {weight}\n")


def _materialize_vectors(manifest: dict, destination: Path) -> tuple[str, int, int]:
    """写入按共享 PRNG 流生成的 1000 个随机与 16 个冻结定向向量。"""
    plan = manifest["operator_test_plan"]
    if plan["shared_primitive_random_cases"] != 1000:
        raise ValueError("冻结 MAC 随机用例数不是 1000")
    directed = plan["directed_case_vectors"]["int8_mac"]
    if len(directed) != 16:
        raise ValueError("冻结 MAC 定向向量数不是 16")

    rng = XorShift32(20260922)
    state_before_mac, lengths = _advance_conv_random_stream(manifest, rng)
    digest = hashlib.sha256()
    vector_count = 0
    total_pairs = 0

    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        class HashingWriter:
            """同步计算临时向量文件的字节摘要。"""

            def write(self, value: str) -> int:
                encoded = value.encode("utf-8")
                digest.update(encoded)
                return stream.write(value)

        output = HashingWriter()
        for case_index in range(plan["shared_primitive_random_cases"]):
            k = lengths[case_index % len(lengths)]
            activations = [rng.int8() for _ in range(k)]
            weights = [rng.int8() for _ in range(k)]
            bias = rng.int32()
            error, result = _checked_dot(activations, weights, bias)
            _write_vector(output, 0, case_index, k, bias, error, result,
                          activations, weights)
            vector_count += 1
            total_pairs += k

        for vector in directed:
            overflow_index = vector["first_int32_overflow_product_index"]
            error = 7 if overflow_index is not None else 0
            result = vector["expected_int32_result"]
            if result is None:
                result = 0
            _write_vector(
                output,
                1,
                vector["case_index"],
                vector["k"],
                vector["bias_int32"],
                error,
                result,
                vector["activation_int8"],
                vector["weight_int8"],
            )
            vector_count += 1
            total_pairs += vector["k"]

    if vector_count != 1016 or rng.state == state_before_mac:
        raise ValueError("MAC 向量数量或共享 PRNG 推进状态异常")
    return digest.hexdigest(), total_pairs, state_before_mac


def _run_tool(tool: Path, arguments: list[str], cwd: Path, log_path: Path) -> tuple[int, str]:
    """在临时目录调用 Vivado 批处理脚本并保留该次调用日志。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
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
        timeout=600,
    )
    output = process.stdout + process.stderr
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return process.returncode, output


class TestS2AMacRtl(unittest.TestCase):
    """验证 MAC RTL、冻结测试向量和握手异常路径。"""

    def test_vivado_simulation_against_frozen_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        self.assertEqual(manifest_sha, _MANIFEST_SHA256, "G0 manifest 字节已变化，需回退规格核对")
        manifest = json.loads(manifest_bytes.decode("utf-8"))

        with tempfile.TemporaryDirectory(prefix="s2a_t02_mac_") as temporary:
            work = Path(temporary)
            vectors = work / "vectors.dat"
            vectors_sha, total_pairs, mac_start_state = _materialize_vectors(manifest, vectors)
            self.assertGreater(vectors.stat().st_size, 0, "规范向量文件不能是空文件")
            self.assertEqual(total_pairs, 987591, "冻结向量点积长度总和变化")

            xvlog = _XILINX_BIN / "xvlog.bat"
            xelab = _XILINX_BIN / "xelab.bat"
            xsim = _XILINX_BIN / "xsim.bat"
            source = repository / "src/int8_mac_accumulator.sv"
            bench = repository / "sim/tb_s2a_int8_mac_accumulator.sv"

            phases = [
                ("xvlog", xvlog, ["-sv", str(source), str(bench)]),
                ("xelab", xelab, ["-top", "tb_s2a_int8_mac_accumulator",
                                  "-snapshot", "s2a_mac_snapshot"]),
                ("xsim", xsim, ["-R", "s2a_mac_snapshot"]),
            ]
            phase_summaries = []
            for name, tool, arguments in phases:
                code, output = _run_tool(tool, arguments, work, work / f"{name}.log")
                phase_summaries.append((name, code))
                self.assertEqual(
                    code,
                    0,
                    f"{name} 退出码 {code}；日志尾部：\n{output[-6000:]}",
                )
                if name == "xsim":
                    self.assertIn("PASS: vectors=1016 random=1000 directed=16", output)

            self.assertEqual([code for _, code in phase_summaries], [0, 0, 0])
            print(
                "S2A-T02 vectors_sha256={} pairs={} shared_prng_state_before_mac=0x{:08X} "
                "vivado_exit_codes={}".format(
                    vectors_sha, total_pairs, mac_start_state, phase_summaries
                )
            )


if __name__ == "__main__":
    unittest.main()
