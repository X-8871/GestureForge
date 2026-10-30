#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为 B25 绑定最终同会话回绕规格并复验 r02 报告的封包固定点。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[3]
RUN_REL = RUN.relative_to(ROOT).as_posix()
RUN_ID = RUN.name
HEAD_EXPECTED = "638353b92c83b88bc667bd23284b7fc0375a54ac"
MAIN_ROOT = Path(r"D:\FPGA_Competition")
MAIN_HASH = MAIN_ROOT / "verification" / "check_manifest_hash_basis.py"
MAIN_DELIVERY = MAIN_ROOT / "verification" / "check_stage_delivery.py"
SELF_CHECK = ROOT / "verification" / "s6_g0_selfcheck.py"
MANIFEST = RUN / "delivery_manifest.json"
MANIFEST_REL = MANIFEST.relative_to(ROOT).as_posix()
PYTHON = Path(sys.executable).resolve()

BEHAVIOR_DOC = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
BEHAVIOR_JSON = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
CASES = "report/evidence/S6-A/s6a_g0_20261024_r17/hand_computed_cases.json"
UPSTREAM = "report/evidence/S6-A/s6a_g0_20261024_r17/upstream_bindings.json"
S4_CONTRACT = "report/evidence/S6-D/s6d_replay_qualification_20261029_r05/inputs/w4/s4b_shared_input_result_contract.json"
R01 = "report/evidence/S6-A/s6a_b25_decision_20261030_r01"
R02 = "report/evidence/S6-A/s6a_b25_decision_20261030_r02"

TEST_DIRECTED = [str(PYTHON), "-B", "-X", "utf8", "-m", "unittest",
                 "verification.test_s6b_core_regressions.S6BCoreRegressionTests.test_uint32_frame_wrap_is_rejected_until_session_changes", "-v"]
TEST_FULL = [str(PYTHON), "-B", "-X", "utf8", "-m", "unittest", "verification.test_s6b_core_regressions", "-v"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def write_json(path: Path, value: object) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)


def run_c11(out_path: Path, evidence_rel: str, manifest_rel: str) -> tuple[int, list[str], bytes, bytes, bytes]:
    command = [
        str(PYTHON), "-B", "-X", "utf8", str(SELF_CHECK),
        "--json", BEHAVIOR_JSON, "--doc", BEHAVIOR_DOC,
        "--cases", CASES, "--upstream", UPSTREAM,
        "--out", str(out_path), "--project-root", str(ROOT),
        "--evidence-dir", evidence_rel, "--manifest", manifest_rel,
        "--state", ".codex/STATE.md",
    ]
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
    output = out_path.read_bytes() if out_path.is_file() else b""
    return proc.returncode, command, output, proc.stdout, proc.stderr


def command_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def check_command(name: str, command: list[str], exit_code: int, reason: str | None = None) -> dict[str, object]:
    return {
        "name": name,
        "status": "PASS" if exit_code == 0 else "FAIL",
        "command": command_text(command),
        "exit_code": exit_code,
        "reason": reason if exit_code != 0 else None,
    }


