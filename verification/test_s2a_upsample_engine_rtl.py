"""在隔离 Vivado 临时目录验证 S2A-T13 单元素 upsample memory datapath。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_T05_RTL = _ROOT / "src/int8_upsample_query.sv"
_T05_TB = _ROOT / "sim/tb_s2a_upsample_query.sv"
_T05_RUNNER = _ROOT / "verification/test_s2a_upsample_rtl.py"
_ENGINE = _ROOT / "src/s2a_upsample_engine.sv"
_MEMORY_MODEL = _ROOT / "sim/s2a_memory_model.sv"
_MEMORY_MASTER = _ROOT / "src/s2a_memory_master.sv"
_TB = _ROOT / "sim/tb_s2a_upsample_engine.sv"
_RUNNER = Path(__file__).resolve()
_EVIDENCE = _ROOT / "report/evidence/S2A-T13/upsample_simulation.json"
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_BASELINE_HEAD = "05f7e2e721398d203f29acaa4cc1ad553c82cfeb"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_SEED = 20260922
_INPUT_BASE = 27598336
_INPUT_LENGTH = 21632
_OUTPUT_BASE = 27619968
_OUTPUT_LENGTH = 86528
_INPUT_SHAPE = [1, 128, 13, 13]
_OUTPUT_SHAPE = [1, 128, 26, 26]
_STALL_SCHEDULE = [0, 1, 2, 7, 3]
_T05_EVIDENCE = _ROOT / "report/evidence/S2A-T05/upsample_query_simulation.json"


def _sha256_bytes(payload: bytes) -> str:
    """计算原始字节摘要。"""
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节摘要。"""
    return _sha256_bytes(path.read_bytes())


def _canonical_sha(value: object) -> str:
    """计算稳定 JSON 值摘要。"""
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    return _sha256_bytes(payload)


def _is_under(child: Path, parent: Path) -> bool:
    """判断路径是否位于指定父目录。"""
    try:
        return os.path.commonpath((str(child), str(parent))).casefold() == str(parent).casefold()
    except ValueError:
        return False


def _load_manifest() -> tuple[dict, bytes, list[tuple[int, int]]]:
    """校验 G0 冻结输入并导出 T10 memory model feature ranges。"""
    raw = _MANIFEST.read_bytes()
    if _sha256_bytes(raw) != _MANIFEST_SHA256:
        raise AssertionError("G0 manifest SHA-256 改变，停止 T13 仿真")
    manifest = json.loads(raw.decode("utf-8"))
    layers = manifest["layers"]
    upsample = [layer for layer in layers if layer.get("op") == "upsample"]
    by_index = {layer["layer_index"]: layer for layer in layers}
    if len(upsample) != 1 or upsample[0]["layer_index"] != 33:
        raise AssertionError("G0 tiny416 upsample 层编号改变")
    layer = upsample[0]
    producer = by_index[32]
    if (layer["input_tensor_indices"] != [32] or
            producer["tensor_address"] != _INPUT_BASE or
            producer["tensor_length_bytes"] != _INPUT_LENGTH or
            layer["input_shape_nchw"] != _INPUT_SHAPE or
            layer["output_shape_nchw"] != _OUTPUT_SHAPE or
            layer["stride"] != 2 or layer["method"] != "nearest_repeat" or
            layer["input_scale"] != layer["output_scale"]):
        raise AssertionError("G0 layer32/33 upsample address/shape/stride/scale 改变")
    if (layer["tensor_address"] != _OUTPUT_BASE or
            layer["tensor_length_bytes"] != _OUTPUT_LENGTH):
        raise AssertionError("G0 layer33 output range 改变")
    address_map = manifest["address_map"]
    input_desc = address_map["input"]
    weights_desc = address_map["weight_package"]
    workspace = address_map["feature_workspace"]
    if ((input_desc["address"], input_desc["length_bytes"]) != (0, 519168) or
            (weights_desc["address"], weights_desc["length_bytes"]) !=
            (0x00100000, 5903100) or
            workspace["base_address"] != 0x01000000):
        raise AssertionError("G0 T10 memory object map 改变")
    ranges_set: set[tuple[int, int]] = set()
    for item in layers:
        if item.get("op") == "yolo":
            continue
        start = int(item["tensor_address"])
        end = start + int(item["tensor_length_bytes"])
        if start < int(workspace["base_address"]) or end > int(workspace["end_address_exclusive"]):
            raise AssertionError("G0 feature tensor 超出 workspace")
        ranges_set.add((start, end))
    ranges = sorted(ranges_set)
    if len(ranges) != 36 or ( _OUTPUT_BASE, _OUTPUT_BASE + _OUTPUT_LENGTH) not in ranges:
        raise AssertionError("G0 T10 feature range 个数或 layer33 区间变化")
    for previous, current in zip(ranges, ranges[1:]):
        if previous[1] > current[0]:
            raise AssertionError("G0 feature tensor ranges 重叠")
    return manifest, raw, ranges


