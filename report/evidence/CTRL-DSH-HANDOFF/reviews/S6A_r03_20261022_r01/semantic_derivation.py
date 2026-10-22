"""Reviewer 独立语义推演 v2（不复用被审 selfcheck 的 recompute 代码）。

严格按 r03 规格实现最小状态机：
  TARGET_CONTINUES = 同类 且 (IoU>=P03 或 中心位移<=P04)
  WINDOW_MATCH     = TARGET_CONTINUES 且 score>=P02 且 与上一个 WINDOW_MATCH 帧位移<=P05
  M1  IDLE->CANDIDATE : 连续 C01 条窗口推进帧为同一目标（TARGET_CONTINUES 判定同一性）
  M3  CANDIDATE->STABLE: 连续 WINDOW_MATCH 帧数>=S02 且 时长>=S01（later_of）
  M10 *->LOST          : TARGET_CONTINUES 不成立连续>=L01 或 距上一次 TARGET_CONTINUES 成立>=L02
  M5  STABLE->TRIGGERED: 本次获取未触发 且 t-t_last_submit>=K01
抖动（§9）：窗口内不满足 WINDOW_MATCH 的推进帧 <=J01 不重置；达到 J01+1 立即重置。
求值顺序：M10(P2) -> P3 状态推进 -> M1(P4)。
"""
PARAMS = dict(P01=0.35, P02=0.30, P03=0.30, P04=0.15, P05=0.05, C01=2,
              S01=200.0, S02=6, S04=500.0, L01=5, L02=300.0, K01=1000.0, J01=1)


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def ctr(b):
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


def dist(a, b):
    (x1, y1), (x2, y2) = ctr(a), ctr(b)
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def simulate(frames, period_ms, mode="spec", p=PARAMS):
    state = "IDLE"
    target = cls_t = None
    acq_streak = 0
    wm_count = 0
    wm_start = None
    last_wm_box = None
    last_wm_t = None
    miss = 0
    tc_false = 0
    last_tc_t = None
    triggered = False
    acq_frames = 0
    acq_t = None
    t_last_submit = None
    events, trace = [], []
    ever_stable = False
    for idx, (score, box, cls) in enumerate(frames):
        t = idx * period_ms
        tc = False
        if target is not None and cls == cls_t:
            tc = (iou(target, box) >= p["P03"]) or (dist(target, box) <= p["P04"])
        wm = False
        if tc:
            # 窗口首个 WINDOW_MATCH 帧无前序帧 → 作为锚点，不受 P05 约束
            dp = 0.0 if last_wm_box is None else dist(last_wm_box, box)
            wm = (score >= p["P02"]) and (dp <= p["P05"])

        # ---- M10（P2）----
        if target is not None:
            if tc:
                tc_false = 0
                last_tc_t = t
            else:
                tc_false += 1
            lost = False
            if tc_false >= p["L01"]:
                lost = True
            if mode == "wrong_m10":
                if last_wm_t is not None and (t - last_wm_t) >= p["L02"]:
                    lost = True
            else:
                if last_tc_t is not None and (t - last_tc_t) >= p["L02"]:
                    lost = True
            if lost:
                events.append(("M10", t, "LOST"))
                state, target, cls_t = "LOST", None, None
                acq_streak = wm_count = miss = tc_false = 0
                acq_frames, acq_t = 0, None
                wm_start = last_wm_box = last_wm_t = last_tc_t = None
                triggered = False
                trace.append((t, "LOST", wm, tc, 0))
                continue

        # ---- 窗口计数 / 抖动（§9）----
        if target is not None:
            if wm:
                if wm_count == 0:
                    wm_start = t
                wm_count += 1
                miss = 0
                last_wm_box = box
                last_wm_t = t
            else:
                miss += 1
                if miss > p["J01"]:
                    wm_count, wm_start, last_wm_box, miss = 0, None, None, 0
        count = wm_count
        if mode == "wrong_m3" and target is not None:
            # 缺陷模型：直接按 TARGET_CONTINUES 连续帧计稳定帧数、窗口起点=获取时刻
            if tc:
                acq_frames += 1
            else:
                acq_frames = 0
            if acq_t is None:
                acq_t = t
            count = acq_frames
            wm_start = acq_t

        # ---- M1（P4）----
        if target is None and score >= p["P01"]:
            target, cls_t, acq_streak = box, cls, 1
            acq_frames, acq_t = 1, t
            last_tc_t, tc_false = t, 0
            if acq_streak >= p["C01"]:
                state = "CANDIDATE"
            trace.append((t, state, wm, tc, count))
            continue
        if target is not None and state == "IDLE" and tc:
            acq_streak += 1
            if acq_streak >= p["C01"]:
                state = "CANDIDATE"

        # ---- M3 / M5（P3）：同一帧最多一条迁移 ----
        fired = False
        if state == "CANDIDATE":
            dur = 0.0 if wm_start is None else (t - wm_start)
            if count >= p["S02"] and dur >= p["S01"]:
                state, ever_stable, fired = "STABLE", True, True
                events.append(("M3", t, "STABLE"))
        if state == "STABLE" and not triggered and not fired:
            if t_last_submit is None or (t - t_last_submit) >= p["K01"]:
                triggered = True
                t_last_submit = t
                events.append(("M5", t, "ACTION_SUBMITTED"))
                state = "COOLDOWN"
        trace.append((t, state, wm, tc, count))
    return dict(state=state, submitted=len([e for e in events if e[0] == "M5"]),
                events=events, trace=trace, ever_stable=ever_stable)


A = (0.40, 0.45, 0.60, 0.65)
B = (0.41, 0.46, 0.61, 0.66)


def show(tag, r):
    print("%-22s state=%-10s submitted=%d stable=%s events=%s" %
          (tag, r["state"], r["submitted"], r["ever_stable"], r["events"]))


if __name__ == "__main__":
    print("A) 先以 0.40 建立获取(1 帧)，随后 score=0.28 < P02、几何连续 8 帧，P=33.3ms")
    fr = [(0.40, A, 0)] + [(0.28, B, 0)] * 8
    show("spec", simulate(fr, 33.3))
    show("误按 TC 计稳定帧", simulate(fr, 33.3, mode="wrong_m3"))

    print("\nB) 建立获取后 score 跌破 P02 且几何连续 5 帧，P=100ms（跨过 L02=300ms）")
    fr = [(0.40, A, 0)] * 2 + [(0.28, B, 0)] * 5
    show("spec", simulate(fr, 100.0))
    show("误按 WM 判丢失", simulate(fr, 100.0, mode="wrong_m10"))

    print("\nC) 正常高质量 10 帧，P=33.3ms（规格应能进 STABLE 且只触发一次）")
    fr = [(0.40, A, 0)] * 10
    show("spec", simulate(fr, 33.3))
    show("误按 TC 计稳定帧", simulate(fr, 33.3, mode="wrong_m3"))

    print("\nD) 高分成稳 + 触发后 score 跌破 P02、几何连续 8 帧，P=100ms")
    fr = [(0.40, A, 0)] * 8 + [(0.28, B, 0)] * 8
    show("spec", simulate(fr, 100.0))
    show("误按 WM 判丢失", simulate(fr, 100.0, mode="wrong_m10"))
