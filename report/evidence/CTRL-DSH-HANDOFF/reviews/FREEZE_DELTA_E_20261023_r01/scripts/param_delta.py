#!/usr/bin/env python3
"""独立抽验：F5(61caac0d) → F6d(2f16d668) 的 24 项参数是否零差异（除批准类字段）。

并对 3 项做逐字节（规范 JSON 序列化）抽验。
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
BEH = "docs/stage6/s6a_stage6_g0_behavior_v1.json"
APPROVAL_FIELDS = {"approval_status", "approval_ref", "semantics_status", "value_status", "decision",
                   "approved_caliber", "map_status", "status"}


def load(rev: str) -> dict:
    raw = subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{BEH}"],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(raw)


f5, f6 = load("61caac0d"), load("2f16d668")
p5 = {p["id"]: p for p in f5["parameters"]}
p6 = {p["id"]: p for p in f6["parameters"]}
lines: list[str] = []
lines.append(f"ids_equal={sorted(p5) == sorted(p6)} n5={len(p5)} n6={len(p6)}")

value_diffs = []
field_changes = []
for pid in sorted(set(p5) | set(p6)):
    a, b = p5.get(pid), p6.get(pid)
    if a is None or b is None:
        value_diffs.append({"id": pid, "reason": "missing"})
        continue
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            if key in APPROVAL_FIELDS:
                field_changes.append({"id": pid, "field": key, "f5": a.get(key), "f6d": b.get(key)})
            else:
                value_diffs.append({"id": pid, "field": key, "f5": a.get(key), "f6d": b.get(key)})
lines.append(f"value_diffs={json.dumps(value_diffs, ensure_ascii=False)}")
lines.append(f"n_approval_field_changes={len(field_changes)}")
lines.append("approval_field_changes=" + json.dumps(field_changes, ensure_ascii=False))

# 3 项抽验：逐字节（对参数对象做规范序列化后比对）
lines.append("")
lines.append("### 3 项抽验（F5 vs F6d，值载荷逐字节）")
for pid in ("T6-K01", "T6-C01", "T6-S02"):
    a = {k: v for k, v in p5[pid].items() if k not in APPROVAL_FIELDS}
    b = {k: v for k, v in p6[pid].items() if k not in APPROVAL_FIELDS}
    ja = json.dumps(a, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    jb = json.dumps(b, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    lines.append(f"{pid}: byte_identical={ja == jb} sha_f5={hashlib.sha256(ja).hexdigest()[:16]} "
                 f"sha_f6d={hashlib.sha256(jb).hexdigest()[:16]} payload={b}")
lines.append("")
lines.append("### 24 项值载荷整体哈希（除批准类字段）")
ja = json.dumps([{k: v for k, v in p5[i].items() if k not in APPROVAL_FIELDS} for i in sorted(p5)],
                ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
jb = json.dumps([{k: v for k, v in p6[i].items() if k not in APPROVAL_FIELDS} for i in sorted(p6)],
                ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
lines.append(f"f5_sha256={hashlib.sha256(ja).hexdigest()}")
lines.append(f"f6d_sha256={hashlib.sha256(jb).hexdigest()}")
lines.append(f"identical={ja == jb}")

# 顶层非参数块差异（除声明允许的字段）
allowed_top = {"run_id", "supersedes_run_id", "status_label", "status_note", "upstream", "not_claimed",
               "revision", "behavior_rows", "parameter_notes", "reachability", "parameters",
               "approval_record", "actions", "open_decisions"}
top_changes = []
for key in sorted(set(f5) | set(f6)):
    if f5.get(key) != f6.get(key):
        top_changes.append(key)
lines.append("")
lines.append("top_level_changed_keys=" + json.dumps(top_changes, ensure_ascii=False))
lines.append("top_level_changed_not_in_allowed_set=" +
             json.dumps([k for k in top_changes if k not in allowed_top], ensure_ascii=False))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"value_diffs={len(value_diffs)} approval_field_changes={len(field_changes)} "
      f"top_changed={top_changes}")