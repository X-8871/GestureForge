"""复用已独审的资源监督器，生成修复版离线位流并保留真实状态。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T14" / RUN.name
sys.path.insert(0, str(ROOT / "verification"))
from s2b_process_supervisor import GIB, supervise_process


def sha(path):
    """计算原字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert WORK.is_dir() and not (RUN / "result.json").exists()
metadata = json.loads((ROOT / "board/s2b_inference_platform.json").read_text(encoding="utf-8"))
sources = metadata["rtl_sources"] + ["vivado/s2b_inference_platform.tcl", "vivado/s2b_ps_platform.tcl",
    "board/s2b_inference_platform.json", "board/ps_platform_fields.json",
    "verification/s15_job_guard.py", "verification/s2b_process_supervisor.py"]
assert len(metadata["rtl_sources"]) == 18
assert sha(ROOT / "src/s2b_control_csr.sv") == "4beaad995d31835799a20138ed027125fbb4920795d64e471c6174ced12169d1"
snapshot = RUN / "source_snapshot"
snapshot.mkdir()
bindings = {}
for name in sources:
    source, target = ROOT / name, snapshot / name
    assert source.is_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    bindings[name] = sha(target)
wrapper = RUN / "build.cmd"
wrapper.write_bytes(('@echo off\r\ncall "D:\\Xilinx\\2026.1\\Vivado\\bin\\vivado.bat" -mode batch -source "'
    + str(RUN / "build.tcl") + '" -log "' + str(RUN / "vivado.native.log") + '" -journal "'
    + str(RUN / "vivado.native.jou") + '"\r\nexit /b %errorlevel%\r\n').encode("utf-8"))
record = {"status": "RUNNING", "hardware_execution": "NOT_RUN", "visibility_parameter": 0,
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": bindings, "command": [str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(wrapper)],
    "budget": "既有追加综合预算第2/3轮；4.5GiB启动、2GiB停止、单重型、1800秒墙钟。"}
with (RUN / "input_record.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
with (RUN / "vivado.stdout.log").open("xb") as output:
    job = supervise_process(name="csr_fixed_visibility0_synthesis_implementation", command=record["command"],
        cwd=str(WORK), environment=dict(os.environ), output_stream=output, timeout_seconds=1800,
        sample_interval_seconds=0.25, max_sample_gap_seconds=1.0,
        start_floor_bytes=int(4.5 * GIB), stop_floor_bytes=2 * GIB)
record["job"] = job
record["sources_unchanged"] = all(sha(ROOT / name) == expected for name, expected in bindings.items())
text = (RUN / "vivado.stdout.log").read_text(encoding="utf-8", errors="replace")
record["status"] = ("PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW" if
    job["status"] == "PASS" and job["exit_code"] == 0 and job["cleanup_confirmed"]
    and record["sources_unchanged"] and "PASS_IMPLEMENTED_ARTIFACTS_TIMING_REVIEW_PENDING" in text else "FAIL")
with (RUN / "result.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "job_status": job["status"]}, ensure_ascii=False))
sys.exit(0 if record["status"].startswith("PASS_") else 1)
