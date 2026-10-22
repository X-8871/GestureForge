#!/usr/bin/env python3
"""S6-B r02 复审：M4 机制的逐帧轨迹与三种路径判别。"""
from __future__ import annotations

import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
sys.path.insert(0, str(ISO))
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

PACK = ParamPack(ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=ISO)
TH = PACK.threshold_bundle()
A = [0.20, 0.20, 0.60, 0.60]
A2 = [0.30, 0.20, 0.70, 0.60]   # 中心位移 0.10（> P05=0.05，≤ P04=0.15）


def trace(label, plan, session="s1"):
    print(f"\n=== {label} ===")
    core = GestureInteractionCore(PACK)
    t = 0
    for index, (box, score, dt) in enumerate(plan):
        t += int(dt)
        event = {"kind": "E_FRAME_RESULT", "frame_id": index + 1, "state": "OK",
                 "detections": [{"class_id": 0, "score": score, "xyxy": list(box), "source_order": 0}],
                 "t_input_ns": t, "session_id": session}
        step = core.step(event)
        log = step["log"]
        print(f"  f{index+1} t={t/1e6:7.1f}ms score={score:.2f} box={'A2' if box is A2 else 'A '} "
              f"sel={'Y' if log.get('window_advance') and core.current_target else '-'} "
              f"wm={log.get('window_match')} wmc={core.window_match_count} "
              f"jit={core.jitter_frames} exh={getattr(core,'jitter_exhausted',None)} "
              f"cstr={core.candidate_streak} dwell={None if core.candidate_dwell_start_ns is None else core.candidate_dwell_start_ns/1e6} "
              f"miss={core.continues_false_streak} tlast={None if core.t_last_target_continues_ns is None else core.t_last_target_continues_ns/1e6} "
              f"-> {core.state} {log.get('transition') or ''}")
    return core


# 路径 1：5 帧高分 + 2 帧低于 P01（C4-jitter-reset 同构，但缩短到刚好判别）
trace("路径1 低分(<P01)两帧（C4 同构）", [(A, 0.90, 0), (A, 0.90, 1e8), (A, 0.90, 1e8),
                                            (A, 0.90, 1e8), (A, 0.90, 1e8), (A, 0.28, 1e8),
                                            (A, 0.28, 1e8)])

# 路径 2：位移中断但 TARGET_CONTINUES 成立（A2 起步，之后持续 A）
plan = [(A2, 0.90, 0)] + [(A, 0.90, 1e8)] * 7
core = trace("路径2 位移中断(>P05) 且 TARGET_CONTINUES 成立", plan)
print("  -> M10 是否出现:", "M10" in [])

# 路径 3：score 落在 [P02, P01) 区间是否存在（P01 vs P02）
print(f"\n=== 路径3 低分带检查 ===\n  P01={TH['p01']} P02={TH['p02']} "
      f"→ 区间 [P02,P01) 是否非空: {TH['p02'] < TH['p01']}")

# 路径 4：低于 P01 连续 5 帧（L01）与 300ms（L02）——哪个先到
plan = [(A, 0.90, 0), (A, 0.90, 1e8)] + [(A, 0.10, 1e8)] * 6
trace("路径4 低于 P01 连续 6 帧（观察 M4 与 M10 竞争）", plan)