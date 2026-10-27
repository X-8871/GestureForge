#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""证据 manifest 哈希基座校验器（只读、fail-closed）。

规则（2026-10-27 Wong 批准，项目级）：
- 证据 manifest 的每个哈希项**必须声明哈希基座**，取值二选一：
  - ``commit_blob``    —— 按 ``git cat-file blob <commit>:<path>`` 的字节计算（**推荐、内容权威**）
  - ``worktree_disk``  —— 按工作区磁盘文件字节计算（**仅作附注**，受 autocrlf/换行转换影响）
- 基座可写在**条目级**（``hash_basis``）或 **manifest 级**（默认值）；条目级覆盖 manifest 级。
- ``declared-only`` 模式（默认）：未声明基座的 manifest/条目**跳过并计数**（legacy 不追溯）；
  ``strict`` 模式：未声明基座按 ``commit_blob`` 校验。

为什么需要：本项目已三次出现"清单哈希按磁盘字节算、仓库按 blob 存"导致的假 FAIL/假 PASS
（阶段3 renormalize、阶段5 S5-T27 N1、阶段4 S4-T30 NB-4）。

退出码：
  0 全部一致（或按模式全部跳过）
  1 存在不一致
  2 输入/环境错误（fail-closed，不把异常伪装成通过）

用法：
  python -B verification/check_manifest_hash_basis.py --repo D:/codex-worktrees/w4 \\
      --paths "report/evidence/**/*manifest*.json" --mode strict --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASES = ("commit_blob", "worktree_disk")
LIST_KEYS = ("files", "members", "entries", "artifacts", "items")


def git(repo: Path, *args: str) -> tuple[int, bytes]:
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        capture_output=True,
    )
    return proc.returncode, proc.stdout


def norm_sha(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    for prefix in ("sha256:", "sha256=", "sha256 "):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    return text if len(text) == 64 and all(c in "0123456789abcdef" for c in text) else None


def entry_list(doc: dict) -> list[dict] | None:
    for key in LIST_KEYS:
        value = doc.get(key)
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            if any(("path" in x or "file" in x) and ("sha256" in x or "sha" in x) for x in value):
                return value
    return None


def entry_path(item: dict) -> str | None:
    for key in ("path", "file", "relpath"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().replace("\\", "/")
    return None


def entry_sha(item: dict) -> str | None:
    for key in ("sha256", "sha", "digest"):
        value = norm_sha(item.get(key))
        if value:
            return value
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="证据 manifest 哈希基座校验器（只读、fail-closed）")
    ap.add_argument("--repo", default=".", help="仓库/工作树根（默认当前目录）")
    ap.add_argument("--commit", default="HEAD", help="commit_blob 基座使用的提交（默认 HEAD）")
    ap.add_argument("--paths", action="append", default=None,
                    help="manifest 路径 glob（可重复；默认 report/evidence/**/*.json）")
    ap.add_argument("--mode", choices=("declared-only", "strict"), default="declared-only")
    ap.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = ap.parse_args()

    try:
        repo = Path(args.repo).resolve()
        rc, out = git(repo, "rev-parse", "--show-toplevel")
        if rc != 0:
            print(f"[FAIL] 不是 Git 仓库：{repo}", file=sys.stderr)
            return 2
        root = Path(out.decode("utf-8", "replace").strip())
        commit = args.commit
        rc, out = git(root, "rev-parse", "--verify", f"{commit}^{{commit}}")
        if rc != 0:
            print(f"[FAIL] 提交不可解析：{commit}", file=sys.stderr)
            return 2
        commit = out.decode("utf-8", "replace").strip()
    except Exception as exc:  # fail-closed
        print(f"[FAIL] 环境错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    globs = args.paths or ["report/evidence/**/*.json"]
    paths: list[Path] = []
    for pattern in globs:
        paths.extend(sorted(root.glob(pattern)))
    paths = sorted({p for p in paths if p.is_file()})

    blob_cache: dict[str, bytes | None] = {}

    def blob_bytes(rel: str) -> bytes | None:
        if rel not in blob_cache:
            rc, out = git(root, "cat-file", "blob", f"{commit}:{rel}")
            blob_cache[rel] = out if rc == 0 else None
        return blob_cache[rel]

    checked = mismatched = skipped_entries = 0
    manifests = 0
    problems: list[dict] = []
    skipped_manifests: list[str] = []

    for path in paths:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        items = entry_list(doc)
        if items is None:
            continue
        manifests += 1
        manifest_basis = doc.get("hash_basis")
        seen = False
        for idx, item in enumerate(items):
            rel = entry_path(item)
            declared = entry_sha(item)
            if not rel or not declared:
                continue
            basis = item.get("hash_basis", manifest_basis)
            if basis is None:
                if args.mode == "declared-only":
                    skipped_entries += 1
                    continue
                basis = "commit_blob"
            if basis not in BASES:
                problems.append({"manifest": str(path.relative_to(root)), "index": idx,
                                 "path": rel, "problem": f"unknown_hash_basis:{basis}"})
                mismatched += 1
                seen = True
                continue
            if basis == "commit_blob":
                data = blob_bytes(rel)
                if data is None:
                    problems.append({"manifest": str(path.relative_to(root)), "index": idx,
                                     "path": rel, "problem": "path_not_in_commit"})
                    mismatched += 1
                    seen = True
                    continue
                actual = hashlib.sha256(data).hexdigest()
            else:
                target = root / rel
                if not target.is_file():
                    problems.append({"manifest": str(path.relative_to(root)), "index": idx,
                                     "path": rel, "problem": "worktree_path_missing"})
                    mismatched += 1
                    seen = True
                    continue
                actual = hashlib.sha256(target.read_bytes()).hexdigest()
            checked += 1
            if actual != declared:
                mismatched += 1
                seen = True
                problems.append({"manifest": str(path.relative_to(root)), "index": idx,
                                 "path": rel, "basis": basis,
                                 "declared": declared, "actual": actual, "problem": "hash_mismatch"})
        if not seen and not any(i.get("hash_basis", manifest_basis) for i in items):
            skipped_manifests.append(str(path.relative_to(root)))

    summary = {
        "repo": str(root), "commit": commit, "mode": args.mode,
        "globs": globs, "manifests_seen": manifests,
        "entries_checked": checked, "mismatched": mismatched,
        "entries_skipped_undeclared": skipped_entries,
        "manifests_skipped_no_basis": len(skipped_manifests),
        "verdict": "OK" if mismatched == 0 else "FAIL",
        "problems": problems[:50],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"repo={root}")
        print(f"commit={commit} mode={args.mode}")
        print(f"manifests={manifests} checked={checked} mismatched={mismatched} "
              f"skipped_undeclared={skipped_entries} skipped_manifests={len(skipped_manifests)}")
        for p in problems[:20]:
            print(f"  [MISMATCH] {p['manifest']}#{p['index']} {p['path']} "
                  f"({p.get('basis', '?')}) declared={p.get('declared', '-')} actual={p.get('actual', '-')} "
                  f"problem={p['problem']}")
        print(f"结论：{summary['verdict']}")

    return 0 if mismatched == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # fail-closed：异常一律 exit 2
        print(f"[FAIL] 未捕获异常：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)