def copy_item(source: Path, destination: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(f"来源不存在：{source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    return destination


def external_sources() -> list[tuple[str, str]]:
    return [
        (BEHAVIOR_DOC, "source"),
        (BEHAVIOR_JSON, "source"),
        ("verification/test_s6b_core_regressions.py", "source"),
        ("src/stage6/s6_core.py", "source"),
        ("verification/s6_g0_selfcheck.py", "source"),
        (CASES, "input"),
        (UPSTREAM, "input"),
        (S4_CONTRACT, "input"),
        (f"{R01}/delivery_manifest.json", "input"),
        (f"{R01}/hash_basis_check.json", "input"),
        (f"{R01}/selfcheck_result.json", "input"),
        (f"{R01}/decision_receipt.json", "input"),
        (f"{R01}/task_owned_delta.patch", "input"),
        (f"{R01}/pre_task_hash_verification.json", "input"),
        (f"{R02}/delivery_manifest.json", "input"),
        (f"{R02}/hash_basis_check.json", "input"),
        (f"{R02}/selfcheck_result.json", "input"),
        (f"{R02}/fixed_point_iterations.json", "input"),
    ]


def make_manifest(checks: list[dict[str, object]]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for path in sorted(p for p in RUN.rglob("*") if p.is_file() and p != MANIFEST):
        rel = path.relative_to(ROOT).as_posix()
        if "/inputs/" in rel or "/preflight/" in rel:
            role = "input" if "/inputs/" in rel else "artifact"
        elif path.name == "package_r03.py":
            role = "source"
        elif path.name.endswith("_output.txt") or path.name.endswith("_exit_code.txt") or path.name.endswith("_stdout.txt"):
            role = "log"
        elif path.name.endswith("_check.json") or path.name in {"selfcheck_result.json", "hash_basis_check.json", "inputs_check.json", "evidence_check.json"}:
            role = "result"
        else:
            role = "artifact"
        entries.append({
            "path": rel,
            "sha256": sha_file(path),
            "role": role,
            "hash_basis": "worktree_disk",
            "keep_reason": "r03 最终规格快照、回归和完整清单固定点复核证据。",
        })
    for rel, role in external_sources():
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"外部绑定路径不存在：{path}")
        entries.append({
            "path": rel,
            "sha256": sha_file(path),
            "role": role,
            "hash_basis": "worktree_disk",
            "keep_reason": "绑定已审源码/规格、S4 r07、S6-A 自检输入及 r01 修复轨迹。",
        })
    return {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": HEAD_EXPECTED,
        "evidence_dir": RUN_REL,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本 RunId 只修复 r01 的离线证据清单固定点，不执行阶段4/5真实集成。",
        "files": entries,
        "hash_basis": "worktree_disk",
        "hash_basis_note": "S6-A 规格/回归在本轮起始时已是工作区差异；最终 stdout 文件字节逐项绑定，提交后由总控复核 commit_blob。",
        "checks": checks,
        "tool_versions": {
            "python": sys.version.split()[0],
            "s6_g0_selfcheck": "r04",
            "check_manifest_hash_basis": "main-worktree read-only",
            "check_stage_delivery": "main-worktree read-only",
        },
        "limitations": [
            "本 RunId 只修复审查发现的 r01 证据固定点，不改变源码、规格或用户阈值。",
            "回放/离线检查不构成板级 G3、实物 G4 或阶段 G5。",
            "0xFFFFFFFE 提前停发或换 session_id 阈值仍未裁决。",
        ],
    }


def write_manifest(checks: list[dict[str, object]]) -> None:
    write_json(MANIFEST, make_manifest(checks))


def update_check(checks: list[dict[str, object]], name: str, command: list[str], code: int) -> None:
    for item in checks:
        if item["name"] == name:
            item.update(check_command(name, command, code,
                                      None if code == 0 else f"工具返回 exit {code}，完整输出保留在本 RunId。"))
            return
    checks.append(check_command(name, command, code,
                                None if code == 0 else f"工具返回 exit {code}，完整输出保留在本 RunId。"))


def preflight_fixed_point() -> dict[str, object]:
    base = ROOT / "tmp/stage6/S6-A/s6a_b25_decision_20261030_r03_preflight"
    scratch = base
    suffix = 2
    while scratch.exists():
        scratch = base.with_name(base.name + f"_{suffix:02d}")
        suffix += 1
    evidence = scratch / "evidence"
    evidence_rel = evidence.relative_to(ROOT).as_posix()
    scratch_manifest = scratch / "delivery_manifest.json"
    scratch_manifest_rel = scratch_manifest.relative_to(ROOT).as_posix()
    evidence.mkdir(parents=True)
    for name, value in (
        ("selfcheck_result.json", {"preflight_placeholder": True}),
        ("selfcheck_stdout.txt", "PRECHECK\n"),
        ("selfcheck_stderr.txt", ""),
        ("hash_basis_check.json", {"preflight_placeholder": True}),
    ):
        target = evidence / name
        if name.endswith(".json"):
            write_json(target, value)
        else:
            target.write_text(str(value), encoding="utf-8", newline="\n")
    file_entries = []
    for item in sorted(p for p in evidence.rglob("*") if p.is_file()):
        file_entries.append({
            "path": item.relative_to(ROOT).as_posix(),
            "sha256": sha_file(item),
            "hash_basis": "worktree_disk",
        })
    for rel in (BEHAVIOR_DOC, BEHAVIOR_JSON, CASES, UPSTREAM):
        item = ROOT / rel
        file_entries.append({"path": rel, "sha256": sha_file(item), "hash_basis": "worktree_disk"})
    preflight_manifest = {
        "schema_version": 1,
        "task_id": "S6-A",
        "run_id": "r03_fixed_point_preflight",
        "evidence_dir": evidence_rel,
        "files": file_entries,
        "hash_basis": "worktree_disk",
    }
    write_json(scratch_manifest, preflight_manifest)
    c11_iterations: list[dict[str, object]] = []
    hash_iterations: list[dict[str, object]] = []

    for index in range(1, 4):
        output_path = scratch / f"c11_probe_{index}.json"
        code, command, result_bytes, stdout, stderr = run_c11(output_path, evidence_rel, scratch_manifest_rel)
        if code != 0 or not result_bytes:
            raise RuntimeError(f"C11 固定点预演第 {index} 轮失败，exit={code}")
        result_file = evidence / "selfcheck_result.json"
        stdout_file = evidence / "selfcheck_stdout.txt"
        stderr_file = evidence / "selfcheck_stderr.txt"
        actual_stdout = stdout
        actual_stderr = stderr
        if (result_file.read_bytes() == result_bytes
                and stdout_file.read_bytes() == actual_stdout
                and stderr_file.read_bytes() == actual_stderr):
            c11_iterations.append({
                "iteration": index,
                "command": command_text(command),
                "exit_code": code,
                "result_sha256": sha(result_bytes),
                "stdout_sha256": sha(actual_stdout),
                "stderr_sha256": sha(actual_stderr),
                "equals_saved_files": True,
            })
            break
        result_file.write_bytes(result_bytes)
        stdout_file.write_bytes(actual_stdout)
        stderr_file.write_bytes(actual_stderr)
        for entry in preflight_manifest["files"]:
            if entry["path"] in {result_file.relative_to(ROOT).as_posix(), stdout_file.relative_to(ROOT).as_posix(),
                                  stderr_file.relative_to(ROOT).as_posix()}:
                entry["sha256"] = sha_file(ROOT / entry["path"])
        write_json(scratch_manifest, preflight_manifest)
        c11_iterations.append({
            "iteration": index,
            "command": command_text(command),
            "exit_code": code,
            "result_sha256": sha(result_bytes),
            "stdout_sha256": sha(actual_stdout),
            "stderr_sha256": sha(actual_stderr),
            "equals_saved_files": False,
        })
    else:
        raise RuntimeError("C11 固定点预演三轮仍未收敛")

    for index in range(1, 4):
        command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_HASH), "--repo", str(ROOT),
                   "--commit", HEAD_EXPECTED, "--paths", scratch_manifest_rel, "--mode", "strict", "--json"]
        proc = run(command)
        if proc.returncode != 0:
            raise RuntimeError(f"strict hash 固定点预演第 {index} 轮失败，exit={proc.returncode}")
        target = evidence / "hash_basis_check.json"
        if target.read_bytes() == proc.stdout:
            hash_iterations.append({
                "iteration": index,
                "command": command_text(command),
                "exit_code": proc.returncode,
                "stdout_sha256": sha(proc.stdout),
                "equals_saved_file": True,
                "entries_checked": json.loads(proc.stdout.decode("utf-8"))["entries_checked"],
            })
            break
        target.write_bytes(proc.stdout)
        for entry in preflight_manifest["files"]:
            if entry["path"] == target.relative_to(ROOT).as_posix():
                entry["sha256"] = sha_file(target)
        write_json(scratch_manifest, preflight_manifest)
        hash_iterations.append({
            "iteration": index,
            "command": command_text(command),
            "exit_code": proc.returncode,
            "stdout_sha256": sha(proc.stdout),
            "equals_saved_file": False,
            "entries_checked": json.loads(proc.stdout.decode("utf-8"))["entries_checked"],
        })
    else:
        raise RuntimeError("strict hash 固定点预演三轮仍未收敛")

    scratch_result = json.loads((evidence / "selfcheck_result.json").read_text(encoding="utf-8"))
    scratch_hash = json.loads((evidence / "hash_basis_check.json").read_text(encoding="utf-8"))
    if scratch_result.get("status") != "ALL_PASS" or scratch_hash.get("verdict") != "OK":
        raise RuntimeError("隔离固定点预演输出状态不是 PASS")
    return {
        "status": "PASS",
        "scratch_root": str(scratch),
        "scratch_manifest": str(scratch_manifest),
        "selfcheck_status": scratch_result.get("status"),
        "selfcheck_c11": next(item for item in scratch_result["checks"] if item["id"] == "C11"),
        "hash_entries_checked": scratch_hash.get("entries_checked"),
        "hash_mismatched": scratch_hash.get("mismatched"),
        "selfcheck_iterations": c11_iterations,
        "hash_iterations": hash_iterations,
        "scratch_manifest_sha256": sha_file(scratch_manifest),
        "scratch_selfcheck_sha256": sha_file(evidence / "selfcheck_result.json"),
        "scratch_selfcheck_stdout_sha256": sha_file(evidence / "selfcheck_stdout.txt"),
        "scratch_hash_stdout_sha256": sha_file(evidence / "hash_basis_check.json"),
    }


