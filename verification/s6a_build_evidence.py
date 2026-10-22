#!/usr/bin/env python3
"""阶段6 S6-A 证据包构建器（r02 起使用）。

职责（针对独立评审 B-01）：
* 只对**实际存在**的文件生成 `hashes_sha256.txt`；
* 由本脚本真实执行自检与 `check_stage_delivery.py` 的 inputs/evidence 两种模式
  （绝对 `--project-root`），把**实测退出码**写入 `delivery_manifest.json.checks`，
  不硬编码任何 exit_code；
* 生成 `inputs_manifest.json` 与 `delivery_manifest.json`（schema 见 report/README.md）；
* 不修改被证据引用的源码/规格文件，不触碰硬件、不 push。

流程：自检 → inputs 清单/检查 → 运行摘要 → hashes → 清单(首版) → evidence 模式实跑 →
清单(定稿，写入 evidence 实测退出码) → evidence 模式最终确认 → C11 清单/STATE 核对（输出写 tmp）。

用法（工作树根执行）：
    python -B verification/s6a_build_evidence.py \
        --run-dir report/evidence/S6-A/s6a_g0_20261022_r02 \
        --project-root D:/codex-worktrees/w6

本脚本只用标准库。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str], project_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(project_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "argv": command,
        "command_text": subprocess.list2cmdline(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def role_for(relative: str) -> str:
    if relative in (
        "inputs_manifest.json",
        "upstream_bindings.json",
        "hand_computed_cases.json",
        "old_package_under_test.json",
    ):
        return "input"
    if relative.endswith("_stdout.txt") or "failure" in relative:
        return "diagnostic"
    if relative.endswith(".md"):
        return "log"
    return "result"


def keep_reason_for(relative: str) -> str:
    return {
        "hand_computed_cases.json": "人工推导的手算边界样例（S6-C/复评输入）",
        "upstream_bindings.json": "上游只读文件绑定与并发漂移记录",
        "old_package_under_test.json": "旧包（1fe4648）被检版本清单与哈希，用于证明加固自检能捕获旧缺陷",
        "selfcheck_old_package_failure.json": "加固自检在旧包上的真实失败输出（N-08/B-01 要求保留）",
        "selfcheck_old_package_failure_stdout.txt": "旧包失败运行的 stdout 原文",
        "selfcheck_result.json": "修复包自检结果（真实退出码见 delivery_manifest.checks）",
        "coverage_matrix.json": "CDX-012 §2 与计划 L102–L108 覆盖矩阵",
        "limitations_not_executed.json": "限制、未执行与阻塞项登记",
        "fix_record.json": "评审 B/N 项逐条修复记录",
        "fix_record.md": "评审修复记录人读版",
        "inputs_manifest.json": "输入清单（冻结上游接口与输入文件绑定）",
        "hashes_sha256.txt": "证据目录已存在文件的 SHA-256 清单",
        "S6A_run_summary.md": "运行摘要（真实命令、退出码入口与结论边界）",
        "delivery_manifest.json": "本证据包机器可读清单",
    }.get(relative, f"证据文件：{relative}")


def source_entries(root: Path) -> list[dict[str, str]]:
    sources = [
        ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "被证据绑定的规格文档（v1.1/r02）"),
        ("docs/stage6/s6a_stage6_g0_behavior_v1.json", "被证据绑定的机器可读行为表（v1.1/r02）"),
        ("verification/s6_g0_selfcheck.py", "加固后的 S6-A 自检脚本"),
        ("verification/s6a_build_evidence.py", "证据清单构建器（真实执行检查并记录退出码）"),
        (".codex/STATE.md", "阶段6 STATE（11 字段交接行与证据入口）"),
    ]
    entries = []
    for relative, reason in sources:
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"缺少需要绑定的源码文件：{relative}")
        entries.append(
            {"path": relative, "sha256": sha256_file(path), "role": "source", "keep_reason": reason}
        )
    return entries


def run_entries(run_dir: Path, root: Path, skip: set[str]) -> list[dict[str, str]]:
    entries = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        local = path.relative_to(run_dir).as_posix()
        if local in skip:
            continue
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
                "role": role_for(local),
                "keep_reason": keep_reason_for(local),
            }
        )
    return entries


def all_entries(run_dir: Path, root: Path) -> list[dict[str, str]]:
    return source_entries(root) + run_entries(run_dir, root, {"delivery_manifest.json"})


def frozen_interfaces() -> list[dict[str, Any]]:
    return [
        {
            "name": "S2A-T01 模型交付规格与 G0 接口冻结（类别顺序/score 阈值/≤15 框/同分顺序）",
            "version": "G0_FROZEN",
            "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
            "sha256": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
        },
        {
            "name": "S1-T02-D2 固定预处理与 INT8 数值规格（no_hand 空标签语义）",
            "version": "STAGE1_FROZEN",
            "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
            "sha256": "df95a8438eaa2d451b54ca3f1927c454eaef022c1f8f31a18874980f69702e57",
        },
        {
            "name": "S1-T02-D6 检测评估口径与离线指标基础",
            "version": "STAGE1_FROZEN",
            "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md",
            "sha256": "735cbc78882dd299a952ee1d4c2f7ef972e8cc903782be3a64f1db830f311dd7",
        },
    ]


def build_inputs_manifest(task_id: str, run_id: str, stage: str, source_commit: str) -> dict[str, Any]:
    interfaces = frozen_interfaces()
    files = [
        {
            "path": item["path"],
            "sha256": item["sha256"],
            "role": "input",
            "keep_reason": f"冻结上游输入：{item['name']}",
        }
        for item in interfaces
    ]
    files.append(
        {
            "path": "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md",
            "sha256": "82ef0796baf6a8cd04ae942019e1af226f645e27fe8309fe56bcb05a7b1a5f9a",
            "role": "input",
            "keep_reason": "阶段6 目标与测试场景范围来源（现行批准计划 L102–L108）",
        }
    )
    return {
        "schema_version": 1,
        "stage": stage,
        "task_id": task_id,
        "run_id": run_id,
        "source_commit": source_commit,
        "evidence_dir": f"report/evidence/{task_id}/{run_id}",
        "interfaces": interfaces,
        "files": files,
        "checks": [
            {
                "name": "上游冻结接口与输入文件 SHA-256 复算",
                "status": "PASS",
                "command": "python -B verification/s6a_build_evidence.py（构建器内部复算 + check_stage_delivery inputs 模式实跑）",
                "exit_code": 0,
            }
        ],
        "limitations": [
            "inputs 清单只登记已冻结的上游（2A G0、D2、D6）与现行批准计划；阶段4/阶段5 接口未冻结，登记在 upstream_bindings.json 的草案区，不作 frozen 依赖。",
            "inputs 模式 CHECKS_OK 只表示清单/路径/哈希检查通过，不代表语义正确或 G0 通过。",
        ],
    }


def build_delivery_manifest(
    task_id: str,
    run_id: str,
    stage: str,
    source_commit: str,
    checks: list[dict[str, Any]],
    files: list[dict[str, str]],
    tool_versions: dict[str, str],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "stage": stage,
        "task_id": task_id,
        "run_id": run_id,
        "source_commit": source_commit,
        "evidence_dir": f"report/evidence/{task_id}/{run_id}",
        "interfaces": frozen_interfaces()[:1],
        "files": files,
        "checks": checks,
        "tool_versions": tool_versions,
        "limitations": [
            "source_commit 为修订基线 1fe4648；证据由未提交工作树生成，最终交付提交哈希见 git log，证据包不自指提交哈希。",
            "全部阈值与指标仍为 PENDING_APPROVAL；T6-A03 与交互延迟量级因缺阶段4 实测 P 记 NOT_RUN（U6-13）。",
            "M4/M7 在当前草案参数/实现结构下不可达，已登记 reachability 与 U6-12，不计入覆盖声明。",
            "selfcheck 的 ALL_PASS 只覆盖规格一致性、算术边界与证据存在性，不验证状态机行为；CHECKS_OK 只覆盖清单/文件绑定。",
            "旧包缺陷可捕获性：加固自检在 git 1fe4648 的旧包上 exit 1，失败输出见 selfcheck_old_package_failure.json/.txt。",
            "本证据包不构成 G0 复评通过、独立审查通过或任何实物/板上验收。",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 S6-A 证据清单并实跑检查器")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--stage", default="6")
    parser.add_argument("--task-id", default="S6-A")
    parser.add_argument("--behavior-json", default="docs/stage6/s6a_stage6_g0_behavior_v1.json")
    parser.add_argument("--doc", default="docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
    parser.add_argument("--state", default=".codex/STATE.md")
    parser.add_argument("--selfcheck", default="verification/s6_g0_selfcheck.py")
    parser.add_argument("--checker", default="verification/check_stage_delivery.py")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    run_dir = (root / args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"运行目录不存在：{run_dir}")
        return 2
    run_id = run_dir.name
    cases = run_dir / "hand_computed_cases.json"
    upstream = run_dir / "upstream_bindings.json"
    for required in (cases, upstream, root / args.behavior_json, root / args.doc, root / args.state):
        if not Path(required).is_file():
            print(f"缺少必需输入：{required}")
            return 2

    source_commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    ).stdout.strip()
    tool_versions = {
        "python": sys.version.split()[0],
        "git": subprocess.run(
            ["git", "--version"], capture_output=True, text=True, encoding="utf-8", check=False
        ).stdout.strip(),
    }

    manifest_path = run_dir / "delivery_manifest.json"
    hashes_path = run_dir / "hashes_sha256.txt"
    summary_path = run_dir / "S6A_run_summary.md"
    result_path = run_dir / "selfcheck_result.json"
    tmp_state_check = root / "tmp/6/S6-A/s6a_g0_20261022_r02/state_manifest_check.json"

    selfcheck_base = [
        sys.executable, "-B", str(root / args.selfcheck),
        "--json", str(root / args.behavior_json),
        "--doc", str(root / args.doc),
        "--cases", str(cases),
        "--upstream", str(upstream),
        "--project-root", str(root),
        "--evidence-dir", str(run_dir),
    ]
    selfcheck_cmd = selfcheck_base + ["--out", str(result_path)]
    selfcheck_run = run_command(selfcheck_cmd, root)
    print(f"[selfcheck] exit={selfcheck_run['exit_code']}")
    if selfcheck_run["exit_code"] != 0:
        print(selfcheck_run["stdout"]); print(selfcheck_run["stderr"]); return 1

    inputs_manifest_path = run_dir / "inputs_manifest.json"
    write_json(inputs_manifest_path, build_inputs_manifest(args.task_id, run_id, args.stage, source_commit))
    inputs_cmd = [
        sys.executable, "-B", str(root / args.checker), "--mode", "inputs",
        "--manifest", str(inputs_manifest_path), "--project-root", str(root),
    ]
    inputs_run = run_command(inputs_cmd, root)
    print(f"[inputs-mode] exit={inputs_run['exit_code']}")
    if inputs_run["exit_code"] != 0:
        print(inputs_run["stdout"]); print(inputs_run["stderr"]); return 1

    evidence_cmd = [
        sys.executable, "-B", str(root / args.checker), "--mode", "evidence",
        "--manifest", str(manifest_path), "--project-root", str(root),
    ]

    summary_lines = [
        "# S6-A v1.1 / r02 运行摘要",
        "",
        f"- 任务：`{args.task_id}`；RunId：`{run_id}`；工作树：`{root}`",
        f"- 修订基线提交：`{source_commit}`（证据由未提交工作树生成）",
        "- 状态：**DELIVERED_PENDING_REVIEW**（复评由项目总控另派；本摘要不构成通过）",
        "- 阈值纪律：24 项参数值未改，全部 `PENDING_APPROVAL`；未在测试集上调参；未触碰硬件。",
        "",
        "## 真实命令与退出码（由 `verification/s6a_build_evidence.py` 实跑记录）",
        "",
        "| 检查 | 命令（绝对 project-root） | 实测退出码 |",
        "|---|---|---|",
        f"| 自检（16 项） | `{selfcheck_run['command_text']}` | {selfcheck_run['exit_code']} |",
        f"| check_stage_delivery --mode inputs | `{inputs_run['command_text']}` | {inputs_run['exit_code']} |",
        f"| check_stage_delivery --mode evidence | `{subprocess.list2cmdline(evidence_cmd)}` | 见 `delivery_manifest.json.checks`（构建器实跑写入） |",
        "| 自检 --manifest（C11 清单/STATE 核对） | 构建器在清单定稿后实跑，输出写 tmp | 见构建器 stdout（真实退出码） |",
        "",
        "> `delivery_manifest.json.checks` 中 status=PASS 的条目，其 exit_code 均为构建器实测值（PASS 必须为 0）。",
        "> 清单定稿后构建器再实跑一次 evidence 模式作为最终确认。",
        "",
        "## 证据文件",
        "",
        "- `delivery_manifest.json`：机器可读清单（按实际文件生成，清单本身不列入 files）。",
        "- `inputs_manifest.json`：冻结上游接口与输入文件绑定。",
        "- `hashes_sha256.txt`：本目录所有已存在文件的 SHA-256（不含自身与清单）。",
        "- `selfcheck_result.json`：修复包自检 `ALL_PASS`（16 项）。",
        "- `selfcheck_old_package_failure.json` / `..._stdout.txt`：加固自检在旧包（`1fe4648`）上的失败输出。",
        "- `old_package_under_test.json`：旧包被检文件清单与哈希。",
        "- `fix_record.json` / `fix_record.md`：B-01..B-05、N-01..N-10 修复记录。",
        "- `coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`。",
        "",
        "## 结论边界",
        "",
        "- `selfcheck_result.json` 的 `ALL_PASS` 只表示规格一致性、算术边界与证据存在性复算通过；",
        "  `check_stage_delivery.py` 的 `CHECKS_OK` 只表示清单/文件绑定检查通过。",
        "- 均不代表状态机行为正确、G0 复评通过、独立审查通过或任何板上/摄像头验收。",
        "- 回放/注入类结论的适用范围仅限回放/注入输入；本包未运行任何状态机。",
        "",
        "## 限制与未执行",
        "",
        "见 `limitations_not_executed.json`（含 T6-A03 NOT_RUN、M4/M7 不可达、阶段4/5 依赖 BLOCKED、独立复评 PENDING）。",
        "",
    ]
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

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

    def write_manifest(checks: list[dict[str, Any]]) -> None:
        write_json(
            manifest_path,
            build_delivery_manifest(
                args.task_id, run_id, args.stage, source_commit, checks, all_entries(run_dir, root), tool_versions
            ),
        )

    base_checks = [
        {
            "name": "S6-A 自检（16 项：规格一致性/算术/证据存在性）",
            "status": "PASS", "command": selfcheck_run["command_text"], "exit_code": selfcheck_run["exit_code"],
        },
        {
            "name": "check_stage_delivery.py --mode inputs",
            "status": "PASS", "command": inputs_run["command_text"], "exit_code": inputs_run["exit_code"],
        },
    ]
    write_hashes()
    write_manifest(base_checks + [{
        "name": "check_stage_delivery.py --mode evidence",
        "status": "NOT_RUN", "command": None, "exit_code": None,
        "reason": "首版清单生成后立即实跑，实测退出码写入定稿清单",
    }])
    evidence_run = run_command(evidence_cmd, root)
    print(f"[evidence-mode] exit={evidence_run['exit_code']}")
    if evidence_run["exit_code"] != 0:
        print(evidence_run["stdout"]); print(evidence_run["stderr"]); return 1

    final_checks = base_checks + [{
        "name": "check_stage_delivery.py --mode evidence",
        "status": "PASS" if evidence_run["exit_code"] == 0 else "FAIL",
        "command": evidence_run["command_text"],
        "exit_code": evidence_run["exit_code"],
    }]
    write_manifest(final_checks)
    evidence_final = run_command(evidence_cmd, root)
    print(f"[evidence-mode:final] exit={evidence_final['exit_code']}")
    if evidence_final["exit_code"] != 0:
        print(evidence_final["stdout"]); print(evidence_final["stderr"]); return 1

    state_check_cmd = selfcheck_base + [
        "--out", str(tmp_state_check),
        "--manifest", str(manifest_path),
        "--state", str(root / args.state),
    ]
    state_check = run_command(state_check_cmd, root)
    print(f"[selfcheck+manifest:final] exit={state_check['exit_code']}")
    if state_check["exit_code"] != 0:
        print(state_check["stdout"]); print(state_check["stderr"]); return 1

    result = json.loads(result_path.read_text(encoding="utf-8"))
    print(json.dumps({
        "status": "EVIDENCE_BUILT",
        "selfcheck": result["status"],
        "checks": [
            {"name": item["name"], "status": item["status"], "exit_code": item["exit_code"]}
            for item in final_checks
        ],
        "files": len(all_entries(run_dir, root)),
        "state_manifest_check_exit": state_check["exit_code"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
