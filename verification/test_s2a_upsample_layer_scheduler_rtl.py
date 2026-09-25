"""运行 S2A-T18 tiny416 layer33 整层调度器的 Vivado RTL 验证。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "0612eb80f1798bcbe8a0083e83fdecda5005f280"
_G0_SPEC = _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_T13_RTL = _ROOT / "src/s2a_upsample_engine.sv"
_T13_QUERY = _ROOT / "src/int8_upsample_query.sv"
_T13_TB = _ROOT / "sim/tb_s2a_upsample_engine.sv"
_T13_RUNNER = _ROOT / "verification/test_s2a_upsample_engine_rtl.py"
_T13_EVIDENCE = _ROOT / "report/evidence/S2A-T13/upsample_simulation.json"
_T12_MEMORY_MASTER = _ROOT / "src/s2a_memory_master.sv"
_T10_MEMORY_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_SCHEDULER = _ROOT / "src/s2a_upsample_layer_scheduler.sv"
_TB = _ROOT / "sim/tb_s2a_upsample_layer_scheduler.sv"
_RUNNER = Path(__file__).resolve()
_GITATTRIBUTES = _ROOT / ".gitattributes"
_EVIDENCE = _ROOT / "report/evidence/S2A-T18/upsample_layer_scheduler_simulation.json"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_EXPECTED_HASHES = {
    "g0_spec_sha256": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "manifest_sha256": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "t13_engine_sha256": "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b",
    "t13_query_sha256": "9212f70c31fab6c6e5a30551c5d1fd7b6eeeafa4c1f2cbd20fe157015faa370c",
    "t13_testbench_sha256": "bb2e9f83dd1a27f18d16538cd8cafd08c856e309fc5af53428e468e16fa43b9d",
    "t13_runner_sha256": "86c3ebded47494d7683f94a0dc57c3f732352e7b33321b561b553d02690e391a",
    "t13_evidence_sha256": "ee9c1c0cdd4500eac6398ef0eb0a893021aee3b66d4845e50930f7cfac15d04e",
    "t12_memory_master_sha256": "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07",
    "t10_memory_model_sha256": "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2",
}
_INPUT_BASE = 27598336
_INPUT_BYTES = 21632
_OUTPUT_BASE = 27619968
_OUTPUT_BYTES = 86528
_INPUT_SHAPE = [1, 128, 13, 13]
_OUTPUT_SHAPE = [1, 128, 26, 26]
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_OVERALL_TIMEOUT_SECONDS = 7200
_NO_PROGRESS_TIMEOUT_SECONDS = 1800


def _sha256_bytes(payload: bytes) -> str:
    """计算 byte 序列的 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _check_frozen_bindings() -> tuple[str, dict[str, str], dict, bytes]:
    """校验基线、冻结文档、模型清单和前序实现哈希。"""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
        text=True, encoding="utf-8", check=True,
    ).stdout.strip()
    if head != _BASELINE_HEAD:
        raise AssertionError(f"T18 baseline HEAD 已变化：{head}")
    paths = {
        "g0_spec_sha256": _G0_SPEC,
        "manifest_sha256": _MANIFEST,
        "t13_engine_sha256": _T13_RTL,
        "t13_query_sha256": _T13_QUERY,
        "t13_testbench_sha256": _T13_TB,
        "t13_runner_sha256": _T13_RUNNER,
        "t13_evidence_sha256": _T13_EVIDENCE,
        "t12_memory_master_sha256": _T12_MEMORY_MASTER,
        "t10_memory_model_sha256": _T10_MEMORY_MODEL,
    }
    hashes = {name: _sha256_file(path) for name, path in paths.items()}
    for name, expected in _EXPECTED_HASHES.items():
        if hashes[name] != expected:
            raise AssertionError(f"冻结引用 {name} SHA-256 不匹配：{hashes[name]}")
    manifest_raw = _MANIFEST.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    layers = manifest["layers"]
    by_index = {int(layer["layer_index"]): layer for layer in layers}
    layer = by_index[33]
    producer = by_index[32]
    if (layer.get("cfg_section") != 34 or layer.get("op") != "upsample" or
            layer.get("input_tensor_indices") != [32] or
            layer.get("input_shape_nchw") != _INPUT_SHAPE or
            layer.get("output_shape_nchw") != _OUTPUT_SHAPE or
            layer.get("layout") != "NCHW" or
            layer.get("element_type") != "int8_twos_complement" or
            layer.get("stride") != 2 or layer.get("method") != "nearest_repeat" or
            layer.get("input_scale") != layer.get("output_scale") or
            producer.get("tensor_address") != _INPUT_BASE or
            producer.get("tensor_length_bytes") != _INPUT_BYTES or
            layer.get("tensor_address") != _OUTPUT_BASE or
            layer.get("tensor_length_bytes") != _OUTPUT_BYTES):
        raise AssertionError("G0 manifest layer32/33 形状、地址、scale 或 nearest-repeat 语义改变")
    if _OUTPUT_BASE + _OUTPUT_BYTES != 27706496:
        raise AssertionError("layer33 输出半开区间末端计算不符")
    return head, hashes, manifest, manifest_raw


