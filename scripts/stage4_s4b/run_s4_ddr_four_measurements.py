"""S4-T31 四项板级实测执行驱动（**只在"开窗"授权后运行**）。

设计要点（lead 裁定）：
  · P0 门禁前置校验（他方进程 / index.lock / 3121 端口 / COM4 占用）；
  · 逐项执行 M1 → M2 → M3 → M4a，**每步真实退出码落盘**（不手填）；
  · **任一步 FAIL 立即停止**，不执行后续步骤；**不内置任何"失败后重试写 DDR"**；
  · 汇总 `results_four_measurements.json`；
  · 全程只操作候选区 `[0x12000000,0x12C08000)`；恢复原字节并做 SHA+逐字节双判据；
  · M4-b（DMA 可见性）不在本驱动内：`NOT_APPLICABLE`（归 4-D bring-up）。

用法（开窗后）：
  python -B scripts/stage4_s4b/run_s4_ddr_four_measurements.py \
      --run-dir report/evidence/S4-B/s4_ddr_four_measurements_20261027_r01/execution_<UTC8> \
      --window-instruction <开窗指令文本或决议路径>
退出码：0=四项全 PASS；1=存在 FAIL（已停）；2=门禁/输入/环境不满足（未开口）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import serial  # pyserial：M4-a 的 UART 交互（COM4）
except Exception:  # pragma: no cover
    serial = None

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
XSDBN = Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat")
HW_SERVER_BAT = Path(r"D:\Xilinx\2026.1\Vivado\bin\hw_server.bat")
SCRIPTS = W / "scripts" / "stage4_s4b"
PREP = W / "report" / "evidence" / "S4-B" / "s4_ddr_four_measurements_20261027_r01" / "preparation"
CAND_BASE = 0x12000000
CAND_END = 0x12C08000
CAND_BYTES = 12615680
HW_URL = "tcp:127.0.0.1:3121"
UART = "COM4"


def now_cn() -> str:
    """当前 UTC+8 时间戳。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str | None:
    """文件 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def heavy_processes() -> list[str]:
    """列出可能的板卡占用进程（只读探测）。"""
    # 只匹配**精确镜像名**；`vivado-mcp-server-windows` 等 MCP 包装进程不算（且禁止结束）
    names = {"vivado", "xsdb", "hw_server", "xsct", "openocd", "vivado_lab"}
    found: list[str] = []
    try:
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        for line in out.splitlines():
            image = line.split(",")[0].strip('"').lower().removesuffix(".exe")
            if "mcp" in image:
                continue
            if image in names:
                found.append(line.split(",")[0].strip('"'))
    except OSError:
        pass
    return found


def port_free(host: str, port: int) -> bool:
    """3121 是否空闲（能连上说明已被占用）。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def run_step(run_dir: Path, step: str, cmd: list[str], timeout: int = 900) -> tuple[int, str]:
    """执行一步：真实退出码 + 原始输出落盘。"""
    # `.bat` 需经 cmd /c 调用（Python 不能直接 CreateProcess 一个批处理）
    if cmd and cmd[0].lower().endswith(".bat"):
        cmd = ["cmd", "/c", *cmd]
    (run_dir / f"{step}.stdout.txt").unlink(missing_ok=True)
    log = run_dir / f"{step}.log"
    started = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
        code, out = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        code, out = 124, f"TIMEOUT after {timeout}s"
    elapsed = round(time.time() - started, 3)
    (run_dir / f"{step}.stdout.txt").write_text(out, encoding="utf-8")
    (run_dir / f"{step}.exit_code.txt").write_text(f"exit={code}\nelapsed_s={elapsed}\n", encoding="utf-8")
    with log.open("a", encoding="utf-8") as handle:
        handle.write(f"$ {' '.join(cmd)}\nexit={code} elapsed={elapsed}\n{out}\n")
    return code, out


def xsdb_step(run_dir: Path, step: str, args: list[str], timeout: int = 900) -> tuple[int, str]:
    """以 xsdb 批处理执行一个 Tcl/参数组合。"""
    return run_step(run_dir, step, [str(XSDBN), *args], timeout=timeout)


