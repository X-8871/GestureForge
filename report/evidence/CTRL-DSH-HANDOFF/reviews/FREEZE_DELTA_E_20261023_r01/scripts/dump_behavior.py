#!/usr/bin/env python3
"""导出 F6d 行为表 JSON 的状态/批准类字段，并检查 24 项参数批准状态与语义。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
beh = json.loads((ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))

lines: list[str] = []
for key in ("artifact_version", "run_id", "supersedes_run_id", "status", "status_label", "status_note",
            "revision", "human_doc"):
    lines.append(f"{key} = {json.dumps(beh.get(key), ensure_ascii=False)}")
lines.append("")
lines.append("### approval_record")
lines.append(json.dumps(beh.get("approval_record"), ensure_ascii=False, indent=1))
lines.append("")
params = beh["parameters"]
lines.append(f"### parameters: n={len(params)}")
bad = []
for item in params:
    st = item.get("approval_status")
    ref = item.get("approval_ref")
    if st != "APPROVED_20261023" or not ref:
        bad.append({"id": item.get("id"), "approval_status": st, "approval_ref": ref})
lines.append(f"params_not_approved_or_missing_ref = {json.dumps(bad, ensure_ascii=False)}")
lines.append("")
lines.append("### actions.map_status = " + json.dumps(beh.get("actions", {}).get("map_status"), ensure_ascii=False))
rows = beh["behavior_rows"]
sem = {r.get("semantics_status") for r in rows.values()} if isinstance(rows, dict) else {r.get("semantics_status") for r in rows}
lines.append("### behavior_rows semantics_status values = " + json.dumps(sorted(str(x) for x in sem), ensure_ascii=False))
lines.append("### behavior_rows B16 = " + json.dumps(rows["B16"] if isinstance(rows, dict) else None, ensure_ascii=False)[:800])
lines.append("### reachability = " + json.dumps(beh.get("reachability"), ensure_ascii=False)[:1200])
lines.append("### parameter_notes keys = " + json.dumps(sorted((beh.get("parameter_notes") or {}).keys()), ensure_ascii=False))
lines.append("### parameter_notes.T6-S04 = " + json.dumps((beh.get("parameter_notes") or {}).get("T6-S04"), ensure_ascii=False))
lines.append("### parameter_notes.T6-A03 = " + json.dumps((beh.get("parameter_notes") or {}).get("T6-A03"), ensure_ascii=False))
# 参数值快照（用于与上一冻结逐字节比对）
lines.append("")
lines.append("### param value payload (id, draft_value, comparison, unit, kind)")
for item in params:
    lines.append(json.dumps([item.get("id"), item.get("draft_value"), item.get("comparison"),
                             item.get("unit"), item.get("kind")], ensure_ascii=False))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"n_params={len(params)} bad={len(bad)}")