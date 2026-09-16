"""S1-T02-D3 资源、性能与阶段验收门槛的结构化检查器。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


UTC8 = timezone(timedelta(hours=8))
MODEL_KEYS = ("tiny320", "tiny416", "full")
MODEL_ROLES = {
    "tiny320": "board_candidate",
    "tiny416": "board_candidate",
    "full": "pc_only_reference",
}
EVIDENCE_KINDS = ("estimate", "synthesis", "board_measurement")
RESOURCE_METRICS = ("lut_pct", "ff_pct", "bram_pct", "dsp_pct")
TIMING_METRICS = ("wns_ns", "whs_ns", "tns_ns", "ths_ns")
STORAGE_FIELDS = (
    "weights_bytes",
    "feature_map_peak_bytes",
    "frame_buffer_bytes",
    "ps_buffer_bytes",
    "ddr_peak_bytes",
)
BANDWIDTH_FIELDS = (
    "video_input_bytes_per_s",
    "model_transfer_bytes_per_s",
    "ps_decode_nms_bytes_per_s",
    "cache_competition_bytes_per_s",
    "total_peak_bytes_per_s",
)
PERFORMANCE_STAGES = (
    "preprocess",
    "pl_model",
    "ps_decode_nms",
    "display",
    "end_to_end",
)
ALLOWED_STATUSES = ("MEASURED", "NOT_EXECUTED", "PENDING")
MODEL_INPUT_SIZES = {
    "tiny320": [320, 320],
    "tiny416": [416, 416],
    "full": [608, 608],
}
MODEL_IDS = {
    "tiny320": "yolov4_tiny_320_float_setup",
    "tiny416": "yolov4_tiny_416_float_setup",
    "full": "yolov4_full_608_pc_reference",
}
MODEL_CFG_BINDINGS = {
    "tiny320": "tiny320_cfg",
    "tiny416": "tiny416_cfg",
    "full": "full_cfg",
}
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def now_utc8() -> str:
    """返回当前东八区时间。"""
    return datetime.now(UTC8).isoformat(timespec="seconds")


def _finite_number(value: Any, field: str, errors: list[str]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{field}: 必须是有限数；关闭条件为提供 int/float")
        return None
    converted = float(value)
    if not math.isfinite(converted):
        errors.append(f"{field}: 不得为 NaN/Inf；关闭条件为有限数")
        return None
    return converted


def _nonnegative_integer(value: Any, field: str, errors: list[str]) -> int | None:
    if type(value) is not int or value < 0:
        errors.append(f"{field}: 必须是非负整数；关闭条件为非负计数")
        return None
    return value


def sha256_file(path: Path) -> str:
    """计算文件 SHA256，不改变文件。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _record_file_bindings(document: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    bindings = document.get("file_bindings")
    if not isinstance(bindings, dict) or not bindings:
        errors.append("file_bindings: 必须提供至少一个文件路径；关闭条件为可复核版本绑定")
        return {}
    recorded: dict[str, Any] = {}
    for name, raw_path in bindings.items():
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"file_bindings.{name}: 路径必须是非空字符串")
            continue
        path = Path(raw_path).resolve()
        if not path.is_file():
            errors.append(f"file_bindings.{name}: 文件不存在 {path}；关闭条件为提供可读文件")
            continue
        recorded[name] = {
            "path": str(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return recorded


def _run_git_probe(repository: Path, arguments: list[str], errors: list[str]) -> dict[str, Any]:
    command = ["git", "-C", str(repository), *arguments]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode not in (0, 1):
        errors.append(f"git probe {' '.join(arguments)}: exit={completed.returncode}")
    return {
        "repository": str(repository),
        "cwd": str(repository),
        "argv": command,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
        "observed_utc8": now_utc8(),
        "network_access": False,
    }


def _validate_metric_block(
    block: dict[str, Any], field_prefix: str, errors: list[str], pending: list[str], measured: bool = False
) -> None:
    if not isinstance(block, dict):
        errors.append(f"{field_prefix}: 必须是对象")
        return
    for field in RESOURCE_METRICS:
        value = block.get(field)
        if value is None:
            if measured:
                errors.append(f"{field_prefix}.{field}: MEASURED 必须提供有限数值；关闭条件为完整资源百分比")
            else:
                pending.append(f"{field_prefix}.{field}: 尚无观测值")
            continue
        number = _finite_number(value, f"{field_prefix}.{field}", errors)
        if number is not None and not 0.0 <= number <= 100.0:
            errors.append(f"{field_prefix}.{field}: 必须位于 [0,100]；关闭条件为合法百分比")
        if number is not None and number > 85.0:
            errors.append(f"{field_prefix}.{field}: {number} 超过 85%；关闭条件为不超过资源门槛")


def _validate_timing_block(
    block: dict[str, Any], field_prefix: str, errors: list[str], pending: list[str], measured: bool = False
) -> None:
    if not isinstance(block, dict):
        errors.append(f"{field_prefix}: 必须是对象")
        return
    lower_bounds = {"wns_ns": 0.0, "whs_ns": 0.0, "tns_ns": 0.0, "ths_ns": 0.0}
    for field in TIMING_METRICS:
        value = block.get(field)
        if value is None:
            if measured:
                errors.append(f"{field_prefix}.{field}: MEASURED 必须提供有限数值；关闭条件为完整时序字段")
            else:
                pending.append(f"{field_prefix}.{field}: 尚无观测值")
            continue
        number = _finite_number(value, f"{field_prefix}.{field}", errors)
        if number is not None:
            if field in ("wns_ns", "whs_ns") and number < lower_bounds[field]:
                errors.append(f"{field_prefix}.{field}: {number} 小于 0；关闭条件为 WNS/WHS >= 0")
            if field in ("tns_ns", "ths_ns") and number != 0.0:
                errors.append(f"{field_prefix}.{field}: {number} 非零；关闭条件为 TNS/THS = 0")


def _validate_evidence_entry(
    entry: Any,
    expected_kind: str,
    field_prefix: str,
    applicable: bool,
    errors: list[str],
    pending: list[str],
) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{field_prefix}: 必须是对象")
        return
    if entry.get("evidence_kind") != expected_kind:
        errors.append(f"{field_prefix}.evidence_kind: 必须为 {expected_kind}，禁止混用证据来源")
    status = entry.get("status")
    if status not in ALLOWED_STATUSES and status != "NOT_APPLICABLE":
        errors.append(f"{field_prefix}.status: 非法状态；允许 MEASURED、NOT_EXECUTED、PENDING 或适用时 NOT_APPLICABLE")
        return
    if status == "NOT_APPLICABLE":
        if applicable:
            errors.append(f"{field_prefix}.status: 适用模型不能标记 NOT_APPLICABLE")
        if not entry.get("reason"):
            errors.append(f"{field_prefix}.reason: 不适用必须给出技术理由")
        return
    if not applicable:
        errors.append(f"{field_prefix}: full 模型只允许 PC 对照，不应提供板上适用证据")
        return
    if status in ("NOT_EXECUTED", "PENDING"):
        pending.append(f"{field_prefix}: {status}")
    elif status != "MEASURED":
        errors.append(f"{field_prefix}.status: 仅允许 MEASURED、NOT_EXECUTED 或 PENDING")
    utilization = entry.get("utilization")
    timing = entry.get("timing")
    _validate_metric_block(utilization, f"{field_prefix}.utilization", errors, pending, measured=status == "MEASURED")
    _validate_timing_block(timing, f"{field_prefix}.timing", errors, pending, measured=status == "MEASURED")
    if status == "MEASURED":
        if any(item.startswith(f"{field_prefix}.utilization") or item.startswith(f"{field_prefix}.timing") for item in pending):
            errors.append(f"{field_prefix}: MEASURED 必须完整提供资源与时序数值")


def _validate_storage_and_bandwidth(
    resource: dict[str, Any], field_prefix: str, errors: list[str], pending: list[str]
) -> None:
    storage = resource.get("storage")
    if not isinstance(storage, dict):
        errors.append(f"{field_prefix}.storage: 必须是对象")
    else:
        storage_status = storage.get("status")
        if storage_status not in ALLOWED_STATUSES:
            errors.append(f"{field_prefix}.storage.status: 非法状态；允许 MEASURED、NOT_EXECUTED 或 PENDING")
        elif storage_status in ("NOT_EXECUTED", "PENDING"):
            pending.append(f"{field_prefix}.storage: {storage_status}")
        for field in STORAGE_FIELDS:
            if field not in storage:
                errors.append(f"{field_prefix}.storage.{field}: 缺少字段")
                continue
            value = storage[field]
            if value is None:
                if storage_status == "MEASURED":
                    errors.append(f"{field_prefix}.storage.{field}: MEASURED 必须提供非负整数")
                else:
                    pending.append(f"{field_prefix}.storage.{field}: 尚无观测值")
            else:
                _nonnegative_integer(value, f"{field_prefix}.storage.{field}", errors)
        ranges = storage.get("address_ranges")
        if not isinstance(ranges, list):
            errors.append(f"{field_prefix}.storage.address_ranges: 必须是列表")
        else:
            if storage_status == "MEASURED" and not ranges:
                errors.append(f"{field_prefix}.storage.address_ranges: MEASURED 必须提供地址区间")
            parsed: list[tuple[int, int, str]] = []
            for index, item in enumerate(ranges):
                prefix = f"{field_prefix}.storage.address_ranges[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{prefix}: 必须是对象")
                    continue
                name = item.get("name", str(index))
                start = item.get("start")
                end = item.get("end")
                if type(start) is not int or type(end) is not int or start < 0 or end <= start:
                    errors.append(f"{prefix}: 需要非负 start 且 end>start；关闭条件为半开区间")
                    continue
                parsed.append((start, end, str(name)))
            parsed.sort()
            for previous, current in zip(parsed, parsed[1:]):
                if current[0] < previous[1]:
                    errors.append(
                        f"{field_prefix}.storage.address_ranges: {previous[2]} 与 {current[2]} 重叠；关闭条件为地址无重叠"
                    )
    bandwidth = resource.get("ddr_bandwidth")
    if not isinstance(bandwidth, dict):
        errors.append(f"{field_prefix}.ddr_bandwidth: 必须是对象")
    else:
        bandwidth_status = bandwidth.get("status")
        if bandwidth_status not in ALLOWED_STATUSES:
            errors.append(f"{field_prefix}.ddr_bandwidth.status: 非法状态；允许 MEASURED、NOT_EXECUTED 或 PENDING")
        elif bandwidth_status in ("NOT_EXECUTED", "PENDING"):
            pending.append(f"{field_prefix}.ddr_bandwidth: {bandwidth_status}")
        values: dict[str, float] = {}
        for field in BANDWIDTH_FIELDS:
            if field not in bandwidth:
                errors.append(f"{field_prefix}.ddr_bandwidth.{field}: 缺少字段")
                continue
            value = bandwidth[field]
            if value is None:
                if bandwidth_status == "MEASURED":
                    errors.append(f"{field_prefix}.ddr_bandwidth.{field}: MEASURED 必须提供有限非负数")
                else:
                    pending.append(f"{field_prefix}.ddr_bandwidth.{field}: 尚无观测值")
                continue
            number = _finite_number(value, f"{field_prefix}.ddr_bandwidth.{field}", errors)
            if number is not None:
                if number < 0:
                    errors.append(f"{field_prefix}.ddr_bandwidth.{field}: 不得为负数")
                values[field] = number
        component_sum = sum(values.get(field, 0.0) for field in BANDWIDTH_FIELDS[:-1])
        total = values.get("total_peak_bytes_per_s")
        if total is not None and len(values) == len(BANDWIDTH_FIELDS) and total < component_sum:
            errors.append(f"{field_prefix}.ddr_bandwidth.total_peak_bytes_per_s: 小于组成项之和；关闭条件为覆盖视频/模型/PS/缓存竞争")


def _validate_fixed_config(
    fixed: Any, model_key: str, field_prefix: str, errors: list[str], pending: list[str], measured: bool = False
) -> None:
    if not isinstance(fixed, dict):
        errors.append(f"{field_prefix}: 必须是对象")
        return
    required = (
        "model_id",
        "input_size",
        "weight_sha256",
        "cfg_sha256",
        "preprocess_sha256",
        "score_threshold",
        "nms_iou",
        "max_detections",
    )
    for field in required:
        if field not in fixed:
            errors.append(f"{field_prefix}.{field}: 缺少固定配置字段")
    if fixed.get("model_id") != MODEL_IDS[model_key]:
        errors.append(f"{field_prefix}.model_id: 必须为 {MODEL_IDS[model_key]}，与模型角色/配置不一致")
    if fixed.get("input_size") != MODEL_INPUT_SIZES[model_key]:
        errors.append(f"{field_prefix}.input_size: 必须为 {MODEL_INPUT_SIZES[model_key]}，与模型键不一致")
    for field in ("cfg_sha256", "preprocess_sha256"):
        value = fixed.get(field)
        if value is None:
            errors.append(f"{field_prefix}.{field}: 必须绑定 64 位 SHA-256")
        elif not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
            errors.append(f"{field_prefix}.{field}: 必须是 64 位十六进制 SHA-256")
    weight = fixed.get("weight_sha256")
    if weight is None:
        if measured:
            errors.append(f"{field_prefix}.weight_sha256: MEASURED 必须绑定实际 64 位 SHA-256")
        else:
            pending.append(f"{field_prefix}.weight_sha256: 尚未绑定最终权重")
    elif not isinstance(weight, str) or not SHA256_PATTERN.fullmatch(weight):
        errors.append(f"{field_prefix}.weight_sha256: 必须是 64 位十六进制 SHA-256")
    for field in ("score_threshold", "nms_iou"):
        value = fixed.get(field)
        if value is None:
            if measured:
                errors.append(f"{field_prefix}.{field}: MEASURED 必须绑定数值")
            else:
                pending.append(f"{field_prefix}.{field}: 尚未绑定")
        else:
            number = _finite_number(value, f"{field_prefix}.{field}", errors)
            if number is not None and not 0.0 <= number <= 1.0:
                errors.append(f"{field_prefix}.{field}: 必须位于 [0,1]")
    _nonnegative_integer(fixed.get("max_detections"), f"{field_prefix}.max_detections", errors)


def _validate_performance(
    performance: Any, model_key: str, field_prefix: str, errors: list[str], pending: list[str]
) -> None:
    if not isinstance(performance, dict):
        errors.append(f"{field_prefix}: 必须是对象")
        return
    status = performance.get("status")
    _validate_fixed_config(
        performance.get("fixed_config"),
        model_key,
        f"{field_prefix}.fixed_config",
        errors,
        pending,
        measured=status == "MEASURED",
    )
    if performance.get("warmup") != 100:
        errors.append(f"{field_prefix}.warmup: 必须为 100；关闭条件为固定预热次数")
    effective = performance.get("effective_inferences")
    if type(effective) is not int or effective < 0:
        errors.append(f"{field_prefix}.effective_inferences: 必须为非负整数")
    elif performance.get("status") == "MEASURED" and effective < 10000:
        errors.append(f"{field_prefix}.effective_inferences: {effective} 少于 10000；关闭条件为不少于 10000 次有效推理")
    elif performance.get("status") != "MEASURED" and effective < 10000:
        pending.append(f"{field_prefix}.effective_inferences: 尚未达到 10000 次有效推理")
    if status in ("NOT_EXECUTED", "PENDING"):
        pending.append(f"{field_prefix}: {status}")
    elif status != "MEASURED":
        errors.append(f"{field_prefix}.status: 仅允许 MEASURED、NOT_EXECUTED 或 PENDING")
    stages = performance.get("stages")
    if not isinstance(stages, dict):
        errors.append(f"{field_prefix}.stages: 必须是对象")
    else:
        for stage in PERFORMANCE_STAGES:
            entry = stages.get(stage)
            if not isinstance(entry, dict):
                errors.append(f"{field_prefix}.stages.{stage}: 缺少阶段计时对象")
                continue
            stage_status = entry.get("status")
            if stage_status not in ALLOWED_STATUSES:
                errors.append(f"{field_prefix}.stages.{stage}.status: 非法状态；允许 MEASURED、NOT_EXECUTED 或 PENDING")
                stage_status = status
            elif status == "MEASURED" and stage_status != "MEASURED":
                errors.append(f"{field_prefix}.stages.{stage}.status: 父级 MEASURED 时每个阶段也必须为 MEASURED")
            for metric in ("mean_ms", "p50_ms", "p95_ms", "p99_ms"):
                value = entry.get(metric)
                if value is None:
                    if stage_status == "MEASURED":
                        errors.append(f"{field_prefix}.stages.{stage}.{metric}: MEASURED 必须提供有限非负数")
                    else:
                        pending.append(f"{field_prefix}.stages.{stage}.{metric}: 尚无观测值")
                else:
                    number = _finite_number(value, f"{field_prefix}.stages.{stage}.{metric}", errors)
                    if number is not None and number < 0:
                        errors.append(f"{field_prefix}.stages.{stage}.{metric}: 不得为负数")
            p50 = entry.get("p50_ms")
            p95 = entry.get("p95_ms")
            p99 = entry.get("p99_ms")
            if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in (p50, p95, p99)) and not (p50 <= p95 <= p99):
                errors.append(f"{field_prefix}.stages.{stage}: 分位数必须满足 P50<=P95<=P99")
    failures = performance.get("failure_counts")
    if not isinstance(failures, dict):
        errors.append(f"{field_prefix}.failure_counts: 必须是对象")
    else:
        for field in ("timeout", "drop", "failure"):
            if field not in failures:
                errors.append(f"{field_prefix}.failure_counts.{field}: 缺少失败计数")
            else:
                _nonnegative_integer(failures[field], f"{field_prefix}.failure_counts.{field}", errors)
    if performance.get("sample_selection") != "all_valid_samples_no_fast_sample_filter":
        errors.append(f"{field_prefix}.sample_selection: 必须声明不筛选快样本")


