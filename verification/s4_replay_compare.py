#!/usr/bin/env python3
"""S4-C 阶段4 离线回放与对拍工具：整数推理结果（INT8 heads）vs 2A 冻结 CPU golden。

本模块既可导入（供 S4-C 驱动脚本与阶段4 正式联调复用），也可作为 CLI 运行。

对拍口径（与 2A 冻结事实一致，字段命名对齐 S4-A 契约
``docs/stage4/s4a_stage4_g0_fields.json``）：

1. 逐样本流式 zlib 解压 ``report/evidence/S2A-T25/tensors/sample_NNN.zlib``，
   校验压缩分片 SHA-256 与 ``network.raw_stream_sha256`` /
   ``network.compressed_shard.decompressed_sha256``（口径来源：T25 索引）。
2. 按 T25 索引 ``network.tensors[]`` 的 ``byte_offset`` / ``byte_length`` 从解压流
   切出两头（绝不硬编码偏移）：``head13`` = 5,070 B、``head26`` = 20,280 B，
   其 ``op == "yolo"`` 且 ``alias_of_layer_index`` 指向源卷积层。
   切出后逐头校验 ``tensor_sha256``（T25 索引与 T29 参考必须一致）。
3. 用冻结 2A D9 ``verification/s1_t02_d9_yolo_decode.py::decode_yolov4_tiny416``
   （依赖 ``verification/s1_t02_d6_detection_metrics.py``）解码：
   signed INT8 × 各头 ``int8_scale`` → float64 logits（head13=0.24267549589862975、
   head26=0.30223452951025775，取自 T29 ``head_tensors`` / manifest，
   并与 T25 索引逐层 scale 双向核对）；``score_threshold=0.25``（D9 API 限定闭区间
   [0.25, 0.50]）；几何取 T29 样本 ``input.geometry_wh``（顺序 **width,height**），
   并与 T25 ``original_input`` / T01 样本清单 width/height 交叉核对。
4. 与 T29 ``cpu_decode_nms_reference.json`` 参考框比较：
   - 离散字段必须完全相同：框数（``detection_count``）、``class_id``、
     ``class_name``、``source_order``；
   - ``score`` 与 ``xyxy`` 各分量绝对误差 ≤ 1e-6（2A 规格第 75 行，相对容限 0）。
   任一离散字段不同或数值超容限 = mismatch，并给出样本号、框序号、字段、
   期望值与实际值。

``--actual <dir>``（阶段4 正式联调复用）
----------------------------------------
用任意“实测 heads”与同一 T29 golden 对拍。目录内按 ``sample_id`` 命名，支持格式：

  a) ``<sample_id>.head13.bin`` + ``<sample_id>.head26.bin``
     （也可写 ``<sample_id>_head13.bin`` 或省略扩展名 ``<sample_id>.head13``）；
     内容为 raw INT8 二补码字节，长度必须恰为 5,070 / 20,280 B。
  b) ``<sample_id>.heads.bin``：head13 与 head26 顺序拼接（5,070 + 20,280 B）。
  c) ``<sample_id>.json`` / ``<sample_id>.heads.json``：
     ``{"head13": ..., "head26": ...}``，每项可为
       - 整数列表（全部在 -128..127 视为有符号；全部在 0..255 视为无符号二补码），
       - ``"hex:..."`` / 纯十六进制字符串，
       - ``"base64:..."``，
       - ``{"int8": [...], "int8_scale": <可选覆盖>}`` / ``{"hex": "..."}`` /
         ``{"base64": "..."}``。
     也支持顶层包一层 ``{"heads": {...}}``。覆盖 scale 时报告中记录
     ``scale_source = "actual_override"``（默认 ``t29_reference``）。
     文件中的 ``int8_scale`` 若提供且与冻结值不同，属于实测侧自定义，
     会显式记录，不改变 golden 侧口径。

实测 heads 一律先校验字节 SHA-256 == T29 ``head_tensors[name].tensor_sha256``
（“两头所有 INT8 字节完全相同”先于解码），再做框比较。默认还会按 T25 索引
偏移从分片切出 golden 两头字节，对不一致的头给出逐值定位（首个差异字节偏移、
差异字节数、期望/实际字节值、最大 INT8 差值）；若分片不可用或显式传
``--no-golden-bytes``，则退化为只比对 SHA-256（期望值仍来自 T29 冻结参考），
并在报告中记录降级事实。

``--limit N`` / ``--seed S``：随机子集使用 ``random.Random(seed).sample``，
报告中记录种子、种子来源、样本数与样本 id 列表；默认全量 109。

退出码
------
  0 = 所选项全部 PASS（mismatch = 0）
  1 = 存在 mismatch（含字节/几何/离散字段/数值超容限）
  2 = 环境或输入错误（上游文件缺失或 SHA 不符、参数非法、格式不支持等）
``--self-test-tamper`` 的退出码语义不同：0 = 全部篡改探针均被检出（自检通过），
1 = 存在未被检出的篡改（工具缺陷），2 = 环境错误。

限制
----
- 只读上游，不写 D:\\FPGA_Competition / w2b / dbdf；逐样本处理并释放解压流。
- 不执行硬件、串口、Vivado/xsim；本工具是纯 CPU 离线对拍。
- 不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import math
import random
import struct
import sys
import time
import tracemalloc
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_VERSION = "gestureforge_s4c_replay_compare_v1"
TASK_ID = "S4-C"
DEFAULT_SUBSET_SEED = 20260922

WORKTREE = Path(__file__).resolve().parents[1]
S4A_CONTRACT_PATH = WORKTREE / "docs" / "stage4" / "s4a_stage4_g0_fields.json"
DEFAULT_MAIN_TREE = Path(r"D:\FPGA_Competition")

# S4-A 契约 / task-3 声明的上游 SHA-256（复算不一致即 FAIL，不静默继续）。
EXPECTED_SHA256 = {
    "s2a_t25_layer_golden_index": "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d",
    "s2a_t29_cpu_decode_nms_reference": "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231",
    "s2a_t01_fixed_test_samples": "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed",
    "s2a_t01_model_manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "s1_t02_d9_decoder": "94dacdac18968e70871e1c21d24d5f4c3a9941881eaf37ffaab4d5372e28d190",
    "s1_t02_d6_metrics": "4dcf0f7d9586b7096be015faf2c5037489b03b04baeec0daea4cadec89be591a",
}

FROZEN_CLASSES = ("fist", "palm", "one", "two_up", "three")
FROZEN_SCORE_THRESHOLD = 0.25
FROZEN_NMS_IOU = 0.45
FROZEN_MAX_OUTPUTS = 15
FROZEN_SCORE_ABS_TOLERANCE = 1e-6
FROZEN_XYXY_ABS_TOLERANCE = 1e-6
FROZEN_RELATIVE_TOLERANCE = 0.0
COMPARISON_SOURCE = "S2A-T01 规格第 75 行（S2A-T01_模型交付规格与G0接口冻结.md 第 75 行）"
FROZEN_HEAD_BYTE_LENGTHS = {"head13": 5070, "head26": 20280}
DISCRETE_FIELDS = ("class_id", "class_name", "source_order")

HEAD13_NAME = "head13"
HEAD26_NAME = "head26"


class S4CError(RuntimeError):
    """本工具的基类错误；调用方据此返回退出码 2。"""


class UpstreamError(S4CError):
    """上游冻结资产缺失、SHA 不符或语义不一致。"""


class ActualInputError(S4CError):
    """实测 heads 目录格式不支持或数据非法。"""


def now_utc8() -> str:
    """返回东八区当前时间（秒精度 ISO 8601）。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256_bytes(data: bytes | bytearray | memoryview) -> str:
    """计算内存块的 SHA-256。"""

    return hashlib.sha256(bytes(data)).hexdigest()


def sha256_file(path: Path) -> str:
    """按 1 MiB 分块计算文件 SHA-256，避免大文件整体载入。"""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_newlines_digest(path: Path) -> str:
    """按 1 MiB 分块计算“CRLF→LF 归一化后”的 SHA-256（仅用于诊断行尾差异）。"""

    digest = hashlib.sha256()
    tail = b""
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                break
            data = tail + chunk
            if data.endswith(b"\r"):
                tail = b"\r"
                data = data[:-1]
            else:
                tail = b""
            digest.update(data.replace(b"\r\n", b"\n"))
    digest.update(tail)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    """读取 UTF-8 JSON。"""

    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    """写出 UTF-8 JSON（缩进 2，保留非 ASCII）。"""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------------------
# 上游绑定解析与校验
# --------------------------------------------------------------------------------------


@dataclass
class UpstreamPaths:
    """本次对拍实际使用的上游路径集合。"""

    t25_index: Path
    t29_ref: Path
    catalog: Path
    manifest: Path
    tensors_dir: Path
    decoder_dir: Path
    contract: Path | None = None
    contract_sha256: str | None = None
    contract_status: str | None = None
    sources: dict[str, str] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        """转为机器可读记录。"""

        return {
            "t25_index": str(self.t25_index),
            "t29_reference": str(self.t29_ref),
            "fixed_test_samples": str(self.catalog),
            "model_manifest": str(self.manifest),
            "tensors_dir": str(self.tensors_dir),
            "decoder_dir": str(self.decoder_dir),
            "s4a_contract": str(self.contract) if self.contract else None,
            "s4a_contract_sha256": self.contract_sha256,
            "s4a_contract_status": self.contract_status,
            "resolution_sources": self.sources,
        }


def load_s4a_contract(path: Path | None = None) -> tuple[dict[str, Any] | None, str | None]:
    """读取 S4-A 机器可读契约，返回 (契约, 文件 SHA-256)。

    契约缺失时返回 (None, None)，由调用方回退到默认绝对路径并如实记录。
    """

    candidate = Path(path) if path else S4A_CONTRACT_PATH
    if not candidate.is_file():
        return None, None
    return load_json(candidate), sha256_file(candidate)


def _contract_binding_path(binding: Mapping[str, Any]) -> Path:
    """把契约绑定的 path 解析为绝对路径（相对路径按工作树根解析）。"""

    raw = str(binding.get("path", ""))
    path = Path(raw)
    if not path.is_absolute():
        path = WORKTREE / raw
    return path


def resolve_upstream_paths(
    *,
    contract_path: Path | None = None,
    t25_index: str | Path | None = None,
    t29_ref: str | Path | None = None,
    catalog: str | Path | None = None,
    manifest: str | Path | None = None,
    tensors_dir: str | Path | None = None,
    decoder_dir: str | Path | None = None,
) -> UpstreamPaths:
    """解析上游路径：显式 CLI 参数 > S4-A 契约绑定 > 默认绝对路径。"""

    contract, contract_sha = load_s4a_contract(contract_path)
    bindings: dict[str, Mapping[str, Any]] = {}
    if contract:
        for binding in contract.get("upstream_bindings", []):
            bindings[str(binding.get("id"))] = binding

    sources: dict[str, str] = {}

    def pick(key: str, explicit: str | Path | None, binding_id: str, default: Path) -> Path:
        if explicit:
            sources[key] = "cli"
            return Path(explicit)
        binding = bindings.get(binding_id)
        if binding:
            sources[key] = f"s4a_contract:{binding_id}"
            return _contract_binding_path(binding)
        sources[key] = "default"
        return default

    paths = UpstreamPaths(
        t25_index=pick(
            "t25_index",
            t25_index,
            "s2a_t25_layer_golden_index",
            DEFAULT_MAIN_TREE / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json",
        ),
        t29_ref=pick(
            "t29_ref",
            t29_ref,
            "s2a_t29_cpu_decode_nms_reference",
            DEFAULT_MAIN_TREE / "report" / "evidence" / "S2A-T29" / "cpu_decode_nms_reference.json",
        ),
        catalog=pick(
            "catalog",
            catalog,
            "s2a_t01_fixed_test_samples",
            DEFAULT_MAIN_TREE / "report" / "evidence" / "S2A-T01" / "fixed_test_samples.json",
        ),
        manifest=pick(
            "manifest",
            manifest,
            "s2a_t01_model_manifest",
            DEFAULT_MAIN_TREE / "report" / "evidence" / "S2A-T01" / "tiny416_model_manifest.json",
        ),
        tensors_dir=pick(
            "tensors_dir",
            tensors_dir,
            "s2a_t25_tensor_shards",
            DEFAULT_MAIN_TREE / "report" / "evidence" / "S2A-T25" / "tensors",
        ),
        decoder_dir=pick(
            "decoder_dir", decoder_dir, "s1_t02_d9_decoder", WORKTREE / "verification"
        ),
        contract=None,
        contract_sha256=contract_sha,
        contract_status=(contract or {}).get("status"),
        sources=sources,
    )
    if contract and contract_path is None:
        paths.contract = S4A_CONTRACT_PATH
    elif contract_path is not None and contract:
        paths.contract = Path(contract_path)
    # 解码器绑定若给出的是文件路径，取其所在目录。
    if paths.decoder_dir.is_file():
        paths.decoder_dir = paths.decoder_dir.parent
    return paths


