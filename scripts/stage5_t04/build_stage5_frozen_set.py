#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成阶段5 离线范围冻结集 `frozen_set.json`（S5-T04）。

用途
====
把本卡声明的**成员清单**（契约/规格、离线实现、离线证据包、宿主侧上游引用）在冻结基线上
逐件重算并写成 `frozen_set.json`，供 `verification/verify_stage5_frozen_set.py` 复核。
本脚本只读仓库与宿主侧只读引用，不修改任何被冻结文件。

规则（可复现）
==============
- 证据包：顶层文件逐件登记 `file`；顶层目录登记为 `dir_digest`（覆盖目录内全部文件）。
- 所有 `repo` 成员的 `path` 相对仓库根；`host` 成员用绝对路径（跨树/主仓只读引用）。
- 同一份成员清单 + 同一棵树 ⇒ 同一份 `frozen_set.json`。

用法：`python -B scripts/stage5_t04/build_stage5_frozen_set.py [--out <json>]`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
CHECKER = pathlib.Path("D:/FPGA_Competition/verification/check_stage_delivery.py")
# 必须显式 `--out`：默认写死路径会在换 RunId 时覆盖已提交的冻结包（r02 踩坑），故 fail-closed。
DEFAULT_OUT = ""

# ── 成员清单（本卡声明的冻结范围）────────────────────────────────────────────
CONTRACT_FILES = (
    ".gitattributes",
    "docs/stage5/s5a_stage5_display_g0_fields.json",
    "docs/stage5/S5A_stage5_display_g0_spec_v2.md",
    "docs/stage5/s5t03_input_contract_binding_v1.json",
    "docs/stage5/S5T03_input_contract_binding_colour_v1.md",
    "docs/stage5/s5t03_offline_skeleton_params_v1.json",
    "docs/stage5/S5T03_offline_case_skeleton_v1.md",
    "docs/stage5/s5t03_json_contract_v1.json",
    "docs/stage5/s5t03_json_contract_v1.md",
    "docs/stage5/s5a_g0_ur3_decision_20261025_r01.json",
    "docs/stage5/s5a_g0_ur3_decision_20261025_r01.md",
    "docs/stage5/S5T03_stage4_frozen_replay_consumption_v1.md",
    "docs/stage5/S5T03_board_verification_pending_v1.md",
    "docs/stage5/PROVENANCE_s4d_v1_baseline.md",
)

OFFLINE_IMPLEMENTATION_FILES = (
    "verification/s5_display_geometry_reference.py",
    "verification/test_s5_display_geometry_reference.py",
)

OFFLINE_IMPLEMENTATION_DIRS = (
    "scripts/stage5_t03",
)

# 说明（2026-10-27 冻结轮实测）：`scripts/stage5_s5a|s5b|s5c`（S5-A/B/C 历史离线准备）**不纳入**本冻结集：
# 其测试依赖 w4 侧的黄金数据（`s4c_replay_20261021_r05`、`S4-B/20261021_r13`），上游漂移后当前 16 项失败
# （全量 225 项里 19 项失败，含本文件下方几何测试的 1 项夹具缺陷——后者已在本轮修正）。
# 它们不属于本卡定义的"离线 replay/display 路径"，其历史结论按各自 RunId 自证；本轮如实登记为已知缺口。

OFFLINE_EVIDENCE_PACKAGES = (
    "report/evidence/S5-T03/s5t03_offline_replay_display_20261026_r06",
    "report/evidence/S5-T03/s5t03_offline_long_run_replay_20261026_r04",
    "report/evidence/S5-T03/s5t03_multi_geometry_render_20261026_r02",
    "report/evidence/S5-T03/s5t03_json_contract_20261026_r04",
    "report/evidence/S5-T03/s5t03_hud_occlusion_20261026_r02",
    "report/evidence/S5-T03/s5t03_stage4_frozen_replay_20261027_r04",
    "report/evidence/S5-T03/s5t03_stage4_positive_replay_20261027_r01",
    "report/evidence/S5-T01/s5t02_offline_dynamic_map_20261027_r02",
)

