from __future__ import annotations
import copy, hashlib, json, os, struct, subprocess, sys, zlib
from pathlib import Path

worktree = Path(r"D:\codex-worktrees\w4")
out_dir = Path(r"D:\codex-worktrees\w4\tmp\4\S4-B-REAL-02B-G2-R2\r2_repair1_20261023_1748_01")
prep_path = Path(os.environ["S4B_ADAPTER_TEST_PREPARATION"])
sys.path.insert(0, str(worktree))
from scripts.stage4_s4b import s4b_ps_tensor_adapter as adapter
from scripts.stage4_s4b import decode_s4b_ps_trace as decoder
from verification import test_s4b_ps_tensor_adapter as fixtures

base = adapter.validate_preparation(prep_path)
base_data = copy.deepcopy(base.data)
identity = base_data["artifact_identity"]
real_run = adapter.validate_preparation
real_subprocess_run = subprocess.run
decoder_call = 0

def isolated_subprocess_run(*args, **kwargs):
    global decoder_call
    decoder_call += 1
    child_temp = out_dir / f"decoder_temp_{decoder_call:02d}"
    child_temp.mkdir()
    env = dict(os.environ)
    env["TEMP"] = str(child_temp)
    env["TMP"] = str(child_temp)
    env["PYTHONUTF8"] = "1"
    kwargs["env"] = env
    return real_subprocess_run(*args, **kwargs)

adapter.subprocess.run = isolated_subprocess_run

def make_prepared(project_root: Path, tag: str):
    project_root.mkdir()
    (project_root / "tmp" / "4" / "S4-B-REAL-02B").mkdir(parents=True)
    data = copy.deepcopy(base_data)
    data["project_root"] = str(project_root)
    data["run_id"] = "prepared_" + tag
    return adapter.PreparedRun(base.path, data)

def run_fake(project_root: Path, *, bad_idle: bool):
    prepared = make_prepared(project_root, "bad_idle" if bad_idle else "success")
    adapter.validate_preparation = lambda _path: prepared
    try:
        test_case = fixtures.AdapterFakeExecuteTests()
        return test_case._run_fake(bad_idle=bad_idle)
    finally:
        adapter.validate_preparation = real_run

fake_results = {}
result, controller, evidence = run_fake(out_dir / "fake_success_project", bad_idle=False)
assert result is not None and result["status"] == "ACTUAL_PS_TENSOR_DIAGNOSTIC_CAPTURED"
assert result["trace_uart_join"]["status"] == "PASS_EXACT_TRACE_UART_JOIN"
assert result["trace_dump"]["decoder_status"] == "PASS_DECODED_DOUBLE_READ_SNAPSHOT"
assert "cpu0.stop.after_safe_point" in controller.record["calls"]
assert controller.states == {"cpu0": "Stopped", "cpu1": "Stopped"}
fake_results["full_success"] = {
    "status": result["status"],
    "join": result["trace_uart_join"]["status"],
    "decoder": result["trace_dump"]["decoder_status"],
    "cpu_states_after_owned_stop": controller.states,
    "evidence_dir": str(evidence),
    "uart_rx_bytes": (evidence / "uart_rx.raw.bin").stat().st_size,
    "raw_weight_response": (evidence / "weights_response.raw.bin").is_file(),
    "raw_run_response": (evidence / "run_response_0000.raw.bin").is_file(),
    "decoder_child_temp": str(out_dir / "decoder_temp_01"),
}
result, controller, evidence = run_fake(out_dir / "fake_bad_idle_project", bad_idle=True)
assert result is None and "cpu0.stop.after_safe_point" not in controller.record["calls"]
assert controller.states == {"cpu0": "Running", "cpu1": "Stopped"}
fake_results["invalid_idle_pre_stop"] = {
    "adapter_result": None,
    "cpu0_stop_called": "cpu0.stop.after_safe_point" in controller.record["calls"],
    "cpu_states": controller.states,
    "evidence_dir": str(evidence),
}

state_flip = {}
prepared = make_prepared(out_dir / "fake_state_flip_project", "state_flip")
adapter.validate_preparation = lambda _path: prepared
original_wait = adapter._wait_for_safe_idle

def wait_then_flip(controller_arg, *args, **kwargs):
    snapshot = original_wait(controller_arg, *args, **kwargs)
    state_flip["controller"] = controller_arg
    original_stable = controller_arg.stable_csr
    def changed_after_stop(label):
        current = original_stable(label)
        if label == "after_owned_cpu0_stop":
            current = dict(current)
            current[0x00C] = 1
        return current
    controller_arg.stable_csr = changed_after_stop
    return snapshot

