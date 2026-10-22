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

    def record(probe_id: str, expect_exit: int, note: str, completed: subprocess.CompletedProcess) -> bool:
        ok = completed.returncode == expect_exit
        (run_dir / f"probe_{probe_id}_stdout.txt").write_text(completed.stdout, encoding="utf-8")
        results.append({
            "probe_id": probe_id,
            "note": note,
            "expected_exit": expect_exit,
            "actual_exit": completed.returncode,
            "stdout_tail": completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else "",
            "verdict": "AS_EXPECTED" if ok else "UNEXPECTED",
        })
        return ok

    ok_all = True

    # P1 基线：在 evidence 目录内直接跑（不改动任何东西）
    completed = run_driver(driver, root, run_dir, cases_src)
    ok_all &= record("baseline", 0, "未改动：23 例全部通过", completed)

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