"""通过项目已审资源监督器独立运行 inference OOC 综合。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T14" / RUN.name
R02 = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r02"
R03_SNAPSHOT = RUN / "source_snapshot"
R02_RESULT_SHA256 = "af62259c4469c95fe92ada16595c37580447de1d9280a578e89dba3a33ab8e1f"
PROJECT = ROOT / "tmp/2B/S2B-T13/platform_csr_fixed_20261016_r03/project"
RUNS = PROJECT / "s2b_inference_candidate.runs"
CORE_RUN = RUNS / "s2b_inference_infer_0_synth_1"
CORE_DCP = CORE_RUN / "s2b_inference_infer_0.dcp"
LAUNCHER = RUN / "run_infer_ooc.cmd"
sys.path.insert(0, str(R03_SNAPSHOT / "verification"))
from s2b_process_supervisor import GIB, supervise_process


def sha256(path):
    """计算文件原始字节的 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


assert WORK.is_dir(), f"工作目录不存在：{WORK}"
assert (R02 / "raw_failed_core/s2b_inference_infer_0_synth_1").is_dir()
assert sha256(R02 / "result.json") == R02_RESULT_SHA256, "R02 原结果已变化"
assert LAUNCHER.is_file() and CORE_RUN.is_dir() and PROJECT.joinpath("s2b_inference_candidate.xpr").is_file()
assert not (RUN / "input_record.json").exists()
assert not (RUN / "result.json").exists()
assert not (RUN / "vivado.stdout.log").exists()
assert (CORE_RUN / "__synthesis_is_running__").is_file(), "失败 run 的 Vivado 运行标记与预期不符"
assert not (CORE_RUN / "__synthesis_is_complete__").exists()
assert not (CORE_RUN / ".vivado.end.rst").exists(), "检测到旧成功标记；拒绝将其当作本轮结果"
assert not CORE_DCP.exists(), "core DCP 已存在；停止以避免覆盖未审结果"

r02_result = json.loads((R02 / "result.json").read_text(encoding="utf-8"))
bindings = {}
for source in sorted(path for path in R03_SNAPSHOT.rglob("*") if path.is_file()):
    relative = source.relative_to(R03_SNAPSHOT).as_posix()
    bindings[relative] = sha256(source)
    source_name = relative
    expected = r02_result["source_sha256"].get(source_name)
    if expected is not None:
        assert bindings[relative] == expected, f"R02 源快照哈希不匹配：{relative}"

live_source_bindings = {}
for relative, expected in r02_result["source_sha256"].items():
    live_source = ROOT / relative
    assert live_source.is_file(), f"工程实际引用源缺失：{live_source}"
    actual = sha256(live_source)
    assert actual == expected, f"工程实际引用源与冻结输入不一致：{relative}"
    live_source_bindings[relative] = actual

run_inputs = {}
for name in ("runme.bat", "rundef.js", "ISEWrap.js", "s2b_inference_infer_0.tcl", "s2b_inference_infer_0.vds"):
    path = CORE_RUN / name
    assert path.is_file(), f"OOC run 输入缺失：{path}"
    run_inputs[name] = sha256(path)
project_xpr = PROJECT / "s2b_inference_candidate.xpr"
core_xci = PROJECT / "s2b_inference_candidate.srcs/sources_1/bd/s2b_inference/ip/s2b_inference_infer_0/s2b_inference_infer_0.xci"
assert core_xci.is_file(), f"OOC IP 描述文件缺失：{core_xci}"
reused_ooc_dcps = {}
for instance in ("s2b_inference_ps7_0", "s2b_inference_axi_gp0_lite_0", "s2b_inference_rst_fclk0_0"):
    run_dir = RUNS / f"{instance}_synth_1"
    checkpoint = run_dir / f"{instance}.dcp"
    assert (run_dir / "__synthesis_is_complete__").is_file()
    assert checkpoint.is_file() and checkpoint.stat().st_size > 0
    reused_ooc_dcps[str(checkpoint)] = sha256(checkpoint)
