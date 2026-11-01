r"""P3m 第二步：真实画面窗口（PL=P3m 无 VTC/vid_out；ELF 适配版：VDMA 0x43C00000、不访问 VTC）。

流程：IDENT → 前置 → hw_server/枚举 → loadhw(P3m XSA) → 停两核 → 0xA → `xsdb fpga -file` P3m
     → P3m XSA ps7_init/post → 0xF → `load_elf_ddr`(P3m 适配 ELF) → con → UART 采集 90 s
     → 停两核 → VDMA(0x43C00000/0x04) 与 GPIO(0x43C10000) 各读 3 次（间隔 1 s）→ 收窗。
禁 rst -system；不写 DDR（除 ELF 装载）。

要抓：`S5DISP RESULT={...}`（uf_pix/fps_dis/fps_upd/vdma_err/src）与 `UF GPIO @43c10000 = N` 行。
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
BIT = Path(r"D:\tmp\lead\p3m_axis_to_video_20261030_r01\out\s4d_p3m_r01.bit")
BIT_SHA = "b7220b6dfed20264d16719f297a4c5c1440d9ae4cc9c25749339780479de017c"
XSA = Path(r"D:\tmp\lead\p3m_axis_to_video_20261030_r01\out\s4d_p3m_r01.xsa")
P3B_XSA = Path(r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.xsa")
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf")
ELF_SHA = "b0341d9f571242bc8204cb0c30c0a2279587bdc58b0ce77a20ba5f08a790a4cd"
REGS = [("VDMA_CR", 0x43C00000), ("VDMA_SR", 0x43C00004), ("UF_GPIO", 0x43C10000)]


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
            return z.read(names[0]) if names else None
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
    ap.add_argument("--collect-seconds", type=int, default=90)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3m_display",
                   "started_utc8": now(), "steps": {},
                   "programming_tool": "xsdb fpga -file",
                   "forbidden_ops": "全程禁 rst -system",
                   "elf_note": "P3m 适配版：VDMA 基址 0x43C00000、不访问 VTC、circular、帧存 0x20000000/0x20384000、uf_pix 读 GPIO 0x43C10000"}

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
        (run / "results_p3m_display.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8", newline="\n")
        snaps = (state.get("registers") or {}).get("snapshots") or []
        hold = state.get("hold") or {}
        lines = [
            "# P3m 第二步：真实画面窗口", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state.get('conclusion')}**（屏幕现象由现场判读）", f"- stop_reason：{stop_reason}",
            f"- 位流（P3m）：`{BIT}` sha256={sha(BIT)}",
            f"- ELF（P3m 适配）：`{ELF}` sha256={sha(ELF)}（{ELF.stat().st_size if ELF.is_file() else 'N/A'} B）",
            f"- ps7_init：P3m XSA 内置 sha256={state.get('ps7_p3m_sha')}"
            f"（与 P3b {'逐字节相同' if state.get('ps7_identical') else '存在差异，diff 行数=' + str(state.get('ps7_diff_lines'))}）",
            f"- 编程：xsdb `fpga -file`（fpga_exit={state.get('fpga_exit')}）、load_elf_ddr exit={state.get('load_elf_exit')}",
            f"- UART 采集：{hold.get('elapsed_s')} s、{hold.get('lines_total')} 行",
            f"- **S5DISP RESULT：`{state.get('result_line')}`**",
            f"- **`UF GPIO @43c10000` 行：`{state.get('uf_gpio_line')}`**",
            f"- 解析：{json.dumps(hold.get('fps_values') or {}, ensure_ascii=False)}",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual}", "",
            "## 停机后寄存器（VDMA/GPIO，各 3 次、间隔 1 s）", "",
        ]
        for i, s in enumerate(snaps):
            lines.append(f"- 第 {i + 1} 次：VDMA_CR={s.get('VDMA_CR')}（{hex(s.get('VDMA_CR')) if isinstance(s.get('VDMA_CR'), int) else ''}）、"
                         f"VDMA_SR={s.get('VDMA_SR')}（{hex(s.get('VDMA_SR')) if isinstance(s.get('VDMA_SR'), int) else ''}）、"
                         f"UF_GPIO={s.get('UF_GPIO')}")
        lines += ["", "## 判读方向（lead）", "",
                  "- 屏上出现测试图案 + 右侧信息栏 ⇒ 显示链路彻底打通；",
                  "- 有画面但有黑块/撕裂 ⇒ 带宽欠载（看 uf_pix 大小）；",
                  "- 仍全黑但锁上 ⇒ 数据未到（VDMA/ELF 地址问题，看 uf_pix、vdma_err）。", "",
                  "- 边界：禁 rst -system；未烧 QSPI；未改线"]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state.get('conclusion')} stop={stop_reason}", flush=True)
        return 0 if ok_td and state.get("criterion_ok") else 1

    ident = {"bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
             "xsa": {"path": str(XSA), "sha256": sha(XSA)},
             "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA}}
    id_ok = sha(BIT) == BIT_SHA and sha(ELF) == ELF_SHA
    step("S1_IDENT", {"status": "PASS" if id_ok else "FAIL", "exit_code": 0 if id_ok else 1, "checks": ident})
    if not id_ok:
        return finish("IDENT 失败（未碰板）", None)

    d_m = ps7_from_xsa(XSA)
    d_b = ps7_from_xsa(P3B_XSA)
    state["ps7_p3m_sha"] = hashlib.sha256(d_m).hexdigest() if d_m else None
    state["ps7_identical"] = bool(d_m and d_b and d_m == d_b)
    diff_n = 0
    if d_m and d_b and not state["ps7_identical"]:
        gl = [x.strip() for x in d_m.decode("utf-8", "replace").splitlines()]
        bl = [x.strip() for x in d_b.decode("utf-8", "replace").splitlines()]
        diff_n = len([l for l in difflib.unified_diff(bl, gl, lineterm="")
                      if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))])
    state["ps7_diff_lines"] = diff_n
    step("S1b_ps7_equiv", {"status": "PASS", "exit_code": 0, "p3m_ps7_sha256": state["ps7_p3m_sha"],
                           "p3b_ps7_sha256": hashlib.sha256(d_b).hexdigest() if d_b else None,
                           "identical": state["ps7_identical"], "diff_lines": diff_n})

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() != "vivado"]
    fg = free_gb()
    gate_ok = (not others) and base.listening_3121() == 0
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
                           "lvl_0xA": a.get("status"), "lvl_0xF": f.get("status"),
                           "lvl_readback_after_on": f.get("readback")})
    if not ok5:
        return finish("P3m 编程失败（停手）", hw_pid)
    drv._PL_STATE["programmed"] = True

    t0 = time.time()
    load_exit = drv.load_elf_ddr(ELF, "S6_load_elf", hold_reset=True)
    state["load_elf_exit"] = load_exit
    step("S6_load_elf", {"status": "PASS" if load_exit == 0 else "FAIL",
                         "exit_code": 0 if load_exit == 0 else 1,
                         "load_elf_ddr_exit": load_exit, "elapsed_s": round(time.time() - t0, 1),
                         "elf": str(ELF), "elf_sha256": sha(ELF)})
    if load_exit != 0:
        return finish("ELF 装载失败", hw_pid)

    ser = drv._SER.get("ser")
    lines: list[str] = []
    buf = ""
    t_start = time.time()
    result_line = None
    uf_gpio_line = None
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
                if "UF GPIO" in s:
                    uf_gpio_line = s
    (run / "S7_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    parsed: dict = {}
    if result_line:
        try:
            parsed = json.loads(result_line.split("=", 1)[1])
        except Exception as exc:  # noqa: BLE001
            parsed = {"parse_error": str(exc)}
    fps_seen: dict = {}
    for ln in lines:
        for tok in ln.replace(",", " ").split():
            for k in ("fps_dis", "fps_upd", "vdma_err", "uf_pix", "frames", "vcnt", "src"):
                if tok.startswith(k + "="):
                    v = tok.split("=", 1)[1]
                    try:
                        fps_seen.setdefault(k, []).append(int(v))
                    except ValueError:
                        fps_seen.setdefault(k, []).append(v)
    hold = {"elapsed_s": round(time.time() - t_start, 1), "lines_total": len(lines),
            "result_seen": bool(result_line), "uf_gpio_line": uf_gpio_line,
            "fps_values": {k: sorted(set(v), key=str) if all(isinstance(x, int) for x in v) else v
                           for k, v in fps_seen.items()},
            "first_lines": lines[:8], "last_lines": lines[-8:], "tail_partial": buf}
    state.update({"hold": hold, "result_line": result_line, "uf_gpio_line": uf_gpio_line,
                  "parsed": parsed})
    step("S7_uart", {"status": "PASS" if result_line else "FAIL", "exit_code": 0 if result_line else 1,
                     **hold, "parsed": parsed})
    if not result_line:
        return finish("90 s 内无 S5DISP RESULT（旧/新 ELF 地址不匹配或总线挂）", hw_pid)

    tcl = ["connect -url %s; " % base.HW_URL,
           'targets -set -filter {name =~ "*Cortex-A9*#0*"}; ',
           "if {[catch {loadhw -hw %s -mem-ranges {0x00000000 0x7FFFFFFF}} e]} "
           "{ puts \"LOADHW_SKIP: $e\" } else { puts LOADHW_OK }; " % XSA.as_posix(),
           "rst -processor -stop; ",
           'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; puts CORES_STOPPED; ',
           "for {set i 0} {$i < 3} {incr i} { "
           "puts \"SNAP$i VDMA_CR=[mrd -value 0x43C00000] VDMA_SR=[mrd -value 0x43C00004] "
           "UF_GPIO=[mrd -value 0x43C10000]\"; if {$i < 2} { after 1000 } }; ",
           "disconnect; exit"]
    c8, e8 = drv.xsdb_checked("".join(tcl), "S8_reg_snapshot", timeout=600)
    t8 = (run / "S8_reg_snapshot.log").read_text(encoding="utf-8", errors="replace") if (run / "S8_reg_snapshot.log").is_file() else ""
    b8 = t8.split("exit=", 1)[-1] if "exit=" in t8 else t8
    snaps = []
    for m in re.finditer(r"SNAP(\d).*?VDMA_CR[=\s]+(\S+).*?VDMA_SR[=\s]+(\S+).*?UF_GPIO[=\s]+(\S+)", b8):
        def dec(x):
            try:
                return int(x, 16) if x.lower().startswith("0x") else int(x, 10)
            except Exception:
                return x
        snaps.append({"VDMA_CR": dec(m.group(2)), "VDMA_SR": dec(m.group(3)), "UF_GPIO": dec(m.group(4))})
    state["registers"] = {"snapshots": snaps, "error_text": e8}
    step("S8_reg_snapshot", {"status": "PASS" if (c8 == 0 and len(snaps) == 3) else "FAIL",
                             "exit_code": 0 if (c8 == 0 and len(snaps) == 3) else 1,
                             "xsdb_exit": c8, "error_text": e8, "snapshots": snaps})

    state["criterion_ok"] = bool(ok5 and load_exit == 0 and result_line and c8 == 0 and len(snaps) == 3)
    state["conclusion"] = "P3M_DISPLAY_WINDOW_OK" if state["criterion_ok"] else "P3M_DISPLAY_INCOMPLETE"
    step("S9_judgement", {"status": "PASS" if state["criterion_ok"] else "FAIL",
                          "exit_code": 0 if state["criterion_ok"] else 1,
                          "note": "只判执行完整性；屏幕图案由现场判读", "conclusion": state["conclusion"]})
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())