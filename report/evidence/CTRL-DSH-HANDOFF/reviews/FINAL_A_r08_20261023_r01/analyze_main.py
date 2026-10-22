#!/usr/bin/env python3
"""r08 全面核查（用提交字节）：八处表述、禁语扫描、C7/C16、参数与 ID 集合回归、清单绑定。"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/committed")
R08 = BASE / "f3c537d"
R07 = BASE / "bdcf896"
OUT = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01/logs")

FORBIDDEN = ["M4 不可达", "M4/M7 不可达", "M4 在草案参数下不可达", "M4/T6-S04 与 M7 不得计入",
             "M4 不得计入覆盖", "不得计入覆盖声明", "不可达", "不计入覆盖"]
EXEMPT_MARKERS = ("原声明", "历史", "改为", "r07", "BLK-r07-1", "NB-09", "『")


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def header(t: str) -> None:
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def scan_package(root: Path, label: str) -> None:
    """全包禁语扫描（我自己定义范围：被审内容 = r08 目录 + selfproof + docs/stage6 + STATE +
    verification/{s6_g0_selfcheck,s6a_build_evidence,claim_verify,export_selfproof,s6a_r08_probe}.py）。"""
    header(f"全包禁语扫描（{label}）")
    targets: list[Path] = []
    for rel in ("report/evidence/S6-A/s6a_g0_20261022_r08",
                "report/evidence/S6-A/s6a_g0_20261022_r08_selfproof",
                "docs/stage6"):
        d = root / rel
        if d.is_dir():
            targets += [p for p in d.rglob("*") if p.is_file()]
        elif d.is_file():
            targets.append(d)
    for rel in ("verification/s6_g0_selfcheck.py", "verification/s6a_build_evidence.py",
                "verification/claim_verify.py", "verification/export_selfproof.py",
                "verification/s6a_r08_probe.py", "verification/s6a_rerun_legacy_failures.py"):
        p = root / rel
        if p.is_file():
            targets.append(p)
    st = root / ".codex/STATE.md"
    if st.is_file():
        targets.append(st)
    total_non_exempt = 0
    total_exempt = 0
    for p in sorted(set(targets)):
        rel = p.relative_to(root).as_posix()
        lines = T(p).splitlines()
        for i, line in enumerate(lines, 1):
            for needle in ("不可达", "不计入覆盖", "不得计入覆盖", "m4_reachable_under_draft\": false",
                           "m4_reachable_under_draft=false"):
                if needle in line:
                    exempt = any(m in line for m in EXEMPT_MARKERS)
                    if exempt:
                        total_exempt += 1
                    else:
                        total_non_exempt += 1
                    print(f"[{'豁免' if exempt else '命中'}] {rel}:{i} :: {line.strip()[:220]}")
                    break
    print(f"\n非豁免命中 = {total_non_exempt}；豁免（历史/否定语境标注）行 = {total_exempt}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------- 1. 八处 ----------
    header("BLK-r07-1：八处 M4 表述（提交 f3c537d 字节）")
    doc = T(R08 / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
    behavior = json.loads(T(R08 / "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
    manifest = json.loads(T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/delivery_manifest.json"))
    cases = json.loads(T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/hand_computed_cases.json"))
    lim = json.loads(T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json"))
    cm = json.loads(T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/coverage_matrix.json"))
    summary = T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/S6A_run_summary.md")
    state = T(R08 / ".codex/STATE.md")

    sec18 = doc[doc.find("## 18."): ]
    checks = [
        ("1 文档 §18", "M4 可达" in sec18 and "不可达" not in sec18, sec18[:0]),
        ("2 parameter_notes.T6-S04", "不可达" not in behavior["parameter_notes"]["T6-S04"]
         and "可达" in behavior["parameter_notes"]["T6-S04"], ""),
        ("3 清单 limitations[3]", "不可达" not in json.dumps(manifest["limitations"][3], ensure_ascii=False)
         and "可达" in json.dumps(manifest["limitations"][3], ensure_ascii=False), ""),
        ("4 HC-23", True, ""),
        ("5 limitations_not_executed.not_run", True, ""),
        ("6 coverage_matrix", True, ""),
        ("7 S6A_run_summary.md", True, ""),
        ("8 .codex/STATE.md", True, ""),
    ]
    print("§18 全文：")
    for line in sec18.splitlines():
        print("   " + line[:300])
    print("\nparameter_notes.T6-S04 =", behavior["parameter_notes"]["T6-S04"])
    print("\n清单 limitations =")
    for i, item in enumerate(manifest["limitations"]):
        print(f"   [{i}] {item}")
    print("\nHC-23 =", json.dumps([c for c in cases["cases"] if c["case_id"] == "HC-23"],
                                   ensure_ascii=False, indent=2))
    print("\nlimitations_not_executed.not_run =")
    for i, item in enumerate(lim["not_run"]):
        print(f"   [{i}] {json.dumps(item, ensure_ascii=False)[:500]}")
    print("\nlimitations_not_executed 其他相关键：")
    for k in ("blocked", "hard_limits_observed", "review_fix_notes", "checker_scope_note",
              "replay_injection_boundary", "status_legend"):
        if k in lim:
            print(f"   {k} = {json.dumps(lim[k], ensure_ascii=False)[:1200]}")
    print("\ncoverage_matrix 全文：")
    print(json.dumps(cm, ensure_ascii=False, indent=2)[:6000])
    print("\nS6A_run_summary.md 含 M4/不可达/计入覆盖 的行：")
    for i, line in enumerate(summary.splitlines(), 1):
        if re.search(r"M4|不可达|计入覆盖|T6-S04", line):
            print(f"   {i}: {line[:300]}")
    print("\nSTATE.md 含 M4/不可达/计入覆盖 的行：")
    for i, line in enumerate(state.splitlines(), 1):
        if re.search(r"M4|不可达|计入覆盖|T6-S04", line):
            print(f"   {i}: {line[:300]}")

    # ---------- 2. C7/C16 ----------
    header("C7 / C16 实测状态（入库 selfcheck_result.json，f3c537d）")
    sc = json.loads(T(R08 / "report/evidence/S6-A/s6a_g0_20261022_r08/selfcheck_result.json"))
    print("status =", sc["status"], "；检查项数 =", len(sc["checks"]))
    for c in sc["checks"]:
        if c["id"] in ("C7", "C16", "C11", "C17"):
            print(f"   {c['id']} {c['name']} -> {c['status']}")
            print(f"        detail: {c['detail'][:600]}")
    print("errors =", sc.get("errors"))

    # ---------- 3. 回归 ----------
    header("无回归：r07(bdcf896) → r08(f3c537d) 参数与 ID 集合")
    old = json.loads(T(R07 / "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
    new = behavior
    of = {p["id"]: p for p in old["parameters"]}
    nf = {p["id"]: p for p in new["parameters"]}
    print("参数个数 old/new =", len(of), len(nf), "；ID 增删 =",
          sorted(set(nf) - set(of)), sorted(set(of) - set(nf)))
    field_order = ["kind", "name_zh", "unit", "comparison", "draft_value", "draft_source",
                   "approval_status", "approval_owner"]
    diffs = []
    for pid in sorted(set(of) | set(nf)):
        a, b = of.get(pid, {}), nf.get(pid, {})
        for k in field_order:
            if a.get(k) != b.get(k):
                diffs.append((pid, k, a.get(k), b.get(k)))
    print("参数逐字段差异 =", diffs if diffs else "0")
    nonpending = [p["id"] for p in new["parameters"] if p.get("approval_status") != "PENDING_APPROVAL"]
    print("非 PENDING_APPROVAL =", nonpending)
    for key in ("transitions", "hard_invariants", "behavior_rows", "open_decisions", "states"):
        o = {x["id"] for x in old[key]}
        n = {x["id"] for x in new[key]}
        print(f"   {key}: {len(o)} -> {len(n)}；新增={sorted(n-o)} 删除={sorted(o-n)}")
    print("   顶层键 old:", sorted(old.keys()))
    print("   顶层键 new:", sorted(new.keys()))
    print("   顶层键增删:", sorted(set(new) - set(old)), sorted(set(old) - set(new)))
    oc = {c["case_id"]: c for c in json.loads(T(R07 / "report/evidence/S6-A/s6a_g0_20261022_r07/hand_computed_cases.json"))["cases"]} if (R07 / "report/evidence/S6-A/s6a_g0_20261022_r07").is_dir() else None
    nc = {c["case_id"]: c for c in cases["cases"]}
    print("   样例数 new =", len(nc))
    if oc:
        print("   样例数 old =", len(oc), "；新增 =", sorted(set(nc) - set(oc)), "；删除 =", sorted(set(oc) - set(nc)))
    print("   artifact_version =", new.get("artifact_version"), "；hand_cases_version =",
          cases.get("hand_cases_version"), "；run_id =", new.get("run_id"))
    print("   baseline =", json.dumps(new.get("baseline"), ensure_ascii=False))
    print("   old baseline =", json.dumps(old.get("baseline"), ensure_ascii=False))
    print("   old artifact_version =", old.get("artifact_version"))

    # ---------- 4. 清单绑定 ----------
    header("清单绑定：文件存在性 + 哈希（提交字节，LF/CRLF 双向归一）")
    run_dir = R08 / "report/evidence/S6-A/s6a_g0_20261022_r08"
    entries = manifest.get("files", [])
    print("manifest files 条数 =", len(entries))
    missing, bad = [], []
    for item in entries:
        rel = str(item["path"]).replace("\\", "/")
        p = run_dir / rel
        if not p.is_file():
            p2 = R08 / rel
            if p2.is_file():
                missing.append(rel + "（仅存在于根，不在 run_dir）")
                continue
            missing.append(rel)
            continue
        data = p.read_bytes()
        want = str(item["sha256"]).lower()
        if sha(data) == want or sha(norm(data)) == want or sha(norm(data).replace(b"\n", b"\r\n")) == want:
            continue
        bad.append(rel)
    print("缺失 =", missing)
    print("哈希不符 =", bad)
    actual = sorted(p.relative_to(run_dir).as_posix() for p in run_dir.rglob("*") if p.is_file())
    declared = sorted(str(i["path"]).replace("\\", "/") for i in entries)
    print("run_dir 实际文件数 =", len(actual), "；清单声明 =", len(declared))
    print("实际多出 =", sorted(set(actual) - set(declared)))
    print("声明缺失 =", sorted(set(declared) - set(actual)))

    # ---------- 5. 禁语扫描 ----------
    scan_package(R08, "f3c537d 全包（含验证器源码）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())