r"""空闲测速窗口（P3b）：渲染 10 帧 → 停写 → VDMA 空跑 3 s → 打 idle 行与 RESULT。

取证目标（不判 PASS/FAIL）：
  · `S5DISP idle fps_dis=.. period_us=.. frames=.. vcnt=.. err=..`
  · `S5DISP RESULT={... ` 含 fps_dis（渲染阶段）、fps_dis_idle、idle_period_us
判读由 lead 侧做：
  · idle 也只有 ~52 ⇒ VDMA/HP2 通路本身不够（smc_vid AXI4→AXI3 + 单 outstanding 嫌疑）
  · idle ≈60 ⇒ 渲染期 CPU 写 DDR 与 VDMA 读抢带宽

流程：P3b 位流 + idleprobe ELF；四动作编程、load_elf_ddr、UART 采集至 RESULT、停核、收窗。禁 rst -system。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))

import run_window_b_driver as base  # noqa: E402
import run_bringup_driver as drv  # noqa: E402

UTC8 = timezone(timedelta(hours=8))
BIT = Path(r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.bit")
BIT_SHA = "1670b0b38e4fef7ffe8021a99e4c9a1c0a92724e84f13d3fe5a8ca77a7b6f572"
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_idleprobe.elf")
ELF_SHA = "922a97859605ad12211dfdaa8245f3fb0ffac5d58f5337768af5f86caea960db"


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--collect-seconds", type=int, default=60)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "idle_probe_p3b",
                   "started_utc8": now(), "steps": {}, "stop_reason": None,
                   "judgement_policy": "只取证，不判 PASS/FAIL（lead 侧分析带宽/竞争假设）"}

    def step(name: str, payload: dict) -> dict:
        state["steps"][name] = payload
        (run / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
        (run / f"{name}.exit_code.txt").write_text(f"{payload.get('exit_code')}\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] {name}: {payload.get('status')} exit={payload.get('exit_code')}", flush=True)
        return payload

    def finish(stop_reason, hw_pid) -> int:
        ser = drv._SER.get("ser")
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
        td = base.stop_hw_server(hw_pid) if hw_pid else {"listening_3121": base.listening_3121(),
                                                         "residual_processes": []}
        residual = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
        ok_td = td.get("listening_3121") == 0 and not residual
        step("S9_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1,
                             "detail": td, "hw_server_xsdb_residual": residual})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        state["conclusion"] = "IDLE_PROBE_CAPTURED" if (state.get("idle_line") and state.get("result_line")) else "IDLE_PROBE_INCOMPLETE"
        (run / "results_idleprobe.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8", newline="\n")
        p = state.get("parsed") or {}
        lines = [
            "# 空闲测速窗口（P3b + idleprobe ELF）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state['conclusion']}**（只取证，不判 PASS/FAIL）",
            f"- 位流（P3b）：`{BIT}` sha256={sha(BIT)}",
            f"- ELF（idleprobe）：`{ELF}` sha256={sha(ELF)}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual}", "",
            "## 两行原文", "", "```", state.get("idle_line") or "(未收到)", "```", "```",
            state.get("result_line") or "(未收到)", "```", "",
            f"- fps_dis（渲染阶段）= {p.get('fps_dis')}",
            f"- fps_dis_idle（空闲阶段）= {p.get('fps_dis_idle')}",
            f"- idle_period_us = {p.get('idle_period_us')}",
            f"- frames = {p.get('frames')}、vcnt = {p.get('vcnt')}、vdma_err = {p.get('vdma_err')}、pass = {p.get('pass')}",
            "",
            "- 屏幕：无信号（已知硬件问题：厂商参考位流 A/B 已排除我方设计）；不作为判据",
            "- 边界：ENABLE=0；未烧 QSPI；未改线；PL 编程后未用 rst -system", "",
            "## 判读方向（lead 侧）", "",
            "- idle 也 ~52 ⇒ VDMA/HP2 通路本身不够（smc_vid AXI4→AXI3 转换 + 单 outstanding 嫌疑）",
            "- idle ≈60 ⇒ 渲染期 CPU 写 DDR 与 VDMA 读抢带宽",
        ]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state['conclusion']} stop={stop_reason}", flush=True)
        return 0 if ok_td and state["conclusion"] == "IDLE_PROBE_CAPTURED" else 1

    ident = {"bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
             "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA},
             "init_elf": {"path": str(drv.INIT_ELF), "sha256": sha(drv.INIT_ELF), "expect": "237dd959"}}
    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA and sha(drv.INIT_ELF).startswith("237dd959")
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1, "checks": ident})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() not in ("vivado",)]
    gate_ok = (not others) and base.listening_3121() == 0
    step("S2_preflight", {"status": "PASS" if gate_ok else "FAIL", "exit_code": 0 if gate_ok else 1,
                          "heavy_processes": heavy, "non_vivado_heavy": others,
                          "listening_3121": base.listening_3121()})
    if not gate_ok:
        return finish("前置检查未通过（未碰板）", None)

    srv = base.start_hw_server()
    hw_pid = srv.get("pid")
    step("S3_hw_server", {"status": "PASS" if srv.get("ok") else "FAIL",
                          "exit_code": 0 if srv.get("ok") else 1, "detail": srv})
    if not srv.get("ok"):
        return finish("hw_server 未就绪", hw_pid)

    enum_ok = False
    for i in range(1, 4):
        tcl = "connect -url %s; puts E_BEGIN; puts [targets]; puts E_END; disconnect; exit" % base.HW_URL
        code, err = drv.xsdb_checked(tcl, f"S3_enum_{i}", timeout=300)
        logp = run / f"S3_enum_{i}.log"
        txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
        tail = txt.split("exit=", 1)[-1]
        lst = tail.split("E_BEGIN", 1)[1].split("E_END", 1)[0].strip() if "E_BEGIN" in tail else ""
        enum_ok = (code == 0 and err is None and "Cortex-A9" in lst and "xc7z020" in lst)
        if enum_ok:
            break
        time.sleep(5)
    step("S3_enum", {"status": "PASS" if enum_ok else "FAIL", "exit_code": 0 if enum_ok else 1})
    if not enum_ok:
        return finish("枚举失败", hw_pid)

    def stop_both(tag: str) -> dict:
        tcl = ("connect -url %s; " % base.HW_URL
               + 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; rst -processor -stop; after 300; '
               + 'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; after 300; '
               + 'puts BOTH_STOPPED; disconnect; exit')
        c, e = drv.xsdb_checked(tcl, tag, timeout=300)
        return {"status": "PASS" if (c == 0 and e is None) else "FAIL",
                "exit_code": 0 if (c == 0 and e is None) else 1, "xsdb_exit": c, "error_text": e}

    step("S4_prestop_both", stop_both("S4_prestop_tcl"))
    if state["steps"]["S4_prestop_both"]["exit_code"] != 0:
        return finish("预停核失败", hw_pid)

    a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "S4_lvl_0xA")
    cp = base.program_pl(BIT, BIT_SHA[:8]) if a.get("status") == "PASS" else 1
    f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "S4_lvl_0xF") if cp == 0 else {"status": "FAIL"}
    ok4 = a.get("status") == "PASS" and cp == 0 and f.get("status") == "PASS"
    pl_log = (run / "PL_program.log").read_text(encoding="utf-8", errors="replace") if (run / "PL_program.log").is_file() else ""
    step("S4_pspl_four_actions", {"status": "PASS" if ok4 else "FAIL", "exit_code": 0 if ok4 else 1,
                                  "lvl_0xA": a.get("status"), "program_pl_exit": cp, "lvl_0xF": f.get("status"),
                                  "program_ok_in_log": "PROGRAM_OK" in pl_log,
                                  "startup_high_in_log": "End of startup status: HIGH" in pl_log})
    if not ok4:
        return finish("四动作/编程失败", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load = drv.load_elf_ddr(ELF, "S5_load_display", hold_reset=True)
    step("S5_load_display", {"status": "PASS" if load == 0 else "FAIL", "exit_code": 0 if load == 0 else 1,
                             "load_exit": load, "elapsed_s": round(time.time() - t0, 1)})
    if load != 0:
        return finish("ELF 装载失败", hw_pid)

    ser = drv.ensure_uart()
    lines: list[str] = []
    buf = ""
    t_start = time.time()
    result_line = None
    idle_line = None
    while time.time() - t_start < args.collect_seconds:
        chunk = ser.read(4096)
        if not chunk:
            continue
        buf += chunk.decode("utf-8", "replace")
        while "\n" in buf:
            raw_ln, buf = buf.split("\n", 1)
            s = raw_ln.strip()
            if s:
                lines.append(s)
                if s.startswith("S5DISP idle"):
                    idle_line = s
                if s.startswith("S5DISP RESULT="):
                    result_line = s
                    break
        if result_line:
            break
    (run / "S5DISP_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    parsed: dict = {}
    if result_line:
        try:
            parsed = json.loads(result_line.split("=", 1)[1])
        except Exception as exc:  # noqa: BLE001
            parsed = {"parse_error": str(exc)}
    # 兜底：若 RESULT 没给 fps_dis_idle，从 idle 行解析
    if idle_line and "fps_dis_idle" not in parsed:
        m = re.search(r"fps_dis[= ]+(\d+)", idle_line)
        if m and "fps_dis_idle" not in parsed:
            parsed["fps_dis_idle_from_idle_line"] = int(m.group(1))
        m2 = re.search(r"period_us[= ]+(\d+)", idle_line)
        if m2:
            parsed.setdefault("idle_period_us_from_idle_line", int(m2.group(1)))
    state.update({"result_line": result_line, "idle_line": idle_line, "parsed": parsed})
    step("S6_uart", {"status": "PASS" if (result_line and idle_line) else "FAIL",
                     "exit_code": 0 if (result_line and idle_line) else 1,
                     "elapsed_s": round(time.time() - t_start, 1), "lines_total": len(lines),
                     "idle_line": idle_line, "result_line": result_line, "parsed": parsed})

    step("S7_stop_both", stop_both("S7_stop_tcl"))
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())