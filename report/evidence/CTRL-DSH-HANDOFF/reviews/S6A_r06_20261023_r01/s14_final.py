#!/usr/bin/env python3
# 只读检查脚本 14：哈希表 + 新 HEAD 下复跑自检并与先前结果比对
import hashlib, json, os, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ISO = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01"
B = ISO + r"\blobs"
WT = r"D:\codex-worktrees\w6"
EV6 = B + r"\r06ev\report\evidence\S6-A\s6a_g0_20261022_r06"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


print("=== 我自算哈希：被审提交 04ea58e1 的文件（工作区字节=证据绑定口径）===")
reviewed = [
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "verification/s6_g0_selfcheck.py",
    "verification/s6a_build_evidence.py",
    "verification/s6a_r06_probe.py",
    ".codex/STATE.md",
    "report/evidence/S6-A/s6a_g0_20261022_r06/hand_computed_cases.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/delivery_manifest.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/inputs_manifest.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/selfcheck_result.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/probe_summary.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/fix_record.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/coverage_matrix.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/limitations_not_executed.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/upstream_bindings.json",
    "report/evidence/S6-A/s6a_g0_20261022_r06/selfcheck_r04_failure.json",
]
for rel in reviewed:
    print(f"{sha(os.path.join(WT, rel.replace('/', os.sep)))}  {rel}")
print()
print("=== r05 基线（1632761）同 4 个源文件哈希（我自算 git 字节）===")
for bl in ("r05_docs_stage6_S6A_stage6_g0_behavior_spec_v1.md",
           "r05_docs_stage6_s6a_stage6_g0_behavior_v1.json",
           "r05_verification_s6_g0_selfcheck.py",
           "r05_verification_s6a_build_evidence.py"):
    print(f"{sha(os.path.join(B, bl))}  {bl}")
print()
print("=== r06 证据目录 36 个文件（我自算）===")
n = 0
for dp, _, fs in os.walk(EV6):
    for f in sorted(fs):
        p = os.path.join(dp, f)
        n += 1
        print(f"{sha(p)}  {os.path.relpath(p, EV6).replace(os.sep, '/')}")
print("文件数:", n)
print()
print("=== 新 HEAD(43f7995) 下复跑自检并与先前结果逐字节比对 ===")
cmd = [sys.executable, "-B", os.path.join(WT, "verification/s6_g0_selfcheck.py"),
       "--json", os.path.join(WT, "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
       "--doc", os.path.join(WT, "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
       "--cases", os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r06/hand_computed_cases.json"),
       "--upstream", os.path.join(WT, "report/evidence/S6-A/s6a_g0_20261022_r06/upstream_bindings.json"),
       "--out", os.path.join(ISO, "runs", "my_selfcheck_r06_after_s6b.json"),
       "--project-root", "D:/codex-worktrees/w6",
       "--evidence-dir", "report/evidence/S6-A/s6a_g0_20261022_r06",
       "--manifest", "report/evidence/S6-A/s6a_g0_20261022_r06/delivery_manifest.json",
       "--state", ".codex/STATE.md"]
r = subprocess.run(cmd, cwd=WT, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("exit code =", r.returncode)
a = json.load(open(os.path.join(ISO, "runs", "my_selfcheck_r06.json"), encoding="utf-8"))
b = json.load(open(os.path.join(ISO, "runs", "my_selfcheck_r06_after_s6b.json"), encoding="utf-8"))
print("两次运行 status:", a["status"], b["status"], "| checks 相同:",
      [(c["id"], c["status"], c["detail"]) for c in a["checks"]] == [(c["id"], c["status"], c["detail"]) for c in b["checks"]])
print("inputs 相同:", a["inputs"] == b["inputs"])
print("入库 selfcheck_result.json 亦相同:",
      json.load(open(EV6 + r"\selfcheck_result.json", encoding="utf-8"))["checks"] == b["checks"])
c11 = next(c["detail"] for c in b["checks"] if c["id"] == "C11")
print("C11 detail:", c11)