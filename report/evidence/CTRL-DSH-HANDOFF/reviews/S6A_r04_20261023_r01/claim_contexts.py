# -*- coding: utf-8 -*-
"""独立评审：抽出所有“可能构成完成声明”的关键词上下文，逐个判定是否虚假声明。"""
import json, os, io, re

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
R04 = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04")

FILES = {
    "spec": os.path.join(WT, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
    "json": os.path.join(WT, "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
    "STATE": os.path.join(WT, ".codex/STATE.md"),
    "run_summary": os.path.join(R04, "S6A_run_summary.md"),
    "coverage": os.path.join(R04, "coverage_matrix.json"),
    "limitations": os.path.join(R04, "limitations_not_executed.json"),
    "fix_record": os.path.join(R04, "fix_record.json"),
    "fix_record_md": os.path.join(R04, "fix_record.md"),
}
TOKENS = ["DONE", "已通过", "审查通过", "验收通过", "G0 通过", "已冻结", "APPROVED"]

out = []
def P(*a):
    line = " ".join(str(x) for x in a); print(line); out.append(line)

for label, path in FILES.items():
    txt = open(path, encoding="utf-8").read()
    P("=" * 90)
    P(f"### {label}")
    for tok in TOKENS:
        s = 0
        while True:
            i = txt.find(tok, s)
            if i < 0: break
            ctx = txt[max(0, i - 70): i + len(tok) + 70].replace("\n", "⏎")
            P(f"  [{tok}] …{ctx}…")
            s = i + len(tok)

P("")
P("=" * 90)
P("### coverage_matrix.review_fix_coverage / not_claimed 全文")
cov = json.load(open(os.path.join(R04, "coverage_matrix.json"), encoding="utf-8"))
P(json.dumps(cov.get("review_fix_coverage"), ensure_ascii=False, indent=1)[:4000])
P(json.dumps(cov.get("not_claimed"), ensure_ascii=False, indent=1))

P("")
P("### coverage_matrix.selfcheck_mapping / status_note")
P(json.dumps(cov.get("status_note"), ensure_ascii=False))
P(json.dumps(cov.get("selfcheck_mapping"), ensure_ascii=False, indent=1)[:2500])

P("")
P("### fix_record.json 全文关键字段")
fx = json.load(open(os.path.join(R04, "fix_record.json"), encoding="utf-8"))
P("keys = " + str(list(fx.keys())))
P(json.dumps({k: v for k, v in fx.items() if k not in ("items", "fixes")}, ensure_ascii=False, indent=1)[:2000])

with open(os.path.join(HERE, "claim_contexts.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")