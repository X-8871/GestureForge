#!/usr/bin/env python3
"""被绑工作树 HEAD 漂移断言（B-3 / B-r02-2，fail-closed，只读）。

## 语义（B-r02-2 定义，写入被审提交）
1. **内容权威 = blob 绑定**：契约/登记表按**路径 blob SHA-256** 绑定，**永不随 HEAD 移动而变**；
   树 HEAD 断言**只用于陈旧性检测**。
2. **每棵被绑树必须标类别**：
   - `STABLE`：被审提交内的稳定树（如 dbdf/w5/w2b）⇒ **任何 HEAD 移动即 FAIL**；
   - `MOVING_PRODUCING`：产出树自身（w4）⇒ 记录的是**产出提交的父提交/打包时刻**，其后自身移动为**预期**；
   - `MOVING_HOST_REPO`：主目录（由 DSH 高频提交）⇒ 移动为**预期**。
3. **移动属预期 ≠ 该批次仍 PASS**：按 fail-closed，任一被绑树实际 HEAD ≠ 记录值一律 **exit 1**，
   仅按类别区分**状态与补救**：
   - `FAIL_STABLE_DRIFT`：稳定树移动 ⇒ 该批次失效，须重绑、重跑、新 RunId；
   - `FAIL_MOVING_DRIFT_REBIND_REQUIRED`：预期会移动的树移动 ⇒ **必须重新核对全部 blob 绑定**并重绑重跑，
     **不得**因“移动属预期”而静默 PASS。
4. **PASS 有效窗口**：仅对**打包时刻**成立；任一 `STABLE` 树移动即失效（`validity_window` 写进结果）。

## 负向对照（B-r02-1，必须证明判别力）
`--self-test` 运行 must-fail 对照，并在**恒真变异（把比较改成恒 True）下必须变红**：
  1. 伪造 `expected_head`（翻转一位）⇒ 必须 FAIL 且**指名该树**（MOVING 与 STABLE 各一）；
  2. **非 git 目录**作为被绑树 ⇒ 必须 FAIL；
  3. `trees: []` ⇒ 必须 INPUT_ERROR；
  4. 未知类别 ⇒ fail-closed（不得因类别写错而放行）。
若任一对照未按预期变红（例如闸门被改成恒真），`--self-test` 自身返回 1 并报 `tautology_detected`。

退出码：0 = 全部被绑树与记录一致；1 = 漂移或对照失效；2 = 输入/环境错误。
本脚本不写被绑树、不访问硬件、不修改任何证据。
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))

STABLE = "STABLE"
MOVING_PRODUCING = "MOVING_PRODUCING"
MOVING_HOST_REPO = "MOVING_HOST_REPO"
KNOWN_CLASSES = (STABLE, MOVING_PRODUCING, MOVING_HOST_REPO)

CLASS_MEANING = {
    STABLE: "稳定树：任何 HEAD 移动即 FAIL（批次失效）",
    MOVING_PRODUCING: "产出树自身：记录打包时刻/父提交，其后移动为预期，但必须重核 blob 绑定",
    MOVING_HOST_REPO: "主目录：由 DSH 高频提交，移动为预期，但必须重核 blob 绑定",
}


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


def check_bound(bound: dict) -> tuple[str, list[dict], list[dict], str | None]:
    """核对一份 bound_trees 结构；返回 (status, results, drifts, input_error)。"""
    trees = bound.get("trees")
    if not isinstance(trees, list) or not trees:
        return "INPUT_ERROR", [], [], "bound_trees.trees 缺失或为空"
    results: list[dict] = []
    drifts: list[dict] = []
    stable_drift: list[str] = []
    moving_drift: list[str] = []
    for entry in trees:
        cls = entry.get("class", STABLE)
        tree = Path(entry["path"])
        expected = entry.get("expected_head")
        actual, error = git_head(tree)
        if cls not in KNOWN_CLASSES:
            status = "ERROR"
            remedy = f"未知类别 {cls!r}；必须是 {KNOWN_CLASSES} 之一（fail-closed）"
        elif actual is None:
            status = "ERROR"
            remedy = "无法读取 HEAD（fail-closed）"
        elif actual == expected:
            status = "MATCH"
            remedy = ""
        elif cls == STABLE:
            status = "DRIFT_STABLE"
            remedy = "稳定树移动 ⇒ 该批次失效：重绑、重跑、新 RunId"
            stable_drift.append(entry.get("id") or str(tree))
        else:
            status = "DRIFT_MOVING_EXPECTED"
            remedy = "移动属预期但该批次有效性窗口已过：必须重新核对全部 blob 绑定并重绑重跑（不得静默 PASS）"
            moving_drift.append(entry.get("id") or str(tree))
        record = {
            "id": entry.get("id"),
            "path": str(tree),
            "class": cls,
            "class_meaning": CLASS_MEANING.get(cls, "未知类别"),
            "expected_head": expected,
            "actual_head": actual,
            "error": error,
            "status": status,
            "remedy": remedy,
            "checked_at_utc8": now_cn(),
        }
        results.append(record)
        if status != "MATCH":
            drifts.append(record)
    if stable_drift:
        status = "FAIL_STABLE_DRIFT"
    elif moving_drift:
        status = "FAIL_MOVING_DRIFT_REBIND_REQUIRED"
    elif drifts:
        status = "FAIL_TREE_ERROR"
    else:
        status = "PASS"
    return status, results, drifts, None


def load_bound(path: Path) -> dict:
    """读取清单（bound_trees.json 或含 bound_trees 的 landing manifest）。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("bound_trees") or data


