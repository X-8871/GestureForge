#!/usr/bin/env python3
"""S6-A r08 判别力探针：基线 1 例 + 注入 7 例（共 8 例）+ 历史口径对照 2 例（共 10 次运行）。

注入清单（基线不计入注入数）：
  1. m5_window_advance_removed        N-r04-01 回归 → C12
  2. empty_predicates_used            N-r04-03 回归 → C12
  3. b13_predicates_used_added        N-r04-02 回归 → C12
  4. b07_old_wording                  F1：B07.condition 回退旧措辞「第 N 个…」→ C14
  5. case_timeout_frame_action        N-r04-01 角落用例 → C7
  6. case_span_wrong                  N-r05-04：HC-31 预期改成旧口径（166.5 ms / m3_fires=false）→ C7
  7. case_out_of_sequence_index       F7：HC-32 预期改成越界外推值（completion_index=7/window_span_ms=233.1）→ C7
  8. m4_conflict_phrase            BLK-r07-1：把 parameter_notes.T6-S04 回退为「M4 不可达」→ C16（全包禁语断言）

历史口径对照（不计入注入数）：
  * r05 版自检（git `1632761`）在 r09 样例上运行 → 必须 exit 1（旧脚本无法接受 r07 预期）
  * r06 版自检（git `04ea58e1`）在 r09 样例上运行 → 必须 exit 1 且 C7 FAIL
    （旧实现会把超出所给序列的完成帧报成 7 / 233.1，与 r07 的「序列不足以判定」口径不符，F7）

用法：
    python -B verification/s6a_r09_probe.py --run-dir report/evidence/S6-A/s6a_g0_20261022_r07 \
        --project-root D:/codex-worktrees/w6
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HISTORICAL = (
    ("r07", "bdcf8963300475a61f26cbc3ec85a32275b781d2"),
    ("r06", "04ea58e1e363e956b8a46ae5711ec8aecb27bfd4"),
)
HISTORICAL = (("r05", "1632761b2d60d8c1328aa82be97d53eef30e1072"), HISTORICAL[1])


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


def _b07_old_wording(data: dict[str, Any]) -> str:
    rows = {row["id"]: row for row in data["behavior_rows"]}
    rows["B07"]["condition"] = ("连续 WINDOW_MATCH 帧数 ≥ T6-S02 且窗口时长 ≥ T6-S01；"
                               "完成时刻=第 N 个 WINDOW_MATCH 结果到达时刻；NO_HAND 不计入")
    return "behavior_rows.B07.condition 回退旧措辞「第 N 个 WINDOW_MATCH 结果到达时刻」"


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


def _case_out_of_sequence_index(cases: dict[str, Any]) -> str:
    by_id = {case["case_id"]: case for case in cases["cases"]}
    expected = by_id["HC-32"]["expected"]
    expected["completion_index"] = 7
    expected["window_span_ms"] = 233.1
    expected["m3_fires"] = False
    return "HC-32 预期改成越界外推值（completion_index=7 / window_span_ms=233.1）"


def _m4_conflict_phrase(data: dict[str, Any]) -> str:
    """BLK-r07-1：把 M4 口径回退为不可达，验证 C16 的全包禁语断言可捕获。"""
    data["parameter_notes"]["T6-S04"] = "草案 500ms ≥ T6-L02 300ms，M4 不可达（U6-12）；本行不得计入覆盖声明。"
    return "parameter_notes.T6-S04 回退为「M4 不可达…不得计入覆盖声明」"


INJECTIONS = [
    {"id": "baseline_no_injection", "target": None, "expect_exit": 0, "expect_check": None,
     "note": "基线：不注入，必须 ALL_PASS"},
    {"id": "m5_window_advance_removed", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _m5_remove_qualifier, "note": "N-r04-01 回归"},
    {"id": "empty_predicates_used", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _empty_predicates_used, "note": "N-r04-03 回归"},
    {"id": "b13_predicates_used_added", "target": "json", "expect_exit": 1, "expect_check": "C12",
     "apply": _b13_predicates_used_added, "note": "N-r04-02 回归"},
    {"id": "b07_old_wording", "target": "json", "expect_exit": 1, "expect_check": "C14",
     "apply": _b07_old_wording, "note": "F1：窗口完成文本统一断言"},
    {"id": "case_timeout_frame_action", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_timeout_action, "note": "N-r04-01 角落用例判别力"},
    {"id": "case_span_wrong", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_span_wrong, "note": "N-r05-04 判别力（旧口径：只按第 T6-S02 个 WINDOW_MATCH 帧取跨度）"},
    {"id": "case_out_of_sequence_index", "target": "cases", "expect_exit": 1, "expect_check": "C7",
     "apply": _case_out_of_sequence_index, "note": "F7：完成帧超出所给序列的报值口径"},
    {"id": "m4_conflict_phrase", "target": "json", "expect_exit": 1, "expect_check": "C16",
     "apply": _m4_conflict_phrase, "note": "BLK-r07-1：M4 口径统一的全包禁语断言"},
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-A r08 判别力探针")
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

    for label, rev in HISTORICAL:
        script = work / f"{label}_self_g0_selfcheck.py"
        blob = subprocess.run(["git", "-C", str(root), "cat-file", "blob",
                               f"{rev}:verification/s6_g0_selfcheck.py"],
                              capture_output=True, check=False)
        if blob.returncode != 0:
            print(f"无法取到 {label} 版自检脚本（{rev}）")
            return 2
        script.write_bytes(blob.stdout)
        result_path = work / f"historical_{label}_result.json"
        command = [sys.executable, "-B", str(script), "--json", str(behavior), "--doc", str(doc),
                   "--cases", str(cases_path), "--upstream", str(upstream), "--out", str(result_path),
                   "--project-root", str(root), "--evidence-dir", str(run_dir)]
        completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", check=False)
        (run_dir / f"probe_historical_model_check_{label}_stdout.txt").write_text(completed.stdout,
                                                                                 encoding="utf-8")
        historical = json.loads(result_path.read_text(encoding="utf-8"))
        failed = [check["id"] for check in historical["checks"] if check["status"] == "FAIL"]
        c7_detail = next((c["detail"] for c in historical["checks"] if c["id"] == "C7"), "")
        ok = completed.returncode == 1 and "C7" in failed
        results.append({
            "case_id": f"historical_model_check_{label}",
            "note": (f"{label} 版自检（旧口径/旧键）在 r09 样例上必须失败且 C7 FAIL"
                     + ("；首个 C7 失败在 HC-28（新键不可复算），HC-31 的口径差异由 case_span_wrong 直接证明"
                        if label == "r05" else "；旧实现把超出所给序列的完成帧报成 7/233.1（F7）")),
            "injection": f"使用 git {rev} 的 verification/s6_g0_selfcheck.py",
            "expected_exit": 1, "actual_exit": completed.returncode, "expected_check": "C7",
            "failed_checks": failed, "captured": "C7" in failed, "c7_detail": c7_detail[:400],
            "selfcheck_status": historical["status"],
            "stdout_file": f"probe_historical_model_check_{label}_stdout.txt",
            "verdict": "AS_EXPECTED" if ok else "UNEXPECTED",
        })

    baseline = next(row for row in results if row["case_id"] == "baseline_no_injection")
    injections = [row for row in results if row["case_id"] != "baseline_no_injection"
                  and not row["case_id"].startswith("historical_")]
    historical_rows = [row for row in results if row["case_id"].startswith("historical_")]
    summary = {
        "schema_version": 1,
        "artifact": "s6a_r07_discrimination_probe",
        "task_id": "S6-A",
        "run_id": run_dir.name,
        "purpose": "先证明 C12/C7/C14 的断言能捕获缺陷（含 F1 文本统一与 F7 越界完成帧口径），再允许 r07 出 ALL_PASS",
        "composition": (f"基线 1 例 + 注入 {len(injections)} 例（共 {1 + len(injections)} 例）"
                        f" + 历史口径对照 {len(historical_rows)} 例（共 {len(results)} 次运行）"),
        "baseline_verdict": baseline["verdict"],
        "injection_count": len(injections),
        "historical_check_count": len(historical_rows),
        "total_runs": len(results),
        "results": results,
        "scope_statement": "探针只证明自检断言有判别力，不代表状态机行为、G0 复评、独立审查或实物验收通过。",
    }
    (run_dir / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"status": "PROBE_OK" if all(r["verdict"] == "AS_EXPECTED" for r in results) else "PROBE_FAILED",
                      "composition": summary["composition"],
                      "results": [(row["case_id"], row["actual_exit"], row["verdict"]) for row in results]},
                     ensure_ascii=False))
    return 0 if all(row["verdict"] == "AS_EXPECTED" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())