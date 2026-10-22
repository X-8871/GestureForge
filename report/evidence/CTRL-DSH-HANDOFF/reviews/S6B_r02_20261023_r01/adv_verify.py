#!/usr/bin/env python3
"""S6-B r02 复审：自立验证（M4 可达、acquisition_id 规则、C6b 旧行为反例）。

只读 iso 副本内的实现，不写被审工作树。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\iso")
sys.path.insert(0, str(ISO))
from src.stage6.s6_actions import ActionLayer, OutcomePolicy  # noqa: E402
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

PACK = ParamPack(ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=ISO)
TH = PACK.threshold_bundle()
print("thresholds:", {k: TH[k] for k in ("c01_frames", "s01_ns", "s02_frames", "s04_ns",
                                          "l01_frames", "l02_ns", "k01_ns", "j01_frames",
                                          "p01", "p02", "p03", "p04", "p05", "u00_w", "u00_n")})

A = [0.20, 0.20, 0.60, 0.60]


def det(score, cid=0, box=A):
    return [{"class_id": cid, "score": score, "xyxy": list(box), "source_order": 0}]


def drive(events, policy=None, session="s1"):
    core = GestureInteractionCore(PACK)
    layer = ActionLayer(PACK, policy or OutcomePolicy())
    t = 0
    transitions = []
    requests = []
    acq_seen = []
    for index, raw in enumerate(events):
        if "dt_ns" in raw:
            t += int(raw["dt_ns"])
        else:
            t = int(raw.get("t_ns", t))
        event = dict(raw)
        event.pop("dt_ns", None)
        event.pop("t_ns", None)
        event["t_input_ns"] = t
        event.setdefault("session_id", session)
        step = core.step(event)
        if step["log"].get("transition"):
            transitions.append((index + 1, step["log"]["transition"], step["log"]["to_state"]))
        request = step["action_request"]
        if request is not None:
            requests.append({"frame": event.get("frame_id"), "acq": request.get("acquisition_id"),
                             "action_type": request["action_type"], "target_id": request["target_id"],
                             "t_trigger_ns": request.get("t_trigger_ns")})
            acq_seen.append(core.acquisition_id)
            record = layer.submit(request, t)
            core.note_action_ack(record)
        if step["log"].get("counters"):
            pass
    return core, layer, transitions, requests


# ---------------------------------------------------------------- 1) M4 可达性（自构造序列）
print("\n=== 1) M4 自构造序列：6 帧低分（score<P02、几何连续）===")
events = []
for fid in range(1, 7):
    events.append({"kind": "E_FRAME_RESULT", "frame_id": fid, "state": "OK",
                   "dt_ns": 0 if fid == 1 else 100_000_000, "detections": det(0.28)})
core, layer, transitions, requests = drive(events)
print("transitions:", transitions)
print("final_state:", core.state, "action_submitted:", layer.summary()["action_submitted"])
m4 = any(mid == "M4" for _, mid, _ in transitions)
print("M4_REACHABLE_SELF_CONSTRUCTED:", m4)

# ---------------------------------------------------------------- 2) 同帧 M4/M10 竞争（M10 优先）
print("\n=== 2) 同帧 M4/M10 竞争：先长时间停留（miss_streak 累积）再看谁先命中 ===")
events = [{"kind": "E_FRAME_RESULT", "frame_id": 1, "state": "OK", "dt_ns": 0, "detections": det(0.9)}]
for fid in range(2, 5):
    events.append({"kind": "E_FRAME_RESULT", "frame_id": fid, "state": "OK", "dt_ns": 100_000_000,
                   "detections": det(0.9)})
# 之后 3 帧低于 P01（TARGET_CONTINUES 不成立 → continues_false_streak 累积）
for fid in range(5, 8):
    events.append({"kind": "E_FRAME_RESULT", "frame_id": fid, "state": "OK", "dt_ns": 100_000_000,
                   "detections": det(0.10)})
core, layer, transitions, requests = drive(events)
print("transitions:", transitions, "final:", core.state)

# ---------------------------------------------------------------- 3) C4-jitter-reset 提交日志复核
print("\n=== 3) 证据包 C4-jitter-reset 日志中的 M4 ===")
log_path = ISO / "report/evidence/S6-B/s6b_core_20261023_r02/logs/C4-jitter-reset.jsonl"
for line in log_path.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    if row.get("transition"):
        print("  frame", row.get("frame_id"), "->", row["transition"], row.get("to_state"),
              "|", (row.get("reason") or "")[:70])

# ---------------------------------------------------------------- 4) acquisition_id 规则实测
print("\n=== 4) acquisition_id 递增规则（C3 两次获取）===")
cases = json.loads((ISO / "report/evidence/S6-B/s6b_core_20261023_r02/cases/case_matrix.json")
                   .read_text(encoding="utf-8"))
c3 = next(c for c in cases["cases"] if c["case_id"] == "C3-lost-then-reappear")
core, layer, transitions, requests = drive(c3["events"])
print("transitions:", transitions)
print("action requests:", requests)
print("distinct acquisition_id over two acquisitions:", sorted({r["acq"] for r in requests}))

# 追加：目标切换获取（C5-target-jump）与 M4 结束获取后再获取
print("\n=== 4b) 目标切换后的 acquisition_id ===")
c5 = next(c for c in cases["cases"] if c["case_id"] == "C5-target-jump")
core, layer, transitions, requests = drive(c5["events"])
print("transitions:", transitions, "requests:", requests)

print("\n=== 4c) M4 结束一次获取后重新获取的 acquisition_id ===")
events = []
for fid in range(1, 8):
    events.append({"kind": "E_FRAME_RESULT", "frame_id": fid, "state": "OK",
                   "dt_ns": 0 if fid == 1 else 100_000_000,
                   "detections": det(0.28 if fid >= 6 else 0.9)})
# f6/f7 低分重演 M4；随后重新给稳定高分序列，观察新获取的 id
for fid in range(8, 16):
    events.append({"kind": "E_FRAME_RESULT", "frame_id": fid, "state": "OK", "dt_ns": 100_000_000,
                   "detections": det(0.9)})
core, layer, transitions, requests = drive(events)
print("transitions:", transitions)
print("requests:", requests)