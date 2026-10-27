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
- 证据包/实现目录：顶层文件逐件登记 `file`；目录登记为 `file_set`（逐件列 path/sha256/bytes，仅含 Git 已跟踪文件）。
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
    "docs/stage5/S5T27_replay_colour_input_path_v1.md",
    "scripts/stage5_t27/.gitattributes",
    "report/evidence/S5-T27/.gitattributes",
)

OFFLINE_IMPLEMENTATION_FILES = (
    "verification/s5_display_geometry_reference.py",
    "verification/test_s5_display_geometry_reference.py",
)

OFFLINE_IMPLEMENTATION_DIRS = (
    "scripts/stage5_t03",
    "scripts/stage5_t27",
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
    "report/evidence/S5-T27/s5t27_replay_colour_20261027_r02",
    "report/evidence/S5-T27/s5t27_clean_checkout_20261027_r02",
    "report/evidence/S5-T27/s5t27_hash_basis_authoritative_20261027_r01",
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
    "scripts/stage5_t27/inline_manifest_basis.py",
    "scripts/stage5_t27/run_clean_checkout_proof.py",
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


def tracked_files(directory: pathlib.Path) -> list[pathlib.Path]:
    """该目录下**已纳入 Git** 的文件（相对仓库根的 posix 路径），按路径排序。

    冻结集只登记提交内的字节：未跟踪的生成物（`__pycache__`、构建产物等）不属于冻结范围，
    否则 F6「单独检出后自检」必然因副本缺少这些文件而误报。构建阶段对未跟踪成员直接 fail-closed。
    """
    relative = directory.relative_to(REPO_ROOT).as_posix() if directory.is_absolute() else directory.as_posix()
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", relative],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise SystemExit(f"[ENV_ERROR] git ls-files 失败：{relative}\n{completed.stderr}")
    names = [name for name in completed.stdout.split("\0") if name]
    return sorted(REPO_ROOT / name for name in names)


def file_set_member(directory: pathlib.Path, member_id: str, group: str,
                    skip_absolute: set[pathlib.Path] | None = None) -> dict:
    """目录成员：逐件登记**已跟踪文件**；`skip_absolute` 内已由更具体成员登记的路径不再重复列入。

    M3（r07 修）：同一路径只登记一次（契约/单文件成员优先），保证"成员 id 唯一 + 文件路径唯一、
    计数可复算"；被跳过的路径仍由更具体成员冻结，不丢覆盖。
    """
    entries = []
    for path in tracked_files(directory):
        if skip_absolute and path.resolve() in skip_absolute:
            continue
        entries.append({"path": path.relative_to(directory).as_posix(),
                        "sha256": sha256_file(path), "bytes": path.stat().st_size})
    if not entries:
        raise SystemExit(f"[ENV_ERROR] 目录内没有已跟踪文件，无法作为 file_set 冻结：{directory}")
    return {"id": member_id, "kind": "file_set", "scope": "repo",
            "path": directory.relative_to(REPO_ROOT).as_posix(), "files": entries,
            "group": group}


def assert_tracked(path: pathlib.Path, label: str) -> None:
    """单文件成员必须已纳入 Git（否则无法由提交单独复现）。"""
    relative = path.relative_to(REPO_ROOT).as_posix()
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "--error-unmatch", "--", relative],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise SystemExit(f"[ENV_ERROR] 冻结成员未纳入 Git（无法由提交复现）：{label} -> {relative}")


def head_commit() -> str:
    completed = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
    return completed.stdout.strip()


