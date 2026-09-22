"""GestureForge 三模型摄像头对比网页的本地服务。

服务只在本机接收浏览器主动提交的单帧 JPEG，不保存用户摄像头图像。
模型路径、配置和权重均为只读绑定，便于后续在不改网页接口的情况下回滚模型。
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = Path(tempfile.gettempdir()) / "gestureforge_web_runtime"

# 该可执行文件来自已有的 Darknet 激活校准构建，不会修改仓库外源码或权重。
DARKNET_EXE = Path(
    r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_activation_calibration_r1\darknet_build\Release\darknet.exe"
)
DARKNET_DLL_DIRS = (
    Path(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\x64"),
    Path(
        r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_activation_calibration_r1\darknet_source\3rdparty\pthreads\bin"
    ),
)
NAMES_PATH = Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\gesture.names")
MANIFEST_PATH = Path(r"D:\FPGA_Data\HaGRIDv2\manifest.csv")

CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "tiny320": {
        "label": "YOLOv4-tiny 320",
        "short_label": "tiny320",
        "input_size": "320×320",
        "role": "board_candidate",
        "cfg": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny320_formal_r2\configs\gesture_yolov4_tiny_320_d8_formal.cfg"
        ),
        "data": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny320_formal_r2\data\gesture_tiny320_d8_formal.data"
        ),
        "weights": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny320_formal_r2\checkpoints\gesture_yolov4_tiny_320_d8_formal_final.weights"
        ),
        "stage_status": "正式权重候选；待最终三关冻结",
        "evidence_note": "val mAP@0.5=0.9208（候选测量，非摄像头准确率）",
        "evidence_path": "report/evidence/S1-T02/20260921_s1_t02_d6_tiny320_val_formal_clip_r1_summary.md",
        "evidence_sha256": "91eb2b4ce33c28fc2896a766ee2990f894d29de3f50f25ec8ba32b2a0a17cd70",
    },
    "tiny416": {
        "label": "YOLOv4-tiny 416",
        "short_label": "tiny416",
        "input_size": "416×416",
        "role": "board_candidate",
        "cfg": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\configs\gesture_yolov4_tiny_416_d8_formal.cfg"
        ),
        "data": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\data\gesture_tiny416_d8_formal.data"
        ),
        "weights": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\checkpoints\gesture_yolov4_tiny_416_d8_formal_final.weights"
        ),
        "stage_status": "阶段一优先候选；官方 test 已过数值门槛",
        "evidence_note": "official test mAP@0.5=0.9774，mAP@0.5:0.95=0.7701",
        "evidence_path": "report/evidence/S1-T02/20260922_s1_t02_d6_tiny416_test_formal_clip_r1.json",
        "evidence_sha256": "5419a98cf03074304b7685d765e9bc0e35956df87665bd5cc1fb9e161695554d",
    },
    "full608": {
        "label": "YOLOv4 full 608",
        "short_label": "full608",
        "input_size": "608×608",
        "role": "pc_only_reference",
        "cfg": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r9_resume1000\configs\yolov4_5class_608_formal_r6_random0.cfg"
        ),
        "data": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r9_resume1000\data\gesture_full608_random0_resume1000.data"
        ),
        "weights": Path(
            r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d4_full608_formal_r9_resume1000\checkpoints\yolov4_5class_608_formal_r6_random0_final.weights"
        ),
        "stage_status": "PC 对照；不进入阶段一板上资源门",
        "evidence_note": "val mAP@0.5=0.9895（PC 对照测量，非板上结论）",
        "evidence_path": "report/evidence/S1-T02/20260921_s1_t02_d6_full608_val_formal_clip_r1_summary.md",
        "evidence_sha256": "16cc9a9f58eba936f802a22758d7dedb5c52706234c4b25738dc4f862e195511",
    },
}

POLICY = {
    "float_gate": {
        "map50_min": 0.90,
        "map5095_min": 0.70,
        "per_class_precision_min": 0.90,
        "per_class_recall_min": 0.90,
    },
    "quantization_gate": {
        "map50_absolute_drop_max": 0.05,
        "per_class_recall_absolute_drop_max": 0.05,
    },
    "web_accuracy_semantics": "人工摄像头样本估计；由用户逐帧标记，不替代固定 test mAP",
    "no_hand": "阶段一非阻断诊断项；no_gesture 不改写为 no_hand",
}

_PREDICTION_PATTERN = re.compile(
    r"^\s*(?P<label>fist|palm|one|two_up|three):\s*"
    r"(?P<score>\d+(?:\.\d+)?)%\s+"
    r"\(left_x:\s*(?P<x>-?\d+(?:\.\d+)?)\s+"
    r"top_y:\s*(?P<y>-?\d+(?:\.\d+)?)\s+"
    r"width:\s*(?P<w>-?\d+(?:\.\d+)?)\s+"
    r"height:\s*(?P<h>-?\d+(?:\.\d+)?)\)",
    re.MULTILINE,
)
_PREDICTED_TIME_PATTERN = re.compile(r"Predicted in\s+(?P<ms>\d+(?:\.\d+)?)\s+milli-seconds")
_ANSI_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_MODEL_LOCK = threading.Lock()
_FILE_HASH_CACHE: dict[str, str] = {}


def _sha256(path: Path) -> str:
    """计算只读文件 SHA-256，并在本地服务进程内缓存。"""

    key = str(path)
    if key in _FILE_HASH_CACHE:
        return _FILE_HASH_CACHE[key]
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    value = digest.hexdigest()
    _FILE_HASH_CACHE[key] = value
    return value


def _augment_runtime_path() -> dict[str, str]:
    """只为 Darknet 子进程补充 CUDA 与 pthread DLL 搜索路径。"""

    environment = os.environ.copy()
    existing = environment.get("PATH", "").split(os.pathsep)
    additions = [str(path) for path in DARKNET_DLL_DIRS if path.is_dir()]
    environment["PATH"] = os.pathsep.join(additions + existing)
    return environment


def _write_runtime_data_file(workspace: Path | None = None) -> Path:
    """生成只包含类别映射的隔离 data 文件，避免读取训练集标签。"""

    root = workspace or RUNTIME_ROOT
    root.mkdir(parents=True, exist_ok=True)
    data_path = root / "gestureforge_web.data"
    names_for_darknet = str(NAMES_PATH).replace("\\", "/")
    contents = f"classes=5\nnames={names_for_darknet}\n"
    if not data_path.exists() or data_path.read_text(encoding="utf-8") != contents:
        data_path.write_text(contents, encoding="utf-8", newline="\n")
    return data_path


def _validate_registry() -> list[str]:
    """返回所有缺失绑定，不对外部数据或权重做任何写操作。"""

    missing: list[str] = []
    for label, path in [("darknet_executable", DARKNET_EXE), ("names", NAMES_PATH)]:
        if not path.is_file():
            missing.append(f"{label}: {path}")
    for model_id, model in MODEL_REGISTRY.items():
        for field in ("cfg", "data", "weights"):
            path = model[field]
            if not path.is_file():
                missing.append(f"{model_id}.{field}: {path}")
    return missing


def _model_payload(model_id: str, include_paths: bool = False) -> dict[str, Any]:
    model = MODEL_REGISTRY[model_id]
    weights = model["weights"]
    runtime_data = _write_runtime_data_file()
    payload: dict[str, Any] = {
        "id": model_id,
        "label": model["label"],
        "short_label": model["short_label"],
        "input_size": model["input_size"],
        "role": model["role"],
        "stage_status": model["stage_status"],
        "evidence_note": model["evidence_note"],
        "evidence_path": model["evidence_path"],
        "evidence_sha256": model["evidence_sha256"],
        "available": weights.is_file()
        and model["cfg"].is_file()
        and model["data"].is_file(),
        "weights_file": weights.name,
        "weights_bytes": weights.stat().st_size if weights.is_file() else None,
        "weights_sha256": _sha256(weights) if weights.is_file() else None,
        "cfg_sha256": _sha256(model["cfg"]) if model["cfg"].is_file() else None,
        "data_sha256": _sha256(model["data"]) if model["data"].is_file() else None,
        "names_path": str(NAMES_PATH),
        "names_sha256": _sha256(NAMES_PATH) if NAMES_PATH.is_file() else None,
        "darknet_executable": str(DARKNET_EXE),
        "darknet_executable_sha256": _sha256(DARKNET_EXE) if DARKNET_EXE.is_file() else None,
        "runtime_data_path": str(runtime_data),
        "runtime_data_sha256": _sha256(runtime_data),
        "manifest_path": str(MANIFEST_PATH),
        "manifest_sha256": _sha256(MANIFEST_PATH) if MANIFEST_PATH.is_file() else None,
    }
    if include_paths:
        payload["cfg"] = str(model["cfg"])
        payload["data"] = str(model["data"])
        payload["weights"] = str(weights)
    return payload


def _parse_predictions(output: str) -> list[dict[str, Any]]:
    """从 Darknet ext_output 中提取有界框结果。"""

    cleaned = _ANSI_PATTERN.sub("", output)
    predictions: list[dict[str, Any]] = []
    for match in _PREDICTION_PATTERN.finditer(cleaned):
        score_pct = float(match.group("score"))
        predictions.append(
            {
                "class_name": match.group("label"),
                "confidence": round(score_pct / 100.0, 6),
                "confidence_pct": round(score_pct, 3),
                "box": {
                    "left": float(match.group("x")),
                    "top": float(match.group("y")),
                    "width": float(match.group("w")),
                    "height": float(match.group("h")),
                },
            }
        )
    predictions.sort(key=lambda item: item["confidence"], reverse=True)
    return predictions[:15]


def _run_prediction(model_id: str, image_path: Path, working_root: Path | None = None) -> dict[str, Any]:
    """调用单个固定模型并返回解析后的检测结果。"""

    model = MODEL_REGISTRY[model_id]
    root = working_root or RUNTIME_ROOT
    data_path = _write_runtime_data_file(root)
    command = [
        str(DARKNET_EXE),
        "detector",
        "test",
        str(data_path),
        str(model["cfg"]),
        str(model["weights"]),
        str(image_path),
        "-dont_show",
        "-ext_output",
        "-thresh",
        "0.25",
    ]
    started = time.perf_counter()
    with _MODEL_LOCK:
        completed = subprocess.run(
            command,
            cwd=root,
            env=_augment_runtime_path(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=45,
            check=False,
        )
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    output = completed.stdout.decode("utf-8", errors="replace")
    if completed.returncode != 0:
        tail = output[-1200:].strip()
        raise RuntimeError(f"Darknet 返回码 {completed.returncode}: {tail}")
    predictions = _parse_predictions(output)
    predicted_match = _PREDICTED_TIME_PATTERN.search(output)
    darknet_ms = float(predicted_match.group("ms")) if predicted_match else None
    return {
        "model": _model_payload(model_id),
        "predictions": predictions,
        "elapsed_ms": round(elapsed_ms, 1),
        "darknet_ms": darknet_ms,
        "threshold": 0.25,
        "nms_iou": 0.45,
        "max_outputs": 15,
    }


def _cleanup_request_root(request_root: Path | None) -> str | None:
    """在响应前重试清理 Darknet 生成的输入帧和输出文件。"""

    if request_root is None or not request_root.exists():
        return None
    last_error: OSError | None = None
    for attempt in range(8):
        try:
            shutil.rmtree(request_root)
            return None
        except FileNotFoundError:
            return None
        except OSError as error:
            last_error = error
            time.sleep(0.05 * (attempt + 1))
    return f"临时工作目录清理失败: {request_root}; {last_error}"


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


class GestureForgeHandler(BaseHTTPRequestHandler):
    """提供静态页面和本机模型推理 API。"""

    server_version = "GestureForgeWeb/1.0"

    def log_message(self, format_string: str, *args: Any) -> None:
        # 避免摄像头连续检测时刷屏，只保留错误由请求响应返回。
        return

    def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = _json_bytes(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            try:
                self._send_bytes((WEB_ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            except OSError as error:
                self._send_json({"error": f"网页文件读取失败: {error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if self.path == "/api/health":
            missing = _validate_registry()
            self._send_json({"ok": not missing, "missing": missing})
            return
        if self.path == "/api/models":
            self._send_json(
                {
                    "models": [_model_payload(model_id) for model_id in MODEL_REGISTRY],
                    "policy": POLICY,
                }
            )
            return
        self._send_json({"error": "路径不存在"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/predict":
            self._send_json({"error": "路径不存在"}, HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Content-Length 无效"}, HTTPStatus.BAD_REQUEST)
            return
        if length <= 0 or length > 8 * 1024 * 1024:
            self._send_json({"error": "单帧请求必须在 8 MiB 以内"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            model_id = str(payload.get("model", ""))
            image_data = str(payload.get("image_data", ""))
            if model_id not in MODEL_REGISTRY:
                raise ValueError("model 必须是 tiny320、tiny416 或 full608")
            if "," not in image_data or not image_data.startswith("data:image/"):
                raise ValueError("image_data 必须是浏览器 data URL")
            encoded = image_data.split(",", 1)[1]
            image_bytes = base64.b64decode(encoded, validate=True)
            if len(image_bytes) > 6 * 1024 * 1024:
                raise ValueError("JPEG 单帧超过 6 MiB")
            if not image_bytes.startswith(b"\xff\xd8"):
                raise ValueError("当前接口只接受 JPEG 摄像头帧")
        except (UnicodeDecodeError, json.JSONDecodeError, binascii.Error, ValueError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return

        image_path: Path | None = None
        request_root: Path | None = None
        response_payload: Any
        response_status = HTTPStatus.OK
        try:
            RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
            request_root = Path(tempfile.mkdtemp(prefix="request_", dir=RUNTIME_ROOT))
            image_path = request_root / "frame.jpg"
            image_path.write_bytes(image_bytes)
            response_payload = _run_prediction(model_id, image_path, request_root)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            response_payload = {"error": str(error)}
            response_status = HTTPStatus.INTERNAL_SERVER_ERROR
        cleanup_error = _cleanup_request_root(request_root)
        if cleanup_error is not None:
            response_payload = {
                "error": cleanup_error,
                "inference_error": response_payload.get("error") if isinstance(response_payload, dict) else None,
            }
            response_status = HTTPStatus.INTERNAL_SERVER_ERROR
        self._send_json(response_payload, response_status)


def _check_payload() -> dict[str, Any]:
    missing = _validate_registry()
    return {
        "ok": not missing,
        "project_root": str(PROJECT_ROOT),
        "darknet_executable": {
            "path": str(DARKNET_EXE),
            "bytes": DARKNET_EXE.stat().st_size if DARKNET_EXE.is_file() else None,
            "sha256": _sha256(DARKNET_EXE) if DARKNET_EXE.is_file() else None,
        },
        "models": [_model_payload(model_id, include_paths=True) for model_id in MODEL_REGISTRY],
        "missing": missing,
        "policy": POLICY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="GestureForge 三模型摄像头对比本地服务")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认只监听本机")
    parser.add_argument("--port", type=int, default=8765, help="监听端口")
    parser.add_argument("--check", action="store_true", help="只检查模型绑定并输出 JSON")
    args = parser.parse_args()

    if args.check:
        payload = _check_payload()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 2

    missing = _validate_registry()
    if missing:
        print(json.dumps({"ok": False, "missing": missing}, ensure_ascii=False, indent=2))
        return 2
    _write_runtime_data_file()
    server = ThreadingHTTPServer((args.host, args.port), GestureForgeHandler)
    print(f"GestureForge 网页已启动: http://{args.host}:{args.port}/")
    print("按 Ctrl+C 停止；摄像头帧只在请求期间写入系统临时目录并立即删除。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
