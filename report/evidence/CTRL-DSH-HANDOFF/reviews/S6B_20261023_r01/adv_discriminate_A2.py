#!/usr/bin/env python3
"""补做精确的旧口径注入 A2：M3 仍按「取较晚」，但 window_complete_ns 记在第 T6-S02 个
WINDOW_MATCH 帧（r06 之前的口径）。用于确认 C9c 的 window_complete_ns 断言本身有判别力。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\FPGA_Competition\tmp\review\S6B_20261023_r01")
ISO = ROOT / "iso"
CORE = ISO / "src/stage6/s6_core.py"
PRISTINE = ROOT / "s6_core_pristine.py"
DRIVER = ISO / "verification/s6b_run_cases.py"
RUN = ISO / "report/evidence/S6-B/s6b_core_20261023_r01"
WORK = ISO / "review_tmp"


def run_case(tag: str, case_ids: list[str]) -> dict:
    cases = json.loads((RUN / "cases/case_matrix.json").read_text(encoding="utf-8"))
    cases["cases"] = [c for c in cases["cases"] if c["case_id"] in case_ids]
    rd = WORK / tag
    (rd / "cases").mkdir(parents=True, exist_ok=True)
    (rd / "cases/case_matrix.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    frozen = json.loads((RUN / "expected_freeze.json").read_text(encoding="utf-8"))
    frozen["expected_sha256"] = {k: v for k, v in frozen["expected_sha256"].items() if k in case_ids}
    (rd / "expected_freeze.json").write_text(json.dumps(frozen, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
    cp = subprocess.run([sys.executable, "-B", str(DRIVER), "--project-root", str(ISO),
                         "--run-dir", str(rd), "--cases", str(rd / "cases/case_matrix.json")],
                        cwd=str(ISO), capture_output=True, text=True, encoding="utf-8",
                        errors="replace", check=False)
    rep = json.loads((rd / "run_report.json").read_text(encoding="utf-8"))
    return {"tag": tag, "exit": cp.returncode, "stdout": cp.stdout.strip(),
            "failures": {r["case_id"]: r["assertions_failed"] for r in rep["cases"]},
            "observed": {r["case_id"]: r["observed"].get("window_complete_ns") for r in rep["cases"]},
            "submitted": {r["case_id"]: r["observed"].get("submitted_at_frames") for r in rep["cases"]}}


def main() -> int:
    original = CORE.read_text(encoding="utf-8")
    try:
        patched = original.replace(
            "            self.window_match_count += 1\n            self.jitter_frames = 0",
            "            self.window_match_count += 1\n"
            "            if self.window_match_count == self.th['s02_frames']:\n"
            "                self.window_complete_ns = t_now_ns\n"
            "                log['window_complete_ns'] = t_now_ns\n"
            "            self.jitter_frames = 0",
            1)
        assert patched != original, "patch 未命中"
        CORE.write_text(patched, encoding="utf-8", newline="\n")
        print("== A2：M3 取较晚不变，仅完成时刻改记在第 S02 个 WINDOW_MATCH 帧 ==")
        print(" ", run_case("c9_disc_A2", ["C9c-30fps-later-of", "C1-fist-stable", "C9-s01-equal"]))
    finally:
        shutil.copy(PRISTINE, CORE)
    print("== 还原校验 ==")
    print(" ", run_case("c9_disc_A2_restored", ["C9c-30fps-later-of"]))
    identical = CORE.read_bytes() == PRISTINE.read_bytes()
    print("  核心文件与 w6 原件字节一致:", identical)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())