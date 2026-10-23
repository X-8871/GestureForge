"""评审核查 4：箭头逐文件比对、cmos 计数候选口径、突变体诊断、record 复核、硬件痕迹。"""
import json
import os
import subprocess
import sys

WT = r"D:\codex-worktrees\dbdf"
CLONE = r"D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01\clonet"
OUT = r"D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01\cmd"
ARROW = "\u21d2"
SCOPES = ["report", ".codex", "scripts"]


def git(repo, *args):
    return subprocess.run(["git", "--no-optional-locks", "-C", repo, *args],
                          capture_output=True)


def arrow_map(repo, rev):
    cp = git(repo, "grep", "-c", ARROW, rev, "--", *SCOPES)
    out = cp.stdout.decode("utf-8", "replace")
    m = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        head, _, rest = line.partition(":")
        path, _, cnt = rest.rpartition(":")
        m[path] = int(cnt)
    return m


old = arrow_map(WT, "f77f363")
new = arrow_map(WT, "605f960")
print(f"rev_with_arrows: f77f363={len(old)} 605f960={len(new)}")
print("\n=== 箭头减少的文件（路径 / old -> new） ===")
for path in sorted(set(old) | set(new)):
    a, b = old.get(path, 0), new.get(path, 0)
    if a != b:
        print(f"  {path}  {a} -> {b}   [evidence={path.startswith('report/evidence')}]")
print("\n=== 箭头完全消失的已提交证据文件 ===")
gone_ev = [p for p in old if old[p] and new.get(p, 0) == 0 and p.startswith("report/evidence")]
for p in sorted(gone_ev):
    print("  ", p)
print("  count =", len(gone_ev))

print("\n=== 这些文件的 diff 是否只有箭头替换？（非箭头改动行数） ===")
for p in sorted(gone_ev) + [".codex/STATE.md"]:
    cp = git(WT, "diff", "--unified=0", "f77f363", "605f960", "--", p)
    d = cp.stdout.decode("utf-8", "replace")
    minus = [ln for ln in d.splitlines() if ln.startswith("-") and not ln.startswith("---")]
    plus = [ln for ln in d.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    pure = sum(1 for a, b in zip(minus, plus) if a[1:].replace(ARROW, "=>") == b[1:])
    print(f"  {p}: -{len(minus)}/+{len(plus)} 纯箭头替换行={pure}")

print("\n=== 被点名的历史证据例子 ===")
for p in ["report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/handoff_check_claim.json",
          "report/evidence/S3-T17/t17_fix_20261023_r01/fix_record.md",
          "report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/fix_record.md"]:
    a = git(WT, "rev-parse", f"f77f363:{p}").stdout.decode().strip()
    b = git(WT, "rev-parse", f"605f960:{p}").stdout.decode().strip()
    print(f"  {p}\n    old={a or '<absent>'} new={b or '<absent>'} same={'YES' if a and a == b else 'NO'}")
    blob = git(WT, "show", f"605f960:{p}").stdout.decode("utf-8", "replace")
    print(f"    arrows@605f960={blob.count(ARROW)}")

print("\n=== cmos_8_16bit* 计数候选口径 ===")
cands = {
    "dbdf *.v (excl .git)": ["-name", "cmos_8_16bit*.v", "-not", "-path", "*/.git/*"],
    "dbdf any ext (excl .git)": ["-name", "cmos_8_16bit*", "-not", "-path", "*/.git/*"],
    "dbdf *.v incl .git": ["-name", "cmos_8_16bit*.v"],
    "dbdf exact name cmos_8_16bit.v (excl .git)": ["-name", "cmos_8_16bit.v", "-not", "-path", "*/.git/*"],
}
for label, args in cands.items():
    cp = subprocess.run(["find", "/d/codex-worktrees/dbdf", *args], capture_output=True)
    n = len([x for x in cp.stdout.decode("utf-8", "replace").splitlines() if x])
    print(f"  {label}: {n}")
cp = subprocess.run(["find", "/d/codex-worktrees", "/d/FPGA_Competition", "-name", "cmos_8_16bit*.v",
                     "-not", "-path", "*/.git/*"], capture_output=True)
print("  codex-worktrees + FPGA_Competition (both trees):",
      len([x for x in cp.stdout.decode('utf-8', 'replace').splitlines() if x]))
cp = subprocess.run(["find", "/d/FPGA_Competition", "-name", "cmos_8_16bit*.v", "-not", "-path", "*/.git/*"],
                    capture_output=True)
print("  FPGA_Competition (incl w2b):", len([x for x in cp.stdout.decode('utf-8', 'replace').splitlines() if x]))

print("\n=== 参考文件行号对照（多份副本） ===")
cp = subprocess.run(["find", "/d/codex-worktrees", "/d/FPGA_Competition", "-name", "cmos_8_16bit*.v",
                     "-not", "-path", "*/.git/*"], capture_output=True)
paths = [x for x in cp.stdout.decode("utf-8", "replace").splitlines() if x]
hit157 = []
for p in paths:
    try:
        raw = open(p, "rb").read().replace(b"\r\n", b"\n")
    except OSError:
        continue
    lines = raw.decode("utf-8", "replace").split("\n")
    idx = [i + 1 for i, ln in enumerate(lines) if "pdata_o <= {pdata_i_d0,pdata_i};" in ln]
    if 157 in idx:
        hit157.append((p, len(lines), idx))
print("  含 157 行的副本数:", len(hit157))
for p, n, idx in hit157[:5]:
    print("   ", p, "lines=", n, "idx=", idx[:3])
print("  总副本数:", len(paths))

print("\n=== 突变体诊断 ===")
for f in ["analyze_arrow_keep_rc.py", "analyze_arrow_no_rc.py"]:
    p = os.path.join(r"D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01\mutations", f)
    if not os.path.exists(p):
        print("  MISSING", p)
        continue
    src = open(p, encoding="utf-8").read()
    print(f"  {f}: arrows={src.count(ARROW)} reconfigure_call_lines="
          f"{[i+1 for i, ln in enumerate(src.split(chr(10))) if ln.strip() == '_force_utf8_streams()']}")

print("\n=== 硬件痕迹（F3/G4 新增文件 + 工具） ===")
pat = ["T17_LINK_EXIT=", "T17_BASELINE_CAPTURE_EXIT=", "T17_BARS_CAPTURE_EXIT=",
       "program_hw_devices", "hw_server", "COM4", "xsdb", "write_bitstream"]
cp = git(WT, "diff", "--name-only", "f77f363", "975f3a5")
files = [x for x in cp.stdout.decode().splitlines() if x]
for p in files:
    try:
        blob = git(WT, "show", f"975f3a5:{p}").stdout.decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        continue
    for k in pat:
        if k in blob:
            print(f"  HIT {k} in {p}")
print("  (无 HIT 行即为无痕迹)")