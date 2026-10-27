#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5 阶段5 `camera_capture_replay_colour` **输入路径实现**（离线回放；不接板卡）。

为什么有这一层（NB-5 遗留）
==========================
此前阶段5 只在**绑定层**声明了回放/彩色标签（`docs/stage5/s5t03_input_contract_binding_v1.json`），
实现层仍是合成流（`source_kind=synthetic`、`capture_time_available=false`）。本模块补上实现层：

1. **逐帧 `frame_integrity` 校验**（r04 `source_frame_hash_rule.replay_binding`：algorithm + value + 实际 length_bytes）；
   每次装载源帧都**现场重算**，与声明不符即拒收（fail-closed）。
2. **`replay_source_*` 绑定**：把源帧路径/哈希/宽高/stride/字节序/阶段3 证据入口/源帧号/源抓取时刻
   写进**每一条**产出的结果记录（不再只是文档表格）。
3. **非零 `capture_time_ns` 传递**：取阶段3 绑定里**已文档化的真实抓取时刻**（非零），
   `clock_domain=replay_documented_wallclock`（秒级精度）——**不**把回放注入时刻冒充采集时刻。
4. **`replay_not_live=true` 标记**：产物显式携带，供下游/证据包一眼识别"回放非实时"。

输入（只读）
============
- 阶段3 回放绑定：`dbdf/…/S3-T05/t05_replay_binding_20261025_r01/replay_input_binding.json`
  （`source_kind=camera`、`mode=offline_replay`、`timing_claim_scope=replay_only`、`capture_time_ns` 非零、
  `frame_integrity` 齐全；源帧 `frame_full.bin` sha256 `939fce22…`、2 764 800 B、1280×720、stride 3840、BGR）。
- 源帧文件：路径按绑定的 `source_worktree` + `source_frame_path` 解析，**只读**。

诚实边界
========
本模块只证明"回放输入路径的**实现**成立"：逐帧完整性可校验、字段可传递、非实时标记在位、异常可拒收。
**不**证明：真实摄像头采集、PL 实跑、UART 实收、板上回放、颜色质量、端到端延迟（时钟
`PENDING_MEASUREMENT`）、G0–G5 任一项。结论一律标注"回放/离线"。

退出码（CLI）：0 = 自检通过；1 = 判定失败（校验不通过）；2 = 输入/环境错误（缺失、不可读、结构非法）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
for _candidate in (str(REPO_ROOT), str(pathlib.Path(__file__).resolve().parent)):
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

import verification.s5_display_geometry_reference as R  # noqa: E402

INPUT_SCOPE_LABEL = "camera_capture_replay_colour"
INPUT_KIND = "stage3_fixed_frame_replay"
INTEGRITY_ALGORITHM = "sha256"
REPLAY_SOURCE_FIELDS = (
    "replay_source_path",
    "replay_source_file_sha256",
    "replay_source_width",
    "replay_source_height",
    "replay_source_stride_bytes",
    "replay_source_byte_order",
    "replay_source_pixel_format",
    "stage3_capture_evidence_entry",
    "source_frame_id",
    "source_capture_time_ns",
)
REQUIRED_BINDING_FIELDS = (
    "input_id", "source_kind", "mode", "timing_claim_scope", "source_frame_path",
    "source_frame_sha256", "source_frame_size_bytes", "frame_integrity", "source_frame_id",
    "width", "height", "stride_bytes", "pixel_format", "byte_order", "coordinate_origin",
    "capture_time_available", "capture_time_ns",
)


class ReplayInputError(RuntimeError):
    """回放输入路径的拒收原因（fail-closed：宁可拒绝，不得静默降级）。"""


def _sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayInputError(message)


