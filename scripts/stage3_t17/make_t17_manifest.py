#!/usr/bin/env python3
"""S3-T17 证据打包器：为一次实测生成 manifest.json 与 hashes_sha256.txt。

设计边界：
- 只在**证据目录内部**写 manifest.json / hashes_sha256.txt，不移动、不改写已有原始产物；
- manifest.json 已存在时默认拒绝覆盖（防止误覆盖上一轮 RunId），需要显式 --force；
- 退出码只接受调用方传入的**真实退出码**，本脚本不推断、不合成、不硬编码；
- 不把未测项写成通过：未在 --exit-code 中出现的阶段一律登记为 NOT_PROVIDED。

用法：
    python -B scripts/stage3_t17/make_t17_manifest.py \
        --evidence-dir report/evidence/S3-T17/t17_color_retest_20261023_r01 \
        --run-id t17_color_retest_20261023_r01 \
        --command "bash scripts/stage3_t17/run_t17_color_retest.sh all --allow-hardware" \
        --exit-code preflight=0 --exit-code baseline=1 \
        --limitation "未做电气测量" --not-run ">=30 分钟耐久"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

UTC8 = timezone(timedelta(hours=8))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head_commit(repo: str) -> str:
    try:
        cp = subprocess.run(["git", "--no-optional-locks", "rev-parse", "HEAD"], cwd=repo,
                            capture_output=True, text=True, check=False)
        return (cp.stdout or "").strip() if cp.returncode == 0 else ""
    except OSError:
        return ""


def main(argv):
    ap = argparse.ArgumentParser(description="S3-T17 证据打包器", allow_abbrev=False)
    ap.add_argument("--project-root", default=os.getcwd())
    ap.add_argument("--evidence-dir", required=True, help="相对 project-root 或绝对路径")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--task-id", default="S3-T17")
    ap.add_argument("--command", action="append", default=[], help="实际执行的命令（可重复）")
    ap.add_argument("--exit-code", action="append", default=[], help="阶段真实退出码 name=code（可重复）")
    ap.add_argument("--limitation", action="append", default=[], help="限制（可重复）")
    ap.add_argument("--not-run", action="append", default=[], help="未执行项（可重复）")
    ap.add_argument("--scope", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.project_root)
    evid = args.evidence_dir
    if not os.path.isabs(evid):
        evid = os.path.join(root, evid.replace("/", os.sep))
    if not os.path.isdir(evid):
        print(f"证据目录不存在：{evid}")
        return 2
    manifest_path = os.path.join(evid, "manifest.json")
    if os.path.exists(manifest_path) and not args.force:
        print(f"拒绝覆盖已有清单（需 --force）：{manifest_path}")
        return 3

    exit_codes = {}
    for item in args.exit_code:
        name, _, value = item.partition("=")
        if not name or not value:
            print(f"--exit-code 格式应为 name=code：{item}")
            return 2
        try:
            exit_codes[name] = int(value)
        except ValueError:
            print(f"--exit-code 的 code 必须是整数：{item}")
            return 2

    outputs = []
    for dirpath, _dirnames, filenames in os.walk(evid):
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, evid).replace("\\", "/")
            if rel in ("manifest.json", "hashes_sha256.txt"):
                continue
            outputs.append({"path": rel, "size_bytes": os.path.getsize(full), "sha256": sha256_file(full)})
    outputs.sort(key=lambda x: x["path"])

    manifest = {
        "schema_version": 1,
        "task_id": args.task_id,
        "run_id": args.run_id,
        "created_utc8": datetime.now(UTC8).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "source_commit": head_commit(root),
        "source_branch": "codex/stage3-video",
        "commands": args.command,
        "exit_codes": exit_codes,
        "outputs": outputs,
        "scope": args.scope or "阶段3 色彩复测证据；不代表 G0/G4/G5、独立审查或实物验收。",
        "limitations": args.limitation,
        "not_run": args.not_run,
        "note": "退出码为调用方传入的真实值；未列出的阶段即未执行（不得当作通过）。",
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    lines = [f"{item['sha256']}  {item['path']}" for item in outputs]
    if os.path.exists(manifest_path):
        lines.append(f"{sha256_file(manifest_path)}  manifest.json")
    with open(os.path.join(evid, "hashes_sha256.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"MANIFEST_OK={manifest_path} files={len(outputs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))