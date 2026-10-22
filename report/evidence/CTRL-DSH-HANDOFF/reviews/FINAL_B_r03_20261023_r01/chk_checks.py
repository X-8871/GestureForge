"""补充核验：evidence 检查器在 e3aeb09 / 05126fd 两个提交内容上的真实结果。"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def align(iso: Path) -> dict:
    run = iso / RUNREL
    man = json.loads((run / "delivery_manifest.json").read_text(encoding="utf-8"))
    aligned, unresolved = [], []
    for item in man["files"]:
        p = iso / item["path"]
        if not p.is_file():
            unresolved.append(item["path"] + " (missing)")
            continue
        want = item["sha256"]
        b = p.read_bytes()
        if sha(b) == want:
            continue
        lf = b.replace(b"\r\n", b"\n")
        if sha(lf) == want:
            p.write_bytes(lf); aligned.append(item["path"] + " -> LF")
        elif sha(lf.replace(b"\n", b"\r\n")) == want:
            p.write_bytes(lf.replace(b"\n", b"\r\n")); aligned.append(item["path"] + " -> CRLF")
        else:
            unresolved.append(item["path"])
    return {"aligned": aligned, "unresolved": unresolved}


def run(iso: Path, mode: str) -> dict:
    run_dir = iso / RUNREL
    cmd = [sys.executable, "-B", str(iso / "verification/check_stage_delivery.py"),
           "--mode", mode, "--manifest", str(run_dir / ("inputs_manifest.json" if mode == "inputs"
                                                        else "delivery_manifest.json")),
           "--project-root", str(iso)]
    cp = subprocess.run(cmd, cwd=str(iso), capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    return {"exit": cp.returncode, "out": cp.stdout, "err": cp.stderr}


for label in ("clone_e3a", "clone_051"):
    iso = HERE / label
    print(f"\n===== {label} =====")
    a = align(iso)
    print("align rewritten:", a["aligned"])
    print("align unresolved:", a["unresolved"])
    for mode in ("inputs", "evidence"):
        r = run(iso, mode)
        try:
            payload = json.loads(r["out"])
            errs = payload.get("errors")
            print(f"-- {mode}: exit={r['exit']} status={payload.get('status')} errors={errs}")
        except Exception:
            print(f"-- {mode}: exit={r['exit']} raw={r['out'][:300]}")

# claim_verification 差异
print("\n===== claim_verification 差异（重跑 vs 提交口径） =====")
new = json.loads((HERE / "clone_e3a" / RUNREL / "claim_verification.json").read_text(encoding="utf-8"))
old = json.loads((HERE / "pristine_e3a_clone" / "claim_verification.json").read_text(encoding="utf-8"))
new.pop("generated_at_utc8", None); old.pop("generated_at_utc8", None)
for a, b in zip(old["claims"], new["claims"]):
    if a != b:
        print("DIFF claim", a["claim_id"])
        for k in a:
            if a[k] != b.get(k):
                print("   ", k, "\n      committed:", json.dumps(a[k], ensure_ascii=False)[:300],
                      "\n      rerun    :", json.dumps(b.get(k), ensure_ascii=False)[:300])
print("verdict:", old["verdict"], new["verdict"])