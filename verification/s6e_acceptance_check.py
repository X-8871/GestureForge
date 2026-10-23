#!/usr/bin/env python3
"""S6-E 验收用例集机器校验器（`docs/stage6/s6e_stage6_acceptance_cases_v1.json`）。

    python -B verification/s6e_acceptance_check.py --project-root <abs> [--inject-self-test] [--out <json>]

检查项：
* E1  身份/状态字段齐全，且 `execution_status` 必须为 `NOT_RUN`（不得把未执行写成已执行）
* E2  用例数 ≥26、ID 唯一、每条用例的必需字段齐全
* E3  每条用例 `binds_parameters` ⊆ 行为表 24 项已批准参数 ID
* E4  `approved_parameter_ids` 与行为表 24 项**集合相等**，且无任何 `PENDING` 状态
* E5  `stale_age_limit_ms` 与行为表 `T6-STALE_LIMIT.draft_value` 相等（跨阶段同源常量）
* E6  `T6-A03` 必须为 `NOT_RUN` 且该块**不含任何数值**（禁止填造）
* E7  证据类别合法；ACT/UNK/REC 组一律不得标离线自检，且 `synthetic_substitution_allowed=false`；
     REC-07 必须 `REAL_CAPTURE_REQUIRED`；UNK-01 必须 `REAL_INFERENCE_REQUIRED`
* E8  统计口径：T6-01 0.9/50/10、T6-02 0.05/200、T6-03 1/1800、Clopper-Pearson 与严格 `>`
* E9  上板窗口八类门禁齐全
* E10 用例 ID 在规格文档中逐条出现（文档↔JSON 一致）
* E11 运行手册 §4 的 11 类矩阵类别全部被覆盖

`--inject-self-test`：在临时副本内注入 6 类缺陷（常量漂移、T6-A03 填造、参数集合缺项、
证据类别降级、用例清空、非法参数名），要求**每条都必须被判失败**；基线必须 PASS。
退出码：0 = 全部 PASS（且注入自测全被捕获）；1 = 存在失败。
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

BEHAVIOR = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOC = "docs/stage6/S6E_stage6_acceptance_cases_v1.md"
CASES = "docs/stage6/s6e_stage6_acceptance_cases_v1.json"

ALLOWED_EVIDENCE_CLASSES = {
    "REAL_INFERENCE_REQUIRED", "REAL_CAPTURE_REQUIRED", "REPLAY_ONLY", "OFFLINE_SELFCHECK",
}
REQUIRED_CASE_FIELDS = ("id", "title", "group", "runbook_class", "evidence_class", "input_conditions",
                        "expected", "decision_rule", "binds_parameters", "timeout_s",
                        "failure_preservation", "samples", "synthetic_substitution_allowed")
RUNBOOK_CLASSES = (
    "每类稳定输入", "持续保持与冷却后保持", "手离开再出现", "两类快速切换/短暂抖动",
    "多目标/同分/目标跳变", "NO_HAND / 场景未知 / 低分", "TIMEOUT / ERROR / DROPPED / stale",
    "重复、倒序、缺帧、重启帧号", "时间等于阈值、前后1个计时单位", "无新结果但时间持续前进",
    "动作失败/未观察/重复ACK",
)
EIGHT_GATES = ("operator_authorization", "hardware_session_handoff", "exclusive_session", "g0_approval",
               "command_delivery_review", "timing_freeze", "range_reservation", "cold_basis")


def param_value(param: dict):
    for key in ("draft_value", "value", "approved_value"):
        if key in param:
            return param[key]
    return None


def evaluate(root: Path, cases_rel: str = CASES) -> list[str]:
    errors: list[str] = []
    cpath = root / cases_rel
    if not cpath.is_file():
        return [f"E1: 缺少用例集文件 {cases_rel}"]
    data = json.loads(cpath.read_text(encoding="utf-8"))
    behavior = json.loads((root / BEHAVIOR).read_text(encoding="utf-8"))
    params = {p["id"]: p for p in behavior["parameters"]}
    approved_ids = {pid for pid, p in params.items() if "PENDING" not in str(p.get("approval_status", ""))}

    # E1 身份
    for key in ("schema_version", "artifact", "artifact_version", "task_id", "run_id",
                "case_set_status", "execution_status"):
        if not data.get(key):
            errors.append(f"E1: 缺少字段 {key}")
    if data.get("execution_status") != "NOT_RUN":
        errors.append(f"E1: execution_status 必须为 NOT_RUN（实际 {data.get('execution_status')!r}）")
    if data.get("task_id") != "S6-E":
        errors.append(f"E1: task_id 必须为 S6-E（实际 {data.get('task_id')!r}）")

    # E2 用例规模/唯一性/字段
    cases = data.get("cases") or []
    if len(cases) < 26:
        errors.append(f"E2: 用例数 {len(cases)} < 26")
    ids = [c.get("id") for c in cases]
    if len(ids) != len(set(ids)):
        errors.append("E2: 用例 ID 存在重复")
    for case in cases:
        missing = [f for f in REQUIRED_CASE_FIELDS if f not in case]
        if missing:
            errors.append(f"E2: {case.get('id')} 缺字段 {missing}")
        if not case.get("binds_parameters"):
            errors.append(f"E2: {case.get('id')} 未绑定任何参数")
        if not isinstance(case.get("timeout_s"), int) or case["timeout_s"] <= 0:
            errors.append(f"E2: {case.get('id')} timeout_s 必须为正整数")

    # E3 参数绑定合法性
    for case in cases:
        bad = [p for p in case.get("binds_parameters", []) if p not in approved_ids]
        if bad:
            errors.append(f"E3: {case.get('id')} 绑定了非已批准参数 {bad}")

    # E4 24 项集合相等
    bound_ids = set(data.get("approval_binding", {}).get("approved_parameter_ids") or [])
    if bound_ids != set(params):
        only_json = sorted(bound_ids - set(params))
        only_behavior = sorted(set(params) - bound_ids)
        errors.append(f"E4: 参数集合不一致（用例集多 {only_json}；行为表多 {only_behavior}）")
    if len(approved_ids) != 24:
        errors.append(f"E4: 行为表已批准参数应为 24 项（实际 {len(approved_ids)}）")

    # E5 跨阶段 stale 常量
    limit = data.get("approval_binding", {}).get("stale_age_limit_ms")
    behavior_limit = param_value(params.get("T6-STALE_LIMIT", {}))
    if limit != behavior_limit:
        errors.append(f"E5: stale_age_limit_ms={limit} 与行为表 T6-STALE_LIMIT={behavior_limit} 不一致")
    if limit != 200:
        errors.append(f"E5: stale 常量必须为 200 ms（实际 {limit}）")

    # E6 T6-A03 禁止填造
    a03 = data.get("approval_binding", {}).get("t6_a03") or {}
    if a03.get("value") != "NOT_RUN":
        errors.append(f"E6: T6-A03 value 必须为 NOT_RUN（实际 {a03.get('value')!r}）")
    numeric = [k for k, v in a03.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if numeric:
        errors.append(f"E6: T6-A03 块出现数值字段 {numeric}（禁止填造）")

    # E7 证据类别
    for case in cases:
        cid = case.get("id", "")
        cls = case.get("evidence_class")
        if cls not in ALLOWED_EVIDENCE_CLASSES:
            errors.append(f"E7: {cid} evidence_class 非法：{cls!r}")
        if cid.split("-")[0] in ("ACT", "UNK", "REC"):
            if cls not in ("REAL_INFERENCE_REQUIRED", "REAL_CAPTURE_REQUIRED", "REPLAY_ONLY"):
                errors.append(f"E7: {cid} 属动作/未知/恢复组，不得标离线自检（实际 {cls}）")
            if cls != "REAL_CAPTURE_REQUIRED" and case.get("synthetic_substitution_allowed") is not False:
                errors.append(f"E7: {cid} 必须声明 synthetic_substitution_allowed=false")
    by_id = {c.get("id"): c for c in cases}
    if by_id.get("REC-07", {}).get("evidence_class") != "REAL_CAPTURE_REQUIRED":
        errors.append("E7: REC-07 必须为 REAL_CAPTURE_REQUIRED（连续真实时间 ≥30 min）")
    if by_id.get("UNK-01", {}).get("evidence_class") != "REAL_INFERENCE_REQUIRED":
        errors.append("E7: UNK-01 必须为 REAL_INFERENCE_REQUIRED")

    # E8 统计口径
    stats = data.get("statistics", {})
    known = stats.get("known_action_success", {})
    if (known.get("threshold"), known.get("min_samples"), known.get("min_per_class")) != (0.9, 50, 10):
        errors.append(f"E8: T6-01 口径不符（{known.get('threshold')}/{known.get('min_samples')}/{known.get('min_per_class')}）")
    unknown = stats.get("unknown_false_accept", {})
    if (unknown.get("threshold"), unknown.get("min_samples")) != (0.05, 200):
        errors.append(f"E8: T6-02 口径不符（{unknown.get('threshold')}/{unknown.get('min_samples')}）")
    nohand = stats.get("no_hand_false_action", {})
    if (nohand.get("threshold"), nohand.get("min_segment_seconds")) != (1, 1800):
        errors.append(f"E8: T6-03 口径不符（{nohand.get('threshold')}/{nohand.get('min_segment_seconds')}）")
    if "Clopper-Pearson" not in str(stats.get("confidence_interval", "")):
        errors.append("E8: 缺少 Clopper-Pearson 置信区间口径")
    if "严格 `>`" not in str(stats.get("stale_rule", "")):
        errors.append("E8: stale 规则必须写明严格 `>`")

    # E9 八类门禁
    gates = data.get("board_window", {}).get("eight_gates_required") or []
    missing_gates = [g for g in EIGHT_GATES if g not in gates]
    if missing_gates:
        errors.append(f"E9: 缺少门禁 {missing_gates}")

    # E10 文档↔JSON 一致
    doc = root / DOC
    if not doc.is_file():
        errors.append(f"E10: 缺少规格文档 {DOC}")
    else:
        doc_text = doc.read_text(encoding="utf-8")
        absent = [cid for cid in ids if cid and cid not in doc_text]
        if absent:
            errors.append(f"E10: 文档缺少用例 ID {absent}")

    # E11 11 类矩阵覆盖
    covered = {c.get("runbook_class") for c in cases}
    missing_classes = [k for k in RUNBOOK_CLASSES if k not in covered]
    if missing_classes:
        errors.append(f"E11: 运行手册 §4 的类别未覆盖 {missing_classes}")
    return errors


INJECTIONS = (
    ("I1-stale-constant-drift", lambda d: d["approval_binding"].__setitem__("stale_age_limit_ms", 150)),
    ("I2-t6-a03-fabricated-value", lambda d: d["approval_binding"]["t6_a03"].__setitem__("value", 250)),
    ("I3-approved-param-missing", lambda d: d["approval_binding"].__setitem__(
        "approved_parameter_ids", d["approval_binding"]["approved_parameter_ids"][:-1])),
    ("I4-unknown-downgraded-offline", lambda d: next(
        c for c in d["cases"] if c["id"] == "UNK-01").__setitem__("evidence_class", "OFFLINE_SELFCHECK")),
    ("I5-cases-cleared", lambda d: d.__setitem__("cases", [])),
    ("I6-illegal-parameter-name", lambda d: next(
        c for c in d["cases"] if c["id"] == "ACT-01").__setitem__("binds_parameters", ["T6-NOT_A_PARAM"])),
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--inject-self-test", action="store_true")
    ap.add_argument("--out", default="tmp/6/s6e_acceptance_check.json")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    baseline_errors = evaluate(root)
    payload = {
        "schema_version": 1, "artifact": "s6e_acceptance_check", "run_id": "s6e_acceptance_20261024_r01",
        "checks": "E1..E11（身份/用例/参数绑定/24 项集合/stale 常量/T6-A03 禁填造/证据类别/统计口径/八类门禁/文档一致/11 类覆盖）",
        "baseline": {"verdict": "ALL_PASS" if not baseline_errors else "FAILED", "errors": baseline_errors},
        "verdict": "ALL_PASS" if not baseline_errors else "FAILED",
    }
    rc = 0 if not baseline_errors else 1
    if args.inject_self_test:
        injections = []
        all_caught = True
        for name, mutate in INJECTIONS:
            with tempfile.TemporaryDirectory() as tmp:
                copy_root = Path(tmp) / "copy"
                (copy_root / "docs/stage6").mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / CASES, copy_root / CASES)
                shutil.copyfile(root / BEHAVIOR, copy_root / BEHAVIOR)
                shutil.copyfile(root / DOC, copy_root / DOC)
                target = copy_root / CASES
                doc = json.loads(target.read_text(encoding="utf-8"))
                mutate(doc)
                target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                errs = evaluate(copy_root)
                caught = bool(errs)
                all_caught = all_caught and caught
                injections.append({"id": name, "caught": caught, "errors": errs[:3]})
        payload["injections"] = injections
        payload["self_test"] = {
            "verdict": "AS_EXPECTED" if (all_caught and not baseline_errors) else "UNEXPECTED",
            "all_injections_caught": all_caught,
        }
        payload["verdict"] = payload["self_test"]["verdict"]
        rc = 0 if (all_caught and not baseline_errors) else 1
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "baseline_errors": len(baseline_errors),
                      "self_test": payload.get("self_test", {}).get("verdict"),
                      "missing": [(i["id"], i["errors"][:1]) for i in payload.get("injections", []) if not i["caught"]]},
                     ensure_ascii=False))
    if baseline_errors:
        for item in baseline_errors:
            print("ERR " + item)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())