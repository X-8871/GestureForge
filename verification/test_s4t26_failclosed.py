#!/usr/bin/env python3
"""S4-T26 只读检查器的 fail-closed 负控测试。

目的：证明“未闭合不会被误判成通过”不是口头承诺，而是可用真实退出码复现的行为。
T1–T18 都在 `D:\\tmp` 下的隔离目录里跑**真实子进程**并断言真实退出码；
T19 是函数级真值表（直接调用判定函数、逐行比对期望），单独标注，不冒充子进程用例。
本脚本不写工作树、不生成黄金、不做推理、不访问硬件。

退出码：0 = 全部负控通过；1 = 存在失败用例；2 = 环境错误（脚本/证据缺失）。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
CN = timezone(timedelta(hours=8))
EV = WORKTREE / "report/evidence/S4-CTRL"
AUDIT = WORKTREE / "scripts/stage4_s4ctrl/audit_t26_producer_provenance.py"
RECONCILE = WORKTREE / "scripts/stage4_s4ctrl/reconcile_t26_gate_evidence.py"
BRIDGE = WORKTREE / "scripts/stage4_s4ctrl/replay_forward_bridge.py"
REPORT = WORKTREE / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
PINNED_REPORT_SHA = "6d73283c698a94dd30cf00634de59fb76a8e889916eb4d00e50b76c245687216"

DIVERGENCE_RUN = "s4t26_layer_divergence_20261026_r02"
HEAD_FILES = (
    f"{DIVERGENCE_RUN}/sample_000_actual_head13_int8.bin",
    f"{DIVERGENCE_RUN}/sample_000_actual_head26_int8.bin",
    f"{DIVERGENCE_RUN}/sample_102_actual_head13_int8.bin",
    f"{DIVERGENCE_RUN}/sample_102_actual_head26_int8.bin",
    "s4t26_golden_rebind_20261026_r02/golden/test_fist_000_head13.bin",
    "s4t26_golden_rebind_20261026_r02/golden/test_fist_000_head26.bin",
    "s4t26_golden_rebind_20261026_r02/golden/approved_no_hand_001_head13.bin",
    "s4t26_golden_rebind_20261026_r02/golden/approved_no_hand_001_head26.bin",
)
GATE_CHECKS = (
    "raw_head_gate_forward_byte_compare",
    "positive_detection_gate_forward_d9_nms",
    "negative_control_one_int8_input_byte",
    "png_imread_unchanged_pixel_identity",
    "task25_replay_frame_forward",
)


TRACE_HITS: list[str] = []


def run(script: Path, args: list[str]) -> int:
    """运行脚本并返回真实退出码；顺带记录输出中是否出现 traceback。"""
    proc = subprocess.run([sys.executable, "-B", str(script), *args],
                          capture_output=True, text=True)
    if "Traceback (most recent call last)" in (proc.stdout + proc.stderr):
        TRACE_HITS.append(" ".join(args[:2]))
    return proc.returncode


def sha256_file(path: Path) -> str:
    """按块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_fake_root(tmp: Path, name: str, *, status: str, exit_code: object,
                    bridge_sha: str | None, g0_status: str = "PASS",
                    checks_pass: bool = True) -> Path:
    """在临时目录造一份“证据根”，用于端到端验证对齐判定（只写 tmp）。"""
    root = tmp / name
    for rel in HEAD_FILES:
        src = EV / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    div_dir = root / DIVERGENCE_RUN
    div_dir.mkdir(parents=True, exist_ok=True)
    (div_dir / "layer_divergence_report.json").write_text(json.dumps({
        "status": "LAYER_MATCH_AND_REQUIRED_GATES_PASS", "exit_code": 0,
        "first_byte_mismatch_layer": None,
        "sources": {"bridge": {"sha256": bridge_sha}},
    }, ensure_ascii=False), encoding="utf-8")

    g0_dir = root / "s4t26_g0_inputs_20261026_r13"
    g0_dir.mkdir(parents=True, exist_ok=True)
    (g0_dir / "preflight_verification.json").write_text(json.dumps({
        "status": g0_status, "exit_code": 0 if g0_status == "PASS" else 2,
        "checks": [{"name": "bridge_runner_moving_head_contract",
                    "detail": {"bridge_source_sha256": bridge_sha}}],
    }, ensure_ascii=False), encoding="utf-8")

    run_dir = root / "s4t26_golden_rebind_20261026_r02"
    run_dir.mkdir(parents=True, exist_ok=True)
    checks = {name: {"status": "PASS" if checks_pass else "BLOCKED"} for name in GATE_CHECKS}
    if not checks_pass:
        checks[GATE_CHECKS[1]] = {"status": "BLOCKED"}
    (run_dir / "replay_forward_bridge_result.json").write_text(json.dumps({
        "status": status, "exit_code": exit_code, "checker_version": "r-selftest",
        "generated_utc8": datetime.now(CN).isoformat(timespec="seconds"),
        "checks": checks,
    }, ensure_ascii=False), encoding="utf-8")
    (run_dir / "preflight_verification.json").write_text(json.dumps({
        "bridge_source": {"sha256": bridge_sha, "version": "r-selftest",
                          "path": str(BRIDGE)},
    }, ensure_ascii=False), encoding="utf-8")
    return root