def verify_upstream_files(
    paths: UpstreamPaths, *, verify_sha: bool = True, check_shards: bool = True
) -> tuple[list[dict[str, Any]], list[str]]:
    """复算上游 SHA 并统计分片目录，返回 (绑定明细, 失败说明列表)。"""

    checks = [
        ("s2a_t25_layer_golden_index", paths.t25_index),
        ("s2a_t29_cpu_decode_nms_reference", paths.t29_ref),
        ("s2a_t01_fixed_test_samples", paths.catalog),
        ("s2a_t01_model_manifest", paths.manifest),
        ("s1_t02_d9_decoder", paths.decoder_dir / "s1_t02_d9_yolo_decode.py"),
        ("s1_t02_d6_metrics", paths.decoder_dir / "s1_t02_d6_detection_metrics.py"),
    ]
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for binding_id, path in checks:
        expected = EXPECTED_SHA256.get(binding_id)
        record: dict[str, Any] = {
            "id": binding_id,
            "path": str(path),
            "exists": path.is_file(),
            "expected_sha256": expected,
        }
        if not path.is_file():
            record["status"] = "MISSING"
            failures.append(f"上游文件缺失：{binding_id} -> {path}")
        else:
            actual = sha256_file(path)
            record["actual_sha256"] = actual
            if expected is None:
                record["status"] = "UNVERIFIED_NO_EXPECTATION"
            elif actual == expected:
                record["status"] = "MATCH"
            else:
                record["normalized_sha256"] = normalize_newlines_digest(path)
                if record["normalized_sha256"] == expected:
                    record["status"] = "MATCH_AFTER_LF_NORMALIZATION"
                else:
                    record["status"] = "MISMATCH"
                    failures.append(
                        f"上游 SHA 不一致：{binding_id} 期望 {expected} 实际 {actual}"
                    )
            if not verify_sha and record.get("status") == "MISMATCH":
                # 显式 --no-verify-upstream-sha 时降级为记录，不阻断。
                record["status"] = "MISMATCH_IGNORED_BY_FLAG"
                failures = [f for f in failures if binding_id not in f]
        records.append(record)

    if check_shards:
        shard_record: dict[str, Any] = {"dir": str(paths.tensors_dir), "exists": paths.tensors_dir.is_dir()}
        if paths.tensors_dir.is_dir():
            shards = sorted(paths.tensors_dir.glob("sample_*.zlib"))
            shard_record["file_count"] = len(shards)
            shard_record["total_bytes"] = sum(item.stat().st_size for item in shards)
            shard_record["expected_file_count"] = 109
            shard_record["expected_total_bytes"] = 390700998
            ok = (
                shard_record["file_count"] == 109
                and shard_record["total_bytes"] == 390700998
            )
            shard_record["status"] = "MATCH" if ok else "MISMATCH"
            if not ok:
                failures.append(
                    "T25 分片计数不一致：{0} 个 / {1} B".format(
                        shard_record["file_count"], shard_record["total_bytes"]
                    )
                )
        else:
            shard_record["status"] = "MISSING"
            failures.append(f"T25 分片目录缺失：{paths.tensors_dir}")
        records.append({"id": "s2a_t25_tensor_shards", **shard_record})

    return records, failures


# --------------------------------------------------------------------------------------
# 冻结 D9 解码器加载
# --------------------------------------------------------------------------------------


@dataclass
class DecoderBinding:
    """冻结 2A D9 解码器与其 D6 依赖的实际加载信息。"""

    path: Path
    sha256: str
    api: str
    dependency_path: Path
    dependency_sha256: str
    newline_normalized: bool
    module: Any

    def as_json(self) -> dict[str, Any]:
        """转为机器可读记录。"""

        return {
            "path": str(self.path),
            "sha256": self.sha256,
            "api": self.api,
            "dependency": {"path": str(self.dependency_path), "sha256": self.dependency_sha256},
            "content_matched_after_lf_normalization": self.newline_normalized,
        }