def _materialize_engine_vectors(manifest: dict, work: Path) -> dict:
    """复用 T05 官方完整随机流，仅导出 1000 随机和 18 定向坐标。"""
    spec = importlib.util.spec_from_file_location("s2a_t05_upsample_runner", _T05_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 T05 G0 向量生成器")
    t05 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t05)
    full_vectors = work / "t05_vectors.dat"
    t05_result = t05._materialize_vectors(manifest, full_vectors)
    source_rows = full_vectors.read_text(encoding="ascii").splitlines()
    engine_rows: list[str] = []
    stimuli: list[list[int]] = []
    goldens: list[list[int]] = []
    random_count = 0
    directed_queries = 0
    directed_case_indices: set[int] = set()
    for row in source_rows:
        fields = row.split()
        if len(fields) != 21:
            raise AssertionError("T05 G0 query record 字段数变化")
        vector_class = int(fields[0])
        if vector_class == 2:
            continue
        if vector_class not in (0, 1):
            raise AssertionError("T05 G0 query vector class 非法")
        case_index = int(fields[1])
        query_index = int(fields[2])
        channel = int(fields[8])
        output_y = int(fields[9])
        output_x = int(fields[10])
        source_y = int(fields[14])
        source_x = int(fields[15])
        source_address = int(fields[17])
        t05_source_value = int(fields[18])
        expected_source_address = _INPUT_BASE + ((channel * 13 + source_y) * 13 + source_x)
        if (source_y != output_y // 2 or source_x != output_x // 2 or
                source_address != expected_source_address or
                not -127 <= t05_source_value <= 127):
            raise AssertionError("T05 G0 layer33 coordinate/value 向量非法")
        engine_rows.append(
            f"{vector_class} {case_index} {query_index} {channel} {output_y} "
            f"{output_x} {source_address:08X} {t05_source_value} {source_y} {source_x}\n"
        )
        stimuli.append([vector_class, case_index, query_index, channel,
                        output_y, output_x, source_address, t05_source_value])
        source_byte = _initial_byte(source_address)
        output_address = _OUTPUT_BASE + ((channel * 26 + output_y) * 26 + output_x)
        goldens.append([vector_class, case_index, query_index, source_address,
                        output_address, source_byte])
        if vector_class == 0:
            random_count += 1
        else:
            directed_queries += 1
            directed_case_indices.add(case_index)
    if (random_count != 1000 or directed_queries != 18 or
            directed_case_indices != set(range(16))):
        raise AssertionError("T05 G0 layer33 official random/directed coverage changed")
    engine_payload = "".join(engine_rows).encode("ascii")
    engine_vector_path = work / "engine_vectors.dat"
    engine_vector_path.write_bytes(engine_payload)
    return {
        "t05": t05_result,
        "engine_vector_sha256": _sha256_bytes(engine_payload),
        "engine_vector_bytes": len(engine_payload),
        "stimulus_sha256": _canonical_sha(stimuli),
        "memory_golden_sha256": _canonical_sha(goldens),
        "counts": {
            "model_random_coordinates": random_count,
            "model_directed_cases": len(directed_case_indices),
            "model_directed_queries": directed_queries,
            "memory_path_queries": len(engine_rows),
        },
        "t05_source_values_consumed_but_not_used_as_t10_contents": True,
    }


