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


def disk_candidates(path: Path) -> list[bytes]:
    """磁盘字节候选（原始 + CRLF→LF 归一化），用于无 .git 的干净导出校验。"""
    if not path.is_file():
        return []
    raw = path.read_bytes()
    cands = [raw]
    if b"\r\n" in raw:
        cands.append(raw.replace(b"\r\n", b"\n"))
    return cands


PLACEHOLDER_FILL = 8  # 尾部连续 >=8 个 0 或 f ⇒ 判为占位形态


def looks_like_placeholder(hexstr: str) -> bool:
    """识别占位哈希：长度对但尾部连续 8+ 个 0/f，或前 8 位之后全同字符。"""
    if len(hexstr) != 64:
        return True
    tail0 = len(hexstr) - len(hexstr.rstrip("0"))
    tailf = len(hexstr) - len(hexstr.rstrip("f"))
    if tail0 >= PLACEHOLDER_FILL or tailf >= PLACEHOLDER_FILL:
        return True
    body = hexstr[8:]
    if body and len(set(body)) == 1:
        return True
    return False


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


def check_members(repo: Path, fs: dict, disk: bool = False) -> tuple[int, list[str], list[dict]]:
    """逐成员校验；返回 (退出码, 错误, 明细)。"""
    errors: list[str] = []
    details: list[dict] = []
    skipped_external: list[dict] = []
    commit = fs.get("hash_basis_commit", "")
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        return EXIT_INPUT, [f"hash_basis_commit 非 40 位小写 SHA：{commit!r}"], []
    if not disk:
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
        if disk:
            cands = disk_candidates(repo / rel)
            if not cands:
                errors.append(f"{mid}: 干净导出中缺件：{rel}")
                continue
            matched = next((c for c in cands if sha256(c) == declared), None)
            actual = sha256(matched) if matched is not None else sha256(cands[0])
            details.append({"id": mid, "path": rel, "declared": declared, "actual": actual,
                            "bytes": len(cands[0]), "ok": matched is not None, "mode": "disk"})
            if matched is None:
                errors.append(f"{mid}: sha256 不符 {rel}（disk/CRLF 归一化后仍不一致）")
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
        name = art.get("name", "?")
        sha = art.get("sha256", "")
        if art.get("status") == "NOT_VERIFIED":
            if not art.get("reason"):
                errors.append(f"artifact_identity[{name}] NOT_VERIFIED 必须写 reason")
            continue
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            errors.append(f"artifact_identity[{name}] sha256 非 64 位小写十六进制")
            continue
        if looks_like_placeholder(sha):
            errors.append(f"artifact_identity[{name}] 疑似占位哈希（尾部补零/补齐）：{sha}")
            continue
        apath = art.get("path")
        if not isinstance(apath, str) or not apath:
            errors.append(f"artifact_identity[{name}] 缺 path（必须给出可重算的文件路径）")
            continue
        target = Path(apath)
        if not target.is_absolute():
            target = repo / apath
        if disk and not target.is_file():
            # 干净导出内，仓库外产物不可用：明确记录跳过（不静默）
            skipped_external.append({"name": name, "path": apath, "reason": "导出环境不可达（仓库外产物）"})
            continue
        if not target.is_file():
            errors.append(f"artifact_identity[{name}] 文件不存在：{apath}")
            continue
        actual = sha256(target.read_bytes())
        declared_bytes = art.get("bytes")
        if declared_bytes is not None and target.stat().st_size != declared_bytes:
            errors.append(f"artifact_identity[{name}] 字节数不符 declared={declared_bytes} actual={target.stat().st_size}")
        if actual != sha:
            errors.append(f"artifact_identity[{name}] 重算哈希不符 declared={sha[:12]}… actual={actual[:12]}…")
    for nf in fs.get("not_frozen", []):
        if not isinstance(nf, dict) or "path" not in nf or "reason" not in nf:
            errors.append("not_frozen 项必须含 path 与 reason")

    missing = any("缺件" in e for e in errors)
    if skipped_external:
        for sk in skipped_external:
            print(f"[SKIP] artifact_identity[{sk['name']}] {sk['reason']}")
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
        fs_placeholder = {"schema_version": "stage4_frozen_set_v1", "hash_basis_commit": base,
                          "members": [], "categories": {},
                          "artifact_identity": [{"name": "fake", "sha256": "ea52da1b" + "0" * 56}],
                          "not_frozen": []}
        placeholder, _, _ = check_members(repo, fs_placeholder)
        fs_escape = {"schema_version": "stage4_frozen_set_v1", "hash_basis_commit": base,
                     "members": [{"id": "evil", "path": "../outside.txt", "sha256": "0" * 64}],
                     "categories": {"selftest": ["evil"]}, "artifact_identity": [], "not_frozen": []}
        escaped, _, _ = check_members(repo, fs_escape)

        got = [clean, changed, deleted, escaped, placeholder]
        exp = [EXIT_OK, EXIT_MISMATCH, EXIT_INPUT, EXIT_INPUT, EXIT_MISMATCH]
        labels = ["clean", "one_byte_change", "deleted_member", "path_escape", "placeholder_hash"]
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
    ap.add_argument("--disk", action="store_true", help="无 .git 的干净导出模式（磁盘字节 + CRLF 归一化）")
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

    disk_mode = args.disk or not (repo / ".git").exists()
    code, errors, details = check_members(repo, fs, disk=disk_mode)
    total = len(fs.get("members", []))
    checked = sum(1 for d in details if d["ok"])
    if args.json:
        print(json.dumps({"frozen_set": str(fs_path), "hash_basis_commit": fs.get("hash_basis_commit"),
                          "members_total": total, "members_checked": checked,
                          "mode": "disk" if disk_mode else "commit_blob",
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