def load_frozen_decoder(decoder_dir: Path, *, expect_sha: str = EXPECTED_SHA256["s1_t02_d9_decoder"]) -> DecoderBinding:
    """按绝对路径加载冻结 D9 解码器（不复制、不修改上游文件）。"""

    d9_path = Path(decoder_dir) / "s1_t02_d9_yolo_decode.py"
    d6_path = Path(decoder_dir) / "s1_t02_d6_detection_metrics.py"
    if not d9_path.is_file():
        raise UpstreamError(f"冻结 D9 解码器不存在：{d9_path}")
    if not d6_path.is_file():
        raise UpstreamError(f"冻结 D6 指标模块不存在：{d6_path}")

    d9_sha = sha256_file(d9_path)
    normalized = False
    if expect_sha and d9_sha != expect_sha:
        normalized_sha = normalize_newlines_digest(d9_path)
        if normalized_sha == expect_sha:
            normalized = True
        else:
            raise UpstreamError(
                "冻结 D9 SHA 不一致：期望 {0} 实际 {1}（归一化后 {2}）".format(
                    expect_sha, d9_sha, normalized_sha
                )
            )

    directory = str(Path(decoder_dir).resolve())
    if directory not in sys.path:
        sys.path.insert(0, directory)
    spec = importlib.util.spec_from_file_location("s4c_frozen_d9_decoder", d9_path)
    if spec is None or spec.loader is None:
        raise UpstreamError(f"无法为 {d9_path} 构造导入 spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules["s4c_frozen_d9_decoder"] = module
    spec.loader.exec_module(module)
    api = getattr(module, "decode_yolov4_tiny416", None)
    if api is None:
        raise UpstreamError("冻结 D9 未提供 decode_yolov4_tiny416")
    # D6 由 D9 的 fallback 导入路径加载，此处只记录其实际基线哈希。
    d6_sha = sha256_file(d6_path)
    return DecoderBinding(
        path=d9_path,
        sha256=d9_sha,
        api="decode_yolov4_tiny416",
        dependency_path=d6_path,
        dependency_sha256=d6_sha,
        newline_normalized=normalized,
        module=module,
    )


# --------------------------------------------------------------------------------------
# 索引 / 参考 / 样本清单装配
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class HeadPlan:
    """一个检测头的抽取与解码计划（偏移一律取自 T25 索引）。"""

    name: str
    layer_index: int
    alias_layer_index: int | None
    source_convolution_layer_index: int | None
    byte_offset: int
    byte_length: int
    scale: float
    tensor_sha256: str
    shape_nchw: tuple[int, ...]
    offset_source: str

    def as_json(self) -> dict[str, Any]:
        """转为机器可读记录。"""

        return {
            "name": self.name,
            "layer_index": self.layer_index,
            "yolo_alias_layer_index": self.alias_layer_index,
            "source_convolution_layer_index": self.source_convolution_layer_index,
            "byte_offset": self.byte_offset,
            "byte_length": self.byte_length,
            "int8_scale": self.scale,
            "tensor_sha256": self.tensor_sha256,
            "shape_nchw": list(self.shape_nchw),
            "offset_source": self.offset_source,
        }


def _head_name_from_shape(shape: Sequence[int]) -> str:
    """按 NCHW 栅格尺寸判定头名（13→head13，26→head26）。"""

    if len(shape) != 4:
        raise UpstreamError(f"检测头 shape 必须是 4 维 NCHW，实际 {list(shape)}")
    grid = int(shape[2])
    if grid != int(shape[3]):
        raise UpstreamError(f"检测头栅格非方形：{list(shape)}")
    if grid == 13:
        return HEAD13_NAME
    if grid == 26:
        return HEAD26_NAME
    raise UpstreamError(f"未知检测头栅格尺寸：{list(shape)}")


def build_head_plans(
    index_sample: Mapping[str, Any], t29_sample: Mapping[str, Any]
) -> dict[str, HeadPlan]:
    """从 T25 索引的 yolo 层条目构造两头计划，并与 T29 参考双向核对。

    偏移/长度/总量取自 T25 索引 ``network.tensors[]``（不硬编码）；
    scale 以 T29 ``head_tensors`` 为主，且必须与索引逐层 scale 完全一致。
    """

    tensors = index_sample["network"]["tensors"]
    yolo_tensors = [t for t in tensors if t.get("op") == "yolo"]
    if len(yolo_tensors) != 2:
        raise UpstreamError(
            f"样本 {index_sample.get('sample_id')} 的 yolo 层数量应为 2，实际 {len(yolo_tensors)}"
        )
    by_name: dict[str, HeadPlan] = {}
    for tensor in yolo_tensors:
        name = _head_name_from_shape(tensor["shape_nchw"])
        by_name[name] = HeadPlan(
            name=name,
            layer_index=int(tensor["layer_index"]),
            alias_layer_index=(
                int(tensor["alias_of_layer_index"])
                if tensor.get("alias_of_layer_index") is not None
                else None
            ),
            source_convolution_layer_index=None,
            byte_offset=int(tensor["byte_offset"]),
            byte_length=int(tensor["byte_length"]),
            scale=float(tensor["scale"]),
            tensor_sha256=str(tensor["tensor_sha256"]),
            shape_nchw=tuple(int(v) for v in tensor["shape_nchw"]),
            offset_source=(
                "t25_index.network.tensors[layer_index={0}].byte_offset/byte_length".format(
                    tensor["layer_index"]
                )
            ),
        )

    if set(by_name) != {HEAD13_NAME, HEAD26_NAME}:
        raise UpstreamError(f"样本 {index_sample.get('sample_id')} 未能识别两头：{sorted(by_name)}")

    t29_heads = t29_sample.get("head_tensors", {})
    if set(t29_heads) != {HEAD13_NAME, HEAD26_NAME}:
        raise UpstreamError(
            f"T29 样本 {t29_sample.get('sample_id')} head_tensors 键异常：{sorted(t29_heads)}"
        )

    result: dict[str, HeadPlan] = {}
    for name, plan in by_name.items():
        reference = t29_heads[name]
        mismatches: list[str] = []
        if int(reference["byte_offset"]) != plan.byte_offset:
            mismatches.append(
                f"byte_offset T25={plan.byte_offset} T29={reference['byte_offset']}"
            )
        if int(reference["byte_length"]) != plan.byte_length:
            mismatches.append(
                f"byte_length T25={plan.byte_length} T29={reference['byte_length']}"
            )
        if float(reference["int8_scale"]) != plan.scale:
            mismatches.append(
                f"int8_scale T25={plan.scale!r} T29={reference['int8_scale']!r}"
            )
        if str(reference["tensor_sha256"]) != plan.tensor_sha256:
            mismatches.append("tensor_sha256 T25 与 T29 不同")
        alias = reference.get("yolo_alias_layer_index")
        if alias is not None and int(alias) != plan.layer_index:
            mismatches.append(f"yolo_alias_layer_index T29={alias} T25 层={plan.layer_index}")
        expected_length = FROZEN_HEAD_BYTE_LENGTHS[name]
        if plan.byte_length != expected_length:
            mismatches.append(
                f"byte_length {plan.byte_length} != 冻结值 {expected_length}"
            )
        expected_shape = (1, 30, 13 if name == HEAD13_NAME else 26, 13 if name == HEAD13_NAME else 26)
        if plan.shape_nchw != expected_shape:
            mismatches.append(f"shape_nchw {list(plan.shape_nchw)} != {list(expected_shape)}")
        if mismatches:
            raise UpstreamError(
                f"样本 {index_sample.get('sample_id')} 头 {name} 绑定不一致：" + "；".join(mismatches)
            )
        result[name] = HeadPlan(
            name=plan.name,
            layer_index=plan.layer_index,
            alias_layer_index=plan.alias_layer_index,
            source_convolution_layer_index=(
                int(reference["source_convolution_layer_index"])
                if reference.get("source_convolution_layer_index") is not None
                else plan.alias_layer_index
            ),
            byte_offset=plan.byte_offset,
            byte_length=plan.byte_length,
            scale=float(reference["int8_scale"]),
            tensor_sha256=plan.tensor_sha256,
            shape_nchw=plan.shape_nchw,
            offset_source=plan.offset_source,
        )
    return result


def load_upstream_dataset(
    paths: UpstreamPaths,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """载入 T25 索引、T29 参考与 T01 样本清单，并核对样本 order/集合。"""

    index = load_json(paths.t25_index)
    reference = load_json(paths.t29_ref)
    catalog = load_json(paths.catalog)

    index_ids = [str(s["sample_id"]) for s in index["samples"]]
    ref_ids = [str(s["sample_id"]) for s in reference["samples"]]
    cat_ids = [str(s["sample_id"]) for s in catalog["samples"]]
    if not (index_ids == ref_ids == cat_ids):
        raise UpstreamError(
            "T25 索引 / T29 参考 / T01 清单的样本顺序或集合不一致："
            f"{len(index_ids)}/{len(ref_ids)}/{len(cat_ids)}"
        )
    if len(index_ids) != 109:
        raise UpstreamError(f"固定样本数应为 109，实际 {len(index_ids)}")
    return index, reference, catalog


def index_samples_by_id(index: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    """按 sample_id 建立 T25 索引样本映射。"""

    return {str(sample["sample_id"]): sample for sample in index["samples"]}


# --------------------------------------------------------------------------------------
# 逐样本解压 / 抽取 / 反量化 / 解码
# --------------------------------------------------------------------------------------


@dataclass
class RawStream:
    """一个样本解压后的整网 INT8 原始流及其字节校验结果。"""

    shard_path: Path
    raw: bytearray
    compressed_bytes: int
    raw_bytes: int
    compressed_sha256: str
    raw_sha256: str
    zlib_complete: bool

    def as_json(self) -> dict[str, Any]:
        """转为机器可读记录（不含原始字节）。"""

        return {
            "shard": str(self.shard_path),
            "codec": "zlib",
            "compressed_bytes": self.compressed_bytes,
            "raw_bytes": self.raw_bytes,
            "compressed_sha256": self.compressed_sha256,
            "raw_stream_sha256": self.raw_sha256,
            "zlib_stream_complete": self.zlib_complete,
        }


def read_shard_stream(shard_path: Path) -> RawStream:
    """流式解压一个 zlib 分片，同时计算压缩/解压两侧 SHA-256。"""

    shard_path = Path(shard_path)
    if not shard_path.is_file():
        raise UpstreamError(f"张量分片不存在：{shard_path}")
    digest_compressed = hashlib.sha256()
    decompressor = zlib.decompressobj()
    raw = bytearray()
    compressed_bytes = 0
    with shard_path.open("rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                break
            compressed_bytes += len(chunk)
            digest_compressed.update(chunk)
            raw += decompressor.decompress(chunk)
    raw += decompressor.flush()
    if not decompressor.eof:
        raise UpstreamError(f"zlib 流未正常结束（数据被截断或损坏）：{shard_path}")
    if decompressor.unused_data:
        raise UpstreamError(f"zlib 流尾部存在未消费数据：{shard_path}")
    return RawStream(
        shard_path=shard_path,
        raw=raw,
        compressed_bytes=compressed_bytes,
        raw_bytes=len(raw),
        compressed_sha256=digest_compressed.hexdigest(),
        raw_sha256=sha256_bytes(raw),
        zlib_complete=True,
    )


def dequantize_int8(data: bytes | bytearray | memoryview, scale: float) -> list[float]:
    """signed INT8 → float64 logits（乘各头 int8_scale），逐值显式转换。"""

    payload = bytes(data)
    signed = struct.unpack("{0}b".format(len(payload)), payload)
    scale_value = float(scale)
    return [value * scale_value for value in signed]


def detection_record(prediction: Any) -> dict[str, Any]:
    """把 D6 ``Prediction`` 转为 S4-A 字段命名的机器可读框记录。"""

    box = list(getattr(prediction, "box"))
    return {
        "class_id": int(getattr(prediction, "class_id")),
        "class_name": str(getattr(prediction, "name")),
        "score": float(getattr(prediction, "confidence")),
        "xyxy": [float(value) for value in box],
        "source_order": int(getattr(prediction, "source_order")),
    }


def decode_heads(
    decoder: DecoderBinding | Any,
    head_logits: Mapping[str, Sequence[float]],
    geometry_wh: Sequence[int],
    score_threshold: float = FROZEN_SCORE_THRESHOLD,
) -> list[dict[str, Any]]:
    """调用冻结 D9 解码两头 logits，返回 S4-A 命名的框记录列表。"""

    if not (0.25 <= float(score_threshold) <= 0.50):
        raise S4CError("score_threshold 必须在闭区间 [0.25, 0.50]（D9 API 限制）")
    module = decoder.module if isinstance(decoder, DecoderBinding) else decoder
    width, height = int(geometry_wh[0]), int(geometry_wh[1])
    # D9 以头自身的名称（"13x13"/"26x26"）为键；映射取自冻结 HEAD_SPECS，不硬编码。
    specs = getattr(module, "HEAD_SPECS", None)
    if specs:
        key_for = {
            _head_name_from_shape((1, 30, int(spec.grid_width), int(spec.grid_height))): spec.name
            for spec in specs
        }
    else:  # pragma: no cover - 冻结 D9 一定暴露 HEAD_SPECS，这里仅作防御
        key_for = {HEAD13_NAME: "13x13", HEAD26_NAME: "26x26"}
    head_input = {key_for[name]: list(head_logits[name]) for name in (HEAD13_NAME, HEAD26_NAME)}
    predictions = module.decode_yolov4_tiny416(
        head_input,
        "s4c_replay",
        width,
        height,
        score_threshold=float(score_threshold),
    )
    return [detection_record(item) for item in predictions]


def compare_detections(
    expected: Sequence[Mapping[str, Any]],
    actual: Sequence[Mapping[str, Any]],
    tolerance: float = FROZEN_SCORE_ABS_TOLERANCE,
) -> dict[str, Any]:
    """逐框对拍：离散字段全等，score/xyxy 各分量绝对误差 ≤ tolerance。

    返回 {"mismatches": [...], "max_score_abs_error", "max_xyxy_abs_error",
    "count_expected", "count_actual"}。mismatch 记录含框序号、字段、期望/实际。
    """

    mismatches: list[dict[str, Any]] = []
    max_score: float | None = None
    max_xyxy: float | None = None
    count_expected = len(expected)
    count_actual = len(actual)
    if count_expected != count_actual:
        mismatches.append(
            {
                "kind": "discrete",
                "index": None,
                "field": "detection_count",
                "expected": count_expected,
                "actual": count_actual,
                "note": "框数不同，仅对公共前缀逐框比较",
            }
        )
    for index in range(min(count_expected, count_actual)):
        exp = expected[index]
        act = actual[index]
        for field_name in DISCRETE_FIELDS:
            if exp.get(field_name) != act.get(field_name):
                mismatches.append(
                    {
                        "kind": "discrete",
                        "index": index,
                        "field": field_name,
                        "expected": exp.get(field_name),
                        "actual": act.get(field_name),
                    }
                )
        exp_score, act_score = exp.get("score"), act.get("score")
        if exp_score is None or act_score is None:
            mismatches.append(
                {
                    "kind": "missing_field",
                    "index": index,
                    "field": "score",
                    "expected": exp_score,
                    "actual": act_score,
                }
            )
        else:
            error = abs(float(exp_score) - float(act_score))
            max_score = error if max_score is None else max(max_score, error)
            if error > tolerance:
                mismatches.append(
                    {
                        "kind": "numeric",
                        "index": index,
                        "field": "score",
                        "expected": float(exp_score),
                        "actual": float(act_score),
                        "abs_error": error,
                        "tolerance": tolerance,
                    }
                )
        exp_box, act_box = exp.get("xyxy"), act.get("xyxy")
        if exp_box is None or act_box is None or len(exp_box) != 4 or len(act_box) != 4:
            mismatches.append(
                {
                    "kind": "missing_field",
                    "index": index,
                    "field": "xyxy",
                    "expected": exp_box,
                    "actual": act_box,
                }
            )
            continue
        for component in range(4):
            error = abs(float(exp_box[component]) - float(act_box[component]))
            max_xyxy = error if max_xyxy is None else max(max_xyxy, error)
            if error > tolerance:
                mismatches.append(
                    {
                        "kind": "numeric",
                        "index": index,
                        "field": "xyxy[{0}]".format(component),
                        "component": component,
                        "expected": float(exp_box[component]),
                        "actual": float(act_box[component]),
                        "abs_error": error,
                        "tolerance": tolerance,
                    }
                )
    return {
        "mismatches": mismatches,
        "max_score_abs_error": max_score,
        "max_xyxy_abs_error": max_xyxy,
        "count_expected": count_expected,
        "count_actual": count_actual,
    }


# --------------------------------------------------------------------------------------
# 实测 heads 目录加载（--actual）
# --------------------------------------------------------------------------------------


def _normalize_int_sequence(values: Sequence[Any]) -> bytearray:
    """把整数序列规范化为 INT8 二补码字节（有符号优先，其次无符号字节）。"""

    numbers: list[int] = []
    for value in values:
        if isinstance(value, bool):
            raise ActualInputError("int8 列表不允许布尔值")
        if isinstance(value, float):
            if not float(value).is_integer():
                raise ActualInputError(f"int8 列表含非整数值：{value!r}")
            value = int(value)
        if not isinstance(value, int):
            raise ActualInputError(f"int8 列表含非整数项：{value!r}")
        numbers.append(int(value))
    if all(-128 <= value <= 127 for value in numbers):
        return bytearray(value & 0xFF for value in numbers)
    if all(0 <= value <= 255 for value in numbers):
        return bytearray(numbers)
    raise ActualInputError("int8 列表取值既不在 -128..127 也不在 0..255")


def _decode_head_payload(payload: Any, label: str) -> tuple[bytearray, float | None]:
    """解析一个头的载荷，返回 (INT8 字节, 可选 scale 覆盖)。"""

    scale_override: float | None = None
    if isinstance(payload, str):
        text = payload.strip()
        lowered = text.lower()
        if lowered.startswith("hex:"):
            return bytearray(bytes.fromhex(text[4:])), None
        if lowered.startswith("base64:"):
            return bytearray(base64.b64decode(text[7:])), None
        try:
            return bytearray(bytes.fromhex(text)), None
        except ValueError as exc:
            raise ActualInputError(f"{label} 的字符串既不是 hex 也不是 base64：{exc}") from exc
    if isinstance(payload, (bytes, bytearray, memoryview)):
        return bytearray(payload), None
    if isinstance(payload, Mapping):
        for key in ("int8_scale", "scale", "dequant_scale"):
            if payload.get(key) is not None:
                scale_override = float(payload[key])
        for key in ("int8", "int8_values", "values", "data"):
            if payload.get(key) is not None:
                return _normalize_int_sequence(payload[key]), scale_override
        if payload.get("hex") is not None:
            return bytearray(bytes.fromhex(str(payload["hex"]).strip())), scale_override
        if payload.get("base64") is not None:
            return bytearray(base64.b64decode(str(payload["base64"]).strip())), scale_override
        if payload.get("bytes") is not None:
            return _normalize_int_sequence(payload["bytes"]), scale_override
        raise ActualInputError(f"{label} 的字典载荷缺少已知键（int8/hex/base64/bytes）")
    if isinstance(payload, Sequence):
        return _normalize_int_sequence(payload), None
    raise ActualInputError(f"{label} 载荷类型不支持：{type(payload).__name__}")


def _head_name_tokens(name: str) -> tuple[str, ...]:
    """一个头可能出现的文件名片段。"""

    if name == HEAD13_NAME:
        return ("head13", "head_13", "h13")
    return ("head26", "head_26", "h26")


def load_actual_heads(actual_dir: Path, sample_id: str, expected_lengths: Mapping[str, int]) -> dict[str, Any]:
    """按文档化格式从 ``--actual`` 目录加载一个样本的两头 INT8 字节。"""

    actual_dir = Path(actual_dir)
    if not actual_dir.is_dir():
        raise ActualInputError(f"--actual 目录不存在：{actual_dir}")

    result: dict[str, Any] = {}

    def record(name: str, payload: bytearray, source: Path, scale_override: float | None) -> None:
        expected = int(expected_lengths[name])
        if len(payload) != expected:
            raise ActualInputError(
                f"{source} 的 {name} 长度 {len(payload)} != 期望 {expected}"
            )
        if name in result:
            return
        result[name] = {
            "bytes": payload,
            "source": str(source),
            "scale_override": scale_override,
        }

    # a) 每头独立文件
    for name in (HEAD13_NAME, HEAD26_NAME):
        if name in result:
            continue
        candidates: list[Path] = []
        for token in _head_name_tokens(name):
            candidates.extend(
                [
                    actual_dir / f"{sample_id}.{token}.bin",
                    actual_dir / f"{sample_id}_{token}.bin",
                    actual_dir / f"{sample_id}.{token}",
                    actual_dir / f"{sample_id}_{token}",
                ]
            )
        for candidate in candidates:
            if candidate.is_file():
                record(name, bytearray(candidate.read_bytes()), candidate, None)
                break

    # b) 顺序拼接文件
    if len(result) != 2:
        for candidate in (
            actual_dir / f"{sample_id}.heads.bin",
            actual_dir / f"{sample_id}_heads.bin",
        ):
            if candidate.is_file():
                blobs = bytearray(candidate.read_bytes())
                cursor = 0
                for name in (HEAD13_NAME, HEAD26_NAME):
                    length = int(expected_lengths[name])
                    record(name, blobs[cursor : cursor + length], candidate, None)
                    cursor += length
                if cursor != len(blobs):
                    raise ActualInputError(
                        f"{candidate} 总长度 {len(blobs)} != 两头之和 {cursor}"
                    )
                break

    # c) JSON 载荷
    if len(result) != 2:
        for candidate in (
            actual_dir / f"{sample_id}.json",
            actual_dir / f"{sample_id}.heads.json",
            actual_dir / f"{sample_id}_heads.json",
        ):
            if not candidate.is_file():
                continue
            payload = load_json(candidate)
            if isinstance(payload, Mapping) and isinstance(payload.get("heads"), Mapping):
                payload = payload["heads"]
            if not isinstance(payload, Mapping):
                raise ActualInputError(f"{candidate} 顶层必须是对象")
            for name in (HEAD13_NAME, HEAD26_NAME):
                if name not in payload:
                    raise ActualInputError(f"{candidate} 缺少 {name}")
                blob, scale_override = _decode_head_payload(payload[name], f"{candidate}:{name}")
                record(name, blob, candidate, scale_override)
            break

    missing = [name for name in (HEAD13_NAME, HEAD26_NAME) if name not in result]
    if missing:
        raise ActualInputError(
            f"{actual_dir} 未找到样本 {sample_id} 的 {missing}（支持 .head13.bin/.head26.bin、"
            ".heads.bin、.json 三种命名，见模块文档）"
        )
    return result


# --------------------------------------------------------------------------------------
# 样本选择
# --------------------------------------------------------------------------------------


def select_sample_ids(
    all_ids: Sequence[str],
    *,
    limit: int | None = None,
    seed: int | None = None,
    explicit: Sequence[str] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    """按全量 / 随机子集 / 显式样本号选择样本，返回 (id 列表, 可复核的选择元数据)。"""

    ordered = [str(item) for item in all_ids]
    known = set(ordered)
    if explicit:
        unknown = [item for item in explicit if item not in known]
        if unknown:
            raise S4CError(f"--sample-id 含未知样本：{unknown[:5]}")
        wanted = set(str(item) for item in explicit)
        selected = [item for item in ordered if item in wanted]
        return selected, {
            "rule": "explicit_sample_ids",
            "available": len(ordered),
            "selected": len(selected),
            "limit": limit,
            "seed": seed,
            "seed_source": "not_used",
            "sample_ids": selected,
            "explicit_sample_ids": [str(item) for item in explicit],
        }

    if limit is None or limit >= len(ordered):
        return list(ordered), {
            "rule": "full_all_samples",
            "available": len(ordered),
            "selected": len(ordered),
            "limit": limit,
            "seed": None,
            "seed_source": "not_used_full_selection",
            "sample_ids": list(ordered),
        }

    if type(limit) is not int or limit <= 0:
        raise S4CError("--limit 必须是正整数")
    used_seed = DEFAULT_SUBSET_SEED if seed is None else int(seed)
    rng = random.Random(used_seed)
    picked = sorted(rng.sample(range(len(ordered)), limit))
    selected = [ordered[index] for index in picked]
    return selected, {
        "rule": "seeded_random_subset",
        "available": len(ordered),
        "selected": len(selected),
        "limit": limit,
        "seed": used_seed,
        "seed_source": "cli" if seed is not None else "default",
        "sample_ids": selected,
    }


# --------------------------------------------------------------------------------------
# 逐样本对拍
# --------------------------------------------------------------------------------------


def _finished_sample_record(
    record: dict[str, Any],
    expected: Sequence[Mapping[str, Any]],
    actual: Sequence[Mapping[str, Any]],
    tolerance: float,
) -> dict[str, Any]:
    """填充对拍结果并判定样本状态。"""

    comparison = compare_detections(expected, actual, tolerance)
    record["detection_count_expected"] = comparison["count_expected"]
    record["detection_count_actual"] = comparison["count_actual"]
    record["detections_expected"] = [dict(item) for item in expected]
    record["detections_actual"] = [dict(item) for item in actual]
    record["max_score_abs_error"] = comparison["max_score_abs_error"]
    record["max_xyxy_abs_error"] = comparison["max_xyxy_abs_error"]
    record.setdefault("mismatches", [])
    record["mismatches"] = list(record["mismatches"]) + comparison["mismatches"]
    record["mismatch_count"] = len(record["mismatches"])
    record["status"] = "PASS" if not record["mismatches"] else "FAIL"
    return record


def _select_head_plan(index_sample: Mapping[str, Any]) -> dict[str, HeadPlan]:
    """只从索引取偏移/长度（T29 交叉核对在 golden 模式下用 build_head_plans 完成）。"""

    plans: dict[str, HeadPlan] = {}
    for tensor in index_sample["network"]["tensors"]:
        if tensor.get("op") != "yolo":
            continue
        name = _head_name_from_shape(tensor["shape_nchw"])
        plans[name] = HeadPlan(
            name=name,
            layer_index=int(tensor["layer_index"]),
            alias_layer_index=(
                int(tensor["alias_of_layer_index"])
                if tensor.get("alias_of_layer_index") is not None
                else None
            ),
            source_convolution_layer_index=(
                int(tensor["alias_of_layer_index"])
                if tensor.get("alias_of_layer_index") is not None
                else None
            ),
            byte_offset=int(tensor["byte_offset"]),
            byte_length=int(tensor["byte_length"]),
            scale=float(tensor["scale"]),
            tensor_sha256=str(tensor["tensor_sha256"]),
            shape_nchw=tuple(int(v) for v in tensor["shape_nchw"]),
            offset_source=(
                "t25_index.network.tensors[layer_index={0}].byte_offset/byte_length".format(
                    tensor["layer_index"]
                )
            ),
        )
    return plans


def _cross_check_sample_identity(
    index_sample: Mapping[str, Any],
    t29_sample: Mapping[str, Any],
    catalog_sample: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """核对 frame_id / 几何 / 预处理输入 SHA 在三份上游之间一致。"""

    mismatches: list[dict[str, Any]] = []
    sample_id = str(t29_sample["sample_id"])
    frame_ids = {
        "t25_index": index_sample.get("frame_id"),
        "t29_reference": t29_sample.get("frame_id"),
        "t01_catalog": catalog_sample.get("frame_id"),
    }
    if len(set(frame_ids.values())) != 1:
        mismatches.append(
            {"kind": "upstream_identity", "field": "frame_id", "expected": frame_ids["t01_catalog"], "actual": frame_ids, "sample_id": sample_id}
        )
    geometry = t29_sample.get("input", {}).get("geometry_wh")
    if not geometry or len(geometry) != 2:
        mismatches.append(
            {"kind": "upstream_identity", "field": "geometry_wh", "expected": "[w,h]", "actual": geometry, "sample_id": sample_id}
        )
    else:
        expected_wh = [int(geometry[0]), int(geometry[1])]
        cross = {
            "t25_original_input": [
                int(index_sample.get("original_input", {}).get("width", -1)),
                int(index_sample.get("original_input", {}).get("height", -1)),
            ],
            "t01_catalog": [int(catalog_sample.get("width", -1)), int(catalog_sample.get("height", -1))],
        }
        for label, values in cross.items():
            if values != expected_wh:
                mismatches.append(
                    {
                        "kind": "upstream_identity",
                        "field": f"geometry_wh[{label}]",
                        "expected": expected_wh,
                        "actual": values,
                        "sample_id": sample_id,
                    }
                )
    pl_hashes = {
        "t25_preprocessed_input": index_sample.get("preprocessed_input", {}).get("sha256"),
        "t29_pl_input": t29_sample.get("input", {}).get("pl_input_sha256"),
        "t01_catalog": catalog_sample.get("pl_input_sha256"),
    }
    if len(set(pl_hashes.values())) != 1:
        mismatches.append(
            {
                "kind": "upstream_identity",
                "field": "pl_input_sha256",
                "expected": pl_hashes["t01_catalog"],
                "actual": pl_hashes,
                "sample_id": sample_id,
            }
        )
    return mismatches


def evaluate_golden_sample(
    *,
    decoder: DecoderBinding,
    index_sample: Mapping[str, Any],
    t29_sample: Mapping[str, Any],
    catalog_sample: Mapping[str, Any],
    tensors_dir: Path,
    score_threshold: float = FROZEN_SCORE_THRESHOLD,
    tolerance: float = FROZEN_SCORE_ABS_TOLERANCE,
) -> dict[str, Any]:
    """对 2A 冻结分片执行“解压 → 抽取 → 反量化 → 解码 → 对拍”。"""

    started = time.perf_counter()
    sample_id = str(t29_sample["sample_id"])
    record: dict[str, Any] = {
        "sample_id": sample_id,
        "sample_index": int(index_sample.get("sample_index", -1)),
        "frame_id": t29_sample.get("frame_id"),
        "geometry_wh": list(t29_sample.get("input", {}).get("geometry_wh", [])),
        "mode": "golden",
        "mismatches": [],
        "heads": {},
    }
    plans = build_head_plans(index_sample, t29_sample)
    record["head_plans"] = {name: plan.as_json() for name, plan in plans.items()}

    network = index_sample["network"]
    shard_declared = str(network["compressed_shard"]["path"])
    shard_path = Path(tensors_dir) / Path(shard_declared).name
    record["raw_stream_declared_path"] = shard_declared
    stream = read_shard_stream(shard_path)

    expected_compressed = str(network["compressed_shard"]["sha256"])
    expected_raw = str(network["raw_stream_sha256"])
    expected_raw_decompressed = str(network["compressed_shard"]["decompressed_sha256"])
    expected_decompressed_bytes = int(network["compressed_shard"]["decompressed_bytes"])
    raw_record = stream.as_json()
    raw_record.update(
        {
            "expected_compressed_sha256": expected_compressed,
            "expected_raw_stream_sha256": expected_raw,
            "expected_decompressed_sha256": expected_raw_decompressed,
            "expected_raw_bytes": expected_decompressed_bytes,
            "compressed_byte_match": stream.compressed_sha256 == expected_compressed,
            "raw_stream_byte_match": (
                stream.raw_sha256 == expected_raw == expected_raw_decompressed
            ),
            "raw_bytes_match": stream.raw_bytes == expected_decompressed_bytes,
        }
    )
    record["raw_stream"] = raw_record
    if not raw_record["compressed_byte_match"]:
        record["mismatches"].append(
            {
                "kind": "byte",
                "field": "compressed_shard.sha256",
                "expected": expected_compressed,
                "actual": stream.compressed_sha256,
            }
        )
    if not raw_record["raw_stream_byte_match"]:
        record["mismatches"].append(
            {
                "kind": "byte",
                "field": "network.raw_stream_sha256",
                "expected": expected_raw,
                "actual": stream.raw_sha256,
            }
        )
    if not raw_record["raw_bytes_match"]:
        record["mismatches"].append(
            {
                "kind": "byte",
                "field": "network.compressed_shard.decompressed_bytes",
                "expected": expected_decompressed_bytes,
                "actual": stream.raw_bytes,
            }
        )

    head_logits: dict[str, list[float]] = {}
    for name, plan in plans.items():
        end = plan.byte_offset + plan.byte_length
        if end > len(stream.raw):
            record["heads"][name] = {"extract_error": "偏移超出解压流长度"}
            record["mismatches"].append(
                {
                    "kind": "extract",
                    "field": f"{name}.byte_offset+byte_length",
                    "expected": f"<= {len(stream.raw)}",
                    "actual": end,
                }
            )
            continue
        blob = stream.raw[plan.byte_offset : end]
        actual_sha = sha256_bytes(blob)
        t29_expected = str(t29_sample["head_tensors"][name]["tensor_sha256"])
        head_record = plan.as_json()
        head_record.update(
            {
                "actual_tensor_sha256": actual_sha,
                "expected_tensor_sha256_t29": t29_expected,
                "byte_match": actual_sha == plan.tensor_sha256 == t29_expected,
                "extraction_source": str(shard_path),
            }
        )
        record["heads"][name] = head_record
        if not head_record["byte_match"]:
            record["mismatches"].append(
                {
                    "kind": "byte",
                    "field": f"{name}.tensor_sha256",
                    "expected": t29_expected,
                    "actual": actual_sha,
                    "byte_offset": plan.byte_offset,
                    "byte_length": plan.byte_length,
                }
            )
        head_logits[name] = dequantize_int8(blob, plan.scale)

    # 释放解压流，逐样本内存不累积。
    del stream

    record["mismatches"].extend(
        _cross_check_sample_identity(index_sample, t29_sample, catalog_sample)
    )

    if len(head_logits) == 2 and not any(
        item["kind"] in ("byte", "extract") for item in record["mismatches"]
    ):
        geometry = record["geometry_wh"]
        actual_detections = decode_heads(decoder, head_logits, geometry, score_threshold)
        expected_detections = [
            {
                "class_id": int(item["class_id"]),
                "class_name": str(item["class_name"]),
                "score": float(item["score"]),
                "xyxy": [float(v) for v in item["xyxy"]],
                "source_order": int(item["source_order"]),
            }
            for item in t29_sample.get("detections", [])
        ]
        record["raw_candidate_count_before_stable_nms"] = t29_sample.get(
            "raw_candidate_count_before_stable_nms"
        )
        _finished_sample_record(record, expected_detections, actual_detections, tolerance)
    else:
        record["detection_count_expected"] = len(t29_sample.get("detections", []))
        record["detection_count_actual"] = None
        record["max_score_abs_error"] = None
        record["max_xyxy_abs_error"] = None
        record["status"] = "FAIL"
        record["mismatch_count"] = len(record["mismatches"])

    record["elapsed_seconds"] = time.perf_counter() - started
    return record


def evaluate_actual_sample(
    *,
    decoder: DecoderBinding,
    t29_sample: Mapping[str, Any],
    index_sample: Mapping[str, Any],
    actual_dir: Path,
    score_threshold: float = FROZEN_SCORE_THRESHOLD,
    tolerance: float = FROZEN_SCORE_ABS_TOLERANCE,
    golden_heads: Mapping[str, bytes] | None = None,
    golden_heads_info: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """用 ``--actual`` 目录中的实测 heads 与 T29 golden 对拍。

    ``golden_heads`` 若可用，则对不一致的头给出逐值定位（首个差异字节偏移、
    差异字节数、期望/实际字节值、最大 INT8 差值）；不可用时退化为只比对
    SHA-256（期望值仍来自 T29 冻结参考），并在报告中显式记录降级事实。
    """

    started = time.perf_counter()
    sample_id = str(t29_sample["sample_id"])
    plan_source = _select_head_plan(index_sample)
    expected_lengths = {
        name: int(t29_sample["head_tensors"][name]["byte_length"]) for name in (HEAD13_NAME, HEAD26_NAME)
    }
    record: dict[str, Any] = {
        "sample_id": sample_id,
        "sample_index": int(index_sample.get("sample_index", -1)),
        "frame_id": t29_sample.get("frame_id"),
        "geometry_wh": list(t29_sample.get("input", {}).get("geometry_wh", [])),
        "mode": "actual",
        "actual_dir": str(actual_dir),
        "mismatches": [],
        "heads": {},
        "golden_byte_reference": dict(golden_heads_info)
        if golden_heads_info
        else {
            "available": bool(golden_heads),
            "reason": "调用方未提供 golden 字节",
        },
    }
    record["head_plans"] = {name: plan.as_json() for name, plan in plan_source.items()}

    loaded: dict[str, Any] | None = None
    try:
        loaded = load_actual_heads(actual_dir, sample_id, expected_lengths)
    except ActualInputError as exc:
        record["mismatches"].append(
            {"kind": "actual_input", "field": "heads", "expected": "两头 INT8 文件", "actual": str(exc)}
        )

    head_logits: dict[str, list[float]] = {}
    if loaded:
        for name in (HEAD13_NAME, HEAD26_NAME):
            item = loaded[name]
            blob = item["bytes"]
            actual_sha = sha256_bytes(blob)
            t29_expected = str(t29_sample["head_tensors"][name]["tensor_sha256"])
            plan = plan_source[name]
            scale = plan.scale
            scale_source = "t29_reference"
            if item.get("scale_override") is not None:
                scale = float(item["scale_override"])
                scale_source = "actual_override"
            byte_match = actual_sha == t29_expected
            golden_blob = (golden_heads or {}).get(name)
            if byte_match:
                byte_comparison: dict[str, Any] | None = None
                if golden_blob is not None:
                    byte_comparison = {
                        "compared_bytes": min(len(golden_blob), len(blob)),
                        "length_match": len(golden_blob) == len(blob),
                        "identical": True,
                        "diff_byte_count": 0,
                        "first_diff_offset": None,
                        "expected_byte": None,
                        "actual_byte": None,
                        "max_abs_int8_delta": 0,
                        "diff_offsets_preview": [],
                    }
            elif golden_blob is not None:
                byte_comparison = compare_head_bytes(golden_blob, blob)
            else:
                byte_comparison = {
                    "available": False,
                    "reason": "golden 字节不可用，仅比对 SHA-256 与 T29 期望值",
                }
            head_record = {
                "name": name,
                "byte_length": len(blob),
                "expected_byte_length": expected_lengths[name],
                "actual_tensor_sha256": actual_sha,
                "expected_tensor_sha256_t29": t29_expected,
                "byte_match": byte_match,
                "source_file": item["source"],
                "int8_scale": scale,
                "scale_source": scale_source,
                "offset_source_for_reference": plan.offset_source,
                "golden_byte_comparison": byte_comparison,
            }
            record["heads"][name] = head_record
            if not byte_match:
                mismatch: dict[str, Any] = {
                    "kind": "byte",
                    "field": f"{name}.tensor_sha256",
                    "expected": t29_expected,
                    "actual": actual_sha,
                    "source_file": item["source"],
                    "byte_length": len(blob),
                }
                if byte_comparison and byte_comparison.get("diff_byte_count") is not None:
                    mismatch.update(
                        {
                            "first_diff_offset": byte_comparison.get("first_diff_offset"),
                            "diff_byte_count": byte_comparison.get("diff_byte_count"),
                            "expected_byte": byte_comparison.get("expected_byte"),
                            "actual_byte": byte_comparison.get("actual_byte"),
                            "max_abs_int8_delta": byte_comparison.get("max_abs_int8_delta"),
                            "diff_offsets_preview": byte_comparison.get("diff_offsets_preview"),
                        }
                    )
                record["mismatches"].append(mismatch)
            head_logits[name] = dequantize_int8(blob, scale)

    if len(head_logits) == 2:
        geometry = record["geometry_wh"]
        actual_detections = decode_heads(decoder, head_logits, geometry, score_threshold)
        expected_detections = [
            {
                "class_id": int(item["class_id"]),
                "class_name": str(item["class_name"]),
                "score": float(item["score"]),
                "xyxy": [float(v) for v in item["xyxy"]],
                "source_order": int(item["source_order"]),
            }
            for item in t29_sample.get("detections", [])
        ]
        record["raw_candidate_count_before_stable_nms"] = t29_sample.get(
            "raw_candidate_count_before_stable_nms"
        )
        _finished_sample_record(record, expected_detections, actual_detections, tolerance)
    else:
        record["detection_count_expected"] = len(t29_sample.get("detections", []))
        record["detection_count_actual"] = None
        record["max_score_abs_error"] = None
        record["max_xyxy_abs_error"] = None
        record["status"] = "FAIL"
        record["mismatch_count"] = len(record["mismatches"])

    record["elapsed_seconds"] = time.perf_counter() - started
    return record


# --------------------------------------------------------------------------------------
# 报告装配
# --------------------------------------------------------------------------------------


def comparison_spec(
    paths: UpstreamPaths,
    decoder: DecoderBinding,
    contract: Mapping[str, Any] | None,
    score_threshold: float,
    tolerance: float,
) -> dict[str, Any]:
    """报告中的“口径”节：与 S4-A 契约字段命名对齐。"""

    spec: dict[str, Any] = {
        "model_id": "tiny416",
        "classes": list(FROZEN_CLASSES),
        "class_order_note": "class_id 0..4 严格按此顺序，不得重排",
        "score_threshold": float(score_threshold),
        "score_threshold_rule": "score >= 阈值（含等号，D6 语义）",
        "nms_iou": FROZEN_NMS_IOU,
        "nms_rule": "类别内 greedy NMS，跨类别不抑制；先按分数稳定排序截断到 15 个，再执行 NMS",
        "max_outputs_per_image": FROZEN_MAX_OUTPUTS,
        "score_definition": "score = sigmoid(objectness_logit) * sigmoid(class_logit)",
        "coordinate_policy": "D2 整数截断 resize + 左上 floor padding 逆映射；逐边裁剪到 [0,1]；裁剪后零面积丢弃",
        "tie_order": "head 顺序 → row-major cell → anchor-local 顺序 → class_id",
        "dequantization": "signed int8 × 各头 head int8_scale（float64）",
        "geometry_source": "T29 samples[i].input.geometry_wh（顺序 width,height），与 T25 original_input / T01 清单交叉核对",
        "head_layout": "查看时 reshape 为 [anchor=3, entry=10, row, col]；entry 顺序 x,y,w,h,objectness,class0..class4",
        "head_byte_lengths": dict(FROZEN_HEAD_BYTE_LENGTHS),
        "byte_first_rule": "先要求两头全部 INT8 字节 SHA-256 完全相同，再解码比较",
        "max_error_null_semantics": (
            "样本级 max_score_abs_error / max_xyxy_abs_error 为 null 表示该样本两侧没有可比较的公共框"
            "（例如期望与实测均为零框），不是 0 误差；summary 中的最大值只统计非 null 样本"
        ),
        "tolerance": {
            "discrete_fields": list(DISCRETE_FIELDS) + ["detection_count(框数)"],
            "discrete_rule": "必须完全相同",
            "score_abs_tolerance": float(tolerance),
            "xyxy_abs_tolerance_per_component": float(tolerance),
            "relative_tolerance": FROZEN_RELATIVE_TOLERANCE,
            "source": COMPARISON_SOURCE,
        },
        "decoder": decoder.as_json(),
        "frozen_2a_constants_from_manifest": {
            "address_map_heads": "T01 tiny416_model_manifest.json address_map.heads（name/int8_scale/length_bytes）",
            "detection_postprocess_comparison": "见独立交叉核对产物 manifest_head_crosscheck.json",
        },
    }
    if contract:
        frozen = contract.get("frozen_2a_constants", {})
        spec["s4a_contract_alignment"] = {
            "contract_path": str(paths.contract) if paths.contract else None,
            "contract_sha256": paths.contract_sha256,
            "contract_status": paths.contract_status,
            "result_record_fields_used": [
                "frame_id",
                "geometry",
                "detection_count",
                "detections",
                "error_code",
            ],
            "detection_record_fields_used": [
                "class_id",
                "class_name",
                "score",
                "xyxy",
                "source_order",
            ],
            "contract_field_policy": {
                "read_from_contract": ["frozen_2a_constants"],
                "validated": "只校验 frozen_2a_constants 的冻结常量（阈值/NMS/每图上限/类别顺序/两头字节数/score 与 xyxy 容限）",
                "not_validated": "不校验 result_record/detection_record 的字段集合或 required 标志；契约新增的可选诊断字段（如 candidate_count_pre_threshold、xyxy_px）既不参与对拍，也不会被当成缺失而报 FAIL",
                "candidate_fields": "不参与对拍；报告只原样转发 T29 raw_candidate_count_before_stable_nms 作为参考读数",
                "comparison_scope": "框级字段（detection_count/class_id/class_name/score/xyxy/source_order）+ 两头 INT8 字节 SHA-256",
            },
            "frozen_constants_match": {
                "score_threshold": frozen.get("score_threshold") == FROZEN_SCORE_THRESHOLD,
                "nms_iou": frozen.get("nms_iou") == FROZEN_NMS_IOU,
                "max_outputs_per_image": frozen.get("max_outputs_per_image") == FROZEN_MAX_OUTPUTS,
                "classes": frozen.get("classes") == list(FROZEN_CLASSES),
                "head13_byte_length": frozen.get("head13", {}).get("byte_length")
                == FROZEN_HEAD_BYTE_LENGTHS[HEAD13_NAME],
                "head26_byte_length": frozen.get("head26", {}).get("byte_length")
                == FROZEN_HEAD_BYTE_LENGTHS[HEAD26_NAME],
                "score_abs_tolerance": frozen.get("comparison_tolerance", {}).get(
                    "score_abs_tolerance"
                )
                == FROZEN_SCORE_ABS_TOLERANCE,
                "xyxy_abs_tolerance": frozen.get("comparison_tolerance", {}).get(
                    "xyxy_abs_tolerance_per_component"
                )
                == FROZEN_XYXY_ABS_TOLERANCE,
            },
            "note": "字段名与容限口径取自 S4-A 契约；本工具不修改契约，也不产生阶段4 G0 结论。",
        }
    return spec


def run_compare(
    *,
    paths: UpstreamPaths,
    decoder: DecoderBinding,
    index_by_id: Mapping[str, Mapping[str, Any]],
    t29_by_id: Mapping[str, Mapping[str, Any]],
    catalog_by_id: Mapping[str, Mapping[str, Any]],
    selection: Mapping[str, Any],
    mode: str,
    actual_dir: Path | None = None,
    score_threshold: float = FROZEN_SCORE_THRESHOLD,
    tolerance: float = FROZEN_SCORE_ABS_TOLERANCE,
    run_id: str = "",
    contract: Mapping[str, Any] | None = None,
    upstream_records: Sequence[Mapping[str, Any]] = (),
    tool_path: Path | None = None,
    use_golden_bytes: bool = True,
) -> dict[str, Any]:
    """执行所选样本的逐样本对拍，返回机器可读报告。

    ``use_golden_bytes`` 只影响 ``--actual`` 模式：为真时额外读取 T25 分片里的
    golden 两头字节，用于逐值定位差异；分片不可用或显式关闭时退化为 SHA 比对。
    """

    tracemalloc.start()
    peak_rss = 0.0
    rss_measured = False
    try:
        import psutil  # type: ignore

        process = psutil.Process()
        rss_measured = True
    except Exception:  # pragma: no cover
        process = None  # type: ignore

    started_wall = now_utc8()
    started = time.perf_counter()
    sample_records: list[dict[str, Any]] = []
    for position, sample_id in enumerate(selection["sample_ids"], start=1):
        index_sample = index_by_id[sample_id]
        t29_sample = t29_by_id[sample_id]
        catalog_sample = catalog_by_id[sample_id]
        if mode == "golden":
            record = evaluate_golden_sample(
                decoder=decoder,
                index_sample=index_sample,
                t29_sample=t29_sample,
                catalog_sample=catalog_sample,
                tensors_dir=paths.tensors_dir,
                score_threshold=score_threshold,
                tolerance=tolerance,
            )
        elif mode == "actual":
            if actual_dir is None:
                raise S4CError("actual 模式必须提供 --actual 目录")
            golden_heads: Mapping[str, bytes] | None = None
            golden_info: dict[str, Any]
            if use_golden_bytes and paths.tensors_dir.is_dir():
                try:
                    golden_heads, info = read_golden_heads(
                        index_sample=index_sample,
                        t29_sample=t29_sample,
                        tensors_dir=paths.tensors_dir,
                    )
                    golden_info = {"available": True, **info}
                except (UpstreamError, OSError, KeyError, ValueError) as exc:
                    golden_heads = None
                    golden_info = {"available": False, "reason": str(exc)}
            else:
                golden_info = {
                    "available": False,
                    "reason": (
                        "已用 --no-golden-bytes 跳过 golden 字节读取"
                        if not use_golden_bytes
                        else f"T25 分片目录不可用：{paths.tensors_dir}"
                    ),
                }
            record = evaluate_actual_sample(
                decoder=decoder,
                t29_sample=t29_sample,
                index_sample=index_sample,
                actual_dir=actual_dir,
                score_threshold=score_threshold,
                tolerance=tolerance,
                golden_heads=golden_heads,
                golden_heads_info=golden_info,
            )
        else:
            raise S4CError(f"未知 mode：{mode}")
        record["position"] = position
        sample_records.append(record)
        if process is not None:
            try:
                peak_rss = max(peak_rss, process.memory_info().rss / (1024 * 1024))
            except Exception:  # pragma: no cover
                rss_measured = False
        # 早停：一旦出现 FAIL 也继续跑完（保留全量证据），但及时打印进度。
        if position % 10 == 0 or position == len(selection["sample_ids"]):
            passed = sum(1 for item in sample_records if item["status"] == "PASS")
            elapsed = time.perf_counter() - started
            print(
                f"[INFO] {position}/{len(selection['sample_ids'])} 样本完成，PASS={passed}，"
                f"耗时 {elapsed:.1f}s",
                flush=True,
            )

    total_seconds = time.perf_counter() - started
    traced_current, traced_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    failed = [item for item in sample_records if item["status"] != "PASS"]
    byte_mismatch_samples = [
        item["sample_id"]
        for item in sample_records
        if any(m["kind"] in ("byte", "extract") for m in item["mismatches"])
    ]
    frame_mismatch_samples = [
        item["sample_id"]
        for item in sample_records
        if any(m["kind"] in ("discrete", "numeric", "missing_field") for m in item["mismatches"])
    ]
    identity_mismatch_samples = [
        item["sample_id"]
        for item in sample_records
        if any(m["kind"] == "upstream_identity" for m in item["mismatches"])
    ]
    actual_input_mismatch_samples = [
        item["sample_id"]
        for item in sample_records
        if any(m["kind"] == "actual_input" for m in item["mismatches"])
    ]

    score_errors = [item["max_score_abs_error"] for item in sample_records if item["max_score_abs_error"] is not None]
    xyxy_errors = [item["max_xyxy_abs_error"] for item in sample_records if item["max_xyxy_abs_error"] is not None]
    per_sample_times = [item["elapsed_seconds"] for item in sample_records]

    total_mismatches = sum(item["mismatch_count"] for item in sample_records)
    status = "PASS" if total_mismatches == 0 and not failed else "FAIL"

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "run_id": run_id,
        "generated_utc8": now_utc8(),
        "started_utc8": started_wall,
        "status": status,
        "mode": mode,
        "tool": {
            "path": str(tool_path) if tool_path else str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
            "python": sys.version.split()[0],
            "module_doc_actual_format": "--actual 支持 <sid>.head13.bin/.head26.bin、<sid>.heads.bin、<sid>.json（见模块文档字符串）",
        },
        "upstream_paths": paths.as_json(),
        "s4a_contract": {
            "path": str(paths.contract) if paths.contract else None,
            "sha256": paths.contract_sha256,
            "status": paths.contract_status,
        },
        "upstream_bindings": list(upstream_records),
        "comparison_spec": comparison_spec(paths, decoder, contract, score_threshold, tolerance),
        "selection": dict(selection),
        "samples": sample_records,
        "per_sample_status": {item["sample_id"]: item["status"] for item in sample_records},
        "summary": {
            "samples_selected": len(sample_records),
            "samples_passed": len(sample_records) - len(failed),
            "samples_failed": len(failed),
            "failed_sample_ids": [item["sample_id"] for item in failed],
            "mismatch_total": total_mismatches,
            "byte_mismatch_samples": byte_mismatch_samples,
            "frame_mismatch_samples": frame_mismatch_samples,
            "upstream_identity_mismatch_samples": identity_mismatch_samples,
            "actual_input_mismatch_samples": actual_input_mismatch_samples,
            "byte_mismatch_count": len(byte_mismatch_samples),
            "frame_mismatch_count": len(frame_mismatch_samples),
            "total_detections_expected": sum(item.get("detection_count_expected") or 0 for item in sample_records),
            "total_detections_actual": sum(
                item.get("detection_count_actual") or 0
                for item in sample_records
                if item.get("detection_count_actual") is not None
            ),
            "max_score_abs_error": max(score_errors) if score_errors else None,
            "max_xyxy_abs_error": max(xyxy_errors) if xyxy_errors else None,
            "empty_detection_samples": sum(
                1 for item in sample_records if item.get("detection_count_expected") == 0
            ),
        },
        "timing": {
            "total_seconds": total_seconds,
            "per_sample_mean_seconds": (
                sum(per_sample_times) / len(per_sample_times) if per_sample_times else None
            ),
            "per_sample_max_seconds": max(per_sample_times) if per_sample_times else None,
        },
        "memory": {
            "measurement": (
                "tracemalloc Python 分配峰值 + psutil 进程 RSS 峰值（逐样本采样）"
                if rss_measured
                else "tracemalloc Python 分配峰值；psutil 不可用，RSS 未测"
            ),
            "tracemalloc_peak_mib": traced_peak / (1024 * 1024),
            "peak_rss_mib": peak_rss if rss_measured else None,
        },
        "limitations": [
            "纯 CPU 离线对拍：无硬件、无 hw_server/JTAG/串口、无 Vivado/xsim。",
            "不声称与 Darknet C 后处理逐值相同（2A D9 已声明奇数补边半像素差异）。",
            "T25 分片按需流式读取，未复制进本工作树，也不进入 Git。",
            "S4-A 契约为 DRAFT_NOT_FROZEN，本工具只对齐其字段名与口径，不产生阶段4 G0 结论。",
        ],
        "not_executed": [
            "板上/实物验证（阶段4 G3 不适用本任务）",
            "RTL 仿真与综合（不在本任务范围）",
            "阶段4 正式 UART 联调（待 S4-B 与实物）",
        ],
    }
    if not rss_measured:
        report["memory"]["peak_rss_mib"] = None
    return report


# --------------------------------------------------------------------------------------
# 篡改反例自检
# --------------------------------------------------------------------------------------


def _check_decoder_head_layout(decoder: DecoderBinding) -> None:
    """核对 D9 侧头配置（栅格/mask/entry）与篡改探针的假设一致。"""

    module = decoder.module
    specs = getattr(module, "HEAD_SPECS", None)
    entry_count = getattr(module, "ENTRY_COUNT", None)
    if specs is None or entry_count != 10:
        raise S4CError("冻结 D9 未暴露预期的 HEAD_SPECS/ENTRY_COUNT，无法可靠构造篡改探针")
    layout = tuple((spec.name, spec.grid_width, spec.anchor_mask) for spec in specs)
    expected = (("13x13", 13, (3, 4, 5)), ("26x26", 26, (1, 2, 3)))
    if layout != expected:
        raise S4CError(f"冻结 D9 头布局与冻结事实不符：{layout}")


def objectness_byte_index_for_source_order(source_order: int, decoder: DecoderBinding) -> dict[str, Any]:
    """把 D9 ``source_order`` 反解为对应头内 objectness 字节下标（用于构造 1 字节篡改）。"""

    _check_decoder_head_layout(decoder)
    ordinal = int(source_order)
    if ordinal < 0:
        raise S4CError("source_order 不能为负")
    pair_index, class_id = divmod(ordinal, 5)
    pairs_head13 = 3 * 13 * 13
    if pair_index < pairs_head13:
        head_name, grid, local_pair = HEAD13_NAME, 13, pair_index
    else:
        head_name, grid, local_pair = HEAD26_NAME, 26, pair_index - pairs_head13
    spatial = grid * grid
    local_anchor = local_pair % 3
    cell = local_pair // 3
    row, col = divmod(cell, grid)
    byte_index = local_anchor * 10 * spatial + 4 * spatial + row * grid + col
    return {
        "head": head_name,
        "pair_index_global": pair_index,
        "class_id": class_id,
        "local_anchor": local_anchor,
        "row": row,
        "col": col,
        "byte_index": byte_index,
        "entry": 4,
        "entry_name": "objectness",
    }


def read_golden_heads(
    *,
    index_sample: Mapping[str, Any],
    t29_sample: Mapping[str, Any],
    tensors_dir: Path,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    """按 T25 索引偏移从分片切出 golden 两头字节（校验 SHA 后返回，不写盘）。"""

    plans = build_head_plans(index_sample, t29_sample)
    shard_path = Path(tensors_dir) / Path(str(index_sample["network"]["compressed_shard"]["path"])).name
    stream = read_shard_stream(shard_path)
    heads: dict[str, bytes] = {}
    for name, plan in plans.items():
        blob = bytes(stream.raw[plan.byte_offset : plan.byte_offset + plan.byte_length])
        blob_sha = sha256_bytes(blob)
        if blob_sha != plan.tensor_sha256:
            raise UpstreamError(
                f"{t29_sample.get('sample_id')} 的 {name} 字节 SHA {blob_sha} 与 T25 索引不符"
            )
        heads[name] = blob
    info = {"shard": str(shard_path), "raw_stream_sha256": stream.raw_sha256}
    del stream
    return heads, info


def compare_head_bytes(golden: bytes, actual: bytes) -> dict[str, Any]:
    """逐值比较两头 INT8 字节，返回首个差异位置与差异统计。"""

    diffs: list[int] = []
    max_delta = 0
    for offset, (expected, observed) in enumerate(zip(golden, actual)):
        if expected != observed:
            diffs.append(offset)
            max_delta = max(max_delta, abs(expected - observed))
    result: dict[str, Any] = {
        "compared_bytes": min(len(golden), len(actual)),
        "length_match": len(golden) == len(actual),
        "identical": not diffs and len(golden) == len(actual),
        "diff_byte_count": len(diffs),
        "first_diff_offset": diffs[0] if diffs else None,
        "expected_byte": golden[diffs[0]] if diffs else None,
        "actual_byte": actual[diffs[0]] if diffs else None,
        "max_abs_int8_delta": max_delta if diffs else 0,
        "diff_offsets_preview": diffs[:16],
    }
    return result


def export_golden_heads(
    *,
    index_sample: Mapping[str, Any],
    t29_sample: Mapping[str, Any],
    tensors_dir: Path,
    out_dir: Path,
) -> dict[str, Any]:
    """把某样本的 golden 两头写成 ``<sid>.head13.bin`` / ``<sid>.head26.bin``（供 --actual 复用）。"""

    sample_id = str(t29_sample["sample_id"])
    heads, info = read_golden_heads(
        index_sample=index_sample, t29_sample=t29_sample, tensors_dir=tensors_dir
    )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Any] = {"sample_id": sample_id, **info}
    for name, blob in heads.items():
        path = out_dir / f"{sample_id}.{name}.bin"
        path.write_bytes(blob)
        written[name] = {"path": str(path), "sha256": sha256_bytes(blob), "bytes": len(blob)}
    return written


def run_tamper_self_test(
    *,
    paths: UpstreamPaths,
    decoder: DecoderBinding,
    index_by_id: Mapping[str, Mapping[str, Any]],
    t29_by_id: Mapping[str, Mapping[str, Any]],
    catalog_by_id: Mapping[str, Mapping[str, Any]],
    sample_id: str | None = None,
    tamper_dir: Path,
    score_threshold: float = FROZEN_SCORE_THRESHOLD,
    tolerance: float = FROZEN_SCORE_ABS_TOLERANCE,
    byte_index: int | None = None,
    run_id: str = "",
) -> tuple[int, dict[str, Any]]:
    """篡改反例自检：对 golden heads 做 1 字节篡改，要求工具 FAIL 且定位到样本/字段。

    退出码：0 = 全部探针均被检出（自检通过）；1 = 存在未被检出的篡改（工具缺陷）；
    2 = 环境错误（由调用方处理）。探针：
      - probe1 ``raw_byte_flip``：翻转 head13 指定字节（默认第 0 字节），
        期望字节 SHA mismatch（离散定位到样本 + head13.tensor_sha256）。
      - probe2 ``objectness_bump``：由 golden 首个检出的 ``source_order`` 反解出
        对应 objectness 字节并置为 +127，期望 score/框数/离散字段 mismatch。
    """

    tamper_dir = Path(tamper_dir)
    tamper_dir.mkdir(parents=True, exist_ok=True)

    if sample_id is None:
        preferred = [sid for sid in ("test_fist_000",) if sid in t29_by_id]
        sample_id = preferred[0] if preferred else sorted(t29_by_id)[0]
    if sample_id not in t29_by_id:
        raise S4CError(f"--tamper-sample 未知：{sample_id}")

    index_sample = index_by_id[sample_id]
    t29_sample = t29_by_id[sample_id]
    catalog_sample = catalog_by_id[sample_id]

    pristine_dir = tamper_dir / "pristine_heads"
    golden_files = export_golden_heads(
        index_sample=index_sample,
        t29_sample=t29_sample,
        tensors_dir=paths.tensors_dir,
        out_dir=pristine_dir,
    )
    plans = build_head_plans(index_sample, t29_sample)
    golden_head13 = (pristine_dir / f"{sample_id}.head13.bin").read_bytes()
    golden_head26 = (pristine_dir / f"{sample_id}.head26.bin").read_bytes()
    probe_reports: list[dict[str, Any]] = []

    def _evaluate_probe(name: str, head13: bytes, head26: bytes, tamper_meta: dict[str, Any]) -> dict[str, Any]:
        probe_dir = tamper_dir / name / "heads"
        probe_dir.mkdir(parents=True, exist_ok=True)
        (probe_dir / f"{sample_id}.head13.bin").write_bytes(head13)
        (probe_dir / f"{sample_id}.head26.bin").write_bytes(head26)
        record = evaluate_actual_sample(
            decoder=decoder,
            t29_sample=t29_sample,
            index_sample=index_sample,
            actual_dir=probe_dir,
            score_threshold=score_threshold,
            tolerance=tolerance,
            golden_heads={HEAD13_NAME: golden_head13, HEAD26_NAME: golden_head26},
            golden_heads_info={"available": True, "source": "self_test_in_memory_golden"},
        )
        localized_fields = sorted({str(item.get("field")) for item in record["mismatches"]})
        detected = record["status"] == "FAIL" and bool(record["mismatches"])
        report = {
            "probe": name,
            "tamper": tamper_meta,
            "sample_id": sample_id,
            "observed_status": record["status"],
            "detected": detected,
            "mismatch_count": record["mismatch_count"],
            "localized_fields": localized_fields,
            "mismatches": record["mismatches"],
            "detection_count_expected": record["detection_count_expected"],
            "detection_count_actual": record["detection_count_actual"],
            "max_score_abs_error": record["max_score_abs_error"],
            "max_xyxy_abs_error": record["max_xyxy_abs_error"],
            "actual_heads_dir": str(probe_dir),
        }
        write_json(tamper_dir / name / "compare_report.json", record)
        return report

    # probe1: 单字节翻转
    flip_index = 0 if byte_index is None else int(byte_index)
    if not (0 <= flip_index < len(golden_head13)):
        raise S4CError(f"--tamper-byte-index 越界：{flip_index}")
    tampered_head13 = bytearray(golden_head13)
    before = tampered_head13[flip_index]
    tampered_head13[flip_index] = before ^ 0x01
    probe_reports.append(
        _evaluate_probe(
            "probe1_raw_byte_flip",
            bytes(tampered_head13),
            golden_head26,
            {
                "kind": "raw_byte_flip",
                "head": HEAD13_NAME,
                "byte_index": flip_index,
                "original_byte": before,
                "tampered_byte": tampered_head13[flip_index],
                "xor_mask": 1,
                "original_sha256": sha256_bytes(golden_head13),
                "tampered_sha256": sha256_bytes(tampered_head13),
                "expected_tensor_sha256": plans[HEAD13_NAME].tensor_sha256,
            },
        )
    )

    # probe2: 由 source_order 反解 objectness 字节并置为 +127
    golden_expected = [
        {
            "class_id": int(item["class_id"]),
            "class_name": str(item["class_name"]),
            "score": float(item["score"]),
            "xyxy": [float(v) for v in item["xyxy"]],
            "source_order": int(item["source_order"]),
        }
        for item in t29_sample.get("detections", [])
    ]
    target = min(golden_expected, key=lambda item: item["source_order"]) if golden_expected else None
    if target is None:
        probe_reports.append(
            {
                "probe": "probe2_objectness_bump",
                "sample_id": sample_id,
                "detected": True,
                "skipped": True,
                "reason": "该样本 golden 零框，无法由检出反解 objectness 字节；probe1 已覆盖字节层面定位",
            }
        )
    else:
        target_info = objectness_byte_index_for_source_order(target["source_order"], decoder)
        head_name = target_info["head"]
        source_bytes = bytearray(golden_head13 if head_name == HEAD13_NAME else golden_head26)
        index_in_head = int(target_info["byte_index"])
        if not (0 <= index_in_head < len(source_bytes)):
            raise S4CError("反解出的 objectness 字节下标越界")
        before = source_bytes[index_in_head]
        source_bytes[index_in_head] = 127
        head13_bytes = bytes(source_bytes) if head_name == HEAD13_NAME else golden_head13
        head26_bytes = bytes(source_bytes) if head_name == HEAD26_NAME else golden_head26
        expected_sha_name = plans[head_name].tensor_sha256
        probe_reports.append(
            _evaluate_probe(
                "probe2_objectness_bump",
                head13_bytes,
                head26_bytes,
                {
                    "kind": "objectness_bump",
                    "head": head_name,
                    "byte_index": index_in_head,
                    "original_byte": before,
                    "tampered_byte": 127,
                    "target_source_order": target["source_order"],
                    "target_class_id": target["class_id"],
                    "target_score": target["score"],
                    "decoded_pair": target_info,
                    "original_sha256": sha256_bytes(
                        golden_head13 if head_name == HEAD13_NAME else golden_head26
                    ),
                    "tampered_sha256": sha256_bytes(source_bytes),
                    "expected_tensor_sha256": expected_sha_name,
                },
            )
        )

    all_detected = all(item.get("detected") for item in probe_reports)
    evidence = {
        "schema_version": "gestureforge_s4c_tamper_self_test_v1",
        "task_id": TASK_ID,
        "run_id": run_id,
        "generated_utc8": now_utc8(),
        "sample_id": sample_id,
        "score_threshold": float(score_threshold),
        "tolerance": float(tolerance),
        "golden_head_files": golden_files,
        "probes": probe_reports,
        "all_tamper_probes_detected": all_detected,
        "exit_code": 0 if all_detected else 1,
        "exit_code_semantics": "0=篡改均被检出（自检通过）；1=存在未被检出的篡改（工具缺陷）",
        "note": "本自检证明对拍工具不是恒过：1 字节篡改必须使该样本 FAIL 并定位到字段。",
    }
    return (0 if all_detected else 1), evidence


# --------------------------------------------------------------------------------------
# 模型清单头部交叉核对（可选，独立进程运行以免抬高主对拍峰值内存）
# --------------------------------------------------------------------------------------


def check_manifest_heads(manifest_path: Path) -> dict[str, Any]:
    """载入 T01 manifest 并交叉核对两头 scale/长度/地址（独立于 T25/T29）。"""

    manifest = load_json(manifest_path)
    heads = manifest.get("address_map", {}).get("heads", [])
    yolo_layers = {
        int(layer["layer_index"]): layer for layer in manifest.get("layers", []) if layer.get("op") == "yolo"
    }
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    for head in heads:
        name = str(head.get("name"))
        if name not in FROZEN_HEAD_BYTE_LENGTHS:
            continue
        expected_length = FROZEN_HEAD_BYTE_LENGTHS[name]
        expected_scale = (
            0.24267549589862975 if name == HEAD13_NAME else 0.30223452951025775
        )
        entry: dict[str, Any] = {
            "name": name,
            "manifest_int8_scale": head.get("int8_scale"),
            "manifest_length_bytes": head.get("length_bytes"),
            "manifest_address": head.get("address"),
            "yolo_layer_index": head.get("yolo_layer_index"),
            "source_convolution_layer_index": head.get("source_convolution_layer_index"),
            "shape_nchw": head.get("shape_nchw"),
        }
        layer = yolo_layers.get(int(head.get("yolo_layer_index", -1)))
        if layer:
            entry["layer_output_scale"] = layer.get("output_scale")
            entry["layer_tensor_length_bytes"] = layer.get("tensor_length_bytes")
            entry["layer_tensor_address"] = layer.get("tensor_address")
        ok = (
            float(head.get("int8_scale")) == expected_scale
            and int(head.get("length_bytes")) == expected_length
        )
        if layer:
            ok = ok and float(layer.get("output_scale")) == expected_scale
            ok = ok and int(layer.get("tensor_length_bytes")) == expected_length
        entry["status"] = "MATCH" if ok else "MISMATCH"
        if not ok:
            failures.append(f"manifest 头 {name} 与冻结常量不一致")
        records.append(entry)
    if len(records) != 2:
        failures.append(f"manifest address_map.heads 未给出两头：{len(records)} 项")
    return {
        "schema_version": "gestureforge_s4c_manifest_head_crosscheck_v1",
        "task_id": TASK_ID,
        "generated_utc8": now_utc8(),
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "manifest_status": manifest.get("status"),
        "heads": records,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
        "note": "仅交叉核对冻结常量；换算/解码口径仍以 T29 head_tensors 与 T25 索引为准。",
    }


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _parse_args(argv: Sequence[str] | None) -> argparse.ArgumentParser.parse_args:
    """构造并解析 CLI 参数。"""

    parser = argparse.ArgumentParser(
        description="S4-C 整数推理结果 vs 2A 冻结 CPU golden 离线对拍工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "退出码：0=全部 PASS；1=存在 mismatch（或 --self-test-tamper 未检出篡改）；"
            "2=环境/输入错误。--actual 目录格式见本文件模块文档字符串。"
        ),
    )
    parser.add_argument("--json-out", default="", help="机器可读报告输出路径（'-' 表示 stdout）")
    parser.add_argument("--run-id", default="", help="证据 RunId（写入报告）")
    parser.add_argument("--actual", default="", help="实测 heads 目录（与同一 T29 golden 对拍）")
    parser.add_argument("--limit", type=int, default=None, help="随机子集样本数（默认全量 109）")
    parser.add_argument("--seed", type=int, default=None, help="随机子集种子（默认 20260922 并记录）")
    parser.add_argument(
        "--sample-id",
        action="append",
        default=None,
        help="显式指定样本号（可重复/逗号分隔）；与 --limit 互斥优先",
    )
    parser.add_argument("--t25-index", default="", help="T25 索引路径（默认取 S4-A 契约绑定）")
    parser.add_argument("--t29-ref", default="", help="T29 参考路径（默认取 S4-A 契约绑定）")
    parser.add_argument("--catalog", default="", help="T01 样本清单路径（默认取 S4-A 契约绑定）")
    parser.add_argument("--manifest", default="", help="T01 模型清单路径（默认取 S4-A 契约绑定）")
    parser.add_argument("--tensors-dir", default="", help="T25 分片目录（默认取 S4-A 契约绑定）")
    parser.add_argument("--decoder-dir", default="", help="冻结 D9/D6 所在目录（默认本工作树 verification/）")
    parser.add_argument("--contract", default="", help="S4-A 契约路径（默认 docs/stage4/s4a_stage4_g0_fields.json）")
    parser.add_argument("--score-threshold", type=float, default=FROZEN_SCORE_THRESHOLD, help="分数阈值（D9 限定 [0.25,0.50]）")
    parser.add_argument("--tol", type=float, default=FROZEN_SCORE_ABS_TOLERANCE, help="score/xyxy 绝对容限（默认 1e-6）")
    parser.add_argument("--no-verify-upstream-sha", action="store_true", help="仅记录上游 SHA 不一致，不阻断")
    parser.add_argument(
        "--no-golden-bytes",
        action="store_true",
        help="--actual 模式下不读取 T25 golden 字节（仅 SHA 比对；用于无 372 MB 分片的联调机）",
    )
    parser.add_argument("--self-test-tamper", action="store_true", help="运行 1 字节篡改反例自检")
    parser.add_argument("--tamper-dir", default="", help="篡改自检工作目录（默认 tmp/4/S4C/<run_id>/tamper_self_test）")
    parser.add_argument("--tamper-sample", default="", help="篡改自检使用的样本号（默认 test_fist_000）")
    parser.add_argument("--tamper-byte-index", type=int, default=0, help="probe1 翻转的 head13 字节下标（默认 0）")
    parser.add_argument("--check-manifest-heads", action="store_true", help="只做 manifest 头部常量交叉核对后退出")
    parser.add_argument("--quiet", action="store_true", help="减少 stdout 输出")
    return parser.parse_args(argv)


def _emit(report: Mapping[str, Any], json_out: str) -> None:
    """按 --json-out 写出报告。"""

    if not json_out:
        return
    if json_out == "-":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        write_json(Path(json_out), report)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 入口，返回进程退出码。"""

    args = _parse_args(argv)
    run_id = args.run_id or ""
    try:
        paths = resolve_upstream_paths(
            contract_path=Path(args.contract) if args.contract else None,
            t25_index=args.t25_index or None,
            t29_ref=args.t29_ref or None,
            catalog=args.catalog or None,
            manifest=args.manifest or None,
            tensors_dir=args.tensors_dir or None,
            decoder_dir=args.decoder_dir or None,
        )
    except (S4CError, OSError) as exc:
        print(f"[FAIL] 上游路径解析失败：{exc}")
        return 2

    if args.check_manifest_heads:
        try:
            report = check_manifest_heads(paths.manifest)
        except (S4CError, OSError, ValueError) as exc:
            print(f"[FAIL] manifest 交叉核对失败：{exc}")
            return 2
        _emit(report, args.json_out)
        print(f"[{report['status']}] manifest 头部交叉核对：{len(report['failures'])} 项失败")
        for failure in report["failures"]:
            print(f"[FAIL] {failure}")
        return 0 if report["status"] == "PASS" else 1

    upstream_records, upstream_failures = verify_upstream_files(
        paths, verify_sha=not args.no_verify_upstream_sha
    )
    if upstream_failures:
        for failure in upstream_failures:
            print(f"[FAIL] {failure}")
        print("[FAIL] 上游校验不通过，退出码 2（不伪造通过）")
        return 2

    if not (0.25 <= float(args.score_threshold) <= 0.50):
        print("[FAIL] --score-threshold 必须在闭区间 [0.25, 0.50]（D9 API 限制）")
        return 2

    contract, _ = load_s4a_contract(Path(args.contract) if args.contract else None)

    try:
        decoder = load_frozen_decoder(paths.decoder_dir)
    except (S4CError, ImportError, OSError) as exc:
        print(f"[FAIL] 冻结 D9 解码器加载失败：{exc}")
        return 2

    try:
        index, reference, catalog = load_upstream_dataset(paths)
    except (S4CError, OSError, ValueError, KeyError) as exc:
        print(f"[FAIL] 上游数据载入失败：{exc}")
        return 2

    index_by_id = index_samples_by_id(index)
    t29_by_id = {str(item["sample_id"]): item for item in reference["samples"]}
    catalog_by_id = {str(item["sample_id"]): item for item in catalog["samples"]}

    all_ids = [str(item["sample_id"]) for item in index["samples"]]

    if args.self_test_tamper:
        tamper_dir = Path(args.tamper_dir) if args.tamper_dir else (
            WORKTREE / "tmp" / "4" / "S4C" / (run_id or "adhoc") / "tamper_self_test"
        )
        try:
            exit_code, evidence = run_tamper_self_test(
                paths=paths,
                decoder=decoder,
                index_by_id=index_by_id,
                t29_by_id=t29_by_id,
                catalog_by_id=catalog_by_id,
                sample_id=args.tamper_sample or None,
                tamper_dir=tamper_dir,
                score_threshold=float(args.score_threshold),
                tolerance=float(args.tol),
                byte_index=args.tamper_byte_index,
                run_id=run_id,
            )
        except (S4CError, UpstreamError, ActualInputError, OSError, ValueError) as exc:
            print(f"[FAIL] 篡改自检环境错误：{exc}")
            return 2
        evidence["upstream_bindings"] = upstream_records
        evidence["tamper_dir"] = str(tamper_dir)
        _emit(evidence, args.json_out)
        for probe in evidence["probes"]:
            state = "DETECTED" if probe.get("detected") else "NOT_DETECTED"
            print(
                f"[{'PASS' if probe.get('detected') else 'FAIL'}] {probe['probe']} -> {state}"
                f"（sample={evidence['sample_id']}，mismatch={probe.get('mismatch_count')}，"
                f"fields={probe.get('localized_fields')}）"
            )
        print(
            f"[{'PASS' if exit_code == 0 else 'FAIL'}] 篡改自检："
            f"全部探针检出={evidence['all_tamper_probes_detected']}，exit={exit_code}"
        )
        return exit_code

    explicit: list[str] = []
    if args.sample_id:
        for item in args.sample_id:
            explicit.extend([token.strip() for token in str(item).split(",") if token.strip()])
    try:
        selected, selection = select_sample_ids(
            all_ids, limit=args.limit, seed=args.seed, explicit=explicit or None
        )
    except S4CError as exc:
        print(f"[FAIL] 样本选择失败：{exc}")
        return 2

    mode = "actual" if args.actual else "golden"
    if mode == "golden" and not paths.tensors_dir.is_dir():
        print(f"[FAIL] T25 分片目录不可用：{paths.tensors_dir}（可用 --limit 说明受限，但不得伪造通过）")
        return 2

    try:
        report = run_compare(
            paths=paths,
            decoder=decoder,
            index_by_id=index_by_id,
            t29_by_id=t29_by_id,
            catalog_by_id=catalog_by_id,
            selection=selection,
            mode=mode,
            actual_dir=Path(args.actual) if args.actual else None,
            score_threshold=float(args.score_threshold),
            tolerance=float(args.tol),
            run_id=run_id,
            contract=contract,
            upstream_records=upstream_records,
            use_golden_bytes=not args.no_golden_bytes,
        )
    except (S4CError, UpstreamError, ActualInputError, OSError, ValueError, KeyError) as exc:
        print(f"[FAIL] 对拍执行失败：{exc}")
        return 2

    report["upstream_paths"] = paths.as_json()
    report["selection"] = selection
    _emit(report, args.json_out)

    summary = report["summary"]
    if not args.quiet:
        print(
            f"[{report['status']}] mode={mode} 样本 {summary['samples_selected']}："
            f"PASS={summary['samples_passed']} FAIL={summary['samples_failed']}，"
            f"mismatch 总数={summary['mismatch_total']}，"
            f"字节 mismatch 样本={summary['byte_mismatch_count']}，"
            f"框 mismatch 样本={summary['frame_mismatch_count']}"
        )
        print(
            f"[INFO] 最大 score 绝对误差={summary['max_score_abs_error']}，"
            f"最大 xyxy 分量绝对误差={summary['max_xyxy_abs_error']}，"
            f"框数期望/实际={summary['total_detections_expected']}/{summary['total_detections_actual']}"
        )
        print(
            f"[INFO] 耗时={report['timing']['total_seconds']:.2f}s，"
            f"tracemalloc 峰值={report['memory']['tracemalloc_peak_mib']:.1f} MiB，"
            f"RSS 峰值={report['memory']['peak_rss_mib']}"
        )
        if summary["failed_sample_ids"]:
            printed = 0
            for item in report["samples"]:
                if item["status"] != "FAIL":
                    continue
                for mismatch in item["mismatches"][:3]:
                    print(
                        f"[MISMATCH] sample={item['sample_id']} index={mismatch.get('index')} "
                        f"field={mismatch.get('field')} expected={mismatch.get('expected')} "
                        f"actual={mismatch.get('actual')} kind={mismatch.get('kind')} "
                        f"abs_error={mismatch.get('abs_error')}"
                    )
                    printed += 1
                if item["mismatch_count"] > 3:
                    print(
                        f"[MISMATCH] sample={item['sample_id']} 其余 "
                        f"{item['mismatch_count'] - 3} 条见机器可读报告"
                    )
                if printed >= 20:
                    print("[MISMATCH] 仅打印全部失败样本的前 20 条，完整明细见 --json-out 报告")
                    break
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())