"""S1-T02-D4 官方 Darknet 浮点基线的绑定与预检工具。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
ALLOWED_SEED_STATUS = {"READY", "PENDING", "BLOCKED"}
ALLOWED_PILOT_STATUS = {"NOT_EXECUTED", "BLOCKED", "COMPLETED"}
EXPECTED_MODELS = {
    "tiny320": {"role": "board_candidate", "input_size": [320, 320], "yolo_count": 2},
    "tiny416": {"role": "board_candidate", "input_size": [416, 416], "yolo_count": 2},
    "full": {"role": "pc_only_reference", "input_size": [608, 608], "yolo_count": 3},
}
EXPECTED_TRAINING = {
    "tiny320": {
        "batch": 64,
        "subdivisions": 16,
        "learning_rate": 0.00261,
        "momentum": 0.9,
        "decay": 0.0005,
        "max_batches": 6000,
        "steps": [4800, 5400],
        "burn_in": 1000,
    },
    "tiny416": {
        "batch": 64,
        "subdivisions": 16,
        "learning_rate": 0.00261,
        "momentum": 0.9,
        "decay": 0.0005,
        "max_batches": 6000,
        "steps": [4800, 5400],
        "burn_in": 1000,
    },
    "full": {
        "batch": 64,
        "subdivisions": 32,
        "learning_rate": 0.0013,
        "momentum": 0.9,
        "decay": 0.0005,
        "max_batches": 6000,
        "steps": [4800, 5400],
        "burn_in": 1000,
    },
}


def sha256_file(path: Path) -> str:
    """以分块方式计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc8_now() -> str:
    """返回带时区的 UTC+8 时间。"""
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def normalized(path: str | Path) -> Path:
    """按操作系统语义解析路径，比较时不依赖字符串斜杠形式。"""
    return Path(path).expanduser().resolve(strict=False)


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _as_float(value: str) -> float:
    return float(value.strip())


def parse_key_values(path: Path) -> Dict[str, str]:
    """解析 Darknet data 配置中的键值，坏行直接报错。"""
    values: Dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: 缺少 '='")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value:
            raise ValueError(f"{path}:{line_number}: 键或值为空")
        values[key] = value
    return values


def parse_cfg(path: Path) -> List[Dict[str, str]]:
    """解析 cfg 的 section 和键值，保留 section 顺序。"""
    sections: List[Dict[str, str]] = []
    current: Optional[Dict[str, str]] = None
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = {"__section__": line[1:-1].strip()}
            sections.append(current)
            continue
        if current is None or "=" not in line:
            raise ValueError(f"{path}:{line_number}: cfg 行无 section 或缺少 '='")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value:
            raise ValueError(f"{path}:{line_number}: cfg 键或值为空")
        current[key] = value
    if not sections or sections[0].get("__section__") != "net":
        raise ValueError(f"{path}: 首个 section 必须是 [net]")
    return sections


def _error(errors: List[str], field: str, reason: str) -> None:
    errors.append(f"{field}: {reason}")


def _check_hash(
    errors: List[str], field: str, declared: Any, actual: Optional[str], required: bool = True
) -> None:
    if declared is None:
        if required:
            _error(errors, field, "缺少 SHA-256")
        return
    if not isinstance(declared, str) or not HASH_PATTERN.fullmatch(declared):
        _error(errors, field, "必须是 64 位十六进制 SHA-256")
        return
    if actual is not None and declared.lower() != actual.lower():
        _error(errors, field, f"与现场文件 SHA-256 不一致，实际为 {actual}")


def _under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _check_binding(
    errors: List[str], binding: Mapping[str, Any], run_dir: Path, required: bool = True
) -> None:
    name = str(binding.get("name", "未命名绑定"))
    raw_path = binding.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        _error(errors, f"file_bindings.{name}.path", "路径为空")
        return
    path = normalized(raw_path)
    if not path.is_file():
        if required:
            _error(errors, f"file_bindings.{name}.path", f"文件不存在: {path}")
        return
    _check_hash(errors, f"file_bindings.{name}.sha256", binding.get("sha256"), sha256_file(path), required)
    if binding.get("scope") == "run" and not _under(path, run_dir):
        _error(errors, f"file_bindings.{name}.path", "scope=run 但路径不在隔离 run-dir 内")


