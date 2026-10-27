#!/usr/bin/env python
"""生成 main 侧硬件 OFFER 行（只读 main，不写任何仓库）。

背景：阶段4 硬件执行要求 main 在 main 的 `.codex/STATE.md` 提交**唯一一行**
`S4-B-REAL-02B::s4b_hardware_session_handoff` OFFER。阶段4 不得写 main，因此本工具只负责
把该行按 adapter 的字段要求**精确生成并自校验**，由 main 侧粘贴提交。

本工具做的事：
  1. 读 main 当前 HEAD 与分支，取「起始提交」（OFFER 提交的父提交）；
  2. 读 w4 STATE 的写权负责人，拼出 `OFFERED <负责人>`；
  3. 用 adapter 自己的解析/判定函数**离线自校验**这一行（不写盘），确保粘上去就能过；
  4. 打印可直接粘贴的行，以及提交后应执行的下一步命令。

只读：仅 `git rev-parse` / `git show` / 读文件。绝不写 main、不 commit、不碰硬件。

用法：
    python -B scripts/stage4_s4b/make_offer_line.py \
        --run-id s4b_ps_tensor_hw_20261027_r01

退出码：0 = 生成且自校验通过；1 = 前置不满足（main 不可达/分支不对/w4 写权行缺失）；2 = 参数错误。
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

TZ_UTC8 = timezone(timedelta(hours=8))
MAIN_ROOT = Path(r"D:\FPGA_Competition")
W4_ROOT = Path(r"D:\codex-worktrees\w4")
OFFER_MARKER = "S4-B-REAL-02B::s4b_hardware_session_handoff"
SCOPE = "S4B_PS_TENSOR_DIAGNOSTIC"
FIELDS = ("任务", "负责人", "工作树/分支", "起始提交", "允许修改范围", "未提交改动归属",
          "让出声明", "心跳(UTC+8)", "证据入口", "恢复命令", "状态/下一接手方")


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.stdout.strip()


def load_adapter() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "s4b_adapter_for_offer", W4_ROOT / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["s4b_adapter_for_offer"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    if not (MAIN_ROOT / ".git").exists():
        print(f"[FAIL] main 仓库不可达：{MAIN_ROOT}", file=sys.stderr)
        return 1

    branch = git(MAIN_ROOT, "rev-parse", "--abbrev-ref", "HEAD")
    head = git(MAIN_ROOT, "rev-parse", "HEAD")
    if branch != "main":
        print(f"[FAIL] main 当前分支为 {branch}，必须切到 main 再提交 OFFER", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        print(f"[FAIL] 无法取 main HEAD：{head!r}", file=sys.stderr)
        return 1

    # main 工作树应干净：OFFER 提交只应新增本行
    dirty = git(MAIN_ROOT, "status", "--porcelain")
    dirty_lines = [ln for ln in dirty.splitlines() if ln.strip()]

    adapter = load_adapter()
    w4_state = (W4_ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
    try:
        stage_owner = adapter._state_stage_owner(w4_state)
    except Exception as exc:  # noqa: BLE001 - 写权行缺失属前置不满足
        print(f"[FAIL] w4 STATE 写权行不可解析：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    heartbeat = datetime.now(TZ_UTC8).strftime("%Y-%m-%d %H:%M")
    values = {
        "任务": OFFER_MARKER,
        "负责人": "DSH",
        "工作树/分支": f"{MAIN_ROOT} / main",
        "起始提交": head,
        "允许修改范围": SCOPE,
        "未提交改动归属": "无（main 工作树干净，OFFER 提交仅新增本行）" if not dirty_lines
                          else f"存在 {len(dirty_lines)} 项未提交改动，提交 OFFER 前须先清理或登记归属",
        "让出声明": "OFFERED",
        "心跳(UTC+8)": heartbeat,
        "证据入口": f"hardware_run_id={args.run_id}",
        "恢复命令": (f"git --no-optional-locks -C {MAIN_ROOT} rev-parse HEAD; "
                     f"python -B {W4_ROOT}/scripts/stage4_s4b/make_claim_line.py "
                     f"--offer-commit <本OFFER提交SHA> --run-id {args.run_id}"),
        "状态/下一接手方": f"OFFERED {stage_owner}",
    }
    line = " | ".join(f"{k}=`{values[k]}`" for k in FIELDS)

    # ---- 用 adapter 自己的解析器离线自校验（不写盘）----
    ok, rows = adapter._parse_state_handoff_rows((line + "\n").encode("utf-8"))
    problems: list[str] = []
    if not ok or len(rows) != 1:
        problems.append(f"解析失败：ok={ok} rows={len(rows)}")
    else:
        row = rows[0]
        if tuple(row) != FIELDS:
            problems.append(f"字段集合/顺序不符：{tuple(row)}")
        if row.get("负责人") != adapter.HANDOFF_TRUSTED_SENDER:
            problems.append("负责人必须为 DSH")
        if row.get("允许修改范围") != SCOPE:
            problems.append(f"scope 必须为 {SCOPE}")
        if row.get("让出声明") != "OFFERED":
            problems.append("让出声明必须为 OFFERED")
        if row.get("状态/下一接手方") != f"OFFERED {stage_owner}":
            problems.append("状态/下一接手方必须为 'OFFERED <w4写权负责人>'")
        if row.get("工作树/分支") != f"{adapter.HANDOFF_TRUSTED_SOURCE_ROOT} / {adapter.HANDOFF_TRUSTED_SOURCE_BRANCH}":
            problems.append("工作树/分支必须精确为 D:\\FPGA_Competition / main")
        if not re.fullmatch(r"[0-9a-f]{40}", row.get("起始提交", "")):
            problems.append("起始提交必须是 40 位提交 SHA")
        if not row.get("恢复命令"):
            problems.append("恢复命令不得为空")
        # 唯一性：main 当前不应已存在同标记行
        _, existing = adapter._parse_state_handoff_rows((MAIN_ROOT / ".codex/STATE.md").read_bytes())
        dup = [r for r in existing if r.get("任务") == OFFER_MARKER]
        if dup:
            problems.append(f"main STATE 已存在 {len(dup)} 条同标记行，OFFER 必须唯一（先撤销旧的）")

    print("=" * 78)
    print("main 侧要提交的 OFFER 行（整行复制，追加到 main 的 .codex/STATE.md 顶部状态区）")
    print("=" * 78)
    print(line)
    print("=" * 78)
    print(f"main 分支={branch}  HEAD={head[:12]}  心跳={heartbeat}  w4 写权负责人={stage_owner}")
    if dirty_lines:
        print(f"[WARN] main 工作树有 {len(dirty_lines)} 项未提交改动：")
        for ln in dirty_lines[:8]:
            print(f"       {ln}")
    if problems:
        print("[FAIL] 自校验未通过：")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("[OK] 自校验通过：字段齐备、顺序正确、角色/scope/状态符合 adapter 判定要求")
    print()
    print("提交（在 main 执行，不要带上其他文件）：")
    print(f'  git -C "{MAIN_ROOT}" add -- .codex/STATE.md')
    print(f'  git -C "{MAIN_ROOT}" commit -m "chore(stage4): offer hardware window to w4 '
          f'({args.run_id})"')
    print()
    print("提交后立刻（1 小时内有效）：")
    print(f"  python -B {W4_ROOT}/scripts/stage4_s4b/make_claim_line.py "
          f"--offer-commit <OFFER提交SHA> --run-id {args.run_id}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
