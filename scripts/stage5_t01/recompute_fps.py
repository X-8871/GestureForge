"""S5-T01 §3 FPS 复算（从原始 UART 日志独立重算，不信任板上算出的值）。

关键：UART 日志可能**跨多个应用会话**（前一次运行的应用仍在输出，随后下载新 ELF 重启）。
本脚本先按 `S5_P1_BEGIN … rev=` 把日志**分段**，逐段聚合，并把**最后一段**作为权威结果，
其余段落保留在 `segments` 中作为历史/负向证据（例如 r03 的 VTC 位选择错误 → vtc_events=0）。

复算口径：fps = 事件数 × counts_per_second / dt_counts，并与板上打印的 `*_fps_x10` 逐行比对。

语义（必须随结果报告）：
- `video_refresh_events_per_s`：VTC 中断事件率；本设计实测 **每帧 2 次事件**（ISR 位 12/13/16 同置），
  故 `video_refresh_frames_per_s = 事件率 / 2`。
- `display_fps`：MM2S FrmCntIrq（CR[23:16]=1 ⇒ 每帧一次）= 显示帧完成率。
- `unique_frame_update_fps`：内容提交率（本轮为用例级；frame_id 级需 T5-05）。
- `inference_fps`：无阶段4 注入源 ⇒ NOT_APPLICABLE（日志 NA）。

用法：python -B scripts/stage5_t01/recompute_fps.py --log <uart log> [--json out.json] [--warmup-windows 1]
退出码：0=最新段逐行一致；1=不一致或无可复算行；2=输入错误。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

RE_CLOCK = re.compile(r"S5_P1_CLOCK counts_per_second=(\d+)")
RE_BEGIN = re.compile(r"S5_P1_BEGIN .*?rev=(\S+)")
RE_FPS4 = re.compile(
    r"S5_FPS4 case=(\d+) win=(\d+) vtc_events=(\d+) mm2s_events=(\d+) dt_counts=(\d+) "
    r"video_refresh_fps_x10=(-?\d+) display_fps_x10=(-?\d+) inference_fps=(\S+).*?"
    r"(?:vtc_b12=(\d+) vtc_b13=(\d+) vtc_b16=(\d+) vtc_other=(\d+))?")
RE_LAT = re.compile(r"S5_LAT case=(\d+) commit_to_frame_complete_ns=(\d+|NA)")


def segment(text: str) -> list[dict]:
    """按 S5_P1_BEGIN 切段，返回 [{rev, text}]；首段（若在 BEGIN 之前有输出）记为 pre_boot。"""
    marks = list(RE_BEGIN.finditer(text))
    out: list[dict] = []
    if not marks:
        return [{"rev": "unknown", "text": text}]
    if marks[0].start() > 0:
        out.append({"rev": "pre_boot_output", "text": text[:marks[0].start()]})
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append({"rev": m.group(1), "text": text[m.start():end]})
    return out


def analyze(seg_text: str, rate: int, warmup: int) -> dict:
    rows = []
    for m in RE_FPS4.finditer(seg_text):
        case, win, vtc, mm2s, dt, vr_x10, df_x10, inf = (
            int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)),
            int(m.group(5)), int(m.group(6)), int(m.group(7)), m.group(8))
        if dt <= 0:
            continue
        vr_calc = vtc * 10 * rate / dt
        df_calc = mm2s * 10 * rate / dt
        rows.append({
            "case": case, "win": win, "vtc_events": vtc, "mm2s_events": mm2s, "dt_counts": dt,
            "dt_s": round(dt / rate, 6),
            "video_refresh_events_per_s": round(vtc * rate / dt, 3),
            "video_refresh_frames_per_s": round(vtc * rate / dt / 2.0, 3),
            "display_fps": round(mm2s * rate / dt, 3),
            "logged_video_refresh_fps_x10": vr_x10,
            "logged_display_fps_x10": df_x10,
            "match_logged": (abs(vr_calc - vr_x10) < 1.0) and (abs(df_calc - df_x10) < 1.0),
            "inference_fps_field": inf,
            "vtc_b12": int(m.group(9)) if m.group(9) else None,
            "vtc_b13": int(m.group(10)) if m.group(10) else None,
            "vtc_b16": int(m.group(11)) if m.group(11) else None,
            "vtc_other": int(m.group(12)) if m.group(12) is not None else None,
        })
    lats = [{"case": int(m.group(1)),
             "commit_to_frame_complete_ns": (None if m.group(2) == "NA" else int(m.group(2)))}
            for m in RE_LAT.finditer(seg_text)]
    if not rows:
        return {"rows": 0, "useful": False, "latency": lats}
    steady = rows[warmup:]
    basis = steady if steady else rows
    total_vtc = sum(r["vtc_events"] for r in basis)
    total_mm2s = sum(r["mm2s_events"] for r in basis)
    total_dt = sum(r["dt_counts"] for r in basis)
    return {
        "rows": len(rows), "windows_total": len(rows), "useful": True,
        "warmup_windows_excluded": min(warmup, len(rows)),
        "aggregate": {
            "window_s": round(total_dt / rate, 6),
            "vtc_events": total_vtc, "mm2s_events": total_mm2s,
            "video_refresh_events_per_s": round(total_vtc * rate / total_dt, 3) if total_dt else None,
            "video_refresh_frames_per_s": round(total_vtc * rate / total_dt / 2.0, 3) if total_dt else None,
            "display_fps": round(total_mm2s * rate / total_dt, 3) if total_dt else None,
            "inference_fps": "NOT_APPLICABLE (no stage-4 source; logged NA)",
            "unique_frame_update_fps": "case-level only (see S5_P1_SHOW uniq_case_updates); per-frame_id needs T5-05",
        },
        "consistency": {"all_rows_match_logged": all(r["match_logged"] for r in rows),
                        "mismatch_rows": [r["win"] for r in rows if not r["match_logged"]]},
        "vtc_bit_rates_per_s": {
            "b12": round((rows[-1]["vtc_b12"] - rows[0]["vtc_b12"]) * rate /
                         max(1, sum(r["dt_counts"] for r in rows[1:])), 3)
            if rows[0].get("vtc_b12") is not None and rows[-1].get("vtc_b12") is not None else None,
        },
        "latency": lats,
        "rows_detail": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--json", default=None)
    parser.add_argument("--warmup-windows", type=int, default=1)
    args = parser.parse_args()

    path = pathlib.Path(args.log)
    if not path.is_absolute():
        path = pathlib.Path.cwd() / path
    if not path.exists():
        print(f"[recompute] 不存在：{path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    clock = RE_CLOCK.search(text)
    if not clock:
        print("[recompute] 未找到 S5_P1_CLOCK（无法确定计数频率）")
        return 2
    rate = int(clock.group(1))

    segs = segment(text)
    results = []
    for seg in segs:
        info = analyze(seg["text"], rate, args.warmup_windows)
        info["rev"] = seg["rev"]
        results.append(info)
    useful = [r for r in results if r.get("useful")]
    if not useful:
        print("[recompute] 无可复算的 S5_FPS4 行")
        return 2
    authoritative = useful[-1]
    summary = {
        "log": str(path),
        "counts_per_second": rate,
        "segments_total": len(results),
        "segments": [{k: v for k, v in r.items() if k != "rows_detail"} for r in results],
        "authoritative_rev": authoritative["rev"],
        "aggregate": authoritative["aggregate"],
        "consistency": authoritative["consistency"],
        "vtc_bit_rates_per_s": authoritative.get("vtc_bit_rates_per_s"),
        "latency": authoritative["latency"],
        "rows": authoritative["rows_detail"],
        "notes": [
            "日志按 S5_P1_BEGIN rev= 分段；权威结果=最后一段（最新下载的 ELF）。",
            "video_refresh 语义：VTC 每帧 2 次事件（位 12/13/16 同置）⇒ 帧率=事件率/2。",
            "display_fps：MM2S FrmCntIrq（CR[23:16]=1）每帧一次。",
            "首窗口为预热（含启动前遗留事件），聚合时剔除。",
            "延迟仅 commit→首个帧完成事件，不是光子到屏幕。",
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        out = pathlib.Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok = authoritative["consistency"]["all_rows_match_logged"]
    agg = authoritative["aggregate"]
    print(f"[recompute] authoritative_rev={authoritative['rev']} rows={authoritative['rows']} match={ok} "
          f"display_fps={agg['display_fps']} video_refresh_frames_per_s={agg['video_refresh_frames_per_s']} "
          f"video_refresh_events_per_s={agg['video_refresh_events_per_s']}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())