def _check_plan_binding(
    errors: List[str],
    binding_by_name: Mapping[str, Mapping[str, Any]],
    name: str,
    path_value: Any,
    sha_value: Any,
) -> None:
    """将计划字段与同名文件绑定逐项交叉核对。"""
    binding = binding_by_name.get(name)
    if binding is None:
        _error(errors, f"file_bindings.{name}", "缺少计划字段对应的文件绑定")
        return
    binding_path = binding.get("path")
    if not isinstance(path_value, str) or not isinstance(binding_path, str):
        _error(errors, f"file_bindings.{name}", "计划路径和绑定路径都必须存在")
    elif normalized(path_value) != normalized(binding_path):
        _error(errors, f"file_bindings.{name}.path", "与计划字段路径不一致")
    if (
        sha_value is not None
        and isinstance(binding.get("sha256"), str)
        and binding.get("sha256").lower() != str(sha_value).lower()
    ):
        _error(errors, f"file_bindings.{name}.sha256", "与计划字段 SHA-256 不一致")


def _check_source(
    errors: List[str], source: Mapping[str, Any], run_dir: Path, source_repo: Path
) -> None:
    """校验官方源与隔离修改源的提交、探测和文件绑定。"""
    patched_value = source.get("patched_repository")
    patched_repo = normalized(patched_value) if isinstance(patched_value, str) else Path()
    if not patched_repo.is_dir():
        _error(errors, "source.patched_repository", f"隔离修改源目录不存在: {patched_repo}")
    elif not _under(patched_repo, run_dir):
        _error(errors, "source.patched_repository", "隔离修改源必须位于 D4 run-dir 内")

    modified_files = source.get("modified_files")
    if not isinstance(modified_files, list) or not modified_files:
        _error(errors, "source.modified_files", "必须列出隔离修改源的文件和 SHA-256")
    else:
        for index, item in enumerate(modified_files):
            if not isinstance(item, Mapping):
                _error(errors, f"source.modified_files[{index}]", "必须是对象")
                continue
            path_value = item.get("path")
            if not isinstance(path_value, str) or not path_value:
                _error(errors, f"source.modified_files[{index}].path", "路径为空")
                continue
            path = normalized(path_value)
            if patched_repo.is_dir() and not _under(path, patched_repo):
                _error(errors, f"source.modified_files[{index}].path", "修改文件不在隔离 patched source 内")
            if not path.is_file():
                _error(errors, f"source.modified_files[{index}].path", f"文件不存在: {path}")
                continue
            _check_hash(
                errors,
                f"source.modified_files[{index}].sha256",
                item.get("sha256"),
                sha256_file(path),
            )

    probe = source.get("probe", {})
    if not isinstance(probe, Mapping):
        return
    commands = probe.get("commands")
    if not isinstance(commands, list):
        _error(errors, "source.probe.commands", "必须记录 rev-parse 和 diff 的实际命令")
        return
    rev_command = None
    diff_command = None
    for item in commands:
        if not isinstance(item, Mapping) or not isinstance(item.get("argv"), list):
            continue
        argv = item["argv"]
        if argv == ["git", "-C", str(source_repo).replace("\\", "/"), "rev-parse", "HEAD"]:
            rev_command = item
        if argv == ["git", "-C", str(source_repo).replace("\\", "/"), "diff", "--quiet"]:
            diff_command = item
    if rev_command is None:
        _error(errors, "source.probe.commands", "缺少官方源 git rev-parse HEAD 记录")
    else:
        stdout = rev_command.get("stdout")
        if rev_command.get("exit_code") != 0 or not isinstance(stdout, str):
            _error(errors, "source.probe.rev_parse", "rev-parse 必须退出 0 并记录 stdout")
        elif stdout.strip() != source.get("commit_observed"):
            _error(errors, "source.commit_observed", "必须等于 rev-parse stdout 的完整 40 位值")
    if diff_command is None:
        _error(errors, "source.probe.commands", "缺少官方源 git diff --quiet 记录")
    elif diff_command.get("exit_code") != 0:
        _error(errors, "source.probe.diff", "git diff --quiet 必须退出 0")

    git_marker = (source_repo / ".git").is_dir() or (source_repo / ".git").is_file()
    if git_marker and isinstance(source.get("commit_observed"), str):
        live_rev = subprocess.run(
            ["git", "-C", str(source_repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if live_rev.returncode != 0 or live_rev.stdout.strip() != source.get("commit_observed"):
            _error(errors, "source.commit_observed", "与现场 git rev-parse HEAD 不一致")
        live_diff = subprocess.run(
            ["git", "-C", str(source_repo), "diff", "--quiet"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if live_diff.returncode != 0:
            _error(errors, "source.diff_exit_code", "现场官方源 git diff --quiet 未退出 0")


def _check_preprocessing(errors: List[str], plan: Mapping[str, Any]) -> None:
    """校验 D2 预处理参考实现的现场文件和完整 SHA-256。"""
    preprocessing = plan.get("preprocessing")
    if not isinstance(preprocessing, Mapping):
        _error(errors, "preprocessing", "必须是对象")
        return
    raw_path = preprocessing.get("reference_path")
    if not isinstance(raw_path, str) or not raw_path:
        _error(errors, "preprocessing.reference_path", "路径为空")
        return
    path = normalized(raw_path)
    if not path.is_file():
        _error(errors, "preprocessing.reference_path", f"文件不存在: {path}")
        return
    _check_hash(
        errors,
        "preprocessing.reference_sha256",
        preprocessing.get("reference_sha256"),
        sha256_file(path),
    )


def _check_cfg(
    errors: List[str], model_id: str, model: Mapping[str, Any], run_dir: Path
) -> None:
    expected = EXPECTED_MODELS[model_id]
    cfg_value = model.get("config_path")
    if not isinstance(cfg_value, str) or not cfg_value:
        _error(errors, f"models.{model_id}.config_path", "配置路径为空")
        return
    cfg_path = normalized(cfg_value)
    if not cfg_path.is_file():
        _error(errors, f"models.{model_id}.config_path", f"配置不存在: {cfg_path}")
        return
    _check_hash(errors, f"models.{model_id}.config_sha256", model.get("config_sha256"), sha256_file(cfg_path))
    try:
        sections = parse_cfg(cfg_path)
    except (OSError, ValueError) as exc:
        _error(errors, f"models.{model_id}.config_path", str(exc))
        return
    net = sections[0]
    try:
        actual_size = [int(net["width"]), int(net["height"])]
        channels = int(net["channels"])
    except (KeyError, ValueError) as exc:
        _error(errors, f"models.{model_id}.config", f"net 尺寸/通道不可解析: {exc}")
        return
    if actual_size != expected["input_size"]:
        _error(errors, f"models.{model_id}.input_size", f"期望 {expected['input_size']}，实际 {actual_size}")
    if model.get("input_size") != expected["input_size"]:
        _error(errors, f"models.{model_id}.input_size", "计划尺寸与模型键不一致")
    if channels != 3:
        _error(errors, f"models.{model_id}.config.channels", "必须为 3")
    training = model.get("training", {})
    if not isinstance(training, Mapping):
        _error(errors, f"models.{model_id}.training", "必须是对象")
    else:
        for key, expected_value in EXPECTED_TRAINING[model_id].items():
            actual_value = training.get(key)
            if actual_value != expected_value:
                _error(errors, f"models.{model_id}.training.{key}", f"期望 {expected_value}，实际 {actual_value}")
    cfg_types = {
        "batch": int,
        "subdivisions": int,
        "learning_rate": float,
        "momentum": float,
        "decay": float,
        "burn_in": int,
        "max_batches": int,
        "steps": "int_list",
    }
    for key, value_type in cfg_types.items():
        raw_value = net.get(key)
        field = f"models.{model_id}.config.{key}"
        if raw_value is None:
            _error(errors, field, "实际 cfg 缺少训练字段")
            continue
        try:
            if value_type == "int_list":
                actual_value = [int(part.strip()) for part in raw_value.split(",") if part.strip()]
            elif value_type is int:
                actual_value = int(raw_value)
            else:
                actual_value = float(raw_value)
        except (TypeError, ValueError):
            _error(errors, field, f"实际 cfg 字段不可解析: {raw_value}")
            continue
        expected_value = EXPECTED_TRAINING[model_id][key]
        if value_type is float:
            matches = math.isclose(float(actual_value), float(expected_value), rel_tol=0.0, abs_tol=1e-12)
        else:
            matches = actual_value == expected_value
        if not matches:
            _error(errors, field, f"期望 {expected_value}，实际 {actual_value}")
    yolo_sections = [section for section in sections if section.get("__section__") == "yolo"]
    if len(yolo_sections) != expected["yolo_count"]:
        _error(errors, f"models.{model_id}.topology.yolo_count", f"期望 {expected['yolo_count']}，实际 {len(yolo_sections)}")
    for index, yolo in enumerate(yolo_sections):
        if yolo.get("classes") != "5":
            _error(errors, f"models.{model_id}.topology.yolo[{index}].classes", "必须为 5")
        for key in ("anchors", "mask"):
            if not yolo.get(key):
                _error(errors, f"models.{model_id}.topology.yolo[{index}].{key}", "不能为空")
        yolo_index = sections.index(yolo)
        preceding = next(
            (section for section in reversed(sections[:yolo_index]) if section.get("__section__") == "convolutional"),
            None,
        )
        if preceding is None or preceding.get("filters") != "30":
            _error(errors, f"models.{model_id}.topology.yolo[{index}].head_filters", "检测头前 convolutional filters 必须为 30")
    if not _under(cfg_path, run_dir):
        _error(errors, f"models.{model_id}.config_path", "配置必须来自本 D4 隔离 run-dir")


def _check_data_cfg(
    errors: List[str], model_id: str, model: Mapping[str, Any], run_dir: Path, expected_counts: Mapping[str, int]
) -> None:
    raw = model.get("data_config_path")
    if not isinstance(raw, str) or not raw:
        _error(errors, f"models.{model_id}.data_config_path", "data 配置路径为空")
        return
    path = normalized(raw)
    if not path.is_file():
        _error(errors, f"models.{model_id}.data_config_path", f"data 配置不存在: {path}")
        return
    _check_hash(errors, f"models.{model_id}.data_config_sha256", model.get("data_config_sha256"), sha256_file(path))
    try:
        values = parse_key_values(path)
    except (OSError, ValueError) as exc:
        _error(errors, f"models.{model_id}.data_config", str(exc))
        return
    if values.get("classes") != "5":
        _error(errors, f"models.{model_id}.data.classes", "必须为 5")
    for key in ("names", "train", "valid", "backup"):
        value = values.get(key)
        if not value:
            _error(errors, f"models.{model_id}.data.{key}", "缺少键")
            continue
        resolved = normalized(value)
        if key != "backup" and not resolved.is_file():
            _error(errors, f"models.{model_id}.data.{key}", f"文件不存在: {resolved}")
        if key == "backup" and not _under(resolved, run_dir):
            _error(errors, f"models.{model_id}.data.backup", "必须位于隔离 run-dir 内")
    if values.get("train") and normalized(values["train"]).is_file():
        train_count = sum(1 for line in normalized(values["train"]).read_text(encoding="utf-8").splitlines() if line.strip())
        if train_count != expected_counts.get("train", train_count):
            _error(errors, f"models.{model_id}.data.train_count", f"实际 {train_count}，计划 {expected_counts.get('train')}")
    if values.get("valid") and normalized(values["valid"]).is_file():
        valid_count = sum(1 for line in normalized(values["valid"]).read_text(encoding="utf-8").splitlines() if line.strip())
        if valid_count != expected_counts.get("valid", valid_count):
            _error(errors, f"models.{model_id}.data.valid_count", f"实际 {valid_count}，计划 {expected_counts.get('valid')}")


def _check_command(
    errors: List[str],
    model_id: str,
    command: Any,
    executable: Path,
    data_config_path: Any,
    config_path: Any,
    weight_path: Any,
) -> None:
    """校验官方 detector train 的固定 argv 位置和模型文件交叉绑定。"""
    if not isinstance(command, list) or len(command) < 6:
        _error(errors, f"commands.{model_id}", "必须是至少包含官方 train 五个位置参数的 argv 数组")
        return
    if normalized(command[0]) != executable:
        _error(errors, f"commands.{model_id}[0]", "可执行文件未与 build 绑定")
    if command[1:3] != ["detector", "train"]:
        _error(errors, f"commands.{model_id}[1:3]", "必须是官方 detector train")
    if any(flag in command[3:6] for flag in ("-dont_show", "-map", "-out")):
        _error(errors, f"commands.{model_id}", "data/cfg/weights 的固定位置被 flag 占用")
    if "-map" in command or "-out" in command:
        _error(errors, f"commands.{model_id}", "D4 pilot 不允许正式 test/mAP 参数")
    expected_paths = {
        3: (data_config_path, "data_config_path"),
        4: (config_path, "config_path"),
        5: (weight_path, "initial_weight.path"),
    }
    for index, (expected_value, label) in expected_paths.items():
        if not isinstance(expected_value, str) or not expected_value:
            _error(errors, f"commands.{model_id}[{index}]", f"缺少 {label} 绑定")
        elif not isinstance(command[index], str) or normalized(command[index]) != normalized(expected_value):
            _error(errors, f"commands.{model_id}[{index}]", f"必须等于模型的 {label}")


def _check_build(
    errors: List[str], build: Mapping[str, Any], patched_repo: Path, run_dir: Path
) -> Path:
    """校验隔离构建、日志、可执行文件及其来源绑定。"""
    source_directory = build.get("source_directory")
    if not isinstance(source_directory, str) or normalized(source_directory) != patched_repo:
        _error(errors, "build.source_directory", "必须等于隔离 patched source 路径")
    build_directory_value = build.get("build_directory")
    build_directory = normalized(build_directory_value) if isinstance(build_directory_value, str) else Path()
    if not build_directory.is_dir():
        _error(errors, "build.build_directory", f"构建目录不存在: {build_directory}")
    elif not _under(build_directory, run_dir):
        _error(errors, "build.build_directory", "构建目录必须位于隔离 run-dir 内")
    for label in ("configure_log", "build_log"):
        path_value = build.get(label)
        if not isinstance(path_value, str) or not normalized(path_value).is_file():
            _error(errors, f"build.{label}", "日志路径不存在")
            continue
        _check_hash(
            errors,
            f"build.{label}_sha256",
            build.get(f"{label}_sha256"),
            sha256_file(normalized(path_value)),
        )
    executable_value = build.get("executable_path")
    executable = normalized(executable_value) if isinstance(executable_value, str) else Path()
    if not executable.is_file():
        _error(errors, "build.executable_path", f"Darknet executable 不存在: {executable}")
    elif build_directory.is_dir() and not _under(executable, build_directory):
        _error(errors, "build.executable_path", "可执行文件必须来自隔离 build-directory")
    _check_hash(
        errors,
        "build.executable_sha256",
        build.get("executable_sha256"),
        sha256_file(executable) if executable.is_file() else None,
    )
    if build.get("configure_exit_code") != 0:
        _error(errors, "build.configure_exit_code", "CMake configure 必须退出 0")
    if build.get("build_exit_code") != 0:
        _error(errors, "build.build_exit_code", "构建/复用构建证据必须退出 0")
    return executable


def _check_seed_smoke(errors: List[str], seed: Mapping[str, Any], run_dir: Path) -> None:
    """校验 seed smoke 的退出码、seed 值、日志和 checkpoint 绑定。"""
    smoke = seed.get("seed_smoke")
    if not isinstance(smoke, list) or len(smoke) < 3:
        _error(errors, "seed.seed_smoke", "至少需要三条 seed smoke 记录")
        return
    seeds: List[int] = []
    checkpoint_hashes: List[str] = []
    for index, item in enumerate(smoke):
        field = f"seed.seed_smoke[{index}]"
        if not isinstance(item, Mapping):
            _error(errors, field, "必须是对象")
            continue
        value = item.get("seed")
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 0xFFFFFFFF:
            _error(errors, f"{field}.seed", "必须是非负 32 位整数")
        else:
            seeds.append(value)
        if item.get("command_exit_code") != 0:
            _error(errors, f"{field}.command_exit_code", "seed smoke 必须退出 0")
        for label in ("log", "checkpoint"):
            path_value = item.get(label)
            if not isinstance(path_value, str) or not normalized(path_value).is_file():
                _error(errors, f"{field}.{label}", "文件不存在")
                continue
            path = normalized(path_value)
            if not _under(path, run_dir):
                _error(errors, f"{field}.{label}", "文件必须位于隔离 run-dir 内")
            hash_field = f"{label}_sha256"
            actual = sha256_file(path)
            _check_hash(errors, f"{field}.{hash_field}", item.get(hash_field), actual)
            if label == "checkpoint" and isinstance(item.get(hash_field), str):
                checkpoint_hashes.append(item[hash_field].lower())
    if len(set(seeds)) < 2:
        _error(errors, "seed.seed_smoke", "必须包含相同 seed 与不同 seed 的对照")
    same_seed_indices: Dict[int, List[int]] = {}
    for index, value in enumerate(seeds):
        same_seed_indices.setdefault(value, []).append(index)
    if not any(len(indices) >= 2 for indices in same_seed_indices.values()):
        _error(errors, "seed.seed_smoke", "必须包含至少两条相同 seed 记录")
    if len(set(checkpoint_hashes)) < 2:
        _error(errors, "seed.seed_smoke", "smoke checkpoint SHA 不能全部相同；不得宣称 bit-exact")


def validate_plan(plan: Mapping[str, Any]) -> Dict[str, Any]:
    """检查 D4 运行计划并返回机器可读结果。"""
    errors: List[str] = []
    warnings: List[str] = []
    pending: List[str] = []
    blocking: List[str] = []
    run_dir = normalized(str(plan.get("run_dir", "")))
    if plan.get("schema_version") != "s1-t02-d4-v1":
        _error(errors, "schema_version", "必须为 s1-t02-d4-v1")
    if not run_dir.is_dir():
        _error(errors, "run_dir", f"隔离目录不存在: {run_dir}")
    source = plan.get("source", {})
    if not isinstance(source, Mapping):
        _error(errors, "source", "必须是对象")
        source = {}
    source_repo = normalized(str(source.get("repository", "")))
    if not source_repo.is_dir():
        _error(errors, "source.repository", f"官方源目录不存在: {source_repo}")
    commit = source.get("commit_observed")
    if not isinstance(commit, str) or not COMMIT_PATTERN.fullmatch(commit):
        _error(errors, "source.commit_observed", "必须是现场取得的完整 40 位 commit")
    if source.get("diff_exit_code") != 0:
        _error(errors, "source.diff_exit_code", "官方源必须 git diff --quiet 退出 0")
    probe = source.get("probe", {})
    if not isinstance(probe, Mapping) or probe.get("network_access") is not False:
        _error(errors, "source.probe.network_access", "必须记录 network_access=false")
    if source_repo.is_dir():
        _check_source(errors, source, run_dir, source_repo)
    build = plan.get("build", {})
    if not isinstance(build, Mapping):
        _error(errors, "build", "必须是对象")
        build = {}
    patched_repo = normalized(str(source.get("patched_repository", "")))
    executable = _check_build(errors, build, patched_repo, run_dir)
    seed = plan.get("seed", {})
    if not isinstance(seed, Mapping):
        _error(errors, "seed", "必须是对象")
        seed = {}
    seed_status = seed.get("status")
    if seed_status not in ALLOWED_SEED_STATUS:
        _error(errors, "seed.status", f"必须是 {sorted(ALLOWED_SEED_STATUS)} 之一")
    elif seed_status != "READY":
        blocking.append(f"fixed_seed:{seed_status}:{seed.get('reason', '未提供原因')}")
    if seed_status == "READY":
        patch_path = seed.get("patch_path")
        if not isinstance(patch_path, str) or not normalized(patch_path).is_file():
            _error(errors, "seed.patch_path", "READY 时必须存在隔离 patch")
        _check_hash(errors, "seed.patch_sha256", seed.get("patch_sha256"), sha256_file(normalized(patch_path)) if isinstance(patch_path, str) and normalized(patch_path).is_file() else None)
        if seed.get("bit_exact") is not False:
            _error(errors, "seed.bit_exact", "必须明确为 false，避免过度宣称")
        _check_seed_smoke(errors, seed, run_dir)
    else:
        pending.append("fixed_seed_support")
    data = plan.get("data", {})
    if not isinstance(data, Mapping):
        _error(errors, "data", "必须是对象")
        data = {}
    expected_counts = {"train": data.get("train_count"), "valid": data.get("valid_count")}
    for key in ("names", "train_list", "valid_list", "manifest"):
        path_value = data.get(f"{key}_path")
        if not isinstance(path_value, str) or not normalized(path_value).is_file():
            _error(errors, f"data.{key}_path", "绑定文件不存在")
        _check_hash(errors, f"data.{key}_sha256", data.get(f"{key}_sha256"), sha256_file(normalized(path_value)) if isinstance(path_value, str) and normalized(path_value).is_file() else None)
    if data.get("train_count") != 118001:
        _error(errors, "data.train_count", "必须绑定当前 train.list 118001 行")
    if data.get("valid_count") != 15195:
        _error(errors, "data.valid_count", "必须绑定当前 valid.list 15195 行")
    _check_preprocessing(errors, plan)
    bindings = plan.get("file_bindings")
    binding_by_name: Dict[str, Mapping[str, Any]] = {}
    if not isinstance(bindings, list) or not bindings:
        _error(errors, "file_bindings", "必须提供非空文件绑定数组")
    else:
        binding_names = set()
        for binding in bindings:
            if not isinstance(binding, Mapping):
                _error(errors, "file_bindings", "每项必须是对象")
            else:
                name = binding.get("name")
                if not isinstance(name, str) or not name:
                    _error(errors, "file_bindings.name", "绑定名称不能为空")
                elif name in binding_names:
                    _error(errors, f"file_bindings.{name}", "绑定名称重复")
                else:
                    binding_names.add(name)
                    binding_by_name[name] = binding
                _check_binding(errors, binding, run_dir, required=binding.get("required", True) is not False)
        required_binding_names = {
            "executable", "seed_patch", "source_archive", "configure_log", "build_log",
            "names", "train_list", "valid_list", "manifest", "tiny_weight",
            "tiny320_cfg", "tiny416_cfg", "full_cfg", "tiny320_data", "tiny416_data", "full_data",
            "pilot_cfg", "pilot_data", "pilot_log",
            "seed_smoke_a_log", "seed_smoke_b_log", "seed_smoke_c_log",
            "seed_smoke_a_checkpoint", "seed_smoke_b_checkpoint", "seed_smoke_c_checkpoint",
        }
        for name in sorted(required_binding_names - binding_names):
            _error(errors, "file_bindings", f"缺少必需绑定: {name}")
    models = plan.get("models")
    if not isinstance(models, Mapping) or set(models) != set(EXPECTED_MODELS):
        _error(errors, "models", "必须恰好包含 tiny320、tiny416、full")
        models = models if isinstance(models, Mapping) else {}
    for model_id, expected in EXPECTED_MODELS.items():
        model = models.get(model_id)
        if not isinstance(model, Mapping):
            _error(errors, f"models.{model_id}", "模型计划缺失")
            continue
        if model.get("model_id") != model_id:
            _error(errors, f"models.{model_id}.model_id", "model_id 必须与键一致")
        if model.get("role") != expected["role"]:
            _error(errors, f"models.{model_id}.role", f"必须为 {expected['role']}")
        _check_cfg(errors, model_id, model, run_dir)
        _check_data_cfg(errors, model_id, model, run_dir, expected_counts)
        weight = model.get("initial_weight", {})
        if not isinstance(weight, Mapping):
            _error(errors, f"models.{model_id}.initial_weight", "必须是对象")
        else:
            weight_path = weight.get("path")
            weight_status = weight.get("status")
            exists = isinstance(weight_path, str) and normalized(weight_path).is_file()
            if not exists:
                if model_id == "full" and weight_status in {"PENDING", "BLOCKED"}:
                    pending.append(f"{model_id}.initial_weight")
                else:
                    _error(errors, f"models.{model_id}.initial_weight", "初始权重不存在")
            else:
                _check_hash(errors, f"models.{model_id}.initial_weight.sha256", weight.get("sha256"), sha256_file(normalized(weight_path)))
        weight_path_for_command = weight.get("path") if isinstance(weight, Mapping) else None
        _check_command(
            errors,
            model_id,
            model.get("command"),
            executable,
            model.get("data_config_path"),
            model.get("config_path"),
            weight_path_for_command,
        )
    pilot = plan.get("pilot", {})
    if not isinstance(pilot, Mapping):
        _error(errors, "pilot", "必须是对象")
        pilot = {}
    pilot_status = pilot.get("status")
    if pilot_status not in ALLOWED_PILOT_STATUS:
        _error(errors, "pilot.status", f"必须是 {sorted(ALLOWED_PILOT_STATUS)} 之一")
    if pilot_status == "NOT_EXECUTED":
        pending.append("tiny416_pilot")
    elif pilot_status == "BLOCKED":
        blocking.append(f"tiny416_pilot:{pilot.get('reason', '未提供原因')}")
    if pilot_status == "COMPLETED":
        if pilot.get("model_id") != "tiny416" or pilot.get("updates", 0) > 100 or pilot.get("exit_code") != 0:
            _error(errors, "pilot", "完成 pilot 必须是 tiny416、更新不超过100且退出码0")
    _check_plan_binding(
        errors, binding_by_name, "executable", build.get("executable_path"), build.get("executable_sha256")
    )
    _check_plan_binding(
        errors,
        binding_by_name,
        "seed_patch",
        seed.get("patch_path"),
        seed.get("patch_sha256"),
    )
    _check_plan_binding(
        errors,
        binding_by_name,
        "source_archive",
        source.get("source_archive"),
        source.get("source_archive_sha256"),
    )
    for label in ("configure_log", "build_log"):
        _check_plan_binding(errors, binding_by_name, label, build.get(label), build.get(f"{label}_sha256"))
    for key in ("names", "train_list", "valid_list", "manifest"):
        _check_plan_binding(
            errors,
            binding_by_name,
            key,
            data.get(f"{key}_path"),
            data.get(f"{key}_sha256"),
        )
    for model_id, model in models.items():
        if not isinstance(model, Mapping) or model_id not in EXPECTED_MODELS:
            continue
        _check_plan_binding(
            errors,
            binding_by_name,
            f"{model_id}_cfg",
            model.get("config_path"),
            model.get("config_sha256"),
        )
        _check_plan_binding(
            errors,
            binding_by_name,
            f"{model_id}_data",
            model.get("data_config_path"),
            model.get("data_config_sha256"),
        )
        weight = model.get("initial_weight")
        if isinstance(weight, Mapping) and weight.get("status") == "READY":
            _check_plan_binding(
                errors,
                binding_by_name,
                "tiny_weight",
                weight.get("path"),
                weight.get("sha256"),
            )
    _check_plan_binding(
        errors, binding_by_name, "pilot_cfg", pilot.get("config_path"), pilot.get("config_sha256")
    )
    _check_plan_binding(
        errors, binding_by_name, "pilot_data", pilot.get("data_config_path"), pilot.get("data_config_sha256")
    )
    _check_plan_binding(
        errors, binding_by_name, "pilot_log", pilot.get("combined_log"), pilot.get("combined_log_sha256")
    )
    seed_smoke = seed.get("seed_smoke")
    if isinstance(seed_smoke, list):
        for item in seed_smoke:
            if not isinstance(item, Mapping):
                continue
            name = item.get("name")
            if not isinstance(name, str):
                continue
            suffix = name.removeprefix("seed_")
            _check_plan_binding(
                errors,
                binding_by_name,
                f"seed_smoke_{suffix}_log",
                item.get("log"),
                item.get("log_sha256"),
            )
            _check_plan_binding(
                errors,
                binding_by_name,
                f"seed_smoke_{suffix}_checkpoint",
                item.get("checkpoint"),
                item.get("checkpoint_sha256"),
            )
    formal_eval = plan.get("formal_evaluation", {})
    if not isinstance(formal_eval, Mapping) or formal_eval.get("status") != "NOT_EXECUTED":
        _error(errors, "formal_evaluation.status", "D4 必须标记正式 test 未执行")
    if not source.get("patch_applied", False):
        blocking.append("seed_patch_not_applied")
    status = "BLOCKED" if errors or blocking else ("PENDING" if pending else "READY_FOR_PILOT")
    return {
        "schema_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "pending": pending,
        "blocking_reasons": blocking,
        "status": status,
    }


def make_report(plan_path: Path, report_path: Path, summary_path: Path) -> Dict[str, Any]:
    """从不可覆盖的计划文件生成独立机器报告和中文摘要。"""
    if normalized(plan_path) == normalized(report_path):
        raise ValueError("--input 与 --report 不能是同一路径")
    if normalized(plan_path) == normalized(summary_path):
        raise ValueError("--input 与 --summary 不能是同一路径")
    if normalized(report_path) == normalized(summary_path):
        raise ValueError("--report 与 --summary 不能是同一路径")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    validation = validate_plan(plan)
    report = {
        "schema_version": "s1-t02-d4-report-v1",
        "task": "S1-T02-D4",
        "generated_utc8": utc8_now(),
        "input_plan": str(normalized(plan_path)),
        "input_plan_sha256": sha256_file(plan_path),
        "validation": validation,
        "plan": plan,
        "execution": {
            "network_access": False,
            "checker_argv": sys.argv,
            "checker_cwd": str(Path.cwd().resolve()),
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_sha = sha256_file(report_path)
    summary = "\n".join(
        [
            "# S1-T02-D4 官方 Darknet 浮点基线预检摘要",
            "",
            f"- 生成时间（UTC+8）：{report['generated_utc8']}",
            f"- 计划：`{normalized(plan_path)}`，SHA-256 `{report['input_plan_sha256']}`",
            f"- 机器报告：`{normalized(report_path)}`，SHA-256 `{report_sha}`",
            f"- 状态：`{validation['status']}`；schema_valid={validation['schema_valid']}；errors={len(validation['errors'])}",
            f"- pending：{', '.join(validation['pending']) if validation['pending'] else '无'}",
            f"- 阻断：{'; '.join(validation['blocking_reasons']) if validation['blocking_reasons'] else '无'}",
            "",
            "## 语义边界",
            "",
            "本证据绑定三种浮点模型的配置、数据、官方 Darknet 命令位置、版本和输入输出计划。官方源基线训练 RNG 使用 `time(0)` 且没有 CLI seed 参数；隔离 seeded 副本已应用 `GESTUREFORGE_DARKNET_SEED` patch 并完成构建/seed smoke，固定 seed 不等于 bit-exact。",
            "正式 test、robustness、mAP、最终精度、INT8 整网、Vivado 综合、烧录和板上测量均未执行；tiny320/full pilot 未启动。tiny416 pilot 已启动但 8/100 后以 `0xC000013A` 中止且未生成 checkpoint，保持 BLOCKED。full 缺少 `yolov4.conv.137` 时保持 PENDING，不下载、不伪造。",
            "",
            "## 复现入口",
            "",
            f"`py verification/s1_t02_d4_float_baseline.py validate --input \"{normalized(plan_path)}\" --report \"{normalized(report_path)}\" --summary \"{normalized(summary_path)}\"`",
            "",
            "检查器会拒绝输入和输出同路径；所有路径比较使用规范化解析结果；本报告只记录 pilot，不会自动启动训练。",
            "",
        ]
    )
    summary_path.write_text(summary, encoding="utf-8")
    return report


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="S1-T02-D4 官方 Darknet 浮点基线绑定与预检")
    subparsers = parser.add_subparsers(dest="action", required=True)
    validate = subparsers.add_parser("validate", help="读取运行计划并生成独立报告")
    validate.add_argument("--input", required=True, type=Path, help="不可覆盖的运行计划 JSON")
    validate.add_argument("--report", required=True, type=Path, help="独立机器报告输出 JSON")
    validate.add_argument("--summary", required=True, type=Path, help="中文摘要输出 Markdown")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    try:
        if args.action == "validate":
            report = make_report(args.input, args.report, args.summary)
            return 0 if report["validation"]["schema_valid"] else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"D4_ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
