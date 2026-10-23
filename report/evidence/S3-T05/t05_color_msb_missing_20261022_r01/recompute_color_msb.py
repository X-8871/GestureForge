"""复算脚本：彩条帧的 8 段数值 + “两字节 MSB 同时丢失”签名检查。

用法: python recompute_color_msb.py <frame_full.bin>
内存序为 B,G,R（每像素 3 字节，1280x720）。第三方独立复算脚本可并列引用本文件。
"""
import sys

X = (80, 240, 400, 560, 720, 880, 1040, 1200)
BIN = sys.argv[1]
d = open(BIN, "rb").read()
for y in (200, 360, 500):
    row = d[y * 1280 * 3:(y + 1) * 1280 * 3]
    for x in X:
        i = x * 3
        b, g, r = row[i], row[i + 1], row[i + 2]
        print("y=%d x=%4d asis(R,G,B)=%3d,%3d,%3d rb_swap=%3d,%3d,%3d" % (y, x, r, g, b, b, g, r))

# 缺位签名：白条 5 位蓝应=15（120），绿 6 位应=59（236）；真值应为 31（255）与 63（252）。
row = d[360 * 1280 * 3:361 * 1280 * 3]
b, g, r = row[80 * 3], row[80 * 3 + 1], row[80 * 3 + 2]
print("VERDICT_B5=%d (expect 15 if blue MSB lost, 31 if intact)" % (b >> 3))
print("VERDICT_G6=%d (expect 59 if green bit2 lost, 63 if intact)" % (g >> 2))
