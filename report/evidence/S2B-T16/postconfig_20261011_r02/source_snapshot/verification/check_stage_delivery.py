#!/usr/bin/env python3
"""只读核验阶段输入清单和单次运行证据目录。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
MAX_EVIDENCE_FILES = 10000
SIZE_WARNING_BYTES = 1_000_000_000
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
SHA256_RE = re.compile(r"[0-9a-fA-F]{64}\Z")
TASK_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
ROLES = {"source", "input", "result", "log", "diagnostic", "artifact"}
STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}
BASE_FIELDS = {
    "schema_version",
    "stage",
    "task_id",
    "run_id",
    "source_commit",
    "evidence_dir",
    "interfaces",
    "files",
    "checks",
    "limitations",
}
TOP_LEVEL_FIELDS = BASE_FIELDS | {"tool_versions", "interfaces_not_applicable_reason"}
INTERFACE_FIELDS = {"name", "version", "frozen", "path", "sha256"}
FILE_FIELDS = {"path", "sha256", "role", "keep_reason"}
CHECK_FIELDS = {"name", "status", "command", "exit_code", "reason"}
CACHE_DIR_NAMES = {
    "build",
    "obj_dir",
    ".xil",
    ".runs",
    ".cache",
    ".gen",
    ".srcs",
    ".sim",
    ".hw",
    "ip_user_files",
    "sim_1",
    "synth_1",
    "impl_1",
}
CACHE_SUFFIXES = {".gch", ".o", ".obj"}
PRESERVED_DIAGNOSTIC_SUFFIXES = {
    ".wdb",
    ".vcd",
    ".vcd.gz",
    ".dcp",
    ".wlf",
    ".fsdb",
}
SCOPE_STATEMENT = "检查结果不代表 G0/G4/G5 或实物验收。"
PLACEHOLDERS = {
    "",
    "todo",
    "tbd",
    "pending",
    "unfrozen",
    "not frozen",
    "placeholder",
    "unknown",
    "none",
    "null",
    "n/a",
    "na",
    "not applicable",
    "待填写",
    "待补",
    "待冻结",
    "待确认",
    "待定",
    "未冻结",
    "未填写",
    "占位",
    "不适用",
    "runid",
    "s2b-txx",
}
PLACEHOLDER_KEYS = {
    re.sub(r"[\W_]+", "", value.casefold())
    for value in PLACEHOLDERS
}


class UsageError(ValueError):
    """命令行参数错误。"""


class DuplicateKeyError(ValueError):
    """JSON 对象含重复键。"""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageError(message)


def is_placeholder(value: str) -> bool:
    trimmed = value.strip().casefold()
    normalized = re.sub(r"[\W_]+", "", value.casefold())
    return (
        normalized in PLACEHOLDER_KEYS
        or (trimmed.startswith("<") and trimmed.endswith(">"))
        or bool(re.fullmatch(r"x{2,}|t?xx", normalized))
    )


def is_valid_explanatory_reason(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and not is_placeholder(value)
    )


def is_reparse_or_symlink(info: os.stat_result) -> bool:
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    attributes = getattr(info, "st_file_attributes", 0)
    return stat.S_ISLNK(info.st_mode) or bool(attributes & reparse_flag)


def path_cache_reason(relative_path: str, leaf_is_directory: bool = False) -> str | None:
    parts = PurePosixPath(relative_path.replace("\\", "/")).parts
    directory_parts = parts if leaf_is_directory else parts[:-1]
    for part in directory_parts:
        folded = part.casefold()
        if folded in CACHE_DIR_NAMES or folded.endswith(
            (".runs", ".cache", ".gen", ".srcs", ".sim", ".hw")
        ):
            return f"路径包含生成缓存/工程目录：{part}"
    if not leaf_is_directory and parts:
        suffix = Path(parts[-1]).suffix.casefold()
        if suffix in CACHE_SUFFIXES:
            return f"禁止收录编译缓存文件：{parts[-1]}"
    return None


def preserved_diagnostic_suffix(path_text: str) -> str | None:
    folded = path_text.casefold()
    return next(
        (
            suffix
            for suffix in sorted(PRESERVED_DIAGNOSTIC_SUFFIXES, key=len, reverse=True)
            if folded.endswith(suffix)
        ),
        None,
    )


def _check_absolute_path(path: Path, expected_kind: str, errors: list[str], label: str) -> Path | None:
    if not path.is_absolute():
        errors.append(f"{label}必须是绝对路径")
        return None
    anchor = Path(path.anchor)
    current = anchor
    try:
        info = os.lstat(current)
    except OSError as exc:
        errors.append(f"{label}路径不可访问：{exc}")
        return None
    if is_reparse_or_symlink(info):
        errors.append(f"{label}路径包含符号链接或 reparse 点：{current}")
        return None
    remainder = path.parts[len(anchor.parts) :]
    for index, component in enumerate(remainder):
        try:
            with os.scandir(current) as entries:
                exact_name_exists = any(entry.name == component for entry in entries)
        except OSError as exc:
            errors.append(f"{label}父目录不可访问：{current}：{exc}")
            return None
        if not exact_name_exists:
            errors.append(f"{label}路径分量不存在或大小写不精确：{current / component}")
            return None
        current = current / component
        try:
            info = os.lstat(current)
        except OSError as exc:
            errors.append(f"{label}路径不可访问：{current}：{exc}")
            return None
        if is_reparse_or_symlink(info):
            errors.append(f"{label}路径包含符号链接或 reparse 点：{current}")
            return None
        if index < len(remainder) - 1 and not stat.S_ISDIR(info.st_mode):
            errors.append(f"{label}父路径不是普通目录：{current}")
            return None
    if expected_kind == "directory" and not stat.S_ISDIR(info.st_mode):
        errors.append(f"{label}不是目录：{current}")
        return None
    if expected_kind == "file" and not stat.S_ISREG(info.st_mode):
        errors.append(f"{label}不是普通文件：{current}")
        return None
    return current


def resolve_project_root(raw_root: str | None, errors: list[str]) -> Path | None:
    if raw_root is None:
        requested = Path(__file__).absolute().parent.parent
    else:
        if not isinstance(raw_root, str) or not raw_root or raw_root != raw_root.strip():
            errors.append("project-root 必须是非空、无首尾空白的路径")
            return None
        if "\x00" in raw_root:
            errors.append("project-root 含非法 NUL 字符")
            return None
        if any(
            part in {".", ".."}
            for part in raw_root.replace("\\", "/").split("/")
        ):
            errors.append("project-root 不得包含 . 或 .. 路径分量")
            return None
        requested = Path(raw_root)
        if requested.drive and not requested.is_absolute():
            errors.append("project-root 不能使用盘符相对路径")
            return None
        if not requested.is_absolute():
            requested = Path.cwd() / requested
    requested = Path(os.path.abspath(os.fspath(requested)))
    root = _check_absolute_path(requested, "directory", errors, "project-root")
    if root is None:
        return None
    try:
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        errors.append(f"无法只读核验 Git 仓库根目录：{exc}")
        return None
    if git_root.returncode != 0:
        errors.append("project-root 不是可核验的 Git 仓库根目录")
        return None
    reported_root = Path(os.path.abspath(git_root.stdout.strip()))
    if os.path.normcase(os.fspath(reported_root)) != os.path.normcase(os.fspath(root)):
        errors.append("project-root 必须精确指向 Git 仓库根目录")
        return None
    return root


def resolve_repo_path(
    root: Path,
    raw_path: Any,
    label: str,
    expected_kind: str,
    errors: list[str],
) -> tuple[Path, str] | None:
    if not isinstance(raw_path, str) or not raw_path or raw_path != raw_path.strip():
        errors.append(f"{label}必须是非空、无首尾空白的路径字符串")
        return None
    if "\x00" in raw_path or raw_path.startswith(("\\\\?\\", "//?/")):
        errors.append(f"{label}含不支持的路径字符或设备路径")
        return None
    textual_parts = raw_path.replace("\\", "/").split("/")
    if any(part in {".", ".."} for part in textual_parts):
        errors.append(f"{label}不得包含 . 或 .. 路径分量")
        return None
    candidate = Path(raw_path)
    if candidate.drive and not candidate.is_absolute():
        errors.append(f"{label}不能使用盘符相对路径")
        return None
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = Path(os.path.abspath(os.fspath(candidate)))
    try:
        common = os.path.commonpath((os.fspath(root), os.fspath(candidate)))
    except ValueError:
        errors.append(f"{label}越出 project-root")
        return None
    if os.path.normcase(common) != os.path.normcase(os.fspath(root)):
        errors.append(f"{label}越出 project-root")
        return None
    relative = Path(os.path.relpath(os.fspath(candidate), os.fspath(root)))
    if relative == Path(".") or any(part in {"", ".", ".."} for part in relative.parts):
        errors.append(f"{label}必须指向 project-root 内的具体文件或目录")
        return None
    current = root
    info: os.stat_result | None = None
    for index, component in enumerate(relative.parts):
        try:
            with os.scandir(current) as entries:
                exact_name_exists = any(entry.name == component for entry in entries)
        except OSError as exc:
            errors.append(f"{label}父目录不可访问：{current}：{exc}")
            return None
        if not exact_name_exists:
            errors.append(f"{label}路径分量不存在或大小写不精确：{current / component}")
            return None
        current = current / component
        try:
            info = os.lstat(current)
        except OSError as exc:
            errors.append(f"{label}路径不可访问：{current}：{exc}")
            return None
        if is_reparse_or_symlink(info):
            errors.append(f"{label}路径包含符号链接或 reparse 点：{current}")
            return None
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(info.st_mode):
            errors.append(f"{label}父路径不是普通目录：{current}")
            return None
    if info is None:
        errors.append(f"{label}路径无效")
        return None
    if expected_kind == "file" and not stat.S_ISREG(info.st_mode):
        errors.append(f"{label}不是普通文件：{current}")
        return None
    if expected_kind == "directory" and not stat.S_ISDIR(info.st_mode):
        errors.append(f"{label}不是目录：{current}")
        return None
    relative_posix = PurePosixPath(*relative.parts).as_posix()
    return current, relative_posix


def load_json_strict(path: Path) -> Any:
    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise DuplicateKeyError(f"JSON 对象含重复键：{key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"JSON 含非法常量：{value}")

    text = path.read_text(encoding="utf-8")
    return json.loads(
        text,
        object_pairs_hook=pairs_hook,
        parse_constant=reject_constant,
    )


def sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            size += len(block)
    return digest.hexdigest(), size


def verify_hash(
    path: Path,
    expected: str,
    label: str,
    errors: list[str],
    warnings: list[str],
    hash_cache: dict[str, tuple[str, int]],
) -> None:
    key = os.path.normcase(os.path.abspath(os.fspath(path)))
    try:
        actual, size = hash_cache[key] if key in hash_cache else sha256_file(path)
        hash_cache[key] = (actual, size)
    except OSError as exc:
        errors.append(f"{label}读取或哈希失败：{exc}")
        return
    if actual.casefold() != expected.casefold():
        errors.append(f"{label} SHA-256 不匹配：清单 {expected}，实际 {actual}")
    if size >= SIZE_WARNING_BYTES:
        warnings.append(
            f"{label}文件较大（{size} 字节）；此提示不是验收指标"
        )


def _required_keys(
    item: dict[str, Any],
    required: set[str],
    allowed: set[str],
    label: str,
    errors: list[str],
) -> None:
    for key in sorted(required - item.keys()):
        errors.append(f"{label}缺少字段：{key}")
    for key in sorted(item.keys() - allowed):
        errors.append(f"{label}含未知字段：{key}")


def _valid_name(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        errors.append(f"{label}必须是非空字符串")
        return False
    if is_placeholder(value):
        errors.append(f"{label}不能是占位值")
        return False
    return True


def _valid_sha256(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{label}必须是 64 位十六进制 SHA-256")
        return False
    return True


def validate_check(
    item: Any,
    index: int,
    mode: str,
    errors: list[str],
    check_statuses: list[dict[str, str]],
) -> None:
    label = f"checks[{index}]"
    if not isinstance(item, dict):
        errors.append(f"{label}必须是对象")
        return
    _required_keys(item, {"name", "status", "command", "exit_code"}, CHECK_FIELDS, label, errors)
    _valid_name(item.get("name"), f"{label}.name", errors)
    status_value = item.get("status")
    if not isinstance(status_value, str) or status_value not in STATUSES:
        errors.append(f"{label}.status 必须是 {', '.join(sorted(STATUSES))} 之一")
        return
    reason = item.get("reason")
    if reason is not None and not is_valid_explanatory_reason(reason):
        errors.append(f"{label}.reason 必须是非空、首尾无空白且非占位字符串或省略")
    command = item.get("command")
    if command is not None and not is_valid_explanatory_reason(command):
        errors.append(
            f"{label}.command 必须是非空、首尾无空白且非占位字符串或 null"
        )
    exit_code = item.get("exit_code")
    if exit_code is not None and type(exit_code) is not int:
        errors.append(f"{label}.exit_code 必须是整数或 null，布尔值不算整数")
    if status_value == "PASS":
        if not isinstance(command, str) or not command:
            errors.append(f"{label} 为 PASS 时 command 必须非空")
        if type(exit_code) is not int or exit_code != 0:
            errors.append(f"{label} 为 PASS 时 exit_code 必须严格为整数 0")
    elif status_value == "FAIL":
        if not isinstance(command, str) or not command:
            errors.append(f"{label} 为 FAIL 时必须记录命令")
        if type(exit_code) is not int or exit_code == 0:
            errors.append(f"{label} 为 FAIL 时必须记录真实非零整数退出码")
        if reason is None:
            errors.append(f"{label} 为 FAIL 时必须说明原因")
    else:
        if reason is None:
            errors.append(f"{label} 为 {status_value} 时必须说明原因")
        if exit_code is not None:
            errors.append(f"{label} 为 {status_value} 时 exit_code 必须为 null")
    summary = {"status": status_value}
    if isinstance(item.get("name"), str):
        summary["name"] = item["name"]
    if isinstance(reason, str):
        summary["reason"] = reason
    check_statuses.append(summary)
    if mode == "inputs" and status_value in {"FAIL", "BLOCKED", "NOT_RUN"}:
        errors.append(f"{label} 依赖检查状态为 {status_value}，阻断 inputs 核验")


def validate_interfaces(
    interfaces: Any,
    not_applicable_reason: Any,
    has_not_applicable_reason: bool,
    mode: str,
    root: Path,
    errors: list[str],
    warnings: list[str],
    hash_cache: dict[str, tuple[str, int]],
) -> None:
    if not isinstance(interfaces, list):
        errors.append("interfaces 必须是数组")
        return
    if not interfaces:
        if not has_not_applicable_reason:
            errors.append("interfaces 为空时必须提供 interfaces_not_applicable_reason")
        elif not is_valid_explanatory_reason(not_applicable_reason):
            errors.append(
                "interfaces_not_applicable_reason 必须是非空、首尾无空白且非占位的字符串"
            )
        return
    if has_not_applicable_reason:
        errors.append("interfaces 非空时不允许声明 interfaces_not_applicable_reason")
    for index, item in enumerate(interfaces):
        label = f"interfaces[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}必须是对象")
            continue
        _required_keys(item, INTERFACE_FIELDS, INTERFACE_FIELDS, label, errors)
        _valid_name(item.get("name"), f"{label}.name", errors)
        version = item.get("version")
        _valid_name(version, f"{label}.version", errors)
        frozen = item.get("frozen")
        if type(frozen) is not bool:
            errors.append(f"{label}.frozen 必须是布尔值")
        elif mode == "inputs" and frozen is not True:
            errors.append(f"{label} 接口未冻结，阻断 inputs 核验")
        valid_hash = _valid_sha256(item.get("sha256"), f"{label}.sha256", errors)
        resolved = resolve_repo_path(root, item.get("path"), f"{label}.path", "file", errors)
        if resolved is None:
            continue
        path, relative = resolved
        if not relative.startswith("docs/"):
            errors.append(f"{label}.path 必须引用仓库内现有 docs/ 正式文档")
        cache_error = path_cache_reason(relative)
        if cache_error:
            errors.append(f"{label}.path {cache_error}")
        if valid_hash:
            verify_hash(
                path,
                item["sha256"],
                f"{label}.path",
                errors,
                warnings,
                hash_cache,
            )


def validate_files(
    files: Any,
    mode: str,
    root: Path,
    errors: list[str],
    warnings: list[str],
    hash_cache: dict[str, tuple[str, int]],
) -> list[dict[str, Any]]:
    resolved_files: list[dict[str, Any]] = []
    if not isinstance(files, list):
        errors.append("files 必须是数组")
        return resolved_files
    seen: set[str] = set()
    input_count = 0
    source_count = 0
    output_count = 0
    for index, item in enumerate(files):
        label = f"files[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}必须是对象")
            continue
        _required_keys(item, {"path", "sha256", "role"}, FILE_FIELDS, label, errors)
        role = item.get("role")
        if not isinstance(role, str) or role not in ROLES:
            errors.append(f"{label}.role 必须是 {', '.join(sorted(ROLES))} 之一")
            role = None
        else:
            input_count += role == "input"
            source_count += role == "source"
            output_count += role in {"result", "log"}
        path_value = item.get("path")
        path_text = path_value if isinstance(path_value, str) else ""
        cache_error = path_cache_reason(path_text.replace("\\", "/"))
        if cache_error:
            errors.append(f"{label}.path {cache_error}")
        expected_hash_valid = _valid_sha256(item.get("sha256"), f"{label}.sha256", errors)
        keep_reason = item.get("keep_reason")
        if "keep_reason" in item and (
            not isinstance(keep_reason, str)
            or not keep_reason
            or keep_reason != keep_reason.strip()
            or is_placeholder(keep_reason)
        ):
            errors.append(f"{label}.keep_reason 必须是有内容的说明")
        suffix = preserved_diagnostic_suffix(path_text.replace("\\", "/"))
        if suffix is not None:
            if role not in {"diagnostic", "artifact"}:
                errors.append(
                    f"{label} 的 {suffix} 文件必须标为 diagnostic 或 artifact"
                )
            if not isinstance(keep_reason, str) or not keep_reason:
                errors.append(f"{label} 的 {suffix} 文件必须填写 keep_reason")
        resolved = resolve_repo_path(root, path_value, f"{label}.path", "file", errors)
        if resolved is None:
            continue
        path, relative = resolved
        key = os.path.normcase(os.path.normpath(relative))
        if key in seen:
            errors.append(f"{label}.path 在 files 中重复：{relative}")
        seen.add(key)
        actual_cache_error = path_cache_reason(relative)
        if actual_cache_error:
            errors.append(f"{label}.path {actual_cache_error}")
        if expected_hash_valid:
            verify_hash(
                path,
                item["sha256"],
                f"{label}.path",
                errors,
                warnings,
                hash_cache,
            )
        resolved_files.append(
            {
                "path": path,
                "relative": relative,
                "role": role,
                "keep_reason": keep_reason,
            }
        )
    if mode == "inputs" and input_count == 0:
        errors.append("inputs 模式至少需要一个 role=input 的文件")
    if mode == "evidence":
        if source_count == 0:
            errors.append("evidence 模式至少需要一个 role=source 的源码绑定")
        if output_count == 0:
            errors.append("evidence 模式至少需要一个 role=result 或 role=log 的文件")
    return resolved_files


def validate_tool_versions(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict) or not value:
        errors.append("evidence 模式必须提供非空 tool_versions 对象")
        return
    for name, version in value.items():
        _valid_name(name, "tool_versions 键", errors)
        _valid_name(version, f"tool_versions.{name}", errors)


def scan_evidence_directory(
    root: Path,
    run_dir: Path,
    manifest_path: Path,
    errors: list[str],
) -> set[str] | None:
    found: set[str] = set()
    file_count = 0
    stack = [run_dir]
    manifest_key = os.path.normcase(os.path.abspath(os.fspath(manifest_path)))
    while stack:
        directory = stack.pop()
        subdirectories: list[Path] = []
        try:
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    path = Path(entry.path)
                    relative = PurePosixPath(
                        *Path(os.path.relpath(os.fspath(path), os.fspath(root))).parts
                    ).as_posix()
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError as exc:
                        errors.append(f"运行目录条目无法读取：{path}：{exc}")
                        return None
                    if is_reparse_or_symlink(info):
                        errors.append(f"运行目录含符号链接或 reparse 点：{relative}")
                        return None
                    if stat.S_ISDIR(info.st_mode):
                        cache_error = path_cache_reason(relative, leaf_is_directory=True)
                        if cache_error:
                            errors.append(
                                f"运行目录发现生成缓存/工程目录，枚举未完成：{relative}（{cache_error}）"
                            )
                            return None
                        subdirectories.append(path)
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        errors.append(f"运行目录含非普通文件系统对象：{relative}")
                        return None
                    file_count += 1
                    if file_count > MAX_EVIDENCE_FILES:
                        errors.append(
                            f"运行目录文件枚举超过上限 {MAX_EVIDENCE_FILES}，枚举未完成"
                        )
                        return None
                    cache_error = path_cache_reason(relative)
                    if cache_error:
                        errors.append(f"运行目录含编译缓存：{relative}（{cache_error}）")
                    if os.path.normcase(os.path.abspath(os.fspath(path))) != manifest_key:
                        found.add(relative)
        except OSError as exc:
            errors.append(f"运行目录枚举失败：{directory}：{exc}")
            return None
        subdirectories.sort(key=lambda path: path.name)
        stack.extend(reversed(subdirectories))
    return found


def validate_evidence_directory(
    root: Path,
    data: dict[str, Any],
    manifest_path: Path,
    files: list[dict[str, Any]],
    evidence_dir_is_canonical: bool,
    errors: list[str],
) -> None:
    if not evidence_dir_is_canonical:
        return
    evidence_dir = data["evidence_dir"]
    resolved = resolve_repo_path(root, evidence_dir, "evidence_dir", "directory", errors)
    if resolved is None:
        return
    run_dir, run_relative = resolved
    manifest_relative = PurePosixPath(
        *Path(os.path.relpath(os.fspath(manifest_path), os.fspath(root))).parts
    ).as_posix()
    if not manifest_relative.startswith(run_relative + "/"):
        errors.append("manifest 本身必须位于对应 evidence_dir 内")
    declared_inside: set[str] = set()
    for item in files:
        relative = item["relative"]
        if relative == manifest_relative:
            errors.append("files 不得列出自身清单")
        if relative.startswith(run_relative + "/"):
            declared_inside.add(relative)
        elif item["role"] in {"result", "log", "diagnostic", "artifact"}:
            errors.append(
                f"role={item['role']} 的证据文件必须位于当前 evidence_dir：{relative}"
            )
    discovered = scan_evidence_directory(root, run_dir, manifest_path, errors)
    if discovered is None:
        return
    for relative in sorted(discovered - declared_inside):
        errors.append(f"运行目录文件未列入 files：{relative}")
    for relative in sorted(declared_inside - discovered):
        errors.append(f"files 声明的运行目录文件未被完整枚举：{relative}")


def validate_manifest(
    data: Any,
    mode: str,
    root: Path,
    manifest_path: Path,
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    errors: list[str] = []
    warnings: list[str] = []
    check_statuses: list[dict[str, str]] = []
    if not isinstance(data, dict):
        return ["清单 JSON 顶层必须是对象"], warnings, check_statuses
    _required_keys(data, BASE_FIELDS, TOP_LEVEL_FIELDS, "清单", errors)
    schema_version = data.get("schema_version")
    if type(schema_version) is not int or schema_version != SCHEMA_VERSION:
        errors.append(f"schema_version 必须是整数 {SCHEMA_VERSION}")
    for field in ("stage", "task_id", "run_id"):
        _valid_name(data.get(field), field, errors)
    for field in ("task_id", "run_id"):
        value = data.get(field)
        if isinstance(value, str) and not TASK_ID_RE.fullmatch(value):
            errors.append(f"{field} 只能包含 ASCII 字母、数字、点、下划线和连字符")
    source_commit = data.get("source_commit")
    if not isinstance(source_commit, str) or not SHA1_RE.fullmatch(source_commit):
        errors.append("source_commit 必须是 40 位小写十六进制 commit SHA")
    else:
        try:
            commit_type = subprocess.run(
                ["git", "cat-file", "-t", source_commit],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as exc:
            errors.append(f"source_commit 的只读 Git 对象核验失败：{exc}")
        else:
            if commit_type.returncode != 0 or commit_type.stdout.strip() != "commit":
                errors.append("source_commit 未解析为本地 Git commit 对象")
    evidence_dir = data.get("evidence_dir")
    evidence_dir_is_canonical = False
    if not isinstance(evidence_dir, str) or not evidence_dir:
        errors.append("evidence_dir 必须是非空仓库相对路径")
    elif isinstance(data.get("task_id"), str) and isinstance(data.get("run_id"), str):
        expected = f"report/evidence/{data['task_id']}/{data['run_id']}"
        if evidence_dir != expected:
            errors.append(f"evidence_dir 必须精确等于 {expected}")
        else:
            evidence_dir_is_canonical = True
    interfaces = data.get("interfaces")
    files = data.get("files")
    checks = data.get("checks")
    limitations = data.get("limitations")
    hash_cache: dict[str, tuple[str, int]] = {}
    validate_interfaces(
        interfaces,
        data.get("interfaces_not_applicable_reason"),
        "interfaces_not_applicable_reason" in data,
        mode,
        root,
        errors,
        warnings,
        hash_cache,
    )
    resolved_files = validate_files(files, mode, root, errors, warnings, hash_cache)
    if not isinstance(checks, list):
        errors.append("checks 必须是数组")
    elif not checks:
        errors.append("checks 不能为空")
    else:
        for index, item in enumerate(checks):
            validate_check(item, index, mode, errors, check_statuses)
    if not isinstance(limitations, list):
        errors.append("limitations 必须是字符串数组")
    else:
        for index, limitation in enumerate(limitations):
            if not is_valid_explanatory_reason(limitation):
                errors.append(
                    f"limitations[{index}] 必须是非空、首尾无空白且非占位字符串"
                )
    if mode == "evidence":
        validate_tool_versions(data.get("tool_versions"), errors)
        validate_evidence_directory(
            root,
            data,
            manifest_path,
            resolved_files,
            evidence_dir_is_canonical,
            errors,
        )
    elif "tool_versions" in data:
        validate_tool_versions(data["tool_versions"], errors)
    return errors, warnings, check_statuses


def check_manifest(mode: str, manifest_arg: str, project_root_arg: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    check_statuses: list[dict[str, str]] = []
    result: dict[str, Any] = {
        "status": "CHECKS_FAILED",
        "mode": mode,
        "task_id": None,
        "run_id": None,
        "interfaces_not_applicable": None,
        "check_statuses": check_statuses,
        "errors": errors,
        "warnings": warnings,
        "scope_statement": SCOPE_STATEMENT,
    }
    if mode not in {"inputs", "evidence"}:
        errors.append("mode 必须是 inputs 或 evidence")
        return result
    root = resolve_project_root(project_root_arg, errors)
    if root is None:
        return result
    resolved_manifest = resolve_repo_path(
        root,
        manifest_arg,
        "manifest",
        "file",
        errors,
    )
    if resolved_manifest is None:
        return result
    manifest_path, _ = resolved_manifest
    try:
        data = load_json_strict(manifest_path)
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
        RecursionError,
    ) as exc:
        errors.append(f"清单 JSON 读取或解析失败：{exc}")
        return result
    if isinstance(data, dict):
        if isinstance(data.get("task_id"), str):
            result["task_id"] = data["task_id"]
        if isinstance(data.get("run_id"), str):
            result["run_id"] = data["run_id"]
        if (
            isinstance(data.get("interfaces"), list)
            and not data["interfaces"]
            and is_valid_explanatory_reason(data.get("interfaces_not_applicable_reason"))
        ):
            result["interfaces_not_applicable"] = {
                "status": "NOT_APPLICABLE",
                "reason": data["interfaces_not_applicable_reason"],
                "review_note": "其适用性仍须正式G0/Reviewer确认",
            }
    validation_errors, validation_warnings, statuses = validate_manifest(
        data,
        mode,
        root,
        manifest_path,
    )
    errors.extend(validation_errors)
    warnings.extend(validation_warnings)
    check_statuses.extend(statuses)
    if not errors:
        result["status"] = "CHECKS_OK"
    return result


def build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        prog="check_stage_delivery.py",
        add_help=False,
        allow_abbrev=False,
        description="只读核验阶段输入清单或单次运行证据目录",
    )
    parser.add_argument("--mode", choices=("inputs", "evidence"), required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--project-root")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        arguments = build_parser().parse_args(argv)
        result = check_manifest(
            arguments.mode,
            arguments.manifest,
            arguments.project_root,
        )
    except UsageError as exc:
        result = {
            "status": "CHECKS_FAILED",
            "mode": None,
            "task_id": None,
            "run_id": None,
            "check_statuses": [],
            "errors": [f"命令行参数错误：{exc}"],
            "warnings": [],
            "scope_statement": SCOPE_STATEMENT,
        }
    except Exception as exc:
        result = {
            "status": "CHECKS_FAILED",
            "mode": None,
            "task_id": None,
            "run_id": None,
            "check_statuses": [],
            "errors": [f"检查器未能完成核验：{type(exc).__name__}: {exc}"],
            "warnings": [],
            "scope_statement": SCOPE_STATEMENT,
        }
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0 if result["status"] == "CHECKS_OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
