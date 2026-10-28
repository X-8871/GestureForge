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
RUN_ID = "s6a_u6_02_recovery_20261029_r01"
BASE_COMMIT = "86a2bb18e1a197dc56d07ea8c42ec38a6adf3ed1"
RUN_DIR = ROOT / "report/evidence/S6-A" / RUN_ID
INPUTS_DIR = RUN_DIR / "inputs/project"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root: pathlib.Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def extract_git_archive(project: pathlib.Path) -> None:
    archive_path = project.parent / "baseline.tar"
    with archive_path.open("wb") as archive_file:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "archive", "--format=tar", BASE_COMMIT],
            stdout=archive_file,
            stderr=subprocess.PIPE,
            check=False,
        )
    if result.returncode != 0:
        raise RuntimeError(f"git archive 退出 {result.returncode}: {result.stderr.decode('utf-8', 'replace')}")
    with tarfile.open(archive_path, "r:") as archive:
        for member in archive.getmembers():
            member_path = pathlib.PurePosixPath(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise RuntimeError(f"归档包含越界路径：{member.name}")
            if not (member.isdir() or member.isfile()):
                raise RuntimeError(f"归档包含非普通文件：{member.name}")
        archive.extractall(project, filter="data")
    archive_path.unlink()


def restore_inputs(project: pathlib.Path) -> list[dict[str, object]]:
    manifest_path = RUN_DIR / "inputs_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored: list[dict[str, object]] = []
    for item in manifest["files"]:
        package_path = RUN_DIR / pathlib.PurePosixPath(item["path"])
        target_rel = pathlib.PurePosixPath(item["source_path"])
        if target_rel.is_absolute() or ".." in target_rel.parts:
            raise RuntimeError(f"输入恢复路径越界：{target_rel}")
        target = project.joinpath(*target_rel.parts)
        data_hash = sha256(package_path)
        if data_hash != item["sha256"]:
            raise RuntimeError(f"输入快照哈希不符：{item['path']}")
        if package_path.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"输入快照长度不符：{item['path']}")
        if package_path.is_dir():
            if target.exists():
                raise RuntimeError(f"干净导出中意外已存在历史路径：{target_rel}")
            shutil.copytree(package_path, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(package_path, target)
        restored.append({
            "source_path": str(target_rel),
            "snapshot_path": item["path"],
            "sha256": data_hash,
            "size_bytes": package_path.stat().st_size,
        })
    return restored


def main() -> int:
    if not RUN_DIR.is_dir() or not (RUN_DIR / "inputs_manifest.json").is_file():
        raise RuntimeError("新 RunId 输入包不完整")
    live_head = git(ROOT, "rev-parse", "HEAD")
    if live_head.returncode != 0 or live_head.stdout.decode().strip() != BASE_COMMIT:
        raise RuntimeError("w6 基线已变化；拒绝使用不同提交构建")
    with tempfile.TemporaryDirectory(prefix="s6a-recovery-") as temp_name:
        temp_root = pathlib.Path(temp_name).resolve()
        project = temp_root / "project"
        project.mkdir()
        extract_git_archive(project)
        restored = restore_inputs(project)

        # 独立确认回执正文未被重写，并保留其原始 SHA-256。
        receipt_rel = pathlib.Path("report/evidence/S6-A/s6a_u6_02_decision_20261025_r07/decision_receipt.json")
        receipt = project / receipt_rel
        receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
        expected_semantics = [
            "确认并批准 §10 当前定义：在一个获取区间内，无论目标保持多久、冷却是否结束或窗口是否再次满足，恰好产生一次 ACTION_SUBMITTED。",
            "只有以下任一新获取重新满足稳定窗口，且提交时全局冷却门已结束，才允许产生下一次 ACTION_SUBMITTED：(a) 目标丢失确认后重新获取该目标并再次满足 §9 稳定窗口；(b) 切换到另一合法目标并满足 §9 稳定窗口。提交时须满足 t_now − t_last_submit ≥ T6-K01。",
            "目标持续保持、保持期间稳定窗口再次满足或冷却结束本身都不构成新的获取，也不产生重复提交。",
        ]
        if receipt_data.get("decision_id") != "U6-02" or receipt_data.get("decision_status") != "APPROVED_20261025":
            raise RuntimeError("U6-02 r07 回执身份或批准状态不符")
        if receipt_data.get("approved_semantics") != expected_semantics:
            raise RuntimeError("U6-02 r07 批准语义与固定原文不符")

        evidence_rel = pathlib.Path("report/evidence/S6-A/s6a_u6_02_bound_20261027_r05")
        state_rel = pathlib.Path(".codex/STATE.md")
        out_rel = pathlib.Path("tmp/s6a_recovery_20261029_r01/selfcheck_result.json")
        command = [
            sys.executable, "-B", "-X", "utf8",
            "verification/s6_g0_selfcheck.py",
            "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
            "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
            "--cases", str(evidence_rel / "hand_computed_cases.json"),
            "--upstream", str(evidence_rel / "upstream_bindings.json"),
            "--project-root", ".",
            "--evidence-dir", str(evidence_rel),
            "--out", str(out_rel),
            "--manifest", str(evidence_rel / "delivery_manifest.json"),
            "--state", str(state_rel),
        ]
        started = datetime.now(timezone.utc)
        run = subprocess.run(
            command,
            cwd=project,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        finished = datetime.now(timezone.utc)
        result_path = project / out_rel
        result = None
        if result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
        result_dir = RUN_DIR / "results"
        result_dir.mkdir(parents=True, exist_ok=True)
        if result_path.is_file():
            shutil.copyfile(result_path, result_dir / "clean_export_selfcheck_result.json")
        (result_dir / "clean_export_selfcheck_stdout.txt").write_bytes(run.stdout)
        (result_dir / "clean_export_selfcheck_stderr.txt").write_bytes(run.stderr)

        report = {
            "schema_version": 1,
            "artifact": "s6a_clean_export_recovery_execution",
            "task_id": "S6-A",
            "run_id": RUN_ID,
            "base_commit": BASE_COMMIT,
            "command": command,
            "command_display": subprocess.list2cmdline(command),
            "working_directory": "temporary clean git archive at pinned base commit with only inputs_manifest snapshots restored",
            "started_utc": started.isoformat(),
            "finished_utc": finished.isoformat(),
            "elapsed_seconds": (finished - started).total_seconds(),
            "exit_code": run.returncode,
            "stdout_sha256": hashlib.sha256(run.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(run.stderr).hexdigest(),
            "result_sha256": sha256(result_dir / "clean_export_selfcheck_result.json") if result_path.is_file() else None,
            "result_status": result.get("status") if isinstance(result, dict) else None,
            "checks": result.get("checks") if isinstance(result, dict) else None,
            "restored_inputs": restored,
            "u6_02_receipt_sha256": sha256(receipt),
            "u6_02_receipt_status": receipt_data["decision_status"],
            "u6_02_semantics_exact_match": True,
            "scope_limit": "此结果只证明指定提交加列明快照输入后，可恢复执行 S6-A 离线自检；不代表状态机行为、独立审查、G0/G4/G5 或实物验收通过。",
        }
        (RUN_DIR / "clean_export_execution.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if run.returncode != 0 or not isinstance(result, dict) or result.get("status") != "ALL_PASS":
            return 1
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
