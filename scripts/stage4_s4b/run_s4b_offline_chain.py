#!/usr/bin/env python3
"""S4-B 离线集成链驱动：冻结 heads -> C 解码/NMS -> s2bu 风格帧 -> 主机解帧 -> 与 Python D9 对拍。

只读依赖（绝对路径与 SHA 来自 S4-A 契约 docs/stage4/s4a_stage4_g0_fields.json 的
upstream_bindings）：
  - 2A T25 逐层 CPU 整数张量索引与 zlib 分片（分片只存在于主树，只读引用）
  - 2A T29 CPU D9 解码/NMS 参考（两头 byte_offset/int8_scale/tensor_sha256 与逐样本框）
  - 2A 冻结 D9/D6 参考实现（verification/s1_t02_d9_yolo_decode.py、
    verification/s1_t02_d6_detection_metrics.py）
  - 2B s2bu/1.1 传输实现（只读导入，仅用于独立消费端核验，不由本阶段修改）

本驱动不做的事（明确未执行，不伪造）：
  - 不访问 UART/COM4、JTAG/hw_server、Vivado/xsim、PL、板卡
  - 不测量 PL 推理时间/期限/吞吐，不产生 G3/G4/G5 结论
  - 不覆盖 109 全量样本（S4-C 负责），默认只跑 1~3 个冻结样本

用法：
  python -B scripts/stage4_s4b/run_s4b_offline_chain.py --run-id 20261021_r01 --samples 3
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import zlib
from pathlib import Path

W4_ROOT = Path(__file__).resolve().parents[2]
GCC_DEFAULT = Path(r"D:\mingw64\bin\gcc.exe")
CONTRACT_RELATIVE = "docs/stage4/s4a_stage4_g0_fields.json"
# 编译输入（只含 C 源；头文件经 -I vitis/stage4 解析）。
C_SOURCE_FILES = (
    "vitis/stage4/s4_ps_decode.c",
    "vitis/stage4/s4_uart_protocol.c",
    "vitis/stage4/s4_offline_host.c",
)
# 交付物源码绑定清单（写入证据 JSON 的 sources[]，含 C/H、驱动、unittest、README 与清单生成器）。
SOURCE_FILES = (
    "vitis/stage4/s4_ps_decode.h",
    "vitis/stage4/s4_ps_decode.c",
    "vitis/stage4/s4_uart_protocol.h",
    "vitis/stage4/s4_uart_protocol.c",
    "vitis/stage4/s4_offline_host.c",
    "vitis/stage4/README.md",
    "scripts/stage4_s4b/run_s4b_offline_chain.py",
    "scripts/stage4_s4b/build_s4b_manifest.py",
    "verification/test_s4_ps_decode.py",
)
COMPILE_FLAGS = ("-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wshadow")

# 独立实现的 s2bu/1.1 布局（本驱动自带，不复用 2B 代码；2B 代码另作独立消费端核验）。
S2BU_HEADER = struct.Struct("<4sHH8I")
S2BU_META = struct.Struct("<Q8I")
S2BU_BOX = struct.Struct("<ii5d")
HEAD13_BYTES, HEAD26_BYTES = 5070, 20280
MAX_OUTPUTS, MAX_CANDIDATES = 15, 12675
CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
SCORE_THRESHOLD = 0.25
CRC_CHECK_VECTOR = 0xCBF43926
# 2B 冻结候选缓冲上限 = tiny416 理论最大候选数 = (13*13 + 26*26) * 3 * 5。
CANDIDATE_LIMIT_EXPECTED = 12675
# 注意：契约哈希一律从 docs/stage4/s4a_stage4_g0_fields.json 现场读出（见 --expected-contract-sha256）。
# 契约在工作区会持续修订，历史版本哈希（例如 Lead 裁决 r04 的 1d7fd5f0…、r05 的 3524d02a…）
# 只写进人读证据，不参与判定；判定依据是字段名/语义/常量不变量。

BUNDLE_MAGIC = b"S4BUNDL1"
BUNDLE_VERSION = 1
BUNDLE_HEADER = struct.Struct("<8sIIIIIIIdddIII")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with io.open(path, encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=False)
        stream.write("\n")


class Recorder:
    """收集可机器读取的检查项；FAIL 只记录，不中断，末尾统一判定。"""

    def __init__(self) -> None:
        self.checks: list[dict] = []

    def record(self, name: str, ok: bool | None, detail: str, expected: object = None, actual: object = None) -> None:
        status = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        entry = {"name": name, "status": status, "detail": detail}
        if expected is not None:
            entry["expected"] = expected
        if actual is not None:
            entry["actual"] = actual
        self.checks.append(entry)

    def failures(self) -> list[dict]:
        return [c for c in self.checks if c["status"] == "FAIL"]

    def summary(self) -> dict:
        counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
        for check in self.checks:
            counts[check["status"]] += 1
        return {"pass": counts["PASS"], "fail": counts["FAIL"], "skip": counts["SKIP"]}


def run_command(command: list[str], cwd: Path, timeout: float = 600.0) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command, cwd=str(cwd), capture_output=True, timeout=timeout, check=False
        )
        stdout = completed.stdout.decode("utf-8", "replace")
        stderr = completed.stderr.decode("utf-8", "replace")
        exit_code: int | None = completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode("utf-8", "replace")
        stderr = (exc.stderr or b"").decode("utf-8", "replace")
        exit_code = None
        timed_out = True
    return {
        "command": command,
        "cwd": str(cwd),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "stdout": stdout,
        "stderr": stderr,
    }


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def build_bundle(
    path: Path,
    *,
    width: int,
    height: int,
    frame_id: int,
    sequence: int,
    result_seq: int,
    threshold: float,
    head13_scale: float,
    head26_scale: float,
    head13: bytes,
    head26: bytes,
) -> dict:
    blob = head13 + head26
    header = BUNDLE_HEADER.pack(
        BUNDLE_MAGIC,
        BUNDLE_VERSION,
        width,
        height,
        frame_id,
        sequence,
        len(head13),
        len(head26),
        threshold,
        head13_scale,
        head26_scale,
        crc32(blob),
        MAX_CANDIDATES,
        result_seq,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + blob)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "header_bytes": BUNDLE_HEADER.size,
        "blob_crc32": "0x%08X" % crc32(blob),
        "sha256": sha256_file(path),
        "head13_sha256": sha256_bytes(head13),
        "head26_sha256": sha256_bytes(head26),
    }


def parse_frame(frame: bytes, *, expect_sequence: int, expect_frame_id: int, expect_size: tuple[int, int]) -> dict:
    """独立（不依赖 C 与 2B 代码）解出 s2bu/1.1 帧，并逐项核验。"""

    if len(frame) < S2BU_HEADER.size + S2BU_META.size:
        raise ValueError("帧截断")
    magic, version, op, sequence, frame_id, width, height, repeat, payload_len, payload_crc, header_crc = (
        S2BU_HEADER.unpack_from(frame, 0)
    )
    if magic != b"S2BU" or version != 1:
        raise ValueError("magic/version 错误")
    if crc32(frame[:36]) != header_crc:
        raise ValueError("header CRC 错误")
    if (op & 0x8000) == 0 or (op & 0x7FFF) != 2:
        raise ValueError("响应 op 不是 RUN|0x8000")
    if (sequence, frame_id, width, height, repeat) != (
        expect_sequence,
        expect_frame_id,
        expect_size[0],
        expect_size[1],
        1,
    ):
        raise ValueError("响应 seq/frame/几何/repeat 不匹配")
    payload = frame[S2BU_HEADER.size:]
    if len(payload) != payload_len:
        raise ValueError("payload 长度不符")
    if crc32(payload) != payload_crc:
        raise ValueError("payload CRC 错误")
    epoch, status, error, reject, raw_count, box_count, index, total, code = S2BU_META.unpack_from(payload, 0)
    offset = S2BU_META.size
    head13 = payload[offset : offset + HEAD13_BYTES]
    offset += HEAD13_BYTES
    head26 = payload[offset : offset + HEAD26_BYTES]
    offset += HEAD26_BYTES
    if len(head13) != HEAD13_BYTES or len(head26) != HEAD26_BYTES:
        raise ValueError("双头长度不足")
    if len(payload) != S2BU_META.size + HEAD13_BYTES + HEAD26_BYTES + box_count * S2BU_BOX.size:
        raise ValueError("payload 长度与 box_count 不符")
    boxes = []
    for _ in range(box_count):
        class_id, source_order, score, x1, y1, x2, y2 = S2BU_BOX.unpack_from(payload, offset)
        offset += S2BU_BOX.size
        boxes.append(
            {
                "class_id": class_id,
                "class_name": CLASS_NAMES[class_id],
                "source_order": source_order,
                "score": score,
                "xyxy": [x1, y1, x2, y2],
            }
        )
    meta = {
        "epoch": epoch,
        "phys_status": status,
        "error_code": error,
        "last_reject": reject,
        "raw_candidate_count": raw_count,
        "box_count": box_count,
        "repeat_index": index,
        "repeat_total": total,
        "response_code": code,
    }
    return {
        "header": {
            "magic": magic.decode("ascii"),
            "version": version,
            "op": op,
            "sequence": sequence,
            "frame_id": frame_id,
            "width": width,
            "height": height,
            "repeat_count": repeat,
            "payload_len": payload_len,
            "payload_crc32": "0x%08X" % payload_crc,
            "header_crc32": "0x%08X" % header_crc,
        },
        "meta": meta,
        "head13": head13,
        "head26": head26,
        "boxes": boxes,
    }


def repack_frame(parsed: dict) -> bytes:
    """用独立实现从解出的结构重新打包，用于字节回读一致性比较。"""

    header = parsed["header"]
    meta = parsed["meta"]
    payload = S2BU_META.pack(
        meta["epoch"],
        meta["phys_status"],
        meta["error_code"],
        meta["last_reject"],
        meta["raw_candidate_count"],
        meta["box_count"],
        meta["repeat_index"],
        meta["repeat_total"],
        meta["response_code"],
    )
    payload += parsed["head13"] + parsed["head26"]
    for box in parsed["boxes"]:
        payload += S2BU_BOX.pack(
            box["class_id"],
            box["source_order"],
            box["score"],
            box["xyxy"][0],
            box["xyxy"][1],
            box["xyxy"][2],
            box["xyxy"][3],
        )
    head = S2BU_HEADER.pack(
        b"S2BU",
        1,
        header["op"],
        header["sequence"],
        header["frame_id"],
        header["width"],
        header["height"],
        header["repeat_count"],
        len(payload),
        crc32(payload),
        0,
    )
    return head[:36] + struct.pack("<I", crc32(head[:36])) + payload


def python_d9_decode(head13: bytes, head26: bytes, width: int, height: int,
                     head13_scale: float, head26_scale: float, threshold: float) -> tuple[list, list]:
    """用 2A 冻结 D9 参考解码，并通过临时包装 stable_nms 采集阈值后、NMS 前候选数。

    只读调用冻结模块，不修改其文件；包装仅存在于本进程内。
    """

    if str(W4_ROOT) not in sys.path:
        sys.path.insert(0, str(W4_ROOT))
    from verification import s1_t02_d9_yolo_decode as d9  # noqa: PLC0415

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
            "offline_sample",
            width,
            height,
            score_threshold=threshold,
        )
    finally:
        d9.stable_nms = original
    return predictions, captured.get("candidates", [])


def compare_detections(c_detections: list[dict], python_predictions: list, tolerance: float) -> dict:
    """逐框比较：离散字段必须完全相同，score/xyxy 绝对误差 <= tolerance。"""

    result = {
        "c_count": len(c_detections),
        "python_count": len(python_predictions),
        "count_mismatch": len(c_detections) != len(python_predictions),
        "discrete_mismatch_count": 0,
        "score_max_abs_error": 0.0,
        "xyxy_max_abs_error": 0.0,
        "tolerance": tolerance,
        "tolerance_exceeded": 0,
        "field_mismatch_details": [],
    }
    for index, (candidate, reference) in enumerate(zip(c_detections, python_predictions)):
        if (
            candidate["class_id"] != reference.class_id
            or candidate["class_name"] != reference.name
            or candidate["source_order"] != reference.source_order
        ):
            result["discrete_mismatch_count"] += 1
            if len(result["field_mismatch_details"]) < 8:
                result["field_mismatch_details"].append(
                    {
                        "index": index,
                        "c": {
                            "class_id": candidate["class_id"],
                            "class_name": candidate["class_name"],
                            "source_order": candidate["source_order"],
                        },
                        "python": {
                            "class_id": reference.class_id,
                            "class_name": reference.name,
                            "source_order": reference.source_order,
                        },
                    }
                )
        score_error = abs(candidate["score"] - reference.confidence)
        result["score_max_abs_error"] = max(result["score_max_abs_error"], score_error)
        for axis in range(4):
            error = abs(candidate["xyxy"][axis] - reference.box[axis])
            result["xyxy_max_abs_error"] = max(result["xyxy_max_abs_error"], error)
        if score_error > tolerance or any(
            abs(candidate["xyxy"][axis] - reference.box[axis]) > tolerance for axis in range(4)
        ):
            result["tolerance_exceeded"] += 1
    return result


def compare_with_t29(c_detections: list[dict], reference_detections: list[dict], tolerance: float) -> dict:
    """与 2A T29 冻结参考框比较（独立黄金），用于交叉确认。"""

    result = {
        "reference_count": len(reference_detections),
        "count_mismatch": len(c_detections) != len(reference_detections),
        "discrete_mismatch_count": 0,
        "score_max_abs_error": 0.0,
        "xyxy_max_abs_error": 0.0,
        "tolerance_exceeded": 0,
    }
    for candidate, reference in zip(c_detections, reference_detections):
        if (
            candidate["class_id"] != reference["class_id"]
            or candidate["class_name"] != reference["class_name"]
            or candidate["source_order"] != reference["source_order"]
        ):
            result["discrete_mismatch_count"] += 1
        result["score_max_abs_error"] = max(
            result["score_max_abs_error"], abs(candidate["score"] - reference["score"])
        )
        for axis in range(4):
            result["xyxy_max_abs_error"] = max(
                result["xyxy_max_abs_error"], abs(candidate["xyxy"][axis] - reference["xyxy"][axis])
            )
        if abs(candidate["score"] - reference["score"]) > tolerance or any(
            abs(candidate["xyxy"][axis] - reference["xyxy"][axis]) > tolerance for axis in range(4)
        ):
            result["tolerance_exceeded"] += 1
    return result


def load_2b_transport(path: Path):
    """只读导入 2B 冻结传输实现，作为独立消费端核验（不改其字节）。"""

    spec = importlib.util.spec_from_file_location("s4b_frozen_2b_transport_reference", str(path))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    # dataclass 解析字符串注解时需要 sys.modules 中存在该模块，否则会抛
    # "'NoneType' object has no attribute '__dict__'"。
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return module


def find_binding(contract: dict, binding_id: str) -> dict | None:
    for binding in contract.get("upstream_bindings", []):
        if binding.get("id") == binding_id:
            return binding
    return None


def check_bound_file(recorder: Recorder, contract: dict, binding_id: str, role: str) -> Path | None:
    binding = find_binding(contract, binding_id)
    if binding is None:
        recorder.record("binding.%s" % binding_id, False, "S4-A 契约缺少该 upstream_binding")
        return None
    path = Path(binding["path"])
    if not path.exists():
        recorder.record("binding.%s" % binding_id, False, "绑定路径不存在（只读引用）", str(path), "缺失")
        return None
    actual = sha256_file(path)
    expected = binding.get("sha256")
    ok = expected is None or actual == expected
    recorder.record(
        "binding.%s" % binding_id,
        ok,
        "%s（只读引用，未写入）" % role,
        expected,
        actual,
    )
    return path


def parse_define(text: str, name: str) -> float | None:
    """从 C 头文件文本中读取 #define 的数值常量（用于核对冻结源码是否携带契约常量）。"""

    match = re.search(r"^#define\s+%s\s+([0-9A-Za-z_.+-]+)" % re.escape(name), text, re.MULTILINE)
    if match is None:
        return None
    raw = match.group(1).rstrip("uUlL")
    try:
        return float(raw)
    except ValueError:
        return None


