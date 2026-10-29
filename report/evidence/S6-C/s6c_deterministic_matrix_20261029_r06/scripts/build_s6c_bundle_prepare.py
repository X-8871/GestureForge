#!/usr/bin/env python3
"""封装 S6-C 离线矩阵证据；只读取 r04 与历史 r08，不重跑测试。"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath


UTC8 = timezone(timedelta(hours=8))
ROOT = Path(r"D:\codex-worktrees\w6")
RUN_ID = "s6c_deterministic_matrix_20261029_r06"
RUN_DIR = ROOT / "report/evidence/S6-C" / RUN_ID
SCRIPT = RUN_DIR / "scripts/build_s6c_bundle.py"
R04 = ROOT / "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r04"
R02_MATRIX = ROOT / "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r02/matrix_coverage.json"
RUNBOOK_SOURCE = Path(
    r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\codex_mailbox"
    r"\CDX-20261022-012-stage6-interaction-runbook.md"
)
RECEIPT_SOURCE = ROOT / "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json"
MAIN_VERIFICATION = Path(r"D:\FPGA_Competition\verification")
INPUTS_MANIFEST = RUN_DIR / "inputs_manifest.json"
DELIVERY_MANIFEST = RUN_DIR / "delivery_manifest.json"
EXECUTION_RECORD = RUN_DIR / "execution_record.json"
MATRIX_PATH = RUN_DIR / "matrix_coverage.json"
SOURCE_BINDING = RUN_DIR / "source_binding.json"
PYTHON = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
EXPECTED_HEAD = "52dc7618153eed61f49f4bca116755dde7a56ac4"
EXPECTED_BRANCH = "stage6-interact-prep"
R08_RUN_ID = "s6b_current_20261029_r08"
R08_SOURCE_COMMIT = "e735a5afb5b474793408ec1e61da111006c70e60"
R08_CORE_SHA256 = "8cf5c7f0e89110068a00894f764f65f8a4fc3df2c5db55d9f46f243f348995d9"
HEAD_OLD_TEST_SHA256 = "8c37e67b30cbad770249f0f0664dc328250c63f060b6ccfe67e19186b04781c3"
R04_CURRENT_TEST_SHA256 = "63cdb40865f257d9941fdbf83abbca1ed3c8be0575b2f0bf903de0a7349f73c0"
RUNBOOK_SHA256 = "697506c743ebc6618c68380a86ab80b62f263ad16dbceefb252f260c2392e89f"
RECEIPT_SHA256 = "f8b2cde23f11e132b7df62a7e60df6f6a5d560cf4b7d9a4efd464462b2ba7394"
CURRENT_SOURCES = (
    "src/stage6/s6_core.py",
    "src/stage6/s6_actions.py",
    "src/stage6/s6_params.py",
    "src/stage6/s6_receipts.py",
    "verification/s6b_run_cases.py",
    "verification/test_s6b_core_regressions.py",
    "verification/test_s6b_probe.py",
    "verification/test_s6b_build_evidence.py",
    "verification/test_s6c_receipt_boundary.py",
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "docs/stage6/s6b_frozen_interface_v1.json",
    "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json",
)
MISSING_R08_CASE_ROWS = {
    "C12-gate-reopen-new-acquisition": 1,
    "C12-m8-two-acquisitions": 2,
    "C12-m2-m12-new-target": 4,
}


def now_utc8() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(value)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 退出码 {result.returncode}: {result.stderr}")
    return result.stdout.strip()


def git_blob_sha(commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", f"{commit}:{path}"],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git blob 读取失败：{commit}:{path}")
    return sha256_bytes(result.stdout)


def copy_file_exact(source: Path, destination: Path) -> str:
    if not source.is_file() or source.is_symlink():
        raise RuntimeError(f"输入不是普通文件：{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    destination.write_bytes(data)
    actual = sha256_bytes(data)
    if sha256_file(destination) != actual:
        raise RuntimeError(f"复制后字节哈希不一致：{source} -> {destination}")
    return actual


def copy_tree_exact(source: Path, destination: Path) -> None:
    if not source.is_dir() or source.is_symlink() or destination.exists():
        raise RuntimeError(f"目录复制前置条件不满足：{source} -> {destination}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"输入目录含链接，拒绝复制：{path}")
        if not (path.is_file() or path.is_dir()):
            raise RuntimeError(f"输入目录含非普通文件对象：{path}")
    shutil.copytree(source, destination)
    for path in source.rglob("*"):
        if path.is_file():
            relative = path.relative_to(source)
            copied = destination / relative
            if sha256_file(path) != sha256_file(copied):
                raise RuntimeError(f"目录复制哈希不一致：{path} -> {copied}")


def require_baseline() -> None:
    if ROOT.resolve() != Path(git_text("rev-parse", "--show-toplevel")).resolve():
        raise RuntimeError("工作树根路径与 Git 返回值不一致")
    if git_text("rev-parse", "HEAD") != EXPECTED_HEAD:
        raise RuntimeError("HEAD 已变化，拒绝继续封包")
    if git_text("branch", "--show-current") != EXPECTED_BRANCH:
        raise RuntimeError("分支已变化，拒绝继续封包")
    if not RUN_DIR.is_dir() or SCRIPT.resolve() != Path(__file__).resolve():
        raise RuntimeError("RunId 或封包脚本位置不匹配")


def project_rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def manifest_entry(path: Path, role: str, reason: str) -> dict[str, str]:
    return {
        "path": project_rel(path),
        "sha256": sha256_file(path),
        "role": role,
        "keep_reason": reason,
        "hash_basis": "worktree_disk",
    }


def expected_frame_times(events: list[dict]) -> list[dict]:
    current_ns = 0
    result = []
    for event in events:
        delta = event.get("dt_ns", 0)
        if type(delta) is not int or delta < 0:
            raise RuntimeError("固定回放输入含无效 dt_ns")
        current_ns += delta
        if event.get("frame_id") is not None:
            result.append({
                "frame_id": event.get("frame_id"),
                "kind": event["kind"],
                "t_input_ns": current_ns,
            })
    return result


def logged_frame_times(log_path: Path) -> list[dict]:
    rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line]
    return [
        {"frame_id": row.get("frame_id"), "kind": row.get("event_kind"),
         "t_input_ns": row.get("t_input_ns"), "input_state": row.get("input_state"),
         "transition": row.get("transition"), "from_state": row.get("from_state"),
         "to_state": row.get("to_state"), "event_index": row.get("event_index"),
         "reason": row.get("reason")}
        for row in rows
        if row.get("kind") == "step" and row.get("frame_id") is not None
    ]


def case_detail(case: dict, matrix_case: dict, log_path: Path, display_path: str,
                source_run_id: str) -> dict:
    if case.get("status") != "PASS" or case.get("assertions_failed"):
        raise RuntimeError(f"历史回放子用例未通过：{case.get('case_id')}")
    if case.get("expected") != matrix_case.get("expected"):
        raise RuntimeError(f"expected 与固定输入矩阵不一致：{case.get('case_id')}")
    expected_times = expected_frame_times(matrix_case.get("events", []))
    actual_times = logged_frame_times(log_path)
    expected_identity = [(row["frame_id"], row["t_input_ns"]) for row in expected_times]
    actual_identity = [(row["frame_id"], row["t_input_ns"]) for row in actual_times]
    if expected_identity != actual_identity or len(expected_times) != len(actual_times):
        raise RuntimeError(f"实际日志的 frame_id/虚拟时间与固定输入不一致：{case.get('case_id')}")
    for expected, actual in zip(expected_times, actual_times):
        if actual["kind"] != expected["kind"]:
            duplicate_reclassification = (
                expected["kind"] == "E_FRAME_RESULT"
                and actual["kind"] == "E_FRAME_DUPLICATE"
                and actual["input_state"] == "DUPLICATE"
            )
            if not duplicate_reclassification:
                raise RuntimeError(
                    f"事件分类与固定输入不一致：{case.get('case_id')}，"
                    f"frame_id={expected['frame_id']}，预期 {expected['kind']}，"
                    f"日志 {actual['kind']}/{actual['input_state']}"
                )
    return {
        "case_id": case["case_id"],
        "matrix_class": matrix_case.get("matrix_class"),
        "description": matrix_case.get("description"),
        "expected": case["expected"],
        "actual": case["observed"],
        "time_boundary_ns": case["expected"].get("window_complete_ns"),
        "fixed_virtual_input_times": expected_times,
        "actual_frame_event_classifications": actual_times,
        "actual_log_path": display_path,
        "actual_log_sha256": sha256_file(log_path),
        "source_run_id": source_run_id,
        "assertions_failed": case.get("assertions_failed", []),
        "status": case["status"],
    }


def create_matrix_and_bindings(record: dict) -> None:
    r04_inputs = RUN_DIR / "inputs/r04_preflight/inputs"
    r04_outputs = RUN_DIR / "inputs/r04_preflight/outputs"
    prior = read_json(RUN_DIR / "inputs/prior_r02_matrix_coverage.json")
    r08_root = r04_inputs / "r08_historical/report/evidence/S6-B" / R08_RUN_ID
    r08_manifest = read_json(r08_root / "delivery_manifest.json")
    r08_report_path = r08_root / "matrix_source_r03/run_report.json"
    r08_matrix_path = r08_root / "matrix_source_r03/cases/case_matrix.json"
    r08_report = read_json(r08_report_path)
    r08_matrix = read_json(r08_matrix_path)
    r08_run_files = {row.get("path"): row for row in r08_manifest.get("files", [])}
    old_test_snapshot = r08_root / "inputs/source_snapshots/verification/test_s6b_core_regressions.py"
    current_core = ROOT / "src/stage6/s6_core.py"
    current_test = ROOT / "verification/test_s6b_core_regressions.py"
    head_test_sha = git_blob_sha(EXPECTED_HEAD, "verification/test_s6b_core_regressions.py")
    if r08_manifest.get("source_commit") != R08_SOURCE_COMMIT:
        raise RuntimeError("r08 清单来源提交与已核验值不符")
    if sha256_file(current_core) != R08_CORE_SHA256:
        raise RuntimeError("当前核心哈希已变化")
    if sha256_file(old_test_snapshot) != HEAD_OLD_TEST_SHA256 or head_test_sha != HEAD_OLD_TEST_SHA256:
        raise RuntimeError("r08 历史测试与当前 HEAD blob 绑定不一致")
    if sha256_file(current_test) != R04_CURRENT_TEST_SHA256:
        raise RuntimeError("r04 运行测试文件已变化")
    if r08_run_files.get("src/stage6/s6_core.py", {}).get("sha256") != R08_CORE_SHA256:
        raise RuntimeError("r08 清单未绑定相同的核心字节")
    if r08_run_files.get("verification/test_s6b_core_regressions.py", {}).get("sha256") != HEAD_OLD_TEST_SHA256:
        raise RuntimeError("r08 清单未绑定 HEAD 中的历史测试字节")
    if r08_report.get("status") != "PASS" or r08_report.get("case_count") != 26:
        raise RuntimeError("r08 历史回放报告不是 26/26 PASS")

    old_cases = {case["case_id"]: case for case in r08_report["cases"]}
    matrix_cases = {case["case_id"]: case for case in r08_matrix["cases"]}
    if len(old_cases) != 26 or set(old_cases) != set(matrix_cases):
        raise RuntimeError("r08 run_report 与固定输入 case_matrix 的 26 个 ID 不一致")
    if len(old_cases) != len(r08_report["cases"]):
        raise RuntimeError("r08 run_report 中存在重复 case_id")

    rows = copy.deepcopy(prior["formal_11_rows"])
    case_to_row: dict[str, int] = {}
    for row_index, row in enumerate(rows):
        for case_id in row.get("cases", []):
            if case_id == "C11-duplicate-ack":
                continue
            if case_id in case_to_row:
                raise RuntimeError(f"r02 映射重复 case_id：{case_id}")
            case_to_row[case_id] = row_index
    missing = set(old_cases) - set(case_to_row)
    if missing != set(MISSING_R08_CASE_ROWS):
        raise RuntimeError(f"r02 覆盖缺口與核定缺口不符：{sorted(missing)}")
    case_to_row.update(MISSING_R08_CASE_ROWS)
    unknown = set(case_to_row) - set(old_cases)
    if unknown or set(case_to_row) != set(old_cases):
        raise RuntimeError(f"11 行映射与 r08 26 条矩阵不一致：{sorted(unknown)}")

    source_matrix_dir = r08_root / "matrix_source_r03"
    all_details: dict[str, dict] = {}
    row_case_ids: dict[int, list[str]] = {index: [] for index in range(11)}
    for case in r08_report["cases"]:
        case_id = case["case_id"]
        matrix_case = matrix_cases[case_id]
        row_index = case_to_row[case_id]
        log_relative = PurePosixPath(case["log_file"])
        if log_relative.is_absolute() or ".." in log_relative.parts:
            raise RuntimeError(f"历史日志路径不安全：{case['log_file']}")
        log_path = source_matrix_dir.joinpath(*log_relative.parts)
        if not log_path.is_file():
            raise RuntimeError(f"历史矩阵日志缺失：{log_path}")
        package_path = RUN_DIR / "inputs/r04_preflight/inputs/r08_historical/report/evidence/S6-B" / R08_RUN_ID / "matrix_source_r03" / Path(*log_relative.parts)
        display_path = project_rel(package_path)
        detail = case_detail(case, matrix_case, log_path, display_path, "s6b_current_20261029_r03")
        all_details[case_id] = detail
        row_case_ids[row_index].append(case_id)

    for index, row in enumerate(rows):
        ids = row_case_ids[index]
        row["cases"] = ids
        row["case_count"] = len(ids)
        row["case_details"] = [all_details[case_id] for case_id in ids]
        row["each_case_records_expected_state_action_time_actual_log_and_assertions"] = True
        row["status"] = "PASS"

    c11_case_file = r04_inputs / "C11_duplicate_ack_case.json"
    c11_input = read_json(c11_case_file)["cases"][0]
    c11_report_path = r04_outputs / "duplicate_ack_matrix/run_report.json"
    c11_report = read_json(c11_report_path)
    if c11_report.get("status") != "PASS" or c11_report.get("case_count") != 1:
        raise RuntimeError("r04 C11 duplicate ACK 回放报告不是 PASS")
    c11_case = c11_report["cases"][0]
    c11_log = r04_outputs / "duplicate_ack_matrix/logs/C11-duplicate-ack.jsonl"
    c11_detail = case_detail(
        c11_case, c11_input, c11_log,
        project_rel(RUN_DIR / "inputs/r04_preflight/outputs/duplicate_ack_matrix/logs/C11-duplicate-ack.jsonl"),
        "s6c_deterministic_matrix_20261029_r04",
    )
    observed_actions = c11_case.get("observed", {}).get("action_records", [])
    summary = c11_case.get("observed", {}).get("action_summary", {})
    if (len(observed_actions) != 1 or observed_actions[0].get("duplicate_ack") is not True
            or summary.get("action_submitted") != 1 or summary.get("action_effective") != 1):
        raise RuntimeError("C11 duplicate ACK 结果字段与一次提交/一次生效约束不一致")
    c11_detail["duplicate_ack_observed"] = True
    c11_detail["action_submitted"] = summary["action_submitted"]
    c11_detail["action_effective"] = summary["action_effective"]
    rows[10]["supplemental_cases"] = ["C11-duplicate-ack"]
    rows[10]["supplemental_case_details"] = [c11_detail]

    row8 = rows[7]
    row8["status"] = "BLOCKED"
    row8["subcase_disposition"] = [
        {"item": "duplicate/reorder/missing/session-change RESET log case",
         "status": "PASS", "case_id": "C8-duplicate-reorder-missing-restart"},
        {"item": "B25 same-session large frame_id rollback reset threshold",
         "status": "BLOCKED",
         "reason": "已批准规格未给出数值阈值；不得自行设定或把倒序子用例扩展为大回退复位验收。"},
        {"item": "0xFFFFFFFE frame_id wrap boundary cross-document match",
         "status": "BLOCKED",
         "reason": "人类规格与机器 JSON 未形成一致的显式边界语义，需正式统一后才能判定整行。"},
    ]
    row8["blocked_items"] = [item for item in row8["subcase_disposition"] if item["status"] == "BLOCKED"]

    flattened = []
    for row_index, row in enumerate(rows, 1):
        for detail in row["case_details"]:
            flattened.append({"formal_row_number": row_index, **detail})
        for detail in row.get("supplemental_case_details", []):
            flattened.append({"formal_row_number": row_index, "supplemental": True, **detail})
    if len([item for item in flattened if not item.get("supplemental")]) != 26:
        raise RuntimeError("正式 11 行未覆盖全部 26 个 r08 历史用例")
    if len(flattened) != 27:
        raise RuntimeError("正式矩阵与 C11 补充项记录数不为 27")

    receipt_copy = r04_inputs / "U6-02_r07_decision_receipt.json"
    approval_context = r04_inputs / "user_approval_context.md"
    if sha256_file(RECEIPT_SOURCE) != RECEIPT_SHA256 or sha256_file(receipt_copy) != RECEIPT_SHA256:
        raise RuntimeError("U6-02 r07 批准回执哈希不匹配")
    if RECEIPT_SOURCE.read_bytes() != receipt_copy.read_bytes():
        raise RuntimeError("U6-02 r07 当前正式回执与 r04 绑定快照不同")
    if "业务结果字段" not in approval_context.read_text(encoding="utf-8"):
        raise RuntimeError("用户批准的重复结果比较口径快照缺少关键文本")

    record["source_bindings"] = {
        "source_commit": EXPECTED_HEAD,
        "branch": EXPECTED_BRANCH,
        "current_worktree_files": [
            {"path": relative, "sha256": sha256_file(ROOT / relative), "hash_basis": "worktree_disk"}
            for relative in CURRENT_SOURCES
        ],
        "head_blob_test_sha256": head_test_sha,
        "current_core_sha256": sha256_file(current_core),
        "current_test_sha256": sha256_file(current_test),
        "historical_r08": {
            "run_id": R08_RUN_ID,
            "source_commit": r08_manifest["source_commit"],
            "source_run_id": "s6b_current_20261029_r03",
            "matrix_case_count": 26,
            "matrix_status": r08_report["status"],
            "core_sha256": R08_CORE_SHA256,
            "historical_test_sha256": HEAD_OLD_TEST_SHA256,
            "current_HEAD_test_blob_matches_historical": head_test_sha == HEAD_OLD_TEST_SHA256,
        },
    }
    write_json(EXECUTION_RECORD, record)
    write_json(SOURCE_BINDING, {
        "schema_version": 1,
        "task_id": "S6-C",
        "run_id": RUN_ID,
        "status": "BOUND_OFFLINE_MATRIX_BLOCKED_AT_ROW_8",
        "current_baseline": record["source_bindings"],
        "historical_r08_delivery_manifest_sha256": sha256_file(r08_root / "delivery_manifest.json"),
        "historical_r08_run_report_sha256": sha256_file(r08_report_path),
        "historical_r08_case_matrix_sha256": sha256_file(r08_matrix_path),
        "historical_r08_isolated_evidence_checker": read_json(r04_inputs / "r08_historical/historical_evidence_checker.json"),
        "historical_r08_isolated_hash_basis_checker": read_json(r04_inputs / "r08_historical/historical_hash_basis_strict.json"),
        "r04_execution_record_sha256": sha256_file(RUN_DIR / "inputs/r04_preflight/execution_record.json"),
        "u6_02_r07_receipt": {
            "path": project_rel(RECEIPT_SOURCE), "status": "APPROVED_20261025",
            "sha256": sha256_file(RECEIPT_SOURCE),
        },
        "approved_duplicate_result_comparison_context": {
            "path": project_rel(RUN_DIR / "inputs/r04_preflight/inputs/user_approval_context.md"),
            "sha256": sha256_file(approval_context),
            "scope": "比较业务结果字段；排除接收时间等传输上下文。",
        },
        "r04_bound_commands": record["bound_r04_commands"],
        "hardware_access": "NOT_USED",
    })

    matrix = {
        "schema_version": 1,
        "task_id": "S6-C",
        "run_id": RUN_ID,
        "source_runbook": project_rel(RUN_DIR / "inputs/formal_6c_runbook.md") + " §4",
        "source_runbook_sha256": sha256_file(RUN_DIR / "inputs/formal_6c_runbook.md"),
        "existing_matrix": {
            "run_id": R08_RUN_ID,
            "source_run_id": "s6b_current_20261029_r03",
            "source_commit": R08_SOURCE_COMMIT,
            "status": "PASS",
            "case_count": 26,
            "core_sha256": R08_CORE_SHA256,
            "current_core_sha256": sha256_file(current_core),
            "test_source_sha256": HEAD_OLD_TEST_SHA256,
        },
        "supplemental_matrix": {
            "case_id": "C11-duplicate-ack",
            "source_run_id": "s6c_deterministic_matrix_20261029_r04",
            "freeze_exit_code": 0,
            "run_exit_code": 0,
            "case_status": "PASS",
            "assertions_failed": [],
            "duplicate_ack_log_observed": True,
            "log_path": c11_detail["actual_log_path"],
            "log_sha256": c11_detail["actual_log_sha256"],
            "case_detail": c11_detail,
        },
        "formal_11_rows": rows,
        "case_records": flattened,
        "approved_decision_bindings": {
            "U6-02_r07": {"status": "APPROVED_20261025", "sha256": RECEIPT_SHA256},
            "same_frame_duplicate_result_comparison": {
                "status": "APPROVED", "scope": "比较业务结果字段；排除接收时间等传输上下文。",
                "context_sha256": sha256_file(approval_context),
            },
        },
        "coverage_verdict": "BLOCKED",
        "coverage_summary": {
            "historical_r08_cases_bound": 26,
            "r04_supplemental_duplicate_ack_bound": 1,
            "formal_rows_total": 11,
            "formal_rows_pass": 10,
            "formal_rows_blocked": [8],
            "all_11_rows_pass": False,
        },
        "blocked_conditions": [
            {"id": "B25-SAME-SESSION-LARGE-ROLLBACK", "status": "BLOCKED",
             "reason": "同会话大回退阈值没有已批准数值判据。"},
            {"id": "S6A-FRAME-ID-WRAP-DOCUMENT-MISMATCH", "status": "BLOCKED",
             "reason": "0xFFFFFFFE 边界在人类规格与机器 JSON 间没有一致的显式语义。"},
        ],
        "scope_note": (
            "11 行逐例记录绑定 r08 的历史 26 条固定输入/日志，另绑定 r04 的重复 ACK 补充回放。"
            "R04 测试输出作为只读固定输入，本 RunId 未重跑测试。整体验收因第 8 行保持 BLOCKED。"
            "结果仅适用于指定提交/文件字节及离线回放，不代表实时性能、G3、G4 或 G5。"
        ),
    }
    write_json(MATRIX_PATH, matrix)

    run_summary = f"""# S6-C 离线确定性矩阵封包摘要（{RUN_ID}）

