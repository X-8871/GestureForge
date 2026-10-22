#!/usr/bin/env python3
"""逐项核查：8 处残留、N-r07-3..6、ID 集合、复跑比对。"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASE = Path(r"D:/FPGA_Competition/tmp/review/FINAL_A_20261023_r01")
R08 = BASE / "committed/f3c537d"
R07 = BASE / "committed/bdcf896"
RUN8 = R08 / "report/evidence/S6-A/s6a_g0_20261022_r08"
RUN7 = R07 / "report/evidence/S6-A/s6a_g0_20261022_r07"
RERUN = BASE / "rerun"


def T(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def h(t: str) -> None:
    print("\n" + "=" * 92)
    print(t)
    print("=" * 92)


def norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def main() -> int:
    # ---------------- 1. 八处精确核查 ----------------
    h("1. BLK-r07-1：八处逐处精确核查（r07 提交字节 vs r08 提交字节）")
    places = {
        "1 docs/stage6/s6a_stage6_g0_behavior_v1.json :: parameter_notes.T6-S04":
            ("docs/stage6/s6a_stage6_g0_behavior_v1.json", "json", "parameter_notes", "T6-S04"),
        "2 r08/delivery_manifest.json :: limitations[3]":
            ("report/evidence/S6-A/s6a_g0_20261022_r08/delivery_manifest.json", "json_list", "limitations", 3),
        "3 r08/hand_computed_cases.json :: HC-23":
            ("report/evidence/S6-A/s6a_g0_20261022_r08/hand_computed_cases.json", "hc23", None, None),
        "4 r08/limitations_not_executed.json :: not_run":
            ("report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json", "notrun", None, None),
        "5 r08/coverage_matrix.json :: item4 status":
            ("report/evidence/S6-A/s6a_g0_20261022_r08/coverage_matrix.json", "covitem4", None, None),
        "6 r08/S6A_run_summary.md":
            ("report/evidence/S6-A/s6a_g0_20261022_r08/S6A_run_summary.md", "M4line", None, None),
        "7 docs/stage6/S6A_stage6_g0_behavior_spec_v1.md :: §18":
            ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "sec18", None, None),
        "8 .codex/STATE.md :: 不可达项（不计入覆盖）":
            (".codex/STATE.md", "M4line", None, None),
    }
    # 语义判定：断言「M4 不可达」或「M4/T6-S04 不计入覆盖」
    def asserts_m4_bad(txt: str) -> list[tuple[int, str]]:
        out = []
        for i, ln in enumerate(txt.splitlines(), 1):
            bad = False
            if re.search(r"M4[^。\n]{0,20}不可达", ln) and "不构成不可达" not in ln:
                bad = True
            if re.search(r"不可达项（不计入覆盖）", ln) and "M4" in ln:
                bad = True
            if re.search(r"M4[^。\n]{0,10}显式登记不可达", ln):
                bad = True
            if bad:
                out.append((i, ln.strip()))
        return out

    verdicts = {}
    for label, (rel, kind, a, b) in places.items():
        text8 = T(R08 / rel)
        hits = asserts_m4_bad(text8)
        print(f"\n--- {label}")
        if kind == "json":
            print("    r08 值:", json.loads(text8)[a][b])
        elif kind == "json_list":
            print("    r08 值:", json.loads(text8)[a][b])
        elif kind == "hc23":
            c = json.loads(text8)
            print("    r08 HC-23.expected:", json.dumps([x for x in c["cases"] if x["case_id"] == "HC-23"][0]["expected"], ensure_ascii=False))
        elif kind == "notrun":
            d = json.loads(text8)["not_run"]
            for i, it in enumerate(d):
                if "M4" in json.dumps(it, ensure_ascii=False):
                    print(f"    r08 not_run[{i}]:", json.dumps(it, ensure_ascii=False)[:400])
        elif kind == "covitem4":
            for it in json.loads(text8)["runbook_coverage"]:
                if it["item"] == 4:
                    print("    r08 item4.status:", it["status"])
                    print("    r08 item4.location:", it["location"])
        else:
            for i, ln in hits:
                print(f"    r08 L{i}: {ln[:260]}")
        verdicts[label] = hits
    print("\n>>> 仍断言『M4 不可达 / M4 不计入覆盖』的处数：",
          sorted(k for k, v in verdicts.items() if v))

    h("1b. r07 → r08 相关文件差异（得出改动范围）")
    rels = ["docs/stage6/s6a_stage6_g0_behavior_v1.json",
            "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
            ".codex/STATE.md",
            "report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json",
            "report/evidence/S6-A/s6a_g0_20261022_r08/coverage_matrix.json",
            "report/evidence/S6-A/s6a_g0_20261022_r08/S6A_run_summary.md"]
    mapping = {
        "report/evidence/S6-A/s6a_g0_20261022_r08/limitations_not_executed.json":
            "report/evidence/S6-A/s6a_g0_20261022_r07/limitations_not_executed.json",
        "report/evidence/S6-A/s6a_g0_20261022_r08/coverage_matrix.json":
            "report/evidence/S6-A/s6a_g0_20261022_r07/coverage_matrix.json",
        "report/evidence/S6-A/s6a_g0_20261022_r08/S6A_run_summary.md":
            "report/evidence/S6-A/s6a_g0_20261022_r07/S6A_run_summary.md",
    }
    for rel in rels:
        rel7 = mapping.get(rel, rel)
        print(f"\n--- {rel}")
        try:
            a, b = json.loads(T(R07 / rel7)), json.loads(T(R08 / rel))
            keys = {"limitations_not_executed.json": None}.get(Path(rel).name)
        except Exception:
            a = T(R07 / rel7); b = T(R08 / rel)
            keys = None
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if json.dumps(a.get(k), ensure_ascii=False, sort_keys=True) != json.dumps(b.get(k), ensure_ascii=False, sort_keys=True):
                    print(f"    键 {k} 有变：")
                    print(f"       r07: {json.dumps(a.get(k), ensure_ascii=False)[:400]}")
                    print(f"       r08: {json.dumps(b.get(k), ensure_ascii=False)[:400]}")
        elif isinstance(a, str) and isinstance(b, str):
            la, lb = set(a.splitlines()), set(b.splitlines())
            for ln in sorted(x for x in lb - la if re.search(r"M4|不可达|计入覆盖|v1\.[0-9]|29", x)):
                print(f"     r08 新增行: {ln.strip()[:300]}")
            for ln in sorted(x for x in la - lb if re.search(r"M4|不可达|计入覆盖|v1\.[0-9]|29", x)):
                print(f"     r07 删除行: {ln.strip()[:300]}")

    # ---------------- 2. N-r07-3 ----------------
    h("2. N-r07-3（F2）：修订基线三处口径")
    m8 = json.loads(T(RUN8 / "delivery_manifest.json"))
    j8 = json.loads(T(R08 / "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
    print("   r08 delivery_manifest.source_commit =", m8.get("source_commit"))
    print("   r08 limitations[0] 相关:", [x for x in m8["limitations"] if "source_commit" in x])
    print("   r08 JSON baseline =", json.dumps(j8.get("baseline"), ensure_ascii=False))
    st = T(R08 / ".codex/STATE.md")
    for i, ln in enumerate(st.splitlines(), 1):
        if "修订基线" in ln or "起始提交" in ln:
            print(f"   STATE L{i}: {ln.strip()[:400]}")
    for i, ln in enumerate(st.splitlines(), 1):
        if "source_commit" in ln:
            print(f"   STATE L{i}(source_commit): {ln.strip()[:300]}")
    m7 = json.loads(T(RUN7 / "delivery_manifest.json"))
    j7 = json.loads(T(R07 / "docs/stage6/s6a_stage6_g0_behavior_v1.json"))
    print("   [r07 对照] manifest.source_commit =", m7.get("source_commit"),
          "; JSON baseline =", json.dumps(j7.get("baseline"), ensure_ascii=False))

    # ---------------- 3. N-r07-4 ----------------
    h("3. N-r07-4（F4）：keep_reason 归因数值")
    for name in ("delivery_manifest.json", "fix_record.json", "selfcheck_r04_failure.json"):
        p = RUN8 / name
        txt = T(p)
        for i, ln in enumerate(txt.splitlines(), 1):
            if "29" in ln and ("30" in ln or "32" in ln or "样例" in ln or "不足" in ln):
                print(f"   r08 {name}:{i}: {ln.strip()[:320]}")
    print("   --- 含 '29<30' / '29 < 30' 的行 ---")
    for name in ("delivery_manifest.json", "fix_record.json", "fix_record.md", "S6A_run_summary.md",
                 "limitations_not_executed.json", "coverage_matrix.json"):
        for i, ln in enumerate(T(RUN8 / name).splitlines(), 1):
            if re.search(r"29\s*<\s*30", ln):
                print(f"   [命中] r08 {name}:{i}: {ln.strip()[:320]}")

    # ---------------- 4. N-r07-5 ----------------
    h("4. N-r07-5（F5）：STATE 陈旧行")
    for i, ln in enumerate(st.splitlines(), 1):
        if re.search(r"v1\.4\s*/\s*r05|本轮已完成|证据入口|PENDING_REVIEW|v1\.6|v1\.5", ln):
            print(f"   STATE L{i}: {ln.strip()[:280]}")

    # ---------------- 5. N-r07-6 ----------------
    h("5. N-r07-6（F11）：v1.5 令牌残留（非历史语境）")
    for name in ("coverage_matrix.json", "limitations_not_executed.json", "delivery_manifest.json",
                 "S6A_run_summary.md", "fix_record.json", "fix_record.md", "hand_computed_cases.json"):
        for i, ln in enumerate(T(RUN8 / name).splitlines(), 1):
            for m in re.finditer(r"v1\.\d", ln):
                if m.group(0) != "v1.7":
                    print(f"   r08 {name}:{i} [{m.group(0)}]: {ln.strip()[:220]}")

    # ---------------- 6. ID 集合与样例 ----------------
    h("6. 回归：ID 集合 / 样例数 / 版本")
    for key in ("transitions", "hard_invariants", "behavior_rows", "open_decisions"):
        o = {x["id"] for x in j7[key]}
        n = {x["id"] for x in j8[key]}
        print(f"   {key}: {len(o)} -> {len(n)}；新增={sorted(n-o)} 删除={sorted(o-n)}")
    so = {x for x in j7["states"]}
    sn = {x for x in j8["states"]}
    print("   states(old dict keys):", len(so), "->", len(sn), "；symdiff =", sorted(so ^ sn))
    print("   顶层键增删:", sorted(set(j8) - set(j7)), sorted(set(j7) - set(j8)))
    c7 = json.loads(T(RUN7 / "hand_computed_cases.json"))["cases"]
    c8 = json.loads(T(RUN8 / "hand_computed_cases.json"))["cases"]
    o8 = {x["case_id"]: x for x in c8}
    o7 = {x["case_id"]: x for x in c7}
    print("   样例数:", len(o7), "->", len(o8), "；新增 =", sorted(set(o8) - set(o7)),
          "；删除 =", sorted(set(o7) - set(o8)))
    changed = []
    for cid in sorted(set(o7) & set(o8)):
        if json.dumps(o7[cid], ensure_ascii=False, sort_keys=True) != json.dumps(o8[cid], ensure_ascii=False, sort_keys=True):
            changed.append(cid)
    print("   内容有变的样例:", changed)
    for cid in changed:
        a, b = o7[cid], o8[cid]
        for k in set(a) | set(b):
            if json.dumps(a.get(k), ensure_ascii=False, sort_keys=True) != json.dumps(b.get(k), ensure_ascii=False, sort_keys=True):
                print(f"      {cid}.{k}: old={json.dumps(a.get(k),ensure_ascii=False)[:200]}")
                print(f"      {cid}.{k}: new={json.dumps(b.get(k),ensure_ascii=False)[:200]}")
    print("   artifact_version:", j7.get("artifact_version"), "->", j8.get("artifact_version"))
    print("   hand_cases_version:", json.loads(T(RUN7/"hand_computed_cases.json")).get("hand_cases_version"),
          "->", json.loads(T(RUN8/"hand_computed_cases.json")).get("hand_cases_version"))
    print("   run_id:", j8.get("run_id"))

    # ---------------- 7. 复跑比对 ----------------
    h("7. 隔离副本复跑 vs 入库字节（O1 归一口径）")
    pairs = [
        ("check_inputs_mode_output.txt", RERUN / "check_inputs_mode_output.txt"),
        ("check_evidence_mode_output.txt", RERUN / "check_evidence_mode_output.txt"),
        ("selfcheck_c11_stdout.txt", RERUN / "selfcheck_c11_stdout.txt"),
        ("selfcheck_result.json", RERUN / "run_dir_snapshot/selfcheck_result.json"),
        ("probe_summary.json", RERUN / "run_dir_snapshot/probe_summary.json"),
        ("claim_verification.json", RERUN / "run_dir_snapshot/claim_verification.json"),
        ("claim_verification.md", RERUN / "run_dir_snapshot/claim_verification.md"),
    ]
    for name, rp in pairs:
        cp = RUN8 / name
        if not rp.is_file():
            print(f"   {name}: 复跑产物缺失 {rp}")
            continue
        a, b = norm(cp.read_bytes()), norm(rp.read_bytes())
        same = a == b
        print(f"   {name}: 归一后逐字节相同 = {same}（com {len(a)}B / rerun {len(b)}B）")
        if not same and name.endswith(".json"):
            da, db = json.loads(a.decode("utf-8")), json.loads(b.decode("utf-8"))
            diffs = [(k, da.get(k), db.get(k)) for k in set(da) | set(db)
                     if json.dumps(da.get(k), ensure_ascii=False, sort_keys=True)
                     != json.dumps(db.get(k), ensure_ascii=False, sort_keys=True)]
            for k, x, y in diffs:
                if k == "checks":
                    for cx, cy in zip(x, y):
                        if json.dumps(cx, ensure_ascii=False, sort_keys=True) != json.dumps(cy, ensure_ascii=False, sort_keys=True):
                            for kk in set(cx) | set(cy):
                                if json.dumps(cx.get(kk), ensure_ascii=False, sort_keys=True) != json.dumps(cy.get(kk), ensure_ascii=False, sort_keys=True):
                                    print(f"        checks[{cx['id']}].{kk}: com={json.dumps(cx.get(kk),ensure_ascii=False)[:200]}")
                                    print(f"        checks[{cx['id']}].{kk}: rrn={json.dumps(cy.get(kk),ensure_ascii=False)[:200]}")
                elif k == "claims":
                    for cx, cy in zip(x or [], y or []):
                        for kk in set(cx) | set(cy):
                            if json.dumps(cx.get(kk), ensure_ascii=False, sort_keys=True) != json.dumps(cy.get(kk), ensure_ascii=False, sort_keys=True):
                                print(f"        claims[{cx['claim_id']}].{kk}: com={json.dumps(cx.get(kk),ensure_ascii=False)[:200]}")
                                print(f"        claims[{cx['claim_id']}].{kk}: rrn={json.dumps(cy.get(kk),ensure_ascii=False)[:200]}")
                else:
                    print(f"        {k}: com={json.dumps(x,ensure_ascii=False)[:220]}")
                    print(f"        {k}: rrn={json.dumps(y,ensure_ascii=False)[:220]}")
    probe_files = sorted(p.name for p in RUN8.glob("probe_*_stdout.txt"))
    bad = []
    for name in probe_files:
        rp = RERUN / "run_dir_snapshot" / name
        if not rp.is_file() or norm((RUN8 / name).read_bytes()) != norm(rp.read_bytes()):
            bad.append(name)
    print(f"   probe_*_stdout.txt：{len(probe_files)} 个，逐字节不同 = {bad}")

    # claim_verification 的逐条声明
    h("8. claim_verification.json 逐条声明（入库）")
    cv = json.loads(T(RUN8 / "claim_verification.json"))
    print("   verdict =", cv["verdict"], "；条数 =", len(cv["claims"]))
    for c in cv["claims"]:
        print(f"   - {c['claim_id']} [{c['verdict']}] exit={c['exit_code']}")
        print(f"     声明: {c['statement']}")
        print(f"     命令: {c['command']}")
        for o in c["observations"]:
            print(f"     观察: {o[:300]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())