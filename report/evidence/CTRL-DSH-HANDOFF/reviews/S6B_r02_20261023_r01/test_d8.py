#!/usr/bin/env python3
"""S6-B r02 复审：N-08/D8 前提核验——IDLE 是否可能仍持有 current_target。"""
from __future__ import annotations

import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
sys.path.insert(0, str(ISO))
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

PACK = ParamPack(ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=ISO)
core = GestureInteractionCore(PACK)
A = [0.20, 0.20, 0.60, 0.60]
events = [
    {"kind": "E_FRAME_RESULT", "frame_id": 1, "state": "OK",
     "detections": [{"class_id": 0, "score": 0.9, "xyxy": A, "source_order": 0}], "t_input_ns": 0},
]
t = 0
for k in range(4):
    t += 200_000_000
    events.append({"kind": "E_TICK", "t_input_ns": t})

for index, event in enumerate(events):
    event.setdefault("session_id", "s1")
    step = core.step(event)
    log = step["log"]
    print(f"  ev{index} kind={log['event_kind']:18s} t={event['t_input_ns']/1e6:6.0f}ms "
          f"state={core.state:9s} current_target={'SET' if core.current_target else 'None'} "
          f"t_last_continues={core.t_last_target_continues_ns} transition={log['transition']}")
print("IDLE_WITH_TARGET_OBSERVED:", any(True for _ in [0]) and core.current_target is not None
      and core.state == "IDLE")