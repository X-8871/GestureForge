#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段5 离线 replay/display JSON 契约校验器（只读；不联网、不接板卡）。

用法
====
    python -B scripts/stage5_t03/validate_s5t03_json.py --package report/evidence/S5-T03/<run_id> [...]
    python -B scripts/stage5_t03/validate_s5t03_json.py --packages-from <文件>   # 每行一个包路径

判定（v1.0.1，关闭 JSON 契约专项复审 B1–B6）
============================================
- B1：逐帧校验 **stable 必需子集**（`frame_assertion_stable_required`），不是只查 `frame_assertion_required`；
- B2：`results.schema_version` 的**值**必须等于对应 `artifact_kinds[kind].schema_version`（乱填/升版即违约）；
- B3：`manifest.files[].sha256` **实测**文件内容；且盘上不得有未列入文件（`manifest.json` 自身除外）；
- B4：`checks.passed` 必须为 `true` 且与 `failures` 自洽（失败运行不得作为交付证据）；
- B5：契约本体缺键 ⇒ **fail-closed 退出码 2**（不再静默放过，也不崩成 1）；
- B6：退出码语义固定：0=全部通过 / 1=违约 / 2=输入或环境错误（契约缺失或不完整、包目录不存在、
  `--packages-from` 文件不存在、未指定包）。
- 另加交叉一致性：`manifest.run_id / source_commit / schema_version` 必须与 `results.json` 一致。

限制：本工具**只证明结构契约与文件哈希**，不代表接口语义正确、测试成功、独立审查通过或 G0/G4/G5。
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_json_contract_v1.json"
MAX_ERRORS_PER_PACKAGE = 12


class ContractError(Exception):
    """输入或环境错误 ⇒ 退出码 2。"""


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract(path: pathlib.Path = CONTRACT_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError(f"契约文件不存在：{path}")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"契约文件不是合法 JSON：{exc}") from exc
    # B5：契约自身必须 fail-closed —— 必填键（含契约自声明的 contract_required_keys）
    required = contract.get("contract_required_keys")
    if not isinstance(required, list) or not required:
        raise ContractError("契约缺 contract_required_keys（无法自证完整性）")
    missing = [key for key in required if key not in contract]
    if missing:
        raise ContractError(f"契约缺必填键：{missing}")
    for name, spec in contract["artifact_kinds"].items():
        for key in ("schema_version", "requires_frame_assertions", "required_results", "detect"):
            if key not in spec:
                raise ContractError(f"契约 artifact_kinds.{name} 缺 {key}")
        if not isinstance(spec["schema_version"], str) or not spec["schema_version"]:
            raise ContractError(f"契约 artifact_kinds.{name}.schema_version 必须是非空字符串")
    for key in ("stable_for_consumers", "detail_not_for_consumers", "unclassified_policy"):
        if key not in contract["stability"]:
            raise ContractError(f"契约 stability 缺 {key}")
    return contract


def infer_kind(results: dict[str, Any], contract: dict[str, Any]) -> str:
    """按契约声明的 detect 语义判定产物种类；无法判定即违约（不默认成某一类）。"""
    if "geometries" in results:
        return "multi_geometry_render"
    if "invariants" in results:
        return "long_run_replay"
    if "counters" in results:
        return "replay_display"
    raise ValueError(f"无法判定产物种类（keys={sorted(results)[:8]}…）；契约种类："
                     f"{sorted(contract['artifact_kinds'])}")


def check_results(results: dict[str, Any], contract: dict[str, Any]) -> tuple[str, list[str]]:
    errs = [f"results 缺公共字段 {key}" for key in contract["results_required_common"] if key not in results]
    checks = results.get("checks")
    if not isinstance(checks, dict) or not isinstance(checks.get("passed"), bool) or \
            not isinstance(checks.get("failures"), list):
        errs.append("results.checks 必须是含布尔 passed 与数组 failures 的对象")
    else:
        # B4：失败运行不得作为交付证据；passed 必须与 failures 自洽
        if checks["passed"] is not True:
            errs.append("results.checks.passed 必须为 true（失败运行不得作为交付证据）")
        if bool(checks["failures"]) == bool(checks["passed"]):
            errs.append("results.checks.passed 与 failures 不自洽")
    kind = infer_kind(results, contract)
    spec = contract["artifact_kinds"][kind]
    errs += [f"results[{kind}] 缺字段 {key}" for key in spec["required_results"] if key not in results]
    # B2：schema_version 的**值**必须匹配
    expected = spec["schema_version"]
    if results.get("schema_version") != expected:
        errs.append(f"results.schema_version 应为 {expected}（实为 {results.get('schema_version')!r}）")
    if "counters" in results:
        missing = [key for key in contract["counter_keys"] if key not in results["counters"]]
        if missing:
            errs.append(f"results.counters 缺 {len(missing)} 键：{missing}")
    for key in spec.get("required_invariants", []):
        if key not in (results.get("invariants") or {}):
            errs.append(f"results.invariants 缺 {key}")
    for key in ("limitations", "not_run"):
        if key in results and not isinstance(results[key], list):
            errs.append(f"results.{key} 必须是数组")
    if results.get("input_scope_label") != contract["input_scope_label_expected"]:
        errs.append(f"input_scope_label 应为 {contract['input_scope_label_expected']}"
                    f"（实为 {results.get('input_scope_label')!r}）")
    if results.get("status") != contract["status_label_expected"]:
        errs.append(f"status 应为 {contract['status_label_expected']}（实为 {results.get('status')!r}）")
    return kind, errs


