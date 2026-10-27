#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T27 证据运行器：回放/彩色输入路径实现 + 离线动态显示回归（**全离线，不接板卡**）。

产出 `report/evidence/S5-T27/s5t27_replay_colour_20261027_r01/`：
- `results.json`、`frame_assertions.jsonl`、`summary.md`（回归产物，结论标注"回放/离线"）
- `replay_input_selftest.json`（输入路径实现自检：4 类必失败注入）
- `console/**`（安静窗口、git 状态、输入自检、回归原生日志、套件、检查器，含真实退出码）
- `delivery_manifest.json`、`hashes_sha256.txt`

判定：安静窗口 + 工作树无已跟踪改动 + 无 index.lock + 输入自检 exit 0 + 回归 exit 0 +
      套件 exit 0 + `check_stage_delivery --mode evidence`（M1/M2）exit 0 ⇒ 运行器 exit 0。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
for _candidate in (str(REPO_ROOT), str(REPO_ROOT / "scripts" / "stage5_t04")):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)
import run_stage5_freeze_evidence as F  # noqa: E402  （复用命令执行/哈希/安静窗口/套件摘要）

CHECKER = F.CHECKER
TASK_ID = "S5-T27"
DEFAULT_RUN_DIR = "report/evidence/S5-T27/s5t27_replay_colour_20261027_r01"
STATUS_OK = "CHECKS_OK"
BINDING = pathlib.Path("D:/codex-worktrees/dbdf/report/evidence/S3-T05/"
                       "t05_replay_binding_20261025_r01/replay_input_binding.json")
PACKAGE = pathlib.Path("D:/codex-worktrees/w4/report/evidence/S4-CTRL/"
                       "s4t27_replay_positive_20261027_r01/task27_replay_result_package_positive.json")
FREEZE_INDEX = pathlib.Path("D:/codex-worktrees/w4/report/evidence/S4-CTRL/"
                            "s4t27_replay_positive_20261027_r01/freeze_index.json")
INPUT_MODULE = REPO_ROOT / "scripts" / "stage5_t03" / "s5t03_replay_colour_input.py"
REGRESSION = REPO_ROOT / "scripts" / "stage5_t03" / "s5t03_replay_colour_regression.py"

SOURCE_BINDINGS = (
    "scripts/stage5_t03/s5t03_replay_colour_input.py",
    "scripts/stage5_t03/s5t03_replay_colour_regression.py",
    "scripts/stage5_t03/test_s5t03_replay_colour.py",
    "scripts/stage5_t27/run_s5t27_evidence.py",
    "docs/stage5/S5T27_replay_colour_input_path_v1.md",
    "verification/s5_display_geometry_reference.py",
)
TEST_MODULES = (
    "scripts.stage5_t03.test_s5t03_replay_colour",
    "scripts.stage5_t03.test_s5t03_frozen_replay",
    "scripts.stage5_t03.test_s5t03_stage4_positive_replay",
)
KEEP_REASON = {
    "console/quiet_window.txt": "安静窗口核验（无 vivado.exe/xsdb/hw_server/vitis/xsim）",
    "console/git_state.txt": "运行时刻工作树基线证据",
    "console/replay_input_selftest.txt": "回放输入路径实现自检（含 4 类必失败注入）的真实退出码",
    "console/regression_run.txt": "离线动态回归实跑输出与真实退出码",
    "console/unittest_all.txt": "相关用例完整原始输出",
}
LIMITATIONS = [
    "**回放/离线**：全部结论限于离线回放与离线骨架；不含任何板级/实时/实物结论。",
    "阶段4 冻结回放包只含 **1 帧**结果内容（`frame_id=1/result_seq=1`，1 框）：回归把该冻结内容**逐帧重复回放**，"
    "不是新推理、不是真实采集。",
    "时间用 replay-local 逻辑时基（`replay_timebase.basis=replay_local_logical`）：只验证过期/年龄**规则**；"
    "`capture_time_ns` 在证据模式为阶段3 文档化的真实抓取时刻（非零），回归模式为逻辑采集时刻（由同一真实基准 + 帧序号×周期推导）。",
    "长跑为虚拟逻辑时基（106 573 帧 / 1 800 001 080 000 ns），不是板上耐久。",
    "不主张：板上回放/PL 实跑、UART 实收、摄像头真实采集质量与颜色、端到端延迟（时钟 PENDING_MEASUREMENT）、"
    "T5-10 板上回归、B1–B10 任一项、G0/G1/G3/G4/G5 任一项。",
    "`task-27` 的实现层交付**不改变** S5-T04 离线冻结基线（冻结成员未修改；本卡只新增文件与证据）。",
    "`CHECKS_OK` 仅代表清单/绑定检查通过，不代表语义正确、独立审查通过或任何关口通过。",
]
TOOL_VERSIONS = {
    "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    "replay_input": "scripts/stage5_t03/s5t03_replay_colour_input.py v1（fail-closed：拒收即 ReplayInputError）",
    "regression": "scripts/stage5_t03/s5t03_replay_colour_regression.py v1",
    "checker": "check_stage_delivery.py schema_version=1（--mode evidence）",
}


