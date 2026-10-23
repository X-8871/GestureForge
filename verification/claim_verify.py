#!/usr/bin/env python3
"""验证附录生成器 v2（可信版）：**每条声明的退出码必须来自真实 subprocess 执行**。

设计要点（针对终审 A `BLK-r08-2`）：
* 每条 claim = {id, statement, argv, expect_exit, observable}；`exit_code` 一律记 **真实退出码**；
* 命令全部是**可独立复算**的真实命令（无 `<tmp>` 占位符），产物写入 `tmp/6/claim_runs/<run>/`；
* 跳过判定按 **run_dir 相对路径**（不再因为绝对路径含 `tmp` 就整体跳过）；
* 内置 `self_test_false_claim`：一条**故意为假**的声明必须得到非 0 退出码，证明本工具会 FAIL；
* 判定 `ALL_CLAIMS_VERIFIED` 仅当所有 claim 的真实退出码 = 期望值且 self-test 非 0。

用法：
    python -B verification/claim_verify.py --package s6a|s6b --run-dir <rel> --project-root <abs>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
PY = sys.executable



_HAND_INPUTS = ("coverage_matrix.json", "limitations_not_executed.json", "hand_computed_cases.json",
                "upstream_bindings.json", "fix_record.json", "fix_record.md")


def _hand_hashes(run_dir: Path) -> dict[str, str]:
    """人工撰写输入的哈希（用于**只读自检**：任何 claim 都不得改写证据目录）。"""
    return {name: hashlib.sha256((run_dir / name).read_bytes()).hexdigest()
            for name in _HAND_INPUTS if (run_dir / name).is_file()}

def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def s6a_claims(root: Path, run_rel: str, out_dir: Path) -> list[dict]:
    run_dir = root / run_rel
    return [
        {"id": "S6A-C1-m4-residual-regression",
         "statement": "C16 能捕获评审给出的 3 条真实 M4 残留行（基线 PASS + 逐条注入 FAIL）",
         "argv": [PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                  "--run-dir", run_rel, "--out", str(out_dir / "m4_residual_regression.json")],
         "expect_exit": 0, "observable": str(out_dir / "m4_residual_regression.json")},
        {"id": "S6A-C2-hash-convention-both-directions",
         "statement": "O1 换行口径接受器覆盖两个方向（CRLF→LF 与 LF→CRLF），内容不同必须拒绝",
         "argv": [PY, "-B", "verification/hash_convention_check.py"],
         "expect_exit": 0, "observable": "tmp/6/hash_convention_check.json"},
        {"id": "S6A-C3-m4-two-representations",
         "statement": "transitions[M4].reachability 与 reachability.transitions.M4.status 两个表示一致（NB-r03-10）",
         "argv": [PY, "-B", "-c",
                  "import json;d=json.load(open('docs/stage6/s6a_stage6_g0_behavior_v1.json',encoding='utf-8'));"
                  "tr={e['id']:e for e in d['transitions']};r=d['reachability']['transitions'];"
                  "bad=[k for k,v in tr.items() if 'reachability' in v and k in r and "
                  "(('UNREACHABLE' in str(v['reachability']).upper()) != ('UNREACHABLE' in str(r[k]['status']).upper()))];"
                  "print('conflicts=',bad);assert not bad,bad"],
         "expect_exit": 0, "observable": "stdout: conflicts=[]"},
        {"id": "S6A-C5-tool-self-tests",
         "statement": ("四个验证工具的自测两例全部符合预期（**引用套件产物**，不重跑）："
                       "守门 不改→静默/改→中止 exit1；export_selfproof 有效提交→0/不可解析→非0；"
                       "claim_verify 正常→0/假声明→非0；m4_residual_regression 3 条真实残留被捕获→0/目录不存在→拒绝非0"),
         "argv": [PY, "-B", "-c",
                  "import hashlib,json,pathlib,sys;"
                  "p=pathlib.Path(r'" + run_rel + "/tool_self_tests.json');assert p.is_file(),'缺少自测套件产物（应随包入库）';"
                  "d=json.loads(p.read_text(encoding='utf-8'));"
                  "bad=[c['case_id'] for c in d['cases'] if c['verdict']!='AS_EXPECTED'];"
                  "print('sha256=',hashlib.sha256(p.read_bytes()).hexdigest(),'verdict=',d['verdict'],'cases=',len(d['cases']));"
                  "assert d['verdict']=='ALL_AS_EXPECTED' and not bad,bad"],
         "expect_exit": 0,
         "observable": ("复算命令：python -B verification/tool_self_tests.py --project-root <abs>；"
                        "产物随包入库：<run-dir>/tool_self_tests.json（含各例真实退出码）")},
        {"id": "S6A-C6-fresh-selfcheck-after-build",
         "statement": ("构建结束后**新鲜自检两次**（间隔 30s）均 ALL_PASS 且 C11 不再报任何被声明文件哈希不符"
                       "（证明「清单写在被绑定文件之后」的结构问题已修、且构建后无残留写入者）"),
         "argv": [PY, "-B", "verification/s6a_fresh_selfcheck_twice.py", "--project-root", str(root),
                  "--run-dir", run_rel, "--gap-seconds", "30"],
         "expect_exit": 0,
         "observable": "tmp/6/fresh_selfcheck_pair.json（两次的真实退出码与 C11 状态）"},
        {"id": "S6A-C7-approval-c4-regression",
         "statement": ("C4 批准纪律的反向自测：人为把一项参数改回 PENDING_APPROVAL → C4 必须 FAIL；"
                       "基线（未注入）必须 ALL_PASS。全部操作在临时副本内，不触碰真实证据目录。"),
         "argv": [PY, "-B", "verification/approval_regression.py", "--project-root", str(root),
                  "--run-dir", run_rel, "--out", str(out_dir / "approval_regression.json")],
         "expect_exit": 0,
         "observable": "stdout: baseline [0, PASS] 与 injected [非0, FAIL]；产物 JSON 落盘"},
        {"id": "S6A-C4-selfcheck-all-pass",
         "statement": "S6-A 自检 17 项 ALL_PASS（含 C16 语义扫描与两表示法交叉断言）",
         "argv": [PY, "-B", "verification/s6_g0_selfcheck.py",
                  "--json", "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                  "--doc", "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
                  "--cases", f"{run_rel}/hand_computed_cases.json",
                  "--upstream", f"{run_rel}/upstream_bindings.json",
                  "--out", str(out_dir / "selfcheck_replay.json"),
                  "--project-root", str(root), "--evidence-dir", str(run_dir),
                  "--state", ".codex/STATE.md"],
         "expect_exit": 0, "observable": str(out_dir / "selfcheck_replay.json")},
    ]


def s6b_claims(root: Path, run_rel: str, out_dir: Path) -> list[dict]:
    report = f"{run_rel}/run_report.json"
    id_check = (
        "import json;d=json.load(open('" + report + "',encoding='utf-8'));"
        "ids={c['case_id']:[r.get('acquisition_id') for r in (c['observed'].get('action_records') or [])] "
        "for c in d['cases']};"
        "want={'C12-m8-two-acquisitions':[0,1],'C12-m2-m12-new-target':[0,2],"
        "'C12-gate-reopen-new-acquisition':[0,1,2]};"
        "bad={k:(want[k],ids.get(k)) for k in want if ids.get(k)!=want[k]};"
        "print('status=',d['status'],'ids=',{k:ids.get(k) for k in want});assert d['status']=='PASS';assert not bad, bad"
    )
    return [
        {"id": "S6B-C1-acquisition-id-lifecycle",
         "statement": "BLK-r03-1：M8/M2/M12 等结束获取的转移分配新 acquisition_id（三例实测 [0,1]/[0,2]/[0,1,2]）",
         "argv": [PY, "-B", "-c", id_check], "expect_exit": 0,
         "observable": "stdout: status=PASS 与三例 id 序列"},
        {"id": "S6B-C2-action-records-fields",
         "statement": "action_records 含四个必需字段，且四个 ACTION_* 事件名在证据中出现",
         "argv": [PY, "-B", "-c",
                  "import json;d=json.load(open('" + report + "',encoding='utf-8'));"
                  "recs=[r for c in d['cases'] for r in (c['observed'].get('action_records') or [])];"
                  "need=('action_type','target_id','acquisition_id','t_trigger_ns');"
                  "miss=[k for k in need if not all(k in r for r in recs)];"
                  "ev=set()\n"
                  "for r in recs: ev.update([r.get('event'),r.get('effective_event')])\n"
                  "four=[x for x in ('ACTION_SUBMITTED','ACTION_EFFECTIVE','ACTION_FAILED','ACTION_UNOBSERVED') if x not in ev];"
                  "print('records=',len(recs),'missing_fields=',miss,'missing_events=',four);assert not miss and not four"],
         "expect_exit": 0, "observable": "stdout: records/missing 均为空"},
        {"id": "S6B-C3-no-dead-constants",
         "statement": "核心与动作层没有定义后从未使用的常量",
         "argv": [PY, "-B", "verification/s6b_no_dead_constants.py"], "expect_exit": 0,
         "observable": "stdout: unused=[]"},
        {"id": "S6B-C4-m4-counted-and-registrations",
         "statement": "M4 计入覆盖；未实现项与开放行为偏差均已登记",
         "argv": [PY, "-B", "-c",
                  "import json;L=json.load(open('" + f"{run_rel}/limitations_not_executed.json" + "',encoding='utf-8'));"
                  "print('not_implemented=',len(L.get('not_implemented') or []),"
                  "'open_deviations=',len(L.get('open_behavior_deviations') or []),"
                  "'counted=',L.get('reachability_counted'));"
                  "assert L.get('not_implemented') and L.get('open_behavior_deviations') "
                  "and any('M4' in str(x) for x in (L.get('reachability_counted') or []))"],
         "expect_exit": 0, "observable": "stdout: 三类登记非零且含 M4"},
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="验证附录生成器 v2")
    parser.add_argument("--package", choices=["s6a", "s6b"], required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--simulate-defect", choices=["none", "count_mismatch", "empty"], default="none",
                        help="仅工具自测用：人为制造数量不符/空列表，证明判定会返回 NOT_ALL_VERIFIED")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"RunId 目录不存在：{run_dir}")
        return 1
    out_dir = root / "tmp/6/claim_runs" / run_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    # 命令文本一律用**项目根相对 POSIX 路径**：绝对 Windows 路径含反斜杠，放进 `python -c` 字符串会被转义破坏
    _run_path = Path(args.run_dir)
    run_rel = _run_path.resolve().relative_to(root).as_posix() if _run_path.is_absolute() else _run_path.as_posix()
    claims = s6a_claims(root, run_rel, out_dir) if args.package == "s6a" else s6b_claims(root, run_rel, out_dir)

    results: list[dict] = []
    readonly_guard: dict[str, dict[str, str]] = {}
    declared = len(claims)
    expected_count = declared + 1  # 含内置的 self_test_false_claim

    for claim in claims:
        _before = _hand_hashes(run_dir)
        exit_code, output = run(claim["argv"], root)
        _after = _hand_hashes(run_dir)
        _changed = [k for k in sorted(set(_before) | set(_after)) if _before.get(k) != _after.get(k)]
        print(f"[RO-TRACE] {claim['id']} changed={_changed}")
        if _changed:
            readonly_guard[claim["id"]] = {"changed": _changed}
        ok = (exit_code == claim["expect_exit"]) and not _changed
        # B-1 修复：append 必须在**循环体内**（此前它位于 `return 1` 之后，永不可达 ⇒ 附录只剩 1 条却自称 ALL_CLAIMS_VERIFIED）
        results.append({
            "claim_id": claim["id"], "statement": claim["statement"],
            "command": subprocess.list2cmdline(claim["argv"]),
            "exit_code": exit_code, "expected_exit": claim["expect_exit"],
            "observable": claim["observable"],
            "output_tail": output.strip().splitlines()[-3:] if output.strip() else [],
            "readonly_violation": _changed,
            "verdict": "VERIFIED" if ok else "NOT_VERIFIED",
        })

    false_exit, false_out = run([PY, "-B", "-c", "print('deliberately false claim');assert 1 == 2"], root)
    results.append({
        "claim_id": "self_test_false_claim",
        "statement": "故意为假的声明（assert 1==2）必须得到非 0 退出码——证明本工具会 FAIL",
        "command": subprocess.list2cmdline([PY, "-B", "-c", "assert 1==2"]),
        "exit_code": false_exit, "expected_exit": "非 0",
        "observable": "self-test", "output_tail": false_out.strip().splitlines()[-1:],
        "readonly_violation": [],
        "verdict": "VERIFIED" if false_exit != 0 else "NOT_VERIFIED",
    })

    if readonly_guard:
        print("[RO-GUARD] 只读约束被破坏（下述 claim 改写了证据目录，已如实记为 NOT_VERIFIED）："
              + json.dumps(readonly_guard, ensure_ascii=False))

    # ---- 新增断言 (a)：数量必须等于该包定义的 claim 数 + 1（含 false self-test）----
    simulate = getattr(args, "simulate_defect", "none")
    if simulate == "empty":
        results = []
    elif simulate == "count_mismatch":
        results = results[:-1]  # 人为丢掉一条，制造数量不符
    count_ok = len(results) == expected_count
    if not count_ok:
        print(f"[COUNT-ASSERT] claims 数量不符：记录 {len(results)}，期望 {expected_count}（定义 {declared} + 1）")

    # ---- 新增断言 (b)：verdict 由**全部** claim 的 exit_code 计算；空列表或数量不符一律 NOT_ALL_VERIFIED ----
    all_ok = bool(results) and count_ok and all(c["verdict"] == "VERIFIED" for c in results)
    verdict = "ALL_CLAIMS_VERIFIED" if all_ok else "NOT_ALL_VERIFIED"

    payload = {
        "schema_version": 1,
        "artifact": "claim_verification",
        "task_id": "S6-A" if args.package == "s6a" else "S6-B",
        "run_id": run_dir.name,
        "rule": ("每条声明的 exit_code 均为**真实 subprocess 退出码**；命令可独立复算（无占位符）；"
                 "内置 self_test_false_claim 证明本工具对假声明会 FAIL；"
                 "verdict 由**全部** claim 计算，且 claims 数量必须等于定义数 + 1，空列表/数量不符一律 NOT_ALL_VERIFIED。"),
        "reproduce": (f"python -B verification/claim_verify.py --package {args.package} "
                      f"--run-dir {args.run_dir} --project-root {root}"),
        "generated_at_utc8": datetime.now(UTC8).strftime("%Y-%m-%d %H:%M:%S"),
        "claims_declared": declared,
        "claims_recorded": len(results),
        "count_ok": count_ok,
        "readonly_violations": readonly_guard,
        "claims": results,
        "verdict": verdict,
        "scope_statement": "本附录只证明这些声明在**本次真实执行**下成立；不代表独立审查或验收通过。",
    }
    (run_dir / "claim_verification.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                                                     encoding="utf-8")
    lines = ["# 验证附录 claim_verification（v2：真实退出码）", "", payload["rule"], "",
             f"- 生成：{payload['generated_at_utc8']}；判定：**{payload['verdict']}**",
             f"- 复算命令：`{payload['reproduce']}`", ""]
    for item in results:
        lines += [f"## {item['claim_id']} — {item['verdict']}", "",
                  f"- 声明：{item['statement']}", f"- 命令：`{item['command']}`",
                  f"- 真实退出码：{item['exit_code']}（期望 {item['expected_exit']}）",
                  f"- 可观察输出：{item['output_tail']}", ""]
    lines.append(payload["scope_statement"])
    (run_dir / "claim_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "claims": [(c["claim_id"], c["exit_code"], c["verdict"]) for c in results]}, ensure_ascii=False))
    return 0 if payload["verdict"] == "ALL_CLAIMS_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