@dataclass(frozen=True)
class ReplaySource:
    """阶段3 回放源帧的**已校验**身份（装载时现场重算，不信任声明值）。"""

    binding_path: pathlib.Path
    input_id: str
    source_frame_path: pathlib.Path
    source_frame_rel: str
    source_frame_sha256: str
    source_frame_size_bytes: int
    source_frame_id: int
    width: int
    height: int
    stride_bytes: int
    pixel_format: str
    byte_order: str
    coordinate_origin: str
    capture_time_ns: int
    clock_domain: str
    timing_claim_scope: str
    source_commit: str
    timestamp_source: Mapping[str, Any]
    replay_not_live: bool = True

    def describe(self) -> dict[str, Any]:
        return {
            "input_scope_label": INPUT_SCOPE_LABEL,
            "input_kind": INPUT_KIND,
            "input_id": self.input_id,
            "binding_path": str(self.binding_path),
            "source_frame_path": str(self.source_frame_path),
            "source_frame_sha256": self.source_frame_sha256,
            "source_frame_size_bytes": self.source_frame_size_bytes,
            "source_frame_id": self.source_frame_id,
            "geometry": {"width": self.width, "height": self.height},
            "stride_bytes": self.stride_bytes,
            "pixel_format": self.pixel_format,
            "byte_order": self.byte_order,
            "coordinate_origin": self.coordinate_origin,
            "capture_time_ns": self.capture_time_ns,
            "clock_domain": self.clock_domain,
            "timing_claim_scope": self.timing_claim_scope,
            "replay_not_live": self.replay_not_live,
            "source_commit": self.source_commit,
            "timestamp_source": dict(self.timestamp_source),
        }


def _resolve_frame_path(binding: Mapping[str, Any], binding_path: pathlib.Path) -> pathlib.Path:
    raw = str(binding.get("source_frame_path") or "")
    _require(bool(raw), "绑定缺少 source_frame_path")
    candidate = pathlib.Path(raw)
    if candidate.is_absolute():
        return candidate
    worktree = binding.get("source_worktree")
    if isinstance(worktree, str) and worktree.strip():
        return pathlib.Path(worktree) / candidate
    return binding_path.parent.parent.parent.parent / candidate      # 兜底：仓库根相对


def load_replay_source(binding_path: str | pathlib.Path, *,
                       verify_bytes: bool = True) -> ReplaySource:
    """装载并**校验**阶段3 回放源帧绑定；任一不满足即 `ReplayInputError`。"""
    binding_path = pathlib.Path(binding_path)
    if not binding_path.is_file():
        raise ReplayInputError(f"回放绑定缺失：{binding_path}")
    try:
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReplayInputError(f"回放绑定不可解析：{error}") from error
    _require(isinstance(binding, Mapping), "回放绑定顶层必须是对象")
    missing = [key for key in REQUIRED_BINDING_FIELDS if key not in binding]
    _require(not missing, f"回放绑定缺少必需字段：{missing}")

    _require(binding["source_kind"] == "camera",
             f"回放源 kind 必须是 camera（实际 {binding['source_kind']!r}）")
    _require(binding["mode"] == "offline_replay",
             f"回放 mode 必须是 offline_replay（实际 {binding['mode']!r}）")
    _require(binding["timing_claim_scope"] == "replay_only",
             "回放 timing_claim_scope 必须是 replay_only（不得继承实时结论）")
    _require(binding["capture_time_available"] is True,
             "回放源必须声明 capture_time_available=true（不得用 unavailable 哨兵）")
    capture_time_ns = binding["capture_time_ns"]
    _require(type(capture_time_ns) is int and capture_time_ns > 0,
             f"回放源 capture_time_ns 必须是**非零**整数（实际 {capture_time_ns!r}）")

    integrity = binding["frame_integrity"]
    _require(isinstance(integrity, Mapping), "frame_integrity 必须是对象")
    _require(integrity.get("algorithm") == INTEGRITY_ALGORITHM,
             f"frame_integrity.algorithm 必须是 {INTEGRITY_ALGORITHM}")
    declared_value = integrity.get("value")
    _require(isinstance(declared_value, str) and len(declared_value) == 64,
             "frame_integrity.value 必须是 64 位十六进制")
    declared_length = integrity.get("length_bytes")
    _require(type(declared_length) is int and declared_length > 0,
             "frame_integrity.length_bytes 必须是正整数")
    _require(declared_length == binding["source_frame_size_bytes"],
             "frame_integrity.length_bytes 必须等于 source_frame_size_bytes")
    _require(declared_value == binding["source_frame_sha256"],
             "frame_integrity.value 必须等于 source_frame_sha256")

    frame_path = _resolve_frame_path(binding, binding_path)
    if not frame_path.is_file():
        raise ReplayInputError(f"回放源帧文件缺失：{frame_path}")
    actual_size = frame_path.stat().st_size
    if verify_bytes:
        actual_sha = _sha256_file(frame_path)
        _require(actual_sha == binding["source_frame_sha256"],
                 f"回放源帧字节与绑定不符：声明 {binding['source_frame_sha256']}，实测 {actual_sha}")
        _require(actual_size == binding["source_frame_size_bytes"],
                 f"回放源帧大小与绑定不符：声明 {binding['source_frame_size_bytes']}，实测 {actual_size}")

    width, height = binding["width"], binding["height"]
    _require(type(width) is int and type(height) is int and width > 0 and height > 0,
             "width/height 必须是正整数")
    _require(binding["stride_bytes"] == width * 3,
             f"stride_bytes 必须等于 width×3（实际 {binding['stride_bytes']} vs {width * 3}）")
    _require(binding["pixel_format"] == "BGR888", "pixel_format 必须是 BGR888")
    _require(binding["byte_order"] == "BGR", "byte_order 必须是 BGR")
    _require(binding["coordinate_origin"] == "top_left", "coordinate_origin 必须是 top_left")
    _require(actual_size == binding["stride_bytes"] * height,
             f"源帧大小必须等于 stride×height（实际 {actual_size} vs {binding['stride_bytes'] * height}）")

    return ReplaySource(
        binding_path=binding_path,
        input_id=str(binding["input_id"]),
        source_frame_path=frame_path,
        source_frame_rel=str(binding["source_frame_path"]),
        source_frame_sha256=str(binding["source_frame_sha256"]),
        source_frame_size_bytes=int(binding["source_frame_size_bytes"]),
        source_frame_id=int(binding["source_frame_id"]),
        width=int(width), height=int(height), stride_bytes=int(binding["stride_bytes"]),
        pixel_format=str(binding["pixel_format"]), byte_order=str(binding["byte_order"]),
        coordinate_origin=str(binding["coordinate_origin"]),
        capture_time_ns=int(capture_time_ns),
        clock_domain=str(binding["clock_domain"]),
        timing_claim_scope=str(binding["timing_claim_scope"]),
        source_commit=str(binding.get("source_commit", "")),
        timestamp_source=dict(binding["timestamp_source"])
        if isinstance(binding.get("timestamp_source"), Mapping) else {},
        replay_not_live=True,
    )


