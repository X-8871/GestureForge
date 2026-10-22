#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐文件核对：工作区字节 vs 被审提交 1632761 的 blob 字节（按 git 归一化比较）。"""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
COMMIT = "1632761b2d60d8c1328aa82be97d53eef30e1072"

files = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", "b20b670", COMMIT],
                       capture_output=True, text=True, encoding="utf-8").stdout.split()
lines = [f"被审提交改动 {len(files)} 个文件；逐文件 worktree vs git@1632761 字节比较："]
bad = []
for rel in files:
    blob = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", f"{COMMIT}:{rel}"],
                          capture_output=True).stdout
    work = (ROOT / rel).read_bytes()
    exact = hashlib.sha256(work).hexdigest() == hashlib.sha256(blob).hexdigest()
    norm = work.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n")
    tag = "字节相同" if exact else ("仅换行差异(CRLF↔LF，git 归一化相同)" if norm else "**内容不同**")
    if not norm:
        bad.append(rel)
    lines.append(f"  {rel}: {tag}")
    if not exact:
        lines.append(f"      worktree={'CRLF' if b'\\r\\n' in work else 'LF'} "
                     f"blob={'CRLF' if b'\\r\\n' in blob else 'LF'} "
                     f"worktree_sha={hashlib.sha256(work).hexdigest()[:16]} "
                     f"blob_sha={hashlib.sha256(blob).hexdigest()[:16]}")
lines.append(f"\n内容真正不同的文件：{bad if bad else '（无）'}")
(OUT / "my_bytes_check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))