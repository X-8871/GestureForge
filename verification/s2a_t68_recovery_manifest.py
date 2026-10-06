#!/usr/bin/env python3
"""为被中断的 T68 candidate109 批次生成只读预检与恢复清单。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification import verify_s2a_network_backend_golden as fixture_verifier
from verification import verify_s2a_t68_snapshot_git_binding as snapshot_verifier

SAMPLE_COUNT = 109
OLD_RUN_ID = "candidate8x8_109_20261006_130252"
OLD_COMMIT = "999238284157bed77cdb3a37e3e6eea52daeefc4"
OLD_TREE = "b77b0ae5e1f49d2b7ab1c217f09edaedcbf5ea67"
SCHEMA = "gestureforge_s2a_t68_recovery_manifest_v1"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
RECORD_FILES = (
    "compile_source_snapshot.json",
    "compile_execution_record.json",
    "simulation_execution_record.json",
)
COMPILED_BINDING_PATHS = snapshot_verifier.COMPILE_SOURCE_PATHS + snapshot_verifier.COMPILE_TOOLING_PATHS


class RecoveryManifestError(ValueError):
    """表示 T68 recovery manifest 或预检证据不满足固定契约。"""


def require(condition: bool, message: str) -> None:
    """条件不成立时立即以明确原因停止。"""
    if not condition:
        raise RecoveryManifestError(message)


def _require_same_compile_source_closures(old_closure: dict[str, Any], new_closure: dict[str, Any]) -> None:
    """要求两组 Git tree 的 11 个实际编译源逐项同字节。"""
    for relative in snapshot_verifier.COMPILE_SOURCE_PATHS:
        old_source = old_closure["sources"][relative]
        new_source = new_closure["sources"][relative]
        require(
            old_source["sha256"] == new_source["sha256"],
            f"旧/新 candidate 编译源 SHA 不一致：{relative}",
        )
        require(
            old_source["bytes"] == new_source["bytes"],
            f"旧/新 candidate 编译源长度不一致：{relative}",
        )


def sha256_bytes(raw: bytes) -> str:
    """计算字节串 SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_path(path: Path) -> str:
    """返回适用于本机路径比较的绝对规范路径。"""
    return os.path.normcase(str(path.resolve(strict=True)))


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    """以 UTF-8 读取无重复字段的普通 JSON 文件。"""
    require(path.is_file() and not path.is_symlink(), f"{label} 缺失或不是普通文件：{path}")
    raw = path.read_bytes()

    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            require(key not in value, f"{label} 含重复 JSON 字段：{key}")
            value[key] = item
        return value

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RecoveryManifestError(f"{label} 不是有效 UTF-8 JSON：{path}") from error
    require(isinstance(value, dict), f"{label} 顶层必须是对象：{path}")
    return value, raw


def _plain_root(path: Path, label: str) -> Path:
    """验证并返回不含符号链接的普通目录。"""
    require(path.is_dir() and not path.is_symlink(), f"{label} 缺失或类型错误：{path}")
    resolved = path.resolve(strict=True)
    require(resolved == path.absolute(), f"{label} 路径解析不一致：{path}")
    return resolved


def _relative_name(value: str, label: str) -> str:
    """限制 manifest、dispatch 名称为单个安全路径组件。"""
    require(isinstance(value, str) and NAME_PATTERN.fullmatch(value) is not None, f"{label} 只允许 ASCII 字母、数字、下划线和连字符")
    require(value not in {".", ".."}, f"{label} 不可为路径特殊组件")
    return value


