#!/usr/bin/env python3
"""用 r06（04ea58e1）版自检脚本的 recompute，直接观察旧口径对 HC-31/HC-32 的报值。"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W6 = r"D:\codex-worktrees\w6"
OUT = Path(r"D:\FPGA_Competition\tmp\review\S6A_r07_20261023_r01")
blob = subprocess.run(["git", "-C", W6, "cat-file", "blob",
                       "04ea58e1:verification/s6_g0_selfcheck.py"], capture_output=True).stdout
(OUT / "r06_selfcheck.py").write_bytes(blob)
spec = importlib.util.spec_from_file_location("r06", OUT / "r06_selfcheck.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cases = json.loads(subprocess.run(["git", "-C", W6, "cat-file", "blob",
                                  "bdcf896:report/evidence/S6-A/s6a_g0_20261022_r07/hand_computed_cases.json"],
                                 capture_output=True).stdout.decode("utf-8"))
by = {c["case_id"]: c for c in cases["cases"]}
keys = ("completion_index", "window_span_ms", "m3_fires", "later_of_applied",
        "m3_fires_count_only", "sequence_span_ms")
for cid in ("HC-31", "HC-32"):
    out = m.recompute(by[cid])
    print(f"r06 旧实现 recompute {cid}: ", {k: out.get(k) for k in keys})
    print(f"r07 新 expected     {cid}: ", {k: by[cid]["expected"].get(k) for k in keys})