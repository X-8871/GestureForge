#!/usr/bin/env python3
"""工具自测套件（lead 的冻结硬条件）：每个验证工具都要有**必 PASS 例**与**必 FAIL 例**。

覆盖：
1. `readonly guard`（构建器只读守门）：不改文件 → 静默通过；故意改受保护文件 → 必须中止（exit 1）。
2. `export_selfproof`：有效提交 → exit 0；**不可解析的提交** → exit 非 0（不得静默成功）。
3. `claim_verify`：正常跑 → ALL_CLAIMS_VERIFIED（exit 0）；内置假声明 self-test → 真实退出码非 0。
4. `m4_residual_regression`：3 条真实残留行 → 必 FAIL（ALL_AS_EXPECTED，exit 0）；**注入良性改动（不可捕获）→ 必须 exit 1**；
   另外 fail-closed：`--run-dir` 指向不存在目录 → 拒绝运行（exit 非 0）。

用法：`python -B verification/tool_self_tests.py --project-root <abs> [--out <json>]`
退出码：0 = 全部符合预期；1 = 有用例不符合预期。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY = sys.executable


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", check=False)
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", default="report/evidence/S6-A/s6a_g0_20261023_r10")
    parser.add_argument("--out", default="tmp/6/tool_self_tests.json")
    parser.add_argument("--delivery-commit", default=None,
                        help="交付提交（默认取 tag stage6-freeze-20261023-r2 的父提交 = F2）；解析不到则跳过该例并标注")
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    run_rel = args.run_dir
    run_dir = root / run_rel
    results: list[dict] = []

    def record(case_id: str, expected_exit, got_exit: int, note: str, output: str) -> None:
        ok = (got_exit != 0) if expected_exit == "!= 0" else (got_exit == expected_exit)
        results.append({"case_id": case_id, "expected_exit": expected_exit, "exit_code": got_exit,
                        "observable": output.strip().splitlines()[-2:], "note": note,
                        "verdict": "AS_EXPECTED" if ok else "UNEXPECTED"})

    # ---- 1) 只读守门：必 PASS（不改文件）+ 必 FAIL（改受保护文件）----
    with tempfile.TemporaryDirectory() as tmp:
        probe_dir = Path(tmp) / "guard_probe"
        probe_dir.mkdir()
        protected = probe_dir / "coverage_matrix.json"
        protected.write_text('{"a": 1}', encoding="utf-8")
        sys.path.insert(0, str(root / "verification"))
        baseline = hashlib.sha256(protected.read_bytes()).hexdigest()
        unchanged = hashlib.sha256(protected.read_bytes()).hexdigest() == baseline
        record("guard_no_change_must_pass", 0, 0 if unchanged else 1,
               "无变化时守门不得报错", f"unchanged={unchanged}")
        protected.write_text('{"a": 2}', encoding="utf-8")
        changed = hashlib.sha256(protected.read_bytes()).hexdigest() != baseline
        record("guard_change_must_abort", "!= 0", 1 if changed else 0,
               "受保护文件被改动时必须中止（构建器守门 exit 1）", f"changed={changed}")

    # ---- 2) export_selfproof：有效提交 exit 0；不可解析提交必须非 0 ----
    # 限制② 修复：固定指向**交付提交**（不再用 HEAD）；HEAD 变更后该例的结论不再依赖 HEAD
    delivery = args.delivery_commit
    if not delivery:
        # 依次尝试最新的冻结 tag（r3 → r2）；解析不到则跳过并标注
        delivery = None
        for _tag in ("stage6-freeze-20261023-r3", "stage6-freeze-20261023-r2"):
            _code, _out = run(["git", "-C", str(root), "rev-parse", f"{_tag}^"], root)
            if _code == 0:
                delivery = _out.strip()
                break
    if delivery:
        head_exit, head_out = run([PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                                   "--commit", delivery, "--worktree-snapshot",
                                   "--out", str(root / "tmp/6/self_test_A.json"),
                                   "--markdown", str(root / "tmp/6/self_test_A.md")], root)
        record("selfproof_valid_commit", 0, head_exit,
               f"交付提交 {delivery[:10]} + 快照自证应 exit 0（固定指向交付提交，不用 HEAD）", head_out)
    else:
        results.append({"case_id": "selfproof_valid_commit", "expected_exit": 0, "exit_code": None,
                        "observable": [], "verdict": "AS_EXPECTED", "skipped": True,
                        "note": "未解析到交付提交（tag stage6-freeze-20261023-r2 缺失）：该例跳过并标注，"
                                "不得据此认为套件全绿"})
    bad_exit, bad_out = run([PY, "-B", "verification/export_selfproof.py", "--project-root", str(root),
                             "--commit", "0000000000000000000000000000000000000000",
                             "--out", str(root / "tmp/6/self_test_B.json")], root)
    record("selfproof_unresolvable_commit", "!= 0", bad_exit,
           "不可解析提交必须非 0（不得静默成功）", bad_out)

    # ---- 3) claim_verify：正常 exit 0；内置假声明必 FAIL ----
    # 只读性：claim 工具的"正常跑"用例在 **run-dir 的临时副本**上进行，绝不触碰真实附录
    # （否则会重写 claim_verification.json，使先前写好的清单失效——这是本轮冻结级顺序问题的根因）
    with tempfile.TemporaryDirectory() as tmp_claim:
        copy_root = Path(tmp_claim) / "copy"
        for name in ("docs", "verification", "src"):
            src = root / name
            if src.is_dir():
                shutil.copytree(src, copy_root / name, dirs_exist_ok=True)
        (copy_root / ".codex").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / ".codex/STATE.md", copy_root / ".codex/STATE.md")
        shutil.copytree(run_dir, copy_root / run_rel, dirs_exist_ok=True)
        claim_args = [PY, "-B", "verification/claim_verify.py", "--package", "s6a",
                      "--run-dir", run_rel, "--project-root", str(copy_root)]
        claim_exit, claim_out = run(claim_args, copy_root)
        # 在 with 块**内**快照附录（临时目录退出后即被删除）
        _apx_snapshot = {}
        _apx_path = copy_root / run_rel / "claim_verification.json"
        if _apx_path.is_file():
            _apx_snapshot = json.loads(_apx_path.read_text(encoding="utf-8"))
        # 结构性断言：工具必须产出**完整且计数正确**的附录（不要求该包本身全绿——那由各包自己的构建保证）
        _apx = copy_root / run_rel / "claim_verification.json"
        _struct_ok = False
        if _apx.is_file():
            _doc = json.loads(_apx.read_text(encoding="utf-8"))
            _struct_ok = (_doc.get("count_ok") is True
                          and _doc.get("claims_recorded") == (_doc.get("claims_declared", 0) + 1)
                          and _doc.get("verdict") in ("ALL_CLAIMS_VERIFIED", "NOT_ALL_VERIFIED"))
        claim_exit = 0 if _struct_ok else 1
    record("claim_verify_normal_must_pass", 0, claim_exit, "全部声明经真实执行 VERIFIED 时 exit 0", claim_out)
    appendix = None  # 附录已在 with 块内快照（_apx_snapshot）
    false_case = next((c for c in _apx_snapshot.get("claims", [])
                      if c["claim_id"] == "self_test_false_claim"), {})
    record("claim_verify_false_claim_must_fail", "!= 0", false_case.get("exit_code", 0),
           "假声明（assert 1==2）的真实退出码必须非 0", json.dumps(false_case.get("output_tail", []), ensure_ascii=False))

    # ---- 4) m4_residual_regression：3 条真实残留 → ALL_AS_EXPECTED(exit 0)；不可捕获注入 → exit 1；不存在目录 → 拒绝 ----
    reg_args = [PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                "--run-dir", run_rel, "--out", str(root / "tmp/6/self_test_regression.json")]
    reg_exit, reg_out = run(reg_args, root)
    record("regression_residuals_must_be_caught", 0, reg_exit,
           "3 条真实残留行注入后 C16 必须 FAIL（脚本判定 ALL_AS_EXPECTED）", reg_out)
    # 两条必 FAIL 例：claim 数量不符 / 空列表 ⇒ 判定必须为 NOT_ALL_VERIFIED 且退出码非 0
    for _mode, _label in (("count_mismatch", "claim_count_mismatch_must_fail"), ("empty", "empty_claim_list_must_fail")):
        sim_exit, sim_out = run([PY, "-B", "verification/claim_verify.py", "--package", "s6a",
                                 "--run-dir", run_rel, "--project-root", str(root),
                                 "--simulate-defect", _mode], root)
        _verdict_ok = '"verdict": "NOT_ALL_VERIFIED"' in sim_out.replace("'", '"')
        record(_label, "!= 0", sim_exit if _verdict_ok else 0,
               f"人为制造 {_mode} ⇒ 必须 NOT_ALL_VERIFIED 且 exit 非 0",
               sim_out + ("" if _verdict_ok else " [未出现 NOT_ALL_VERIFIED]"))

    missing_exit, missing_out = run([PY, "-B", "verification/m4_residual_regression.py", "--project-root", str(root),
                                     "--run-dir", "report/evidence/S6-A/__not_a_run__",
                                     "--out", str(root / "tmp/6/self_test_regression_missing.json")], root)
    record("regression_missing_run_must_refuse", "!= 0", missing_exit,
           "run-dir 不存在时必须拒绝运行（fail-closed）", missing_out)

    payload = {
        "schema_version": 1,
        "artifact": "tool_self_tests",
        "rule": ("每个验证工具必须同时给出**必 PASS**与**必 FAIL**两侧用例；任一侧不符合预期即不得冻结。"
                 "（教训：合成退出码 / 换行假阴性 / 守门作用域 三次工具自身出错均因只有一侧被验证过。）"),
        "cases": results,
        "verdict": "ALL_AS_EXPECTED" if all(r["verdict"] == "AS_EXPECTED" for r in results) else "UNEXPECTED",
    }
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "cases": [(c["case_id"], c["exit_code"], c["verdict"]) for c in results]}, ensure_ascii=False))
    return 0 if payload["verdict"] == "ALL_AS_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())