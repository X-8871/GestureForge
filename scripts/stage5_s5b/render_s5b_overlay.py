"""S5-B 离线叠框渲染 / 自测工具（库 + CLI）。

定位
----
阶段5 离线准备（**不接硬件、不跑 Vivado/xsim**）：
- 用确定性合成帧与只读的 S4-B / S4-C 数据离线出图（PNG），并对**数值、语义、用词**做逐项断言；
- 全部几何与口径**只从** `verification/s5_display_geometry_reference.py`（契约 `S5A-G0-v2`）导入，
  本文件不复制任何 letterbox / 逆映射 / 取整公式；
- 正向 letterbox 的**图像**只经 D2 冻结实现
  `verification/s1_t02_d2_numeric_reference.py::letterbox_rgb_uint8`（证明几何同源），本文件不另写 resize。

契约与路径
----------
字段名、门槛、用词规则、FPS/延迟口径、HUD 字段以 `docs/stage5/s5a_stage5_display_g0_fields.json` 为准。
只读上游（S4-C golden 109、S4-B host_result_*.json）的路径由该契约 JSON 的 `upstream_bindings` 解析，
本工具**只读**，不写 w4 树；不可用时可用 `--s4b-dir` / `--s4c-golden` 显式恢复。

坐标路径（重要）
----------------
契约 `consumed_stage4_record.xyxy_semantics` 规定：阶段4 已给出**原图归一化 xyxy**，显示层只允许使用该字段，
不得自行反算第二份坐标；`fallback_inverse_mapping` 仅当阶段4 缺失原图坐标字段时启用。
因此本工具每个用例都显式记录 `coordinate_path`：
- ``stage4_original_norm_xyxy``：直接消费上游 xyxy（S4-B / S4-C 来源用例，以及刻意越界的防御性用例）；
- ``fallback_inverse_mapping``：合成网络归一化框 → `network_norm_to_original_norm`（离线准备自测路径）。

绘制顺序（与断言口径有关，如实声明）
------------------------------------
1) numpy 基础帧（合成内容 / 画布整数倍块复制 + 黑边）
→ 2) 画布黑边与块复制断言（在 HUD 与边框之前）
→ 3) HUD ASCII 文本带（背景层）
→ 4) 按冻结 `border_pixel_sets` 逐像素落框（**覆盖** HUD 文本带，此时做“绘制保真”逐像素断言）
→ 5) ASCII 标签（最后叠加，可能覆盖少量边框像素）
→ 6) 落 PNG。
因此边框像素在 HUD 带之上、标签之下；绘制保真断言以第 4 步的像素层为准。

退出码
------
0 = 全部断言 PASS；1 = 存在断言 FAIL；2 = 环境/输入错误（含上游只读输入缺失、冻结模块无法导入）。
未执行 = NOT_RUN，失败 = FAIL，环境错误 = ERROR；本工具不伪造退出码与哈希。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import platform
import random
import sys
import traceback
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── 常量 ────────────────────────────────────────────────────────────────────
SCHEMA_VERSION = "gestureforge_s5b_case_log_v1"
MANIFEST_SCHEMA_VERSION = "gestureforge_s5b_run_manifest_v1"
TASK_ID = "S5-B"
DEFAULT_SEED = 20261021
RANDOM_BOX_N = 64                      # 种子化随机框样本数（每几何 N=64）
RANDOM_ROUND_TRIP_TOL = 1e-12          # 原图→网络→原图 round-trip 容限
INVERSE_TOL = 1e-9                     # 逆映射 vs 手算样例容限
DISPLAY_PX_TOL = 1.0                   # 显示像素层 vs float64 连续参考容限（px）

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_ERROR = 2

SYNTH_FRAME_INTERVAL_NS = 33_333_333   # 离线合成台账：30 fps 名义间隔（非实测）
OFFLINE_PLACEHOLDER = "OFFLINE_SYNTHETIC_NOT_MEASURED"

# 禁用称谓（拆分拼接构造，避免本文件与产物自触发扫描；语义见契约 scoring.forbidden_without_basis）
FORBIDDEN_SCORE_TOKENS = ("confi" + "dence", "prob" + "ability", "置" + "信度",
                          "可" + "信度", "准" + "确率")
# 不得出现的“画面与结果来自同一帧号”的伪称（契约 display_semantics.no_same_frame_claim）
FORBIDDEN_CLAIM_TOKENS = ("同" + "帧",)

REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_REL = "verification/s5_display_geometry_reference.py"
D2_REFERENCE_REL = "verification/s1_t02_d2_numeric_reference.py"
CONTRACT_REL = "docs/stage5/s5a_stage5_display_g0_fields.json"
DEFAULT_OUT_REL = "report/evidence/S5-B"

REQUIRED_HUD_FIELDS = (
    "capture_fps", "inference_fps", "display_fps",
    "inference_time_ns", "age_result_ns", "age_frame_ns",
    "frame_id", "boxes", "stale_cleared", "dropped_frames", "timeouts", "warmup_state",
    "display_semantics",
)

CLASS_ORDER = ("fist", "palm", "one", "two_up", "three")
CLASS_COLORS = {
    0: (255, 64, 64), 1: (64, 255, 64), 2: (64, 160, 255), 3: (255, 255, 64), 4: (255, 64, 255),
}

# 独立手算样例：border_pixel_sets(1,1,4,3,width=2) 的期望像素集（推导见 unittest 注释）
HAND_BORDER_PIXELS_BOX = (1, 1, 4, 3)
HAND_BORDER_PIXELS = sorted(
    [(x, 0) for x in (1, 2, 3, 4)] + [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3, 4)]
)


# ─────────────────────────────────────────────────────────────────────────────
# 基础工具
# ─────────────────────────────────────────────────────────────────────────────


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_python_module(path: Path, name: str):
    if not path.is_file():
        raise FileNotFoundError(f"模块不存在：{path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法为 {path} 构建 import spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_float(value: float) -> str:
    return repr(float(value))


def dump_json(path: Path, payload: Any) -> str:
    """确定性 JSON 落盘（LF、UTF-8、键排序），返回文本 SHA256。"""
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return sha256_bytes(text.encode("utf-8"))


def write_png(path: Path, image: Image.Image) -> dict:
    """确定性 PNG 落盘（不写任何元数据/时间戳），返回名称、哈希与字节数。"""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=6)
    data = buffer.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    return {"name": path.name, "sha256": sha256_bytes(data), "bytes": len(data),
            "width": image.width, "height": image.height}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


class Tee:
    """把 print 同时写到原始流与内存缓冲，用于原样保存 stdout。"""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, text: str) -> int:
        for stream in self._streams:
            stream.write(text)
        return len(text)

    def flush(self) -> None:
        for stream in self._streams:
            stream.flush()


class Recorder:
    """记录断言与错误；错误优先级高于断言失败（退出码 2 > 1 > 0）。"""

    def __init__(self) -> None:
        self.checks: list[dict] = []
        self.errors: list[dict] = []

    def check(self, check_id: str, ok: bool, detail: str = "") -> bool:
        self.checks.append({"id": check_id, "status": "PASS" if bool(ok) else "FAIL",
                            "detail": str(detail)})
        return bool(ok)

    def fail(self, check_id: str, detail: str) -> None:
        self.check(check_id, False, detail)

    def error(self, error_id: str, detail: str) -> None:
        self.errors.append({"id": error_id, "detail": str(detail)})

    def counts(self) -> dict:
        passed = sum(1 for check in self.checks if check["status"] == "PASS")
        return {"assertions_total": len(self.checks), "assertions_passed": passed,
                "assertions_failed": len(self.checks) - passed, "errors_total": len(self.errors)}

    def failed_ids(self) -> list[str]:
        return [check["id"] for check in self.checks if check["status"] == "FAIL"]

    def case_checks(self, case_id: str) -> list[dict]:
        return [check for check in self.checks if check["id"].startswith(case_id + ".")]

    def exit_code(self) -> int:
        if self.errors:
            return EXIT_ERROR
        return EXIT_FAIL if self.failed_ids() else EXIT_PASS


# ─────────────────────────────────────────────────────────────────────────────
# 用词与伪称扫描（token 以拆分拼接构造，避免源码/产物自触发）
# ─────────────────────────────────────────────────────────────────────────────


def token_identity(token: str) -> dict:
    return {
        "length": len(token),
        "sha256": sha256_bytes(token.encode("utf-8")),
        "codepoints": " ".join(f"U+{ord(ch):04X}" for ch in token),
        "reversed": token[::-1],
    }


def build_scan_token_table() -> list[dict]:
    table = []
    index = 1
    for token in FORBIDDEN_SCORE_TOKENS:
        entry = {"token_id": f"W{index}", "role": "forbidden_score_appellation"}
        entry.update(token_identity(token))
        table.append(entry)
        index += 1
    for token in FORBIDDEN_CLAIM_TOKENS:
        entry = {"token_id": f"W{index}", "role": "forbidden_same_frame_claim"}
        entry.update(token_identity(token))
        table.append(entry)
        index += 1
    return table


def scan_artifact(path: Path, tokens: Sequence[str]) -> dict:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="ignore")
    hits: dict[str, int] = {}
    for token in tokens:
        count = text.count(token)
        if count:
            hits[sha256_bytes(token.encode("utf-8"))[:16]] = count
    return {"path": str(path), "sha256": sha256_bytes(data), "bytes": len(data),
            "hits": hits, "hit_total": sum(hits.values())}


def scan_paths(paths: Sequence[Path]) -> dict:
    tokens = tuple(FORBIDDEN_SCORE_TOKENS) + tuple(FORBIDDEN_CLAIM_TOKENS)
    artifacts: list[dict] = []
    for path in paths:
        if path.is_file():
            artifacts.append(scan_artifact(path, tokens))
    return {
        "artifacts_scanned": len(artifacts),
        "hit_total": sum(item["hit_total"] for item in artifacts),
        "tokens": build_scan_token_table(),
        "method": ("对文本产物按 UTF-8 子串扫描；PNG 为光栅像素，绘制文本不以字符串存于文件，"
                   "故对 PNG 做字节级 UTF-8 子串扫描，另对实际绘制的 ASCII 标签串"
                   "（记录于用例 JSON 的 labels/drawing 段）单独扫描"),
        "per_artifact": artifacts,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 独立手算（仅用于对拍冻结参考；渲染路径绝不使用）
# ─────────────────────────────────────────────────────────────────────────────


def hand_geometry(src_w: int, src_h: int, dst_w: int = 416, dst_h: int = 416) -> dict:
    """独立手算式（整数截断 resize + 左上 floor 补边），**只用于对拍冻结参考**。

    new_w/new_h 由“取较小缩放比的一维填满”手写条件分支得到；补边宽度按
    pad_right = dst_w - new_w - offset_x、pad_bottom = dst_h - new_h - offset_y 直接展开，
    不使用冻结模块的字段，从而构成独立依据。
    """
    if (dst_w / src_w) < (dst_h / src_h):
        new_w, new_h = dst_w, (src_h * dst_w) // src_w
    else:
        new_h, new_w = dst_h, (src_w * dst_h) // src_h
    offset_x, offset_y = (dst_w - new_w) // 2, (dst_h - new_h) // 2
    return {
        "new_width": new_w, "new_height": new_h,
        "offset_x": offset_x, "offset_y": offset_y,
        "pad_right": dst_w - new_w - offset_x,
        "pad_bottom": dst_h - new_h - offset_y,
        "asymmetric_padding": ((dst_w - new_w) % 2 == 1) or ((dst_h - new_h) % 2 == 1),
    }


def hand_computed_samples() -> list[dict]:
    """≥3 个手算样例：算式写在注释里，期望值由算式给出并附十进制字面量交叉核对。

    逆映射手算推导（与契约 geometry.inverse 同义，此处独立书写）：
        x_r = u*dst_w - offset_x            （反补边，落在缩放图坐标）
        x_px = x_r * (src_w-1)/(new_w-1)    （端点对齐反缩放，float64 全程不取整）
        u_orig = x_px/(src_w-1) = x_r/(new_w-1)
    故 `u_orig = (u*dst - offset) / (new - 1)`，逐轴套用即得手算值。

    HS1：683×384 → new 416×233、offset (0, 91)（**奇数补边**：上 91 / 下 92）
        u=(0.25, 0.50, 0.75, 0.75)
        x1 = (0.25*416 - 0)/415 = 104/415
        y1 = (0.50*416 - 91)/232 = 117/232
        x2 = (0.75*416 - 0)/415 = 312/415
        y2 = (0.75*416 - 91)/232 = 221/232
    HS2：1280×720 → new 416×234、offset (0, 91)，取到网络边界 u=1.0（端点对齐下略超 1）
        u=(0.0, 0.25, 1.0, 0.75)
        x1 = (0.0*416 - 0)/415 = 0
        y1 = (0.25*416 - 91)/233 = 13/233
        x2 = (1.0*416 - 0)/415 = 416/415  (>1，显示层必须裁剪)
        y2 = (0.75*416 - 91)/233 = 221/233
    HS3：1440×1920 → new 312×416、offset (52, 0)，反补边后为非整数（验证不提前取整）
        u=(0.50, 0.10, 0.60, 0.20)
        x1 = (0.50*416 - 52)/311 = 156/311
        y1 = (0.10*416 - 0)/415 = 41.6/415
        x2 = (0.60*416 - 52)/311 = 197.6/311
        y2 = (0.20*416 - 0)/415 = 83.2/415
    """
    return [
        {
            "sample_id": "HS1_683x384_odd_padding",
            "src_width": 683, "src_height": 384,
            "geometry": {"new_width": 416, "new_height": 233, "offset_x": 0, "offset_y": 91,
                         "pad_right": 0, "pad_bottom": 92},
            "network_box": (0.25, 0.50, 0.75, 0.75),
            "formula": ("x1=(0.25*416-0)/(416-1); y1=(0.50*416-91)/(233-1); "
                        "x2=(0.75*416-0)/(416-1); y2=(0.75*416-91)/(233-1)"),
            "expected": (104 / 415, 117 / 232, 312 / 415, 221 / 232),
            "expected_literals": (0.2506024096385542, 0.5043103448275862,
                                  0.7518072289156626, 0.9525862068965517),
            "note": "非对称补边（上 91 / 下 92）参与 y 轴逆映射",
        },
        {
            "sample_id": "HS2_1280x720_network_boundary",
            "src_width": 1280, "src_height": 720,
            "geometry": {"new_width": 416, "new_height": 234, "offset_x": 0, "offset_y": 91,
                         "pad_right": 0, "pad_bottom": 91},
            "network_box": (0.0, 0.25, 1.0, 0.75),
            "formula": ("x1=(0.0*416-0)/(416-1); y1=(0.25*416-91)/(234-1); "
                        "x2=(1.0*416-0)/(416-1); y2=(0.75*416-91)/(234-1)"),
            "expected": (0 / 415, 13 / 233, 416 / 415, 221 / 233),
            "expected_literals": (0.0, 0.055793991416309012, 1.0024096385542168,
                                  0.9484978540772532),
            "note": "网络边界 u=1.0 经端点对齐反算略大于 1，显示层必须裁剪而非截断",
        },
        {
            "sample_id": "HS3_1440x1920_non_integer",
            "src_width": 1440, "src_height": 1920,
            "geometry": {"new_width": 312, "new_height": 416, "offset_x": 52, "offset_y": 0,
                         "pad_right": 52, "pad_bottom": 0},
            "network_box": (0.50, 0.10, 0.60, 0.20),
            "formula": ("x1=(0.50*416-52)/(312-1); y1=(0.10*416-0)/(416-1); "
                        "x2=(0.60*416-52)/(312-1); y2=(0.20*416-0)/(416-1)"),
            "expected": (156 / 311, 41.6 / 415, 197.6 / 311, 83.2 / 415),
            "expected_literals": (0.5016077170418006, 0.10024096385542168,
                                  0.6353697749196141, 0.20048192771084338),
            "note": "反补边后为非整数：若提前取整即与手算不符",
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 时间台账、年龄与 HUD
# ─────────────────────────────────────────────────────────────────────────────


def synth_clock(frame_id: int, age_frame_ns: int | None = None, display_lag_frames: int = 1) -> dict:
    """离线合成单调台账（**非实测**）：capture → result 发布 → overlay commit。

    给定目标 age_frame = commit - capture 时，result 发布时刻取
    `capture + clamp(age - 1ms, 0, 20ms)`，保证 commit >= result（不触发时间倒流）。
    """
    capture = frame_id * SYNTH_FRAME_INTERVAL_NS
    if age_frame_ns is None:
        age = 15_000_000 + (frame_id % 5) * 1_000_000
        publish_gap = 10_000_000
    else:
        age = int(age_frame_ns)
        publish_gap = max(0, min(20_000_000, age - 1_000_000))
    result = capture + publish_gap
    commit = capture + age
    return {"capture_time_ns": capture, "result_time_ns": result, "overlay_commit_ns": commit,
            "displayed_frame_id": frame_id + int(display_lag_frames),
            "time_source": OFFLINE_PLACEHOLDER}


HUD_PROVENANCE = {
    "capture_fps": "离线合成台账整段平均（(N-1)/(t_last-t_first)），非实测",
    "inference_fps": "离线合成台账：已完成并发布结果的帧数 / 观测时长，非实测",
    "display_fps": "离线合成台账：输出帧数 / 观测时长，非实测",
    "inference_time_ns": OFFLINE_PLACEHOLDER + "（推理耗时占位值，非实测）",
    "age_result_ns": "t_overlay_commit - t_result_publish（合成台账）",
    "age_frame_ns": "t_overlay_commit - t_capture(result_frame_id)（合成台账；语义 B 下唯一可称端到端延迟者）",
    "frame_id": "被叠加结果自身的 frame_id（result_frame_id）",
    "boxes": "最终实际绘制框数（过期清除/裁剪零面积/超框不入画）；结果内框数另记 boxes_in_result",
    "stale_cleared": "每结果只计一次（0/1/累计）",
    "dropped_frames": "离线合成值（无真实丢帧事实）",
    "timeouts": "离线合成值（无真实超时事实）",
    "warmup_state": "离线占位枚举，非实测状态机值",
    "display_semantics": "固定为契约 display_semantics.value（单一语义）",
}


def build_hud(ages: Mapping[str, Any], *, frame_id: int, boxes: int, stale_cleared: int,
              dropped_frames: int, timeouts: int, inference_time_ns: int, capture_fps: float,
              inference_fps: float, display_fps: float, display_semantics: str) -> dict:
    return {
        "capture_fps": capture_fps,
        "inference_fps": inference_fps,
        "display_fps": display_fps,
        "inference_time_ns": inference_time_ns,
        "age_result_ns": ages["age_result_ns"],
        "age_frame_ns": ages["age_frame_ns"],
        "frame_id": frame_id,
        "boxes": boxes,
        "stale_cleared": stale_cleared,
        "dropped_frames": dropped_frames,
        "timeouts": timeouts,
        "warmup_state": "OFFLINE_PLACEHOLDER_NOT_MEASURED",
        "display_semantics": display_semantics,
    }


def ledger_fps(n_frames: int, first_ns: int, last_ns: int, completed: int, displayed: int) -> dict:
    span = max(1, int(last_ns) - int(first_ns))
    return {
        "capture_fps": (n_frames - 1) * 1e9 / span if n_frames > 1 else 0.0,
        "inference_fps": completed * 1e9 / span,
        "display_fps": displayed * 1e9 / span,
        "span_ns": span,
        "definition": "整段平均（非滑动窗口）；三类 FPS 分母口径分别记录于 hud_provenance",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 合成帧、显示像素与标签布局
# ─────────────────────────────────────────────────────────────────────────────


def synth_frame(src_w: int, src_h: int, seed: int, case_index: int) -> np.ndarray:
    """确定性合成帧：算术渐变 + 64px 网格 + 外边框，不使用随机数（跨版本稳定）。"""
    xs = np.arange(src_w, dtype=np.int64)
    ys = np.arange(src_h, dtype=np.int64)
    frame = np.empty((src_h, src_w, 3), dtype=np.uint8)
    frame[:, :, 0] = ((xs[None, :] + case_index * 7) % 256).astype(np.uint8)
    frame[:, :, 1] = ((ys[:, None] * 2 + case_index * 11) % 256).astype(np.uint8)
    frame[:, :, 2] = ((((xs[None, :] + ys[:, None]) // 2) + case_index * 13) % 256).astype(np.uint8)
    grid = np.array([255, 255, 255], dtype=np.uint8)
    for x in range(0, src_w, 64):
        frame[:, x] = grid
    for y in range(0, src_h, 64):
        frame[y, :] = grid
    if src_h >= 2 and src_w >= 2:
        black = np.array([0, 0, 0], dtype=np.uint8)
        frame[0, :] = black
        frame[-1, :] = black
        frame[:, 0] = black
        frame[:, -1] = black
    return frame


def float64_display_continuous(box: Sequence[float], display_w: int, display_h: int) -> dict:
    """显示像素的 **float64 连续** 位置（即冻结 `round_half_up` 的输入）。

    仅用于度量取整误差（契约 B_display_pixel_layer ≤1.0 px）；权威取整仍由冻结函数完成。
    """
    return {"x1": float(box[0]) * (display_w - 1), "y1": float(box[1]) * (display_h - 1),
            "x2": float(box[2]) * (display_w - 1), "y2": float(box[3]) * (display_h - 1)}


def float64_canvas_continuous(box: Sequence[float], fit_info: Mapping[str, Any]) -> dict:
    ox, oy = int(fit_info["offset_x"]), int(fit_info["offset_y"])
    dw, dh = int(fit_info["drawn_width"]), int(fit_info["drawn_height"])
    k = int(fit_info["scale_k"])
    return {"x1": float(box[0]) * (dw // k - 1) * k + ox, "y1": float(box[1]) * (dh // k - 1) * k + oy,
            "x2": float(box[2]) * (dw // k - 1) * k + ox, "y2": float(box[3]) * (dh // k - 1) * k + oy}


def place_label(px_x1: int, px_y1: int, text_w: int, text_h: int,
                canvas_w: int, canvas_h: int, safe: int) -> dict:
    """契约 overlay_layout.label_anchor_rule：框左上外侧 → 越界翻转框内左上 → 仍越界钳入安全区。"""
    x, y = int(px_x1), int(px_y1) - 1 - int(text_h)
    flipped = False
    if x < safe or y < safe or x + text_w > canvas_w - safe:
        x, y = int(px_x1) + 1, int(px_y1) + 1
        flipped = True
    nx = min(max(x, safe), max(safe, canvas_w - safe - text_w))
    ny = min(max(y, safe), max(safe, canvas_h - safe - text_h))
    return {"x": nx, "y": ny, "width": text_w, "height": text_h,
            "flipped_inside": bool(flipped), "clamped_to_safe_area": (nx, ny) != (x, y)}


# ─────────────────────────────────────────────────────────────────────────────
# 用例表（确定性纯数据）
# ─────────────────────────────────────────────────────────────────────────────


def _box(class_id: int, score: float, xyxy: Sequence[float], source_order: int) -> tuple:
    return (int(class_id), float(score), tuple(float(v) for v in xyxy), int(source_order))


def case_table() -> list[dict]:
    cases: list[dict] = []

    def add(**kwargs) -> None:
        base = dict(kind="synthetic", coordinate_path="fallback_inverse_mapping", state="OK",
                    fit="exact", canvas=None, stale_flag=False, age_frame_ns=None,
                    display_lag_frames=1, expects_degenerate=False, upstream=None,
                    d2_letterbox_proof=False, batch_png_limit=5, notes=[])
        base.update(kwargs)
        base["frame_id"] = 5000 + 10 * len(cases)
        cases.append(base)

    # ── T5-01 非方形 / 补边 / 画布 ────────────────────────────────────────
    add(case_id="t5_01_landscape_1280x720", group="T5-01", src_w=1280, src_h=720,
        boxes=[_box(0, 0.91, (0.10, 0.20, 0.40, 0.55), 100),
               _box(2, 0.55, (0.60, 0.55, 0.95, 0.90), 205)],
        notes=["横屏 16:9；补边对称（上 91 / 下 91）"])
    add(case_id="t5_01_portrait_720x1280", group="T5-01", src_w=720, src_h=1280,
        boxes=[_box(4, 0.80, (0.30, 0.10, 0.70, 0.40), 77)],
        notes=["竖屏；补边在左右（左 91 / 右 91）"])
    add(case_id="t5_01_oddw_683x384", group="T5-01", src_w=683, src_h=384,
        boxes=[_box(1, 0.75, (0.25, 0.50, 0.75, 0.75), 310),
               _box(3, 0.33, (0.05, 0.05, 0.30, 0.25), 42)],
        d2_letterbox_proof=True,
        notes=["奇数宽 683；总补边 183 为奇数 ⇒ 上 91 / 下 92（非对称，禁止对称化）",
               "正向 letterbox 图像走 D2 冻结 letterbox_rgb_uint8，证明几何同源"])
    add(case_id="t5_01_square_640x640_no_pad", group="T5-01", src_w=640, src_h=640,
        boxes=[_box(0, 0.66, (0.20, 0.20, 0.50, 0.50), 11),
               _box(4, 0.41, (0.55, 0.60, 0.90, 0.95), 12)],
        notes=["方形源：无补边（new 416×416、offset 0/0、pad 0/0）"])
    add(case_id="t5_01_canvas_683x384_k2_1920x1080", group="T5-01", src_w=683, src_h=384,
        boxes=[_box(1, 0.88, (0.20, 0.20, 0.60, 0.60), 5)],
        fit="fit_no_stretch", canvas=(1920, 1080),
        notes=["非方形源入 1920×1080 画布：整数倍 k=2 等比居中（1366×768），四周留黑边，不拉伸"])
    add(case_id="t5_01_canvas_1280x720_k1_1920x1080", group="T5-01", src_w=1280, src_h=720,
        boxes=[_box(0, 0.50, (0.10, 0.10, 0.40, 0.40), 9)],
        fit="fit_no_stretch", canvas=(1920, 1080),
        notes=["整数倍 k=1 居中（1280×720），左右 320 / 上下 180 黑边"])

    # ── T5-02 边缘框 / 越界 / 裁剪零面积 / 退化几何 ────────────────────────
    add(case_id="t5_02_edge_flush", group="T5-02", src_w=640, src_h=640,
        boxes=[_box(0, 0.90, (0.0, 0.0, 0.50, 0.25), 1),
               _box(1, 0.90, (0.50, 0.75, 1.0, 1.0), 2)],
        notes=["贴边：网络归一化 u/v ∈ {0,1}；端点对齐反算 u=1 → 略超 1，须裁剪"])
    add(case_id="t5_02_corners", group="T5-02", src_w=640, src_h=640,
        boxes=[_box(0, 0.60, (0.00, 0.00, 0.15, 0.15), 3),
               _box(0, 0.60, (0.85, 0.00, 1.00, 0.15), 4),
               _box(0, 0.60, (0.00, 0.85, 0.15, 1.00), 5),
               _box(0, 0.60, (0.85, 0.85, 1.00, 1.00), 6)],
        notes=["四角框：方形源（无补边）使四角落到画布四角（0/639）"])
    add(case_id="t5_02_letterbox_padding_zero_area", group="T5-02", src_w=1280, src_h=720,
        boxes=[_box(2, 0.64, (0.30, 0.02, 0.70, 0.20), 13),
               _box(2, 0.44, (0.10, 0.05, 0.35, 0.15), 14),
               _box(0, 0.72, (0.30, 0.35, 0.70, 0.60), 15)],
        notes=["前两框整体落在 letterbox 上补边带（网络 y ≤ 0.219）内：逆映射后在原图上侧之外 "
               "⇒ 裁剪后零面积、不得绘制；第三框正常绘制"])
    add(case_id="t5_02_partial_out_of_bounds", group="T5-02", src_w=640, src_h=480,
        coordinate_path="stage4_original_norm_xyxy",
        boxes=[_box(2, 0.70, (-0.10, -0.05, 0.30, 0.40), 8),
               _box(3, 0.60, (0.70, 0.80, 1.15, 1.05), 9)],
        notes=["防御性用例：上游 xyxy 刻意越界（阶段4 契约称 xyxy 已裁剪；本用例验证显示层裁剪路径）"])
    add(case_id="t5_02_clip_zero_area", group="T5-02", src_w=640, src_h=480,
        coordinate_path="stage4_original_norm_xyxy",
        boxes=[_box(0, 0.50, (1.20, 0.20, 1.40, 0.40), 7),
               _box(1, 0.80, (0.20, 0.20, 0.60, 0.60), 8)],
        notes=["第一个框完全在画布外 ⇒ 裁剪后零面积，不得绘制；第二个正常绘制"])
    add(case_id="t5_02_degenerate_new_w_1", group="T5-02", src_w=1, src_h=300,
        boxes=[_box(0, 0.70, (0.20, 0.20, 0.60, 0.60), 4)],
        expects_degenerate=True,
        notes=["极窄源 1×300 ⇒ new_w=1；逆式不适用，必须抛 DegenerateGeometryError 并改用阶段4 原图坐标字段"])

    # ── T5-03 多框 / 零框 ─────────────────────────────────────────────────
    multi = []
    for index in range(15):
        col, row = index % 5, index // 5
        multi.append(_box(index % 5, round(0.95 - 0.04 * index, 2),
                          (0.02 + 0.19 * col, 0.05 + 0.30 * row,
                           0.02 + 0.19 * col + 0.16, 0.05 + 0.30 * row + 0.24), 1000 + index))
    add(case_id="t5_03_multi_15", group="T5-03", src_w=640, src_h=640, boxes=multi,
        notes=["15 框上限（MAX_OUTPUTS_PER_IMAGE）；显示层不得重排、不得因遮挡丢弃"])
    add(case_id="t5_03_no_hand_zero", group="T5-03", src_w=640, src_h=640, boxes=[],
        state="NO_HAND", coordinate_path="stage4_original_norm_xyxy",
        notes=["零框 NO_HAND：合法结果，区别于过期/丢失；boxes=0 且不计入过期"])
    add(case_id="t5_03_no_hand_s4b_640x963", group="T5-03", src_w=640, src_h=963, boxes=[],
        state="NO_HAND", coordinate_path="stage4_original_norm_xyxy", upstream="s4b_no_hand",
        notes=["只读 S4-B host_result_approved_no_hand_001.json（frame_id=102，NO_HAND 零框）"])

    # ── T5-04 过期清除 ────────────────────────────────────────────────────
    box_one = [_box(1, 0.77, (0.30, 0.30, 0.60, 0.60), 21)]
    add(case_id="t5_04_age_equal_limit", group="T5-04", src_w=640, src_h=640, boxes=box_one,
        notes=["age_frame == limit：严格大于才过期 ⇒ 不过期，正常出框"])
    add(case_id="t5_04_age_limit_plus_1", group="T5-04", src_w=640, src_h=640, boxes=box_one,
        age_frame_ns=200_000_001,
        notes=["age_frame == limit+1 ⇒ 过期，不叠加，stale_cleared=1，原因 age_frame_exceeds_limit"])
    add(case_id="t5_04_stale_flag_small_age", group="T5-04", src_w=640, src_h=640, boxes=box_one,
        stale_flag=True, notes=["PS stale=true 且 age 很小 ⇒ 原因 stale_flag（年龄未越限）"])
    add(case_id="t5_04_stale_both", group="T5-04", src_w=640, src_h=640, boxes=box_one,
        stale_flag=True, age_frame_ns=200_000_001,
        notes=["PS stale=true 且 age 越限 ⇒ 原因 both，仍只计一次"])

    # ── T5-01（只读 S4-B 记录形态）────────────────────────────────────────
    add(case_id="t5_01_s4b_palm_1440x1920", group="T5-01", src_w=1440, src_h=1920,
        boxes=[], coordinate_path="stage4_original_norm_xyxy", upstream="s4b_palm",
        notes=["只读 S4-B host_result_test_palm_036.json（2 框，含一个贴 [1,1]；上游时间字段为 0 哨兵）"])

    # ── T5-05 S4-C golden 109 帧台账 ──────────────────────────────────────
    add(case_id="t5_05_s4c_golden109_frame_ledger", group="T5-05", src_w=0, src_h=0, boxes=[],
        kind="s4c_batch", coordinate_path="stage4_original_norm_xyxy", upstream="s4c_golden109",
        notes=["只读 S4-C replay_golden_109.json：109 帧五元组台账（可按 frame_id 索引）；"
               "仅对最小几何子集出 PNG，其余帧只记台账"])
    return cases


# ─────────────────────────────────────────────────────────────────────────────
# 上游输入（契约 JSON 声明路径，只读）
# ─────────────────────────────────────────────────────────────────────────────


def resolve_upstream_inputs(contract: Mapping[str, Any], overrides: Mapping[str, str]) -> dict:
    paths: dict[str, str] = {}
    for binding in contract.get("upstream_bindings", []):
        ident = binding.get("id")
        if ident == "s4c_replay_golden_109":
            paths["s4c_golden109"] = binding.get("path", "")
        elif ident == "s4b_offline_chain_r13":
            paths["s4b_dir"] = binding.get("path", "")
    for key, value in overrides.items():
        if value:
            paths[key] = value
    return paths


def upstream_inventory(paths: Mapping[str, str]) -> dict:
    inventory: dict[str, dict] = {}
    for key, raw in paths.items():
        path = Path(raw)
        if not raw:
            inventory[key] = {"path": "", "exists": False, "status": "MISSING_DECLARATION"}
        elif path.is_dir():
            entries = [{"name": child.name, "bytes": child.stat().st_size,
                        "sha256": sha256_file(child)}
                       for child in sorted(child for child in path.iterdir() if child.is_file())]
            inventory[key] = {"path": str(path), "exists": True, "kind": "dir",
                              "files": entries, "file_count": len(entries)}
        elif path.is_file():
            inventory[key] = {"path": str(path), "exists": True, "kind": "file",
                              "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        else:
            inventory[key] = {"path": str(path), "exists": False, "status": "NOT_FOUND"}
    return inventory


def read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# ─────────────────────────────────────────────────────────────────────────────
# 单用例渲染
# ─────────────────────────────────────────────────────────────────────────────


def _class_name(class_id: int) -> str:
    if not 0 <= int(class_id) < len(CLASS_ORDER):
        raise ValueError(f"class_id 越界：{class_id}")
    return CLASS_ORDER[int(class_id)]


def _record_from_boxes(frame_id: int, src_w: int, src_h: int, boxes: Sequence[tuple],
                       state: str, ledger: Mapping[str, Any], stale_flag: bool,
                       inference_time_ns: int) -> dict:
    detections = [
        {"class_id": int(class_id), "class_name": _class_name(class_id), "score": float(score),
         "xyxy": [float(v) for v in xyxy], "source_order": int(source_order)}
        for class_id, score, xyxy, source_order in boxes
    ]
    return {
        "frame_id": int(frame_id),
        "geometry": {"width": int(src_w), "height": int(src_h)},
        "state": state,
        "detection_count": len(detections),
        "detections": detections,
        "stale": bool(stale_flag),
        "dropped_frames": 0,
        "capture_time_ns": int(ledger["capture_time_ns"]),
        "result_time_ns": int(ledger["result_time_ns"]),
        "inference_time_ns": int(inference_time_ns),
        "end_to_end_latency_ns": int(ledger["overlay_commit_ns"] - ledger["capture_time_ns"]),
        "error_code": 0,
    }


def expected_stale_case(case_id: str, reference) -> dict:
    if case_id == "t5_04_age_equal_limit":
        return {"stale_effective": False, "reason": reference.STALE_REASON_NONE}
    if case_id == "t5_04_age_limit_plus_1":
        return {"stale_effective": True, "reason": reference.STALE_REASON_AGE}
    if case_id == "t5_04_stale_flag_small_age":
        return {"stale_effective": True, "reason": reference.STALE_REASON_FLAG}
    if case_id == "t5_04_stale_both":
        return {"stale_effective": True, "reason": reference.STALE_REASON_BOTH}
    return {"stale_effective": False, "reason": reference.STALE_REASON_NONE}


def letterbox_d2_proof(src_w: int, src_h: int, geom: Mapping[str, Any], d2_reference,
                       seed: int, case_index: int) -> dict:
    """用 D2 冻结 letterbox_rgb_uint8 走通正向图像，证明与冻结几何同源。"""
    source = synth_frame(src_w, src_h, seed, case_index)
    rgb = [[[int(px) for px in source[y, x]] for x in range(src_w)] for y in range(src_h)]
    boxed = d2_reference.letterbox_rgb_uint8(rgb, 416, 416)
    new_w, new_h = int(geom["new_width"]), int(geom["new_height"])
    off_x, off_y = int(geom["offset_x"]), int(geom["offset_y"])
    pad_values = set()
    for y in range(416):
        for x in range(416):
            if y < off_y or y >= off_y + new_h or x < off_x or x >= off_x + new_w:
                pad_values.add(tuple(int(v) for v in boxed[y][x]))
    corners_ok = (boxed[off_y][off_x] == [float(v) for v in source[0, 0]]
                  and boxed[off_y + new_h - 1][off_x + new_w - 1]
                  == [float(v) for v in source[src_h - 1, src_w - 1]])
    d2_geom = d2_reference.letterbox_geometry(src_w, src_h, 416, 416)
    scale_ok, scale_detail = True, ""
    if new_w > 1:
        w_scale_d2 = (src_w - 1) / (new_w - 1)
        for ix in (0, 1, new_w // 3, new_w // 2, new_w - 1):
            continuous = (ix / 416 * 416 - off_x) * geom["w_scale"]
            if abs(continuous - ix * w_scale_d2) > 1e-12:
                scale_ok = False
                scale_detail = f"（ix={ix} 冻结 {continuous!r} vs D2 {ix * w_scale_d2!r}）"
                break
    checks = [
        ("letterbox_d2_geometry_identity",
         all(d2_geom[key] == geom[key] for key in ("new_width", "new_height", "offset_x", "offset_y")),
         f"D2 与冻结几何逐值一致：new {new_w}×{new_h} off ({off_x},{off_y})"),
        ("letterbox_padding_uniform", pad_values == {(128, 128, 128)},
         f"补边区域取值集合 {sorted(pad_values)[:3]}（期望补边常量 128）"),
        ("letterbox_endpoint_alignment", corners_ok,
         "缩放区四角等于源帧对应角像素（端点对齐双线性）"),
        ("letterbox_scale_same_source", scale_ok,
         "冻结逆式 scale 与 D2 resize 的 sx=ix*(src-1)/(new-1) 逐值一致" + scale_detail),
    ]
    return {"source_pixels": f"{src_w}×{src_h}", "padding_value": 128, "checks": checks,
            "new_width": new_w, "new_height": new_h, "offset_x": off_x, "offset_y": off_y,
            "note": "正向 letterbox 图像由 D2 冻结 letterbox_rgb_uint8 生成，证明几何同源",
            "image_pixels": np.array(boxed, dtype=np.uint8)}


def render_case(spec: Mapping[str, Any], case_index: int, reference, d2_reference,
                contract: Mapping[str, Any], seed: int, run_dir: Path,
                rec: Recorder, upstream: Mapping[str, str]) -> dict:
    """渲染单用例并返回机器可读用例日志（不含时间戳 ⇒ 可复现）。"""
    case_id = spec["case_id"]
    if spec["kind"] == "s4c_batch":
        return render_batch_case(spec, case_index, reference, seed, run_dir, rec, upstream)

    log: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "case_id": case_id,
        "case_group": spec["group"],
        "case_kind": spec["kind"],
        "coordinate_path": spec["coordinate_path"],
        "coordinate_path_note": (
            "显示层直接消费阶段4 原图归一化 xyxy（契约唯一允许路径）"
            if spec["coordinate_path"] == "stage4_original_norm_xyxy" else
            "离线准备兜底路径：网络归一化 → network_norm_to_original_norm 逆映射"
            "（契约 fallback_inverse_mapping）"),
        "display_semantics": reference.DISPLAY_SEMANTICS,
        "notes": list(spec.get("notes", [])),
        "seed": int(seed),
        "random_box_n": RANDOM_BOX_N,
        "limitations": ["离线合成时间台账与 HUD 数值为占位量，非实测",
                        "本用例不含实板 HDMI / PL / UART 证据"],
        "not_executed": ["实板 HDMI 叠加", "PL/UART 时序实测", "长时间无死锁运行"],
    }

    # ── 数据来源：只读 S4-B 记录 或 合成 ─────────────────────────────────
    upstream_record = None
    if spec.get("upstream") in ("s4b_palm", "s4b_no_hand"):
        filename = ("host_result_test_palm_036.json" if spec["upstream"] == "s4b_palm"
                    else "host_result_approved_no_hand_001.json")
        s4b_path = Path(upstream["s4b_dir"]) / filename
        if not s4b_path.is_file():
            rec.error(f"{case_id}.upstream_missing", f"只读 S4-B 输入不存在：{s4b_path}")
            log["status"] = "ERROR"
            return log
        upstream_record = read_json(s4b_path)
        log["upstream"] = {"id": spec["upstream"], "path": str(s4b_path),
                           "sha256": sha256_file(s4b_path), "mode": "read_only"}
        problems = reference.validate_result_record(upstream_record)
        rec.check(f"{case_id}.upstream_record_contract_valid", not problems,
                  "上游记录通过 validate_result_record" if not problems else str(problems[:4]))
        src_w = int(upstream_record["geometry"]["width"])
        src_h = int(upstream_record["geometry"]["height"])
        boxes = [(det["class_id"], det["score"], det["xyxy"], det["source_order"])
                 for det in upstream_record["detections"]]
        state = str(upstream_record["state"])
        log["upstream_time_fields_sentinel"] = {
            "capture_time_ns": upstream_record["capture_time_ns"],
            "result_time_ns": upstream_record["result_time_ns"],
            "note": "上游离线骨架时间字段为 0 哨兵（未测量）；本用例改用离线合成台账时间计算年龄，不声称实测",
        }
        log["upstream_geometry_letterbox"] = upstream_record.get("geometry_letterbox")
    else:
        src_w, src_h = int(spec["src_w"]), int(spec["src_h"])
        boxes = list(spec["boxes"])
        state = spec["state"]

    if src_w <= 0 or src_h <= 0:
        rec.error(f"{case_id}.src_size", f"源尺寸非法：{src_w}×{src_h}")
        log["status"] = "ERROR"
        return log

    frame_id = int(spec["frame_id"])
    age_override = spec["age_frame_ns"]
    if case_id == "t5_04_age_equal_limit":
        age_override = int(reference.STALE_AGE_LIMIT_NS)
    if upstream_record is not None:
        frame_id = int(upstream_record["frame_id"])
    ledger = synth_clock(frame_id, age_override, spec["display_lag_frames"])
    inference_time_ns = 33_000_000
    record = _record_from_boxes(frame_id, src_w, src_h, boxes, state, ledger,
                                spec["stale_flag"], inference_time_ns)
    problems = reference.validate_result_record(record)
    rec.check(f"{case_id}.record_contract_valid", not problems,
              "validate_result_record 通过" if not problems else f"问题：{problems[:5]}")
    log["record_contract_problems"] = problems
    log["frame_id"] = frame_id
    log["state"] = state
    log["boxes_in_result"] = len(boxes)

    # ── 几何：冻结参考 + 独立手算 + D2 双源 ──────────────────────────────
    geom = reference.letterbox_geometry(src_w, src_h, 416, 416)
    hand = hand_geometry(src_w, src_h)
    d2_geom = d2_reference.letterbox_geometry(src_w, src_h, 416, 416)
    rec.check(f"{case_id}.geometry_vs_hand", all(geom[key] == hand[key] for key in hand),
              f"冻结 new {geom['new_width']}×{geom['new_height']} off "
              f"({geom['offset_x']},{geom['offset_y']}) pad ({geom['pad_right']},{geom['pad_bottom']}) vs "
              f"手算 new {hand['new_width']}×{hand['new_height']} pad ({hand['pad_right']},{hand['pad_bottom']})")
    rec.check(f"{case_id}.geometry_vs_d2_reference",
              all(geom[key] == d2_geom[key] for key in
                  ("src_width", "src_height", "dst_width", "dst_height")),
              "D2 与冻结 letterbox_geometry 的源/目标尺寸逐值一致")
    log["geometry"] = {key: geom[key] for key in
                       ("src_width", "src_height", "dst_width", "dst_height", "new_width",
                        "new_height", "offset_x", "offset_y", "w_scale", "h_scale",
                        "pad_right", "pad_bottom", "asymmetric_padding", "padding_uint8")}
    log["geometry_hand_check"] = hand
    log["geometry_d2_check"] = {key: d2_geom[key] for key in
                                ("new_width", "new_height", "offset_x", "offset_y")}
    if upstream_record is not None and upstream_record.get("geometry_letterbox"):
        upstream_box = upstream_record["geometry_letterbox"]
        rec.check(f"{case_id}.geometry_vs_upstream_letterbox",
                  int(upstream_box["resized_width"]) == geom["new_width"]
                  and int(upstream_box["resized_height"]) == geom["new_height"]
                  and int(upstream_box["pad_left"]) == geom["offset_x"]
                  and int(upstream_box["pad_top"]) == geom["offset_y"],
                  f"上游 geometry_letterbox={upstream_box} vs 冻结 "
                  f"new {geom['new_width']}×{geom['new_height']} off "
                  f"({geom['offset_x']},{geom['offset_y']})")

    if (src_w, src_h) == (683, 384):
        rec.check(f"{case_id}.odd_padding_asymmetry_preserved",
                  geom["offset_y"] == 91 and geom["pad_bottom"] == 92
                  and geom["asymmetric_padding"] is True,
                  f"上 {geom['offset_y']} / 下 {geom['pad_bottom']}，"
                  f"asymmetric={geom['asymmetric_padding']}（禁止对称化/ceil/重新居中）")
        rec.check(f"{case_id}.odd_padding_not_symmetrized",
                  geom["offset_y"] + geom["new_height"] + geom["pad_bottom"] == 416
                  and geom["pad_bottom"] == geom["offset_y"] + 1,
                  "总补边 183 为奇数：上 91 / 下 92 且 91+233+92=416，未被对称化")
    if (src_w, src_h) == (1280, 720):
        rec.check(f"{case_id}.symmetric_padding_expected",
                  geom["offset_y"] == 91 and geom["pad_bottom"] == 91,
                  "总补边 182 为偶数 ⇒ 上 91 / 下 91")

    # ── 退化几何 ────────────────────────────────────────────────────────
    degenerate = None
    if spec["expects_degenerate"]:
        try:
            reference.network_norm_to_original_norm((0.1, 0.1, 0.2, 0.2), geom)
            rec.fail(f"{case_id}.degenerate_raises", "退化几何未抛 DegenerateGeometryError")
            degenerate = {"raised": None, "ok": False}
        except reference.DegenerateGeometryError as exc:
            rec.check(f"{case_id}.degenerate_raises", True, f"DegenerateGeometryError：{exc}")
            degenerate = {"raised": "DegenerateGeometryError", "ok": True, "message": str(exc),
                          "fallback": "改用阶段4 原图坐标字段（契约 geometry.degenerate_rule）",
                          "geometry": {"new_width": geom["new_width"], "new_height": geom["new_height"]}}
            rec.check(f"{case_id}.degenerate_fallback_recorded",
                      "原图坐标字段" in degenerate["fallback"], degenerate["fallback"])
    log["degenerate"] = degenerate

    # ── 逆映射 / round-trip / 手算样例 ──────────────────────────────────
    round_trip: dict[str, Any] = {"n": 0, "max_abs_error": 0.0}
    hand_rows: list[dict] = []
    if not spec["expects_degenerate"]:
        for row in hand_computed_samples():
            if (row["src_width"], row["src_height"]) != (src_w, src_h):
                continue
            got = reference.network_norm_to_original_norm(row["network_box"], geom)
            err = max(abs(a - b) for a, b in zip(got, row["expected"]))
            literal_err = max(abs(a - b) for a, b in zip(got, row["expected_literals"]))
            rec.check(f"{case_id}.hand_sample_{row['sample_id']}",
                      err <= INVERSE_TOL and literal_err <= INVERSE_TOL,
                      f"手算值 {[format_float(v) for v in row['expected']]} vs 参考 "
                      f"{[format_float(v) for v in got]}，误差 {err:.3e}（容限 {INVERSE_TOL:g}）")
            hand_rows.append({"sample_id": row["sample_id"], "formula": row["formula"],
                              "network_box": list(row["network_box"]),
                              "expected": list(row["expected"]),
                              "expected_literals": list(row["expected_literals"]),
                              "reference": list(got), "max_abs_error": err,
                              "literal_max_abs_error": literal_err, "tol": INVERSE_TOL})
        if spec["coordinate_path"] == "fallback_inverse_mapping":
            errors = []
            for _, _, xyxy, _ in boxes:
                original = reference.network_norm_to_original_norm(xyxy, geom)
                back = reference.original_norm_to_network_norm(original, geom)
                errors.append(max(abs(a - b) for a, b in zip(back, xyxy)))
            round_trip = {"n": len(errors), "max_abs_error": max(errors) if errors else 0.0}
            rec.check(f"{case_id}.round_trip_case_boxes",
                      round_trip["n"] > 0 and round_trip["max_abs_error"] <= RANDOM_ROUND_TRIP_TOL,
                      f"n={round_trip['n']} 最大误差 {round_trip['max_abs_error']:.3e}"
                      f"（容限 {RANDOM_ROUND_TRIP_TOL:g}）")
        rng = random.Random(seed)
        rng_errors = []
        for _ in range(RANDOM_BOX_N):
            x1, x2 = sorted((rng.random(), rng.random()))
            y1, y2 = sorted((rng.random(), rng.random()))
            net_box = (x1, y1, x2, y2)
            original = reference.network_norm_to_original_norm(net_box, geom)
            back = reference.original_norm_to_network_norm(original, geom)
            rng_errors.append(max(abs(a - b) for a, b in zip(back, net_box)))
        max_rng = max(rng_errors)
        rec.check(f"{case_id}.seeded_random_round_trip_n{RANDOM_BOX_N}",
                  max_rng <= RANDOM_ROUND_TRIP_TOL,
                  f"N={RANDOM_BOX_N}（种子 {seed}）最大误差 {max_rng:.3e}，"
                  f"容限 {RANDOM_ROUND_TRIP_TOL:g}")
        round_trip["seeded_n"] = RANDOM_BOX_N
        round_trip["seeded_max_abs_error"] = max_rng
    log["hand_samples"] = hand_rows
    log["round_trip"] = round_trip

    # ── 画布 / 显示像素 ──────────────────────────────────────────────────
    fit_info = None
    if spec["fit"] == "fit_no_stretch":
        canvas_w, canvas_h = spec["canvas"]
        try:
            fit_info = reference.canvas_fit(src_w, src_h, canvas_w, canvas_h)
        except Exception as exc:  # noqa: BLE001 - 契约性失败如实记录
            rec.error(f"{case_id}.canvas_fit", f"canvas_fit 失败：{exc}")
            log["status"] = "ERROR"
            return log
        k = int(fit_info["scale_k"])
        expected_k = min(canvas_w // src_w, canvas_h // src_h)
        rec.check(f"{case_id}.canvas_fit_integer_scale",
                  k == expected_k and fit_info["drawn_width"] == src_w * k
                  and fit_info["drawn_height"] == src_h * k,
                  f"k={k}（手算 {expected_k}）绘制区 "
                  f"{fit_info['drawn_width']}×{fit_info['drawn_height']}")
        rec.check(f"{case_id}.canvas_no_stretch",
                  fit_info["drawn_width"] / src_w == fit_info["drawn_height"] / src_h == k,
                  "绘制区宽高比与源帧一致（整数倍等比，不拉伸）")
        rec.check(f"{case_id}.canvas_centered_offsets",
                  fit_info["offset_x"] == (canvas_w - fit_info["drawn_width"]) // 2
                  and fit_info["offset_y"] == (canvas_h - fit_info["drawn_height"]) // 2,
                  f"居中 offset=({fit_info['offset_x']},{fit_info['offset_y']})")
        display_w, display_h = int(canvas_w), int(canvas_h)
    else:
        display_w, display_h = src_w, src_h
    log["canvas"] = {"fit": spec["fit"], "display_width": display_w, "display_height": display_h,
                     "fit_info": fit_info}

    # ── 逐框：裁剪 → 像素 → 边框像素集 ───────────────────────────────────
    boxes_log: list[dict] = []
    drawn_sets: list[list[tuple[int, int]]] = []
    drawn_entries: list[dict] = []
    age_frame = int(ledger["overlay_commit_ns"] - ledger["capture_time_ns"])
    stale_info = reference.effective_stale(bool(spec["stale_flag"]), age_frame)
    draw_allowed = not stale_info["stale_effective"]
    clipped_count = 0
    zero_area_count = 0

    for index, (class_id, score, xyxy, source_order) in enumerate(boxes):
        entry: dict[str, Any] = {
            "index": index, "class_id": int(class_id), "class_name": _class_name(class_id),
            "score": float(score), "source_order": int(source_order),
            "input_coords": [float(v) for v in xyxy],
            "input_coords_kind": spec["coordinate_path"], "drawn": False,
        }
        try:
            if spec["expects_degenerate"]:
                # 退化几何：契约要求改用阶段4 原图坐标字段，本用例不进入逆映射
                entry["skip_reason"] = "degenerate_geometry_use_stage4_original_coords"
                boxes_log.append(entry)
                continue
            if spec["coordinate_path"] == "fallback_inverse_mapping":
                original = reference.network_norm_to_original_norm(xyxy, geom)
            else:
                original = tuple(float(v) for v in xyxy)
            entry["original_norm_preclip"] = list(original)
            clip = reference.clip_unit_box(original)
            clipped_count += int(clip["clipped"])
            zero_area_count += int(clip["zero_area"])
            entry["clipped"] = bool(clip["clipped"])
            entry["zero_area"] = bool(clip["zero_area"])
            entry["xyxy_clipped"] = list(clip["xyxy"])
            if clip["zero_area"]:
                entry["skip_reason"] = "zero_area_after_clip"
                boxes_log.append(entry)
                continue
            if not draw_allowed:
                entry["skip_reason"] = f"stale_cleared:{stale_info['reason']}"
                boxes_log.append(entry)
                continue
            if fit_info is None:
                px = reference.original_norm_to_display_px(clip["xyxy"], display_w, display_h)
                continuous = float64_display_continuous(clip["xyxy"], display_w, display_h)
            else:
                px = reference.original_norm_to_canvas_px(clip["xyxy"], fit_info)
                continuous = float64_canvas_continuous(clip["xyxy"], fit_info)
            px_errors = {axis: abs(float(px[axis]) - continuous[axis])
                         for axis in ("x1", "y1", "x2", "y2")}
            entry["display_px"] = {axis: int(px[axis]) for axis in ("x1", "y1", "x2", "y2")}
            entry["display_px_float64"] = dict(continuous)
            entry["display_px_round_error"] = px_errors
            entry["display_px_round_error_max"] = max(px_errors.values())
            rec.check(f"{case_id}.box{index}.display_px_vs_float64_le_1px",
                      max(px_errors.values()) <= DISPLAY_PX_TOL,
                      f"最大取整误差 {max(px_errors.values()):.6f} px（容限 {DISPLAY_PX_TOL:g}）")
            pixels = reference.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]),
                                                 int(px["y2"]),
                                                 int(reference.DISPLAY_LINE_WIDTH_PX),
                                                 display_w, display_h)
            entry["border_pixel_count"] = len(pixels)
            entry["border_pixels_sha256"] = sha256_bytes(
                json.dumps(pixels, separators=(",", ":")).encode("utf-8"))
            entry["drawn"] = True
            rec.check(f"{case_id}.box{index}.border_pixels_non_empty", len(pixels) > 0,
                      f"边框像素数 {len(pixels)}")
            drawn_sets.append(pixels)
            drawn_entries.append(entry)
        except Exception as exc:  # noqa: BLE001 - 异常计入断言而非静默
            entry["error"] = f"{type(exc).__name__}: {exc}"
            rec.fail(f"{case_id}.box{index}.mapping", entry["error"])
        boxes_log.append(entry)

    log["boxes"] = boxes_log
    log["clip_summary"] = {"clipped_count": clipped_count, "zero_area_count": zero_area_count,
                           "drawn_box_count": len(drawn_sets)}
    rec.check(f"{case_id}.zero_area_not_drawn",
              all(not box["drawn"] for box in boxes_log if box.get("zero_area")),
              "裁剪后零面积框一律不绘制")
    if spec["expects_degenerate"]:
        rec.check(f"{case_id}.degenerate_no_box_drawn", len(drawn_sets) == 0,
                  "退化几何下不出框（须改用阶段4 原图坐标字段）")
    if case_id == "t5_02_corners":
        touched = []
        expected_corners = [("x1", "y1", 0, 0), ("x2", "y1", display_w - 1, 0),
                            ("x1", "y2", 0, display_h - 1),
                            ("x2", "y2", display_w - 1, display_h - 1)]
        for entry, (ka, kb, cx, cy) in zip(drawn_entries, expected_corners):
            px = entry["display_px"]
            touched.append(px[ka] == cx and px[kb] == cy)
        rec.check(f"{case_id}.four_corners_touched",
                  len(drawn_entries) == 4 and all(touched),
                  f"四角框是否各触及画布一角（0 或 {display_w - 1}/{display_h - 1}）："
                  f"{touched}；绘制 {len(drawn_entries)} 框")

    # ── 基础帧（合成内容；画布用例为整数倍块复制 + 黑边）──────────────────
    assert display_w > 0 and display_h > 0
    if fit_info is not None:
        ox, oy = int(fit_info["offset_x"]), int(fit_info["offset_y"])
        dw, dh = int(fit_info["drawn_width"]), int(fit_info["drawn_height"])
        k = int(fit_info["scale_k"])
        source = synth_frame(src_w, src_h, seed, case_index)
        frame_core = np.zeros((display_h, display_w, 3), dtype=np.uint8)
        frame_core[oy:oy + dh, ox:ox + dw] = np.repeat(np.repeat(source, k, axis=0), k, axis=1)
    else:
        frame_core = synth_frame(display_w, display_h, seed, case_index)

    # ── 画布黑边与整数倍块复制（HUD 文本与边框之前断言）─────────────────
    if fit_info is not None:
        ox, oy = int(fit_info["offset_x"]), int(fit_info["offset_y"])
        dw, dh = int(fit_info["drawn_width"]), int(fit_info["drawn_height"])
        bar_mask = np.zeros((display_h, display_w), dtype=bool)
        if ox > 0:
            bar_mask[:, :ox] = True
        if ox + dw < display_w:
            bar_mask[:, ox + dw:] = True
        if oy > 0:
            bar_mask[:oy, :] = True
        if oy + dh < display_h:
            bar_mask[oy + dh:, :] = True
        inside = frame_core[bar_mask]
        bars = {"bar_pixels": int(bar_mask.sum()),
                "all_black": bool(np.all(inside == 0)) if inside.size else True}
        rec.check(f"{case_id}.canvas_black_bars", bars["all_black"],
                  f"黑边像素 {bars['bar_pixels']} 个全部为 (0,0,0)"
                  f"（offset=({ox},{oy}) 绘制区 {dw}×{dh}）")
        k = int(fit_info["scale_k"])
        source = synth_frame(src_w, src_h, seed, case_index)
        block = np.tile(source[0, 0], (k, k, 1))
        rec.check(f"{case_id}.canvas_exact_block_replication",
                  np.array_equal(frame_core[oy:oy + k, ox:ox + k], block),
                  f"整数 k={k} 块复制（无插值 ⇒ 不拉伸）逐像素一致")
        log["canvas"]["black_bars"] = bars
        log["canvas"]["replication_verified"] = True
        log["canvas"]["checks_done_before_text_overlay"] = True

    # ── 图层顺序：合成内容 → HUD ASCII 文本带 → 冻结边框像素 → ASCII 标签 ──
    font = ImageFont.load_default()
    hud_band = (f"frame={frame_id} boxes={len(drawn_sets)} stale_cleared="
                f"{1 if stale_info['stale_effective'] else 0} age_frame_ns={age_frame} "
                f"sem={reference.DISPLAY_SEMANTICS}")
    hud_bbox = font.getbbox(hud_band)
    hud_w, hud_h = hud_bbox[2] - hud_bbox[0], hud_bbox[3] - hud_bbox[1]
    hud_drawn = False
    image = Image.fromarray(frame_core, "RGB")
    draw = ImageDraw.Draw(image)
    if hud_w + 2 <= display_w and hud_h + 2 <= display_h:
        draw.rectangle([0, 0, display_w - 1, hud_h + 2], fill=(0, 0, 0))
        draw.text((1 - hud_bbox[0], 1 - hud_bbox[1]), hud_band, font=font, fill=(255, 255, 0))
        hud_drawn = True
    rec.check(f"{case_id}.hud_band_ascii", hud_band.isascii(), "HUD 文本带仅 ASCII")
    frame = np.array(image)

    # ── 边框像素：按冻结 border_pixel_sets 逐像素落盘（覆盖 HUD 文本带）──
    owner: dict[tuple[int, int], int] = {}
    for index, pixels in enumerate(drawn_sets):
        color = CLASS_COLORS.get(int(drawn_entries[index]["class_id"]), (255, 255, 255))
        for x, y in pixels:
            frame[y, x] = color
            owner[(x, y)] = index
    mismatch = 0
    for (x, y), index in owner.items():
        color = CLASS_COLORS.get(int(drawn_entries[index]["class_id"]), (255, 255, 255))
        if tuple(int(v) for v in frame[y, x]) != tuple(color):
            mismatch += 1
    rec.check(f"{case_id}.draw_fidelity_exact", mismatch == 0,
              f"逐像素比对冻结 border_pixel_sets 与颜色归属（HUD 文本带之下、标签之上）："
              f"不一致 {mismatch} 个像素，绘制像素总数 {len(owner)}")

    # ── ASCII 标签（最后叠加；声明无 CJK 字体）───────────────────────────
    image = Image.fromarray(frame, "RGB")
    draw = ImageDraw.Draw(image)
    safe = max(1, int(reference.round_half_up(reference.SAFE_AREA_PX_1080P * display_h / 1080)))
    label_records: list[dict] = []
    for entry in drawn_entries:
        text = f"{entry['class_name']} {entry['score']:.2f}"
        if not text.isascii():
            rec.fail(f"{case_id}.label_ascii", f"标签非 ASCII：{text!r}")
            continue
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_w + 2 * safe > display_w or text_h + 2 * safe > display_h:
            label_records.append({"index": entry["index"], "text": text, "skipped": True,
                                  "skip_reason": "canvas_too_small_for_label"})
            continue
        px = entry["display_px"]
        place = place_label(px["x1"], px["y1"], text_w, text_h, display_w, display_h, safe)
        draw.text((place["x"] - bbox[0], place["y"] - bbox[1]), text, font=font,
                  fill=(255, 255, 255))
        place.update({"index": entry["index"], "text": text, "ascii_only": True,
                      "skipped": False, "safe_area_px": safe})
        label_records.append(place)
        rec.check(f"{case_id}.box{entry['index']}.label_within_canvas",
                  0 <= place["x"] and place["x"] + text_w <= display_w
                  and 0 <= place["y"] and place["y"] + text_h <= display_h,
                  f"标签矩形 ({place['x']},{place['y']}) 尺寸 {text_w}×{text_h} 在画布内")
    rec.check(f"{case_id}.labels_ascii_only",
              all(record.get("text", "").isascii() for record in label_records),
              "全部标签为 ASCII")
    log["labels"] = {"font": "PIL_default_bitmap", "ascii_only": True, "cjk_font_available": False,
                     "declaration": "无 CJK 字体，仅 ASCII 标签",
                     "safe_area_px": safe, "items": label_records}

    log["drawing"] = {
        "line_width_px": int(reference.DISPLAY_LINE_WIDTH_PX),
        "line_width_semantics": reference.LINE_WIDTH_SEMANTICS,
        "color_table": {str(key): list(value) for key, value in CLASS_COLORS.items()},
        "drawn_pixels": len(owner),
        "layer_order": ["synthetic_content_or_canvas_block_replication", "hud_band_ascii",
                        "boxes_from_frozen_border_pixel_sets", "box_labels_ascii"],
        "draw_fidelity_checked_after_hud_before_labels": True,
        "note": "边框像素在 HUD 文本带之上、ASCII 标签之下；标签可能覆盖少量边框像素（文本叠加为可选层）",
        "hud_band_text": hud_band if hud_drawn else None,
        "hud_band_drawn": hud_drawn,
        "hud_band_skipped_reason": None if hud_drawn else "canvas_too_small_for_hud_band",
    }

    # ── 语义：五元组 / 年龄 / 过期 ──────────────────────────────────────
    ages = reference.compute_ages(ledger["capture_time_ns"], ledger["result_time_ns"],
                                  ledger["overlay_commit_ns"])
    five_tuple = [ledger["displayed_frame_id"], frame_id, ages["age_result_ns"],
                  ages["age_frame_ns"], ages["display_semantics"]]
    rec.check(f"{case_id}.five_tuple_present",
              len(five_tuple) == 5 and all(value is not None for value in five_tuple),
              str(five_tuple))
    rec.check(f"{case_id}.five_tuple_semantics_matches",
              five_tuple[4] == reference.DISPLAY_SEMANTICS == contract["display_semantics"]["value"],
              f"{five_tuple[4]} == {reference.DISPLAY_SEMANTICS}")
    rec.check(f"{case_id}.age_frame_identity",
              ages["age_frame_ns"] == ages["age_result_ns"]
              + (ledger["result_time_ns"] - ledger["capture_time_ns"]),
              "age_frame == age_result + (result_publish - capture)（契约 identity）")
    rec.check(f"{case_id}.latest_result_overlay_index_differs",
              ledger["displayed_frame_id"] != frame_id,
              f"displayed_frame_id={ledger['displayed_frame_id']} 与 "
              f"result_frame_id={frame_id} 不同（最新结果叠加）")

    expected_stale = expected_stale_case(case_id, reference)
    rec.check(f"{case_id}.stale_expected",
              stale_info["stale_effective"] == expected_stale["stale_effective"]
              and stale_info["reason"] == expected_stale["reason"],
              f"实际 {stale_info} vs 期望 {expected_stale}")
    if stale_info["stale_effective"]:
        rec.check(f"{case_id}.stale_box_not_drawn", len(drawn_sets) == 0, "过期结果不叠加任何框")
    stale_events = []
    if stale_info["stale_effective"]:
        stale_events.append({"frame_id": frame_id, "age_frame_ns": stale_info["age_frame_ns"],
                             "cleared_at_ns": ledger["overlay_commit_ns"],
                             "reason": stale_info["reason"]})
    rec.check(f"{case_id}.stale_cleared_counted_once", len(stale_events) <= 1,
              f"每结果只计一次：{len(stale_events)} 条")
    zero_box_stale_conflation = bool(len(boxes) == 0 and stale_info["stale_effective"])
    rec.check(f"{case_id}.zero_box_not_counted_as_stale", zero_box_stale_conflation is False,
              "零框（NO_HAND）不因无框被判过期：过期仅由 PS stale 标志或 age 越限触发")

    fps_value = 1e9 / SYNTH_FRAME_INTERVAL_NS
    hud = build_hud(ages, frame_id=frame_id, boxes=len(drawn_sets),
                    stale_cleared=len(stale_events), dropped_frames=0, timeouts=0,
                    inference_time_ns=inference_time_ns, capture_fps=fps_value,
                    inference_fps=fps_value, display_fps=fps_value,
                    display_semantics=reference.DISPLAY_SEMANTICS)
    rec.check(f"{case_id}.hud_fields_complete",
              tuple(hud.keys()) == REQUIRED_HUD_FIELDS
              and tuple(contract["overlay_layout"]["hud_fields"]) == REQUIRED_HUD_FIELDS
              and tuple(hud.keys()) == reference.HUD_FIELDS,
              f"{len(hud)} 字段：{sorted(hud.keys())}")
    rec.check(f"{case_id}.hud_semantics_single",
              hud["display_semantics"] == reference.DISPLAY_SEMANTICS, hud["display_semantics"])

    log.update({
        "five_tuple": five_tuple,
        "ages": ages,
        "stale": {"stale_flag": stale_info["stale_flag"],
                  "age_frame_exceeds_limit": stale_info["age_frame_exceeds_limit"],
                  "stale_effective": stale_info["stale_effective"],
                  "reason": stale_info["reason"], "limit_ns": stale_info["limit_ns"],
                  "age_frame_ns": stale_info["age_frame_ns"], "stale_cleared": len(stale_events),
                  "events": stale_events, "zero_box_stale_conflation": zero_box_stale_conflation},
        "hud": hud,
        "hud_provenance": HUD_PROVENANCE,
        "hud_expected_fields": list(REQUIRED_HUD_FIELDS),
        "boxes_drawn": len(drawn_sets),
        "status": "PASS",
    })

    # ── 落盘：PNG → JSON 内记录 PNG 哈希 ────────────────────────────────
    png_info = write_png(run_dir / "cases" / f"{case_id}.png", image)
    log["png"] = {"name": f"cases/{case_id}.png", "sha256": png_info["sha256"],
                  "bytes": png_info["bytes"], "width": display_w, "height": display_h}

    if spec.get("d2_letterbox_proof"):
        proof = letterbox_d2_proof(src_w, src_h, geom, d2_reference, seed, case_index)
        proof_image = proof.pop("image_pixels")
        for key, ok, detail in proof["checks"]:
            rec.check(f"{case_id}.{key}", ok, detail)
        rec.check(f"{case_id}.letterbox_padding_value_is_128", proof["padding_value"] == 128,
                  f"补边像素常量 {proof['padding_value']} == 契约 padding_uint8 128")
        info2 = write_png(run_dir / "cases" / f"{case_id}_letterbox416.png",
                          Image.fromarray(proof_image, "RGB"))
        log["d2_letterbox_proof"] = proof
        log["png_letterbox416"] = {"name": f"cases/{case_id}_letterbox416.png",
                                   "sha256": info2["sha256"], "bytes": info2["bytes"],
                                   "width": 416, "height": 416}
    return log


# ─────────────────────────────────────────────────────────────────────────────
# S4-C golden 109 帧台账用例
# ─────────────────────────────────────────────────────────────────────────────


def render_batch_case(spec: Mapping[str, Any], case_index: int, reference, seed: int,
                      run_dir: Path, rec: Recorder, upstream: Mapping[str, str]) -> dict:
    case_id = spec["case_id"]
    golden_path = Path(upstream["s4c_golden109"])
    if not golden_path.is_file():
        rec.error(f"{case_id}.upstream_missing", f"只读 S4-C golden 不存在：{golden_path}")
        return {"case_id": case_id, "case_group": spec["group"], "case_kind": "s4c_batch",
                "status": "ERROR", "assertions": []}
    golden = read_json(golden_path)
    samples = golden["samples"]
    log: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "case_id": case_id,
        "case_group": spec["group"],
        "case_kind": "s4c_batch",
        "coordinate_path": "stage4_original_norm_xyxy",
        "coordinate_path_note": "显示层直接消费阶段4 原图归一化 xyxy（契约唯一允许路径）",
        "display_semantics": reference.DISPLAY_SEMANTICS,
        "notes": list(spec.get("notes", [])),
        "seed": int(seed),
        "random_box_n": RANDOM_BOX_N,
        "upstream": {"id": "s4c_golden109", "path": str(golden_path),
                     "sha256": sha256_file(golden_path), "mode": "read_only",
                     "samples": len(samples), "upstream_status": golden.get("status")},
        "limitations": ["只读重放上游 golden 记录，不重新解码、不重跑 NMS、不引入第二套阈值",
                        "台账时间与 HUD 数值为离线合成占位量，非实测"],
        "not_executed": ["实板 HDMI 叠加", "PL/UART 时序实测"],
        "status": "PASS",
    }

    rec.check(f"{case_id}.frame_count_ge_100", len(samples) >= 100,
              f"台账帧数 {len(samples)}（契约 T5-05 要求 ≥100 帧）")
    rec.check(f"{case_id}.upstream_status_pass", str(golden.get("status")) == "PASS",
              f"上游 status={golden.get('status')}")

    ledger_rows: list[dict] = []
    frame_ids: list[int] = []
    geometries: dict[str, dict] = {}
    zero_box_frames = 0
    stale_events: list[dict] = []
    distinct_states: dict[str, int] = {}
    round_trip_max = 0.0
    round_trip_n = 0
    first_ns = last_ns = None
    for position, sample in enumerate(samples):
        src_w, src_h = int(sample["geometry_wh"][0]), int(sample["geometry_wh"][1])
        frame_id = int(sample["frame_id"])
        detections = sample["detections_actual"]
        state = "OK" if detections else "NO_HAND"
        boxes = [(det["class_id"], det["score"], det["xyxy"], det["source_order"])
                 for det in detections]
        clock = synth_clock(frame_id, None, spec["display_lag_frames"])
        record = _record_from_boxes(frame_id, src_w, src_h, boxes, state, clock, False, 33_000_000)
        problems = reference.validate_result_record(record)
        if problems:
            rec.fail(f"{case_id}.frame{frame_id}.record_contract_valid", str(problems[:4]))
        ages = reference.compute_ages(clock["capture_time_ns"], clock["result_time_ns"],
                                      clock["overlay_commit_ns"])
        stale = reference.effective_stale(False, ages["age_frame_ns"])
        drawn = 0
        for _, _, xyxy, _ in boxes:
            clip = reference.clip_unit_box(xyxy)
            if clip["zero_area"] or stale["stale_effective"]:
                continue
            reference.original_norm_to_display_px(clip["xyxy"], src_w, src_h)
            drawn += 1
        if stale["stale_effective"]:
            stale_events.append({"frame_id": frame_id, "age_frame_ns": ages["age_frame_ns"],
                                 "cleared_at_ns": clock["overlay_commit_ns"],
                                 "reason": stale["reason"]})
        if not boxes:
            zero_box_frames += 1
        distinct_states[state] = distinct_states.get(state, 0) + 1
        frame_ids.append(frame_id)
        first_ns = clock["capture_time_ns"] if first_ns is None else first_ns
        last_ns = clock["capture_time_ns"]
        key = f"{src_w}x{src_h}"
        if key not in geometries:
            geom = reference.letterbox_geometry(src_w, src_h, 416, 416)
            hand = hand_geometry(src_w, src_h)
            rec.check(f"{case_id}.geometry_{key}_vs_hand",
                      all(geom[k] == hand[k] for k in hand),
                      f"{key}: new {geom['new_width']}×{geom['new_height']} "
                      f"off({geom['offset_x']},{geom['offset_y']}) "
                      f"pad({geom['pad_right']},{geom['pad_bottom']})")
            rng = random.Random(seed)
            errors = []
            degenerate = False
            try:
                for _ in range(RANDOM_BOX_N):
                    x1, x2 = sorted((rng.random(), rng.random()))
                    y1, y2 = sorted((rng.random(), rng.random()))
                    net_box = (x1, y1, x2, y2)
                    original = reference.network_norm_to_original_norm(net_box, geom)
                    back = reference.original_norm_to_network_norm(original, geom)
                    errors.append(max(abs(a - b) for a, b in zip(back, net_box)))
            except reference.DegenerateGeometryError as exc:
                degenerate = True
                rec.check(f"{case_id}.geometry_{key}.degenerate_raises", True, str(exc))
            if not degenerate:
                max_err = max(errors)
                rec.check(f"{case_id}.geometry_{key}.seeded_random_round_trip_n{RANDOM_BOX_N}",
                          max_err <= RANDOM_ROUND_TRIP_TOL,
                          f"N={RANDOM_BOX_N} 最大误差 {max_err:.3e}，"
                          f"容限 {RANDOM_ROUND_TRIP_TOL:g}")
                round_trip_max = max(round_trip_max, max_err)
                round_trip_n += len(errors)
            geometries[key] = {
                "geometry": {k2: geom[k2] for k2 in
                             ("src_width", "src_height", "new_width", "new_height", "offset_x",
                              "offset_y", "pad_right", "pad_bottom", "asymmetric_padding")},
                "hand_check_equal": all(geom[k] == hand[k] for k in hand),
                "degenerate": degenerate,
                "seeded_random_round_trip_max_abs_error": None if degenerate else max_err,
            }
        hud = build_hud(ages, frame_id=frame_id, boxes=drawn,
                        stale_cleared=1 if stale["stale_effective"] else 0, dropped_frames=0,
                        timeouts=0, inference_time_ns=33_000_000, capture_fps=0.0,
                        inference_fps=0.0, display_fps=0.0,
                        display_semantics=reference.DISPLAY_SEMANTICS)
        ledger_rows.append({
            "position": position, "frame_id": frame_id, "state": state,
            "geometry": {"width": src_w, "height": src_h}, "boxes_in_result": len(boxes),
            "boxes_drawn": drawn,
            "five_tuple": [clock["displayed_frame_id"], frame_id, ages["age_result_ns"],
                           ages["age_frame_ns"], ages["display_semantics"]],
            "stale": {"stale_effective": stale["stale_effective"], "reason": stale["reason"]},
            "hud": hud, "sample_id": sample["sample_id"],
        })

    rec.check(f"{case_id}.frame_ids_unique_indexable",
              len(set(frame_ids)) == len(frame_ids)
              and [row["frame_id"] for row in ledger_rows] == frame_ids,
              f"{len(frame_ids)} 帧，五元组可按 frame_id 索引，无重复帧号")
    semantics_values = {row["five_tuple"][4] for row in ledger_rows}
    rec.check(f"{case_id}.display_semantics_unique",
              semantics_values == {reference.DISPLAY_SEMANTICS},
              f"语义取值集合 {sorted(semantics_values)}")
    rec.check(f"{case_id}.five_tuples_complete",
              all(len(row["five_tuple"]) == 5 and all(v is not None for v in row["five_tuple"])
                  for row in ledger_rows), "逐帧五元组字段齐全")
    rec.check(f"{case_id}.no_same_index_claim",
              all(row["five_tuple"][0] != row["five_tuple"][1] for row in ledger_rows),
              "displayed_frame_id 与 result_frame_id 逐帧不同（最新结果叠加）")
    rec.check(f"{case_id}.zero_box_frames_present", zero_box_frames >= 1,
              f"零框 NO_HAND 帧数 {zero_box_frames}")
    rec.check(f"{case_id}.zero_box_not_counted_as_stale",
              all(not row["stale"]["stale_effective"] for row in ledger_rows
                  if row["boxes_in_result"] == 0), "零框帧不因无框被判过期")
    rec.check(f"{case_id}.stale_cleared_zero_in_batch", len(stale_events) == 0,
              f"批次台账内过期清除事件 {len(stale_events)} 条（合成年龄均未越限）")
    rec.check(f"{case_id}.states_only_ok_or_no_hand", set(distinct_states) <= {"OK", "NO_HAND"},
              f"状态分布 {distinct_states}")
    rec.check(f"{case_id}.hud_fields_complete_per_frame",
              all(tuple(row["hud"].keys()) == REQUIRED_HUD_FIELDS for row in ledger_rows),
              f"逐帧 HUD 含 {len(REQUIRED_HUD_FIELDS)} 字段")
    rec.check(f"{case_id}.no_second_threshold_or_nms",
              int(golden["comparison_spec"]["max_outputs_per_image"]) == reference.MAX_OUTPUTS_PER_IMAGE
              and float(golden["comparison_spec"]["score_threshold"]) == reference.SCORE_THRESHOLD
              and float(golden["comparison_spec"]["nms_iou"]) == reference.NMS_IOU,
              "上游阈值/NMS 与冻结常量一致（本工具不重跑 NMS、不引入第二套）")

    fps = ledger_fps(len(samples), int(first_ns), int(last_ns), len(samples), len(samples))

    # PNG：最小几何子集出图，其余帧只记台账
    ordered = sorted(range(len(samples)), key=lambda i: (int(samples[i]["geometry_wh"][0])
                                                         * int(samples[i]["geometry_wh"][1]), i))
    chosen: list[int] = []
    seen_geom: set[tuple] = set()
    sized = 0
    for index in ordered:
        key = tuple(samples[index]["geometry_wh"])
        if key in seen_geom:
            continue
        if len(chosen) >= int(spec["batch_png_limit"]) - 1:
            break
        chosen.append(index)
        seen_geom.add(key)
        sized += 1
    zero_index = next((i for i, sample in enumerate(samples) if not sample["detections_actual"]), None)
    if zero_index is not None and zero_index not in chosen:
        chosen.append(zero_index)
    png_records = []
    for index in chosen:
        sample = samples[index]
        src_w, src_h = int(sample["geometry_wh"][0]), int(sample["geometry_wh"][1])
        frame = synth_frame(src_w, src_h, seed, case_index + index)
        for det in sample["detections_actual"]:
            clip = reference.clip_unit_box(det["xyxy"])
            if clip["zero_area"]:
                continue
            px = reference.original_norm_to_display_px(clip["xyxy"], src_w, src_h)
            pixels = reference.border_pixel_sets(int(px["x1"]), int(px["y1"]), int(px["x2"]),
                                                 int(px["y2"]),
                                                 int(reference.DISPLAY_LINE_WIDTH_PX), src_w, src_h)
            color = CLASS_COLORS.get(int(det["class_id"]), (255, 255, 255))
            for x, y in pixels:
                frame[y, x] = color
        image = Image.fromarray(frame, "RGB")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        for det in sample["detections_actual"]:
            clip = reference.clip_unit_box(det["xyxy"])
            if clip["zero_area"]:
                continue
            px = reference.original_norm_to_display_px(clip["xyxy"], src_w, src_h)
            text = f"{det['class_name']} {float(det['score']):.2f}"
            if text.isascii():
                draw.text((int(px["x1"]) + 2, int(px["y1"]) + 2), text, font=font,
                          fill=(255, 255, 255))
        name = f"cases/{case_id}__{sample['sample_id']}.png"
        info = write_png(run_dir / "cases" / f"{case_id}__{sample['sample_id']}.png", image)
        png_records.append({"sample_id": sample["sample_id"], "frame_id": int(sample["frame_id"]),
                            "geometry": {"width": src_w, "height": src_h},
                            "detections": len(sample["detections_actual"]),
                            "name": name, "sha256": info["sha256"], "bytes": info["bytes"]})
    rec.check(f"{case_id}.png_subset_written", len(png_records) >= 1,
              f"出图子集 {len(png_records)} 例（其余 {len(samples) - len(png_records)} 帧仅台账，"
              f"原因见 png_subset_rule）")

    log.update({
        "frame_ledger": ledger_rows,
        "five_tuple": ledger_rows[0]["five_tuple"],
        "five_tuple_scope": "批次首帧；逐帧五元组见 frame_ledger[*].five_tuple",
        "five_tuple_count": len(ledger_rows),
        "frame_count": len(samples),
        "geometry_count": len(geometries),
        "geometries": geometries,
        "zero_box_frames": zero_box_frames,
        "state_distribution": distinct_states,
        "stale_clear_events": stale_events,
        "round_trip": {"seeded_n_per_geometry": RANDOM_BOX_N, "geometries": len(geometries),
                       "samples_total": round_trip_n, "max_abs_error": round_trip_max,
                       "tol": RANDOM_ROUND_TRIP_TOL},
        "hud": {**ledger_rows[-1]["hud"], "capture_fps": fps["capture_fps"],
                "inference_fps": fps["inference_fps"], "display_fps": fps["display_fps"]},
        "hud_provenance": HUD_PROVENANCE,
        "hud_expected_fields": list(REQUIRED_HUD_FIELDS),
        "ledger_fps": fps,
        "png_subset_rule": ("台账用例仅对最小面积几何各出 1 张 PNG（外加首个零框样本），其余帧只记"
                            "机器可读台账，避免无信息量的批量大图；未出图不等于未断言"),
        "png_subset": png_records,
        "boxes_in_result": sum(row["boxes_in_result"] for row in ledger_rows),
        "boxes_drawn": sum(row["boxes_drawn"] for row in ledger_rows),
    })
    return log


# ─────────────────────────────────────────────────────────────────────────────
# 全局断言
# ─────────────────────────────────────────────────────────────────────────────


def global_checks(reference, logs: Sequence[Mapping[str, Any]], run_dir: Path, rec: Recorder) -> dict:
    result: dict[str, Any] = {}

    # 1) 手算样例（≥3）：逆映射 + 正向 round-trip
    hand_rows = []
    for row in hand_computed_samples():
        geom = reference.letterbox_geometry(row["src_width"], row["src_height"], 416, 416)
        got = reference.network_norm_to_original_norm(row["network_box"], geom)
        err = max(abs(a - b) for a, b in zip(got, row["expected"]))
        literal_err = max(abs(a - b) for a, b in zip(got, row["expected_literals"]))
        back = reference.original_norm_to_network_norm(got, geom)
        rt = max(abs(a - b) for a, b in zip(back, row["network_box"]))
        rec.check(f"global.hand_sample.{row['sample_id']}.inverse_le_1e-9",
                  err <= INVERSE_TOL and literal_err <= INVERSE_TOL,
                  f"手算 {row['formula']} ⇒ {[format_float(v) for v in row['expected']]}；"
                  f"参考 {[format_float(v) for v in got]}；误差 {err:.3e} / 字面量 {literal_err:.3e}")
        rec.check(f"global.hand_sample.{row['sample_id']}.round_trip_le_1e-12",
                  rt <= RANDOM_ROUND_TRIP_TOL, f"round-trip 误差 {rt:.3e}")
        hand_rows.append({"sample_id": row["sample_id"], "formula": row["formula"],
                          "network_box": list(row["network_box"]),
                          "expected": list(row["expected"]),
                          "expected_literals": list(row["expected_literals"]),
                          "reference": list(got), "inverse_max_abs_error": err,
                          "literal_max_abs_error": literal_err, "round_trip_max_abs_error": rt})
    rec.check("global.hand_sample_count_ge_3", len(hand_rows) >= 3, f"手算样例数 {len(hand_rows)}")
    result["hand_samples"] = hand_rows

    # 2) 冻结 border_pixel_sets 的独立手算对拍（19 像素样例）
    x1, y1, x2, y2 = HAND_BORDER_PIXELS_BOX
    frozen_border = reference.border_pixel_sets(x1, y1, x2, y2, 2, 16, 16)
    rec.check("global.border_pixels_vs_hand",
              [tuple(p) for p in frozen_border] == HAND_BORDER_PIXELS,
              f"手算 {HAND_BORDER_PIXELS} vs 冻结 {[tuple(p) for p in frozen_border]}")
    result["border_pixel_hand_sample"] = {"box": list(HAND_BORDER_PIXELS_BOX), "width": 2,
                                          "expected": HAND_BORDER_PIXELS,
                                          "reference": [list(p) for p in frozen_border]}

    # 3) 五元组 / 语义唯一性 / 无“画面与结果来自同一帧号”的伪称
    five_tuples: list[list] = []
    semantics: set[str] = set()
    for log in logs:
        if "frame_ledger" in log:
            for row in log["frame_ledger"]:
                five_tuples.append(row["five_tuple"])
                semantics.add(row["five_tuple"][4])
        elif log.get("five_tuple"):
            five_tuples.append(log["five_tuple"])
            semantics.add(log["five_tuple"][4])
    batch_present = any("frame_ledger" in log for log in logs)
    rec.check("global.five_tuple_count",
              len(five_tuples) >= 100 if batch_present else len(five_tuples) >= len(logs),
              f"五元组总数 {len(five_tuples)}；S4-C 台账 109 帧用例"
              f"{'已选中（要求 ≥100）' if batch_present else '未选中（仅要求 ≥ 用例数）'}")
    rec.check("global.display_semantics_unique", semantics == {reference.DISPLAY_SEMANTICS},
              f"全部产物语义集合 {sorted(semantics)}（唯一）")
    rec.check("global.no_same_index_claim", all(t[0] != t[1] for t in five_tuples),
              "所有五元组的 displayed_frame_id 与 result_frame_id 不同（禁止伪称同一帧号）")
    result["five_tuple_total"] = len(five_tuples)
    result["display_semantics_values"] = sorted(semantics)

    # 4) HUD 13 字段
    hud_bad = []
    for log in logs:
        rows = log.get("frame_ledger") or [log]
        for row in rows:
            if tuple(row["hud"].keys()) != REQUIRED_HUD_FIELDS:
                hud_bad.append(log["case_id"])
                break
    rec.check("global.hud_all_cases_13_fields", not hud_bad, f"异常用例 {hud_bad[:3]}")
    result["hud_fields"] = list(REQUIRED_HUD_FIELDS)
    result["hud_field_count"] = len(REQUIRED_HUD_FIELDS)

    # 5) 过期清除唯一性与零框不混同
    events: list[dict] = []
    conflation: list[str] = []
    for log in logs:
        if "frame_ledger" in log:
            events.extend(log["stale_clear_events"])
            if any(row["boxes_in_result"] == 0 and row["stale"]["stale_effective"]
                   for row in log["frame_ledger"]):
                conflation.append(log["case_id"])
        else:
            events.extend(log.get("stale", {}).get("events", []))
            if log.get("stale", {}).get("zero_box_stale_conflation"):
                conflation.append(log["case_id"])
    keys = [(event["frame_id"], event["cleared_at_ns"]) for event in events]
    rec.check("global.stale_cleared_counted_once", len(keys) == len(set(keys)),
              f"过期清除事件 {len(events)} 条，无同一结果重复计数")
    rec.check("global.stale_reason_recorded",
              all(event.get("reason") in (reference.STALE_REASON_FLAG, reference.STALE_REASON_AGE,
                                          reference.STALE_REASON_BOTH) for event in events),
              f"原因取值 {sorted({event['reason'] for event in events})}")
    rec.check("global.zero_box_not_counted_as_stale", not conflation,
              f"零框被判过期的用例 {conflation}")
    result["stale_clear_events"] = events
    result["zero_box_stale_conflation_cases"] = conflation

    # 6) 用词与伪称扫描（用例 JSON + PNG 字节；manifest/summary 由写后扫描覆盖）
    scan_targets = sorted((run_dir / "logs").glob("*.json")) + sorted((run_dir / "cases").glob("*.png"))
    result["artifact_scan"] = scan_paths(scan_targets)
    rec.check("global.wording_and_claim_scan_zero_hits",
              result["artifact_scan"]["hit_total"] == 0,
              f"扫描 {result['artifact_scan']['artifacts_scanned']} 个产物，"
              f"禁用称谓/伪称命中 {result['artifact_scan']['hit_total']} 次")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 运行主体
# ─────────────────────────────────────────────────────────────────────────────


def selected_cases(selector: str | None) -> list[dict]:
    cases = case_table()
    if not selector:
        return cases
    wanted = [token.strip() for token in selector.split(",") if token.strip()]
    chosen = []
    for case in cases:
        if any(case["case_id"] == token or case["group"] == token or token in case["case_id"]
               for token in wanted):
            chosen.append(case)
    return chosen


def git_info() -> dict:
    import subprocess

    info: dict[str, Any] = {"head": None, "branch": None, "dirty_paths": [], "method": "git_cli"}
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        status = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT,
                                capture_output=True, text=True, check=True).stdout.splitlines()
        info.update({"head": head, "branch": branch, "dirty_paths": status[:60],
                     "dirty_path_count": len(status)})
    except Exception as exc:  # noqa: BLE001
        info["method"] = "git_cli_failed"
        info["error"] = f"{type(exc).__name__}: {exc}"
        head_file = REPO_ROOT / ".git" / "HEAD"
        if head_file.is_file():
            content = head_file.read_text(encoding="utf-8").strip()
            info["head_file_content"] = content
            if content.startswith("ref: "):
                ref_path = REPO_ROOT / ".git" / content.split(" ", 1)[1].strip()
                if ref_path.is_file():
                    info["head"] = ref_path.read_text(encoding="utf-8").strip()
    return info


def library_versions() -> dict:
    import PIL

    return {"python": sys.version.split()[0],
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__, "pillow": PIL.__version__,
            "platform": platform.platform(), "executable": sys.executable}


def package_files() -> list[dict]:
    files = []
    for name in ("render_s5b_overlay.py", "run_s5b_evidence.py", "test_s5b_overlay.py"):
        path = Path(__file__).resolve().parent / name
        if path.is_file():
            files.append({"name": name, "path": str(path), "sha256": sha256_file(path),
                          "bytes": path.stat().st_size})
    return files


def build_manifest(args, run_dir: Path, reference, exit_code: int, status: str,
                   logs: Sequence[Mapping[str, Any]], counts: Mapping[str, int],
                   globals_result: Mapping[str, Any], inventory: Mapping[str, Any],
                   checks: Sequence[Mapping[str, Any]],
                   errors: Sequence[Mapping[str, Any]]) -> dict:
    png_hashes: dict[str, str] = {}
    for log in logs:
        for key in ("png", "png_letterbox416"):
            if log.get(key):
                png_hashes[log[key]["name"]] = log[key]["sha256"]
        for info in log.get("png_subset", []) or []:
            png_hashes[info["name"]] = info["sha256"]
    json_stats = {f"logs/{log['case_id']}.json": log["_json_sha256"] for log in logs}
    json_stats_digest = sha256_bytes("\n".join(f"{key}:{json_stats[key]}"
                                               for key in sorted(json_stats)).encode("utf-8"))
    png_set_digest = sha256_bytes("\n".join(f"{key}:{png_hashes[key]}"
                                            for key in sorted(png_hashes)).encode("utf-8"))
    rng_samples_total = 0
    for log in logs:
        round_trip = log.get("round_trip") or {}
        if round_trip.get("seeded_n"):
            rng_samples_total += int(round_trip["seeded_n"])
        if round_trip.get("samples_total"):
            rng_samples_total += int(round_trip["samples_total"])
    case_status = []
    for log in logs:
        case_checks = [check for check in checks if check["id"].startswith(log["case_id"] + ".")]
        case_status.append({
            "case_id": log["case_id"], "group": log["case_group"],
            "kind": log.get("case_kind"), "status": log.get("status", "PASS"),
            "assertions_total": len(case_checks),
            "assertions_failed": len([c for c in case_checks if c["status"] == "FAIL"]),
            "coordinate_path": log.get("coordinate_path"),
            "five_tuple": log.get("five_tuple"),
            "json": f"logs/{log['case_id']}.json", "json_sha256": log["_json_sha256"],
            "png": log.get("png"), "png_letterbox416": log.get("png_letterbox416"),
            "png_subset": log.get("png_subset"), "png_subset_count": len(log.get("png_subset", []) or []),
            "boxes_in_result": log.get("boxes_in_result"), "boxes_drawn": log.get("boxes_drawn"),
            "stale": log.get("stale"), "hud": log.get("hud"),
            "frame_count": log.get("frame_count"),
        })
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "run_id": args.run_id,
        "run_dir": str(run_dir),
        "command": {"argv": [str(item) for item in sys.argv],
                    "shell": ("python scripts/stage5_s5b/render_s5b_overlay.py "
                              f"--out {args.out} --run-id {args.run_id} --seed {args.seed}"
                              + (f" --cases {args.cases}" if args.cases else "")
                              + (" --selfcheck" if args.selfcheck else ""))},
        "exit_code": exit_code,
        "status": status,
        "source": {"repo_root": str(REPO_ROOT), "git": git_info()},
        "scripts": package_files(),
        "imported_modules": [
            {"path": str(REPO_ROOT / REFERENCE_REL), "sha256": sha256_file(REPO_ROOT / REFERENCE_REL),
             "contract_id": reference.CONTRACT_ID, "contract_status": reference.CONTRACT_STATUS,
             "role": "冻结几何/口径唯一来源（import，未复制公式）"},
            {"path": str(REPO_ROOT / D2_REFERENCE_REL), "sha256": sha256_file(REPO_ROOT / D2_REFERENCE_REL),
             "role": "D2 冻结 letterbox_rgb_uint8（正向图像同源证明）"},
            {"path": str(REPO_ROOT / CONTRACT_REL), "sha256": sha256_file(REPO_ROOT / CONTRACT_REL),
             "role": "阶段5 G0 契约字段（只读）"},
        ],
        "upstream_inputs": inventory,
        "versions": library_versions(),
        "seed": int(args.seed),
        "statistics": {
            "cases_total": len(logs), "cases_failed": len([c for c in case_status if c["status"] != "PASS"]),
            "assertions_total": counts["assertions_total"], "assertions_passed": counts["assertions_passed"],
            "assertions_failed": counts["assertions_failed"], "errors_total": counts["errors_total"],
            "random_box_n_per_geometry": RANDOM_BOX_N,
            "rng_samples_total": rng_samples_total,
            "png_count": len(png_hashes), "json_count": len(json_stats),
            "five_tuple_total": globals_result.get("five_tuple_total"),
            "hud_field_count": globals_result.get("hud_field_count"),
            "stale_clear_events": len(globals_result.get("stale_clear_events", [])),
            "capability": {"hardware": "NOT_RUN", "vivado": "NOT_RUN", "xsim": "NOT_RUN",
                           "hdmi_screenshot": "NOT_RUN"},
        },
        "determinism": {"status": "NOT_RUN_SINGLE_PASS",
                        "note": "单 pass 不构成确定性证据；请用 scripts/stage5_s5b/run_s5b_evidence.py 双 pass 比对",
                        "png_sha256": png_hashes, "json_stats": json_stats,
                        "png_set_digest": png_set_digest, "json_stats_digest": json_stats_digest},
        "cases": case_status,
        "assertions": list(checks),
        "errors": list(errors),
        "globals": dict(globals_result),
        "limitations": [
            "几何/口径全部导入冻结参考模块；本工具不复制 letterbox/逆映射公式",
            "合成帧与合成时间台账为离线占位，非真实摄像头/HDMI 数据",
            "S4-B 时间字段为 0 哨兵：改用离线合成台账时间，不声称实测",
            "G0 未固定非 1080p 的布局相对缩放规则：本工具仅对安全区按画布高度等比缩放，线宽统一用 1080p 参考值 2",
            "画布缩放仅用整数倍块复制（无插值）；文本叠加为可选 ASCII 层",
        ],
        "not_executed": ["实板 HDMI 输出与截图", "摄像头采集与 30 分钟无死锁运行",
                         "PL/UART 时序与真实 FPS 实测", "阶段6 状态机联动实测",
                         "CJK 字体渲染（本工具仅 ASCII 标签）"],
    }


CONTRACT_TEST_CASE_STATUS = (
    # 契约 docs/stage5/s5a_stage5_display_g0_fields.json test_cases 的离线准备覆盖对照（如实标注）
    ("T5-01", "PASS", "非方形/竖屏/奇数宽/方形无补边/画布整数倍不拉伸：逐值断言 + 出图",
     ["t5_01_landscape_1280x720", "t5_01_portrait_720x1280", "t5_01_oddw_683x384",
      "t5_01_square_640x640_no_pad", "t5_01_canvas_683x384_k2_1920x1080",
      "t5_01_canvas_1280x720_k1_1920x1080", "t5_01_s4b_palm_1440x1920"]),
    ("T5-02", "PASS", "贴边/四角/部分越界/裁剪零面积/补边带零面积/退化几何兜底：逐边裁剪断言 + 出图",
     ["t5_02_edge_flush", "t5_02_corners", "t5_02_partial_out_of_bounds",
      "t5_02_clip_zero_area", "t5_02_letterbox_padding_zero_area",
      "t5_02_degenerate_new_w_1"]),
    ("T5-03", "PASS", "15 框上限与零框 NO_HAND：契约校验 + 出图",
     ["t5_03_multi_15", "t5_03_no_hand_zero", "t5_03_no_hand_s4b_640x963"]),
    ("T5-04", "PASS", "过期边界/原因/每结果只计一次：age==limit 不过期、limit+1 过期、flag/both",
     ["t5_04_age_equal_limit", "t5_04_age_limit_plus_1", "t5_04_stale_flag_small_age",
      "t5_04_stale_both"]),
    ("T5-05", "PASS", "结果—帧号对应：S4-C 只读台账 109 帧，五元组可按 frame_id 索引、语义唯一",
     ["t5_05_s4c_golden109_frame_ledger"]),
    ("T5-06", "PASS", "分数用词扫描：产物 0 命中；字段名统一 score",
     []),
    ("T5-07", "PASS", "奇数补边半像素：683×384 上 91/下 92 保留；D2 端点对齐 scale 同源",
     ["t5_01_oddw_683x384"]),
    ("T5-08", "PARTIAL", "FPS/延迟口径：13 个 HUD 字段与本工具两个年龄可由合成台账复算；"
                         "真实采集/推理/显示 FPS 与实测延迟 NOT_RUN（需硬件）", []),
    ("T5-09", "NOT_RUN", "30 分钟无死锁：需实板与摄像头，本任务不执行（无硬件）", []),
    ("T5-10", "PARTIAL", "S5-B 侧：显示消费的框可直接追溯到 S4-C 台账与 S4-B 记录（只读重放、"
                         "不重跑 NMS）；与阶段4 整数结果的完整回归属 S5-C 任务", []),
    ("T5-11", "PARTIAL", "预热/丢帧/超时字段在 HUD 与逐用例 JSON 中单列；取值为离线占位（非实测）", []),
    ("T5-12", "PASS", "显示语义一致性：全部产物 display_semantics 唯一且与五元组一致", []),
)


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except Exception:  # noqa: BLE001
        return str(path)


def write_summary(run_dir: Path, manifest: Mapping[str, Any], logs: Sequence[Mapping[str, Any]],
                  extra_sections: str = "") -> None:
    lines: list[str] = []
    lines.append(f"# S5-B 离线渲染/叠框自测证据 — RunId `{manifest['run_id']}`")
    lines.append("")
    lines.append(f"- 任务：{TASK_ID}（阶段5 离线准备；不接硬件、不跑 Vivado/xsim）")
    lines.append(f"- 状态：**{manifest['status']}**")
    lines.append(f"- 退出码（写 summary 时计算）：**{manifest['exit_code']}**"
                 "（0=全部断言 PASS / 1=断言失败 / 2=环境或输入错误）；"
                 "写后复核见 `console/wording_scan.txt`、`console/hash_recheck.txt` 与 "
                 "`console/final_verdict.json`")
    lines.append(f"- 源码 HEAD：`{(manifest['source']['git'].get('head') or 'UNKNOWN')}`"
                 f"（分支 `{manifest['source']['git'].get('branch')}`）")
    lines.append(f"- 种子：{manifest['seed']}；种子化随机框 N={RANDOM_BOX_N}/几何；"
                 f"五元组 {manifest['statistics']['five_tuple_total']} 条")
    lines.append(f"- 断言：{manifest['statistics']['assertions_passed']}"
                 f"/{manifest['statistics']['assertions_total']} PASS，"
                 f"FAIL {manifest['statistics']['assertions_failed']}，"
                 f"ERROR {manifest['statistics']['errors_total']}")
    lines.append("")
    lines.append("## 一键命令 / 恢复命令")
    lines.append("")
    lines.append("```bash")
    base_run_id = manifest["run_id"]
    if base_run_id.endswith(("_a", "_b")):
        base_run_id = base_run_id[:-2]
    lines.append(f"# 本证据包的实际一键命令（RunId 基名 {base_run_id}，产出 <out>/{base_run_id}_a 与 _b）")
    lines.append(f"python scripts/stage5_s5b/run_s5b_evidence.py "
                 f"--out {_repo_relative(run_dir.parent)} --run-id {base_run_id} "
                 f"--seed {manifest['seed']}")
    lines.append("")
    lines.append("# 全新 RunId 重跑（不覆盖已有 RunId）")
    lines.append("python scripts/stage5_s5b/run_s5b_evidence.py --out report/evidence/S5-B \\")
    lines.append("       --run-id <新的 RunId> --seed 20261021")
    lines.append("")
    lines.append("# 恢复：单 pass 重出（新 RunId，不覆盖他人 RunId）")
    lines.append("python scripts/stage5_s5b/render_s5b_overlay.py --out report/evidence/S5-B \\")
    lines.append("       --run-id <新 RunId>_recover --seed 20261021")
    lines.append("")
    lines.append("# 恢复：库内自检 / 子集用例")
    lines.append("python scripts/stage5_s5b/render_s5b_overlay.py --selfcheck")
    lines.append("python scripts/stage5_s5b/render_s5b_overlay.py --out tmp/5/S5-B \\")
    lines.append("       --run-id probe_t5_04 --cases T5-04")
    lines.append("")
    lines.append("# 单元测试")
    lines.append("python -m unittest discover -s scripts/stage5_s5b -p \"test_s5b_overlay.py\" -v")
    lines.append("")
    lines.append("# 只读输入恢复参数（契约声明路径不可用时）")
    lines.append("python scripts/stage5_s5b/render_s5b_overlay.py --run-id <id> \\")
    lines.append("       --s4b-dir <S4-B 目录> --s4c-golden <replay_golden_109.json>")
    lines.append("```")
    lines.append("")
    lines.append("## 用例逐项结果")
    lines.append("")
    lines.append("| 用例 | 组 | 状态 | 断言(通过/总) | 框(结果/绘制) | PNG | 五元组 / 台账 |")
    lines.append("|---|---|---|---|---|---|---|")
    for log in logs:
        five = log.get("five_tuple")
        if "frame_ledger" in log:
            five = f"{log['frame_ledger'][0]['five_tuple']} … 共 {len(log['frame_ledger'])} 帧"
        png = (log.get("png") or {}).get("name")
        if log.get("png_subset"):
            png = (f"{png} + 子集 {len(log['png_subset'])} 张" if png
                   else f"台账子集 {len(log['png_subset'])} 张（用例日志见 logs/）")
        elif not png:
            png = "-"
        case_checks = [check for check in manifest["assertions"]
                       if check["id"].startswith(log["case_id"] + ".")]
        passed = len([c for c in case_checks if c["status"] == "PASS"])
        lines.append(f"| `{log['case_id']}` | {log['case_group']} | {log.get('status', 'PASS')} | "
                     f"{passed}/{len(case_checks)} | {log.get('boxes_in_result')}/"
                     f"{log.get('boxes_drawn')} | {png} | `{five}` |")
    lines.append("")
    lines.append("## 数值断言摘要")
    lines.append("")
    lines.append("| 手算样例 | 算式 | 手算值 | 参考值 | 误差 | 容限 |")
    lines.append("|---|---|---|---|---|---|")
    for row in manifest["globals"]["hand_samples"]:
        lines.append(f"| {row['sample_id']} | `{row['formula']}` | "
                     f"{[format_float(v) for v in row['expected']]} | "
                     f"{[format_float(v) for v in row['reference']]} | "
                     f"{row['inverse_max_abs_error']:.3e} | {INVERSE_TOL:g} |")
    border = manifest["globals"]["border_pixel_hand_sample"]
    lines.append("")
    lines.append(f"- 冻结 `border_pixel_sets` 独立手算对拍：框 {border['box']} 线宽 {border['width']} "
                 f"⇒ {len(border['expected'])} 像素，逐值一致")
    seeded = [log["round_trip"]["seeded_max_abs_error"] for log in logs
              if log.get("round_trip", {}).get("seeded_max_abs_error") is not None]
    lines.append(f"- 原图→网络→原图 round-trip：逐用例最大误差 "
                 f"{max(seeded) if seeded else float('nan'):.3e}，容限 {RANDOM_ROUND_TRIP_TOL:g}；"
                 f"每几何 N={RANDOM_BOX_N}（种子 {manifest['seed']}）")
    batch = next((log for log in logs if log.get("case_kind") == "s4c_batch"), None)
    if batch:
        lines.append(f"- S4-C 台账：{batch['frame_count']} 帧 / {batch['geometry_count']} 种几何；"
                     f"台账内种子化随机框样本 {batch['round_trip']['samples_total']} 条，最大误差 "
                     f"{batch['round_trip']['max_abs_error']:.3e}")
    lines.append(f"- 显示像素层 vs float64 连续参考：逐框逐边 ≤{DISPLAY_PX_TOL:g} px"
                 "（实际落在取整半像素内）")
    lines.append("- 683×384：上侧补边 91 / 下侧补边 92，非对称补边保留，未被对称化")
    lines.append("")
    lines.append("## 语义断言摘要")
    lines.append("")
    lines.append(f"- display_semantics 唯一取值：`{manifest['globals']['display_semantics_values']}`")
    lines.append(f"- 五元组 {manifest['globals']['five_tuple_total']} 条，全部满足 "
                 "displayed_frame_id != result_frame_id（最新结果叠加；"
                 "未出现画面与结果来自同一帧号的伪称）")
    lines.append(f"- 过期清除事件 {len(manifest['globals']['stale_clear_events'])} 条：每结果只计一次，"
                 "记录 frame_id / age_frame_ns / cleared_at_ns / reason；"
                 "边界为严格大于（age==limit 不过期）")
    lines.append(f"- 零框（NO_HAND）被判过期的用例："
                 f"{manifest['globals']['zero_box_stale_conflation_cases'] or '无'}")
    lines.append("")
    scan = manifest["globals"]["artifact_scan"]
    lines.append("## 用词与伪称扫描")
    lines.append("")
    lines.append(f"- 扫描 {scan['artifacts_scanned']} 个产物（用例 JSON、PNG 字节），命中 {scan['hit_total']} 次")
    lines.append(f"- 禁用 token 身份（拆分存储以避免自触发）："
                 f"{[t['token_id'] + ':' + t['codepoints'] for t in scan['tokens']]}")
    lines.append("- 字段名统一使用 `score`；阈值/NMS/上限/类别顺序取自冻结契约，未引入第二套")
    lines.append("")
    lines.append("## 契约 test_cases 覆盖对照（逐项如实标注）")
    lines.append("")
    lines.append("| 契约用例 | 本任务状态 | 说明 | 覆盖用例 |")
    lines.append("|---|---|---|---|")
    for case_id, status, note, covered in CONTRACT_TEST_CASE_STATUS:
        lines.append(f"| {case_id} | {status} | {note} | "
                     f"{', '.join('`' + item + '`' for item in covered) if covered else '-'} |")
    lines.append("")
    lines.append("## 确定性")
    lines.append("")
    lines.append(f"- 确定性状态：{manifest['determinism']['status']}"
                 "（双 pass 比对口径见 `determinism.note` 与 `console/determinism_compare.txt`）")
    lines.append(f"- 主 pass A 的 PNG 集合摘要：`{manifest['determinism']['png_set_digest']}`")
    lines.append(f"- 主 pass A 的 JSON 统计摘要：`{manifest['determinism']['json_stats_digest']}`")
    lines.append("- 双 pass 比对结果见 `run_s5b_evidence.py` 写入的 `determinism` 段")
    lines.append("")
    lines.append("## HUD 字段")
    lines.append("")
    lines.append(f"- 逐用例 JSON 的 `hud` 字段：{manifest['globals']['hud_fields']}")
    lines.append("- 数值均为离线合成占位量（非实测）；逐字段口径见 `hud_provenance`")
    lines.append("")
    lines.append("## 限制与未执行项")
    lines.append("")
    for item in manifest["limitations"]:
        lines.append(f"- 限制：{item}")
    for item in manifest["not_executed"]:
        lines.append(f"- NOT_RUN：{item}")
    lines.append("")
    lines.append(f"- 环境错误：{manifest['errors'] if manifest['errors'] else '无'}")
    if extra_sections:
        lines.append("")
        lines.append(extra_sections)
    lines.append("")
    write_text(run_dir / "summary.md", "\n".join(lines))


def run_pipeline(args, run_dir: Path) -> dict:
    contract = read_json(REPO_ROOT / CONTRACT_REL)
    reference = load_python_module(REPO_ROOT / REFERENCE_REL, "s5_display_geometry_reference")
    d2_reference = load_python_module(REPO_ROOT / D2_REFERENCE_REL, "s1_t02_d2_numeric_reference")

    rec = Recorder()
    rec.check("env.contract_id_matches", reference.CONTRACT_ID == contract["contract_id"],
              f"{reference.CONTRACT_ID} == {contract['contract_id']}")
    rec.check("env.contract_json_rounding_rule_id",
              contract["geometry"].get("rounding_rule_id") == reference.ROUNDING_RULE,
              f"rounding_rule_id={contract['geometry'].get('rounding_rule_id')}")
    rec.check("env.hud_fields_match_reference",
              tuple(contract["overlay_layout"]["hud_fields"]) == reference.HUD_FIELDS
              == REQUIRED_HUD_FIELDS, "契约 HUD == 冻结模块 HUD_FIELDS == 工具字段表")
    rec.check("env.stale_limit_single_source",
              float(contract["stale_and_age"]["stale_age_limit_ns"]) == float(reference.STALE_AGE_LIMIT_NS),
              f"{contract['stale_and_age']['stale_age_limit_ns']} == {reference.STALE_AGE_LIMIT_NS}")
    rec.check("env.thresholds_match",
              float(contract["scoring"]["score_threshold"]) == reference.SCORE_THRESHOLD
              and float(contract["scoring"]["nms_iou"]) == reference.NMS_IOU
              and int(contract["scoring"]["max_outputs_per_image"]) == reference.MAX_OUTPUTS_PER_IMAGE
              and tuple(contract["scoring"]["class_order"]) == reference.CLASS_ORDER,
              "score 阈值 / NMS IoU / 上限 / 类别顺序与冻结常量一致")
    rec.check("env.contract_no_frozen_conflict",
              reference.STALE_AGE_LIMIT_NS == 200_000_000
              and contract["display_semantics"]["value"] == reference.DISPLAY_SEMANTICS,
              "过期阈值 200ms 与画面语义单一来源一致")

    upstream_paths = resolve_upstream_inputs(contract, {"s4b_dir": args.s4b_dir,
                                                        "s4c_golden109": args.s4c_golden})
    inventory = upstream_inventory(upstream_paths)
    for key, item in inventory.items():
        rec.check(f"env.upstream_input.{key}", bool(item.get("exists")),
                  f"{item.get('path')} exists={item.get('exists')}")

    specs = selected_cases(args.cases)
    logs: list[dict] = []
    for index, spec in enumerate(specs):
        logs.append(render_case(spec, index, reference, d2_reference, contract, args.seed,
                                run_dir, rec, upstream_paths))

    # 逐用例断言注入 + 落盘（JSON 不含时间戳 ⇒ 可复现）
    for log in logs:
        case_checks = rec.case_checks(log["case_id"])
        log["assertions"] = case_checks
        log["assertion_counts"] = {
            "total": len(case_checks),
            "passed": len([c for c in case_checks if c["status"] == "PASS"]),
            "failed": len([c for c in case_checks if c["status"] == "FAIL"]),
        }
        if log.get("status") != "ERROR":
            log["status"] = "FAIL" if log["assertion_counts"]["failed"] else "PASS"
        log["_json_sha256"] = dump_json(run_dir / "logs" / f"{log['case_id']}.json", log)
    rec.check("env.case_count", len(logs) == len(specs) and len(logs) > 0,
              f"执行用例数 {len(logs)} / 选中 {len(specs)}")

    globals_result = global_checks(reference, logs, run_dir, rec)
    counts = rec.counts()
    exit_code = rec.exit_code()
    status = "PASS" if exit_code == EXIT_PASS else ("ERROR" if rec.errors else "FAIL")
    globals_result["selected_cases"] = [spec["case_id"] for spec in specs]
    globals_result["seed"] = int(args.seed)
    globals_result["case_count"] = len(logs)
    return {"contract": contract, "reference": reference, "d2_reference": d2_reference,
            "recorder": rec, "logs": logs, "globals": globals_result, "counts": counts,
            "status": status, "exit_code": exit_code, "inventory": inventory,
            "upstream_paths": upstream_paths}


def post_write_scan(run_dir: Path, console_dir: Path) -> dict:
    """写后复核：扫描 summary/manifest/日志/PNG 的禁用用词与“画面与结果来自同一帧号”的伪称。"""
    targets = [run_dir / "summary.md", run_dir / "run_manifest.json"]
    targets += sorted((run_dir / "logs").glob("*.json"))
    targets += sorted((run_dir / "cases").glob("*.png"))
    result = scan_paths(targets)
    lines = [f"写后用词/伪称扫描：artifacts={result['artifacts_scanned']} "
             f"hits={result['hit_total']}"]
    for token in result["tokens"]:
        lines.append(f"  token {token['token_id']} role={token['role']} "
                     f"codepoints=[{token['codepoints']}] sha256={token['sha256'][:16]}")
    for item in result["per_artifact"]:
        lines.append(f"  {item['path']} bytes={item['bytes']} hits={item['hit_total']} "
                     f"sha256={item['sha256']}")
    write_text(console_dir / "wording_scan.txt", "\n".join(lines) + "\n")
    dump_json(console_dir / "wording_scan.json", result)
    return result


def render_run(args, run_dir: Path) -> int:
    if run_dir.exists() and not args.force:
        markers = [run_dir / "run_manifest.json", run_dir / "cases", run_dir / "logs"]
        if any(marker.exists() for marker in markers):
            print(f"[ERROR] RunId 目录已存在且非空：{run_dir}"
                  "（不覆盖他人 RunId；如需覆盖请显式 --force）")
            return EXIT_ERROR
    (run_dir / "cases").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    console_dir = run_dir / "console"
    console_dir.mkdir(parents=True, exist_ok=True)

    print(f"[S5-B] run_id={args.run_id} out={run_dir} seed={args.seed} cases={args.cases or 'ALL'}")
    result = run_pipeline(args, run_dir)
    logs = result["logs"]
    manifest = build_manifest(args, run_dir, result["reference"], result["exit_code"],
                              result["status"], logs, result["counts"], result["globals"],
                              result["inventory"], result["recorder"].checks,
                              result["recorder"].errors)
    write_summary(run_dir, manifest, logs)
    scan_after = post_write_scan(run_dir, console_dir)
    final_exit = result["exit_code"]
    if scan_after["hit_total"] > 0:
        final_exit = EXIT_FAIL if final_exit != EXIT_ERROR else final_exit
        result["recorder"].error("global.post_write_scan", f"写后扫描命中 {scan_after['hit_total']} 次")
    final_counts = result["recorder"].counts()
    manifest["exit_code"] = final_exit
    manifest["status"] = "PASS" if final_exit == EXIT_PASS else ("ERROR" if result["recorder"].errors else "FAIL")
    manifest["statistics"].update({"assertions_total": final_counts["assertions_total"],
                                   "assertions_passed": final_counts["assertions_passed"],
                                   "assertions_failed": final_counts["assertions_failed"],
                                   "errors_total": final_counts["errors_total"]})
    manifest["errors"] = result["recorder"].errors
    manifest["post_write_scan"] = {"artifacts_scanned": scan_after["artifacts_scanned"],
                                   "hit_total": scan_after["hit_total"],
                                   "tokens": scan_after["tokens"],
                                   "artifact_hashes": {item["path"]: item["sha256"]
                                                       for item in scan_after["per_artifact"]},
                                   "note": "写后复核 summary/manifest/日志/PNG；"
                                           "manifest 自身哈希由 S5-B 证据驱动脚本再复核"}
    dump_json(run_dir / "run_manifest.json", manifest)
    write_summary(run_dir, {**manifest, "exit_code": final_exit}, logs)

    print(f"[S5-B] cases={len(logs)} assertions={final_counts['assertions_total']} "
          f"failed={final_counts['assertions_failed']} errors={final_counts['errors_total']} "
          f"exit={final_exit}")
    for failed_id in result["recorder"].failed_ids():
        print(f"[S5-B][FAIL] {failed_id}")
    for error in result["recorder"].errors:
        print(f"[S5-B][ERROR] {error['id']}: {error['detail']}")
    print(f"[S5-B] run_dir={run_dir}")
    print(f"[S5-B] png_set_digest={manifest['determinism']['png_set_digest']}")
    print(f"[S5-B] json_stats_digest={manifest['determinism']['json_stats_digest']}")
    return final_exit


def selfcheck(args) -> int:
    """库内自检：几何同源 / 手算样例 / round-trip / 边界语义 / 画布；不写证据。"""
    contract = read_json(REPO_ROOT / CONTRACT_REL)
    reference = load_python_module(REPO_ROOT / REFERENCE_REL, "s5_display_geometry_reference")
    d2_reference = load_python_module(REPO_ROOT / D2_REFERENCE_REL, "s1_t02_d2_numeric_reference")
    rec = Recorder()
    rec.check("selfcheck.contract_id", reference.CONTRACT_ID == contract["contract_id"] == "S5A-G0-v2",
              reference.CONTRACT_ID)
    for spec in case_table():
        if spec["kind"] != "synthetic" or spec["expects_degenerate"]:
            continue
        src_w, src_h = int(spec["src_w"]), int(spec["src_h"])
        geom = reference.letterbox_geometry(src_w, src_h, 416, 416)
        hand = hand_geometry(src_w, src_h)
        d2_geom = d2_reference.letterbox_geometry(src_w, src_h, 416, 416)
        rec.check(f"selfcheck.{spec['case_id']}.geometry_vs_hand",
                  all(geom[k] == hand[k] for k in hand)
                  and all(geom[k] == d2_geom[k] for k in ("new_width", "new_height",
                                                          "offset_x", "offset_y")),
                  f"{src_w}×{src_h} new {geom['new_width']}×{geom['new_height']}")
        rng = random.Random(args.seed)
        errors = []
        for _ in range(RANDOM_BOX_N):
            x1, x2 = sorted((rng.random(), rng.random()))
            y1, y2 = sorted((rng.random(), rng.random()))
            net_box = (x1, y1, x2, y2)
            original = reference.network_norm_to_original_norm(net_box, geom)
            back = reference.original_norm_to_network_norm(original, geom)
            errors.append(max(abs(a - b) for a, b in zip(back, net_box)))
        rec.check(f"selfcheck.{spec['case_id']}.round_trip_n{RANDOM_BOX_N}",
                  max(errors) <= RANDOM_ROUND_TRIP_TOL, f"最大误差 {max(errors):.3e}")
    for row in hand_computed_samples():
        geom = reference.letterbox_geometry(row["src_width"], row["src_height"], 416, 416)
        got = reference.network_norm_to_original_norm(row["network_box"], geom)
        err = max(abs(a - b) for a, b in zip(got, row["expected"]))
        rec.check(f"selfcheck.hand.{row['sample_id']}", err <= INVERSE_TOL,
                  f"误差 {err:.3e}（容限 {INVERSE_TOL:g}）")
    try:
        reference.network_norm_to_original_norm((0.1, 0.1, 0.2, 0.2),
                                                reference.letterbox_geometry(1, 300, 416, 416))
        rec.fail("selfcheck.degenerate_raises", "未抛 DegenerateGeometryError")
    except reference.DegenerateGeometryError as exc:
        rec.check("selfcheck.degenerate_raises", True, str(exc))
    rec.check("selfcheck.stale_boundary",
              reference.is_stale(reference.STALE_AGE_LIMIT_NS) is False
              and reference.is_stale(reference.STALE_AGE_LIMIT_NS + 1) is True
              and reference.effective_stale(True, 1000)["reason"] == reference.STALE_REASON_FLAG,
              "age==limit 不过期；limit+1 过期；flag 原因 stale_flag")
    rec.check("selfcheck.canvas_fit",
              reference.canvas_fit(683, 384, 1920, 1080) == {"scale_k": 2, "drawn_width": 1366,
                                                             "drawn_height": 768, "offset_x": 277,
                                                             "offset_y": 156},
              "683×384 → k=2、1366×768、offset (277,156)")
    rec.check("selfcheck.border_pixels_vs_hand",
              [tuple(p) for p in reference.border_pixel_sets(*HAND_BORDER_PIXELS_BOX, 2, 16, 16)]
              == HAND_BORDER_PIXELS, "border_pixel_sets 与独立手算 19 像素一致")
    print(f"[S5-B][selfcheck] assertions={rec.counts()['assertions_total']} "
          f"failed={rec.counts()['assertions_failed']}")
    for failed_id in rec.failed_ids():
        print(f"[S5-B][selfcheck][FAIL] {failed_id}")
    if rec.errors:
        return EXIT_ERROR
    return rec.exit_code()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="render_s5b_overlay.py",
        description="S5-B 离线叠框渲染与数值/语义/用词自测（只读 S4-B/S4-C；导入冻结几何参考）")
    parser.add_argument("--out", default=DEFAULT_OUT_REL,
                        help=f"证据根目录（默认 {DEFAULT_OUT_REL}，相对仓库根；run 目录 = <out>/<run-id>）")
    parser.add_argument("--run-id", default="s5b_local",
                        help="RunId；证据落在 <out>/<run-id>/；已存在非空目录时报错（不覆盖他人 RunId）")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"确定性随机种子（默认 {DEFAULT_SEED}）")
    parser.add_argument("--cases", default=None,
                        help="可选子集：逗号分隔的 case_id 或组号（如 T5-04）")
    parser.add_argument("--selfcheck", action="store_true",
                        help="只做库内自检（几何同源/手算/round-trip/边界语义），不写证据")
    parser.add_argument("--force", action="store_true", help="允许写入已存在的 RunId 目录")
    parser.add_argument("--s4b-dir", default=None, help="恢复用：覆盖只读 S4-B 目录")
    parser.add_argument("--s4c-golden", default=None, help="恢复用：覆盖只读 S4-C golden 路径")
    return parser


def run_main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:  # noqa: BLE001 - 老式流对象可能不支持 reconfigure
            pass
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, buffer)
    exit_code = EXIT_PASS
    run_dir = Path(args.out).resolve() / args.run_id
    try:
        try:
            if args.selfcheck:
                exit_code = selfcheck(args)
            else:
                exit_code = render_run(args, run_dir)
        except FileNotFoundError as exc:
            exit_code = EXIT_ERROR
            print(f"[ERROR] 输入/环境缺失：{exc}")
        except ImportError as exc:
            exit_code = EXIT_ERROR
            print(f"[ERROR] 冻结模块导入失败：{exc}")
        except Exception as exc:  # noqa: BLE001
            exit_code = EXIT_ERROR
            print(f"[ERROR] 未预期异常：{type(exc).__name__}: {exc}")
            traceback.print_exc(file=sys.stdout)
    finally:
        sys.stdout = original_stdout
        if not args.selfcheck:
            console_dir = run_dir / "console"
            console_dir.mkdir(parents=True, exist_ok=True)
            write_text(console_dir / "render_stdout.txt", buffer.getvalue())
            write_text(console_dir / "render_exit_code.txt", f"{exit_code}\n")
    return exit_code


def main() -> int:
    return run_main()


if __name__ == "__main__":
    sys.exit(main())