def frame_integrity_of(source: ReplaySource, *, verify_bytes: bool = True) -> dict[str, Any]:
    """对源帧**现场重算** `frame_integrity`（逐帧校验用；不缓存声明值）。"""
    if verify_bytes:
        value = _sha256_file(source.source_frame_path)
        length = source.source_frame_path.stat().st_size
    else:
        value, length = source.source_frame_sha256, source.source_frame_size_bytes
    return {"algorithm": INTEGRITY_ALGORITHM, "value": value, "length_bytes": length}


def validate_frame_integrity(declared: Mapping[str, Any] | None,
                             computed: Mapping[str, Any]) -> None:
    """逐帧完整性校验：算法/值/长度三者必须全部一致，否则拒收（fail-closed）。"""
    _require(isinstance(declared, Mapping), "缺少 frame_integrity（逐帧完整性不可省略）")
    _require(declared.get("algorithm") == computed.get("algorithm"),
             f"frame_integrity.algorithm 不符：{declared.get('algorithm')!r} vs {computed.get('algorithm')!r}")
    _require(declared.get("value") == computed.get("value"),
             "frame_integrity.value 不符（源帧字节已变或声明错误）")
    _require(declared.get("length_bytes") == computed.get("length_bytes"),
             f"frame_integrity.length_bytes 不符：{declared.get('length_bytes')!r} vs "
             f"{computed.get('length_bytes')!r}")


def replay_source_fields(source: ReplaySource) -> dict[str, Any]:
    """结果记录里必须携带的 `replay_source_*` 绑定字段。"""
    return {
        "replay_source_path": source.source_frame_rel,
        "replay_source_file_sha256": source.source_frame_sha256,
        "replay_source_width": source.width,
        "replay_source_height": source.height,
        "replay_source_stride_bytes": source.stride_bytes,
        "replay_source_byte_order": source.byte_order,
        "replay_source_pixel_format": source.pixel_format,
        "stage3_capture_evidence_entry": str(source.binding_path),
        "source_frame_id": source.source_frame_id,
        "source_capture_time_ns": source.capture_time_ns,
    }


