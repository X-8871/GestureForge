#!/usr/bin/env python3
"""S3-T17 自证工具：逐文件比较「指定提交的 blob 字节」与「工作区字节」，并统计 CRLF。

用途（本仓库 core.autocrlf=true 会引入 CRLF/LF 口径差，曾导致哈希绑定失配）：
    证明证据包里 `hashes_sha256.txt` 记录的字节确实等于提交内字节；第三方可复跑。

用法：
    python -B scripts/stage3_t17/verify_t17_blob_identity.py [--commit <rev>] [--json-out f.json] \
        [--scope <dir>]... [--certify <被认证的 run 目录>]...
默认范围：`report/evidence/S3-T17/**`、`report/evidence/S3-CTRL/S3-T17/**`、`scripts/stage3_t17/**`
的文本文件（.json/.md/.txt/.py/.sh/.tcl）。
期望集合来自解析后的固定提交树，与工作区集合双向比较；缺文件、额外文件、每个空范围或空认证目录均失败。
二进制文件不在本工具认证范围内；--exclude 显式排除的路径也不在证书范围内。

范围断言（评审 B-2，**fail-closed**）：每个 `--certify <dir>` 必须被 `--scope` 覆盖（同路径或其后代）；
否则**拒绝给出结论**并以退出码 4 结束，明确打印 `SCOPE_ASSERTION_FAILED` 与未被覆盖的目录。
理由：曾出现「默认范围只含 S3-T17，却对外声称覆盖了本次窗口证据」的口径错误；断言使该错误无法静默通过。
每次运行都会打印生效范围与真实退出码（`SCOPE=...`、`CERTIFY=...`、`EXIT_CODE=...`）。

退出码：0 全部一致；1 存在不一致（列出路径）；2 参数/环境错误；3 自测失败；4 范围断言失败（fail-closed）。
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

def _force_utf8_streams() -> None:
    """强制 stdout/stderr 为 UTF-8 + LF（评审 R-1）。

    Windows 下 stdout 被重定向/管道时默认 `stdout_encoding=gbk`，非 GBK 字符会抛 UnicodeEncodeError，
    导致崩溃且不写 `--json-out`（而该退出码 1 与本工具 MISMATCH 同值，会被误读为哈希失配）。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError, OSError):
            pass


_force_utf8_streams()

UTC8 = timezone(timedelta(hours=8))
DEFAULT_SCOPES = (
    "report/evidence/S3-T17",
    "report/evidence/S3-CTRL/S3-T17",
    "scripts/stage3_t17",
)
TEXT_EXT = (".json", ".md", ".txt", ".py", ".sh", ".tcl")
DEFAULT_FIXTURE_DIR = "tmp/3/S3-T17/t17_verify_selftest_r01"


def _run_verify_cli(script: str, repo: str, json_out: str):
    """以**子进程 + 管道 stdout**运行一次本工具，复现「不设 PYTHONUTF8、非控制台 stdout」的常规调用；
    并显式 `PYTHONIOENCODING=gbk` 以复现 GBK 环境（评审 Q-5）。返回 (CompletedProcess, json_written)。"""
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "gbk"
    if os.path.exists(json_out):
        os.remove(json_out)
    cp = subprocess.run([sys.executable, "-B", script, "--repo-root", repo, "--commit", "HEAD",
                         "--scope", "scripts/stage3_t17",
                         "--json-out", json_out], capture_output=True, env=env)
    return cp, os.path.isfile(json_out)


def _make_old_form_mutant(script: str, dest: str) -> str:
    """复制本工具并还原**旧形态**（评审 R-1）：删掉入口 `_force_utf8_streams()` 调用，
    并把打印里的 ASCII 换回 U+21D2 => 该副本在 GBK 下必然崩溃。用于证明回归确有判别力。"""
    src = open(script, encoding="utf-8").read()
    src = src.replace("\n_force_utf8_streams()\n", "\n", 1)
    # 只对**打印那一行**注入 U+21D2：按行定位（`+ ("（true =>`），避免命中本模块内其它同类字面量。
    out = []
    for line in src.split("\n"):
        if line.lstrip().startswith('+ ("（true =>'):
            line = line.replace("=>", "\u21d2", 1)
        out.append(line)
    src = "\n".join(out)
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(src)
    return dest


def _scope_covers(scopes, path: str) -> str | None:
    """返回覆盖 path 的范围（同路径或祖先），无则 None。用于 fail-closed 范围断言。"""
    p = path.replace("\\", "/").strip("/")
    for scope in scopes:
        s = scope.replace("\\", "/").strip("/")
        if p == s or p.startswith(s + "/"):
            return s
    return None


