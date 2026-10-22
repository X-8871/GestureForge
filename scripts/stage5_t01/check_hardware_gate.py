"""S5-T01 上板硬性前置门禁（fail-closed）：未获 2B 书面让出则拒绝放行。

本脚本**只读**：读信箱、读工作树状态、读进程列表；不连接板卡、不启动 `hw_server`、不写寄存器。

放行（GO）必须同时满足：
  1. `codex_mailbox/` 存在**新的书面让出/释放**通知（编号晚于最近的占用通知，且正文含正向让出表述、
     且不含“不将本通知当作…释放/占用”这类否定措辞）；
  2. 操作者显式传入 `--release-id <该通知编号>`，与自动检出的编号一致；
  3. 现场无 `hw_server`/`vivado`/`xsdb`/`vitis`/`xsim` 进程；
  4. 六棵树均无 `index.lock`。
任一不满足即 BLOCKED（退出码 1），并在 JSON 中给出原因。**不存在“没看到进程就算让出”的判定。**

退出码：0=GO；1=BLOCKED；2=环境/输入错误。
用法：
  python -B scripts/stage5_t01/check_hardware_gate.py --out report/evidence/S5-T01/<run_id>
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

MAIN_ROOT = pathlib.Path(r"D:\FPGA_Competition")
MAILBOX = MAIN_ROOT / "report/evidence/CTRL-DSH-HANDOFF/codex_mailbox"
WORKTREES = {
    "main": MAIN_ROOT,
    "w2b": MAIN_ROOT / "w2b",
    "w4": pathlib.Path(r"D:\codex-worktrees\w4"),
    "w5": pathlib.Path(r"D:\codex-worktrees\w5"),
    "dbdf": pathlib.Path(r"D:\codex-worktrees\dbdf"),
    "96a3": pathlib.Path(r"D:\codex-worktrees\96a3"),
}
PROCESS_PATTERNS = ("hw_server", "vivado", "xsdb", "vitis", "xsim", "cs_server")
# 正向让出表述
POSITIVE = re.compile(r"(让出|释放|空档|交还|release)", re.IGNORECASE)
# 否定措辞：出现即说明该通知不是让出声明（如占用通知里常见的“不将本通知当作…释放”）
NEGATIVE = re.compile(r"(不将本通知当作|未让出|不得当作|尚未?让出|仍在占用|独占)", re.IGNORECASE)


def now_utc8() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def run(cmd: list[str], cwd: pathlib.Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def git(worktree: pathlib.Path, *args: str) -> str:
    code, out = run(["git", "-C", str(worktree), *args])
    return out.strip()


def mailbox_entries() -> list[dict]:
    entries = []
    if not MAILBOX.is_dir():
        return entries
    for path in sorted(MAILBOX.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        entries.append({
            "file": path.name,
            "id": path.stem.split("-")[0] + "-" + "-".join(path.stem.split("-")[1:3]) if "-" in path.stem else path.stem,
            "mtime_utc8": datetime.datetime.fromtimestamp(path.stat().st_mtime,
                                                          datetime.timezone(datetime.timedelta(hours=8))
                                                          ).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "positive_release_wording": bool(POSITIVE.search(text)),
            "non_release_negation": bool(NEGATIVE.search(text)),
        })
    return entries


def detect_release(entries: list[dict]) -> tuple[dict | None, dict | None]:
    """返回 (最近的占用通知, 候选让出通知)。占用/让出以文件名顺序（编号递增）与措辞共同判定。"""
    occupation, release = None, None
    for entry in entries:                        # 文件名已排序 = 编号递增
        text_positive = entry["positive_release_wording"] and not entry["non_release_negation"]
        if text_positive:
            release = entry
        else:
            occupation = entry
    # 只有当让出通知出现在最近占用通知之后才有效
    if release is not None and occupation is not None and release["file"] <= occupation["file"]:
        release = None
    return occupation, release


def processes() -> tuple[list[dict], str, bool]:
    """枚举硬件/重型进程；返回 (命中列表, 原始输出, 枚举是否成功)。

    fail-closed：枚举失败时调用方**不得**把它当作“无占用”，必须判 BLOCKED。
    注意 Git Bash(MSYS) 会把 `/FO` 改写成路径，故优先用 `cmd.exe /c tasklist`，并以 PowerShell 兜底。
    """
    attempts = [
        ["cmd.exe", "/c", "tasklist", "/FO", "CSV", "/NH"],
        ["tasklist", "/FO", "CSV", "/NH"],
        ["pwsh", "-NoProfile", "-Command",
         "Get-Process | Select-Object ProcessName,Id | ConvertTo-Csv -NoTypeInformation"],
    ]
    raw = ""
    for cmd in attempts:
        code, out = run(cmd)
        raw += f"$ {' '.join(cmd)}\n[exit code: {code}]\n{out}\n"
        if code != 0 or not out.strip():
            continue
        found = []
        for line in out.splitlines():
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) < 2:
                continue
            name = parts[0].strip('"')
            if any(pattern in name.lower() for pattern in PROCESS_PATTERNS):
                found.append({"name": name, "pid": parts[1].strip('"')})
        return found, raw, True
    return [], raw, False


def main() -> int:
    parser = argparse.ArgumentParser(description="S5-T01 上板硬性前置门禁（只读、fail-closed）")
    parser.add_argument("--out", required=True, help="证据输出目录")
    parser.add_argument("--release-id", default=None,
                        help="操作者确认的让出通知编号（必须与自动检出的一致才放行）")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out)
    if not out_dir.is_absolute():
        out_dir = pathlib.Path(r"D:\codex-worktrees\w5") / out_dir
    console = out_dir / "console"
    console.mkdir(parents=True, exist_ok=True)

    reasons: list[str] = []
    entries = mailbox_entries()
    occupation, release = detect_release(entries)

    worktrees = {}
    for name, path in WORKTREES.items():
        if not path.exists():
            worktrees[name] = {"exists": False}
            continue
        lock_path = git(path, "rev-parse", "--git-path", "index.lock")
        lock_abs = pathlib.Path(lock_path) if pathlib.Path(lock_path).is_absolute() else path / lock_path
        worktrees[name] = {
            "exists": True,
            "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD"),
            "head": git(path, "rev-parse", "HEAD"),
            "index_lock_path": lock_path,
            "index_lock_exists": lock_abs.exists(),
        }
    locks = [name for name, info in worktrees.items() if info.get("index_lock_exists")]
    if locks:
        reasons.append(f"存在 index.lock：{locks}")

    procs, proc_raw, proc_enum_ok = processes()
    if not proc_enum_ok:
        reasons.append("无法枚举系统进程（fail-closed）：不得据此认为无硬件占用，也不得放行")
    elif procs:
        reasons.append("检测到硬件/重型进程：" + ", ".join(f"{p['name']}({p['pid']})" for p in procs))

    main_state = (MAIN_ROOT / ".codex/STATE.md")
    state_text = main_state.read_text(encoding="utf-8", errors="replace") if main_state.exists() else ""
    release_keywords = ("让出", "空档", "释放", "handover")
    state_mentions_release = any(word in state_text for word in release_keywords)

    if release is None:
        reasons.append("codex_mailbox 未发现新的书面让出/释放通知"
                       f"（最近占用通知：{occupation['file'] if occupation else '未识别'}）")
    elif args.release_id != release["id"]:
        reasons.append(f"未提供匹配的 --release-id：自动检出 {release['id']}，"
                       f"实际传入 {args.release_id!r}")

    decision = "GO" if not reasons else "BLOCKED"
    report = {
        "schema_version": "gestureforge_s5t01_hardware_gate_v1",
        "task_id": "S5-T01",
        "generated_utc8": now_utc8(),
        "decision": decision,
        "reasons": reasons,
        "release_detection": {
            "latest_occupation_notice": occupation,
            "candidate_release_notice": release,
            "provided_release_id": args.release_id,
            "rule": "让出通知必须编号晚于最近占用通知，含正向让出表述且不含否定措辞；另需 --release-id 精确匹配",
        },
        "mailbox_entries": entries,
        "worktrees": worktrees,
        "hardware_processes": procs,
        "hardware_process_enumeration_ok": proc_enum_ok,
        "main_state_release_wording_present": state_mentions_release,
        "notes": [
            "本门禁只读：不连接板卡、不启动 hw_server、不写寄存器。",
            "“没看到进程”不作为让出依据；必须同时具备书面让出与显式 release-id。",
            "门禁通过只表示可以进入上板流程，不代表 G3/G4/G5 或任何验收通过。",
        ],
    }

    (console / "mailbox_entries.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8")
    (console / "worktrees.json").write_text(json.dumps(worktrees, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    (console / "processes.json").write_text(json.dumps(procs, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
    (console / "process_enumeration.txt").write_text(proc_raw, encoding="utf-8")
    (out_dir / "hardware_gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"decision": decision, "reasons": reasons,
                      "release": release["file"] if release else None,
                      "occupation": occupation["file"] if occupation else None},
                     ensure_ascii=False))
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())