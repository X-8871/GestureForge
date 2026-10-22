#!/usr/bin/env python3
# 只读检查脚本 10：N-r05-01/02/03 措辞与归因审计 + C11 STATE 声明目录在提交中的存在性
import json, os, re, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
B = ISO + r"\blobs"
EV6 = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"
COMMIT = "04ea58e1"

print("=== A. 关键词在所有 r06 提交文本中的出现 ===")
files = {}
for root in (EV6, B):
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith((".json", ".md", ".txt")):
                p = os.path.join(dp, f)
                files[os.path.relpath(p, B)] = open(p, encoding="utf-8", errors="replace").read()
for rel in ("r06_docs_stage6_S6A_stage6_g0_behavior_spec_v1.md", "r06_.codex_STATE.md",
            "r06_verification_s6a_build_evidence.py", "r06_verification_s6a_r06_probe.py",
            "r06_verification_s6_g0_selfcheck.py", "r06_docs_stage6_s6a_stage6_g0_behavior_v1.json"):
    files[rel] = open(os.path.join(B, rel), encoding="utf-8", errors="replace").read()

PAT = {
    "8 个注入": "N-r05-01 旧表述（应已改）",
    "基线 1 例 + 注入 7 例": "N-r05-01 新表述",
    "C7 捕获 N-r04-04": "N-r05-02 旧归因（应已改）",
    "29<30": "N-r05-02 新归因（阈值 30）",
    "29<31": "N-r05-02 归因（r06 阈值 31）",
    "不足 31": "r06 自检阈值",
    "span_conventions_agree": "r05 已移除的口径一致性键",
    "actions_within_supplied_sequence": "N-r05-03 新字段",
    "total_actions": "N-r05-03 旧字段",
    "m3_fires_count_only": "N-r05-04 旧口径对照字段",
}
for pat, note in PAT.items():
    hits = [(rel, t.count(pat)) for rel, t in files.items() if pat in t]
    print(f"\n[{pat}]  {note}")
    for rel, n in sorted(hits):
        for m in re.finditer(re.escape(pat), files[rel]):
            s = max(0, m.start() - 90)
            print(f"   {rel} x{n}: ...{files[rel][s:m.end()+90].strip()}...")
            break

print()
print("=== B. r04 重跑证据（r06 提交内）===")
rf = json.load(open(EV6 + r"\selfcheck_r04_failure.json", encoding="utf-8"))
print("status:", rf["status"], "| FAILED:", [c["id"] for c in rf["checks"] if c["status"] == "FAIL"])
for c in rf["checks"]:
    if c["status"] == "FAIL":
        print(f"  {c['id']}: {c['detail'][:300]}")
pu = json.load(open(EV6 + r"\r04_package_under_test.json", encoding="utf-8"))
print("r04_package_under_test:", json.dumps(pu, ensure_ascii=False)[:700])

print()
print("=== C. C11 的 STATE 声明目录 vs 提交内容 ===")
state = files["r06_.codex_STATE.md"]
decl_files, decl_dirs = set(), set()
for line in state.splitlines():
    if "证据入口" not in line and "report/evidence" not in line:
        continue
    for tok in re.findall(r"`([^`]+)`", line):
        if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*\.(json|md|txt|jsonl)", tok) and "/" not in tok:
            decl_files.add(tok)
        elif tok.startswith("report/evidence/"):
            decl_dirs.add(tok.rstrip("/"))
print("STATE 声明文件:", len(decl_files), "| 声明目录:", len(decl_dirs), sorted(decl_dirs))
for d in sorted(decl_dirs):
    r = subprocess.run(["git", "-C", r"D:\codex-worktrees\w6", "ls-tree", "-r", "--name-only",
                        COMMIT, "--", d], capture_output=True, text=True, encoding="utf-8")
    n = len([x for x in r.stdout.splitlines() if x.strip()])
    ex = os.path.isdir(os.path.join(r"D:\codex-worktrees\w6", d.replace("/", "\\")))
    print(f"  {d}: 提交内文件数={n} | 工作区存在={ex}")
print("=> 提交内不含任何文件、但工作区存在的声明目录：",
      [d for d in sorted(decl_dirs)
       if not subprocess.run(["git", "-C", r"D:\codex-worktrees\w6", "ls-tree", "-r", "--name-only",
                              COMMIT, "--", d], capture_output=True, text=True).stdout.strip()])