"""运行 S2A-T19 tiny416 layer34 双输入 route 整层调度器 RTL 验证。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
_BASELINE_HEAD = "e1d2026635281d75efdb9e6562e5b74c134fa8a7"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_ROUTE_QUERY = _ROOT / "src/int8_route_query.sv"
_T15_ENGINE = _ROOT / "src/s2a_route_engine.sv"
_T15_TB = _ROOT / "sim/tb_s2a_route_engine.sv"
_T15_RUNNER = _ROOT / "verification/test_s2a_route_engine_rtl.py"
_T15_EVIDENCE = _ROOT / "report/evidence/S2A-T15/route_simulation.json"
_T06_RUNNER = _ROOT / "verification/test_s2a_route_rtl.py"
_T06_EVIDENCE = _ROOT / "report/evidence/S2A-T06/route_query_simulation.json"
_T10_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_T12_MASTER = _ROOT / "src/s2a_memory_master.sv"
_T18_SCHEDULER = _ROOT / "src/s2a_upsample_layer_scheduler.sv"
_T18_TB = _ROOT / "sim/tb_s2a_upsample_layer_scheduler.sv"
_T18_RUNNER = _ROOT / "verification/test_s2a_upsample_layer_scheduler_rtl.py"
_T18_EVIDENCE = _ROOT / "report/evidence/S2A-T18/upsample_layer_scheduler_simulation.json"
_SCHEDULER = _ROOT / "src/s2a_route_layer_scheduler.sv"
_TB = _ROOT / "sim/tb_s2a_route_layer_scheduler.sv"
_RUNNER = Path(__file__).resolve()
_EVIDENCE = _ROOT / "report/evidence/S2A-T19/route_layer_scheduler_simulation.json"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")

_EXPECTED_HASHES = {
    "g0_spec_sha256": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "manifest_sha256": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "route_query_sha256": "2f13e90858f6e665cf05444aac8e4db396b09f798acedd51e37bfd2c56f1dd64",
    "t15_engine_sha256": "4748df19474e6b90e11bb760854311da92ba8d19a5b1d4b12e3d7b2b7968fe44",
    "t15_testbench_sha256": "8de3c9bb146527e8017faa919b9b591397ee90bacc36aaed3f742ed3413586eb",
    "t15_runner_sha256": "f49d00c24e22850024209872504bcf5a93165eaf79c2b04fad15f6056e163937",
    "t15_evidence_sha256": "6011c3272c05b8e428128410b0d7a25a689873a12404631f23dc707f1fa9f124",
    "t06_runner_sha256": "bfd661391b234a97e66f6cadd73d7c2d323b4099203eeed46aa6397082286934",
    "t06_evidence_sha256": "9237d06d387209281789ab966b4e0e987b9f07a87c7103e7e112de62d3d7632a",
    "t10_memory_model_sha256": "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
    "t12_memory_master_sha256": "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    "t18_scheduler_sha256": "1473fd371c65658e105ff2ad575d523a98a53e5c5ebd8bb9f21ca33b61678bce",
    "t18_testbench_sha256": "ec15fd8a86a6c63e1a0ffa2fe4059c644cb61a78cd01f1ebef03901f917469de",
    "t18_runner_sha256": "c8ddc62aae0a1da19379c600349de4380287afec85f82727828b0cd55ec5af1b",
    "t18_evidence_sha256": "0f2a4a81275ffa225babb78b767bfc42a597320308ef7b150af5f80fd6aac35d",
}
_SOURCE0_BASE = 27619968
_SOURCE0_BYTES = 86528
_SOURCE1_BASE = 26727936
_SOURCE1_BYTES = 173056
_OUTPUT_BASE = 27706496
_OUTPUT_BYTES = 259584
_INPUT_BYTES = _SOURCE0_BYTES + _SOURCE1_BYTES
_SOURCE0_SCALE = 0.145512708528774
_SOURCE1_SCALE = 0.1594378704161156
_OUTPUT_SCALE = 0.1594378704161156
_RANDOM_SEED = 0x2A202609
_SOURCE0_Q31 = 1959924335
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_OVERALL_TIMEOUT_SECONDS = 7200
_NO_PROGRESS_TIMEOUT_SECONDS = 1800


def _sha256_bytes(payload: bytes) -> str:
    """计算 byte 序列 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _frozen_paths() -> dict[str, Path]:
    """列出冻结规格、先行实现和证据入口。"""
    return {
        "g0_spec_sha256": _G0_SPEC,
        "manifest_sha256": _MANIFEST,
        "route_query_sha256": _ROUTE_QUERY,
        "t15_engine_sha256": _T15_ENGINE,
        "t15_testbench_sha256": _T15_TB,
        "t15_runner_sha256": _T15_RUNNER,
        "t15_evidence_sha256": _T15_EVIDENCE,
        "t06_runner_sha256": _T06_RUNNER,
        "t06_evidence_sha256": _T06_EVIDENCE,
        "t10_memory_model_sha256": _T10_MODEL,
        "t12_memory_master_sha256": _T12_MASTER,
        "t18_scheduler_sha256": _T18_SCHEDULER,
        "t18_testbench_sha256": _T18_TB,
        "t18_runner_sha256": _T18_RUNNER,
        "t18_evidence_sha256": _T18_EVIDENCE,
    }


