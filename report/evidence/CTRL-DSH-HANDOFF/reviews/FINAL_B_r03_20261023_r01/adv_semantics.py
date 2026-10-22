"""S6-B 语义对抗测试（独立推导期望；只读 clone 内 src；不写被审工作树）。

运行：python -B adv_semantics.py <clone_root>
"""
from __future__ import annotations
import json, sys
from pathlib import Path

CLONE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent / "clone_e3b"
sys.path.insert(0, str(CLONE))
sys.stdout.reconfigure(encoding="utf-8")
from src.stage6.s6_actions import ActionLayer, OutcomePolicy  # noqa: E402
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

PACK = ParamPack(CLONE / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=CLONE)
TH = PACK.threshold_bundle()
MS = 1_000_000
print("阈值：", {k: v for k, v in TH.items() if k != "class_ids"})

RESULTS = []


def check(name, got, want, extra=""):
    ok = got == want
    RESULTS.append((name, ok, got, want, extra))
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got={got!r} want={want!r} {extra}")


def det(cls, score, box, order=0):
    return {"class_id": cls, "score": score, "xyxy": list(box), "source_order": order}


BOX = [0.30, 0.30, 0.50, 0.50]          # 中心 (0.40,0.40)


def run(events, session="s1", t0=0):
    core = GestureInteractionCore(PACK)
    layer = ActionLayer(PACK)
    logs, actions, t = [], [], t0
    for i, ev in enumerate(events):
        if "t" in ev:
            t = ev["t"]
        e = {k: v for k, v in ev.items() if k != "t"}
        e["t_input_ns"] = t
        e.setdefault("session_id", session)
        st = core.step(e)
        log = st["log"]
        log["t_input_ns"] = t
        logs.append(log)
        actions.append(None)
        if st["action_request"]:
            rec = layer.submit(st["action_request"], t)
            ack = core.note_action_ack(rec)
            actions[-1] = rec
    return core, layer, logs, actions, t


def frames(spec, start=0, period=100 * MS, state="OK", dets=None, kind="E_FRAME_RESULT"):
    """spec: 帧数；返回逐帧事件（frame_id 从 1 起）。"""
    out = []
    for i in range(spec):
        out.append({"kind": kind, "frame_id": i + 1, "t": start + i * period,
                    "state": state, "detections": (dets(i) if callable(dets) else (dets or []))})
    return out


# ---------------------------------------------------------------- A) 零框 NO_HAND
ev = frames(8, period=100 * MS, state="NO_HAND", dets=[])
core, layer, logs, acts, _ = run(ev)
check("A1 零框 8 帧 final_state", core.state, "IDLE")
check("A2 零框 transitions", [l["transition"] for l in logs if l["transition"]], [])
check("A3 零框 no_hand_frames", core.counters["no_hand_frames"], 8)
check("A4 零框 action_submitted", layer.summary()["action_submitted"], 0)
check("A5 零框 window_match_count", core.window_match_count, 0)

# ---------------------------------------------------------------- B) 跨目标全局冷却门
ev = frames(6, period=100 * MS, state="OK", dets=[det(0, 0.9, BOX)])
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK",
           "detections": [det(0, 0.9, BOX)]})                    # M5 触发 @600ms
BOX_B = [0.60, 0.60, 0.80, 0.80]                                 # 不同类别+不同位置 → 切换
for k in range(8, 18):                                           # 700..1600ms
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": k, "t": k * 100 * MS,
               "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
core, layer, logs, acts, _ = run(ev)
subs = [(a["t_submit_ns"], a["action_type"], a["acquisition_id"]) for a in acts if a]
check("B1 两次提交（跨目标）", len(subs), 2)
check("B2 第二次提交时刻 >= t_last_submit+K01", subs[1][0] - subs[0][0] >= TH["k01_ns"], True,
      f"delta={subs[1][0] - subs[0][0]} ns")
check("B3 第二次提交 acquisition_id", subs[1][2], 1)
check("B4 门开前无提前提交（第 2 次提交在门开之后）",
      subs[1][0] - subs[0][0] >= TH["k01_ns"] and len(subs) == 2, True,
      f"states={[l.get('transition') for l in logs if l.get('transition')]}")
check("B5 第一次提交在 600ms", subs[0][0], 600 * MS)

# ---------------------------------------------------------------- C) 门开启帧为非推进帧 → 不触发
ev = frames(6, period=100 * MS, state="OK", dets=[det(0, 0.9, BOX)])
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK",
           "detections": [det(0, 0.9, BOX)]})                    # 触发 @600
