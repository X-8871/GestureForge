"""独立非空框手算MOCK；生产恢复入口和全框检查器，不构造设备。"""
import ctypes
import hashlib
import inspect
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import textwrap
import time
from unittest import mock
import zlib

ROOT = Path(__file__).absolute().parents[4]
sys.path.insert(0, str(ROOT))
from verification import test_s2b_csr_board_acceptance as fixture

OUT = Path(__file__).absolute().parent
original_temp = tempfile.mkdtemp
def isolated(suffix=None, prefix=None, dir=None):
    """全部测试临时目录限制在独立审查目录。"""
    return original_temp(suffix=suffix, prefix=prefix, dir=str(OUT))
tempfile.mkdtemp = isolated

head13 = bytearray([129] * 5070)
cell = 6 * 13 + 6
for entry in range(4):
    head13[entry * 169 + cell] = 0
head13[4 * 169 + cell] = 31
head13[5 * 169 + cell] = 31
HEADS = {"head13": bytes(head13), "head26": bytes([129]) * 20280}
score = (1.0 / (1.0 + math.exp(-31 * 0.24267549589862975))) ** 2
DETECTION = {"class_id": 0, "class_name": "fist", "source_order": 1260, "score": score,
             "xyxy": [0.5 - 81 / 832, 0.5 - 82 / 832, 0.5 + 81 / 832, 0.5 + 82 / 832]}

def response(request, epoch, *, status=0x400, run=False, error=0, code=0, corrupt=False):
    """双头仅中心一个候选超过阈值；序号和坐标由手算确定。"""
    payload = struct.pack("<Q8I", epoch, status, error, 0, int(run), int(run), 0, 1, code)
    if run:
        d = DETECTION
        payload += HEADS["head13"] + HEADS["head26"]
        payload += struct.pack("<ii5d", d["class_id"], d["source_order"],
                               d["score"] - (0.01 if corrupt else 0), *d["xyxy"])
    prefix = struct.pack("<4sHH7I", b"S2BU", 1, request.op | 0x8000, request.sequence,
                         request.frame, request.width, request.height, 1, len(payload), zlib.crc32(payload))
    return prefix + struct.pack("<I", zlib.crc32(prefix)) + payload

source = textwrap.dedent(inspect.getsource(fixture.RawWireTests.test_abort_ack_golden_recovery_uses_real_transport_and_t16))
source = source.replace('bytes([129]) * count', 'HEADS[name]')
source = source.replace('[640, 480]', '[416, 416]')
source = source.replace('"nms_output_box_count": 0, "detections": []', '"nms_output_box_count": 1, "detections": [DETECTION]')
source = source.replace('全负logits使objectness低于0.25，独立手算无框。',
    '手算非空框：head13中心cell84/anchor0，xywh为0；object/class0为31，其余-127。中心0.5，宽81/416，高82/416；source_order=84*3*5=1260；score=sigmoid(31*scale)^2。')
source = source.replace('仅mock的独立全负logits空框', '仅MOCK的独立中心单框手算')
namespace = dict(fixture.__dict__, HEADS=HEADS, DETECTION=DETECTION)
exec(compile(source, str(OUT / "nonempty_golden_probe.py"), "exec"), namespace)
method = namespace['test_abort_ack_golden_recovery_uses_real_transport_and_t16']
started = time.perf_counter()
outcomes = []
for corrupt in (False, True):
    case = fixture.RawWireTests()
    case.setUp()
    try:
        controlled_response = lambda *a, **k: response(*a, **k, corrupt=corrupt and k.get('run', False) and a[1] == 3)
        namespace["raw_response"] = controlled_response
        with mock.patch.object(fixture, "raw_response", side_effect=controlled_response):
            try:
                method(case)
                observed = "ACCEPTED"
            except Exception as exc:
                observed = "REJECTED"
                detail = repr(exc)
        assert observed == ("REJECTED" if corrupt else "ACCEPTED"), (corrupt, observed, detail if observed == "REJECTED" else None)
        outcomes.append({"corrupt_box_score": corrupt, "observed": observed,
                         "detail": detail if observed == "REJECTED" else None})
    finally:
        case.tearDown()
result = {"scope": "INDEPENDENT_HAND_COMPUTED_NONEMPTY_MOCK_NOT_BOARD", "native_exit_code": 0,
          "model_runtime_gate": "MOCK_VALIDATE_PLAN_AND_EXECUTE_ONLY", "expected": DETECTION,
          "head_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in HEADS.items()},
          "outcomes": outcomes, "elapsed_seconds": time.perf_counter() - started,
          "hardware_execution": "NOT_RUN", "source_transformation": "只在内存替换测试空框数据与独立手算来源；生产T20/T18/T16/运输及捕获检查器未改"}
with (OUT / "nonempty_golden_result_r03.json").open("x", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False))
