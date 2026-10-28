from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone


ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
RUN_ID = "s6a_u6_02_recovery_20261029_r04"
RUN_DIR = ROOT / "report/evidence/S6-A" / RUN_ID
BASE_COMMIT = "86a2bb18e1a197dc56d07ea8c42ec38a6adf3ed1"
UTC8 = timezone(timedelta(hours=8))
CHECK_STAGE = RUN_DIR / "inputs/tool_sources/check_stage_delivery.py"
CHECK_HASH = RUN_DIR / "inputs/tool_sources/check_manifest_hash_basis.py"
INPUT_MANIFEST = f"report/evidence/S6-A/{RUN_ID}/inputs_manifest.json"
BINDINGS_MANIFEST = f"report/evidence/S6-A/{RUN_ID}/source_bindings.json"
DELIVERY_MANIFEST = f"report/evidence/S6-A/{RUN_ID}/delivery_manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(ROOT), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} 退出 {result.returncode}: "
            f"{result.stderr.decode('utf-8', 'replace')}"
        )
    return result.stdout.decode("utf-8", "replace").strip()


def write_json(path: pathlib.Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def command_display(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def run_command(command: list[str]) -> tuple[int, bytes, bytes]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def manifest_file_entries() -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    manifest_path = RUN_DIR / "delivery_manifest.json"
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise RuntimeError(f"证据目录不接受符号链接：{path}")
        if path.resolve() == manifest_path.resolve():
            continue
        relative = path.relative_to(ROOT).as_posix()
        in_project = "inputs/project/" in relative
        if in_project or relative.endswith("inputs_manifest.json") or relative.endswith("source_bindings.json"):
            role = "input"
        elif relative.endswith(".py"):
            role = "source"
        elif relative.endswith(".txt"):
            role = "log"
        else:
            role = "result"
        entries.append({
            "path": relative,
            "sha256": sha256_file(path),
            "role": role,
            "keep_reason": f"本次 S6-A r07 恢复闭环的可复核文件：{path.relative_to(RUN_DIR).as_posix()}。",
            "hash_basis": "worktree_disk",
        })
    return entries


def check_entry(
    name: str,
    command: list[str],
    exit_code: int | None,
    reason: str | None = None,
) -> dict[str, object]:
    if exit_code is None:
        return {
            "name": name,
            "status": "NOT_RUN",
            "command": command_display(command),
            "exit_code": None,
            "reason": reason or "该门禁尚未运行。",
        }
    if exit_code == 0:
        return {
            "name": name,
            "status": "PASS",
            "command": command_display(command),
            "exit_code": 0,
        }
    return {
        "name": name,
        "status": "FAIL",
        "command": command_display(command),
        "exit_code": exit_code,
        "reason": reason or f"命令真实退出码为 {exit_code}。",
    }


def check_output_entry(
    name: str,
    command: list[str],
    exit_code: int,
    payload: dict[str, object],
    expected_field: str,
    expected_value: str,
) -> dict[str, object]:
    if exit_code == 0 and payload.get(expected_field) == expected_value:
        return check_entry(name, command, 0)
    if exit_code != 0:
        return check_entry(name, command, exit_code, f"命令返回非零退出码 {exit_code}。")
    return {
        "name": name,
        "status": "BLOCKED",
        "command": command_display(command),
        "exit_code": None,
        "reason": f"进程退出码为 0，但 stdout 的 {expected_field} 不等于 {expected_value}；结论不一致。",
    }


def read_json(path: pathlib.Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON 顶层不是对象：{path}")
    return value


def build_delivery_manifest(checks: list[dict[str, object]]) -> None:
    execution = read_json(RUN_DIR / "clean_export_execution.json")
    tool_provenance = read_json(RUN_DIR / "tool_source_provenance.json")
    basis_note = "所有 files 哈希按当前工作区磁盘字节计算；未提交快照不声明为 commit_blob。"
    manifest = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": BASE_COMMIT,
        "evidence_dir": f"report/evidence/S6-A/{RUN_ID}",
        "hash_basis": "worktree_disk",
        "hash_basis_note": basis_note,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本次交付仅恢复 S6-A 已批准语义、当前规格与 C11 声明的离线文件，不消费阶段4/5接口。",
        "files": manifest_file_entries(),
        "checks": checks,
        "limitations": [
            "恢复自检仅适用于指定提交与 inputs_manifest/source_bindings 中列明的磁盘字节。",
            "结果不代表独立复核、阶段4/5真实集成、板级 G3、G4 或 G5。",
            "T6-A03 实测帧周期与阶段6实物验收未由本次离线恢复执行。",
        ],
        "tool_versions": {
            "python": f"CPython {platform.python_version()}",
            "git": git_text("--version"),
            "check_stage_delivery_sha256": next(
                item["origin_disk_sha256"] for item in tool_provenance["files"]
                if item.get("origin_path") == "verification/check_stage_delivery.py"
            ),
            "check_manifest_hash_basis_sha256": next(
                item["origin_disk_sha256"] for item in tool_provenance["files"]
                if item.get("origin_path") == "verification/check_manifest_hash_basis.py"
            ),
            "main_tool_source_commit": "11044e5fb815f9f8570ee0b7332b113d9f924460",
        },
    }
    write_json(RUN_DIR / "delivery_manifest.json", manifest)


def main() -> int:
    if not RUN_DIR.is_dir():
        raise RuntimeError("r04 RunId 目录不存在")
    if git_text("rev-parse", "HEAD") != BASE_COMMIT:
        raise RuntimeError("w6 HEAD 已变化；拒绝封装")
    if not CHECK_STAGE.is_file() or not CHECK_HASH.is_file():
        raise RuntimeError("固定版本门禁源码缺失")
    execution = read_json(RUN_DIR / "clean_export_execution.json")
    receipt_command = [
        sys.executable, "-B", "-X", "utf8",
        str(RUN_DIR / "verify_approved_receipt.py"),
    ]
    receipt_rc, receipt_out, receipt_err = run_command(receipt_command)
    (RUN_DIR / "results/receipt_verification_stdout.json").write_bytes(receipt_out)
    (RUN_DIR / "results/receipt_verification_stderr.txt").write_bytes(receipt_err)
    receipt_payload = read_json(RUN_DIR / "results/approved_receipt_verification.json")
    recovery_command = [
        sys.executable, "-B", "-X", "utf8",
        str(RUN_DIR / "recover_clean_checkout.py"),
    ]
    input_check_command = [
        sys.executable, "-B", "-X", "utf8", str(CHECK_STAGE),
        "--mode", "inputs", "--manifest", INPUT_MANIFEST, "--project-root", str(ROOT),
    ]
    inputs_rc, inputs_out, inputs_err = run_command(input_check_command)
    (RUN_DIR / "results/inputs_check_stdout.json").write_bytes(inputs_out)
    (RUN_DIR / "results/inputs_check_stderr.txt").write_bytes(inputs_err)
    inputs_payload = json.loads(inputs_out.decode("utf-8")) if inputs_out else {}

    basis_input_command = [
        sys.executable, "-B", "-X", "utf8", str(CHECK_HASH),
        "--repo", str(ROOT),
        "--paths", INPUT_MANIFEST,
        "--paths", BINDINGS_MANIFEST,
        "--paths", f"report/evidence/S6-A/{RUN_ID}/tool_source_provenance.json",
        "--mode", "strict",
        "--json",
    ]
    basis_input_rc, basis_input_out, basis_input_err = run_command(basis_input_command)
    (RUN_DIR / "results/hash_basis_inputs_stdout.json").write_bytes(basis_input_out)
    (RUN_DIR / "results/hash_basis_inputs_stderr.txt").write_bytes(basis_input_err)
    basis_input_payload = json.loads(basis_input_out.decode("utf-8")) if basis_input_out else {}

    evidence_stdout_path = RUN_DIR / "results/evidence_check_stdout.json"
    evidence_stderr_path = RUN_DIR / "results/evidence_check_stderr.txt"
    hash_stdout_path = RUN_DIR / "results/hash_basis_strict_stdout.json"
    hash_stderr_path = RUN_DIR / "results/hash_basis_strict_stderr.txt"
    for path in (evidence_stdout_path, evidence_stderr_path, hash_stdout_path, hash_stderr_path):
        if path.exists() or path.is_symlink():
            raise RuntimeError(f"预期为空的最终门禁结果路径已存在：{path}")
        path.write_bytes(b"")

    evidence_command = [
        sys.executable, "-B", "-X", "utf8", str(CHECK_STAGE),
        "--mode", "evidence", "--manifest", DELIVERY_MANIFEST, "--project-root", str(ROOT),
    ]
    basis_all_command = [
        sys.executable, "-B", "-X", "utf8", str(CHECK_HASH),
        "--repo", str(ROOT),
        "--paths", INPUT_MANIFEST,
        "--paths", BINDINGS_MANIFEST,
        "--paths", f"report/evidence/S6-A/{RUN_ID}/tool_source_provenance.json",
        "--paths", DELIVERY_MANIFEST,
        "--mode", "strict",
        "--json",
    ]

    selfcheck_record = next(
        (item for item in execution.get("commands", [])
         if any("s6_g0_selfcheck.py" in str(arg) for arg in item.get("command", []))),
        None,
    )
    checks = [
        check_output_entry(
            "u6_02_r07_receipt_semantics_exact",
            receipt_command,
            receipt_rc,
            receipt_payload,
            "status",
            "PASS",
        ),
        check_entry(
            "clean_git_clone_s6a_selfcheck",
            [str(arg) for arg in selfcheck_record["command"]] if selfcheck_record else recovery_command,
            int(selfcheck_record["exit_code"]) if selfcheck_record else None,
            "在固定提交的临时 Git 克隆中运行 S6-A 自检（含 C11/C17）。"
            if not selfcheck_record else None,
        ) if selfcheck_record else {
            "name": "clean_git_clone_s6a_selfcheck",
            "status": "NOT_RUN",
            "command": command_display(recovery_command),
            "exit_code": None,
            "reason": "隔离恢复在启动正式自检前受阻；查看 clean_export_execution.json。",
        },
        check_output_entry(
            "check_stage_delivery_inputs",
            input_check_command,
            inputs_rc,
            inputs_payload,
            "status",
            "CHECKS_OK",
        ),
        check_output_entry(
            "hash_basis_inputs_and_source_bindings_strict",
            basis_input_command,
            basis_input_rc,
            basis_input_payload,
            "verdict",
            "OK",
        ),
        check_entry(
            "check_stage_delivery_evidence",
            evidence_command,
            None,
            "待生成包含本 RunId 全部文件哈希的证据清单后核验。",
        ),
        check_entry(
            "hash_basis_all_manifests_strict",
            basis_all_command,
            None,
            "待证据清单及门禁输出全部落盘后核验。",
        ),
    ]
    evidence_check_index = 4
    hash_basis_check_index = 5
    prerequisite_checks_pass = all(
        item["status"] == "PASS" for item in checks[:4]
    )
    overall_exit = 1
    last_evidence_output = b""
    last_hash_output = b""
    failure: str | None = None
    try:
        # 两个 stdout 都是证据文件；交替执行直到状态、日志内容和文件哈希稳定。
        for _ in range(8):
            build_delivery_manifest(checks)
            prior_evidence = evidence_stdout_path.read_bytes()
            evidence_rc, evidence_out, evidence_err = run_command(evidence_command)
            evidence_stdout_path.write_bytes(evidence_out)
            evidence_stderr_path.write_bytes(evidence_err)
            evidence_payload = json.loads(evidence_out.decode("utf-8")) if evidence_out else {}
            checks[evidence_check_index] = check_output_entry(
                "check_stage_delivery_evidence",
                evidence_command,
                evidence_rc,
                evidence_payload,
                "status",
                "CHECKS_OK",
            )

            build_delivery_manifest(checks)
            prior_hash = hash_stdout_path.read_bytes()
            hash_rc, hash_out, hash_err = run_command(basis_all_command)
            hash_stdout_path.write_bytes(hash_out)
            hash_stderr_path.write_bytes(hash_err)
            hash_payload = json.loads(hash_out.decode("utf-8")) if hash_out else {}
            checks[hash_basis_check_index] = check_output_entry(
                "hash_basis_all_manifests_strict",
                basis_all_command,
                hash_rc,
                hash_payload,
                "verdict",
                "OK",
            )
            last_evidence_output = evidence_out
            last_hash_output = hash_out
            if (
                prerequisite_checks_pass
                and
                evidence_rc == 0
                and evidence_payload.get("status") == "CHECKS_OK"
                and hash_rc == 0
                and hash_payload.get("verdict") == "OK"
                and prior_evidence == evidence_out
                and prior_hash == hash_out
            ):
                overall_exit = 0
                break
        if overall_exit != 0:
            failure = "evidence 与 strict 哈希基座门禁未达到互相一致的稳定状态。"
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        # 确保失败时也把已发生的门禁状态和真实退出码留在唯一 RunId 中。
        build_delivery_manifest(checks)

    if overall_exit == 0:
        # 只读复跑最终已封装文件，避免更新任一日志。
        final_evidence_rc, final_evidence_out, _ = run_command(evidence_command)
        final_hash_rc, final_hash_out, _ = run_command(basis_all_command)
        if (
            final_evidence_rc != 0
            or final_evidence_out != last_evidence_output
            or final_hash_rc != 0
            or final_hash_out != last_hash_output
        ):
            overall_exit = 1
            failure = "最终只读复核与已封存 stdout 不一致。"
    print(json.dumps({
        "status": "EVIDENCE_CHECKS_OK" if overall_exit == 0 else "EVIDENCE_CHECKS_FAILED",
        "run_id": RUN_ID,
        "inputs_check_exit_code": inputs_rc,
        "hash_basis_inputs_exit_code": basis_input_rc,
        "evidence_check_exit_code": checks[evidence_check_index].get("exit_code"),
        "hash_basis_strict_exit_code": checks[hash_basis_check_index].get("exit_code"),
        "failure": failure,
        "evidence_stdout_sha256": sha256_bytes(last_evidence_output),
        "hash_basis_stdout_sha256": sha256_bytes(last_hash_output),
    }, ensure_ascii=False))
    return overall_exit


if __name__ == "__main__":
    raise SystemExit(main())
