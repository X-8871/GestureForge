"""清单 source 绑定 vs 交付提交 e3aeb09 的实际字节。"""
from __future__ import annotations
import hashlib, json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\codex-worktrees\w6"
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"


def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


man = json.loads(blob("e3aeb09", f"{RUNREL}/delivery_manifest.json"))
for item in man["files"]:
    if item["role"] != "source":
        continue
    want = item["sha256"]
    for rev in ("e3aeb09", "05126fd", "87a6bdc"):
        b = blob(rev, item["path"])
        if b is None:
            print(f"{item['path']:55s} {rev}: ABSENT")
            continue
        lf = b.replace(b"\r\n", b"\n")
        cands = {"raw": hashlib.sha256(b).hexdigest(), "lf": hashlib.sha256(lf).hexdigest(),
                 "crlf": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}
        tag = [k for k, v in cands.items() if v == want]
        print(f"{item['path']:55s} {rev}: {'MATCH(' + tag[0] + ')' if tag else '*** NO MATCH ***'}")