- 正式矩阵依据：`{project_rel(RUN_DIR / 'inputs/formal_6c_runbook.md')} §4`，SHA-256 `{sha256_file(RUN_DIR / 'inputs/formal_6c_runbook.md')}`。
- 历史 S6-B r08 来源提交 `{R08_SOURCE_COMMIT}`；其 26 条用例、固定输入、run_report 与 JSONL 日志已在隔离副本通过证据及严格哈希复核。核心 SHA-256 `{R08_CORE_SHA256}` 与当前一致；r08 历史测试 blob 与当前 HEAD `{EXPECTED_HEAD}` 的 blob SHA-256 `{HEAD_OLD_TEST_SHA256}` 一致。
- r04 实际运行日志作为只读输入绑定：S6-B 回归 40 项、S6-C receipt boundary 17 项、C11 duplicate ACK 回放、freeze 及 `git diff --check`；本 RunId 不重跑这些命令。当前新增测试磁盘 SHA-256 `{R04_CURRENT_TEST_SHA256}` 与 r08 历史测试字节不同，二者各自范围已分开绑定。
- 矩阵表逐项列出历史 26 条的预期、实际、窗口时间边界、固定虚拟输入时序、日志路径/哈希及断言；C11 duplicate ACK 单列为 r04 补充回放，观察到重复 ACK 不重复提交/生效，计数均为 1。
- 第 8 行与整体判定为 **BLOCKED**：已跑的 duplicate/reorder/missing/session-change 子用例通过；B25 同会话大回退阈值未批准，且 `0xFFFFFFFE` 边界的文档/机器规格差异未统一。不得把该行或整体验收标 PASS。
- U6-02 r07 批准回执 SHA-256 `{RECEIPT_SHA256}`；重复 frame 结果按已批准的业务字段口径绑定，不比较接收时间等传输上下文。

