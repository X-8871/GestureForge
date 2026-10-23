#!/usr/bin/env python3
"""Reviewer 自造夹具（独立于被审脚本，不复用其任何 helper）。

内存序 B,G,R；1280x720；彩条中心与判定器 BAR_X 一致。
模拟「两字节 MSB 同源同断」：蓝 MSB=B[4] -> 显示蓝字节 bit7；绿 MSB=G[2] -> 显示绿字节 bit4。
"""
import hashlib
import json
import os

WIDTH = 1280
ROW = WIDTH * 3
BAR_X = (80, 240, 400, 560, 720, 880, 1040, 1200)

# 8 段理想彩条（显示字节 R,G,B）。x=80 白条、x=1200 黑条。
BARS = [
    (248, 252, 248),   # 0 white (R,G,B)
    (248, 248, 16),
    (16, 248, 248),
    (16, 248, 16),
    (248, 16, 248),
    (248, 16, 16),
    (16, 16, 248),
    (0, 4, 0),         # 7 black
]


def seg_of(x):
    return min(range(len(BAR_X)), key=lambda i: abs(BAR_X[i] - x))


def build(mask_blue_msb=False, mask_green_msb=False):
    row = bytearray()
    for x in range(WIDTH):
        r, g, b = BARS[seg_of(x)]
        if mask_blue_msb:
            b &= 0x7F   # B[4] 丢失 -> 显示蓝 bit7 = 0
        if mask_green_msb:
            g &= 0xEF   # G[2] 丢失 -> 显示绿 bit4 = 0
        row += bytes((b, g, r))
    assert len(row) == ROW
    return bytes(row) * 720


out = {}
frames = {
    "ideal_repaired": build(),
    "defect_both_masked": build(mask_blue_msb=True, mask_green_msb=True),
    "partial_blue_only_restored": build(mask_green_msb=True),
    "repaired_black_residual_g2": None,  # 单独构造：白满量程，黑条 G 残差=2 字段值（8 显示）
    "repaired_black_residual_g3": None,  # 超容差：黑条 G 残差=3 字段值（12 显示）
}


def build_with_black(g_black_display):
    row = bytearray()
    for x in range(WIDTH):
        r, g, b = BARS[seg_of(x)]
        if seg_of(x) == 7:
            r, g, b = 0, g_black_display, 0
        row += bytes((b, g, r))
    return bytes(row) * 720


frames["repaired_black_residual_g2"] = build_with_black(8)    # 8>>2 = 2 = G 容差上限
frames["repaired_black_residual_g3"] = build_with_black(12)   # 12>>2 = 3 > 容差

base = os.path.dirname(os.path.abspath(__file__))
for name, data in frames.items():
    p = os.path.join(base, "myframe_%s.bin" % name)
    with open(p, "wb") as fh:
        fh.write(data)
    out[name] = {"path": p, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

with open(os.path.join(base, "my_fixtures.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))