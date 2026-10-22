#!/usr/bin/env python3
"""独立验证 M4 可达性（第 7 轮评审自推导；只读 r07 提交内的谓词定义/迁移条件/草案参数）。

序列（更贴近真实抖动场景）：
  帧 0 起：TARGET_CONTINUES 成立、score ≥ P02 → WINDOW_MATCH（累计 3 帧 < S02=6，故 M3 不完成）
  帧 3 起：same_class/IoU 仍成立 → TARGET_CONTINUES 继续成立（t_last_target_continues 每帧刷新），
           但 score < P02 → WINDOW_MATCH 不成立（窗口内中断，抖动计数累积）
  观察 M4（抖动耗尽 且 停留 ≥ S04）与 M10（连续 L01 帧 TARGET_CONTINUES 不成立 或 距锚点 ≥ L02）谁先命中。
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
W6 = r"D:\codex-worktrees\w6"


def blob(p):
    return subprocess.run(["git", "-C", W6, "cat-file", "blob", "bdcf896:" + p],
                          capture_output=True).stdout


data = json.loads(blob("docs/stage6/s6a_stage6_g0_behavior_v1.json").decode("utf-8"))
pm = {p["id"]: p.get("draft_value") for p in data["parameters"]}
s04, l01, l02, j01 = float(pm["T6-S04"]), int(pm["T6-L01"]), float(pm["T6-L02"]), int(pm["T6-J01"])
p02, p03, p04, c01 = float(pm["T6-P02"]), float(pm["T6-P03"]), float(pm["T6-P04"]), int(pm["T6-C01"])
print(f"草案参数：S04={s04} L01={l01} L02={l02} J01={j01} P02={p02} P03={p03} P04={p04} C01={c01}")
for period in (100.0, 40.0, 33.3):
    frames = [(0.9, 0.60), (0.9, 0.60), (0.9, 0.60)] + [(0.28, 0.60)] * 40
    dwell = streak = anchor_age = jitter = 0
    m1 = m3 = m4 = m10 = None
    wm_count = 0
    for idx, (score, iou) in enumerate(frames):
        dwell = idx * period
        continues = iou >= p03                     # 同类别 + IoU ≥ P03 → TARGET_CONTINUES
        wm = continues and score >= p02            # WINDOW_MATCH 另需 score ≥ P02
        wm_count += 1 if wm else 0
        if wm_count >= c01 and m1 is None:
            m1 = idx
        if wm_count >= 6 and (idx * period) >= 200 and m3 is None:
            m3 = idx
        if continues:
            streak, anchor_age = 0, 0.0
        else:
            streak += 1
            anchor_age += period
        jitter = 0 if wm else jitter + 1
        if m10 is None and (streak >= l01 or anchor_age >= l02):
            m10 = idx
        if m4 is None and jitter > j01 and dwell >= s04:
            m4 = idx
        if m4 is not None:
            break
    print(f"P={period} ms：M1@{m1}  M3={'未完成' if m3 is None else m3}  "
          f"M4@{m4}({m4 * period:.1f} ms，dwell≥S04 且 jitter={jitter}>J01)  "
          f"M10={'始终未命中' if m10 is None else m10}  → M4 可达 = {m4 is not None}")