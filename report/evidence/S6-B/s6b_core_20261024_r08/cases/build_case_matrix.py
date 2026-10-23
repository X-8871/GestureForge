#!/usr/bin/env python3
"""生成 S6-B / S6-C 确定性用例矩阵（expected 由行为表 v1.8 人工推导后写入，不由状态机生成）。"""

from __future__ import annotations

import json
from pathlib import Path

RUN = Path(r"D:\codex-worktrees\w6\report\evidence\S6-B\s6b_core_20261024_r08")

A = [0.20, 0.20, 0.60, 0.60]      # 近处框
B = [0.62, 0.22, 0.90, 0.50]      # 远处框（目标跳变用）
MS = 1_000_000


def det(class_id: int, score: float, box: list[float], order: int = 0) -> dict:
    return {"class_id": class_id, "score": score, "xyxy": list(box), "source_order": order}


def ev(kind: str, frame_id: int | None, dt_ms: float, **extra) -> dict:
    event = {"kind": kind, "dt_ns": int(round(dt_ms * MS))}
    if frame_id is not None:
        event["frame_id"] = frame_id
    event.update(extra)
    return event


def ok(frame_id: int, dt_ms: float, dets: list[dict], **extra) -> dict:
    return ev("E_FRAME_RESULT", frame_id, dt_ms, state="OK", detections=dets, **extra)


def no_hand(frame_id: int, dt_ms: float) -> dict:
    return ev("E_FRAME_RESULT", frame_id, dt_ms, state="NO_HAND", detections=[])


def tick(dt_ms: float) -> dict:
    return ev("E_TICK", None, dt_ms)


def stable_frames(count: int, class_id: int = 0, score: float = 0.90,
                  start: int = 1, dt_ms: float = 100.0, box: list[float] | None = None,
                  first_dt_ms: float = 0.0) -> list[dict]:
    return [ok(frame_id, first_dt_ms if frame_id == start else dt_ms,
               [det(class_id, score, box or A)])
            for frame_id in range(start, start + count)]


def expected_triggered(target: str, display_key: str, transitions: list[str],
                       submitted_frames: list[int], counters: dict | None = None,
                       final_state: str = "COOLDOWN", effective: int = 1,
                       visible: int = 1, failed: int = 0, unobserved: int = 0,
                       window_complete_ns: int = 500_000_000) -> dict:
    display = {display_key: target}
    return {
        "final_state": final_state,
        "transitions": transitions,
        "submitted_at_frames": submitted_frames,
        "window_complete_ns": window_complete_ns,
        "action_summary": {
            "action_submitted": len(submitted_frames),
            "action_effective": effective,
            "action_failed": failed,
            "action_unobserved": unobserved,
            "visible_state_changes": visible,
            "final_display_state": display.get("final_display_state"),
            "final_channel": display.get("final_channel"),
        },
        "core_counters": counters or {},
    }


cases: list[dict] = []

# ---- C1：每类稳定输入（5 例） ----
for class_id, class_name, action_type, target_id, key in (
    (0, "fist", "A_SWITCH_UI", "UI_MENU", "final_display_state"),
    (1, "palm", "A_SWITCH_UI", "UI_STATS", "final_display_state"),
    (2, "one", "A_SWITCH_CHANNEL", "CH_1", "final_channel"),
    (3, "two_up", "A_SWITCH_CHANNEL", "CH_2", "final_channel"),
    (4, "three", "A_SWITCH_CHANNEL", "CH_3", "final_channel"),
):
    cases.append({
        "case_id": f"C1-{class_name}-stable",
        "matrix_class": "每类稳定输入",
        "description": f"class_id={class_id}（{class_name}）连续 8 帧稳定：第 6 帧满足窗口（M3），第 7 帧触发（M5→M6），动作映射为 {action_type}/{target_id}。",
        "events": stable_frames(8, class_id),
        "expected": expected_triggered(target_id, key, ["M1", "M3", "M5", "M6"], [7],
                                       {"no_hand_frames": 0, "invalid": 0, "action_submitted": 1}),
    })