def _run_verify_args(script: str, repo: str, extra: list, json_out: str | None = None):
    """以子进程运行本工具并返回 (CompletedProcess, json_written, stdout_text)。"""
    if json_out and os.path.exists(json_out):
        os.remove(json_out)
    argv = [sys.executable, "-B", script, "--repo-root", repo, "--commit", "HEAD"] + list(extra)
    if json_out:
        argv += ["--json-out", json_out]
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "gbk"
    cp = subprocess.run(argv, capture_output=True, env=env)
    return cp, (os.path.isfile(json_out) if json_out else False), cp.stdout.decode("utf-8", "replace")


def run_selftest(fixture_dir: str) -> dict:
    """CLI 级回归（评审 Q-5）：本工具**没有**第三重防护（打印在写 JSON 之前），故
    ① 正规路径在 GBK + 管道下必须 exit 0 且写 JSON；② 「旧形态」突变体必须被检出（非 0 退出或缺 JSON）。"""
    os.makedirs(fixture_dir, exist_ok=True)
    repo = os.path.join(fixture_dir, "selftest_repo")
    if not os.path.isdir(os.path.join(repo, ".git")):
        probe_dir = os.path.join(repo, "scripts", "stage3_t17")
        os.makedirs(probe_dir, exist_ok=True)
        with open(os.path.join(probe_dir, "probe.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("print('probe')\n")
        subprocess.run(["git", "init", "-q", repo], capture_output=True)
        subprocess.run(["git", "-C", repo, "add", "-A"], capture_output=True)
        subprocess.run(["git", "-C", repo, "-c", "user.email=t17@local", "-c", "user.name=t17",
                        "commit", "-q", "-m", "selftest probe"], capture_output=True)
    # 范围断言自测夹具（评审 B-2）：一个位于「自定义范围」下的 run 目录
    runfix_rel = "report/evidence/S3-T05/runfix_selftest_r01"
    runfix = os.path.join(repo, runfix_rel.replace("/", os.sep))
    os.makedirs(runfix, exist_ok=True)
    with open(os.path.join(runfix, "note.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("runfix selftest run dir\n")
    subprocess.run(["git", "-C", repo, "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", repo, "-c", "user.email=t17@local", "-c", "user.name=t17",
                    "commit", "-q", "-m", "selftest run dir"], capture_output=True)

    checks = []

    good_json = os.path.join(fixture_dir, "cli_verify_gbk.json")
    cp, json_ok = _run_verify_cli(os.path.abspath(__file__), repo, good_json)
    checks.append({
        "name": "cli_verify_gbk_exit0_json",
        "expectation": "exit 0 且 JSON 落盘（GBK + 管道下不崩）",
        "actual_exit_code": cp.returncode,
        "json_written": json_ok,
        "matched": cp.returncode == 0 and json_ok,
        "stderr_tail": cp.stderr[-200:].decode("utf-8", "replace"),
    })

    mutant = _make_old_form_mutant(os.path.abspath(__file__), os.path.join(fixture_dir, "verify_old_form.py"))
    mut_json = os.path.join(fixture_dir, "cli_verify_old_form.json")
    cp2, json_ok2 = _run_verify_cli(mutant, repo, mut_json)
    mtext = open(mutant, encoding="utf-8").read()
    # 自检突变是否真的打中**打印行**（否则会「突变没生效 => 假失败/假通过」）
    mutation_applied = ('+ ("（true \u21d2' in mtext) and ("\n_force_utf8_streams()\n" not in mtext)
    detected = (cp2.returncode != 0) or (not json_ok2)
    checks.append({
        "name": "mutant_old_form_detected",
        "expectation": "非 0 退出或未写 JSON（旧形态：无入口兜底 + 打印 U+21D2）",
        "actual_exit_code": cp2.returncode,
        "json_written": json_ok2,
        "mutation_applied": mutation_applied,
        "matched": mutation_applied and detected,
        "stderr_tail": cp2.stderr[-200:].decode("utf-8", "replace"),
    })

    # 评审 B-2 的 must-fail 回归：**范围不覆盖被认证 run 目录** ⇒ 必须 fail-closed（退出码 4，且不得给 PASS）
    bad_json = os.path.join(fixture_dir, "cli_scope_uncovered.json")
    cp3, json_ok3, out3 = _run_verify_args(
        os.path.abspath(__file__), repo,
        ["--scope", "scripts/stage3_t17", "--certify", runfix_rel], bad_json)
    checks.append({
        "name": "must_fail_scope_not_covering_certified_dir",
        "expectation": "退出码 4 且 stdout 不含 BLOB_BYTE_IDENTITY_OK（fail-closed 拒绝给结论）",
        "actual_exit_code": cp3.returncode,
        "json_written": json_ok3,
        "pass_verdict_in_stdout": "BLOB_BYTE_IDENTITY_OK" in out3,
        "matched": cp3.returncode == 4 and ("BLOB_BYTE_IDENTITY_OK" not in out3),
        "stdout_tail": out3[-220:],
    })

    # 正向对照：范围**覆盖**该 run 目录 ⇒ exit 0 且给出 PASS
    ok_json = os.path.join(fixture_dir, "cli_scope_covered.json")
    cp4, json_ok4, out4 = _run_verify_args(
        os.path.abspath(__file__), repo,
        ["--scope", "report/evidence/S3-T05", "--certify", runfix_rel], ok_json)
    checks.append({
        "name": "scope_covering_certified_dir_passes",
        "expectation": "退出码 0 且 stdout 含 BLOB_BYTE_IDENTITY_OK",
        "actual_exit_code": cp4.returncode,
        "json_written": json_ok4,
        "pass_verdict_in_stdout": "BLOB_BYTE_IDENTITY_OK" in out4,
        "matched": cp4.returncode == 0 and ("BLOB_BYTE_IDENTITY_OK" in out4),
        "stdout_tail": out4[-220:],
    })

    ok = all(item["matched"] for item in checks)
    return {
        "created_utc8": datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "conclusion": "SELFTEST_PASS" if ok else "SELFTEST_FAIL",
        "exit_code": 0 if ok else 3,
        "checks": checks,
        "fixture_dir": os.path.abspath(fixture_dir),
        "note": "本工具防护层次 = ①入口 UTF-8 reconfigure ②源码无 U+21D2（**无**第三重防护，打印在写 JSON 之前）；"
                "故旧形态突变体（去 ① + 恢复 U+21D2）在 GBK + 管道下必崩，回归可检出。",
    }


def git_show(repo: str, rev: str, path: str) -> bytes | None:
    cp = subprocess.run(["git", "--no-optional-locks", "-C", repo, "show", f"{rev}:{path}"],
                        capture_output=True)
    return cp.stdout if cp.returncode == 0 else None


def resolve_rev(repo: str, rev: str) -> str | None:
    cp = subprocess.run(["git", "--no-optional-locks", "-C", repo, "rev-parse", "--verify", f"{rev}^{{commit}}"],
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
    ap.add_argument("--certify", action="append", default=[],
                    help="必须被 --scope 覆盖的目录（如本次被认证的 run 目录，可重复）；"
                         "未被覆盖 ⇒ 退出码 4 且拒绝给结论（fail-closed，评审 B-2）")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--selftest", action="store_true",
                    help="CLI 级回归（评审 Q-5）：GBK+管道下必须 exit 0 且写 JSON，并能检出『旧形态』突变体")
    ap.add_argument("--fixture-dir", default=DEFAULT_FIXTURE_DIR, help="自测夹具目录（缓存，不入库）")
    args = ap.parse_args(argv)

    if args.selftest:
        result = run_selftest(args.fixture_dir)
        if args.json_out:
            os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
            with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"SELFTEST 结论={result['conclusion']} 退出码={result['exit_code']}")
        for item in result["checks"]:
            print("  %-30s 期望=%s 实际退出码=%s JSON=%s 匹配=%s" % (
                item["name"], item["expectation"], item["actual_exit_code"],
                item["json_written"], item["matched"]))
        if args.json_out:
            print(f"JSON_OUT={args.json_out}")
        return result["exit_code"]

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
    # 范围必须精确位于仓库内，禁止通过绝对路径或上级目录改变认证边界。
    for path in (*scopes, *args.certify, *args.exclude):
        normalized = path.replace("\\", "/")
        if (not normalized or normalized.startswith("/") or ":" in normalized
                or any(part in ("", ".", "..") for part in normalized.split("/"))):
            print(f"非法仓库相对路径：{path}")
            return 2
    excluded = {item.replace("\\", "/") for item in args.exclude}

    # 评审 B-2：fail-closed 范围断言——声明的范围必须覆盖每一个被认证目录，否则拒绝给结论。
    certified = [item.replace("\\", "/").strip("/") for item in args.certify]
    print(f"SCOPE={','.join(scopes)}")
    if certified:
        print(f"CERTIFY={','.join(certified)}")
    uncovered = [item for item in certified if _scope_covers(scopes, item) is None]
    if uncovered:
        print("SCOPE_ASSERTION_FAILED：声明范围未覆盖被认证目录 ⇒ 拒绝给出结论（fail-closed）")
        for item in uncovered:
            print(f"  UNCOVERED {item}")
        result = {
            "created_utc8": datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "repo_root": repo,
            "commit": rev,
            "scopes": list(scopes),
            "certified_dirs": certified,
            "uncovered_dirs": uncovered,
            "files_checked": 0,
            "verdict": "SCOPE_ASSERTION_FAILED",
            "note": "范围断言失败：本次运行不得被引用为任何范围的自证通过（评审 B-2）。",
        }
        if args.json_out:
            os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
            with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(result, fh, ensure_ascii=False, indent=2)
            print(f"JSON_OUT={args.json_out}")
        print("EXIT_CODE=4")
        return 4

    # 评审 N-4：本仓库 core.autocrlf=true 会让 clone 的工作区变 CRLF，使按 LF 记录的哈希全部不匹配。
    # 本工具只比较「提交 blob vs 工作区」；若工作区是 CRLF 检出，请改用 git -c core.autocrlf=false clone。
    autocrlf = subprocess.run(["git", "--no-optional-locks", "-C", repo, "config", "--get",
                              "core.autocrlf"], capture_output=True, text=True)
    autocrlf_value = (autocrlf.stdout or "").strip() or "(unset)"
    print(f"CORE_AUTOCRLF={autocrlf_value}"
          + ("（true => 若本仓库是 CRLF 检出的克隆，请用 git -c core.autocrlf=false clone 复核）"
             if autocrlf_value.lower() == "true" else ""))

    # 固定提交而非工作区遍历定义期望集合，防止删文件后出现空集或残缺集合假通过。
    tree = subprocess.run(["git", "--no-optional-locks", "-C", repo,
                           "ls-tree", "-r", "--full-tree", "-z", rev], capture_output=True)
    if tree.returncode != 0:
        print("固定提交树读取失败")
        return 2
    tree_files = set()
    for entry in tree.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        rel = raw_path.decode("utf-8")
        if metadata.split()[1] == b"blob" and rel.lower().endswith(TEXT_EXT):
            if _scope_covers(scopes, rel) is not None and rel not in excluded:
                tree_files.add(rel)
    empty_scopes = [s for s in scopes if not any(_scope_covers([s], p) for p in tree_files)]
    empty_certified = [s for s in certified if not any(_scope_covers([s], p) for p in tree_files)]
    files = set()
    for scope in scopes:
        root = os.path.join(repo, scope.replace("/", os.sep))
        for dirpath, _dirs, names in os.walk(root):
            for name in names:
                if name.lower().endswith(TEXT_EXT):
                    rel = os.path.relpath(os.path.join(dirpath, name), repo).replace("\\", "/")
                    if rel not in excluded:
                        files.add(rel)
    missing_worktree = sorted(tree_files - files)
    unexpected_worktree = sorted(files - tree_files)
    files = sorted(tree_files & files)

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
        "core_autocrlf": autocrlf_value,
        "commit": rev,
        "scopes": list(scopes),
        "certified_dirs": certified,
        "excluded_selfproof_artifacts": sorted(excluded),
        "files_checked": len(files),
        "expected_text_files": sorted(tree_files),
        "expected_file_count": len(tree_files),
        "missing_from_worktree": missing_worktree,
        "unexpected_in_worktree": unexpected_worktree,
        "empty_scopes": empty_scopes,
        "empty_certified_dirs": empty_certified,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "not_in_commit": missing,
        "crlf_files_in_worktree": crlf,
        "verdict": "BLOB_BYTE_IDENTITY_OK" if (tree_files and not mismatches and not missing
                    and not missing_worktree and not unexpected_worktree
                    and not empty_scopes and not empty_certified) else "BLOB_BYTE_IDENTITY_MISMATCH",
        "note": "逐文件比较 git blob 字节与工作区字节。本仓库 core.autocrlf=true：**未被 `-text` 覆盖**的范围里"
                "git 会把 CRLF 归一为 LF，故只有 `-text` 覆盖（如 report/evidence/S3-T05/**）的文件才保证"
                "「提交字节 == 原始字节」；对未覆盖范围，本工具的不一致是口径差而非证据损坏。",
    }
    print(f"提交={rev} 检查文件={len(files)} 不一致={len(mismatches)} 提交内缺失={len(missing)} 工作区含 CRLF={len(crlf)}")
    for item in mismatches:
        print("  MISMATCH %s" % item["path"])
    for rel in missing:
        print("  NOT_IN_COMMIT %s" % rel)
    for label, paths in (("MISSING_FROM_WORKTREE", missing_worktree),
                         ("UNEXPECTED_IN_WORKTREE", unexpected_worktree),
                         ("EMPTY_SCOPE", empty_scopes), ("EMPTY_CERTIFIED", empty_certified)):
        for rel in paths:
            print(f"  {label} {rel}")
    print(f"结论={result['verdict']}")
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
        print(f"JSON_OUT={args.json_out}")
    code = 0 if result["verdict"] == "BLOB_BYTE_IDENTITY_OK" else 1
    print(f"EXIT_CODE={code}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
