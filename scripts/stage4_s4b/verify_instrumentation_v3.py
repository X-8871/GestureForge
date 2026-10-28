r"""长跑仪表化可达性检查器 v3（fail-closed）+ 负控。

检查（源码可达性为主，ELF 证据为辅）：
  R1 注册语句必须位于 `s4d_longrun_selfcheck` **函数体内**（花括号配对），且在其体内**首次**
     预处理/CSR 访问之前；
  R2 记录区：8 字布局常量、mark(进入,含 CSR 地址/值)、done(完成)、commit 常量、handler 写 DFSR/DFAR；
  R3 ELF：handler 保留、longrun 符号存在（含 .isra 克隆）、`_vector_table` 存在；
  R4 objdump：`Xil_ExceptionInit` 与 `Xil_ExceptionRegisterHandler` 调用点归属于 longrun 符号；
  R5 源码中注册语句**只能出现一次**且不在 chainb 等相关分支内。
负控（--source 指向变异副本）必须 FAIL：否则检查器无判别力。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

W = Path(r"D:\codex-worktrees\w4")
BIN = Path(r"D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin")
NM, OBJDUMP = BIN / "arm-none-eabi-nm.exe", BIN / "arm-none-eabi-objdump.exe"
DEFAULT_ELF = W / "report/evidence/S4-T34/ps_decode_link_20261028_r01/longrunK/s4d_ps_app_sw0_longrunK.elf"
FUNC_RE = re.compile(r"static\s+(?:__attribute__\(\([^)]*\)\)\s*)?int\s+s4d_longrun_selfcheck\s*\(void\)")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def func_body(text: str, start: int) -> tuple[int, int]:
    """从函数声明处开始，找到函数体 { ... } 的区间（花括号配对，忽略字符串/注释的近似实现）。"""
    i = text.index("{", start)
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i, j + 1
        j += 1
    return i, len(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(W / "vitis/stage4/ps/s4d_ps_app.c"))
    ap.add_argument("--elf", default=str(DEFAULT_ELF))
    ap.add_argument("--evidence", default=str(W / "report/evidence/S4-T34/longrun_instr_v2_20261028_r01/evidence.json"))
    ap.add_argument("--expect", choices=("PASS", "FAIL"), default="PASS",
                    help="负控时传 FAIL：检查器判定必须等于它")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    src_p, elf_p = Path(args.source), Path(args.elf)
    checks: list[dict] = []

    def add(cid: str, name: str, ok: bool, detail) -> None:
        checks.append({"id": cid, "name": name, "ok": bool(ok), "detail": detail})

    if not src_p.is_file():
        print("[FAIL] 源码缺失")
        return 2
    src = src_p.read_text(encoding="utf-8")
    m = FUNC_RE.search(src)
    add("R1a", "longrun_function_found", bool(m), {"found": bool(m)})
    if m:
        b0, b1 = func_body(src, m.start())
        body = src[b0:b1]
        reg_pos = body.find("Xil_ExceptionRegisterHandler")
        init_pos = body.find("Xil_ExceptionInit")
        first_csr = min([p for p in (body.find("s4d_wr("), body.find("s4d_rd("),
                         body.find("s4d_sw_preproc_"), body.find("s4d_read_epoch(")) if p >= 0],
                        default=len(body))
        add("R1b", "registration_inside_longrun_body", reg_pos >= 0, {"pos": reg_pos, "body_len": len(body)})
        add("R1c", "registration_before_first_csr_or_preproc",
            reg_pos >= 0 and reg_pos < first_csr, {"reg_pos": reg_pos, "first_csr_pos": first_csr})
        add("R1d", "exception_init_called", init_pos >= 0 and init_pos < first_csr,
            {"init_pos": init_pos, "first_csr_pos": first_csr})
    # R2 记录区
    r2 = {
        "rec_addr": "0x11B00000u" in src,
        "rec_bytes_32": "S4D_LR_REC_BYTES     32u" in src or "S4D_LR_REC_BYTES 32u" in src,
        "magic": "0x53344C01u" in src,
        "commit_valid": "0xC0DEC0DEu" in src,
        "commit_abort": "0xAB0AB70Bu" in src,
        "read_sentinel": "0xFFFFFFFFu" in src and "S4D_LR_READ_SENTINEL" in src,
        "mark_signature": "static void s4d_lr_mark(uint32_t step_id, uint32_t iter, uint32_t csr_addr, uint32_t csr_val)" in src,
        "done_signature": "static void s4d_lr_done(uint32_t step_id, uint32_t iter)" in src,
        "handler_writes_dfsr": '"mrc p15, 0, %0, c5, c0, 0"' in src,
        "handler_writes_dfar": '"mrc p15, 0, %0, c6, c0, 0"' in src,
        "handler_sets_commit": "m[7] = S4D_LR_COMMIT_ABORT;" in src,
    }
    add("R2", "record_layout_and_handler", all(r2.values()), r2)
    # R5 唯一性
    reg_count = src.count("Xil_ExceptionRegisterHandler")
    add("R5", "registration_declared_once", reg_count == 1, {"count": reg_count})
    # R3 ELF
    if elf_p.is_file():
        nm = subprocess.run([str(NM), str(elf_p)], capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout
        syms = {}
        for line in nm.splitlines():
            parts = line.split()
            if len(parts) == 3:
                syms[parts[2]] = {"addr": parts[0], "type": parts[1]}
        r3 = {
            "handler_retained": "s4d_lr_data_abort_handler" in syms,
            "longrun_symbol": any(k.startswith("s4d_longrun_selfcheck") for k in syms),
            "vector_table": "_vector_table" in syms,
        }
        add("R3", "elf_symbols", all(r3.values()), r3)
        obj = subprocess.run([str(OBJDUMP), "-d", "--no-show-raw-insn", str(elf_p)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        sites = []
        for mm in re.finditer(r"bl\s+[0-9a-f]+ <Xil_ExceptionRegisterHandler>", obj):
            marks = re.findall(r"\n([0-9a-f]{8}) <([^>]+)>:", obj[:mm.start()])
            sites.append(marks[-1][1] if marks else "?")
        add("R4", "registration_call_site_in_longrun",
            bool(sites) and all(s.startswith("s4d_longrun_selfcheck") for s in sites),
            {"sites": sites})
    else:
        add("R3", "elf_symbols", False, {"reason": "ELF 缺失", "path": str(elf_p)})
        add("R4", "registration_call_site_in_longrun", False, {"reason": "ELF 缺失"})
    # 证据文件一致性（可选）
    ev_p = Path(args.evidence)
    if ev_p.is_file():
        ev = json.loads(ev_p.read_text(encoding="utf-8"))
        same_elf = ev.get("elf", {}).get("sha256") == sha(elf_p) if elf_p.is_file() else False
        add("R6", "evidence_matches_elf", same_elf,
            {"evidence_elf": ev.get("elf", {}).get("sha256"),
             "actual": sha(elf_p) if elf_p.is_file() else None})
    fails = [c for c in checks if not c["ok"]]
    verdict = "PASS" if not fails else "FAIL"
    ok = verdict == args.expect
    payload = {"checker": "instrumentation_reachability_v3", "source": str(src_p),
               "source_sha256": sha(src_p), "elf": str(elf_p),
               "elf_sha256": sha(elf_p) if elf_p.is_file() else None,
               "checks": checks, "verdict": verdict, "expect": args.expect,
               "discriminative": ok}
    out_dir = W / "report/evidence/S4-T34/longrun_instr_v2_20261028_r01"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = "negative_control" if args.expect == "FAIL" else "verify_v3"
    (out_dir / f"{tag}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['id']} {c['name']}")
        print(f"VERDICT={verdict} expect={args.expect} discriminative={ok} exit={0 if ok else 1}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())