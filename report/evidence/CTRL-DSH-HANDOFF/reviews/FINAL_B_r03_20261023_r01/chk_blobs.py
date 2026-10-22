"""比较提交 blob 的字节形态与清单声明（判断换行口径与陈旧绑定）。"""
from __future__ import annotations
import hashlib, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\codex-worktrees\w6"


def blob(rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True, check=True).stdout


def cands(b: bytes) -> dict:
    lf = b.replace(b"\r\n", b"\n")
    return {"raw": hashlib.sha256(b).hexdigest()[:16],
            "lf": hashlib.sha256(lf).hexdigest()[:16],
            "crlf": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()[:16]}


paths = ["report/evidence/S6-B/s6b_core_20261023_r03/run_report.json",
         "report/evidence/S6-B/s6b_core_20261023_r03/cases/build_case_matrix.py",
         "report/evidence/S6-B/s6b_core_20261023_r03/cases/case_matrix.json",
         "report/evidence/S6-B/s6b_core_20261023_r03/expected_freeze.json",
         "src/stage6/s6_core.py",
         ".codex/STATE.md"]
want = {"report/evidence/S6-B/s6b_core_20261023_r03/run_report.json": "0e698c89ddd475bf",
        "report/evidence/S6-B/s6b_core_20261023_r03/cases/build_case_matrix.py": "3ad9a33dc019c47a",
        "report/evidence/S6-B/s6b_core_20261023_r03/cases/case_matrix.json": "b79a68c9a1617833",
        "src/stage6/s6_core.py": "ab75b0740a6d8ce3",
        ".codex/STATE.md": "450ab45dbb172ef2"}
for p in paths:
    for rev in ("e3aeb09", "05126fd"):
        try:
            b = blob(rev, p)
        except subprocess.CalledProcessError:
            print(f"{p} @ {rev}: ABSENT")
            continue
        c = cands(b)
        flag = ""
        if p in want:
            flag = "  <== 清单/哈希文件声明 450ab45d/3ad9a33d/etc" if any(v.startswith(want[p][:16]) for v in c.values()) else ""
        print(f"{p.split('/')[-1]:26s} @{rev}: crlf_in_blob={b'\\r\\n' in b} {c}{flag}")
    m = subprocess.run(["git", "-C", ROOT, "show",
                        "e3aeb09:report/evidence/S6-B/s6b_core_20261023_r03/delivery_manifest.json"],
                       capture_output=True).stdout
    import json
    man = json.loads(m)
    for i in man["files"]:
        if i["path"] == p:
            print(f"    manifest declares sha256 = {i['sha256'][:16]}")
    break
print("---- .gitattributes ----")
ga = Path(ROOT) / ".gitattributes"
print(ga.read_text(encoding="utf-8", errors="replace") if ga.is_file() else "(none)")
print("---- hashes_sha256.txt line for build_case_matrix.py ----")
h = Path(ROOT, "report/evidence/S6-B/s6b_core_20261023_r03/hashes_sha256.txt")
print([l for l in h.read_text(encoding="utf-8").splitlines() if "build_case_matrix" in l])