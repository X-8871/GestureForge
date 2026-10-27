#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-T04 阶段5 **离线范围冻结**证据运行器（只跑离线；不动硬件）。

产出（新 RunId）
================
`report/evidence/S5-T04/s5_freeze_20261027_r01/`：
- `README.md`          —— 冻结文书（范围 / 逐条不主张 / 继承上游局限 / 恢复入口 / 真实退出码）
- `frozen_set.json`    —— 冻结集（由 `build_stage5_frozen_set.py` 现场生成，逐件哈希）
- `frozen_set_report.json` / `selftest_injection.json` —— 校验器输出与注入自测输出
- `results_freeze.json`—— 本轮结果与退出码汇总
- `console/**`         —— 安静窗口、git 状态、校验器/自测/套件/检查器原始输出（含真实退出码）
- `delivery_manifest.json` / `hashes_sha256.txt`

判定：安静窗口 + 工作树无已跟踪改动 + 无 index.lock + 冻结集校验 exit 0 + 注入自测 exit 0
      + 离线套件 exit 0 + `check_stage_delivery --mode evidence`（M1/M2）exit 0 ⇒ 本运行器 exit 0。

只读边界：不写被冻结文件；不连接/加载/烧录任何硬件；不 push；不复用、不改写既有 RunId。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
TASK_ID = "S5-T04"
DEFAULT_RUN_DIR = "report/evidence/S5-T04/s5_freeze_20261027_r06"
STATUS_OK = "CHECKS_OK"

TOOLING_SOURCES = (
    "verification/verify_stage5_frozen_set.py",
    "scripts/stage5_t04/build_stage5_frozen_set.py",
    "scripts/stage5_t04/run_stage5_freeze_evidence.py",
    "scripts/stage5_t04/run_f6_export_selfcheck.py",
)

CONTRACT_SOURCES = (
    "docs/stage5/s5a_stage5_display_g0_fields.json",
    "docs/stage5/s5t03_input_contract_binding_v1.json",
    "docs/stage5/s5t03_offline_skeleton_params_v1.json",
    "docs/stage5/s5t03_json_contract_v1.json",
    "docs/stage5/s5a_g0_ur3_decision_20261025_r01.json",
)

# DSH-20261027-017：`vivado-mcp-server*` 是 MCP 桥接进程，不等于 hw_server/xsdb，不得据此判"板级占用"
HEAVY_PATTERNS = ("vivado.exe", "xsdb", "hw_server", "vitis", "xsim")
EXTERNAL_HW_SESSION_MARKERS = ("hw_server",)  # 外部 Agent 的 JTAG server（如 2B），非本卡硬件操作

BRIDGE_MARKERS = ("vivado-mcp-server",)

KEEP_REASON = {
    "console/quiet_window.txt": "安静窗口核验（无 vivado.exe/xsdb/hw_server/vitis/xsim）",
    "console/git_state.txt": "冻结基线的工作树/分支/HEAD/lock 现场记录",
    "console/verify_frozen_set.txt": "冻结集校验器实跑输出与真实退出码",
    "console/selftest_injection.txt": "必须失败的注入自测（改字节/删件）实跑输出与退出码",
    "console/unittest_all.txt": "离线套件完整原始输出",
    "console/suite_command.txt": "离线套件的精确命令与模块清单",
    "console/check_evidence_mode_output.txt": "check_stage_delivery --mode evidence 的真实退出码",
    "console/legacy_suite_known_gap.txt": "S5-A/B/C 历史模块探测原始输出（已知缺口，非门禁）",
    "console/selftest_injection.txt": "必须失败的注入自测（改字节/删件）实跑输出与退出码",
}

LIMITATIONS = [
    "**离线范围冻结**：本包只冻结**离线**契约/实现/证据字节并证明其可复现，不代表 G0/G1/G3/G4/G5 或任何板级/实物验收。",
    "**不主张真实回放接入**：阶段4 回放结果包（`s4t27_replay_package_freeze_20261027_r01`，`replay_only`）与本树离线消费已存在，"
    "但 **task-27 的板级/实时/实物部分**仍未做（NOT_RUN）；其**离线部分已交付并纳入本冻结**。板上/实时回放不主张。",
    "**不主张板级项**：板上动态映射/绘制、摄像头真实采集、真实集成 30 分钟、T5-10 板上回归、HUD 屏上视觉确认、真彩目视一律 NOT_RUN。",
    "**继承上游局限（引用不改写）**：阶段3 VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核；"
    "阶段4 `complete_stage4_or_RGB_preprocess=NOT_CLAIMED`。",
    "**宿主侧引用**：阶段3 帧/绑定与阶段4 冻结包记录、Wong 批准回执为仓库外只读引用；本包只按哈希引用其字节，不改写、不复制其所有权。",
    "冻结集只覆盖 `frozen_set.json` 列出的成员；冻结文书自身（README/manifest/console）不在被冻结成员内（由 Git 提交与清单绑定）。",
    "**已知缺口（未闭合）**：`scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史离线准备）测试因 w4 侧黄金数据漂移而失败，"
    "不纳入冻结集、不计入本冻结的离线回归主张；原始输出见 `console/legacy_suite_known_gap.txt`。",
    "`CHECKS_OK` 仅表示清单/文件绑定/目录检查通过，不代表接口语义正确、测试充分、独立审查通过或任何关口通过。",
]

