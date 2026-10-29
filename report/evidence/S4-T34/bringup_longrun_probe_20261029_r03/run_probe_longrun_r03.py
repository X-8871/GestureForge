r"""长跑停住定位 r03（2026-10-29）：修正 r02 的执行顺序缺陷后重跑。

r02 失效根因（见 r02/ERRATA_INVALID_RUN.md）：复用 load_elf_ddr 时未置位 _PL_STATE，
它走了 `rst -system -stop`，把刚编程的 PL 配置清掉 → 应用首次 CSR 读挂死 → DAP 粘连。

r03 顺序（与 2026-10-29 14:38 已成功的探针窗口一致，不再依赖 _PL_STATE）：
  W0  rst -system -stop → dow init.elf → con 2s → rst -processor -stop（DDR 就绪、PL 未配置）
  W1  0xA → 编程 PL（2B 位流）→ 0xF 读回断言
  W2  preload RAW(0x12000000) + 权重(0x10100000) → dow 探针 ELF（**只 rst -processor**）
      → 0xF 读回断言 → con → 采集（CRC 门禁 0x5B183B50）
  W3  停住则保全：先确认 state 可读（不可读 ⇒ DAP_WEDGED 立即停），再读两核 PC/CPSR、
      记录区 8 字、CSR 三读（-mem-ranges 修正）+ DevCfg(0xF8007000)
  W4  候选区恢复 + 记录区清零（DAP 不可用则如实 NOT_DONE，不伪称已恢复）
不写 QSPI、不改线、ENABLE=0、禁 -force；不主张 G3/G4/G5。
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

W = Path(r"D:\codex-worktrees\w4")
TMP = W / "tmp" / "4" / "S4-T34"
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))
sys.path.insert(0, str(TMP))

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "bringup_longrun_probe_20261029_r03"
RUN = W / "report" / "evidence" / "S4-T34" / RUN_ID

import run_diag_longrun_v2 as dg  # noqa: E402
import run_window_b_driver as base  # noqa: E402
import run_bringup_driver as drv  # noqa: E402

UTC8 = timezone(timedelta(hours=8))
PROBE = W / "report/evidence/S4-T34/longrun_probe_step_prints_20261029_r01/s4d_ps_app_sw0_longrunP.elf"
PROBE_SHA = "f9095655bde0624d9844c4c60894b8366d6a874e900cbe7b6b220380c46c33dc"
FIXTURE = W / "report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/fixture/fixture_fist_000_640x480_bgr888.raw"
FIXTURE_SHA = "ce37aa772aec9d45084edc37f3a1e0fe1b258385ec57b1fd994d98614792dad4"
WEIGHTS = Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8")
WEIGHTS_PREFIX = "f6feb6d4"
M3REF = W / "report/evidence/S4-T32/window_a_20261027_r01/m3_snapshot_orig.bin"
M3REF_SHA = "41907f53"
BIT = Path(r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit")
BIT_PREFIX = "555a70c2"
XSA = Path(r"D:\FPGA_Competition\w2b\report\evidence\S2B-T14\csr_fixed_visibility0_20261016_r08\s2b_inference.xsa")
OFFLINE_TENSOR_CRC = 0x5B183B50
COLLECT_MAX_S = 1950
STALL_QUIET_S = 60
EARLY_STALL_S = 150

dg.RUN_ID = RUN_ID
dg.RUN = RUN
dg.LR_ELF = PROBE
dg.LR_ELF_SHA = PROBE_SHA
dg.COLLECT_MAX_S = COLLECT_MAX_S
dg.STALL_QUIET_S = STALL_QUIET_S
dg.EARLY_STALL_S = EARLY_STALL_S
dg.M3REF = M3REF
RUN.mkdir(parents=True, exist_ok=True)
base.RUN_DIR = RUN
drv.RUN_DIR = RUN
base.uart_open = drv.uart_open_preopened

T0 = datetime.now(UTC8)
dg.STATE = {
    "task_id": "S4-T34", "run_id": RUN_ID,
    "phase": "长跑停住定位 r03（顺序修正：编程 PL 后不再系统复位）",
    "driver_sha256": dg.DRIVER_SHA, "probe_elf_sha256": PROBE_SHA,
    "fixture_sha256": FIXTURE_SHA, "weights_sha256_prefix": WEIGHTS_PREFIX,
    "offline_tensor_crc32": f"0x{OFFLINE_TENSOR_CRC:08x}",
    "collect_max_s": COLLECT_MAX_S, "stall_quiet_s": STALL_QUIET_S,
    "started_utc8": T0.isoformat(timespec="seconds"), "steps": {}, "stop_reason": None,
    "judgement": "停住 = 末行打印定位步骤 + 记录区 step/iter + 停核可读；未复现 ⇒ 30 min RESULT 后如实记",
    "boundary": "2B 平台位流 + SW 预处理 + fixture 非实拍；ENABLE=0；不烧 QSPI；不改线；不 push；不主张 G3/G4/G5",
    "r02_correction": "r02 因 load_elf_ddr 走 rst -system -stop 清 PL 而自伤；r03 改为只 rst -processor 装探针 ELF",
}
STATE = dg.STATE
step = dg.step
now = dg.now


def sha(p: Path):
    if not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def load_probe_app() -> dict:
    """只停核 → dow 探针 ELF → 四动作(0xF 读回) → con。**不做系统复位**，不清 PL。"""
    cmds = (
        "connect -url %s; %s" % (base.HW_URL, base.select_core())
        + "rst -processor -stop; puts LOAD_HOLD_BEGIN; state; puts LOAD_HOLD_END; "
        + "dow %s; " % PROBE.as_posix()
        + drv.lvl_shifter_inline_assert(drv.LVL_SHFTR_ON)
        + 'after 200; puts "HOLD_STATE=[state]"; con; after 2000; puts "RUN_STATE=[state]"; disconnect; exit'
    )
    code, err = drv.xsdb_checked(cmds, "W2_load")
    log = (RUN / "W2_load.log").read_text(encoding="utf-8", errors="replace") if (RUN / "W2_load.log").is_file() else ""
    hold = "LOAD_HOLD_BEGIN" in log and "LOAD_HOLD_END" in log
    running = "RUN_STATE Running" in log
    ok = code == 0 and err is None and hold and running
    return {"status": "PASS" if ok else "FAIL", "exit_code": 0 if ok else 1,
            "xsdb_exit": code, "xsdb_error_text": err, "hold_readable": hold,
            "run_state_running": running,
            "note": "关键：首条为 rst -processor -stop（不出现 rst -system）"}


def parse_result(line: str) -> dict:
    try:
        return json.loads(line.split("=", 1)[1])
    except Exception:  # noqa: BLE001
        return {}


def collect(log_path: Path) -> tuple[list[str], str, dict]:
    ser, err = base.uart_open()
    if ser is None:
        log_path.write_text(f"[uart_unavailable] {err}\n", encoding="utf-8")
        return [], "NOUART", {"uart": err}
    lines: list[str] = []
    buf = b""
    t_begin = time.time()
    last_line_t = t_begin
    end = t_begin + COLLECT_MAX_S
    why = "MAXTIME"
    crc = None
    hb_count = 0
    while time.time() < end:
        try:
            chunk = ser.read(512)
        except Exception:  # noqa: BLE001
            chunk = b""
        if chunk:
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                txt = raw.decode("utf-8", errors="replace").strip()
                if not txt:
                    continue
                lines.append(txt)
                last_line_t = time.time()
                print("U:", txt, flush=True)
                if txt.startswith("LONGRUN STEP=1 "):
                    for tok in txt.split():
                        if tok.startswith("tensor_crc32=0x"):
                            try:
                                crc = int(tok.split("=", 1)[1], 16)
                            except ValueError:
                                crc = None
                    if crc is not None and crc != OFFLINE_TENSOR_CRC:
                        why = "PRELOAD_CRC_MISMATCH"
                elif txt.startswith("LONGRUN STEP iter="):
                    hb_count += 1
                elif txt.startswith("LONGRUN RESULT="):
                    why = "RESULT"
                elif txt.startswith("LONGRUN FAIL "):
                    why = "FAIL"
        if why in ("RESULT", "FAIL", "PRELOAD_CRC_MISMATCH"):
            break
        if hb_count > 0 and (time.time() - last_line_t) > STALL_QUIET_S:
            why = "STALL"
            break
        if hb_count == 0 and lines and (time.time() - t_begin) > EARLY_STALL_S:
            why = "STALL_EARLY"
            break
    try:
        ser.close()
    except Exception:  # noqa: BLE001
        pass
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    meta = {"elapsed_s": round(time.time() - t_begin, 1), "lines": len(lines),
            "silence_s": round(time.time() - last_line_t, 1), "heartbeats": hb_count,
            "tensor_crc32": (hex(crc) if crc is not None else None)}
    print(f"[collect] why={why} {meta}", flush=True)
    return lines, why, meta


def longrun_step() -> dict:
    raw = FIXTURE.read_bytes()
    words = (len(raw) + 3) // 4
    pf = RUN / "W2_pre_fixture_padded.bin"
    pf.write_bytes(raw + (b"\x00" * (words * 4 - len(raw)) if len(raw) % 4 else b""))
    c_raw, e_raw = drv.jtag_write_checked(pf, 0x12000000, "W2_pre_raw", words)
    c_w, e_w = drv.jtag_write_checked(WEIGHTS, 0x10100000, "W2_pre_weights", WEIGHTS.stat().st_size // 4)
    pre_ok = c_raw == 0 and e_raw is None and c_w == 0 and e_w is None
    step("W2_preload", {"status": "PASS" if pre_ok else "FAIL", "exit_code": 0 if pre_ok else 1,
                        "raw_write_exit": c_raw, "raw_err": e_raw,
                        "weights_write_exit": c_w, "weights_err": e_w,
                        "raw_words": words, "weights_words": WEIGHTS.stat().st_size // 4})
    if not pre_ok:
        return {"status": "FAIL", "exit_code": 1, "reason": "preload 写入失败"}
    ld = load_probe_app()
    step("W2_load_probe", ld)
    if ld["status"] != "PASS":
        return {"status": "FAIL", "exit_code": 1, "reason": "探针 ELF 装载/启动失败", "load": ld}
    lines, why, meta = collect(RUN / "W2_uart.log")
    result_line = next((ln for ln in lines if ln.startswith("LONGRUN RESULT=")), None)
    fail_line = next((ln for ln in lines if ln.startswith("LONGRUN FAIL ")), None)
    parsed = parse_result(result_line) if result_line else {}
    if why == "RESULT":
        ok = parsed.get("exit") == 0 and parsed.get("within_judgement") == 1
        status, code = ("PASS" if ok else "FAIL"), (0 if ok else 1)
    elif why in ("PRELOAD_CRC_MISMATCH", "NOUART", "FAIL"):
        status, code = "FAIL", 1
    elif why in ("STALL", "STALL_EARLY"):
        status, code = "STALL", 1
    else:
        status, code = "MAXTIME", 1
    return {"status": status, "exit_code": code, "collect": why, "collect_meta": meta,
            "result_line": result_line, "fail_line": fail_line, "parsed": parsed,
            "last_line": (lines[-1] if lines else None), "lines_total": len(lines),
            "uart_log": str(RUN / "W2_uart.log")}


def _seg(text: str, begin: str, end: str) -> str:
    idx = text.find("\nexit=")
    tail = text[idx + 1:] if idx >= 0 else text
    nl = tail.find("\n")
    tail = tail[nl + 1:] if nl >= 0 else tail
    if begin in tail and end in tail:
        return tail.split(begin, 1)[1].split(end, 1)[0]
    return ""


def _val_for(seg: str, addr: int):
    want = f"{addr:08x}".lower()
    for ln in seg.splitlines():
        low = ln.strip().lower()
        if want in low and ":" in low:
            tok = low.split(":", 1)[1].strip().split()[0] if low.split(":", 1)[1].strip() else ""
            try:
                return int(tok.rstrip("h"), 16)
            except ValueError:
                return None
    return None


def preserve_evidence_r03() -> dict:
    """停核 → 两核 state/PC/CPSR → 记录区 8 字 → CSR 三读(修正 -mem-ranges) + DevCfg。"""
    out: dict = {"steps": {}}
    tcl_parts = ["connect -url " + base.HW_URL,
                 'targets -set -filter {name =~ "*Cortex-A9*#0*"}',
                 "puts STOP_BEGIN; rst -processor -stop; puts STOP_END"]
    for idx in (0, 1):
        tcl_parts.append('targets -set -filter {name =~ "*Cortex-A9*#%d*"}' % idx)
        tcl_parts.append('puts "CORE%d_BEGIN"; state; rrd pc; rrd cpsr; puts "CORE%d_END"' % (idx, idx))
    tcl_parts.append("disconnect; exit")
    c0, e0 = drv.xsdb_checked("; ".join(tcl_parts), "EV_core_state")
    log = (RUN / "EV_core_state.log").read_text(encoding="utf-8", errors="replace") if (RUN / "EV_core_state.log").is_file() else ""
    cores = {}
    for idx in (0, 1):
        key = f"CORE{idx}"
        seg = _seg(log, f"{key}_BEGIN", f"{key}_END")
        cores[key] = {"raw": seg.strip(),
                      "pc": (seg.split("pc")[1].split()[0] if "pc" in seg else None),
                      "cpsr": (seg.split("cpsr")[1].split()[0] if "cpsr" in seg else None)}
    dap_ok = c0 == 0 and e0 is None and all(v["raw"] for v in cores.values())
    out["steps"]["core_state"] = {"exit_code": c0, "xsdb_error_text": e0, "cores": cores,
                                  "status": "PASS" if dap_ok else "NOT_CAPTURED",
                                  "note": "全空 ⇒ DAP 粘连/停核失败；此时后续 mrd 全部不可用"}
    out["dap_ok"] = dap_ok
    rf = RUN / "EV_record.bin"
    c1 = base.jtag_read(0x11B00000, 32, rf, "EV_mrd_record")
    words = list(struct.unpack("<8I", rf.read_bytes()[:32])) if (c1 == 0 and rf.is_file() and rf.stat().st_size >= 32) else []
    magic = {"mrd_exit": c1, "words_hex": [f"0x{w:08x}" for w in words], "magic": (words[0] if words else None),
             "valid": bool(words) and words[0] == 0x53344C01,
             "step_id": ((words[1] & 0xFF) if len(words) > 1 else None),
             "iter": ((words[1] >> 8) if len(words) > 1 else None),
             "done_step_id": ((words[2] & 0xFF) if len(words) > 2 else None),
             "done_iter": ((words[2] >> 8) if len(words) > 2 else None),
             "csr_addr": (words[3] if len(words) > 3 else None),
             "csr_val": (words[4] if len(words) > 4 else None),
             "dfsr": (words[5] if len(words) > 5 else None),
             "dfar": (words[6] if len(words) > 6 else None),
             "commit": (words[7] if len(words) > 7 else None),
             "abort_captured": bool(len(words) > 7 and words[7] == 0xAB0AB70B),
             "source": "normal_mrd"}
    magic["status"] = "PASS" if magic["valid"] else "NOT_CAPTURED"
    (RUN / "magic_parsed.json").write_text(json.dumps(magic, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    out["steps"]["record"] = magic
    # CSR 三读（-mem-ranges 修正；值解析按 "地址: 值" 行）
    tcl = ("connect -url %s; targets -set -filter {name =~ \"*Cortex-A9*#0*\"}; "
           "loadhw -hw %s -mem-ranges {0x43C00000 0x43C0FFFF}; puts LOADHW_DONE; "
           "puts CSR1_BEGIN; mrd 0x43C00010 1; puts CSR1_END; "
           "puts CSR2_BEGIN; mrd 0x43C00064 1; puts CSR2_END; "
           "puts CSR3_BEGIN; mrd 0x43C0000C 1; puts CSR3_END; "
           "puts DEVCFG_BEGIN; mrd 0xF8007000 1; puts DEVCFG_END; disconnect; exit"
           % (base.HW_URL, XSA.as_posix()))
    c2, e2 = drv.xsdb_checked(tcl, "EV_csr_tri_read")
    clog = (RUN / "EV_csr_tri_read.log").read_text(encoding="utf-8", errors="replace") if (RUN / "EV_csr_tri_read.log").is_file() else ""
    reads = {}
    for name, addr, tag in (("error_code", 0x43C00010, "CSR1"), ("last_reject", 0x43C00064, "CSR2"),
                            ("status", 0x43C0000C, "CSR3"), ("devcfg_status", 0xF8007000, "DEVCFG")):
        seg = _seg(clog, f"{tag}_BEGIN", f"{tag}_END")
        reads[name] = {"addr": hex(addr), "raw": seg.strip(), "value": _val_for(seg, addr)}
    csr_ok = c2 == 0 and e2 is None and all(v["value"] is not None for v in reads.values())
    out["steps"]["csr_tri_read"] = {"status": "PASS" if csr_ok else "CSR_DIAG_UNAVAILABLE",
                                    "loadhw_done": "LOADHW_DONE" in clog, "reads": reads,
                                    "note": "r02 的三读因 loadhw -memrange 无效选项 + 地址误当值而无效；本版已修正"}
    (RUN / "csr_devcfg_read.json").write_text(json.dumps(out["steps"]["csr_tri_read"], ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
    return out


def finish() -> int:
    ser = getattr(drv, "_SER", {}).get("ser")
    if ser is not None:
        try:
            ser.close()
        except Exception:  # noqa: BLE001
            pass
    killed = dg.kill_recent_hw_server()
    time.sleep(2)
    td = {"killed_pids": killed, "listening_3121": base.listening_3121(),
          "residual_processes": base.heavy_processes()}
    ok = td["listening_3121"] == 0 and not td.get("residual_processes")
    step("P4_teardown", {"status": "PASS" if ok else "FAIL", "exit_code": 0 if ok else 1, "detail": td})
    STATE["finished_utc8"] = now()
    STATE["elapsed_min"] = round((datetime.now(UTC8) - T0).total_seconds() / 60.0, 1)
    w2 = STATE["steps"].get("W2_longrun", {})
    ev = STATE["steps"].get("W3_preserve", {}).get("steps", {})
    rec = ev.get("record", {})
    csr = ev.get("csr_tri_read", {})
    m = w2.get("collect_meta") or {}
    if w2.get("status") == "PASS":
        STATE["conclusion"] = "LONGRUN_PASS"
    elif w2.get("collect") == "MAXTIME" and m.get("heartbeats", 0) > 0:
        STATE["conclusion"] = "DIAG_NOT_REPRODUCED"
    elif w2.get("status") == "STALL" and rec.get("valid"):
        STATE["conclusion"] = "DIAG_LOCATED"
    elif w2.get("status") == "STALL":
        STATE["conclusion"] = "DIAG_STALL_RECORD_NOT_CAPTURED"
    elif w2.get("status") == "FAIL":
        STATE["conclusion"] = "DIAG_FAILED_OR_PRELOAD_MISMATCH"
    else:
        STATE["conclusion"] = "DIAG_INCOMPLETE"
    (RUN / "results_diag_probe.json").write_text(json.dumps(STATE, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    lines = ["# 长跑停住定位 r03（预载真实 RAW+权重 + 五步探针；编程 PL 后不做系统复位）", "",
             f"- RunId：`{RUN_ID}`；开窗 {STATE['started_utc8']}；收窗 {STATE['finished_utc8']}；用时 {STATE['elapsed_min']} min",
             f"- 探针 ELF：`{PROBE_SHA}`", f"- 结论：**{STATE['conclusion']}**",
             f"- W2：{w2.get('status')}（collect={w2.get('collect')}，心跳 {m.get('heartbeats')}，"
             f"静默 {m.get('silence_s')} s，tensor_crc32={m.get('tensor_crc32')}）",
             f"- **最后一行打印**：`{w2.get('last_line')}`",
             f"- 记录区：magic={rec.get('magic')} valid={rec.get('valid')} step={rec.get('step_id')} iter={rec.get('iter')} "
             f"CSR=0x{(rec.get('csr_addr') or 0):08x} val=0x{(rec.get('csr_val') or 0):08x} "
             f"DFSR=0x{(rec.get('dfsr') or 0):08x} DFAR=0x{(rec.get('dfar') or 0):08x} commit=0x{(rec.get('commit') or 0):08x}",
             f"- CSR/DevCfg：{csr.get('status')} " + json.dumps({k: (v or {}).get('value') for k, v in csr.get('reads', {}).items()}),
             "", "## 各步"]
    for k, v in STATE["steps"].items():
        lines.append(f"- {k}：`{v.get('status')}` exit=`{v.get('exit_code')}`")
    lines += ["", "## 边界",
              "- 2B 平台位流 + SW 预处理 + fixture 非实拍；`ENABLE=0`；未写 QSPI；未改线；未 push；未用 `-force`；"
              "CSR/DevCfg 读仅作诊断，不作验收判据。", "- 不主张 G3/G4/G5；M3/M2 未闭合。"]
    (RUN / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[{now()}] done conclusion={STATE['conclusion']}", flush=True)
    return 0 if STATE["conclusion"] in ("DIAG_LOCATED", "LONGRUN_PASS", "DIAG_NOT_REPRODUCED") else 1


def main() -> int:
    print(f"[{now()}] probe longrun r03 start {RUN}", flush=True)
    ident = {"checks": [], "exit_code": 0}
    for tag, p, exp in (("bit", BIT, BIT_PREFIX), ("probe_elf", PROBE, PROBE_SHA),
                        ("m3", M3REF, M3REF_SHA), ("driver", W / "scripts/stage4_s4b/run_bringup_driver.py", dg.DRIVER_SHA),
                        ("fixture", FIXTURE, FIXTURE_SHA), ("weights", WEIGHTS, WEIGHTS_PREFIX),
                        ("xsa", XSA, None), ("runner", Path(__file__), None)):
        got = sha(p)
        ok = bool(got) and (exp is None or got.startswith(exp))
        ident["checks"].append({"tag": tag, "path": str(p), "sha256": got, "expect": exp, "match": ok})
        ident["exit_code"] = 0 if (ident["exit_code"] == 0 and ok) else 1
    ident["status"] = "PASS" if ident["exit_code"] == 0 else "FAIL"
    step("IDENT", ident)
    if ident["exit_code"] != 0:
        STATE["stop_reason"] = "身份核对失败"
        return finish()
    p0 = drv.p0_gate()
    p0["exit_code"] = 0 if p0.get("ok") else 1
    step("P0_gate", p0)
    if not p0.get("ok"):
        STATE["stop_reason"] = "P0 未通过"
        return finish()
    print(f"[{now()}] 空等 15 s 释放 USB 句柄", flush=True)
    time.sleep(15)
    en = dg.enum_preflight()
    step("P2_enum_preflight", en)
    if en["status"] != "PASS":
        STATE["stop_reason"] = "枚举 3 次均无 A9（若含 AP transaction error ⇒ DAP 粘连，需整机断电）"
        return finish()
    w0 = dg.restore_region("W0")
    step("W0_restore_candidate", w0)
    if w0["status"] != "PASS":
        STATE["stop_reason"] = f"W0 恢复失败 diff={w0.get('restore_diff')}"
        return finish()
    a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "W1_lvl_0xA_cfg")
    cp = base.program_pl(BIT, drv.BIT_REGISTERED_PREFIX) if a["status"] == "PASS" else 1
    if cp == 0:
        drv._PL_STATE["programmed"] = True   # 双重保险（r02 缺陷）
    f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "W1_lvl_0xF_after_cfg") if cp == 0 else {
        "status": "FAIL", "exit_code": 1}
    ok1 = a["status"] == "PASS" and cp == 0 and f["status"] == "PASS"
    step("W1_pspl_four_actions", {"status": "PASS" if ok1 else "FAIL", "exit_code": 0 if ok1 else 1,
                                  "lvl_0xA": a, "program_pl_exit": cp, "lvl_0xF": f,
                                  "pl_state_programmed": True})
    if not ok1:
        STATE["stop_reason"] = "四动作失败"
        return finish()
    lr = longrun_step()
    step("W2_longrun", lr)
    if lr.get("collect") in ("STALL", "STALL_EARLY", "FAIL", "MAXTIME", "PRELOAD_CRC_MISMATCH"):
        ev = preserve_evidence_r03()
        step("W3_preserve", {"status": "PASS" if ev.get("dap_ok") else "DAP_WEDGED", "exit_code": 0, **ev})
        if not ev.get("dap_ok"):
            STATE["stop_reason"] = "DAP 粘连：停核/读核失败，候选区恢复无法执行（需整机断电）"
            return finish()
    w4 = dg.restore_region("W4")
    cl = dg.clear_record()
    w4["record_clear"] = cl
    w4["status"] = "PASS" if (w4["status"] == "PASS" and cl["status"] == "PASS") else "FAIL"
    w4["exit_code"] = 0 if w4["status"] == "PASS" else 1
    step("W4_final_restore", w4)
    if w4["status"] != "PASS":
        STATE["stop_reason"] = "W4 恢复/记录清零未通过"
    return finish()


if __name__ == "__main__":
    sys.exit(main())