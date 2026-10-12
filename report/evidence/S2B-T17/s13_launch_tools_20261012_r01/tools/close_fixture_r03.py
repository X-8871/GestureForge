"""只读核对已关闭夹具原流，补充包装字段错误；不补造未记录的原生码。"""
import json
from pathlib import Path
import runtime_consumer as c

W = Path(__file__).absolute().parent
D = W/"native_consumer_canary_r03"
rows, streams = c.complete(str(D/"consumer"/"consumption.jsonl"))
sup = json.loads((D/"supervision"/"supervisor_receipt.json").read_text(encoding="utf-8"))
guard = json.loads((D/"supervision"/"guard"/"guard_receipt.json").read_text(encoding="utf-8"))
receipt = json.loads((D/"consumer"/"consumer_receipt.json").read_text(encoding="utf-8"))
known = json.loads((D/"known_identity_terminal.json").read_text(encoding="utf-8"))
assert len(rows) == 4 and all(row["status"] == "CONSUMED_LIVE_READY" for row in rows[:3])
assert all(0 < row["actual_gap_seconds"] <= 10 for row in rows[1:])
assert rows[-1]["blocked_latched"] is True and receipt["native_exit_code"] == 2
assert sup["child_native_exit_code"] == 2 and sup["supervisor_exit_code"] == 2 and guard["status"] == "STOPPED"
assert all(row["same_identity_present"] is False for row in known["observations"])
output = {"status": "PASS_G1_FIXTURE_ONLY", "original_wrapper_native_exit_code": 1, "original_failure": "结果包装读取guard_receipt不存在的native_exit_code键，实际consumer/STOP断言已完成。",
          "consumer_native_exit_code": 2, "supervisor_native_exit_code": 2, "guard_native_exit_code": sup["child_native_exit_code"],
          "root_canary_native_exit_code": None, "live_rows_during_driver_wait": 3, "gaps": [row["actual_gap_seconds"] for row in rows],
          "consumption_binding": streams, "known_identity_readback": known, "complete_tree_terminal": "NOT_PROVEN", "continuous_peak_bytes": None,
          "no_native_canary_reexecution": True, "actual_ross_wait_executed": False, "production_source_freeze": "PENDING"}
with (W/"monitor_fixture_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(output, stream, ensure_ascii=False, indent=2); stream.write("\n")
print(json.dumps(output, ensure_ascii=False))
