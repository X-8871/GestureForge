#!/usr/bin/env python3
"""Reviewer 隔离注入脚本（S6-B 第 1 轮复审）：阈值参数化 / 24 项状态强制 / 装载强制。

只在隔离副本 tmp/review/S6B_20261023_r01/iso 下写文件；不修改被审工作树。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_20261023_r01\iso")
RUN = ISO / "report/evidence/S6-B/s6b_core_20261023_r01"
BEHAVIOR = ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
WORK = ISO / "review_tmp"
DRIVER = ISO / "verification/s6b_run_cases.py"


def run(tag: str, behavior: Path, extra_cases: list[str] | None = None) -> dict:
    rd = WORK / tag
    (rd / "cases").mkdir(parents=True, exist_ok=True)
    if not (rd / "cases/case_matrix.json").exists():
        (rd / "cases/case_matrix.json").write_text(
            (RUN / "cases/case_matrix.json").read_text(encoding="utf-8"), encoding="utf-8")
    if not (rd / "expected_freeze.json").exists():
        (rd / "expected_freeze.json").write_text(
            (RUN / "expected_freeze.json").read_text(encoding="utf-8"), encoding="utf-8")
    cmd = [sys.executable, "-B", str(DRIVER), "--project-root", str(ISO),
           "--run-dir", str(rd), "--cases", str(rd / "cases/case_matrix.json"),
           "--behavior-json", str(behavior)] + (extra_cases or [])
    cp = subprocess.run(cmd, cwd=str(ISO), capture_output=True, text=True,
                        encoding="utf-8", errors="replace", check=False)
    return {"tag": tag, "exit": cp.returncode,
            "stdout": cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else "",
            "stderr_tail": cp.stderr.strip().splitlines()[-1] if cp.stderr.strip() else ""}


def variant(tag: str, mutate) -> Path:
    data = json.loads(BEHAVIOR.read_text(encoding="utf-8"))
    mutate(data)
    out = WORK / f"behavior_{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def set_param(data, pid, **kw):
    for item in data["parameters"]:
        if item["id"] == pid:
            item.update(kw)
            return
    raise SystemExit(f"参数不存在：{pid}")


def drop_param(data, pid):
    data["parameters"] = [p for p in data["parameters"] if p["id"] != pid]


def observed_c1(tag: str) -> dict:
    rep = json.loads((WORK / tag / "run_report.json").read_text(encoding="utf-8"))
    row = next(r for r in rep["cases"] if r["case_id"] == "C1-fist-stable")
    return {"status": row["status"],
            "window_complete_ns": row["observed"]["window_complete_ns"],
            "submitted_at_frames": row["observed"]["submitted_at_frames"],
            "transitions": row["observed"]["transitions"],
            "assertions_failed": rep["assertions_failed"]}


def main() -> int:
    out = {}
    print("== 基线（未改）==")
    base = variant("baseline", lambda d: None)
    out["baseline"] = run("baseline", base)
    print(" ", out["baseline"], observed_c1("baseline"))

    print("== 注入 T6-S02 = 4（原 6）==")
    v = variant("s02_4", lambda d: set_param(d, "T6-S02", draft_value=4))
    out["s02_4"] = run("s02_4", v)
    print(" ", out["s02_4"], observed_c1("s02_4"))

    print("== 注入 T6-S01 = 100（原 200）==")
    v = variant("s01_100", lambda d: set_param(d, "T6-S01", draft_value=100))
    out["s01_100"] = run("s01_100", v)
    print(" ", out["s01_100"], observed_c1("s01_100"))

    print("== 注入 T6-P02 = 0.7（低分不再算 WINDOW_MATCH）==")
    v = variant("p02_07", lambda d: set_param(d, "T6-P02", draft_value=0.7))
    out["p02_07"] = run("p02_07", v)
    print(" ", out["p02_07"], observed_c1("p02_07"))

    print("== 必需参数 T6-S02 -> APPROVED（应拒载）==")
    v = variant("s02_approved", lambda d: set_param(d, "T6-S02", approval_status="APPROVED"))
    out["s02_approved"] = run("s02_approved", v)
    print(" ", out["s02_approved"])

    print("== 非必需参数 T6-A03 -> APPROVED（草案值 None，应仍被强制）==")
    v = variant("a03_approved", lambda d: set_param(d, "T6-A03", approval_status="APPROVED"))
    out["a03_approved"] = run("a03_approved", v)
    print(" ", out["a03_approved"])

    print("== 非必需参数 T6-03 -> APPROVED（表内指标）==")
    v = variant("t603_approved", lambda d: set_param(d, "T6-03", approval_status="APPROVED"))
    out["t603_approved"] = run("t603_approved", v)
    print(" ", out["t603_approved"])

    print("== 删除非必需参数 T6-A03（是否仍能装载＝是否真的强制 24 项）==")
    v = variant("drop_a03", lambda d: drop_param(d, "T6-A03"))
    out["drop_a03"] = run("drop_a03", v)
    print(" ", out["drop_a03"])
    try:
        print(" ", observed_c1("drop_a03"))
    except Exception as exc:  # noqa: BLE001
        print("  (no report)", exc)

    print("== 删除必需参数 T6-S02（应拒载）==")
    v = variant("drop_s02", lambda d: drop_param(d, "T6-S02"))
    out["drop_s02"] = run("drop_s02", v)
    print(" ", out["drop_s02"])

    print("== status 不再是 PENDING_APPROVAL 口径（应拒载）==")
    v = variant("status_done", lambda d: d.update({"status": "G0_PACKET_APPROVED"}))
    out["status_done"] = run("status_done", v)
    print(" ", out["status_done"])

    (WORK / "tamper_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())