#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T27 证据**哈希基座定稿**（companion 形式，兼容两套门禁）。

背景
====
项目级新规（2026-10-27，Wong 批准）要求证据 manifest 的每个哈希项声明 `hash_basis`
（`commit_blob` 权威 / `worktree_disk` 仅附注）。但主仓 `check_stage_delivery.py`（schema_version=1）
**尚未接受**清单内联的 `hash_basis` 字段（实测报"清单含未知字段：hash_basis"，exit 2），
而 N1 验收要求"干净检出复跑 checker exit 0"。

因此采用**双文件**形式，两套门禁同时满足：
- `delivery_manifest.json`：保持 schema 干净（不加内联字段）⇒ checker exit 0；
- `hash_basis_manifest.json`（同目录）：`entries[]` 逐项列出与清单一致的 path/sha256，并声明
  `hash_basis="commit_blob"`（按 `git cat-file blob <commit>:<path>` 重算核对）⇒ 新门禁 strict/declared-only 均 exit 0。

只读承诺：只改本包清单/基座表/哈希列表三个文件，不碰证据本体与被冻结成员。
退出码：0 = 三套门禁均 0 且无漂移；1 = 有不一致/门禁失败；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
GATE = pathlib.Path("D:/FPGA_Competition/verification/check_manifest_hash_basis.py")
CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
BASIS_FILE = "hash_basis_manifest.json"


class FinalizeError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(repo: pathlib.Path, commit: str, rel: str) -> bytes | None:
    completed = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), "cat-file", "blob",
                                f"{commit}:{rel}"], capture_output=True)
    return completed.stdout if completed.returncode == 0 else None