def case_results(tmp: Path) -> list[dict[str, object]]:
    """逐用例执行并记录真实退出码与期望值。"""
    cases: list[dict[str, object]] = []
    empty_root = tmp / "no_candidates"
    empty_root.mkdir(parents=True, exist_ok=True)
    fast = ["--search-root", str(empty_root)]
    bridge_now = sha256_file(BRIDGE) if BRIDGE.is_file() else ""
    stale = "6780446fc4f0d774b5868896b455deec8fc3dcd9e1ffa12a6990577138e57f26"

    # T1：证据目录指向已存在的普通文件 → 输入错误 2（不是 1）
    blocker = tmp / "is_a_file.txt"
    blocker.write_text("x", encoding="utf-8")
    cases.append({
        "id": "T1_audit_evidence_dir_is_file", "expect": 2,
        "actual": run(AUDIT, ["--evidence-dir", str(blocker), *fast]),
        "meaning": "非法证据目录必须归为输入错误（2），不得与未闭合（1）混同",
    })
    # T2：被审报告被改写（与冻结 SHA 不一致）→ 拒绝审计（2）
    tampered = tmp / "activation_report_tampered.json"
    tampered.write_bytes(REPORT.read_bytes() + b" ")  # 仅追加一个字节，JSON 仍合法
    tampered_sha = sha256_file(tampered)
    cases.append({
        "id": "T2_audit_report_not_pinned", "expect": 2,
        "actual": run(AUDIT, ["--evidence-dir", str(tmp / "t2"),
                              "--activation-report", str(tampered), *fast]),
        "meaning": "禁止用被改写过的 activation report 自证关闭",
    })
    # T2b：换钉必须显式承认——同一份改写报告，带 --allow-repin 才允许继续审计（预期 1，仍 BLOCKED）
    cases.append({
        "id": "T2b_audit_repin_requires_flag", "expect": 1,
        "actual": run(AUDIT, ["--evidence-dir", str(tmp / "t2b"),
                              "--activation-report", str(tampered),
                              "--expect-report-sha256", tampered_sha, "--allow-repin", *fast]),
        "meaning": "换钉须具名承认；即使承认，审计结论仍是 BLOCKED/1，不会变绿",
    })
    # T3：RunId 复用（目录非空）→ 拒绝（2）
    reused = tmp / "reused"
    reused.mkdir()
    (reused / "keep.txt").write_text("keep", encoding="utf-8")
    cases.append({
        "id": "T3_audit_runid_reuse", "expect": 2,
        "actual": run(AUDIT, ["--evidence-dir", str(reused), *fast]),
        "meaning": "RunId 不得复用，旧证据不得被覆盖",
    })
    # T4：已被删除的 --no-binding-audit 开关必须不再被接受（argparse → 2）
    cases.append({
        "id": "T4_audit_no_binding_audit_switch_removed", "expect": 2,
        "actual": run(AUDIT, ["--evidence-dir", str(tmp / "t4"), "--no-binding-audit", *fast]),
        "meaning": "绑定口径歧义不可通过开关跳过",
    })
    # T5：reconcile 证据目录为普通文件 → 2
    cases.append({
        "id": "T5_reconcile_evidence_dir_is_file", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(blocker), *fast]),
        "meaning": "非法证据目录归为输入错误",
    })
    # T6：真实审计在未闭合时必须是 1（不得为 0）
    cases.append({
        "id": "T6_audit_real_unclosed_exit1", "expect": 1,
        "actual": run(AUDIT, ["--evidence-dir", str(tmp / "t6")]),
        "meaning": "producer 不可复现 + 绑定歧义时必须 BLOCKED/1",
    })
    # T7：真实对齐在权威门未重跑时必须是 1
    cases.append({
        "id": "T7_reconcile_real_unclosed_exit1", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t7")]),
        "meaning": "当前桥接器无 PASS 运行时必须 BLOCKED/1",
    })
    # T8：证据根缺失 → 2
    cases.append({
        "id": "T8_reconcile_missing_root", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t8"),
                                  "--evidence-root", str(tmp / "no_such_root")]),
        "meaning": "证据根缺失属输入错误",
    })
    # T9：证据 JSON 结构非法（顶层是数组）→ 2，不得崩成 1
    bad_root = tmp / "bad_struct"
    (bad_root / DIVERGENCE_RUN).mkdir(parents=True)
    (bad_root / DIVERGENCE_RUN / "layer_divergence_report.json").write_text("[1]", encoding="utf-8")
    cases.append({
        "id": "T9_reconcile_invalid_structure_exit2", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t9"),
                                  "--evidence-root", str(bad_root)]),
        "meaning": "结构非法的合法 JSON 必须归为输入错误（2），不得伪装成未闭合（1）",
    })
    # T10：门运行 BLOCKED 但仍记录当前桥接器字节 → 不得判通过
    root10 = build_fake_root(tmp, "run_blocked", status="BLOCKED", exit_code=2,
                             bridge_sha=bridge_now)
    cases.append({
        "id": "T10_blocked_run_on_current_bridge", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t10"),
                                  "--evidence-root", str(root10)]),
        "meaning": "跑过但失败 ≠ 通过（首轮 Review 的 P1 绿通道）",
    })
    # T11：门 PASS 但桥接器是旧字节 → 不得判通过
    root11 = build_fake_root(tmp, "run_stale", status="PASS", exit_code=0, bridge_sha=stale)
    cases.append({
        "id": "T11_pass_on_stale_bridge", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t11"),
                                  "--evidence-root", str(root11)]),
        "meaning": "门必须在当前桥接器字节上跑过，旧 PASS 不算",
    })
    # T12：exit_code 为布尔 false（Python 中 False == 0）→ 不得判通过
    root12 = build_fake_root(tmp, "run_bool", status="PASS", exit_code=False,
                             bridge_sha=bridge_now)
    cases.append({
        "id": "T12_exit_code_bool_false", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t12"),
                                  "--evidence-root", str(root12)]),
        "meaning": "False == 0 的隐式比较会造成绿通道，必须严格整型判定",
    })
    # T13：五项必备检查缺项/未 PASS → 不得判通过
    root13 = build_fake_root(tmp, "run_missing_check", status="PASS", exit_code=0,
                             bridge_sha=bridge_now, checks_pass=False)
    cases.append({
        "id": "T13_missing_gate_check", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t13"),
                                  "--evidence-root", str(root13)]),
        "meaning": "缺任一门不得算门 PASS（防止只看顶层 status）",
    })
    # T14：正控——PASS/0 + 当前桥接器 + 五项全 PASS + G0 PASS → 必须 0
    root14 = build_fake_root(tmp, "run_pass", status="PASS", exit_code=0,
                             bridge_sha=bridge_now)
    cases.append({
        "id": "T14_positive_control_exit0", "expect": 0,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t14"),
                                  "--evidence-root", str(root14)]),
        "meaning": "证明判定不是恒 1：条件全满足时必须能通过",
    })
    # T15：G0 未闭合 → 即使门 PASS 也必须 1
    root15 = build_fake_root(tmp, "run_g0_blocked", status="PASS", exit_code=0,
                             bridge_sha=bridge_now, g0_status="BLOCKED")
    cases.append({
        "id": "T15_g0_blocked_gate_pass", "expect": 1,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t15"),
                                  "--evidence-root", str(root15)]),
        "meaning": "G0 未闭合时不得因门 PASS 而整体判通过",
    })
    # T16a：深层嵌套 JSON（20 万层）→ 2，不得以 RecursionError 崩成 1
    deep = tmp / "deep.json"
    deep.write_text("[" * 200000, encoding="utf-8")
    t16a_dir = tmp / "t16a"
    cases.append({
        "id": "T16a_audit_deep_json_exit2", "expect": 2,
        "actual": run(AUDIT, ["--evidence-dir", str(t16a_dir),
                              "--activation-report", str(deep),
                              "--expect-report-sha256", sha256_file(deep), "--allow-repin", *fast]),
        "meaning": "递归过深属输入错误（2），不得伪装成未闭合（1）",
        "expect_no_dir": str(t16a_dir),
    })
    # T16b：完整伪根 + 仅把 divergence 换成深层 JSON，确保失败原因就是“递归过深”
    deep_root = build_fake_root(tmp, "run_deep", status="PASS", exit_code=0,
                                bridge_sha=bridge_now)
    (deep_root / DIVERGENCE_RUN / "layer_divergence_report.json").write_bytes(deep.read_bytes())
    t16b_dir = tmp / "t16b"
    cases.append({
        "id": "T16b_reconcile_deep_json_exit2", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(t16b_dir),
                                  "--evidence-root", str(deep_root)]),
        "meaning": "关键证据递归过深同样属输入错误",
        "expect_no_dir": str(t16b_dir),
    })
    # T17：落盘阶段编码失败（孤立代理项）→ 2，且不留“非空但无结论”的目录
    sur_root = build_fake_root(tmp, "run_surrogate", status="PASS", exit_code=0,
                               bridge_sha=bridge_now)
    g0_path = sur_root / "s4t26_g0_inputs_20261026_r13/preflight_verification.json"
    g0_path.write_text(json.dumps({  # ensure_ascii=True：写入 \ud800 转义，读入后成为孤立代理项
        "status": "PASS", "exit_code": 0, "checks": [],
        "blocking_reasons": ["\ud800"],
    }, ensure_ascii=True), encoding="utf-8")
    t17_dir = tmp / "t17"
    cases.append({
        "id": "T17_write_failure_no_residue", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(t17_dir),
                                  "--evidence-root", str(sur_root)]),
        "meaning": "编码失败必须 exit 2，且不得留下 0 字节结论文件或空目录",
        "expect_no_dir": str(t17_dir),
    })
    # T18：单次门运行结果损坏（存在但无法解析）→ 2，不得降级成“没跑过”
    corrupt_root = build_fake_root(tmp, "run_corrupt", status="PASS", exit_code=0,
                                   bridge_sha=bridge_now)
    (corrupt_root / "s4t26_golden_rebind_20261026_r02/replay_forward_bridge_result.json").write_text(
        "{", encoding="utf-8")
    cases.append({
        "id": "T18_corrupt_run_json_exit2", "expect": 2,
        "actual": run(RECONCILE, ["--evidence-dir", str(tmp / "t18"),
                                  "--evidence-root", str(corrupt_root)]),
        "meaning": "“读不了证据”与“门没跑过”必须区分，前者是输入错误",
    })
    # 残留检查必须在此处（仍在 tempfile 上下文内）执行，放到上下文之外会恒真失效。
    for case in cases:
        target = case.get("expect_no_dir")
        if target is not None:
            case["residue_present"] = Path(target).exists()
    return cases