def manifest_files(run_dir: pathlib.Path) -> list[dict]:
    files: list[dict] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative.endswith("delivery_manifest.json"):
            continue
        name = relative.split("/")[-1]
        role = "log" if name.endswith((".txt", ".log", ".jsonl")) else "artifact"
        if name in ("results.json", "replay_input_selftest.json"):
            role = "result"
        entry = {"path": relative, "role": role, "sha256": F.sha256_file(path)}
        reason = KEEP_REASON.get("/".join(relative.split("/")[-2:]))
        if reason:
            entry["keep_reason"] = reason
        files.append(entry)
    for relative in SOURCE_BINDINGS:
        files.append({"path": relative, "role": "source", "sha256": F.sha256_file(REPO_ROOT / relative)})
    return files


def build_manifest(run_dir_rel: str, source_commit: str, checks: list[dict]) -> pathlib.Path:
    run_dir = REPO_ROOT / run_dir_rel
    manifest = {
        "schema_version": 1,
        "stage": "5",
        "task_id": TASK_ID,
        "run_id": run_dir.name,
        "source_commit": source_commit,
        "evidence_dir": run_dir_rel,
        "interfaces": [],
        "interfaces_not_applicable_reason": (
            "本卡为**离线回放**实现与回归：输入为仓库外只读引用（阶段3 回放绑定/固定帧、阶段4 冻结回放包），"
            "无 role=input 的本地输入文件（--mode inputs 要求至少一个 role=input）；上游接口非本卡可冻结对象，"
            "故 inputs 模式不适用，不伪造 frozen 字段。"),
        "files": manifest_files(run_dir),
        "checks": checks,
        "limitations": LIMITATIONS,
        "tool_versions": TOOL_VERSIONS,
    }
    manifest_path = run_dir / "delivery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def write_hashes(run_dir: pathlib.Path) -> None:
    lines = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir() or path.name in {"hashes_sha256.txt", "delivery_manifest.json"}:
            continue
        lines.append(f"{F.sha256_file(path)} *{path.relative_to(REPO_ROOT).as_posix()}")
    (run_dir / "hashes_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_checker(manifest_path: pathlib.Path) -> dict:
    return F.run_command([sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                          "--project-root", str(REPO_ROOT), "--manifest", str(manifest_path)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--tmp-out", default="")
    args = parser.parse_args(argv)

    run_dir = REPO_ROOT / args.run_dir
    if run_dir.exists() and any(run_dir.iterdir()):
        print(f"[ENV_ERROR] RunId 目录已存在且非空：{run_dir}", file=sys.stderr)
        return 2
    (run_dir / "console").mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "tmp" / "5" / TASK_ID).mkdir(parents=True, exist_ok=True)

    quiet = F.quiet_window_check()
    git = F.git_state()
    source_commit = args.source_commit or git["head"]
    (run_dir / "console" / "quiet_window.txt").write_text("\n".join([
        f"heavy_processes={quiet['heavy_processes'] or '(none)'}",
        f"mcp_bridge_processes={quiet['mcp_bridge_processes'] or '(none)'}",
        f"verdict={'QUIET' if quiet['quiet_ok'] else 'BUSY'}", f"note={quiet['note']}", ""]),
        encoding="utf-8")
    (run_dir / "console" / "git_state.txt").write_text("\n".join([
        f"branch={git['branch']}", f"head={git['head']}", f"source_commit={source_commit}",
        f"lock_present={git['lock_present']}", "--- git status --short ---",
        git["status_short"], "", "--- tracked-only ---", git["tracked_status"], ""]), encoding="utf-8")

    # 1. 输入路径自检（实现层）
    selftest = F.run_command([sys.executable, "-B", str(INPUT_MODULE), "--binding", str(BINDING),
                              "--json-out", str(run_dir / "replay_input_selftest.json")])
    (run_dir / "console" / "replay_input_selftest.txt").write_text("\n".join([
        f"command={selftest['command']}", f"exit_code={selftest['exit_code']}",
        "--- stdout tail ---", "\n".join(selftest["stdout"].rstrip().splitlines()[-6:]),
        "--- stderr ---", selftest["stderr"].rstrip(), ""]), encoding="utf-8")

    # 2. 离线动态回归（写入 run_dir 根）
    regression = F.run_command([sys.executable, "-B", str(REGRESSION), "--out", str(run_dir),
                                "--binding", str(BINDING), "--package", str(PACKAGE),
                                "--freeze-record", str(FREEZE_INDEX)])
    (run_dir / "console" / "regression_run.txt").write_text("\n".join([
        f"command={regression['command']}", f"exit_code={regression['exit_code']}",
        "--- stdout ---", regression["stdout"].rstrip(),
        "--- stderr ---", regression["stderr"].rstrip(), ""]), encoding="utf-8")

    # 3. 用例套件
    suite_command = [sys.executable, "-B", "-m", "unittest", *TEST_MODULES]
    suite = F.run_command(suite_command)
    (run_dir / "console" / "unittest_all.txt").write_text("\n".join([
        f"command={' '.join(suite_command)}", f"exit_code={suite['exit_code']}",
        "--- stdout ---", suite["stdout"].rstrip(), "--- stderr ---", suite["stderr"].rstrip(), ""]),
        encoding="utf-8")
    suite_summary = F.parse_unittest_summary(suite["stdout"] + "\n" + suite["stderr"])

    results = (json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
               if (run_dir / "results.json").is_file() else {})
    regression_ok = regression["exit_code"] == 0 and results.get("verdict") == "REPLAY_OFFLINE_REGRESSION_PASS"

    checks = [
        {"name": "回放输入路径实现自检（逐帧完整性/replay_source_*/非零 capture/replay_not_live + 必失败注入）",
         "status": "PASS" if selftest["exit_code"] == 0 else "FAIL",
         "command": selftest["command"], "exit_code": selftest["exit_code"],
         "reason": f"{(json.loads((run_dir / 'replay_input_selftest.json').read_text(encoding='utf-8')) if (run_dir / 'replay_input_selftest.json').is_file() else {}).get('status')}；"
                   "4 类注入（replay_not_live=false / capture=0 / 缺 replay_source 字段 / frame_integrity 不符）均被拒收"},
        {"name": "离线动态显示回归（回放/离线）",
         "status": "PASS" if regression_ok else "FAIL",
         "command": regression["command"], "exit_code": regression["exit_code"],
         "reason": f"{results.get('verdict')}；断言 {len(results.get('assertions', []))} 项、"
                   f"失败 {len(results.get('failed_assertions', []))} 项；"
                   f"长跑 {results.get('long_run', {}).get('frames')} 帧 / "
                   f"{results.get('long_run', {}).get('elapsed_ns')} ns"},
        {"name": "相关用例套件",
         "status": "PASS" if suite["exit_code"] == 0 else "FAIL",
         "command": " ".join(suite_command), "exit_code": suite["exit_code"],
         "reason": f"Ran {suite_summary['ran']} / failures {suite_summary['failures']} / "
                   f"errors {suite_summary['errors']} / skipped {suite_summary['skipped']}"},
        {"name": "安静窗口（无 vivado.exe/xsdb/hw_server/vitis/xsim）",
         "status": "PASS" if quiet["quiet_ok"] else "FAIL",
         "command": "tasklist 过滤 vivado.exe|xsdb|hw_server|vitis|xsim",
         "exit_code": 0 if quiet["quiet_ok"] else 1,
         "reason": f"heavy={quiet['heavy_processes'] or '(none)'}；桥接进程 {len(quiet['mcp_bridge_processes'])} 个只作信息记录"},
        {"name": "工作树基线（无已跟踪改动、无 index.lock）",
         "status": "PASS" if not git["tracked_status"] and not git["lock_present"] else "FAIL",
         "command": "git status --short --untracked-files=no; git rev-parse --git-path index.lock",
         "exit_code": 0 if not git["tracked_status"] and not git["lock_present"] else 1,
         "reason": f"tracked_dirty={bool(git['tracked_status'])} lock={git['lock_present']}"},
        {"name": "check_stage_delivery --mode inputs",
         "status": "NOT_APPLICABLE",
         "command": f"python -B {CHECKER} --mode inputs --project-root <w5> --manifest <本清单>",
         "exit_code": None,
         "reason": "无 role=input 本地输入（输入为跨树只读引用），不伪造冻结字段"},
    ]
    write_hashes(run_dir)
    manifest = build_manifest(args.run_dir, source_commit, checks)
    check_m1 = run_checker(manifest)
    (run_dir / "console" / "check_evidence_mode_output.txt").write_text("\n".join([
        f"command={check_m1['command']}", f"exit_code={check_m1['exit_code']}",
        "--- stdout ---", check_m1["stdout"].rstrip(), "--- stderr ---", check_m1["stderr"].rstrip(), ""]),
        encoding="utf-8")
    checks.append({"name": "check_stage_delivery --mode evidence",
                   "status": "PASS" if (check_m1["exit_code"] == 0 and STATUS_OK in check_m1["stdout"]) else "FAIL",
                   "command": check_m1["command"], "exit_code": check_m1["exit_code"],
                   "reason": "对 M1 运行（M2 只新增本 check 与 console 一个文件）；CHECKS_OK 仅代表包装检查通过"})
    if isinstance(results, dict):
        results["checks"] = checks
        (run_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8")
    write_hashes(run_dir)
    manifest = build_manifest(args.run_dir, source_commit, checks)
    check_m2 = run_checker(manifest)
    if args.tmp_out:
        pathlib.Path(args.tmp_out).write_text("\n".join([
            f"exit_code={check_m2['exit_code']}", "--- stdout ---", check_m2["stdout"].rstrip(), ""]),
            encoding="utf-8")

    final_ok = (selftest["exit_code"] == 0 and regression_ok and suite["exit_code"] == 0
                and quiet["quiet_ok"] and not git["tracked_status"] and not git["lock_present"]
                and check_m1["exit_code"] == 0 and check_m2["exit_code"] == 0)
    print(f"selftest={selftest['exit_code']} regression={regression['exit_code']} "
          f"suite={suite['exit_code']}(ran={suite_summary['ran']}) quiet={'OK' if quiet['quiet_ok'] else 'BUSY'} "
          f"checker_M1={check_m1['exit_code']} checker_M2={check_m2['exit_code']}")
    print(f"run_dir={args.run_dir}")
    print(f"final_exit={0 if final_ok else 1}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())