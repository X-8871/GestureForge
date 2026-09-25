"""运行 S2A-T21 tiny416 layer25 固定 maxpool 层调度器验证。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import queue
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "18c075c2154bdbb6a985310354503682766eb3d5"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_T14_ENGINE = _ROOT / "src/s2a_maxpool_engine.sv"
_T14_EVIDENCE = _ROOT / "report/evidence/S2A-T14/maxpool_simulation.json"
_T10_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_T10_EVIDENCE = _ROOT / "report/evidence/S2A-T10/memory_model_simulation.json"
_T12_MASTER = _ROOT / "src/s2a_memory_master.sv"
_T12_EVIDENCE = _ROOT / "report/evidence/S2A-T12/runtime_protocol_simulation.json"
_GEOMETRY = _ROOT / "src/int8_maxpool_geometry.sv"
_WINDOW = _ROOT / "src/int8_maxpool_window.sv"
_SCHEDULER = _ROOT / "src/s2a_maxpool_layer_scheduler.sv"
_TB = _ROOT / "sim/tb_s2a_maxpool_layer_scheduler.sv"
_RUNNER = Path(__file__).resolve()
_EVIDENCE = _ROOT / "report/evidence/S2A-T21/maxpool_layer_scheduler_simulation.json"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")

_INPUT_BASE = 26900992
_INPUT_BYTES = 346112
_INPUT_CHANNELS = 512
_INPUT_DIMENSION = 26
_OUTPUT_BASE = 27247104
_OUTPUT_BYTES = 86528
_OUTPUT_DIMENSION = 13
_T10_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_PATCH_CAPACITY = 131072
_OVERALL_TIMEOUT_SECONDS = 3600
_NO_PROGRESS_TIMEOUT_SECONDS = 900
_MAX_FEATURE_RANGES = 36

_FIXED_HASHES = {
    "g0_spec": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "t14_engine": "3dbb1fd41fbe773debade2629e8e7565554d14051a906466042906bb925de7b7",
    "t14_evidence": "2e681fb5db9037f6858c7516b4620053374d571e66d27c15ded6dfbffb8927e3",
    "t10_model": "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
    "t10_evidence": "0629d137c2df4aa96f3bc1713556cd6cd23f5cec4f2e35a388a448f13b370556",
    "t12_master": "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    "t12_evidence": "332e038d85f27366b9692e4a4aeaa4933fcec9a22d64c2f9b905fe7978dcd01d",
    "geometry": "0e1d398a479990dc2e614fda734fac14ddf8217c1197b1a52f9be0efe3b1905a",
    "window": "0ea5865e939a691ccb7fea4602fd31211c816d13424ac7c77c89713ff5a15653",
}


class T21Error(RuntimeError):
    """报告冻结输入、逐 byte 黄金或 RTL 仿真失败。"""


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _frozen_paths() -> dict[str, Path]:
    return {
        "g0_spec": _G0_SPEC,
        "manifest": _MANIFEST,
        "t14_engine": _T14_ENGINE,
        "t14_evidence": _T14_EVIDENCE,
        "t10_model": _T10_MODEL,
        "t10_evidence": _T10_EVIDENCE,
        "t12_master": _T12_MASTER,
        "t12_evidence": _T12_EVIDENCE,
        "geometry": _GEOMETRY,
        "window": _WINDOW,
    }


def _verify_frozen() -> tuple[str, dict[str, str], dict, dict, dict]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
        text=True, encoding="utf-8", check=True,
    ).stdout.strip()
    if head != _BASELINE_HEAD:
        raise T21Error(f"T21 baseline HEAD 不符：{head}")

    frozen_hashes = {name: _sha256_file(path) for name, path in _frozen_paths().items()}
    for name, expected in _FIXED_HASHES.items():
        if frozen_hashes[name] != expected:
            raise T21Error(f"冻结依赖 {name} SHA-256 不符：{frozen_hashes[name]}")

    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    layers = {int(row["layer_index"]): row for row in manifest["layers"]}
    source = layers[24]
    layer = layers[25]
    if (
        int(layer["cfg_section"]) != 26
        or layer["op"] != "maxpool"
        or list(map(int, layer["input_tensor_indices"])) != [24]
        or list(map(int, source["output_shape_nchw"])) != [1, 512, 26, 26]
        or int(source["tensor_address"]) != _INPUT_BASE
        or int(source["tensor_length_bytes"]) != _INPUT_BYTES
        or list(map(int, layer["input_shape_nchw"])) != [1, 512, 26, 26]
        or list(map(int, layer["output_shape_nchw"])) != [1, 512, 13, 13]
        or int(layer["tensor_address"]) != _OUTPUT_BASE
        or int(layer["tensor_length_bytes"]) != _OUTPUT_BYTES
        or list(map(int, layer["kernel_hw"])) != [2, 2]
        or list(map(int, layer["stride_hw"])) != [2, 2]
        or int(layer["darknet_padding_parameter"]) != 1
        or list(map(int, layer["padding_lrtb_actual"])) != [0, 0, 0, 0]
        or int(layer["pad_value_int8"]) != -127
        or layer["layout"] != "NCHW"
        or layer["element_type"] != "int8_twos_complement"
        or float(layer["input_scale"]) != float(layer["output_scale"])
    ):
        raise T21Error("T01 layer24/25 固定形状、地址或 maxpool 规格与任务边界不符")

    t14 = json.loads(_T14_EVIDENCE.read_text(encoding="utf-8"))
    if t14.get("result") != "PASS":
        raise T21Error("T14 maxpool engine evidence 不是 PASS")
    t14_sources = t14.get("bindings", {}).get("source_sha256", {})
    for path, key in (
        (_G0_SPEC, "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"),
        (_MANIFEST, "report/evidence/S2A-T01/tiny416_model_manifest.json"),
        (_T14_ENGINE, "src/s2a_maxpool_engine.sv"),
        (_T10_MODEL, "sim/s2a_memory_model.sv"),
        (_T12_MASTER, "src/s2a_memory_master.sv"),
        (_GEOMETRY, "src/int8_maxpool_geometry.sv"),
        (_WINDOW, "src/int8_maxpool_window.sv"),
    ):
        if t14_sources.get(key) != _sha256_file(path):
            raise T21Error(f"T14 evidence source binding 不一致：{key}")
    layer25_vectors = t14.get("counts", {}).get("by_layer", {}).get("25", {})
    if layer25_vectors.get("random") != 1000 or layer25_vectors.get("directed") != 16:
        raise T21Error("T14 layer25 1000 随机和16定向 engine 向量绑定缺失")

    t10 = json.loads(_T10_EVIDENCE.read_text(encoding="utf-8"))
    t10_bindings = t10.get("bindings", {})
    if (
        t10.get("result") != "PASS"
        or t10_bindings.get("model_sha256") != frozen_hashes["t10_model"]
        or t10_bindings.get("manifest_sha256") != frozen_hashes["manifest"]
        or t10_bindings.get("g0_spec_sha256") != frozen_hashes["g0_spec"]
    ):
        raise T21Error("T10 evidence 与当前 memory model/G0/manifest 不一致")
    t12 = json.loads(_T12_EVIDENCE.read_text(encoding="utf-8"))
    t12_bindings = t12.get("bindings", {})
    if (
        t12.get("result") != "PASS"
        or t12_bindings.get("memory_master_sha256") != frozen_hashes["t12_master"]
        or t12_bindings.get("memory_model_sha256") != frozen_hashes["t10_model"]
        or t12_bindings.get("manifest_sha256") != frozen_hashes["manifest"]
        or t12_bindings.get("g0_spec_sha256") != frozen_hashes["g0_spec"]
    ):
        raise T21Error("T12 evidence 与当前 memory master/T10/G0/manifest 不一致")
    return head, frozen_hashes, manifest, layer, {"t14": t14, "t10": t10, "t12": t12}


def _initial_byte(address: int) -> int:
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _input_and_golden() -> tuple[bytes, bytes, list[int]]:
    """按 T10 地址公式生成输入、修正 raw -128，并计算 NCHW maxpool 黄金。"""
    input_data = bytearray()
    sentinel_offsets: list[int] = []
    for offset in range(_INPUT_BYTES):
        value = _initial_byte(_INPUT_BASE + offset)
        if value == 0x80:
            value = 0
            sentinel_offsets.append(offset)
        input_data.append(value)
    if len(sentinel_offsets) != 1352:
        raise T21Error(f"T10 layer25 input raw 0x80 数量不符：{len(sentinel_offsets)}")

    output = bytearray()
    for channel in range(_INPUT_CHANNELS):
        channel_base = channel * _INPUT_DIMENSION * _INPUT_DIMENSION
        for output_y in range(_OUTPUT_DIMENSION):
            source_y = output_y * 2
            for output_x in range(_OUTPUT_DIMENSION):
                source_x = output_x * 2
                candidates = (
                    input_data[channel_base + source_y * _INPUT_DIMENSION + source_x],
                    input_data[channel_base + source_y * _INPUT_DIMENSION + source_x + 1],
                    input_data[channel_base + (source_y + 1) * _INPUT_DIMENSION + source_x],
                    input_data[channel_base + (source_y + 1) * _INPUT_DIMENSION + source_x + 1],
                )
                signed_candidates = tuple(value if value < 128 else value - 256
                                          for value in candidates)
                if -128 in signed_candidates:
                    raise T21Error("golden maxpool 输入仍包含非法 INT8 -128")
                output.append(max(signed_candidates) & 0xFF)
    if len(output) != _OUTPUT_BYTES:
        raise T21Error(f"CPU golden 输出 byte 数量错误：{len(output)}")
    return bytes(input_data), bytes(output), sentinel_offsets


def _write_hex_file(path: Path, payload: bytes) -> None:
    path.write_text("".join(f"{value:02x}\n" for value in payload),
                    encoding="ascii", newline="\n")


def _write_memory_ranges(manifest: dict, work: Path) -> tuple[str, int]:
    ranges = sorted({
        (int(row["tensor_address"]),
         int(row["tensor_address"]) + int(row["tensor_length_bytes"]))
        for row in manifest["layers"] if row.get("op") != "yolo"
    })
    if len(ranges) != _MAX_FEATURE_RANGES:
        raise T21Error(f"manifest feature range 数量错误：{len(ranges)}")
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise T21Error("manifest feature tensor address 范围重叠")
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
    result: dict[str, str] = {}
    for name, path in (("scheduler", _SCHEDULER), ("testbench", _TB), ("runner", _RUNNER)):
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise T21Error(f"T21 source 不是 UTF-8/LF：{path}")
        raw.decode("utf-8")
        result[name] = _sha256_bytes(raw)
    return result


def _tool_version(tool: Path) -> str:
    command = f'cmd.exe /d /s /c "{tool} -version"'
    result = subprocess.run(command, shell=False, cwd=_ROOT, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=30)
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        raise T21Error(f"{tool.name} -version exit={result.returncode}: {output[-1000:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise T21Error(f"无法解析 {tool.name} 版本：{output[-1000:]}")
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
                raise TimeoutError(f"T21 全局时限到期；日志：{log_path}")
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
    marker = "PASS S2A-T21 focused smoke" if mode == "smoke" else \
             "PASS S2A-T21 complete tiny416 layer25 maxpool scheduler"
    if content.count(marker) != 1 or content.count("RESULT mode=") != 1:
        raise T21Error(f"xsim RESULT/PASS 标记不唯一：{log_path}")
    row = next(line for line in content.splitlines() if line.startswith("RESULT mode="))
    values = {key: int(value) for key, value in re.findall(r"([a-z0-9_]+)=(\d+)", row)}
    if mode == "smoke":
        expected = {
            "input_sentinels": 1352, "patches": 1353, "output": 1,
            "feature_reads": 4, "writes": 1, "abort": 1, "timeout": 1,
            "zero_timeout": 1, "timeout_n1": 1, "timeout_n2": 1, "reset": 1,
            "error_priority": 1, "raw_memory_error_priority": 1, "done_priority": 1,
        }
    else:
        expected = {
            "input_sentinels": 1352, "patches": 1352 + _OUTPUT_BYTES,
            "output": _OUTPUT_BYTES, "feature_reads": _OUTPUT_BYTES * 4,
            "writes": _OUTPUT_BYTES, "busy_start_checks": 3, "done_hold": 9,
            "timeout": 1, "zero_timeout": 1, "timeout_n1": 1,
            "timeout_n2": 1, "abort": 1, "reset": 1,
            "error_priority": 1, "raw_memory_error_priority": 1, "done_priority": 1,
        }
    for key, wanted in expected.items():
        if values.get(key) != wanted:
            raise T21Error(f"xsim summary {key}={values.get(key)!r}，期望 {wanted}")
    if mode == "full" and values.get("stalls", 0) < 100000:
        raise T21Error("T10 scheduled stall cycles 不足")
    return values


def _run(mode: str) -> dict[str, object]:
    started = time.monotonic()
    overall_timeout = 1800 if mode == "smoke" else _OVERALL_TIMEOUT_SECONDS
    deadline = started + overall_timeout
    head, frozen_hashes, manifest, layer, prior_evidence = _verify_frozen()
    input_bytes, expected_bytes, sentinel_offsets = _input_and_golden()
    source_hashes_before = _source_hashes()

    tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
    for path in tools.values():
        if not path.is_file():
            raise T21Error(f"Vivado 2026.1 工具不存在：{path}")
    tool_versions = {name: _tool_version(path) for name, path in tools.items()}

    temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t21_layer25_{mode}_", dir=temp_parent))
    try:
        if os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) == str(_ROOT.resolve()):
            raise T21Error(f"T21 临时仿真目录意外位于仓库：{work}")
    except ValueError:
        pass

    ranges_sha, range_count = _write_memory_ranges(manifest, work)
    t10_ranges_sha = prior_evidence["t10"]["bindings"]["manifest_derived_ranges_sha256"]
    if ranges_sha != t10_ranges_sha:
        raise T21Error("T10 memory ranges 与冻结 evidence 不一致")
    _write_hex_file(work / "layer25_expected_output.hex", expected_bytes)

    phases: list[dict[str, object]] = []
    source_paths = [_GEOMETRY, _WINDOW, _T14_ENGINE, _SCHEDULER,
                    _T12_MASTER, _T10_MODEL, _TB]
    for phase, args in (
        ("xvlog", ["-sv", *map(str, source_paths)]),
        ("xelab", ["-top", "tb_s2a_maxpool_layer_scheduler",
         "-snapshot", "s2a_maxpool_layer_scheduler_snapshot"]),
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
            raise T21Error(f"{phase} exit={code}; log={log}")

    sim_args = ["-R", "s2a_maxpool_layer_scheduler_snapshot"]
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
        raise T21Error(f"xsim exit={sim_code}; log={sim_log}")
    summary = _parse_summary(sim_log, mode)

    trace_path = work / "observed_output_hex.txt"
    trace_rows = trace_path.read_text(encoding="ascii").splitlines()
    expected_trace_rows = _OUTPUT_BYTES if mode == "full" else 1
    if len(trace_rows) != expected_trace_rows or any(
        re.fullmatch(r"[0-9a-fA-F]{2}", row) is None for row in trace_rows
    ):
        raise T21Error(f"observed output trace 行数/格式错误：{len(trace_rows)}")
    observed_bytes = bytes(int(row, 16) for row in trace_rows)
    expected_compared = expected_bytes if mode == "full" else expected_bytes[:1]
    mismatch = next((index for index, (actual, expected) in enumerate(
        zip(observed_bytes, expected_compared, strict=True)) if actual != expected), None)
    if mismatch is not None:
        raise T21Error(
            f"逐 byte mismatch index={mismatch} observed={observed_bytes[mismatch]:02x} "
            f"expected={expected_compared[mismatch]:02x}"
        )
    if _sha256_bytes(observed_bytes) != _sha256_bytes(expected_compared):
        raise T21Error("逐 byte 对比和 observed/golden SHA 不一致")

    source_hashes_after = _source_hashes()
    if source_hashes_before != source_hashes_after:
        raise T21Error("仿真期间 T21 RTL/TB/runner 发生变化")

    result: dict[str, object] = {
        "schema": "GestureForge-S2A-T21-maxpool-layer-scheduler-simulation-v1",
        "task": "S2A-T21",
        "result": "PASS",
        "mode": mode.upper(),
        "baseline_head": head,
        "scope": "固定 tiny416 layer25 maxpool 整层调度器 pilot；不是整网、G4/G5 或 PS/CSR descriptor。",
        "bindings": {
            "g0_spec_path": str(_G0_SPEC.relative_to(_ROOT)).replace("\\", "/"),
            "manifest_path": str(_MANIFEST.relative_to(_ROOT)).replace("\\", "/"),
            "t14_engine_path": str(_T14_ENGINE.relative_to(_ROOT)).replace("\\", "/"),
            "t14_evidence_path": str(_T14_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "t10_memory_model_path": str(_T10_MODEL.relative_to(_ROOT)).replace("\\", "/"),
            "t10_evidence_path": str(_T10_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "t12_memory_master_path": str(_T12_MASTER.relative_to(_ROOT)).replace("\\", "/"),
            "t12_evidence_path": str(_T12_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "dependency_sha256": frozen_hashes,
            "t21_sha256": source_hashes_after,
            "t14_layer25_random_vectors": prior_evidence["t14"]["counts"]["by_layer"]["25"]["random"],
            "t14_layer25_directed_vectors": prior_evidence["t14"]["counts"]["by_layer"]["25"]["directed"],
            "memory_ranges_sha256": ranges_sha,
            "memory_ranges_count": range_count,
        },
        "layer25": {
            "cfg_section": 26,
            "input_tensor_index": 24,
            "input_shape_nchw": [1, _INPUT_CHANNELS, _INPUT_DIMENSION, _INPUT_DIMENSION],
            "input_base_address": _INPUT_BASE,
            "input_length_bytes": _INPUT_BYTES,
            "input_scale": layer["input_scale"],
            "output_shape_nchw": [1, _INPUT_CHANNELS, _OUTPUT_DIMENSION, _OUTPUT_DIMENSION],
            "output_base_address": _OUTPUT_BASE,
            "output_length_bytes": _OUTPUT_BYTES,
            "output_half_open_range": [_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES],
            "last_output_byte_address": _OUTPUT_BASE + _OUTPUT_BYTES - 1,
            "kernel_hw": [2, 2],
            "stride_hw": [2, 2],
            "darknet_padding_parameter": 1,
            "padding_lrtb_actual": [0, 0, 0, 0],
            "pad_value_int8": -127,
            "layout": "NCHW channel,row,column order",
            "element_type": "int8_twos_complement",
            "output_scale": layer["output_scale"],
        },
        "fixture": {
            "input_generator": "T10 initial_byte(address)=address[7:0]^address[15:8]^address[23:16]^address[31:24]^0xA5；raw 0x80 全部按 INT8 合法域修补为0。",
            "input_seed": None,
            "input_bytes": len(input_bytes),
            "raw_0x80_count_before_patch": len(sentinel_offsets),
            "input_patch_count": len(sentinel_offsets),
            "input_patch_rule": "仅将输入区间内 raw 0x80（INT8 -128）写为 0；其他字节保持 T10 初值。",
            "input_patch_offsets_sha256": _sha256_bytes(
                b"".join(offset.to_bytes(4, "little") for offset in sentinel_offsets)
            ),
            "input_sha256_after_patch": _sha256_bytes(input_bytes),
            "t10_patch_capacity": _PATCH_CAPACITY,
            "unique_patch_count_expected": len(sentinel_offsets) + _OUTPUT_BYTES,
            "patch_capacity_headroom": _PATCH_CAPACITY - len(sentinel_offsets) - _OUTPUT_BYTES,
        },
        "golden": {
            "oracle": "独立 Python 按 NCHW 和 2x2 row-major tap 次序取 T10-backed 修补后输入，转换为有符号 INT8 并取最大值；scale 相同，不做 requant。",
            "input_sha256": _sha256_bytes(input_bytes),
            "expected_output_bytes": len(expected_bytes),
            "expected_output_sha256": _sha256_bytes(expected_bytes),
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
            "feature_read_count_expected": _INPUT_BYTES,
            "output_write_count_expected": _OUTPUT_BYTES,
            "byte_lane_and_order_checks": "逐个 feature 请求校验 word 地址、one-hot byte lane、通道/行/列及四 tap 次序；逐个 output 请求校验地址、lane、NCHW 序号和值。",
            "control_coverage": {
                "zero_timeout_bad_argument": summary["zero_timeout"],
                "N1_timeout_edge_after_start": summary["timeout_n1"],
                "N2_timeout_edge_after_start": summary["timeout_n2"],
                "pending_read_abort": summary["abort"],
                "pending_read_timeout_cancel": summary["timeout"],
                "pending_write_hard_reset_cancel": summary["reset"],
                "Nth_edge_error_over_timeout_priority": summary["error_priority"],
                "raw_T10_T12_memory_error_response_at_deadline": summary["raw_memory_error_priority"],
                "Nth_edge_done_over_timeout_priority": summary["done_priority"],
                "completion_hold_cycles": summary["done_hold"] if mode == "full" else 9,
                "busy_start_backpressure_checks": summary.get("busy_start_checks", 0),
                "recovery_after_error_abort_reset": "ACK 或复位后接受新的合法 start；full 模式随后完成全部 layer25。",
                "Nth_edge_error_test_cycles": summary.get("timeout_priority_cycles"),
                "Nth_edge_done_test_cycles": summary.get("done_priority_cycles"),
            },
            "timeout_protocol": "沿用 T01/G0：start 接受沿之后的 N 个 PL 周期均可推进，在第 N 个后续上升沿错误或最终 done 优先，否则 timeout；取消在 timeout 决策后生效。定向覆盖 N=1/N=2、pending read timeout、raw T10/T12 memory error 同沿 handshake、最终 done 同沿。",
            "scheduled_memory_stalls": _T10_STALL_SCHEDULE,
            "full_stall_cycles": summary.get("stalls"),
            "tool_versions": tool_versions,
            "python_version": platform.python_version(),
            "phases": phases,
            "work_directory": str(work),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "overall_timeout_seconds": overall_timeout,
            "no_progress_stop_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
            "no_progress_checkpoint": "每1024个输出写入一条 PROGRESS；合成输入修补也输出fixture进度。",
            "synthesis_and_resource_estimation": "未执行；本层仿真 pilot 不包含综合或资源估算。",
            "board_validation": "不适用；未烧录或操作实物。",
            "scope_limit": "仅固定 tiny416 layer25 单层调度，不表示整网验证、阶段 G4/G5 或整网完成。",
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
        print(f"FAIL S2A-T21: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
