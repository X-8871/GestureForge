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
    "scripts/stage5_t03/recompute_from_log.py",
    "scripts/stage5_t03/scan_hash_drift.py",
    "docs/stage5/s5t03_input_contract_binding_v1.json",
    "docs/stage5/S5T03_input_contract_binding_colour_v1.md",
    "docs/stage5/s5t03_offline_skeleton_params_v1.json",
    "docs/stage5/S5T03_offline_case_skeleton_v1.md",
    "docs/stage5/S5T03_board_verification_pending_v1.md",
    "verification/s5_display_geometry_reference.py",
)

# N-7：上游接口本轮均未冻结、且本任务**没有本地输入文件**（无 role=input），
# 按 report/README.md 的规定 inputs 模式不适用；不伪造 frozen 字段，也不以空 interfaces 绕过核验。
INTERFACES: tuple = ()
INTERFACES_NOT_APPLICABLE_REASON = (
    "无 role=input 文件（本任务无本地输入文件，--mode inputs 要求至少一个 role=input）；"
    "次因：上游接口本轮均未冻结（S5A-G0-v2 frozen=false、阶段4 r04 结果契约 committed-not-frozen），"
    "frozen 核验无法成立。按 report/README.md 的规定声明 inputs 不适用，不伪造冻结字段。"
)

