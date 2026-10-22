#!/usr/bin/env python3
"""S6-A r06 判别力探针：基线 1 例 + 注入 7 例（共 8 例）+「旧口径对照」1 例。

对 **r06 最终版**自检脚本执行：

  * 基线（不注入）：exit 0 / ALL_PASS；
  * 注入 7 例：每例把 r06 的 JSON/样例在 tmp 副本里改坏一处，断言 exit 1 且预期检查项报 FAIL；
  * 旧口径对照：用 **r05 版自检脚本**（git `1632761:verification/s6_g0_selfcheck.py`）在 r06 样例上运行，
    必须 exit 1 且 C7 报 FAIL —— 证明 N-r05-04 的 30fps「取较晚」修正确实能被捕获（旧口径会把
    HC-31 的完成帧算成第 6 帧 166.5 ms、m3_fires=false）。

注入清单（基线不计入注入数）：
  1. m5_window_advance_removed              N-r04-01 回归 → C12
  2. empty_predicates_used                  N-r04-03 回归 → C12
  3. b13_predicates_used_added              N-r04-02 回归 → C12
  4. undeclared_predicate_name              R3-B02 回归 → C12
  5. suppressed_release_not_window_advancing N-r04-01 一致性 → C12
  6. case_timeout_frame_action              N-r04-01 角落用例 → C7
  7. case_span_wrong                    N-r05-04：HC-31 预期改成旧口径（166.5 ms / m3_fires=false）→ C7

用法：
    python -B verification/s6a_r06_probe.py --run-dir report/evidence/S6-A/s6a_g0_20261022_r06 \
        --project-root D:/codex-worktrees/w6
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

R05_COMMIT = "1632761b2d60d8c1328aa82be97d53eef30e1072"


def _m5_remove_qualifier(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    condition = str(transitions["M5"]["condition"])
    marker = "（且本帧必须为窗口推进帧"
    if marker not in condition:
        raise RuntimeError("M5 条件中找不到窗口推进帧限定")
    transitions["M5"]["condition"] = condition.split(marker)[0]
    return "M5.condition 回退为无窗口推进帧限定"


def _empty_predicates_used(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    transitions["M2"]["predicates_used"] = []
    return "transitions.M2.predicates_used = []"


def _b13_predicates_used_added(data: dict[str, Any]) -> str:
    rows = {row["id"]: row for row in data["behavior_rows"]}
    rows["B13"]["predicates_used"] = ["TARGET_CONTINUES"]
    return "behavior_rows.B13.predicates_used = ['TARGET_CONTINUES']"


def _undeclared_predicate_name(data: dict[str, Any]) -> str:
    transitions = {item["id"]: item for item in data["transitions"]}
    transitions["M8"]["predicates_used"] = ["TARGET_LOST"]
    return "transitions.M8.predicates_used = ['TARGET_LOST']"


def _suppressed_release_removed(data: dict[str, Any]) -> str:
    release = str(data["stable_latching"]["suppressed_trigger_release"])
    data["stable_latching"]["suppressed_trigger_release"] = release.replace("窗口推进帧", "结果帧")
    return "stable_latching.suppressed_trigger_release 去掉「窗口推进帧」"


def _case_timeout_action(cases: dict[str, Any]) -> str:
    by_id = {case["case_id"]: case for case in cases["cases"]}
    by_id["HC-30"]["expected"]["action_at_gate_open_frame"]["gate_opens_on_timeout"] = True
    return "HC-30.expected.action_at_gate_open_frame.gate_opens_on_timeout = true（应无动作）"


def _case_span_wrong(cases: dict[str, Any]) -> str:
    by_id = {case["case_id"]: case for case in cases["cases"]}
    expected = by_id["HC-31"]["expected"]
    expected["window_span_ms"] = 166.5
    expected["m3_fires"] = False
    return "HC-31 预期改成旧口径（第 6 帧 166.5 ms、m3_fires=false）"


INJECTIONS = [
    {"id": "baseline_no_injection", "target": None, "expect_exit": 0, "expect_check": None,
     "note": "基线：不注入，必须 ALL_PASS"},
    {"id": "m5_window_advance_removed", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _m5_remove_qualifier, "note": "N-r04-01 回归"},
    {"id": "empty_predicates_used", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _empty_predicates_used, "note": "N-r04-03 回归"},
    {"id": "b13_predicates_used_added", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _b13_predicates_used_added, "note": "N-r04-02 回归"},
    {"id": "undeclared_predicate_name", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _undeclared_predicate_name, "note": "R3-B02 回归"},
    {"id": "suppressed_release_not_window_advancing", "target": "json", "expect_exit": 1,
     "expect_check": "C12", "apply": _suppressed_release_removed, "note": "N-r04-01 一致性断言"},
    {"id": "case_timeout_frame_action", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_timeout_action, "note": "N-r04-01 角落用例判别力"},
    {"id": "case_span_wrong", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_span_wrong, "note": "N-r05-04 判别力（旧口径：只按第 T6-S02 个 WINDOW_MATCH 帧取跨度）"},
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-A r06 判别力探针")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--selfcheck", default="verification/s6_g0_selfcheck.py")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
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
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif entry["target"] == "cases":
            data = json.loads(cases_path.read_text(encoding="utf-8"))
            injection_detail = entry["apply"](data)
            cases_file = work / f"{case_id}_cases.json"
            cases_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result_path = work / f"{case_id}_result.json"
        command = [sys.executable, "-B", str(selfcheck), "--json", str(json_path), "--doc", str(doc),
                   "--cases", str(cases_file), "--upstream", str(upstream), "--out", str(result_path),
                   "--project-root", str(root), "--evidence-dir", str(run_dir)]
        completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", check=False)
        (run_dir / f"probe_{case_id}_stdout.txt").write_text(completed.stdout, encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        failed = [check["id"] for check in result["checks"] if check["status"] == "FAIL"]
        captured = entry["expect_check"] in failed if entry["expect_check"] else not failed
        ok = completed.returncode == entry["expect_exit"] and captured
        results.append({
            "case_id": case_id, "note": entry["note"], "injection": injection_detail,
            "expected_exit": entry["expect_exit"], "actual_exit": completed.returncode,
            "expected_check": entry["expect_check"], "failed_checks": failed,
            "captured": captured, "selfcheck_status": result["status"],
            "stdout_file": f"probe_{case_id}_stdout.txt",
            "verdict": "AS_EXPECTED" if ok else "UNEXPECTED",
        })
        if not ok:
            print(f"[{case_id}] 非预期：exit={completed.returncode} failed={failed}")
            return 1

    # ---- 旧口径对照：r05 版自检脚本在 r06 样例上必须失败（C7） ----
    historical_script = work / "r05_self_g0_selfcheck.py"
    blob = subprocess.run(["git", "-C", str(root), "cat-file", "blob",
                           f"{R05_COMMIT}:verification/s6_g0_selfcheck.py"],
                          capture_output=True, check=False)
    if blob.returncode != 0:
        print("无法取到 r05 版自检脚本")
        return 2
    historical_script.write_bytes(blob.stdout)
    historical_result_path = work / "historical_model_check_result.json"
    command = [sys.executable, "-B", str(historical_script), "--json", str(behavior), "--doc", str(doc),
               "--cases", str(cases_path), "--upstream", str(upstream), "--out", str(historical_result_path),
               "--project-root", str(root), "--evidence-dir", str(run_dir)]
    completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    (run_dir / "probe_historical_model_check_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    historical = json.loads(historical_result_path.read_text(encoding="utf-8"))
    historical_failed = [check["id"] for check in historical["checks"] if check["status"] == "FAIL"]
    historical_ok = completed.returncode == 1 and "C7" in historical_failed
    c7_detail = next((c["detail"] for c in historical["checks"] if c["id"] == "C7"), "")
    results.append({
        "case_id": "historical_model_check",
        "note": "r05 版自检（旧口径）在 r06 样例上必须失败且 C7 报 FAIL（N-r05-04 捕获证明）",
        "injection": "使用 git 1632761 的 verification/s6_g0_selfcheck.py（r05 旧口径）",
        "expected_exit": 1, "actual_exit": completed.returncode, "expected_check": "C7",
        "failed_checks": historical_failed, "captured": "C7" in historical_failed,
        "c7_detail": c7_detail[:400],
        "selfcheck_status": historical["status"],
        "stdout_file": "probe_historical_model_check_stdout.txt",
        "verdict": "AS_EXPECTED" if historical_ok else "UNEXPECTED",
    })

    injection_results = [row for row in results if row["case_id"] != "historical_model_check"]
    baseline = next(row for row in injection_results if row["case_id"] == "baseline_no_injection")
    injections = [row for row in injection_results if row["case_id"] != "baseline_no_injection"]
    summary = {
        "schema_version": 1,
        "artifact": "s6a_r06_discrimination_probe",
        "task_id": "S6-A",
        "run_id": run_dir.name,
        "purpose": "先证明 C12/C7 的新断言能捕获缺陷，再允许 r06 出 ALL_PASS（N-r05-01..04）",
        "composition": "基线 1 例 + 注入 7 例（共 8 例）+ 旧口径对照 1 例（共 9 次运行）",
        "baseline_verdict": baseline["verdict"],
        "injection_count": len(injections),
        "total_runs": len(results),
        "results": results,
        "scope_statement": "探针只证明自检断言有判别力，不代表状态机行为、G0 复评、独立审查或实物验收通过。",
    }
    (run_dir / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"status": "PROBE_OK", "composition": summary["composition"],
                      "results": [(row["case_id"], row["actual_exit"], row["verdict"]) for row in results]},
                     ensure_ascii=False))
    return 0 if all(row["verdict"] == "AS_EXPECTED" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())