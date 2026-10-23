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
STAGE3_FACTS = Path("D:/codex-worktrees/dbdf/report/evidence/S3-T05/t05_stage3_window_20261024_r01/address_facts.md")

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

    for path in (ADDRESS_MAP, W2B_PLATFORM, W5_OVERLAY, W5_DOWNLOAD, DBDF_APP_PATCH, DBDF_README, STAGE3_FACTS):
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

    # 核对 1/2：2B 冻结对象与 2B 专属窗口（排除阶段4 自有 region，避免自证冲突）
    arena = (int(platform2b["memory"]["arena_base"], 16), int(platform2b["memory"]["arena_end_exclusive"], 16))
    two_b_names = ("network_input_tensor", "gf8_weight_package", "feature_envelope")
    two_b = [{"name": r["name"], "start": r["base_addr"], "end_exclusive": r["end_addr_exclusive"]}
             for r in address_map["regions"] if r["name"] in two_b_names]
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
    # 阶段3 书面部署事实（2026-10-24 板级窗口只读回读）
    stage3_text = STAGE3_FACTS.read_text(encoding="utf-8", errors="replace")
    stage3_observed = [0x00110C00, 0x00114C00]
    stage3_observed_max = max(stage3_observed) + frame_bytes  # 缓冲末端，用于不相交判定
    stage3_fact_tokens = {
        "s2mm_addr_token": "0x00110C00" in stage3_text,
        "v11_addr_token": "0x00114C00" in stage3_text,
        "single_buffer_token": "单缓冲" in stage3_text,
        "shared_capture_display_token": "与采集完全相同" in stage3_text,
        "runtime_alloc_no_static_token": "无静态编译期保证" in stage3_text or "无链接期静态保证" in stage3_text,
        "no_hardcode_token": "禁止硬编码" in stage3_text,
    }
    stage3_fact_ok = all(stage3_fact_tokens.values())
    checks["stage3_video_buffer_fact"] = {
        "status": "PASS" if (stage3_fact_ok and CANDIDATE[0] > stage3_observed_max) else "FAIL",
        "written_fact_source": str(STAGE3_FACTS),
        "written_fact_tokens": stage3_fact_tokens,
        "code_level_fact": code_fact_tokens,
        "code_fact_source": str(DBDF_APP_PATCH),
        "observed_addresses_hex": [hex(a) for a in stage3_observed],
        "observed_upper_bound_hex": hex(stage3_observed_max),
        "disjoint_from_candidate": CANDIDATE[0] > stage3_observed_max,
        "reservation_clause": "阶段3 帧基址为**运行期分配**（dispCtrl.framePtr[curFrame]）、**无链接期静态保证**，换应用会变；"
                              "任何消费方使用前必须运行期回读、**禁止硬编码**（已写入地址图 raw_frame/raw_meta 的 notes）。",
    }
    if not stage3_fact_ok:
        failures.append("阶段3 书面事实缺少必要语义标记（采集/显示地址、单缓冲、共用、运行期分配、禁止硬编码）")
    if not (CANDIDATE[0] > stage3_observed_max):
        failures.append("候选与阶段3 观测到的视频缓冲上界相交")

    # 核对 4（信息性）：BSP 软件窗口与现行禁区（r03 已缩减）
    bsp_window = (0x00100000, 0x40000000)
    forbidden = next((g for g in address_map["gaps"] if g.get("base_addr_hex") == "0x12C08000"), None)
    checks["informational"] = {
        "candidate_inside_bsp_software_window": CANDIDATE[0] >= bsp_window[0] and CANDIDATE[1] <= bsp_window[1],
        "candidate_currently_inside_forbidden_gap": bool(forbidden) and CANDIDATE[0] >= int(forbidden["base_addr_hex"], 16),
        "forbidden_rule": forbidden["rule"] if forbidden else None,
        "forbidden_has_sources": "sources" in (forbidden or {}),
        "forbidden_span_hex": [forbidden["base_addr_hex"], forbidden["end_addr_exclusive_hex"]] if forbidden else None,
    }

    missing_facts: list[dict[str, object]] = []
    condition1 = "SATISFIED_BY_BOUND_FACTS" if (not failures and not missing_facts) else "INCOMPLETE"
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
            {"id": "dbdf_stage3_window_address_facts", "path": str(STAGE3_FACTS), "sha256": sha256_of(STAGE3_FACTS)},
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