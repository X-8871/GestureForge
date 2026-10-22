# -*- coding: utf-8 -*-
"""独立评审：上游哈希自算、hashes_sha256.txt 交叉核对、HC-27/28/29 内容审查。"""
import json, os, io, hashlib, re

HERE = os.path.dirname(os.path.abspath(__file__))
WT = r"D:\codex-worktrees\w6"
R04 = os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r04")
ROOT = r"D:\FPGA_Competition"

out = []
def P(*a):
    line = " ".join(str(x) for x in a); print(line); out.append(line)

def sha(p):
    with open(p, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

P("### 1. 自算：文档 §17 上游哈希表 vs 实际文件")
DOC = os.path.join(WT, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
doc = open(DOC, encoding="utf-8").read()
# 解析 §17 表
sec = doc.split("**上游只读文件 SHA-256")[1]
rows = re.findall(r"\|\s*`([^`]+)`[^|]*\|\s*`([0-9a-f]{64})`\s*\|", sec)
for rel, claimed in rows:
    rel_clean = rel.replace("（w6 基线版本）", "").replace("（只读）", "").strip()
    cands = [os.path.join(WT, rel_clean), os.path.join(ROOT, rel_clean)]
    if rel_clean.startswith("w4/") or rel_clean.startswith("w5/"):
        cands = [os.path.join(r"D:\codex-worktrees", rel_clean), os.path.join(ROOT, rel_clean)]
    found = next((c for c in cands if os.path.isfile(c)), None)
    if not found:
        P(f"  MISSING {rel_clean}")
        continue
    mine = sha(found)
    P(f"  {'MATCH  ' if mine == claimed else 'MISMATCH'} {rel_clean}")
    if mine != claimed:
        P(f"      claimed={claimed} mine={mine} file={found}")

P("")
P("### 2. upstream_bindings.json 逐条自算核对（含 drift 声明）")
ub = json.load(open(os.path.join(R04, "upstream_bindings.json"), encoding="utf-8"))
P("keys = " + str(list(ub.keys())))
def rec(node, depth=0):
    if isinstance(node, dict):
        if "path" in node and "sha256" in node:
            rel = node["path"]
            cands = [os.path.join(WT, rel), os.path.join(ROOT, rel)]
            if rel.startswith(("w4/", "w5/")):
                cands = [os.path.join(r"D:\codex-worktrees", rel), os.path.join(ROOT, rel)]
            found = next((c for c in cands if os.path.isfile(c)), None)
            if found:
                mine = sha(found)
                ok = mine == node["sha256"]
                P(f"  {'MATCH  ' if ok else 'DIFF   '} {rel}  frozen={node.get('frozen_status')}")
                if not ok:
                    P(f"      recorded={node['sha256']} actual={mine}")
            else:
                P(f"  MISSING {rel}")
        for v in node.values(): rec(v, depth + 1)
    elif isinstance(node, list):
        for v in node: rec(v, depth + 1)
rec(ub)

P("")
P("### 3. hashes_sha256.txt 与我自算的 23 个证据文件交叉核对")
htxt = open(os.path.join(R04, "hashes_sha256.txt"), encoding="utf-8").read()
P("  --- hashes_sha256.txt 原文 ---")
for line in htxt.splitlines(): P("   " + line)
P("")
mismatch, missing, checked = [], [], 0
for line in htxt.splitlines():
    m = re.match(r"^([0-9a-f]{64})\s+\*?(.+?)\s*$", line)
    if not m: continue
    claimed, rel = m.group(1), m.group(2).strip().replace("\\", "/")
    checked += 1
    cands = [os.path.join(R04, os.path.basename(rel)), os.path.join(WT, rel), os.path.join(ROOT, rel)]
    found = next((c for c in cands if os.path.isfile(c)), None)
    if not found:
        missing.append(rel); continue
    if sha(found) != claimed:
        mismatch.append((rel, claimed, sha(found)))
P(f"  解析条目={checked} 缺失={missing} 不符={mismatch}")

P("")
P("### 4. HC-27 / HC-28 / HC-29 内容审查（N02：不得自比较）")
cases = json.load(open(os.path.join(R04, "hand_computed_cases.json"), encoding="utf-8"))
P(f"  版本={cases.get('hand_cases_version')} 样例数={len(cases['cases'])}")
P(f"  derivation_note={cases.get('derivation_note')}")
byid = {c["case_id"]: c for c in cases["cases"]}
suspicious = []
for c in cases["cases"]:
    d = json.dumps(c, ensure_ascii=False)
    # 自比较探测：同一参数名出现在不等号两侧
    for m in re.finditer(r"([A-Za-z0-9_]+)\s*(>=|<=|>|<)\s*([A-Za-z0-9_]+)", d):
        if m.group(1) == m.group(3):
            suspicious.append((c["case_id"], m.group(0)))
P(f"  自比较探测（形如 X>=X）：{suspicious}")
P("  recompute 字段类型分布：" + str({type(c.get('recompute')).__name__ for c in cases['cases']}))
P("  全部样例 ID = " + str(sorted(byid)))
for cid in ("HC-27", "HC-28", "HC-29"):
    c = byid.get(cid)
    if not c:
        P(f"  缺少 {cid}"); continue
    P("")
    P(f"  --- {cid} ---")
    P(json.dumps(c, ensure_ascii=False, indent=2)[:2200])

with open(os.path.join(HERE, "upstream_and_cases.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")