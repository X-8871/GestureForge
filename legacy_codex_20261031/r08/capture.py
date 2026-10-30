#!/usr/bin/env python3
"""只读核验R-08交接范围，保留本轮执行前的暂存与工作区身份。"""

import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def git(*args):
    """禁用可选锁并保留真实退出码。"""
    proc = subprocess.run(["git", "--no-optional-locks", "-c", "core.longpaths=true", "-C", str(ROOT), *args], capture_output=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return proc.stdout


def main():
    """仅在全新输出名不存在时保存一次快照，不修改Git或既有文件。"""
    target = OUT / "initial_snapshot.json"
    if target.exists():
        raise FileExistsError(target)
    status = git("status", "--porcelain=v1", "-z").decode("utf-8").split("\0")
    entries = []
    for line in filter(None, status):
        state, rel = line[:2], line[3:]
        path = ROOT / rel
        row = {"status": state, "path": rel, "type": "directory" if path.is_dir() else "file"}
        if path.is_file():
            row.update(disk_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)
        entries.append(row)
    raw = git("ls-files", "--stage", "-z").decode("utf-8")
    index_path = Path(git("rev-parse", "--git-path", "index").decode("utf-8").strip())
    lock = Path(git("rev-parse", "--git-path", "index.lock").decode("utf-8").strip())
    state = (ROOT / ".codex/STATE.md").read_text(encoding="utf-8")
    offer = next(line for line in state.splitlines() if line.startswith("任务=`R-08："))
    fields = offer.split(" | ")
    if len(fields) != 11 or "让出声明=`OFFERED" not in offer:
        raise ValueError("正式OFFER必须含11字段并明确让出")
    staged_paths = git("diff", "--cached", "--name-only", "-z").decode("utf-8").split("\0")
    result = {"created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
              "root": str(ROOT), "head": git("rev-parse", "HEAD").decode().strip(),
              "branch": git("branch", "--show-current").decode().strip(), "index_path": str(index_path),
              "index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
              "index_lock_exists": lock.exists(), "index_entries_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
              "staged_paths": list(filter(None, staged_paths)), "status_entries": entries,
              "offer_field_count": len(fields), "offer": offer,
              "ownership": {"tracked_legacy": [".codex/STATE.md", ".gitattributes", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "docs/stage6/s6a_stage6_g0_behavior_v1.json"],
                            "historical_directories": 14, "c1_staged_files_excluding_state": 32,
                            "owner": "此前Codex阶段6工作；DSH显式CLAIM后逐项接收，不混本轮遗留代码提交"},
              "status": "OFFERED_PENDING_DSH_CLAIM", "hardware_access": False}
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "offer_fields": len(fields), "entries": len(entries), "exit_code": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
