#!/usr/bin/env python3
"""BLK-r07-1 八处 M4 表述核查 + 全包禁语扫描（用提交字节）。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/committed")
R08 = BASE / "f3c537d"
R07 = BASE / "bdcf896"

PLACES = [
    ("1 文档 §18", R08 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", None),
    ("2 行为表 JSON parameter_notes.T6-S04", R08 / "docs/stage6/s6a_stage6_g0_behavior_v1.json", None),
    ("3 清单 limitations", R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/delivery_manifest.json", None),
    ("4 手算样例 HC-23", R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/hand_computed_cases.json", None),
    ("5 limitations_not_executed.not_run", R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json", None),
    ("6 coverage_matrix", R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/coverage_matrix.json", None),
    ("7 S6A_run_summary.md", R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/S6A_run_summary.md", None),
    ("8 .codex/STATE.md", R08 / ".codex/STATE.md", None),
]


def text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def show_lines(p: Path, pattern: str, label: str, window: int = 0) -> None:
    print(f"\n----- {label} :: {p.relative_to(BASE)}")
    lines = text(p).splitlines()
    hits = [i for i, line in enumerate(lines) if re.search(pattern, line)]
    if not hits:
        print("   （无匹配）")
    for i in hits:
        lo, hi = max(0, i - window), min(len(lines), i + window + 1)
        for j in range(lo, hi):
            mark = ">>" if j == i else "  "
            print(f"   {mark} {j+1}: {lines[j][:400]}")


def main() -> int:
    print("=" * 100)
    print("BLK-r07-1 八处核查（提交 f3c537d 字节）")
    print("=" * 100)

    # 1 文档 §18
    show_lines(PLACES[0][1], r"M4|T6-S04", "文档：M4/T6-S04 行")
    # 2 parameter_notes
    d = json.loads(text(PLACES[1][1]))
    print("\n----- 行为表 JSON：parameter_notes 中涉及 M4/T6-S04/L02 的全部键")
    for k, v in d.get("parameter_notes", {}).items():
        if any(t in str(k) + str(v) for t in ("M4", "T6-S04", "T6-L02")):
            print(f"   {k} = {v}")
    print("\n----- reachability")
    print("   M4 =", json.dumps(d["reachability"]["transitions"]["M4"], ensure_ascii=False))
    print("   M7 =", json.dumps(d["reachability"]["transitions"]["M7"], ensure_ascii=False))
    print("   consequence =", json.dumps(d["reachability"].get("consequence"), ensure_ascii=False)[:900])
    for key in ("counted_in_coverage", "not_counted_in_coverage", "resolution"):
        if key in d["reachability"]:
            print(f"   reachability.{key} =", json.dumps(d["reachability"][key], ensure_ascii=False)[:600])
    print("\n----- open_decisions U6-12")
    u12 = [x for x in d["open_decisions"] if x["id"] == "U6-12"]
    print(json.dumps(u12, ensure_ascii=False, indent=2))
    # 3 清单 limitations
    m = json.loads(text(PLACES[2][1]))
    print("\n----- 清单 limitations")
    for i, item in enumerate(m.get("limitations", [])):
        print(f"   [{i}] {json.dumps(item, ensure_ascii=False)[:500]}")
    # 4 HC-23
    c = json.loads(text(PLACES[3][1]))
    hc = [x for x in c["cases"] if x["case_id"] == "HC-23"]
    print("\n----- HC-23（提交字节）")
    print(json.dumps(hc, ensure_ascii=False, indent=2)[:2000])
    # 5 limitations_not_executed
    l = json.loads(text(PLACES[4][1]))
    print("\n----- limitations_not_executed 顶层键：", list(l.keys()))
    for key in ("not_run", "not_implemented", "reachability_counted", "reachability_not_counted"):
        if key in l:
            print(f"   {key} = {json.dumps(l[key], ensure_ascii=False)[:900]}")
    # 6 coverage_matrix
    cm = json.loads(text(PLACES[5][1]))
    print("\n----- coverage_matrix 顶层键：", list(cm.keys()))
    print("   coverage_matrix 全文（截断 3000）:")
    print(text(PLACES[5][1])[:3000])
    # 7 summary
    show_lines(PLACES[6][1], r"M4|T6-S04|不可达|计入覆盖", "S6A_run_summary.md")
    # 8 STATE
    show_lines(PLACES[7][1], r"M4|T6-S04|不可达|计入覆盖", "STATE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())