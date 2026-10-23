#!/usr/bin/env python3
"""M4 残留回归：用终审批次 A 给出的 **3 条真实残留行**逐条注入，要求 C16 **必须 FAIL**。

三条残留（原文，来自 REVIEW_FINAL_A_r08.md）：
1. limitations_not_executed.json 的 not_run[7].reason：
   「当前草案 T6-S04=500ms ≥ T6-L02=300ms，M4 被 M10 遮蔽、不可达；已登记 reachability 与 U6-12，未运行任何状态机。」
2. coverage_matrix.json 的 runbook_coverage[item4].status：
   「…M4/M7 显式登记不可达，U6-12…」
3. .codex/STATE.md 的对应行：
   「- 不可达项（不计入覆盖）：B16 …、M4/`T6-S04`（U6-12）、M7（构造上）；…」

做法：把交付目录整体复制到临时目录 → 逐条改回旧措辞（一次一条）→ 在副本上跑自检 → 断言 C16 = FAIL。
退出码 0 = 三条都被捕获（且基线副本 C16 = PASS），1 = 存在未被捕获的注入（判别力不足）。
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

RESIDUALS = [
    {
        "id": "R1-limitations-not-run",
        "file": "limitations_not_executed.json",
        "residual": "当前草案 T6-S04=500ms ≥ T6-L02=300ms，M4 被 M10 遮蔽、不可达；已登记 reachability 与 U6-12，未运行任何状态机。",
    },
    {
        "id": "R2-coverage-item4",
        "file": "coverage_matrix.json",
        "residual": "DONE_WITH_PREDICATE_BINDING（M4/M7 显式登记不可达，U6-12）",
    },
    {
        "id": "R3-state-line",
        "file": ".codex/STATE.md",
        "residual": "- 不可达项（不计入覆盖）：B16 `S_DEDUP`、M4/`T6-S04`（U6-12）、M7（构造上）",
    },
]


def run_selfcheck(py: str, root: Path, work: Path, run_rel: str, out: Path) -> dict:
    command = [py, "-B", str(root / "verification/s6_g0_selfcheck.py"),
               "--json", str(work / "docs/stage6/s6a_stage6_g0_behavior_v1.json"),
               "--doc", str(work / "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md"),
               "--cases", str(work / run_rel / "hand_computed_cases.json"),
               "--upstream", str(work / run_rel / "upstream_bindings.json"),
               "--out", str(out), "--project-root", str(work),
               "--evidence-dir", str(work / run_rel), "--state", str(work / ".codex/STATE.md")]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    status, c16 = "MISSING", "MISSING"
    if out.is_file():
        data = json.loads(out.read_text(encoding="utf-8"))
        status = data.get("status")
        c16 = next((c["status"] for c in data["checks"] if c["id"] == "C16"), "MISSING")
    return {"status": status, "c16": c16, "exit_code": completed.returncode,
            "command_text": subprocess.list2cmdline(command)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--run-dir", required=True, help="相对 project-root 的 S6-A RunId 目录（源，只读）")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    # **窗口 B 修复（fail-closed）**：`--run-dir` 允许绝对/相对，但内部一律归一为**相对 project-root** 的路径，
    # 否则 `work / <绝对路径>` 会被 pathlib 丢弃左操作数，注入就会写到真实证据目录。
    run_rel_path = Path(args.run_dir)
    if run_rel_path.is_absolute():
        run_rel_path = run_rel_path.resolve().relative_to(root)
    run_rel = run_rel_path.as_posix()
    out_path = root / args.out
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name in ("docs", "verification", "src", "report/evidence"):
            src = root / name
            if src.is_dir():
                shutil.copytree(src, work / name, dirs_exist_ok=True)
        (work / ".codex").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / ".codex/STATE.md", work / ".codex/STATE.md")

        baseline = run_selfcheck(sys.executable, root, work, run_rel, out_path.parent / "baseline.json")
        results.append({"id": "baseline", "expected": "C16=PASS", "observed": baseline,
                        "verdict": "AS_EXPECTED" if baseline["c16"] == "PASS" else "UNEXPECTED"})

        for item in RESIDUALS:
            for name in ("docs", "verification", "src", "report/evidence"):
                src = root / name
                if src.is_dir():
                    shutil.copytree(src, work / name, dirs_exist_ok=True)
            shutil.copyfile(root / ".codex/STATE.md", work / ".codex/STATE.md")
            source_run = root / run_rel
            source_before = {n: hashlib.sha256((source_run / n).read_bytes()).hexdigest()
                             for n in ("coverage_matrix.json", "limitations_not_executed.json")
                             if (source_run / n).is_file()}
            if item["file"].endswith(".json"):
                target = work / run_rel / item["file"]
                obj = json.loads(target.read_text(encoding="utf-8"))
                if item["id"] == "R1-limitations-not-run":
                    obj["not_run"][7]["reason"] = item["residual"]
                else:
                    for entry in obj["runbook_coverage"]:
                        if entry.get("item") == 4:
                            entry["status"] = "DONE_WITH_PREDICATE_BINDING（M4/M7 显式登记不可达，U6-12）"
                target.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\r\n")
            else:
                target = work / ".codex/STATE.md"
                lines = target.read_text(encoding="utf-8").splitlines()
                residual = ("- 不可达项（不计入覆盖）：B16 `S_DEDUP`（`T6-A02`500 ms < `T6-K01`1000 ms）、"
                            "M4/`T6-S04`（U6-12）、M7（构造上）；见 `reachability_notes.json`。")
                for index, line in enumerate(lines):
                    if "不计入覆盖项" in line or "不可达项" in line:
                        lines[index] = residual
                        break
                else:
                    # 锚点不存在时**无条件追加**：否则注入空转 ⇒ 假通过（本轮 STATE 压缩后暴露）
                    lines.append(residual)
                target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
            # fail-closed：注入目标必须落在副本树内（否则立即中止，绝不触碰原始证据）
            if not str(target.resolve()).startswith(str(work.resolve())):
                print(f"拒绝运行：注入目标 {target} 不在副本树 {work} 内（fail-closed）")
                return 1
            source_after = {n: hashlib.sha256((source_run / n).read_bytes()).hexdigest()
                            for n in ("coverage_matrix.json", "limitations_not_executed.json")
                            if (source_run / n).is_file()}
            if source_after != source_before:
                print(f"拒绝运行：原始证据目录被改动（{item['id']}）：{source_before} -> {source_after}")
                return 1
            observed = run_selfcheck(sys.executable, root, work, run_rel,
                                     out_path.parent / f"{item['id']}.json")
            results.append({"id": item["id"], "expected": "C16=FAIL", "observed": observed,
                            "verdict": "AS_EXPECTED" if observed["c16"] == "FAIL" else "UNEXPECTED"})
    payload = {
        "schema_version": 1,
        "artifact": "m4_residual_regression",
        "source": "REVIEW_FINAL_A_r08.md 给出的 3 条真实残留行（逐条注入，要求 C16 FAIL）",
        "rule": "C16 只有在「3 条真实残留行注入后均 FAIL、且基线 PASS」成立时才可信。",
        "results": results,
        "verdict": "ALL_AS_EXPECTED" if all(r["verdict"] == "AS_EXPECTED" for r in results) else "UNEXPECTED",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"],
                      "results": [(r["id"], r["observed"].get("c16"), r["verdict"]) for r in results]}, ensure_ascii=False))
    return 0 if payload["verdict"] == "ALL_AS_EXPECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())