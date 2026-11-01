r"""长跑模式离线自检（S4-T34）：强符号 / 判据常量 / 循环与失败即停逻辑 / ELF 身份与登记一致。

检查项（任一不符即非 0）：
  L1 两个变体 ELF 中 `s2a_t62_decode_nms` 仍为强符号 T；
  L2 判据常量：`S4D_LR_WALL_MS 1800000u`、`S4D_LR_MAX_ITERS 160u`、`S4D_LR_MIN_ITERS 140u`；
  L3 循环与失败即停逻辑：`for (iter = 1u; iter <= S4D_LR_MAX_ITERS; iter++)`、
     `wall_ms >= S4D_LR_WALL_MS` 退出、`LONGRUN FAIL iter=` 即时打印并 `break`、
     每轮校验 `status != 0x00000E04u` / `err != 0u` / `decode_rc != 0` / `count != 1u` / `raw != 2u` /
     `ack_idle != 1` / `epoch_not_monotonic` / `box_changed`；
  L4 汇总字段：`LONGRUN RESULT=` 含 iterations/failures/wall_ms/min/avg/max/epoch_first/epoch_last/box/within_judgement；
  L5 ELF SHA-256 与 `app_elf_registration_r6.json` 登记一致（旧 SHA 不复用）。

用法：python -B scripts/stage4_s4b/verify_longrun_v1.py [--repo D:/codex-worktrees/w4] [--json]
退出码：0=全部通过；1=存在不符；2=输入/环境缺失。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

W_DEFAULT = Path(r"D:\codex-worktrees\w4")
NM = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-nm.exe")
APP = "vitis/stage4/ps/s4d_ps_app.c"
REG = "report/evidence/S4-T34/ps_decode_link_20261028_r01/app_elf_registration_r6.json"
STRONG = "s2a_t62_decode_nms"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def nm_strong_T(elf: Path) -> tuple[bool, str]:
    proc = subprocess.run([str(NM), "-C", str(elf)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    hits = [ln for ln in (proc.stdout or "").splitlines() if ln.strip().endswith(STRONG)]
    if not hits:
        return False, "未找到符号"
    kind = hits[0].split()[1] if len(hits[0].split()) > 1 else "?"
    return kind == "T", f"type={kind}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(W_DEFAULT))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    src_p = repo / APP
    reg_p = repo / REG
    if not src_p.is_file() or not reg_p.is_file() or not NM.is_file():
        print(f"[FAIL] 输入缺失：app={src_p.is_file()} reg={reg_p.is_file()} nm={NM.is_file()}")
        return 2
    src = src_p.read_text(encoding="utf-8")
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    checks: list[dict] = []

    # L1 强符号
    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        if not elf.is_file():
            checks.append({"id": "L1", "name": f"strong_symbol[{key}]", "ok": False, "detail": "ELF 缺失"})
            continue
        ok, detail = nm_strong_T(elf)
        checks.append({"id": "L1", "name": f"strong_symbol[{key}]", "ok": ok, "detail": f"{elf.name}: {detail}"})

    # L2 常量
    consts = {
        "wall": "#define S4D_LR_WALL_MS     1800000u" in src,
        "max": "#define S4D_LR_MAX_ITERS   160u" in src,
        "min": "#define S4D_LR_MIN_ITERS   140u" in src,
    }
    checks.append({"id": "L2", "name": "judgement_constants", "ok": all(consts.values()), "detail": consts})

    # L3 循环与失败即停
    logic = {
        "loop": "for (iter = 1u; iter <= S4D_LR_MAX_ITERS; iter++)" in src,
        "wall_exit": "if (wall_ms >= S4D_LR_WALL_MS) { break; }" in src,
        "fail_print": "LONGRUN FAIL iter=%u why=%s" in src,
        "fail_break": src.count("LONGRUN FAIL iter=%u why=%s") >= 1 and "break;" in src.split("LONGRUN FAIL iter=%u why=%s")[1][:400],
        "status_e04": "st != 0x00000E04u" in src,
        "error_zero": "err != 0u" in src,
        "decode_rc": "decode_rc != 0" in src,
        "count_1": "count != 1u" in src,
        "raw_2": "raw != 2u" in src,
        "ack_idle": "ack_idle != 1" in src,
        "epoch_mono": "epoch_not_monotonic" in src,
        "box_change": "box_changed" in src,
        "box_equal": "s4d_lr_box_equal" in src,
    }
    checks.append({"id": "L3", "name": "loop_and_failfast", "ok": all(logic.values()), "detail": logic})

    # L4 汇总字段（源码格式串中的引号以 \" 转义出现，先去反斜杠再比对）
    norm = src.replace("\\", "")
    need = ('"iterations":%u', '"failures":%u', '"wall_ms_lo":%u', '"min_elapsed_ms":%u',
            '"avg_elapsed_ms":%u', '"max_elapsed_ms":%u', '"epoch_first_lo":%u',
            '"epoch_last_lo":%u', '"within_judgement":%d')
    present = {n: (n in norm) for n in need}
    checks.append({"id": "L4", "name": "summary_fields", "ok": all(present.values()), "detail": present})

    # L5 ELF 身份
    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        actual = sha256(elf) if elf.is_file() else None
        checks.append({"id": "L5", "name": f"elf_sha_matches_registration[{key}]",
                       "ok": actual == item["elf_sha256"],
                       "detail": {"expected": item["elf_sha256"], "actual": actual}})

    fails = [c for c in checks if not c["ok"]]
    payload = {"task_id": "S4-T34", "checker": "verify_longrun_v1.py", "checks": checks,
               "fail": [c["name"] for c in fails], "verdict": "PASS" if not fails else "FAIL"}
    out = repo / "report/evidence/S4-T34/ps_decode_link_20261028_r01/longrun"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify_longrun_v1.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    code = 0 if not fails else 1
    (out / "verify_longrun_v1.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['id']} {c['name']}")
        print(f"VERDICT={payload['verdict']} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())