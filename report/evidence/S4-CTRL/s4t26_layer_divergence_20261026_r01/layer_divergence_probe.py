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
EXPECTED_BRIDGE_SHA256 = "6780446fc4f0d774b5868896b455deec8fc3dcd9e1ffa12a6990577138e57f26"
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


def source_sha(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256_file(path)}


def main() -> int:
    if not PREEXISTING_SNAPSHOT.is_file():
        raise RuntimeError("缺少运行前工作树快照")
    if sha256_file(IMAGE) != EXPECTED_IMAGE_SHA256:
        raise RuntimeError("sample_000 原图 SHA 与 T25 固定样本不符")
    if sha256_file(T25_INDEX) != EXPECTED_T25_INDEX_SHA256:
        raise RuntimeError("w4 中的 T25 索引 SHA 不符")
    if sha256_file(T25_SHARD) != EXPECTED_T25_SHARD_SHA256:
        raise RuntimeError("T25 sample_000 压缩分片 SHA 不符")

    bridge = import_bridge()
    bridge_path = WORKTREE / "scripts" / "stage4_s4ctrl" / "replay_forward_bridge.py"
    if sha256_file(bridge_path) != EXPECTED_BRIDGE_SHA256:
        raise RuntimeError("task-26 bridge SHA 与 r10 冻结版本不符")
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
    numeric_result = numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), 416, 416)
    t25_input = np.asarray(numeric_result, dtype=np.int8)
    del numeric_result
    t25_input_bytes = raw_tensor(t25_input)
    t25_input_sha = sha256_bytes(t25_input_bytes)
    write_new(RUN_DIR / "t25_preprocessed_input_int8.bin", t25_input_bytes)

    bridge_float32 = np.ascontiguousarray(forward.load_image_chw(IMAGE, 416, 416))
    bridge_float64 = np.ascontiguousarray(bridge_float32.astype(np.float64))
    float32_bytes = raw_tensor(bridge_float32)
    float64_bytes = raw_tensor(bridge_float64)
    write_new(RUN_DIR / "bridge_input_prequant_float32_chw.bin", float32_bytes)
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
    if len(raw_stream) != network.get("decompressed_bytes"):
        raise RuntimeError("T25 sample_000 解压长度与索引不符")
    stream_sha = sha256_bytes(raw_stream)
    if stream_sha != EXPECTED_RAW_STREAM_SHA256 or stream_sha != network.get("decompressed_sha256"):
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

    metrics, details, layer_inputs, layer_outputs = trace_forward(
        forward, bridge_float32, sections, float_layers, package_layers, activation_scales
    )
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

    source_files = {
        "bridge": source_sha(bridge_path),
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
        "float32_chw": {"dtype": str(bridge_float32.dtype), "shape_chw": list(bridge_float32.shape),
                        "scale_semantics": "normalized_rgb_0_to_1_before_forward_one_quantization",
                        "raw_data_sha256": sha256_bytes(float32_bytes),
                        "file": "bridge_input_prequant_float32_chw.bin"},
        "float64_chw_internal": {"dtype": str(bridge_float64.dtype), "shape_chw": list(bridge_float64.shape),
                                  "origin": "forward_one image_chw.astype(float64)",
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
        "worktree": str(WORKTREE),
        "baseline_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=WORKTREE, check=True,
                                         capture_output=True, text=True, encoding="utf-8").stdout.strip(),
        "branch": subprocess.run(["git", "branch", "--show-current"], cwd=WORKTREE, check=True,
                                 capture_output=True, text=True, encoding="utf-8").stdout.strip(),
        "status": "DIVERGENCE_FOUND" if first_divergence is not None or not input_match else "ALL_T25_LAYER_BYTES_MATCH",
        "exit_code": 0,
        "sample": {"sample_id": SAMPLE_ID, "sample_index": SAMPLE_INDEX,
                   "image_path": str(IMAGE), "image_sha256": EXPECTED_IMAGE_SHA256,
                   "decoded_rgb_shape_hwc": list(rgb.shape), "decoded_rgb_dtype": str(rgb.dtype),
                   "decoded_rgb_sha256": sha256_bytes(rgb_bytes)},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "opencv": cv2.__version__},
        "sources": source_files,
        "bridge_input_representations": prequant,
        "t25_stream": {"compressed_path": str(T25_SHARD), "compressed_sha256": sha256_file(T25_SHARD),
                       "decompressed_bytes": len(raw_stream), "decompressed_sha256": stream_sha,
                       "expected_decompressed_sha256": EXPECTED_RAW_STREAM_SHA256,
                       "layer_count": len(descriptors)},
        "bridge_forward": {"function": "verification/s1_t02_d2_int8_forward.py::forward_one",
                            "invocation": "same frozen bridge r10 parameter loader and forward_one call; trace observes locals without changing network math",
                            "captured_input_layers": len(layer_inputs), "captured_output_layers": len(layer_outputs),
                            "metrics_layer_count": len(metrics), "integer_stats_layer_count": len(details.get("integer_stats", {})),
                            "bridge_unique_stream_bytes": len(actual_stream_bytes),
                            "bridge_unique_stream_sha256": sha256_bytes(actual_stream_bytes),
                            "t25_unique_stream_bytes": network.get("unique_output_raw_bytes"),
                            "scale_hashes_compared_as_bytes": False},
        "first_divergence": input_divergence if input_divergence is not None else first_divergence,
        "first_layer_divergence": first_divergence,
        "first_byte_mismatch_layer": first_byte_mismatch,
        "all_layer_comparisons": layer_rows,
        "follow_up_gates": {"sample_102_raw_head": "NOT_RUN_IN_THIS_DIAGNOSTIC",
                            "sample_000_d9_nms": "NOT_RUN_BECAUSE_LAYER_DIVERGENCE_REMAINS",
                            "single_byte_perturbation": "NOT_RUN_BECAUSE_LAYER_DIVERGENCE_REMAINS",
                            "png_imread_unchanged": "NOT_RUN_BECAUSE_LAYER_DIVERGENCE_REMAINS",
                            "task27_input_generated": False},
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
        "command": [sys.executable, str(Path(__file__).resolve())],
        "source_script_sha256": sha256_file(Path(__file__).resolve()),
        "baseline_head": report["baseline_head"],
        "branch": report["branch"],
        "outputs": file_records,
        "task27_input_generated": False,
    }
    write_json_new(RUN_DIR / "delivery_manifest.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
