#!/usr/bin/env python3
"""S6-B 版"新鲜证据检查两步"（限制③）：构建结束后间隔 N 秒跑两次 `--mode evidence`，两次都必须 exit 0。

    python -B verification/s6b_fresh_evidence_twice.py --project-root <abs> --run-dir report/evidence/S6-B/<run> --gap-seconds 30
产物：<root>/tmp/6/s6b_fresh_evidence_pair.json（两次真实退出码 + 判定）
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
    manifest = f"{run_rel}/delivery_manifest.json"
    command = [PY, "-B", "verification/check_stage_delivery.py", "--mode", "evidence",
               "--manifest", manifest, "--project-root", str(root)]
    completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    out.write_text(completed.stdout or "", encoding="utf-8")
    status = "MISSING"
    if (completed.stdout or "").strip().startswith("{"):
        try:
            status = json.loads(completed.stdout).get("status", "MISSING")
        except json.JSONDecodeError:
            status = "UNPARSEABLE"
    return {"command": subprocess.list2cmdline(command), "exit_code": completed.returncode,
            "status": status, "output_file": str(out)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--gap-seconds", type=int, default=30)
    parser.add_argument("--out", default="tmp/6/s6b_fresh_evidence_pair.json")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    tmp = root / "tmp/6"
    tmp.mkdir(parents=True, exist_ok=True)
    first = run_once(root, args.run_dir, tmp / "s6b_fresh_evidence_1.txt")
    time.sleep(max(0, args.gap_seconds))
    second = run_once(root, args.run_dir, tmp / "s6b_fresh_evidence_2.txt")
    payload = {"schema_version": 1, "artifact": "s6b_fresh_evidence_pair",
               "rule": "构建后间隔 gap_seconds 跑两次 --mode evidence，两次都必须 exit 0 且 CHECKS_OK",
               "gap_seconds": args.gap_seconds, "first": first, "second": second,
               "verdict": "BOTH_CHECKS_OK" if first["exit_code"] == 0 and second["exit_code"] == 0
                          and first["status"] == "CHECKS_OK" and second["status"] == "CHECKS_OK" else "FAILED"}
    out_path = root / args.out
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "first": [first["exit_code"], first["status"]],
                      "second": [second["exit_code"], second["status"]]}, ensure_ascii=False))
    return 0 if payload["verdict"] == "BOTH_CHECKS_OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
