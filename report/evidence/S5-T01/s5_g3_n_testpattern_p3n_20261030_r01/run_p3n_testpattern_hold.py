r"""P3n + 新测试图长跑 ELF（A/B 帧存同图）hold 窗口：验证花屏根因（A/B 内容不同）+ 挂 30 min 给现场看。

流程：IDENT → hw_server/枚举 → loadhw(P3n XSA) → 停两核 → 0xA → `xsdb fpga -file` P3n → 0xF
     → `load_elf_ddr`(新长跑 ELF) → con → 采 UART 30 s
     → 杀 hw_server、**不停核、不收窗**（长跑上限 1800 s，画面持续）。
要抓：`TEST PATTERN DRAWN: bars8+border+cross`、`TEST PATTERN HOLD: 2000 ms`、`… done, vdma_err=N`、`fps_dis`、`UF GPIO`。
禁 rst -system。
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
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app_longrun.elf")
ELF_SHA = "34093912f22961f5191fae17687167f9b9d712e3f88ec1033d4f0f666ad7ed50"
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
    ap.add_argument("--collect-seconds", type=float, default=30.0)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "p3n_testpattern_hold",
                   "started_utc8": now(), "steps": {},
                   "purpose": "验证花屏根因（A/B 帧存内容不同）；两帧存同图后应稳定显示 8 竖彩条+白框+中央十字",
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
        step("S8_teardown", {"status": "PASS" if ok_td else "FAIL", "exit_code": 0 if ok_td else 1,
                             "detail": td, "hw_server_xsdb_residual": residual,
                             "note": "仅杀 hw_server；不停核、不收窗"})
        state["finished_utc8"] = now()
        state["stop_reason"] = stop_reason
        (run / "results_testpattern.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                    encoding="utf-8", newline="\n")
        u = state.get("uart") or {}
        lines = [
            "# P3n + 新测试图长跑 hold 窗口", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；释放：{state.get('hold_released_hhmmss')}",
            f"- **HOLD_RELEASED_AT={state.get('hold_released_hhmmss')}**",
            f"- **EXPECTED_UNTIL={state.get('expected_until_hhmmss')}**（长跑上限 {TIME_CAP_S} s，按 con 折算）",
            f"- **PL=P3n sha256={sha(BIT)}**",
            f"- **ELF=新长跑 sha256={sha(ELF)}**（{ELF.stat().st_size if ELF.is_file() else 'N/A'} B）",
            f"- 编程 fpga_exit={state.get('fpga_exit')}；load_elf_ddr exit={state.get('load_elf_exit')}；cores=RUNNING；hw_server=killed",
            f"- UART 行数={u.get('lines')}（采 {args.collect_seconds} s）", "",
            "## UART 关键行", "", "```", "\n".join(u.get("key_lines") or []), "```", "",
            "- 判读：稳定显示 8 竖彩条+白框+中央十字、不再闪 ⇒ 花屏根因=A/B 帧存内容不同（软件），P3n 可作干净基线；",
            "  仍闪 ⇒ 需 P3p（fsync）。",
            "- 边界：禁 rst -system；未烧 QSPI；未改线",
        ]
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] HOLD_RELEASED_AT={state.get('hold_released_hhmmss')} "
              f"EXPECTED_UNTIL={state.get('expected_until_hhmmss')}", flush=True)
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
    (run / "S6_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    key = [ln for ln in lines if ("TEST PATTERN" in ln or "UF GPIO" in ln or "fps_dis" in ln
                                  or "vdma_err" in ln or "done" in ln or "hw:" in ln)]
    state["uart"] = {"lines": len(lines), "key_lines": key[:25], "last_lines": lines[-8:],
                     "elapsed_s": round(time.time() - t_start, 1)}
    step("S7_uart", {"status": "PASS" if lines else "FAIL", "exit_code": 0 if lines else 1,
                     **state["uart"]})

    released = datetime.now(UTC8)
    td = base.stop_hw_server(hw_pid)
    residual = [n for n in base.heavy_processes() if n.lower() in ("hw_server", "xsdb")]
    expected = released + timedelta(seconds=TIME_CAP_S - (args.collect_seconds + 10))
    state.update({"hold_released_at": released.isoformat(timespec="seconds"),
                  "hold_released_hhmmss": hhmmss(released),
                  "expected_until_hhmmss": hhmmss(expected),
                  "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                  "pl_sha256": sha(BIT), "elf_sha256": sha(ELF),
                  "listening_3121": td.get("listening_3121"), "residual": residual})
    step("S8_release", {"status": "PASS" if td.get("listening_3121") == 0 else "FAIL",
                        "exit_code": 0 if td.get("listening_3121") == 0 else 1,
                        "hold_released_at": state["hold_released_hhmmss"],
                        "expected_until": state["expected_until_hhmmss"],
                        "cores": "RUNNING", "hw_server": "killed", "pl": "P3n",
                        "listening_3121": td.get("listening_3121"), "residual": residual})
    state["criterion_ok"] = bool(ok5 and load_exit == 0 and lines)
    state["conclusion"] = "P3N_TESTPATTERN_HOLD_OK" if state["criterion_ok"] else "P3N_TESTPATTERN_INCOMPLETE"
    return finish(None, hw_pid)


if __name__ == "__main__":
    sys.exit(main())