def validate_manifest(value: dict[str, Any], evidence_root: Path, repo_root: Path = ROOT) -> dict[str, Any]:
    """验证恢复清单的固定旧组、完整样本映射和逐样本哈希。"""
    root = _plain_root(evidence_root, "evidence root")
    repository = _plain_root(repo_root, "repository root")
    require(value.get("schema_version") == SCHEMA, "recovery manifest schema 不符")
    require(value.get("status") == "PASS_109_RECOVERY_MANIFEST", "recovery manifest 尚未完成")
    require(value.get("sample_count") == SAMPLE_COUNT, "recovery manifest sample_count 必须为 109")
    require(isinstance(value.get("evidence_root"), str), "recovery manifest evidence_root 缺失")
    require(_canonical_path(Path(value["evidence_root"])) == _canonical_path(root), "recovery manifest evidence_root 与当前目录不符")

    old_group = value.get("old_group")
    new_group = value.get("new_group")
    require(isinstance(old_group, dict) and isinstance(new_group, dict), "recovery manifest 缺少分组定义")
    require(old_group.get("run_id") == OLD_RUN_ID, "旧组 RunId 与本次 candidate109 不符")
    require(old_group.get("candidate_commit") == OLD_COMMIT and old_group.get("candidate_tree") == OLD_TREE, "旧组 Git commit/tree 未绑定已验证的完整 14 项闭包")
    require(old_group.get("first_index") == 0 and old_group.get("last_index") == 24, "旧组索引范围必须为 0..24")
    new_run_id = new_group.get("run_id")
    require(isinstance(new_run_id, str) and RUN_ID_PATTERN.fullmatch(new_run_id) is not None, "新组 RunId 非法")
    require(new_run_id != OLD_RUN_ID, "续跑 RunId 必须区别于原 RunId")
    require(new_group.get("first_index") == 25 and new_group.get("last_index") == 108, "新组索引范围必须为 25..108")
    for label, group in (("old", old_group), ("new", new_group)):
        require(isinstance(group.get("candidate_commit"), str) and GIT_OBJECT_PATTERN.fullmatch(group["candidate_commit"]) is not None, f"{label} group candidate commit 非法")
        require(isinstance(group.get("candidate_tree"), str) and GIT_OBJECT_PATTERN.fullmatch(group["candidate_tree"]) is not None, f"{label} group candidate tree 非法")
        require(group.get("binding_scope") == "11_rtl_sources_plus_3_tooling_sources", f"{label} group Git 绑定范围声明缺失")

    old_closure = snapshot_verifier.load_candidate_closure(
        repository, old_group["candidate_commit"], old_group["candidate_tree"]
    )
    new_closure = snapshot_verifier.load_candidate_closure(
        repository, new_group["candidate_commit"], new_group["candidate_tree"]
    )
    _require_same_compile_source_closures(old_closure, new_closure)

    rows = value.get("samples")
    require(isinstance(rows, list) and len(rows) == SAMPLE_COUNT, "recovery manifest 必须包含 109 个样本行")
    observed_indices: list[int] = []
    backend_hashes: set[str] = set()
    for row in rows:
        require(isinstance(row, dict), "recovery manifest sample row 类型错误")
        index = row.get("sample_index")
        require(type(index) is int and 0 <= index < SAMPLE_COUNT, "recovery manifest sample_index 非法")
        observed_indices.append(index)
        group = old_group if index <= 24 else new_group
        require(row.get("run_id") == group["run_id"], f"sample_{index:03d} RunId 与分组不符")
        require(row.get("candidate_commit") == group["candidate_commit"], f"sample_{index:03d} candidate commit 与分组不符")
        require(row.get("candidate_tree") == group["candidate_tree"], f"sample_{index:03d} candidate tree 与分组不符")
        require(isinstance(row.get("backend_sha256"), str) and SHA256_PATTERN.fullmatch(row["backend_sha256"]) is not None, f"sample_{index:03d} backend SHA 非法")
        expected_closure = old_closure if index <= 24 else new_closure
        require(
            row["backend_sha256"] == expected_closure["sources"]["src/s2a_network_backend.sv"]["sha256"],
            f"sample_{index:03d} backend SHA 与 candidate Git tree 不符",
        )
        backend_hashes.add(row["backend_sha256"])
        record_hashes = row.get("record_sha256")
        require(isinstance(record_hashes, dict) and set(record_hashes) == set(RECORD_FILES), f"sample_{index:03d} record_sha256 集合不完整")
        for filename, digest in record_hashes.items():
            require(isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest) is not None, f"sample_{index:03d} {filename} SHA 非法")
        tools = row.get("compile_tooling_sources")
        require(isinstance(tools, list) and len(tools) == len(snapshot_verifier.COMPILE_TOOLING_PATHS), f"sample_{index:03d} compile tooling rows 数量不符")
        tool_paths: list[str] = []
        for tool in tools:
            require(isinstance(tool, dict), f"sample_{index:03d} tooling row 类型错误")
            path = tool.get("path")
            require(path in snapshot_verifier.COMPILE_TOOLING_PATHS, f"sample_{index:03d} tooling path 未批准：{path}")
            require(path not in tool_paths, f"sample_{index:03d} tooling path 重复：{path}")
            tool_paths.append(path)
            require(type(tool.get("bytes")) is int and tool["bytes"] >= 0, f"sample_{index:03d} tooling byte length 非法：{path}")
            require(isinstance(tool.get("sha256"), str) and SHA256_PATTERN.fullmatch(tool["sha256"]) is not None, f"sample_{index:03d} tooling SHA 非法：{path}")
        require(set(tool_paths) == set(snapshot_verifier.COMPILE_TOOLING_PATHS), f"sample_{index:03d} tooling path 集合不完整")
    require(observed_indices == list(range(SAMPLE_COUNT)), "recovery manifest 样本索引必须按序精确覆盖 0..108")
    require(len(backend_hashes) == 1, "旧/新组 backend SHA 不一致，整批必须阻断")

    dispatch = value.get("dispatch")
    require(isinstance(dispatch, dict), "recovery manifest dispatch 绑定缺失")
    dispatch_name = _relative_name(dispatch.get("name"), "dispatch name")
    for field in ("batch_summary_sha256", "scheduler_snapshot_sha256"):
        digest = dispatch.get(field)
        require(isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest) is not None, f"dispatch {field} 非法")
    summary_path = root / dispatch_name / "batch_summary.json"
    scheduler_path = root / dispatch_name / "scheduler_source_snapshot.json"
    require(sha256_file(summary_path) == dispatch["batch_summary_sha256"], "dispatch batch_summary SHA 不符")
    require(sha256_file(scheduler_path) == dispatch["scheduler_snapshot_sha256"], "dispatch scheduler snapshot SHA 不符")
    summary, _ = _read_json(summary_path, "batch summary")
    require(summary.get("status") == "PASS_RESUMED_84_RUNNERS", "batch summary 未通过续跑 84 样本门")
    require(summary.get("run_id") == new_run_id and summary.get("first_index") == 25 and summary.get("last_index") == 108, "batch summary RunId/index 范围不符")
    require(summary.get("recovery_mode") is True, "batch summary 未声明 recovery mode")
    manifest_events = dispatch.get("events")
    summary_events = summary.get("events")
    require(isinstance(manifest_events, list) and isinstance(summary_events, list), "dispatch event 清单缺失")
    require(len(manifest_events) == len(summary_events) == 84, "dispatch event 数量必须为 84")
    sample_by_index = {row["sample_index"]: row for row in rows}
    event_indices: list[int] = []
    for event in manifest_events:
        require(isinstance(event, dict), "manifest event row 类型错误")
        index = event.get("sample_index")
        require(type(index) is int and 25 <= index <= 108, "manifest event sample_index 越界")
        event_indices.append(index)
        filename = f"sample_{index:03d}_event.json"
        require(event.get("file") == filename, f"sample_{index:03d} event file 名称不符")
        digest = event.get("sha256")
        require(isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest) is not None, f"sample_{index:03d} event SHA 非法")
        event_path = root / dispatch_name / filename
        event_value, event_raw = _read_json(event_path, f"sample_{index:03d} scheduler event")
        require(sha256_bytes(event_raw) == digest, f"sample_{index:03d} scheduler event SHA 不符")
        require(event_value.get("sample_index") == index and event_value.get("run_id") == new_run_id, f"sample_{index:03d} event 身份不符")
        require(event_value.get("status") == "PASS_RUNNER_AND_RECORDS" and event_value.get("runner_exit_code") == 0, f"sample_{index:03d} scheduler event 未通过")
        require(event_value.get("stdout_read_error") in (None, "") and event_value.get("stderr_read_error") in (None, ""), f"sample_{index:03d} stdout/stderr 存在未解决读取错误")
        validated = event_value.get("validated_records")
        expected_records = sample_by_index[index]["record_sha256"]
        require(isinstance(validated, dict), f"sample_{index:03d} event 缺少 record validation")
        require(validated.get("compile_snapshot_sha256") == expected_records["compile_source_snapshot.json"], f"sample_{index:03d} event snapshot SHA 与 manifest 不符")
        require(validated.get("compile_record_sha256") == expected_records["compile_execution_record.json"], f"sample_{index:03d} event compile SHA 与 manifest 不符")
        require(validated.get("simulation_record_sha256") == expected_records["simulation_execution_record.json"], f"sample_{index:03d} event simulation SHA 与 manifest 不符")
        for label in ("stdout", "stderr"):
            log_value = event_value.get(f"{label}_path")
            log_sha = event_value.get(f"{label}_sha256")
            log_bytes = event_value.get(f"{label}_bytes")
            log_path = Path(str(log_value))
            require(log_path.is_absolute() and _canonical_path(log_path.parent) == _canonical_path(root / dispatch_name), f"sample_{index:03d} {label} path 越界")
            require(isinstance(log_sha, str) and SHA256_PATTERN.fullmatch(log_sha) is not None, f"sample_{index:03d} {label} SHA 缺失")
            require(type(log_bytes) is int and log_path.is_file() and not log_path.is_symlink() and log_path.stat().st_size == log_bytes, f"sample_{index:03d} {label} 文件长度/类型不符")
            require(sha256_file(log_path) == log_sha, f"sample_{index:03d} {label} 文件 SHA 不符")
    require(event_indices == list(range(25, 109)), "dispatch events 必须按序精确覆盖 25..108")
    summary_event_indices = sorted(row.get("sample_index") for row in summary_events if isinstance(row, dict))
    require(summary_event_indices == event_indices, "batch summary event 集合与 recovery manifest 不一致")
    return value


