from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone


ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
RUN_ID = "s6a_u6_02_recovery_20261029_r03"
RUN_DIR = ROOT / "report/evidence/S6-A" / RUN_ID
BASE_COMMIT = "86a2bb18e1a197dc56d07ea8c42ec38a6adf3ed1"
UTC8 = timezone(timedelta(hours=8))
RECEIPT_SOURCE = pathlib.PurePosixPath(
    "report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json"
)
R05 = pathlib.PurePosixPath("report/evidence/S6-A/s6a_u6_02_bound_20261027_r05")
OVERWRITE_TRACKED = {
    ".codex/STATE.md",
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
}
EXPECTED_SEMANTICS = [
    "确认并批准 §10 当前定义：在一个获取区间内，无论目标保持多久、冷却是否结束或窗口是否再次满足，恰好产生一次 ACTION_SUBMITTED。",
    "只有以下任一新获取重新满足稳定窗口，且提交时全局冷却门已结束，才允许产生下一次 ACTION_SUBMITTED：(a) 目标丢失确认后重新获取该目标并再次满足 §9 稳定窗口；(b) 切换到另一合法目标并满足 §9 稳定窗口。提交时须满足 t_now − t_last_submit ≥ T6-K01。",
    "目标持续保持、保持期间稳定窗口再次满足或冷却结束本身都不构成新的获取，也不产生重复提交。",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str) -> pathlib.PurePosixPath:
    path = pathlib.PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise RuntimeError(f"不安全的仓库相对路径：{value}")
    return path


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_record(command: list[str], cwd: pathlib.Path) -> tuple[dict[str, object], bytes, bytes]:
    started = datetime.now(UTC8)
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    record = {
        "command": command,
        "command_display": subprocess.list2cmdline(command),
        "cwd": str(cwd),
        "started_utc8": started.strftime("%Y-%m-%d %H:%M:%S%z"),
        "finished_utc8": datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S%z"),
        "exit_code": result.returncode,
        "stdout_sha256": sha256_bytes(result.stdout),
        "stderr_sha256": sha256_bytes(result.stderr),
    }
    return record, result.stdout, result.stderr


