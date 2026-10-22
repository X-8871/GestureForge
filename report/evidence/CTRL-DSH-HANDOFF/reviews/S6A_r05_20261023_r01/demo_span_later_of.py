#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""演示：C7 的 m3_fires 只取「第 T6-S02 个 WINDOW_MATCH 帧」跨度，
与 M3/§9/§14 T6-S03「取较晚满足者」及 §15 的 30 fps 示例（第 8 帧 233.1 ms）不一致。

构造：P=33.3 ms、S01=200 ms、S02=6，连续 8 个 WINDOW_MATCH 帧。
按 §9/§15 语义，窗口在第 8 帧（跨度 233.1 ms ≥ 200）完成 → m3_fires 应为 true；
按 C7 模型，第 6 个 WINDOW_MATCH 帧跨度 5×33.3=166.5 < 200 → 报 false。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w6")
OUT = Path("D:/FPGA_Competition/tmp/review/S6A_r05_20261023_r01")
RUN = ROOT / "report/evidence/S6-A/s6a_g0_20261022_r05"
cases = json.loads((RUN / "hand_computed_cases.json").read_text(encoding="utf-8"))
by = {c["case_id"]: c for c in cases["cases"]}
frames = [
    {"index": i, "same_class": True, "iou": 0.6, "center_disp": round(0.025 + (i - 1) * 0.005, 4),
     "score": 0.35}
    for i in range(1, 9)
]
replacement = {
    "case_id": "HC-29",
    "topic": "Y1：30 fps（P=33.3）下按 §9/§15 取较晚完成",
    "recompute": {
        "kind": "window_match_vs_continues",
        "p02": 0.3, "p03": 0.3, "p04": 0.15, "p05": 0.05,
        "s02_frames": 6, "s01_ms": 200, "period_ms": 33.3,
        "l01_frames": 5, "l02_ms": 300, "frames": frames,
    },
    "derivation": "§9/§15：第 6 个 WINDOW_MATCH 帧（第 6 帧）跨度 5×33.3=166.5 < 200；"
                  "第 8 帧跨度 7×33.3=233.1 ≥ 200 且计数已 ≥6 → 窗口在第 8 帧完成，m3_fires=true"
                  "（§15 表格「30 | 33.3 | 166.7 | 200 | 时长 | 第 8 帧 233.1 ms」）。",
    "expected": {"m3_fires": True, "window_span_ms": 233.1, "window_match_count": 8,
                 "lost": False, "span_conventions_agree": False},
}
path = OUT / "inject" / "Y1_hc29_33fps_cases.json"
for idx, case in enumerate(cases["cases"]):
    if case["case_id"] == "HC-29":
        cases["cases"][idx] = replacement
        break
else:
    raise SystemExit("未找到 HC-29")
path.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
result_path = OUT / "inject" / "Y1_result.json"
command = [
    sys.executable, "-B", str(ROOT / "verification/s6_g0_selfcheck.py"),
    "--json", str(ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
    "--doc", str(ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
    "--cases", str(path), "--upstream", str(RUN / "upstream_bindings.json"),
    "--out", str(result_path), "--project-root", str(ROOT), "--evidence-dir", str(RUN),
]
completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", check=False)
result = json.loads(result_path.read_text(encoding="utf-8"))
lines = [f"退出码 = {completed.returncode}  status={result['status']}"]
for c in result["checks"]:
    if c["status"] == "FAIL":
        lines.append(f"FAIL {c['id']}: {c['detail']}")
(OUT / "inject" / "Y1_demo.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))