#!/usr/bin/env python3
"""为 S2A-T68 生成并校验单个固定样本的全网输入与逐层 golden 夹具。"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
import zlib
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
T01_MANIFEST = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T01_SAMPLES = ROOT / "report/evidence/S2A-T01/fixed_test_samples.json"
T25_INDEX = ROOT / "report/evidence/S2A-T25/cpu_layer_golden_index.json"
T25_SHARDS = ROOT / "report/evidence/S2A-T25/tensors"
T65_SAMPLE0_INPUT = ROOT / "report/evidence/S2A-T65/run02/fixture/sample0_input_chw_int8.bin"
DESCRIPTOR_PACKAGE = ROOT / "src/s2a_network_descriptor_pkg.sv"
DEFAULT_DATASET_ROOT = Path(r"D:\FPGA_Data\HaGRIDv2")
DEFAULT_OUTPUT_ROOT = ROOT / "report/evidence/S2A-T68/run01"

PINNED_HASHES = {
    "t01_manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "t01_samples": "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed",
    "t25_index": "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d",
    "descriptor_package": "295df973188878388ff8ef48c50dfacb1fe3d23a169369d737d1babe0507dc14",
    "numeric_reference": "ea48281fa1c1ba14006f6131ff377c7e4523da8c7e4977b0949d454a7c9ded90",
    "model_delivery": "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8",
}
EXPECTED_LAYER_COUNT = 38
EXPECTED_SAMPLE_COUNT = 109


def sha256_bytes(data: bytes) -> str:
    """计算字节串的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """以流式方式计算文件的 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    """条件不成立时以明确原因停止。"""
    if not condition:
        raise ValueError(message)


def read_json(path: Path, expected_hash: str | None = None) -> dict[str, Any]:
    """读取 UTF-8 JSON，并在需要时核验冻结摘要。"""
    require(path.is_file(), f"缺少输入文件：{path}")
    raw = path.read_bytes()
    if expected_hash is not None:
        require(sha256_bytes(raw) == expected_hash, f"SHA-256 不匹配：{path}")
    value = json.loads(raw.decode("utf-8"))
    require(isinstance(value, dict), f"JSON 顶层必须为对象：{path}")
    return value


def parse_descriptor_array(source: str, name: str, width: int) -> list[int]:
    """从冻结 SV 包中读取一个定长十六进制数组。"""
    pattern = re.compile(
        rf"localparam\s+logic\s+\[[^]]+\]\s+{re.escape(name)}\s*\[[^]]+\]\s*=\s*'\{{(.*?)\}};",
        re.DOTALL,
    )
    match = pattern.search(source)
    require(match is not None, f"descriptor ROM 缺少数组：{name}")
    values = [int(value, 16) for value in re.findall(rf"{width}'h([0-9a-fA-F_]+)", match.group(1))]
    require(len(values) == EXPECTED_LAYER_COUNT, f"descriptor ROM 数组长度错误：{name}={len(values)}")
    return values


def descriptor_rows(manifest: dict[str, Any], t25_sample: dict[str, Any]) -> list[dict[str, Any]]:
    """交叉核对模型 manifest、descriptor ROM 与 T25 输出清单。"""
    package_text = DESCRIPTOR_PACKAGE.read_text(encoding="utf-8")
    addresses = parse_descriptor_array(package_text, "S2A_OUTPUT_ADDRESS", 32)
    lengths = parse_descriptor_array(package_text, "S2A_OUTPUT_LENGTH_BYTES", 32)
    write_required = parse_descriptor_array(package_text, "S2A_OUTPUT_MEMORY_WRITE_REQUIRED", 1)
    aliases = parse_descriptor_array(package_text, "S2A_OUTPUT_ALIAS_LAYER_INDEX", 6)
    model_layers = manifest.get("layers")
    tensor_rows = t25_sample.get("network", {}).get("tensors")
    require(isinstance(model_layers, list) and len(model_layers) == EXPECTED_LAYER_COUNT, "模型 manifest 层数不是 38")
    require(isinstance(tensor_rows, list) and len(tensor_rows) == EXPECTED_LAYER_COUNT, "T25 tensor 清单层数不是 38")

    rows: list[dict[str, Any]] = []
    golden_offset = 0
    for layer_index, (layer, tensor) in enumerate(zip(model_layers, tensor_rows, strict=True)):
        require(layer.get("layer_index") == layer_index == tensor.get("layer_index"), f"层索引绑定不一致：{layer_index}")
        require(layer.get("tensor_address") == addresses[layer_index], f"层 {layer_index} descriptor 地址不匹配")
        require(layer.get("tensor_length_bytes") == lengths[layer_index], f"层 {layer_index} descriptor 长度不匹配")
        require(tensor.get("byte_length") == lengths[layer_index], f"层 {layer_index} T25 长度不匹配")
        is_stored = bool(tensor.get("stored"))
        require(bool(write_required[layer_index]) == is_stored, f"层 {layer_index} 写分配与 T25 stored 标志不匹配")
        alias_index = tensor.get("alias_of_layer_index")
        expected_alias = None if write_required[layer_index] else aliases[layer_index]
        if expected_alias is not None:
            require(alias_index == expected_alias, f"层 {layer_index} alias 目标不匹配")
            require(addresses[layer_index] == addresses[expected_alias], f"层 {layer_index} alias 地址不匹配")
            require(lengths[layer_index] == lengths[expected_alias], f"层 {layer_index} alias 长度不匹配")
        else:
            require(alias_index is None, f"层 {layer_index} 不应是 alias")
        row = {
            "layer_index": layer_index,
            "op": tensor.get("op"),
            "address": addresses[layer_index],
            "byte_length": lengths[layer_index],
            "stored": is_stored,
            "alias_of_layer_index": alias_index,
            "t25_byte_offset": tensor.get("byte_offset"),
            "t25_sha256": tensor.get("tensor_sha256"),
            "golden_stream_offset": golden_offset if is_stored else None,
        }
        if is_stored:
            golden_offset += lengths[layer_index]
        rows.append(row)
    require(golden_offset == t25_sample["network"]["unique_output_raw_bytes"], "T25 unique output byte count 不一致")
    require(golden_offset == 11_382_150, "冻结模型的 T25 unique output byte count 不是预期值")
    return rows


def sample_input_bytes(
    sample_index: int,
    sample: dict[str, Any],
    t25_sample: dict[str, Any],
    fixed_samples_doc: dict[str, Any],
    dataset_root: Path,
) -> tuple[bytes, dict[str, Any]]:
    """读取或重建一个样本的完整 CHW INT8 输入，并校验 T01 哈希。"""
    expected_hash = sample.get("pl_input_sha256")
    t25_input = t25_sample.get("preprocessed_input", {})
    require(expected_hash == t25_input.get("sha256"), f"sample{sample_index} 的 T01/T25 输入 SHA 不同")
    require(t25_input.get("raw_bytes") == 519_168, f"sample{sample_index} 输入长度不是 519168")

    if sample_index == 0:
        require(T65_SAMPLE0_INPUT.is_file(), f"缺少 T65 sample0 输入夹具：{T65_SAMPLE0_INPUT}")
        raw = T65_SAMPLE0_INPUT.read_bytes()
        origin = {
            "kind": "frozen_t65_sample0_fixture",
            "path": str(T65_SAMPLE0_INPUT),
            "sha256": sha256_bytes(raw),
        }
    else:
        sys.path.insert(0, str(ROOT))
        delivery = importlib.import_module("verification.s2a_model_delivery")
        numeric = importlib.import_module("verification.s1_t02_d2_numeric_reference")
        try:
            import numpy as np
        except ImportError as error:
            raise RuntimeError("生成非零样本输入需要仓库指定的 NumPy runtime") from error

        source = t25_sample.get("original_input", {})
        if sample.get("source") == "synthetic_rgb416":
            seed = fixed_samples_doc.get("seed")
            require(isinstance(seed, int), "固定样本清单缺少 synthetic seed")
            sample_id = sample.get("sample_id")
            synthetic_by_id = {row.get("sample_id"): row for row in delivery.synthetic_cases(seed)}
            require(sample_id in synthetic_by_id, f"未找到 synthetic 样本生成描述：{sample_id}")
            height = int(sample["height"])
            width = int(sample["width"])
            if sample_id == "synthetic_black":
                rgb = np.zeros((height, width, 3), dtype=np.uint8)
            elif sample_id == "synthetic_white":
                rgb = np.full((height, width, 3), 255, dtype=np.uint8)
            elif sample_id == "synthetic_checkerboard":
                y, x = np.indices((height, width))
                checker = np.where((x + y) & 1, 255, 0).astype(np.uint8)
                rgb = np.repeat(checker[:, :, None], 3, axis=2)
            elif sample_id == "synthetic_xorshift32":
                random_bytes = delivery.xorshift32(seed, width * height * 3)
                rgb = np.fromiter(random_bytes, dtype=np.uint8, count=width * height * 3).reshape(height, width, 3)
            else:
                raise ValueError(f"未知 synthetic sample id：{sample_id}")
            origin = {"kind": "synthetic_rgb", "sample_id": sample_id}
            expected_rgb_sha = sample.get("rgb_sha256")
        else:
            relative_image = sample.get("relative_image")
            require(isinstance(relative_image, str), f"sample{sample_index} 缺少相对图像路径")
            image_path = dataset_root.joinpath(*PurePosixPath(relative_image).parts)
            require(image_path.is_file(), f"sample{sample_index} 原图不存在：{image_path}")
            raw_image = image_path.read_bytes()
            actual_image_hash = sha256_bytes(raw_image)
            expected_rgb_sha = sample.get("image_sha256")
            require(actual_image_hash == expected_rgb_sha == source.get("sha256"), f"sample{sample_index} 原图 SHA 不匹配")
            rgb = delivery.decode_rgb(image_path)
            require(list(rgb.shape) == [sample["height"], sample["width"], 3], f"sample{sample_index} 解码后尺寸不匹配")
            origin = {
                "kind": "fixed_sample_image",
                "path": str(image_path),
                "sha256": actual_image_hash,
            }
        if sample.get("source") == "synthetic_rgb416":
            rgb_bytes = np.ascontiguousarray(rgb).tobytes(order="C")
            require(sha256_bytes(rgb_bytes) == expected_rgb_sha == source.get("sha256"), f"sample{sample_index} synthetic RGB SHA 不匹配")
            origin["rgb_sha256"] = sha256_bytes(rgb_bytes)
        require(rgb.dtype == np.uint8, f"sample{sample_index} RGB dtype 不是 uint8")
        tensor = np.asarray(numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), 416, 416), dtype=np.int8)
        require(list(tensor.shape) == [3, 416, 416], f"sample{sample_index} 预处理 shape 不匹配")
        raw = np.ascontiguousarray(tensor).tobytes(order="C")

    actual_hash = sha256_bytes(raw)
    require(len(raw) == 519_168, f"sample{sample_index} 输入字节数不匹配：{len(raw)}")
    require(actual_hash == expected_hash, f"sample{sample_index} 输入 SHA 不匹配：{actual_hash}")
    origin.update({"bytes": len(raw), "sha256": actual_hash, "layout": "CHW int8 two's complement"})
    return raw, origin


def write_new_or_verify(path: Path, data: bytes, expected_hash: str) -> None:
    """新建文件；已存在时只接受完全相同的字节。"""
    if path.exists():
        require(path.is_file(), f"输出目标不是普通文件：{path}")
        require(path.stat().st_size == len(data), f"拒绝覆盖不同长度的已有文件：{path}")
        require(sha256_file(path) == expected_hash, f"拒绝覆盖不同内容的已有文件：{path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(data)
    require(path.stat().st_size == len(data) and sha256_file(path) == expected_hash, f"写入后校验失败：{path}")


def prepare_sample(sample_index: int, output_root: Path, dataset_root: Path) -> dict[str, Any]:
    """验证冻结来源并为单个样本生成输入、GF8 权重和唯一 tensor stream。"""
    manifest = read_json(T01_MANIFEST, PINNED_HASHES["t01_manifest"])
    fixed_samples_doc = read_json(T01_SAMPLES, PINNED_HASHES["t01_samples"])
    t25_index = read_json(T25_INDEX, PINNED_HASHES["t25_index"])
    package_raw = DESCRIPTOR_PACKAGE.read_bytes()
    require(sha256_bytes(package_raw) == PINNED_HASHES["descriptor_package"], "descriptor package SHA 不匹配")
    numeric_path = ROOT / "verification/s1_t02_d2_numeric_reference.py"
    delivery_path = ROOT / "verification/s2a_model_delivery.py"
    for key, path in (("numeric_reference", numeric_path), ("model_delivery", delivery_path)):
        require(path.is_file() and sha256_file(path) == PINNED_HASHES[key], f"绑定源码 SHA 不匹配：{path}")

    samples = fixed_samples_doc.get("samples")
    golden_samples = t25_index.get("samples")
    require(fixed_samples_doc.get("sample_count") == EXPECTED_SAMPLE_COUNT, "T01 固定样本数不是 109")
    require(isinstance(samples, list) and len(samples) == EXPECTED_SAMPLE_COUNT, "T01 固定样本数组长度不是 109")
    require(isinstance(golden_samples, list) and len(golden_samples) == EXPECTED_SAMPLE_COUNT, "T25 样本数组长度不是 109")
    require(0 <= sample_index < EXPECTED_SAMPLE_COUNT, "sample index 必须在 0..108")
    sample = samples[sample_index]
    t25_sample = golden_samples[sample_index]
    require(sample.get("sample_id") == t25_sample.get("sample_id"), f"sample{sample_index} 的 T01/T25 ID 不匹配")
    require(sample.get("frame_id") == t25_sample.get("frame_id"), f"sample{sample_index} 的 T01/T25 frame 不匹配")
    layers = descriptor_rows(manifest, t25_sample)

    package_binding = manifest.get("bindings", {}).get("gf8_package", {})
    gf8_path = Path(package_binding.get("path", ""))
    require(gf8_path.is_file(), f"GF8 package 不存在：{gf8_path}")
    gf8_raw = gf8_path.read_bytes()
    gf8_hash = sha256_bytes(gf8_raw)
    require(len(gf8_raw) == package_binding.get("bytes") == 5_903_100, "GF8 package 字节数不匹配")
    require(gf8_hash == package_binding.get("sha256"), "GF8 package SHA 与 T01 manifest 不匹配")

    shard = t25_sample.get("network", {}).get("compressed_shard", {})
    shard_path = ROOT.joinpath(*PurePosixPath(shard.get("path", "")).parts)
    require(shard_path.is_file(), f"T25 shard 不存在：{shard_path}")
    shard_raw = shard_path.read_bytes()
    shard_hash = sha256_bytes(shard_raw)
    require(shard_hash == shard.get("sha256"), f"sample{sample_index} T25 shard SHA 不匹配")
    require(len(shard_raw) == shard.get("compressed_bytes"), f"sample{sample_index} T25 shard 长度不匹配")
    raw_stream = zlib.decompress(shard_raw)
    network = t25_sample["network"]
    require(len(raw_stream) == network.get("unique_output_raw_bytes"), f"sample{sample_index} T25 解压长度不匹配")
    require(sha256_bytes(raw_stream) == network.get("raw_stream_sha256"), f"sample{sample_index} T25 解压 SHA 不匹配")

    golden_parts: list[bytes] = []
    cursor = 0
    for row, tensor in zip(layers, network["tensors"], strict=True):
        if not row["stored"]:
            continue
        offset = tensor.get("byte_offset")
        length = tensor.get("byte_length")
        require(offset == cursor, f"sample{sample_index} layer{row['layer_index']} T25 offset 不连续")
        tensor_raw = raw_stream[offset : offset + length]
        require(len(tensor_raw) == length, f"sample{sample_index} layer{row['layer_index']} golden 被截断")
        require(sha256_bytes(tensor_raw) == tensor.get("tensor_sha256"), f"sample{sample_index} layer{row['layer_index']} tensor SHA 不匹配")
        golden_parts.append(tensor_raw)
        cursor += length
    require(cursor == len(raw_stream), f"sample{sample_index} T25 stream 尾部未被存储 tensor 覆盖")
    golden_stream = b"".join(golden_parts)
    require(sha256_bytes(golden_stream) == network.get("raw_stream_sha256"), "拼接后的 unique golden stream SHA 不匹配")

    input_raw, input_origin = sample_input_bytes(sample_index, sample, t25_sample, fixed_samples_doc, dataset_root)
    output_root = output_root.absolute()
    require(not output_root.exists() or output_root.is_dir(), f"输出根路径类型错误：{output_root}")
    sample_dir = output_root / "fixtures" / f"sample_{sample_index:03d}"
    fixture_file_dir = sample_dir / "golden_unique.bin"
    common_weight_path = output_root / "fixtures" / "common" / "weights.gf8"
    input_path = sample_dir / "input_chw_int8.bin"
    write_new_or_verify(common_weight_path, gf8_raw, gf8_hash)
    write_new_or_verify(input_path, input_raw, sha256_bytes(input_raw))
    write_new_or_verify(fixture_file_dir, golden_stream, sha256_bytes(golden_stream))

    t25_tensor_rows = [
        {
            "layer_index": row["layer_index"],
            "address": row["address"],
            "byte_length": row["byte_length"],
            "stored": row["stored"],
            "alias_of_layer_index": row["alias_of_layer_index"],
            "t25_byte_offset": row["t25_byte_offset"],
            "t25_sha256": row["t25_sha256"],
            "golden_stream_offset": row["golden_stream_offset"],
        }
        for row in layers
    ]
    payload = {
        "schema_version": "gestureforge_s2a_t68_sample_fixture_v1",
        "task_id": "S2A-T68",
        "sample_index": sample_index,
        "sample_id": sample["sample_id"],
        "frame_id": sample["frame_id"],
        "input": {
            "path": input_path.relative_to(output_root).as_posix(),
            "bytes": len(input_raw),
            "sha256": sha256_bytes(input_raw),
            "source": input_origin,
        },
        "weight_package": {
            "path": common_weight_path.relative_to(output_root).as_posix(),
            "bytes": len(gf8_raw),
            "sha256": gf8_hash,
        },
        "golden_unique_stream": {
            "path": fixture_file_dir.relative_to(output_root).as_posix(),
            "bytes": len(golden_stream),
            "sha256": sha256_bytes(golden_stream),
            "comparison_scope": "36 stored output tensors; 2 YOLO rows are aliases and have no separate write range",
        },
        "layers": t25_tensor_rows,
        "bindings": {
            "t01_manifest": {"path": T01_MANIFEST.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["t01_manifest"]},
            "t01_fixed_samples": {"path": T01_SAMPLES.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["t01_samples"]},
            "t25_index": {"path": T25_INDEX.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["t25_index"]},
            "t25_compressed_shard": {"path": shard_path.relative_to(ROOT).as_posix(), "bytes": len(shard_raw), "sha256": shard_hash},
            "t25_raw_stream": {"bytes": len(raw_stream), "sha256": sha256_bytes(raw_stream)},
            "gf8_package": {"path": str(gf8_path), "bytes": len(gf8_raw), "sha256": gf8_hash},
            "descriptor_package": {"path": DESCRIPTOR_PACKAGE.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["descriptor_package"]},
            "numeric_reference": {"path": numeric_path.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["numeric_reference"]},
            "model_delivery": {"path": delivery_path.relative_to(ROOT).as_posix(), "sha256": PINNED_HASHES["model_delivery"]},
        },
        "limitations": [
            "夹具准备结果不是 RTL 仿真结果。",
            "runner 仅在显式传入已冻结 backend SHA 后编译，且只有显式 RunSimulation 开关才运行仿真。",
            "T25 CPU golden 是独立逐字节 oracle；本夹具不执行检测头解码或 NMS。",
        ],
    }
    manifest_path = sample_dir / "fixture_manifest.json"
    manifest_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_new_or_verify(manifest_path, manifest_bytes, sha256_bytes(manifest_bytes))
    return payload


def main() -> int:
    """解析命令行并生成一个样本夹具。"""
    parser = argparse.ArgumentParser(description="准备并校验 S2A-T68 单样本全网 golden 夹具")
    parser.add_argument("--sample-index", type=int, default=0, help="T01 固定样本索引 0..108")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="T68 run evidence 根目录")
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT, help="固定样本原图数据集根目录")
    args = parser.parse_args()
    try:
        result = prepare_sample(args.sample_index, args.output_root, args.dataset_root)
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, zlib.error) as error:
        print(f"T68 夹具准备失败：{error}", file=sys.stderr)
        return 2
    print(
        f"T68 夹具就绪：sample={result['sample_index']} id={result['sample_id']} "
        f"layers=38 stored=36 aliases=2 input_sha256={result['input']['sha256']} "
        f"golden_sha256={result['golden_unique_stream']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
