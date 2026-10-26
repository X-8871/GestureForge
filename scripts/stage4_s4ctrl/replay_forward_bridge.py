#!/usr/bin/env python3
"""离线真实彩色链 · task-26 双样本门与回放结果桥（r11，离线等价）。

## 边界（2026-10-24 lead 裁决，逐条实现）
1. **优先复用而非重写**：使用 T25 冻结的 `preprocess_rgb_uint8_to_chw_int8` 产生实际输入，
   以其 INT8 值乘冻结 `INPUT_SCALE` 传给既有 `forward_one`；入口回量化必须逐字节不变。
   `forward_one` 内部完成量化：`Tensor(saturate(round_away(chw/INPUT_SCALE)), INPUT_SCALE)`。
   本文件**不复制**任何预处理或网络数学，也不修改任何冻结件。
2. **量化与顺序沿冻结口径**：网络量化由既有 `forward_one` 执行；证据记录 `INPUT_SCALE`、
   各层 `activation_scale` 与张量/输出摘要哈希。
3. **可复现与判别力**：同一输入跑两次须得同一层级摘要哈希；负向对照覆盖错 scale、跨过 INT8 量化档的输入改动、有损 JPEG 容器。
4. **双样本门**：`approved_no_hand_001` 只作 raw-head 逐字节门，`test_fist_000` 作阳性检测/D9/NMS 门；旧校准样本只保留历史身份。
5. **真实检测头**：只通过既有前向模块的 `metric` 调用捕获 YOLO 输出；按 cfg layer index、D9 head grid 与 T25/T29 元数据校验，不复制网络数学。
6. **冻结黄金**：只从经固定 SHA 验证的 T25/T29 材料化字节加载 raw head；当前 Darknet/hook 控制未复现 T29，不作黄金来源。
7. **执行门禁**：材料化、决策、上游提交绑定和运行参数检查全 PASS 后才执行真实前向。任一真实前向失败时保持 BLOCKED，禁止生成 task-27 包。
8. **输入完整性**：单字节输入扰动与 PNG `IMREAD_UNCHANGED` 像素检查独立记录；所有结果标记 `replay_only` / `scope=offline_host`。

用法（只写 --run-dir）：
  python -B scripts/stage4_s4ctrl/replay_forward_bridge.py --run-dir <evidence_dir>
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import platform
import subprocess
import sys
import time
import types
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

CN = timezone(timedelta(hours=8))
BRIDGE_VERSION = "r12"
WORKTREE = Path(__file__).resolve().parents[2]
FORWARD_MODULE = WORKTREE / "verification" / "s1_t02_d2_int8_forward.py"
D9_MODULE = WORKTREE / "verification" / "s1_t02_d9_yolo_decode.py"
D6_MODULE = WORKTREE / "verification" / "s1_t02_d6_detection_metrics.py"
T25_INDEX = WORKTREE / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json"
T29_REFERENCE = WORKTREE / "report" / "evidence" / "S2A-T29" / "cpu_decode_nms_reference.json"
T29_GENERATOR = WORKTREE / "verification" / "s2a_decode_nms_reference.py"
T29_TEST = WORKTREE / "verification" / "test_s2a_decode_nms_reference.py"
BOUND_T25_T29_TREE = Path(r"D:\codex-worktrees\dbdf")
TASK25_PACKAGE_COMMIT = "584b07664e88a18bf786ba9565a138861e136d76"
TASK25_FRAME_COMMIT = "0ad2000cbc4af7b29f299c2277465bba608a8129"
S4A_CONTRACT = WORKTREE / "docs" / "stage4" / "s4a_stage4_g0_fields.json"
# 激活报告未列入 S4-A 契约；本离线脚本单独固定其 raw SHA 与 LF 内容 SHA，不改写正式契约。
ACTIVATION_REPORT = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
REFERENCE_RUN = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_int8_forward_r2.json"
REPLAY_DIR = Path(r"D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_stage3_window_20261024_r01")
REPLAY_FRAME = REPLAY_DIR / "frame_full.bin"
REPLAY_FRAME_SHA256 = "939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0"
TASK25_REPLAY_BINDING = Path(r"D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_replay_binding_20261025_r01\replay_input_binding.json")
TASK25_REPLAY_BINDING_SHA256 = "2addbb5a7da2c4c4b75f5518af6639f42b0e3b6bdfd4da1a67a34e9289f38a41"
S4A_CONTRACT_SHA256 = "657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5"
ACTIVATION_REPORT_SHA256 = "6d73283c698a94dd30cf00634de59fb76a8e889916eb4d00e50b76c245687216"
ACTIVATION_REPORT_CONTENT_SHA256 = "1156ef813db4e08504c6bb8935b02720a6dd9b792e8a48d255725571d27063e5"
REFERENCE_RUN_SHA256 = "3d5ccedc9dc25f62353711c75f509706187047dbd70321cefb98e0bc0ade3973"
REFERENCE_RUN_CONTENT_SHA256 = "63f5bfef5cb9801f45cc51779ca87997686f46f52b48a3a22d87ff012271d3e4"
WEIGHT_REPORT = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
WEIGHT_REPORT_SHA256 = "d867cd5dc7497f0de9db5c4e0643afd2e52d4c1e77632852487e8afceaa0dd80"
FORWARD_MODULE_SHA256 = "0b90ef46b923b046cfcabb0b8ff8aaff4f6b927b9b8ee9eaa10335362c6c922a"
FORWARD_MODULE_CONTENT_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
T25_INDEX_LF_SHA256 = "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d"
T29_REFERENCE_LF_SHA256 = "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"
D9_MODULE_LF_SHA256 = "0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6"
D6_MODULE_LF_SHA256 = "5ff91ffbbaa82935811f2ddc335434a3c70afa58eaa980e353e64b057803bea2"
T29_GENERATOR_LF_SHA256 = "219a09720d9de0723730b51ed9c007aeec5e1b9abf6bc49c5e0268c2173bc49c"
T25_INDEX_RAW_SHA256 = "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72"
T29_REFERENCE_RAW_SHA256 = "26392c8d7f5ca8643a26c149411c66d6f2343a544f8c4f03d32584dc4e071d33"
EXPECTED_W4_BASELINE_COMMIT = "4c726f17d4a83df9e6fbd8b1a9863c0ac2fb256e"
GOLDEN_RUN_ID = "s4t26_golden_rebind_20261026_r02"
GOLDEN_OUTPUT_DIR = WORKTREE / "report" / "evidence" / "S4-CTRL" / GOLDEN_RUN_ID
GOLDEN_MANIFEST = WORKTREE / "report" / "evidence" / "S4-CTRL" / GOLDEN_RUN_ID / "golden_materialization_manifest.json"
GOLDEN_MANIFEST_SHA256 = "47e4cc362d174f1c8eb451197554e5978cd818032c3461af655f959f9fa108c6"
REBIND_DECISION = WORKTREE / "docs" / "stage4" / "s4t26_golden_rebind_decision_20261026_r01.md"
REBIND_DECISION_SHA256 = "819c9054be9bc3232d51666bc9e52e112fc3932b1d3a165d36040f26744356e1"
T25_SHARDS = Path(r"D:\FPGA_Competition\report\evidence\S2A-T25\tensors")
RAW_HEAD_GATE = {
    "gate": "raw_head_gate", "sample_id": "approved_no_hand_001", "sample_index": 102,
    "image_path": Path(r"D:\FPGA_Data\HaGRIDv2\user_no_hand\20260915_friend_001.png"),
    "image_sha256": "10f1f104343cae97abf817316de3a75bacb646da6c686a2204eedcc2611f34f4",
}
POSITIVE_DETECTION_GATE = {
    "gate": "positive_detection_gate", "sample_id": "test_fist_000", "sample_index": 0,
    "image_path": Path(r"D:\FPGA_Data\HaGRIDv2\dataset\fist\fist\c39c0301-d0ed-4d34-97a0-84c93dd0f515.jpg"),
    "image_sha256": "6dbd72693bc6ad2af6121ffe95e2ee5e9c14597a4c4d16a6db8cdf07d8e43b0e",
}
OLD_CALIBRATION_SAMPLE = {
    "sample_id": "98529267-1eda-43a6-8e38-245947ecb312",
    "image_sha256": "c116ba1d...35ee70b", "status": "NOT_USED_HISTORICAL",
}
STALE_LIMIT_NS = 200_000_000
STALE_APPROVAL_SHA256 = "d8edb84849cd1f93fded902dd913e841564bb1abedbfacd7c7ecde3112e874fb"
T29_SCORE_THRESHOLD = 0.25
REFERENCE_STATUS = "INT8_INTEGER_FORWARD_COMPLETE_FLOAT_REFERENCE_COMPARISON_PENDING_REVIEW"
SOURCE_SNAPSHOT = WORKTREE / "report" / "evidence" / "S4-CTRL" / "s4t26_forward_bridge_20261024_r01" / "replay_forward_bridge.py.original"
SOURCE_SNAPSHOT_SHA256 = "8d0e46fa20058a4039c1dbb462d8150a7d5c64030e3620f0a8b7aaf922b6a43c"
PNG_COMPRESSION = 0  # 写死：无损、无额外滤波
LOG_PATH: Path | None = None


def now_cn() -> str:
    """当前 UTC+8 时间戳。"""
    return datetime.now(timezone.utc).astimezone(CN).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    """字节 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """文件 SHA-256。"""
    return sha256_bytes(path.read_bytes())


def sha256_lf_content(path: Path) -> str:
    """按 Git 文本文件的 LF 内容口径计算 SHA-256。"""
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def emit(message: str) -> None:
    """同时输出到终端和本次证据日志。"""
    print(message, flush=True)
    if LOG_PATH is not None:
        with LOG_PATH.open("a", encoding="utf-8") as stream:
            stream.write(message + "\n")


def canonical_digest(obj: object) -> str:
    """对 JSON 可序列化对象求确定性摘要。"""
    return sha256_bytes(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def load_forward_module():
    """导入既有前向模块（dataclass 需要先注册 sys.modules）。"""
    sys.path.insert(0, str(WORKTREE)) if str(WORKTREE) not in sys.path else None
    sys.path.insert(0, str(WORKTREE / "verification")) if str(WORKTREE / "verification") not in sys.path else None
    spec = importlib.util.spec_from_file_location("d2fwd_bridge", FORWARD_MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["d2fwd_bridge"] = module
    spec.loader.exec_module(module)
    return module


def load_t25_preprocessed_forward_input(path: Path, width: int, height: int, module: object,
                                        expected_sha256: str | None) -> tuple[np.ndarray, dict[str, object]]:
    """复用 T25 冻结 RGB→INT8 预处理，并验证 forward_one 的回量化字节不变。"""
    if str(WORKTREE) not in sys.path:
        sys.path.insert(0, str(WORKTREE))
    numeric = importlib.import_module("verification.s1_t02_d2_numeric_reference")
    delivery = importlib.import_module("verification.s2a_model_delivery")
    if float(numeric.INPUT_SCALE) != float(module.INPUT_SCALE):
        raise RuntimeError("T25 预处理 scale 与 forward_one INPUT_SCALE 不一致")
    rgb = delivery.decode_rgb(path)
    t25_values = numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), width, height)
    t25_int8 = np.ascontiguousarray(np.asarray(t25_values, dtype=np.int8))
    expected_shape = (3, height, width)
    if t25_int8.shape != expected_shape or int(t25_int8.min()) < -127 or int(t25_int8.max()) > 127:
        raise RuntimeError(f"T25 预处理 INT8 CHW 形状/范围错误：{t25_int8.shape}")
    t25_bytes = t25_int8.tobytes(order="C")
    t25_sha = sha256_bytes(t25_bytes)
    if expected_sha256 is not None and t25_sha != expected_sha256.lower():
        raise RuntimeError(f"T25 预处理输入 SHA 不匹配：expected={expected_sha256} actual={t25_sha}")
    forward_chw = np.ascontiguousarray(t25_int8.astype(np.float64) * np.float64(module.INPUT_SCALE))
    forward_int8 = np.asarray(module.saturate_array(module.round_away_array(
        forward_chw / module.INPUT_SCALE)), dtype=np.int8)
    forward_bytes = np.ascontiguousarray(forward_int8).tobytes(order="C")
    if not np.array_equal(forward_int8, t25_int8):
        raise RuntimeError("forward_one 入口回量化与 T25 预处理 INT8 不逐字节相同")
    float_bytes = forward_chw.tobytes(order="C")
    evidence = {
        "preprocess_oracle": "verification/s1_t02_d2_numeric_reference.py::preprocess_rgb_uint8_to_chw_int8",
        "image_decoder": "verification/s2a_model_delivery.py::decode_rgb",
        "decoded_rgb_shape_hwc": list(rgb.shape),
        "decoded_rgb_dtype": str(rgb.dtype),
        "decoded_rgb_sha256": sha256_bytes(np.ascontiguousarray(rgb).tobytes(order="C")),
        "t25_post_quantization": {"dtype": "int8", "shape_chw": list(t25_int8.shape),
                                  "scale": float(numeric.INPUT_SCALE), "sha256": t25_sha,
                                  "expected_sha256": expected_sha256.lower() if expected_sha256 else None},
        "forward_one_pre_quantization": {"dtype": str(forward_chw.dtype),
                                         "shape_chw": list(forward_chw.shape),
                                         "source": "T25 INT8 values multiplied by frozen INPUT_SCALE",
                                         "raw_data_sha256": sha256_bytes(float_bytes)},
        "forward_one_post_quantization": {"dtype": str(forward_int8.dtype),
                                          "shape_chw": list(forward_int8.shape),
                                          "scale": float(module.INPUT_SCALE),
                                          "quantizer": "round_away_array(x / INPUT_SCALE), saturate_array([-127,127])",
                                          "raw_data_sha256": sha256_bytes(forward_bytes),
                                          "bytewise_equal_to_t25": True},
        "cross_dtype_hash_comparison_performed": False,
    }
    return forward_chw, evidence


def load_d9_module():
    """导入既有 D9 解码器及其冻结 D6 NMS 依赖。"""
    verify_dir = str(WORKTREE / "verification")
    if verify_dir not in sys.path:
        sys.path.insert(0, verify_dir)
    spec = importlib.util.spec_from_file_location("d9_yolo_decode_bridge", D9_MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["d9_yolo_decode_bridge"] = module
    spec.loader.exec_module(module)
    return module


def git_head(path: Path) -> str:
    """读取指定工作树当前 HEAD；无法读取时向上抛错。"""
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(path), capture_output=True,
                            check=True, text=True, encoding="utf-8")
    return result.stdout.strip().lower()


def git_is_ancestor(path: Path, ancestor: str, descendant: str) -> bool:
    """固定上游提交必须是观察到的工作树 HEAD 祖先；不固定移动中的 HEAD。"""
    result = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=str(path),
                            capture_output=True, check=False, text=True, encoding="utf-8")
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "git merge-base --is-ancestor 失败")
    return result.returncode == 0