for k in range(8, 17):                                           # 700..1500 切换目标并稳定
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": k, "t": k * 100 * MS,
               "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
ev.append({"kind": "E_FRAME_TIMEOUT", "frame_id": 17, "t": 1600 * MS})   # 门恰在非推进帧开启
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 18, "t": 1610 * MS, "state": "OK",
           "detections": [det(1, 0.9, BOX_B)]})                  # 下一条推进帧才可触发
core, layer, logs, acts, _ = run(ev)
subs = [(a["t_submit_ns"], a["acquisition_id"]) for a in acts if a]
check("C1 TIMEOUT 帧不触发（提交仍在 1610ms）", [s[0] for s in subs], [600 * MS, 1610 * MS])

# ---------------------------------------------------------------- D) K01 边界 ±1ns
# 构造：首次触发锁门后，用异常→M2/M12 回到 IDLE（此时门仍锁），再让新目标在 CANDIDATE
# 内完成窗口进入 STABLE（门仍锁）→ M5 被 H-10 抑制 → 恰在 K01 的推进帧才允许触发。
ev = frames(6, period=100 * MS, state="OK", dets=[det(0, 0.9, BOX)])
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK",
           "detections": [det(0, 0.9, BOX)]})                       # 触发 @600ms（t_last_submit）
for i, tm in enumerate((610 * MS, 620 * MS, 630 * MS)):
    ev.append({"kind": "E_FRAME_ERROR", "frame_id": 8 + i, "t": tm})   # 3 异常 → M2
for i in range(5):                                                  # 5 合法 → M12 → IDLE
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": 11 + i, "t": 640 * MS + i * 10 * MS,
               "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
for i in range(6):                                                  # 700..1200 新目标窗口 → M3
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": 16 + i, "t": 700 * MS + i * 100 * MS,
               "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
for i, tm in enumerate((1300 * MS, 1400 * MS, 1500 * MS, 1600 * MS - 1, 1600 * MS)):
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": 22 + i, "t": tm,
               "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
core, layer, logs, acts, _ = run(ev)
subs = [(a["t_submit_ns"], a["acquisition_id"]) for a in acts if a]
check("D1 K01-1ns 不触发、=K01 触发", [s[0] for s in subs], [600 * MS, 1600 * MS],
      f"transitions={[l['transition'] for l in logs if l['transition']]}")
check("D2 新获取 id（B11/D7 推导：新获取应为新 id）", [s[1] for s in subs], [0, 1],
      "← 本项为对抗发现：M2/M12 结束获取但不递增 acquisition_id")
check("D3 K01-1ns 帧被 S_COOLDOWN 抑制",
      any("S_COOLDOWN" in (l.get("suppression_events") or []) for l in logs), True,
      f"suppressions={core.suppressions}")

# ---------------------------------------------------------------- E) L02 边界 ±1ns
ev = [{"kind": "E_FRAME_RESULT", "frame_id": 1, "t": 0, "state": "OK", "detections": [det(0, 0.9, BOX)]},
      {"kind": "E_FRAME_RESULT", "frame_id": 2, "t": 1, "state": "OK", "detections": [det(0, 0.9, BOX)]},
      {"kind": "E_TICK", "t": 1 + TH["l02_ns"] - 1},
      {"kind": "E_TICK", "t": 1 + TH["l02_ns"]}]
core, layer, logs, acts, _ = run(ev)
check("E1 距上次 CONTINUES = L02-1ns 不判 M10", logs[2]["transition"], None,
      f"state={logs[2]['to_state']}")
check("E2 距上次 CONTINUES = L02 判 M10", logs[3]["transition"], "M10")

# ---------------------------------------------------------------- F) 30fps 取较晚（第 8 帧 233.1ms）
P30 = 33_300_000
ev = frames(9, period=P30, state="OK", dets=[det(0, 0.9, BOX)])
core, layer, logs, acts, _ = run(ev)
m3 = [(i, l) for i, l in enumerate(logs) if l.get("transition") == "M3"]
check("F1 M3 出现在第 8 帧", m3[0][0], 7, f"t={m3[0][1]['t_input_ns']}")
check("F2 window_complete_ns = 233.1ms（M3 帧日志）", logs[7]["window_complete_ns"], 233_100_000)
check("F3 第 6 帧（166.5ms）未完成", [l.get("window_complete_ns") for l in logs[:6]],
      [None] * 6)

