#!/usr/bin/env python3
"""S1-T02-D9 tiny416 原始 YOLO 检测头 CPU 参考解码器。

输入是 Darknet YOLO 层卷积的 sigmoid 前 raw logits。扁平布局严格采用
entry_index：((anchor * 10 + entry) * grid_h * grid_w + row * grid_w + col)，
    张量布局则为 [3, 10, grid_h, grid_w]。entry 依次为 x、y、w、h、objectness、
class0..class4；本参考只支持单图、416×416 网络输入和 new_coords=0。

输出直接复用 D6 Prediction 与 stable_nms，score 使用 sigmoid(obj)*sigmoid(class)，
阈值含等号（D6 语义），类别内 NMS IoU=0.45，最多保留 15 个。与 Darknet
get_yolo_detections 的 objectness/prob 严格大于阈值不同，这里按 D6 的 >= 判定。
letterbox 逆变换使用 D2 的整数截断尺寸及左上 floor padding；Darknet C 后处理
使用总 pad 的半值，奇数 pad 时会与此 D2 像素语义相差半像素，本参考不声称逐值相同。
坐标裁剪到 [0,1]，
裁剪后零面积框丢弃，以满足 D6 归一化 xyxy 约束。

活动 D8 与正式 D4 tiny416 cfg 的 SHA-256 相同，二者 masks 均为 3,4,5 / 1,2,3；
D4 tiny320 与 Darknet 上游 cfg 也使用相同 masks。旧的 0,1,2 比较来自非正式
``official_darknet_seeded/cfg/yolov4-tiny-custom.cfg``，不能标作正式 D4 tiny416。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

try:
    from .s1_t02_d6_detection_metrics import (
        EXPECTED_CLASSES,
        FIXED_NMS_IOU,
        MAX_OUTPUTS,
        Prediction,
        stable_nms,
    )
except ImportError:
    from s1_t02_d6_detection_metrics import (
        EXPECTED_CLASSES,
        FIXED_NMS_IOU,
        MAX_OUTPUTS,
        Prediction,
        stable_nms,
    )


NETWORK_WIDTH = 416
NETWORK_HEIGHT = 416
CLASS_COUNT = 5
ENTRY_COUNT = 4 + 1 + CLASS_COUNT
SCALE_X_Y = 1.05
ANCHORS = ((10, 14), (23, 27), (37, 58), (81, 82), (135, 169), (344, 319))


@dataclass(frozen=True)
class HeadSpec:
    """一个 tiny416 YOLO 头的栅格与 D8 cfg anchor mask。"""

    name: str
    grid_width: int
    grid_height: int
    anchor_mask: tuple[int, int, int]


HEAD_SPECS = (
    HeadSpec("13x13", 13, 13, (3, 4, 5)),
    HeadSpec("26x26", 26, 26, (1, 2, 3)),
)
CLASS_NAMES = tuple(EXPECTED_CLASSES)


class DecodeError(ValueError):
    """表示检测头、图像几何或数值输入不符合参考解码接口。"""


def _is_indexable(value: Any) -> bool:
    """判断值是否为可按长度和整数下标读取的张量/序列。"""

    return not isinstance(value, (str, bytes, bytearray)) and hasattr(value, "__len__") and hasattr(value, "__getitem__")


def _materialize_cpu_tensor(value: Any, head_name: str) -> Any:
    """将常见 CPU 张量转换为 Python 容器，不接受 GPU 张量。"""

    if hasattr(value, "device"):
        device = getattr(value, "device")
        device_type = getattr(device, "type", str(device).split(":", 1)[0])
        if device_type != "cpu":
            raise DecodeError(f"{head_name} 必须是 CPU 张量，收到 device={device}")
    if hasattr(value, "detach"):
        try:
            value = value.detach()
        except Exception as exc:
            raise DecodeError(f"{head_name} 张量无法 detach") from exc
    if hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except Exception as exc:
            raise DecodeError(f"{head_name} 张量无法转换为 CPU 列表") from exc
    return value


def _finite_logit(value: Any, label: str) -> float:
    """将一个 raw logit 转为有限浮点数，拒绝布尔值和文本。"""

    if isinstance(value, (bool, str, bytes, bytearray)):
        raise DecodeError(f"{label} 必须是有限数值，不能是布尔值或文本")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DecodeError(f"{label} 必须是有限数值") from exc
    if not math.isfinite(result):
        raise DecodeError(f"{label} 不能是 NaN 或 Inf")
    return result


def _flatten_exact(value: Any, shape: tuple[int, ...], label: str) -> list[float]:
    """验证张量各维长度并按 C 顺序展平为有限浮点数。"""

    if not shape:
        return [_finite_logit(value, label)]
    if not _is_indexable(value):
        raise DecodeError(f"{label} 张量维度错误，期望形状 {shape}")
    try:
        length = len(value)
    except (TypeError, OverflowError) as exc:
        raise DecodeError(f"{label} 无法读取张量维度") from exc
    if length != shape[0]:
        raise DecodeError(f"{label} 形状错误：第 0 维应为 {shape[0]}，实际为 {length}")
    flattened: list[float] = []
    for index in range(length):
        try:
            child = value[index]
        except (TypeError, IndexError, KeyError) as exc:
            raise DecodeError(f"{label} 无法读取第 {index} 项") from exc
        flattened.extend(_flatten_exact(child, shape[1:], f"{label}[{index}]"))
    return flattened


def _read_head(raw: Any, spec: HeadSpec) -> list[float]:
    """读取 Darknet 原生扁平布局或 [anchor,entry,row,col] 张量。"""

    value = _materialize_cpu_tensor(raw, spec.name)
    total = 3 * ENTRY_COUNT * spec.grid_height * spec.grid_width
    if not _is_indexable(value):
        raise DecodeError(f"{spec.name} 必须是扁平序列或四维张量")
    if len(value) == total:
        try:
            first = value[0] if total else None
        except (TypeError, IndexError, KeyError) as exc:
            raise DecodeError(f"{spec.name} 无法读取扁平序列") from exc
        if not _is_indexable(first):
            return _flatten_exact(value, (total,), spec.name)
    shape = (3, ENTRY_COUNT, spec.grid_height, spec.grid_width)
    return _flatten_exact(value, shape, spec.name)


def _sigmoid(value: float) -> float:
    """用稳定形式计算 sigmoid，避免有限大 logits 的指数溢出。"""

    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _safe_exp(value: float, head_name: str, row: int, col: int, entry: str) -> float:
    """计算 Darknet 的 exp(tw/th)，明确拒绝指数溢出。"""

    try:
        result = math.exp(value)
    except OverflowError as exc:
        raise DecodeError(f"{head_name}[row={row},col={col}] {entry} 的 exp 溢出") from exc
    if not math.isfinite(result):
        raise DecodeError(f"{head_name}[row={row},col={col}] {entry} 的 exp 非有限")
    return result


def _letterbox_geometry(image_width: int, image_height: int) -> tuple[int, int, int, int]:
    """返回 D2 的整数截断 resize 宽高及左上 floor padding。"""

    if NETWORK_WIDTH * image_height < NETWORK_HEIGHT * image_width:
        resized_width = NETWORK_WIDTH
        resized_height = (image_height * NETWORK_WIDTH) // image_width
    else:
        resized_height = NETWORK_HEIGHT
        resized_width = (image_width * NETWORK_HEIGHT) // image_height
    if resized_width < 1 or resized_height < 1:
        raise DecodeError("D2 letterbox 整数截断产生了零尺寸 resize")
    pad_left = (NETWORK_WIDTH - resized_width) // 2
    pad_top = (NETWORK_HEIGHT - resized_height) // 2
    return resized_width, resized_height, pad_left, pad_top


def _validate_fixed_configuration() -> None:
    """拒绝固定头配置中的栅格、类别、anchor 或 mask 结构异常。"""

    if CLASS_COUNT != len(CLASS_NAMES) or ENTRY_COUNT != 4 + 1 + CLASS_COUNT:
        raise DecodeError("类别数或 YOLO entry 配置异常")
    if len(ANCHORS) != 6 or any(
        len(anchor) != 2 or any(type(value) is not int or value <= 0 for value in anchor)
        for anchor in ANCHORS
    ):
        raise DecodeError("anchor 配置异常")
    if len(HEAD_SPECS) != 2 or len({spec.name for spec in HEAD_SPECS}) != 2:
        raise DecodeError("tiny416 必须恰有两个名称唯一的检测头")
    if tuple((spec.name, spec.grid_width, spec.grid_height) for spec in HEAD_SPECS) != (
        ("13x13", 13, 13),
        ("26x26", 26, 26),
    ):
        raise DecodeError("tiny416 检测头名称或栅格尺寸与固定参考不符")
    for spec in HEAD_SPECS:
        if type(spec.grid_width) is not int or type(spec.grid_height) is not int:
            raise DecodeError(f"{spec.name} 栅格尺寸类型异常")
        if spec.grid_width <= 0 or spec.grid_height <= 0:
            raise DecodeError(f"{spec.name} 栅格尺寸必须为正数")
        if (
            len(spec.anchor_mask) != 3
            or len(set(spec.anchor_mask)) != 3
            or any(type(index) is not int or not 0 <= index < len(ANCHORS) for index in spec.anchor_mask)
        ):
            raise DecodeError(f"{spec.name} anchor mask 必须是三个互异有效索引")


def _finite_coordinate(value: float, label: str) -> float:
    """拒绝反变换产生的非有限坐标。"""

    if not math.isfinite(value):
        raise DecodeError(f"{label} 反变换产生非有限坐标")
    return value


def _clip_unit(value: float) -> float:
    """裁剪一个归一化坐标到 D6 所需的闭区间。"""

    return min(1.0, max(0.0, value))


def decode_yolov4_tiny416(
    head_logits: Mapping[str, Any],
    image_key: str,
    image_width: int,
    image_height: int,
    *,
    score_threshold: float,
) -> list[Prediction]:
    """将两个 tiny416 检测头的 raw logits 解码为 D6 规范的归一化 xyxy。

    ``head_logits`` 必须恰含 ``13x13`` 与 ``26x26`` 两项。每头可以是
    Darknet 原生一维扁平数组，或形状严格为 ``[3, 10, grid_h, grid_w]`` 的
    CPU 张量/嵌套序列；不接受 batch 维、NHWC 或 class-interleaved 布局。
    阈值是必填参数，范围为闭区间 [0.25, 0.50]。

    D8 cfg 的第二头 mask 为 (1,2,3)，故 anchor 0 未被该 cfg 的两个头使用，
    anchor 3 则在两头重复出现；本函数保留此配置事实，不替训练 cfg 修正。

    D2 左上 pad 使用整数 floor；Darknet C ``correct_yolo_boxes`` 使用总 pad/2.0，
    奇数总 pad 时本函数与其逆变换会有意相差半像素。

    越过原图边界的框会按坐标逐边裁剪至 [0,1]；裁剪后宽或高为零的框丢弃。
    返回列表已由 D6 ``stable_nms`` 执行类别内 IoU=0.45 的 greedy NMS，并
    按 D6 顺序截断为每图最多 15 个结果。
    """

    _validate_fixed_configuration()
    if not isinstance(head_logits, Mapping):
        raise DecodeError("head_logits 必须是以头名称为键的 mapping")
    if set(head_logits) != {spec.name for spec in HEAD_SPECS}:
        raise DecodeError("head_logits 必须且只能包含 13x13 与 26x26 两个检测头")
    if not isinstance(image_key, str) or not image_key:
        raise DecodeError("image_key 必须是非空字符串")
    if type(image_width) is not int or image_width <= 0:
        raise DecodeError("image_width 必须是正整数")
    if type(image_height) is not int or image_height <= 0:
        raise DecodeError("image_height 必须是正整数")
    if isinstance(score_threshold, (bool, str, bytes, bytearray)):
        raise DecodeError("score_threshold 必须是范围 0.25..0.50 内的有限数值")
    try:
        score_threshold = float(score_threshold)
    except (TypeError, ValueError, OverflowError) as exc:
        raise DecodeError("score_threshold 必须是范围 0.25..0.50 内的有限数值") from exc
    if not math.isfinite(score_threshold) or not 0.25 <= score_threshold <= 0.50:
        raise DecodeError("score_threshold 必须在闭区间 [0.25, 0.50]")

    resized_width, resized_height, pad_left, pad_top = _letterbox_geometry(image_width, image_height)
    values_by_head = {spec.name: _read_head(head_logits[spec.name], spec) for spec in HEAD_SPECS}
    candidates: list[Prediction] = []
    source_order = 0

    for spec in HEAD_SPECS:
        values = values_by_head[spec.name]
        grid_width = spec.grid_width
        grid_height = spec.grid_height
        spatial_size = grid_width * grid_height
        for row in range(grid_height):
            for col in range(grid_width):
                cell = row * grid_width + col
                for local_anchor, anchor_index in enumerate(spec.anchor_mask):
                    base = local_anchor * ENTRY_COUNT * spatial_size + cell

                    def raw_entry(entry: int) -> float:
                        return values[base + entry * spatial_size]

                    tx = _sigmoid(raw_entry(0)) * SCALE_X_Y - 0.5 * (SCALE_X_Y - 1.0)
                    ty = _sigmoid(raw_entry(1)) * SCALE_X_Y - 0.5 * (SCALE_X_Y - 1.0)
                    tw = raw_entry(2)
                    th = raw_entry(3)
                    width_scale = _safe_exp(tw, spec.name, row, col, "tw")
                    height_scale = _safe_exp(th, spec.name, row, col, "th")
                    anchor_width, anchor_height = ANCHORS[anchor_index]
                    box_width = width_scale * (anchor_width / NETWORK_WIDTH)
                    box_height = height_scale * (anchor_height / NETWORK_HEIGHT)
                    if not math.isfinite(box_width) or not math.isfinite(box_height):
                        raise DecodeError(f"{spec.name}[row={row},col={col}] 框宽高溢出")

                    center_x = (col + tx) / grid_width
                    center_y = (row + ty) / grid_height
                    objectness = _sigmoid(raw_entry(4))
                    eligible_scores: list[tuple[int, float]] = []
                    for class_id in range(CLASS_COUNT):
                        confidence = objectness * _sigmoid(raw_entry(5 + class_id))
                        if confidence >= score_threshold:
                            eligible_scores.append((class_id, confidence))
                        source_order += 1
                    if not eligible_scores:
                        continue

                    left = (center_x - box_width / 2.0) * NETWORK_WIDTH
                    right = (center_x + box_width / 2.0) * NETWORK_WIDTH
                    top = (center_y - box_height / 2.0) * NETWORK_HEIGHT
                    bottom = (center_y + box_height / 2.0) * NETWORK_HEIGHT
                    x1 = _finite_coordinate((left - pad_left) / resized_width, "x1")
                    y1 = _finite_coordinate((top - pad_top) / resized_height, "y1")
                    x2 = _finite_coordinate((right - pad_left) / resized_width, "x2")
                    y2 = _finite_coordinate((bottom - pad_top) / resized_height, "y2")
                    box = (_clip_unit(x1), _clip_unit(y1), _clip_unit(x2), _clip_unit(y2))
                    if box[2] <= box[0] or box[3] <= box[1]:
                        continue
                    for class_id, confidence in eligible_scores:
                        candidates.append(
                            Prediction(
                                image_key=image_key,
                                class_id=class_id,
                                name=CLASS_NAMES[class_id],
                                confidence=confidence,
                                box=box,
                                source_order=source_order - CLASS_COUNT + class_id,
                            )
                        )

    return stable_nms(candidates, score_threshold, FIXED_NMS_IOU, MAX_OUTPUTS)
