#!/usr/bin/env python3
# 只读检查脚本 7：汇总注入/历史模型运行的 exit code 与失败检查项
import json, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = r"D:\FPGA_Competition\tmp\review\S6A_r06_20261023_r01\runs"
FULL = {
  "ext_cases": 0, "inj_hc31_old": 1, "inj_hc31_later_false": 1, "inj_hc31_count_only_true": 1,
  "inj_hc31_removed": 1, "inj_hc29_later_true": 1, "hist_r05_selfcheck": 1,
  "inj_anchor_old": None, "inj_m3_no_later": None, "inj_b07_fixed": None, "inj_b07_b27_fixed": None,
}
print("(exit code 取自 runs_inject.txt 的 exit=NN；这里读结果文件与 stdout)")
for tag in FULL:
    rp = os.path.join(W, tag + "_result.json")
    sp = os.path.join(W, tag + "_stdout.txt")
    if not os.path.exists(rp):
        print(f"{tag}: 无结果文件；stdout 尾部:")
        if os.path.exists(sp):
            print("   " + open(sp, encoding="utf-8", errors="replace").read().strip()[-400:].replace("\n", "\n   "))
        continue
    d = json.load(open(rp, encoding="utf-8"))
    failed = [(c["id"], c["status"]) for c in d["checks"] if c["status"] == "FAIL"]
    c7 = next((c["detail"] for c in d["checks"] if c["id"] == "C7"), "")
    c1 = next((c["detail"] for c in d["checks"] if c["id"] == "C1"), "")
    print(f"{tag}: status={d['status']} FAILED={[f[0] for f in failed]}")
    print(f"   C7={c7[:260]}")
    if c1 and c1 != "identity ok":
        print(f"   C1={c1[:200]}")
print()
print("stdout 首行（各例）:")
for tag in FULL:
    sp = os.path.join(W, tag + "_stdout.txt")
    if os.path.exists(sp):
        txt = open(sp, encoding="utf-8", errors="replace").read().strip().splitlines()
        print(f"{tag}: {txt[0][:200] if txt else '(空)'}")