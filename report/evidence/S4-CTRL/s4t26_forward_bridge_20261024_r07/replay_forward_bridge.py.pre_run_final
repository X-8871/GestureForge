#!/usr/bin/env python3
"""离线真实彩色链 · 输入张量驱动前向桥（task-26 / (A)，只读复用，离线等价）。

## 边界（2026-10-24 lead 裁决，逐条实现）
1. **优先复用而非重写**：`import` 既有 `verification/s1_t02_d2_int8_forward.py`，调用其
   `load_image_chw`（冻结预处理本体：BGR→RGB、自带确定性双线性、letterbox 0.5、/255、CHW）
   与 `forward_one`（**内部完成量化**：`Tensor(saturate(round_away(chw/INPUT_SCALE)), INPUT_SCALE)`）。
   本文件**不复制**任何预处理或网络数学，也不修改任何冻结件。
2. **量化与顺序沿冻结口径**：量化全部发生在既有 `forward_one` 内部；证据记录 `INPUT_SCALE`、
   各层 `activation_scale` 与张量/输出摘要哈希。
3. **可复现与判别力**：同一输入跑两次须得同一层级摘要哈希；负向对照覆盖错 scale、跨过 INT8 量化档的输入改动、有损 JPEG 容器。
4. **真实检测头**：只通过既有前向模块的 `metric` 调用捕获 YOLO 输出；按 cfg 的 layer index、前一卷积层、
   D9 head grid 和冻结 T25/T29 元数据 fail-closed 校验映射及形状，不复制网络数学。
5. **独立逐值对拍**：冻结校准样本必须有独立 raw head13/head26 参考并逐字节比较；摘要 metrics 不能代替检测头。
   缺少该参考或 OpenCV 时只生成 `BLOCKED/NOT_RUN` 证据，不执行推理。
6. **可复现与判别力**：同一输入比较两次 raw heads 哈希；错一个量化 scale、改输入 tensor 一个字节都必须改变 heads 哈希。
7. **PNG 双路像素核验**：A/B 都以 `IMREAD_UNCHANGED` 解码并分别逐像素对照源 BGR；CHW 相等不作为替代。
8. **缺失输入不得编造**：冻结件按 SHA 校验；所有产物标注 `offline_equivalent` / `replay_only` / `scope=offline_host`。

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
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

CN = timezone(timedelta(hours=8))
WORKTREE = Path(__file__).resolve().parents[2]
BASELINE_COMMIT = "1046cdc9eedefd903e6b96e0190f4897c6a371db"
FORWARD_MODULE = WORKTREE / "verification" / "s1_t02_d2_int8_forward.py"
D9_MODULE = WORKTREE / "verification" / "s1_t02_d9_yolo_decode.py"
D6_MODULE = WORKTREE / "verification" / "s1_t02_d6_detection_metrics.py"
T25_INDEX = WORKTREE / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json"
T29_REFERENCE = WORKTREE / "report" / "evidence" / "S2A-T29" / "cpu_decode_nms_reference.json"
T29_GENERATOR = WORKTREE / "verification" / "s2a_decode_nms_reference.py"
T29_TEST = WORKTREE / "verification" / "test_s2a_decode_nms_reference.py"
BOUND_T25_T29_TREE = Path(r"D:\codex-worktrees\dbdf")
S4A_CONTRACT = WORKTREE / "docs" / "stage4" / "s4a_stage4_g0_fields.json"
# 激活报告未列入 S4-A 契约；本离线脚本单独固定其 raw SHA 与 LF 内容 SHA，不改写正式契约。
ACTIVATION_REPORT = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
REFERENCE_RUN = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_int8_forward_r2.json"
REPLAY_DIR = Path(r"D:\codex-worktrees\dbdf\report\evidence\S3-T05\t05_stage3_window_20261024_r01")
REPLAY_FRAME = REPLAY_DIR / "frame_full.bin"
REPLAY_FRAME_SHA256 = "939fce22b7e86aa6356dc80d977626dcfe34ce8e9def8964ff03122d956752f0"
S4A_CONTRACT_SHA256 = "657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5"
ACTIVATION_REPORT_SHA256 = "6d73283c698a94dd30cf00634de59fb76a8e889916eb4d00e50b76c245687216"
ACTIVATION_REPORT_CONTENT_SHA256 = "1156ef813db4e08504c6bb8935b02720a6dd9b792e8a48d255725571d27063e5"
REFERENCE_RUN_SHA256 = "3d5ccedc9dc25f62353711c75f509706187047dbd70321cefb98e0bc0ade3973"
REFERENCE_RUN_CONTENT_SHA256 = "63f5bfef5cb9801f45cc51779ca87997686f46f52b48a3a22d87ff012271d3e4"
WEIGHT_REPORT = WORKTREE / "report" / "evidence" / "S1-T02" / "20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
WEIGHT_REPORT_SHA256 = "d867cd5dc7497f0de9db5c4e0643afd2e52d4c1e77632852487e8afceaa0dd80"
FORWARD_MODULE_SHA256 = "0b90ef46b923b046cfcabb0b8ff8aaff4f6b927b9b8ee9eaa10335362c6c922a"
FORWARD_MODULE_CONTENT_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
EXPECTED_W4_HEAD = BASELINE_COMMIT
EXPECTED_DBDF_HEAD = "1d54894be4d547955034eeff8bce853dd4286fac"
T25_INDEX_LF_SHA256 = "cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d"
T29_REFERENCE_LF_SHA256 = "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"
D9_MODULE_LF_SHA256 = "0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6"
D6_MODULE_LF_SHA256 = "5ff91ffbbaa82935811f2ddc335434a3c70afa58eaa980e353e64b057803bea2"
T29_GENERATOR_LF_SHA256 = "219a09720d9de0723730b51ed9c007aeec5e1b9abf6bc49c5e0268c2173bc49c"
T25_INDEX_RAW_SHA256 = "2d76f9e284130c96374de6ea3525e0c92778b0f701c8894cd4d127234c8d3c72"
T29_REFERENCE_RAW_SHA256 = "26392c8d7f5ca8643a26c149411c66d6f2343a544f8c4f03d32584dc4e071d33"
DBDF_TREE_HEAD = EXPECTED_DBDF_HEAD
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


def run_static_interface_selfcheck(sample_index: int) -> dict[str, object]:
    """只读核验冻结模块、cfg/head 映射、参考来源与校准样本身份。"""
    checks: dict[str, dict[str, object]] = {}

    def add(name: str, ok: bool, detail: dict[str, object]) -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail}

    try:
        w4_head = git_head(WORKTREE)
        w4_branch = subprocess.run(["git", "branch", "--show-current"], cwd=str(WORKTREE),
                                   capture_output=True, check=True, text=True, encoding="utf-8").stdout.strip()
        dbdf_head = git_head(BOUND_T25_T29_TREE)
        add("bound_tree_heads", w4_head == EXPECTED_W4_HEAD and w4_branch == "stage4-infer-prep"
            and dbdf_head == EXPECTED_DBDF_HEAD,
            {"w4": {"head": w4_head, "branch": w4_branch, "expected_head": EXPECTED_W4_HEAD},
             "dbdf_t25_t29": {"head": dbdf_head, "expected_head": EXPECTED_DBDF_HEAD},
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
        "task_id": "S4-CTRL/S4-T26", "run_id": "s4t26_forward_bridge_20261024_r07",
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
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": "r07",
        "status": "FAIL", "exit_code": 1, "generated_utc8": now_cn(), "elapsed_seconds": elapsed,
        "command": command, "worktree": str(WORKTREE),
        "baseline": {"commit": BASELINE_COMMIT, "branch": "stage4-infer-prep"},
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
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": "r07",
        "status": "BLOCKED", "exit_code": 2, "generated_utc8": now_cn(), "elapsed_seconds": elapsed,
        "command": command, "worktree": str(WORKTREE),
        "baseline": {"commit": BASELINE_COMMIT, "branch": "stage4-infer-prep"},
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


def main() -> int:
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

    preflight = run_static_interface_selfcheck(args.sample_index)
    interpreter_probes = probe_cv2_runtimes()
    preflight["runtime_interpreter_probes"] = interpreter_probes
    preflight["bridge_source"] = {"path": str(Path(__file__).resolve()),
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
    if current_head != BASELINE_COMMIT or current_branch != "stage4-infer-prep":
        raise SystemExit(f"[FAIL] 工作树基线漂移：head={current_head} branch={current_branch}")
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
        "baseline": {"head": current_head, "branch": current_branch},
        "bound_tree_heads": {"w4": current_head, "dbdf_t25_t29": git_head(BOUND_T25_T29_TREE),
                             "dbdf_expected": EXPECTED_DBDF_HEAD,
                             "drift_assertion": git_head(BOUND_T25_T29_TREE) == EXPECTED_DBDF_HEAD},
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
            "bound_tree_heads": {"w4": git_head(WORKTREE), "dbdf_t25_t29": git_head(BOUND_T25_T29_TREE)},
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
        "task_id": "S4-CTRL/S4-T26", "checker": "replay_forward_bridge", "checker_version": "r07",
        "status": status, "exit_code": exit_code, "generated_utc8": now_cn(), "elapsed_seconds": elapsed_seconds,
        "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
        "worktree": str(WORKTREE), "hardware_execution": "NOT_RUN",
        "baseline": {"commit": BASELINE_COMMIT, "branch": "stage4-infer-prep"},
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
        "source": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve()),
                   "original_snapshot_path": str(SOURCE_SNAPSHOT), "original_snapshot_sha256": snapshot_sha},
        "inputs": identity, "outputs": artifact_hashes, "temporary_artifacts": temporary_hashes,
        "limitations": report["limitations"],
    }
    (out_dir / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
