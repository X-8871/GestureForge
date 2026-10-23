#!/usr/bin/env python3
"""阶段4 w4 接续接管只读核对（S4-T21）。

只读核对：工作树/分支/HEAD、`index.lock` 真实路径与存在性、重型进程、未跟踪产物
归属与逐文件 SHA-256。本脚本**不删除、不覆盖、不移动**任何未跟踪产物，也不据
“无锁”推断无人写入；它只记录可核验事实。

退出码：0 = 结构与归属核对通过；1 = 存在未分类改动或缺项；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))

# 交接口径：12 项未提交改动 = 6 ELF + 6 map，均为 Codex 本机恢复产物，留原位。
EXPECTED_UNTRACKED = 12
RECOVERY_STEM = "s4b_ps_tensor_diagnostic"
RECOVERY_SUFFIXES = (".elf", ".map")

# 重型任务类别（判断是否可安全接手）。MCP 服务器进程不是综合/仿真引擎，单独归类。
HEAVY_TOKENS = ("vivado", "xsim", "hw_server", "xsdb", "vitis", "xelab", "verilator", "vlm")
MCP_SERVER_TOKEN = "vivado-mcp-server"


def run(cmd: list[str], cwd: Path | None = None) -> dict[str, object]:
    """执行只读子进程并记录真实退出码与输出。"""
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return {
        "cmd": cmd,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_processes() -> dict[str, object]:
    """只读枚举本机进程，按重型类别/MCP 服务器分类。"""
    proc = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    rows: list[dict[str, object]] = []
    for row in csv.reader(io.StringIO(proc.stdout)):
        if len(row) < 2:
            continue
        name = row[0].strip()
        lowered = name.lower()
        if not any(token in lowered for token in HEAVY_TOKENS):
            continue
        rows.append({
            "name": name,
            "pid": row[1].strip(),
            "kind": "mcp_server_process" if MCP_SERVER_TOKEN in lowered else "heavy_engine_process",
        })
    return {
        "cmd": ["tasklist", "/FO", "CSV", "/NH"],
        "exit_code": proc.returncode,
        "rows": rows,
        "heavy_engine_count": sum(1 for r in rows if r["kind"] == "heavy_engine_process"),
        "mcp_server_count": sum(1 for r in rows if r["kind"] == "mcp_server_process"),
    }


def classify_untracked(rel_path: str, size_bytes: int) -> tuple[str, str]:
    """按交接声明归类未跟踪产物；无法归类即如实标记 unclassified。"""
    name = Path(rel_path).name
    if name.startswith(RECOVERY_STEM) and name.endswith(RECOVERY_SUFFIXES) and size_bytes > 0:
        return "codex_local_recovery_output", "交接声明：Codex 本机恢复产物（ELF/map），留原位不入源码 Git"
    return "unclassified", "无归属声明，必须停止并报告"


def main() -> int:
    """执行全部只读核对。"""
    parser = argparse.ArgumentParser(description="w4 接续接管只读核对")
    parser.add_argument("--evidence-dir", required=True)
    parser.add_argument("--expected-untracked", type=int, default=EXPECTED_UNTRACKED)
    parser.add_argument(
        "--own-artifact", action="append", default=[],
        help="本轮本任务自身新建的路径前缀（相对工作树）；计入 this_task_artifact，不计入交接声明的 12 项",
    )
    args = parser.parse_args()

    if not (WORKTREE / ".codex" / "STATE.md").is_file():
        print(f"[FAIL] 工作树不可识别：{WORKTREE}")
        return 2

    failures: list[str] = []
    out_dir = Path(args.evidence_dir)
    if out_dir.exists():
        # 新 RunId 必须未存在；允许脚本自身写入已创建的空目录。
        if any(out_dir.iterdir()):
            print(f"[FAIL] 证据目录非空，RunId 可能被复用：{out_dir}")
            return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    facts: dict[str, object] = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "audit_w4_takeover",
        "checker_version": "r01",
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "worktree": str(WORKTREE),
        "python_version": sys.version,
        "platform": platform.platform(),
    }

    branch = run(["git", "-C", str(WORKTREE), "branch", "--show-current"])
    head = run(["git", "-C", str(WORKTREE), "rev-parse", "HEAD"])
    lock_rel = run(["git", "-C", str(WORKTREE), "rev-parse", "--git-path", "index.lock"])
    status = run(["git", "-C", str(WORKTREE), "status", "--porcelain"])
    log = run(["git", "-C", str(WORKTREE), "log", "--oneline", "-8"])
    for label, entry in (("branch", branch), ("head", head), ("index_lock_path", lock_rel),
                         ("git_status", status), ("git_log", log)):
        if entry["exit_code"] != 0:
            failures.append(f"git 只读命令失败：{label} exit={entry['exit_code']} {entry['stderr']}")

    lock_path = Path(str(lock_rel["stdout"])) if lock_rel["stdout"] else None
    lock_exists = bool(lock_path and lock_path.exists())

    entries: list[dict[str, object]] = []
    own_entries: list[dict[str, object]] = []
    unclassified: list[str] = []
    own_prefixes = [p.strip("/\\").replace("\\", "/") for p in args.own_artifact]
    for line in str(status["stdout"]).splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:].strip().strip('"').replace("\\", "/")
        path = WORKTREE / rel
        size = path.stat().st_size if path.is_file() else -1
        is_own = any(rel == prefix or rel.startswith(prefix + "/") for prefix in own_prefixes)
        if is_own:
            own_entries.append({
                "path": rel, "kind": "this_task_artifact",
                "note": "本任务（task-21 / stage4-lead）本轮新建，未提交", "size_bytes": size,
            })
            continue
        kind, note = classify_untracked(rel, size)
        record = {
            "path": rel,
            "size_bytes": size,
            "kind": kind,
            "note": note,
            "sha256": sha256_of(path) if path.is_file() else None,
            "action": "left_in_place_not_committed",
        }
        entries.append(record)
        if kind == "unclassified":
            unclassified.append(rel)

    tracked_changes = [l for l in str(status["stdout"]).splitlines() if l and not l.startswith("?? ")]
    facts.update({
        "branch": branch["stdout"],
        "head": head["stdout"],
        "index_lock_path": str(lock_path) if lock_path else None,
        "index_lock_exists": lock_exists,
        "tracked_modified_or_staged_count": len(tracked_changes),
        "tracked_changes": tracked_changes,
        "untracked_count": len(entries),
        "untracked_expected": args.expected_untracked,
        "untracked_entries": entries,
        "this_task_untracked": own_entries,
        "untracked_classification_counts": {
            "codex_local_recovery_output": sum(1 for e in entries if e["kind"] == "codex_local_recovery_output"),
            "unclassified": len(unclassified),
            "this_task_artifact": len(own_entries),
        },
        "recent_commits": str(log["stdout"]).splitlines(),
        "processes": list_processes(),
        "commands": {"branch": branch, "head": head, "index_lock_path": lock_rel,
                     "git_status": status, "git_log": log},
        "interpretation_boundary": [
            "无 index.lock 不等于无人写入；本记录只陈述可核验事实。",
            "本脚本未删除、未覆盖、未移动任何未跟踪产物，也未运行重型任务或访问硬件。",
            "重型进程计数只覆盖本次枚举到的名称；不代表其他窗口的会话归属。",
        ],
    })

    if lock_exists:
        failures.append(f"工作树存在 index.lock：{lock_path}")
    if tracked_changes:
        failures.append(f"存在已跟踪文件的未提交改动（{len(tracked_changes)} 项），超出本轮交接声明：{tracked_changes}")
    if len(entries) != args.expected_untracked:
        failures.append(f"未跟踪产物数量 {len(entries)} != 声明 {args.expected_untracked}")
    if unclassified:
        failures.append(f"未分类未跟踪产物：{unclassified}")
    if facts["processes"]["heavy_engine_count"]:
        failures.append("检测到重型引擎进程，禁止接手写入")

    facts["status"] = "PASS" if not failures else "FAIL"
    facts["failures"] = failures
    facts["checker_sha256"] = sha256_of(Path(__file__).resolve())

    (out_dir / "takeover_audit.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "git_status_short.txt").write_text(str(status["stdout"]) + "\n", encoding="utf-8")
    (out_dir / "git_log.txt").write_text(str(log["stdout"]) + "\n", encoding="utf-8")
    (out_dir / "untracked_sha256.txt").write_text(
        "".join(f"{e['sha256']}  {e['path']}  {e['size_bytes']}\n" for e in entries), encoding="utf-8"
    )

    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{facts['status']}] 接管核对：分支={facts['branch']} HEAD={facts['head']} "
          f"锁={'存在' if lock_exists else '不存在'} 未跟踪={len(entries)} "
          f"重型引擎={facts['processes']['heavy_engine_count']} MCP服务器={facts['processes']['mcp_server_count']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())