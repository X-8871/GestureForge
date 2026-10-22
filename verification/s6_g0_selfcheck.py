#!/usr/bin/env python3
"""阶段6 S6-A（G0 包 + 行为表 v1）只读自检。

用途：在没有状态机实现的前提下，对本轮交付的**规格一致性**做机器检查：
  C1  JSON 身份与必填块
  C2  标识唯一性（行为行 / 参数 / 迁移）
  C3  文档 ↔ JSON 标识双向一致（缺一即缺陷）
  C4  待批准纪律（全部阈值与指标必须是 PENDING_APPROVAL，不得宣称已冻结/已批准）
  C5  五类动作映射一致（class_id 0..4、类名顺序、target 唯一、类型合法）
  C6  硬不变量与不宣称块完整（H-1..H-9、唯一触发解释）
  C7  人工手算样例的独立算术复算（预期键必须全部可复算）
  C8  上游只读文件 SHA-256 复算（含 w4/w5 只读路径）
  C9  文档必备覆盖关键词与章节存在
  C10 窄口径禁止声明扫描

边界：本脚本只做算术与文本一致性复算，**不**验证状态机行为、**不**代表 G0/G2/G4/G5 或任何验收结论。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

BEHAVIOR_ID_RE = re.compile(r"\bB\d{2}\b")
PARAM_ID_RE = re.compile(r"\bT6-[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*")

REQUIRED_INVARIANTS = [f"H-{i}" for i in range(1, 10)]
REQUIRED_DOC_KEYWORDS = [
    "行为表 v1",
    "ACTION_SUBMITTED",
    "ACTION_EFFECTIVE",
    "提交成功",
    "实际生效",
    "持续保持只触发一次",
    "低 FPS",
    "NO_HAND",
    "单调时钟",
    "frame_id",
    "冷却",
    "抖动",
    "重获",
    "过期",
    "UNKNOWN_RECOVER",
    "class_id",
]
REQUIRED_DOC_SECTIONS = ["## 5.", "## 9.", "## 10.", "## 12.", "## 15.", "## 18."]
FORBIDDEN_CLAIMS = [
    "阈值已冻结",
    "指标已批准",
    "G0 已通过",
    "验收已通过",
    "已通过验收",
    "已实测通过",
    "已冻结数值",
]
EXPECTED_CLASS_ORDER = ["fist", "palm", "one", "two_up", "three"]
SCOPE_STATEMENT = (
    "本自检只复算规格一致性与算术边界，不代表状态机行为正确、独立审查通过或 G0/G4/G5。"
)


class CheckFailure(Exception):
    """单个检查项失败。"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def r6(value: float) -> float:
    return round(float(value), 6)


# ---------------------------------------------------------------- C1 / C2


