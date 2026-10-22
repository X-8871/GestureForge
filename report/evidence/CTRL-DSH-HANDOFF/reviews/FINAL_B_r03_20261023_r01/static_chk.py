"""静态核验（读取提交 e3aeb09 的 blob，不受 w6 工作区脏改动影响）。"""
from __future__ import annotations
import json, re, subprocess, sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"D:\codex-worktrees\w6"
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"
REV = "e3aeb09"


def blob(rev: str, path: str) -> str:
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""


def blobs(rev: str, prefix: str) -> dict:
    lst = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", rev, prefix],
                         capture_output=True).stdout.decode("utf-8", "replace").splitlines()
    return {p: blob(rev, p) for p in lst if p.strip()}


rep_txt = blob(REV, f"{RUNREL}/run_report.json")
rep = json.loads(rep_txt)
print("=== 1) BLK-r02-1 acquisition_id ===")
c3 = next(c for c in rep["cases"] if c["case_id"] == "C3-lost-then-reappear")
print("C3 action_records acquisition_id 序列 =", [r.get("acquisition_id") for r in c3["observed"]["action_records"]])
print("C3 observed transitions =", c3["observed"]["transitions"])
print("C3 status =", c3["status"])
acq_case = {}
for c in rep["cases"]:
    ids = [r.get("acquisition_id") for r in c["observed"]["action_records"]]
    if ids:
        acq_case[c["case_id"]] = ids
print("各用例 action acquisition_id 序列：", json.dumps(acq_case, ensure_ascii=False))
print("run_report 中 'acquisition_id' 命中 =", rep_txt.count("acquisition_id"))
logs = blobs(REV, f"{RUNREL}/logs")
print("logs 文件数 =", len(logs), " 'acquisition_id' 命中总数 =", sum(t.count("acquisition_id") for t in logs.values()))
# 每帧日志是否都带 acquisition_id
missing_frames = []
for name, txt in logs.items():
    for line in txt.splitlines():
        row = json.loads(line)
        if row.get("kind") == "step" and "acquisition_id" not in row:
            missing_frames.append((name, row.get("frame_id"), row.get("transition")))
print("step 日志缺 acquisition_id 的帧数 =", len(missing_frames), missing_frames[:5])
# action_ack 日志
ack_no_id = []
for name, txt in logs.items():
    for line in txt.splitlines():
        row = json.loads(line)
        if row.get("kind") != "action_ack":
            continue
        if "acquisition_id" not in row:
            ack_no_id.append(name)
print("action_ack 日志缺 acquisition_id 的条数 =", len(ack_no_id), sorted(set(ack_no_id))[:3])

print("\n=== 2) BLK-r02-2 action_records / ACTION_* / 死常量 ===")
allrec = [r for c in rep["cases"] for r in c["observed"].get("action_records", [])]
print("action_records 总条数 =", len(allrec))
keys = set().union(*[set(r) for r in allrec]) if allrec else set()
need = ["action_type", "target_id", "acquisition_id", "t_trigger_ns", "event", "effective_event",
        "action_id", "submit_result", "effective_result", "suppression"]
print("字段存在性：", {k: (k in keys) for k in need})
cnt = Counter()
for r in allrec:
    for k in ("event", "effective_event"):
        if r.get(k):
            cnt[r[k]] += 1
print("event/effective_event 计数 =", dict(cnt))
for name in ("ACTION_SUBMITTED", "ACTION_EFFECTIVE", "ACTION_FAILED", "ACTION_UNOBSERVED", "S_DEDUP"):
    print(f"  证据文本中 '{name}' 命中（run_report+logs） =",
          rep_txt.count(name) + sum(t.count(name) for t in logs.values()))
for path in ("src/stage6/s6_core.py", "src/stage6/s6_actions.py"):
    text = blob(REV, path)
    names = set(re.findall(r"^([A-Z][A-Z0-9_]{2,})\s*=", text, flags=re.MULTILINE))
    unused = [n for n in sorted(names) if len(re.findall(rf"\b{n}\b", text)) <= 1]
    print(f"{path}: 常量 {len(names)} 个，未使用 = {unused}")
    for dead in ("OUT_SUBMITTED", "OUT_EFFECTIVE", "OUT_FAILED", "OUT_UNOBSERVED", "SUP_DEDUP", "STATES"):
        print(f"    {dead}: {'存在' if re.search(rf'^{dead}\s*=', text, re.M) else '已删除'}")

