"""对提交 e3aeb09 的 r03 证据包做内部一致性核验（清单声明 vs 提交字节；含换行口径分析）。"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\FPGA_Competition\tmp\review\FINAL_B_20261023_r01\iso_e3aeb09")
RUN = ROOT / "report/evidence/S6-B/s6b_core_20261023_r03"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def candidates(b: bytes):
    lf = b.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return {"raw": sha(b), "lf": sha(lf), "crlf": sha(crlf)}


man = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
print("source_commit =", man["source_commit"])
print("entries =", len(man["files"]))
missing, ok_raw, ok_lf, ok_crlf, unresolved = [], [], [], [], []
for i, item in enumerate(man["files"]):
    p = ROOT / item["path"]
    if not p.is_file():
        missing.append((i, item["path"]))
        continue
    b = p.read_bytes()
    c = candidates(b)
    want = item["sha256"]
    if c["raw"] == want:
        ok_raw.append(i)
    elif c["lf"] == want:
        ok_lf.append(i)
    elif c["crlf"] == want:
        ok_crlf.append(i)
    else:
        unresolved.append((i, item["path"], want, c))
print("missing =", missing)
print(f"raw-match={len(ok_raw)} lf-match={len(ok_lf)} crlf-match={len(ok_crlf)} unresolved={len(unresolved)}")
for i, p, want, c in unresolved:
    print(f"  UNRESOLVED [{i}] {p}\n     want {want}\n     raw {c['raw']} lf {c['lf']} crlf {c['crlf']}")
print("lf-match paths:", [man['files'][i]['path'].split('/')[-1] for i in ok_lf][:12])
print("crlf-match paths:", [man['files'][i]['path'].split('/')[-1] for i in ok_crlf][:12])

# 清单自身 & hashes_sha256.txt
h = RUN / "hashes_sha256.txt"
lines = [l for l in h.read_text(encoding="utf-8").splitlines() if l.strip()]
bad = []
for l in lines:
    want, rel = l.split("  ", 1)
    p = RUN / rel
    if not p.is_file():
        bad.append(("missing", rel))
        continue
    if sha(p.read_bytes()) != want:
        bad.append(("mismatch", rel, want, sha(p.read_bytes())))
print("hashes_sha256.txt lines =", len(lines), "bad =", len(bad))
for x in bad[:8]:
    print("  ", x)

# 声明 vs 盘上
declared = {i["path"] for i in man["files"]}
actual = {p.relative_to(ROOT).as_posix() for p in RUN.rglob("*") if p.is_file()}
print("undeclared in run dir =", sorted(actual - declared))
print("declared but absent =", sorted(x for x in declared - actual))

# 关键清单字段
print("checks =", [(c["name"], c["status"], c["exit_code"]) for c in man["checks"]])
print("limitations[0] =", man["limitations"][0])