#!/usr/bin/env python
"""从 main 的 OFFER 提交生成 w4 CLAIM 行（只读 main，不写任何仓库）。

用途：main 提交 `S4-B-REAL-02B::s4b_hardware_session_handoff` 后，本工具从该提交
取出 STATE blob 的 OID 与字节 SHA，并解析出 OFFER 行的「起始提交」，拼出 adapter
`_verify_handoff_reference_values` 要求的六键证据入口，打印可直接粘贴的 11 字段 CLAIM 行。

只读：仅执行 `git rev-parse` / `git show` / `git merge-base`，不写文件、不改仓库。

用法：
    python -B scripts/stage4_s4b/make_claim_line.py \
        --offer-commit <40位OFFER提交SHA> \
        --run-id s4b_ps_tensor_hw_20261027_r01

退出码：0 = 生成成功；1 = 输入不满足前置（如 OFFER 行缺失/不唯一）；2 = 环境/参数错误。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ_UTC8 = timezone(timedelta(hours=8))
OFFER_MARKER = "S4-B-REAL-02B::s4b_hardware_session_handoff"
STATE_PATH = ".codex/STATE.md"
SCOPE = "S4B_PS_TENSOR_DIAGNOSTIC"
FIELDS = ("任务", "负责人", "工作树/分支", "起始提交", "允许修改范围", "未提交改动归属",
          "让出声明", "心跳(UTC+8)", "证据入口", "恢复命令", "状态/下一接手方")


def git(repo: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout


def parse_rows(text: str) -> list[dict[str, str]]:
    rows = []
    for line in text.splitlines():
        start = line.find("任务=")
        if start < 0:
            continue
        parts = [p.strip() for p in line[start:].strip().strip("|").split("|")]
        if len(parts) != len(FIELDS):
            continue
        row, ok = {}, True
        for text_field, expected in zip(parts, FIELDS):
            key, sep, raw = text_field.partition("=")
            value = raw.strip()
            if not sep or key.strip() != expected or not (value.startswith("`") and value.endswith("`")):
                ok = False
                break
            row[expected] = value[1:-1]
        if ok and tuple(row) == FIELDS:
            rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="从 main OFFER 生成 w4 CLAIM 行（只读）")
    ap.add_argument("--main-repo", default=r"D:\FPGA_Competition")
    ap.add_argument("--offer-commit", required=True, help="承载 OFFER 行的 40 位提交 SHA")
    ap.add_argument("--run-id", required=True, help="与 OFFER 完全一致的 hardware_run_id")
    ap.add_argument("--w4-worktree", default=r"D:\codex-worktrees\w4")
    ap.add_argument("--w4-branch", default="stage4-infer-prep")
    ap.add_argument("--owner", default="Workbuddy 阶段4总控")
    ap.add_argument("--recovery-command", default=None)
    args = ap.parse_args(argv)

    repo = Path(args.main_repo)
    if not re.fullmatch(r"[0-9a-f]{40}", args.offer_commit):
        print("[ERROR] --offer-commit 不是 40 位小写 SHA", file=sys.stderr)
        return 2
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}", args.run_id):
        print("[ERROR] --run-id 字符集不合法", file=sys.stderr)
        return 2

    code, _ = git(repo, "cat-file", "-e", f"{args.offer_commit}^{{commit}}")
    if code != 0:
        print(f"[ERROR] main 中不存在该提交：{args.offer_commit}", file=sys.stderr)
        return 2

    code, blob_oid = git(repo, "rev-parse", "--verify", f"{args.offer_commit}:{STATE_PATH}")
    if code != 0:
        print(f"[ERROR] 该提交中缺少 {STATE_PATH}", file=sys.stderr)
        return 2
    blob_oid = blob_oid.strip()

    code, raw = git(repo, "show", f"{args.offer_commit}:{STATE_PATH}")
    if code != 0 or not raw:
        print("[ERROR] 无法读取该提交的 STATE 字节", file=sys.stderr)
        return 2
    state_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    rows = [r for r in parse_rows(raw) if OFFER_MARKER in r["任务"]]
    if len(rows) != 1:
        print(f"[FAIL] 该提交中 {OFFER_MARKER} 行数量为 {len(rows)}（必须恰好 1 行）", file=sys.stderr)
        return 1
    offer = rows[0]
    if offer["允许修改范围"] != SCOPE:
        print(f"[FAIL] OFFER scope 为 {offer['允许修改范围']!r}，必须精确 {SCOPE}", file=sys.stderr)
        return 1

    offer_start = offer["起始提交"]
    code, resolved = git(repo, "rev-parse", "--verify", f"{offer_start}^{{commit}}")
    if code != 0 or resolved.strip() != offer_start:
        print(f"[FAIL] OFFER 起始提交不是真实提交：{offer_start}", file=sys.stderr)
        return 1

    evidence = (f"offer_commit={args.offer_commit};offer_blob_oid={blob_oid};"
                f"offer_sha256={state_sha};offer_source_commit={offer_start};"
                f"hardware_run_id={args.run_id};scope={SCOPE}")

    now = datetime.now(TZ_UTC8).isoformat(timespec="seconds")
    recovery = args.recovery_command or (
        "git --no-optional-locks -C D:/codex-worktrees/w4 rev-parse HEAD; "
        "python -B -X utf8 verification/check_s4t26_g0_inputs.py --run-id <新RunId> --accept-producer-break")

    values = {
        "任务": f"S4-B-REAL-02B::{OFFER_MARKER.split('::')[1].replace('handoff', 'claim')}",
        "负责人": args.owner,
        "工作树/分支": f"{args.w4_worktree} / {args.w4_branch}",
        "起始提交": git(repo, "rev-parse", "HEAD")[1].strip() if False else offer_start,
        "允许修改范围": SCOPE,
        "未提交改动归属": "main OFFER 引用的未提交改动归属保持原口径；w4 侧仅本轮新增证据归 Workbuddy 阶段4总控",
        "让出声明": "CLAIMED",
        "心跳(UTC+8)": now,
        "证据入口": evidence,
        "恢复命令": recovery,
        "状态/下一接手方": f"CLAIMED {args.owner}",
    }
    # claim 的起始提交应为本行写入前的 w4 HEAD（由调用方在提交时替换），这里先给占位说明
    values["起始提交"] = "<w4 本行写入前的 HEAD 40 位 SHA>"

    line = " | ".join(f"{k}=`{values[k]}`" for k in FIELDS)
    print("=== 可直接粘贴到 w4 .codex/STATE.md 的 CLAIM 行 ===")
    print(line)
    print()
    print("=== 绑定值（供核对） ===")
    print(f"offer_commit      = {args.offer_commit}")
    print(f"offer_blob_oid    = {blob_oid}")
    print(f"offer_sha256      = {state_sha}")
    print(f"offer_source_commit = {offer_start}")
    print(f"hardware_run_id   = {args.run_id}")
    print()
    print("注意：CLAIM 的「起始提交」必须是本行写入前的 w4 HEAD；心跳须在 1 小时内被执行校验读取。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        print(f"[ERROR] 未预期错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