def check_identity(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise CheckFailure("schema_version 必须为 1")
    if data.get("artifact") != "s6a_stage6_g0_behavior":
        raise CheckFailure("artifact 名称不符")
    if data.get("artifact_version") != "S6A-G0-v1":
        raise CheckFailure("artifact_version 必须为 S6A-G0-v1")
    if data.get("status") != "G0_PACKET_PENDING_APPROVAL":
        raise CheckFailure("status 必须为 G0_PACKET_PENDING_APPROVAL")
    for key in ("baseline", "upstream", "hard_invariants", "event_classes", "behavior_rows", "parameters", "transitions"):
        if not data.get(key):
            raise CheckFailure(f"缺少必填块：{key}")
    if data["baseline"].get("start_commit") != "d8bc70e43572a8e44ddcd4b3489166e28a1c6151":
        raise CheckFailure("起始提交与开工核验不一致")


def check_unique_ids(data: dict[str, Any]) -> None:
    for block in ("behavior_rows", "parameters", "transitions", "open_decisions"):
        ids = [item["id"] for item in data[block]]
        if len(ids) != len(set(ids)):
            raise CheckFailure(f"{block} 存在重复 ID")
    states = list(data["states"])
    if len(states) != len(set(states)):
        raise CheckFailure("states 存在重复")
    if len(data["behavior_rows"]) < 20:
        raise CheckFailure("行为表行数少于预期")


# ---------------------------------------------------------------- C3


def doc_id_tokens(doc_text: str) -> tuple[set[str], set[str]]:
    params: set[str] = set()
    for match in PARAM_ID_RE.finditer(doc_text):
        end = match.end()
        if doc_text[end : end + 2] == "_*":
            continue
        params.add(match.group(0))
    behaviors = set(BEHAVIOR_ID_RE.findall(doc_text))
    return behaviors, params


def check_doc_json_consistency(data: dict[str, Any], doc_text: str) -> None:
    json_behaviors = {item["id"] for item in data["behavior_rows"]}
    json_params = {item["id"] for item in data["parameters"]}
    doc_behaviors, doc_params = doc_id_tokens(doc_text)
    missing_in_doc = sorted((json_behaviors - doc_behaviors) | (json_params - doc_params))
    unknown_in_doc = sorted((doc_behaviors - json_behaviors) | (doc_params - json_params))
    if missing_in_doc:
        raise CheckFailure(f"JSON 中存在而文档未提及的标识：{missing_in_doc}")
    if unknown_in_doc:
        raise CheckFailure(f"文档中存在而 JSON 未定义的标识：{unknown_in_doc}")


# ---------------------------------------------------------------- C4


def check_pending_approval_discipline(data: dict[str, Any], doc_text: str) -> None:
    for item in data["parameters"]:
        if item.get("approval_status") != "PENDING_APPROVAL":
            raise CheckFailure(f"{item['id']} 的 approval_status 必须是 PENDING_APPROVAL")
        if not item.get("draft_source"):
            raise CheckFailure(f"{item['id']} 缺少来源标注")
        if item.get("approval_owner") != "项目总控转呈 Wong":
            raise CheckFailure(f"{item['id']} 的批准责任人必须为项目总控转呈 Wong")
    metrics = [item for item in data["parameters"] if item.get("kind") == "metric"]
    if {item["id"] for item in metrics} != {"T6-01", "T6-02", "T6-03"}:
        raise CheckFailure("三项目标指标登记不完整")
    if data["actions"]["map_status"] != "PENDING_APPROVAL":
        raise CheckFailure("动作映射必须标为待批准")
    if "PENDING_APPROVAL" not in doc_text:
        raise CheckFailure("文档未出现待批准标记 PENDING_APPROVAL")


# ---------------------------------------------------------------- C5


def check_action_map(data: dict[str, Any]) -> None:
    mapping = data["actions"]["class_action_map"]
    if [item["class_id"] for item in mapping] != [0, 1, 2, 3, 4]:
        raise CheckFailure("class_id 必须为 0..4 且顺序固定")
    if [item["class_name"] for item in mapping] != EXPECTED_CLASS_ORDER:
        raise CheckFailure("类别顺序与 2A 冻结顺序不一致")
    if data["actions"]["class_order"] != EXPECTED_CLASS_ORDER:
        raise CheckFailure("actions.class_order 与 2A 冻结顺序不一致")
    targets = [item["target_id"] for item in mapping]
    if len(targets) != len(set(targets)):
        raise CheckFailure("target_id 必须互不相同")
    allowed = set(data["actions"]["supported_types"])
    for item in mapping:
        if item["action_type"] not in allowed:
            raise CheckFailure(f"{item['class_name']} 的动作类型不在支持集合内")
    


# ---------------------------------------------------------------- C6


def check_invariants(data: dict[str, Any]) -> None:
    ids = {item["id"] for item in data["hard_invariants"]}
    for required in REQUIRED_INVARIANTS:
        if required not in ids:
            raise CheckFailure(f"缺少硬不变量 {required}")
    for key in ("not_claimed", "evidence_boundaries"):
        if not data.get(key):
            raise CheckFailure(f"{key} 不得为空")
    once = data["trigger_once_while_held"]
    if once.get("declared") != "ONCE_PER_ACQUISITION":
        raise CheckFailure("持续保持必须唯一声明为 ONCE_PER_ACQUISITION")
    if once.get("second_trigger_allowed_only_by_new_acquisition") is not True:
        raise CheckFailure("二次触发必须只允许来自新的获取")
    if once.get("m15_path_is_not_new_acquisition") is not True:
        raise CheckFailure("M15 路径必须声明为不是新获取")
    if not once.get("rejected_alternative"):
        raise CheckFailure("必须显式登记被否决的备选解释")


# ---------------------------------------------------------------- C7


def recompute(case: dict[str, Any]) -> dict[str, Any]:
    spec = case["recompute"]
    kind = spec["kind"]
    if kind == "stable_window":
        period = float(spec["period_ms"])
        s01 = float(spec["s01_ms"])
        s02 = int(spec["s02_frames"])
        index = 1
        while not (index >= s02 and (index - 1) * period >= s01):
            index += 1
            if index > 10_000:
                raise CheckFailure("窗口复算未收敛")
        return {
            "frames_required": index,
            "actual_window_ms": r6((index - 1) * period),
            "lower_bound_W_ms": r6(max(s01, (s02 - 1) * period)),
            "dominant": "frame_count" if (s02 - 1) * period > s01 else "duration",
            "stable": True,
            "stable_at_sixth_frame": 6 >= s02 and (6 - 1) * period >= s01,
            "stable_at_fifth_frame": 5 >= s02 and (5 - 1) * period >= s01,
        }
    if kind == "cooldown":
        t_submit = float(spec["t_submit_ms"])
        k01 = float(spec["k01_ms"])
        return {
            "ended_at_ms": r6(t_submit + k01),
            "ended_at_minus_1ns": (k01 - 0.000001) >= k01,
            "ended_at_exact": k01 >= k01,
        }
    if kind == "dedup":
        a02 = float(spec["a02_ms"])
        return {
            "suppressed_at_minus_1": (a02 - 1.0) < a02,
            "suppressed_at_exact": a02 < a02,
        }
    if kind == "lost_frames":
        l01 = int(spec["l01_frames"])
        return {"lost_at_4": 4 >= l01, "lost_at_5": 5 >= l01}
    if kind == "lost_time":
        l02 = float(spec["l02_ms"])
        return {
            "lost_at_minus_1ns": (l02 - 0.000001) >= l02,
            "lost_at_exact": l02 >= l02,
        }
    if kind == "stale":
        limit = float(spec["limit_ms"])
        return {
            "stale_at_exact": limit > limit,
            "stale_at_exact_plus_1ns": (limit + 0.000001) > limit,
        }
    if kind == "jitter":
        j01 = int(spec["j01_frames"])
        return {"tolerated_at_1": 1 <= j01, "reset_at_2": 2 > j01}
    if kind == "frame_id_seen":
        prev_id = int(spec["prev_frame_id"])
        cur_id = int(spec["cur_frame_id"])
        same = bool(spec["session_same"])
        if not same:
            return {
                "event": "E_SESSION_RESET_SUSPECTED",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 1,
            }
        if cur_id == prev_id:
            return {
                "event": "E_FRAME_DUPLICATE",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 0,
            }
        if cur_id < prev_id:
            return {
                "event": "E_FRAME_OUT_OF_ORDER",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 1,
            }
        return {
            "event": "E_FRAME_RESULT",
            "advances_match_count": True,
            "may_trigger_action": True,
            "anomaly_delta": 0,
        }
    if kind == "session_change":
        same = bool(spec["session_same"])
        return {
            "state_after": "IDLE" if not same else "UNCHANGED",
            "target_cleared": not same,
            "may_trigger_action_on_reset_frame": False,
        }
    if kind == "trigger_once_hold":
        fps = float(spec["fps"])
        hold_s = float(spec["hold_s"])
        return {
            "hold_frames": int(round(fps * hold_s)),
            "submitted_total": 1,
            "trigger_after_cooldown": 0,
        }
    if kind == "hysteresis":
        current_score = float(spec["current_score"])
        p02 = float(spec["p02"])
        held = bool(spec["current_match"]) and current_score >= p02
        return {
            "held": held,
            "selected_class": "fist" if held else "palm",
            "suppression_event": "S_TARGET_HELD" if held else "NONE",
        }
    if kind == "tie":
        scores = [float(value) for value in spec["scores"]]
        orders = [int(value) for value in spec["source_orders"]]
        if len(set(scores)) != 1:
            raise CheckFailure("tie 样例要求分数完全相等")
        best = min(range(len(scores)), key=lambda i: orders[i])
        return {"selected_source_order": orders[best]}
    if kind == "action_events":
        t_trigger = float(spec["t_trigger_ms"])
        t_submit = float(spec["t_submit_ms"])
        t_effective = float(spec["t_effective_ms"])
        a01 = float(spec["a01_ms"])
        observed = bool(spec["effective_observed"])
        latency_action = t_effective - t_trigger
        return {
            "latency_action_ms": r6(latency_action),
            "latency_submit_ms": r6(t_submit - t_trigger),
            "counts_as_success_when_effective_observed": observed and latency_action <= a01,
            "counts_as_success_when_unobserved": False,
        }
    if kind == "unknown_rejection_proof":
        class_id = int(spec["unknown_class_id"])
        return {
            "class_membership_passes": 0 <= class_id <= 4,
            "proves_unknown_rejection": False,
            "counts_as_false_accept_in_T6_02": True,
        }
    raise CheckFailure(f"未知的复算类型：{kind}")


def check_hand_cases(cases: dict[str, Any]) -> int:
    seen: set[str] = set()
    for case in cases["cases"]:
        case_id = case["case_id"]
        if case_id in seen:
            raise CheckFailure(f"样例 ID 重复：{case_id}")
        seen.add(case_id)
        expected = case["expected"]
        try:
            computed = recompute(case)
        except CheckFailure:
            raise
        except Exception as exc:  # noqa: BLE001
            raise CheckFailure(f"{case_id} 复算异常：{type(exc).__name__}: {exc}") from exc
        for key, want in expected.items():
            if key not in computed:
                raise CheckFailure(f"{case_id}.{key} 无法独立复算（禁止不可复算的预期）")
            got = computed[key]
            if isinstance(want, float) or isinstance(got, float):
                if abs(r6(want) - r6(got)) > 1e-6:
                    raise CheckFailure(f"{case_id}.{key} 预期 {want} 与复算 {got} 不符")
            elif want != got:
                raise CheckFailure(f"{case_id}.{key} 预期 {want} 与复算 {got} 不符")
        for key in expected:
            if key not in computed:  # pragma: no cover - 上面已覆盖
                raise CheckFailure(f"{case_id}.{key} 未复算")
    return len(seen)


# ---------------------------------------------------------------- C8


def check_upstream(bindings: dict[str, Any], project_root: Path) -> str:
    """复算上游绑定。w6 内文件按工作副本哈希；外部树按 Git 对象哈希（并发写入时不抖动）。"""
    import subprocess

    verified = 0
    drift: list[str] = []
    for item in bindings["bindings"]:
        raw = item["path"]
        path = Path(raw)
        if not path.is_absolute():
            path = project_root / raw
        if item.get("git_repo"):
            repo = item["git_repo"]
            spec = f"{item['git_commit']}:{item['git_relpath']}"
            try:
                blob = subprocess.run(
                    ["git", "-C", repo, "show", spec],
                    capture_output=True,
                    check=False,
                )
            except OSError as exc:  # pragma: no cover
                raise CheckFailure(f"无法调用 git 复算 {item['id']}：{exc}") from exc
            if blob.returncode != 0:
                raise CheckFailure(
                    f"无法取到 {item['id']} 的提交版本 {spec}："
                    f"{blob.stderr.decode('utf-8', 'replace').strip()}"
                )
            actual = hashlib.sha256(blob.stdout).hexdigest()
            if actual.casefold() != item["sha256"].casefold():
                raise CheckFailure(
                    f"上游提交版本哈希不匹配：{item['id']} 清单 {item['sha256']} 实际 {actual}"
                )
            if path.is_file():
                work = sha256_file(path)
                if work.casefold() != item["sha256"].casefold():
                    drift.append(f"{item['id']}({work[:8]})")
        else:
            if not path.is_file():
                raise CheckFailure(f"上游文件不存在：{raw}")
            actual = sha256_file(path)
            if actual.casefold() != item["sha256"].casefold():
                raise CheckFailure(
                    f"上游哈希不匹配：{item['id']} 清单 {item['sha256']} 实际 {actual}"
                )
        verified += 1
    detail = f"{verified} 个上游绑定哈希一致（外部树按提交版本复算）"
    if drift:
        detail += f"；工作副本漂移（非失败，已在上游绑定中记录）：{', '.join(drift)}"
    return detail


# ---------------------------------------------------------------- C9 / C10


def check_doc_coverage(doc_text: str) -> None:
    missing = [word for word in REQUIRED_DOC_KEYWORDS if word not in doc_text]
    if missing:
        raise CheckFailure(f"文档缺少必备关键词：{missing}")
    missing_sections = [item for item in REQUIRED_DOC_SECTIONS if item not in doc_text]
    if missing_sections:
        raise CheckFailure(f"文档缺少必备章节：{missing_sections}")


NEGATION_PREFIXES = ("不宣称", "不构成", "不得", "禁止", "未", "不是", "并非")


def check_forbidden_claims(doc_text: str, data: dict[str, Any]) -> None:
    """窄口径扫描：命中禁止短语且其前 12 字符内**没有**否定标记才算违规。"""
    haystack = doc_text + json.dumps(data, ensure_ascii=False)
    hits: list[str] = []
    for phrase in FORBIDDEN_CLAIMS:
        start = 0
        while True:
            index = haystack.find(phrase, start)
            if index < 0:
                break
            context = haystack[max(0, index - 12) : index]
            if not any(marker in context for marker in NEGATION_PREFIXES):
                hits.append(f"{phrase}@{index}")
            start = index + len(phrase)
    if hits:
        raise CheckFailure(f"出现禁止的通过/冻结声明（非否定语境）：{hits}")


# ---------------------------------------------------------------- main


def run_checks(
    data: dict[str, Any],
    doc_text: str,
    cases: dict[str, Any],
    bindings: dict[str, Any],
    project_root: Path,
    doc_path: Path,
    json_path: Path,
    cases_path: Path,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def run(check_id: str, name: str, func) -> None:
        try:
            detail = func()
        except CheckFailure as exc:
            checks.append({"id": check_id, "name": name, "status": "FAIL", "detail": str(exc)})
            errors.append(f"{check_id}: {exc}")
        except Exception as exc:  # noqa: BLE001
            checks.append(
                {
                    "id": check_id,
                    "name": name,
                    "status": "FAIL",
                    "detail": f"未预期异常 {type(exc).__name__}: {exc}",
                }
            )
            errors.append(f"{check_id}: {type(exc).__name__}: {exc}")
        else:
            checks.append({"id": check_id, "name": name, "status": "PASS", "detail": detail})

    run("C1", "JSON 身份与必填块", lambda: check_identity(data) or "identity ok")
    run("C2", "标识唯一性", lambda: check_unique_ids(data) or "unique ok")
    run("C3", "文档↔JSON 标识双向一致", lambda: check_doc_json_consistency(data, doc_text) or f"{len(data['behavior_rows'])} 行行为 + {len(data['parameters'])} 个参数双向一致")
    run("C4", "待批准纪律", lambda: check_pending_approval_discipline(data, doc_text) or "全部参数与指标 PENDING_APPROVAL")
    run("C5", "五类动作映射一致", lambda: check_action_map(data) or "5 类映射一致，target 唯一")
    run("C6", "硬不变量与唯一触发解释", lambda: check_invariants(data) or "H-1..H-9 齐全，ONCE_PER_ACQUISITION 唯一")
    run("C7", "人工手算样例独立复算", lambda: f"{check_hand_cases(cases)} 个样例全部复算一致")
    run("C8", "上游只读文件哈希复算", lambda: check_upstream(bindings, project_root))
    run("C9", "文档必备覆盖与章节", lambda: check_doc_coverage(doc_text) or "关键词与章节齐全")
    run("C10", "禁止声明扫描（窄口径）", lambda: check_forbidden_claims(doc_text, data) or "未发现禁止声明")

    status = "ALL_PASS" if not errors else "FAILED"
    return {
        "schema_version": 1,
        "artifact": "s6a_g0_selfcheck_result",
        "task_id": data["task_id"],
        "run_id": data["run_id"],
        "status": status,
        "checks": checks,
        "errors": errors,
        "inputs": {
            "behavior_json_path": str(json_path),
            "behavior_json_sha256": sha256_file(json_path),
            "human_doc_path": str(doc_path),
            "human_doc_sha256": sha256_file(doc_path),
            "hand_cases_path": str(cases_path),
            "hand_cases_sha256": sha256_file(cases_path),
        },
        "scope_statement": SCOPE_STATEMENT,
        "limitations": [
            "只复算规格一致性与算术边界；不验证状态机行为（本轮尚无实现）",
            "C10 为窄口径文本扫描，不是完备的声明审计",
            "CHECKS_OK/ALL_PASS 不代表独立审查、G0/G2/G4/G5 或实物验收通过",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="阶段6 S6-A G0 包自检")
    parser.add_argument("--json", required=True, help="行为表 JSON 路径")
    parser.add_argument("--doc", required=True, help="人读规格路径")
    parser.add_argument("--cases", required=True, help="人工手算样例 JSON 路径")
    parser.add_argument("--upstream", required=True, help="上游绑定 JSON 路径")
    parser.add_argument("--out", required=True, help="自检结果输出路径")
    parser.add_argument("--project-root", default=None, help="工作树根（默认脚本上级目录）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else Path(__file__).resolve().parent.parent
    )
    json_path = Path(args.json).resolve()
    doc_path = Path(args.doc).resolve()
    cases_path = Path(args.cases).resolve()
    data = load_json(json_path)
    doc_text = doc_path.read_text(encoding="utf-8")
    cases = load_json(cases_path)
    bindings = load_json(Path(args.upstream).resolve())
    result = run_checks(
        data, doc_text, cases, bindings, project_root, doc_path, json_path, cases_path
    )
    Path(args.out).write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"status": result["status"], "errors": result["errors"]}, ensure_ascii=False))
    return 0 if result["status"] == "ALL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())