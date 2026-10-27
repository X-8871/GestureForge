#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 阶段4 冻结包**完整性复算**器（只读消费前置，不进显示语义）。

职责（严格按冻结件原文要求）
============================
1. **逐文件复算**：对冻结记录 `files[]` 的每个文件现场复算 `sha256` 与 `bytes`，
   **任一不符即拒绝消费**（不得只校验 package.json 一个文件）。
2. **契约绑定复算**：现场复算契约 JSON/MD 的 SHA-256，与冻结记录的
   `contract_binding.json_sha256` / `md_sha256` 逐字比对。
3. **漂移检测（契约 `authority_rules.drift_detection`）**：现场复算契约 `upstream_bindings`
   的每条 SHA-256。跨树条目按条目 `byte_basis` 解析所属工作树：
   - `git_blob_content`：`git -C <所属工作树> cat-file blob <rev>:<rel>`（`rev` 取条目
     `fixed_revision`，缺省 `HEAD`）；**绝不在别的树里取 blob**（会得到空输入哈希
     `e3b0c442…` 并伪报漂移——已知陷阱，本模块对 blob 读取失败显式记 FAIL，不把空哈希当值）；
   - `worktree_disk_bytes`（默认）：按文件原始字节复算。

诚实边界
========
本模块只证明**文件字节与绑定字符串一致**，不证明接口语义正确、测试通过、独立审查通过，
也不证明板上行为、UART 实收、真实采集质量或任何 G0/G1/G3/G4/G5 关口。
只读：不写上游工作树，不修改任何证据目录。

退出码：0 = 全部 PASS；1 = 存在 FAIL/被拒消费；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any, Mapping

SCHEMA_VERSION = "gestureforge_s5t03_freeze_integrity_v1"
DEFAULT_BASIS = "worktree_disk_bytes"
BLOB_BASIS = "git_blob_content"
EXPECTED_CONTRACT_SHA256 = "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class EnvironmentError5T03(RuntimeError):
    """输入缺失/路径不可读（退出码 2），不得与判定 FAIL 混同。"""