def _t10_initial_byte(address: int) -> int:
    """按冻结 T10 memory model initial_byte 规则生成一个 byte。"""
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _materialize_golden() -> tuple[bytes, bytes]:
    """生成完整 layer32 确定性输入和独立 nearest-repeat 输出黄金。"""
    input_bytes = bytes(_t10_initial_byte(_INPUT_BASE + offset)
                        for offset in range(_INPUT_BYTES))
    expected = bytearray()
    for channel in range(128):
        for output_y in range(26):
            for output_x in range(26):
                input_offset = ((channel * 13 + output_y // 2) * 13 +
                                output_x // 2)
                expected.append(input_bytes[input_offset])
    if len(expected) != _OUTPUT_BYTES:
        raise AssertionError(f"golden 输出数量非法：{len(expected)}")
    return input_bytes, bytes(expected)


def _write_memory_ranges(manifest: dict, work: Path) -> tuple[str, int]:
    """从 T01 manifest 生成 T10 byte-address 对象范围文件。"""
    ranges_set: set[tuple[int, int]] = set()
    for layer in manifest["layers"]:
        if layer.get("op") == "yolo":
            continue
        start = int(layer["tensor_address"])
        end = start + int(layer["tensor_length_bytes"])
        ranges_set.add((start, end))
    ranges = sorted(ranges_set)
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise AssertionError("manifest feature tensor ranges 有重叠")
    if len(ranges) != 36 or (_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES) not in ranges:
        raise AssertionError("manifest-derived feature ranges 不符合 T10 冻结 map")
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
    """读取并提取 Vivado 工具版本。"""
    command = f'cmd.exe /d /s /c "{tool} -version"'
    completed = subprocess.run(
        command, shell=False, cwd=_ROOT,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, check=False,
    )
    text = completed.stdout + "\n" + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(f"{tool.name} -version exit={completed.returncode}: {text[-1500:]}")
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", text)
    if match is None:
        raise RuntimeError(f"无法解析 {tool.name} 版本：{text[-1500:]}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _command_text(tool: Path, args: list[str]) -> str:
    """构造 cmd.exe 可执行的 Vivado 命令并保留证据文本。"""
    parts = [str(tool), *args]
    return " ".join(f'"{item}"' if (" " in item or "&" in item) else item
                    for item in parts)


def _run_logged(tool: Path, args: list[str], work: Path, log_path: Path,
                deadline: float, progress_timeout: float | None = None) -> tuple[int, float, list[str]]:
    """执行工具，将日志实时落盘并按进度或总时限停止。"""
    command = _command_text(tool, args)
    started = time.monotonic()
    proc = subprocess.Popen(
        f'cmd.exe /d /s /c "{command}"', shell=False, cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", bufsize=1,
    )
    messages: queue.Queue[str | None] = queue.Queue()

    def _reader() -> None:
        assert proc.stdout is not None
        for row in proc.stdout:
            messages.put(row)
        messages.put(None)

    reader = threading.Thread(target=_reader, daemon=True)
    reader.start()
    checkpoints: list[str] = []
    last_activity = started
    eof = False
    with log_path.open("w", encoding="utf-8", newline="\n") as log_file:
        while not eof or proc.poll() is None:
            now = time.monotonic()
            if now > deadline:
                _terminate_process_tree(proc)
                raise TimeoutError(f"总时限 {_OVERALL_TIMEOUT_SECONDS}s 到期；日志：{log_path}")
            if progress_timeout is not None and now - last_activity > progress_timeout:
                _terminate_process_tree(proc)
                raise TimeoutError(f"xsim {progress_timeout}s 没有日志进展；日志：{log_path}")
            try:
                row = messages.get(timeout=1)
            except queue.Empty:
                continue
            if row is None:
                eof = True
                continue
            log_file.write(row)
            log_file.flush()
            if row.startswith("PROGRESS "):
                last_activity = time.monotonic()
                checkpoints.append(row.strip())
                print(row.rstrip(), flush=True)
            elif progress_timeout is None:
                last_activity = time.monotonic()
    reader.join(timeout=5)
    elapsed = time.monotonic() - started
    return int(proc.wait()), elapsed, checkpoints


def _terminate_process_tree(proc: subprocess.Popen[str]) -> None:
    """仅终止本 runner 创建的 Vivado 命令进程树。"""
    if proc.poll() is None:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, text=True, check=False)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def _parse_summary(log_path: Path, mode: str) -> dict[str, int]:
    """校验唯一 xsim 结果摘要与 PASS 标记。"""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if "FAIL:" in text.upper() or re.search(r"(?im)^\s*(?:ERROR|FATAL)\s*:", text):
        raise AssertionError(f"xsim log 含失败诊断：{log_path}")
    if mode == "smoke":
        pattern = (r"RESULT mode=SMOKE pending_read_abort=(\d+) "
                   r"pending_write_reset=(\d+) error_hold=(\d+) "
                   r"partial_writes=(\d+) stalls=(\d+)")
        marker = "PASS S2A-T18 focused smoke"
        names = ("pending_read_abort", "pending_write_reset", "error_hold",
                 "partial_writes", "stalls")
    else:
        pattern = (r"RESULT mode=FULL output_count=(\d+) reads=(\d+) "
                   r"writes=(\d+) stalls=(\d+) error_responses=(\d+) "
                   r"pending_read_abort=(\d+) pending_write_reset=(\d+) "
                   r"busy_start_checks=(\d+) completion_hold=(\d+) "
                   r"error_hold=(\d+) recovery_runs=(\d+) cycles=(\d+)")
        marker = "PASS S2A-T18 full layer33 scheduler"
        names = ("output_count", "reads", "writes", "stalls", "error_responses",
                 "pending_read_abort", "pending_write_reset", "busy_start_checks",
                 "completion_hold", "error_hold", "recovery_runs", "cycles")
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1 or text.count(marker) != 1 or matches[0].end() > text.index(marker):
        raise AssertionError(f"xsim 结果摘要或 PASS 不唯一：{log_path}")
    summary = dict(zip(names, map(int, matches[0].groups()), strict=True))
    if mode == "smoke":
        expected = {"pending_read_abort": 1, "pending_write_reset": 1,
                    "error_hold": 3, "partial_writes": 16}
    else:
        expected = {"output_count": _OUTPUT_BYTES, "reads": _OUTPUT_BYTES,
                    "writes": _OUTPUT_BYTES, "error_responses": 1,
                    "pending_read_abort": 1, "pending_write_reset": 1,
                    "busy_start_checks": 3, "completion_hold": 3,
                    "error_hold": 3, "recovery_runs": 1}
    for name, value in expected.items():
        if summary[name] != value:
            raise AssertionError(f"仿真摘要 {name}={summary[name]}，期望 {value}")
    minimum_stalls = 1 if mode == "smoke" else 200000
    if summary["stalls"] < minimum_stalls:
        raise AssertionError(f"T10 scheduled stall 覆盖不足：{summary['stalls']}")
    return summary


def _assert_source_bytes(paths: dict[str, Path]) -> dict[str, str]:
    """确保所有绑定文本均为 UTF-8/LF 并采集哈希。"""
    hashes: dict[str, str] = {}
    for name, path in paths.items():
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") or b"\r\n" in raw:
            raise AssertionError(f"源码必须使用 UTF-8/LF：{path}")
        raw.decode("utf-8")
        hashes[name] = _sha256_bytes(raw)
    return hashes


def _run(mode: str) -> dict[str, object]:
    """运行 smoke 或 full 流程并在 full 成功后更新证据。"""
    started = time.monotonic()
    overall_deadline = started + _OVERALL_TIMEOUT_SECONDS
    head, frozen_hashes, manifest, manifest_raw = _check_frozen_bindings()
    bound_paths = {
        "scheduler_rtl": _SCHEDULER,
        "testbench": _TB,
        "runner": _RUNNER,
        "gitattributes": _GITATTRIBUTES,
        "t13_engine_rtl": _T13_RTL,
        "t13_query_rtl": _T13_QUERY,
        "t13_testbench": _T13_TB,
        "t13_runner": _T13_RUNNER,
        "t10_memory_model": _T10_MEMORY_MODEL,
        "t12_memory_master": _T12_MEMORY_MASTER,
        "g0_spec": _G0_SPEC,
        "manifest": _MANIFEST,
        "t13_evidence": _T13_EVIDENCE,
    }
    source_hashes_before = _assert_source_bytes(bound_paths)
    input_bytes, expected_bytes = _materialize_golden()
    tool_names = ("xvlog", "xelab", "xsim")
    tools = {name: _XILINX_BIN / f"{name}.bat" for name in tool_names}
    for tool in tools.values():
        if not tool.is_file():
            raise FileNotFoundError(f"Vivado tool 不存在：{tool}")
    tool_versions = {name: _tool_version(tool) for name, tool in tools.items()}
    temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix=f"s2a_t18_layer33_{mode}_", dir=temp_parent))
    try:
        work_under_repo = (os.path.commonpath((str(work.resolve()), str(_ROOT.resolve()))) ==
                           str(_ROOT.resolve()))
    except ValueError:
        work_under_repo = False
    if work_under_repo:
        raise RuntimeError(f"仿真目录落入仓库：{work}")
    ranges_sha, range_count = _write_memory_ranges(manifest, work)
    compile_phases: list[dict[str, object]] = []
    commands = [
        ("xvlog", ["-sv", str(_T13_QUERY), str(_T13_RTL), str(_SCHEDULER),
                   str(_T12_MEMORY_MASTER), str(_T10_MEMORY_MODEL), str(_TB)]),
        ("xelab", ["-top", "tb_s2a_upsample_layer_scheduler",
                   "-snapshot", "s2a_upsample_layer_scheduler_snapshot"]),
    ]
    for phase, args in commands:
        log = work / f"{phase}_command.log"
        exit_code, elapsed, _ = _run_logged(
            tools[phase], args, work, log,
            overall_deadline,
        )
        compile_phases.append({
            "phase": phase,
            "command": _command_text(tools[phase], args),
            "exit_code": exit_code,
            "elapsed_seconds": round(elapsed, 3),
            "log_path": str(log),
        })
        if exit_code != 0:
            raise RuntimeError(f"{phase} exit={exit_code}; log={log}")

    sim_args = ["-R", "s2a_upsample_layer_scheduler_snapshot"]
    if mode == "smoke":
        sim_args.extend(["-testplusarg", "SMOKE"])
    xsim_log = work / "xsim_command.log"
    xsim_exit, xsim_elapsed, checkpoints = _run_logged(
        tools["xsim"], sim_args, work, xsim_log,
        overall_deadline,
        progress_timeout=_NO_PROGRESS_TIMEOUT_SECONDS,
    )
    compile_phases.append({
        "phase": "xsim",
        "command": _command_text(tools["xsim"], sim_args),
        "exit_code": xsim_exit,
        "elapsed_seconds": round(xsim_elapsed, 3),
        "log_path": str(xsim_log),
        "no_progress_timeout_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
        "progress_checkpoints": checkpoints,
    })
    if xsim_exit != 0:
        raise RuntimeError(f"xsim exit={xsim_exit}; log={xsim_log}")
    summary = _parse_summary(xsim_log, mode)

    trace_path = work / "observed_output_hex.txt"
    trace_sha = _sha256_file(trace_path) if trace_path.is_file() else None
    observed_bytes = b""
    if mode == "full":
        if not trace_path.is_file():
            raise AssertionError("full xsim 未生成逐 byte output trace")
        rows = trace_path.read_text(encoding="ascii").splitlines()
        if len(rows) != _OUTPUT_BYTES or any(not re.fullmatch(r"[0-9a-fA-F]{2}", row)
                                             for row in rows):
            raise AssertionError(f"output trace 行数或 byte 格式错误：{len(rows)}")
        observed_bytes = bytes(int(row, 16) for row in rows)
        mismatch = next((index for index, (actual, expected) in enumerate(
            zip(observed_bytes, expected_bytes, strict=True)) if actual != expected), None)
        if mismatch is not None:
            raise AssertionError(
                f"逐 byte 黄金比较失败 index={mismatch} "
                f"actual={observed_bytes[mismatch]:02x} expected={expected_bytes[mismatch]:02x}"
            )
        if _sha256_bytes(observed_bytes) != _sha256_bytes(expected_bytes):
            raise AssertionError("output trace SHA-256 与独立 CPU golden 不一致")

    source_hashes_after = _assert_source_bytes(bound_paths)
    if source_hashes_before != source_hashes_after:
        raise AssertionError("验证过程发生源文件变更")
    final_hashes = dict(frozen_hashes)
    final_hashes.update(source_hashes_after)
    if _sha256_file(_MANIFEST) != _EXPECTED_HASHES["manifest_sha256"]:
        raise AssertionError("仿真期间 G0 manifest 改变")

    result: dict[str, object] = {
        "schema_version": "gestureforge_s2a_t18_upsample_layer_scheduler_v1",
        "task": "S2A-T18",
        "result": "PASS",
        "mode": mode.upper(),
        "base_commit": head,
        "scope": "tiny416 layer33 整层 nearest-repeat 调度 pilot；不代表完整网络或阶段 G4/G5",
        "bindings": {
            "g0_spec_path": str(_G0_SPEC.relative_to(_ROOT)).replace("\\", "/"),
            "manifest_path": str(_MANIFEST.relative_to(_ROOT)).replace("\\", "/"),
            "t13_engine_path": str(_T13_RTL.relative_to(_ROOT)).replace("\\", "/"),
            "t13_query_path": str(_T13_QUERY.relative_to(_ROOT)).replace("\\", "/"),
            "t13_evidence_path": str(_T13_EVIDENCE.relative_to(_ROOT)).replace("\\", "/"),
            "t10_memory_model_path": str(_T10_MEMORY_MODEL.relative_to(_ROOT)).replace("\\", "/"),
            "t12_memory_master_path": str(_T12_MEMORY_MASTER.relative_to(_ROOT)).replace("\\", "/"),
            **final_hashes,
            "memory_ranges_sha256": ranges_sha,
            "memory_ranges_count": range_count,
        },
        "layer33": {
            "cfg_section": 34,
            "input_nchw": _INPUT_SHAPE,
            "input_base_address": _INPUT_BASE,
            "input_length_bytes": _INPUT_BYTES,
            "output_nchw": _OUTPUT_SHAPE,
            "output_base_address": _OUTPUT_BASE,
            "output_length_bytes": _OUTPUT_BYTES,
            "output_half_open_range": [_OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_BYTES],
            "last_output_byte_address": _OUTPUT_BASE + _OUTPUT_BYTES - 1,
            "stride": 2,
            "input_scale": 0.145512708528774,
            "output_scale": 0.145512708528774,
            "layout": "NCHW channel,row,column order",
            "mapping": "input(c, output_y//2, output_x//2), byte unchanged",
        },
        "golden": {
            "generator": "T10 initial_byte(address) = address[7:0] XOR [15:8] XOR [23:16] XOR [31:24] XOR 0xA5",
            "input_byte_count": len(input_bytes),
            "input_sha256": _sha256_bytes(input_bytes),
            "expected_output_byte_count": len(expected_bytes),
            "expected_output_sha256": _sha256_bytes(expected_bytes),
            "comparison": "all output writes in NCHW order compared byte-for-byte with independent Python nearest-repeat mapping",
            "observed_output_sha256": _sha256_bytes(observed_bytes) if mode == "full" else None,
            "observed_hex_trace_sha256": trace_sha,
            "observed_hex_trace_path": str(trace_path) if trace_path.is_file() else None,
        },
        "verification": {
            "xsim_summary": summary,
            "protocol": "one outstanding T12 memory master; T10 byte-lane handshake and stable request checks",
            "scheduled_stalls": list(_STALL_SCHEDULE),
            "patch_capacity": 131072,
            "tool_versions": tool_versions,
            "python_version": platform.python_version(),
            "phases": compile_phases,
            "work_directory": str(work),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "overall_timeout_seconds": _OVERALL_TIMEOUT_SECONDS,
            "no_progress_stop_seconds": _NO_PROGRESS_TIMEOUT_SECONDS,
            "synthesis": "not executed; pilot task does not require synthesis",
            "board_validation": "not executed; no hardware access authorized or needed",
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
    except Exception as exc:
        print(f"FAIL S2A-T18 mode={args.mode}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
