#!/usr/bin/env python3
"""工具自测套件（冻结硬条件）：每个验证工具都要有**必 PASS 例**与**必 FAIL 例**。

覆盖（r13 收紧版，对应 FREEZE_DELTA_E §七.4 与任务 A7②③）：
1. `readonly guard`（构建器只读守门）：**真实调用** `s6a_build_evidence._guard_check` ——
   不改文件 → 静默通过；故意改受保护文件 → 必须中止（exit 1）。
2. `export_selfproof`：**交付提交**自证 → exit 0；**工作区快照**自证 → exit 0；
   **不可解析的提交** → exit 非 0（不得静默成功）。BLK-D1 之后 `--s6a-run` 为必填，凡调用一律显式传入。
3. `claim_verify`（按 `--package` 选 S6-A/S6-B 声明集）：正常跑 → ALL_CLAIMS_VERIFIED（exit 0）；
   内置假声明 self-test → 真实退出码非 0。两条「数量不符 / 空列表」必 FAIL 例**只在临时副本内**运行
   （A7②：绝不改写真实 run-dir 的冻结附录）。
4. `m4_residual_regression`：3 条真实残留行 → 必 FAIL；`--run-dir` 不存在 → 拒绝。
5. `approved_package_scan`：**两向自测** —— B1..B7 必判失败形态全部命中、C1..C4 必须放行对照全部不命中。

新增（A7③）：`skipped` **不得计绿**。任一侧例被跳过（无法解析交付提交等）时总判定为
`INCOMPLETE_SKIPPED` 且退出码非 0；只有全部用例非跳过且符合预期才是 `ALL_AS_EXPECTED`。
`--simulate-skip` 是这条规则的**必 FAIL 自测**：人为把一例置为跳过，总判定必须变红。

用法：
    python -B verification/tool_self_tests.py --project-root <abs> --run-dir <rel> \
        --package s6a|s6b [--s6a-run <rel>] [--s6b-run <rel>] [--out <json>]
退出码：0 = 全部符合预期且无跳过；1 = 有不符合预期或有跳过；2 = 输入不合法。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY = sys.executable


def claim_normal_ok(exit_code: int, payload: dict) -> bool:
    """正常声明必须真实成功；结构完整不能替代声明验证通过。"""
    claims = payload.get("claims", [])
    declared = payload.get("claims_declared")
    return (exit_code == 0 and payload.get("verdict") == "ALL_CLAIMS_VERIFIED"
            and payload.get("count_ok") is True and isinstance(declared, int)
            and declared > 0 and payload.get("claims_recorded") == declared + 1
            and len(claims) == declared + 1
            and len({c.get("claim_id") for c in claims}) == len(claims)
            and all(c.get("verdict") == "VERIFIED" and not c.get("readonly_violation")
                    and type(c.get("exit_code")) is int
                    and (c.get("exit_code") != 0 if c.get("claim_id") == "self_test_false_claim"
                         else c.get("exit_code") == c.get("expected_exit") == 0)
                    for c in claims)
            and sum(c.get("claim_id") == "self_test_false_claim" for c in claims) == 1)

# 冻结 tag 的**父提交** = 该轮交付内容（F 段）；从新到旧依次尝试
DELIVERY_CANDIDATES = (
    ("stage6-freeze-20261023-r6", "report/evidence/S6-A/s6a_g0_20261023_r12",
     "report/evidence/S6-B/s6b_core_20261023_r07"),
    ("stage6-freeze-20261023-r5", "report/evidence/S6-A/s6a_g0_20261023_r11",
     "report/evidence/S6-B/s6b_core_20261023_r06"),
)


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def make_temp_copy(root: Path, run_rel: str, tmp: Path) -> Path:
    """把工具运行所需的只读输入 + run-dir 复制到隔离临时树（A7②）。"""
    copy_root = tmp / "copy"
    for name in ("docs", "verification", "src"):
        src = root / name
        if src.is_dir():
            shutil.copytree(src, copy_root / name, dirs_exist_ok=True)
    (copy_root / ".codex").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / ".codex/STATE.md", copy_root / ".codex/STATE.md")
    shutil.copytree(root / run_rel, copy_root / run_rel, dirs_exist_ok=True)
    # C11 还核对 STATE 中明确引用的兄弟证据；隔离副本必须保留这些输入，不能删去其核对。
    state_text = (root / ".codex/STATE.md").read_text(encoding="utf-8")
    for token in re.findall(r"`(report/evidence/[^`]+)`", state_text):
        source = root / token.rstrip("/")
        target = copy_root / token.rstrip("/")
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return copy_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", required=True, help="被检 RunId（相对 project-root；只读，全部写入走临时副本）")
    parser.add_argument("--package", choices=["s6a", "s6b"], required=True)
    parser.add_argument("--out", default="tmp/6/tool_self_tests.json")
    parser.add_argument("--s6a-run", default=None, help="S6-A 证据目录（自证必填项）")
    parser.add_argument("--s6b-run", default=None, help="S6-B 证据目录（提供时自证兼跑 S6-B 剖面）")
    parser.add_argument("--delivery-commit", default=None, help="交付提交（默认取最新冻结 tag 的父提交）")
    parser.add_argument("--delivery-s6a-run", default=None)
    parser.add_argument("--delivery-s6b-run", default=None)
    parser.add_argument("--simulate-skip", action="store_true",
                        help="必 FAIL 自测：人为把一例置为跳过，总判定必须为 INCOMPLETE_SKIPPED 且 exit 非 0")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    run_rel = args.run_dir
    run_dir = root / run_rel
    if not run_dir.is_dir():
        print(f"RunId 目录不存在：{run_dir}")
        return 2
    s6a_run = args.s6a_run or (run_rel if args.package == "s6a" else None)
    s6b_run = args.s6b_run or (run_rel if args.package == "s6b" else None)
    if not s6a_run:
        print("S6-A 剖面必须给出 --s6a-run（BLK-D1 之后不再隐式查找）")
        return 2
    results: list[dict] = []

    def record(case_id: str, expected_exit, got_exit, note: str, output: str,
               skipped: bool = False) -> None:
        if skipped:
            results.append({"case_id": case_id, "expected_exit": expected_exit, "exit_code": None,
                            "observable": [], "note": note, "verdict": "AS_EXPECTED", "skipped": True})
            return
        ok = (got_exit != 0) if expected_exit == "!= 0" else (got_exit == expected_exit)
        results.append({"case_id": case_id, "expected_exit": expected_exit, "exit_code": got_exit,
                        "observable": output.strip().splitlines()[-2:], "note": note,
                        "verdict": "AS_EXPECTED" if ok else "UNEXPECTED"})

    def proof_argv(extra: list[str]) -> list[str]:
        argv_ = [PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                 "--s6a-run", s6a_run]
        if s6b_run:
            argv_ += ["--s6b-run", s6b_run]
        return argv_ + extra

    # ---- 1) 只读守门：**真实调用**构建器守门函数 ----
    with tempfile.TemporaryDirectory() as tmp:
        probe_dir = Path(tmp) / "guard_probe"
        probe_dir.mkdir()
        protected = probe_dir / "coverage_matrix.json"
        protected.write_text('{"a": 1}', encoding="utf-8")
        sys.path.insert(0, str(root / "verification"))
        import s6a_build_evidence as builder  # noqa: E402
        builder._guard_init(probe_dir)
        no_change_exit = 0
        try:
            builder._guard_check("no_change")
        except SystemExit as exc:
            no_change_exit = int(exc.code or 0)
        record("guard_no_change_must_pass", 0, no_change_exit,
               "无变化时守门不得报错（真实调用 _guard_check）", f"exit={no_change_exit}")
        protected.write_text('{"a": 2}', encoding="utf-8")
        changed_exit = 0
        try:
            builder._guard_check("changed")
        except SystemExit as exc:
            changed_exit = int(exc.code or 0)
        record("guard_change_must_abort", "!= 0", changed_exit,
               "受保护文件被改动时守门必须中止（真实调用 _guard_check，exit 1）", f"exit={changed_exit}")

    # ---- 2) export_selfproof：交付提交 / 工作区快照 / 不可解析提交 ----
    delivery = args.delivery_commit
    delivery_s6a = args.delivery_s6a_run
    delivery_s6b = args.delivery_s6b_run
    if not delivery or not delivery_s6a:
        for tag, d_s6a, d_s6b in DELIVERY_CANDIDATES:
            code, out = run(["git", "-C", str(root), "rev-parse", f"{tag}^"], root)
            if code == 0:
                delivery = delivery or out.strip()
                delivery_s6a = delivery_s6a or d_s6a
                delivery_s6b = delivery_s6b or d_s6b
                break
    if args.simulate_skip:
        record("selfproof_delivery_commit_must_pass", 0, 0,
               "【必 FAIL 自测】人为置为跳过（不由任何实际运行得出）", "simulated skip", skipped=True)
    elif delivery and delivery_s6a:
        argv_d = [PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                  "--commit", delivery, "--s6a-run", delivery_s6a]
        if delivery_s6b:
            argv_d += ["--s6b-run", delivery_s6b]
        argv_d += ["--out", str(root / "tmp/6/self_test_delivery.json")]
        code, out = run(argv_d, root)
        record("selfproof_delivery_commit_must_pass", 0, code,
               f"交付提交 {delivery[:10]} 自证应 exit 0（显式 --s6a-run {delivery_s6a}）", out)
    else:
        record("selfproof_delivery_commit_must_pass", 0, 0,
               f"未解析到交付提交（尝试 {[c[0] for c in DELIVERY_CANDIDATES]}）⇒ 该例跳过，"
               "总判定必须为 INCOMPLETE_SKIPPED", "", skipped=True)

    code, out = run(proof_argv(["--worktree-snapshot", "--out", str(root / "tmp/6/self_test_snapshot.json")]), root)
    record("selfproof_worktree_snapshot_must_pass", 0, code,
           f"当前工作区快照自证应 exit 0（--s6a-run {s6a_run}" + (f" --s6b-run {s6b_run}" if s6b_run else "") + "）", out)

    code, out = run(proof_argv(["--commit", "0000000000000000000000000000000000000000",
                                "--out", str(root / "tmp/6/self_test_bad.json")]), root)
    record("selfproof_unresolvable_commit", "!= 0", code,
           "不可解析提交必须非 0（不得静默成功）", out)

    # ---- 3) claim_verify：正常 exit 0；内置假声明必 FAIL；数量/空列表必 FAIL 例在临时副本内 ----
    with tempfile.TemporaryDirectory() as tmp_claim:
        copy_root = make_temp_copy(root, run_rel, Path(tmp_claim))
        claim_args = [PY, "-B", "verification/claim_verify.py", "--package", args.package,
                      "--run-dir", run_rel, "--project-root", str(copy_root)]
        claim_exit, claim_out = run(claim_args, copy_root)
        _apx_snapshot: dict = {}
        _apx = copy_root / run_rel / "claim_verification.json"
        if _apx.is_file():
            _apx_snapshot = json.loads(_apx.read_text(encoding="utf-8"))
        record("claim_verify_normal_must_pass", 0, claim_exit,
               f"全部声明经真实执行 VERIFIED 时 exit 0（package={args.package}）", claim_out)
        results[-1]["claims_verified"] = claim_normal_ok(claim_exit, _apx_snapshot)
        results[-1]["claim_verification"] = _apx_snapshot
        pair = copy_root / run_rel / "fresh_selfcheck_pair.json"
        if pair.is_file():
            results[-1]["fresh_selfcheck_pair"] = json.loads(pair.read_text(encoding="utf-8"))
        if not results[-1]["claims_verified"]:
            results[-1]["verdict"] = "UNEXPECTED"
        # 与真实命令分开记录：这个反例专门证明结构正确的失败声明不能被正常例接受。
        failed_claim = {"count_ok": True, "claims_declared": 1, "claims_recorded": 2,
                        "verdict": "NOT_ALL_VERIFIED", "claims": [
                            {"claim_id": "probe", "verdict": "NOT_VERIFIED", "exit_code": 1,
                             "expected_exit": 0},
                            {"claim_id": "self_test_false_claim", "verdict": "VERIFIED", "exit_code": 1}]}
        rejected = not claim_normal_ok(1, failed_claim) and not claim_normal_ok(0, failed_claim)
        results.append({"case_id": "claim_structurally_valid_failure_must_reject",
                        "expected": "REJECT", "exit_code": None, "kind": "predicate_counterexample",
                        "input": failed_claim, "rejected": rejected,
                        "note": "真实退出码 1 与不一致的退出码 0 两种输入均必须拒绝；非 subprocess 用例",
                        "verdict": "AS_EXPECTED" if rejected else "UNEXPECTED"})

        with tempfile.TemporaryDirectory() as tmp_sim:
            sim_root = make_temp_copy(root, run_rel, Path(tmp_sim))
            for _mode, _label in (("count_mismatch", "claim_count_mismatch_must_fail"),
                                  ("empty", "empty_claim_list_must_fail")):
                sim_exit, sim_out = run([PY, "-B", "verification/claim_verify.py", "--package", args.package,
                                        "--run-dir", run_rel, "--project-root", str(sim_root),
                                        "--simulate-defect", _mode], sim_root)
                _verdict_ok = '"verdict": "NOT_ALL_VERIFIED"' in sim_out.replace("'", '"')
                record(_label, "!= 0", sim_exit if _verdict_ok else 0,
                       f"人为制造 {_mode} ⇒ 必须 NOT_ALL_VERIFIED 且 exit 非 0（仅在临时副本内运行）",
                       sim_out + ("" if _verdict_ok else " [未出现 NOT_ALL_VERIFIED]"))
    false_case = next((c for c in _apx_snapshot.get("claims", [])
                       if c["claim_id"] == "self_test_false_claim"), {})
    record("claim_verify_false_claim_must_fail", "!= 0", false_case.get("exit_code", 0),
           "假声明（assert 1==2）的真实退出码必须非 0", json.dumps(false_case.get("output_tail", []), ensure_ascii=False))

    # ---- 4) m4_residual_regression（**S6-A 专用**：注入点在其人工输入内，故一律用 --s6a-run 目录）----
    reg_exit, reg_out = run([PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                             "--run-dir", s6a_run, "--out", str(root / "tmp/6/self_test_regression.json")], root)
    record("regression_residuals_must_be_caught", 0, reg_exit,
           "3 条真实残留行注入后 C16 必须 FAIL（脚本判定 ALL_AS_EXPECTED）", reg_out)
    missing_exit, missing_out = run([PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                                     "--run-dir", "report/evidence/S6-A/__not_a_run__",
                                     "--out", str(root / "tmp/6/self_test_regression_missing.json")], root)
    record("regression_missing_run_must_refuse", "!= 0", missing_exit,
           "run-dir 不存在时必须拒绝运行（fail-closed）", missing_out)

    # ---- 5) approved_package_scan：两向自测（B1..B7 必命中 / C1..C4 必放行）----
    scan_exit, scan_out = run([PY, "-B", "verification/approved_package_scan.py", "--project-root", str(root),
                               "--run-dir", run_rel, "--inject-self-test",
                               "--out", str(root / "tmp/6/self_test_scan.json")], root)
    record("approval_scan_counterexamples_must_fail", 0, scan_exit,
           "B1..B7 必判失败形态全部被捕获、C1..C4 必须放行对照全部不命中（exit 0 = AS_EXPECTED）", scan_out)

    unexpected = [c["case_id"] for c in results if c["verdict"] != "AS_EXPECTED"]
    skipped = [c["case_id"] for c in results if c.get("skipped")]
    verdict = ("UNEXPECTED" if unexpected else
               "INCOMPLETE_SKIPPED" if skipped else "ALL_AS_EXPECTED")

    payload = {
        "schema_version": 1,
        "artifact": "tool_self_tests",
        "task_id": "S6-A" if args.package == "s6a" else "S6-B",
        "run_id": run_dir.name,
        "package": args.package,
        "rule": ("每个验证工具必须同时给出**必 PASS**与**必 FAIL**两侧用例；任一侧不符合预期即不得冻结。"
                 "**跳过（skipped）不得计绿**：存在跳过时总判定为 INCOMPLETE_SKIPPED 且退出码非 0。"
                 "（教训：合成退出码 / 换行假阴性 / 守门作用域 / 空转 skipped / 缺 --s6a-run 数次工具自身出错，"
                 "均因只有一侧被验证过。）"),
        "cases": results,
        "unexpected": unexpected,
        "skipped_cases": skipped,
        "verdict": verdict,
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "cases": [(c["case_id"], c["exit_code"], c["verdict"], bool(c.get("skipped")))
                                for c in results]}, ensure_ascii=False))
    if args.simulate_skip:
        as_expected = verdict == "INCOMPLETE_SKIPPED"
        print(json.dumps({"simulate_skip_verdict": verdict, "as_expected": as_expected}, ensure_ascii=False))
        return 0 if as_expected else 1
    return 0 if verdict == "ALL_AS_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
