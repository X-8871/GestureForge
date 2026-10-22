# -*- coding: utf-8 -*-
"""独立评审：声明文件存在性 / 声明纪律 / 覆盖矩阵 自算核对。"""
import json, os, io

WT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
R04 = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04")
DOC = os.path.join(WT, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
J = os.path.join(WT, "docs/stage6/s6a_stage6_g0_behavior_v1.json")

out = []
def P(*a):
    line = " ".join(str(x) for x in a); print(line); out.append(line)

doc = open(DOC, encoding="utf-8").read()
data = json.load(open(J, encoding="utf-8"))
man = json.load(open(os.path.join(R04, "delivery_manifest.json"), encoding="utf-8"))
inp = json.load(open(os.path.join(R04, "inputs_manifest.json"), encoding="utf-8"))
cov = json.load(open(os.path.join(R04, "coverage_matrix.json"), encoding="utf-8"))
lim = json.load(open(os.path.join(R04, "limitations_not_executed.json"), encoding="utf-8"))
fix = json.load(open(os.path.join(R04, "fix_record.json"), encoding="utf-8"))
summ = open(os.path.join(R04, "S6A_run_summary.md"), encoding="utf-8").read()
state = open(os.path.join(WT, ".codex/STATE.md"), encoding="utf-8").read()

P("### 1. delivery_manifest 声明文件存在性（自算）")
def walk_files(node, acc):
    if isinstance(node, dict):
        if "path" in node and isinstance(node["path"], str) and node.get("sha256"):
            acc.append(node)
        for v in node.values(): walk_files(v, acc)
    elif isinstance(node, list):
        for v in node: walk_files(v, acc)
rows = []
walk_files(man, rows)
P(f"  manifest 中带 path+sha256 的条目 = {len(rows)}")
missing, mism = [], []
import hashlib
for r in rows:
    p = os.path.join(WT, r["path"])
    if not os.path.isfile(p):
        p2 = os.path.join(os.path.dirname(WT), r["path"])
        if os.path.isfile(p2): p = p2
    if not os.path.isfile(p):
        missing.append(r["path"]); continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if h != r["sha256"]:
        mism.append((r["path"], r["sha256"], h))
P(f"  声明但缺失 = {missing}")
P(f"  哈希不符 = {mism}")

P("")
P("### 2. 文档 §18 声明的产物文件实际存在性")
import re
names = sorted(set(re.findall(r"`([A-Za-z0-9_./-]+\.(?:json|md|txt))`", doc)))
evfiles = [n for n in names if "/" in n or n.endswith((".json", ".txt"))]
for n in evfiles:
    p = os.path.join(R04, n) if not n.startswith("report") else os.path.join(WT, n)
    if os.path.isfile(p):
        P(f"  OK      {n}")
    else:
        P(f"  MISSING {n}")

P("")
P("### 3. 运行目录实际文件 vs 文档 §18 逐一列举")
actual = sorted(os.listdir(R04))
P(f"  实际文件数 = {len(actual)}")
doc_items = re.search(r"运行证据：(.*?)三类旧包失败证据", doc, re.S)
listed = set(re.findall(r"`([^`]+\.(?:json|md|txt))`", doc_items.group(1))) if doc_items else set()
# 文档用 `a.json`/`.txt` 成对写法，展开
P(f"  文档列举条目 = {sorted(listed)}")
missing_listed = [x for x in actual
                  if x not in doc_items.group(1) and x.replace("selfcheck_old_package_failure",
                      "selfcheck_old_package_failure") not in doc_items.group(1)]
P(f"  实际存在但 §18 未逐一点名的文件 = {missing_listed}")

P("")
P("### 4. 声明纪律扫描（是否自称已审查/已通过/G0 通过）")
bad = ["已审查通过", "审查通过", "已通过", "G0 通过", "G0_PASS", "APPROVED", "已冻结",
       "FROZEN", "已验收", "验收通过", "PASS", "DONE"]
targets = {"文档": doc, "JSON": json.dumps(data, ensure_ascii=False),
           "STATE": state, "run_summary": summ,
           "limitations": json.dumps(lim, ensure_ascii=False),
           "coverage": json.dumps(cov, ensure_ascii=False)}
for label, txt in targets.items():
    hits = []
    for b in bad:
        c = txt.count(b)
        if c:
            hits.append(f"{b}x{c}")
    P(f"  {label}: {hits}")

P("")
P("### 5. not_claimed / evidence_boundaries / limitations")
for s in data["not_claimed"]: P(f"  not_claimed: {s}")
for s in data["evidence_boundaries"]: P(f"  evidence_boundary: {s}")
P(f"  limitations keys = {list(lim.keys())}")
P(f"  limitations JSON 文本含 'NOT_RUN' = {'NOT_RUN' in json.dumps(lim, ensure_ascii=False)}")

P("")
P("### 6. coverage_matrix 自算核对")
P(f"  coverage keys = {list(cov.keys())}")
def find_counts(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, int) and any(t in k.lower() for t in ("count", "total", "num")):
                P(f"    {path}{k} = {v}")
            find_counts(v, path + k + ".")
    elif isinstance(o, list):
        for i, v in enumerate(o): find_counts(v, path + f"[{i}].")
find_counts(cov)
P(f"  文档/JSON 声明的 C7 样例数：JSON 未直接给；coverage 中 c7 相关="
  f"{json.dumps({k:v for k,v in cov.items() if 'c7' in k.lower()}, ensure_ascii=False)[:400]}")
cases = json.load(open(os.path.join(R04, "hand_computed_cases.json"), encoding="utf-8"))
P(f"  hand_computed_cases 实际样例数 = {len(cases.get('cases', cases)) if isinstance(cases, dict) else len(cases)}")
if isinstance(cases, dict):
    P(f"  cases 顶层键 = {list(cases.keys())}")

P("")
P("### 7. M5/B13 predicate_binding_note 与 global_cooldown_gate 实际内容")
for t in data["transitions"]:
    if t["id"] == "M5":
        P(f"  M5.predicate_binding_note = {t.get('predicate_binding_note')!r}")
        P(f"  M5.global_cooldown_gate = {t.get('global_cooldown_gate')!r}")
for b in data["behavior_rows"]:
    if b["id"] == "B13":
        P(f"  B13.predicate_binding_note = {b.get('predicate_binding_note')!r}")
        P(f"  B13.global_cooldown_gate = {b.get('global_cooldown_gate')!r}")
others = [t['id'] for t in data['transitions'] if 'predicate_binding_note' in t]
P(f"  带 predicate_binding_note 的迁移 = {others}")

P("")
P("### 8. STATE 与阶段6 事实核对")
for kw in ("S6-A", "s6a", "stage6", "6-B", "S6-B", "NOT_RUN", "stable", "锁存", "审查"):
    P(f"  STATE 含 {kw!r} = {kw in state}")
P("  --- STATE 中 stage6/S6 相关行 ---")
for i, line in enumerate(state.splitlines(), 1):
    if any(k in line for k in ("S6", "stage6", "阶段6", "6-A", "6-B")):
        P(f"    {i}: {line}")

with open(os.path.join(HERE, "claims_and_files.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")