adapter._wait_for_safe_idle = wait_then_flip
try:
    test_case = fixtures.AdapterFakeExecuteTests()
    try:
        test_case._run_fake(bad_idle=False)
        state_flip["adapter_error"] = None
    except adapter.AdapterError as error:
        state_flip["adapter_error"] = str(error)
finally:
    adapter._wait_for_safe_idle = original_wait
    adapter.validate_preparation = real_run
flip_controller = state_flip["controller"]
state_flip["cpu0_stop_called_before_changed_snapshot_was_rejected"] = (
    "cpu0.stop.after_safe_point" in flip_controller.record["calls"])
state_flip["cpu_states_at_failure"] = flip_controller.states
assert state_flip["cpu0_stop_called_before_changed_snapshot_was_rejected"]
assert flip_controller.states["cpu0"] == "Stopped"
fake_results["status_change_after_safe_wait"] = state_flip

source = str(identity["derived_source_sha256"])
seed = int(identity["boot_seed"])
first = int(identity["session_first"])
last = int(identity["session_last"])
frame = 700
repeat = 1
sequence = 2
epoch = 5
input_crc = 0x1234ABCD
terminal = (adapter.TRACE_CSR_DONE_SAFE | adapter.TRACE_CSR_HEAD_VALID |
            adapter.TRACE_CSR_SAFE_REUSE | adapter.TRACE_CSR_TERMINAL)
header = fixtures._completed_trace_header(identity, sequence, frame, repeat)
record = fixtures._successful_trace_record(first, frame, 1, 0, sequence,
                                            input_crc, epoch, terminal)
records = record + bytes(adapter.TRACE_RECORDS_BYTES - len(record))
meta = {"epoch": epoch, "phys_status": terminal, "error_code": 0,
        "last_reject": 0, "box_count": 0, "raw_candidate_count": 0,
        "response_code": 0, "index": 0, "total": repeat}
receipt = {"meta": meta, "index": 0, "frame": frame, "sequence": sequence,
           "epoch": epoch, "input_crc32": input_crc,
           "input_bytes": adapter.INPUT_BYTES, "input_format": "INT8_CHW_416"}

def crc_header(words):
    raw = bytearray(struct.pack("<36I", *words))
    words[35] = zlib.crc32(raw[:140]) & 0xFFFFFFFF
    return struct.pack("<36I", *words)

def crc_record(words):
    raw = bytearray(struct.pack("<46I", *words))
    words[45] = zlib.crc32(raw[:180]) & 0xFFFFFFFF
    return struct.pack("<46I", *words)

def join_status(label, hdr, recs, rows, *, seq=sequence, frm=frame):
    try:
        value = adapter._validate_trace_uart_join(
            hdr, recs, rows, identity=identity, uart_sequence=seq,
            frame_id=frm, repeat=repeat, input_crc32=input_crc)
        return {"accepted": True, "status": value["status"]}
    except adapter.AdapterError as error:
        return {"accepted": False, "error": str(error)}

join_results = {}
join_results["valid_current_run"] = join_status("valid", header, records, [receipt])
assert join_results["valid_current_run"]["accepted"]
join_results["empty_no_run"] = join_status(
    "empty", fixtures._valid_trace_header(source, seed, first, last),
    bytes(adapter.TRACE_RECORDS_BYTES), [receipt])
assert not join_results["empty_no_run"]["accepted"]
old_header = fixtures._completed_trace_header(identity, sequence - 1, frame - 1, repeat)
old_record = fixtures._successful_trace_record(first, frame - 1, 1, 0,
                                                sequence - 1, input_crc, epoch, terminal)
