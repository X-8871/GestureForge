#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T03 离线骨架证据运行器：跑用例骨架 → 落盘证据 → 生成交付清单 → 真实退出码。

用法（真实退出码）：
    python -B scripts/stage5_t03/run_s5t03_evidence.py \
        --run-dir report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01 \
        --source-commit <40位交付内容提交> [--kind skeleton|takeover] [--allow-existing]

产物（run 目录内）：
    console/unittest_s5t03.txt            用例骨架完整输出（UTF-8）
    console/git_state.txt                 工作树/分支/HEAD/锁/状态
    console/not_modification_check.txt    既有合成源证据未被改写的真实命令与退出码
    results_skeleton.json                 逐用例结果 + 实测数字 + checks + limitations
    summary.md                            人读摘要（含未做项与范围声明）
    hashes_sha256.txt                     逐文件 SHA-256
    console/check_evidence_mode_output.txt 交付检查器（evidence 模式）实跑输出
    delivery_manifest.json                schema_version=1 机器清单

停止条件与边界：只用标准库；不读硬件/串口/阶段4 证据；不 push；不得把骨架结论写成真实集成通过。
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import pathlib
import subprocess
import sys
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
for entry in (str(REPO_ROOT), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

for _stream_name in ("stdout", "stderr"):
    _stream = getattr(sys, _stream_name, None)
    _reconfigure = getattr(_stream, "reconfigure", None)
    if _reconfigure is not None:
        try:
            _reconfigure(encoding="utf-8")
        except (ValueError, OSError):   # pragma: no cover
            pass

import test_s5t03_skeleton as T  # noqa: E402

CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
BASE_COMMIT = T.BASE_COMMIT
UNTOUCHED_PATHS = T.UNTOUCHED_PATHS
STATUS_OK = "CHECKS_OK"

SOURCE_BINDINGS = (
    "scripts/stage5_t03/s5t03_display_pipeline.py",
    "scripts/stage5_t03/s5t03_dynamic_stream.py",
    "scripts/stage5_t03/test_s5t03_skeleton.py",
    "scripts/stage5_t03/run_s5t03_evidence.py",
    "docs/stage5/s5t03_input_contract_binding_v1.json",
    "docs/stage5/S5T03_input_contract_binding_colour_v1.md",
    "docs/stage5/s5t03_offline_skeleton_params_v1.json",
    "docs/stage5/S5T03_offline_case_skeleton_v1.md",
    "docs/stage5/S5T03_board_verification_pending_v1.md",
    "verification/s5_display_geometry_reference.py",
)

INTERFACES = (
    {"name": "阶段5 显示 G0 契约（S5A-G0-v2；冻结参考实现的上游）",
     "version": "S5A-G0-v2 / 2026-10-21", "frozen": False,
     "path": "docs/stage5/s5a_stage5_display_g0_fields.json"},
    {"name": "阶段5 显示 G0 定稿规格 v2",
     "version": "v2 / 2026-10-21", "frozen": False,
     "path": "docs/stage5/S5A_stage5_display_g0_spec_v2.md"},
    {"name": "阶段5 输入契约改绑（本任务，未冻结）",
     "version": "S5T03-INPUT-BINDING-v1 / 2026-10-24", "frozen": False,
     "path": "docs/stage5/s5t03_input_contract_binding_v1.json"},
    {"name": "阶段5 离线骨架冻结参数（样本数与种子）",
     "version": "S5T03-SKELETON-PARAMS-v1 / 2026-10-24", "frozen": False,
     "path": "docs/stage5/s5t03_offline_skeleton_params_v1.json"},
    {"name": "阶段5 离线用例骨架规格（本任务，未冻结）",
     "version": "S5T03-SKELETON-v1 / 2026-10-24", "frozen": False,
     "path": "docs/stage5/S5T03_offline_case_skeleton_v1.md"},
    {"name": "阶段5 板级待验项与窗口申请材料（本任务，未冻结）",
     "version": "S5T03-BOARD-PENDING-v1 / 2026-10-24", "frozen": False,
     "path": "docs/stage5/S5T03_board_verification_pending_v1.md"},
)

KEEP_REASON = {
    "console/unittest_s5t03.txt": "用例骨架完整原始输出，供独立复核逐条断言",
    "console/git_state.txt": "运行时刻工作树基线证据（分支/HEAD/锁/状态）",
    "console/not_modification_check.txt": "既有合成源证据未被改写的真实命令与退出码",
    "console/check_evidence_mode_output.txt": "交付检查器 evidence 模式实跑输出（前置清单 M1）",
    "results_skeleton.json": "逐用例结果、实测数字、checks 与 limitations",
    "summary.md": "人读摘要与未做项/范围声明",
    "hashes_sha256.txt": "本包逐文件 SHA-256",
    "run_meta.json": "接管类运行的 checks/limitations 输入",
}


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(args: list[str]) -> dict:
    completed = subprocess.run(args, cwd=str(REPO_ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
    return {"command": " ".join(args), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


class Recorder(unittest.TextTestResult):
    """记录逐用例结果（供 JSON 证据），同时保留标准文本输出。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes: list[dict] = []

    def _add(self, test, status: str, detail: str = ""):
        self.outcomes.append({"test": test.id(), "status": status, "detail": detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self._add(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._add(test, "FAIL", self._exc_info_to_string(err, test).strip().splitlines()[-1])

    def addError(self, test, err):
        super().addError(test, err)
        self._add(test, "ERROR", self._exc_info_to_string(err, test).strip().splitlines()[-1])

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._add(test, "NOT_RUN", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._add(test, "FAIL", "expected failure")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._add(test, "FAIL", "unexpected success")


def run_suite(log_path: pathlib.Path) -> tuple[dict, int]:
    """在进程内跑一次并写 UTF-8 日志；返回（结果字典，退出码）。"""
    suite = unittest.TestLoader().loadTestsFromModule(T)
    buffer = io.StringIO()
    runner = unittest.TextTestRunner(stream=buffer, verbosity=2, resultclass=Recorder)
    started = time.time()
    result = runner.run(suite)
    elapsed = time.time() - started
    text = buffer.getvalue()
    log_path.write_text(text, encoding="utf-8")
    summary = {
        "ran": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "was_successful": result.wasSuccessful(),
        "elapsed_seconds": round(elapsed, 3),
        "outcomes": result.outcomes,
    }
    return summary, (0 if result.wasSuccessful() else 1)


def manifest_files(run_dir: pathlib.Path) -> list[dict]:
    files: list[dict] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative.endswith("delivery_manifest.json"):
            continue
        role = "log" if relative.split("/")[-1].endswith((".txt", ".log")) else "artifact"
        if relative.endswith(("results_skeleton.json", "run_meta.json")):
            role = "result"
        entry = {"path": relative, "role": role, "sha256": sha256_file(path)}
        reason = KEEP_REASON.get("/".join(relative.split("/")[-2:]))
        if reason:
            entry["keep_reason"] = reason
        files.append(entry)
    for relative in SOURCE_BINDINGS:
        files.append({"path": relative, "role": "source", "sha256": sha256_file(REPO_ROOT / relative)})
    return files


def build_manifest(run_dir_rel: str, source_commit: str, checks: list[dict],
                   limitations: list[dict], tool_versions: dict) -> pathlib.Path:
    run_dir = REPO_ROOT / run_dir_rel
    interfaces = []
    for item in INTERFACES:
        entry = dict(item)
        entry["sha256"] = sha256_file(REPO_ROOT / item["path"])
        interfaces.append(entry)
    manifest = {
        "schema_version": 1,
        "stage": "5",
        "task_id": "S5-T03",
        "run_id": run_dir.name,
        "source_commit": source_commit,
        "evidence_dir": run_dir_rel,
        "interfaces": interfaces,
        "files": manifest_files(run_dir),
        "checks": checks,
        "limitations": limitations,
        "tool_versions": tool_versions,
    }
    manifest_path = run_dir / "delivery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    return manifest_path


def write_hashes(run_dir: pathlib.Path) -> None:
    lines = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir() or path.name in {"hashes_sha256.txt", "delivery_manifest.json"}:
            continue
        lines.append(f"{sha256_file(path)} *{path.relative_to(REPO_ROOT).as_posix()}")
    (run_dir / "hashes_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_checker(manifest_path: pathlib.Path) -> dict:
    return run_command([sys.executable, "-B", str(CHECKER), "--mode", "evidence",
                        "--project-root", str(REPO_ROOT), "--manifest", str(manifest_path)])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--kind", choices=("skeleton", "takeover"), default="skeleton")
    parser.add_argument("--allow-existing", action="store_true")
    parser.add_argument("--tmp-out", default="")
    args = parser.parse_args(argv)

    run_dir = REPO_ROOT / args.run_dir
    if run_dir.exists() and not args.allow_existing:
        print(f"[STOP] RunId 目录已存在，不得覆盖重跑：{run_dir}", file=sys.stderr)
        return 2
    (run_dir / "console").mkdir(parents=True, exist_ok=True)

    tool_versions = {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "unittest": "python-stdlib",
        "checker": "check_stage_delivery.py schema_version=1",
        "git": run_command(["git", "--version"])["stdout"].strip().replace("git version ", ""),
    }

    if args.kind == "takeover":
        meta_path = run_dir / "run_meta.json"
        if not meta_path.exists():
            print(f"[STOP] takeover 运行缺少 run_meta.json：{meta_path}", file=sys.stderr)
            return 2
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta["checks"]
        limitations = meta["limitations"]
        tool_versions.update(meta.get("tool_versions", {}))
        write_hashes(run_dir)
        manifest = build_manifest(args.run_dir, args.source_commit, checks, limitations, tool_versions)
        result = run_checker(manifest)
        print(f"checker(evidence) exit={result['exit_code']}")
        print(result["stdout"][-2000:])
        return 0 if result["exit_code"] == 0 else 1

    # ── 1. 基线证据 ──────────────────────────────────────────────────────
    git_state = run_command(["git", "-C", str(REPO_ROOT), "status", "--short"])
    head = run_command(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"])
    branch = run_command(["git", "-C", str(REPO_ROOT), "branch", "--show-current"])
    lock = run_command(["git", "-C", str(REPO_ROOT), "rev-parse", "--git-path", "index.lock"])
    lock_exists = pathlib.Path(lock["stdout"].strip()).exists() if lock["stdout"].strip() else False
    (run_dir / "console" / "git_state.txt").write_text(
        "\n".join([
            f"worktree={REPO_ROOT}",
            f"branch={branch['stdout'].strip()}",
            f"head={head['stdout'].strip()}",
            f"source_commit={args.source_commit}",
            f"index.lock_path={lock['stdout'].strip()}",
            f"index.lock_exists={lock_exists}",
            "--- git status --short ---",
            git_state["stdout"].rstrip(),
            "",
        ]), encoding="utf-8")

    # ── 2. 既有合成源证据未被改写（真实命令 + 退出码）─────────────────────
    untouched = run_command(["git", "-C", str(REPO_ROOT), "diff", "--name-only", BASE_COMMIT,
                             "--", *UNTOUCHED_PATHS])
    untouched_ok = untouched["exit_code"] == 0 and untouched["stdout"].strip() == ""
    (run_dir / "console" / "not_modification_check.txt").write_text(
        "\n".join([f"command={untouched['command']}", f"exit_code={untouched['exit_code']}",
                   f"changed_files={(untouched['stdout'].strip() or '(none)')}",
                   f"verdict={'UNTOUCHED' if untouched_ok else 'CHANGED'}", ""]),
        encoding="utf-8")

    # ── 3. 用例骨架 ──────────────────────────────────────────────────────
    suite_summary, suite_exit = run_suite(run_dir / "console" / "unittest_s5t03.txt")

    # ── 4. results / summary ─────────────────────────────────────────────
    checks = [
        {"name": "S5-T03 离线用例骨架（unittest，含长跑虚拟时间）",
         "status": "PASS" if suite_exit == 0 else "FAIL",
         "command": "python -B scripts/stage5_t03/test_s5t03_skeleton.py -v",
         "exit_code": suite_exit,
         "reason": f"ran={suite_summary['ran']} failures={suite_summary['failures']} "
                   f"errors={suite_summary['errors']}；范围＝合成动态流离线骨架"},
        {"name": "既有合成源证据未被改写（S5-A/S5-B/S5-C/S5-T01）",
         "status": "PASS" if untouched_ok else "FAIL",
         "command": untouched["command"], "exit_code": untouched["exit_code"],
         "reason": f"git diff --name-only {BASE_COMMIT} 对四个目录为空 ⇒ 不重做、不改写既有结论"},
        {"name": "check_stage_delivery --mode inputs",
         "status": "NOT_APPLICABLE",
         "command": f"python -B {CHECKER} --mode inputs --project-root <w5> --manifest <本清单>",
         "exit_code": None,
         "reason": "上游接口均未冻结（S5A-G0-v2 frozen=false、阶段4 结果契约为草案），"
                   "按 report/README.md 规定 inputs 模式不适用；不伪造冻结字段"},
    ]
    limitations = [
        "输入范围：全部为合成动态流（synthetic_dynamic_reference）；capture_time_ns 为合成单调时钟，"
        "不是真实采集时刻。",
        "真实集成 NOT_RUN：阶段4 结果契约未冻结、未注入真实彩色帧，本包不得作为真实采集/真实推理集成证据。",
        "板上实测 NOT_RUN：本轮不动硬件（阶段3 窗口占用中），板上动态映射/过期边界/长跑按 board pending 清单另行申请窗口。",
        "长跑语义：30 分钟为离线虚拟时钟加速（106573 帧 × 16.89 ms），不是板上耐久；"
        "板上 31.06 min 结论仍属既有合成源显示侧证据。",
        "既有结论：四 FPS、120 帧五元组、31.06 min 长跑结论原样保留，未重跑、未升级；"
        "check_stage_delivery --mode inputs 本轮不适用，不采用其结论。",
    ]
    results = {
        "task_id": "S5-T03",
        "run_id": run_dir.name,
        "source_commit": args.source_commit,
        "base_commit": BASE_COMMIT,
        "input_scope_label": "synthetic_dynamic_reference",
        "suite": suite_summary,
        "seed": T.NEW["seed"],
        "samples": {"frame_association_sample_frames": T.NEW["frame_association_sample_frames"],
                    "mixed_frames": T.NEW["stream_samples"]["mixed_frames"],
                    "long_run_min_frames": T.NEW["long_run_min_frames"]},
        "measured_mixed_240": T.LAST_MIXED,
        "measured_long_run": T.LAST_LONG,
        "checks": checks,
        "limitations": limitations,
    }
    (run_dir / "results_skeleton.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mixed = T.LAST_MIXED.get("counters", {})
    long_run = T.LAST_LONG
    summary_lines = [
        "# S5-T03 离线用例骨架摘要（合成动态流，非真实集成）",
        "",
        f"- RunId：`{run_dir.name}`；基线提交：`{args.source_commit}`；输入范围标签：`synthetic_dynamic_reference`",
        f"- 用例骨架：{suite_summary['ran']} 项，失败 {suite_summary['failures']}，错误 {suite_summary['errors']}，"
        f"耗时 {suite_summary['elapsed_seconds']} s，退出码 {suite_exit}",
        f"- 既有合成源证据未被改写：{'UNTOUCHED' if untouched_ok else 'CHANGED'}（退出码 {untouched['exit_code']}）",
        "",
        "## 覆盖（离线）",
        "- 坐标映射：手算 5 例 + 冻结参考实现同源（哈希比对）+ 越界/零面积 + 2 px 偶数线宽钳位",
        "- 帧关联：顺序/迟到/跳帧/重复/乱序；120 帧五元组可按 `displayed_frame_id` 索引、语义唯一 B、"
        "`displayed != result` 如实记录",
        "- 异常与过期：`age==limit` 不过期、`limit+1` 过期且每结果只计一次、显式 `stale_flag`、"
        "零框 ≠ 过期、`TIMEOUT/ERROR/DROPPED` 分列、无效记录不绘制",
        f"- 长跑（离线虚拟时间）：{long_run.get('frames', 'NA')} 帧 ≈ "
        f"{long_run.get('virtual_elapsed_ns', 0) / 1e9 / 60:.2f} 分钟，"
        f"每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算",
        "",
        "## 关键计数（合成流，仅供骨架核对；不得当作板上结论）",
        f"- 240 帧 mixed：{json.dumps(mixed, ensure_ascii=False)}",
        f"- 长跑：commit_events={long_run.get('commit_events', 'NA')}，"
        f"counters={json.dumps(long_run.get('counters', {}), ensure_ascii=False)}",
        "",
        "## 未做项（NOT_RUN，如实）",
        "- 真实彩色采集/回放输入接入（待阶段4 结果契约冻结与注入路径确认）",
        "- 板上动态映射与绘制（待阶段5 板级窗口；见 `docs/stage5/S5T03_board_verification_pending_v1.md`）",
        "- 板上 `age==limit`/`limit+1`/`stale_flag` 边界样例、HUD 13 字段视觉、跨进程故障注入",
        "- 真实集成的 30 分钟联调与 T5-10 板上回归",
        "",
        "## 范围声明",
        "本包只是**离线骨架**结论；`check_stage_delivery` 的 `CHECKS_OK` 仅代表清单/文件绑定通过，",
        "不代表测试语义正确、独立审查通过或 G0/G4/G5；亦不得把合成流结论升级为真实集成通过。",
        "",
    ]
    (run_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    write_hashes(run_dir)

    # ── 5. 交付清单 M1 + 检查器 ──────────────────────────────────────────
    manifest = build_manifest(args.run_dir, args.source_commit, checks, limitations, tool_versions)
    check_m1 = run_checker(manifest)
    (run_dir / "console" / "check_evidence_mode_output.txt").write_text(
        "\n".join([f"command={check_m1['command']}", f"exit_code={check_m1['exit_code']}",
                   "--- stdout ---", check_m1["stdout"].rstrip(),
                   "--- stderr ---", check_m1["stderr"].rstrip(), ""]), encoding="utf-8")
    checks.append({
        "name": "check_stage_delivery --mode evidence",
        "status": "PASS" if (check_m1["exit_code"] == 0 and STATUS_OK in check_m1["stdout"]) else "FAIL",
        "command": check_m1["command"], "exit_code": check_m1["exit_code"],
        "reason": "对本包前置清单 M1 运行（M2 相对 M1 只新增本 check 条目与 "
                  "console/check_evidence_mode_output.txt 一个文件）；CHECKS_OK 仅代表包装检查通过",
    })
    write_hashes(run_dir)
    manifest = build_manifest(args.run_dir, args.source_commit, checks, limitations, tool_versions)
    check_m2 = run_checker(manifest)
    if args.tmp_out:
        pathlib.Path(args.tmp_out).write_text(
            "\n".join([f"exit_code={check_m2['exit_code']}", "--- stdout ---",
                       check_m2["stdout"].rstrip(), "--- stderr ---", check_m2["stderr"].rstrip(), ""]),
            encoding="utf-8")

    final_ok = suite_exit == 0 and untouched_ok and check_m1["exit_code"] == 0 and check_m2["exit_code"] == 0
    print(f"suite_exit={suite_exit} untouched={'OK' if untouched_ok else 'CHANGED'} "
          f"checker_M1_exit={check_m1['exit_code']} checker_M2_exit={check_m2['exit_code']} "
          f"manifest={manifest}")
    print(f"final_exit={0 if final_ok else 1}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())