#!/usr/bin/env python3
# 只读检查脚本 5：我自己独立实现「完成帧 = 第一个 (计数≥S02 且 (帧序−窗口首帧序)·P≥S01) 的帧」
# 与自检实现（ceil + max）对比；构造 5 个边界情形；生成我自己的扩展样例（保留原 31 例）。
import json, math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
EV = ISO + r"\blobs\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"


def literal(frames_wm, period, s01, s02):
    """逐帧显式扫描（与自检的 ceil/max 写法不同）。返回 (completion_index, span, m3)"""
    first = next((i for i, f in enumerate(frames_wm) if f), None)
    if first is None:
        return None, 0.0, False
    cnt = 0
    for i in range(first, len(frames_wm)):
        if frames_wm[i]:
            cnt += 1
        if cnt >= s02 and (i - first) * period >= s01:
            return i, (i - first) * period, True
    return None, 0.0, False


def checker(frames_wm, period, s01, s02):
    """自检写法（ceil(S01/P − 1e−9) 与计数帧取 max）"""
    idx = [i for i, f in enumerate(frames_wm) if f]
    if len(idx) < s02:
        return None, 0.0, False
    first = idx[0]
    count_index = idx[s02 - 1]
    dur = int(math.ceil(s01 / period - 1e-9)) if period > 0 else 0
    comp = max(count_index, first + dur)
    return comp, (comp - first) * period, comp <= len(frames_wm) - 1


scen = [
    ("A 30fps P=33.3ms 时长支配", [True] * 9, 33.3, 200, 6),
    ("B 恰好 200.0ms P=40ms 两条件同帧", [True] * 9, 40.0, 200, 6),
    ("C P=50ms 计数支配", [True] * 9, 50.0, 200, 6),
    ("D P=39.8ms 时长−1单位", [True] * 9, 39.8, 200, 6),
    ("E P=25ms 完成帧超出所给序列", [True] * 8, 25.0, 200, 6),
    ("F 10fps P=100ms（§15 表）", [True] * 9, 100.0, 200, 6),
    ("G 5fps P=200ms（§15 表）", [True] * 9, 200.0, 200, 6),
    ("H 计数不足（0 个 WM）", [False] * 9, 40.0, 200, 6),
]
print("=== 我的独立推演 vs 自检写法（P / S01 / S02 = 见行）===")
print(f"{'情形':<34}{'literal(idx,span,m3)':<34}{'checker(idx,span,m3)':<34}{'一致'}")
allok = True
for name, wm, p, s01, s02 in scen:
    a = literal(wm, p, s01, s02)
    b = checker(wm, p, s01, s02)
    ok = (a[0] == b[0]) and abs(a[1] - b[1]) < 1e-9 and a[2] == b[2]
    allok &= ok
    print(f"{name:<34}{str((a[0], round(a[1],4), a[2])):<34}{str((b[0], round(b[1],4), b[2])):<34}{ok}")
print("全部一致:", allok)
print()
print("=== 与文档 §15 表 / HC-06 / HC-29 / HC-31 对照 ===")
ref = {"30fps": ("第 8 帧", 233.1), "10fps": ("第 6 帧", 500.0), "5fps": ("第 6 帧", 1000.0)}
for key, (p, expect_frame, expect_ms) in {"30fps": (33.3, 8, 233.1), "10fps": (100.0, 6, 500.0),
                                          "5fps": (200.0, 6, 1000.0)}.items():
    idx, span, _ = literal([True] * 9, p, 200, 6)
    print(f"{key}: 我的完成帧=第 {idx+1} 帧, span={round(span,4)} ms | 文档 {ref[key][0]} {ref[key][1]} ms"
          f" | 一致={idx+1==expect_frame and abs(span-expect_ms)<1e-6}")
print("HC-06(P=33.3): 文档/入库 expected frames_required=8, actual_completion_ms=233.1 | 我="
      f"{literal([True]*9, 33.3, 200, 6)[0]+1}, {round(literal([True]*9,33.3,200,6)[1],4)}")
print("HC-29(P=40): 入库 expected completion_index=5, span=200.0, later_of=false | 我="
      f"{literal([True]*9,40.0,200,6)[0]}, {round(literal([True]*9,40.0,200,6)[1],4)}")
print("HC-31(P=33.3): 入库 expected completion_index=7, span=233.1, later_of=true | 我="
      f"{literal([True]*9,33.3,200,6)[0]}, {round(literal([True]*9,33.3,200,6)[1],4)}")
print()
print("=== 浮点边界探测：s01/P 恰为整数但浮点乘积下偏 ===")
for p, s01 in ((33.3, 99.9), (0.1, 0.3), (33.3, 200.0), (39.8, 199.0)):
    q = s01 / p
    dur = int(math.ceil(q - 1e-9))
    lit = next((i for i in range(0, 50) if i * p >= s01), None)
    print(f"P={p} S01={s01}: s01/P={q!r} ceil(.-1e-9)={dur} literal间隔数={lit} 一致={dur==lit}")
print()

# ---- 生成我的扩展样例（原 31 例 + 我自造的 5 例）----
base = json.load(open(EV + r"\hand_computed_cases.json", encoding="utf-8"))
mine_cases = []
p02, p03, p04, p05 = 0.3, 0.3, 0.15, 0.05
designs = [
    ("ZX-A-33.3", 33.3, 9), ("ZX-B-40.0", 40.0, 9), ("ZX-C-50.0", 50.0, 9),
    ("ZX-D-39.8", 39.8, 9), ("ZX-E-25.0", 25.0, 8),
]
for cid, period, nfr in designs:
    frames = [{"index": i + 1, "same_class": True, "iou": 0.6,
               "center_disp": round(0.025 + 0.005 * i, 4), "score": 0.9} for i in range(nfr)]
    wm = [True] * nfr
    idx, span, m3 = literal(wm, period, 200, 6)
    count_only_idx = 5 if nfr >= 6 else None
    count_only_span = (count_only_idx) * period if count_only_idx is not None else 0.0
    mine_cases.append({
        "case_id": cid,
        "topic": f"独立推演边界：P={period} ms（我自算，非抄自入库）",
        "recompute": {"kind": "window_match_vs_continues", "p02": p02, "p03": p03, "p04": p04,
                      "p05": p05, "s02_frames": 6, "s01_ms": 200, "period_ms": period,
                      "l01_frames": 5, "l02_ms": 300, "frames": frames},
        "derivation": "我的独立逐帧扫描推演",
        "expected": {
            "m3_fires": m3,
            "completion_index": idx if idx is not None else -1,
            "window_span_ms": round(span, 6),
            "later_of_applied": (idx is not None and idx > 5),
            "m3_fires_count_only": bool(count_only_idx is not None and count_only_span >= 200),
            "window_match_count": nfr,
            "continues_count": nfr,
            "lost": False,
            "trigger": False,
        },
    })
    print("我的自造样例", cid, "expected:", json.dumps(mine_cases[-1]["expected"], ensure_ascii=False))

ext = dict(base)
ext["cases"] = base["cases"] + mine_cases
ext["derivation_note"] = (str(base.get("derivation_note", "")) +
                          " 另含评审 r06 自造边界样例 ZX-A..ZX-E（Reviewer 独立推演）。")
out = ISO + r"\runs\my_extended_cases.json"
json.dump(ext, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n已写:", out, "样例数:", len(ext["cases"]))