def prepare_run() -> list[dict[str, object]]:
    actual_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, check=True).stdout.decode().strip()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, check=True).stdout.decode().strip()
    if actual_head != HEAD_EXPECTED or branch != "stage6-interact-prep":
        raise RuntimeError(f"w6 基线已变：{actual_head} {branch}")
    if MANIFEST.exists():
        raise RuntimeError(f"拒绝复用既有 r03：{MANIFEST}")
    r01 = ROOT / R01
    for name in ("delivery_manifest.json", "hash_basis_check.json", "selfcheck_result.json", "decision_receipt.json", "task_owned_delta.patch", "pre_task_hash_verification.json"):
        if not (r01 / name).is_file():
            raise FileNotFoundError(f"r01 输入缺失：{r01 / name}")

    copy_map = {
        f"{R01}/delivery_manifest.json": "inputs/r01_delivery_manifest.json",
        f"{R01}/hash_basis_check.json": "inputs/r01_hash_basis_check.json",
        f"{R01}/selfcheck_result.json": "inputs/r01_selfcheck_result.json",
        f"{R01}/decision_receipt.json": "inputs/r01_decision_receipt.json",
        f"{R01}/task_owned_delta.patch": "inputs/r01_task_owned_delta.patch",
        f"{R01}/pre_task_hash_verification.json": "inputs/r01_pre_task_hash_verification.json",
        f"{R01}/inputs/s4_contract_r07.json": "inputs/s4_contract_r07.json",
        f"{R01}/inputs/s6a_cases_r17.json": "inputs/s6a_cases_r17.json",
        f"{R01}/inputs/s6a_upstream_r17.json": "inputs/s6a_upstream_r17.json",
        f"{R01}/inputs/pre_task_snapshot/S6A_stage6_g0_behavior_spec_v1.md": "inputs/pre_task_snapshot/S6A_stage6_g0_behavior_spec_v1.md",
        f"{R01}/inputs/pre_task_snapshot/s6a_stage6_g0_behavior_v1.json": "inputs/pre_task_snapshot/s6a_stage6_g0_behavior_v1.json",
        f"{R01}/inputs/pre_task_snapshot/test_s6b_core_regressions.py": "inputs/pre_task_snapshot/test_s6b_core_regressions.py",
        BEHAVIOR_DOC: "inputs/final_source_snapshot/S6A_stage6_g0_behavior_spec_v1.md",
        BEHAVIOR_JSON: "inputs/final_source_snapshot/s6a_stage6_g0_behavior_v1.json",
        "verification/test_s6b_core_regressions.py": "inputs/final_source_snapshot/test_s6b_core_regressions.py",
        "src/stage6/s6_core.py": "inputs/final_source_snapshot/s6_core.py",
        "verification/s6_g0_selfcheck.py": "inputs/final_source_snapshot/s6_g0_selfcheck.py",
    }
    for rel, dest in copy_map.items():
        copy_item(ROOT / rel, RUN / dest)
    prior_manifest = json.loads((ROOT / f"{R02}/delivery_manifest.json").read_text(encoding="utf-8"))
    prior_hashes = {item["path"]: item["sha256"] for item in prior_manifest["files"]}
    current_paths = [BEHAVIOR_DOC, BEHAVIOR_JSON, "verification/test_s6b_core_regressions.py"]
    source_hashes = {
        rel: {
            "r02_sha256": prior_hashes[rel],
            "r03_start_sha256": sha_file(ROOT / rel),
            "r02_equals_r03_start": prior_hashes[rel] == sha_file(ROOT / rel),
        }
        for rel in current_paths
    }
    write_json(RUN / "inputs" / "r02_to_r03_source_hashes.json", {
        "source_commit": HEAD_EXPECTED,
        "capture_point": "r03 封包脚本开始复制最终源码快照前",
        "hash_basis": "worktree_disk",
        "files": source_hashes,
        "scope_note": "明确列出 r02 已绑定版本与 r03 当前快照；r03 不修改规格、JSON 或测试源码。",
    })
    write_json(RUN / "inputs" / "prior_r02_review_context.json", {
        "source": "阶段6总控向本轮执行者的任务交接",
        "prior_run": f"{R02}",
        "prior_packaging_review": "C11/hash 固定点通过；唯一 CHANGES_REQUIRED 是 MD §13 对 0xFFFFFFFE 阈值仍呈冻结语义。",
        "r03_scope": "当前 MD 将旧阈值改列待裁决、非冻结；绑定 r03 最终快照并重跑验证。独立审查仍待阶段6总控执行。",
        "not_an_independent_review_artifact": True,
    })

    # 保存 S4 r07 与校验工具来源副本，便于离线复核。
    copy_item(ROOT / S4_CONTRACT, RUN / "inputs" / "s4_contract_r07_source.json")
    (RUN / "inputs" / "main_check_manifest_hash_basis.py").write_bytes(MAIN_HASH.read_bytes())
    (RUN / "inputs" / "main_check_stage_delivery.py").write_bytes(MAIN_DELIVERY.read_bytes())

    preflight_result = preflight_fixed_point()
    (RUN / "preflight").mkdir(exist_ok=True)
    scratch = Path(preflight_result["scratch_root"])
    scratch_evidence = scratch / "evidence"
    for source, destination in (
        (scratch / "delivery_manifest.json", RUN / "preflight" / "scratch_manifest.json"),
        (scratch_evidence / "selfcheck_result.json", RUN / "preflight" / "scratch_selfcheck_result.json"),
        (scratch_evidence / "selfcheck_stdout.txt", RUN / "preflight" / "scratch_selfcheck_stdout.txt"),
        (scratch_evidence / "selfcheck_stderr.txt", RUN / "preflight" / "scratch_selfcheck_stderr.txt"),
        (scratch_evidence / "hash_basis_check.json", RUN / "preflight" / "scratch_hash_basis_stdout.json"),
    ):
        copy_item(source, destination)
    write_json(RUN / "preflight" / "fixed_point_preflight.json", preflight_result)

    context = {
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "branch": branch,
        "worktree": str(ROOT),
        "repair_scope": "最终 B25 规格快照绑定、33项回归与 r02 C11/hash 固定点复验",
        "source_spec_test_unchanged_by_r03": True,
        "source_hashes_at_start": source_hashes,
        "hardware_used": False,
        "vivado_used": False,
        "g3_status": "NOT_RUN",
        "fffe_threshold": "UNDECIDED",
        "r01_preserved": True,
        "preflight_fixed_point": "PASS",
    }
    write_json(RUN / "run_context.json", context)

    tests: list[dict[str, object]] = []
    for name, command, output_name, code_name in (
        ("B25 定向回绕回归", TEST_DIRECTED, "test_output.txt", "test_exit_code.txt"),
        ("S6-B 核心回归全套", TEST_FULL, "regression_full_output.txt", "regression_full_exit_code.txt"),
    ):
        proc = run(command)
        (RUN / output_name).write_bytes(proc.stdout)
        (RUN / code_name).write_text(f"{proc.returncode}\n", encoding="utf-8", newline="\n")
        tests.append(check_command(name, command, proc.returncode,
                                   None if proc.returncode == 0 else "回归失败；完整输出保留。"))
        if proc.returncode != 0:
            raise RuntimeError(f"离线回归失败：{name} exit={proc.returncode}")

    # 所有最终检查输出文件预先建位，使 C11 与交付检查的文件计数稳定。
    for name in ("selfcheck_result.json", "hash_basis_check.json", "inputs_check.json", "evidence_check.json"):
        write_json(RUN / name, {"pending": True})
    for name in ("selfcheck_stdout.txt", "selfcheck_stderr.txt"):
        (RUN / name).write_bytes(b"")
    write_json(RUN / "fixed_point_iterations.json", {"status": "PENDING"})

    temp_root = ROOT / "tmp/stage6/S6-A/s6a_b25_decision_20261030_r03_final_checks"
    if temp_root.exists():
        raise FileExistsError(f"最终校验临时目录已存在，不覆盖：{temp_root}")
    temp_root.mkdir(parents=True)

    c11_command = [
        str(PYTHON), "-B", "-X", "utf8", str(SELF_CHECK),
        "--json", BEHAVIOR_JSON, "--doc", BEHAVIOR_DOC, "--cases", CASES, "--upstream", UPSTREAM,
        "--out", str(temp_root / "selfcheck_result.json"), "--project-root", str(ROOT),
        "--evidence-dir", RUN_REL, "--manifest", MANIFEST_REL, "--state", ".codex/STATE.md",
    ]
    hash_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_HASH), "--repo", str(ROOT),
                    "--commit", actual_head, "--paths", MANIFEST_REL, "--mode", "strict", "--json"]
    inputs_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_DELIVERY), "--mode", "inputs",
                      "--manifest", MANIFEST_REL, "--project-root", str(ROOT)]
    evidence_command = [str(PYTHON), "-B", "-X", "utf8", str(MAIN_DELIVERY), "--mode", "evidence",
                        "--manifest", MANIFEST_REL, "--project-root", str(ROOT)]

    check_names = ["S6-A 完整自检含 C11", "S6-A C11 最终 fixed-point 复核", "严格 hash_basis", "严格 hash_basis 最终 fixed-point 复核",
                   "主目录 inputs 检查", "主目录 inputs 最终复核", "主目录 evidence 检查", "主目录 evidence 最终复核"]
    checks = [*tests]
    checks.extend({"name": name, "status": "PASS", "command": command_text(command), "exit_code": 0, "reason": None}
                   for name, command in zip(check_names, [c11_command, c11_command, hash_command, hash_command,
                                                          inputs_command, inputs_command, evidence_command, evidence_command]))
    write_manifest(checks)

    iterations: dict[str, list[dict[str, object]]] = {"c11": [], "hash_basis": [], "inputs": [], "evidence": []}

    def run_c11_iteration(index: int) -> tuple[bytes, bytes, bytes, int, list[str]]:
        command = c11_command
        output = temp_root / "selfcheck_result.json"
        if output.exists():
            output.unlink()
        code, _, result_bytes, out, err = run_c11(output, RUN_REL, MANIFEST_REL)
        return result_bytes, out, err, code, command

    def fixed_file(name: str, runner, comparison: str) -> tuple[int, list[str]]:
        path = RUN / name
        command_last: list[str] = []
        for index in range(1, 5):
            observed = runner(index)
            if comparison == "c11":
                result_bytes, stdout_bytes, stderr_bytes, code, command = observed
                if code != 0 or not result_bytes:
                    path.write_bytes(result_bytes or b"{}\n")
                    (RUN / "selfcheck_stdout.txt").write_bytes(stdout_bytes)
                    (RUN / "selfcheck_stderr.txt").write_bytes(stderr_bytes)
                    write_manifest(checks)
                    raise RuntimeError(f"C11 最终封包失败，exit={code}")
                current_stdout = (RUN / "selfcheck_stdout.txt").read_bytes()
                current_stderr = (RUN / "selfcheck_stderr.txt").read_bytes()
                equal = path.read_bytes() == result_bytes and current_stdout == stdout_bytes and current_stderr == stderr_bytes
                if not equal:
                    path.write_bytes(result_bytes)
                    (RUN / "selfcheck_stdout.txt").write_bytes(stdout_bytes)
                    (RUN / "selfcheck_stderr.txt").write_bytes(stderr_bytes)
                    write_manifest(checks)
                iterations["c11"].append({"iteration": index, "exit_code": code, "result_sha256": sha(result_bytes),
                                           "stdout_sha256": sha(stdout_bytes), "stderr_sha256": sha(stderr_bytes),
                                           "equals_saved_files": equal, "command": command_text(command)})
                command_last = command
                if equal:
                    return code, command_last
            else:
                code, command, stdout_bytes = observed
                if code != 0:
                    path.write_bytes(stdout_bytes)
                    write_manifest(checks)
                    raise RuntimeError(f"{comparison} 最终封包失败，exit={code}")
                equal = path.read_bytes() == stdout_bytes
                if not equal:
                    path.write_bytes(stdout_bytes)
                    write_manifest(checks)
                iterations[comparison].append({"iteration": index, "exit_code": code, "stdout_sha256": sha(stdout_bytes),
                                                "equals_saved_file": equal, "command": command_text(command)})
                command_last = command
                if equal:
                    return code, command_last
        raise RuntimeError(f"{comparison} 四轮未收敛，停止封包")

    def run_hash(index: int):
        proc = run(hash_command)
        return proc.returncode, hash_command, proc.stdout

    def run_delivery(command: list[str]):
        proc = run(command)
        return proc.returncode, command, proc.stdout

    # 先以占位输出跑真实检查，循环至保存字节与当前命令 stdout 完全相同。
    c11_code, c11_command_final = fixed_file("selfcheck_result.json", run_c11_iteration, "c11")
    update_check(checks, check_names[0], c11_command_final, c11_code)
    update_check(checks, check_names[1], c11_command_final, c11_code)
    write_manifest(checks)

    hash_code, hash_command_final = fixed_file("hash_basis_check.json", run_hash, "hash_basis")
    update_check(checks, check_names[2], hash_command_final, hash_code)
    update_check(checks, check_names[3], hash_command_final, hash_code)
    write_manifest(checks)

    inputs_code, inputs_command_final = fixed_file("inputs_check.json", lambda _i: run_delivery(inputs_command), "inputs")
    update_check(checks, check_names[4], inputs_command_final, inputs_code)
    update_check(checks, check_names[5], inputs_command_final, inputs_code)
    write_manifest(checks)

    evidence_code, evidence_command_final = fixed_file("evidence_check.json", lambda _i: run_delivery(evidence_command), "evidence")
    update_check(checks, check_names[6], evidence_command_final, evidence_code)
    update_check(checks, check_names[7], evidence_command_final, evidence_code)
    write_manifest(checks)

    # 把每一轮观测写入既有日志文件，不增加文件路径或改变输出计数。
    iterations["preflight"] = json.loads((RUN / "preflight" / "fixed_point_preflight.json").read_text(encoding="utf-8"))
    write_json(RUN / "fixed_point_iterations.json", iterations)
    write_manifest(checks)

    # 按 r08 的封口方式：固定清单后再跑最终检查，并逐字节比较已保存 stdout/JSON。
    final_manifest_bytes = MANIFEST.read_bytes()
    final_c11_result, final_c11_stdout, final_c11_stderr, final_c11_code, final_c11_command = run_c11_iteration(99)
    final_hash_code, final_hash_command, final_hash_stdout = run_hash(99)
    final_inputs_code, final_inputs_command, final_inputs_stdout = run_delivery(inputs_command)
    final_evidence_code, final_evidence_command, final_evidence_stdout = run_delivery(evidence_command)
    final_observations = [final_c11_code, final_hash_code, final_inputs_code, final_evidence_code]
    final_output_bytes = {
        "selfcheck_result.json": final_c11_result,
        "selfcheck_stdout.txt": final_c11_stdout,
        "selfcheck_stderr.txt": final_c11_stderr,
        "hash_basis_check.json": final_hash_stdout,
        "inputs_check.json": final_inputs_stdout,
        "evidence_check.json": final_evidence_stdout,
    }
    stdout_hash_checks = {
        name: (RUN / name).read_bytes() == observed
        for name, observed in final_output_bytes.items()
    }
    if any(code != 0 for code in final_observations) or not all(stdout_hash_checks.values()):
        failure_dir = temp_root / "final_recheck_observed"
        failure_dir.mkdir(exist_ok=True)
        for name, observed in final_output_bytes.items():
            (failure_dir / name).write_bytes(observed)
        failure = {
            "status": "FAIL",
            "exit_codes": final_observations,
            "output_matches_saved_files": stdout_hash_checks,
            "commands": [command_text(final_c11_command), command_text(final_hash_command),
                         command_text(final_inputs_command), command_text(final_evidence_command)],
            "observed_output_sha256": {name: sha(data) for name, data in final_output_bytes.items()},
            "preserved_under": str(failure_dir),
        }
        write_json(temp_root / "final_recheck_failure.json", failure)
        raise RuntimeError(f"最终清单复核或 stdout 绑定失败；观测保存在 {failure_dir}")
    if MANIFEST.read_bytes() != final_manifest_bytes:
        raise RuntimeError("最终 checker 复核期间 delivery_manifest.json 意外改变")

    manifest_data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selfcheck = json.loads((RUN / "selfcheck_result.json").read_text(encoding="utf-8"))
    hash_result = json.loads((RUN / "hash_basis_check.json").read_text(encoding="utf-8"))
    inputs_result = json.loads((RUN / "inputs_check.json").read_text(encoding="utf-8"))
    evidence_result = json.loads((RUN / "evidence_check.json").read_text(encoding="utf-8"))
    internal_files = sum(1 for item in manifest_data["files"] if item["path"].startswith(RUN_REL + "/"))
    external_files = len(manifest_data["files"]) - internal_files
    c11 = next(item for item in selfcheck["checks"] if item["id"] == "C11")
    actual_count = sum(1 for path in RUN.rglob("*") if path.is_file())
    if selfcheck.get("status") != "ALL_PASS" or c11.get("status") != "PASS":
        raise RuntimeError("最终 selfcheck/C11 未 PASS")
    if f"实际文件 {actual_count} 个" not in c11.get("detail", ""):
        raise RuntimeError(f"C11 文件数与最终目录不一致：actual={actual_count}; {c11.get('detail')}")
    if f"运行目录 {internal_files} 个文件 + 外部绑定 {external_files} 个文件哈希复算通过" not in c11.get("detail", ""):
        raise RuntimeError(f"C11 manifest 数量与最终清单不一致：{c11.get('detail')}")
    if hash_result.get("verdict") != "OK" or hash_result.get("entries_checked") != len(manifest_data["files"]) or hash_result.get("mismatched") != 0:
        raise RuntimeError("最终 strict hash_basis 结果/条目数与 manifest 不一致")
    if inputs_result.get("status") != "CHECKS_OK" or evidence_result.get("status") != "CHECKS_OK":
        raise RuntimeError("最终 inputs/evidence 检查未 CHECKS_OK")
    print(json.dumps({
        "run_id": RUN_ID,
        "source_commit": actual_head,
        "selfcheck_status": selfcheck["status"],
        "c11_status": c11["status"],
        "c11_actual_files": actual_count,
        "c11_manifest_run_files": internal_files,
        "c11_manifest_external_files": external_files,
        "strict_hash_entries_checked": hash_result["entries_checked"],
        "strict_hash_mismatched": hash_result["mismatched"],
        "inputs_status": inputs_result["status"],
        "evidence_status": evidence_result["status"],
        "all_final_exit_codes": final_observations,
        "stdout_bindings": stdout_hash_checks,
        "manifest_sha256": sha_file(MANIFEST),
        "manifest_file_count": len(manifest_data["files"]),
        "hardware": "NOT_RUN",
        "fffe_threshold": "UNDECIDED",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(prepare_run())
    except Exception as exc:
        print(f"r03 封包失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
