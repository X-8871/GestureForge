#!/usr/bin/env python3
"""r01/r02/r03 旧包失败证据的可复现重跑（S6-A r04 / N03）。

对每个历史修订：
  1) 用 `git cat-file blob <commit>:<path>` 的**二进制输出**提取该修订的行为表 JSON、
     规格 MD、hand_computed_cases.json、upstream_bindings.json 与 .codex/STATE.md；
     全程不经过任何文本管道，避免行尾/编码被改写（BLK-2 / N05）；
  2) 对 git 字节计算 SHA-256，写入 `<tag>_package_under_test.json`；
  3) 用**当前最终版** verification/s6_g0_selfcheck.py 在同一字节上重跑；
  4) 断言退出码必须为 1（加固自检必须捕获旧缺陷），否则本脚本失败——
     失败输出落盘为 `selfcheck_<tag>_failure.json` 与 `..._stdout.txt`。

用法：
    python -B verification/s6a_rerun_legacy_failures.py \
        --run-dir report/evidence/S6-A/s6a_g0_20261022_r04 \
        --project-root D:/codex-worktrees/w6

退出码：0=三份旧包均按预期失败并落盘；1=出现非预期结果（含"旧包竟然通过"）；2=输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

LEGACY = [
    {
        "label": "r01",
        "tag": "old",
        "commit": "1fe4648cba5a9f1ffc87dbe21cea732b72716bff",
        "evidence_run": "s6a_g0_20261022_r01",
        "package_out": "old_package_under_test.json",
        "failure_json": "selfcheck_old_package_failure.json",
        "failure_txt": "selfcheck_old_package_failure_stdout.txt",
        "artifact": "s6a_old_package_under_test",
        "purpose": "用 r01 真实字节证明加固自检能捕获旧缺陷；r03 同时修正 r02 的哈希绑定错误（BLK-2）。",
    },
    {
        "label": "r02",
        "tag": "r02",
        "commit": "3b59674f93e8a2c020a0670fa475ee6a15330833",
        "evidence_run": "s6a_g0_20261022_r02",
        "package_out": "r02_package_under_test.json",
        "failure_json": "selfcheck_r02_blk1_failure.json",
        "failure_txt": "selfcheck_r02_blk1_failure_stdout.txt",
        "artifact": "s6a_r02_package_under_test",
        "purpose": "r02 被检版本字节与哈希；加固自检的 C12 必须在 r02 上捕获 BLK-1（predicates.used_by 未登记 M3）。",
    },
    {
        "label": "r03",
        "tag": "r03",
        "commit": "2ce290f495e3bd50b249158be9f4f876a5f8e3fb",
        "evidence_run": "s6a_g0_20261022_r03",
        "package_out": "r03_package_under_test.json",
        "failure_json": "selfcheck_r03_failure.json",
        "failure_txt": "selfcheck_r03_failure_stdout.txt",
        "artifact": "s6a_r03_package_under_test",
        "purpose": "r03 被检版本字节与哈希；加固自检的 C12 必须在 r03 上捕获 R3-B01（禁用标识符 / §12 谓词残留）"
                   "与 R3-B02（predicates.used_by ↔ predicates_used 非双向、B03/B17 缺字段、B14 反向缺），"
                   "C17 必须捕获缺失的 stable_latching。",
    },
]

HASH_ERROR_EXPLANATION = (
    "r02 的旧包哈希曾用 PowerShell 文本管道提取（git show | Set-Content -Encoding utf8）直接改写字节："
    "LF→CRLF 且文件末尾被补 CRLF，故 5/5 哈希与 git 对象不符（复评 BLK-2；成因措辞按 N05 更正，不再声称“编码”被改写）。"
    "本文件一律改为 git cat-file blob 二进制提取，SHA-256 直接对 git 字节计算；失败结论（exit 1）不变。"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_blob(commit: str, relpath: str, root: Path) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", f"{commit}:{relpath}"],
        capture_output=True, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"无法取到 {commit}:{relpath}：{completed.stderr.decode('utf-8', 'replace').strip()}"
        )
    return completed.stdout


def legend_paths(evidence_run: str) -> dict[str, str]:
    base = f"report/evidence/S6-A/{evidence_run}"
    return {
        "behavior": "docs/stage6/s6a_stage6_g0_behavior_v1.json",
        "doc": "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
        "cases": f"{base}/hand_computed_cases.json",
        "bindings": f"{base}/upstream_bindings.json",
        "state": ".codex/STATE.md",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="r01/r02/r03 旧包失败证据可复现重跑（N03）")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--selfcheck", default="verification/s6_g0_selfcheck.py")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"运行目录不存在：{run_dir}")
        return 2
    run_id = run_dir.name
    selfcheck = (root / args.selfcheck).resolve()
    if not selfcheck.is_file():
        print(f"缺少自检脚本：{selfcheck}")
        return 2

    work_root = root / "tmp/6/S6-A" / run_id / "legacy"
    work_root.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, Any]] = []
    for item in LEGACY:
        commit = item["commit"]
        paths = legend_paths(item["evidence_run"])
        work = work_root / item["label"]
        work.mkdir(parents=True, exist_ok=True)

        extracted: dict[str, Path] = {}
        file_rows: list[dict[str, str]] = []
        for key, relpath in paths.items():
            try:
                payload = git_blob(commit, relpath, root)
            except RuntimeError as exc:
                print(f"[{item['label']}] {exc}")
                return 2
            target = work / f"{item['tag']}_{key}{Path(relpath).suffix}"
            target.write_bytes(payload)
            extracted[key] = target
            file_rows.append({
                "path": relpath,
                "git_ref": f"{commit}:{relpath}",
                "extracted_copy": target.relative_to(root).as_posix(),
                "sha256": sha256_bytes(payload),
                "extraction": "git cat-file blob <commit>:<path> 的二进制输出直接 write_bytes（无文本/换行转换）",
            })

        evidence_dir = root / f"report/evidence/S6-A/{item['evidence_run']}"
        result_path = run_dir / item["failure_json"]
        command = [
            sys.executable, "-B", str(selfcheck),
            "--json", str(extracted["behavior"]),
            "--doc", str(extracted["doc"]),
            "--cases", str(extracted["cases"]),
            "--upstream", str(extracted["bindings"]),
            "--out", str(result_path),
            "--project-root", str(root),
            "--evidence-dir", str(evidence_dir),
        ]
        if extracted["state"].is_file():
            command += ["--state", str(extracted["state"])]
        completed = subprocess.run(
            command, cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False,
        )
        (run_dir / item["failure_txt"]).write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 1:
            print(f"[{item['label']}] 预期 exit 1，实测 {completed.returncode}")
            print(completed.stdout)
            print(completed.stderr)
            return 1

        result = json.loads(result_path.read_text(encoding="utf-8"))
        failed_checks = [check["id"] for check in result["checks"] if check["status"] == "FAIL"]
        actual_files = sorted(
            path.relative_to(evidence_dir).as_posix()
            for path in evidence_dir.rglob("*")
            if path.is_file()
        ) if evidence_dir.is_dir() else []
        package = {
            "schema_version": 1,
            "artifact": item["artifact"],
            "task_id": "S6-A",
            "run_id": run_id,
            "purpose": item["purpose"],
            "git_commit": commit,
            "files_under_test": file_rows,
            "evidence_dir_under_test": {
                "path": f"report/evidence/S6-A/{item['evidence_run']}",
                "actual_files": actual_files,
            },
            "expected_outcome": "FAILED（exit 1）",
            "observed": {
                "command": subprocess.list2cmdline(command),
                "exit_code": completed.returncode,
                "status": result["status"],
                "failed_checks": failed_checks,
                "failure_json": item["failure_json"],
                "failure_stdout": item["failure_txt"],
            },
            "extraction_policy": "git cat-file blob 二进制输出直接落盘；SHA-256 对 git 字节计算（N03/N05）",
        }
        if item["label"] == "r01":
            package["r02_hash_error_explanation"] = HASH_ERROR_EXPLANATION
        (run_dir / item["package_out"]).write_text(
            json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        summary.append({
            "label": item["label"],
            "exit_code": completed.returncode,
            "status": result["status"],
            "failed_checks": failed_checks,
            "package": item["package_out"],
        })

    print(json.dumps({"status": "LEGACY_RERUN_OK", "results": summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())