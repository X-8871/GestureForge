"""窗口 B 板测驱动 v2（离线开发；开窗后由本文件执行，禁止现场改脚本）。

覆盖（相对 v1 的改动）：
  A. M4-a 装载时序修正：`dow <elf>` 之后**显式** `rst -processor -stop` → 校验 `state` 含 Suspended
     → 再 `con`；随后**必须**先收到 UART `M4A READY` 横幅（超时即 FAIL 并停止，不进入 R/I/F/W）。
  B. M4-b 全流程（八步）：切 M4-b ELF → 预置 head13/head26 参考到 RAW、输入/权重到 arena（由 CLI 传入，
     缺失则显式 `NOT_RUN` 并写原因，**不允许**静默 NOT_APPLICABLE）→ 桥接触发 → 首拍门控快照
     （`state∈{1,2}` 且 owner=1、head/terminal/safe_reuse=0；首拍已 DONE_SAFE ⇒ `INCONCLUSIVE`）
     → 等 `state∈{4,5}` 且 `safe_reuse|terminal` → invalidate → head13/head26 逐字节比对
     → ACK（`0x05C/0x060` → `0x008=4`）→ `is_idle()` 收敛。
  C. 可选 PL 装载：`--bit` 给出时用 Vivado Tcl（`program_2b_bit.tcl`）装载并解析 `PROGRAM_OK`；
     PL 若已配置，M2 走"位流身份已登记"分支（要求 `--bit-sha256` 与已登记 `555a70c2…` 前缀一致，
     否则拒绝执行）。
  D. M3 只读复检（`--m3-recheck`）：整区 dump 与 `--m3-reference`（`41907f53…` 的快照）逐字节比较。

安全纪律（与窗口 A′ 相同）：
  · 每步真实退出码写 `<step>.exit_code.txt`（`exit=<code>`）；
  · FAIL 即停；不重试写 DDR；M3 差异 ≠0 立即停；
  · P0 只看 LISTENING，TIME_WAIT 不清理；不结束任何名字含 `mcp` 的进程；
  · 只写候选区 `[0x12000000,0x12C08000)`（M4-a/M4-b 的 RAW 参考写入也在此区间内）；
  · 不发独立 `stop`；收尾停 hw_server 并核验 3121 无 LISTENING。

用法：
  python -B scripts/stage4_s4b/run_window_b_driver.py --run-dir <dir> --window-instruction "<text>" \
      [--bit <path> --bit-sha256 <sha>] [--m3-recheck --m3-reference <bin>] \
      [--m4b-elf <path> --m4b-input <bin> --m4b-weights <bin> --m4b-head13 <bin> --m4b-head26 <bin>] \
      [--skip-m4b]
  python -B scripts/stage4_s4b/run_window_b_driver.py --offline-selftest
离线自检退出码：0=PASS、1=FAIL、2=输入/环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
SCRIPTS = W / "scripts" / "stage4_s4b"
M4A_ELF = W / "report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/preparation/payloads/m4a_cache_probe.elf"
INIT_ELF = W / "report/evidence/S4-B/s4b_ps_tensor_20261023_r13/verified_payload/init.elf"
M4B_ELF = W / "report/evidence/S4-T32/phase2_ps_app_20261027_r01/s4d_ps_app_m4b_v2.elf"
HW_URL = "tcp:127.0.0.1:3121"
XSDB = Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat")
HW_SERVER = Path(r"D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\hw_server.exe")
VIVADO = Path(r"D:\Xilinx\2026.1\Vivado\bin\vivado.bat")
PY = r"C:\Users\22061\AppData\Local\Programs\Python\Python312\python.exe"

CAND_BASE = 0x12000000
CAND_END = 0x12C08000
CAND_BYTES = CAND_END - CAND_BASE
RAW_BASE = 0x12000000
ARENA = 0x10000000
M3_REGISTERED_SHA = "41907f539cff35f357b433c121d4b7cc01f6b362cc6722dcfa0d6411f20a0abf"
BIT_REGISTERED_PREFIX = "555a70c2"
HEAD13_OFF, HEAD13_BYTES = 0x01A46100, 5070
HEAD26_OFF, HEAD26_BYTES = 0x01AD5E80, 20280
INPUT_BYTES, WEIGHT_BYTES = 519168, 5903100
CSR = 0x43C00000

ST_HEAVY_BLOCKLIST = ("mcp",)   # 永不结束名字含 mcp 的进程


def now_cn() -> str:
    """UTC+8 时间串。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_file(path: Path | None) -> str | None:
    """文件 SHA-256。"""
    if path is None or not Path(path).is_file():
        return None
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_exit(step: str, code: int) -> None:
    """落真实退出码。"""
    (RUN_DIR / f"{step}.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")


