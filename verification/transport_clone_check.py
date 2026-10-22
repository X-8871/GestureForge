#!/usr/bin/env python3
"""传输克隆可解析性检查：`source_commit` 必须能在**传输克隆**（git clone --no-local）里解析。

    python -B verification/transport_clone_check.py --project-root <abs> [--commit <sha>] [--out <json>]

判定（真实退出码 0 = 可解析；1 = 不可解析或不是 commit）：
* 传输克隆（`--no-local`，模拟第三方仅经传输拿到对象）中 `git cat-file -t <sha> == commit`；
* 该提交被某个 ref 包含（`git merge-base --is-ancestor <sha> HEAD`）。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(argv: list[str], cwd: Path | None = None) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, ((completed.stdout or "") + (completed.stderr or "")).strip()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--out", default="tmp/6/transport_clone_check.json")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    code, rev = run(["git", "-C", str(root), "rev-parse", args.commit])
    if code != 0:
        print(f"rev-parse 失败：{rev}")
        return 1
    sha = rev.strip()
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "transport"
        clone_code, clone_out = run(["git", "clone", "--no-local", "--quiet", str(root), str(clone)])
        payload: dict = {"schema_version": 1, "artifact": "transport_clone_check",
                         "source_commit": sha, "clone_exit": clone_code, "clone_output_tail": clone_out[-200:]}
        if clone_code != 0:
            payload.update({"verdict": "CLONE_FAILED", "resolvable": False})
        else:
            t_code, t_out = run(["git", "-C", str(clone), "cat-file", "-t", sha])
            anc_code, _ = run(["git", "-C", str(clone), "merge-base", "--is-ancestor", sha, "HEAD"])
            payload.update({"cat_file_type": t_out, "cat_file_exit": t_code,
                            "is_ancestor_exit": anc_code,
                            "resolvable": t_code == 0 and t_out.strip() == "commit" and anc_code == 0,
                            "guess_exit": 0})
            payload["command"] = (f"git clone --no-local <root> <tmp> && git -C <tmp> cat-file -t {sha} && "
                                  f"git -C <tmp> merge-base --is-ancestor {sha} HEAD")
            payload["verdict"] = "RESOLVABLE" if payload["resolvable"] else "NOT_RESOLVABLE"
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "source_commit": sha,
                      "cat_file": payload.get("cat_file_type"), "is_ancestor_exit": payload.get("is_ancestor_exit")},
                     ensure_ascii=False))
    return 0 if payload["verdict"] == "RESOLVABLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
