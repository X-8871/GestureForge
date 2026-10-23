#!/usr/bin/env python3
import json
import pathlib

root = pathlib.Path(r"D:\codex-worktrees\w6")
out = []
for rel in ("report/evidence/S6-B/s6b_core_20261023_r07/claim_verification.json",
            "report/evidence/S6-A/s6a_g0_20261023_r12/claim_verification.json"):
    d = json.loads((root / rel).read_text(encoding="utf-8"))
    out.append(f"=== {rel} ===")
    out.append("top keys: " + json.dumps(sorted(d.keys()), ensure_ascii=False))
    cl = d.get("claims") or d.get("results") or []
    out.append(f"n_claims={len(cl)}")
    for c in cl:
        cid = str(c.get("claim_id") or c.get("id") or "")
        if any(t in cid for t in ("C4", "C5", "C8")):
            slim = {k: v for k, v in c.items() if k not in ("stdout", "stderr", "command")}
            out.append(json.dumps(slim, ensure_ascii=False)[:1200])
    out.append("overall: " + json.dumps({k: v for k, v in d.items() if k not in ("claims", "results")},
                                       ensure_ascii=False)[:900])
    out.append("")
out.append("=== r12 limitations_not_executed.json ===")
lim = json.loads((root / "report/evidence/S6-A/s6a_g0_20261023_r12/limitations_not_executed.json").read_text(encoding="utf-8"))
out.append(json.dumps(lim, ensure_ascii=False, indent=1)[:6000])
out.append("")
out.append("=== r07 limitations_not_executed.json ===")
lim2 = json.loads((root / "report/evidence/S6-B/s6b_core_20261023_r07/limitations_not_executed.json").read_text(encoding="utf-8"))
out.append(json.dumps(lim2, ensure_ascii=False, indent=1)[:6000])
pathlib.Path(r"D:\FPGA_Competition\tmp\review\FREEZE_DELTA_E_20261023_r01\09_claims_and_limits.txt").write_text(
    "\n".join(out), encoding="utf-8")
print("ok", len(out))