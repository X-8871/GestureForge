"""S6-B r03 独立复跑套件（只在隔离副本内运行；不写 w6）。

用法：python -B run_suite.py <iso_root> <label>
- 先按清单声明的 SHA-256 做换行口径对齐（镜像 export_selfproof.align_by_manifest_hashes 的口径）
- 再跑驱动 / 探针 / 两个检查器 / claim_verify，记录真实退出码与耗时
- 产出 run_suite_<label>.json 与 run_suite_<label>.log
"""
from __future__ import annotations
import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ISO = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2] if len(sys.argv) > 2 else ISO.name
HERE = Path(__file__).resolve().parent
RUNREL = "report/evidence/S6-B/s6b_core_20261023_r03"
RUN = ISO / RUNREL
MAN = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
DECL = {i["path"]: i["sha256"] for i in MAN["files"]}

log_lines: list[str] = []
results: dict = {"label": LABEL, "iso": str(ISO)}


def log(msg: str) -> None:
    print(msg)
    log_lines.append(msg)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def align() -> dict:
    aligned, unresolved, kept = [], [], []
    for item in MAN["files"]:
        p = ISO / item["path"]
        if not p.is_file():
            unresolved.append(item["path"])
            continue
        want = item["sha256"]
        b = p.read_bytes()
        if sha(b) == want:
            kept.append(item["path"])
            continue
        lf = b.replace(b"\r\n", b"\n")
        crlf = lf.replace(b"\n", b"\r\n")
        if sha(lf) == want:
            p.write_bytes(lf)
            aligned.append(item["path"] + " -> LF")
        elif sha(crlf) == want:
            p.write_bytes(crlf)
            aligned.append(item["path"] + " -> CRLF")
        else:
            unresolved.append(item["path"])
    return {"aligned": aligned, "already_exact": len(kept), "unresolved": unresolved}


def run(cmd: list[str], timeout=900) -> dict:
    t0 = time.perf_counter()
    cp = subprocess.run(cmd, cwd=str(ISO), capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=timeout)
    dt = time.perf_counter() - t0
    return {"command": subprocess.list2cmdline(cmd), "exit_code": cp.returncode,
            "seconds": round(dt, 3), "stdout": cp.stdout, "stderr": cp.stderr}


# ---------------------------------------------------------------- 0) 对齐
a = align()
results["alignment"] = a
log(f"[align] exact={a['already_exact']} rewritten={len(a['aligned'])} unresolved={a['unresolved']}")
for x in a["aligned"]:
    log(f"         rewrite {x}")
if a["unresolved"]:
    log(f"         UNRESOLVED {a['unresolved']}")

PY = sys.executable
pristine = HERE / f"pristine_{LABEL}"
if pristine.exists():
    shutil.rmtree(pristine)
shutil.copytree(RUN, pristine)
log(f"[pristine] saved declared run dir -> {pristine}")

# ---------------------------------------------------------------- 1) 驱动（23/23）
drv = run([PY, "-B", str(ISO / "verification/s6b_run_cases.py"),
           "--project-root", str(ISO), "--run-dir", str(RUN)])
results["driver"] = drv
log(f"[driver] exit={drv['exit_code']} {drv['seconds']}s stdout={drv['stdout'].strip()}")
if drv["stderr"].strip():
    log(f"[driver] stderr={drv['stderr'].strip()[:400]}")

# 逐字节 vs 清单声明
byte_cmp = {"run_report.json": None, "logs": {}, "extra": []}
declared_ok = declared_bad = 0
for rel, want in list(DECL.items()):
    if not rel.startswith(RUNREL):
        continue
    local = ISO / rel
    if not local.is_file():
        continue
    got = sha(local.read_bytes())
    if got == want:
        declared_ok += 1
        byte_cmp["logs"][rel.split("/")[-1]] = "OK"
    else:
        declared_bad += 1
        byte_cmp["logs"][rel.split("/")[-1]] = f"MISMATCH got={got[:16]} want={want[:16]}"