def _initial_byte(address: int) -> int:
    """计算 T10 memory model 的只读确定性初始 byte。"""
    return ((address & 0xFF) ^ ((address >> 8) & 0xFF) ^
            ((address >> 16) & 0xFF) ^ ((address >> 24) & 0xFF) ^ 0xA5)


def _write_memory_ranges(manifest: dict, ranges: list[tuple[int, int]], work: Path) -> str:
    """按 T12 T10 格式生成全量 manifest-derived memory range 文件。"""
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
    return _sha256_bytes(payload)


def _run_command(tool: Path, args: list[str], work: Path,
                 repository: Path, deadline: float) -> tuple[int, str]:
    """在系统 TEMP 隔离目录运行 Vivado 命令。"""
    temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
    work = work.resolve(strict=True)
    if not _is_under(work, temp_root) or _is_under(work, repository.resolve(strict=True)):
        raise RuntimeError(f"拒绝在仓库或 TEMP 之外运行 Vivado：{work}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("T13 Vivado 仿真超过 600 秒停止限制")
    command = " ".join(
        f'"{argument}"' if (" " in argument or "&" in argument) else argument
        for argument in (str(tool), *args)
    )
    completed = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=work, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=remaining, check=False,
    )
    output = completed.stdout + "\n" + completed.stderr
    return completed.returncode, output