# ---- C2：持续保持与冷却后保持（唯一触发） ----
cases.append({
    "case_id": "C2-hold-past-cooldown",
    "matrix_class": "持续保持与冷却后保持",
    "description": "保持 20 帧（2 s）：第 7 帧触发一次；冷却在 t_last_submit+T6-K01=1600 ms 结束，第 17 帧走 M9 维持态，不再触发（B15/§10）。",
    "events": stable_frames(20),
    "expected": expected_triggered("UI_MENU", "final_display_state",
                                   ["M1", "M3", "M5", "M6", "M9"], [7],
                                   {"action_submitted": 1}, final_state="STABLE"),
})

# ---- C3：手离开再出现（新获取可再次触发） ----
c3_events = stable_frames(8)
c3_events += [no_hand(9, 100), no_hand(10, 100), no_hand(11, 100)]
c3_events += stable_frames(8, start=12, first_dt_ms=100.0)
cases.append({
    "case_id": "C3-lost-then-reappear",
    "matrix_class": "手离开再出现",
    "description": "触发后手离开：第 8 帧仍为 OK（刷新 t_last_target_continues=700 ms），第 9–11 帧 NO_HAND 且第 11 帧距锚点满 T6-L02=300 ms → M10→LOST；第 12 帧先按丢失态走 M11→IDLE（清空目标与证据）；同目标自第 13 帧起重新累积窗口 → 第 18 帧 M3、第 19 帧第二次触发（新获取，门已结束）。",
    "events": c3_events,
    "expected": expected_triggered("UI_MENU", "final_display_state",
                                   ["M1", "M3", "M5", "M6", "M10", "M11", "M1", "M3", "M5", "M6"],
                                   [7, 19], {"no_hand_frames": 3, "action_submitted": 2},
                                   effective=2),
})

# ---- C4a：短暂抖动 → 窗口重置且不触发 ----
c4a = stable_frames(5)
c4a += [ok(6, 100, [det(0, 0.28, A)]), ok(7, 100, [det(0, 0.28, A)])]
cases.append({
    "case_id": "C4-jitter-reset",
    "matrix_class": "短暂抖动",
    "description": "5 帧稳定后连续 2 帧 score<P02：第 1 帧容忍（≤T6-J01），第 2 帧重置窗口；候选停留已达 T6-S04=500 ms → M4→IDLE，不触发。",
    "events": c4a,
    "expected": {
        "final_state": "IDLE",
        "transitions": ["M1", "M4"],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"action_submitted": 0},
        "suppressions_include": ["S_JITTER_TOLERATED"],
    },
})

# ---- C4b：两类快速切换 → 不建立候选 ----
c4b = [ok(1, 0, [det(0, 0.9, A)]), ok(2, 100, [det(1, 0.9, A)]), ok(3, 100, [det(0, 0.9, A)]),
       ok(4, 100, [det(1, 0.9, A)]), ok(5, 100, [det(0, 0.9, A)]), ok(6, 100, [det(1, 0.9, A)])]
cases.append({
    "case_id": "C4-quick-switch",
    "matrix_class": "两类快速切换",
    "description": "fist/palm 逐帧交替：每帧都是目标切换（TARGET_CONTINUES 不成立），连续同目标帧数达不到 T6-C01=2 → 不进入 CANDIDATE、不触发。",
    "events": c4b,
    "expected": {
        "final_state": "IDLE",
        "transitions": [],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"action_submitted": 0},
    },
})

# ---- C5a：同分 → source_order 权威 ----
cases.append({
    "case_id": "C5-tie-source-order",
    "matrix_class": "多目标/同分",
    "description": "每帧两框同分 0.90（fist order=5、palm order=2）：同分按 source_order 权威解析 → 选中 palm（order 2），稳定后动作为 UI_STATS；记录 S_CONFLICT_RESOLVED。",
    "events": [ok(frame_id, 0.0 if frame_id == 1 else 100,
                  [det(0, 0.90, A, order=5), det(1, 0.90, A, order=2)])
               for frame_id in range(1, 9)],
    "expected": dict(expected_triggered("UI_STATS", "final_display_state",
                                        ["M1", "M3", "M5", "M6"], [7],
                                        {"action_submitted": 1}),
                     markers_include=["source_order"]),
})

