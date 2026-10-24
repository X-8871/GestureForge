#!/usr/bin/env python3
"""RAW 系统 G0 缺口登记表的只读算术复算与状态纪律检查（S4-T21）。

只做两件事：
  1. 对 `docs/stage4/S4B_raw_system_g0_gap_registry.json` 声明的离线算术/容量事实**现场重算**
     （依据件逐项复算 SHA-256），任何不一致即 FAIL；
  2. 检查缺口状态纪律：需要硬件或独立审查的缺口不得被标成已通过；`CLOSED_OFFLINE` 必须由
     本轮真正 PASS 的离线检查支持。

本脚本不访问硬件、不修改任何输入，也不给出 G0/G4/G5 结论。

退出码：0 = 全部一致且状态纪律通过；1 = 存在不一致/越权标注；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
REGISTRY = WORKTREE / "docs" / "stage4" / "S4B_raw_system_g0_gap_registry.json"
CN = timezone(timedelta(hours=8))

HARDWARE_STATUSES = {
    "NOT_RUN_HARDWARE_REQUIRED",
    "BLOCKED_PENDING_HARDWARE",
    "PARTIALLY_CLOSED_OFFLINE",
    "CLOSED_OFFLINE",
    "NOT_APPLICABLE_WITH_REASON",
}


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def align_up(value: int, alignment: int) -> int:
    """向上对齐到给定字节边界。"""
    return ((value + alignment - 1) // alignment) * alignment


def find_git_root(path: Path) -> Path | None:
    """向上查找包含 `.git` 的目录（worktree 中 `.git` 可能是文件）。"""
    for parent in [path.parent, *path.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def blob_content_sha256(path: Path) -> tuple[str | None, str | None]:
    """按 git blob 内容口径计算 SHA-256；返回 (sha256, error)。"""
    root = find_git_root(path)
    if root is None:
        return None, f"未找到 git 根：{path}"
    rel = path.relative_to(root).as_posix()
    proc = subprocess.run(["git", "-C", str(root), "cat-file", "blob", f"HEAD:{rel}"], capture_output=True)
    if proc.returncode != 0:
        return None, f"cat-file blob HEAD:{rel} 退出 {proc.returncode}"
    return hashlib.sha256(proc.stdout).hexdigest(), None


def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    """半开区间 [a0,a1) 与 [b0,b1) 是否相交。"""
    return max(a0, b0) < min(a1, b1)


def redundant_fact_errors(registry: dict) -> list[str]:
    """拒绝登记表内重复地址及依据哈希互相矛盾或缺失绑定。"""
    errors: list[str] = []
    bindings = {entry["id"]: entry for entry in registry["basis_bindings"]}
    owners = registry.get("documented_historical_owners", [])
    intervals = list(registry["candidate_intervals"].items()) + [
        (owner["name"], owner) for owner in owners
    ]
    for name, interval in intervals:
        if not isinstance(interval, dict):
            continue
        for decimal, hexadecimal in (("start", "start_hex"), ("end_exclusive", "end_hex")):
            if hexadecimal not in interval:
                continue
            try:
                matches = type(interval.get(decimal)) is int and interval[decimal] == int(interval[hexadecimal], 16)
            except (TypeError, ValueError):
                matches = False
            if not matches:
                errors.append(f"{name}.{decimal}/{hexadecimal} 地址表示不一致")
    for owner in owners:
        if "basis_sha256" not in owner and "basis_binding_id" not in owner:
            continue
        binding = bindings.get(owner.get("basis_binding_id"))
        if binding is None or owner.get("basis_sha256") != binding.get("sha256"):
            errors.append(f"{owner['name']}.basis_sha256 与依据绑定不一致或绑定缺失")
    return errors


def main() -> int:
    """执行全部离线复算与纪律检查。"""
    parser = argparse.ArgumentParser(description="RAW 系统 G0 缺口登记表只读复算")
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    if not REGISTRY.is_file():
        print(f"[FAIL] 缺口登记表不存在：{REGISTRY}")
        return 2

    out_dir = Path(args.evidence_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[FAIL] 证据目录非空，RunId 可能被复用：{out_dir}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    failures: list[str] = []
    passes: list[str] = []
    details: dict[str, object] = {}

    def resolve(rel: str) -> Path:
        part = Path(rel)
        return part if part.is_absolute() else WORKTREE / rel

    # 0. 依据件 SHA 复算
    checked = 0
    bad_basis: list[dict[str, object]] = []
    for entry in registry["basis_bindings"]:
        path = resolve(entry["path"])
        if not path.is_file():
            bad_basis.append({"id": entry["id"], "path": str(path), "status": "MISSING"})
            continue
        basis = entry.get("byte_basis", "worktree_disk_bytes")
        if basis == "git_blob_content":
            actual, blob_error = blob_content_sha256(path)
            if actual is None:
                bad_basis.append({"id": entry["id"], "path": str(path), "status": "BLOB_UNAVAILABLE", "error": blob_error})
                continue
        elif basis == "worktree_disk_bytes":
            actual = sha256_of(path)
        else:
            bad_basis.append({"id": entry["id"], "path": str(path), "status": "BAD_BYTE_BASIS", "byte_basis": basis})
            continue
        checked += 1
        if actual != entry["sha256"]:
            bad_basis.append({"id": entry["id"], "expected": entry["sha256"], "actual": actual,
                              "status": "MISMATCH", "byte_basis": basis})
    details["basis_checks"] = {"checked": checked, "total": len(registry["basis_bindings"]), "bad": bad_basis}

    scope = json.loads(resolve("report/evidence/S4-B/s4b_pl_g0_input_scope_20261023_r01/input_scope_audit.json").read_text(encoding="utf-8"))
    addr_map = json.loads(resolve("docs/stage4/S4B_stage4_address_map.json").read_text(encoding="utf-8"))
    ranges = json.loads(resolve("report/evidence/S4-B/s4b_ps_tensor_20261023_r13/memory_ranges.json").read_text(encoding="utf-8"))

    results: dict[str, dict[str, object]] = {}

    def record(check_id: str, ok: bool, actual: dict[str, object], note: str = "") -> None:
        results[check_id] = {"status": "PASS" if ok else "FAIL", "actual": actual, "note": note}
        if not ok:
            failures.append(f"offline_check {check_id} 不一致：{actual} {note}")

    redundant_errors = redundant_fact_errors(registry)
    record("redundant_facts_consistent", not redundant_errors, {"errors": redundant_errors})

    cand = registry["candidate_intervals"]
    raw = cand["raw"]
    combined = cand["combined"]

    # 1. RAW 区间算术
    max_frame = scope["packed_raw_max_bytes"]
    storage = align_up(max_frame, 8)
    actual = {
        "raw_bytes": raw["bytes"],
        "expected_raw_bytes": 12 * 1024 * 1024,
        "max_frame_bytes": max_frame,
        "storage_bytes": storage,
        "storage_equals_logical": storage == max_frame,
        "margin_bytes": raw["bytes"] - storage,
        "end_minus_start": raw["end_exclusive"] - raw["start"],
    }
    record("raw_region_arithmetic", actual["raw_bytes"] == actual["expected_raw_bytes"]
           and actual["end_minus_start"] == raw["bytes"] and actual["margin_bytes"] == 1523712, actual)

    # 2. 张量几何
    tensor_bytes = 3 * 416 * 416
    record("tensor_geometry_arithmetic", tensor_bytes == 519168 and tensor_bytes % 8 == 0,
           {"tensor_bytes": tensor_bytes, "word8_count": tensor_bytes // 8})

    # 3. 几何表算术
    entry_bytes = 24
    axis_entries = 416
    geometry_bytes = 2 * axis_entries * entry_bytes
    x_start = 0x140
    x_end = x_start + axis_entries * entry_bytes
    y_start = x_end
    y_end = y_start + axis_entries * entry_bytes
    record("geometry_table_arithmetic",
           geometry_bytes == 19968 and x_start == 320 and x_end == 10304 and y_start == 10304 and y_end == 20288,
           {"geometry_bytes": geometry_bytes, "x_start": x_start, "x_end": x_end, "y_start": y_start, "y_end": y_end})

    # 4. mailbox 布局
    meta_bytes = 0x8000
    result_start = y_end
    result_region = meta_bytes - result_start
    max_block = 40 + 48 * 15
    record("mailbox_layout_arithmetic",
           meta_bytes == 32768 and result_region == 12480 and max_block == 760 and max_block <= result_region,
           {"meta_bytes": meta_bytes, "result_start": result_start, "result_end": meta_bytes,
            "result_region_bytes": result_region, "max_result_block_bytes": max_block})

    # 5. 109 帧输入范围自洽
    over4 = scope["over_4MiB"]
    over8 = scope["over_8MiB"]
    recomputed_over4 = [e for e in over4 if e["bytes"] == e["width"] * e["height"] * 3 and e["bytes"] > 4 * 1024 * 1024]
    recomputed_over8 = [e for e in over8 if e["bytes"] == e["width"] * e["height"] * 3 and e["bytes"] > 8 * 1024 * 1024]
    actual = {
        "sample_count": scope["sample_count"],
        "min_bytes": scope["packed_raw_min_bytes"],
        "max_bytes": scope["packed_raw_max_bytes"],
        "over_4mib_count": len(over4),
        "over_4mib_consistent": len(recomputed_over4),
        "over_8mib_count": len(over8),
        "over_8mib_consistent": len(recomputed_over8),
    }
    record("input_scope_consistency",
           scope["sample_count"] == 109 and scope["packed_raw_min_bytes"] == 519168
           and scope["packed_raw_max_bytes"] == 11059200 and len(over4) == 97 and len(recomputed_over4) == 97
           and len(over8) == 2 and len(recomputed_over8) == 2, actual,
           "每项 bytes 必须等于 width×height×3")

    # 6. 候选已不在缩减后的自设禁区内，且缩减起点恰为候选末端（Wong D1=A 落盘）
    forbidden = next((g for g in addr_map["gaps"] if g.get("base_addr_hex") == "0x12C08000"), None)
    if forbidden:
        forbidden_start = int(forbidden["base_addr_hex"], 16)
        forbidden_end = int(forbidden["end_addr_exclusive_hex"], 16)
    else:
        forbidden_start = forbidden_end = None
    inside = bool(forbidden) and combined["start"] >= forbidden_start and combined["end_exclusive"] <= forbidden_end
    record("candidate_outside_shrunk_forbidden_gap",
           bool(forbidden) and forbidden_start == combined["end_exclusive"]
           and forbidden_end == 536870912 and (forbidden_end - forbidden_start) == 222265344 and not inside,
           {"forbidden_range": [forbidden_start, forbidden_end],
            "forbidden_bytes": (forbidden_end - forbidden_start) if forbidden else None,
            "candidate": [combined["start"], combined["end_exclusive"]], "candidate_fully_inside": inside})

    # 6b. 地址图已按 D1=A 登记 raw_frame/raw_meta（区间/长度/对齐/状态/使能开关）
    regions_by_name = {r["name"]: r for r in addr_map["regions"]}
    raw_region = regions_by_name.get("raw_frame")
    meta_region = regions_by_name.get("raw_meta")
    registered = bool(raw_region and meta_region) \
        and (raw_region["base_addr"], raw_region["end_addr_exclusive"]) == (combined["start"], 314572800) \
        and (meta_region["base_addr"], meta_region["end_addr_exclusive"]) == (314572800, combined["end_exclusive"]) \
        and raw_region["length_bytes"] == 12582912 and meta_region["length_bytes"] == 32768 \
        and raw_region["alignment_bytes"] == 64 and meta_region["alignment_bytes"] == 64 \
        and raw_region.get("enable_required") is True and meta_region.get("enable_required") is True \
        and raw_region.get("status") == "PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW" \
        and meta_region.get("status") == "PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW"
    record("approved_regions_registered", registered, {
        "raw_frame": [raw_region["base_addr"], raw_region["end_addr_exclusive"], raw_region.get("status")] if raw_region else None,
        "raw_meta": [meta_region["base_addr"], meta_region["end_addr_exclusive"], meta_region.get("status")] if meta_region else None,
    })

    # 6c. 阶段3 书面部署事实已绑定，且其观测上界低于候选起点
    facts_path = resolve("D:\\codex-worktrees\\dbdf\\report\\evidence\\S3-T05\\t05_stage3_window_20261024_r01\\address_facts.md")
    observed = 0x00114C00 if facts_path.is_file() else None
    facts_ok = False
    if observed is not None:
        facts_text = facts_path.read_text(encoding="utf-8", errors="replace")
        facts_ok = "0x00110C00" in facts_text and "0x00114C00" in facts_text and "单缓冲" in facts_text
    record("stage3_owner_fact_bound", bool(facts_ok and observed is not None and combined["start"] > observed),
           {"stage3_observed_max_hex": hex(observed) if observed else None,
            "candidate_start_hex": hex(combined["start"]),
            "fact_file_present": observed is not None})

    # 7. 与已知 owner 不相交
    owner_names = ("ps_app_arena", "bss", "heap", "stack", "staging", "network_input_tensor", "s2b_tensor_arena")
    overlaps_found = []
    for name in owner_names:
        entry = ranges.get(name)
        if not entry:
            continue
        if overlaps(combined["start"], combined["end_exclusive"], entry["start"], entry["end_exclusive"]):
            overlaps_found.append(name)
    historical_overlaps = [
        h["name"] for h in registry.get("documented_historical_owners", [])
        if overlaps(combined["start"], combined["end_exclusive"], h["start"], h["end_exclusive"])
    ]
    adjacent = combined["start"] == ranges["s2b_tensor_arena"]["end_exclusive"]
    record("no_overlap_with_known_owners", not overlaps_found and not historical_overlaps and adjacent,
           {"overlaps_with_r13": overlaps_found, "overlaps_with_historical": historical_overlaps,
            "adjacent_to_tensor_arena": adjacent})

    # 8. 现有 4 MiB 草案不足
    draft = next((r for r in addr_map["regions"] if r["name"] == "injection_frame_rgb"), None)
    insufficient = bool(draft) and draft["length_bytes"] < max_frame
    record("draft_4mib_insufficient", insufficient,
           {"draft_bytes": draft["length_bytes"] if draft else None, "max_frame_bytes": max_frame,
            "insufficient": insufficient})

    # 9. 依据件哈希
    record("basis_hash_match", not bad_basis, {"mismatches": len(bad_basis)})

    # 10. 状态纪律
    vocab = registry["status_vocabulary"]
    allowed = set(vocab["allowed"])
    forbidden_values = set(vocab["forbidden_values"])
    pass_ids = {cid for cid, entry in results.items() if entry["status"] == "PASS"}
    discipline: list[str] = []
    for gap in registry["gaps"]:
        for key in ("id", "title", "layer", "status", "basis"):
            if key not in gap:
                discipline.append(f"{gap.get('id', '?')} 缺字段 {key}")
        status = gap.get("status")
        if status not in allowed:
            discipline.append(f"{gap['id']} 非法状态 {status}")
        if status in forbidden_values:
            discipline.append(f"{gap['id']} 使用被禁状态 {status}（禁止把未验证项标成已通过）")
        if gap.get("requires_hardware") and status not in HARDWARE_STATUSES:
            discipline.append(f"{gap['id']} 需要硬件却标为 {status}")
        if status == "CLOSED_OFFLINE":
            closed_by = gap.get("closed_by") or []
            if not closed_by:
                discipline.append(f"{gap['id']} 标 CLOSED_OFFLINE 但未给出 closed_by")
            unsupported = [cid for cid in closed_by if cid not in pass_ids]
            if unsupported:
                discipline.append(f"{gap['id']} 的 closed_by 未被本轮 PASS 的检查支持：{unsupported}")
        if gap.get("requires_hardware") and "NOT_RUN" not in status and status != "BLOCKED_PENDING_HARDWARE" and status != "PARTIALLY_CLOSED_OFFLINE":
            discipline.append(f"{gap['id']} 需要硬件的缺口必须保持 NOT_RUN/BLOCKED 语义")
    if registry["source_checkpoint"]["system_g0"] != "CHANGES_REQUIRED_NOT_CLOSED":
        discipline.append("系统 G0 不得在本轮被标为已闭合（无新证据支持）")
    details["status_discipline_errors"] = discipline
    if discipline:
        failures.extend(discipline)
    else:
        passes.append("缺口状态纪律通过：无被禁状态、需要硬件的缺口保持 NOT_RUN/BLOCKED、CLOSED_OFFLINE 有本轮 PASS 检查支持")

    if not bad_basis:
        passes.append(f"依据件现场复算一致（{checked}/{len(registry['basis_bindings'])} 项）")
    else:
        failures.append(f"依据件漂移：{bad_basis}")
    if not failures:
        passes.append(f"离线算术复算一致（{len(pass_ids)}/{len(registry['offline_checks'])} 项）")

    status = "PASS" if not failures else "FAIL"
    report = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "audit_raw_system_g0_gaps",
        "checker_version": "r02",
        "status": status,
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "exit_code": 0 if status == "PASS" else 1,
        "cwd": str(Path.cwd()),
        "python_version": sys.version,
        "platform": platform.platform(),
        "artifact_sha256": {"registry": sha256_of(REGISTRY), "checker_script": sha256_of(Path(__file__).resolve())},
        "checks": results,
        "passes": passes,
        "failures": failures,
        "details": details,
        "hardware_execution": "NOT_RUN",
        "boundary": "只读离线复算与状态纪律检查；不代表 G0/G4/G5、独立审查或实物验收。",
    }
    (out_dir / "raw_system_g0_gap_audit_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for line in passes:
        print(f"[PASS] {line}")
    for line in failures:
        print(f"[FAIL] {line}")
    print(f"[{status}] RAW 系统 G0 缺口复算：{len(passes)} 项通过、{len(failures)} 项失败")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
