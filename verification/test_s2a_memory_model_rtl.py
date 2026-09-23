"""通过 Vivado 验证 G0 单 outstanding memory testbench model。"""

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
_RANDOM_SEED = 20260923
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_MAX_FEATURE_RANGES = 64
_FIELD_COUNT = 14
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_CLASS_NAMES = ["read_input", "read_weights", "read_feature", "write_feature"]
_CATEGORY_NAMES = ["random", "directed", "invalid", "fault"]


class XorShift32:
    """维护 T10 独立 memory-transfer 向量随机流。"""

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
            raise ValueError("T10 选择器上界必须为正数")
        return self.next_u32() % bound


def _sha256_bytes(value: bytes) -> str:
    """计算原始字节的 SHA-256。"""
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _manifest_ranges(manifest: dict) -> dict:
    """从冻结 manifest 生成互不重叠的逻辑 memory object 清单。"""
    address_map = manifest["address_map"]
    input_map = address_map["input"]
    weights_map = address_map["weight_package"]
    workspace = address_map["feature_workspace"]
    input_range = (int(input_map["address"]),
                   int(input_map["address"]) + int(input_map["length_bytes"]))
    weights_range = (int(weights_map["address"]),
                     int(weights_map["address"]) + int(weights_map["length_bytes"]))
    workspace_range = (int(workspace["base_address"]),
                       int(workspace["end_address_exclusive"]))
    if input_range != (0, 519168) or weights_range != (0x00100000, 0x00100000 + 5903100):
        raise ValueError("G0 输入/权重对象范围变化")
    if int(workspace["alignment_bytes"]) != 64:
        raise ValueError("G0 feature workspace alignment 变化")
    if input_range[1] > weights_range[0] or weights_range[1] > workspace_range[0]:
        raise ValueError("G0 输入、权重、feature workspace 顺序或重叠发生变化")

    layers = {int(item["layer_index"]): item for item in manifest["layers"]}
    heads = {item["name"]: item for item in address_map["heads"]}
    for yolo_index, head_name in ((30, "head13"), (37, "head26")):
        yolo = layers[yolo_index]
        head = heads[head_name]
        sources = yolo.get("input_tensor_indices", [])
        source_index = int(head["source_convolution_layer_index"])
        source = layers[source_index]
        if (yolo.get("op") != "yolo" or sources != [source_index] or
                int(yolo["tensor_address"]) != int(source["tensor_address"]) or
                int(yolo["tensor_length_bytes"]) != int(source["tensor_length_bytes"]) or
                int(head["address"]) != int(source["tensor_address"]) or
                int(head["length_bytes"]) != int(source["tensor_length_bytes"])):
            raise ValueError(f"G0 {head_name} alias 与 source convolution 不一致")

    unique: dict[tuple[int, int], list[int]] = {}
    for layer in manifest["layers"]:
        if layer.get("op") == "yolo":
            continue
        start = int(layer["tensor_address"])
        length = int(layer["tensor_length_bytes"])
        end = start + length
        shape = layer["output_shape_nchw"]
        elements = 1
        for dimension in shape:
            elements *= int(dimension)
        if (length != elements or start % 64 != 0 or start < workspace_range[0] or
                end > workspace_range[1] or end > 0x1_0000_0000):
            raise ValueError(f"G0 layer {layer['layer_index']} feature descriptor 非法")
        unique.setdefault((start, end), []).append(int(layer["layer_index"]))
    ranges = sorted(unique)
    if len(ranges) != 36 or len(unique) != len(ranges):
        raise ValueError("G0 unique feature tensor 数量或别名范围改变")
    for index, (start, end) in enumerate(ranges):
        if index and ranges[index - 1][1] > start:
            raise ValueError("G0 feature tensor 半开区间重叠")
        if (start < input_range[1] and input_range[0] < end) or (
                start < weights_range[1] and weights_range[0] < end):
            raise ValueError("G0 feature 与 input/weight object 重叠")

    protocol = manifest["memory_protocol"]
    plan_vectors = manifest["operator_test_plan"]["protocol_vectors"]
    expected_stall = plan_vectors["memory_stall_cycles"]
    recovery = plan_vectors["memory_error_recovery"]
    cancel = plan_vectors["cancel_pending_write"]
    if (expected_stall != _STALL_SCHEDULE or
            recovery["trigger"] !=
            "issue a legal feature-memory read and inject each listed nonzero mem_error_code on its handshake; codes 6 and 7 respectively cover INTERNAL and unknown-nonzero mapping" or
            cancel["request"] !=
            "feature write with mem_valid=1 while testbench holds mem_ready=0 for 7 cycles" or
            "selected lanes must each lie in one logical readable object" not in protocol["read_strobe"] or
            "selected lanes must each lie in one logical feature tensor" not in protocol["write_strobe"] or
            protocol["error_response_codes"].get("6") !=
            "INTERNAL; memory-model storage failure"):
        raise ValueError("G0 memory protocol/stall/error vector changed")
    return {
        "input": input_range,
        "weights": weights_range,
        "workspace": workspace_range,
        "features": ranges,
        "feature_owners": [unique[item] for item in ranges],
        "protocol": protocol,
        "protocol_vectors": plan_vectors,
    }


