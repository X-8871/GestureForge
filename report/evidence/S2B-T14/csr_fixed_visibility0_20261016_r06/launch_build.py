"""用已审资源监督器从R05 routed checkpoint执行一次post-route优化。"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import psutil

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T14" / RUN.name
R05 = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r05"
PROJECT = ROOT / "tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project"
XPR = PROJECT / "s2b_inference_candidate.xpr"
IMPL_RUN = PROJECT / "s2b_inference_candidate.runs/impl_1"
IMPL_BIT = IMPL_RUN / "s2b_inference_wrapper.bit"
R05_DCP = R05 / "routed.dcp"
R05_BIT = R05 / "s2b_inference.bit"
ARTIFACTS = (
    "timing_summary.rpt", "actual_timing_setup.rpt", "actual_timing_hold.rpt",
    "pulse_width.rpt", "clock_interaction.rpt", "clocks.rpt", "check_timing.rpt",
    "route_status.rpt", "utilization.rpt", "drc.rpt", "methodology.rpt",
    "methodology.json", "constraints.xdc", "routed.dcp", "s2b_inference.xsa",
    "s2b_inference.bit", "timing_metrics.tcldict",
)
GIB = 1024 ** 3
EXPECTED_SUPERVISOR_SHA256 = "c1f1eb733675a0c316788198420940236f062363808648f84c5293caccc85ac3"
EXPECTED_GUARD_SHA256 = "102f396c0e696bc611da5759d204f0bb25ee006026a7ada85f13b6eb9325035a"
sys.path.insert(0, str(RUN / "source_snapshot/verification"))
from s2b_process_supervisor import GIB as SUPERVISOR_GIB, supervise_process


def sha256(path):
    """计算文件原始字节SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    """读取UTF-8 JSON对象。"""
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    """先决条件失败即停止，禁止重复综合或覆盖证据。"""
    if not condition:
        raise RuntimeError(message)


def preflight():
    """核验R05真实失败、routed DCP、既有源和四个OOC输入。"""
    require(sys.version_info[:2] == (3, 12), "必须由受信任Python 3.12启动")
    supervisor = RUN / "source_snapshot/verification/s2b_process_supervisor.py"
    require(sha256(supervisor) == EXPECTED_SUPERVISOR_SHA256, "资源监督器快照SHA错误")
    guard = RUN / "source_snapshot/verification/s15_job_guard.py"
    require(sha256(guard) == EXPECTED_GUARD_SHA256, "Job guard快照SHA错误")
    result_path = R05 / "result.json"
    input_path = R05 / "input_record.json"
    require(result_path.is_file() and input_path.is_file(), "R05终态记录缺失")
    r05, r05_input = load_json(result_path), load_json(input_path)
    require(r05.get("status") == "FAIL" and r05.get("hardware_execution") == "NOT_RUN" and
            r05.get("source_commit") == r05_input.get("source_commit"), "R05不是预期的真实失败Run")
    job = r05.get("job", {})
    require(job.get("status") == "PASS" and job.get("exit_code") == 0 and
            job.get("cleanup_confirmed") is True, "R05原生Job或清理未通过")
    require(r05.get("native_log_has_bitstream_complete") is True and
            r05.get("input_bindings_unchanged") is True and
            r05.get("missing_or_empty_artifacts") == [], "R05完整产物/输入绑定核验失败")
    timing = r05.get("timing_slack_values", {})
    require(type(timing.get("setup_slack")) in (int, float) and timing["setup_slack"] < 0 and
            r05.get("timing_slacks_nonnegative") is False, "R05失败依据不是setup timing violation")
    for path, name in ((R05_DCP, "routed.dcp"), (R05_BIT, "s2b_inference.bit")):
        require(path.is_file() and path.stat().st_size > 0 and
                r05.get("artifact_sha256", {}).get(name) == sha256(path),
                "R05原始产物缺失或SHA不符：" + name)
    require(XPR.is_file() and sha256(XPR) == r05.get("project_xpr_after_sha256"),
            "R05已核验工程XPR发生变化")
    require(IMPL_BIT.is_file() and sha256(IMPL_BIT) == r05.get("artifact_sha256", {}).get("s2b_inference.bit"),
            "临时impl_1 bit与R05归档bit不一致，拒绝替换")
    source_sha256 = r05.get("source_sha256")
    require(type(source_sha256) is dict, "R05源码绑定缺失")
    key_sources = ("src/s2b_control_csr.sv", "src/s2b_stage2b_core.sv", "src/s2b_inference_top.sv")
    for relative in key_sources:
        expected = source_sha256.get(relative)
        require(type(expected) is str, "R05缺少关键RTL绑定：" + relative)
        path = ROOT / relative
        require(path.is_file() and sha256(path) == expected, "RTL/flow源发生变化：" + relative)
    require(r05.get("native_log_has_failure") is True, "R05应保留并识别原始TIMING_NOT_MET失败")
    return r05, r05_input, {relative: source_sha256[relative] for relative in key_sources}


