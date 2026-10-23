"""评审核查 5：证据目录 hashes_sha256.txt 与实际 blob 字节的绑定核对。"""
import hashlib
import subprocess
import sys

WT = r"D:\codex-worktrees\dbdf"


def blob(rev, path):
    cp = subprocess.run(["git", "--no-optional-locks", "-C", WT, "show", f"{rev}:{path}"],
                        capture_output=True)
    return cp.stdout if cp.returncode == 0 else None


def check(dirpath, hashes_path, revs):
    raw = blob(revs[-1], hashes_path)
    if raw is None:
        print(f"!! {hashes_path} 不存在")
        return
    entries = []
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        h, _, p = line.partition("  ")
        entries.append((h, p))
    print(f"\n=== {dirpath}（{hashes_path}） ===")
    for h, p in entries:
        full = f"{dirpath}/{p}"
        row = []
        for rev in revs:
            b = blob(rev, full)
            if b is None:
                row.append(f"{rev}=<absent>")
            else:
                row.append(f"{rev}={hashlib.sha256(b).hexdigest()[:12]}({len(b)}B)")
        ok = "OK" if blob(revs[-1], full) is not None and hashlib.sha256(blob(revs[-1], full)).hexdigest() == h else "MISMATCH"
        print(f"  {p:44s} rec={h[:12]}  {'  '.join(row)}  -> {ok}")


REVS = ["f77f363", "605f960", "975f3a5"]
check("report/evidence/S3-T17/t17_color_retest_prep_20261023_r01",
      "report/evidence/S3-T17/t17_color_retest_prep_20261023_r01/hashes_sha256.txt", REVS)
check("report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01",
      "report/evidence/S3-CTRL/S3-T17/t17_takeover_20261023_r01/hashes_sha256.txt", REVS)
check("report/evidence/S3-T17/t17_quickfix_20261023_r01",
      "report/evidence/S3-T17/t17_quickfix_20261023_r01/hashes_sha256.txt", REVS)
check("report/evidence/S3-T17/t17_fix_20261023_r01",
      "report/evidence/S3-T17/t17_fix_20261023_r01/hashes_sha256.txt", REVS)
check("report/evidence/S3-T17/t17_quickfix_preflight_20261023_r01",
      "report/evidence/S3-T17/t17_quickfix_preflight_20261023_r01/hashes_sha256.txt", REVS)

print("\n=== 4 个被机械改写的证据文件：F3 前后 blob 是否与 prep hashes 一致 ===")
prep = "report/evidence/S3-T17/t17_color_retest_prep_20261023_r01"
for p in ["README.md", "t17_artifacts_verified.json", "t17_judgement_table.json", "t17_judgement_table.md"]:
    for rev in REVS:
        b = blob(rev, f"{prep}/{p}")
        print(f"  {p:34s} {rev} sha256={(hashlib.sha256(b).hexdigest() if b else '<absent>')} size={len(b) if b else '-'}")