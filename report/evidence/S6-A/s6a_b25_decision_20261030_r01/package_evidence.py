#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""封装 B25 回绕裁决的离线输入、回归结果与清单自检证据。"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
RUN_REL = RUN.relative_to(ROOT).as_posix()
RUN_ID = RUN.name
HEAD_EXPECTED = "638353b92c83b88bc667bd23284b7fc0375a54ac"
PYTHON = Path(sys.executable).resolve()
MAIN_ROOT = Path(r"D:\FPGA_Competition")
MAIN_CHECKER = MAIN_ROOT / "verification" / "check_manifest_hash_basis.py"
MAIN_DELIVERY_CHECKER = MAIN_ROOT / "verification" / "check_stage_delivery.py"
MANIFEST = RUN / "delivery_manifest.json"
MANIFEST_REL = MANIFEST.relative_to(ROOT).as_posix()

SOURCES = {
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md": "source",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json": "source",
    "verification/test_s6b_core_regressions.py": "source",
    "src/stage6/s6_core.py": "source",
    "verification/s6_g0_selfcheck.py": "source",
    "report/evidence/S6-A/s6a_g0_20261024_r17/hand_computed_cases.json": "input",
    "report/evidence/S6-A/s6a_g0_20261024_r17/upstream_bindings.json": "input",
    "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json": "input",
    "report/evidence/S6-A/s6a_b25_decision_20261029_r04/inputs/DSH-20261029-004-b25-frame-session-ruling.md": "input",
    "report/evidence/S6-A/s6a_b25_decision_20261029_r04/inputs/DSH-20261029-005-b25-reaffirm-and-6c-closing.md": "input",
    "report/evidence/S6-A/s6a_b25_decision_20261029_r04/prior_failed_runs.json": "input",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def checked_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def copy_input(relative: str, destination: str) -> Path:
    source = ROOT / relative
    if not source.is_file():
        raise FileNotFoundError(f"输入文件不存在：{source}")
    target = RUN / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    return target


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout.strip()


def restore_pre_task_snapshots() -> dict[str, Path]:
    """仅反向移除本脚本对应的三处增量，保留此前工作区内容。"""
    doc_path = ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
    json_path = ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
    test_path = ROOT / "verification/test_s6b_core_regressions.py"

    doc = checked_text(doc_path)
    doc_new = "| 倒序 | `frame_id` 小于上一条已处理值且 `session_id` 未变；包含同会话 uint32 回绕后的较小值 | 该帧一律按倒序拒绝：不推进窗口或 `WINDOW_MATCH` 计数，不更新帧序列高水位；计异常且不因回退复位会话。超时/失踪期限仍按单调时间评估 | `E_FRAME_OUT_OF_ORDER` |"
    doc_old = "| 倒序 | `frame_id` 小于上一条已处理值且 `session_id` 未变 | 该帧不推进窗口或 `WINDOW_MATCH` 计数，不更新帧序列高水位；计异常且不因回退复位会话。超时/失踪期限仍按单调时间评估 | `E_FRAME_OUT_OF_ORDER` |"
    if doc.count(doc_new) != 1:
        raise ValueError("人读规格回退锚点不唯一，拒绝生成原始快照")
    doc = doc.replace(doc_new, doc_old, 1)
    doc_newline = "\r\n" if "\r\n" in doc else "\n"
    added_doc = "| 同会话回绕输入 | 已接受较大帧号后收到回绕后的较小值，包括 `0xFFFFFFFF→0`、`0xFFFFFFFE→0` | 一律按 B23 拒绝，不更新高水位或目标/窗口证据；单调时间仍推进。更换 `session_id` 后方可重新从 0 开始 | `E_FRAME_OUT_OF_ORDER` |\n\n> **回绕裁决边界（2026-10-30）**：Wong 明确批准同一 `session_id` 下回绕输入一律拒绝。本轮没有裁决 §13 中 `0xFFFFFFFE` 的提前停发/换会话阈值应如何解释；该阈值保持待决，不得从回绕拒绝规则推导 `0xFFFFFFFF` 前后的可接受序列。\n".replace("\n", doc_newline)
    if doc.count(added_doc) != 1:
        raise ValueError("人读规格新增行不唯一，拒绝生成原始快照")
    doc = doc.replace(added_doc, "", 1)

    machine = checked_text(json_path)
    new_condition = '"condition": "frame_id 小于上一条已处理值且 session_id 未变；包含同会话 uint32 回绕后的较小值"'
    old_condition = '"condition": "frame_id 小于上一条已处理值且 session_id 未变"'
    new_output = '"output": "该帧一律按倒序拒绝，不推进窗口或目标证据，不更新帧序列高水位；计异常且不因回退复位会话，期限仍按单调时间评估"'
    old_output = '"output": "该帧不推进窗口或目标证据，不更新帧序列高水位；计异常且不因回退复位会话，期限仍按单调时间评估"'
    for current, original in ((new_condition, old_condition), (new_output, old_output)):
        if machine.count(current) != 1:
            raise ValueError("机器规格回退锚点不唯一，拒绝生成原始快照")
        machine = machine.replace(current, original, 1)
    machine_newline = "\r\n" if "\r\n" in machine else "\n"
    policy = '      "frame_id_wrap_policy": {\n        "scope": "same session_id",\n        "examples": ["0xFFFFFFFF→0", "0xFFFFFFFE→0"],\n        "classification": "B23 / OUT_OF_ORDER",\n        "rule": "同一 session_id 下任何回绕后的较小 frame_id 一律拒绝；不更新帧序列高水位或目标/窗口证据，期限仍按单调时间评估；更换 session_id 后方可重新从 0 开始。",\n        "approval_ref": "report/evidence/S6-A/s6a_b25_decision_20261030_r01/decision_receipt.json",\n        "unresolved": "0xFFFFFFFE 是否为提前停止递增或强制换 session_id 的阈值，本轮未裁决；不得据此推定 0xFFFFFFFF 边界的可接受序列。"\n      },\n'.replace("\n", machine_newline)
    if machine.count(policy) != 1:
        raise ValueError("机器规格策略块不唯一，拒绝生成原始快照")
    machine = machine.replace(policy, "", 1)

    test_lines = checked_text(test_path).splitlines(keepends=True)
    start = next((i for i, line in enumerate(test_lines) if line.startswith("    def test_uint32_frame_wrap_is_rejected_until_session_changes(")), None)
    stop = next((i for i, line in enumerate(test_lines) if line.startswith("    def test_out_of_order_at_l02_runs_loss_check_without_refreshing_progress(")), None)
    if start is None or stop is None or stop <= start:
        raise ValueError("回归测试快照锚点异常，拒绝构造旧内容")
    del test_lines[start:stop]

    snapshot_dir = RUN / "inputs" / "pre_task_snapshot"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshots = {
        "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md": snapshot_dir / "S6A_stage6_g0_behavior_spec_v1.md",
        "docs/stage6/s6a_stage6_g0_behavior_v1.json": snapshot_dir / "s6a_stage6_g0_behavior_v1.json",
        "verification/test_s6b_core_regressions.py": snapshot_dir / "test_s6b_core_regressions.py",
    }
    snapshots["docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"].write_bytes(doc.encode("utf-8"))
    snapshots["docs/stage6/s6a_stage6_g0_behavior_v1.json"].write_bytes(machine.encode("utf-8"))
    snapshots["verification/test_s6b_core_regressions.py"].write_bytes("".join(test_lines).encode("utf-8"))
    return snapshots


def create_task_delta(snapshots: dict[str, Path]) -> Path:
    diffs: list[str] = []
    for rel, snapshot in snapshots.items():
        before = checked_text(snapshot).replace("\r\n", "\n").splitlines(keepends=True)
        after = checked_text(ROOT / rel).replace("\r\n", "\n").splitlines(keepends=True)
        diffs.extend(difflib.unified_diff(before, after, fromfile=f"a/{rel}", tofile=f"b/{rel}", n=3))
    target = RUN / "task_owned_delta.patch"
    target.write_text("".join(diffs), encoding="utf-8", newline="\n")
    return target


def make_manifest(checks: list[dict[str, object]]) -> dict[str, object]:
    files: list[dict[str, object]] = []
    for item in sorted(p for p in RUN.rglob("*") if p.is_file() and p != MANIFEST):
        relative = item.relative_to(ROOT).as_posix()
        role = "source" if item.name == "package_evidence.py" else "input" if "/inputs/" in relative or relative.endswith("/decision_receipt.json") else "result"
        entry: dict[str, object] = {
            "path": relative,
            "sha256": sha256_file(item),
            "role": role,
            "hash_basis": "worktree_disk",
            "keep_reason": "本轮 B25 回绕裁决及验证可复核输入/结果。",
        }
        files.append(entry)
    for relative, role in SOURCES.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"清单外部绑定文件不存在：{path}")
        files.append({
            "path": relative,
            "sha256": sha256_file(path),
            "role": role,
            "hash_basis": "worktree_disk",
            "keep_reason": "绑定回绕行为规格、运行核心与实际回归/自检输入。",
        })
    return {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": git_output("rev-parse", "HEAD"),
        "evidence_dir": RUN_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本包只验证阶段6离线回绕分类与行为规格；阶段4 r07 冻结文件作为文件输入绑定，不执行跨阶段真实集成。",
        "files": files,
        "hash_basis": "worktree_disk",
        "hash_basis_note": "本轮规格/测试含未提交差异，按工作树字节绑定；提交后由总控另做 commit_blob 复核。",
        "checks": checks,
        "tool_versions": {
            "python": "3.12.14",
            "s6_g0_selfcheck": "r04",
            "check_stage_delivery": "main-worktree read-only",
            "check_manifest_hash_basis": "main-worktree read-only",
        },
        "limitations": [
            "结论仅限本工作树绑定版本的离线行为与单元测试，不代表板级实时性能或实物验收。",
            "0xFFFFFFFE 提前停发/换 session_id 阈值未获本轮单独裁决，保持待决。",
            "G3、G4 实物验收、6-D 真实集成与阶段 G5 未由本包验证。",
        ],
    }


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


