r"""P3h 点屏窗口（P3h = P3g + 解除 VTC gen_clken 反馈环）。

流程（与 r05 完全一致）：IDENT → 前置 → 引脚门禁 → hw_server/枚举 → 选中 A9#0 → loadhw → 停两核
     → SLCR 0xA → `xsdb fpga -file` P3h → SLCR 0xF → load_elf_ddr(长跑 ELF)（内含 init.elf 跑 ps7_init → dow → 0xF → con）
     → UART 采集 120 s（含精确 HOLD_START/HOLD_END HH:MM:SS）→ 停两核 → VTC/VDMA 各 3 次 + 结果块 8 word → 收窗。
禁 rst -system；不写 DDR（除 ELF 装载）。

ps7_init：优先 P3h XSA 内置版；与 P3b XSA 内置版做逐字节比对并记录结果。
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))

import run_window_b_driver as base  # noqa: E402
import run_bringup_driver as drv  # noqa: E402

UTC8 = timezone(timedelta(hours=8))
BIT = Path(r"D:\tmp\lead\p3h_video_20261030_r01\out\s4d_p3h_r01.bit")
BIT_SHA = "b7abd4d1baf46aba954294d63d84bee75a26bd9b043811a3212bc43126a0b297"
XSA = Path(r"D:\tmp\lead\p3h_video_20261030_r01\out\s4d_p3h_r01.xsa")
XSA_SHA = "65e97c5a"
P3B_XSA = Path(r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.xsa")
IO_RPT = Path(r"D:\tmp\lead\p3h_video_20261030_r01\out\io_route.rpt")
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_longrun.elf")
ELF_SHA = "2b08ae9868a6e1dfbff056803fa0d7ee76f54a09edfd9febe6738b2f266d915e"


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def hhmmss() -> str:
    return datetime.now(UTC8).strftime("%H:%M:%S")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def ps7_from_xsa(xsa: Path):
    try:
        with zipfile.ZipFile(xsa) as z:
            names = [n for n in z.namelist() if n.lower().endswith("ps7_init.tcl")]
            if not names:
                return None
            return z.read(names[0])
    except Exception:
        return None


def free_gb():
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullAvailPhys / (1 << 30), 2)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--hold-seconds", type=int, default=120)
    ap.add_argument("--collect-seconds", type=int, default=120)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3h_screen",
                   "started_utc8": now(), "steps": {},
                   "programming_tool": "xsdb fpga -file",
                   "forbidden_ops": "全程禁 rst -system",
                   "purpose": "P3h = P3g + 解除 VTC gen_clken 反馈环；判定亮屏根因是否在 BD 握手"}

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
        (run / "results_p3h.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
        snaps = (state.get("registers") or {}).get("snapshots") or []
        lines = [
            "# P3h 点屏窗口（解除 VTC gen_clken 反馈环）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state.get('conclusion')}**（屏幕现象由现场判读）", f"- stop_reason：{stop_reason}",
            f"- 位流（P3h）：`{BIT}` sha256={sha(BIT)}（{BIT.stat().st_size if BIT.is_file() else 'N/A'} B）",
            f"- XSA：`{XSA}` sha256={sha(XSA)}；P3h XSA ps7_init sha256={state.get('ps7_p3h_sha')}"
            f"（与 P3b {state.get('ps7_p3b_sha')} {'逐字节相同' if state.get('ps7_identical') else '存在差异'}）",
            f"- 长跑 ELF：`{ELF}` sha256={sha(ELF)}",
            f"- 编程工具：xsdb `fpga -file`（fpga_exit={state.get('fpga_exit')}）",
            f"- load_elf_ddr：exit={state.get('load_elf_exit')}",
            f"- **画面保持窗口：{state.get('hold_start_hhmmss')}–{state.get('hold_end_hhmmss')}"
            f"（{state.get('hold_elapsed_s')} s）**",
            f"- UART 机器侧值：{json.dumps((state.get('hold') or {}).get('fps_values') or {}, ensure_ascii=False)}",
            f"- UART 行数={((state.get('hold') or {}).get('lines_total'))}、tick/帧行="
            f"{((state.get('hold') or {}).get('tick_lines'))}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual}", "",
            "## 停机后寄存器时间序列（只读 mrd，间隔 1 s）", "",
        ]
        for i, s in enumerate(snaps):
            lines.append(f"- 第 {i + 1} 次：VTC_CTL={s.get('VTC_CTL')}、VTC_GTSTAT={s.get('VTC_GTSTAT')}、"
                         f"VTC_STATUS={s.get('VTC_STATUS')}、VDMA_CR={s.get('VDMA_CR')}、"
                         f"VDMA_SR={s.get('VDMA_SR')}、VDMA_PARKPTR={s.get('VDMA_PARKPTR')}")
        lines += ["", "## 结果块首 8 word", "",
                  f"```\n{(state.get('registers') or {}).get('result_block_raw', '')}\n```", "",
                  "- 屏幕：现场判读（Wong）；停核后画面消失属正常",
                  "- 边界：禁 rst -system；未烧 QSPI；未改线"]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state.get('conclusion')} stop={stop_reason}", flush=True)
        return 0 if ok_td and state.get("criterion_ok") else 1

    # 输入与 ps7_init 比对
    ident = {"bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
             "xsa": {"path": str(XSA), "sha256": sha(XSA)},
             "elf_longrun": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA}}
    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1, "checks": ident})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    d_h = ps7_from_xsa(XSA)
    d_b = ps7_from_xsa(P3B_XSA)
    state["ps7_p3h_sha"] = hashlib.sha256(d_h).hexdigest() if d_h else None
    state["ps7_p3b_sha"] = hashlib.sha256(d_b).hexdigest() if d_b else None
    state["ps7_identical"] = bool(d_h and d_b and d_h == d_b)
    diff_n = 0
    if d_h and d_b and not state["ps7_identical"]:
        gl = [x.strip() for x in d_h.decode("utf-8", "replace").splitlines()]
        bl = [x.strip() for x in d_b.decode("utf-8", "replace").splitlines()]
        diff_n = len([l for l in difflib.unified_diff(bl, gl, lineterm="")
                      if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))])
    step("S1b_ps7_equiv", {"status": "PASS", "exit_code": 0,
                           "p3h_ps7_sha256": state["ps7_p3h_sha"],
                           "p3b_ps7_sha256": state["ps7_p3b_sha"],
                           "identical": state["ps7_identical"], "diff_lines": diff_n,
                           "note": "load_elf_ddr 用 P3b init.elf 执行同一份（或等价）ps7_init"})

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() != "vivado"]
    fg = free_gb()
    gate_ok = (not others) and base.listening_3121() == 0 and (fg is None or fg >= 3.0)
    step("S2_preflight", {"status": "PASS" if gate_ok else "FAIL", "exit_code": 0 if gate_ok else 1,
                          "heavy_processes": heavy, "non_vivado_heavy": others, "free_gb": fg,
                          "listening_3121": base.listening_3121()})
    if not gate_ok:
        return finish("前置检查未通过（未碰板）", None)

    pins = ["N18", "V20", "T20", "N20"]
    ptxt = IO_RPT.read_text(encoding="utf-8", errors="replace") if IO_RPT.is_file() else ""
    pin_hits = {p: [ln.strip() for ln in ptxt.splitlines() if p in ln][:2] for p in pins}
    pin_ok = all(pin_hits[p] for p in pins)
    step("S2b_pin_check", {"status": "PASS" if pin_ok else "FAIL", "exit_code": 0 if pin_ok else 1,
                           "report": str(IO_RPT), "hits": pin_hits})
    if not pin_ok:
        return finish("引脚复核未通过（未碰板）", None)

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

    tcl = ["connect -url %s; " % base.HW_URL,
           'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw %s -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP: $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "rst -processor -stop; puts RST0_DONE; ",
           'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; puts RST1_DONE; ',
           "disconnect; exit"]
    c4, e4 = drv.xsdb_checked("".join(tcl), "S4_loadhw_stop", timeout=300)
    t4 = (run / "S4_loadhw_stop.log").read_text(encoding="utf-8", errors="replace") if (run / "S4_loadhw_stop.log").is_file() else ""
    b4 = t4.split("exit=", 1)[-1] if "exit=" in t4 else t4
    loadhw_ok = any(ln.strip() == "LOADHW_OK" for ln in b4.splitlines())
    step("S4_loadhw_stop", {"status": "PASS" if (c4 == 0 and e4 is None and loadhw_ok) else "FAIL",
                            "exit_code": 0 if (c4 == 0 and e4 is None and loadhw_ok) else 1,
                            "xsdb_exit": c4, "error_text": e4, "loadhw_ok": loadhw_ok})
    if c4 != 0 or e4 is not None or not loadhw_ok:
        return finish("loadhw/停核失败", hw_pid)

    a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "S4_lvl_0xA")
    if a.get("status") != "PASS":
        step("S5_program_pl", {"status": "FAIL", "exit_code": 1, "reason": "SLCR 0xA 失败", "detail": a})
        return finish("SLCR 0xA 失败", hw_pid)

    tcl = ("connect -url %s; targets -set -filter {name =~ \"*xc7z020*\"}; "
           "fpga -file %s; puts FPGA_FILE_DONE; disconnect; exit" % (base.HW_URL, BIT.as_posix()))
    c5, e5 = drv.xsdb_checked(tcl, "S5_fpga_file", timeout=600)
    logp = run / "S5_fpga_file.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    b5 = txt.split("exit=", 1)[-1] if "exit=" in txt else txt
    fpga_done = "FPGA_FILE_DONE" in b5
    f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "S5_lvl_0xF")
    ok5 = (c5 == 0 and e5 is None and fpga_done and f.get("status") == "PASS")
    state["fpga_exit"] = 0 if (c5 == 0 and fpga_done) else (c5 if c5 else 1)
    step("S5_program_pl", {"status": "PASS" if ok5 else "FAIL", "exit_code": 0 if ok5 else 1,
                           "programming_tool": "xsdb fpga -file", "fpga_exit": state["fpga_exit"],
                           "fpga_done": fpga_done, "fpga_error_text": e5,
                           "bit": str(BIT), "bit_sha256": sha(BIT),
                           "lvl_0xA": a.get("status"), "lvl_0xF": f.get("status"),
                           "lvl_readback_after_on": f.get("readback")})
    if not ok5:
        return finish("P3h 编程失败（停手，不重试）", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load_exit = drv.load_elf_ddr(ELF, "S6_load_longrun", hold_reset=True)
    state["load_elf_exit"] = load_exit
    step("S6_load_longrun", {"status": "PASS" if load_exit == 0 else "FAIL",
                             "exit_code": 0 if load_exit == 0 else 1,
                             "load_elf_ddr_exit": load_exit, "elapsed_s": round(time.time() - t0, 1)})
    if load_exit != 0:
        return finish("ELF 装载失败", hw_pid)

    hold_start_hms = hhmmss()
    ser = drv._SER.get("ser")
    lines: list[str] = []
    buf = ""
    t_start = time.time()
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
    hold_elapsed = round(time.time() - t_start, 1)
    hold_end_hms = hhmmss()
    print(f"[{now()}] HOLD {hold_start_hms}-{hold_end_hms} ({hold_elapsed}s) — 画面保持中/已结束", flush=True)
    (run / "S7_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    fps_seen: dict = {}
    for ln in lines:
        for tok in ln.replace(",", " ").split():
            for k in ("fps_dis", "fps_upd", "vdma_err", "frames", "vcnt"):
                if tok.startswith(k + "="):
                    try:
                        fps_seen.setdefault(k, []).append(int(tok.split("=", 1)[1]))
                    except ValueError:
                        pass
    hold = {"elapsed_s": hold_elapsed, "lines_total": len(lines),
            "tick_lines": len([ln for ln in lines if "tick" in ln.lower() or "S5DISP frame" in ln]),
            "fps_values": {k: sorted(set(v)) for k, v in fps_seen.items()},
            "first_lines": lines[:8], "last_lines": lines[-8:], "tail_partial": buf}
    state["hold"] = hold
    state.update({"hold_start_hhmmss": hold_start_hms, "hold_end_hhmmss": hold_end_hms,
                  "hold_elapsed_s": hold_elapsed})
    step("S7_uart_hold", {"status": "PASS" if lines else "FAIL", "exit_code": 0 if lines else 1,
                          "hold_start_hhmmss": hold_start_hms, "hold_end_hhmmss": hold_end_hms,
                          "uart_lines": len(lines), **hold})
    if not lines:
        return finish("120 s 内 UART 无输出（长跑 ELF 可能未启动）", hw_pid)

    tcl = ["connect -url %s; " % base.HW_URL,
           'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw %s -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP: $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "rst -processor -stop; ",
           'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; puts CORES_STOPPED; ',
           "for {set i 0} {$i < 3} {incr i} { "
           "puts \"SNAP$i VTC_CTL=[mrd -value 0x43C30000] VTC_GTSTAT=[mrd -value 0x43C30064] "
           "VTC_STATUS=[mrd -value 0x43C30004] VDMA_CR=[mrd -value 0x43C40000] "
           "VDMA_SR=[mrd -value 0x43C40004] VDMA_PARKPTR=[mrd -value 0x43C40028]\"; "
           "if {$i < 2} { after 1000 } }; ",
           "puts RBLK_BEGIN; puts [mrd 0x20800000 8]; puts RBLK_END; disconnect; exit"]
    c8, e8 = drv.xsdb_checked("".join(tcl), "S8_reg_snapshot", timeout=600)
    t8 = (run / "S8_reg_snapshot.log").read_text(encoding="utf-8", errors="replace") if (run / "S8_reg_snapshot.log").is_file() else ""
    b8 = t8.split("exit=", 1)[-1] if "exit=" in t8 else t8
    snaps = []
    for m in re.finditer(r"SNAP(\d).*?VTC_CTL[=\s]+(\S+).*?VTC_GTSTAT[=\s]+(\S+).*?VTC_STATUS[=\s]+(\S+)"
                         r".*?VDMA_CR[=\s]+(\S+).*?VDMA_SR[=\s]+(\S+).*?VDMA_PARKPTR[=\s]+(\S+)", b8):
        def dec(x):
            try:
                return int(x, 16) if x.lower().startswith("0x") else int(x, 10)
            except Exception:
                return x
        snaps.append({"VTC_CTL": dec(m.group(2)), "VTC_GTSTAT": dec(m.group(3)), "VTC_STATUS": dec(m.group(4)),
                      "VDMA_CR": dec(m.group(5)), "VDMA_SR": dec(m.group(6)), "VDMA_PARKPTR": dec(m.group(7))})
    rblk = ""
    if "RBLK_BEGIN" in b8 and "RBLK_END" in b8:
        rblk = b8.split("RBLK_BEGIN", 1)[1].split("RBLK_END", 1)[0].strip()
    state["registers"] = {"snapshots": snaps, "result_block_raw": rblk, "error_text": e8}
    step("S8_reg_snapshot", {"status": "PASS" if (c8 == 0 and len(snaps) == 3) else "FAIL",
                             "exit_code": 0 if (c8 == 0 and len(snaps) == 3) else 1,
                             "xsdb_exit": c8, "error_text": e8, "snapshots": snaps,
                             "result_block_raw": rblk})

    state["criterion_ok"] = bool(ok5 and load_exit == 0 and lines and c8 == 0 and len(snaps) == 3)
    state["conclusion"] = "P3H_WINDOW_OK" if state["criterion_ok"] else "P3H_INCOMPLETE"
    step("S9_judgement", {"status": "PASS" if state["criterion_ok"] else "FAIL",
                          "exit_code": 0 if state["criterion_ok"] else 1,
                          "note": "只判执行完整性；亮屏由现场判读", "conclusion": state["conclusion"]})
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())