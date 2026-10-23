#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reviewer 夹具 F：**判定表自己声明的「已修好」情形**
  白条 = (248,252,248)（表内 if_fixed），黑条 = (0,4,0)（表内 if_fixed 亦为 0,4,0）
  做法：归档缺陷帧 → 其余段恢复两处缺位（蓝 bit7|=0x80、绿 bit4|=0x10），
        黑条（x=1200..1279）保持归档原值 (0,4,0) 不变。
目的：判定表称此情形应 C1..C7 全通过（exit 0）；实测检验可满足性。
"""
import os

WT = r"D:\codex-worktrees\dbdf"
SRC = os.path.join(WT, r"report\evidence\S3-T05\t05_color_msb_missing_20261022_r01\bars_raw_frame_full.bin")
OUT = os.path.dirname(os.path.abspath(__file__))
W, ROW = 1280, 1280 * 3

orig = open(SRC, "rb").read()
d = bytearray(orig)
for y in range(720):
    base = y * ROW
    for x in range(0, 1200):             # 黑条以外的所有段
        i = base + x * 3
        d[i] |= 0x80
        d[i + 1] |= 0x10
open(os.path.join(OUT, "fixture_F_fixed_black_residual.bin"), "wb").write(bytes(d))

for x in (80, 240, 1200):
    i = 360 * ROW + x * 3
    print("y=360 x=%4d  归档=(R,G,B)=(%3d,%3d,%3d)  F=(%3d,%3d,%3d)" % (
        x, orig[i + 2], orig[i + 1], orig[i], d[i + 2], d[i + 1], d[i]))