def current_yolo_head_bindings(sections: list[object], d9: object,
                               reference_heads: dict[str, object]) -> tuple[list[tuple[int, str]], dict[str, dict[str, object]]]:
    """由 cfg 执行层序、D9 栅格与冻结 T29 映射绑定两个真实 YOLO 输出。"""
    yolo_layers = [(index, section) for index, section in enumerate(sections[1:])
                   if section.kind == "yolo"]
    specs = sorted(d9.HEAD_SPECS, key=lambda item: item.grid_width)
    if len(yolo_layers) != 2 or len(specs) != 2:
        raise RuntimeError("必须恰有两个 cfg YOLO 层和两个 D9 head spec")
    head_names = ("head13", "head26")
    bindings: dict[str, dict[str, object]] = {}
    for (layer_index, section), spec, head_name in zip(yolo_layers, specs, head_names):
        expected = reference_heads.get(head_name)
        if not isinstance(expected, dict):
            raise RuntimeError(f"T29 缺少冻结头绑定：{head_name}")
        source_layer = layer_index - 1
        expected_shape = [1, 30, int(spec.grid_height), int(spec.grid_width)]
        mask = tuple(int(value.strip()) for value in section.options.get("mask", "").split(",") if value.strip())
        conv_options = sections[1:][source_layer].options if source_layer >= 0 else {}
        actual = {
            "yolo_layer_index": layer_index,
            "source_convolution_layer_index": source_layer,
            "grid_shape": [int(spec.grid_height), int(spec.grid_width)],
            "mask": list(mask),
            "classes": int(section.options.get("classes", "-1")),
            "filters": int(conv_options.get("filters", "-1")),
        }
        frozen = {
            "yolo_layer_index": expected.get("yolo_alias_layer_index"),
            "source_convolution_layer_index": expected.get("source_convolution_layer_index"),
            "shape_nchw": expected.get("shape_nchw"),
            "scale": expected.get("int8_scale"),
            "length_bytes": expected.get("byte_length"),
        }
        if (actual["yolo_layer_index"] != frozen["yolo_layer_index"]
                or actual["source_convolution_layer_index"] != frozen["source_convolution_layer_index"]
                or frozen["shape_nchw"] != expected_shape
                or actual["classes"] != int(d9.CLASS_COUNT)
                or actual["filters"] != 3 * int(d9.ENTRY_COUNT)
                or mask != tuple(spec.anchor_mask)
                or frozen["length_bytes"] != 3 * int(d9.ENTRY_COUNT) * int(spec.grid_height) * int(spec.grid_width)):
            raise RuntimeError(f"cfg、D9 与 T29 head 映射/形状不一致：{head_name} actual={actual} frozen={frozen}")
        bindings[head_name] = {
            "d9_name": spec.name,
            "yolo_layer_index": layer_index,
            "source_convolution_layer_index": source_layer,
            "shape_chw": expected_shape[1:],
            "shape_nchw": expected_shape,
            "mask": list(mask),
            "classes": actual["classes"],
            "scale": float(frozen["scale"]),
            "length_bytes": int(frozen["length_bytes"]),
        }
    metric_layers = [(index, section.kind) for index, section in enumerate(sections[1:])
                     if section.kind in ("convolutional", "yolo")]
    expected_yolo_indices = [item["yolo_layer_index"] for item in bindings.values()]
    if [index for index, kind in metric_layers if kind == "yolo"] != expected_yolo_indices:
        raise RuntimeError("forward_one metric 调用层序不能映射到冻结 YOLO 层")
    return metric_layers, bindings


def capture_forward_heads(module: object, d9: object, image_chw: np.ndarray,
                          sections: list[object], float_layers: dict[int, object],
                          package_layers: dict[int, object], activation_scales: dict[int, float],
                          reference_heads: dict[str, object]) -> tuple[dict[int, object], dict[str, object], dict[str, dict[str, object]]]:
    """只包装既有 metric 调用捕获量化输出，不执行或复制网络数学。"""
    metric_layers, bindings = current_yolo_head_bindings(sections, d9, reference_heads)
    original_metric = module.metric
    call_index = 0
    heads: dict[str, dict[str, object]] = {}

    def observing_metric(float_values: np.ndarray, integer_values: object) -> dict[str, object]:
        nonlocal call_index
        if call_index >= len(metric_layers):
            raise RuntimeError("forward_one 的 metric 调用次数超过 cfg 映射")
        layer_index, kind = metric_layers[call_index]
        call_index += 1
        if kind == "yolo":
            head_name = "head13" if bindings["head13"]["yolo_layer_index"] == layer_index else "head26"
            binding = bindings[head_name]
            values = integer_values.values
            if list(values.shape) != binding["shape_chw"] or str(values.dtype) != "int8":
                raise RuntimeError(f"{head_name} 实际输出 shape/dtype 不符：{values.shape}/{values.dtype}")
            if float(integer_values.scale) != binding["scale"]:
                raise RuntimeError(f"{head_name} 实际输出量化 scale 与 T29 不符：{integer_values.scale}")
            raw = np.ascontiguousarray(values).reshape((3, int(d9.ENTRY_COUNT),
                                                        int(binding["shape_chw"][1]),
                                                        int(binding["shape_chw"][2])))
            heads[head_name] = {"raw_int8": raw, "scale": float(integer_values.scale),
                                "layer_index": layer_index, "shape": list(raw.shape)}
        return original_metric(float_values, integer_values)

    module.metric = observing_metric
    try:
        metrics, details = module.forward_one(image_chw, sections, float_layers,
                                              package_layers, activation_scales)
    finally:
        module.metric = original_metric
    if call_index != len(metric_layers):
        raise RuntimeError(f"forward_one metric 调用次数不符：{call_index}/{len(metric_layers)}")
    if set(heads) != {"head13", "head26"}:
        raise RuntimeError(f"捕获到的 YOLO head 名称集合异常：{sorted(heads)}")
    return metrics, details, heads


def head_hashes(heads: dict[str, dict[str, object]]) -> dict[str, str]:
    """计算 head13/head26 的原始 INT8 字节摘要。"""
    return {name: sha256_bytes(np.ascontiguousarray(heads[name]["raw_int8"]).tobytes())
            for name in ("head13", "head26")}


def decode_heads_with_d9(d9: object, heads: dict[str, dict[str, object]], image_key: str,
                         image_width: int, image_height: int) -> tuple[list[object], int]:
    """按 T29 既有约定反量化 head 并调用 D9 解码与稳定 NMS。"""
    head_logits = {}
    for name, grid in (("head13", "13x13"), ("head26", "26x26")):
        item = heads[name]
        head_logits[grid] = np.asarray(item["raw_int8"], dtype=np.float64) * np.float64(item["scale"])
    nms_counts: list[int] = []
    original_nms = d9.stable_nms

    def observing_nms(predictions: object, *args: object, **kwargs: object) -> list[object]:
        values = list(predictions)
        nms_counts.append(len(values))
        return original_nms(values, *args, **kwargs)

    d9.stable_nms = observing_nms
    try:
        predictions = d9.decode_yolov4_tiny416(
            head_logits, image_key=image_key, image_width=image_width, image_height=image_height,
            score_threshold=T29_SCORE_THRESHOLD)
    finally:
        d9.stable_nms = original_nms
    if len(nms_counts) != 1:
        raise RuntimeError("D9 解码未恰好调用一次既有 stable_nms")
    return predictions, nms_counts[0]


