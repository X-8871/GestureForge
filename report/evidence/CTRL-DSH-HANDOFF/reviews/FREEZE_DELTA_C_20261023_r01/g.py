"""复核用 Git 助手（只读）。所有命令打印真实退出码。"""
import subprocess, sys, os

W6 = r"D:\codex-worktrees\w6"


def run(args, cwd=W6, text=True):
    p = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def show(args, label=None, cwd=W6):
    rc, out, err = run(args, cwd=cwd)
    print("$ git " + " ".join(args) + (f"   # {label}" if label else ""))
    print(f"[exit {rc}]")
    if out.strip():
        print(out.rstrip())
    if err.strip():
        print("STDERR:", err.rstrip())
    print("-" * 70)
    return rc, out, err


def run_plain(cmd, cwd=W6):
    """任意可执行文件；打印退出码。"""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("$ " + " ".join(cmd))
    print(f"[exit {p.returncode}]")
    if p.stdout.strip():
        print(p.stdout.rstrip())
    if p.stderr.strip():
        print("STDERR:", p.stderr.rstrip())
    print("-" * 70)
    return p.returncode, p.stdout, p.stderr