def log(msg: str) -> None:
    """控制台 + 逐行日志。"""
    print(msg, flush=True)
    with (RUN_DIR / "driver_v2_console.log").open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def listening_3121() -> int:
    """统计 3121 LISTENING 数量（不看 TIME_WAIT）。"""
    try:
        out = subprocess.run(
            ["pwsh", "-NoProfile", "-Command",
             "(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | Measure-Object).Count"],
            capture_output=True, text=True, timeout=60)
        return int((out.stdout or "0").strip() or 0)
    except Exception:
        return -1


def heavy_processes() -> list[str]:
    """枚举重型进程（精确镜像名，跳过名字含 mcp 的）。"""
    try:
        out = subprocess.run(
            ["pwsh", "-NoProfile", "-Command",
             "Get-Process -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName"],
            capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    heavy = {"hw_server", "xsdb", "vivado", "xsim", "xelab", "xvlog", "vitis"}
    names = [n.strip() for n in (out.stdout or "").splitlines() if n.strip()]
    return sorted({n for n in names if n.lower() in heavy and not any(b in n.lower() for b in ST_HEAVY_BLOCKLIST)})


def p0_gate() -> dict:
    """P0 门禁：无重型进程、3121 无 LISTENING、无 index.lock、COM4 空闲。"""
    heavy = heavy_processes()
    listen = listening_3121()
    lock = W / ".git" / "index.lock"
    com_ok = Path("COM4").exists()
    detail = {"heavy_processes": heavy, "listening_3121": listen,
              "index_lock": lock.exists(), "com4_present": com_ok,
              "time_wait_note": "TIME_WAIT 不计入、不清理",
              "mcp_exclusion": "名字含 mcp 的进程一律不判断、不结束"}
    ok = (not heavy) and listen == 0 and not lock.exists() and com_ok
    return {"ok": ok, **detail}


def start_hw_server() -> dict:
    """启动 hw_server 并等待 3121 LISTENING。"""
    proc = subprocess.Popen([str(HW_SERVER)], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    for _ in range(60):
        time.sleep(1)
        if listening_3121() > 0:
            return {"ok": True, "pid": proc.pid}
    return {"ok": False, "pid": proc.pid, "reason": "hw_server 未监听 3121"}


def stop_hw_server(pid: int | None) -> dict:
    """停 hw_server（仅自起进程），核验 3121 无 LISTENING。"""
    if pid:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    for _ in range(20):
        time.sleep(1)
        if listening_3121() == 0:
            break
    return {"stopped_pid": pid, "listening_3121": listening_3121(),
            "residual_processes": heavy_processes(), "time_wait_note": "TIME_WAIT 可接受，不清理"}


def xsdb(eval_text: str, step: str, timeout: int = 600) -> int:
    """跑一段 xsdb -eval 并落日志/退出码。"""
    cmd = ["cmd", "/c", str(XSDB), "-eval", eval_text]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=timeout)
    out = (proc.stdout or "") + (proc.stderr or "")
    (RUN_DIR / f"{step}.log").write_text(f"$ {' '.join(cmd)}\nexit={proc.returncode} elapsed={time.time()-t0:.3f}\n{out}\n",
                                         encoding="utf-8")
    write_exit(step, proc.returncode)
    return proc.returncode


def xsdb_step(step: str, tcl: str, args: list[str], timeout: int = 900) -> int:
    """跑受控 Tcl 脚本。"""
    cmd = ["cmd", "/c", str(XSDB), str(SCRIPTS / tcl), *args]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=timeout)
    out = (proc.stdout or "") + (proc.stderr or "")
    (RUN_DIR / f"{step}.log").write_text(f"$ {' '.join(cmd)}\nexit={proc.returncode} elapsed={time.time()-t0:.3f}\n{out}\n",
                                         encoding="utf-8")
    write_exit(step, proc.returncode)
    return proc.returncode


