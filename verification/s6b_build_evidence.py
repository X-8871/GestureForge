#!/usr/bin/env python3
"""S6-B 证据包构建器（清单/哈希/参数快照/限制 + 空跑检查器，退出码实测）。

流程（严格保持"先冻结预期、再运行、再探针"的顺序）：

  1. 冻结 expected（--freeze-only ），记录冻结文件哈希；
  2. 运行确定性用例（驱动自查冻结哈希 → 断言）；
  3. 运行判别力探针（verification/s6b_probe.py）；
  4. 写入 params_snapshot / reachability_notes / limitations / run_summary；
  5. 生成 delivery_manifest.json / inputs_manifest.json / hashes_sha256.txt（不动点迭代）；
  6. 实跑 check_stage_delivery.py --mode inputs / evidence（绝对 --project-root），
     把**真实退出码**写入清单。

用法：
    python -B verification/s6b_build_evidence.py --run-dir report/evidence/S6-B/s6b_core_20261023_r01 \
        --project-root D:/codex-worktrees/w6
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

UTC8 = timezone(timedelta(hours=8))
SOURCES = (
    "src/stage6/s6_core.py",
    "src/stage6/s6_params.py",
    "src/stage6/s6_actions.py",
    "verification/s6b_run_cases.py",
    "verification/s6b_probe.py",
    "verification/s6b_build_evidence.py",
    "verification/s6b_fresh_evidence_twice.py",
    "verification/tool_self_tests.py",
    "verification/claim_verify.py",
    "verification/approved_package_scan.py",
    "docs/stage6/s6a_stage6_g0_behavior_v1.json",
    "docs/stage6/S6A_stage6_g0_behavior_spec_v1.md",
    "docs/stage6/s6b_frozen_interface_v1.json",
    # 活文档不含哈希（lead 裁定 (a)）：STATE 只做存在性与声明路径检查；哈希记入 _selfproof 快照注记。
)


TEXT_SUFFIXES = (".md", ".json", ".jsonl", ".txt", ".py", ".csv", ".yaml", ".yml", ".xdc")


def hash_normalized(path: Path) -> str:
    """git 归一化口径哈希：文本文件把 CRLF 归一为 LF 后再取 SHA-256（O1 口径的可移植写法）。

    清单对文本文件可声明该口径；检查器**同时接受**原字节与归一化字节，因此
    工作区 CRLF、`git archive` 的全 LF 导出、以及历史清单（绑原字节）三者都能通过。
    """
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()




def evidence_check_manifest_entry(check_result: dict) -> dict:
    """把收敛后的 evidence 检查结果转换为清单记录。"""
    exit_code = check_result.get("exit_code")
    command = check_result.get("command_text")
    if type(exit_code) is not int or not isinstance(command, str) or not command:
        raise ValueError("最终 evidence 检查必须包含整数退出码和命令")
    return {
        "name": "check_stage_delivery.py --mode evidence",
        "status": "PASS" if exit_code == 0 else "FAIL",
        "command": command,
        "exit_code": exit_code,
    }


def format_evidence_summary_rows(first_precheck: dict | None,
                                 final_check: dict | None) -> tuple[str, str]:
    """格式化首次预检与最终收敛检查，命令和退出码对应各自的真实结果。"""
    def format_row(label: str, result: dict | None) -> str:
        if result is None:
            return f"| 交付检查 evidence {label} | 未运行 | — |"
        command = result.get("command_text") or result.get("command")
        exit_code = result.get("exit_code")
        if not isinstance(command, str) or not command or type(exit_code) is not int:
            raise ValueError(f"{label} 必须包含命令和整数退出码")
        return f"| 交付检查 evidence {label} | `{command}` | 实测 {exit_code} |"

    return (
        format_row("首次预检（fixpoint iteration 0）", first_precheck),
        format_row("最终收敛检查", final_check),
    )


def update_evidence_summary_rows(summary_text: str, first_precheck: dict,
                                  final_check: dict) -> str:
    """在摘要现有行中更新退出码，避免另增一份未绑定的结果文本。"""
    rows = format_evidence_summary_rows(first_precheck, final_check)
    prefixes = (
        "| 交付检查 evidence 首次预检（fixpoint iteration 0）",
        "| 交付检查 evidence 最终收敛检查",
    )
    lines = summary_text.splitlines()
    for prefix, row in zip(prefixes, rows):
        matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError(f"摘要中 {prefix} 行必须恰有一条，实际 {len(matches)}")
        lines[matches[0]] = row
    return "\n".join(lines) + ("\n" if summary_text.endswith("\n") else "")


def interface_reason(version: str) -> str:
    """interfaces 为空时的适用性说明（版本随行为表动态取，避免声明与契约版本漂移）。"""
    return (
        "S6-B 不消费任何已冻结接口：唯一上游是 docs/stage6/s6a_stage6_g0_behavior_v1.json"
        f"（{version}），其 24 项阈值已于 2026-10-23 批准（值仍为草案值），但接口契约本身仍未冻结；"
        "阶段4 结果记录与阶段5 显示契约仍未冻结，集成验收依赖 BLOCKED。"
    )


def run_command(command: list[str], root: Path) -> dict:
    """执行子进程。NB-07：显式 UTF-8，使产物不依赖宿主 locale（否则不设 PYTHONUTF8 时出现 U+FFFD）。"""
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(command, cwd=str(root), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", env=env, check=False)
    _guard_after_command(command)
    return {"command_text": subprocess.list2cmdline(command), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


# ---------------------------------------------------------------- 只读守门（构建期只读约束）
# S6-B 包内 limitations/coverage/摘要/清单均由**构建器与驱动生成**，不属只读输入；
# 只保护人工撰写的用例矩阵脚本（构建期不得被任何相位改写）。
_HAND_INPUTS = ("cases/build_case_matrix.py",)
_GUARD: dict[str, str] = {}
_GUARD_VIOLATIONS: list[str] = []


def _guard_snapshot(run_dir: Path) -> dict[str, str]:
    return {name: hashlib.sha256((run_dir / name).read_bytes()).hexdigest()
            for name in _HAND_INPUTS if (run_dir / name).is_file()}


def _guard_check(phase: str) -> None:
    """比对人工输入哈希；任何变化都记为违规（构建期只读约束）。"""
    global _GUARD
    after = _guard_snapshot(_GUARD_DIR) if _GUARD_DIR is not None else {}
    _trace = {k: (v[:8]) for k, v in sorted(after.items())}
    print(f"[GUARD-TRACE] {phase} coverage={_trace.get('coverage_matrix.json')} "
          f"limitations={_trace.get('limitations_not_executed.json')}")
    changed = [k for k in sorted(set(_GUARD) | set(after)) if _GUARD.get(k) != after.get(k)]
    if changed:
        _GUARD_VIOLATIONS.append(f"{phase}: {changed}")
        print(f"[GUARD] {phase} 后人工输入被改写：{changed}")
        print("[GUARD] 构建中止（只读约束被破坏：人工撰写输入在构建期发生变化）")
        raise SystemExit(1)
    _GUARD = after


_GUARD_DIR: Path | None = None

def _guard_init(run_dir: Path) -> None:
    """初始化守门基线（必须在此处声明 global，否则模块级 _GUARD 永远为空 → 假警报）。"""
    global _GUARD_DIR, _GUARD
    _GUARD_DIR = run_dir
    _GUARD = _guard_snapshot(run_dir)


def _guard_after_command(command: list[str]) -> None:
    """每个 subprocess 调用后立即比对（label = 被调脚本名），变化即中止。"""
    if _GUARD_DIR is None:
        return
    label = Path(command[2]).name if len(command) > 2 else "command"
    _guard_check(f"subprocess:{label}")



def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S6-B 证据包构建器")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--cases", default=None)
    parser.add_argument("--fresh-pair", action="store_true",
                        help="在不动点内跑「间隔 30 s 两次 --mode evidence」并把产物入库"
                             "（清单写入后立即跑，保证记录的是**清单当前**时的真实退出码）")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    _guard_init(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    driver = root / "verification/s6b_run_cases.py"
    probe = root / "verification/s6b_probe.py"
    checker = root / "verification/check_stage_delivery.py"
    cases = Path(args.cases).resolve() if args.cases else run_dir / "cases/case_matrix.json"
    if not cases.is_file():
        print(f"缺少用例文件：{cases}")
        return 2

    # 1) 冻结预期
    freeze_run = run_command([sys.executable, "-B", str(driver), "--project-root", str(root),
                              "--run-dir", str(run_dir), "--cases", str(cases),
                              "--freeze-only"], root)
    _guard_check("freeze")
    print(f"[freeze] exit={freeze_run['exit_code']}")
    if freeze_run["exit_code"] != 0:
        print(freeze_run["stdout"]); print(freeze_run["stderr"]); return 1
    freeze_path = run_dir / "expected_freeze.json"
    freeze_sha = sha256_file(freeze_path)

    # 2) 运行用例（驱动在运行前再次校验冻结哈希）
    run_result = run_command([sys.executable, "-B", str(driver), "--project-root", str(root),
                              "--run-dir", str(run_dir), "--cases", str(cases)], root)
    _guard_check("cases")
    print(f"[cases] exit={run_result['exit_code']}")
    (run_dir / "run_stdout.txt").write_text(run_result["stdout"], encoding="utf-8")
    if run_result["exit_code"] != 0:
        print(run_result["stdout"]); print(run_result["stderr"]); return 1

    # 3) 判别力探针
    probe_result = run_command([sys.executable, "-B", str(probe), "--project-root", str(root),
                                "--run-dir", str(run_dir)], root)
    _guard_check("probe")
    print(f"[probe] exit={probe_result['exit_code']}")
    if probe_result["exit_code"] != 0:
        print(probe_result["stdout"]); print(probe_result["stderr"]); return 1

    # 4) 参数快照 / 可达性 / 限制 / 摘要
    sys.path.insert(0, str(root))
    from src.stage6.s6_params import ParamPack  # noqa: E402

    pack = ParamPack(root / "docs/stage6/s6a_stage6_g0_behavior_v1.json", project_root=root)
    write_json(run_dir / "params_snapshot.json", pack.snapshot())

    thresholds = pack.threshold_bundle()
    write_json(run_dir / "reachability_notes.json", {
        "schema_version": 1, "artifact": "s6b_reachability_notes", "task_id": "S6-B",
        "derived_from": (f"{pack.data.get('artifact_version')} 已批准参数（APPROVED_20261023，2026-10-23 批准；值仍为草案值）"),
        "notes": [
            {
                "id": "B16-dedup-window",
                "statement": "T6-A02(500 ms) < T6-K01(1000 ms)：任何第二次提交都必须等冷却门结束（≥K01），"
                             "届时已超出 T6-A02 去重窗口 → 在当前草案值下 B16 的 S_DEDUP 分支不可达。",
                "consequence": "去重逻辑保留并单列，但不得计入覆盖声明；若 G0 批准 T6-A02 > T6-K01 则可达。",
                "checked": thresholds["a02_ns"] < thresholds["k01_ns"],
            },
            {
                "id": "M4-candidate-timeout",
                "statement": "**M4 可达（BLK-1 修正）**：T6-S04(500 ms) 与 T6-L02(300 ms) 的大小不足以判定——"
                             "§3 的 TARGET_CONTINUES 不含 score ≥ T6-P02，低分/位移造成的 WINDOW_MATCH 中断仍满足 "
                             "TARGET_CONTINUES（t_last_target_continues 继续刷新、miss_streak 不增），M10 不会先命中，"
                             "候选停留可达到 T6-S04 → M4 可达并**计入覆盖**（用例 C4-jitter-reset 实测 M4@f7）。",
                "consequence": "M4 计入覆盖声明；S6-A 侧 reachability.M4 与 U6-12 已同步修正（r07）。",
                "checked": True,
            },
            {
                "id": "M7-triggered-loss",
                "statement": "M5 为同步提交，TRIGGERED 之后不存在独立的提交流失窗口 → M7 构造上不可达。",
                "consequence": "保留编号与日志位，不为 M7 造路径。",
                "checked": True,
            },
        ],
    })

    report = json.loads((run_dir / "run_report.json").read_text(encoding="utf-8"))
    class_counter = Counter(row.get("matrix_class") for row in report["cases"])
    wrong = [row["case_id"] for row in report["cases"] if row["status"] != "PASS"]
    write_json(run_dir / "limitations_not_executed.json", {
        "schema_version": 1, "artifact": "s6b_limitations_not_executed", "task_id": "S6-B",
        "run_id": run_dir.name,
        "not_run": [
            {"item": "6-D 一级/二级联调（PS 状态机 → HDMI）", "status": "NOT_RUN",
             "reason": "无硬件授权；阶段4/阶段5 接口未冻结，集成验收依赖 BLOCKED。"},
            {"item": "6-E 真摄像头验收与 T6-01/02/03 统计", "status": "BLOCKED",
             "reason": "摄像头不可用；指标已于 2026-10-23 批准（值仍为草案值），且本轮为纯离线注入输入。"},
            {"item": "≥30 分钟真实时间回放稳定性", "status": "NOT_RUN",
             "reason": "本轮只跑虚拟单调时钟的确定性用例；未做长时间回放。"},
            {"item": "板上时序/资源/功耗验证", "status": "NOT_APPLICABLE",
             "reason": "本任务为离线状态机实现与测试，不含 PL/PS 实现。"},
        ],
        "reachability_not_counted_as_coverage": ["B16 S_DEDUP（A02<K01，草案值下不可达）", "M7（构造上不可达）"],
        "reachability_counted": ["M4（TARGET_CONTINUES 不含 score ≥ T6-P02 → M10 不先命中；用例 C4-jitter-reset）"],
        "known_limitations": [
            "工具自测套件的 selfproof_valid_commit 曾用 --commit HEAD；现已固定指向交付提交，解析不到时跳过并标注",
            "上一轮 G（1e2a66c）自身快照自证不绿（STATE 以文件形式声明 report/evidence 路径而 C11 曾按目录判定）；本轮已修为区分文件/目录，G2 全绿",
        ],
        "known_costs": [
            "工具自测套件（tool_self_tests.py）约 20 分钟/次；冻结时由项目总控与增量复核方各跑一次",
            "附录引用自测产物而不重跑；套件内守门两侧为同逻辑探针副本（构建器内真实守门另有独立实测）",
        ],
        "not_implemented": [
            "§4 的 transition_candidates / S_CONFLICT_RESOLVED 未实现：每帧只输出单一 transition；"
            "相关常量与分支已从代码移除（NB-04 登记）。",
        ],
        "open_behavior_deviations": [
            "M10 在 IDLE 有目标时不求值（D8/NB-03）：单帧选中目标后 IDLE 保留 current_target，"
            "「1 帧选中 + 4×E_TICK」到 800 ms 仍未判 M10，与规格「M10 适用于任意有目标状态」存在偏差；"
            "修正前不得声称 M10 全覆盖（登记为 U6 开放项；修正需在 IDLE 显式求值 M10 并回归全部用例）。",
        ],
        "expected_corrections": [
            "C3：初版把 t_last_target_continues 误判为第 7 帧值（未计入第 8 帧 OK 的刷新），"
            "并误把第 12 帧当作 NO_HAND；按 §9/§13 重新推演后改为 M10@f11、M11@f12、第二次触发@f19、"
            "no_hand_frames=3、action_effective=2。",
            "C4：初版未计入 M4 需要「容忍已耗尽」标志在窗口清空后仍然可见；实现改为先清空窗口、再置位 "
            "jitter_exhausted（置位在清空之后），用例维持 M4@f7 不变。",
            "C8：会话切换会按 B25/§13 清空计数，故改为断言 counter_highs（过程峰值）与复位后的零值，"
            "而不是复位前的累计值。",
            "N-r05-04（S6-A r06 同步）：核心原先把 window_complete_ns 写在「第 T6-S02 个 WINDOW_MATCH 帧」，"
            "未体现 T6-S03「取较晚」；现改为在 M3 成立帧（计数与时长同时满足的第一帧）写入，"
            "新增 30fps 用例 C9c-30fps-later-of 断言 window_complete_ns=233100000（P=33.3 ms 时旧逻辑会给 166.5 ms 帧）。",
        ],
        "parameter_discipline": "全部阈值来自行为表 JSON（APPROVED_20261023，值仍为草案值），实现与用例均未写死、未调参。",
        "replay_scope": "全部结论只对注入输入 + 虚拟单调时钟有效，不代表摄像头/板上行为。",
    })

    summary_lines = [
        f"# S6-B 确定性状态机与用例矩阵运行摘要（契约 {pack.data.get('artifact_version')}；RunId {run_dir.name}）",
        "",
        f"- RunId：`{run_dir.name}`；工作树：`{root}`",
        f"- 契约：`{pack.data.get('artifact_version')}`（S6-A 侧行为表；批准状态 APPROVED_20261023）",
        f"- 用例：{report['case_count']} 条，覆盖 CDX-20261022-012 §4 全部 11 类；结果 **{report['status']}**",
        f"- 预期：运行前冻结，`expected_freeze.json` SHA-256 = `{freeze_sha}`",
        f"- 参数：全部 `APPROVED_20261023`（2026-10-23 批准，值仍为草案值；见 `params_snapshot.json`）；未写死、未在测试集调参",
        "",
        "## 真实命令与退出码",
        "",
        "| 步骤 | 命令（绝对 project-root） | 实测退出码 |",
        "|---|---|---|",
        f"| 冻结预期 | `{freeze_run['command_text']}` | {freeze_run['exit_code']} |",
        f"| 运行用例 | `{run_result['command_text']}` | {run_result['exit_code']} |",
        f"| 判别力探针 | `{probe_result['command_text']}` | {probe_result['exit_code']} |",
        f"| 交付检查 inputs | `{inputs_run['command_text']}` | 实测 {inputs_run['exit_code']} |",
        *format_evidence_summary_rows(None, None),
        "",
        "## 覆盖（11 类）",
        "",
    ]
    for case_class, count in class_counter.items():
        summary_lines.append(f"- {case_class}：{count} 条")
    summary_lines += [
        "",
        "## 结论边界",
        "",
        "- 本包只覆盖离线确定性回放（注入输入 + 虚拟单调时钟）；不代表摄像头/HDMI/板上验收。",
        f"- `PASS` 只表示 {report['case_count']} 条用例的独立预期全部满足；不代表 6-C 验收通过或独立审查通过。",
        f"- 计入覆盖：**M4**（BLK-1 修正，见 `reachability_notes.json`）；不计入覆盖：B16 S_DEDUP、M7。",
        "",
    ]
    (run_dir / "s6b_run_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    # 5) 清单与哈希（不动点迭代）
    source_commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   capture_output=True, text=True, encoding="utf-8", check=False).stdout.strip()
    tool_versions = {
        "python": sys.version.split()[0],
        "git": subprocess.run(["git", "--version"], capture_output=True, text=True,
                              encoding="utf-8", check=False).stdout.strip(),
    }
    inputs_manifest_path = run_dir / "inputs_manifest.json"
    manifest_path = run_dir / "delivery_manifest.json"
    hashes_path = run_dir / "hashes_sha256.txt"
    inputs_out = run_dir / "check_inputs_mode_output.txt"
    evidence_out = run_dir / "check_evidence_mode_output.txt"
    for placeholder in (inputs_out, evidence_out):
        placeholder.write_text("", encoding="utf-8")

    def file_entries(include_sources: bool):
        rows = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(run_dir).as_posix()
            if relative == "delivery_manifest.json":
                continue  # 清单不声明自身（检查器按此约定放行）
            rows.append({"path": path.relative_to(root).as_posix(), "sha256": hash_normalized(path),
                         "role": "result" if "/logs/" not in relative else "log",
                         "keep_reason": f"S6-B 证据文件：{relative}"})
        if include_sources:
            for relative in SOURCES:
                path = root / relative
                if path.is_file():
                    rows.append({"path": relative, "sha256": hash_normalized(path), "role": "source",
                                 "keep_reason": "S6-B 实现/契约/状态绑定"})
        return rows

    def write_hashes() -> None:
        lines = []
        for path in sorted(run_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(run_dir).as_posix()
            if relative in ("hashes_sha256.txt", "delivery_manifest.json"):
                continue
            lines.append(f"{sha256_file(path)}  {relative}")
        hashes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    write_json(inputs_manifest_path, {
        "schema_version": 1, "stage": "6", "task_id": "S6-B", "run_id": run_dir.name,
        "source_commit": source_commit, "evidence_dir": f"report/evidence/S6-B/{run_dir.name}",
        "interfaces": [],
        "interfaces_not_applicable_reason": (
            interface_reason(pack.data.get("artifact_version"))
        ),
        "files": [{"path": "docs/stage6/s6a_stage6_g0_behavior_v1.json",
                   "sha256": pack.behavior_sha256, "role": "input",
                   "keep_reason": "S6-B 唯一的阈值来源（已于 2026-10-23 批准，值仍为草案值）"}],
        "checks": [{"name": "输入文件 SHA-256 复算", "status": "PASS",
                    "command": "内置复算（构建器）", "exit_code": 0}],
        "limitations": [
            "interfaces 为空：S6-B 没有可声明为 frozen 的接口；24 项阈值已于 2026-10-23 批准（值仍为草案值）。",
            "inputs 模式 CHECKS_OK 只表示清单/路径/哈希检查通过，不代表语义正确或验收通过。",
        ],
    })
    inputs_run = run_command([sys.executable, "-B", str(checker), "--mode", "inputs",
                              "--manifest", str(inputs_manifest_path), "--project-root", str(root)], root)
    _guard_check("inputs-mode")
    print(f"[inputs-mode] exit={inputs_run['exit_code']}")
    if inputs_run["exit_code"] != 0:
        print(inputs_run["stdout"]); print(inputs_run["stderr"]); return 1
    inputs_out.write_text(inputs_run["stdout"], encoding="utf-8")

    selfproof_path = run_dir.parent / f"{run_dir.name}_selfproof" / "export_selfproof.json"  # N-r07-2：自证报告在兄弟目录，可在提交后补入交付提交主体
    selfproof_check = None
    if selfproof_path.is_file():
        proof = json.loads(selfproof_path.read_text(encoding="utf-8"))
        verdicts = {row["subject"]: row["verdict"] for row in proof.get("subjects", [])}
        per_check = {row["subject"]: [c["exit_code"] for c in row.get("checks", [])]
                    for row in proof.get("subjects", [])}
        expected = (proof.get("verdict") == "ALL_SELF_PROVEN"
                    and all(all(code == 0 for code in codes) for codes in per_check.values()))
        selfproof_check = {
            "name": "冻结自证（git clone 导出后跑该提交内 S6-A 自检 + S6-B 驱动 + 两个检查器）",
            "status": "PASS" if expected else "FAIL",
            "command": ("`python -B verification/export_selfproof.py --project-root <abs> "
                        "--s6b-run report/evidence/S6-B/<run> --worktree-snapshot [--commit <rev>]`"),
            "exit_code": 0 if expected else 1,
            "reason": f"工具判定 {proof.get('verdict')}；逐项退出码 {per_check}",
        }

    claim_verdict_path = run_dir / "claim_verification.json"
    if claim_verdict_path.is_file():
        _verdict = json.loads(claim_verdict_path.read_text(encoding="utf-8")).get("verdict")
        _claim_doc = json.loads(claim_verdict_path.read_text(encoding="utf-8"))
        claim_check = {
            "name": "claim_verification.verdict == ALL_CLAIMS_VERIFIED",
            "status": "PASS" if _verdict == "ALL_CLAIMS_VERIFIED" else "FAIL",
            "command": _claim_doc.get("reproduce", "python -B verification/claim_verify.py --package s6b ..."),
            "exit_code": 0 if _verdict == "ALL_CLAIMS_VERIFIED" else 1,
            **({} if _verdict == "ALL_CLAIMS_VERIFIED" else {"reason": f"附录判定 {_verdict}（真实退出码见附录）"}),
        }
    else:
        claim_check = None
    checks = [
        *([] if claim_check is None else [claim_check]),
        *([] if selfproof_check is None else [selfproof_check]),
        {"name": f"S6-B 确定性用例（{report['case_count']} 条 / 11 类）", "status": "PASS" if run_result["exit_code"] == 0 else "FAIL",
         "command": run_result["command_text"], "exit_code": run_result["exit_code"]},
        {"name": "S6-B 判别力探针（4 项）", "status": "PASS" if probe_result["exit_code"] == 0 else "FAIL",
         "command": probe_result["command_text"], "exit_code": probe_result["exit_code"]},
        {"name": "check_stage_delivery.py --mode inputs", "status": "PASS" if inputs_run["exit_code"] == 0 else "FAIL",
         "command": inputs_run["command_text"], "exit_code": inputs_run["exit_code"]},
        {"name": "check_stage_delivery.py --mode evidence", "status": "NOT_RUN", "command": None,
         "exit_code": None, "reason": "首版清单生成后立即实跑（本轮结束前回填真实退出码）"},
    ]

    def write_manifest() -> None:
        """清单必须是**最后写入者**（结构规则）：由 FIXPOINT 在 selfcheck_result/hashes 之后调用。"""
        write_json(manifest_path, {
            "schema_version": 1, "stage": "6", "task_id": "S6-B", "run_id": run_dir.name,
            "source_commit": source_commit, "evidence_dir": f"report/evidence/S6-B/{run_dir.name}",
            "interfaces": [],
            "interfaces_not_applicable_reason": (
                interface_reason(pack.data.get("artifact_version"))
            ),
            "files": file_entries(include_sources=False) + [
                {"path": source, "sha256": hash_normalized(root / source), "role": "source",
                 "keep_reason": "S6-B 实现/契约/状态绑定"} for source in SOURCES if (root / source).is_file()
            ],
            "checks": checks, "tool_versions": tool_versions,
            "limitations": [
                f"source_commit 为本次构建时的 HEAD（动态取值 {source_commit}）；实际交付提交由 "
                "verification/export_selfproof.py 导出后复跑自证。",
                "全部阈值为 2026-10-23 批准的草案值（值未修改）；interfaces 为空表示没有可声明为 frozen 的接口。",
                "结论只对注入输入 + 虚拟单调时钟有效。",
                "计入覆盖：M4（BLK-1 修正）；不计入覆盖：B16 S_DEDUP、M7。",
                "活文档（.codex/STATE.md、进度记录）不进硬哈希集合；只有交付物绑哈希（lead 裁定 (a)）。",
                "FIXPOINT 必须是最后动作；冻结后禁止再改动 run-dir 内容（[CLOSING] 断言兜底）。",
            ],
        })

    # ---- FIXPOINT（与 S6-A 同构）：driver → selfcheck/证据产物 → hashes/manifest → run-dir 之外的验证自检 ----
    previous = None
    first_evidence_precheck = None
    for iteration in range(6):
        evidence_run = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                                    "--manifest", str(manifest_path), "--project-root", str(root)], root)
        print(f"[evidence-mode:iter{iteration}] exit={evidence_run['exit_code']}")
        if iteration == 0:
            first_evidence_precheck = evidence_run
        # 预检可能因**上一轮**清单已过期而失败：不据此中止，先重写清单再用"清单之后"的验证自检判定
        evidence_out.write_text(evidence_run["stdout"], encoding="utf-8")
        write_hashes()
        write_manifest()
        # 新鲜证据对必须在**清单刚写好、仍然当前**的时刻跑，产物直接入库；否则记录到的是
        # 「清单已过期」的假失败（批次 C ① 的同类问题）。
        if args.fresh_pair:
            fp = run_command([sys.executable, "-B", str(root / "verification/s6b_fresh_evidence_twice.py"),
                              "--project-root", str(root), "--run-dir", args.run_dir,
                              "--gap-seconds", "30",
                              "--out", f"{args.run_dir}/s6b_fresh_evidence_pair.json"], root)
            print(f"[fresh-pair:iter{iteration}] exit={fp['exit_code']}")
            if fp["exit_code"] != 0:
                print(fp["stdout"]); print(fp["stderr"]); return 1
            write_hashes()
            write_manifest()
        # 验证自检的输出必须落在 run-dir **之外**（否则会改写被声明文件、让清单当场过期）
        _verify_out = root / "tmp/6" / f"fixpoint_area_{run_dir.name}.txt"
        _verify = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                               "--manifest", str(manifest_path), "--project-root", str(root)], root)
        checks[-1] = evidence_check_manifest_entry(_verify)
        if _verify["exit_code"] != 0:
            print("[FIXPOINT-B] 验证自检失败"); print(_verify["stdout"]); return 1
        _verify_out.parent.mkdir(parents=True, exist_ok=True)
        _verify_out.write_text(_verify["stdout"], encoding="utf-8")
        _summary_path = run_dir / "s6b_run_summary.md"
        _summary = _summary_path.read_text(encoding="utf-8")
        _summary_path.write_text(
            update_evidence_summary_rows(_summary, first_evidence_precheck, checks[-1]),
            encoding="utf-8")
        # 固定输出保存本轮清单检查结果；后续先重绑，再由 closing 检查最终清单。
        evidence_out.write_text(_verify["stdout"], encoding="utf-8")
        # 摘要与最终检查状态一并进入下一轮哈希/清单；FIXPOINT 收敛后不再修改 run-dir。
        write_hashes()
        write_manifest()
        # 收敛判据必须覆盖**全部已声明文件**（只比清单+哈希会在其它产物后写时假收敛）
        state = {q.relative_to(run_dir).as_posix(): sha256_file(q)
                 for q in sorted(run_dir.rglob("*")) if q.is_file()}

        if previous == state:
            print(f"[FIXPOINT-B] converged at round {iteration + 1}")
            break
        previous = state
    else:
        print("[FIXPOINT-B] 清单无法收敛")
        return 1

    # ---- [CLOSING] 收尾断言：FIXPOINT 之后不得再改 run-dir ----
    _closing = run_command([sys.executable, "-B", str(checker), "--mode", "evidence",
                            "--manifest", str(manifest_path), "--project-root", str(root)], root)
    if _closing["exit_code"] != 0:
        print("[CLOSING] run-dir 出现未声明文件或哈希不符，构建中止")
        print(_closing["stdout"]); return 1
    print("[CLOSING] run-dir 无未声明文件、清单一致")

    print(json.dumps({"status": "S6B_EVIDENCE_BUILT", "cases": report["case_count"],
                      "report_status": report["status"], "failed_cases": wrong,
                      "freeze_sha256": freeze_sha,
                      "checks": [(c["name"], c["status"], c["exit_code"]) for c in checks]},
                     ensure_ascii=False))
    print(f"built at {datetime.now(UTC8).strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