def load_manifest(path: Path, evidence_root: Path, repo_root: Path = ROOT) -> tuple[dict[str, Any], str]:
    """读取、验证清单并返回其原始字节 SHA-256。"""
    raw_value, raw = _read_json(path, "recovery manifest")
    validate_manifest(raw_value, evidence_root, repo_root)
    return raw_value, sha256_bytes(raw)


def _fixture_inventory(root: Path) -> tuple[list[dict[str, Any]], str]:
    """为只读夹具目录建立轻量文件名、长度、时间戳指纹。"""
    fixtures = root / "fixtures"
    require(fixtures.is_dir() and not fixtures.is_symlink(), f"fixtures 目录缺失或类型错误：{fixtures}")
    rows: list[dict[str, Any]] = []
    for current, directories, filenames in os.walk(fixtures, topdown=True, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            path = current_path / name
            require(not path.is_symlink(), f"拒绝 fixtures 符号链接目录：{path}")
        for name in filenames:
            path = current_path / name
            require(path.is_file() and not path.is_symlink(), f"拒绝 fixtures 非普通文件：{path}")
            stat = path.stat()
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            })
    rows.sort(key=lambda row: row["path"])
    raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return rows, sha256_bytes(raw)


def _verify_current_candidate_worktree(closure: dict[str, Any], repo_root: Path) -> None:
    """确保 11 个编译源和 3 个编译工具正是所选 candidate Git tree 的字节。"""
    for relative in COMPILED_BINDING_PATHS:
        path = repo_root.joinpath(*relative.split("/"))
        require(path.is_file() and not path.is_symlink(), f"candidate 工作树源缺失或类型错误：{relative}")
        expected = closure["sources"][relative]
        stat = path.stat()
        require(stat.st_size == expected["bytes"], f"candidate 工作树 byte length 与 Git tree 不符：{relative}")
        require(sha256_file(path) == expected["sha256"], f"candidate 工作树 SHA 与 Git tree 不符：{relative}")


