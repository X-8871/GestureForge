#!/usr/bin/env python3
"""S4-B PS 解码/NMS + s2bu 风格 UART 帧的 unittest。

覆盖范围：
  1. C 自检（CRC32 检查向量 '123456789' -> 0xCBF43926、头部/meta/框/整帧 pack-unpack 回读、
     篡改拒绝、扩展 op 门闸）；
  2. C 与 Python 冻结 D9 逐框对拍（离散字段完全相同、score/xyxy 绝对误差 <= 1e-6）：
     合成夹具覆盖阈值含等号（score 恰为 0.25）、下面紧邻的排除、类别内 NMS 抑制
     IoU>=0.45、跨类别不抑制、稳定排序截断到 15、稳定 tie 顺序（head->cell->anchor->class_id）、
     裁剪后零面积丢弃、几何补边逆映射、NO_HAND 零框；
  3. 冻结样本链：T25 分片抽取的 head13/head26 INT8 原字节进出一致、
     C 帧与独立 Python 打包逐字节一致、与 2A T29 冻结参考框交叉确认；
  4. 拒收路径：head 长度错误、bundle CRC 损坏必须非零退出。

只读依赖：verification/s1_t02_d9_yolo_decode.py（2A 冻结 D9）与 2A T25/T29 冻结证据。
本测试不访问 UART/JTAG/hw_server/Vivado/板卡，只使用 gcc 与轻量 Python。

运行：工作目录为工作树根，`python -m unittest verification.test_s4_ps_decode -v`。
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import struct
import subprocess
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GCC = Path(r"D:\mingw64\bin\gcc.exe")
SOURCES = (
    "vitis/stage4/s4_ps_decode.c",
    "vitis/stage4/s4_uart_protocol.c",
    "vitis/stage4/s4_offline_host.c",
)
INCLUDE_DIR = "vitis/stage4"
COMPILE_FLAGS = ("-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow")
WORK_DIR = ROOT / "tmp" / "4" / "S4B" / "unittest"
CONTRACT_PATH = ROOT / "docs" / "stage4" / "s4a_stage4_g0_fields.json"

HEAD13_BYTES, HEAD26_BYTES = 5070, 20280
HEAD13_GRID, HEAD26_GRID = 13, 26
SCORE_THRESHOLD = 0.25
NMS_IOU = 0.45
MAX_OUTPUTS = 15
TOLERANCE = 1e-6
CRC_CHECK_VECTOR = 0xCBF43926

BUNDLE_MAGIC = b"S4BUNDL1"
BUNDLE_VERSION = 1
BUNDLE_HEADER = struct.Struct("<8sIIIIIIIdddIII")
HEADER = struct.Struct("<4sHH8I")
META = struct.Struct("<Q8I")
BOX = struct.Struct("<ii5d")

MAIN_ROOT = Path(r"D:\FPGA_Competition")
DELTA = 1.05 - 1.0
ANCHOR_WH = ((10, 14), (23, 27), (37, 58), (81, 82), (135, 169), (344, 319))
MASK13 = (3, 4, 5)
MASK26 = (1, 2, 3)
CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")

_BINARY: Path | None = None
_BINARY_ERROR: str | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def host_binary() -> Path:
    """编译一次 S4-B C 源（0 error 且 0 warning 才算成功），返回可执行文件路径。"""

    global _BINARY, _BINARY_ERROR
    if _BINARY is not None:
        return _BINARY
    if _BINARY_ERROR is not None:
        raise unittest.SkipTest(_BINARY_ERROR)
    if not GCC.exists():
        _BINARY_ERROR = "找不到 %s，跳过依赖 C 的测试" % GCC
        raise unittest.SkipTest(_BINARY_ERROR)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    binary = WORK_DIR / "s4_offline_host.exe"
    command = [str(GCC), *COMPILE_FLAGS, "-I", INCLUDE_DIR, *SOURCES, "-o", str(binary)]
    completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, check=False)
    output = (completed.stdout + completed.stderr).decode("utf-8", "replace")
    if completed.returncode != 0 or " error" in output.lower() or " warning" in output.lower():
        _BINARY_ERROR = "S4-B C 编译未达到 0 error/0 warning：exit=%s\n%s" % (
            completed.returncode,
            output,
        )
        raise unittest.SkipTest(_BINARY_ERROR)
    _BINARY = binary
    return binary


def write_bundle(
    path: Path,
    head13: bytes,
    head26: bytes,
    *,
    width: int,
    height: int,
    frame_id: int = 7,
    sequence: int = 1,
    result_seq: int = 1,
    threshold: float = SCORE_THRESHOLD,
    head13_scale: float = 1.0,
    head26_scale: float = 1.0,
    head13_len: int | None = None,
    head26_len: int | None = None,
    corrupt_crc: bool = False,
) -> None:
    blob = head13 + head26
    header = BUNDLE_HEADER.pack(
        BUNDLE_MAGIC,
        BUNDLE_VERSION,
        width,
        height,
        frame_id,
        sequence,
        HEAD13_BYTES if head13_len is None else head13_len,
        HEAD26_BYTES if head26_len is None else head26_len,
        threshold,
        head13_scale,
        head26_scale,
        (crc32(blob) ^ 0x1) if corrupt_crc else crc32(blob),
        12675,
        result_seq,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + blob)


def run_host(
    head13: bytes,
    head26: bytes,
    *,
    width: int,
    height: int,
    frame_id: int = 7,
    sequence: int = 1,
    threshold: float = SCORE_THRESHOLD,
    head13_scale: float = 1.0,
    head26_scale: float = 1.0,
    tag: str = "case",
    head13_len: int | None = None,
    head26_len: int | None = None,
    corrupt_crc: bool = False,
) -> dict:
    """写 bundle、调用主机 CLI、回收结果 JSON/帧原字节/回写的 INT8 副本。"""

    binary = host_binary()
    case_dir = WORK_DIR / tag
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True)
    bundle = case_dir / "bundle.bin"
    write_bundle(
        bundle,
        head13,
        head26,
        width=width,
        height=height,
        frame_id=frame_id,
        sequence=sequence,
        threshold=threshold,
        head13_scale=head13_scale,
        head26_scale=head26_scale,
        head13_len=head13_len,
        head26_len=head26_len,
        corrupt_crc=corrupt_crc,
    )
    result_json = case_dir / "host_result.json"
    frame_path = case_dir / "frame.bin"
    heads_dir = case_dir / "heads"
    heads_dir.mkdir()
    completed = subprocess.run(
        [
            str(binary),
            "--bundle",
            str(bundle),
            "--json",
            str(result_json),
            "--frame",
            str(frame_path),
            "--heads-dir",
            str(heads_dir),
        ],
        cwd=str(ROOT),
        capture_output=True,
        check=False,
    )
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout.decode("utf-8", "replace"),
        "stderr": completed.stderr.decode("utf-8", "replace"),
        "result": json.loads(result_json.read_text(encoding="utf-8")) if result_json.exists() else None,
        "frame": frame_path.read_bytes() if frame_path.exists() else None,
        "head13_out": (heads_dir / "head13.raw").read_bytes() if (heads_dir / "head13.raw").exists() else None,
        "head26_out": (heads_dir / "head26.raw").read_bytes() if (heads_dir / "head26.raw").exists() else None,
    }


def python_d9(head13: bytes, head26: bytes, width: int, height: int,
              head13_scale: float = 1.0, head26_scale: float = 1.0,
              threshold: float = SCORE_THRESHOLD) -> tuple[list, list]:
    """调用 2A 冻结 D9 参考；临时包装 stable_nms 以取得阈值后、NMS 前的候选列表。"""

    from verification import s1_t02_d9_yolo_decode as d9

    logits13 = [value * head13_scale for value in struct.unpack("<%db" % HEAD13_BYTES, head13)]
    logits26 = [value * head26_scale for value in struct.unpack("<%db" % HEAD26_BYTES, head26)]
    captured: dict = {}
    original = d9.stable_nms

    def spy(predictions, score_threshold, nms_iou, max_outputs):
        captured["candidates"] = list(predictions)
        return original(predictions, score_threshold, nms_iou, max_outputs)

    d9.stable_nms = spy
    try:
        predictions = d9.decode_yolov4_tiny416(
            {"13x13": logits13, "26x26": logits26},
            "unittest_sample",
            width,
            height,
            score_threshold=threshold,
        )
    finally:
        d9.stable_nms = original
    return predictions, captured.get("candidates", [])


def blank_heads(fill: int = -20) -> tuple[bytearray, bytearray]:
    """填充为低分背景：obj/class logit 很低，保证不产生候选。"""

    byte = (fill + 256) % 256
    return bytearray([byte] * HEAD13_BYTES), bytearray([byte] * HEAD26_BYTES)


def set_cell(buffer: bytearray, grid: int, local_anchor: int, row: int, col: int,
             entries: tuple[int, int, int, int, int, int, int, int, int, int]) -> None:
    """按 Darknet 布局 [anchor(3), entry(10), row, col] 写一个 cell 的 10 个 entry。"""

    assert len(entries) == 10, "entry 顺序 x,y,w,h,objectness,class0..class4"
    for entry, value in enumerate(entries):
        index = (local_anchor * 10 + entry) * grid * grid + row * grid + col
        buffer[index] = (value + 256) % 256


def independent_pack_frame(detections: list[dict], *, sequence: int, frame_id: int,
                           width: int, height: int, head13: bytes, head26: bytes,
                           epoch: int = 1, phys_status: int = 0xE04,
                           error_code: int = 0, last_reject: int = 0,
                           raw_candidate_count: int = 0, response_code: int = 0) -> bytes:
    """本测试自带的 s2bu/1.1 打包实现（独立于 C 与 2B 代码，用于逐字节比对）。"""

    payload = META.pack(
        epoch, phys_status, error_code, last_reject, raw_candidate_count,
        len(detections), 0, 1, response_code,
    )
    payload += head13 + head26
    for detection in detections:
        payload += BOX.pack(
            detection["class_id"],
            detection["source_order"],
            detection["score"],
            detection["xyxy"][0],
            detection["xyxy"][1],
            detection["xyxy"][2],
            detection["xyxy"][3],
        )
    head = HEADER.pack(
        b"S2BU", 1, 2 | 0x8000, sequence, frame_id, width, height, 1, len(payload),
        crc32(payload), 0,
    )
    return head[:36] + struct.pack("<I", crc32(head[:36])) + payload


def unpack_frame(frame: bytes) -> dict:
    """独立解帧并返回各段（用于 C 帧回读核验）。"""

    magic, version, op, sequence, frame_id, width, height, repeat, payload_len, payload_crc, header_crc = (
        HEADER.unpack_from(frame, 0)
    )
    assert magic == b"S2BU" and version == 1
    assert crc32(frame[:36]) == header_crc, "header CRC 不一致"
    payload = frame[HEADER.size:]
    assert len(payload) == payload_len
    assert crc32(payload) == payload_crc, "payload CRC 不一致"
    epoch, status, error, reject, raw_count, box_count, index, total, code = META.unpack_from(payload, 0)
    offset = META.size
    head13 = payload[offset : offset + HEAD13_BYTES]
    offset += HEAD13_BYTES
    head26 = payload[offset : offset + HEAD26_BYTES]
    offset += HEAD26_BYTES
    boxes = []
    for _ in range(box_count):
        class_id, source_order, score, x1, y1, x2, y2 = BOX.unpack_from(payload, offset)
        offset += BOX.size
        boxes.append(
            {
                "class_id": class_id,
                "class_name": CLASS_NAMES[class_id],
                "source_order": source_order,
                "score": score,
                "xyxy": [x1, y1, x2, y2],
            }
        )
    return {
        "op": op,
        "sequence": sequence,
        "frame_id": frame_id,
        "width": width,
        "height": height,
        "repeat": repeat,
        "meta": {
            "epoch": epoch,
            "phys_status": status,
            "error_code": error,
            "last_reject": reject,
            "raw_candidate_count": raw_count,
            "box_count": box_count,
            "repeat_index": index,
            "repeat_total": total,
            "response_code": code,
        },
        "head13": head13,
        "head26": head26,
        "boxes": boxes,
    }


def iou(first: list[float], second: list[float]) -> float:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    area_first = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    area_second = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = area_first + area_second - intersection
    return intersection / union if union else 0.0


def frozen_evidence() -> dict | None:
    """按 S4-A 契约解析 T25/T29 只读绑定；缺失时返回 None（相关测试跳过）。"""

    if not CONTRACT_PATH.exists():
        return None
    with io.open(CONTRACT_PATH, encoding="utf-8") as stream:
        contract = json.load(stream)
    bindings = {binding["id"]: binding for binding in contract.get("upstream_bindings", [])}
    needed = ("s2a_t25_layer_golden_index", "s2a_t29_cpu_decode_nms_reference", "s2a_t25_tensor_shards")
    if any(name not in bindings for name in needed):
        return None
    paths = {name: Path(bindings[name]["path"]) for name in needed}
    if not all(path.exists() for path in paths.values()):
        return None
    with io.open(paths["s2a_t25_layer_golden_index"], encoding="utf-8") as stream:
        index = json.load(stream)
    with io.open(paths["s2a_t29_cpu_decode_nms_reference"], encoding="utf-8") as stream:
        t29 = json.load(stream)
    return {
        "index": index,
        "t29": t29,
        "shard_dir": paths["s2a_t25_tensor_shards"],
        "index_sha256": sha256_file(paths["s2a_t25_layer_golden_index"]),
        "t29_sha256": sha256_file(paths["s2a_t29_cpu_decode_nms_reference"]),
    }


def extract_frozen_heads(evidence: dict, sample_index: int) -> dict:
    """按 T25 索引偏移抽取 head13/head26 并核对 T29 的 tensor_sha256。"""

    index_sample = evidence["index"]["samples"][sample_index]
    t29_sample = evidence["t29"]["samples"][sample_index]
    shard = evidence["shard_dir"] / Path(index_sample["network"]["compressed_shard"]["path"]).name
    stream = zlib.decompress(shard.read_bytes())
    heads = {}
    for name, length, layer_index in (("head13", HEAD13_BYTES, 29), ("head26", HEAD26_BYTES, 36)):
        reference = t29_sample["head_tensors"][name]
        layer = next(t for t in index_sample["network"]["tensors"] if t["layer_index"] == layer_index)
        offset = reference["byte_offset"]
        blob = stream[offset : offset + length]
        assert sha256_bytes(blob) == reference["tensor_sha256"], "%s 抽取哈希与 T29 不符" % name
        assert layer["byte_offset"] == offset and layer["scale"] == reference["int8_scale"]
        heads[name] = blob
    return {
        "sample_id": t29_sample["sample_id"],
        "frame_id": t29_sample["frame_id"],
        "width": t29_sample["input"]["geometry_wh"][0],
        "height": t29_sample["input"]["geometry_wh"][1],
        "head13": heads["head13"],
        "head26": heads["head26"],
        "head13_scale": t29_sample["head_tensors"]["head13"]["int8_scale"],
        "head26_scale": t29_sample["head_tensors"]["head26"]["int8_scale"],
        "t29_detections": t29_sample["detections"],
        "t29_candidate_count": t29_sample["raw_candidate_count_before_stable_nms"],
    }


def assert_matches_d9(case: unittest.TestCase, detections: list[dict], predictions: list, *,
                      tolerance: float = TOLERANCE) -> None:
    """逐框断言：离散字段完全相同、score/xyxy 绝对误差不超容限。"""

    case.assertEqual(len(detections), len(predictions), "框数不一致")
    for index, (detection, prediction) in enumerate(zip(detections, predictions)):
        case.assertEqual(detection["class_id"], prediction.class_id, "第 %d 框 class_id" % index)
        case.assertEqual(detection["class_name"], prediction.name, "第 %d 框 class_name" % index)
        case.assertEqual(detection["source_order"], prediction.source_order, "第 %d 框 source_order" % index)
        case.assertLessEqual(abs(detection["score"] - prediction.confidence), tolerance, "第 %d 框 score" % index)
        for axis in range(4):
            case.assertLessEqual(
                abs(detection["xyxy"][axis] - prediction.box[axis]), tolerance,
                "第 %d 框 xyxy[%d]" % (index, axis),
            )


class TestS4HostSelftest(unittest.TestCase):
    """C 自检：CRC 检查向量、pack/unpack 回读、篡改拒绝、扩展门闸。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.binary = host_binary()
        cls.json_path = WORK_DIR / "selftest.json"
        cls.json_path.parent.mkdir(parents=True, exist_ok=True)
        cls.completed = subprocess.run(
            [str(cls.binary), "--selftest", "--json", str(cls.json_path)],
            cwd=str(ROOT), capture_output=True, check=False,
        )
        cls.data = json.loads(cls.json_path.read_text(encoding="utf-8"))
        cls.checks = {check["name"]: check for check in cls.data["checks"]}

    def test_selftest_exit_zero_and_all_pass(self) -> None:
        self.assertEqual(self.completed.returncode, 0, self.completed.stdout.decode("utf-8", "replace"))
        self.assertTrue(self.data["all_pass"])
        self.assertEqual(self.data["checks"][-1]["failed"], 0)

    def test_crc32_check_vector(self) -> None:
        check = self.checks["crc32_check_vector_123456789"]
        self.assertTrue(check["pass"], check)
        self.assertEqual(check["actual"], "0x%08X" % CRC_CHECK_VECTOR)
        self.assertEqual(crc32(b"123456789"), CRC_CHECK_VECTOR, "Python zlib 独立复核")

    def test_pack_unpack_byte_readback_checks(self) -> None:
        for name in (
            "header_pack_unpack_roundtrip",
            "meta_pack_unpack_roundtrip",
            "box_pack_unpack_roundtrip",
            "run_response_pack_unpack_roundtrip",
            "run_response_repack_byte_identical",
        ):
            self.assertTrue(self.checks[name]["pass"], "%s: %s" % (name, self.checks[name]))

    def test_tamper_and_gate_rejections(self) -> None:
        for name in (
            "header_crc_rejects_tamper",
            "header_rejects_bad_magic",
            "payload_crc_rejects_tamper",
            "extension_op_gate_closed",
        ):
            self.assertTrue(self.checks[name]["pass"], "%s: %s" % (name, self.checks[name]))


