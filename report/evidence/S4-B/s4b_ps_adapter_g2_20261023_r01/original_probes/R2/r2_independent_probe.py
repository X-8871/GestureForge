from __future__ import annotations
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import sys
import zlib

from scripts.stage4_s4b import s4b_ps_tensor_adapter as adapter

out_dir = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B-G2-R2\r2_exec_20261023_01")
out = {"run_id": "r2_exec_20261023_01", "real_hardware_used": False}
prep_path = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B\s4b_ps_tensor_adapter_20261023_r11\adapter_preparation.json")
prep = json.loads(prep_path.read_text(encoding="utf-8"))
manifest_path = Path(prep["source_evidence"]["frozen_2b_manifest"]["path"])
computed_root = manifest_path.parents[3]
actual_root = manifest_path.parents[4]
try:
    adapter._frozen_tool_blobs(computed_root)
except adapter.AdapterError as error:
    out["frozen_repo_root_probe"] = {
        "computed_from_parents_3": str(computed_root),
        "actual_git_root_from_parents_4": str(actual_root),
        "computed_root_rejected": True,
        "error": str(error),
    }
else:
    raise AssertionError("parents[3] unexpectedly accepted as Git root")
blobs = adapter._frozen_tool_blobs(actual_root)
out["frozen_blob_positive_control"] = {
    "git_root": str(actual_root),
    "commit": adapter.FROZEN_2B_COMMIT,
    "files": {name: hashlib.sha256(raw).hexdigest() for name, raw in blobs.items()},
    "all_hashes_match": all(hashlib.sha256(raw).hexdigest() == adapter.FROZEN_TOOL_SHA256[name]
                            for name, raw in blobs.items()),
}
assert out["frozen_blob_positive_control"]["all_hashes_match"]

source = adapter.EXPECTED_DERIVED_SOURCE_SHA256
seed = 0x5342424F4F543132
first, last = 0x53422800, 0x53422BE7
words = [0] * 36
words[0] = adapter.TRACE_MAGIC
words[1] = adapter.TRACE_SCHEMA_VERSION
words[2] = adapter.TRACE_HEADER_BYTES
words[3] = adapter.TRACE_RECORD_BYTES
words[4] = adapter.TRACE_CAPACITY
words[6], words[7] = seed & 0xFFFFFFFF, seed >> 32
words[8], words[9], words[10] = first, last, first
words[25], words[26] = 1, 1
words[27:35] = [int(source[i:i + 8], 16) for i in range(0, 64, 8)]
header = bytearray(struct.pack("<36I", *words))
words[35] = zlib.crc32(header[:140]) & 0xFFFFFFFF
header = struct.pack("<36I", *words)
records = bytes(adapter.TRACE_RECORDS_BYTES)
packed = adapter.pack_double_snapshot(
    header, records, header, records, expected_source_sha256=source,
    expected_boot_seed=seed, expected_session_first=first, expected_session_last=last)
assert len(packed) == adapter.DUMP_HEADER.size + 2 * adapter.TRACE_SNAPSHOT_BYTES == 368316
out["snapshot_layout_positive"] = {
    "header_bytes": adapter.TRACE_HEADER_BYTES,
    "record_bytes": adapter.TRACE_RECORD_BYTES,
    "capacity": adapter.TRACE_CAPACITY,
    "record_region_bytes": len(records),
    "snapshot_bytes": adapter.TRACE_SNAPSHOT_BYTES,
    "dump_bytes": len(packed),
}
try:
    adapter.pack_double_snapshot(
        header, records, header, records[:-1] + b"\x01",
        expected_source_sha256=source, expected_boot_seed=seed,
        expected_session_first=first, expected_session_last=last)
except adapter.AdapterError as error:
    out["snapshot_mismatch_negative"] = {"rejected": True, "error": str(error)}
else:
    raise AssertionError("unstable record snapshots were accepted")

spec = importlib.util.spec_from_file_location(
    "review_probe_transport", r"D:\FPGA_Competition\w2b\verification\s2b_board_transport.py")
transport = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = transport
spec.loader.exec_module(transport)

class FakeStream:
    def __init__(self, raw):
        self.raw = bytearray(raw)
        self.writes = []
        self.read_calls = 0
    def write(self, raw):
        self.writes.append(bytes(raw))
        return len(raw)
    def read(self, count):
        self.read_calls += 1
        result = bytes(self.raw[:count])
        del self.raw[:count]
        return result

def response_for(request, epoch, frame):
    status = 4 | (1 << 9) | (1 << 10) | (1 << 11)
    payload = transport.META.pack(epoch, status, 0, 0, 0, 0, 0, request.repeat, 0)
    payload += bytes(sum(transport.HEAD_LENGTHS.values()))
    response = transport.Header(
        request.op | 0x8000, request.sequence, frame, request.width, request.height,
        request.repeat, len(payload), zlib.crc32(payload)).pack()
    return response + payload

request_payload = struct.pack("<II", 1, 1) + bytes(transport.INPUT_BYTES)
request, request_header = transport.make_request(
    transport.OP_RUN, 1, 17, request_payload, width=640, height=480, repeat=1)
valid_raw = response_for(request, 1, request.frame)
stream = FakeStream(valid_raw)
wire = transport.WireSession(stream, io.BytesIO(), io.BytesIO(), response_timeout=0.1)
wire.send(request, request_header, request_payload, {"kind": "fake_probe"})
parsed = wire.receive(request, 0)
assert parsed[0]["epoch"] == 1 and len(parsed[1]["head13"]) == 5070 and len(parsed[1]["head26"]) == 20280
out["wire_response_positive"] = {
    "epoch": parsed[0]["epoch"],
    "head13_bytes": len(parsed[1]["head13"]),
    "head26_bytes": len(parsed[1]["head26"]),
    "send_write_calls": len(stream.writes),
    "wire_failed": wire.failed,
}
for label, raw in (
    ("wrong_epoch", response_for(request, 2, request.frame)),
    ("wrong_frame", response_for(request, 1, request.frame + 1)),
):
    fake = FakeStream(raw)
    rejected = transport.WireSession(fake, io.BytesIO(), io.BytesIO(), response_timeout=0.1)
    rejected.send(request, request_header, request_payload, {"kind": "fake_negative"})
    write_count = len(fake.writes)
    try:
        rejected.receive(request, 0)
    except transport.TransportError as error:
        assert rejected.failed and len(fake.writes) == write_count
        out[f"wire_{label}_negative"] = {
            "rejected": True, "failed_latched": rejected.failed,
            "extra_writes_after_failure": len(fake.writes) - write_count,
            "error": str(error),
        }
    else:
        raise AssertionError(f"{label} response was accepted")
timeout_stream = FakeStream(b"")
timeout_wire = transport.WireSession(timeout_stream, io.BytesIO(), io.BytesIO(), response_timeout=0.005)
timeout_wire.send(request, request_header, request_payload, {"kind": "fake_timeout"})
timeout_writes = len(timeout_stream.writes)
try:
    timeout_wire.receive(request, 0)
except transport.TransportError as error:
    assert timeout_wire.failed and len(timeout_stream.writes) == timeout_writes
    out["wire_timeout_negative"] = {
        "rejected": True, "failed_latched": timeout_wire.failed,
        "extra_writes_after_failure": len(timeout_stream.writes) - timeout_writes,
        "error": str(error),
    }
else:
    raise AssertionError("empty-stream timeout was accepted")

result_path = out_dir / "r2_independent_probe_results.json"
result_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(out, ensure_ascii=False, indent=2))
print(f"result_path={result_path}")