def _validate_new_targets(root: Path, new_run_id: str, dispatch_name: str, manifest_name: str) -> None:
    """拒绝任何已存在的新 RunId 目标、dispatch 或清单目标。"""
    runs = root / "runs"
    require(not runs.exists() or (runs.is_dir() and not runs.is_symlink()), f"runs 目录缺失或类型错误：{runs}")
    if runs.exists():
        for index in range(SAMPLE_COUNT):
            candidate = runs / f"sample_{index:03d}" / new_run_id
            require(not os.path.lexists(candidate), f"拒绝复用已存在的新 RunId 目录：{candidate}")
    dispatch_path = root / dispatch_name
    manifest_path = root / f"{manifest_name}.json"
    require(not os.path.lexists(dispatch_path), f"拒绝复用已存在的 dispatch 目录：{dispatch_path}")
    require(not os.path.lexists(manifest_path), f"拒绝覆盖已存在的 recovery manifest：{manifest_path}")


def preflight(
    evidence_root: Path,
    new_run_id: str,
    new_candidate_commit: str,
    new_candidate_tree: str,
    dispatch_name: str,
    manifest_name: str,
    repo_root: Path = ROOT,
) -> dict[str, Any]:
    """只读核验旧组、fixtures、候选源码与所有新输出目标。"""
    root = _plain_root(evidence_root, "evidence root")
    repository = _plain_root(repo_root, "repository root")
    require(root.name == OLD_RUN_ID, "EvidenceDirectory 必须是精确的原 candidate RunId 目录")
    require(RUN_ID_PATTERN.fullmatch(new_run_id) is not None and new_run_id != OLD_RUN_ID, "新 RunId 非法或与旧 RunId 相同")
    _relative_name(dispatch_name, "dispatch name")
    _relative_name(manifest_name, "manifest name")
    require(GIT_OBJECT_PATTERN.fullmatch(new_candidate_commit) is not None, "新 candidate commit 必须是完整小写 40 位 SHA-1")
    require(GIT_OBJECT_PATTERN.fullmatch(new_candidate_tree) is not None, "新 candidate tree 必须是完整小写 40 位 SHA-1")
    _validate_new_targets(root, new_run_id, dispatch_name, manifest_name)

    old_closure = snapshot_verifier.load_candidate_closure(repository, OLD_COMMIT, OLD_TREE)
    new_closure = snapshot_verifier.load_candidate_closure(repository, new_candidate_commit, new_candidate_tree)
    _require_same_compile_source_closures(old_closure, new_closure)
    old_backend = old_closure["sources"]["src/s2a_network_backend.sv"]["sha256"]
    new_backend = new_closure["sources"]["src/s2a_network_backend.sv"]["sha256"]
    require(old_backend == new_backend, "候选 backend SHA 与旧 PASS 组不同，不能构成同一 109 样本批次")
    _verify_current_candidate_worktree(new_closure, repository)

    old_samples = [
        snapshot_verifier._verify_sample(root, repository, OLD_RUN_ID, index, old_closure)
        for index in range(25)
    ]
    require([row["sample_index"] for row in old_samples] == list(range(25)), "旧 PASS 组未精确覆盖 0..24")

    inventory_before, inventory_before_sha = _fixture_inventory(root)
    fixture_rows: list[dict[str, Any]] = []
    for index in range(SAMPLE_COUNT):
        sample_name = f"sample_{index:03d}"
        manifest_path = root / "fixtures" / sample_name / "fixture_manifest.json"
        result = fixture_verifier.verify(manifest_path)
        require(result.get("sample_index") == index and result.get("simulator_started") is False, f"{sample_name} fixture 只读验证失败")
        fixture_rows.append({"sample_index": index, "manifest_sha256": sha256_file(manifest_path)})
    inventory_after, inventory_after_sha = _fixture_inventory(root)
    require(inventory_before == inventory_after and inventory_before_sha == inventory_after_sha, "fixture preflight 期间检测到文件集合、长度或时间戳变化")

    return {
        "schema_version": "gestureforge_s2a_t68_recovery_preflight_v1",
        "status": "PASS_READ_ONLY_RECOVERY_PREFLIGHT",
        "simulator_started": False,
        "process_check_performed": False,
        "evidence_root": str(root),
        "old_group": {
            "run_id": OLD_RUN_ID,
            "candidate_commit": OLD_COMMIT,
            "candidate_tree": OLD_TREE,
            "sample_count": len(old_samples),
            "samples": old_samples,
        },
        "new_group": {
            "run_id": new_run_id,
            "candidate_commit": new_candidate_commit,
            "candidate_tree": new_candidate_tree,
            "sample_indices": [25, 108],
            "backend_sha256": new_backend,
            "sources": [
                {
                    "path": str(repository.joinpath(*relative.split("/"))),
                    "sha256": new_closure["sources"][relative]["sha256"],
                    "bytes": new_closure["sources"][relative]["bytes"],
                }
                for relative in snapshot_verifier.COMPILE_SOURCE_PATHS
            ],
            "tooling_sources": [
                {
                    "path": str(repository.joinpath(*relative.split("/"))),
                    "sha256": new_closure["sources"][relative]["sha256"],
                    "bytes": new_closure["sources"][relative]["bytes"],
                }
                for relative in snapshot_verifier.COMPILE_TOOLING_PATHS
            ],
        },
        "fixture_read_only_check": {
            "sample_count": len(fixture_rows),
            "file_count": len(inventory_before),
            "inventory_sha256_before": inventory_before_sha,
            "inventory_sha256_after": inventory_after_sha,
            "sample_manifests": fixture_rows,
        },
        "new_targets_absent": True,
    }


