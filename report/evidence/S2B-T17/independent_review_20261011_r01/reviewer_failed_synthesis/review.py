"""独立只读核查失败综合证据，输出仅位于本审查临时目录。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone, timedelta

ROOT = Path.cwd().resolve()
RUN = ROOT / "report/evidence/S2B-T17/full_synthesis_20261011_r01"
OUT = Path(__file__).resolve().parent
BASELINE = "b8d5e5238fd01c460aa3155144785d65e06fc16e"
MANIFEST_SHA = "0f9febad96973109ccaba7877665ac0cfaa9f1f2bad9526d2f6293176bf51136"
STA_SHA = "e41b01e24be3fbefd38780a0516ef98d47ff1fdf7378ec42d033ee28cec7bee5"
started = time.monotonic()
checks = []
commands = []

def digest(path):
    """按原始字节计算哈希。"""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def load(name):
    """UTF-8 读取当前唯一证据目录中的 JSON。"""
    return json.loads((RUN / name).read_text(encoding="utf-8"))

def verify(name, condition, detail):
    """积累独立检查结果，保留失败诊断。"""
    checks.append({"name": name, "pass": bool(condition), "detail": detail})

def command(args, name):
    """运行轻量只读命令并保留真实原生退出码。"""
    result = subprocess.run(args, cwd=ROOT, capture_output=True)
    log = OUT / (name + ".log")
    log.write_bytes(result.stdout + b"\nSTDERR\n" + result.stderr)
    commands.append({"command": args, "native_exit_code": result.returncode,
                     "log": str(log), "sha256": digest(log)})
    return result

head = command(["git", "rev-parse", "HEAD"], "baseline").stdout.decode().strip()
verify("审查基线", head == BASELINE, head)
verify("固定清单", digest(RUN / "delivery_manifest.json") == MANIFEST_SHA, MANIFEST_SHA)
verify("固定STA分类", digest(RUN / "sta_classification.json") == STA_SHA, STA_SHA)
manifest = load("delivery_manifest.json")
verify("源码提交字段", manifest["source_commit"] == "f260880aa68c3aeb45405bb2dcd92d0b32bb9b16", manifest["source_commit"])
before_files = {str(p.relative_to(RUN)): digest(p) for p in RUN.rglob("*") if p.is_file()}
for name in ["original_inventory.json", "original_inventory_r02.json"]:
    inventory = load(name)
    verify(name, all((ROOT / p).is_file() and digest(ROOT / p) == sha for p, sha in inventory.items()), {"count": len(inventory)})
source = load("source_before.json")
source_results = []
for row in source["source_files"]:
    snap = (ROOT / row["snapshot"]).read_bytes()
    blob = subprocess.run(["git", "show", source["source_commit"] + ":" + row["path"]], cwd=ROOT, capture_output=True)
    same = blob.returncode == 0 and snap == blob.stdout
    eol_only = blob.returncode == 0 and b"\r\n" not in blob.stdout and blob.stdout.replace(b"\n", b"\r\n") == snap
    source_results.append({"path": row["path"], "declared_sha256": row["sha256"], "actual_sha256": hashlib.sha256(snap).hexdigest(),
                           "git_raw_same": same, "exact_git_lf_to_snapshot_crlf": eol_only, "git_exit_code": blob.returncode,
                           "git_blob_sha256": hashlib.sha256(blob.stdout).hexdigest()})
verify("24份RAW快照与声明", len(source_results) == 24 and all(r["actual_sha256"] == r["declared_sha256"] for r in source_results), source_results)
eol_paths = sorted(r["path"] for r in source_results if not r["git_raw_same"])
verify("20份Git RAW相同与4份精确EOL转换", sum(r["git_raw_same"] for r in source_results) == 20 and
       eol_paths == sorted(["src/s2a_conv_tile_engine.sv", "src/s2a_network_backend.sv", "src/s2a_network_descriptor_pkg.sv", "src/s2a_stage2a_core_ooc.sv"]) and
       all(r["git_raw_same"] or r["exact_git_lf_to_snapshot_crlf"] for r in source_results), eol_paths)
native_tcl = (RUN / "native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
rtl_block = re.search(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}", native_tcl)[1]
rtl_inputs = [Path(line.strip()).relative_to(ROOT).as_posix() for line in rtl_block.splitlines() if line.strip()]
verify("原native综合Tcl的18RTL与快照闭包对应", len(rtl_inputs) == 18 and set(rtl_inputs) == {r["path"] for r in source["source_files"] if r["path"].endswith(".sv")}, rtl_inputs)
mapping = load("native_archive_mapping.json")
relocation = load("native_archive_relocation_r02.json")
relocated = {r["original_saved_path"]: r["new_saved_path"] for r in relocation["files"]}
native_files = []
for row in mapping["files"]:
    saved = ROOT / row["saved_path"]
    if not saved.exists():
        saved = Path(relocated.get(str(saved), "__INVALID__"))
    native_files.append(saved.is_file() and digest(saved) == row["sha256"] and saved.stat().st_size == row["bytes"])
verify("native归档精确迁移与SHA", len(native_files) == 30 and all(native_files), {"files": len(native_files), "relocated": len(relocation["files"])})
job_results = []
for row in mapping["jobs"]:
    name = "wrapper_native_r01" if row["run"] == "synth_1" else row["run"]
    directory = RUN / "native_jobs" / name
    log = (directory / "runme.log").read_text(encoding="utf-8")
    timing = re.search(r"synth_design:.*?elapsed = (\d+):(\d+):(\d+).*?peak = ([0-9.]+)", log)
    seconds = sum(int(timing[i]) * scale for i, scale in [(1,3600),(2,60),(3,1)]) if timing else None
    peak = float(timing[4]) if timing else None
    pid = int(re.search(r"Process ID\s*:\s*(\d+)", log)[1])
    ok = seconds == row["elapsed_synth_design_seconds"] and peak == row["reported_single_process_peak_mb"] and pid == row["reported_process_id"]
    ok = ok and "synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log
    ok = ok and (directory / ".vivado.end.rst").is_file() and (directory / "__synthesis_is_complete__").is_file()
    ok = ok and len(list(directory.glob("*.tcl"))) == 1 and len(list(directory.glob("*_utilization_synth.rpt"))) == 1 and row["raw_process_exit_code"] is None
    job_results.append({"run": row["run"], "pass": ok, "elapsed_seconds": seconds, "single_process_peak_mb": peak, "pid": pid})
verify("5个job原始日志资源耗时和完成记录", len(job_results) == 5 and all(r["pass"] for r in job_results), job_results)
verify("禁止混加内存与耗时", mapping["process_tree_peak_bytes"] is None and mapping["queue_elapsed_seconds"] is None, "各job单进程峰值不等于总进程树峰值")
raw = load("root_mcp_calls_and_history.json")
history = json.loads(raw["history"]["content"][0]["text"])["history"]
wait = next(r for r in history if r["command"] == "wait_on_run synth_1")
client_wait = next(r for r in raw["calls"] if r["command"] == "wait_on_run synth_1")["result"]
verify("客户端timeout和native完成分开", client_wait["isError"] and "after 300s" in client_wait["content"][0]["text"] and wait["code"] == 0 and wait["elapsed"] == 311.587, {"client": "FAIL_TIMEOUT_300S", "native_code": wait["code"], "native_elapsed": wait["elapsed"]})
verify("原采集失败保留", load("collection_result.json")["collection_native_exit_code"] == 1 and load("collection_result.json")["status"] == "FAIL_COLLECTION", "原始Git RAW相同断言失败不改写")
old_probe = (RUN / "evidence_probe.log").read_text(encoding="utf-8")
verify("原归档目录包装失败保留", "synth_1" in old_probe and "CHECKS_FAILED" in old_probe, old_probe[-1600:])
for mode, expected in [("evidence", 0), ("inputs", 2)]:
    result = command([sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode, "--manifest", str(RUN / "delivery_manifest.json")], "delivery_" + mode)
    verify("当前清单" + mode, result.returncode == expected, {"native_exit_code": result.returncode, "expected": expected})
sta_result = command([sys.executable, "-B", str(RUN / "classify_sta.py"), str(RUN), str(OUT / "sta_reparsed_r02.json")], "sta_reparse_r02")
sta = load("sta_classification.json")
parsed = json.loads((OUT / "sta_reparsed_r02.json").read_text(encoding="utf-8"))
verify("STA重解析", sta_result.returncode == 2 and parsed == sta, {"native_exit_code": sta_result.returncode})
verify("失败时序及资源值", sta["status"] == "FAIL_TIMING" and sta["timing"]["wns_ns"] == -76.685 and sta["timing"]["tns_ns"] == -117866.523 and sta["timing"]["setup_failing_endpoints"] == 2639 and sta["timing"]["ths_ns"] == 0 and sta["worst_setup_path"]["logic_levels"] == 239 and sta["clock"]["frequency_mhz"] == 50 and sta["resources"] == {"lut":42820,"ff":4003,"bram_tiles":32,"dsp":186}, sta)
verify("后实现与实物未运行", sta["post_route"] == "NOT_RUN" and sta["hardware_execution"] == "NOT_RUN", "仅综合报告，STA失败")
after_files = {str(p.relative_to(RUN)): digest(p) for p in RUN.rglob("*") if p.is_file()}
verify("被审全部文件前后不变", before_files == after_files and digest(RUN / "delivery_manifest.json") == MANIFEST_SHA, {"file_count": len(after_files)})
class ProcessMemoryCounters(ctypes.Structure):
    """Windows 单进程工作集计数器。"""
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [(name, ctypes.c_size_t) for name in ["PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage"]]
memory = ProcessMemoryCounters()
memory.cb = ctypes.sizeof(memory)
kernel = ctypes.WinDLL("kernel32")
kernel.GetCurrentProcess.restype = wintypes.HANDLE
psapi = ctypes.WinDLL("psapi")
psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessMemoryCounters), wintypes.DWORD]
measured = bool(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(memory), memory.cb))
verify("轻量审查内存预算", measured and memory.PeakWorkingSetSize < 300 * 1024 * 1024, {"single_process_peak_working_set_bytes": memory.PeakWorkingSetSize, "child_peak_not_measured": True})
status = "PASS_EVIDENCE_INTEGRITY" if all(c["pass"] for c in checks) else "CHANGES_REQUIRED"
receipt = {"schema_version":1, "status":status, "scope":"S2B-T17 原失败综合证据保全，只读核验准确性；不代表STA或2B通过", "reviewed_baseline": BASELINE,
           "manifest_sha256":MANIFEST_SHA, "sta_sha256":STA_SHA, "source_origin_commit":source["source_commit"], "current_S1_source_consumed":False,
           "time_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(), "elapsed_seconds":time.monotonic()-started,
           "commands":commands, "checks":checks, "findings":[c for c in checks if not c["pass"]],
           "limitations":["未执行Vivado/MCP/硬件/大型仿真，未复制模型或DCP，未修改源和证据，未提交。", "仅审查此次已保存字节，未声称复现综合或时序收敛。", "历史进程树峰值未测；本审查仅测自身单进程峰值，子进程峰值未测；最大证据单文件1302748字节。", "receipt.json的初版限制误称最大单文件小于1MB，现已精确纠正，初版保留。"]}
(OUT / "receipt_r02.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(status, "checks", len(checks), "failures", [c["name"] for c in checks if not c["pass"]])
sys.exit(0 if status == "PASS_EVIDENCE_INTEGRITY" else 2)
