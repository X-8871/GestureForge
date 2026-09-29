#!/usr/bin/env python3
"""构建并比较 S2A-T62 C99 主机解码/NMS 参考核与冻结 D9。"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
import s2a_decode_nms_reference as t29
import s1_t02_d9_yolo_decode as d9


C_SOURCE = ROOT / "verification/s2a_ps_decode_nms_reference.c"
C_HEADER = ROOT / "verification/s2a_ps_decode_nms_reference.h"
T29_EVIDENCE = ROOT / "report/evidence/S2A-T29/cpu_decode_nms_reference.json"
T62_EVIDENCE = ROOT / "report/evidence/S2A-T62/layer35_ps_decode_nms_c_reference.json"
G0_SPEC = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
T01_PLAN = ROOT / "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md"
MANIFEST = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T25_INDEX = ROOT / "report/evidence/S2A-T25/cpu_layer_golden_index.json"
T29_RUNNER = ROOT / "verification/s2a_decode_nms_reference.py"
D6_REFERENCE = ROOT / "verification/s1_t02_d6_detection_metrics.py"
D9_REFERENCE = ROOT / "verification/s1_t02_d9_yolo_decode.py"
CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
SAMPLE_COUNT = 109
BASELINE_HEAD = "ec25ea282783da2e7c6e6c3f042398a75e5f130c"
PREVIOUS_REPORT_SHA256 = "8aceb76892f0bcb8b3174ffc49b33206840f94b40724cb915d9f03386130fca7"
SCORE_TOLERANCE = 1e-6
COORDINATE_TOLERANCE = 1e-6


class CDetection(ctypes.Structure):
    """与 C 头文件对应的 ABI 结构。"""

    _fields_ = [
        ("class_id", ctypes.c_int32),
        ("source_order", ctypes.c_int32),
        ("score", ctypes.c_double),
        ("x1", ctypes.c_double),
        ("y1", ctypes.c_double),
        ("x2", ctypes.c_double),
        ("y2", ctypes.c_double),
    ]


def sha256_bytes(value: bytes) -> str:
    """计算字节串 SHA-256。"""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """按字节计算文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    """检查固定契约，不满足时停止生成 PASS 证据。"""

    if not condition:
        raise RuntimeError(message)


