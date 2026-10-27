#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 阶段4 冻结包离线消费**证据包驱动**：产出 report/evidence/S5-T03/<RunId>/。

流程（每步都记录**真实退出码**）
================================
1. 完整性复算 CLI（逐文件 sha256+bytes、契约绑定、upstream_bindings 漂移）
2. 消费者 CLI（冻结包 → 逐帧输入 + 标签 + 五元组 + 门禁几何投影）
3. 独立对拍检查器 CLI（逐框 xyxy_px verdict + 标签/时间口径）
4. 回归套件：既有 7 个 `test_s5t03_*` 模块 + 本任务新增测试模块

诚实边界
========
- 只做离线回放消费；不接板卡、不起 vivado/xsdb/hw_server/vitis/xsim、不终止任何进程。
- `summary.md` 的每个数字均由本包产物派生（现场解析 JSON），不手写未复算的数字。
- 结论范围：离线回放口径的数值一致性；**不含**板上真实回放、UART 实收、真实采集质量，
  也不构成 P/4-D/G3/G4/G5 任何关口判定。
"""

from __future__ import annotations

import argparse
import json
import platform
import pathlib
import subprocess
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.stage5_t03.s5t03_freeze_integrity as FI  # noqa: E402
import scripts.stage5_t03.s5t03_stage4_frozen_replay as C  # noqa: E402

SUITE_MODULES = [
    "scripts.stage5_t03.test_s5t03_json_contract_malformed",
    "scripts.stage5_t03.test_s5t03_hud_occlusion",
    "scripts.stage5_t03.test_s5t03_json_contract",
    "scripts.stage5_t03.test_s5t03_multi_geometry_render",
    "scripts.stage5_t03.test_s5t03_long_run_replay",
    "scripts.stage5_t03.test_s5t03_replay_display",
    "scripts.stage5_t03.test_s5t03_skeleton",
    "scripts.stage5_t03.test_s5t03_frozen_replay",
]


def sha256_file(path: pathlib.Path) -> str:
    return FI.sha256_file(path)


def run_step(cmd: list[str], *, log_path: pathlib.Path, cwd: pathlib.Path) -> dict:
    started = time.time()
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    elapsed = time.time() - started
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"$ {' '.join(cmd)}\n[exit code: {proc.returncode}]\n"
                        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
                        encoding="utf-8")
    return {"cmd": cmd, "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "log": log_path.name, "elapsed_s": round(elapsed, 3)}


def parse_unittest(output: str) -> dict:
    """解析 unittest 输出（**注意**：`-v` 的详细输出走 stderr，调用方须把两路合并后传入）。"""
    ran = None
    for line in output.splitlines():
        if line.startswith("Ran ") and " test" in line:
            try:
                ran = int(line.split()[1])
            except (IndexError, ValueError):
                ran = None
    tail_lines = [line for line in output.splitlines() if line.strip()]
    tail = tail_lines[-1] if tail_lines else ""
    return {"tests_ran": ran, "tail": tail, "ok": tail.startswith("OK"),
            "failed": "FAILED" in output}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S5-T03 冻结回放离线消费证据包驱动（不接板卡）")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--package-dir", default=str(C.DEFAULT_PACKAGE_DIR))
    parser.add_argument("--freeze-record", default=str(C.DEFAULT_FREEZE_RECORD))
    parser.add_argument("--contract", default=str(C.DEFAULT_CONTRACT))
    parser.add_argument("--out-root", default=str(REPO_ROOT / "report" / "evidence" / "S5-T03"))
    parser.add_argument("--skip-suite", action="store_true")
    parser.add_argument("--supersedes-run-id", default=None,
                        help="被本 RunId 取代的失败 RunId（登记取代关系，不改写其目录）")
    parser.add_argument("--supersedes-reason", default=None)
    args = parser.parse_args(argv)

    ev = pathlib.Path(args.out_root) / args.run_id
    if ev.exists():
        print(f"[evidence] 拒绝覆盖既有 RunId 目录：{ev}")
        return 2
    console = ev / "console"
    console.mkdir(parents=True, exist_ok=True)
    tmp_dir = REPO_ROOT / "tmp" / "5" / "S5-T03" / args.run_id
    tmp_dir.mkdir(parents=True, exist_ok=True)

    py = [sys.executable, "-B"]
    steps: dict[str, dict] = {}

    steps["freeze_integrity"] = run_step(
        py + ["scripts/stage5_t03/s5t03_freeze_integrity.py",
              "--freeze-record", args.freeze_record, "--package-dir", args.package_dir,
              "--contract", args.contract, "--out", str(tmp_dir / "freeze_integrity_cli.json")],
        log_path=console / "freeze_integrity.txt", cwd=REPO_ROOT)

    steps["consumer"] = run_step(
        py + ["scripts/stage5_t03/s5t03_stage4_frozen_replay.py", "--out", str(ev),
              "--package-dir", args.package_dir, "--freeze-record", args.freeze_record,
              "--contract", args.contract],
        log_path=console / "consumer.txt", cwd=REPO_ROOT)

    steps["crosscheck"] = run_step(
        py + ["scripts/stage5_t03/check_s5t03_frozen_replay.py", "--artifacts", str(ev),
              "--package-dir", args.package_dir, "--freeze-record", args.freeze_record,
              "--contract", args.contract, "--out", str(ev / "crosscheck_report.json")],
        log_path=console / "crosscheck.txt", cwd=REPO_ROOT)

    if not args.skip_suite:
        steps["unittest"] = run_step(py + ["-m", "unittest", "-v"] + SUITE_MODULES,
                                     log_path=console / "unittest_all.txt", cwd=REPO_ROOT)
        (console / "suite_command.txt").write_text(" ".join(SUITE_MODULES) + "\n", encoding="utf-8")

    # ── 现场解析产物（summary 的每个数字都由此派生）───────────────────────────
    frames_payload = json.loads((ev / "frames.json").read_text(encoding="utf-8"))
    gate_payload = json.loads((ev / "gate_evidence_projection.json").read_text(encoding="utf-8"))
    consumer_report = json.loads((ev / "consumer_report.json").read_text(encoding="utf-8"))
    integrity = json.loads((ev / "freeze_integrity.json").read_text(encoding="utf-8"))
    crosscheck = json.loads((ev / "crosscheck_report.json").read_text(encoding="utf-8"))
    five_tuples = [json.loads(line) for line in
                   (ev / "five_tuples.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    drift = integrity["upstream_binding_drift"]
    box = crosscheck["box_crosscheck"]
    derived = {
        "file_integrity_ok": integrity["file_integrity"]["ok"],
        "file_integrity_checked": integrity["file_integrity"]["checked"],
        "contract_json_sha256": integrity["contract_binding_check"]["json_actual_sha256"],
        "contract_binding_all_pass": integrity["contract_binding_check"]["all_pass"],
        "drift_ok": drift.get("ok"), "drift_checked": drift.get("checked"),
        "frames": frames_payload["frame_count"],
        "frame_detections": sum(len(f["detections"]) for f in frames_payload["frames"]),
        "frame_states": {f["state"]: sum(1 for g in frames_payload["frames"] if g["state"] == f["state"])
                         for f in frames_payload["frames"]},
        "five_tuples": len(five_tuples),
        "gate_boxes": gate_payload["box_count"],
        "boxes_checked": box["boxes_checked"], "axes_checked": box["axes_checked"],
        "box_mismatches": box["box_mismatches"],
        "labels": {"input_kind": consumer_report["input_kind"],
                   "consumption_mode": consumer_report["consumption_mode"],
                   "evidence_kind": consumer_report["evidence_kind"]},
        "crosscheck_verdict": crosscheck["verdict"],
        "suite_exit_code": steps.get("unittest", {}).get("exit_code"),
        "suite_parse": parse_unittest((steps.get("unittest", {}).get("stdout", "") + "\n"
                                       + steps.get("unittest", {}).get("stderr", ""))),
    }

    summary_lines = [
        f"# S5-T03 阶段4 冻结包离线消费（RunId `{args.run_id}`）",
        "",
        "> 范围：离线主机回放；不代表 PL、实物或实时检测输出。"
        "板上真实回放仍需硬件 OFFER/CLAIM + 八类门禁（当前 0/8）。",
        "",
        "## 结论（全部由本包产物派生）",
        "",
        f"- 冻结包逐文件复算：sha256+bytes **{derived['file_integrity_ok']}/{derived['file_integrity_checked']} PASS**"
        f"（`freeze_integrity.json`）。",
        f"- 契约绑定：`{derived['contract_json_sha256']}`，与冻结记录一致 = "
        f"**{derived['contract_binding_all_pass']}**。",
        f"- `upstream_bindings` 漂移现场复算：**{derived['drift_ok']}/{derived['drift_checked']} PASS**。",
        f"- 逐帧输入：{derived['frames']} 帧（状态 {derived['frame_states']}），"
        f"回放帧检测框 {derived['frame_detections']} 个；显示五元组 {derived['five_tuples']} 条。",
        f"- 输入口径标签：`input_kind={derived['labels']['input_kind']}`、"
        f"`consumption_mode={derived['labels']['consumption_mode']}`、"
        f"`evidence_kind={derived['labels']['evidence_kind']}`（已覆盖既有 `synthetic_replay`）。",
        f"- 独立对拍（`xyxy_px` 逐框 vs 检查器从冻结包重算）："
        f"**{box['boxes_checked']} 框 / {box['axes_checked']} 轴，mismatch={box['box_mismatches']}，"
        f"verdict={box['verdict']}**；门禁样本框 {derived['gate_boxes']} 个。",
        f"- 对拍总分节：labels={crosscheck['labels']['verdict']}、"
        f"frame_records={crosscheck['frame_records']['verdict']}、"
        f"five_tuples={crosscheck['five_tuples']['verdict']}、"
        f"package_consistency={crosscheck['package_consistency']['verdict']}；"
        f"总 verdict={derived['crosscheck_verdict']}。",
        "",
        "## 命令与真实退出码",
        "",
        "| 步骤 | 命令 | 真实退出码 | 日志 |",
        "|---|---|---|---|",
    ]
    for name, step in steps.items():
        summary_lines.append(f"| {name} | `{' '.join(step['cmd'])}` | {step['exit_code']} | "
                             f"`console/{step['log']}` |")
    summary_lines += [
        "",
        f"回归套件：{len(SUITE_MODULES)} 个模块（既有 7 + 新增 1），"
        f"解析 `Ran {derived['suite_parse']['tests_ran']}` 例、OK={derived['suite_parse']['ok']}、"
        f"FAILED={derived['suite_parse']['failed']}。",
        "",
        "## 时间口径（冻结件陷阱处理）",
        "",
        f"- `capture_time_ns` 基准 = `{consumer_report['timing']['capture_time_ns_basis']}`"
        "（冻结包已文档化的秒级墙钟抓取时刻，**非** PS 单调采集计数）。",
        f"- `result_time_ns` / `end_to_end_latency_ns` / 两个 `age_*_ns` 均**不可定义**"
        f"（`stale_evaluation={consumer_report['timing']['stale_evaluation']}`）；未伪造年龄或延迟。",
        "- `injection_start_ns` **未**被当作采集时间（`injection_start_ns_used_as_capture_time=false`）；"
        "`FILE_INJECTION` 的 0 哨兵路径由检查器与判别力用例覆盖。",
        "",
        "## 限制与 NOT_RUN",
        "",
    ]
    summary_lines += [f"- {item}" for item in consumer_report["limitations"]]
    summary_lines += [f"- NOT_RUN：{item}" for item in consumer_report["not_run"]]
    summary_lines += [
        "",
        "## 诚实边界声明",
        "",
        "- 允许声明：离线回放口径下的数值一致性；task-27 结果包可被阶段5 消费。",
        "- 禁止声明：板上行为/PL 真实运行、UART 实收/真帧、真实摄像头采集质量或颜色、"
        "P/4-D/G3/G4/G5 任一项通过、把回放结果当实时结果。",
        "- §4.5/§7.3 未关闭；G0/G1/G3/G4/G5 判定不归本任务。",
        "",
    ]
    (ev / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    source_files = ["scripts/stage5_t03/s5t03_freeze_integrity.py",
                    "scripts/stage5_t03/s5t03_stage4_frozen_replay.py",
                    "scripts/stage5_t03/check_s5t03_frozen_replay.py",
                    "scripts/stage5_t03/run_s5t03_frozen_replay_evidence.py",
                    "scripts/stage5_t03/test_s5t03_frozen_replay.py",
                    "verification/s5_display_geometry_reference.py",
                    "docs/stage5/S5T03_stage4_frozen_replay_consumption_v1.md"]
    frozen_inputs = [{"path": r["path"], "sha256": r["actual_sha256"], "bytes": r["actual_bytes"],
                      "verdict": r["verdict"]} for r in integrity["file_integrity"]["records"]]
    manifest = {
        "schema_version": "gestureforge_s5t03_frozen_replay_evidence_v1",
        "run_id": args.run_id,
        "task_id": "S5-T03",
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "goal": "阶段4 冻结回放包 → 阶段5 显示路径的离线消费（可机检）",
        "input_kind": C.INPUT_KIND, "consumption_mode": C.CONSUMPTION_MODE,
        "evidence_kind": C.EVIDENCE_KIND,
        "scope_statement": C.SCOPE_STATEMENT,
        "verdict": {
            "file_integrity": f"{derived['file_integrity_ok']}/{derived['file_integrity_checked']} PASS",
            "contract_binding": derived["contract_binding_all_pass"],
            "upstream_binding_drift": f"{derived['drift_ok']}/{derived['drift_checked']} PASS",
            "consumer": "PASS" if steps["consumer"]["exit_code"] == 0 else "FAIL",
            "crosscheck": derived["crosscheck_verdict"],
            "regression_suite_exit_code": derived["suite_exit_code"],
            "regression_suite_tests_ran": derived["suite_parse"]["tests_ran"],
            "regression_suite_ok": derived["suite_parse"]["ok"],
        },
        "commands": {name: {"cmd": step["cmd"], "exit_code": step["exit_code"], "log": step["log"],
                            "elapsed_s": step["elapsed_s"]} for name, step in steps.items()},
        "sources": [{"path": rel, "sha256": sha256_file(REPO_ROOT / rel)} for rel in source_files
                    if (REPO_ROOT / rel).is_file()],
        "frozen_inputs": {
            "package_dir": args.package_dir, "freeze_record": args.freeze_record,
            "freeze_record_sha256": integrity["freeze_record_sha256"],
            "contract": args.contract, "contract_sha256": derived["contract_json_sha256"],
            "files": frozen_inputs,
        },
        "derived_numbers": derived,
        "supersedes": (None if not args.supersedes_run_id else
                       {"run_id": args.supersedes_run_id, "reason": args.supersedes_reason,
                        "note": "被取代 RunId 目录保留不改写（失败证据），不得作为消费入口"}),
        "tools": {"python": sys.version.split()[0], "platform": platform.platform(),
                  "executable": sys.executable},
        "limitations": consumer_report["limitations"],
        "not_run": consumer_report["not_run"],
        "forbidden_claims": C.FORBIDDEN_CLAIMS,
        "hardware_boundary": consumer_report["hardware_boundary"],
        "exit_codes": {name: step["exit_code"] for name, step in steps.items()},
        "artifacts": sorted(p.relative_to(ev).as_posix() for p in ev.rglob("*")
                            if p.is_file() and p.name != "manifest.json"),
    }
    (ev / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    print(f"[evidence] run_id={args.run_id} dir={ev} "
          f"consumer_exit={steps['consumer']['exit_code']} crosscheck_exit={steps['crosscheck']['exit_code']} "
          f"suite_exit={derived['suite_exit_code']}")
    failed = steps["consumer"]["exit_code"] != 0 or steps["crosscheck"]["exit_code"] != 0 or \
        steps["freeze_integrity"]["exit_code"] != 0
    if not args.skip_suite:
        failed = failed or steps["unittest"]["exit_code"] != 0
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())