r"""独立复核 S5-T01 证据清单：逐文件重算 sha256/bytes，并检查外部原件的副本一致性。

只读；不 git。退出码 0=全对，1=有不符。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
RUN_ID = "s5_p3b_smoke_plan_20261030_r01"
PLAN = W / "report" / "evidence" / "S5-T01" / RUN_ID


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    d = json.loads((PLAN / "manifest.json").read_text(encoding="utf-8"))
    bad = 0
    print(f"manifest: task={d['task_id']} run={d['run_id']} basis={d['hash_basis']} "
          f"state={d['hash_basis_state']} files={len(d['files'])}")
    for f in d["files"]:
        p = W / f["path"]
        if not p.is_file():
            print(f"[BAD] missing {f['path']}")
            bad += 1
            continue
        got, size = sha(p), p.stat().st_size
        if got != f["sha256"] or size != f["bytes"]:
            print(f"[BAD] {f['path']} sha {got} size {size}")
            bad += 1
    for e in d["external_tmp_artifacts"]:
        p = Path(e["path"])
        if not p.is_file():
            print(f"[BAD] external missing {p}")
            bad += 1
            continue
        if sha(p) != e["sha256"]:
            print(f"[BAD] external sha changed {p}")
            bad += 1
        if not e.get("copy_matches"):
            print(f"[BAD] external copy mismatch {p}")
            bad += 1
    print(f"RESULT={'OK' if bad == 0 else 'MISMATCH'} bad={bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())