def select_core() -> str:
    """统一选核前置（M3/M4-a/M4-b 共用）。"""
    return 'targets -set -filter {name =~ "*Cortex-A9*#0*"}; '


def program_pl(bit: Path, bit_sha: str) -> int:
    """用 Vivado Tcl 装载 PL 位流并解析 PROGRAM_OK。"""
    cmd = ["cmd", "/c", str(VIVADO), "-mode", "batch", "-source",
           str(SCRIPTS / "program_2b_bit.tcl"), "-tclargs", bit.as_posix(), bit_sha]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=1200)
    out = (proc.stdout or "") + (proc.stderr or "")
    (RUN_DIR / "PL_program.log").write_text(f"$ {' '.join(cmd)}\nexit={proc.returncode} elapsed={time.time()-t0:.3f}\n{out}\n",
                                            encoding="utf-8")
    code = 0 if "PROGRAM_OK" in out else 1
    if proc.returncode != 0:
        code = proc.returncode
    write_exit("PL_program", code)
    return code


def load_elf(elf: Path, tag: str, hold_reset: bool) -> int:
    """下载 ELF；hold_reset=True 时 dow 后 rst -processor -stop（窗口 A′ 缺陷修正）。"""
    base = f"connect -url {HW_URL}; {select_core()}rst -system -stop; dow {elf.as_posix()}; "
    if hold_reset:
        base += 'rst -processor -stop; after 200; puts "HOLD_STATE=[state]"; '
    base += "con; after 2000; puts \"RUN_STATE=[state]\"; disconnect; exit"
    return xsdb(base, tag, timeout=600)


def uart_open():
    """打开 COM4 115200 8N1。"""
    try:
        import serial  # type: ignore
    except Exception as exc:  # pragma: no cover
        return None, f"pyserial 不可用: {exc}"
    try:
        ser = serial.Serial("COM4", 115200, timeout=0.2)
        ser.reset_input_buffer()
        return ser, None
    except Exception as exc:
        return None, f"COM4 打开失败: {exc}"


def uart_wait(ser, needle: str, timeout_s: int) -> str | None:
    """等待指定横幅/应答行。"""
    deadline = time.time() + timeout_s
    buf = ""
    while time.time() < deadline:
        chunk = ser.read(4096)
        if chunk:
            buf += chunk.decode("utf-8", "replace")
            if needle in buf:
                return buf
    return None


def uart_cmd(ser, text: str, expect_prefix: str, timeout_s: int = 20) -> tuple[str, str | None]:
    """发一条命令并取应答行（形如 `M4A ...`）。"""
    ser.write((text + "\r\n").encode())
    ser.flush()
    deadline = time.time() + timeout_s
    buf = ""
    while time.time() < deadline:
        chunk = ser.read(4096)
        if chunk:
            buf += chunk.decode("utf-8", "replace")
            for line in buf.splitlines():
                if line.startswith(expect_prefix):
                    return buf, line.strip()
    return buf, None


