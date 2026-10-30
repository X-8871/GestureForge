r"""P3n 窗口（候选 A：数据面 100 MHz，保 720p60）：烧 P3n + P3m 长跑 ELF 出画面，并量化运行期欠载。

流程：IDENT → 前置 → hw_server/枚举 → loadhw(P3n XSA) → 停两核 → 0xA → `xsdb fpga -file` P3n
     → 0xF → `load_elf_ddr`(P3m 长跑 ELF) → con → **等 8 s（越过开流前空档）**
     → 只读采样 `0x43C10000` 25 次/200 ms（带 TCL 毫秒时间戳）+ 读 VDMA CR/SR
     → 杀 hw_server、**不停核、不收窗**（画面继续挂）。
禁 rst -system；采样期间不 rst -processor。
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
BIT = Path(r"D:\tmp\lead\p3n_video_20261030_r01\out\s4d_p3n_r01.bit")
BIT_SHA = "80b88f1750698e15a1961a2b1ee3081fc9d2c8f5744035e9f119ac82fc9cfcb0"
XSA = Path(r"D:\tmp\lead\p3n_video_20261030_r01\out\s4d_p3n_r01.xsa")
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_longrun.elf")
ELF_SHA = "2481b2d17b96ce65b1a6d2cc1284f824e98ca0ecc97fb9f1b57869cb846530e4"
PIXEL_RATE = 1280 * 720 * 60
TIME_CAP_S = 1800


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def hhmmss(dt: datetime | None = None) -> str:
    return (dt or datetime.now(UTC8)).strftime("%H:%M:%S")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--samples", type=int, default=25)
    ap.add_argument("--interval-ms", type=int, default=200)
    ap.add_argument("--settle-seconds", type=float, default=8.0)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3n_hold_ufsample",
                   "started_utc8": now(), "steps": {},
                   "candidate": "A：数据面(VDMA MM/HP2) 100 MHz，保 720p60",
                   "programming_tool": "xsdb fpga -file",
                   "reference_pixel_rate_px_s": PIXEL_RATE,
                   "forbidden_ops": "禁 rst -system；采样期不 rst -processor"}

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
                             "note": "仅杀 hw_server；不停核、不收窗，画面继续挂"})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        (run / "results_p3n.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
        s = state.get("sample") or {}
        u = state.get("uart") or {}
        lines = [
            "# P3n 窗口（候选 A：数据面 100 MHz，保 720p60）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；释放：{state.get('hold_released_hhmmss')}",
            f"- **HOLD_RELEASED_AT={state.get('hold_released_hhmmss')}**",
            f"- **EXPECTED_UNTIL={state.get('expected_until_hhmmss')}**（长跑上限 {TIME_CAP_S} s，按 con 折算）",
            f"- **cores=RUNNING**、**hw_server=killed**（3121 LISTENING={td.get('listening_3121')}、残留={residual}）",
            f"- **PL=P3n sha256={sha(BIT)}**",
            f"- ELF（P3m 长跑）：`{ELF}` sha256={sha(ELF)}",
            f"- 位流：`{BIT}`（{BIT.stat().st_size if BIT.is_file() else 'N/A'} B）",
            f"- 执行：loadhw → 停两核 → 0xA → `xsdb fpga -file`（fpga_exit={state.get('fpga_exit')}）→ 0xF → "
            f"`load_elf_ddr`（exit={state.get('load_elf_exit')}）→ con → 等 {args.settle_seconds}s → 采样", "",
            "## UF 原始值（0x43C10000，每 200 ms）", "",
            "| # | 值 | hex |", "|---|---|---|",
        ]
        for i, v in enumerate(s.get("values") or []):
            lines.append(f"| {i} | {v} | {hex(v) if isinstance(v, int) else v} |")
        lines += [
            "", f"- 首值={s.get('first')}、末值={s.get('last')}、跨度={s.get('span_ms')} ms",
            f"- **差值={s.get('delta')} px ⇒ {s.get('rate_px_s')} px/s ⇒ 占有效像素率 "
            f"{s.get('ratio_vs_pixel_rate')}**",
            f"- VDMA_CR={s.get('vdma_cr')}（{hex(s.get('vdma_cr')) if isinstance(s.get('vdma_cr'), int) else ''}）、"
            f"VDMA_SR={s.get('vdma_sr')}（{hex(s.get('vdma_sr')) if isinstance(s.get('vdma_sr'), int) else ''}）",
            f"- 判读：{s.get('verdict_text')}", "",
            "## UART（fps_dis / tick / RESULT）", "", "```",
            "\n".join(u.get("key_lines") or []), "```", "",
            "- 边界：禁 rst -system；采样不 rst -processor；未烧 QSPI；未改线",
        ]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] HOLD_RELEASED_AT={state.get('hold_released_hhmmss')} "
              f"rate={s.get('rate_px_s')} px/s ratio={s.get('ratio_vs_pixel_rate')}", flush=True)
        return 0 if ok_td and state.get("criterion_ok") else 1

    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1,
                      "bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
                      "xsa": {"path": str(XSA), "sha256": sha(XSA)},
                      "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA}})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() != "vivado"]
    gate_ok = (not others) and base.listening_3121() == 0
    step("S2_preflight", {"status": "PASS" if gate_ok else "FAIL", "exit_code": 0 if gate_ok else 1,
                          "heavy_processes": heavy, "non_vivado_heavy": others,
                          "listening_3121": base.listening_3121(),
                          "note": "会重配 PL：先停两核；当前 P3m hold 将被替换为 P3n"})
    if not gate_ok:
        return finish("前置检查未通过（未碰板）", None)

    srv = base.start_hw_server()
    hw_pid = srv.get("pid")
    step("S3_hw_server", {"status": "PASS" if srv.get("ok") else "FAIL", "exit_code": 0 if srv.get("ok") else 1,
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
                           "fpga_done": fpga_done, "fpga_error_text": e5,
                           "lvl_0xF": f.get("status"), "lvl_readback_after_on": f.get("readback")})
    if not ok5:
        return finish("P3n 编程失败（停手）", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load_exit = drv.load_elf_ddr(ELF, "S6_load_longrun", hold_reset=True)
    logp = run / "S6_load_longrun.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    run_state = "Running" if "RUN_STATE Running" in txt else None
    state["load_elf_exit"] = load_exit
    step("S6_load_longrun", {"status": "PASS" if (load_exit == 0 and run_state) else "FAIL",
                             "exit_code": 0 if (load_exit == 0 and run_state) else 1,
                             "load_elf_ddr_exit": load_exit, "run_state": run_state,
                             "elapsed_s": round(time.time() - t0, 1)})
    if load_exit != 0 or not run_state:
        return finish("长跑 ELF 未进入 Running", hw_pid)

    # 等 8 s：同时读 UART（越过开流前空档）
    ser = drv._SER.get("ser")
    lines_uart: list[str] = []
    buf = ""
    t_wait = time.time()
    while time.time() - t_wait < args.settle_seconds:
        chunk = ser.read(4096)
        if not chunk:
            continue
        buf += chunk.decode("utf-8", "replace")
        while "\n" in buf:
            raw_ln, buf = buf.split("\n", 1)
            s = raw_ln.strip()
            if s:
                lines_uart.append(s)
    state["settle_seconds"] = args.settle_seconds

    # 只读采样（不 rst）
    tcl = ["connect -url %s; " % base.HW_URL,
           'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw %s -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "puts SAMPLE_BEGIN; ",
           f"for {{set i 0}} {{$i < {args.samples}}} {{incr i}} {{ "
           f"set t [clock milliseconds]; "
           f"puts \"UF$i [mrd -value 0x43C10000] T $t\"; "
           f"if {{$i < {args.samples - 1}}} {{ after {args.interval_ms} }} }}; ",
           "puts SAMPLE_END; ",
           "puts \"VDMA_CR [mrd -value 0x43C00000]\"; ",
           "puts \"VDMA_SR [mrd -value 0x43C00004]\"; ",
           "disconnect; exit"]
    c7, e7 = drv.xsdb_checked("".join(tcl), "S7_uf_sample", timeout=600)
    logp = run / "S7_uf_sample.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    b7 = txt.split("exit=", 1)[-1] if "exit=" in txt else txt
    pairs = [(int(m.group(1)), int(m.group(2)), int(m.group(3)))
             for m in re.finditer(r"UF(\d+)\s+(\d+)\s+T\s+(\d+)", b7)]
    pairs.sort()
    values = [p[1] for p in pairs]
    times = [p[2] for p in pairs]
    vdma_cr = vdma_sr = None
    for m in re.finditer(r"VDMA_CR\s+(\d+)", b7):
        vdma_cr = int(m.group(1))
    for m in re.finditer(r"VDMA_SR\s+(\d+)", b7):
        vdma_sr = int(m.group(1))
    sample: dict = {"values": values, "first": values[0] if values else None,
                    "last": values[-1] if values else None,
                    "delta": (values[-1] - values[0]) if len(values) > 1 else None,
                    "span_ms": (times[-1] - times[0]) if len(times) > 1 else None,
                    "vdma_cr": vdma_cr, "vdma_sr": vdma_sr, "error_text": e7}
    if sample["delta"] is not None and sample["span_ms"]:
        rate = sample["delta"] / (sample["span_ms"] / 1000.0)
        ratio = rate / PIXEL_RATE
        sample.update({"rate_px_s": round(rate, 1), "ratio_vs_pixel_rate": round(ratio, 4)})
        if ratio < 0.01:
            vt = "欠载率 <1% ⇒ 候选 A 成功（100 MHz 有效），画质应干净"
        elif ratio < 0.05:
            vt = "欠载率 1–5% ⇒ 100 MHz 有改善但仍轻微欠载"
        elif ratio < 0.16:
            vt = "欠载率 ≈13% ⇒ 100 MHz 无效（与 P3m 相同），需候选 B（720p50）"
        else:
            vt = "欠载率 >16% ⇒ 明显更差，需排查"
        sample["verdict_text"] = vt
    else:
        sample.update({"rate_px_s": None, "ratio_vs_pixel_rate": None,
                       "verdict_text": "采样值不足，无法计算速率"})
    state["sample"] = sample
    step("S7_uf_sample", {"status": "PASS" if len(values) == args.samples else "FAIL",
                          "exit_code": 0 if len(values) == args.samples else 1, **sample})

    # 采样后再读 2 s UART，凑 fps_dis/tick 行；然后释放
    t_extra = time.time()
    while time.time() - t_extra < 2.0:
        chunk = ser.read(4096)
        if not chunk:
            continue
        buf += chunk.decode("utf-8", "replace")
        while "\n" in buf:
            raw_ln, buf = buf.split("\n", 1)
            s = raw_ln.strip()
            if s:
                lines_uart.append(s)
    (run / "S6_uart.log").write_text("\n".join(lines_uart) + "\n", encoding="utf-8", newline="\n")
    key = [ln for ln in lines_uart if ("fps_dis" in ln or "tick" in ln or "RESULT" in ln
                                       or "VDMA" in ln or "hw:" in ln)]
    state["uart"] = {"lines": len(lines_uart), "key_lines": key[:20], "last_lines": lines_uart[-6:]}
    step("S8_uart", {"status": "PASS" if lines_uart else "FAIL", "exit_code": 0 if lines_uart else 1,
                     **state["uart"]})

    released = datetime.now(UTC8)
    td = base.stop_hw_server(hw_pid)
    residual = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
    expected = released + timedelta(seconds=TIME_CAP_S - (args.settle_seconds + 12))
    state.update({"hold_released_at": released.isoformat(timespec="seconds"),
                  "hold_released_hhmmss": hhmmss(released),
                  "expected_until_hhmmss": hhmmss(expected),
                  "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                  "pl_sha256": sha(BIT), "listening_3121": td.get("listening_3121"), "residual": residual})
    step("S9_release", {"status": "PASS" if td.get("listening_3121") == 0 else "FAIL",
                        "exit_code": 0 if td.get("listening_3121") == 0 else 1,
                        "hold_released_at": state["hold_released_hhmmss"],
                        "expected_until": state["expected_until_hhmmss"],
                        "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                        "listening_3121": td.get("listening_3121"), "residual": residual})

    state["criterion_ok"] = bool(ok5 and load_exit == 0 and len(values) == args.samples)
    state["conclusion"] = "P3N_HOLD_OK" if state["criterion_ok"] else "P3N_INCOMPLETE"
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())