def run_selfcheck(save_artifacts: bool) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="s6a_b25_c11_") as temp_dir:
        out_path = Path(temp_dir) / "selfcheck_result.json"
        command = [
            str(PYTHON), "-B", "-X", "utf8", str(ROOT / "verification/s6_g0_selfcheck.py"),
            "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
            "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
            "--cases", "report/evidence/S6-A/s6a_g0_20261024_r17/hand_computed_cases.json",
            "--upstream", "report/evidence/S6-A/s6a_g0_20261024_r17/upstream_bindings.json",
            "--out", str(out_path), "--project-root", str(ROOT), "--evidence-dir", RUN_REL,
            "--manifest", MANIFEST_REL, "--state", ".codex/STATE.md",
        ]
        result = run(command)
        if save_artifacts:
            output_copy = RUN / "selfcheck_result.json"
            stdout_copy = RUN / "selfcheck_stdout.txt"
            stderr_copy = RUN / "selfcheck_stderr.txt"
            if out_path.is_file():
                output_copy.write_bytes(out_path.read_bytes())
            else:
                write_json(output_copy, {"result_file_created": False, "exit_code": result.returncode})
            stdout_copy.write_text(result.stdout, encoding="utf-8", newline="\n")
            stderr_copy.write_text(result.stderr, encoding="utf-8", newline="\n")
        return result.returncode, subprocess.list2cmdline(command)