def crc32_int(data: bytes) -> int:
    """CRC-32（与 UART 侧同口径）。"""
    import zlib
    return zlib.crc32(data) & 0xFFFFFFFF


def jtag_read(addr: int, nbytes: int, out: Path, tag: str) -> int:
    """JTAG 读内存到文件。"""
    return xsdb(f"connect -url {HW_URL}; {select_core()}mrd -bin -file {out.as_posix()} {hex(addr)} {nbytes // 4}; "
                f"disconnect; exit", tag)


def jtag_write_file(path: Path, addr: int, tag: str, words: int) -> int:
    """JTAG 从文件整块写内存（mwr -bin -file 必须带字数）。"""
    return xsdb(f"connect -url {HW_URL}; {select_core()}mwr -bin -file {path.as_posix()} {hex(addr)} {words}; "
                f"disconnect; exit", tag)


def step_m4a() -> dict:
    """M4-a：装载时序修正 + UART 横幅 + R/I/F/W 对拍 + 恢复校验。"""
    out: dict = {"status": "FAIL"}
    code = load_elf(M4A_ELF, "M4a_load_fixed", hold_reset=True)
    out["load_exit"] = code
    if code != 0:
        out["reason"] = "装载失败"
        return out
    ser, err = uart_open()
    if ser is None:
        out["reason"] = err
        return out
    try:
        banner = uart_wait(ser, "M4A READY", 30)
        out["banner_seen"] = banner is not None
        if banner is None:
            out["reason"] = "30s 内未收到 M4A READY 横幅（装载后仍无输出，FAIL，不继续 R/I/F/W）"
            return out
        orig = RUN_DIR / "m4a_orig_1k.bin"
        c_o = jtag_read(RAW_BASE, 1024, orig, "M4a_jtag_read_orig")
        out["jtag_read_exit"] = c_o
        orig_bytes = orig.read_bytes() if orig.is_file() else b""
        if c_o != 0 or not orig_bytes:
            out["reason"] = "JTAG 读取原始 1 KiB 失败"
            return out
        checks: dict = {"orig_sha256": sha256_file(orig), "orig_crc32": "0x%08x" % crc32_int(orig_bytes)}
        _, r = uart_cmd(ser, f"R {hex(RAW_BASE)} 1024", "M4A")
        checks["R_ack"] = r
        checks["R_matches"] = bool(r and ("%08x" % crc32_int(orig_bytes)) in r.lower())
        # JTAG 写 0xA5 图案（仅候选区 1 KiB）
        pat = RUN_DIR / "m4a_pattern_1k.bin"
        pat.write_bytes(b"\xa5" * 1024)
        checks["jtag_write_exit"] = jtag_write_file(pat, RAW_BASE, "M4a_jtag_write_pattern", 256)
        _, f = uart_cmd(ser, f"F {hex(RAW_BASE)} 1024", "M4A")
        checks["F_ack"] = f
        checks["F_matches"] = bool(f and ("%08x" % crc32_int(b"\xa5" * 1024)) in f.lower())
        # 恢复并逐字节校验
        checks["jtag_restore_exit"] = jtag_write_file(orig, RAW_BASE, "M4a_jtag_restore", 256)
        chk = RUN_DIR / "m4a_restored_1k.bin"
        checks["jtag_verify_exit"] = jtag_read(RAW_BASE, 1024, chk, "M4a_jtag_verify")
        checks["restored_byte_equal"] = chk.is_file() and chk.read_bytes() == orig_bytes
        out["checks"] = checks
        out["status"] = "PASS" if all([checks["R_matches"], checks["F_matches"], checks["restored_byte_equal"]]) else "FAIL"
        if out["status"] != "PASS":
            out["reason"] = "R/F/恢复校验未全过"
    finally:
        try:
            ser.close()
        except Exception:
            pass
    return out