# ---------------------------------------------------------------- G) 异常滑动窗口 M2/M13/M12
ev = [{"kind": "E_FRAME_ERROR", "frame_id": 1, "t": 0},
      {"kind": "E_FRAME_ERROR", "frame_id": 2, "t": 100 * MS},
      {"kind": "E_FRAME_ERROR", "frame_id": 3, "t": 200 * MS},
      {"kind": "E_FRAME_ERROR", "frame_id": 4, "t": 300 * MS},   # 恢复期内再异常 → M13
      ]
for i in range(5, 10):                                          # 5 条合法 → M12
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": i, "t": (i) * 100 * MS, "state": "OK",
               "detections": [det(0, 0.9, BOX)]})
core, layer, logs, acts, _ = run(ev)
check("G1 异常滑动窗口 → M2/M13/M12",
      [l["transition"] for l in logs if l["transition"]], ["M2", "M13", "M12"])
check("G2 恢复后 final_state", core.state, "IDLE")

# ---------------------------------------------------------------- H) 同帧 M4/M10 → M10 优先
ev = [{"kind": "E_FRAME_RESULT", "frame_id": 1, "t": 10 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]},
      {"kind": "E_FRAME_RESULT", "frame_id": 2, "t": 110 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]},
      {"kind": "E_FRAME_RESULT", "frame_id": 3, "t": 210 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]},
      # 之后三帧零框（TARGET_CONTINUES 不成立）→ 抖动耗尽 + 停留达到 S04
      {"kind": "E_FRAME_RESULT", "frame_id": 4, "t": 310 * MS, "state": "NO_HAND", "detections": []},
      {"kind": "E_FRAME_RESULT", "frame_id": 5, "t": 410 * MS, "state": "NO_HAND", "detections": []},
      {"kind": "E_FRAME_RESULT", "frame_id": 6, "t": 510 * MS, "state": "NO_HAND", "detections": []}]
core = GestureInteractionCore(PACK)
pre = None
for i, e in enumerate(ev):
    e = dict(e); e["t_input_ns"] = e.pop("t"); e["session_id"] = "s1"
    if i == 5:
        # 独立核对：本帧同时满足 M4（容忍已耗尽 + 停留 >= S04）
        pre = {"jitter_exhausted": core.jitter_exhausted,
               "dwell_ns": e["t_input_ns"] - core.candidate_dwell_start_ns,
               "dwell_ok": (e["t_input_ns"] - core.candidate_dwell_start_ns) >= TH["s04_ns"],
               "streak": core.continues_false_streak}
    st = core.step(e)
check("H1 同帧 M4/M10 取 M10", st["log"]["transition"], "M10")
check("H2 该帧同时满足 M4 条件（独立观测）",
      (pre["jitter_exhausted"], pre["dwell_ok"]), (True, True), str(pre))

def drive(core, layer, events):
    """逐步喂事件（把 't' 映射为 t_input_ns），返回 (logs, action_ids)。"""
    logs, ids = [], []
    for e in events:
        e = dict(e)
        t = e.pop("t", None)
        if t is not None:
            e["t_input_ns"] = t
        e.setdefault("session_id", "s1")
        st = core.step(e)
        logs.append(st["log"])
        if st["action_request"]:
            rec = layer.submit(st["action_request"], e["t_input_ns"])
            core.note_action_ack(rec)
            ids.append(rec["acquisition_id"])
    return logs, ids


# ---------------------------------------------------------------- I) STABLE 锁存
def to_stable(start=0, period=100 * MS, cls=0, box=BOX, n=6):
    ev = frames(n, start=start, period=period, state="OK", dets=[det(cls, 0.9, box)])
    core = GestureInteractionCore(PACK)
    logs, _ = drive(core, ActionLayer(PACK), ev)
    return core, logs


