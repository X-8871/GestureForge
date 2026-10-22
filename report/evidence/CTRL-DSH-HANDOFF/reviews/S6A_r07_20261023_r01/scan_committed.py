#!/usr/bin/env python3
"""用提交字节（非 git grep）准确扫描残留措辞。"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
W6 = r"D:\codex-worktrees\w6"
EV = "report/evidence/S6-A/s6a_g0_20261022_r07"
DOC = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
JSONP = "docs/stage6/s6a_stage6_g0_behavior_v1.json"


def blob(p):
    r = subprocess.run(["git", "-C", W6, "cat-file", "blob", "bdcf896:" + p], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def scan(label, path, needles):
    raw = blob(path)
    if raw is None:
        print(f"[{label}] 文件不存在: {path}")
        return
    text = raw.decode("utf-8")
    for n in needles:
        hits = [(i + 1, ln.strip()[:150]) for i, ln in enumerate(text.splitlines()) if n in ln]
        print(f"[{label}] {path} 含 {n!r}：{len(hits)} 行")
        for ln, body in hits[:12]:
            print(f"    L{ln}: {body}")


scan("doc", DOC, ["第 N 个", "29<30", "29 < 30", "v1.5", "行为表 v1.5"])
scan("json", JSONP, ["第 N 个", "M4 不可达", "不得计入覆盖"])
scan("manifest", f"{EV}/delivery_manifest.json", ["29<30", "8 个注入", "不可达", "不计入覆盖"])
scan("limitations", f"{EV}/limitations_not_executed.json", ["v1.5", "不可达", "不计入覆盖"])
scan("coverage", f"{EV}/coverage_matrix.json", ["v1.5", "不可达", "不计入覆盖"])
scan("runsum", f"{EV}/S6A_run_summary.md", ["不可达", "29"])
scan("cases", f"{EV}/hand_computed_cases.json", ["不可达", "第 N 个"])
scan("selfcheck", "verification/s6_g0_selfcheck.py", ["UNIFIED_COMPLETION_PHRASE", "required_completion_index"])
scan("state", ".codex/STATE.md", ["v1.4/r05 为", "不可达", "本轮已完成（S6-A v1.5"])
scan("fixrec", f"{EV}/fix_record.json", ["29<30", "29 < 32"])
scan("probe_summary", f"{EV}/probe_summary.json", ["29<30", "7/233.1", "HC-28"])

# C14 断言的 4 个锚点 + 文档 B07/B27/§9 行的实际文本
data = json.loads(blob(JSONP).decode("utf-8"))
PHRASE = "第一个同时满足帧数与时长（取较晚）的帧"
rows = {r["id"]: r for r in data["behavior_rows"]}
tr = {t["id"]: t for t in data["transitions"]}
anchors = {"behavior_rows.B07.condition": rows["B07"]["condition"],
           "behavior_rows.B27.output": rows["B27"]["output"],
           "time_anchors.window_complete": data["time_anchors"]["window_complete"],
           "transitions.M3.condition": tr["M3"]["condition"],
           "low_fps_latency.window_completion_definition": data["low_fps_latency"]["window_completion_definition"]}
print("--- F1 统一口径存在性（JSON）")
for k, v in anchors.items():
    print(f"    {k}: phrase={PHRASE in v} 第N个={'第 N 个' in v}")
print("--- 文档 §4 M4 行 / §14 T6-S04 行 / §12.1")
doc = blob(DOC).decode("utf-8")
for ln in doc.splitlines():
    if ln.startswith("| M4 |") or ln.startswith("| `T6-S04` |") or "T6-S04` | 新增 HC-23" in ln:
        print("   ", ln.strip()[:220])