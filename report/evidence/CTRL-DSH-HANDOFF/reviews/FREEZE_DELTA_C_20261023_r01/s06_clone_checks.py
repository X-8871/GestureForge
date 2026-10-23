# 传输克隆内的四条硬条件核查（只写克隆 + tmp/review 目录）
import sys, os, json, subprocess
from pathlib import Path

ROOT = Path(r"D:\FPGA_Competition\tmp\review\FREEZE_DELTA_C_20261023_r01")
CLONE = ROOT / "clone"
PY = sys.executable
LOG = ROOT / "clone_checks.log"
logf = open(LOG, "a", encoding="utf-8")


def step(label, argv, cwd=CLONE):
    p = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    head = "\n".join(out.strip().splitlines()[:12])
    tail = "\n".join(out.strip().splitlines()[-8:])
    rec = (f"\n{'='*90}\n### {label}\n$ {' '.join(str(a) for a in argv)}\n[exit {p.returncode}]\n"
           f"--- head ---\n{head}\n--- tail ---\n{tail}\n")
    print(rec, flush=True)
    logf.write(rec)
    logf.flush()
    return p.returncode, out


R10 = "report/evidence/S6-A/s6a_g0_20261023_r10"
R05 = "report/evidence/S6-B/s6b_core_20261023_r05"
F4 = "6b8e5f2a23ce6f7dec41fc9992141b3423612081"
G4 = "f5b749ed1a49dc7e05238511d3b69d63bf3e9b8d"
F2 = "33b1fee30af1974560fa0b94bf6c6662d3e5d1e0"
F3 = "efb9f191c67fff307366f9552059ba7a5720b477"
OLD_F3 = "66f45dd47056261720f55abc7d661bafd8714970"

print("############ 0. 克隆基本信息 ############", flush=True)
for a in (["rev-parse", "HEAD"], ["status", "--short"], ["tag", "-l"], ["cat-file", "-t", OLD_F3]):
    rc, o, e = (lambda p: (p.returncode, p.stdout, p.stderr))(
        subprocess.run(["git"] + a, cwd=str(CLONE), capture_output=True, text=True, encoding="utf-8", errors="replace"))
    print(f"$ git {' '.join(a)}\n[exit {rc}]\n{o.strip()}{e.strip()}", flush=True)

print("\n############ 1. 克隆内 S6-A 新鲜自检两步（r10，原始工作区，未跑 claim_verify）############", flush=True)
step("fresh_selfcheck_twice r10", [PY, "-B", "verification/s6a_fresh_selfcheck_twice.py",
                                   "--project-root", str(CLONE), "--run-dir", R10,
                                   "--gap-seconds", "30",
                                   "--out", "tmp/6/fresh_selfcheck_pair_review.json"])

print("\n############ 2. claim_verify --package s6a / s6b（写入克隆 run-dir）############", flush=True)
rc_a, _ = step("claim_verify s6a", [PY, "-B", "verification/claim_verify.py", "--package", "s6a",
                                    "--run-dir", R10, "--project-root", str(CLONE)])
pa = CLONE / R10 / "claim_verification.json"
if pa.is_file():
    j = json.loads(pa.read_text(encoding="utf-8"))
    print(f"  -> r10 附录：verdict={j['verdict']} declared={j['claims_declared']} recorded={j['claims_recorded']} "
          f"count_ok={j['count_ok']} n={len(j['claims'])}", flush=True)
rc_b, _ = step("claim_verify s6b", [PY, "-B", "verification/claim_verify.py", "--package", "s6b",
                                    "--run-dir", R05, "--project-root", str(CLONE)])
pb = CLONE / R05 / "claim_verification.json"
if pb.is_file():
    j = json.loads(pb.read_text(encoding="utf-8"))
    print(f"  -> r05 附录：verdict={j['verdict']} declared={j['claims_declared']} recorded={j['claims_recorded']} "
          f"count_ok={j['count_ok']} n={len(j['claims'])}", flush=True)

print("\n############ 3. 必 FAIL 例：--simulate-defect count_mismatch / empty ############", flush=True)
for mode in ("count_mismatch", "empty"):
    rc, out = step(f"simulate-defect {mode}", [PY, "-B", "verification/claim_verify.py", "--package", "s6a",
                                               "--run-dir", R10, "--project-root", str(CLONE),
                                               "--simulate-defect", mode])
    j = json.loads((CLONE / R10 / "claim_verification.json").read_text(encoding="utf-8"))
    print(f"  -> mode={mode} exit={rc} verdict={j['verdict']} count_ok={j['count_ok']} "
          f"recorded={j['claims_recorded']} declared={j['claims_declared']}", flush=True)

print("\n############ 4. 硬条件②/③：export_selfproof --commit F4 / G4 ############", flush=True)
for label, args in [
    ("F4 (S6-A 剖面)", ["--commit", F4]),
    ("F4 (S6-B 剖面)", ["--commit", F4, "--s6b-run", R05]),
    ("G4 (S6-A 剖面)", ["--commit", G4]),
    ("G4 (S6-B 剖面)", ["--commit", G4, "--s6b-run", R05]),
    ("F2 (S6-A 剖面)", ["--commit", F2]),
    ("F2 (S6-B 剖面)", ["--commit", F2, "--s6b-run", R05]),
    ("F3 (S6-A 剖面)", ["--commit", F3]),
    ("F3 (S6-B 剖面)", ["--commit", F3, "--s6b-run", R05]),
    ("旧 F3 66f45dd（已 amend 掉，克隆内应不可解析）", ["--commit", OLD_F3]),
]:
    step(f"export_selfproof {label}", [PY, "-B", "verification/export_selfproof.py",
                                       "--project-root", str(CLONE)] + args)

logf.close()
print("\nDONE", flush=True)