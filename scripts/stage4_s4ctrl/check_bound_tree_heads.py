#!/usr/bin/env python3
"""被绑工作树 HEAD 漂移断言（B-3，fail-closed，只读）。

规则（由复审裁决立为规则）：
  落盘清单必须为**每个被绑树**记录期望 HEAD 提交与记录时间窗，并断言
  **实际 HEAD == 记录值**；任一不等即：
  - 该批次判定 **FAIL**（不得因为“值当时是对的”而 PASS）；
  - 输出漂移明细（记录值、实际值、观测时间）供重绑/重跑。

本脚本不写被绑树、不访问硬件、不修改任何证据。

退出码：0 = 全部被绑树 HEAD 与记录一致；1 = 存在漂移（fail-closed）；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))


def now_cn() -> str:
    """当前 UTC+8 时间戳。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def git_head(tree: Path) -> tuple[str | None, str | None]:
    """读取工作树 HEAD（只读）；返回 (head, error)。"""
    if not (tree / ".git").exists():
        return None, f"不是 git 工作树（无 .git）：{tree}"
    proc = subprocess.run(["git", "-C", str(tree), "rev-parse", "HEAD"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        return None, f"git rev-parse HEAD 退出 {proc.returncode}: {proc.stderr.strip()}"
    return proc.stdout.strip(), None


def main() -> int:
    """执行漂移断言。"""
    parser = argparse.ArgumentParser(description="被绑工作树 HEAD 漂移断言（fail-closed）")
    parser.add_argument("--manifest", required=True, help="含 bound_trees 的 JSON（bound_trees.json 或 landing manifest）")
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    path = Path(args.manifest)
    if not path.is_file():
        print(f"[FAIL] 清单不存在：{path}")
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    bound = data.get("bound_trees") or data
    trees = bound.get("trees")
    if not isinstance(trees, list) or not trees:
        print("[FAIL] 清单缺少 bound_trees.trees")
        return 2

    observed_at_start = now_cn()
    drifts: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    for entry in trees:
        tree = Path(entry["path"])
        expected = entry.get("expected_head")
        actual, error = git_head(tree)
        ok = actual is not None and actual == expected
        record = {
            "id": entry.get("id"),
            "path": str(tree),
            "expected_head": expected,
            "actual_head": actual,
            "error": error,
            "status": "MATCH" if ok else "DRIFT",
            "checked_at_utc8": now_cn(),
        }
        results.append(record)
        if not ok:
            drifts.append(record)

    status = "PASS" if not drifts else "FAIL"
    report = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "check_bound_tree_heads",
        "checker_version": "r01",
        "status": status,
        "fail_closed_rule": "任一被绑工作树实际 HEAD != 记录值 ⇒ 本批次 FAIL；必须重绑、重跑并以新 RunId 落盘真实退出码。",
        "manifest": str(path),
        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "recorded_utc8": bound.get("recorded_utc8"),
        "evidence_window_utc8": bound.get("evidence_window_utc8"),
        "observed_at_start_utc8": observed_at_start,
        "observed_at_end_utc8": now_cn(),
        "trees": results,
        "drifts": drifts,
        "python_version": sys.version,
        "platform": platform.platform(),
        "hardware_execution": "NOT_RUN",
        "boundary": "只读断言；不代表 G0/G4/G5 或实物验收。",
    }
    if args.evidence_dir:
        out = Path(args.evidence_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "bound_tree_heads_result.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for record in results:
        print(f"[{record['status']}] {record['id']} {record['path']} "
              f"expected={record['expected_head']} actual={record['actual_head']}"
              + (f" error={record['error']}" if record["error"] else ""))
    print(f"[{status}] 被绑树 HEAD 漂移断言：{len(results) - len(drifts)}/{len(results)} 一致"
          + (f"；漂移 {[d['id'] for d in drifts]}" if drifts else ""))
    return 0 if not drifts else 1


if __name__ == "__main__":
    sys.exit(main())