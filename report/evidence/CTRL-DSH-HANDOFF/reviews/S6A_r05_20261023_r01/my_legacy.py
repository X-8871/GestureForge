#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 5 轮评审：独立复现 s6a_rerun_legacy_failures.py 的 r04 重跑（只写隔离目录）。

- 用 git cat-file blob 二进制提取 b20b670 的 5 个文件到隔离目录；
- 用 r05 最终版自检重跑（--project-root 绝对路径，--evidence-dir 指向只读的 r04 证据目录）；
- 与入库 selfcheck_r04_failure.json / r04_package_under_test.json 逐项对比。
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
WORK = OUT / "legacy" / "r04"
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
R04_RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r04"
COMMIT = "b20b6705e8c7dd6c43cc2195860e3fc84e1c4ec7"


def git_blob(relpath: str) -> bytes:
    completed = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", f"{COMMIT}:{relpath}"],
                               capture_output=True, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"git cat-file 失败：{relpath}: {completed.stderr!r}")
    return completed.stdout


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    paths = {
        "behavior": "docs/stage6/s6a_stage6_g0_behavior_v1.json",
        "doc": "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
        "cases": "report/evidence/S6-A/s6a_g0_20261022_r04/hand_computed_cases.json",
        "bindings": "report/evidence/S6-A/s6a_g0_20261022_r04/upstream_bindings.json",
        "state": ".codex/STATE.md",
    }
    extracted: dict[str, Path] = {}
    hashes: dict[str, str] = {}
    lines: list[str] = []
    for key, rel in paths.items():
        payload = git_blob(rel)
        target = WORK / f"r04_{key}{Path(rel).suffix}"
        target.write_bytes(payload)
        extracted[key] = target
        hashes[rel] = sha(payload)
        lines.append(f"提取 {rel}\n  sha256(git 字节)={sha(payload)}  字节数={len(payload)}")

    result_path = OUT / "my_selfcheck_r04_bytes.json"
    command = [
        sys.executable, "-B", str(ROOT / "verification/s6_g0_selfcheck.py"),
        "--json", str(extracted["behavior"]), "--doc", str(extracted["doc"]),
        "--cases", str(extracted["cases"]), "--upstream", str(extracted["bindings"]),
        "--out", str(result_path), "--project-root", str(ROOT),
        "--evidence-dir", str(R04_RUN), "--state", str(extracted["state"]),
    ]
    completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    (OUT / "my_selfcheck_r04_bytes_stdout.txt").write_text(completed.stdout, encoding="utf-8")
    lines.append(f"\n[r05 自检 @ r04 git 字节] 真实退出码 = {completed.returncode}")
    mine = json.loads(result_path.read_text(encoding="utf-8"))
    theirs = json.loads((RUN / "selfcheck_r04_failure.json").read_text(encoding="utf-8"))
    lines.append(f"我的 status={mine['status']}  入库 status={theirs['status']}")
    mf = [(c["id"], c["detail"]) for c in mine["checks"] if c["status"] == "FAIL"]
    tf = [(c["id"], c["detail"]) for c in theirs["checks"] if c["status"] == "FAIL"]
    lines.append(f"我的 FAILED={[i for i, _ in mf]}")
    lines.append(f"入库 FAILED={[i for i, _ in tf]}")
    lines.append(f"FAILED 集合相同：{[i for i, _ in mf] == [i for i, _ in tf]}")
    lines.append(f"FAILED detail 逐字相同：{mf == tf}")
    for cid, det in mf:
        lines.append(f"  {cid}: {det}")
    same_status = [(c["id"], c["status"]) for c in mine["checks"]] == \
                  [(c["id"], c["status"]) for c in theirs["checks"]]
    lines.append(f"全部 17 项 id/status 相同：{same_status}")

    pkg = json.loads((RUN / "r04_package_under_test.json").read_text(encoding="utf-8"))
    lines.append("\n与入库 r04_package_under_test.json 的哈希对比：")
    for row in pkg["files_under_test"]:
        rel = row["path"]
        mine_hash = hashes.get(rel)
        lines.append(f"  {rel}: 入库={row['sha256']} 我算={mine_hash} "
                     f"{'一致' if mine_hash == row['sha256'] else '**不符**'}")

    lines.append(f"\n入库 selfcheck_r04_failure.json 的 inputs 与我提取文件的哈希对比：")
    for key, rel in paths.items():
        their_key = {"behavior": "behavior_json_sha256", "doc": "human_doc_sha256",
                     "cases": "hand_cases_sha256"}.get(key)
        if their_key:
            lines.append(f"  {their_key}: 我算={hashes[rel]} 入库="
                         f"{theirs['inputs'][their_key]} "
                         f"{'一致' if hashes[rel] == theirs['inputs'][their_key] else '**不符**'}")

    # r04 的 HC-29 是否含 window_span_ms（判断 C7 在 r04 上失败的真实原因）
    r04_cases = json.loads(extracted["cases"].read_text(encoding="utf-8"))
    by = {c["case_id"]: c for c in r04_cases["cases"]}
    lines.append(f"\nr04 样例数={len(r04_cases['cases'])}；HC-30 存在={'HC-30' in by}；"
                 f"HC-29.expected 键={sorted(by['HC-29']['expected'])}")
    lines.append(f"r04 HC-29 推导文字片段：{by['HC-29']['derivation'][:200]}")

    (OUT / "my_legacy.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())