"""通过已审资源监督器复用完整 OOC 产物并完成顶层实现导出。"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T14" / RUN.name
R02 = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r02"
R03 = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r03"
R04_SNAPSHOT = RUN / "source_snapshot"
PROJECT = ROOT / "tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project"
RUNS = PROJECT / "s2b_inference_candidate.runs"
R02_RESULT_SHA256 = "af62259c4469c95fe92ada16595c37580447de1d9280a578e89dba3a33ab8e1f"
REUSED_IPS = (
    "s2b_inference_ps7_0",
    "s2b_inference_axi_gp0_lite_0",
    "s2b_inference_rst_fclk0_0",
)
ARTIFACTS = (
    "timing_summary.rpt",
    "actual_timing_setup.rpt",
    "actual_timing_hold.rpt",
    "pulse_width.rpt",
    "clock_interaction.rpt",
    "clocks.rpt",
    "check_timing.rpt",
    "route_status.rpt",
    "utilization.rpt",
    "drc.rpt",
    "methodology.rpt",
    "methodology.json",
    "constraints.xdc",
    "routed.dcp",
    "s2b_inference.xsa",
    "s2b_inference.bit",
    "timing_metrics.tcldict",
)
sys.path.insert(0, str(R04_SNAPSHOT / "verification"))
from s2b_process_supervisor import GIB, supervise_process


def sha256(path):
    """计算文件原始字节 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    """读取 UTF-8 JSON。"""
    return json.loads(path.read_text(encoding="utf-8"))


assert WORK.is_dir(), f"工作目录不存在：{WORK}"
assert sha256(R02 / "result.json") == R02_RESULT_SHA256, "R02 失败结果原件已变化"
R03_RESULT = R03 / "result.json"
R03_INPUT = R03 / "input_record.json"
assert R03_RESULT.is_file() and R03_INPUT.is_file(), "core-only R03 尚未产生终态结果"
core_result = load_json(R03_RESULT)
core_input = load_json(R03_INPUT)
core_job = core_result.get("job", {})
assert core_result.get("status") == "PASS_CORE_OOC_SYNTH", "R03 core OOC 未通过"
assert core_job.get("status") == "PASS" and core_job.get("exit_code") == 0, "R03 supervisor 原生状态非零"
assert core_job.get("cleanup_confirmed") is True, "R03 Job 清理未确认"
assert core_result.get("sources_unchanged") is True
assert core_result.get("source_bindings_unchanged") is True
assert core_result.get("live_project_sources_unchanged") is True
assert core_result.get("reused_ooc_dcps_unchanged") is True
assert core_result.get("new_runme_log_has_synth_success") is True
assert core_result.get("vivado_complete_marker") is True
assert core_result.get("vivado_end_marker") is True
assert core_result.get("vivado_running_marker_absent") is True
assert core_result.get("vivado_error_marker_absent") is True

project_xpr = PROJECT / "s2b_inference_candidate.xpr"
core_xci = PROJECT / "s2b_inference_candidate.srcs/sources_1/bd/s2b_inference/ip/s2b_inference_infer_0/s2b_inference_infer_0.xci"
assert core_xci.is_file()
assert project_xpr.is_file()
ooc_dcp_hashes = {}
core_run = RUNS / "s2b_inference_infer_0_synth_1"
core_dcp = core_run / "s2b_inference_infer_0.dcp"
assert core_dcp.is_file() and core_dcp.stat().st_size > 0
ooc_dcp_hashes[str(core_dcp)] = sha256(core_dcp)
assert ooc_dcp_hashes[str(core_dcp)] == core_result.get("core_dcp_sha256")
assert core_result.get("core_dcp_nonempty") is True
assert (core_run / "__synthesis_is_complete__").is_file()
assert (core_run / ".vivado.end.rst").is_file()
assert not (core_run / "__synthesis_is_running__").exists()
assert not (core_run / ".vivado.error.rst").exists()

