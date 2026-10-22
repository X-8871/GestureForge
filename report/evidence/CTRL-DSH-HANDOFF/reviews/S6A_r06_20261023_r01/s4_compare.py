#!/usr/bin/env python3
# 只读检查脚本 4：比对复跑自检结果 vs 入库 selfcheck_result.json；比对我自算哈希
import json, hashlib, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
B = ISO + r"\blobs"
EV = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


mine = json.load(open(ISO + r"\runs\my_selfcheck_r06.json", encoding="utf-8"))
lib = json.load(open(EV + r"\selfcheck_result.json", encoding="utf-8"))

print("=== 自检结果比对（我复跑 vs 入库）===")
print("status:", mine["status"], "|", lib["status"], "| equal:", mine["status"] == lib["status"])
print("errors:", mine["errors"], "|", lib["errors"])
d = 0
for a, b in zip(mine["checks"], lib["checks"]):
    if (a["id"], a["name"], a["status"], a["detail"]) != (b["id"], b["name"], b["status"], b["detail"]):
        d += 1
        print("DIFF:", a["id"])
        print("  mine:", json.dumps(a, ensure_ascii=False))
        print("  lib :", json.dumps(b, ensure_ascii=False))
print("check 条目:", len(mine["checks"]), "vs", len(lib["checks"]), "| 逐字差异数:", d)
print("id_inventory equal:", mine["id_inventory"] == lib["id_inventory"])
if mine["id_inventory"] != lib["id_inventory"]:
    print(" mine:", json.dumps(mine["id_inventory"], ensure_ascii=False)[:600])
    print(" lib :", json.dumps(lib["id_inventory"], ensure_ascii=False)[:600])
print("limitations equal:", mine["limitations"] == lib["limitations"])
print("scope equal:", mine["scope_statement"] == lib["scope_statement"])
print()
print("=== inputs 逐字段 ===")
for k in mine["inputs"]:
    a, b = mine["inputs"][k], lib["inputs"][k]
    print(("OK  " if a == b else "DIFF"), k, "|", a)
print()

print("=== 我自算哈希（入库 r06 证据，blob/LF 字节）===")
declared = {}
m = json.load(open(EV + r"\delivery_manifest.json", encoding="utf-8"))
for item in m["files"]:
    declared[item["path"].replace("\\", "/")] = item["sha256"]
hs = {}
for line in open(EV + r"\hashes_sha256.txt", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split()
    if len(parts) >= 2:
        hs[parts[-1].lstrip("*")] = parts[0]
print("hashes_sha256.txt 解析条数:", len(hs), "| manifest files:", len(declared))

bad = []
for rel, want in sorted(hs.items()):
    got = sha(os.path.join(EV, rel))
    if got != want:
        bad.append((rel, want, got))
print("hashes_sha256.txt：不符条数 =", len(bad))
for r in bad:
    print("  MISMATCH", r)

code_srcs = ["docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
             "docs/stage6/s6a_stage6_g0_behavior_v1.json",
             "verification/s6_g0_selfcheck.py",
             "verification/s6a_build_evidence.py",
             "verification/s6a_r06_probe.py",
             ".codex/STATE.md"]
print()
print("=== 被审源码/规格 worktree(CRLF) 与 blob(LF) 哈希 ===")
for rel in code_srcs:
    wt = os.path.join(r"D:\codex-worktrees\w6", rel.replace("/", "\\"))
    blob = B + r"\r06_" + rel.replace("/", "_")
    print(f"{rel}\n  worktree={sha(wt)}\n  blob    ={sha(blob)}\n  equal={sha(wt)==sha(blob)}")
print()
print("=== selfcheck_result.json.inputs 三项哈希 vs 我自算 worktree ===")
for key, rel in (("behavior_json_sha256", code_srcs[1]), ("human_doc_sha256", code_srcs[0]),
                 ("hand_cases_sha256", None)):
    p = os.path.join(r"D:\codex-worktrees\w6", rel.replace("/", "\\")) if rel else os.path.join(EV, "hand_computed_cases.json")
    print(key, lib["inputs"][key], "| mine(worktree)", sha(p), "| equal", lib["inputs"][key] == sha(p))