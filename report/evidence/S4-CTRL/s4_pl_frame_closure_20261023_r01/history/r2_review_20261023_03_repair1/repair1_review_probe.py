from pathlib import Path
import hashlib
import json
import math
import re
import struct

root = Path(r"D:\codex-worktrees\w4")
review = root / "tmp/4/S4B-PL-FRAME-01/r2_review_20261023_03_repair1"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def need(condition, message):
    if not condition:
        raise AssertionError(message)

freeze_path = root / "report/evidence/S4-B/s4b_pl_frame_g2_20261023_r02/frozen_sources.json"
freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
need(sha(freeze_path) == "490aff4f087d8db8aa725b198210b7198d49a0d7cad6fb3e73c288f263a369d5", "freeze SHA")
need(freeze["baseline_commit"] == "d4f30e35937efed07c4f3ff62393e2e3a6a2ebdc", "baseline")
for item in freeze["sources"]:
    live = root / item["source_path"]
    snap = Path(item["snapshot_path"])
    need(sha(live) == item["sha256"], f"live source SHA: {item['source_path']}")
    need(sha(snap) == item["sha256"], f"snapshot SHA: {item['source_path']}")
    need(live.stat().st_size == item["bytes"] == snap.stat().st_size, f"source bytes: {item['source_path']}")

run_path = root / "report/evidence/S4-B/s4b_pl_frame_20261023_r08/run_manifest.json"
run = json.loads(run_path.read_text(encoding="utf-8"))
need(sha(run_path) == freeze["run_manifest_sha256"] == "c9ab2e5cf75f60d6e2b90ec06e819a5439e68bbcb5ea81a8f745887757bc49c5", "run manifest SHA")
need(run["vivado"]["native_exit_code"] == 0 and run["vivado"]["part"] == "xc7z020clg400-2", "run result/part")
need(run["vivado"]["elapsed_seconds"] == 17.459 and run["vivado"]["cycles"] == 30898 and run["vivado"]["finish_sim_time_ns"] == 308980, "run metrics")
need("weight_accept=4 weight_reject=4" in run["vivado"]["pass_line"], "pass line weight counts")
for src in run["source_files"]:
    frozen = next(s for s in freeze["sources"] if s["source_path"] == src["path"])
    need(src["current_sha256"] == frozen["sha256"], f"run/current source SHA: {src['path']}")

inventory_path = root / "report/evidence/S4-CTRL/s4_pl_frame_closure_20261023_r01/r08_artifact_inventory.json"
inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
need(len(inventory["files"]) == 17, "artifact count")
for item in inventory["files"]:
    archived = root / item["archive_path"]
    need(sha(archived) == item["sha256"], f"archive SHA: {item['archive_path']}")
    original = Path(item["original_path"])
    if original.exists():
        need(sha(original) == item["sha256"], f"original SHA: {item['original_path']}")
sim_artifact = root / "report/evidence/S4-CTRL/s4_pl_frame_closure_20261023_r01/artifacts_r08/simulate.log"
sim = sim_artifact.read_text(encoding="utf-8")
need(sha(sim_artifact) == "60b1e05984efb4ab6abad79743bbba077aabaf88e84bf5979f7c996b1fa0e569", "simulation log SHA")
need("TEST_PASS small_cases=2 descriptor_overlap=1 geometry_fault=1 weight_accept=4 weight_reject=4 raw_error=1 write_error=1 large_prefix_bytes=88 abort=1 unsolicited_response=1 seed=20261023 cycles=30898" in sim, "simulation pass line")
need("$finish called at time : 308980 ns" in sim and "fatal" not in sim.lower(), "simulation finish/fatal")

frame_path = root / "src/s4b_preproc_frame.sv"
pixel_path = root / "src/s4b_preproc_pixel.sv"
frame = frame_path.read_text(encoding="utf-8")
pixel = pixel_path.read_text(encoding="utf-8")
frame_match = re.search(r"FP64_MIN_WEIGHT_MAG\s*=\s*63'h([0-9a-fA-F]+)", frame)
pixel_match = re.search(r"FP64_MIN_GEOMETRY_WEIGHT\s*=\s*64'h([0-9a-fA-F]+)", pixel)
need(frame_match is not None and pixel_match is not None, "threshold declarations")
frame_min = int(frame_match.group(1), 16)
pixel_min = int(pixel_match.group(1), 16)
need(frame_min == pixel_min == 0x3ca0000000000000, "frame/pixel threshold mismatch")
need(struct.unpack(">Q", struct.pack(">d", math.ldexp(1.0, -53)))[0] == frame_min, "2^-53 encoding")
one = 0x3ff0000000000000
def accepts(bits):
    mag = bits & ((1 << 63) - 1)
    exponent = (bits >> 52) & 0x7ff
    if mag == 0:
        return (bits >> 63) == 0
    return not ((bits >> 63) or exponent == 0 or exponent == 0x7ff or mag < frame_min or mag > one)
cases = {
    "positive_zero": (0x0000000000000000, True),
    "minimum_2^-53": (0x3ca0000000000000, True),
    "nextafter_below": (0x3c9fffffffffffff, False),
    "2^-100": (0x39b0000000000000, False),
    "one": (0x3ff0000000000000, True),
}
for name, (bits, expected) in cases.items():
    actual = accepts(bits)
    need(actual == expected, f"predicate case {name}: {actual}")

TB = (root / "sim/tb_s4b_preproc_frame.sv").read_text(encoding="utf-8")
pattern = re.compile(r"exercise_weight_domain\(1'b([01]),\s*64'h([0-9a-f]{16}),\s*1'b([01]),\s*(\d+)\);", re.IGNORECASE)
calls = [(int(a), int(v, 16), int(ok), int(n)) for a, v, ok, n in pattern.findall(TB)]
expected = {
    (0, 0x0000000000000000, 1, 24), (1, 0x0000000000000000, 1, 24),
    (0, 0x3ca0000000000000, 1, 24), (1, 0x3ca0000000000000, 1, 24),
    (0, 0x3c9fffffffffffff, 0, 3), (1, 0x3c9fffffffffffff, 0, 15),
    (0, 0x39b0000000000000, 0, 3), (1, 0x39b0000000000000, 0, 15),
}
need(len(calls) == 8 and set(calls) == expected, "eight X/Y cases")
for token in [
    "if (sm_error_valid || small_dut.state_q !== SMALL_ST_RAW_REQ)",
    "small_raw_read_count - raw_before != 1",
    "small_dut.pixel_busy || small_dut.pixel_out_valid || small_dut.pixel_error_valid",
    "sm_error_code !== 4'd4",
    "sm_error_address !== table_base + 32'd16",
    "small_raw_read_count != raw_before || small_write_count != writes_before",
]:
    need(token in TB, f"test assertion missing: {token}")

print(f"freeze_sha={sha(freeze_path)}")
print(f"r02_manifest_sha={sha(run_path)}")
print("live_and_snapshot_sources=4/4 MATCH")
print("r08_archived_artifacts=17/17 MATCH; originals_present_and_matching where available")
print(f"r08_simulate_sha={sha(sim_artifact)}")
print(f"threshold=0x{frame_min:016x}; independent_predicate_cases={len(cases)}/5 PASS")
print(f"X/Y_weight_cases={len(calls)}/8 PASS; assertions_checked=6")
print("result=PASS_STATIC_BINDING_AND_WEIGHT_BOUNDARIES")
