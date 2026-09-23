"""按 G0 冻结清单和共享 PRNG 验证 tiny416 YOLO 视图查询 RTL。"""

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
_T05_EVIDENCE_SHA256 = "0b3f8919c0c25a267e359e452ab2c3e71a4e04cd454be20ecfb82764256c678e"
_T06_EVIDENCE_SHA256 = "9237d06d387209281789ab966b4e0e987b9f07a87c7103e7e112de62d3d7632a"
_T05_STATE_AFTER_UPSAMPLE = 0xD3804965
_STATE_AFTER_ROUTE = 0x0BE74782
_EXPECTED_HEAD_STATES = {30: 0xEB32F146, 37: 0xAA476160}
_RANDOM_SEED = 20260922
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_FIELD_COUNT = 29


class XorShift32:
    """实现 G0 规定的共享 xorshift32 流。"""

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
            raise ValueError("G0 选择器上界必须为正数")
        return self.next_u32() % bound


def _sha256_bytes(data: bytes) -> str:
    """计算原始字节的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _hex_state(value: object, field: str) -> int:
    """校验并解析证据中的 32-bit 十六进制状态。"""
    if not isinstance(value, str) or len(value) != 10 or not value.startswith("0x"):
        raise ValueError(f"{field} 不是单前缀 32-bit 状态")
    parsed = int(value[2:], 16)
    if not 0 <= parsed <= 0xFFFFFFFF:
        raise ValueError(f"{field} 超出 32-bit 范围")
    return parsed


def _head_descriptors(manifest: dict) -> list[dict]:
    """从 manifest 绑定 YOLO 头与真实卷积来源描述符。"""
    layers = manifest["layers"]
    conv_by_layer = {
        layer["layer_index"]: layer
        for layer in layers
        if layer.get("op") == "convolutional"
    }
    heads = sorted(
        (layer for layer in layers if layer.get("op") == "yolo"),
        key=lambda layer: layer["layer_index"],
    )
    if [head["layer_index"] for head in heads] != [30, 37]:
        raise ValueError("G0 tiny416 YOLO 头层顺序或数量发生变化")

    descriptors = []
    for head in heads:
        if (head.get("layout") != "NCHW" or
                head.get("element_type") != "int8_twos_complement" or
                len(head.get("input_tensor_indices", [])) != 1):
            raise ValueError("YOLO head layout、元素类型或来源数量不符合 G0")
        source_tensor_index = head["input_tensor_indices"][0]
        source = conv_by_layer.get(source_tensor_index)
        if source is None:
            raise ValueError("YOLO 头来源未绑定到卷积输出 tensor")
        shape = head["input_shape_nchw"]
        if (shape != head["output_shape_nchw"] or
                shape != source["output_shape_nchw"] or
                source.get("layout") != "NCHW" or
                source.get("element_type") != "int8_twos_complement"):
            raise ValueError("YOLO 头与来源卷积的 NCHW 描述不一致")
        if (head["output_tensor_index"] != source_tensor_index or
                source["layer_index"] != source_tensor_index or
                source["layer_index"] >= head["layer_index"]):
            raise ValueError("YOLO 头 tensor index 或生产层链接不符合零拷贝 view")
        if (head["tensor_address"] != source["tensor_address"] or
                head["tensor_length_bytes"] != source["tensor_length_bytes"] or
                head["input_scale"] != source["output_scale"] or
                head["head_logit_scale"] != source["output_scale"]):
            raise ValueError("YOLO 头未与来源卷积共用地址、长度或 scale")

        batch, channels, height, width = shape
        anchor_count = len(head["mask"])
        entries_per_anchor = head["classes"] + 5
        if (batch != 1 or anchor_count <= 0 or entries_per_anchor <= 0 or
                channels != anchor_count * entries_per_anchor or
                head["tensor_length_bytes"] != channels * height * width):
            raise ValueError("YOLO 头 NCHW 长度或 anchor/entry 通道规格不符合 G0")
        if not (0 <= head["tensor_address"] <= 0xFFFFFFFF):
            raise ValueError("YOLO logical base address 超出 uint32")
        if head["tensor_address"] + head["tensor_length_bytes"] > 0x100000000:
            raise ValueError("冻结 YOLO tensor 超出 uint32 地址空间")

        descriptors.append({
            "head_layer_index": head["layer_index"],
            "head_input_tensor_index": source_tensor_index,
            "head_output_tensor_index": head["output_tensor_index"],
            "source_layer_index": source["layer_index"],
            "source_tensor_index": source["layer_index"],
            "source_is_convolution": 1,
            "head_base_address": head["tensor_address"],
            "head_length_bytes": head["tensor_length_bytes"],
            "head_channels": channels,
            "head_height": height,
            "head_width": width,
            "source_base_address": source["tensor_address"],
            "source_length_bytes": source["tensor_length_bytes"],
            "source_channels": source["output_shape_nchw"][1],
            "source_height": source["output_shape_nchw"][2],
            "source_width": source["output_shape_nchw"][3],
            "anchor_count": anchor_count,
            "entries_per_anchor": entries_per_anchor,
            "mask": list(head["mask"]),
            "classes": head["classes"],
            "output_scale": head["output_scale"],
        })
    return descriptors


def _descriptor_fields(descriptor: dict) -> list[int]:
    """将冻结 descriptor 按 testbench 端口顺序展开。"""
    return [
        descriptor["head_layer_index"],
        descriptor["head_input_tensor_index"],
        descriptor["head_output_tensor_index"],
        descriptor["source_layer_index"],
        descriptor["source_tensor_index"],
        descriptor["source_is_convolution"],
        descriptor["head_base_address"],
        descriptor["head_length_bytes"],
        descriptor["head_channels"],
        descriptor["head_height"],
        descriptor["head_width"],
        descriptor["source_base_address"],
        descriptor["source_length_bytes"],
        descriptor["source_channels"],
        descriptor["source_height"],
        descriptor["source_width"],
        descriptor["anchor_count"],
        descriptor["entries_per_anchor"],
    ]


def _oracle(descriptor: dict, query: dict) -> tuple[int, int, int, int, int, int]:
    """按独立 NCHW flatten 规则计算通道、偏移和别名地址。"""
    channel_index = (query["anchor_local"] * descriptor["entries_per_anchor"] +
                     query["entry"])
    plane_size = descriptor["head_height"] * descriptor["head_width"]
    flat_index = channel_index * plane_size + query["row"] * descriptor["head_width"] + query["column"]
    return (
        channel_index,
        flat_index,
        descriptor["head_base_address"] + flat_index,
        descriptor["source_base_address"] + flat_index,
        1,
        0,
    )


def _record(vector_class: int, descriptor: dict, query: dict,
            expected: tuple[int, int, int, int, int, int] | None = None) -> list[int]:
    """生成由 TB 驱动的完整 descriptor、query 和期望输出行。"""
    if expected is None:
        expected = _oracle(descriptor, query)
    fields = [vector_class, *_descriptor_fields(descriptor),
              query["anchor_local"], query["entry"], query["row"], query["column"],
              *expected]
    if len(fields) != _FIELD_COUNT or any(not 0 <= value <= 0xFFFFFFFF for value in fields):
        raise ValueError("向量字段数量或 uint32 范围错误")
    return fields


def _emit(stream, fields: list[int], vector_digest, stimulus_digest,
          golden_digest) -> None:
    """写入稳定十六进制向量并分别摘要输入和黄金输出。"""
    packed = struct.pack("<29I", *fields)
    stream.write(" ".join(f"{value:08X}" for value in fields) + "\n")
    vector_digest.update(packed)
    stimulus_digest.update(struct.pack("<23I", *fields[:23]))
    golden_digest.update(struct.pack("<6I", *fields[23:]))


def _state_trace(manifest: dict, t05: dict, t06: dict) -> tuple[XorShift32, dict]:
    """核验 T05/T06 连续状态后建立 YOLO 查询随机流。"""
    plan = manifest["operator_test_plan"]
    if (plan.get("random_cases_per_model_layer") != 1000 or
            plan.get("directed_cases_per_model_layer") != 16 or
            "random case_index 0..999 then directed case_index 0..15" not in plan.get("case_order", "") or
            plan.get("yolo") != (
                "1000 address-view queries per cfg YOLO layer; consume anchor_local,entry,row,col selectors in that order and verify byte address aliases source convolution NCHW offset"
            )):
        raise ValueError("G0 YOLO 样本数、层顺序或 selector 消耗规则变化")
    t05_random = t05["random_vectors"]
    t06_random = t06["randomness"]
    state_after_route = _hex_state(t06_random["state_after_route"], "T06 state_after_route")
    state_before_upsample = _hex_state(t05_random["state_before_upsample"], "T05 state_before_upsample")
    t05_route_state = _hex_state(t05_random["state_after_route"], "T05 state_after_route")
    state_after_upsample = _hex_state(t05_random["state_after_upsample"], "T05 state_after_upsample")
    if not (state_after_route == state_before_upsample == t05_route_state == _STATE_AFTER_ROUTE):
        raise ValueError("T05/T06 route-to-upsample PRNG checkpoint differs")
    if state_after_upsample != _T05_STATE_AFTER_UPSAMPLE:
        raise ValueError("T05 random query endpoint differs from frozen continuation")
    if _hex_state(t05_random["seed"].__str__() if isinstance(t05_random["seed"], str)
                  else f"0x{int(t05_random['seed']):08X}", "T05 seed") != _RANDOM_SEED:
        raise ValueError("T05 shared PRNG seed differs from G0")
    if int(plan["prng"].split("state starts ", 1)[1].split(";", 1)[0]) != _RANDOM_SEED:
        raise ValueError("G0 shared PRNG seed differs")

    return XorShift32(state_after_upsample), {
        "seed": _RANDOM_SEED,
        "state_after_route": f"0x{state_after_route:08X}",
        "state_before_upsample": f"0x{state_before_upsample:08X}",
        "state_before_yolo": f"0x{state_after_upsample:08X}",
        "draw_order": "随机 head 按 layer_index 升序；每个查询依次消耗 anchor_local、entry、row、column 四个 selector；directed case 不消耗状态",
    }


def _materialize_vectors(manifest: dict, t05: dict, t06: dict,
                         destination: Path) -> dict:
    """生成两头随机、G0 directed、非法参数及地址边界向量。"""
    descriptors = _head_descriptors(manifest)
    rng, randomness = _state_trace(manifest, t05, t06)
    vector_digest = hashlib.sha256()
    stimulus_digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    plan = manifest["operator_test_plan"]
    directed_by_layer = plan["directed_case_vectors"]["yolo"]
    counts = {
        "model_random_queries": 0,
        "model_directed_cases": 0,
        "model_directed_queries": 0,
        "BAD_ARGUMENT": 0,
        "BAD_RANGE": 0,
        "maximum_uint32_boundary_success": 0,
    }
    layer_states = []
    directed_cases = []

    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        for descriptor in descriptors:
            layer_index = descriptor["head_layer_index"]
            height = descriptor["head_height"]
            width = descriptor["head_width"]
            state_before = rng.state
            for _ in range(1000):
                query = {
                    "anchor_local": rng.selector(descriptor["anchor_count"]),
                    "entry": rng.selector(descriptor["entries_per_anchor"]),
                    "row": rng.selector(height),
                    "column": rng.selector(width),
                }
                _emit(stream, _record(0, descriptor, query), vector_digest,
                      stimulus_digest, golden_digest)
                counts["model_random_queries"] += 1
            state_after_random = rng.state
            if (layer_index in _EXPECTED_HEAD_STATES and
                    state_after_random != _EXPECTED_HEAD_STATES[layer_index]):
                raise ValueError(f"YOLO layer {layer_index} PRNG endpoint mismatch")

            cases = directed_by_layer.get(str(layer_index))
            if not isinstance(cases, list) or len(cases) != 16:
                raise ValueError(f"G0 YOLO layer {layer_index} directed case count changed")
            directed_query_count = 0
            for expected_case_index, case in enumerate(cases):
                if case.get("case_index") != expected_case_index:
                    raise ValueError("G0 directed case_index 顺序变化")
                if (case.get("source_convolution_layer_index") != descriptor["source_layer_index"] or
                        case.get("tensor_shape_nchw") !=
                        [1, descriptor["head_channels"], height, width] or
                        case.get("head_base_address") != descriptor["head_base_address"] or
                        case.get("source_convolution_base_address") != descriptor["source_base_address"] or
                        case.get("zero_copy_alias") is not True):
                    raise ValueError("G0 YOLO directed case descriptor 与实际 manifest 不一致")
                queries = case.get("queries")
                if not isinstance(queries, list) or not queries:
                    raise ValueError("G0 YOLO directed case 缺少查询")
                for frozen in queries:
                    query = {
                        "anchor_local": frozen["anchor_local"],
                        "entry": frozen["entry"],
                        "row": frozen["row"],
                        "column": frozen["column"],
                    }
                    expected = (
                        frozen["channel"],
                        frozen["tensor_byte_offset"],
                        frozen["tensor_byte_address"],
                        frozen["source_tensor_byte_address"],
                        1,
                        0,
                    )
                    if _oracle(descriptor, query) != expected:
                        raise ValueError("G0 directed query 与独立 NCHW oracle 不一致")
                    _emit(stream, _record(1, descriptor, query, expected), vector_digest,
                          stimulus_digest, golden_digest)
                    directed_query_count += 1
                if case.get("contiguous_channel_boundary"):
                    if (len(queries) != 2 or
                            queries[1]["channel"] != queries[0]["channel"] + 1):
                        raise ValueError("G0 contiguous channel boundary vector changed")
                if case.get("tail_byte_query") and any(
                        query["tensor_byte_offset"] != descriptor["head_length_bytes"] - 1
                        for query in queries):
                    raise ValueError("G0 tail byte vector does not address final tensor byte")
                directed_cases.append({
                    "layer_index": layer_index,
                    "case_index": expected_case_index,
                    "query_count": len(queries),
                })
                counts["model_directed_cases"] += 1
                counts["model_directed_queries"] += len(queries)

            if rng.state != state_after_random:
                raise ValueError("G0 directed YOLO cases unexpectedly consumed PRNG state")
            layer_states.append({
                "layer_index": layer_index,
                "state_before_random": f"0x{state_before:08X}",
                "state_after_random": f"0x{state_after_random:08X}",
                "random_queries": 1000,
                "directed_cases": len(cases),
                "directed_queries": directed_query_count,
            })

        base_descriptor = descriptors[0]
        last_query = {
            "anchor_local": base_descriptor["anchor_count"] - 1,
            "entry": base_descriptor["entries_per_anchor"] - 1,
            "row": base_descriptor["head_height"] - 1,
            "column": base_descriptor["head_width"] - 1,
        }
        length = base_descriptor["head_length_bytes"]
        boundary_descriptor = dict(base_descriptor)
        boundary_descriptor["head_base_address"] = 0x100000000 - length
        boundary_descriptor["source_base_address"] = 0x100000000 - length
        _emit(stream, _record(4, boundary_descriptor, last_query), vector_digest,
              stimulus_digest, golden_digest)
        counts["maximum_uint32_boundary_success"] += 1

        overflow_descriptor = dict(base_descriptor)
        overflow_descriptor["head_base_address"] = 0xFFFFFFFF
        overflow_descriptor["source_base_address"] = 0xFFFFFFFF
        _emit(stream, _record(3, overflow_descriptor, {"anchor_local": 0,
              "entry": 0, "row": 0, "column": 0}, (0, 0, 0, 0, 0, 2)),
              vector_digest, stimulus_digest, golden_digest)
        counts["BAD_RANGE"] += 1

        short_descriptor = dict(base_descriptor)
        short_descriptor["head_length_bytes"] = length - 1
        short_descriptor["source_length_bytes"] = length - 1
        _emit(stream, _record(3, short_descriptor, {"anchor_local": 0,
              "entry": 0, "row": 0, "column": 0}, (0, 0, 0, 0, 0, 2)),
              vector_digest, stimulus_digest, golden_digest)
        counts["BAD_RANGE"] += 1

        invalid_cases = []
        for query in (
                {"anchor_local": base_descriptor["anchor_count"], "entry": 0, "row": 0, "column": 0},
                {"anchor_local": 0, "entry": base_descriptor["entries_per_anchor"], "row": 0, "column": 0},
                {"anchor_local": 0, "entry": 0, "row": base_descriptor["head_height"], "column": 0},
                {"anchor_local": 0, "entry": 0, "row": 0, "column": base_descriptor["head_width"]},
        ):
            invalid_cases.append((base_descriptor, query))

        descriptor_mutations = []
        mutated = dict(base_descriptor)
        mutated["head_output_tensor_index"] += 1
        descriptor_mutations.append(mutated)
        mutated = dict(base_descriptor)
        mutated["source_layer_index"] = mutated["head_layer_index"]
        descriptor_mutations.append(mutated)
        mutated = dict(base_descriptor)
        mutated["source_is_convolution"] = 0
        descriptor_mutations.append(mutated)
        mutated = dict(base_descriptor)
        mutated["head_base_address"] += 1
        descriptor_mutations.append(mutated)
        mutated = dict(base_descriptor)
        mutated["head_channels"] += 1
        descriptor_mutations.append(mutated)
        mutated = dict(base_descriptor)
        mutated["head_height"] = 0
        mutated["source_height"] = 0
        descriptor_mutations.append(mutated)
        for descriptor in descriptor_mutations:
            invalid_cases.append((descriptor, {"anchor_local": 0, "entry": 0,
                               "row": 0, "column": 0}))

        identity_mismatch_cases = 0
        for descriptor in descriptors:
            wrong_tensor_index = descriptor["source_tensor_index"] - 1
            wrong_identity = dict(descriptor)
            wrong_identity["head_input_tensor_index"] = wrong_tensor_index
            wrong_identity["head_output_tensor_index"] = wrong_tensor_index
            wrong_identity["source_tensor_index"] = wrong_tensor_index
            if (wrong_identity["source_layer_index"] != descriptor["source_layer_index"] or
                    wrong_identity["head_base_address"] != descriptor["head_base_address"] or
                    wrong_identity["head_length_bytes"] != descriptor["head_length_bytes"] or
                    wrong_identity["head_channels"] != descriptor["head_channels"] or
                    wrong_identity["head_height"] != descriptor["head_height"] or
                    wrong_identity["head_width"] != descriptor["head_width"]):
                raise ValueError("身份链负向用例必须保留合法 producer、shape 与地址")
            invalid_cases.append((wrong_identity, {"anchor_local": 0, "entry": 0,
                               "row": 0, "column": 0}))
            identity_mismatch_cases += 1

        non_immediate = dict(descriptors[0])
        non_immediate["head_input_tensor_index"] = 28
        non_immediate["head_output_tensor_index"] = 28
        non_immediate["source_tensor_index"] = 28
        non_immediate["source_layer_index"] = 28
        if (non_immediate["head_layer_index"] != 30 or
                non_immediate["source_layer_index"] != non_immediate["source_tensor_index"] or
                non_immediate["source_layer_index"] + 1 == non_immediate["head_layer_index"] or
                non_immediate["source_is_convolution"] != 1 or
                non_immediate["head_base_address"] != descriptors[0]["head_base_address"] or
                non_immediate["head_length_bytes"] != descriptors[0]["head_length_bytes"] or
                non_immediate["head_channels"] != descriptors[0]["head_channels"] or
                non_immediate["head_height"] != descriptors[0]["head_height"] or
                non_immediate["head_width"] != descriptors[0]["head_width"]):
            raise ValueError("直接前驱 guard 向量必须只违反 producer adjacency")
        invalid_cases.append((non_immediate, {"anchor_local": 0, "entry": 0,
                           "row": 0, "column": 0}))

        for descriptor, query in invalid_cases:
            _emit(stream, _record(2, descriptor, query, (0, 0, 0, 0, 0, 1)),
                  vector_digest, stimulus_digest, golden_digest)
            counts["BAD_ARGUMENT"] += 1

    if counts != {
        "model_random_queries": 2000,
        "model_directed_cases": 32,
        "model_directed_queries": 34,
        "BAD_ARGUMENT": 13,
        "BAD_RANGE": 2,
        "maximum_uint32_boundary_success": 1,
    }:
        raise ValueError(f"T08 向量数量变化：{counts}")
    if identity_mismatch_cases != 2:
        raise ValueError("必须分别覆盖两个 YOLO head 的 producer/tensor 身份错误")
    if [item["state_after_random"] for item in layer_states] != [
            "0xEB32F146", "0xAA476160"]:
        raise ValueError("T08 逐层 PRNG 状态链不匹配")

    randomness.update({
        "state_after_random_queries": f"0x{rng.state:08X}",
        "per_head": layer_states,
    })
    if rng.state != _EXPECTED_HEAD_STATES[37]:
        raise ValueError("YOLO 随机查询最终 PRNG 状态错误")
    return {
        "vector_sha256": _sha256_file(destination),
        "stimulus_vector_sha256": stimulus_digest.hexdigest(),
        "golden_output_sha256": golden_digest.hexdigest(),
        "vector_file_bytes": destination.stat().st_size,
        "counts": counts,
        "identity_mismatch_cases": identity_mismatch_cases,
        "non_immediate_producer_cases": 1,
        "directed_cases": directed_cases,
        "randomness": randomness,
        "descriptors": [
            {key: descriptor[key] for key in (
                "head_layer_index", "head_input_tensor_index", "head_output_tensor_index",
                "source_layer_index", "source_tensor_index", "head_base_address",
                "head_length_bytes", "head_channels", "head_height", "head_width",
                "anchor_count", "entries_per_anchor", "mask", "classes", "output_scale")}
            for descriptor in descriptors
        ],
    }


def _assert_temporary_cwd(cwd: Path, repository: Path) -> None:
    """确保 Vivado 当前目录严格位于系统临时目录内。"""
    temp_root = Path(tempfile.gettempdir()).resolve()
    resolved = cwd.resolve()
    if (not resolved.is_dir() or resolved == repository or
            os.path.commonpath([str(temp_root), str(resolved)]) != str(temp_root) or
            repository in resolved.parents):
        raise RuntimeError(f"拒绝在非系统临时目录运行 Vivado：{resolved}")


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float, repository: Path) -> tuple[int, str]:
    """在系统临时目录中运行单个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    _assert_temporary_cwd(cwd, repository)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("S2A-T08 Vivado 总运行时间超过 600 秒停止条件")
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


