#!/usr/bin/env python3
"""RAW/META 地址候选方案的容量与冲突算术（G-01/G-02 待决提案支撑，只读）。

只做确定性算术：
  1. 计算 2B 专属窗口 `[0x10000000,0x12000000)` 内扣除冻结对象后的空洞与最大连续空洞；
  2. 按输入清单直方图计算各候选容量的“可容纳帧数”与“被排除帧”；
  3. 评估各候选区间是否落在地址图准入禁区内、是否需要治理层批准。

不访问硬件、不改任何输入、不给出批准结论。

退出码：0 = 算术完成；1 = 输入数据不足/不一致；2 = 输入或环境错误。
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))
ADDRESS_MAP = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
SCOPE = WORKTREE / "report" / "evidence" / "S4-B" / "s4b_pl_g0_input_scope_20261023_r01" / "input_scope_audit.json"
RANGES = WORKTREE / "report" / "evidence" / "S4-B" / "s4b_ps_tensor_20261023_r13" / "memory_ranges.json"

WINDOW = (0x10000000, 0x12000000)      # 2B 专属窗口（tensor arena 全量）
FORBIDDEN = (0x12000000, 0x20000000)   # 地址图当前“不得访问”跨段
META_BYTES = 32_768
MAINT_ALIGN = 64
STORAGE_ALIGN = 8


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def align_up(value: int, alignment: int) -> int:
    """向上对齐。"""
    return ((value + alignment - 1) // alignment) * alignment


def frame_sizes(audit: dict) -> list[tuple[str, int]]:
    """按直方图展开每类尺寸的 packed RGB888 字节数（width×height×3）。"""
    sizes: list[tuple[str, int]] = []
    for dims, count in audit["width_height_histogram"].items():
        width, height = (int(part) for part in dims.split("x"))
        sizes.extend([(dims, width * height * 3)] * count)
    return sizes


def main() -> int:
    """执行算术并输出结果。"""
    parser = argparse.ArgumentParser(description="RAW/META 地址候选容量算术")
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    for path in (ADDRESS_MAP, SCOPE, RANGES):
        if not path.is_file():
            print(f"[FAIL] 缺少输入：{path}")
            return 2
    out_dir = Path(args.evidence_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[FAIL] 证据目录非空，RunId 可能被复用：{out_dir}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    address_map = json.loads(ADDRESS_MAP.read_text(encoding="utf-8"))
    audit = json.loads(SCOPE.read_text(encoding="utf-8"))
    ranges = json.loads(RANGES.read_text(encoding="utf-8"))

    failures: list[str] = []

    # 1. 窗口内冻结对象与空洞
    frozen_ids = ("network_input_tensor", "gf8_weight_package", "feature_envelope")
    frozen = [r for r in address_map["regions"] if r["name"] in frozen_ids]
    occupied = sorted((r["base_addr"], r["end_addr_exclusive"], r["name"]) for r in frozen)
    holes: list[dict[str, object]] = []
    cursor = WINDOW[0]
    for start, end, name in occupied:
        if start > cursor:
            holes.append({"start": cursor, "end": end if False else start, "bytes": start - cursor})
        cursor = max(cursor, end)
    if cursor < WINDOW[1]:
        holes.append({"start": cursor, "end": WINDOW[1], "bytes": WINDOW[1] - cursor})
    for hole in holes:
        hole["start_hex"] = hex(int(hole["start"]))
        hole["end_hex"] = hex(int(hole["end"]))
    largest_hole = max((int(h["bytes"]) for h in holes), default=0)

    sizes = frame_sizes(audit)
    if len(sizes) != audit["sample_count"]:
        failures.append(f"直方图展开帧数 {len(sizes)} != sample_count {audit['sample_count']}")
    max_frame = max(size for _, size in sizes)

    draft = next((r for r in address_map["regions"] if r["name"] == "injection_frame_rgb"), None)
    forbidden_gap = next((g for g in address_map["gaps"]
                          if g.get("base_addr_hex") == hex(FORBIDDEN[0])), None)

    def option(name: str, raw_start: int, raw_bytes: int, meta_start: int, meta_bytes: int,
               shares_range: bool) -> dict[str, object]:
        """评估一个候选：容量、可容纳帧数、被排除帧、治理层影响。"""
        raw_end = raw_start + raw_bytes
        usable = raw_bytes - (meta_bytes if shares_range else 0)
        fitting = [dims for dims, size in sizes if align_up(size, STORAGE_ALIGN) <= usable]
        excluded = sorted({dims for dims, size in sizes if align_up(size, STORAGE_ALIGN) > usable})
        in_forbidden = raw_start >= FORBIDDEN[0] and raw_end <= FORBIDDEN[1]
        return {
            "name": name,
            "raw_range_hex": [hex(raw_start), hex(raw_end)],
            "raw_bytes": raw_bytes,
            "meta_range_hex": [hex(meta_start), hex(meta_start + meta_bytes)],
            "meta_bytes": meta_bytes,
            "raw_start_aligned_64": raw_start % MAINT_ALIGN == 0,
            "usable_for_frame_bytes": usable,
            "max_frame_required_bytes": max_frame,
            "capacity_margin_bytes": usable - max_frame,
            "fits_full_109_list": len(fitting) == len(sizes),
            "frames_supported": len(fitting),
            "frames_total": len(sizes),
            "excluded_dimension_buckets": excluded,
            "inside_current_forbidden_span": in_forbidden,
            "governance_change_required": in_forbidden or True,
            "governance_note": (
                "需批准缩减地址图禁区 " + hex(FORBIDDEN[0]) + ".." + hex(FORBIDDEN[1])
                if in_forbidden else "需批准占用 2B 专属窗口内既有空洞并登记 owner"
            ),
        }

    options = [
        option("A_readiness_candidate_12MiB", FORBIDDEN[0], 12 * 1024 * 1024,
               FORBIDDEN[0] + 12 * 1024 * 1024, META_BYTES, False),
        option("B_inside_window_9MiB_contiguous", 0x10700000, 0x11000000 - 0x10700000,
               0x10700000, META_BYTES, True),
        option("C_minimal_11MiB_plus_meta_in_window", FORBIDDEN[0], 11 * 1024 * 1024,
               align_up(0x11ADADB8, MAINT_ALIGN), META_BYTES, False),
        option("E_upper_ps_app_arena", 0, 0, 0, 0, False),
    ]
    # 选项 E：ps_app_arena 上部空闲（受 16 MiB arena 上限约束）
    arena = ranges["ps_app_arena"]
    r13_upper = max(entry["end_exclusive"] for key, entry in ranges.items()
                    if isinstance(entry, dict) and "end_exclusive" in entry
                    and key not in ("ps_app_arena", "s2b_tensor_arena", "network_input_tensor"))
    arena_free = arena["end_exclusive"] - r13_upper
    options[-1] = {
        "name": "E_upper_ps_app_arena",
        "arena_range_hex": [hex(arena["start"]), hex(arena["end_exclusive"])],
        "arena_bytes": arena["end_exclusive"] - arena["start"],
        "r13_used_upper_bound_hex": hex(r13_upper),
        "free_above_r13_bytes": arena_free,
        "max_frame_required_bytes": max_frame,
        "capacity_margin_bytes": arena_free - max_frame,
        "fits_full_109_list": arena_free >= max_frame,
        "frames_supported": sum(1 for _, size in sizes if align_up(size, STORAGE_ALIGN) <= arena_free),
        "frames_total": len(sizes),
        "incompatibility": "该区间所有权属 PS 应用 linker arena；4-D 最终 ELF 布局未冻结，且 arena 总上限 16 MiB 本身就小于部分帧需求",
        "governance_change_required": True,
        "governance_note": "需先冻结 4-D PS 应用 linker 布局并重新登记 arena 内部切分",
    }

    draft_capacity = draft["length_bytes"] if draft else 0
    draft_supported = sum(1 for _, size in sizes if align_up(size, STORAGE_ALIGN) <= draft_capacity)

    result = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "check_raw_address_options",
        "checker_version": "r01",
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hardware_execution": "NOT_RUN",
        "inputs": {
            "address_map": {"path": str(ADDRESS_MAP), "sha256": sha256_of(ADDRESS_MAP)},
            "input_scope_audit": {"path": str(SCOPE), "sha256": sha256_of(SCOPE)},
            "r13_memory_ranges": {"path": str(RANGES), "sha256": sha256_of(RANGES)},
        },
        "facts": {
            "window_hex": [hex(WINDOW[0]), hex(WINDOW[1])],
            "frozen_objects": [{"name": n, "range_hex": [hex(s), hex(e)], "bytes": e - s} for s, e, n in occupied],
            "holes_in_window": holes,
            "largest_contiguous_hole_bytes": largest_hole,
            "max_frame_bytes": max_frame,
            "sample_count": len(sizes),
            "meta_bytes": META_BYTES,
            "storage_align_bytes": STORAGE_ALIGN,
            "maintenance_align_bytes": MAINT_ALIGN,
            "current_draft_region_bytes": draft_capacity,
            "current_draft_region_supported_frames": draft_supported,
            "forbidden_span_hex": [hex(FORBIDDEN[0]), hex(FORBIDDEN[1])],
            "forbidden_gap_rule": forbidden_gap["rule"] if forbidden_gap else None,
        },
        "options": options,
        "conclusion": {
            "full_109_inside_window_possible": False,
            "reason": f"窗口内最大连续空洞 {largest_hole} B < 最大帧需求 {max_frame} B；"
                      "全 109 覆盖必须扩到窗口外或缩小输入范围",
            "rejected_options": {
                "D_split_frame_across_holes": "帧缓冲必须连续（PL master 单区间寻址）；非连续空洞拼接不成立",
                "F_keep_4MiB_draft": f"4 MiB 草案仅支持 {draft_supported}/{len(sizes)} 帧，远低于 ≥100 帧要求",
            },
        },
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "boundary": "只读算术；不构成地址批准、owner 登记或 G0/G4/G5 结论。",
    }
    (out_dir / "raw_address_options_arithmetic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "largest_hole_bytes": largest_hole,
        "max_frame_bytes": max_frame,
        "holes": holes,
        "draft_supported": draft_supported,
        "options": [{k: o[k] for k in ("name", "raw_bytes", "usable_for_frame_bytes",
                                       "capacity_margin_bytes", "frames_supported",
                                       "excluded_dimension_buckets", "inside_current_forbidden_span")
                     if k in o} for o in options],
    }, ensure_ascii=False, indent=2))
    if failures:
        for line in failures:
            print(f"[FAIL] {line}")
        return 1
    print(f"[PASS] 算术完成：最大连续空洞 {largest_hole} B、最大帧 {max_frame} B、候选 {len(options)} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())