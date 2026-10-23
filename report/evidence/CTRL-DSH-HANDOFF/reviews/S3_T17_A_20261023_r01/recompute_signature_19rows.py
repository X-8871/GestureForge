#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reviewer 独立复算「旧签名 0.000%/0.000%、19 样本、24,320 像素」：
自行按归档扫描表列出的 19 个行样本重算蓝 bit7 / 绿 bit4 置位率（不用被审脚本）。"""
import os
import re

WT = r"D:\codex-worktrees\dbdf"
SCAN = os.path.join(WT, r"report\evidence\S3-T05\t05_msb_line_diagnosis_20261021_r01\msb_signature_scan.txt")

# 目录索引
index = {}
for root in (os.path.join(WT, "report", "evidence"), os.path.join(WT, "tmp")):
    for dp, _d, names in os.walk(root):
        for n in names:
            index.setdefault(n, []).append(os.path.join(dp, n))

rows = []
for line in open(SCAN, encoding="utf-8", errors="replace").read().splitlines():
    if not line.strip() or line.startswith("file ") or line.startswith("---") or "扫描文件=" in line:
        continue
    parts = line.split()
    if len(parts) < 5:
        continue
    shown, npx, maxB, b7, g4 = parts[0], int(parts[1]), int(parts[2]), parts[3], parts[4]
    base = os.path.basename(shown)
    cands = index.get(base, [])
    # 用被截断的路径尾串校验
    tail = shown.split("/", 1)[-1] if "/" in shown else shown
    # 只接受「相对路径以扫描表所示字符串结尾」的候选（避免同名文件误配）
    hit = None
    for c in cands:
        rel = os.path.relpath(c, WT).replace("\\", "/")
        if rel.endswith(shown.replace("\\", "/")):
            hit = c
            break
    if hit is None:
        rows.append((shown, None, npx, maxB, b7, g4))
        continue
    d = open(hit, "rb").read()
    n = len(d) // 3
    blue = d[0::3]
    green = d[1::3]
    my_b7 = 100.0 * sum(1 for v in blue if v & 0x80) / n
    my_g4 = 100.0 * sum(1 for v in green if v & 0x10) / n
    rows.append((os.path.relpath(hit, WT), n, max(blue), f"{my_b7:.3f}%", f"{my_g4:.3f}%"))

tot = 0
bad = 0
print("%-58s %6s %6s %10s %10s" % ("我复算的文件", "npx", "maxB", "B.bit7=1", "G.bit4=1"))
for shown, n, maxB, b7, g4 in rows:
    mark = ""
    if n is None:
        mark = "  <未找到: %s>" % shown
        bad += 1
    else:
        tot += n
        if b7 != "0.000%" or g4 != "0.000%":
            mark = "  <非零!>"
    print("%-58s %6s %6s %10s %10s%s" % (str(shown)[-58:], n, maxB, b7, g4, mark))
print("-" * 100)
print("样本数=%d（含未找到 %d）；总像素=%d" % (len(rows), bad, tot))
print("我复算的最大置位率 = %s / %s" % (
    max((r[3] for r in rows if r[1] is not None), default="n/a"),
    max((r[4] for r in rows if r[1] is not None), default="n/a")))
print("归档扫描表声明 = 19 样本 / 24320 像素 / 0.000% / 0.000%")