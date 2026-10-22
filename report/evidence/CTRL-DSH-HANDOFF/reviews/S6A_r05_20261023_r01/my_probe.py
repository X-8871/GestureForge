#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 5 轮评审：自己跑 s6a_r05_probe.py 的 8 个用例 + 我额外自造注入；全部落隔离目录。

复刻 probe 的注入定义（逐字对照 verification/s6a_r05_probe.py 的 apply 函数），
并补充我自己的判别力注入。自检一律用被审 r05 最终版脚本，--project-root 用绝对路径。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
WORK = OUT / "probe"
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
SELFCHECK = ROOT / "verification/s6_g0_selfcheck.py"
BEHAVIOR = ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOC = ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
CASES = RUN / "hand_computed_cases.json"
UPSTREAM = RUN / "upstream_bindings.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(data, path: Path) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# ---------------- 复刻 probe 的注入（逐字同逻辑） ----------------

def i_m5_remove_qualifier(data):
    tr = {i["id"]: i for i in data["transitions"]}
    cond = str(tr["M5"]["condition"])
    marker = "（且本帧必须为窗口推进帧"
    if marker not in cond:
        raise RuntimeError("M5 条件中找不到窗口推进帧限定")
    tr["M5"]["condition"] = cond.split(marker)[0]
    return f"M5.condition 回退为无窗口推进帧限定：{tr['M5']['condition']}"


def i_empty_predicates_used(data):
    tr = {i["id"]: i for i in data["transitions"]}
    tr["M2"]["predicates_used"] = []
    return "transitions.M2.predicates_used = []"


def i_b13_predicates_used_added(data):
    rows = {r["id"]: r for r in data["behavior_rows"]}
    rows["B13"]["predicates_used"] = ["TARGET_CONTINUES"]
    return "behavior_rows.B13.predicates_used = ['TARGET_CONTINUES']"


def i_undeclared_predicate_name(data):
    tr = {i["id"]: i for i in data["transitions"]}
    tr["M8"]["predicates_used"] = ["TARGET_LOST"]
    return "transitions.M8.predicates_used = ['TARGET_LOST']"


def i_suppressed_release_removed(data):
    rel = str(data["stable_latching"]["suppressed_trigger_release"])
    data["stable_latching"]["suppressed_trigger_release"] = rel.replace("窗口推进帧", "结果帧")
    return "suppressed_trigger_release 去掉「窗口推进帧」"


