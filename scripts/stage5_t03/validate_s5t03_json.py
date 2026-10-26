#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段5 离线 replay/display JSON 契约校验器（只读；不联网、不接板卡）。

用法
====
    python -B scripts/stage5_t03/validate_s5t03_json.py --package report/evidence/S5-T03/<run_id> [...]
    python -B scripts/stage5_t03/validate_s5t03_json.py --packages-from <文件>   # 每行一个包路径

判定
====
- 依据 `docs/stage5/s5t03_json_contract_v1.json`（版本化契约，不在此硬编码字段清单）；
- 退出码：0 = 全部通过；1 = 存在违约；2 = 输入/环境错误（缺契约、缺包）。
- 本工具**只证明结构契约**，不代表接口语义正确、测试成功、独立审查通过或 G0/G4/G5。
"""

from __future__ import annotations

import argparse
import gzip
import json
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5t03_json_contract_v1.json"
MAX_FRAME_ERRORS = 5


def load_contract(path: pathlib.Path = CONTRACT_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"缺契约文件：{path}")
    contract = json.loads(path.read_text(encoding="utf-8"))
    for key in ("contract_id", "contract_version", "artifact_kinds", "counter_keys",
                "frame_assertion_required", "manifest_required"):
        if key not in contract:
            raise ValueError(f"契约缺字段 {key}")
    return contract


def infer_kind(results: dict[str, Any], contract: dict[str, Any]) -> str:
    """按契约声明的 detect 规则判定产物种类；不得靠猜。"""
    kinds = contract["artifact_kinds"]
    if "geometries" in results:
        return "multi_geometry_render"
    if "invariants" in results:
        return "long_run_replay"
    if "counters" in results:
        return "replay_display"
    raise ValueError(f"无法判定产物种类（keys={sorted(results)[:8]}…）；契约要求三选一"
                     f"：{sorted(kinds)}")


def check_results(results: dict[str, Any], contract: dict[str, Any]) -> tuple[str, list[str]]:
    errs = [f"results 缺公共字段 {key}" for key in contract["results_required_common"]
            if key not in results]
    checks = results.get("checks")
    if not isinstance(checks, dict) or "passed" not in checks or "failures" not in checks:
        errs.append("results.checks 必须含 passed/failures")
    kind = infer_kind(results, contract)
    spec = contract["artifact_kinds"][kind]
    errs += [f"results[{kind}] 缺字段 {key}" for key in spec["required_results"] if key not in results]
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


def check_manifest(manifest: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    errs = [f"manifest 缺字段 {key}" for key in contract["manifest_required"] if key not in manifest]
    files = manifest.get("files")
    if not isinstance(files, list):
        errs.append("manifest.files 必须是数组")
    else:
        for index, entry in enumerate(files):
            missing = [key for key in contract["manifest_files_entry_required"] if key not in entry]
            if missing:
                errs.append(f"manifest.files[{index}] 缺 {missing}")
                break
    tools = manifest.get("tools")
    if not isinstance(tools, dict) or not tools:
        errs.append("manifest.tools 必须是非空对象")
    return errs


def check_frame_assertions(path: pathlib.Path, contract: dict[str, Any]) -> tuple[int, list[str]]:
    errs: list[str] = []
    opener = (lambda: gzip.open(path, "rt", encoding="utf-8")) if path.suffix == ".gz" else \
             (lambda: open(path, encoding="utf-8"))
    count = 0
    with opener() as handle:
        for line in handle:
            if not line.strip():
                continue
            count += 1
            if len(errs) < MAX_FRAME_ERRORS:
                errs += [f"frame[{count}] 缺字段 {key}" for key
                         in contract["frame_assertion_required"] if key not in json.loads(line)]
    return count, errs


def validate_package(run: pathlib.Path, contract: dict[str, Any]) -> dict[str, Any]:
    report: dict[str, Any] = {"run_id": run.name, "errors": [], "counts": {}}
    if not run.is_dir():
        report["errors"].append(f"包目录不存在：{run}")
        report["ok"] = False
        return report
    results_path = run / "results.json"
    kind = None
    if results_path.is_file():
        results = json.loads(results_path.read_text(encoding="utf-8"))
        kind, errs = check_results(results, contract)
        report["kind"] = kind
        report["errors"] += errs
    else:
        report["errors"].append("缺 results.json")
    manifest_path = run / "manifest.json"
    if manifest_path.is_file():
        report["errors"] += check_manifest(json.loads(manifest_path.read_text(encoding="utf-8")), contract)
    else:
        report["errors"].append("缺 manifest.json")
    plain = run / "frame_assertions.jsonl"
    gzipped = run / "frame_assertions.jsonl.gz"
    needs = contract["artifact_kinds"][kind]["requires_frame_assertions"] if kind else True
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
    except (FileNotFoundError, ValueError) as exc:
        print(f"[contract] 环境错误：{exc}")
        return 2
    targets = [pathlib.Path(p) for p in args.package]
    if args.packages_from:
        targets += [pathlib.Path(line.strip()) for line in
                    pathlib.Path(args.packages_from).read_text(encoding="utf-8").splitlines()
                    if line.strip()]
    if not targets:
        print("[contract] 输入错误：未指定任何包（--package / --packages-from）")
        return 2
    failed = 0
    for target in targets:
        run = target if target.is_absolute() else REPO_ROOT / target
        report = validate_package(run, contract)
        status = "OK  " if report["ok"] else "FAIL"
        print(f"{status} {report['run_id']:48s} kind={report.get('kind')} "
              f"frames={report['counts'].get('frame_assertions')} errors={report['errors'][:3]}")
        failed += 0 if report["ok"] else 1
    print(f"contract={contract['contract_id']} v{contract['contract_version']} "
          f"packages={len(targets)} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())