def check_manifest(manifest: dict[str, Any], run: pathlib.Path, results: dict[str, Any] | None,
                   contract: dict[str, Any]) -> list[str]:
    errs = [f"manifest 缺字段 {key}" for key in contract["manifest_required"] if key not in manifest]
    files = manifest.get("files")
    listed: set[str] = set()
    if not isinstance(files, list):
        errs.append("manifest.files 必须是数组")
    else:
        for index, entry in enumerate(files):
            missing = [key for key in contract["manifest_files_entry_required"] if key not in entry]
            if missing:
                errs.append(f"manifest.files[{index}] 缺 {missing}")
                continue
            listed.add(entry["path"])
            # B3：实测哈希（不是只查键存在）
            target = run / entry["path"]
            if not target.is_file():
                errs.append(f"manifest.files[{index}] 指向不存在文件：{entry['path']}")
            elif sha256_file(target) != entry["sha256"]:
                errs.append(f"manifest.files[{index}] 哈希不符：{entry['path']}")
    on_disk = {p.relative_to(run).as_posix() for p in run.rglob("*")
               if p.is_file() and p.name != "manifest.json"}
    unlisted = sorted(on_disk - listed)
    if unlisted:
        errs.append(f"盘上有未列入 manifest.files[] 的文件：{unlisted[:5]}")
    tools = manifest.get("tools")
    if not isinstance(tools, dict) or not tools:
        errs.append("manifest.tools 必须是非空 role→对象映射")
    else:
        for role, entry in tools.items():
            if not isinstance(entry, dict) or "path" not in entry or "sha256" not in entry:
                errs.append(f"manifest.tools.{role} 必须是含 path/sha256 的对象")
    if results is not None:
        for key in ("run_id", "source_commit", "schema_version"):
            if manifest.get(key) != results.get(key):
                errs.append(f"manifest.{key} 与 results.{key} 不一致"
                            f"（{manifest.get(key)!r} vs {results.get(key)!r}）")
    return errs


def check_frame_assertions(path: pathlib.Path, contract: dict[str, Any]) -> tuple[int, list[str]]:
    errs: list[str] = []
    required = contract["frame_assertion_required"]
    stable = contract["frame_assertion_stable_required"]
    opener = (lambda: gzip.open(path, "rt", encoding="utf-8")) if path.suffix == ".gz" else \
             (lambda: open(path, encoding="utf-8"))
    count = 0
    with opener() as handle:
        for line in handle:
            if not line.strip():
                continue
            count += 1
            if len(errs) < MAX_ERRORS_PER_PACKAGE:
                frame = json.loads(line)
                errs += [f"frame[{count}] 缺必需字段 {key}" for key in required if key not in frame]
                # B1：stable 必需子集同样要查
                errs += [f"frame[{count}] 缺 stable 必需字段 {key}" for key in stable
                         if key not in frame and key not in required]
    return count, errs


def validate_package(run: pathlib.Path, contract: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {"run_id": run.name, "errors": [], "counts": {}}
    if not run.is_dir():
        raise ContractError(f"包目录不存在：{run}")
    results: dict[str, Any] | None = None
    results_path = run / "results.json"
    if results_path.is_file():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        try:
            kind, errs = check_results(results, contract)
        except ValueError as exc:
            kind, errs = None, [str(exc)]
        report["kind"] = kind
        report["errors"] += errs
    else:
        report["errors"].append("缺 results.json")
    manifest_path = run / "manifest.json"
    if manifest_path.is_file():
        report["errors"] += check_manifest(json.loads(manifest_path.read_text(encoding="utf-8")),
                                           run, results, contract)
    else:
        report["errors"].append("缺 manifest.json")
    plain = run / "frame_assertions.jsonl"
    gzipped = run / "frame_assertions.jsonl.gz"
    needs = contract["artifact_kinds"][report.get("kind")]["requires_frame_assertions"] \
        if report.get("kind") else True
    if gzipped.is_file() or plain.is_file():
        count, errs = check_frame_assertions(gzipped if gzipped.is_file() else plain, contract)
        report["counts"]["frame_assertions"] = count
        report["errors"] += errs
    elif needs:
        report["errors"].append("缺 frame_assertions.jsonl(.gz)（该种类要求逐帧断言）")
    report["ok"] = not report["errors"]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="阶段5 JSON 契约校验器（只读）")
    parser.add_argument("--package", action="append", default=[], help="包目录（可重复）")
    parser.add_argument("--packages-from", default=None, help="文件：每行一个包目录")
    parser.add_argument("--contract", default=str(CONTRACT_PATH))
    args = parser.parse_args(argv)
    try:
        contract = load_contract(pathlib.Path(args.contract))
        targets = [pathlib.Path(p) for p in args.package]
        if args.packages_from:
            listing = pathlib.Path(args.packages_from)
            if not listing.is_file():
                raise ContractError(f"--packages-from 文件不存在：{listing}")
            targets += [pathlib.Path(line.strip()) for line in
                        listing.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not targets:
            raise ContractError("未指定任何包（--package / --packages-from）")
        for target in targets:
            run = target if target.is_absolute() else REPO_ROOT / target
            if not run.is_dir():
                raise ContractError(f"包目录不存在：{run}")
        reports = [validate_package(target if target.is_absolute() else REPO_ROOT / target, contract)
                   for target in targets]
    except ContractError as exc:
        print(f"[contract] 环境错误（退出码 2）：{exc}")
        return 2
    failed = 0
    for report in reports:
        status = "OK  " if report["ok"] else "FAIL"
        print(f"{status} {report['run_id']:48s} kind={report.get('kind')} "
              f"frames={report['counts'].get('frame_assertions')} errors={report['errors'][:3]}")
        failed += 0 if report["ok"] else 1
    print(f"contract={contract['contract_id']} v{contract['contract_version']} "
          f"packages={len(reports)} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())