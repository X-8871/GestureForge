#!/usr/bin/env python3
"""S6-E 验收用例集机器校验器（`docs/stage6/s6e_stage6_acceptance_cases_v1.json`）。

    python -B verification/s6e_acceptance_check.py --project-root <abs> [--inject-self-test] [--out <json>]

检查项：
* E1  身份/状态字段齐全，且 `execution_status` 必须为 `NOT_RUN`（不得把未执行写成已执行）
* E2  用例数 ≥26、ID 唯一、每条用例的必需字段齐全
* E3  每条用例 `binds_parameters` ⊆ 行为表 24 项已批准参数 ID
* E4  `approved_parameter_ids` 与行为表 24 项**集合相等**，逐项批准状态和批准索引必须匹配
* E5  `stale_age_limit_ms` 与行为表 `T6-STALE_LIMIT.draft_value` 相等（跨阶段同源常量）
* E6  `T6-A03` 必须为 `NOT_RUN` 且该块**不含任何数值**（禁止填造）
* E7  证据类别合法；ACT/UNK/REC 组一律不得标离线自检，且 `synthetic_substitution_allowed=false`；
     REC-07 必须 `REAL_CAPTURE_REQUIRED`；UNK-01 必须 `REAL_INFERENCE_REQUIRED`
* E8  统计口径：T6-01 0.9/50/10、T6-02 0.05/200、T6-03 1/1800、Clopper-Pearson 与严格 `>`
* E9  上板窗口八类门禁齐全
* E10 用例 ID 在规格文档中逐条出现（文档↔JSON 一致）
* E11 运行手册 §4 的 11 类矩阵类别全部被覆盖

`--inject-self-test`：在临时副本内注入 14 类缺陷（含真实证据降级、合成替代和批准状态/索引缺失），
要求**每条都必须被判失败**；基线必须 PASS。
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
APPROVAL_STATUS = "APPROVED_20261023"
APPROVAL_RECEIPT = "report/evidence/CTRL-DSH-HANDOFF/decisions/stage6_approval_receipt_20261023_r01.md"
EXPECTED_PARAMETER_IDS = (
    "T6-A01", "T6-A02", "T6-A03", "T6-C01", "T6-S01", "T6-S02", "T6-S03", "T6-S04",
    "T6-L01", "T6-L02", "T6-K01", "T6-J01", "T6-U00_W", "T6-U00_N", "T6-U01",
    "T6-P01", "T6-P02", "T6-P03", "T6-P04", "T6-P05", "T6-STALE_LIMIT", "T6-01",
    "T6-02", "T6-03",
)
EXPECTED_PARAMETER_ID_SET = frozenset(EXPECTED_PARAMETER_IDS)
REAL_CASE_CLASSES = {
    **{f"ACT-{i:02d}": "REAL_INFERENCE_REQUIRED" for i in range(1, 12)},
    **{f"UNK-{i:02d}": "REAL_INFERENCE_REQUIRED" for i in range(1, 4)},
    **{f"REC-{i:02d}": "REAL_INFERENCE_REQUIRED" for i in range(1, 9)},
    "REC-07": "REAL_CAPTURE_REQUIRED",
}


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
    approval_binding = data.get("approval_binding")
    if not isinstance(approval_binding, dict):
        errors.append("E4: 用例集 approval_binding 必须为对象")
        approval_binding = {}

    raw_params = behavior.get("parameters")
    if not isinstance(raw_params, list):
        errors.append("E4: 行为表 parameters 必须为列表")
        raw_params = []
    if len(raw_params) != len(EXPECTED_PARAMETER_IDS):
        errors.append(f"E4: 行为表参数记录必须恰为 24 项（实际 {len(raw_params)}）")

    params = {}
    parameter_ids = []
    seen_parameter_ids = set()
    duplicate_parameter_ids = set()
    approved_ids = set()
    for index, param in enumerate(raw_params):
        if not isinstance(param, dict):
            errors.append(f"E4: 行为表第 {index + 1} 项参数记录必须为对象")
            continue
        pid = param.get("id")
        if not isinstance(pid, str):
            errors.append(f"E4: 行为表第 {index + 1} 项参数 ID 必须为字符串（实际 {pid!r}）")
        else:
            parameter_ids.append(pid)
            if pid in seen_parameter_ids:
                duplicate_parameter_ids.add(pid)
            seen_parameter_ids.add(pid)
            if pid not in EXPECTED_PARAMETER_ID_SET:
                errors.append(f"E4: 行为表包含非正式参数 ID {pid!r}")
            params.setdefault(pid, param)
            if (param.get("approval_status") == APPROVAL_STATUS
                    and param.get("approval_ref") == APPROVAL_RECEIPT):
                approved_ids.add(pid)
        if param.get("approval_status") != APPROVAL_STATUS:
            errors.append(f"E4: 参数 {pid!r} approval_status 必须为 {APPROVAL_STATUS}")
        if param.get("approval_ref") != APPROVAL_RECEIPT:
            errors.append(f"E4: 参数 {pid!r} approval_ref 必须精确匹配批准回执")
    if duplicate_parameter_ids:
        errors.append(f"E4: 行为表参数 ID 重复 {sorted(duplicate_parameter_ids)}")
    parameter_id_set = set(parameter_ids)
    if parameter_id_set != EXPECTED_PARAMETER_ID_SET:
        missing = sorted(EXPECTED_PARAMETER_ID_SET - parameter_id_set)
        unexpected = sorted(parameter_id_set - EXPECTED_PARAMETER_ID_SET)
        errors.append(f"E4: 行为表参数 ID 必须恰为正式 24 项（缺少 {missing}；额外 {unexpected}）")

    approval_record = behavior.get("approval_record")
    if not isinstance(approval_record, dict) or approval_record.get("receipt") != APPROVAL_RECEIPT:
        errors.append("E4: 行为表批准索引与已批准记录不一致或缺失")
    if approval_binding.get("approval_receipt") != APPROVAL_RECEIPT:
        errors.append("E4: 用例集批准索引与已批准记录不一致或缺失")

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
    raw_approved_ids = approval_binding.get("approved_parameter_ids")
    if not isinstance(raw_approved_ids, list):
        errors.append("E4: approved_parameter_ids 必须为列表")
        raw_approved_ids = []
    if len(raw_approved_ids) != len(EXPECTED_PARAMETER_IDS):
        errors.append(f"E4: approved_parameter_ids 必须恰为 24 项（实际 {len(raw_approved_ids)}）")
    approved_id_values = []
    for index, pid in enumerate(raw_approved_ids):
        if not isinstance(pid, str):
            errors.append(f"E4: approved_parameter_ids 第 {index + 1} 项必须为字符串（实际 {pid!r}）")
        else:
            approved_id_values.append(pid)
    bound_ids = set(approved_id_values)
    if len(bound_ids) != len(approved_id_values):
        errors.append("E4: approved_parameter_ids 含重复 ID")
    if bound_ids != EXPECTED_PARAMETER_ID_SET:
        only_json = sorted(bound_ids - EXPECTED_PARAMETER_ID_SET)
        only_expected = sorted(EXPECTED_PARAMETER_ID_SET - bound_ids)
        errors.append(f"E4: approved_parameter_ids 必须恰为正式 24 项（多 {only_json}；缺 {only_expected}）")
    if bound_ids != parameter_id_set:
        only_json = sorted(bound_ids - parameter_id_set)
        only_behavior = sorted(parameter_id_set - bound_ids)
        errors.append(f"E4: approved_parameter_ids 与行为表参数集合不一致（用例集多 {only_json}；行为表多 {only_behavior}）")

    # E5 跨阶段 stale 常量
    limit = approval_binding.get("stale_age_limit_ms")
    behavior_limit = param_value(params.get("T6-STALE_LIMIT", {}))
    if limit != behavior_limit:
        errors.append(f"E5: stale_age_limit_ms={limit} 与行为表 T6-STALE_LIMIT={behavior_limit} 不一致")
    if limit != 200:
        errors.append(f"E5: stale 常量必须为 200 ms（实际 {limit}）")

    # E6 T6-A03 禁止填造
    a03 = approval_binding.get("t6_a03") or {}
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
            required = REAL_CASE_CLASSES.get(cid)
            if required is None or cls != required:
                errors.append(f"E7: {cid} 必须使用逐 ID 真实证据类别 {required!r}（实际 {cls}）；回放仅作另列预演")
            if case.get("synthetic_substitution_allowed") is not False:
                errors.append(f"E7: {cid} 必须声明 synthetic_substitution_allowed=false")
    for cid in REAL_CASE_CLASSES:
        if cid not in ids:
            errors.append(f"E7: 缺少真实验收用例 {cid}")
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
    ("I7-action-replay-substitution", lambda d: next(
        c for c in d["cases"] if c["id"] == "ACT-01").__setitem__("evidence_class", "REPLAY_ONLY")),
    ("I8-capture-synthetic-substitution", lambda d: next(
        c for c in d["cases"] if c["id"] == "REC-07").__setitem__("synthetic_substitution_allowed", True)),
    ("I9-approval-binding-missing", lambda d: d["approval_binding"].pop("approval_receipt")),
)

BEHAVIOR_INJECTIONS = (
    ("I10-all-approval-status-missing", lambda d: [p.pop("approval_status", None) for p in d["parameters"]]),
    ("I11-approval-rejected", lambda d: d["parameters"][0].__setitem__("approval_status", "REJECTED")),
    ("I12-approval-unknown", lambda d: d["parameters"][0].__setitem__("approval_status", "UNKNOWN")),
    ("I13-parameter-approval-ref-missing", lambda d: d["parameters"][0].pop("approval_ref", None)),
    ("I14-approval-record-missing", lambda d: d.pop("approval_record", None)),
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
        mutations = [(name, CASES, mutate) for name, mutate in INJECTIONS]
        mutations += [(name, BEHAVIOR, mutate) for name, mutate in BEHAVIOR_INJECTIONS]
        for name, relative, mutate in mutations:
            with tempfile.TemporaryDirectory() as tmp:
                copy_root = Path(tmp) / "copy"
                (copy_root / "docs/stage6").mkdir(parents=True, exist_ok=True)
                shutil.copyfile(root / CASES, copy_root / CASES)
                shutil.copyfile(root / BEHAVIOR, copy_root / BEHAVIOR)
                shutil.copyfile(root / DOC, copy_root / DOC)
                target = copy_root / relative
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
