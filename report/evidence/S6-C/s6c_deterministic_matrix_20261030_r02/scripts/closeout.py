#!/usr/bin/env python3
"""构建 S6-C 离线确定性矩阵及可复核证据。"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


UTC8 = timezone(timedelta(hours=8))
RUN_ID = "s6c_deterministic_matrix_20261030_r02"
RUN_DIR = Path(__file__).resolve().parents[1]
ROOT = RUN_DIR.parents[3]
HEAD = "e13c5532abde97771c9e8ce3776e837f0c6816df"
BRANCH = "stage6-interact-prep"
PYTHON = Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
MAIN_CHECKERS = Path(r"D:\FPGA_Competition\verification")
INPUTS = RUN_DIR / "inputs"
OUTPUTS = RUN_DIR / "outputs"
SCRIPT = RUN_DIR / "scripts/closeout.py"
RECORD = RUN_DIR / "execution_record.json"
INPUTS_MANIFEST = RUN_DIR / "inputs_manifest.json"
DELIVERY = RUN_DIR / "delivery_manifest.json"
MATRIX = RUN_DIR / "matrix_coverage.json"

SOURCES = {
    "core.py": "src/stage6/s6_core.py",
    "actions.py": "src/stage6/s6_actions.py",
    "params.py": "src/stage6/s6_params.py",
    "receipts.py": "src/stage6/s6_receipts.py",
    "case_runner.py": "verification/s6b_run_cases.py",
    "s6b_tests.py": "verification/test_s6b_core_regressions.py",
    "s6c_tests.py": "verification/test_s6c_receipt_boundary.py",
    "behavior.md": "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "behavior.json": "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "interface.json": "docs/stage6/s6b_frozen_interface_v1.json",
}
INPUT_FILES = {
    "case_matrix.json": "report/evidence/S6-B/s6b_current_20261029_r08/matrix_source_r03/cases/case_matrix.json",
    "r08_manifest.json": "report/evidence/S6-B/s6b_current_20261029_r08/delivery_manifest.json",
    "r08_run_report.json": "report/evidence/S6-B/s6b_current_20261029_r08/matrix_source_r03/run_report.json",
    "c11_case.json": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r04/inputs/C11_duplicate_ack_case.json",
    "u6_02_r07.json": "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json",
    "wrap_receipt.json": "report/evidence/S6-A/s6a_b25_decision_20261030_r01/decision_receipt.json",
    "s4_contract.json": "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json",
    "runbook.md": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r06/inputs/formal_6c_runbook.md",
    "r02_coverage.json": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r02/matrix_coverage.json",
    "r06_behavior.json": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r06/inputs/r04_preflight/inputs/source_snapshots/docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "r02_freeze.json": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r02/outputs/duplicate_ack_matrix/expected_freeze.json",
    "r02_c11_report.json": "report/evidence/S6-C/s6c_deterministic_matrix_20261029_r02/outputs/duplicate_ack_matrix/run_report.json",
}


def utc8() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(value)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-C", str(ROOT), *args],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} 退出 {result.returncode}: {result.stderr.decode('utf-8','replace')}")
    return result.stdout.decode("utf-8", "replace").strip()


def baseline() -> None:
    if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT.resolve():
        raise RuntimeError("工作树根目录不符")
    if git("rev-parse", "HEAD") != HEAD or git("branch", "--show-current") != BRANCH:
        raise RuntimeError("HEAD 或分支已变化")
    lock = (ROOT / git("rev-parse", "--git-path", "index.lock")).resolve()
    if lock.exists():
        raise RuntimeError(f"index.lock 存在：{lock}")


def copy_file(source: Path, destination: Path) -> str:
    if not source.is_file() or source.is_symlink():
        raise RuntimeError(f"快照来源不是普通文件：{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    destination.write_bytes(data)
    digest = sha(data)
    if file_sha(destination) != digest:
        raise RuntimeError(f"快照校验不一致：{source}")
    return digest


def prepare() -> None:
    baseline()
    if RUN_DIR.name != RUN_ID or SCRIPT.resolve() != Path(__file__).resolve():
        raise RuntimeError("RunId 或脚本路径不匹配")
    if RECORD.exists() or INPUTS.exists() or OUTPUTS.exists() or DELIVERY.exists() or INPUTS_MANIFEST.exists():
        raise RuntimeError("此 RunId 已用或非空；拒绝覆盖")
    INPUTS.mkdir()
    bindings = []
    for alias, relative in SOURCES.items():
        origin = ROOT / relative
        snapshot_rel = f"inputs/src/{alias}"
        snapshot = RUN_DIR / snapshot_rel
        disk_sha = copy_file(origin, snapshot)
        blob = subprocess.run(
            ["git", "-c", "core.longpaths=true", "-C", str(ROOT), "cat-file", "blob", f"{HEAD}:{relative}"],
            capture_output=True, check=False,
        )
        blob_sha = sha(blob.stdout) if blob.returncode == 0 else None
        bindings.append({"alias": alias, "origin_path": relative, "snapshot_path": snapshot_rel,
                         "worktree_disk_sha256": disk_sha, "commit_blob_sha256": blob_sha,
                         "matches_commit_blob": blob_sha == disk_sha if blob_sha else False,
                         "hash_basis": "worktree_disk"})
    for alias, relative in INPUT_FILES.items():
        origin = ROOT / relative
        snapshot_rel = f"inputs/ref/{alias}"
        bindings.append({"alias": alias, "origin_path": relative, "snapshot_path": snapshot_rel,
                         "worktree_disk_sha256": copy_file(origin, RUN_DIR / snapshot_rel),
                         "hash_basis": "worktree_disk"})
    for name in ("check_stage_delivery.py", "check_manifest_hash_basis.py"):
        origin = MAIN_CHECKERS / name
        snapshot_rel = f"inputs/checkers/{name}"
        bindings.append({"alias": name, "origin_path": str(origin), "snapshot_path": snapshot_rel,
                         "worktree_disk_sha256": copy_file(origin, RUN_DIR / snapshot_rel),
                         "hash_basis": "worktree_disk"})
    write_json(RUN_DIR / "source_bindings.json", {
        "schema_version": 1, "artifact": "s6c_source_and_input_bindings", "task_id": "S6-C",
        "run_id": RUN_ID, "source_commit": HEAD, "branch": BRANCH,
        "hash_basis": "worktree_disk", "files": bindings,
    })

    source_matrix = read_json(RUN_DIR / "inputs/ref/case_matrix.json")
    if len(source_matrix.get("cases", [])) != 26:
        raise RuntimeError("r08 固定矩阵不是 26 case")
    r08_manifest = read_json(RUN_DIR / "inputs/ref/r08_manifest.json")
    matrix_entry = next((row for row in r08_manifest.get("files", [])
                         if row.get("path", "").endswith("matrix_source_r03/cases/case_matrix.json")), None)
    if matrix_entry is None or matrix_entry.get("sha256") != file_sha(RUN_DIR / "inputs/ref/case_matrix.json"):
        raise RuntimeError("r08 固定矩阵与原 delivery_manifest 不匹配")
    prior_report = read_json(RUN_DIR / "inputs/ref/r08_run_report.json")
    if prior_report.get("status") != "PASS" or prior_report.get("case_count") != 26:
        raise RuntimeError("r08 原始运行报告不符合 26-case PASS 来源条件")

    contract = read_json(RUN_DIR / "inputs/ref/s4_contract.json")
    fields = {row.get("name"): row for row in contract.get("input_frame_contract", {}).get("fields", [])}
    f = fields.get("frame_id", {})
    s = fields.get("session_id", {})
    if (contract.get("contract_version") != "1.3.0" or contract.get("revision") != "r07"
            or contract.get("status") != "FROZEN_OFFLINE_ONLY"
            or f.get("type") != "uint32" or f.get("required") is not True
            or "+1" not in f.get("semantics", "") or "重新分配" not in s.get("semantics", "")):
        raise RuntimeError("阶段4 r07 冻结字段契约不满足 S6-C 序号边界前提")
    if file_sha(RUN_DIR / "inputs/ref/s4_contract.json") != "7228f51350feb0c63de9e58de20d72d1fdfcd3bf13c39374344e82b027a0f145":
        raise RuntimeError("阶段4 r07 契约磁盘哈希不匹配")

    current_behavior = read_json(RUN_DIR / "inputs/src/behavior.json")
    l02 = next(row for row in current_behavior["parameters"] if row.get("id") == "T6-L02")
    if l02.get("approval_status") != "APPROVED_20261023" or l02.get("draft_value") != 300 or l02.get("unit") != "ms":
        raise RuntimeError("T6-L02 未按 2026-10-23 批准值冻结")
    l02_ns = int(l02["draft_value"]) * 1_000_000

    write_json(INPUTS / "controller_resolution.json", {
        "schema_version": 1, "artifact": "s6c_frame_sequence_boundary_resolution",
        "resolved_date_utc8": "2026-10-30",
        "user_direct_approval_scope": "Wong 批准同一 session_id 下回绕 frame_id 一律按 B23 拒绝。",
        "delegated_decision_scope": "Wong 授权阶段6总控决定未决的 0xFFFFFFFE 阈值语义；具体内容为总控裁定，不归述为 Wong 直接给定。",
        "controller_decision": {
            "0xFFFFFFFE": "无特殊停发/换 session_id 阈值；同会话可合法递增至 0xFFFFFFFF。",
            "wrap": "FE→0、FFFFFFFF→0 及任何较小值同会话均 B23 拒绝；不更新高水位、窗口和目标证据，单调期限照常评估。",
            "new_session": "需要从 0 重新计数时使用新 session_id；新会话从 0 接受。",
        },
        "scope": "只适用于 S6-B/S6-C 离线序号边界，服从阶段4 s4-shared-io/1.3.0 r07。",
        "user_receipt": "report/evidence/S6-A/s6a_b25_decision_20261030_r01/decision_receipt.json",
    })
    cases = [
        {"case_id": "FE-first", "session_id": "seq-old", "frame_id": 0xFFFFFFFE, "t_input_ns": 0},
        {"case_id": "FE-to-zero", "session_id": "seq-old", "frame_id": 0, "t_input_ns": 1},
        {"case_id": "FE-to-FF", "session_id": "seq-old", "frame_id": 0xFFFFFFFF, "t_input_ns": 2},
        {"case_id": "FF-to-zero-at-L02", "session_id": "seq-old", "frame_id": 0, "t_input_ns": l02_ns + 2},
        {"case_id": "new-session-reset-zero", "session_id": "seq-new", "frame_id": 0, "t_input_ns": l02_ns + 3},
        {"case_id": "new-session-zero-accepted", "session_id": "seq-new", "frame_id": 0, "t_input_ns": l02_ns + 4},
    ]
    expected = [
        {"input_state": "OK", "transition": "M1", "to_state": "CANDIDATE", "state": "CANDIDATE", "last_frame_id": 0xFFFFFFFE, "window_match_count": 1, "t_last_target_continues_ns": 0, "out_of_order_frames": 0, "action_request": False},
        {"input_state": "OUT_OF_ORDER", "transition": None, "state": "CANDIDATE", "last_frame_id": 0xFFFFFFFE, "window_match_count": 1, "t_last_target_continues_ns": 0, "out_of_order_frames": 1, "action_request": False},
        {"input_state": "OK", "state": "CANDIDATE", "last_frame_id": 0xFFFFFFFF, "window_match_count": 2, "t_last_target_continues_ns": 2, "out_of_order_frames": 1, "action_request": False},
        {"input_state": "OUT_OF_ORDER", "transition": "M10", "to_state": "LOST", "state": "LOST", "last_frame_id": 0xFFFFFFFF, "window_match_count": 2, "t_last_target_continues_ns": 2, "out_of_order_frames": 2, "action_request": False},
        {"transition": "RESET", "to_state": "IDLE", "state": "IDLE", "last_frame_id": None, "window_match_count": 0, "t_last_target_continues_ns": None, "out_of_order_frames": 0, "action_request": False},
        {"input_state": "OK", "transition": "M1", "to_state": "CANDIDATE", "state": "CANDIDATE", "last_frame_id": 0, "window_match_count": 1, "t_last_target_continues_ns": l02_ns + 4, "out_of_order_frames": 0, "action_request": False},
    ]
    write_json(INPUTS / "sequence_boundary_fixture.json", {
        "schema_version": 1, "artifact": "s6c_sequence_boundary_independent_expected",
        "expected_authorship": "总控依据规格与阶段4冻结契约手写；不由状态机输出生成。",
        "l02_ns_from_approved_parameter": l02_ns, "cases": cases,
        "expected_steps": expected,
        "invariants": ["FE→0 同会话拒绝，不更新高水位/窗口/目标连续锚点且无动作。",
                       "FE→FFFFFFFF 同会话合法递增。",
                       "FFFFFFFF→0 同会话拒绝，在 L02 边界仍触发 M10；高水位/窗口/锚点不被拒绝帧推进且无动作。",
                       "session_id 改变复位；后续新会话 frame_id=0 接受。",
                       "精确虚拟时间：0、1、2、300000002、300000003、300000004 ns。"],
    })

    prior = RUN_DIR / "inputs/ref/r06_behavior.json"
    old_raw = file_sha(prior)
    old_norm = sha(prior.read_bytes().replace(b"\r\n", b"\n"))
    old_freeze = read_json(RUN_DIR / "inputs/ref/r02_freeze.json")
    old_c11 = read_json(RUN_DIR / "inputs/ref/r02_c11_report.json")
    if (old_raw != "dc1808332575f31953d3b83ac19a02bc4d610bc3a65fcc7d8b5ffce70825fba7"
            or old_norm != "f44bd3eb17d1f6785cd632e3e01700ba5469950a8e03cd45589b9a366a25f9c9"
            or old_freeze.get("behavior_json_sha256") != old_norm
            or old_c11.get("behavior_json_sha256") != old_norm):
        raise RuntimeError("旧 r02/r06 行为 JSON 原始/归一哈希关系不符")
    write_json(RUN_DIR / "hash_reconciliation.json", {
        "schema_version": 1, "artifact": "s6c_behavior_json_hash_reconciliation",
        "historical_snapshot": "inputs/ref/r06_behavior.json",
        "raw_sha256_worktree_disk": old_raw,
        "normalization": "CRLF 字节替换为 LF 后计算 SHA-256；不解码且不修改其他字节。",
        "lf_normalized_sha256": old_norm,
        "r02_expected_freeze_behavior_sha256": old_freeze["behavior_json_sha256"],
        "r02_C11_report_behavior_sha256": old_c11["behavior_json_sha256"],
        "resolution": "dc180... 是原始 CRLF 磁盘字节基座，f44... 是 ParamPack 使用的 CRLF→LF 归一基座；两者一致地绑定同一历史内容。",
        "current_spec_raw_sha256": file_sha(INPUTS / "src/behavior.json"),
        "current_spec_lf_normalized_sha256": sha((INPUTS / "src/behavior.json").read_bytes().replace(b"\r\n", b"\n")),
    })
    write_json(RUN_DIR / "source_bindings.json", read_json(RUN_DIR / "source_bindings.json"))
    write_json(RECORD, {
        "schema_version": 1, "artifact": "s6c_execution_record", "task_id": "S6-C",
        "run_id": RUN_ID, "source_commit": HEAD, "branch": BRANCH,
        "prepared_at_utc8": utc8(), "status": "PREPARED_RUN_PENDING",
        "hardware_access": "NOT_USED", "commands": [],
        "matrix_source_run_id": "s6b_current_20261029_r08",
        "matrix_source_commit": "e735a5afb5b474793408ec1e61da111006c70e60",
        "matrix_source_case_count": 26,
        "expected_provenance": "旧 26-case expected 先独立冻结再运行；新增边界 expected 由总控依据规格/契约手写。",
    })


def capture(name: str, command: list[str], output_rel: str) -> dict:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                            encoding="utf-8", errors="replace", env=env, check=False)
    output = result.stdout + result.stderr
    output_path = RUN_DIR / output_rel
    write_text(output_path, output)
    return {"name": name, "command": subprocess.list2cmdline(command), "cwd": str(ROOT),
            "exit_code": result.returncode, "output_path": output_rel,
            "output_sha256": file_sha(output_path), "stdout": result.stdout,
            "stderr": result.stderr}


def run_boundary_probe() -> dict:
    from src.stage6.s6_core import EV_FRAME_RESULT, GestureInteractionCore
    from src.stage6.s6_params import ParamPack

    fixture = read_json(INPUTS / "sequence_boundary_fixture.json")
    core = GestureInteractionCore(ParamPack(ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                                            project_root=ROOT))
    steps = []
    mismatches = []
    for case, expected in zip(fixture["cases"], fixture["expected_steps"]):
        event = {
            "kind": EV_FRAME_RESULT, "session_id": case["session_id"],
            "frame_id": case["frame_id"], "state": "OK",
            "t_input_ns": case["t_input_ns"],
            "detections": [{"class_id": 0, "score": 0.9,
                            "xyxy": [0.2, 0.2, 0.6, 0.6], "source_order": 0}],
        }
        result = core.step(event)
        log = result["log"]
        actual = {
            "input_state": log.get("input_state"),
            "transition": log.get("transition"),
            "to_state": log.get("to_state"),
            "state": core.state,
            "last_frame_id": core.last_frame_id,
            "window_match_count": core.window_match_count,
            "t_last_target_continues_ns": core.t_last_target_continues_ns,
            "out_of_order_frames": core.counters.get("out_of_order_frames", 0),
            "action_request": result["action_request"] is not None,
        }
        for key, wanted in expected.items():
            if actual.get(key) != wanted:
                mismatches.append({"case_id": case["case_id"], "field": key,
                                   "expected": wanted, "actual": actual.get(key)})
        steps.append({"case_id": case["case_id"], "input": case,
                      "actual_log": log, "post_state": actual})
    doc = {
        "schema_version": 1, "artifact": "s6c_sequence_boundary_probe_result",
        "run_id": RUN_ID, "source_commit": HEAD,
        "expected_path": "inputs/sequence_boundary_fixture.json",
        "expected_sha256": file_sha(INPUTS / "sequence_boundary_fixture.json"),
        "status": "PASS" if not mismatches else "FAIL",
        "steps": steps, "mismatches": mismatches,
        "scope": "固定输入与虚拟单调时钟下的软件行为，不含板测或实时结论。",
    }
    write_json(OUTPUTS / "sequence_boundary_probe.json", doc)
    return doc


def times_for(events: list[dict], start_ns: int = 0) -> list[dict]:
    current = start_ns
    rows = []
    for event in events:
        if "dt_ns" in event:
            if type(event["dt_ns"]) is not int or event["dt_ns"] < 0:
                raise RuntimeError("case 含无效 dt_ns")
            current += event["dt_ns"]
        elif "t_ns" in event:
            current = event["t_ns"]
        if event.get("frame_id") is not None:
            rows.append({"frame_id": event["frame_id"], "kind": event["kind"],
                         "t_input_ns": current})
    return rows


def detail(case: dict, run_case: dict, log_path: Path, display_path: str) -> dict:
    if run_case.get("status") != "PASS" or run_case.get("assertions_failed"):
        raise RuntimeError(f"case 未 PASS：{case['case_id']}")
    if run_case.get("expected") != case.get("expected"):
        raise RuntimeError(f"冻结输入 expected 不一致：{case['case_id']}")
    expected_times = times_for(case["events"], case.get("t_start_ns", 0))
    logs = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    actual_rows = [row for row in logs if row.get("kind") == "step" and row.get("frame_id") is not None]
    actual_times = [{"frame_id": row.get("frame_id"), "kind": row.get("event_kind"),
                     "t_input_ns": row.get("t_input_ns"), "input_state": row.get("input_state"),
                     "transition": row.get("transition"), "from_state": row.get("from_state"),
                     "to_state": row.get("to_state"), "event_index": row.get("event_index"),
                     "reason": row.get("reason")} for row in actual_rows]
    if [(r["frame_id"], r["t_input_ns"]) for r in expected_times] != [
            (r["frame_id"], r["t_input_ns"]) for r in actual_times]:
        raise RuntimeError(f"输入 frame/time 与逐行日志不一致：{case['case_id']}")
    for want, got in zip(expected_times, actual_times):
        if want["kind"] != got["kind"] and not (
                want["kind"] == "E_FRAME_RESULT" and got["kind"] == "E_FRAME_DUPLICATE"
                and got["input_state"] == "DUPLICATE"):
            raise RuntimeError(f"事件分类不符：{case['case_id']} / {want['frame_id']}")
    expected = case["expected"]
    actual = run_case["observed"]
    direct_fields = ("final_state", "transitions", "window_complete_ns", "submitted_at_frames")
    for key in direct_fields:
        if key in expected and actual.get(key) != expected[key]:
            raise RuntimeError(f"独立 expected 与实际 {key} 不符：{case['case_id']}，{expected[key]} != {actual.get(key)}")
    for key, wanted in expected.get("action_summary", {}).items():
        if actual.get("action_summary", {}).get(key) != wanted:
            raise RuntimeError(f"独立 expected 与实际 action_summary.{key} 不符：{case['case_id']}")
    return {
        "case_id": case["case_id"], "matrix_class": case.get("matrix_class"),
        "description": case.get("description"),
        "expected_state": expected.get("final_state"), "actual_state": actual.get("final_state"),
        "expected_action_count": expected.get("action_summary", {}).get("action_submitted", 0),
        "actual_action_count": actual.get("action_summary", {}).get("action_submitted", 0),
        "expected_time_boundary_ns": expected.get("window_complete_ns"),
        "actual_time_boundary_ns": actual.get("window_complete_ns"),
        "expected_transitions": expected.get("transitions"), "actual_transitions": actual.get("transitions"),
        "expected_submitted_at_frames": expected.get("submitted_at_frames"),
        "actual_submitted_at_frames": actual.get("submitted_at_frames"),
        "expected_virtual_input_times": expected_times, "actual_logged_frame_events": actual_times,
        "actual_log_path": display_path, "actual_log_sha256": file_sha(log_path),
        "assertions_failed": run_case.get("assertions_failed", []), "status": run_case["status"],
    }


def build_matrix() -> dict:
    source = read_json(INPUTS / "ref/case_matrix.json")
    report = read_json(OUTPUTS / "base_matrix/run_report.json")
    if report.get("status") != "PASS" or report.get("case_count") != 26:
        raise RuntimeError("新矩阵结果不是 26/26 PASS")
    cases = {row["case_id"]: row for row in source["cases"]}
    results = {row["case_id"]: row for row in report["cases"]}
    if len(cases) != 26 or len(results) != 26 or cases.keys() != results.keys():
        raise RuntimeError("输入矩阵与新运行报告的 26 个 case_id 不一致")
    detail_map = {}
    for case_id, case in cases.items():
        result = results[case_id]
        log = OUTPUTS / "base_matrix" / result["log_file"]
        detail_map[case_id] = detail(case, result, log, f"outputs/base_matrix/{result['log_file']}")

    c11_source = read_json(INPUTS / "ref/c11_case.json")
    c11_report = read_json(OUTPUTS / "c11_matrix/run_report.json")
    if c11_report.get("status") != "PASS" or c11_report.get("case_count") != 1:
        raise RuntimeError("C11 duplicate ACK 不是 1/1 PASS")
    c11_inputs = {row["case_id"]: row for row in c11_source["cases"]}
    c11_results = {row["case_id"]: row for row in c11_report["cases"]}
    if set(c11_inputs) != {"C11-duplicate-ack"} or set(c11_results) != {"C11-duplicate-ack"}:
        raise RuntimeError("C11 duplicate ACK case_id 不符")
    c11_id = "C11-duplicate-ack"
    c11_result = c11_results[c11_id]
    c11_log = OUTPUTS / "c11_matrix" / c11_result["log_file"]
    c11_detail = detail(c11_inputs[c11_id], c11_result, c11_log,
                        f"outputs/c11_matrix/{c11_result['log_file']}")

    seq = read_json(OUTPUTS / "sequence_boundary_probe.json")
    if seq.get("status") != "PASS" or seq.get("mismatches"):
        raise RuntimeError("独立序号边界期望未全部通过")
    names = ["每类稳定输入", "持续保持与冷却后保持", "手离开再出现",
             "两类快速切换/短暂抖动", "多目标/同分/目标跳变",
             "NO_HAND / 场景未知 / 低分", "TIMEOUT / ERROR / DROPPED / stale",
             "重复、倒序、缺帧、重启帧号", "时间等于阈值、前后1个计时单位",
             "无新结果但时间持续前进", "动作失败/未观察/重复ACK"]
    groups = [
        ["C1-fist-stable", "C1-palm-stable", "C1-one-stable", "C1-two_up-stable", "C1-three-stable"],
        ["C2-hold-past-cooldown", "C11-global-gate-second-acquisition", "C12-m8-two-acquisitions", "C12-gate-reopen-new-acquisition"],
        ["C3-lost-then-reappear", "C12-m8-two-acquisitions", "C12-gate-reopen-new-acquisition"],
        ["C4-jitter-reset", "C4-quick-switch", "C12-m2-m12-new-target"],
        ["C5-tie-source-order", "C5-held-priority", "C5-target-jump", "C12-m2-m12-new-target"],
        ["C6-no-hand-unknown-lowscore", "C6b-no-hand-with-detections"],
        ["C7-timeout-error-dropped-stale"],
        ["C8-duplicate-reorder-missing-restart"],
        ["C9c-30fps-later-of", "C9-s01-equal", "C9-s01-minus-1ns"],
        ["C10-tick-time-advance"],
        ["C11-fail-then-success", "C11-unobserved"],
    ]
    unique_ids = set().union(*(set(group) for group in groups))
    if unique_ids != set(cases):
        raise RuntimeError(f"11 行映射未精确覆盖 26 case：漏 {sorted(set(cases)-unique_ids)} 多 {sorted(unique_ids-set(cases))}")
    rows = []
    for name, ids in zip(names, groups):
        rows.append({"runbook_row": name, "case_ids": ids,
                     "case_details": [detail_map[case_id] for case_id in ids],
                     "status": "PASS"})
    rows[-1]["case_ids"] = rows[-1]["case_ids"] + [c11_id]
    rows[-1]["case_details"].append(c11_detail)
    rows[7]["supplemental_sequence_boundary"] = {
        "case_id": "uint32-sequence-boundary",
        "expected_path": "inputs/sequence_boundary_fixture.json",
        "actual_path": "outputs/sequence_boundary_probe.json",
        "actual_sha256": file_sha(OUTPUTS / "sequence_boundary_probe.json"),
        "exact_times_ns": [step["input"]["t_input_ns"] for step in seq["steps"]],
        "frame_ids": [step["input"]["frame_id"] for step in seq["steps"]],
        "expected_action_count": 0, "actual_action_count": 0,
        "high_water_window_anchor_invariants": "每步独立断言，见 expected_steps 与 probe post_state。",
        "assertions_failed": [], "status": "PASS",
    }
    return {
        "schema_version": 1, "task_id": "S6-C", "run_id": RUN_ID,
        "source_commit": HEAD,
        "contract_version": "S6A-G0-v1.8 / S4 s4-shared-io/1.3.0 r07",
        "matrix_source": {"run_id": "s6b_current_20261029_r08",
                          "source_run_id": "s6b_current_20261029_r03",
                          "source_commit": "e735a5afb5b474793408ec1e61da111006c70e60",
                          "case_matrix_alias": "inputs/ref/case_matrix.json",
                          "case_matrix_sha256": file_sha(INPUTS / "ref/case_matrix.json"),
                          "case_count": 26, "replayed_status": report["status"]},
        "controller_resolution": "inputs/controller_resolution.json",
        "formal_11_rows": rows,
        "base_matrix_unique_case_count": 26,
        "supplemental_duplicate_ack": {"case_id": c11_id, "expected_freeze": "outputs/c11_matrix/expected_freeze.json",
                                       "run_report": "outputs/c11_matrix/run_report.json",
                                       "actual_log": f"outputs/c11_matrix/{c11_result['log_file']}",
                                       "log_sha256": c11_detail["actual_log_sha256"],
                                       "action_submitted": c11_detail["actual_action_count"],
                                       "action_effective": c11_result["observed"]["action_summary"].get("action_effective"),
                                       "status": c11_report["status"]},
        "supplemental_sequence_boundary": {"expected": "inputs/sequence_boundary_fixture.json",
                                           "actual": "outputs/sequence_boundary_probe.json",
                                           "status": seq["status"], "step_count": len(seq["steps"])},
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "scope_note": "离线输入/虚拟时钟软件结果不构成板级 G3、实物 G4、真实阶段4/5集成或阶段6 G5。",
    }


def execute() -> None:
    baseline()
    record = read_json(RECORD)
    if record.get("status") != "PREPARED_RUN_PENDING":
        raise RuntimeError("execute 只允许在 PREPARED_RUN_PENDING 执行一次")
    OUTPUTS.mkdir()
    (OUTPUTS / "base_matrix").mkdir()
    (OUTPUTS / "c11_matrix").mkdir()
    runner = ROOT / "verification/s6b_run_cases.py"
    commands = []
    commands.append(capture("S6-B 回归 unittest",
        [str(PYTHON), "-B", "-m", "unittest", "discover", "-s", "verification", "-p", "test_s6b_*.py", "-v"],
        "outputs/s6b_unittest.log"))
    commands.append(capture("S6-C receipt boundary unittest",
        [str(PYTHON), "-B", "-m", "unittest", "verification.test_s6c_receipt_boundary", "-v"],
        "outputs/s6c_receipt_unittest.log"))
    commands.append(capture("git diff --check 本轮规格和测试",
        ["git", "-c", "core.longpaths=true", "-C", str(ROOT), "diff", "--check", "--",
         "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
         "docs/stage6/s6a_stage6_g0_behavior_v1.json",
         "verification/test_s6b_core_regressions.py"],
        "outputs/git_diff_check.log"))
    for label, folder, casefile in (
        ("基础矩阵", "base_matrix", INPUTS / "ref/case_matrix.json"),
        ("C11 duplicate ACK", "c11_matrix", INPUTS / "ref/c11_case.json"),
    ):
        common = [str(PYTHON), "-B", str(runner), "--project-root", str(ROOT),
                  "--run-dir", (RUN_DIR / "outputs" / folder).relative_to(ROOT).as_posix(),
                  "--cases", str(casefile)]
        commands.append(capture(f"{label} expected freeze",
                                common + ["--freeze-only"], f"outputs/{folder}_freeze.log"))
        commands.append(capture(f"{label} replay", common, f"outputs/{folder}_run.log"))

    sequence = run_boundary_probe()
    if sequence["status"] != "PASS":
        raise RuntimeError(f"序号边界补充失败：{sequence['mismatches']}")
    if any(row["exit_code"] != 0 for row in commands):
        raise RuntimeError("离线回归命令有非零退出；保留失败输出且不进入封包")
    base_stdout = commands[4]["stdout"]
    c11_stdout = commands[6]["stdout"]
    if "26" not in base_stdout or "PASS" not in base_stdout:
        raise RuntimeError("基础矩阵 runner 摘要未证明 26 PASS")
    if "1" not in c11_stdout or "PASS" not in c11_stdout:
        raise RuntimeError("C11 runner 摘要未证明 1 PASS")
    write_json(MATRIX, build_matrix())
    summaries = []
    for label, output_rel in (("S6-B", "outputs/s6b_unittest.log"),
                              ("S6-C", "outputs/s6c_receipt_unittest.log")):
        output = (RUN_DIR / output_rel).read_text(encoding="utf-8")
        line = next((line.strip() for line in output.splitlines() if line.strip().startswith("Ran ")), "")
        if not line or "OK" not in output:
            raise RuntimeError(f"单测汇总未 PASS：{label}")
        summaries.append({"suite": label, "summary": line})
    record["commands"] = [{key: row[key] for key in ("name", "command", "cwd", "exit_code", "output_path", "output_sha256")} for row in commands]
    record["test_summaries"] = summaries
    record["sequence_boundary"] = {"status": sequence["status"],
                                   "expected_sha256": file_sha(INPUTS / "sequence_boundary_fixture.json"),
                                   "actual_sha256": file_sha(OUTPUTS / "sequence_boundary_probe.json")}
    record["matrix_coverage_sha256"] = file_sha(MATRIX)
    record["status"] = "RUNS_PASS_PACKAGE_PENDING"
    record["finished_at_utc8"] = utc8()
    write_json(RECORD, record)
    print(json.dumps({"status": record["status"], "run_id": RUN_ID,
                      "s6b": summaries[0]["summary"], "s6c": summaries[1]["summary"],
                      "base_matrix": base_stdout.strip(), "c11": c11_stdout.strip(),
                      "sequence_boundary": sequence["status"]}, ensure_ascii=False))


def entries_for(directory: Path, include_manifest: bool = False) -> list[dict]:
    rows = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or (path == DELIVERY and not include_manifest):
            continue
        inside = path.relative_to(RUN_DIR).as_posix()
        if inside.startswith("inputs/src/") or inside.startswith("scripts/"):
            role = "source"
        elif inside.startswith("inputs/"):
            role = "input"
        elif path.suffix in {".log", ".txt", ".jsonl"}:
            role = "log"
        else:
            role = "result"
        rows.append({"path": path.relative_to(ROOT).as_posix(), "sha256": file_sha(path),
                     "role": role, "keep_reason": f"本轮 S6-C 离线证据：{inside}",
                     "hash_basis": "worktree_disk"})
    return rows


def package() -> None:
    baseline()
    record = read_json(RECORD)
    if record.get("status") != "RUNS_PASS_PACKAGE_PENDING":
        raise RuntimeError("package 只允许在所有离线回归 PASS 后运行")
    logs = {name: OUTPUTS / name for name in (
        "check_inputs.txt", "check_evidence.txt", "check_hash_basis_strict.txt", "check_closing.txt")}
    for path in logs.values():
        write_text(path, "")
    checks = [{"name": row["name"], "status": "PASS", "command": row["command"], "exit_code": row["exit_code"]}
              for row in record["commands"]]
    pending_checks = [
        {"name": "check_stage_delivery inputs", "status": "NOT_RUN", "command": "尚未运行", "exit_code": None, "reason": "固定点循环待执行"},
        {"name": "check_stage_delivery evidence", "status": "NOT_RUN", "command": "尚未运行", "exit_code": None, "reason": "固定点循环待执行"},
        {"name": "check_manifest_hash_basis strict", "status": "NOT_RUN", "command": "尚未运行", "exit_code": None, "reason": "固定点循环待执行"},
        {"name": "check_stage_delivery evidence closing", "status": "NOT_RUN", "command": "尚未运行", "exit_code": None, "reason": "固定点循环待执行"},
    ]
    checks.extend(copy.deepcopy(pending_checks))
    interface_note = "只验证 S6-C 软件与离线输入；阶段4/5真实运行期集成未执行，接口适用性仍由正式验收判定。"
    input_doc = {
        "schema_version": 1, "stage": "6", "task_id": "S6-C", "run_id": RUN_ID,
        "source_commit": HEAD, "evidence_dir": f"report/evidence/S6-C/{RUN_ID}",
        "interfaces": [], "interfaces_not_applicable_reason": interface_note,
        "hash_basis": "worktree_disk", "hash_basis_commit": HEAD,
        "files": entries_for(INPUTS) + [{"path": MATRIX.relative_to(ROOT).as_posix(),
            "sha256": file_sha(MATRIX), "role": "input", "keep_reason": "S6-C 逐 case 预期/实际/时刻/日志覆盖索引", "hash_basis": "worktree_disk"}],
        "checks": [row for row in checks if row["status"] == "PASS"],
    }
    write_json(INPUTS_MANIFEST, input_doc)
    delivery = {
        "schema_version": 1, "stage": "6", "task_id": "S6-C", "run_id": RUN_ID,
        "source_commit": HEAD, "evidence_dir": f"report/evidence/S6-C/{RUN_ID}",
        "interfaces": [], "interfaces_not_applicable_reason": interface_note,
        "hash_basis": "worktree_disk", "hash_basis_commit": HEAD,
        "hash_basis_note": "逐条按磁盘原始字节 SHA-256；源码提交 blob 与工作树差异另在 source_bindings.json 区分。",
        "files": entries_for(RUN_DIR), "checks": checks,
        "tool_versions": {"python": sys.version.split()[0], "git": git("--version"),
                          "check_stage_delivery_sha256": file_sha(MAIN_CHECKERS / "check_stage_delivery.py"),
                          "check_manifest_hash_basis_sha256": file_sha(MAIN_CHECKERS / "check_manifest_hash_basis.py")},
        "limitations": [
            "26-case 与 C11/序号边界结果只证明当前绑定软件字节对离线固定输入/虚拟时间的行为。",
            "T6-A03 因缺阶段4实测帧周期 P 仍 NOT_RUN；6-E 实物验收未执行；无板测/G3。",
            "阶段4/5真实结果链路集成如字段或上游条件不足仍 BLOCKED；本包只读消费 S4 r07 冻结契约。",
            "独立复审尚未完成；checker CHECKS_OK 不表示 G0/G2/G4/G5。",
        ],
    }
    write_json(DELIVERY, delivery)
    checker = MAIN_CHECKERS / "check_stage_delivery.py"
    basis = MAIN_CHECKERS / "check_manifest_hash_basis.py"
    for name in ("check_stage_delivery.py", "check_manifest_hash_basis.py"):
        if file_sha(MAIN_CHECKERS / name) != file_sha(INPUTS / "checkers" / name):
            raise RuntimeError(f"主 checker 快照不符：{name}")
    commands = {
        "inputs": [str(PYTHON), "-B", str(checker), "--mode", "inputs", "--manifest", str(INPUTS_MANIFEST), "--project-root", str(ROOT)],
        "evidence": [str(PYTHON), "-B", str(checker), "--mode", "evidence", "--manifest", str(DELIVERY), "--project-root", str(ROOT)],
        "hash": [str(PYTHON), "-B", str(basis), "--repo", str(ROOT), "--paths", INPUTS_MANIFEST.relative_to(ROOT).as_posix(), "--paths", DELIVERY.relative_to(ROOT).as_posix(), "--mode", "strict", "--json"],
    }
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    def run_check(command: list[str], output_path: Path) -> dict:
        result = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                                encoding="utf-8", errors="replace", env=env, check=False)
        write_text(output_path, result.stdout + result.stderr)
        return {"command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    def refresh() -> None:
        delivery["checks"] = copy.deepcopy(checks)
        delivery["files"] = entries_for(RUN_DIR)
        write_json(DELIVERY, delivery)

    last_state = None
    last = {}
    for iteration in range(8):
        refresh()
        a = run_check(commands["inputs"], logs["check_inputs.txt"])
        if a["exit_code"] != 0:
            raise RuntimeError(f"inputs checker 失败：{a['stdout']}{a['stderr']}")
        refresh()
        b = run_check(commands["evidence"], logs["check_evidence.txt"])
        if b["exit_code"] != 0:
            raise RuntimeError(f"evidence checker 失败：{b['stdout']}{b['stderr']}")
        refresh()
        c = run_check(commands["hash"], logs["check_hash_basis_strict.txt"])
        if c["exit_code"] != 0:
            raise RuntimeError(f"strict hash checker 失败：{c['stdout']}{c['stderr']}")
        refresh()
        d = run_check(commands["evidence"], logs["check_closing.txt"])
        if d["exit_code"] != 0:
            raise RuntimeError(f"closing evidence checker 失败：{d['stdout']}{d['stderr']}")
        refresh()
        state = (tuple((x["path"], x["sha256"]) for x in delivery["files"]),
                 tuple(file_sha(p) for p in logs.values()))
        last = {"inputs": a, "evidence": b, "hash": c, "closing": d}
        if iteration and state == last_state:
            break
        last_state = state
    else:
        raise RuntimeError("8 轮内 delivery 清单/校验器输出未收敛")

    for row in pending_checks:
        name = row["name"]
        alias = {"check_stage_delivery inputs": "inputs",
                 "check_stage_delivery evidence": "evidence",
                 "check_manifest_hash_basis strict": "hash",
                 "check_stage_delivery evidence closing": "closing"}[name]
        row["status"] = "PASS"
        row["command"] = last[alias]["command"]
        row["exit_code"] = 0
        row.pop("reason", None)
    record["status"] = "PACKAGED_OFFLINE_PASS_REVIEW_PENDING"
    record["packaged_at_utc8"] = utc8()
    record["package_checks"] = {key: {"exit_code": value["exit_code"], "command": value["command"]}
                                for key, value in last.items()}
    write_json(RECORD, record)
    refresh()

    # 状态记录与清单最后更新后重新求固定点，保存的 stdout 必须逐字节一致。
    last_state = None
    for iteration in range(8):
        refresh()
        ev = run_check(commands["evidence"], logs["check_evidence.txt"])
        hb = run_check(commands["hash"], logs["check_hash_basis_strict.txt"])
        if ev["exit_code"] != 0 or hb["exit_code"] != 0:
            raise RuntimeError("最终 evidence/strict hash 复核失败")
        refresh()
        closing = run_check(commands["evidence"], logs["check_closing.txt"])
        if closing["exit_code"] != 0:
            raise RuntimeError("最终 closing 复核失败")
        refresh()
        state = (tuple((x["path"], x["sha256"]) for x in delivery["files"]),
                 tuple(file_sha(p) for p in logs.values()))
        if iteration and state == last_state:
            break
        last_state = state
    else:
        raise RuntimeError("最终 fixed point 未收敛")
    final_inputs = run_check(commands["inputs"], logs["check_inputs.txt"])
    refresh()
    final_ev = run_check(commands["evidence"], logs["check_evidence.txt"])
    final_hash = run_check(commands["hash"], logs["check_hash_basis_strict.txt"])
    final_close = run_check(commands["evidence"], logs["check_closing.txt"])
    if any(x["exit_code"] != 0 for x in (final_inputs, final_ev, final_hash, final_close)):
        raise RuntimeError("最终 inputs/evidence/hash/closing 至少一项非零")
    refresh()
    print(json.dumps({"status": "CHECKS_OK_OFFLINE_MATRIX_PASS_REVIEW_PENDING", "run_id": RUN_ID,
                      "base_cases": 26, "duplicate_ack_cases": 1, "sequence_boundary_steps": 6,
                      "inputs": 0, "evidence": 0, "strict_hash": 0, "closing": 0}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="构建 S6-C 离线 evidence package")
    parser.add_argument("--stage", required=True, choices=("prepare", "execute", "package"))
    stage = parser.parse_args().stage
    try:
        if stage == "prepare":
            prepare()
        elif stage == "execute":
            execute()
        else:
            package()
        return 0
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}\n"
        if RUN_DIR.is_dir():
            write_text(OUTPUTS / f"{stage}_failure.txt", error)
        sys.stderr.write(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