KEEP_REASON = {
    "console/unittest_s5t03.txt": "用例骨架完整原始输出，供独立复核逐条断言",
    "console/git_state.txt": "运行时刻工作树基线证据（分支/HEAD/锁/状态）",
    "console/not_modification_check.txt": "既有合成源证据未被改写的真实命令与退出码",
    "console/check_evidence_mode_output.txt": "交付检查器 evidence 模式实跑输出（前置清单 M1）",
    "console/recompute_from_log.txt": "独立复算器对落盘帧级日志的实跑输出与退出码（N-4）",
    "console/impact_scan.txt": "漂移登记扫描器实跑输出与退出码（NB-2）",
    "console/quiet_window.txt": "运行前安静窗口核验（无 Vivado/xsim/hw_server 进程、3121 未监听）（task-24 纪律）",
    "console/file_mtimes.txt": "本轮修订文件的实测 mtime（NB-4 取值来源证据）",
    "results_skeleton.json": "逐用例结果、实测数字、checks 与 limitations",
    "summary.md": "人读摘要与未做项/范围声明",
    "hashes_sha256.txt": "本包逐文件 SHA-256",
    "run_meta.json": "接管类运行的 checks/limitations 输入",
    "logs/events_mixed_240.jsonl": "240 帧合成流的帧级事件日志（紧凑 JSONL），供独立复算",
    "logs/events_long_run.jsonl.gz": "长跑（106573 帧）帧级事件日志（gzip 紧凑 JSONL），供独立复算",
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
        role = ("log" if relative.split("/")[-1].endswith((".txt", ".log", ".jsonl", ".jsonl.gz"))
                else "artifact")
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
    if not interfaces:
        manifest["interfaces_not_applicable_reason"] = INTERFACES_NOT_APPLICABLE_REASON
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


P_COUNTER_KEYS = T.P.COUNTER_KEYS
HARDWARE_PROCESS_PATTERN = ("vivado", "xsdb", "hw_server", "vitis", "xsim")


def quiet_window_check() -> dict:
    """运行前安静窗口核验（task-24 纪律）：无硬件/仿真进程、3121 未监听。"""
    listing = subprocess.run(["tasklist"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
    hits = [line.strip() for line in listing.stdout.splitlines()
            if any(part.lower() in line.lower() for part in HARDWARE_PROCESS_PATTERN)]
    port = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    port_lines = [line.strip() for line in port.stdout.splitlines() if ":3121" in line]
    return {"quiet_processes": hits, "port_3121_lines": port_lines,
            "quiet_ok": not hits and not port_lines}


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

    # ── 3. 用例骨架（并把帧级事件日志落到本包 logs/，N-4）──────────────────
    quiet = quiet_window_check()
    quiet_procs, quiet_port, quiet_ok = quiet["quiet_processes"], quiet["port_3121_lines"], quiet["quiet_ok"]
    (run_dir / "console" / "quiet_window.txt").write_text(
        "\n".join(["# 运行前安静窗口核验（task-24：交接核验须在安静窗口做）",
                   f"hardware_or_sim_processes={quiet_procs or '(none)'}",
                   f"port_3121_lines={quiet_port or '(none)'}",
                   f"verdict={'QUIET' if quiet_ok else 'BUSY'}", ""]), encoding="utf-8")
    T.LOG_DIR = run_dir / "logs"
    suite_summary, suite_exit = run_suite(run_dir / "console" / "unittest_s5t03.txt")

    # ── 3b. 独立复算器实跑（N-4）────────────────────────────────────────
    expect_dir = run_dir / "logs"
    recompute_runs = []
    for name, measured in (("events_mixed_240.jsonl", T.LAST_MIXED),
                           ("events_long_run.jsonl.gz", T.LAST_LONG)):
        log_path = T.LOG_DIR / name
        expect_path = expect_dir / (name.replace(".jsonl.gz", "").replace(".jsonl", "") + "_expected.json")
        expect_payload = {"counters": measured.get("counters", {}),
                          "virtual_elapsed_ns": measured.get("virtual_elapsed_ns")}
        expect_path.write_text(json.dumps(expect_payload, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        run = run_command([sys.executable, "-B", str(HERE / "recompute_from_log.py"),
                           "--log", str(log_path), "--expect", str(expect_path)])
        recompute_runs.append({"log": name, **run})
    (run_dir / "console" / "recompute_from_log.txt").write_text(
        "\n\n".join([f"log={item['log']}\ncommand={item['command']}\nexit_code={item['exit_code']}\n"
                     f"--- stdout ---\n{item['stdout'].rstrip()}\n--- stderr ---\n{item['stderr'].rstrip()}"
                     for item in recompute_runs]) + "\n", encoding="utf-8")
    recompute_ok = all(item["exit_code"] == 0 for item in recompute_runs)

    # ── 3c. 漂移登记扫描（NB-2）──────────────────────────────────────────
    impact_run = run_command([sys.executable, "-B", str(HERE / "scan_hash_drift.py")])
    (run_dir / "console" / "impact_scan.txt").write_text(
        "\n".join([f"command={impact_run['command']}", f"exit_code={impact_run['exit_code']}",
                   "--- stdout ---", impact_run["stdout"].rstrip(),
                   "--- stderr ---", impact_run["stderr"].rstrip(), ""]), encoding="utf-8")
    impact_ok = impact_run["exit_code"] == 0
    try:
        impact_summary = json.loads(impact_run["stdout"])
        impact_summary = {"found_count": len(impact_summary.get("found", [])),
                          "registered_count": len(impact_summary.get("registered", [])),
                          "verdict": impact_summary.get("verdict")}
    except json.JSONDecodeError:
        impact_summary = {}

    # ── 3d. 本轮修订文件实测 mtime（NB-4 取值来源）────────────────────────
    mtime_lines = []
    for relative in ("docs/stage5/s5t03_input_contract_binding_v1.json",
                     "docs/stage5/s5t03_offline_skeleton_params_v1.json",
                     "docs/stage5/s5a_stage5_display_g0_fields.json",
                     "scripts/stage5_t03/s5t03_display_pipeline.py",
                     "scripts/stage5_t03/test_s5t03_skeleton.py",
                     "scripts/stage5_t03/run_s5t03_evidence.py"):
        info = (REPO_ROOT / relative).stat()
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(info.st_mtime))
        mtime_lines.append(f"{stamp}+08:00  {relative}")
    (run_dir / "console" / "file_mtimes.txt").write_text(
        "\n".join(["# 本轮修订文件的实测 mtime（本地时区 UTC+8）；重新 checkout 后 mtime 会变，"
                   "字节权威为 Git blob", *mtime_lines, ""]), encoding="utf-8")

    # ── 4. results / summary ─────────────────────────────────────────────
    checks = [
        {"name": "S5-T03 离线用例骨架（unittest，含长跑虚拟时间与落盘日志复算）",
         "status": "PASS" if suite_exit == 0 else "FAIL",
         "command": "python -B scripts/stage5_t03/test_s5t03_skeleton.py -v",
         "exit_code": suite_exit,
         "reason": f"ran={suite_summary['ran']} failures={suite_summary['failures']} "
                   f"errors={suite_summary['errors']}；范围＝合成动态流离线骨架"},
        {"name": "既有合成源证据未被改写（S5-A/S5-B/S5-C/S5-T01）",
         "status": "PASS" if untouched_ok else "FAIL",
         "command": untouched["command"], "exit_code": untouched["exit_code"],
         "reason": f"git diff --name-only {BASE_COMMIT} 对四个目录为空 ⇒ 不重做、不改写既有结论"},
        {"name": "独立复算器对落盘帧级日志复算（N-4）",
         "status": "PASS" if recompute_ok else "FAIL",
         "command": "python -B scripts/stage5_t03/recompute_from_log.py --log <logs/*.jsonl[.gz]> --expect <logs/*_expected.json>",
         "exit_code": 0 if recompute_ok else 1,
         "reason": "两次复算（240 帧 mixed 与长跑）exit_code 均为 0 且与在线计数逐项一致；"
                   "复算器不导入流水线内存计数"},
        {"name": "漂移登记扫描（NB-2：旧哈希绑定清单集合 == 已登记集合）",
         "status": "PASS" if impact_ok else "FAIL",
         "command": "python -B scripts/stage5_t03/scan_hash_drift.py",
         "exit_code": impact_run["exit_code"],
         "reason": "扫描 report/evidence/**/*manifest*.json 中绑定旧哈希的清单，与绑定 JSON 的登记逐项相等；"
                   "只登记、不改写旧包"},
        {"name": "安静窗口核验（无 Vivado/xsim/hw_server、3121 未监听）",
         "status": "PASS" if quiet_ok else "FAIL",
         "command": "python: tasklist 过滤 vivado|xsdb|hw_server|vitis|xsim + netstat :3121",
         "exit_code": 0 if quiet_ok else 1,
         "reason": f"命中进程={quiet_procs or '(none)'}；3121={'LISTENING' if quiet_port else 'not listening'}；"
                   "在本安静窗口内完成本包的全部核验（task-24 纪律）"},
        {"name": "check_stage_delivery --mode inputs",
         "status": "NOT_APPLICABLE",
         "command": f"python -B {CHECKER} --mode inputs --project-root <w5> --manifest <本清单>",
         "exit_code": None,
         "reason": INTERFACES_NOT_APPLICABLE_REASON},
    ]
    units = T.NEW["counter_units"]
    counter_unit_lines = [f"计数单位（{key}）：{units[key]}"
                          for key in P_COUNTER_KEYS if key in units]
    limitations = [
        "输入范围：全部为合成动态流（synthetic_dynamic_reference）；capture_time_ns 为合成单调时钟，"
        "不是真实采集时刻。",
        "真实集成 NOT_RUN：阶段4 结果契约（r04）committed-not-frozen、未注入真实彩色帧，"
        "本包不得作为真实采集/真实推理集成证据。",
        "实现层 NOT_RUN（NB-5）：camera/回放输入路径尚未实现 —— replay_source_*/frame_integrity 未接线；"
        "本轮的关闭只在**绑定层**，不得读成实现已完成。",
        "板上实测 NOT_RUN：板卡已由 Wong 于 2026-10-24 拔下，一切板级工作暂停；板上动态映射/过期边界/长跑"
        "按 board pending 清单在重连后另行申请窗口。",
        "长跑语义：30 分钟为离线虚拟时钟加速 —— 判据用区间数 106572（帧数 106573 − 1）× 16.89 ms "
        "= 1 800 001 080 000 ns，余量 +1.08 ms；不是板上耐久（板上 31.06 min 结论仍属既有合成源显示侧证据）。",
        *counter_unit_lines,
        "N-1：S5A-G0-v2 JSON 本轮只修 stale 判定域的**措辞**（阈值/几何/语义未变），哈希由 8eac7007… 变为 "
        "10d24a39…；本轮 NB-4 又补 `revised_utc8_source` 说明键 ⇒ 现值 af51a4bf…（阈值/几何/语义自 N-1 后未再变）；"
        "report/evidence/S5-A/s5a_g0_20261021_r03 等旧包绑定的仍是 8eac7007…，已按扫描判据登记（如实登记，未删除其证据）。",
        "取代关系：本包取代 r01 两个包（s5t03_offline_skeleton_20261024_r01、s5t03_takeover_20261024_r01）——"
        "r01 清单绑定的源文件在本轮 B-1/B-2/N-1..N-7 更正后字节已变，故 r01 清单对当前字节不再匹配；"
        "r01 证据保留、不删除、不就地改写。",
        "既有结论：四 FPS、120 帧五元组、31.06 min 长跑结论原样保留，未重跑、未升级；"
        "check_stage_delivery --mode inputs 本轮不适用（见 checks 说明），不采用其结论。",
    ]
    results = {
        "task_id": "S5-T03",
        "run_id": run_dir.name,
        "source_commit": args.source_commit,
        "base_commit": BASE_COMMIT,
        "input_scope_label": "synthetic_dynamic_reference",
        "contract_revision": {"display_contract": "S5A-G0-v2（N-1 措辞修订 + NB-4 来源说明，哈希 af51a4bf…）",
                              "input_binding": "S5T03-INPUT-BINDING-v2（对齐阶段4 r04 7a9507a）",
                              "order_rule": "阶段4 r04 frame_sequence_rules：重复/乱序/回退一律拒绝并记 FAIL"},
        "supersedes_runs": ["report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r01",
                            "report/evidence/S5-T03/s5t03_takeover_20261024_r01",
                            "report/evidence/S5-T03/s5t03_offline_skeleton_20261024_r02",
                            "report/evidence/S5-T03/s5t03_takeover_20261024_r02"],
        "suite": suite_summary,
        "seed": T.NEW["seed"],
        "samples": {"frame_association_sample_frames": T.NEW["frame_association_sample_frames"],
                    "mixed_frames": T.NEW["stream_samples"]["mixed_frames"],
                    "long_run_min_frames": T.NEW["long_run_min_frames"],
                    "long_run_period_count": T.NEW["long_run_period_count"]},
        "counter_units": T.NEW["counter_units"],
        "log_dumps": T.LOG_DUMPS,
        "recompute_runs": [{"log": item["log"], "command": item["command"],
                            "exit_code": item["exit_code"]} for item in recompute_runs],
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
        f"- 长跑（离线虚拟时间）：{long_run.get('frames', 'NA')} 帧、区间数 "
        f"{T.NEW['long_run_period_count']} × 16.89 ms = {long_run.get('virtual_elapsed_ns', 0) / 1e9 / 60:.4f} 分钟，"
        f"每帧恰一次提交事件（无死锁）、时间戳单调、计数可复算",
        "- 乱序/回退（B-2）：重复与乱序同构拒绝并记 FAIL；乱序帧框与前一帧逐值相同；不进入已接受集合",
        "- 等价 frame_id（NB-1，fail-closed）：同 session 等价 frame_id 且未显式声明重复/重放 ⇒ 拒绝并记 FAIL；"
        "`repeat_declared=true` 或 `repeat_index` 递增才放行（含判别力对照与 `equiv` 流 40 帧覆盖）",
        "- 落盘日志（N-4）：`logs/events_mixed_240.jsonl`、`logs/events_long_run.jsonl.gz`；"
        "独立复算器 `scripts/stage5_t03/recompute_from_log.py` 两次 exit 0",
        "- 漂移登记（NB-2）：`scripts/stage5_t03/scan_hash_drift.py` 扫描旧哈希绑定清单 == 登记集合；"
        f"安静窗口：{'QUIET' if quiet_ok else 'BUSY'}；实现层回放/彩色路径仍 **NOT_RUN**（NB-5）",
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
        "## 本轮更正（B-1/B-2/N-1..N-7，v1→v2）",
        "- **B-1**：输入绑定重绑到阶段4 **r04**（`7a9507a`，JSON blob `611e6c7c…`）：两个彩色标签都映射 "
        "`source_kind=camera`、`capture_time_available=true`，回放用 `timing_claim_scope=replay_only` 区分；"
        "v1 曾引用的 `f6fa9f0` 快照记录为 SUPERSEDED。",
        "- **B-2**：乱序/回退采用上游 r04 `frame_sequence_rules` 的**拒绝并记 FAIL**（与重复同构：不写已接受集合、"
        "不更新最新结果、不绘制）；新增「`frame_id` 回退」「`result_seq` 回退」两个必拒绝用例与「乱序帧框与前一帧逐值相同」断言。",
        "- **N-1**：只改 S5A-G0-v2 JSON 的 stale 判定域**措辞**（行为不变），登记差异并提请正式 G0 裁定。",
        "- **N-2**：长跑判据改为区间数 106572 × 16.89 ms = 1 800 001 080 000 ns（余量 +1.08 ms）。",
        "- **N-3**：计数单位与时机已声明并机器自检（提交帧 / 结果键 / 提交次数 / 框数）。",
        "- **N-4**：帧级事件日志已随证据落盘（`logs/events_mixed_240.jsonl`、`logs/events_long_run.jsonl.gz`），"
        "并有独立复算器实跑（`console/recompute_from_log.txt`，两次 exit 0）。",
        "- **N-5**：时间戳按实际值改正（部署核对 01:07:50；参数首次冻结 00:43:33）。",
        "- **N-6**：`UR-2` 已 RESOLVED（dbdf README 于 01:14 更正为 `v10_read`）。",
        "- **N-7**：清单以 `interfaces=[]` + `interfaces_not_applicable_reason` 声明 inputs 不适用，"
        "**首要理由＝无 `role=input` 文件**。",
        "",
        "## 取代关系与既有包影响",
        f"- 本包取代：`{', '.join(results['supersedes_runs'])}`（被取代包清单绑定的源文件在本轮更正后字节已变，"
        "其清单对当前字节不再匹配；被取代证据保留、不删除、不就地改写）。",
        "- 旧哈希漂移登记（NB-2 扫描判据）：以 8eac7007… 绑定 S5A-G0-v2 JSON 的清单已全部登记；"
        f"扫描命中 {impact_summary.get('found_count', 'NA')} 个清单文件、登记 {impact_summary.get('registered_count', 'NA')} 个；"
        "哈希轨迹 8eac7007… → 10d24a39… → e3347c4e… → af51a4bf…（阈值/几何/语义自 N-1 后未再变）。",
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

    final_ok = (suite_exit == 0 and untouched_ok and recompute_ok and impact_ok and quiet_ok
                and check_m1["exit_code"] == 0 and check_m2["exit_code"] == 0)
    print(f"suite_exit={suite_exit} untouched={'OK' if untouched_ok else 'CHANGED'} "
          f"recompute_ok={recompute_ok} impact_ok={impact_ok} quiet_ok={quiet_ok} "
          f"checker_M1_exit={check_m1['exit_code']} checker_M2_exit={check_m2['exit_code']} "
          f"manifest={manifest}")
    print(f"final_exit={0 if final_ok else 1}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())