def _read_frozen_spec() -> tuple[str, dict[str, str], dict, dict, dict, dict]:
    """校验冻结来源哈希和 layer34 的张量、拼接及 scale 语义。"""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
        text=True, encoding="utf-8", check=True,
    ).stdout.strip()
    if head != _BASELINE_HEAD:
        raise AssertionError(f"T19 baseline HEAD 已变化：{head}")
    paths = _frozen_paths()
    hashes = {name: _sha256_file(path) for name, path in paths.items()}
    for name, expected in _EXPECTED_HASHES.items():
        if hashes[name] != expected:
            raise AssertionError(f"冻结引用 {name} SHA-256 不匹配：{hashes[name]}")
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    by_index = {int(layer["layer_index"]): layer for layer in manifest["layers"]}
    layer = by_index[34]
    source0 = by_index[33]
    source1 = by_index[23]
    expected = {
        "layer_index": 34,
        "cfg_section": 35,
        "op": "route",
        "input_tensor_indices": [33, 23],
        "input_shape_nchw": [[1, 128, 26, 26], [1, 256, 26, 26]],
        "input_scales": [_SOURCE0_SCALE, _SOURCE1_SCALE],
        "route_groups": 1,
        "route_group_id": 0,
        "route_source_channel_ranges": [[0, 128], [0, 256]],
        "output_shape_nchw": [1, 384, 26, 26],
        "output_scale": _OUTPUT_SCALE,
        "tensor_address": _OUTPUT_BASE,
        "tensor_length_bytes": _OUTPUT_BYTES,
        "layout": "NCHW",
        "element_type": "int8_twos_complement",
    }
    for key, value in expected.items():
        if layer.get(key) != value:
            raise AssertionError(f"G0 layer34 {key}={layer.get(key)!r}，期望 {value!r}")
    if (source0.get("tensor_address") != _SOURCE0_BASE or
            source0.get("tensor_length_bytes") != _SOURCE0_BYTES or
            source0.get("output_shape_nchw") != [1, 128, 26, 26] or
            source1.get("tensor_address") != _SOURCE1_BASE or
            source1.get("tensor_length_bytes") != _SOURCE1_BYTES or
            source1.get("output_shape_nchw") != [1, 256, 26, 26]):
        raise AssertionError("layer34 两个来源的冻结地址、形状或长度发生变化")
    if _OUTPUT_BASE + _OUTPUT_BYTES != 27966080:
        raise AssertionError("输出半开区间末端应为 27966080")
    ratio = _SOURCE0_SCALE / _OUTPUT_SCALE
    multiplier = math.floor(ratio * (1 << 31) + 0.5)
    if multiplier != _SOURCE0_Q31:
        raise AssertionError(f"T15 Q31 multiplier {multiplier} != {_SOURCE0_Q31}")
    return head, hashes, manifest, layer, source0, source1


