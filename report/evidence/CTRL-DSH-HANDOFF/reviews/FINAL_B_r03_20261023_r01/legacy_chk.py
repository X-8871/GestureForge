"""遗留项核验：重复键/自赋值、参数未变、接口文件哈希、声明缺失、禁止声明。"""
from __future__ import annotations
import json, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\codex-worktrees\w6"
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"
RUN2 = "report/evidence/S6-B/s6b_core_20261023_r02"


def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else b""


def text(rev, path):
    return blob(rev, path).decode("utf-8", "replace")


print("=== 重复键 / 自赋值（e3aeb09） ===")
core = text("e3aeb09", "src/stage6/s6_core.py")
seg = core.split("request = {")[1].split("}")[0]
print("request 字典内 acquisition_id 出现次数 =", seg.count('"acquisition_id"'))
for i, line in enumerate(core.splitlines(), 1):
    if '"acquisition_id"' in line and "self.acquisition_id" in line:
        print(f"   s6_core.py:{i}: {line.strip()}")
params = text("e3aeb09", "src/stage6/s6_params.py")
for i, line in enumerate(params.splitlines(), 1):
    if re.match(r"\s*self\.(\w+) = self\.\1\s*$", line):
        print(f"   自赋值 s6_params.py:{i}: {line.strip()}")
esp = text("e3aeb09", "verification/export_selfproof.py")
print("   state_declared_s6b_dir_files_in_commit 赋值行:",
      [l.strip() for l in esp.splitlines() if "state_declared_s6b_dir_files_in_commit" in l][:2])

print("\n=== 24 项参数是否与 r02 相同 ===")
p_new = json.loads(text("e3aeb09", f"{RUNREL}/params_snapshot.json"))
p_old = json.loads(text("87a6bdc", f"{RUN2}/params_snapshot.json"))
new_vals = {p["id"]: (p["draft_value"], p["unit"], p["comparison"], p["approval_status"]) for p in p_new["parameters"]}
old_vals = {p["id"]: (p["draft_value"], p["unit"], p["comparison"], p["approval_status"]) for p in p_old["parameters"]}
print("参数条数:", len(new_vals), len(old_vals), " 集合相同:", set(new_vals) == set(old_vals))
print("值/单位/比较/状态 完全相同的项数:", sum(1 for k in new_vals if new_vals[k] == old_vals.get(k)), "/", len(new_vals))
for k in new_vals:
    if new_vals[k] != old_vals.get(k):
        print("   差异", k, old_vals.get(k), "->", new_vals[k])

print("\n=== 接口文件哈希：r02 vs r03 ===")
import hashlib
for rev in ("87a6bdc", "e3aeb09", "f3c537d"):
    b = blob(rev, "docs/stage6/s6b_frozen_interface_v1.json")
    print(f"   {rev}: {hashlib.sha256(b).hexdigest()[:24]} bytes={len(b)}")
fi = json.loads(text("e3aeb09", "docs/stage6/s6b_frozen_interface_v1.json"))
print("   artifact_version=", fi.get("artifact_version"), " status_note=", fi.get("status_note")[:80])
print("   contract=", json.dumps(fi.get("contract"), ensure_ascii=False)[:200])

print("\n=== S6-A 侧 M4 残留（仅记录，属 S6-A 范围） ===")
beh = json.loads(text("e3aeb09", "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
m4 = [t for t in beh["transitions"] if t["id"] == "M4"][0]
print("   transitions[M4].reachability =", m4.get("reachability"), "| note =", str(m4.get("reachability_note"))[:60])
print("   reachability.transitions.M4.status =", beh["reachability"]["transitions"]["M4"]["status"])

print("\n=== 清单声明 vs 提交内实际文件 ===")
man = json.loads(text("e3aeb09", f"{RUNREL}/delivery_manifest.json"))
missing = [i["path"] for i in man["files"] if b"" == blob("e3aeb09", i["path"]) and not _is_empty_ok(i["path"])] if False else []
for i in man["files"]:
    r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", f"e3aeb09:{i['path']}"], capture_output=True)
    if r.returncode != 0:
        missing.append(i["path"])
print("   清单 55 条中在提交内不存在的 =", missing)
# 盘上未声明
lst = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", "e3aeb09", RUNREL],
                     capture_output=True).stdout.decode().splitlines()
declared = {i["path"] for i in man["files"]}
print("   run 目录内未声明文件 =", sorted(set(lst) - declared - {f"{RUNREL}/delivery_manifest.json"}))
print("   hashes_sha256.txt 行数 =", len([l for l in text("e3aeb09", f"{RUNREL}/hashes_sha256.txt").splitlines() if l.strip()]))

print("\n=== 禁止声明扫描（S6-B 包 + 代码） ===")
pat = re.compile(r"已审查|审查通过|已通过|验收通过|G2 通过|G4 通过|G5 通过|审查完成")
paths = [f"{RUNREL}/{n}" for n in ("s6b_run_summary.md", "delivery_manifest.json", "inputs_manifest.json",
                                   "limitations_not_executed.json", "reachability_notes.json",
                                   "claim_verification.md", "probe_summary.json", "export_selfproof.md")]
paths += ["src/stage6/s6_core.py", "src/stage6/s6_actions.py", "src/stage6/s6_params.py"]
for p in paths:
    t = text("e3aeb09", p)
    hits = [(i, l.strip()[:150]) for i, l in enumerate(t.splitlines(), 1) if pat.search(l)]
    if hits:
        print(f"   {p}: {hits}")