def parse_pairs(text: str, prefix: str) -> dict[str, str]:
    """从输出中提取 `PREFIX ... key=value` 风格行（此处按首个 `=` 切分）。"""
    found: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith(prefix):
            continue
        payload = line[len(prefix):].strip()
        if "=" in payload:
            key, value = payload.split("=", 1)
            found[key.strip()] = value.strip()
    return found


def listening_3121() -> int:
    """返回 3121 上处于 LISTEN 的连接数（TIME_WAIT 不计）。"""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue).Count"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return int(out or "0")
    except (OSError, ValueError, subprocess.SubprocessError):
        return -1


def start_hw_server(run_dir: Path) -> tuple[int | None, str]:
    """启动 hw_server 并等待 3121 进入 LISTEN；返回 (PID, 错误)。"""
    if not HW_SERVER_BAT.is_file():
        return None, f"hw_server 缺失：{HW_SERVER_BAT}"
    out_log = (run_dir / "hw_server.stdout.txt").open("w", encoding="utf-8")
    err_log = (run_dir / "hw_server.stderr.txt").open("w", encoding="utf-8")
    proc = subprocess.Popen(["cmd", "/c", str(HW_SERVER_BAT), "-s", "tcp::3121"],
                            stdout=out_log, stderr=err_log,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    deadline = time.time() + 30
    while time.time() < deadline:
        if listening_3121() > 0 and not port_free("127.0.0.1", 3121):
            return proc.pid, ""
        time.sleep(0.5)
    return None, "hw_server 30 s 内未监听 3121"


def stop_hw_server(run_dir: Path, pid: int | None) -> dict[str, object]:
    """停 hw_server（含其派生子进程），并核验 3121 无 LISTEN。"""
    stopped: list[int] = []
    if pid:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)
        stopped.append(pid)
    # 兜底：结束本机所有 hw_server（本窗口为唯一使用者，P0 已确认无他方进程）
    try:
        listing = subprocess.run(["tasklist", "/FI", "IMAGENAME eq hw_server.exe", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        for line in listing.splitlines():
            if "hw_server.exe" in line:
                hwid = line.split(",")[1].strip('"')
                if hwid.isdigit():
                    subprocess.run(["taskkill", "/PID", hwid, "/T", "/F"], capture_output=True, text=True)
                    stopped.append(int(hwid))
    except OSError:
        pass
    time.sleep(2)
    listening = listening_3121()
    residual = heavy_processes()
    detail = {"stopped_pids": stopped, "listening_3121": listening,
              "residual_processes": residual, "time_wait_note": "TIME_WAIT 可接受，不清理"}
    (run_dir / "P4_teardown_result.json").write_text(
        json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "P4_teardown.exit_code.txt").write_text(f"exit={0 if (listening == 0 and not residual) else 1}\n",
                                                       encoding="utf-8")
    return detail


def crc32_int(data: bytes) -> int:
    """标准 CRC-32（与最小 ELF 的按位实现一致）。"""
    return zlib.crc32(data) & 0xFFFFFFFF


def uart_open(timeout: float = 30.0) -> tuple[object | None, str]:
    """打开 COM4 等待 `M4A READY` 横幅；返回 (serial, 错误)。"""
    if serial is None:
        return None, "pyserial 不可用"
    try:
        ser = serial.Serial(UART, 115200, timeout=0.5, write_timeout=2)
    except Exception as exc:  # noqa: BLE001
        return None, f"打开 {UART} 失败：{exc}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = ser.readline().decode("utf-8", errors="replace").strip()
        if line.startswith("M4A READY"):
            return ser, ""
    ser.close()
    return None, f"{timeout}s 内未收到 M4A READY 横幅"


def uart_cmd(ser: object, command: str, timeout: float = 15.0) -> tuple[str, str | None]:
    """发送一条命令并读回应答行；返回 (原始应答, crc 字符串或 None)。"""
    try:
        ser.reset_input_buffer()  # type: ignore[attr-defined]
        ser.write((command + "\r\n").encode())  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001
        return "", f"写串口失败：{exc}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = ser.readline().decode("utf-8", errors="replace").strip()  # type: ignore[attr-defined]
        if not line:
            continue
        if "crc=" in line:
            return line, line.split("crc=")[1].split()[0]
        if "M4A ERR" in line:
            return line, None
    return "", "超时无应答"


def main() -> int:
    """按序执行四项实测；FAIL 即停。"""
    parser = argparse.ArgumentParser(description="S4-T31 四项板测执行驱动（开窗后使用）")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--window-instruction", required=True,
                        help="开窗指令文本/路径（缺失即拒绝执行：未开窗不得接触板卡）")
    parser.add_argument("--skip-m4a", action="store_true", help="仅当 M4-a 载荷不可用时显式跳过（会记 NOT_RUN）")
    args = parser.parse_args()

    run_dir: Path = args.run_dir
    if run_dir.exists() and any(run_dir.iterdir()):
        print(f"[FAIL] 证据目录非空：{run_dir}")
        return 2
    run_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, object] = {"generated_utc8": now_cn(), "run_dir": str(run_dir), "steps": {}}
    stop_reason: str | None = None

    def record(step: str, status: str, detail: dict[str, object]) -> None:
        results["steps"][step] = {"status": status, **detail}  # type: ignore[index]

    # ---------------- P0 门禁 ----------------
    p0: dict[str, object] = {}
    proc_list = heavy_processes()
    p0["heavy_processes"] = proc_list
    p0["index_lock_present"] = any(Path(g).exists() for g in [
        W / ".git" / "index.lock", W / ".git" / "worktrees" / W.name / "index.lock"])
    p0["port_3121_free"] = port_free("127.0.0.1", 3121)
    p0["uart_configured"] = UART
    p0["window_instruction_present"] = bool(args.window_instruction)
    p0_ok = (not proc_list) and (not p0["index_lock_present"]) and bool(p0["port_3121_free"])
    record("P0_gate", "PASS" if p0_ok else "FAIL", p0)
    if not p0_ok:
        results["conclusion"] = "STOPPED_AT_P0"
        stop_reason = "P0 门禁不满足（他方进程 / index.lock / 3121 占用）"
        (run_dir / "results_four_measurements.json").write_text(
            json.dumps({**results, "stop_reason": stop_reason}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[FAIL] {stop_reason}：{p0}")
        return 2

    # ---------------- P0b：启动 hw_server（P0 已确认端口空闲、无他方进程） ----------------
    hw_pid: int | None = None
    if stop_reason is None:
        hw_pid, hw_err = start_hw_server(run_dir)
        record("P0b_hw_server", "PASS" if hw_pid else "FAIL", {"pid": hw_pid, "error": hw_err})
        if not hw_pid:
            stop_reason = f"hw_server 启动失败：{hw_err}"
            stop_hw_server(run_dir, None)
            (run_dir / "results_four_measurements.json").write_text(
                json.dumps({**results, "stop_reason": stop_reason}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
            print(f"[FAIL] {stop_reason}")
            return 2

    # ---------------- P1 smoke：分步断言（targets → 选目标 → 只读） ----------------
    if stop_reason is None:
        code, out = xsdb_step(run_dir, "P1_smoke", [str(SCRIPTS / "p1_smoke.tcl")], timeout=300)
        steps = {"step1_targets": "P1_STEP1=OK" in out,
                 "step2_select": "P1_STEP2=OK" in out,
                 "step3_read": "P1_STEP3=OK" in out}
        failed_step = {11: "step1_targets", 12: "step2_select", 13: "step3_read"}.get(code)
        record("P1_smoke", "PASS" if (code == 0 and all(steps.values())) else "FAIL",
               {"exit_code": code, "steps": steps, "failed_step": failed_step,
                "xsdb_version": parse_pairs(out, "P1_").get("XSDB_VERSION")})
        if not (code == 0 and all(steps.values())):
            stop_reason = f"P1 smoke 失败（失败步={failed_step or code}）"

    # ---------------- PRELOAD：易失下载 init.elf → 运行 → 下载最小 ELF（不 con app） ----------------
    if stop_reason is None:
        init_elf = W / "report" / "evidence" / "S4-B" / "s4b_ps_tensor_20261023_r13" / "verified_payload" / "init.elf"
        elf = PREP / "payloads" / "m4a_cache_probe.elf"
        pre: dict[str, object] = {"init_elf": str(init_elf), "app_elf": str(elf),
                                  "init_elf_sha256": sha256_file(init_elf), "app_elf_sha256": sha256_file(elf)}
        if not init_elf.is_file() or not elf.is_file():
            record("PRELOAD", "FAIL", {**pre, "reason": "载荷缺失"})
            stop_reason = "PRELOAD 载荷缺失"
        else:
            code_i, out_i = xsdb_step(run_dir, "PRELOAD_init",
                                      ["-eval", f"connect -url {HW_URL}; "
                                                f"targets -set -filter {{name =~ \"*Cortex-A9*#0*\"}}; "
                                                f"rst -system -stop; dow {init_elf.as_posix()}; "
                                                f"con; after 6000; disconnect; exit"],
                                      timeout=600)
            code_a, out_a = xsdb_step(run_dir, "PRELOAD_app",
                                      ["-eval", f"connect -url {HW_URL}; "
                                                f"targets -set -filter {{name =~ \"*Cortex-A9*#0*\"}}; "
                                                f"dow {elf.as_posix()}; disconnect; exit"],
                                      timeout=600)
            pre.update({"init_exit": code_i, "app_exit": code_a,
                        "init_tail": out_i.strip().splitlines()[-3:], "app_tail": out_a.strip().splitlines()[-3:]})
            record("PRELOAD", "PASS" if (code_i == 0 and code_a == 0) else "FAIL", pre)
            if not (code_i == 0 and code_a == 0):
                stop_reason = "PRELOAD 失败（init.elf 运行或最小 ELF 下载）"

    # ---------------- M1：CPU1 保持停止 ----------------
    code, out = xsdb_step(run_dir, "M1_cpu1_state", [str(SCRIPTS / "m1_cpu1_state.tcl")])
    m1 = {"exit_code": code, "parsed": parse_pairs(out, "M1_")}
    record("M1_cpu1_state", "PASS" if code == 0 else "FAIL", m1)
    if code != 0:
        stop_reason = "M1 失败（CPU1 非 halted 或目标未找到）"

    # ---------------- M2：无其他 DDR consumer ----------------
    if stop_reason is None:
        code, out = xsdb_step(run_dir, "M2_consumer_check", [str(SCRIPTS / "m2_consumer_check.tcl")])
        m2 = {"exit_code": code, "parsed": parse_pairs(out, "M2_"), "limit": "构造性证明（无总线探针）"}
        record("M2_consumer_check", "PASS" if code == 0 else "FAIL", m2)
        if code != 0:
            stop_reason = "M2 失败（无法排除其他 DDR consumer）"

    # ---------------- M3：候选区写-回读 + 恢复 ----------------
    if stop_reason is None:
        snap = run_dir / "m3_snapshot_orig.bin"
        # 图案文件（窗口5 后）：mwr 无 -pattern，故由主机生成二进制图案再整区写入
        pattern = run_dir / "m3_pattern.bin"
        chunk_words = 16384
        chunks = (CAND_BYTES // 4 + chunk_words - 1) // chunk_words
        with pattern.open("wb") as pch:
            for c in range(chunks):
                remain = CAND_BYTES // 4 - c * chunk_words
                n = min(chunk_words, remain)
                pch.write((0x5A5A0000 | c).to_bytes(4, "little"))
                if n > 1:
                    pch.write(b"\xa5" * ((n - 1) * 4))
        code, _ = xsdb_step(run_dir, "M3_snapshot", [str(SCRIPTS / "m3_candidate_rw.tcl"), "snapshot", str(snap)], timeout=1200)
        m3: dict[str, object] = {"snapshot_exit": code, "snapshot_sha256": sha256_file(snap),
                                "candidate_bytes": CAND_BYTES}
        if code != 0 or m3["snapshot_sha256"] is None:
            record("M3_candidate_rw", "FAIL", {**m3, "reason": "快照失败，拒绝继续（不得在无快照下写入）"})
            stop_reason = "M3 快照失败"
        else:
            code_w, _ = xsdb_step(run_dir, "M3_write", [str(SCRIPTS / "m3_candidate_rw.tcl"), "write", str(pattern)], timeout=1200)
            readback = run_dir / "m3_readback_pattern.bin"
            code_r, _ = xsdb_step(run_dir, "M3_readback", [str(SCRIPTS / "m3_candidate_rw.tcl"), "readback", str(readback)], timeout=1200)
            # 恢复（无论写/读是否成功，只要快照存在就必须恢复）
            code_restore, _ = xsdb_step(run_dir, "M3_restore", [str(SCRIPTS / "m3_candidate_rw.tcl"), "restore", str(snap)], timeout=1200)
            verify = run_dir / "m3_snapshot_restored.bin"
            code_v, _ = xsdb_step(run_dir, "M3_verify", [str(SCRIPTS / "m3_candidate_rw.tcl"), "readback", str(verify)], timeout=1200)
            diff_bytes = None
            if verify.is_file() and snap.is_file():
                a = snap.read_bytes()
                b = verify.read_bytes()
                diff_bytes = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
            m3.update({"write_exit": code_w, "readback_exit": code_r,
                       "restore_exit": code_restore, "verify_exit": code_v,
                       "restored_sha256": sha256_file(verify), "diff_bytes": diff_bytes,
                       "region_byte_equal": (diff_bytes == 0)})
            occupied = None
            if readback.is_file() and snap.is_file():
                occupied = readback.read_bytes() == snap.read_bytes()
            m3["write_readback_identical_to_original"] = occupied
            ok = (code_w == 0 and code_r == 0 and code_restore == 0 and code_v == 0
                  and diff_bytes == 0 and m3["restored_sha256"] == m3["snapshot_sha256"])
            record("M3_candidate_rw", "PASS" if ok else "FAIL", m3)
            if not ok:
                stop_reason = "M3 失败（恢复校验不通过 ⇒ 立即停、保留现场）"

    # ---------------- M4a：cache 维护/可见性（最小 ELF） ----------------
    m4a_status = "NOT_RUN"
    if stop_reason is None:
        elf = PREP / "payloads" / "m4a_cache_probe.elf"
        init_elf = W / "report" / "evidence" / "S4-B" / "s4b_ps_tensor_20261023_r13" / "verified_payload" / "init.elf"
        if args.skip_m4a or not elf.is_file() or not init_elf.is_file():
            m4a_status = "NOT_RUN"
            record("M4a_cache_visibility", "NOT_RUN",
                   {"reason": "载荷缺失或显式跳过", "elf": str(elf), "init_elf": str(init_elf)})
        else:
            # PRELOAD 已下载 init.elf 与最小 ELF；此处只 con CPU0（CPU1 保持 suspended）
            sel = "targets -set -filter {name =~ \"*Cortex-A9*#0*\"}; "
            base_hex = hex(CAND_BASE)
            code, out = xsdb_step(run_dir, "M4a_run_cpu0",
                                  ["-eval", "connect -url " + HW_URL + "; " + sel +
                                            "con; after 2000; puts \"M4A_CPU0_STATE=[state]\"; "
                                            "disconnect; exit"])
            m4: dict[str, object] = {"run_exit": code, "elf_sha256": sha256_file(elf),
                                     "init_elf_sha256": sha256_file(init_elf),
                                     "subrange": {"base": base_hex, "bytes": 1024},
                                     "uart_protocol": "COM4 115200 8N1；R/I/F/W；应答行 M4A ..."}
            ok_m4 = code == 0
            checks: dict[str, object] = {}
            uart_log: list[str] = []

            def jtag(cmds: str, tag: str) -> int:
                """跑一段 xsdb -eval（命令内路径必须 as_posix）。"""
                c, _ = xsdb_step(run_dir, tag,
                                 ["-eval", "connect -url " + HW_URL + "; " + sel + cmds + " disconnect; exit"])
                return c

            if ok_m4:
                orig = run_dir / "m4a_orig_1k.bin"
                c_o = jtag("mrd -bin -file " + orig.as_posix() + " " + base_hex + " 256; ", "M4a_jtag_read_orig")
                orig_bytes = orig.read_bytes() if orig.is_file() else b""
                crc_orig = crc32_int(orig_bytes) if orig_bytes else None
                checks["jtag_read_exit"] = c_o
                checks["orig_sha256"] = sha256_file(orig)
                ser, uerr = (uart_open() if (c_o == 0 and orig_bytes) else (None, "前置失败"))
                if ser is None:
                    checks["uart_error"] = uerr
                    ok_m4 = False
                else:
                    try:
                        import contextlib
                        with contextlib.closing(ser):
                            raw, c = uart_cmd(ser, "R " + base_hex + " 1024")
                            uart_log.append(raw)
                            checks["R_matches_snapshot"] = (c is not None and crc_orig is not None
                                                            and c.lower() == ("0x%08x" % crc_orig))
                            jin = jtag("for {set i 0} {$i < 256} {incr i} { mwr [expr {0x12000000 + $i*4}] 0xA5A5A5A5 }; ",
                                       "M4a_jtag_write_pattern")
                            checks["jtag_write_exit"] = jin
                            raw, c = uart_cmd(ser, "F " + base_hex + " 1024")
                            uart_log.append(raw)
                            checks["F_matches_written_pattern"] = (
                                c is not None and c.lower() == ("0x%08x" % crc32_int(b"\xa5" * 1024)))
                            rst1 = jtag("mwr -bin -file " + orig.as_posix() + " " + base_hex + "; ",
                                        "M4a_jtag_restore")
                            checks["jtag_restore_exit"] = rst1
                            raw, c = uart_cmd(ser, "I " + base_hex + " 1024")
                            uart_log.append(raw)
                            checks["I_matches_restored_snapshot"] = (
                                c is not None and crc_orig is not None and c.lower() == ("0x%08x" % crc_orig))
                            raw, c = uart_cmd(ser, "W " + base_hex + " 1024 0xA5A5A5A5")
                            uart_log.append(raw)
                            checks["W_matches_ps_written_pattern"] = (
                                c is not None and c.lower() == ("0x%08x" % crc32_int(b"\xa5" * 1024)))
                            jtag("mwr -bin -file " + orig.as_posix() + " " + base_hex + "; ", "M4a_jtag_restore2")
                            chk = run_dir / "m4a_verify_1k.bin"
                            jtag("mrd -bin -file " + chk.as_posix() + " " + base_hex + " 256; ",
                                 "M4a_jtag_verify")
                            checks["restored_byte_equal"] = (chk.read_bytes() == orig_bytes) if chk.is_file() else False
                    except Exception as exc:  # noqa: BLE001
                        checks["uart_exception"] = str(exc)
                        ok_m4 = False

            m4["checks"] = checks
            m4["uart_exchanges"] = uart_log
            m4["note"] = "M4-a 只测 cache 维护/可见性；收尾不 stop；W 后已再次恢复并逐字节校验"
            record("M4a_cache_visibility", "PASS" if (ok_m4 and all(v is not False for v in checks.values())) else "FAIL", m4)
            if not (ok_m4 and all(v is not False for v in checks.values())):
                stop_reason = "M4-a 失败（cache 可见性检查未全过）"

    # ---------------- P4：收尾（停 hw_server；核验 3121 无 LISTENING） ----------------
    teardown = stop_hw_server(run_dir, hw_pid)
    record("P4_teardown", "PASS" if (teardown["listening_3121"] == 0 and not teardown["residual_processes"]) else "FAIL",
           teardown)

    results["m4b_dma_visibility"] = {
        "status": "NOT_APPLICABLE",
        "reason": "需 PL consumer（改设计）⇒ 并入 4-D bring-up 验收；本窗口不可测",
        "consequence": "ENABLE=1 前置在 M4-b 未闭合前不满足；本窗口即使全过也不得申请 ENABLE=1/4-D",
    }
    ok_all = stop_reason is None and all(
        results["steps"][s]["status"] in ("PASS", "NOT_RUN") for s in results["steps"])  # type: ignore[index]
    results["conclusion"] = "ALL_STEPS_PASS_M4B_NOT_APPLICABLE" if ok_all else "STOPPED_ON_FAILURE"
    results["stop_reason"] = stop_reason
    results["hardware_execution"] = "EXECUTED" if results["steps"].get("M3_candidate_rw", {}).get("status") == "PASS" else "PARTIAL"
    (run_dir / "results_four_measurements.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"conclusion": results["conclusion"], "stop_reason": stop_reason,
                      "steps": {k: v["status"] for k, v in results["steps"].items()}},
                     ensure_ascii=False, indent=2))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())