# 宿主侧（仓库外）上游只读引用：冻结范围只"引用其字节"，不改写、不复制；
# 证据包/契约仍在各自工作树与主仓内，权威归其所有者。
HOST_REFERENCES = (
    {"id": "stage3_input_frame_full_bin",
     "path": "D:\\codex-worktrees\\dbdf\\report\\evidence\\S3-T05\\t05_stage3_window_20261024_r01\\frame_full.bin",
     "role": "stage3_reference_frame_input_only",
     "note": "阶段3 固定参考帧（BGR888 1280×720 stride 3840），仅作**输入帧/背景**；不代表实时采集或颜色质量"},
    {"id": "stage3_replay_input_binding",
     "path": "D:\\codex-worktrees\\dbdf\\report\\evidence\\S3-T05\\t05_replay_binding_20261025_r01\\replay_input_binding.json",
     "role": "stage3_replay_binding",
     "note": "阶段3 回放输入包绑定记录（含 939fce22… 帧身份与 capture_time 口径）"},
    {"id": "stage4_replay_package_freeze_json",
     "path": "D:\\codex-worktrees\\w4\\report\\evidence\\S4-CTRL\\s4t27_replay_package_freeze_20261027_r01\\replay_package_freeze.json",
     "role": "stage4_replay_package_freeze_record",
     "note": "阶段4 回放结果包冻结记录（consumption_mode=replay_only、contract s4-shared-io 1.3.0 r07 FROZEN_OFFLINE_ONLY）"},
    {"id": "stage4_replay_package_freeze_manifest",
     "path": "D:\\codex-worktrees\\w4\\report\\evidence\\S4-CTRL\\s4t27_replay_package_freeze_20261027_r01\\manifest.json",
     "role": "stage4_replay_package_freeze_manifest",
     "note": "阶段4 冻结包自身的清单"},
    {"id": "stage4_positive_replay_freeze_index",
     "path": "D:\\codex-worktrees\\w4\\report\\evidence\\S4-CTRL\\s4t27_replay_positive_20261027_r01\\freeze_index.json",
     "role": "stage4_boxed_replay_freeze_index",
     "note": "阶段5 离线消费所用的带框阶段4 冻结回放包索引（verdict FROZEN_REPLAY_ONLY_WITH_DETECTIONS）"},
    {"id": "stage4_positive_replay_package",
     "path": "D:\\codex-worktrees\\w4\\report\\evidence\\S4-CTRL\\s4t27_replay_positive_20261027_r01\\task27_replay_result_package_positive.json",
     "role": "stage4_boxed_replay_result_package",
     "note": "带框阶段4 回放结果包本体（离线消费输入）"},
    {"id": "wong_stale_200ms_approval_receipt",
     "path": "D:\\FPGA_Competition\\report\\evidence\\CTRL-DSH-HANDOFF\\decisions\\stage6_approval_receipt_20261023_r01.md",
     "role": "approved_stale_limit_reference",
     "note": "Wong 批准的 stale=200 ms 依据（阶段5 只**引用**，不改写、不重解释）"},
    {"id": "stage3_closeout_partial_open_and_task11",
     "path": "D:\\codex-worktrees\\dbdf\\report\\evidence\\S3-T17\\stage3_closeout_20261026_r01\\manifest.json",
     "role": "stage3_inherited_limitations",
     "note": "阶段3 收尾清单：含 VDMA 首帧 bit11 `PARTIAL_OPEN`、task-11 `BLOCKED_NOT_RUN`、`TIMING-17` 未签核（阶段5 只引用）"},
    {"id": "stage4_freeze_supplement_hardware_limitation",
     "path": "D:\\codex-worktrees\\w4\\docs\\stage4\\s4_stage4_freeze_supplement_hardware_20261027_r01.md",
     "role": "stage4_inherited_limitations",
     "note": "阶段4 冻结补充：`complete_stage4_or_RGB_preprocess=NOT_CLAIMED`（阶段5 只引用）"},
)

FREEZE_TOOLING_FILES = (
    "verification/verify_stage5_frozen_set.py",
    "scripts/stage5_t04/build_stage5_frozen_set.py",
    "scripts/stage5_t04/run_stage5_freeze_evidence.py",
    "scripts/stage5_t04/run_f6_export_selfcheck.py",
)

