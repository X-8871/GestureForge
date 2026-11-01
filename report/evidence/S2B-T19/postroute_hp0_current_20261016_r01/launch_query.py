"""在当前实现结束后，只读导出路由网表的 HP0 连接事实。"""
from pathlib import Path
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T19" / RUN.name
T14 = ROOT / "report/evidence/S2B-T14/csr_fixed_visibility0_20261016_r08"
sys.path.insert(0, str(ROOT / "verification"))
from s2b_process_supervisor import GIB, supervise_process


def sha(path):
    """计算原始字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


result = json.loads((T14 / "result.json").read_text(encoding="utf-8"))
assert result["status"] == "PASS_ARTIFACTS_PENDING_INDEPENDENT_REVIEW"
assert result["job"]["cleanup_confirmed"] is True
dcp = T14 / "routed.dcp"
assert sha(dcp) == result["artifact_sha256"]["routed.dcp"]
assert WORK.is_dir() and not (RUN / "result.json").exists()
record = {"status": "RUNNING", "hardware_execution": "NOT_RUN", "routed_dcp": str(dcp),
          "routed_dcp_sha256": sha(dcp), "t14_result_sha256": sha(T14 / "result.json"),
          "query_source_sha256": sha(RUN / "query.tcl")}
with (RUN / "input_record.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
with (RUN / "vivado.stdout.log").open("xb") as stream:
    job = supervise_process(name="current_routed_hp0_query",
        command=[str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(RUN / "query.cmd")],
        cwd=str(WORK), environment=dict(os.environ), output_stream=stream,
        timeout_seconds=480, sample_interval_seconds=0.25, max_sample_gap_seconds=1.0,
        start_floor_bytes=int(4.5 * GIB), stop_floor_bytes=2 * GIB)
record["job"] = job
output = RUN / "query_output.tcldict"
record["status"] = "PASS_QUERY_OBSERVATIONS_PENDING_REVIEW" if (
    job["status"] == "PASS" and job["exit_code"] == 0 and job["cleanup_confirmed"] is True
    and output.is_file() and "record hp0_handshakes" in output.read_text(encoding="utf-8")
    and sha(dcp) == record["routed_dcp_sha256"]
) else "FAIL"
if output.is_file():
    record["output_sha256"] = sha(output)
with (RUN / "result.json").open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
print(record["status"])
sys.exit(0 if record["status"].startswith("PASS_") else 1)