def load_reference_head_tensors(reference_sample: dict[str, object],
                                bindings: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """按独立参考文件逐字节加载冻结校准样本 head；缺路径或哈希即拒绝。"""
    records = reference_sample.get("head_tensors")
    if not isinstance(records, dict) or set(records) != {"head13", "head26"}:
        raise RuntimeError("冻结参考样本没有独立 head13/head26 字节文件")
    result: dict[str, dict[str, object]] = {}
    for name in ("head13", "head26"):
        record = records[name]
        if not isinstance(record, dict):
            raise RuntimeError(f"{name} 参考记录格式非法")
        path = Path(str(record.get("path", "")))
        if not path.is_absolute():
            path = WORKTREE / path
        expected_hash = str(record.get("sha256", "")).lower()
        expected_shape = tuple(bindings[name]["shape_chw"])
        if not path.is_file() or len(expected_hash) != 64 or sha256_file(path) != expected_hash:
            raise RuntimeError(f"{name} 参考字节文件缺失或 SHA 不匹配：{path}")
        raw_bytes = path.read_bytes()
        if len(raw_bytes) != int(bindings[name]["length_bytes"]):
            raise RuntimeError(f"{name} 参考字节长度不符：{len(raw_bytes)}")
        tensor = np.frombuffer(raw_bytes, dtype=np.int8).reshape(expected_shape)
        result[name] = {"raw_int8": tensor, "scale": float(record.get("scale", -1.0)),
                        "path": str(path), "sha256": expected_hash,
                        "shape": list(tensor.shape)}
        if result[name]["scale"] != bindings[name]["scale"]:
            raise RuntimeError(f"{name} 参考 head scale 与冻结 T29 不一致")
    return result


def compare_raw_heads(actual: dict[str, dict[str, object]],
                      expected: dict[str, dict[str, object]]) -> tuple[bool, dict[str, object]]:
    """对冻结 INT8 head 张量做严格形状、类型和逐值比较。"""
    comparisons: dict[str, object] = {}
    passed = set(actual) == set(expected) == {"head13", "head26"}
    for name in ("head13", "head26"):
        if name not in actual or name not in expected:
            comparisons[name] = {"status": "FAIL", "reason": "head 缺失"}
            passed = False
            continue
        left = np.ascontiguousarray(actual[name]["raw_int8"])
        right = np.ascontiguousarray(expected[name]["raw_int8"])
        equal = left.shape == right.shape and left.dtype == np.int8 and right.dtype == np.int8 \
            and np.array_equal(left, right)
        comparisons[name] = {"shape": list(left.shape), "dtype": str(left.dtype),
                             "actual_sha256": sha256_bytes(left.tobytes()),
                             "reference_sha256": sha256_bytes(right.tobytes()),
                             "elementwise_equal": bool(equal)}
        passed = passed and bool(equal)
    return bool(passed), comparisons


def prediction_records(predictions: list[object]) -> list[dict[str, object]]:
    """把既有 D9 Prediction 转成可序列化的检测结果。"""
    return [{"class_id": int(item.class_id), "class_name": str(item.name),
             "score": float(item.confidence), "xyxy": [float(value) for value in item.box],
             "source_order": int(item.source_order)} for item in predictions]


def save_head_bytes(out_dir: Path, prefix: str,
                    heads: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """保存真实捕获的 INT8 检测头字节并记录尺寸、哈希和量化 scale。"""
    records: dict[str, dict[str, object]] = {}
    for name in ("head13", "head26"):
        raw = np.ascontiguousarray(heads[name]["raw_int8"]).tobytes()
        path = out_dir / f"{prefix}_{name}_int8.bin"
        path.write_bytes(raw)
        records[name] = {"path": str(path), "size_bytes": len(raw), "sha256": sha256_bytes(raw),
                         "shape": heads[name]["shape"], "scale": heads[name]["scale"],
                         "source_convolution_layer_index": heads[name]["layer_index"] - 1,
                         "yolo_layer_index": heads[name]["layer_index"]}
    return records


def mutate_one_input_byte(image_chw: np.ndarray) -> tuple[np.ndarray, dict[str, int]]:
    """仅改变 INT8 输入张量一个字节且保持项目规定的数值范围。"""
    changed = np.ascontiguousarray(image_chw).copy()
    flat = changed.reshape(-1)
    index = int(flat.size // 2)
    before = int(flat[index])
    after = before + 1 if before < 127 else before - 1
    flat[index] = np.int8(after)
    if np.count_nonzero(changed != image_chw) != 1:
        raise RuntimeError("输入字节扰动必须且只能改变一个 INT8 元素")
    return changed, {"flat_index": index, "before": before, "after": after}


def probe_cv2_runtimes() -> list[dict[str, object]]:
    """只探测当前已存在解释器，不安装包或改变运行环境。"""
    candidates = [
        Path(sys.executable),
        Path(r"C:\Users\22061\anaconda3\python.exe"),
        Path(r"C:\Users\22061\anaconda3\envs\dl_env\python.exe"),
        Path(r"C:\Users\22061\anaconda3\pkgs\python-3.11.15-h1044e36_0\python.exe"),
        Path(r"C:\Users\22061\anaconda3\pkgs\python-3.7.0-hea74fb7_0\python.exe"),
        Path(r"C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"),
    ]
    result: list[dict[str, object]] = []
    seen: set[str] = set()
    for interpreter in candidates:
        key = str(interpreter).lower()
        if key in seen:
            continue
        seen.add(key)
        if not interpreter.is_file():
            result.append({"interpreter": str(interpreter), "status": "NOT_FOUND"})
            continue
        command = [str(interpreter), "-B", "-c", "import cv2; print(cv2.__version__)"]
        try:
            proc = subprocess.run(command, cwd=str(WORKTREE), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=15, check=False)
            result.append({"interpreter": str(interpreter), "command": command,
                           "exit_code": proc.returncode, "stdout": proc.stdout.strip(),
                           "stderr": proc.stderr.strip(),
                           "status": "AVAILABLE" if proc.returncode == 0 else "UNAVAILABLE"})
        except Exception as exc:
            result.append({"interpreter": str(interpreter), "command": command,
                           "status": "PROBE_ERROR", "error": f"{type(exc).__name__}: {exc}"})
    return result


def run_static_interface_selfcheck(sample_index: int, run_id: str) -> dict[str, object]:
    """只读核验冻结模块、cfg/head 映射、参考来源与校准样本身份。"""
    checks: dict[str, dict[str, object]] = {}

    def add(name: str, ok: bool, detail: dict[str, object]) -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail}

    try:
        w4_head = git_head(WORKTREE)
        w4_branch = subprocess.run(["git", "branch", "--show-current"], cwd=str(WORKTREE),
                                   capture_output=True, check=True, text=True, encoding="utf-8").stdout.strip()
        dbdf_head = git_head(BOUND_T25_T29_TREE)
        package_is_ancestor = git_is_ancestor(BOUND_T25_T29_TREE, TASK25_PACKAGE_COMMIT, dbdf_head)
        frame_is_ancestor = git_is_ancestor(BOUND_T25_T29_TREE, TASK25_FRAME_COMMIT, dbdf_head)
        add("bound_tree_heads", w4_branch == "stage4-infer-prep" and package_is_ancestor and frame_is_ancestor,
            {"w4": {"head_observed_only": w4_head, "branch": w4_branch,
                    "head_is_not_pinned": True},
             "dbdf_t25_t29": {"head_observed_only": dbdf_head,
                              "task25_package_commit": TASK25_PACKAGE_COMMIT,
                              "task25_package_is_ancestor": package_is_ancestor,
                              "task25_frame_commit": TASK25_FRAME_COMMIT,
                              "task25_frame_is_ancestor": frame_is_ancestor},
             "fixed_inputs": "task-25 package/frame commits are immutable; current dbdf HEAD may advance",
             "fail_closed": True})
    except Exception as exc:
        add("bound_tree_heads", False, {"error": f"{type(exc).__name__}: {exc}", "fail_closed": True})

    source_hashes: dict[str, dict[str, str]] = {}
    expected_sources = [
        ("forward_module", FORWARD_MODULE, FORWARD_MODULE_SHA256, FORWARD_MODULE_CONTENT_SHA256),
        ("d9_decoder", D9_MODULE, None, D9_MODULE_LF_SHA256),
        ("d6_nms", D6_MODULE, None, D6_MODULE_LF_SHA256),
        ("t29_generator", T29_GENERATOR, None, T29_GENERATOR_LF_SHA256),
        ("t25_index", T25_INDEX, T25_INDEX_RAW_SHA256, T25_INDEX_LF_SHA256),
        ("t29_reference", T29_REFERENCE, T29_REFERENCE_RAW_SHA256, T29_REFERENCE_LF_SHA256),
    ]
    source_ok = True
    for name, path, expected_raw, expected_lf in expected_sources:
        try:
            actual_raw = sha256_file(path)
            actual_lf = sha256_lf_content(path)
            matches = (expected_raw is None or actual_raw == expected_raw) and actual_lf == expected_lf
            source_ok = source_ok and matches
            source_hashes[name] = {"path": str(path), "raw_sha256": actual_raw,
                                   "lf_content_sha256": actual_lf,
                                   "expected_raw_sha256": expected_raw or "not_pinned",
                                   "expected_lf_content_sha256": expected_lf}
        except Exception as exc:
            source_ok = False
            source_hashes[name] = {"path": str(path), "error": f"{type(exc).__name__}: {exc}"}
    add("module_and_reference_hashes", source_ok, source_hashes)

    cross_tree_files: dict[str, object] = {}
    cross_tree_ok = True
    for label, rel_path, expected_lf in (
        ("t25_index", Path("report/evidence/S2A-T25/cpu_layer_golden_index.json"), T25_INDEX_LF_SHA256),
        ("t29_reference", Path("report/evidence/S2A-T29/cpu_decode_nms_reference.json"), T29_REFERENCE_LF_SHA256),
    ):
        entries = {}
        for tree_name, tree in (("w4", WORKTREE), ("dbdf", BOUND_T25_T29_TREE)):
            path = tree / rel_path
            try:
                actual = sha256_lf_content(path)
                entries[tree_name] = {"path": str(path), "lf_content_sha256": actual}
                cross_tree_ok = cross_tree_ok and actual == expected_lf
            except Exception as exc:
                cross_tree_ok = False
                entries[tree_name] = {"path": str(path), "error": f"{type(exc).__name__}: {exc}"}
        cross_tree_files[label] = entries
    add("cross_tree_t25_t29_content", cross_tree_ok, {"files": cross_tree_files, "fail_closed": True})

    interface_detail: dict[str, object] = {}
    bindings: dict[str, dict[str, object]] = {}
    try:
        d2 = load_forward_module()
        d9 = load_d9_module()
        contract_bindings = resolve_contract_bindings()
        cfg = Path(contract_bindings["cfg"]["path"])
        sections = d2.parse_cfg_sections(cfg)
        t25 = json.loads(T25_INDEX.read_text(encoding="utf-8"))
        t29 = json.loads(T29_REFERENCE.read_text(encoding="utf-8"))
        t29_sample = next((item for item in t29.get("samples", []) if item.get("sample_id") == "test_fist_000"), None)
        if not isinstance(t29_sample, dict):
            raise RuntimeError("T29 缺少已冻结 test_fist_000 示例 head 元数据")
        metric_layers, bindings = current_yolo_head_bindings(sections, d9, t29_sample.get("head_tensors", {}))
        signature = inspect.signature(d9.decode_yolov4_tiny416)
        expected_args = ("head_logits", "image_key", "image_width", "image_height", "score_threshold")
        if not all(name in signature.parameters for name in expected_args):
            raise RuntimeError(f"D9 解码 API 参数变化：{signature}")
        interface_detail = {
            "forward_api": {"name": "forward_one", "return_contract": "metrics, details(integer_stats); heads observed through existing metric callback"},
            "metric_call_layer_count": len(metric_layers),
            "metric_call_sequence_sha256": canonical_digest([[index, kind] for index, kind in metric_layers]),
            "head_mapping": bindings,
            "d9_api": {"name": "decode_yolov4_tiny416", "signature": str(signature),
                       "score_threshold": T29_SCORE_THRESHOLD, "head_specs": [
                           {"name": spec.name, "grid_width": spec.grid_width, "grid_height": spec.grid_height,
                            "anchor_mask": list(spec.anchor_mask)} for spec in d9.HEAD_SPECS]},
            "t25_status": t25.get("status"), "t25_samples": len(t25.get("samples", [])),
            "t29_status": t29.get("status"), "t29_samples": len(t29.get("samples", [])),
            "t29_baseline_git_head": t29.get("baseline_git_head"),
            "t29_runtime_git_head": t29.get("runtime_git_head"),
        }
        yolo_layer_names = {int(value["yolo_layer_index"]): name for name, value in bindings.items()}

        class SyntheticForward:
            """只模拟 metric 回调顺序的接口夹具，不执行网络层计算。"""
            metric = staticmethod(d2.metric)

            def forward_one(self, image_chw: np.ndarray, parsed_sections: list[object],
                            float_params: dict[int, object], package_params: dict[int, object],
                            scales: dict[int, float]) -> tuple[dict[int, object], dict[str, object]]:
                for layer_index, kind in metric_layers:
                    if kind == "yolo":
                        name = yolo_layer_names[layer_index]
                        shape = bindings[name]["shape_chw"]
                        values = np.full(shape, -127, dtype=np.int8)
                        scale = float(bindings[name]["scale"])
                    else:
                        values = np.zeros((1,), dtype=np.int8)
                        scale = 1.0
                    integer = types.SimpleNamespace(values=values, scale=scale)
                    self.metric(np.zeros(values.shape, dtype=np.float64), integer)
                return {}, {"integer_stats": {}}

        synthetic = SyntheticForward()
        synthetic_input = np.zeros((3, 416, 416), dtype=np.float32)
        _, _, synthetic_heads_a = capture_forward_heads(
            synthetic, d9, synthetic_input, sections, {}, {}, {}, t29_sample["head_tensors"])
        _, _, synthetic_heads_b = capture_forward_heads(
            synthetic, d9, synthetic_input, sections, {}, {}, {}, t29_sample["head_tensors"])
        synthetic_hashes_a = head_hashes(synthetic_heads_a)
        synthetic_hashes_b = head_hashes(synthetic_heads_b)
        original_nms = d9.stable_nms
        synthetic_predictions, synthetic_candidates = decode_heads_with_d9(
            d9, synthetic_heads_a, "synthetic-interface-only", 1280, 720)
        interface_detail["synthetic_hook_smoke"] = {
            "inference_executed": False, "network_math_copied": False,
            "metric_call_layer_count": len(metric_layers),
            "captured_head_shapes": {name: value["shape"] for name, value in synthetic_heads_a.items()},
            "repeat_head_hashes_equal": synthetic_hashes_a == synthetic_hashes_b,
            "d9_api_invoked": True, "synthetic_raw_candidate_count": synthetic_candidates,
            "synthetic_prediction_count": len(synthetic_predictions),
            "stable_nms_restored": d9.stable_nms is original_nms,
        }
        if (synthetic_hashes_a != synthetic_hashes_b or synthetic_candidates != 0
                or synthetic_predictions or d9.stable_nms is not original_nms):
            raise RuntimeError("合成 metric/D9 接口自检失败")
        add("forward_head_and_d9_interface", True, interface_detail)
    except Exception as exc:
        add("forward_head_and_d9_interface", False,
            {"error": f"{type(exc).__name__}: {exc}", "fail_closed": True})

    reference_detail: dict[str, object] = {}
    reference_ok = False
    try:
        d2 = load_forward_module()
        reference = json.loads(REFERENCE_RUN.read_text(encoding="utf-8"))
        sample_paths = d2.read_calibration_list(Path(resolve_contract_bindings()["calibration_list"]["path"]), 512)
        if sample_index < 0 or sample_index >= len(sample_paths):
            raise RuntimeError(f"冻结校准样本序号越界：{sample_index}/{len(sample_paths)}")
        sample_path = sample_paths[sample_index]
        sample_sha = sha256_file(sample_path)
        rows = [item for item in reference.get("samples", []) if item.get("sample_index") == sample_index]
        ref_sample = rows[0] if len(rows) == 1 else None
        ref_sha = str(ref_sample.get("sha256", "")).lower() if ref_sample else ""
        ref_path = str(ref_sample.get("path", "")) if ref_sample else ""
        raw_keys = ("head_tensors", "heads", "raw_heads")
        ref_heads = next((ref_sample.get(key) for key in raw_keys
                          if isinstance(ref_sample, dict) and ref_sample.get(key)), None)
        t25 = json.loads(T25_INDEX.read_text(encoding="utf-8"))
        t25_image_shas = {str(item.get("original_input", {}).get("sha256", "")).lower()
                          for item in t25.get("samples", []) if isinstance(item, dict)}
        reference_ok = bool(ref_sample and ref_sha == sample_sha
                            and Path(ref_path).resolve() == sample_path.resolve() and isinstance(ref_heads, dict)
                            and set(ref_heads) == {"head13", "head26"})
        reference_detail = {
            "sample_index": sample_index, "sample_path": str(sample_path), "sample_sha256": sample_sha,
            "history_entry_count": len(rows), "history_sample_path": ref_path,
            "history_sample_sha256": ref_sha,
            "history_fields": sorted(ref_sample.keys()) if isinstance(ref_sample, dict) else [],
            "history_contains_independent_raw_heads": bool(isinstance(ref_heads, dict)),
            "matching_t25_image_sha": sample_sha in t25_image_shas,
            "value_by_value_head_reference_available": reference_ok,
            "metrics_are_not_accepted_as_head_reference": True,
        }
    except Exception as exc:
        reference_detail = {"error": f"{type(exc).__name__}: {exc}",
                            "value_by_value_head_reference_available": False}
    checks["frozen_calibration_head_oracle"] = {
        "status": "PASS" if reference_ok else "BLOCKED", "detail": reference_detail}

    static_failures = [name for name, item in checks.items() if item["status"] == "FAIL"]
    task_blockers = []
    if not reference_ok:
        task_blockers.append("冻结校准样本缺少独立 raw head13/head26 黄金，历史 metrics/integer_stats 不作为替代")
    return {
        "task_id": "S4-CTRL/S4-T26", "run_id": run_id, "checker_version": BRIDGE_VERSION,
        "status": "PASS" if not static_failures else "FAIL",
        "static_checks": checks, "static_failures": static_failures,
        "task_blockers": task_blockers, "runtime_forward": "NOT_RUN",
        "replay_frame_inference": "NOT_RUN", "frozen_sample_inference": "NOT_RUN",
        "head_bindings": bindings, "generated_utc8": now_cn(),
    }


def source_hashes_for_manifest(preflight: dict[str, object]) -> dict[str, object]:
    """提取静态检查中已核验的输入文件哈希。"""
    checks = preflight.get("static_checks", {})
    if not isinstance(checks, dict):
        return {}
    item = checks.get("module_and_reference_hashes", {})
    return item.get("detail", {}) if isinstance(item, dict) else {}


def pre_run_snapshot_path(out_dir: Path) -> Path:
    """返回当前 RunId 内最明确的运行前源码快照。"""
    for name in ("replay_forward_bridge.py.pre_run_final", "replay_forward_bridge.py.pre_run",
                 "replay_forward_bridge.py.pre_repair"):
        candidate = out_dir / name
        if candidate.is_file():
            return candidate
    raise RuntimeError("RunId 中缺少桥接源码运行前快照")


def write_static_failure(out_dir: Path, started: float, preflight: dict[str, object],
                         interpreter_probes: list[dict[str, object]]) -> int:
    """把冻结源、树 HEAD 或接口映射漂移记为 FAIL 并立即停止。"""
    elapsed = time.perf_counter() - started
    command = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    emit("[FAIL] 静态冻结输入/HEAD/API 自检失败；推理与解码均未运行")
    report = {
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": BRIDGE_VERSION,
        "status": "FAIL", "exit_code": 1, "generated_utc8": now_cn(), "elapsed_seconds": elapsed,
        "command": command, "worktree": str(WORKTREE),
        "baseline": {"head_observed_only": git_head(WORKTREE), "branch": "stage4-infer-prep"},
        "hardware_execution": "NOT_RUN", "real_frozen_sample_inference": "NOT_RUN",
        "replay_frame_forward": "NOT_RUN", "preflight": preflight,
        "runtime_interpreter_probes": interpreter_probes,
        "limitations": ["静态冻结输入或 head 映射自检失败，立即 fail-closed；没有推理结果。"],
    }
    result_path = out_dir / "replay_forward_bridge_result.json"
    result_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "delivery_manifest.json":
            outputs[path.name] = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "task_id": "S4-CTRL/S4-T26", "run_id": out_dir.name, "status": "FAIL", "exit_code": 1,
        "worktree": str(WORKTREE), "baseline": report["baseline"], "command": command,
        "elapsed_seconds": elapsed,
        "source": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve()),
                   "pre_run_snapshot": str(pre_run_snapshot_path(out_dir)),
                   "pre_run_snapshot_sha256": sha256_file(pre_run_snapshot_path(out_dir))},
        "inputs": {"source_hashes": source_hashes_for_manifest(preflight),
                   "tree_heads": preflight.get("static_checks", {}).get("bound_tree_heads", {}).get("detail")},
        "outputs": outputs, "static_failures": preflight.get("static_failures", []),
        "real_frozen_sample_inference": "NOT_RUN", "replay_frame_forward": "NOT_RUN",
    }
    (out_dir / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1


def resolve_contract_bindings() -> dict[str, dict[str, str]]:
    """从 S4-A 契约读取 cfg/weights/gf8/校准清单 的路径与 SHA（不硬编码）。"""
    contract = json.loads(S4A_CONTRACT.read_text(encoding="utf-8"))
    wanted = {
        "cfg": "gesture_yolov4_tiny_416_d8_formal.cfg",
        "weights": "gesture_yolov4_tiny_416_d8_formal_6000.weights",
        "gf8_package": "gesture_yolov4_tiny_416_int8_weights.gf8",
        "calibration_list": "calibration.list",
    }
    found: dict[str, dict[str, str]] = {}
    for entry in contract.get("upstream_bindings", []):
        path = str(entry.get("path", ""))
        for key, suffix in wanted.items():
            if path.endswith(suffix):
                found[key] = {"path": path, "sha256": str(entry.get("sha256", "")).lower()}
    missing = [k for k in wanted if k not in found]
    if missing:
        raise SystemExit(f"[FAIL] S4-A 契约缺少绑定：{missing}")
    return found


def verify(path: Path, expected: str, label: str) -> str:
    """校验文件存在的 SHA；不符即 fail-closed。"""
    if not path.is_file():
        raise SystemExit(f"[FAIL] {label} 不存在：{path}")
    actual = sha256_file(path)
    if actual != expected.lower():
        raise SystemExit(f"[FAIL] {label} SHA 不符：expected={expected} actual={actual}")
    return actual


def reference_input_diffs(reference: dict[str, object], bindings: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """核对已保存参考结果声明的冻结输入与本次绑定逐项相同。"""
    diffs: list[dict[str, str]] = []
    inputs = reference.get("inputs")
    if not isinstance(inputs, dict):
        return [{"field": "inputs", "expected": "object", "actual": type(inputs).__name__}]
    key_map = {
        "cfg": "cfg",
        "weights": "weights",
        "weight_package": "gf8_package",
        "calibration_list": "calibration_list",
    }
    for reference_key, binding_key in key_map.items():
        expected = bindings[binding_key]["sha256"].lower()
        entry = inputs.get(reference_key)
        actual = str(entry.get("sha256", "")).lower() if isinstance(entry, dict) else ""
        if not actual or actual != expected:
            diffs.append({"field": f"inputs.{reference_key}.sha256", "expected": expected, "actual": actual})
    activation_entry = inputs.get("activation_report")
    activation_hash = str(activation_entry.get("sha256", "")).lower() if isinstance(activation_entry, dict) else ""
    if activation_hash != ACTIVATION_REPORT_CONTENT_SHA256:
        diffs.append({"field": "inputs.activation_report.sha256",
                      "expected": ACTIVATION_REPORT_CONTENT_SHA256, "actual": activation_hash})
    weight_report_entry = inputs.get("weight_report")
    weight_report_hash = str(weight_report_entry.get("sha256", "")).lower() \
        if isinstance(weight_report_entry, dict) else ""
    if weight_report_hash != WEIGHT_REPORT_SHA256:
        diffs.append({"field": "inputs.weight_report.sha256", "expected": WEIGHT_REPORT_SHA256,
                      "actual": weight_report_hash})
    tool_entry = reference.get("tool")
    tool_hash = str(tool_entry.get("sha256", "")).lower() if isinstance(tool_entry, dict) else ""
    if tool_hash != FORWARD_MODULE_CONTENT_SHA256:
        diffs.append({"field": "tool.sha256", "expected": FORWARD_MODULE_CONTENT_SHA256, "actual": tool_hash})
    if reference.get("status") != REFERENCE_STATUS:
        diffs.append({"field": "status", "expected": REFERENCE_STATUS, "actual": str(reference.get("status"))})
    return diffs


def decode_png_exact(encoded: bytes) -> np.ndarray:
    """按原始字节解码 PNG（不做任何转换/缩放）。"""
    import cv2
    array = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if array is None:
        raise SystemExit("[FAIL] PNG 解码失败")
    return array


def write_runtime_blocked(out_dir: Path, started: float, preflight: dict[str, object],
                          interpreter_probes: list[dict[str, object]], cv2_error: str | None) -> int:
    """记录运行依赖或独立黄金缺失；任何受阻结果均不伪造成推理产物。"""
    elapsed = time.perf_counter() - started
    command = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    blockers = list(preflight.get("task_blockers", []))
    if cv2_error:
        blockers.append("当前执行解释器无法导入 cv2：" + cv2_error)
    emit("[BLOCKED] " + "；".join(blockers))
    emit("[BLOCKED] 冻结校准样本前向、回放帧前向、heads 对照和解码/NMS 均为 NOT_RUN")
    preflight_path = out_dir / "preflight_verification.json"
    report = {
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": BRIDGE_VERSION,
        "status": "BLOCKED", "exit_code": 2, "generated_utc8": now_cn(), "elapsed_seconds": elapsed,
        "command": command, "worktree": str(WORKTREE),
        "baseline": {"head_observed_only": git_head(WORKTREE), "branch": "stage4-infer-prep"},
        "bound_tree_heads": preflight["static_checks"].get("bound_tree_heads", {}).get("detail"),
        "cross_tree_t25_t29": preflight["static_checks"].get("cross_tree_t25_t29_content", {}).get("detail"),
        "hardware_execution": "NOT_RUN", "real_frozen_sample_inference": "NOT_RUN",
        "frozen_sample_heads": "NOT_RUN", "frozen_sample_decode_nms": "NOT_RUN",
        "replay_frame_forward": "NOT_RUN", "replay_frame_heads": "NOT_RUN",
        "replay_frame_decode_nms": "NOT_RUN", "negative_control_wrong_scale": "NOT_RUN",
        "negative_control_one_byte_input": "NOT_RUN", "png_pixel_roundtrip_a": "NOT_RUN",
        "png_pixel_roundtrip_b": "NOT_RUN", "preflight": str(preflight_path),
        "preflight_sha256": sha256_file(preflight_path),
        "runtime_interpreter_probes": interpreter_probes,
        "cv2_runtime_available": cv2_error is None,
        "checks": preflight.get("static_checks", {}), "failures": preflight.get("static_failures", []),
        "blocking_reasons": blockers,
        "limitations": [
            "本次未执行任何冻结样本或回放帧推理、heads 生成、D9 解码/NMS、负向对照或 PNG 往返。",
            "r01-r06 的历史证据保持原样；当前 r07 只含源码快照、静态接口检查和受阻记录。",
            "历史前向 JSON 只含 metrics/integer_stats，不能充当 raw head13/head26 或检测结果黄金。",
            "尚无与冻结校准样本相同 SHA 的独立 heads 与逐值解码参考；需要新增受冻结来源绑定的黄金输入。",
            "无板卡、摄像头、Vivado 或其他硬件操作。",
        ],
        "versions": {"python": sys.version, "numpy": np.__version__, "platform": platform.platform()},
    }
    result_path = out_dir / "replay_forward_bridge_result.json"
    result_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = {}
    for path in sorted(out_dir.iterdir()):
        if path.is_file() and path.name != "delivery_manifest.json":
            outputs[path.name] = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "task_id": "S4-CTRL/S4-T26", "run_id": out_dir.name, "status": "BLOCKED", "exit_code": 2,
        "worktree": str(WORKTREE), "baseline": report["baseline"], "command": command,
        "elapsed_seconds": elapsed,
        "source": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve()),
                   "pre_run_snapshot": str(pre_run_snapshot_path(out_dir)),
                   "pre_run_snapshot_sha256": sha256_file(pre_run_snapshot_path(out_dir))},
        "inputs": {"forward_module": source_hashes_for_manifest(preflight),
                   "tree_heads": report["bound_tree_heads"], "cross_tree_t25_t29": report["cross_tree_t25_t29"]},
        "outputs": outputs, "blocking_reasons": blockers,
        "real_frozen_sample_inference": "NOT_RUN", "replay_frame_forward": "NOT_RUN",
        "limitations": report["limitations"],
    }
    (out_dir / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 2


def _legacy_main_r09() -> int:
    """执行双路无损比对 → 冻结样本对拍 → 回放帧前向。"""
    parser = argparse.ArgumentParser(description="离线真实彩色链输入张量驱动前向桥（离线等价）")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--sample-index", type=int, default=0, help="校准清单中可与已保存结果精确对应的样本序号")
    args = parser.parse_args()
    started = time.perf_counter()

    out_dir: Path = args.run_dir
    allowed_existing = {"replay_forward_bridge.py.pre_repair", "repair_source_snapshot_manifest.json",
                        "replay_forward_bridge.py.pre_run", "source_snapshot_manifest.json",
                        "replay_forward_bridge.py.pre_run_final", "source_snapshot_manifest_final.json"}
    existing_names = {path.name for path in out_dir.iterdir()} if out_dir.exists() else set()
    if existing_names - allowed_existing:
        print(f"[FAIL] r07 目录含不属于本轮的文件：{sorted(existing_names - allowed_existing)}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = WORKTREE / "tmp" / "4" / "S4-CTRL" / out_dir.name / "tmp_png"
    if tmp_dir.exists() and any(tmp_dir.iterdir()):
        print(f"[FAIL] 临时目录非空：{tmp_dir}")
        return 2
    tmp_dir.mkdir(parents=True, exist_ok=True)
    global LOG_PATH
    LOG_PATH = out_dir / "console.log"

    preflight = run_static_interface_selfcheck(args.sample_index, out_dir.name)
    interpreter_probes = probe_cv2_runtimes()
    preflight["runtime_interpreter_probes"] = interpreter_probes
    preflight["bridge_source"] = {"path": str(Path(__file__).resolve()), "version": BRIDGE_VERSION,
                                  "sha256": sha256_file(Path(__file__).resolve())}
    preflight["command"] = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    preflight_path = out_dir / "preflight_verification.json"
    preflight_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    emit(f"[STATIC] 静态检查 status={preflight['status']} failures={preflight['static_failures']}")
    for probe in interpreter_probes:
        emit(f"[RUNTIME_PROBE] {probe.get('interpreter')} status={probe.get('status')} exit={probe.get('exit_code')}")
    if preflight.get("static_failures"):
        return write_static_failure(out_dir, started, preflight, interpreter_probes)

    try:
        import cv2
    except Exception as exc:
        return write_runtime_blocked(out_dir, started, preflight, interpreter_probes,
                                     f"{type(exc).__name__}: {exc}")
    if preflight.get("task_blockers"):
        return write_runtime_blocked(out_dir, started, preflight, interpreter_probes, None)
    module = load_forward_module()
    d9 = load_d9_module()
    t29_report = json.loads(T29_REFERENCE.read_text(encoding="utf-8"))
    t29_sample = next(item for item in t29_report["samples"] if item.get("sample_id") == "test_fist_000")
    reference_heads_meta = t29_sample["head_tensors"]
    checks: dict[str, dict[str, object]] = {}
    failures: list[str] = []

    def record(name: str, ok: bool, detail: dict[str, object], note: str = "") -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail, "note": note}
        if not ok:
            failures.append(name)

    # 0. 冻结件身份（fail-closed）
    current_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=WORKTREE,
                                 capture_output=True, check=True, text=True).stdout.strip()
    current_branch = subprocess.run(["git", "branch", "--show-current"], cwd=WORKTREE,
                                    capture_output=True, check=True, text=True).stdout.strip()
    if current_branch != "stage4-infer-prep":
        raise SystemExit(f"[FAIL] 工作树分支不符：head_observed={current_head} branch={current_branch}")
    snapshot_sha = verify(SOURCE_SNAPSHOT, SOURCE_SNAPSHOT_SHA256, "原稿快照")
    contract_sha = verify(S4A_CONTRACT, S4A_CONTRACT_SHA256, "S4-A 契约")
    bindings = resolve_contract_bindings()
    versions = {
        "python": sys.version, "numpy": np.__version__, "cv2": cv2.__version__,
        "platform": platform.platform(),
    }
    forward_sha = verify(FORWARD_MODULE, FORWARD_MODULE_SHA256, "前向模块")
    forward_content_sha = sha256_lf_content(FORWARD_MODULE)
    if forward_content_sha != FORWARD_MODULE_CONTENT_SHA256:
        raise SystemExit(f"[FAIL] 前向模块 LF 内容 SHA 不符：expected={FORWARD_MODULE_CONTENT_SHA256} actual={forward_content_sha}")
    activation_sha = verify(ACTIVATION_REPORT, ACTIVATION_REPORT_SHA256, "激活校准报告")
    activation_content_sha = sha256_lf_content(ACTIVATION_REPORT)
    if activation_content_sha != ACTIVATION_REPORT_CONTENT_SHA256:
        raise SystemExit(f"[FAIL] 激活报告 LF 内容 SHA 不符：expected={ACTIVATION_REPORT_CONTENT_SHA256} actual={activation_content_sha}")
    reference_sha = verify(REFERENCE_RUN, REFERENCE_RUN_SHA256, "既有前向结果")
    reference_content_sha = sha256_lf_content(REFERENCE_RUN)
    if reference_content_sha != REFERENCE_RUN_CONTENT_SHA256:
        raise SystemExit(f"[FAIL] 既有前向结果 LF 内容 SHA 不符：expected={REFERENCE_RUN_CONTENT_SHA256} actual={reference_content_sha}")
    identity = {
        "s4a_contract": {"path": str(S4A_CONTRACT), "sha256": contract_sha},
        "forward_module": {"path": str(FORWARD_MODULE), "sha256": forward_sha,
                           "lf_content_sha256": forward_content_sha},
        "d9_decoder": {"path": str(D9_MODULE), "sha256": sha256_file(D9_MODULE),
                       "lf_content_sha256": sha256_lf_content(D9_MODULE)},
        "d6_nms": {"path": str(D6_MODULE), "sha256": sha256_file(D6_MODULE),
                   "lf_content_sha256": sha256_lf_content(D6_MODULE)},
        "t25_index": {"path": str(T25_INDEX), "sha256": sha256_file(T25_INDEX),
                      "lf_content_sha256": sha256_lf_content(T25_INDEX)},
        "t29_reference": {"path": str(T29_REFERENCE), "sha256": sha256_file(T29_REFERENCE),
                           "lf_content_sha256": sha256_lf_content(T29_REFERENCE)},
        "weight_report": {"path": str(WEIGHT_REPORT),
                          "sha256": verify(WEIGHT_REPORT, WEIGHT_REPORT_SHA256, "量化权重报告")},
        "activation_report": {"path": str(ACTIVATION_REPORT), "sha256": activation_sha,
                              "lf_content_sha256": activation_content_sha},
        "reference_run": {"path": str(REFERENCE_RUN), "sha256": reference_sha,
                          "lf_content_sha256": reference_content_sha},
        "source_snapshot": {"path": str(SOURCE_SNAPSHOT),
                            "sha256": snapshot_sha},
        "baseline": {"head_observed_only": current_head, "branch": current_branch},
        "bound_tree_heads": checks.get("bound_tree_heads", {}).get("detail", {}),
    }
    for key, entry in bindings.items():
        identity[key] = {"path": entry["path"], "sha256": verify(Path(entry["path"]), entry["sha256"], key)}
    identity["replay_frame"] = {"path": str(REPLAY_FRAME), "sha256": verify(REPLAY_FRAME, REPLAY_FRAME_SHA256, "回放帧")}
    reference = json.loads(REFERENCE_RUN.read_text(encoding="utf-8"))
    reference_diffs = reference_input_diffs(reference, bindings)
    record("frozen_identity", True, identity,
           "激活报告、既有结果与前向模块按 raw SHA 和 LF 内容 SHA 双重固定")
    record("reference_provenance", not reference_diffs,
           {"reference_run_sha256": reference_sha, "activation_report_content_sha256": activation_content_sha,
            "diffs": reference_diffs},
           "参考输入需与本次 S4-A 冻结参数、激活报告及前向模块内容逐项一致")

    # 1. 装载冻结参数（全部走既有函数）
    cfg = Path(bindings["cfg"]["path"])
    weights = Path(bindings["weights"]["path"])
    gf8 = Path(bindings["gf8_package"]["path"])
    calib = Path(bindings["calibration_list"]["path"])
    sections = module.parse_cfg_sections(cfg)
    float_layers = module.read_fused_float_layers(cfg, weights)
    header, package_layers = module.parse_package(gf8)
    activation_scales = module.load_activation_scales(ACTIVATION_REPORT, cfg, weights, calib)
    _, head_bindings = current_yolo_head_bindings(sections, d9, reference_heads_meta)
    record("load_frozen_parameters",
           header.get("width") == 416 and header.get("height") == 416 and header.get("channels") == 3
           and set(package_layers) == set(float_layers) == set(activation_scales),
           {"package_header": header, "layers": len(package_layers),
            "input_scale": float(module.INPUT_SCALE), "activation_layer_count": len(activation_scales),
            "activation_scales": {str(k): float(v) for k, v in sorted(activation_scales.items())},
            "activation_scales_digest": canonical_digest({str(k): float(v) for k, v in sorted(activation_scales.items())})})

    # 2. tmp PNG 双路无损比对（边界 7）
    frame_bytes = REPLAY_FRAME.read_bytes()
    side = int(round((len(frame_bytes) / 3 / 720) ** 0.5 * 720))  # 1280x720 => 显式校验
    frame_bgr = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(720, 1280, 3)
    ok_encode_a, enc_a = cv2.imencode(".png", frame_bgr, [cv2.IMWRITE_PNG_COMPRESSION, PNG_COMPRESSION])
    frame_rgb_inmem = frame_bgr[:, :, ::-1].copy()
    frame_bgr_from_rgb = frame_rgb_inmem[:, :, ::-1].copy()
    ok_encode_b, enc_b = cv2.imencode(".png", frame_bgr_from_rgb,
                                      [cv2.IMWRITE_PNG_COMPRESSION, PNG_COMPRESSION])
    if not (ok_encode_a and ok_encode_b):
        print("[FAIL] PNG 编码失败")
        return 2
    png_a, png_b = tmp_dir / "replay_path_a.png", tmp_dir / "replay_path_b.png"
    png_a.write_bytes(enc_a.tobytes())
    png_b.write_bytes(enc_b.tobytes())
    decoded_a = decode_png_exact(enc_a.tobytes())
    decoded_b = decode_png_exact(enc_b.tobytes())
    pixel_equal_a = bool(decoded_a.shape == frame_bgr.shape and decoded_a.dtype == frame_bgr.dtype
                         and np.array_equal(decoded_a, frame_bgr))
    pixel_equal_b = bool(decoded_b.shape == frame_bgr.shape and decoded_b.dtype == frame_bgr.dtype
                         and np.array_equal(decoded_b, frame_bgr))
    chw_a = module.load_image_chw(png_a, 416, 416)
    chw_b = module.load_image_chw(png_b, 416, 416)
    record("tmp_png_roundtrip_lossless", pixel_equal_a and pixel_equal_b,
           {"png_path_a_sha256": sha256_bytes(enc_a.tobytes()), "png_path_b_sha256": sha256_bytes(enc_b.tobytes()),
            "png_compression": PNG_COMPRESSION, "path_a_imread_unchanged_pixel_equal": pixel_equal_a,
            "path_b_imread_unchanged_pixel_equal": pixel_equal_b,
            "chw_equal": bool(np.array_equal(chw_a, chw_b)),
            "png_is_process_artifact": "PNG 为过程产物，源真值仍是 frame_full.bin"},
           "两路都使用 IMREAD_UNCHANGED 解码并与源 BGR 逐像素比较；CHW 相等只作附加观察")
    record("tmp_png_path_a_pixelwise_source_bgr", pixel_equal_a,
           {"imread_flag": "IMREAD_UNCHANGED", "decoded_shape": list(decoded_a.shape),
            "source_shape": list(frame_bgr.shape), "pixelwise_equal": pixel_equal_a})
    record("tmp_png_path_b_pixelwise_source_bgr", pixel_equal_b,
           {"imread_flag": "IMREAD_UNCHANGED", "decoded_shape": list(decoded_b.shape),
            "source_shape": list(frame_bgr.shape), "pixelwise_equal": pixel_equal_b})

    # 3. 负向对照：有损 JPEG ⇒ CHW 必须不同（证明容器检查有判别力）
    ok_jpeg, enc_jpeg = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 60])
    jpg = tmp_dir / "replay_lossy.jpg"
    jpg.write_bytes(enc_jpeg.tobytes())
    chw_jpeg = module.load_image_chw(jpg, 416, 416)
    record("negative_control_lossy_container", ok_jpeg and not np.array_equal(chw_a, chw_jpeg),
           {"jpeg_sha256": sha256_bytes(enc_jpeg.tobytes()), "chw_differs": bool(not np.array_equal(chw_a, chw_jpeg))})

    # 4. 冻结样本：按序号、规范路径、样本 SHA 定位唯一参考记录
    sample_paths = module.read_calibration_list(calib, 512)
    if args.sample_index < 0 or args.sample_index >= len(sample_paths):
        print(f"[FAIL] sample-index 越界：{args.sample_index} / {len(sample_paths)}")
        return 2
    sample = sample_paths[args.sample_index]
    sample_entries = [item for item in reference.get("samples", [])
                      if item.get("sample_index") == args.sample_index]
    ref_entry = sample_entries[0] if len(sample_entries) == 1 else None
    sample_sha = sha256_file(sample)
    ref_sample_sha = str(ref_entry.get("sha256", "")).lower() if ref_entry else ""
    ref_sample_path = str(ref_entry.get("path", "")) if ref_entry else ""
    same_sample_path = bool(ref_sample_path) and Path(ref_sample_path).resolve() == sample.resolve()
    sample_identity_ok = ref_entry is not None and same_sample_path and ref_sample_sha == sample_sha
    record("frozen_sample_identity", sample_identity_ok,
           {"sample_index": args.sample_index, "sample_path": str(sample), "sample_sha256": sample_sha,
            "reference_entry_count": len(sample_entries), "reference_sample_path": ref_sample_path,
            "reference_sample_sha256": ref_sample_sha},
           "必须按冻结样本序号和完整路径匹配，不使用文件名后缀搜索")

    chw_sample = module.load_image_chw(sample, 416, 416)
    sample_chw_sha = sha256_bytes(chw_sample.tobytes())
    sample_bgr = cv2.imread(str(sample), cv2.IMREAD_COLOR)
    if sample_bgr is None:
        raise RuntimeError(f"无法按冻结预处理输入路径读取校准样本几何：{sample}")
    sample_height, sample_width = sample_bgr.shape[:2]
    reference_sample_heads = load_reference_head_tensors(ref_entry, head_bindings)
    emit("[INFO] 冻结校准样本前向 1/2 并捕获真实 YOLO heads")
    metrics, stats, sample_heads = capture_forward_heads(
        module, d9, chw_sample, sections, float_layers, package_layers, activation_scales, reference_heads_meta)
    sample_head_hashes = head_hashes(sample_heads)
    sample_predictions, sample_candidate_count = decode_heads_with_d9(
        d9, sample_heads, str(sample), sample_width, sample_height)
    sample_prediction_records = prediction_records(sample_predictions)
    emit("[INFO] 冻结校准样本前向 2/2 并重捕获 heads")
    metrics_repeat, stats_repeat, sample_heads_repeat = capture_forward_heads(
        module, d9, chw_sample, sections, float_layers, package_layers, activation_scales, reference_heads_meta)
    repeat_head_hashes = head_hashes(sample_heads_repeat)
    repeat_predictions, repeat_candidate_count = decode_heads_with_d9(
        d9, sample_heads_repeat, str(sample), sample_width, sample_height)
    repeat_prediction_records = prediction_records(repeat_predictions)
    record("reproducible_same_input_same_heads",
           sample_head_hashes == repeat_head_hashes and sample_candidate_count == repeat_candidate_count
           and sample_prediction_records == repeat_prediction_records,
           {"head13_sha256": sample_head_hashes["head13"], "head26_sha256": sample_head_hashes["head26"],
            "repeat_head13_sha256": repeat_head_hashes["head13"],
            "repeat_head26_sha256": repeat_head_hashes["head26"],
            "decoded_results_equal": sample_prediction_records == repeat_prediction_records,
            "raw_candidate_count": sample_candidate_count, "repeat_raw_candidate_count": repeat_candidate_count})

    sample_heads_match, sample_head_comparison = compare_raw_heads(sample_heads, reference_sample_heads)
    reference_predictions, reference_candidate_count = decode_heads_with_d9(
        d9, reference_sample_heads, str(sample), sample_width, sample_height)
    reference_prediction_records = prediction_records(reference_predictions)
    sample_decoded_match = (sample_prediction_records == reference_prediction_records
                            and sample_candidate_count == reference_candidate_count)
    reference_match = bool(sample_identity_ok and not reference_diffs and sample_heads_match and sample_decoded_match)
    record("reconcile_reference_head_values", bool(sample_identity_ok and sample_heads_match),
           {"sample_index": args.sample_index, "sample_sha256": sample_sha,
            "reference_run_sha256": reference_sha, "reference_status": reference.get("status"),
            "per_head": sample_head_comparison,
            "comparison_basis": "逐元素比较独立冻结 INT8 head13/head26 文件；metrics 不作替代"})
    record("reconcile_reference_decoded_results", bool(sample_identity_ok and sample_decoded_match),
           {"raw_candidate_count": sample_candidate_count,
            "reference_raw_candidate_count": reference_candidate_count,
            "predictions": sample_prediction_records,
            "reference_predictions": reference_prediction_records,
            "exact_result_match": sample_decoded_match})

    sample_head_files = save_head_bytes(out_dir, "frozen_sample", sample_heads)
    frozen_sample_result = {
        "task_id": "S4-CTRL/S4-T26", "sample_index": args.sample_index,
        "sample_path": str(sample), "sample_sha256": sample_sha,
        "chw_shape": list(chw_sample.shape), "chw_dtype": str(chw_sample.dtype),
        "chw_tensor_sha256": sample_chw_sha,
        "heads": sample_head_files, "head_sha256": sample_head_hashes,
        "decoded_predictions": sample_prediction_records, "raw_candidate_count_before_nms": sample_candidate_count,
        "supplementary_forward_summaries": {"metrics": metrics, "integer_stats": stats["integer_stats"],
                                             "comparison_role": "diagnostic_only_not_head_oracle"},
        "reference": {"path": str(REFERENCE_RUN), "sha256": reference_sha,
                      "lf_content_sha256": reference_content_sha, "status": reference.get("status"),
                      "comparison_status": "PASS" if reference_match else "FAIL",
                      "comparison_basis": ["head13_int8_elementwise", "head26_int8_elementwise",
                                           "D9_candidate_count", "D9_NMS_predictions"]},
        "marking": {"evidence_kind": "offline_equivalent", "timing_claim_scope": "replay_only",
                    "buffer_scope": "offline_host", "statement": "冻结校准样本离线 INT8 heads 与 D9 解码逐值对照"},
    }
    (out_dir / "frozen_sample_inference_result.json").write_text(
        json.dumps(frozen_sample_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5. 负向对照：只错一个量化 scale，heads 摘要必须变化。
    wrong_scales = dict(activation_scales)
    wrong_scale_layer = min(wrong_scales)
    wrong_scale_before = float(wrong_scales[wrong_scale_layer])
    wrong_scales[wrong_scale_layer] = wrong_scale_before * 1.01
    try:
        emit("[INFO] 单层错 scale 负向对照前向")
        _, _, wrong_scale_heads = capture_forward_heads(
            module, d9, chw_sample, sections, float_layers, package_layers, wrong_scales, reference_heads_meta)
        wrong_scale_hashes = head_hashes(wrong_scale_heads)
        wrong_scale_changed = wrong_scale_hashes != sample_head_hashes
        record("negative_control_wrong_scale", wrong_scale_changed,
               {"changed_layer_index": wrong_scale_layer, "scale_before": wrong_scale_before,
                "scale_after": wrong_scales[wrong_scale_layer], "baseline_head_sha256": sample_head_hashes,
                "perturbed_head_sha256": wrong_scale_hashes,
                "head_hash_changed": wrong_scale_changed})
    except Exception as exc:
        record("negative_control_wrong_scale", False,
               {"changed_layer_index": wrong_scale_layer,
                "error": f"{type(exc).__name__}: {exc}",
                "required_result": "heads 哈希必须改变；拒绝或摘要相同均为 FAIL"})

    # 6. 负向对照：在既有输入量化口径后只改一个 INT8 字节。
    q_original = np.asarray(module.saturate_array(module.round_away_array(
        chw_sample.astype(np.float64) / module.INPUT_SCALE)), dtype=np.int8)
    q_tampered, tamper_detail = mutate_one_input_byte(q_original)
    q_roundtrip = np.asarray(module.saturate_array(module.round_away_array(
        q_tampered.astype(np.float64) * module.INPUT_SCALE / module.INPUT_SCALE)), dtype=np.int8)
    one_byte_only = int(np.count_nonzero(q_original != q_tampered)) == 1
    quantized_roundtrip_exact = bool(np.array_equal(q_roundtrip, q_tampered))
    tampered_chw = q_tampered.astype(np.float64) * module.INPUT_SCALE
    try:
        emit("[INFO] 单字节 INT8 输入负向对照前向")
        _, _, tampered_heads = capture_forward_heads(
            module, d9, tampered_chw, sections, float_layers, package_layers,
            activation_scales, reference_heads_meta)
        tampered_hashes = head_hashes(tampered_heads)
        tampered_head_changed = tampered_hashes != sample_head_hashes
        record("negative_control_one_byte_input", one_byte_only and quantized_roundtrip_exact
               and tampered_head_changed,
               {**tamper_detail, "changed_int8_values": int(np.count_nonzero(q_original != q_tampered)),
                "quantized_roundtrip_exact": quantized_roundtrip_exact,
                "baseline_head_sha256": sample_head_hashes,
                "tampered_head_sha256": tampered_hashes,
                "head_hash_changed": tampered_head_changed})
    except Exception as exc:
        record("negative_control_one_byte_input", False,
               {**tamper_detail, "changed_int8_values": int(np.count_nonzero(q_original != q_tampered)),
                "quantized_roundtrip_exact": quantized_roundtrip_exact,
                "error": f"{type(exc).__name__}: {exc}",
                "required_result": "单字节扰动后的 heads 哈希必须改变"})

    # 7. 回放帧前向（仅在对拍通过且无损比对通过时产出结果）
    gate_ok = all(checks[name]["status"] == "PASS" for name in (
        "frozen_identity", "reference_provenance", "load_frozen_parameters", "tmp_png_roundtrip_lossless",
        "tmp_png_path_a_pixelwise_source_bgr", "tmp_png_path_b_pixelwise_source_bgr",
        "frozen_sample_identity", "reproducible_same_input_same_heads",
        "reconcile_reference_head_values", "reconcile_reference_decoded_results",
        "negative_control_wrong_scale", "negative_control_one_byte_input", "negative_control_lossy_container"))
    if not gate_ok:
        record("replay_frame_forward", False, {"reason": "前置身份、参考结果、无损检查或负向对照未通过，不产出回放结论"})
    else:
        emit("[INFO] 真实冻结回放帧前向 1/2 并捕获 heads")
        m_rep, s_rep, replay_heads = capture_forward_heads(
            module, d9, chw_a, sections, float_layers, package_layers, activation_scales, reference_heads_meta)
        replay_head_hashes = head_hashes(replay_heads)
        replay_predictions, replay_candidate_count = decode_heads_with_d9(
            d9, replay_heads, "s4t26-replay-frame-1", 1280, 720)
        replay_prediction_records = prediction_records(replay_predictions)
        emit("[INFO] 真实冻结回放帧前向 2/2 并重捕获 heads")
        m_rep2, s_rep2, replay_heads_repeat = capture_forward_heads(
            module, d9, chw_a, sections, float_layers, package_layers, activation_scales, reference_heads_meta)
        replay_repeat_hashes = head_hashes(replay_heads_repeat)
        replay_predictions_repeat, replay_repeat_candidate_count = decode_heads_with_d9(
            d9, replay_heads_repeat, "s4t26-replay-frame-1", 1280, 720)
        replay_prediction_records_repeat = prediction_records(replay_predictions_repeat)
        replay_heads_repeatable = (replay_head_hashes == replay_repeat_hashes
                                   and replay_prediction_records == replay_prediction_records_repeat
                                   and replay_candidate_count == replay_repeat_candidate_count)
        record("replay_frame_forward", replay_heads_repeatable,
               {"frame_sha256": REPLAY_FRAME_SHA256, "head_sha256": replay_head_hashes,
                "repeat_head_sha256": replay_repeat_hashes,
                "decoded_predictions_equal": replay_prediction_records == replay_prediction_records_repeat,
                "raw_candidate_count": replay_candidate_count,
                "repeat_raw_candidate_count": replay_repeat_candidate_count,
                "chw_tensor_sha256": sha256_bytes(chw_a.tobytes()), "chw_shape": list(chw_a.shape),
                "chw_dtype": str(chw_a.dtype), "evidence_kind": "offline_replay",
                "range_label": "camera_capture_replay_colour", "timing_claim_scope": "replay_only",
                "buffer_scope": "offline_host"})
        replay_head_files = save_head_bytes(out_dir, "replay_frame", replay_heads)
        session_id = int(sha256_bytes(out_dir.name.encode("utf-8"))[:8], 16)
        replay_package = {
            "task_id": "S4-CTRL/S4-T26", "frame_id": 1, "result_seq": 1,
            "contract_result_key": {"session_id": session_id, "frame_id": 1, "result_seq": 1},
            "stage4a_join_key": None, "ps_log_primary_key": None, "uart_observable_key": None,
            "unavailable_fields": ["stage4a_join_key", "ps_log_primary_key", "uart_observable_key",
                                   "board_pl_timing", "uart_transport", "live_capture_clock"],
            "frame_integrity": {"path": str(REPLAY_FRAME), "sha256": REPLAY_FRAME_SHA256,
                                "length_bytes": len(frame_bytes), "width": 1280, "height": 720,
                                "stride_bytes": 3840, "source_byte_order": "BGR"},
            "heads": replay_head_files, "head_sha256": replay_head_hashes,
            "d9": {"module_path": str(D9_MODULE), "module_sha256": sha256_file(D9_MODULE),
                   "api": "decode_yolov4_tiny416", "score_threshold": T29_SCORE_THRESHOLD,
                   "raw_candidate_count_before_nms": replay_candidate_count,
                   "decoded_predictions": replay_prediction_records},
            "bound_tree_heads": {"w4_head_observed_only": git_head(WORKTREE),
                                 "dbdf_t25_t29_head_observed_only": git_head(BOUND_T25_T29_TREE),
                                 "task25_package_commit": TASK25_PACKAGE_COMMIT,
                                 "task25_frame_commit": TASK25_FRAME_COMMIT},
            "marking": {"evidence_kind": "offline_replay", "range_label": "camera_capture_replay_colour",
                        "timing_claim_scope": "replay_only", "buffer_scope": "offline_host",
                        "statement": "离线主机回放结果，不代表 PL 或实物输出"},
        }
        (out_dir / "replay_frame_result_package.json").write_text(
            json.dumps(replay_package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if not failures else "FAIL"
    exit_code = 0 if status == "PASS" else 1
    elapsed_seconds = time.perf_counter() - started
    report = {
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": BRIDGE_VERSION,
        "status": status, "exit_code": exit_code, "generated_utc8": now_cn(), "elapsed_seconds": elapsed_seconds,
        "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "worktree": str(WORKTREE), "hardware_execution": "NOT_RUN",
        "baseline": {"head_observed_only": git_head(WORKTREE), "branch": "stage4-infer-prep"},
        "marking": {"evidence_kind": "offline_equivalent", "timing_claim_scope": "replay_only",
                    "buffer_scope": "offline_host", "statement": "离线等价，不声明与板上一致"},
        "reuse_declaration": "预处理与网络数学全部来自既有 verification/s1_t02_d2_int8_forward.py（load_image_chw / forward_one），本脚本不复制第二份数学",
        "versions": versions, "identity": identity, "checks": checks, "failures": failures,
        "limitations": [
            "离线等价：不声明与板上/PL 一致；计时结论一律 replay_only。",
            "tmp PNG 仅写入隔离 tmp/4/S4-CTRL/<run_id>/；源真值仍是 dbdf 的 frame_full.bin（SHA-256 939fce22…）。",
            "检测头由既有 forward_one 的 metric 回调捕获；未复制网络数学，D9 只消费捕获的 INT8 heads。",
            "冻结校准样本必须有独立 raw head13/head26 参考文件；历史 metrics/integer_stats 不作为对拍输入。",
            "T25/T29 与既有前向样本各有其绑定用途；不同输入样本的结果不能代替冻结校准样本黄金。",
            "激活报告与既有结果分别以 raw SHA 和 LF 内容 SHA 固定；S4-A 冻结契约本身也按 SHA 固定。",
            "峰值内存未测；本次只运行单张冻结校准样本与单张回放帧，不代表 512 样本统计。",
        ],
    }
    report_path = out_dir / "replay_forward_bridge_result.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, item in checks.items():
        emit(f"[{item['status']}] {name}")
    emit(f"[{status}] 桥接：{len(checks) - len(failures)}/{len(checks)} 通过；失败={failures}")
    artifact_hashes = {}
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            artifact_hashes[str(path.relative_to(out_dir))] = {
                "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    temporary_hashes = {}
    for path in sorted(tmp_dir.rglob("*")):
        if path.is_file():
            temporary_hashes[str(path.relative_to(WORKTREE))] = {
                "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "task_id": "S4-CTRL/S4-T26", "run_id": out_dir.name, "status": status, "exit_code": exit_code,
        "worktree": str(WORKTREE), "baseline": report["baseline"], "command": report["command"],
        "elapsed_seconds": elapsed_seconds, "versions": versions,
        "source": {"path": str(Path(__file__).resolve()), "version": BRIDGE_VERSION,
                   "sha256": sha256_file(Path(__file__).resolve()),
                   "original_snapshot_path": str(SOURCE_SNAPSHOT), "original_snapshot_sha256": snapshot_sha},
        "inputs": identity, "outputs": artifact_hashes, "temporary_artifacts": temporary_hashes,
        "limitations": report["limitations"],
    }
    (out_dir / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return exit_code


def load_rebound_goldens(golden_dir: Path) -> dict[str, dict[str, object]]:
    """按决策、T25/T29 索引与原始文件字节验证双样本材料化黄金。

    `golden_dir` 是**黄金来源目录**（材料化 RunId），与本次运行输出目录解耦：
    黄金字节与其清单 SHA 固定，输出必须写入新 RunId，不得覆盖黄金目录。
    """
    manifest_path = golden_dir / "golden_materialization_manifest.json"
    verify(manifest_path, GOLDEN_MANIFEST_SHA256, "材料化黄金清单")
    verify(REBIND_DECISION, REBIND_DECISION_SHA256, "Wong 批准的黄金改绑决策")
    verify(T25_INDEX, T25_INDEX_RAW_SHA256, "T25 黄金索引")
    verify(T29_REFERENCE, T29_REFERENCE_RAW_SHA256, "T29 检测参考")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "MATERIALIZED_AND_SHA_VERIFIED":
        raise RuntimeError("材料化 manifest 状态不是 SHA 已核验")
    decision_ref = manifest.get("decision_record", {})
    if decision_ref.get("sha256") != REBIND_DECISION_SHA256:
        raise RuntimeError("材料化 manifest 未绑定批准的 decision SHA")

    t25 = json.loads(T25_INDEX.read_text(encoding="utf-8"))
    t29 = json.loads(T29_REFERENCE.read_text(encoding="utf-8"))
    manifest_goldens = manifest.get("goldens")
    if not isinstance(manifest_goldens, list) or len(manifest_goldens) != 4:
        raise RuntimeError("材料化 manifest 必须恰有两样本、四个 raw head 文件")

    expected_gates = (RAW_HEAD_GATE, POSITIVE_DETECTION_GATE)
    result: dict[str, dict[str, object]] = {}
    expected_hashes = {
        "approved_no_hand_001": {
            "head13": "902bb209b285cf46b5adb17e8051035aae0bcc3cca88ee9a7fe650737330ea6d",
            "head26": "f96cca6678114df8e997847bfeb244664a9cb583ebf120990774cb680277e1c2",
        },
        "test_fist_000": {
            "head13": "07b59ca389890e8ac2ac704d97364e9717164becbbe90950dc10e9ed28d2cab6",
            "head26": "7524ce5c60a1a0af3b7275dda1481158f808c1d2354141a66c10de2afe7be14e",
        },
    }

    for gate in expected_gates:
        sample_id = str(gate["sample_id"])
        index = int(gate["sample_index"])
        t25_sample = next((item for item in t25.get("samples", [])
                           if item.get("sample_index") == index and item.get("sample_id") == sample_id), None)
        t29_sample = next((item for item in t29.get("samples", [])
                           if item.get("sample_id") == sample_id), None)
        if not isinstance(t25_sample, dict) or not isinstance(t29_sample, dict):
            raise RuntimeError(f"T25/T29 缺少固定样本：{sample_id}")
        image_path = Path(str(gate["image_path"]))
        image_sha = verify(image_path, str(gate["image_sha256"]), f"批准样本图像 {sample_id}")
        if str(t25_sample.get("original_input", {}).get("sha256", "")).lower() != image_sha:
            raise RuntimeError(f"T25 样本图像 SHA 未绑定批准文件：{sample_id}")

        shard = t25_sample.get("network", {}).get("compressed_shard", {})
        shard_path = T25_SHARDS / Path(str(shard.get("path", ""))).name
        if not shard_path.is_file():
            raise RuntimeError(f"T25 冻结分片缺失：{shard_path}")
        compressed = shard_path.read_bytes()
        compressed_sha = sha256_bytes(compressed)
        if compressed_sha != str(shard.get("sha256", "")).lower():
            raise RuntimeError(f"T25 冻结分片 SHA 不符：{sample_id}")
        raw_stream = zlib.decompress(compressed)
        raw_stream_sha = sha256_bytes(raw_stream)
        if (len(raw_stream) != int(shard.get("decompressed_bytes", -1))
                or raw_stream_sha != str(shard.get("decompressed_sha256", "")).lower()
                or raw_stream_sha != str(t25_sample.get("network", {}).get("raw_stream_sha256", "")).lower()):
            raise RuntimeError(f"T25 解压整包长度或 SHA 不符：{sample_id}")

        sample_heads: dict[str, dict[str, object]] = {}
        for name, layer_index, scale, shape in (
            ("head13", 29, 0.24267549589862975, [1, 30, 13, 13]),
            ("head26", 36, 0.30223452951025775, [1, 30, 26, 26]),
        ):
            material_rows = [item for item in manifest_goldens
                             if item.get("sample_id") == sample_id and item.get("gate") == gate["gate"]
                             and Path(str(item.get("file", ""))).name == f"{sample_id}_{name}.bin"]
            if len(material_rows) != 1:
                raise RuntimeError(f"材料化清单缺失或重复 {sample_id}/{name}")
            material = material_rows[0]
            if material.get("name") != name:
                raise RuntimeError(f"材料化清单 head 名称不符：{sample_id}/{name}")
            t25_tensor = next((item for item in t25_sample.get("network", {}).get("tensors", [])
                               if item.get("layer_index") == layer_index), None)
            t29_tensor = t29_sample.get("head_tensors", {}).get(name)
            if not isinstance(t25_tensor, dict) or not isinstance(t29_tensor, dict):
                raise RuntimeError(f"T25/T29 缺少 {sample_id}/{name} 元数据")
            if (t25_tensor.get("shape_nchw") != shape or t29_tensor.get("shape_nchw") != shape
                    or float(t25_tensor.get("scale", -1.0)) != scale
                    or float(t29_tensor.get("int8_scale", -1.0)) != scale):
                raise RuntimeError(f"冻结 {sample_id}/{name} shape 或 scale 不一致")
            offset = int(t25_tensor.get("byte_offset", -1))
            length = int(t25_tensor.get("byte_length", -1))
            if (offset < 0 or length <= 0 or int(t29_tensor.get("byte_offset", -2)) != offset
                    or int(t29_tensor.get("byte_length", -2)) != length):
                raise RuntimeError(f"冻结 {sample_id}/{name} byte offset/length 不一致")
            expected_sha = expected_hashes[sample_id][name]
            t25_tensor_sha = str(t25_tensor.get("tensor_sha256", "")).lower()
            t29_tensor_sha = str(t29_tensor.get("tensor_sha256", "")).lower()
            if t25_tensor_sha != expected_sha or t29_tensor_sha != expected_sha:
                raise RuntimeError(f"冻结 {sample_id}/{name} T25/T29 SHA 不一致")
            golden_rel = Path(str(material.get("file", "")))
            golden_path = (golden_dir / golden_rel).resolve()
            if not golden_path.is_relative_to(golden_dir.resolve()):
                raise RuntimeError(f"黄金文件路径越出黄金来源目录：{golden_rel}")
            raw_bytes = golden_path.read_bytes()
            exact_slice = raw_stream[offset:offset + length]
            actual_sha = sha256_bytes(raw_bytes)
            if (len(exact_slice) != length or raw_bytes != exact_slice
                    or actual_sha != expected_sha or actual_sha != str(material.get("sha256", "")).lower()
                    or actual_sha != str(material.get("t25_tensor_sha256", "")).lower()
                    or actual_sha != str(material.get("t29_tensor_sha256", "")).lower()
                    or len(raw_bytes) != int(material.get("byte_length", -1))
                    or material.get("shape_nchw") != shape or float(material.get("scale", -1.0)) != scale
                    or str(material.get("t25_shard_sha256", "")).lower() != compressed_sha
                    or str(material.get("t25_decompressed_stream_sha256", "")).lower() != raw_stream_sha):
                raise RuntimeError(f"材料化文件不等于冻结 T25 byte slice：{sample_id}/{name}")
            tensor = np.frombuffer(raw_bytes, dtype=np.int8).reshape((3, 10, shape[2], shape[3]))
            sample_heads[name] = {"raw_int8": tensor, "scale": scale, "path": str(golden_path),
                                  "sha256": actual_sha, "shape": list(tensor.shape)}

        result[sample_id] = {
            "gate": gate, "image_path": image_path, "image_sha256": image_sha,
            "t25_sample": t25_sample, "t29_sample": t29_sample,
            "expected_heads": sample_heads, "t25_shard_sha256": compressed_sha,
            "t25_decompressed_stream_sha256": raw_stream_sha,
        }
    return result


def r10_preflight(run_dir: Path, golden_dir: Path) -> dict[str, object]:
    """先验证批准、固定文件、材料化黄金、树提交与回放时间元数据。

    `run_dir` 仅用于本轮输出；黄金与决策绑定从 `golden_dir` 读取。
    """
    checks: dict[str, dict[str, object]] = {}

    def add(name: str, passed: bool, detail: dict[str, object]) -> None:
        checks[name] = {"status": "PASS" if passed else "BLOCKED", "detail": detail}

    w4_head = git_head(WORKTREE)
    w4_branch = subprocess.run(["git", "branch", "--show-current"], cwd=WORKTREE, capture_output=True,
                                check=True, text=True, encoding="utf-8").stdout.strip()
    baseline_ok = git_is_ancestor(WORKTREE, EXPECTED_W4_BASELINE_COMMIT, w4_head)
    dbdf_head = git_head(BOUND_T25_T29_TREE)
    package_ancestor = git_is_ancestor(BOUND_T25_T29_TREE, TASK25_PACKAGE_COMMIT, dbdf_head)
    frame_ancestor = git_is_ancestor(BOUND_T25_T29_TREE, TASK25_FRAME_COMMIT, dbdf_head)
    add("fixed_baseline_and_moving_dbdf_heads", w4_branch == "stage4-infer-prep" and baseline_ok
        and package_ancestor and frame_ancestor,
        {"w4_head_observed_only": w4_head, "required_branch": "stage4-infer-prep",
         "reviewed_baseline_commit": EXPECTED_W4_BASELINE_COMMIT,
         "reviewed_baseline_is_ancestor": baseline_ok, "dbdf_head_observed_only": dbdf_head,
         "task25_package_commit": TASK25_PACKAGE_COMMIT, "task25_package_is_ancestor": package_ancestor,
         "task25_frame_commit": TASK25_FRAME_COMMIT, "task25_frame_is_ancestor": frame_ancestor})

    hashes: dict[str, object] = {}
    source_ok = True
    for label, path, expected in (
        ("S4-A contract", S4A_CONTRACT, S4A_CONTRACT_SHA256),
        ("forward module", FORWARD_MODULE, FORWARD_MODULE_SHA256),
        ("weight report", WEIGHT_REPORT, WEIGHT_REPORT_SHA256),
        ("activation report", ACTIVATION_REPORT, ACTIVATION_REPORT_SHA256),
        ("T25 index", T25_INDEX, T25_INDEX_RAW_SHA256),
        ("T29 reference", T29_REFERENCE, T29_REFERENCE_RAW_SHA256),
        ("D9 decoder", D9_MODULE, None), ("D6 metrics", D6_MODULE, None),
    ):
        actual = sha256_file(path) if path.is_file() else None
        passed = path.is_file() and (expected is None or actual == expected)
        hashes[label] = {"path": str(path), "expected_sha256": expected or "observed_and_recorded",
                         "actual_sha256": actual, "status": "PASS" if passed else "BLOCKED"}
        source_ok = source_ok and passed
    add("frozen_source_hashes", source_ok, hashes)

    try:
        goldens = load_rebound_goldens(golden_dir)
        add("approved_decision_and_materialized_t25_t29_goldens", True,
            {"decision_path": str(REBIND_DECISION), "decision_sha256": REBIND_DECISION_SHA256,
             "manifest_path": str(golden_dir / "golden_materialization_manifest.json"),
             "manifest_sha256": GOLDEN_MANIFEST_SHA256,
             "gates": {sample_id: {"gate": item["gate"]["gate"],
                                   "image_sha256": item["image_sha256"],
                                   "heads": head_hashes(item["expected_heads"])}
                       for sample_id, item in goldens.items()},
             "old_calibration_sample": OLD_CALIBRATION_SAMPLE,
             "raw_head_negative_is_not_positive_gate": True,
             "current_darknet_control_is_not_golden_source": True})
    except Exception as exc:
        goldens = None
        add("approved_decision_and_materialized_t25_t29_goldens", False,
            {"error": f"{type(exc).__name__}: {exc}", "real_forward_allowed": False})

    try:
        binding_sha = verify(TASK25_REPLAY_BINDING, TASK25_REPLAY_BINDING_SHA256,
                             "task-25 replay input binding")
        replay_binding = json.loads(TASK25_REPLAY_BINDING.read_text(encoding="utf-8"))
        frame_sha = verify(REPLAY_FRAME, REPLAY_FRAME_SHA256, "task-25 replay frame")
        binding_ok = (replay_binding.get("source_commit") == TASK25_FRAME_COMMIT
                      and replay_binding.get("source_frame_sha256") == frame_sha
                      and replay_binding.get("mode") == "offline_replay"
                      and replay_binding.get("timing_claim_scope") == "replay_only"
                      and replay_binding.get("clock_domain") == "replay_documented_wallclock"
                      and replay_binding.get("capture_time_available") is True
                      and isinstance(replay_binding.get("capture_time_ns"), int)
                      and int(replay_binding.get("source_frame_id", 0)) > 0)
        add("task25_frame_and_replay_time_binding", binding_ok,
            {"binding_path": str(TASK25_REPLAY_BINDING), "binding_sha256": binding_sha,
             "frame_path": str(REPLAY_FRAME), "frame_sha256": frame_sha,
             "source_frame_id": replay_binding.get("source_frame_id"),
             "capture_time_available": replay_binding.get("capture_time_available"),
             "capture_time_ns": replay_binding.get("capture_time_ns"),
             "clock_domain": replay_binding.get("clock_domain"),
             "injection_start_ns_used_as_capture_time": False})
    except Exception as exc:
        replay_binding = None
        add("task25_frame_and_replay_time_binding", False,
            {"error": f"{type(exc).__name__}: {exc}"})

    try:
        contract = json.loads(S4A_CONTRACT.read_text(encoding="utf-8"))
        bindings = resolve_contract_bindings()
        for name, item in bindings.items():
            verify(Path(item["path"]), item["sha256"], f"S4-A {name}")
        s4b_path = WORKTREE / "docs" / "stage4" / "s4b_shared_input_result_contract.json"
        s4b = json.loads(s4b_path.read_text(encoding="utf-8"))
        stale = s4b.get("result_contract", {}).get("stale_rule", {})
        receipt_path = Path(str(stale.get("approval_reference", {}).get("receipt_path", "")))
        receipt_sha = (sha256_file(receipt_path) if receipt_path.is_file() else None)
        stale_ok = (int(stale.get("stale_limit_ns", -1)) == STALE_LIMIT_NS
                    and stale.get("stale_limit_status") == "APPROVED_BY_WONG"
                    and stale.get("approval_reference", {}).get("receipt_sha256") == STALE_APPROVAL_SHA256
                    and receipt_sha == STALE_APPROVAL_SHA256)
        activation = json.loads(ACTIVATION_REPORT.read_text(encoding="utf-8"))
        activation_sources = activation.get("inputs", {})
        producer_status = {}
        for key in ("darknet_executable", "activation_hook_source"):
            path_value = activation_sources.get(key)
            expected_value = str(activation_sources.get(key + "_sha256", "")).lower()
            path = Path(str(path_value or ""))
            actual = sha256_file(path) if path.is_file() else None
            producer_status[key] = {"path": str(path), "historical_expected_sha256": expected_value,
                                    "current_sha256": actual,
                                    "status": "MATCH" if actual == expected_value else "HISTORICAL_MISMATCH_NOT_GOLDEN_SOURCE"}
        add("frozen_parameters_and_approved_stale_semantics", stale_ok and bool(bindings),
            {"s4a_contract_status": contract.get("status"), "s4a_contract_sha256": S4A_CONTRACT_SHA256,
             "parameter_bindings": bindings, "activation_report_sha256": ACTIVATION_REPORT_SHA256,
             "activation_producer_sources": producer_status,
             "activation_report_is_golden_source": False,
             "darknet_producer_mismatch_is_recorded_as_history": True,
             "stale_limit_ns": stale.get("stale_limit_ns"),
             "stale_limit_status": stale.get("stale_limit_status"),
             "approval_receipt_sha256": receipt_sha,
             "actual_stale_age_evaluation": "NOT_RUN_FOR_OFFLINE_REPLAY"})
    except Exception as exc:
        bindings = None
        add("frozen_parameters_and_approved_stale_semantics", False,
            {"error": f"{type(exc).__name__}: {exc}"})

    blocked = [name for name, item in checks.items() if item["status"] != "PASS"]
    return {"task_id": "S4-T26-GOLDEN-REBIND", "bridge_version": BRIDGE_VERSION,
            "run_id": run_dir.name, "status": "PASS" if not blocked else "BLOCKED",
            "checks": checks, "blocking_checks": blocked, "real_forward": "NOT_RUN",
            "goldens": goldens, "task25_replay_binding": replay_binding,
            "contract_bindings": bindings, "generated_utc8": now_cn()}


def load_materialized_reference_heads(item: dict[str, object]) -> dict[str, dict[str, object]]:
    """取已验证材料化字节作为 INT8 逐值参考。"""
    heads = item.get("expected_heads")
    if not isinstance(heads, dict) or set(heads) != {"head13", "head26"}:
        raise RuntimeError("材料化参考必须恰有 head13/head26")
    return heads


def write_r10_outputs(out_dir: Path, preflight: dict[str, object], report: dict[str, object],
                      started: float) -> None:
    """写入本次执行报告与机器清单，不写入 task-27 包本身。"""
    preflight_report = dict(preflight)
    goldens = preflight_report.pop("goldens", None)
    if isinstance(goldens, dict):
        preflight_report["verified_golden_summary"] = {
            sample_id: {"gate": item["gate"]["gate"], "image_sha256": item["image_sha256"],
                        "expected_head_sha256": head_hashes(item["expected_heads"])}
            for sample_id, item in goldens.items()}
    preflight_path = out_dir / "preflight_verification.json"
    preflight_path.write_text(json.dumps(preflight_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["preflight_path"] = str(preflight_path)
    report["preflight_sha256"] = sha256_file(preflight_path)
    report["elapsed_seconds"] = time.perf_counter() - started
    result_path = out_dir / "replay_forward_bridge_result.json"
    result_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = {}
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "delivery_manifest.json":
            outputs[str(path.relative_to(out_dir)).replace("\\", "/")] = {
                "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    manifest = {
        "task_id": "S4-T26-GOLDEN-REBIND", "run_id": out_dir.name,
        "status": report["status"], "exit_code": report["exit_code"],
        "worktree": str(WORKTREE), "baseline": report.get("baseline"),
        "command": report.get("command"), "elapsed_seconds": report["elapsed_seconds"],
        "source": {"path": str(Path(__file__).resolve()), "version": BRIDGE_VERSION,
                   "sha256": sha256_file(Path(__file__).resolve())},
        "inputs": preflight.get("checks", {}), "outputs": outputs,
        "task27_package_generated": report.get("task27_package_generated", False),
        "blocking_checks": report.get("blocking_checks", []),
        "limitations": report.get("limitations", []),
    }
    (out_dir / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    """执行已批准的双样本门；所有必需验证通过后才生成 task-27 包。"""
    parser = argparse.ArgumentParser(description="task-26 双样本离线推理与回放证据桥")
    parser.add_argument("--run-dir", required=True, type=Path,
                        help="本次运行的证据输出目录（新 RunId；不得指向黄金来源目录）")
    parser.add_argument("--golden-run-dir", default=GOLDEN_OUTPUT_DIR, type=Path,
                        help="黄金来源 RunId（只读；默认本轮已材料化的 r02）")
    args = parser.parse_args()
    started = time.perf_counter()
    out_dir = args.run_dir.resolve()
    golden_run_dir = args.golden_run_dir.resolve()

    # 输出目录必须位于阶段4 证据根下，且不得与黄金来源目录相同（防覆盖黄金）
    evidence_root = (WORKTREE / "report" / "evidence" / "S4-CTRL").resolve()
    if evidence_root not in out_dir.parents:
        print(f"[BLOCKED] 输出目录必须位于 {evidence_root} 下：{out_dir}", flush=True)
        return 2
    # 无论 --golden-run-dir 指向哪里，都不得写入本轮固定黄金 RunId 目录之内
    fixed_golden_dir = (WORKTREE / "report" / "evidence" / "S4-CTRL" / GOLDEN_RUN_ID).resolve()
    forbidden_roots = {fixed_golden_dir, golden_run_dir}
    for forbidden in forbidden_roots:
        if out_dir == forbidden or forbidden in out_dir.parents:
            print(f"[BLOCKED] 输出目录不得等于或位于黄金目录之内：{forbidden}", flush=True)
            return 2
    if not golden_run_dir.is_dir():
        print(f"[BLOCKED] 黄金来源 RunId 不存在：{golden_run_dir}", flush=True)
        return 2
    if out_dir.exists():
        if not out_dir.is_dir():
            print(f"[BLOCKED] 输出路径已存在且不是目录：{out_dir}", flush=True)
            return 2
        try:
            non_empty = any(out_dir.iterdir())
        except OSError as exc:
            print(f"[BLOCKED] 无法读取输出目录：{type(exc).__name__}: {exc}", flush=True)
            return 2
        if non_empty:
            print(f"[BLOCKED] 输出 RunId 已存在且非空，拒绝复用：{out_dir}", flush=True)
            return 2
    expected_golden_names = {"approved_no_hand_001_head13.bin", "approved_no_hand_001_head26.bin",
                             "test_fist_000_head13.bin", "test_fist_000_head26.bin"}
    golden_dir = golden_run_dir / "golden"
    actual_golden_names = {path.name for path in golden_dir.iterdir() if path.is_file()} if golden_dir.is_dir() else set()
    if actual_golden_names != expected_golden_names:
        print(f"[BLOCKED] 黄金来源 golden/ 内容不符：{sorted(actual_golden_names)}", flush=True)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    tmp_dir = WORKTREE / "tmp" / "4" / "S4-CTRL" / out_dir.name
    if tmp_dir.exists() and any(tmp_dir.iterdir()):
        print(f"[BLOCKED] 隔离临时目录非空，拒绝覆盖：{tmp_dir}", flush=True)
        return 2
    tmp_dir.mkdir(parents=True, exist_ok=True)
    global LOG_PATH
    LOG_PATH = out_dir / "console.log"

    preflight = r10_preflight(out_dir, golden_run_dir)
    interpreter_probes = probe_cv2_runtimes()
    preflight["runtime_interpreter_probes"] = interpreter_probes
    preflight["bridge_source"] = {"path": str(Path(__file__).resolve()), "version": BRIDGE_VERSION,
                                  "sha256": sha256_file(Path(__file__).resolve())}
    preflight["command"] = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]
    try:
        import cv2
        preflight["opencv"] = {"status": "AVAILABLE", "version": cv2.__version__}
    except Exception as exc:
        cv2 = None
        preflight["opencv"] = {"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}"}
    if preflight["status"] != "PASS" or cv2 is None:
        blockers = list(preflight.get("blocking_checks", []))
        if cv2 is None:
            blockers.append("当前解释器无法导入 cv2")
        preflight["blocking_checks"] = blockers
        preflight["status"] = "BLOCKED"
        report = {
            "task_id": "S4-T26-GOLDEN-REBIND", "checker": "replay_forward_bridge",
            "checker_version": BRIDGE_VERSION, "status": "BLOCKED", "exit_code": 2,
            "generated_utc8": now_cn(), "command": preflight["command"],
            "worktree": str(WORKTREE), "baseline": {"head_observed_only": git_head(WORKTREE),
                                                    "branch": "stage4-infer-prep"},
            "hardware_execution": "NOT_RUN", "real_forward": "NOT_RUN",
            "task27_package_generated": False, "blocking_checks": blockers,
            "checks": {}, "limitations": ["尚未执行真实前向、D9/NMS、负向对照或 PNG 检查。",
                                           "不会生成 task-27 包；ENABLE=0、RAW G0 OPEN、P/4-D/G3/G5 NOT_RUN。"],
        }
        write_r10_outputs(out_dir, preflight, report, started)
        emit("[BLOCKED] 前置材料或环境未全部通过；真实前向 NOT_RUN；不生成 task-27 包")
        return 2

    goldens = preflight["goldens"]
    bindings = preflight["contract_bindings"]
    replay_binding = preflight["task25_replay_binding"]
    module = None
    d9 = None
    try:
        module = load_forward_module()
        d9 = load_d9_module()
        activation_sha = verify(ACTIVATION_REPORT, ACTIVATION_REPORT_SHA256, "activation report 参数来源")
        contract_sha = verify(S4A_CONTRACT, S4A_CONTRACT_SHA256, "S4-A 参数契约")
        sections = module.parse_cfg_sections(Path(bindings["cfg"]["path"]))
        float_layers = module.read_fused_float_layers(Path(bindings["cfg"]["path"]),
                                                      Path(bindings["weights"]["path"]))
        header, package_layers = module.parse_package(Path(bindings["gf8_package"]["path"]))
        activation_scales = module.load_activation_scales(
            ACTIVATION_REPORT, Path(bindings["cfg"]["path"]),
            Path(bindings["weights"]["path"]), Path(bindings["calibration_list"]["path"]))
        model_ok = (header.get("width") == 416 and header.get("height") == 416
                    and header.get("channels") == 3 and set(package_layers) == set(float_layers)
                    == set(activation_scales))
    except Exception as exc:
        preflight["checks"]["load_frozen_parameters"] = {
            "status": "BLOCKED", "detail": {"error": f"{type(exc).__name__}: {exc}"}}
        blockers = list(preflight.get("blocking_checks", [])) + ["load_frozen_parameters"]
        preflight["blocking_checks"] = blockers
        report = {"task_id": "S4-T26-GOLDEN-REBIND", "checker": "replay_forward_bridge",
                  "checker_version": BRIDGE_VERSION, "status": "BLOCKED", "exit_code": 2,
                  "generated_utc8": now_cn(),
                  "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  "worktree": str(WORKTREE), "baseline": {"head_observed_only": git_head(WORKTREE),
                                                            "branch": "stage4-infer-prep"},
                  "hardware_execution": "NOT_RUN", "real_forward": "NOT_RUN",
                  "task27_package_generated": False, "blocking_checks": blockers,
                  "checks": {}, "limitations": ["冻结参数装载失败；真实前向 NOT_RUN。",
                                                 "不生成 task-27 包；ENABLE=0、RAW G0 OPEN、P/4-D/G3/G5 NOT_RUN。"]}
        write_r10_outputs(out_dir, preflight, report, started)
        emit(f"[BLOCKED] 冻结参数装载失败，真实前向 NOT_RUN：{type(exc).__name__}: {exc}")
        return 2
    checks: dict[str, dict[str, object]] = {}

    def record(name: str, ok: bool, detail: dict[str, object]) -> None:
        checks[name] = {"status": "PASS" if ok else "BLOCKED", "detail": detail}
        emit(f"[{checks[name]['status']}] {name}")

    record("load_frozen_parameters", model_ok,
           {"package_header": header, "layer_count": len(package_layers),
            "activation_scale_count": len(activation_scales), "activation_report_sha256": activation_sha,
            "s4a_contract_sha256": contract_sha,
            "activation_report_is_golden_source": False,
            "current_darknet_used_to_generate_golden": False})
    if not model_ok:
        report = {"task_id": "S4-T26-GOLDEN-REBIND", "checker": "replay_forward_bridge",
                  "checker_version": BRIDGE_VERSION, "status": "BLOCKED", "exit_code": 2,
                  "generated_utc8": now_cn(),
                  "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  "worktree": str(WORKTREE), "baseline": {"head_observed_only": git_head(WORKTREE),
                                                            "branch": "stage4-infer-prep"},
                  "hardware_execution": "NOT_RUN", "real_forward": "NOT_RUN",
                  "task27_package_generated": False, "blocking_checks": ["load_frozen_parameters"],
                  "checks": checks, "limitations": ["冻结参数形状或层集合不符；真实前向 NOT_RUN。",
                                                    "不生成 task-27 包；ENABLE=0、RAW G0 OPEN、P/4-D/G3/G5 NOT_RUN。"]}
        write_r10_outputs(out_dir, preflight, report, started)
        return 2

    gate_outputs: dict[str, dict[str, object]] = {}
    real_forward_ok = model_ok
    for sample_id in (RAW_HEAD_GATE["sample_id"], POSITIVE_DETECTION_GATE["sample_id"]):
        item = goldens[sample_id]
        gate = item["gate"]
        path = Path(item["image_path"])
        sample_t29 = item["t29_sample"]
        reference_meta = sample_t29["head_tensors"]
        try:
            image_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image_bgr is None:
                raise RuntimeError(f"OpenCV 无法读取输入图像：{path}")
            height, width = image_bgr.shape[:2]
            image_chw, preprocess_evidence = load_t25_preprocessed_forward_input(
                path, 416, 416, module,
                str(item["t25_sample"]["preprocessed_input"]["sha256"]))
            before = time.perf_counter()
            metrics, stats, actual_heads = capture_forward_heads(
                module, d9, image_chw, sections, float_layers, package_layers,
                activation_scales, reference_meta)
            elapsed_ms = (time.perf_counter() - before) * 1000.0
            actual_hashes = head_hashes(actual_heads)
            expected_heads = load_materialized_reference_heads(item)
            raw_equal, raw_comparison = compare_raw_heads(actual_heads, expected_heads)
            saved_heads = save_head_bytes(out_dir, f"{gate['gate']}", actual_heads)
            output: dict[str, object] = {
                "gate": gate["gate"], "sample_id": sample_id, "sample_index": gate["sample_index"],
                "input_path": str(path), "input_sha256": item["image_sha256"],
                "input_shape_bgr": list(image_bgr.shape), "input_chw_shape": list(image_chw.shape),
                "input_chw_sha256": sha256_bytes(np.ascontiguousarray(image_chw).tobytes()),
                "preprocessing_representations": preprocess_evidence,
                "raw_head_match": raw_equal, "raw_head_comparison": raw_comparison,
                "actual_heads": saved_heads, "actual_head_sha256": actual_hashes,
                "offline_host_elapsed_ms": elapsed_ms,
                "metrics_and_integer_stats_role": "diagnostic_only_not_golden",
                "metrics": metrics, "integer_stats": stats.get("integer_stats", {}),
                "marking": {"evidence_kind": "offline_equivalent", "timing_claim_scope": "replay_only",
                            "buffer_scope": "offline_host"},
            }
            if sample_id == POSITIVE_DETECTION_GATE["sample_id"]:
                predictions, candidate_count = decode_heads_with_d9(
                    d9, actual_heads, sample_id, width, height)
                prediction_rows = prediction_records(predictions)
                reference_rows = sample_t29.get("detections", [])
                expected_candidates = int(sample_t29.get("raw_candidate_count_before_stable_nms", -1))
                expected_after_nms = int(sample_t29.get("nms_output_box_count", -1))
                detection_equal = (candidate_count == expected_candidates
                                   and len(prediction_rows) == expected_after_nms
                                   and prediction_rows == reference_rows)
                output["d9_nms"] = {
                    "raw_candidate_count_before_stable_nms": candidate_count,
                    "expected_raw_candidate_count": expected_candidates,
                    "nms_output_count": len(prediction_rows),
                    "expected_nms_output_count": expected_after_nms,
                    "predictions": prediction_rows, "t29_reference_predictions": reference_rows,
                    "exact_t29_detection_match": detection_equal,
                }
                output["positive_detection_match"] = bool(detection_equal and raw_equal)
                record("positive_detection_gate_forward_d9_nms",
                       bool(detection_equal and raw_equal), output)
                real_forward_ok = real_forward_ok and bool(detection_equal and raw_equal)
            else:
                output["raw_head_gate_match"] = bool(raw_equal)
                record("raw_head_gate_forward_byte_compare", bool(raw_equal), output)
                real_forward_ok = real_forward_ok and bool(raw_equal)
            gate_outputs[sample_id] = output
        except Exception as exc:
            record(f"{gate['gate']}_forward", False,
                   {"sample_id": sample_id, "input_path": str(path),
                    "error": f"{type(exc).__name__}: {exc}",
                    "outcome": "BLOCKED; no task-27 package"})
            real_forward_ok = False

    mutation_ok = False
    if real_forward_ok and RAW_HEAD_GATE["sample_id"] in gate_outputs:
        try:
            base_item = goldens[RAW_HEAD_GATE["sample_id"]]
            base_path = Path(base_item["image_path"])
            base_chw, mutation_preprocess_evidence = load_t25_preprocessed_forward_input(
                base_path, 416, 416, module,
                str(base_item["t25_sample"]["preprocessed_input"]["sha256"]))
            quantized = np.asarray(module.saturate_array(module.round_away_array(
                base_chw.astype(np.float64) / module.INPUT_SCALE)), dtype=np.int8)
            tampered, mutation = mutate_one_input_byte(quantized)
            roundtrip = np.asarray(module.saturate_array(module.round_away_array(
                tampered.astype(np.float64) * module.INPUT_SCALE / module.INPUT_SCALE)), dtype=np.int8)
            tampered_chw = tampered.astype(np.float64) * module.INPUT_SCALE
            _, _, changed_heads = capture_forward_heads(
                module, d9, tampered_chw, sections, float_layers, package_layers,
                activation_scales, goldens[RAW_HEAD_GATE["sample_id"]]["t29_sample"]["head_tensors"])
            changed_hashes = head_hashes(changed_heads)
            baseline_hashes = gate_outputs[RAW_HEAD_GATE["sample_id"]]["actual_head_sha256"]
            one_byte_only = int(np.count_nonzero(quantized != tampered)) == 1
            roundtrip_exact = bool(np.array_equal(roundtrip, tampered))
            hash_changed = changed_hashes != baseline_hashes
            mutation_ok = one_byte_only and roundtrip_exact and hash_changed
            record("negative_control_one_int8_input_byte",
                   mutation_ok,
                   {**mutation, "changed_int8_elements": int(np.count_nonzero(quantized != tampered)),
                    "roundtrip_exact": roundtrip_exact, "baseline_head_sha256": baseline_hashes,
                    "perturbed_head_sha256": changed_hashes, "head_hash_changed": hash_changed,
                    "input_gate": RAW_HEAD_GATE["sample_id"],
                    "preprocessing_representations": mutation_preprocess_evidence})
        except Exception as exc:
            record("negative_control_one_int8_input_byte", False,
                   {"error": f"{type(exc).__name__}: {exc}"})
    else:
        record("negative_control_one_int8_input_byte", False,
               {"status": "NOT_RUN", "reason": "真实 raw-head gate 未通过"})

    png_ok = False
    png_item = goldens[RAW_HEAD_GATE["sample_id"]]
    png_path = Path(png_item["image_path"])
    try:
        source_pixels = cv2.imread(str(png_path), cv2.IMREAD_UNCHANGED)
        if (source_pixels is None or source_pixels.dtype != np.uint8
                or source_pixels.ndim != 3 or source_pixels.shape[2] != 3):
            raise RuntimeError("approved_no_hand_001 PNG 必须是 uint8 三通道原图")
        ok_a, encoded_a = cv2.imencode(".png", source_pixels,
                                       [cv2.IMWRITE_PNG_COMPRESSION, PNG_COMPRESSION])
        bgr_from_rgb = source_pixels[:, :, ::-1][:, :, ::-1].copy()
        ok_b, encoded_b = cv2.imencode(".png", bgr_from_rgb,
                                       [cv2.IMWRITE_PNG_COMPRESSION, PNG_COMPRESSION])
        decoded_a = cv2.imdecode(encoded_a, cv2.IMREAD_UNCHANGED) if ok_a else None
        decoded_b = cv2.imdecode(encoded_b, cv2.IMREAD_UNCHANGED) if ok_b else None
        equal_a = bool(decoded_a is not None and decoded_a.shape == source_pixels.shape
                       and decoded_a.dtype == source_pixels.dtype and np.array_equal(decoded_a, source_pixels))
        equal_b = bool(decoded_b is not None and decoded_b.shape == source_pixels.shape
                       and decoded_b.dtype == source_pixels.dtype and np.array_equal(decoded_b, source_pixels))
        png_ok = bool(ok_a and ok_b and equal_a and equal_b)
        record("png_imread_unchanged_pixel_identity", png_ok,
               {"source_path": str(png_path), "source_sha256": png_item["image_sha256"],
                "imread_flag": "IMREAD_UNCHANGED", "source_shape": list(source_pixels.shape),
                "dtype": str(source_pixels.dtype), "roundtrip_a_pixel_equal": equal_a,
                "roundtrip_b_pixel_equal": equal_b,
                "encoded_a_sha256": sha256_bytes(encoded_a.tobytes()) if ok_a else None,
                "encoded_b_sha256": sha256_bytes(encoded_b.tobytes()) if ok_b else None,
                "source_pixels_are_authoritative": True})
    except Exception as exc:
        record("png_imread_unchanged_pixel_identity", False,
               {"source_path": str(png_path), "error": f"{type(exc).__name__}: {exc}"})

    required_before_replay = (real_forward_ok and mutation_ok and png_ok
                              and all(item["status"] == "PASS" for item in checks.values()))
    replay_package: dict[str, object] | None = None
    if required_before_replay:
        try:
            frame_bytes = REPLAY_FRAME.read_bytes()
            frame_bgr = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((720, 1280, 3))
            png_ok, frame_png = cv2.imencode(".png", frame_bgr,
                                             [cv2.IMWRITE_PNG_COMPRESSION, PNG_COMPRESSION])
            if not png_ok:
                raise RuntimeError("task-25 回放帧 PNG 编码失败")
            replay_png = tmp_dir / "task25_replay_frame.png"
            replay_png.write_bytes(frame_png.tobytes())
            replay_chw, replay_preprocess_evidence = load_t25_preprocessed_forward_input(
                replay_png, 416, 416, module, None)
            replay_meta = goldens[POSITIVE_DETECTION_GATE["sample_id"]]["t29_sample"]["head_tensors"]
            frame_started = time.perf_counter()
            replay_metrics, replay_stats, replay_heads = capture_forward_heads(
                module, d9, replay_chw, sections, float_layers, package_layers,
                activation_scales, replay_meta)
            replay_elapsed_ms = (time.perf_counter() - frame_started) * 1000.0
            replay_hashes = head_hashes(replay_heads)
            replay_predictions, replay_candidate_count = decode_heads_with_d9(
                d9, replay_heads, "task25-frozen-frame-1", 1280, 720)
            replay_prediction_rows = prediction_records(replay_predictions)
            replay_head_files = save_head_bytes(out_dir, "task25_replay_frame", replay_heads)
            binding = replay_binding
            session_id = int(sha256_bytes(out_dir.name.encode("utf-8"))[:8], 16)
            replay_package = {
                "task_id": "S4-T26-GOLDEN-REBIND", "frame_id": int(binding["source_frame_id"]),
                "result_seq": 1,
                "contract_result_key": {"session_id": session_id,
                                         "frame_id": int(binding["source_frame_id"]), "result_seq": 1},
                "raw_head_gate": {"sample_id": RAW_HEAD_GATE["sample_id"], "sample_index": 102,
                                   "status": "PASS", "image_sha256": goldens[RAW_HEAD_GATE["sample_id"]]["image_sha256"],
                                   "actual_head_sha256": gate_outputs[RAW_HEAD_GATE["sample_id"]]["actual_head_sha256"]},
                "positive_detection_gate": {"sample_id": POSITIVE_DETECTION_GATE["sample_id"],
                                             "sample_index": 0, "status": "PASS",
                                             "image_sha256": goldens[POSITIVE_DETECTION_GATE["sample_id"]]["image_sha256"],
                                             "actual_head_sha256": gate_outputs[POSITIVE_DETECTION_GATE["sample_id"]]["actual_head_sha256"],
                                             "d9_nms": gate_outputs[POSITIVE_DETECTION_GATE["sample_id"]]["d9_nms"]},
                "historical_calibration_sample": OLD_CALIBRATION_SAMPLE,
                "source_replay_input_binding": dict(binding),
                "replay_frame": {
                    "source_kind": binding["source_kind"], "mode": binding["mode"],
                    "timing_claim_scope": "replay_only", "source_frame_id": int(binding["source_frame_id"]),
                    "frame_id": int(binding["source_frame_id"]),
                    "path": str(REPLAY_FRAME), "sha256": REPLAY_FRAME_SHA256,
                    "length_bytes": len(frame_bytes), "width": 1280, "height": 720,
                    "stride_bytes": 3840, "pixel_format": "BGR888", "byte_order": "BGR",
                    "capture_time_available": bool(binding["capture_time_available"]),
                    "source_capture_time_text": binding.get("source_capture_time_text"),
                    "source_capture_time_precision": binding.get("source_capture_time_precision"),
                    "capture_time_ns": int(binding["capture_time_ns"]),
                    "clock_domain": binding["clock_domain"],
                    "timestamp_source": binding.get("timestamp_source"),
                    "injection_start_ns": None,
                    "injection_start_ns_is_capture_time": False,
                    "stale_limit_ns": STALE_LIMIT_NS,
                    "stale_limit_approval_reference_sha256": STALE_APPROVAL_SHA256,
                    "stale_evaluation": "NOT_RUN_OFFLINE_REPLAY_HAS_NO_MONOTONIC_PUBLISH_CLOCK",
                    "head_sha256": replay_hashes, "head_files": replay_head_files,
                    "d9": {"module_path": str(D9_MODULE), "module_sha256": sha256_file(D9_MODULE),
                           "raw_candidate_count_before_stable_nms": replay_candidate_count,
                           "decoded_predictions": replay_prediction_rows},
                    "offline_host_elapsed_ms": replay_elapsed_ms,
                    "preprocessing_representations": replay_preprocess_evidence,
                    "metrics_and_integer_stats_role": "diagnostic_only_not_golden",
                    "metrics": replay_metrics, "integer_stats": replay_stats.get("integer_stats", {}),
                },
                "source_bindings": {
                    "task25_package_commit": TASK25_PACKAGE_COMMIT,
                    "task25_frame_commit": TASK25_FRAME_COMMIT,
                    "task25_replay_binding_path": str(TASK25_REPLAY_BINDING),
                    "task25_replay_binding_sha256": TASK25_REPLAY_BINDING_SHA256,
                    "decision_path": str(REBIND_DECISION), "decision_sha256": REBIND_DECISION_SHA256,
                    "golden_manifest_path": str(GOLDEN_MANIFEST),
                    "golden_manifest_sha256": GOLDEN_MANIFEST_SHA256,
                },
                "marking": {"replay_only": True, "evidence_kind": "offline_replay",
                            "buffer_scope": "offline_host",
                            "statement": "离线主机回放；不代表 PL、实物或实时检测输出"},
                "limitations": ["ENABLE=0；RAW 系统 G0 OPEN；P/4-D/G3/G5 NOT_RUN；",
                                "原校准样本 NOT_USED_HISTORICAL；负样本未替代阳性检测/显示覆盖。"],
            }
            record("task25_replay_frame_forward", True,
                   {"frame_sha256": REPLAY_FRAME_SHA256, "head_sha256": replay_hashes,
                    "prediction_count": len(replay_prediction_rows),
                    "raw_candidate_count_before_nms": replay_candidate_count,
                    "offline_host_elapsed_ms": replay_elapsed_ms,
                    "capture_time_ns_is_documented_wallclock": True,
                    "injection_start_ns_used_as_capture_time": False})
        except Exception as exc:
            record("task25_replay_frame_forward", False,
                   {"error": f"{type(exc).__name__}: {exc}", "task27_package_generated": False})
    else:
        record("task25_replay_frame_forward", False,
               {"status": "NOT_RUN", "reason": "前置真实门、扰动或 PNG 检查未全部通过"})

    final_ok = bool(replay_package is not None and all(item["status"] == "PASS" for item in checks.values()))
    if final_ok:
        package_path = out_dir / "task27_replay_result_package.json"
        package_path.write_text(json.dumps(replay_package, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    blockers = [name for name, item in checks.items() if item["status"] != "PASS"]
    final_status = "PASS" if final_ok else "BLOCKED"
    report = {
        "task_id": "S4-T26-GOLDEN-REBIND", "checker": "replay_forward_bridge",
        "checker_version": BRIDGE_VERSION, "status": final_status,
        "exit_code": 0 if final_ok else 2, "generated_utc8": now_cn(),
        "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "worktree": str(WORKTREE), "baseline": {"head_observed_only": git_head(WORKTREE),
                                                  "branch": "stage4-infer-prep"},
        "hardware_execution": "NOT_RUN", "checks": checks,
        "raw_head_gate": gate_outputs.get(RAW_HEAD_GATE["sample_id"], {"status": "NOT_RUN"}),
        "positive_detection_gate": gate_outputs.get(POSITIVE_DETECTION_GATE["sample_id"], {"status": "NOT_RUN"}),
        "task27_package_generated": final_ok,
        "task27_package_path": str(out_dir / "task27_replay_result_package.json") if final_ok else None,
        "blocking_checks": blockers,
        "limitations": ["结果仅为 replay_only/offline_host，不声明板级、实时或阶段验收结论。",
                        "当前 Darknet r03/r04 失败证据保留；未被用作黄金来源。",
                        "原校准样本 NOT_USED_HISTORICAL；负样本 raw-head 门不替代阳性检测/显示覆盖。",
                        "ENABLE=0、RAW G0 OPEN、P/4-D/G3/G5 NOT_RUN。"],
    }
    write_r10_outputs(out_dir, preflight, report, started)
    return 0 if final_ok else 2


if __name__ == "__main__":
    sys.exit(main())
