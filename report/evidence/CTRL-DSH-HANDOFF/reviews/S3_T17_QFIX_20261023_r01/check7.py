"""评审核查 7：修好路径问题后重跑 record 复现、突变体诊断、58 份逐字节比对。"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace", newline="\n")

WT = r"D:\codex-worktrees\dbdf"
R = r"D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01"
ARROW = "\u21d2"


def git(*args):
    return subprocess.run(["git", "--no-optional-locks", "-C", WT, *args], capture_output=True)


def sha1blob(rev, path):
    cp = git("rev-parse", "--verify", "-q", f"{rev}:{path}")
    return cp.stdout.decode().strip() or None


print("=== 1. record 复现（base_commit=当前 HEAD 的临时副本） ===")
cur = git("rev-parse", "HEAD").stdout.decode().strip()
rec_rel = "report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_record_stage3_delivered.json"
rec = json.load(open(os.path.join(WT, rec_rel.replace("/", os.sep)), encoding="utf-8"))
print("keys=", len(rec))
rec2 = dict(rec, base_commit=cur)
tmp = os.path.join(R, "cmd", "record_head_updated.json")
json.dump(rec2, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
cp = subprocess.run(["python", "-B", r"D:\FPGA_Competition\verification\handoff_check.py",
                     "--worktree", WT, "--record", tmp], capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
print("headUpdated rc=", cp.returncode)
for line in cp.stdout.splitlines():
    if line.startswith("[") or line.startswith("结论") or line.startswith("退出码"):
        print("  ", line[:200])
open(os.path.join(R, "cmd", "item4_handoff_headUpdated.txt"), "w", encoding="utf-8",
     newline="\n").write(cp.stdout)

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace", newline="\n")

print("\n=== 2. 突变体 selftest 的 cli_regressions 诊断 ===")
for n in ("m1_arrow_keep_rc", "m2_arrow_no_rc", "b1_noreconf_selftest"):
    p = os.path.join(R, "cmd", "item2", f"{n}.json")
    if not os.path.exists(p):
        print("  MISSING", p)
        continue
    d = json.load(open(p, encoding="utf-8"))
    print(f"--- {n}: {d.get('conclusion')} exit={d.get('exit_code')}")
    for c in d.get("cli_regressions", []):
        print(f"    {c['name']}: exp={c['expected_exit_code']} act={c['actual_exit_code']} "
              f"json={c['json_written']} matched={c['matched']}")
        print("      stdout_head=", repr(c["stdout_head"])[:200])
        print("      stderr_tail=", repr(c["stderr_tail"])[:240])

print("\n=== 3. 58 份含箭头证据文件的逐字节比对（修正版） ===")
cp = git("grep", "-l", ARROW, "f77f363", "--", "report/evidence")
ev = [x for x in cp.stdout.decode("utf-8", "replace").splitlines() if x]
print("evidence_files_with_arrow@f77f363 =", len(ev))
same, diff = [], []
for f in ev:
    a, b = sha1blob("f77f363", f), sha1blob("605f960", f)
    (diff if a != b else same).append(f)
print("byte_identical =", len(same), " differing =", len(diff))
for f in diff:
    print("   DIFF", f)
print("\n--- 按目录分组 ---")
from collections import Counter
print("  all with arrow:", Counter(f.split("/")[2] for f in ev))
print("  differing     :", Counter(f.split("/")[2] for f in diff))
print("\n=== 4. .codex/STATE.md 与 record 的箭头计数 ===")
for p in (".codex/STATE.md", rec_rel):
    a = git("show", f"f77f363:{p}").stdout.decode("utf-8", "replace").count(ARROW)
    b = git("show", f"605f960:{p}").stdout.decode("utf-8", "replace").count(ARROW)
    print(f"  {p}: {a} -> {b}")