# ---- C5b：维持优先（低分当前目标胜过更高分异类框） ----
c5b = [ok(1, 0, [det(0, 0.40, A)])]
c5b += [ok(frame_id, 100, [det(0, 0.40, A), det(1, 0.95, A)]) for frame_id in range(2, 9)]
cases.append({
    "case_id": "C5-held-priority",
    "matrix_class": "多目标/维持优先",
    "description": "当前 fist 0.40（≥T6-P02）持续成立，另有 palm 0.95 异类高分框：按 B03 维持 fist（记录 S_TARGET_HELD），稳定后动作仍是 UI_MENU。",
    "events": c5b,
    "expected": dict(expected_triggered("UI_MENU", "final_display_state",
                                        ["M1", "M3", "M5", "M6"], [7],
                                        {"action_submitted": 1}),
                     suppressions_include=["S_TARGET_HELD"]),
})

# ---- C5c：目标跳变 → 新目标必须重新累积窗口 ----
c5c = stable_frames(3)
c5c += stable_frames(6, class_id=1, start=4, box=B, first_dt_ms=100.0)
c5c.append(ok(10, 100, [det(1, 0.9, B)]))
cases.append({
    "case_id": "C5-target-jump",
    "matrix_class": "多目标/目标跳变",
    "description": "第 1–3 帧 fist，第 4 帧起换成远处 palm：切换结束当前获取并清空窗口证据，新目标重新累积 6 帧 → 第 9 帧 M3、第 10 帧触发 UI_STATS。",
    "events": c5c,
    "expected": expected_triggered("UI_STATS", "final_display_state",
                                   ["M1", "M3", "M5", "M6"], [10],
                                   {"action_submitted": 1},
                                   window_complete_ns=800_000_000),
})

# ---- C6：NO_HAND / 未知类 / 低分分开计数 ----
c6 = [no_hand(frame_id, 0.0 if frame_id == 1 else 100) for frame_id in range(1, 5)]
c6.append(ok(5, 100, [det(5, 0.90, A)]))                     # class_id 越界 → E_FRAME_INVALID
c6 += [ok(frame_id, 100, [det(0, 0.20, A)]) for frame_id in range(6, 9)]  # 低于 T6-P01
cases.append({
    "case_id": "C6-no-hand-unknown-lowscore",
    "matrix_class": "NO_HAND / 未知类 / 低分",
    "description": "4 帧 NO_HAND（合法零框）+ 1 帧 class_id=5（E_FRAME_INVALID，单独计 unknown_class_frames）+ 3 帧低分（<T6-P01）：全部不触发，分区计数不混用。",
    "events": c6,
    "expected": {
        "final_state": "IDLE",
        "transitions": [],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"no_hand_frames": 4, "unknown_class_frames": 1, "invalid": 1, "ok_frames": 3},
    },
})

# ---- C6b：NO_HAND 携带 detections → 按 §11.3 计非法（N-07） ----
cases.append({
    "case_id": "C6b-no-hand-with-detections",
    "matrix_class": "NO_HAND / 未知类 / 低分",
    "description": "state=NO_HAND 却携带 detections（§11.3 非法输入）：计 E_FRAME_INVALID 并丢弃该帧证据，"
                   "**不**计入 no_hand_frames；2 帧未达异常窗口阈值（W=3）→ 不进入恢复态、无动作。",
    "events": [ev("E_FRAME_RESULT", 1, 0, state="NO_HAND", detections=[det(0, 0.9, A)]),
               ev("E_FRAME_RESULT", 2, 100, state="NO_HAND", detections=[det(0, 0.9, A)])],
    "expected": {
        "final_state": "IDLE",
        "transitions": [],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"invalid": 2, "no_hand_with_detections": 2, "no_hand_frames": 0},
    },
})

# ---- C7：TIMEOUT / ERROR / DROPPED / stale ----
c7 = [ok(1, 0, [det(0, 0.9, A)]), ok(2, 100, [det(0, 0.9, A)])]
c7 += [ev("E_FRAME_TIMEOUT", 3, 100), ev("E_FRAME_ERROR", 4, 100), ev("E_FRAME_DROPPED", 5, 100)]
c7.append(ok(6, 100, [det(0, 0.9, A)], stale=True))
c7 += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(7, 12)]
cases.append({
    "case_id": "C7-timeout-error-dropped-stale",
    "matrix_class": "TIMEOUT / ERROR / DROPPED / stale",
    "description": "3 个异常帧（TIMEOUT/ERROR/DROPPED）达 T6-U00 阈值 → M2→UNKNOWN_RECOVER 并清空目标；stale 帧不触发不计窗口；随后 5 帧合法结果 → M12→IDLE。全程无动作。",
    "events": c7,
    "expected": {
        "final_state": "IDLE",
        "transitions": ["M1", "M2", "M12"],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"timeout": 1, "error": 1, "dropped": 1, "stale": 1},
    },
})