class FrozenPackageRejected(RuntimeError):
    """冻结包完整性不符：消费方必须拒绝消费（fail-closed）。"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    return sha256_bytes(pathlib.Path(path).read_bytes())


def worktree_root(path: pathlib.Path) -> pathlib.Path | None:
    """向上找到含 `.git`（文件或目录，兼容 linked worktree）的树根。"""
    current = pathlib.Path(path)
    current = current if current.is_dir() else current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def git_blob_sha256(tree: pathlib.Path, revision: str, rel: str) -> tuple[str | None, str | None]:
    """在**指定工作树**里取 `<rev>:<rel>` 的 blob 原始字节并复算 SHA-256。

    返回 `(sha256, None)` 或 `(None, 错误说明)`；**不返回空输入哈希**以免掩盖失败。
    """
    proc = subprocess.run(["git", "-C", str(tree), "cat-file", "blob", f"{revision}:{rel}"],
                          capture_output=True)
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip()[:200]
        return None, f"git_blob_read_failed(exit={proc.returncode}): {detail}"
    data = proc.stdout
    if not data:
        return None, "git_blob_empty(空 blob：路径在该修订下不存在或为空，不得当作有效绑定)"
    return sha256_bytes(data), None


def resolve_binding_path(raw_path: str, contract_tree: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(raw_path)
    return path if path.is_absolute() else (contract_tree / path)


def recompute_upstream_bindings(contract: Mapping[str, Any],
                                contract_tree: pathlib.Path) -> dict[str, Any]:
    """现场复算 `upstream_bindings` 全部条目（契约 `authority_rules.drift_detection`）。"""
    default_basis = str(contract.get("binding_byte_basis", {}).get("default_basis", DEFAULT_BASIS))
    entries: list[dict[str, Any]] = []
    for binding in contract.get("upstream_bindings", []):
        binding_id = str(binding.get("id"))
        raw_path = str(binding.get("path"))
        basis = str(binding.get("byte_basis") or default_basis)
        expected = str(binding.get("sha256"))
        resolved = resolve_binding_path(raw_path, contract_tree)
        record: dict[str, Any] = {
            "id": binding_id, "declared_path": raw_path, "resolved_path": str(resolved),
            "byte_basis": basis, "expected_sha256": expected,
        }
        if not resolved.is_file():
            record.update({"verdict": "FAIL", "actual_sha256": None,
                           "reason": "path_not_found（绑定路径不存在，不得静默跳过）"})
            entries.append(record)
            continue
        if basis == BLOB_BASIS:
            tree = worktree_root(resolved)
            if tree is None:
                record.update({"verdict": "FAIL", "actual_sha256": None,
                               "reason": "no_worktree_root（无法定位所属工作树）"})
                entries.append(record)
                continue
            revision = str(binding.get("fixed_revision") or "HEAD")
            rel = resolved.resolve().relative_to(tree.resolve()).as_posix()
            actual, error = git_blob_sha256(tree, revision, rel)
            record.update({"git_tree": str(tree), "git_revision": revision, "git_rel_path": rel})
            if error is not None:
                record.update({"verdict": "FAIL", "actual_sha256": actual, "reason": error})
            else:
                record.update({"verdict": "PASS" if actual == expected else "FAIL",
                               "actual_sha256": actual,
                               "reason": None if actual == expected else "sha256_mismatch"})
                annotation = binding.get("worktree_disk_sha256_annotation")
                if annotation is not None:
                    record["worktree_disk_sha256_annotation"] = str(annotation)
                    record["worktree_disk_annotation_role"] = "注记，不参与校验（blob 口径为准）"
        else:
            actual = sha256_file(resolved)
            record.update({"verdict": "PASS" if actual == expected else "FAIL", "actual_sha256": actual,
                           "reason": None if actual == expected else "sha256_mismatch"})
        entries.append(record)
    checked = len(entries)
    ok = sum(1 for entry in entries if entry["verdict"] == "PASS")
    return {"checked": checked, "ok": ok, "fail": checked - ok,
            "all_pass": checked > 0 and ok == checked, "entries": entries,
            "rule": "契约 authority_rules.drift_detection：现场复算，任一不符即 FAIL"}


def verify_package_files(package_dir: pathlib.Path,
                         freeze_record: Mapping[str, Any]) -> dict[str, Any]:
    """逐文件复算 sha256 与 bytes；任一不符即整体 FAIL（拒绝消费）。"""
    package_dir = pathlib.Path(package_dir)
    if not package_dir.is_dir():
        raise EnvironmentError5T03(f"冻结包目录不存在：{package_dir}")
    listed = list(freeze_record.get("files", []))
    if not listed:
        raise EnvironmentError5T03("冻结记录 files[] 为空：无法逐文件复算，拒绝消费")
    records: list[dict[str, Any]] = []
    for item in listed:
        name = str(item.get("path"))
        target = package_dir / name
        expected_sha, expected_bytes = str(item.get("sha256")), item.get("bytes")
        if not target.is_file():
            records.append({"path": name, "verdict": "FAIL", "reason": "file_missing",
                            "expected_sha256": expected_sha, "expected_bytes": expected_bytes})
            continue
        actual_bytes = target.stat().st_size
        actual_sha = sha256_file(target)
        same_sha = actual_sha == expected_sha
        same_bytes = (expected_bytes is not None) and int(actual_bytes) == int(expected_bytes)
        records.append({"path": name,
                        "verdict": "PASS" if (same_sha and same_bytes) else "FAIL",
                        "expected_sha256": expected_sha, "actual_sha256": actual_sha,
                        "expected_bytes": expected_bytes, "actual_bytes": actual_bytes,
                        "sha256_match": same_sha, "bytes_match": same_bytes,
                        "reason": None if (same_sha and same_bytes)
                        else ("sha256_mismatch" if not same_sha else "bytes_mismatch")})
    actual_names = {r["path"] for r in records}
    missing_extra = [str(n) for n in freeze_record.get("missing_files", [])]
    unlisted = sorted(p.name for p in package_dir.iterdir()
                      if p.is_file() and p.name not in actual_names)
    ok = sum(1 for entry in records if entry["verdict"] == "PASS")
    return {
        "package_dir": str(package_dir), "checked": len(records), "ok": ok,
        "fail": len(records) - ok, "all_pass": ok == len(records),
        "records": records, "unlisted_files_in_dir": unlisted,
        "declared_missing_files": missing_extra,
        "rule": "冻结件 integrity_rule：逐文件复算 sha256 与 bytes；任一不符即拒绝消费",
    }


def verify_contract_binding(freeze_record: Mapping[str, Any],
                            contract_json: pathlib.Path) -> dict[str, Any]:
    """现场复算契约 JSON/MD 的 SHA-256，与冻结记录 contract_binding 比对。"""
    binding = freeze_record.get("contract_binding", {})
    contract_json = pathlib.Path(contract_json)
    if not contract_json.is_file():
        raise EnvironmentError5T03(f"契约 JSON 不存在：{contract_json}")
    actual_json = sha256_file(contract_json)
    expected_json = str(binding.get("json_sha256"))
    contract_md = contract_json.with_suffix(".md")
    actual_md = sha256_file(contract_md) if contract_md.is_file() else None
    expected_md = str(binding.get("md_sha256")) if binding.get("md_sha256") else None
    json_ok = actual_json == expected_json
    md_ok = (actual_md is not None) and (expected_md is not None) and actual_md == expected_md
    return {
        "contract_json_path": str(contract_json),
        "json_expected_sha256": expected_json, "json_actual_sha256": actual_json,
        "json_match": json_ok,
        "json_matches_frozen_offline_reference": actual_json == EXPECTED_CONTRACT_SHA256,
        "contract_md_path": str(contract_md), "md_expected_sha256": expected_md,
        "md_actual_sha256": actual_md, "md_match": md_ok,
        "declared_contract_id": binding.get("contract_id"),
        "declared_contract_version": binding.get("contract_version"),
        "declared_status": binding.get("status"),
        "all_pass": json_ok and md_ok,
    }


def verify_all(*, freeze_record_path: pathlib.Path, package_dir: pathlib.Path,
               contract_json: pathlib.Path, drift: bool = True) -> dict[str, Any]:
    """一次跑齐：逐文件复算 + 契约绑定复算 + 漂移复算。"""
    freeze_record_path = pathlib.Path(freeze_record_path)
    if not freeze_record_path.is_file():
        raise EnvironmentError5T03(f"冻结记录不存在：{freeze_record_path}")
    freeze_record = json.loads(freeze_record_path.read_text(encoding="utf-8"))
    contract_json = pathlib.Path(contract_json)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "freeze_record_path": str(freeze_record_path),
        "freeze_record_sha256": sha256_file(freeze_record_path),
        "freeze_record_run_id": freeze_record.get("run_id"),
        "package_identity": freeze_record.get("package_identity"),
        "declared_consumption_mode": freeze_record.get("consumption_mode"),
        "file_integrity": verify_package_files(package_dir, freeze_record),
        "contract_binding_check": verify_contract_binding(freeze_record, contract_json),
    }
    if drift:
        contract = json.loads(contract_json.read_text(encoding="utf-8"))
        contract_tree = worktree_root(contract_json) or contract_json.parent
        result["contract_tree"] = str(contract_tree)
        result["upstream_binding_drift"] = recompute_upstream_bindings(contract, contract_tree)
    else:
        result["upstream_binding_drift"] = {"skipped": True, "all_pass": True, "checked": 0, "ok": 0, "entries": []}
    result["consumable"] = bool(result["file_integrity"]["all_pass"]
                                and result["contract_binding_check"]["all_pass"]
                                and result["upstream_binding_drift"]["all_pass"])
    result["verdict"] = "CONSUMABLE_OFFLINE_REPLAY_ONLY" if result["consumable"] else "REJECTED"
    result["limits"] = [
        "本复算只证明文件字节与绑定字符串一致；不证明接口语义、测试、独立审查或任何关口。",
        "跨树条目按条目 byte_basis 在所属工作树复算；在别的树取 blob 会得到空输入哈希，本器显式记 FAIL。",
        "只读：未写上游工作树、未改任何证据目录。",
    ]
    return result


def require_consumable(report: Mapping[str, Any]) -> None:
    """消费前置：不满足即抛（fail-closed），调用方不得自行降级。"""
    if not report.get("consumable"):
        reasons = []
        integrity = report.get("file_integrity", {})
        if not integrity.get("all_pass"):
            bad = [r["path"] for r in integrity.get("records", []) if r.get("verdict") != "PASS"]
            reasons.append(f"file_integrity FAIL: {bad}")
        contract = report.get("contract_binding_check", {})
        if not contract.get("all_pass"):
            reasons.append("contract_binding FAIL")
        drift = report.get("upstream_binding_drift", {})
        if not drift.get("all_pass"):
            bad = [e["id"] for e in drift.get("entries", []) if e.get("verdict") != "PASS"]
            reasons.append(f"upstream_binding_drift FAIL: {bad}")
        raise FrozenPackageRejected("拒绝消费阶段4 冻结包：" + "；".join(reasons))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 阶段4 冻结包完整性/漂移复算（只读）")
    parser.add_argument("--freeze-record", required=True)
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--out", default=None, help="把完整报告写到该 JSON 路径")
    parser.add_argument("--no-drift", action="store_true", help="跳过 upstream_bindings 漂移复算")
    args = parser.parse_args(argv)
    try:
        report = verify_all(freeze_record_path=pathlib.Path(args.freeze_record),
                            package_dir=pathlib.Path(args.package_dir),
                            contract_json=pathlib.Path(args.contract), drift=not args.no_drift)
    except EnvironmentError5T03 as error:
        print(f"[freeze-integrity] 环境错误（退出码 2）：{error}")
        return 2
    if args.out:
        target = pathlib.Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    integrity = report["file_integrity"]
    drift = report["upstream_binding_drift"]
    for record in integrity["records"]:
        print(f"{record['verdict']:4s} bytes/sha {record['path']} "
              f"({record.get('actual_bytes')} B, {str(record.get('actual_sha256'))[:16]}…)")
    print(f"[freeze-integrity] 文件复算 {integrity['ok']}/{integrity['checked']} PASS；"
          f"契约绑定 {'PASS' if report['contract_binding_check']['all_pass'] else 'FAIL'}；"
          f"漂移复算 {drift.get('ok')}/{drift.get('checked')} PASS；verdict={report['verdict']}")
    return 0 if report["consumable"] else 1


if __name__ == "__main__":
    sys.exit(main())