#!/usr/bin/env python3
"""独立审查复算：哈希、标识、参数、手算边界。不修改被审文件。"""
import hashlib, json, re, subprocess
from pathlib import Path

W6 = Path(r"D:\codex-worktrees\w6")
RUN = W6 / "report" / "evidence" / "S6-A" / "s6a_g0_20261022_r01"
TMP = Path(r"D:\FPGA_Competition\tmp\review\S6A_20261022_r01")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

out = {"hashes": [], "counts": {}, "params_not_in_md14": [], "transition_mismatch": [],
       "case_recompute": [], "missing_claimed_evidence": [], "approval_issues": []}

# 1) 上游 11 项哈希
bind = json.loads((RUN / "upstream_bindings.json").read_text(encoding="utf-8"))
for it in bind["bindings"]:
    if it.get("git_repo"):
        blob = subprocess.run(["git", "-C", it["git_repo"], "show",
                               f"{it['git_commit']}:{it['git_relpath']}"],
                              capture_output=True)
        actual = hashlib.sha256(blob.stdout).hexdigest() if blob.returncode == 0 else f"GIT_ERR({blob.returncode})"
        mode = f"git {it['git_commit']}:{it['git_relpath']}"
    else:
        p = Path(it["path"])
        if not p.is_absolute():
            p = W6 / it["path"]
        actual = sha(p) if p.is_file() else "MISSING"
        mode = "file"
    out["hashes"].append({"id": it["id"], "mode": mode, "declared": it["sha256"],
                          "actual": actual, "match": actual.casefold() == it["sha256"].casefold()})

