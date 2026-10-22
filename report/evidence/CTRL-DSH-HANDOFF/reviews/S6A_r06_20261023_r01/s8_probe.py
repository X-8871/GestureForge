#!/usr/bin/env python3
# 只读检查脚本 8：忠实复刻 r06 探针的 8 例 + 旧口径对照（不写入 w6；注入副本与 --out 落隔离目录）
import importlib.util, json, os, subprocess, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ISO = pathlib.Path(r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01")
ROOT = pathlib.Path(r"D:\codex-worktrees\w6")
RUN_REL = "report/evidence/S6-A/s6a_g0_20261022_r06"
RUN = ROOT / RUN_REL
EV = ISO / "blobs/r06ev/report/evidence/S6-A/s6a_g0_20261022_r06"
W = ISO / "runs/probe"
W.mkdir(parents=True, exist_ok=True)
SELFCHECK = ROOT / "verification/s6_g0_selfcheck.py"
BEHAVIOR = ROOT / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
DOC = ROOT / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"

spec = importlib.util.spec_from_file_location("r06probe", ISO / "blobs/r06_verification_s6a_r06_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

INJ = probe.INJECTIONS
print("INJECTIONS 条目数 =", len(INJ),
      "| target 非 None（真注入）= ", sum(1 for e in INJ if e["target"] is not None),
      "| 基线 =", sum(1 for e in INJ if e["target"] is None))
print("注入 id:", [e["id"] for e in INJ])
print()

lib = json.load(open(EV / "probe_summary.json", encoding="utf-8"))
print("入库 probe_summary.composition =", lib.get("composition"))
print("入库 injection_count =", lib.get("injection_count"), "| total_runs =", lib.get("total_runs"),
      "| results =", len(lib.get("results", [])), "| baseline_verdict =", lib.get("baseline_verdict"))
print()

mine = []
for entry in INJ:
    cid = entry["id"]
    json_path, cases_path = BEHAVIOR, RUN / "hand_computed_cases.json"
    detail = "（无注入）"
    if entry["target"] == "json":
        data = json.loads(BEHAVIOR.read_text(encoding="utf-8"))
        detail = entry["apply"](data)
        json_path = W / f"{cid}_behavior.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif entry["target"] == "cases":
        data = json.loads((RUN / "hand_computed_cases.json").read_text(encoding="utf-8"))
        detail = entry["apply"](data)
        cases_path = W / f"{cid}_cases.json"
        cases_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out = W / f"{cid}_result.json"
    cmd = [sys.executable, "-B", str(SELFCHECK), "--json", str(json_path), "--doc", str(DOC),
           "--cases", str(cases_path), "--upstream", str(RUN / "upstream_bindings.json"),
           "--out", str(out), "--project-root", str(ROOT), "--evidence-dir", str(RUN)]
    cp = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                        errors="replace", check=False)
    (W / f"{cid}_stdout.txt").write_text(cp.stdout, encoding="utf-8")
    res = json.load(open(out, encoding="utf-8"))
    failed = [c["id"] for c in res["checks"] if c["status"] == "FAIL"]
    captured = (entry["expect_check"] in failed) if entry["expect_check"] else (not failed)
    mine.append({"case_id": cid, "injection": detail, "expected_exit": entry["expect_exit"],
                 "actual_exit": cp.returncode, "expected_check": entry["expect_check"],
                 "failed_checks": failed, "captured": captured, "selfcheck_status": res["status"]})

# 旧口径对照：r05 版自检脚本（git 1632761 blob，我用 cat-file 二进制提取的副本）
hist_script = ISO / "blobs/r05_verification_s6_g0_selfcheck.py"
out = W / "historical_model_check_result.json"
cmd = [sys.executable, "-B", str(hist_script), "--json", str(BEHAVIOR), "--doc", str(DOC),
       "--cases", str(RUN / "hand_computed_cases.json"), "--upstream", str(RUN / "upstream_bindings.json"),
       "--out", str(out), "--project-root", str(ROOT), "--evidence-dir", str(RUN)]
cp = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                    errors="replace", check=False)
(W / "historical_model_check_stdout.txt").write_text(cp.stdout, encoding="utf-8")
hres = json.load(open(out, encoding="utf-8"))
hfailed = [c["id"] for c in hres["checks"] if c["status"] == "FAIL"]
mine.append({"case_id": "historical_model_check", "actual_exit": cp.returncode,
             "expected_exit": 1, "expected_check": "C7", "failed_checks": hfailed,
             "captured": "C7" in hfailed, "verdict": "AS_EXPECTED" if (cp.returncode == 1 and "C7" in hfailed) else "UNEXPECTED"})

print("=== 我的复刻结果 vs 入库 probe_summary ===")
libmap = {r["case_id"]: r for r in lib["results"]}
print(f"{'case':<42}{'mine_exit':<10}{'lib_exit':<10}{'mine_failed':<16}{'lib_failed':<16}{'一致'}")
alldiff = 0
for r in mine:
    lr = libmap.get(r["case_id"])
    if lr is None:
        print(r["case_id"], "入库缺失"); alldiff += 1; continue
    ok = (r["actual_exit"] == lr["actual_exit"] and r["failed_checks"] == lr["failed_checks"])
    alldiff += 0 if ok else 1
    print(f"{r['case_id']:<42}{r['actual_exit']:<10}{lr['actual_exit']:<10}"
          f"{','.join(r['failed_checks']) or 'NONE':<16}{','.join(lr['failed_checks']) or 'NONE':<16}{ok}")
print("差异数 =", alldiff)
print()
print("入库 results 的 verdict:", [(r["case_id"], r["verdict"]) for r in lib["results"]])
print("我的 verdict:", [(r["case_id"], r["verdict"]) for r in mine])
print()
print("入库 historical c7_detail:", libmap["historical_model_check"].get("c7_detail"))
print("我的 historical C7 detail:",
      next((c["detail"] for c in hres["checks"] if c["id"] == "C7"), "")[:400])