def run(cmd: list[str]) -> dict:
    completed = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": " ".join(cmd), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def write_hashes(run_dir: pathlib.Path) -> None:
    lines = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir() or path.name in {"hashes_sha256.txt", "delivery_manifest.json"}:
            continue
        lines.append(f"{sha256_bytes(path.read_bytes())} *{path.relative_to(REPO_ROOT).as_posix()}")
    (run_dir / "hashes_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    run_dir = pathlib.Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    manifest_path = run_dir / "delivery_manifest.json"
    if not manifest_path.is_file():
        print(f"[ENV_ERROR] 清单缺失：{manifest_path}", file=sys.stderr)
        return 2
    resolved = subprocess.run(["git", "--no-optional-locks", "-C", str(REPO_ROOT), "rev-parse",
                              "--verify", f"{args.commit}^{{commit}}"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
    if resolved.returncode != 0:
        print(f"[ENV_ERROR] 提交不可解析：{args.commit}", file=sys.stderr)
        return 2
    commit = resolved.stdout.strip()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    # 1) 清单保持 schema 干净：移除可能残留的内联基座字段
    manifest.pop("hash_basis", None)
    manifest.pop("hash_basis_note", None)
    for entry in manifest.get("files", []):
        entry.pop("hash_basis", None)
    # 2) 先登记 companion 文件（其自身哈希由 finalize 之后写入；清单只登记载荷）
    entries = manifest["files"]
    declared_paths = {e["path"] for e in entries}
    basis_rel = (run_dir / BASIS_FILE).relative_to(REPO_ROOT).as_posix()
    if basis_rel not in declared_paths:
        entries.append({"path": basis_rel, "role": "artifact",
                        "sha256": "0" * 64,
                        "keep_reason": "逐项声明哈希基座（commit_blob）的伴生清单；配合项目级新规与门禁"})
    # 3) 生成基座表（覆盖清单内除自身外的全部条目；逐项按 commit blob 复算）
    basis_entries: list[dict] = []
    mismatches: list[dict] = []
    missing: list[str] = []
    for entry in entries:
        rel = str(entry["path"]).replace("\\", "/")
        if rel == basis_rel:
            continue
        if rel.endswith("hashes_sha256.txt"):
            # 索引文件与基座表互为引用（循环），故不进基座表；其本身在 delivery_manifest 内
            # 作为 commit_blob 条目由 strict 模式核验（见 gate strict delivery_manifest）。
            continue
        data = git_blob(REPO_ROOT, commit, rel)
        if data is None:
            missing.append(rel)
            continue
        actual = sha256_bytes(data)
        if actual != entry["sha256"]:
            mismatches.append({"path": rel, "declared": entry["sha256"], "actual": actual})
            continue
        basis_entries.append({"path": rel, "sha256": entry["sha256"], "hash_basis": "commit_blob"})
    basis_doc = {
        "schema_version": 1,
        "task_id": manifest.get("task_id"),
        "run_id": manifest.get("run_id"),
        "hash_basis": "commit_blob",
        "hash_basis_note": (
            f"逐项 commit_blob 基座：按 `git cat-file blob {commit[:12]}:<path>` 的权威字节核对；"
            "本表与 delivery_manifest.json 的 files[] 一一对应（自身除外，由 finalize 复跑核对）。"
            "形式说明：主仓 check_stage_delivery.py 尚不接受清单内联 hash_basis 字段，故采用伴生清单形式，"
            "两套门禁（check_stage_delivery / check_manifest_hash_basis）同时满足。"),
        "entries": basis_entries,
    }
    basis_path = run_dir / BASIS_FILE
    basis_path.write_text(json.dumps(basis_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # 4) 回填 companion 自身哈希到清单
    basis_sha = sha256_bytes(basis_path.read_bytes())
    for entry in entries:
        if entry["path"] == basis_rel:
            entry["sha256"] = basis_sha
    write_hashes(run_dir)
    hashes_rel = (run_dir / "hashes_sha256.txt").relative_to(REPO_ROOT).as_posix()
    hashes_sha = sha256_bytes((run_dir / "hashes_sha256.txt").read_bytes())
    if hashes_rel not in {str(e["path"]).replace("\\", "/") for e in entries}:
        entries.append({"path": hashes_rel, "role": "artifact", "sha256": hashes_sha,
                        "keep_reason": "运行目录逐文件哈希索引（finalize 生成）"})
    for entry in entries:
        if entry["path"] == hashes_rel:
            entry["sha256"] = hashes_sha
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rel_manifest = manifest_path.relative_to(REPO_ROOT).as_posix()
    rel_basis = basis_path.relative_to(REPO_ROOT).as_posix()
    checker = run([sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                   "--project-root", str(REPO_ROOT), "--manifest", str(manifest_path)])
    strict_basis = run([sys.executable, "-B", str(GATE), "--repo", str(REPO_ROOT), "--commit", commit,
                        "--paths", rel_basis, "--mode", "strict", "--json"])
    declared_basis = run([sys.executable, "-B", str(GATE), "--repo", str(REPO_ROOT), "--commit", commit,
                          "--paths", rel_basis, "--mode", "declared-only", "--json"])
    strict_manifest = run([sys.executable, "-B", str(GATE), "--repo", str(REPO_ROOT), "--commit", commit,
                           "--paths", rel_manifest, "--mode", "strict", "--json"])

    summary = {
        "run_dir": run_dir.relative_to(REPO_ROOT).as_posix(), "commit": commit,
        "entries": len(entries), "basis_entries": len(basis_entries),
        "missing_in_commit": missing, "mismatches": mismatches,
        "basis_form": "companion hash_basis_manifest.json (commit_blob), delivery_manifest kept schema-clean",
        "gates": {
            "check_stage_delivery_evidence": checker["exit_code"],
            "hash_basis_strict_basis_file": strict_basis["exit_code"],
            "hash_basis_declared_only_basis_file": declared_basis["exit_code"],
            "hash_basis_strict_delivery_manifest": strict_manifest["exit_code"],
        },
        "gate_stdout": {"strict_basis": strict_basis["stdout"].strip()[-1200:],
                        "declared_basis": declared_basis["stdout"].strip()[-600:],
                        "checker": checker["stdout"].strip()[:600]},
    }
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    ok = (not missing and not mismatches
          and checker["exit_code"] == 0 and strict_basis["exit_code"] == 0
          and declared_basis["exit_code"] == 0 and strict_manifest["exit_code"] == 0)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