# ---- C8：重复 / 倒序 / 缺帧 / 重启 ----
c8 = [ok(1, 0, [det(0, 0.9, A)]), ok(2, 100, [det(0, 0.9, A)])]
c8.append(ok(2, 100, [det(0, 0.9, A)]))                      # 重复 frame_id
c8.append(ok(5, 100, [det(0, 0.9, A)]))                      # 缺 3、4
c8.append(ok(1, 100, [det(0, 0.9, A)]))                      # 倒序
c8.append(ev("E_FRAME_RESULT", 1, 100, session_id="s2", state="OK", detections=[det(0, 0.9, A)]))
cases.append({
    "case_id": "C8-duplicate-reorder-missing-restart",
    "matrix_class": "重复 / 倒序 / 缺帧 / 重启帧号",
    "description": "重复 frame_id 幂等丢弃；缺帧计 2；倒序计异常；session 变化 → 全量复位（RESET）并清空计数，不延续旧会话状态。全程无动作。",
    "events": c8,
    "expected": {
        "final_state": "IDLE",
        "transitions": ["M1", "RESET"],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
        "core_counters": {"duplicate_frames": 0, "out_of_order_frames": 0, "ok_frames": 0},
        "counter_highs": {"duplicate_frames": 1, "missing_frames": 2, "out_of_order_frames": 1, "ok_frames": 3},
    },
})

# ---- C9c：30fps（P=33.3 ms）时长支配 → 完成帧 = 第 8 帧 233.1 ms（N-r05-04） ----
cases.append({
    "case_id": "C9c-30fps-later-of",
    "matrix_class": "低 FPS / 窗口完成取较晚",
    "description": "30fps（P=33.3 ms，T6-S01=200 ms，T6-S02=6）：第 6 个 WINDOW_MATCH 帧只有 166.5 ms < 200 ms，"
                   "按 T6-S03「取较晚」完成帧是第 8 帧（233.1 ms）→ 第 8 帧 M3、第 9 帧触发；"
                   "若按旧口径（只数帧）会误判为第 6 帧完成。",
    "period_ns": 33_300_000,
    "events": [ok(frame_id, 0.0 if frame_id == 1 else 33.3, [det(0, 0.90, A)])
               for frame_id in range(1, 10)],
    "expected": expected_triggered("UI_MENU", "final_display_state",
                                   ["M1", "M3", "M5", "M6"], [9], {"action_submitted": 1},
                                   window_complete_ns=233_100_000),
})

# ---- C9a：T6-S01 恰好相等 → 满足（周期 40 ms，第 6 帧恰 200 ms） ----
cases.append({
    "case_id": "C9-s01-equal",
    "matrix_class": "时间等于阈值",
    "description": "周期 40 ms：第 6 个 WINDOW_MATCH 帧恰为 200 ms = T6-S01，含等号 → M3 在第 6 帧成立，第 7 帧触发。",
    "period_ns": 40 * MS,
    "events": stable_frames(7, dt_ms=40.0),
    "expected": expected_triggered("UI_MENU", "final_display_state",
                                   ["M1", "M3", "M5", "M6"], [7], {"action_submitted": 1},
                                   window_complete_ns=200_000_000),
})

# ---- C9b：T6-S01 − 1 ns → 不满足，+1 ns 后满足 ----
c9b = stable_frames(5, dt_ms=40.0)
c9b.append(ev("E_FRAME_RESULT", 6, 0, state="OK", detections=[det(0, 0.9, A)]))
c9b[-1]["dt_ns"] = 200 * MS - 1 - 4 * 40 * MS     # 第 6 帧落在 199 999 999 ns
c9b.append(ev("E_FRAME_RESULT", 7, 0, state="OK", detections=[det(0, 0.9, A)]))
c9b[-1]["dt_ns"] = 2                               # 第 7 帧落在 200 000 001 ns
c9b.append(ok(8, 100, [det(0, 0.9, A)]))
cases.append({
    "case_id": "C9-s01-minus-1ns",
    "matrix_class": "时间阈值 −1 个计时单位",
    "description": "第 6 帧落在 T6-S01−1 ns（199 999 999 ns）→ 帧数够但时长不足，不进入 STABLE；第 7 帧落在 T6-S01+1 ns → 成立；第 8 帧触发。",
    "period_ns": 40 * MS,
    "events": c9b,
    "expected": expected_triggered("UI_MENU", "final_display_state",
                                   ["M1", "M3", "M5", "M6"], [8], {"action_submitted": 1},
                                   window_complete_ns=200_000_001),
})