def report_for(bound: dict, manifest: Path | None, results: list[dict], drifts: list[dict], status: str) -> dict:
    """构造机器可读结果。"""
    return {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "check_bound_tree_heads",
        "checker_version": "r02",
        "status": status,
        "semantics": {
            "content_authority": "blob 绑定（按路径 blob SHA-256），永不随 HEAD 移动而变",
            "head_assertion": "仅用于陈旧性检测",
            "stable": "任何 HEAD 移动即 FAIL",
            "moving": "移动属预期，但必须重新核对全部 blob 绑定且不得静默 PASS",
            "validity_window": "PASS 仅对打包时刻成立；任一 STABLE 树移动即失效",
        },
        "fail_closed_rule": "任一被绑树实际 HEAD != 记录值 ⇒ 本批次 FAIL（按类别区分状态与补救）。",
        "manifest": str(manifest) if manifest else None,
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest() if manifest and manifest.is_file() else None,
        "recorded_utc8": bound.get("recorded_utc8"),
        "evidence_window_utc8": bound.get("evidence_window_utc8"),
        "packaging_instant_utc8": bound.get("packaging_instant_utc8"),
        "observed_at_end_utc8": now_cn(),
        "trees": results,
        "drifts": drifts,
        "blob_recheck_required": any(r["status"] in ("DRIFT_MOVING_EXPECTED", "DRIFT_STABLE") for r in results),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hardware_execution": "NOT_RUN",
        "boundary": "只读断言；不代表 G0/G4/G5 或实物验收；不对被审对象做任何写入。",
    }