def build_replay_record(source: ReplaySource, *, session_id: int, frame_id: int, result_seq: int,
                        detections: Iterable[Mapping[str, Any]] = (), repeat_index: int = 1,
                        state: str = "OK", repeat_declared: bool = False,
                        capture_offset_ns: int = 0,
                        result_offset_ns: int | None = None,
                        verify_bytes: bool = True) -> dict[str, Any]:
    """构造一条**回放**结果记录（可直接投给 `DisplayPipeline.submit_result`）。

    - 默认（证据模式）：`result_time_ns/inference_time_ns/end_to_end_latency_ns` 一律 `null`
      —— 回放无单调发布时钟，不得伪造延迟/年龄。
    - 给出 `capture_offset_ns`/`result_offset_ns` 时（**仅离线动态回归用**）：按
      `capture = source.capture_time_ns + capture_offset_ns`、`result = capture + result_offset_ns`
      构造 **replay-local 逻辑时基**，并写入 `replay_timebase.basis="replay_local_logical"`；
      `source_capture_time_ns` 仍保留阶段3 **文档化的真实抓取时刻**原值（非零），两者不混同。
    """
    detections = [dict(item) for item in detections]
    integrity = frame_integrity_of(source, verify_bytes=verify_bytes)
    validate_frame_integrity({"algorithm": integrity["algorithm"], "value": source.source_frame_sha256,
                              "length_bytes": source.source_frame_size_bytes}, integrity)
    logical = result_offset_ns is not None
    offset = int(result_offset_ns or 0)
    capture_ns = source.capture_time_ns + int(capture_offset_ns or 0)
    record: dict[str, Any] = {
        "session_id": int(session_id),
        "frame_id": int(frame_id),
        "result_seq": int(result_seq),
        "repeat_index": int(repeat_index),
        "geometry": {"width": source.width, "height": source.height},
        "state": state,
        "detection_count": len(detections),
        "detections": detections,
        "stale": False,
        "dropped_frames": 0,
        "capture_time_ns": capture_ns,                   # 证据模式＝文档化真实抓取时刻；回归＝逻辑时刻
        "result_time_ns": capture_ns + offset if logical else None,
        "inference_time_ns": offset if logical else None,
        "end_to_end_latency_ns": offset if logical else None,
        "error_code": 0,
        "input_scope_label": INPUT_SCOPE_LABEL,
        "input_kind": INPUT_KIND,
        "replay_not_live": True,
        "frame_integrity": integrity,
        "clock_domain": source.clock_domain,
        "timing_claim_scope": source.timing_claim_scope,
        **replay_source_fields(source),
    }
    if logical:
        record["replay_timebase"] = {
            "basis": "replay_local_logical",
            "note": "回放局部逻辑时基：capture/result 由阶段3 文档化抓取时刻 + 帧序号×周期推导，"
                    "仅用于验证过期/年龄**规则**，不是实测采集或端到端延迟",
            "capture_offset_ns": int(capture_offset_ns or 0),
            "result_offset_ns": offset,
            "source_capture_time_ns": source.capture_time_ns,
        }
    if repeat_declared:
        record["repeat_declared"] = True
    return record


