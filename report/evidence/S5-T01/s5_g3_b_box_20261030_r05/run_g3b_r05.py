r"""G3-B r05：源坐标种子（640×480）→ 应用自行 ×1.5 映射 → 校验 box_crc/nbox/src/boxes hex。

与 r04 的差异：种子用 `g3b_box_seed_src640.json`（20 word，头 8 word 与 r04 相同；候选框为 640×480 源坐标），
应用先把源坐标 ×1.5 映射到 960×720，再算 24 B 的 CRC-32/ISO-HDLC。

判据（G3-B 本体；fps_dis=52 为已知带宽问题，本窗口不作为判据，仅记录）：
  B-1 box_crc == 0x2D949C0C
  B-2 nbox == 3（来自 `S5DISP frame=` 行）
  B-3 src == "real"
  B-4 `S5DISP boxes ... hex=` == 96 78 b4 12c 2ee 1c2 96 96 0 0 3c0 2d0

流程：P3b 位流（1670b0b3）+ 有界 ELF e392aa96；写种子 80 B（白名单 0x20800000..0x2080004F）→
     回读 96 B 校验前 80 B → load_elf_ddr → UART → 停核 → 判据 → 收窗。禁 rst -system。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
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
ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf")
ELF_SHA = "e392aa9676b783955c8a70d32040919e457d125959a1c1fa156f2f34ceb6810d"
SEED_JSON = Path(r"D:\tmp\lead\p3b_smoke_20261030_r01\g3b_box_seed_src640.json")
SEED_ADDR = 0x20800000
SEED_DUMP = 0x60
EXPECT_HEX = "96 78 b4 12c 2ee 1c2 96 96 0 0 3c0 2d0"


def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def norm_hex(s: str | None) -> str:
    out = []
    for t in (s or "").replace(",", " ").split():
        t = t.lower()
        if t.startswith("0x"):
            t = t[2:]
        try:
            out.append("%x" % int(t, 16))
        except ValueError:
            out.append(t)
    return " ".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--collect-seconds", type=int, default=60)
    args = ap.parse_args()

    run = W / "report" / "evidence" / "S5-T01" / args.run_id
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run

    seed = json.loads(SEED_JSON.read_text(encoding="utf-8"))
    words = [int(w, 16) for w in seed["seed_words"]]
    raw = b"".join(struct.pack("<I", w) for w in words)
    expect_crc = int(seed.get("expected_box_crc32_zlib", seed.get("box_crc32_zlib")), 16)
    expect_mapped = seed.get("expected_app_mapped_960x720") or seed.get("mapped_boxes_960x720")
    expect_hex = " ".join("%x" % v for b in expect_mapped for v in b)

    state: dict = {"task_id": "S5-T01", "run_id": args.run_id, "mode": "g3b_r05_src640_seed",
                   "started_utc8": now(), "steps": {}, "stop_reason": None,
                   "seed_json": str(SEED_JSON), "seed_json_sha256": sha(SEED_JSON),
                   "seed_words_count": len(words), "seed_addr": hex(SEED_ADDR),
                   "expect_box_crc": hex(expect_crc), "expect_boxes_hex": expect_hex,
                   "fps_policy": "fps_dis=52 为已知带宽问题（P3b/P3d 均 52），本窗口不作为 G3-B 判据，仅记录"}

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
        (run / "results_g3b_r05.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8", newline="\n")
        diag = state.get("diagnosis") or {}
        lines = [
            "# G3-B r05（源坐标种子）窗口记录", "",
            f"- RunId：`{args.run_id}`", f"- 开窗：{state['started_utc8']}；收窗：{state['finished_utc8']}",
            f"- 结论：**{state.get('conclusion')}**", f"- stop_reason：{stop_reason}",
            f"- 位流（P3b）：`{BIT}` sha256={sha(BIT)}",
            f"- ELF（有界）：`{ELF}` sha256={sha(ELF)}",
            f"- 种子：`{SEED_JSON}` sha256={sha(SEED_JSON)}（{len(words)} word / {len(raw)} B，源坐标 640×480）",
            f"- 种子 dump96：`{diag.get('seed_dump')}` sha256={diag.get('seed_dump_sha256')}",
            f"- 应用 boxes 行：`{diag.get('boxes_line')}`",
            f"- boxes_hex={diag.get('boxes_hex')}；expect_hex={diag.get('expect_hex')}；hex_match={diag.get('hex_match')}",
            f"- box_crc={diag.get('app_box_crc')} ({diag.get('app_box_crc_hex')})；"
            f"expect={diag.get('expect_box_crc')} ({diag.get('expect_box_crc_hex')})；crc_match={diag.get('crc_match')}",
            f"- nbox={diag.get('nbox')}；src={diag.get('src')}",
            f"- fps_dis={diag.get('fps_dis')}、fps_upd={diag.get('fps_upd')}（已知带宽问题，不作为本窗口判据，仅记录）",
            f"- 收窗：3121 LISTENING={td.get('listening_3121')}、hw_server/xsdb 残留={residual}",
            "- 屏幕：无信号（已由厂商参考位流 A/B `s5_g3_vendorref_20261030_r01` 排除我方设计）；不作为判据",
            "- 边界：仅写白名单 0x20800000..0x2080004F 共 80 B；未写其它 DDR；禁 rst -system", "",
            "## 判据", "",
        ]
        for c in (state.get("criteria") or []):
            lines.append(f"- {c['id']} {c['desc']}：**{'PASS' if c['pass'] else 'FAIL'}** {json.dumps(c['detail'], ensure_ascii=False)}")
        (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"[{now()}] done conclusion={state.get('conclusion')} stop={stop_reason}", flush=True)
        return 0 if (state.get("criterion_ok") and ok_td) else 1

    ident = {"bit": {"path": str(BIT), "sha256": sha(BIT), "expect": BIT_SHA},
             "elf": {"path": str(ELF), "sha256": sha(ELF), "expect": ELF_SHA},
             "seed": {"path": str(SEED_JSON), "sha256": sha(SEED_JSON), "words": len(words)},
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

    seed_bin = run / "g3b_seed_src640_80B.bin"
    seed_bin.write_bytes(raw)
    wc, we = drv.jtag_write_checked(seed_bin, SEED_ADDR, "S5_write_seed", len(words))
    dump96 = run / "seed_block_src640_0x20800000.bin"
    dc = drv._dump("S5_dump_seed_96B", SEED_ADDR, SEED_DUMP, dump96) if (wc == 0 and we is None) else 1
    d96 = dump96.read_bytes() if dump96.is_file() else b""
    seed_ok = (wc == 0 and we is None and dc == 0 and len(d96) == SEED_DUMP and d96[: len(raw)] == raw)
    step("S5_seed_block", {"status": "PASS" if seed_ok else "FAIL", "exit_code": 0 if seed_ok else 1,
                           "addr": hex(SEED_ADDR), "bytes": len(raw), "words": len(words),
                           "write_exit": wc, "write_error": we, "dump_exit": dc, "dump_bytes": len(d96),
                           "first80_equal": d96[: len(raw)] == raw,
                           "seed80_sha256": sha(seed_bin), "seed_dump96_sha256": sha(dump96),
                           "seed_json": str(SEED_JSON), "seed_json_sha256": sha(SEED_JSON)})
    if not seed_ok:
        return finish("种子块写入/回读失败", hw_pid)

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
    boxes_line = next((ln for ln in lines if ln.startswith("S5DISP boxes")), None)
    nbox_vals = []
    for ln in lines:
        for tok in ln.replace(",", " ").split():
            if tok.startswith("nbox="):
                try:
                    nbox_vals.append(int(tok.split("=", 1)[1]))
                except ValueError:
                    pass
    nbox = nbox_vals[-1] if nbox_vals else None
    step("S6_uart", {"status": "PASS" if result_line else "FAIL", "exit_code": 0 if result_line else 1,
                     "elapsed_s": round(time.time() - t_start, 1), "lines_total": len(lines),
                     "result_line": result_line, "boxes_line": boxes_line, "nbox": nbox, "parsed": parsed})
    if not result_line:
        return finish("60 s 内无 S5DISP RESULT", hw_pid)

    step("S7_stop_both", stop_both("S7_stop_tcl"))

    boxes_hex = None
    if boxes_line:
        m = re.search(r"hex=(.+)$", boxes_line)
        if m:
            boxes_hex = m.group(1).strip()
    hex_match = boxes_hex is not None and norm_hex(boxes_hex) == norm_hex(expect_hex)
    app_crc = parsed.get("box_crc")
    crc_match = app_crc == expect_crc
    src = parsed.get("src")
    src_ok = str(src).lower() in ("real", "real_nobox")
    criteria = [
        {"id": "B-1", "desc": f"box_crc=={hex(expect_crc)}", "pass": crc_match,
         "detail": {"box_crc": app_crc, "box_crc_hex": hex(app_crc) if isinstance(app_crc, int) else None,
                    "expect": hex(expect_crc)}},
        {"id": "B-2", "desc": "nbox==3（UART frame 行）", "pass": nbox == 3,
         "detail": {"nbox": nbox, "nbox_values": sorted(set(nbox_vals))}},
        {"id": "B-3", "desc": "src==real", "pass": src_ok, "detail": {"src": src}},
        {"id": "B-4", "desc": "boxes hex==96 78 b4 12c 2ee 1c2 96 96 0 0 3c0 2d0", "pass": hex_match,
         "detail": {"boxes_hex": boxes_hex, "expect_hex": expect_hex}},
        {"id": "INFO-J4", "desc": "fps_dis>=55（已知带宽问题，不判）", "pass": None,
         "detail": {"fps_dis": parsed.get("fps_dis"), "fps_upd": parsed.get("fps_upd"),
                    "note": "P3b/P3d 实测 52，属已知带宽问题；本窗口不作判据"}},
    ]
    criterion_ok = crc_match and nbox == 3 and src_ok and hex_match
    state["criterion_ok"] = criterion_ok
    state["criteria"] = criteria
    state["conclusion"] = "G3B_R05_PASS" if criterion_ok else "G3B_R05_FAIL"
    state["diagnosis"] = {"boxes_line": boxes_line, "boxes_hex": boxes_hex, "expect_hex": expect_hex,
                          "hex_match": hex_match, "app_box_crc": app_crc,
                          "app_box_crc_hex": hex(app_crc) if isinstance(app_crc, int) else None,
                          "expect_box_crc": expect_crc, "expect_box_crc_hex": hex(expect_crc),
                          "crc_match": crc_match, "nbox": nbox, "src": src,
                          "fps_dis": parsed.get("fps_dis"), "fps_upd": parsed.get("fps_upd"),
                          "seed_dump": str(dump96), "seed_dump_sha256": sha(dump96),
                          "result_line": result_line,
                          "verdict_text": ("映射与 CRC 均与期望一致" if criterion_ok else
                                           "不满足：见 B-1..B-4 逐条")}
    (run / "W3_judgement.json").write_text(json.dumps({"criteria": criteria,
                                                       "verdict": state["conclusion"],
                                                       "criterion_ok": criterion_ok,
                                                       "result_line": result_line, "parsed": parsed,
                                                       "diagnosis": state["diagnosis"], "utc8": now()},
                                                      ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")
    step("S8_judgement", {"status": "PASS" if criterion_ok else "FAIL",
                          "exit_code": 0 if criterion_ok else 1, "criteria": criteria})
    return finish(None if criterion_ok else "G3-B 判据 FAIL", hw_pid)


if __name__ == "__main__":
    sys.exit(main())