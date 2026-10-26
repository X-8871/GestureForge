from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import platform
import subprocess
import sys
import time
import textwrap
import zlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

import cv2
import numpy as np

RUN_DIR = Path(__file__).resolve().parent
WORKTREE = RUN_DIR.parents[3]
IMAGE = Path(r"D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\c39c0301-d0ed-4d34-97a0-84c93dd0f515.jpg")
T25_INDEX = WORKTREE / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json"
T25_SHARD = Path(r"D:\FPGA_Competition\report\evidence\S2A-T25\tensors\sample_000.zlib")
PREEXISTING_SNAPSHOT = RUN_DIR / "preexisting_snapshot.json"
SAMPLE_ID = "test_fist_000"
SAMPLE_INDEX = 0
EXPECTED_IMAGE_SHA256 = "6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e"
EXPECTED_T25_INDEX_SHA256 = "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72"
EXPECTED_T25_SHARD_SHA256 = "49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e"
EXPECTED_INPUT_SHA256 = "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"
EXPECTED_RAW_STREAM_SHA256 = "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80"
EXPECTED_BRIDGE_SHA256 = "8a80c33cee83d348af476aada3b922bc1e7671c5e626781560c4de6689d60d19"
CN = timezone(timedelta(hours=8))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def raw_tensor(values: np.ndarray) -> bytes:
    return np.ascontiguousarray(values).tobytes(order="C")


def write_new(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"证据文件已存在，拒绝覆盖：{path}")
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()


def write_json_new(path: Path, value: object) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    write_new(path, payload)


def import_bridge():
    bridge_path = WORKTREE / "scripts" / "stage4_s4ctrl" / "replay_forward_bridge.py"
    spec = importlib.util.spec_from_file_location("s4t26_layer_divergence_bridge", bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法载入冻结的 task-26 桥接器")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def capture_lines(function) -> tuple[int, int]:
    source_lines, first_line = inspect.getsourcelines(function)
    tree = ast.parse(textwrap.dedent("".join(source_lines)))
    definition = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "forward_one")
    loop = next(item for item in definition.body if isinstance(item, ast.For))
    input_statement = next(
        item for item in loop.body
        if isinstance(item, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "kind" for target in item.targets)
    )
    output_statement = next(
        item for item in loop.body
        if isinstance(item, ast.Expr)
        and isinstance(item.value, ast.Call)
        and isinstance(item.value.func, ast.Attribute)
        and isinstance(item.value.func.value, ast.Name)
        and item.value.func.value.id == "int_tensors"
        and item.value.func.attr == "append"
    )
    return first_line + input_statement.lineno - 1, first_line + output_statement.lineno - 1


def tensor_snapshot(tensor) -> dict[str, object]:
    values = np.ascontiguousarray(tensor.values)
    copied = values.copy()
    raw = copied.tobytes(order="C")
    return {
        "values": copied,
        "shape_chw": list(copied.shape),
        "shape_nchw": [1, *list(copied.shape)],
        "dtype": str(copied.dtype),
        "scale": float(tensor.scale),
        "sha256": sha256_bytes(raw),
        "size_bytes": len(raw),
    }


def trace_forward(forward, image_chw: np.ndarray, sections, float_layers, package_layers, scales):
    input_line, output_line = capture_lines(forward.forward_one)
    input_rows: dict[int, dict[str, object]] = {}
    output_rows: dict[int, dict[str, object]] = {}
    target_code = forward.forward_one.__code__

    def tracer(frame, event, argument):
        if frame.f_code is not target_code or event != "line":
            return tracer
        if frame.f_lineno == input_line:
            layer_index = int(frame.f_locals["layer_index"])
            section = frame.f_locals["section"]
            current = frame.f_locals["int_current"]
            tensors = frame.f_locals["int_tensors"]
            if layer_index == 0:
                sources = [{"source": "network_input", "layer_index": None,
                            "tensor": tensor_snapshot(current)}]
            elif section.kind == "route":
                raw_refs = [int(value.strip()) for value in section.options.get("layers", "").split(",") if value.strip()]
                resolved = [forward.resolve_reference(value, layer_index) for value in raw_refs]
                sources = [{"source": "route_ref", "layer_index": source_index,
                            "tensor": tensor_snapshot(tensors[source_index])} for source_index in resolved]
            else:
                source_index = layer_index - 1
                sources = [{"source": "previous_layer", "layer_index": source_index,
                            "tensor": tensor_snapshot(tensors[source_index])}]
            current_snapshot = tensor_snapshot(current)
            input_rows[layer_index] = {
                "layer_index": layer_index,
                "op": section.kind,
                "current_before_op": current_snapshot,
                "sources": sources,
            }
        elif frame.f_lineno == output_line:
            layer_index = int(frame.f_locals["layer_index"])
            section = frame.f_locals["section"]
            output_rows[layer_index] = {
                "layer_index": layer_index,
                "op": section.kind,
                "tensor": tensor_snapshot(frame.f_locals["int_current"]),
            }
        return tracer

    previous_trace = sys.gettrace()
    sys.settrace(tracer)
    try:
        metrics, details = forward.forward_one(image_chw, sections, float_layers, package_layers, scales)
    finally:
        sys.settrace(previous_trace)
    return metrics, details, input_rows, output_rows