def validate_document(document: dict[str, Any]) -> dict[str, Any]:
    """检查 D3 规格/证据并返回结构化结果。"""
    errors: list[str] = []
    pending: list[str] = []
    if document.get("schema_version") != "s1_t02_d3_resource_performance_v1":
        errors.append("schema_version: 不匹配 D3 v1")
    thresholds = document.get("thresholds")
    if not isinstance(thresholds, dict):
        errors.append("thresholds: 必须是对象")
    else:
        if thresholds.get("max_utilization_percent") != 85:
            errors.append("thresholds.max_utilization_percent: 必须为 85")
        for field, expected in (("wns_min_ns", 0), ("whs_min_ns", 0), ("tns_max_ns", 0), ("ths_max_ns", 0)):
            if thresholds.get(field) != expected:
                errors.append(f"thresholds.{field}: 不符合批准门槛 {expected}")
    if document.get("final_threshold_status") != "pending_until_wong_decision":
        errors.append("final_threshold_status: 必须为 pending_until_wong_decision；不得隐式冻结旧性能门槛")
    board = document.get("hardware_baseline")
    if not isinstance(board, dict) or board.get("board") != "AX7Z020" or board.get("device") != "XA7Z020" or board.get("package") != "CLG400" or board.get("speed_grade") != "-1":
        errors.append("hardware_baseline: 必须绑定 AX7Z020/XA7Z020 CLG400 -1 基线")
    models = document.get("models")
    if not isinstance(models, dict) or set(models) != set(MODEL_KEYS):
        errors.append("models: 必须恰好包含 tiny320、tiny416、full")
        models = {}
    model_results: dict[str, Any] = {}
    for model_key in MODEL_KEYS:
        model = models.get(model_key)
        prefix = f"models.{model_key}"
        if not isinstance(model, dict):
            errors.append(f"{prefix}: 必须是对象")
            continue
        if model.get("role") != MODEL_ROLES[model_key]:
            errors.append(f"{prefix}.role: 角色不正确")
        applicable = model_key != "full"
        applicability = model.get("applicability")
        if not isinstance(applicability, dict):
            errors.append(f"{prefix}.applicability: 必须是对象")
        else:
            if applicability.get("board_resource_gate") is not applicable:
                errors.append(f"{prefix}.applicability.board_resource_gate: 与模型角色不一致")
            if applicability.get("pc_budget") is not True:
                errors.append(f"{prefix}.applicability.pc_budget: 必须为 true")
        resource = model.get("resource")
        model_pending_before = len(pending)
        if not isinstance(resource, dict):
            errors.append(f"{prefix}.resource: 必须是对象")
        else:
            evidence = resource.get("evidence")
            if not isinstance(evidence, dict):
                errors.append(f"{prefix}.resource.evidence: 必须分离 estimate/synthesis/board_measurement")
            else:
                for kind in EVIDENCE_KINDS:
                    _validate_evidence_entry(evidence.get(kind), kind, f"{prefix}.resource.evidence.{kind}", applicable or kind == "estimate", errors, pending)
            _validate_storage_and_bandwidth(resource, prefix + ".resource", errors, pending)
        _validate_performance(model.get("performance"), model_key, prefix + ".performance", errors, pending)
        resource_pending = len(pending) > model_pending_before
        model_results[model_key] = {
            "resource_status": "NOT_APPLICABLE_PC_ONLY" if not applicable else ("NOT_EXECUTED_PENDING" if resource_pending else "READY_FOR_WONG_DECISION"),
            "performance_status": "NOT_EXECUTED_PENDING" if any(item.startswith(prefix + ".performance") for item in pending) else "READY_FOR_WONG_DECISION",
        }
    file_errors: list[str] = []
    files = _record_file_bindings(document, file_errors)
    errors.extend(file_errors)
    for model_key in MODEL_KEYS:
        model = models.get(model_key)
        if not isinstance(model, dict):
            continue
        fixed = model.get("performance", {}).get("fixed_config", {})
        cfg_binding = MODEL_CFG_BINDINGS[model_key]
        if cfg_binding not in files:
            errors.append(f"models.{model_key}.performance.fixed_config.cfg_sha256: 缺少交叉绑定文件 {cfg_binding}")
        elif fixed.get("cfg_sha256") != files[cfg_binding]["sha256"]:
            errors.append(f"models.{model_key}.performance.fixed_config.cfg_sha256: 与 {cfg_binding} 文件 SHA 不一致")
        if "d2_numeric_reference" not in files:
            errors.append(f"models.{model_key}.performance.fixed_config.preprocess_sha256: 缺少 d2_numeric_reference 文件绑定")
        elif fixed.get("preprocess_sha256") != files["d2_numeric_reference"]["sha256"]:
            errors.append(f"models.{model_key}.performance.fixed_config.preprocess_sha256: 与 d2_numeric_reference 文件 SHA 不一致")
    probes: dict[str, Any] = {}
    provenance = document.get("provenance_requests")
    if isinstance(provenance, dict):
        for name, raw_path in provenance.items():
            if not isinstance(raw_path, str):
                errors.append(f"provenance_requests.{name}: 必须是仓库路径")
                continue
            repository = Path(raw_path).resolve()
            if not repository.is_dir():
                errors.append(f"provenance_requests.{name}: 仓库不存在 {repository}")
                continue
            probes[name] = {
                "head": _run_git_probe(repository, ["rev-parse", "HEAD"], errors),
                "diff_quiet": _run_git_probe(repository, ["diff", "--quiet"], errors),
                "status_short": _run_git_probe(repository, ["status", "--short"], errors),
            }
    else:
        errors.append("provenance_requests: 必须提供仓库路径")
    if errors:
        status = "INVALID"
    elif pending:
        status = "NOT_EXECUTED_PENDING"
    else:
        status = "READY_FOR_WONG_DECISION"
    return {
        "validation": {
            "status": status,
            "schema_valid": not errors,
            "errors": errors,
            "pending": pending,
            "models": model_results,
        },
        "files": files,
        "git_probes": probes,
        "observed_utc8": now_utc8(),
        "network_access": False,
    }