NOT_FROZEN = (
    {"item": "docs/stage5/S5_stage5_display_spec_draft.md、S5T01_*、S5T02_onboard_dynamic_mapping_taskcard.md",
     "reason": "上游草案/任务卡/运行书，非冻结交付面（历史入口），本轮不登记"},
    {"item": "report/evidence/S5-A|S5-B|S5-C|S5-CTRL|S5-T01 的历史 RunId（含板级 hw_gate/hw_probe/board_dynamic_map/pixel_*）",
     "reason": "历史轮次与**板级**证据：板级项不在本冻结范围（不主张），且历史包按其自身轮次自证；本轮不重写、不冻结"},
    {"item": "scripts/stage5_t01/**（含 P1 C 应用与构建）",
     "reason": "板上应用与构建属板级范围；离线宿主映射实现由 s5t02_offline_dynamic_map_20261027_r02 覆盖"},
    {"item": "scripts/stage5_s5a|s5b|s5c（S5-A/B/C 历史离线准备与测试）",
     "reason": "不属于本卡定义的离线 replay/display 路径；其测试依赖 w4 侧黄金数据（`s4c_replay_20261021_r05`、"
               "`S4-B/20261021_r13`），上游漂移后当前失败（实测：全量 225 项中 19 项失败，其中 s5b 15 项、s5c 3 项、"
               "几何夹具 1 项（已修））；如实登记为已知缺口，不并入冻结范围、不冒称通过"},
    {"item": "report/evidence/S5-T04/s5_freeze_20261027_r00_runner_crash（本冻结轮首次运行器崩溃）",
     "reason": "运行器在解析套件摘要时崩溃（未产出清单），按其真实值保留为独立 RunId，不覆盖重跑；修复见 r01"},
    {"item": "task-27（回放/彩色输入路径实现 + 用回放结果包做离线动态回归）",
     "reason": "该卡整体 NOT_RUN（未按卡交付）：冻结的是既有离线骨架与离线消费，不是 task-27 的完整实现与回归"},
    {"item": "任何 G0/G1/G3/G4/G5 或板级/实物结论",
     "reason": "本冻结只覆盖离线字节集，不主张任何关口通过"},
)

EXTERNAL_REFERENCE_POLICY = (
    "host 成员为跨树/主仓只读引用：默认参与校验（缺失/不符 ⇒ exit 2/1）；"
    "在离开本机的导出副本中可用 --skip-host-references 跳过，但跳过的项会逐条打印，不得当作已验证。"
)

RESTORE_ENTRYPOINTS = (
    "python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --root D:/codex-worktrees/w5 --frozen-set <冻结包>/frozen_set.json",
    "python -B D:/codex-worktrees/w5/verification/verify_stage5_frozen_set.py --frozen-set <冻结包>/frozen_set.json --selftest tmp/5/S5-T04/frozen_selftest",
    "python -B D:/codex-worktrees/w5/scripts/stage5_t04/build_stage5_frozen_set.py --out <新路径>/frozen_set.json",
    "python -B D:/codex-worktrees/w5/scripts/stage5_t04/run_stage5_freeze_evidence.py --run-dir report/evidence/S5-T04/<新RunId> --source-commit <提交>",
    "python -B D:/codex-worktrees/w5/scripts/stage5_t04/run_f6_export_selfcheck.py --commit <冻结提交> --frozen-run-dir report/evidence/S5-T04/<冻结包RunId>",
    "python -B -m unittest <scripts.stage5_t03.test_*> <verification.test_s5_display_geometry_reference>",
    "python -B D:/FPGA_Competition/verification/check_stage_delivery.py --mode evidence --project-root D:/codex-worktrees/w5 --manifest <冻结包>/delivery_manifest.json",
)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dir_digest(path: pathlib.Path) -> tuple[str, int]:
    lines, count = [], 0
    for entry in sorted(path.rglob("*")):
        if entry.is_dir():
            continue
        relative = entry.relative_to(path).as_posix()
        lines.append(f"{relative}\0{sha256_file(entry)}\0{entry.stat().st_size}\n")
        count += 1
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest(), count


def head_commit() -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout.strip()