class TestS4UartFrameLayout(unittest.TestCase):
    """C 帧与独立 Python s2bu/1.1 打包逐字节一致（布局/端序/CRC 交叉核验）。"""

    def test_frame_bytes_match_independent_pack(self) -> None:
        head13, head26 = blank_heads()
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 1, 3, 3, (0, 0, 1, 1, 1, -20, 0, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="uart_layout")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        frame = result["frame"]
        parsed = unpack_frame(frame)
        detections = [dict(box) for box in parsed["boxes"]]
        expected = independent_pack_frame(
            detections,
            sequence=1,
            frame_id=7,
            width=1440,
            height=1920,
            head13=head13,
            head26=head26,
            raw_candidate_count=parsed["meta"]["raw_candidate_count"],
        )
        self.assertEqual(frame, expected, "C 帧与独立 Python 打包字节不一致")
        self.assertEqual(parsed["op"], 2 | 0x8000)
        self.assertEqual(parsed["sequence"], 1)
        self.assertEqual(parsed["frame_id"], 7)
        self.assertEqual((parsed["width"], parsed["height"]), (1440, 1920))
        self.assertEqual(len(frame), HEADER.size + META.size + HEAD13_BYTES + HEAD26_BYTES
                         + len(detections) * BOX.size)
        self.assertEqual(result["result"]["readback"]["repack_byte_identical"], True)

    def test_head_bytes_roundtrip_unchanged(self) -> None:
        head13, head26 = blank_heads()
        set_cell(head26, HEAD26_GRID, 2, 20, 20, (0, 0, 1, 1, 2, 3, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="head_roundtrip")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        self.assertEqual(result["head13_out"], bytes(head13), "head13 INT8 原字节被改写")
        self.assertEqual(result["head26_out"], bytes(head26), "head26 INT8 原字节被改写")
        self.assertTrue(result["result"]["head_bytes_unchanged"])


class TestS4DecodeSemantics(unittest.TestCase):
    """合成夹具：逐条覆盖 2A D9 冻结语义，并与 Python D9 逐框对拍。"""

    def test_threshold_inclusive_at_exactly_0_25(self) -> None:
        head13, head26 = blank_heads()
        # obj logit 0 -> sigmoid = 0.5；class0 logit 0 -> 0.5；score = 0.25 恰在阈值上，必须保留。
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="threshold_equal")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        predictions, candidates = python_d9(head13, head26, 1440, 1920)
        self.assertEqual(len(detections), 1, "score 恰为 0.25 的候选必须按 >= 保留")
        self.assertEqual(detections[0]["score"], 0.25)
        self.assertEqual(len(candidates), 1)
        assert_matches_d9(self, detections, predictions)

    def test_threshold_excludes_below(self) -> None:
        head13, head26 = blank_heads()
        # obj logit -1 -> 0.2689；class0 0.5 -> score 0.1345 < 0.25，必须排除 -> NO_HAND。
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, -1, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="threshold_below")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        self.assertEqual(parsed["boxes"], [])
        self.assertEqual(parsed["meta"]["raw_candidate_count"], 0)
        self.assertEqual(result["result"]["state"], "NO_HAND")
        self.assertEqual(result["result"]["detection_count"], 0)
        predictions, candidates = python_d9(head13, head26, 1440, 1920)
        self.assertEqual(predictions, [])
        self.assertEqual(candidates, [])

    def test_same_class_nms_suppression_ge_0_45(self) -> None:
        head13, head26 = blank_heads()
        # 相邻 cell（row 6 col 6 与 row 6 col 7）、同一 anchor、较大 w/h -> 同类别框高度重叠。
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 2, 2, 2, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 0, 6, 7, (0, 0, 2, 2, 1, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="nms_same_class")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        predictions, candidates = python_d9(head13, head26, 1440, 1920)
        self.assertEqual(len(candidates), 2, "两个同类别候选都应先进入候选集")
        overlap = iou(candidates[0].box, candidates[1].box)
        self.assertGreaterEqual(overlap, NMS_IOU, "夹具未真正触发 IoU>=0.45 抑制（实际 %.6f）" % overlap)
        self.assertEqual(len(predictions), 1, "同类别高 IoU 候选必须被抑制")
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["source_order"], predictions[0].source_order)
        assert_matches_d9(self, detections, predictions)

    def test_cross_class_not_suppressed(self) -> None:
        head13, head26 = blank_heads()
        # 同一几何、不同类别，跨类别不得抑制。
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 2, 2, 2, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 0, 6, 7, (0, 0, 2, 2, 1, -20, 1, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="nms_cross_class")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        predictions, _ = python_d9(head13, head26, 1440, 1920)
        self.assertEqual(len(predictions), 2, "跨类别不得抑制")
        self.assertEqual({box["class_id"] for box in detections}, {0, 1})
        assert_matches_d9(self, detections, predictions)

    def test_top15_truncation_then_nms(self) -> None:
        head13, head26 = blank_heads()
        for index in range(20):
            row, col = divmod(index * 2, HEAD13_GRID * 2)
            set_cell(
                head13, HEAD13_GRID, 0, row % HEAD13_GRID, (col % HEAD13_GRID),
                (0, 0, 0, 0, 20 - index, 0, -20, -20, -20, -20),
            )
        result = run_host(head13, head26, width=1440, height=1920, tag="top15")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        detections = [dict(box) for box in parsed["boxes"]]
        predictions, candidates = python_d9(head13, head26, 1440, 1920)
        self.assertGreater(len(candidates), MAX_OUTPUTS, "候选数必须超过 15 才能验证截断")
        self.assertLessEqual(len(detections), MAX_OUTPUTS)
        self.assertEqual(len(detections), len(predictions))
        assert_matches_d9(self, detections, predictions)

    def test_tie_order_is_head_cell_anchor_class(self) -> None:
        head13, head26 = blank_heads()
        # 四个远隔 cell 使用完全相同的 logits（分数完全相同，均为 0.25），
        # 按 row-major 顺序为 (3,3)、(3,9)、(9,3)、(9,9)；每 cell 产生 5 个同分候选（class_id 0..4），
        # 共 20 个 > 15，用于验证“稳定排序截断到 15”发生在 NMS 之前且 tie 顺序稳定。
        # D9 source_order = 5 * (3 * cell_index + anchor_local) + class_id（anchor 在最内层）。
        cells = ((3, 3), (3, 9), (9, 3), (9, 9))
        for row, col in cells:
            set_cell(head13, HEAD13_GRID, 0, row, col, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        result = run_host(head13, head26, width=1440, height=1920, tag="tie_order")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        predictions, candidates = python_d9(head13, head26, 1440, 1920)
        cell_indices = [row * HEAD13_GRID + col for row, col in cells]
        self.assertEqual(cell_indices, [42, 48, 120, 126])
        expected_orders = [
            5 * (3 * cell + 0) + class_id for cell in cell_indices[:3] for class_id in range(5)
        ]
        self.assertEqual(len(candidates), 5 * len(cell_indices))
        self.assertGreater(len(candidates), MAX_OUTPUTS, "同分候选必须超过 15 才能验证稳定截断")
        self.assertEqual([box["source_order"] for box in detections], expected_orders)
        self.assertEqual(len({box["score"] for box in detections}), 1, "同分夹具分数应完全一致")
        assert_matches_d9(self, detections, predictions)

    def test_zero_area_after_clip_is_dropped(self) -> None:
        head13, head26 = blank_heads()
        # 几何 640x963 -> resized_width=276、pad_left=70；左侧 col=0 的窄框会整段落在补边内，
        # 裁剪后 x1==x2==0（零面积）必须丢弃；中间 cell 的框保留。
        set_cell(head13, HEAD13_GRID, 0, 0, 0, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=640, height=963, tag="zero_area")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        detections = [dict(box) for box in parsed["boxes"]]
        predictions, candidates = python_d9(head13, head26, 640, 963)
        self.assertEqual(len(candidates), 1, "零面积框必须在候选生成前被丢弃")
        self.assertEqual(len(detections), 1)
        self.assertEqual(parsed["meta"]["raw_candidate_count"], 1)
        assert_matches_d9(self, detections, predictions)

    def test_candidate_cap_boundary_all_cells_pass(self) -> None:
        """全部 cell 分数恰为 0.25（全零 logits）时，候选数达到理论上界 12675：

        - candidate_count == candidate_limit == 12675（= (13²+26²)×3×5），必须显式记录；
        - candidate_overflow 必须保留字段且为 false（2B 参考实现只在尝试追加第 12676 个候选时
          返回硬错误；达到上界本身不触发，故不可达）；
        - 稳定 tie 顺序下截断到前 15 个候选（cell 0 的 3 个 anchor × 5 类），且 C 与 D9 逐框一致。
        几何取 416x416（letterbox 恒等、无补边）以避免左侧 cell 被补边裁剪成零面积。
        """

        head13 = bytearray([0] * HEAD13_BYTES)
        head26 = bytearray([0] * HEAD26_BYTES)
        result = run_host(head13, head26, width=416, height=416, tag="cap_boundary")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        detections = [dict(box) for box in parsed["boxes"]]
        predictions, candidates = python_d9(head13, head26, 416, 416)
        self.assertEqual(len(candidates), 12675, "理论上界候选数应为 12675")
        self.assertEqual(parsed["meta"]["raw_candidate_count"], 12675)
        data = result["result"]
        self.assertEqual(data["candidate_count"], 12675)
        self.assertEqual(data["candidate_limit"], 12675)
        self.assertIs(data["candidate_overflow"], False, "达到上界不得置位 candidate_overflow（2B 仅在超出时硬错误）")
        self.assertEqual(data["candidate_count_pre_threshold"], 12675)
        self.assertEqual(data["candidate_box_count"], 2535)
        self.assertEqual(len(detections), 15)
        expected_orders = sorted(candidate.source_order for candidate in candidates)[:15]
        self.assertEqual([box["source_order"] for box in detections], expected_orders)
        assert_matches_d9(self, detections, predictions)

    def test_odd_total_padding_geometry(self) -> None:
        """奇数总补边用例（993x1920 -> resized_width=215、pad_left=100、总补边 201）：

        现有冻结样本的补边均为偶数，无法覆盖“总 pad/2 半像素”这一 2A D9 声明过的差异面。
        本用例用合成夹具把该几何固定下来，期望值全部由 2A 冻结 D9 现场生成（不手写猜测），
        并断言 C 与 D9 逐框一致（离散字段完全相同、score/xyxy 绝对误差 <= 1e-6）。
        """

        width, height = 993, 1920
        head13, head26 = blank_heads()
        # 覆盖：补边区内（左侧 col=0）、正中间、右边界外溢（col=12）、第二头（26x26）。
        set_cell(head13, HEAD13_GRID, 0, 0, 0, (0, 0, 1, 1, 2, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 1, 1, 1, 0, -20, -20, -20, -20))
        set_cell(head13, HEAD13_GRID, 2, 12, 12, (0, 0, 2, 2, 1, -20, 0, -20, -20, -20))
        set_cell(head26, HEAD26_GRID, 1, 12, 12, (0, 0, 1, 1, 2, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=width, height=height, tag="odd_padding")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        letterbox = result["result"]["geometry_letterbox"]
        self.assertEqual(
            (letterbox["resized_width"], letterbox["resized_height"], letterbox["pad_left"], letterbox["pad_top"]),
            (215, 416, 100, 0),
            "奇数总补边几何与 D2/2A 冻结公式不符",
        )
        self.assertEqual((416 - letterbox["resized_width"]) % 2, 1, "本夹具必须是奇数总补边（416-215=201）")
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        predictions, _ = python_d9(head13, head26, width, height)
        self.assertGreaterEqual(len(predictions), 1, "夹具必须至少产生一个框")
        assert_matches_d9(self, detections, predictions)

    def test_no_hand_all_background(self) -> None:
        head13, head26 = blank_heads()
        result = run_host(head13, head26, width=1440, height=1920, tag="no_hand")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        self.assertEqual(parsed["boxes"], [])
        self.assertEqual(parsed["meta"]["box_count"], 0)
        self.assertEqual(parsed["meta"]["raw_candidate_count"], 0)
        self.assertEqual(result["result"]["state"], "NO_HAND")
        self.assertEqual(result["result"]["error_code"], 0)
        self.assertEqual(result["result"]["candidate_overflow"], False)

    def test_clipping_keeps_unit_interval(self) -> None:
        head13, head26 = blank_heads()
        # 靠右下角的大框：逆映射后越界，必须逐边裁剪到 [0,1] 且保持正面积。
        set_cell(head13, HEAD13_GRID, 2, 12, 12, (0, 0, 3, 3, 2, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="clip_unit")
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        detections = [dict(box) for box in unpack_frame(result["frame"])["boxes"]]
        self.assertEqual(len(detections), 1)
        for value in detections[0]["xyxy"]:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        self.assertGreater(detections[0]["xyxy"][2], detections[0]["xyxy"][0])
        self.assertGreater(detections[0]["xyxy"][3], detections[0]["xyxy"][1])
        predictions, _ = python_d9(head13, head26, 1440, 1920)
        assert_matches_d9(self, detections, predictions)

    def test_scale_dequantization_applied(self) -> None:
        head13, head26 = blank_heads(fill=-20)
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        scaled = run_host(
            head13, head26, width=1440, height=1920, tag="scale_applied",
            head13_scale=0.24267549589862975, head26_scale=0.30223452951025775,
        )
        self.assertEqual(scaled["exit_code"], 0, scaled["stderr"])
        detections = [dict(box) for box in unpack_frame(scaled["frame"])["boxes"]]
        # logit = 0 * scale = 0 -> score 仍为 0.25；但 scale 必须真实参与乘法路径。
        self.assertEqual(detections[0]["score"], 0.25)
        predictions, _ = python_d9(
            head13, head26, 1440, 1920,
            head13_scale=0.24267549589862975, head26_scale=0.30223452951025775,
        )
        assert_matches_d9(self, detections, predictions)


class TestS4BundleRejections(unittest.TestCase):
    """非法输入必须被拒绝（非零退出），不产生成功结果。"""

    def test_bad_head_length_rejected(self) -> None:
        head13, head26 = blank_heads()
        result = run_host(head13, head26, width=1440, height=1920, tag="bad_length", head13_len=5069)
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIsNone(result["result"])

    def test_corrupt_bundle_crc_rejected(self) -> None:
        head13, head26 = blank_heads()
        result = run_host(head13, head26, width=1440, height=1920, tag="bad_crc", corrupt_crc=True)
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIsNone(result["result"])

    def test_zero_geometry_rejected(self) -> None:
        head13, head26 = blank_heads()
        result = run_host(head13, head26, width=0, height=1920, tag="bad_geometry")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIsNone(result["result"])


class TestS4FrozenSampleChain(unittest.TestCase):
    """冻结样本链：T25 分片 -> C 解码 -> 帧 -> 与 Python D9 / T29 对拍。

    覆盖样本索引 0（单框）、36（多框 + 边界裁剪到 1.0）、56（同框两类，跨类别不抑制）、
    102（NO_HAND，几何 640x963 非方形补边）。
    """

    SAMPLE_INDICES = (0, 36, 56, 102)

    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = frozen_evidence()
        if cls.evidence is None:
            raise unittest.SkipTest("2A T25/T29 冻结证据不可用（只读引用缺失）")
        host_binary()

    def _chain(self, sample_index: int) -> dict:
        sample = extract_frozen_heads(self.evidence, sample_index)
        result = run_host(
            sample["head13"],
            sample["head26"],
            width=sample["width"],
            height=sample["height"],
            frame_id=sample["frame_id"],
            sequence=1,
            head13_scale=sample["head13_scale"],
            head26_scale=sample["head26_scale"],
            tag="frozen_%03d" % sample_index,
        )
        self.assertEqual(result["exit_code"], 0, result["stderr"])
        parsed = unpack_frame(result["frame"])
        detections = [dict(box) for box in parsed["boxes"]]
        predictions, candidates = python_d9(
            sample["head13"], sample["head26"], sample["width"], sample["height"],
            sample["head13_scale"], sample["head26_scale"],
        )
        return {"sample": sample, "result": result, "parsed": parsed,
                "detections": detections, "predictions": predictions, "candidates": candidates}

    def test_frozen_head_extraction_matches_t29_sha(self) -> None:
        for sample_index in self.SAMPLE_INDICES:
            with self.subTest(sample=sample_index):
                sample = extract_frozen_heads(self.evidence, sample_index)
                self.assertEqual(sha256_bytes(sample["head13"]),
                                 self.evidence["t29"]["samples"][sample_index]["head_tensors"]["head13"]["tensor_sha256"])
                self.assertEqual(sha256_bytes(sample["head26"]),
                                 self.evidence["t29"]["samples"][sample_index]["head_tensors"]["head26"]["tensor_sha256"])

    def test_c_matches_python_d9_and_t29(self) -> None:
        for sample_index in self.SAMPLE_INDICES:
            with self.subTest(sample=sample_index):
                chain = self._chain(sample_index)
                assert_matches_d9(self, chain["detections"], chain["predictions"])
                # 与 2A T29 冻结参考框交叉确认
                reference = chain["sample"]["t29_detections"]
                self.assertEqual(len(chain["detections"]), len(reference))
                for detection, golden in zip(chain["detections"], reference):
                    self.assertEqual(detection["class_id"], golden["class_id"])
                    self.assertEqual(detection["class_name"], golden["class_name"])
                    self.assertEqual(detection["source_order"], golden["source_order"])
                    self.assertLessEqual(abs(detection["score"] - golden["score"]), TOLERANCE)
                    for axis in range(4):
                        self.assertLessEqual(abs(detection["xyxy"][axis] - golden["xyxy"][axis]), TOLERANCE)
                self.assertEqual(chain["parsed"]["meta"]["raw_candidate_count"],
                                 len(chain["candidates"]))
                self.assertEqual(chain["parsed"]["meta"]["raw_candidate_count"],
                                 chain["sample"]["t29_candidate_count"])

    def test_frozen_head_bytes_unchanged_and_frame_heads_identical(self) -> None:
        for sample_index in self.SAMPLE_INDICES:
            with self.subTest(sample=sample_index):
                chain = self._chain(sample_index)
                sample, result, parsed = chain["sample"], chain["result"], chain["parsed"]
                self.assertEqual(result["head13_out"], sample["head13"])
                self.assertEqual(result["head26_out"], sample["head26"])
                self.assertEqual(parsed["head13"], sample["head13"])
                self.assertEqual(parsed["head26"], sample["head26"])
                self.assertTrue(result["result"]["head_bytes_unchanged"])

    def test_state_and_counts_consistency(self) -> None:
        for sample_index in self.SAMPLE_INDICES:
            with self.subTest(sample=sample_index):
                chain = self._chain(sample_index)
                data = chain["result"]["result"]
                self.assertEqual(data["detection_count"], len(data["detections"]))
                if data["detection_count"] == 0:
                    self.assertEqual(data["state"], "NO_HAND")
                    self.assertEqual(data["error_code"], 0)
                else:
                    self.assertEqual(data["state"], "OK")
                self.assertEqual(data["candidate_count"], chain["parsed"]["meta"]["raw_candidate_count"])
                self.assertEqual(data["frame_id"], chain["sample"]["frame_id"])
                self.assertEqual(data["geometry"]["width"], chain["sample"]["width"])
                self.assertEqual(data["geometry"]["height"], chain["sample"]["height"])

    def test_geometry_aware_letterbox(self) -> None:
        # 640x963 -> resized_width = 640*416//963 = 276，pad_left = (416-276)//2 = 70。
        chain = self._chain(102)
        self.assertEqual(chain["sample"]["width"], 640)
        self.assertEqual((chain["result"]["result"]["geometry_letterbox"]["resized_width"],
                          chain["result"]["result"]["geometry_letterbox"]["pad_left"]), (276, 70))


class TestS4ContractFields(unittest.TestCase):
    """结果 JSON 字段名与 S4-A 契约一致（字段名以契约为权威）。"""

    def test_result_json_covers_contract_fields(self) -> None:
        if not CONTRACT_PATH.exists():
            self.skipTest("S4-A 契约文件不存在")
        with io.open(CONTRACT_PATH, encoding="utf-8") as stream:
            contract = json.load(stream)
        result_fields = [field["name"] for field in contract["result_record"]["fields"]]
        detection_fields = [
            field["name"] for field in contract["detection_record"]["fields"] if field["name"] != "xyxy_px"
        ]
        head13, head26 = blank_heads()
        set_cell(head13, HEAD13_GRID, 0, 6, 6, (0, 0, 0, 0, 0, 0, -20, -20, -20, -20))
        result = run_host(head13, head26, width=1440, height=1920, tag="contract_fields")
        data = result["result"]
        for name in result_fields:
            self.assertIn(name, data, "结果 JSON 缺少 S4-A 字段 %s" % name)
        for detection in data["detections"]:
            for name in detection_fields:
                self.assertIn(name, detection, "检测记录缺少 S4-A 字段 %s" % name)
        self.assertIn(data["state"], contract["state_enum"])
        # 离线无 PL：时间字段按 absent_value_policy 用 0 哨兵（未观测），不得伪造实测值。
        for name in ("capture_time_ns", "result_time_ns", "inference_time_ns", "end_to_end_latency_ns"):
            self.assertEqual(data[name], 0, "%s 在离线链中必须是 0 哨兵" % name)
        scope = data["measurement_scope"]
        self.assertEqual(scope["pl_timing"], "NOT_EXECUTED_OFFLINE")
        self.assertEqual(scope["uart_transport"], "NOT_EXECUTED_OFFLINE")
        self.assertEqual(scope["board_pl"], "NOT_EXECUTED_OFFLINE")
        for name in ("capture_time_ns", "result_time_ns", "inference_time_ns", "end_to_end_latency_ns"):
            self.assertIn(name, scope["unavailable_fields"])
        # F4：unavailable_fields 只允许出现在 measurement_scope 内，顶层不得重复。
        self.assertNotIn("unavailable_fields", data)
        # 两个候选数口径必须分别存在且自洽（契约修订后：candidate_count 为阈值后/NMS 前）。
        parsed = unpack_frame(result["frame"])
        self.assertEqual(
            data["candidate_count"],
            parsed["meta"]["raw_candidate_count"],
            "candidate_count（契约口径）必须与 UART raw_candidate_count 同值",
        )
        self.assertEqual(data["candidate_count_pre_threshold"], 5 * data["candidate_box_count"])
        self.assertGreaterEqual(data["candidate_count_pre_threshold"], data["candidate_count"])
        self.assertEqual(data["candidate_count_semantics"]["divergence_open"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)