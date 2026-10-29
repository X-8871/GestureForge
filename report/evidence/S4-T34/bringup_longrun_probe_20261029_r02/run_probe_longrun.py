r"""长跑停住定位（A 项，2026-10-29）：预载真实 RAW+权重 -> 探针 ELF 连续跑 30 min。

复用 run_diag_longrun_v2.py 的窗口步骤（IDENT/P0/枚举/W0 恢复/W1 四动作/恢复/W4），
只替换：被测 ELF = 探针 ELF（f9095655…，含 start/epoch_ok/start_written/wait_done_pre/done
五步打印 + 0x11B00000 记录区 mark），并新增：
  1) 预载真实 fixture RAW（0x12000000）+ INT8 权重 GF8（0x10100000）——CRC 门禁 0x5B183B50；
  2) 采集上限 1950 s（覆盖应用自身 1800 s wall_ms_max）；
  3) 停住判据：最近一条完整行之后静默 > 60 s（心跳行为 `LONGRUN STEP iter=`）；
  4) 停住后先保全（停核 + 两核 state/PC + 记录区 8 字 + 三 CSR 只读），再恢复候选区。

不写 QSPI、不改线、ENABLE=0、禁 -force；不主张 G3/G4/G5。
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

W = Path(r"D:\codex-worktrees\w4")
TMP = Path(r"D:\codex-worktrees\w4\tmp\4\S4-T34")
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))
sys.path.insert(0, str(TMP))

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "bringup_longrun_probe_20261029_r02"
RUN = W / "report" / "evidence" / "S4-T34" / RUN_ID

# 先把 argv[1] 固定，避免被 import 的 diag 模块占位
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
M3REF_SHA = "41907f53"
BIT = Path(r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit")
INIT = drv.INIT_ELF
OFFLINE_TENSOR_CRC = 0x5B183B50
COLLECT_MAX_S = 1950          # 应用 wall_ms_max=1800 s，留 150 s 余量
STALL_QUIET_S = 60            # 心跳行之间的静默阈值（正常每轮 ~11.8 s）
EARLY_STALL_S = 150           # 有输出但始终没有心跳时，首轮前挂住的判据

# 覆盖 diag 模块的全局（供其 restore_region/preserve_evidence/step 复用）
dg.RUN_ID = RUN_ID
dg.RUN = RUN
dg.LR_ELF = PROBE
dg.LR_ELF_SHA = PROBE_SHA
dg.COLLECT_MAX_S = COLLECT_MAX_S
dg.STALL_QUIET_S = STALL_QUIET_S
dg.EARLY_STALL_S = EARLY_STALL_S
RUN.mkdir(parents=True, exist_ok=True)
base.RUN_DIR = RUN
drv.RUN_DIR = RUN
base.uart_open = drv.uart_open_preopened
base.load_elf = drv.load_elf_ddr

T0 = datetime.now(UTC8)
dg.STATE = {
    "task_id": "S4-T34", "run_id": RUN_ID,
    "phase": "长跑停住定位：预载真实 RAW+权重 + 五步探针 ELF（A 项）",
    "driver_sha256": dg.DRIVER_SHA, "probe_elf_sha256": PROBE_SHA,
    "fixture_sha256": FIXTURE_SHA, "weights_sha256_prefix": WEIGHTS_PREFIX,
    "offline_tensor_crc32": f"0x{OFFLINE_TENSOR_CRC:08x}",
    "collect_max_s": COLLECT_MAX_S, "stall_quiet_s": STALL_QUIET_S,
    "started_utc8": T0.isoformat(timespec="seconds"), "steps": {}, "stop_reason": None,
    "judgement": "停住 = 末行打印定位到具体步骤；若 30 min 无停住 ⇒ DIAG_NOT_REPRODUCED（如实记）",
    "boundary": "2B 平台位流 + SW 预处理 + fixture 非实拍；ENABLE=0；不烧 QSPI；不改线；不 push；不主张 G3/G4/G5",
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


def parse_result(line: str) -> dict:
    try:
        return json.loads(line.split("=", 1)[1])
    except Exception:  # noqa: BLE001
        return {}


def collect(log_path: Path) -> tuple[list[str], str, dict]:
    """采集 UART 直到 RESULT / FAIL / 停住 / 超时；STEP=1 行做 CRC 门禁。"""
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
                    crc = None
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
    """预载 RAW+权重 -> 装载探针 ELF -> 采集。"""
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
    load = drv.load_elf_ddr(PROBE, "W2_load", hold_reset=True)
    if load != 0:
        return {"status": "FAIL", "exit_code": 1, "reason": f"探针 ELF 装载失败 exit={load}"}

    lines, why, meta = collect(RUN / "W2_uart.log")
    result_line = next((ln for ln in lines if ln.startswith("LONGRUN RESULT=")), None)
    fail_line = next((ln for ln in lines if ln.startswith("LONGRUN FAIL ")), None)
    box_line = next((ln for ln in lines if ln.startswith("LONGRUN BOX ")), None)
    parsed = parse_result(result_line) if result_line else {}
    if why == "RESULT":
        ok = parsed.get("exit") == 0 and parsed.get("within_judgement") == 1
        status, code = ("PASS" if ok else "FAIL"), (0 if ok else 1)
    elif why == "PRELOAD_CRC_MISMATCH":
        status, code = "FAIL", 1
    elif why in ("NOUART", "FAIL"):
        status, code = "FAIL", 1
    elif why in ("STALL", "STALL_EARLY"):
        status, code = "STALL", 1
    else:  # MAXTIME
        status, code = "MAXTIME", 1
    return {"status": status, "exit_code": code, "collect": why, "collect_meta": meta,
            "result_line": result_line, "fail_line": fail_line, "box_line": box_line,
            "parsed": parsed, "last_line": (lines[-1] if lines else None),
            "uart_log": str(RUN / "W2_uart.log")}


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
    if w2.get("status") == "PASS":
        STATE["conclusion"] = "LONGRUN_PASS"
    elif w2.get("collect") == "MAXTIME" and (w2.get("collect_meta") or {}).get("heartbeats", 0) > 0:
        STATE["conclusion"] = "DIAG_NOT_REPRODUCED"
    elif w2.get("status") == "STALL" and rec.get("valid"):
        STATE["conclusion"] = "DIAG_LOCATED"
    elif w2.get("status") == "STALL":
        STATE["conclusion"] = "DIAG_NOT_CAPTURED"
    elif w2.get("status") == "FAIL":
        STATE["conclusion"] = "DIAG_FAILED_OR_PRELOAD_MISMATCH"
    else:
        STATE["conclusion"] = "DIAG_INCOMPLETE"
    (RUN / "results_diag_probe.json").write_text(json.dumps(STATE, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    m = w2.get("collect_meta") or {}
    lines = ["# 长跑停住定位（预载真实 RAW+权重 + 五步探针）", "",
             f"- RunId：`{RUN_ID}`；开窗 {STATE['started_utc8']}；收窗 {STATE['finished_utc8']}；"
             f"用时 {STATE['elapsed_min']} min",
             f"- 探针 ELF：`{PROBE_SHA}`", f"- 结论：**{STATE['conclusion']}**",
             f"- W2：{w2.get('status')}（collect={w2.get('collect')}，心跳 {m.get('heartbeats')}，"
             f"静默 {m.get('silence_s')} s，tensor_crc32={m.get('tensor_crc32')}）",
             f"- **最后一行打印**：`{w2.get('last_line')}`",
             f"- 记录区：magic={rec.get('magic')} valid={rec.get('valid')} step={rec.get('step_id')} "
             f"iter={rec.get('iter')} CSR=0x{(rec.get('csr_addr') or 0):08x} val=0x{(rec.get('csr_val') or 0):08x} "
             f"DFSR=0x{(rec.get('dfsr') or 0):08x} DFAR=0x{(rec.get('dfar') or 0):08x} "
             f"commit=0x{(rec.get('commit') or 0):08x}",
             f"- 三 CSR：{csr.get('status')} " + json.dumps({k: v.get('value') for k, v in csr.get('reads', {}).items()}),
             "", "## 各步"]
    for k, v in STATE["steps"].items():
        lines.append(f"- {k}：`{v.get('status')}` exit=`{v.get('exit_code')}`")
    lines += ["", "## 边界",
              "- 2B 平台位流 + SW 预处理 + fixture 非实拍；`ENABLE=0`；未写 QSPI；未改线；未 push；未用 `-force`；"
              "CSR 三读仅作诊断，不作验收判据。", "- 不主张 G3/G4/G5；M3/M2 未闭合。"]
    (RUN / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[{now()}] done conclusion={STATE['conclusion']}", flush=True)
    return 0 if STATE["conclusion"] in ("DIAG_LOCATED", "LONGRUN_PASS", "DIAG_NOT_REPRODUCED") else 1


def main() -> int:
    print(f"[{now()}] probe longrun start {RUN}", flush=True)
    ident = {"checks": [], "exit_code": 0}
    for tag, p, exp in (("bit", BIT, "555a70c2"), ("init_elf", INIT, "237dd959"),
                        ("probe_elf", PROBE, PROBE_SHA), ("m3", Path(r"D:\codex-worktrees\w4\report\evidence\S4-T32\window_a_20261027_r01\m3_snapshot_orig.bin"), M3REF_SHA),
                        ("driver", W / "scripts/stage4_s4b/run_bringup_driver.py", dg.DRIVER_SHA),
                        ("fixture", FIXTURE, FIXTURE_SHA), ("weights", WEIGHTS, WEIGHTS_PREFIX),
                        ("runner", Path(__file__), None)):
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
    if not p0.get("ok") and not p0.get("index_lock"):
        print(f"[{now()}] P0 未通过（{p0.get('heavy_processes')} / com4={p0.get('com4_error')}），10 s 后复检一次", flush=True)
        time.sleep(10)
        p0_2 = drv.p0_gate()
        p0 = p0_2 if p0_2.get("ok") else p0
        p0["retried_after_10s"] = True
    p0["exit_code"] = 0 if p0.get("ok") else 1
    step("P0_gate", p0)
    if not p0.get("ok"):
        STATE["stop_reason"] = "P0 未通过"
        return finish()
    print(f"[{now()}] 空等 15 s 释放 USB 句柄（不预起 hw_server）", flush=True)
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
    f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "W1_lvl_0xF_after_cfg") if cp == 0 else {
        "status": "FAIL", "exit_code": 1}
    ok1 = a["status"] == "PASS" and cp == 0 and f["status"] == "PASS"
    step("W1_pspl_four_actions", {"status": "PASS" if ok1 else "FAIL", "exit_code": 0 if ok1 else 1,
                                  "lvl_0xA": a, "program_pl_exit": cp, "lvl_0xF": f})
    if not ok1:
        STATE["stop_reason"] = "四动作失败"
        return finish()
    lr = longrun_step()
    step("W2_longrun", lr)
    if lr.get("collect") in ("STALL", "STALL_EARLY", "FAIL", "MAXTIME", "PRELOAD_CRC_MISMATCH"):
        ev = dg.preserve_evidence()
        step("W3_preserve", {"status": "PASS", "exit_code": 0, **ev})
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