#!/usr/bin/env python3
"""S6-A r05 注入探针：先证明 C12/C7 的新断言能捕获缺陷，再允许 r05 出 ALL_PASS。

对 **r05 最终版** 自检脚本（verification/s6_g0_selfcheck.py）执行：

  * 基线（不注入）：必须 exit 0 / ALL_PASS —— 证明探针框架本身不引入噪声；
  * 8 个注入用例：每个都把 r05 的 JSON/样例在 **tmp 副本**里改坏一处，
    然后用同一份最终自检运行，断言 exit 1 且预期检查项（C12/C7）确实报 FAIL。

注入清单（对应第 4 轮复评的非阻断建议）：
  1. m5_window_advance_removed              N-r04-01：M5 条件回退掉「仅窗口推进帧」限定 → C12
  2. empty_predicates_used                  N-r04-03：给 M2 注入 predicates_used: [] → C12
  3. b13_predicates_used_added              N-r04-02：给 B13 注入 predicates_used（叙述不实）→ C12
  4. undeclared_predicate_name              R3-B02 回归：M8 注入未定义谓词名 → C12
  5. suppressed_release_not_window_advancing N-r04-01：去掉 suppressed_trigger_release 的窗口推进帧限定 → C12
  6. case_timeout_frame_action              N-r04-01：HC-30 预期反转成「TIMEOUT 帧产生动作」→ C7
  7. case_span_wrong                        N-r04-04：HC-29 预期跨度改成宽松口径 320 ms → C7

用法：
    python -B verification/s6a_r05_probe.py --run-dir report/evidence/S6-A/s6a_g0_20261022_r05 \
        --project-root D:/codex-worktrees/w6

退出码：0=基线与全部注入均符合预期且产物落盘；1=出现非预期结果；2=输入/环境错误。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


def _m5_remove_qualifier(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    condition = str(transitions["M5"]["condition"])
    marker = "（且本帧必须为窗口推进帧"
    if marker not in condition:
        raise RuntimeError("M5 条件中找不到窗口推进帧限定，无法注入")
    transitions["M5"]["condition"] = condition.split(marker)[0]
    return f"M5.condition 回退为无窗口推进帧限定：{transitions['M5']['condition']}"


def _empty_predicates_used(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    transitions["M2"]["predicates_used"] = []
    return "transitions.M2.predicates_used = []"


def _b13_predicates_used_added(data: dict[str, Any]) -> str:
    rows = {row["id"]: row for row in data["behavior_rows"]}
    rows["B13"]["predicates_used"] = ["TARGET_CONTINUES"]
    return "behavior_rows.B13.predicates_used = ['TARGET_CONTINUES']（叙述声明其无该字段）"


def _undeclared_predicate_name(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    transitions["M8"]["predicates_used"] = ["TARGET_LOST"]
    return "transitions.M8.predicates_used = ['TARGET_LOST']（未定义谓词）"


def _suppressed_release_removed(data: dict[str, Any]) -> str:
    release = str(data["stable_latching"]["suppressed_trigger_release"])
    if "窗口推进帧" not in release:
        raise RuntimeError("suppressed_trigger_release 中没有窗口推进帧，无法注入")
    data["stable_latching"]["suppressed_trigger_release"] = release.replace("窗口推进帧", "结果帧")
    return "stable_latching.suppressed_trigger_release 去掉「窗口推进帧」限定"


def _case_timeout_action(cases: dict[str, Any]) -> str:
    by_id = {case["case_id"]: case for case in cases["cases"]}
    expected = by_id["HC-30"]["expected"]["action_at_gate_open_frame"]
    expected["gate_opens_on_timeout"] = True
    return "HC-30.expected.action_at_gate_open_frame.gate_opens_on_timeout = true（应无动作）"


def _case_span_wrong(cases: dict[str, Any]) -> str:
    by_id = {case["case_id"]: case for case in cases["cases"]}
    by_id["HC-29"]["expected"]["window_span_ms"] = 320.0
    return "HC-29.expected.window_span_ms = 320.0（宽松序列跨度，非 §9 口径）"


INJECTIONS: list[dict[str, Any]] = [
    {"id": "baseline_no_injection", "target": None, "expect_exit": 0, "expect_check": None,
     "note": "基线：不注入，必须 ALL_PASS"},
    {"id": "m5_window_advance_removed", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _m5_remove_qualifier, "note": "N-r04-01 回归"},
    {"id": "empty_predicates_used", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _empty_predicates_used, "note": "N-r04-03"},
    {"id": "b13_predicates_used_added", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _b13_predicates_used_added, "note": "N-r04-02"},
    {"id": "undeclared_predicate_name", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _undeclared_predicate_name, "note": "R3-B02 回归"},
    {"id": "suppressed_release_not_window_advancing", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _suppressed_release_removed, "note": "N-r04-01 一致性断言"},
    {"id": "case_timeout_frame_action", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_timeout_action, "note": "N-r04-01 角落用例判别力"},
    {"id": "case_span_wrong", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_span_wrong, "note": "N-r04-04 跨度口径判别力"},
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-A r05 注入探针（证明新断言有判别力）")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--selfcheck", default="verification/s6_g0_selfcheck.py")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"运行目录不存在：{run_dir}")
        return 2
    selfcheck = (root / args.selfcheck).resolve()
    behavior = root / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
    doc = root / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
    cases_path = run_dir / "hand_computed_cases.json"
    upstream = run_dir / "upstream_bindings.json"
    for required in (selfcheck, behavior, doc, cases_path, upstream):
        if not required.is_file():
            print(f"缺少必需输入：{required}")
            return 2

    work = root / "tmp/6/S6-A" / run_dir.name / "probe"
    work.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for entry in INJECTIONS:
        case_id = entry["id"]
        json_path = behavior
        cases_file = cases_path
        injection_detail = "（无注入）"
        if entry["target"] == "json":
            data = json.loads(behavior.read_text(encoding="utf-8"))
            injection_detail = entry["apply"](data)
            json_path = work / f"{case_id}_behavior.json"
            json_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        elif entry["target"] == "cases":
            data = json.loads(cases_path.read_text(encoding="utf-8"))
            injection_detail = entry["apply"](data)
            cases_file = work / f"{case_id}_cases.json"
            cases_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

        result_path = work / f"{case_id}_result.json"
        command = [
            sys.executable, "-B", str(selfcheck),
            "--json", str(json_path),
            "--doc", str(doc),
            "--cases", str(cases_file),
            "--upstream", str(upstream),
            "--out", str(result_path),
            "--project-root", str(root),
            "--evidence-dir", str(run_dir),
        ]
        completed = subprocess.run(
            command, cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False,
        )
        (run_dir / f"probe_{case_id}_stdout.txt").write_text(completed.stdout, encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        failed = [check["id"] for check in result["checks"] if check["status"] == "FAIL"]
        captured = entry["expect_check"] in failed if entry["expect_check"] else not failed
        ok = completed.returncode == entry["expect_exit"] and captured
        results.append({
            "case_id": case_id,
            "note": entry["note"],
            "injection": injection_detail,
            "expected_exit": entry["expect_exit"],
            "actual_exit": completed.returncode,
            "expected_check": entry["expect_check"],
            "failed_checks": failed,
            "captured": captured,
            "selfcheck_status": result["status"],
            "stdout_file": f"probe_{case_id}_stdout.txt",
            "verdict": "AS_EXPECTED" if ok else "UNEXPECTED",
        })
        if not ok:
            print(f"[{case_id}] 非预期：exit={completed.returncode} failed={failed}")
            print(completed.stdout)
            return 1

    summary = {
        "schema_version": 1,
        "artifact": "s6a_r05_injection_probe",
        "task_id": "S6-A",
        "run_id": run_dir.name,
        "selfcheck": "verification/s6_g0_selfcheck.py（r05 最终版）",
        "purpose": "先证明 C12/C7 的新断言能捕获缺陷，再允许 r05 出 ALL_PASS（N-r04-01/N-r04-03/N-r04-04）",
        "baseline_verdict": results[0]["verdict"],
        "results": results,
        "scope_statement": "探针只证明自检断言有判别力，不代表状态机行为、G0 复评、独立审查或实物验收通过。",
    }
    (run_dir / "probe_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": "PROBE_OK",
        "cases": [(r["case_id"], r["actual_exit"], r["failed_checks"]) for r in results],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())