results["declared_byte_compare"] = byte_cmp
log(f"[bytes] 全清单声明逐字节复核（运行后）：OK={declared_ok} MISMATCH={declared_bad}")
for k, v in byte_cmp["logs"].items():
    if v != "OK":
        log(f"         {k}: {v}")

# 与 pristine（声明口径）对比
diff_files = []
for p in sorted(pristine.rglob("*")):
    if not p.is_file():
        continue
    q = RUN / p.relative_to(pristine)
    if not q.is_file() or p.read_bytes() != q.read_bytes():
        diff_files.append(p.relative_to(pristine).as_posix())
results["diff_vs_pristine"] = diff_files
log(f"[diff] 运行后与声明口径副本不同的文件：{diff_files}")

# ---------------------------------------------------------------- 2) 探针
probe = run([PY, "-B", str(ISO / "verification/s6b_probe.py"),
             "--project-root", str(ISO), "--run-dir", str(RUN)])
results["probe"] = probe
log(f"[probe] exit={probe['exit_code']} {probe['seconds']}s stdout={probe['stdout'].strip()}")
ps = json.loads((RUN / "probe_summary.json").read_text(encoding="utf-8"))
results["probe_results"] = [(r["probe_id"], r["expected_exit"], r["actual_exit"], r["verdict"],
                            r["stdout_tail"][:120]) for r in ps["results"]]
for row in results["probe_results"]:
    log(f"        {row}")

# ---------------------------------------------------------------- 3) 两个检查器
inp = run([PY, "-B", str(ISO / "verification/check_stage_delivery.py"), "--mode", "inputs",
           "--manifest", str(RUN / "inputs_manifest.json"), "--project-root", str(ISO)])
evd = run([PY, "-B", str(ISO / "verification/check_stage_delivery.py"), "--mode", "evidence",
           "--manifest", str(RUN / "delivery_manifest.json"), "--project-root", str(ISO)])
results["check_inputs"] = inp
results["check_evidence"] = evd
log(f"[check inputs]   exit={inp['exit_code']} {inp['seconds']}s stdout={inp['stdout'].strip()[:300]}")
log(f"[check evidence] exit={evd['exit_code']} {evd['seconds']}s stdout={evd['stdout'].strip()[:600]}")

# ---------------------------------------------------------------- 4) claim_verify
cv = run([PY, "-B", str(ISO / "verification/claim_verify.py"), "--package", "s6b",
          "--run-dir", RUNREL, "--project-root", str(ISO)])
results["claim_verify"] = cv
log(f"[claim_verify] exit={cv['exit_code']} {cv['seconds']}s stdout={cv['stdout'].strip()}")
cvd = json.loads((RUN / "claim_verification.json").read_text(encoding="utf-8"))
old = json.loads((pristine / "claim_verification.json").read_text(encoding="utf-8"))
def strip(p):  # 去掉时间戳字段再比较
    q = json.loads(json.dumps(p))
    q.pop("generated_at_utc8", None)
    return q
results["claim_same_as_committed"] = strip(cvd) == strip(old)
results["claim_verdict"] = cvd["verdict"]
log(f"[claim_verify] verdict={cvd['verdict']} 与提交版一致(除生成时间)={results['claim_same_as_committed']}")
for c in cvd["claims"]:
    log(f"        {c['claim_id']}: {c['verdict']} exit={c['exit_code']}")

# ---------------------------------------------------------------- 5) 与提交版检查器输出比较
for name, got in (("inputs", inp), ("evidence", evd)):
    ref = (pristine / f"check_{name}_mode_output.txt").read_text(encoding="utf-8")
    same = got["stdout"].strip() == ref.strip()
    results[f"check_{name}_stdout_matches_committed"] = same
    log(f"[stdout] check {name} 与提交版逐字节(去尾空白)一致 = {same}")

(HERE / f"run_suite_{LABEL}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
(HERE / f"run_suite_{LABEL}.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
print(f"\n=== wrote run_suite_{LABEL}.json / .log ===")