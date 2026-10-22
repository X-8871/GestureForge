# -*- coding: utf-8 -*-
"""独立评审：自写全量双向谓词一致性 + 文本级绑定审计（不使用被审自检代码）。

结论写入 my_bidir.txt。
"""
import json, os, io, re

ROOT = r"D:\codex-worktrees\w6"
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(ROOT, "docs", "stage6", "s6a_stage6_g0_behavior_v1.json")
DOC = os.path.join(ROOT, "docs", "stage6", "S6A_stage6_g0_behavior_spec_v1.md")

d = json.load(open(J, encoding="utf-8"))
doc = open(DOC, encoding="utf-8").read()
w = io.StringIO()
def P(*a): w.write(" ".join(str(x) for x in a) + "\n")

PREDS = ("TARGET_CONTINUES", "WINDOW_MATCH")
items = {}
for t in d["transitions"]:
    items[t["id"]] = ("transition", t)
for b in d["behavior_rows"]:
    items[b["id"]] = ("row", b)

# ---- 1) 自写全量双向比较 ----
P("### 1. 自写全量双向比较（predicates.used_by  <->  每条目 predicates_used）")
forward = {}
for name in PREDS:
    ids, others = set(), []
    for e in d["predicates"][name]["used_by"]:
        m = re.match(r"^\s*(M\d+|B\d{2})\b", str(e))
        (ids.add(m.group(1)) if m else others.append(str(e)))
    forward[name] = ids
    P(f"  used_by[{name}] 条目ID({len(ids)}) = {sorted(ids)}")
    P(f"  used_by[{name}] 非条目引用 = {others}")

reverse = {n: set() for n in PREDS}
declared_map = {}
for iid, (kind, it) in items.items():
    if "predicates_used" in it:
        declared_map[iid] = it["predicates_used"]
        for n in it["predicates_used"]:
            reverse.setdefault(n, set()).add(iid)

for name in PREDS:
    of = sorted(forward[name] - reverse[name])
    orr = sorted(reverse[name] - forward[name])
    P(f"  {name}: only_forward={of} only_reverse={orr} -> {'双向一致' if not of and not orr else '不一致!'}")

P("")
P("  逐条目 predicates_used 现值：")
for iid in sorted(declared_map, key=lambda x: (x[0], int(x[1:]))):
    P(f"    {iid}: {declared_map[iid]}")

# 反向：哪些条目「没有」predicates_used 字段
no_field = sorted([i for i in items if "predicates_used" not in items[i][1]],
                  key=lambda x: (x[0], int(x[1:])))
P(f"  没有 predicates_used 字段的条目({len(no_field)}) = {no_field}")

# 空列表 / 未定义谓词 / 幽灵条目
P("")
P("### 2. 结构异常扫描")
for iid, (kind, it) in items.items():
    if "predicates_used" in it:
        v = it["predicates_used"]
        if v == []:
            P(f"  [异常] {iid}.predicates_used 为空列表（策略要求不用谓词的条目不得出现该字段）")
        for n in v:
            if n not in PREDS:
                P(f"  [异常] {iid}.predicates_used 含未定义谓词 {n!r}")
for name in PREDS:
    for i in forward[name]:
        if i not in items:
            P(f"  [异常] used_by[{name}] 引用了不存在的条目 {i}")

# ---- 3) 文本级绑定审计（比被审自检更严：覆盖全部声明绑定的条目）----
P("")
P("### 3. 文本级绑定审计（我自己加的：声明绑定必须在该条目的文本里出现）")
for iid in sorted(declared_map, key=lambda x: (x[0], int(x[1:]))):
    kind, it = items[iid]
    text = str(it.get("condition", "")) + " " + str(it.get("output", "")) + " " + str(it.get("must_log", ""))
    for n in declared_map[iid]:
        if n not in text:
            P(f"  [文本未绑定] {iid} 声明使用 {n}，但其 condition/output/must_log 全文未出现 {n}")
            P(f"      condition={it.get('condition')}")
            P(f"      output={it.get('output')}")
P("  （以上为文本级缺口；被审自检的 required_binding 只覆盖其中一部分条目）")

# ---- 4) 投射到文档：谓词在文档全文中是否出现 ----
P("")
P("### 4. 文档层面")
for n in PREDS:
    P(f"  文档出现 {n} 次数 = {doc.count(n) if False else doc.count(n)}")
raw = doc
for tok in ("matched_frames", "t_last_match", "t_submit+", "t_last_target_continues"):
    idxs = []
    s = 0
    while True:
        i = raw.find(tok, s)
        if i < 0: break
        idxs.append(i); s = i + len(tok)
    P(f"  文档 '{tok}' 出现 {len(idxs)} 次")
    for i in idxs:
        ctx = raw[max(0, i - 60): i + len(tok) + 60].replace("\n", " ")
        near = any(mk in ctx for mk in ("已废弃", "废弃"))
        P(f"     @{i} 邻近“废弃”={near} :: ...{ctx}...")

P("")
for tok in ("matched_frames", "t_last_match", "t_submit+"):
    P(f"  JSON '{tok}' 出现 {d and json.dumps(d, ensure_ascii=False).count(tok)} 次")

# ---- 5) M5/B13 现状 ----
P("")
P("### 5. M5 / B13 字段现状 vs 叙述")
for iid in ("M5", "B13"):
    kind, it = items[iid]
    P(f"  {iid}: 有 predicates_used 字段 = {'predicates_used' in it}；键={sorted(it.keys())}")
P(f"  predicate_binding_policy.statement = {d['predicate_binding_policy']['statement']!r}")
P(f"  statement 出现在文档 = {d['predicate_binding_policy']['statement'] in doc}")

# ---- 6) STABLE 退出路径与 M5 条件 ----
P("")
P("### 6. STABLE 锁存 / 退出路径（自算）")
computed = sorted([i for i, (k, it) in items.items() if it.get("from") in ("STABLE", "*")],
                  key=lambda x: int(x[1:]))
P(f"  迁移表中 from ∈ {{STABLE,*}} 的迁移 = {computed}")
P(f"  stable_latching.exit_paths 声明 = {d['stable_latching']['exit_paths']}")
demote = [i for i, (k, it) in items.items() if it.get("from") == "STABLE" and it.get("to") == "CANDIDATE"]
P(f"  STABLE→CANDIDATE 迁移 = {demote}")
P(f"  M5 condition = {items['M5'][1]['condition']}")

open(os.path.join(HERE, "my_bidir.txt"), "w", encoding="utf-8").write(w.getvalue())
print("wrote my_bidir.txt", len(w.getvalue()))