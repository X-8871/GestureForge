"""blob 字节形态 vs 清单/哈希文件声明（修正：不再提前 break）。"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\codex-worktrees\w6"


def blob(rev: str, path: str) -> bytes | None:
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def cands(b: bytes) -> dict:
    lf = b.replace(b"\r\n", b"\n")
    return {"raw": hashlib.sha256(b).hexdigest(),
            "lf": hashlib.sha256(lf).hexdigest(),
            "crlf": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}


RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"
man = json.loads(blob("e3aeb09", f"{RUNREL}/delivery_manifest.json"))
declared = {i["path"]: i["sha256"] for i in man["files"]}
hashes_txt = {}
for line in blob("e3aeb09", f"{RUNREL}/hashes_sha256.txt").decode("utf-8").splitlines():
    if line.strip():
        value, rel = line.split("  ", 1)
        hashes_txt[f"{RUNREL}/{rel}"] = value

probe_paths = ["src/stage6/s6_core.py", "src/stage6/s6_actions.py", "src/stage6/s6_params.py",
               "verification/s6b_run_cases.py", "verification/s6b_probe.py",
               "verification/s6b_build_evidence.py", "verification/check_stage_delivery.py",
               "verification/s6_g0_selfcheck.py", "docs/stage6/s6b_frozen_interface_v1.json",
               f"{RUNREL}/run_report.json", f"{RUNREL}/cases/build_case_matrix.py",
               f"{RUNREL}/cases/case_matrix.json", f"{RUNREL}/expected_freeze.json",
               f"{RUNREL}/export_selfproof.json", ".codex/STATE.md"]
print(f"{'path':62s} {'rev':9s} {'form':5s} {'sha256[:16]':18s} declared")
for p in probe_paths:
    for rev in ("e3aeb09", "05126fd", "HEAD"):
        b = blob(rev, p)
        if b is None:
            print(f"{p:62s} {rev:9s} ABSENT")
            continue
        c = cands(b)
        form = "crlf" if b"\r\n" in b else "lf"
        d = declared.get(p)
        tag = ""
        if d:
            tag = [k for k, v in c.items() if v == d]
            tag = f"MATCH({tag[0]})" if tag else "*** NO MATCH ***"
        print(f"{p:62s} {rev:9s} {form:5s} {c['raw'][:16]:18s} {tag}")
print("---- hashes_sha256.txt 对 build_case_matrix.py 声明 ----")
print("declared", hashes_txt.get(f"{RUNREL}/cases/build_case_matrix.py", "")[:16],
      "manifest", declared.get(f"{RUNREL}/cases/build_case_matrix.py", "")[:16])
print("---- STATE.md 提交间差异 ----")
print(subprocess.run(["git", "-C", ROOT, "diff", "05126fd", "e3aeb09", "--", ".codex/STATE.md"],
                     capture_output=True).stdout.decode("utf-8", "replace")[:1500])