def _tool_version(tool: Path) -> str:
    """读取工具版本并仅保留稳定的版本标识。"""
    completed = subprocess.run(
        f'cmd.exe /d /s /c "{tool} -version"', shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"工具版本查询失败：{tool.name} exit={completed.returncode}")
    output = completed.stdout + "\n" + completed.stderr
    match = re.search(r"(?i)(?:Vivado(?: Simulator)?|Xilinx).*?v\d+(?:\.\d+)+", output)
    if match is None:
        raise RuntimeError(f"无法解析工具版本：{tool.name}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _parse_xsim_summary(log: str) -> dict[str, int]:
    """fail-closed 解析仿真唯一汇总并检查固定用例数量。"""
    if "FAIL:" in log.upper():
        raise AssertionError("xsim log 包含 FAIL 诊断")
    if re.search(r"(?im)^\s*(?:ERROR|FATAL)\s*:", log):
        raise AssertionError("xsim log 包含 ERROR/FATAL 诊断")
    pattern = (
        r"RESULT model_random=(\d+) directed_cases=(\d+) directed_queries=(\d+) "
        r"memory_path_queries=(\d+) success=(\d+) errors=(\d+) readback=(\d+) "
        r"invalid=(\d+) raw_fault=(\d+) response_override=(\d+) write_fault=(\d+) "
        r"abort_cancel=(\d+) reset_cancel=(\d+) ownership=(\d+) accepted=(\d+) "
        r"responses=(\d+) memory_handshakes=(\d+) stall_cycles=(\d+)"
    )
    matches = list(re.finditer(pattern, log))
    marker = "PASS S2A-T13 upsample memory datapath"
    marker_positions = [match.start() for match in re.finditer(re.escape(marker), log)]
    if len(matches) != 1 or len(marker_positions) != 1 or marker_positions[0] < matches[0].end():
        raise AssertionError("仿真必须包含唯一且顺序正确的 RESULT/PASS")
    names = (
        "model_random", "directed_cases", "directed_queries", "memory_path_queries",
        "success", "errors", "readback", "invalid", "raw_fault", "response_override",
        "write_fault", "abort_cancel", "reset_cancel", "ownership", "accepted",
        "responses", "memory_handshakes", "stall_cycles",
    )
    summary = dict(zip(names, map(int, matches[0].groups()), strict=True))
    expected = {
        "model_random": 1000, "directed_cases": 16, "directed_queries": 18,
        "memory_path_queries": 1018, "success": 1025, "errors": 15,
        "readback": 1047, "invalid": 10, "raw_fault": 2,
        "response_override": 2, "write_fault": 1, "abort_cancel": 2,
        "reset_cancel": 2, "ownership": 1, "accepted": 3109,
        "responses": 3105, "memory_handshakes": 3105,
    }
    for name, value in expected.items():
        if summary[name] != value:
            raise AssertionError(f"仿真计数 {name}={summary[name]}，期望 {value}")
    if summary["stall_cycles"] <= 7000:
        raise AssertionError("T10 memory stall schedule 覆盖不足")
    return summary


def _run_t05_in_shadow(work: Path, repository: Path,
                       deadline: float) -> dict[str, object]:
    """在临时镜像中执行既有 T05 oracle，不重写仓库内 T05 evidence。"""
    shadow = work / "t05_shadow"
    for relative in (
        "verification/test_s2a_upsample_rtl.py",
        "report/evidence/S2A-T01/tiny416_model_manifest.json",
        "src/int8_upsample_query.sv",
        "sim/tb_s2a_upsample_query.sv",
    ):
        source = repository / relative
        target = shadow / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    remaining = deadline - time.monotonic()
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "unittest",
         "verification.test_s2a_upsample_rtl", "-v"],
        cwd=shadow, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=remaining, check=False,
    )
    output = completed.stdout + "\n" + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(f"既有 T05 oracle exit={completed.returncode}:\n{output[-5000:]}")
    if output.count("S2A-T05 manifest_sha256=") != 1 or "Ran 1 test" not in output or "OK" not in output:
        raise AssertionError("T05 shadow unittest 未提供唯一成功摘要：\n" + output[-5000:])
    generated_evidence = shadow / "report/evidence/S2A-T05/upsample_query_simulation.json"
    if not generated_evidence.is_file():
        raise AssertionError("T05 shadow run 未生成 query evidence")
    t05_evidence = json.loads(generated_evidence.read_text(encoding="utf-8"))
    if (t05_evidence.get("result") != "PASS" or
            t05_evidence.get("bindings", {}).get("manifest_sha256") != _MANIFEST_SHA256 or
            t05_evidence.get("counts") != {
                "model_random_queries": 1000,
                "model_directed_cases": 16,
                "model_directed_queries": 18,
                "fixture_queries": 16,
            } or
            t05_evidence.get("bindings", {}).get("rtl_sha256") != _sha256_file(_T05_RTL) or
            t05_evidence.get("bindings", {}).get("testbench_sha256") != _sha256_file(_T05_TB) or
            t05_evidence.get("bindings", {}).get("runner_sha256") != _sha256_file(_T05_RUNNER)):
        raise AssertionError("T05 shadow evidence 未绑定 G0/T05 源码或冻结样本数")
    generated_sha = _sha256_file(generated_evidence)
    committed_sha = _sha256_file(_T05_EVIDENCE)
    if generated_sha != committed_sha:
        raise AssertionError("T05 shadow evidence 与仓库冻结证据字节不一致")
    return {
        "command": "python -B -m unittest verification.test_s2a_upsample_rtl -v",
        "exit_code": completed.returncode,
        "coverage_counts": t05_evidence["counts"],
        "generated_evidence_sha256": generated_sha,
        "repository_evidence_sha256": committed_sha,
    }


