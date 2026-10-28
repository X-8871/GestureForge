r"""M4-b r3 应用自检（离线，S4-T34）：确认"超时修正"三条 + 强符号 + ELF 身份。

检查项（任一不符即非 0）：
  C1 新 ELF（sw0/pl 两变体）中 `s2a_t62_decode_nms` 仍为 **强符号 T**（arm-none-eabi-nm）；
  C2 源码超时常量 = `0xFFFFFFFFu`（S4D_NET_TIMEOUT_CYCLES），且**不存在** `400u` 超时写入
     （`S4D_CSR_CORETO_W` / `S4D_CSR_DRAINTO_W` 两处都必须用常量）；
  C3 轮询预算：`S4D_M4B_SPIN_MAX = 150000000`（>=1.5e8）与 `S4D_M4B_WALL_MS = 120000`，
     且等待循环使用两者；`M4B RESULT` 含 `elapsed_ms`；
  C4 ELF SHA-256 与 `app_elf_registration_r3.json` 登记值一致（旧 SHA 不复用）。

用法：python -B scripts/stage4_s4b/verify_m4b_timeout_v3.py [--repo D:/codex-worktrees/w4] [--json]
退出码：0=全部通过；1=存在不符；2=输入/环境缺失。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

W_DEFAULT = Path(r"D:\codex-worktrees\w4")
NM = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-nm.exe")
APP = "vitis/stage4/ps/s4d_ps_app.c"
REG = "report/evidence/S4-T34/ps_decode_link_20261028_r01/app_elf_registration_r3.json"
STRONG = "s2a_t62_decode_nms"


def sha256(p: Path) -> str:
    """文件 SHA-256。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def nm_strong_T(elf: Path) -> tuple[bool, str]:
    """用 nm 判断强符号：命中行类型必须为 T。"""
    proc = subprocess.run([str(NM), "-C", str(elf)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    hits = [ln for ln in (proc.stdout or "").splitlines() if ln.strip().endswith(STRONG)]
    if not hits:
        return False, "未找到符号"
    kind = hits[0].split()[1] if len(hits[0].split()) > 1 else "?"
    return kind == "T", f"type={kind}"


def main() -> int:
    """逐项校验。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(W_DEFAULT))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    checks: list[dict] = []

    app_p = repo / APP
    reg_p = repo / REG
    if not app_p.is_file() or not reg_p.is_file() or not NM.is_file():
        print(f"[FAIL] 输入缺失：app={app_p.is_file()} reg={reg_p.is_file()} nm={NM.is_file()}")
        return 2
    src = app_p.read_text(encoding="utf-8")
    reg = json.loads(reg_p.read_text(encoding="utf-8"))

    # C1 强符号（两变体）
    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        if not elf.is_file():
            checks.append({"id": "C1", "name": f"strong_symbol[{key}]", "ok": False, "detail": "ELF 缺失"})
            continue
        ok, detail = nm_strong_T(elf)
        checks.append({"id": "C1", "name": f"strong_symbol[{key}]", "ok": ok,
                       "detail": f"{elf.name}: {detail}"})

    # C2 超时常量
    has_const = "#define S4D_NET_TIMEOUT_CYCLES  0xFFFFFFFFu" in src
    co = [ln.strip() for ln in src.splitlines() if "S4D_CSR_CORETO_W," in ln]
    dr = [ln.strip() for ln in src.splitlines() if "S4D_CSR_DRAINTO_W," in ln]
    co_ok = len(co) == 2 and all("S4D_NET_TIMEOUT_CYCLES" in ln for ln in co)
    dr_ok = len(dr) == 2 and all("S4D_NET_TIMEOUT_CYCLES" in ln for ln in dr)
    no_400 = "400u" not in src
    checks.append({"id": "C2", "name": "timeout_const_0xFFFFFFFF",
                   "ok": has_const and co_ok and dr_ok and no_400,
                   "detail": {"define": has_const, "coreto_lines": co, "drainto_lines": dr,
                              "no_400u": no_400}})

    # C3 预算与 elapsed_ms
    spin_ok = "#define S4D_M4B_SPIN_MAX        150000000u" in src
    wall_ok = "#define S4D_M4B_WALL_MS         120000u" in src
    loop_ok = "spin < S4D_M4B_SPIN_MAX" in src and "elapsed_ms >= S4D_M4B_WALL_MS" in src
    # RESULT 里的键在 C 源码中以 \" 转义出现；先去反斜杠再比对
    norm = src.replace("\\", "")
    res_ok = '"elapsed_ms":%u' in norm and '"spin":%u' in norm
    checks.append({"id": "C3", "name": "spin_budget_and_elapsed",
                   "ok": spin_ok and wall_ok and loop_ok and res_ok,
                   "detail": {"spin_max_1_5e8": spin_ok, "wall_ms_120000": wall_ok,
                              "loop_uses_both": loop_ok, "result_has_elapsed_ms": res_ok}})

    # C4 ELF 身份与登记一致
    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        actual = sha256(elf) if elf.is_file() else None
        ok = actual == item["elf_sha256"]
        checks.append({"id": "C4", "name": f"elf_sha_matches_registration[{key}]", "ok": ok,
                       "detail": {"expected": item["elf_sha256"], "actual": actual}})

    fails = [c for c in checks if not c["ok"]]
    payload = {"task_id": "S4-T34", "checker": "verify_m4b_timeout_v3.py",
               "checks": checks, "fail": [c["name"] for c in fails],
               "verdict": "PASS" if not fails else "FAIL"}
    out = repo / "report" / "evidence" / "S4-T34" / "ps_decode_link_20261028_r01" / "m4b_r3"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify_m4b_timeout_v3.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    code = 0 if not fails else 1
    (out / "verify_m4b_timeout_v3.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['id']} {c['name']}")
        print(f"VERDICT={payload['verdict']} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())