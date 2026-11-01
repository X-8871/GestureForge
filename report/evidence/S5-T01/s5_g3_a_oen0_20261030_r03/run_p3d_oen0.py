r"""P3d 诊断窗口（hdmi_oen 常量 0）：编程 P3d → 装载有界显示 ELF → 采 UART → 停机后只读寄存器快照。

判读（本轮不做 J-4）：
  · S5DISP RESULT pass==1；
  · VTC 在生成：CTL(0x43C30000) bit0/bit2 置位、GTSTAT(0x43C30064) != 0；
  · VDMA 无错：MM2S_VDMASR(0x43C40004) 的 Err 位（bit3/4/5/12）为 0；
  · 结果块 0x20800000 首 8 word（magic/status）记录供人工判读。
禁止：rst -system；除 2B 四动作 SLCR 白名单外的任何 mwr（本窗口无 G3-B 种子写入）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))

import run_window_b_driver as base  # noqa: E402
import run_bringup_driver as drv  # noqa: E402

UTC8 = timezone(timedelta(hours=8))

DEFAULT_BIT = Path(r"D:\tmp\lead\p3d_video_20261030_r01\out\s4d_p3d_r01.bit")
DEFAULT_BIT_SHA = "f6488e4a65b7057b8da8079816b983f9ca334157c8d43627801398e9b67c0187"
DEFAULT_ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf")
DEFAULT_ELF_SHA = "e392aa9676b783955c8a70d32040919e457d125959a1c1fa156f2f34ceb6810d"

REGS = [
    ("VTC_CTL", 0x43C30000),
    ("VTC_GTSTAT", 0x43C30064),
    ("VTC_STATUS", 0x43C30004),
    ("VDMA_MM2S_VDMACR", 0x43C40000),
    ("VDMA_MM2S_VDMASR", 0x43C40004),
    ("VDMA_PARKPTR", 0x43C40028),
]
RESULT_BLOCK = 0x20800000


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--bit", default=str(DEFAULT_BIT))
    ap.add_argument("--expect-bit-sha", default=DEFAULT_BIT_SHA)
    ap.add_argument("--elf", default=str(DEFAULT_ELF))
    ap.add_argument("--expect-elf-sha", default=DEFAULT_ELF_SHA)
    ap.add_argument("--collect-seconds", type=int, default=50)
    ap.add_argument("--xsa", default=r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.xsa",
                    help="用于 loadhw 登记 PL AXI 地址映射（P3d 位级改动，地址映射同 P3b）")
    args = ap.parse_args()

    bit = Path(args.bit)
    elf = Path(args.elf)
    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3d_oen0",
                   "started_utc8": now(), "steps": {}, "stop_reason": None,
                   "authorization_note": "lead 2026-10-30 诊断窗口；禁 rst -system；写操作仅 2B 四动作 SLCR 白名单"}

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
                                                         "residual_processes": base.heavy_processes()}
        ok_td = td.get("listening_3121") == 0 and not td.get("residual_processes")
        step("S9_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1, "detail": td})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        state["teardown_ok"] = ok_td
        (run / "results_p3d_oen0.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8", newline="\n")
        regs = state.get("registers") or {}
        lines = [
            "# P3d 诊断窗口（hdmi_oen=0）记录", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state.get('conclusion')}**", f"- stop_reason：{stop_reason}",
            f"- 位流（P3d，oen 常量 0）：`{bit}` sha256={sha(bit)}",
            f"- ELF：`{elf}` sha256={sha(elf)}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、残留={td.get('residual_processes')}",
            "- 边界：禁 rst -system；除 SLCR 白名单外无 mwr；不做 J-4 判据；屏幕现象需人工目视", "",
            "## 停机后寄存器快照（只读 mrd）", "",
        ]
        for name, val in regs.get("values_hex", {}).items():
            lines.append(f"- `{name}` = {val}")
        lines += ["", "## 结果块首 8 word", "", f"```\n{regs.get('result_block_raw', '')}\n```", "",
                  "## S5DISP 关键行", ""]
        for ln in (state.get("uart_key_lines") or []):
            lines.append(f"```\n{ln}\n```")
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state.get('conclusion')} stop={stop_reason}", flush=True)
        return 0 if (state.get("criterion_ok") and ok_td) else 1

    ident = {"bit": {"path": str(bit), "sha256": sha(bit), "expect": args.expect_bit_sha},
             "elf": {"path": str(elf), "sha256": sha(elf), "expect": args.expect_elf_sha},
             "init_elf": {"path": str(drv.INIT_ELF), "sha256": sha(drv.INIT_ELF), "expect": "237dd959"}}
    id_ok = (sha(bit) == args.expect_bit_sha and sha(elf) == args.expect_elf_sha
             and sha(drv.INIT_ELF).startswith("237dd959"))
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1, "checks": ident})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    p0 = drv.p0_gate()
    p0["exit_code"] = 0 if p0.get("ok") else 1
    step("S2_P0_gate", p0)
    if not p0.get("ok"):
        return finish("P0 门禁未通过（未碰板）", None)

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
    cp = base.program_pl(bit, args.expect_bit_sha[:8]) if a.get("status") == "PASS" else 1
    f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "S4_lvl_0xF") if cp == 0 else {"status": "FAIL"}
    ok4 = a.get("status") == "PASS" and cp == 0 and f.get("status") == "PASS"
    step("S4_pspl_four_actions", {"status": "PASS" if ok4 else "FAIL", "exit_code": 0 if ok4 else 1,
                                  "lvl_0xA": a.get("status"), "program_pl_exit": cp, "lvl_0xF": f.get("status"),
                                  "bit": str(bit), "bit_prefix": args.expect_bit_sha[:8]})
    if not ok4:
        return finish("四动作/编程失败", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load = drv.load_elf_ddr(elf, "S5_load_display", hold_reset=True)
    step("S5_load_display", {"status": "PASS" if load == 0 else "FAIL", "exit_code": 0 if load == 0 else 1,
                             "load_exit": load, "elapsed_s": round(time.time() - t0, 1), "elf": str(elf)})
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
    key_lines = [ln for ln in lines if ln.startswith(("S5DISP RESULT=", "S5DISP done", "S5DISP frame=180",
                                                      "VTC:", "VDMA:", "S5DISP boxes"))]
    state["uart_key_lines"] = key_lines
    parsed = {}
    if result_line:
        try:
            parsed = json.loads(result_line.split("=", 1)[1])
        except Exception as exc:  # noqa: BLE001
            parsed = {"parse_error": str(exc)}
    step("S6_uart", {"status": "PASS" if result_line else "FAIL", "exit_code": 0 if result_line else 1,
                     "elapsed_s": round(time.time() - t_start, 1), "lines_total": len(lines),
                     "result_seen": bool(result_line), "result_line": result_line, "parsed": parsed})

    step("S7_stop_both", stop_both("S7_stop_tcl"))

    # 停机后只读寄存器快照
    tcl = ["connect -url %s; " % base.HW_URL, 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ']
    xsa = Path(args.xsa)
    tcl.append("if {[catch {loadhw -hw " + xsa.as_posix()
               + " -mem-ranges {0x00000000 0x7FFFFFFF}} e]} { puts \"LOADHW_SKIP: $e\" } else { puts LOADHW_OK }; ")
    for name, addr in REGS:
        tcl.append(f"puts \"REG {name}={hex(addr)} VAL=[mrd -value {hex(addr)}]\"; ")
    tcl.append(f"puts \"RBLK_BEGIN\"; puts [mrd {hex(RESULT_BLOCK)} 8]; puts \"RBLK_END\"; ")
    tcl.append("disconnect; exit")
    code, err = drv.xsdb_checked("".join(tcl), "S8_reg_snapshot", timeout=300)
    logp = run / "S8_reg_snapshot.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    body = txt.split("exit=", 1)[-1] if "exit=" in txt else txt
    values_hex: dict = {}
    import re as _re
    for name, _addr in REGS:
        for ln in body.splitlines():
            m = _re.search(r"REG\s+" + _re.escape(name) + r"\b.*?VAL[=\s]+(\S+)", ln)
            if m:
                values_hex[name] = m.group(1).strip()
    rblk = ""
    if "RBLK_BEGIN" in body and "RBLK_END" in body:
        rblk = body.split("RBLK_BEGIN", 1)[1].split("RBLK_END", 1)[0].strip()
    def num(name):
        v = values_hex.get(name, "")
        try:
            return int(v, 16) if v.lower().startswith("0x") else int(v, 10)
        except Exception:
            return None
    ctl = num("VTC_CTL")
    gtstat = num("VTC_GTSTAT")
    sr = num("VDMA_MM2S_VDMASR")
    vtc_ok = bool(ctl is not None and (ctl & 0x5) == 0x5) and gtstat not in (None, 0)
    # AXI VDMA SR：bit3 DMAIntErr / bit4 DMASlvErr / bit5 DMADecErr 为错误位；
    # bit12 Err_Irq 是"错误中断已置起"的汇总状态位，单独记录、不并入错误判据（PG020）。
    err_bits = (sr & 0x38) if isinstance(sr, int) else None
    err_irq_latched = bool(isinstance(sr, int) and (sr & 0x1000))
    vdma_ok = err_bits == 0 if err_bits is not None else False
    regs = {"values_hex": values_hex, "raw_log": txt, "result_block_raw": rblk,
            "vtc_ctl": ctl, "vtc_gtstat": gtstat, "vdma_sr": sr, "vdma_err_bits": err_bits,
            "vdma_err_irq_latched_bit12": err_irq_latched}
    state["registers"] = regs
    step("S8_reg_snapshot", {"status": "PASS" if (code == 0 and err is None and len(values_hex) == len(REGS)) else "FAIL",
                             "exit_code": 0 if (code == 0 and err is None and len(values_hex) == len(REGS)) else 1,
                             "xsdb_exit": code, "error_text": err,
                             "loadhw_xsa": str(xsa), "loadhw_xsa_sha256": sha(xsa),
                             "loadhw_note": "P3d 无独立 XSA；用 P3b XSA 仅登记地址映射（P3d 只改 hdmi_oen 常量）",
                             **regs})

    pass_ok = parsed.get("pass") == 1
    criterion_ok = bool(pass_ok and vtc_ok and vdma_ok)
    state["criterion_ok"] = criterion_ok
    state["conclusion"] = "P3D_DIAG_PASS" if criterion_ok else "P3D_DIAG_CHECK"
    step("S9_judgement", {"status": "PASS" if criterion_ok else "FAIL", "exit_code": 0 if criterion_ok else 1,
                          "pass_ok": pass_ok, "vtc_generating": vtc_ok, "vdma_no_err": vdma_ok,
                          "vtc_ctl": ctl, "vtc_gtstat": gtstat, "vdma_sr": sr, "vdma_err_bits": err_bits,
                          "note": "本轮不做 J-4（fps_dis 已知 52，等 P3c）；屏幕现象需人工目视"})
    return finish(None if criterion_ok else "诊断项未满足", hw_pid)


if __name__ == "__main__":
    sys.exit(main())