expected_reused_hashes = {}
for instance in REUSED_IPS:
    run_name = f"{instance}_synth_1"
    run_dir = RUNS / run_name
    dcp = run_dir / f"{instance}.dcp"
    archived = R02 / "raw_failed_core/completed_ooc_reuse" / run_name / dcp.name
    assert (run_dir / "__synthesis_is_complete__").is_file()
    assert (run_dir / ".vivado.end.rst").is_file()
    assert dcp.is_file() and dcp.stat().st_size > 0
    assert archived.is_file(), f"已完成 IP 的封存副本缺失：{archived}"
    actual_hash = sha256(dcp)
    assert actual_hash == sha256(archived), f"DCP 与封存快照不一致：{instance}"
    expected_reused_hashes[str(dcp)] = actual_hash
    ooc_dcp_hashes[str(dcp)] = actual_hash
assert expected_reused_hashes == core_result.get("reused_ooc_dcp_sha256")

source_sha256 = core_result.get("source_sha256", {})
snapshot_sha256 = core_result.get("snapshot_sha256", {})
assert source_sha256 and snapshot_sha256
for relative, expected in source_sha256.items():
    source = ROOT / relative
    assert source.is_file() and sha256(source) == expected, f"live RTL/flow 输入已变化：{relative}"
for relative, expected in snapshot_sha256.items():
    snapshot_file = R04_SNAPSHOT / relative
    assert snapshot_file.is_file() and sha256(snapshot_file) == expected, f"R04 绑定快照不匹配：{relative}"

assert not (RUN / "input_record.json").exists()
assert not (RUN / "result.json").exists()
assert not (RUN / "vivado.stdout.log").exists()
for artifact in ARTIFACTS:
    assert not (RUN / artifact).exists(), f"R04 目标证据已存在，拒绝覆盖：{artifact}"

run_input_files = {}
for name in (
    "s2b_inference_infer_0.tcl",
    "s2b_inference_ps7_0.tcl",
    "s2b_inference_axi_gp0_lite_0.tcl",
    "s2b_inference_rst_fclk0_0.tcl",
):
    candidate = None
    for instance in ("s2b_inference_infer_0", "s2b_inference_ps7_0", "s2b_inference_axi_gp0_lite_0", "s2b_inference_rst_fclk0_0"):
        path = RUNS / f"{instance}_synth_1" / name
        if path.is_file():
            candidate = path
            break
    if candidate is not None:
        run_input_files[str(candidate)] = sha256(candidate)