def assert_replay_record(record: Mapping[str, Any]) -> None:
    """产出记录的**实现层**守卫：任何一项不满足即拒收（不得只靠文档声明）。"""
    _require(record.get("input_scope_label") == INPUT_SCOPE_LABEL,
             f"input_scope_label 必须是 {INPUT_SCOPE_LABEL}")
    _require(record.get("replay_not_live") is True, "replay_not_live 必须为 true（回放不得冒充实时）")
    capture = record.get("capture_time_ns")
    _require(type(capture) is int and capture > 0, "capture_time_ns 必须非零（不得 0 哨兵/unavailable）")
    missing = [key for key in REPLAY_SOURCE_FIELDS if key not in record]
    _require(not missing, f"结果记录缺少 replay_source_* 字段：{missing}")
    timebase = record.get("replay_timebase")
    logical = isinstance(timebase, Mapping) and timebase.get("basis") == "replay_local_logical"
    if logical:
        _require(type(record.get("result_time_ns")) is int,
                 "replay-local 逻辑时基下 result_time_ns 必须是整数（回放局部逻辑时间）")
    else:
        _require(record.get("result_time_ns") is None and record.get("inference_time_ns") is None,
                 "回放无单调发布时钟：result_time_ns/inference_time_ns 必须为 null（不得伪造）")
    integrity = record.get("frame_integrity")
    _require(isinstance(integrity, Mapping), "结果记录必须携带 frame_integrity")
    # N2：三要素都要查（只查 value 可被手搓记录绕过）
    _require(integrity.get("algorithm") == INTEGRITY_ALGORITHM,
             f"frame_integrity.algorithm 必须是 {INTEGRITY_ALGORITHM}"
             f"（实际 {integrity.get('algorithm')!r}）")
    _require(integrity.get("value") == record.get("replay_source_file_sha256"),
             "frame_integrity.value 必须与 replay_source_file_sha256 一致")
    stride = record.get("replay_source_stride_bytes")
    height = record.get("replay_source_height")
    _require(type(stride) is int and type(height) is int and stride > 0 and height > 0,
             "replay_source_stride_bytes/height 必须是正整数（用于复算 length_bytes）")
    length = integrity.get("length_bytes")
    _require(type(length) is int and length > 0, "frame_integrity.length_bytes 必须是正整数")
    _require(length == stride * height,
             f"frame_integrity.length_bytes 必须等于 stride×height（{length} vs {stride * height}）")
    problems = R.validate_result_record(record)
    _require(not problems, f"结果记录不满足阶段4 输入契约：{problems}")


def selftest(binding_path: str | pathlib.Path) -> dict[str, Any]:
    """实现层自检：装载 + 逐帧完整性 + 构造 + 守卫 + 3 类必失败注入。"""
    source = load_replay_source(binding_path)
    record = build_replay_record(source, session_id=1396854863, frame_id=1, result_seq=1,
                                 detections=[{"class_id": 0, "class_name": "fist", "score": 0.77,
                                              "xyxy": [0.25, 0.37, 0.35, 0.44], "source_order": 1}])
    assert_replay_record(record)
    negatives: list[dict[str, Any]] = []

    def expect_reject(name: str, mutate) -> None:
        candidate = json.loads(json.dumps(record))
        mutate(candidate)
        try:
            assert_replay_record(candidate)
        except ReplayInputError as error:
            negatives.append({"injection": name, "rejected": True, "reason": str(error)[:160]})
        else:
            negatives.append({"injection": name, "rejected": False, "reason": "未被拒收（缺陷）"})

    expect_reject("replay_not_live_false", lambda rec: rec.__setitem__("replay_not_live", False))
    expect_reject("capture_time_zero", lambda rec: rec.__setitem__("capture_time_ns", 0))
    expect_reject("drop_replay_source_field", lambda rec: rec.pop("replay_source_file_sha256", None))
    expect_reject("frame_integrity_mismatch", lambda rec: rec["frame_integrity"].__setitem__("value", "0" * 64))
    expect_reject("frame_integrity_algorithm_wrong",
                  lambda rec: rec["frame_integrity"].__setitem__("algorithm", "md5"))
    expect_reject("frame_integrity_length_wrong",
                  lambda rec: rec["frame_integrity"].__setitem__("length_bytes",
                                                                rec["frame_integrity"]["length_bytes"] + 1))
    result = {
        "status": "REPLAY_INPUT_SELFTEST_PASS" if all(item["rejected"] for item in negatives)
                  else "REPLAY_INPUT_SELFTEST_FAIL",
        "source": source.describe(),
        "record_keys": sorted(record.keys()),
        "frame_integrity": record["frame_integrity"],
        "must_fail_injections": negatives,
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding", required=True, help="阶段3 回放输入绑定 JSON（只读）")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)
    try:
        result = selftest(args.binding)
    except ReplayInputError as error:
        print(f"[REPLAY_INPUT_ERROR] {error}", file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        pathlib.Path(args.json_out).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["status"] == "REPLAY_INPUT_SELFTEST_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())