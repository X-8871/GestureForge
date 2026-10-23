#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 漂移登记扫描器（NB-2）：列出所有以**旧哈希**绑定 S5A-G0-v2 JSON 的清单，并核对是否已登记。

判据
====
- 扫描范围：`report/evidence/**/*manifest*.json`（delivery_manifest / run_manifest / 各 tamper manifest）。
- 命中条件：文件文本包含 `impacted_by_this_revision.old_hash`。
- 通过条件：命中集合 **等于** 绑定 JSON 里 `impacted_by_this_revision.entries[*].manifests` 的并集
  （既不漏登记，也不留过时登记）。
- 只读：不修改任何旧包文件。

用法（真实退出码）
==================
    python -B scripts/stage5_t03/scan_hash_drift.py [--json-out <path>]

退出码：0 = 集合一致；1 = 存在未登记或过时登记；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
BINDING_REL = "docs/stage5/s5t03_input_contract_binding_v1.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    binding_path = REPO_ROOT / BINDING_REL
    if not binding_path.is_file():
        print(f"[ERROR] 绑定文件不存在：{binding_path}", file=sys.stderr)
        return 2
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    impact = binding.get("impacted_by_this_revision")
    if not isinstance(impact, dict) or "old_hash" not in impact:
        print("[ERROR] 绑定缺少 impacted_by_this_revision.old_hash", file=sys.stderr)
        return 2
    old_hash = impact["old_hash"]
    registered = {manifest for entry in impact["entries"] for manifest in entry["manifests"]}

    found: set[str] = set()
    scanned = 0
    for path in sorted((REPO_ROOT / "report" / "evidence").rglob("*manifest*.json")):
        if not path.is_file():
            continue
        scanned += 1
        if old_hash in path.read_text(encoding="utf-8", errors="replace"):
            found.add(path.relative_to(REPO_ROOT).as_posix())

    unregistered = sorted(found - registered)
    stale = sorted(registered - found)
    ok = not unregistered and not stale
    result = {
        "old_hash": old_hash,
        "new_hash": impact["new_hash"],
        "scanned_manifest_files": scanned,
        "found": sorted(found),
        "registered": sorted(registered),
        "unregistered": unregistered,
        "stale_registrations": stale,
        "verdict": "COVERED" if ok else "NOT_COVERED",
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())