"""运行 S2A-T28 layer33→34 runtime shell 串行集成仿真。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
_G0_SPEC = Path("docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md")
_MANIFEST = Path("report/evidence/S2A-T01/tiny416_model_manifest.json")
_T22 = Path("report/evidence/S2A-T22/network_dispatch_contract_validation.json")
_T18_EVIDENCE = Path("report/evidence/S2A-T18/upsample_layer_scheduler_simulation.json")
_T19_EVIDENCE = Path("report/evidence/S2A-T19/route_layer_scheduler_simulation.json")
_T27_EVIDENCE = Path("report/evidence/S2A-T27/runtime_layer33_pilot_validation.json")
_T10_MODEL = Path("sim/s2a_memory_model.sv")
_T12_MASTER = Path("src/s2a_memory_master.sv")
_CSR = Path("src/s2a_control_csr.sv")
_SHELL = Path("src/s2a_runtime_shell.sv")
_UPSAMPLE_QUERY = Path("src/int8_upsample_query.sv")
_UPSAMPLE_ENGINE = Path("src/s2a_upsample_engine.sv")
_UPSAMPLE_SCHEDULER = Path("src/s2a_upsample_layer_scheduler.sv")
_ROUTE_QUERY = Path("src/int8_route_query.sv")
_ROUTE_ENGINE = Path("src/s2a_route_engine.sv")
_ROUTE_SCHEDULER = Path("src/s2a_route_layer_scheduler.sv")
_T18_TB = Path("sim/tb_s2a_upsample_layer_scheduler.sv")
_T18_RUNNER = Path("verification/test_s2a_upsample_layer_scheduler_rtl.py")
_T19_TB = Path("sim/tb_s2a_route_layer_scheduler.sv")
_T19_RUNNER = Path("verification/test_s2a_route_layer_scheduler_rtl.py")
_T27_WRAPPER = Path("src/s2a_runtime_layer33_pilot.sv")
_T27_TB = Path("sim/tb_s2a_runtime_layer33_pilot.sv")
_T27_RUNNER = Path("verification/s2a_runtime_layer33_pilot.py")
_T27_TEST = Path("verification/test_s2a_runtime_layer33_pilot_rtl.py")
_WRAPPER = Path("src/s2a_runtime_layers33_34_pilot.sv")
_TB = Path("sim/tb_s2a_runtime_layers33_34_pilot.sv")
_RUNNER = Path("verification/s2a_runtime_layers33_34_pilot.py")
_TEST = Path("verification/test_s2a_runtime_layers33_34_pilot_rtl.py")
_EVIDENCE_DIR = Path("report/evidence/S2A-T28")
_EVIDENCE = _EVIDENCE_DIR / "runtime_layers33_34_pilot_validation.json"
_TRACE33 = "observed_layer33_hex.txt"
_TRACE34 = "observed_layer34_hex.txt"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_TOTAL_TIMEOUT_SECONDS = 7200
_NO_PROGRESS_SECONDS = 1800
_RANDOM_SEED = 0x2A202609
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_REPLACEABLE_PREVIOUS_EVIDENCE_SHA256 = "2ba916f933c48cdffbf4d7c4874f66899717ab50eea6fac1c759c174fcc6faa4"

_PINNED_HASHES = {
    _G0_SPEC.as_posix(): "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    _MANIFEST.as_posix(): "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    _T22.as_posix(): "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
    _T18_EVIDENCE.as_posix(): "0f2a4a81275ffa225babb78b767bfc42a597320308ef7b150af5f80fd6aac35d",
    _T19_EVIDENCE.as_posix(): "e3921f382fc8c6af3dea5ec9edf3fd9795a49e09982381e2501ad8d9aa592880",
    _T27_EVIDENCE.as_posix(): "33250855f5b80c30dd477f74ccbaf88b7bf721faf6286abc25d8dd0f652a30f6",
    _T10_MODEL.as_posix(): "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
    _T12_MASTER.as_posix(): "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    _CSR.as_posix(): "97fc62dd1967ea9486db1c6e48134283d62005805a0ca5ef44d6ea70ab2fc9d2",
    _SHELL.as_posix(): "c784de2c94456eb4bdbd9ff763454b9784ebcb8d8821d6505d68707cfc37e52e",
    _UPSAMPLE_QUERY.as_posix(): "9212f70c31fab6c6e5a30551c5d1fd7b6eeeafa4c1f2cbd20fe157015faa370c",
    _UPSAMPLE_ENGINE.as_posix(): "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b",
    _UPSAMPLE_SCHEDULER.as_posix(): "1473fd371c65658e105ff2ad575d523a98a53e5c5ebd8bb9f21ca33b61678bce",
    _ROUTE_QUERY.as_posix(): "2f13e90858f6e665cf05444aac8e4db396b09f798acedd51e37bfd2c56f1dd64",
    _ROUTE_ENGINE.as_posix(): "4748df19474e6b90e11bb760854311da92ba8d19a5b1d4b12e3d7b2b7968fe44",
    _ROUTE_SCHEDULER.as_posix(): "ff078b830f76ca12baaa307e65f90958c0d0938fd0d1a4489955c2021a5d94d1",
    _T18_TB.as_posix(): "ec15fd8a86a6c63e1a0ffa2fe4059c644cb61a78cd01f1ebef03901f917469de",
    _T18_RUNNER.as_posix(): "c8ddc62aae0a1da19379c600349de4380287afec85f82727828b0cd55ec5af1b",
    _T19_TB.as_posix(): "63a82b0b74e68874ff24810e9598a9d0c1b536bb2da4fd2aaa008ee6e5ff8755",
    _T19_RUNNER.as_posix(): "9c84dee53e87333f991f2536a0d98719ad3e3964ea095e12ce069406c846bbc0",
    _T27_WRAPPER.as_posix(): "6c3a5fd7bb0d0351f01ecfd722da41532db0405c2405a141274e26aca6381c1d",
    _T27_TB.as_posix(): "612de6f7f65d5a1e51579d7b4052b257e2a426b665309255ee14a098e6e19ad5",
    _T27_RUNNER.as_posix(): "3f53cd3a4a2137f3ae4ed316b62197823ae8f612bf0c53d98125ce7c8597a5ca",
    _T27_TEST.as_posix(): "8defc1fbcb8fc3c717997a71b836427e82df22f06dd4ead84ecb0036441fa542",
}


def _sha256_bytes(payload: bytes) -> str:
    """计算 byte 序列 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _repo_path(relative: Path) -> Path:
    """取得并验证仓库内的精确源文件路径。"""
    path = _ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(f"必需输入文件不存在：{relative.as_posix()}")
    return path


