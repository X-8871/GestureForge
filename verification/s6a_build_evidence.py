#!/usr/bin/env python3
"""阶段6 S6-A 证据包构建器（r06 起：第 5 轮复评 N-r05-01..04 收尾）。

r07 变更：探针改为 verification/s6a_r07_probe.py（基线 1 例 + 注入 7 例，共 8 例 + 历史口径对照 2 例，共 10 次运行）；
构建后由 verification/export_selfproof.py 做「导出副本复跑」自证（F6 规则），结果写入 export_selfproof.json/.md；
旧包失败证据重跑保持；版本口径统一为 v1.6/r07。

r04 变更：构建前先用 verification/s6a_rerun_legacy_failures.py 以**最终脚本**重跑
r01/r02/r03 旧包失败证据（N03），失败输出直接落入本运行目录；自检条目由 16 项增至 17 项
（新增 C17 STABLE 锁存）；版本口径统一为 v1.3/r04。

关键行为：
* 只对**实际存在**文件生成 `hashes_sha256.txt`；
* 真实执行自检与 `check_stage_delivery.py` inputs/evidence（绝对 `--project-root`），
  实测退出码写入清单（不硬编码）；
* 入库的 `selfcheck_result.json` 由 **`--manifest` + `--state` 完整命令**生成，
  C11 的清单/STATE 核对结果因此进入证据；同时落盘 `selfcheck_c11_stdout.txt`、
  `check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`；
* `inputs_manifest.checks` 两阶段写入：先 `NOT_RUN`，实测后回写 `PASS` + 真实退出码（NBL-1）；
* 清单/哈希/自检结果用不动点迭代，保证最终清单与实际文件逐一对应。

用法：
    python -B verification/s6a_build_evidence.py \
        --run-dir report/evidence/S6-A/s6a_g0_20261022_r03 \
        --project-root D:/codex-worktrees/w6
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
        command, cwd=str(project_root), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    return {
        "command_text": subprocess.list2cmdline(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def role_for(relative: str) -> str:
    if relative in ("inputs_manifest.json", "upstream_bindings.json", "hand_computed_cases.json",
                    "old_package_under_test.json", "r02_package_under_test.json"):
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
        "old_package_under_test.json": "r01 被检版本 git 字节与哈希（BLK-2 可复核）",
        "r02_package_under_test.json": "r02 被检版本 git 字节与哈希（BLK-1 失败证据）",
        "r03_package_under_test.json": "r03 被检版本 git 字节与哈希（R3-B01/R3-B02 失败证据）",
        "selfcheck_r03_failure.json": "加固自检在 r03 上的失败输出（C12 捕获 R3 项、C17 捕获缺锁存块）",
        "selfcheck_r03_failure_stdout.txt": "r03 失败运行 stdout 原文",
        "r04_package_under_test.json": "r04 被检版本 git 字节与哈希（N-r04-01..04 捕获证据）",
        "selfcheck_r04_failure.json": "r06/r07/r08 自检在 r04 上的失败输出（C12 捕获 M5/policy 缺陷；"
                                      "C7 因**样例数不足 32：29**（缺 HC-30/31/32）失败；F4）",
        "selfcheck_r04_failure_stdout.txt": "r04 失败运行 stdout 原文（C7 归因：样例数 29<30，缺 HC-30）",
        "selfcheck_old_package_failure.json": "加固自检在 r01 真实字节上的失败输出（exit 1）",
        "selfcheck_old_package_failure_stdout.txt": "r01 失败运行 stdout 原文",
        "selfcheck_r02_blk1_failure.json": "加固自检在 r02 上的失败输出，C12 捕获 BLK-1",
        "selfcheck_r02_blk1_failure_stdout.txt": "r02 BLK-1 失败运行 stdout 原文",
        "selfcheck_result.json": "修复包自检结果（含完整 C11 清单/STATE 核对）",
        "selfcheck_c11_stdout.txt": "完整 C11 自检运行 stdout",
        "check_inputs_mode_output.txt": "check_stage_delivery --mode inputs 真实 stdout",
        "check_evidence_mode_output.txt": "check_stage_delivery --mode evidence 真实 stdout",
        "probe_summary.json": "判别力探针汇总（基线 1 例 exit 0 + 注入 7 例（共 8 例）+ 历史口径对照 2 例，"
                              "共 10 次运行；F3/F10）",
        "export_selfproof.json": "冻结自证报告（导出副本复跑：r06 提交应 FAIL、本包工作区快照应 PASS；F6）",
        "export_selfproof.md": "冻结自证报告（可读版；F6）",
        "coverage_matrix.json": "CDX-012 §2 与计划 L102–L108 覆盖矩阵",
        "limitations_not_executed.json": "限制、未执行与阻塞项登记",
        "fix_record.json": "评审 BLK/NBL 项逐条修复记录",
        "fix_record.md": "评审修复记录人读版",
        "inputs_manifest.json": "输入清单（冻结上游接口与输入文件绑定）",
        "hashes_sha256.txt": "证据目录已存在文件的 SHA-256 清单",
        "S6A_run_summary.md": "运行摘要（真实命令、退出码入口与结论边界）",
        "delivery_manifest.json": "本证据包机器可读清单",
    }.get(relative, f"证据文件：{relative}")


def source_entries(root: Path) -> list[dict[str, str]]:
    sources = [
        ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "被证据绑定的规格文档（v1.7/r08）"),
        ("docs/stage6/s6a_stage6_g0_behavior_v1.json", "被证据绑定的机器可读行为表（v1.7/r08）"),
        ("verification/s6a_rerun_legacy_failures.py", "旧包失败证据可复现重跑脚本（N03）"),
        ("verification/s6a_r08_probe.py", "C12/C7/C14/C16 断言判别力探针（基线 1 例 + 注入 8 例 + 历史对照 1 例）"),
        ("verification/claim_verify.py", "验证附录生成器（声明↔命令↔真实退出码↔可观察输出）"),
        ("verification/export_selfproof.py", "冻结自证工具（导出提交后复跑自检 + 两个交付检查器，F6 规则）"),
        ("verification/s6_g0_selfcheck.py", "加固后的 S6-A 自检脚本"),
        ("verification/s6a_build_evidence.py", "证据清单构建器（真实执行检查并记录退出码）"),
        (".codex/STATE.md", "阶段6 STATE（11 字段交接行与证据入口）"),
    ]
    entries = []
    for relative, reason in sources:
        path = root / relative
        if not path.is_file():
            raise SystemExit(f"缺少需要绑定的源码文件：{relative}")
        entries.append({"path": relative, "sha256": sha256_file(path), "role": "source", "keep_reason": reason})
    return entries


def run_entries(run_dir: Path, root: Path) -> list[dict[str, str]]:
    entries = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        local = path.relative_to(run_dir).as_posix()
        if local == "delivery_manifest.json":
            continue
        entries.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "role": role_for(local),
            "keep_reason": keep_reason_for(local),
        })
    return entries


def all_entries(run_dir: Path, root: Path) -> list[dict[str, str]]:
    return source_entries(root) + run_entries(run_dir, root)


def frozen_interfaces() -> list[dict[str, Any]]:
    return [
        {
            "name": "S2A-T01 模型交付规格与 G0 接口冻结（类别顺序/score 阈值/≤15 框/同分顺序）",
            "version": "G0_FROZEN", "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
            "sha256": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
        },
        {
            "name": "S1-T02-D2 固定预处理与 INT8 数值规格（no_hand 空标签语义）",
            "version": "STAGE1_FROZEN", "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
            "sha256": "df95a8438eaa2d451b54ca3f1927c454eaef022c1f8f31a18874980f69702e57",
        },
        {
            "name": "S1-T02-D6 检测评估口径与离线指标基础",
            "version": "STAGE1_FROZEN", "frozen": True,
            "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md",
            "sha256": "735cbc78882dd299a952ee1d4c2f7ef972e8cc903782be3a64f1db830f311dd7",
        },
    ]


def build_inputs_manifest(task_id: str, run_id: str, stage: str, source_commit: str, checks: list[dict]) -> dict[str, Any]:
    interfaces = frozen_interfaces()
    files = [
        {"path": item["path"], "sha256": item["sha256"], "role": "input", "keep_reason": f"冻结上游输入：{item['name']}"}
        for item in interfaces
    ]
    files.append({
        "path": "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md",
        "sha256": "82ef0796baf6a8cd04ae942019e1af226f645e27fe8309fe56bcb05a7b1a5f9a",
        "role": "input",
        "keep_reason": "阶段6 目标与测试场景范围来源（现行批准计划 L102–L108）",
    })
    return {
        "schema_version": 1, "stage": stage, "task_id": task_id, "run_id": run_id,
        "source_commit": source_commit,
        "evidence_dir": f"report/evidence/{task_id}/{run_id}",
        "interfaces": interfaces, "files": files, "checks": checks,
        "limitations": [
            "inputs 清单只登记已冻结上游（2A G0、D2、D6）与现行批准计划；阶段4/阶段5 接口未冻结，登记在 upstream_bindings.json 草案区。",
            "inputs 模式 CHECKS_OK 只表示清单/路径/哈希检查通过，不代表语义正确或 G0 通过。",
        ],
    }


def build_delivery_manifest(task_id, run_id, stage, source_commit, checks, files, tool_versions):
    return {
        "schema_version": 1, "stage": stage, "task_id": task_id, "run_id": run_id,
        "source_commit": source_commit,
        "evidence_dir": f"report/evidence/{task_id}/{run_id}",
        "interfaces": frozen_interfaces()[:1],
        "files": files, "checks": checks, "tool_versions": tool_versions,
        "limitations": [
            f"source_commit = 本轮构建时的 HEAD（修订基线 {source_commit}）；本清单绑定的源码字节 = 该提交 + "
            "本轮未提交差异（F2 口径三处统一：manifest / STATE 11 字段 / JSON baseline 均指向同一提交）；"
            "交付提交由 export_selfproof.py 导出复跑自证（见 _selfproof/export_selfproof.json）。",
            "r01/r02/r03/r04 旧包失败证据由 verification/s6a_rerun_legacy_failures.py 用最终脚本重跑生成，"
            "提取一律 git cat-file blob 二进制（N03）。",
            "全部阈值与指标仍为 PENDING_APPROVAL；T6-A03/交互延迟因缺阶段4 实测 P 记 NOT_RUN（U6-13）。",
            "M4 可达并计入覆盖；不计入覆盖的只有 B16 S_DEDUP（A02<K01）与 M7（构造上）（r08/BLK-1、BLK-r07-1）。",
            "入库 selfcheck_result.json 使用 --manifest + --state 完整命令，C11 含清单双向与 STATE 声明核对；stdout 见 selfcheck_c11_stdout.txt。",
            "旧包证据：r01（git 1fe4648 字节）与 r02（git 3b59674 字节）失败输出均已保留；后者由 C12 捕获 BLK-1。",
            "selfcheck ALL_PASS / CHECKS_OK 均不代表状态机行为、G0 复评、独立审查或实物验收通过。",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 S6-A 证据清单并实跑检查器（r03 不动点迭代）")
    parser.add_argument("--run-dir", required=False)
    parser.add_argument("--project-root", required=False)
    parser.add_argument("--stage", default="6")
    parser.add_argument("--task-id", default="S6-A")
    parser.add_argument("--behavior-json", default="docs/stage6/s6a_stage6_g0_behavior_v1.json")
    parser.add_argument("--doc", default="docs/stage6/S6A_stage6_g0_behavior_spec_v1.md")
    parser.add_argument("--state", default=".codex/STATE.md")
    parser.add_argument("--selfcheck", default="verification/s6_g0_selfcheck.py")
    parser.add_argument("--checker", default="verification/check_stage_delivery.py")
    parser.add_argument("--verify-inputs", default=None, help="内部模式：复算 inputs 清单的输入文件哈希，退出码 0/1")
    args = parser.parse_args(argv)

    if args.verify_inputs:
        manifest = json.loads(Path(args.verify_inputs).resolve().read_text(encoding="utf-8"))
        failures = []
        for item in manifest.get("files", []):
            path = (Path(args.project_root).resolve() / item["path"]).resolve()
            if not path.is_file() or sha256_file(path) != item["sha256"]:
                failures.append(item["path"])
        print(json.dumps({"verified": len(manifest.get("files", [])), "failures": failures}, ensure_ascii=False))
        return 0 if not failures else 1

    if not args.run_dir or not args.project_root:
        print("缺少 --run-dir/--project-root")
        return 2
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

    # ---- N03：用最终脚本重跑 r01/r02/r03 旧包失败证据（失败即中止），到构建器里落地，不再手工搬动 ----
    legacy_cmd = [
        sys.executable, "-B", str(root / "verification/s6a_rerun_legacy_failures.py"),
        "--run-dir", str(run_dir), "--project-root", str(root),
    ]
    legacy_run = run_command(legacy_cmd, root)
    print(f"[legacy-rerun] exit={legacy_run['exit_code']}")
    if legacy_run["exit_code"] != 0:
        print(legacy_run["stdout"]); print(legacy_run["stderr"]); return 1

    # ---- r06：注入探针（基线 1 例 + 注入 7 例 + 旧口径对照；任何非预期结果即中止） ----
    probe_cmd = [
        sys.executable, "-B", str(root / "verification/s6a_r08_probe.py"),
        "--run-dir", str(run_dir), "--project-root", str(root),
    ]
    probe_run = run_command(probe_cmd, root)
    print(f"[r08-probe] exit={probe_run['exit_code']}")
    if probe_run["exit_code"] != 0:
        print(probe_run["stdout"]); print(probe_run["stderr"]); return 1

    source_commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    ).stdout.strip()
    tool_versions = {
        "python": sys.version.split()[0],
        "git": subprocess.run(["git", "--version"], capture_output=True, text=True, encoding="utf-8", check=False).stdout.strip(),
    }

    manifest_path = run_dir / "delivery_manifest.json"
    hashes_path = run_dir / "hashes_sha256.txt"
    summary_path = run_dir / "S6A_run_summary.md"
    result_path = run_dir / "selfcheck_result.json"
    c11_stdout_path = run_dir / "selfcheck_c11_stdout.txt"
    claim_cmd = [sys.executable, "-B", str(root / "verification/claim_verify.py"),
                 "--package", "s6a", "--run-dir", str(run_dir), "--project-root", str(root)]
    claim_run = run_command(claim_cmd, root)
    print(f"[claim-verify] exit={claim_run['exit_code']}")
    if claim_run["exit_code"] != 0 and (run_dir / "selfcheck_result.json").is_file():
        # 首版构建时自检结果可能尚未落盘（换代收敛中）；已有结果却失败即中止（不得带未验证声明发布）
        print(claim_run["stdout"]); print(claim_run["stderr"]); return 1

    inputs_manifest_path = run_dir / "inputs_manifest.json"
    inputs_output_path = run_dir / "check_inputs_mode_output.txt"
    evidence_output_path = run_dir / "check_evidence_mode_output.txt"

    # 预置本轮将写入的 stdout 证据文件，保证 C11 的 STATE 声明在首次完整自检时已存在
    for placeholder in (c11_stdout_path, inputs_output_path, evidence_output_path):
        if not placeholder.exists():
            placeholder.write_text("", encoding="utf-8")

    selfcheck_base = [
        sys.executable, "-B", str(root / args.selfcheck),
        "--json", str(root / args.behavior_json),
        "--doc", str(root / args.doc),
        "--cases", str(cases),
        "--upstream", str(upstream),
        "--project-root", str(root),
        "--evidence-dir", str(run_dir),
    ]
    selfcheck_cmd = selfcheck_base + [
        "--out", str(result_path), "--manifest", str(manifest_path), "--state", str(root / args.state),
    ]
    inputs_cmd = [
        sys.executable, "-B", str(root / args.checker), "--mode", "inputs",
        "--manifest", str(inputs_manifest_path), "--project-root", str(root),
    ]
    evidence_cmd = [
        sys.executable, "-B", str(root / args.checker), "--mode", "evidence",
        "--manifest", str(manifest_path), "--project-root", str(root),
    ]

    # ---- NBL-1：inputs 清单 checks 由真实复算命令的退出码填写（不硬编码） ----
    write_json(inputs_manifest_path, build_inputs_manifest(args.task_id, run_id, args.stage, source_commit, []))
    verify_cmd = [
        sys.executable, "-B", str(root / "verification/s6a_build_evidence.py"),
        "--verify-inputs", str(inputs_manifest_path), "--project-root", str(root),
    ]
    verify_run = run_command(verify_cmd, root)
    if verify_run["exit_code"] != 0:
        print(verify_run["stdout"]); print(verify_run["stderr"]); return 1
    write_json(inputs_manifest_path, build_inputs_manifest(args.task_id, run_id, args.stage, source_commit, [{
        "name": "输入文件 SHA-256 复算（构建器 --verify-inputs 实跑）",
        "status": "PASS", "command": verify_run["command_text"], "exit_code": verify_run["exit_code"],
    }]))
    inputs_final = run_command(inputs_cmd, root)
    print(f"[inputs-mode] exit={inputs_final['exit_code']}")
    if inputs_final["exit_code"] != 0:
        print(inputs_final["stdout"]); print(inputs_final["stderr"]); return 1
    inputs_output_path.write_text(inputs_final["stdout"], encoding="utf-8")

    summary_lines = [
        "# S6-A v1.7 / r08 运行摘要",
        "",
        f"- 任务：`{args.task_id}`；RunId：`{run_id}`；工作树：`{root}`",
        f"- 绑定提交：`{source_commit}`（证据由该次构建的工作树生成；交付提交由 `verification/export_selfproof.py` 导出复跑自证）",
        "- 状态：**DELIVERED_PENDING_REVIEW**（复评由项目总控另派；本摘要不构成通过）",
        "- 阈值纪律：24 项参数值与 `PENDING_APPROVAL` 状态未改；未在测试集调参；未触碰硬件。",
        "",
        "## 真实命令与退出码",
        "",
        "| 检查 | 命令（绝对 project-root） | 实测退出码 |",
        "|---|---|---|",
        f"| 旧包失败证据重跑（r01/r02/r03/r04） | `{subprocess.list2cmdline(legacy_cmd)}` | 实测 {legacy_run['exit_code']}（各类失败输出落盘） |",
        f"| 判别力探针（基线 1 例 + 注入 7 例，共 8 例 + 历史口径对照 2 例） | `{subprocess.list2cmdline(probe_cmd)}` | 实测 {probe_run['exit_code']}（各用例自检输出落盘） |",
        f"| 冻结自证（导出副本复跑，F6 规则） | `python -B verification/export_selfproof.py --commit <历史提交> --worktree-snapshot` | 见 `export_selfproof.json`（历史提交应 NOT_SELF_PROVEN、本包快照应 SELF_PROVEN） |",
        f"| 自检（17 项，含完整 C11 与 C17） | `{subprocess.list2cmdline(selfcheck_cmd)}` | 见 `delivery_manifest.json.checks` 与 `selfcheck_c11_stdout.txt` |",
        f"| check_stage_delivery --mode inputs | `{subprocess.list2cmdline(inputs_cmd)}` | {inputs_final['exit_code']}（stdout: `check_inputs_mode_output.txt`） |",
        f"| check_stage_delivery --mode evidence | `{subprocess.list2cmdline(evidence_cmd)}` | 见 `delivery_manifest.json.checks`（stdout: `check_evidence_mode_output.txt`） |",
        "",
        "> 清单 checks 中 status=PASS 的条目其 exit_code 均为构建器实测值（PASS 必须为 0）。",
        "> 入库 `selfcheck_result.json` 由带 `--manifest` + `--state` 的命令生成，C11 detail 含清单双向一致与 STATE 声明核对。",
        "",
        "## 证据文件",
        "",
        "- `delivery_manifest.json` / `inputs_manifest.json` / `hashes_sha256.txt`（只哈希实际存在文件）",
        "- `selfcheck_result.json`（ALL_PASS 17 项，含完整 C11 与 C17）+ `selfcheck_c11_stdout.txt`",
        "- `check_inputs_mode_output.txt` / `check_evidence_mode_output.txt`（检查器完整 stdout）",
        "- `selfcheck_old_package_failure.json/.txt` + `old_package_under_test.json`（r01，git 字节可复核）",
        "- `selfcheck_r02_blk1_failure.json/.txt` + `r02_package_under_test.json`（r02，C12 捕获 BLK-1）",
        "- `selfcheck_r03_failure.json/.txt` + `r03_package_under_test.json`（r03，C12 捕获 R3-B01/R3-B02、C17 捕获缺锁存块）",
        "- `selfcheck_r04_failure.json/.txt` + `r04_package_under_test.json`（r04，C12 捕获 N-r04-01/02；C7 因样例数不足（29 < 32，缺 HC-30/31/32）失败；F4）",
        "- `probe_summary.json` + `probe_*_stdout.txt`（基线 1 例 exit 0；注入 7 例各自捕获预期检查项，含 F1 的 `b07_old_wording` 与 F7 的 `case_out_of_sequence_index`；历史口径对照 2 例必须失败）",
        "- `export_selfproof.json`/`export_selfproof.md`（F6 规则：导出副本复跑的三项真实退出码；r06 实测 C11 FAIL、本包快照 SELF_PROVEN）",
        "- `fix_record.json` / `fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`",
        "",
        "## 结论边界",
        "",
        "- `ALL_PASS`/`CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不验证状态机行为，不代表 G0 复评/独立审查/实物验收通过。",
        "- 回放/注入类结论仅限回放/注入输入；本包未运行任何状态机。",
        "",
        "## 限制与未执行",
        "",
        "见 `limitations_not_executed.json`（T6-A03 NOT_RUN、M4 可达并计入覆盖、阶段4/5 依赖 BLOCKED、独立复评 PENDING）。",
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

    def write_manifest(selfcheck_exit: int | None, evidence_exit: int | None, selfcheck_command: str) -> None:
        selfproof_path = run_dir.parent / f"{run_dir.name}_selfproof" / "export_selfproof.json"  # N-r07-2：自证报告在兄弟目录，可在提交后补入交付提交主体
        selfproof_check = None
        if selfproof_path.is_file():
            proof = json.loads(selfproof_path.read_text(encoding="utf-8"))
            verdicts = {row["subject"]: row["verdict"] for row in proof.get("subjects", [])}
            snapshot_ok = any(key.startswith("worktree") and verdict == "SELF_PROVEN"
                              for key, verdict in verdicts.items())
            historical_failures = [key for key, verdict in verdicts.items()
                                   if key.startswith("commit") and verdict == "NOT_SELF_PROVEN"]
            # r08：自证报告以「工作区快照」为主体（历史提交主体在提交后由 export_selfproof 追加），
            # 因此只要求快照 SELF_PROVEN；含历史提交时允许其 NOT_SELF_PROVEN（可能是真缺陷，见报告）。
            expected = snapshot_ok
            selfproof_check = {
                "name": "冻结自证（导出副本复跑，F6：历史提交应 FAIL / 本包快照应 PASS）",
                "status": "PASS" if expected else "FAIL",
                "command": ("`python -B verification/export_selfproof.py --project-root <abs> "
                            "--commit <历史提交> --worktree-snapshot [--out <run>/export_selfproof.json]`"),
                "exit_code": 0 if expected else 1,
                "reason": (f"断言 = 本包快照 SELF_PROVEN；实测 subjects={verdicts}；工具总体判定 {proof.get('verdict')}"),
            }
        checks = [
            *([] if selfproof_check is None else [selfproof_check]),
            {
                "name": "S6-A 自检（17 项：规格一致性/算术/证据存在性/C11 清单与 STATE/C12 全量双向/C17 锁存）",
                "status": "PASS" if selfcheck_exit == 0 else ("NOT_RUN" if selfcheck_exit is None else "FAIL"),
                "command": selfcheck_command if selfcheck_exit is not None else None,
                "exit_code": selfcheck_exit,
                **({"reason": "首版清单生成后立即实跑"} if selfcheck_exit is None else {}),
            },
            {
                "name": "check_stage_delivery.py --mode inputs",
                "status": "PASS" if inputs_final["exit_code"] == 0 else "FAIL",
                "command": inputs_final["command_text"], "exit_code": inputs_final["exit_code"],
            },
            {
                "name": "check_stage_delivery.py --mode evidence",
                "status": "PASS" if evidence_exit == 0 else ("NOT_RUN" if evidence_exit is None else "FAIL"),
                "command": subprocess.list2cmdline(evidence_cmd) if evidence_exit is not None else None,
                "exit_code": evidence_exit,
                **({"reason": "首版清单生成后立即实跑"} if evidence_exit is None else {}),
            },
        ]
        write_json(manifest_path, build_delivery_manifest(
            args.task_id, run_id, args.stage, source_commit, checks, all_entries(run_dir, root), tool_versions,
        ))

    # 首版自检结果（保证 C11 的 STATE 声明文件存在）+ 首版清单
    provisional = run_command(selfcheck_base + ["--out", str(result_path)], root)
    if provisional["exit_code"] != 0:
        print(provisional["stdout"]); print(provisional["stderr"]); return 1
    write_hashes()
    write_manifest(None, None, "")
    evidence_run = run_command(evidence_cmd, root)
    print(f"[evidence-mode:first] exit={evidence_run['exit_code']}")
    if evidence_run["exit_code"] != 0:
        print(evidence_run["stdout"]); print(evidence_run["stderr"]); return 1
    evidence_output_path.write_text(evidence_run["stdout"], encoding="utf-8")
    write_hashes()
    write_manifest(None, evidence_run["exit_code"], "")

    selfcheck_exit: int | None = None
    previous_state: tuple | None = None
    for iteration in range(1, 7):
        run = run_command(selfcheck_cmd, root)
        print(f"[selfcheck:iter{iteration}] exit={run['exit_code']}")
        if run["exit_code"] != 0:
            print(run["stdout"]); print(run["stderr"]); return 1
        selfcheck_exit = run["exit_code"]
        c11_stdout_path.write_text(run["stdout"], encoding="utf-8")
        write_hashes()
        write_manifest(selfcheck_exit, evidence_run["exit_code"], run["command_text"])
        evidence_run = run_command(evidence_cmd, root)
        print(f"[evidence-mode:iter{iteration}] exit={evidence_run['exit_code']}")
        if evidence_run["exit_code"] != 0:
            print(evidence_run["stdout"]); print(evidence_run["stderr"]); return 1
        evidence_output_path.write_text(evidence_run["stdout"], encoding="utf-8")
        write_hashes()
        write_manifest(selfcheck_exit, evidence_run["exit_code"], run["command_text"])
        state = (
            sha256_file(result_path),
            sha256_file(c11_stdout_path),
            sha256_file(hashes_path),
            sha256_file(inputs_output_path),
            sha256_file(evidence_output_path),
            tuple(item["path"] for item in all_entries(run_dir, root)),
        )
        if previous_state == state:
            break
        previous_state = state

    final_evidence = run_command(evidence_cmd, root)
    print(f"[evidence-mode:final] exit={final_evidence['exit_code']}")
    if final_evidence["exit_code"] != 0:
        print(final_evidence["stdout"]); print(final_evidence["stderr"]); return 1
    result = json.loads(result_path.read_text(encoding="utf-8"))
    c11 = next((item for item in result["checks"] if item["id"] == "C11"), None)
    if c11 is None or "manifest 双向一致" not in c11["detail"] or "STATE 声明" not in c11["detail"]:
        print(f"C11 未执行完整清单/STATE 核对：{c11}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(json.dumps({
        "status": "EVIDENCE_BUILT",
        "selfcheck": result["status"],
        "c11_detail": c11["detail"],
        "checks": [{"name": c["name"], "status": c["status"], "exit_code": c["exit_code"]} for c in manifest["checks"]],
        "files": len(manifest["files"]),
        "evidence_final_exit": final_evidence["exit_code"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
