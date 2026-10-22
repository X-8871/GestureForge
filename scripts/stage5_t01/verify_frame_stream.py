"""S5-T01 §4/T5-05 帧流校验：把 UART 的 `S5_5T*` 行与**文档化的确定性调度模型**逐轮比对。

调度模型（与板上 r05 应用一致，纯算术、可审阅）：
  k=0..119：case = k%6；age_result = 250ms（k%7==0）否则 k ms；age_frame = age_result + 5ms
            warm  = k<9
            DROP  = k>9 且 k%17==0      → 不显示，计 dropped
            TIMEOUT = k>9 且 k%19==0    → 不显示，计 timeouts
            DUP   = k>9 且 k%23==0      → result 沿用上一条（不改写 frame_id），计 dup
            OOO   = k>9 且 k%29==0      → result = k-3，计 ooo
            其余 result = k
  stale = age_result > 200ms（契约同源常量）⇒ 不画框、stale_cleared+1

校验：
 1. 每个**完整** round 的 (displayed, result) 序列与模型**完全一致**（尾部截断轮跳过并说明）；
 2. 计数（displayed/stale/dropped/timeouts/dup/ooo/warmup/uniq）与模型一致；
 3. `semantics` 全为 B；`age_frame>=age_result`；`stale=1⇒boxes=0`；`stale ⇔ age>limit`；
 4. FPS 可由 displayed/elapsed_ms 复算；
 5. 观测模式（连续相等/回退）与标记计数的差异必须**能被 OOO 目标撞上一条结果**解释（逐条列出）。

用法：python -B scripts/stage5_t01/verify_frame_stream.py --log <uart log> [--json out] [--expect-frames 120] [--soak-minutes N]
退出码：0=全通过；1=有失败；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

N_FRAMES = 120
STALE_LIMIT_NS = 200_000_000
RE_5T = re.compile(
    r"S5_5T displayed=(\d+) result=(\d+) age_result_ns=(\d+) age_frame_ns=(\d+) semantics=(\S+) "
    r"boxes=(\d+) stale=(\d) warm=(\d) occ=(\d+)")
RE_SKIP = re.compile(r"S5_5T_SKIP frames=(\d+) kind=(DROP|TIMEOUT)")
RE_SUM = re.compile(
    r"S5_5T_SUMMARY round=(\d+) frames=(\d+) displayed=(\d+) stale_cleared=(\d+) dropped=(\d+) "
    r"timeouts=(\d+) dup=(\d+) ooo=(\d+) warmup=(\d+) uniq_displayed=(\d+) elapsed_(?:ms|ns)=(\d+) "
    r"display_fps_x10=(\d+) unique_frame_update_fps_x10=(\d+) occ_max=(\d+)")


def build_model(n: int = N_FRAMES) -> dict:
    """确定性调度模型：返回期望的显示序列与计数。"""
    shown: list[dict] = []
    dropped = timeouts = warm = stale = dup = ooo = uniq = 0
    last: int | None = None
    coincidences: list[str] = []
    for k in range(n):
        age = 250_000_000 if (k % 7 == 0) else k * 1_000_000
        age_frame = age + 5_000_000
        is_warm = k < 9
        if is_warm:
            warm += 1
        if k > 9 and k % 17 == 0:
            dropped += 1
            continue
        if k > 9 and k % 19 == 0:
            timeouts += 1
            continue
        result = k
        flag = "NORMAL"
        if k > 9 and k % 23 == 0 and last is not None:
            result = last
            dup += 1
            flag = "DUP"
        if k > 9 and k % 29 == 0:
            result = k - 3
            ooo += 1
            flag = "OOO"
            if last is not None and result == last:
                coincidences.append(f"k={k} OOO 目标 {result} 恰等于上一条结果 ⇒ 观测上表现为重复")
        is_stale = age > STALE_LIMIT_NS
        if is_stale:
            stale += 1
        if result != last:
            uniq += 1
        shown.append({"k": k, "result": result, "age": age, "age_frame": age_frame,
                      "stale": int(is_stale), "warm": int(is_warm), "flag": flag})
        last = result
    return {"shown": shown, "dropped": dropped, "timeouts": timeouts, "warm": warm,
            "stale": stale, "dup": dup, "ooo": ooo, "uniq": uniq, "coincidences": coincidences}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--expect-frames", type=int, default=N_FRAMES)
    ap.add_argument("--soak-minutes", type=float, default=0.0)
    args = ap.parse_args()

    path = pathlib.Path(args.log)
    if not path.is_absolute():
        path = pathlib.Path.cwd() / path
    if not path.exists():
        print(f"[verify] 不存在：{path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")

    rows = [{"displayed": int(m.group(1)), "result": int(m.group(2)),
             "age_result_ns": int(m.group(3)), "age_frame_ns": int(m.group(4)),
             "semantics": m.group(5), "boxes": int(m.group(6)),
             "stale": int(m.group(7)), "warm": int(m.group(8)), "occ": int(m.group(9))}
            for m in RE_5T.finditer(text)]
    skips = [{"frames": int(m.group(1)), "kind": m.group(2)} for m in RE_SKIP.finditer(text)]
    sums = []
    for m in RE_SUM.finditer(text):
        unit = "ms" if "elapsed_ms=" in m.group(0) else "ns"
        raw = int(m.group(11))
        sums.append({"round": int(m.group(1)), "frames": int(m.group(2)), "displayed": int(m.group(3)),
                     "stale_cleared": int(m.group(4)), "dropped": int(m.group(5)), "timeouts": int(m.group(6)),
                     "dup": int(m.group(7)), "ooo": int(m.group(8)), "warmup": int(m.group(9)),
                     "uniq_displayed": int(m.group(10)), "elapsed_raw": raw, "elapsed_unit": unit,
                     "elapsed_s": (raw / 1000.0) if unit == "ms" else (raw / 1e9),
                     "fps_recomputable": unit == "ms",
                     "display_fps_x10": int(m.group(12)), "unique_fps_x10": int(m.group(13)),
                     "occ_max": int(m.group(14))})
    if not rows or not sums:
        print(f"[verify] 数据不足：rows={len(rows)} summaries={len(sums)}")
        return 2

    residue = [s for s in sums if not s["fps_recomputable"]]
    sums = [s for s in sums if s["fps_recomputable"]]
    if not sums:
        print("[verify] 仅有 elapsed_ns（历史截断）轮次，无法复算")
        return 2

    model = build_model(args.expect_frames)
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    # 切分 round（displayed 归零），只取最后 len(sums) 段
    segs: list[list[dict]] = []
    cur: list[dict] = []
    for row in rows:
        if row["displayed"] == 0 and cur:
            segs.append(cur)
            cur = []
        cur.append(row)
    if cur:
        segs.append(cur)
    segs = segs[-len(sums):]
    complete = [s for s in segs if len(s) == model["shown"].__len__()]
    truncated = [len(s) for s in segs if len(s) != len(model["shown"])]

    add("rounds_present", len(sums) >= 1, f"可复算 round 数={len(sums)}，完整轮={len(complete)}，截断轮长度={truncated}")
    add("at_least_one_complete_round", len(complete) >= 1, f"完整轮数={len(complete)}")

    # 1) 逐帧序列与模型一致
    seq_ok, seq_detail = True, []
    for ri, seg in enumerate(complete):
        exp = [(i, m["result"]) for i, m in enumerate(model["shown"])]
        got = [(r["displayed"], r["result"]) for r in seg]
        if got != exp:
            seq_ok = False
            diff = [f"#{i}: got={g} exp={e}" for i, (g, e) in enumerate(zip(got, exp)) if g != e][:3]
            seq_detail.append(f"round{ri} 序列不一致：{diff}")
    add("displayed_result_sequence_matches_model", seq_ok,
        "; ".join(seq_detail) or f"{len(complete)} 个完整轮的 (displayed,result) 序列与调度模型完全一致")

    # 2) 计数与模型一致（只对完整轮）
    cnt_ok, cnt_detail = True, []
    for ri, s in enumerate(sums):
        if ri >= len(complete):
            continue
        expect = {"displayed": len(model["shown"]), "stale_cleared": model["stale"],
                  "dropped": model["dropped"], "timeouts": model["timeouts"], "dup": model["dup"],
                  "ooo": model["ooo"], "warmup": model["warm"], "uniq_displayed": model["uniq"]}
        bad = {k: (s[k], v) for k, v in expect.items() if s[k] != v}
        if bad:
            cnt_ok = False
            cnt_detail.append(f"round{ri} 计数与模型不符（实测,期望）={bad}")
    add("counters_match_model", cnt_ok, "; ".join(cnt_detail) or
        f"计数与模型一致：displayed={len(model['shown'])}, stale={model['stale']}, dropped={model['dropped']}, "
        f"timeouts={model['timeouts']}, dup={model['dup']}, ooo={model['ooo']}, warmup={model['warm']}, "
        f"uniq={model['uniq']}")

    # 3) 五元组语义
    add("semantics_unique_B", all(r["semantics"] == "B" for r in rows),
        f"出现过的 semantics={sorted({r['semantics'] for r in rows})}")
    add("age_frame_ge_age_result", all(r["age_frame_ns"] >= r["age_result_ns"] for r in rows),
        "全部满足 age_frame_ns >= age_result_ns")
    add("stale_implies_no_box", all(r["boxes"] == 0 for r in rows if r["stale"] == 1),
        f"stale 行数={sum(1 for r in rows if r['stale'] == 1)}")
    bad_stale = [r for r in rows if (r["stale"] == 1) != (r["age_result_ns"] > STALE_LIMIT_NS)]
    add("stale_iff_age_over_limit", not bad_stale,
        f"违反条数={len(bad_stale)}（判据 age_result_ns > {STALE_LIMIT_NS}）")

    # 4) 观测模式 vs 标记计数（差异须由 OOO 撞值解释）
    pattern_dup = pattern_ooo = 0
    for seg in complete:
        for i in range(1, len(seg)):
            if seg[i]["result"] < seg[i - 1]["result"]:
                pattern_ooo += 1
            elif seg[i]["result"] == seg[i - 1]["result"]:
                pattern_dup += 1
    n_complete = len(complete)
    exp_pat_dup = (model["dup"] + len(model["coincidences"])) * n_complete
    exp_pat_ooo = (model["ooo"] - len(model["coincidences"])) * n_complete
    add("pattern_vs_flag_counts_explained",
        pattern_dup == exp_pat_dup and pattern_ooo == exp_pat_ooo,
        f"观测 dup={pattern_dup}/ooo={pattern_ooo}；标记 dup={model['dup']*n_complete}/"
        f"ooo={model['ooo']*n_complete}；撞值解释={len(model['coincidences'])}×{n_complete}"
        + (f"；撞值明细：{model['coincidences']}" if model["coincidences"] else ""))

    # 5) FPS 复算
    fps_ok, fps_detail = True, []
    for s in sums:
        if s["elapsed_s"] <= 0:
            fps_ok = False
            fps_detail.append(f"round{s['round']} elapsed 非法")
            continue
        calc = s["displayed"] * 10 / s["elapsed_s"]
        calc_u = s["uniq_displayed"] * 10 / s["elapsed_s"]
        if abs(calc - s["display_fps_x10"]) > 1 or abs(calc_u - s["unique_fps_x10"]) > 1:
            fps_ok = False
            fps_detail.append(f"round{s['round']}: display {calc:.1f} vs {s['display_fps_x10']}, "
                              f"uniq {calc_u:.1f} vs {s['unique_fps_x10']}")
    add("fps_recomputable", fps_ok,
        "; ".join(fps_detail) or "display/unique FPS 可由 displayed/elapsed_ms 复算一致")

    total_s = sum(s["elapsed_s"] for s in sums)
    if args.soak_minutes > 0:
        add("soak_duration_ge_required", total_s >= args.soak_minutes * 60 * 0.98,
            f"累计运行 {total_s/60:.2f} 分钟，要求 ≥{args.soak_minutes} 分钟（含 2% 容差）")

    skipped = [s["round"] for s in residue]
    failed = [c for c in checks if c["status"] == "FAIL"]
    summary = {
        "log": str(path), "rounds_recomputable": len(sums), "complete_rounds": n_complete,
        "truncated_round_lengths": truncated, "rows": len(rows), "skips": len(skips),
        "residue_rounds_excluded": skipped, "total_runtime_s": round(total_s, 3),
        "model": {"displayed": len(model["shown"]), "stale": model["stale"], "dropped": model["dropped"],
                  "timeouts": model["timeouts"], "dup": model["dup"], "ooo": model["ooo"],
                  "warmup": model["warm"], "uniq": model["uniq"],
                  "coincidences": model["coincidences"]},
        "observed": {"pattern_dup": pattern_dup, "pattern_ooo": pattern_ooo,
                     "per_round": sums},
        "checks": checks, "passed": len(checks) - len(failed), "failed": len(failed),
        "occ_max": max(s["occ_max"] for s in sums),
        "not_claimed": ["result 流为**合成**（非阶段4 真实输出）；本校验只覆盖显示侧消费语义。",
                        "`unique_frame_update_fps` 为 result-frame_id 级，不是推理完成率。",
                        "dup/ooo 的标记计数由调度模型解释；观测模式在 OOO 撞值时会表现为重复（已逐条列出）。"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        out = pathlib.Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[verify] PASS={summary['passed']} FAIL={summary['failed']} complete_rounds={n_complete} "
          f"runtime_s={summary['total_runtime_s']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())