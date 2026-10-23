#!/usr/bin/env python3
"""S3-T17 自证工具：逐文件比较「指定提交的 blob 字节」与「工作区字节」，并统计 CRLF。

用途（本仓库 core.autocrlf=true 会引入 CRLF/LF 口径差，曾导致哈希绑定失配）：
    证明证据包里 `hashes_sha256.txt` 记录的字节确实等于提交内字节；第三方可复跑。

用法：
    python -B scripts/stage3_t17/verify_t17_blob_identity.py [--commit <rev>] [--json-out f.json]
默认范围：`report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/S3-T17/**`、`scripts/stage3_t17/**`
的文本文件（.json/.md/.txt/.py/.sh/.tcl）。

退出码：0 全部一致；1 存在不一致（列出路径）；2 参数/环境错误。
边界：只读；不写仓库文件（--json-out 只写调用方指定的路径）；结论不代表 G0/G4/G5 或独立审查。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

UTC8 = timezone(timedelta(hours=8))
DEFAULT_SCOPES = (
    "report/evidence/S3-T17",
    "report/evidence/S3-CTRL/S3-T17",
    "scripts/stage3_t17",
)
TEXT_EXT = (".json", ".md", ".txt", ".py", ".sh", ".tcl")


def git_show(repo: str, rev: str, path: str) -> bytes | None:
    cp = subprocess.run(["git", "--no-optional-locks", "-C", repo, "show", f"{rev}:{path}"],
                        capture_output=True)
    return cp.stdout if cp.returncode == 0 else None


def resolve_rev(repo: str, rev: str) -> str | None:
    cp = subprocess.run(["git", "--no-optional-locks", "-C", repo, "rev-parse", rev],
                        capture_output=True, text=True)
    return (cp.stdout or "").strip() if cp.returncode == 0 else None


def main(argv):
    ap = argparse.ArgumentParser(description="S3-T17 blob 字节自证", allow_abbrev=False)
    ap.add_argument("--repo-root", default=os.getcwd())
    ap.add_argument("--commit", default="HEAD")
    ap.add_argument("--scope", action="append", default=[])
    ap.add_argument("--exclude", action="append", default=[],
                    help="排除的自证产物（仓库相对路径，可重复）。用于 F/G 两段式："
                         "对内容提交 F 核验时排除仅在自证提交 G 中新增的本工具与自证输出。")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.repo_root)
    if not os.path.isdir(os.path.join(repo, ".git")) and subprocess.run(
            ["git", "--no-optional-locks", "-C", repo, "rev-parse", "--git-dir"],
            capture_output=True).returncode != 0:
        print(f"不是 git 仓库：{repo}")
        return 2
    rev = resolve_rev(repo, args.commit)
    if rev is None:
        print(f"提交不可解析：{args.commit}")
        return 2
    scopes = tuple(args.scope) or DEFAULT_SCOPES
    excluded = {item.replace("\\", "/") for item in args.exclude}

    files = []
    for scope in scopes:
        root = os.path.join(repo, scope.replace("/", os.sep))
        for dirpath, _dirs, names in os.walk(root):
            for name in names:
                if name.lower().endswith(TEXT_EXT):
                    rel = os.path.relpath(os.path.join(dirpath, name), repo).replace("\\", "/")
                    if rel not in excluded:
                        files.append(rel)
    files.sort()

    mismatches, missing, crlf = [], [], []
    for rel in files:
        full = os.path.join(repo, rel.replace("/", os.sep))
        wt = open(full, "rb").read()
        if b"\r\n" in wt:
            crlf.append(rel)
        blob = git_show(repo, rev, rel)
        if blob is None:
            missing.append(rel)
            continue
        if blob != wt:
            mismatches.append({
                "path": rel,
                "worktree_sha256": hashlib.sha256(wt).hexdigest(),
                "commit_sha256": hashlib.sha256(blob).hexdigest(),
            })

    result = {
        "created_utc8": datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "repo_root": repo,
        "commit": rev,
        "scopes": list(scopes),
        "excluded_selfproof_artifacts": sorted(excluded),
        "files_checked": len(files),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "not_in_commit": missing,
        "crlf_files_in_worktree": crlf,
        "verdict": "BLOB_BYTE_IDENTITY_OK" if not mismatches and not missing else "BLOB_BYTE_IDENTITY_MISMATCH",
        "note": "逐文件比较 git blob 字节与工作区字节；本仓库 autocrlf=true，故哈希一律以 blob（LF）为准。",
    }
    print(f"提交={rev} 检查文件={len(files)} 不一致={len(mismatches)} 提交内缺失={len(missing)} 工作区含 CRLF={len(crlf)}")
    for item in mismatches:
        print("  MISMATCH %s" % item["path"])
    for rel in missing:
        print("  NOT_IN_COMMIT %s" % rel)
    print(f"结论={result['verdict']}")
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"JSON_OUT={args.json_out}")
    return 0 if result["verdict"] == "BLOB_BYTE_IDENTITY_OK" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))