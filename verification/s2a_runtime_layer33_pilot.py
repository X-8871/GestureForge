"""运行 T27 G0 runtime shell 与 tiny416 layer33 的 Vivado 仿真。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import queue
import re
import shutil
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
_T18_TB = Path("sim/tb_s2a_upsample_layer_scheduler.sv")
_T18_RUNNER = Path("verification/test_s2a_upsample_layer_scheduler_rtl.py")
_T10_MODEL = Path("sim/s2a_memory_model.sv")
_SHELL = Path("src/s2a_runtime_shell.sv")
_CSR = Path("src/s2a_control_csr.sv")
_T12_MASTER = Path("src/s2a_memory_master.sv")
_QUERY = Path("src/int8_upsample_query.sv")
_ENGINE = Path("src/s2a_upsample_engine.sv")
_SCHEDULER = Path("src/s2a_upsample_layer_scheduler.sv")
_WRAPPER = Path("src/s2a_runtime_layer33_pilot.sv")
_TB = Path("sim/tb_s2a_runtime_layer33_pilot.sv")
_TEST = Path("verification/test_s2a_runtime_layer33_pilot_rtl.py")
_RUNNER = Path("verification/s2a_runtime_layer33_pilot.py")
_EVIDENCE_DIR = Path("report/evidence/S2A-T27")
_EVIDENCE = _EVIDENCE_DIR / "runtime_layer33_pilot_validation.json"
_TRACE_NAME = "observed_output_hex.txt"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_TOTAL_TIMEOUT_SECONDS = 3600
_NO_PROGRESS_SECONDS = 1800

_PINNED_HASHES = {
    _G0_SPEC.as_posix(): "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    _MANIFEST.as_posix(): "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    _T22.as_posix(): "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
    _T18_EVIDENCE.as_posix(): "0f2a4a81275ffa225babb78b767bfc42a597320308ef7b150af5f80fd6aac35d",
    _SHELL.as_posix(): "c784de2c94456eb4bdbd9ff763454b9784ebcb8d8821d6505d68707cfc37e52e",
    _CSR.as_posix(): "97fc62dd1967ea9486db1c6e48134283d62005805a0ca5ef44d6ea70ab2fc9d2",
    _T12_MASTER.as_posix(): "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    _QUERY.as_posix(): "9212f70c31fab6c6e5a30551c5d1fd7b6eeeafa4c1f2cbd20fe157015faa370c",
    _ENGINE.as_posix(): "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b",
    _SCHEDULER.as_posix(): "1473fd371c65658e105ff2ad575d523a98a53e5c5ebd8bb9f21ca33b61678bce",
    _T10_MODEL.as_posix(): "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
    _T18_TB.as_posix(): "ec15fd8a86a6c63e1a0ffa2fe4059c644cb61a78cd01f1ebef03901f917469de",
    _T18_RUNNER.as_posix(): "c8ddc62aae0a1da19379c600349de4380287afec85f82727828b0cd55ec5af1b",
}


def _sha256_bytes(payload: bytes) -> str:
    """计算字节序列的 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _repo_path(relative: Path) -> Path:
    """通过仓库相对路径取得文件并校验其存在。"""
    path = _ROOT / relative
    if not path.is_file():
        raise FileNotFoundError(f"必需输入文件不存在：{relative.as_posix()}")
    return path


def _assert_pinned_hash(name: str, observed: str, expected: str) -> None:
    """拒绝与冻结哈希不一致的输入源。"""
    if observed != expected:
        raise AssertionError(
            f"冻结来源 SHA-256 不匹配：{name} observed={observed} expected={expected}"
        )


def _load_json(relative: Path) -> dict[str, Any]:
    """以 UTF-8 读取 JSON 对象。"""
    raw = _repo_path(relative).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON 根节点不是对象：{relative.as_posix()}")
    return value