prelaunch_log_bytes = (CORE_RUN / "runme.log").stat().st_size
wrapper_sha256 = sha256(LAUNCHER)
record = {
    "status": "RUNNING",
    "hardware_execution": "NOT_RUN",
    "source_commit": r02_result["source_commit"],
    "source_sha256": r02_result["source_sha256"],
    "live_project_source_sha256": live_source_bindings,
    "snapshot_sha256": bindings,
    "ooc_run_input_sha256": run_inputs,
    "project_xpr": str(project_xpr),
    "project_xpr_sha256": sha256(project_xpr),
    "core_xci": str(core_xci),
    "core_xci_sha256": sha256(core_xci),
    "reused_ooc_dcp_sha256": reused_ooc_dcps,
    "core_run_directory": str(CORE_RUN),
    "core_launcher": str(LAUNCHER),
    "core_launcher_sha256": wrapper_sha256,
    "prelaunch_runme_log_bytes": prelaunch_log_bytes,
    "command": [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(LAUNCHER)],
    "working_directory": str(WORK),
    "budget": "既有第3/3次综合预算；4.5GiB启动、2GiB停止、单重型、1800秒墙钟。",
    "memory_note": "独立 runme 子进程不保留约600MiB Vivado父工程进程；该节省是预测值，未实测。",
}

with (RUN / "input_record.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)

with (RUN / "vivado.stdout.log").open("xb") as output:
    job = supervise_process(
        name="s2b_inference_infer_0_ooc_synthesis",
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
record["source_bindings_unchanged"] = all(
    sha256(R03_SNAPSHOT / name) == expected for name, expected in bindings.items())
record["live_project_sources_unchanged"] = all(
    sha256(ROOT / name) == expected for name, expected in live_source_bindings.items())
record["reused_ooc_dcps_unchanged"] = all(
    sha256(Path(name)) == expected for name, expected in reused_ooc_dcps.items())
record["r02_result_unchanged"] = sha256(R02 / "result.json") == R02_RESULT_SHA256
record["launcher_unchanged"] = sha256(LAUNCHER) == wrapper_sha256
run_log = CORE_RUN / "runme.log"
record["runme_log_sha256"] = sha256(run_log) if run_log.is_file() else None
record["core_dcp_sha256"] = sha256(CORE_DCP) if CORE_DCP.is_file() else None
record["core_dcp_nonempty"] = CORE_DCP.is_file() and CORE_DCP.stat().st_size > 0
try:
    with run_log.open("rb") as stream:
        stream.seek(prelaunch_log_bytes)
        new_log = stream.read().decode("utf-8", errors="replace")
except OSError:
    new_log = ""
record["new_runme_log_has_synth_success"] = "synth_design completed successfully" in new_log
record["vivado_complete_marker"] = (CORE_RUN / "__synthesis_is_complete__").is_file()
record["vivado_end_marker"] = (CORE_RUN / ".vivado.end.rst").is_file()
record["vivado_running_marker_absent"] = not (CORE_RUN / "__synthesis_is_running__").exists()
record["vivado_error_marker_absent"] = not (CORE_RUN / ".vivado.error.rst").exists()
record["sources_unchanged"] = (
    record["source_bindings_unchanged"]
    and record["live_project_sources_unchanged"]
    and record["reused_ooc_dcps_unchanged"]
    and record["r02_result_unchanged"]
    and record["launcher_unchanged"]
)
record["status"] = "PASS_CORE_OOC_SYNTH" if (
    job["status"] == "PASS"
    and job["exit_code"] == 0
    and job["cleanup_confirmed"]
    and record["sources_unchanged"]
    and record["new_runme_log_has_synth_success"]
    and record["vivado_complete_marker"]
    and record["vivado_end_marker"]
    and record["vivado_running_marker_absent"]
    and record["vivado_error_marker_absent"]
    and record["core_dcp_nonempty"]
) else "FAIL"
with (RUN / "result.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "job_status": job["status"]}, ensure_ascii=False))
sys.exit(0 if record["status"] == "PASS_CORE_OOC_SYNTH" else 1)