print("\n=== 3) 版本 / 计数 / 登记 ===")
for path in ("src/stage6/s6_core.py", "src/stage6/s6_params.py", "docs/stage6/s6b_frozen_interface_v1.json",
             f"{RUNREL}/s6b_run_summary.md", f"{RUNREL}/reachability_notes.json",
             f"{RUNREL}/delivery_manifest.json", f"{RUNREL}/cases/case_matrix.json",
             f"{RUNREL}/cases/build_case_matrix.py", f"{RUNREL}/export_selfproof.md",
             f"{RUNREL}/probe_summary.json", "verification/s6b_probe.py"):
    t = blob(REV, path)
    hits = re.findall(r"S6A-G0-v1\.[0-9]|v1\.[0-9]|21 例|三项退出码", t)
    print(f"{path}: {sorted(set(hits))}")
print("契约令牌出现统计（全 run 目录）：",
      Counter(re.findall(r"S6A-G0-v1\.[0-9]", rep_txt + blob(REV, f"{RUNREL}/params_snapshot.json"))))
lim = json.loads(blob(REV, f"{RUNREL}/limitations_not_executed.json"))
print("not_run 条数=", len(lim["not_run"]), "not_implemented=", lim["not_implemented"])
print("open_behavior_deviations=", lim["open_behavior_deviations"])
print("reachability_counted=", lim["reachability_counted"])
print("not_counted=", lim["reachability_not_counted_as_coverage"])
print("D7 =", blob(REV, "src/stage6/s6_core.py").split('"D7')[1][:260].replace("\n", " "))
print("D8 =", blob(REV, "src/stage6/s6_core.py").split('"D8')[1][:300].replace("\n", " "))
probe_s = json.loads(blob(REV, f"{RUNREL}/probe_summary.json"))
print("probe baseline note =", [r["note"] for r in probe_s["results"] if r["probe_id"] == "baseline"])
ps = json.loads(blob(REV, f"{RUNREL}/params_snapshot.json"))
print("params 数 =", len(ps["parameters"]), " 全 PENDING =", ps["all_parameters_pending_approval"])
print("params 值=", {p["id"]: p["draft_value"] for p in ps["parameters"]})
summ = blob(REV, f"{RUNREL}/s6b_run_summary.md")
print("summary 回填行 =", [l for l in summ.splitlines() if "交付检查" in l])
print("summary 用例数行 =", [l for l in summ.splitlines() if "用例：" in l])
mani = json.loads(blob(REV, f"{RUNREL}/delivery_manifest.json"))
print("manifest case/selfproof check =", json.dumps([c for c in mani["checks"] if "自证" in c["name"]], ensure_ascii=False))
print("case_matrix contract_version =", json.loads(blob(REV, f"{RUNREL}/cases/case_matrix.json")).get("contract_version"))
print("cases 数 =", len(json.loads(blob(REV, f"{RUNREL}/cases/case_matrix.json"))["cases"]))
print("matrix_class 数 =", len({c.get("matrix_class") for c in json.loads(blob(REV, f'{RUNREL}/cases/case_matrix.json'))["cases"]}))
print("\n=== 4) 自证兄弟报告（各提交版本） ===")
for rev in ("e3aeb09", "f3c537d"):
    t = blob(rev, f"{RUNREL}_selfproof/export_selfproof.json")
    if not t:
        print(rev, "ABSENT"); continue
    d = json.loads(t)
    print(rev, "verdict=", d["verdict"], "subjects=",
          [(s.get("label"), s["verdict"], [c["exit_code"] for c in s["checks"]]) for s in d["subjects"]])
    print("      generated_at=", d.get("generated_at"), " artifact_versions=",
          [s.get("artifact_version") for s in d["subjects"]])