def stable_with_closed_gate():
    """先提交锁门（600ms），再用异常→恢复清空目标，最后让新目标在门锁期间进入 STABLE。"""
    ev = frames(6, period=100 * MS, state="OK", dets=[det(0, 0.9, BOX)])
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK",
               "detections": [det(0, 0.9, BOX)]})
    for i, tm in enumerate((610 * MS, 620 * MS, 630 * MS)):
        ev.append({"kind": "E_FRAME_ERROR", "frame_id": 8 + i, "t": tm})
    for i in range(5):
        ev.append({"kind": "E_FRAME_RESULT", "frame_id": 11 + i, "t": 640 * MS + i * 10 * MS,
                   "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
    for i in range(6):
        ev.append({"kind": "E_FRAME_RESULT", "frame_id": 16 + i, "t": 700 * MS + i * 100 * MS,
                   "state": "OK", "detections": [det(1, 0.9, BOX_B)]})
    core = GestureInteractionCore(PACK)
    layer = ActionLayer(PACK)
    logs, ids = drive(core, layer, ev)
    return core, layer, logs, ids


core, layer, logs, ids = stable_with_closed_gate()
check("I1 门锁期间进入 STABLE", core.state, "STABLE")
check("I1b 仅 1 次提交（首次获取）", ids, [0])
# score 跌破 P02（仍几何连续）+ 窗口中断 → 锁存，不回 CANDIDATE
st = core.step({"kind": "E_FRAME_RESULT", "frame_id": 22, "t_input_ns": 1300 * MS, "state": "OK",
                "session_id": "s1", "detections": [det(1, 0.20, BOX_B)]})
check("I2 score 跌破 P02 仍在 STABLE（且门锁抑制）",
      (st["log"]["to_state"], st["log"]["transition"], "S_COOLDOWN" in st["log"]["suppression_events"]),
      ("STABLE", None, True))
for k, tm in ((23, 1400 * MS), (24, 1500 * MS)):
    st = core.step({"kind": "E_FRAME_RESULT", "frame_id": k, "t_input_ns": tm, "state": "OK",
                    "session_id": "s1", "detections": [det(1, 0.20, BOX_B)]})
check("I3 抖动耗尽后仍在 STABLE（M4 只作用 CANDIDATE）", core.state, "STABLE")
# 门未开启时的推进帧不触发；门开启帧（1600ms）触发
st = core.step({"kind": "E_FRAME_RESULT", "frame_id": 25, "t_input_ns": 1600 * MS - 1,
                "state": "OK", "session_id": "s1", "detections": [det(1, 0.9, BOX_B)]})
check("I4 门开前 1ns 的推进帧不触发", (core.state, st["log"]["transition"]), ("STABLE", None))
st = core.step({"kind": "E_FRAME_RESULT", "frame_id": 26, "t_input_ns": 1600 * MS, "state": "OK",
                "session_id": "s1", "detections": [det(1, 0.9, BOX_B)]})
check("I5 门开启帧触发 M5（无需重建窗口）", st["log"]["transition"], "M5")
check("I6 触发记录 acquisition_id（B11 推导：新获取应为 1；同 D2 发现）", core.acquisition_id, 1)

# STABLE 经异常退出（M2）
core, logs = to_stable()
for k in (7, 8, 9):
    st = core.step({"kind": "E_FRAME_ERROR", "frame_id": k, "t_input_ns": k * 100 * MS,
                    "session_id": "s1"})
check("I7 STABLE 经 M2 退出", st["log"]["transition"], "M2")

# ---------------------------------------------------------------- J) 动作层幂等 / 去重
layer = ActionLayer(PACK)
r1 = layer.submit({"action_type": "A_SWITCH_UI", "target_id": "T-fist", "class_id": 0}, 0)
r2 = layer.submit({"action_type": "A_SWITCH_UI", "target_id": "T-fist", "class_id": 0}, TH["a02_ns"])
check("J1 同键在 A02 处不判去重", r2.get("suppression"), None)
check("J2 幂等：已处于该状态无可见变化",
      (r2["already_active_before"], r2["visible_state_change"]), (True, False))
check("J3 首次提交有可见变化", r1["visible_state_change"], True)
layer = ActionLayer(PACK)
layer.submit({"action_type": "A_SWITCH_UI", "target_id": "T-fist", "class_id": 0}, 0)
r = layer.submit({"action_type": "A_SWITCH_UI", "target_id": "T-fist", "class_id": 0}, TH["a02_ns"] - 1)
check("J4 A02-1ns 判 S_DEDUP", r.get("suppression"), "S_DEDUP")
check("J5 去重记录进 records", layer.summary()["dedup_suppressed"], 1)
r = layer.submit({"action_type": "A_SWITCH_CHANNEL", "target_id": "T-fist", "class_id": 0},
                 TH["a02_ns"] - 1)
check("J6 不同 action_type 不去重", r.get("suppression"), None)
check("J7 声明不可达条件 A02<K01", TH["a02_ns"] < TH["k01_ns"], True)

# ---------------------------------------------------------------- K) acquisition_id 语义
# K1: M11 递增（LOST→IDLE 后再获取）
ev = frames(6, period=100 * MS, dets=[det(0, 0.9, BOX)])
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]})
ev += [{"kind": "E_TICK", "t": 1000 * MS}, {"kind": "E_TICK", "t": 1300 * MS}, {"kind": "E_TICK", "t": 1400 * MS}]
ev += [{"kind": "E_FRAME_RESULT", "frame_id": 8, "t": 1500 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]}]
ev += [{"kind": "E_FRAME_RESULT", "frame_id": 9, "t": 1600 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]}]
ev += frames(6, start=1700 * MS, period=100 * MS, dets=[det(0, 0.9, BOX)])
ev = [dict(e, frame_id=i + 1) for i, e in enumerate(ev)]
core, layer, logs, acts, _ = run(ev)
ids = [a["acquisition_id"] for a in acts if a]
check("K1 M11 后再获取 → 新 acquisition_id", ids, [0, 1])
check("K2 M11 迁移确实发生", "M11" in [l["transition"] for l in logs], True)

