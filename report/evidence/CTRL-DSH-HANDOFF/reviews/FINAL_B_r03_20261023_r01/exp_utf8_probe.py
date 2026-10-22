"""顺序实验（干净副本）：
  1) 干净克隆上只跑 evidence 检查器（判定 e3aeb09 的清单自洽性）
  2) 不设 PYTHONUTF8 直接跑探针，与提交字节比对（NB-07）
  3) 设 PYTHONUTF8=1 再跑一次，与提交字节比对
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, shutil
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ISO = (HERE / "clone_e3b").resolve()
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"
RUN = ISO / RUNREL
MAN = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
DECL = {i["path"]: i["sha256"] for i in MAN["files"]}
log: list[str] = []


def L(m):
    print(m); log.append(m)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def align():
    rewritten, unresolved = [], []
    for item in MAN["files"]:
        p = ISO / item["path"]
        if not p.is_file():
            unresolved.append(item["path"] + " (missing)"); continue
        want = item["sha256"]; b = p.read_bytes()
        if sha(b) == want:
            continue
        lf = b.replace(b"\r\n", b"\n")
        if sha(lf) == want:
            p.write_bytes(lf); rewritten.append(item["path"])
        elif sha(lf.replace(b"\n", b"\r\n")) == want:
            p.write_bytes(lf.replace(b"\n", b"\r\n")); rewritten.append(item["path"])
        else:
            unresolved.append(item["path"])
    return rewritten, unresolved


def run(cmd, env=None):
    cp = subprocess.run(cmd, cwd=str(ISO), capture_output=True, text=True, encoding="utf-8",
                        errors="replace", env=env)
    return cp


rw, un = align()
L(f"[align] rewritten={len(rw)} unresolved={un}")

# 1) 干净 evidence 检查
cp = run([sys.executable, "-B", str(ISO / "verification/check_stage_delivery.py"), "--mode", "evidence",
          "--manifest", str(RUN / "delivery_manifest.json"), "--project-root", str(ISO)])
L(f"[1] 干净 evidence 检查: exit={cp.returncode}")
try:
    payload = json.loads(cp.stdout)
    L("    status=" + str(payload["status"]))
    for e in payload["errors"]:
        L("    ERROR " + e)
except Exception:
    L("    raw=" + cp.stdout[:500])

# 2) 直接跑探针，不设 PYTHONUTF8
snap = {rel: (ISO / rel).read_bytes() for rel in DECL if rel.startswith(RUNREL)}
cp2 = run([sys.executable, "-B", str(ISO / "verification/s6b_probe.py"),
           "--project-root", str(ISO), "--run-dir", str(RUN)])
L(f"[2] 探针（无 PYTHONUTF8）: exit={cp2.returncode} stdout={cp2.stdout.strip()[:200]}")
diff2 = {}
for rel, want in DECL.items():
    if not rel.startswith(RUNREL):
        continue
    p = ISO / rel
    if sha(p.read_bytes()) != want:
        diff2[rel.split("/")[-1]] = (want[:16], sha(p.read_bytes())[:16])
L(f"    与提交清单声明不一致的文件：{json.dumps(diff2, ensure_ascii=False)}")
for name in ("probe_expected_tampered_stdout.txt", "probe_summary.json"):
    t = (RUN / name).read_text(encoding="utf-8", errors="replace")
    L(f"    {name}: U+FFFD 计数={t.count(chr(0xFFFD))}")

# 3) 设 PYTHONUTF8=1 重跑
env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
cp3 = run([sys.executable, "-B", str(ISO / "verification/s6b_probe.py"),
           "--project-root", str(ISO), "--run-dir", str(RUN)], env=env)
L(f"[3] 探针（PYTHONUTF8=1）: exit={cp3.returncode} stdout={cp3.stdout.strip()[:200]}")
diff3 = {}
for rel, want in DECL.items():
    if not rel.startswith(RUNREL):
        continue
    p = ISO / rel
    if sha(p.read_bytes()) != want:
        diff3[rel.split("/")[-1]] = (want[:16], sha(p.read_bytes())[:16])
L(f"    与提交清单声明不一致的文件：{json.dumps(diff3, ensure_ascii=False)}")

# 4) 直接跑驱动（无 PYTHONUTF8）看 run_report 是否逐字节
cp4 = run([sys.executable, "-B", str(ISO / "verification/s6b_run_cases.py"),
           "--project-root", str(ISO), "--run-dir", str(RUN)])
ok = sha((RUN / "run_report.json").read_bytes()) == DECL[f"{RUNREL}/run_report.json"]
L(f"[4] 驱动（无 PYTHONUTF8）exit={cp4.returncode} run_report 逐字节==声明: {ok}")

(HERE / "utf8_probe_sequence.log").write_text("\n".join(log) + "\n", encoding="utf-8")
print("wrote utf8_probe_sequence.log")