class TestS2AUpsampleEngineRtl(unittest.TestCase):
    """验证 G0 layer33 地址映射和 T10/T12 byte-lane memory integration。"""

    def test_upsample_engine_memory_path(self) -> None:
        """先运行只读 T05 oracle，再执行 T13 两阶段 Vivado 仿真。"""
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
            text=True, encoding="utf-8", check=True,
        ).stdout.strip()
        self.assertEqual(head, _BASELINE_HEAD, "T13 baseline HEAD 已变化")
        manifest, manifest_raw, ranges = _load_manifest()
        source_paths = {
            "upsample_query_rtl": _T05_RTL,
            "memory_master_rtl": _MEMORY_MASTER,
            "memory_model_rtl": _MEMORY_MODEL,
            "engine_rtl": _ENGINE,
            "testbench": _TB,
            "runner": _RUNNER,
            "t05_runner": _T05_RUNNER,
            "t05_testbench": _T05_TB,
        }
        for source in source_paths.values():
            self.assertTrue(source.is_file(), f"验证源文件缺失：{source}")
            raw = source.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{source.name} 含 UTF-8 BOM")
            self.assertNotIn(b"\r\n", raw, f"{source.name} 非 LF 原始字节")
            raw.decode("utf-8")
        source_hashes_before = {name: _sha256_file(path)
                                for name, path in source_paths.items()}
        self.assertEqual(source_hashes_before["memory_master_rtl"],
                         "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07")
        self.assertEqual(source_hashes_before["memory_model_rtl"],
                         "4db3a955e2bdf9007a6365fd2dd01e588c63e9e2cc7b270fc511d1f5a06f3ae2")

        tools = {name: _XILINX_BIN / f"{name}.bat"
                 for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"Vivado tool 不存在：{tool}")
        versions = {name: _tool_version(tool) for name, tool in tools.items()}

        with tempfile.TemporaryDirectory(prefix="s2a_t13_upsample_engine_") as temp_name:
            work = Path(temp_name).resolve(strict=True)
            temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
            self.assertTrue(_is_under(work, temp_root))
            self.assertFalse(_is_under(work, _ROOT.resolve(strict=True)))
            t05_result = _run_t05_in_shadow(work, _ROOT, time.monotonic() + 600.0)
            vector_result = _materialize_engine_vectors(manifest, work)
            ranges_sha = _write_memory_ranges(manifest, ranges, work)
            phases: list[dict[str, int | str]] = []
            logs: dict[str, str] = {}
            commands = [
                ("xvlog", ["-sv", str(_T05_RTL), str(_ENGINE),
                           str(_MEMORY_MODEL), str(_MEMORY_MASTER), str(_TB)]),
                ("xelab", ["-top", "tb_s2a_upsample_engine",
                           "-snapshot", "s2a_upsample_engine_snapshot"]),
                ("xsim", ["-R", "s2a_upsample_engine_snapshot"]),
            ]
            deadline = time.monotonic() + 600.0
            for phase, args in commands:
                exit_code, log = _run_command(tools[phase], args, work,
                                              _ROOT, deadline)
                phases.append({"phase": phase, "exit_code": exit_code})
                logs[phase] = log
                (work / f"{phase}.log").write_text(log, encoding="utf-8", newline="\n")
                self.assertEqual(exit_code, 0,
                                 f"{phase} exit={exit_code}; log tail:\n{log[-5000:]}")
            try:
                summary = _parse_xsim_summary(logs["xsim"])
            except AssertionError as exc:
                self.fail(f"T13 xsim summary gate failed: {exc}; tail:\n{logs['xsim'][-6000:]}")
            for phase_log in logs.values():
                self.assertNotRegex(phase_log, r"(?im)^\s*(?:ERROR|FATAL)\s*:")
                self.assertNotIn("FAIL:", phase_log.upper())

        source_hashes_after = {name: _sha256_file(path)
                               for name, path in source_paths.items()}
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真期间验证源码发生变化")
        self.assertEqual(_sha256_file(_MANIFEST), _MANIFEST_SHA256,
                         "仿真期间 G0 manifest 改变")

        evidence = {
            "schema_version": "gestureforge_s2a_t13_upsample_simulation_v1",
            "task": "S2A-T13",
            "result": "PASS",
            "baseline_head": head,
            "scope": "tiny416 layer33 单输出元素 nearest-repeat INT8 memory read/copy/write",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": _sha256_bytes(manifest_raw),
                "upsample_query_rtl_sha256": source_hashes_after["upsample_query_rtl"],
                "memory_model_rtl_sha256": source_hashes_after["memory_model_rtl"],
                "memory_master_rtl_sha256": source_hashes_after["memory_master_rtl"],
                "engine_rtl_sha256": source_hashes_after["engine_rtl"],
                "testbench_sha256": source_hashes_after["testbench"],
                "runner_sha256": source_hashes_after["runner"],
                "t05_runner_sha256": source_hashes_after["t05_runner"],
                "t05_testbench_sha256": source_hashes_after["t05_testbench"],
                "t05_frozen_evidence_sha256": t05_result["repository_evidence_sha256"],
                "memory_ranges_sha256": ranges_sha,
                "official_query_vector_sha256": vector_result["t05"]["vector_sha256"],
                "official_query_golden_sha256": vector_result["t05"]["golden_output_sha256"],
                "engine_vector_sha256": vector_result["engine_vector_sha256"],
                "official_stimulus_sha256": vector_result["stimulus_sha256"],
                "memory_golden_results_sha256": vector_result["memory_golden_sha256"],
                "gitattributes_sha256": _sha256_file(_ROOT / ".gitattributes"),
            },
            "model": {
                "name": "tiny416",
                "layer_index": 33,
                "source_layer_index": 32,
                "input_nchw": _INPUT_SHAPE,
                "output_nchw": _OUTPUT_SHAPE,
                "input_base": _INPUT_BASE,
                "input_length_bytes": _INPUT_LENGTH,
                "output_base": _OUTPUT_BASE,
                "output_length_bytes": _OUTPUT_LENGTH,
                "stride": 2,
                "input_scale": 0.145512708528774,
                "output_scale": 0.145512708528774,
                "scale_preserved": True,
            },
            "randomness": {
                "seed": _RANDOM_SEED,
                "prng": "G0 shared xorshift32 via verification/test_s2a_upsample_rtl.py",
                "state_before_upsample": vector_result["t05"]["prng"]["state_before_upsample"],
                "state_after_random_queries": vector_result["t05"]["prng"]["state_after_random_queries"],
                "state_after_upsample": vector_result["t05"]["prng"]["state_after_upsample"],
                "official_draw_order": vector_result["t05"]["prng"]["random_draw_order"],
                "t05_source_value_consumed_but_t10_initial_byte_used_for_bus_golden": True,
            },
            "coverage": {
                **summary,
                "t05_query_oracle": t05_result,
                "input_byte_golden": "T10 memory model initial_byte(address); official T05 random source_value is not substituted into read-only memory",
                "byte_strobes": "single little-endian lane; aligned word address; every selected lane checked",
                "request_stability_under_backpressure": True,
                "one_outstanding_master_order": True,
                "result_fields_held_until_ready": True,
                "no_output_write_after_read_error": True,
                "hard_reset_pending_read_write_cancel_silent": True,
                "abort_pending_read_write_cancel_silent": True,
                "raw_model_fault_mapping": {"6_to_6": True, "7_to_6": True},
                "backend_response_override_mapping": {"1_to_1": True, "2_to_2": True},
                "write_fault_has_no_memory_side_effect": True,
                "ownership_gate_tested": True,
            },
            "commands": {
                "t05": t05_result["command"],
                "t05_exit_code": t05_result["exit_code"],
                "t13": "python -B -m unittest verification.test_s2a_upsample_engine_rtl -v",
            },
            "vivado": {
                "bin": str(_XILINX_BIN),
                "tool_versions": versions,
                "phases": phases,
            },
            "limitations": [
                "T13 仅验证单元素内存读写，不实现完整 layer scheduler 或整层网络执行。",
                "T10 输入初值是确定性 byte pattern；G0 source_value 与 nearest-repeat query/value 由独立 T05 oracle 全量验证，不冒充 T10 中的真实 tiny416 激活张量。",
                "T12 backend private contract 通过 memory master 接入；未接入完整 CSR runtime shell 或真实 AXI/DMA。",
                "未读取外部 weights，不执行综合、资源/时序分析或实物验证。",
            ],
        }
        evidence_bytes = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_bytes(evidence_bytes)
        print(
            "S2A-T13 manifest_sha256={} engine_sha256={} vectors={} golden={} "
            "summary={} phases={} evidence_sha256={}".format(
                _MANIFEST_SHA256, source_hashes_after["engine_rtl"],
                vector_result["counts"], vector_result["memory_golden_sha256"],
                summary, [phase["exit_code"] for phase in phases],
                _sha256_bytes(evidence_bytes),
            )
        )


if __name__ == "__main__":
    unittest.main()
