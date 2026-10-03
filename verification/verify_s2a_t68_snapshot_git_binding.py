#!/usr/bin/env python3
"""逐样本核验 T68 编译源快照与冻结 Git tree 的对应关系。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "report/evidence/S2A-T68/static_source_closure_20261003.json"
MANIFEST_SHA256 = "c42e2b2bb420239e4988b95bbe241476d1be89fe798079b8fa5136b42daf8f49"
BASELINE_COMMIT = "ff3d00245da9c28097f2f4c130469b5cb278b53a"
BASELINE_TREE = "f6799d6b06141cef20090d8d75311a7417fa29cf"
SAMPLE_COUNT = 109
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SAMPLE_DIRECTORY_PATTERN = re.compile(r"^sample_([0-9]{3})$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
GIT_BLOB_PATTERN = re.compile(r"^[0-9a-f]{40}$")

COMPILE_SOURCE_PATHS = (
    "src/s2a_network_descriptor_pkg.sv",
    "src/int8_maxpool_geometry.sv",
    "src/int8_maxpool_window.sv",
    "src/int8_route_query.sv",
    "src/int8_upsample_query.sv",
    "src/s2a_conv_tile_engine.sv",
    "src/s2a_maxpool_engine.sv",
    "src/s2a_route_engine.sv",
    "src/s2a_upsample_engine.sv",
    "src/s2a_network_backend.sv",
    "sim/tb_s2a_network_backend_golden.sv",
)
COMPILE_TOOLING_PATHS = (
    "verification/run_s2a_network_backend_verilator.ps1",
    "verification/prepare_s2a_network_backend_golden.py",
    "verification/verify_s2a_network_backend_golden.py",
)
COMPILED_SOURCE_SCHEMA = "gestureforge_s2a_t68_compile_source_snapshot_v1"
COMPILE_RECORD_SCHEMA = "gestureforge_s2a_t68_compile_execution_v1"
SIMULATION_RECORD_SCHEMA = "gestureforge_s2a_t68_simulation_execution_v1"
REPORT_STATUS = "PASS_109_SOURCE_SNAPSHOT_TO_GIT_TREE"
TASK_ID = "S2A-T68"
TOP_MODULE = "tb_s2a_network_backend_golden"
VERILATOR_PATH = r"D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe"
ABI_CFLAGS = "-D_GLIBCXX_USE_CXX11_ABI=0"


class SnapshotBindingError(ValueError):
    """表示 T68 快照、执行记录或冻结 Git 源闭包绑定失败。"""


def require(condition: bool, message: str) -> None:
    """在固定契约不满足时停止验证。"""
    if not condition:
        raise SnapshotBindingError(message)


def sha256_bytes(value: bytes) -> str:
    """计算字节串的 SHA-256。"""
    return hashlib.sha256(value).hexdigest()


def _canonical_absolute_path(value: str | Path) -> str:
    """生成不跟随符号链接的本机绝对路径比较键。"""
    return os.path.normcase(os.path.normpath(os.path.abspath(os.fspath(value))))


def _require_plain_directory(path: Path, label: str) -> Path:
    """拒绝目录路径中的符号链接、缺失目录和越界解析。"""
    absolute = Path(os.path.abspath(path))
    require(absolute.is_dir() and not absolute.is_symlink(), f"{label} 缺失或不是普通目录：{absolute}")
    try:
        resolved = absolute.resolve(strict=True)
    except OSError as error:
        raise SnapshotBindingError(f"{label} 无法解析：{absolute}") from error
    require(_canonical_absolute_path(absolute) == _canonical_absolute_path(resolved), f"{label} 路径含符号链接：{absolute}")
    return resolved


def _require_plain_file(path: Path, label: str, parent: Path) -> bytes:
    """读取位于指定目录下且无符号链接的普通文件。"""
    absolute = Path(os.path.abspath(path))
    root_key = _canonical_absolute_path(parent)
    file_key = _canonical_absolute_path(absolute)
    require(file_key.startswith(root_key + os.sep), f"{label} 越出允许目录：{absolute}")
    cursor = absolute
    while _canonical_absolute_path(cursor) != root_key:
        require(not cursor.is_symlink(), f"{label} 路径含符号链接：{cursor}")
        cursor = cursor.parent
        require(cursor != cursor.parent, f"{label} 不在允许目录下：{absolute}")
    require(absolute.is_file() and not absolute.is_symlink(), f"{label} 缺失或不是普通文件：{absolute}")
    try:
        resolved = absolute.resolve(strict=True)
    except OSError as error:
        raise SnapshotBindingError(f"{label} 无法解析：{absolute}") from error
    require(_canonical_absolute_path(resolved).startswith(root_key + os.sep), f"{label} 解析后越出允许目录：{absolute}")
    return absolute.read_bytes()


def _read_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    """将 UTF-8 JSON 解码为对象。"""
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        """拒绝 JSON 对象中的重复属性。"""
        value: dict[str, Any] = {}
        for key, item in pairs:
            require(key not in value, f"{label} 含重复 JSON 字段：{key}")
            value[key] = item
        return value

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise SnapshotBindingError(f"{label} 不是有效 UTF-8 JSON") from error
    require(isinstance(value, dict), f"{label} 顶层必须是对象")
    return value


def _load_git_tree(root: Path) -> dict[str, dict[str, Any]]:
    """读取冻结 commit 的 tree，并核验其 tree id 与对象类型。"""
    try:
        tree_result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", f"{BASELINE_COMMIT}^{{tree}}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        actual_tree = tree_result.stdout.decode("ascii").strip()
        require(actual_tree == BASELINE_TREE, "冻结 commit 的 tree id 与 pinned manifest 不符")
        listing = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "-l", "-z", BASELINE_COMMIT],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        detail = getattr(error, "stderr", b"")
        if isinstance(detail, bytes):
            detail_text = detail.decode("utf-8", errors="replace").strip()
        else:
            detail_text = str(detail)
        raise SnapshotBindingError(f"无法读取冻结 Git tree：{detail_text or error}") from error

    entries: dict[str, dict[str, Any]] = {}
    for raw_row in listing.split(b"\0"):
        if not raw_row:
            continue
        metadata, separator, raw_path = raw_row.partition(b"\t")
        require(bool(separator), "git ls-tree 输出格式错误")
        try:
            mode, object_type, object_id, size_text = metadata.decode("ascii").split(" ", 3)
            path = raw_path.decode("utf-8")
        except (UnicodeError, ValueError) as error:
            raise SnapshotBindingError("git ls-tree 行无法解码") from error
        size = None if size_text == "-" else int(size_text)
        entries[path] = {"mode": mode, "type": object_type, "oid": object_id, "bytes": size}
    return entries


def load_pinned_closure(repo_root: Path = ROOT, manifest_path: Path = MANIFEST_PATH) -> dict[str, Any]:
    """核验静态闭包清单、固定源码集合及 Git baseline tree。"""
    root = _require_plain_directory(repo_root, "repository root")
    manifest = Path(os.path.abspath(manifest_path))
    require(_canonical_absolute_path(manifest) == _canonical_absolute_path(root / MANIFEST_PATH.relative_to(ROOT)), "static closure manifest 路径不符")
    require(manifest.is_file() and not manifest.is_symlink(), f"static closure manifest 缺失或类型不符：{manifest}")
    require(_canonical_absolute_path(manifest) == _canonical_absolute_path(manifest.resolve(strict=True)), "static closure manifest 路径含符号链接")
    raw_manifest = manifest.read_bytes()
    require(sha256_bytes(raw_manifest) == MANIFEST_SHA256, "static closure manifest SHA-256 与固定值不符")
    value = _read_json_bytes(raw_manifest, "static closure manifest")

    require(value.get("schema_version") == 1 and value.get("task_id") == "S2A-T68", "static closure manifest schema/task 不符")
    require(
        isinstance(value.get("repository_root"), str)
        and _canonical_absolute_path(value["repository_root"]) == _canonical_absolute_path(root),
        "static closure repository_root 与当前仓库不符",
    )
    require(value.get("baseline_commit") == BASELINE_COMMIT, "static closure baseline commit 不符")
    require(value.get("baseline_tree_sha1") == BASELINE_TREE, "static closure baseline tree 不符")
    require(value.get("source_count") == 38, "static closure source_count 不符")
    require(value.get("compiled_rtl_and_testbench_count") == len(COMPILE_SOURCE_PATHS), "static closure compile source count 不符")
    require(value.get("compile_tooling_count") == len(COMPILE_TOOLING_PATHS), "static closure compile tooling count 不符")
    rows = value.get("sources")
    require(isinstance(rows, list) and len(rows) == 38, "static closure sources 缺失或数量不符")

    sources: dict[str, dict[str, Any]] = {}
    for row in rows:
        require(isinstance(row, dict), "static closure source row 类型错误")
        path = row.get("path")
        require(isinstance(path, str) and path, "static closure source path 缺失")
        pure_path = PurePosixPath(path)
        require(not pure_path.is_absolute() and ".." not in pure_path.parts and pure_path.as_posix() == path, f"static closure path 非法：{path}")
        require(path not in sources, f"static closure source 重复：{path}")
        digest = row.get("sha256_worktree_bytes")
        blob = row.get("git_blob_sha1")
        length = row.get("bytes")
        require(isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest) is not None, f"static closure SHA-256 无效：{path}")
        require(isinstance(blob, str) and GIT_BLOB_PATTERN.fullmatch(blob) is not None, f"static closure Git blob id 无效：{path}")
        require(type(length) is int and length >= 0, f"static closure byte length 无效：{path}")
        require(row.get("matches_baseline_tree") is True, f"static closure 未标记 baseline tree 匹配：{path}")
        sources[path] = {
            "path": path,
            "sha256": digest,
            "bytes": length,
            "git_blob_sha1": blob,
            "matches_t29_frozen_binding": row.get("matches_t29_frozen_binding"),
        }

    require(set(COMPILE_SOURCE_PATHS).issubset(sources), "static closure 缺少获批编译源")
    require(set(COMPILE_TOOLING_PATHS).issubset(sources), "static closure 缺少获批编译工具源")
    git_tree = _load_git_tree(root)
    for path, row in sources.items():
        entry = git_tree.get(path)
        require(entry is not None, f"manifest source 不在冻结 Git tree：{path}")
        require(entry["type"] == "blob" and entry["mode"] in {"100644", "100755"}, f"baseline source 不是普通文件 blob：{path}")
        require(entry["oid"] == row["git_blob_sha1"], f"manifest Git blob id 不属于冻结 tree：{path}")
        require(row.get("matches_t29_frozen_binding") is True, f"manifest source 未确认 T29 pinned binding：{path}")
        try:
            revision_oid = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--verify", f"{BASELINE_COMMIT}:{path}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout.decode("ascii").strip()
            normalized_worktree_oid = subprocess.run(
                ["git", "-C", str(root), "hash-object", f"--path={path}", str(root / Path(*PurePosixPath(path).parts))],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout.decode("ascii").strip()
        except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
            detail = getattr(error, "stderr", b"")
            detail_text = detail.decode("utf-8", errors="replace").strip() if isinstance(detail, bytes) else str(detail)
            raise SnapshotBindingError(f"无法核验 Git path/blob binding {path}：{detail_text or error}") from error
        require(revision_oid == row["git_blob_sha1"], f"manifest blob id 与 baseline:path 不符：{path}")
        require(normalized_worktree_oid == row["git_blob_sha1"], f"工作树 Git-normalized blob 与冻结 baseline 不符：{path}")

    for path in COMPILE_SOURCE_PATHS + COMPILE_TOOLING_PATHS:
        row = sources[path]
        source_path = root / Path(*PurePosixPath(path).parts)
        require(source_path.is_file() and not source_path.is_symlink(), f"编译闭包工作树源缺失或类型错误：{path}")
        require(
            _canonical_absolute_path(source_path) == _canonical_absolute_path(source_path.resolve(strict=True)),
            f"编译闭包工作树源路径含符号链接：{path}",
        )
        raw_source = source_path.read_bytes()
        require(len(raw_source) == row["bytes"], f"编译闭包工作树 byte length 与 manifest 不符：{path}")
        require(sha256_bytes(raw_source) == row["sha256"], f"编译闭包工作树 SHA-256 与 manifest 不符：{path}")

    return {
        "manifest_path": manifest,
        "manifest_sha256": MANIFEST_SHA256,
        "baseline_commit": BASELINE_COMMIT,
        "baseline_tree_sha1": BASELINE_TREE,
        "sources": sources,
    }


def _binding_rows(
    rows: Any,
    expected_paths: tuple[str, ...],
    closure: dict[str, Any],
    repo_root: Path,
    label: str,
) -> dict[str, dict[str, Any]]:
    """校验记录中的路径、SHA-256、长度和精确集合。"""
    require(isinstance(rows, list) and len(rows) == len(expected_paths), f"{label}: row 数量不符")
    expected_set = set(expected_paths)
    observed: dict[str, dict[str, Any]] = {}
    expected_absolute = {
        relative: _canonical_absolute_path(repo_root / Path(*PurePosixPath(relative).parts))
        for relative in expected_paths
    }
    path_to_relative = {canonical: relative for relative, canonical in expected_absolute.items()}
    for row in rows:
        require(isinstance(row, dict), f"{label}: row 类型错误")
        value = row.get("path")
        require(isinstance(value, str) and value, f"{label}: source path 缺失")
        path = Path(value)
        require(path.is_absolute(), f"{label}: source path 必須是絕對路徑：{value}")
        key = _canonical_absolute_path(path)
        require(key in path_to_relative, f"{label}: path 不在批准集合：{value}")
        relative = path_to_relative[key]
        require(relative in expected_set and relative not in observed, f"{label}: path 重複或不批准：{value}")
        digest = row.get("sha256")
        length = row.get("bytes")
        expected = closure["sources"][relative]
        require(digest == expected["sha256"], f"{label}: SHA-256 與 Git baseline 不符：{relative}")
        require(type(length) is int and length == expected["bytes"], f"{label}: byte length 與 Git baseline 不符：{relative}")
        observed[relative] = {"path": value, "sha256": digest, "bytes": length}
    require(set(observed) == expected_set, f"{label}: path 集合缺失或多出來源")
    return observed


def _require_runner_binding(record: dict[str, Any], closure: dict[str, Any], repo_root: Path, label: str) -> None:
    """核对 execution record 的 runner path 和固定 SHA。"""
    runner_relative = COMPILE_TOOLING_PATHS[0]
    runner = closure["sources"][runner_relative]
    path_value = record.get("runner_path")
    require(isinstance(path_value, str) and Path(path_value).is_absolute(), f"{label}: runner_path 缺失或非绝对路径")
    require(
        _canonical_absolute_path(path_value) == _canonical_absolute_path(repo_root / Path(*PurePosixPath(runner_relative).parts)),
        f"{label}: runner_path 不属于批准闭包",
    )
    require(record.get("runner_sha256") == runner["sha256"], f"{label}: runner SHA 与 Git baseline 不符")


def _verify_compile_command(
    snapshot: dict[str, Any],
    compile_record: dict[str, Any],
    repo_root: Path,
    run_directory: Path,
    sample_index: int,
    closure: dict[str, Any],
) -> None:
    """核验 runner 固定的 Verilator 参数、源顺序及快照元数据。"""
    require(snapshot.get("task_id") == TASK_ID, "compile snapshot task_id 不符")
    require(snapshot.get("top_module") == TOP_MODULE, "compile snapshot top_module 不符")
    require(type(snapshot.get("source_count")) is int and snapshot.get("source_count") == len(COMPILE_SOURCE_PATHS), "compile snapshot source_count 不符")
    backend_sha = closure["sources"]["src/s2a_network_backend.sv"]["sha256"]
    require(snapshot.get("backend_sha256_expected") == backend_sha, "compile snapshot backend SHA expectation 不符")

    snapshot_verilator = snapshot.get("verilator_path")
    record_verilator = compile_record.get("verilator_path")
    require(isinstance(snapshot_verilator, str) and Path(snapshot_verilator).is_absolute(), "compile snapshot verilator_path 缺失或非绝对路径")
    require(isinstance(record_verilator, str) and Path(record_verilator).is_absolute(), "compile record verilator_path 缺失或非绝对路径")
    require(_canonical_absolute_path(snapshot_verilator) == _canonical_absolute_path(VERILATOR_PATH), "compile snapshot verilator_path 不属于批准工具链")
    require(_canonical_absolute_path(record_verilator) == _canonical_absolute_path(snapshot_verilator), "snapshot/compile verilator_path 不一致")

    command = snapshot.get("command")
    compile_command = compile_record.get("command")
    require(isinstance(command, list) and all(isinstance(item, str) for item in command), "compile snapshot command 必须是字符串 argv")
    require(isinstance(compile_command, list) and all(isinstance(item, str) for item in compile_command), "compile record command 必须是字符串 argv")
    require(compile_command and _canonical_absolute_path(compile_command[0]) == _canonical_absolute_path(snapshot_verilator), "compile argv executable 与 snapshot verilator_path 不一致")
    require(compile_command[1:] == command, "snapshot command 与 compile record argv 不一致")

    fixed_prefix = ["--binary", "--timing", "-Wno-fatal", "--top-module", TOP_MODULE, "--Mdir"]
    fixed_suffix = ["-CFLAGS", ABI_CFLAGS]
    expected_count = len(fixed_prefix) + 1 + len(fixed_suffix) + len(COMPILE_SOURCE_PATHS)
    require(len(command) == expected_count, "compile argv 参数数量不符合 runner 合同")
    require(command[: len(fixed_prefix)] == fixed_prefix, "compile argv 固定参数缺失、额外或顺序错误")
    mdir_value = command[len(fixed_prefix)]
    require(Path(mdir_value).is_absolute(), "compile argv --Mdir 值必须是绝对路径")
    require(
        _canonical_absolute_path(mdir_value) == _canonical_absolute_path(run_directory / "build"),
        "compile argv --Mdir 未绑定当前样本 build 目录",
    )
    suffix_start = len(fixed_prefix) + 1
    require(command[suffix_start : suffix_start + len(fixed_suffix)] == fixed_suffix, "compile argv ABI CFLAGS 缺失或顺序错误")
    source_operands = command[suffix_start + len(fixed_suffix) :]
    require(len(source_operands) == len(COMPILE_SOURCE_PATHS), "compile argv source operand 数量不符")
    expected_sources = [
        _canonical_absolute_path(repo_root / Path(*PurePosixPath(relative).parts))
        for relative in COMPILE_SOURCE_PATHS
    ]
    observed_sources: list[str] = []
    for operand in source_operands:
        require(Path(operand).is_absolute(), f"compile argv source operand 必须是绝对路径：{operand}")
        observed_sources.append(_canonical_absolute_path(operand))
    require(observed_sources == expected_sources, "compile argv 源路径缺失、替换或顺序不符合 runner 源清单")


def _verify_sample(
    evidence_root: Path,
    repo_root: Path,
    run_id: str,
    sample_index: int,
    closure: dict[str, Any],
) -> dict[str, Any]:
    """验证一个样本的 source snapshot 及 compile/simulation 记录绑定。"""
    sample_name = f"sample_{sample_index:03d}"
    run_directory = evidence_root / "runs" / sample_name / run_id
    runs_directory = evidence_root / "runs"
    require(run_directory.is_dir() and not run_directory.is_symlink(), f"{sample_name}: run directory 缺失或类型错误")
    require(
        _canonical_absolute_path(run_directory.resolve(strict=True)).startswith(_canonical_absolute_path(evidence_root) + os.sep),
        f"{sample_name}: run directory 解析后越出 evidence root",
    )

    snapshot_path = run_directory / "compile_source_snapshot.json"
    compile_path = run_directory / "compile_execution_record.json"
    simulation_path = run_directory / "simulation_execution_record.json"
    snapshot_raw = _require_plain_file(snapshot_path, f"{sample_name} source snapshot", runs_directory)
    compile_raw = _require_plain_file(compile_path, f"{sample_name} compile record", runs_directory)
    simulation_raw = _require_plain_file(simulation_path, f"{sample_name} simulation record", runs_directory)
    snapshot = _read_json_bytes(snapshot_raw, f"{sample_name} source snapshot")
    compile_record = _read_json_bytes(compile_raw, f"{sample_name} compile record")
    simulation_record = _read_json_bytes(simulation_raw, f"{sample_name} simulation record")

    require(snapshot.get("schema_version") == COMPILED_SOURCE_SCHEMA, f"{sample_name}: snapshot schema 不符")
    require(compile_record.get("schema_version") == COMPILE_RECORD_SCHEMA, f"{sample_name}: compile record schema 不符")
    require(simulation_record.get("schema_version") == SIMULATION_RECORD_SCHEMA, f"{sample_name}: simulation record schema 不符")
    for label, record in (("snapshot", snapshot), ("compile", compile_record), ("simulation", simulation_record)):
        require(type(record.get("sample_index")) is int and record.get("sample_index") == sample_index, f"{sample_name}: {label} sample_index 不符")
        require(record.get("run_id") == run_id, f"{sample_name}: {label} run_id 不符")
    require(snapshot.get("simulator_started") is False, f"{sample_name}: snapshot 不应标记 simulator 已启动")
    require(compile_record.get("simulator_started") is False, f"{sample_name}: compile record 不应标记 simulator 已启动")
    require(compile_record.get("source_unchanged") is True, f"{sample_name}: compile 期间 source 发生变化或未证明稳定")
    require(compile_record.get("tooling_sources_unchanged") is True, f"{sample_name}: compile 期间 tooling source 发生变化或未证明稳定")
    require(compile_record.get("exit_code") == 0 and compile_record.get("native_exit_code") == 0, f"{sample_name}: compile execution 未成功")
    require(compile_record.get("compile_accepted") is True and compile_record.get("launch_error") == "", f"{sample_name}: compile 接受标记或启动状态不符")
    require(compile_record.get("warning_gate") == "-Wno-fatal", f"{sample_name}: compile warning gate 不符")
    require(type(compile_record.get("warning_count")) is int and compile_record["warning_count"] >= 0, f"{sample_name}: compile warning_count 无效")
    require(compile_record.get("error_count") == 0 and compile_record.get("warning_text_retained") is True, f"{sample_name}: compile error/warning evidence 状态不符")

    snapshot_sources = _binding_rows(snapshot.get("sources"), COMPILE_SOURCE_PATHS, closure, repo_root, f"{sample_name} snapshot sources")
    compile_sources = _binding_rows(compile_record.get("sources_after"), COMPILE_SOURCE_PATHS, closure, repo_root, f"{sample_name} compile sources_after")
    require(snapshot_sources == compile_sources, f"{sample_name}: snapshot 和 compile sources_after 不一致")
    require(tuple(snapshot_sources) == COMPILE_SOURCE_PATHS and tuple(compile_sources) == COMPILE_SOURCE_PATHS, f"{sample_name}: compiled source row 顺序不符合 runner 源清单")
    snapshot_tools = _binding_rows(snapshot.get("tooling_sources"), COMPILE_TOOLING_PATHS, closure, repo_root, f"{sample_name} snapshot tooling")
    compile_tools = _binding_rows(compile_record.get("tooling_sources"), COMPILE_TOOLING_PATHS, closure, repo_root, f"{sample_name} compile tooling")
    compile_tools_after = _binding_rows(compile_record.get("tooling_sources_after"), COMPILE_TOOLING_PATHS, closure, repo_root, f"{sample_name} compile tooling_sources_after")
    simulation_tools = _binding_rows(simulation_record.get("tooling_sources"), COMPILE_TOOLING_PATHS, closure, repo_root, f"{sample_name} simulation tooling")
    require(tuple(snapshot_tools) == COMPILE_TOOLING_PATHS, f"{sample_name}: tooling source row 顺序不符合 runner 源清单")
    require(snapshot_tools == compile_tools == compile_tools_after == simulation_tools, f"{sample_name}: snapshot/compile/post-compile/simulation tooling 不一致")

    command = compile_record.get("command")
    require(isinstance(command, list) and command, f"{sample_name}: compile argv 缺失")
    _verify_compile_command(snapshot, compile_record, repo_root, run_directory, sample_index, closure)
    require(compile_record.get("backend_sha256_expected") == snapshot.get("backend_sha256_expected"), f"{sample_name}: snapshot/compile backend SHA expectation 不一致")
    _require_runner_binding(compile_record, closure, repo_root, f"{sample_name} compile")
    _require_runner_binding(simulation_record, closure, repo_root, f"{sample_name} simulation")

    snapshot_sha = sha256_bytes(snapshot_raw)
    compile_sha = sha256_bytes(compile_raw)
    require(simulation_record.get("compile_source_snapshot_sha256") == snapshot_sha, f"{sample_name}: simulation record 的 snapshot SHA 绑定失败")
    require(simulation_record.get("compile_execution_record_sha256") == compile_sha, f"{sample_name}: simulation record 的 compile SHA 绑定失败")

    def report_bindings(observed: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "path": relative,
                "sha256": closure["sources"][relative]["sha256"],
                "bytes": closure["sources"][relative]["bytes"],
                "git_blob_sha1": closure["sources"][relative]["git_blob_sha1"],
            }
            for relative in observed
        ]

    return {
        "sample_index": sample_index,
        "run_id": run_id,
        "record_sha256": {
            "compile_source_snapshot.json": snapshot_sha,
            "compile_execution_record.json": compile_sha,
            "simulation_execution_record.json": sha256_bytes(simulation_raw),
        },
        "compile_sources": report_bindings(snapshot_sources),
        "compile_tooling_sources": report_bindings(snapshot_tools),
    }


def _verify_run_directory_set(runs_directory: Path, run_id: str) -> None:
    """要求指定 RunId 恰好出现在 109 个固定样本目录中。"""
    observed: list[int] = []
    for sample_directory in runs_directory.iterdir():
        candidate = sample_directory / run_id
        if not os.path.lexists(candidate):
            continue
        require(sample_directory.is_dir() and not sample_directory.is_symlink(), f"RunId 父目录缺失、类型错误或为符号链接：{sample_directory}")
        require(candidate.is_dir() and not candidate.is_symlink(), f"RunId 目录类型错误或为符号链接：{candidate}")
        match = SAMPLE_DIRECTORY_PATTERN.fullmatch(sample_directory.name)
        require(match is not None, f"RunId 出现在非标准样本目录：{sample_directory.name}")
        observed.append(int(match.group(1)))
    require(len(observed) == SAMPLE_COUNT, f"RunId 目录数量不是 109：{len(observed)}")
    require(len(set(observed)) == SAMPLE_COUNT, "RunId 存在重复样本目录")
    require(set(observed) == set(range(SAMPLE_COUNT)), "RunId 样本目录不是精确的 0..108")


def verify_batch(evidence_root: Path, run_id: str, repo_root: Path = ROOT) -> dict[str, Any]:
    """验证并返回完整 109 样本 source-to-Git 绑定报告，不写文件。"""
    require(isinstance(run_id, str) and RUN_ID_PATTERN.fullmatch(run_id) is not None, "run_id 仅可含 ASCII 字母、数字、下划线和连字符")
    root = _require_plain_directory(repo_root, "repository root")
    evidence = _require_plain_directory(evidence_root, "evidence root")
    closure = load_pinned_closure(root)
    runs_directory = evidence / "runs"
    require(runs_directory.is_dir() and not runs_directory.is_symlink(), f"runs directory 缺失或类型错误：{runs_directory}")
    _verify_run_directory_set(runs_directory, run_id)
    samples = [
        _verify_sample(evidence, root, run_id, sample_index, closure)
        for sample_index in range(SAMPLE_COUNT)
    ]
    require(len(samples) == SAMPLE_COUNT and [row["sample_index"] for row in samples] == list(range(SAMPLE_COUNT)), "样本索引集合不是精确的 0..108")
    return {
        "schema_version": "gestureforge_s2a_t68_snapshot_git_binding_v1",
        "status": REPORT_STATUS,
        "scope": "仅核验 109 个编译源快照到静态闭包及冻结 Git tree 的映射；不证明仿真完成、逐层 PL golden、PL head/D9、G4、G5 或阶段通过。",
        "sample_count": SAMPLE_COUNT,
        "run_id": run_id,
        "evidence_root": str(evidence),
        "repository_root": str(root),
        "static_source_closure": {
            "path": str(closure["manifest_path"].relative_to(root).as_posix()),
            "sha256": closure["manifest_sha256"],
            "baseline_commit": closure["baseline_commit"],
            "baseline_tree_sha1": closure["baseline_tree_sha1"],
            "source_count": len(closure["sources"]),
            "compiled_source_count": len(COMPILE_SOURCE_PATHS),
            "compile_tooling_count": len(COMPILE_TOOLING_PATHS),
            "baseline_blob_membership_count": len(closure["sources"]),
            "compiled_baseline_blob_content_verified_count": len(COMPILE_SOURCE_PATHS) + len(COMPILE_TOOLING_PATHS),
            "support_file_git_normalization": "其余闭包路径使用 git hash-object --path 核对冻结 baseline blob；原始字节长度保留清单采集值，不与经过 clean 过滤的 blob 长度比较。",
        },
        "samples": samples,
    }


def _write_new_report(evidence_root: Path, run_id: str, report: dict[str, Any]) -> tuple[Path, str]:
    """在 evidence root 中独占创建验证通过后的报告。"""
    report_name = f"source_snapshot_git_binding_{run_id}.json"
    report_path = evidence_root / report_name
    require(report_path.parent == evidence_root, "报告路径必须位于 evidence root 根目录")
    require(not report_path.is_symlink() and not os.path.lexists(report_path), f"拒绝覆盖既有报告或符号链接：{report_path}")
    raw = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    try:
        with report_path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        try:
            if report_path.is_file() and not report_path.is_symlink():
                report_path.unlink()
        except OSError:
            pass
        raise SnapshotBindingError(f"无法独占写入报告：{error}") from error
    return report_path, sha256_bytes(raw)


def main(argv: list[str] | None = None) -> int:
    """执行 109 样本只读核验，并仅在完整通过后写新报告。"""
    parser = argparse.ArgumentParser(description="核验 T68 编译源快照是否映射到冻结 Git tree")
    parser.add_argument("--evidence-root", type=Path, required=True, help="包含 runs/sample_NNN/<RunId> 的 T68 evidence root")
    parser.add_argument("--run-id", required=True, help="109 个样本共有的 RunId")
    args = parser.parse_args(argv)
    try:
        evidence = _require_plain_directory(args.evidence_root, "evidence root")
        report = verify_batch(evidence, args.run_id)
        report_path, report_sha = _write_new_report(evidence, args.run_id, report)
        console_report = dict(report)
        console_report["report_path"] = str(report_path)
        console_report["report_sha256"] = report_sha
        print(json.dumps(console_report, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (SnapshotBindingError, OSError, ValueError, TypeError, KeyError, OverflowError) as error:
        print(f"T68_SNAPSHOT_GIT_BINDING_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
