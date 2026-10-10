#!/usr/bin/env python3
"""独立审查：只读被审文件，所有验证产物仅写隔离临时目录。"""
from pathlib import Path
from bisect import bisect_right
from collections import Counter
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
SEED = 0x10092B77

def sha(path):
    """返回原始字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    """保存 UTF-8 机器可读审查证据。"""
    (BASE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

spec = importlib.util.spec_from_file_location("reviewed_runner", ROOT / "verification/test_s2b_request_guard_rtl.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
model = json.loads((ROOT / runner.MODEL).read_text(encoding="utf-8"))
assert sha(ROOT / runner.MODEL) == runner.MODEL_SHA
objects = [(v["address"], v["address"] + v["length_bytes"], False, k)
           for k, v in model["address_map"].items() if k in ("input", "weight_package")]
objects += [(v["tensor_address"], v["tensor_address"] + v["tensor_length_bytes"], True,
             "layer" + str(v["layer_index"])) for v in model["layers"] if v["op"] != "yolo"]
objects.sort()
assert len(objects) == 38 and sum(v[2] for v in objects) == 36
assert all(a[1] <= b[0] for a, b in zip(objects, objects[1:]))
starts = [v[0] for v in objects]
rtl = (ROOT / runner.SOURCES[0]).read_text(encoding="utf-8")
for label, expected in (("OBJECT_BEGIN", starts), ("OBJECT_END", [v[1] for v in objects])):
    body = re.search(label + r".*?= '\{(.*?)\};", rtl, re.S).group(1)
    actual = [int(v, 16) for v in re.findall(r"32'h([0-9A-Fa-f]+)", body)]
    assert actual == expected, label
for h in model["address_map"]["heads"]:
    source = next(v for v in model["layers"] if v["layer_index"] == h["source_convolution_layer_index"])
    view = next(v for v in model["layers"] if v["layer_index"] == h["yolo_layer_index"])
    assert source["tensor_address"] == view["tensor_address"] == h["address"]
    assert source["tensor_length_bytes"] == view["tensor_length_bytes"] == h["length_bytes"]

def oracle(request):
    """二分查找最小选中字节对象，再比较最大选中字节，不逐对象逐lane搜索。"""
    write, address, read_mask, write_mask = request
    active = write_mask if write else read_mask
    opposite = read_mask if write else write_mask
    if address & 3 or active == 0 or opposite:
        return (0, 0, 1)
    physical = address + 0x10000000
    if physical >> 32 or physical < 0x10000000 or physical >= 0x12000000:
        return (0, 0, 2)
    minimum = address + (active & -active).bit_length() - 1
    maximum = address + active.bit_length() - 1
    index = bisect_right(starts, minimum) - 1
    if index < 0:
        return (0, 0, 2)
    begin, end, writable, _ = objects[index]
    if maximum >= end or write and not writable:
        return (0, 0, 2)
    return (1, physical, 0)

manual = [
    ((0, 0, 15, 0), (1, 0x10000000, 0)),
    ((1, 0, 0, 15), (0, 0, 2)),
    ((0, 0x00100000, 15, 0), (1, 0x10100000, 0)),
    ((1, 0x006A12F8, 0, 15), (0, 0, 2)),
    ((0, 0x006A12FC, 1, 0), (0, 0, 2)),
    ((0, 0x01A474CC, 3, 0), (1, 0x11A474CC, 0)),
    ((1, 0x01A474CC, 0, 3), (1, 0x11A474CC, 0)),
    ((0, 0x01A474CC, 4, 0), (0, 0, 2)),
    ((0, 0x01A474D0, 1, 0), (0, 0, 2)),
    ((0, 0x01A474FE, 15, 0), (0, 0, 1)),
    ((0, 0x01A47500, 15, 0), (1, 0x11A47500, 0)),
    ((1, 0x01ADADB4, 0, 15), (1, 0x11ADADB4, 0)),
    ((0, 0x01ADADB8, 1, 0), (0, 0, 2)),
    ((0, 0xFFFFFFFC, 15, 0), (0, 0, 2)),
    ((0, 0xFFFFFFFF, 15, 0), (0, 0, 1)),
    ((1, 0xFFFFFFFF, 1, 0), (0, 0, 1)),
    ((0, 0x02000000, 0, 0), (0, 0, 1)),
]
for request, expected in manual:
    assert oracle(request) == expected, (request, expected)
save("manual_and_static.json", {"status": "PASS", "objects": objects, "manual": manual,
     "model_sha256": sha(ROOT / runner.MODEL), "spec_sha256": sha(ROOT / runner.SPEC)})
history = []
for name in ("request_guard_20261010_r01", "request_guard_20261010_r02", "request_guard_20261010_r03"):
    folder = ROOT / "report/evidence/S2B-T09" / name
    report = json.loads((folder / "result.json").read_text(encoding="utf-8"))
    manifest = json.loads((folder / "delivery_manifest.json").read_text(encoding="utf-8"))
    for source in report["sources"]:
        assert sha(folder / "source_snapshot" / Path(source["path"]).name) == source["sha256"]
    for entry in manifest["files"]:
        assert sha(ROOT / entry["path"]) == entry["sha256"], (name, entry["path"])
    for run in report["runs"]:
        assert sha(folder / (run["name"] + ".log")) == run["log_sha256"]
    history.append({"run_id": name, "status": report["status"], "error": report.get("error"),
                    "coverage": report["coverage"], "sources": report["sources"], "runs": report["runs"]})
assert history[0]["status"] == "FAIL" and history[0]["runs"][0]["exit_code"] == 1
assert all(h["status"] == "PASS_COMBINATIONAL_REQUEST_GUARD" for h in history[1:])
save("historical_audit.json", history)

work, evidence = BASE / "work", BASE / "evidence"
work.mkdir()
evidence.mkdir()
report = {"status": "FAIL", "runs": [], "source_commit": subprocess.check_output(
          ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
started = time.monotonic()
runner.run(work, evidence, Path(r"D:\FPGA_S2A_MSYS2_20261001\env"), report)
report["elapsed_seconds"] = round(time.monotonic() - started, 3)
save("rebuild_result.json", report)

rows = []
counter = Counter()
def add(request, category):
    """写入独立参考期望与类别统计。"""
    expected = oracle(request)
    rows.append(" ".join(format(x, "x") for x in (*request, *expected)))
    counter[category] += 1
    counter["error" + str(expected[2])] += 1

for request, expected in manual:
    add(request, "manual")
for begin, end, writable, name in objects:
    addresses = {begin - 4, begin, begin + 4, begin + 1, begin + 3,
                 (end & ~3) - 4, end & ~3, (end & ~3) + 4, end - 1, end + 1}
    for address in addresses:
        if address < 0:
            continue
        for write in (0, 1):
            for read_mask in range(16):
                for write_mask in range(16):
                    add((write, address, read_mask, write_mask), "boundary_all_direction_masks")
rng = random.Random(SEED)
for index in range(20000):
    begin, end, writable, name = rng.choice(objects)
    address = rng.getrandbits(32) if index % 5 == 0 else rng.randrange(max(0, begin - 8), end + 8)
    if index % 3:
        address &= ~3
    write, read_mask, write_mask = rng.randrange(2), rng.randrange(16), rng.randrange(16)
    if index % 2:
        if write:
            read_mask = 0
        else:
            write_mask = 0
    add((write, address, read_mask, write_mask), "random")
vectors = BASE / "independent_vectors.txt"
vectors.write_text("\n".join(rows) + "\n", encoding="utf-8")
command = [str(work / "obj_dir/Vtb_s2b_request_guard.exe"), "+VECTORS=" + str(vectors)]
started = time.monotonic()
with (BASE / "independent_simulation.log").open("x", encoding="utf-8") as stream:
    result = subprocess.run(command, cwd=work, stdout=stream, stderr=subprocess.STDOUT, timeout=60)
assert result.returncode == 0
assert (BASE / "independent_simulation.log").read_text(encoding="utf-8").count(
       "PASS REQUEST_GUARD cases=" + str(len(rows))) == 1
save("independent_result.json", {"status": "PASS", "command": command, "exit_code": result.returncode,
     "elapsed_seconds": round(time.monotonic() - started, 3), "seed": SEED, "random_samples": 20000,
     "samples": len(rows), "counts": dict(counter), "vectors_sha256": sha(vectors),
     "sources": report["sources"], "algorithm": "最小/最大选中字节与二分查找半开区间"})
checks = []
for mode in ("evidence", "inputs"):
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
               "--manifest", "report/evidence/S2B-T09/request_guard_20261010_r03/delivery_manifest.json"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60)
    (BASE / ("checker_" + mode + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
    assert result.returncode == (0 if mode == "evidence" else 1)
    checks.append({"mode": mode, "command": command, "exit_code": result.returncode})
save("checker_results.json", checks)
assert all(sha(ROOT / s["path"]) == s["sha256"] for s in report["sources"])
print(json.dumps({"status": "PASS_INDEPENDENT_REVIEW", "rebuild_samples": report["coverage"]["total_samples"],
                  "independent_samples": len(rows), "directory": str(BASE)}, ensure_ascii=False))
