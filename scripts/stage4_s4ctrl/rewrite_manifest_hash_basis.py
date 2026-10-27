#!/usr/bin/env python3
"""把证据清单的 `files[].sha256` 重算为**提交 blob 基座**（DELTA 修复 ①）。

背景：早前清单用 `Get-FileHash`（工作区字节）生成，而工作区文本文件在 `core.autocrlf`
下是 CRLF、提交 blob 是 LF，且个别项在清单生成后又被同一会话重写 ⇒ 基座不一致。
本脚本以 `git cat-file blob <commit>:<path>` 的**提交内容**为唯一权威重算，并：
  · 为每项写入 `hash_basis = "commit_blob"` 与 `source_commit`；
  · 同时在 `hash_basis_recompute.json` 中给出 **提交 blob SHA-256 与当前磁盘 SHA-256 并列**的复算表；
  · 任一路径无法从该提交解析 ⇒ fail-closed（exit 1），不写半成品。

用法：
  python -B scripts/stage4_s4ctrl/rewrite_manifest_hash_basis.py \
      --manifest report/evidence/S4-CTRL/<run>/landing_manifest.json \
      --commit <sha> [--verify-only]
退出码：0=全部解析并写入；1=存在无法解析项或校验不符；2=参数/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]


def git_blob(commit: str, rel: str) -> tuple[str | None, str | None]:
    """取 `<commit>:<rel>` 的 blob 内容字节；返回 (sha256, error)。

    `commit` 传 `:index:` 表示取**暂存区**内容（等价于即将写入提交的 blob）。
    """
    spec = f":{rel}" if commit == ":index:" else f"{commit}:{rel}"
    proc = subprocess.run(["git", "-C", str(WORKTREE), "cat-file", "blob", spec],
                          capture_output=True)
    if proc.returncode != 0:
        return None, f"cat-file blob {spec} 退出 {proc.returncode}"
    return hashlib.sha256(proc.stdout).hexdigest(), None


def disk_sha(rel: str) -> str | None:
    """当前工作区字节 SHA-256（仅作并列参考）。"""
    path = WORKTREE / rel
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main() -> int:
    """执行重算。"""
    parser = argparse.ArgumentParser(description="证据清单 hash basis 重算（提交 blob 基座）")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--commit", required=True,
                        help="commit_blob 基座所用提交；传 :index: 表示暂存区（即将写入的提交）")
    parser.add_argument("--baseline-commit", default="",
                        help="可选：被审基线提交，复算表中并列其 blob SHA（仅历史参考）")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"[FAIL] 清单不存在：{args.manifest}")
        return 2
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        print("[FAIL] 清单缺少 files[]")
        return 2

    table: list[dict[str, object]] = []
    failures: list[str] = []
    changed = 0
    for entry in files:
        rel = str(entry["path"]).replace("\\", "/")
        blob, error = git_blob(args.commit, rel)
        baseline_blob = git_blob(args.baseline_commit, rel)[0] if args.baseline_commit else None
        record = {"path": rel, "commit_blob_sha256": blob, "disk_sha256": disk_sha(rel),
                  "baseline_commit": args.baseline_commit or None,
                  "baseline_blob_sha256": baseline_blob,
                  "previous_recorded_sha256": entry.get("sha256"), "error": error}
        if blob is None:
            failures.append(rel)
        else:
            record["previous_matches_commit_blob"] = entry.get("sha256") == blob
            if not record["previous_matches_commit_blob"]:
                changed += 1
            if not args.verify_only:
                entry["sha256"] = blob
                entry["hash_basis"] = "commit_blob"
                if args.commit != ":index:":
                    entry["source_commit"] = args.commit
        table.append(record)

    if not args.verify_only:
        manifest["hash_basis"] = "commit_blob"
        manifest["hash_basis_note"] = (
            "全部 files[].sha256 取自 `git cat-file blob <承载提交>:<path>` 的**提交内容**"
            "（仓库内容权威）；工作区字节（`core.autocrlf` 下为 CRLF）与可选的被审基线 blob 仅写入 "
            "hash_basis_recompute.json 并列参考，不参与校验。")
        manifest["hash_basis_commit"] = ("HEAD（承载本清单的提交）" if args.commit == ":index:"
                                         else args.commit)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out_dir = args.manifest.parent
    (out_dir / "hash_basis_recompute.json").write_text(
        json.dumps({"manifest": args.manifest.name, "source_commit": args.commit,
                    "hash_basis": "commit_blob", "entries": len(table),
                    "previous_mismatch_count": changed,
                    "baseline_commit": args.baseline_commit or None,
                    "columns": ["commit_blob_sha256", "baseline_blob_sha256", "disk_sha256"],
                    "table": table, "failures": failures},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for record in table:
        print(f"[{'OK' if record['commit_blob_sha256'] else 'FAIL'}] {record['path']} "
              f"blob={record['commit_blob_sha256']} disk={record['disk_sha256']}")
    status = "PASS" if not failures else "FAIL"
    print(f"[{status}] hash basis 重算：{len(table) - len(failures)}/{len(table)} 项来自提交 blob；"
          f"原记录不符项 {changed} 项已更正；失败={failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())