def self_test(worktree: Path) -> int:
    """B-r02-1 负向对照：证明闸门有判别力（含恒真变异必须变红）。"""
    head, error = git_head(worktree)
    if head is None:
        print(f"[FAIL] 自检前置失败：{error}")
        return 2
    not_git = Path(r"C:\Windows")
    base = {
        "recorded_utc8": now_cn(),
        "packaging_instant_utc8": now_cn(),
        "trees": [
            {"id": "w4", "path": str(worktree), "expected_head": head, "class": MOVING_PRODUCING},
        ],
    }
    controls: dict[str, dict] = {}

    # 对照 0（基线）：真实清单必须 PASS
    s0, _, _, e0 = check_bound(copy.deepcopy(base))
    controls["baseline_pass"] = {
        "expected": "PASS", "actual": s0, "ok": s0 == "PASS" and e0 is None,
        "note": "真实清单必须 PASS；这是判别力的前提",
    }

    orig = base["trees"][0]["expected_head"]
    forged_value = ("0" if orig[0] != "0" else "1") + orig[1:]

    # 对照 1：MOVING 树伪造 expected_head ⇒ 必须 FAIL 且指名该树
    forged = copy.deepcopy(base)
    forged["trees"][0]["expected_head"] = forged_value
    s1, _, d1, _ = check_bound(forged)
    named = [r["id"] for r in d1]
    controls["forged_expected_head_moving"] = {
        "expected": "FAIL_MOVING_DRIFT_REBIND_REQUIRED", "actual": s1, "named_trees": named,
        "ok": s1 == "FAIL_MOVING_DRIFT_REBIND_REQUIRED" and named == ["w4"],
        "discrimination_note": "若闸门被改成恒真（ok=True），本对照会返回 PASS ⇒ 判别力丢失，自检必须变红",
    }

    # 对照 1b：STABLE 树伪造 ⇒ 必须是稳定树漂移状态
    forged_stable = copy.deepcopy(base)
    forged_stable["trees"][0]["class"] = STABLE
    forged_stable["trees"][0]["expected_head"] = forged_value
    s1b, _, _, _ = check_bound(forged_stable)
    controls["forged_expected_head_stable"] = {
        "expected": "FAIL_STABLE_DRIFT", "actual": s1b, "ok": s1b == "FAIL_STABLE_DRIFT",
    }

    # 对照 2：非 git 目录 ⇒ 必须 FAIL 且指名
    bogus = copy.deepcopy(base)
    bogus["trees"][0] = {"id": "not_git", "path": str(not_git), "expected_head": "0" * 40, "class": STABLE}
    s2, _, d2, _ = check_bound(bogus)
    controls["non_git_directory"] = {
        "expected": "FAIL_TREE_ERROR", "actual": s2, "named_trees": [r["id"] for r in d2],
        "ok": s2 == "FAIL_TREE_ERROR" and [r["id"] for r in d2] == ["not_git"],
    }

    # 对照 3：trees 为空 ⇒ 必须 INPUT_ERROR
    s3, _, _, e3 = check_bound({"trees": []})
    controls["empty_trees"] = {
        "expected": "INPUT_ERROR", "actual": s3, "error": e3, "ok": s3 == "INPUT_ERROR" and bool(e3),
    }

    # 对照 4：未知类别 ⇒ fail-closed（不得因类别写错而放行）
    unknown = copy.deepcopy(base)
    unknown["trees"][0]["class"] = "SOMETHING_ELSE"
    s4, _, _, _ = check_bound(unknown)
    controls["unknown_class"] = {"expected": "FAIL_TREE_ERROR", "actual": s4, "ok": s4 == "FAIL_TREE_ERROR"}

    all_ok = all(c["ok"] for c in controls.values())
    report = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "check_bound_tree_heads",
        "checker_version": "r02",
        "mode": "self_test",
        "status": "PASS" if all_ok else "FAIL",
        "tautology_detected": not controls["forged_expected_head_moving"]["ok"],
        "controls": controls,
        "generated_utc8": now_cn(),
        "hardware_execution": "NOT_RUN",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"[{'PASS' if all_ok else 'FAIL'}] 负向对照 {sum(1 for c in controls.values() if c['ok'])}/{len(controls)} 按预期；"
          f"恒真检出={report['tautology_detected']}")
    return 0 if all_ok else 1


def main() -> int:
    """执行漂移断言或自检。"""
    parser = argparse.ArgumentParser(description="被绑工作树 HEAD 漂移断言（fail-closed）")
    parser.add_argument("--manifest", help="含 bound_trees 的 JSON")
    parser.add_argument("--self-test", action="store_true", help="运行 B-r02-1 负向对照（判别力证明）")
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    if args.self_test:
        report_dir = Path(args.evidence_dir) if args.evidence_dir else None
        code = self_test(Path(__file__).resolve().parents[2])
        if report_dir is not None:
            report_dir.mkdir(parents=True, exist_ok=True)
            (report_dir / "bound_tree_heads_selftest_result.json").write_text(
                json.dumps({"status": "PASS" if code == 0 else "FAIL", "generated_utc8": now_cn(),
                            "exit_code": code,
                            "note": "自检明细同时打印到 stdout；此处记录状态与退出码"},
                           ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return code

    if not args.manifest:
        print("[FAIL] 必须给出 --manifest 或 --self-test")
        return 2
    path = Path(args.manifest)
    if not path.is_file():
        print(f"[FAIL] 清单不存在：{path}")
        return 2
    bound = load_bound(path)
    status, results, drifts, input_error = check_bound(bound)
    if input_error:
        print(f"[FAIL] {input_error}")
        return 2
    report = report_for(bound, path, results, drifts, status)
    if args.evidence_dir:
        out = Path(args.evidence_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "bound_tree_heads_result.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for record in results:
        print(f"[{record['status']}] {record['id']} ({record['class']}) {record['path']} "
              f"expected={record['expected_head']} actual={record['actual_head']}"
              + (f" error={record['error']}" if record["error"] else ""))
    print(f"[{status}] 被绑树 HEAD 断言：{len(results) - len(drifts)}/{len(results)} 一致"
          + (f"；漂移 {[d['id'] for d in drifts]}" if drifts else "")
          + ("；**须重核 blob 绑定并重绑重跑**" if report["blob_recheck_required"] else ""))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())