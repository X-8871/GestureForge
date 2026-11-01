r"""P3c 上的 G3-A 机器侧判据窗口（屏幕类判据挂起）。

背景：屏幕无信号已由厂商参考位流 A/B 对照（`s5_g3_vendorref_20261030_r01`）判定为
      板卡 HDMI 通路/线缆/显示器输入问题，**不是我们的设计**；故本窗口只看机器侧指标。

判据（lead 2026-10-30 指定）：
  · S5DISP RESULT 存在且可解析；pass==1；vdma_err==0；
  · **fps_dis >= 55**（P3c 带宽修复的唯一验证点；同时 <=90 防单位歧义）；
  · fps_upd / frames / vcnt 记录（不判）。
流程：P3b 式四动作 + 编程 P3c `f55a9370…` → load_elf_ddr(有界显示 ELF) → UART 采集（<=60 s）
     → 停两核 → 只读寄存器快照（VTC/VDMA）→ 收窗。禁 rst -system。
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

BIT = Path(r"D:\tmp\lead\p3c_video_20261030_r01\out\s4d_p3c_r01.bit")
BIT_SHA = "f55a93706e2bbdb64f32d60947c4139ab0f2acba32861e14ac76ed0efcd31485"
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf")
ELF_SHA = "e392aa9676b783955c8a70d32040919e457d125959a1c1fa156f2f34ceb6810d"
XSA = Path(r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.xsa")
REGS = [("VTC_CTL", 0x43C30000), ("VTC_GTSTAT", 0x43C30064),
        ("VDMA_MM2S_VDMACR", 0x43C40000), ("VDMA_MM2S_VDMASR", 0x43C40004), ("VDMA_PARKPTR", 0x43C40028)]


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

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "g3a_p3c_machine_only",
                   "started_utc8": now(), "steps": {}, "stop_reason": None,
                   "screen_policy": "屏幕不作为判据：显示器无信号，已由厂商参考位流 A/B 对照"
                                    "（s5_g3_vendorref_20261030_r01）排除我方设计"}

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
        residual_now = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
        ok_td = td.get("listening_3121") == 0 and not residual_now
        step("S9_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1,
                             "detail": td, "hw_server_xsdb_residual": residual_now,
                             "other_heavy_processes_note": "vivado 若存在为他人并行构建，不计入本窗口残留"})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        (run / "results_g3a_p3c.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8", newline="\n")
        parsed = state.get("parsed") or {}
        regs = state.get("registers") or {}
        lines = [
            "# P3c-G3A 机器侧判据窗口（屏幕判据挂起）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state.get('conclusion')}**", f"- stop_reason：{stop_reason}",
            f"- 位流（P3c，带宽修复、oen=1）: `{BIT}` sha256={sha(BIT)}",
            f"- ELF：`{ELF}` sha256={sha(ELF)}",
            f"- S5DISP RESULT：`{state.get('result_line')}`",
            f"- fps_dis={parsed.get('fps_dis')}（判据 >=55）、fps_upd={parsed.get('fps_upd')}、"
            f"pass={parsed.get('pass')}、vdma_err={parsed.get('vdma_err')}、"
            f"frames={parsed.get('frames')}、vcnt={parsed.get('vcnt')}、src={parsed.get('src')}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual_now}",
            "- 屏幕：**不作为判据** —— 显示器无信号，已由厂商参考位流 A/B（`s5_g3_vendorref_20261030_r01`）"
            "判定为板卡 HDMI 通路/线缆/显示器输入问题，非我方设计",
            "- 边界：ENABLE=0；未烧 QSPI；未改线；PL 编程后未用 rst -system", "",
            "## 停机后寄存器（只读）", "",
        ]
        for k, v in (regs.get("values_hex") or {}).items():
            lines.append(f"- `{k}` = {v}（十进制 {regs.get('values_decimal', {}).get(k)}）")
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state.get('conclusion')} stop={stop_reason}", flush=True)
        return 0 if state.get("criterion_ok") and ok_td else 1

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
                          "listening_3121": base.listening_3121(),
                          "note": "要求 vivado 构建已结束（P3e 构建须先完成）、无 xsdb/hw_server 占用"})
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
                                  "bit": str(BIT), "bit_sha256": BIT_SHA,
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
    vdma_period_line = next((ln for ln in lines if "read period" in ln), None)
    step("S6_uart", {"status": "PASS" if result_line else "FAIL", "exit_code": 0 if result_line else 1,
                     "elapsed_s": round(time.time() - t_start, 1), "budget_s": args.collect_seconds,
                     "lines_total": len(lines), "result_seen": bool(result_line),
                     "result_line": result_line, "parsed": parsed,
                     "vdma_read_period_line": vdma_period_line})
    if not result_line:
        return finish("60 s 内无 S5DISP RESULT", hw_pid)

    step("S7_stop_both", stop_both("S7_stop_tcl"))

    # 只读寄存器快照（loadhw 登记地址；不改任何状态）
    xsa = XSA
    tcl = ["connect -url %s; " % base.HW_URL, 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw " + xsa.as_posix() + " -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP: $e\" } else { puts LOADHW_OK }; "]
    for name, addr in REGS:
        tcl.append(f"puts \"REG {name} VAL=[mrd -value {hex(addr)}]\"; ")
    tcl.append("disconnect; exit")
    code_r, err_r = drv.xsdb_checked("".join(tcl), "S8_reg_snapshot", timeout=300)
    logp = run / "S8_reg_snapshot.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    body = txt.split("exit=", 1)[-1] if "exit=" in txt else txt
    values = {}
    for name, _a in REGS:
        m = re.search(r"REG\s+" + re.escape(name) + r"\s+VAL[=\s]+(\S+)", body)
        if m:
            tok = m.group(1).strip()
            values[name] = int(tok, 16) if tok.lower().startswith("0x") else int(tok, 10)
    regs = {"values_decimal": values, "values_hex": {k: hex(v) for k, v in values.items()},
            "loadhw_xsa": str(xsa), "loadhw_xsa_sha256": sha(xsa),
            "loadhw_note": "P3c 无独立 XSA；用 P3b XSA 仅登记地址映射（P3c 与 P3b 的 AXI 地址映射相同）"}
    state["registers"] = regs
    step("S8_reg_snapshot", {"status": "PASS" if (code_r == 0 and len(values) == len(REGS)) else "FAIL",
                             "exit_code": 0 if (code_r == 0 and len(values) == len(REGS)) else 1,
                             "xsdb_exit": code_r, "error_text": err_r, **regs})

    fps = parsed.get("fps_dis")
    pass_ok = parsed.get("pass") == 1
    vdma_ok = parsed.get("vdma_err") == 0
    fps_ok = isinstance(fps, int) and 55 <= fps <= 90
    criterion_ok = bool(pass_ok and vdma_ok and fps_ok)
    state["criterion_ok"] = criterion_ok
    state["parsed"] = parsed
    state["result_line"] = result_line
    state["conclusion"] = "P3C_G3A_PASS" if criterion_ok else "P3C_G3A_FAIL"
    crit = [
        {"id": "K-1", "desc": "S5DISP RESULT 可解析", "pass": "parse_error" not in parsed, "detail": parsed},
        {"id": "K-2", "desc": "pass==1", "pass": pass_ok, "detail": parsed.get("pass")},
        {"id": "K-3", "desc": "vdma_err==0", "pass": vdma_ok, "detail": parsed.get("vdma_err")},
        {"id": "K-4", "desc": "fps_dis>=55（P3c 带宽修复验证点，且<=90）", "pass": fps_ok,
         "detail": {"fps_dis": fps, "fps_upd": parsed.get("fps_upd"),
                    "vdma_read_period_line": vdma_period_line}},
        {"id": "K-5", "desc": "frames/vcnt 记录（不判）", "pass": True,
         "detail": {"frames": parsed.get("frames"), "vcnt": parsed.get("vcnt")}},
    ]
    (run / "W3_judgement.json").write_text(json.dumps({"criteria": crit, "verdict": state["conclusion"],
                                                       "result_line": result_line, "parsed": parsed,
                                                       "utc8": now()}, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    step("S8_judgement", {"status": "PASS" if criterion_ok else "FAIL", "exit_code": 0 if criterion_ok else 1,
                          "criteria": crit})
    return finish(None if criterion_ok else "机器侧判据 FAIL", hw_pid)


if __name__ == "__main__":
    sys.exit(main())