def build() -> dict:
    members: list[dict] = []

    for path in CONTRACT_FILES:
        full = REPO_ROOT / path
        if not full.is_file():
            raise SystemExit(f"[ENV_ERROR] 契约成员缺失：{path}")
        members.append({"id": f"contract::{pathlib.Path(path).name}", "kind": "file", "scope": "repo",
                        "path": path, "sha256": sha256_file(full), "bytes": full.stat().st_size,
                        "group": "contracts_and_specs"})

    for path in OFFLINE_IMPLEMENTATION_FILES:
        full = REPO_ROOT / path
        if not full.is_file():
            raise SystemExit(f"[ENV_ERROR] 离线实现文件缺失：{path}")
        members.append({"id": f"impl_file::{path}", "kind": "file", "scope": "repo",
                        "path": path, "sha256": sha256_file(full), "bytes": full.stat().st_size,
                        "group": "offline_implementation"})

    for directory in OFFLINE_IMPLEMENTATION_DIRS:
        full = REPO_ROOT / directory
        if not full.is_dir():
            raise SystemExit(f"[ENV_ERROR] 离线实现目录缺失：{directory}")
        digest, count = dir_digest(full)
        members.append({"id": f"impl_dir::{directory}", "kind": "dir_digest", "scope": "repo",
                        "path": directory, "digest_sha256": digest, "file_count": count,
                        "group": "offline_implementation"})

    for package in OFFLINE_EVIDENCE_PACKAGES:
        full = REPO_ROOT / package
        if not full.is_dir():
            raise SystemExit(f"[ENV_ERROR] 离线证据包缺失：{package}")
        group = "offline_evidence_s5t02" if "S5-T01" in package else "offline_evidence_replay_display"
        for entry in sorted(full.iterdir()):
            relative = f"{package}/{entry.name}"
            if entry.is_file():
                members.append({"id": f"evidence_file::{relative}", "kind": "file", "scope": "repo",
                                "path": relative, "sha256": sha256_file(entry),
                                "bytes": entry.stat().st_size, "group": group})
            elif entry.is_dir():
                digest, count = dir_digest(entry)
                members.append({"id": f"evidence_dir::{relative}", "kind": "dir_digest", "scope": "repo",
                                "path": relative, "digest_sha256": digest, "file_count": count,
                                "group": group})
            else:
                raise SystemExit(f"[ENV_ERROR] 证据包内存在非普通条目：{relative}")

    for reference in HOST_REFERENCES:
        full = pathlib.Path(reference["path"])
        if not full.is_file():
            raise SystemExit(f"[ENV_ERROR] 宿主侧引用缺失：{reference['path']}")
        members.append({"id": f"host::{reference['id']}", "kind": "file", "scope": "host",
                        "path": reference["path"], "sha256": sha256_file(full),
                        "bytes": full.stat().st_size, "group": "host_upstream_references",
                        "role": reference["role"], "note": reference["note"]})

    return {
        "schema_version": "gestureforge_s5t04_frozen_set_v1",
        "frozen_set_id": "S5T04-OFFLINE-SCOPE-FROZEN-20261027-R01",
        "task_id": "S5-T04",
        "stage": 5,
        "freeze_kind": "OFFLINE_SCOPE_FROZEN",
        "baseline_commit": head_commit(),
        "generated_utc8": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) + "+08:00",
        "generator": "scripts/stage5_t04/build_stage5_frozen_set.py",
        "verifier": "verification/verify_stage5_frozen_set.py",
        "claims": ["离线契约/规格字节", "离线实现字节", "离线证据包字节", "宿主侧上游引用字节"],
        "non_claims": ["G0/G1/G3/G4/G5", "板级/实物/实时结论", "task-27 完整实现与回归"],
        "external_reference_policy": EXTERNAL_REFERENCE_POLICY,
        "restore_entrypoints": list(RESTORE_ENTRYPOINTS),
        "byte_fidelity_note": (
            "冻结成员一律按**工作树原始字节**登记（`.gitattributes` 已在成员内，S5-A/T01/T03/T04 等目录为 `-text`）。"
            "F6 导出/检出必须同时携带 `.gitattributes`，否则 `core.autocrlf` 会在导出时把 LF 转成 CRLF、"
            "导致 44 项哈希不符（r01 实测踩坑，r02 已修）。"),
        "superseded_runs": [
            {"run_id": "s5_freeze_20261027_r00_runner_crash",
             "reason": "运行器在解析套件摘要时崩溃（未产出清单）；保留不改写"},
            {"run_id": "s5_freeze_20261027_r01",
             "reason": "F6 自证发现冻结工具缺陷：导出/检出未携带 `.gitattributes` ⇒ 换行被转换、44 项哈希不符；"
                       "r02 已修工具并把 `.gitattributes` 纳入冻结集，故 r01 被取代（保留不改写）"},
        ],
        "not_frozen": list(NOT_FROZEN),
        "members": members,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    if not args.out:
        print("[ENV_ERROR] 必须显式指定 --out（禁止默认覆盖已提交的冻结包）", file=sys.stderr)
        return 2
    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    groups: dict[str, int] = {}
    for member in data["members"]:
        groups[member["group"]] = groups.get(member["group"], 0) + 1
    print(json.dumps({"out": str(out), "baseline_commit": data["baseline_commit"],
                      "members": len(data["members"]), "by_group": groups,
                      "frozen_set_sha256": sha256_file(out)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())