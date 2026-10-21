#!/usr/bin/env python3
"""S3-T05：按已有帧缓冲转储检验「DVP 字节 MSB 缺失」签名（只读，无需上板）。

依据（2026-10-21 Codex 更正 + 本脚本复核）：
- 帧缓冲内存字节序 offset0/1/2 = B/G/R；
- 16 位输入字 = {第一字节, 第二字节}，第一字节 = {g[2:0], b[4:0]}，第二字节 = {r[4:0], g[5:3]}；
- 两个字节的 MSB 都来自同一条 DVP 数据线（厂商 IP 取 cmos_d[9:2]，故 MSB = cmos_d[9]）；
- 该线若无信号，则同时且必然造成：
    · 蓝 8 位 bit7 恒 0（B[4] 丢失，因 B[4] = 第一字节 MSB → 字 bit15）
    · 绿 8 位 bit4 恒 0（G[2] 丢失，因 G[2] = 第二字节 MSB → 字 bit7）

用法：python analyze_missing_msb_signature.py <row*.bin>...
输出：每行文件的像素数、蓝 bit7 置位率、绿 bit4 置位率，以及总体判定。
"""
import glob
import os
import sys


def scan(path):
    data = open(path, "rb").read()
    if len(data) % 3:
        return None
    n = len(data) // 3
    blue = data[0::3]
    green = data[1::3]
    return {
        "n": n,
        "maxB": max(blue) if n else None,
        "blue_bit7": sum(1 for v in blue if v & 0x80) / n if n else 0.0,
        "green_bit4": sum(1 for v in green if v & 0x10) / n if n else 0.0,
    }


def main(argv):
    files = []
    for arg in argv:
        files.extend(sorted(glob.glob(arg)) if any(c in arg for c in "*?[") else [arg])
    if not files:
        print("用法: python analyze_missing_msb_signature.py <row*.bin>...")
        return 2
    print("%-58s %6s %6s %11s %11s" % ("file", "npx", "maxB", "B.bit7=1", "G.bit4=1"))
    worst_b = worst_g = 0.0
    ok = 0
    for path in files:
        r = scan(path)
        if r is None:
            print("%-58s  跳过（长度非 3 的倍数）" % os.path.basename(path))
            continue
        worst_b = max(worst_b, r["blue_bit7"])
        worst_g = max(worst_g, r["green_bit4"])
        ok += 1
        print("%-58s %6d %6s %10.3f%% %10.3f%%" % (
            path.replace(os.sep, "/")[-58:], r["n"], r["maxB"],
            100 * r["blue_bit7"], 100 * r["green_bit4"]))
    print("-" * 104)
    print("扫描文件=%d；最大蓝 bit7 置位率=%.3f%%；最大绿 bit4 置位率=%.3f%%" % (ok, 100 * worst_b, 100 * worst_g))
    verdict = (worst_b == 0.0 and worst_g == 0.0)
    print("判定：%s" % ("符合『两个字节 MSB 同时恒 0』签名（单一数据线无信号）" if verdict
                      else "不符合该签名，需重新检查通道映射与样本"))
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))