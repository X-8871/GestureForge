#!/usr/bin/env python3
"""第二轮注入实验：
  P1 claim_verify 的路径敏感（绝对路径含 tmp 组件 → 全量跳过 → 假 PASS）实证
  P2 claim_verify 的 needle 判别力（去掉路径守卫后的忠实复算）
  T5 构建器在「已有 selfcheck_result.json 且声明失败」时是否中止
  T6 首版构建（无 selfcheck_result.json）时是否仍会中止
"""
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
LIMITS = RUN / "limitations_not_executed.json"
RESULT = RUN / "selfcheck_result.json"
LOGS = R / "logs"
PY = sys.executable

NEEDLES = ["M4 不可达", "M4/M7 不可达", "不得计入覆盖", "m4_reachable_under_draft\": false",
           "m4_reachable_under_draft=false", "M4 在草案参数下不可达"]
MARKERS = ("原声明", "历史", "改为", "r07", "BLK-r07-1", "NB-09", "『")
SCAN_NAMES = ("coverage_matrix.json", "limitations_not_executed.json", "fix_record.json", "fix_record.md",
              "S6A_run_summary.md", "delivery_manifest.json", "hand_computed_cases.json")


def sh(cmd: list[str], tag: str) -> dict:
    cp = subprocess.run(cmd, cwd=str(P), capture_output=True, text=True, encoding="utf-8",
                        errors="replace", check=False)
    print(f"\n### [{tag}] exit={cp.returncode}")
    for line in (cp.stdout or "").strip().splitlines()[-4:]:
        print("    out:", line[:400])
    for line in (cp.stderr or "").strip().splitlines()[-3:]:
        print("    err:", line[:300])
    return {"tag": tag, "exit": cp.returncode, "stdout": cp.stdout}


def claim_verify(tag: str) -> dict:
    return sh([PY, "-B", "verification/claim_verify.py", "--package", "s6a",
               "--run-dir", str(RUN.relative_to(P)), "--project-root", str(P)], tag)


def builder(tag: str) -> dict:
    return sh([PY, "-B", "verification/s6a_build_evidence.py",
               "--run-dir", str(RUN.relative_to(P)), "--project-root", str(P)], tag)


def restore() -> None:
    for name in ("limitations_not_executed.json", "coverage_matrix.json"):
        src = BK / name
        if src.is_file():
            shutil.copy2(src, RUN / name)
    if (BK / "selfcheck_result.json").is_file():
        shutil.copy2(BK / "selfcheck_result.json", RESULT)


