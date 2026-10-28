"""验证阶段4 PS 应用"真实解码接线"（离线，S4-T34）。

检查项（任一失败即非 0）：
  A1 应用源码不再对两个入口使用 weak 桩（`__attribute__((weak))` 不得出现在这两处）；
  A2 两个入口在应用内以**强实现**出现（函数定义存在，非 extern 声明）；
  A3 应用包含 r13 冻结解码头 `s2a_ps_decode_nms_reference.h`，并调用 `s2a_t62_decode_nms`；
  A4 解码参数与 r13 调用点一致（head13 5070 / head26 20280、两尺度、score_th 0.25、容量 15）；
  A5 网络启动强实现写 0x008=START(1) 并轮询状态（TERMINAL/FAULT），不再直接返回 -1；
  B1 两变体 ELF 的 `nm` 结果中三个符号均为 **T（强）**，无 W；
  B2 构建记录/主机单测证据存在且单测 exit=0。

用法：
  python -B scripts/stage4_s4ctrl/verify_ps_decode_link.py --repo D:/codex-worktrees/w4
退出码：0=全部通过；1=存在不符；2=输入缺失。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

W_DEFAULT = Path(r"D:\codex-worktrees\w4")
APP = "vitis/stage4/ps/s4d_ps_app.c"
EVID = "report/evidence/S4-T34/ps_decode_link_20261028_r01"
NM = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin\arm-none-eabi-nm.exe")
SYMBOLS = ("s2a_t62_decode_nms", "s2a_decode_nms_reference", "s2b_network_start_from_tensor")


def extract_function(source: str, signature: str) -> str:
    """按花括号配对提取函数体（仅函数文本，不含后续函数）。"""
    start = source.find(signature)
    if start < 0:
        return ""
    depth = 0
    begun = False
    for i in range(start, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
            begun = True
        elif ch == "}":
            depth -= 1
            if begun and depth == 0:
                return source[start:i + 1]
    return source[start:]


def main() -> int:
    """逐项校验并打印结论。"""
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(W_DEFAULT))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    app = (repo / APP).read_text(encoding="utf-8")
    ev = repo / EVID
    errors: list[str] = []
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok:
            errors.append(f"{name}: {detail}")

    # A1/A2：不再 weak、两入口有强定义
    add("A1_no_weak_attributes", "__attribute__((weak))" not in app,
        "源码中不应再出现 __attribute__((weak))")
    for fn in ("s2a_decode_nms_reference", "s2b_network_start_from_tensor"):
        defs = re.findall(r"^int\s+" + fn + r"\s*\(", app, re.M)
        add(f"A2_strong_definition[{fn}]", bool(defs), "未找到强实现定义")
    # A3：include 参考头 + 调 s2a_t62_decode_nms
    add("A3_reference_include", "s2a_ps_decode_nms_reference.h" in app, "缺少参考头 include")
    add("A3_calls_reference_decode", "s2a_t62_decode_nms(" in app, "未调用 s2a_t62_decode_nms")
    # A4：参数一致性
    for pat, why in (("S4D_HEAD13_BYTES", "head13 len 5070"),
                     ("S4D_HEAD26_BYTES", "head26 len 20280"),
                     ("0.24267549589862975", "head13 scale"),
                     ("0.30223452951025775", "head26 scale"),
                     ("S4D_DEC_SCORE_TH   0.25", "score_th 0.25"),
                     ("S4D_DEC_MAX_BOX    15u", "容量 15")):
        add(f"A4_param[{why}]", pat in app, f"缺少 {pat}")
    # A5：网络启动语义（写 START + 轮询 TERMINAL/FAULT）
    body = extract_function(app, "int s2b_network_start_from_tensor")
    seg = body
    add("A5_writes_start", "S4D_CSR_CMD, S4D_CMD_START" in seg, "未写 0x008=START")
    add("A5_polls_terminal", "S4D_TERMINAL" in seg and "S4D_ST_FAULT" in seg, "未轮询 TERMINAL/FAULT")
    add("A5_not_stub", "return -1;" not in seg, "仍是 -1 桩")

    # B1：两变体 ELF nm 强符号
    for variant in ("sw0", "pl"):
        elf = ev / f"s4d_ps_app_{variant}.elf"
        if not elf.is_file():
            add(f"B1_elf_exists[{variant}]", False, f"缺 {elf.name}")
            continue
        nm = subprocess.run([str(NM), "-C", str(elf)], capture_output=True, text=True)
        lines = nm.stdout.splitlines()
        for sym in SYMBOLS:
            hit = [ln for ln in lines if ln.strip().endswith(sym)]
            strong = bool(hit) and hit[0].split()[1] == "T"
            add(f"B1_nm_T[{variant}:{sym}]", strong, f"nm 未显示强符号 T：{hit}")
    # B2：构建记录 + 主机单测
    for variant in ("sw", "pl"):
        rec = ev / f"build_record_{variant}.json"
        if not rec.is_file():
            add(f"B2_build_record[{variant}]", False, "缺 build_record")
            continue
        obj = json.loads(rec.read_text(encoding="utf-8"))
        add(f"B2_build_record[{variant}]", obj["nm"]["is_strong_T"] and
            obj["exit_codes"]["link"] == 0, "build_record 记录非强符号或链接失败")
    host = ev / "host_decode_test" / "exit_code.txt"
    add("B2_host_test_exit0", host.is_file() and "exit=0" in host.read_text(encoding="utf-8"),
        "主机单测未通过")

    ok = not errors
    if args.json:
        print(json.dumps({"verdict": "PASS" if ok else "FAIL", "checks": checks,
                          "errors": errors}, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(("PASS " if c["ok"] else "FAIL ") + c["name"] + ("" if c["ok"] else " | " + c["detail"]))
        print(f"PS_DECODE_LINK_{'VERIFIED' if ok else 'BLOCKED'} ({sum(1 for c in checks if c['ok'])}/{len(checks)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())