本包未访问板卡、JTAG、串口、摄像头或 HDMI。G2 独立审查待进行；G3 未执行；T6-A03 因缺阶段4实测帧周期 P 保持 NOT_RUN；6-E 实物验收未执行；阶段4/5真实结果链路仍 BLOCKED；不声称 G4 或阶段6 G5 通过。
"""
    write_text(RUN_DIR / "run_summary.md", run_summary)
    write_text(RUN_DIR / "limitations.md", """# S6-C 当前限制

- 第 8 行和整体矩阵保持 BLOCKED：B25 没有已批准的同会话大回退数值阈值；0xFFFFFFFE 的人类规格与机器 JSON 语义不一致。
- r08 的 26 条结果来自历史离线回放，其核心/历史测试字节按清单绑定；r04 的新测试输出单独作为只读固定输入，不把历史测试范围扩展为当前新增测试。
- 本 RunId 只封装证据与运行只读校验器，没有重跑单元测试；机械清单核验不等于行为审查或独立 G2。
- 没有执行板卡、JTAG、串口、摄像头、HDMI、实时会话或阶段4/5真实集成。
- T6-A03 缺阶段4实测帧周期 P，状态为 NOT_RUN；6-E 实物验收 NOT_RUN；G3 未满足，G4/G5 不作通过声明。
""")

    for command in read_json(RUN_DIR / "inputs/r04_preflight/execution_record.json")["commands"]:
        if command.get("exit_code") != 0:
            raise RuntimeError(f"r04 被绑定的命令不是成功退出：{command.get('name')}")
    record["matrix_status"] = "BLOCKED"
    record["matrix_case_count"] = 26
    record["supplemental_case_count"] = 1
    record["matrix_checks"] = {
        "formal_rows": 11, "pass": 10, "blocked": [8], "overall": "BLOCKED"
    }
    record["status"] = "PREPARED_BLOCKED_CHECKS_PENDING"
    write_json(EXECUTION_RECORD, record)


def file_role(path: Path) -> str:
    relative = path.relative_to(RUN_DIR).as_posix()
    if relative.startswith("scripts/"):
        return "source"
    if "/source_snapshots/src/" in relative or "/source_snapshots/verification/" in relative:
        return "source"
    if path.suffix.lower() in {".log", ".jsonl"} or path.name.endswith("_output.txt"):
        return "log"
    if relative.startswith("inputs/"):
        return "input"
    if relative.startswith("outputs/"):
        return "log"
    return "result"


def all_delivery_files() -> list[dict[str, str]]:
    entries = []
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise RuntimeError(f"交付目录出现链接：{path}")
        if path == DELIVERY_MANIFEST:
            continue
        entries.append(manifest_entry(path, file_role(path), f"S6-C 离线矩阵封包文件：{path.relative_to(RUN_DIR).as_posix()}"))
    for relative in CURRENT_SOURCES:
        entries.append(manifest_entry(ROOT / relative, "source", f"本轮实际来源文件字节：{relative}"))
    return sorted(entries, key=lambda row: row["path"])


def write_hashes_file() -> None:
    lines = []
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file() or path in {RUN_DIR / "hashes_sha256.txt", DELIVERY_MANIFEST}:
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(RUN_DIR).as_posix()}")
    write_text(RUN_DIR / "hashes_sha256.txt", "\n".join(lines) + "\n")


def make_inputs_manifest() -> dict:
    entries = []
    for path in sorted((RUN_DIR / "inputs").rglob("*")):
        if path.is_file():
            entries.append(manifest_entry(
                path, file_role(path), f"S6-C 已消费输入快照：{path.relative_to(RUN_DIR).as_posix()}"
            ))
    for relative in CURRENT_SOURCES:
        entries.append(manifest_entry(ROOT / relative, "source", f"当前工作树来源文件：{relative}"))
    return {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-C",
        "run_id": RUN_ID,
        "source_commit": EXPECTED_HEAD,
        "evidence_dir": project_rel(RUN_DIR),
        "interfaces": [],
        "interfaces_not_applicable_reason": "本包封装 S6-C 离线矩阵证据；行为规格、批准回执及阶段接口均按输入快照绑定，不在本清单内新增接口冻结声明。",
        "hash_basis": "worktree_disk",
        "hash_basis_commit": EXPECTED_HEAD,
        "files": sorted(entries, key=lambda row: row["path"]),
        "checks": [{
            "name": "r04固定输入与批准快照复制核对",
            "status": "PASS",
            "command": "build_s6c_bundle.py --stage prepare：逐文件复算输入复制前后 SHA-256",
            "exit_code": 0,
        }],
        "limitations": [
            "历史 r08 数据、r04 测试输出均以原始字节副本绑定；本次不重跑历史或回归测试。",
            "所有清单哈希项声明 hash_basis=worktree_disk，source_commit 固定为当前 HEAD。",
        ],
    }


def initial_checks() -> list[dict]:
    r04_record = read_json(RUN_DIR / "inputs/r04_preflight/execution_record.json")
    by_name = {row["name"]: row for row in r04_record["commands"]}
    def prior(name: str, title: str) -> dict:
        row = by_name[name]
        return {"name": title, "status": "PASS", "command": row["command"], "exit_code": row["exit_code"]}
    return [
        {"name": "S6-B r08历史离线矩阵26条", "status": "PASS",
         "command": "隔离历史包 CHECKS_OK + strict hash_basis OK；详情见 source_binding.json。", "exit_code": 0},
        prior("S6-B regression unittest", "r04 S6-B回归40项（固定历史输出）"),
        prior("S6-C receipt boundary unittest", "r04 S6-C receipt boundary 17项（固定历史输出）"),
        prior("C11 duplicate ACK replay", "r04 C11 duplicate ACK回放（固定历史输出）"),
        {"name": "S6-C正式11行矩阵整体", "status": "BLOCKED", "command": "见 matrix_coverage.json", "exit_code": None,
         "reason": "第8行存在未决规格项；其余10行完成逐项证据绑定。"},
        {"name": "正式第8行 B25 与 frame_id wrap", "status": "BLOCKED", "command": "见 matrix_coverage.json.formal_11_rows[7]", "exit_code": None,
         "reason": "大回退数值阈值未批准，0xFFFFFFFE 文档与机器 JSON 语义未统一。"},
        {"name": "独立审查 G2", "status": "NOT_RUN", "command": "", "exit_code": None,
         "reason": "等待总控安排独立只读审查。"},
        {"name": "T6-A03 实测帧周期 P", "status": "NOT_RUN", "command": "", "exit_code": None,
         "reason": "缺阶段4实测帧周期 P；本包不推算或替代实测。"},
        {"name": "6-E 摄像头/板卡实物验收", "status": "NOT_RUN", "command": "", "exit_code": None,
         "reason": "未执行任何硬件操作。"},
        {"name": "阶段4/5真实集成", "status": "BLOCKED", "command": "", "exit_code": None,
         "reason": "本包仅使用已绑定离线结果；没有阶段4/5实时集成证据。"},
        {"name": "G4/G5 阶段验收", "status": "NOT_RUN", "command": "", "exit_code": None,
         "reason": "矩阵仍 BLOCKED，且独立审查、板级/集成验收未完成。"},
    ]


def run_capture(command: list[str]) -> dict:
    environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        command, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
        errors="replace", env=environment, check=False,
    )
    return {
        "command": subprocess.list2cmdline(command),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def store_check_result(key: str, result: dict, output_path: Path, record: dict,
                       checks: list[dict], check_name: str) -> None:
    write_text(output_path, str(result["stdout"]) + str(result["stderr"]))
    row = next(item for item in checks if item["name"] == check_name)
    row["command"] = str(result["command"])
    row["exit_code"] = int(result["exit_code"])
    row["status"] = "PASS" if int(result["exit_code"]) == 0 else "FAIL"
    if int(result["exit_code"]) != 0:
        row["reason"] = f"{key} 返回非零；完整 stdout/stderr 已保存在 {project_rel(output_path)}。"
    record.setdefault("package_checks", {})[key] = {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "output_path": project_rel(output_path),
        "output_sha256": sha256_file(output_path),
    }
    write_json(EXECUTION_RECORD, record)


def refresh_delivery(delivery: dict) -> None:
    write_hashes_file()
    delivery["files"] = all_delivery_files()
    write_json(DELIVERY_MANIFEST, delivery)


def checks_stage(record: dict) -> None:
    require_baseline()
    if not MATRIX_PATH.is_file() or not SOURCE_BINDING.is_file():
        raise RuntimeError("prepare 阶段产物缺失")
    if INPUTS_MANIFEST.exists() or DELIVERY_MANIFEST.exists():
        raise RuntimeError("本 RunId 已存在清单；拒绝覆盖")
    outputs = RUN_DIR / "outputs"
    outputs.mkdir(exist_ok=False)
    inputs_checker = MAIN_VERIFICATION / "check_stage_delivery.py"
    basis_checker = MAIN_VERIFICATION / "check_manifest_hash_basis.py"
    snapshot_stage = RUN_DIR / "inputs/r04_preflight/inputs/tool_snapshots/check_stage_delivery.py"
    snapshot_basis = RUN_DIR / "inputs/r04_preflight/inputs/tool_snapshots/check_manifest_hash_basis.py"
    if sha256_file(inputs_checker) != sha256_file(snapshot_stage):
        raise RuntimeError("主 check_stage_delivery.py 与 r04 固定快照哈希不一致")
    if sha256_file(basis_checker) != sha256_file(snapshot_basis):
        raise RuntimeError("主 check_manifest_hash_basis.py 与 r04 固定快照哈希不一致")

    inputs_manifest = make_inputs_manifest()
    write_json(INPUTS_MANIFEST, inputs_manifest)
    checks = initial_checks()
    delivery = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-C",
        "run_id": RUN_ID,
        "source_commit": EXPECTED_HEAD,
        "evidence_dir": project_rel(RUN_DIR),
        "interfaces": [],
        "interfaces_not_applicable_reason": inputs_manifest["interfaces_not_applicable_reason"],
        "hash_basis": "worktree_disk",
        "hash_basis_commit": EXPECTED_HEAD,
        "hash_basis_note": "每项按磁盘原始字节 SHA-256；当前工作树差异与 source_commit 分别绑定。",
        "files": [],
        "checks": checks,
        "tool_versions": {
            "python": sys.version.split()[0],
            "git": git_text("--version"),
            "main_check_stage_delivery_sha256": sha256_file(inputs_checker),
            "main_check_manifest_hash_basis_sha256": sha256_file(basis_checker),
        },
        "limitations": [
            "矩阵整体与第8行保持 BLOCKED；校验器 CHECKS_OK 只表示封包结构、文件哈希和清单字段可复核。",
            "没有板级操作、实时性能结果或阶段4/5真实结果集成；T6-A03 与 6-E 未执行。",
            "独立审查尚未进行；本封包不构成 G2/G3/G4/G5 通过。",
        ],
    }
    input_command = [str(PYTHON), "-B", str(inputs_checker), "--mode", "inputs",
                     "--manifest", str(INPUTS_MANIFEST), "--project-root", str(ROOT)]
    evidence_command = [str(PYTHON), "-B", str(inputs_checker), "--mode", "evidence",
                        "--manifest", str(DELIVERY_MANIFEST), "--project-root", str(ROOT)]
    basis_command = [str(PYTHON), "-B", str(basis_checker), "--repo", str(ROOT),
                     "--paths", project_rel(INPUTS_MANIFEST), "--paths", project_rel(DELIVERY_MANIFEST),
                     "--mode", "strict", "--json"]

    input_output = outputs / "check_inputs_mode_output.txt"
    input_result = run_capture(input_command)
    store_check_result("inputs", input_result, input_output, record, checks,
                       "main check_stage_delivery inputs")
    inputs_manifest["checks"].append({
        "name": "main check_stage_delivery inputs",
        "status": "PASS" if input_result["exit_code"] == 0 else "FAIL",
        "command": input_result["command"],
        "exit_code": input_result["exit_code"],
    })
    write_json(INPUTS_MANIFEST, inputs_manifest)
    if input_result["exit_code"] != 0:
        raise RuntimeError("inputs checker 非零，保留失败输出并停止")

    checks.extend([
        {"name": "main check_stage_delivery inputs", "status": "PASS",
         "command": input_result["command"], "exit_code": input_result["exit_code"]},
        {"name": "main check_stage_delivery evidence", "status": "NOT_RUN", "command": "", "exit_code": None},
        {"name": "main check_manifest_hash_basis strict", "status": "NOT_RUN", "command": "", "exit_code": None},
        {"name": "main check_stage_delivery evidence closing", "status": "NOT_RUN", "command": "", "exit_code": None},
    ])
    record["status"] = "CHECKING_FIXED_POINT"
    record["packaging_invocations"].append({
        "stage": "checks", "command": subprocess.list2cmdline([str(PYTHON), "-B", str(SCRIPT), "--stage", "checks"]),
        "exit_code": None,
    })
    write_json(EXECUTION_RECORD, record)

    evidence_output = outputs / "check_evidence_mode_output.txt"
    basis_output = outputs / "check_hash_basis_output.txt"
    closing_output = outputs / "check_closing_evidence_mode_output.txt"
    for path in (evidence_output, basis_output, closing_output):
        write_text(path, "")

    previous_state = None
    final_results = {}
    for _ in range(8):
        refresh_delivery(delivery)
        evidence = run_capture(evidence_command)
        store_check_result("evidence", evidence, evidence_output, record, checks,
                           "main check_stage_delivery evidence")
        refresh_delivery(delivery)
        basis = run_capture(basis_command)
        store_check_result("hash_basis", basis, basis_output, record, checks,
                           "main check_manifest_hash_basis strict")
        refresh_delivery(delivery)
        closing = run_capture(evidence_command)
        store_check_result("evidence_closing", closing, closing_output, record, checks,
                           "main check_stage_delivery evidence closing")
        refresh_delivery(delivery)
        final_results = {"evidence": evidence, "hash_basis": basis, "closing": closing}
        current_state = (
            tuple((item["path"], item["sha256"]) for item in delivery["files"]),
            tuple((item["name"], item["status"], item.get("exit_code")) for item in checks),
            sha256_file(evidence_output), sha256_file(basis_output), sha256_file(closing_output),
            sha256_file(RUN_DIR / "hashes_sha256.txt"),
        )
        if all(result["exit_code"] == 0 for result in final_results.values()) and current_state == previous_state:
            break
        previous_state = current_state
    else:
        raise RuntimeError("r08 固定点模板 8 轮内未收敛；保留当前失败轨迹，不重用 RunId")

    refresh_delivery(delivery)
    final_inputs = run_capture(input_command)
    final_evidence = run_capture(evidence_command)
    final_basis = run_capture(basis_command)
    if (final_inputs["exit_code"] != 0 or final_evidence["exit_code"] != 0 or final_basis["exit_code"] != 0
            or final_inputs["stdout"] + final_inputs["stderr"] != input_output.read_text(encoding="utf-8")
            or final_evidence["stdout"] + final_evidence["stderr"] != evidence_output.read_text(encoding="utf-8")
            or final_evidence["stdout"] + final_evidence["stderr"] != closing_output.read_text(encoding="utf-8")
            or final_basis["stdout"] + final_basis["stderr"] != basis_output.read_text(encoding="utf-8")):
        raise RuntimeError("最终清单复核失败或校验器输出与已封存日志不一致")
    invocation = record["packaging_invocations"][-1]
    invocation["exit_code"] = 0
    record["package_status"] = "EVIDENCE_CHECKS_OK_MATRIX_BLOCKED_REVIEW_PENDING"
    record["status"] = "PACKAGED_BLOCKED_REVIEW_PENDING"
    write_json(EXECUTION_RECORD, record)
    refresh_delivery(delivery)

    # 最终文件列表更新后再只读验证一次，输出必须与封存日志逐字节一致。
    final_evidence = run_capture(evidence_command)
    final_basis = run_capture(basis_command)
    if (final_evidence["exit_code"] != 0 or final_basis["exit_code"] != 0
            or final_evidence["stdout"] + final_evidence["stderr"] != evidence_output.read_text(encoding="utf-8")
            or final_basis["stdout"] + final_basis["stderr"] != basis_output.read_text(encoding="utf-8")):
        raise RuntimeError("封存 execution_record 后的 closing 复核未与固定日志一致")

    print(json.dumps({
        "status": "CHECKS_OK_MATRIX_BLOCKED_REVIEW_PENDING",
        "run_id": RUN_ID,
        "historical_cases": 26,
        "supplemental_cases": 1,
        "formal_rows_pass": 10,
        "formal_rows_blocked": [8],
        "checks": {"inputs": 0, "evidence": 0, "hash_basis_strict": 0, "closing": 0},
    }, ensure_ascii=True))


def prepare_stage(record: dict) -> None:
    require_baseline()
    if (RUN_DIR / "inputs").exists() or (RUN_DIR / "outputs").exists() or MATRIX_PATH.exists():
        raise RuntimeError("prepare 只允许在全新 RunId 执行，拒绝覆盖已有证据")
    if not R04.is_dir() or not R02_MATRIX.is_file() or not RUNBOOK_SOURCE.is_file():
        raise RuntimeError("固定输入路径缺失")
    if sha256_file(RUNBOOK_SOURCE) != RUNBOOK_SHA256:
        raise RuntimeError("正式 6-C runbook SHA-256 与已核验值不符")
    if sha256_file(RECEIPT_SOURCE) != RECEIPT_SHA256:
        raise RuntimeError("正式 U6-02 r07 receipt SHA-256 与已核验值不符")
    r04_record = read_json(R04 / "execution_record.json")
    if (r04_record.get("source_commit") != EXPECTED_HEAD
            or r04_record.get("preflight", {}).get("current_test_sha256") != R04_CURRENT_TEST_SHA256
            or r04_record.get("preflight", {}).get("current_core_sha256") != R08_CORE_SHA256):
        raise RuntimeError("r04 固定输入基线与本次绑定条件不一致")

    inputs_root = RUN_DIR / "inputs"
    inputs_root.mkdir()
    copy_tree_exact(R04 / "inputs", inputs_root / "r04_preflight/inputs")
    copy_tree_exact(R04 / "outputs", inputs_root / "r04_preflight/outputs")
    copy_file_exact(R04 / "execution_record.json", inputs_root / "r04_preflight/execution_record.json")
    copy_file_exact(R04 / "source_diff.patch", inputs_root / "r04_preflight/source_diff.patch")
    copy_file_exact(R02_MATRIX, inputs_root / "prior_r02_matrix_coverage.json")
    copy_file_exact(RUNBOOK_SOURCE, inputs_root / "formal_6c_runbook.md")
    copy_file_exact(RECEIPT_SOURCE, inputs_root / "U6-02_r07_decision_receipt.json")

    command_bindings = []
    for command in r04_record["commands"]:
        source_path = ROOT / PurePosixPath(command["output_path"])
        if not source_path.is_file() or sha256_file(source_path) != command["output_sha256"]:
            raise RuntimeError(f"r04 命令输出当前字节与 execution_record 不符：{command['name']}")
        copied_path = inputs_root / "r04_preflight/outputs" / PurePosixPath(command["output_path"]).relative_to(
            PurePosixPath("report/evidence/S6-C") / "s6c_deterministic_matrix_20261029_r04" / "outputs"
        )
        if not copied_path.is_file() or sha256_file(copied_path) != command["output_sha256"]:
            raise RuntimeError(f"r04 命令输出副本哈希不符：{command['name']}")
        command_bindings.append({
            "name": command["name"], "command": command["command"], "cwd": command["cwd"],
            "exit_code": command["exit_code"], "source_output_path": command["output_path"],
            "source_output_sha256": command["output_sha256"],
            "copied_output_path": project_rel(copied_path),
            "copied_output_sha256": sha256_file(copied_path),
        })
    record["bound_r04_commands"] = command_bindings
    record["r04_run_id"] = r04_record["run_id"]
    record["r04_test_counts"] = r04_record["test_counts"]
    record["r04_c11_result"] = r04_record["C11_result"]
    record["packaging_invocations"][-1]["exit_code"] = 0
    create_matrix_and_bindings(record)
    record["status"] = "PREPARED_BLOCKED_CHECKS_PENDING"
    record["prepared_at_utc8"] = now_utc8()
    write_json(EXECUTION_RECORD, record)
    print(json.dumps({
        "status": "PREPARED_BLOCKED_CHECKS_PENDING",
        "run_id": RUN_ID,
        "historical_cases": 26,
        "supplemental_cases": 1,
        "formal_rows_pass": 10,
        "formal_rows_blocked": [8],
        "r04_tests_rerun": False,
    }, ensure_ascii=True))


def new_record(stage: str) -> dict:
    return {
        "schema_version": 1,
        "task_id": "S6-C",
        "run_id": RUN_ID,
        "source_commit": EXPECTED_HEAD,
        "branch": EXPECTED_BRANCH,
        "started_at_utc8": now_utc8(),
        "builder_script_sha256": sha256_file(SCRIPT),
        "hardware_access": "NOT_USED",
        "test_execution_policy": "r04 真实命令输出为只读固定输入；本 RunId 不复跑单元/集成测试。",
        "packaging_invocations": [{
            "stage": stage,
            "command": subprocess.list2cmdline([str(PYTHON), "-B", str(SCRIPT), "--stage", stage]),
            "exit_code": None,
        }],
        "status": "RUNNING",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="组装 S6-C 离线证据包，不重跑测试")
    parser.add_argument("--stage", choices=("prepare", "checks"), required=True)
    args = parser.parse_args()
    try:
        require_baseline()
        if args.stage == "prepare":
            if EXECUTION_RECORD.exists():
                raise RuntimeError("本 RunId 已开始执行，拒绝重用 prepare")
            record = new_record(args.stage)
            write_json(EXECUTION_RECORD, record)
            prepare_stage(record)
        else:
            if not EXECUTION_RECORD.is_file():
                raise RuntimeError("checks 需依赖成功的 prepare 阶段")
            record = read_json(EXECUTION_RECORD)
            if record.get("status") != "PREPARED_BLOCKED_CHECKS_PENDING":
                raise RuntimeError("prepare 状态不允许进入 checks，且本 RunId 不可重跑")
            checks_stage(record)
        return 0
    except Exception:
        error_text = traceback.format_exc()
        error_log = RUN_DIR / "outputs" / f"package_{args.stage}_error.txt"
        try:
            write_text(error_log, error_text)
            if EXECUTION_RECORD.is_file():
                record = read_json(EXECUTION_RECORD)
                record["status"] = f"FAILED_{args.stage.upper()}"
                record["failure_log"] = project_rel(error_log)
                record["failure_sha256"] = sha256_file(error_log)
                record["failed_at_utc8"] = now_utc8()
                if record.get("packaging_invocations"):
                    record["packaging_invocations"][-1]["exit_code"] = 1
                write_json(EXECUTION_RECORD, record)
        except Exception:
            pass
        sys.stderr.write(error_text)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
