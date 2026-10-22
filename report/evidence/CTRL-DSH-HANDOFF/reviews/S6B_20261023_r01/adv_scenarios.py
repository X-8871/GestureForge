#!/usr/bin/env python3
"""Reviewer 自构造对抗序列（S6-B）：逐条核对 H-4 / H-10 / M3 / M5 / M10 / 锁存 / 边界。

全部期望由规格文档与行为表草案值（S01=200ms、S02=6、S03=later_of、S04=500ms、L01=5、
L02=300ms、K01=1000ms、J01=1、C01=2、U00_W=3、U00_N=3、U01=5、P01=.35、P02=.30、
P03=.30、P04=.15、P05=.05、A02=500ms）人工推导，不读取状态机输出作为预期。
只在隔离副本内运行。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ISO = Path(r"D:\FPGA_Competition\tmp\review\S6B_20261023_r01\iso")
sys.path.insert(0, str(ISO))

from src.stage6.s6_actions import ActionLayer, OutcomePolicy  # noqa: E402
from src.stage6.s6_core import GestureInteractionCore  # noqa: E402
from src.stage6.s6_params import ParamPack  # noqa: E402

PACK = ParamPack(ISO / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=ISO)
BOX_A = [0.2, 0.2, 0.6, 0.6]
BOX_B = [0.25, 0.25, 0.65, 0.65]


class Rig:
    """驱动核心 + 动作层（与 s6b_run_cases.py 同构，但独立实现，便于交叉核对）。"""

    def __init__(self, policy: OutcomePolicy | None = None):
        self.core = GestureInteractionCore(PACK)
        self.layer = ActionLayer(PACK, policy)
        self.transitions: list[str] = []
        self.submits: list[tuple[int, dict]] = []   # (frame_id, record)
        self.suppressions: list[str] = []
        self.states: list[str] = []
        self.window_completes: list[int | None] = []

    def step(self, t: int, kind: str = "E_FRAME_RESULT", fid=None, state="OK",
             dets=None, stale=False, session="s1"):
        ev = {"kind": kind, "t_input_ns": t, "session_id": session}
        if kind == "E_FRAME_RESULT":
            ev.update({"frame_id": fid, "state": state, "stale": stale,
                       "detections": [] if dets is None else dets})
        elif fid is not None:
            ev["frame_id"] = fid
        out = self.core.step(ev)
        log = out["log"]
        if log.get("transition"):
            self.transitions.append(log["transition"])
        for name in log.get("suppression_events") or []:
            self.suppressions.append(str(name))
        req = out["action_request"]
        if req is not None:
            rec = self.layer.submit(req, t)
            ack = self.core.note_action_ack(rec)
            if ack.get("transition"):
                self.transitions.append(ack["transition"])
            for name in ack.get("suppression_events") or []:
                self.suppressions.append(str(name))
            self.submits.append((log.get("frame_id"), rec))
        self.states.append(self.core.state)
        self.window_completes.append(log.get("window_complete_ns"))
        return out

    @property
    def window_complete_ns(self):
        """M3 成立帧的记录值（核心字段进入 COOLDOWN 时会被清空，故从逐帧日志取首次非空值）。"""
        return next((v for v in self.window_completes if v is not None), None)

    @property
    def submitted_frames(self):
        return [f for f, r in self.submits if r.get("submit_result") == "success"
                and not r.get("suppression")]


def det(cls=0, score=0.9, box=None, order=0):
    return {"class_id": cls, "score": score, "xyxy": list(box or BOX_A), "source_order": order}


def ok(dets=None, **kw):
    return dict(state="OK", dets=dets if dets is not None else [det(0, 0.9)], **kw)


RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str) -> None:
    RESULTS.append((name, bool(cond), detail))


# ---------------------------------------------------------------- S1: H-4 零框
def s1_no_hand_cannot_complete():
    r = Rig()
    r.step(0, fid=1, **ok())
    counts = [r.core.window_match_count]
    for i in range(2, 11):
        r.step(20_000_000 * (i - 1), fid=i, state="NO_HAND", dets=[])
        counts.append(r.core.window_match_count)
    check("S1a NO_HAND 从不推进 WINDOW_MATCH（峰值仍为 1；连续 2 帧后按抖动规则重置证据）",
          max(counts) == 1 and counts[1:] == [1] + [0] * 8,
          f"counts={counts}")
    check("S1a NO_HAND 不得完成窗口（无 M3）",
          "M3" not in r.transitions and r.core.state == "IDLE",
          f"transitions={r.transitions} state={r.core.state}")
    check("S1a 零框不触发动作",
          r.layer.summary()["action_submitted"] == 0 and r.core.counters["no_hand_frames"] == 9,
          f"submitted={r.layer.summary()['action_submitted']} no_hand={r.core.counters['no_hand_frames']}")


def s1b_matches_plus_zeros_plus_matches():
    r = Rig()
    for i in range(1, 6):            # 5 帧稳定
        r.step(20_000_000 * (i - 1), fid=i, **ok())
    for i in range(6, 9):            # 3 帧零框（>J01=1 → 第 2 帧即重置窗口）
        r.step(20_000_000 * (i - 1), fid=i, state="NO_HAND", dets=[])
    for i in range(9, 12):           # 再 3 帧 OK（不足 S02=6）
        r.step(20_000_000 * (i - 1), fid=i, **ok())
    check("S1b 5 匹配 + 3 零框 + 3 匹配 ≠ 完成窗口",
          r.core.state == "CANDIDATE" and r.core.window_match_count == 3 and "M3" not in r.transitions,
          f"state={r.core.state} cnt={r.core.window_match_count} transitions={r.transitions}")
    check("S1b 无动作",
          r.layer.summary()["action_submitted"] == 0, f"submitted={r.layer.summary()['action_submitted']}")


# ------------------------------------------------- S2: H-10 全局门 + 切目标 + 锁存
def s2_global_gate_cross_target(gate_frame_kind: str = "TIMEOUT", last_ns: int = 0):
    """构造：目标 A 触发一次 → 丢失 → 目标 B 在冷却内达标（必须被抑制）→
    STABLE 锁存 → 门开启那一帧若是非推进帧（TIMEOUT）不得触发 → 下一条推进帧触发。"""
    r = Rig()
    # 阶段 A：目标 A（class 0）稳定并触发
    for i in range(1, 8):                     # t = 0,50,...,300 ms
        r.step(50_000_000 * (i - 1), fid=i, **ok([det(0, 0.9)]))
    first = list(r.submitted_frames)
    # 阶段 B：手离开（NO_HAND ×5）→ M10 → LOST；再 1 帧 → M11 → IDLE
    for i in range(8, 13):
        r.step(50_000_000 * (i - 1), fid=i, state="NO_HAND", dets=[])
    r.step(50_000_000 * 12, fid=13, state="NO_HAND", dets=[])
    # 阶段 C：目标 B（class 1）在冷却内重新达标 → M3 但 M5 必须被 H-10 抑制
    n_before_c = len(r.submits)
    for i in range(14, 20):                   # t = 650..900 ms
        r.step(50_000_000 * (i - 1), fid=i, **ok([det(1, 0.9, BOX_B)]))
    mid_submits = [f for f, rec in r.submits[n_before_c:]
                   if rec.get("submit_result") == "success" and not rec.get("suppression")]
    # 阶段 D：锁存期内低分帧（TARGET_CONTINUES 成立、score<P02）→ 不得退回 CANDIDATE
    r.step(1_000_000_000, fid=20, **ok([det(1, 0.28, BOX_B)]))
    r.step(1_050_000_000, fid=21, **ok([det(1, 0.28, BOX_B)]))
    states_after_low = list(r.states)
    # 阶段 E：持续推进帧保持丢失锚点新鲜，直到门开启（t_last_submit=300ms + K01=1000ms = 1300ms）
    for i, t in zip(range(22, 27), (1_100_000_000, 1_150_000_000, 1_200_000_000,
                                    1_250_000_000, 1_260_000_000)):
        r.step(t, fid=i, **ok([det(1, 0.9, BOX_B)]))
    gate_open_t = 300_000_000 + 1_000_000_000 + last_ns
    if gate_frame_kind == "TIMEOUT":
        r.step(gate_open_t, fid=27, kind="E_FRAME_TIMEOUT")
        r.step(gate_open_t + 50_000_000, fid=28, **ok([det(1, 0.9, BOX_B)]))
    else:                                     # OK_BOUNDARY：在门开启时刻（±last_ns）给一条推进帧
        r.step(gate_open_t, fid=27, **ok([det(1, 0.9, BOX_B)]))
    return r, first, mid_submits, states_after_low, gate_open_t


def s2_checks():
    r, first, mid, states_after_low, gate_open_t = s2_global_gate_cross_target()
    check("S2a 首次触发帧 = 7", first == [7], f"first={first}")
    check("S2b 冷却内（切目标后）不得提交（0 次）", mid == [],
          f"冷却内提交帧={mid}")
    check("S2b 冷却内达标触发被 H-10 抑制并记 S_COOLDOWN",
          "S_COOLDOWN" in r.suppressions, f"suppressions={sorted(set(r.suppressions))}")
    check("S2c STABLE 锁存：低分帧不退回 CANDIDATE",
          states_after_low[-2:] == ["STABLE", "STABLE"], f"after_low={states_after_low[-3:]}")
    check("S2c 锁存期内不出现 M4", "M4" not in r.transitions, f"transitions={r.transitions}")
    check("S2d 门开启那一帧为非推进帧（TIMEOUT）→ 不触发",
          r.submitted_frames == [7, 28], f"submitted={r.submitted_frames}")
    check("S2e 门开启后无需重新累积窗口即可触发（第 28 帧）",
          r.core.counters["action_submitted"] == 2 and r.layer.summary()["action_submitted"] == 2,
          f"core={r.core.counters['action_submitted']} layer={r.layer.summary()['action_submitted']}")


def s2_gate_boundary():
    """K01 边界：门开启时刻前 1 ns 的推进帧必须被抑制；恰好开启的那一帧必须触发。"""
    r, first, mid, _, _ = s2_global_gate_cross_target(gate_frame_kind="OK_BOUNDARY", last_ns=-1)
    check("S2f K01−1 ns 的推进帧被抑制（不产生第二次提交）",
          r.submitted_frames == [7], f"submitted={r.submitted_frames}")
    r2, *_ = s2_global_gate_cross_target(gate_frame_kind="OK_BOUNDARY", last_ns=0)
    check("S2g K01 恰好等于 1000 ms 的推进帧触发（含等号）",
          r2.submitted_frames == [7, 27], f"submitted={r2.submitted_frames}")


# --------------------------------------------------------- S3: M10 时间边界 ±1ns
def s3_l02_boundary():
    def run(extra: int):
        r = Rig()
        r.step(0, fid=1, **ok())
        r.step(100_000_000, fid=2, **ok())          # 最后一次 TARGET_CONTINUES = 100 ms
        r.step(100_000_000 + 300_000_000 + extra, kind="E_TICK")   # L02 边界
        return r

    r_before = run(-1)
    check("S3a L02−1 ns 的 TICK 不确认丢失（不出现 M10）",
          "M10" not in r_before.transitions and r_before.core.state == "CANDIDATE",
          f"transitions={r_before.transitions} state={r_before.core.state}")
    r_equal = run(0)
    check("S3b L02 恰好 300 ms 的 TICK 确认丢失（M10，含等号）",
          "M10" in r_equal.transitions and r_equal.core.state == "LOST",
          f"transitions={r_equal.transitions} state={r_equal.core.state}")
    check("S3c 丢失确认不产生动作", r_equal.layer.summary()["action_submitted"] == 0, "")


# --------------------------------------------------- S4: 非推进帧不得触发（门开启时刻）
def s4_non_advancing_cannot_trigger():
    r = Rig()
    seen: list[int] = []
    for i in range(1, 8):                     # 目标 A 触发一次（t=0..300 ms）
        r.step(50_000_000 * (i - 1), fid=i, **ok([det(0, 0.9)]))
    for i in range(8, 13):                    # 丢失确认（NO_HAND ×5）
        r.step(50_000_000 * (i - 1), fid=i, state="NO_HAND", dets=[])
    r.step(50_000_000 * 12, fid=13, state="NO_HAND", dets=[])
    for i in range(14, 20):                   # 目标 B 在冷却内达标 → STABLE（门仍关）
        r.step(50_000_000 * (i - 1), fid=i, **ok([det(1, 0.9, BOX_B)]))
    for i, t in zip(range(20, 27), (950_000_000, 1_000_000_000, 1_050_000_000,
                                    1_100_000_000, 1_150_000_000, 1_200_000_000,
                                    1_250_000_000)):
        r.step(t, fid=i, **ok([det(1, 0.9, BOX_B)]))   # 保持丢失锚点新鲜
    t_gate = 300_000_000 + 1_000_000_000               # 恰为 K01 门开启时刻
    r.step(t_gate, fid=27, **ok([det(1, 0.9, BOX_B)], stale=True))
    seen.append(len(r.submitted_frames))
    check("S4a stale 帧即使恰逢门开启也不触发（状态停留 STABLE）",
          r.submitted_frames == [7] and r.core.state == "STABLE",
          f"submitted={r.submitted_frames} state={r.core.state}")
    r.step(t_gate + 10_000_000, fid=27, **ok([det(1, 0.9, BOX_B)]))   # 同 frame_id 重复
    check("S4b 重复 frame_id 不得触发",
          r.submitted_frames == [7] and r.core.counters["duplicate_frames"] == 1,
          f"submitted={r.submitted_frames} dup={r.core.counters['duplicate_frames']}")
    r.step(t_gate + 20_000_000, fid=5, **ok([det(1, 0.9, BOX_B)]))    # 倒序
    check("S4c 倒序 frame_id 不得触发（并计异常）",
          r.submitted_frames == [7] and r.core.counters["out_of_order_frames"] == 1,
          f"submitted={r.submitted_frames} ooo={r.core.counters['out_of_order_frames']}")
    r.step(t_gate + 50_000_000, fid=28, **ok([det(1, 0.9, BOX_B)]))   # 真正的推进帧
    check("S4d 门开启后的下一条窗口推进帧触发",
          r.submitted_frames == [7, 28], f"submitted={r.submitted_frames}")


# ------------------------------------------- S5: 异常窗口（滑动 3 帧 / 3 异常）
def s5_anomaly_window():
    r = Rig()
    r.step(0, fid=1, **ok())
    r.step(100_000_000, fid=2, **ok())
    r.step(200_000_000, fid=3, kind="E_FRAME_ERROR")
    r.step(300_000_000, fid=4, **ok())           # 窗口中 [E,OK]
    r.step(400_000_000, fid=5, kind="E_FRAME_TIMEOUT")
    r.step(500_000_000, fid=6, kind="E_FRAME_ERROR")
    check("S5a 窗口内异常数 2 < 3 时不进恢复态",
          "M2" not in r.transitions and r.core.state == "CANDIDATE",
          f"transitions={r.transitions} state={r.core.state}")
    r.step(600_000_000, fid=7, kind="E_FRAME_DROPPED")
    check("S5b 第 3 个异常（最近 3 条内）→ M2 进 UNKNOWN_RECOVER",
          r.transitions[-1] == "M2" and r.core.state == "UNKNOWN_RECOVER",
          f"transitions={r.transitions} state={r.core.state}")
    check("S5c 恢复态清空目标与稳定证据",
          r.core.current_target is None and r.core.window_match_count == 0, "")
    # 恢复期 5 条合法结果 → M12
    for i, t in zip(range(8, 13), range(700_000_000, 1_200_000_000, 100_000_000)):
        r.step(t, fid=i, **ok())
    check("S5d 恢复期连续 5 条合法结果 → M12 回 IDLE",
          r.transitions[-1] == "M12" and r.core.state == "IDLE", f"transitions={r.transitions}")
    # 恢复期再次异常 → M13（自环）并重置计数起点：此后仅 4 条合法结果不得恢复
    r2 = Rig()
    r2.step(0, fid=1, **ok())
    r2.step(100_000_000, fid=2, **ok())
    for i, t in zip(range(3, 6), (200_000_000, 300_000_000, 400_000_000)):
        r2.step(t, fid=i, kind="E_FRAME_ERROR")
    r2.step(500_000_000, fid=6, kind="E_FRAME_ERROR")
    check("S5e 恢复态内再次异常 → M13（保持 UNKNOWN_RECOVER）",
          "M13" in r2.transitions and r2.core.state == "UNKNOWN_RECOVER",
          f"transitions={r2.transitions} state={r2.core.state}")
    for i, t in zip(range(7, 11), range(600_000_000, 1_000_000_000, 100_000_000)):
        r2.step(t, fid=i, **ok())
    check("S5f M13 后需重新累计 5 条（4 条不恢复）",
          r2.core.state == "UNKNOWN_RECOVER" and "M12" not in r2.transitions,
          f"state={r2.core.state} transitions={r2.transitions}")


# ---------------------------------------------------- S6: 30 fps 取较晚（233.1ms）
def s6_30fps_later_of():
    r = Rig()
    for i in range(1, 10):
        r.step(33_300_000 * (i - 1), fid=i, **ok())
    check("S6 30fps：第 6 帧 166.5 ms 不足 200 ms → M3 在第 8 帧（233.1 ms）",
          r.window_complete_ns == 233_100_000 and r.transitions[:2] == ["M1", "M3"]
          and r.submitted_frames == [9],
          f"complete={r.window_complete_ns} transitions={r.transitions} submitted={r.submitted_frames}")


# ------------------------------------------- S8: P2 优先于 P3（M10 与 M4 同帧竞争）
def s8_m10_beats_m4():
    """CANDIDATE 下同一帧同时满足 M4（抖动耗尽 + dwell≥S04=500ms）与 M10（miss_streak≥L01=5）
    → 规格 §4 规定 M10 优先（P2 先于 P3）。
    构造：f1 建立 dwell_start=0；f2 迟至 450 ms（IDLE 内 M10 不求值）→ M1；随后 5 帧 NO_HAND
    以 10 ms 间隔使 miss_streak=5 且距锚点仅 50 ms（时间条件未命中）；第 5 帧 dwell=500 ms
    且抖动已耗尽 → M4/M10 同帧竞争。"""
    r = Rig()
    r.step(0, fid=1, **ok())
    r.step(450_000_000, fid=2, **ok())          # IDLE 内不判 M10；M1，dwell_start 保持 0
    for k, t in enumerate((460_000_000, 470_000_000, 480_000_000, 490_000_000, 500_000_000)):
        r.step(t, fid=3 + k, state="NO_HAND", dets=[])
    check("S8 同帧 M4/M10 同时满足时按求值序取 M10（P2 先于 P3）",
          r.transitions == ["M1", "M10"] and r.core.state == "LOST" and "M4" not in r.transitions,
          f"transitions={r.transitions} state={r.core.state}")


# ------------------------------------- S9: M10 只按 TARGET_CONTINUES（低分几何连续不算丢失）
def s9_m10_ignores_window_score():
    """M10 只按 TARGET_CONTINUES：score=0.28（<P01=0.35、<P02=0.30）但几何完全相同的连续 6 帧
    经 §8 迟滞分支仍被维持 → miss_streak 保持 0、锚点刷新 → 即使距上次 WINDOW_MATCH 远超
    L02=300 ms 也不得确认丢失；同时这些帧不满足 WINDOW_MATCH（窗口证据被抖动重置）。"""
    r = Rig()
    r.step(0, fid=1, **ok())
    r.step(100_000_000, fid=2, **ok())              # M1 → CANDIDATE；最后一次 WINDOW_MATCH = 100 ms
    for k, t in enumerate((200_000_000, 300_000_000, 400_000_000)):
        r.step(t, fid=3 + k, **ok([det(0, 0.28)]))  # 低分但几何连续（迟滞维持）
    check("S9 M10 只按 TARGET_CONTINUES：距上次 WINDOW_MATCH 已达 300 ms（=L02）仍不确认丢失",
          r.core.state == "CANDIDATE" and "M10" not in r.transitions
          and r.core.continues_false_streak == 0,
          f"state={r.core.state} transitions={r.transitions} miss={r.core.continues_false_streak}")
    check("S9 这些帧确实不满足 WINDOW_MATCH（窗口证据被抖动重置，count=0）",
          r.core.window_match_count == 0, f"count={r.core.window_match_count}")


# ------------------------------------- S7: 动作层幂等 / A02 去重（直接调用动作层）
def s7_action_layer():
    layer = ActionLayer(PACK)
    req = {"action_type": "A_SWITCH_UI", "target_id": "UI_MENU", "class_id": 0,
           "class_name": "fist", "source_frame_id": 7, "trigger_frame_id": 7,
           "t_trigger_ns": 600_000_000, "acquisition_id": 0}
    r1 = layer.submit(req, 600_000_000)
    r2 = layer.submit(req, 700_000_000)          # 100 ms < A02=500 ms → 去重
    r3 = layer.submit(req, 1_100_000_000)        # 恰 500 ms ≥ A02 → 不去重
    s = layer.summary()
    check("S7a 首次提交：success + observed + 可见变化",
          (r1["action_id"], r1["submit_result"], r1["effective_result"],
           r1["visible_state_change"]) == ("ACT-0001", "success", "observed", True),
          json.dumps({k: r1[k] for k in ("action_id", "submit_result", "effective_result", "visible_state_change")}))
    check("S7b A02 内重复 → S_DEDUP 抑制，且不分配新 action_id/不更新锚点",
          r2["suppression"] == "S_DEDUP" and r2["action_id"] is None and r2["submit_result"] is None,
          json.dumps({k: r2.get(k) for k in ("suppression", "action_id", "submit_result")}))
    check("S7c 恰 A02=500 ms 不再抑制（含等号外的严格小于语义）",
          r3["suppression"] is None and r3["action_id"] == "ACT-0002", json.dumps(r3.get("suppression")))
    check("S7d 幂等：同一具名状态再提交无额外可见变化",
          r3["visible_state_change"] is False and r3["already_active_before"] is True, "")
    check("S7e 汇总不虚报成功：submitted=2 / effective=2 / dedup=1 / 可见变化=1",
          (s["action_submitted"], s["action_effective"], s["dedup_suppressed"],
           s["visible_state_changes"]) == (2, 2, 1, 1), json.dumps(s))
    check("S7f action_id 与来源帧保留",
          r1["source_frame_id"] == 7 and r1["trigger_frame_id"] == 7 and r1["t_trigger_ns"] == 600_000_000,
          "")


def s7b_core_dedup_unreachable():
    """核心驱动下两次提交的最短间隔 = K01(1000 ms) > A02(500 ms) → S_DEDUP 分支不可能命中。"""
    k01 = PACK.ns("T6-K01")
    a02 = PACK.ns("T6-A02")
    check("S7g K01 > A02 ⇒ 核心驱动路径下 S_DEDUP 不可达（与 reachability_notes 自洽）",
          k01 > a02, f"K01={k01} A02={a02}")


def main() -> int:
    s1_no_hand_cannot_complete()
    s1b_matches_plus_zeros_plus_matches()
    s2_checks()
    s2_gate_boundary()
    s3_l02_boundary()
    s4_non_advancing_cannot_trigger()
    s5_anomaly_window()
    s6_30fps_later_of()
    s8_m10_beats_m4()
    s9_m10_ignores_window_score()
    s7_action_layer()
    s7b_core_dedup_unreachable()

    failed = [row for row in RESULTS if not row[1]]
    for name, okk, detail in RESULTS:
        print(("PASS " if okk else "FAIL ") + name + ("   | " + detail if detail else ""))
    print(f"\n合计 {len(RESULTS)} 项；通过 {len(RESULTS) - len(failed)}；失败 {len(failed)}")
    out = Path(r"D:\FPGA_Competition\tmp\review\S6B_20261023_r01\adv_scenarios_result.json")
    out.write_text(json.dumps(
        {"checks": [{"name": n, "pass": o, "detail": d} for n, o, d in RESULTS],
         "failed": len(failed)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())