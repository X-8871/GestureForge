from __future__ import annotations

import hashlib
import json
import pathlib
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone


ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
MAIN_ROOT = pathlib.Path(r"D:\FPGA_Competition")
RUN_ID = "s6a_u6_02_recovery_20261029_r04"
RUN_DIR = ROOT / "report/evidence/S6-A" / RUN_ID
OLD_RUN_DIR = ROOT / "report/evidence/S6-A/s6a_u6_02_recovery_20261029_r01"
BASE_COMMIT = "86a2bb18e1a197dc56d07ea8c42ec38a6adf3ed1"
MAIN_COMMIT = "11044e5fb815f9f8570ee0b7332b113d9f924460"
UTC8 = timezone(timedelta(hours=8))
TOOL_SPECS = {
    "check_stage_delivery.py": {
        "blob_oid": "7be1af75609e9fa29ca9afe5f8024d31545a3224",
        "disk_sha256": "00350ac813e928c052e43a5237fdf7a9be79d75c952cf691318eeb1e9fceeb8e",
    },
    "check_manifest_hash_basis.py": {
        "blob_oid": "2565d9a54d26ffc1392b5a3156ee8a9f004d5a21",
        "disk_sha256": "10e3fe7121cc46665cfcd553dc5237833fe3134bc0dd00a8652d79fa290e85f6",
    },
}


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


