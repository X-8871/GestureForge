#!/usr/bin/env python3
"""S6-B 判别力探针：证明"预期冻结 + 断言 + 阈值参数化"三者真的能捕获缺陷。

四个探针（全部写 tmp 副本，不污染证据）：

  P1 baseline                 未改动：必须 PASS（exit 0）
  P2 expected_tampered        冻结后篡改 expected：驱动必须**拒绝运行**（exit 2）
  P3 wrong_semantics_expected 注入"NO_HAND 也能完成窗口"的错误预期：必须断言失败（exit 1）
  P4 threshold_tampered       把行为表 JSON 的 T6-S01 改成 900 ms（其余不变）：用例必须失败（exit 1），
                              证明阈值确实从 JSON 读入、未写死

用法：
    python -B verification/s6b_probe.py --run-dir report/evidence/S6-B/s6b_core_20261023_r01 \
        --project-root D:/codex-worktrees/w6
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_driver(driver: Path, root: Path, run_dir: Path, cases: Path,
               extra: list[str] | None = None) -> subprocess.CompletedProcess:
    command = [
        sys.executable, "-B", str(driver),
        "--project-root", str(root),
        "--run-dir", str(run_dir),
        "--cases", str(cases),
    ] + (extra or [])
    return subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)


def validate_baseline(case_matrix: Any, run_report: Any, driver_exit: int) -> dict[str, Any]:
    """依据用例矩阵和实际运行报告核验基线数量及通过状态。"""
    matrix_cases = case_matrix.get("cases") if isinstance(case_matrix, dict) else None
    report_cases = run_report.get("cases") if isinstance(run_report, dict) else None
    if not isinstance(matrix_cases, list) or not isinstance(report_cases, list):
        return {
            "passed": False,
            "expected_case_count": len(matrix_cases) if isinstance(matrix_cases, list) else None,
            "actual_case_count": len(report_cases) if isinstance(report_cases, list) else None,
            "reason": "用例矩阵或运行报告缺少 cases 列表",
        }

    expected_ids = [item.get("case_id") for item in matrix_cases if isinstance(item, dict)]
    actual_ids = [item.get("case_id") for item in report_cases if isinstance(item, dict)]
    failed_case_ids = []
    for index, item in enumerate(report_cases):
        if not isinstance(item, dict) or item.get("status") != "PASS":
            failed_case_ids.append(
                item.get("case_id", f"index-{index}") if isinstance(item, dict) else f"index-{index}"
            )
    expected_count = len(matrix_cases)
    actual_count = len(report_cases)
    reported_count = run_report.get("case_count")
    reasons: list[str] = []
    if any(not isinstance(case_id, str) or not case_id for case_id in expected_ids):
        reasons.append("用例矩阵包含无效 case_id")
    if len(expected_ids) != expected_count:
        reasons.append("用例矩阵包含无效用例项")
    if actual_count != expected_count:
        reasons.append(f"实际用例数 {actual_count} 与矩阵数 {expected_count} 不一致")
    if type(reported_count) is not int or reported_count != actual_count:
        reasons.append(f"报告 case_count={reported_count!r} 与实际报告行数 {actual_count} 不一致")
    if actual_ids != expected_ids:
        reasons.append("运行报告 case_id 与矩阵不一致")
    if run_report.get("status") != "PASS":
        reasons.append(f"运行报告状态为 {run_report.get('status')!r}")
    if failed_case_ids:
        reasons.append(f"未通过用例：{failed_case_ids}")
    if driver_exit != 0:
        reasons.append(f"驱动退出码为 {driver_exit}")
    return {
        "passed": not reasons,
        "expected_case_count": expected_count,
        "actual_case_count": actual_count,
        "reported_case_count": reported_count,
        "failed_case_ids": failed_case_ids,
        "reason": "基线用例数量与状态均符合预期" if not reasons else "; ".join(reasons),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-B 判别力探针")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    driver = root / "verification/s6b_run_cases.py"
    cases_src = run_dir / "cases/case_matrix.json"
    freeze_src = run_dir / "expected_freeze.json"
    behavior_src = root / "docs/stage6/s6a_stage6_g0_behavior_v1.json"
    for required in (driver, cases_src, freeze_src, behavior_src):
        if not required.is_file():
            print(f"缺少必需输入：{required}")
            return 2

    work = root / "tmp/6/S6-B" / run_dir.name / "probe"
    work.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    def record(probe_id: str, expect_exit: int, note: str, completed: subprocess.CompletedProcess,
               validation: dict[str, Any] | None = None) -> bool:
        ok = completed.returncode == expect_exit and (validation is None or validation["passed"])
        (run_dir / f"probe_{probe_id}_stdout.txt").write_text(completed.stdout, encoding="utf-8")
        result = {
            "probe_id": probe_id,
            "note": note,
            "expected_exit": expect_exit,
            "actual_exit": completed.returncode,
            "stdout_tail": completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else "",
            "verdict": "AS_EXPECTED" if ok else "UNEXPECTED",
        }
        if validation is not None:
            result["validation"] = validation
        results.append(result)
        return ok

    ok_all = True

    # P1 基线：在 evidence 目录内直接跑（不改动任何东西）
    completed = run_driver(driver, root, run_dir, cases_src)
    try:
        baseline_report = json.loads((run_dir / "run_report.json").read_text(encoding="utf-8"))
        baseline_matrix = json.loads(cases_src.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        baseline_report = None
        baseline_matrix = None
        baseline_report_error = f"无法读取基线用例矩阵或运行报告：{exc}"
    else:
        baseline_report_error = ""
    baseline_check = validate_baseline(
        baseline_matrix, baseline_report, completed.returncode
    )
    if baseline_report_error:
        baseline_check["passed"] = False
        baseline_check["reason"] = baseline_report_error
    expected_count = baseline_check["expected_case_count"]
    actual_count = baseline_check["actual_case_count"]
    baseline_note = f"基线：矩阵 {expected_count} 例，报告 {actual_count} 例；{baseline_check['reason']}"
    ok_all &= record("baseline", 0, baseline_note, completed, baseline_check)

    # P2 冻结后篡改 expected → 拒绝运行
    probe2 = work / "expected_tampered"
    probe2.mkdir(parents=True, exist_ok=True)
    cases2 = json.loads(cases_src.read_text(encoding="utf-8"))
    cases2["cases"][0]["expected"]["final_state"] = "IDLE"
    (probe2 / "cases").mkdir(exist_ok=True)
    (probe2 / "cases/case_matrix.json").write_text(json.dumps(cases2, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    shutil.copy(freeze_src, probe2 / "expected_freeze.json")
    completed = run_driver(driver, root, probe2, probe2 / "cases/case_matrix.json")
    ok_all &= record("expected_tampered", 2, "冻结后修改 expected：必须拒绝运行", completed)

    # P3 注入"NO_HAND 也能完成窗口"的错误预期 → 断言失败
    probe3 = work / "wrong_semantics"
    (probe3 / "cases").mkdir(parents=True, exist_ok=True)
    cases3 = json.loads(cases_src.read_text(encoding="utf-8"))
    wrong = {
        "case_id": "X-wrong-nohand-window",
        "matrix_class": "探针：错误语义",
        "description": "错误预期：零框（NO_HAND）也能完成稳定窗口并触发（违反 H-4/B17）。",
        "events": [{"kind": "E_FRAME_RESULT", "frame_id": fid, "dt_ns": 0 if fid == 1 else 100_000_000,
                    "state": "NO_HAND", "detections": []} for fid in range(1, 9)],
        "expected": {"final_state": "COOLDOWN", "transitions": ["M3", "M5"],
                     "action_summary": {"action_submitted": 1}},
    }
    cases3["cases"] = cases3["cases"][:1] + [wrong]
    (probe3 / "cases/case_matrix.json").write_text(json.dumps(cases3, ensure_ascii=False, indent=2) + "\n",
                                                   encoding="utf-8")
    frozen3 = run_driver(driver, root, probe3, probe3 / "cases/case_matrix.json",
                         extra=["--freeze-only", "--force-freeze"])
    if frozen3.returncode != 0:
        print(f"P3 冻结失败：{frozen3.stdout}")
        return 1
    completed = run_driver(driver, root, probe3, probe3 / "cases/case_matrix.json")
    ok_all &= record("wrong_semantics_expected", 1, "错误预期（NO_HAND 完成窗口）：必须断言失败", completed)

    # P4 篡改阈值 JSON（T6-S02=99）→ 用例失败，证明阈值未写死
    probe4 = work / "threshold_tampered"
    (probe4 / "cases").mkdir(parents=True, exist_ok=True)
    shutil.copy(cases_src, probe4 / "cases/case_matrix.json")
    # N-09 起，冻结文件与用例文件哈希绑定到其所在路径；探针目录必须重新冻结，
    # 否则会在「用例文件哈希」这一层被拒（exit 2），测不到阈值篡改的判别力（exit 1）。
    frozen4 = run_driver(driver, root, probe4, probe4 / "cases/case_matrix.json",
                         extra=["--freeze-only", "--force-freeze"])
    if frozen4.returncode != 0:
        print(f"P4 冻结失败：{frozen4.stdout}")
        return 1
    behavior = json.loads(behavior_src.read_text(encoding="utf-8"))
    for item in behavior["parameters"]:
        if item["id"] == "T6-S01":
            # 取一个 ParamPack 允许范围内的值（99 会被装载校验直接拒载，退化为 exit 2 而测不到判别力）
            item["draft_value"] = 900.0
            item["draft_source"] = "探针：临时篡改（仅 tmp 副本）"
    tampered = probe4 / "behavior_tampered.json"
    tampered.write_text(json.dumps(behavior, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    completed = run_driver(driver, root, probe4, probe4 / "cases/case_matrix.json",
                           extra=["--behavior-json", str(tampered)])
    ok_all &= record("threshold_tampered", 1, "T6-S01 篡改为 900 ms：用例必须失败（阈值确实来自 JSON）", completed)

    summary = {
        "schema_version": 1,
        "artifact": "s6b_discrimination_probe",
        "task_id": "S6-B",
        "run_id": run_dir.name,
        "purpose": "证明预期冻结（H-7）、断言判别力与阈值参数化（不写死）三者可被实测验证",
        "results": results,
        "scope_statement": "探针只证明测试机制有判别力，不代表状态机行为正确、独立审查或实物验收通过。",
    }
    (run_dir / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                                encoding="utf-8")
    print(json.dumps({"status": "PROBE_OK" if ok_all else "PROBE_FAILED",
                      "results": [(r["probe_id"], r["actual_exit"], r["verdict"]) for r in results]},
                     ensure_ascii=False))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
