#!/usr/bin/env python3
"""S6-B r02 复审：证据包自证一致性、清单/哈希复算、缺失文件与声明扫描。"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

W6 = Path(r"D:\codex-worktrees\w6")
RUN = W6 / "report/evidence/S6-B/s6b_core_20261023_r02"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


print("=== A) delivery_manifest 53 条绑定复算 ===")
man = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
bad, missing = [], []
for item in man["files"]:
    p = W6 / item["path"]
    if not p.is_file():
        missing.append(item["path"]); continue
    if sha(p) != item["sha256"]:
        bad.append((item["path"], item["sha256"], sha(p)))
print(f"declared={len(man['files'])} missing={len(missing)} hash_mismatch={len(bad)}")
print("  missing:", missing)
print("  mismatch:", bad)
print("  source_commit:", man["source_commit"])
src = man["source_commit"]
print("  files declared but absent:", missing)
extra = [p.relative_to(W6).as_posix() for p in RUN.rglob("*") if p.is_file()
         and p.relative_to(W6).as_posix() not in {i["path"] for i in man["files"]}
         and p.name != "delivery_manifest.json"]
print("  files on disk but NOT declared (excl. manifest itself):", extra)

print("\n=== B) hashes_sha256.txt 复算 ===")
lines = (RUN / "hashes_sha256.txt").read_text(encoding="utf-8").strip().splitlines()
bad2, miss2 = [], []
for line in lines:
    digest, name = line.split("  ", 1)
    p = RUN / name
    if not p.is_file():
        miss2.append(name); continue
    if sha(p) != digest:
        bad2.append((name, digest, sha(p)))
print(f"entries={len(lines)} missing={miss2} mismatch={bad2}")

print("\n=== C) 提交的 export_selfproof 与我的复跑对照 ===")
sub = json.loads((RUN / "export_selfproof.json").read_text(encoding="utf-8"))
mine = json.loads(Path(r"D:\FPGA_Competition\tmp\review\S6B_r02_20261023_r01\selfproof_worktree.json")
                  .read_text(encoding="utf-8"))
s, m = sub["subjects"][0], mine["subjects"][0]
for key in ("label", "artifact_version", "run_id", "evidence_dir", "evidence_dir_file_count",
            "state_declared_s6b_dir_files_in_commit", "selfcheck_status", "verdict", "subject"):
    print(f"  {key}: submitted={s.get(key)}  rerun={m.get(key)}  same={s.get(key)==m.get(key)}")
print("  checks(submitted):", [(c["name"][:34], c["exit_code"]) for c in s["checks"]])
print("  checks(rerun)    :", [(c["name"][:34], c["exit_code"]) for c in m["checks"]])
print("  stdout_tail same per check:",
      [a["stdout_tail"] == b["stdout_tail"] for a, b in zip(s["checks"], m["checks"])])
print("  newline_alignment submitted:", json.dumps(s["newline_alignment"], ensure_ascii=False)[:400])
print("  newline_alignment rerun    :", json.dumps(m["newline_alignment"], ensure_ascii=False)[:400])

print("\n=== D) S6-A r07 清单中被 87a6bdc 改动后失配的文件 ===")
s6a = json.loads((W6 / "report/evidence/S6-A/s6a_g0_20261022_r07/delivery_manifest.json")
                 .read_text(encoding="utf-8"))
for item in s6a["files"]:
    if item["path"] in ("verification/export_selfproof.py", ".codex/STATE.md"):
        p = W6 / item["path"]
        print(f"  {item['path']}: manifest={item['sha256'][:16]} now={sha(p)[:16]} "
              f"match={sha(p)==item['sha256']}")

print("\n=== E) 禁止/夸大声明扫描（S6-B 相关文件）===")
targets = list((W6 / "src/stage6").glob("*.py")) + list(RUN.rglob("*.json")) + list(RUN.rglob("*.md")) \
    + [W6 / "verification/s6b_run_cases.py", W6 / "verification/s6b_probe.py",
       W6 / "verification/s6b_build_evidence.py"]
pats = ["已审查", "审查通过", "已通过", "PASS 复核", "approved by", "G0 通过", "验收通过",
        "审查已", "APPROVED", "reviewed by", "G2 通过", "G4 通过", "G5 通过"]
for p in targets:
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for pat in pats:
        for m in re.finditer(re.escape(pat), text):
            ctx = text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
            print(f"  {p.relative_to(W6)} :: {pat} :: ...{ctx}...")