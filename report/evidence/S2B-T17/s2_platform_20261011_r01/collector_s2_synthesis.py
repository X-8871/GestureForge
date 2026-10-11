"""保存已结束 S2 综合的原始证据，失败时序不改判通过。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile
import zlib

ROOT = Path.cwd()
RUN = ROOT / "report/evidence/S2B-T17/s2_platform_20261011_r01"
PRE = ROOT / "report/evidence/S2B-T17/s2_source_preflight_20261011_r01"
PROJECT = ROOT / "tmp/2B/S2B-T17/s2p1"
BASELINE = "5a676b700af4c27297977379417b1694dd64840e"
STARTED = time.monotonic()


def sha(path):
    """流式核对原字节。"""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    """读取 UTF-8 记录。"""
    return json.loads(path.read_text(encoding="utf-8"))


def save(name, value):
    """只创建新文件，禁止覆盖原件。"""
    p = RUN / name
    assert p.parent.is_dir() and not p.exists(), p
    with p.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return p


def copy_raw(source, target):
    """精确复制已结束运行的原件。"""
    assert source.is_file() and not source.is_symlink()
    assert target.parent.is_dir() and not target.exists()
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        for block in iter(lambda: incoming.read(1048576), b""):
            outgoing.write(block)
    assert sha(source) == sha(target)
    return {"original_path": str(source), "saved_path": target.relative_to(ROOT).as_posix(),
            "sha256": sha(target), "bytes": target.stat().st_size}


assert str(ROOT) == r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition"
assert all(p.is_dir() and not p.is_symlink() for p in [RUN, PRE, PROJECT])
original = {p.relative_to(ROOT).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
            for p in sorted(RUN.rglob("*")) if p.is_file()}
save("collector_original_inventory.json", original)
before = read(PRE / "source_before.json")
after = read(RUN / "source_after.json")
assert before["source_commit"] == BASELINE and before["platform_version"] == "0.1.2"
assert before["visibility"] == 0 and len(before["sources"]) == 28
assert before["sources"] == after["sources"]
source_rows = []
for row in before["sources"]:
    p = PRE / "source_snapshot" / row["path"]
    assert p.is_file() and sha(p) == row["sha256"] and p.stat().st_size == row["bytes"]
    result = subprocess.run(["git", "show", BASELINE + ":" + row["path"]], cwd=ROOT, capture_output=True)
    assert result.returncode == 0
    raw = p.read_bytes()
    equal = raw == result.stdout
    eol_only = b"\r\n" not in result.stdout and result.stdout.replace(b"\n", b"\r\n") == raw
    assert equal or eol_only, row["path"]
    source_rows.append({**row, "snapshot_path": p.relative_to(ROOT).as_posix(),
                        "git_blob_sha256": hashlib.sha256(result.stdout).hexdigest(),
                        "git_native_exit_code": result.returncode,
                        "git_raw_same": equal, "exact_git_lf_to_snapshot_crlf": eol_only})
save("collector_source_binding.json", {"status": "SOURCE28_RAW_BEFORE_AFTER_IDENTICAL_GIT_BOUND",
    "source_commit": BASELINE, "sources": source_rows, "current_s3_source_consumed": False})
native_dir = RUN / "native_jobs"
assert not native_dir.exists()
native_dir.mkdir()
native_map = []
jobs = []
dcp = []
run_root = PROJECT / "s2b_inference_candidate.runs"
assert run_root.is_dir()
for directory in sorted(p for p in run_root.iterdir() if p.is_dir() and p.name != ".jobs"):
    target_dir = native_dir / directory.name
    target_dir.mkdir()
    log_path = directory / "runme.log"
    assert log_path.is_file()
    log = log_path.read_text(encoding="utf-8")
    assert "synth_design completed successfully" in log
    assert "0 Critical Warnings and 0 Errors encountered" in log
    assert (directory / "__synthesis_is_complete__").is_file()
    assert (directory / ".vivado.end.rst").is_file() and not (directory / ".vivado.error.rst").exists()
    for p in sorted(directory.iterdir()):
        if not p.is_file():
            continue
        if p.suffix in {".tcl", ".log", ".jou", ".xdc", ".rpt"} or p.name in {
            ".vivado.begin.rst", ".vivado.end.rst", ".vivado.error.rst", "__synthesis_is_complete__",
            ".Vivado_Synthesis.queue.rst"}:
            native_map.append(copy_raw(p, target_dir / p.name))
        elif p.suffix == ".dcp":
            dcp.append({"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size,
                        "permanent": False, "scope": "ignored 可重建缓存，仅保存引用"})
    m = re.search(r"synth_design:.*?elapsed = (\d+):(\d+):(\d+)", log)
    jobs.append({"run": directory.name, "status": "NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS",
                 "pid": int(re.search(r"Process ID\s*:\s*(\d+)", log)[1]),
                 "synth_design_elapsed_seconds": sum(int(m[i]) * scale for i, scale in [(1, 3600), (2, 60), (3, 1)]),
                 "reported_single_process_peak_mb": max(map(float, re.findall(r"peak = ([0-9.]+)", log))),
                 "raw_process_exit_code": None,
                 "reason": "未直接观测各子进程OS退出码；使用原生wait及实际日志/结束markers。"})
assert len(jobs) == 5
profile = read(PRE / "source_snapshot/board/s2b_inference_platform.json")
native_tcl = (native_dir / "s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
block = re.search(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}", native_tcl)[1]
rtl = [Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
assert len(rtl) == 18 and set(rtl) == set(profile["rtl_sources"])
save("collector_native_mapping.json", {"files": native_map, "jobs": jobs, "actual_rtl_sources": rtl,
    "dcp_references": dcp, "process_tree_peak_memory": "NOT_MEASURED"})
raw = read(RUN / "root_mcp_calls_final.json")
history = json.loads(raw["history_after_reports"]["content"][0]["text"])["history"]
waits = [x for x in history if x["command"] == "wait_on_run synth_1"]
assert len(waits) == 1 and waits[0]["code"] == 0 and waits[0]["elapsed"] == 381.939
products = (RUN / "products.tcldict").read_text(encoding="utf-8")
assert "status FAIL code 0" in products and "emitted=-8" in products
log_source = Path(before["native_log_path"])
log_copy = RUN / "collector_root_session_log_snapshot.log"
native_log = copy_raw(log_source, log_copy)
save("collector_mcp_classification.json", {"wait_history": waits[0], "calls": len(raw["calls"]),
    "history_ids": [x["id"] for x in history], "mcp_client_wait_timeout_seconds": 300,
    "wait_native_exit_code": 0, "wait_native_elapsed_seconds": 381.939,
    "products_native_exit_code": 0, "products_capture_exit_code": 1,
    "capture_reason": "WARNING累计9→1导致capture失败，原入口native1/产品native0分别保留。",
    "root_session_log": native_log,
    "root_reported_cumulative_peak_mb": max(map(float, re.findall(rb"peak = ([0-9.]+)", log_copy.read_bytes()))),
    "process_tree_peak_memory": "NOT_MEASURED",
    "limitation": "追加日志原字节含前轮非UTF8字节，不转码；history和当前job绑定本次S2，旧run_progress不作完成依据。"})
timing = (RUN / "timing_summary_synth.rpt").read_text(encoding="utf-8")
line = re.search(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s*$", timing, re.M)
keys = ["wns_ns", "tns_ns", "setup_failing_endpoints", "setup_total_endpoints", "whs_ns", "ths_ns",
        "hold_failing_endpoints", "hold_total_endpoints", "wpws_ns", "tpws_ns", "pulse_failing_endpoints", "pulse_total_endpoints"]
values = {key: int(line[i + 1]) if "endpoints" in key else float(line[i + 1]) for i, key in enumerate(keys)}
assert values["wns_ns"] == -62.174 and values["tns_ns"] == -12041.195
assert values["setup_failing_endpoints"] == 811 and values["ths_ns"] == 0
clock = re.search(r"^clk_fpga_0\s+\{[^}]+\}\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$", timing, re.M)
assert clock and float(clock[1]) == 20 and float(clock[2]) == 50
checks = dict((k, int(v)) for k, v in re.findall(r"checking ([a-z_]+) \((\d+)\)", timing))
assert checks["unconstrained_internal_endpoints"] == 0
assert "No valid timing exceptions found." in (RUN / "exceptions_synth.rpt").read_text(encoding="utf-8")
util = (RUN / "utilization_flat_synth.rpt").read_text(encoding="utf-8")
resources = {key: int(re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*(\d+)\s*\|", util)[1])
             for label, key in [("Slice LUTs*", "lut"), ("Slice Registers", "ff"), ("Block RAM Tile", "bram"), ("DSPs", "dsp")]}
assert resources == {"lut": 35058, "ff": 4027, "bram": 32, "dsp": 173}
save("collector_sta_classification.json", {"status": "FAIL_TIMING", "timing": values,
    "resources": resources, "check_timing": checks, "clock_hz": 50000000,
    "worst_source": re.search(r"Source:\s+([^\r\n]+)", timing)[1].strip(),
    "worst_destination": re.search(r"Destination:\s+([^\r\n]+)", timing)[1].strip(),
    "logic_levels": 323, "carry4": 305, "data_path_delay_ns": 81.562,
    "report_command_native_exit_code": 0, "implementation": "NOT_RUN", "bitstream": "NOT_RUN", "hardware": "NOT_RUN"})
old_xsa = ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"
new_xsa = RUN / "s2b_inference_no_bit.xsa"
comparison = []
with zipfile.ZipFile(old_xsa) as a, zipfile.ZipFile(new_xsa) as b:
    for name in ["ps7_init.c", "ps7_init.h", "ps7_init.html", "ps7_init.tcl", "ps7_init_gpl.c", "ps7_init_gpl.h", "s2b_inference.hwh"]:
        x, y = a.read(name), b.read(name)
        assert zlib.crc32(x) == a.getinfo(name).CRC and zlib.crc32(y) == b.getinfo(name).CRC
        comparison.append({"member": name, "old_sha256": hashlib.sha256(x).hexdigest(),
            "new_sha256": hashlib.sha256(y).hexdigest(), "raw_equal": x == y,
            "old_crc32": a.getinfo(name).CRC, "new_crc32": b.getinfo(name).CRC})
assert all(x["raw_equal"] for x in comparison[:6]) and not comparison[6]["raw_equal"]
save("collector_xsa_member_comparison.json", {"status": "SIX_PS_INIT_RAW_IDENTICAL_HWH_CHANGED",
    "old_xsa_path": old_xsa.relative_to(ROOT).as_posix(), "old_xsa_sha256": sha(old_xsa),
    "new_xsa_path": new_xsa.relative_to(ROOT).as_posix(), "new_xsa_sha256": sha(new_xsa), "members": comparison,
    "limitation": "不能把旧BSP/ELF构建或整体XSA相同当成新runtime兼容性已批准。"})
assert all(sha(ROOT / p) == v["sha256"] for p, v in original.items())
save("collector_result.json", {"status": "COLLECTED_FAIL_TIMING", "role": "ROOT_COLLECTOR",
    "source_commit": BASELINE, "native_exit_code": 0, "elapsed_seconds": time.monotonic() - STARTED,
    "original_file_count": len(original), "original_raw_unchanged": True,
    "postroute": "NOT_RUN", "bitstream": "NOT_RUN", "hardware": "NOT_RUN",
    "process_tree_peak_memory": "NOT_MEASURED", "aggregate_synthesis_wall_time": "NOT_MEASURED"})
interfaces = read(ROOT / "report/evidence/S2B-T17/coordinates_20261011_r04/delivery_manifest.json")["interfaces"]
rows = []
for p in sorted(list(RUN.rglob("*")) + list(PRE.rglob("*"))):
    if p.is_file():
        role = "source" if "source_snapshot" in p.parts or p.suffix == ".py" else "log" if p.suffix in {".log", ".jou"} else "result"
        if p.name in {"source_before.json", "source_after.json", "s2b_inference_no_bit.xsa"}:
            role = "input"
        rows.append({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "role": role})
rows.append({"path": old_xsa.relative_to(ROOT).as_posix(), "sha256": sha(old_xsa), "role": "input"})
save("collector_delivery_manifest.json", {"schema_version": 1, "stage": "2B", "task_id": "S2B-T17",
    "run_id": "s2_platform_20261011_r01", "source_commit": BASELINE,
    "evidence_dir": RUN.relative_to(ROOT).as_posix(), "interfaces": interfaces, "files": rows,
    "tool_versions": {"Vivado": "2026.1", "Python": sys.version.split()[0], "part": "xc7z020clg400-2"},
    "checks": [
        {"name": "原件采集", "status": "PASS", "command": f'"{sys.executable}" -B "{__file__}"', "exit_code": 0},
        {"name": "本次native综合完成", "status": "PASS", "command": "wait_on_run synth_1", "exit_code": 0,
         "reason": "实际同次wait381.939秒；MCP300秒超时另存。"},
        {"name": "products入口capture", "status": "FAIL", "command": "::s2b_inference_platform::run", "exit_code": 1,
         "reason": "原capture计数9→1失败，产品native0单独保留。"},
        {"name": "50MHz综合STA", "status": "FAIL", "command": "report_timing_summary", "exit_code": 0,
         "reason": "报告命令真实0但STA失败WNS−62.174/TNS−12041.195；811setup端点失败。"},
        {"name": "实现/位流/板上验收", "status": "NOT_RUN", "command": None, "exit_code": None,
         "reason": "未满足时序；继续派生ROUTE优化，无降频或例外掩盖。"}],
    "limitations": ["ROOT采集未独立G2；CHECKS_OK只证明包装，STA仍失败。",
        "物理0.1.1未冻结；无postroute/bit/cache/实际模型或G3/G4/G5。",
        "仅消费S2 preflight28快照，不消费后续S3变化中的源码。",
        "DCP仅ignored缓存参考；各job单进程峰与root累计峰分开，完整进程树及严格总墙钟未测。"]})
print(json.dumps({"status": "STOP_COLLECTED_FAIL_TIMING", "manifest_sha256": sha(RUN / "collector_delivery_manifest.json"),
                  "files": len(rows), "resources": resources}, ensure_ascii=False))