# ---- C10：无新结果但时间前进（E_TICK） ----
cases.append({
    "case_id": "C10-tick-time-advance",
    "matrix_class": "无新结果但时间前进",
    "description": "2 帧建立候选后只有时钟推进：距最近一次 TARGET_CONTINUES 成立达 T6-L02=300 ms → M10→LOST，下一 tick M11→IDLE；全程无动作。",
    "events": [ok(1, 0, [det(0, 0.9, A)]), ok(2, 100, [det(0, 0.9, A)]),
               tick(100), tick(100), tick(100), tick(100)],
    "expected": {
        "final_state": "IDLE",
        "transitions": ["M1", "M10", "M11"],
        "submitted_at_frames": [],
        "action_summary": {"action_submitted": 0, "action_effective": 0},
    },
})

# ---- C11a：动作失败不虚报成功（失败后可重试） ----
cases.append({
    "case_id": "C11-fail-then-success",
    "matrix_class": "动作失败 / 未观察",
    "outcome_policy": {"fail_attempts": [1]},
    "description": "第 1 次提交执行层返回 fail：不产生 ACTION_SUBMITTED、不更新冷却锚点、不计成功；下一窗口推进帧重新提交成功 → 恰好一次成功。",
    "events": stable_frames(8),
    "expected": {
        "final_state": "COOLDOWN",
        "transitions": ["M1", "M3", "M5", "M5", "M6"],
        "submitted_at_frames": [8],
        "action_summary": {"action_submitted": 1, "action_effective": 1, "action_failed": 1,
                           "visible_state_changes": 1, "final_display_state": "UI_MENU"},
    },
})

# ---- C11b：未观察不计成功 ----
cases.append({
    "case_id": "C11-unobserved",
    "matrix_class": "动作未观察",
    "outcome_policy": {"unobserved_attempts": [1]},
    "description": "提交成功但未观察到生效：ACTION_SUBMITTED 计入、ACTION_EFFECTIVE 不计入、可见状态不变（H-8/B28）。",
    "events": stable_frames(8),
    "expected": {
        "final_state": "COOLDOWN",
        "transitions": ["M1", "M3", "M5", "M6"],
        "submitted_at_frames": [7],
        "action_summary": {"action_submitted": 1, "action_effective": 0, "action_unobserved": 1,
                           "visible_state_changes": 0, "final_display_state": None},
        "core_counters": {"unobserved": 1},
    },
})

# ---- C11c：全局冷却门跨获取（H-10） ----
period = 20.0
c11c = stable_frames(12, dt_ms=period)                        # 第 11 帧 M3、第 12 帧触发（t=220 ms）
c11c += [no_hand(frame_id, period) for frame_id in range(13, 18)]   # 5 帧 NO_HAND → M10
c11c.append(no_hand(18, period))                              # M11 → IDLE
c11c += stable_frames(14, start=19, dt_ms=period)             # 重新获取
cases.append({
    "case_id": "C11-global-gate-second-acquisition",
    "matrix_class": "冷却后保持 / 全局冷却门",
    "description": "第 12 帧触发（t_submit=220 ms）；目标丢失后重获并再次满足窗口（第 29 帧 M3），但 t_now−t_submit=360 ms < T6-K01=1000 ms → M5 被 H-10 抑制（S_COOLDOWN），全程只提交一次。",
    "period_ns": int(period * MS),
    "events": c11c,
    "expected": {
        "final_state": "STABLE",
        "submitted_at_frames": [12],
        "action_summary": {"action_submitted": 1, "action_effective": 1},
        "core_counters": {"no_hand_frames": 6, "action_submitted": 1},
        "suppressions_include": ["S_COOLDOWN"],
        "window_complete_ns": 200_000_000,
    },
})


