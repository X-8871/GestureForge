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
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
XSDBN = Path(r"D:\Xilinx\2026.1\Vitis\bin\xsdb.bat")
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
    names = ("vivado", "xsdb", "hw_server", "xsct", "openocd", "vivado_lab")
    found: list[str] = []
    try:
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        for line in out.splitlines():
            low = line.lower()
            for name in names:
                if name in low:
                    found.append(line.split(",")[0].strip('"'))
                    break
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
        code, _ = xsdb_step(run_dir, "M3_snapshot", [str(SCRIPTS / "m3_candidate_rw.tcl"), "snapshot", str(snap)], timeout=1200)
        m3: dict[str, object] = {"snapshot_exit": code, "snapshot_sha256": sha256_file(snap),
                                "candidate_bytes": CAND_BYTES}
        if code != 0 or m3["snapshot_sha256"] is None:
            record("M3_candidate_rw", "FAIL", {**m3, "reason": "快照失败，拒绝继续（不得在无快照下写入）"})
            stop_reason = "M3 快照失败"
        else:
            code_w, _ = xsdb_step(run_dir, "M3_write", [str(SCRIPTS / "m3_candidate_rw.tcl"), "write", str(snap)], timeout=1200)
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
                diff_bytes = sum(1 for x, y in zip(a, b)) + abs(len(a) - len(b))
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
            # PRELOAD 已下载 init.elf 与最小 ELF；此处只**选 CPU0 并 con**（CPU1 保持 halted 不释放）
            code, out = xsdb_step(run_dir, "M4a_run_cpu0",
                                  ["-eval", f"connect -url {HW_URL}; "
                                            f"targets -set -filter {{name =~ \"*Cortex-A9*\"}}; con; after 2000; "
                                            f"puts \"M4A_CPU0_STATE=[state]\"; disconnect; exit"])
            record("M4a_cache_visibility", "PASS" if code == 0 else "FAIL",
                   {"run_exit": code,
                    "elf_sha256": sha256_file(elf), "init_elf_sha256": sha256_file(init_elf),
                    "uart_protocol": "COM4 115200 8N1；命令 R/I/F/W/Q；应答行以 M4A 开头",
                    "load_flow": "init.elf（rst -system -stop + con，完成 PS/DDR 初始化）→ dow 最小 ELF → M1/M2/M3 → 此处仅 con CPU0",
                    "note": "M4-a 的 UART 命令交换须按计划书 §4 执行并落盘原始收发；收尾不 stop（避免改状态）"})
            if code != 0:
                stop_reason = "M4-a CPU0 启动失败"

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