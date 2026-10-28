"""阶段4 离线冻结集成员校验器（只读、fail-closed、可复跑）。S4-T33。

与 `verification/verify_stage4_frozen_set.py`（旧 F1–F8 语义校验器，保留供历史）不同：
本验证器校验的是**冻结集成员逐字节身份**，即 `frozen_set.json` 中每个成员的
`sha256` 是否等于 `git cat-file blob <hash_basis_commit>:<path>` 的实际字节哈希。

契约：
  · fail-closed：缺件 / 哈希不符 / 重复 id / 路径逃逸（绝对路径、`..`）⇒ 非 0；
  · `--selftest`：clean=0、改一字节=1、删一件=2、路径逃逸=2；
  · 成功输出 `FROZEN_SET_VERIFIED (N/N)`。

用法：
  python -B scripts/stage4_s4ctrl/verify_stage4_frozen_set.py \
      --repo D:/codex-worktrees/w4 \
      --frozen-set report/evidence/S4-FREEZE/stage4_freeze_20261028_r01/frozen_set.json
  python -B scripts/stage4_s4ctrl/verify_stage4_frozen_set.py --selftest

退出码：0=全部一致；1=哈希不符；2=输入/环境错误或结构违规。
本脚本不写任何被校验对象、不接触硬件、不启动服务。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_INPUT = 2


def git(repo: Path, *args: str) -> tuple[int, bytes]:
    """跑 git，返回 (退出码, stdout)。"""
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    return proc.returncode, proc.stdout


def blob_bytes(repo: Path, commit: str, rel: str) -> bytes | None:
    """按 commit:path 取 blob；不存在返回 None。"""
    code, out = git(repo, "cat-file", "blob", f"{commit}:{rel}")
    return out if code == 0 else None


def sha256(data: bytes) -> str:
    """字节 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def is_safe_relpath(rel: str) -> tuple[bool, str]:
    """仓库相对路径安全性（拒绝绝对路径、`..`、`.`、空段、反斜杠、NUL）。"""
    if not rel or "\x00" in rel:
        return False, "空路径或含 NUL"
    if rel.startswith("/") or rel.startswith("\\"):
        return False, "绝对路径"
    if "\\" in rel:
        return False, "含反斜杠（要求 POSIX 分隔）"
    p = PurePosixPath(rel)
    if p.is_absolute():
        return False, "绝对路径"
    if any(part in ("", ".", "..") for part in p.parts):
        return False, "含 '.' 或 '..' 段"
    return True, ""


def check_members(repo: Path, fs: dict) -> tuple[int, list[str], list[dict]]:
    """逐成员校验；返回 (退出码, 错误, 明细)。"""
    errors: list[str] = []
    details: list[dict] = []
    commit = fs.get("hash_basis_commit", "")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        return EXIT_INPUT, [f"hash_basis_commit 非 40 位小写 SHA：{commit!r}"], []
    code, _ = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if code != 0:
        return EXIT_INPUT, [f"hash_basis_commit 在仓库中不存在：{commit}"], []

    seen: dict[str, str] = {}
    duplicate = False
    escape = False
    for idx, item in enumerate(fs.get("members", [])):
        if not isinstance(item, dict):
            errors.append(f"members[{idx}] 不是对象")
            continue
        mid, rel, declared = item.get("id"), item.get("path"), item.get("sha256")
        if not isinstance(mid, str) or not mid:
            errors.append(f"members[{idx}] 缺 id")
            continue
        if mid in seen:
            duplicate = True
            errors.append(f"重复 id：{mid}（另一成员路径 {seen[mid]}）")
            continue
        seen[mid] = str(rel)
        if not isinstance(rel, str):
            errors.append(f"{mid}: 缺 path")
            continue
        ok, why = is_safe_relpath(rel)
        if not ok:
            escape = True
            errors.append(f"{mid}: 路径逃逸/不安全（{why}）：{rel!r}")
            continue
        if not isinstance(declared, str) or len(declared) != 64:
            errors.append(f"{mid}: sha256 非 64 位十六进制")
            continue
        data = blob_bytes(repo, commit, rel)
        if data is None:
            errors.append(f"{mid}: 在 {commit} 中缺件：{rel}")
            continue
        actual = sha256(data)
        details.append({"id": mid, "path": rel, "declared": declared, "actual": actual,
                        "bytes": len(data), "ok": actual == declared})
        if actual != declared:
            errors.append(f"{mid}: sha256 不符 {rel}（declared={declared[:12]}… actual={actual[:12]}…）")

    cats = fs.get("categories")
    if not isinstance(cats, dict):
        errors.append("缺 categories 分类表")
    else:
        covered: set[str] = set()
        for name, members in cats.items():
            if not isinstance(members, list):
                errors.append(f"categories.{name} 不是列表")
                continue
            covered.update(str(x) for x in members)
        for item in fs.get("members", []):
            if isinstance(item, dict) and str(item.get("id")) not in covered:
                errors.append(f"成员未归入任何分类：{item.get('id')}")
    for art in fs.get("artifact_identity", []):
        if not isinstance(art, dict):
            errors.append("artifact_identity 含非对象项")
            continue
        sha = art.get("sha256", "")
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            errors.append(f"artifact_identity[{art.get('name', '?')}] sha256 非 64 位小写十六进制")
    for nf in fs.get("not_frozen", []):
        if not isinstance(nf, dict) or "path" not in nf or "reason" not in nf:
            errors.append("not_frozen 项必须含 path 与 reason")

    missing = any("缺件" in e for e in errors)
    if duplicate or escape or missing:
        return EXIT_INPUT, errors, details
    if errors:
        return EXIT_MISMATCH, errors, details
    return EXIT_OK, [], details