# ---- C12：acquisition_id 生命周期（BLK-r03-1，终审 B）----------------------------------
# 设计语义（非回填）：结束一次获取的迁移（M11/M4/M8/M2/M12）与目标切换各自分配新 id；
# 触发时记录 acquisition_id，故"两次触发"的 id 序列就是"两次获取"的逐次凭据。

# (a) M8 路径两次触发 → [0,1]
#     语义：f1..f7 获取并触发（id 0）→ 冷却期内保持目标 → 冷却结束帧起目标缺失且缺失时长 < T6-L02=300ms
#     （M10 不先命中）→ **M8**（结束获取，id 1）→ 重新获取并再次触发（id 1）。
c12a = stable_frames(7)                                     # f1..f7：获取 + 触发（id 0）
c12a += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(8, 16)]
c12a += [no_hand(frame_id, 100) for frame_id in range(16, 22)]   # 冷却结束帧目标缺失 → M8（M10 未先命中）
c12a += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(22, 36)]   # 重新获取并再次触发（id 1）
cases.append({
    "case_id": "C12-m8-two-acquisitions",
    "matrix_class": "id 生命周期",
    "description": "BLK-r03-1：M8（COOLDOWN 结束且目标缺失、M10 未先命中）结束一次获取并分配新 acquisition_id；该路径两次触发应得 [0,1]。",
    "events": c12a,
    "expected": {
        "final_state": "COOLDOWN",
        "transitions": ["M1", "M3", "M5", "M6", "M8", "M1", "M3", "M5", "M6"],
        "submitted_at_frames": [7, 28],
        "window_complete_ns": 500_000_000,
        "action_summary": {"action_submitted": 2, "action_effective": 2},
        "acquisition_ids": [0, 1],
    },
})

# (b) M5→M2→M12→新目标→M5 → 新 id（M2/M12 各分配一次，故第二次触发的 id 为 2）
c12b = stable_frames(12)
c12b += [ev("E_FRAME_TIMEOUT", 13, 100), ev("E_FRAME_ERROR", 14, 100), ev("E_FRAME_DROPPED", 15, 100)]
c12b += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(16, 22)]
c12b += stable_frames(12, start=22)
cases.append({
    "case_id": "C12-m2-m12-new-target",
    "matrix_class": "id 生命周期",
    "description": "BLK-r03-1：M5→M2（恢复态）→M12（恢复出口）→新目标→M5 必须使用新的 acquisition_id（两个出口各分配一次）。",
    "events": c12b,
    "expected": {
        "final_state": "COOLDOWN",
        "transitions": ["M1", "M3", "M5", "M6", "M2", "M12", "M1", "M3", "M5", "M6"],
        "submitted_at_frames": [7, 27],
        "window_complete_ns": 500_000_000,
        "action_summary": {"action_submitted": 2, "action_effective": 2},
        "acquisition_ids": [0, 2],
    },
})

# (c) 三次获取连续：M8（id 1）后再经 M10→M11（id 2）再触发 → 三段 id 各自独立
c12c = stable_frames(7)                                     # f1..f7：获取 + 触发（id 0，t_submit≈600 ms）
c12c += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(8, 16)]   # 冷却期内保持（M9）
c12c += [no_hand(frame_id, 100) for frame_id in range(16, 22)]               # ≥T6-L02 → M10 → M11（结束获取，id 1）
c12c += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(22, 36)]  # 重新获取并再次触发（id 1）
c12c += [no_hand(frame_id, 100) for frame_id in range(36, 42)]               # ≥T6-L02 → M10 → M11（结束获取，id 2）
c12c += [ok(frame_id, 100, [det(0, 0.9, A)]) for frame_id in range(42, 60)]  # 第三次获取 → 触发（id 2）
cases.append({
    "case_id": "C12-gate-reopen-new-acquisition",
    "matrix_class": "id 生命周期",
    "description": "BLK-r03-1：三段获取（首触发 → M8 结束 → 再触发 → M10/M11 结束 → 再触发）的 acquisition_id 必须逐段独立，不得复用。",
    "events": c12c,
    "expected": {
        "final_state": "STABLE",
        "transitions": ["M1", "M3", "M5", "M6", "M8", "M1", "M3", "M5", "M6", "M10", "M11", "M1", "M3", "M5", "M6", "M9"],
        "submitted_at_frames": [7, 28, 48],
        "window_complete_ns": 500_000_000,
        "action_summary": {"action_submitted": 3, "action_effective": 3},
        "acquisition_ids": [0, 1, 2],
    },
})

