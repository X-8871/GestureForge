#!/usr/bin/env python3
"""验收：构建结束后连跑两次新鲜自检（间隔 N 秒），两次都必须 exit 0 且 C11 无哈希不符。

    python -B verification/s6a_fresh_selfcheck_twice.py --project-root <abs> --run-dir <rel> --gap-seconds 30
产物：<root>/tmp/6/fresh_selfcheck_pair.json（两次的真实退出码、C11 状态、被报不符的文件）
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PY = sys.executable


def run_once(root: Path, run_rel: str, out: Path) -> dict:
    run_dir = root / run_rel
    command = [PY, "-B", "verification/s6_g0_selfcheck.py",
               "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
               "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
               "--cases", f"{run_rel}/hand_computed_cases.json",
               "--upstream", f"{run_rel}/upstream_bindings.json",
               "--out", str(out), "--project-root", str(root), "--evidence-dir", str(run_dir),
               "--manifest", f"{run_rel}/delivery_manifest.json", "--state", ".codex/STATE.md"]
    completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    status, c11, errors = "MISSING", "MISSING", []
    if out.is_file():
        data = json.loads(out.read_text(encoding="utf-8"))
        status = data.get("status")
        errors = data.get("errors", [])
        c11 = next((c["status"] for c in data.get("checks", []) if c["id"] == "C11"), "MISSING")
    return {"command": subprocess.list2cmdline(command), "exit_code": completed.returncode,
            "status": status, "c11": c11, "errors": errors, "out": str(out)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--gap-seconds", type=int, default=30)
    parser.add_argument("--out", default="tmp/6/fresh_selfcheck_pair.json")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    tmp = root / "tmp/6"
    tmp.mkdir(parents=True, exist_ok=True)
    first = run_once(root, args.run_dir, tmp / "fresh_selfcheck_1.json")
    time.sleep(max(0, args.gap_seconds))
    second = run_once(root, args.run_dir, tmp / "fresh_selfcheck_2.json")
    payload = {"schema_version": 1, "artifact": "fresh_selfcheck_pair",
               "rule": "构建后新鲜自检两次（间隔秒数见 gap_seconds）都必须 exit 0 且 C11 无哈希不符",
               "gap_seconds": args.gap_seconds, "first": first, "second": second,
               "verdict": "BOTH_ALL_PASS" if first["exit_code"] == 0 and second["exit_code"] == 0
                          and first["c11"] == "PASS" and second["c11"] == "PASS" else "FAILED"}
    out_path = root / args.out
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "first": [first["exit_code"], first["c11"]],
                      "second": [second["exit_code"], second["c11"]]}, ensure_ascii=False))
    return 0 if payload["verdict"] == "BOTH_ALL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