def _xorshift32(value: int) -> int:
    """与 testbench 一致的固定 32-bit xorshift PRNG 步进。"""
    value = (value ^ ((value << 13) & 0xFFFFFFFF)) & 0xFFFFFFFF
    value ^= value >> 17
    value = (value ^ ((value << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF
    return value


def _input_and_golden() -> tuple[bytes, bytes]:
    """产生两个 NCHW 输入及按原 scale 独立舍入的完整输出黄金。"""
    state = _RANDOM_SEED
    source0_values: list[int] = []
    source1_values: list[int] = []
    for target, count in ((source0_values, _SOURCE0_BYTES),
                          (source1_values, _SOURCE1_BYTES)):
        for _ in range(count):
            state = _xorshift32(state)
            target.append((state % 255) - 127)
    input_bytes = bytes(value & 0xFF for value in source0_values + source1_values)
    ratio = _SOURCE0_SCALE / _OUTPUT_SCALE
    source0_output = bytearray()
    for value in source0_values:
        scaled = value * ratio
        rounded = math.floor(scaled + 0.5) if scaled >= 0 else math.ceil(scaled - 0.5)
        source0_output.append(max(-127, min(127, rounded)) & 0xFF)
    expected = bytes(source0_output) + bytes(value & 0xFF for value in source1_values)
    if len(input_bytes) != _INPUT_BYTES or len(expected) != _OUTPUT_BYTES:
        raise AssertionError("输入或黄金 byte 数量错误")
    if 0x80 in input_bytes:
        raise AssertionError("输入 PRNG 产生 raw -128 sentinel")
    return input_bytes, expected


def _write_memory_ranges(manifest: dict, work: Path) -> tuple[str, int]:
    """按冻结 manifest 生成 T10 memory model 范围文件。"""
    ranges = sorted({
        (int(layer["tensor_address"]),
         int(layer["tensor_address"]) + int(layer["tensor_length_bytes"]))
        for layer in manifest["layers"] if layer.get("op") != "yolo"
    })
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise AssertionError("manifest feature ranges 重叠")
    if len(ranges) != 36 or (_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES) not in ranges:
        raise AssertionError("manifest-derived T10 feature ranges 数量或输出范围错误")
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


def _tool_version(tool: Path) -> str:
    """读取并缩短 Vivado 工具版本文本。"""
    command = f'cmd.exe /d /s /c "{tool} -version"'
    result = subprocess.run(command, shell=False, cwd=_ROOT, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=30)
    output = result.stdout + "\n" + result.stderr
    if result.returncode != 0:
        raise RuntimeError(f"{tool.name} -version exit={result.returncode}: {output[-1200:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise RuntimeError(f"无法解析 {tool.name} 版本：{output[-1200:]}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _command_text(tool: Path, args: list[str]) -> str:
    """为 Windows cmd.exe 构造可复现的命令文本。"""
    parts = [str(tool), *args]
    return " ".join(f'"{part}"' if (" " in part or "&" in part) else part
                    for part in parts)


def _terminate_process_tree(proc: subprocess.Popen[str]) -> None:
    """停止当前 runner 创建的工具进程树。"""
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
    """实时记录工具日志并按 overall/no-progress 限时停止。"""
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
                raise TimeoutError(f"全局时限 {_OVERALL_TIMEOUT_SECONDS}s 到期；日志：{log_path}")
            if progress_timeout is not None and now - last_progress > progress_timeout:
                _terminate_process_tree(proc)
                raise TimeoutError(f"xsim {progress_timeout}s 无 PROGRESS 行；日志：{log_path}")
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
    """解析唯一 RESULT 行并强制检查实际样本和控制计数。"""
    content = log_path.read_text(encoding="utf-8", errors="replace")
    marker = "PASS S2A-T19 focused smoke" if mode == "smoke" else \
             "PASS S2A-T19 complete layer34 route scheduler"
    if content.count(marker) != 1 or content.count("RESULT mode=") != 1:
        raise AssertionError(f"xsim RESULT/PASS 标记不唯一：{log_path}")
    row = next(line for line in content.splitlines() if line.startswith("RESULT mode="))
    values = {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", row)}
    if mode == "smoke":
        expected = {
            "pending_read_abort": 1, "pending_write_reset": 1,
            "error_hold": 3, "partial_writes": 2, "error_responses": 1,
        }
    else:
        expected = {
            "output_count": _OUTPUT_BYTES, "reads": _OUTPUT_BYTES,
            "writes": _OUTPUT_BYTES, "pending_read_abort": 1,
            "pending_write_reset": 1, "error_hold": 3,
            "busy_start_checks": 3, "completion_hold": 3,
            "recovery_runs": 1, "input_patches": _INPUT_BYTES,
            "output_patches": _OUTPUT_BYTES, "error_responses": 1,
        }
    for key, value in expected.items():
        if values.get(key) != value:
            raise AssertionError(f"xsim summary {key}={values.get(key)!r}，期望 {value}")
    if values.get("stalls", 0) < (1 if mode == "smoke" else 100000):
        raise AssertionError("scheduled stall 覆盖计数不足")
    return values


def _text_bindings() -> dict[str, Path]:
    """列出运行时应保持只读、UTF-8/LF 的源文件。"""
    result = _frozen_paths()
    result.update({
        "scheduler_rtl": _SCHEDULER,
        "testbench": _TB,
        "runner": _RUNNER,
    })
    return result


def _hash_utf8_lf(paths: dict[str, Path]) -> dict[str, str]:
    """验证 UTF-8/LF 编码并采集每个绑定文件的 SHA-256。"""
    hashes: dict[str, str] = {}
    for name, path in paths.items():
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"绑定文件不是 UTF-8/LF 原始文本：{path}")
        raw.decode("utf-8")
        hashes[name] = _sha256_bytes(raw)
    return hashes


def _run(mode: str) -> dict[str, object]:
    """运行 smoke 或 full，并在 full 通过后落盘证据。"""
    started = time.monotonic()
    deadline = started + _OVERALL_TIMEOUT_SECONDS
    head, frozen_hashes, manifest, layer, source0, source1 = _read_frozen_spec()
    bound_paths = _text_bindings()
    hashes_before = _hash_utf8_lf(bound_paths)
    input_bytes, expected_bytes = _input_and_golden()
    tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
    for path in tools.values():
        if not path.is_file():
            raise FileNotFoundError(f"Vivado 工具不存在：{path}")
    tool_versions = {name: _tool_version(path) for name, path in tools.items()}
    temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t19_layer34_{mode}_", dir=temp_parent))
    try:
        work_under_repo = (os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) ==
                           str(_ROOT.resolve()))
    except ValueError:
        work_under_repo = False
    if work_under_repo:
        raise RuntimeError(f"隔离仿真目录意外位于仓库：{work}")
    ranges_sha, range_count = _write_memory_ranges(manifest, work)
    phases: list[dict[str, object]] = []
    source_args = [
        str(_ROUTE_QUERY), str(_T15_ENGINE), str(_SCHEDULER),
        str(_T12_MASTER), str(_T10_MODEL), str(_TB),
    ]
    for phase, args in (
        ("xvlog", ["-sv", *source_args]),
        ("xelab", ["-top", "tb_s2a_route_layer_scheduler",
         "-snapshot", "s2a_route_layer_scheduler_snapshot"]),
    ):
        log = work / f"{phase}_command.log"
        code, elapsed, checkpoints = _run_logged(tools[phase], args, work, log, deadline)
        phases.append({"phase": phase, "command": _command_text(tools[phase], args),
                       "exit_code": code, "elapsed_seconds": round(elapsed, 3),
                       "log_path": str(log), "progress_checkpoints": checkpoints})
        if code != 0:
            raise RuntimeError(f"{phase} exit={code}; log={log}")

    sim_args = ["-R", "s2a_route_layer_scheduler_snapshot"]
    if mode == "smoke":
        sim_args.extend(["-testplusarg", "SMOKE"])
    sim_log = work / "xsim_command.log"
    sim_code, sim_elapsed, checkpoints = _run_logged(
        tools["xsim"], sim_args, work, sim_log, deadline,
        progress_timeout=_NO_PROGRESS_TIMEOUT_SECONDS,
    )
    phases.append({
        "phase": "xsim", "command": _command_text(tools["xsim"], sim_args),
        "exit_code": sim_code, "elapsed_seconds": round(sim_elapsed, 3),
        "log_path": str(sim_log),
        "no_progress_timeout_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
        "progress_checkpoints": checkpoints,
    })
    if sim_code != 0:
        raise RuntimeError(f"xsim exit={sim_code}; log={sim_log}")
    summary = _parse_summary(sim_log, mode)

    trace_path = work / "observed_output_hex.txt"
    observed = b""
    trace_sha = _sha256_file(trace_path) if trace_path.is_file() else None
    if mode == "full":
        rows = trace_path.read_text(encoding="ascii").splitlines()
        if len(rows) != _OUTPUT_BYTES or any(re.fullmatch(r"[0-9a-fA-F]{2}", row) is None
                                             for row in rows):
            raise AssertionError(f"full output trace 行数/格式错误：{len(rows)}")
        observed = bytes(int(row, 16) for row in rows)
        mismatch = next((i for i, (actual, expected) in enumerate(
            zip(observed, expected_bytes, strict=True)) if actual != expected), None)
        if mismatch is not None:
            raise AssertionError(
                f"independent Python golden mismatch index={mismatch} "
                f"observed={observed[mismatch]:02x} expected={expected_bytes[mismatch]:02x}"
            )
        if _sha256_bytes(observed) != _sha256_bytes(expected_bytes):
            raise AssertionError("逐 byte 比较通过但 observed/golden SHA 不同")

    hashes_after = _hash_utf8_lf(bound_paths)
    if hashes_before != hashes_after:
        raise AssertionError("运行期间冻结源文件发生变化")
    if {key: hashes_after[key] for key in _EXPECTED_HASHES} != _EXPECTED_HASHES:
        raise AssertionError("冻结依赖在仿真期间被修改")

    result: dict[str, object] = {
        "schema_version": "gestureforge_s2a_t19_route_layer_scheduler_v1",
        "task": "S2A-T19",
        "result": "PASS",
        "mode": mode.upper(),
        "base_commit": head,
        "scope": "tiny416 layer34 固定双输入 route/concat 整层调度 pilot；不代表整网或 G4/G5",
        "bindings": {
            "g0_spec_path": str(_G0_SPEC.relative_to(_ROOT)).replace("\\", "/"),
            "manifest_path": str(_MANIFEST.relative_to(_ROOT)).replace("\\", "/"),
            "route_query_path": str(_ROUTE_QUERY.relative_to(_ROOT)).replace("\\", "/"),
            "t15_engine_path": str(_T15_ENGINE.relative_to(_ROOT)).replace("\\", "/"),
            "t15_evidence_path": str(_T15_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "t06_evidence_path": str(_T06_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "t10_memory_model_path": str(_T10_MODEL.relative_to(_ROOT)).replace("\\", "/"),
            "t12_memory_master_path": str(_T12_MASTER.relative_to(_ROOT)).replace("\\", "/"),
            "t18_scheduler_path": str(_T18_SCHEDULER.relative_to(_ROOT)).replace("\\", "/"),
            **hashes_after,
            "memory_ranges_sha256": ranges_sha,
            "memory_ranges_count": range_count,
        },
        "layer34": {
            "cfg_section": 35,
            "source_order": [33, 23],
            "source0_nchw": [1, 128, 26, 26],
            "source0_base_address": _SOURCE0_BASE,
            "source0_length_bytes": _SOURCE0_BYTES,
            "source1_nchw": [1, 256, 26, 26],
            "source1_base_address": _SOURCE1_BASE,
            "source1_length_bytes": _SOURCE1_BYTES,
            "output_nchw": [1, 384, 26, 26],
            "output_base_address": _OUTPUT_BASE,
            "output_length_bytes": _OUTPUT_BYTES,
            "output_half_open_range": [_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES],
            "last_output_byte_address": _OUTPUT_BASE + _OUTPUT_BYTES - 1,
            "source0_scale": _SOURCE0_SCALE,
            "source1_scale": _SOURCE1_SCALE,
            "output_scale": _OUTPUT_SCALE,
            "source0_q31_multiplier": _SOURCE0_Q31,
            "source1_q31_multiplier": 1 << 31,
            "channel_selection": "out c[0,128) -> source0 c; out c[128,384) -> source1 c-128",
            "layout": "NCHW channel,row,column order",
        },
        "golden": {
            "generator": "xorshift32 seed 0x2A202609; each step maps state%255-127; source0 NCHW then source1 NCHW",
            "seed": _RANDOM_SEED,
            "input_byte_count": len(input_bytes),
            "input_sha256": _sha256_bytes(input_bytes),
            "raw_minus_128_count": 0,
            "expected_output_byte_count": len(expected_bytes),
            "expected_output_sha256": _sha256_bytes(expected_bytes),
            "oracle": "原始冻结 float scale 比例，half-away-from-zero 后饱和 [-127,127]；source1 比例为 1",
            "observed_output_sha256": _sha256_bytes(observed) if mode == "full" else None,
            "observed_hex_trace_sha256": trace_sha,
            "observed_hex_trace_path": str(trace_path) if trace_path.is_file() else None,
        },
        "verification": {
            "xsim_summary": summary,
            "full_output_bytewise_comparison": "completed" if mode == "full" else "not run in smoke",
            "reads_and_writes": summary.get("reads", 0),
            "scheduled_stalls": _STALL_SCHEDULE,
            "patch_capacity": 519168,
            "patch_capacity_semantics": "T10 holds 259584 seeded source bytes plus up to 259584 distinct output bytes",
            "tool_versions": tool_versions,
            "python_version": platform.python_version(),
            "phases": phases,
            "work_directory": str(work),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "overall_timeout_seconds": _OVERALL_TIMEOUT_SECONDS,
            "no_progress_stop_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
            "synthesis": "not executed; pilot task does not require synthesis",
            "board_validation": "not executed; no hardware access requested",
        },
    }
    if mode == "full":
        payload = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_bytes(payload)
        result["evidence_sha256"] = _sha256_bytes(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "full"), required=True)
    args = parser.parse_args()
    try:
        _run(args.mode)
    except Exception as error:
        print(f"FAIL S2A-T19: {type(error).__name__}: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
