#!/usr/bin/env python3
"""阶段6 6-E 离线轮 A 组**逐项**核验（对终审批次 E §七 关闭条件与任务卡 A1..A7）。

    python -B verification/s6e_a_group_verify.py --project-root <abs> [--out <json>]

只读核验：每项给出判定与**真实命令/退出码**（需要执行的行内跑子进程并记录退出码）。
退出码：0 = A 组全部按预期；1 = 存在未达预期项。

注意：`A7①` 依赖 r13/r08 的「新鲜证据对」已由各自构建器真实产出；构建未完成时该项会如实报 FAIL。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SPEC = "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"
STATE = ".codex/STATE.md"
R12 = "report/evidence/S6-A/s6a_g0_20261023_r12"
R13 = "report/evidence/S6-A/s6a_g0_20261024_r13"
R08 = "report/evidence/S6-B/s6b_core_20261024_r08"
S6E = "report/evidence/S6-E/s6e_acceptance_20261024_r01"


def run(argv: list[str], root: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--out", default="tmp/6/s6e_a_group_verify.json")
    args = ap.parse_args(argv)
    root = Path(args.project_root).resolve()
    items: list[dict] = []

    def item(item_id: str, desc: str, ok: bool, command: str, detail: str) -> None:
        items.append({"id": item_id, "desc": desc, "verdict": "PASS" if ok else "FAIL",
                      "command": command, "detail": detail})

    spec = (root / SPEC).read_text(encoding="utf-8")
    state = (root / STATE).read_text(encoding="utf-8")

    # A-1 STATE 失实陈述更正
    ok = ("A1 失实陈述更正" in state and "该表述属「把未做写成已做」" in state
          and "本轮 r13 已真正落实" in state and "DELIVERED_PENDING_REVIEW" in state)
    item("A1-state-correction", "STATE 更正 G6b 的「8 条历史行已写回」失实表述并声明本轮真正落实", ok,
         f"read {STATE}", f"含 A1 段={('A1 失实陈述更正' in state)}；含失实定性与落实声明={ok}")

    # A-2 规格文档行号/措辞
    needles = {
        "L9": "（已批准 2026-10-23）。** 本文是阶段6",
        "L171": "表 A-1（动作映射；`supported_types` 已按 `U6-15`",
        "L185": "具体可见时长属开放项 `U6-14`",
        "L282": "门槛本身已由 Wong 于 2026-10-23 批准",
        "L320": "受 `T6-A01`（1000 ms，已批准 2026-10-23）约束",
        "L321": "**数值仍 `NOT_RUN`**",
    }
    missing = [k for k, v in needles.items() if v not in spec]
    stale = "（待批准）。** 本文是阶段6" in spec
    item("A2-spec-wording", "规格 L9/L171/L185/L282/L320/L321 改准（无残留「待批准」状态行）",
         not missing and not stale, f"read {SPEC}",
         f"缺失={missing}；仍含旧状态行={stale}")

    # A-3 8 条历史修订行写回 + 机读标记
    written_back = spec.count("（当时状态）")
    markers = spec.count("【历史语境】")
    pending_tokens = spec.count("`PENDING_APPROVAL`")
    item("A3-history-lines", "8 条历史修订行写回当时状态并逐行加机读标记",
         written_back == 8 and markers == 8 and pending_tokens >= 8,
         f"read {SPEC}",
         f"「（当时状态）」计数={written_back}（期望 8）；【历史语境】计数={markers}（期望 8）；"
         f"PENDING_APPROVAL 计数={pending_tokens}")

    # A-4 机读假命题清除 + 旧 RunId 未改写
    fix13_text = (root / R13 / "fix_record.json").read_text(encoding="utf-8")
    fix13 = json.loads(fix13_text)

    def all_keys(obj) -> set:
        keys: set = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.add(k)
                keys |= all_keys(v)
        elif isinstance(obj, list):
            for v in obj:
                keys |= all_keys(v)
        return keys

    disc = fix13.get("revision_discipline", {})
    false_keys = [k for k in all_keys(fix13) if k in ("all_parameters_pending_approval",
                                                       "thresholds_are_draft_not_approved")]
    code, old_text = run(["git", "-C", str(root), "show", f"HEAD:{R12}/fix_record.json"], root)
    old_keeps = False
    if code == 0:
        try:
            old_keeps = "all_parameters_pending_approval" in all_keys(json.loads(old_text))
        except json.JSONDecodeError:
            old_keeps = False
    item("A4-false-claim-cleared", "r13 清除机读假命题、身份改准为 r13；r12（旧 RunId）未被就地改写",
         (not false_keys) and disc.get("new_run_id") == "s6a_g0_20261024_r13"
         and disc.get("false_machine_claims_present") is False and old_keeps,
         "read r13/fix_record.json + git show HEAD:r12/fix_record.json",
         f"r13 机读假字段键={false_keys}；new_run_id={disc.get('new_run_id')}；"
         f"r12 仍保有历史假字段键={old_keeps}")

    # A-5 扫描器大小写不敏感 + 收窄；旧包仍是反例
    scan = root / "verification/approved_package_scan.py"
    scan_src = scan.read_text(encoding="utf-8")
    src_ok = "re.IGNORECASE" in scan_src and "SKIP_FILES" in scan_src and "PROHIBITION" in scan_src
    exits = {}
    for label, rel in (("r12", R12), ("r13", R13), ("r08", R08)):
        out = f"tmp/6/a_group_scan_{label}.json"
        rc, _ = run([sys.executable, "-B", "verification/approved_package_scan.py", "--project-root", str(root),
                     "--run-dir", rel, "--out", out], root)
        payload = json.loads((root / out).read_text(encoding="utf-8"))
        exits[label] = (rc, len(payload["hits"]))
    item("A5-scanner-tightened", "扫描器大小写不敏感并收窄豁免；旧包 r12 仍报命中、r13/r08 CLEAN",
         src_ok and exits["r12"][0] == 1 and exits["r12"][1] > 0
         and exits["r13"][0] == 0 and exits["r13"][1] == 0 and exits["r08"][0] == 0 and exits["r08"][1] == 0,
         "approved_package_scan.py --run-dir {r12,r13,r08}",
         f"源码标记={src_ok}；退出码/命中 r12={exits['r12']} r13={exits['r13']} r08={exits['r08']}")

    # A-6 B3/B6/B7 等形态的必失败注入（两向）
    rc, stdout = run([sys.executable, "-B", "verification/approved_package_scan.py", "--project-root", str(root),
                      "--run-dir", R13, "--inject-self-test", "--out", "tmp/6/a_group_scan_inject.json"], root)
    inject = json.loads((root / "tmp/6/a_group_scan_inject.json").read_text(encoding="utf-8"))
    st = inject.get("self_test", {})
    caught = st.get("must_fail_caught", {})
    clean = st.get("must_pass_clean", {})
    ok6 = (rc == 0 and st.get("verdict") == "AS_EXPECTED" and caught and all(caught.values())
           and clean and not any(clean.values()))
    item("A6-must-fail-injections", "B1..B7 必判失败形态全部被捕获 + C1..C4 放行对照全部不命中",
         ok6, "approved_package_scan.py --run-dir r13 --inject-self-test",
         f"exit={rc}；verdict={st.get('verdict')}；caught={caught}；clean={clean}")

    # A-7 批次 C 三项
    pair_a = root / R13 / "fresh_selfcheck_pair.json"
    pair_b = root / R08 / "s6b_fresh_evidence_pair.json"
    pair_a_ok = pair_a.is_file() and json.loads(pair_a.read_text(encoding="utf-8")).get("verdict") == "BOTH_ALL_PASS"
    pair_b_ok = pair_b.is_file() and json.loads(pair_b.read_text(encoding="utf-8")).get("verdict") == "BOTH_CHECKS_OK"
    tests_src = (root / "verification/tool_self_tests.py").read_text(encoding="utf-8")
    tmp_copy_ok = "sim_root" in tests_src and "只在临时副本" in tests_src
    failclosed_src = "INCOMPLETE_SKIPPED" in tests_src and "--simulate-skip" in tests_src
    sim = root / "tmp/6/simulate_skip_suite.json"
    sim_ok = sim.is_file() and json.loads(sim.read_text(encoding="utf-8")).get("verdict") == "INCOMPLETE_SKIPPED"
    item("A7-batch-c", "① 新鲜证据对真实产出并入库 ② 必 FAIL 例改临时副本 ③ skipped fail-closed + 套件入库",
         pair_a_ok and pair_b_ok and tmp_copy_ok and failclosed_src and sim_ok,
         "read r13/fresh_selfcheck_pair.json, r08/s6b_fresh_evidence_pair.json, tool_self_tests.py, tmp/6/simulate_skip_suite.json",
         f"① r13 对={pair_a_ok} r08 对={pair_b_ok}；② 临时副本={tmp_copy_ok}；"
         f"③ fail-closed 源码={failclosed_src}、--simulate-skip 产物 INCOMPLETE_SKIPPED={sim_ok}")

    # A-8 三包的清单检查项退出口径
    summary = {}
    ok8 = True
    for rel in (R13, R08, S6E):
        manifest = json.loads((root / rel / "delivery_manifest.json").read_text(encoding="utf-8"))
        checks = [(c["name"], c["status"], c["exit_code"]) for c in manifest["checks"]]
        summary[rel] = checks
        if any(s not in ("PASS",) or (e not in (0,)) for _, s, e in checks):
            ok8 = False
    item("A8-package-checks", "r13/r08/S6-E 三包清单内全部检查项均为 PASS 且 exit_code=0", ok8,
         "read {r13,r08,S6-E}/delivery_manifest.json", json.dumps(summary, ensure_ascii=False)[:400])

    verdict = "ALL_PASS" if all(x["verdict"] == "PASS" for x in items) else "FAILED"
    payload = {"schema_version": 1, "artifact": "s6e_a_group_verify", "run_id": "s6e_acceptance_20261024_r01",
               "scope": "终审批次 E §七 关闭条件（A1..A7）与 A8 退出口径的逐项只读核验",
               "items": items, "verdict": verdict}
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "items": [(i["id"], i["verdict"]) for i in items]}, ensure_ascii=False))
    for i in items:
        if i["verdict"] != "PASS":
            print(f"FAIL {i['id']}: {i['detail']}")
    return 0 if verdict == "ALL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())