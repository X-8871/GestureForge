#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立复核：新 16 位字的三个通道位是否确实来自绿通道 G'（PL4 中性灰度）

用法：
    python verify_gray_netlist.py <netlist_din_trace_gray*.log> [--expect gray|raw]

期望映射（word[i] = din[i+2]，因为 din = {word, tlast, tuser}）：
    word[15:11] = G'[5:1] = t10, t9, t8, maj, t6
    word[10:5]  = G'[5:0] = t10, t9, t8, maj, t6, t5
    word[4:0]   = G'[5:1] = t10, t9, t8, maj, t6
  --expect gray（默认）：每一位的根驱动必须落在允许集合
        { cmos_d_16bit_d1_reg[5|6|8|9|10]/Q, gray_g2_d*_reg/Q }
     且 G'[2] 的三处（word[12]/[7]/[1]）必须由 3 输入多数门驱动。
  --expect raw：用于**阴性对照**（SOF-only 基线），此时 word[15] 等应来自 B 字段寄存器、
     word[7] 来自已死的 reg[7] ⇒ 预期该模式**不满足**灰度的允许集合。

退出码：0 = 满足所选期望；1 = 不满足；2 = 输入/解析错误。
"""

import re
import sys

LINE_RE = re.compile(r"bit=(\d+)\s+net=(\S+)\s+depth1=(\S+)\s+lut_inputs=(\S*)\s+roots=(.*)$")

EXPECT_WORD = {
    15: ("G'[5]=tdata[10]", "reg", 10), 14: ("G'[4]=tdata[9]", "reg", 9),
    13: ("G'[3]=tdata[8]", "reg", 8),   12: ("G'[2]=maj3(tdata[8])", "maj", 8),
    11: ("G'[1]=tdata[6]", "reg", 6),
    10: ("G'[5]=tdata[10]", "reg", 10), 9: ("G'[4]=tdata[9]", "reg", 9),
    8: ("G'[3]=tdata[8]", "reg", 8),    7: ("G'[2]=maj3(tdata[8])", "maj", 8),
    6: ("G'[1]=tdata[6]", "reg", 6),    5: ("G'[0]=tdata[5]", "reg", 5),
    4: ("G'[5]=tdata[10]", "reg", 10),  3: ("G'[4]=tdata[9]", "reg", 9),
    2: ("G'[3]=tdata[8]", "reg", 8),    1: ("G'[2]=maj3(tdata[8])", "maj", 8),
    0: ("G'[1]=tdata[6]", "reg", 6),
}
ALLOWED_REGS = {5, 6, 8, 9, 10}
FORBIDDEN_REGS = {0, 1, 2, 3, 4, 7, 11, 12, 13, 14, 15}


def parse(path):
    T = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "ILA_GRAY|" not in line:
                continue
            body = line.split("ILA_GRAY|", 1)[1].strip()
            m = LINE_RE.match(body)
            if m:
                T[int(m.group(1))] = {
                    "net": m.group(2), "depth1": m.group(3),
                    "lut_inputs": [x for x in m.group(4).split("|") if x],
                    "roots": [x for x in m.group(5).split("|") if x],
                }
    return T


def base_reg(n):
    return "inst/cmos_d_16bit_d1_reg[%d]/Q" % n


def check(T):
    per_bit, problems, leaks = [], [], []
    for wbit in sorted(EXPECT_WORD, reverse=True):
        db = wbit + 2
        desc, kind, regn = EXPECT_WORD[wbit]
        got = T.get(db)
        row = {"din_bit": db, "word_bit": wbit, "expected": desc,
               "driver": got["depth1"] if got else None,
               "roots": got["roots"] if got else None, "ok": False}
        if not got:
            row["problem"] = "din bit missing from trace"
            problems.append(row); per_bit.append(row); continue
        roots = got["roots"]
        ref = got["depth1"].split("(")[-1].rstrip(")") if got["depth1"] else ""
        if kind == "reg":
            row["ok"] = roots == [base_reg(regn)]
            if not row["ok"]:
                row["problem"] = "expected single root %s" % base_reg(regn)
        else:
            others = [r for r in roots if r != base_reg(regn)]
            row["ok"] = (re.match(r"^(LUT|MUXF)", ref or "") is not None
                         and len(roots) == 3 and base_reg(regn) in roots
                         and len(others) == 2 and all(o.endswith("/Q") for o in others))
            row["majority_extra_roots"] = others
            if not row["ok"]:
                row["problem"] = "expected LUT3 majority over {reg8/Q, d1, d2}"
        if not row["ok"]:
            problems.append(row)
        per_bit.append(row)

    for wbit in EXPECT_WORD:
        for r in (T.get(wbit + 2) or {}).get("roots", []) or []:
            m = re.match(r"^inst/cmos_d_16bit_d1_reg\[(\d+)\]/Q$", r)
            if m and int(m.group(1)) in FORBIDDEN_REGS:
                leaks.append({"din_bit": wbit + 2, "word_bit": wbit, "root": r,
                              "why": "forbidden reg (R/B field or dead G[2] source)"})
            elif not m and not (re.search(r"gray_g2_d\d", r) and r.endswith("/Q")):
                leaks.append({"din_bit": wbit + 2, "word_bit": wbit, "root": r,
                              "why": "unrecognised root"})
    return per_bit, problems, leaks


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: verify_gray_netlist.py <trace.log> [--expect gray|raw]")
    path = sys.argv[1]
    expect = "gray"
    if "--expect" in sys.argv:
        expect = sys.argv[sys.argv.index("--expect") + 1]
    T = parse(path)
    if not T or len(T) < 18:
        print("FAIL=trace_parse_incomplete (parsed %d bits)" % len(T))
        return 2
    per_bit, problems, leaks = check(T)
    print("TRACE_LOG=%s" % path)
    print("EXPECT_MODE=%s" % expect)
    print("PARSED_DIN_BITS=%d" % len(T))
    print("")
    print("%-8s %-8s %-24s %-10s %s" % ("din_bit", "word_bit", "expected_source", "ok", "actual_roots"))
    for r in per_bit:
        print("%-8d %-8d %-24s %-10s %s" % (r["din_bit"], r["word_bit"], r["expected"],
                                            "OK" if r["ok"] else "BAD", r["roots"]))
    print("")
    passed = (not problems) and (not leaks)
    print("PROBLEMS=%d LEAKS=%d" % (len(problems), len(leaks)))
    if leaks:
        print("LEAK_DETAIL=%s" % leaks)
    if expect == "gray":
        print("RESULT=%s" % ("ALL_BITS_FROM_GREEN_G = PASS" if passed else "GRAY_MAP_FAIL"))
        return 0 if passed else 1
    # raw 阴性对照：应当不满足灰度允许集合
    print("RESULT=%s" % ("UNEXPECTEDLY_GREEN (baseline should not be gray)" if passed
                         else "BASELINE_NOT_GREEN = expected for negative control"))
    return 1 if passed else 0


if __name__ == "__main__":
    sys.exit(main())