def i_case_timeout_action(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    by["HC-30"]["expected"]["action_at_gate_open_frame"]["gate_opens_on_timeout"] = True
    return "HC-30.expected.action_at_gate_open_frame.gate_opens_on_timeout = true"


def i_case_span_wrong(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    by["HC-29"]["expected"]["window_span_ms"] = 320.0
    return "HC-29.expected.window_span_ms = 320.0"


# ---------------- 我额外自造的注入 ----------------

def x_doc_m5_qualifier_removed(doc_text: str) -> str:
    marker = "**且本帧必须为窗口推进帧**"
    if marker not in doc_text:
        raise RuntimeError("文档 M5 行找不到限定")
    return doc_text.replace(
        marker + "（`state ∈ {OK, NO_HAND}`、`stale=false`、非重复、非倒序）", "", 1
    )


def x_m5_partial_marker_removed(data):
    tr = {i["id"]: i for i in data["transitions"]}
    cond = str(tr["M5"]["condition"])
    tr["M5"]["condition"] = cond.replace("、非倒序", "")
    return "M5 条件仅删去 '非倒序' 一个限定词"


def x_predicates_used_string(data):
    tr = {i["id"]: i for i in data["transitions"]}
    tr["M6"]["predicates_used"] = "TARGET_CONTINUES"
    return "M6.predicates_used = 字符串（非列表）"


def x_predicates_used_empty_on_m6(data):
    tr = {i["id"]: i for i in data["transitions"]}
    tr["M6"]["predicates_used"] = []
    return "M6.predicates_used = []"


def x_hc29_expected_150(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    by["HC-29"]["expected"]["window_span_ms"] = 150.0
    return "HC-29.expected.window_span_ms = 150.0"


def x_hc29_s01_250(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    by["HC-29"]["recompute"]["s01_ms"] = 250
    return "HC-29.recompute.s01_ms = 250（宽松口径仍 ≥250、严格口径 200<250 → 两口径不一致）"


def x_hc30_total_actions_2(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    by["HC-30"]["expected"]["total_actions"]["gate_opens_on_timeout"] = 2
    return "HC-30.expected.total_actions.gate_opens_on_timeout = 2"


def x_hc30_second_ok_becomes_timeout(cases):
    by = {c["case_id"]: c for c in cases["cases"]}
    scen = [s for s in by["HC-30"]["recompute"]["scenarios"] if s["name"] == "gate_opens_on_timeout"][0]
    for frame in scen["frames"]:
        if frame["index"] == 12:
            frame["kind"] = "TIMEOUT"
    return "HC-30 场景A 第 12 帧改为 TIMEOUT（此后无窗口推进帧 → 应无动作，与 expected 冲突）"


def x_predicate_empty_statement(data):
    data["predicate_binding_policy"]["statement"] = "M5 与 B13 没有 predicates_used 字段。"
    return "statement 回退为不含 H-10/global_cooldown_gate 要素的旧措辞"


def x_artifact_version_downgrade(data):
    data["artifact_version"] = "S6A-G0-v1.3"
    data["run_id"] = "s6a_g0_20261022_r04"
    return "artifact_version 回退 v1.3（检验版本断言未削弱）"


INJECTIONS = [
    ("baseline_no_injection", None, 0, None, None),
    ("m5_window_advance_removed", "json", 1, "C12", i_m5_remove_qualifier),
    ("empty_predicates_used", "json", 1, "C12", i_empty_predicates_used),
    ("b13_predicates_used_added", "json", 1, "C12", i_b13_predicates_used_added),
    ("undeclared_predicate_name", "json", 1, "C12", i_undeclared_predicate_name),
    ("suppressed_release_not_window_advancing", "json", 1, "C12", i_suppressed_release_removed),
    ("case_timeout_frame_action", "cases", 1, "C7", i_case_timeout_action),
    ("case_span_wrong", "cases", 1, "C7", i_case_span_wrong),
    # ---- 我额外自造 ----
    ("X1_doc_m5_qualifier_removed", "doc", 1, "C12", x_doc_m5_qualifier_removed),
    ("X2_m5_partial_marker_removed", "json", 1, "C12", x_m5_partial_marker_removed),
    ("X3_predicates_used_string", "json", 1, "C12", x_predicates_used_string),
    ("X4_predicates_used_empty_M6", "json", 1, "C12", x_predicates_used_empty_on_m6),
    ("X5_hc29_expected_150", "cases", 1, "C7", x_hc29_expected_150),
    ("X6_hc29_s01_250", "cases", 1, "C7", x_hc29_s01_250),
    ("X7_hc30_total_actions_2", "cases", 1, "C7", x_hc30_total_actions_2),
    ("X8_hc30_frame12_timeout", "cases", 1, "C7", x_hc30_second_ok_becomes_timeout),
    ("X9_statement_old_wording", "json", 1, "C12", x_predicate_empty_statement),
    ("X10_version_downgrade", "json", 1, "C1", x_artifact_version_downgrade),
]


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    doc_base = DOC.read_text(encoding="utf-8")
    rows = []
    for case_id, target, expect_exit, expect_check, apply in INJECTIONS:
        json_path, cases_path, doc_path = BEHAVIOR, CASES, DOC
        note = "（无注入）"
        if target == "json":
            data = load(BEHAVIOR)
            note = apply(data)
            json_path = dump(data, WORK / f"{case_id}_behavior.json")
        elif target == "cases":
            data = load(CASES)
            note = apply(data)
            cases_path = dump(data, WORK / f"{case_id}_cases.json")
        elif target == "doc":
            mutated = apply(doc_base)
            doc_path = WORK / f"{case_id}_doc.md"
            doc_path.write_text(mutated, encoding="utf-8")
            note = "文档 M5 行限定被删除"
        result_path = WORK / f"{case_id}_result.json"
        command = [
            sys.executable, "-B", str(SELFCHECK),
            "--json", str(json_path), "--doc", str(doc_path), "--cases", str(cases_path),
            "--upstream", str(UPSTREAM), "--out", str(result_path),
            "--project-root", str(ROOT), "--evidence-dir", str(RUN),
        ]
        completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", check=False)
        (WORK / f"{case_id}_stdout.txt").write_text(completed.stdout, encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        failed = [c["id"] for c in result["checks"] if c["status"] == "FAIL"]
        captured = (expect_check in failed) if expect_check else (not failed)
        detail = next((c["detail"] for c in result["checks"] if c["id"] == expect_check), "") if expect_check else ""
        rows.append({
            "case_id": case_id,
            "injection": note,
            "expected_exit": expect_exit,
            "actual_exit": completed.returncode,
            "expected_check": expect_check,
            "failed_checks": failed,
            "captured": captured,
            "verdict": "AS_EXPECTED" if (completed.returncode == expect_exit and captured) else "UNEXPECTED",
            "detail_first_240": detail[:240],
        })
    summary = {
        "artifact": "reviewer_r05_probe_replication",
        "baseline_exit": rows[0]["actual_exit"],
        "probe_cases": rows[:8],
        "extra_cases": rows[8:],
        "all_as_expected": all(r["verdict"] == "AS_EXPECTED" for r in rows),
    }
    (OUT / "my_probe.txt").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['case_id']:38s} exit={r['actual_exit']} expect={r['expected_exit']} "
              f"failed={r['failed_checks']} {r['verdict']}")
    print("all_as_expected =", summary["all_as_expected"])
    return 0 if summary["all_as_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())