def heads_from_layer_trace(layer_outputs: dict[int, dict[str, object]]) -> dict[str, dict[str, object]]:
    """从已观察的卷积输出构造 D9 所需的两个 INT8 检测头视图。"""
    heads: dict[str, dict[str, object]] = {}
    for name, layer_index, height, width in (("head13", 29, 13, 13), ("head26", 36, 26, 26)):
        tensor = layer_outputs[layer_index]["tensor"]
        values = np.ascontiguousarray(tensor["values"])
        expected_shape = (3, 10, height, width)
        if values.dtype != np.int8 or values.size != int(np.prod(expected_shape)):
            raise RuntimeError(f"{name} 卷积输出 dtype/元素数不符：{values.dtype}/{values.shape}")
        heads[name] = {"raw_int8": values.reshape(expected_shape), "scale": float(tensor["scale"]),
                       "layer_index": layer_index, "shape": list(expected_shape)}
    return heads


def save_head_artifacts(prefix: str, heads: dict[str, dict[str, object]]) -> dict[str, object]:
    """只新建本 RunId 的实际前向检测头字节文件。"""
    rows: dict[str, object] = {}
    for name in ("head13", "head26"):
        values = np.ascontiguousarray(heads[name]["raw_int8"])
        raw = values.tobytes(order="C")
        filename = f"{prefix}_{name}_int8.bin"
        write_new(RUN_DIR / filename, raw)
        rows[name] = {"file": filename, "sha256": sha256_bytes(raw), "size_bytes": len(raw),
                      "shape": list(values.shape), "dtype": str(values.dtype),
                      "scale": float(heads[name]["scale"]),
                      "layer_index": int(heads[name]["layer_index"])}
    return rows


def source_sha(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256_file(path)}


def verify_preexisting_changes() -> dict[str, object]:
    """核验开工前记录的 13 项既有差异逐字节未变。"""
    snapshot = json.loads(PREEXISTING_SNAPSHOT.read_text(encoding="utf-8"))
    expected_rows = snapshot.get("preserved_13", [])
    if len(expected_rows) != 13:
        raise RuntimeError(f"既有差异快照条数不是 13：{len(expected_rows)}")
    actual_rows = []
    for row in expected_rows:
        path = WORKTREE / str(row["path"])
        if not path.is_file():
            raise RuntimeError(f"既有差异文件缺失：{row['path']}")
        actual = {"path": row["path"], "size_bytes": path.stat().st_size,
                  "sha256": sha256_file(path)}
        if actual != {"path": row["path"], "size_bytes": row["size_bytes"], "sha256": row["sha256"]}:
            raise RuntimeError(f"既有差异文件字节改变：{row['path']}")
        actual_rows.append(actual)
    return {"snapshot_sha256": sha256_file(PREEXISTING_SNAPSHOT),
            "count": len(actual_rows), "all_unchanged": True, "files": actual_rows}


