#!/usr/bin/env python
"""生成 hardware_session_handoff 门禁记录（只读 Git，不写任何仓库）。

上游：main 已提交 OFFER 行，w4 已提交 CLAIM 行。
本工具从这两个提交的 `.codex/STATE.md` blob 取真实 Git 身份，按 adapter 要求的
`authority_source` / `claim_source` 结构生成 `hardware_session_handoff.json`。

判定权不在本脚本：生成后必须由 `check_hardware_gate_readiness.py`（内部调用
`s4b_ps_tensor_adapter.validate_hardware_gates`）复核。本脚本只负责"取真实身份 + 组装"。

只读：仅 `git rev-parse` / `git show` / `git cat-file` 与读文件。不 commit、不写 main、不碰硬件。

用法：
    python -B scripts/stage4_s4b/make_handoff_record.py \
        --offer-commit <main OFFER 提交> \
        --claim-commit <w4 CLAIM 提交> \
        --hardware-run-id s4b_ps_tensor_hw_20261027_r01 \
        --out-dir report/evidence/S4-B/s4b_hw_handoff_<RunId>

退出码：0 = 记录已生成；1 = 前置不满足（OFFER/CLAIM 缺失或身份不符）；2 = 参数/环境错误。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType

TZ_UTC8 = timezone(timedelta(hours=8))
WORKTREE = Path(__file__).resolve().parents[2]
W4_ROOT = Path(r"D:\codex-worktrees\w4")
MAIN_ROOT = Path(r"D:\FPGA_Competition")


def load_adapter() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "s4b_adapter_for_handoff", W4_ROOT / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["s4b_adapter_for_handoff"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offer-commit", required=True)
    ap.add_argument("--claim-commit", required=True)
    ap.add_argument("--hardware-run-id", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (WORKTREE / out_dir).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 输出目录已存在且非空：{out_dir}", file=sys.stderr)
        return 2

    adapter = load_adapter()
    snap = adapter._git_record_snapshot_at_commit

    # ---- 1) main 侧 OFFER blob ----
    try:
        offer_ctx = snap(adapter.HANDOFF_TRUSTED_SOURCE_ROOT, adapter.HANDOFF_SOURCE_PATH,
                         args.offer_commit)
    except Exception as exc:  # noqa: BLE001 - 提交不可达/分支不符都属前置不满足
        print(f"[FAIL] 无法从 main 取 OFFER 提交的 STATE blob：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    authority_source = {k: offer_ctx[k] for k in
                        ("worktree", "branch", "commit", "path", "blob_oid", "sha256")}
    authority_source["kind"] = adapter.HANDOFF_SOURCE_KIND

    # ---- 2) w4 侧 CLAIM blob ----
    try:
        claim_ctx = snap(W4_ROOT, adapter.HANDOFF_SOURCE_PATH, args.claim_commit)
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] 无法从 w4 取 CLAIM 提交的 STATE blob：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    claim_source = {k: claim_ctx[k] for k in
                    ("worktree", "branch", "commit", "path", "blob_oid", "sha256")}
    claim_source["kind"] = adapter.HANDOFF_CLAIM_SOURCE_KIND

    # ---- 3) 预检：两行必须各自唯一且标记正确（只报事实，不做放行判断）----
    _, offer_rows = adapter._parse_state_handoff_rows(offer_ctx["state_raw"])
    _, claim_rows = adapter._parse_state_handoff_rows(claim_ctx["state_raw"])
    offers = [r for r in offer_rows if r.get("任务") == adapter.HANDOFF_OFFER_TASK_MARKER]
    claims = [r for r in claim_rows if r.get("任务") == adapter.HANDOFF_CLAIM_TASK_MARKER]
    if len(offers) != 1:
        print(f"[FAIL] OFFER 提交内的 OFFER 行数为 {len(offers)}，必须为 1", file=sys.stderr)
        return 1
    if len(claims) != 1:
        print(f"[FAIL] CLAIM 提交内的 CLAIM 行数为 {len(claims)}，必须为 1", file=sys.stderr)
        return 1

    now = datetime.now(TZ_UTC8)
    record = {
        "schema_version": "s4b_hardware_session_handoff_record_v1",
        "kind": adapter.HANDOFF_RECORD_KIND,
        "task_id": "S4-B-REAL-02B",
        "hardware_run_id": args.hardware_run_id,
        "scope": "S4B_PS_TENSOR_DIAGNOSTIC",
        "recorded_at_utc8": now.isoformat(timespec="seconds"),
        "authority_source": authority_source,
        "claim_source": claim_source,
        "offer_row": offers[0],
        "claim_row": claims[0],
        "boundaries": [
            "本记录只绑定 OFFER 与 CLAIM 的真实 Git 身份，不证板上行为。",
            "OFFER 心跳 1 小时有效；过期即失效，须由 main 重新 OFFER。",
            "本记录由检查器复核，不由本脚本自我放行。",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "hardware_session_handoff.json"
    target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[GENERATED] {target}")
    print(f"  offer_commit={authority_source['commit'][:12]} blob={authority_source['blob_oid'][:12]}")
    print(f"  claim_commit={claim_source['commit'][:12]} blob={claim_source['blob_oid'][:12]}")
    print(f"  offer_heartbeat={offers[0].get('心跳(UTC+8)')}  "
          f"scope={offers[0].get('允许修改范围')}")
    print("  下一步：把本目录加入 --gate-dir 一起交给 check_hardware_gate_readiness.py 复核")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