CDX_ORDER = [
    "每类稳定输入",
    "持续保持与冷却后保持",
    "手离开再出现",
    "两类快速切换/短暂抖动",
    "多目标/同分/目标跳变",
    "NO_HAND / 场景未知 / 低分",
    "TIMEOUT / ERROR / DROPPED / stale",
    "重复、倒序、缺帧、重启帧号",
    "时间等于阈值、前后 1 个计时单位",
    "无新结果但时间持续前进",
    "动作失败/未观察/重复 ACK",
    "id 生命周期",
]

CDX_CLASS_MAPPING = {
    "id 生命周期": "id 生命周期",
    "每类稳定输入": "每类稳定输入",
    "持续保持与冷却后保持": "持续保持与冷却后保持",
    "冷却后保持 / 全局冷却门": "持续保持与冷却后保持",
    "手离开再出现": "手离开再出现",
    "短暂抖动": "两类快速切换/短暂抖动",
    "两类快速切换": "两类快速切换/短暂抖动",
    "多目标/同分": "多目标/同分/目标跳变",
    "多目标/维持优先": "多目标/同分/目标跳变",
    "多目标/目标跳变": "多目标/同分/目标跳变",
    "NO_HAND / 未知类 / 低分": "NO_HAND / 场景未知 / 低分",
    "TIMEOUT / ERROR / DROPPED / stale": "TIMEOUT / ERROR / DROPPED / stale",
    "重复 / 倒序 / 缺帧 / 重启帧号": "重复、倒序、缺帧、重启帧号",
    "时间等于阈值": "时间等于阈值、前后 1 个计时单位",
    "时间阈值 −1 个计时单位": "时间等于阈值、前后 1 个计时单位",
    "低 FPS / 窗口完成取较晚": "时间等于阈值、前后 1 个计时单位",
    "无新结果但时间前进": "无新结果但时间持续前进",
    "动作失败 / 未观察": "动作失败/未观察/重复 ACK",
    "动作未观察": "动作失败/未观察/重复 ACK",
}

coverage: dict[str, list[str]] = {name: [] for name in CDX_ORDER}
for _case in cases:
    _cdx = CDX_CLASS_MAPPING.get(_case["matrix_class"])
    if _cdx is None:
        raise SystemExit(f"用例 {_case['case_id']} 的 matrix_class 未映射到 CDX 类别：{_case['matrix_class']}")
    coverage[_cdx].append(_case["case_id"])
if any(not ids for ids in coverage.values()):
    raise SystemExit(f"CDX 类别无用例覆盖：{[k for k, v in coverage.items() if not v]}")
if sum(len(v) for v in coverage.values()) != len(cases):
    raise SystemExit("覆盖映射存在重复或遗漏")

matrix = {
    "schema_version": 1,
    "artifact": "s6b_case_matrix",
    "task_id": "S6-B",
    "run_id": RUN.name,
    "contract_version": "S6A-G0-v1.8",
    "cdx_class_mapping": CDX_CLASS_MAPPING,
    "case_class_coverage": coverage,
    "runbook_matrix_coverage": [
        {"case_class": name, "cases": coverage[name]} for name in CDX_ORDER
    ],
    "expected_derivation_note": (
        "expected 全部由行为表 v1.4（§4 迁移表、§9 窗口、§10 冷却/一次获取一次、§13 帧序、§14 参数草案值）"
        "人工推导：周期、帧号、时间偏移均在用例内显式给出；不使用状态机输出作为预期（H-7）。"
        "参数全部为 APPROVED_20261023（2026-10-23 批准；值仍为草案值），任何结论只对注入输入有效。"
    ),
    "cases": cases,
}

(RUN / "cases").mkdir(parents=True, exist_ok=True)
(RUN / "cases" / "case_matrix.json").write_text(
    json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"cases={len(cases)}")
print("classes=", sorted({case["matrix_class"] for case in cases}))
print("cases=", [case["case_id"] for case in cases])
