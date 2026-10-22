#!/usr/bin/env python3
"""阶段6 S6-B 确定性测试驱动（虚拟单调时钟 + JSON/JSONL + 预期断言 + 非零退出）。

用法：

    # 1) 先冻结预期（只写 expected_freeze.json，不运行状态机）
    python -B verification/s6b_run_cases.py --project-root D:/codex-worktrees/w6 \
        --run-dir report/evidence/S6-B/s6b_core_20261023_r01 --freeze-only

    # 2) 再运行（断言冻结哈希与当前 expected 一致，否则拒绝运行）
    python -B verification/s6b_run_cases.py --project-root D:/codex-worktrees/w6 \
        --run-dir report/evidence/S6-B/s6b_core_20261023_r01

设计要点（对应 H-7 与 CDX-20261022-012 §4）：

* 预期一律来自用例文件的 ``expected`` 块——由行为表独立推导/人工手算，**不由状态机生成**；
* 预期在运行前冻结 SHA-256；运行前若 expected 与冻结值不一致 → 退出码 2（拒绝运行）；
* 每行用例输出：预期状态/预期动作数/时间边界/实际日志（JSONL）/断言结果；
* 全部用例通过 → 退出码 0；任一断言不通过 → 退出码 1（非零失败退出）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.stage6.s6_actions import ActionLayer, OutcomePolicy  # noqa: E402
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

UTC8 = timezone(timedelta(hours=8))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def expected_hash(case: dict) -> str:
    """对单条用例的 expected 块取哈希（冻结与运行前复核都用它）。"""
    return sha256_text(_canonical(case["expected"]))


def freeze_payload(cases: dict, behavior_sha: str) -> dict:
    return {
        "schema_version": 1,
        "artifact": "s6b_expected_freeze",
        "task_id": "S6-B",
        "cases_file": cases.get("cases_file"),
        "cases_file_sha256": sha256_text(_canonical(cases)),
        "behavior_json_sha256": behavior_sha,
        "frozen_at_utc8": datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S"),
        "note": "预期由行为表独立推导/人工手算后冻结；运行时若不一致即拒绝运行（H-7）。",
        "expected_sha256": {case["case_id"]: expected_hash(case) for case in cases["cases"]},
    }


def _event_counts(records: list[dict]) -> dict:
    """统计四个 ACTION_* 事件名与 S_DEDUP 的出现次数（供 must_log 核对）。"""
    counts: dict[str, int] = {}
    for row in records:
        for key in ("event", "effective_event"):
            name = row.get(key)
            if name:
                counts[name] = counts.get(name, 0) + 1
    return counts


def run_case(case: dict, pack: ParamPack) -> dict:
    """运行单条用例，返回实际观测（含逐帧日志）。"""
    period_ns = int(case.get("period_ns", 100_000_000))
    policy = OutcomePolicy(
        fail_attempts=case.get("outcome_policy", {}).get("fail_attempts"),
        unobserved_attempts=case.get("outcome_policy", {}).get("unobserved_attempts"),
        duplicate_ack_attempts=case.get("outcome_policy", {}).get("duplicate_ack_attempts"),
    )
    core = GestureInteractionCore(pack)
    layer = ActionLayer(pack, policy)
    session_id = case.get("session_id", "s1")
    t_ns = int(case.get("t_start_ns", 0))
    logs: list[dict] = []
    actions: list[dict] = []
    submitted_at_frames: list[int] = []
    transitions: list[str] = []

    for index, raw in enumerate(case["events"]):
        if "dt_ns" in raw:
            t_ns += int(raw["dt_ns"])
        else:
            t_ns = int(raw.get("t_ns", t_ns + (0 if index == 0 else period_ns)))
        event = dict(raw)
        event.pop("dt_ns", None)
        event.pop("t_ns", None)
        event["t_input_ns"] = t_ns
        event.setdefault("session_id", session_id)
        if event.get("session_id") != session_id:
            session_id = event["session_id"]
        step = core.step(event)
        log = step["log"]
        log["event_index"] = index
        log["t_input_ns"] = t_ns
        if log.get("transition"):
            transitions.append(str(log["transition"]))
        request = step["action_request"]
        if request is not None:
            record = layer.submit(request, t_ns)
            ack_log = core.note_action_ack(record)
            ack_log["event_index"] = index
            ack_log["t_input_ns"] = t_ns
            actions.append(record)
            logs.append({"kind": "action_ack", **ack_log})
            if record.get("submit_result") == "success" and not record.get("suppression"):
                submitted_at_frames.append(log.get("frame_id"))
            if ack_log.get("transition"):
                transitions.append(str(ack_log["transition"]))
        logs.append({"kind": "step", **log})

    counter_highs: dict[str, int] = {}
    suppression_events = set(core.suppressions)
    markers: set[str] = set()
    for row in logs:
        if row.get("kind") != "step":
            continue
        for key, value in (row.get("counters") or {}).items():
            if isinstance(value, int) and not isinstance(value, bool):
                counter_highs[key] = max(counter_highs.get(key, 0), value)
        for name in row.get("suppression_events") or []:
            suppression_events.add(str(name))
        if row.get("tie_resolved"):
            markers.add(str(row["tie_resolved"]))

    return {
        "case_id": case["case_id"],
        "matrix_class": case.get("matrix_class"),
        "final_state": core.state,
        "transitions": transitions,
        "action_summary": layer.summary(),
        "core_counters": dict(core.counters),
        "submitted_at_frames": submitted_at_frames,
        "suppressions": sorted(suppression_events),
        "markers": sorted(markers),
        "counter_highs": counter_highs,
        "window_complete_ns": next(
            (row["window_complete_ns"] for row in logs
             if row.get("kind") == "step" and row.get("window_complete_ns") is not None),
            core.window_complete_ns,
        ),
        "action_records": actions,
        "logs": logs,
    }


def compare(case: dict, observed: dict) -> list[str]:
    """返回断言失败列表（空列表表示通过）。"""
    expected = case["expected"]
    failures: list[str] = []
    if observed["final_state"] != expected["final_state"]:
        failures.append(f"final_state 预期 {expected['final_state']}，实际 {observed['final_state']}")
    for key in ("transitions",):
        if key in expected and observed[key] != expected[key]:
            failures.append(f"{key} 预期 {expected[key]}，实际 {observed[key]}")
    summary = observed["action_summary"]
    for key in ("action_submitted", "action_effective", "action_failed",
                "action_unobserved", "dedup_suppressed", "visible_state_changes",
                "final_display_state", "final_channel"):
        if key in expected.get("action_summary", {}) and summary.get(key) != expected["action_summary"][key]:
            failures.append(f"action_summary.{key} 预期 {expected['action_summary'][key]}，实际 {summary.get(key)}")
    for key, want in expected.get("core_counters", {}).items():
        got = observed["core_counters"].get(key)
        if got != want:
            failures.append(f"core_counters.{key} 预期 {want}，实际 {got}")
    for key, want in expected.get("counter_highs", {}).items():
        got = observed["counter_highs"].get(key)
        if got != want:
            failures.append(f"counter_highs.{key} 预期 {want}，实际 {got}")
    for marker in expected.get("markers_include", []):
        if marker not in observed["markers"]:
            failures.append(f"缺少标记 {marker}")
    if "window_complete_ns" in expected and observed["window_complete_ns"] != expected["window_complete_ns"]:
        failures.append(
            f"window_complete_ns 预期 {expected['window_complete_ns']}，实际 {observed['window_complete_ns']}"
        )
    if "submitted_at_frames" in expected and observed["submitted_at_frames"] != expected["submitted_at_frames"]:
        failures.append(
            f"submitted_at_frames 预期 {expected['submitted_at_frames']}，实际 {observed['submitted_at_frames']}"
        )
    for name in expected.get("suppressions_include", []):
        if name not in observed["suppressions"] and not any(
            row.get("suppression") == name for row in observed["action_records"]
        ):
            failures.append(f"缺少抑制事件 {name}")
    if "max_action_submitted" in expected and summary["action_submitted"] > expected["max_action_submitted"]:
        failures.append(
            f"action_submitted 超过上限 {expected['max_action_submitted']}：{summary['action_submitted']}"
        )
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-B 确定性测试驱动（虚拟时钟 + 预期断言）")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--cases", default=None, help="用例文件（默认 <run-dir>/cases/case_matrix.json）")
    parser.add_argument("--freeze-only", action="store_true", help="只冻结预期，不运行状态机")
    parser.add_argument("--force-freeze", action="store_true", help="允许覆盖已存在的冻结文件")
    parser.add_argument("--behavior-json", default=None,
                        help="行为表 JSON（默认 docs/stage6/s6a_stage6_g0_behavior_v1.json；探针用副本）")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    cases_path = Path(args.cases).resolve() if args.cases else run_dir / "cases/case_matrix.json"
    freeze_path = run_dir / "expected_freeze.json"
    if not cases_path.is_file():
        print(f"用例文件不存在：{cases_path}")
        return 2
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    cases["cases_file"] = cases_path.relative_to(root).as_posix()
    # N-09：在同一字典（含 cases_file 身份字段）上取哈希，冻结与运行口径一致
    cases_sha = sha256_text(_canonical(cases))

    behavior_json = (Path(args.behavior_json).resolve() if args.behavior_json
                     else root / "docs/stage6/s6a_stage6_g0_behavior_v1.json")
    try:
        pack = ParamPack(behavior_json, project_root=root)
    except Exception as exc:  # noqa: BLE001
        print(f"参数装载失败：{type(exc).__name__}: {exc}")
        return 2
    payload = freeze_payload(cases, pack.behavior_sha256)

    if args.freeze_only:
        if freeze_path.exists() and not args.force_freeze:
            existing = json.loads(freeze_path.read_text(encoding="utf-8"))
            if existing.get("expected_sha256") != payload["expected_sha256"]:
                print("已存在不同的冻结文件；如需覆盖请加 --force-freeze")
                return 2
        run_dir.mkdir(parents=True, exist_ok=True)
        freeze_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "EXPECTED_FROZEN", "cases": len(payload["expected_sha256"])}, ensure_ascii=False))
        return 0

    if not freeze_path.is_file():
        print("缺少 expected_freeze.json：必须先冻结预期再运行（H-7）")
        return 2
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    # N-09：运行前同时校验**用例文件**哈希（冻结点之后改用例即拒运行），
    # 不只校验每条 expected；两者共同保证「先冻结、后运行」不被绕过（H-7）。
    if frozen.get("cases_file_sha256") != cases_sha:
        print("用例文件在冻结后被修改：expected_freeze.json.cases_file_sha256 与当前不一致——拒绝运行")
        return 2
    for case in cases["cases"]:
        case_id = case["case_id"]
        want = frozen["expected_sha256"].get(case_id)
        got = expected_hash(case)
        if want != got:
            print(f"预期在冻结后被修改：{case_id}（冻结 {want}，当前 {got}）——拒绝运行")
            return 2

    results: list[dict] = []
    log_dir = run_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    failed_total = 0
    for case in cases["cases"]:
        observed = run_case(case, pack)
        failures = compare(case, observed)
        with (log_dir / f"{case['case_id']}.jsonl").open("w", encoding="utf-8") as handle:
            for row in observed["logs"]:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        results.append({
            "case_id": case["case_id"],
            "matrix_class": case.get("matrix_class"),
            "expected": case["expected"],
            "observed": {
                "final_state": observed["final_state"],
                "transitions": observed["transitions"],
                "action_summary": observed["action_summary"],
                "core_counters": observed["core_counters"],
                "submitted_at_frames": observed["submitted_at_frames"],
                "suppressions": observed["suppressions"],
                "markers": observed["markers"],
                "counter_highs": observed["counter_highs"],
                "window_complete_ns": observed["window_complete_ns"],
                # BLK-r02-2：动作记录与四个 ACTION_* 事件名必须进交付证据（原实现只在内存里）
                "action_records": observed["action_records"],
                "action_event_counts": _event_counts(observed["action_records"]),
            },
            "assertions_failed": failures,
            "status": "PASS" if not failures else "FAIL",
            "log_file": f"logs/{case['case_id']}.jsonl",
        })
        failed_total += len(failures)

    report = {
        "schema_version": 1,
        "artifact": "s6b_deterministic_run_report",
        "task_id": "S6-B",
        "run_id": run_dir.name,
        "behavior_json_sha256": pack.behavior_sha256,
        "contract_version": pack.data.get("artifact_version"),
        "parameters_pending_approval": pack.snapshot()["all_parameters_pending_approval"],
        "expected_frozen_sha256": freeze_path.relative_to(root).as_posix(),
        "expected_freeze_sha256": hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
        "case_count": len(results),
        "status": "PASS" if failed_total == 0 else "FAIL",
        "assertions_failed": failed_total,
        "cases": results,
        "scope_statement": (
            "本报告只覆盖离线确定性回放（注入输入 + 虚拟单调时钟）；"
            "不代表摄像头/HDMI/板上验收，也不代表独立审查通过。"
        ),
    }
    (run_dir / "run_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": report["status"],
        "case_count": report["case_count"],
        "assertions_failed": failed_total,
        "failed_cases": [row["case_id"] for row in results if row["status"] == "FAIL"],
    }, ensure_ascii=False))
    return 0 if failed_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())