def verify_recovery_samples(
    evidence_root: Path,
    old_commit: str,
    old_tree: str,
    new_run_id: str,
    new_commit: str,
    new_tree: str,
    repo_root: Path = ROOT,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """按旧 0..24 与新 25..108 的独立 candidate tree 验证 109 份记录。"""
    root = _plain_root(evidence_root, "evidence root")
    repository = _plain_root(repo_root, "repository root")
    require(old_commit == OLD_COMMIT and old_tree == OLD_TREE, "旧组 commit/tree 与已核验闭包不符")
    require(RUN_ID_PATTERN.fullmatch(new_run_id) is not None and new_run_id != OLD_RUN_ID, "新组 RunId 非法")
    old_closure = snapshot_verifier.load_candidate_closure(repository, old_commit, old_tree)
    new_closure = snapshot_verifier.load_candidate_closure(repository, new_commit, new_tree)
    _require_same_compile_source_closures(old_closure, new_closure)
    closures = {"old": old_closure, "new": new_closure}
    samples: list[dict[str, Any]] = []
    for index in range(SAMPLE_COUNT):
        group_name = "old" if index <= 24 else "new"
        run_id = OLD_RUN_ID if group_name == "old" else new_run_id
        closure = closures[group_name]
        result = snapshot_verifier._verify_sample(root, repository, run_id, index, closure)
        backend_sha = closure["sources"]["src/s2a_network_backend.sv"]["sha256"]
        tooling_rows = result["compile_tooling_sources"]
        sample = {
            "sample_index": index,
            "run_id": run_id,
            "candidate_commit": closure.get("candidate_commit"),
            "candidate_tree": closure.get("candidate_tree_sha1"),
            "backend_sha256": backend_sha,
            "record_sha256": result["record_sha256"],
            "compile_tooling_sources": tooling_rows,
        }
        samples.append(sample)
    require(len(samples) == SAMPLE_COUNT and [row["sample_index"] for row in samples] == list(range(SAMPLE_COUNT)), "恢复验证未覆盖精确 0..108")
    require(len({row["backend_sha256"] for row in samples}) == 1, "旧/新组 backend SHA 不一致")
    return samples, closures


def create_manifest(
    evidence_root: Path,
    new_run_id: str,
    new_candidate_commit: str,
    new_candidate_tree: str,
    dispatch_name: str,
    manifest_name: str,
    repo_root: Path = ROOT,
) -> tuple[Path, dict[str, Any], str]:
    """所有样本与 dispatch 摘要通过后独占创建完整 recovery manifest。"""
    root = _plain_root(evidence_root, "evidence root")
    repository = _plain_root(repo_root, "repository root")
    require(root.name == OLD_RUN_ID, "EvidenceDirectory 必须是精确的原 candidate RunId 目录")
    _relative_name(dispatch_name, "dispatch name")
    _relative_name(manifest_name, "manifest name")
    require(RUN_ID_PATTERN.fullmatch(new_run_id) is not None and new_run_id != OLD_RUN_ID, "新 RunId 非法")
    require(GIT_OBJECT_PATTERN.fullmatch(new_candidate_commit) is not None and GIT_OBJECT_PATTERN.fullmatch(new_candidate_tree) is not None, "新 candidate commit/tree 非法")
    manifest_path = root / f"{manifest_name}.json"
    require(not os.path.lexists(manifest_path), f"拒绝覆盖 recovery manifest：{manifest_path}")

    samples, closures = verify_recovery_samples(
        root, OLD_COMMIT, OLD_TREE, new_run_id, new_candidate_commit, new_candidate_tree, repository
    )
    dispatch_dir = root / dispatch_name
    require(dispatch_dir.is_dir() and not dispatch_dir.is_symlink(), f"dispatch 目录缺失或类型错误：{dispatch_dir}")
    summary_path = dispatch_dir / "batch_summary.json"
    scheduler_path = dispatch_dir / "scheduler_source_snapshot.json"
    summary, summary_raw = _read_json(summary_path, "batch summary")
    require(summary.get("status") == "PASS_RESUMED_84_RUNNERS", "续跑 scheduler 未以 84 个样本通过结束")
    require(summary.get("run_id") == new_run_id and summary.get("first_index") == 25 and summary.get("last_index") == 108, "续跑 scheduler 摘要身份或范围不符")
    require(summary.get("recovery_mode") is True, "续跑 scheduler 摘要缺少 recovery_mode")
    require(summary.get("succeeded_indices") == list(range(25, 109)), "scheduler 成功索引集合不是 25..108")
    require(summary.get("failed_indices") == [] and summary.get("remaining_indices") == [], "scheduler 仍记录失败或未运行样本")
    _, scheduler_raw = _read_json(scheduler_path, "scheduler source snapshot")
    event_rows: list[dict[str, Any]] = []
    sample_by_index = {row["sample_index"]: row for row in samples}
    events = summary.get("events")
    require(isinstance(events, list) and len(events) == 84, "scheduler 摘要 event 数量必须为 84")
    events = sorted(events, key=lambda row: row.get("sample_index", -1) if isinstance(row, dict) else -1)
    for event_row in events:
        require(isinstance(event_row, dict), "scheduler summary event row 类型错误")
        index = event_row.get("sample_index")
        require(type(index) is int and 25 <= index <= 108, "scheduler summary event sample_index 越界")
        expected_event_path = dispatch_dir / f"sample_{index:03d}_event.json"
        actual_event_path = Path(str(event_row.get("path", "")))
        require(actual_event_path.resolve(strict=True) == expected_event_path.resolve(strict=True), f"sample_{index:03d} scheduler event path 不符")
        event_value, event_raw = _read_json(expected_event_path, f"sample_{index:03d} scheduler event")
        event_sha = sha256_bytes(event_raw)
        require(event_row.get("sha256") == event_sha and event_row.get("write_error") in (None, ""), f"sample_{index:03d} scheduler event 写入或 SHA 失败")
        require(event_value.get("status") == "PASS_RUNNER_AND_RECORDS" and event_value.get("runner_exit_code") == 0, f"sample_{index:03d} scheduler event 未通过")
        require(event_value.get("stdout_read_error") in (None, "") and event_value.get("stderr_read_error") in (None, ""), f"sample_{index:03d} stdout/stderr 持续不可读")
        validated = event_value.get("validated_records")
        expected_records = sample_by_index[index]["record_sha256"]
        require(isinstance(validated, dict), f"sample_{index:03d} scheduler event 缺少 validated_records")
        require(validated.get("compile_snapshot_sha256") == expected_records["compile_source_snapshot.json"], f"sample_{index:03d} event snapshot SHA 不符")
        require(validated.get("compile_record_sha256") == expected_records["compile_execution_record.json"], f"sample_{index:03d} event compile SHA 不符")
        require(validated.get("simulation_record_sha256") == expected_records["simulation_execution_record.json"], f"sample_{index:03d} event simulation SHA 不符")
        event_rows.append({"sample_index": index, "file": expected_event_path.name, "sha256": event_sha})
    require([row["sample_index"] for row in event_rows] == list(range(25, 109)), "scheduler event rows 必须精确覆盖 25..108")
    dispatch = {
        "name": dispatch_name,
        "batch_summary_sha256": sha256_bytes(summary_raw),
        "scheduler_snapshot_sha256": sha256_bytes(scheduler_raw),
        "events": event_rows,
    }
    value: dict[str, Any] = {
        "schema_version": SCHEMA,
        "status": "PASS_109_RECOVERY_MANIFEST",
        "sample_count": SAMPLE_COUNT,
        "evidence_root": str(root),
        "old_group": {
            "run_id": OLD_RUN_ID,
            "candidate_commit": OLD_COMMIT,
            "candidate_tree": OLD_TREE,
            "first_index": 0,
            "last_index": 24,
            "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
        },
        "new_group": {
            "run_id": new_run_id,
            "candidate_commit": new_candidate_commit,
            "candidate_tree": new_candidate_tree,
            "first_index": 25,
            "last_index": 108,
            "binding_scope": "11_rtl_sources_plus_3_tooling_sources",
        },
        "dispatch": dispatch,
        "samples": samples,
    }
    validate_manifest(value, root, repository)
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    try:
        with manifest_path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        raise RecoveryManifestError(
            f"无法独占写入 recovery manifest；保留已存在或部分写入的目标，请使用新名称重试：{manifest_path}: {error}"
        ) from error
    return manifest_path, value, sha256_bytes(raw)


def main(argv: list[str] | None = None) -> int:
    """执行只读预检或在全部仿真证据通过后生成恢复清单。"""
    parser = argparse.ArgumentParser(description="T68 candidate109 只读预检及跨 RunId 恢复清单工具")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    for operation in ("preflight", "create"):
        child = subparsers.add_parser(operation)
        child.add_argument("--evidence-root", type=Path, required=True)
        child.add_argument("--new-run-id", required=True)
        child.add_argument("--new-candidate-commit", required=True)
        child.add_argument("--new-candidate-tree", required=True)
        child.add_argument("--dispatch-name", required=True)
        child.add_argument("--manifest-name", required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "preflight":
            result = preflight(
                args.evidence_root, args.new_run_id, args.new_candidate_commit,
                args.new_candidate_tree, args.dispatch_name, args.manifest_name,
            )
        else:
            path, manifest, digest = create_manifest(
                args.evidence_root, args.new_run_id, args.new_candidate_commit,
                args.new_candidate_tree, args.dispatch_name, args.manifest_name,
            )
            result = {"status": manifest["status"], "manifest_path": str(path), "manifest_sha256": digest, "sample_count": len(manifest["samples"])}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (RecoveryManifestError, snapshot_verifier.SnapshotBindingError, OSError, ValueError, TypeError, KeyError, OverflowError) as error:
        print(f"T68_RECOVERY_MANIFEST_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