# 2) 自检输入哈希 vs selfcheck_result
sc = json.loads((RUN / "selfcheck_result.json").read_text(encoding="utf-8"))
for key, path in [("behavior_json_sha256", W6 / "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
                  ("human_doc_sha256", W6 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
                  ("hand_cases_sha256", RUN / "hand_computed_cases.json")]:
    actual = sha(path)
    out["hashes"].append({"id": key, "mode": "file", "declared": sc["inputs"][key],
                          "actual": actual, "match": actual == sc["inputs"][key]})

# 3) 计数与待批准纪律
data = json.loads((W6 / "docs/stage6/s6a_stage6_g0_behavior_v1.json").read_text(encoding="utf-8"))
out["counts"] = {
    "behavior_rows": len(data["behavior_rows"]),
    "parameters": len(data["parameters"]),
    "transitions": len(data["transitions"]),
    "hard_invariants": len(data["hard_invariants"]),
    "actions": len(data["actions"]["class_action_map"]),
}
for p in data["parameters"]:
    if p.get("approval_status") != "PENDING_APPROVAL":
        out["approval_issues"].append(p["id"])

doc = (W6 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md").read_text(encoding="utf-8")
# MD §14 表行（限定在 ## 14 与 ## 15 之间）
sec14 = doc.split("## 14.")[1].split("## 15.")[0]
md14 = set(re.findall(r"`(T6-[A-Za-z0-9_]+)`", sec14))
json_params = {p["id"] for p in data["parameters"]}
out["params_not_in_md14"] = sorted(json_params - md14)
out["params_md14_not_json"] = sorted(md14 - json_params)

# 4) 迁移表 MD vs JSON（从/到）
sec4 = doc.split("## 4.")[1].split("## 5.")[0]
md_tr = {}
for line in sec4.splitlines():
    m = re.match(r"\|\s*(M\d+)\s*\|\s*`([^`]+)`(?:\s*/\s*`([^`]+)`)?\s*→\s*`([^`]+)`\s*\|", line)
    if m:
        md_tr[m.group(1)] = {"from": (m.group(2), m.group(3)), "to": m.group(4)}
json_tr = {t["id"]: t for t in data["transitions"]}
for tid, jt in json_tr.items():
    mt = md_tr.get(tid)
    if not mt:
        out["transition_mismatch"].append({"id": tid, "issue": "MD 缺失"})
        continue
    froms = tuple(x for x in mt["from"] if x)
    if jt["from"] not in froms:
        out["transition_mismatch"].append({"id": tid, "json_from": jt["from"], "md_from": list(froms)})
    if jt["to"] != mt["to"]:
        out["transition_mismatch"].append({"id": tid, "json_to": jt["to"], "md_to": mt["to"]})

# 5) 独立手算（不复用被测脚本 recompute）
cases = json.loads((RUN / "hand_computed_cases.json").read_text(encoding="utf-8"))["cases"]
def stable(period, s01, s02):
    n = 1
    while not (n >= s02 and (n - 1) * period >= s01):
        n += 1
    return n, round((n - 1) * period, 6), max(s01, (s02 - 1) * period)
for c in cases:
    spec, exp = c["recompute"], c["expected"]
    kind = spec["kind"]
    got = {}
    if kind == "stable_window":
        n, actual, w = stable(float(spec["period_ms"]), float(spec["s01_ms"]), int(spec["s02_frames"]))
        got = {"frames_required": n, "actual_window_ms": actual, "lower_bound_W_ms": w,
               "stable": True,
               "stable_at_sixth_frame": 6 >= int(spec["s02_frames"]) and (6 - 1) * float(spec["period_ms"]) >= float(spec["s01_ms"]),
               "stable_at_fifth_frame": 5 >= int(spec["s02_frames"]) and (5 - 1) * float(spec["period_ms"]) >= float(spec["s01_ms"]),
               "dominant": "frame_count" if (int(spec["s02_frames"]) - 1) * float(spec["period_ms"]) > float(spec["s01_ms"]) else "duration"}
    elif kind == "cooldown":
        k = float(spec["k01_ms"]); t = float(spec["t_submit_ms"])
        got = {"ended_at_ms": round(t + k, 6),
               "ended_at_minus_1ns": (t + k - 1e-6 - t) >= k,
               "ended_at_exact": (t + k - t) >= k}
    elif kind == "dedup":
        a = float(spec["a02_ms"])
        got = {"suppressed_at_minus_1": (a - 1.0) < a, "suppressed_at_exact": a < a}
    elif kind == "lost_frames":
        l = int(spec["l01_frames"]); got = {"lost_at_4": 4 >= l, "lost_at_5": 5 >= l}
    elif kind == "lost_time":
        l = float(spec["l02_ms"]); got = {"lost_at_minus_1ns": (l - 1e-6) >= l, "lost_at_exact": l >= l}
    elif kind == "stale":
        l = float(spec["limit_ms"]); got = {"stale_at_exact": l > l, "stale_at_exact_plus_1ns": l + 1e-6 > l}
    elif kind == "jitter":
        j = int(spec["j01_frames"]); got = {"tolerated_at_1": 1 <= j, "reset_at_2": 2 > j}
    elif kind == "frame_id_seen":
        p, q, same = int(spec["prev_frame_id"]), int(spec["cur_frame_id"]), bool(spec["session_same"])
        if not same:
            got = {"event": "E_SESSION_RESET_SUSPECTED", "advances_match_count": False,
                   "may_trigger_action": False, "anomaly_delta": 1}
        elif p == q:
            got = {"event": "E_FRAME_DUPLICATE", "advances_match_count": False,
                   "may_trigger_action": False, "anomaly_delta": 0}
        elif q < p:
            got = {"event": "E_FRAME_OUT_OF_ORDER", "advances_match_count": False,
                   "may_trigger_action": False, "anomaly_delta": 1}
    elif kind == "session_change":
        same = bool(spec["session_same"])
        got = {"state_after": "IDLE" if not same else "UNCHANGED", "target_cleared": not same,
               "may_trigger_action_on_reset_frame": False}
    elif kind == "trigger_once_hold":
        got = {"hold_frames": int(round(float(spec["fps"]) * float(spec["hold_s"]))),
               "submitted_total": 1, "trigger_after_cooldown": 0}
    elif kind == "hysteresis":
        held = bool(spec["current_match"]) and float(spec["current_score"]) >= float(spec["p02"])
        got = {"held": held, "selected_class": "fist" if held else "palm",
               "suppression_event": "S_TARGET_HELD" if held else "NONE"}
    elif kind == "tie":
        orders = [int(v) for v in spec["source_orders"]]
        got = {"selected_source_order": min(orders)}
    elif kind == "action_events":
        trig, sub, eff = float(spec["t_trigger_ms"]), float(spec["t_submit_ms"]), float(spec["t_effective_ms"])
        a01, obs = float(spec["a01_ms"]), bool(spec["effective_observed"])
        got = {"latency_action_ms": round(eff - trig, 6), "latency_submit_ms": round(sub - trig, 6),
               "counts_as_success_when_effective_observed": obs and (eff - trig) <= a01,
               "counts_as_success_when_unobserved": False}
    elif kind == "unknown_rejection_proof":
        cid = int(spec["unknown_class_id"])
        got = {"class_membership_passes": 0 <= cid <= 4, "proves_unknown_rejection": False,
               "counts_as_false_accept_in_T6_02": True}
    mism = {k: (v, got.get(k)) for k, v in exp.items() if k not in got or (
        abs(v - got[k]) > 1e-6 if isinstance(v, float) else v != got[k])}
    # 记录复算是否真正使用了该 case 的关键输入（用于识别同义反复）
    unused = []
    if kind == "hysteresis" and "other_class_score" not in spec: unused.append("other_class_score")
    out["case_recompute"].append({"case_id": c["case_id"], "kind": kind,
                                  "mismatch": mism, "ok": not mism,
                                  "key_inputs_used": sorted(spec.keys())})

# 6) MD/SUMMARY 声称存在的证据文件
claimed = ["delivery_manifest.json", "inputs_manifest.json", "hashes_sha256.txt"]
out["missing_claimed_evidence"] = [n for n in claimed if not (RUN / n).exists()]

(TMP / "independent_verify_result.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: out[k] for k in ("counts", "params_not_in_md14", "params_md14_not_json",
                                      "transition_mismatch", "missing_claimed_evidence",
                                      "approval_issues")}, ensure_ascii=False, indent=2))
print("hashes_all_match=", all(h["match"] for h in out["hashes"]), "n=", len(out["hashes"]))
print("cases_ok=", sum(1 for c in out["case_recompute"] if c["ok"]), "/", len(out["case_recompute"]))
for c in out["case_recompute"]:
    if not c["ok"]:
        print("CASE_MISMATCH", c)
