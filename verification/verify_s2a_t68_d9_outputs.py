#!/usr/bin/env python3
"""绑定 T68 backend head 实际字节并逐样本复算冻结 CPU D9。"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification import s2a_decode_nms_reference as t29
from verification import verify_s2a_network_backend_golden as fixture_verifier

T29_REPORT = ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json"
T29_REPORT_SHA256 = "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"
T25_INDEX = ROOT / "report/evidence/S2A-T25/cpu_layer_golden_index.json"
T25_INDEX_SHA256 = "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d"
T01_MANIFEST = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T01_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T01_SAMPLES = ROOT / "report/evidence/S2A-T01/fixed_test_samples.json"
T01_SAMPLES_SHA256 = "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"
T29_GENERATOR = ROOT / "verification/s2a_decode_nms_reference.py"
D9_REFERENCE = ROOT / "verification/s1_t02_d9_yolo_decode.py"
T68_RUNNER = ROOT / "verification/run_s2a_network_backend_verilator.ps1"
T68_PREPARER = ROOT / "verification/prepare_s2a_network_backend_golden.py"
T68_FIXTURE_VERIFIER = ROOT / "verification/verify_s2a_network_backend_golden.py"
T68_D9_VERIFIER = Path(__file__).resolve()
T68_TESTBENCH = ROOT / "sim/tb_s2a_network_backend_golden.sv"
SAMPLE_COUNT = 109
T29_CANONICAL_SHA256 = "10a4116904261ee092940e1e354bed64dbd944023f6d8fdae5cf2079ad9b4c63"
T29_REGENERATED_CANONICAL_SHA256 = "1cd26b9e655a9e8faa6d9f614b4569fecda8fb236cf9237e6e72726469de8cdd"
T29_RUNTIME_FIELDS = ("python", "zlib_compile", "zlib_runtime")
T29_FROZEN_RUNTIME = {"python": "3.12.10", "zlib_compile": "1.3.1", "zlib_runtime": "1.3.1"}
T29_PINNED_RUNTIME = {"python": "3.12.14", "zlib_compile": "1.3.2", "zlib_runtime": "1.3.2"}
HEAD_SPECS = {
    "head13": {"file": "head13_actual_int8.bin", "layer": 29, "bytes": 5070, "shape": (3, 10, 13, 13)},
    "head26": {"file": "head26_actual_int8.bin", "layer": 36, "bytes": 20280, "shape": (3, 10, 26, 26)},
}
SCORE_TOLERANCE = 1e-6
COORDINATE_TOLERANCE = 1e-6
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class D9VerificationError(ValueError):
    """表示 T68 PL head、冻结 CPU gold 或 D9 结果绑定失败。"""


def require(condition: bool, message: str) -> None:
    """在任一固定契约不满足时停止。"""
    if not condition:
        raise D9VerificationError(message)


def sha256_bytes(value: bytes) -> str:
    """计算字节串 SHA-256。"""
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    """读取普通 UTF-8 JSON 文件。"""
    require(path.is_file() and not path.is_symlink(), f"{label} 缺失或不是普通文件：{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise D9VerificationError(f"{label} 不是有效 UTF-8 JSON：{path}") from error
    require(isinstance(value, dict), f"{label} 顶层必须是对象：{path}")
    return value


def canonical_path(path: Path) -> str:
    """返回用于本机源记录比较的绝对规范路径。"""
    return os.path.normcase(str(path.resolve()))


def verify_frozen_cpu_baseline() -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    """重建 109 个 T25 CPU head 的 D9 结果并核对冻结 T29 报告。"""
    pinned_files = (
        (T29_REPORT, T29_REPORT_SHA256, "T29 CPU D9 evidence"),
        (T25_INDEX, T25_INDEX_SHA256, "T25 index"),
        (T01_MANIFEST, T01_MANIFEST_SHA256, "T01 model manifest"),
        (T01_SAMPLES, T01_SAMPLES_SHA256, "T01 fixed sample catalog"),
    )
    for path, expected_sha, label in pinned_files:
        require(path.is_file() and not path.is_symlink(), f"{label} 缺失或类型不符：{path}")
        require(sha256_file(path) == expected_sha, f"{label} SHA-256 不符：{path}")

    parent = read_json(T29_REPORT, "T29 CPU D9 evidence")
    require(parent.get("status") == "CPU_REFERENCE_GENERATED", "T29 CPU D9 evidence 未完成")
    require(parent.get("schema_version") == "gestureforge_s2a_t29_cpu_decode_nms_reference_v1", "T29 schema 不符")
    require(len(parent.get("samples", [])) == SAMPLE_COUNT, "T29 CPU D9 evidence 不是 109 样本")
    require(sha256_file(T29_GENERATOR) == "219a09720d9de0723730b51ed9c007aeec5e1b9abf6bc49c5e0268c2173bc49c", "T29 generator SHA 不符")
    require(sha256_file(D9_REFERENCE) == "0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6", "D9 decoder SHA 不符")

    regenerated = t29.generate_evidence(ROOT, progress=None, preflight_only=False)
    require(len(regenerated.get("samples", [])) == SAMPLE_COUNT, "从 T25 重建的 CPU D9 结果不是 109 样本")
    frozen_canonical = t29._canonical_evidence_bytes(parent)
    regenerated_canonical = t29._canonical_evidence_bytes(regenerated)
    frozen_canonical_sha256 = sha256_bytes(frozen_canonical)
    regenerated_canonical_sha256 = sha256_bytes(regenerated_canonical)
    require(frozen_canonical_sha256 == T29_CANONICAL_SHA256, "冻结 T29 canonical SHA-256 不符")
    require(regenerated_canonical_sha256 == T29_REGENERATED_CANONICAL_SHA256, "当前固定 Python T29 canonical SHA-256 不符")

    frozen_normalized = copy.deepcopy(parent)
    regenerated_normalized = copy.deepcopy(regenerated)
    frozen_runtime = frozen_normalized.get("runtime")
    regenerated_runtime = regenerated_normalized.get("runtime")
    require(isinstance(frozen_runtime, dict) and isinstance(regenerated_runtime, dict), "T29 runtime 必须是对象")
    runtime_versions: dict[str, dict[str, str]] = {}
    for field in T29_RUNTIME_FIELDS:
        frozen_value = frozen_runtime.get(field)
        regenerated_value = regenerated_runtime.get(field)
        require(isinstance(frozen_value, str) and isinstance(regenerated_value, str), f"T29 runtime.{field} 必须是字符串")
        require(frozen_value == T29_FROZEN_RUNTIME[field], f"冻结 T29 runtime.{field} 不符")
        require(regenerated_value == T29_PINNED_RUNTIME[field], f"当前 T29 runtime.{field} 不符")
        runtime_versions[field] = {"frozen": frozen_value, "regenerated": regenerated_value}
        frozen_runtime[field] = None
        regenerated_runtime[field] = None

    sample_outputs_match = regenerated_normalized.get("samples") == frozen_normalized.get("samples")
    require(sample_outputs_match, "T29 CPU D9 样本输出不能与冻结报告逐字段精确匹配")
    normalized_canonical_match = (
        t29._canonical_evidence_bytes(regenerated_normalized)
        == t29._canonical_evidence_bytes(frozen_normalized)
    )
    require(
        normalized_canonical_match,
        "T29 CPU D9 父 evidence 除三个明确 runtime 版本字段外不能由当前冻结 T25 shards/source 确定性重建",
    )
    require(regenerated.get("decoder", {}).get("score_threshold") == 0.25, "T29 score threshold 不等于冻结值 0.25")
    require(regenerated.get("decoder", {}).get("max_outputs") == 15, "T29 max output 不等于冻结值 15")
    generated_rows = {row["sample_id"]: row for row in regenerated["samples"]}
    require(len(generated_rows) == SAMPLE_COUNT, "T29 sample_id 重复或缺失")
    reconstruction = {
        "schema_version": "gestureforge_s2a_t68_cpu_d9_reconstruction_v1",
        "status": "PASS_T29_REGENERATION_EXCEPT_RUNTIME_VERSION_FIELDS",
        "frozen_canonical_sha256": frozen_canonical_sha256,
        "regenerated_canonical_sha256": regenerated_canonical_sha256,
        "runtime_versions": runtime_versions,
        "ignored_fields": [f"runtime.{field}" for field in T29_RUNTIME_FIELDS],
        "exact_outputs_status": "PASS_ALL_109_SAMPLES_EXACT",
        "exact_outputs_match": sample_outputs_match,
        "normalized_canonical_match": normalized_canonical_match,
    }
    return regenerated, generated_rows, reconstruction


def verify_tooling_bindings(record: dict[str, Any], sample_dir: Path, label: str) -> dict[str, str]:
    """核对 compile/run records 对当前 runner 与 Python 工具源的哈希绑定。"""
    expected = {
        canonical_path(T68_RUNNER): sha256_file(T68_RUNNER),
        canonical_path(T68_PREPARER): sha256_file(T68_PREPARER),
        canonical_path(T68_FIXTURE_VERIFIER): sha256_file(T68_FIXTURE_VERIFIER),
    }
    recorded = record.get("tooling_sources")
    require(isinstance(recorded, list) and len(recorded) == len(expected), f"{label}: tooling_sources 数量不符")
    observed: dict[str, str] = {}
    for row in recorded:
        require(isinstance(row, dict), f"{label}: tooling source row 类型错误")
        path = Path(str(row.get("path", "")))
        key = canonical_path(path)
        require(key in expected, f"{label}: 未批准的 tooling source：{path}")
        require(key not in observed, f"{label}: tooling source 重复：{path}")
        require(row.get("sha256") == expected[key], f"{label}: tooling source SHA 不符：{path}")
        require(path.is_file() and path.stat().st_size == row.get("bytes"), f"{label}: tooling source byte length 不符：{path}")
        observed[key] = row["sha256"]
    require(observed == expected, f"{label}: tooling source 集合不完整")
    require(canonical_path(Path(str(record.get("runner_path", "")))) == canonical_path(T68_RUNNER), f"{label}: runner path 不符")
    require(record.get("runner_sha256") == expected[canonical_path(T68_RUNNER)], f"{label}: runner SHA 不符")
    require(sample_dir.is_dir() and not sample_dir.is_symlink(), f"{label}: sample run directory 类型错误")
    return {str(Path(key)): value for key, value in observed.items()}


def verify_compiled_source_binding(
    sample_dir: Path,
    simulation_record: dict[str, Any],
    compile_record: dict[str, Any],
    source_snapshot: dict[str, Any],
    sample_index: int,
) -> None:
    """核对本样本编译闭包、TB/backend SHA 和实际仿真命令。"""
    require(compile_record.get("schema_version") == "gestureforge_s2a_t68_compile_execution_v1", "compile record schema 不符")
    require(compile_record.get("exit_code") == 0 and compile_record.get("simulator_started") is False, "compile record 失败或包含意外仿真")
    require(compile_record.get("native_exit_code") == 0 and compile_record.get("compile_accepted") is True, "Verilator native compile 未通过退出码门")
    require(compile_record.get("launch_error") == "", "Verilator compile 启动异常")
    require(compile_record.get("warning_gate") == "-Wno-fatal", "compile 未记录获批的 -Wno-fatal 编译标志")
    require(type(compile_record.get("warning_count")) is int and compile_record["warning_count"] >= 0, "compile warning_count 缺失或无效")
    require(compile_record.get("error_count") == 0, "compile 含 Verilator %Error diagnostics")
    require(compile_record.get("warning_text_retained") is True, "compile stderr 原始 warning 日志未保留")
    require(compile_record.get("sample_index") == sample_index and compile_record.get("run_id") == simulation_record.get("run_id"), "compile record sample/run id 不符")
    require(compile_record.get("source_unchanged") is True and compile_record.get("tooling_sources_unchanged") is True, "compile 源在运行期间发生变化")
    require(source_snapshot.get("schema_version") == "gestureforge_s2a_t68_compile_source_snapshot_v1", "compile snapshot schema 不符")
    require(source_snapshot.get("sample_index") == sample_index and source_snapshot.get("run_id") == simulation_record.get("run_id"), "compile snapshot sample/run id 不符")
    require(source_snapshot.get("simulator_started") is False, "compile snapshot 标记 simulator 已启动")
    compile_command = compile_record.get("command")
    require(isinstance(compile_command, list) and compile_command, "compile command argv 缺失")
    require(compile_command[0] == compile_record.get("verilator_path"), "compile argv executable 与记录的 Verilator 路径不同")
    require(compile_command.count("-Wno-fatal") == 1, "compile argv 必须恰有一个 -Wno-fatal")
    require(source_snapshot.get("command") == compile_command[1:], "compile snapshot argv 与 execution record 不同")
    verify_captured_native_logs(sample_dir, compile_record, "Verilator compile")

    version_record_path = safe_child_file(sample_dir, compile_record.get("version_record_path"), "Verilator version record")
    require(sha256_file(version_record_path) == compile_record.get("version_record_sha256"), "Verilator version record SHA 不符")
    version_record = read_json(version_record_path, "Verilator version record")
    require(version_record.get("schema_version") == "gestureforge_s2a_t68_verilator_version_v1", "Verilator version record schema 不符")
    require(version_record.get("accepted") is True and version_record.get("exit_code") == 0, "Verilator --version 未通过")
    require(version_record.get("launch_error") == "" and version_record.get("error_count") == 0, "Verilator --version 含启动错误或 %Error")
    require(type(version_record.get("warning_count")) is int and version_record["warning_count"] >= 0, "version warning_count 缺失或无效")
    require(version_record.get("warning_text_retained") is True, "version stderr 原始日志未保留")
    version_command = version_record.get("command")
    require(version_command == [compile_record.get("verilator_path"), "--version"], "Verilator version argv 不符")
    verify_captured_native_logs(sample_dir, version_record, "Verilator version")
    require(simulation_record.get("compile_source_snapshot_sha256") == sha256_file(sample_dir / "compile_source_snapshot.json"), "simulation record 未绑定当前 compile snapshot")
    require(simulation_record.get("compile_execution_record_sha256") == sha256_file(sample_dir / "compile_execution_record.json"), "simulation record 未绑定当前 compile record")

    expected_sources = (*fixture_verifier.EXPECTED_RTL_SOURCE_PATHS, "sim/tb_s2a_network_backend_golden.sv")
    expected_by_path = {canonical_path(ROOT / relative): relative for relative in expected_sources}
    for label, rows in (("snapshot", source_snapshot.get("sources")), ("compile", compile_record.get("sources_after"))):
        require(isinstance(rows, list) and len(rows) == len(expected_sources), f"{label}: compiled source count 不符")
        observed: dict[str, str] = {}
        for row in rows:
            require(isinstance(row, dict), f"{label}: compiled source row 类型错误")
            path = Path(str(row.get("path", "")))
            key = canonical_path(path)
            require(key in expected_by_path, f"{label}: 未批准 compiled source：{path}")
            require(key not in observed, f"{label}: compiled source 重复：{path}")
            relative = expected_by_path[key]
            require(path.is_file() and row.get("sha256") == sha256_file(path), f"{label}: source SHA 不符：{relative}")
            require(path.stat().st_size == row.get("bytes"), f"{label}: source byte length 不符：{relative}")
            observed[key] = row["sha256"]
        require(set(observed) == set(expected_by_path), f"{label}: compiled source 集合不完整")
    require(source_snapshot.get("tooling_sources") == compile_record.get("tooling_sources"), "compile snapshot 与 execution record 的 tooling bindings 不同")
    verify_tooling_bindings(compile_record, sample_dir, "compile")
    verify_tooling_bindings(simulation_record, sample_dir, "simulation")

    backend_rows = [row for row in source_snapshot["sources"] if canonical_path(Path(row["path"])) == canonical_path(ROOT / "src/s2a_network_backend.sv")]
    tb_rows = [row for row in source_snapshot["sources"] if canonical_path(Path(row["path"])) == canonical_path(T68_TESTBENCH)]
    require(len(backend_rows) == len(tb_rows) == 1, "backend/TB source binding 不唯一")
    require(compile_record.get("backend_sha256_expected") == backend_rows[0]["sha256"], "显式 backend SHA 与 compiled source 不一致")
    require(simulation_record.get("sample_index") == sample_index, "simulation sample_index 不符")

    command = simulation_record.get("command")
    require(isinstance(command, list) and len(command) >= 7, "simulation argv 不完整")
    args = [str(item) for item in command[1:]]
    expected_args = (
        ("+SAMPLE_INDEX=", str(sample_index)),
        ("+FIXTURE_DIR=", str((sample_dir.parents[2] / "fixtures" / f"sample_{sample_index:03d}").resolve())),
        ("+RESULT_FILE=", str((sample_dir / "result_summary.txt").resolve())),
        ("+PROGRESS_FILE=", str((sample_dir / "progress_markers.txt").resolve())),
        ("+HEAD13_FILE=", str((sample_dir / HEAD_SPECS["head13"]["file"]).resolve())),
        ("+HEAD26_FILE=", str((sample_dir / HEAD_SPECS["head26"]["file"]).resolve())),
    )
    for prefix, value in expected_args:
        matches = [item[len(prefix) :] for item in args if item.startswith(prefix)]
        require(len(matches) == 1 and canonical_path(Path(matches[0])) == canonical_path(Path(value)), f"simulation argv 缺少或错绑 {prefix}")
    max_cycle_args = [item for item in args if item.startswith("+MAX_CYCLES=")]
    require(len(max_cycle_args) == 1 and max_cycle_args[0].split("=", 1)[1].isdigit(), "simulation argv 的 MAX_CYCLES 缺失或格式错误")
    require(0 < int(max_cycle_args[0].split("=", 1)[1]) <= 4294967295, "simulation argv 的 MAX_CYCLES 超出 32-bit 范围")


def safe_child_file(run_directory: Path, path_value: Any, label: str) -> Path:
    """要求记录中的文件路径指向当前 run 目录中的普通文件。"""
    require(isinstance(path_value, str) and path_value, f"{label}: file path 缺失")
    path = Path(path_value)
    require(path.is_absolute(), f"{label}: file path 不是绝对路径")
    require(canonical_path(path).startswith(canonical_path(run_directory) + os.sep), f"{label}: file path 越出 run directory")
    require(path.is_file() and not path.is_symlink(), f"{label}: 文件缺失或不是普通文件：{path}")
    return path


def verify_captured_native_logs(run_directory: Path, record: dict[str, Any], label: str) -> dict[str, Any]:
    """核对 native stdout/stderr 原始文件、hash 与 warning/error 计数。"""
    require(record.get("warning_text_retained") is True, f"{label}: native stderr 未声明保留")
    require(type(record.get("warning_count")) is int and record["warning_count"] >= 0, f"{label}: warning_count 无效")
    require(record.get("error_count") == 0, f"{label}: 记录含错误诊断")
    captured_text: dict[str, str] = {}
    for path_field, hash_field, stream in (
        ("stdout_path", "stdout_sha256", "stdout"),
        ("stderr_path", "stderr_sha256", "stderr"),
        ("console_path", "console_sha256", "console"),
    ):
        log_path = safe_child_file(run_directory, record.get(path_field), f"{label} {stream}")
        require(sha256_file(log_path) == record.get(hash_field), f"{label} {stream} SHA 不符")
        if stream != "console":
            captured_text[stream] = log_path.read_text(encoding="utf-8")
    diagnostics = captured_text["stdout"] + "\n" + captured_text["stderr"]
    warning_count = len(re.findall(r"(?m)^%Warning[^:\r\n]*:", diagnostics))
    error_count = len(re.findall(r"(?m)^%Error[^:\r\n]*:", diagnostics))
    require(warning_count == record.get("warning_count"), f"{label}: 原始日志 warning 数与记录不一致")
    require(error_count == record.get("error_count") == 0, f"{label}: 原始日志含 %Error 或 error_count 不一致")
    return {"warning_count": warning_count, "error_count": error_count}


def decode_heads(head13: bytes, head26: bytes, head13_scale: float, head26_scale: float) -> dict[str, np.ndarray]:
    """把实际导出的有符号 INT8 head 按冻结 scale 解量化为 float64。"""
    require(len(head13) == HEAD_SPECS["head13"]["bytes"], "head13 原始 byte length 错误")
    require(len(head26) == HEAD_SPECS["head26"]["bytes"], "head26 原始 byte length 错误")
    values13 = np.frombuffer(head13, dtype=np.int8)
    values26 = np.frombuffer(head26, dtype=np.int8)
    require(values13.size == int(np.prod(HEAD_SPECS["head13"]["shape"])), "head13 元素数错误")
    require(values26.size == int(np.prod(HEAD_SPECS["head26"]["shape"])), "head26 元素数错误")
    require(math.isfinite(head13_scale) and head13_scale > 0.0, "head13 scale 非法")
    require(math.isfinite(head26_scale) and head26_scale > 0.0, "head26 scale 非法")
    return {
        "13x13": values13.astype(np.float64).reshape(HEAD_SPECS["head13"]["shape"]) * np.float64(head13_scale),
        "26x26": values26.astype(np.float64).reshape(HEAD_SPECS["head26"]["shape"]) * np.float64(head26_scale),
    }


def compare_d9_rows(
    expected: list[dict[str, Any]],
    observed: list[Any],
    sample_id: str,
    expected_raw_count: int,
    observed_raw_count: int,
) -> dict[str, Any]:
    """逐序比较 D9 离散字段，并按绝对误差门比较分数和坐标。"""
    require(expected_raw_count == observed_raw_count, f"{sample_id}: pre-NMS candidate count 不一致")
    require(len(expected) == len(observed), f"{sample_id}: D9 输出框数不一致")
    max_score_error = 0.0
    max_coordinate_error = 0.0
    rows: list[dict[str, Any]] = []
    for index, (reference, actual) in enumerate(zip(expected, observed, strict=True)):
        require(int(reference["class_id"]) == int(actual.class_id), f"{sample_id}[{index}]: class_id 不一致")
        require(reference["class_name"] == actual.name, f"{sample_id}[{index}]: class_name 不一致")
        require(int(reference["source_order"]) == int(actual.source_order), f"{sample_id}[{index}]: source_order 不一致")
        require(actual.image_key == sample_id, f"{sample_id}[{index}]: D9 image_key 不一致")
        expected_score = float(reference["score"])
        observed_score = float(actual.confidence)
        score_error = abs(expected_score - observed_score)
        expected_box = [float(value) for value in reference["xyxy"]]
        observed_box = [float(value) for value in actual.box]
        require(len(expected_box) == len(observed_box) == 4, f"{sample_id}[{index}]: box shape 错误")
        coordinate_error = max(abs(left - right) for left, right in zip(expected_box, observed_box, strict=True))
        require(math.isfinite(score_error) and score_error <= SCORE_TOLERANCE, f"{sample_id}[{index}]: score absolute error 超限：{score_error}")
        require(math.isfinite(coordinate_error) and coordinate_error <= COORDINATE_TOLERANCE, f"{sample_id}[{index}]: coordinate absolute error 超限：{coordinate_error}")
        max_score_error = max(max_score_error, score_error)
        max_coordinate_error = max(max_coordinate_error, coordinate_error)
        rows.append({"class_id": int(actual.class_id), "class_name": actual.name, "source_order": int(actual.source_order), "score_abs_error": score_error, "xyxy_max_abs_error": coordinate_error})
    return {
        "detection_count": len(observed),
        "raw_candidate_count": observed_raw_count,
        "max_score_abs_error": max_score_error,
        "max_xyxy_abs_error": max_coordinate_error,
        "relative_tolerance": 0.0,
        "detections": rows,
    }


def verify_sample(
    evidence_root: Path,
    run_id: str,
    sample_index: int,
    expected_cpu_row: dict[str, Any],
    threshold: float,
) -> dict[str, Any]:
    """验证一个 sample 的 fixture、RTL 源、仿真记录和两个实际 head。"""
    sample_key = f"sample_{sample_index:03d}"
    sample_dir = evidence_root / "runs" / sample_key / run_id
    require(sample_dir.is_dir() and not sample_dir.is_symlink(), f"{sample_key}: run directory 缺失或类型错误：{sample_dir}")
    simulation_record_path = sample_dir / "simulation_execution_record.json"
    compile_record_path = sample_dir / "compile_execution_record.json"
    snapshot_path = sample_dir / "compile_source_snapshot.json"
    simulation_record = read_json(simulation_record_path, f"{sample_key} simulation record")
    compile_record = read_json(compile_record_path, f"{sample_key} compile record")
    source_snapshot = read_json(snapshot_path, f"{sample_key} source snapshot")

    require(simulation_record.get("schema_version") == "gestureforge_s2a_t68_simulation_execution_v1", f"{sample_key}: simulation record schema 不符")
    require(simulation_record.get("exit_code") == 0 and simulation_record.get("runner_exit_code") == 0, f"{sample_key}: simulation/runner 非零退出")
    require(simulation_record.get("result_summary_valid") is True and simulation_record.get("head_exports_valid") is True, f"{sample_key}: result/head export 未通过 runner 门")
    require(simulation_record.get("progress_markers_valid") is True and simulation_record.get("last_progress_phase") == "complete", f"{sample_key}: simulation 未正常完成")
    require(simulation_record.get("wave_dump_requested") is False, f"{sample_key}: 不应生成波形")
    require(simulation_record.get("run_id") == run_id, f"{sample_key}: simulation run_id 不符")
    verify_compiled_source_binding(sample_dir, simulation_record, compile_record, source_snapshot, sample_index)

    compile_console = safe_child_file(sample_dir, compile_record.get("console_path"), f"{sample_key} compile console")
    require(sha256_file(compile_console) == compile_record.get("console_sha256"), f"{sample_key}: compile console SHA 不符")
    for field, hash_field, label in (
        ("console_path", "console_sha256", "simulation console"),
        ("stderr_path", "stderr_sha256", "simulation stderr"),
        ("progress_marker_path", "progress_marker_sha256", "progress markers"),
    ):
        log_path = safe_child_file(sample_dir, simulation_record.get(field), f"{sample_key} {label}")
        require(sha256_file(log_path) == simulation_record.get(hash_field), f"{sample_key}: {label} SHA 不符")
    progress_path = Path(simulation_record["progress_marker_path"])
    progress_lines = [line for line in progress_path.read_text(encoding="utf-8").splitlines() if line]
    require(len(progress_lines) == simulation_record.get("progress_marker_count"), f"{sample_key}: progress marker count 与记录不符")

    fixture_manifest_path = evidence_root / "fixtures" / sample_key / "fixture_manifest.json"
    fixture_result = fixture_verifier.verify(fixture_manifest_path)
    fixture_manifest = read_json(fixture_manifest_path, f"{sample_key} fixture manifest")
    require(fixture_manifest.get("sample_index") == sample_index, f"{sample_key}: fixture sample_index 不符")
    require(fixture_manifest.get("sample_id") == expected_cpu_row["sample_id"], f"{sample_key}: fixture sample_id 与 CPU golden 不符")
    require(fixture_manifest.get("input", {}).get("sha256") == expected_cpu_row["input"]["pl_input_sha256"], f"{sample_key}: fixture 输入 SHA 与 CPU golden 不符")
    require(fixture_manifest.get("input", {}).get("bytes") == 519168, f"{sample_key}: fixture 输入 byte length 错误")
    require(fixture_result.get("simulator_started") is False, f"{sample_key}: fixture verifier 不应启动 simulator")

    result_path = safe_child_file(sample_dir, simulation_record.get("result_summary_path"), f"{sample_key} result summary")
    require(sha256_file(result_path) == simulation_record.get("result_summary_sha256"), f"{sample_key}: result summary SHA 不符")
    summary = result_path.read_text(encoding="utf-8")
    require("status=PASS_LAYERWISE_EXACT_GOLDEN" in summary, f"{sample_key}: 未通过逐层 golden")
    require("feature_write_bytes=11382150 mismatches=0" in summary, f"{sample_key}: 输出字节或 mismatch summary 不符")
    require("head13_bytes=5070 head26_bytes=20280" in summary, f"{sample_key}: result summary 未确认两个 head 导出长度")

    raw_heads: dict[str, bytes] = {}
    head_report: dict[str, Any] = {}
    for name, spec in HEAD_SPECS.items():
        record_key = f"{name}_export"
        export = simulation_record.get(record_key)
        require(isinstance(export, dict), f"{sample_key}: {record_key} 缺失")
        path = safe_child_file(sample_dir, export.get("path"), f"{sample_key} {name}")
        require(path.name == spec["file"], f"{sample_key}: {name} 文件名不符合冻结路径")
        raw = path.read_bytes()
        digest = sha256_bytes(raw)
        require(len(raw) == spec["bytes"] == export.get("bytes"), f"{sample_key}: {name} byte length 不符")
        require(digest == export.get("sha256"), f"{sample_key}: {name} record SHA 不符")
        gold_binding = expected_cpu_row["head_tensors"][name]
        require(len(raw) == gold_binding["byte_length"], f"{sample_key}: {name} 与 CPU golden 长度不同")
        require(digest == gold_binding["tensor_sha256"], f"{sample_key}: {name} PL raw bytes 与 T25 CPU head golden SHA 不同")
        expected_nchw = (1, 30, spec["shape"][2], spec["shape"][3])
        require(tuple(gold_binding["shape_nchw"]) == expected_nchw, f"{sample_key}: {name} CPU golden shape 不符")
        raw_heads[name] = raw
        head_report[name] = {"bytes": len(raw), "sha256": digest, "t25_cpu_sha256": gold_binding["tensor_sha256"]}

    geometry = expected_cpu_row["input"]["geometry_wh"]
    require(len(geometry) == 2 and all(type(value) is int and value > 0 for value in geometry), f"{sample_key}: input geometry 不合法")
    logits = decode_heads(
        raw_heads["head13"], raw_heads["head26"],
        float(expected_cpu_row["head_tensors"]["head13"]["int8_scale"]),
        float(expected_cpu_row["head_tensors"]["head26"]["int8_scale"]),
    )
    actual_d9, actual_raw_count = t29.decode_and_count_candidates(
        logits, expected_cpu_row["sample_id"], geometry[0], geometry[1], threshold
    )
    d9_comparison = compare_d9_rows(
        expected_cpu_row["detections"], actual_d9, expected_cpu_row["sample_id"],
        int(expected_cpu_row["raw_candidate_count_before_stable_nms"]), actual_raw_count,
    )
    return {
        "sample_index": sample_index,
        "sample_id": expected_cpu_row["sample_id"],
        "frame_id": expected_cpu_row["frame_id"],
        "fixture_manifest_sha256": sha256_file(fixture_manifest_path),
        "simulation_execution_record_sha256": sha256_file(simulation_record_path),
        "compile_execution_record_sha256": sha256_file(compile_record_path),
        "compile_source_snapshot_sha256": sha256_file(snapshot_path),
        "input_sha256": fixture_manifest["input"]["sha256"],
        "head_exports": head_report,
        "d9_comparison": d9_comparison,
    }


def verify_batch(evidence_root: Path, run_id: str) -> dict[str, Any]:
    """按固定 sample_000..108 路径执行只读 109 样本 D9 比对。"""
    require(RUN_ID_PATTERN.fullmatch(run_id) is not None, "run_id 仅可含 ASCII 字母、数字、下划线、连字符")
    require(evidence_root.is_dir() and not evidence_root.is_symlink(), f"evidence root 缺失或类型错误：{evidence_root}")
    evidence_root = evidence_root.resolve()
    require(all(part.casefold() != "run01" for part in evidence_root.parts), "为保护既有 run01，拒绝读取路径中包含 run01 的 T68 evidence root")
    cpu_report, cpu_rows, reconstruction = verify_frozen_cpu_baseline()
    threshold = float(cpu_report["decoder"]["score_threshold"])
    sample_reports = [
        verify_sample(evidence_root, run_id, sample_index, cpu_rows_by_index(cpu_rows, sample_index), threshold)
        for sample_index in range(SAMPLE_COUNT)
    ]
    require(len(sample_reports) == SAMPLE_COUNT, "实际 PL head 未覆盖全部 109 个固定样本")
    max_score_error = max((row["d9_comparison"]["max_score_abs_error"] for row in sample_reports), default=0.0)
    max_coordinate_error = max((row["d9_comparison"]["max_xyxy_abs_error"] for row in sample_reports), default=0.0)
    return {
        "schema_version": "gestureforge_s2a_t68_d9_actual_head_comparison_v2",
        "status": "PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9",
        "sample_count": len(sample_reports),
        "run_id": run_id,
        "evidence_root": str(evidence_root.resolve()),
        "cpu_d9_reference": {"path": str(T29_REPORT.relative_to(ROOT).as_posix()), "sha256": sha256_file(T29_REPORT)},
        "cpu_d9_reconstruction": reconstruction,
        "t25_index": {"path": str(T25_INDEX.relative_to(ROOT).as_posix()), "sha256": sha256_file(T25_INDEX)},
        "d9_decoder_sha256": sha256_file(D9_REFERENCE),
        "verifier_sha256": sha256_file(T68_D9_VERIFIER),
        "score_threshold": threshold,
        "score_absolute_tolerance": SCORE_TOLERANCE,
        "coordinate_absolute_tolerance": COORDINATE_TOLERANCE,
        "relative_tolerance": 0.0,
        "max_score_abs_error": max_score_error,
        "max_xyxy_abs_error": max_coordinate_error,
        "samples": sample_reports,
        "simulator_started_by_verifier": False,
    }


def cpu_rows_by_index(rows: dict[str, dict[str, Any]], sample_index: int) -> dict[str, Any]:
    """以固定 frame_id 取回唯一 T29 样本行。"""
    matches = [row for row in rows.values() if row.get("frame_id") == sample_index]
    require(len(matches) == 1, f"T29 frame_id={sample_index} 缺失或重复")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    """验证所有实际 head 导出并可选写入新的独立报告。"""
    parser = argparse.ArgumentParser(description="逐样本绑定 T68 PL INT8 heads 并与冻结 T29 CPU D9 对照")
    parser.add_argument("--evidence-root", type=Path, required=True, help="含 fixtures 与 runs 的 T68 独立 evidence root")
    parser.add_argument("--run-id", required=True, help="109 个样本共用的唯一 T68 RunId")
    parser.add_argument("--report", type=Path, help="可选的新报告路径，须位于 evidence root 内且尚不存在")
    args = parser.parse_args(argv)
    try:
        result = verify_batch(args.evidence_root.absolute(), args.run_id)
        if args.report is not None:
            report_candidate = args.report.absolute()
            require(report_candidate.parent.is_dir() and not report_candidate.parent.is_symlink(), "报告父目录缺失或类型错误")
            report_path = report_candidate.resolve()
            require(report_path.is_relative_to(args.evidence_root.absolute().resolve()), "报告路径必须位于 evidence root 内")
            require(not report_path.exists(), f"拒绝覆盖既有报告：{report_path}")
            report_bytes = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
            report_path.write_bytes(report_bytes)
            result["report_path"] = str(report_path)
            result["report_sha256"] = sha256_bytes(report_bytes)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (D9VerificationError, OSError, ValueError, KeyError, TypeError, OverflowError, t29.ReferenceError) as error:
        print(f"T68_D9_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
