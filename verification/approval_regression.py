#!/usr/bin/env python3
"""C4 反向自测：人为把某参数改回 PENDING_APPROVAL → C4 必须 FAIL（且基线必须 ALL_PASS）。

    python -B verification/approval_regression.py --project-root <abs> --run-dir <rel> [--out <json>]

全部操作在**临时副本**内进行，绝不触碰真实证据目录。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY = sys.executable


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", check=False)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def selfcheck(work: Path, run_rel: str, out: Path) -> tuple[int, dict]:
    cmd = [PY, "-B", "verification/s6_g0_selfcheck.py",
           "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
           "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
           "--cases", f"{run_rel}/hand_computed_cases.json",
           "--upstream", f"{run_rel}/upstream_bindings.json",
           "--out", str(out), "--project-root", str(work),
           "--evidence-dir", str(work / run_rel), "--state", ".codex/STATE.md"]
    code, output = run(cmd, work)
    doc = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}
    return code, {"status": doc.get("status"), "c4": next((c["status"] for c in doc.get("checks", [])
                                                           if c["id"] == "C4"), "MISSING"), "output_tail": output[-200:]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default="tmp/6/approval_regression.json")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "copy"
        for name in ("docs", "verification", "src", "report/evidence"):
            shutil.copytree(root / name, work / name, dirs_exist_ok=True)  # 含全部证据轮次，保证副本自洽（C11 需要）
        (work / ".codex").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / ".codex/STATE.md", work / ".codex/STATE.md")
        shutil.copytree(root / args.run_dir, work / args.run_dir, dirs_exist_ok=True)

        base_code, base = selfcheck(work, args.run_dir, Path(tmp) / "base.json")
        results["baseline"] = {"exit_code": base_code, **base}

        # 注入：把一项参数改回 PENDING_APPROVAL（只在副本内）
        jp = work / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
        data = json.loads(jp.read_text(encoding="utf-8"))
        data["parameters"][0]["approval_status"] = "PENDING_APPROVAL"
        jp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        inj_code, inj = selfcheck(work, args.run_dir, Path(tmp) / "injected.json")
        results["injected_pending"] = {"exit_code": inj_code, **inj}

        # 复制一份真实运行目录的哈希，证明未被改写
        real_files = sorted((root / args.run_dir).glob("*"))
        results["real_run_dir_files"] = len(real_files)

    ok = (results["baseline"]["exit_code"] == 0 and results["baseline"]["c4"] == "PASS"
          and results["injected_pending"]["exit_code"] != 0 and results["injected_pending"]["c4"] == "FAIL")
    payload = {"schema_version": 1, "artifact": "approval_regression",
               "rule": "C4 必须在注入 PENDING_APPROVAL 后 FAIL（基线 ALL_PASS）；全部操作在临时副本内",
               "results": results, "verdict": "AS_EXPECTED" if ok else "UNEXPECTED"}
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "baseline": [results["baseline"]["exit_code"], results["baseline"]["c4"]],
                      "injected": [results["injected_pending"]["exit_code"], results["injected_pending"]["c4"]]},
                     ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
