"""收集 S4-T32 Phase 2 构建证据（license 重试 build_r02；不接触板卡）。

收集内容（全部取自真实文件，不手填）：
  · bitstream / XSA 完整 SHA-256 与大小（若存在）；
  · 利用率与 时序 摘要（从 Vivado 报告原文截取关键行，含 WNS/TNS/WHS/THS）；
  · license 上下文（文件路径、sha256、日志中的 license 行原文）；
  · 构建耗时（起止时间）与真实失败分类：
      SUCCESS / TIMING_NOT_MET / LICENSE_TIER_INSUFFICIENT / BUILD_FAILED / NOT_COMPLETED
  · 输出 `phase2_build_r02_<date>/phase2_build_result.json` + 关键日志副本（.txt，可入库）。

用法：python -B scripts/stage4_s4b/collect_phase2_build_evidence.py
退出码：0=证据收集完成（不代表构建成功）；2=输入缺失。
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CN = timezone(timedelta(hours=8))
W = Path(r"D:\codex-worktrees\w4")
BUILD = W / "tmp" / "4" / "S4-T32" / "build_r02"
EVID = W / "report" / "evidence" / "S4-T32" / "phase2_build_r02_20261027_r01"
LIC = Path(r"C:\Users\22061\Documents\s15_appdata_56C955A6_5bcd56b837931ca1a05d6293153a3476\basic_only.lic")


def sha(path: Path) -> str | None:
    """文件 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def grep(path: Path, pattern: str, limit: int = 20) -> list[str]:
    """从文件抓取匹配行。"""
    if not path.is_file():
        return []
    rx = re.compile(pattern)
    out: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if rx.search(line):
            out.append(line.strip())
            if len(out) >= limit:
                break
    return out


def main() -> int:
    """收集并落证。"""
    if not BUILD.is_dir():
        print(f"[FAIL] 构建目录缺失：{BUILD}")
        return 2
    EVID.mkdir(parents=True, exist_ok=True)
    prj = BUILD / "prj"
    bits = sorted((prj / "s4d_baseline.runs").rglob("*.bit")) if (prj / "s4d_baseline.runs").is_dir() else []
    xsas = sorted(prj.rglob("*.xsa")) if prj.is_dir() else []
    console = BUILD / "vivado_console.log"
    buildlog = BUILD / "build.log"

    # 关键日志副本（.txt 便于入库）
    for src, name in ((console, "vivado_console_excerpt.txt"),):
        if src.is_file():
            lines = grep(src, r"license|Licensed|Synthesis finished|ERROR|Exiting Vivado|write_bitstream|WNS|TNS")
            (EVID / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if buildlog.is_file():
        shutil.copy2(buildlog, EVID / "build_log.txt")

    timing = {}
    for rpt in sorted(prj.rglob("timing_summary*.rpt")) if prj.is_dir() else []:
        text = rpt.read_text(encoding="utf-8", errors="replace")
        for key in ("WNS(ns)", "TNS(ns)", "WHS(ns)", "THS(ns)"):
            m = re.search(re.escape(key) + r"\s+([-\d.]+)", text)
            if m:
                timing[key] = m.group(1)
        shutil.copy2(rpt, EVID / f"timing_{rpt.parent.name}.rpt")
    util = {}
    for rpt in sorted(prj.rglob("utilization*.rpt")) if prj.is_dir() else []:
        text = rpt.read_text(encoding="utf-8", errors="replace")
        for key in ("Slice LUTs", "Slice Registers", "Block RAM Tile", "DSPs"):
            m = re.search(r"\| " + re.escape(key) + r"\s*\| ([^|]+)\|", text)
            if m:
                util[key] = m.group(1).strip()
        shutil.copy2(rpt, EVID / f"utilization_{rpt.parent.name}.rpt")

    # 失败分类
    console_text = console.read_text(encoding="utf-8", errors="replace") if console.is_file() else ""
    license_lines = grep(console, r"license|Licensed")
    if bits:
        status = "SUCCESS"
    elif re.search(r"Common 17-345|Common 17-348", console_text):
        status = "LICENSE_TIER_INSUFFICIENT"
    elif timing and any(float(v) < 0 for v in timing.values() if re.match(r"^-?\d+(\.\d+)?$", v)):
        status = "TIMING_NOT_MET"
    elif "BUILD DONE" in (buildlog.read_text(encoding="utf-8", errors="replace") if buildlog.is_file() else ""):
        status = "BUILD_DONE_NO_BITSTREAM"
    elif "Exiting Vivado" in console_text:
        status = "BUILD_FAILED"
    else:
        status = "NOT_COMPLETED"

    pid_line = (BUILD / "vivado.pid.txt").read_text(encoding="utf-8", errors="replace") if (BUILD / "vivado.pid.txt").is_file() else ""
    lic_ctx = json.loads((BUILD / "license_context.json").read_text(encoding="utf-8")) if (BUILD / "license_context.json").is_file() else {}
    result = {
        "task_id": "S4-B/S4-T32", "phase": "Phase2 build (license retry, build_r02)",
        "collected_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "status": status,
        "license": {"path": str(LIC), "sha256": sha(LIC),
                     "env_var_value": lic_ctx.get("env_var"),
                     "log_lines": license_lines[:6],
                     "increments_expected": ["Vivado_Basic_Package", "Vivado_Simulation",
                                             "Vivado_Synthesis", "Vivado_Implementation"]},
        "artifacts": {
            "bitstreams": [{"path": str(p), "sha256": sha(p), "size_bytes": p.stat().st_size} for p in bits],
            "xsas": [{"path": str(p), "sha256": sha(p), "size_bytes": p.stat().st_size} for p in xsas],
        },
        "timing": timing, "utilization": util,
        "build_pid_file": pid_line.strip(),
        "failed_previous_run": {"run": "build_r01", "status": "LICENSE_BLOCKED_PRESERVED（未覆盖）"},
        "honesty": "构建成功不等于 G3/G4/G5；未上板；未 FROZEN。",
    }
    (EVID / "phase2_build_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "bits": len(bits), "xsas": len(xsas),
                      "timing": timing, "utilization": util,
                      "evidence_dir": str(EVID)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())