def run_json_checker(name: str, command: list[str]) -> tuple[int, str, dict[str, object]]:
    result = run(command)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}
    write_json(RUN / name, payload)
    return result.returncode, subprocess.list2cmdline(command), payload


def preflight() -> None:
    """只读检查即将封入 RunId 的路径、基线、锚点与已保存测试结果。"""
    actual_head = git_output("rev-parse", "HEAD")
    branch = git_output("branch", "--show-current")
    if actual_head != HEAD_EXPECTED or branch != "stage6-interact-prep":
        raise RuntimeError(f"基线不符：HEAD={actual_head}, branch={branch}")
    if not RUN.is_dir() or RUN.name != "s6a_b25_decision_20261030_r01":
        raise RuntimeError(f"RunId 路径不符：{RUN}")
    if MANIFEST.exists():
        raise RuntimeError(f"目标 manifest 已存在，拒绝复用 RunId：{MANIFEST}")
    for relative in SOURCES:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(f"输入路径缺失：{ROOT / relative}")
    if not MAIN_CHECKER.is_file() or not MAIN_DELIVERY_CHECKER.is_file():
        raise FileNotFoundError("主目录只读 checker 路径不完整")
    doc = checked_text(ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
    machine = json.loads(checked_text(ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
    test_source = checked_text(ROOT / "verification/test_s6b_core_regressions.py")
    receipt = json.loads(checked_text(RUN / "decision_receipt.json"))
    if doc.count("同会话回绕输入") != 1 or doc.count("回绕裁决边界（2026-10-30）") != 1:
        raise RuntimeError("人读规格中的回绕规则或未决边界未唯一落位")
    doc_newline = "\r\n" if "\r\n" in doc else "\n"
    expected_doc_addition = "| 同会话回绕输入 | 已接受较大帧号后收到回绕后的较小值，包括 `0xFFFFFFFF→0`、`0xFFFFFFFE→0` | 一律按 B23 拒绝，不更新高水位或目标/窗口证据；单调时间仍推进。更换 `session_id` 后方可重新从 0 开始 | `E_FRAME_OUT_OF_ORDER` |\n\n> **回绕裁决边界（2026-10-30）**：Wong 明确批准同一 `session_id` 下回绕输入一律拒绝。本轮没有裁决 §13 中 `0xFFFFFFFE` 的提前停发/换会话阈值应如何解释；该阈值保持待决，不得从回绕拒绝规则推导 `0xFFFFFFFF` 前后的可接受序列。\n".replace("\n", doc_newline)
    if doc.count(expected_doc_addition) != 1:
        raise RuntimeError("人读规格精确快照锚点不唯一")
    if "达到 `0xFFFFFFFE`" not in doc:
        raise RuntimeError("原有 FFFE 阈值行不见，停止以防覆盖未决语义")
    b23 = next(row for row in machine["behavior_rows"] if row.get("id") == "B23")
    policy = b23.get("frame_id_wrap_policy", {})
    if policy.get("classification") != "B23 / OUT_OF_ORDER" or "未裁决" not in policy.get("unresolved", ""):
        raise RuntimeError("机器规格缺少回绕拒绝或 FFFE 未决声明")
    machine_newline = "\r\n" if "\r\n" in checked_text(ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json") else "\n"
    expected_policy = '      "frame_id_wrap_policy": {\n        "scope": "same session_id",\n        "examples": ["0xFFFFFFFF→0", "0xFFFFFFFE→0"],\n        "classification": "B23 / OUT_OF_ORDER",\n        "rule": "同一 session_id 下任何回绕后的较小 frame_id 一律拒绝；不更新帧序列高水位或目标/窗口证据，期限仍按单调时间评估；更换 session_id 后方可重新从 0 开始。",\n        "approval_ref": "report/evidence/S6-A/s6a_b25_decision_20261030_r01/decision_receipt.json",\n        "unresolved": "0xFFFFFFFE 是否为提前停止递增或强制换 session_id 的阈值，本轮未裁决；不得据此推定 0xFFFFFFFF 边界的可接受序列。"\n      },\n'.replace("\n", machine_newline)
    if checked_text(ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json").count(expected_policy) != 1:
        raise RuntimeError("机器规格精确快照锚点不唯一")
    if "批准" not in receipt.get("decision_scope", "") and "一律按 B23 倒序拒绝" not in receipt.get("decision_scope", ""):
        raise RuntimeError("决定回执缺少本轮明确批准的范围")
    if "test_uint32_frame_wrap_is_rejected_until_session_changes" not in test_source:
        raise RuntimeError("新增边界测试不存在")
    if test_source.count("# 直接注入高水位隔离回绕分类") != 1:
        raise RuntimeError("测试未显式隔离 FFFE 可达性结论")
    for relative in ("test_exit_code_final.txt", "regression_full_exit_code_final.txt"):
        code_file = RUN / relative
        if not code_file.is_file() or code_file.read_text(encoding="utf-8").strip() != "0":
            raise RuntimeError(f"最终测试退出码缺失或非 0：{code_file}")
    lock_path = ROOT / git_output("rev-parse", "--git-path", "index.lock")
    result = {
        "status": "PREFLIGHT_OK",
        "worktree": str(ROOT),
        "branch": branch,
        "head": actual_head,
        "run_id": RUN_ID,
        "index_lock_path": str(lock_path),
        "index_lock_present": lock_path.exists(),
        "source_and_input_paths": "ALL_PRESENT",
        "s4_contract_sha256": sha256_file(ROOT / "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json"),
        "fffe_threshold": "PRESERVED_AND_UNRESOLVED",
        "tests": {"directed": 0, "full_core": 0},
        "manifest_present_before_package": False,
        "writes_performed": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> int:
    if "--preflight" in sys.argv:
        preflight()
        return 0
    actual_head = git_output("rev-parse", "HEAD")
    branch = git_output("branch", "--show-current")
    if actual_head != HEAD_EXPECTED or branch != "stage6-interact-prep":
        raise RuntimeError(f"基线已变化，停止封包：HEAD={actual_head}, branch={branch}")

    snapshots = restore_pre_task_snapshots()
    create_task_delta(snapshots)
    copy_map = {
        "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json": "inputs/s4_contract_r07.json",
        "report/evidence/S6-A/s6a_g0_20261024_r17/hand_computed_cases.json": "inputs/s6a_cases_r17.json",
        "report/evidence/S6-A/s6a_g0_20261024_r17/upstream_bindings.json": "inputs/s6a_upstream_r17.json",
        "report/evidence/S6-A/s6a_b25_decision_20261029_r04/inputs/DSH-20261029-004-b25-frame-session-ruling.md": "inputs/prior_ruling_dsh_004.md",
        "report/evidence/S6-A/s6a_b25_decision_20261029_r04/inputs/DSH-20261029-005-b25-reaffirm-and-6c-closing.md": "inputs/prior_ruling_dsh_005.md",
        "report/evidence/S6-A/s6a_b25_decision_20261029_r04/prior_failed_runs.json": "inputs/prior_failed_runs.json",
        "verification/s6_g0_selfcheck.py": "inputs/s6_g0_selfcheck.py",
        "src/stage6/s6_core.py": "inputs/s6_core.py",
        "verification/test_s6b_core_regressions.py": "inputs/test_s6b_core_regressions_after.py",
    }
    for relative, destination in copy_map.items():
        copy_input(relative, destination)
    copy_input(".codex/STATE.md", "inputs/state_at_run.md")
    (RUN / "inputs" / "main_check_manifest_hash_basis.py").write_bytes(MAIN_CHECKER.read_bytes())
    (RUN / "inputs" / "main_check_stage_delivery.py").write_bytes(MAIN_DELIVERY_CHECKER.read_bytes())

    status_before = git_output("status", "--short", "--untracked-files=normal")
    initial_check = {
        "id": "C0_BASELINE",
        "head": actual_head,
        "branch": branch,
        "index_lock_path": git_output("rev-parse", "--git-path", "index.lock"),
        "worktree_status_at_package_time": status_before,
        "pre_task_snapshot_hashes": {rel: sha256_file(path) for rel, path in snapshots.items()},
        "interpretation": "快照由当前文件精确反向移除本脚本的显式增量得到；此前 STATE、两规格及未跟踪 RunId 均保留。",
    }
    write_json(RUN / "pre_task_hash_verification.json", initial_check)
    write_json(RUN / "run_context.json", {
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "branch": branch,
        "worktree": str(ROOT),
        "hardware_used": False,
        "vivado_used": False,
        "scope": "B23/B25 same-session uint32 wrap rejection; offline only",
        "fffe_threshold": "NOT_DECIDED",
        "superseded_attempts": [
            {"output": "test_output.txt", "reason": "同一回归在最终测试收窄前运行；由 test_output_final.txt 取代。"},
            {"output": "regression_full_output.txt", "reason": "全量回归在最终测试收窄前运行；由 regression_full_output_final.txt 取代。"},
        ],
    })

    test_commands = [
        [str(PYTHON), "-B", "-X", "utf8", "-m", "unittest", "verification.test_s6b_core_regressions.S6BCoreRegressionTests.test_uint32_frame_wrap_is_rejected_until_session_changes", "-v"],
        [str(PYTHON), "-B", "-X", "utf8", "-m", "unittest", "verification.test_s6b_core_regressions", "-v"],
    ]
    test_results = []
    for index, command in enumerate(test_commands, start=1):
        output_name = "test_output_final.txt" if index == 1 else "regression_full_output_final.txt"
        code_name = "test_exit_code_final.txt" if index == 1 else "regression_full_exit_code_final.txt"
        output_file = RUN / output_name
        code_file = RUN / code_name
        if not output_file.is_file() or not code_file.is_file():
            raise FileNotFoundError(f"实际回归输出或退出码缺失：{output_file} / {code_file}")
        code = int(code_file.read_text(encoding="utf-8").strip())
        test_results.append({
            "name": "B25 定向回绕回归" if index == 1 else "S6-B 核心回归全套",
            "status": "PASS" if code == 0 else "FAIL",
            "command": subprocess.list2cmdline(command),
            "exit_code": code,
            "reason": None if code == 0 else "真实回归命令返回非零；完整输出保存在本 RunId。",
        })

    initial_checks = [*test_results, {
        "name": "S6-A 完整自检（含 C11）",
        "status": "NOT_RUN",
        "command": "pending",
        "exit_code": None,
        "reason": "尚未运行 C11 自检。",
    }]
    write_json(MANIFEST, make_manifest(initial_checks))

    c11_code, c11_command = run_selfcheck(save_artifacts=True)
    c11_status = "PASS" if c11_code == 0 else "FAIL"
    checks = [*test_results, {
        "name": "S6-A 完整自检（含 C11）",
        "status": c11_status,
        "command": c11_command,
        "exit_code": c11_code,
        "reason": None if c11_code == 0 else "完整 S6-A 自检返回非零；C11 与其余检查详情见 selfcheck_initial_result.json。",
    }]
    write_json(MANIFEST, make_manifest(checks))

    hash_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_CHECKER), "--repo", str(ROOT), "--commit", actual_head, "--paths", MANIFEST_REL, "--mode", "strict", "--json"]
    hash_code, hash_cmd_text, hash_payload = run_json_checker("hash_basis_check.json", hash_command)
    checks.append({
        "name": "证据 manifest 严格 hash_basis",
        "status": "PASS" if hash_code == 0 else "FAIL",
        "command": hash_cmd_text,
        "exit_code": hash_code,
        "reason": None if hash_code == 0 else "严格 hash_basis 校验失败；详情见 hash_basis_check.json。",
    })
    write_json(MANIFEST, make_manifest(checks))

    inputs_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_DELIVERY_CHECKER), "--mode", "inputs", "--manifest", MANIFEST_REL, "--project-root", str(ROOT)]
    inputs_code, inputs_cmd_text, _ = run_json_checker("inputs_check.json", inputs_command)
    checks.append({
        "name": "主目录 inputs 清单检查",
        "status": "PASS" if inputs_code == 0 else "FAIL",
        "command": inputs_cmd_text,
        "exit_code": inputs_code,
        "reason": None if inputs_code == 0 else "inputs 模式检查失败；详情见 inputs_check.json。",
    })
    write_json(MANIFEST, make_manifest(checks))

    evidence_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_DELIVERY_CHECKER), "--mode", "evidence", "--manifest", MANIFEST_REL, "--project-root", str(ROOT)]
    evidence_code, evidence_cmd_text, _ = run_json_checker("evidence_check.json", evidence_command)
    checks.append({
        "name": "主目录 evidence 清单检查",
        "status": "PASS" if evidence_code == 0 else "FAIL",
        "command": evidence_cmd_text,
        "exit_code": evidence_code,
        "reason": None if evidence_code == 0 else "evidence 模式检查失败；详情见 evidence_check.json。",
    })
    write_json(MANIFEST, make_manifest(checks))

    final_codes: dict[str, int | None] = {}
    first_codes = {"c11": c11_code, "hash_basis": hash_code, "inputs": inputs_code, "evidence": evidence_code}
    final_commands = {"c11": c11_command, "hash_basis": hash_cmd_text, "inputs": inputs_cmd_text, "evidence": evidence_cmd_text}
    for key, initial_code in first_codes.items():
        if initial_code != 0:
            final_codes[key] = None
        elif key == "c11":
            final_codes[key] = run_selfcheck(save_artifacts=False)[0]
        elif key == "hash_basis":
            final_codes[key] = run(hash_command).returncode
        elif key == "inputs":
            final_codes[key] = run(inputs_command).returncode
        else:
            final_codes[key] = run(evidence_command).returncode
    names = {
        "c11": "S6-A 最终包复核（含 C11）",
        "hash_basis": "严格 hash_basis 最终复核",
        "inputs": "inputs 清单最终复核",
        "evidence": "evidence 清单最终复核",
    }
    commands = final_commands
    for key, code in final_codes.items():
        status = "PASS" if code == 0 else "FAIL" if code is not None else "NOT_RUN"
        checks.append({
            "name": names[key],
            "status": status,
            "command": commands[key] if code is not None else None,
            "exit_code": code,
            "reason": None if code == 0 else (f"最终复核返回 exit {code}；首轮原始结果与最终退出码均保留。" if code is not None else "首轮检查失败，按要求不重复运行该工具。"),
        })
    write_json(MANIFEST, make_manifest(checks))

    result = {
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "test_exit_codes": [item["exit_code"] for item in test_results],
        "initial_c11_exit_code": c11_code,
        "initial_hash_basis_exit_code": hash_code,
        "inputs_check_exit_code": inputs_code,
        "evidence_check_exit_code": evidence_code,
        "final_exit_codes": final_codes,
        "verdict": "PASS" if c11_code == 0 and hash_code == 0 and inputs_code == 0 and evidence_code == 0 and all(code == 0 for code in final_codes.values()) else "REVIEW_REQUIRED",
        "review_status": "PENDING_INDEPENDENT_REVIEW",
        "hardware_status": "NOT_RUN",
        "fffe_threshold_status": "UNDECIDED",
        "evidence_dir": RUN_REL,
    }
    # 最后只更新 manifest 的检查元数据；文件清单与被检字节保持不变。
    write_json(MANIFEST, make_manifest(checks))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"封包异常：{type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