def _layer_map(manifest: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """验证并按层号索引模型清单。"""
    layers = manifest.get("layers")
    if not isinstance(layers, list) or len(layers) != 38:
        raise AssertionError("tiny416 manifest 必须包含 38 个网络层")
    result: dict[int, dict[str, Any]] = {}
    for row in layers:
        if not isinstance(row, dict):
            raise AssertionError("manifest layer row 必须为对象")
        index = int(row["layer_index"])
        if index in result:
            raise AssertionError(f"manifest layer_index 重复：{index}")
        result[index] = row
    if sorted(result) != list(range(38)):
        raise AssertionError("manifest layer_index 必须连续覆盖 0..37")
    return result


def _layer33_descriptor(manifest: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """交叉核对 manifest 与 T22 中冻结的 layer33 描述。"""
    layers = _layer_map(manifest)
    source = layers[32]
    layer = layers[33]
    if (layer.get("cfg_section") != 34 or layer.get("op") != "upsample" or
            layer.get("input_tensor_indices") != [32] or
            layer.get("input_shape_nchw") != [1, 128, 13, 13] or
            layer.get("output_shape_nchw") != [1, 128, 26, 26] or
            layer.get("layout") != "NCHW" or
            layer.get("element_type") != "int8_twos_complement" or
            layer.get("stride") != 2 or layer.get("method") != "nearest_repeat" or
            layer.get("input_scale") != layer.get("output_scale") or
            int(source.get("tensor_address", -1)) != 27598336 or
            int(source.get("tensor_length_bytes", -1)) != 21632 or
            int(layer.get("tensor_address", -1)) != 27619968 or
            int(layer.get("tensor_length_bytes", -1)) != 86528):
        raise AssertionError("manifest layer32/33 与冻结的 layer33 规格不一致")

    if contract.get("task_id") != "S2A-T22" or contract.get("artifact_status") != "CONTRACT_VALIDATED":
        raise AssertionError("T22 dispatch contract 状态不是已验证")
    dispatch = contract.get("network_dispatch")
    if not isinstance(dispatch, dict) or dispatch.get("layer_count") != 38:
        raise AssertionError("T22 contract 未声明 38 层 dispatch")
    rows = dispatch.get("layers")
    if not isinstance(rows, list) or len(rows) != 38:
        raise AssertionError("T22 contract 必须包含 38 个 dispatch rows")
    contract_rows = [row for row in rows if row.get("layer_index") == 33]
    if len(contract_rows) != 1:
        raise AssertionError("T22 contract layer33 row 缺失或重复")
    contract_row = contract_rows[0]
    inputs = contract_row.get("input_tensors_in_manifest_order")
    output = contract_row.get("output_tensor")
    params = contract_row.get("operator_parameters")
    if (contract_row.get("cfg_section") != 34 or contract_row.get("op") != "upsample" or
            not isinstance(inputs, list) or len(inputs) != 1 or
            inputs[0].get("source_index") != 32 or
            inputs[0].get("address") != 27598336 or
            inputs[0].get("length_bytes") != 21632 or
            inputs[0].get("shape_nchw") != [1, 128, 13, 13] or
            not isinstance(output, dict) or output.get("memory_write_required") is not True or
            output.get("address") != 27619968 or output.get("length_bytes") != 86528 or
            output.get("shape_nchw") != [1, 128, 26, 26] or
            not isinstance(params, dict) or params.get("stride") != 2 or
            params.get("method") != "nearest_repeat"):
        raise AssertionError("T22 dispatch row layer33 不符合已冻结 tensor/op 描述")
    protocol = contract.get("dispatch_protocol", {})
    timeout = protocol.get("global_timeout", {})
    completion = protocol.get("completion_event", {})
    if (timeout.get("per_layer_timeout_restart_allowed") is not False or
            completion.get("pulse_cycles") != 1 or completion.get("backpressure") is not False or
            completion.get("one_event_per_accepted_task") is not True):
        raise AssertionError("T22 timeout 或单周期终态事件语义不符合冻结规则")

    return {
        "cfg_section": 34,
        "input_address": int(source["tensor_address"]),
        "input_length_bytes": int(source["tensor_length_bytes"]),
        "input_shape_nchw": list(source["output_shape_nchw"]),
        "input_scale": float(layer["input_scale"]),
        "output_address": int(layer["tensor_address"]),
        "output_length_bytes": int(layer["tensor_length_bytes"]),
        "output_shape_nchw": list(layer["output_shape_nchw"]),
        "output_scale": float(layer["output_scale"]),
        "stride": int(layer["stride"]),
        "layout": str(layer["layout"]),
        "method": str(layer["method"]),
    }


def _verify_frozen_bindings() -> tuple[dict[str, str], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """校验固定来源哈希并读取层33模型和 contract 描述。"""
    hashes: dict[str, str] = {}
    for relative_name, expected in _PINNED_HASHES.items():
        relative = Path(relative_name)
        actual = _sha256_file(_repo_path(relative))
        _assert_pinned_hash(relative_name, actual, expected)
        raw = _repo_path(relative).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"冻结输入必须为 UTF-8/LF：{relative_name}")
        raw.decode("utf-8")
        hashes[relative_name] = actual

    manifest = _load_json(_MANIFEST)
    contract = _load_json(_T22)
    t18 = _load_json(_T18_EVIDENCE)
    descriptor = _layer33_descriptor(manifest, contract)
    golden = t18.get("golden", {})
    if (t18.get("task") != "S2A-T18" or t18.get("result") != "PASS" or
            t18.get("mode") != "FULL" or
            golden.get("expected_output_byte_count") != descriptor["output_length_bytes"] or
            golden.get("expected_output_sha256") != "39d1494ec1dfa28846aebfd56bff2396c5610c60873c99cae6186d8f3ea4a9ab" or
            golden.get("input_sha256") != "e4a755bd4b0e34607c3d245adc640aaf427e1f6d2a25f1cd39a33fb9bb51abcb"):
        raise AssertionError("T18 完整层黄金或层33 input/output 摘要不匹配")

    dynamic_relatives = (_WRAPPER, _TB, _RUNNER, _TEST)
    for relative in dynamic_relatives:
        raw = _repo_path(relative).read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"T27 源文件必须为 UTF-8/LF：{relative.as_posix()}")
        raw.decode("utf-8")
        hashes[relative.as_posix()] = _sha256_bytes(raw)
    return hashes, manifest, contract, descriptor


def _initial_byte(address: int) -> int:
    """重现冻结 T10 memory model 的初始 byte 函数。"""
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _materialize_golden(descriptor: dict[str, Any]) -> tuple[bytes, bytes]:
    """按 manifest 张量形状构造输入与 NCHW 最近邻复制黄金。"""
    channels, input_height, input_width = descriptor["input_shape_nchw"][1:]
    output_channels, output_height, output_width = descriptor["output_shape_nchw"][1:]
    if (channels != output_channels or
            descriptor["input_length_bytes"] != channels * input_height * input_width or
            descriptor["output_length_bytes"] != output_channels * output_height * output_width):
        raise AssertionError("layer33 NCHW byte count 与张量描述不一致")
    input_bytes = bytes(
        _initial_byte(descriptor["input_address"] + offset)
        for offset in range(descriptor["input_length_bytes"])
    )
    expected = bytearray()
    for channel in range(channels):
        for y in range(output_height):
            for x in range(output_width):
                source_offset = (channel * input_height + y // descriptor["stride"]) * input_width + x // descriptor["stride"]
                expected.append(input_bytes[source_offset])
    result = bytes(expected)
    if (len(result) != descriptor["output_length_bytes"] or
            _sha256_bytes(input_bytes) != "e4a755bd4b0e34607c3d245adc640aaf427e1f6d2a25f1cd39a33fb9bb51abcb" or
            _sha256_bytes(result) != "39d1494ec1dfa28846aebfd56bff2396c5610c60873c99cae6186d8f3ea4a9ab"):
        raise AssertionError("T10 派生输入或独立 nearest-repeat 黄金摘要不匹配")
    return input_bytes, result


def _write_memory_ranges(manifest: dict[str, Any], work: Path) -> tuple[str, int]:
    """从 tiny416 manifest 生成 T10 所需 feature tensor 地址范围。"""
    ranges: set[tuple[int, int]] = set()
    for layer in manifest["layers"]:
        if layer.get("op") == "yolo":
            continue
        start = int(layer["tensor_address"])
        end = start + int(layer["tensor_length_bytes"])
        ranges.add((start, end))
    ordered = sorted(ranges)
    if len(ordered) != 36:
        raise AssertionError(f"T10 feature range 数应为 36，实为 {len(ordered)}")
    for left, right in zip(ordered, ordered[1:], strict=False):
        if left[1] > right[0]:
            raise AssertionError("manifest feature tensor byte ranges 重叠")
    input_desc = manifest["address_map"]["input"]
    weight_desc = manifest["address_map"]["weight_package"]
    lines = [
        f"{int(input_desc['address']):08X} "
        f"{int(input_desc['address']) + int(input_desc['length_bytes']):08X} "
        f"{int(weight_desc['address']):08X} "
        f"{int(weight_desc['address']) + int(weight_desc['length_bytes']):08X} "
        f"{len(ordered):08X}"
    ]
    lines.extend(f"{start:08X} {end:08X}" for start, end in ordered)
    payload = ("\n".join(lines) + "\n").encode("ascii")
    target = work / "memory_ranges.dat"
    if target.exists():
        raise FileExistsError(f"T10 range file already exists：{target}")
    target.write_bytes(payload)
    return _sha256_bytes(payload), len(ordered)


def _tool_version(tool: Path) -> str:
    """读取 Vivado Simulator 工具版本。"""
    command = f'cmd.exe /d /s /c "{tool} -version"'
    result = subprocess.run(
        command, shell=False, cwd=_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"{tool.name} -version exit={result.returncode}: {output[-1200:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise RuntimeError(f"无法解析 {tool.name} 版本：{output[-1200:]}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _command_text(tool: Path, args: list[str]) -> str:
    """生成供 cmd.exe 和证据记录使用的命令文本。"""
    return " ".join(f'"{item}"' if (" " in item or "&" in item) else item
                     for item in [str(tool), *args])


def _terminate_tree(process: subprocess.Popen[str]) -> None:
    """只终止本 runner 创建的工具进程树。"""
    if process.poll() is None:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, text=True, check=False)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _run_logged(tool: Path, args: list[str], work: Path, log_path: Path,
                deadline: float, progress_timeout: float | None = None
                ) -> tuple[int, float, list[str]]:
    """执行 Vivado 工具并实时保留唯一临时日志及进度标记。"""
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
            if now > deadline:
                _terminate_tree(process)
                raise TimeoutError(f"Vivado 整体运行超过 {_TOTAL_TIMEOUT_SECONDS}s：{log_path}")
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
                last_progress = time.monotonic()
    reader.join(timeout=5)
    return int(process.wait()), time.monotonic() - started, checkpoints


def _assert_no_vivado_processes() -> None:
    """拒绝在已有 Vivado Simulator 进程时启动本次验证。"""
    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                            text=True, encoding="utf-8", errors="replace", check=True)
    names = {line.split(",", 1)[0].strip('"').lower()
             for line in result.stdout.splitlines() if line.strip()}
    active = sorted(names.intersection({"vivado.exe", "xvlog.exe", "xelab.exe", "xsim.exe"}))
    if active:
        raise RuntimeError(f"检测到已有相关 Vivado 进程：{', '.join(active)}")


def _parse_result(log_path: Path, mode: str) -> dict[str, int]:
    """检查仿真只产生一个结果摘要和一个 PASS 标记。"""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?im)^\s*(?:FAIL:|FATAL:|ERROR:)", text):
        raise AssertionError(f"xsim 日志含失败诊断：{log_path}")
    if mode == "quick":
        pattern = (r"RESULT mode=QUICK timeout_abort=(\d+) "
                   r"hard_reset_pending_write=(\d+) soft_reset_pending_write=(\d+)")
        marker = "PASS S2A-T27 G0 shell-child control smoke"
        keys = ("timeout_abort", "hard_reset_pending_write", "soft_reset_pending_write")
    else:
        pattern = (r"RESULT layer33_bytes=(\d+) reads=(\d+) writes=(\d+) "
                   r"terminal_events=(\d+) stalls=(\d+) timeout_abort=(\d+) "
                   r"hard_reset_pending_write=(\d+) soft_reset_pending_write=(\d+) recovery=(\d+)")
        marker = "PASS S2A-T27 G0 shell-child layer33 pilot"
        keys = ("layer33_bytes", "reads", "writes", "terminal_events", "stalls",
                "timeout_abort", "hard_reset_pending_write", "soft_reset_pending_write", "recovery")
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1 or text.count(marker) != 1 or matches[0].end() > text.index(marker):
        raise AssertionError(f"xsim 结果或 PASS 标记缺失/重复：{log_path}")
    values = dict(zip(keys, map(int, matches[0].groups()), strict=True))
    expected = ({"timeout_abort": 1, "hard_reset_pending_write": 1,
                 "soft_reset_pending_write": 1} if mode == "quick" else
                {"layer33_bytes": 86528, "reads": 86528, "writes": 86528,
                 "terminal_events": 1, "timeout_abort": 1,
                 "hard_reset_pending_write": 1, "soft_reset_pending_write": 1,
                 "recovery": 1})
    for name, expected_value in expected.items():
        if values[name] != expected_value:
            raise AssertionError(f"仿真摘要 {name}={values[name]}，应为 {expected_value}")
    if mode == "full" and values["stalls"] <= 0:
        raise AssertionError("T10 memory backpressure/stall 未被覆盖")
    return values