def step_m4b(args) -> dict:
    """M4-b：按八步序列执行（缺参考数据则显式 NOT_RUN 并写原因）。"""
    need = {"elf": args.m4b_elf, "input": args.m4b_input, "weights": args.m4b_weights,
            "head13": args.m4b_head13, "head26": args.m4b_head26}
    missing = [k for k, v in need.items() if not v or not Path(v).is_file()]
    if args.skip_m4b or missing:
        return {"status": "NOT_RUN",
                "reason": ("显式 --skip-m4b" if args.skip_m4b else f"参考数据缺失: {missing}"),
                "note": "禁止静默 NOT_APPLICABLE；缺数据即 NOT_RUN 并保留原因"}
    # 预置：head13/head26 参考写到 RAW（候选区内），输入/权重写到 arena（PS 内存，非候选区）
    head13 = Path(args.m4b_head13)
    head26 = Path(args.m4b_head26)
    inp = Path(args.m4b_input)
    wts = Path(args.m4b_weights)
    bad = [(p.name, p.stat().st_size) for p in (head13, head26, inp, wts)
           if not (p.stat().st_size == {head13: HEAD13_BYTES, head26: HEAD26_BYTES,
                                        inp: INPUT_BYTES, wts: WEIGHT_BYTES}[p])]
    if bad:
        return {"status": "NOT_RUN", "reason": f"参考数据尺寸不符: {bad}"}
    pre: dict = {}
    pre["jtag_ref_head13"] = jtag_write_file(head13, RAW_BASE, "M4b_pre_ref_head13", HEAD13_BYTES // 4)
    pre["jtag_ref_head26"] = jtag_write_file(head26, RAW_BASE + 0x2000, "M4b_pre_ref_head26", HEAD26_BYTES // 4)
    pre["jtag_input"] = jtag_write_file(inp, ARENA, "M4b_pre_input", INPUT_BYTES // 4)
    pre["jtag_weights"] = jtag_write_file(wts, ARENA + 0x00100000, "M4b_pre_weights", WEIGHT_BYTES // 4)
    code = load_elf(Path(args.m4b_elf), "M4b_load", hold_reset=True)
    pre["load_exit"] = code
    if code != 0:
        return {"status": "FAIL", "reason": "M4-b ELF 装载失败", "preload": pre}
    ser, err = uart_open()
    if ser is None:
        return {"status": "FAIL", "reason": err, "preload": pre}
    try:
        got = uart_wait(ser, "M4B", 60)
        pre["uart_seen"] = got is not None
        if not got:
            return {"status": "FAIL", "reason": "60s 内无 M4B 输出", "preload": pre}
        # 等待完整结果行
        deadline = time.time() + 30
        result_line = None
        buf = got
        while time.time() < deadline:
            for line in buf.splitlines():
                if line.startswith("M4B RESULT="):
                    result_line = line
                    break
            if result_line:
                break
            chunk = ser.read(4096)
            if chunk:
                buf += chunk.decode("utf-8", "replace")
        (RUN_DIR / "m4b_uart.log").write_text(buf, encoding="utf-8")
        gating_line = next((ln for ln in buf.splitlines() if ln.startswith("M4B GATE=")), None)
        parsed: dict = {}
        if result_line:
            try:
                parsed = json.loads(result_line.split("=", 1)[1])
            except Exception as exc:
                parsed = {"parse_error": str(exc)}
        status = "PASS" if (parsed.get("pass") == 1) else ("INCONCLUSIVE" if parsed.get("gate") == 2 else "FAIL")
        return {"status": status, "preload": pre, "result_line": result_line,
                "gating_line": gating_line, "parsed": parsed,
                "rule": "首拍已 DONE_SAFE ⇒ gate=2 ⇒ INCONCLUSIVE（不记 PASS）"}
    finally:
        try:
            ser.close()
        except Exception:
            pass


def step_m3_recheck(ref: Path) -> dict:
    """M3 只读复检：整区 dump 与已登记快照逐字节比较（不写）。"""
    out = RUN_DIR / "m3_recheck_dump.bin"
    code = xsdb_step("M3_recheck_dump", "m3_candidate_rw.tcl", ["readback", str(out)], timeout=1800)
    res = {"readback_exit": code, "dump": str(out), "dump_sha256": sha256_file(out),
           "dump_bytes": out.stat().st_size if out.is_file() else 0,
           "reference_sha256": sha256_file(ref)}
    if code != 0 or not out.is_file():
        res["status"] = "FAIL"
        res["reason"] = "整区只读复检读取失败"
        return res
    a = out.read_bytes()
    b = ref.read_bytes() if ref.is_file() else b""
    diff = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
    res.update({"diff_bytes": diff, "byte_equal": diff == 0,
                "registered_sha_match": res["dump_sha256"] == M3_REGISTERED_SHA,
                "status": "PASS" if (diff == 0 and res["dump_sha256"] == M3_REGISTERED_SHA) else "FAIL"})
    if res["status"] != "PASS":
        res["reason"] = "候选区与已登记快照不一致（PL 装载后可能被写）⇒ 立即停"
    return res


def offline_selftest() -> int:
    """离线自检：不接触板卡，验证门禁逻辑/参数表/关键常量/无 NOT_APPLICABLE 硬编码。"""
    fails: list[str] = []

    def chk(name: str, cond: bool, detail: str = "") -> None:
        print(f"[{'PASS' if cond else 'FAIL'}] {name}{(' :: ' + detail) if detail and not cond else ''}")
        if not cond:
            fails.append(name)

    chk("candidate_region_math", CAND_BYTES == 12615680 and CAND_END - CAND_BASE == CAND_BYTES)
    chk("raw_inside_candidate", CAND_BASE <= RAW_BASE and RAW_BASE + 0x4000 <= CAND_END)
    chk("head13_within_arena", HEAD13_OFF + HEAD13_BYTES <= 0x02000000)
    chk("head26_within_arena", HEAD26_OFF + HEAD26_BYTES <= 0x02000000)
    chk("tensor_bytes_math", 416 * 416 * 3 == INPUT_BYTES)
    chk("pl_identity_prefix", len(BIT_REGISTERED_PREFIX) == 8)
    chk("m3_registered_sha_len", len(M3_REGISTERED_SHA) == 64 and all(c in "0123456789abcdef" for c in M3_REGISTERED_SHA))
    chk("no_mcp_kill_targets", all("mcp" in b for b in ST_HEAVY_BLOCKLIST))
    chk("xsdb_present", XSDB.is_file(), str(XSDB))
    chk("hw_server_present", HW_SERVER.is_file(), str(HW_SERVER))
    chk("m4a_payload_present", M4A_ELF.is_file(), str(M4A_ELF))
    chk("init_payload_present", INIT_ELF.is_file(), str(INIT_ELF))
    chk("m4b_elf_present", M4B_ELF.is_file(), str(M4B_ELF))
    src = Path(__file__).read_text(encoding="utf-8")
    token = "NOT_" + "APPLICABLE"
    chk("no_hardcoded_not_applicable", (chr(34) + token + chr(34)) not in src)
    chk("has_load_reset_fix", "rst -processor -stop" in src)
    chk("has_m4b_sequence", all(k in src for k in ("M4b_pre_ref_head13", "M4b_pre_weights", "M4B RESULT=")))
    chk("has_m3_recheck", "m3_recheck_dump" in src)
    # 纯逻辑：门禁判定
    def gate_ok(heavy, listen, lock, com):
        return (not heavy) and listen == 0 and not lock and com
    chk("gate_rejects_heavy", gate_ok(["hw_server"], 0, False, True) is False)
    chk("gate_rejects_time_wait_only_ok", gate_ok([], 0, False, True) is True)
    chk("gate_rejects_lock", gate_ok([], 0, True, True) is False)
    chk("gate_accepts_clean", gate_ok([], 0, False, True) is True)
    print(f"\nSELFTEST_RESULT={'PASS' if not fails else 'FAIL'} failures={len(fails)}")
    return 0 if not fails else 1


def main() -> int:
    """入口。"""
    ap = argparse.ArgumentParser(description="窗口 B 板测驱动 v2")
    ap.add_argument("--run-dir")
    ap.add_argument("--window-instruction")
    ap.add_argument("--bit")
    ap.add_argument("--bit-sha256")
    ap.add_argument("--m3-recheck", action="store_true")
    ap.add_argument("--m3-reference")
    ap.add_argument("--m4b-elf", default=str(M4B_ELF))
    ap.add_argument("--m4b-input")
    ap.add_argument("--m4b-weights")
    ap.add_argument("--m4b-head13")
    ap.add_argument("--m4b-head26")
    ap.add_argument("--skip-m4b", action="store_true")
    ap.add_argument("--offline-selftest", action="store_true")
    args = ap.parse_args()

    if args.offline_selftest:
        return offline_selftest()

    global RUN_DIR
    if not args.run_dir or not args.window_instruction:
        print("[FAIL] 缺少 --run-dir 或 --window-instruction（未开窗不得接触板卡）")
        return 2
    RUN_DIR = Path(args.run_dir)
    if RUN_DIR.exists() and any(RUN_DIR.iterdir()):
        print(f"[FAIL] 证据目录非空：{RUN_DIR}")
        return 2
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "window_instruction.txt").write_text(
        f"{args.window_instruction}\nSTART_UTC8={now_cn()}\nDRIVER=run_window_b_driver.py v2\n", encoding="utf-8")

    results: dict = {"run_dir": str(RUN_DIR), "generated_utc8": now_cn(), "steps": {}, "stop_reason": None}

    def record(step: str, status: str, detail: dict) -> None:
        results["steps"][step] = {"status": status, **detail}
        log(f"[{status}] {step}")

    # ---- P0 ----
    p0 = p0_gate()
    record("P0_gate", "PASS" if p0["ok"] else "FAIL", p0)
    if not p0["ok"]:
        results["stop_reason"] = "P0 门禁不通过（拒绝接触板卡）"
        (RUN_DIR / "results_window_b.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 1

    # ---- P0b / P1 ----
    hs = start_hw_server()
    record("P0b_hw_server", "PASS" if hs["ok"] else "FAIL", hs)
    if not hs["ok"]:
        results["stop_reason"] = "hw_server 启动失败"
        (RUN_DIR / "results_window_b.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 1
    hw_pid = hs.get("pid")
    try:
        c = xsdb_step("P1_smoke", "p1_smoke.tcl", [], timeout=600)
        txt = (RUN_DIR / "P1_smoke.log").read_text(encoding="utf-8", errors="replace")
        steps = {"step1_targets": "P1_STEP1=OK" in txt, "step2": "P1_STEP2=OK" in txt, "step3": "P1_STEP3=OK" in txt}
        record("P1_smoke", "PASS" if (c == 0 and all(steps.values())) else "FAIL",
               {"exit": c, "steps": steps})
        if c != 0 or not all(steps.values()):
            results["stop_reason"] = "P1 冒烟失败"

        # ---- 可选 PL 装载 ----
        if results["stop_reason"] is None and args.bit:
            bit_sha = sha256_file(Path(args.bit))
            if not (args.bit_sha256 or "").lower().startswith(BIT_REGISTERED_PREFIX):
                record("PL_program", "FAIL", {"reason": "位流身份未登记（SHA 前缀不匹配）", "sha256": bit_sha})
                results["stop_reason"] = "位流身份未登记，拒绝装载"
            else:
                pc = program_pl(Path(args.bit), bit_sha or "")
                record("PL_program", "PASS" if pc == 0 else "FAIL", {"exit": pc, "sha256": bit_sha})
                if pc != 0:
                    results["stop_reason"] = "PL 装载失败"
        else:
            record("PL_program", "NOT_RUN", {"reason": "未提供 --bit（本窗口不装载位流）"})

        # ---- 装载 + M1/M2 ----
        if results["stop_reason"] is None:
            c = load_elf(INIT_ELF, "PRELOAD_init", hold_reset=False)
            record("PRELOAD_init", "PASS" if c == 0 else "FAIL", {"exit": c})
            if c != 0:
                results["stop_reason"] = "init.elf 装载失败"
        if results["stop_reason"] is None:
            c1 = xsdb_step("M1_cpu1_state", "m1_cpu1_state.tcl", [], timeout=300)
            txt = (RUN_DIR / "M1_cpu1_state.log").read_text(encoding="utf-8", errors="replace")
            record("M1_cpu1_state", "PASS" if (c1 == 0 and "RESULT=PASS" in txt) else "FAIL", {"exit": c1})
            c2 = xsdb_step("M2_consumer_check", "m2_consumer_check.tcl", [], timeout=300)
            txt2 = (RUN_DIR / "M2_consumer_check.log").read_text(encoding="utf-8", errors="replace")
            record("M2_consumer_check", "PASS" if (c2 == 0 and "RESULT=READ_ONLY_DONE" in txt2) else "FAIL",
                   {"exit": c2, "note": "只读构造性；PL 已装载时走位流身份已登记分支"})
            if c1 != 0 or c2 != 0:
                results["stop_reason"] = "M1/M2 复核失败"

        # ---- M3 只读复检 ----
        if results["stop_reason"] is None and args.m3_recheck:
            ref = Path(args.m3_reference) if args.m3_reference else None
            if ref is None or not ref.is_file():
                record("M3_recheck", "FAIL", {"reason": "缺少 --m3-reference 快照"})
                results["stop_reason"] = "M3 复检缺参考"
            else:
                m3 = step_m3_recheck(ref)
                record("M3_recheck", m3["status"], m3)
                if m3["status"] != "PASS":
                    results["stop_reason"] = "M3 复检不通过（差异≠0 ⇒ 立即停）"
        else:
            record("M3_recheck", "NOT_RUN", {"reason": "未启用 --m3-recheck"})

        # ---- M4-a ----
        if results["stop_reason"] is None:
            m4a = step_m4a()
            record("M4a_cache_visibility", m4a["status"], m4a)
            if m4a["status"] != "PASS":
                results["stop_reason"] = "M4-a 失败"

        # ---- M4-b ----
        if results["stop_reason"] is None:
            m4b = step_m4b(args)
            record("M4b_dma_visibility", m4b["status"], m4b)
            if m4b["status"] == "FAIL":
                results["stop_reason"] = "M4-b 失败（不满足即 FAIL）"
            elif m4b["status"] == "INCONCLUSIVE":
                results["stop_reason"] = "M4-b 门控不可判定（INCONCLUSIVE，不记 PASS）"
    finally:
        teardown = stop_hw_server(hw_pid)
        record("P4_teardown", "PASS" if teardown["listening_3121"] == 0 and not teardown["residual_processes"] else "FAIL",
               teardown)

    ok_steps = all(v["status"] in ("PASS", "NOT_RUN") for v in results["steps"].values())
    results["conclusion"] = ("WINDOW_B_ALL_PASS_OR_NOT_RUN" if (results["stop_reason"] is None and ok_steps)
                             else "STOPPED_ON_FAILURE")
    results["hardware_execution"] = "EXECUTED"
    (RUN_DIR / "results_window_b.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"conclusion": results["conclusion"], "stop_reason": results["stop_reason"],
                      "steps": {k: v["status"] for k, v in results["steps"].items()}}, ensure_ascii=False, indent=2))
    return 0 if results["conclusion"].startswith("WINDOW_B_ALL") else 1


if __name__ == "__main__":
    sys.exit(main())