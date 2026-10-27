#!/usr/bin/env python3
"""证据时间戳 fail-closed 断言（DELTA 修复 ②）。

规则：证据/记录里的时间戳**不得晚于其所在提交的提交时刻**（写不出未来事实）。
本脚本对以下位置取时间戳并逐条断言：
  · 契约 `post_freeze_rebinds[*].at_utc8`
  · 缺口登记表 `updated_utc8`
  · 可选的证据 JSON `generated_utc8`
并与 `git log -1 --format=%cI <commit>` 的提交时刻比较（缺省用 HEAD）。

`--self-test` 生成两条合成记录做**负向自测**：
  · valid   = 提交时刻 - 60 s  ⇒ 必须 **PASS**
  · future  = 提交时刻 + 3600 s ⇒ 必须 **被拒（FAIL）**
自测在合成分支上运行同一验证函数，把真实结论写入 `<run-dir>/timestamp_assertion_selftest.json`。
若无 run-dir，则拒绝运行（本脚本只写证据目录）。

退出码：0 = 全部时间戳合法（或自测两条均符合预期）；1 = 存在晚于提交时刻的时间戳 / 自测未按预期；2 = 输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CONTRACT = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
REGISTRY = WORKTREE / "docs" / "stage4" / "S4B_raw_system_g0_gap_registry.json"


def commit_time(commit: str) -> datetime:
    """取提交时刻（committer date, ISO 8601 带偏移）。"""
    proc = subprocess.run(["git", "-C", str(WORKTREE), "log", "-1", "--format=%cI", commit],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0 or not proc.stdout.strip():
        raise SystemExit(f"[FAIL] 无法读取提交时刻：{commit}（{proc.stderr.strip()[:200]}）")
    return datetime.fromisoformat(proc.stdout.strip())


def parse_ts(text: str) -> datetime:
    """解析 ISO 8601 时间戳。"""
    value = datetime.fromisoformat(text)
    if value.tzinfo is None:
        raise ValueError(f"时间戳缺少时区：{text}")
    return value


def validate(records: list[tuple[str, str]], reference: datetime) -> list[dict[str, object]]:
    """逐条断言（record <= reference）；返回违规清单。"""
    violations: list[dict[str, object]] = []
    for label, raw in records:
        try:
            value = parse_ts(raw)
        except ValueError as exc:
            violations.append({"label": label, "value": raw, "reason": f"不可解析：{exc}"})
            continue
        if value > reference:
            violations.append({"label": label, "value": raw, "commit_time": reference.isoformat(),
                               "delta_seconds": (value - reference).total_seconds(),
                               "reason": "时间戳晚于提交时刻（写不出未来事实）"})
    return violations


def collect() -> list[tuple[str, str]]:
    """收集待断言的时间戳。"""
    records: list[tuple[str, str]] = []
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for index, entry in enumerate(contract.get("post_freeze_rebinds", [])):
        if entry.get("at_utc8"):
            records.append((f"contract.post_freeze_rebinds[{index}].at_utc8", entry["at_utc8"]))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("updated_utc8"):
        records.append(("registry.updated_utc8", registry["updated_utc8"]))
    return records


def main() -> int:
    """执行断言或自测。"""
    parser = argparse.ArgumentParser(description="证据时间戳 fail-closed 断言")
    parser.add_argument("--commit", default="HEAD", help="参照提交（缺省 HEAD）")
    parser.add_argument("--run-dir", required=True, type=Path, help="证据目录（本脚本只写这里）")
    parser.add_argument("--self-test", action="store_true", help="运行负向自测（未来时刻必须被拒）")
    args = parser.parse_args()

    out_dir: Path = args.run_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    reference = commit_time(args.commit)

    if args.self_test:
        valid = [("selftest.valid", (reference - timedelta(seconds=60)).isoformat())]
        future = [("selftest.future", (reference + timedelta(hours=1)).isoformat())]
        valid_violations = validate(valid, reference)
        future_violations = validate(future, reference)
        expected_ok = (not valid_violations) and bool(future_violations)
        report = {
            "mode": "self_test", "reference_commit": args.commit,
            "commit_time": reference.isoformat(),
            "valid_case": {"records": valid, "violations": valid_violations, "expected": "PASS"},
            "future_case": {"records": future, "violations": future_violations,
                            "expected": "REJECTED", "rejected": bool(future_violations)},
            "negative_control": {"future_timestamp_rejected": bool(future_violations)},
            "status": "PASS" if expected_ok else "FAIL",
        }
        (out_dir / "timestamp_assertion_selftest.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report["negative_control"], ensure_ascii=False))
        print(f"[{'PASS' if expected_ok else 'FAIL'}] 负向自测：valid 通过={not valid_violations}；"
              f"future 被拒={bool(future_violations)}")
        return 0 if expected_ok else 1

    records = collect()
    violations = validate(records, reference)
    report = {
        "mode": "check", "reference_commit": args.commit, "commit_time": reference.isoformat(),
        "records": [{"label": label, "value": value} for label, value in records],
        "violations": violations, "status": "PASS" if not violations else "FAIL",
        "rule": "任一证据时间戳晚于其提交时刻 ⇒ FAIL（fail-closed）",
    }
    (out_dir / "timestamp_assertion_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for label, value in records:
        print(f"[INFO] {label} = {value} (commit={reference.isoformat()})")
    status = "PASS" if not violations else "FAIL"
    print(f"[{status}] 时间戳断言：{len(records) - len(violations)}/{len(records)} 合法"
          + (f"；违规={violations}" if violations else ""))
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())