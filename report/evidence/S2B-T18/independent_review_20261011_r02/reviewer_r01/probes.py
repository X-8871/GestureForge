"""独立只读核查；所有输出写入本隔离目录，协议字节仅为MOCK。"""
from pathlib import Path
import copy
import json
import os
import struct
import sys
import time

ROOT = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(ROOT))
from verification import s2b_board_acceptance as a
from verification import s2b_board_transport as t
from verification import s2b_board_jtag as j
from verification import check_s2b_inference_platform as p
from verification import check_stage_delivery as d
from verification.test_s2b_board_acceptance import MockSerial, response

OUT = Path(__file__).absolute().parent
started = time.monotonic()
result = {"schema_version": 1, "hardware_execution": "NOT_RUN", "checks": []}

def record(name, value):
    """保存明确的检查结果。"""
    result["checks"].append({"name": name, **value})

preparation = ROOT / "tmp/2B/S2B-T18/offline_prepare_20261011_r02/preparation.json"
plan = json.loads(preparation.read_text(encoding="utf-8"))
a.validate_plan(plan)
for row in plan["rows"]:
    _, raw = a.read_bound(row["input"])
    assert len(raw) == t.INPUT_BYTES
    reference = json.loads(a.read_bound(row["reference"])[1])["samples"][0]
    for name in t.HEAD_LENGTHS:
        head = reference["head_tensors"][name]
        assert t.digest(Path(head["path"]).read_bytes()) == head["tensor_sha256"]
_, raw = a.read_bound(plan["weights"])
assert len(raw) == t.WEIGHT_BYTES
record("109冻结真实输入/GF8/双头原字节", {"status": "PASS", "sample_count": 109, "preparation": a.binding(preparation)})

build_path = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
_, build = t.verify_build(build_path)
absolute_elf = build["elf"]
relative_elf = {"path": Path(absolute_elf["path"]).relative_to(ROOT).as_posix(), "sha256": absolute_elf["sha256"]}
assert p.relative_file(ROOT, relative_elf["path"]) == Path(absolute_elf["path"])
assert t.digest(j.bound_bytes(absolute_elf)) == relative_elf["sha256"]
assert relative_elf != absolute_elf
record("R1同ELF路径门禁矛盾", {"status": "CONFIRMED_BLOCKER", "proof_elf": relative_elf,
    "controller_elf": absolute_elf, "same_exact_file_and_sha": True,
    "cause": "现有proof只接受相对路径，controller只接受绝对路径，admit却比较原字典。"})

# 真实黄金多个框/无框/边界输入经MOCK原UART调用真实检查器。
selected = []
for predicate in (lambda r: "empty_ground_truth" in r["coverage_tags"],
                  lambda r: "multi_ground_truth_boxes" in r["coverage_tags"],
                  lambda r: "boundary_ground_truth_box" in r["coverage_tags"]):
    selected.append(next(row for row in plan["rows"] if predicate(row)))
for row in selected:
    directory = OUT / f"golden_uart_mock_{row['index']:03d}"
    directory.mkdir()
    with (directory / "rx.bin").open("xb") as rx, (directory / "tx.bin").open("xb") as tx:
        serial = MockSerial()
        wire = t.WireSession(serial, rx, tx, response_timeout=.1)
        runner = a.AcceptanceRunner(wire, directory / "frames", {"scope": "MOCK_GOLDEN_BYTES_ONLY"})
        reference = json.loads(a.read_bound(row["reference"])[1])["samples"][0]
        heads = b"".join(Path(reference["head_tensors"][name]["path"]).read_bytes() for name in t.HEAD_LENGTHS)
        boxes = [(box["class_id"], box["source_order"], box["score"], *box["xyxy"]) for box in reference["detections"]]
        payload = struct.pack("<II", 0xFFFFFFFF, 17) + a.read_bound(row["input"])[1]
        request, header = t.make_request(t.OP_RUN, 1, row["index"], payload, width=416, height=416)
        serial.raw.extend(response(request, heads=heads, boxes=boxes))
        runner.send(request, header, payload, row["input"])
        runner.receive(request, 0, row, "corpus")
        runner.log.close()
        record("真实冻结golden经MOCK_UART", {"status": "PASS", "index": row["index"], "boxes": len(boxes), "scope": "MOCK_ONLY"})

# 1000次连续身份协议检查不运行模型；逐帧原字节全部保存。
directory = OUT / "continuous1000_mock"
directory.mkdir()
with (directory / "rx.bin").open("xb") as rx, (directory / "tx.bin").open("xb") as tx:
    serial = MockSerial()
    wire = t.WireSession(serial, rx, tx, response_timeout=.1)
    runner = a.AcceptanceRunner(wire, directory / "frames", {"scope": "MOCK_PROTOCOL_ONLY"})
    payload = struct.pack("<II", 0xFFFFFFFF, 17) + bytes(t.INPUT_BYTES)
    request, header = t.make_request(t.OP_RUN, 1, 109, payload, width=416, height=416, repeat=1000)
    runner.send(request, header, payload, {"scope": "MOCK_ONLY"})
    for index in range(1000):
        serial.raw.extend(response(request, epoch=index+1, index=index))
        runner.receive(request, index, phase="stress")
    assert wire.epoch == 1000 and len(runner.record["frames"]) == 1000
    runner.finish("PASS_MOCK_PROTOCOL_1000")
record("1000连续MOCK_epoch/frame/seq", {"status": "PASS", "frames": 1000, "model_checked": False})

manifest = ROOT / "report/evidence/S2B-T18/offline_delivery_20261011_r01/delivery_manifest.json"
for mode in ("evidence", "inputs"):
    checked = d.check_manifest(mode, str(manifest), str(ROOT))
    record("包装_"+mode, {"status": checked["status"], "result": checked})
result.update(status="CHANGES_REQUIRED", elapsed_seconds=time.monotonic()-started,
              source_bindings=[a.binding(ROOT/"verification/s2b_board_acceptance.py"), a.binding(ROOT/"verification/test_s2b_board_acceptance.py")],
              limitations=["UART结果为MOCK，不计入G3/G4。", "未访问SDK/串口/MCP/硬件。", "峰值内存未测。"])
a.save(OUT / "review_result.json", result)
print(json.dumps({"status": result["status"], "elapsed_seconds": result["elapsed_seconds"], "check_count": len(result["checks"])}, ensure_ascii=False))
