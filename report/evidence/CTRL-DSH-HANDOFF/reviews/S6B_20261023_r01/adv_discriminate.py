#!/usr/bin/env python3
"""Reviewer 判别力注入：把核心改回 N-r05-04 之前的旧口径（window_complete_ns 记在第 T6-S02 个
WINDOW_MATCH 帧），确认 C9c-30fps-later-of 必须 FAIL。仅改隔离副本，事后还原。"""
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
    cmd = [sys.executable, "-B", str(DRIVER), "--project-root", str(ISO), "--run-dir", str(rd),
           "--cases", str(rd / "cases/case_matrix.json")]
    cp = subprocess.run(cmd, cwd=str(ISO), capture_output=True, text=True,
                        encoding="utf-8", errors="replace", check=False)
    rep = json.loads((rd / "run_report.json").read_text(encoding="utf-8"))
    return {"tag": tag, "exit": cp.returncode, "stdout": cp.stdout.strip(),
            "failures": {r["case_id"]: r["assertions_failed"] for r in rep["cases"]},
            "observed": {r["case_id"]: r["observed"].get("window_complete_ns") for r in rep["cases"]}}


def main() -> int:
    shutil.copy(CORE, PRISTINE)
    original = CORE.read_text(encoding="utf-8")

    case_ids = ["C9c-30fps-later-of", "C9-s01-equal", "C1-fist-stable"]
    print("== 未打补丁（原实现）==")
    print(" ", run_case("c9_disc_orig", case_ids))

    # 旧口径 1：在第 T6-S02 个 WINDOW_MATCH 帧写 window_complete_ns
    old1 = original.replace(
        "            self.window_match_count += 1\n            self.jitter_frames = 0",
        "            self.window_match_count += 1\n"
        "            if self.window_match_count == self.th['s02_frames'] and self.window_complete_ns is None:\n"
        "                self.window_complete_ns = t_now_ns\n"
        "            self.jitter_frames = 0",
        1)
    assert old1 != original, "patch1 未命中"
    old1 = old1.replace(
        "                self.window_complete_ns = t_now_ns\n                log[\"window_complete_ns\"] = t_now_ns\n",
        "", 1)
    assert "log[\"window_complete_ns\"] = t_now_ns\n" not in old1, "patch1b 未命中"
    CORE.write_text(old1, encoding="utf-8")
    print("== 旧口径 A：完成时刻记在第 T6-S02 个 WINDOW_MATCH 帧 ==")
    print(" ", run_case("c9_disc_oldA", case_ids))
    CORE.write_text(original, encoding="utf-8")

    # 旧口径 2：M3 只看帧数（忽略 T6-S01 时长）
    old2 = original.replace(
        "            if (self.window_match_count >= self.th[\"s02_frames\"] and self.window_start_ns is not None\n"
        "                    and (t_now_ns - self.window_start_ns) >= self.th[\"s01_ns\"]):",
        "            if (self.window_match_count >= self.th[\"s02_frames\"] and self.window_start_ns is not None):",
        1)
    assert old2 != original, "patch2 未命中"
    CORE.write_text(old2, encoding="utf-8")
    print("== 旧口径 B：M3 只数帧、忽略时长（应令 C9c/C9-s01 系列 FAIL）==")
    print(" ", run_case("c9_disc_oldB", case_ids))
    CORE.write_text(original, encoding="utf-8")
    print("== 还原后复核 ==")
    print(" ", run_case("c9_disc_restored", case_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())