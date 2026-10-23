#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reviewer 自造夹具（不调用被审脚本的构造函数）：
  D = 归档缺陷帧 + 两处缺位都恢复（蓝 bit7 |=0x80、绿 bit4 |=0x10）→ 模拟「硬件已修好」
  E = D 再把黑条(x=1200 整列)清零 → 隔离黑条残差对 C7 的影响
目的：检验判定器在「期望的良好」情形下能否给出 exit 0 / BIT_INTEGRITY_PASS。
"""
import os

WT = r"D:\codex-worktrees\dbdf"
SRC = os.path.join(WT, r"report\evidence\S3-T05\t05_color_msb_missing_20261022_r01\bars_raw_frame_full.bin")
OUT = os.path.dirname(os.path.abspath(__file__))
W, ROW = 1280, 1280 * 3

data = bytearray(open(SRC, "rb").read())
assert len(data) == 720 * ROW

d = bytearray(data)
for i in range(0, len(d) - 2, 3):
    d[i] |= 0x80      # 蓝 bit7（B5 bit4）
    d[i + 1] |= 0x10  # 绿 bit4（G6 bit2）
open(os.path.join(OUT, "fixture_D_fixed.bin"), "wb").write(bytes(d))

e = bytearray(d)
for y in range(720):
    base = y * ROW
    for x in range(1200, 1280):          # 黑条第 8 段（最后 80 像素）
        i = base + x * 3
        e[i] = e[i + 1] = e[i + 2] = 0
open(os.path.join(OUT, "fixture_E_fixed_black0.bin"), "wb").write(bytes(e))

print("fixture_D_fixed.bin bytes=%d" % len(d))
print("fixture_E_fixed_black0.bin bytes=%d" % len(e))
for x in (80, 1200):
    i = 360 * ROW + x * 3
    print("y=360 x=%d  D=(R,G,B)=(%d,%d,%d)  E=(%d,%d,%d)" % (
        x, d[i + 2], d[i + 1], d[i], e[i + 2], e[i + 1], e[i]))