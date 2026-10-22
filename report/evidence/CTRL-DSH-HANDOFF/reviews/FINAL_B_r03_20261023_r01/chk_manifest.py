"""只读核验：r03 交付清单的绑定、索引与漂移（不写被审工作树）。"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\codex-worktrees\w6")
RUN = ROOT / "report/evidence/S6-B/s6b_core_20261023_r03"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


man = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
print("manifest source_commit =", man["source_commit"])
print("manifest entries =", len(man["files"]))
print("checks =", [(c["name"], c["status"], c["exit_code"]) for c in man["checks"]])
print("tool_versions =", man.get("tool_versions"))
print("limitations:")
for l in man["limitations"]:
    print("   -", l)

# 逐条复算
missing, mismatched = [], []
for i, item in enumerate(man["files"]):
    p = ROOT / item["path"]
    if not p.is_file():
        missing.append((i, item["path"]))
        continue
    if sha(p) != item["sha256"]:
        mismatched.append((i, item["path"], item["sha256"], sha(p)))
print("missing =", missing)
print("mismatched =", [(i, p) for i, p, *_ in mismatched])
for i, p, want, got in mismatched:
    print(f"  [{i}] {p}\n      want {want}\n      got  {got}")

# files[54] 身份
if len(man["files"]) > 54:
    print("files[54] =", man["files"][54]["path"], man["files"][54]["sha256"])

# 盘上未声明文件（除清单自身）
declared = {item["path"] for item in man["files"]}
actual = {p.relative_to(ROOT).as_posix() for p in RUN.rglob("*") if p.is_file()}
print("undeclared =", sorted(actual - declared))
print("declared-but-absent =", sorted(declared - actual - {x for x in declared if not (ROOT / x).is_file()}))

# 清单中的 source 条目绑定的是哪个提交
SRC = [i["path"] for i in man["files"] if i["role"] == "source"]
print("source entries =", len(SRC))
for rev in ("e3aeb09", "87a6bdc", "05126fd"):
    ok = bad = 0
    for s in SRC:
        try:
            blob = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{s}"],
                                  capture_output=True, check=True).stdout
        except subprocess.CalledProcessError:
            bad += 1
            continue
        if hashlib.sha256(blob).hexdigest() == next(i["sha256"] for i in man["files"] if i["path"] == s):
            ok += 1
        else:
            bad += 1
    print(f"  source hashes vs {rev}: match {ok} / mismatch {bad}")

# hashes_sha256.txt 复算
h = RUN / "hashes_sha256.txt"
lines = h.read_text(encoding="utf-8").splitlines()
bad = [l for l in lines if l.strip() and sha(RUN / l.split("  ", 1)[1]) != l.split("  ", 1)[0]]
print("hashes_sha256.txt lines =", len(lines), "mismatch =", len(bad))
for l in bad:
    print("   BAD:", l)