def git_text(repo: pathlib.Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
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


def main() -> int:
    started = datetime.now(UTC8)
    if not RUN_DIR.is_dir():
        raise RuntimeError("唯一新 RunId 目录不存在")
    if git_text(ROOT, "rev-parse", "--abbrev-ref", "HEAD") != "stage6-interact-prep":
        raise RuntimeError("w6 分支已变化；拒绝继续")
    if git_text(ROOT, "rev-parse", "HEAD") != BASE_COMMIT:
        raise RuntimeError("w6 HEAD 已变化；拒绝继续")
    if git_text(MAIN_ROOT, "rev-parse", "HEAD") != MAIN_COMMIT:
        raise RuntimeError("main 门禁工具提交已变化；拒绝继续")

    old_manifest_path = OLD_RUN_DIR / "inputs_manifest.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    if old_manifest.get("run_id") != "s6a_u6_02_recovery_20261029_r01":
        raise RuntimeError("r01 原始输入清单身份不符")
    if old_manifest.get("source_commit") != BASE_COMMIT:
        raise RuntimeError("r01 输入清单的来源提交不符")

    # 先完成所有只读校验，随后才向 r04 的专属输入目录写入快照。
    pending: list[dict[str, object]] = []
    destinations: set[str] = set()
    for item in old_manifest.get("files", []):
        source_rel = safe_relative(item["source_path"])
        source = ROOT.joinpath(*source_rel.parts)
        prior_snapshot = OLD_RUN_DIR.joinpath(*safe_relative(item["path"]).parts)
        if not source.is_file() or not prior_snapshot.is_file():
            raise RuntimeError(f"缺少源文件或 r01 快照：{item['source_path']}")
        if source.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"当前源文件长度与 r01 快照不同：{item['source_path']}")
        if sha256_file(source) != item["sha256"]:
            raise RuntimeError(f"当前源文件哈希与 r01 快照不同：{item['source_path']}")
        if prior_snapshot.stat().st_size != item["size_bytes"]:
            raise RuntimeError(f"r01 快照长度不符：{item['path']}")
        if sha256_file(prior_snapshot) != item["sha256"]:
            raise RuntimeError(f"r01 快照哈希不符：{item['path']}")
        destination_rel = pathlib.PurePosixPath("inputs/project", *source_rel.parts)
        destination = RUN_DIR.joinpath(*destination_rel.parts)
        if destination.exists() or destination.is_symlink():
            raise RuntimeError(f"r04 快照目标已存在：{destination_rel.as_posix()}")
        key = destination_rel.as_posix().casefold()
        if key in destinations:
            raise RuntimeError(f"r01 输入清单存在重复路径：{destination_rel.as_posix()}")
        destinations.add(key)
        pending.append({
            "source": source,
            "source_path": source_rel.as_posix(),
            "prior_snapshot": prior_snapshot,
            "destination": destination,
            "destination_path": destination_rel.as_posix(),
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
        })

    tool_pending: list[dict[str, object]] = []
    for name, spec in TOOL_SPECS.items():
        source = MAIN_ROOT / "verification" / name
        if not source.is_file():
            raise RuntimeError(f"main 门禁源码不存在：{source}")
        blob = git_text(MAIN_ROOT, "rev-parse", f"{MAIN_COMMIT}:verification/{name}")
        object_id = git_text(MAIN_ROOT, "hash-object", str(source))
        disk_sha = sha256_file(source)
        if blob != spec["blob_oid"] or object_id != spec["blob_oid"]:
            raise RuntimeError(f"main 门禁源码 Git blob 与固定版本不符：{name}")
        if disk_sha != spec["disk_sha256"]:
            raise RuntimeError(f"main 门禁源码磁盘 SHA-256 与固定版本不符：{name}")
        destination_rel = pathlib.PurePosixPath("inputs/tool_sources", name)
        destination = RUN_DIR.joinpath(*destination_rel.parts)
        if destination.exists() or destination.is_symlink():
            raise RuntimeError(f"r04 门禁源码快照目标已存在：{destination_rel.as_posix()}")
        tool_pending.append({
            "name": name,
            "source": source,
            "destination": destination,
            "destination_path": destination_rel.as_posix(),
            "source_path": f"verification/{name}",
            "blob_oid": blob,
            "disk_sha256": disk_sha,
            "size_bytes": source.stat().st_size,
        })

    helpers = [
        RUN_DIR / "prepare_recovery_package.py",
        RUN_DIR / "recover_clean_checkout.py",
        RUN_DIR / "finalize_recovery_package.py",
        RUN_DIR / "verify_approved_receipt.py",
    ]
    for helper in helpers:
        if not helper.is_file():
            raise RuntimeError(f"缺少已预建并待核验的脚本：{helper.name}")

    bindings: list[dict[str, object]] = []
    for item in pending:
        destination = item["destination"]
        assert isinstance(destination, pathlib.Path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item["source"], destination)
        if sha256_file(destination) != item["sha256"]:
            raise RuntimeError(f"快照写入后哈希不符：{item['source_path']}")
        bindings.append({
            "path": f"report/evidence/S6-A/{RUN_ID}/{item['destination_path']}",
            "source_path": item["source_path"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "hash_basis": "worktree_disk",
            "origin": "w6 当前工作树；与 r01 初始捕获快照逐项复核一致",
        })

    tool_bindings: list[dict[str, object]] = []
    for item in tool_pending:
        destination = item["destination"]
        assert isinstance(destination, pathlib.Path)
        shutil.copyfile(item["source"], destination)
        if sha256_file(destination) != item["disk_sha256"]:
            raise RuntimeError(f"门禁源码快照哈希不符：{item['name']}")
        tool_bindings.append({
            "path": f"report/evidence/S6-A/{RUN_ID}/{item['destination_path']}",
            "sha256": item["disk_sha256"],
            "size_bytes": item["size_bytes"],
            "hash_basis": "worktree_disk",
            "origin_repo": str(MAIN_ROOT),
            "origin_path": item["source_path"],
            "origin_commit": MAIN_COMMIT,
            "origin_git_blob_oid": item["blob_oid"],
            "origin_disk_sha256": item["disk_sha256"],
            "origin_worktree_sha256": item["disk_sha256"],
        })

    basis_note = "SHA-256 按工作区磁盘字节计算；不将未提交快照伪称为 commit_blob。"
    bindings_doc = {
        "schema_version": 1,
        "artifact": "s6a_recovery_source_bindings",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": BASE_COMMIT,
        "hash_basis": "worktree_disk",
        "hash_basis_note": basis_note,
        "files": bindings,
        "source_scope": "包含 C11 STATE 实际引用的全部本地文件快照，以及为门禁核验固定的 main 当前脚本。",
    }
    bindings_path = RUN_DIR / "source_bindings.json"
    write_json(bindings_path, bindings_doc)
    tool_provenance_doc = {
        "schema_version": 1,
        "artifact": "s6a_recovery_tool_source_provenance",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": BASE_COMMIT,
        "hash_basis": "worktree_disk",
        "hash_basis_note": basis_note,
        "tool_source_commit": MAIN_COMMIT,
        "files": tool_bindings,
        "scope": "工具快照用于在原 w6 工作树运行项目统一门禁；不覆盖 pinned clean clone 中 86a2 绑定的旧 checker。",
    }
    tool_provenance_path = RUN_DIR / "tool_source_provenance.json"
    write_json(tool_provenance_path, tool_provenance_doc)

    source_commit_time = git_text(ROOT, "show", "-s", "--format=%cI", BASE_COMMIT)
    prep_doc = {
        "schema_version": 1,
        "artifact": "s6a_recovery_snapshot_preparation",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": BASE_COMMIT,
        "source_commit_time": source_commit_time,
        "branch": "stage6-interact-prep",
        "started_utc8": started.strftime("%Y-%m-%d %H:%M:%S%z"),
        "finished_utc8": datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S%z"),
        "input_source_run_id": old_manifest["run_id"],
        "source_input_count": len(pending),
        "tool_source_count": len(tool_pending),
        "total_snapshot_bytes": sum(int(item["size_bytes"]) for item in pending + tool_pending),
        "source_bindings_sha256": sha256_file(bindings_path),
        "tool_source_provenance_sha256": sha256_file(tool_provenance_path),
        "checks": [
            {"name": "pinned_w6_branch_and_HEAD", "status": "PASS", "exit_code": 0},
            {"name": "current_source_files_equal_r01_snapshot", "status": "PASS", "exit_code": 0},
            {"name": "main_gate_sources_match_pinned_git_blob_and_disk_sha256", "status": "PASS", "exit_code": 0},
        ],
        "limitations": [
            "此准备记录仅绑定离线恢复输入，不等同于 S6-A 语义自检、独立审查或阶段验收。",
            "文件快照使用 worktree_disk 基座；基线提交仅用于隔离克隆与源码版本定位。",
        ],
        "hash_basis": "worktree_disk",
        "hash_basis_note": basis_note,
    }
    prep_path = RUN_DIR / "snapshot_preparation.json"
    write_json(prep_path, prep_doc)

    command = subprocess.list2cmdline([
        sys.executable, "-B", "-X", "utf8", str(RUN_DIR / "prepare_recovery_package.py")
    ])
    files: list[dict[str, object]] = []
    for item in pending:
        files.append({
            "path": f"report/evidence/S6-A/{RUN_ID}/{item['destination_path']}",
            "sha256": item["sha256"],
            "role": "input",
            "keep_reason": f"从精确源路径 {item['source_path']} 捕获的恢复输入；覆盖 r01 所有源字节。",
            "hash_basis": "worktree_disk",
        })
    for item in tool_pending:
        files.append({
            "path": f"report/evidence/S6-A/{RUN_ID}/{item['destination_path']}",
            "sha256": item["disk_sha256"],
            "role": "source",
            "keep_reason": f"统一项目门禁源码，固定 main {MAIN_COMMIT} 的 Git blob 与磁盘 SHA-256。",
            "hash_basis": "worktree_disk",
        })
    files.append({
        "path": f"report/evidence/S6-A/{RUN_ID}/source_bindings.json",
        "sha256": sha256_file(bindings_path),
        "role": "input",
        "keep_reason": "把快照文件精确绑定到恢复目标路径及原始来源。",
        "hash_basis": "worktree_disk",
    })
    files.append({
        "path": f"report/evidence/S6-A/{RUN_ID}/tool_source_provenance.json",
        "sha256": sha256_file(tool_provenance_path),
        "role": "input",
        "keep_reason": "固定 main 统一门禁源码的提交、Git blob、原始磁盘 SHA 与快照哈希。",
        "hash_basis": "worktree_disk",
    })
    for helper in helpers:
        files.append({
            "path": f"report/evidence/S6-A/{RUN_ID}/{helper.name}",
            "sha256": sha256_file(helper),
            "role": "source",
            "keep_reason": "本次离线恢复与证据封装脚本，随运行证据保留。",
            "hash_basis": "worktree_disk",
        })
    input_manifest = {
        "schema_version": 1,
        "stage": "6",
        "task_id": "S6-A",
        "run_id": RUN_ID,
        "source_commit": BASE_COMMIT,
        "evidence_dir": f"report/evidence/S6-A/{RUN_ID}",
        "hash_basis": "worktree_disk",
        "hash_basis_note": basis_note,
        "interfaces": [],
        "interfaces_not_applicable_reason": "本次只恢复和复跑 S6-A 的既有批准与自检输入，不消费阶段4/5接口或真实测量结果。",
        "files": files,
        "checks": [{
            "name": "source_snapshots_and_tool_versions_bound",
            "status": "PASS",
            "command": command,
            "exit_code": 0,
            "reason": "脚本先只读校验所有源路径和文件哈希，再写入新 RunId 快照并核对复制字节。",
        }],
        "limitations": [
            "输入核验只检查本地快照路径、内容绑定与固定工具版本，不代表 S6-A 语义、独立审查或 G0/G4/G5。",
            "阶段4/5实测依赖、硬件连接与板级结果不属于此离线恢复输入。",
        ],
        "tool_versions": {
            "python": f"CPython {platform.python_version()}",
            "git": git_text(ROOT, "--version"),
            "main_commit": MAIN_COMMIT,
            "check_stage_delivery_blob": TOOL_SPECS["check_stage_delivery.py"]["blob_oid"],
            "check_manifest_hash_basis_blob": TOOL_SPECS["check_manifest_hash_basis.py"]["blob_oid"],
        },
    }
    write_json(RUN_DIR / "inputs_manifest.json", input_manifest)
    print(json.dumps({
        "status": "SNAPSHOTS_PREPARED",
        "run_id": RUN_ID,
        "source_inputs": len(pending),
        "tool_sources": len(tool_pending),
        "bytes": prep_doc["total_snapshot_bytes"],
        "source_bindings_sha256": prep_doc["source_bindings_sha256"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"准备失败：{type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
