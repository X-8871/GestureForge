#!/usr/bin/env python3
"""为 task-21 仅生成缺失的通用交付清单（check_stage_delivery schema）。

生成器在运行时枚举 RunId 目录内的全部文件并逐项绑定 SHA-256（保证“运行目录文件全部列入”），
再按显式声明补充目录外的源码/文档/接口绑定。

落点遵循 `report/evidence/<task_id>/<run_id>/`（单层）：task_id = `S4-CTRL`，run_id = `t21_*`。
接口与文件绑定一律使用工作树内路径，避免越出 project-root。

已存在的清单视为不可变证据：重复运行只核验/跳过，不覆盖；两个 r02 历史清单还绑定
固定 SHA-256，缺失或漂移时失败关闭。新证据必须使用新 RunId。

用法：python -B scripts/stage4_s4ctrl/build_t21_manifests.py
退出码：0 = 缺失清单已生成且既有清单保留；1 = 有 RunId 目录缺失；2 = 历史证据缺失或漂移。
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
TASK_ID = "S4-CTRL"
SOURCE_COMMIT = "f6fa9f0d84274f1a0d03e6f87263fb550ebc6656"
EVIDENCE_ROOT = f"report/evidence/{TASK_ID}"

CONTRACT_JSON = "docs/stage4/s4b_shared_input_result_contract.json"
CONTRACT_MD = "docs/stage4/S4B_shared_input_result_contract.md"
APPROVAL_JSON = "docs/stage4/s4a_stale_age_limit_approval_applied_20261024_r01.json"
CONTRACT_CHECKER = "scripts/stage4_s4ctrl/verify_shared_io_contract.py"
REGISTRY_JSON = "docs/stage4/S4B_raw_system_g0_gap_registry.json"
GAP_CHECKER = "scripts/stage4_s4b/audit_raw_system_g0_gaps.py"
READINESS_MD = "docs/stage4/S4B_pl_preprocess_g0_readiness.md"
P_PLAN_MD = "docs/stage4/S4B_frame_period_P_measurement_plan.md"
P_TEMPLATE = "docs/stage4/s4b_frame_period_p_evidence_template.json"
P_CHECKER = "scripts/stage4_s4b/validate_frame_period_p_evidence.py"
TAKEOVER_SCRIPT = "scripts/stage4_s4ctrl/audit_w4_takeover.py"
S4A_JSON = "docs/stage4/s4a_stage4_g0_fields.json"
ADDRESS_MAP = "docs/stage4/S4B_stage4_address_map.json"
CDX_010 = "D:\\FPGA_Competition\\report\\evidence\\CTRL-DSH-HANDOFF\\codex_mailbox\\CDX-20261022-010-stage4-inference-runbook.md"
HISTORICAL_MANIFEST_SHA256 = {
    "t21_takeover_20261024_r02": "887f280089521dd42e2126f31d57b7e09fb175eb437fec62f7fbd24b44e49c71",
    "t21_contract_colour_rebind_20261024_r02": "5f4687c96c0ce9c37adeeb9426858a230a5c7097309849a58f1a9b92c4a06820",
}


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_version() -> str:
    """记录 git 版本（只读）。"""
    try:
        proc = subprocess.run(["git", "--version"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        return proc.stdout.strip() or "unknown"
    except OSError:
        return "unavailable"


def role_for(name: str) -> str:
    """按文件名推断 schema 允许的 role。"""
    if name == "handoff_record.json":
        return "input"
    if name.endswith(".json"):
        return "result"
    if name.endswith(".txt"):
        return "log"
    if name.endswith((".py", ".c", ".h")):
        return "source"
    return "artifact"


def entry(path_text: str, role: str, note: str) -> dict[str, object]:
    """构造 files 条目。"""
    path = Path(path_text)
    resolved = path if path.is_absolute() else WORKTREE / path_text
    return {"path": path_text, "sha256": sha256_of(resolved), "role": role, "keep_reason": note}


def interface(name: str, version: str, frozen: bool, path_text: str) -> dict[str, object]:
    """构造 interfaces 条目。"""
    path = Path(path_text)
    resolved = path if path.is_absolute() else WORKTREE / path_text
    return {"name": name, "version": version, "frozen": frozen, "path": path_text,
            "sha256": sha256_of(resolved)}


def check(name: str, status: str, command: str | None, exit_code: int | None, reason: str) -> dict[str, object]:
    """构造 checks 条目。"""
    return {"name": name, "status": status, "command": command, "exit_code": exit_code, "reason": reason}


def run_dir(run_id: str) -> str:
    """运行目录的仓库相对路径。"""
    return f"{EVIDENCE_ROOT}/{run_id}"


SPECS = [
    {
        "run_id": "t21_takeover_20261024_r02",
        "interfaces": [
            interface("阶段4 共享输入/结果契约（写权交接与输入改绑的接口权威）", "s4-shared-io/1.1.0 r04", False, CONTRACT_JSON),
            interface("阶段4 地址图（接管时准入与所有权口径）", "r02（DRAFT_PENDING_REVIEW）", False, ADDRESS_MAP),
        ],
        "extra_files": [
            entry(f"{run_dir('t21_takeover_20261024_r02')}/handoff_record.json", "input", "本阶段总控接续的 11 字段交接记录（接管依据）"),
            entry(TAKEOVER_SCRIPT, "source", "接管只读核对脚本（可复跑入口）"),
            entry(CONTRACT_JSON, "source", "接管时生效的共享契约版本绑定"),
        ],
        "checks": [
            check("接管只读核对（分支/HEAD/index.lock/重型进程/12 项未跟踪归属与 SHA）", "PASS",
                  f"python -B scripts/stage4_s4ctrl/audit_w4_takeover.py --evidence-dir {run_dir('t21_takeover_20261024_r02')} --expected-untracked 12 --own-artifact scripts/stage4_s4ctrl/audit_w4_takeover.py --own-artifact report/evidence/S4-CTRL/t21_",
                  0, "分支 stage4-infer-prep、HEAD f6fa9f0、无 index.lock、无重型引擎进程（6 个为 MCP server 进程）、12 项未跟踪全部按 Codex 口径归类且留原位"),
            check("接管契约核验（handoff_check --claim，含越界核验与让出契约）", "PASS",
                  f"python -B D:/FPGA_Competition/verification/handoff_check.py --worktree D:/codex-worktrees/w4 --record {run_dir('t21_takeover_20261024_r02')}/handoff_record.json --claim --claimed-path docs/stage4/ --claimed-path scripts/stage4_s4ctrl/ --claimed-path scripts/stage4_s4b/ --claimed-path verification/ --claimed-path report/evidence/S4-CTRL/ --claimed-path .codex/STATE.md",
                  0, "HANDOFF_OK（PASS 9 / FAIL 0 / SKIP 0）"),
            check("对 DSH 原认领记录在新 HEAD 上的复跑（结构性漂移登记）", "FAIL",
                  "python -B D:/FPGA_Competition/verification/handoff_check.py --worktree D:/codex-worktrees/w4 --record report/evidence/CTRL-DSH-HANDOFF/dsh_claim_20261024_r01/handoff_record.json --json",
                  1, "检查项 a：原认领记录写于其自身提交之前（声明 d13610d，实际 HEAD f6fa9f0），其余 8 项 PASS；据实保留，不冒充通过"),
            check("硬件操作", "NOT_RUN", None, None, "依 CDX-20261023-019 全离线；未装载位流、未打开 COM4/JTAG、未起 hw_server"),
        ],
        "limitations": [
            "source_commit 为任务起始 HEAD（f6fa9f0）；本轮改动在运行时尚未提交，提交后以 Git 提交身份为准。",
            "首轮尝试 t21_takeover_20261024_r01 因脚本把本任务自身新建文件计入而报 14 项，失败输出原样保留、未覆盖。",
            "只证明接管时的可核验事实，不代表 G0/G4/G5、测试通过或实物验收。",
        ],
    },
    {
        "run_id": "t21_contract_colour_rebind_20261024_r02",
        "interfaces": [
            interface("阶段4↔阶段5 共享输入/结果契约（真实彩色改绑 + 已批准 stale 常量）", "s4-shared-io/1.1.0 r04", False, CONTRACT_JSON),
            interface("S4-A 阶段4 G0 契约（结果字段/时间口径权威，本轮未改写其字节）", "r06", True, S4A_JSON),
        ],
        "extra_files": [
            entry(CONTRACT_JSON, "source", "契约机器可读权威（r04，本轮改绑主交付）"),
            entry(CONTRACT_MD, "source", "契约人读镜像（r04）"),
            entry(APPROVAL_JSON, "source", "已批准项应用记录（200ms + 批准依据 + 取代关系）"),
            entry(CONTRACT_CHECKER, "source", "契约自检 r05（批准态 + 彩色改绑 + 负向对照）"),
            entry(f"{run_dir('t21_contract_colour_rebind_20261024_r01')}/baseline_selfcheck_stdout.txt",
                  "input", "改绑前基线自检 stdout（22 PASS / 1 FAIL，exit 1）"),
        ],
        "checks": [
            check("契约自检 r05（12/12 绑定复算、已批准 stale 与彩色改绑共 8/8 负向对照）", "PASS",
                  f"python -B scripts/stage4_s4ctrl/verify_shared_io_contract.py --evidence-dir {run_dir('t21_contract_colour_rebind_20261024_r02')}",
                  0, "25 项通过、0 项失败；upstream_bindings 12/12 一致；cdx_015 r02→r03 取代关系已登记"),
            check("改绑前基线自检（漂移真实性）", "FAIL",
                  "python -B scripts/stage4_s4ctrl/verify_shared_io_contract.py", 1,
                  "22 项通过、1 项失败：cdx_015 已升 r03（be7b6520…），r03 契约仍绑 r02 旧哈希 a3ce50d2…；证明本次改绑真实必要"),
            check("契约消费方回归（地址图/词表/离线驱动集成）", "PASS",
                  "python -B -m unittest verification.test_s4_inject_frame -v", 0, "Ran 10 tests，OK"),
            check("契约独立复审", "NOT_RUN", None, None,
                  "本轮无独立 Reviewer（阶段4 总控受委派深度限制）；r04 改绑仍待独立复审，自检 PASS 不等于已审查"),
            check("硬件操作", "NOT_RUN", None, None, "依 CDX-20261023-019 全离线；真实彩色采集/回放均未执行"),
        ],
        "limitations": [
            "source_commit 为任务起始 HEAD（f6fa9f0）；本轮改动运行时尚未提交。",
            "契约 r04 未经独立复审；PASS 只表示绑定与结构自洽，不代表接口语义已审或任何实物验收。",
            "阶段3 无补偿部署的 bit/XSA/ELF 身份来自阶段3 已提交证据（dbdf 只读引用），本轮未在硬件上核对现场。",
        ],
    },
    {
        "run_id": "t21_raw_g0_gap_registry_20261024_r03",
        "interfaces": [
            interface("RAW 系统 G0 缺口登记表（RAW→PL 预处理→HP0 串行 owner→冻结网络→PS 结果）",
                      "gestureforge_s4b_raw_system_g0_gap_registry_v1", False, REGISTRY_JSON),
            interface("阶段4 地址图（区域/空洞/准入禁区与缓存维护方向）", "r02（DRAFT_PENDING_REVIEW）", False, ADDRESS_MAP),
        ],
        "extra_files": [
            entry(REGISTRY_JSON, "source", "缺口登记表（G-01..G-19 + 不适用项）"),
            entry(GAP_CHECKER, "source", "离线算术复算与状态纪律检查器"),
            entry(READINESS_MD, "source", "被登记表绑定的 readiness 文档（末尾追加 r04 指针）"),
        ],
        "checks": [
            check("缺口登记表离线复算（算术 + 依据件哈希 + 状态纪律）", "PASS",
                  f"python -B scripts/stage4_s4b/audit_raw_system_g0_gaps.py --evidence-dir {run_dir('t21_raw_g0_gap_registry_20261024_r03')}",
                  0, "离线算术 9/9 一致、依据件 8/8 复算一致、状态纪律通过"),
            check("首轮与次轮尝试（脚本缺陷修正轨迹）", "FAIL",
                  f"python -B scripts/stage4_s4b/audit_raw_system_g0_gaps.py --evidence-dir {run_dir('t21_raw_g0_gap_registry_20261024_r01')}",
                  1, "r01 因地址图 gaps 仅有十六进制字段而 KeyError（输出保留）；r02 通过后被 r03 取代（readiness 文档更新）"),
            check("系统 G0 闭合判定", "NOT_RUN", None, None,
                  "系统 G0 仍为 CHANGES_REQUIRED_NOT_CLOSED；地址/所有权/平台/数值/资源缺口需批准、实现、独立审查与硬件窗口"),
            check("硬件操作", "NOT_RUN", None, None, "依 CDX-20261023-019 全离线；未访问板卡、未起 hw_server"),
        ],
        "limitations": [
            "source_commit 为任务起始 HEAD（f6fa9f0）；本轮改动运行时尚未提交。",
            "本轮只关闭可离线判定的容量/算术与状态纪律，不关闭任何需要设计、批准、独立审查或硬件的缺口。",
            "登记表不替代独立 G0 审查，也不改变 d4f30e3 的历史检查点记录。",
        ],
    },
    {
        "run_id": "t21_frame_period_p_plan_20261024_r01",
        "interfaces": [
            interface("帧周期 P 实测方案（供阶段6 T6-A03；数值 NOT_RUN）", "r01（方案）", False, P_PLAN_MD),
            interface("P 证据结构模板（全字段 null，status=NOT_RUN）", "v1", False, P_TEMPLATE),
        ],
        "extra_files": [
            entry(P_PLAN_MD, "source", "P 实测方案（方法/证据格式/停止条件/与阶段6 接口）"),
            entry(P_TEMPLATE, "input", "P 证据结构模板（防填造结构）"),
            entry(P_CHECKER, "source", "P 证据校验器（结构性禁止填造 + 6 项负向对照）"),
        ],
        "checks": [
            check("P 证据模板校验与负向对照", "PASS",
                  f"python -B scripts/stage4_s4b/validate_frame_period_p_evidence.py --record docs/stage4/s4b_frame_period_p_evidence_template.json --evidence-dir {run_dir('t21_frame_period_p_plan_20261024_r01')}",
                  0, "模板（status=NOT_RUN，全数值 null）合规；6/6 负向对照被拒（填造/回放冒充/样本不足/统计矛盾/门禁缺失/计时器未标定）"),
            check("帧周期 P 数值", "NOT_RUN", None, None,
                  "需真实彩色采集与硬件窗口；本轮全离线，禁止填造；阶段6 T6-A03 相应保持 NOT_RUN"),
            check("硬件操作", "NOT_RUN", None, None, "依 CDX-20261023-019 全离线；未访问板卡"),
        ],
        "limitations": [
            "source_commit 为任务起始 HEAD（f6fa9f0）；本轮改动运行时尚未提交。",
            "本方案本身不是实测证据，不含任何 P 数值，也不构成 G3/G4/G5 依据。",
            "P 的数值来源必须是 camera_live_colour；抓帧回放不得作为 T6-A03 的数值来源。",
        ],
    },
]


def main() -> int:
    """生成全部清单。"""
    missing = []
    blocked = []
    for spec in SPECS:
        target = WORKTREE / run_dir(spec["run_id"])
        if not target.is_dir():
            missing.append(str(target))
            continue
        manifest_path = target / "manifest.json"
        if manifest_path.is_file():
            expected_hash = HISTORICAL_MANIFEST_SHA256.get(spec["run_id"])
            if expected_hash is not None:
                actual_hash = sha256_of(manifest_path)
                if actual_hash != expected_hash:
                    blocked.append(f"{manifest_path}: 历史清单 SHA-256 漂移，expected={expected_hash} actual={actual_hash}")
                    continue
                print(f"[SKIP_IMMUTABLE] {spec['run_id']}：历史清单 SHA-256 已核对，保留原字节")
            else:
                print(f"[SKIP_IMMUTABLE] {spec['run_id']}：清单已存在，保留原字节")
            continue
        if spec["run_id"] in HISTORICAL_MANIFEST_SHA256:
            blocked.append(f"{manifest_path}: 固定历史 RunId 的清单缺失，拒绝从当前源文件重建")
            continue
        files = [entry(f"{run_dir(spec['run_id'])}/{item.name}", role_for(item.name),
                       f"{spec['run_id']} 运行产物（{item.name}）")
                 for item in sorted(target.iterdir()) if item.is_file() and item.name != "manifest.json"]
        for extra in spec["extra_files"]:
            if not any(f["path"] == extra["path"] for f in files):
                files.append(extra)
        manifest = {
            "schema_version": 1,
            "stage": "4",
            "task_id": TASK_ID,
            "run_id": spec["run_id"],
            "source_commit": SOURCE_COMMIT,
            "evidence_dir": run_dir(spec["run_id"]),
            "interfaces": spec["interfaces"],
            "files": files,
            "checks": spec["checks"],
            "tool_versions": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "git": git_version(),
            },
            "limitations": spec["limitations"],
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[OK] {spec['run_id']}：files={len(files)} interfaces={len(spec['interfaces'])} checks={len(spec['checks'])}")
    if missing:
        for path in missing:
            print(f"[FAIL] RunId 目录缺失：{path}")
        return 1
    if blocked:
        for item in blocked:
            print(f"[FAIL] {item}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