def semantic_alignment(contract: dict, report: dict, tolerance: float,
                       header_texts: str) -> list[dict]:
    """逐项核对契约的语义常量与运行期观测值；任一不符即 MISMATCH（调用方会记 FAIL）。"""

    frozen = contract.get("frozen_2a_constants", {})
    uart_mapping = contract.get("uart_mapping", {})
    anomaly = contract.get("anomaly_accounting", {}).get("candidate_overflow", {})
    derived = contract.get("derived_values_not_draft", {}).get("candidate_limit", {})
    scope_keys_contract = set(
        contract.get("evidence_annotation", {}).get("measurement_scope", {}).get("keys", {})
    )
    state_keys = set(contract.get("state_enum", {}).keys())
    samples = [s for s in report["samples"] if s.get("host_result")]
    hosts = [s["host_result"] for s in samples]
    frames = [s.get("frame", {}) for s in samples]
    candidate_text = json.dumps(contract.get("result_record", {}), ensure_ascii=False)
    items: list[dict] = []

    def add(item: str, ok: bool, actual: str, expectation: str) -> None:
        items.append(
            {
                "item": item,
                "expectation": expectation,
                "actual": actual,
                "status": "ALIGNED" if ok else "MISMATCH",
            }
        )

    # 阈值 0.25 含等号
    contract_threshold = frozen.get("score_threshold")
    header_threshold = parse_define(header_texts, "S4_SCORE_THRESHOLD")
    host_thresholds = [h["decode"]["score_threshold"] for h in hosts]
    rule_ok = ">=" in str(frozen.get("score_threshold_rule", "")) or "含等号" in str(
        frozen.get("score_threshold_rule", "")
    )
    add(
        "score_threshold=0.25 且含等号",
        contract_threshold == 0.25 and rule_ok and header_threshold == 0.25
        and all(value == 0.25 for value in host_thresholds),
        "contract=%s, C 头=%s, 运行期=%s, rule含等号=%s"
        % (contract_threshold, header_threshold, sorted(set(host_thresholds)), rule_ok),
        "contract/frozen 与 C 头均为 0.25，rule 含等号",
    )
    # NMS IoU 0.45
    contract_iou = frozen.get("nms_iou")
    header_iou = parse_define(header_texts, "S4_NMS_IOU")
    add(
        "nms_iou=0.45（类别内 greedy，>= 抑制）",
        contract_iou == 0.45 and header_iou == 0.45 and "类别内" in str(frozen.get("nms_rule", "")),
        "contract=%s, C 头=%s, rule=%s" % (contract_iou, header_iou, frozen.get("nms_rule")),
        "contract 与 C 头均为 0.45，规则为类别内 greedy",
    )
    # ≤15 框
    contract_max = frozen.get("max_outputs_per_image")
    header_max = parse_define(header_texts, "S4_MAX_OUTPUTS")
    add(
        "max_outputs_per_image=15",
        contract_max == 15 and header_max == 15
        and all(h["detection_count"] <= 15 for h in hosts)
        and all(f.get("meta", {}).get("box_count", 0) <= 15 for f in frames),
        "contract=%s, C 头=%s, 各样本框数=%s"
        % (contract_max, header_max, [h["detection_count"] for h in hosts]),
        "contract 与 C 头均为 15，且所有样本与帧内框数 <= 15",
    )
    # 5 类与类别顺序
    classes = frozen.get("classes")
    header_classes = parse_define(header_texts, "S4_CLASS_COUNT")
    host_class_names = sorted({d["class_name"] for h in hosts for d in h["detections"]})
    add(
        "5 类与类别顺序",
        header_classes == 5 and isinstance(classes, list) and len(classes) == 5
        and classes == list(CLASS_NAMES) and set(host_class_names) <= set(CLASS_NAMES)
        and all(d["class_name"] == CLASS_NAMES[d["class_id"]] for h in hosts for d in h["detections"]),
        "contract=%s, C 头=%s, 运行期出现的类=%s" % (classes, header_classes, host_class_names),
        "contract 顺序与脚本 CLASS_NAMES 一致，class_name 由 class_id 派生",
    )
    # 两头字节长度与 scale
    contract_head13 = frozen.get("head13", {})
    contract_head26 = frozen.get("head26", {})
    header_h13 = parse_define(header_texts, "S4_HEAD13_BYTES")
    header_h26 = parse_define(header_texts, "S4_HEAD26_BYTES")
    header_s13 = parse_define(header_texts, "S4_HEAD13_SCALE")
    header_s26 = parse_define(header_texts, "S4_HEAD26_SCALE")
    observed_ok = all(
        h["decode"]["head13_len"] == 5070 and h["decode"]["head26_len"] == 20280
        and h["decode"]["head13_scale"] == contract_head13.get("int8_scale")
        and h["decode"]["head26_scale"] == contract_head26.get("int8_scale")
        for h in hosts
    )
    add(
        "两头 5,070/20,280 B 与 int8_scale",
        contract_head13.get("byte_length") == 5070 and contract_head26.get("byte_length") == 20280
        and header_h13 == 5070 and header_h26 == 20280
        and header_s13 == contract_head13.get("int8_scale")
        and header_s26 == contract_head26.get("int8_scale") and observed_ok,
        "contract=(%s,%s)/(%s,%s), C 头=(%s,%s)/(%s,%s), 运行期=%s"
        % (
            contract_head13.get("byte_length"), contract_head26.get("byte_length"),
            contract_head13.get("int8_scale"), contract_head26.get("int8_scale"),
            header_h13, header_h26, header_s13, header_s26, observed_ok,
        ),
        "contract/C 头/运行期三方一致",
    )
    # 容限 1e-6 与相对容限 0
    contract_tol = frozen.get("comparison_tolerance", {})
    add(
        "比较容限 score/xyxy 1e-6、相对 0",
        contract_tol.get("score_abs_tolerance") == 1e-6
        and contract_tol.get("xyxy_abs_tolerance_per_component") == 1e-6
        and contract_tol.get("relative_tolerance") == 0
        and tolerance == 1e-6
        and all(
            s["comparison_c_vs_python_d9"]["score_max_abs_error"] <= 1e-6
            and s["comparison_c_vs_python_d9"]["xyxy_max_abs_error"] <= 1e-6
            and s["comparison_c_vs_python_d9"]["discrete_mismatch_count"] == 0
            for s in samples
        ),
        "contract=%s, 驱动 tolerance=%s, 实测最大误差=%s"
        % (
            {k: contract_tol.get(k) for k in ("score_abs_tolerance", "xyxy_abs_tolerance_per_component", "relative_tolerance")},
            tolerance,
            [
                (s["comparison_c_vs_python_d9"]["score_max_abs_error"],
                 s["comparison_c_vs_python_d9"]["xyxy_max_abs_error"])
                for s in samples
            ],
        ),
        "contract 容限 1e-6/1e-6/相对 0，且实测误差在容限内",
    )
    # candidate_count 口径：阈值后、15 框截断前、NMS 前
    candidate_field = next(
        (f for f in contract.get("result_record", {}).get("fields", []) if f["name"] == "candidate_count"),
        {},
    )
    candidate_sem = str(candidate_field.get("semantics", ""))
    candidate_ok = (
        "阈值筛除后" in candidate_sem and "NMS 前" in candidate_sem
        and all(
            s["host_result"]["candidate_count"] == s["frame"]["meta"]["raw_candidate_count"]
            == s["python_d9"]["candidate_count"]
            for s in samples
        )
    )
    add(
        "candidate_count=阈值后/15 框截断前/NMS 前",
        candidate_ok,
        "contract 语义=%s；各样本 record=UART=Python=%s"
        % (
            candidate_sem[:60],
            [
                (s["host_result"]["candidate_count"], s["python_d9"]["candidate_count"])
                for s in samples
            ],
        ),
        "契约语义为阈值筛除后/NMS 前，且记录值 == UART 值 == Python D9 候选数",
    )
    # candidate_count_pre_threshold 为可选诊断
    pre_field = next(
        (f for f in contract.get("result_record", {}).get("fields", [])
         if f["name"] == "candidate_count_pre_threshold"),
        {},
    )
    add(
        "candidate_count_pre_threshold 仅为可选诊断（required=false、不进 UART）",
        pre_field.get("required") is False and "不进 UART" in str(pre_field.get("field_semantics_note", ""))
        and all(
            h["candidate_count_pre_threshold"] == 5 * h["candidate_box_count"]
            and h["candidate_count_pre_threshold"] >= h["candidate_count"]
            for h in hosts
        ),
        "contract.required=%s；各样本 pre=5×boxes 且 >= candidate_count" % pre_field.get("required"),
        "required=false 且不进 UART；运行期 pre == 5 × candidate_box_count",
    )
    # candidate_limit=12675 与硬错误语义、不定义截断
    anomaly_text = json.dumps(anomaly, ensure_ascii=False)
    add(
        "candidate_limit=12675 且为硬错误路径（不定义候选截断）",
        anomaly.get("limit_value") == 12675 and derived.get("value") == 12675
        and "硬错误" in anomaly_text and "不定义候选截断" in anomaly_text
        and all(h["candidate_limit"] == 12675 and h["candidate_overflow"] is False for h in hosts),
        "limit_value=%s, derived=%s, 运行期 limit/overflow=%s"
        % (
            anomaly.get("limit_value"), derived.get("value"),
            [(h["candidate_limit"], h["candidate_overflow"]) for h in hosts],
        ),
        "契约与运行期均为 12675；语义为硬错误且不定义截断；overflow 恒 false 但字段保留",
    )
    # state_enum 5 态
    expected_states = {"OK", "NO_HAND", "TIMEOUT", "ERROR", "DROPPED"}
    add(
        "state_enum 5 态",
        expected_states <= state_keys
        and all(h["state"] in expected_states for h in hosts),
        "contract=%s, 运行期 state=%s" % (sorted(state_keys), [h["state"] for h in hosts]),
        "契约含 OK/NO_HAND/TIMEOUT/ERROR/DROPPED，运行期取值合法",
    )
    # <ii5d> 48 B
    header_box = parse_define(header_texts, "S4_UART_BOX_BYTES")
    box_text = str(uart_mapping.get("existing_box", ""))
    frame_length_ok = all(
        s["frame"]["bytes"] == 40 + 40 + 5070 + 20280 + 48 * s["host_result"]["detection_count"]
        for s in samples
    )
    add(
        "每框 <ii5d> 48 B 与帧长等式",
        header_box == 48 and "<ii5d>" in box_text and "48" in box_text and frame_length_ok,
        "C 头 S4_UART_BOX_BYTES=%s, contract=%s, 帧长等式=%s" % (header_box, box_text[:60], frame_length_ok),
        "C 头 48 B、契约 <ii5d> 48 B、帧长 = 40+40+5070+20280+48×框数",
    )
    # measurement_scope 4 键
    observed_scope_keys = sorted(set().union(*[set(h.get("measurement_scope", {})) for h in hosts])) if hosts else []
    add(
        "measurement_scope 4 键（含 note 允许）",
        scope_keys_contract == {"pl_timing", "uart_transport", "board_pl", "unavailable_fields"}
        and set(observed_scope_keys) >= scope_keys_contract
        and all(
            h["measurement_scope"].get(key) == "NOT_EXECUTED_OFFLINE"
            for h in hosts for key in ("pl_timing", "uart_transport", "board_pl")
        )
        and all("unavailable_fields" not in h for h in hosts),
        "contract=%s, 运行期=%s, 顶层无重复 unavailable_fields=%s"
        % (sorted(scope_keys_contract), observed_scope_keys, all("unavailable_fields" not in h for h in hosts)),
        "契约 4 键齐备、取值合法，且顶层不再重复 unavailable_fields",
    )
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="S4-B 离线集成链驱动（冻结 heads -> C 解码 -> s2bu 帧 -> 对拍）")
    parser.add_argument("--run-id", required=True, help="新运行标识；evidence/<run_id> 必须不存在")
    parser.add_argument("--samples", type=int, default=3, help="使用前 N 个冻结样本（1..3）")
    parser.add_argument(
        "--sample-indices",
        default=None,
        help="逗号分隔的冻结样本索引（最多 3 个，如 36,56,102 用于多框/跨类/NO_HAND 覆盖）；"
        "缺省取前 --samples 个",
    )
    parser.add_argument("--gcc", default=str(GCC_DEFAULT), help="gcc 路径")
    parser.add_argument("--contract", default=CONTRACT_RELATIVE, help="S4-A 契约相对路径")
    parser.add_argument("--tolerance", type=float, default=1e-6, help="score/xyxy 绝对误差上限")
    parser.add_argument(
        "--expected-contract-sha256",
        default=None,
        help="期望的 S4-A 契约 SHA-256；缺省取现场读出值（不硬编码历史哈希）",
    )
    args = parser.parse_args(argv)

    if not 1 <= args.samples <= 3:
        print("[s4b] --samples 只允许 1..3（全量 109 由 S4-C 负责）", file=sys.stderr)
        return 2
    if args.sample_indices:
        try:
            sample_indices = [int(part) for part in args.sample_indices.split(",") if part.strip()]
        except ValueError:
            print("[s4b] --sample-indices 必须是逗号分隔整数", file=sys.stderr)
            return 2
        if not 1 <= len(sample_indices) <= 3:
            print("[s4b] --sample-indices 只允许 1..3 个索引", file=sys.stderr)
            return 2
    else:
        sample_indices = list(range(args.samples))

    contract_path = W4_ROOT / args.contract
    if not contract_path.exists():
        print("[s4b] S4-A 契约不存在：%s" % contract_path, file=sys.stderr)
        return 2
    contract = load_json(contract_path)
    contract_sha = sha256_file(contract_path)
    expected_contract_sha = args.expected_contract_sha256 or contract_sha

    tmp_dir = W4_ROOT / "tmp" / "4" / "S4B" / args.run_id
    evidence_dir = W4_ROOT / "report" / "evidence" / "S4-B" / args.run_id
    if evidence_dir.exists():
        print("[s4b] 拒绝覆盖既有 RunId：%s" % evidence_dir, file=sys.stderr)
        return 2
    tmp_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True)

    recorder = Recorder()
    started = time.perf_counter()
    report: dict = {
        "schema_version": "gestureforge_s4b_offline_chain_v1",
        "task_id": "S4-B",
        "run_id": args.run_id,
        "stage": "4",
        "scope": "离线准备：冻结 heads -> C 解码/NMS -> s2bu/1.1 风格帧 -> 主机解帧 -> Python D9 对拍",
        "created_utc8": time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime()),
        "w4_root": str(W4_ROOT),
        "contract": {
            "path": str(contract_path),
            "relative": args.contract,
            "sha256": contract_sha,
            "schema_version": contract.get("schema_version"),
            "status": contract.get("status"),
            "note": "S4-A 契约为 DRAFT_NOT_FROZEN；字段名以其 result_record.fields 为权威命名",
        },
        "bindings": [],
        "environment": {
            "python": sys.version.split()[0],
            "gcc": None,
            "host_os": os.name,
            "note": "未使用 Vivado/xsim/综合/仿真；未访问 UART/JTAG/hw_server/COM4/板卡",
        },
        "sources": [],
        "commands": {},
        "samples": [],
        "checks": [],
        "limitations": [
            "离线骨架：无板卡、无 PL、无真实 UART/JTAG、无 PL 时间戳；不产生 G3/G4/G5 结论",
            "默认只覆盖 1~3 个冻结样本；109 全量由 S4-C 负责",
            "未测量 PL 推理时间/期限/吞吐；四个时间字段按契约用 0 哨兵（未观测），并在 measurement_scope 内标注 NOT_EXECUTED_OFFLINE，绝不冒充实测值",
            "S4-A 草案候选上限 4096 已弃用（会引入 2A D9/2B 参考实现中都不存在的候选截断）；本链使用契约 candidate_limit=12675 且候选超限为硬错误路径（不可达，恒 false）",
            "2B 验收（s2bu/1.1 板上行为）不在本任务范围；本链只做帧格式/CRC/字节一致性核验",
            "s2bu/1.1 缺少 result_seq/state/时间/丢帧/过期字段：扩展格式待 Wong 决策，本链不新增传输字段",
        ],
        "not_executed": [
            "板上真实串口 / COM4 / UART 收发",
            "JTAG / hw_server / DAP / PL 加载",
            "PL inference_time / deadline / 吞吐测量",
            "109 全量样本（S4-C）",
            "2B 实板验收与 s2bu/1.1 板上行为",
            "Vivado / xsim / 综合 / 仿真 / 上板",
        ],
        "development_notes": [
            "证据落点：按 Lead 决定统一为官方两段式 report/evidence/S4-B/<run_id>/（早期运行曾写在 "
            "report/evidence/S4-CTRL/S4B/<run_id>/，其 summary 内嵌的 evidence_dir 字符串为迁移前路径，内容未改写；"
            "本 run 的落点与内嵌路径一致，为权威运行）。",
            "开发期驱动调用暴露并修复了两个骨架缺陷（C 自检帧缓冲 4096 B < 完整 RUN 帧 26150 B；"
            "importlib 导入 2B 冻结传输时未注册 sys.modules 导致 dataclass 字符串注解解析失败）。"
            "修复后的权威运行见本 run_id；先前 run_id=20261021_r01/r02 为 schema 不完整或样本集不同的早期运行，"
            "按“不删除既有 RunId 证据”的规则保留，其结论以本 run 为准。",
        ],
        "open_items": [
            {
                "id": "S4B-OPEN-01",
                "title": "candidate_count 口径冲突（契约 vs 2B/T29 冻结实现）",
                "contract_text": "S4-A 原草案曾定义 candidate_count = 阈值筛除前的原始候选数；uart_mapping.raw_candidate_count_semantics 指出 2B 正文未定义该口径",
                "frozen_reality": "2B 冻结 C 实现与 2A T29 黄金 raw_candidate_count_before_stable_nms 均为阈值筛除后、NMS 前的候选数",
                "resolution": "已由 Lead 裁决并修订 S4-A 契约：candidate_count = 阈值筛除后、NMS 前（2B/T29 同口径，可被 T29 黄金独立验证）；阈值前候选机会数改列可选诊断字段 candidate_count_pre_threshold（不进 UART、不参与对拍）",
                "implementation": "结果记录 candidate_count 取自 UART raw_candidate_count（阈值后/NMS 前）；candidate_count_pre_threshold = 5 * candidate_box_count；UART 字段语义未改",
                "status": "RESOLVED_BY_LEAD_CONTRACT_REVISION",
            },
            {
                "id": "S4B-OPEN-02",
                "title": "S4-A absent_value_policy 与离线无 PL 的取值",
                "interim_behaviour": "四个时间字段按契约用 0 哨兵 + measurement_scope.pl_timing=NOT_EXECUTED_OFFLINE + unavailable_fields 显式标注，不冒充实测值",
                "status": "CONFORMANT_PENDING_CONFIRMATION",
            },
            {
                "id": "S4B-OPEN-03",
                "title": "S4-A 草案 candidate_limit=4096 未启用",
                "interim_behaviour": "保持 2B 冻结缓冲上限 12675（= 理论最大候选数），启用 4096 会破坏与 2A D9 的逐框等价",
                "status": "NOT_APPLIED_DRAFT_VALUE",
            },
            {
                "id": "S4B-OPEN-04",
                "title": "s2bu/1.1 时间/丢帧/过期/result_seq/state 字段扩展",
                "interim_behaviour": "按 Lead 指示预留（新 op/TLV 位置已定义，S4_UART_ENABLE_EXTENSION=0、扩展 op 门闸关闭），不修改 2B 正文语义",
                "status": "OPEN_AWAITING_WONG_DECISION",
            },
        ],
    }

    # --- 契约与上游绑定 -----------------------------------------------------
    required_result_fields = [f["name"] for f in contract.get("result_record", {}).get("fields", [])]
    required_detection_fields = [f["name"] for f in contract.get("detection_record", {}).get("fields", [])]
    report["contract"]["result_record_fields"] = required_result_fields
    report["contract"]["detection_record_fields"] = required_detection_fields
    report["contract"]["state_enum"] = sorted(contract.get("state_enum", {}).keys())
    recorder.record(
        "contract.result_record_fields_present",
        bool(required_result_fields),
        "S4-A result_record.fields 非空，字段名以其为权威",
        "非空",
        "%d 个字段" % len(required_result_fields),
    )

    # 契约的 candidate_count 口径文本（与 2B/T29 冻结实现口径的差异属于未决项，必须显式记录）。
    candidate_field = next(
        (f for f in contract.get("result_record", {}).get("fields", []) if f["name"] == "candidate_count"),
        {},
    )
    contract_candidate_text = "%s | %s" % (
        candidate_field.get("semantics", ""),
        contract.get("uart_mapping", {}).get("raw_candidate_count_semantics", ""),
    )
    report["contract"]["candidate_count_semantics_text"] = contract_candidate_text
    report["contract"]["candidate_count_declares_thresholded_after_nms"] = (
        "阈值筛除后" in contract_candidate_text
    )
    recorder.record(
        "contract.candidate_count_semantics_read",
        bool(contract_candidate_text.strip()),
        "已读取契约 candidate_count 口径文本并据此实现（阈值后/NMS 前口径进入结果记录 candidate_count）",
        "契约文本存在且明确口径",
        contract_candidate_text[:160],
    )
    recorder.record(
        "contract.candidate_count_semantics_is_thresholded_after_nms",
        report["contract"]["candidate_count_declares_thresholded_after_nms"],
        "契约 candidate_count 已与 2B 冻结实现/T29 黄金统一为阈值后、NMS 前口径（原冲突已裁决）",
        "契约声明阈值后/NMS 前",
        "阈值后" if report["contract"]["candidate_count_declares_thresholded_after_nms"] else "其它口径",
    )
    recorder.record(
        "contract.sha256_read_from_file",
        contract_sha == expected_contract_sha,
        "契约 SHA-256 现场读出并与期望值一致（期望值默认取读出值；不硬编码历史哈希）",
        expected_contract_sha,
        contract_sha,
    )
    # 语义不变量（与易变哈希解耦）：契约若再修订，这些检查仍能判定实现是否对齐。
    contract_measurement_scope = (
        contract.get("evidence_annotation", {}).get("measurement_scope", {}).get("keys", {})
    )
    recorder.record(
        "contract.measurement_scope_keys_defined",
        set(contract_measurement_scope) == {"pl_timing", "uart_transport", "board_pl", "unavailable_fields"},
        "契约 evidence_annotation.measurement_scope 键名（离线证据必须使用同一组键）",
        "pl_timing/uart_transport/board_pl/unavailable_fields",
        ",".join(sorted(contract_measurement_scope)),
    )
    contract_overflow_text = json.dumps(
        contract.get("anomaly_accounting", {}).get("candidate_overflow", {}), ensure_ascii=False
    )
    recorder.record(
        "contract.candidate_overflow_is_hard_error_semantics",
        "硬错误" in contract_overflow_text and "不定义候选截断语义" in contract_overflow_text,
        "契约 candidate_overflow 为硬错误语义且不定义候选截断（本实现仅在尝试超出上限时置位，不可达）",
        "硬错误路径且无截断",
        contract_overflow_text[:150],
    )
    contract_overflow = contract.get("anomaly_accounting", {}).get("candidate_overflow", {})
    contract_limit = contract_overflow.get("limit_value")
    recorder.record(
        "contract.candidate_limit_is_12675",
        contract_limit == CANDIDATE_LIMIT_EXPECTED,
        "契约候选缓冲上限 = 12675（2B 冻结上限 = tiny416 理论最大候选数），4096 已弃用",
        CANDIDATE_LIMIT_EXPECTED,
        contract_limit,
    )
    contract_pre_field = next(
        (f for f in contract.get("result_record", {}).get("fields", [])
         if f["name"] == "candidate_count_pre_threshold"),
        None,
    )
    recorder.record(
        "contract.candidate_count_pre_threshold_is_optional_diagnostic",
        contract_pre_field is not None and contract_pre_field.get("required") is False
        and "不进 UART" in contract_pre_field.get("field_semantics_note", ""),
        "candidate_count_pre_threshold 为 required=false 诊断字段且不进 UART（缺省表示未统计）",
        "required=false 且不进 UART",
        json.dumps(contract_pre_field, ensure_ascii=False)[:160] if contract_pre_field else "字段缺失",
    )

    index_path = check_bound_file(recorder, contract, "s2a_t25_layer_golden_index", "2A T25 逐层索引")
    t29_path = check_bound_file(recorder, contract, "s2a_t29_cpu_decode_nms_reference", "2A T29 D9 参考")
    d9_path = check_bound_file(recorder, contract, "s1_t02_d9_decoder", "2A 冻结 D9 参考实现")
    d6_path = check_bound_file(recorder, contract, "s1_t02_d6_metrics", "2A 冻结 D6 指标/stable_nms")
    samples_path = check_bound_file(recorder, contract, "s2a_t01_fixed_test_samples", "2A 固定样本清单")
    for relative in SOURCE_FILES:
        path = W4_ROOT / relative
        report["sources"].append(
            {"path": relative, "sha256": sha256_file(path) if path.exists() else None, "exists": path.exists()}
        )
    report["bindings"] = [
        {"id": "s4a_contract", "path": str(contract_path), "sha256": contract_sha},
        {"id": "t25_index", "path": str(index_path) if index_path else None},
        {"id": "t29_reference", "path": str(t29_path) if t29_path else None},
        {"id": "d9_decoder", "path": str(d9_path) if d9_path else None},
        {"id": "d6_metrics", "path": str(d6_path) if d6_path else None},
        {"id": "fixed_samples", "path": str(samples_path) if samples_path else None},
    ]
    if index_path is None or t29_path is None or d9_path is None or d6_path is None or samples_path is None:
        report["checks"] = recorder.checks
        write_json(evidence_dir / "offline_chain_summary.json", report)
        print("[s4b] 上游绑定缺失，无法继续；详见 evidence/offline_chain_summary.json", file=sys.stderr)
        return 1

    index = load_json(index_path)
    t29 = load_json(t29_path)
    index_samples = index["samples"]
    t29_samples = t29["samples"]
    shard_dir = Path(find_binding(contract, "s2a_t25_tensor_shards")["path"])
    recorder.record(
        "t25_shard_dir_present",
        shard_dir.is_dir() and len(list(shard_dir.glob("sample_*.zlib"))) == 109,
        "T25 分片目录只读引用（主树物化，工作树未物化）",
        "109 个 sample_NNN.zlib",
        "%d 个" % len(list(shard_dir.glob("sample_*.zlib"))),
    )

    # --- 编译 C ------------------------------------------------------------
    gcc = Path(args.gcc)
    binary = tmp_dir / "s4_offline_host.exe"
    compile_result = run_command(
        [str(gcc), *COMPILE_FLAGS, "-I", "vitis/stage4", *C_SOURCE_FILES, "-o", str(binary)], W4_ROOT
    )
    error_lines = [line for line in (compile_result["stdout"] + compile_result["stderr"]).splitlines() if " error" in line.lower()]
    warning_lines = [line for line in (compile_result["stdout"] + compile_result["stderr"]).splitlines() if " warning" in line.lower()]
    report["environment"]["gcc"] = run_command([str(gcc), "--version"], W4_ROOT)["stdout"].splitlines()[:1]
    report["commands"]["compile"] = {
        "command": compile_result["command"],
        "exit_code": compile_result["exit_code"],
        "elapsed_seconds": compile_result["elapsed_seconds"],
        "error_line_count": len(error_lines),
        "warning_line_count": len(warning_lines),
        "stderr_tail": compile_result["stderr"][-2000:],
    }
    recorder.record(
        "c_compile_zero_error",
        compile_result["exit_code"] == 0 and not error_lines,
        "d:\\mingw64\\bin\\gcc.exe 编译 S4-B C 源",
        "exit 0 且 0 error",
        "exit %s，error 行 %d，warning 行 %d" % (compile_result["exit_code"], len(error_lines), len(warning_lines)),
    )
    if compile_result["exit_code"] != 0 or error_lines:
        report["checks"] = recorder.checks
        write_json(evidence_dir / "offline_chain_summary.json", report)
        return 1
    report["commands"]["compile"]["binary_sha256"] = sha256_file(binary)

    # --- C 自检（CRC 检查向量 / pack-unpack 回读） --------------------------
    selftest_json = evidence_dir / "c_selftest.json"
    selftest_result = run_command(
        [str(binary), "--selftest", "--json", str(selftest_json)], W4_ROOT
    )
    report["commands"]["selftest"] = {
        "command": selftest_result["command"],
        "exit_code": selftest_result["exit_code"],
        "elapsed_seconds": selftest_result["elapsed_seconds"],
        "stdout": selftest_result["stdout"].strip(),
    }
    selftest_data = load_json(selftest_json)
    checks_by_name = {c["name"]: c for c in selftest_data["checks"]}
    recorder.record(
        "c_selftest_all_pass",
        selftest_result["exit_code"] == 0 and selftest_data.get("all_pass") is True,
        "C 自检全部通过（11 项：CRC/头/meta/框/整帧回读/篡改拒绝/扩展门闸）",
        "exit 0 且 all_pass=true",
        "exit %s，all_pass=%s" % (selftest_result["exit_code"], selftest_data.get("all_pass")),
    )
    crc_check = checks_by_name.get("crc32_check_vector_123456789", {})
    recorder.record(
        "c_crc32_check_vector",
        crc_check.get("pass") is True and crc_check.get("actual") == "0x%08X" % CRC_CHECK_VECTOR,
        "CRC32 自检 '123456789' -> 0xCBF43926",
        "0x%08X" % CRC_CHECK_VECTOR,
        crc_check.get("actual"),
    )
    recorder.record(
        "python_crc32_check_vector",
        crc32(b"123456789") == CRC_CHECK_VECTOR,
        "Python zlib 独立复核同一检查向量",
        "0x%08X" % CRC_CHECK_VECTOR,
        "0x%08X" % crc32(b"123456789"),
    )
    roundtrip_ok = all(
        checks_by_name.get(name, {}).get("pass") is True
        for name in (
            "header_pack_unpack_roundtrip",
            "meta_pack_unpack_roundtrip",
            "box_pack_unpack_roundtrip",
            "run_response_pack_unpack_roundtrip",
            "run_response_repack_byte_identical",
        )
    )
    recorder.record(
        "c_frame_pack_unpack_byte_readback",
        roundtrip_ok,
        "帧 pack->unpack->re-pack 字节回读一致（含双头与每框 48 B）",
        "全部一致",
        "一致" if roundtrip_ok else "存在不一致",
    )

    # --- 独立消费端：2B 冻结传输实现 ----------------------------------------
    transport_path = None
    transport_binding = find_binding(contract, "s2b_uart_transport")
    if transport_binding:
        candidate_path = Path(transport_binding["path"])
        for parent in candidate_path.parents if candidate_path.exists() else []:
            sibling = parent / "verification" / "s2b_board_transport.py"
            if sibling.is_file():
                transport_path = sibling
                break
    transport_module = None
    if transport_path is not None:
        try:
            transport_module = load_2b_transport(transport_path)
            report["bindings"].append(
                {"id": "s2b_transport_reference", "path": str(transport_path), "sha256": sha256_file(transport_path)}
            )
        except Exception as exc:  # pragma: no cover - 记录而不掩盖
            recorder.record("frozen_2b_transport_import", False, "只读导入 2B 传输失败：%s" % exc)
            transport_module = None
    if transport_module is None:
        recorder.record(
            "frozen_2b_transport_import",
            None,
            "未找到/未导入 2B 冻结传输实现，跳过独立消费端核验",
        )
    else:
        recorder.record("frozen_2b_transport_import", True, "已只读导入 2B 冻结传输实现作为独立消费端")

    # --- 逐样本链 ----------------------------------------------------------
    for position, sample_index in enumerate(sample_indices):
        ordinal = position + 1
        if not 0 <= sample_index < len(index_samples):
            print("[s4b] 样本索引越界：%d" % sample_index, file=sys.stderr)
            return 2
        index_sample = index_samples[sample_index]
        t29_sample = t29_samples[sample_index]
        sample_id = t29_sample["sample_id"]
        frame_id = t29_sample["frame_id"]
        geometry_wh = t29_sample["input"]["geometry_wh"]
        width, height = geometry_wh[0], geometry_wh[1]
        sample_record: dict = {
            "sample_index": sample_index,
            "sample_id": sample_id,
            "frame_id": frame_id,
            "geometry": {"width": width, "height": height},
        }
        # 先登记引用再填充，保证即使中途 early-continue 也保留已核验的部分证据。
        report["samples"].append(sample_record)
        recorder.record(
            "sample%d.index_vs_t29_identity" % sample_index,
            index_sample["sample_id"] == sample_id and index_sample["frame_id"] == frame_id,
            "%s T25 索引与 T29 参考的 sample_id/frame_id 一致（同一冻结样本）" % sample_id,
            "%s/frame_id=%d" % (sample_id, frame_id),
            "%s/frame_id=%s" % (index_sample["sample_id"], index_sample["frame_id"]),
        )

        shard_relative = index_sample["network"]["compressed_shard"]["path"]
        shard_path = shard_dir / Path(shard_relative).name
        sample_record["shard"] = {
            "path": str(shard_path),
            "bytes": shard_path.stat().st_size if shard_path.exists() else None,
            "sha256": sha256_file(shard_path) if shard_path.exists() else None,
            "expected_sha256": index_sample["network"]["compressed_shard"]["sha256"],
        }
        recorder.record(
            "sample%d.shard_binding" % sample_index,
            shard_path.exists() and sample_record["shard"]["sha256"] == sample_record["shard"]["expected_sha256"],
            "%s zlib 分片只读引用与 SHA-256 绑定" % sample_id,
            sample_record["shard"]["expected_sha256"],
            sample_record["shard"]["sha256"],
        )
        if not shard_path.exists():
            continue

        stream = zlib.decompress(shard_path.read_bytes())
        stream_sha = sha256_bytes(stream)
        index_network = index_sample["network"]
        t29_shard = next(
            (s for s in t29["shard_bindings"] if s["sample_index"] == sample_index), None
        )
        expected_stream_sha = index_network["raw_stream_sha256"]
        expected_stream_bytes = index_network["unique_output_raw_bytes"]
        sample_record["stream"] = {
            "bytes": len(stream),
            "sha256": stream_sha,
            "expected_sha256": expected_stream_sha,
            "expected_bytes": expected_stream_bytes,
            "t29_decompressed_sha256": t29_shard["decompressed_sha256"] if t29_shard else None,
        }
        recorder.record(
            "sample%d.stream_binding" % sample_index,
            len(stream) == expected_stream_bytes
            and stream_sha == expected_stream_sha
            and (t29_shard is None or stream_sha == t29_shard["decompressed_sha256"]),
            "%s 解压后逐层 raw 层流长度/SHA-256 绑定（T25 索引与 T29 双方一致）" % sample_id,
            expected_stream_sha,
            stream_sha,
        )

        heads_record = {}
        heads_ok = True
        for head_name, length, layer_index in (
            ("head13", HEAD13_BYTES, 29),
            ("head26", HEAD26_BYTES, 36),
        ):
            t29_head = t29_sample["head_tensors"][head_name]
            index_layer = next(
                t for t in index_network["tensors"] if t["layer_index"] == layer_index
            )
            offset = t29_head["byte_offset"]
            blob = stream[offset : offset + length]
            blob_sha = sha256_bytes(blob)
            entry = {
                "byte_offset": offset,
                "byte_length": length,
                "int8_scale": t29_head["int8_scale"],
                "tensor_sha256": blob_sha,
                "expected_tensor_sha256": t29_head["tensor_sha256"],
                "index_layer_index": index_layer["layer_index"],
                "index_byte_offset": index_layer["byte_offset"],
                "index_byte_length": index_layer["byte_length"],
                "index_scale": index_layer["scale"],
                "index_tensor_sha256": index_layer["tensor_sha256"],
                "first8_hex": blob[:8].hex(),
            }
            heads_record[head_name] = entry
            offsets_agree = (
                index_layer["byte_offset"] == offset
                and index_layer["byte_length"] == length
                and index_layer["scale"] == t29_head["int8_scale"]
                and index_layer["tensor_sha256"] == t29_head["tensor_sha256"]
            )
            recorder.record(
                "sample%d.%s_extraction_binding" % (sample_index, head_name),
                blob_sha == t29_head["tensor_sha256"] and offsets_agree,
                "%s %s 按 T25 索引偏移抽取，T25 索引与 T29 的偏移/scale/SHA 一致" % (sample_id, head_name),
                t29_head["tensor_sha256"],
                blob_sha,
            )
            heads_ok = heads_ok and blob_sha == t29_head["tensor_sha256"]
        sample_record["heads"] = heads_record
        head13 = stream[
            heads_record["head13"]["byte_offset"] : heads_record["head13"]["byte_offset"] + HEAD13_BYTES
        ]
        head26 = stream[
            heads_record["head26"]["byte_offset"] : heads_record["head26"]["byte_offset"] + HEAD26_BYTES
        ]
        if not heads_ok:
            continue

        # --- bundle -> C host ---
        bundle_path = tmp_dir / ("bundle_%s.bin" % sample_id)
        bundle_record = build_bundle(
            bundle_path,
            width=width,
            height=height,
            frame_id=frame_id,
            sequence=ordinal,
            result_seq=ordinal,
            threshold=SCORE_THRESHOLD,
            head13_scale=heads_record["head13"]["int8_scale"],
            head26_scale=heads_record["head26"]["int8_scale"],
            head13=head13,
            head26=head26,
        )
        sample_record["bundle"] = bundle_record

        host_json = tmp_dir / ("host_result_%s.json" % sample_id)
        frame_path = tmp_dir / ("frame_%s.bin" % sample_id)
        heads_dir = tmp_dir / ("heads_%s" % sample_id)
        heads_dir.mkdir(parents=True, exist_ok=True)
        host_result = run_command(
            [
                str(binary),
                "--bundle",
                str(bundle_path),
                "--json",
                str(host_json),
                "--frame",
                str(frame_path),
                "--heads-dir",
                str(heads_dir),
            ],
            W4_ROOT,
        )
        sample_record["host"] = {
            "command": host_result["command"],
            "exit_code": host_result["exit_code"],
            "elapsed_seconds": host_result["elapsed_seconds"],
            "stdout": host_result["stdout"].strip(),
            "stderr_tail": host_result["stderr"][-1000:],
        }
        recorder.record(
            "sample%d.host_exit_zero" % sample_index,
            host_result["exit_code"] == 0,
            "%s 主机链（解码->打包->解帧回读）退出码" % sample_id,
            "exit 0",
            "exit %s" % host_result["exit_code"],
        )
        if host_result["exit_code"] != 0 or not host_json.exists():
            continue
        host_data = load_json(host_json)
        sample_record["host_result"] = host_data

        # 证据归档：C 出参 JSON、帧原字节、C 侧回写的 INT8 副本
        shutil.copyfile(host_json, evidence_dir / host_json.name)
        shutil.copyfile(frame_path, evidence_dir / frame_path.name)
        for name in ("head13.raw", "head26.raw"):
            shutil.copyfile(heads_dir / name, evidence_dir / ("%s_%s" % (sample_id, name)))

        # --- 进出一致：C 回写的 INT8 副本 ---
        emitted13 = (heads_dir / "head13.raw").read_bytes()
        emitted26 = (heads_dir / "head26.raw").read_bytes()
        sample_record["head_bytes_roundtrip"] = {
            "head13_in_sha256": sha256_bytes(head13),
            "head13_out_sha256": sha256_bytes(emitted13),
            "head26_in_sha256": sha256_bytes(head26),
            "head26_out_sha256": sha256_bytes(emitted26),
            "frozen_head13_sha256": heads_record["head13"]["expected_tensor_sha256"],
            "frozen_head26_sha256": heads_record["head26"]["expected_tensor_sha256"],
            "c_reported_unchanged": host_data.get("head_bytes_unchanged"),
        }
        recorder.record(
            "sample%d.head_int8_bytes_unchanged" % sample_index,
            head13 == emitted13
            and head26 == emitted26
            and sha256_bytes(emitted13) == heads_record["head13"]["expected_tensor_sha256"]
            and sha256_bytes(emitted26) == heads_record["head26"]["expected_tensor_sha256"]
            and host_data.get("head_bytes_unchanged") is True,
            "%s head13/head26 INT8 原字节进出一致且等于 2A 冻结 tensor_sha256" % sample_id,
            heads_record["head13"]["expected_tensor_sha256"],
            sha256_bytes(emitted13),
        )

        # --- 独立解帧 ---
        frame_bytes = frame_path.read_bytes()
        try:
            parsed = parse_frame(
                frame_bytes,
                expect_sequence=ordinal,
                expect_frame_id=frame_id,
                expect_size=(width, height),
            )
            frame_error = None
        except ValueError as exc:
            parsed = None
            frame_error = str(exc)
        recorder.record(
            "sample%d.frame_independent_unpack" % sample_index,
            parsed is not None,
            "%s 独立（非 C、非 2B 代码）解帧：头/payload CRC、op、seq、frame、几何、长度" % sample_id,
            "解帧成功",
            "失败：%s" % frame_error if frame_error else "成功",
        )
        if parsed is None:
            continue
        sample_record["frame"] = {
            "bytes": len(frame_bytes),
            "sha256": sha256_bytes(frame_bytes),
            "header": parsed["header"],
            "meta": parsed["meta"],
        }

        # 帧 pack->unpack 字节回读一致（独立重打包）
        repacked = repack_frame(parsed)
        recorder.record(
            "sample%d.frame_repack_byte_identical" % sample_index,
            repacked == frame_bytes,
            "%s 独立重打包与 C 帧原字节逐字节相同（pack->unpack 回读一致）" % sample_id,
            sha256_bytes(frame_bytes),
            sha256_bytes(repacked),
        )
        # C 自报的回读结论
        recorder.record(
            "sample%d.c_readback_flags" % sample_index,
            all(
                host_data["readback"][key] is True
                for key in ("field_identical", "heads_identical", "boxes_identical", "repack_byte_identical")
            ),
            "%s C 侧 pack/unpack 回读标记（字段/双头/框/re-pack 字节）" % sample_id,
            "全部 true",
            json.dumps(host_data["readback"], ensure_ascii=False),
        )
        # 帧内双头 == 冻结头
        recorder.record(
            "sample%d.frame_heads_frozen_identical" % sample_index,
            parsed["head13"] == head13 and parsed["head26"] == head26,
            "%s 帧内双头 INT8 与抽取自冻结分片的原字节逐字节相同" % sample_id,
            heads_record["head13"]["expected_tensor_sha256"],
            sha256_bytes(parsed["head13"]),
        )

        # --- Python D9 对拍 ---
        python_predictions, python_candidates = python_d9_decode(
            head13,
            head26,
            width,
            height,
            heads_record["head13"]["int8_scale"],
            heads_record["head26"]["int8_scale"],
            SCORE_THRESHOLD,
        )
        comparison = compare_detections(parsed["boxes"], python_predictions, args.tolerance)
        sample_record["python_d9"] = {
            "detection_count": len(python_predictions),
            "candidate_count": len(python_candidates),
            "detections": [
                {
                    "class_id": p.class_id,
                    "class_name": p.name,
                    "score": p.confidence,
                    "xyxy": list(p.box),
                    "source_order": p.source_order,
                }
                for p in python_predictions
            ],
        }
        sample_record["comparison_c_vs_python_d9"] = comparison
        recorder.record(
            "sample%d.c_vs_python_d9_discrete" % sample_index,
            not comparison["count_mismatch"] and comparison["discrete_mismatch_count"] == 0,
            "%s C 与 Python D9 逐框离散字段（框数/class_id/class_name/source_order）完全相同" % sample_id,
            "0 mismatch",
            "count_mismatch=%s, discrete_mismatch=%d"
            % (comparison["count_mismatch"], comparison["discrete_mismatch_count"]),
        )
        recorder.record(
            "sample%d.c_vs_python_d9_tolerance" % sample_index,
            comparison["tolerance_exceeded"] == 0
            and comparison["score_max_abs_error"] <= args.tolerance
            and comparison["xyxy_max_abs_error"] <= args.tolerance,
            "%s C 与 Python D9 的 score/xyxy 绝对误差 <= %g" % (sample_id, args.tolerance),
            "max_abs <= %g" % args.tolerance,
            "score=%.3e, xyxy=%.3e, exceeded=%d"
            % (
                comparison["score_max_abs_error"],
                comparison["xyxy_max_abs_error"],
                comparison["tolerance_exceeded"],
            ),
        )
        recorder.record(
            "sample%d.candidate_count_matches_d9" % sample_index,
            parsed["meta"]["raw_candidate_count"] == len(python_candidates)
            and host_data["candidate_count"] == len(python_candidates),
            "%s candidate_count（契约口径：阈值后/NMS 前）与 UART raw_candidate_count 均等于 Python D9 候选数" % sample_id,
            len(python_candidates),
            "record=%s, UART=%s"
            % (host_data["candidate_count"], parsed["meta"]["raw_candidate_count"]),
        )
        recorder.record(
            "sample%d.candidate_count_matches_t29" % sample_index,
            host_data["candidate_count"] == t29_sample["raw_candidate_count_before_stable_nms"]
            and parsed["meta"]["raw_candidate_count"] == t29_sample["raw_candidate_count_before_stable_nms"],
            "%s candidate_count 与 UART raw_candidate_count 均等于 2A T29 冻结参考（可被黄金独立验证）" % sample_id,
            t29_sample["raw_candidate_count_before_stable_nms"],
            host_data["candidate_count"],
        )
        # S4-A 可选诊断字段：阈值前候选机会数 = 5 * 正面积候选框数，且不得替代 candidate_count。
        pre_threshold_ok = (
            host_data["candidate_count_pre_threshold"] == 5 * host_data["candidate_box_count"]
            and host_data["candidate_count_pre_threshold"] >= host_data["candidate_count"]
        )
        recorder.record(
            "sample%d.candidate_count_pre_threshold_consistent" % sample_index,
            pre_threshold_ok,
            "%s candidate_count_pre_threshold == 5 * candidate_box_count 且不小于 candidate_count" % sample_id,
            "5 * candidate_box_count",
            "%s vs 5 * %s（candidate_count=%s）"
            % (
                host_data["candidate_count_pre_threshold"],
                host_data["candidate_box_count"],
                host_data["candidate_count"],
            ),
        )
        recorder.record(
            "sample%d.candidate_count_semantics_resolved" % sample_index,
            host_data.get("candidate_count_semantics", {}).get("divergence_open") is False,
            "%s 候选数口径冲突已由 S4-A 契约修订裁决（candidate_count=阈值后/NMS 前，pre_threshold 为可选诊断）" % sample_id,
            "divergence_open=false",
            json.dumps(host_data.get("candidate_count_semantics", {}), ensure_ascii=False)[:200],
        )
        scope = host_data.get("measurement_scope", {})
        recorder.record(
            "sample%d.timing_sentinel_not_fabricated" % sample_index,
            all(host_data[name] == 0 for name in
                ("capture_time_ns", "result_time_ns", "inference_time_ns", "end_to_end_latency_ns"))
            and scope.get("pl_timing") == "NOT_EXECUTED_OFFLINE"
            and scope.get("uart_transport") == "NOT_EXECUTED_OFFLINE"
            and scope.get("board_pl") == "NOT_EXECUTED_OFFLINE"
            and set(scope.get("unavailable_fields", []))
            >= {"capture_time_ns", "result_time_ns", "inference_time_ns", "end_to_end_latency_ns"},
            "%s 离线无 PL：四个时间字段为 0 哨兵，measurement_scope 按契约键名标注三项 NOT_EXECUTED_OFFLINE" % sample_id,
            "0 哨兵 + pl_timing/uart_transport/board_pl=NOT_EXECUTED_OFFLINE",
            json.dumps(scope, ensure_ascii=False),
        )
        recorder.record(
            "sample%d.candidate_overflow_explicitly_false" % sample_index,
            "candidate_overflow" in host_data and host_data["candidate_overflow"] is False
            and host_data["candidate_limit"] == CANDIDATE_LIMIT_EXPECTED,
            "%s candidate_overflow 字段保留并显式记录“未超限”（硬错误路径、无候选截断；上限 12675 = 理论上界，恒 false）" % sample_id,
            "字段存在且为 false，上限 12675",
            "overflow=%s, limit=%s"
            % (host_data.get("candidate_overflow"), host_data.get("candidate_limit")),
        )
        recorder.record(
            "sample%d.max_outputs_is_15" % sample_index,
            host_data["detection_count"] <= 15
            and len(host_data["detections"]) <= 15,
            "%s NMS 后输出上限 15（2A 冻结）与候选缓冲上限 12675 不得混用" % sample_id,
            "detection_count <= 15",
            "%s" % host_data["detection_count"],
        )
        # --- 与 T29 冻结参考框交叉确认 ---
        t29_comparison = compare_with_t29(parsed["boxes"], t29_sample["detections"], args.tolerance)
        sample_record["comparison_c_vs_t29_reference"] = t29_comparison
        recorder.record(
            "sample%d.c_vs_t29_reference" % sample_index,
            not t29_comparison["count_mismatch"]
            and t29_comparison["discrete_mismatch_count"] == 0
            and t29_comparison["tolerance_exceeded"] == 0,
            "%s C 结果与 2A T29 冻结参考框逐框一致（独立黄金交叉确认）" % sample_id,
            "0 mismatch",
            "count_mismatch=%s, discrete=%d, exceeded=%d"
            % (
                t29_comparison["count_mismatch"],
                t29_comparison["discrete_mismatch_count"],
                t29_comparison["tolerance_exceeded"],
            ),
        )
        # --- C 结果 JSON 字段名对齐 S4-A ---
        missing_result = [name for name in required_result_fields if name not in host_data]
        missing_detection = [
            name
            for name in required_detection_fields
            if name != "xyxy_px" and any(name not in det for det in host_data.get("detections", []))
        ]
        sample_record["s4a_field_check"] = {
            "missing_result_fields": missing_result,
            "missing_detection_fields": missing_detection,
            "state": host_data.get("state"),
            "state_enum": sorted(contract.get("state_enum", {}).keys()),
        }
        recorder.record(
            "sample%d.s4a_field_names" % sample_index,
            not missing_result and not missing_detection,
            "%s C 结果 JSON 覆盖 S4-A result_record/detection_record 权威字段名" % sample_id,
            "无缺失",
            "缺失 result=%s detection=%s" % (missing_result, missing_detection),
        )
        state_ok = host_data.get("state") in ("OK", "NO_HAND", "TIMEOUT", "ERROR", "DROPPED")
        detection_count_ok = host_data.get("detection_count") == len(host_data.get("detections", []))
        state_consistency = (
            state_ok
            and detection_count_ok
            and (
                (host_data.get("state") == "OK" and host_data.get("detection_count", 0) >= 1)
                or (host_data.get("state") == "NO_HAND" and host_data.get("detection_count") == 0)
            )
        )
        recorder.record(
            "sample%d.state_and_count_consistency" % sample_index,
            state_consistency,
            "%s state 属 S4-A state_enum，且 detection_count == len(detections) 并符合 OK/NO_HAND 口径" % sample_id,
            "state=OK(>=1框) 或 NO_HAND(0框)",
            "state=%s, detection_count=%s"
            % (host_data.get("state"), host_data.get("detection_count")),
        )
        # --- 2B 冻结传输实现的独立消费端核验 ---
        if transport_module is not None:
            try:
                request = transport_module.Header(
                    2,
                    ordinal,
                    frame_id,
                    width,
                    height,
                    1,
                    len(frame_bytes) - transport_module.HEADER.size,
                    transport_module.zlib.crc32(frame_bytes[transport_module.HEADER.size :]),
                )
                meta_2b, heads_2b, detections_2b = transport_module.decode_response(
                    frame_bytes[: transport_module.HEADER.size],
                    frame_bytes[transport_module.HEADER.size :],
                    request,
                    0,
                    0,
                )
                accepted = (
                    len(detections_2b) == len(parsed["boxes"])
                    and heads_2b["head13"] == head13
                    and heads_2b["head26"] == head26
                    and all(
                        a["class_id"] == b["class_id"]
                        and a["source_order"] == b["source_order"]
                        and a["score"] == b["score"]
                        and a["xyxy"] == b["xyxy"]
                        for a, b in zip(detections_2b, parsed["boxes"])
                    )
                )
                detail = "2B decode_response 接受该帧：meta=%s" % json.dumps(meta_2b, ensure_ascii=False)
            except Exception as exc:  # noqa: BLE001 - 记录真实拒绝原因
                accepted = False
                detail = "2B decode_response 拒绝该帧：%s" % exc
            recorder.record(
                "sample%d.frozen_2b_transport_accepts_frame" % sample_index,
                accepted,
                "%s 2B 冻结传输实现作为独立消费端核对帧（未修改 2B 代码）" % sample_id,
                "接受且双头/框一致",
                detail,
            )

        sample_record["host_process_elapsed_seconds"] = host_result["elapsed_seconds"]

    # --- 收尾 --------------------------------------------------------------
    report["checks"] = recorder.checks

    # 与 Lead 裁决 r04 的逐项对齐清单（机器可读，供 Reviewer 直接核对）。
    sample_results = [s.get("host_result") for s in report["samples"] if s.get("host_result")]
    # 契约哈希项：运行期读出值如实记录；期望值缺省即读出值（不硬编码历史哈希）。
    contract_hash_item = {
        "item": "契约 SHA-256（运行期读出，不硬编码）",
        "expectation": "从 docs/stage4/s4a_stage4_g0_fields.json 现场读出 sha256 并如实记录；"
        "--expected-contract-sha256 缺省时取读出值",
        "actual": "读出 sha256=%s；期望值=%s" % (contract_sha, expected_contract_sha),
        "status": "ALIGNED" if contract_sha == expected_contract_sha else "MISMATCH",
    }
    # 语义不变量逐项计算（任一 MISMATCH 记 FAIL，不得 SKIP）。
    header_texts = "\n".join(
        (W4_ROOT / path).read_text(encoding="utf-8")
        for path in ("vitis/stage4/s4_ps_decode.h", "vitis/stage4/s4_uart_protocol.h")
    )
    semantic_items = semantic_alignment(contract, report, args.tolerance, header_texts)
    report["s4a_alignment"] = {
        "contract_sha256_at_run": contract_sha,
        "expected_contract_sha256": expected_contract_sha,
        "judgement_basis": "契约哈希运行期读出并记录（不硬编码历史值）；对齐判定以字段名/语义/常量不变量为准"
        "（candidate_count 阈值后/15 框截断前/NMS 前、candidate_count_pre_threshold 可选诊断、candidate_limit=12675 硬错误语义、"
        "score_threshold=0.25 含等号、nms_iou=0.45、<=15 框、5 类、两头 5070/20280 与 scale、容限 1e-6/相对 0、"
        "state_enum 5 态、<ii5d> 48 B、measurement_scope 4 键）",
        "contract_hash_item": contract_hash_item,
        "items": semantic_items,
        "all_aligned": all(item["status"] == "ALIGNED" for item in semantic_items),
    }
    # 语义对齐项逐项判定：任一不符即 FAIL（不得降级为 SKIP）。
    for item in semantic_items:
        recorder.record(
            "s4a_alignment.%s" % re.sub(r"[\W]+", "_", item["item"]).strip("_"),
            item["status"] == "ALIGNED",
            "S4-A 语义对齐：%s" % item["item"],
            item["expectation"],
            item["actual"],
        )

    report["check_summary"] = recorder.summary()
    failures = recorder.failures()
    report["status"] = "PASS" if not failures else "FAIL"
    report["failed_checks"] = [f["name"] for f in failures]
    report["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    report["tmp_dir"] = str(tmp_dir)
    report["evidence_dir"] = str(evidence_dir)
    report["limitations"].append(
        "只执行轻量 Python 与 d:\\mingw64 gcc 编译；未启动 Vivado/xsim，未争用 2B 硬件会话"
    )

    write_json(evidence_dir / "offline_chain_summary.json", report)
    write_json(evidence_dir / "s4a_alignment.json", report["s4a_alignment"])
    summary_lines = [
        "S4-B 离线集成链 run_id=%s" % args.run_id,
        "status=%s  checks: PASS=%d FAIL=%d SKIP=%d" % (
            report["status"],
            report["check_summary"]["pass"],
            report["check_summary"]["fail"],
            report["check_summary"]["skip"],
        ),
        "evidence=%s" % evidence_dir,
    ]
    if failures:
        summary_lines.append("failed checks:")
        for failure in failures:
            summary_lines.append("  - %s: %s" % (failure["name"], failure["detail"]))
    (evidence_dir / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(summary_lines))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())