def unit_checks() -> list[dict[str, object]]:
    """函数级真值表（不冒充子进程用例，单独标注）。"""
    spec = importlib.util.spec_from_file_location("reconcile_mod", RECONCILE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    rows = {
        "blocked_on_current": ({"status": "BLOCKED", "exit_code": 2,
                                "bridge_matches_current": True,
                                "checks_not_pass_or_missing": []}, False),
        "clean_pass": ({"status": "PASS", "exit_code": 0,
                        "bridge_matches_current": True,
                        "checks_not_pass_or_missing": []}, True),
        "bool_false_exit": ({"status": "PASS", "exit_code": False,
                             "bridge_matches_current": True,
                             "checks_not_pass_or_missing": []}, False),
        "string_zero_exit": ({"status": "PASS", "exit_code": "0",
                              "bridge_matches_current": True,
                              "checks_not_pass_or_missing": []}, False),
        "stale_bridge": ({"status": "PASS", "exit_code": 0,
                          "bridge_matches_current": False,
                          "checks_not_pass_or_missing": []}, False),
        "unknown_bridge": ({"status": "PASS", "exit_code": 0,
                            "checks_not_pass_or_missing": []}, False),
        "missing_check": ({"status": "PASS", "exit_code": 0,
                           "bridge_matches_current": True,
                           "checks_not_pass_or_missing": ["g"]}, False),
        "wrong_status": ({"status": "FAILED", "exit_code": 0,
                          "bridge_matches_current": True,
                          "checks_not_pass_or_missing": []}, False),
    }
    failed = []
    for name, (payload, expected) in rows.items():
        got = module.qualifies_as_gate_pass(payload)
        if got is not expected:
            failed.append({"case": name, "expected": expected, "actual": got})
    return [{"id": "T19_qualifies_as_gate_pass_truth_table",
             "kind": "function_level_truth_table",
             "rows": len(rows),
             "expect": "全部一致", "actual": "全部一致" if not failed else failed,
             "meaning": "只有 PASS+整型0+当前字节+五项检查齐备才算门通过"}]


def main() -> int:
    """执行负控并落盘。"""
    parser = argparse.ArgumentParser(description="S4-T26 检查器 fail-closed 负控")
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    if not AUDIT.is_file() or not RECONCILE.is_file() or not BRIDGE.is_file() or not REPORT.is_file():
        print("[ERROR] 脚本、桥接器或 activation report 缺失，无法运行负控")
        return 2

    out_dir = Path(args.evidence_dir)
    if not out_dir.is_absolute():
        out_dir = WORKTREE / out_dir
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[ERROR] 证据目录非空，拒绝复用 RunId：{out_dir}")
        return 2

    with tempfile.TemporaryDirectory(dir=r"D:\tmp", prefix="s4failclosed_") as tmp:
        cases = case_results(Path(tmp))
        checks = unit_checks()

    failures = []
    for case in cases:
        if case["actual"] != case["expect"]:
            failures.append(case)
            continue
        if case.get("expect_no_dir") is not None and case.get("residue_present"):
            failures.append(dict(case, actual=f"{case['actual']} 但留下了目录 {case['expect_no_dir']}"))
    if TRACE_HITS:
        failures.append({"id": "X0_no_traceback", "expect": "无 traceback",
                         "actual": TRACE_HITS})
    bad_units = [c for c in checks if c["actual"] != c["expect"]]
    verdict = "PASS" if not failures and not bad_units else "FAIL"
    exit_code = 0 if verdict == "PASS" else 1
    facts = {
        "schema_version": "s4t26_failclosed_selftest_v2",
        "task_id": "S4-T26-FAILCLOSED-SELFTEST",
        "run_id": out_dir.name,
        "checker": "verification/test_s4t26_failclosed.py",
        "checker_sha256": sha256_file(Path(__file__).resolve()),
        "generated_utc8": datetime.now(CN).isoformat(timespec="seconds"),
        "worktree": str(WORKTREE),
        "activation_report_pinned_sha256": PINNED_REPORT_SHA,
        "cases": cases,
        "unit_checks": checks,
        "failures": failures,
        "verdict": verdict,
        "exit_code": exit_code,
        "scope": "只读负控；20 项子进程用例用真实退出码证明未闭合不会被判成通过；T19 为函数级真值表",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "selftest.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [{"path": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
             for p in sorted(out_dir.iterdir()) if p.is_file()]
    (out_dir / "manifest.json").write_text(json.dumps({
        "schema_version": 1, "task_id": "S4-T26-FAILCLOSED-SELFTEST", "run_id": out_dir.name,
        "generated_utc8": facts["generated_utc8"], "verdict": verdict,
        "exit_code": exit_code, "files": files,
        "scope": "只读负控；不含推理、黄金生成或硬件操作",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{verdict}] exit={exit_code} 子进程用例={len(cases)} 函数级={len(checks)} "
          f"失败={len(failures) + len(bad_units)}")
    for c in failures:
        print(f"  - {c['id']}: expect={c['expect']} actual={c['actual']}")
    for c in bad_units:
        print(f"  - {c['id']}: {c['actual']}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"[ERROR] 输入或环境错误：{type(exc).__name__}: {exc}")
        sys.exit(2)
