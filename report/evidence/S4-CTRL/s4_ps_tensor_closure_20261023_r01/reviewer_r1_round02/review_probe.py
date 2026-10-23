import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path("D:/codex-worktrees/w4")
sys.path.insert(0, str(ROOT))
from scripts.stage4_s4b import build_s4b_ps_tensor as builder
from verification.test_s4b_ps_tensor import synthetic_memory_map

snapshot_path = ROOT / "report/evidence/S4-CTRL/s4_ps_tensor_closure_20261023_r01/frozen_sources_r02.json"
snapshot_bytes = snapshot_path.read_bytes()
snapshot_sha = hashlib.sha256(snapshot_bytes).hexdigest()
assert snapshot_sha == "dc87596dbcae6bd539c23a821d726fbb9d155c824acbc03ac7d61cd643dd0348"
snapshot = json.loads(snapshot_bytes.decode("utf-8"))
bad_sources = []
for item in snapshot["files"]:
    p = ROOT / item["path"]
    if not p.is_file():
        bad_sources.append((item["path"], "missing"))
    elif hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]:
        bad_sources.append((item["path"], "sha_mismatch"))
assert not bad_sources, bad_sources
print("frozen_manifest_sha256=" + snapshot_sha)
print("frozen_source_files=%d mismatches=%d" % (len(snapshot["files"]), len(bad_sources)))

delivery_path = ROOT / "report/evidence/S4-B/s4b_ps_tensor_20261023_r11/delivery_manifest.json"
delivery_bytes = delivery_path.read_bytes()
delivery_sha = hashlib.sha256(delivery_bytes).hexdigest()
assert delivery_sha == "620878850e996dcd8a7e9214b4eb3b5e4219380f907be45bc35a3b0f5ef8b601"
delivery = json.loads(delivery_bytes.decode("utf-8"))
bad_delivery = []
for item in delivery["files"]:
    p = (ROOT / item["path"]).resolve()
    if not p.is_relative_to(ROOT.resolve()):
        bad_delivery.append((item["path"], "outside_root"))
    elif not p.is_file():
        bad_delivery.append((item["path"], "missing"))
    elif hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]:
        bad_delivery.append((item["path"], "sha_mismatch"))
assert not bad_delivery, bad_delivery
print("r11_delivery_manifest_sha256=" + delivery_sha)
print("r11_delivery_files=%d mismatches=%d source_commit=%s" %
      (len(delivery["files"]), len(bad_delivery), delivery["source_commit"]))
machine = json.loads((delivery_path.parent / "machine_result.json").read_text(encoding="utf-8"))
assert machine["status"] == "PASS_BUILD_ONLY"
print("machine_status=" + machine["status"])
print("hardware_check=" + next(c["status"] for c in delivery["checks"] if c["name"] == "hardware_board_ps_pl_uart"))
print("rgb_check=" + next(c["status"] for c in delivery["checks"] if c["name"] == "rgb_preprocessing"))

bad_paths = [
    ".." + chr(92) + "escape.bin",
    "C:/escape.bin",
    chr(92) * 2 + "server" + chr(92) + "share" + chr(92) + "escape.bin",
    "/absolute.bin",
    "bundle/workspace/../../escape.bin",
    "bundle/workspace/C:/escape.bin",
    "bundle/workspace/foo./bar",
    "bundle/workspace/foo /bar",
]
path_results = []
for name in bad_paths:
    try:
        builder.validate_bundle_member(name)
        path_results.append((name, "ACCEPTED"))
    except builder.BuildError:
        path_results.append((name, "REJECTED"))
assert all(result == "REJECTED" for _, result in path_results), path_results
assert builder.validate_bundle_member("bundle/workspace/nested/safe.txt").as_posix() == "bundle/workspace/nested/safe.txt"
original_mkdir = Path.mkdir
original_write_bytes = Path.write_bytes
def deny_write(*args, **kwargs):
    raise AssertionError("unexpected filesystem write during preflight probe")
Path.mkdir = deny_write
Path.write_bytes = deny_write
try:
    preflight_results = []
    probe_destination = ROOT / "tmp/4/S4-B-REAL-G2-R1-02/codex_review_r1_02_20261023_01/no_write_target"
    for name in bad_paths:
        try:
            builder.extract_members(
                {"bundle/workspace/safe.txt": b"safe", name: b"must-not-write"},
                probe_destination,
            )
            preflight_results.append((name, "ACCEPTED"))
        except builder.BuildError:
            preflight_results.append((name, "REJECTED_BEFORE_WRITE"))
    assert all(result == "REJECTED_BEFORE_WRITE" for _, result in preflight_results), preflight_results
finally:
    Path.mkdir = original_mkdir
    Path.write_bytes = original_write_bytes
print("path_rejections=" + repr(path_results))
print("extract_preflight=" + repr(preflight_results))
print("valid_path=ACCEPTED")

nm_text, sections_text, symbols = synthetic_memory_map()
ranges = builder.verify_memory_map(nm_text, sections_text)
assert ranges["stack"]["size_bytes"] == 71680
assert ranges["thread_stack"]["size_bytes"] == 65536
assert {name: item["size_bytes"] for name, item in ranges["exception_stacks"].items()} == {
    "IRQ": 1024, "SVC": 2048, "ABT": 1024, "FIQ": 1024, "UND": 1024
}
print("stack_positive=%s" % json.dumps({
    "full_stack": ranges["stack"]["size_bytes"],
    "thread_stack": ranges["thread_stack"]["size_bytes"],
    "exception_stacks": {name: item["size_bytes"] for name, item in ranges["exception_stacks"].items()},
}, sort_keys=True))
missing = chr(10).join(line for line in nm_text.splitlines() if not line.endswith("__irq_stack"))
try:
    builder.verify_memory_map(missing, sections_text)
    raise AssertionError("missing exception stack symbol was accepted")
except builder.BuildError as exc:
    assert "__irq_stack" in str(exc)
    print("missing_stack_symbol=REJECTED:" + str(exc))
stack_names = {
    "_stack_end", "_stack", "__stack", "_irq_stack_end", "__irq_stack",
    "_supervisor_stack_end", "__supervisor_stack", "_abort_stack_end",
    "__abort_stack", "_fiq_stack_end", "__fiq_stack", "_undef_stack_end",
    "__undef_stack",
}
delta = 0x02000000
shifted = chr(10).join(
    f"{int(parts[0], 16) + (delta if parts[-1] in stack_names else 0):08x} " + " ".join(parts[1:])
    for parts in (line.split() for line in nm_text.splitlines())
)
try:
    builder.verify_memory_map(shifted, sections_text)
    raise AssertionError("out-of-bounds complete stack was accepted")
except builder.BuildError as exc:
    assert "heap/stack范围越出" in str(exc)
    print("stack_oob=REJECTED:" + str(exc))
print("probe_result=PASS")
