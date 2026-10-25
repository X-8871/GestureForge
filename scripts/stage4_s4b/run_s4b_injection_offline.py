#!/usr/bin/env python3
"""阶段4 单帧注入通路的离线驱动（4-B）：构建 → 地址图核对 → 单帧全流程 → 小图边界 →
有限序列/背压 → 故障序列 → 证据 JSON。

不接板卡、不碰 JTAG/COM4/串口；只用 gcc 与主机 mock（`s4_inject_frame_host.c`）。
退出码：0 = 全部按预期；1 = 有用例与预期不符；2 = 输入/环境错误。

用法：
  python -B scripts/stage4_s4b/run_s4b_injection_offline.py \
      --run-id s4b_injection_20261023_r02 [--evidence-dir report/evidence/S4-B/<run_id>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
GCC = Path(r"d:\mingw64\bin\gcc.exe")
MAP_PATH = WORKTREE / "docs" / "stage4" / "S4B_stage4_address_map.json"
SRC = [WORKTREE / "vitis/stage4/s4_inject_frame.c", WORKTREE / "vitis/stage4/s4_inject_frame_host.c"]
API_TEST_SRC = WORKTREE / "verification/test_s4_inject_frame_api.c"
INC = WORKTREE / "vitis/stage4"
CN = timezone(timedelta(hours=8))

FLAGS = ["-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow"]
LEGACY_C_API_CONTRACT_VERSION = "s4-shared-io/1.1.0"

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
E_FLUSH_COVERAGE = 22
E_CACHE_BARRIER = 24
E_CACHE_VISIBILITY = 25
E_CLI = 26

STATUS_NAMES = {
    E_OK: "OK", E_CONTRACT: "ERR_CONTRACT_VERSION", E_SOURCE: "ERR_SOURCE_KIND",
    E_FORMAT: "ERR_PIXEL_FORMAT", E_GEOMETRY: "ERR_GEOMETRY", E_STRIDE: "ERR_STRIDE",
    E_LENGTH: "ERR_LENGTH", E_REGION: "ERR_REGION_UNKNOWN", E_RANGE: "ERR_BUFFER_RANGE",
    E_ALIGN: "ERR_ALIGNMENT", E_OVERLAP: "ERR_BUFFER_OVERLAP", E_NO_FREE: "ERR_NO_FREE_BUFFER",
    E_NO_OVERWRITE: "ERR_NO_OVERWRITE", E_DUP: "ERR_DUPLICATE_FRAME", E_ORDER_FRAME: "ERR_OUT_OF_ORDER",
    E_EVENT_ORDER: "ERR_EVENT_ORDER", E_INTEGRITY: "ERR_INTEGRITY", E_TIMEOUT: "ERR_CONSUMER_TIMEOUT",
    E_FORGED_CAPTURE: "ERR_CAPTURE_TIME_FORGED", E_SCOPE: "ERR_MEASUREMENT_SCOPE",
    E_CACHE_BARRIER: "ERR_CACHE_BARRIER", E_CACHE_VISIBILITY: "ERR_CACHE_VISIBILITY",
    E_CLI: "ERR_CLI_ARGUMENT", E_FLUSH_COVERAGE: "ERR_FLUSH_COVERAGE",
}

CASE_FIELDS = {
    "single_frame_full": ("", "OK"), "small_1x1": ("", "OK"), "small_3x2": ("", "OK"),
    "odd_width_5_rgb565_padded": ("", "OK"), "queue_full_on_third_frame": ("slots", "队列满"),
    "no_overwrite_held_slot": ("slot", "仍被持有"), "release_then_reuse": ("", "OK"),
    "fault_contract_version": ("contract_version", "与契约不一致"),
    "fault_source_kind": ("source", "不在契约词表"), "fault_pixel_format": ("pixel_format", "pixel_format"),
    "fault_geometry_zero": ("width/height", "geometry 宽高"), "fault_stride_too_small": ("stride_bytes", "小于该格式"),
    "fault_length_mismatch": ("buffer.length_bytes", "不等于 stride*height*planes"),
    "fault_unknown_region": ("buffer.region_name", "不在地址图内"), "fault_out_of_range": ("buffer", "超出所属 region"),
    "fault_alignment": ("buffer.offset_bytes", "未按 alignment 对齐"), "fault_integrity_wrong_digest": ("frame_integrity.value", "CRC32 与声明不一致"),
    "fault_forged_capture_time": ("capture_time_ns", "capture_time_ns 必须为 0 哨兵"),
    "fault_measurement_scope": ("measurement_scope.source_kind", "映射不一致"),
    "fault_duplicate_frame": ("frame_id", "已接纳且仍占有槽位"), "fault_out_of_order_frame": ("frame_id", "递增"),
    "fault_event_order": ("event", "事件顺序与契约"), "fault_consumer_timeout": ("consumer_done", "FAILED 槽仍占有帧"),
    "fault_overlap_before_write": ("buffer", "写入前拒绝"),
    "fault_accept_10_then_9": ("frame_id", "严格递增"),
    "fault_release_out_of_order": ("frame_id", "递增 frame_id 顺序"),
    "fault_abort_before_stop_confirmation": ("consumer_stopped_confirmed", "不得释放"),
    "fault_skip_flush": ("cache_flush_by_producer", "仍有脏 cache 行"),
    "fault_skip_invalidate": ("consumer_invalidate", "消费者视图无效"),
    "fault_shift_invalidate": ("consumer_invalidate", "消费者视图无效"),
    "fault_skip_barrier": ("cache.flush_barrier", "DSB/barrier 失败"),
    "valid_synthetic_source": ("", "OK"), "valid_camera_source": ("", "OK"),
    "fault_synthetic_capture_available": ("capture_time_ns", "synthetic 模式"),
    "fault_camera_capture_missing": ("capture_time_ns", "camera 模式要求"),
    "fault_capture_trailing_junk": ("capture", "完整、非负"),
    "fault_capture_empty": ("capture", "完整、非负"),
    "fault_capture_negative": ("capture", "完整、非负"),
    "fault_capture_overflow": ("capture", "完整、非负"),
    "fault_u32_width_overflow": ("width", "字段位宽"),
    "fault_u32_frame_overflow": ("frame_id", "字段位宽"),
    "fault_slot_overflow": ("slot", "uint32 表示范围"),
}


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
    proc, stdout, stderr = _run_utf8(cmd)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "exe": str(exe),
        "exe_sha256": sha256_of(exe) if exe.is_file() else None,
    }


def build_api_test(build_dir: Path) -> dict:
    """严格编译独立 C API 反例程序。"""
    build_dir.mkdir(parents=True, exist_ok=True)
    exe = build_dir / "s4_inject_api_test.exe"
    cmd = [str(GCC), *FLAGS, "-I", str(INC), str(SRC[0]), str(API_TEST_SRC), "-o", str(exe)]
    proc, stdout, stderr = _run_utf8(cmd)
    checks: list[dict] = []
    summary = None
    if proc.returncode == 0:
        test_proc, test_out, test_err = _run_utf8([str(exe)])
        stdout += test_out
        stderr += test_err
        try:
            parsed_lines = [json.loads(line) for line in test_out.splitlines() if line.startswith("{")]
            summary = parsed_lines[-1] if parsed_lines else None
            checks = parsed_lines[:-1]
        except json.JSONDecodeError:
            summary = None
        exit_code = test_proc.returncode
    else:
        exit_code = proc.returncode
    checks_ok = bool(summary) and summary.get("status") == "PASS" and \
        summary.get("failures") == 0 and len(checks) == summary.get("checks") and \
        all(row.get("status") == "PASS" for row in checks)
    return {
        "command": " ".join(cmd), "exit_code": exit_code, "compile_exit_code": proc.returncode,
        "stdout": stdout, "stderr": stderr, "exe": str(exe),
        "exe_sha256": sha256_of(exe) if exe.is_file() else None,
        "checks": checks, "summary": summary, "matched": checks_ok and exit_code == 0 and not stderr.strip(),
    }


def build_api_test_32bit(build_dir: Path) -> dict:
    """編譯 32-bit size_t 分支並如實記錄 CRT 缺失時的不可執行狀態。"""
    build_dir.mkdir(parents=True, exist_ok=True)
    compile_results: list[dict] = []
    compile_sources = [SRC[0], API_TEST_SRC]
    for source in compile_sources:
        obj = build_dir / f"{source.stem}_32.o"
        cmd = [str(GCC), "-m32", *FLAGS, "-I", str(INC), "-c", str(source), "-o", str(obj)]
        proc, stdout, stderr = _run_utf8(cmd)
        compile_results.append({"source": str(source), "command": " ".join(cmd),
                                "exit_code": proc.returncode, "stdout": stdout,
                                "stderr": stderr, "object": str(obj),
                                "object_sha256": sha256_of(obj) if obj.is_file() else None})
    exe = build_dir / "s4_inject_api_test_32.exe"
    link_cmd = [str(GCC), "-m32", *FLAGS, "-I", str(INC), str(SRC[0]), str(API_TEST_SRC), "-o", str(exe)]
    link_proc, link_stdout, link_stderr = _run_utf8(link_cmd)
    runtime: dict = {"status": "NOT_RUN", "exit_code": None, "stdout": "", "stderr": ""}
    if link_proc.returncode == 0:
        test_proc, test_stdout, test_stderr = _run_utf8([str(exe)])
        try:
            parsed_lines = [json.loads(line) for line in test_stdout.splitlines() if line.startswith("{")]
            test_summary = parsed_lines[-1] if parsed_lines else None
            test_checks = parsed_lines[:-1]
        except json.JSONDecodeError:
            test_summary = None
            test_checks = []
        runtime_ok = test_proc.returncode == 0 and bool(test_summary) and \
            test_summary.get("status") == "PASS" and test_summary.get("failures") == 0 and \
            len(test_checks) == test_summary.get("checks") and \
            all(row.get("status") == "PASS" for row in test_checks) and not test_stderr.strip()
        runtime = {"status": "PASS" if runtime_ok else "FAIL",
                   "exit_code": test_proc.returncode, "stdout": test_stdout, "stderr": test_stderr,
                   "checks": test_checks, "summary": test_summary}
    compiler_ok = all(row["exit_code"] == 0 and row["stderr"].strip() == "" for row in compile_results)
    expected_crt_unavailable = link_proc.returncode != 0 and \
        "cannot find -lmingw32" in link_stderr and "cannot find -lgcc" in link_stderr
    return {
        "mode": "compile_only_unless_runtime_links",
        "compile_only": compile_results,
        "compile_only_status": "PASS" if compiler_ok else "FAIL",
        "link_attempt": {"command": " ".join(link_cmd), "exit_code": link_proc.returncode,
                          "stdout": link_stdout, "stderr": link_stderr,
                          "exe_sha256": sha256_of(exe) if exe.is_file() else None},
        "runtime": runtime,
        "behavioral_status": runtime["status"],
        "link_failure_classified_as_missing_i686_runtime": expected_crt_unavailable,
        "matched": compiler_ok and (runtime["status"] == "PASS" or
                                     (runtime["status"] == "NOT_RUN" and expected_crt_unavailable)),
        "limitation": None if runtime["status"] == "PASS" else
            "32-bit size_t API 分支仅完成 -m32 编译期检查；链接/行为测试 NOT_RUN，当前 MinGW 缺少兼容 i686 CRT/libgcc。",
    }


def region_lines(regions: list[dict]) -> list[str]:
    """把地址图 region 转成 host op 脚本的 region 行。"""
    return [f"region name={r['name']} base={hex(r['base_addr'])} len={hex(r['length_bytes'])}" for r in regions]


def frame_line(**kwargs) -> str:
    """拼一条 frame op 行。"""
    order = ["id", "fmt", "w", "h", "stride", "len", "region", "base", "offset", "source", "scope_source",
             "capture", "capture_avail", "inject_ns", "clock", "freq", "wrap", "domain",
             "contract", "align", "algorithm", "digest", "payload", "payload_len",
             "scope_pl", "scope_uart", "scope_board"]
    return "frame " + " ".join(f"{key}={kwargs[key]}" for key in order if key in kwargs)


BASE_FRAME = {
    "fmt": "RGB888", "w": 4, "h": 4, "stride": 12, "region": "injection_frame_rgb", "session": 1,
    "source": "file_injection", "capture": "unavailable", "capture_avail": 0,
    "inject_ns": 12345, "clock": "XTime", "freq": 100000000, "wrap": "64bit",
    "domain": "PS", "contract": LEGACY_C_API_CONTRACT_VERSION,
    "scope_pl": "NOT_EXECUTED_OFFLINE", "scope_uart": "NOT_EXECUTED_OFFLINE",
    "scope_board": "NOT_EXECUTED_OFFLINE", "payload": "pattern:1",
}

FULL_SEQUENCE = [
    "bind",
    "advance slot=0 ev=producer_write_complete",
    "advance slot=0 ev=cache_flush_by_producer",
    "advance slot=0 ev=ownership_publish_to_consumer",
    "consume slot=0",
    "advance slot=0 ev=buffer_release_to_producer",
]


def _run_utf8(command: list[str], **kwargs) -> tuple[subprocess.CompletedProcess[bytes], str, str]:
    """以 UTF-8 模式运行子进程，并对原始输出作严格 UTF-8 解码。"""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(command, capture_output=True, env=env, **kwargs)
    return proc, proc.stdout.decode("utf-8", errors="strict"), proc.stderr.decode("utf-8", errors="strict")


def run_case(exe: Path, work: Path, name: str, body: list[str], expected: int, regions: list[dict],
             base_addr: int, postcondition: dict | None = None) -> dict:
    """运行一个 op 脚本，核对退出码、稳定异常字段和状态后置条件。"""
    script = work / f"{name}.op"
    script.write_text("\n".join([*region_lines(regions), *body, ""]), encoding="utf-8")
    proc, stdout, stderr = _run_utf8([str(exe), str(script)])
    out_path = work / f"{name}.json"
    out_path.write_text(stdout, encoding="utf-8")
    parsed = None
    try:
        parsed = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        parsed = None
    ops = (parsed or {}).get("ops", [])
    failures = [op for op in ops if op.get("status") != E_OK and not op.get("try")]
    failure = failures[0] if failures else None
    expected_field, reason_part = CASE_FIELDS.get(name, ("", ""))
    status_ok = bool(parsed) and parsed.get("status") == expected and parsed.get("status_name") == STATUS_NAMES.get(expected)
    if expected == E_OK:
        stable_ok = not failures and all(op.get("status_name") == "OK" for op in ops)
    else:
        stable_ok = bool(failure) and failure.get("status") == expected and \
            failure.get("status_name") == STATUS_NAMES.get(expected) and \
            failure.get("field") == expected_field and bool(failure.get("reason")) and \
            (reason_part in failure.get("reason", ""))
    post_ok = True
    post_errors: list[str] = []
    if parsed and postcondition:
        ring = parsed.get("ring", {})
        mock = parsed.get("mock_cache", {})
        for key, value in postcondition.items():
            if key == "write_count":
                actual = mock.get(key)
            elif key == "slot0_state":
                actual = (ring.get("slots") or [{}])[0].get("state")
            elif key == "slot1_state":
                actual = (ring.get("slots") or [{}, {}])[1].get("state")
            elif key == "held":
                actual = ring.get("held")
            else:
                actual = parsed.get(key)
            if actual != value:
                post_errors.append(f"{key}: expected={value!r} actual={actual!r}")
        post_ok = not post_errors
    if name == "fault_overlap_before_write" and parsed:
        mock = parsed.get("mock_cache", {})
        records = mock.get("write_records", [])
        expected_crc = zlib.crc32(lcg_payload(1, 48)) & 0xFFFFFFFF
        post_errors.extend([] if len(records) == 1 and records[0].get("crc32") == expected_crc else
                           [f"overlap altered/added write record: {records!r}"])
        post_ok = not post_errors
    detail = {
        "case": name,
        "expected_exit": expected,
        "actual_exit": proc.returncode,
        "expected_status_name": STATUS_NAMES.get(expected),
        "status_name": (parsed or {}).get("status_name"),
        "failed_op": failure,
        "stable_status_field_reason_matched": stable_ok,
        "postcondition_matched": post_ok,
        "postcondition_errors": post_errors,
        "matched": proc.returncode == expected and status_ok and stable_ok and post_ok,
        "script": str(script),
        "json": str(out_path),
        "ops": ops,
        "consumer": (parsed or {}).get("consumer"),
        "ring": (parsed or {}).get("ring"),
        "mock_cache": (parsed or {}).get("mock_cache"),
        "stderr": stderr,
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

    tmp_dir = WORKTREE / "tmp" / "4" / "S4-FIX-01" / args.run_id
    if tmp_dir.exists():
        print(f"[FAIL] 临时 RunId 已存在，拒绝覆盖：{tmp_dir}")
        return 2
    work = tmp_dir / "cases"
    work.mkdir(parents=True, exist_ok=True)
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
    if evidence_dir:
        if evidence_dir.exists() and any(evidence_dir.iterdir()):
            print(f"[FAIL] 证据 RunId 已存在且非空，拒绝覆盖：{evidence_dir}")
            return 2
        evidence_dir.mkdir(parents=True, exist_ok=True)

    build_info = build(tmp_dir / "build")
    if build_info["exit_code"] != 0:
        print(f"[FAIL] 编译失败：{build_info['stderr'][:2000]}")
        return 1
    exe = Path(build_info["exe"])
    warnings = [line for line in (build_info["stderr"] or "").splitlines() if line.strip()]
    api_info = build_api_test(tmp_dir / "api_build")
    warnings.extend(line for line in api_info["stderr"].splitlines() if line.strip())
    api_32_info = build_api_test_32bit(tmp_dir / "api32_build")
    for item in api_32_info["compile_only"]:
        warnings.extend(line for line in item["stderr"].splitlines() if line.strip())

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
        frame(id=10, offset=0), "bind",
        frame(id=11, offset=64), "bind",
        frame(id=12, offset=128), "bind",
    ], E_NO_FREE, regions, base_addr))
    results.append(run_case(exe, work, "no_overwrite_held_slot", [
        "ring slots=2",
        frame(id=20, offset=0), "bind",
        "advance slot=0 ev=producer_write_complete",
        frame(id=21, offset=64), "bind slot=0",
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
    results.append(run_case(exe, work, "fault_measurement_scope", ["ring slots=4",
        frame(id=51, scope_source="CAMERA"), "bind"], E_SCOPE, regions, base_addr))
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
    # 5) R2 反例：写前重叠、在途序号回退、乱序释放、停止确认与缓存可见性。
    results.append(run_case(exe, work, "fault_overlap_before_write", [
        "ring slots=2", frame(id=100, offset=0), "bind", frame(id=101, offset=0), "bind",
    ], E_OVERLAP, regions, base_addr, {"write_count": 1, "slot1_state": "FREE"}))
    results.append(run_case(exe, work, "fault_accept_10_then_9", [
        "ring slots=2", frame(id=10, offset=0), "bind", frame(id=9, offset=64), "bind",
    ], E_ORDER_FRAME, regions, base_addr, {"write_count": 1, "slot1_state": "FREE"}))
    results.append(run_case(exe, work, "fault_release_out_of_order", [
        "ring slots=2", frame(id=20, offset=0), "bind", frame(id=21, offset=64), "bind",
        "advance slot=0 ev=producer_write_complete", "advance slot=0 ev=cache_flush_by_producer",
        "advance slot=0 ev=ownership_publish_to_consumer", "consume slot=0",
        "advance slot=1 ev=producer_write_complete", "advance slot=1 ev=cache_flush_by_producer",
        "advance slot=1 ev=ownership_publish_to_consumer", "consume slot=1",
        "advance slot=1 ev=buffer_release_to_producer",
        "advance slot=0 ev=buffer_release_to_producer",
    ], E_ORDER_FRAME, regions, base_addr))
    results.append(run_case(exe, work, "fault_abort_before_stop_confirmation", [
        "ring slots=1", frame(id=110), "bind", "advance slot=0 ev=producer_write_complete",
        "advance slot=0 ev=cache_flush_by_producer", "advance slot=0 ev=ownership_publish_to_consumer",
        "try timeout slot=0", "abort slot=0",
    ], E_EVENT_ORDER, regions, base_addr, {"slot0_state": "FAILED", "held": 1, "write_count": 1}))
    for fault, name, expected in (
        ("skip_flush", "fault_skip_flush", E_FLUSH_COVERAGE),
        ("skip_invalidate", "fault_skip_invalidate", E_CACHE_VISIBILITY),
        ("shift_invalidate", "fault_shift_invalidate", E_CACHE_VISIBILITY),
        ("skip_barrier", "fault_skip_barrier", E_CACHE_BARRIER),
    ):
        if fault == "skip_flush":
            body = ["ring slots=1", f"mock_fault name={fault}", frame(id=120), "bind",
                    "advance slot=0 ev=producer_write_complete", "advance slot=0 ev=cache_flush_by_producer",
                    "advance slot=0 ev=ownership_publish_to_consumer"]
        else:
            body = ["ring slots=1", f"mock_fault name={fault}", frame(id=120), *FULL_SEQUENCE]
        results.append(run_case(exe, work, name, body, expected, regions, base_addr))
    # 6) 来源/采集时间真值表与严格数值解析。
    results.append(run_case(exe, work, "valid_synthetic_source", ["ring slots=1",
        frame(id=130, source="synthetic", scope_source="OFFLINE_REGRESSION"), *FULL_SEQUENCE], E_OK, regions, base_addr))
    results.append(run_case(exe, work, "valid_camera_source", ["ring slots=1",
        frame(id=131, source="camera", scope_source="CAMERA", capture="123", capture_avail=1), *FULL_SEQUENCE], E_OK, regions, base_addr))
    results.append(run_case(exe, work, "fault_synthetic_capture_available", ["ring slots=1",
        frame(id=132, source="synthetic", scope_source="OFFLINE_REGRESSION", capture="123", capture_avail=1), "bind"], E_FORGED_CAPTURE, regions, base_addr))
    results.append(run_case(exe, work, "fault_camera_capture_missing", ["ring slots=1",
        frame(id=133, source="camera", scope_source="CAMERA", capture="unavailable", capture_avail=0), "bind"], E_SCOPE, regions, base_addr))
    for name, value in (("fault_capture_trailing_junk", "123junk"), ("fault_capture_empty", ""),
                        ("fault_capture_negative", "-1"), ("fault_capture_overflow", "18446744073709551616")):
        results.append(run_case(exe, work, name, ["ring slots=1", frame(id=140, capture=value), "bind"], E_CLI, regions, base_addr))
    results.append(run_case(exe, work, "fault_u32_width_overflow", ["ring slots=1", frame(id=150, w=4294967296), "bind"], E_CLI, regions, base_addr))
    results.append(run_case(exe, work, "fault_u32_frame_overflow", ["ring slots=1", frame(id=4294967296), "bind"], E_CLI, regions, base_addr))
    results.append(run_case(exe, work, "fault_slot_overflow", ["ring slots=1", frame(id=151), "bind slot=4294967296"], E_CLI, regions, base_addr))

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
    status = "PASS" if not failures and not small_failures and map_check["status"] == "PASS" and \
        not warnings and api_info["matched"] and api_32_info["matched"] else "FAIL"

    summary = {
        "task_id": "S4-B",
        "run_id": args.run_id,
        "driver": "run_s4b_injection_offline",
        "generated_at_utc8": now_utc8(),
        "command": " ".join([sys.executable, *sys.argv]),
        "contract_version": LEGACY_C_API_CONTRACT_VERSION,
        "contract_scope": "仅验证当前旧版 C 注入 API s4-shared-io/1.1.0；不验证新契约 1.2.0 的 BGR888 运行期支持。",
        "address_map": {"path": str(MAP_PATH), "sha256": sha256_of(MAP_PATH), "check": map_check},
        "build": build_info,
        "direct_c_api_test": api_info,
        "direct_c_api_32bit": api_32_info,
        "build_warning_lines": warnings,
        "cases": results,
        "case_failures": [r["case"] for r in failures],
        "small_image_checks": small_image_checks,
        "small_image_failures": [c["case"] for c in small_failures],
        "counts": {"cases": len(results), "matched": len(results) - len(failures), "failed": len(failures),
                   "host_direct_api_checks": (api_info.get("summary") or {}).get("checks", 0),
                   "host_direct_api_failures": (api_info.get("summary") or {}).get("failures", 1),
                   "direct_api_32bit_compile_units": len(api_32_info["compile_only"]),
                   "direct_api_32bit_behavior": api_32_info["behavioral_status"]},
        "status": status,
        "limits": [
            "仅主机 mock DDR/cache 与 gcc；未接板卡、未接真实串口、未跑 PL。",
            "本驱动固定验证 C API 旧版 s4-shared-io/1.1.0；不覆盖 BGR888/1.2.0，运行期支持状态仍 NOT_IMPLEMENTED。",
            "NOT_RUN：板上注入（4-D）、真实 UART、摄像头、PL 推理时间/期限/吞吐、109 全量（S4-C）。",
            "注入模式下 capture_time_ns 不可用；本驱动不接受任何伪造采集时间。",
            api_32_info["limitation"] or "32-bit size_t 反例已完成严格编译及行为执行。",
        ],
    }
    console_lines = []
    if evidence_dir:
        (evidence_dir / "injection_offline_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        console_lines.append(f"[INFO] 证据：{evidence_dir / 'injection_offline_summary.json'}")
    for case in results:
        mark = "OK " if case["matched"] else "BAD"
        failure = case.get("failed_op") or {}
        console_lines.append(
            f"{mark} {case['case']}: exit={case['actual_exit']} expected={case['expected_exit']} "
            f"status={case['status_name']} field={failure.get('field')} reason={failure.get('reason')}"
        )
    for check in small_image_checks:
        console_lines.append(
            f"{'OK ' if check['crc_match'] and check['bytes_match'] else 'BAD'} {check['case']}: "
            f"crc={check['actual_crc32']} expected={check['expected_crc32']} valid={check['actual_valid_bytes']}"
        )
    console_lines.append(
        f"[{status}] 用例 {len(results)}（失败 {len(failures)}）、C API "
        f"{(api_info.get('summary') or {}).get('checks', 0)}（失败 {(api_info.get('summary') or {}).get('failures', 1)}）、"
        f"32-bit size_t 编译 {len(api_32_info['compile_only'])} 单元/行为 {api_32_info['behavioral_status']}、"
        f"小图 {len(small_image_checks)}（失败 {len(small_failures)}）、地址图 {map_check['status']}、编译告警行 {len(warnings)}"
    )
    if evidence_dir:
        (evidence_dir / "driver_console.txt").write_text("\n".join(console_lines) + "\n", encoding="utf-8")
    for line in console_lines:
        print(line)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
