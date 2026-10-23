#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立复算（Reviewer 自写，不调用被审脚本）：直接从归档原始帧二进制复算判定表数值。

输入：
  A report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin （彩条 8 段缺陷帧）
  B .../pose1_frame_full.bin / pose2 / colpose1 （真实场景帧，用于旧签名置位率复算）
  C report/evidence/S3-T05/t05_msb_line_diagnosis_20261021_r01/（19 行样本，签名置位率来源）

输出：stdout 文本 + JSON（本评审目录内）。
"""
import hashlib
import json
import os
import sys

WT = r"D:\codex-worktrees\dbdf"
WIDTH = 1280
ROW = WIDTH * 3
BAR_X = (80, 240, 400, 560, 720, 880, 1040, 1200)
OUT = os.path.dirname(os.path.abspath(__file__))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def row_of(data, y):
    return data[y * ROW:(y + 1) * ROW]


def bars_of(chunk):
    out = []
    for x in BAR_X:
        i = x * 3
        b, g, r = chunk[i], chunk[i + 1], chunk[i + 2]  # 内存序 B,G,R
        out.append({"x": x, "R": r, "G": g, "B": b,
                    "R5": r >> 3, "G6": g >> 2, "B5": b >> 3})
    return out


def sig_of(chunk):
    blue = chunk[0::3]
    green = chunk[1::3]
    return {"px": len(blue),
            "blue_bit7_set": sum(1 for v in blue if v & 0x80),
            "green_bit4_set": sum(1 for v in green if v & 0x10),
            "maxB": max(blue), "maxG": max(green), "maxR": max(chunk[2::3])}


def field_bits(white, black):
    """按 RGB565 有效字段位复算逐位可辨数（我自己实现，不用被审脚本）。"""
    res = []
    for ch, n, wk, bk in (("R", 5, "R5", "R5"), ("G", 6, "G6", "G6"), ("B", 5, "B5", "B5")):
        for k in range(n - 1, -1, -1):
            w = (white[wk] >> k) & 1
            b = (black[bk] >> k) & 1
            res.append({"ch": ch, "field_bit": k,
                        "display_bit": k + (3 if ch in "RB" else 2),
                        "white_bit": w, "black_bit": b,
                        "discriminated": (w == 1 and b == 0)})
    return res


report = {"independent_recompute": True, "by": "reviewer", "files": {}}

# ---------- A 彩条缺陷帧 ----------
p = os.path.join(WT, "report/evidence/S3-T05/t05_color_msb_missing_20261022_r01/bars_raw_frame_full.bin")
data = open(p, "rb").read()
report["files"]["bars_raw_frame_full.bin"] = {"sha256": sha256(p), "bytes": len(data),
                                              "rows_expected": len(data) // ROW}
per_row = {}
for y in (200, 360, 500):
    per_row[y] = bars_of(row_of(data, y))
report["bars_by_row"] = {str(k): v for k, v in per_row.items()}
# 判定器口径：判读行优先 y=360，白=max(R+G+B)，黑=min(R+G+B)
segs = per_row[360]
white = max(segs, key=lambda s: s["R"] + s["G"] + s["B"])
black = min(segs, key=lambda s: s["R"] + s["G"] + s["B"])
report["judge_row_360_white"] = white
report["judge_row_360_black"] = black
report["white_all_rows_same"] = all(per_row[y][0]["R"] == 248 and per_row[y][0]["G"] == 236
                                    and per_row[y][0]["B"] == 120 for y in (200, 360, 500))
report["black_all_rows_same"] = all(per_row[y][7]["R"] == 0 and per_row[y][7]["G"] == 4
                                    and per_row[y][7]["B"] == 0 for y in (200, 360, 500))

# 我自算的判定项
w, b = white, black
report["my_criteria"] = {
    "C1_R>=240": w["R"] >= 240, "C2_G>=248": w["G"] >= 248, "C3_B>=240": w["B"] >= 240,
    "C4_three_diffs<=8": all(abs(x - y) <= 8 for x, y in
                             ((w["R"], w["G"]), (w["G"], w["B"]), (w["R"], w["B"]))),
    "C5_black_R0_G<=8_B<=8": (b["R"] == 0 and b["G"] <= 8 and b["B"] <= 8),
}
bits = field_bits(w, b)
report["my_field_bits"] = bits
report["my_c7_discriminated"] = sum(1 for i in bits if i["discriminated"])
report["my_c7_total_field_bits"] = len(bits)
report["my_c7_lost_field_bits"] = [f'{i["ch"]}6/5 bit{i["field_bit"]}' for i in bits
                                   if not i["discriminated"]]
report["fill_bits_R_B_low3_G_low2"] = 3 + 3 + 2

# ---------- B 真实场景帧：旧签名置位率 ----------
for name in ("pose1_frame_full.bin", "pose2_frame_full.bin", "colpose1_frame_full.bin"):
    fp = os.path.join(WT, "report/evidence/S3-T05/t05_color_msb_missing_20261022_r01", name)
    d = open(fp, "rb").read()
    agg = {"px": 0, "blue_bit7_set": 0, "green_bit4_set": 0, "maxB": 0, "maxG": 0, "maxR": 0}
    for y in (200, 360, 500):
        s = sig_of(row_of(d, y))
        agg["px"] += s["px"]
        agg["blue_bit7_set"] += s["blue_bit7_set"]
        agg["green_bit4_set"] += s["green_bit4_set"]
        agg["maxB"] = max(agg["maxB"], s["maxB"])
        agg["maxG"] = max(agg["maxG"], s["maxG"])
        agg["maxR"] = max(agg["maxR"], s["maxR"])
    agg["blue_bit7_set_rate_pct"] = 100.0 * agg["blue_bit7_set"] / agg["px"]
    agg["green_bit4_set_rate_pct"] = 100.0 * agg["green_bit4_set"] / agg["px"]
    agg["sha256"] = sha256(fp)
    report["files"][name] = {"sha256": agg["sha256"], "bytes": len(d)}
    report.setdefault("scene_frames_signature_3rows", {})[name] = agg

# ---------- C 归档 19 行样本签名 ----------
d19 = os.path.join(WT, "report/evidence/S3-T05/t05_msb_line_diagnosis_20261021_r01")
report["msb_line_diagnosis_dir"] = sorted(os.listdir(d19))
report["msb_signature_scan_txt"] = open(os.path.join(d19, "msb_signature_scan.txt"),
                                        encoding="utf-8", errors="replace").read()

with open(os.path.join(OUT, "recompute_judgement_myself.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)

print("白色段(y=360,max sum):", w)
print("黑色段(y=360,min sum):", b)
print("三行白/黑一致:", report["white_all_rows_same"], report["black_all_rows_same"])
print("我自算判定项:", json.dumps(report["my_criteria"], ensure_ascii=False))
print("字段位可辨: %d/%d  丢失=%s" % (report["my_c7_discriminated"], report["my_c7_total_field_bits"],
                                     report["my_c7_lost_field_bits"]))
print("结构性填充低位合计 =", report["fill_bits_R_B_low3_G_low2"])
for k, v in report.get("scene_frames_signature_3rows", {}).items():
    print("%s: px=%d blue_set=%d(%.4f%%) green_set=%d(%.4f%%) maxR/G/B=%d/%d/%d" % (
        k, v["px"], v["blue_bit7_set"], v["blue_bit7_set_rate_pct"],
        v["green_bit4_set"], v["green_bit4_set_rate_pct"], v["maxR"], v["maxG"], v["maxB"]))