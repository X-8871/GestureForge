r"""生成 S5-T01 P3b 冒烟计划证据清单（manifest.json + MANIFEST.md）。

只读扫描证据目录，逐文件 sha256；**不做 git**。
hash_basis 目标为 `commit_blob`，但本会话禁止 git，因此清单显式标注 `PENDING_COMMIT`：
逐项 sha256 是**磁盘字节**（worktree_disk），lead 提交后必须用
`verification/check_manifest_hash_basis.py --mode strict` 复核提交后 blob 与清单一致。
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
TMP = Path(r"D:\tmp\lead\p3b_smoke_20261030_r01")
RUN_ID = "s5_p3b_smoke_plan_20261030_r01"
PLAN = W / "report" / "evidence" / "S5-T01" / RUN_ID
SELF_NAMES = {"manifest.json", "MANIFEST.md"}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    if not PLAN.is_dir():
        print(f"[FAIL] 证据目录不存在：{PLAN}")
        return 2
    files = []
    for p in sorted(PLAN.rglob("*")):
        if not p.is_file() or p.name in SELF_NAMES:
            continue
        files.append({
            "path": p.relative_to(W).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": sha(p),
            "hash_basis": "commit_blob",
            "hash_basis_state": "PENDING_COMMIT",
        })
    external = []
    for p in (TMP / "run_p3b_smoke.py", TMP / "P3B_SMOKE_PLAN.md",
              TMP / "make_evidence_manifest.py", TMP / "verify_manifest.py"):
        if not p.is_file():
            continue
        copy = PLAN / p.name
        external.append({
            "path": str(p),
            "bytes": p.stat().st_size,
            "sha256": sha(p),
            "hash_basis": "worktree_disk",
            "copy_in_evidence": copy.relative_to(W).as_posix() if copy.is_file() else None,
            "copy_sha256": sha(copy) if copy.is_file() else None,
            "copy_matches": bool(copy.is_file() and sha(copy) == sha(p)),
        })
    now = datetime.now(UTC8).isoformat(timespec="seconds")
    manifest = {
        "task_id": "S5-T01",
        "run_id": RUN_ID,
        "phase": "阶段5 P3b 上屏冒烟：窗口执行器脚本 + 操作单（离线产物，dry-run 通过）",
        "generated_utc8": now,
        "status": "PLAN_ONLY",
        "hash_basis": "commit_blob",
        "hash_basis_state": "PENDING_COMMIT",
        "commit": None,
        "hash_basis_note": (
            "本会话禁止 git（任务边界），因此证据文件在生成时未提交；下面逐项 sha256 为磁盘字节"
            "（worktree_disk）。lead 提交本目录后，必须用 "
            "`python -B D:\\FPGA_Competition\\verification\\check_manifest_hash_basis.py "
            "--worktree w4 --mode strict` 复核 commit_blob 与清单一致；不一致即不得作为交付物。"
        ),
        "boundary": "离线：未碰板卡/JTAG/COM4/hw_server；未跑 Vivado；未 git；ENABLE=0；"
                    "不主张 G3/G4/G5",
        "artifacts": {
            "script": "run_p3b_smoke.py（dry-run / self-test 均 exit=0）",
            "plan": "P3B_SMOKE_PLAN.md（上板步骤/判据/停止点/降级建议）",
            "offline_checks": ["ast_check.log（ast.parse OK）", "dry_run.log（12 条命令 / 8 条判据）",
                               "selftest.log（14 个判据正负例全 PASS）"],
        },
        "dependencies_missing": [
            {"item": "P3b 位流", "path": r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.bit",
             "state": "NOT_YET_BUILT", "effect": "真实窗口在 IDENT/X1 停止；dry-run 已报告缺失"},
            {"item": "显示 ELF 的 S5DISP RESULT 打印",
             "path": r"D:\tmp\lead\p3b_display_sw_20261030_r01\src\s5_display_app.c",
             "state": "NOT_IMPLEMENTED（当前主循环 for(;;)，只打 frame 行）",
             "effect": "重建前真实窗口会在 X6 停止（无结果行）"},
        ],
        "files": files,
        "external_tmp_artifacts": external,
        "verification": {
            "recompute": "python -B make_evidence_manifest.py（本文件由它生成）",
            "commit_blob_gate": r"python -B D:\FPGA_Competition\verification\check_manifest_hash_basis.py "
                                r"--worktree w4 --mode strict",
            "expected": "提交后 verdict OK / 0 不符；PENDING_COMMIT 期间不得声称已过该门禁",
        },
    }
    (PLAN / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
    md = ["# S5-T01 P3b 上屏冒烟计划证据清单", "",
          f"- RunId `{RUN_ID}`；状态 **PLAN_ONLY**（未上板；位流未产出；显示 ELF 待重建）",
          f"- 生成：{now}；`hash_basis=commit_blob`，当前 **PENDING_COMMIT**（本会话禁止 git）",
          "- `path` 为仓库相对路径；逐项 sha256 为磁盘字节，提交后须用统一门禁复核", "",
          "| 文件 | 字节 | sha256 |", "|---|---|---|"]
    for f in files:
        md.append(f"| `{f['path']}` | {f['bytes']} | `{f['sha256']}` |")
    md += ["", "## 外部 tmp 原件（worktree_disk）", "", "| 文件 | 字节 | sha256 | 与证据副本一致 |",
           "|---|---|---|---|"]
    for e in external:
        md.append(f"| `{e['path']}` | {e['bytes']} | `{e['sha256']}` | {e['copy_matches']} |")
    md += ["", "## 依赖缺失", ""]
    for d in manifest["dependencies_missing"]:
        md.append(f"- **{d['item']}**：{d['state']} —— {d['effect']}")
    md += ["", "## 边界", "", "离线产物；`ENABLE=0`；未碰板卡/JTAG/COM4/hw_server；未跑 Vivado；未 git；",
           "不主张 G3/G4/G5。PENDING_COMMIT 期间不得声称已通过 `check_manifest_hash_basis.py`。"]
    (PLAN / "MANIFEST.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] manifest.json / MANIFEST.md：{len(files)} 个仓库文件 + {len(external)} 个外部原件")
    print(f"[OK] PENDING_COMMIT（{PLAN}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())