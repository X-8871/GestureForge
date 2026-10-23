#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reviewer 复算：① 记录哈希 vs git blob（LF）字节哈希；② 工作区字节 BOM/LF 事实。
在传输克隆内按 blob 口径复算，避免 checkout 的 CRLF 转换干扰。"""
import hashlib
import os
import re
import subprocess
import sys

REAL = r"D:\codex-worktrees\dbdf"
CLONE = r"D:\FPGA_Competition\tmp\review\S3_T17_A_20261023_r01\dbdf_clone"
OUT = os.path.dirname(os.path.abspath(__file__))
SCOPES = ("report/evidence/S3-T17", "report/evidence/S3-CTRL/S3-T17", "scripts/stage3_t17")


def git(repo, *args):
    cp = subprocess.run(["git", "--no-optional-locks", "-C", repo, *args], capture_output=True)
    return cp.stdout if cp.returncode == 0 else None


def blob(repo, rev, path):
    return git(repo, "show", f"{rev}:{path}")


rev = git(CLONE, "rev-parse", "HEAD").decode().strip()
tracked = [l for l in git(CLONE, "ls-tree", "-r", "--name-only", rev).decode().splitlines()]
in_scope = [p for p in tracked if any(p.startswith(s + "/") for s in SCOPES)]
print("HEAD=%s  三范围被跟踪文件数=%d" % (rev, len(in_scope)))

# ① 记录哈希 vs blob 哈希
records = []
for p in in_scope:
    if os.path.basename(p) == "hashes_sha256.txt" or p.endswith("selfproof_hashes_sha256.txt"):
        records.append(p)
rec_ok = rec_bad = 0
problems = []
print("\n--- 记录哈希清单 ---")
for rp in sorted(records):
    raw = blob(CLONE, rev, rp)
    if raw is None:
        print("  MISSING %s" % rp); continue
    text = raw.decode("utf-8", errors="replace")
    n = 0
    for line in text.splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+\*?(.+?)\s*$", line.strip())
        if not m:
            continue
        want, path = m.group(1), m.group(2).replace("\\", "/").strip()
        if path.startswith("./"):
            path = path[2:]
        # 记录里的路径是「相对该 hashes 文件所在目录」的
        if "/" not in path or not any(path.startswith(s + "/") for s in SCOPES):
            path = os.path.dirname(rp).replace("\\", "/") + "/" + path
        b = blob(CLONE, rev, path)
        if b is None:
            rec_bad += 1; problems.append((rp, path, "NOT_IN_COMMIT")); continue
        got = hashlib.sha256(b).hexdigest()
        n += 1
        if got == want:
            rec_ok += 1
        else:
            rec_bad += 1; problems.append((rp, path, f"blob={got} rec={want}"))
    print("  %-70s 条目=%d" % (rp, n))
print("blob哈希与记录一致=%d 不一致=%d" % (rec_ok, rec_bad))
for item in problems:
    print("   PROBLEM %s -> %s : %s" % item)

# ② 工作区字节：BOM / CRLF（源工作树 = 被审实际状态）
print("\n--- 源工作树字节事实（UTF-8 BOM / CRLF）---")
bom = crlf = plain = 0
for p in sorted(in_scope):
    fp = os.path.join(REAL, p.replace("/", os.sep))
    if not os.path.isfile(fp):
        print("  MISSING_IN_WORKTREE %s" % p); continue
    b = open(fp, "rb").read()
    has_bom = b.startswith(b"\xef\xbb\xbf")
    has_crlf = b"\r\n" in b
    bom += has_bom; crlf += has_crlf; plain += (not has_bom and not has_crlf)
    if has_bom or has_crlf:
        print("  ODD %s bom=%s crlf=%s" % (p, has_bom, has_crlf))
print("合计 %d 个文件：含 BOM=%d，含 CRLF=%d，纯 UTF-8 无 BOM + LF=%d" % (len(in_scope), bom, crlf, plain))

# ③ blob 口径与工作区口径的同一性（源工作树）
same = diff = 0
for p in sorted(in_scope):
    fp = os.path.join(REAL, p.replace("/", os.sep))
    if not os.path.isfile(fp):
        continue
    b = blob(CLONE, rev, p)
    if b is None:
        continue
    if b == open(fp, "rb").read():
        same += 1
    else:
        diff += 1
print("源工作树字节 == 提交 blob 字节：一致=%d 不一致=%d" % (same, diff))