class TestS2AYoloViewQueryRtl(unittest.TestCase):
    """验证两组 YOLO head 的 NCHW 零拷贝地址视图。"""

    def test_vivado_query_against_g0_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        g0_doc_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
        d2_doc_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md"
        t05_path = repository / "report/evidence/S2A-T05/upsample_query_simulation.json"
        t06_path = repository / "report/evidence/S2A-T06/route_query_simulation.json"
        rtl_path = repository / "src/int8_yolo_view_query.sv"
        bench_path = repository / "sim/tb_s2a_yolo_view_query.sv"
        script_path = Path(__file__).resolve()
        for required in (manifest_path, g0_doc_path, d2_doc_path, t05_path,
                         t06_path, rtl_path, bench_path, script_path):
            self.assertTrue(required.is_file(), f"缺少绑定输入或测试源文件：{required}")

        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(manifest_sha, _MANIFEST_SHA256,
                         "G0 manifest 原始 SHA 变化，按任务停止条件中止")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        t05_bytes = t05_path.read_bytes()
        t06_bytes = t06_path.read_bytes()
        t05_sha = _sha256_bytes(t05_bytes)
        t06_sha = _sha256_bytes(t06_bytes)
        self.assertEqual(t05_sha, _T05_EVIDENCE_SHA256,
                         "T05 冻结 evidence SHA 变化")
        self.assertEqual(t06_sha, _T06_EVIDENCE_SHA256,
                         "T06 冻结 evidence SHA 变化")
        t05 = json.loads(t05_bytes.decode("utf-8"))
        t06 = json.loads(t06_bytes.decode("utf-8"))
        self.assertEqual(t05.get("result"), "PASS")
        self.assertEqual(t06.get("result"), "PASS")
        self.assertEqual(t05.get("bindings", {}).get("manifest_sha256"), _MANIFEST_SHA256)
        self.assertEqual(t06.get("bindings", {}).get("manifest_sha256"), _MANIFEST_SHA256)

        tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"未找到 Vivado 工具：{tool}")
        source_hashes_before = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        phase_codes = []
        with tempfile.TemporaryDirectory(prefix="s2a_t08_yolo_view_") as temporary:
            work = Path(temporary).resolve()
            _assert_temporary_cwd(work, repository)
            vector_path = work / "vectors.dat"
            vector_result = _materialize_vectors(manifest, t05, t06, vector_path)
            self.assertGreater(vector_result["vector_file_bytes"], 0)

            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_yolo_view_query",
                           "-snapshot", "s2a_yolo_view_query_snapshot"]),
                ("xsim", ["-R", "s2a_yolo_view_query_snapshot"]),
            ]
            deadline = time.monotonic() + 600.0
            for name, arguments in phases:
                code, output = _run_tool(
                    tools[name], arguments, work, work / f"{name}.log", deadline, repository
                )
                phase_codes.append({"phase": name, "exit_code": code})
                self.assertEqual(code, 0,
                                 f"{name} 退出码 {code}；临时日志尾部：\n{output[-5000:]}")
                if name == "xsim":
                    self.assertIn(
                        "PASS: total=2050 random=2000 directed_cases=32 directed_queries=34 bad_argument=13 bad_range=2 boundary=1",
                        output,
                    )

        self.assertEqual([phase["exit_code"] for phase in phase_codes], [0, 0, 0])
        source_hashes_after = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真期间测试源文件发生变化")
        self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                         "仿真期间 G0 manifest 原始 SHA 发生变化")
        self.assertEqual(_sha256_file(t05_path), _T05_EVIDENCE_SHA256)
        self.assertEqual(_sha256_file(t06_path), _T06_EVIDENCE_SHA256)

        evidence = {
            "schema_version": "gestureforge_s2a_t08_yolo_view_query_simulation_v1",
            "result": "PASS",
            "scope": "tiny416 两个 YOLO head 的 NCHW INT8 零拷贝单元素视图查询",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": manifest_sha,
                "g0_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
                "g0_spec_sha256": _sha256_file(g0_doc_path),
                "d2_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
                "d2_spec_sha256": _sha256_file(d2_doc_path),
                "t05_evidence_sha256": t05_sha,
                "t06_evidence_sha256": t06_sha,
                **source_hashes_after,
                "vector_file_sha256": vector_result["vector_sha256"],
                "stimulus_vector_sha256": vector_result["stimulus_vector_sha256"],
                "golden_output_sha256": vector_result["golden_output_sha256"],
            },
            "randomness": vector_result["randomness"],
            "head_descriptors": vector_result["descriptors"],
            "counts": vector_result["counts"],
            "directed_cases": vector_result["directed_cases"],
            "vector_file_bytes": vector_result["vector_file_bytes"],
            "invalid_assertions": {
                "BAD_ARGUMENT_code_1": vector_result["counts"]["BAD_ARGUMENT"],
                "BAD_RANGE_code_2": vector_result["counts"]["BAD_RANGE"],
                "producer_tensor_identity_mismatch_both_heads": vector_result["identity_mismatch_cases"],
                "non_immediate_producer_guard": vector_result["non_immediate_producer_cases"],
                "maximum_uint32_boundary_success": vector_result["counts"]["maximum_uint32_boundary_success"],
            },
            "vivado": {
                "bin": str(_XILINX_BIN),
                "phases": phase_codes,
                "command_template": "python -B -m unittest verification.test_s2a_yolo_view_rtl -v",
            },
            "limitations": [
                "只查询一个 YOLO 输出元素的逻辑通道、NCHW byte offset 和来源地址别名，不发起 memory transaction。",
                "不执行 INT8 值读取、解码、sigmoid、阈值、NMS、PS/PL 联调或完整网络运算。",
                "本证据不代表整网逐层比对、Vivado 综合、资源估算或时序通过。",
                "地址是 G0 逻辑仿真 byte address，不表示 Zynq DDR 物理地址。",
            ],
        }
        evidence_path = repository / "report/evidence/S2A-T08/yolo_view_query_simulation.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_bytes(
            (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        print(
            "S2A-T08 manifest_sha256={} vector_sha256={} stimulus_sha256={} golden_sha256={} "
            "counts={} yolo_before={} yolo_after={} vivado={}".format(
                manifest_sha,
                vector_result["vector_sha256"],
                vector_result["stimulus_vector_sha256"],
                vector_result["golden_output_sha256"],
                vector_result["counts"],
                vector_result["randomness"]["state_before_yolo"],
                vector_result["randomness"]["state_after_random_queries"],
                [phase["exit_code"] for phase in phase_codes],
            )
        )


if __name__ == "__main__":
    unittest.main()
