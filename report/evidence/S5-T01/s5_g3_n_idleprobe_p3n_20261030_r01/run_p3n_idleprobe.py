r"""P3n + idleprobe ELF 定性窗口：渲染 10 帧后停止写帧存、VDMA 继续读 ⇒ 屏上应完全静止。

目的：把「②帧不同步（撕裂/滚动）」与「③像素格式问题」分开：
  · 画面静止不闪 ⇒ 撕裂来自 CPU 边写帧存 + VDMA 边读（修法 fsync/双缓冲同步）；
  · 仍闪/彩色雪花 ⇒ 像素格式/stride/缓存问题；
  · 静止但图案本身彩色块 ⇒ 启动测试图本身的样子，正常。

流程：IDENT → 前置 → hw_server/枚举 → loadhw(P3n XSA) → 停两核 → 0xA → `xsdb fpga -file` P3n
     → 0xF → `load_elf_ddr`(idleprobe ELF) → con → 等 15 s（读 UART，等 RESULT）
     → 杀 hw_server、**不停核、不收窗**（画面挂着）。禁 rst -system。
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
BIT = Path(r"D:\tmp\lead\p3n_video_20261030_r01\out\s4d_p3n_r01.bit")
BIT_SHA = "80b88f1750698e15a1961a2b1ee3081fc9d2c8f5744035e9f119ac82fc9cfcb0"
XSA = Path(r"D:\tmp\lead\p3n_video_20261030_r01\out\s4d_p3n_r01.xsa")
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_idleprobe.elf")
ELF_SHA = "49ca58fd9d6c3ba299997623e43508fcb3a5956cd806133358d29fd402db136f"


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def hhmmss(dt: datetime | None = None) -> str:
    return (dt or datetime.now(UTC8)).strftime("%H:%M:%S")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--settle-seconds", type=float, default=15.0)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3n_idleprobe_hold",
                   "started_utc8": now(), "steps": {},
                   "purpose": "区分②帧不同步 vs ③像素格式：渲染 10 帧后停写帧存、VDMA 继续读 ⇒ 应静止",
                   "forbidden_ops": "禁 rst -system"}

    def step(name: str, payload: dict) -> dict:
        state["steps"][name] = payload
        (run / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
        (run / f"{name}.exit_code.txt").write_text(f"{payload.get('exit_code')}\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] {name}: {payload.get('status')} exit={payload.get('exit_code')}", flush=True)
        return payload

    def finish(stop_reason, hw_pid) -> int:
        td = base.stop_hw_server(hw_pid) if hw_pid else {"listening_3121": base.listening_3121(),
                                                         "residual_processes": []}
        residual = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
        ok_td = td.get("listening_3121") == 0 and not residual
        step("S9_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1,
                             "detail": td, "hw_server_xsdb_residual": residual,
                             "note": "仅杀 hw_server；不停核、不收窗，画面挂着"})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        (run / "results_p3n_idleprobe.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                      encoding="utf-8", newline="\n")
        u = state.get("uart") or {}
        lines = [
            "# P3n + idleprobe 定性窗口（10 帧后停写 ⇒ 应静止）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；释放：{state.get('hold_released_hhmmss')}",
            f"- **HOLD_RELEASED_AT={state.get('hold_released_hhmmss')}**",
            f"- **PL=P3n sha256={sha(BIT)}**",
            f"- **ELF=idleprobe sha256={sha(ELF)}**（{ELF.stat().st_size if ELF.is_file() else 'N/A'} B）",
            f"- `load_elf_ddr` exit={state.get('load_elf_exit')}；fpga_exit={state.get('fpga_exit')}",
            f"- UART 行数={u.get('lines')}；**RESULT 行**：`{u.get('result_line')}`",
            f"- **idle 行**：`{u.get('idle_line')}`", "",
            "## UART 关键行", "", "```", "\n".join(u.get("key_lines") or []), "```", "",
            "- 判读：静止不闪 ⇒ ②帧不同步（需 fsync/双缓冲）；仍闪/彩色雪花 ⇒ ③像素格式/stride/缓存；",
            "  静止但图案为彩色块 ⇒ 启动测试图本身的样子，正常。",
            "- 边界：禁 rst -system；未烧 QSPI；未改线",
        ]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] HOLD_RELEASED_AT={state.get('hold_released_hhmmss')} pl=P3n elf={sha(ELF)[:8]}", flush=True)
        return 0 if ok_td and state.get("criterion_ok") else 1

    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1,
                      "bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
                      "xsa": {"path": str(XSA), "sha256": sha(XSA)},
                      "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA,
                              "size": ELF.stat().st_size if ELF.is_file() else None}})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    srv = base.start_hw_server()
    hw_pid = srv.get("pid")
    step("S2_hw_server", {"status": "PASS" if srv.get("ok") else "FAIL", "exit_code": 0 if srv.get("ok") else 1,
                          "detail": srv})
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
           "{ puts \"LOADHW_SKIP $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "rst -processor -stop; puts RST0_DONE; ",
           'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; puts RST1_DONE; ',
           "disconnect; exit"]
    c4, e4 = drv.xsdb_checked("".join(tcl), "S4_loadhw_stop", timeout=300)
    t4 = (run / "S4_loadhw_stop.log").read_text(encoding="utf-8", errors="replace") if (run / "S4_loadhw_stop.log").is_file() else ""
    b4 = t4.split("exit=", 1)[-1] if "exit=" in t4 else t4
    loadhw_ok = any(ln.strip() == "LOADHW_OK" for ln in b4.splitlines())
    step("S4_loadhw_stop", {"status": "PASS" if (c4 == 0 and e4 is None and loadhw_ok) else "FAIL",
                            "exit_code": 0 if (c4 == 0 and e4 is None and loadhw_ok) else 1,
                            "loadhw_ok": loadhw_ok, "error_text": e4})
    if c4 != 0 or e4 is not None or not loadhw_ok:
        return finish("loadhw/停核失败", hw_pid)

    a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "S4_lvl_0xA")
    if a.get("status") != "PASS":
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
                           "fpga_done": fpga_done, "lvl_0xF": f.get("status"),
                           "lvl_readback_after_on": f.get("readback")})
    if not ok5:
        return finish("P3n 编程失败（停手）", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load_exit = drv.load_elf_ddr(ELF, "S6_load_idleprobe", hold_reset=True)
    logp = run / "S6_load_idleprobe.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    run_state = "Running" if "RUN_STATE Running" in txt else None
    state["load_elf_exit"] = load_exit
    step("S6_load_idleprobe", {"status": "PASS" if (load_exit == 0 and run_state) else "FAIL",
                               "exit_code": 0 if (load_exit == 0 and run_state) else 1,
                               "load_elf_ddr_exit": load_exit, "run_state": run_state,
                               "elapsed_s": round(time.time() - t0, 1)})
    if load_exit != 0 or not run_state:
        return finish("idleprobe ELF 未进入 Running", hw_pid)

    ser = drv._SER.get("ser")
    lines: list[str] = []
    buf = ""
    result_line = None
    idle_line = None
    t_start = time.time()
    while time.time() - t_start < args.settle_seconds:
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
                if s.startswith("S5DISP idle"):
                    idle_line = s
    (run / "S6_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    parsed = {}
    if result_line:
        try:
            parsed = json.loads(result_line.split("=", 1)[1])
        except Exception as exc:  # noqa: BLE001
            parsed = {"parse_error": str(exc)}
    key = [ln for ln in lines if ("RESULT" in ln or "idle" in ln or "UF GPIO" in ln
                                  or "fps_dis" in ln or "hw:" in ln or "done" in ln)]
    uart = {"lines": len(lines), "result_line": result_line, "idle_line": idle_line,
            "parsed": parsed, "key_lines": key[:20], "last_lines": lines[-6:],
            "settle_seconds": args.settle_seconds}
    state["uart"] = uart
    step("S7_uart", {"status": "PASS" if result_line else "FAIL", "exit_code": 0 if result_line else 1,
                     **uart})
    if not result_line:
        return finish("15 s 内无 RESULT（idleprobe 未跑起来）", hw_pid)

    released = datetime.now(UTC8)
    td = base.stop_hw_server(hw_pid)
    residual = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
    state.update({"hold_released_at": released.isoformat(timespec="seconds"),
                  "hold_released_hhmmss": hhmmss(released),
                  "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                  "pl_sha256": sha(BIT), "elf_sha256": sha(ELF),
                  "listening_3121": td.get("listening_3121"), "residual": residual,
                  "note": "idleprobe 为有界程序：已渲染 10 帧并停写帧存，之后 VDMA 继续读 → 屏应静止"})
    step("S8_release", {"status": "PASS" if td.get("listening_3121") == 0 else "FAIL",
                        "exit_code": 0 if td.get("listening_3121") == 0 else 1,
                        "hold_released_at": state["hold_released_hhmmss"],
                        "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                        "listening_3121": td.get("listening_3121"), "residual": residual})
    state["criterion_ok"] = bool(ok5 and load_exit == 0 and result_line)
    state["conclusion"] = "P3N_IDLEPROBE_OK" if state["criterion_ok"] else "P3N_IDLEPROBE_INCOMPLETE"
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())