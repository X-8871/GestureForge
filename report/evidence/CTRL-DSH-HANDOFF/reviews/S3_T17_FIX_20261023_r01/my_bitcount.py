#!/usr/bin/env python3
"""Reviewer 独立复算：位计数与两种口径（不复用被审 per_bit_table）。

只读帧字节，按 1280x720x3 内存序 B,G,R 取 BAR_X 采样点，
自行推导白条/黑条字段值，再逐位判可辨性。
"""
import json
import os
import sys

WIDTH = 1280
ROW = WIDTH * 3
BAR_X = (80, 240, 400, 560, 720, 880, 1040, 1200)


def sample(path):
    data = open(path, "rb").read()
    rows = {}
    for y in (200, 360, 500):
        chunk = data[y * ROW:(y + 1) * ROW]
        segs = []
        for x in BAR_X:
            b, g, r = chunk[x * 3], chunk[x * 3 + 1], chunk[x * 3 + 2]
            segs.append((r, g, b))
        rows[y] = segs
    return rows


def fields(seg):
    r, g, b = seg
    return {"R": r >> 3, "G": g >> 2, "B": b >> 3}


def per_bit(white, black, tolerance):
    wf, bf = fields(white), fields(black)
    out = {}
    for ch, nbits in (("R", 5), ("G", 6), ("B", 5)):
        for k in range(nbits - 1, -1, -1):
            wbit = (wf[ch] >> k) & 1
            bbit = (bf[ch] >> k) & 1
            if wbit != 1:
                st = "NOT_DISC"
            elif bf[ch] <= tolerance[ch]:
                st = "OBS"
            elif bbit:
                st = "NOT_DISC"
            else:
                st = "OBS"
            out[(ch, k)] = (wbit, bbit, st)
    return out


def strict_per_bit(white, black):
    wf, bf = fields(white), fields(black)
    out = {}
    for ch, nbits in (("R", 5), ("G", 6), ("B", 5)):
        for k in range(nbits - 1, -1, -1):
            wbit = (wf[ch] >> k) & 1
            bbit = (bf[ch] >> k) & 1
            st = "OBS" if (wbit == 1 and bbit == 0) else "NOT_DISC"
            out[(ch, k)] = (wbit, bbit, st)
    return out


TOL = {ch: 8 >> (3 if ch in ("R", "B") else 2) for ch in ("R", "G", "B")}

for path in sys.argv[1:]:
    rows = sample(path)
    # 用 y=360 定白/黑段（与判定器一致）
    segs = rows[360]
    wi = max(range(8), key=lambda i: sum(segs[i]))
    bi = min(range(8), key=lambda i: sum(segs[i]))
    white, black = segs[wi], segs[bi]
    wf, bf = fields(white), fields(black)
    aligned = per_bit(white, black, TOL)
    strict = strict_per_bit(white, black)
    da = sum(1 for v in aligned.values() if v[2] == "OBS")
    ds = sum(1 for v in strict.values() if v[2] == "OBS")
    print("== %s ==" % os.path.basename(path))
    print("  white(R,G,B)@%d=%s  black@%d=%s" % (BAR_X[wi], white, BAR_X[bi], black))
    print("  white fields R/G/B=%d/%d/%d  black fields=%d/%d/%d"
          % (wf["R"], wf["G"], wf["B"], bf["R"], bf["G"], bf["B"]))
    print("  field bits total 5+6+5=%d ; structural 3+2+3=%d ; sum=%d"
          % (5 + 6 + 5, 3 + 2 + 3, 24))
    print("  aligned discriminated=%d/16 ; strict discriminated=%d/16" % (da, ds))
    print("  aligned NOT_DISC=%s" % sorted(k for k, v in aligned.items() if v[2] == "NOT_DISC"))
    print("  strict  NOT_DISC=%s" % sorted(k for k, v in strict.items() if v[2] == "NOT_DISC"))