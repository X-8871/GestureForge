import json
from pathlib import Path
from scripts.stage4_s4b import s4b_ps_tensor_adapter as adapter
from scripts.stage4_s4b import decode_s4b_ps_trace as decoder
from verification.test_s4b_ps_tensor_adapter import _valid_trace_header

out_dir = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B-G2-R2\r2_exec_20261023_01")
source = adapter.EXPECTED_DERIVED_SOURCE_SHA256
seed = 0x123456789ABCDEF
first, last = 0x100, 0x1FF
header = _valid_trace_header(source, seed, first, last)
records = bytes(adapter.TRACE_RECORDS_BYTES)
dump = adapter.pack_double_snapshot(
    header, records, header, records,
    expected_source_sha256=source, expected_boot_seed=seed,
    expected_session_first=first, expected_session_last=last)
decoded = decoder.decode_bytes(
    dump, expected_derived_source_sha256=source, expected_boot_seed=seed)
assert decoded["status"] == "PASS_DECODED_DOUBLE_READ_SNAPSHOT"
assert decoded["record_count"] == 0
assert decoded["header"]["last_run_status"] == 0
assert decoded["header"]["last_assigned_session_id"] == 0
fake_run_rows = [{"index": 0, "frame": 17, "sequence": 1,
                  "epoch": 9, "raw_response_sha256": "d" * 64}]
require_predicate = (
    decoded.get("status") == "PASS_DECODED_DOUBLE_READ_SNAPSHOT" and
    decoded.get("header", {}).get("derived_source_sha256") == source and
    decoded.get("header", {}).get("boot_seed") == seed)
assert len(fake_run_rows) == 1 and require_predicate
result_status = "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED" if require_predicate else "FAILED"
assert result_status == "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED"
out = {
    "fake_only": True,
    "hardware_used": False,
    "double_snapshot_bytes": len(dump),
    "decoder_status": decoded["status"],
    "decoder_record_count": decoded["record_count"],
    "trace_last_run_status": decoded["header"]["last_run_status"],
    "trace_last_assigned_session_id": decoded["header"]["last_assigned_session_id"],
    "fake_uart_receipt_rows": len(fake_run_rows),
    "actual_adapter_final_predicate_accepts": require_predicate,
    "result_status_under_current_final_predicate": result_status,
    "conclusion": "header validator/decoder accept a fresh no-run log and adapter final predicate can call it captured without correlating trace records to UART run rows"
}
(out_dir / "r2_empty_trace_claim_probe.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(out, ensure_ascii=False, indent=2))