def main() -> int:
    started = time.perf_counter()
    if not PREEXISTING_SNAPSHOT.is_file():
        raise RuntimeError("缺少运行前工作树快照")
    preexisting_changes = verify_preexisting_changes()
    if sha256_file(IMAGE) != EXPECTED_IMAGE_SHA256:
        raise RuntimeError("sample_000 原图 SHA 与 T25 固定样本不符")
    if sha256_file(T25_INDEX) != EXPECTED_T25_INDEX_SHA256:
        raise RuntimeError("w4 中的 T25 索引 SHA 不符")
    if sha256_file(T25_SHARD) != EXPECTED_T25_SHARD_SHA256:
        raise RuntimeError("T25 sample_000 压缩分片 SHA 不符")

    bridge = import_bridge()
    bridge_path = WORKTREE / "scripts" / "stage4_s4ctrl" / "replay_forward_bridge.py"
    if sha256_file(bridge_path) != EXPECTED_BRIDGE_SHA256:
        raise RuntimeError("task-26 bridge SHA 与 r11 冻结版本不符")
    forward = bridge.load_forward_module()
    numeric = importlib.import_module("verification.s1_t02_d2_numeric_reference")
    delivery = importlib.import_module("verification.s2a_model_delivery")

    index = json.loads(T25_INDEX.read_text(encoding="utf-8"))
    sample_rows = [row for row in index.get("samples", [])
                   if row.get("sample_index") == SAMPLE_INDEX and row.get("sample_id") == SAMPLE_ID]
    if len(sample_rows) != 1:
        raise RuntimeError("T25 索引未唯一绑定 sample_000")
    sample = sample_rows[0]
    if sample.get("original_input", {}).get("sha256") != EXPECTED_IMAGE_SHA256:
        raise RuntimeError("T25 sample_000 原图绑定不一致")
    if sample.get("preprocessed_input", {}).get("sha256") != EXPECTED_INPUT_SHA256:
        raise RuntimeError("T25 sample_000 预处理输入绑定不一致")

    rgb = delivery.decode_rgb(IMAGE)
    rgb_bytes = raw_tensor(rgb)
    bridge_float64, preprocessing_evidence = bridge.load_t25_preprocessed_forward_input(
        IMAGE, 416, 416, forward, EXPECTED_INPUT_SHA256)
    bridge_float64 = np.ascontiguousarray(bridge_float64, dtype=np.float64)
    t25_values = numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), 416, 416)
    t25_input = np.ascontiguousarray(np.asarray(t25_values, dtype=np.int8))
    t25_input_bytes = raw_tensor(t25_input)
    t25_input_sha = sha256_bytes(t25_input_bytes)
    write_new(RUN_DIR / "t25_preprocessed_input_int8.bin", t25_input_bytes)

    float64_bytes = raw_tensor(bridge_float64)
    write_new(RUN_DIR / "bridge_input_prequant_float64_chw.bin", float64_bytes)
    bridge_quantized = np.asarray(
        forward.saturate_array(forward.round_away_array(bridge_float64 / forward.INPUT_SCALE)),
        dtype=np.int8,
    )
    bridge_input_bytes = raw_tensor(bridge_quantized)
    bridge_input_sha = sha256_bytes(bridge_input_bytes)
    write_new(RUN_DIR / "bridge_input_postquant_int8_chw.bin", bridge_input_bytes)
    input_difference = np.abs(bridge_quantized.astype(np.int16) - t25_input.astype(np.int16))
    input_mismatch_count = int(np.count_nonzero(bridge_quantized != t25_input))
    input_match = input_mismatch_count == 0 and bridge_input_sha == EXPECTED_INPUT_SHA256 == t25_input_sha

    compressed = T25_SHARD.read_bytes()
    raw_stream = zlib.decompress(compressed)
    network = sample.get("network", {})
    compressed_ref = network.get("compressed_shard", {})
    if len(raw_stream) != compressed_ref.get("decompressed_bytes"):
        raise RuntimeError("T25 sample_000 解压长度与索引不符")
    stream_sha = sha256_bytes(raw_stream)
    if (stream_sha != EXPECTED_RAW_STREAM_SHA256
            or stream_sha != compressed_ref.get("decompressed_sha256")
            or stream_sha != network.get("raw_stream_sha256")):
        raise RuntimeError("T25 sample_000 解压张量流 SHA 不符")
    descriptors = network.get("tensors", [])
    if len(descriptors) != 38:
        raise RuntimeError("T25 sample_000 索引不是 38 层")

    bindings = bridge.resolve_contract_bindings()
    verified_bindings = {}
    for key, item in bindings.items():
        path = Path(item["path"])
        digest = bridge.verify(path, item["sha256"], f"冻结参数 {key}")
        verified_bindings[key] = {"path": str(path), "sha256": digest}
    cfg_path = Path(bindings["cfg"]["path"])
    weights_path = Path(bindings["weights"]["path"])
    package_path = Path(bindings["gf8_package"]["path"])
    calibration_path = Path(bindings["calibration_list"]["path"])
    activation_path = bridge.ACTIVATION_REPORT
    bridge.verify(activation_path, bridge.ACTIVATION_REPORT_SHA256, "冻结 activation report")
    sections = forward.parse_cfg_sections(cfg_path)
    float_layers = forward.read_fused_float_layers(cfg_path, weights_path)
    header, package_layers = forward.parse_package(package_path)
    activation_scales = forward.load_activation_scales(activation_path, cfg_path, weights_path, calibration_path)
    if header.get("width") != 416 or header.get("height") != 416 or header.get("channels") != 3:
        raise RuntimeError("GF8 输入头不是 tiny416")
    if set(float_layers) != set(package_layers) or set(package_layers) != set(activation_scales):
        raise RuntimeError("cfg、浮点权重、GF8 与 activation scale 层集合不一致")

    print("[RUN] sample_000 frozen-input forward_one and 38-layer byte comparison", flush=True)
    metrics, details, layer_inputs, layer_outputs = trace_forward(
        forward, bridge_float64, sections, float_layers, package_layers, activation_scales
    )
    print("[DONE] sample_000 forward_one captured", flush=True)
    if len(layer_inputs) != 38 or len(layer_outputs) != 38:
        raise RuntimeError(f"forward_one trace 层数不完整：inputs={len(layer_inputs)} outputs={len(layer_outputs)}")
    if layer_inputs[0]["current_before_op"]["sha256"] != bridge_input_sha:
        raise RuntimeError("forward_one 实际层0输入与记录的桥接器量化输入不一致")

    layer_rows = []
    first_divergence = None
    first_byte_mismatch = None
    actual_unique_stream = bytearray()
    for descriptor in descriptors:
        layer_index = int(descriptor["layer_index"])
        capture = layer_outputs[layer_index]
        actual = capture["tensor"]["values"]
        actual_bytes = raw_tensor(actual)
        offset = int(descriptor["byte_offset"])
        length = int(descriptor["byte_length"])
        expected_bytes = raw_stream[offset:offset + length]
        if len(expected_bytes) != length:
            raise RuntimeError(f"T25 layer{layer_index} 切片长度不完整")
        if sha256_bytes(expected_bytes) != descriptor.get("tensor_sha256"):
            raise RuntimeError(f"T25 layer{layer_index} 切片 SHA 与索引不符")
        expected = np.frombuffer(expected_bytes, dtype=np.int8).reshape(actual.shape)
        shape_nchw = [1, *list(actual.shape)]
        shape_equal = shape_nchw == descriptor.get("shape_nchw") and actual.dtype == np.int8
        scale_equal = float(capture["tensor"]["scale"]) == float(descriptor["scale"])
        bytes_equal = shape_equal and len(actual_bytes) == length and actual_bytes == expected_bytes
        mismatch_count = int(np.count_nonzero(actual != expected)) if shape_equal else None
        max_abs_difference = int(np.max(np.abs(actual.astype(np.int16) - expected.astype(np.int16)))) if shape_equal else None
        source_rows = layer_inputs[layer_index]["sources"]
        source_sha_values = [item["tensor"]["sha256"] for item in source_rows]
        row = {
            "layer_index": layer_index,
            "op": descriptor["op"],
            "forward_op": capture["op"],
            "shape_nchw": shape_nchw,
            "t25_shape_nchw": descriptor["shape_nchw"],
            "dtype": str(actual.dtype),
            "different_byte_count": mismatch_count,
            "max_absolute_int8_difference": max_abs_difference,
            "t25_scale": float(descriptor["scale"]),
            "bridge_scale": float(capture["tensor"]["scale"]),
            "scale_equal": scale_equal,
            "shape_equal": shape_equal,
            "bytewise_equal": bytes_equal,
            "exact_equal_including_scale": bytes_equal and scale_equal,
            "input_source_sha256": source_sha_values[0] if len(source_sha_values) == 1 else None,
            "input_sources": [{"source": item["source"], "layer_index": item["layer_index"],
                               "shape_nchw": item["tensor"]["shape_nchw"],
                               "scale": item["tensor"]["scale"],
                               "sha256": item["tensor"]["sha256"]} for item in source_rows],
            "bridge_output_sha256": sha256_bytes(actual_bytes),
            "t25_output_sha256": descriptor["tensor_sha256"],
            "t25_byte_offset": offset,
            "t25_byte_length": length,
            "t25_stored": descriptor.get("stored"),
            "t25_alias_of_layer_index": descriptor.get("alias_of_layer_index"),
        }
        layer_rows.append(row)
        if descriptor.get("stored", True):
            actual_unique_stream.extend(actual_bytes)
        if first_byte_mismatch is None and not bytes_equal:
            first_byte_mismatch = row
        if first_divergence is None and not (bytes_equal and scale_equal):
            first_divergence = row

    actual_stream_bytes = bytes(actual_unique_stream)
    write_new(RUN_DIR / "bridge_unique_layer_output_stream.zlib", zlib.compress(actual_stream_bytes, level=9))
    if first_divergence is not None:
        layer_index = int(first_divergence["layer_index"])
        descriptor = descriptors[layer_index]
        offset = int(descriptor["byte_offset"])
        length = int(descriptor["byte_length"])
        expected_bytes = raw_stream[offset:offset + length]
        actual_bytes = raw_tensor(layer_outputs[layer_index]["tensor"]["values"])
        write_new(RUN_DIR / f"first_divergence_layer_{layer_index:02d}_t25_int8.bin", expected_bytes)
        write_new(RUN_DIR / f"first_divergence_layer_{layer_index:02d}_bridge_int8.bin", actual_bytes)

    goldens = bridge.load_rebound_goldens(bridge.GOLDEN_OUTPUT_DIR)
    d9 = bridge.load_d9_module()
    validation: dict[str, object] = {}

    sample000_heads = heads_from_layer_trace(layer_outputs)
    sample000_expected = goldens[SAMPLE_ID]
    sample000_raw_equal, sample000_raw_comparison = bridge.compare_raw_heads(
        sample000_heads, sample000_expected["expected_heads"])
    sample000_head_artifacts = save_head_artifacts("sample_000_actual", sample000_heads)
    predictions000, candidate_count000 = bridge.decode_heads_with_d9(
        d9, sample000_heads, SAMPLE_ID, int(rgb.shape[1]), int(rgb.shape[0]))
    prediction_rows000 = bridge.prediction_records(predictions000)
    t29_sample000 = sample000_expected["t29_sample"]
    expected_candidates000 = int(t29_sample000.get("raw_candidate_count_before_stable_nms", -1))
    expected_nms_count000 = int(t29_sample000.get("nms_output_box_count", -1))
    detection_equal000 = (candidate_count000 == expected_candidates000
                          and len(prediction_rows000) == expected_nms_count000
                          and prediction_rows000 == t29_sample000.get("detections", []))
    validation["sample_000_positive_detection_gate"] = {
        "input_sha256": EXPECTED_IMAGE_SHA256,
        "raw_head_gate": {"status": "PASS" if sample000_raw_equal else "BLOCKED",
                           "comparisons": sample000_raw_comparison,
                           "actual_head_files": sample000_head_artifacts},
        "d9_nms": {"status": "PASS" if detection_equal000 else "BLOCKED",
                   "raw_candidate_count_before_stable_nms": candidate_count000,
                   "expected_raw_candidate_count": expected_candidates000,
                   "nms_output_count": len(prediction_rows000),
                   "expected_nms_output_count": expected_nms_count000,
                   "predictions": prediction_rows000,
                   "expected_predictions": t29_sample000.get("detections", []),
                   "exact_match": detection_equal000},
    }

    sample102 = goldens["approved_no_hand_001"]
    sample102_path = Path(sample102["image_path"])
    sample102_t25_input = sample102["t25_sample"]["preprocessed_input"]
    input102_chw, input102_preprocess = bridge.load_t25_preprocessed_forward_input(
        sample102_path, 416, 416, forward, str(sample102_t25_input["sha256"]))
    input102_quantized = np.asarray(forward.saturate_array(forward.round_away_array(
        input102_chw.astype(np.float64) / forward.INPUT_SCALE)), dtype=np.int8)
    input102_prequant_bytes = raw_tensor(input102_chw)
    input102_quantized_bytes = raw_tensor(input102_quantized)
    write_new(RUN_DIR / "sample_102_bridge_input_prequant_float64_chw.bin", input102_prequant_bytes)
    write_new(RUN_DIR / "sample_102_bridge_input_postquant_int8_chw.bin", input102_quantized_bytes)
    print("[RUN] sample_102 real forward and raw-head byte gate", flush=True)
    metrics102, stats102, heads102 = bridge.capture_forward_heads(
        forward, d9, input102_chw, sections, float_layers, package_layers, activation_scales,
        sample102["t29_sample"]["head_tensors"])
    print("[DONE] sample_102 forward captured", flush=True)
    sample102_raw_equal, sample102_raw_comparison = bridge.compare_raw_heads(
        heads102, sample102["expected_heads"])
    hashes102 = bridge.head_hashes(heads102)
    sample102_head_artifacts = save_head_artifacts("sample_102_actual", heads102)
    validation["sample_102_raw_head_gate"] = {
        "input_sha256": sample102["image_sha256"],
        "preprocessing_representations": input102_preprocess,
        "input_float64_raw_sha256": sha256_bytes(input102_prequant_bytes),
        "input_postquant_int8_sha256": sha256_bytes(input102_quantized_bytes),
        "input_postquant_matches_t25": (sha256_bytes(input102_quantized_bytes)
                                         == str(sample102_t25_input["sha256"]).lower()),
        "raw_head_gate": {"status": "PASS" if sample102_raw_equal else "BLOCKED",
                           "comparisons": sample102_raw_comparison,
                           "actual_head_sha256": hashes102,
                           "actual_head_files": sample102_head_artifacts},
        "metrics_and_integer_stats_role": "diagnostic_only_not_golden",
        "metrics": metrics102,
        "integer_stats": stats102.get("integer_stats", {}),
    }

    print("[RUN] one-byte INT8 perturbation forward", flush=True)
    tampered102, mutation102 = bridge.mutate_one_input_byte(input102_quantized)
    tampered102_chw = tampered102.astype(np.float64) * np.float64(forward.INPUT_SCALE)
    roundtrip102 = np.asarray(forward.saturate_array(forward.round_away_array(
        tampered102_chw / forward.INPUT_SCALE)), dtype=np.int8)
    _, _, perturbed_heads102 = bridge.capture_forward_heads(
        forward, d9, tampered102_chw, sections, float_layers, package_layers, activation_scales,
        sample102["t29_sample"]["head_tensors"])
    perturbed_hashes102 = bridge.head_hashes(perturbed_heads102)
    mutation_single_byte = int(np.count_nonzero(input102_quantized != tampered102)) == 1
    mutation_roundtrip = bool(np.array_equal(roundtrip102, tampered102))
    mutation_changes_heads = perturbed_hashes102 != hashes102
    mutation_pass = mutation_single_byte and mutation_roundtrip and mutation_changes_heads
    print("[DONE] one-byte INT8 perturbation captured", flush=True)
    validation["single_byte_perturbation"] = {
        "status": "PASS" if mutation_pass else "BLOCKED",
        **mutation102,
        "changed_int8_elements": int(np.count_nonzero(input102_quantized != tampered102)),
        "roundtrip_exact": mutation_roundtrip,
        "baseline_head_sha256": hashes102,
        "perturbed_head_sha256": perturbed_hashes102,
        "head_hash_changed": mutation_changes_heads,
    }

    png_cv2 = importlib.import_module("cv2")
    png_path = Path(sample102["image_path"])
    png_pixels = png_cv2.imread(str(png_path), png_cv2.IMREAD_UNCHANGED)
    if (png_pixels is None or png_pixels.dtype != np.uint8 or png_pixels.ndim != 3
            or png_pixels.shape[2] != 3):
        png_pass = False
        png_detail = {"error": "approved_no_hand_001 PNG 未解码为 uint8 三通道像素"}
    else:
        encoded_ok, encoded_png = png_cv2.imencode(
            ".png", png_pixels, [png_cv2.IMWRITE_PNG_COMPRESSION, 0])
        decoded_png = png_cv2.imdecode(encoded_png, png_cv2.IMREAD_UNCHANGED) if encoded_ok else None
        png_pass = bool(encoded_ok and decoded_png is not None
                        and decoded_png.shape == png_pixels.shape
                        and decoded_png.dtype == png_pixels.dtype
                        and np.array_equal(decoded_png, png_pixels))
        png_detail = {"source_image_sha256": sample102["image_sha256"],
                      "imread_flag": "IMREAD_UNCHANGED", "shape": list(png_pixels.shape),
                      "dtype": str(png_pixels.dtype), "lossless_roundtrip_pixel_identity": png_pass,
                      "encoded_png_sha256": sha256_bytes(encoded_png.tobytes()) if encoded_ok else None}
    validation["png_imread_unchanged"] = {"status": "PASS" if png_pass else "BLOCKED", **png_detail}
    validation["all_required_checks_pass"] = bool(
        sample000_raw_equal and detection_equal000 and sample102_raw_equal
        and mutation_pass and png_pass)
    validation["task27_input_generated"] = False

    source_files = {
        "bridge": source_sha(bridge_path),
        "g0_checker_r14": source_sha(WORKTREE / "verification" / "check_s4t26_g0_inputs.py"),
        "forward_module": source_sha(bridge.FORWARD_MODULE),
        "numeric_preprocess_oracle": source_sha(WORKTREE / "verification" / "s1_t02_d2_numeric_reference.py"),
        "t25_decode_module": source_sha(WORKTREE / "verification" / "s2a_model_delivery.py"),
        "t25_layer_index": source_sha(T25_INDEX),
        "t25_compressed_shard": source_sha(T25_SHARD),
        "sample_image": source_sha(IMAGE),
        "activation_report": source_sha(activation_path),
        **{key: value for key, value in verified_bindings.items()},
    }
    prequant = {
        "float64_chw_internal": {"dtype": str(bridge_float64.dtype), "shape_chw": list(bridge_float64.shape),
                                  "origin": "T25 frozen INT8 input dequantized with frozen INPUT_SCALE; actual forward_one argument",
                                  "raw_data_sha256": sha256_bytes(float64_bytes),
                                  "file": "bridge_input_prequant_float64_chw.bin"},
        "post_quantization_int8": {"dtype": str(bridge_quantized.dtype), "shape_chw": list(bridge_quantized.shape),
                                   "scale": float(forward.INPUT_SCALE),
                        "quantizer": "round_away_array(float64 / INPUT_SCALE), saturate_array([-127,127])",
                                   "raw_data_sha256": bridge_input_sha,
                                   "file": "bridge_input_postquant_int8_chw.bin",
                                   "forward_one_layer0_input_sha256": layer_inputs[0]["current_before_op"]["sha256"],
                                   "forward_one_input_identity_verified": layer_inputs[0]["current_before_op"]["sha256"] == bridge_input_sha},
        "t25_oracle_int8": {"dtype": str(t25_input.dtype), "shape_chw": list(t25_input.shape),
                             "scale": float(numeric.INPUT_SCALE), "raw_data_sha256": t25_input_sha,
                             "expected_index_sha256": EXPECTED_INPUT_SHA256,
                             "file": "t25_preprocessed_input_int8.bin"},
        "int8_to_int8_comparison": {"equal": input_match, "different_byte_count": input_mismatch_count,
                                    "max_absolute_int8_difference": int(input_difference.max()),
                                    "bridge_int8_sha256": bridge_input_sha,
                                    "t25_int8_sha256": t25_input_sha},
        "cross_dtype_hash_comparison_performed": False,
        "bridge_t25_preprocessing_evidence": preprocessing_evidence,
    }
    input_divergence = None
    if not input_match:
        input_divergence = {
            "stage": "input_preprocess",
            "layer_index": -1,
            "op": "input_preprocess",
            "shape_chw": list(bridge_quantized.shape),
            "dtype": "int8",
            "different_byte_count": input_mismatch_count,
            "max_absolute_int8_difference": int(input_difference.max()),
            "scale": float(forward.INPUT_SCALE),
            "input_source_sha256": EXPECTED_IMAGE_SHA256,
            "bridge_output_sha256": bridge_input_sha,
            "t25_output_sha256": t25_input_sha,
        }
    report = {
        "task_id": "S4-T26-LAYER-DIVERGENCE",
        "run_id": RUN_DIR.name,
        "generated_utc8": datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds"),
        "command": [sys.executable, "-B", str(Path(__file__).resolve())],
        "worktree": str(WORKTREE),
        "baseline_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=WORKTREE, check=True,
                                         capture_output=True, text=True, encoding="utf-8").stdout.strip(),
        "branch": subprocess.run(["git", "branch", "--show-current"], cwd=WORKTREE, check=True,
                                 capture_output=True, text=True, encoding="utf-8").stdout.strip(),
        "elapsed_seconds": time.perf_counter() - started,
        "status": ("DIVERGENCE_FOUND" if first_divergence is not None or not input_match
                   else ("LAYER_MATCH_AND_REQUIRED_GATES_PASS" if validation["all_required_checks_pass"]
                         else "BLOCKED_POST_PREPROCESS_VALIDATION")),
        "exit_code": 0,
        "sample": {"sample_id": SAMPLE_ID, "sample_index": SAMPLE_INDEX,
                   "image_path": str(IMAGE), "image_sha256": EXPECTED_IMAGE_SHA256,
                   "decoded_rgb_shape_hwc": list(rgb.shape), "decoded_rgb_dtype": str(rgb.dtype),
                   "decoded_rgb_sha256": sha256_bytes(rgb_bytes)},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "opencv": cv2.__version__},
        "sources": source_files,
        "preexisting_changes": preexisting_changes,
        "g0_checker_execution": {"version": "r14", "status": "NOT_RUN",
                                  "reason": "当前任务边界禁止读取 dbdf；G0 检查器包含 task-25 提交祖先关系只读查询。"},
        "bridge_input_representations": prequant,
        "t25_stream": {"compressed_path": str(T25_SHARD), "compressed_sha256": sha256_file(T25_SHARD),
                       "decompressed_bytes": len(raw_stream), "decompressed_sha256": stream_sha,
                       "expected_decompressed_sha256": EXPECTED_RAW_STREAM_SHA256,
                       "layer_count": len(descriptors)},
        "bridge_forward": {"function": "verification/s1_t02_d2_int8_forward.py::forward_one",
                            "invocation": "same frozen bridge r11 parameter loader and forward_one call; trace observes locals without changing network math",
                            "captured_input_layers": len(layer_inputs), "captured_output_layers": len(layer_outputs),
                            "metrics_layer_count": len(metrics), "integer_stats_layer_count": len(details.get("integer_stats", {})),
                            "bridge_unique_stream_bytes": len(actual_stream_bytes),
                            "bridge_unique_stream_sha256": sha256_bytes(actual_stream_bytes),
                            "t25_unique_stream_bytes": network.get("unique_output_raw_bytes"),
                            "scale_hashes_compared_as_bytes": False},
        "execution_scope": {"evidence_kind": "offline_host", "timing_claim_scope": "replay_only",
                            "hardware_execution": "NOT_RUN", "task27_input_generated": False,
                            "ENABLE": "0", "RAW_G0": "OPEN",
                            "P_4D_G3_G5": "NOT_RUN"},
        "first_divergence": input_divergence if input_divergence is not None else first_divergence,
        "first_layer_divergence": first_divergence,
        "first_byte_mismatch_layer": first_byte_mismatch,
        "all_layer_comparisons": layer_rows,
        "follow_up_gates": validation,
        "limitations": ["本RunId只定位T25逐层整数输出分歧，不是task-27输入包。",
                        "未更改T25/T29、分片、模型、权重或scale。",
                        "ENABLE=0；G3/G5未通过或解除。"],
    }
    write_json_new(RUN_DIR / "layer_divergence_report.json", report)
    file_records = {}
    for path in sorted(RUN_DIR.iterdir()):
        if path.is_file() and path.name != "delivery_manifest.json":
            file_records[path.name] = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "task_id": "S4-T26-LAYER-DIVERGENCE",
        "run_id": RUN_DIR.name,
        "status": report["status"],
        "exit_code": 0,
        "command": [sys.executable, "-B", str(Path(__file__).resolve())],
        "source_script_sha256": sha256_file(Path(__file__).resolve()),
        "baseline_head": report["baseline_head"],
        "branch": report["branch"],
        "outputs": file_records,
        "task27_input_generated": False,
    }
    write_json_new(RUN_DIR / "delivery_manifest.json", manifest)
    print(f"[RESULT] {report['status']} required_gates={validation['all_required_checks_pass']} task27=false", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
