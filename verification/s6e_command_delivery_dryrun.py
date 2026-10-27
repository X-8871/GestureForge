#!/usr/bin/env python3
"""生成并校验不派发硬件命令的 S6-E 离线计划。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

CASES_REL = "docs/stage6/s6e_stage6_acceptance_cases_v1.json"
SUPPORTED_EVIDENCE = {
    "REAL_INFERENCE_REQUIRED",
    "REAL_CAPTURE_REQUIRED",
    "REPLAY_ONLY",
    "OFFLINE_SELFCHECK",
}
REQUIRED_GATES = (
    "operator_authorization",
    "hardware_session_handoff",
    "exclusive_session",
    "g0_approval",
    "command_delivery_review",
    "timing_freeze",
    "range_reservation",
    "cold_basis",
)
REQUIRED_CASE_FIELDS = (
    "id", "title", "group", "evidence_class", "input_conditions", "expected",
    "decision_rule", "binds_parameters", "timeout_s", "failure_preservation",
    "samples", "synthetic_substitution_allowed",
)
RUN_ID_RE = re.compile(r"s6e_command_delivery_(?P<date>[0-9]{8})_r(?P<revision>[0-9]{2})\Z")
PLAN_FIELDS = {
    "schema_version", "artifact", "artifact_version", "task_id", "run_id", "source",
    "mode", "execution_status", "commands_issued", "hardware_touched", "acceptance_claim",
    "board_window_gates", "scope_note", "cases",
}
SOURCE_FIELDS = {"path", "sha256", "artifact_version"}
CASE_PLAN_FIELDS = {
    "case_id", "title", "group", "evidence_class", "input_conditions",
    "synthetic_substitution_allowed", "expected", "decision_rule", "binds_parameters",
    "timeout_s", "failure_preservation", "samples", "disposition", "reason",
    "execution_status", "command", "result",
}
GATE_FIELDS = {"gate", "status"}
SCOPE_NOTE = (
    "仅预览冻结用例的证据类别、预期与判定条件。正式材料没有规定阶段6硬件执行命令或真实结果记录接口，"
    "因此不生成可执行命令，不伪造授权、板级结果或 command_delivery_review 通过结论。"
)
CASE_DISPOSITIONS = {
    "OFFLINE_SELFCHECK": "LOCAL_CHECK_NOT_EXECUTED",
    "REPLAY_ONLY": "REPLAY_PREFLIGHT_ONLY",
    "REAL_INFERENCE_REQUIRED": "BLOCKED_REAL_EVIDENCE_REQUIRED",
    "REAL_CAPTURE_REQUIRED": "BLOCKED_REAL_EVIDENCE_REQUIRED",
}
CASE_REASONS = {
    "OFFLINE_SELFCHECK": "仅允许后续运行对应离线自检；本计划没有执行自检或声明验收通过。",
    "REPLAY_ONLY": "回放资格须另行核验；回放结果不得替代真实推理或实物验收。",
    "REAL_INFERENCE_REQUIRED": "用例要求真实推理或真实采集；离线计划不派发该用例。",
    "REAL_CAPTURE_REQUIRED": "用例要求真实推理或真实采集；离线计划不派发该用例。",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """递归构造 JSON 对象，并拒绝任意层级的重复键。"""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 对象包含重复键：{key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"非标准 JSON 常量不允许：{value}")


def _strict_json_float(value: str) -> float:
    """解析有限 JSON 小数，拒绝指数溢出为 Infinity 的数值。"""
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"JSON 数值超出有限浮点范围：{value}")
    return parsed


def _load_json_strict(path: Path) -> Any:
    """以 UTF-8 严格读取 JSON，递归拒绝重复键和非标准常量。"""
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique_json_object,
        parse_constant=_reject_json_constant,
        parse_float=_strict_json_float,
    )


def _is_linklike(path: Path) -> bool:
    """检测符号链接及 Windows junction。"""
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and is_junction())


def _validate_run_id(run_id: str) -> None:
    match = RUN_ID_RE.fullmatch(run_id) if isinstance(run_id, str) else None
    if match is None or int(match.group("revision")) < 1:
        raise ValueError("run_id 必须符合 s6e_command_delivery_YYYYMMDD_rNN")
    try:
        datetime.strptime(match.group("date"), "%Y%m%d")
    except ValueError as exc:
        raise ValueError("run_id 中的日期不是有效日历日期") from exc


def _expected_output_rel(run_id: str) -> str:
    _validate_run_id(run_id)
    return f"report/evidence/S6-E/{run_id}/dry_run_plan.json"


def _validate_new_output(root: Path, run_id: str, out_arg: str | None) -> tuple[Path, Path]:
    """只接受证据根下新 RunId 的规范计划路径，拒绝已有项及链接路径。"""
    expected_rel = _expected_output_rel(run_id)
    if out_arg is not None and out_arg != expected_rel:
        raise ValueError(f"--out 仅允许规范新文件路径 {expected_rel!r}")

    if _is_linklike(root):
        raise ValueError("project-root 不得为符号链接或 junction")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project-root 必须是普通目录")
    evidence_root = root / "report" / "evidence" / "S6-E"
    for directory in (root / "report", root / "report" / "evidence", evidence_root):
        if _is_linklike(directory):
            raise ValueError(f"拒绝经过符号链接或 junction：{directory}")
        if not directory.is_dir():
            raise ValueError(f"证据目录不存在或不是目录：{directory}")

    run_dir = evidence_root / run_id
    if _is_linklike(run_dir) or run_dir.exists():
        raise FileExistsError(f"RunId 目录已存在，拒绝覆盖：{run_dir}")
    output = run_dir / "dry_run_plan.json"
    resolved_output = output.resolve(strict=False)
    if not resolved_output.is_relative_to(root):
        raise ValueError("--out 解析后超出 project-root")
    return run_dir, output


def _write_new_plan(root: Path, run_id: str, out_arg: str | None, plan: dict[str, Any]) -> Path:
    """以目录和文件的独占创建模式写入新计划，不覆盖任何现存对象。"""
    run_dir, output = _validate_new_output(root, run_id, out_arg)
    encoded = (json.dumps(plan, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    run_dir.mkdir(exist_ok=False)
    if _is_linklike(run_dir) or not run_dir.resolve(strict=True).is_relative_to(root.resolve(strict=True)):
        raise ValueError("新 RunId 目录类型或解析路径异常")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    descriptor = os.open(output, flags, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    return output


def build_dry_run_plan(root: Path, run_id: str) -> dict[str, Any]:
    """只读取冻结用例集，构造不含可执行命令的离线计划。"""
    _validate_run_id(run_id)
    cases_path = root / CASES_REL
    raw = _load_json_strict(cases_path)
    if raw.get("task_id") != "S6-E" or raw.get("artifact_version") != "S6E-ACC-v1":
        raise ValueError("用例集身份或版本不符合冻结的 S6E-ACC-v1")
    if raw.get("case_set_status") != "FROZEN_PENDING_EXECUTION":
        raise ValueError("用例集未处于 FROZEN_PENDING_EXECUTION")
    if raw.get("execution_status") != "NOT_RUN":
        raise ValueError("拒绝读取已改变执行状态的用例集")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("run_id 必须为非空字符串")

    cases = raw.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("用例集缺少 cases")
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("用例记录必须为对象")
        missing_fields = [field for field in REQUIRED_CASE_FIELDS if field not in case]
        if missing_fields:
            raise ValueError(f"用例记录缺少字段：{missing_fields}")
        case_id = case.get("id")
        evidence_class = case.get("evidence_class")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"用例 ID 缺失或重复：{case_id!r}")
        seen.add(case_id)
        if evidence_class not in SUPPORTED_EVIDENCE:
            raise ValueError(f"{case_id}: 不支持的 evidence_class {evidence_class!r}")

        disposition = CASE_DISPOSITIONS[evidence_class]
        reason = CASE_REASONS[evidence_class]

        rows.append({
            "case_id": case_id,
            "title": case.get("title"),
            "group": case.get("group"),
            "evidence_class": evidence_class,
            "input_conditions": case.get("input_conditions"),
            "synthetic_substitution_allowed": case.get("synthetic_substitution_allowed"),
            "expected": case.get("expected"),
            "decision_rule": case.get("decision_rule"),
            "binds_parameters": case.get("binds_parameters"),
            "timeout_s": case.get("timeout_s"),
            "failure_preservation": case.get("failure_preservation"),
            "samples": case.get("samples"),
            "disposition": disposition,
            "reason": reason,
            "execution_status": "NOT_RUN",
            "command": None,
            "result": None,
        })

    gates = raw.get("board_window", {}).get("eight_gates_required")
    if not isinstance(gates, list) or set(gates) != set(REQUIRED_GATES):
        raise ValueError("窗口八类门禁与正式清单不一致")

    return {
        "schema_version": 1,
        "artifact": "s6e_command_delivery_dry_run",
        "artifact_version": "S6E-CMD-DRYRUN-v1",
        "task_id": "S6-E",
        "run_id": run_id,
        "source": {
            "path": CASES_REL,
            "sha256": _sha256(cases_path),
            "artifact_version": raw["artifact_version"],
        },
        "mode": "DRY_RUN_ONLY",
        "execution_status": "NOT_RUN",
        "commands_issued": False,
        "hardware_touched": False,
        "acceptance_claim": False,
        "board_window_gates": [
            {"gate": name, "status": "NOT_ASSESSED_BY_OFFLINE_PLAN"}
            for name in REQUIRED_GATES
        ],
        "scope_note": SCOPE_NOTE,
        "cases": rows,
    }


def validate_dry_run_plan(root: Path, plan: dict[str, Any]) -> list[str]:
    """核对 dry-run 计划与冻结用例逐项一致，并保证没有执行或结果声明。"""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["计划根节点必须为对象"]
    missing_plan_fields = PLAN_FIELDS - set(plan)
    unknown_plan_fields = set(plan) - PLAN_FIELDS
    if missing_plan_fields:
        errors.append(f"计划缺少字段：{sorted(missing_plan_fields)}")
    if unknown_plan_fields:
        errors.append(f"计划包含未批准字段：{sorted(unknown_plan_fields)}")
    cases_path = root / CASES_REL
    try:
        raw = _load_json_strict(cases_path)
    except (OSError, ValueError) as exc:
        return [f"无法读取冻结用例集：{exc}"]
    if not isinstance(raw, dict):
        return ["冻结用例集根节点必须为对象"]
    if (raw.get("task_id") != "S6-E" or raw.get("artifact_version") != "S6E-ACC-v1"
            or raw.get("case_set_status") != "FROZEN_PENDING_EXECUTION"
            or raw.get("execution_status") != "NOT_RUN"):
        errors.append("当前来源不再满足 S6E-ACC-v1 冻结且未执行条件")

    expected_head = {
        "schema_version": 1,
        "artifact": "s6e_command_delivery_dry_run",
        "artifact_version": "S6E-CMD-DRYRUN-v1",
        "task_id": "S6-E",
        "source_path": CASES_REL,
        "source_sha256": _sha256(cases_path),
        "source_artifact_version": "S6E-ACC-v1",
    }
    source = plan.get("source")
    if not isinstance(source, dict):
        source = {}
        errors.append("source 必须为对象")
    else:
        missing_source_fields = SOURCE_FIELDS - set(source)
        unknown_source_fields = set(source) - SOURCE_FIELDS
        if missing_source_fields:
            errors.append(f"source 缺少字段：{sorted(missing_source_fields)}")
        if unknown_source_fields:
            errors.append(f"source 包含未批准字段：{sorted(unknown_source_fields)}")
    checks = (
        (plan.get("schema_version"), expected_head["schema_version"], "schema_version"),
        (plan.get("artifact"), expected_head["artifact"], "artifact"),
        (plan.get("artifact_version"), expected_head["artifact_version"], "artifact_version"),
        (plan.get("task_id"), expected_head["task_id"], "task_id"),
        (source.get("path"), expected_head["source_path"], "source.path"),
        (source.get("sha256"), expected_head["source_sha256"], "source.sha256"),
        (source.get("artifact_version"), expected_head["source_artifact_version"], "source.artifact_version"),
    )
    for actual, expected, field in checks:
        if type(actual) is not type(expected) or actual != expected:
            errors.append(f"字段 {field} 不匹配冻结用例集")
    if plan.get("scope_note") != SCOPE_NOTE:
        errors.append("scope_note 不得削弱离线范围或声称验收结果")

    for field, expected in (("mode", "DRY_RUN_ONLY"), ("execution_status", "NOT_RUN"),
                            ("commands_issued", False), ("hardware_touched", False),
                            ("acceptance_claim", False)):
        actual = plan.get(field)
        if type(actual) is not type(expected) or actual != expected:
            errors.append(f"{field} 必须为 {expected!r}")
    run_id = plan.get("run_id")
    try:
        _validate_run_id(run_id)
    except ValueError:
        errors.append("run_id 必须符合有效的 s6e_command_delivery_YYYYMMDD_rNN")

    expected_cases = raw.get("cases", [])
    actual_cases = plan.get("cases")
    if not isinstance(actual_cases, list):
        return errors + ["cases 必须为列表"]
    expected_by_id = {row.get("id"): row for row in expected_cases if isinstance(row, dict)}
    actual_ids = [row.get("case_id") if isinstance(row, dict) else None for row in actual_cases]
    valid_ids = [case_id for case_id in actual_ids if isinstance(case_id, str) and case_id]
    if len(valid_ids) != len(actual_ids):
        errors.append("计划 case_id 必须为非空字符串")
    if len(valid_ids) != len(set(valid_ids)):
        errors.append("计划 case_id 存在重复")
    if set(valid_ids) != set(expected_by_id):
        errors.append("计划用例 ID 集合与冻结用例集不一致")

    for row in actual_cases:
        if not isinstance(row, dict):
            errors.append("用例计划项必须为对象")
            continue
        missing_case_fields = CASE_PLAN_FIELDS - set(row)
        unknown_case_fields = set(row) - CASE_PLAN_FIELDS
        if missing_case_fields:
            errors.append(f"用例计划项缺少字段：{sorted(missing_case_fields)}")
        if unknown_case_fields:
            errors.append(f"用例计划项包含未批准字段：{sorted(unknown_case_fields)}")
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            continue
        source_case = expected_by_id.get(case_id)
        if source_case is None:
            continue
        if row.get("evidence_class") != source_case.get("evidence_class"):
            errors.append(f"{case_id}: evidence_class 与冻结用例不一致")
        for field in ("title", "group", "input_conditions", "binds_parameters",
                      "failure_preservation", "samples"):
            if row.get(field) != source_case.get(field):
                errors.append(f"{case_id}: {field} 与冻结用例不一致")
        if (type(row.get("synthetic_substitution_allowed")) is not type(source_case.get("synthetic_substitution_allowed"))
                or row.get("synthetic_substitution_allowed") != source_case.get("synthetic_substitution_allowed")):
            errors.append(f"{case_id}: 合成替代许可与冻结用例不一致")
        if row.get("expected") != source_case.get("expected"):
            errors.append(f"{case_id}: expected 与冻结用例不一致")
        if row.get("decision_rule") != source_case.get("decision_rule"):
            errors.append(f"{case_id}: decision_rule 与冻结用例不一致")
        if (type(row.get("timeout_s")) is not type(source_case.get("timeout_s"))
                or row.get("timeout_s") != source_case.get("timeout_s")):
            errors.append(f"{case_id}: timeout_s 与冻结用例不一致")
        source_evidence_class = source_case.get("evidence_class")
        expected_disposition = CASE_DISPOSITIONS.get(source_evidence_class)
        if row.get("disposition") != expected_disposition:
            errors.append(f"{case_id}: disposition 不符合冻结 evidence_class")
        if row.get("reason") != CASE_REASONS.get(source_evidence_class):
            errors.append(f"{case_id}: reason 不得添加或声称冻结规范之外的结果")
        if row.get("execution_status") != "NOT_RUN":
            errors.append(f"{case_id}: 离线 dry-run 用例必须保持 NOT_RUN")
        if row.get("command") is not None:
            errors.append(f"{case_id}: dry-run 计划不得含可执行命令")
        if row.get("result") is not None:
            errors.append(f"{case_id}: dry-run 计划不得含执行结果")

    gates = plan.get("board_window_gates")
    if not isinstance(gates, list):
        errors.append("八类门禁集合与正式用例集不一致")
    else:
        gate_names = [row.get("gate") if isinstance(row, dict) else None for row in gates]
        valid_gate_names = [name for name in gate_names if isinstance(name, str)]
        if (len(valid_gate_names) != len(gate_names)
                or len(valid_gate_names) != len(set(valid_gate_names))
                or set(valid_gate_names) != set(REQUIRED_GATES)):
            errors.append("八类门禁集合与正式用例集不一致")
        for row in gates:
            if not isinstance(row, dict):
                errors.append("门禁计划项必须为对象")
                continue
            missing_gate_fields = GATE_FIELDS - set(row)
            unknown_gate_fields = set(row) - GATE_FIELDS
            if missing_gate_fields:
                errors.append(f"门禁计划项缺少字段：{sorted(missing_gate_fields)}")
            if unknown_gate_fields:
                errors.append(f"门禁计划项包含未批准字段：{sorted(unknown_gate_fields)}")
            if row.get("status") != "NOT_ASSESSED_BY_OFFLINE_PLAN":
                errors.append("离线计划不得声明任一板级门禁通过或失败")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-E command-delivery dry-run 计划与完整性校验")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    plan_parser = subparsers.add_parser("plan", help="从冻结用例生成纯离线计划")
    plan_parser.add_argument("--project-root", required=True)
    plan_parser.add_argument("--run-id", required=True)
    plan_parser.add_argument("--out", help="可选；必须精确等于该 RunId 下的规范 dry_run_plan.json 路径")
    validate_parser = subparsers.add_parser("validate", help="校验 dry-run 计划，不能验证真实验收结果")
    validate_parser.add_argument("--project-root", required=True)
    validate_parser.add_argument("--plan", required=True)
    args = parser.parse_args(argv)
    root_arg = Path(args.project_root)
    if _is_linklike(root_arg):
        print(json.dumps({"status": "BLOCKED", "errors": ["project-root 不得为符号链接或 junction"]},
                         ensure_ascii=False))
        return 2
    try:
        root = root_arg.resolve(strict=True)
    except OSError as exc:
        print(json.dumps({"status": "BLOCKED", "errors": [f"project-root 无效：{exc}"]}, ensure_ascii=False))
        return 2
    if args.operation == "plan":
        try:
            plan = build_dry_run_plan(root, args.run_id)
            errors = validate_dry_run_plan(root, plan)
            if errors:
                print(json.dumps({"status": "INVALID", "errors": errors}, ensure_ascii=False))
                return 1
            out = _write_new_plan(root, args.run_id, args.out, plan)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(json.dumps({"status": "BLOCKED", "errors": [str(exc)]}, ensure_ascii=False))
            return 2
        result = {"status": "DRY_RUN_PLAN_READY" if not errors else "INVALID",
                  "run_id": args.run_id, "case_count": len(plan["cases"]),
                  "execution_status": "NOT_RUN", "commands_issued": False,
                  "hardware_touched": False, "errors": errors, "output": str(out)}
        print(json.dumps(result, ensure_ascii=False))
        return 0 if not errors else 1

    try:
        plan = _load_json_strict(Path(args.plan))
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    if not isinstance(plan, dict):
        print(json.dumps({"status": "INVALID", "errors": ["计划根节点必须为对象"]}, ensure_ascii=False))
        return 1
    errors = validate_dry_run_plan(root, plan)
    result = {"status": "DRY_RUN_PLAN_VALID" if not errors else "INVALID",
              "run_id": plan.get("run_id"), "case_count": len(plan.get("cases", [])),
              "execution_status": plan.get("execution_status"), "commands_issued": plan.get("commands_issued"),
              "hardware_touched": plan.get("hardware_touched"), "errors": errors}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
