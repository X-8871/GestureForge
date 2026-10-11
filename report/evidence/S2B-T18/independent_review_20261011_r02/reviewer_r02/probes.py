"""R2只读独立核查与额外MOCK门禁反例。"""
from pathlib import Path
import json
import sys
import tempfile
import time

OUT = Path(__file__).absolute().parent
ROOT = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(ROOT))
tempfile.tempdir = str(OUT)
from verification import s2b_board_acceptance as a
from verification import s2b_board_transport as t
from verification import check_stage_delivery as d
from verification.test_s2b_board_acceptance import AdmissionTests

started = time.monotonic()
checks = []
prep = ROOT / "tmp/2B/S2B-T18/offline_prepare_20261011_r03/preparation.json"
plan = json.loads(a.read_bound(a.binding(prep))[1])
a.validate_plan(plan)
for row in plan["rows"]:
    assert len(a.read_bound(row["input"])[1]) == t.INPUT_BYTES
    gold = json.loads(a.read_bound(row["reference"])[1])["samples"][0]
    for name, head in gold["head_tensors"].items():
        assert t.digest(Path(head["path"]).read_bytes()) == head["tensor_sha256"]
assert len(a.read_bound(plan["weights"])[1]) == t.WEIGHT_BYTES
checks.append({"name": "109实际input/GF8/双head只读SHA", "status": "PASS", "preparation": a.binding(prep)})

old = ROOT / "report/evidence/S2B-T18/offline_delivery_20261011_r01/source_snapshot/s2b_board_acceptance.py"
old_text, new_text = old.read_text(encoding="utf-8"), Path(a.__file__).read_text(encoding="utf-8")
assert old_text[old_text.index("def validate_plan("):] == new_text[new_text.index("def validate_plan("):]
checks.append({"name": "validate_plan及完整RAW/models/1000消费与R1被审版精确相同", "status": "PASS", "old": a.binding(old)})

# 独立重解析R1保存的1000帧MOCK原字节，逐帧重查CRC、frame、index和epoch。
corpus = ROOT / "tmp/2B/S2B-T18/independent_review_20261011_r01/continuous1000_mock/frames"
planned = json.loads((corpus / "request_00000001.json").read_text(encoding="utf-8"))
request = t.Header.unpack(bytes.fromhex(planned["header_hex"]))
epoch = 0
for index in range(1000):
    raw = (corpus / f"stress_{109+index:08d}/uart_response_raw.bin").read_bytes()
    meta, heads, boxes = t.decode_response(raw[:40], raw[40:], request, index, epoch)
    epoch = meta["epoch"]
    assert len(heads["head13"]) == 5070 and len(heads["head26"]) == 20280
assert epoch == 1000
checks.append({"name": "1000既存MOCK原UART独立重解析", "status": "PASS", "epoch": epoch, "hardware_execution": "NOT_RUN"})

for case in ("profile_receipt_sha", "final_manifest_binding", "final_profile_binding", "visibility_parameter", "bsp_flag", "only_parameter_flag", "failed_controller", "failed_wire", "missing_proof"):
    test = AdmissionTests()
    test.setUp()
    try:
        if case == "profile_receipt_sha":
            obj = json.loads(test.review_path.read_text(encoding="utf-8"))
            obj["approved_profile_sha256"] = "0"*64
            test.review_path.write_text(json.dumps(obj), encoding="utf-8")
        elif case.startswith("final_") or case in ("visibility_parameter", "bsp_flag", "only_parameter_flag"):
            obj = json.loads(test.final_review.read_text(encoding="utf-8"))
            key, value = {"final_manifest_binding": ("approved_manifest_sha256", "0"*64),
                          "final_profile_binding": ("approved_profile_sha256", "0"*64),
                          "visibility_parameter": ("visibility_parameter", 0),
                          "bsp_flag": ("same_runtime_bsp_mmu_macros", False),
                          "only_parameter_flag": ("only_visibility_parameter_changed", False)}[case]
            obj[key] = value
            test.final_review.write_text(json.dumps(obj), encoding="utf-8")
        elif case == "failed_controller": test.controller.failed = True
        elif case == "failed_wire": test.wire.failed = True
        else: test.proof_path = None
        try:
            test.call_admit()
        except (ValueError, RuntimeError, TypeError) as error:
            assert not test.serial.sent
            checks.append({"name": case, "status": "PASS_REJECTED_BEFORE_TX", "error": repr(error), "scope": "MOCK_ONLY"})
        else:
            raise AssertionError(case + "未拒绝")
    finally:
        test.tearDown()

manifest = ROOT / "report/evidence/S2B-T18/repair_validation_20261011_r01/delivery_manifest.json"
for mode in ("evidence", "inputs"):
    result = d.check_manifest(mode, str(manifest), str(ROOT))
    checks.append({"name": "包装_"+mode, "result": result})
result = {"schema_version": 1, "status": "PASS_OFFLINE_G2_R2", "hardware_execution": "NOT_RUN",
    "checks": checks, "elapsed_seconds": time.monotonic()-started,
    "source_bindings": [a.binding(ROOT/"verification/s2b_board_acceptance.py"), a.binding(ROOT/"verification/test_s2b_board_acceptance.py")],
    "limitations": ["当前profile并行开发，未固定其语义或批准visibility1。", "所有UART为MOCK，G3/G4/G5未通过。", "峰值内存未测，单文件最大5.9MB。"]}
a.save(OUT/"review_result.json", result)
print(json.dumps({"status": result["status"], "checks": len(checks), "elapsed_seconds": result["elapsed_seconds"]}))
