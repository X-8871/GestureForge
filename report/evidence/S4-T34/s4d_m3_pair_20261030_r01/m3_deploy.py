r"""M3 成对取样窗口 · 部署阶段（r04 = 断电后恢复版）。

顺序（对应 lead r04 的窗口步骤中「部署 + 候选区重建 + 双读校验」，止于两核 Stopped）：
  D1 预停两核（rst -processor，禁 rst -system）
  D2 SLCR 四动作：LVL_SHFTR=0xA（解锁/关转换/FPGA_RST_CTRL=0/lock）
  D3 编程 2B 基线位流（Vivado batch program_2b_bit.tcl）
  D4 SLCR 恢复 LVL_SHFTR=0xF
  D5 load_elf_ddr：rst -processor → dow init.elf(d2_keep_pl ps7_init) → rst -processor → dow chainA → 内联 0xF 断言 → con
  D6 UART 采至 `CHAIN RESULT=`（单帧约 47 s）
  D7 帧后显式 stop 两核
  D8 只读 targets 核验两核均 Stopped
  D9 按登记快照重建候选区 [0x12000000,0x12C08000)（RESTORED_FROM_SNAPSHOT，仅一次）
  D10/D11 候选区全量双读（各 12,615,680 B）
  D12 双读 sha256 必须都 == baseline 41907f53…

之后由 m3_pair.py 做 capture before / 只读 mrd 事件 / capture after / compare。
不执行：rst -system；两次 capture 之间的任何写。
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

W = Path(r"D:\codex-worktrees\w4")
sys.path.insert(0, str(W / "scripts" / "stage4_s4b"))

import run_window_b_driver as base  # noqa: E402
import run_bringup_driver as drv  # noqa: E402

RUN = Path(r"D:\codex-worktrees\w4\report\evidence\S4-T34\s4d_m3_pair_20261030_r01")
BIT = Path(r"D:\FPGA_Competition\w2b\report\evidence\S2B-T19\visibility1_csr_fixed_20261016_r04\artifacts\s2b_inference.bit")
BIT_PREFIX = "555a70c2"
CHAIN = Path(r"D:\tmp\lead\tailfix_20261029_r01\build\s4d_ps_app_sw0_chainA.elf")
CHAIN_SHA = "87e049b4db8f7debd212f91b354648c2e83f845d419048ae5783d1a9923bdc52"
INIT = Path(drv.INIT_ELF)
INIT_SHA_PREFIX = "237dd959"
SNAP = W / "report/evidence/S4-T32/window_a_20261027_r01/m3_snapshot_orig.bin"
BASELINE = "41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf"
WINDOW_ID = "DSH-M3PAIR-20261030-W02"
EVENT_ID = "readonly-mrd-sampling-no-candidate-write"
LIFECYCLE_ID = "board-lifecycle-20261030-03"

RUN.mkdir(parents=True, exist_ok=True)
base.RUN_DIR = RUN
drv.RUN_DIR = RUN

STEPS: dict = {}


def sha(p: Path) -> str | None:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None


def rec(name: str, payload: dict) -> dict:
    STEPS[name] = payload
    (RUN / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
    (RUN / f"{name}.exit_code.txt").write_text(f"{payload.get('exit_code')}\n", encoding="utf-8", newline="\n")
    print(f"[{time.strftime('%H:%M:%S')}] {name}: {payload.get('status')} exit={payload.get('exit_code')}", flush=True)
    return payload


def stop_both(tag: str) -> dict:
    tcl = ("connect -url %s; " % base.HW_URL
           + 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; rst -processor -stop; after 300; '
           + 'targets -set -filter {name =~ "*Cortex-A9*#1*"}; rst -processor -stop; after 300; '
           + 'puts "BOTH_STOPPED"; disconnect; exit')
    code, err = drv.xsdb_checked(tcl, tag, timeout=300)
    return {"status": "PASS" if (code == 0 and err is None) else "FAIL",
            "exit_code": 0 if (code == 0 and err is None) else 1,
            "xsdb_exit": code, "error_text": err}


def core_states(tag: str) -> dict:
    code, err = drv.xsdb_checked("connect -url %s; targets; disconnect; exit" % base.HW_URL, tag, timeout=300)
    logp = RUN / f"{tag}.log"
    txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
    a9 = [ln.strip() for ln in txt.splitlines() if "Cortex-A9" in ln]
    stopped = [ln for ln in a9 if ("Stopped" in ln or "Suspended" in ln)]
    ok = (code == 0 and err is None and len(a9) >= 2 and len(stopped) >= 2)
    return {"status": "PASS" if ok else "FAIL", "exit_code": 0 if ok else 1,
            "xsdb_exit": code, "error_text": err, "a9_targets": a9, "raw_targets": txt}


def main() -> int:
    ident = {"bit": {"path": str(BIT), "sha256": sha(BIT), "expect_prefix": BIT_PREFIX},
             "init_elf": {"path": str(INIT), "sha256": sha(INIT), "expect_prefix": INIT_SHA_PREFIX},
             "chain_elf": {"path": str(CHAIN), "sha256": sha(CHAIN), "expect": CHAIN_SHA},
             "snapshot": {"path": str(SNAP), "sha256": sha(SNAP), "expect": BASELINE},
             "baseline": BASELINE, "window_id": WINDOW_ID, "event_id": EVENT_ID,
             "lifecycle_id": LIFECYCLE_ID}
    ok_ident = (bool(ident["bit"]["sha256"]) and ident["bit"]["sha256"].startswith(BIT_PREFIX)
                and bool(ident["init_elf"]["sha256"]) and ident["init_elf"]["sha256"].startswith(INIT_SHA_PREFIX)
                and ident["chain_elf"]["sha256"] == CHAIN_SHA
                and ident["snapshot"]["sha256"] == BASELINE)
    rec("D0_ident", {"status": "PASS" if ok_ident else "FAIL", "exit_code": 0 if ok_ident else 1,
                     "checks": ident})
    if not ok_ident:
        return 1

    heavy = base.heavy_processes()
    others = [h for h in heavy if h.lower() != "hw_server"]
    listen = base.listening_3121()
    ok_pf = (not others) and listen > 0
    rec("D0_preflight", {"status": "PASS" if ok_pf else "FAIL", "exit_code": 0 if ok_pf else 1,
                         "heavy_processes": heavy, "non_hw_server_heavy": others,
                         "listening_3121": listen})
    if not ok_pf:
        return 1

    enum_attempts = []
    for i in range(1, 4):
        tcl = ("connect -url %s; puts E_BEGIN; puts [targets]; puts E_END; disconnect; exit" % base.HW_URL)
        code, err = drv.xsdb_checked(tcl, f"D0_enum_targets_{i}", timeout=300)
        logp = RUN / f"D0_enum_targets_{i}.log"
        txt = logp.read_text(encoding="utf-8", errors="replace") if logp.is_file() else ""
        tail = txt.split("exit=", 1)[-1]
        lst = tail.split("E_BEGIN", 1)[1].split("E_END", 1)[0].strip() if "E_BEGIN" in tail else ""
        ok = (code == 0 and err is None and "Cortex-A9" in lst and "MPCore" in lst
              and "#0" in lst and "#1" in lst and "xc7z020" in lst)
        enum_attempts.append({"attempt": i, "xsdb_exit": code, "error_text": err,
                              "targets_raw": lst, "tap_ok": ok})
        if ok:
            break
        time.sleep(5)
    enum_ok = bool(enum_attempts) and enum_attempts[-1]["tap_ok"]
    rec("D0_enum_targets", {"status": "PASS" if enum_ok else "FAIL", "exit_code": 0 if enum_ok else 1,
                            "attempts": enum_attempts})
    if not enum_ok:
        return 1

    rec("D1_prestop_both", stop_both("D1_prestop_both_tcl"))
    if STEPS["D1_prestop_both"]["exit_code"] != 0:
        return 1

    lvl_a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "D2_lvl_0xA_cfg")
    rec("D2_lvl_0xA", {"status": "PASS" if lvl_a.get("status") == "PASS" else "FAIL",
                       "exit_code": 0 if lvl_a.get("status") == "PASS" else 1, "detail": lvl_a})
    if STEPS["D2_lvl_0xA"]["exit_code"] != 0:
        return 1

    cp = base.program_pl(BIT, BIT_PREFIX)
    rec("D3_program_pl_2b", {"status": "PASS" if cp == 0 else "FAIL", "exit_code": 0 if cp == 0 else 1,
                             "bit": str(BIT), "bit_prefix": BIT_PREFIX})
    if cp != 0:
        return 1
    drv._PL_STATE["programmed"] = True

    lvl_f = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "D4_lvl_0xF_after_cfg")
    rec("D4_lvl_0xF", {"status": "PASS" if lvl_f.get("status") == "PASS" else "FAIL",
                       "exit_code": 0 if lvl_f.get("status") == "PASS" else 1, "detail": lvl_f})
    if STEPS["D4_lvl_0xF"]["exit_code"] != 0:
        return 1

    t_load = time.time()
    load = drv.load_elf_ddr(CHAIN, "D5_load_chainA", hold_reset=True)
    rec("D5_load_chainA", {"status": "PASS" if load == 0 else "FAIL", "exit_code": 0 if load == 0 else 1,
                           "load_exit": load, "elapsed_s": round(time.time() - t_load, 1),
                           "elf": str(CHAIN), "elf_sha256": CHAIN_SHA,
                           "path": "rst -processor → dow init.elf(d2_keep_pl) → rst -processor → dow chainA → 内联 0xF 断言 → con"})
    if load != 0:
        return 1

    ser = drv.ensure_uart()
    lines: list[str] = []
    buf = ""
    t0 = time.time()
    hit = False
    while time.time() - t0 < 150:
        chunk = ser.read(4096)
        if not chunk:
            continue
        buf += chunk.decode("utf-8", "replace")
        while "\n" in buf:
            raw, buf = buf.split("\n", 1)
            s = raw.strip()
            if s:
                lines.append(s)
                if s.startswith("CHAIN RESULT="):
                    hit = True
        if hit:
            break
    (RUN / "chain_uart.log").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    rec("D6_frame", {"status": "PASS" if hit else "FAIL", "exit_code": 0 if hit else 1,
                     "wait_s": round(time.time() - t0, 1), "uart_lines": len(lines),
                     "result_line": next((ln for ln in lines if ln.startswith("CHAIN RESULT=")), None),
                     "step_lines": [ln for ln in lines if ln.startswith("CHAIN STEP=")]})
    if not hit:
        return 1

    rec("D7_stop_both_after_frame", stop_both("D7_stop_both_after_frame_tcl"))
    if STEPS["D7_stop_both_after_frame"]["exit_code"] != 0:
        return 1

    cs = core_states("D8_targets_state")
    rec("D8_core_states", cs)

    words = drv.CAND_BYTES // 4
    w, we = drv.jtag_write_checked(SNAP, drv.CAND_BASE, "D9_restore_write", words)
    rec("D9_restore_snapshot", {
        "status": "PASS" if (w == 0 and we is None) else "FAIL", "exit_code": 0 if (w == 0 and we is None) else 1,
        "marker": "RESTORED_FROM_SNAPSHOT", "snapshot": str(SNAP), "snapshot_sha256": BASELINE,
        "addr": hex(drv.CAND_BASE), "bytes": drv.CAND_BYTES, "words": words,
        "write_exit": w, "write_error_text": we,
        "note": "断电后 DDR 内容丢失；按 r04 用登记快照重建候选区内容（同一字节序列），不改基准"})
    if STEPS["D9_restore_snapshot"]["exit_code"] != 0:
        return 1

    shas = {}
    for tag, out in (("D10_region_read1", "region_read1.bin"), ("D11_region_read2", "region_read2.bin")):
        outp = RUN / out
        code = drv._dump(tag, drv.CAND_BASE, drv.CAND_BYTES, outp)
        sz = outp.stat().st_size if outp.is_file() else None
        h = sha(outp) if outp.is_file() else None
        shas[tag] = {"sha256": h, "bytes": sz}
        rec(tag, {"status": "PASS" if (code == 0 and sz == drv.CAND_BYTES) else "FAIL",
                  "exit_code": 0 if (code == 0 and sz == drv.CAND_BYTES) else 1,
                  "dump_exit": code, "bytes": sz, "sha256": h, "file": str(outp)})
        if code != 0 or sz != drv.CAND_BYTES:
            return 1
        shas[tag]["match_baseline"] = (h == BASELINE)

    ok_v = all(shas[t]["sha256"] == BASELINE for t in ("D10_region_read1", "D11_region_read2"))
    rec("D12_restore_verify", {"status": "PASS" if ok_v else "FAIL", "exit_code": 0 if ok_v else 1,
                               "baseline": BASELINE, "reads": shas,
                               "rule": "两次全量读 sha256 均须 == baseline，不等即停"})
    if not ok_v:
        return 1

    all_ok = all(v.get("exit_code") == 0 for k, v in STEPS.items() if k.startswith("D"))
    summary = {"status": "PASS" if all_ok else "FAIL", "exit_code": 0 if all_ok else 1,
               "window_id": WINDOW_ID, "event_id": EVENT_ID, "lifecycle_id": LIFECYCLE_ID,
               "steps": {k: {"status": v.get("status"), "exit_code": v.get("exit_code")} for k, v in STEPS.items()},
               "ident": ident, "core_states": cs.get("a9_targets"),
               "restore": {"marker": "RESTORED_FROM_SNAPSHOT", "baseline": BASELINE,
                           "read1_sha256": shas["D10_region_read1"]["sha256"],
                           "read2_sha256": shas["D11_region_read2"]["sha256"]},
               "note": "部署+重建完成；capture/event/compare 由 m3_pair.py 与 xsdb 在窗口内继续执行"}
    rec("D13_deploy_summary", summary)
    print("DEPLOY_DONE status=%s" % summary["status"], flush=True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())