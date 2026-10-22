#!/usr/bin/env python3
# 只读检查脚本 11：run_summary / manifest checks / §18 重复段 / S6-B 目录清点 / r01..r05 未改动
import json, os, subprocess, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
EV6 = ISO + r"\blobs\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"
WT = r"D:\codex-worktrees\w6"

print("=== S6A_run_summary.md 全文 ===")
print(open(EV6 + r"\S6A_run_summary.md", encoding="utf-8").read())

print("=== delivery_manifest.json 非 files 块 ===")
m = json.load(open(EV6 + r"\delivery_manifest.json", encoding="utf-8"))
print(json.dumps({k: v for k, v in m.items() if k != "files"}, ensure_ascii=False, indent=1))

print()
print("=== inputs_manifest.json 非 files 块 ===")
im = json.load(open(EV6 + r"\inputs_manifest.json", encoding="utf-8"))
print(json.dumps({k: v for k, v in im.items() if k != "files"}, ensure_ascii=False, indent=1))

print()
print("=== doc §18 的 r06 行（检查重复段）===")
doc = open(ISO + r"\blobs\r06_docs_stage6_S6A_stage6_g0_behavior_spec_v1.md", encoding="utf-8").read()
lines = doc.splitlines()
for i, ln in enumerate(lines):
    if "本轮（v1.5 / r06）运行证据" in ln:
        print("行号:", i + 1, "| 长度:", len(ln))
        idx = ln.find("（清单")
        print("首次出现「（清单」位置:", idx)
        # 找重复：第二次出现 "缓存 `tmp/6/S6-A/s6a_g0_20261022_r06/（不入库）。"
        for pat in ["缓存 `tmp/6/S6-A/s6a_g0_20261022_r06/（不入库）。",
                    "（清单与自检：`delivery_manifest.json`",
                    "缓存 `tmp/6/S6-A/s6a_g0_20261022_r05/（不入库）。"]:
            print(f"  出现 {pat[:36]!r} 次数:", ln.count(pat))
        j = ln.find("（清单与自检：", idx + 3)
        print("  第二段起点:", j)
        print("  重复段片段:", ln[j:j + 200] if j > 0 else "（无）")
        print("  重复段是否含 r05 缓存路径:", "s6a_g0_20261022_r05/（不入库）" in ln[j:] if j > 0 else None)

print()
print("=== S6-B 证据目录清点（工作区，未跟踪；仅列事实，不评价内容）===")
sb = os.path.join(WT, "report/evidence/S6-B/s6b_core_20261023_r01")
if os.path.isdir(sb):
    for dp, dns, fs in os.walk(sb):
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(dp, f), sb).replace("\\", "/")
            print("  ", rel, os.path.getsize(os.path.join(dp, f)))
        for d in sorted(dns):
            print("   [dir]", os.path.relpath(os.path.join(dp, d), sb).replace("\\", "/"))
else:
    print("  不存在")
print("STATE 的 S6-B 行点名文件是否都存在:",
      {n: os.path.isfile(os.path.join(sb, n)) for n in
       ("run_report.json", "expected_freeze.json", "probe_summary.json", "params_snapshot.json",
        "reachability_notes.json", "limitations_not_executed.json", "delivery_manifest.json",
        "inputs_manifest.json", "hashes_sha256.txt", "check_inputs_mode_output.txt",
        "check_evidence_mode_output.txt", "s6b_run_summary.md", "cases/case_matrix.json")})

print()
print("=== 提交内 r01..r05 是否被改动 ===")
r = subprocess.run(["git", "-C", WT, "diff", "--name-status", "1632761", "04ea58e1", "--",
                    "report/evidence/S6-A/s6a_g0_20261022_r01", "report/evidence/S6-A/s6a_g0_20261022_r02",
                    "report/evidence/S6-A/s6a_g0_20261022_r03", "report/evidence/S6-A/s6a_g0_20261022_r04",
                    "report/evidence/S6-A/s6a_g0_20261022_r05"],
                   capture_output=True, text=True, encoding="utf-8")
print("diff 输出:", repr(r.stdout.strip()) or "（空 = 未改动）", "| rc=", r.returncode)

print()
print("=== 工作区漂移（未跟踪 + 已跟踪修改）===")
r = subprocess.run(["git", "-C", WT, "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
print()
r = subprocess.run(["git", "-C", WT, "status", "--porcelain", "--untracked-files=all"], capture_output=True,
                   text=True, encoding="utf-8")
unt = [l for l in r.stdout.splitlines()]
print("未跟踪条目数(-uall):", len(unt))
for l in unt[:25]:
    print("  ", l)
print()
print("=== 被审提交内文件哈希 vs 工作区（是否漂移）===")
for rel in ("docs/stage6/s6a_stage6_g0_behavior_v1.json",
            "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
            "verification/s6_g0_selfcheck.py", "verification/s6a_build_evidence.py",
            "verification/s6a_r06_probe.py", ".codex/STATE.md",
            "report/evidence/S6-A/s6a_g0_20261022_r06/selfcheck_result.json",
            "report/evidence/S6-A/s6a_g0_20261022_r06/hand_computed_cases.json"):
    r = subprocess.run(["git", "-C", WT, "diff", "--quiet", "04ea58e1", "--", rel],
                       capture_output=True, text=True)
    print(f"  {rel}: 工作区与提交一致={r.returncode == 0}")