def _summary(report: dict[str, Any], input_path: Path, report_path: Path, summary_path: Path) -> str:
    """生成中文 D3 证据摘要。"""
    validation = report["validation"]
    status = validation["status"]
    return f"""# S1-T02-D3 资源、性能与阶段验收门槛

状态：`{status}`。本任务只冻结资源/性能测量口径和自动检查语义；没有伪造 Vivado 综合、真实板上测量或最终 FPS/延迟结果。

## 已编码门槛

- 硬件基线：AX7Z020 / XA7Z020 CLG400，`-1` 时序基线；LUT、FF、BRAM、DSP 分别不超过 85%；WNS/WHS 不小于 0，TNS/THS 必须为 0。
- tiny320、tiny416 分别作为板上候选预算；完整 YOLOv4 仅 PC 对照，板上资源验收为不适用，但保留 PC 计算/存储预算字段。
- 权重、feature map、frame buffer、PS buffer、DDR peak 分栏；DDR 带宽字段覆盖视频输入、模型传输、PS 解码/NMS、缓存竞争及总峰值。
- 每个固定配置要求 100 次 warmup、至少 10000 次有效推理，不筛快样本；分别记录 preprocess、PL/model、PS decode/NMS、display、end-to-end 的 mean/P50/P95/P99，并单列 timeout/drop/failure。
- `final_threshold_status=pending_until_wong_decision`；旧 20 FPS、100 ms、3–5 倍不作为现行门槛。

## 当前证据

- `estimate`、`synthesis`、`board_measurement` 严格分栏；当前缺少综合与板测，自动状态为 `NOT_EXECUTED_PENDING`，不是 PASS。
- 机器报告：`{report_path.resolve()}`。
- 校验错误数：`{len(validation['errors'])}`；待执行/待决数：`{len(validation['pending'])}`。
- 当前未执行训练、CUDA 长测、Vivado 综合、上板烧录、板上性能测量和最终精度/性能判定。

## 关口状态语义

- G0：本规格和输入输出口径待总控/Wong确认；本报告不宣称正式 G0 通过。
- G1：检查器、测试和证据结构已实现；不等于资源或性能实测。
- G2：须由独立 Reviewer 核对版本、字段、边界和证据来源。
- G3：tiny 需要目标板综合/实现及板上实测；full 对板上资源不适用。
- G4：必须同时具备精度、数值、资源和性能适用证据，并经 Wong 决策冻结最终候选。

## 复现命令

```powershell
py verification\\s1_t02_d3_resource_performance.py --input "{input_path}" --report "{report_path}" --summary "{summary_path}"
```

该命令只读输入并刷新机器报告/摘要，不启动训练、CUDA、Vivado 或硬件；非法百分比、时序、地址重叠、样本不足和错误证据来源返回非零退出码。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 S1-T02-D3 资源与性能规格证据")
    parser.add_argument("--input", type=Path, required=True, help="D3 JSON 规格或已有证据")
    parser.add_argument("--report", type=Path, required=True, help="机器检查报告")
    parser.add_argument("--summary", type=Path, required=True, help="中文摘要")
    args = parser.parse_args()
    try:
        input_path = args.input.resolve()
        report_path = args.report.resolve()
        if input_path == report_path:
            print("D3 检查失败: --input 与 --report 规范化后不能相同；请使用不可变 spec input 和独立 report output", file=sys.stderr)
            return 2
        document = json.loads(input_path.read_text(encoding="utf-8"))
        result = validate_document(document)
        output = {
            **document,
            "validation": result["validation"],
            "files": result["files"],
            "git_probes": result["git_probes"],
            "observed_utc8": result["observed_utc8"],
            "argv": [str(value) for value in sys.argv],
            "cwd": str(Path.cwd()),
            "spec_input": str(input_path),
            "network_access": False,
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        summary_path = args.summary.resolve()
        summary_path.write_text(_summary(output, input_path, report_path, summary_path), encoding="utf-8", newline="\n")
        print(json.dumps({"status": result["validation"]["status"], "errors": len(result["validation"]["errors"]), "pending": len(result["validation"]["pending"])}, ensure_ascii=False))
        return 0 if result["validation"]["schema_valid"] else 2
    except Exception as error:
        print(f"D3 检查失败: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