def _object_id(address: int, ranges: dict) -> int | None:
    """按半开区间确定单个逻辑字节所属对象。"""
    if ranges["input"][0] <= address < ranges["input"][1]:
        return 0
    if ranges["weights"][0] <= address < ranges["weights"][1]:
        return 1
    for feature_index, (start, end) in enumerate(ranges["features"]):
        if start <= address < end:
            return feature_index + 2
    return None


def _request_class(write: int, address: int, ranges: dict) -> int:
    """返回协议四类之一；写请求统一归入 write_feature 类。"""
    if write:
        return 3
    if ranges["input"][0] <= address < ranges["input"][1]:
        return 0
    if ranges["weights"][0] <= address < ranges["weights"][1]:
        return 1
    return 2


def _request_error(write: int, address: int, read_strobe: int,
                   write_strobe: int, fault_valid: int, fault_code: int,
                   ranges: dict) -> int:
    """独立 Python oracle 判定协议错误和注入故障返回码。"""
    if ((not write and (read_strobe == 0 or write_strobe != 0)) or
            (write and (write_strobe == 0 or read_strobe != 0))):
        return 1
    if address & 3:
        return 2
    strobe = write_strobe if write else read_strobe
    selected = [address + lane for lane in range(4) if (strobe >> lane) & 1]
    objects = [_object_id(byte_address, ranges) for byte_address in selected]
    if (not selected or any(item is None for item in objects) or
            len(set(objects)) != 1 or (write and objects[0] < 2)):
        return 2
    if fault_valid:
        return fault_code if fault_code in (6, 7) else 6
    return 0


def _initial_byte(address: int) -> int:
    """返回仅用于仿真的稳定初始字节图样。"""
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _read_data(address: int, strobe: int, shadow: dict[int, int]) -> int:
    """按 little-endian byte lane 组装已选择的读数据。"""
    result = 0
    for lane in range(4):
        if (strobe >> lane) & 1:
            byte_address = address + lane
            value = shadow.get(byte_address, _initial_byte(byte_address))
            result |= value << (lane * 8)
    return result