TOOL_VERSIONS = {
    "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    "verify_stage5_frozen_set": "verification/verify_stage5_frozen_set.py v1（fail-closed：0 一致 / 1 不一致 / 2 输入或环境错误）",
    "build_stage5_frozen_set": "scripts/stage5_t04/build_stage5_frozen_set.py v1",
    "checker": "check_stage_delivery.py schema_version=1（--mode evidence）",
    "git": "Git Bash（只读调用）",
}


def sha256_file(path: pathlib.Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_command(args: list[str]) -> dict:
    completed = subprocess.run(args, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", cwd=str(REPO_ROOT))
    return {"command": " ".join(args), "exit_code": completed.returncode,
            "stdout": completed.stdout, "stderr": completed.stderr}


def quiet_window_check() -> dict:
    """安静窗口：自有重型工具（Vivado/xsim 等）必须不在跑；外部 `hw_server` 会话与 MCP 桥接只记录。

    r06 修订（S5-T04 复审/再冻结轮）：`hw_server.exe` 属**其他 Agent 的硬件会话**（AGENTS.md：2B 持有、任何窗口不得结束
    或干扰），而本卡是**离线字节冻结**（`ENABLE=0`、未连接/未加载位流/未烧录/未占用 JTAG）。若把外部 JTAG server 的存在
    当作冻结失败条件，会把"别人开着板"误判成"我做了硬件操作"，且无法自行消除（不得杀他人进程）。故分档：
    - `heavy_processes`（vivado.exe/xsdb/vitis/xsim）→ 判 BUSY（fail-closed，因为无法排除本卡占用）；
    - `external_hw_sessions`（hw_server）→ 只记录，并要求与 `vivado.exe` 缺失一起作为"未驱动硬件"的证明。
    """
    listing = subprocess.run(["tasklist"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
    lines = [line.strip() for line in listing.stdout.splitlines() if line.strip()]
    heavy = [line for line in lines if any(p.lower() in line.lower() for p in HEAVY_PATTERNS)]
    external = [line for line in lines if any(m.lower() in line.lower() for m in EXTERNAL_HW_SESSION_MARKERS)]
    bridges = [line for line in lines if any(m.lower() in line.lower() for m in BRIDGE_MARKERS)]
    return {"heavy_processes": heavy, "external_hw_sessions": external, "mcp_bridge_processes": bridges,
            "quiet_ok": not heavy,
            "board_driver_absent": not heavy,
            "note": ("vivado-mcp-server* 桥接按 DSH-20261027-017 只作信息记录；hw_server 属外部 Agent 会话，"
                     "本卡离线冻结不连接/不加载/不烧录，仅记录并在 README 说明")}


def git_state() -> dict:
    def git(*args: str) -> str:
        completed = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True,
                                   text=True, encoding="utf-8", errors="replace")
        return completed.stdout.strip()

    lock_path = git("rev-parse", "--git-path", "index.lock")
    lock_file = pathlib.Path(lock_path)
    if not lock_file.is_absolute():
        lock_file = REPO_ROOT / lock_file
    return {"branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
            "status_short": git("status", "--short"),
            "tracked_status": git("status", "--short", "--untracked-files=no"),
            "lock_path": str(lock_file), "lock_present": lock_file.exists()}


def test_modules() -> list[str]:
    """本冻结的**离线回归主套件**：当前离线 replay/display 路径 + 几何参考测试。

    `scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史准备）不在主套件内：其依赖 w4 侧黄金数据、上游漂移后失败，
    按已知缺口单独探测记录（`legacy_test_modules`），不计入本冻结的回归主张。
    """
    modules: list[str] = []
    for path in sorted((REPO_ROOT / "scripts/stage5_t03").glob("test_*.py")):
        modules.append(f"scripts.stage5_t03.{path.stem}")
    geometry_test = REPO_ROOT / "verification" / "test_s5_display_geometry_reference.py"
    if geometry_test.is_file():
        modules.append("verification.test_s5_display_geometry_reference")
    return modules


def legacy_test_modules() -> list[str]:
    modules: list[str] = []
    for directory, package in (("scripts/stage5_s5b", "scripts.stage5_s5b"),
                               ("scripts/stage5_s5c", "scripts.stage5_s5c")):
        for path in sorted((REPO_ROOT / directory).glob("test_*.py")):
            modules.append(f"{package}.{path.stem}")
    return modules


def parse_unittest_summary(text: str) -> dict:
    """解析 unittest 摘要（`FAILED (failures=19, skipped=2)` / `OK (skipped=2)` 两种格式）。"""
    import re
    summary = {"ran": None, "failures": 0, "errors": 0, "skipped": 0, "ok": None}
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"^Ran (\d+) tests? in ", stripped)
        if match:
            summary["ran"] = int(match.group(1))
            continue
        if stripped.startswith("FAILED"):
            summary["ok"] = False
            for key, value in re.findall(r"(failures|errors|skipped)=(\d+)", stripped):
                summary[key] = int(value)
        elif stripped == "OK" or stripped.startswith("OK ("):
            summary["ok"] = True
            for key, value in re.findall(r"(failures|errors|skipped)=(\d+)", stripped):
                summary[key] = int(value)
    return summary


def manifest_files(run_dir: pathlib.Path) -> list[dict]:
    files: list[dict] = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        if relative.endswith("delivery_manifest.json"):
            continue
        name = relative.split("/")[-1]
        role = "log" if name.endswith((".txt", ".log")) else "artifact"
        if name in ("results_freeze.json", "frozen_set.json", "frozen_set_report.json",
                    "selftest_injection.json"):
            role = "result"
        entry = {"path": relative, "role": role, "sha256": sha256_file(path)}
        reason = KEEP_REASON.get("/".join(relative.split("/")[-2:]))
        if reason:
            entry["keep_reason"] = reason
        files.append(entry)
    for relative in (*TOOLING_SOURCES, *CONTRACT_SOURCES):
        files.append({"path": relative, "role": "source", "sha256": sha256_file(REPO_ROOT / relative)})
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
            "本卡为阶段5 **离线范围冻结**：冻结对象是仓库内字节集 + 宿主侧只读引用，"
            "无 role=input 的本地输入文件（--mode inputs 要求至少一个 role=input）；"
            "上游接口（阶段3/阶段4）本轮均非本卡可冻结对象，故 inputs 模式不适用，不伪造 frozen 字段。"),
        "files": manifest_files(run_dir),
        "checks": checks,
        "limitations": LIMITATIONS,
        "tool_versions": TOOL_VERSIONS,
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


def freeze_document(context: dict) -> str:
    frozen = context["frozen_set_summary"]
    verify = context["verify"]
    selftest = context["selftest"]
    suite = context["suite"]
    return "\n".join([
        "# S5-T04 阶段5 **离线范围冻结**（`OFFLINE_SCOPE_FROZEN`）——冻结文书",
        "",
        f"> 冻结标识：`{frozen.get('frozen_set_id')}`｜RunId：`{context['run_id']}`｜生成：{context['generated_utc8']}",
        f"> 冻结前基线提交（构建冻结集时的 HEAD）：`{frozen.get('baseline_commit')}`；本轮内容提交见 §6。",
        "> 本冻结**只覆盖离线字节集**：不主张 G0/G1/G3/G4/G5，不主张任何板级/实物/实时结论。",
        "> 本卡不需要板卡（Wong 2026-10-27 确认）；本轮未连接、未加载位流、未烧录、未占用 JTAG/串口。",
        "",
        "## 1. 冻结范围（只此四类）",
        "1. **离线契约/规格**：`docs/stage5/**` 中列出的显示契约 JSON、输入绑定 JSON、离线参数/用例骨架、JSON 契约、UR-3 决策（stale=200 ms 批准引用）。",
        "2. **离线实现**：`verification/s5_display_geometry_reference.py`（+几何参考测试）、`scripts/stage5_t03/**`（渲染/回放/长跑/多几何/HUD 遮挡/JSON 契约/阶段4 冻结包消费；含 task-27 的 replay/colour 三件套）、`scripts/stage5_t27/**`（冻结证据运行器/基座定稿/干净检出自证）。**注意**：`scripts/stage5_s5a|s5b|s5c/**` **不在**本冻结集内（见 `not_frozen`，其测试依赖 w4 黄金数据、上游漂移后失败）。",
        "3. **离线证据包**（现场从 `frozen_set.json` 枚举，共 "
        + str(len(context.get("evidence_packages", []))) + " 个，避免文书漏列）："
        + "、".join(f"`{x}`" for x in context.get("evidence_packages", [])) + "。",
        "4. **宿主侧只读引用**（`scope=host`）：阶段3 参考帧 `939fce22…` 与回放绑定、阶段4 回放结果包冻结记录/索引/带框包、"
        "Wong 批准的 `stale=200 ms` 回执、阶段3/阶段4 局限引用文件。",
        "",
        "成员总数与分组计数（现场生成）：",
        f"```json\n{json.dumps(frozen, ensure_ascii=False, indent=2)}\n```",
        "",
        "## 2. 明确不主张（逐条写死）",
        "1. **真实回放接入**（板上/实时）与 **task-27 的板级/实时/实物部分**：不主张（未做）。"
        "**task-27 的离线部分已交付并纳入本冻结**（`impl_dir::scripts/stage5_t27`、`scripts/stage5_t03` 追加 3 文件、"
        "3 个 S5-T27 证据包），离线结论不代表板上/实时结论。",
        "2. **板上动态映射/绘制**：不主张（S5-T02 板级 §4.5/§7.3 未关闭）。",
        "3. **摄像头真实采集**：不主张。",
        "4. **真实集成 30 分钟**：不主张（仅有离线虚拟长跑）。",
        "5. **T5-10 板上回归**：不主张。",
        "6. **HUD 屏上视觉确认**：不主张（仅有离线栅格化遮挡量化）。",
        "7. **任何 G0/G1/G3/G4/G5 通过**：不主张。",
        "8. **真实采集质量/颜色与端到端延迟实测**：不主张（`capture_clock=PENDING_MEASUREMENT`）。",
        "9. **上游关口的替代判定**：不主张；上游自述局限按其原文继承（§3）。",
        "",
        "## 3. 继承的上游局限（引用不改写）",
        f"- 阶段3：VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17`/I-O delay 未签核 "
        f"（引用 `{context['host_refs']['stage3']}`）。",
        f"- 阶段4：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（引用 `{context['host_refs']['stage4']}`）。",
        "- 以上只引用，不重解释、不替代其所有者判定。",
        "",
        "## 4. 冻结集校验器与真实退出码",
        "| 步骤 | 命令 | 退出码 | 结论 |",
        "|---|---|---|---|",
        f"| 冻结集生成 | `python -B scripts/stage5_t04/build_stage5_frozen_set.py --out <冻结包目录>/frozen_set.json`（`--out` 必填） | {context['build']['exit_code']} | "
        f"{frozen.get('members')} 个成员，`frozen_set.json` sha256 `{context['frozen_set_sha256']}` |",
        f"| 冻结集校验 | `python -B verification/verify_stage5_frozen_set.py` | **{verify['exit_code']}** | "
        f"`{verify['status']}`（一致 {verify['totals']['matched']} / 不一致 {verify['totals']['mismatched']} / "
        f"环境错误 {verify['totals']['env_errors']}） |",
        "| 注入自测（必须失败） | `python -B verification/verify_stage5_frozen_set.py --selftest <tmp>` | "
        f"**{selftest['exit_code']}** | `{selftest['verdict']}`："
        + "、".join(
            f"{item['step']}={item['observed_exit']}（期望 {item['expected_exit']}）"
            for item in (selftest.get("checks") or selftest.get("steps") or []))
        + " |",
        f"| 离线套件（回归） | `{' '.join(suite['command'])}` | {suite['exit_code']} | "
        f"Ran {suite['summary']['ran']} / failures {suite['summary']['failures']} / errors {suite['summary']['errors']} / "
        f"skipped {suite['summary']['skipped']} |",
        f"| 历史模块探测（**非门禁**） | `python -B -m unittest {' '.join(context['legacy']['modules'])}` | "
        f"{context['legacy']['exit_code']} | Ran {context['legacy']['summary']['ran']} / failures "
        f"{context['legacy']['summary']['failures']} / errors {context['legacy']['summary']['errors']} —— "
        f"**已知缺口**（w4 侧黄金数据漂移），不计入本冻结回归主张，见 §8 |",
        f"| 安静窗口 | `tasklist` 过滤 `{', '.join(HEAVY_PATTERNS)}` | {context['checks']['quiet']['exit_code']} | "
        f"{'QUIET（桥接进程 ' + str(len(context['quiet']['mcp_bridge_processes'])) + ' 个，已按 DSH-20261027-017 区分）' if context['quiet']['quiet_ok'] else 'BUSY'} |",
        f"| 工作树已跟踪改动 | `git status --short --untracked-files=no` | {context['checks']['clean']['exit_code']} | "
        f"{'CLEAN' if not context['git']['tracked_status'] else 'DIRTY'}；index.lock "
        f"{'PRESENT' if context['git']['lock_present'] else 'ABSENT'} |",
        "",
        "> 包装检查器（`check_stage_delivery --mode evidence`，M1/M2）的真实退出码见 "
        "`console/check_evidence_mode_output.txt` 与 `results_freeze.json`；`CHECKS_OK` 只代表清单/绑定检查通过。",
        "",
        "## 5. 从零复跑（恢复入口）",
        "```bash",
        "git -C D:/codex-worktrees/w5 log --oneline -3; git -C D:/codex-worktrees/w5 status --short",
        f"python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --root D:/codex-worktrees/w5 --frozen-set {context['run_dir_rel']}/frozen_set.json",
        f"python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --frozen-set {context['run_dir_rel']}/frozen_set.json --selftest tmp/5/S5-T04/frozen_selftest",
        "python -B D:/codex-worktrees/w5/scripts/stage5_t04/build_stage5_frozen_set.py --out <out.json>   # 可复现同一冻结集",
        "python -B D:/codex-worktrees/w5/scripts/stage5_t04/run_stage5_freeze_evidence.py --run-dir report/evidence/S5-T04/<新RunId> --source-commit <提交>",
        "python -B D:/codex-worktrees/w5/scripts/stage5_t04/run_f6_export_selfcheck.py --commit <冻结提交> --frozen-run-dir " + context['run_dir_rel'],
        "python -B -m unittest " + " ".join(suite["modules"]),
        f"python -B D:/FPGA_Competition/verification/check_stage_delivery.py --mode evidence --project-root D:/codex-worktrees/w5 --manifest {context['run_dir_rel']}/delivery_manifest.json",
        "```",
        "- 离线回归的可视/数值入口（示例）：`python -B scripts/stage5_t03/s5t03_replay_display.py --out report/evidence/S5-T03/<新RunId> --mode mixed --frames 240 --keyframe-max 24 --stage3-binding <binding> --demo-mp4`。",
        "- 在**离开本机**的副本中，`scope=host` 引用可用 `--skip-host-references` 跳过（跳过项会逐条打印，不得当作已验证）。",
        "",
        "## 6. 提交与 F6 自证",
        f"- 冻结前基线（`frozen_set.json.baseline_commit`）：`{frozen.get('baseline_commit')}`。",
        f"- 本轮内容提交与最终 HEAD：见外部报告（本文件不写自身提交哈希，避免自指）；`git log -1` 为权威。",
        "- **F6 自证**：本轮内容提交单独 `git archive` 导出（或 `git clone --shared --no-checkout` 部分检出）后，"
        "在**副本内**复跑冻结集校验器；`check_stage_delivery --mode evidence` 在**主工作树**上运行"
        "（其清单绑定按提交 blob 复算，副本与主树的 `files[]` 字节一致；副本内跑需自带完整依赖，故不作为权威口径，见 F2 更正），"
        "原始输出与真实退出码见 `" + context["f6_run_dir_rel"] + "/`（C1 提交前 handoff 为**信息项，非门禁**；提交后 handoff 见 `" + context["f6_handoff_run_dir_rel"] + "/`）。",
        "",
        "### 6.1 失败/被取代 RunId 的 `run_id` 残留（F4 标注，不重写失败证据）",
        "- `report/evidence/S5-T04/s5_freeze_f6export_20261027_r00_crlf_fail/` 与 `…_r00b_tracked_dirs_fail/` 内部 "
        "`results_f6export.json.run_id` 仍写着 `…_r01`（修复前驱动硬编码，属历史残留）。",
        "- 处置：**不重写失败证据**；在此标注其真实归属为 `r00_crlf_fail` / `r00b_tracked_dirs_fail`，"
        "r06 起驱动强制 `--frozen-run-dir` 显式传参（`run_id` 由目录名派生）。",
        "",
        "### 6.2 哈希基座（2026-10-27 项目级新规）",
        "- 本包 `delivery_manifest.json` **内联** `hash_basis=\"commit_blob\"` + `hash_basis_commit=<40 位真实 SHA>`，"
        "`files[]` 逐项声明基座；权威运行方式为显式 `--commit <hash_basis_commit>`（默认 HEAD 仅在该提交后字节未变时等价）。",
        "- 本地附注 tag：`stage5-offline-freeze-20261027`（**不 push**）。",
        "",
        "## 7. 限制",
        *[f"- {item}" for item in LIMITATIONS],
        "",
        "## 8. 未闭合项与未做项（NOT_RUN，如实）",
        f"1. **历史模块已知缺口**：`scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史离线准备）探测 "
        f"{context['legacy']['exit_code']}，Ran {context['legacy']['summary']['ran']} / failures "
        f"{context['legacy']['summary']['failures']} / errors {context['legacy']['summary']['errors']}；"
        "根因＝其测试依赖 w4 侧黄金数据（`s4c_replay_20261021_r05`、`S4-B/20261021_r13`）上游漂移，"
        "**不属于本卡定义的离线 replay/display 路径**；原始输出见 `console/legacy_suite_known_gap.txt`。"
        "本冻结**不冒称**这些历史模块回归通过；其历史结论仍按各自 RunId 自证。",
        "2. **`task-27` 的板级/实时/实物部分未做（NOT_RUN）**：其**离线部分已交付并纳入本冻结**；"
        "阶段4 回放结果包已冻结（`replay_only`）且本树有离线消费证据；板级/实时/实物部分未做、不主张。",
        "3. **板级 B1–B10 全项**：已随 Wong 拔板暂停；重连后需先过第 0 步（占用/部署身份/运行期回读地址/真彩目视需 Wong 在场）。",
        "4. **端到端真实链窗口**（`end2end_real_chain_window_plan_20261027_r01`）中的 P1=task-27、W-E=B1–B10 均未开工（等待信号）。",
        "5. **阶段5 G0/G1/G3/G4/G5 与实物验收仍未通过**。",
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--tmp-out", default="")
    parser.add_argument("--allow-existing", action="store_true")
    parser.add_argument("--f6-run-dir", default="report/evidence/S5-T04/s5_freeze_f6export_20261027_r03",
                        help="本轮 F6 自证包目录（写入 README §6，避免指错轮次）")
    parser.add_argument("--f6-handoff-run-dir",
                        default="report/evidence/S5-T04/s5_freeze_f6export_20261027_r02_postcommit_handoff")
    args = parser.parse_args(argv)

    run_dir = REPO_ROOT / args.run_dir
    if run_dir.exists() and any(run_dir.iterdir()) and not args.allow_existing:
        print(f"[ENV_ERROR] RunId 目录已存在且非空，按纪律不覆盖重跑：{run_dir}", file=sys.stderr)
        return 2
    (run_dir / "console").mkdir(parents=True, exist_ok=True)
    scratch = REPO_ROOT / "tmp" / "5" / TASK_ID
    scratch.mkdir(parents=True, exist_ok=True)

    generated = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + "+08:00"
    quiet = quiet_window_check()
    git = git_state()
    source_commit = args.source_commit or git["head"]

    (run_dir / "console" / "quiet_window.txt").write_text("\n".join([
        "# 安静窗口核验（S5-T04 冻结；未进行任何硬件操作）",
        f"heavy_patterns={list(HEAVY_PATTERNS)}",
        f"heavy_processes={quiet['heavy_processes'] or '(none)'}",
        f"external_hw_sessions={quiet.get('external_hw_sessions') or '(none)'}",
        f"board_driver_absent={quiet.get('board_driver_absent')}",
        f"mcp_bridge_processes={quiet['mcp_bridge_processes'] or '(none)'}",
        f"verdict={'QUIET' if quiet['quiet_ok'] else 'BUSY'}",
        f"note={quiet['note']}", ""]), encoding="utf-8")
    (run_dir / "console" / "git_state.txt").write_text("\n".join([
        f"branch={git['branch']}", f"head={git['head']}", f"source_commit={source_commit}",
        f"lock_path={git['lock_path']}", f"lock_present={git['lock_present']}",
        "--- git status --short ---", git["status_short"], "",
        "--- git status --short --untracked-files=no ---", git["tracked_status"], ""]), encoding="utf-8")

    # ── 1. 生成冻结集 ────────────────────────────────────────────────────
    build = run_command([sys.executable, "-B", str(HERE / "build_stage5_frozen_set.py"),
                         "--out", str((run_dir / "frozen_set.json").relative_to(REPO_ROOT).as_posix())])
    (run_dir / "console" / "build_frozen_set.txt").write_text("\n".join([
        f"command={build['command']}", f"exit_code={build['exit_code']}",
        "--- stdout ---", build["stdout"].rstrip(), "--- stderr ---", build["stderr"].rstrip(), ""]),
        encoding="utf-8")
    build_ok = build["exit_code"] == 0
    frozen_set_path = run_dir / "frozen_set.json"
    if not build_ok or not frozen_set_path.is_file():
        print(f"[ENV_ERROR] 冻结集生成失败：exit={build['exit_code']}", file=sys.stderr)
        return 2
    frozen_set = json.loads(frozen_set_path.read_text(encoding="utf-8"))
    groups: dict[str, int] = {}
    for member in frozen_set["members"]:
        groups[member["group"]] = groups.get(member["group"], 0) + 1
    frozen_summary = {"frozen_set_id": frozen_set["frozen_set_id"],
                      "baseline_commit": frozen_set["baseline_commit"],
                      "generated_utc8": frozen_set["generated_utc8"],
                      "members": len(frozen_set["members"]), "by_group": groups}

    # ── 2. 校验 + 注入自测 ───────────────────────────────────────────────
    verify_run = run_command([sys.executable, "-B", str(REPO_ROOT / "verification" / "verify_stage5_frozen_set.py"),
                              "--root", str(REPO_ROOT), "--frozen-set", str(frozen_set_path),
                              "--json-out", str(run_dir / "frozen_set_report.json")])
    (run_dir / "console" / "verify_frozen_set.txt").write_text("\n".join([
        f"command={verify_run['command']}", f"exit_code={verify_run['exit_code']}",
        "--- stdout ---", verify_run["stdout"].rstrip(), "--- stderr ---", verify_run["stderr"].rstrip(), ""]),
        encoding="utf-8")
    report_path = run_dir / "frozen_set_report.json"
    verify = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {
        "status": "NO_REPORT", "exit_code": verify_run["exit_code"],
        "totals": {"matched": 0, "mismatched": 0, "env_errors": -1}}

    selftest_run = run_command([sys.executable, "-B", str(REPO_ROOT / "verification" / "verify_stage5_frozen_set.py"),
                                "--frozen-set", str(frozen_set_path),
                                "--selftest", str(scratch / "frozen_selftest"),
                                "--json-out", str(run_dir / "selftest_injection.json")])
    (run_dir / "console" / "selftest_injection.txt").write_text("\n".join([
        f"command={selftest_run['command']}", f"exit_code={selftest_run['exit_code']}",
        "--- stdout ---", selftest_run["stdout"].rstrip(), "--- stderr ---", selftest_run["stderr"].rstrip(), ""]),
        encoding="utf-8")
    selftest_path = run_dir / "selftest_injection.json"
    selftest = (json.loads(selftest_path.read_text(encoding="utf-8")) if selftest_path.is_file()
                else {"verdict": "NO_SELFTEST_REPORT", "exit_code": selftest_run["exit_code"],
                      "steps": {"clean": {"exit_code": None}, "tampered_one_byte": {"exit_code": None},
                                "deleted_one_member": {"exit_code": None}}})
    if "steps" not in selftest:                                  # 自测自身环境错误：补齐结构，仍如实记录
        selftest = {"verdict": "SELFTEST_ENV_ERROR", "exit_code": selftest_run["exit_code"],
                    "steps": {"clean": {"exit_code": None}, "tampered_one_byte": {"exit_code": None},
                              "deleted_one_member": {"exit_code": None}}}

    # ── 3. 离线套件（回归）───────────────────────────────────────────────
    modules = test_modules()
    suite_command = [sys.executable, "-B", "-m", "unittest", *modules]
    (run_dir / "console" / "suite_command.txt").write_text("\n".join([
        "# 离线套件的精确命令与模块清单（模块按目录 glob test_*.py 现场生成）",
        " ".join(suite_command), "", *[f"- {m}" for m in modules], ""]), encoding="utf-8")
    suite_run = run_command(suite_command)
    (run_dir / "console" / "unittest_all.txt").write_text(
        "\n".join([f"command={' '.join(suite_command)}", f"exit_code={suite_run['exit_code']}",
                   "--- stdout ---", suite_run["stdout"].rstrip(),
                   "--- stderr ---", suite_run["stderr"].rstrip(), ""]), encoding="utf-8")
    suite_summary = parse_unittest_summary(suite_run["stdout"] + "\n" + suite_run["stderr"])

    # ── 3b. 历史模块探测（**非门禁**：如实记录已知缺口，不计入冻结回归主张）──
    legacy_modules = legacy_test_modules()
    legacy_run = (run_command([sys.executable, "-B", "-m", "unittest", *legacy_modules])
                  if legacy_modules else {"command": "(none)", "exit_code": None, "stdout": "", "stderr": ""})
    legacy_summary = parse_unittest_summary(legacy_run["stdout"] + "\n" + legacy_run["stderr"])
    (run_dir / "console" / "legacy_suite_known_gap.txt").write_text("\n".join([
        "# S5-A/B/C 历史离线准备模块（scripts/stage5_s5a|s5b|s5c）——**已知缺口**，非本冻结回归门禁",
        "# 原因：其测试依赖 w4 侧黄金数据（s4c_replay_20261021_r05、S4-B/20261021_r13），上游漂移后失败；",
        "# 它们不属于本卡定义的离线 replay/display 路径，其历史结论按各自 RunId 自证。",
        f"command={' '.join(legacy_run['command'].split()) if isinstance(legacy_run['command'], str) else legacy_run['command']}",
        f"exit_code={legacy_run['exit_code']}",
        f"summary={json.dumps(legacy_summary, ensure_ascii=False)}",
        "--- stdout tail ---", "\n".join(legacy_run["stdout"].rstrip().splitlines()[-4:]),
        "--- stderr tail ---", "\n".join(legacy_run["stderr"].rstrip().splitlines()[-4:]), ""]),
        encoding="utf-8")

    # ── 4. 冻结文书 + 结果 ───────────────────────────────────────────────
    # M1-②：从 frozen_set 实际成员枚举证据包（避免文书漏列/多列），供 README §1.3 使用
    evidence_packages: list[str] = []
    for member in json.loads(frozen_set_path.read_text(encoding="utf-8")).get("members", []):
        if member.get("group") not in ("offline_evidence_replay_display", "offline_evidence_s5t02"):
            continue
        parts = member["path"].split("/")
        if len(parts) >= 4:
            package = "/".join(parts[:4])
            if package not in evidence_packages:
                evidence_packages.append(package)

    context = {
        "run_id": run_dir.name, "run_dir_rel": args.run_dir,
        "evidence_packages": sorted(evidence_packages),
        "generated_utc8": generated,
        "f6_run_dir_rel": args.f6_run_dir,
        "f6_handoff_run_dir_rel": args.f6_handoff_run_dir,
        "frozen_set_summary": frozen_summary, "frozen_set_sha256": sha256_file(frozen_set_path),
        "build": build, "verify": verify, "selftest": selftest,
        "suite": {"command": suite_command, "modules": modules,
                  "exit_code": suite_run["exit_code"], "summary": suite_summary},
        "legacy": {"modules": legacy_modules, "exit_code": legacy_run["exit_code"],
                   "summary": legacy_summary},
        "quiet": quiet, "git": git,
        "host_refs": {
            "stage3": "D:/codex-worktrees/dbdf/report/evidence/S3-T17/stage3_closeout_20261026_r01/manifest.json",
            "stage4": "D:/codex-worktrees/w4/docs/stage4/s4_stage4_freeze_supplement_hardware_20261027_r01.md",
        },
        "checks": {"quiet": {"exit_code": 0 if quiet["quiet_ok"] else 1},
                   "clean": {"exit_code": 0 if not git["tracked_status"] and not git["lock_present"] else 1}},
    }
    (run_dir / "README.md").write_text(freeze_document(context), encoding="utf-8")

    results = {
        "task_id": TASK_ID, "run_id": run_dir.name, "freeze_kind": "OFFLINE_SCOPE_FROZEN",
        "generated_utc8": generated, "source_commit": source_commit,
        "baseline_commit_at_build": frozen_set["baseline_commit"],
        "frozen_set": frozen_summary, "frozen_set_sha256": sha256_file(frozen_set_path),
        "verify": {"status": verify.get("status"), "exit_code": verify_run["exit_code"],
                   "totals": verify.get("totals"), "mismatches": verify.get("mismatches", []),
                   "errors": verify.get("errors", [])},
        "selftest": {"verdict": selftest.get("verdict"), "exit_code": selftest_run["exit_code"],
                     "steps": {k: v.get("exit_code") for k, v in selftest.get("steps", {}).items()},
                     "checks": selftest.get("checks", [])},
        "offline_suite": {"modules": modules, "exit_code": suite_run["exit_code"],
                          "summary": suite_summary},
        "legacy_suite_known_gap": {"modules": legacy_modules, "exit_code": legacy_run["exit_code"],
                                   "summary": legacy_summary,
                                   "note": "S5-A/B/C 历史准备模块，依赖 w4 侧黄金数据、上游漂移后失败；"
                                           "**不计入**本冻结的离线回归主张，如实登记为未闭合项"},
        "quiet_window": {"heavy_processes": quiet["heavy_processes"],
                         "external_hw_sessions": quiet.get("external_hw_sessions", []),
                         "board_driver_absent": quiet.get("board_driver_absent"),
                         "mcp_bridge_processes": quiet["mcp_bridge_processes"],
                         "verdict": "QUIET" if quiet["quiet_ok"] else "BUSY"},
        "worktree": {"branch": git["branch"], "head": git["head"],
                     "tracked_dirty": bool(git["tracked_status"]), "index_lock": git["lock_present"]},
        "not_run": ["task-27 的板级/实时/实物部分（离线部分已交付并纳入本冻结）",
                    "板级 B1–B10（需重连 + Wong 开工信号）",
                    "端到端真实链窗口 P1/W-E",
                    "G0/G1/G3/G4/G5 与实物验收"],
        "checks": [],
        "limitations": LIMITATIONS,
        "tool_versions": TOOL_VERSIONS,
    }
    write_hashes(run_dir)

    checks = [
        {"name": "冻结集生成（逐件哈希）",
         "status": "PASS" if build_ok else "FAIL", "command": build["command"],
         "exit_code": build["exit_code"],
         "reason": f"{frozen_summary['members']} 个成员；分组 {json.dumps(groups, ensure_ascii=False)}"},
        {"name": "冻结集校验（只读、fail-closed）",
         "status": "PASS" if verify_run["exit_code"] == 0 else "FAIL",
         "command": verify_run["command"], "exit_code": verify_run["exit_code"],
         "reason": f"{verify.get('status')}；一致 {verify.get('totals', {}).get('matched')}、"
                   f"不一致 {verify.get('totals', {}).get('mismatched')}、"
                   f"环境错误 {verify.get('totals', {}).get('env_errors')}"},
        {"name": "注入自测（改一字节必须非 0、删一件必须 exit 2）",
         "status": "PASS" if selftest_run["exit_code"] == 0 else "FAIL",
         "command": selftest_run["command"], "exit_code": selftest_run["exit_code"],
         "reason": f"{selftest.get('verdict')}；"
                   f"clean={selftest.get('steps', {}).get('clean', {}).get('exit_code')}、"
                   f"tamper={selftest.get('steps', {}).get('tampered_one_byte', {}).get('exit_code')}、"
                   f"missing={selftest.get('steps', {}).get('deleted_one_member', {}).get('exit_code')}"},
        {"name": "离线套件（回归）",
         "status": "PASS" if suite_run["exit_code"] == 0 else "FAIL",
         "command": " ".join(suite_command), "exit_code": suite_run["exit_code"],
         "reason": f"Ran {suite_summary['ran']} / failures {suite_summary['failures']} / "
                   f"errors {suite_summary['errors']} / skipped {suite_summary['skipped']}"},
        {"name": "历史模块探测（S5-A/B/C，非门禁：已知缺口如实记录）",
         "status": "FAIL" if legacy_summary["failures"] else "PASS",
         "command": f"python -B -m unittest {' '.join(legacy_modules)}" if legacy_modules else "(none)",
         "exit_code": legacy_run["exit_code"],
         "reason": f"Ran {legacy_summary['ran']} / failures {legacy_summary['failures']} / "
                   f"errors {legacy_summary['errors']} / skipped {legacy_summary['skipped']}；"
                   "根因＝其测试依赖 w4 侧黄金数据（s4c_replay_20261021_r05 / S4-B/20261021_r13）漂移；"
                   "**不计入**本冻结的离线回归主张，作为未闭合项登记"},
        {"name": "安静窗口（无 vivado.exe/xsdb/hw_server/vitis/xsim）",
         "status": "PASS" if quiet["quiet_ok"] else "FAIL",
         "command": f"tasklist 过滤 {'|'.join(HEAVY_PATTERNS)}",
         "exit_code": 0 if quiet["quiet_ok"] else 1,
         "reason": f"heavy={quiet['heavy_processes'] or '(none)'}；"
                   f"桥接进程 {len(quiet['mcp_bridge_processes'])} 个按 DSH-20261027-017 只作信息记录"},
        {"name": "工作树基线（无已跟踪改动、无 index.lock）",
         "status": "PASS" if not git["tracked_status"] and not git["lock_present"] else "FAIL",
         "command": "git status --short --untracked-files=no; git rev-parse --git-path index.lock",
         "exit_code": 0 if not git["tracked_status"] and not git["lock_present"] else 1,
         "reason": f"tracked_dirty={bool(git['tracked_status'])} lock={git['lock_present']}"},
        {"name": "check_stage_delivery --mode inputs",
         "status": "NOT_APPLICABLE",
         "command": f"python -B {CHECKER} --mode inputs --project-root <w5> --manifest <本清单>",
         "exit_code": None,
         "reason": "本卡无 role=input 本地输入（冻结对象为仓库内字节集 + 宿主侧只读引用），不伪造冻结字段"},
    ]

    # ── 5. 清单 M1 + 检查器 ──────────────────────────────────────────────
    manifest = build_manifest(args.run_dir, source_commit, checks)
    check_m1 = run_checker(manifest)
    (run_dir / "console" / "check_evidence_mode_output.txt").write_text("\n".join([
        f"command={check_m1['command']}", f"exit_code={check_m1['exit_code']}",
        "--- stdout ---", check_m1["stdout"].rstrip(), "--- stderr ---", check_m1["stderr"].rstrip(), ""]),
        encoding="utf-8")
    checks.append({
        "name": "check_stage_delivery --mode evidence",
        "status": "PASS" if (check_m1["exit_code"] == 0 and STATUS_OK in check_m1["stdout"]) else "FAIL",
        "command": check_m1["command"], "exit_code": check_m1["exit_code"],
        "reason": "对前置清单 M1 运行（M2 相对 M1 只新增本 check 条目与 console/check_evidence_mode_output.txt）；"
                  "CHECKS_OK 仅代表包装检查通过，不代表语义/审查/关口通过",
    })
    results["checks"] = checks
    results["checker_m1_exit"] = check_m1["exit_code"]
    (run_dir / "results_freeze.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_hashes(run_dir)
    manifest = build_manifest(args.run_dir, source_commit, checks)
    check_m2 = run_checker(manifest)
    results["checker_m2_exit"] = check_m2["exit_code"]
    if args.tmp_out:
        pathlib.Path(args.tmp_out).write_text("\n".join([
            f"exit_code={check_m2['exit_code']}", "--- stdout ---", check_m2["stdout"].rstrip(),
            "--- stderr ---", check_m2["stderr"].rstrip(), ""]), encoding="utf-8")

    final_ok = (build_ok and verify_run["exit_code"] == 0 and selftest_run["exit_code"] == 0
                and suite_run["exit_code"] == 0 and quiet["quiet_ok"] and not git["tracked_status"]
                and not git["lock_present"] and check_m1["exit_code"] == 0 and check_m2["exit_code"] == 0)
    print(f"build={build['exit_code']} verify={verify_run['exit_code']}({verify.get('status')}) "
          f"selftest={selftest_run['exit_code']}({selftest.get('verdict')}) suite={suite_run['exit_code']}"
          f"(ran={suite_summary['ran']}) quiet={'OK' if quiet['quiet_ok'] else 'BUSY'} "
          f"clean={not git['tracked_status']} lock={git['lock_present']} "
          f"checker_M1={check_m1['exit_code']} checker_M2={check_m2['exit_code']}")
    print(f"run_dir={args.run_dir}")
    print(f"final_exit={0 if final_ok else 1}")
    if not final_ok:
        write_hashes(run_dir)
        build_manifest(args.run_dir, source_commit, checks)
    return 0 if final_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())