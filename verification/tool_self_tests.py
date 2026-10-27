#!/usr/bin/env python3
"""工具自测套件（冻结硬条件）：每个验证工具都要有**必 PASS 例**与**必 FAIL 例**。

覆盖（r13 收紧版，对应 FREEZE_DELTA_E §七.4 与任务 A7②③）：
1. `readonly guard`（构建器只读守门）：**真实调用** `s6a_build_evidence._guard_check` ——
   不改文件 → 静默通过；故意改受保护文件 → 必须中止（exit 1）。
2. `export_selfproof`：**交付提交**自证 → exit 0；**工作区快照**自证 → exit 0；
   **不可解析的提交** → exit 非 0（不得静默成功）。BLK-D1 之后 `--s6a-run` 为必填，凡调用一律显式传入。
3. `claim_verify`（按 `--package` 选 S6-A/S6-B 声明集）：正常跑 → ALL_CLAIMS_VERIFIED（exit 0）；
   内置假声明 self-test → 真实退出码非 0。两条「数量不符 / 空列表」必 FAIL 例**只在临时副本内**运行
   （A7②：绝不改写真实 run-dir 的冻结附录）。
4. `m4_residual_regression`：3 条真实残留行 → 必 FAIL；`--run-dir` 不存在 → 拒绝。
5. `approved_package_scan`：**两向自测** —— B1..B7 必判失败形态全部命中、C1..C4 必须放行对照全部不命中。

新增（A7③）：`skipped` **不得计绿**。任一侧例被跳过（无法解析交付提交等）时总判定为
`INCOMPLETE_SKIPPED` 且退出码非 0；只有全部用例非跳过且符合预期才是 `ALL_AS_EXPECTED`。
`--simulate-skip` 是这条规则的**必 FAIL 自测**：人为把一例置为跳过，总判定必须变红。

路径限制按本机非对抗并发文件系统变更威胁模型处理；固定子进程输出在调用前复验以缩小 TOCTOU 窗口，
但不能抵御本机恶意进程在复验与实际打开文件之间替换路径。

用法：
    python -B verification/tool_self_tests.py --project-root <abs> --run-dir <rel> \
        --package s6a|s6b [--s6a-run <rel>] [--s6b-run <rel>] [--out <json>]
退出码：0 = 全部符合预期且无跳过；1 = 有不符合预期或有跳过；2 = 输入不合法。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

PY = sys.executable


def claim_normal_ok(exit_code: int, payload: dict) -> bool:
    """正常声明必须真实成功；结构完整不能替代声明验证通过。"""
    claims = payload.get("claims", [])
    declared = payload.get("claims_declared")
    return (exit_code == 0 and payload.get("verdict") == "ALL_CLAIMS_VERIFIED"
            and payload.get("count_ok") is True and isinstance(declared, int)
            and declared > 0 and payload.get("claims_recorded") == declared + 1
            and len(claims) == declared + 1
            and len({c.get("claim_id") for c in claims}) == len(claims)
            and all(c.get("verdict") == "VERIFIED" and not c.get("readonly_violation")
                    and type(c.get("exit_code")) is int
                    and (c.get("exit_code") != 0 if c.get("claim_id") == "self_test_false_claim"
                         else c.get("exit_code") == c.get("expected_exit") == 0)
                    for c in claims)
            and sum(c.get("claim_id") == "self_test_false_claim" for c in claims) == 1)

# 仅使用经确认的可达提交—已提交包配对；tag 移动时不默认为新来源。
DELIVERY_CANDIDATES = (
    ("stage6-freeze-20261023-r6", "2f16d668a14604ad3d4846e29c8a0f10489ac08b",
     "report/evidence/S6-A/s6a_g0_20261023_r12", "report/evidence/S6-B/s6b_core_20261023_r07"),
    ("stage6-freeze-20261023-r5", "0a2abc4956242c118b7d5ef6d4a1fe1b1ff28351",
     "report/evidence/S6-A/s6a_g0_20261023_r11", "report/evidence/S6-B/s6b_core_20261023_r06"),
)


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def make_temp_copy(root: Path, run_rel: str, tmp: Path) -> Path:
    """把工具运行所需的只读输入 + run-dir 复制到隔离临时树（A7②）。"""
    root = root.resolve()
    run_rel = _normalize_run_rel(run_rel, "run-dir")
    source_run = _resolve_confined_path(root, run_rel, "run-dir 源路径", must_exist=True)
    if not source_run.is_dir():
        raise ValueError(f"run-dir 必须是项目根内的目录：{source_run}")
    _validate_source_tree(root, source_run, "run-dir 源条目")
    state_source, state_references = _state_reference_copy_plan(root)

    temp_root = tmp.resolve()
    if not temp_root.is_dir():
        raise ValueError(f"临时副本父目录不存在：{temp_root}")
    copy_root = _resolve_confined_path(temp_root, "copy", "临时副本根目录", must_exist=False)
    if copy_root.exists() or copy_root.is_symlink():
        raise ValueError(f"临时副本目标已存在：{copy_root}")

    copy_plan: list[tuple[str, Path, str]] = []
    for name in ("docs", "verification", "src"):
        source = _resolve_confined_path(root, name, f"隔离副本源目录 {name}", must_exist=False)
        if source.is_dir():
            _validate_source_tree(root, source, f"隔离副本源目录 {name}")
            copy_plan.append((name, source, "tree"))
    copy_plan.append((".codex/STATE.md", state_source, "file"))
    copy_plan.append((run_rel, source_run, "tree"))
    copy_plan.extend(state_references)

    for relative, _source, _kind in copy_plan:
        _resolve_confined_path(copy_root, relative,
                               f"临时副本目标路径 {relative}", must_exist=False)
    copy_root.mkdir(parents=True, exist_ok=False)
    for relative, source, kind in copy_plan:
        source = _resolve_confined_path(root, relative,
                                        f"临时副本源路径 {relative}", must_exist=True)
        target = _resolve_confined_path(copy_root, relative,
                                        f"临时副本目标路径 {relative}", must_exist=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        target = _resolve_confined_path(copy_root, relative,
                                        f"临时副本目标路径 {relative}", must_exist=False)
        source = _resolve_confined_path(root, relative,
                                        f"临时副本源路径 {relative}", must_exist=True)
        if kind == "tree":
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)
    return copy_root


def _normalized_run_rel(value: str) -> str:
    """仅用于和已知候选路径比较，不改写传给验证工具的显式路径。"""
    return _normalize_run_rel(value, "证据 RunId")


def resolve_delivery_pair(root: Path, explicit_commit: str | None = None,
                          explicit_s6a_run: str | None = None,
                          explicit_s6b_run: str | None = None) -> dict:
    """解析提交与其证据包的配对；不把显式部分参数与默认包混搭。"""
    candidates = []
    for tag, expected_commit, s6a_run, s6b_run in DELIVERY_CANDIDATES:
        code, output = run(["git", "-C", str(root), "rev-parse", f"{tag}^"], root)
        actual_commit = output.strip()
        if code == 0 and actual_commit == expected_commit:
            candidates.append({"tag": tag, "commit": expected_commit,
                               "s6a_run": s6a_run, "s6b_run": s6b_run})

    explicit = any((explicit_commit, explicit_s6a_run, explicit_s6b_run))
    normalized_commit = None
    if explicit_commit:
        code, output = run(["git", "-C", str(root), "rev-parse", "--verify",
                            f"{explicit_commit}^{{commit}}"], root)
        if code == 0:
            normalized_commit = output.strip()

    for candidate in candidates:
        if explicit_commit and normalized_commit != candidate["commit"]:
            continue
        if explicit_s6a_run and _normalized_run_rel(explicit_s6a_run) != candidate["s6a_run"]:
            continue
        if explicit_s6b_run and _normalized_run_rel(explicit_s6b_run) != candidate["s6b_run"]:
            continue
        selection = "known_candidate" if explicit else "default_candidate"
        return {**candidate, "selection": selection, "explicit": explicit}

    if explicit_commit and explicit_s6a_run:
        # 自定义成对输入仍交给真实 export_selfproof 验证哈希与 C11。
        return {"tag": None, "commit": normalized_commit or explicit_commit,
                "s6a_run": explicit_s6a_run, "s6b_run": explicit_s6b_run,
                "selection": "explicit_pair", "explicit": True}
    if explicit:
        return {"tag": None, "commit": None, "s6a_run": None, "s6b_run": None,
                "selection": "unpaired_explicit_arguments", "explicit": True}
    if candidates:
        return {**candidates[0], "selection": "default_candidate", "explicit": False}
    return {"tag": None, "commit": None, "s6a_run": None, "s6b_run": None,
            "selection": "no_reachable_candidate", "explicit": False}


def delivery_pairing_regression(root: Path) -> dict:
    """回归默认配对固定且未成对显式参数不会被静默补齐。"""
    default = resolve_delivery_pair(root)
    explicit_candidate = resolve_delivery_pair(root, DELIVERY_CANDIDATES[0][1],
                                               DELIVERY_CANDIDATES[0][2], DELIVERY_CANDIDATES[0][3])
    unpaired_commit = resolve_delivery_pair(root, "0000000000000000000000000000000000000000")
    unpaired_run = resolve_delivery_pair(root, None, "report/evidence/S6-A/custom_run")
    explicit_pair = resolve_delivery_pair(root, "0000000000000000000000000000000000000000",
                                          "report/evidence/S6-A/custom_run")
    mismatched_known_pair = resolve_delivery_pair(root, DELIVERY_CANDIDATES[0][1],
                                                  DELIVERY_CANDIDATES[1][2])
    expected = (DELIVERY_CANDIDATES[0][1], DELIVERY_CANDIDATES[0][2], DELIVERY_CANDIDATES[0][3])
    passed = (
        default["selection"] == "default_candidate"
        and (default["commit"], default["s6a_run"], default["s6b_run"]) == expected
        and explicit_candidate["selection"] == "known_candidate"
        and (explicit_candidate["commit"], explicit_candidate["s6a_run"], explicit_candidate["s6b_run"]) == expected
        and unpaired_commit["selection"] == "unpaired_explicit_arguments"
        and unpaired_commit["s6a_run"] is None and unpaired_commit["s6b_run"] is None
        and unpaired_run["selection"] == "unpaired_explicit_arguments"
        and unpaired_run["commit"] is None and unpaired_run["s6b_run"] is None
        and explicit_pair["selection"] == "explicit_pair"
        and explicit_pair["commit"] == "0000000000000000000000000000000000000000"
        and explicit_pair["s6a_run"] == "report/evidence/S6-A/custom_run"
        and explicit_pair["s6b_run"] is None
        and mismatched_known_pair["selection"] == "explicit_pair"
        and mismatched_known_pair["commit"] == DELIVERY_CANDIDATES[0][1]
        and mismatched_known_pair["s6a_run"] == DELIVERY_CANDIDATES[1][2]
        and mismatched_known_pair["s6b_run"] is None
    )
    return {"passed": passed, "default": default, "explicit_candidate": explicit_candidate,
            "unpaired_commit": unpaired_commit, "unpaired_run": unpaired_run,
            "explicit_pair": explicit_pair, "mismatched_known_pair": mismatched_known_pair}


def _claim_positive_fixtures(run_id: str, package: str) -> dict[str, dict]:
    """为隔离 claim_verify 正例装配带标记的最小有效输入；不是交付证据。"""
    task_id = "S6-A" if package == "s6a" else "S6-B"
    tool_fixture = {
        "schema_version": 1, "artifact": "tool_self_tests", "task_id": task_id,
        "run_id": run_id, "package": package, "fixture_only": True,
        "fixture_marker": "ISOLATED_CLAIM_VERIFY_POSITIVE_FIXTURE",
        "scope": "仅供隔离副本的 claim_verify 正向装配回归；不是工具套件实测证据。",
        "cases": [{"case_id": "fixture_positive_case", "verdict": "AS_EXPECTED",
                   "fixture_only": True}],
        "unexpected": [], "skipped_cases": [], "verdict": "ALL_AS_EXPECTED",
    }
    pair_fixture = {
        "schema_version": 1, "artifact": "fresh_selfcheck_pair", "fixture_only": True,
        "fixture_marker": "ISOLATED_FRESH_SELFCHECK_POSITIVE_FIXTURE",
        "scope": "仅供隔离副本在真实 C6 重跑前校验清单绑定；随后由 C6 实际输出覆盖。",
        "rule": "正例夹具仅验证 claim_verify/C11 装配，不代表构建后实测。",
        "gap_seconds": 30,
        "first": {"command": "fixture-only", "exit_code": 0, "status": "ALL_PASS",
                   "c11": "PASS", "errors": []},
        "second": {"command": "fixture-only", "exit_code": 0, "status": "ALL_PASS",
                    "c11": "PASS", "errors": []},
        "verdict": "BOTH_ALL_PASS",
    }
    return {"tool_self_tests.json": tool_fixture, "fresh_selfcheck_pair.json": pair_fixture}


def _fixture_binding_paths(copy_root: Path, run_dir: Path, names: list[str]) -> tuple[Path, Path, dict[str, Path], dict[str, Path]]:
    """在临时副本写入前验证全部清单、源码和夹具目标路径。"""
    names = [_safe_relative_path(name, "fixture 文件名").as_posix() for name in names]
    manifest_path = _resolve_confined_path(run_dir, "delivery_manifest.json",
                                           "fixture delivery_manifest.json", must_exist=True)
    hashes_path = _resolve_confined_path(run_dir, "hashes_sha256.txt",
                                         "fixture hashes_sha256.txt", must_exist=True)
    source_relatives = ("verification/tool_self_tests.py",
                        "verification/hash_convention_check.py")
    source_paths = {
        relative: _resolve_confined_path(copy_root, relative,
                                         f"fixture 验证源码 {relative}", must_exist=True)
        for relative in source_relatives
    }
    target_paths = {
        name: _resolve_confined_path(run_dir, name, f"fixture 文件 {name}", must_exist=True)
        for name in names
    }
    return manifest_path, hashes_path, source_paths, target_paths


def _refresh_copy_hash_bindings(copy_root: Path, run_rel: str, names: list[str]) -> dict[str, str]:
    """只在隔离副本内同步指定 fixture 文件的 SHA-256 与两份清单。"""
    run_rel, run_dir = _resolve_run_dir(copy_root, run_rel, "fixture RunId")
    names = [_safe_relative_path(name, "fixture 文件名").as_posix() for name in names]
    manifest_path, hashes_path, source_paths, target_paths = _fixture_binding_paths(
        copy_root, run_dir, names)
    if not manifest_path.is_file() or not hashes_path.is_file():
        raise ValueError("隔离副本缺少 delivery_manifest.json 或 hashes_sha256.txt")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise ValueError("隔离副本 delivery_manifest.files 必须为列表")
    hash_lines = hashes_path.read_text(encoding="utf-8").splitlines()
    source_relatives = tuple(source_paths)
    updates: dict[str, str] = {}
    line_indexes: dict[str, int] = {}
    for name in names:
        target = target_paths[name]
        if not target.is_file():
            raise ValueError(f"隔离副本缺少 fixture 文件：{name}")
        relative = f"{Path(run_rel).as_posix().rstrip('/')}/{name}"
        matched = [entry for entry in entries if entry.get("path") == relative]
        if len(matched) != 1:
            raise ValueError(f"manifest 对 {relative} 应恰有一条绑定，实际 {len(matched)}")
        line_matches = []
        for index, line in enumerate(hash_lines):
            parts = line.split(maxsplit=1)
            if len(parts) == 2 and Path(parts[1]).name == name:
                line_matches.append(index)
        if len(line_matches) != 1:
            raise ValueError(f"hashes_sha256.txt 对 {name} 应恰有一条绑定，实际 {len(line_matches)}")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        matched[0]["sha256"] = digest
        line_indexes[name] = line_matches[0]
        updates[name] = digest
    for name, digest in updates.items():
        hash_lines[line_indexes[name]] = f"{digest}  {name}"
    if names:
        hashes_path = _resolve_confined_path(run_dir, "hashes_sha256.txt",
                                             "fixture hashes_sha256.txt", must_exist=True)
        hashes_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    for source_relative in source_relatives:
        source_path = source_paths[source_relative]
        if not source_path.is_file():
            raise ValueError(f"隔离副本缺少当前自测源码：{source_relative}")
        source_entries = [entry for entry in entries if entry.get("path") == source_relative]
        if len(source_entries) != 1:
            raise ValueError(f"manifest 对 {source_relative} 应恰有一条绑定，实际 {len(source_entries)}")
        source_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_entries[0]["sha256"] = source_digest
        updates[source_relative] = source_digest

    if names:
        hashes_relative = f"{Path(run_rel).as_posix().rstrip('/')}/hashes_sha256.txt"
        hashes_entries = [entry for entry in entries if entry.get("path") == hashes_relative]
        if len(hashes_entries) != 1:
            raise ValueError(f"manifest 对 {hashes_relative} 应恰有一条绑定，实际 {len(hashes_entries)}")
        hashes_digest = hashlib.sha256(hashes_path.read_bytes()).hexdigest()
        hashes_entries[0]["sha256"] = hashes_digest
        updates["hashes_sha256.txt"] = hashes_digest
    manifest_path = _resolve_confined_path(run_dir, "delivery_manifest.json",
                                           "fixture delivery_manifest.json", must_exist=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reread_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reread_lines = hashes_path.read_text(encoding="utf-8").splitlines()
    for name in names:
        digest = updates[name]
        relative = f"{Path(run_rel).as_posix().rstrip('/')}/{name}"
        matching = [entry for entry in reread_manifest["files"] if entry.get("path") == relative]
        line_matching = [line.split(maxsplit=1) for line in reread_lines
                         if len(line.split(maxsplit=1)) == 2 and Path(line.split(maxsplit=1)[1]).name == name]
        if (len(matching) != 1 or matching[0].get("sha256") != digest
                or len(line_matching) != 1 or line_matching[0][0] != digest):
            raise ValueError(f"隔离副本哈希绑定回读不一致：{relative}")
    if names:
        hashes_relative = f"{Path(run_rel).as_posix().rstrip('/')}/hashes_sha256.txt"
        hashes_entries = [entry for entry in reread_manifest["files"] if entry.get("path") == hashes_relative]
        if (len(hashes_entries) != 1
                or hashes_entries[0].get("sha256") != hashlib.sha256(hashes_path.read_bytes()).hexdigest()):
            raise ValueError(f"隔离副本 manifest 未绑定更新后的 hashes_sha256.txt：{hashes_relative}")
    for source_relative in source_relatives:
        source_path = source_paths[source_relative]
        source_entries = [entry for entry in reread_manifest["files"]
                          if entry.get("path") == source_relative]
        if (len(source_entries) != 1
                or source_entries[0].get("sha256") != hashlib.sha256(source_path.read_bytes()).hexdigest()):
            raise ValueError(f"隔离副本 manifest 未绑定当前验证源码：{source_relative}")
    return updates


def _verify_copy_hash_bindings(copy_root: Path, run_rel: str, names: list[str]) -> dict[str, str]:
    """只读核验隔离副本当前字节与 hash 文件、delivery manifest 一致。"""
    run_rel, run_dir = _resolve_run_dir(copy_root, run_rel, "fixture RunId")
    names = [_safe_relative_path(name, "fixture 文件名").as_posix() for name in names]
    manifest_path, hashes_path, source_paths, target_paths = _fixture_binding_paths(
        copy_root, run_dir, names)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hash_lines = hashes_path.read_text(encoding="utf-8").splitlines()
    verified = {}
    for name in names:
        target = target_paths[name]
        if not target.is_file():
            raise ValueError(f"隔离副本缺少 fixture 文件：{name}")
        relative = f"{Path(run_rel).as_posix().rstrip('/')}/{name}"
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        entries = [item for item in manifest.get("files", []) if item.get("path") == relative]
        lines = [line.split(maxsplit=1) for line in hash_lines
                 if len(line.split(maxsplit=1)) == 2 and Path(line.split(maxsplit=1)[1]).name == name]
        if (len(entries) != 1 or entries[0].get("sha256") != digest
                or len(lines) != 1 or lines[0][0] != digest):
            raise ValueError(f"隔离副本哈希绑定与文件字节不一致：{relative}")
        verified[name] = digest
    hashes_relative = f"{run_rel}/hashes_sha256.txt"
    bound_relatives = [hashes_relative, *source_paths]
    for relative in bound_relatives:
        path = (_resolve_confined_path(copy_root, relative,
                                       f"fixture 绑定文件 {relative}", must_exist=True)
                if relative == hashes_relative else source_paths[relative])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries = [item for item in manifest.get("files", []) if item.get("path") == relative]
        if len(entries) != 1 or entries[0].get("sha256") != digest:
            raise ValueError(f"隔离副本哈希绑定与文件字节不一致：{relative}")
        verified[relative] = digest
    return verified


def prepare_claim_positive_fixture(copy_root: Path, run_rel: str, package: str) -> dict:
    """仅填充隔离副本里的空占位，并校验其哈希列表与 manifest。"""
    if package != "s6a":
        return {"applicable": False, "fixture_only": True, "created_files": [], "sha256": {}}
    run_rel, run_dir = _resolve_run_dir(copy_root, run_rel, "claim fixture RunId")
    fixtures = _claim_positive_fixtures(run_dir.name, package)
    created = []
    markers = {}
    _manifest_path, _hashes_path, _source_paths, target_paths = _fixture_binding_paths(
        copy_root, run_dir, list(fixtures))
    for name, payload in fixtures.items():
        target = target_paths[name]
        if not target.is_file():
            raise ValueError(f"隔离副本缺少预期的 S6-A 文件：{name}")
        if target.stat().st_size == 0:
            target = _resolve_confined_path(run_dir, name,
                                            f"claim fixture 文件 {name}", must_exist=True)
            target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            created.append(name)
            markers[name] = payload["fixture_marker"]
    updated = _refresh_copy_hash_bindings(copy_root, run_rel, created)
    # 即使保留了非空真实文件，也要验证其既有绑定；不帮忙“修复”失配包。
    current_hashes = _verify_copy_hash_bindings(copy_root, run_rel, list(fixtures))
    return {"applicable": True, "fixture_only": True,
            "scope": "仅隔离副本；不修改真实 RunId 或生成交付自测证据。",
            "created_files": created, "fixture_markers": markers,
            "updated_sha256": updated, "validated_sha256": current_hashes}


def seed_fresh_claim_positive_placeholders(copy_root: Path, run_rel: str) -> dict:
    """在新建临时测试副本内从空占位开始构造正例夹具。"""
    run_rel, run_dir = _resolve_run_dir(copy_root, run_rel, "claim fixture RunId")
    names = ["tool_self_tests.json", "fresh_selfcheck_pair.json"]
    prior_copy_files = {}
    _manifest_path, _hashes_path, _source_paths, targets = _fixture_binding_paths(
        copy_root, run_dir, names)
    for name in names:
        target = targets[name]
        if not target.is_file():
            raise ValueError(f"隔离副本缺少待种子占位文件：{name}")
        content = target.read_bytes()
        prior_copy_files[name] = {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        target = _resolve_confined_path(run_dir, name,
                                        f"claim fixture 文件 {name}", must_exist=True)
        target.write_bytes(b"")
    updated = _refresh_copy_hash_bindings(copy_root, run_rel, names)
    verified = _verify_copy_hash_bindings(copy_root, run_rel, names)
    return {"fixture_only": True,
            "scope": "仅在新建临时副本中以空占位种子构造正例；不修复或改写源 RunId。",
            "seeded_placeholder_sha256": hashlib.sha256(b"").hexdigest(),
            "copied_source_file_before_seed": prior_copy_files,
            "updated_sha256": updated, "validated_sha256": verified}


def _file_snapshot(path: Path) -> dict:
    """读取共享输出的存在性、字节哈希和修改时间，不创建目标。"""
    if not path.is_file():
        return {"exists": False}
    stat = path.stat()
    return {"exists": True, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def hash_convention_isolation_regression(root: Path, shared_root: Path) -> dict:
    """证明换行口径自测在临时项目副本中只向该副本写输出。"""
    root = root.resolve()
    shared_root = shared_root.resolve()
    source_helper = _resolve_confined_path(root, "verification/hash_convention_check.py",
                                           "换行检查源码", must_exist=True)
    source_checker = _resolve_confined_path(root, "verification/check_stage_delivery.py",
                                            "交付检查源码", must_exist=True)
    shared_output = _resolve_confined_path(shared_root, "tmp/6/hash_convention_check.json",
                                           "共享输出路径", must_exist=False)
    before = _file_snapshot(shared_output)
    with tempfile.TemporaryDirectory(prefix="hash_convention_isolation_") as tmp:
        temp_root = Path(tmp).resolve()
        isolated_root = _resolve_confined_path(temp_root, "project_copy",
                                               "换行检查临时项目根", must_exist=False)
        isolated_root.mkdir(parents=True, exist_ok=False)
        isolated_verification = _resolve_confined_path(isolated_root, "verification",
                                                       "临时验证源码目录", must_exist=False)
        isolated_verification.mkdir(parents=True, exist_ok=False)
        helper_target = _resolve_confined_path(isolated_root,
                                               "verification/hash_convention_check.py",
                                               "临时换行检查源码目标", must_exist=False)
        checker_target = _resolve_confined_path(isolated_root,
                                                "verification/check_stage_delivery.py",
                                                "临时交付检查源码目标", must_exist=False)
        shutil.copyfile(source_helper, helper_target)
        shutil.copyfile(source_checker, checker_target)
        isolated_output = _resolve_confined_path(isolated_root, "tmp/6/hash_convention_check.json",
                                                 "临时换行检查输出", must_exist=False)
        exit_code, output = run([PY, "-B", "verification/hash_convention_check.py"], isolated_root)
        payload = {}
        if isolated_output.is_file():
            payload = json.loads(isolated_output.read_text(encoding="utf-8"))
        after = _file_snapshot(shared_output)
        cases = payload.get("cases", [])
        passed = (exit_code == 0 and payload.get("verdict") == "ALL_AS_EXPECTED"
                  and len(cases) == 5
                  and all(case.get("verdict") == "AS_EXPECTED" for case in cases)
                  and isolated_output.is_file() and before == after)
        return {"passed": passed, "exit_code": exit_code,
                "disposable_output": str(isolated_output),
                "disposable_output_exists": isolated_output.is_file(),
                "semantic_verdict": payload.get("verdict"),
                "semantic_case_count": len(cases),
                "shared_output": str(shared_output),
                "shared_output_before": before, "shared_output_after": after,
                "stdout_stderr": output.strip()}


def _safe_relative_path(value: str, label: str) -> Path:
    """拒绝绝对路径、盘符、UNC 与路径穿越，只接受普通相对路径。"""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 必须是非空相对路径")
    windows_path = PureWindowsPath(value)
    portable = value.replace("\\", "/").rstrip("/")
    if (not portable or Path(value).is_absolute() or PurePosixPath(portable).is_absolute()
            or windows_path.drive or windows_path.root):
        raise ValueError(f"{label} 不允许绝对路径、盘符或 UNC 路径")
    parts = portable.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"{label} 不允许空路径段、当前目录或路径穿越")
    return Path(*parts)


def _normalize_run_rel(value: str, label: str) -> str:
    """规范化仓库内 RunId，并拒绝所有绝对路径与穿越段。"""
    return _safe_relative_path(value, label).as_posix()


def _resolve_run_dir(root: Path, value: str, label: str) -> tuple[str, Path]:
    """验证 RunId 是根目录内的现存目录并返回规范路径。"""
    relative = _normalize_run_rel(value, label)
    run_dir = _resolve_confined_path(root, relative, f"{label} 源目录", must_exist=True)
    if not run_dir.is_dir():
        raise ValueError(f"{label} 必须是根目录内的目录：{run_dir}")
    return relative, run_dir


def _resolve_confined_path(root: Path, relative: str, label: str, *, must_exist: bool) -> Path:
    """解析并约束路径；调用前复验以缩小 TOCTOU 窗口，但不消除竞态。"""
    relative_path = _safe_relative_path(relative, label)
    base = root.resolve()
    candidate = base.joinpath(*relative_path.parts)
    cursor = base
    for part in relative_path.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"{label} 不允许经过符号链接：{cursor}")
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(base)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"{label} 解析后必须位于根目录内：{candidate}") from exc
    return resolved


def _state_reference_copy_plan(root: Path) -> tuple[Path, list[tuple[str, Path, str]]]:
    """校验 STATE 与其所有证据引用，并返回仅包含根内现存对象的复制计划。"""
    root = root.resolve()
    state_source = _resolve_confined_path(root, ".codex/STATE.md",
                                          "STATE 源路径", must_exist=True)
    if not state_source.is_file():
        raise ValueError("缺少项目根内的 .codex/STATE.md")
    state_text = state_source.read_text(encoding="utf-8")
    references = []
    for token in re.findall(r"`(report/evidence/[^`]+)`", state_text):
        relative = _safe_relative_path(token.rstrip("/\\"), "STATE 证据引用").as_posix()
        source = _resolve_confined_path(root, relative,
                                        f"STATE 证据源路径 {relative}", must_exist=False)
        if source.is_dir():
            _validate_source_tree(root, source, f"STATE 证据目录 {relative}")
            references.append((relative, source, "tree"))
        elif source.is_file():
            references.append((relative, source, "file"))
    return state_source, references


def _manifest_external_copy_plan(root: Path, run_rel: str, run_dir: Path) -> list[tuple[str, Path, str]]:
    """读取并校验交付清单里的根外部绑定，供隔离快照复制实际被测字节。"""
    manifest_path = _resolve_confined_path(run_dir, "delivery_manifest.json",
                                           "快照交付清单", must_exist=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ValueError("快照 delivery_manifest.files 必须为列表")
    prefix = f"{Path(run_rel).as_posix().rstrip('/')}/"
    bindings: dict[str, tuple[str, Path, str]] = {}
    for item in files:
        raw = str(item.get("path", "")).replace("\\", "/").strip()
        if not raw or raw == run_rel or raw.startswith(prefix):
            continue
        relative = _safe_relative_path(raw, "清单外部绑定路径").as_posix()
        source = _resolve_confined_path(root, relative,
                                        f"清单外部绑定 {relative}", must_exist=True)
        if not source.is_file():
            raise ValueError(f"清单外部绑定不是文件：{relative}")
        data = source.read_bytes()
        normalized = data.replace(b"\r\n", b"\n")
        variants = {
            hashlib.sha256(data).hexdigest(),
            hashlib.sha256(normalized).hexdigest(),
            hashlib.sha256(normalized.replace(b"\n", b"\r\n")).hexdigest(),
        }
        expected = str(item.get("sha256", "")).casefold()
        if expected not in {value.casefold() for value in variants}:
            raise ValueError(f"清单外部绑定哈希与源文件不符：{relative}")
        entry = (relative, source, "file")
        previous = bindings.get(relative)
        if previous and (previous[1].resolve() != source.resolve() or previous[2] != "file"):
            raise ValueError(f"清单重复绑定路径来源冲突：{relative}")
        bindings[relative] = entry
    return [bindings[key] for key in sorted(bindings)]


def _validate_source_tree(root: Path, source: Path, label: str) -> None:
    """确认待复制目录中的每个条目都位于源根内且不经过符号链接。"""
    base = root.resolve()
    for current, directories, files in os.walk(source, followlinks=False):
        for name in directories + files:
            item = Path(current) / name
            relative = item.relative_to(base).as_posix()
            _resolve_confined_path(base, relative, label, must_exist=True)


def _normalize_s6a_run_rel(value: str) -> str:
    """把 S6-A RunId 限制在约定目录，并返回仓库相对 POSIX 路径。"""
    relative = _safe_relative_path(value, "S6-A RunId")
    prefix = Path("report/evidence/S6-A")
    if relative.parts[:len(prefix.parts)] != prefix.parts:
        relative = prefix / relative
    if len(relative.parts) <= len(prefix.parts):
        raise ValueError("S6-A RunId 必须指向 report/evidence/S6-A 下的具体运行目录")
    return relative.as_posix()


def prepare_clean_snapshot_fixture(root: Path, s6a_run: str, fixture_parent: Path) -> tuple[Path, str, dict]:
    """在临时 Git clone 中装配源码与清单绑定的 S6-A 快照正例。"""
    source_root = root.resolve()
    run_rel = _normalize_s6a_run_rel(s6a_run)
    source_run = _resolve_confined_path(source_root, run_rel, "S6-A RunId 源路径", must_exist=True)
    if not source_run.is_dir():
        raise ValueError(f"快照正例源 RunId 不存在或不是目录：{source_run}")
    _validate_source_tree(source_root, source_run, "S6-A RunId 源条目")

    state_source = _resolve_confined_path(source_root, ".codex/STATE.md",
                                          "STATE 源路径", must_exist=True)
    if not state_source.is_file():
        raise ValueError("快照正例缺少当前 .codex/STATE.md")
    state_text = state_source.read_text(encoding="utf-8")
    copied_state_references = []
    copy_plan: list[tuple[str, Path, str]] = []
    for relative in ("verification/tool_self_tests.py", "verification/hash_convention_check.py"):
        source = _resolve_confined_path(source_root, relative,
                                        f"验证源码 {relative}", must_exist=True)
        if not source.is_file():
            raise ValueError(f"快照正例缺少当前验证源码：{relative}")
        copy_plan.append((relative, source, "file"))
    copy_plan.append((run_rel, source_run, "tree"))
    copy_plan.append((".codex/STATE.md", state_source, "file"))
    manifest_external_files = _manifest_external_copy_plan(source_root, run_rel, source_run)
    copy_plan.extend(manifest_external_files)

    for token in re.findall(r"`(report/evidence/[^`]+)`", state_text):
        relative_path = _safe_relative_path(token.rstrip("/\\"), "STATE 证据引用")
        relative = relative_path.as_posix()
        source = _resolve_confined_path(source_root, relative,
                                        f"STATE 证据源路径 {relative}", must_exist=False)
        if source.is_dir():
            _validate_source_tree(source_root, source, f"STATE 证据目录 {relative}")
            copy_plan.append((relative, source, "tree"))
            copied_state_references.append(relative)
        elif source.is_file():
            copy_plan.append((relative, source, "file"))
            copied_state_references.append(relative)

    unique_copy_plan: dict[str, tuple[str, Path, str]] = {}
    for relative, source, kind in copy_plan:
        previous = unique_copy_plan.get(relative)
        if previous and (previous[1].resolve() != source.resolve() or previous[2] != kind):
            raise ValueError(f"隔离快照重复路径来源冲突：{relative}")
        unique_copy_plan[relative] = (relative, source, kind)
    copy_plan = list(unique_copy_plan.values())

    fixture_parent = fixture_parent.resolve()
    fixture_root = fixture_parent / "project"
    try:
        fixture_root.resolve(strict=False).relative_to(fixture_parent)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("临时 Git fixture 目录必须位于指定临时父目录内") from exc
    if fixture_root.exists() or fixture_root.is_symlink():
        raise ValueError(f"临时 Git fixture 目标已存在：{fixture_root}")

    clone_exit, clone_output = run(["git", "clone", "--shared", "--no-checkout",
                                    str(source_root), str(fixture_root)], source_root)
    if clone_exit != 0:
        raise RuntimeError(f"临时 Git clone 失败：{clone_output.strip()}")
    checkout_exit, checkout_output = run(["git", "-C", str(fixture_root),
                                          "checkout", "--detach", "HEAD"], root)
    if checkout_exit != 0:
        raise RuntimeError(f"临时 Git checkout 失败：{checkout_output.strip()}")

    for key in ("core.autocrlf", "core.eol"):
        config_exit, config_value = run(["git", "-C", str(root), "config", "--get", key], root)
        if config_exit == 0 and config_value.strip():
            set_exit, set_output = run(["git", "-C", str(fixture_root), "config", key,
                                        config_value.strip()], fixture_root)
            if set_exit != 0:
                raise RuntimeError(f"设置临时 Git {key} 失败：{set_output.strip()}")

    fixture_real_root = fixture_root.resolve(strict=True)
    try:
        fixture_real_root.relative_to(fixture_parent)
    except ValueError as exc:
        raise ValueError("临时 Git clone 解析后逃逸出指定临时父目录") from exc
    destinations = []
    for relative, source, kind in copy_plan:
        destination = _resolve_confined_path(fixture_real_root, relative,
                                             f"fixture 目标路径 {relative}", must_exist=False)
        destinations.append((relative, source, kind, destination))
    for relative, source, kind, destination in destinations:
        source = _resolve_confined_path(source_root, relative,
                                        f"fixture 源路径 {relative}", must_exist=True)
        destination = _resolve_confined_path(fixture_real_root, relative,
                                             f"fixture 目标路径 {relative}", must_exist=False)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination = _resolve_confined_path(fixture_real_root, relative,
                                             f"fixture 目标路径 {relative}", must_exist=False)
        source = _resolve_confined_path(source_root, relative,
                                        f"fixture 源路径 {relative}", must_exist=True)
        if kind == "tree":
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

    seed_report = seed_fresh_claim_positive_placeholders(fixture_root, run_rel)
    package_report = prepare_claim_positive_fixture(fixture_root, run_rel, "s6a")
    add_exit, add_output = run(["git", "-C", str(fixture_root), "add", "-A"], fixture_root)
    if add_exit != 0:
        raise RuntimeError(f"暂存临时 Git fixture 失败：{add_output.strip()}")
    before_commit_exit, before_commit_status = run(
        ["git", "-C", str(fixture_root), "status", "--porcelain", "--untracked-files=all"], fixture_root)
    if before_commit_exit != 0:
        raise RuntimeError(f"读取临时 Git fixture 状态失败：{before_commit_status.strip()}")
    if before_commit_status.strip():
        commit_exit, commit_output = run(
            ["git", "-C", str(fixture_root), "-c", "user.email=selfproof@local",
             "-c", "user.name=selfproof", "commit", "--quiet", "-m",
             "clean worktree snapshot self-test fixture"], fixture_root)
        if commit_exit != 0:
            raise RuntimeError(f"临时 Git fixture 提交失败：{commit_output.strip()}")
    status_exit, status = run(
        ["git", "-C", str(fixture_root), "status", "--porcelain", "--untracked-files=all"], fixture_root)
    if status_exit != 0 or status.strip():
        raise RuntimeError(f"临时 Git fixture 未达到 clean 状态：{status.strip()}")
    commit_exit, commit = run(["git", "-C", str(fixture_root), "rev-parse", "HEAD"], fixture_root)
    if commit_exit != 0:
        raise RuntimeError(f"读取临时 Git fixture commit 失败：{commit.strip()}")
    return fixture_root, run_rel, {
        "fixture_only": True,
        "git_status": "clean",
        "fixture_commit": commit.strip(),
        "run_rel": run_rel,
        "state_reference_count": len(copied_state_references),
        "manifest_external_files": [relative for relative, _source, _kind in manifest_external_files],
        "seeded_placeholder_fixture": seed_report,
        "bound_positive_fixture": package_report,
    }


def u6_02_receipt_binding_scope_regression(root: Path, run_rel: str) -> dict:
    """确认批准回执有原始字节绑定，且扫描器仍拒绝待批准文本。"""
    import approved_package_scan

    root = root.resolve()
    run_rel, run_dir = _resolve_run_dir(root, run_rel, "U6-02 回执绑定自测 RunId")
    receipt_rel = "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json"
    receipt_path = _resolve_confined_path(root, receipt_rel, "U6-02 r07 原始回执", must_exist=True)
    if not receipt_path.is_file():
        raise ValueError("U6-02 r07 原始回执不是文件")
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes.decode("utf-8"))
    receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
    inputs_manifest = json.loads((run_dir / "inputs_manifest.json").read_text(encoding="utf-8"))
    delivery_manifest = json.loads((run_dir / "delivery_manifest.json").read_text(encoding="utf-8"))
    input_matches = [item for item in inputs_manifest.get("files", [])
                     if item.get("path") == receipt_rel and item.get("sha256") == receipt_sha
                     and item.get("role") == "input"]
    delivery_matches = [item for item in delivery_manifest.get("files", [])
                        if item.get("path") == receipt_rel and item.get("sha256") == receipt_sha
                        and item.get("role") == "input"]
    package_copy_present = (run_dir / "decision_receipt.json").exists()
    metadata_line_is_rejected = approved_package_scan.line_is_hit('"not_approved_or_not_claimed": [')
    true_pending_line_is_rejected = approved_package_scan.line_is_hit('"approval_status": "PENDING_APPROVAL"')
    approved_line_is_clean = not approved_package_scan.line_is_hit(
        '"decision_status": "APPROVED_20261025"')
    actual_hits = approved_package_scan.scan(root, run_rel)
    checks = {
        "receipt_identity_and_status": (receipt.get("run_id") == "s6a_u6_02_decision_20261025_r07"
                                         and receipt.get("decision_id") == "U6-02"
                                         and receipt.get("decision_status") == "APPROVED_20261025"),
        "inputs_manifest_raw_sha_binding": len(input_matches) == 1,
        "delivery_manifest_raw_sha_binding": len(delivery_matches) == 1,
        "no_local_receipt_copy_in_scan_scope": not package_copy_present,
        "negated_metadata_still_hits_if_scanned": metadata_line_is_rejected,
        "bad_status_line_still_hits": true_pending_line_is_rejected,
        "approved_status_remains_clean": approved_line_is_clean,
        "actual_package_scan_clean": not actual_hits,
    }
    return {
        "case_id": "u6_02_receipt_binding_scope_regression",
        "exit_code": None,
        "expected": "原始回执在 inputs/delivery 清单双重绑定；扫描器保留窄口径判定",
        "kind": "binding_and_scan_scope_regression",
        "receipt_path": receipt_rel,
        "receipt_sha256": receipt_sha,
        "checks": checks,
        "actual_package_hit_count": len(actual_hits),
        "verdict": "AS_EXPECTED" if all(checks.values()) else "UNEXPECTED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--shared-project-root", default=None,
                        help="隔离根路径回归比较的共享项目根目录；默认与 --project-root 相同")
    parser.add_argument("--run-dir", required=True, help="被检 RunId（相对 project-root；只读，全部写入走临时副本）")
    parser.add_argument("--package", choices=["s6a", "s6b"], required=True)
    parser.add_argument("--out", default="tmp/6/tool_self_tests.json")
    parser.add_argument("--s6a-run", default=None, help="S6-A 证据目录（自证必填项）")
    parser.add_argument("--s6b-run", default=None, help="S6-B 证据目录（提供时自证兼跑 S6-B 剖面）")
    parser.add_argument("--delivery-commit", default=None, help="交付提交（默认取最新冻结 tag 的父提交）")
    parser.add_argument("--delivery-s6a-run", default=None)
    parser.add_argument("--delivery-s6b-run", default=None)
    parser.add_argument("--simulate-skip", action="store_true",
                        help="必 FAIL 自测：人为把一例置为跳过，总判定必须为 INCOMPLETE_SKIPPED 且 exit 非 0")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    shared_root = Path(args.shared_project_root).resolve() if args.shared_project_root else root
    try:
        run_rel, run_dir = _resolve_run_dir(root, args.run_dir, "--run-dir")
        _validate_source_tree(root, run_dir, "--run-dir 源条目")
        s6a_value = args.s6a_run or (run_rel if args.package == "s6a" else None)
        s6b_value = args.s6b_run or (run_rel if args.package == "s6b" else None)
        if not s6a_value:
            raise ValueError("S6-A 剖面必须给出 --s6a-run（BLK-D1 之后不再隐式查找）")
        s6a_run, s6a_dir = _resolve_run_dir(root, s6a_value, "--s6a-run")
        if s6a_dir != run_dir:
            _validate_source_tree(root, s6a_dir, "--s6a-run 源条目")
        s6b_run = None
        if s6b_value:
            s6b_run, s6b_dir = _resolve_run_dir(root, s6b_value, "--s6b-run")
            if s6b_dir not in (run_dir, s6a_dir):
                _validate_source_tree(root, s6b_dir, "--s6b-run 源条目")
        delivery_s6a_value = (_normalize_run_rel(args.delivery_s6a_run, "--delivery-s6a-run")
                              if args.delivery_s6a_run else None)
        delivery_s6b_value = (_normalize_run_rel(args.delivery_s6b_run, "--delivery-s6b-run")
                              if args.delivery_s6b_run else None)
        if delivery_s6a_value:
            _resolve_confined_path(root, delivery_s6a_value,
                                   "--delivery-s6a-run 源路径", must_exist=False)
        if delivery_s6b_value:
            _resolve_confined_path(root, delivery_s6b_value,
                                   "--delivery-s6b-run 源路径", must_exist=False)
        output_rel = _normalize_run_rel(args.out, "--out")
        out_path = _resolve_confined_path(root, output_rel, "--out 输出路径", must_exist=False)
        _state_reference_copy_plan(root)
        output_relatives = {
            "delivery": "tmp/6/self_test_delivery.json",
            "snapshot": "tmp/6/self_test_snapshot.json",
            "bad_commit": "tmp/6/self_test_bad.json",
            "regression": "tmp/6/self_test_regression.json",
            "regression_missing": "tmp/6/self_test_regression_missing.json",
            "scan": "tmp/6/self_test_scan.json",
        }
        for name, relative in output_relatives.items():
            _resolve_confined_path(root, relative, f"{name} 自测输出路径", must_exist=False)
        verification_dir = _resolve_confined_path(root, "verification",
                                                  "验证源码目录", must_exist=True)
        if not verification_dir.is_dir():
            raise ValueError("项目根内的 verification 必须是目录")
        _validate_source_tree(root, verification_dir, "verification 源条目")

        delivery_selection = resolve_delivery_pair(
            root, args.delivery_commit, delivery_s6a_value, delivery_s6b_value)
        delivery = delivery_selection["commit"]
        delivery_s6a = delivery_selection["s6a_run"]
        delivery_s6b = delivery_selection["s6b_run"]
        delivery_s6a_dir = None
        delivery_s6b_dir = None
        if delivery_s6a:
            delivery_s6a, delivery_s6a_dir = _resolve_run_dir(
                root, delivery_s6a, "最终交付 S6-A RunId")
            _validate_source_tree(root, delivery_s6a_dir,
                                  "最终交付 S6-A RunId 源条目")
        if delivery_s6b:
            delivery_s6b, delivery_s6b_dir = _resolve_run_dir(
                root, delivery_s6b, "最终交付 S6-B RunId")
            if delivery_s6b_dir not in (run_dir, s6a_dir, delivery_s6a_dir):
                _validate_source_tree(root, delivery_s6b_dir,
                                      "最终交付 S6-B RunId 源条目")
    except (OSError, ValueError) as exc:
        print(f"输入路径拒绝：{type(exc).__name__}: {exc}")
        return 2
    results: list[dict] = []

    def child_output_path(name: str) -> Path:
        """在每次启动写入子进程前重新解析固定输出路径。"""
        relative = output_relatives[name]
        return _resolve_confined_path(root, relative,
                                      f"{name} 自测输出路径", must_exist=False)

    def record(case_id: str, expected_exit, got_exit, note: str, output: str,
               skipped: bool = False) -> None:
        if skipped:
            results.append({"case_id": case_id, "expected_exit": expected_exit, "exit_code": None,
                            "observable": [], "note": note, "verdict": "AS_EXPECTED", "skipped": True})
            return
        ok = (got_exit != 0) if expected_exit == "!= 0" else (got_exit == expected_exit)
        results.append({"case_id": case_id, "expected_exit": expected_exit, "exit_code": got_exit,
                        "observable": output.strip().splitlines()[-2:], "note": note,
                        "verdict": "AS_EXPECTED" if ok else "UNEXPECTED"})

    if args.package == "s6a":
        try:
            receipt_case = u6_02_receipt_binding_scope_regression(root, run_rel)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            receipt_case = {"case_id": "u6_02_receipt_binding_scope_regression",
                            "exit_code": None,
                            "expected": "原始回执有双清单绑定，扫描器保留窄口径判定",
                            "kind": "binding_and_scan_scope_regression",
                            "error": f"{type(exc).__name__}: {exc}", "verdict": "UNEXPECTED"}
        results.append(receipt_case)

    def proof_argv(extra: list[str]) -> list[str]:
        argv_ = [PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                 "--s6a-run", s6a_run]
        if s6b_run:
            argv_ += ["--s6b-run", s6b_run]
        return argv_ + extra

    pairing = delivery_pairing_regression(root)
    results.append({"case_id": "delivery_candidate_pairing_regression",
                    "expected": "固定默认已知配对；显式不完整参数不得混入默认包",
                    "exit_code": None, "kind": "selection_regression",
                    "selection_check": pairing,
                    "note": "仅检查自测用例装配规则；实际提交—证据兼容性仍由 export_selfproof 真实验证",
                    "verdict": "AS_EXPECTED" if pairing["passed"] else "UNEXPECTED"})

    hash_isolation = hash_convention_isolation_regression(root, shared_root)
    results.append({"case_id": "hash_convention_helper_uses_disposable_root",
                    "expected": "五个语义用例通过，输出仅写入临时项目根；共享输出哈希与修改时间不变",
                    "exit_code": hash_isolation["exit_code"], "kind": "filesystem_isolation_regression",
                    "isolation_check": hash_isolation,
                    "note": "子进程输出以 UTF-8 解码；对共享目标仅做前后只读快照",
                    "verdict": "AS_EXPECTED" if hash_isolation["passed"] else "UNEXPECTED"})

    # ---- 1) 只读守门：**真实调用**构建器守门函数 ----
    with tempfile.TemporaryDirectory() as tmp:
        temp_root = Path(tmp).resolve()
        probe_dir = _resolve_confined_path(temp_root, "guard_probe",
                                           "只读守门临时目录", must_exist=False)
        probe_dir.mkdir(parents=True, exist_ok=False)
        protected = _resolve_confined_path(probe_dir, "coverage_matrix.json",
                                           "只读守门临时输入", must_exist=False)
        protected.write_text('{"a": 1}', encoding="utf-8")
        sys.path.insert(0, str(verification_dir))
        import s6a_build_evidence as builder  # noqa: E402
        builder._guard_init(probe_dir)
        no_change_exit = 0
        try:
            builder._guard_check("no_change")
        except SystemExit as exc:
            no_change_exit = int(exc.code or 0)
        record("guard_no_change_must_pass", 0, no_change_exit,
               "无变化时守门不得报错（真实调用 _guard_check）", f"exit={no_change_exit}")
        protected = _resolve_confined_path(probe_dir, "coverage_matrix.json",
                                           "只读守门临时输入", must_exist=True)
        protected.write_text('{"a": 2}', encoding="utf-8")
        changed_exit = 0
        try:
            builder._guard_check("changed")
        except SystemExit as exc:
            changed_exit = int(exc.code or 0)
        record("guard_change_must_abort", "!= 0", changed_exit,
               "受保护文件被改动时守门必须中止（真实调用 _guard_check，exit 1）", f"exit={changed_exit}")

    # ---- 2) export_selfproof：交付提交 / 工作区快照 / 不可解析提交 ----
    if args.simulate_skip:
        record("selfproof_delivery_commit_must_pass", 0, 0,
               "【必 FAIL 自测】人为置为跳过（不由任何实际运行得出）", "simulated skip", skipped=True)
    elif delivery and delivery_s6a:
        argv_d = [PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                  "--commit", delivery, "--s6a-run", delivery_s6a]
        if delivery_s6b:
            argv_d += ["--s6b-run", delivery_s6b]
        argv_d += ["--out", str(child_output_path("delivery"))]
        code, out = run(argv_d, root)
        record("selfproof_delivery_commit_must_pass", 0, code,
               f"交付提交 {delivery[:10]} 自证应 exit 0（显式 --s6a-run {delivery_s6a}）", out)
    else:
        if delivery_selection["explicit"]:
            reason = ("显式提交/证据参数未组成已知候选或完整自定义配对；拒绝补入默认证据。"
                      f" selection={delivery_selection['selection']}")
        else:
            reason = (f"未找到 tag 父提交与登记证据匹配的可达候选（尝试 {[c[0] for c in DELIVERY_CANDIDATES]}）；"
                      "该例跳过后总判定必须为 INCOMPLETE_SKIPPED")
        record("selfproof_delivery_commit_must_pass", 0, 0, reason, "", skipped=True)
        results[-1]["delivery_selection"] = delivery_selection

    snapshot_fixture = {}
    try:
        with tempfile.TemporaryDirectory(prefix="s6_worktree_snapshot_fixture_") as tmp_snapshot:
            snapshot_root, snapshot_run_rel, snapshot_fixture = prepare_clean_snapshot_fixture(
                root, s6a_run, Path(tmp_snapshot))
            snapshot_out = child_output_path("snapshot")
            snapshot_argv = [PY, "-B", "verification/export_selfproof.py",
                             "--project-root", str(snapshot_root), "--s6a-run", snapshot_run_rel,
                             "--worktree-snapshot", "--out", str(snapshot_out)]
            code, out = run(snapshot_argv, snapshot_root)
            record("selfproof_worktree_snapshot_must_pass", 0, code,
                   "干净临时 Git fixture（当前验证源码 + 已绑定 S6-A 正例包）工作区快照应 exit 0", out)
            results[-1]["snapshot_fixture"] = snapshot_fixture
    except (OSError, ValueError, RuntimeError) as exc:
        record("selfproof_worktree_snapshot_must_pass", 0, 1,
               "干净临时 Git fixture（当前验证源码 + 已绑定 S6-A 正例包）工作区快照应 exit 0",
               f"fixture setup failed: {type(exc).__name__}: {exc}")
        results[-1]["snapshot_fixture"] = {"fixture_only": True,
                                            "error": f"{type(exc).__name__}: {exc}"}

    code, out = run(proof_argv(["--commit", "0000000000000000000000000000000000000000",
                                "--out", str(child_output_path("bad_commit"))]), root)
    record("selfproof_unresolvable_commit", "!= 0", code,
           "不可解析提交必须非 0（不得静默成功）", out)

    # ---- 3) claim_verify：正常 exit 0；内置假声明必 FAIL；数量/空列表必 FAIL 例在临时副本内 ----
    with tempfile.TemporaryDirectory() as tmp_claim:
        copy_root = make_temp_copy(root, run_rel, Path(tmp_claim))
        _copy_run_rel, copy_run_dir = _resolve_run_dir(copy_root, run_rel,
                                                       "claim_verify 临时 RunId")
        fixture_report = {"applicable": False}
        fixture_error = None
        if args.package == "s6a":
            try:
                seed_report = seed_fresh_claim_positive_placeholders(copy_root, run_rel)
                fixture_report = prepare_claim_positive_fixture(copy_root, run_rel, args.package)
                fixture_report["seeded_placeholder_fixture"] = seed_report
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                fixture_error = f"{type(exc).__name__}: {exc}"
                fixture_report = {"applicable": True, "fixture_only": True, "error": fixture_error}
            results.append({"case_id": "claim_positive_fixture_isolated_and_bound",
                            "expected": "marked fixture only in temp copy; both SHA bindings match",
                            "exit_code": None, "kind": "fixture_assembly_regression",
                            "fixture": fixture_report,
                            "note": "新建隔离副本以空占位种子装配；源 RunId 保持只读，通用夹具装配仍拒绝非空失配输入",
                            "verdict": "AS_EXPECTED" if fixture_error is None else "UNEXPECTED"})
        claim_args = [PY, "-B", "verification/claim_verify.py", "--package", args.package,
                      "--run-dir", run_rel, "--project-root", str(copy_root)]
        claim_exit, claim_out = run(claim_args, copy_root)
        _apx_snapshot: dict = {}
        _apx = _resolve_confined_path(copy_run_dir, "claim_verification.json",
                                      "claim_verification 输出", must_exist=False)
        if _apx.is_file():
            _apx_snapshot = json.loads(_apx.read_text(encoding="utf-8"))
        record("claim_verify_normal_must_pass", 0, claim_exit,
               f"隔离正例装配下全部声明经真实执行 VERIFIED 时 exit 0（package={args.package}；"
               "fixture 明确标记且仅在临时副本）", claim_out)
        results[-1]["claims_verified"] = claim_normal_ok(claim_exit, _apx_snapshot)
        results[-1]["claim_verification"] = _apx_snapshot
        results[-1]["fixture_only"] = args.package == "s6a"
        if args.package == "s6a":
            results[-1]["positive_fixture"] = fixture_report
        pair = _resolve_confined_path(copy_run_dir, "fresh_selfcheck_pair.json",
                                      "fresh_selfcheck_pair 输出", must_exist=False)
        if pair.is_file():
            results[-1]["fresh_selfcheck_pair"] = json.loads(pair.read_text(encoding="utf-8"))
        if not results[-1]["claims_verified"]:
            results[-1]["verdict"] = "UNEXPECTED"
        # 与真实命令分开记录：这个反例专门证明结构正确的失败声明不能被正常例接受。
        failed_claim = {"count_ok": True, "claims_declared": 1, "claims_recorded": 2,
                        "verdict": "NOT_ALL_VERIFIED", "claims": [
                            {"claim_id": "probe", "verdict": "NOT_VERIFIED", "exit_code": 1,
                             "expected_exit": 0},
                            {"claim_id": "self_test_false_claim", "verdict": "VERIFIED", "exit_code": 1}]}
        rejected = not claim_normal_ok(1, failed_claim) and not claim_normal_ok(0, failed_claim)
        results.append({"case_id": "claim_structurally_valid_failure_must_reject",
                        "expected": "REJECT", "exit_code": None, "kind": "predicate_counterexample",
                        "input": failed_claim, "rejected": rejected,
                        "note": "真实退出码 1 与不一致的退出码 0 两种输入均必须拒绝；非 subprocess 用例",
                        "verdict": "AS_EXPECTED" if rejected else "UNEXPECTED"})

        with tempfile.TemporaryDirectory() as tmp_sim:
            sim_root = make_temp_copy(root, run_rel, Path(tmp_sim))
            for _mode, _label in (("count_mismatch", "claim_count_mismatch_must_fail"),
                                  ("empty", "empty_claim_list_must_fail")):
                sim_exit, sim_out = run([PY, "-B", "verification/claim_verify.py", "--package", args.package,
                                        "--run-dir", run_rel, "--project-root", str(sim_root),
                                        "--simulate-defect", _mode], sim_root)
                _verdict_ok = '"verdict": "NOT_ALL_VERIFIED"' in sim_out.replace("'", '"')
                record(_label, "!= 0", sim_exit if _verdict_ok else 0,
                       f"人为制造 {_mode} ⇒ 必须 NOT_ALL_VERIFIED 且 exit 非 0（仅在临时副本内运行）",
                       sim_out + ("" if _verdict_ok else " [未出现 NOT_ALL_VERIFIED]"))
    false_case = next((c for c in _apx_snapshot.get("claims", [])
                       if c["claim_id"] == "self_test_false_claim"), {})
    record("claim_verify_false_claim_must_fail", "!= 0", false_case.get("exit_code", 0),
           "假声明（assert 1==2）的真实退出码必须非 0", json.dumps(false_case.get("output_tail", []), ensure_ascii=False))

    # ---- 4) m4_residual_regression（**S6-A 专用**：注入点在其人工输入内，故一律用 --s6a-run 目录）----
    reg_exit, reg_out = run([PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                             "--run-dir", s6a_run, "--out", str(child_output_path("regression"))], root)
    record("regression_residuals_must_be_caught", 0, reg_exit,
           "3 条真实残留行注入后 C16 必须 FAIL（脚本判定 ALL_AS_EXPECTED）", reg_out)
    missing_exit, missing_out = run([PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                                     "--run-dir", _normalize_run_rel("report/evidence/S6-A/__not_a_run__",
                                                                     "missing-run negative case"),
                                     "--out", str(child_output_path("regression_missing"))], root)
    record("regression_missing_run_must_refuse", "!= 0", missing_exit,
           "run-dir 不存在时必须拒绝运行（fail-closed）", missing_out)

    # ---- 5) approved_package_scan：两向自测（B1..B7 必命中 / C1..C4 必放行）----
    scan_exit, scan_out = run([PY, "-B", "verification/approved_package_scan.py", "--project-root", str(root),
                               "--run-dir", run_rel, "--inject-self-test",
                               "--out", str(child_output_path("scan"))], root)
    record("approval_scan_counterexamples_must_fail", 0, scan_exit,
           "B1..B7 必判失败形态全部被捕获、C1..C4 必须放行对照全部不命中（exit 0 = AS_EXPECTED）", scan_out)

    unexpected = [c["case_id"] for c in results if c["verdict"] != "AS_EXPECTED"]
    skipped = [c["case_id"] for c in results if c.get("skipped")]
    verdict = ("UNEXPECTED" if unexpected else
               "INCOMPLETE_SKIPPED" if skipped else "ALL_AS_EXPECTED")

    payload = {
        "schema_version": 1,
        "artifact": "tool_self_tests",
        "task_id": "S6-A" if args.package == "s6a" else "S6-B",
        "run_id": run_dir.name,
        "package": args.package,
        "rule": ("每个验证工具必须同时给出**必 PASS**与**必 FAIL**两侧用例；任一侧不符合预期即不得冻结。"
                 "**跳过（skipped）不得计绿**：存在跳过时总判定为 INCOMPLETE_SKIPPED 且退出码非 0。"
                 "（教训：合成退出码 / 换行假阴性 / 守门作用域 / 空转 skipped / 缺 --s6a-run 数次工具自身出错，"
                 "均因只有一侧被验证过。）"),
        "cases": results,
        "unexpected": unexpected,
        "skipped_cases": skipped,
        "verdict": verdict,
    }
    out_path = _resolve_confined_path(root, output_rel, "--out 输出路径", must_exist=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path = _resolve_confined_path(root, output_rel, "--out 输出路径", must_exist=False)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "cases": [(c["case_id"], c["exit_code"], c["verdict"], bool(c.get("skipped")))
                                for c in results]}, ensure_ascii=False))
    if args.simulate_skip:
        as_expected = verdict == "INCOMPLETE_SKIPPED"
        print(json.dumps({"simulate_skip_verdict": verdict, "as_expected": as_expected}, ensure_ascii=False))
        return 0 if as_expected else 1
    return 0 if verdict == "ALL_AS_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