def parse_timing_summary(path):
    """读取Vivado总表第一行设计级WNS/TNS、WHS/THS和WPWS/TPWS。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    section = text.split("| Design Timing Summary", 1)[-1].split("| Clock Summary", 1)[0]
    match = re.search(
        r"(?m)^\s*(-?(?:\d+(?:\.\d*)?|\.\d+))\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s+\d+\s+\d+\s+"
        r"(-?(?:\d+(?:\.\d*)?|\.\d+))\s+(-?(?:\d+(?:\.\d*)?|\.\d+))\s+\d+\s+\d+\s+"
        r"(-?(?:\d+(?:\.\d*)?|\.\d+))\s+(-?(?:\d+(?:\.\d*)?|\.\d+))",
        section,
    )
    if match is None:
        return {}
    values = [float(value) for value in match.groups()]
    return dict(zip(("setup_wns", "setup_tns", "hold_whs", "hold_ths", "pulse_wpws", "pulse_tpws"), values))


def main():
    """先核验输入，再以一项受控Vivado Job执行，并把负slack如实判为失败。"""
    require(WORK.is_dir(), "R06临时工作目录缺失")
    require(not (RUN / "input_record.json").exists() and not (RUN / "result.json").exists(),
            "R06已有运行记录，拒绝覆盖")
    for name in (*ARTIFACTS, "vivado.stdout.log", "vivado.native.log", "vivado.native.jou"):
        require(not (RUN / name).exists(), "R06已有输出，拒绝覆盖：" + name)
    r05, r05_input, key_rtl_sha256 = preflight()
    build_tcl, build_cmd = RUN / "build.tcl", RUN / "build.cmd"
    require(build_tcl.is_file() and build_cmd.is_file(), "R06 Vivado脚本缺失")
    interpreter = Path(sys.executable).resolve()
    require(interpreter.is_file(), "当前Python解释器路径无效")
    record = {
        "status": "RUNNING", "hardware_execution": "NOT_RUN",
        "source_commit": r05["source_commit"],
        "r05_result": str(R05 / "result.json"), "r05_result_sha256": sha256(R05 / "result.json"),
        "r05_input_record": str(R05 / "input_record.json"), "r05_input_record_sha256": sha256(R05 / "input_record.json"),
        "r05_routed_dcp": str(R05_DCP), "r05_routed_dcp_sha256": sha256(R05_DCP),
        "r05_bit_sha256": sha256(R05_BIT),
        "project_xpr": str(XPR), "project_xpr_sha256": sha256(XPR),
        "temporary_impl_bit": str(IMPL_BIT), "temporary_impl_bit_before_sha256": sha256(IMPL_BIT),
        "build_tcl_sha256": sha256(build_tcl), "build_cmd_sha256": sha256(build_cmd),
        "driver_sha256": sha256(Path(__file__)), "python_executable": str(interpreter),
        "python_version": sys.version, "psutil_version": psutil.__version__,
        "supervisor_sha256": sha256(RUN / "source_snapshot/verification/s2b_process_supervisor.py"),
        "key_rtl_sha256": key_rtl_sha256,
        "command": [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(build_cmd)],
        "working_directory": str(WORK),
        "budget": {"max_heavy_jobs": 1, "start_floor_bytes": int(4.5 * GIB),
                   "stop_floor_bytes": 2 * GIB, "timeout_seconds": 1800,
                   "sample_interval_seconds": 0.25, "max_sample_gap_seconds": 1.0},
        "temporary_bit_replacement_reason": "先核对临时impl_1 bit等于不可变R05归档bit；用R06新bit替换可重建临时run产物，供Vivado原生write_hw_platform -include_bit导出。R05报告目录原bit/XSA/DCP保持不变。",
    }
    with (RUN / "input_record.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    with (RUN / "vivado.stdout.log").open("xb") as output:
        job = supervise_process(
            name="s2b_inference_visibility0_postroute_physopt_r06",
            command=record["command"], cwd=str(WORK), environment=dict(os.environ),
            output_stream=output, timeout_seconds=1800, sample_interval_seconds=0.25,
            max_sample_gap_seconds=1.0, start_floor_bytes=int(4.5 * GIB), stop_floor_bytes=2 * GIB,
        )
    record["job"] = job
    native_log = RUN / "vivado.native.log"
    native_text = native_log.read_text(encoding="utf-8", errors="replace") if native_log.is_file() else ""
    record["native_log_sha256"] = sha256(native_log) if native_log.is_file() else None
    record["native_log_has_failure"] = "BUILD_FAILED:" in native_text
    record["native_log_has_artifacts_written"] = "R06_ARTIFACTS_WRITTEN" in native_text
    record["native_log_has_phys_opt"] = "CHECKPOINT POSTROUTE_PHYS_OPT_COMPLETE" in native_text
    record["native_log_has_reroute"] = "CHECKPOINT REROUTE_COMPLETE" in native_text
    record["missing_or_empty_artifacts"] = [name for name in ARTIFACTS
                                            if not (RUN / name).is_file() or (RUN / name).stat().st_size == 0]
    record["artifact_sha256"] = {name: sha256(RUN / name) for name in ARTIFACTS
                                 if name not in record["missing_or_empty_artifacts"]}
    record["timing_slack_values"] = parse_timing_summary(RUN / "timing_summary.rpt") \
        if "timing_summary.rpt" not in record["missing_or_empty_artifacts"] else {}
    record["timing_slacks_nonnegative"] = (
        set(record["timing_slack_values"]) ==
        {"setup_wns", "setup_tns", "hold_whs", "hold_ths", "pulse_wpws", "pulse_tpws"}
        and all(value >= 0 for value in record["timing_slack_values"].values())
    )
    record["xsa_contains_bit"] = False
    record["xsa_embedded_bit_sha256"] = None
    xsa = RUN / "s2b_inference.xsa"
    bit = RUN / "s2b_inference.bit"
    if xsa.is_file() and xsa.stat().st_size > 0:
        try:
            with zipfile.ZipFile(xsa) as archive:
                bit_entries = [name for name in archive.namelist() if name.lower().endswith(".bit")]
                record["xsa_contains_bit"] = len(bit_entries) == 1
                if len(bit_entries) == 1:
                    record["xsa_embedded_bit_sha256"] = hashlib.sha256(archive.read(bit_entries[0])).hexdigest()
        except zipfile.BadZipFile:
            pass
    record["xsa_bit_matches_r06_bit"] = (
        record["xsa_contains_bit"] and bit.is_file() and
        record["xsa_embedded_bit_sha256"] == sha256(bit)
    )
    record["temporary_impl_bit_after_sha256"] = sha256(IMPL_BIT) if IMPL_BIT.is_file() else None
    record["temporary_impl_bit_matches_r06"] = (
        record["temporary_impl_bit_after_sha256"] == record["artifact_sha256"].get("s2b_inference.bit")
    )
    record["project_xpr_after_sha256"] = sha256(XPR) if XPR.is_file() else None
    record["input_bindings_unchanged"] = (
        record["project_xpr_after_sha256"] == record["project_xpr_sha256"]
        and record["temporary_impl_bit_matches_r06"]
        and sha256(R05 / "result.json") == record["r05_result_sha256"]
        and sha256(R05 / "input_record.json") == record["r05_input_record_sha256"]
        and sha256(R05_DCP) == record["r05_routed_dcp_sha256"]
        and sha256(R05_BIT) == record["r05_bit_sha256"]
        and all((ROOT / relative).is_file() and sha256(ROOT / relative) == expected
                for relative, expected in record["key_rtl_sha256"].items())
    )
    method_path = RUN / "methodology.json"
    record["methodology_checks_found"] = None
    if method_path.is_file():
        try:
            record["methodology_checks_found"] = int(load_json(method_path)["report_header"]["Checks found"])
        except (KeyError, ValueError, json.JSONDecodeError):
            pass
    base_ok = (
        job.get("status") == "PASS" and job.get("exit_code") == 0 and
        job.get("cleanup_confirmed") is True and not record["native_log_has_failure"] and
        record["native_log_has_artifacts_written"] and record["native_log_has_phys_opt"] and
        record["native_log_has_reroute"] and not record["missing_or_empty_artifacts"] and
        record["input_bindings_unchanged"] and record["xsa_bit_matches_r06_bit"]
    )
    if base_ok and record["timing_slacks_nonnegative"]:
        record["status"] = "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW"
    elif base_ok and not record["timing_slacks_nonnegative"]:
        record["status"] = "FAIL_TIMING"
    else:
        record["status"] = "FAIL"
    with (RUN / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    print(json.dumps({"status": record["status"], "job_status": job.get("status"),
                      "timing_slacks_nonnegative": record["timing_slacks_nonnegative"],
                      "xsa_bit_matches_r06_bit": record["xsa_bit_matches_r06_bit"]}, ensure_ascii=False))
    sys.exit(0 if record["status"] == "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW" else 1)


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        result_path = RUN / "result.json"
        if not result_path.exists():
            result_path.write_text(json.dumps({"status": "FAIL_PRECONDITION", "hardware_execution": "NOT_RUN",
                                               "source_commit": None, "error": repr(error),
                                               "job": {"status": "NOT_STARTED", "exit_code": None,
                                                       "cleanup_confirmed": True},
                                               "missing_or_empty_artifacts": list(ARTIFACTS),
                                               "native_log_has_failure": False,
                                               "timing_slacks_nonnegative": False,
                                               "xsa_contains_bit": False}, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        raise