build_tcl = RUN / "build.tcl"
build_cmd = RUN / "build.cmd"
assert build_tcl.is_file() and build_cmd.is_file()
record = {
    "status": "RUNNING",
    "hardware_execution": "NOT_RUN",
    "source_commit": core_result["source_commit"],
    "source_sha256": source_sha256,
    "source_snapshot_sha256": snapshot_sha256,
    "core_ooc_result": str(R03_RESULT),
    "core_ooc_result_sha256": sha256(R03_RESULT),
    "core_ooc_input_sha256": sha256(R03_INPUT),
    "core_dcp_sha256": sha256(core_dcp),
    "reused_ooc_dcp_sha256": expected_reused_hashes,
    "all_ooc_dcp_sha256": ooc_dcp_hashes,
    "project_xpr": str(project_xpr),
    "project_xpr_sha256": sha256(project_xpr),
    "core_xci": str(core_xci),
    "core_xci_sha256": sha256(core_xci),
    "ooc_run_input_sha256": run_input_files,
    "build_tcl_sha256": sha256(build_tcl),
    "build_cmd_sha256": sha256(build_cmd),
    "command": [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(build_cmd)],
    "working_directory": str(WORK),
    "budget": "既有第3/3次综合预算；4.5GiB启动、2GiB停止、单重型、1800秒墙钟。只运行顶层 synth_1 与 impl_1 到 write_bitstream，不创建或重置 OOC run。",
    "memory_note": "经本地 CLI Vivado 驱动，不保留 IDE/MCP 父工程进程；节省量未经本 Run 实测。",
}
with (RUN / "input_record.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)

with (RUN / "vivado.stdout.log").open("xb") as output:
    job = supervise_process(
        name="s2b_inference_visibility0_top_synthesis_implementation",
        command=record["command"],
        cwd=str(WORK),
        environment=dict(os.environ),
        output_stream=output,
        timeout_seconds=1800,
        sample_interval_seconds=0.25,
        max_sample_gap_seconds=1.0,
        start_floor_bytes=int(4.5 * GIB),
        stop_floor_bytes=2 * GIB,
    )

record["job"] = job
record["input_bindings_unchanged"] = (
    sha256(R03_RESULT) == record["core_ooc_result_sha256"]
    and sha256(R03_INPUT) == record["core_ooc_input_sha256"]
    and sha256(project_xpr) == record["project_xpr_sha256"]
    and sha256(core_xci) == record["core_xci_sha256"]
    and sha256(build_tcl) == record["build_tcl_sha256"]
    and sha256(build_cmd) == record["build_cmd_sha256"]
    and all(sha256(Path(path)) == expected for path, expected in run_input_files.items())
    and all(sha256(Path(path)) == expected for path, expected in ooc_dcp_hashes.items())
    and all(sha256(ROOT / name) == expected for name, expected in source_sha256.items())
    and all(sha256(R04_SNAPSHOT / name) == expected for name, expected in snapshot_sha256.items())
)
native_log = RUN / "vivado.native.log"
native_text = native_log.read_text(encoding="utf-8", errors="replace") if native_log.is_file() else ""
record["native_log_sha256"] = sha256(native_log) if native_log.is_file() else None
record["native_log_has_ooc_gate"] = "CHECKPOINT OOC_PREREQUISITES_VERIFIED" in native_text
record["native_log_has_synth_complete"] = "CHECKPOINT SYNTH_COMPLETE" in native_text
record["native_log_has_bitstream_complete"] = "CHECKPOINT BITSTREAM_COMPLETE" in native_text
record["native_log_has_final_sentinel"] = "PASS_TOP_SYNTH_IMPL_ARTIFACTS_TIMING_REVIEW_PENDING" in native_text
record["native_log_has_failure"] = "BUILD_FAILED:" in native_text
record["artifact_sha256"] = {}
record["artifact_sizes"] = {}
missing_artifacts = []
for name in ARTIFACTS:
    path = RUN / name
    if not path.is_file() or path.stat().st_size == 0:
        missing_artifacts.append(name)
        continue
    record["artifact_sha256"][name] = sha256(path)
    record["artifact_sizes"][name] = path.stat().st_size
record["missing_or_empty_artifacts"] = missing_artifacts
metrics_path = RUN / "timing_metrics.tcldict"
metrics_text = metrics_path.read_text(encoding="utf-8", errors="replace") if metrics_path.is_file() else ""
metric_values = {}
for metric in ("setup_slack", "hold_slack"):
    match = re.search(rf"(?:^|\s){metric}\s+\{{?(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\}}?(?=\s|$)", metrics_text)
    if match:
        metric_values[metric] = float(match.group(1))
record["timing_slack_values"] = metric_values
record["timing_slacks_nonnegative"] = (
    set(metric_values) == {"setup_slack", "hold_slack"}
    and all(value >= 0 for value in metric_values.values())
)
record["xsa_contains_bit"] = False
xsa = RUN / "s2b_inference.xsa"
if xsa.is_file() and xsa.stat().st_size > 0:
    try:
        with zipfile.ZipFile(xsa) as archive:
            record["xsa_contents"] = archive.namelist()
            record["xsa_contains_bit"] = any(name.lower().endswith(".bit") for name in archive.namelist())
    except zipfile.BadZipFile:
        record["xsa_contents"] = []

record["status"] = "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW" if (
    job.get("status") == "PASS"
    and job.get("exit_code") == 0
    and job.get("cleanup_confirmed") is True
    and record["input_bindings_unchanged"]
    and record["native_log_has_ooc_gate"]
    and record["native_log_has_synth_complete"]
    and record["native_log_has_bitstream_complete"]
    and record["native_log_has_final_sentinel"]
    and not record["native_log_has_failure"]
    and not missing_artifacts
    and record["timing_slacks_nonnegative"]
    and record["xsa_contains_bit"]
) else "FAIL"
with (RUN / "result.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "job_status": job.get("status")}, ensure_ascii=False))
sys.exit(0 if record["status"].startswith("PASS_") else 1)
