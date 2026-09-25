"""运行 S2A-T20 tiny416 layer36 固定卷积层调度器验证。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import queue
import re
import struct
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "b42bde6cd9ccbb8613239fb003f5b4f9687b8c33"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_D2_FORWARD = _ROOT / "verification/s1_t02_d2_int8_forward.py"
_T16_PROOF = _ROOT / "report/evidence/S2A-T16/conv_requant_proof.json"
_T16_SCRIPT = _ROOT / "verification/s2a_conv_requant_proof.py"
_T17_ENGINE = _ROOT / "src/s2a_conv_engine.sv"
_T17_GEOMETRY = _ROOT / "src/int8_conv_tap_geometry.sv"
_T17_WEIGHT_ADDRESS = _ROOT / "src/int8_conv_weight_address.sv"
_T17_MAC = _ROOT / "src/int8_mac_accumulator.sv"
_T17_TB = _ROOT / "sim/tb_s2a_conv_engine.sv"
_T17_RUNNER = _ROOT / "verification/test_s2a_conv_engine_rtl.py"
_T17_EVIDENCE = _ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json"
_T10_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_T11_EVIDENCE = _ROOT / "report/evidence/S2A-T11/control_csr_simulation.json"
_T12_MASTER = _ROOT / "src/s2a_memory_master.sv"
_T12_EVIDENCE = _ROOT / "report/evidence/S2A-T12/runtime_protocol_simulation.json"
_T19_SCHEDULER = _ROOT / "src/s2a_route_layer_scheduler.sv"
_T19_TB = _ROOT / "sim/tb_s2a_route_layer_scheduler.sv"
_T19_RUNNER = _ROOT / "verification/test_s2a_route_layer_scheduler_rtl.py"
_T19_EVIDENCE = _ROOT / "report/evidence/S2A-T19/route_layer_scheduler_simulation.json"
_SCHEDULER = _ROOT / "src/s2a_conv_layer_scheduler.sv"
_TB = _ROOT / "sim/tb_s2a_conv_layer_scheduler.sv"
_RUNNER = Path(__file__).resolve()
_EVIDENCE = _ROOT / "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")

_INPUT_BASE = 27966080
_INPUT_BYTES = 173056
_INPUT_CHANNELS = 256
_HEIGHT = 26
_WIDTH = 26
_K = 256
_WEIGHT_BASE = 1048576
_WEIGHT_OFFSET = 5895420
_WEIGHT_BYTES = 7680
_WEIGHT_PACKAGE_BYTES = 5903100
_OUTPUT_BASE = 28139136
_OUTPUT_BYTES = 20280
_OUTPUT_CHANNELS = 30
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_OVERALL_TIMEOUT_SECONDS = 14400
_NO_PROGRESS_TIMEOUT_SECONDS = 900
_MAX_FEATURE_RANGES = 36

_FIXED_HASHES = {
    "g0_spec": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "d2_forward": "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393",
    "t16_proof": "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24",
    "t16_script": "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9",
    "t17_engine": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "t17_geometry": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "t17_weight_address": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "t17_mac": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "t17_testbench": "2b642eb47cded4644e4e9ba3a1e3fa60d484cf795ec6e51dd8d4cfcc97d2f001",
    "t17_runner": "adbb7e2574c50fd8e702e386a0898d27a0e4a16aebfc782436e386d56c768357",
    "t17_evidence": "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2",
    "t10_model": "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
    "t12_master": "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    "t11_evidence": "b24558e55f65b2c7a11d85ba81ed923b07e0689a1712275d490908104bbabc90",
    "t12_evidence": "332e038d85f27366b9692e4a4aeaa4933fcec9a22d64c2f9b905fe7978dcd01d",
    "t19_scheduler": "ff078b830f76ca12baaa307e65f90958c0d0938fd0d1a4489955c2021a5d94d1",
    "t19_testbench": "63a82b0b74e68874ff24810e9598a9d0c1b536bb2da4fd2aaa008ee6e5ff8755",
    "t19_runner": "9c84dee53e87333f991f2536a0d98719ad3e3964ea095e12ce069406c846bbc0",
    "t19_evidence": "e3921f382fc8c6af3dea5ec9edf3fd9795a49e09982381e2501ad8d9aa592880",
}


class T20Error(RuntimeError):
    """报告冻结引用、黄金数据或 RTL 仿真失败。"""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _frozen_paths() -> dict[str, Path]:
    """列出 G0、前序任务实现与验收证据。"""
    return {
        "g0_spec": _G0_SPEC,
        "manifest": _MANIFEST,
        "d2_forward": _D2_FORWARD,
        "t16_proof": _T16_PROOF,
        "t16_script": _T16_SCRIPT,
        "t17_engine": _T17_ENGINE,
        "t17_geometry": _T17_GEOMETRY,
        "t17_weight_address": _T17_WEIGHT_ADDRESS,
        "t17_mac": _T17_MAC,
        "t17_testbench": _T17_TB,
        "t17_runner": _T17_RUNNER,
        "t17_evidence": _T17_EVIDENCE,
        "t10_model": _T10_MODEL,
        "t11_evidence": _T11_EVIDENCE,
        "t12_master": _T12_MASTER,
        "t12_evidence": _T12_EVIDENCE,
        "t19_scheduler": _T19_SCHEDULER,
        "t19_testbench": _T19_TB,
        "t19_runner": _T19_RUNNER,
        "t19_evidence": _T19_EVIDENCE,
    }


def _load_t17_runner():
    """导入 T17 冻结 helper，用其 GF8 parser 与 T16 参数核验逻辑。"""
    sys.path.insert(0, str((_ROOT / "verification").resolve()))
    spec = importlib.util.spec_from_file_location("s2a_t17_conv_engine_runner", _T17_RUNNER)
    if spec is None or spec.loader is None:
        raise T20Error("不能加载已冻结的 T17 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _round_half_away(value: float) -> int:
    magnitude = math.floor(abs(value) + 0.5)
    return -magnitude if value < 0 else magnitude


def _read_frozen_spec() -> tuple[str, dict[str, str], dict, dict, bytes, list[dict[str, int]], Path]:
    """校验固定规格，解析真实 GF8 片段并重建 T16 通道参数。"""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
        text=True, encoding="utf-8", check=True,
    ).stdout.strip()
    if head != _BASELINE_HEAD:
        raise T20Error(f"T20 baseline HEAD 不符：{head}")

    frozen_paths = _frozen_paths()
    hashes = {name: _sha256_file(path) for name, path in frozen_paths.items()}
    for name, expected in _FIXED_HASHES.items():
        if expected and hashes[name] != expected:
            raise T20Error(f"冻结依赖 {name} SHA-256 不符：{hashes[name]}")

    t19_evidence = json.loads(_T19_EVIDENCE.read_text(encoding="utf-8"))
    t19_bindings = t19_evidence.get("bindings", {})
    for path_key, evidence_key in (
        ("t19_scheduler", "scheduler_rtl"),
        ("t19_testbench", "testbench"),
        ("t19_runner", "runner"),
    ):
        if t19_bindings.get(evidence_key) != hashes[path_key]:
            raise T20Error(f"T19 evidence {evidence_key} hash 与文件不一致")

    t17 = _load_t17_runner()
    manifest, proof, all_weights, package_path = t17._load_bound_inputs()
    layers = {int(row["layer_index"]): row for row in manifest["layers"]}
    layer = layers[36]
    source = layers[35]
    expected_layer = {
        "cfg_section": 37,
        "op": "convolutional",
        "input_tensor_indices": [35],
        "input_shape_nchw": [1, 256, 26, 26],
        "input_scale": 0.12693486251230315,
        "layout": "NCHW",
        "element_type": "int8_twos_complement",
        "kernel_hw": [1, 1],
        "stride_hw": [1, 1],
        "padding_lrtb": [0, 0, 0, 0],
        "groups": 1,
        "padding_value_int8": 0,
        "activation": "linear",
        "accumulator_bits": 32,
        "output_scale": 0.30223452951025775,
        "weight_layer_index": 36,
        "output_shape_nchw": [1, 30, 26, 26],
        "tensor_address": _OUTPUT_BASE,
        "tensor_length_bytes": _OUTPUT_BYTES,
    }
    for name, expected in expected_layer.items():
        if layer.get(name) != expected:
            raise T20Error(f"T01 layer36 {name}={layer.get(name)!r}，期望 {expected!r}")
    if (source.get("tensor_address") != _INPUT_BASE or
            source.get("tensor_length_bytes") != _INPUT_BYTES or
            source.get("output_shape_nchw") != [1, 256, 26, 26] or
            source.get("output_scale") != layer["input_scale"]):
        raise T20Error("layer35 到 layer36 的输入地址、尺寸或 scale 不符合 T01")
    if _OUTPUT_BASE + _OUTPUT_BYTES != 28159416:
        raise T20Error("layer36 输出半开区间末端核算不符")

    weight_map = manifest["address_map"]["weight_package"]
    offsets = layer["gf8_parameter_offsets"]
    if (int(weight_map["address"]) != _WEIGHT_BASE or
            int(weight_map["length_bytes"]) != _WEIGHT_PACKAGE_BYTES or
            int(offsets["quantized_weight_offset"]) != _WEIGHT_OFFSET or
            int(offsets["quantized_weight_bytes"]) != _WEIGHT_BYTES):
        raise T20Error("T01 layer36 GF8 权重映射与固定层参数不符")
    weight_end = _WEIGHT_BASE + _WEIGHT_OFFSET + _WEIGHT_BYTES
    if (_WEIGHT_BASE + _WEIGHT_OFFSET != 0x0069F4FC or
            weight_end != 0x006A12FC):
        raise T20Error("layer36 GF8 权重绝对半开区间核算不符")

    proof_layers = {int(row["layer_index"]): row for row in proof["layers"]}
    parameters = t17._candidate_parameters(layer, proof_layers[36])
    if len(parameters) != _OUTPUT_CHANNELS:
        raise T20Error("T16 layer36 通道参数数量不是30")

    package = package_path.read_bytes()
    package_sha = _sha256_bytes(package)
    if (len(package) != _WEIGHT_PACKAGE_BYTES or
            package_sha != weight_map["sha256"] or
            package_sha != "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"):
        raise T20Error("T01 绑定 GFINT8W1 包长度或 SHA-256 不符")
    package_scales = struct.unpack_from("<30f", package, int(offsets["weight_scale_offset"]))
    package_biases = struct.unpack_from("<30f", package, int(offsets["fused_bias_offset"]))
    if tuple(package_scales) != tuple(map(float, layer["weight_scale_per_output_channel"])):
        raise T20Error("layer36 GF8 weight_scale_per_output_channel 与 T01 不一致")
    if tuple(package_biases) != tuple(map(float, layer["fused_bias_float32_per_output_channel"])):
        raise T20Error("layer36 GF8 fused_bias_float32_per_output_channel 与 T01 不一致")
    expected_biases = list(map(int, layer["bias_accumulator_int32_per_output_channel"]))
    input_scale = float(layer["input_scale"])
    rebuilt_biases = []
    for scale, fused_bias in zip(package_scales, package_biases, strict=True):
        denominator = t17.np.float64(input_scale) * t17.np.float64(scale)
        accumulator_bias = _round_half_away(float(t17.np.float64(fused_bias) / denominator))
        rebuilt_biases.append(accumulator_bias)
    if rebuilt_biases != expected_biases:
        raise T20Error("GF8 fused bias 按 T01 half-away 规则重建的 INT32 bias 不一致")

    layer_weights = all_weights[36]
    if len(layer_weights) != _WEIGHT_BYTES:
        raise T20Error("T17 GF8 parser 提取的 layer36 权重长度不符")
    return head, hashes, manifest, layer, layer_weights, parameters, package_path


def _initial_byte(address: int) -> int:
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _input_fixture() -> tuple[bytes, list[int]]:
    """按 T10 地址异或公式产生 layer35 输入并修正 raw -128 sentinel。"""
    result = bytearray()
    sentinel_offsets: list[int] = []
    for offset in range(_INPUT_BYTES):
        value = _initial_byte(_INPUT_BASE + offset)
        if value == 0x80:
            value = 0
            sentinel_offsets.append(offset)
        result.append(value)
    if len(sentinel_offsets) != 675:
        raise T20Error(f"T10 input fixture raw -128 数量不符：{len(sentinel_offsets)}")
    return bytes(result), sentinel_offsets


def _input_and_golden(layer: dict, weights: bytes,
                      parameters: list[dict[str, int]], t17) -> tuple[bytes, bytes, dict[str, int]]:
    """独立逐 tap INT32 累加，再按 T16 integer M/Q 产生 layer36 完整 golden。"""
    input_bytes, _sentinels = _input_fixture()
    signed_input = [t17._signed_byte(value) for value in input_bytes]
    output = bytearray()
    accumulator_min = (1 << 31) - 1
    accumulator_max = -(1 << 31)
    d2_checked = 0
    for channel in range(_OUTPUT_CHANNELS):
        channel_weights = [
            t17._signed_byte(value)
            for value in weights[channel * _K:(channel + 1) * _K]
        ]
        bias = int(layer["bias_accumulator_int32_per_output_channel"][channel])
        params = parameters[channel]
        for pixel in range(_HEIGHT * _WIDTH):
            accumulator = bias
            for reduction_index, weight in enumerate(channel_weights):
                activation = signed_input[reduction_index * (_HEIGHT * _WIDTH) + pixel]
                accumulator += activation * weight
                if not -(1 << 31) <= accumulator <= (1 << 31) - 1:
                    raise T20Error(
                        f"layer36 INT32 accumulation overflow c={channel} p={pixel} k={reduction_index}"
                    )
            accumulator_min = min(accumulator_min, accumulator)
            accumulator_max = max(accumulator_max, accumulator)
            integer_value = t17._fixed_point_quantize(accumulator, params)
            d2_value = t17._d2_quantize(
                accumulator,
                float(layer["input_scale"]),
                float(layer["weight_scale_per_output_channel"][channel]),
                float(layer["output_scale"]),
                "linear",
            )
            if integer_value != d2_value:
                raise T20Error(
                    f"layer36 T16/D2 mismatch c={channel} p={pixel}: {integer_value}!={d2_value}"
                )
            output.append(integer_value & 0xFF)
            d2_checked += 1
    if len(output) != _OUTPUT_BYTES or d2_checked != _OUTPUT_BYTES:
        raise T20Error("layer36 CPU golden 输出 byte 数量错误")
    return input_bytes, bytes(output), {
        "int32_accumulator_min": accumulator_min,
        "int32_accumulator_max": accumulator_max,
        "d2_float_cross_checks": d2_checked,
    }


def _write_hex_file(path: Path, payload: bytes) -> None:
    path.write_text("".join(f"{value:02x}\n" for value in payload),
                    encoding="ascii", newline="\n")


def _write_memory_ranges(manifest: dict, work: Path) -> tuple[str, int]:
    """按 T01 manifest 建立 T10 输入、权重与 feature 半开区间。"""
    ranges = sorted({
        (int(row["tensor_address"]),
         int(row["tensor_address"]) + int(row["tensor_length_bytes"]))
        for row in manifest["layers"] if row.get("op") != "yolo"
    })
    if len(ranges) != _MAX_FEATURE_RANGES:
        raise T20Error(f"T10 feature tensor ranges 数量不符：{len(ranges)}")
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise T20Error("T01 feature tensor address ranges 重叠")
    input_desc = manifest["address_map"]["input"]
    weight_desc = manifest["address_map"]["weight_package"]
    lines = [
        f"{int(input_desc['address']):08X} "
        f"{int(input_desc['address']) + int(input_desc['length_bytes']):08X} "
        f"{int(weight_desc['address']):08X} "
        f"{int(weight_desc['address']) + int(weight_desc['length_bytes']):08X} "
        f"{len(ranges):08X}\n"
    ]
    lines.extend(f"{start:08X} {end:08X}\n" for start, end in ranges)
    payload = "".join(lines).encode("ascii")
    (work / "memory_ranges.dat").write_bytes(payload)
    return _sha256_bytes(payload), len(ranges)


def _source_hashes() -> dict[str, str]:
    """绑定本轮 RTL、testbench 和 runner 的 UTF-8/LF 内容。"""
    result = {}
    for name, path in (("t20_scheduler", _SCHEDULER), ("t20_testbench", _TB),
                       ("t20_runner", _RUNNER)):
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise T20Error(f"T20 source 不是 UTF-8/LF：{path}")
        raw.decode("utf-8")
        result[name] = _sha256_bytes(raw)
    return result


def _tool_version(tool: Path) -> str:
    command = f'cmd.exe /d /s /c "{tool} -version"'
    result = subprocess.run(command, shell=False, cwd=_ROOT, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=30)
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        raise T20Error(f"{tool.name} -version exit={result.returncode}: {output[-1000:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise T20Error(f"无法解析 {tool.name} 版本：{output[-1000:]}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _command_text(tool: Path, args: list[str]) -> str:
    parts = [str(tool), *args]
    return " ".join(f'"{part}"' if (" " in part or "&" in part) else part
                    for part in parts)


def _terminate_process_tree(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is None:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, text=True, check=False)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def _run_logged(tool: Path, args: list[str], work: Path, log_path: Path,
                deadline: float, progress_timeout: int | None = None
                ) -> tuple[int, float, list[str]]:
    command = _command_text(tool, args)
    proc = subprocess.Popen(
        f'cmd.exe /d /s /c "{command}"', shell=False, cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", bufsize=1,
    )
    messages: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            messages.put(line)
        messages.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    started = time.monotonic()
    last_progress = started
    checkpoints: list[str] = []
    eof = False
    with log_path.open("w", encoding="utf-8", newline="\n") as log_file:
        while not eof or proc.poll() is None:
            now = time.monotonic()
            if now > deadline:
                _terminate_process_tree(proc)
                raise TimeoutError(f"T20 全局时限到期；日志：{log_path}")
            if progress_timeout is not None and now - last_progress > progress_timeout:
                _terminate_process_tree(proc)
                raise TimeoutError(f"xsim 超过 {progress_timeout}s 无进度；日志：{log_path}")
            try:
                line = messages.get(timeout=1)
            except queue.Empty:
                continue
            if line is None:
                eof = True
                continue
            log_file.write(line)
            log_file.flush()
            if line.startswith("PROGRESS "):
                checkpoints.append(line.strip())
                last_progress = time.monotonic()
                print(line.rstrip(), flush=True)
    reader.join(timeout=5)
    return int(proc.wait()), time.monotonic() - started, checkpoints


def _parse_summary(log_path: Path, mode: str) -> dict[str, int]:
    content = log_path.read_text(encoding="utf-8", errors="replace")
    marker = "PASS S2A-T20 focused smoke" if mode == "smoke" else \
             "PASS S2A-T20 complete tiny416 layer36 convolution scheduler"
    if content.count(marker) != 1 or content.count("RESULT mode=") != 1:
        raise T20Error(f"xsim RESULT/PASS 标记不唯一：{log_path}")
    row = next(line for line in content.splitlines() if line.startswith("RESULT mode="))
    values = {key: int(value) for key, value in re.findall(r"([a-z0-9_]+)=(\d+)", row)}
    if mode == "smoke":
        expected = {
            "inputs": _INPUT_BYTES,
            "input_sentinels": 675,
            "weights": _WEIGHT_BYTES,
            "patches": 675 + _WEIGHT_BYTES + 1,
            "output": 1,
            "feature_reads": _K,
            "weight_reads": _K,
            "abort": 1,
            "timeout": 1,
            "zero_timeout": 1,
            "timeout_n1": 1,
            "timeout_n2": 1,
            "reset": 1,
            "error_priority": 1,
            "raw_memory_error_priority": 1,
            "done_priority": 1,
        }
    else:
        expected = {
            "output": _OUTPUT_BYTES,
            "feature_reads": _OUTPUT_BYTES * _K,
            "weight_reads": _OUTPUT_BYTES * _K,
            "writes": _OUTPUT_BYTES,
            "patches": 675 + _WEIGHT_BYTES + _OUTPUT_BYTES,
            "busy_start_checks": 3,
            "done_hold": 3,
            "timeout": 1,
            "zero_timeout": 1,
            "timeout_n1": 1,
            "timeout_n2": 1,
            "abort": 1,
            "reset": 1,
            "error_priority": 1,
            "raw_memory_error_priority": 1,
            "done_priority": 1,
        }
    for key, wanted in expected.items():
        if values.get(key) != wanted:
            raise T20Error(f"xsim summary {key}={values.get(key)!r}，期望 {wanted}")
    if mode == "full" and values.get("stalls", 0) < 100000:
        raise T20Error("T10 scheduled stall cycles 不足")
    return values


def _run(mode: str) -> dict[str, object]:
    started = time.monotonic()
    overall_timeout = 1800 if mode == "smoke" else _OVERALL_TIMEOUT_SECONDS
    deadline = started + overall_timeout
    t17 = _load_t17_runner()
    head, frozen_hashes, manifest, layer, weights, parameters, package_path = _read_frozen_spec()
    input_bytes, expected_bytes, golden_stats = _input_and_golden(layer, weights, parameters, t17)
    source_hashes_before = _source_hashes()
    tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
    for path in tools.values():
        if not path.is_file():
            raise T20Error(f"Vivado 工具不存在：{path}")
    tool_versions = {name: _tool_version(path) for name, path in tools.items()}

    temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t20_layer36_{mode}_", dir=temp_parent))
    try:
        if os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) == str(_ROOT.resolve()):
            raise T20Error(f"T20 临时仿真目录意外位于仓库：{work}")
    except ValueError:
        pass

    ranges_sha, range_count = _write_memory_ranges(manifest, work)
    _write_hex_file(work / "layer36_weights.hex", weights)
    _write_hex_file(work / "layer36_expected_output.hex", expected_bytes)
    phases: list[dict[str, object]] = []
    source_paths = [
        _T17_GEOMETRY, _T17_WEIGHT_ADDRESS, _T17_MAC, _T17_ENGINE,
        _SCHEDULER, _T12_MASTER, _T10_MODEL, _TB,
    ]
    for phase, args in (
        ("xvlog", ["-sv", *map(str, source_paths)]),
        ("xelab", ["-top", "tb_s2a_conv_layer_scheduler",
         "-snapshot", "s2a_conv_layer_scheduler_snapshot"]),
    ):
        log = work / f"{phase}_command.log"
        code, elapsed, checkpoints = _run_logged(tools[phase], args, work, log, deadline)
        phases.append({
            "phase": phase,
            "command": _command_text(tools[phase], args),
            "exit_code": code,
            "elapsed_seconds": round(elapsed, 3),
            "log_path": str(log),
            "progress_checkpoints": checkpoints,
        })
        if code != 0:
            raise T20Error(f"{phase} exit={code}; log={log}")

    sim_args = ["-R", "s2a_conv_layer_scheduler_snapshot"]
    if mode == "smoke":
        sim_args.extend(["-testplusarg", "SMOKE"])
    sim_log = work / "xsim_command.log"
    sim_code, sim_elapsed, checkpoints = _run_logged(
        tools["xsim"], sim_args, work, sim_log, deadline,
        progress_timeout=_NO_PROGRESS_TIMEOUT_SECONDS,
    )
    phases.append({
        "phase": "xsim",
        "command": _command_text(tools["xsim"], sim_args),
        "exit_code": sim_code,
        "elapsed_seconds": round(sim_elapsed, 3),
        "log_path": str(sim_log),
        "no_progress_stop_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
        "progress_checkpoints": checkpoints,
    })
    if sim_code != 0:
        raise T20Error(f"xsim exit={sim_code}; log={sim_log}")
    summary = _parse_summary(sim_log, mode)

    trace_path = work / "observed_output_hex.txt"
    trace_rows = trace_path.read_text(encoding="ascii").splitlines()
    expected_trace_rows = _OUTPUT_BYTES if mode == "full" else 1
    if len(trace_rows) != expected_trace_rows or any(
        re.fullmatch(r"[0-9a-fA-F]{2}", row) is None for row in trace_rows
    ):
        raise T20Error(f"observed output trace 行数/格式不符：{len(trace_rows)}")
    observed_bytes = bytes(int(row, 16) for row in trace_rows)
    expected_compared = expected_bytes if mode == "full" else expected_bytes[:1]
    mismatch = next((index for index, (actual, expected) in enumerate(
        zip(observed_bytes, expected_compared, strict=True)) if actual != expected), None)
    if mismatch is not None:
        raise T20Error(
            f"逐 byte 输出 mismatch index={mismatch} "
            f"observed={observed_bytes[mismatch]:02x} expected={expected_compared[mismatch]:02x}"
        )
    if _sha256_bytes(observed_bytes) != _sha256_bytes(expected_compared):
        raise T20Error("trace 逐 byte 比较通过但 observed/golden SHA 不同")

    source_hashes_after = _source_hashes()
    if source_hashes_before != source_hashes_after:
        raise T20Error("仿真期间 T20 RTL/TB/runner 发生变化")
    if _FIXED_HASHES["manifest"] != frozen_hashes["manifest"]:
        raise T20Error("仿真期间 T01 manifest binding 不一致")

    result: dict[str, object] = {
        "schema": "GestureForge-S2A-T20-conv-layer-scheduler-simulation-v1",
        "task": "S2A-T20",
        "result": "PASS",
        "mode": mode.upper(),
        "baseline_head": head,
        "scope": "固定 tiny416 layer36 convolution layer scheduler pilot；不是整网，不是 PS/CSR descriptor。",
        "scheduler_shape_control": "OUTPUT_COUNT_LIMIT 默认编译为 20280；仅边界测试实例编译期设为 1，用于 Nth-edge done/error 优先级；生产固定层没有运行时 shape/descriptor 输入。",
        "bindings": {
            "g0_spec_path": str(_G0_SPEC.relative_to(_ROOT)).replace("\\", "/"),
            "manifest_path": str(_MANIFEST.relative_to(_ROOT)).replace("\\", "/"),
            "t16_proof_path": str(_T16_PROOF.relative_to(_ROOT)).replace("\\", "/"),
            "t16_script_path": str(_T16_SCRIPT.relative_to(_ROOT)).replace("\\", "/"),
            "t17_engine_path": str(_T17_ENGINE.relative_to(_ROOT)).replace("\\", "/"),
            "t10_memory_model_path": str(_T10_MODEL.relative_to(_ROOT)).replace("\\", "/"),
            "t12_memory_master_path": str(_T12_MASTER.relative_to(_ROOT)).replace("\\", "/"),
            "t19_scheduler_path": str(_T19_SCHEDULER.relative_to(_ROOT)).replace("\\", "/"),
            "t19_testbench_path": str(_T19_TB.relative_to(_ROOT)).replace("\\", "/"),
            "t19_runner_path": str(_T19_RUNNER.relative_to(_ROOT)).replace("\\", "/"),
            "t19_evidence_path": str(_T19_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "dependency_sha256": frozen_hashes,
            "t20_sha256": source_hashes_after,
            "gfint8w1_package_path": str(package_path),
            "gfint8w1_package_sha256": "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39",
            "gfint8w1_package_bytes": _WEIGHT_PACKAGE_BYTES,
            "layer36_weight_slice_sha256": _sha256_bytes(weights),
            "layer36_weight_slice_bytes": len(weights),
            "memory_ranges_sha256": ranges_sha,
            "memory_ranges_count": range_count,
        },
        "layer36": {
            "cfg_section": 37,
            "input_tensor_index": 35,
            "input_shape_nchw": [1, _INPUT_CHANNELS, _HEIGHT, _WIDTH],
            "input_base_address": _INPUT_BASE,
            "input_length_bytes": _INPUT_BYTES,
            "input_scale": layer["input_scale"],
            "weight_layer_index": 36,
            "weight_absolute_half_open_range": [
                _WEIGHT_BASE + _WEIGHT_OFFSET,
                _WEIGHT_BASE + _WEIGHT_OFFSET + _WEIGHT_BYTES,
            ],
            "weight_package_offset": _WEIGHT_OFFSET,
            "weight_bytes": _WEIGHT_BYTES,
            "output_shape_nchw": [1, _OUTPUT_CHANNELS, _HEIGHT, _WIDTH],
            "output_base_address": _OUTPUT_BASE,
            "output_length_bytes": _OUTPUT_BYTES,
            "output_half_open_range": [_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES],
            "last_output_byte_address": _OUTPUT_BASE + _OUTPUT_BYTES - 1,
            "kernel_hw": [1, 1],
            "stride_hw": [1, 1],
            "padding_lrtb": [0, 0, 0, 0],
            "groups": 1,
            "activation": "linear",
            "layout": "NCHW channel,row,column order",
            "reduction_length": _K,
            "output_scale": layer["output_scale"],
            "t16_parameter_sha256": next(
                row["candidate_parameter_sha256"]
                for row in json.loads(_T16_PROOF.read_text(encoding="utf-8"))["layers"]
                if int(row["layer_index"]) == 36
            ),
            "t16_channel_parameter_count": len(parameters),
            "t16_linear_positive_negative_common_mq": True,
            "bias_int32": list(map(int, layer["bias_accumulator_int32_per_output_channel"])),
            "multiplier_per_channel": [int(row["positive_multiplier"]) for row in parameters],
            "q_shift_per_channel": [int(row["positive_q_shift"]) for row in parameters],
        },
        "fixture": {
            "input_generator": "T10 initial_byte(address)=address[7:0]^address[15:8]^address[23:16]^address[31:24]^0xA5；只将所有 raw 0x80 地址修正为 INT8 0。",
            "input_seed": None,
            "input_bytes": len(input_bytes),
            "raw_minus_128_count_before_patch": 675,
            "input_sha256_after_patch": _sha256_bytes(input_bytes),
            "input_patch_count": 675,
            "weight_source": "只读解析 T01 绑定 GFINT8W1 包真实 layer36 quantized weight 字节；不把包或原始权重加入 Git。",
            "weight_slice_bytes": len(weights),
            "weight_slice_sha256": _sha256_bytes(weights),
            "t10_patch_capacity": 32768,
            "unique_patch_count_expected": 675 + _WEIGHT_BYTES + _OUTPUT_BYTES,
            "patch_capacity_headroom": 32768 - (675 + _WEIGHT_BYTES + _OUTPUT_BYTES),
        },
        "golden": {
            "oracle": "逐NCHW输出和K顺序执行INT32有序累加并逐步溢出检查；使用T16精确整数M/Q half-away映射和[-127,127]饱和；每个输出同时与D2原始scale的half-away浮点公式交叉检查。",
            "input_sha256": _sha256_bytes(input_bytes),
            "expected_output_bytes": len(expected_bytes),
            "expected_output_sha256": _sha256_bytes(expected_bytes),
            "int32_accumulator_min": golden_stats["int32_accumulator_min"],
            "int32_accumulator_max": golden_stats["int32_accumulator_max"],
            "d2_float_cross_checks": golden_stats["d2_float_cross_checks"],
            "observed_output_bytes": len(observed_bytes),
            "observed_output_sha256": _sha256_bytes(observed_bytes),
            "observed_hex_trace_sha256": _sha256_file(trace_path),
            "observed_hex_trace_path": str(trace_path),
            "mismatch_count": 0,
        },
        "verification": {
            "xsim_summary": summary,
            "full_layer_outputs_required": _OUTPUT_BYTES,
            "full_output_bytes_compared": len(observed_bytes),
            "feature_read_count_expected": _OUTPUT_BYTES * _K,
            "weight_read_count_expected": _OUTPUT_BYTES * _K,
            "output_write_count_expected": _OUTPUT_BYTES,
            "byte_lane_and_order_checks": "每个feature/weight字节的word地址、one-hot lane、K/通道/像素顺序逐请求检查；每个output地址、lane与NCHW序号及值逐byte检查。",
            "control_coverage": {
                "zero_timeout_bad_argument": summary["zero_timeout"],
                "N1_timeout_edge_after_start": summary["timeout_n1"],
                "N2_timeout_edge_after_start": summary["timeout_n2"],
                "pending_read_abort": 1,
                "pending_read_timeout_cancel": 1,
                "pending_write_hard_reset_cancel": 1,
                "Nth_edge_error_over_timeout_priority": 1,
                "raw_T10_T12_memory_error_response_at_deadline":
                    summary["raw_memory_error_priority"],
                "Nth_edge_done_over_timeout_priority": 1,
                "completion_hold_cycles": 9 if mode == "full" else 9,
                "busy_start_backpressure_checks": summary.get("busy_start_checks", 0),
                "recovery_after_error_abort_reset": "ACK/reset后重新启动；full模式随后完整执行 layer36。",
                "Nth_edge_error_test_cycles": summary.get("timeout_priority_cycles"),
                "Nth_edge_done_test_cycles": summary.get("done_priority_cycles"),
            },
            "timeout_protocol": "按T01/G0从start接受后的第一个后续posedge起计，N个周期均可推进；第N个后续posedge才判定timeout，错误或最终done同沿优先。timeout锁存后才取消子引擎和未完成请求。定向验证N=1、N=2、N=8 pending-read取消、原始T10/T12 memory error response恰在deadline沿握手仍优先于timeout，以及最终done恰在deadline沿优先。该语义仅为固定layer wrapper内部实现，没有新增PS/CSR descriptor。",
            "scheduled_memory_stalls": _STALL_SCHEDULE,
            "full_stall_cycles": summary.get("stalls"),
            "tool_versions": tool_versions,
            "python_version": platform.python_version(),
            "phases": phases,
            "work_directory": str(work),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "overall_timeout_seconds": overall_timeout,
            "no_progress_stop_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
            "no_progress_checkpoint": "每128个输出写入一条PROGRESS；初始化输入与权重fixture也有进度行。",
            "synthesis_and_resource_estimation": "未执行；本 pilot 验收未要求综合或资源估算。",
            "board_validation": "不适用；未请求烧录或实物操作。",
            "scope_limit": "只覆盖layer36固定单层调度，不表示整网验证/G4/G5，不实现PS解码/NMS或PS/CSR控制器。",
        },
    }
    if mode == "full":
        payload = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_bytes(payload)
        result["evidence_sha256"] = _sha256_bytes(payload)
    print(json.dumps({
        "result": result["result"],
        "mode": result["mode"],
        "output_bytes_compared": len(observed_bytes),
        "output_sha256": _sha256_bytes(observed_bytes),
        "xsim_exit_code": sim_code,
        "xsim_seconds": round(sim_elapsed, 3),
        "progress_checkpoints": len(checkpoints),
        "work_directory": str(work),
        "evidence_path": str(_EVIDENCE) if mode == "full" else None,
        "evidence_sha256": result.get("evidence_sha256"),
    }, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), required=True)
    args = parser.parse_args()
    try:
        _run(args.mode)
    except Exception as error:
        print(f"FAIL S2A-T20: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
