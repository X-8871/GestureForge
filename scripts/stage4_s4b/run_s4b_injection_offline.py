#!/usr/bin/env python3
"""阶段4 单帧注入通路的离线驱动（4-B）：构建 → 地址图核对 → 单帧全流程 → 小图边界 →
有限序列/背压 → 故障序列 → 证据 JSON。

不接板卡、不碰 JTAG/COM4/串口；只用 gcc 与主机 mock（`s4_inject_frame_host.c`）。
退出码：0 = 全部按预期；1 = 有用例与预期不符；2 = 输入/环境错误。

用法：
  python -B scripts/stage4_s4b/run_s4b_injection_offline.py \
      --run-id s4b_injection_20261022_r01 [--evidence-dir report/evidence/S4-B/<run_id>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
GCC = Path(r"d:\mingw64\bin\gcc.exe")
MAP_PATH = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
SRC = [WORKTREE / "vitis/stage4/s4_inject_frame.c", WORKTREE / "vitis/stage4/s4_inject_frame_host.c"]
INC = WORKTREE / "vitis/stage4"
CN = timezone(timedelta(hours=8))

FLAGS = ["-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow"]
CONTRACT_VERSION = "s4-shared-io/1.1.0"

# 期望退出码（= s4_inject_status 数值）
E_OK = 0
E_CONTRACT = 2
E_SOURCE = 3
E_FORMAT = 4
E_GEOMETRY = 5
E_STRIDE = 6
E_LENGTH = 7
E_REGION = 8
E_RANGE = 9
E_ALIGN = 10
E_OVERLAP = 11
E_NO_FREE = 12
E_NO_OVERWRITE = 13
E_DUP = 14
E_ORDER_FRAME = 15
E_EVENT_ORDER = 16
E_INTEGRITY = 17
E_TIMEOUT = 18
E_FORGED_CAPTURE = 19
E_SCOPE = 20


def now_utc8() -> str:
    """返回 UTC+8 的 ISO 8601 时间。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_of(path: Path) -> str:
    """计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lcg_payload(seed: int, length: int) -> bytes:
    """复现 host 的 pattern: 生成器（state=state*A+C, byte=(state>>33)&0xFF）。"""
    mask = (1 << 64) - 1
    state = seed
    out = bytearray(length)
    for index in range(length):
        state = (state * 6364136223846793005 + 1442695040888963407) & mask
        out[index] = (state >> 33) & 0xFF
    return bytes(out)


def load_regions() -> tuple[list[dict], dict]:
    """读取地址图顶层 region 与其 address_space。"""
    if not MAP_PATH.is_file():
        print(f"[FAIL] 地址图不存在：{MAP_PATH}")
        sys.exit(2)
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return data["regions"], data


def check_address_map(regions: list[dict], data: dict) -> dict:
    """核对地址图：区间自洽 + 两两不相交 + 负例（人为重叠必须被检出）。"""
    problems: list[str] = []
    for region in regions:
        if region["end_addr_exclusive"] - region["base_addr"] != region["length_bytes"]:
            problems.append(f"{region['name']}: end-base != length_bytes")
        for space in data["address_space"]["spaces"]:
            if space["name"] == region.get("kind"):
                if not (space["base_addr"] <= region["base_addr"] and region["end_addr_exclusive"] <= space["end_addr_exclusive"]):
                    problems.append(f"{region['name']}: 越出 address_space {space['name']}")
                break
    pairs = 0
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            pairs += 1
            start = max(a["base_addr"], b["base_addr"])
            end = min(a["end_addr_exclusive"], b["end_addr_exclusive"])
            if start < end:
                problems.append(f"重叠：{a['name']} 与 {b['name']} -> [{start:#x},{end:#x})")
    # 负例：把 injection_frame_rgb 移到 gf8 区间内，必须被同一算法判定为重叠
    negative_detected = False
    gf8 = next((r for r in regions if r["name"] == "gf8_weight_package"), None)
    inj = next((r for r in regions if r["name"] == "injection_frame_rgb"), None)
    if gf8 and inj:
        mutated = dict(inj)
        mutated["base_addr"] = gf8["base_addr"]
        start = max(gf8["base_addr"], mutated["base_addr"])
        end = min(gf8["end_addr_exclusive"], mutated["base_addr"] + mutated["length_bytes"])
        negative_detected = start < end
    if not negative_detected:
        problems.append("负例未被检出（重叠检测算法可能失效）")
    return {
        "status": "PASS" if not problems else "FAIL",
        "pairs_checked": pairs,
        "problems": problems,
        "negative_control": {"mutation": "把 injection_frame_rgb.base_addr 改到 gf8_weight_package 起点", "detected": negative_detected},
    }


def build(build_dir: Path) -> dict:
    """严格旗标编译 host harness。"""
    build_dir.mkdir(parents=True, exist_ok=True)
    exe = build_dir / "s4_inject_host.exe"
    cmd = [str(GCC), *FLAGS, "-I", str(INC), *(str(s) for s in SRC), "-o", str(exe)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "exe": str(exe),
        "exe_sha256": sha256_of(exe) if exe.is_file() else None,
    }


def region_lines(regions: list[dict]) -> list[str]:
    """把地址图 region 转成 host op 脚本的 region 行。"""
    return [f"region name={r['name']} base={hex(r['base_addr'])} len={hex(r['length_bytes'])}" for r in regions]


def frame_line(**kwargs) -> str:
    """拼一条 frame op 行。"""
    order = ["id", "fmt", "w", "h", "stride", "len", "region", "base", "offset", "source",
             "capture", "capture_avail", "inject_ns", "clock", "freq", "wrap", "domain",
             "contract", "align", "algorithm", "digest", "payload", "payload_len",
             "scope_pl", "scope_uart", "scope_board"]
    return "frame " + " ".join(f"{key}={kwargs[key]}" for key in order if key in kwargs)


BASE_FRAME = {
    "fmt": "RGB888", "w": 4, "h": 4, "stride": 12, "region": "injection_frame_rgb",
    "source": "file_injection", "capture": "unavailable", "capture_avail": 0,
    "inject_ns": 12345, "clock": "XTime", "freq": 100000000, "wrap": "64bit",
    "domain": "PS", "contract": CONTRACT_VERSION,
    "scope_pl": "NOT_EXECUTED_OFFLINE", "scope_uart": "NOT_EXECUTED_OFFLINE",
    "scope_board": "NOT_EXECUTED_OFFLINE", "payload": "pattern:1",
}

FULL_SEQUENCE = [
    "bind",
    "advance slot=0 ev=producer_write_complete",
    "advance slot=0 ev=cache_flush_by_producer",
    "advance slot=0 ev=ownership_publish_to_consumer",
    "consume slot=0",
    "advance slot=0 ev=consumer_invalidate",
    "advance slot=0 ev=buffer_release_to_producer",
]


def run_case(exe: Path, work: Path, name: str, body: list[str], expected: int, regions: list[dict],
             base_addr: int) -> dict:
    """运行一个 op 脚本并核对退出码。"""
    script = work / f"{name}.op"
    script.write_text("\n".join([*region_lines(regions), *body, ""]), encoding="utf-8")
    proc = subprocess.run([str(exe), str(script)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    out_path = work / f"{name}.json"
    out_path.write_text(proc.stdout, encoding="utf-8")
    parsed = None
    try:
        parsed = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        parsed = None
    detail = {
        "case": name,
        "expected_exit": expected,
        "actual_exit": proc.returncode,
        "status_name": (parsed or {}).get("status_name"),
        "matched": proc.returncode == expected,
        "script": str(script),
        "json": str(out_path),
        "consumer": (parsed or {}).get("consumer"),
        "ring": (parsed or {}).get("ring"),
        "mock_cache": (parsed or {}).get("mock_cache"),
        "stderr": proc.stderr,
    }
    return detail


def main() -> int:
    """执行全部离线用例。"""
    parser = argparse.ArgumentParser(description="4-B 单帧注入离线驱动")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evidence-dir", default="")
    args = parser.parse_args()

    if not GCC.is_file():
        print(f"[FAIL] gcc 不存在：{GCC}")
        return 2
    regions, map_data = load_regions()
    inj_region = next(r for r in regions if r["name"] == "injection_frame_rgb")
    base_addr = inj_region["base_addr"]

    tmp_dir = WORKTREE / "tmp" / "4" / "S4-B" / args.run_id
    work = tmp_dir / "cases"
    work.mkdir(parents=True, exist_ok=True)
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
    if evidence_dir:
        evidence_dir.mkdir(parents=True, exist_ok=True)

    build_info = build(tmp_dir / "build")
    if build_info["exit_code"] != 0:
        print(f"[FAIL] 编译失败：{build_info['stderr'][:2000]}")
        return 1
    exe = Path(build_info["exe"])
    warnings = [line for line in (build_info["stderr"] or "").splitlines() if line.strip()]

    map_check = check_address_map(regions, map_data)
    results: list[dict] = []

    def frame(**over):
        merged = dict(BASE_FRAME)
        merged.update(over)
        merged.setdefault("base", hex(base_addr))
        return frame_line(**merged)

    # 1) 单帧全流程
    results.append(run_case(exe, work, "single_frame_full", ["ring slots=2", frame(id=1), *FULL_SEQUENCE], E_OK, regions, base_addr))
    # 2) 小图边界：1x1、3x2、奇数宽 5（RGB565 + stride 填充）
    results.append(run_case(exe, work, "small_1x1", ["ring slots=2", frame(id=2, w=1, h=1, stride=3), *FULL_SEQUENCE], E_OK, regions, base_addr))
    results.append(run_case(exe, work, "small_3x2", ["ring slots=2", frame(id=3, w=3, h=2, stride=9), *FULL_SEQUENCE], E_OK, regions, base_addr))
    results.append(run_case(exe, work, "odd_width_5_rgb565_padded",
                           ["ring slots=2", frame(id=4, fmt="RGB565", w=5, h=3, stride=16), *FULL_SEQUENCE],
                           E_OK, regions, base_addr))
    # 3) 有限序列/背压：2 槽，两帧在途，第 3 帧应 NO_FREE_BUFFER；释放后可复用
    results.append(run_case(exe, work, "queue_full_on_third_frame", [
        "ring slots=2",
        frame(id=10), "bind",
        frame(id=11), "bind",
        frame(id=12), "bind",
    ], E_NO_FREE, regions, base_addr))
    results.append(run_case(exe, work, "no_overwrite_held_slot", [
        "ring slots=2",
        frame(id=20), "bind",
        "advance slot=0 ev=producer_write_complete",
        frame(id=21), "bind slot=0",
    ], E_NO_OVERWRITE, regions, base_addr))
    results.append(run_case(exe, work, "release_then_reuse", [
        "ring slots=1",
        frame(id=30), *FULL_SEQUENCE,
        frame(id=31), *FULL_SEQUENCE,
    ], E_OK, regions, base_addr))
    # 4) 故障序列（每条只触发一个原因）
    results.append(run_case(exe, work, "fault_contract_version", ["ring slots=2", frame(id=40, contract="s4-shared-io/1.0.0"), "bind"], E_CONTRACT, regions, base_addr))
    results.append(run_case(exe, work, "fault_source_kind", ["ring slots=2", frame(id=41, source="bogus"), "bind"], E_SOURCE, regions, base_addr))
    results.append(run_case(exe, work, "fault_pixel_format", ["ring slots=2", frame(id=42, fmt="YUYV"), "bind"], E_FORMAT, regions, base_addr))
    results.append(run_case(exe, work, "fault_geometry_zero", ["ring slots=2", frame(id=43, w=0), "bind"], E_GEOMETRY, regions, base_addr))
    results.append(run_case(exe, work, "fault_stride_too_small", ["ring slots=2", frame(id=44, stride=8), "bind"], E_STRIDE, regions, base_addr))
    results.append(run_case(exe, work, "fault_length_mismatch", ["ring slots=2", frame(id=45, len=47), "bind"], E_LENGTH, regions, base_addr))
    results.append(run_case(exe, work, "fault_unknown_region", ["ring slots=2", frame(id=46, region="no_such_region"), "bind"], E_REGION, regions, base_addr))
    results.append(run_case(exe, work, "fault_out_of_range", ["ring slots=2", frame(id=47, offset=hex(inj_region["length_bytes"] - 16)), "bind"], E_RANGE, regions, base_addr))
    results.append(run_case(exe, work, "fault_alignment", ["ring slots=2", frame(id=48, offset=8), "bind"], E_ALIGN, regions, base_addr))
    results.append(run_case(exe, work, "fault_integrity_wrong_digest", ["ring slots=2", frame(id=49, algorithm="crc32_ieee", digest="wrong"), "bind"], E_INTEGRITY, regions, base_addr))
    results.append(run_case(exe, work, "fault_forged_capture_time", ["ring slots=4", frame(id=50, capture=987654321, capture_avail=0), "bind"], E_FORGED_CAPTURE, regions, base_addr))
    results.append(run_case(exe, work, "fault_measurement_scope", ["ring slots=4", frame(id=51, capture_avail=1), "bind"], E_SCOPE, regions, base_addr))
    results.append(run_case(exe, work, "fault_duplicate_frame", [
        "ring slots=2", frame(id=60), "bind",
        "advance slot=0 ev=producer_write_complete",
        "advance slot=0 ev=cache_flush_by_producer",
        "advance slot=0 ev=ownership_publish_to_consumer",
        frame(id=60), "bind",
    ], E_DUP, regions, base_addr))
    results.append(run_case(exe, work, "fault_out_of_order_frame", ["ring slots=2", frame(id=70), *FULL_SEQUENCE, frame(id=69), *FULL_SEQUENCE], E_ORDER_FRAME, regions, base_addr))
    results.append(run_case(exe, work, "fault_event_order", ["ring slots=2", frame(id=80), "bind", "advance slot=0 ev=cache_flush_by_producer"], E_EVENT_ORDER, regions, base_addr))
    results.append(run_case(exe, work, "fault_consumer_timeout", [
        "ring slots=2", frame(id=90), "bind",
        "advance slot=0 ev=producer_write_complete",
        "advance slot=0 ev=cache_flush_by_producer",
        "advance slot=0 ev=ownership_publish_to_consumer",
        "timeout slot=0",
    ], E_TIMEOUT, regions, base_addr))

    # 5) 小图完整性：独立复现 payload 并核对 consumer CRC 与字节数
    small_image_checks: list[dict] = []
    for case_name, seed, width, height, stride, bpp in (
        ("small_1x1", 1, 1, 1, 3, 3),
        ("small_3x2", 1, 3, 2, 9, 3),
    ):
        payload = lcg_payload(seed, stride * height)
        expected_crc = zlib.crc32(payload) & 0xFFFFFFFF
        matched_case = next(r for r in results if r["case"] == case_name)
        consumer = matched_case.get("consumer") or {}
        small_image_checks.append({
            "case": case_name,
            "width": width,
            "height": height,
            "stride_bytes": stride,
            "payload_bytes": len(payload),
            "expected_crc32": expected_crc,
            "actual_crc32": consumer.get("last_crc32"),
            "actual_valid_bytes": consumer.get("valid_bytes"),
            "crc_match": consumer.get("last_crc32") == expected_crc,
            "bytes_match": consumer.get("valid_bytes") == len(payload),
        })

    failures = [r for r in results if not r["matched"]]
    small_failures = [c for c in small_image_checks if not c["crc_match"] or not c["bytes_match"]]
    status = "PASS" if not failures and not small_failures and map_check["status"] == "PASS" and not warnings else "FAIL"

    summary = {
        "task_id": "S4-B",
        "run_id": args.run_id,
        "driver": "run_s4b_injection_offline",
        "generated_at_utc8": now_utc8(),
        "command": " ".join([sys.executable, *sys.argv]),
        "contract_version": CONTRACT_VERSION,
        "address_map": {"path": str(MAP_PATH), "sha256": sha256_of(MAP_PATH), "check": map_check},
        "build": build_info,
        "build_warning_lines": warnings,
        "cases": results,
        "case_failures": [r["case"] for r in failures],
        "small_image_checks": small_image_checks,
        "small_image_failures": [c["case"] for c in small_failures],
        "counts": {"cases": len(results), "matched": len(results) - len(failures), "failed": len(failures)},
        "status": status,
        "limits": [
            "仅主机 mock DDR/cache 与 gcc；未接板卡、未接真实串口、未跑 PL。",
            "NOT_RUN：板上注入（4-D）、真实 UART、摄像头、PL 推理时间/期限/吞吐、109 全量（S4-C）。",
            "注入模式下 capture_time_ns 不可用；本驱动不接受任何伪造采集时间。",
        ],
    }
    if evidence_dir:
        (evidence_dir / "injection_offline_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[INFO] 证据：{evidence_dir / 'injection_offline_summary.json'}")

    for case in results:
        mark = "OK " if case["matched"] else "BAD"
        print(f"{mark} {case['case']}: exit={case['actual_exit']} expected={case['expected_exit']} status={case['status_name']}")
    for check in small_image_checks:
        print(f"{'OK ' if check['crc_match'] and check['bytes_match'] else 'BAD'} {check['case']}: crc={check['actual_crc32']} expected={check['expected_crc32']} valid={check['actual_valid_bytes']}")
    print(f"[{status}] 用例 {len(results)}（失败 {len(failures)}）、小图 {len(small_image_checks)}（失败 {len(small_failures)}）、地址图 {map_check['status']}、编译告警行 {len(warnings)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())