def write_json(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_live_inputs() -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    input_manifest_path = RUN_DIR / "inputs_manifest.json"
    bindings_path = RUN_DIR / "source_bindings.json"
    tool_provenance_path = RUN_DIR / "tool_source_provenance.json"
    manifest = json.loads(input_manifest_path.read_text(encoding="utf-8"))
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    tool_provenance = json.loads(tool_provenance_path.read_text(encoding="utf-8"))
    if manifest.get("run_id") != RUN_ID or manifest.get("source_commit") != BASE_COMMIT:
        raise RuntimeError("输入清单身份或 source_commit 不符")
    if bindings.get("run_id") != RUN_ID or bindings.get("source_commit") != BASE_COMMIT:
        raise RuntimeError("source_bindings 身份或 source_commit 不符")
    manifest_files = {
        item["path"]: item for item in manifest.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    bindings_path_rel = f"report/evidence/S6-A/{RUN_ID}/source_bindings.json"
    tool_provenance_rel = f"report/evidence/S6-A/{RUN_ID}/tool_source_provenance.json"
    for rel, path in (
        (bindings_path_rel, bindings_path),
        (tool_provenance_rel, tool_provenance_path),
    ):
        if rel not in manifest_files:
            raise RuntimeError(f"inputs_manifest 未绑定 {rel}")
        if sha256_file(path) != manifest_files[rel]["sha256"]:
            raise RuntimeError(f"{rel} 哈希与 inputs_manifest 不符")

    restored: list[dict[str, object]] = []
    for item in bindings.get("files", []):
        package_rel = safe_relative(item["path"])
        target_rel = safe_relative(item["source_path"])
        package_path = ROOT.joinpath(*package_rel.parts)
        if not package_path.is_file() or package_path.is_symlink():
            raise RuntimeError(f"快照文件缺失或为符号链接：{item['path']}")
        if package_path.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"快照长度与 source_bindings 不符：{item['path']}")
        if sha256_file(package_path) != item["sha256"]:
            raise RuntimeError(f"快照哈希与 source_bindings 不符：{item['path']}")
        declared = manifest_files.get(item["path"])
        if declared is None or declared.get("sha256") != item["sha256"]:
            raise RuntimeError(f"快照没有被 inputs_manifest 同哈希绑定：{item['path']}")

        origin_repo = pathlib.Path(item.get("origin_repo", str(ROOT)))
        original = origin_repo.joinpath(*target_rel.parts)
        if not original.is_file() or sha256_file(original) != item["sha256"]:
            raise RuntimeError(f"原始源文件与快照漂移：{item['source_path']}")
        restored.append({
            "path": item["path"],
            "source_path": item["source_path"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "origin_repo": str(origin_repo),
            "overwrites_tracked_baseline": False,
        })
    if len(restored) != len(bindings.get("files", [])):
        raise RuntimeError("source_bindings 文件计数不一致")

    tool_records: list[dict[str, object]] = []
    for item in tool_provenance.get("files", []):
        package_rel = safe_relative(item["path"])
        package_path = ROOT.joinpath(*package_rel.parts)
        if not package_path.is_file() or package_path.is_symlink():
            raise RuntimeError(f"统一门禁工具快照缺失或为符号链接：{item['path']}")
        if package_path.stat().st_size != item["size_bytes"] or sha256_file(package_path) != item["sha256"]:
            raise RuntimeError(f"统一门禁工具快照哈希/长度不符：{item['path']}")
        declared = manifest_files.get(item["path"])
        if declared is None or declared.get("sha256") != item["sha256"]:
            raise RuntimeError(f"统一门禁工具快照未被 inputs_manifest 绑定：{item['path']}")
        origin_repo = pathlib.Path(item["origin_repo"])
        origin_path = safe_relative(item["origin_path"])
        original = origin_repo.joinpath(*origin_path.parts)
        if not original.is_file() or sha256_file(original) != item["origin_disk_sha256"]:
            raise RuntimeError(f"main 统一门禁工具源文件与固定磁盘 SHA 不符：{item['origin_path']}")
        blob = git(
            origin_repo,
            "rev-parse",
            f"{item['origin_commit']}:{origin_path.as_posix()}",
        )
        if blob.returncode != 0 or blob.stdout.decode("ascii", "replace").strip() != item["origin_git_blob_oid"]:
            raise RuntimeError(f"main 统一门禁工具 Git blob 与固定版本不符：{item['origin_path']}")
        tool_records.append({
            "snapshot_path": item["path"],
            "origin_repo": str(origin_repo),
            "origin_path": origin_path.as_posix(),
            "origin_commit": item["origin_commit"],
            "origin_git_blob_oid": item["origin_git_blob_oid"],
            "origin_disk_sha256": item["origin_disk_sha256"],
            "snapshot_sha256": item["sha256"],
            "restored_into_clean_clone": False,
        })
    return bindings, restored, tool_records


def restore_inputs(project: pathlib.Path, bindings: dict[str, object]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for item in bindings["files"]:
        source_path = safe_relative(item["source_path"])
        snapshot_path = ROOT.joinpath(*safe_relative(item["path"]).parts)
        target = project.joinpath(*source_path.parts)
        try:
            target.resolve().relative_to(project.resolve())
        except ValueError as exc:
            raise RuntimeError(f"恢复目标越出临时 Git 克隆：{source_path}") from exc
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise RuntimeError(f"恢复目标类型不安全：{source_path}")
        overwritten = target.exists()
        baseline_blob_oid = None
        if overwritten:
            rel_text = source_path.as_posix()
            if rel_text not in OVERWRITE_TRACKED:
                raise RuntimeError(f"固定提交中意外已有未跟踪恢复目标：{rel_text}")
            object_type = git(project, "cat-file", "-t", f"{BASE_COMMIT}:{rel_text}")
            if object_type.returncode != 0 or object_type.stdout.strip() != b"blob":
                raise RuntimeError(f"被覆盖基线路径不是固定提交中的 blob：{rel_text}")
            blob = git(project, "rev-parse", f"{BASE_COMMIT}:{rel_text}")
            if blob.returncode != 0:
                raise RuntimeError(f"无法解析被覆盖路径的固定提交 blob：{rel_text}")
            baseline_blob_oid = blob.stdout.decode("ascii", "replace").strip()
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot_path, target)
        if sha256_file(target) != item["sha256"]:
            raise RuntimeError(f"恢复后文件哈希不符：{source_path}")
        records.append({
            "source_path": source_path.as_posix(),
            "snapshot_path": item["path"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "overwrites_tracked_baseline": overwritten,
            "baseline_git_blob_oid": baseline_blob_oid,
        })
    return records


def main() -> int:
    started = datetime.now(UTC8)
    report: dict[str, object] = {
        "schema_version": 1,
        "artifact": "s6a_clean_git_clone_recovery_execution",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "base_commit": BASE_COMMIT,
        "hash_basis": "worktree_disk",
        "hash_basis_note": "本报告中的输出文件 SHA-256 按磁盘字节计算。",
        "source_snapshot_run_id": "s6a_u6_02_recovery_20261029_r01",
        "started_utc8": started.strftime("%Y-%m-%d %H:%M:%S%z"),
        "commands": [],
        "restored_inputs": [],
        "limitations": [
            "仅在固定 S6-A 提交的临时本地 Git 克隆上恢复快照并运行离线自检。",
            "结果不代表独立审查、阶段4/5真实集成、G3板级或G4/G5验收。",
            "临时克隆使用 --shared 只读借用 w6 对象库；不会创建/切换 w6 分支、暂存或提交。",
        ],
    }
    exit_code = 1
    failure: str | None = None
    selfcheck: dict[str, object] | None = None
    receipt_info: dict[str, object] | None = None
    restored: list[dict[str, object]] = []
    try:
        if git(ROOT, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip() != "stage6-interact-prep":
            raise RuntimeError("w6 分支不再是 stage6-interact-prep")
        if git(ROOT, "rev-parse", "HEAD").stdout.decode().strip() != BASE_COMMIT:
            raise RuntimeError("w6 HEAD 不再是固定基线")
        bindings, preflight_records, tool_records = verify_live_inputs()
        report["input_preflight"] = {
            "status": "PASS",
            "file_count": len(preflight_records),
            "files": preflight_records,
        }
        report["tool_source_preflight"] = tool_records

        with tempfile.TemporaryDirectory(prefix="s6a-recovery-r03-") as temp_name:
            temp_root = pathlib.Path(temp_name).resolve()
            project = temp_root / "project"
            clone_record, clone_stdout, clone_stderr = run_record(
                ["git", "clone", "--quiet", "--shared", "--no-checkout", str(ROOT), str(project)],
                ROOT,
            )
            report["commands"].append(clone_record)
            if clone_record["exit_code"] != 0:
                raise RuntimeError(f"临时 Git clone 失败：{clone_stderr.decode('utf-8', 'replace')}")

            for key in ("core.autocrlf", "core.eol"):
                value = git(ROOT, "config", "--get", key)
                if value.returncode == 0 and value.stdout.strip():
                    config_record, _, config_err = run_record(
                        ["git", "-C", str(project), "config", key, value.stdout.decode("utf-8", "replace").strip()],
                        ROOT,
                    )
                    report["commands"].append(config_record)
                    if config_record["exit_code"] != 0:
                        raise RuntimeError(f"镜像 Git 换行配置失败：{config_err.decode('utf-8', 'replace')}")
            checkout_record, _, checkout_err = run_record(
                ["git", "-C", str(project), "checkout", "--quiet", "--detach", BASE_COMMIT],
                ROOT,
            )
            report["commands"].append(checkout_record)
            if checkout_record["exit_code"] != 0:
                raise RuntimeError(f"固定提交检出失败：{checkout_err.decode('utf-8', 'replace')}")
            cloned_head = git(project, "rev-parse", "HEAD")
            if cloned_head.returncode != 0 or cloned_head.stdout.decode().strip() != BASE_COMMIT:
                raise RuntimeError("临时克隆 HEAD 与固定提交不符")
            report["clean_clone"] = {
                "path": str(project),
                "head": cloned_head.stdout.decode().strip(),
                "status_before_restore": git(project, "status", "--short").stdout.decode("utf-8", "replace"),
            }
            restored = restore_inputs(project, bindings)
            report["restored_inputs"] = restored

            receipt_path = project.joinpath(*RECEIPT_SOURCE.parts)
            receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
            exact_semantics = receipt_data.get("approved_semantics") == EXPECTED_SEMANTICS
            receipt_info = {
                "path": RECEIPT_SOURCE.as_posix(),
                "sha256": sha256_file(receipt_path),
                "decision_id": receipt_data.get("decision_id"),
                "decision_status": receipt_data.get("decision_status"),
                "semantics_exact_match": exact_semantics,
            }
            if receipt_info["decision_id"] != "U6-02" or receipt_info["decision_status"] != "APPROVED_20261025":
                raise RuntimeError("恢复后的 U6-02 r07 回执身份/批准状态不符")
            if not exact_semantics:
                raise RuntimeError("恢复后的 U6-02 r07 批准语义不等于用户批准原文")
            report["u6_02_receipt"] = receipt_info

            evidence = project.joinpath(*R05.parts)
            out_rel = pathlib.PurePosixPath("tmp/s6a_recovery_20261029_r03/selfcheck_result.json")
            result_path = project.joinpath(*out_rel.parts)
            if result_path.exists() or result_path.is_symlink():
                raise RuntimeError("隔离克隆自检输出路径意外已存在；拒绝覆盖")
            result_path.parent.mkdir(parents=True, exist_ok=True)
            command = [
                sys.executable,
                "-B",
                "-X",
                "utf8",
                "verification/s6_g0_selfcheck.py",
                "--json",
                "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                "--doc",
                "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
                "--cases",
                str(R05 / "hand_computed_cases.json"),
                "--upstream",
                str(R05 / "upstream_bindings.json"),
                "--project-root",
                ".",
                "--evidence-dir",
                R05.as_posix(),
                "--out",
                out_rel.as_posix(),
                "--manifest",
                str(R05 / "delivery_manifest.json"),
                "--state",
                ".codex/STATE.md",
            ]
            selfcheck_record, stdout, stderr = run_record(command, project)
            report["commands"].append(selfcheck_record)
            if result_path.is_file():
                payload = json.loads(result_path.read_text(encoding="utf-8"))
                selfcheck = {
                    "status": payload.get("status"),
                    "error_count": len(payload.get("errors", [])),
                    "check_count": len(payload.get("checks", [])),
                    "sha256": sha256_file(result_path),
                    "path": str(out_rel),
                }
                shutil.copyfile(result_path, RUN_DIR / "results/clean_export_selfcheck_result.json")
            (RUN_DIR / "results/clean_export_selfcheck_stdout.txt").write_bytes(stdout)
            (RUN_DIR / "results/clean_export_selfcheck_stderr.txt").write_bytes(stderr)
            report["selfcheck"] = selfcheck
            if selfcheck_record["exit_code"] != 0 or not selfcheck or selfcheck.get("status") != "ALL_PASS":
                raise RuntimeError(
                    f"S6-A 离线自检未通过：exit={selfcheck_record['exit_code']}，"
                    f"status={selfcheck.get('status') if selfcheck else 'missing'}"
                )
            exit_code = 0
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        report["failure"] = failure
        exit_code = 1
    finally:
        report["finished_utc8"] = datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S%z")
        report["exit_code"] = exit_code
        report["failure"] = failure
        report["u6_02_receipt"] = receipt_info
        report["selfcheck"] = selfcheck
        report["restored_inputs"] = restored
        write_json(RUN_DIR / "clean_export_execution.json", report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
