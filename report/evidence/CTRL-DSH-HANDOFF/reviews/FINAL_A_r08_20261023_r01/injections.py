#!/usr/bin/env python3
"""注入/反例实验：C16 禁语断言的判别力边界、claim_verify 的盲区、构建器中止行为。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

R = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01")
P = R / "parity"
RUN = P / "report/evidence/S6-A/s6a_g0_20261022_r08"
BK = R / "expbak"
BEHAVIOR = P / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
LIMITS = RUN / "limitations_not_executed.json"
COV = RUN / "coverage_matrix.json"
RESULT = RUN / "selfcheck_result.json"
STATE = P / ".codex/STATE.md"
LOGS = R / "logs"
PY = sys.executable

SHIPPED = "草案 500ms ≥ T6-L02 300ms，M4 不可达（U6-12）；本行不得计入覆盖声明。"
RESIDUAL_STYLE = "当前草案 T6-S04=500ms ≥ T6-L02=300ms，M4 被 M10 遮蔽、不可达；已登记 reachability 与 U6-12。"
COV_STYLE = "M4/M7 显式登记不可达，U6-12"
STATE_STYLE = "不可达项（不计入覆盖）：B16 S_DEDUP、M4/`T6-S04`（U6-12）、M7（构造上）"


def run(cmd: list[str], tag: str, timeout: int = 1800) -> dict:
    cp = subprocess.run(cmd, cwd=str(P), capture_output=True, text=True, encoding="utf-8",
                        errors="replace", check=False, timeout=timeout)
    print(f"\n### [{tag}] exit={cp.returncode}")
    print("    cmd:", subprocess.list2cmdline(cmd))
    out = (cp.stdout or "").strip().splitlines()
    err = (cp.stderr or "").strip().splitlines()
    for line in out[-12:]:
        print("    out:", line[:300])
    for line in err[-6:]:
        print("    err:", line[:300])
    return {"tag": tag, "exit": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}


def selfcheck(tag: str, manifest: bool = False, out: Path | None = None) -> dict:
    cmd = [PY, "-B", "verification/s6_g0_selfcheck.py",
           "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
           "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
           "--cases", str(RUN.relative_to(P) / "hand_computed_cases.json"),
           "--upstream", str(RUN.relative_to(P) / "upstream_bindings.json"),
           "--out", str(out or (R / "logs" / f"{tag}_result.json")),
           "--project-root", str(P), "--evidence-dir", str(RUN),
           "--state", ".codex/STATE.md"]
    if manifest:
        cmd += ["--manifest", str(RUN.relative_to(P) / "delivery_manifest.json")]
    res = run(cmd, tag)
    if out is not None and Path(out).is_file():
        data = json.loads(Path(out).read_text(encoding="utf-8"))
        c16 = next((c for c in data["checks"] if c["id"] == "C16"), None)
        print(f"    => status={data['status']}；C16={c16['status'] if c16 else 'MISSING'}；"
              f"detail={c16['detail'][:200] if c16 else ''}")
    return res


def claim_verify(tag: str) -> dict:
    return run([PY, "-B", "verification/claim_verify.py", "--package", "s6a",
                "--run-dir", str(RUN.relative_to(P)), "--project-root", str(P)], tag)


def restore() -> None:
    for src, dst in ((BK / "limitations_not_executed.json", LIMITS),
                     (BK / "coverage_matrix.json", COV),
                     (BK / "s6a_stage6_g0_behavior_v1.json", BEHAVIOR),
                     (BK / "STATE.md", STATE),
                     (BK / "selfcheck_result.json", RESULT)):
        if src.is_file():
            shutil.copy2(src, dst)
    print("\n[restore] 已从备份恢复被改文件")


def main() -> int:
    BK.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    for src in (LIMITS, COV, BEHAVIOR, STATE, RESULT):
        tgt = BK / src.name
        if src.is_file() and not tgt.is_file():
            shutil.copy2(src, tgt)
    print("=== 备份完成 ===", [p.name for p in sorted(BK.iterdir())])

    results = []

    # ---- T2a：C16 对「出厂探针字面量」的判别力（应 FAIL） ----
    print("\n" + "=" * 90 + "\nT2a C16 vs 出厂探针字面量（M4 不可达 / 不得计入覆盖声明）\n" + "=" * 90)
    d = json.loads(BEHAVIOR.read_text(encoding="utf-8"))
    d["parameter_notes"]["T6-S04"] = SHIPPED
    BEHAVIOR.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(selfcheck("T2a_shipped_literal", out=LOGS / "T2a_result.json"))
    restore()

    # ---- T2b：C16 对「包内实际残留措辞」的判别力（预期漏判） ----
    print("\n" + "=" * 90 + "\nT2b C16 vs 实际残留措辞（M4 被 M10 遮蔽、不可达）\n" + "=" * 90)
    d = json.loads(BEHAVIOR.read_text(encoding="utf-8"))
    d["parameter_notes"]["T6-S04"] = RESIDUAL_STYLE
    BEHAVIOR.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(selfcheck("T2b_residual_style", out=LOGS / "T2b_result.json"))
    restore()

    # ---- T3a：C16 是否扫描 limitations/coverage/STATE（预期不扫描） ----
    print("\n" + "=" * 90 + "\nT3a C16 vs 残留写进 limitations_not_executed.json（原样）\n" + "=" * 90)
    results.append(selfcheck("T3a_untouched_package", out=LOGS / "T3a_result.json"))
    print("\n--- T3a 附加：把阴性对照（字面量）写进 limitations ---")
    lim = json.loads(LIMITS.read_text(encoding="utf-8"))
    for item in lim["not_run"]:
        if "M4" in item.get("item", ""):
            item["reason"] = "已被注入：M4 不可达（U6-12）；其余同原文。"
    LIMITS.write_text(json.dumps(lim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(selfcheck("T3a2_literal_in_limits", out=LOGS / "T3a2_result.json"))
    restore()

    # ---- T3b：claim_verify 对残留写法的盲区 ----
    print("\n" + "=" * 90 + "\nT3b claim_verify 判别力\n" + "=" * 90)
    print("\n[1] 原样包（残留为『M4 被 M10 遮蔽、不可达』+ STATE『不可达项（不计入覆盖）』）")
    results.append(claim_verify("T3b1_pristine"))
    print("\n[2] 注入出厂字面量『M4 不可达』到 limitations（应 FAIL）")
    lim = json.loads(LIMITS.read_text(encoding="utf-8"))
    for item in lim["not_run"]:
        if "M4" in item.get("item", ""):
            item["reason"] = RESIDUAL_STYLE + "；M4 不可达（U6-12）"
    LIMITS.write_text(json.dumps(lim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(claim_verify("T3b2_literal_injected"))
    restore()
    print("\n[3] 注入 coverage_matrix 风格『M4/M7 显式登记不可达』（应漏判）")
    cov = json.loads(COV.read_text(encoding="utf-8"))
    cov["review_fix_coverage"].append({"issue": "INJECTED-X", "location": COV_STYLE, "status": "OPEN"})
    COV.write_text(json.dumps(cov, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(claim_verify("T3b3_cov_style"))
    restore()
    print("\n[4] STATE 风格行（与包内 STATE L61 同形）——直接看是否已被漏判（不注入，读原包）")
    print("    STATE L61 原文是否在扫描范围内：是（claim_verify 扫描 .codex/STATE.md）")
    for i, ln in enumerate(STATE.read_text(encoding="utf-8").splitlines(), 1):
        if STATE_STYLE.split("：")[0] in ln:
            print(f"    L{i}: {ln.strip()[:200]}")

    # ---- T5：构建器在「已有 selfcheck_result.json」且声明失败时是否中止 ----
    print("\n" + "=" * 90 + "\nT5 构建器在声明失败时是否中止（已有 selfcheck_result.json）\n" + "=" * 90)
    RESULTS_BACKUP = BK / "selfcheck_result.json"
    if RESULTS_BACKUP.is_file():
        shutil.copy2(RESULTS_BACKUP, RESULT)
    lim = json.loads(LIMITS.read_text(encoding="utf-8"))
    for item in lim["not_run"]:
        if "M4" in item.get("item", ""):
            item["reason"] = "注入未验证声明：M4 不可达（U6-12）。"
    LIMITS.write_text(json.dumps(lim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    results.append(claim_verify("T5_claim_verify_should_fail"))
    results.append(run([PY, "-B", "verification/s6a_build_evidence.py",
                        "--run-dir", str(RUN.relative_to(P)), "--project-root", str(P)],
                       "T5_builder_should_abort"))
    restore()
    shutil.copy2(RESULTS_BACKUP, RESULT)

    # ---- T6：首版构建（无 selfcheck_result.json）时是否仍会中止 ----
    print("\n" + "=" * 90 + "\nT6 首版构建（无 selfcheck_result.json）+ 未验证声明\n" + "=" * 90)
    if RESULT.is_file():
        RESULT.unlink()
        print("    已删除 selfcheck_result.json（模拟首版构建）")
    lim = json.loads(LIMITS.read_text(encoding="utf-8"))
    for item in lim["not_run"]:
        if "M4" in item.get("item", ""):
            item["reason"] = "注入未验证声明：M4 不可达（U6-12）。"
    LIMITS.write_text(json.dumps(lim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    r6 = run([PY, "-B", "verification/s6a_build_evidence.py",
              "--run-dir", str(RUN.relative_to(P)), "--project-root", str(P)],
             "T6_builder_first_build")
    results.append(r6)
    cvt = RUN / "claim_verification.json"
    if cvt.is_file():
        cv = json.loads(cvt.read_text(encoding="utf-8"))
        print(f"    => 构建结束后入库 claim_verification.json verdict = {cv['verdict']}")
        print(f"       claims = {[(c['claim_id'], c['verdict']) for c in cv['claims']]}")
    dm = json.loads((RUN / "delivery_manifest.json").read_text(encoding="utf-8"))
    print(f"    => 构建结束后入库清单 checks = "
          f"{[(c['name'][:40], c['status'], c['exit_code']) for c in dm['checks']]}")

    print("\n\n=== 汇总 ===")
    for r in results:
        print(f"  {r['tag']}: exit={r['exit']}")
    restore()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())