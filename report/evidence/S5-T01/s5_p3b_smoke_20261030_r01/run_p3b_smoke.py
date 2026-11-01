r"""P3b 上屏冒烟窗口执行器（阶段5 / S5-T01，2026-10-30 r01）——**离线编写 + dry-run**。

目的：在一个受控板级窗口里，把 P3b 位流装进 PL、跑显示 ELF，抓 `S5DISP RESULT=` 并按
**事先写死**的判据给出 PASS/FAIL；失败即停、保原文、不重试、**绝不 `rst -system`**。

判据（写死，不得放宽；改判据必须新 RunId + lead 批准）：
  J-1 `S5DISP RESULT` JSON 可解析，且包含 pass/fps_cap/fps_inf/fps_dis/latency_ms/age_ms/vdma_err；
  J-2 `pass == 1`；
  J-3 `vdma_err == 0`；
  J-4 `fps_dis >= 55`（720p60 理论 60；**且 <= 90**：>90 视为单位歧义，直接 FAIL，不猜 x10）；
  J-5 `age_ms <= 47317`（= 47300 + 17；基于 47.3 s 推理周期 + 17 ms 抖动）；
  J-6 `0 <= latency_ms <= 1000`（数值合理，非 0xFFFF/负数/离谱值）；
  J-7 结果行与 JSON 里**无** `error`/`timeout` 语义（fail-closed）；
  J-8 UART 结果窗 >= 60 s（命令行下限强制），且**末尾半行被丢弃**、不计入判据。

边界：
  · 本脚本只做窗口执行；**不跑 Vivado 综合/实现**（PL 编程由现有 `program_2b_bit.tcl` 完成，
    这是窗口动作，不是构建动作）；
  · PL 编程后**禁 `rst -system`**：装载统一 `drv.load_elf_ddr`（`_PL_STATE["programmed"]=True`
    时它只用 `rst -processor -stop`，保持 PL 配置）；
  · `ENABLE=0`；不烧 QSPI；不改线；不 push；不主张 G3/G4/G5；
  · 任何一步失败：停、保留日志、写 `window_close.txt`，**不重试**。

用法：
  python -B run_p3b_smoke.py --dry-run                 # 只打印命令与判据（不碰硬件、不建目录）
  python -B run_p3b_smoke.py --run-id s5_p3b_smoke_20261030_r01
  python -B run_p3b_smoke.py --expect-bit-sha <sha> --expect-elf-sha <sha> ...
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

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

W = Path(r"D:\codex-worktrees\w4")
SCRIPTS = W / "scripts" / "stage4_s4b"
sys.path.insert(0, str(SCRIPTS))

import run_bringup_driver as drv  # noqa: E402  v3.2.7（6c41ff4c…）
import run_window_b_driver as base  # noqa: E402

UTC8 = timezone(timedelta(hours=8))

# ---- 身份（IDENT）：期望值写死；位流未产出时由 dry-run 只报告缺失 ----------------------
DRIVER_SHA = "6c41ff4c4c4043d8f53ff963806f8e3e5211086ca8de204b0773985898d4e461"  # v3.2.7
INIT_ELF_SHA = "237dd959f903589c657b743ea1fce175628aaa24020384058fc66339c779e7b1"
DEFAULT_BIT = Path(r"D:\tmp\lead\p3b_video_20261030_r01\out\s4d_p3b_r01.bit")
DEFAULT_ELF = Path(r"D:\tmp\lead\p3b_display_sw_20261030_r01\build\s5_display_app.elf")
DEFAULT_ELF_SHA = "9fdec1d909054b1a08fdcd9a6b048fc8e0381327dc07e711e9c85d8de8790b38"
DEFAULT_RUN_ID = "s5_p3b_smoke_20261030_r01"
EVID_ROOT = W / "report" / "evidence" / "S5-T01"

# ---- 判据（写死） -----------------------------------------------------------------------
COLLECT_MIN_S = 60          # 结果窗下限（任务硬要求）
COLLECT_DEFAULT_S = 90      # 默认给 90 s（>60）
FPS_DIS_MIN = 55
FPS_DIS_SANITY_MAX = 90     # >90 ⇒ 单位歧义，FAIL（不猜 x10）
AGE_MAX_MS = 47317          # 47300 + 17
LATENCY_MAX_MS = 1000
REQUIRED_KEYS = ("pass", "fps_cap", "fps_inf", "fps_dis", "latency_ms", "age_ms", "vdma_err")

STATE: dict = {}
FAILS: list[str] = []


# ---- 通用小工具 -------------------------------------------------------------------------
def now() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def sha_file(p: Path | None) -> str | None:
    if p is None or not p.is_file():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def out_dir(run_id: str) -> Path:
    return EVID_ROOT / run_id


def step(run: Path | None, name: str, payload: dict) -> dict:
    """落 step JSON + exit_code（dry-run 时 run=None，只打印）。"""
    payload.setdefault("utc8", now())
    STATE.setdefault("steps", {})[name] = payload
    if run is None:
        print(f"[DRY] {name}: status={payload.get('status')} exit={payload.get('exit_code')}", flush=True)
        return payload
    (run / f"{name}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8", newline="\n")
    (run / f"{name}.exit_code.txt").write_text(f"{payload.get('exit_code')}\n",
                                               encoding="utf-8", newline="\n")
    print(f"[{now()}] {name}: status={payload.get('status')} exit={payload.get('exit_code')}", flush=True)
    return payload


def _no_system_reset(cmd_text: str) -> None:
    """硬守卫：任何我们要执行的命令文本里都不允许出现 `rst -system`。"""
    if "rst -system" in cmd_text:
        raise RuntimeError("禁止 rst -system（会清掉 PL 配置）：" + cmd_text[:160])


def pc_memory_gate() -> dict:
    """内存检查：空闲物理内存 >= 1 GB（不足则门禁失败，避免窗口中途 OOM）。"""
    import subprocess
    try:
        out = subprocess.run(
            ["pwsh", "-NoProfile", "-Command",
             "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)"],
            capture_output=True, text=True, timeout=60)
        free_gb = float((out.stdout or "0").strip() or 0)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "free_gb": None, "error": str(exc)}
    return {"ok": free_gb >= 1.0, "free_gb": free_gb, "threshold_gb": 1.0}


# ---- 身份核对 ---------------------------------------------------------------------------
def ident(bit: Path, elf: Path, expect_bit_sha: str, expect_elf_sha: str) -> dict:
    checks: list[dict] = []

    def add(tag: str, path: Path, expect: str | None, required: bool) -> bool:
        got = sha_file(path)
        ok = bool(got) and (expect is None or got.startswith(expect.lower()))
        checks.append({"tag": tag, "path": str(path), "exists": path.is_file(),
                       "bytes": path.stat().st_size if path.is_file() else None,
                       "sha256": got, "expect_prefix": expect, "required": required, "match": ok})
        return ok

    ok_bit = add("p3b_bitstream", bit, expect_bit_sha, True)
    ok_elf = add("display_elf", elf, expect_elf_sha, True)
    ok_drv = add("driver_v327", SCRIPTS / "run_bringup_driver.py", DRIVER_SHA, True)
    ok_init = add("init_elf", drv.INIT_ELF, INIT_ELF_SHA, True)
    ok_base = add("base_driver", SCRIPTS / "run_window_b_driver.py", None, True)
    ok = ok_bit and ok_elf and ok_drv and ok_init and ok_base
    return {"status": "PASS" if ok else "FAIL", "exit_code": 0 if ok else 1,
            "checks": checks,
            "bit_frozen": bool(expect_bit_sha),
            "note": "位流未给 --expect-bit-sha 时 SHA 仅记录、不判冻结；显示 ELF 重建后须用 "
                    "--expect-elf-sha 传新值（默认值来自计划基线）"}


# ---- UART 采集（滤掉末尾半行） -----------------------------------------------------------
def collect_uart(ser, needle: str, seconds: int, raw_path: Path) -> dict:
    """读 UART 到 needle 出现或超时；只有以 '\\n' 结尾的完整行才进入 lines。

    末尾未换行的半行**不解析**，单独存 `tail_partial`（防止把半截 JSON 当结果）。
    """
    lines: list[str] = []
    tail = b""
    buf = b""
    hit = False
    t0 = time.time()
    deadline = t0 + seconds
    while time.time() < deadline:
        try:
            chunk = ser.read(4096)
        except Exception as exc:  # noqa: BLE001
            lines.append(f"[uart_read_error] {exc}")
            break
        if not chunk:
            continue
        buf += chunk
        while b"\n" in buf:
            raw, buf = buf.split(b"\n", 1)
            s = raw.decode("utf-8", errors="replace").rstrip("\r").strip()
            if s:
                lines.append(s)
                if needle in s:
                    hit = True
        if hit:
            break
    tail = buf[:4096]
    elapsed = round(time.time() - t0, 2)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")
    tail_path = raw_path.with_name(raw_path.stem + "_tail_partial.txt")
    tail_path.write_text(tail.decode("utf-8", errors="replace"), encoding="utf-8", newline="\n")
    return {"lines": lines, "hit": hit, "elapsed_s": elapsed, "seconds_budget": seconds,
            "tail_partial_bytes": len(tail),
            "tail_partial_text": tail.decode("utf-8", errors="replace"),
            "tail_partial_file": str(tail_path),
            "tail_partial_dropped": True}


# ---- 判据（写死） -----------------------------------------------------------------------
def judge(lines: list[str]) -> dict:
    """对完整行集合执行 J-1..J-7；返回逐条结果与总体 verdict。"""
    result_lines = [ln for ln in lines if ln.startswith("S5DISP RESULT=")]
    res: dict = {"criteria": [], "verdict": "FAIL", "result_line": None, "parsed": None,
                 "reason": None}

    def crit(cid: str, desc: str, ok: bool, detail=None) -> None:
        res["criteria"].append({"id": cid, "desc": desc, "pass": bool(ok), "detail": detail})

    if not result_lines:
        any_s5 = [ln for ln in lines if ln.startswith("S5DISP")]
        res["reason"] = ("no_result_line" if any_s5 else "no_s5disp_line")
        crit("J-1", "S5DISP RESULT 行存在且 JSON 可解析", False,
             {"s5disp_lines": any_s5[-10:], "reason": res["reason"]})
        for cid, desc in (("J-2", "pass==1"), ("J-3", "vdma_err==0"), ("J-4", "fps_dis>=55"),
                          ("J-5", "age_ms<=47317"), ("J-6", "latency_ms 合理"),
                          ("J-7", "无 error/timeout")):
            crit(cid, desc, False, "no_result_line")
        return res

    line = result_lines[-1]
    res["result_line"] = line
    raw_json = line.split("=", 1)[1].strip()
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        res["reason"] = f"json_parse_error: {exc}"
        crit("J-1", "S5DISP RESULT 行存在且 JSON 可解析", False, str(exc))
        return res
    res["parsed"] = parsed
    missing = [k for k in REQUIRED_KEYS if k not in parsed]
    crit("J-1", "S5DISP RESULT 行存在且 JSON 可解析（含全部键）", not missing, {"missing": missing})
    if missing:
        res["reason"] = f"missing_keys: {missing}"
        return res

    def as_int(key: str):
        v = parsed.get(key)
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float) and v.is_integer():
            return int(v)
        return None

    p = as_int("pass")
    vdma = as_int("vdma_err")
    fps = as_int("fps_dis")
    age = as_int("age_ms")
    lat = as_int("latency_ms")
    crit("J-2", "pass==1", p == 1, {"pass": parsed.get("pass")})
    crit("J-3", "vdma_err==0", vdma == 0, {"vdma_err": parsed.get("vdma_err")})
    if fps is None:
        crit("J-4", f"fps_dis>={FPS_DIS_MIN}（且 <= {FPS_DIS_SANITY_MAX}，>上限视为单位歧义）", False,
             {"fps_dis": parsed.get("fps_dis"), "reason": "not_int"})
    elif fps > FPS_DIS_SANITY_MAX:
        crit("J-4", f"fps_dis>={FPS_DIS_MIN}（且 <= {FPS_DIS_SANITY_MAX}）", False,
             {"fps_dis": fps, "reason": "unit_ambiguous（疑似 x10；不猜）"})
    else:
        crit("J-4", f"fps_dis>={FPS_DIS_MIN}（且 <= {FPS_DIS_SANITY_MAX}）", fps >= FPS_DIS_MIN,
             {"fps_dis": fps})
    crit("J-5", f"age_ms<={AGE_MAX_MS}", age is not None and 0 <= age <= AGE_MAX_MS,
         {"age_ms": parsed.get("age_ms")})
    crit("J-6", f"0<=latency_ms<={LATENCY_MAX_MS}", lat is not None and 0 <= lat <= LATENCY_MAX_MS,
         {"latency_ms": parsed.get("latency_ms")})
    low = raw_json.lower()
    bad_tokens = [t for t in ("error", "timeout") if t in low]
    crit("J-7", "结果行无 error/timeout 语义", not bad_tokens, {"bad_tokens": bad_tokens})

    ok = all(c["pass"] for c in res["criteria"])
    res["verdict"] = "PASS" if ok else "FAIL"
    res["reason"] = None if ok else "criterion_failed"
    return res


# ---- dry-run：打印将要执行的命令与判据 ---------------------------------------------------
def dry_run(args) -> int:
    run = None
    bit = Path(args.bit)
    elf = Path(args.elf)
    print("=" * 78)
    print(f"[DRY-RUN] P3b 上屏冒烟窗口执行器  RunId={args.run_id}")
    print(f"[DRY-RUN] 证据目录（真实运行才创建）：{out_dir(args.run_id)}")
    print("=" * 78)
    print("[DRY-RUN] 依赖检查（只读；缺失不失败，只报告）：")
    for tag, p, exp in (("P3b 位流", bit, args.expect_bit_sha),
                        ("显示 ELF", elf, args.expect_elf_sha or DEFAULT_ELF_SHA),
                        ("驱动 v3.2.7", SCRIPTS / "run_bringup_driver.py", DRIVER_SHA),
                        ("init ELF", drv.INIT_ELF, INIT_ELF_SHA)):
        got = sha_file(p)
        state = "存在" if p.is_file() else "**缺失**"
        match = "match" if (got and exp and got.startswith(exp.lower())) else ("record_only" if not exp else "MISMATCH")
        print(f"  - {tag:10s} {state:8s} path={p}  sha={got}  expect={exp or '(仅记录)'}  -> {match}")

    cmds: list[str] = []
    cmds.append(f"IDENT: sha256sum {bit} {elf} {SCRIPTS / 'run_bringup_driver.py'} {drv.INIT_ELF}")
    cmds.append("P0: pwsh Get-Process / Get-NetTCPConnection -LocalPort 3121 -State Listen "
                "/ ::Get-CimInstance Win32_OperatingSystem（空闲内存 >= 1 GB）/ 打开 COM4@115200")
    cmds.append(f"P1: 启动 {base.HW_SERVER}（等 3121 LISTENING）")
    cmds.append(f"P2: {base.XSDB} -eval \"connect -url {base.HW_URL}; puts [targets]; disconnect; exit\"")
    cmds.append(f"W1a: xsdb SLCR UNLOCK 0xDF0D -> LVL_SHFTR_EN(0xF8000900)=0x{drv.LVL_SHFTR_CFG:02X}（PL 配置期间）")
    cmds.append(f"W1b: {base.VIVADO} -mode batch -source {SCRIPTS / 'program_2b_bit.tcl'} "
                f"-tclargs {bit} <bit_sha256>   # 期望输出 PROGRAM_OK")
    cmds.append(f"W1c: xsdb LVL_SHFTR_EN=0x{drv.LVL_SHFTR_ON:02X} 并读回断言（四动作完成）")
    cmds.append(f"W2: drv.load_elf_ddr({elf}, hold_reset=True)  # 内含 init.elf ps7_init；"
                f"已编程时只用 rst -processor -stop（**禁 rst -system**）")
    cmds.append(f"W3: 串口 COM4@115200 读 UART，needle='S5DISP RESULT='，窗口 {args.collect_seconds}s（>= {COLLECT_MIN_S}s）")
    cmds.append("W3b: 只解析完整行；末尾半行丢弃（tail_partial 单独记录）")
    cmds.append("W3c: 判据 J-1..J-7 -> W3_judgement.json / results_p3b_smoke.json")
    cmds.append("W4: 关串口 -> taskkill hw_server(自起 PID) -> 核验 3121 无 LISTENING / 无残留重型进程 -> window_close.txt")
    for i, c in enumerate(cmds, 1):
        print(f"[DRY] {i:02d}. {c}")
    print("[DRY-RUN] 判据（写死）：")
    crit_lines = [
        f"J-1 S5DISP RESULT JSON 可解析且含 {', '.join(REQUIRED_KEYS)}",
        "J-2 pass == 1",
        "J-3 vdma_err == 0",
        f"J-4 fps_dis >= {FPS_DIS_MIN} 且 <= {FPS_DIS_SANITY_MAX}（>上限=单位歧义=>FAIL）",
        f"J-5 age_ms <= {AGE_MAX_MS}",
        f"J-6 0 <= latency_ms <= {LATENCY_MAX_MS}",
        "J-7 结果行无 error/timeout 语义（fail-closed）",
        f"J-8 UART 窗口 >= {COLLECT_MIN_S}s 且末尾半行丢弃",
    ]
    for ln in crit_lines:
        print(f"[DRY] {ln}")
    print(f"[DRY-RUN SUMMARY] commands={len(cmds)} criteria={len(crit_lines)} "
          f"collect_seconds={args.collect_seconds} dry_run=1")
    print("[DRY-RUN] 未触碰板卡/JTAG/COM4/hw_server，未创建任何目录，未运行 Vivado。")
    return 0


# ---- 真实窗口执行 -----------------------------------------------------------------------
def run_window(args) -> int:
    run = out_dir(args.run_id)
    run.mkdir(parents=True, exist_ok=True)
    base.RUN_DIR = run
    drv.RUN_DIR = run
    t0 = datetime.now(UTC8)
    STATE.update({"task_id": "S5-T01", "run_id": args.run_id,
                  "phase": "P3b 上屏冒烟（P3b 位流 + 显示 ELF，HDMI 720p60）",
                  "started_utc8": t0.isoformat(timespec="seconds"),
                  "driver_sha256": DRIVER_SHA, "init_elf_sha256": INIT_ELF_SHA,
                  "collect_seconds": args.collect_seconds, "steps": {}, "stop_reason": None,
                  "criteria_version": "J-1..J-8（写死，见脚本 docstring）",
                  "boundary": "ENABLE=0；不烧 QSPI；不改线；不 push；不主张 G3/G4/G5"})

    bit = Path(args.bit)
    elf = Path(args.elf)
    hw_pid = None
    hw_started = False

    try:
        # S1 IDENT
        idt = ident(bit, elf, args.expect_bit_sha, args.expect_elf_sha or DEFAULT_ELF_SHA)
        step(run, "S1_IDENT", idt)
        if idt["exit_code"] != 0:
            STATE["stop_reason"] = "身份核对失败（未碰板卡）"
            return finish(run, hw_pid, hw_started)

        # S2 板卡前置
        p0 = drv.p0_gate()
        p0["real_index_lock_present"] = Path(r"D:\FPGA_Competition\.git\worktrees\w4\index.lock").exists()
        p0["memory"] = pc_memory_gate()
        p0["ok"] = (bool(p0.get("ok")) and not p0["real_index_lock_present"]
                    and bool(p0["memory"].get("ok")))
        p0["exit_code"] = 0 if p0["ok"] else 1
        step(run, "S2_P0_gate", p0)
        if not p0["ok"]:
            STATE["stop_reason"] = "P0 门禁未通过（不碰板卡）"
            return finish(run, hw_pid, hw_started)

        # S3 起 hw_server + 枚举
        srv = base.start_hw_server()
        hw_started = True
        hw_pid = srv.get("pid")
        srv["exit_code"] = 0 if srv.get("ok") else 1
        step(run, "S3_hw_server", srv)
        if srv["exit_code"] != 0:
            STATE["stop_reason"] = "hw_server 未就绪"
            return finish(run, hw_pid, hw_started)
        _no_system_reset("")
        en_tcl = f"connect -url {base.HW_URL}; puts E_BEGIN; puts [targets]; puts E_END; disconnect; exit"
        ec = base.xsdb(en_tcl, "S3_enum")
        en_log = run / "S3_enum.log"
        en_txt = en_log.read_text(encoding="utf-8", errors="replace") if en_log.is_file() else ""
        en = {"status": "PASS" if (ec == 0 and "Cortex-A9" in en_txt) else "FAIL",
              "exit_code": 0 if (ec == 0 and "Cortex-A9" in en_txt) else 1,
              "xsdb_exit": ec, "a9_seen": "Cortex-A9" in en_txt}
        step(run, "S3_enum", en)
        if en["exit_code"] != 0:
            STATE["stop_reason"] = "JTAG 枚举失败（未见 Cortex-A9）"
            return finish(run, hw_pid, hw_started)

        # S4 PL 编程：四动作（禁 rst -system）
        a = drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_CFG, "S4_lvl_0xA")
        bit_sha = sha_file(bit)
        cp = base.program_pl(bit, bit_sha) if a.get("status") == "PASS" else 1
        if cp == 0:
            drv._PL_STATE["programmed"] = True
        f = (drv.enable_ps_pl_level_shifters(drv.LVL_SHFTR_ON, "S4_lvl_0xF") if cp == 0
             else {"status": "FAIL", "reason": "PL 编程未成功"})
        ok1 = (a.get("status") == "PASS" and cp == 0 and f.get("status") == "PASS")
        step(run, "S4_pspl_four_actions",
             {"status": "PASS" if ok1 else "FAIL", "exit_code": 0 if ok1 else 1,
              "lvl_0xA": a, "program_pl_exit": cp, "lvl_0xF": f,
              "bit_sha256": bit_sha, "rst_system_used": False})
        if not ok1:
            STATE["stop_reason"] = "四动作/装 PL 未通过（不继续）"
            return finish(run, hw_pid, hw_started)

        # S5 ps7_init（保持 PL）+ 装载显示 ELF
        if not drv._PL_STATE["programmed"]:
            raise RuntimeError("_PL_STATE.programmed 必须为 True，否则 load_elf_ddr 会 rst -system")
        load = drv.load_elf_ddr(elf, "S5_load_display", hold_reset=True)
        step(run, "S5_load_display", {"status": "PASS" if load == 0 else "FAIL",
                                       "exit_code": 0 if load == 0 else 1, "load_elf_exit": load,
                                       "elf": str(elf), "elf_sha256": sha_file(elf),
                                       "ps7_init": "init.elf -> con 2500ms -> rst -processor -stop "
                                                   "-> dow display ELF -> LVL 0xF 断言 -> con"})
        if load != 0:
            STATE["stop_reason"] = f"显示 ELF 装载失败 exit={load}"
            return finish(run, hw_pid, hw_started)

        # S6 采 UART（>=60 s；只解析完整行）
        ser, err = drv.uart_open_preopened()
        if ser is None:
            step(run, "S6_uart", {"status": "FAIL", "exit_code": 1, "reason": err})
            STATE["stop_reason"] = "COM4 不可用"
            return finish(run, hw_pid, hw_started)
        col = collect_uart(ser, "S5DISP RESULT=", args.collect_seconds, run / "S5DISP_uart.log")
        lines = col.pop("lines")
        step(run, "S6_uart", {"status": "PASS" if col["hit"] else "FAIL",
                              "exit_code": 0 if col["hit"] else 1,
                              "result_seen": col["hit"], "lines_total": len(lines),
                              "elapsed_s": col["elapsed_s"], "seconds_budget": col["seconds_budget"],
                              "tail_partial_bytes": col["tail_partial_bytes"],
                              "tail_partial_dropped": True,
                              "tail_partial_text": col["tail_partial_text"],
                              "log": str(run / "S5DISP_uart.log"),
                              "first_lines": lines[:5], "last_lines": lines[-5:]})

        # S7 判据
        jd = judge(lines)
        (run / "W3_judgement.json").write_text(
            json.dumps(jd, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        jd.update({"exit_code": 0 if jd["verdict"] == "PASS" else 1,
                   "criteria_written": str(run / "W3_judgement.json")})
        step(run, "S7_judgement", jd)
        if jd["verdict"] != "PASS":
            STATE["stop_reason"] = f"判据 FAIL：{jd.get('reason')}"
            return finish(run, hw_pid, hw_started, verdict="FAIL")

        return finish(run, hw_pid, hw_started, verdict="PASS")

    except Exception as exc:  # noqa: BLE001
        import traceback
        (run / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8", newline="\n")
        STATE["stop_reason"] = STATE.get("stop_reason") or f"异常：{exc}"
        print(f"[{now()}] EXC {exc}", flush=True)
        return finish(run, hw_pid, hw_started)


def finish(run: Path, hw_pid, hw_started: bool, verdict: str = "STOPPED") -> int:
    """收窗：关串口、停自起 hw_server、核验 3121/残留、写 window_close.txt。"""
    ser = getattr(drv, "_SER", {}).get("ser")
    if ser is not None:
        try:
            ser.close()
        except Exception:  # noqa: BLE001
            pass
    td = base.stop_hw_server(hw_pid) if (hw_started and hw_pid) else {
        "stopped_pid": None, "listening_3121": base.listening_3121(),
        "residual_processes": base.heavy_processes()}
    td_ok = td.get("listening_3121") == 0 and not td.get("residual_processes")
    step(run, "S8_teardown", {"status": "PASS" if td_ok else "FAIL",
                              "exit_code": 0 if td_ok else 1, "detail": td})
    STATE["finished_utc8"] = now()
    STATE["elapsed_min"] = round((datetime.now(UTC8)
                                  - datetime.fromisoformat(STATE["started_utc8"])).total_seconds() / 60.0, 2)
    STATE["verdict"] = verdict if td_ok else "STOPPED_TEARDOWN_FAIL"
    STATE["failed_steps"] = [k for k, v in STATE.get("steps", {}).items()
                             if v.get("exit_code") not in (0, None)]
    jd = STATE.get("steps", {}).get("S7_judgement", {})
    conclusion = ("P3B_SMOKE_PASS" if STATE["verdict"] == "PASS" else
                  ("P3B_SMOKE_FAIL" if STATE["verdict"] == "FAIL" else "P3B_SMOKE_STOPPED"))
    STATE["conclusion"] = conclusion
    (run / "results_p3b_smoke.json").write_text(json.dumps(STATE, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    lines = ["# P3b 上屏冒烟窗口记录", "",
             f"- RunId：`{STATE['run_id']}`",
             f"- 开窗：{STATE['started_utc8']}；收窗：{STATE['finished_utc8']}；用时：{STATE['elapsed_min']} min",
             f"- 结论：**{conclusion}**（verdict={STATE['verdict']}）",
             f"- stop_reason：{STATE.get('stop_reason')}",
             f"- 判据版本：{STATE['criteria_version']}；UART 窗口 {STATE['collect_seconds']} s",
             f"- P3b 位流 SHA-256：{STATE.get('steps', {}).get('S4_pspl_four_actions', {}).get('bit_sha256')}",
             f"- 显示 ELF SHA-256：{STATE.get('steps', {}).get('S5_load_display', {}).get('elf_sha256')}",
             "", "## 判据结果"]
    for c in jd.get("criteria", []):
        lines.append(f"- {c['id']} {c['desc']}：`{'PASS' if c['pass'] else 'FAIL'}` {c.get('detail') or ''}")
    lines += ["", "## 各步"]
    for k, v in STATE.get("steps", {}).items():
        lines.append(f"- {k}：`{v.get('status')}` exit=`{v.get('exit_code')}`")
    lines += ["", "## 回传材料",
              f"- UART 原始日志：`{run / 'S5DISP_uart.log'}`",
              f"- 判据：`{run / 'W3_judgement.json'}`；结果：`{run / 'results_p3b_smoke.json'}`",
              "- 屏幕照片（人工佐证，不参与机器判据）：见 `P3B_SMOKE_PLAN.md` §回传材料",
              "", "## 边界",
              "- `ENABLE=0`；未烧 QSPI；未改线；未 push；未用 `-force`；PL 编程后**未用 `rst -system`**。",
              "- 本窗口结论只覆盖 P3b 位流 + 显示 ELF 的冒烟；**不主张 G3/G4/G5**。"]
    (run / "window_close.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[{now()}] p3b smoke done conclusion={conclusion} stop={STATE.get('stop_reason')} "
          f"elapsed={STATE['elapsed_min']}min", flush=True)
    return 0 if conclusion == "P3B_SMOKE_PASS" else 1


def selftest() -> int:
    """离线判据自测（不碰硬件）：覆盖 J-1..J-7 的正/负例。"""
    def good(**kw) -> str:
        base_obj = {"pass": 1, "fps_cap": 30, "fps_inf": 28, "fps_dis": 60,
                    "latency_ms": 17, "age_ms": 47310, "vdma_err": 0}
        base_obj.update(kw)
        return "S5DISP RESULT=" + json.dumps(base_obj)

    cases: list[tuple[str, list[str], str]] = [
        ("good_720p60", [good()], "PASS"),
        ("no_s5disp_line", ["VTC: init OK", "frame 60 lat 17 ms age 30 ms"], "FAIL"),
        ("json_parse_error", ['S5DISP RESULT={"pass":1,'], "FAIL"),
        ("missing_key", ["S5DISP RESULT=" + json.dumps({"pass": 1, "fps_dis": 60})], "FAIL"),
        ("pass_0", [good(**{"pass": 0})], "FAIL"),
        ("vdma_err_1", [good(vdma_err=1)], "FAIL"),
        ("fps_low_54", [good(fps_dis=54)], "FAIL"),
        ("fps_unit_x10_598", [good(fps_dis=598)], "FAIL"),
        ("age_over_47318", [good(age_ms=47318)], "FAIL"),
        ("latency_0xFFFF", [good(latency_ms=65535)], "FAIL"),
        ("error_token", [good(error=1)], "FAIL"),
        ("timeout_token", [good(timeout=0)], "FAIL"),
        ("lat_boundary_47317", [good(age_ms=47317)], "PASS"),
        ("fps_boundary_55", [good(fps_dis=55)], "PASS"),
    ]
    bad = 0
    for name, lines, expect in cases:
        got = judge(lines)["verdict"]
        ok = got == expect
        bad += 0 if ok else 1
        print(f"[SELFTEST] {'PASS' if ok else 'FAIL'} {name}: expect={expect} got={got}", flush=True)
    print(f"[SELFTEST SUMMARY] cases={len(cases)} failed={bad}")
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="P3b 上屏冒烟窗口执行器（离线 dry-run 可用）")
    ap.add_argument("--run-id", default=DEFAULT_RUN_ID)
    ap.add_argument("--bit", default=str(DEFAULT_BIT))
    ap.add_argument("--elf", default=str(DEFAULT_ELF))
    ap.add_argument("--expect-bit-sha", default="", help="位流 SHA-256（全值或前缀）；空=仅记录")
    ap.add_argument("--expect-elf-sha", default="", help="显示 ELF SHA-256（全值或前缀）；空=用计划基线")
    ap.add_argument("--collect-seconds", type=int, default=COLLECT_DEFAULT_S,
                    help=f"UART 结果窗秒数（>= {COLLECT_MIN_S}）")
    ap.add_argument("--dry-run", action="store_true", help="只打印命令与判据，不碰硬件、不建目录")
    ap.add_argument("--self-test", action="store_true", help="离线判据自测（不碰硬件）")
    args = ap.parse_args()
    if args.collect_seconds < COLLECT_MIN_S:
        ap.error(f"--collect-seconds 必须 >= {COLLECT_MIN_S}（任务硬要求）")
    print(f"[{now()}] p3b smoke start run_id={args.run_id} dry_run={int(args.dry_run)}", flush=True)
    if args.self_test:
        return selftest()
    if args.dry_run:
        return dry_run(args)
    return run_window(args)


if __name__ == "__main__":
    sys.exit(main())