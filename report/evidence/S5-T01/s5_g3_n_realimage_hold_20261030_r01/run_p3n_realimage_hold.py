r"""P3n 真实图像挂屏：先把 640×480 BGR888 fixture 写入 raw 区 0x12000000（921,600 B，分段 64 KiB），
校验前/末 96 B，再跑 P3n 长跑 ELF 渲染 ⇒ 停 CPU 保留 VDMA ⇒ 画面永久保持（左侧真实手部图像 + 3 框 + 右侧面板）。

流程：IDENT → 前置 → hw_server/枚举 → loadhw(P3n XSA) → 停两核 → 0xA → `xsdb fpga -file` P3n → 0xF
     → 跑 init.elf 的 ps7_init（初始化 DDR）→ 分段把 fixture 写到 0x12000000 → 回读前 96 B / 末 96 B 校验
     → `load_elf_ddr`(P3n 长跑 ELF) → con → 等 15 s（渲染几帧；抓 src/nbox）→ `rst -processor -stop` 仅两核
     → 只读 CR/SR/GPIO → 杀 hw_server（不收窗、VDMA 继续读）。
禁 rst -system；禁读 0x43C30000。
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
ELF_SHA = "388a0a07101a16e3b3fb43a51b6b987f63bff9200821c3f9ddca1e896fe0752a"
FIXTURE = Path(r"D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_chainlite_b_20261028_r01\fixture"
               r"\fixture_fist_000_640x480_bgr888.raw")
FIXTURE_SHA = "ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4"
RAW_ADDR = 0x12000000
RAW_BYTES = 640 * 480 * 3
CHUNK = 64 * 1024


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def hhmmss() -> str:
    return datetime.now(UTC8).strftime("%H:%M:%S")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


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
    ap.add_argument("--warmup-seconds", type=float, default=15.0)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3n_realimage_hold",
                   "started_utc8": now(), "steps": {},
                   "purpose": "raw 区 0x12000000 灌真实 fixture ⇒ 左侧出真实手部图像；停 CPU 保留 VDMA ⇒ 永久挂屏",
                   "forbidden_ops": "禁 rst -system；禁读 0x43C30000"}

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
        step("S10_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1,
                              "detail": td, "hw_server_xsdb_residual": residual,
                              "note": "仅杀 hw_server；CPU 已停、PL 与 VDMA 保持"})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        (run / "results_realimage_hold.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                       encoding="utf-8", newline="\n")
        r = state.get("readonly") or {}
        wr = state.get("raw_write") or {}
        lines = [
            "# P3n 真实图像挂屏（raw 区灌 fixture）", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- **STATIC_HOLD_AT={state.get('static_hold_hhmmss')}**", f"- **cores=STOPPED**（仅 CPU）",
            f"- **PL=P3n sha256={sha(BIT)}**", f"- **ELF sha256={sha(ELF)}**（{ELF.stat().st_size if ELF.is_file() else 'N/A'} B）",
            f"- fixture：`{FIXTURE}` sha256={sha(FIXTURE)}（{FIXTURE.stat().st_size if FIXTURE.is_file() else 'N/A'} B）",
            f"- raw 写入：addr={hex(RAW_ADDR)}、bytes={wr.get('bytes_written')}、chunks={wr.get('chunks')}、"
            f"write_elapsed_s={wr.get('elapsed_s')}",
            f"- **raw 回读校验**：前 96 B equal={wr.get('head96_equal')}、末 96 B equal={wr.get('tail96_equal')}、"
            f"head96_sha256={wr.get('head96_sha')}、tail96_sha256={wr.get('tail96_sha')}",
            f"- VDMA_CR={r.get('VDMA_CR')}（{hex(r['VDMA_CR']) if isinstance(r.get('VDMA_CR'), int) else ''}）、"
            f"VDMA_SR={r.get('VDMA_SR')}（{hex(r['VDMA_SR']) if isinstance(r.get('VDMA_SR'), int) else ''}）、"
            f"UF_GPIO={r.get('UF_GPIO')}",
            f"- 停核后 VDMA 运行：CR.RS={((r.get('VDMA_CR') or 0) & 1)}、SR.Halted={((r.get('VDMA_SR') or 0) & 1)}"
            f" ⇒ {'仍在读帧存 ✅' if ((r.get('VDMA_CR') or 0) & 1) and not ((r.get('VDMA_SR') or 0) & 1) else '已停 ⚠'}",
            f"- UART：src={ (state.get('parsed') or {}).get('src') }、nbox={state.get('nbox')}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual}", "",
            "## 预热期 UART 关键行", "", "```",
            "\n".join((state.get("warmup_uart") or {}).get("key_lines") or []), "```", "",
            "- 边界：禁 rst -system；禁读 0x43C30000；未烧 QSPI；未改线",
        ]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] STATIC_HOLD_AT={state.get('static_hold_hhmmss')} cores=STOPPED CR={r.get('VDMA_CR')} "
              f"SR={r.get('VDMA_SR')} head96={wr.get('head96_equal')} tail96={wr.get('tail96_equal')}", flush=True)
        return 0 if ok_td and state.get("criterion_ok") else 1

    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA and sha(FIXTURE) == FIXTURE_SHA
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1,
                      "bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
                      "xsa": {"path": str(XSA), "sha256": sha(XSA)},
                      "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA},
                      "fixture": {"path": str(FIXTURE), "sha256": sha(FIXTURE), "expect": FIXTURE_SHA,
                                  "size": FIXTURE.stat().st_size if FIXTURE.is_file() else None}})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() != "vivado"]
    fg = free_gb()
    gate_ok = (not others) and base.listening_3121() == 0 and (fg is None or fg >= 3.0)
    step("S2_preflight", {"status": "PASS" if gate_ok else "FAIL", "exit_code": 0 if gate_ok else 1,
                          "heavy_processes": heavy, "non_vivado_heavy": others, "free_gb": fg,
                          "listening_3121": base.listening_3121()})
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

    a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "S5_lvl_0xA")
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
    state["fpga_exit"] = 0 if (c5 == 0 and fpga_done) else (c5 if c5 else 0)
    step("S5_program_pl", {"status": "PASS" if ok5 else "FAIL", "exit_code": 0 if ok5 else 1,
                           "programming_tool": "xsdb fpga -file", "fpga_exit": state["fpga_exit"],
                           "fpga_done": fpga_done, "lvl_0xF": f.get("status"),
                           "lvl_readback_after_on": f.get("readback")})
    if not ok5:
        return finish("P3n 编程失败（停手）", hw_pid)
    drv._PL_STATE["programmed"] = True

    # 先跑 init.elf 的 ps7_init 初始化 DDR（之后才能安全写 raw 区）
    tcl = ("connect -url %s; %s" % (base.HW_URL, base.select_core())
           + "rst -processor -stop; dow %s; con; after 2500; rst -processor -stop; puts INIT_DONE; disconnect; exit"
           % drv.INIT_ELF.as_posix())
    c_init, e_init = drv.xsdb_checked(tcl, "S5b_init_ddr", timeout=600)
    t_init = (run / "S5b_init_ddr.log").read_text(encoding="utf-8", errors="replace") if (run / "S5b_init_ddr.log").is_file() else ""
    init_done = "INIT_DONE" in (t_init.split("exit=", 1)[-1] if "exit=" in t_init else t_init)
    step("S5b_init_ddr", {"status": "PASS" if (c_init == 0 and e_init is None and init_done) else "FAIL",
                          "exit_code": 0 if (c_init == 0 and e_init is None and init_done) else 1,
                          "init_done": init_done, "error_text": e_init})
    if c_init != 0 or not init_done:
        return finish("DDR 初始化（init.elf ps7_init）失败", hw_pid)

    # 分段写 fixture 到 0x12000000（64 KiB/段）
    data = FIXTURE.read_bytes()
    chunks = []
    t_w = time.time()
    ok_w = True
    for i, off in enumerate(range(0, len(data), CHUNK)):
        seg = data[off:off + CHUNK]
        p = run / f"raw_chunk_{i:02d}.bin"
        p.write_bytes(seg)
        words = len(seg) // 4
        c, e = drv.jtag_write_checked(p, RAW_ADDR + off, f"S6_write_chunk{i:02d}", words)
        chunks.append({"i": i, "addr": hex(RAW_ADDR + off), "bytes": len(seg), "exit": c, "error": e})
        if c != 0 or e is not None:
            ok_w = False
            break
    write_elapsed = round(time.time() - t_w, 1)
    # 回读前/末 96 B 校验
    head_p = run / "raw_head96.bin"
    tail_p = run / "raw_tail96.bin"
    ch = drv._dump("S6_read_head96", RAW_ADDR, 96, head_p) if ok_w else 1
    ct = drv._dump("S6_read_tail96", RAW_ADDR + RAW_BYTES - 96, 96, tail_p) if ok_w else 1
    head_ok = head_p.is_file() and head_p.read_bytes() == data[:96]
    tail_ok = tail_p.is_file() and tail_p.read_bytes() == data[-96:]
    raw_write = {"addr": hex(RAW_ADDR), "bytes_written": len(data), "chunks": len(chunks),
                 "elapsed_s": write_elapsed, "ok": ok_w, "head96_exit": ch, "tail96_exit": ct,
                 "head96_equal": head_ok, "tail96_equal": tail_ok,
                 "head96_sha": sha(head_p), "tail96_sha": sha(tail_p),
                 "expect_head96_sha": hashlib.sha256(data[:96]).hexdigest(),
                 "expect_tail96_sha": hashlib.sha256(data[-96:]).hexdigest(),
                 "chunk_detail": chunks}
    state["raw_write"] = raw_write
    step("S6_raw_write", {"status": "PASS" if (ok_w and head_ok and tail_ok) else "FAIL",
                          "exit_code": 0 if (ok_w and head_ok and tail_ok) else 1,
                          "addr": hex(RAW_ADDR), "bytes": len(data), "chunks": len(chunks),
                          "elapsed_s": write_elapsed, "head96_equal": head_ok, "tail96_equal": tail_ok,
                          "head96_sha": raw_write["head96_sha"], "tail96_sha": raw_write["tail96_sha"],
                          "chunk_exits": [c["exit"] for c in chunks]})
    if not (ok_w and head_ok and tail_ok):
        return finish("raw fixture 写入/回读校验失败", hw_pid)

    # 装载长跑 ELF（内部会再跑 init.elf 的 ps7_init → dow → 0xF → con）
    t0 = time.time()
    load_exit = drv.load_elf_ddr(ELF, "S7_load_longrun", hold_reset=True)
    logp = run / "S7_load_longrun.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    run_state = "Running" if "RUN_STATE Running" in txt else None
    state["load_elf_exit"] = load_exit
    step("S7_load_longrun", {"status": "PASS" if (load_exit == 0 and run_state) else "FAIL",
                             "exit_code": 0 if (load_exit == 0 and run_state) else 1,
                             "load_elf_ddr_exit": load_exit, "run_state": run_state,
                             "elapsed_s": round(time.time() - t0, 1)})
    if load_exit != 0 or not run_state:
        return finish("长跑 ELF 未进入 Running", hw_pid)

    # 预热 15 s：渲染真实图像；抓 src/nbox
    ser = drv._SER.get("ser")
    lines: list[str] = []
    buf = ""
    t_start = time.time()
    while time.time() - t_start < args.warmup_seconds:
        chunk = ser.read(4096)
        if not chunk:
            continue
        buf += chunk.decode("utf-8", "replace")
        while "\n" in buf:
            raw_ln, buf = buf.split("\n", 1)
            s = raw_ln.strip()
            if s:
                lines.append(s)
    (run / "S7_warmup_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    parsed = {}
    result_line = next((ln for ln in lines if ln.startswith("S5DISP RESULT=")), None)
    if result_line:
        try:
            parsed = json.loads(result_line.split("=", 1)[1])
        except Exception:
            parsed = {}
    nbox_vals = []
    for ln in lines:
        for tok in ln.replace(",", " ").split():
            if tok.startswith("nbox="):
                try:
                    nbox_vals.append(int(tok.split("=", 1)[1]))
                except ValueError:
                    pass
    state["parsed"] = parsed
    state["nbox"] = nbox_vals[-1] if nbox_vals else None
    key = [ln for ln in lines if ("TEST PATTERN" in ln or "src=" in ln or "fps_dis" in ln
                                  or "UF GPIO" in ln or "hw:" in ln)]
    state["warmup_uart"] = {"lines": len(lines), "key_lines": key[:15], "last_lines": lines[-8:]}
    step("S8_warmup_uart", {"status": "PASS" if lines else "FAIL", "exit_code": 0 if lines else 1,
                            "lines": len(lines), "src": parsed.get("src"), "nbox": state["nbox"],
                            "key_lines": key[:15], "last_lines": lines[-8:]})

    # 只停 CPU 两核（保留 PL/VDMA）
    tcl = ("connect -url %s; " % base.HW_URL
           + 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; rst -processor -stop; '
           + 'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; '
           + "puts CPU_STOPPED; disconnect; exit")
    c9, e9 = drv.xsdb_checked(tcl, "S9_stop_cpu", timeout=300)
    t9 = (run / "S9_stop_cpu.log").read_text(encoding="utf-8", errors="replace") if (run / "S9_stop_cpu.log").is_file() else ""
    cpu_stopped = "CPU_STOPPED" in (t9.split("exit=", 1)[-1] if "exit=" in t9 else t9)
    state["static_hold_hhmmss"] = hhmmss()
    step("S9_stop_cpu", {"status": "PASS" if (c9 == 0 and cpu_stopped) else "FAIL",
                         "exit_code": 0 if (c9 == 0 and cpu_stopped) else 1,
                         "cpu_stopped": cpu_stopped, "static_hold_at": state["static_hold_hhmmss"]})

    # 只读确认
    tcl = ["connect -url %s; " % base.HW_URL,
           'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw %s -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "puts \"UF_GPIO [mrd -value 0x43C10000]\"; ",
           "puts \"VDMA_CR [mrd -value 0x43C00000]\"; ",
           "puts \"VDMA_SR [mrd -value 0x43C00004]\"; ",
           "disconnect; exit"]
    c10, e10 = drv.xsdb_checked("".join(tcl), "S9b_readonly_confirm", timeout=300)
    txt = (run / "S9b_readonly_confirm.log").read_text(encoding="utf-8", errors="replace") if (run / "S9b_readonly_confirm.log").is_file() else ""
    b10 = txt.split("exit=", 1)[-1] if "exit=" in txt else txt
    ro = {}
    for m in re.finditer(r"(UF_GPIO|VDMA_CR|VDMA_SR)\s+(\d+)", b10):
        ro[m.group(1)] = int(m.group(2))
    state["readonly"] = ro
    vdma_running = bool((ro.get("VDMA_CR") or 0) & 1) and not ((ro.get("VDMA_SR") or 0) & 1)
    step("S9b_readonly_confirm", {"status": "PASS" if len(ro) == 3 else "FAIL",
                                  "exit_code": 0 if len(ro) == 3 else 1, "values": ro,
                                  "vdma_still_running": vdma_running, "error_text": e10})

    state["criterion_ok"] = bool(ok5 and ok_w and head_ok and tail_ok and load_exit == 0
                                 and cpu_stopped and len(ro) == 3 and vdma_running)
    state["conclusion"] = "P3N_REALIMAGE_HOLD_OK" if state["criterion_ok"] else "P3N_REALIMAGE_CHECK"
    step("S9c_judgement", {"status": "PASS" if state["criterion_ok"] else "FAIL",
                           "exit_code": 0 if state["criterion_ok"] else 1,
                           "note": "画面由现场判读；此处确认 raw 写入校验 + 停核后 VDMA 仍在读",
                           "src": parsed.get("src"), "nbox": state["nbox"],
                           "vdma_cr": ro.get("VDMA_CR"), "vdma_sr": ro.get("VDMA_SR"),
                           "conclusion": state["conclusion"]})
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())