# K3: M4 递增（CANDIDATE 内抖动耗尽 + 停留 >= S04，且 M10 未命中、窗口未完成）
ev = []
for i, tm in enumerate((10 * MS, 110 * MS, 210 * MS, 310 * MS, 410 * MS)):
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": i + 1, "t": tm, "state": "OK",
               "detections": [det(0, 0.9, BOX)]})
for i, tm in enumerate((510 * MS, 610 * MS)):
    ev.append({"kind": "E_FRAME_RESULT", "frame_id": 6 + i, "t": tm, "state": "NO_HAND",
               "detections": []})
core = GestureInteractionCore(PACK)
seq = []
for e in ev:
    e = dict(e); e["t_input_ns"] = e.pop("t")
    st = core.step({**e, "session_id": "s1"})
    seq.append((st["log"]["transition"], core.acquisition_id))
check("K3 M4 迁移发生", [s[0] for s in seq if s[0] == "M4"], ["M4"], str(seq))
check("K4 M4 递增 acquisition_id", [s[1] for s in seq if s[0] == "M4"], [1])
check("K5 M4 后 current_target 清空", core.current_target, None)

# K6: 会话切换归零
core, layer, logs, acts, _ = run(frames(6, period=100 * MS, dets=[det(0, 0.9, BOX)]))
before = core.acquisition_id
st = core.step({"kind": "E_FRAME_RESULT", "frame_id": 7, "t_input_ns": 700 * MS, "state": "OK",
                "session_id": "s2", "detections": []})
check("K6 会话切换归零", (st["log"]["transition"], core.acquisition_id), ("RESET", 0))

# K7: M8 路径的 acquisition_id 行为（D7 措辞的实测）
# 首次触发 @600ms → 门到 1600ms；COOLDOWN 内 1590ms 维持帧、1595ms 零框（CONTINUES 不成立），
# 门开启帧 1600ms 恰为 E_TICK → B14 第三分支 M8。
ev = frames(6, period=100 * MS, dets=[det(0, 0.9, BOX)])
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 7, "t": 600 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]})
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 8, "t": 1590 * MS, "state": "OK", "detections": [det(0, 0.9, BOX)]})
ev.append({"kind": "E_FRAME_RESULT", "frame_id": 9, "t": 1595 * MS, "state": "NO_HAND", "detections": []})
ev.append({"kind": "E_TICK", "t": 1600 * MS})
core, layer, logs, acts, _ = run(ev)
check("K7a M8 可达（门开启帧 CONTINUES 不成立）", logs[-1]["transition"], "M8",
      f"state={core.state} acq={core.acquisition_id}")
# 之后重新获取另一目标：M8 未分配新 id
ev2 = frames(7, start=1700 * MS, period=100 * MS, dets=[det(1, 0.9, BOX_B)])
ev2 = [dict(e, frame_id=10 + i) for i, e in enumerate(ev2)]
core = GestureInteractionCore(PACK)
layer = ActionLayer(PACK)
logs2, ids = drive(core, layer, ev + ev2)
check("K7b M8 后新获取仍复用旧 acquisition_id（D7/B11 推导应为 1）", ids, [0, 1],
      f"transitions={[l['transition'] for l in logs2 if l['transition']]}")

print("\n==== 汇总 ====")
bad = [r for r in RESULTS if not r[1]]
print(f"共 {len(RESULTS)} 项断言，FAIL {len(bad)}")
for name, ok, got, want, extra in bad:
    print(f"  FAIL {name}: got={got!r} want={want!r} {extra}")
Path(__file__).resolve().parent.joinpath("adv_semantics_result.json").write_text(
    json.dumps([{"name": n, "ok": o, "got": repr(g), "want": repr(w), "extra": e}
                for n, o, g, w, e in RESULTS], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")