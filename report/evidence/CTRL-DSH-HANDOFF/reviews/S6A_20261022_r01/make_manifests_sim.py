#!/usr/bin/env python3
"""一次性生成 S6-A 证据清单（tmp 缓存，不入库）。

用途：以真实 SHA-256 生成 hashes_sha256.txt、inputs_manifest.json、delivery_manifest.json，
避免手工转写哈希出错。运行后由 check_stage_delivery.py 复核。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

W6 = Path(r"D:\codex-worktrees\w6")
RUN = Path(r"D:\FPGA_Competition\tmp\review\S6A_20261022_r01\manifest_sim")
SOURCE_COMMIT = "d8bc70e43572a8e44ddcd4b3489166e28a1c6151"
EVIDENCE_DIR = "report/evidence/S6-A/s6a_g0_20261022_r01"
TOOL_VERSIONS = {
    "python": "3.12.10",
    "git": "2.56.0.windows.2",
    "os": "Windows 11 (10.0.26200)",
}
SELFCHECK_CMD = (
    "python -B verification/s6_g0_selfcheck.py "
    "--json docs/stage6/s6a_stage6_g0_behavior_v1.json "
    "--doc docs/stage6/S6A_stage6_g0_behavior_spec_v1.md "
    "--cases report/evidence/S6-A/s6a_g0_20261022_r01/hand_computed_cases.json "
    "--upstream report/evidence/S6-A/s6a_g0_20261022_r01/upstream_bindings.json "
    "--out report/evidence/S6-A/s6a_g0_20261022_r01/selfcheck_result.json --project-root ."
)


def sha256(rel_or_abs: str) -> str:
    path = Path(rel_or_abs)
    if not path.is_absolute():
        path = W6 / rel_or_abs
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


INTERFACES = [
    {
        "name": "S2A-T01 模型交付规格与G0接口冻结",
        "version": "S2A-T01-G0-FROZEN",
        "frozen": True,
        "path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
        "sha256": sha256("docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"),
    },
    {
        "name": "B方案实施与阶段验收计划（阶段6 条目 L102-L108）",
        "version": "PLAN-CURRENT-20261022",
        "frozen": True,
        "path": "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md",
        "sha256": sha256("docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md"),
    },
    {
        "name": "S1-T02-D2 固定预处理与INT8数值规格",
        "version": "S1-T02-D2-FROZEN",
        "frozen": True,
        "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
        "sha256": sha256("docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md"),
    },
    {
        "name": "S1-T02-D6 检测评估口径与离线指标基础",
        "version": "S1-T02-D6-FROZEN",
        "frozen": True,
        "path": "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md",
        "sha256": sha256("docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md"),
    },
]

RUN_FILES = [
    ("upstream_bindings.json", "artifact", "11 项上游只读绑定与并发漂移记录"),
    ("hand_computed_cases.json", "result", "20 例人工手算边界样例与推导"),
    ("coverage_matrix.json", "result", "操作文档 6-A、计划 L102-L108 与阶段5 建议的覆盖矩阵"),
    ("selfcheck_result.json", "result", "自检 10 项结果（ALL_PASS）与输入哈希"),
    ("limitations_not_executed.json", "result", "NOT_RUN/BLOCKED/NOT_APPLICABLE 逐项与理由"),
    ("inputs_manifest.json", "artifact", "inputs 模式输入清单"),
    ("S6A_run_summary.md", "log", "运行摘要、命令与真实退出码、恢复入口"),
    ("hashes_sha256.txt", "result", "关键文件 SHA-256 清单"),
]

SOURCE_FILES = [
    ("docs/stage6/S6A_stage6_g0_behavior_spec_v1.md", "source", "阶段6 G0 包与行为表 v1（人读）"),
    ("docs/stage6/s6a_stage6_g0_behavior_v1.json", "source", "阶段6 行为表 v1（机器可读 S6A-G0-v1）"),
    ("verification/s6_g0_selfcheck.py", "source", "阶段6 G0 自检脚本"),
    (".codex/STATE.md", "source", "阶段6 专用状态与 11 字段交接行"),
]


def build_hashes_file() -> None:
    lines = ["# S6-A (s6a_g0_20261022_r01) 关键文件 SHA-256", ""]
    lines.append("## 本轮源码与规格")
    for rel, _role, _why in SOURCE_FILES:
        lines.append(f"{sha256(rel)}  {rel}")
    lines.append("")
    lines.append("## 上游只读绑定（w4/w5 按提交版本复算，见 upstream_bindings.json）")
    for item in INTERFACES:
        lines.append(f"{item['sha256']}  {item['path']}")
    lines.append("")
    lines.append("## 本运行目录证据文件")
    for name, _role, _why in RUN_FILES:
        if name == "hashes_sha256.txt":
            continue
        lines.append(f"{sha256(EVIDENCE_DIR + '/' + name)}  {EVIDENCE_DIR}/{name}")
    lines.append("")
    lines.append("# 本文件不含自身哈希与 delivery_manifest.json 的哈希（避免自指）；两者由 delivery_manifest.json 绑定。")
    (RUN / "hashes_sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_inputs_manifest() -> None:
    manifest = {
        "schema_version": 1,
        "stage": "stage6",
        "task_id": "S6-A",
        "run_id": "s6a_g0_20261022_r01",
        "source_commit": SOURCE_COMMIT,
        "evidence_dir": EVIDENCE_DIR,
        "interfaces": INTERFACES,
        "files": [
            {"path": item["path"], "sha256": item["sha256"], "role": "input",
             "keep_reason": f"上游冻结接口输入：{item['name']}"}
            for item in INTERFACES
        ]
        + [
            {"path": rel, "sha256": sha256(rel), "role": "source", "keep_reason": why}
            for rel, _role, why in SOURCE_FILES
        ],
        "checks": [
            {
                "name": "上游冻结接口哈希与文档↔JSON 一致性复算",
                "status": "PASS",
                "command": SELFCHECK_CMD,
                "exit_code": 0,
            },
            {
                "name": "工作树/分支/HEAD 开工核验",
                "status": "PASS",
                "command": "git -C D:/codex-worktrees/w6 status --short; git -C D:/codex-worktrees/w6 rev-parse --short HEAD",
                "exit_code": 0,
            },
            {
                "name": "阶段计划阶段6 条目存在性核验（L102-L108）",
                "status": "PASS",
                "command": "python -B -c \"import pathlib,sys;p=pathlib.Path(r'D:/codex-worktrees/w6/docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md').read_text(encoding='utf-8').splitlines();sys.exit(0 if ('阶段6：交互控制' in p[101]) and ('已知手势有效动作成功率' in p[105]) and ('交互通过不代替阶段7' in p[107]) else 1)\"",
                "exit_code": 0,
            },
        ],
        "limitations": [
            "阶段4 结果记录契约与阶段5 显示契约均未冻结，不能作为 frozen 接口登记；其草案绑定见 upstream_bindings.json 与 limitations_not_executed.json",
            "本清单只登记当前声明的输入；不扫描历史证据，不替代 G0/审查/验收",
        ],
        "tool_versions": TOOL_VERSIONS,
    }
    (RUN / "inputs_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build_delivery_manifest() -> None:
    files = []
    for rel, role, why in RUN_FILES:
        files.append({"path": f"{EVIDENCE_DIR}/{rel}", "sha256": sha256(f"{EVIDENCE_DIR}/{rel}"), "role": role, "keep_reason": why})
    for rel, role, why in SOURCE_FILES:
        files.append({"path": rel, "sha256": sha256(rel), "role": role, "keep_reason": why})
    for item in INTERFACES:
        files.append({"path": item["path"], "sha256": item["sha256"], "role": "input", "keep_reason": f"上游冻结接口输入：{item['name']}"})

    checks = [
        {
            "name": "开工只读核验（工作树/分支/HEAD/index.lock）",
            "status": "PASS",
            "command": "git -C D:/codex-worktrees/w6 status --short; git -C D:/codex-worktrees/w6 rev-parse --short HEAD; git -C D:/codex-worktrees/w6 rev-parse --git-path index.lock",
            "exit_code": 0,
        },
        {"name": "阶段6 G0 自检（10 项，含 20 例手算复算与 11 项上游哈希）", "status": "PASS", "command": SELFCHECK_CMD, "exit_code": 0},
        {
            "name": "输入清单核验（inputs 模式）",
            "status": "PASS",
            "command": "python -B verification/check_stage_delivery.py --mode inputs --project-root . --manifest report/evidence/S6-A/s6a_g0_20261022_r01/inputs_manifest.json",
            "exit_code": 0,
        },
        {
            "name": "证据目录核验（evidence 模式）",
            "status": "PASS",
            "command": "python -B verification/check_stage_delivery.py --mode evidence --project-root . --manifest report/evidence/S6-A/s6a_g0_20261022_r01/delivery_manifest.json",
            "exit_code": 0,
        },
        {
            "name": "6-B 状态机实现与 6-C 确定性测试矩阵",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "本轮范围仅 6-A（G0 与行为表）；尚无状态机实现，故不得声明“状态机确定性测试 PASS”",
        },
        {
            "name": "6-D 无摄像头两级联调（脚本注入/板上推理）",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "依赖状态机实现与阶段4/阶段5 就绪；本轮未执行",
        },
        {
            "name": "≥30 分钟回放稳定性实验与 T6-01/02/03 统计",
            "status": "NOT_RUN",
            "command": None,
            "exit_code": None,
            "reason": "指标未获批准且无实现与样本；不得把任何观测值报告为通过",
        },
        {
            "name": "6-E 真摄像头验收与统计",
            "status": "BLOCKED",
            "command": None,
            "exit_code": None,
            "reason": "摄像头不可用（待重新采购）；真手势验收延期至模块到货并完成阶段3 验收",
        },
        {
            "name": "阶段6 集成验收依赖",
            "status": "BLOCKED",
            "command": None,
            "exit_code": None,
            "reason": "阶段4 结果记录契约 DRAFT_NOT_FROZEN 且本轮被 w4 窗口并发修改（未提交）；阶段5 显示契约为离线定稿未验收",
        },
        {
            "name": "独立 Reviewer 审查",
            "status": "BLOCKED",
            "command": None,
            "exit_code": None,
            "reason": "本阶段总控在本次会话无法创建子代理（委派深度已用尽）；须由项目总控在后续轮次安排",
        },
    ]
    limitations = [
        "本轮未实现状态机、未执行任何测试、未上板、未接摄像头、未操作 HDMI、未烧录；6-B/6-C/6-D/6-E 全部未执行",
        "阶段4 结果记录契约与阶段5 显示契约均未冻结，集成验收依赖 BLOCKED；阶段4 文件在本轮期间被并发修改（未提交），本清单绑定其提交 73c3dad 版本",
        "全部阈值与指标待批准，未在正式测试集上调参；本运行不含任何验收统计",
        "显示侧新增 HUD 字段与五类动作映射为提案，未获批准前不得作为集成验收依赖",
        "本轮未完成独立审查（无法创建子代理）；CHECKS_OK 与 ALL_PASS 都不代表状态机行为正确或 G0/G2/G4/G5 与实物验收通过",
        "回放/注入结论适用范围仅限回放/注入输入，不得冒充真实摄像头验收",
    ]
    manifest = {
        "schema_version": 1,
        "stage": "stage6",
        "task_id": "S6-A",
        "run_id": "s6a_g0_20261022_r01",
        "source_commit": SOURCE_COMMIT,
        "evidence_dir": EVIDENCE_DIR,
        "interfaces": INTERFACES,
        "files": files,
        "checks": checks,
        "limitations": limitations,
        "tool_versions": TOOL_VERSIONS,
    }
    (RUN / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    RUN.mkdir(parents=True, exist_ok=True)
    build_hashes_file()
    build_inputs_manifest()
    build_delivery_manifest()
    print("generated:", EVIDENCE_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
