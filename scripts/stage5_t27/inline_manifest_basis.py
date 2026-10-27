#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T27 清单**内联哈希基座**定稿（`commit_blob`，符合项目级新规 + 已打补丁的检查器 HL-T79）。

作用
====
1. `delivery_manifest.json` 清单级写入 `hash_basis="commit_blob"`、`hash_basis_commit=<40 位真实 SHA>`、
   `hash_basis_note`；`files[]` 逐项写入 `hash_basis="commit_blob"`；
2. 可选删除伴生基座表 `hash_basis_manifest.json` 与索引 `hashes_sha256.txt`（及其清单条目），
   避免"两文件漂移"与自引用循环——清单本身即权威哈希表；
3. 在写盘后实跑三套门禁并记录真实退出码：
   - `check_stage_delivery --mode evidence`（期望 0）
   - `check_manifest_hash_basis --mode strict`（`--commit <basis_commit>`，期望 0）
   - `check_manifest_hash_basis --mode declared-only`（同上，期望 0）

`hash_basis_commit` 语义：**承载 `files[]` 所列全部字节的提交**（清单自身不入 `files[]`，故其字节不上卷）。
脚本会断言：basis_commit 非符号引用、40 位小写 SHA，且每个条目在该提交下都能取到 blob 并与声明值一致
（不一致即 fail-closed，不写盘）。

退出码：0 = 写盘后三套门禁均 0；1 = 有不一致/门禁失败；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
GATE = pathlib.Path("D:/FPGA_Competition/verification/check_manifest_hash_basis.py")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def run(cmd: list[str]) -> dict:
    completed = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": " ".join(cmd), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def git_blob(commit: str, rel: str) -> bytes | None:
    completed = subprocess.run(["git", "--no-optional-locks", "-C", str(REPO_ROOT),
                                "cat-file", "blob", f"{commit}:{rel}"], capture_output=True)
    return completed.stdout if completed.returncode == 0 else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--basis-commit", required=True)
    parser.add_argument("--drop-companion", action="store_true")
    parser.add_argument("--drop-hashes", action="store_true")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    if not SHA_RE.match(args.basis_commit):
        print(f"[ENV_ERROR] basis_commit 必须是 40 位小写 SHA（实际 {args.basis_commit!r}）", file=sys.stderr)
        return 2
    run_dir = pathlib.Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = REPO_ROOT / run_dir
    manifest_path = run_dir / "delivery_manifest.json"
    if not manifest_path.is_file():
        print(f"[ENV_ERROR] 清单缺失：{manifest_path}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        print("[ENV_ERROR] 清单没有 files[] 条目", file=sys.stderr)
        return 2

    drop_paths: set[str] = set()
    if args.drop_companion:
        drop_paths.add((run_dir / "hash_basis_manifest.json").relative_to(REPO_ROOT).as_posix())
    if args.drop_hashes:
        drop_paths.add((run_dir / "hashes_sha256.txt").relative_to(REPO_ROOT).as_posix())
    entries = [e for e in entries if str(e.get("path", "")).replace("\\", "/") not in drop_paths]

    # 预检：每个条目的声明值必须等于 basis_commit 下的 blob（fail-closed，不写盘）
    mismatches, missing = [], []
    for entry in entries:
        rel = str(entry["path"]).replace("\\", "/")
        data = git_blob(args.basis_commit, rel)
        if data is None:
            missing.append(rel)
            continue
        actual = hashlib.sha256(data).hexdigest()
        if actual != str(entry["sha256"]).lower():
            mismatches.append({"path": rel, "declared": entry["sha256"], "actual": actual})
    if missing or mismatches:
        payload = {"missing": missing, "mismatches": mismatches,
                   "note": "basis_commit 未承载这些字节 ⇒ 拒绝写盘（fail-closed）"}
        if args.json_out:
            pathlib.Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    for path in drop_paths:                       # 删除降级/循环文件
        target = REPO_ROOT / path
        if target.is_file():
            target.unlink()
    for entry in entries:
        entry["hash_basis"] = "commit_blob"
    manifest["files"] = entries
    manifest["hash_basis"] = "commit_blob"
    manifest["hash_basis_commit"] = args.basis_commit
    manifest["hash_basis_note"] = (
        f"内联基座：files[] 每项按 `git cat-file blob {args.basis_commit[:12]}:<path>` 的权威字节核对；"
        "hash_basis_commit 为承载这些字节的提交，禁止符号引用。清单本身不入 files[]，其字节不上卷。")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rel_manifest = manifest_path.relative_to(REPO_ROOT).as_posix()
    checker = run([sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                   "--project-root", str(REPO_ROOT), "--manifest", str(manifest_path)])
    strict = run([sys.executable, "-B", str(GATE), "--repo", str(REPO_ROOT), "--commit", args.basis_commit,
                  "--paths", rel_manifest, "--mode", "strict", "--json"])
    declared = run([sys.executable, "-B", str(GATE), "--repo", str(REPO_ROOT), "--commit", args.basis_commit,
                    "--paths", rel_manifest, "--mode", "declared-only", "--json"])
    summary = {
        "manifest": rel_manifest, "basis_commit": args.basis_commit,
        "entries": len(entries), "dropped": sorted(drop_paths),
        "gates": {"check_stage_delivery_evidence": checker["exit_code"],
                  "hash_basis_strict": strict["exit_code"],
                  "hash_basis_declared_only": declared["exit_code"]},
        "gate_stdout": {"strict": strict["stdout"].strip()[-600:],
                        "declared": declared["stdout"].strip()[-400:],
                        "checker": checker["stdout"].strip()[:300]},
    }
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    ok = all(code == 0 for code in summary["gates"].values())
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())