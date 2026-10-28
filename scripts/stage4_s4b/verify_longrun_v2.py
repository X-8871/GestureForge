r"""长跑仪表化自检（S4-T34）：在 v1 基础上增加心跳/魔数/中止处理/清零检查。

检查项：
  L1 强符号 T（两变体）；L2 判据常量；L3 循环与失败即停；L4 汇总字段；
  M1 心跳**每轮一行**（不再是每 10 轮）；
  M2 魔数：`S4D_LR_MAGIC_ADDR 0x11B00000`、`s4d_lr_mark` 且步骤 1..8 全部出现、写后 `Xil_DCacheFlushRange`；
  M3 数据中止处理器：`XIL_EXCEPTION_ID_DATA_ABORT_INT` 注册、读 DFSR/DFAR（mrc p15 c5/c6）、写 abort marker；
  M4 收尾清零 `s4d_lr_clear_magic`；
  L5/M5 ELF SHA 与 `app_elf_registration_r7.json` 一致。
退出码：0=全过；1=存在不符；2=输入缺失。
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
REG = "report/evidence/S4-T34/ps_decode_link_20261028_r01/app_elf_registration_r7.json"
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
    src_p, reg_p = repo / APP, repo / REG
    if not src_p.is_file() or not reg_p.is_file() or not NM.is_file():
        print("[FAIL] 输入缺失")
        return 2
    src = src_p.read_text(encoding="utf-8")
    norm = src.replace("\\", "")
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    checks: list[dict] = []

    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        if not elf.is_file():
            checks.append({"id": "L1", "name": f"strong_symbol[{key}]", "ok": False, "detail": "ELF 缺失"})
            continue
        ok, detail = nm_strong_T(elf)
        checks.append({"id": "L1", "name": f"strong_symbol[{key}]", "ok": ok, "detail": f"{elf.name}: {detail}"})

    consts = {"wall": "#define S4D_LR_WALL_MS     1800000u" in src,
              "max": "#define S4D_LR_MAX_ITERS   160u" in src,
              "min": "#define S4D_LR_MIN_ITERS   140u" in src}
    checks.append({"id": "L2", "name": "judgement_constants", "ok": all(consts.values()), "detail": consts})

    logic = {"loop": "for (iter = 1u; iter <= S4D_LR_MAX_ITERS; iter++)" in src,
             "wall_exit": "if (wall_ms >= S4D_LR_WALL_MS) { break; }" in src,
             "fail_print": "LONGRUN FAIL iter=%u why=%s" in src,
             "status_e04": "st != 0x00000E04u" in src,
             "error_zero": "err != 0u" in src,
             "decode_rc": "decode_rc != 0" in src,
             "count_1": "count != 1u" in src,
             "raw_2": "raw != 2u" in src,
             "ack_idle": "ack_idle != 1" in src,
             "epoch_mono": "epoch_not_monotonic" in src,
             "box_change": "box_changed" in src}
    checks.append({"id": "L3", "name": "loop_and_failfast", "ok": all(logic.values()), "detail": logic})

    need = ('"iterations":%u', '"failures":%u', '"wall_ms_lo":%u', '"min_elapsed_ms":%u',
            '"avg_elapsed_ms":%u', '"max_elapsed_ms":%u', '"epoch_first_lo":%u',
            '"epoch_last_lo":%u', '"within_judgement":%d')
    checks.append({"id": "L4", "name": "summary_fields",
                   "ok": all(n in norm for n in need), "detail": {n: (n in norm) for n in need}})

    # M1 心跳每轮
    m1 = {"no_progress_modulo": "iter % S4D_LR_PROGRESS" not in src,
          "heartbeat_marker": "心跳：**每轮一行**" in src,
          "step_line": 'xil_printf("LONGRUN STEP iter=%u elapsed_ms=%u wall_ms=%u epoch_lo=%u' in src}
    checks.append({"id": "M1", "name": "heartbeat_every_round", "ok": all(m1.values()), "detail": m1})

    # M2 魔数
    steps_needed = ["s4d_lr_mark(1u, iter)", "s4d_lr_mark(2u, iter)", "s4d_lr_mark(3u, iter)",
                    "s4d_lr_mark(4u, iter)", "s4d_lr_mark(5u, iter)", "s4d_lr_mark(6u, iter)",
                    "s4d_lr_mark(7u, iter)", "s4d_lr_mark(8u, iter)"]
    m2 = {"addr": "#define S4D_LR_MAGIC_ADDR   0x11B00000u" in src,
          "magic_val": "#define S4D_LR_MAGIC_VAL    0x4C524D47u" in src,
          "helper": "static void s4d_lr_mark(uint32_t step_id, uint32_t iter)" in src,
          "steps_1_to_8": all(x in src for x in steps_needed),
          "flush_after_write": "Xil_DCacheFlushRange((UINTPTR)S4D_LR_MAGIC_ADDR, 64);" in src}
    checks.append({"id": "M2", "name": "step_magic", "ok": all(m2.values()),
                   "detail": {**m2, "missing_steps": [x for x in steps_needed if x not in src]}})

    # M3 中止处理
    m3 = {"register": "XIL_EXCEPTION_ID_DATA_ABORT_INT" in src,
          "handler": "static void s4d_lr_data_abort_handler(void *arg)" in src,
          "dfsr": '"mrc p15, 0, %0, c5, c0, 0"' in src,
          "dfar": '"mrc p15, 0, %0, c6, c0, 0"' in src,
          "abort_marker": "S4D_LR_ABORT_VAL" in src}
    checks.append({"id": "M3", "name": "data_abort_capture", "ok": all(m3.values()), "detail": m3})

    # M4 清零
    m4 = {"clear_fn": "static void s4d_lr_clear_magic(void)" in src,
          "called_at_end": "s4d_lr_clear_magic();   /* 收尾清零魔数区" in src}
    checks.append({"id": "M4", "name": "magic_cleared", "ok": all(m4.values()), "detail": m4})

    for key, item in reg["outputs"].items():
        elf = repo / item["elf"]
        actual = sha256(elf) if elf.is_file() else None
        checks.append({"id": "M5", "name": f"elf_sha_matches_registration[{key}]",
                       "ok": actual == item["elf_sha256"],
                       "detail": {"expected": item["elf_sha256"], "actual": actual}})

    fails = [c for c in checks if not c["ok"]]
    payload = {"task_id": "S4-T34", "checker": "verify_longrun_v2.py", "checks": checks,
               "fail": [c["name"] for c in fails], "verdict": "PASS" if not fails else "FAIL"}
    out = repo / "report/evidence/S4-T34/ps_decode_link_20261028_r01/longrunI"
    out.mkdir(parents=True, exist_ok=True)
    (out / "verify_longrun_v2.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    code = 0 if not fails else 1
    (out / "verify_longrun_v2.exit_code.txt").write_text(f"exit={code}\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['id']} {c['name']}")
        print(f"VERDICT={payload['verdict']} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())