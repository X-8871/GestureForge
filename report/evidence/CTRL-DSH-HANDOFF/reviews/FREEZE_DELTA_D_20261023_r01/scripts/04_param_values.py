#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立抽验：F4 vs F5 行为表 24 项参数的数值/字段逐字节比较（不依赖 lead 自述）。

用法：python -B 04_param_values.py <repo> <out.json>
"""
import json
import subprocess
import sys
from pathlib import Path

F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"
F5 = "caa9728af84b0a5b79bed17427eec0091b922923"
J = "docs/stage6/s6a_stage6_g0_behavior_v1.json"


def show(repo: str, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{rev}:{path}"], cwd=repo,
                          capture_output=True, check=True).stdout


def main() -> int:
    repo = sys.argv[1]
    out = Path(sys.argv[2])
    raw4 = show(repo, F4, J)
    raw5 = show(repo, F5, J)
    d4 = json.loads(raw4.decode("utf-8"))
    d5 = json.loads(raw5.decode("utf-8"))
    p4 = {p["id"]: p for p in d4["parameters"]}
    p5 = {p["id"]: p for p in d5["parameters"]}
    report = {"schema": 1, "n_f4": len(p4), "n_f5": len(p5),
              "id_sets_equal": sorted(p4) == sorted(p5), "per_param": {}, "value_diffs": [],
              "field_added": [], "field_removed": [], "field_changed": []}
    for pid in sorted(p4):
        a, b = p4[pid], p5[pid]
        va, vb = a.get("draft_value"), b.get("draft_value")
        same = (type(va) is type(vb)) and va == vb
        entry = {"draft_value_f4": va, "draft_value_f5": vb, "value_identical": same,
                 "comparison_f4": a.get("comparison"), "comparison_f5": b.get("comparison"),
                 "unit_f4": a.get("unit"), "unit_f5": b.get("unit"),
                 "kind_f4": a.get("kind"), "kind_f5": b.get("kind"),
                 "keys_f4": sorted(a), "keys_f5": sorted(b)}
        report["per_param"][pid] = entry
        if not same:
            report["value_diffs"].append({"id": pid, "f4": va, "f5": vb})
        added = sorted(set(b) - set(a))
        removed = sorted(set(a) - set(b))
        changed = [k for k in sorted(set(a) & set(b)) if a[k] != b[k] and k not in
                   ("approval_status", "approval_ref", "approval_record", "approval_decision_note",
                    "value_status", "approved_caliber", "cross_stage_note", "approval_owner")]
        # draft_value 单独记录（避免重复）
        changed = [k for k in changed if k != "draft_value"]
        if added:
            report["field_added"].append({"id": pid, "keys": added})
        if removed:
            report["field_removed"].append({"id": pid, "keys": removed})
        if changed:
            report["field_changed"].append({"id": pid, "keys": changed,
                                            "f4": {k: a[k] for k in changed},
                                            "f5": {k: b[k] for k in changed}})
    # 顶层批准块
    report["approval_record_f5"] = d5.get("approval_record")
    report["approval_record_f4"] = d4.get("approval_record")
    report["top_status"] = [d4.get("status"), d5.get("status")]
    # 三个抽验参数（随机固定种子）
    import random
    rng = random.Random(20261023)
    sample = rng.sample(sorted(p4), 3)
    report["sampled_ids"] = sample
    report["sampled"] = {pid: report["per_param"][pid] for pid in sample}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"n_f4={report['n_f4']} n_f5={report['n_f5']} id_sets_equal={report['id_sets_equal']}")
    print(f"value_diffs={report['value_diffs']}")
    print(f"field_added_ids={[x['id'] for x in report['field_added']]}")
    print(f"field_removed_ids={[x['id'] for x in report['field_removed']]}")
    print(f"field_changed={report['field_changed']}")
    print(f"sampled_ids={sample}")
    for pid in sample:
        e = report["sampled"][pid]
        print(f"  {pid}: F4={e['draft_value_f4']!r} F5={e['draft_value_f5']!r} identical={e['value_identical']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())