r"""冻结回归执行器（阶段4/5，2026-10-29 r01）：串行跑 7 个板级窗口，任一 FAIL 立即停。

前置：`python -B gen_frozen_inputs.py --check` 必须 exit 0；板卡空闲。
本脚本只做编排（subprocess 调既有 runner），不改判据、不碰源码。

用法：
  python -B run_freeze_regression.py --dry-run     # 只打印将执行的命令与预计时长
  python -B run_freeze_regression.py               # 真实执行（约 45–55 min）
  python -B run_freeze_regression.py --start R3    # 从 R3 开始（断点续跑）
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
HERE = Path(__file__).resolve().parent
BOARD_DIR = Path(r"D:\tmp\lead\p2b_board_20261029_r01")
CLOSE_DIR = Path(r"D:\tmp\lead\m4b_close_20261029_r01")
W4 = Path(r"D:\codex-worktrees\w4")
EVID = W4 / "report" / "evidence" / "S4-T34"

# (id, 说明, cwd, 脚本, RunId, 预计分钟)
STEPS = [
    ("R1", "2B 基线：M3 只读复检 + M4-a", BOARD_DIR, "run_freeze_r1_m3_m4a_2b.py",
     "s4d_freeze_r1_m3_m4a_2b_20261029_r01", 4),
    ("R2", "2B 基线：M4-b 收口（padded 参考 + 投毒）", CLOSE_DIR, "run_m4b_close.py",
     "s4d_freeze_r2_m4b_2b_20261029_r01", 6),
    ("R3", "2B 基线：chain-lite A", BOARD_DIR, "run_chainlite_a_2b.py",
     "s4d_freeze_r3_chaina_2b_20261029_r01", 5),
    ("R4", "2B 基线：chain-lite B", BOARD_DIR, "run_chainlite_b_2b.py",
     "s4d_freeze_r4_chainb_2b_20261029_r01", 5),
    ("R5", "P2d：2B 单帧性能（47000–48000 ms）", BOARD_DIR, "run_m4b_p2d.py",
     "s4d_freeze_r5_m4b_p2d_20261029_r01", 6),
    ("R6", "P2d：chain-lite A", BOARD_DIR, "run_chainlite_a_p2d.py",
     "s4d_freeze_r6_chaina_p2d_20261029_r01", 6),
    ("R7", "P2d：preproc→DMA(HP1) 张量 CRC", BOARD_DIR, "run_p2c_crc_on_p2d.py",
     "s4d_freeze_r7_crc_p2d_20261029_r01", 6),
]

# 各步 PASS 的结论串（runner 内部 conclusion 字段；大小写敏感）
PASS_CONCLUSIONS = {
    "R1": {"P2B_4D_STOPPED_ON_FAILURE_NOT_USED"},       # R1 只要 M3+M4-a PASS，见 step_ok()
    "R2": {"M4B_PASS_TAIL13_CLOSED"},
    "R3": {"CHAINLITE_A_PASS"},
    "R4": {"PASS"},
    "R5": {"M4B_ON_P2B_DONE_LEGACY_REF", "M4B_ON_P2B_FAIL"},  # 只判 done/error/elapsed，见 step_ok()
    "R6": {"CHAINLITE_A_PASS"},
    "R7": {"P2C_TENSOR_CRC_MATCH"},
}


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def board_idle() -> bool:
    try:
        ps = subprocess.run(["powershell", "-NoProfile", "-Command",
                             "(Get-Process hw_server,xsdb,vivado -ErrorAction SilentlyContinue | Measure-Object).Count"],
                            capture_output=True, text=True, timeout=60)
        return (ps.stdout or "").strip() == "0"
    except Exception:  # noqa: BLE001
        return False


def result_of(run_id: str) -> dict:
    d = EVID / run_id
    for p in sorted(d.glob("results_*.json")) if d.is_dir() else []:
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
    return {}


def step_ok(step_id: str, run_id: str) -> tuple[bool, str]:
    res = result_of(run_id)
    if not res:
        return False, "无 results_*.json"
    concl = str(res.get("conclusion") or "")
    if step_id == "R1":
        m3 = res.get("steps", {}).get("W3_m3_recheck", {})
        m4a = res.get("steps", {}).get("W4_m4a", {})
        ok = m3.get("status") == "PASS" and m4a.get("status") == "PASS"
        return ok, f"m3={m3.get('status')} m4a={m4a.get('status')} m4b_skipped_ok"
    if step_id == "R5":
        # 不依赖具体步骤名：任一步骤里带 parsed 且含 done/elapsed_ms 的就是 M4-b 结果
        parsed = {}
        for st in (res.get("steps") or {}).values():
            q = (st or {}).get("parsed") or {}
            if isinstance(q, dict) and "done" in q and "elapsed_ms" in q:
                parsed = q
                break
        el = parsed.get("elapsed_ms")
        ok = parsed.get("done") == 1 and parsed.get("error") == 0 and isinstance(el, int) and 47000 <= el <= 48000
        return ok, f"done={parsed.get('done')} error={parsed.get('error')} elapsed_ms={el}"
    return concl in PASS_CONCLUSIONS.get(step_id, set()), concl


def main() -> int:
    start = "R1"
    if "--start" in sys.argv:
        start = sys.argv[sys.argv.index("--start") + 1]
    dry = "--dry-run" in sys.argv

    print(f"[{now()}] 冻结回归：前置检查")
    chk = subprocess.run([sys.executable, "-B", str(HERE / "gen_frozen_inputs.py"), "--check"],
                         capture_output=True, text=True, cwd=str(HERE))
    print(chk.stdout.strip()[:800])
    if chk.returncode != 0:
        print("冻结输入校验失败 → 拒绝开跑")
        return 2
    if not board_idle():
        print("板卡非空闲（存在 hw_server/xsdb/vivado）→ 拒绝开跑")
        return 2

    report = []
    started = False
    for sid, desc, cwd, script, run_id, mins in STEPS:
        if not started:
            if sid != start:
                print(f"[{now()}] 跳过 {sid}（--start {start}）")
                continue
            started = True
        cmd = [sys.executable, "-B", str(cwd / script), run_id]
        print(f"[{now()}] {sid} {desc} → {' '.join(cmd)}  (~{mins} min)", flush=True)
        if dry:
            report.append({"id": sid, "run_id": run_id, "desc": desc, "dry_run": True})
            continue
        t0 = time.time()
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        dt = round((time.time() - t0) / 60, 1)
        ok, detail = step_ok(sid, run_id)
        # runner 的 stdout 末尾几行落到报告里，便于现场判读
        tail = "\n".join((proc.stdout or "").strip().splitlines()[-3:])
        report.append({"id": sid, "run_id": run_id, "desc": desc, "minutes": dt,
                       "runner_exit": proc.returncode, "ok": ok, "detail": detail, "tail": tail})
        print(f"[{now()}] {sid} {'PASS' if ok else 'FAIL'} ({detail}) 用时 {dt} min", flush=True)
        if not ok:
            print(f"[{now()}] 停止：{sid} 未通过。后续步骤不再执行。")
            break

    out = HERE / f"FREEZE_REGRESSION_{datetime.now(UTC8).strftime('%Y%m%dT%H%M%S')}{'_DRYRUN' if dry else ''}.json"
    out.write_text(json.dumps({"started_utc8": now(), "dry_run": dry, "steps": report,
                               "verdict": "DRY_RUN" if dry else ("PASS" if all(s.get("ok") for s in report) and len(report) == len(STEPS) else "FAIL")},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[{now()}] 报告：{out}")
    return 0 if dry or all(s.get("ok") for s in report) else 1


if __name__ == "__main__":
    sys.exit(main())