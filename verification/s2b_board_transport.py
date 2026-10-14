#!/usr/bin/env python3
"""候选S2BU UART传输、原字节采集与冻结黄金核验；不下载程序或配置PL。"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
import zlib

ROOT = Path(__file__).absolute().parents[1]
HEADER = struct.Struct("<4sHH8I")
META = struct.Struct("<Q8I")
BOX = struct.Struct("<ii5d")
INPUT_BYTES, WEIGHT_BYTES = 519168, 5903100
HEAD_LENGTHS = {"head13": 5070, "head26": 20280}
CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
MAX_RESPONSE = META.size + sum(HEAD_LENGTHS.values()) + 15 * BOX.size
MODEL_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
SAMPLES_SHA = "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"
CPU_D9_SHA = "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"
OP_WEIGHTS, OP_RUN, OP_DIAG, OP_CACHE_PROBE = 1, 2, 3, 4
SAFE_MASK = (1 << 10) | (1 << 11)
UNSAFE_MASK = (1 << 8) | (1 << 12) | (1 << 13)


class TransportError(ValueError):
    """传输、资产绑定或结果身份不满足候选契约。"""


def require(condition, message):
    """失败立即停止，保留此前原字节与记录。"""
    if not condition:
        raise TransportError(message)


def digest(raw):
    """计算原字节SHA-256。"""
    return hashlib.sha256(raw).hexdigest()


def exact_path(raw, kind="file"):
    """按完整磁盘名称核对目标类型，不修正来源字符串。"""
    path = Path(raw)
    require(path.is_absolute() and not any(part in {".", ".."} for part in path.parts), f"需要精确绝对路径：{raw}")
    root_parts = ROOT.parts
    if len(path.parts) >= len(root_parts) and path.parts[:len(root_parts)] == root_parts:
        current = ROOT
        remaining = path.parts[len(root_parts):]
    else:
        current = Path(path.anchor)
        remaining = path.parts[1:]
    for part in remaining:
        try:
            with os.scandir(current) as scan:
                entries = {entry.name: entry for entry in scan}
        except OSError as exc:
            raise TransportError(f"无法核验精确路径目录 {current}: {exc}") from exc
        require(part in entries, f"精确路径不存在：{current / part}")
        current = Path(entries[part].path)
    require(current.is_file() if kind == "file" else current.is_dir(), f"目标类型不符：{current}")
    return current


def new_directory(raw, parent=None):
    """新运行名称必须未存在，禁止覆盖失败或既有RunId。"""
    path = Path(raw)
    actual_parent = exact_path(path.parent, "directory")
    if parent is not None:
        require(path.parent == parent, "新运行只能在指定证据父目录")
    require(not any(entry.name.casefold() == path.name.casefold() for entry in os.scandir(actual_parent)), f"拒绝覆盖：{path}")
    path.mkdir()
    return exact_path(path, "directory")


def write_json_new(path, value):
    """UTF-8/LF创建机器记录，禁止覆盖。"""
    exact_path(path.parent, "directory")
    require(not path.exists(), f"拒绝覆盖：{path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


@dataclass(frozen=True)
class Header:
    """S2BU固定40-byte头；字段按little-endian显式编码。"""
    op: int
    sequence: int
    frame: int
    width: int
    height: int
    repeat: int
    length: int
    payload_crc: int

    def pack(self):
        require(type(self.op) is int and 0 <= self.op <= 0xFFFF, "op范围错误")
        values = (self.sequence, self.frame, self.width, self.height, self.repeat, self.length, self.payload_crc)
        require(all(type(value) is int and 0 <= value <= 0xFFFFFFFF for value in values), "header整数范围错误")
        raw = HEADER.pack(b"S2BU", 1, self.op, *values, 0)
        return raw[:36] + struct.pack("<I", zlib.crc32(raw[:36]))

    @classmethod
    def unpack(cls, raw):
        require(len(raw) == HEADER.size, "header截断或长度错误")
        magic, version, op, *values = HEADER.unpack(raw)
        require(magic == b"S2BU" and version == 1, "header magic/version错误")
        require(zlib.crc32(raw[:36]) == values[-1], "header CRC错误")
        return cls(op, *values[:-1])


def make_request(op, sequence, frame, payload, *, width=0, height=0, repeat=1):
    """CPU参数候选与固定payload长度先验证后编码。"""
    require(type(sequence) is int and 1 <= sequence < 0xFFFFFFFF, "sequence必须单调且不能耗尽")
    expected = {OP_WEIGHTS: WEIGHT_BYTES, OP_RUN: INPUT_BYTES + 8, OP_DIAG: 12, OP_CACHE_PROBE: 12}
    require(op in expected and len(payload) == expected[op], "请求op/payload长度错误")
    if op == OP_RUN:
        require(type(repeat) is int and 1 <= repeat <= 1000, "repeat必须1..1000")
        require(1 <= width <= 65535 and 1 <= height <= 65535, "图像几何错误")
        require(0 <= frame <= 0xFFFFFFFF - (repeat - 1), "frame递增溢出")
        core, drain = struct.unpack_from("<II", payload)
        require(core > 0 and drain > 0, "CORE/DRAIN deadline必须非零")
    else:
        require(width == 0 and height == 0 and repeat == 1, "非RUN头几何/repeat错误")
        if op == OP_CACHE_PROBE:
            phase, cpu_seed, dap_seed = struct.unpack("<III", payload)
            require(frame == 0 and phase in (0, 1) and cpu_seed != dap_seed, "CACHE_PROBE phase/frame/seed错误")
    head = Header(op, sequence, frame, width, height, repeat, len(payload), zlib.crc32(payload))
    return head, head.pack()


def decode_response(header_raw, payload, request, index, previous_epoch, *, abort_ready=False):
    """CRC、身份、安全状态、全部head及框先核对，失败响应不生成捕获帧。"""
    head = Header.unpack(header_raw)
    require(head.op == (request.op | 0x8000) and head.sequence == request.sequence, "响应op/sequence不匹配或重复")
    require((head.frame, head.width, head.height, head.repeat) ==
            (request.frame + index, request.width, request.height, request.repeat), "响应frame/几何/repeat不匹配")
    require(META.size <= head.length <= MAX_RESPONSE and len(payload) == head.length, "响应payload长度错误或截断")
    require(zlib.crc32(payload) == head.payload_crc, "响应payload CRC错误")
    epoch, status, error, reject, raw_count, count, actual_index, total, code = META.unpack_from(payload)
    require(actual_index == index and total == request.repeat, "响应index/total丢失、重复或乱序")
    require(0 <= code <= 10 and 0 <= error <= 12 and 0 <= reject <= 6, "未知响应/硬件诊断码")
    require(status & ~0x3F07 == 0, "PHYS_STATUS保留位必须为零")
    require(count <= 15 and raw_count <= 12675 and count <= raw_count, "框数/候选数错误")
    meta = {"epoch": epoch, "phys_status": status, "error_code": error, "last_reject": reject,
            "raw_candidate_count": raw_count, "box_count": count, "index": actual_index, "total": total, "response_code": code}
    if abort_ready:
        require(request.op == OP_DIAG and code == 10 and index == 0 and request.repeat == 1 and
                epoch == previous_epoch + 1 and status & 7 in (1, 2) and status & (1 << 8) and
                status & (SAFE_MASK | (1 << 9)) == 0 and error == 0 and count == 0 and raw_count == 0 and len(payload) == META.size,
                "WAIT_DAP_ABORT没有匹配的seq/frame/epoch或ARMING/RUN所有权")
        return meta, {}, []
    require(code != 10, "中间WAIT_DAP_ABORT只能由专用API消费，禁止当最终成功")
    if request.op == OP_CACHE_PROBE:
        require(len(payload) == META.size + 256 and count == 0 and raw_count == 0 and epoch == 0 and
                status & 7 == 0 and status & (1 << 10) and
                status & (UNSAFE_MASK | (1 << 9) | (1 << 11)) == 0 and error == 0, "CACHE_PROBE响应状态/长度错误")
        require(code in (0, 7), "CACHE_PROBE响应码错误")
        meta["probe_bytes"] = payload[META.size:]
        require(code == 0, f"CACHE_PROBE失败，实际原字节已保留：{payload[META.size:].hex()}")
        return meta, {}, []
    if code != 0:
        require(len(payload) == META.size and count == 0 and raw_count == 0, "失败响应不能携带成功结果")
        raise TransportError(f"板端失败，诊断={meta}")
    if request.op != OP_RUN:
        require(len(payload) == META.size and count == 0 and raw_count == 0, "非RUN响应不能携带检测结果")
        idle = status & 7 == 0 and status & (1 << 10) and status & (UNSAFE_MASK | (1 << 9) | (1 << 11)) == 0 and error == 0
        require(request.op in (OP_WEIGHTS, OP_DIAG), "未知非RUN响应op")
        if request.op == OP_WEIGHTS or idle:
            require(idle and epoch == previous_epoch, "IDLE响应状态/epoch错误")
        else:
            require(request.op == OP_DIAG and status & 7 == 5 and status & SAFE_MASK == SAFE_MASK and
                    status & (UNSAFE_MASK | (1 << 9)) == 0 and error in (3, 8) and epoch == previous_epoch + 1,
                    "DIAGNOSTICS没有匹配的ERROR_SAFE终态")
        return meta, {}, []
    require((status & 7) == 4 and status & SAFE_MASK == SAFE_MASK and status & (1 << 9) and
            status & UNSAFE_MASK == 0 and error == 0, "RUN结果不是DONE_SAFE/HEAD_VALID")
    require(type(previous_epoch) is int and epoch == previous_epoch + 1 and epoch <= 0xFFFFFFFFFFFFFFFF, "RUN epoch丢失、重复或倒退")
    require(len(payload) == META.size + sum(HEAD_LENGTHS.values()) + count * BOX.size, "RUN成功必须携带完整双头和所有框")
    offset, heads, detections, orders = META.size, {}, [], set()
    for name, length in HEAD_LENGTHS.items():
        heads[name] = payload[offset:offset + length]
        offset += length
    for _ in range(count):
        class_id, order, score, x1, y1, x2, y2 = BOX.unpack_from(payload, offset)
        offset += BOX.size
        require(0 <= class_id < 5 and 0 <= order < 12675 and order % 5 == class_id and order not in orders, "框类别/source_order错误")
        require(all(math.isfinite(value) for value in (score, x1, y1, x2, y2)) and
                0.25 <= score <= 1 and 0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1, "框值非有限、越界或零面积")
        orders.add(order)
        detections.append({"class_id": class_id, "class_name": CLASS_NAMES[class_id], "source_order": order,
                           "score": score, "xyxy": [x1, y1, x2, y2]})
    return meta, heads, detections


class WireSession:
    """有界串口读取/写入与原字节保存；不丢弃缓冲，不自动重同步或重试任务。"""
    def __init__(self, stream, rx_file, tx_header_file, *, response_timeout=450.0):
        self.stream, self.rx_file, self.tx_header_file = stream, rx_file, tx_header_file
        require(math.isfinite(response_timeout) and response_timeout > 0, "响应观察期限错误")
        self.response_timeout = response_timeout
        self.events, self.epoch, self.last_sequence = [], 0, 0
        self.failed = False
        self.abort_pending = None

    def read_exact(self, length, deadline):
        """每次真实收到的原字节立即保存，截断/超时非零失败。"""
        require(0 <= length <= MAX_RESPONSE, "读取长度超过候选上限")
        result = bytearray()
        while len(result) < length:
            require(time.monotonic() < deadline, f"UART读超时：{len(result)}/{length}")
            raw = self.stream.read(min(4096, length - len(result)))
            require(isinstance(raw, bytes) and len(raw) <= length - len(result), "串口read返回错误类型/长度")
            if raw:
                self.rx_file.write(raw); self.rx_file.flush(); result.extend(raw)
        return bytes(result)

    def banner(self, source_sha, xsa_sha):
        """启动ASCII行最大320B，精确绑定应用源码/XSA/model；随后只读二进制帧。"""
        raw = bytearray()
        deadline = time.monotonic() + self.response_timeout
        while not raw.endswith(b"\r\n"):
            require(len(raw) < 320, "启动banner超过长度上限")
            raw.extend(self.read_exact(1, deadline))
        expected = f"S2B-INFERENCE/1 READY SOURCE={source_sha} XSA={xsa_sha} MODEL={MODEL_SHA}\r\n".encode("ascii")
        require(bytes(raw) == expected, "启动banner或构建身份不匹配")
        return {"bytes": len(raw), "sha256": digest(raw), "text": raw.decode("ascii")}

    def send(self, request, header, payload, source_binding):
        """发送前记录来源和计划payload哈希；中断保留实际发送字节统计。"""
        require(not self.failed, "已失败的UART会话禁止重新发送")
        if self.abort_pending is not None:
            pending = self.abort_pending
            require(pending["phase"] == "ACK_REQUIRED" and request.op == OP_DIAG and request.frame == pending["request"].frame and
                    payload == struct.pack("<III", 3, pending["epoch"] & 0xFFFFFFFF, pending["epoch"] >> 32),
                    "DAP ABORT诊断pending期间只允许消费final后同frame/epoch的显式ACK，禁止新任务")
        require(request.sequence == self.last_sequence + 1, "host sequence必须严格递增")
        require(header == request.pack(), "传入header不是已验证请求的精确原字节")
        require(request.length == len(payload) and request.payload_crc == zlib.crc32(payload), "传入payload与header不一致")
        event = {"direction": "TX", "sequence": request.sequence, "frame": request.frame,
                 "op": request.op, "header_sha256": digest(header), "payload_sha256": digest(payload),
                 "payload_crc32": request.payload_crc, "source_binding": source_binding, "sent_bytes": 0, "status": "IN_PROGRESS"}
        self.events.append(event)
        self.tx_header_file.write(header); self.tx_header_file.flush()
        deadline = time.monotonic() + (900.0 if request.op == OP_WEIGHTS else 120.0)
        sent_hash = hashlib.sha256()
        try:
            for raw in (header, payload):
                offset = 0
                while offset < len(raw):
                    require(time.monotonic() < deadline, "UART写超过观察期限")
                    chunk = raw[offset:offset + 4096]
                    count = self.stream.write(chunk)
                    require(type(count) is int and 0 <= count <= len(chunk), "串口write返回错误长度")
                    sent_hash.update(chunk[:count]); offset += count; event["sent_bytes"] += count
            event["status"] = "SENT_TO_SERIAL_DRIVER"
            self.last_sequence = request.sequence
            if self.abort_pending is not None:
                self.abort_pending.update(phase="ACK_SENT", ack_request=request)
        except BaseException as error:
            self.failed = True
            event["status"], event["error"] = "FAILED", repr(error)
            raise
        finally:
            event["sent_sha256"] = sent_hash.hexdigest()

    def receive(self, request, index):
        """一次响应有界解析；错误不消耗epoch或发布成功capture。"""
        require(not self.failed, "已失败的UART会话禁止继续消费响应")
        try:
            pending = self.abort_pending
            if pending is not None:
                expected = pending["ack_request"] if pending["phase"] == "ACK_SENT" else pending["request"]
                require(pending["phase"] != "ACK_REQUIRED" and request == expected and index == 0, "DAP ABORT最终响应/ACK请求身份不匹配或已消费final")
            result = self._receive(request, index)
            meta = result[0]
            if request.op == OP_DIAG and meta["error_code"] == 8:
                require(pending is not None and pending["phase"] == "WAIT_FINAL" and meta["epoch"] == pending["epoch"], "ABORT最终响应缺失匹配的中间phase")
                pending.update(phase="ACK_REQUIRED", final_meta=meta)
            elif pending is not None:
                require(pending["phase"] == "ACK_SENT" and meta["phys_status"] & 7 == 0 and meta["error_code"] == 0 and
                        meta["epoch"] == pending["epoch"], "显式诊断ACK未回到同epoch的真实IDLE")
                self.abort_pending = None
            if request.op in (OP_RUN, OP_DIAG): self.epoch = meta["epoch"]
            return result
        except BaseException:
            self.failed = True
            raise

    def receive_abort_ready(self, request):
        """仅消费mode2的真实WAIT_DAP_ABORT；不推进epoch，必须继续读同seq最终响应。"""
        require(not self.failed and self.abort_pending is None, "ABORT会话已失败或已有未消费最终响应")
        try:
            meta, heads, boxes = self._receive(request, 0, abort_ready=True)
            self.abort_pending = {"request": request, "epoch": meta["epoch"], "phase": "WAIT_FINAL"}
            return meta, heads, boxes
        except BaseException:
            self.failed = True
            raise

    def acknowledge_abort(self, sequence):
        """DAP已独立确认final ERROR_SAFE/code8后，显式发送下一seq同frame/epoch诊断ACK并验证IDLE。"""
        require(not self.failed and self.abort_pending is not None and self.abort_pending["phase"] == "ACK_REQUIRED",
                "必须先消费真实ABORT final才能显式ACK")
        pending = self.abort_pending
        payload = struct.pack("<III", 3, pending["epoch"] & 0xFFFFFFFF, pending["epoch"] >> 32)
        request, header = make_request(OP_DIAG, sequence, pending["request"].frame, payload)
        self.send(request, header, payload, {"kind": "explicit_diagnostic_ack", "epoch": pending["epoch"], "final_metadata": pending["final_meta"]})
        return self.receive(request, 0)

    def _receive(self, request, index, *, abort_ready=False):
        """在失败锁存保护下保存全部原字节和解析记录。"""
        deadline = time.monotonic() + self.response_timeout
        raw_header = self.read_exact(HEADER.size, deadline)
        header = Header.unpack(raw_header)
        require(META.size <= header.length <= MAX_RESPONSE, "响应声明长度超出上限")
        payload = self.read_exact(header.length, deadline)
        self.events.append({"direction": "RX", "header_sha256": digest(raw_header), "payload_sha256": digest(payload),
                            "header": header.__dict__, "raw_meta": list(META.unpack_from(payload)), "bytes": HEADER.size + len(payload)})
        meta, heads, detections = decode_response(raw_header, payload, request, index, self.epoch, abort_ready=abort_ready)
        if request.op == OP_WEIGHTS:
            require(meta["epoch"] == self.epoch and meta["phys_status"] & 7 == 0 and meta["error_code"] == 0 and
                    meta["phys_status"] & (1 << 10) != 0 and meta["phys_status"] & UNSAFE_MASK == 0, "LOAD_WEIGHTS响应状态错误")
        return meta, heads, detections


def load_assets(asset_root, indices):
    """工作树冻结索引与指定大文件逐个绑定；不复制GF8或输入集合。"""
    model_raw = exact_path(ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json").read_bytes()
    sample_raw = exact_path(ROOT / "report/evidence/S2A-T01/fixed_test_samples.json").read_bytes()
    d9_raw = exact_path(ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json").read_bytes()
    require(digest(model_raw) == MODEL_SHA and digest(sample_raw) == SAMPLES_SHA and digest(d9_raw) == CPU_D9_SHA, "冻结索引原字节SHA错误")
    model, samples, golden = json.loads(model_raw), json.loads(sample_raw)["samples"], json.loads(d9_raw)["samples"]
    root = exact_path(asset_root, "directory")
    weight_path = exact_path(root / "fixtures/common/weights.gf8")
    weight = weight_path.read_bytes()
    require(len(weight) == WEIGHT_BYTES and digest(weight) == model["bindings"]["gf8_package"]["sha256"] and weight[:8] == b"GFINT8W1", "GF8实际文件绑定错误")
    rows = []
    for index in indices:
        require(type(index) is int and 0 <= index < 109, "样本索引范围错误")
        sample, gold = samples[index], golden[index]
        path = exact_path(root / "fixtures" / f"sample_{index:03d}" / "input_chw_int8.bin")
        raw = path.read_bytes()
        require(len(raw) == INPUT_BYTES and digest(raw) == sample["pl_input_sha256"] == gold["input"]["pl_input_sha256"], "固定input绑定错误")
        rows.append({"sample_index": index, "sample": sample, "golden": gold, "input_path": path,
                     "input_sha256": digest(raw), "asset_root": root})
    return weight_path, weight, rows


def verify_build(build_path):
    """PC实际核对完整新XSA/ELF/源码绑定，禁止只凭一个PASS字符串部署。"""
    path = exact_path(build_path)
    build = json.loads(path.read_text(encoding="utf-8"))
    require(build.get("status") == "PASS_OFFLINE_FULL_XSA_BUILD" and build.get("hardware_mode") == "FULL_PLATFORM_BOUND",
            "必须新整网XSA绑定并重建ELF，拒绝PS-only产物")
    config = build["config"]
    require(build["xsa_sha256"] == config["xsa_sha256"] and digest(exact_path(config["xsa"]).read_bytes()) == config["xsa_sha256"], "完整XSA原字节绑定错误")
    require(digest(exact_path(config["platform_manifest"]).read_bytes()) == config["platform_manifest_sha256"], "完整平台证据清单绑定错误")
    for name in ("elf", "initializer_elf"):
        binding = build[name]
        require(digest(exact_path(binding["path"]).read_bytes()) == binding["sha256"], f"实际{name}原字节绑定错误")
    for relative, expected in build["source_sha256"].items():
        require(digest(exact_path(ROOT / relative).read_bytes()) == expected, "构建源码与当前运输/应用版本不同")
    require("vitis/s2b_inference_app.c" in build["source_sha256"] and "verification/s2b_board_transport.py" in build["source_sha256"], "缺少实际app/host源码绑定")
    return path, build


def capture_row(run, row, frame, heads, detections):
    """保存实际捕获头，比较全部字节和确定性框；不把黄金文件当捕获文件。"""
    try:
        from .s2b_fixed_capture_check import compare_detections
    except ImportError:
        from s2b_fixed_capture_check import compare_detections
    directory = new_directory(run / f"frame_{frame:08d}")
    tensors = {}
    for name, length in HEAD_LENGTHS.items():
        raw = heads[name]
        path = directory / f"{name}.bin"
        with path.open("xb") as stream:
            stream.write(raw)
        require(len(raw) == length and digest(raw) == row["golden"]["head_tensors"][name]["tensor_sha256"], f"实际{frame}/{name}与CPU黄金不匹配")
        tensors[name] = {"path": str(path), "tensor_sha256": digest(raw), "byte_length": length}
    comparison = compare_detections(row["golden"]["detections"], detections, 1e-6)
    require(comparison["match"], f"实际{frame}完整框不匹配：{comparison}")
    return {"frame_id": frame, "sample_id": row["sample"]["sample_id"], "input": row["golden"]["input"],
            "head_tensors": tensors, "nms_output_box_count": len(detections), "detections": detections}


def reference_row(run, row):
    """从CPU黄金流独立提取两头并绑定冻结D9，不读取捕获字节生成参考。"""
    gold = row["golden"]
    directory = new_directory(run / f"golden_{row['sample_index']:03d}")
    raw_path = exact_path(row["asset_root"] / "fixtures" / f"sample_{row['sample_index']:03d}" / "golden_unique.bin")
    tensors = {}
    with raw_path.open("rb") as source:
        for name, head in gold["head_tensors"].items():
            source.seek(head["byte_offset"]); raw = source.read(head["byte_length"])
            require(len(raw) == head["byte_length"] and digest(raw) == head["tensor_sha256"], "CPU黄金head切片绑定错误")
            path = directory / f"{name}.bin"
            with path.open("xb") as target:
                target.write(raw)
            tensors[name] = {"path": str(path), "tensor_sha256": digest(raw), "byte_length": len(raw)}
    return {key: tensors if key == "head_tensors" else gold[key] for key in
            ("frame_id", "sample_id", "input", "head_tensors", "nms_output_box_count", "detections")}


def main():
    """显式打开指定串口，捕获启动身份后执行授权的固定输入任务。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--build-details", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--sample-indices", default=",".join(map(str, range(109))))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--core-timeout", type=lambda value: int(value, 0), default=0xFFFFFFFF)
    parser.add_argument("--drain-timeout", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--response-timeout", type=float, default=450.0)
    args = parser.parse_args()
    require(1 <= args.core_timeout <= 0xFFFFFFFF and 1 <= args.drain_timeout <= 0xFFFFFFFF, "deadline必须非零32-bit")
    indices = [int(part) for part in args.sample_indices.split(",")]
    require(len(indices) == len(set(indices)) and indices == sorted(indices), "样本索引必须唯一升序")
    require(args.repeat == 1 or (args.repeat == 1000 and indices == [0]), "连续验收仅允许sample000重复1000；完整109样本逐次发送")
    parent = exact_path(ROOT / "report/evidence/S2B-T15", "directory")
    run = new_directory(args.run_dir, parent)
    record = {"schema_version": 1, "status": "FAIL", "hardware_execution": "UART_CAPTURE_REQUESTED",
              "requested_build_details": str(args.build_details),
              "command": sys.argv, "port": args.port, "serial": "115200/8N1; no RTS/CTS", "frames": [],
              "core_timeout": args.core_timeout, "drain_timeout": args.drain_timeout, "events": [],
              "source_sha256": digest(Path(__file__).read_bytes()), "started_monotonic": time.monotonic(), "limitations": []}
    wire, stream = None, None
    try:
        build_path, build = verify_build(args.build_details)
        record["build_details"] = {"path": str(build_path), "sha256": digest(build_path.read_bytes())}
        weight_path, weight, rows = load_assets(args.asset_root, indices)
        import serial
        with (run / "uart_rx_raw.bin").open("xb") as rx, (run / "uart_tx_headers.bin").open("xb") as tx:
            stream = serial.Serial(args.port, baudrate=115200, bytesize=8, parity="N", stopbits=1,
                                   timeout=0.1, write_timeout=1.0, rtscts=False, dsrdtr=False)
            wire = WireSession(stream, rx, tx, response_timeout=args.response_timeout)
            record["banner"] = wire.banner(build["source_sha256"]["vitis/s2b_inference_app.c"], build["xsa_sha256"])
            request, header = make_request(OP_WEIGHTS, 1, 0, weight)
            wire.send(request, header, weight, {"path": str(weight_path), "bytes": len(weight), "sha256": digest(weight)})
            wire.receive(request, 0)
            sequence = 2
            references, captures = [], []
            for row in rows:
                input_raw = exact_path(row["input_path"]).read_bytes()
                require(digest(input_raw) == row["input_sha256"], "输入在发送前变化")
                gold = row["golden"]
                payload = struct.pack("<II", args.core_timeout, args.drain_timeout) + input_raw
                request, header = make_request(OP_RUN, sequence, gold["frame_id"], payload,
                                               width=gold["input"]["geometry_wh"][0], height=gold["input"]["geometry_wh"][1], repeat=args.repeat)
                wire.send(request, header, payload, {"path": str(row["input_path"]), "sha256": row["input_sha256"], "bytes": INPUT_BYTES})
                for index in range(args.repeat):
                    meta, heads, detections = wire.receive(request, index)
                    captured = capture_row(run, row, request.frame + index, heads, detections)
                    record["frames"].append({"transport": meta, "capture": captured})
                    if index == 0:
                        captures.append(captured)
                references.append(reference_row(run, row)); sequence += 1
            reference = {"schema_version": 1, "kind": "s2b_fixed_reference", "model_manifest_sha256": MODEL_SHA,
                         "golden_source": {"kind": "frozen_cpu_d9", "path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json", "sha256": CPU_D9_SHA}, "samples": references}
            capture = {"schema_version": 1, "kind": "s2b_fixed_capture", "model_manifest_sha256": MODEL_SHA, "samples": captures}
            write_json_new(run / "reference.json", reference); write_json_new(run / "capture.json", capture)
            try:
                from .s2b_fixed_capture_check import check_capture
            except ImportError:
                from s2b_fixed_capture_check import check_capture
            comparison = check_capture(run / "reference.json", run / "capture.json")
            write_json_new(run / "capture_check.json", comparison)
            require(comparison["status"] == "PASS_OFFLINE_CAPTURE_CHECK", "现有固定捕获检查器失败")
            require(len(record["frames"]) == len(rows) * args.repeat, "连续任务数量不足")
            record["status"] = "PASS_CAPTURED_AND_FROZEN_GOLDEN_MATCHED"
    except BaseException as error:
        record["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        if stream is not None:
            stream.close(); record["serial_closed"] = not stream.is_open
        record["events"] = [] if wire is None else wire.events
        record["elapsed_seconds"] = time.monotonic() - record["started_monotonic"]
        write_json_new(run / "transport_result.json", record)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TransportError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(2)