def main() -> int:
    BK.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)

    # ---------- P1：claim_verify 的绝对路径守卫实证 ----------
    print("=" * 92)
    print("P1 claim_verify 扫描路径守卫（绝对路径含 'tmp' 组件即整文件跳过）")
    print("=" * 92)
    print("project_root =", P)
    print("含 'tmp' 组件？", "tmp" in P.parts, "->", [x for x in P.parts if x in ('logs', 'tmp')])
    # 注入出厂字面量到 limitations_not_executed.json
    lim = json.loads(LIMITS.read_text(encoding="utf-8"))
    for item in lim["not_run"]:
        if "M4" in item.get("item", ""):
            item["reason"] = "注入阴性对照：M4 不可达（U6-12）。"
    LIMITS.write_text(json.dumps(lim, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    r = claim_verify("P1_tool_with_literal_injected")
    text = LIMITS.read_text(encoding="utf-8")
    lines = [(i, ln) for i, ln in enumerate(text.splitlines(), 1) if "M4 不可达" in ln]
    print("    注入后 limitations_not_executed.json 命中行：", lines)
    # 忠实复算：完全照抄 claim_verify.verify_s6a 的循环，只额外记录"因路径守卫被跳过"
    hits, skipped = [], {}
    for name in SCAN_NAMES:
        cand = RUN / name
        if not cand.is_file():
            continue
        try:
            txt = cand.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if any(part in ("logs", "tmp") for part in cand.parts):
            skipped[str(cand)] = "绝对路径含 logs/tmp 组件 → 跳过"
            continue
        for lineno, line in enumerate(txt.splitlines(), 1):
            if any(m in line for m in MARKERS):
                continue
            for needle in NEEDLES:
                if needle in line:
                    hits.append(f"{name}:{lineno} [{needle}]")
    print("    工具实测 verdict/exit:", r["exit"], "(扫描集为空 → C1 平凡通过)")
    print("    因绝对路径守卫被整体跳过的文件数：", len(skipped))
    print("    去掉路径守卫后的命中：", hits)
    print("    => 结论：路径守卫使 claim_verify 在本评审目录下**完全不扫描**；needle 集合本身对")
    print("       『M4 不可达』这类字面量是有判别力的，但对『M4 被 M10 遮蔽、不可达』/")
    print("       『M4/M7 显式登记不可达』/『不可达项（不计入覆盖）…M4/T6-S04』无判别力。")
    restore()

    # needle 判别力的字符级证明
    print("\n" + "-" * 92)
    print("P2 needle 逐条对包内三条真实残留行的匹配结果（纯字符串判定）")
    print("-" * 92)
    residuals = {
        "limitations_not_executed.json not_run[7].reason": "当前草案 T6-S04=500ms ≥ T6-L02=300ms，M4 被 M10 遮蔽、不可达；已登记 reachability 与 U6-12。",
        "coverage_matrix.json item4.status": "DONE_WITH_PREDICATE_BINDING（…；M4/M7 显式登记不可达，U6-12）",
        ".codex/STATE.md L61": "不可达项（不计入覆盖）：B16 `S_DEDUP`（…）、M4/`T6-S04`（U6-12）、M7（构造上）；见 `reachability_notes.json`。",
        "[对照]出厂探针字面量": "草案 500ms ≥ T6-L02 300ms，M4 不可达（U6-12）；本行不得计入覆盖声明。",
    }
    for label, line in residuals.items():
        m = [n for n in NEEDLES if n in line]
        print(f"    {label}: needle 命中 = {m if m else '无（漏判）'}")

    # ---------- T5：声明失败 + 已有 selfcheck_result.json → 必须中止 ----------
    print("\n" + "=" * 92)
    print("T5 构建器：声明未通过 + run_dir 已有 selfcheck_result.json → 应中止")
    print("=" * 92)
    sc = json.loads((BK / "selfcheck_result.json").read_text(encoding="utf-8"))
    for c in sc["checks"]:
        if c["id"] == "C16":
            c["status"] = "FAIL"
            c["detail"] = "（合成状态：模拟自检结果中 C16 未通过，用于验证构建器中止路径）"
    sc["status"] = "FAILED"
    RESULT.write_text(json.dumps(sc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("    已把 selfcheck_result.json 的 C16 改判 FAIL（合成状态，文件存在）")
    claim_verify("T5_claim_verify_expected_fail")
    builder("T5_builder_expected_abort")

    # ---------- T6：首版构建（无 selfcheck_result.json）----------
    print("\n" + "=" * 92)
    print("T6 构建器：首版构建（删除 selfcheck_result.json）→ 是否仍中止")
    print("=" * 92)
    RESULT.unlink()
    print("    已删除 selfcheck_result.json（模拟新 RunId 首版构建）")
    claim_verify("T6_claim_verify_expected_fail")
    builder("T6_builder_first_build")
    cvp = RUN / "claim_verification.json"
    if cvp.is_file():
        cv = json.loads(cvp.read_text(encoding="utf-8"))
        print(f"    => 构建结束后 run_dir/claim_verification.json verdict = {cv['verdict']}")
        print(f"       claims = {[(c['claim_id'], c['verdict'], c['exit_code']) for c in cv['claims']]}")
    dmp = RUN / "delivery_manifest.json"
    dm = json.loads(dmp.read_text(encoding="utf-8"))
    print(f"    => 构建结束后清单 checks = {[(c['status'], c['exit_code']) for c in dm['checks']]}")
    print(f"    => 清单是否引用 claim_verification 的判定：",
          any("claim" in json.dumps(c).lower() for c in dm["checks"]))
    restore()
    print("\n[restore] 完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())