def _assert_hash(name: str, observed: str, expected: str) -> None:
    """拒绝冻结来源或动态代码的摘要不匹配。"""
    if observed != expected:
        raise AssertionError(
            f"SHA-256 不匹配：{name} observed={observed} expected={expected}"
        )


def _assert_source_snapshot_equal(
    before: dict[str, str], after: dict[str, str], context: str,
) -> None:
    """拒绝运行期间任何已绑定输入发生变化。"""
    changed = sorted(
        name for name in before.keys() | after.keys()
        if before.get(name) != after.get(name)
    )
    if changed:
        details = ", ".join(
            f"{name}: before={before.get(name, '<missing>')} after={after.get(name, '<missing>')}"
            for name in changed
        )
        raise AssertionError(f"{context} source hash snapshot changed: {details}")


def _write_verified_evidence(
    path: Path,
    result: dict[str, Any],
    before: dict[str, str],
    after: dict[str, str],
    expected_existing_sha256: str | None = None,
) -> bytes:
    """仅在源码快照一致时以独占方式写入 PASS evidence。"""
    _assert_source_snapshot_equal(before, after, "evidence write")
    payload = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(exist_ok=True)
    if expected_existing_sha256 is None:
        with path.open("xb") as evidence_file:
            evidence_file.write(payload)
            evidence_file.flush()
            os.fsync(evidence_file.fileno())
    else:
        _assert_hash(path.as_posix(), _sha256_file(path), expected_existing_sha256)
        temporary_path = path.with_name(path.name + ".candidate")
        if temporary_path.exists():
            raise FileExistsError(f"拒绝覆盖已存在 evidence 临时文件：{temporary_path}")
        created_temporary = False
        try:
            with temporary_path.open("xb") as evidence_file:
                created_temporary = True
                evidence_file.write(payload)
                evidence_file.flush()
                os.fsync(evidence_file.fileno())
            _assert_source_snapshot_equal(before, after, "evidence replace")
            _assert_hash(path.as_posix(), _sha256_file(path), expected_existing_sha256)
            os.replace(temporary_path, path)
        finally:
            if created_temporary and temporary_path.exists():
                temporary_path.unlink()
    return payload


def _copy_compilation_sources(
    sources: list[Path], hashes: dict[str, str], work: Path,
) -> list[Path]:
    """将已哈希的仿真输入复制到唯一临时目录并再次核对摘要。"""
    snapshot_root = work / "source_snapshot"
    snapshot_root.mkdir()
    copied: list[Path] = []
    for source in sources:
        relative = source.relative_to(_ROOT).as_posix()
        expected = hashes.get(relative)
        if expected is None:
            raise AssertionError(f"编译输入没有绑定 source SHA-256：{relative}")
        payload = source.read_bytes()
        _assert_hash(relative, _sha256_bytes(payload), expected)
        target = snapshot_root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        _assert_hash(f"临时编译副本 {relative}", _sha256_file(target), expected)
        copied.append(target)
    return copied