def _verify_trace(trace: Path, expected: bytes) -> tuple[str, int]:
    """逐行解析所有 output byte 并与独立 CPU nearest-repeat 黄金比较。"""
    if not trace.is_file():
        raise AssertionError("xsim 未生成 layer33 output trace")
    rows = trace.read_text(encoding="ascii").splitlines()
    if len(rows) != len(expected) or any(not re.fullmatch(r"[0-9a-fA-F]{2}", row) for row in rows):
        raise AssertionError(f"output trace byte 数/格式错误：{len(rows)}")
    actual = bytes(int(row, 16) for row in rows)
    mismatch = next((index for index, (observed, golden) in enumerate(
        zip(actual, expected, strict=True)) if observed != golden), None)
    if mismatch is not None:
        raise AssertionError(
            f"逐 byte golden mismatch offset={mismatch} actual={actual[mismatch]:02x} "
            f"expected={expected[mismatch]:02x}"
        )
    return _sha256_bytes(actual), len(actual)


def run(mode: str) -> dict[str, Any]:
    """运行 quick 控制预检或完整 layer33 仿真。"""
    if mode not in {"quick", "full"}:
        raise ValueError(f"未知仿真模式：{mode}")
    if mode == "full" and _EVIDENCE_DIR.exists():
        raise FileExistsError(f"T27 evidence 目录已存在，拒绝覆盖：{_EVIDENCE_DIR}")
    started = time.monotonic()
    deadline = started + _TOTAL_TIMEOUT_SECONDS
    frozen_hashes, manifest, contract, descriptor = _verify_frozen_bindings()
    input_bytes, expected_bytes = _materialize_golden(descriptor)
    _assert_no_vivado_processes()

    tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
    for path in tools.values():
        if not path.is_file():
            raise FileNotFoundError(f"Vivado executable 不存在：{path}")
    versions = {name: _tool_version(path) for name, path in tools.items()}
    if any("2026.1" not in version for version in versions.values()):
        raise AssertionError(f"Vivado Simulator 版本与冻结 T18 不符：{versions}")

    work_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t27_layer33_{mode}_", dir=work_parent))
    try:
        if os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) == str(_ROOT.resolve()):
            raise RuntimeError(f"临时仿真目录不能位于仓库内：{work}")
    except ValueError:
        pass
    range_sha, range_count = _write_memory_ranges(manifest, work)

    compile_phases: list[dict[str, Any]] = []
    sources = [
        _repo_path(_QUERY), _repo_path(_ENGINE), _repo_path(_SCHEDULER),
        _repo_path(_CSR), _repo_path(_T12_MASTER), _repo_path(_SHELL),
        _repo_path(_WRAPPER), _repo_path(_T10_MODEL), _repo_path(_TB),
    ]
    commands: list[tuple[str, list[str]]] = [
        ("xvlog", ["-sv", *[str(path) for path in sources]]),
        ("xelab", ["-top", "tb_s2a_runtime_layer33_pilot",
                   "-snapshot", "s2a_runtime_layer33_pilot_snapshot"]),
    ]
    for phase, args in commands:
        log = work / f"{phase}_command.log"
        exit_code, elapsed, checkpoints = _run_logged(
            tools[phase], args, work, log, deadline,
        )
        compile_phases.append({
            "phase": phase,
            "exit_code": exit_code,
            "elapsed_seconds": round(elapsed, 3),
            "log_file": log.name,
            "command": _command_text(tools[phase], args),
            "progress_checkpoints": checkpoints,
        })
        if exit_code != 0:
            raise RuntimeError(f"{phase} exit={exit_code}; 日志：{log}")

    sim_args = ["-R", "s2a_runtime_layer33_pilot_snapshot"]
    if mode == "quick":
        sim_args.extend(["-testplusarg", "QUICK"])
    sim_log = work / "xsim_command.log"
    sim_exit, sim_elapsed, checkpoints = _run_logged(
        tools["xsim"], sim_args, work, sim_log, deadline,
        progress_timeout=_NO_PROGRESS_SECONDS,
    )
    compile_phases.append({
        "phase": "xsim",
        "exit_code": sim_exit,
        "elapsed_seconds": round(sim_elapsed, 3),
        "log_file": sim_log.name,
        "command": _command_text(tools["xsim"], sim_args),
        "progress_checkpoints": checkpoints,
        "no_progress_stop_seconds": _NO_PROGRESS_SECONDS,
    })
    if sim_exit != 0:
        raise RuntimeError(f"xsim exit={sim_exit}; 日志：{sim_log}")
    summary = _parse_result(sim_log, mode)

    output_sha: str | None = None
    output_count = 0
    if mode == "full":
        output_sha, output_count = _verify_trace(work / _TRACE_NAME, expected_bytes)

    after_hashes, _, _, after_descriptor = _verify_frozen_bindings()
    if after_hashes != frozen_hashes or after_descriptor != descriptor:
        raise AssertionError("仿真期间固定来源或 T27 代码发生变化")
    elapsed = round(time.monotonic() - started, 3)
    result: dict[str, Any] = {
        "schema_version": "gestureforge_s2a_t27_layer33_shell_child_v1",
        "task_id": "S2A-T27",
        "result": "PASS",
        "mode": mode.upper(),
        "scope": "单层 tiny416 layer33 shell-child pilot；不是通用38层 dispatcher，不代表 G4/G5",
        "source_bindings": [
            {"path": name, "sha256": digest}
            for name, digest in sorted(frozen_hashes.items())
        ],
        "layer33": descriptor,
        "golden": {
            "input_byte_count": len(input_bytes),
            "input_sha256": _sha256_bytes(input_bytes),
            "output_byte_count": output_count,
            "expected_output_sha256": _sha256_bytes(expected_bytes),
            "observed_output_sha256": output_sha,
            "comparison": "逐项对 86,528 个 NCHW byte 与冻结 T10 initial_byte 输入及独立 nearest-repeat CPU oracle 比较",
        },
        "control_and_memory": {
            "ps_visible_abi": "原样实例化冻结 G0 s2a_runtime_shell；CSR/register semantics 未修改",
            "child_start": "单周期 G0 backend_start 驱动 layer33 scheduler start_valid",
            "terminal_event": "child done/error 生成无 backpressure operator_result_valid；成功路径逐任务恰 1 个单周期事件",
            "abort_equivalence": "child scheduler backend_cancel 与 G0 shell cancel_master 同为 hard_reset || backend_abort || 接受的 soft_reset",
            "global_timeout": "由冻结 G0 CSR 单一 whole-task deadline 触发；不在 layer33 内重新计时",
            "memory_master": "冻结 T12 单 outstanding master；memory stall request 字段由 T10 模型检查稳定",
        },
        "simulation": {
            "summary": summary,
            "tool_versions": versions,
            "phases": compile_phases,
            "memory_ranges_sha256": range_sha,
            "memory_ranges_count": range_count,
            "temporary_log_directory_name": work.name,
            "elapsed_seconds": elapsed,
            "overall_timeout_seconds": _TOTAL_TIMEOUT_SECONDS,
            "no_progress_stop_seconds": _NO_PROGRESS_SECONDS,
        },
        "synthesis": "NOT_EXECUTED：此 pilot 不含综合检查或资源估算",
        "board_validation": "NOT_APPLICABLE：未执行上板或实物操作",
        "g4_status": "NOT_MET",
        "g5_status": "NOT_MET",
    }
    if mode == "full":
        evidence_parent = _ROOT / _EVIDENCE_DIR.parent
        if not evidence_parent.is_dir():
            raise FileNotFoundError(f"T27 evidence 父目录不存在：{_EVIDENCE_DIR.parent.as_posix()}")
        if _EVIDENCE_DIR.exists() or _EVIDENCE.exists():
            raise FileExistsError(f"拒绝覆盖 T27 evidence：{_EVIDENCE_DIR}")
        payload = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        evidence_dir = evidence_parent / _EVIDENCE_DIR.name
        evidence_dir.mkdir()
        with (evidence_dir / _EVIDENCE.name).open("xb") as evidence_file:
            evidence_file.write(payload)
            evidence_file.flush()
            os.fsync(evidence_file.fileno())
        result["evidence_path"] = _EVIDENCE.as_posix()
        result["evidence_sha256"] = _sha256_bytes(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    """解析 CLI 参数并返回验证状态。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("quick", "full"), required=True)
    args = parser.parse_args()
    try:
        run(args.mode)
    except Exception as exc:
        print(f"FAIL S2A-T27 mode={args.mode}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