def run_selftest() -> int:
    """自测四情形（临时 git 仓库，不触碰真实工作树）。"""
    with tempfile.TemporaryDirectory(prefix="s4freeze_selftest_") as td:
        repo = Path(td)
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "selftest@example.com")
        git(repo, "config", "user.name", "selftest")
        (repo / "a.txt").write_bytes(b"alpha\n")
        (repo / "b.txt").write_bytes(b"beta\n")
        git(repo, "add", "a.txt", "b.txt")
        git(repo, "commit", "-q", "-m", "selftest base")
        base = git(repo, "rev-parse", "HEAD")[1].decode().strip()
        members = [{"id": "a", "path": "a.txt", "sha256": sha256((repo / "a.txt").read_bytes())},
                   {"id": "b", "path": "b.txt", "sha256": sha256((repo / "b.txt").read_bytes())}]
        fs = {"schema_version": "stage4_frozen_set_v1", "hash_basis_commit": base,
              "members": members, "categories": {"selftest": ["a", "b"]},
              "artifact_identity": [], "not_frozen": []}

        clean, _, det = check_members(repo, fs)
        (repo / "a.txt").write_bytes(b"Alpha\n")
        git(repo, "add", "a.txt")
        git(repo, "commit", "-q", "-m", "one byte change")
        fs_changed = json.loads(json.dumps(fs))
        fs_changed["hash_basis_commit"] = git(repo, "rev-parse", "HEAD")[1].decode().strip()
        changed, _, _ = check_members(repo, fs_changed)
        (repo / "b.txt").unlink()
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "delete b")
        fs_deleted = json.loads(json.dumps(fs))
        fs_deleted["hash_basis_commit"] = git(repo, "rev-parse", "HEAD")[1].decode().strip()
        deleted, _, _ = check_members(repo, fs_deleted)
        fs_escape = {"schema_version": "stage4_frozen_set_v1", "hash_basis_commit": base,
                     "members": [{"id": "evil", "path": "../outside.txt", "sha256": "0" * 64}],
                     "categories": {"selftest": ["evil"]}, "artifact_identity": [], "not_frozen": []}
        escaped, _, _ = check_members(repo, fs_escape)

        got = [clean, changed, deleted, escaped]
        exp = [EXIT_OK, EXIT_MISMATCH, EXIT_INPUT, EXIT_INPUT]
        labels = ["clean", "one_byte_change", "deleted_member", "path_escape"]
        for label, g, e in zip(labels, got, exp):
            print(f"  [{('PASS' if g == e else 'FAIL')}] {label}: got={g} expected={e}")
        ok = got == exp
        print(f"SELFTEST_RESULT={'PASS' if ok else 'FAIL'} (members_clean={len(det)})")
        return EXIT_OK if ok else EXIT_MISMATCH


def main() -> int:
    """入口。"""
    ap = argparse.ArgumentParser(description="阶段4 冻结集成员校验器（只读、fail-closed）")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--frozen-set",
                    default="report/evidence/S4-FREEZE/stage4_freeze_20261028_r01/frozen_set.json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    repo = Path(args.repo).resolve()
    fs_path = Path(args.frozen_set)
    if not fs_path.is_absolute():
        fs_path = repo / fs_path
    if not repo.is_dir() or not fs_path.is_file():
        print(f"[FAIL] 输入缺失：repo={repo} frozen_set={fs_path}", file=sys.stderr)
        return EXIT_INPUT
    try:
        fs = json.loads(fs_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[FAIL] frozen_set 解析失败：{exc}", file=sys.stderr)
        return EXIT_INPUT
    if not isinstance(fs, dict):
        print("[FAIL] frozen_set 顶层必须是对象", file=sys.stderr)
        return EXIT_INPUT

    code, errors, details = check_members(repo, fs)
    total = len(fs.get("members", []))
    checked = sum(1 for d in details if d["ok"])
    if args.json:
        print(json.dumps({"frozen_set": str(fs_path), "hash_basis_commit": fs.get("hash_basis_commit"),
                          "members_total": total, "members_checked": checked,
                          "errors": errors, "exit_code": code}, ensure_ascii=False, indent=2))
    if code == EXIT_OK:
        print(f"FROZEN_SET_VERIFIED ({checked}/{total})")
        return EXIT_OK
    for e in errors[:40]:
        print(f"[FAIL] {e}", file=sys.stderr)
    if len(errors) > 40:
        print(f"[FAIL] 另有 {len(errors) - 40} 条未显示", file=sys.stderr)
    print(f"FROZEN_SET_BLOCKED ({checked}/{total})", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())