def _load_json(relative: Path) -> dict[str, Any]:
    """以 UTF-8 读取 JSON 对象。"""
    value = json.loads(_repo_path(relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON 根节点不是对象：{relative.as_posix()}")
    return value


def _layer_map(manifest: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """验证 tiny416 manifest 连续包含 38 个 layer rows。"""
    rows = manifest.get("layers")
    if not isinstance(rows, list) or len(rows) != 38:
        raise AssertionError("tiny416 manifest 必须包含 38 个 layer rows")
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("manifest layer row 必须为对象")
        index = int(row["layer_index"])
        if index in result:
            raise AssertionError(f"manifest layer_index 重复：{index}")
        result[index] = row
    if sorted(result) != list(range(38)):
        raise AssertionError("manifest layer_index 必须按 0..37 连续覆盖")
    return result


def _validate_contract(
    manifest: dict[str, Any], contract: dict[str, Any],
    t18: dict[str, Any], t19: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """交叉检查 manifest、T22、T18 与 T19 冻结的相邻层描述。"""
    layers = _layer_map(manifest)
    layer32 = layers[32]
    layer33 = layers[33]
    layer23 = layers[23]
    layer34 = layers[34]
    if (layer33.get("cfg_section") != 34 or layer33.get("op") != "upsample" or
            layer33.get("input_tensor_indices") != [32] or
            layer33.get("input_shape_nchw") != [1, 128, 13, 13] or
            layer33.get("output_shape_nchw") != [1, 128, 26, 26] or
            layer33.get("tensor_address") != 27619968 or
            layer33.get("tensor_length_bytes") != 86528 or
            layer33.get("stride") != 2 or layer33.get("method") != "nearest_repeat" or
            layer33.get("layout") != "NCHW" or
            layer33.get("element_type") != "int8_twos_complement" or
            layer33.get("input_scale") != layer32.get("output_scale") or
            layer33.get("output_scale") != layer33.get("input_scale") or
            layer32.get("tensor_address") != 27598336 or
            layer32.get("tensor_length_bytes") != 21632 or
            layer32.get("output_shape_nchw") != [1, 128, 13, 13]):
        raise AssertionError("manifest layer32/33 不符合冻结的 nearest-repeat 输入输出")
    if (layer34.get("cfg_section") != 35 or layer34.get("op") != "route" or
            layer34.get("input_tensor_indices") != [33, 23] or
            layer34.get("input_shape_nchw") != [[1, 128, 26, 26], [1, 256, 26, 26]] or
            layer34.get("input_scales") != [layer33["output_scale"], layer23["output_scale"]] or
            layer34.get("output_shape_nchw") != [1, 384, 26, 26] or
            layer34.get("tensor_address") != 27706496 or
            layer34.get("tensor_length_bytes") != 259584 or
            layer34.get("route_groups") != 1 or layer34.get("route_group_id") != 0 or
            layer34.get("route_source_channel_ranges") != [[0, 128], [0, 256]] or
            layer34.get("layout") != "NCHW" or
            layer34.get("element_type") != "int8_twos_complement"):
        raise AssertionError("manifest layer34 的 route ref 顺序、per-ref scale 或输出规格不符")
    if (layer23.get("tensor_address") != 26727936 or
            layer23.get("tensor_length_bytes") != 173056 or
            layer23.get("output_shape_nchw") != [1, 256, 26, 26]):
        raise AssertionError("manifest layer23 route 来源规格不符")

    if (contract.get("task_id") != "S2A-T22" or
            contract.get("artifact_status") != "CONTRACT_VALIDATED"):
        raise AssertionError("T22 dispatch contract 状态不是已验证")
    dispatch = contract.get("network_dispatch", {})
    rows = dispatch.get("layers")
    if dispatch.get("layer_count") != 38 or not isinstance(rows, list) or len(rows) != 38:
        raise AssertionError("T22 dispatch contract 必须保留 38 层完整图")
    protocol = contract.get("dispatch_protocol", {})
    timeout = protocol.get("global_timeout", {})
    completion = protocol.get("completion_event", {})
    if (timeout.get("per_layer_timeout_restart_allowed") is not False or
            completion.get("pulse_cycles") != 1 or completion.get("backpressure") is not False or
            completion.get("one_event_per_accepted_task") is not True):
        raise AssertionError("T22 的 global deadline / single terminal 规则不符")

    t22_rows = {int(row["layer_index"]): row for row in rows}
    row33 = t22_rows.get(33)
    row34 = t22_rows.get(34)
    if not isinstance(row33, dict) or not isinstance(row34, dict):
        raise AssertionError("T22 缺少 layer33 或 layer34 dispatch row")
    inputs33 = row33.get("input_tensors_in_manifest_order")
    inputs34 = row34.get("input_tensors_in_manifest_order")
    output33 = row33.get("output_tensor")
    output34 = row34.get("output_tensor")
    params33 = row33.get("operator_parameters")
    params34 = row34.get("operator_parameters")
    if (row33.get("cfg_section") != 34 or row33.get("op") != "upsample" or
            not isinstance(inputs33, list) or len(inputs33) != 1 or
            inputs33[0].get("source_index") != 32 or
            inputs33[0].get("address") != 27598336 or
            inputs33[0].get("length_bytes") != 21632 or
            not isinstance(output33, dict) or output33.get("address") != 27619968 or
            output33.get("length_bytes") != 86528 or
            not isinstance(params33, dict) or params33.get("stride") != 2 or
            params33.get("method") != "nearest_repeat"):
        raise AssertionError("T22 layer33 dispatch row 与 manifest 不一致")
    if (row34.get("cfg_section") != 35 or row34.get("op") != "route" or
            not isinstance(inputs34, list) or len(inputs34) != 2 or
            [item.get("source_index") for item in inputs34] != [33, 23] or
            [item.get("address") for item in inputs34] != [27619968, 26727936] or
            [item.get("length_bytes") for item in inputs34] != [86528, 173056] or
            [item.get("shape_nchw") for item in inputs34] != layer34["input_shape_nchw"] or
            [item.get("scale") for item in inputs34] != layer34["input_scales"] or
            not isinstance(output34, dict) or output34.get("address") != 27706496 or
            output34.get("length_bytes") != 259584 or
            output34.get("shape_nchw") != layer34["output_shape_nchw"] or
            not isinstance(params34, dict) or params34.get("route_groups") != 1 or
            params34.get("route_group_id") != 0 or
            params34.get("route_source_channel_ranges") != [[0, 128], [0, 256]]):
        raise AssertionError("T22 layer34 ref 顺序/per-ref scale/route range 与 manifest 不一致")

    t18_layer = t18.get("layer33", {})
    t18_golden = t18.get("golden", {})
    if (t18.get("task") != "S2A-T18" or t18.get("result") != "PASS" or
            t18.get("mode") != "FULL" or t18_layer.get("output_base_address") != 27619968 or
            t18_layer.get("output_length_bytes") != 86528 or
            t18_golden.get("expected_output_byte_count") != 86528 or
            t18_golden.get("expected_output_sha256") !=
            "39d1494ec1dfa28846aebfd56bff2396c5610c60873c99cae6186d8f3ea4a9ab"):
        raise AssertionError("T18 layer33 的完整仿真证据或 nearest-repeat hash 不符")

    t19_layer = t19.get("layer34", {})
    t19_golden = t19.get("golden", {})
    if (t19.get("task") != "S2A-T19" or t19.get("result") != "PASS" or
            t19.get("mode") != "FULL" or t19_layer.get("source_order") != [33, 23] or
            t19_layer.get("source0_base_address") != 27619968 or
            t19_layer.get("source0_length_bytes") != 86528 or
            t19_layer.get("source1_base_address") != 26727936 or
            t19_layer.get("source1_length_bytes") != 173056 or
            t19_layer.get("output_base_address") != 27706496 or
            t19_layer.get("output_length_bytes") != 259584 or
            t19_layer.get("source0_q31_multiplier") != 1959924335 or
            t19_layer.get("source1_q31_multiplier") != 2147483648 or
            t19_golden.get("seed") != _RANDOM_SEED or
            t19_golden.get("expected_output_sha256") !=
            "e0f76b78366b8af1c36fb5050f54e0e8ca8c0a6dc87852228a3a027bf219c8ad"):
        raise AssertionError("T19 route shape/order/Q31/hash evidence 不匹配")
    if (math.floor((layer34["input_scales"][0] / layer34["output_scale"]) * (1 << 31) + 0.5)
            != t19_layer["source0_q31_multiplier"] or
            math.floor((layer34["input_scales"][1] / layer34["output_scale"]) * (1 << 31) + 0.5)
            != t19_layer["source1_q31_multiplier"]):
        raise AssertionError("manifest per-ref scale 派生的 Q31 multiplier 与 T19 证据不一致")

    layer33_descriptor = {
        "layer_index": 33,
        "cfg_section": 34,
        "input_source_layer": 32,
        "input_address": int(layer32["tensor_address"]),
        "input_length_bytes": int(layer32["tensor_length_bytes"]),
        "input_shape_nchw": list(layer33["input_shape_nchw"]),
        "input_scale": float(layer33["input_scale"]),
        "output_address": int(layer33["tensor_address"]),
        "output_length_bytes": int(layer33["tensor_length_bytes"]),
        "output_shape_nchw": list(layer33["output_shape_nchw"]),
        "output_scale": float(layer33["output_scale"]),
        "stride": int(layer33["stride"]),
        "method": str(layer33["method"]),
        "layout": str(layer33["layout"]),
    }
    layer34_descriptor = {
        "layer_index": 34,
        "cfg_section": 35,
        "source_order": list(layer34["input_tensor_indices"]),
        "source_addresses": [int(layer33["tensor_address"]), int(layer23["tensor_address"])],
        "source_lengths_bytes": [int(layer33["tensor_length_bytes"]), int(layer23["tensor_length_bytes"])],
        "source_shapes_nchw": [list(item) for item in layer34["input_shape_nchw"]],
        "source_scales": [float(item) for item in layer34["input_scales"]],
        "legacy_single_input_scale": float(layer34["input_scale"]),
        "legacy_single_input_scale_semantics":
            "manifest generic sequential-predecessor field; route input_scales/order are authoritative",
        "output_address": int(layer34["tensor_address"]),
        "output_length_bytes": int(layer34["tensor_length_bytes"]),
        "output_shape_nchw": list(layer34["output_shape_nchw"]),
        "output_scale": float(layer34["output_scale"]),
        "groups": int(layer34["route_groups"]),
        "group_id": int(layer34["route_group_id"]),
        "source_channel_ranges": [list(item) for item in layer34["route_source_channel_ranges"]],
        "source_q31_multipliers": [1959924335, 2147483648],
        "layout": str(layer34["layout"]),
    }
    return layer33_descriptor, layer34_descriptor


def _xorshift32(state: int) -> int:
    """执行 32-bit xorshift PRNG 的冻结步进。"""
    state = (state ^ ((state << 13) & 0xFFFFFFFF)) & 0xFFFFFFFF
    state ^= state >> 17
    return (state ^ ((state << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF


def _seeded_values(seed: int, count: int) -> tuple[bytes, int]:
    """按 T19 规则产生有符号 INT8 合成张量字节。"""
    state = seed & 0xFFFFFFFF
    result = bytearray(count)
    for index in range(count):
        state = _xorshift32(state)
        result[index] = ((state % 255) - 127) & 0xFF
    if 0x80 in result:
        raise AssertionError("固定 PRNG 不得产生 raw -128 sentinel")
    return bytes(result), state


def _signed_int8(value: int) -> int:
    """把 byte 按 two's complement 解码为 signed INT8。"""
    return value - 256 if value >= 128 else value


def _requantize_q31(value: int, multiplier: int) -> int:
    """重现 T19 的有符号 Q31 最近舍入与 [-127,127] 饱和。"""
    magnitude = (abs(value) * multiplier + (1 << 30)) >> 31
    signed = -magnitude if value < 0 else magnitude
    return max(-127, min(127, signed))


def _requantize_float_reference(value: int, ratio: float) -> int:
    """以冻结 scale ratio 计算 half-away-from-zero 数学参考值。"""
    scaled = value * ratio
    rounded = math.floor(scaled + 0.5) if scaled >= 0 else math.ceil(scaled - 0.5)
    return max(-127, min(127, rounded))


def _materialize_golden(
    layer33: dict[str, Any], layer34: dict[str, Any], seed: int = _RANDOM_SEED,
) -> dict[str, bytes | int | str]:
    """构造 layer32、layer23 输入及独立 nearest-repeat/route 完整黄金。"""
    input32, state = _seeded_values(seed, int(layer33["input_length_bytes"]))
    input23, state = _seeded_values(state, int(layer34["source_lengths_bytes"][1]))
    _, _, input_height, input_width = layer33["input_shape_nchw"]
    _, channels, output_height, output_width = layer33["output_shape_nchw"]
    if (len(input32) != int(layer33["input_length_bytes"]) or
            len(input23) != int(layer34["source_lengths_bytes"][1]) or
            channels != 128 or input_height != 13 or input_width != 13 or
            output_height != 26 or output_width != 26):
        raise AssertionError("seeded input 或 layer33 NCHW shape/byte count 不一致")
    output33 = bytearray()
    for channel in range(channels):
        for y in range(output_height):
            for x in range(output_width):
                source_offset = (channel * input_height + y // 2) * input_width + x // 2
                output33.append(input32[source_offset])

    output34 = bytearray()
    multiplier0, multiplier1 = layer34["source_q31_multipliers"]
    for channel in range(384):
        source0 = channel < 128
        source = output33 if source0 else input23
        source_channel = channel if source0 else channel - 128
        multiplier = multiplier0 if source0 else multiplier1
        for pixel in range(26 * 26):
            offset = source_channel * 26 * 26 + pixel
            quantized = _requantize_q31(_signed_int8(source[offset]), multiplier)
            output34.append(quantized & 0xFF)

    expected33 = bytes(output33)
    expected34 = bytes(output34)
    if (len(expected33) != int(layer33["output_length_bytes"]) or
            len(expected34) != int(layer34["output_length_bytes"])):
        raise AssertionError("layer33/layer34 oracle byte count 不匹配冻结 NCHW tensor")
    return {
        "seed": seed,
        "final_prng_state": state,
        "layer32_input": input32,
        "layer23_input": input23,
        "layer33_expected": expected33,
        "layer34_expected": expected34,
        "layer32_sha256": _sha256_bytes(input32),
        "layer23_sha256": _sha256_bytes(input23),
        "layer33_sha256": _sha256_bytes(expected33),
        "layer34_sha256": _sha256_bytes(expected34),
        "combined_inputs_sha256": _sha256_bytes(input32 + input23),
        "combined_outputs_sha256": _sha256_bytes(expected33 + expected34),
    }


def _write_hex(path: Path, payload: bytes) -> None:
    """以独占创建方式写出 $readmemh 使用的逐 byte 十六进制 fixture。"""
    if path.exists():
        raise FileExistsError(f"临时 fixture 已存在，拒绝覆盖：{path}")
    with path.open("x", encoding="ascii", newline="\n") as target:
        target.write("".join(f"{value:02x}\n" for value in payload))


def _write_memory_ranges(manifest: dict[str, Any], work: Path) -> tuple[str, int]:
    """从 manifest 计算并保存 36 个非 alias feature 区间校验清单。"""
    ranges = sorted({
        (int(row["tensor_address"]),
         int(row["tensor_address"]) + int(row["tensor_length_bytes"]))
        for row in manifest["layers"] if row.get("op") != "yolo"
    })
    if len(ranges) != 36:
        raise AssertionError(f"manifest 非 alias feature range 数应为36，实为{len(ranges)}")
    for previous, current in zip(ranges, ranges[1:], strict=False):
        if previous[1] > current[0]:
            raise AssertionError("manifest feature tensor range 重叠")
    input_desc = manifest["address_map"]["input"]
    weights_desc = manifest["address_map"]["weight_package"]
    lines = [
        f"{int(input_desc['address']):08X} "
        f"{int(input_desc['address']) + int(input_desc['length_bytes']):08X} "
        f"{int(weights_desc['address']):08X} "
        f"{int(weights_desc['address']) + int(weights_desc['length_bytes']):08X} "
        f"{len(ranges):08X}\n"
    ]
    lines.extend(f"{start:08X} {end:08X}\n" for start, end in ranges)
    payload = "".join(lines).encode("ascii")
    target = work / "memory_ranges.dat"
    if target.exists():
        raise FileExistsError(f"临时 memory range 文件已存在：{target}")
    target.write_bytes(payload)
    return _sha256_bytes(payload), len(ranges)


def _verify_sources() -> tuple[dict[str, str], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """验证冻结 source/evidence 哈希并取得完整层规格与黄金。"""
    hashes: dict[str, str] = {}
    for relative_name, expected in _PINNED_HASHES.items():
        relative = Path(relative_name)
        raw = _repo_path(relative).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"冻结输入必须为 UTF-8/LF：{relative_name}")
        raw.decode("utf-8")
        actual = _sha256_bytes(raw)
        _assert_hash(relative_name, actual, expected)
        hashes[relative_name] = actual
    dynamic = (_WRAPPER, _TB, _RUNNER, _TEST)
    for relative in dynamic:
        raw = _repo_path(relative).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"本轮 T28 source 必须为 UTF-8/LF：{relative.as_posix()}")
        raw.decode("utf-8")
        hashes[relative.as_posix()] = _sha256_bytes(raw)

    manifest = _load_json(_MANIFEST)
    contract = _load_json(_T22)
    t18 = _load_json(_T18_EVIDENCE)
    t19 = _load_json(_T19_EVIDENCE)
    layer33, layer34 = _validate_contract(manifest, contract, t18, t19)
    return hashes, manifest, contract, t18, t19, {"layer33": layer33, "layer34": layer34}


def _tool_version(tool: Path) -> str:
    """读取 Vivado Simulator 可执行文件版本。"""
    command = f'cmd.exe /d /s /c "{tool} -version"'
    result = subprocess.run(
        command, shell=False, cwd=_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"{tool.name} -version exit={result.returncode}: {output[-1000:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise RuntimeError(f"无法解析 {tool.name} 版本：{output[-1000:]}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _command_text(tool: Path, args: list[str]) -> str:
    """生成 Windows cmd 运行和证据记录使用的精确命令。"""
    return " ".join(f'"{item}"' if (" " in item or "&" in item) else item
                     for item in [str(tool), *args])


def _terminate_tree(process: subprocess.Popen[str]) -> None:
    """超时后只终止本 runner 创建的工具进程树。"""
    if process.poll() is not None:
        return
    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                   capture_output=True, text=True, check=False)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _run_logged(
    tool: Path, args: list[str], work: Path, log_path: Path,
    deadline: float, progress_timeout: float | None = None,
) -> tuple[int, float, list[str]]:
    """执行单个 Vivado 阶段并将完整日志保存在唯一临时目录。"""
    command = _command_text(tool, args)
    started = time.monotonic()
    process = subprocess.Popen(
        f'cmd.exe /d /s /c "{command}"', shell=False, cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", bufsize=1,
    )
    messages: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            messages.put(line)
        messages.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    checkpoints: list[str] = []
    last_progress = started
    eof = False
    with log_path.open("x", encoding="utf-8", newline="\n") as log_file:
        while not eof or process.poll() is None:
            now = time.monotonic()
            if now - started > _TOTAL_TIMEOUT_SECONDS:
                _terminate_tree(process)
                raise TimeoutError(f"T28 全阶段运行超过 {_TOTAL_TIMEOUT_SECONDS}s：{log_path}")
            if progress_timeout is not None and now - last_progress > progress_timeout:
                _terminate_tree(process)
                raise TimeoutError(f"xsim {progress_timeout}s 无进度：{log_path}")
            try:
                line = messages.get(timeout=1)
            except queue.Empty:
                continue
            if line is None:
                eof = True
                continue
            log_file.write(line)
            log_file.flush()
            if line.startswith(("PROGRESS ", "CHECK ", "RESULT ", "PASS ")):
                print(line.rstrip(), flush=True)
                checkpoints.append(line.strip())
                if line.startswith(("PROGRESS ", "CHECK ", "RESULT ", "PASS ")):
                    last_progress = time.monotonic()
    reader.join(timeout=5)
    return int(process.wait()), time.monotonic() - started, checkpoints


def _assert_no_vivado_processes() -> None:
    """防止与已有 Vivado Simulator 工具进程并行运行。"""
    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                            text=True, encoding="utf-8", errors="replace", check=True)
    names = {line.split(",", 1)[0].strip('"').lower()
             for line in result.stdout.splitlines() if line.strip()}
    active = sorted(names.intersection({"vivado.exe", "xvlog.exe", "xelab.exe", "xsim.exe"}))
    if active:
        raise RuntimeError(f"检测到已有相关 Vivado 进程：{', '.join(active)}")


def _parse_result(log_path: Path, mode: str) -> dict[str, int]:
    """验证 xsim 唯一 result 行、PASS 标记和固定计数。"""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?im)^\s*(?:FAIL:|FATAL:|ERROR:)", text):
        raise AssertionError(f"xsim 日志含失败诊断：{log_path}")
    if mode == "quick":
        pattern = (r"RESULT mode=QUICK timeout_abort=(\d+) memory_error=(\d+) "
                   r"hard_reset=(\d+) soft_reset=(\d+) layer33_boundary=(\d+) "
                   r"route_start=(\d+) terminal_events=(\d+)")
        marker = "PASS S2A-T28 runtime shell layer33-to-layer34 control and boundary smoke"
        keys = ("timeout_abort", "memory_error", "hard_reset", "soft_reset",
                "layer33_boundary", "route_start", "terminal_events")
        expected = {"timeout_abort": 1, "memory_error": 1, "hard_reset": 1,
                    "soft_reset": 1, "layer33_boundary": 1, "route_start": 1,
                    "terminal_events": 0}
    else:
        pattern = (r"RESULT mode=FULL layer33_bytes=(\d+) layer34_bytes=(\d+) reads=(\d+) "
                   r"writes=(\d+) terminal_events=(\d+) stalls=(\d+) source0_reads=(\d+) "
                   r"source1_reads=(\d+) timeout_abort=(\d+) memory_error=(\d+) "
                   r"hard_reset=(\d+) soft_reset=(\d+) recovery=(\d+) "
                   r"global_timeout_cycles=(\d+) elapsed_task_cycles=(\d+) "
                   r"read_input_transactions=(\d+) read_weights_transactions=(\d+) "
                   r"read_feature_transactions=(\d+) read_feature_stall_cycles=(\d+) "
                   r"write_feature_transactions=(\d+) write_feature_stall_cycles=(\d+)")
        marker = "PASS S2A-T28 runtime shell serial layer33-to-layer34 pilot"
        keys = ("layer33_bytes", "layer34_bytes", "reads", "writes", "terminal_events",
                "stalls", "source0_reads", "source1_reads", "timeout_abort",
                "memory_error", "hard_reset", "soft_reset", "recovery",
                "global_timeout_cycles", "elapsed_task_cycles",
                "read_input_transactions", "read_weights_transactions",
                "read_feature_transactions", "read_feature_stall_cycles",
                "write_feature_transactions", "write_feature_stall_cycles")
        expected = {
            "layer33_bytes": 86528,
            "layer34_bytes": 259584,
            "reads": 346112,
            "writes": 346112,
            "terminal_events": 1,
            "source0_reads": 86528,
            "source1_reads": 173056,
            "timeout_abort": 1,
            "memory_error": 1,
            "hard_reset": 1,
            "soft_reset": 1,
            "recovery": 1,
            "global_timeout_cycles": 8000000,
            "read_input_transactions": 0,
            "read_weights_transactions": 0,
            "read_feature_transactions": 346112,
            "write_feature_transactions": 346112,
        }
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1 or text.count(marker) != 1 or matches[0].end() > text.index(marker):
        raise AssertionError(f"xsim result 或 PASS 标记缺失/重复：{log_path}")
    values = dict(zip(keys, map(int, matches[0].groups()), strict=True))
    for name, expected_value in expected.items():
        if values[name] != expected_value:
            raise AssertionError(f"xsim {name}={values[name]}，应为 {expected_value}")
    if mode == "full" and values["stalls"] <= 0:
        raise AssertionError("memory responder 没有覆盖 backpressure")
    if mode == "full" and values["stalls"] != (
        values["read_feature_stall_cycles"] + values["write_feature_stall_cycles"]
    ):
        raise AssertionError("总 ready-low 周期与 READ_FEATURE/WRITE_FEATURE 分类统计不符")
    if mode == "full" and not (0 < values["elapsed_task_cycles"] < values["global_timeout_cycles"]):
        raise AssertionError("整网两层任务未在唯一 G0 deadline 内完成")
    return values


def _verify_trace(path: Path, expected: bytes) -> tuple[str, str, int]:
    """读取逐 byte trace 并与 Python 独立 tensor golden 比较。"""
    if not path.is_file():
        raise AssertionError(f"xsim 未生成 trace：{path.name}")
    lines = path.read_text(encoding="ascii").splitlines()
    if len(lines) != len(expected) or any(not re.fullmatch(r"[0-9a-fA-F]{2}", row) for row in lines):
        raise AssertionError(f"trace byte count/format 错误：{path.name} lines={len(lines)}")
    observed = bytes(int(row, 16) for row in lines)
    mismatch = next((index for index, (actual, golden) in enumerate(
        zip(observed, expected, strict=True)) if actual != golden), None)
    if mismatch is not None:
        raise AssertionError(
            f"{path.name} golden mismatch offset={mismatch} "
            f"actual={observed[mismatch]:02x} expected={expected[mismatch]:02x}"
        )
    trace_sha = _sha256_file(path)
    return _sha256_bytes(observed), trace_sha, len(observed)


def run(mode: str) -> dict[str, Any]:
    """运行 QUICK 控制检查或完整 layer33→34 shell-child 集成仿真。"""
    if mode not in {"quick", "full"}:
        raise ValueError(f"未知仿真模式：{mode}")
    evidence_dir = _ROOT / _EVIDENCE_DIR
    evidence_path = _ROOT / _EVIDENCE
    existing_evidence_sha256: str | None = None
    if mode == "full" and evidence_path.exists():
        if not evidence_path.is_file():
            raise FileExistsError(f"T28 evidence 目标不是普通文件：{_EVIDENCE.as_posix()}")
        existing_evidence_sha256 = _sha256_file(evidence_path)
        _assert_hash(
            _EVIDENCE.as_posix(), existing_evidence_sha256,
            _REPLACEABLE_PREVIOUS_EVIDENCE_SHA256,
        )
    elif mode == "full" and evidence_dir.exists():
        raise FileExistsError(f"拒绝覆盖已有 T28 evidence 目录：{_EVIDENCE_DIR.as_posix()}")
    if mode == "full" and not (_ROOT / _EVIDENCE_DIR.parent).is_dir():
        raise FileNotFoundError(f"T28 evidence 精确父目录不存在：{_EVIDENCE_DIR.parent.as_posix()}")

    started = time.monotonic()
    deadline = started + _TOTAL_TIMEOUT_SECONDS
    bindings, manifest, contract, t18, t19, descriptors = _verify_sources()
    layer33 = descriptors["layer33"]
    layer34 = descriptors["layer34"]
    golden = _materialize_golden(layer33, layer34)
    _assert_no_vivado_processes()

    tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
    for path in tools.values():
        if not path.is_file():
            raise FileNotFoundError(f"Vivado Simulator executable 不存在：{path}")
    versions = {name: _tool_version(path) for name, path in tools.items()}
    if any("2026.1" not in version for version in versions.values()):
        raise AssertionError(f"Vivado Simulator 版本与固定T18/T19证据不符：{versions}")

    work_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t28_layers33_34_{mode}_", dir=work_parent))
    try:
        if os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) == str(_ROOT.resolve()):
            raise RuntimeError(f"Vivado 临时目录不能位于仓库内：{work}")
    except ValueError:
        pass
    _write_hex(work / "layer32_seed.hex", golden["layer32_input"])
    _write_hex(work / "layer23_seed.hex", golden["layer23_input"])
    _write_hex(work / "expected_layer33.hex", golden["layer33_expected"])
    _write_hex(work / "expected_layer34.hex", golden["layer34_expected"])
    range_sha, range_count = _write_memory_ranges(manifest, work)

    sources = [
        _repo_path(_UPSAMPLE_QUERY), _repo_path(_UPSAMPLE_ENGINE),
        _repo_path(_UPSAMPLE_SCHEDULER), _repo_path(_ROUTE_QUERY),
        _repo_path(_ROUTE_ENGINE), _repo_path(_ROUTE_SCHEDULER),
        _repo_path(_CSR), _repo_path(_T12_MASTER), _repo_path(_SHELL),
        _repo_path(_WRAPPER), _repo_path(_TB),
    ]
    precompile_bindings, _, _, _, _, precompile_descriptors = _verify_sources()
    _assert_source_snapshot_equal(bindings, precompile_bindings, "before xvlog")
    if precompile_descriptors != descriptors:
        raise AssertionError("编译前 layer descriptor 与初始验证结果变化")
    bindings = precompile_bindings
    compile_sources = _copy_compilation_sources(sources, bindings, work)
    phases: list[dict[str, Any]] = []
    compile_commands = [
        ("xvlog", ["-sv", *[str(path) for path in compile_sources]]),
        ("xelab", ["-top", "tb_s2a_runtime_layers33_34_pilot",
                   "-snapshot", "s2a_runtime_layers33_34_pilot_snapshot"]),
    ]
    for phase, args in compile_commands:
        log_path = work / f"{phase}_command.log"
        exit_code, elapsed, checkpoints = _run_logged(
            tools[phase], args, work, log_path, deadline,
        )
        phases.append({
            "phase": phase,
            "exit_code": exit_code,
            "elapsed_seconds": round(elapsed, 3),
            "log_file_name": log_path.name,
            "command": _command_text(tools[phase], args),
            "checkpoints": checkpoints,
        })
        if exit_code != 0:
            raise RuntimeError(f"{phase} exit={exit_code}; full log={log_path}")

    sim_args = ["-R", "s2a_runtime_layers33_34_pilot_snapshot"]
    if mode == "quick":
        sim_args.extend(["-testplusarg", "QUICK"])
    sim_log = work / "xsim_command.log"
    sim_exit, sim_elapsed, checkpoints = _run_logged(
        tools["xsim"], sim_args, work, sim_log, deadline,
        progress_timeout=_NO_PROGRESS_SECONDS,
    )
    phases.append({
        "phase": "xsim",
        "exit_code": sim_exit,
        "elapsed_seconds": round(sim_elapsed, 3),
        "log_file_name": sim_log.name,
        "command": _command_text(tools["xsim"], sim_args),
        "checkpoints": checkpoints,
        "no_progress_stop_seconds": _NO_PROGRESS_SECONDS,
    })
    if sim_exit != 0:
        raise RuntimeError(f"xsim exit={sim_exit}; full log={sim_log}")
    summary = _parse_result(sim_log, mode)

    observed: dict[str, Any] | None = None
    if mode == "full":
        observed33_sha, trace33_sha, count33 = _verify_trace(
            work / _TRACE33, golden["layer33_expected"]
        )
        observed34_sha, trace34_sha, count34 = _verify_trace(
            work / _TRACE34, golden["layer34_expected"]
        )
        observed = {
            "layer33": {
                "byte_count": count33,
                "expected_sha256": golden["layer33_sha256"],
                "observed_sha256": observed33_sha,
                "hex_trace_sha256": trace33_sha,
                "comparison": "逐 byte 对完整 86,528-byte NCHW nearest-repeat tensor 比较",
            },
            "layer34": {
                "byte_count": count34,
                "expected_sha256": golden["layer34_sha256"],
                "observed_sha256": observed34_sha,
                "hex_trace_sha256": trace34_sha,
                "comparison": "逐 byte 对完整 259,584-byte NCHW route/concat tensor 比较",
            },
        }

    after_bindings, _, _, _, _, after_descriptors = _verify_sources()
    _assert_source_snapshot_equal(bindings, after_bindings, "during compile/simulation")
    if after_descriptors != descriptors:
        raise AssertionError("运行期间 layer descriptor 发生变化")
    elapsed = round(time.monotonic() - started, 3)
    result: dict[str, Any] = {
        "schema_version": "gestureforge_s2a_t28_runtime_layers33_34_shell_pilot_v1",
        "task_id": "S2A-T28",
        "result": "PASS",
        "mode": mode.upper(),
        "scope": "固定tiny416 layer33→34串行runtime-shell pilot；不是通用38层dispatcher，不代表G4/G5",
        "source_bindings": [
            {"path": name, "sha256": digest}
            for name, digest in sorted(bindings.items())
        ],
        "dispatch": {
            "start_event": "G0接受一次backend_start后只启动layer33 scheduler",
            "layer33_to_layer34": "layer33完成不生成operator_result_valid；确认layer33完成后才启动layer34",
            "terminal_event": "layer34成功或任一算子失败产生无backpressure内部终态；正常全网pilot恰有一个终态事件",
            "global_deadline": "唯一G0 whole-task timeout；层切换不重启计数，无child-local timeout",
            "global_deadline_cycles": summary.get("global_timeout_cycles"),
            "observed_task_elapsed_cycles": summary.get("elapsed_task_cycles"),
            "child_order": [33, 34],
            "shared_memory_master": "冻结T12单outstanding master；仅active child可驱动G0 shell memory request/response",
        },
        "layer33": layer33,
        "layer34": layer34,
        "golden": {
            "generator": "连续xorshift32固定seed；每步state%255-127；先NCHW layer32后NCHW layer23",
            "seed": golden["seed"],
            "final_prng_state": golden["final_prng_state"],
            "layer32_input_bytes": len(golden["layer32_input"]),
            "layer32_input_sha256": golden["layer32_sha256"],
            "layer23_input_bytes": len(golden["layer23_input"]),
            "layer23_input_sha256": golden["layer23_sha256"],
            "combined_inputs_sha256": golden["combined_inputs_sha256"],
            "layer33_expected_bytes": len(golden["layer33_expected"]),
            "layer33_expected_sha256": golden["layer33_sha256"],
            "layer34_expected_bytes": len(golden["layer34_expected"]),
            "layer34_expected_sha256": golden["layer34_sha256"],
            "combined_expected_outputs_sha256": golden["combined_outputs_sha256"],
            "layer33_oracle": "NCHW nearest-repeat stride2；每个byte按[c,y//2,x//2]复制",
            "layer34_oracle": "manifest refs顺序[33,23]；T19冻结Q31 multiplier、整数half-away rounding、signed INT8饱和[-127,127]",
            "minus_128_inputs": 0,
            "observed": observed,
        },
        "memory_responder": {
            "implementation": "direct-index TB responder, not T10 instance",
            "t10_source_binding_role": "冻结T10 SHA用于逐项对照；仿真不实例化T10 sparse patch model",
            "stall_schedule_by_t10_class": {
                "READ_INPUT_0": [0, 1, 2, 7, 3],
                "READ_WEIGHTS_1": [0, 1, 2, 7, 3],
                "READ_FEATURE_2": [0, 1, 2, 7, 3],
                "WRITE_FEATURE_3": [0, 1, 2, 7, 3],
            },
            "accepted_transactions_by_t10_class": {
                "READ_INPUT_0": summary.get("read_input_transactions"),
                "READ_WEIGHTS_1": summary.get("read_weights_transactions"),
                "READ_FEATURE_2": summary.get("read_feature_transactions"),
                "WRITE_FEATURE_3": summary.get("write_feature_transactions"),
            },
            "observed_ready_low_rising_edges_by_t10_class": {
                "READ_INPUT_0": 0 if mode == "full" else None,
                "READ_WEIGHTS_1": 0 if mode == "full" else None,
                "READ_FEATURE_2": summary.get("read_feature_stall_cycles"),
                "WRITE_FEATURE_3": summary.get("write_feature_stall_cycles"),
            },
            "sequence_state": "每类 stall index 从0开始；仅 accepted transaction 后加一；hard reset、soft reset和cancel不清零",
            "semantics_asserted": [
                "32-bit word address aligned to 4 bytes",
                "single active byte lane for each read or write; read/write strobes mutually exclusive",
                "single outstanding T12 transaction; responder accepts only the held current request",
                "address and data/strobes/fault fields remain stable for every stalled request cycle",
                "read data and error code are presented with accepted ready/valid response",
                "reads restricted to layer32, layer33, and layer23 frozen input ranges",
                "writes restricted to sequential layer33 and layer34 output ranges; input writes rejected",
                "unknown or uninitialized layer33 source bytes rejected",
                "layer32/layer33/layer23 activation reads map to T10 READ_FEATURE class 2",
                "layer33/layer34 output writes map to T10 WRITE_FEATURE class 3",
                "no READ_INPUT class 0 or READ_WEIGHTS class 1 request is accepted",
                "delay=0 is ready-high before the first accepting rising edge",
                "delay=N>0 counts exactly N ready-low rising edges before acceptance",
                "every accepted request asserts its class and observed low-ready edge count against T10 schedule",
                "per-class stall index advances only on acceptance and persists through cancel and reset",
                "hard reset, accepted soft reset, G0 abort/timeout cancel pending request before side effect",
            ],
            "feature_range_count_from_manifest": range_count,
            "manifest_ranges_sha256": range_sha,
        },
        "control_and_memory": {
            "ps_visible_abi": "原样实例化G0 s2a_runtime_shell；不修改CSR、register、memory或timeout语义",
            "serial_backend": "一次G0 backend_start；layer33与layer34各成功start握手一次；只layer34正常完成产生terminal event",
            "busy_start": "full仿真在layer34 active期间写G0 CMD.start并确认busy状态未重复启动",
            "error_and_abort": "G0 global timeout与memory error分别停止下游child；hard/soft reset及abort无迟到读写副作用",
        },
        "simulation": {
            "summary": summary,
            "tool_versions": versions,
            "phases": phases,
            "temporary_log_directory_name": work.name,
            "elapsed_seconds": elapsed,
            "overall_timeout_seconds": _TOTAL_TIMEOUT_SECONDS,
            "no_progress_stop_seconds": _NO_PROGRESS_SECONDS,
        },
        "synthesis": "NOT_EXECUTED：本固定两层shell-child pilot没有运行综合或资源估算",
        "board_validation": "NOT_APPLICABLE：未操作板卡、未烧录、未运行Vitis",
        "g4_status": "NOT_MET",
        "g5_status": "NOT_MET",
    }
    if mode == "full":
        if existing_evidence_sha256 is None and (evidence_dir.exists() or evidence_path.exists()):
            raise FileExistsError(f"仿真结束时T28 evidence目标已存在，拒绝覆盖：{_EVIDENCE_DIR}")
        if existing_evidence_sha256 is not None:
            _assert_hash(
                _EVIDENCE.as_posix(), _sha256_file(evidence_path),
                existing_evidence_sha256,
            )
        payload = _write_verified_evidence(
            evidence_path, result, bindings, after_bindings,
            expected_existing_sha256=existing_evidence_sha256,
        )
        result["evidence_path"] = _EVIDENCE.as_posix()
        result["evidence_sha256"] = _sha256_bytes(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    """解析执行模式并返回可由 shell 检查的退出码。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), required=True)
    args = parser.parse_args()
    try:
        run(args.mode)
    except Exception as exc:
        print(f"FAIL S2A-T28 mode={args.mode}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