def compile_library(temp_dir: Path) -> tuple[ctypes.CDLL, dict[str, Any]]:
    """使用本机 GCC 编译隔离的共享库。"""

    gcc = "gcc"
    suffix = ".dll" if os.name == "nt" else ".so"
    library_path = temp_dir / f"s2a_t62_ps_decode_nms{suffix}"
    command = [
        gcc,
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        "-O2",
        "-shared",
        str(C_SOURCE),
        "-o",
        str(library_path),
        "-lm",
    ]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    elapsed = time.perf_counter() - started
    require(completed.returncode == 0, f"GCC 失败，退出码={completed.returncode}\n{completed.stderr}")
    library = ctypes.CDLL(str(library_path))
    function = library.s2a_t62_decode_nms
    double_pointer = ctypes.POINTER(ctypes.c_double)
    size_type = ctypes.c_size_t
    function.argtypes = [
        double_pointer,
        size_type,
        double_pointer,
        size_type,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_double,
        ctypes.POINTER(CDetection),
        size_type,
        ctypes.POINTER(size_type),
        ctypes.POINTER(size_type),
    ]
    function.restype = ctypes.c_int
    compiler_version = subprocess.run(
        [gcc, "--version"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
    )
    require(compiler_version.returncode == 0, "无法读取 GCC 版本")
    return library, {
        "command": command,
        "exit_code": completed.returncode,
        "elapsed_seconds": round(elapsed, 6),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "language_standard": "ISO C99",
        "gcc_version_first_line": compiler_version.stdout.splitlines()[0],
        "shared_library_sha256": sha256_file(library_path),
    }


def unload_library(library: ctypes.CDLL) -> None:
    """Windows 临时 DLL 映射结束后显式释放句柄。"""

    if os.name == "nt" and getattr(library, "_handle", 0):
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.FreeLibrary.argtypes = [ctypes.c_void_p]
        kernel32.FreeLibrary.restype = ctypes.c_int
        handle = library._handle
        require(kernel32.FreeLibrary(ctypes.c_void_p(handle)) != 0, "FreeLibrary 无法释放临时 C DLL")
        library._handle = 0


def c_decode(
    library: ctypes.CDLL,
    heads: dict[str, np.ndarray],
    width: int,
    height: int,
    threshold: float,
) -> tuple[list[dict[str, Any]], int]:
    """将 D9 同一解量化输入传入 C ABI。"""

    head13 = np.ascontiguousarray(heads["13x13"], dtype=np.float64).reshape(-1)
    head26 = np.ascontiguousarray(heads["26x26"], dtype=np.float64).reshape(-1)
    output = (CDetection * 15)()
    output_count = ctypes.c_size_t()
    raw_count = ctypes.c_size_t()
    status = library.s2a_t62_decode_nms(
        head13.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        head13.size,
        head26.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        head26.size,
        width,
        height,
        threshold,
        output,
        len(output),
        ctypes.byref(output_count),
        ctypes.byref(raw_count),
    )
    require(status == 0, f"C ABI 返回错误 {status}")
    detections = []
    for index in range(output_count.value):
        row = output[index]
        detections.append(
            {
                "class_id": int(row.class_id),
                "source_order": int(row.source_order),
                "score": float(row.score),
                "xyxy": [float(row.x1), float(row.y1), float(row.x2), float(row.y2)],
            }
        )
    return detections, int(raw_count.value)


def c_call_error_case(
    library: ctypes.CDLL,
    case_id: str,
    heads: dict[str, np.ndarray],
    threshold: float,
    expected_status: int,
) -> dict[str, Any]:
    """检查错误码及失败时不改写输出或计数哨兵。"""

    head13 = np.ascontiguousarray(heads["13x13"], dtype=np.float64).reshape(-1)
    head26 = np.ascontiguousarray(heads["26x26"], dtype=np.float64).reshape(-1)
    output = (CDetection * 15)()
    for index in range(len(output)):
        output[index].class_id = -101 - index
        output[index].source_order = -201 - index
        output[index].score = -301.0 - index
        output[index].x1 = -401.0 - index
        output[index].y1 = -501.0 - index
        output[index].x2 = -601.0 - index
        output[index].y2 = -701.0 - index
    output_before = ctypes.string_at(ctypes.addressof(output), ctypes.sizeof(output))
    output_count = ctypes.c_size_t(777)
    raw_count = ctypes.c_size_t(888)
    status = library.s2a_t62_decode_nms(
        head13.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        head13.size,
        head26.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        head26.size,
        416,
        416,
        threshold,
        output,
        len(output),
        ctypes.byref(output_count),
        ctypes.byref(raw_count),
    )
    output_preserved = ctypes.string_at(ctypes.addressof(output), ctypes.sizeof(output)) == output_before
    counts_preserved = output_count.value == 777 and raw_count.value == 888
    require(status == expected_status, f"{case_id}: 错误码 {status}，预期 {expected_status}")
    require(status != 0, f"{case_id}: 非法输入被报告为成功")
    require(output_preserved, f"{case_id}: 失败时改写了输出缓冲区")
    require(counts_preserved, f"{case_id}: 失败时改写了输出计数")
    return {
        "case_id": case_id,
        "expected_status": expected_status,
        "observed_status": status,
        "success_reported": status == 0,
        "output_buffer_preserved": output_preserved,
        "output_count_preserved": output_count.value == 777,
        "raw_candidate_count_preserved": raw_count.value == 888,
    }


def run_error_contract_tests(library: ctypes.CDLL) -> list[dict[str, Any]]:
    """检查非法参数、非有限值与有限 tw 指数溢出的 ABI 错误语义。"""

    cases = []
    clean = blank_heads()
    cases.append(c_call_error_case(library, "negative_threshold", clean, -0.01, -1))
    cases.append(c_call_error_case(library, "nonfinite_threshold_nan", clean, float("nan"), -1))

    nan_heads = blank_heads()
    nan_heads["13x13"][0, 0, 0, 0] = float("nan")
    cases.append(c_call_error_case(library, "nonfinite_logit_nan", nan_heads, 0.25, -2))

    inf_heads = blank_heads()
    inf_heads["13x13"][0, 2, 0, 0] = float("inf")
    cases.append(c_call_error_case(library, "nonfinite_logit_infinity", inf_heads, 0.25, -2))

    overflow_heads = blank_heads()
    overflow_heads["13x13"][0, 2, 0, 0] = 1000.0
    cases.append(c_call_error_case(library, "finite_tw_exp_overflow_1000", overflow_heads, 0.25, -3))
    return cases


def d9_decode(
    heads: dict[str, np.ndarray], sample_id: str, width: int, height: int, threshold: float
) -> tuple[list[Any], int]:
    """调用 D9 并观察进入冻结 NMS 的候选数。"""

    candidates_seen: list[int] = []
    original_nms = d9.stable_nms

    def observe_nms(predictions: Any, *args: Any, **kwargs: Any) -> list[Any]:
        values = list(predictions)
        candidates_seen.append(len(values))
        return original_nms(values, *args, **kwargs)

    d9.stable_nms = observe_nms
    try:
        detections = d9.decode_yolov4_tiny416(
            heads,
            image_key=sample_id,
            image_width=width,
            image_height=height,
            score_threshold=threshold,
        )
    finally:
        d9.stable_nms = original_nms
    require(len(candidates_seen) == 1, f"{sample_id}: D9 NMS 调用次数不是 1")
    return detections, candidates_seen[0]


def compare_detections(expected: list[Any], observed: list[dict[str, Any]], sample_id: str) -> dict[str, Any]:
    """按冻结容差逐框比较类别、分数、坐标和源顺序。"""

    require(len(expected) == len(observed), f"{sample_id}: 输出框数不同，D9={len(expected)} C={len(observed)}")
    rows: list[dict[str, Any]] = []
    max_score_error = 0.0
    max_coordinate_error = 0.0
    for index, (reference, actual) in enumerate(zip(expected, observed)):
        expected_box = [float(value) for value in reference.box]
        score_error = abs(float(reference.confidence) - actual["score"])
        coordinate_error = max(abs(left - right) for left, right in zip(expected_box, actual["xyxy"]))
        require(reference.class_id == actual["class_id"], f"{sample_id}[{index}]: 类别不匹配")
        require(reference.source_order == actual["source_order"], f"{sample_id}[{index}]: source_order 不匹配")
        require(score_error <= SCORE_TOLERANCE, f"{sample_id}[{index}]: score 误差 {score_error} 超限")
        require(coordinate_error <= COORDINATE_TOLERANCE, f"{sample_id}[{index}]: 坐标误差 {coordinate_error} 超限")
        rows.append(
            {
                "class_id": int(reference.class_id),
                "class_name": CLASS_NAMES[reference.class_id],
                "source_order": int(reference.source_order),
                "d9_score": float(reference.confidence),
                "c_score": actual["score"],
                "score_abs_error": score_error,
                "d9_xyxy": expected_box,
                "c_xyxy": actual["xyxy"],
                "xyxy_max_abs_error": coordinate_error,
            }
        )
        max_score_error = max(max_score_error, score_error)
        max_coordinate_error = max(max_coordinate_error, coordinate_error)
    return {
        "detection_count": len(expected),
        "detections": rows,
        "max_score_abs_error": max_score_error,
        "max_xyxy_abs_error": max_coordinate_error,
    }


def blank_heads(fill: float = -12.0) -> dict[str, np.ndarray]:
    """创建两个固定形状的 CPU head。"""

    return {
        "13x13": np.full((3, 10, 13, 13), fill, dtype=np.float64),
        "26x26": np.full((3, 10, 26, 26), fill, dtype=np.float64),
    }


def activate(
    heads: dict[str, np.ndarray],
    head_name: str,
    local_anchor: int,
    row: int,
    col: int,
    *,
    objectness: float,
    classes: tuple[float, float, float, float, float],
    tx: float = 0.0,
    ty: float = 0.0,
    tw: float = 0.0,
    th: float = 0.0,
) -> None:
    """设置一个 NCHW anchor/cell 的十项输入。"""

    value = heads[head_name]
    value[local_anchor, 0, row, col] = tx
    value[local_anchor, 1, row, col] = ty
    value[local_anchor, 2, row, col] = tw
    value[local_anchor, 3, row, col] = th
    value[local_anchor, 4, row, col] = objectness
    value[local_anchor, 5:10, row, col] = classes


def compare_fixture(library: ctypes.CDLL, label: str, heads: dict[str, np.ndarray], width: int, height: int) -> dict[str, Any]:
    """将一个 T01 风格固定边界夹具同时送入 D9 与 C。"""

    expected, d9_raw_count = d9_decode(heads, label, width, height, 0.25)
    observed, c_raw_count = c_decode(library, heads, width, height, 0.25)
    require(d9_raw_count == c_raw_count, f"{label}: raw candidate 数不匹配")
    compared = compare_detections(expected, observed, label)
    return {
        "fixture_id": label,
        "image_wh": [width, height],
        "raw_candidate_count_d9": d9_raw_count,
        "raw_candidate_count_c": c_raw_count,
        **compared,
    }


def run_fixtures(library: ctypes.CDLL) -> list[dict[str, Any]]:
    """覆盖冻结解码契约的空、等号、padding、裁剪、NMS、类别和上限夹具。"""

    fixtures = []
    fixtures.append(compare_fixture(library, "empty_output", blank_heads(), 416, 416))

    threshold_heads = blank_heads()
    activate(threshold_heads, "13x13", 0, 2, 3, objectness=0.0, classes=(0.0, -12.0, -12.0, -12.0, -12.0))
    threshold_fixture = compare_fixture(library, "score_threshold_equal", threshold_heads, 416, 416)
    require(threshold_fixture["raw_candidate_count_d9"] == 1, "阈值等号夹具未产生恰好一个候选")
    require(threshold_fixture["detections"][0]["d9_score"] == 0.25, "阈值等号夹具 score 不等于 0.25")
    fixtures.append(threshold_fixture)

    geometry_heads = blank_heads()
    activate(geometry_heads, "26x26", 0, 0, 0, objectness=6.0, classes=(6.0, 6.0, -12.0, -12.0, -12.0), tw=2.0, th=2.0)
    activate(geometry_heads, "26x26", 0, 0, 1, objectness=5.0, classes=(6.0, -12.0, -12.0, -12.0, -12.0), tw=2.0, th=2.0)
    geometry_fixture = compare_fixture(library, "odd_padding_clipping_class_nms", geometry_heads, 333, 200)
    require(geometry_fixture["raw_candidate_count_d9"] == 3, "奇数补边/NMS夹具候选数不为 3")
    require(geometry_fixture["detection_count"] == 2, "同类抑制、异类保留夹具输出数不为 2")
    require({row["class_id"] for row in geometry_fixture["detections"]} == {0, 1}, "异类保留夹具类别不符")
    require(any(value == 0.0 for row in geometry_fixture["detections"] for value in row["d9_xyxy"]), "边界裁剪夹具未触及 0")
    fixtures.append(geometry_fixture)

    cap_heads = {"13x13": np.zeros((3, 10, 13, 13), dtype=np.float64), "26x26": np.zeros((3, 10, 26, 26), dtype=np.float64)}
    cap_fixture = compare_fixture(library, "stable_tie_and_max_15", cap_heads, 416, 416)
    require(cap_fixture["raw_candidate_count_d9"] == 12675, "最大候选夹具未覆盖全部 12675 项")
    require(cap_fixture["detection_count"] <= 15, "最大输出夹具超过 15 框上限")
    require([row["source_order"] for row in cap_fixture["detections"]] == sorted(row["source_order"] for row in cap_fixture["detections"]), "同分稳定次序不符合 source_order")
    fixtures.append(cap_fixture)

    rng = random.Random(20260929)
    random_heads = blank_heads(-8.0)
    random_activations = []
    for _ in range(48):
        head_name = "13x13" if rng.randrange(2) == 0 else "26x26"
        grid = 13 if head_name == "13x13" else 26
        local_anchor = rng.randrange(3)
        row = rng.randrange(grid)
        col = rng.randrange(grid)
        activate(
            random_heads,
            head_name,
            local_anchor,
            row,
            col,
            objectness=rng.uniform(0.5, 7.0),
            classes=tuple(rng.uniform(-1.0, 7.0) for _ in range(5)),
            tx=rng.uniform(-1.0, 1.0),
            ty=rng.uniform(-1.0, 1.0),
            tw=rng.uniform(-1.0, 1.0),
            th=rng.uniform(-1.0, 1.0),
        )
        random_activations.append([head_name, local_anchor, row, col])
    random_fixture = compare_fixture(library, "fixed_seed_random_20260929", random_heads, 640, 359)
    random_fixture["seed"] = 20260929
    random_fixture["activated_anchor_cells"] = len(random_activations)
    fixtures.append(random_fixture)
    return fixtures


def load_parent_report() -> tuple[dict[str, Any], str]:
    """验证 T29 父报告为已完成的 109 样本 CPU 参考。"""

    require(T29_EVIDENCE.is_file() and not T29_EVIDENCE.is_symlink(), "T29 父证据缺失或类型错误")
    payload = T29_EVIDENCE.read_bytes()
    parent = json.loads(payload.decode("utf-8"))
    require(parent.get("task_id") == "S2A-T29", "T29 父报告 task_id 不符")
    require(parent.get("status") == "CPU_REFERENCE_GENERATED", "T29 父报告不是已生成状态")
    require(parent.get("scope", {}).get("fixed_sample_count") == SAMPLE_COUNT, "T29 父报告样本数不是 109")
    require(len(parent.get("samples", [])) == SAMPLE_COUNT, "T29 父报告逐样本结果数不是 109")
    require(len(parent.get("shard_bindings", [])) == SAMPLE_COUNT, "T29 父报告 shard 绑定数不是 109")
    require(parent.get("scope", {}).get("rtl_simulation") == "NOT_EXECUTED", "T29 报告 scope 异常")
    require(parent.get("t25_index_binding", {}).get("status") == "COMPLETE", "T29 父报告 T25 索引状态不是 COMPLETE")
    require(parent.get("t25_index_binding", {}).get("completed_samples") == SAMPLE_COUNT, "T29 父报告未绑定完整 T25 109 样本")
    for binding in parent.get("source_bindings", []):
        relative = binding.get("path")
        digest = binding.get("sha256")
        if isinstance(relative, str) and isinstance(digest, str):
            bound_path = (ROOT / Path(relative)).resolve()
            require(bound_path.is_relative_to(ROOT.resolve()), f"T29 父报告绑定路径越界：{relative}")
            require(bound_path.is_file() and not bound_path.is_symlink(), f"T29 父报告绑定源缺失或类型错误：{relative}")
            require(sha256_file(bound_path) == digest, f"T29 父报告源哈希不匹配：{relative}")
    for index, row in enumerate(parent["samples"]):
        require(row.get("frame_id") == index and isinstance(row.get("sample_id"), str), f"T29 样本序列异常：{index}")
        require(len(row.get("detections", [])) == row.get("nms_output_box_count"), f"T29 样本框数异常：{index}")
    return parent, sha256_bytes(payload)


def compare_109_cpu_goldens(library: ctypes.CDLL, parent: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """经 T29 校验器读取 109 个 T25 CPU head golden 并逐框比较 C 与 D9。"""

    parent_rows = {row["sample_id"]: row for row in parent["samples"]}
    comparisons: list[dict[str, Any]] = []
    raw_candidate_total = 0
    output_total = 0
    d9_original = t29.decode_and_count_candidates

    def observing_decode(
        head_logits: dict[str, np.ndarray], sample_id: str, width: int, height: int, threshold: float
    ) -> tuple[list[Any], int]:
        nonlocal raw_candidate_total, output_total
        expected, d9_raw_count = d9_original(head_logits, sample_id, width, height, threshold)
        observed, c_raw_count = c_decode(library, head_logits, width, height, threshold)
        require(d9_raw_count == c_raw_count, f"{sample_id}: raw candidate 数不匹配")
        compared = compare_detections(expected, observed, sample_id)
        row = parent_rows.get(sample_id)
        require(row is not None, f"T29 父报告缺少样本 {sample_id}")
        require(row["nms_output_box_count"] == len(expected), f"{sample_id}: 运行 D9 与父证据框数不匹配")
        for index, (runtime_detection, parent_detection) in enumerate(zip(expected, row["detections"])):
            require(
                runtime_detection.class_id == parent_detection["class_id"]
                and runtime_detection.source_order == parent_detection["source_order"]
                and runtime_detection.confidence == parent_detection["score"]
                and list(runtime_detection.box) == parent_detection["xyxy"],
                f"{sample_id}[{index}]: 运行 D9 与 T29 父检测记录不一致",
            )
        comparisons.append(
            {
                "frame_id": row["frame_id"],
                "sample_id": sample_id,
                "input_head_tensors": row["head_tensors"],
                "image_wh": row["input"]["geometry_wh"],
                "d9_raw_candidate_count": d9_raw_count,
                "c_raw_candidate_count": c_raw_count,
                **compared,
            }
        )
        raw_candidate_total += d9_raw_count
        output_total += len(expected)
        current = len(comparisons)
        if current == 1 or current % 13 == 0 or current == SAMPLE_COUNT:
            print(f"PROGRESS T62 CPU samples={current}/{SAMPLE_COUNT} outputs={output_total}", flush=True)
        return expected, d9_raw_count

    t29.decode_and_count_candidates = observing_decode
    started = time.perf_counter()
    try:
        regenerated = t29.generate_evidence(ROOT, progress=None, preflight_only=False)
    finally:
        t29.decode_and_count_candidates = d9_original
    elapsed = time.perf_counter() - started
    require(len(comparisons) == SAMPLE_COUNT, f"T29 运行未拦截全部 109 个 head golden，实际={len(comparisons)}")
    require(len(regenerated["samples"]) == SAMPLE_COUNT, "T29 运行时生成结果不是 109 样本")
    regenerated_rows = {row["sample_id"]: row for row in regenerated["samples"]}
    for sample_id, parent_row in parent_rows.items():
        fresh_row = regenerated_rows.get(sample_id)
        require(fresh_row is not None, f"重算 T29 缺少父报告样本 {sample_id}")
        for field in ("input", "head_tensors", "raw_candidate_count_before_stable_nms", "nms_output_box_count", "detections"):
            require(fresh_row[field] == parent_row[field], f"T29 父报告与 T25 重算字段不一致：{sample_id}/{field}")
    require(regenerated["shard_bindings"] == parent["shard_bindings"], "T29 父报告压缩/解压 shard SHA 绑定与重算不同")
    require(regenerated["source_bindings"] == parent["source_bindings"], "T29 父报告源路径/SHA 绑定与当前工作区不同")
    require(t29._canonical_evidence_bytes(regenerated) == t29._canonical_evidence_bytes(parent), "T29 父报告不能由当前 109 个冻结 CPU golden 确定性重建")
    return {
        "samples_compared": len(comparisons),
        "raw_candidate_count_total": raw_candidate_total,
        "output_box_count_total": output_total,
        "elapsed_seconds": round(elapsed, 6),
        "score_abs_tolerance": SCORE_TOLERANCE,
        "coordinate_abs_tolerance": COORDINATE_TOLERANCE,
        "relative_tolerance": 0.0,
        "per_sample": comparisons,
    }, regenerated


def main() -> int:
    """执行编译、夹具、109 样本逐框比较并写唯一证据。"""

    run_started = time.perf_counter()
    parser = argparse.ArgumentParser(description="S2A-T62 C99 主机 decode/NMS 参考核验")
    evidence_group = parser.add_mutually_exclusive_group()
    evidence_group.add_argument("--write-evidence", action="store_true", help="通过全部比较后创建 T62 主报告")
    evidence_group.add_argument("--refresh-evidence", action="store_true", help="通过全部比较后修订已知 SHA 的 T62 主报告")
    parser.add_argument("--skip-109", action="store_true", help="仅运行固定夹具供快速开发检查")
    args = parser.parse_args()

    initial_head = t29.current_git_head(ROOT)
    require(initial_head == BASELINE_HEAD, f"T62 基线 HEAD 不匹配：{initial_head}")
    parent, parent_sha = load_parent_report()
    previous_report_sha: str | None = None
    if args.write_evidence:
        require(not T62_EVIDENCE.exists(), f"拒绝覆盖既有 T62 证据：{T62_EVIDENCE}")
    elif args.refresh_evidence:
        require(T62_EVIDENCE.is_file() and not T62_EVIDENCE.is_symlink(), "待修订 T62 报告缺失或类型错误")
        previous_payload = T62_EVIDENCE.read_bytes()
        previous_report_sha = sha256_bytes(previous_payload)
        require(previous_report_sha == PREVIOUS_REPORT_SHA256, "待修订 T62 报告 SHA 不等于已审版本")
        previous_report = json.loads(previous_payload.decode("utf-8"))
        require(previous_report.get("task_id") == "S2A-T62" and previous_report.get("status") == "PASS_CPU_REFERENCE_ONLY", "待修订 T62 报告身份或状态不符")
    require(all(path.is_file() and not path.is_symlink() for path in (G0_SPEC, T01_PLAN, MANIFEST, T25_INDEX, T29_RUNNER, D6_REFERENCE, D9_REFERENCE, C_SOURCE, C_HEADER)), "T62 绑定源文件缺失或类型错误")

    with tempfile.TemporaryDirectory(prefix="s2a_t62_gcc_") as temporary:
        library, compile_record = compile_library(Path(temporary))
        try:
            fixture_results = run_fixtures(library)
            require(len(fixture_results) >= 5, "T01 语义夹具数量不足")
            error_contract_results = run_error_contract_tests(library)
            require(len(error_contract_results) == 5, "错误码负例数量不符")

            cpu_comparison: dict[str, Any] | None = None
            regenerated: dict[str, Any] | None = None
            if not args.skip_109:
                cpu_comparison, regenerated = compare_109_cpu_goldens(library, parent)
                require(cpu_comparison["samples_compared"] == SAMPLE_COUNT, "109 样本比较不完整")

            if args.write_evidence or args.refresh_evidence:
                require(cpu_comparison is not None and regenerated is not None, "写证据前必须完成 109 样本比较")
                require(sha256_file(T29_EVIDENCE) == parent_sha, "T29 父报告在比较期间发生变化")
                final_head = t29.current_git_head(ROOT)
                require(final_head == initial_head == BASELINE_HEAD, "T62 验证期间 Git HEAD 发生变化")
                if args.write_evidence:
                    require(not T62_EVIDENCE.exists(), f"拒绝覆盖 T62 证据：{T62_EVIDENCE}")
                else:
                    require(sha256_file(T62_EVIDENCE) == previous_report_sha, "T62 待修订报告在验证期间发生变化")
                evidence = {
                "schema_version": "gestureforge_s2a_t62_ps_decode_nms_c_reference_v1",
                "task_id": "S2A-T62",
                "status": "PASS_CPU_REFERENCE_ONLY",
                "baseline_git_head": BASELINE_HEAD,
                "runtime_git_head": final_head,
                "scope": {
                    "description": "tiny416 PS decode/NMS 可移植 C99 主机参考核，与冻结 D9 CPU 解码结果逐项比较。",
                    "sample_domain": "CPU_GOLDEN_INPUTS_ONLY",
                    "pl_connection": "NOT_PL_CONNECTED",
                    "vitis_build": "NOT_VITIS_BUILD",
                    "vivado_or_xsim": "NOT_RUN",
                    "whole_network_or_hardware_acceptance": "NOT_CLAIMED",
                    "g3_g4_g5": "NOT_ESTABLISHED",
                },
                "contract": {
                    "input_layout": {"head13": [3, 10, 13, 13], "head26": [3, 10, 26, 26]},
                    "numeric_input": "signed INT8 head bytes converted to float64 by corresponding G0 scale, same arrays passed to D9 and C",
                    "score_threshold": 0.25,
                    "nms_iou": 0.45,
                    "max_outputs": 15,
                    "score_absolute_tolerance": SCORE_TOLERANCE,
                    "coordinate_absolute_tolerance": COORDINATE_TOLERANCE,
                    "relative_tolerance": 0.0,
                    "class_and_source_order": "exact",
                    "raw_candidate_count": "exact",
                    "error_codes": {
                        "S2A_T62_INVALID_ARGUMENT": -1,
                        "S2A_T62_NONFINITE_INPUT": -2,
                        "S2A_T62_EXP_OVERFLOW": -3,
                        "S2A_T62_NO_MEMORY": -4,
                    },
                },
                "review_revision": {
                    "iteration": 2 if args.refresh_evidence else 1,
                    "supersedes_sha256": previous_report_sha,
                    "change_summary": "修复有限 tw/th 导致 exp 溢出时返回 -3，并验证参数/非有限输入/指数溢出负例失败时保持输出哨兵不变。" if args.refresh_evidence else "首次生成 T62 CPU C 参考证据。",
                },
                "toolchain": compile_record,
                "verification_run": {
                    "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                    "working_directory": str(ROOT),
                    "python_version": sys.version.split()[0],
                    "elapsed_seconds_before_evidence_write": round(time.perf_counter() - run_started, 6),
                    "exit_code_after_evidence_write": 0,
                },
                "fixture_verification": {
                    "status": "PASS",
                    "fixture_count": len(fixture_results),
                    "fixed_random_seed": 20260929,
                    "cases": fixture_results,
                },
                "error_contract_verification": {
                    "status": "PASS",
                    "failure_does_not_report_success": True,
                    "failure_preserves_output_and_counts": True,
                    "cases": error_contract_results,
                },
                "cpu_golden_comparison": cpu_comparison,
                "bindings": {
                    "g0_specification": {"path": "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md", "sha256": sha256_file(G0_SPEC)},
                    "s2a_plan": {"path": "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md", "sha256": sha256_file(T01_PLAN)},
                    "model_manifest": {"path": "report/evidence/S2A-T01/tiny416_model_manifest.json", "sha256": sha256_file(MANIFEST)},
                    "t25_golden_index": {"path": "report/evidence/S2A-T25/cpu_layer_golden_index.json", "sha256": sha256_file(T25_INDEX), "sample_count": SAMPLE_COUNT},
                    "t29_parent_report": {"path": "report/evidence/S2A-T29/cpu_decode_nms_reference.json", "sha256": parent_sha, "task_id": parent["task_id"], "status": parent["status"], "sample_count": len(parent["samples"])},
                    "t29_runtime_regenerated_sample_count": len(regenerated["samples"]),
                    "d9_decoder": {"path": "verification/s1_t02_d9_yolo_decode.py", "sha256": sha256_file(D9_REFERENCE)},
                    "d6_metrics_nms": {"path": "verification/s1_t02_d6_detection_metrics.py", "sha256": sha256_file(D6_REFERENCE)},
                    "t29_runner": {"path": "verification/s2a_decode_nms_reference.py", "sha256": sha256_file(T29_RUNNER)},
                    "c_source": {"path": "verification/s2a_ps_decode_nms_reference.c", "sha256": sha256_file(C_SOURCE)},
                    "c_header": {"path": "verification/s2a_ps_decode_nms_reference.h", "sha256": sha256_file(C_HEADER)},
                    "python_bridge_test": {"path": "verification/test_s2a_ps_decode_nms_c.py", "sha256": sha256_file(Path(__file__).resolve())},
                },
                "limitations": [
                    "只验证 T01 固定输入集合中的 109 个 T25 CPU head golden；不是独立 PL 输出比对。",
                    "C 代码是 host 可编译的参考核；未作为 Vitis 应用构建或集成到 PS。",
                    "未连接 PL、未运行 Vivado/XSim、未执行上板验证。",
                    "结果不表示完整 layer/network、G3、G4 或 G5 已通过。",
                ],
            }
                T62_EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
                rendered = (json.dumps(evidence, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
                open_mode = "wb" if args.refresh_evidence else "xb"
                with T62_EVIDENCE.open(open_mode) as stream:
                    stream.write(rendered)
                print(
                    f"T62_EVIDENCE_PASS samples=109 fixtures={len(fixture_results)} errors={len(error_contract_results)} "
                    f"evidence={T62_EVIDENCE.relative_to(ROOT).as_posix()} sha256={sha256_bytes(rendered)}",
                    flush=True,
                )
            else:
                print(f"T62_LOCAL_CHECK_PASS fixtures={len(fixture_results)} samples={0 if cpu_comparison is None else cpu_comparison['samples_compared']}")
        finally:
            unload_library(library)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