def build() -> dict:
    members: list[dict] = []
    registered: set[pathlib.Path] = set()

    for path in CONTRACT_FILES:
        full = REPO_ROOT / path
        if not full.is_file():
            raise SystemExit(f"[ENV_ERROR] 契约成员缺失：{path}")
        assert_tracked(full, path)
        members.append({"id": f"contract::{path}", "kind": "file", "scope": "repo",
                        "path": path, "sha256": sha256_file(full), "bytes": full.stat().st_size,
                        "group": "contracts_and_specs"})
        registered.add(full.resolve())

    for path in OFFLINE_IMPLEMENTATION_FILES:
        full = REPO_ROOT / path
        if not full.is_file():
            raise SystemExit(f"[ENV_ERROR] 离线实现文件缺失：{path}")
        assert_tracked(full, path)
        members.append({"id": f"impl_file::{path}", "kind": "file", "scope": "repo",
                        "path": path, "sha256": sha256_file(full), "bytes": full.stat().st_size,
                        "group": "offline_implementation"})
        registered.add(full.resolve())

    for directory in OFFLINE_IMPLEMENTATION_DIRS:
        full = REPO_ROOT / directory
        if not full.is_dir():
            raise SystemExit(f"[ENV_ERROR] 离线实现目录缺失：{directory}")
        members.append(file_set_member(full, f"impl_dir::{directory}", "offline_implementation", registered))

    for package in OFFLINE_EVIDENCE_PACKAGES:
        full = REPO_ROOT / package
        if not full.is_dir():
            raise SystemExit(f"[ENV_ERROR] 离线证据包缺失：{package}")
        group = "offline_evidence_s5t02" if "S5-T01" in package else "offline_evidence_replay_display"
        for entry in sorted(full.iterdir()):
            relative = f"{package}/{entry.name}"
            if entry.is_file():
                assert_tracked(entry, relative)
                members.append({"id": f"evidence_file::{relative}", "kind": "file", "scope": "repo",
                                "path": relative, "sha256": sha256_file(entry),
                                "bytes": entry.stat().st_size, "group": group})
                registered.add(entry.resolve())
            elif entry.is_dir():
                members.append(file_set_member(entry, f"evidence_dir::{relative}", group, registered))
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

    # M3：唯一性与覆盖计数（可复算；不一致直接 fail-closed）
    ids = [m["id"] for m in members]
    duplicate_ids = sorted({i for i in ids if ids.count(i) > 1})
    repo_paths = [m["path"] for m in members if m.get("kind") == "file" and m.get("scope", "repo") == "repo"]
    for member in members:
        if member.get("kind") == "file_set":
            base = member["path"]
            repo_paths.extend(f"{base}/{f['path']}" for f in member["files"])
    duplicate_paths = sorted({x for x in repo_paths if repo_paths.count(x) > 1})
    if duplicate_ids:
        raise SystemExit(f"[ENV_ERROR] 成员 id 不唯一：{duplicate_ids}")
    if duplicate_paths:
        raise SystemExit(f"[ENV_ERROR] repo 文件路径重复登记：{duplicate_paths}")
    coverage = {
        "members": len(members),
        "unique_member_ids": len(set(ids)),
        "by_group": {},
        "repo_file_registrations": len(repo_paths),
        "repo_unique_paths": len(set(repo_paths)),
        "host_references": sum(1 for m in members if m.get("scope") == "host"),
        "note": ("成员 id 由路径派生（唯一）；同一路径只登记一次（契约/单文件成员优先，file_set 跳过已登记路径）。"
                 "repo_file_registrations 与 repo_unique_paths 必须相等，否则构建器 fail-closed。"),
    }
    for member in members:
        coverage["by_group"][member["group"]] = coverage["by_group"].get(member["group"], 0) + 1

    return {
        "coverage": coverage,
        "schema_version": "gestureforge_s5t04_frozen_set_v1",
        "frozen_set_id": "S5T04-OFFLINE-SCOPE-FROZEN-20261027-R03",
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
        "tracked_only_rule": "冻结集只登记 Git 已跟踪文件；构建时对未跟踪成员 fail-closed（不可由提交单独复现的一律拒收）",
        "restore_entrypoints": list(RESTORE_ENTRYPOINTS),
        "byte_fidelity_note": (
            "冻结成员一律按**工作树原始字节**登记，且**只登记已纳入 Git 的文件**（目录成员为 `file_set`，"
            "逐件列 path/sha256/bytes）：未跟踪的生成物（`__pycache__`、构建产物等）不属于冻结范围，"
            "否则 F6「单独检出后自检」会因副本缺少这些文件而误报（r01/r04 实测踩坑）。"
            "`.gitattributes` 本身也是冻结成员并带 `.gitattributes -text` 自规则，保证其字节不经 EOL 转换。"),
        "superseded_runs": [
            {"run_id": "s5_freeze_20261027_r00_runner_crash",
             "reason": "运行器解析套件摘要时崩溃（int('19, skipped')），未产出清单；保留不改写"},
            {"run_id": "s5_freeze_20261027_r01",
             "reason": "F6 自证发现冻结工具缺陷：导出/检出未携带 .gitattributes ⇒ 换行被转换、44 项哈希不符；r02 起修工具并把 .gitattributes 纳入冻结集，故 r01 被取代（保留不改写）"},
            {"run_id": "s5_freeze_20261027_r02_incomplete_builder_path",
             "reason": "构建器曾以默认 --out 覆盖已提交的 r01 包（已用 git checkout 恢复）；该目录为残留，现构建器强制显式 --out。属工具缺陷，非成员内容问题（保留不改写）"},
            {"run_id": "s5_freeze_20261027_r03",
             "reason": "校验器/F6 驱动硬编码 r01 RunId ⇒ 改为强制显式 --frozen-set/--frozen-run-dir，r03 被取代"},
            {"run_id": "s5_freeze_20261027_r04",
             "reason": "3 项不符：__pycache__/未跟踪产物污染目录摘要、.gitattributes 自身换行不稳定 ⇒ 改为 file_set（仅 Git 已跟踪文件）+ .gitattributes -text 自规则，r04 被取代"},
            {"run_id": "s5_freeze_20261027_r06",
             "reason": "首版再冻结（93 成员、tag r2）；独立复审 CHANGES_REQUIRED：M1 文书范围误报（s5a/b/c、8 包、F6 r01 路径）、"
                       "M2 范围自相矛盾（not_frozen 称 task-27 NOT_RUN）、M3 成员 id 非唯一 + 重复路径登记。"
                       "r07 修模板重建冻结集（唯一 id/去重/覆盖计数），故 r06 被取代；r06 包与 tag r2 保留不改"},
            {"run_id": "s5_freeze_20261027_r05",
             "reason": "上一轮正式冻结（tag stage5-offline-freeze-20261027 → 26b7439；77 成员）；本 r06 为再冻结：纳入 task-27 增量与 N1 修复并清 5 项非阻断（F1–F5），故 r05 被 r06 取代。r05 字节与 tag 均不改不删（保留为历史）"},
        ],
        "re_freeze": {
            "reason": "task-27（回放/彩色输入路径 + 离线动态回归）交付 + 复审 N1 修复（子目录 .gitattributes、内联 hash_basis）纳入冻结；并清 S5-T04 复审 F1–F5",
            "previous_frozen_set": "report/evidence/S5-T04/s5_freeze_20261027_r05/frozen_set.json",
            "previous_frozen_set_sha256": "109254238e2aede8ab9005ed153e768e611c3ba325a5b1b75b312b415408b1bf",
            "previous_baseline_commit": "26b743901b4ec76107ca2cd6a010337a5ae40bf2",
            "previous_tag": "stage5-offline-freeze-20261027",
            "previous_member_count": 77,
            "delta_members": [
                "契约/规格 +3：docs/stage5/S5T27_replay_colour_input_path_v1.md、scripts/stage5_t27/.gitattributes、report/evidence/S5-T27/.gitattributes",
                "离线实现 +1 file_set：scripts/stage5_t27（跟踪文件逐件登记）",
                "离线实现扩展：scripts/stage5_t03 file_set 由 25 件扩到 28 件（task-27 三件套）",
                "离线证据包 +3：S5-T27 r02 主包 / clean_checkout r02 自证包 / hash_basis_authoritative r01",
                "冻结工具 +2：inline_manifest_basis.py、run_clean_checkout_proof.py",
            ],
            "carried_forward_rule": "旧 77 成员的**路径与成员内既有文件字节**保留；唯一变化是 `impl_dir::scripts/stage5_t03` file_set 追加 3 个文件（已在 delta_members 披露），其余成员的 path/sha256/bytes 未变。",
        },
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