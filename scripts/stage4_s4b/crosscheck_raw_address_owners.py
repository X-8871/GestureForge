#!/usr/bin/env python3
"""RAW/META 候选区交叉核对取证（G-01 条件①，只读）。

对候选 `[0x12000000,0x12C08000)`（选项 A：RAW 12 MiB + META 32 KiB）核对其与
2B 冻结对象、阶段5 送显缓冲（w5 已提交运行清单记录的实际地址）、阶段3 视频缓冲
事实来源的不相交性。

纪律：
  - 只从**已提交文件**取事实并现场复算其 SHA-256；不猜地址。
  - 阶段3 未发布静态地址事实时，如实标记 `STAGE3_STATIC_ADDRESS_FACT_MISSING`，
    **不得**据此判定条件①已满足。

退出码：0 = 全部可得事实不相交（缺失事实另行标记）；1 = 发现实际重叠；2 = 输入错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
CN = timezone(timedelta(hours=8))

ADDRESS_MAP = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
W2B_PLATFORM = Path("D:/FPGA_Competition/w2b/board/s2b_inference_platform.json")
W5_OVERLAY = Path("D:/codex-worktrees/w5/report/evidence/S5-T01/s5t01_board_overlay_20261022_r01/run_manifest.json")
W5_DOWNLOAD = Path("D:/codex-worktrees/w5/report/evidence/S5-T01/s5t01_board_download_20261022_r01/run_manifest.json")
DBDF_APP_PATCH = Path("D:/codex-worktrees/dbdf/board/stage3/software/sensor/s3_t04_app_diag_v12.patch")
DBDF_README = Path("D:/codex-worktrees/dbdf/board/stage3/README.md")

CANDIDATE = (0x12000000, 0x12C08000)  # RAW 12 MiB + META 32 KiB（选项 A）


def sha256_of(path: Path) -> str:
    """按 1 MiB 分块计算 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    """半开区间是否相交。"""
    return max(a0, b0) < min(a1, b1)