old_records = old_record + bytes(adapter.TRACE_RECORDS_BYTES - len(old_record))
join_results["stale_previous_run"] = join_status("stale", old_header, old_records, [receipt])
assert not join_results["stale_previous_run"]["accepted"]
incomplete_words = list(struct.unpack("<36I", header))
incomplete_words[18] = 2
incomplete_header = crc_header(incomplete_words)
join_results["incomplete_run_status_2"] = join_status("incomplete", incomplete_header, records, [receipt])
assert not join_results["incomplete_run_status_2"]["accepted"]
wrong_epoch_words = list(struct.unpack("<46I", record))
wrong_epoch_words[31] = epoch + 1
wrong_epoch_record = crc_record(wrong_epoch_words)
wrong_epoch_records = wrong_epoch_record + bytes(adapter.TRACE_RECORDS_BYTES - len(wrong_epoch_record))
join_results["record_epoch_mismatch"] = join_status("epoch", header, wrong_epoch_records, [receipt])
assert not join_results["record_epoch_mismatch"]["accepted"]
wrong_receipt = dict(receipt)
wrong_receipt["sequence"] = sequence + 1
join_results["receipt_sequence_mismatch"] = join_status("receipt", header, records, [wrong_receipt])
assert not join_results["receipt_sequence_mismatch"]["accepted"]
changed_initial = adapter._validate_empty_trace_header(
    fixtures._valid_trace_header(source, seed, first, last), identity)
assert changed_initial[5] == 0
try:
    adapter._validate_empty_trace_header(header, identity)
    stale_pre_run_rejected = False
except adapter.AdapterError:
    stale_pre_run_rejected = True
assert stale_pre_run_rejected
join_results["stale_pre_run_rejected"] = stale_pre_run_rejected

dump = adapter.pack_double_snapshot(
    header, records, header, records,
    expected_source_sha256=source, expected_boot_seed=seed,
    expected_session_first=first, expected_session_last=last)
decoded = decoder.decode_bytes(dump, expected_derived_source_sha256=source,
                               expected_boot_seed=seed)
assert decoded["status"] == "PASS_DECODED_DOUBLE_READ_SNAPSHOT"
join_results["valid_decoder_status"] = decoded["status"]

# 检查ACK epoch和CSR frame变更都会使有限等待拒绝状态。
class PollController:
    def __init__(self, csr, hdr):
        self.csr = csr
        self.hdr = hdr
    def stable_csr(self, _label):
        return dict(self.csr)
    def words(self, _address, count):
        return list(struct.unpack("<" + "I" * count, self.hdr[:count * 4]))

def poll_csr(*, ack_epoch=epoch, current_epoch=epoch, csr_frame=frame, state=adapter.TRACE_CSR_SAFE_REUSE):
    return {
        0x00C: state, 0x010: 0,
        0x050: current_epoch & 0xFFFFFFFF, 0x054: current_epoch >> 32,
        0x05C: ack_epoch & 0xFFFFFFFF, 0x060: ack_epoch >> 32,
        0x058: csr_frame,
    }

wait_results = {}
for name, csr in [
    ("valid_idle_ack_epoch_frame", poll_csr()),
    ("ack_epoch_mismatch", poll_csr(ack_epoch=epoch - 1)),
    ("current_epoch_mismatch", poll_csr(current_epoch=epoch + 1)),
    ("frame_mismatch", poll_csr(csr_frame=frame + 1)),
    ("owner_pending_unsafe", poll_csr(state=adapter.TRACE_CSR_SAFE_REUSE | adapter.TRACE_CSR_OWNER_PL)),
]:
    poll = PollController(csr, header)
    try:
        adapter._wait_for_safe_idle(
            poll, identity, uart_sequence=sequence, frame_id=frame, repeat=repeat,
            expected_epoch=epoch,
            header_address=base.data["memory_ranges"]["trace_header"]["start"],
            timeout_seconds=0.004, poll_interval_seconds=0.001)
        wait_results[name] = {"accepted": True}
    except adapter.AdapterError as error:
        wait_results[name] = {"accepted": False, "error": str(error)}
for name in ("valid_idle_ack_epoch_frame",):
    assert wait_results[name]["accepted"]
for name in ("ack_epoch_mismatch", "current_epoch_mismatch", "frame_mismatch", "owner_pending_unsafe"):
    assert not wait_results[name]["accepted"]

output = {
    "run_id": out_dir.name,
    "hardware_used": False,
    "prepared_input": str(prep_path),
    "source_sha256": hashlib.sha256((worktree / "scripts/stage4_s4b/s4b_ps_tensor_adapter.py").read_bytes()).hexdigest(),
    "test_sha256": hashlib.sha256((worktree / "verification/test_s4b_ps_tensor_adapter.py").read_bytes()).hexdigest(),
    "fake_execute": fake_results,
    "trace_join_variants": join_results,
    "idle_ack_frame_variants": wait_results,
    "decoder_subprocesses": decoder_call,
}
out_path = out_dir / "r2_repair1_probe_results.json"
out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(output, ensure_ascii=False, indent=2))