def _materialize_vectors(manifest: dict, work: Path) -> dict:
    """生成 manifest 派生范围、随机传输、边界、错误和恢复向量。"""
    ranges = _manifest_ranges(manifest)
    range_lines = [
        " ".join(f"{value:08X}" for value in (
            ranges["input"][0], ranges["input"][1], ranges["weights"][0],
            ranges["weights"][1], len(ranges["features"])))
    ]
    range_lines.extend(f"{start:08X} {end:08X}"
                       for start, end in ranges["features"])
    ranges_bytes = ("\n".join(range_lines) + "\n").encode("ascii")
    ranges_path = work / "memory_ranges.dat"
    ranges_path.write_bytes(ranges_bytes)

    rng = XorShift32(_RANDOM_SEED)
    class_schedule_index = [0, 0, 0, 0]
    shadow: dict[int, int] = {}
    rows: list[list[int]] = []
    vector_digest = hashlib.sha256()
    stimulus_digest = hashlib.sha256()
    expected_digest = hashlib.sha256()
    stall_digest = hashlib.sha256()
    counts = {
        "random_by_class": {name: 0 for name in _CLASS_NAMES},
        "accepted_by_class": {name: 0 for name in _CLASS_NAMES},
        "category_transfers": {name: 0 for name in _CATEGORY_NAMES},
        "directed_cases": 0,
        "BAD_ARGUMENT": 0,
        "BAD_RANGE": 0,
        "fault_code_6": 0,
        "fault_code_7": 0,
        "cancel_valid_withdrawal": 0,
        "cancel_reset": 0,
        "valid_read_lanes": 0,
        "valid_write_lanes": 0,
        "disabled_read_lanes_checked": 0,
        "disabled_write_lanes_checked": 0,
        "feature_ranges_checked": 0,
        "feature_holes_checked": 0,
    }

    def append_row(mode: int, category: int, write: int, address: int,
                   wdata: int, read_strobe: int, write_strobe: int,
                   fault_valid: int = 0, fault_code: int = 0,
                   abort_cycles: int = 0) -> None:
        request_class = _request_class(write, address, ranges)
        if mode == 0:
            stall = _STALL_SCHEDULE[class_schedule_index[request_class] % 5]
            error = _request_error(write, address, read_strobe, write_strobe,
                                   fault_valid, fault_code, ranges)
            read_data = 0
            if not write and error == 0:
                read_data = _read_data(address, read_strobe, shadow)
            fields = [mode, category, request_class, write, address, wdata,
                      read_strobe, write_strobe, fault_valid, fault_code,
                      error, read_data, stall, abort_cycles]
            if not 0 <= category <= 3:
                raise ValueError("向量 category 超出固定类别")
            counts["accepted_by_class"][_CLASS_NAMES[request_class]] += 1
            counts["category_transfers"][_CATEGORY_NAMES[category]] += 1
            counts["BAD_ARGUMENT"] += error == 1
            counts["BAD_RANGE"] += error == 2
            if fault_valid and error == fault_code:
                counts[f"fault_code_{fault_code}"] += 1
            if not write and error == 0:
                counts["valid_read_lanes"] += read_strobe.bit_count()
                counts["disabled_read_lanes_checked"] += 4 - read_strobe.bit_count()
            if write and error == 0:
                counts["valid_write_lanes"] += write_strobe.bit_count()
                counts["disabled_write_lanes_checked"] += 4 - write_strobe.bit_count()
                for lane in range(4):
                    if (write_strobe >> lane) & 1:
                        shadow[address + lane] = (wdata >> (lane * 8)) & 0xFF
            class_schedule_index[request_class] += 1
        elif mode in (1, 2):
            stall = _STALL_SCHEDULE[class_schedule_index[request_class] % 5]
            if write != 1 or request_class != 3 or stall != 7:
                raise ValueError("取消向量必须命中 write_feature 的七周期 stall");
            error = 0
            read_data = 0
            fields = [mode, category, request_class, write, address, wdata,
                      read_strobe, write_strobe, 0, 0, error, read_data,
                      stall, abort_cycles]
            counts["cancel_valid_withdrawal" if mode == 1 else "cancel_reset"] += 1
        else:
            raise ValueError("未知 memory vector mode")
        if len(fields) != _FIELD_COUNT or any(not 0 <= item <= 0xFFFFFFFF for item in fields):
            raise ValueError("T10 vector field count/uint32 range invalid")
        rows.append(fields)
        vector_digest.update(struct.pack("<14I", *fields))
        stimulus_digest.update(struct.pack("<10I", *fields[:10]))
        expected_digest.update(struct.pack("<2I", fields[10], fields[11]))
        stall_digest.update(struct.pack("<3I", fields[0], fields[2], fields[12]))

    def add_transfer(category: int, write: int, address: int, wdata: int = 0,
                     read_strobe: int = 0, write_strobe: int = 0,
                     fault_valid: int = 0, fault_code: int = 0) -> None:
        append_row(0, category, write, address, wdata, read_strobe,
                   write_strobe, fault_valid, fault_code)
        if category == 1:
            counts["directed_cases"] += 1

    def add_cancel(mode: int, address: int, wdata: int,
                   abort_cycles: int) -> None:
        append_row(mode, 1, 1, address, wdata, 0, 0xF, abort_cycles=abort_cycles)

    first_feature = ranges["features"][0][0]
    # 三次 feature write 先消耗 0/1/2 周期，随后按 G0 做 reset/撤销取消。
    for index, mask in enumerate((0xF, 0x5, 0xA)):
        address = first_feature + 4 * (index + 1)
        add_transfer(1, 1, address, 0x11223344 ^ (index * 0x01010101), 0, mask)
        add_transfer(1, 0, address, 0, 0xF, 0)
    if class_schedule_index[3] % 5 != 3:
        raise ValueError("T10 write_feature schedule did not reach seven-cycle slot")
    reset_cancel_address = first_feature + 64
    add_cancel(2, reset_cancel_address, 0xA1B2C3D4, abort_cycles=5)
    add_transfer(1, 0, reset_cancel_address, 0, 0xF, 0)
    withdraw_cancel_address = first_feature + 68
    add_cancel(1, withdraw_cancel_address, 0x5E6F7081, abort_cycles=7)
    add_transfer(1, 0, withdraw_cancel_address, 0, 0xF, 0)
    add_transfer(1, 1, withdraw_cancel_address, 0x89ABCDEF, 0, 0xF)
    add_transfer(1, 0, withdraw_cancel_address, 0, 0xF, 0)

    # 每类各一千个随机事务；写入先于 feature 随机读取以验证持久 lane 值。
    for request_class in (0, 1, 3, 2):
        for _ in range(1000):
            if request_class == 0:
                start, end = ranges["input"]
            elif request_class == 1:
                start, end = ranges["weights"]
            else:
                eligible = [item for item in ranges["features"]
                            if (item[1] - item[0]) >= 4]
                start, end = eligible[rng.selector(len(eligible))]
            first_word = (start + 3) & ~3
            last_full_word = (end - 4) & ~3
            word_count = ((last_full_word - first_word) // 4) + 1
            address = first_word + 4 * rng.selector(word_count)
            strobe = 1 + rng.selector(15)
            value = rng.next_u32()
            if request_class == 0:
                add_transfer(0, 0, address, value, strobe, 0)
            elif request_class == 1:
                add_transfer(0, 0, address, value, strobe, 0)
            elif request_class == 2:
                add_transfer(0, 0, address, value, strobe, 0)
            else:
                add_transfer(0, 1, address, value, 0, strobe)
            counts["random_by_class"][_CLASS_NAMES[request_class]] += 1

    # 每个对象首尾读；feature 张量另覆盖首尾写和 lane 保留。
    for object_range in (ranges["input"], ranges["weights"]):
        start, end = object_range
        for address in (start, end - 4):
            add_transfer(1, 0, address, 0, 0xF, 0)
        add_transfer(2, 1, start, 0xDEADBEEF, 0, 0xF)
        add_transfer(1, 0, start, 0, 0xF, 0)

    for feature_index, (start, end) in enumerate(ranges["features"]):
        first_word = start & ~3
        last_word = (end - 1) & ~3
        tail_lanes = end - last_word
        tail_mask = (1 << tail_lanes) - 1
        add_transfer(1, 0, first_word, 0, 0x1, 0)
        add_transfer(1, 1, first_word, 0xA1B2C3D4 ^ feature_index, 0, 0xF)
        add_transfer(1, 0, first_word, 0, 0xF, 0)
        add_transfer(1, 0, last_word, 0, tail_mask, 0)
        add_transfer(1, 1, last_word, 0x5A6B7C8D ^ feature_index, 0, tail_mask)
        add_transfer(1, 0, last_word, 0, tail_mask, 0)
        if tail_mask != 0xF:
            add_transfer(2, 0, last_word, 0, tail_mask | (1 << tail_lanes), 0)
            add_transfer(1, 0, last_word, 0, tail_mask, 0)
            add_transfer(2, 1, last_word, 0xFFFFFFFF, 0,
                         tail_mask | (1 << tail_lanes))
            add_transfer(1, 0, last_word, 0, tail_mask, 0)
        counts["feature_ranges_checked"] += 1

    # 用单独选中的 byte lane 检查每个 feature 对齐空洞均不可访问。
    cursor = ranges["workspace"][0]
    for start, end in ranges["features"]:
        if cursor < start:
            probe = cursor
            aligned = probe & ~3
            lane = probe & 3
            add_transfer(2, 0, aligned, 0, 1 << lane, 0)
            counts["feature_holes_checked"] += 1
        cursor = end
    if cursor < ranges["workspace"][1]:
        aligned = cursor & ~3
        add_transfer(2, 0, aligned, 0, 1 << (cursor & 3), 0)
        counts["feature_holes_checked"] += 1
    add_transfer(2, 0, ranges["workspace"][1], 0, 0x1, 0)

    # 逻辑错误与非法写入必须在之后读回原值，证明未产生副作用。
    first_input = ranges["input"][0]
    first_weight = ranges["weights"][0]
    add_transfer(2, 1, first_input, 0x01020304, 0, 0xF)
    add_transfer(1, 0, first_input, 0, 0xF, 0)
    add_transfer(2, 1, first_weight, 0x05060708, 0, 0xF)
    add_transfer(1, 0, first_weight, 0, 0xF, 0)

    feature_start = ranges["features"][0][0]
    add_transfer(2, 0, feature_start, 0, 0, 0)
    add_transfer(2, 1, feature_start, 0x12345678, 0, 0)
    add_transfer(2, 0, feature_start, 0, 0x1, 0x1)
    add_transfer(2, 1, feature_start, 0x12345678, 0x1, 0x1)
    add_transfer(2, 0, ranges["input"][0] + 1, 0, 0x1, 0)
    add_transfer(2, 1, feature_start + 1, 0x12345678, 0, 0x1)
    add_transfer(1, 0, feature_start, 0, 0xF, 0)

    # 固定 head13 odd tail：0011 成功，访问下一 lane 失败且随后原样读回。
    head13 = next((item for item in ranges["features"]
                   if item == (int(manifest["address_map"]["heads"][0]["address"]),
                               int(manifest["address_map"]["heads"][0]["address"]) +
                               int(manifest["address_map"]["heads"][0]["length_bytes"]))), None)
    if head13 is None:
        raise ValueError("G0 head13 tensor interval 缺失")
    tail_word = (head13[1] - 1) & ~3
    if head13[1] - tail_word != 2:
        raise ValueError("G0 head13 odd tail lane mask 不再是 0011")

    # 按 G0 memory recovery 向量对 feature read 注入 6/7，再测错误释放后恢复。
    for injected_code in (6, 7):
        add_transfer(3, 0, feature_start, 0, 0xF, 0, 1, injected_code)
        add_transfer(1, 0, feature_start, 0, 0xF, 0)
    # 额外模型局部验证：故障写请求不提交任何 byte patch。
    for injected_code, address in ((6, feature_start + 112),
                                   (7, feature_start + 116)):
        add_transfer(3, 1, address, 0xC001D00D ^ injected_code, 0, 0x5,
                     1, injected_code)
        add_transfer(1, 0, address, 0, 0xF, 0)

    if counts["cancel_valid_withdrawal"] != 1 or counts["cancel_reset"] != 1:
        raise ValueError("T10 cancel vector count mismatch")
    if any(counts["random_by_class"][name] != 1000 for name in _CLASS_NAMES):
        raise ValueError("每类随机事务必须恰为 1000")
    if counts["feature_ranges_checked"] != 36 or counts["feature_holes_checked"] == 0:
        raise ValueError("feature range/hole 覆盖不完整")
    if counts["fault_code_6"] < 2 or counts["fault_code_7"] < 2:
        raise ValueError("G0 read 与 model-local write fault 覆盖不完整")

    vector_path = work / "vectors.dat"
    with vector_path.open("w", encoding="ascii", newline="\n") as stream:
        for fields in rows:
            stream.write(" ".join(f"{value:08X}" for value in fields) + "\n")
    encoded_rows = vector_path.read_bytes()
    if len(encoded_rows) != vector_path.stat().st_size:
        raise ValueError("向量文件字节数不稳定")
    return {
        "ranges": ranges,
        "feature_ranges_count": len(ranges["features"]),
        "feature_range_owners": ranges["feature_owners"],
        "feature_holes": counts["feature_holes_checked"],
        "range_file_bytes": len(ranges_bytes),
        "range_file_sha256": _sha256_bytes(ranges_bytes),
        "counts": counts,
        "total_vector_rows": len(rows),
        "vector_file_bytes": len(encoded_rows),
        "vector_file_sha256": _sha256_bytes(encoded_rows),
        "stimulus_vector_sha256": stimulus_digest.hexdigest(),
        "expected_response_sha256": expected_digest.hexdigest(),
        "stall_sequence_sha256": stall_digest.hexdigest(),
        "prng": {
            "seed": _RANDOM_SEED,
            "scope": "T10 独立 transfer stream，不推进 G0 operator PRNG",
            "draw_order": "类别 read_input/read_weights/write_feature/read_feature；每个随机事务依次选择 feature 范围（适用时）、word、strobe、write data",
            "state_after_random_transfers": f"0x{rng.state:08X}",
        },
        "class_stall_order": {
            name: _STALL_SCHEDULE for name in _CLASS_NAMES
        },
        "category_counts": counts["category_transfers"],
        "class_transfer_counts": counts["accepted_by_class"],
    }


def _assert_temporary_cwd(work: Path, repository: Path) -> None:
    """确保 Vivado 工作目录位于系统 TEMP 且不在仓库内。"""
    temp_root = Path(tempfile.gettempdir()).resolve()
    resolved = work.resolve()
    if (not resolved.is_dir() or resolved == repository or
            os.path.commonpath([str(temp_root), str(resolved)]) != str(temp_root) or
            repository in resolved.parents):
        raise RuntimeError(f"拒绝在非隔离系统 TEMP 目录运行 Vivado：{resolved}")


def _run_tool(tool: Path, arguments: list[str], work: Path,
              log_path: Path, deadline: float, repository: Path) -> tuple[int, str]:
    """在已验证 TEMP cwd 运行一个 Vivado 阶段并保存隔离日志。"""
    if not tool.is_file():
        raise FileNotFoundError(f"Vivado 工具不存在：{tool}")
    _assert_temporary_cwd(work, repository)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("S2A-T10 Vivado 运行超过 600 秒停止限制")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    result = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=work, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=remaining,
    )
    output = result.stdout + result.stderr
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return result.returncode, output


