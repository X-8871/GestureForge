#!/usr/bin/env python3
"""校验副本工作树与某提交的逐路径“同口径”（内容相同，允许换行差异），并报告换行约定。"""
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
W6 = r"D:\codex-worktrees\w6"
repo, rev = sys.argv[1], sys.argv[2]


def git(*args, **kw):
    return subprocess.run(["git", "-C", W6, *args], capture_output=True, **kw)


# -z：NUL 分隔且不做 C 风格引号转义（非 ASCII 路径必须用此方式取真名）
paths = [p.decode("utf-8") for p in
         git("ls-tree", "-r", "--name-only", "-z", rev).stdout.split(b"\x00") if p]
crlf = lf = other = mismatch = missing = 0
bad = []
for p in paths:
    blob = git("cat-file", "blob", f"{rev}:{p}").stdout
    try:
        with open(f"{repo}/{p}", "rb") as fh:
            wt = fh.read()
    except OSError:
        missing += 1
        bad.append(("MISSING", p))
        continue
    if wt == blob:
        conv = "LF"
    elif wt == blob.replace(b"\n", b"\r\n"):
        conv = "CRLF"
    else:
        conv = "CONTENT_DIFF"
        mismatch += 1
        bad.append((conv, p))
        continue
    if conv == "CRLF":
        crlf += 1
    elif conv == "LF":
        lf += 1
    else:
        other += 1
print(f"paths={len(paths)} LF={lf} CRLF={crlf} other={other} content_mismatch={mismatch} missing={missing}")
for kind, p in bad[:20]:
    print("  !!", kind, p)