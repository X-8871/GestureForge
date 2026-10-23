from __future__ import annotations
import json
from pathlib import Path
import sys
from scripts.stage4_s4b import s4b_ps_tensor_adapter as adapter

out_dir = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B-G2-R2\r2_exec_20261023_01")
base = out_dir / "api_root_case"
if base.exists():
    raise RuntimeError(f"probe target already exists: {base}")
project_root = base / "project"
evidence_parent = project_root / "tmp" / "4" / "S4-B-REAL-02B"
evidence_parent.mkdir(parents=True)
hardware_run_id = "api_root_probe_r01"
evidence_dir = evidence_parent / hardware_run_id
manifest_path = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B\s4b_ps_tensor_adapter_20261023_r11\adapter_preparation.json")
prepared_data = {
    "project_root": str(project_root),
    "run_id": "offline_fake_r01",
    "artifact_identity": {
        "model_weights_sha256": "a" * 64,
        "model_manifest_sha256": "b" * 64,
        "derived_source_sha256": adapter.EXPECTED_DERIVED_SOURCE_SHA256,
        "boot_seed": 1,
        "session_first": 1,
        "session_last": 2,
    },
    "source_evidence": {
        "frozen_2b_manifest": {"path": str(json.loads(manifest_path.read_text(encoding="utf-8"))["source_evidence"]["frozen_2b_manifest"]["path"])}
    },
}
prepared = adapter.PreparedRun(out_dir / "fake_preparation.json", prepared_data)
auth = {
    "authorization_id": "FAKE_ONLY",
    "weight_sha256": prepared_data["artifact_identity"]["model_weights_sha256"],
    "tensor_sha256": "c" * 64,
}
gate = adapter.GateCheck(True, (), {"operator_authorization": auth}, {})

class Bomb:
    def __init__(self):
        object.__setattr__(self, "accesses", [])
    def __getattribute__(self, name):
        if name == "accesses":
            return object.__getattribute__(self, name)
        object.__getattribute__(self, "accesses").append(name)
        raise AssertionError(f"fake hardware object was accessed: {name}")

session = Bomb()
stream = Bomb()
original_validate = adapter.validate_preparation
original_gates = adapter.validate_hardware_gates
original_inputs = adapter._read_bound_run_inputs
try:
    adapter.validate_preparation = lambda path: prepared
    adapter.validate_hardware_gates = lambda p, run_id, files: gate
    adapter._read_bound_run_inputs = lambda *args: (
        b"fake-weight", b"fake-tensor",
        {"path": "fake-tensor", "sha256": auth["tensor_sha256"], "bytes": adapter.INPUT_BYTES,
         "source_id": "fake", "format": "INT8_CHW_416"})
    try:
        adapter.execute_prepared(
            prepared.path, hardware_run_id=hardware_run_id, gate_files={"fake": True},
            xsdb_session=session, uart_stream=stream,
            weight_path=Path("fake-weight"), tensor_path=Path("fake-tensor"),
            tensor_binding_path=Path("fake-binding"),
            rx_record_path=evidence_dir / "uart_rx.raw.bin",
            tx_header_record_path=evidence_dir / "uart_tx_headers.raw.bin",
            frame_id=17, width=640, height=480, repeat=1, core_timeout=1, drain_timeout=1)
    except adapter.AdapterError as error:
        expected_error = str(error)
    else:
        raise AssertionError("execute_prepared unexpectedly reached a return")
finally:
    adapter.validate_preparation = original_validate
    adapter.validate_hardware_gates = original_gates
    adapter._read_bound_run_inputs = original_inputs

result_path = evidence_dir / "adapter_hardware_result.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
assert session.accesses == [] and stream.accesses == []
assert result["status"] == "FAILED" and result["sdk_call_count"] == 0
assert result["uart_read_write_operations"] == 0
assert "仓库根路径变化" in expected_error
out = {
    "result_path": str(result_path),
    "expected_api_exception": expected_error,
    "result_status": result["status"],
    "sdk_call_count": result["sdk_call_count"],
    "uart_read_write_operations": result["uart_read_write_operations"],
    "xsdb_property_accesses": session.accesses,
    "uart_property_accesses": stream.accesses,
    "hardware_execution": result["hardware_execution"],
    "fake_only": True,
}
print(json.dumps(out, ensure_ascii=False, indent=2))
(out_dir / "r2_execute_api_root_probe.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