class TestS2AMemoryModelRtl(unittest.TestCase):
    """验证 G0 memory model 字节寻址、strobe、stall 与恢复语义。"""

    def test_memory_model_against_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        spec_path = repository / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
        model_path = repository / "sim/s2a_memory_model.sv"
        bench_path = repository / "sim/tb_s2a_memory_model.sv"
        runner_path = Path(__file__).resolve()
        for path in (manifest_path, spec_path, model_path, bench_path, runner_path):
            self.assertTrue(path.is_file(), f"缺少 T10 绑定文件：{path}")

        manifest_raw = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_raw)
        self.assertEqual(manifest_sha, _MANIFEST_SHA256,
                         "G0 manifest 原始 SHA 变化，按任务停止条件中止")
        manifest = json.loads(manifest_raw.decode("utf-8"))
        source_hashes_before = {
            "model_sha256": _sha256_file(model_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(runner_path),
        }
        spec_sha = _sha256_file(spec_path)
        tool_paths = {name: _XILINX_BIN / f"{name}.bat"
                      for name in ("xvlog", "xelab", "xsim")}
        for path in tool_paths.values():
            self.assertTrue(path.is_file(), f"Vivado 工具不存在：{path}")

        with tempfile.TemporaryDirectory(prefix="s2a_t10_memory_model_") as temp_dir:
            work = Path(temp_dir).resolve()
            _assert_temporary_cwd(work, repository)
            generated = _materialize_vectors(manifest, work)
            self.assertEqual(generated["counts"]["random_by_class"],
                             {name: 1000 for name in _CLASS_NAMES})
            phases = []
            commands = [
                ("xvlog", ["-sv", str(model_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_memory_model",
                           "-snapshot", "s2a_memory_model_snapshot"]),
                ("xsim", ["-R", "s2a_memory_model_snapshot"]),
            ]
            deadline = time.monotonic() + 600.0
            for name, arguments in commands:
                exit_code, output = _run_tool(
                    tool_paths[name], arguments, work, work / f"{name}.log",
                    deadline, repository,
                )
                phases.append({"phase": name, "exit_code": exit_code})
                self.assertEqual(exit_code, 0,
                                 f"{name} 退出码 {exit_code}，日志尾部：\n{output[-5000:]}")
                if name == "xsim":
                    expected_summary = (
                        f"PASS: accepted={sum(generated['class_transfer_counts'].values())} "
                        f"read_input={generated['class_transfer_counts']['read_input']} "
                        f"read_weights={generated['class_transfer_counts']['read_weights']} "
                        f"read_feature={generated['class_transfer_counts']['read_feature']} "
                        f"write_feature={generated['class_transfer_counts']['write_feature']} "
                        f"random={sum(generated['category_counts'].values()) - generated['category_counts']['directed'] - generated['category_counts']['invalid'] - generated['category_counts']['fault']} "
                        f"directed={generated['category_counts']['directed']} "
                        f"invalid={generated['category_counts']['invalid']} "
                        f"fault={generated['category_counts']['fault']} cancelled=2 "
                        f"BAD_ARGUMENT={generated['counts']['BAD_ARGUMENT']} "
                        f"BAD_RANGE={generated['counts']['BAD_RANGE']}"
                    )
                    self.assertIn(expected_summary, output)

        source_hashes_after = {
            "model_sha256": _sha256_file(model_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(runner_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真期间 T10 源文件发生变化")
        self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                         "仿真期间 G0 manifest 原始 SHA 变化")
        self.assertEqual(_sha256_file(spec_path), spec_sha,
                         "仿真期间 G0 spec 原始 SHA 变化")

        evidence = {
            "schema_version": "gestureforge_s2a_t10_memory_model_simulation_v1",
            "result": "PASS",
            "scope": "G0 单 outstanding memory testbench model，不含 PL memory master",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": manifest_sha,
                "g0_spec_path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
                "g0_spec_sha256": spec_sha,
                **source_hashes_after,
                "manifest_derived_ranges_sha256": generated["range_file_sha256"],
                "vector_file_sha256": generated["vector_file_sha256"],
                "stimulus_vector_sha256": generated["stimulus_vector_sha256"],
                "expected_response_sha256": generated["expected_response_sha256"],
                "stall_sequence_sha256": generated["stall_sequence_sha256"],
            },
            "objects": {
                "input": {"start_inclusive": generated["ranges"]["input"][0],
                          "end_exclusive": generated["ranges"]["input"][1],
                          "access": "read_only"},
                "weights": {"start_inclusive": generated["ranges"]["weights"][0],
                            "end_exclusive": generated["ranges"]["weights"][1],
                            "package_sha256_from_manifest": manifest["address_map"]["weight_package"]["sha256"],
                            "access": "read_only", "external_package_read": False},
                "feature_workspace": {
                    "start_inclusive": generated["ranges"]["workspace"][0],
                    "end_exclusive": generated["ranges"]["workspace"][1],
                    "unique_tensor_range_count": generated["feature_ranges_count"],
                    "tensor_ranges": [
                        {"start_inclusive": start, "end_exclusive": end,
                         "manifest_layer_indices": owners}
                        for (start, end), owners in zip(
                            generated["ranges"]["features"],
                            generated["feature_range_owners"],
                        )
                    ],
                    "yolo_aliases_deduplicated": [30, 37],
                    "checked_holes": generated["feature_holes"],
                    "alignment_gaps_are_unmapped": True,
                },
            },
            "protocol": {
                "request": "single outstanding 32-bit word, byte addressed, little endian",
                "lanes": "lane i maps address+i and data bits [8*i +: 8]",
                "request_classes": _CLASS_NAMES,
                "stall_cycle_order_per_class": _STALL_SCHEDULE,
                "acceptance": "ready is low for the scheduled N cycles; the first following ready-high rising edge accepts the request",
                "idle_reset_ownerless": "ready=0 and error=NONE",
                "error_codes": {"BAD_ARGUMENT": 1, "BAD_RANGE": 2,
                                "INTERNAL": 6, "unknown_nonzero_injection": 7},
                "head13_tail": {"aligned_word_address": (int(manifest["address_map"]["heads"][0]["address"]) +
                                                              int(manifest["address_map"]["heads"][0]["length_bytes"]) - 2) & ~3,
                                 "valid_lane_mask": "0011"},
                "fault_vectors": {
                    "G0_feature_read_code_6_and_7": True,
                    "model_local_failed_feature_writes_no_side_effect": True,
                },
                "cancel_vectors": {
                    "withdraw_valid_after_seven_ready_low_cycles": 1,
                    "reset_before_ready_high_handshake": 1,
                    "reset_timeout_pl_master_integration": False,
                },
            },
            "randomness": generated["prng"],
            "counts": generated["counts"],
            "total_vector_rows": generated["total_vector_rows"],
            "vector_file_bytes": generated["vector_file_bytes"],
            "vivado": {
                "bin": str(_XILINX_BIN),
                "phases": phases,
                "command_template": "python -B -m unittest verification.test_s2a_memory_model_rtl -v",
            },
            "limitations": [
                "只验证 testbench logical memory model；不实现或验证 PL master、DMA、控制FSM、CSR、物理 AXI/cache 或实物行为。",
                "读对象数据由确定性仿真图样提供；不读取外部权重包，也不代表真实输入/权重内容。",
                "6/7 code 的G0 recovery向量在合法 feature read 上验证；额外写故障用例仅验证 model 无副作用，不冒充 G0 控制恢复。",
                "reset/valid撤销仅在独立模型边界验证；不代表 master reset/timeout 集成路径已通过。",
                "未执行综合、资源估算或时序检查。",
            ],
        }
        evidence_path = repository / "report/evidence/S2A-T10/memory_model_simulation.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_bytes(
            (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        print(
            "S2A-T10 manifest_sha256={} range_sha256={} vector_sha256={} stimulus_sha256={} "
            "expected_sha256={} counts={} random_state={} vivado={}".format(
                manifest_sha, generated["range_file_sha256"],
                generated["vector_file_sha256"], generated["stimulus_vector_sha256"],
                generated["expected_response_sha256"], generated["counts"],
                generated["prng"]["state_after_random_transfers"],
                [phase["exit_code"] for phase in phases],
            )
        )


if __name__ == "__main__":
    unittest.main()
