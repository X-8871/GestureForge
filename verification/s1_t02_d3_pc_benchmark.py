"""阶段一 D3 的 PC 模型性能基准。

一次加载固定 Darknet 模型后连续送入确定性的图片路径，丢弃 warmup，
只对 Darknet 输出的 Predicted in 时间统计，不把进程装载时间混入模型延迟。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"D:\FPGA_Data\HaGRIDv2")
MANIFEST_PATH = DATA_ROOT / "manifest.csv"
RUNTIME_ROOT = Path(os.environ.get("TEMP", r"C:\Windows\Temp")) / "gestureforge_web_runtime"
PREDICTED_TIME_PATTERN = re.compile(r"Predicted in\s+(?P<ms>\d+(?:\.\d+)?)\s+milli-seconds")

# 从网页注册表复用同一组只读模型绑定，避免基准与网页指向不同权重。
sys.path.insert(0, str(REPOSITORY_ROOT))
from web.gestureforge_web import (
    DARKNET_EXE,
    MODEL_REGISTRY,
    NAMES_PATH,
    _augment_runtime_path,
    _sha256,
    _write_runtime_data_file,
)


def _percentile(values: list[float], percentile: float) -> float:
    """使用 nearest-rank 计算可复核的百分位。"""

    if not values:
        raise ValueError("没有可用延迟样本")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile / 100.0 * len(ordered)))
    return ordered[rank - 1]


def _select_images(limit: int = 20) -> list[Path]:
    """按 manifest 顺序选择固定 test 图片，保证跨次运行输入一致。"""

    images: list[Path] = []
    with MANIFEST_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("split") != "test":
                continue
            image_path = DATA_ROOT / str(row["image"])
            if image_path.is_file():
                images.append(image_path)
            if len(images) >= limit:
                break
    if len(images) < limit:
        raise RuntimeError(f"固定 test 图片不足 {limit} 张，实际为 {len(images)} 张")
    return images


def _run_darknet(model_id: str, image_paths: list[Path], total_samples: int, timeout_s: int) -> str:
    """启动一次 Darknet，连续输入图片路径并合并读取所有输出。"""

    model = MODEL_REGISTRY[model_id]
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix="benchmark_", dir=RUNTIME_ROOT))
    data_path = _write_runtime_data_file(run_root)
    command = [
        str(DARKNET_EXE),
        "detector",
        "test",
        str(data_path),
        str(model["cfg"]),
        str(model["weights"]),
        "-dont_show",
        "-ext_output",
        "-thresh",
        "0.25",
    ]
    input_text = "".join(f"{image_paths[index % len(image_paths)]}\n" for index in range(total_samples))
    try:
        completed = subprocess.run(
            command,
            cwd=run_root,
            env=_augment_runtime_path(),
            input=input_text,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"Darknet 返回码 {completed.returncode}: {completed.stdout[-2000:]}")
        return completed.stdout
    finally:
        shutil.rmtree(run_root, ignore_errors=True)


def run_benchmark(model_id: str, warmup: int, valid: int, timeout_s: int) -> dict[str, Any]:
    if model_id not in MODEL_REGISTRY:
        raise ValueError(f"未知模型: {model_id}")
    if warmup < 0 or valid <= 0:
        raise ValueError("warmup 必须非负，valid 必须为正")
    model = MODEL_REGISTRY[model_id]
    missing = [str(model[field]) for field in ("cfg", "data", "weights") if not model[field].is_file()]
    if not DARKNET_EXE.is_file() or missing:
        raise FileNotFoundError(f"模型绑定缺失: {missing}")
    images = _select_images()
    output = _run_darknet(model_id, images, warmup + valid, timeout_s)
    measurements = [float(match.group("ms")) for match in PREDICTED_TIME_PATTERN.finditer(output)]
    if len(measurements) < warmup + valid:
        raise RuntimeError(f"Darknet 只返回 {len(measurements)} 个延迟，期望 {warmup + valid}")
    measured = measurements[warmup : warmup + valid]
    image_list_digest = hashlib.sha256("\n".join(str(path) for path in images).encode("utf-8")).hexdigest()
    return {
        "schema_version": "s1-t02-d3-pc-benchmark-v1",
        "task": "S1-T02-D3",
        "status": "MEASURED_PC_MODEL_ONLY",
        "observed_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "model": {
            "id": model_id,
            "label": model["label"],
            "role": model["role"],
            "input_size": model["input_size"],
            "cfg": str(model["cfg"]),
            "cfg_sha256": _sha256(model["cfg"]),
            "data": str(model["data"]),
            "data_sha256": _sha256(model["data"]),
            "names": str(NAMES_PATH),
            "names_sha256": _sha256(NAMES_PATH),
            "darknet_executable": str(DARKNET_EXE),
            "darknet_executable_sha256": _sha256(DARKNET_EXE),
            "manifest": str(MANIFEST_PATH),
            "manifest_sha256": _sha256(MANIFEST_PATH),
            "weights": str(model["weights"]),
            "weights_sha256": _sha256(model["weights"]),
            "weights_bytes": model["weights"].stat().st_size,
            "threshold": 0.25,
            "nms_iou": 0.45,
            "max_outputs": 15,
        },
        "runtime_binding": {
            "data_filename": "gestureforge_web.data",
            "runtime_data_sha256": "7dbb0f6b017adf7c1d60aa1c6c372370f04847090192a90d9352157b11464128",
            "working_directory": "每次基准运行使用独立临时目录，结束后整体删除。",
        },
        "input": {
            "source_manifest": str(MANIFEST_PATH),
            "source_manifest_sha256": _sha256(MANIFEST_PATH),
            "fixed_test_images": len(images),
            "image_list_sha256": image_list_digest,
            "sampling": "按 manifest 顺序循环固定 20 张 test 图片；性能统计不作精度结论。",
        },
        "samples": {
            "warmup": warmup,
            "valid": valid,
            "returned_predictions": len(measurements),
            "timeout": 0,
            "drop": 0,
            "failure": 0,
        },
        "model_inference_ms": {
            "mean": round(mean(measured), 6),
            "p50": round(_percentile(measured, 50), 6),
            "p95": round(_percentile(measured, 95), 6),
            "p99": round(_percentile(measured, 99), 6),
            "min": round(min(measured), 6),
            "max": round(max(measured), 6),
        },
        "limitations": [
            "仅统计 Darknet 输出的模型推理时间，不含进程装载、网页传输、预处理、解码/NMS 和显示。",
            "PC 测量不等于 AX7020 板上资源、时序或实时性能通过。",
            "完整 YOLOv4 仍为 PC 对照，不进入阶段一板上资源门。",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="GestureForge 阶段一 D3 PC 性能基准")
    parser.add_argument("--model", choices=sorted(MODEL_REGISTRY), required=True, help="模型注册表 ID")
    parser.add_argument("--warmup", type=int, default=100, help="warmup 次数，默认 100")
    parser.add_argument("--valid", type=int, default=1000, help="有效样本数，默认 1000")
    parser.add_argument("--timeout", type=int, default=900, help="Darknet 最大秒数，默认 900")
    parser.add_argument("--output", type=Path, required=True, help="UTF-8 JSON 输出路径")
    args = parser.parse_args()
    report = run_benchmark(args.model, args.warmup, args.valid, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report["model_inference_ms"], ensure_ascii=False))
    print(f"写入: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
