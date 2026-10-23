"""评审自查：汇总 item1/item2 的 JSON 与 stdout 关键字段（只读）。"""
import glob
import json
import os

R = r"D:\FPGA_Competition\tmp\review\S3_T17_QFIX_20261023_r01\cmd"
for p in sorted(glob.glob(os.path.join(R, "**", "*.json"), recursive=True)):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"[unreadable] {p}: {exc}")
        continue
    rel = os.path.relpath(p, R)
    if isinstance(d, dict):
        keep = {}
        for k in ("verdict", "exit_code", "conclusion", "commit", "core_autocrlf", "files_checked",
                  "mismatch_count", "not_in_commit", "crlf_files_in_worktree", "status",
                  "counts", "head", "branch", "reason"):
            if k in d:
                keep[k] = d[k]
        if "results" in d:
            keep["results_matched"] = [r.get("matched") for r in d["results"]]
        if "cli_regressions" in d:
            keep["cli"] = [(c["name"], c["expected_exit_code"], c["actual_exit_code"],
                            c["json_written"], c["matched"]) for c in d["cli_regressions"]]
        if "checks" in d and isinstance(d["checks"], dict):
            ck = d["checks"]
            keep["checks"] = {k: (v.get("pass") if isinstance(v, dict) else v) for k, v in ck.items()}
        if "checks" in d and isinstance(d["checks"], list):
            keep["checks"] = [(c["id"], c["status"]) for c in d["checks"]]
        print(f"--- {rel}\n    {json.dumps(keep, ensure_ascii=False)[:1400]}")
print("\n=== item1 05 check_t17_preflight detail ===")
p = os.path.join(R, "item1", "05_check_preflight.json")
d = json.load(open(p, encoding="utf-8"))
print(json.dumps({k: v for k, v in d.items() if k not in ("checks",)}, ensure_ascii=False)[:1200])
print(json.dumps(d.get("checks"), ensure_ascii=False, indent=1)[:2500])
print("\n=== item1 07 handoff (as-is) ===")
s = open(os.path.join(R, "item1", "07_handoff_dbdf_asIs.stdout.txt"), encoding="utf-8", errors="replace").read()
for line in s.splitlines():
    if line.startswith("[") or line.startswith("结论") or line.startswith("退出码") or "FAIL" in line:
        print(line[:400])