def main() -> int:
    """执行交叉核对。"""
    parser = argparse.ArgumentParser(description="RAW/META 候选区交叉核对")
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    for path in (ADDRESS_MAP, W2B_PLATFORM, W5_OVERLAY, W5_DOWNLOAD, DBDF_APP_PATCH, DBDF_README):
        if not path.is_file():
            print(f"[FAIL] 缺少事实来源：{path}")
            return 2
    out_dir = Path(args.evidence_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"[FAIL] 证据目录非空，RunId 可能被复用：{out_dir}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    address_map = json.loads(ADDRESS_MAP.read_text(encoding="utf-8"))
    platform2b = json.loads(W2B_PLATFORM.read_text(encoding="utf-8"))
    overlay = json.loads(W5_OVERLAY.read_text(encoding="utf-8"))
    download = json.loads(W5_DOWNLOAD.read_text(encoding="utf-8"))
    patch_text = DBDF_APP_PATCH.read_text(encoding="utf-8", errors="replace")
    readme_text = DBDF_README.read_text(encoding="utf-8", errors="replace")

    failures: list[str] = []
    checks: dict[str, dict[str, object]] = {}

    # 阶段5 事实：三个送显缓冲 + 每帧字节数（来自其已提交运行清单）
    markers = overlay["board_evidence"]["uart_markers"]
    bufs = [int(markers["buf0"], 16), int(markers["buf1"], 16), int(markers["buf2"], 16)]
    v_size = int(overlay["board_evidence"]["mm2s"]["frame_size"].split(",")[0].split("=")[1].split("(")[0], 16)
    h_size = int(overlay["board_evidence"]["mm2s"]["frame_size"].split(",")[1].split("=")[1].split("(")[0], 16)
    frame_bytes = v_size * h_size
    w5_buffers = [{"name": f"w5_display_buf{i}", "start": start, "end_exclusive": start + frame_bytes,
                   "start_hex": hex(start), "end_hex": hex(start + frame_bytes)} for i, start in enumerate(bufs)]
    addr_s2mm = int(download["vdma_readback"]["ADDR_S2MM"], 16)

    checks["w5_addr_s2mm_equals_buf0"] = {
        "status": "PASS" if addr_s2mm == bufs[0] else "FAIL",
        "s2mm_hex": hex(addr_s2mm), "buf0_hex": hex(bufs[0]),
        "note": "阶段5 清单记录的 VDMA 写地址与送显 buf0 相同（采集与显示共用当前帧缓冲，与阶段3 README 的未决项一致）",
    }
    if addr_s2mm != bufs[0]:
        failures.append("w5 清单内部不一致：ADDR_S2MM != buf0")

    # 核对 1/2：2B 冻结对象与 2B 专属窗口
    arena = (int(platform2b["memory"]["arena_base"], 16), int(platform2b["memory"]["arena_end_exclusive"], 16))
    two_b = [{"name": r["name"], "start": r["base_addr"], "end_exclusive": r["end_addr_exclusive"]}
             for r in address_map["regions"] if r["kind"] == "ddr"]
    two_b_conflicts = [r["name"] for r in two_b
                       if overlaps(CANDIDATE[0], CANDIDATE[1], r["start"], r["end_exclusive"])]
    inside_arena = CANDIDATE[0] >= arena[0] and CANDIDATE[1] <= arena[1]
    checks["candidate_vs_2b_objects"] = {
        "status": "PASS" if not two_b_conflicts else "FAIL",
        "conflicts": two_b_conflicts, "2b_objects": two_b,
    }
    checks["candidate_vs_2b_arena"] = {
        "status": "PASS" if CANDIDATE[0] >= arena[1] and not inside_arena else "FAIL",
        "arena_hex": [hex(arena[0]), hex(arena[1])], "candidate_starts_at_or_above_arena_end": CANDIDATE[0] >= arena[1],
        "note": "候选整体位于 2B 专属窗口之外（其起点即窗口末端），与 2B 全部对象不相交",
    }
    if two_b_conflicts or inside_arena:
        failures.append(f"候选与 2B 对象冲突：{two_b_conflicts} / inside_arena={inside_arena}")

    # 核对 3：阶段5 送显缓冲
    w5_conflicts = [b["name"] for b in w5_buffers
                    if overlaps(CANDIDATE[0], CANDIDATE[1], b["start"], b["end_exclusive"])]
    checks["candidate_vs_w5_display_buffers"] = {
        "status": "PASS" if not w5_conflicts else "FAIL",
        "conflicts": w5_conflicts, "w5_buffers": w5_buffers, "frame_bytes": frame_bytes,
        "fact_source": str(W5_OVERLAY),
    }
    if w5_conflicts:
        failures.append(f"候选与阶段5 送显缓冲冲突：{w5_conflicts}")

    # 阶段3 事实：代码级 pointer-array + 每帧长度；静态地址表缺失
    code_fact_tokens = {
        "pointer_array": "dispCtrl.framePtr[curFrame]" in patch_text,
        "frame_len_token": "0x2A3000" in patch_text,
        "readme_buffer_ownership_unresolved": "采集与显示可能使用同一当前帧缓冲" in readme_text,
    }
    stage3_static_available = False  # 阶段3 未发布静态地址表（见下 missing_facts）
    stage3_observed_max = max(b["end_exclusive"] for b in w5_buffers)
    checks["stage3_video_buffer_fact"] = {
        "status": "PARTIAL_FACT_ONLY",
        "code_level_fact": code_fact_tokens,
        "code_fact_source": str(DBDF_APP_PATCH),
        "static_address_table_available": stage3_static_available,
        "observed_upper_bound_hex": hex(stage3_observed_max),
        "observed_source": str(W5_OVERLAY),
        "disjoint_from_candidate_on_observed_facts": CANDIDATE[0] > stage3_observed_max,
        "note": "阶段3 自身文档给出的是运行时指针数组与每帧 0x2A3000（720×3840），未发布静态地址表；"
                "实际地址事实仅见于阶段5 已提交运行清单。观测事实与候选不相交，但不足以替代阶段3 的书面静态事实。",
    }
    if not (CANDIDATE[0] > stage3_observed_max):
        failures.append("候选与阶段3 观测到的视频缓冲上界相交")

    # 核对 4（信息性）：BSP 软件窗口与现行禁区
    bsp_window = (0x00100000, 0x40000000)
    forbidden = next((g for g in address_map["gaps"] if g.get("base_addr_hex") == "0x12000000"), None)
    checks["informational"] = {
        "candidate_inside_bsp_software_window": CANDIDATE[0] >= bsp_window[0] and CANDIDATE[1] <= bsp_window[1],
        "candidate_currently_inside_forbidden_gap": bool(forbidden) and forbidden["base_addr_hex"] == "0x12000000",
        "forbidden_rule": forbidden["rule"] if forbidden else None,
        "forbidden_has_sources": "sources" in (forbidden or {}),
    }

    missing_facts = []
    if not stage3_static_available:
        missing_facts.append({
            "stage": "3",
            "item": "视频缓冲（VDMA/framebuffer）静态地址事实",
            "why": "dbdf 自身文档/证据未发布静态地址表；仅有代码级 dispCtrl.framePtr[curFrame] 与每帧 0x2A3000，"
                   "以及阶段5 清单记录的实际地址。",
            "request": "请阶段3 写入方在其正式文档中确认三缓冲地址集合（或发布地址图），供条件①闭合。",
        })

    condition1 = "INCOMPLETE_PENDING_STAGE3_WRITTEN_FACT" if missing_facts else "SATISFIED_BY_BOUND_FACTS"
    result = {
        "task_id": "S4-CTRL/S4-T21",
        "checker": "crosscheck_raw_address_owners",
        "checker_version": "r01",
        "status": "PASS" if not failures else "FAIL",
        "generated_at_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": " ".join([sys.executable, *sys.argv]),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hardware_execution": "NOT_RUN",
        "candidate_hex": [hex(CANDIDATE[0]), hex(CANDIDATE[1])],
        "condition_1_status": condition1,
        "basis_facts": [
            {"id": "w4_address_map", "path": str(ADDRESS_MAP), "sha256": sha256_of(ADDRESS_MAP)},
            {"id": "w2b_platform", "path": str(W2B_PLATFORM), "sha256": sha256_of(W2B_PLATFORM)},
            {"id": "w5_overlay_manifest", "path": str(W5_OVERLAY), "sha256": sha256_of(W5_OVERLAY)},
            {"id": "w5_download_manifest", "path": str(W5_DOWNLOAD), "sha256": sha256_of(W5_DOWNLOAD)},
            {"id": "dbdf_stage3_app_patch_v12", "path": str(DBDF_APP_PATCH), "sha256": sha256_of(DBDF_APP_PATCH)},
            {"id": "dbdf_stage3_readme", "path": str(DBDF_README), "sha256": sha256_of(DBDF_README)},
        ],
        "checks": checks,
        "missing_facts": missing_facts,
        "failures": failures,
        "boundary": [
            "只读取证；不构成地址批准、owner 登记或 G0/G4/G5 结论。",
            "条件①在缺失事实补齐前不得判为满足；未实施任何地址图/契约改动。",
            "本轮全离线：未装载位流、未打开 COM4/JTAG、未起 hw_server。",
        ],
    }
    (out_dir / "raw_address_owner_crosscheck.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for key, entry in checks.items():
        print(f"[{entry.get('status', 'INFO')}] {key}")
    for line in failures:
        print(f"[FAIL] {line}")
    for item in missing_facts:
        print(f"[MISSING] 阶段{item['stage']}：{item['item']}")
    print(f"[{result['status']}] 条件① = {condition1}；候选 {hex(CANDIDATE[0])}..{hex(CANDIDATE[1])}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())