"""阶段5 显示「补边逆映射 / 坐标 / 结果年龄 / 过期」冻结参考实现（S5-A v2 契约）。

定位：本模块是阶段5 离线准备的**唯一几何与口径来源**（single source of truth）。
- 只读复用 D2/2A 冻结公式，不重新定义 letterbox：`verification/s1_t02_d2_numeric_reference.py::letterbox_geometry`
  与此处的 `letterbox_geometry` 必须逐值一致（由测试 `test_letterbox_matches_d2_reference` 对拍）。
- 本模块只做**纯计算**：不读文件、不画图、不依赖 Pillow/numpy；渲染与出图由 S5-B 实现。
- 所有中间量用 float64；**只有最终落像素时**才按 ROUNDING_RULE 取整一次。

来源与状态（不得冒充已完成）：
- 几何公式来源：`docs/stage4/s4a_stage4_g0_fields.json` 与 S4-D v1 草案 §3.1（w4 冻结树 `73c3dad`，只读）。
- 契约为阶段5 **G0 定稿（离线准备）**；`STALE_AGE_LIMIT_NS` 与阶段4/5 同源同一常量。
  本模块不代表阶段5 已开工、已上板或已验收；未实测项一律 `NOT_RUN`。
"""

from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence

# ── 契约身份 ────────────────────────────────────────────────────────────────
CONTRACT_ID = "S5A-G0-v2"
CONTRACT_STATUS = "STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED"

# ── 沿用 2A 的冻结常量（不得在显示层引入第二套）────────────────────────────
CLASS_ORDER: tuple[str, ...] = ("fist", "palm", "one", "two_up", "three")
SCORE_THRESHOLD = 0.25          # score >= 0.25（含等号）
NMS_IOU = 0.45                  # 类别内 greedy NMS，跨类不抑制
MAX_OUTPUTS_PER_IMAGE = 15      # NMS 前截断与 NMS 后输出上限
NETWORK_INPUT_W = 416
NETWORK_INPUT_H = 416

# ── 结果年龄与过期：单一常量、同源固定（阶段4 `stale_age_limit` ≡ 阶段5 判定阈值）──
STALE_AGE_LIMIT_NS = 200_000_000        # 200 ms
STALE_AGE_LIMIT_SOURCE = "S5A-G0-v2 / S4A stale_age_limit 同源固定（同一单调时基）"
STALE_AGE_LIMIT_STATUS = "G0_FIXED_OFFLINE"

# ── 布局与绘制（G0 已固定，1080p 参考；其他分辨率按相对规则缩放）─────────────
DISPLAY_LINE_WIDTH_PX = 2
LINE_WIDTH_SEMANTICS = "偶数线宽居中：几何线落于像素索引 p 时占 {p-1, p}，逐边钳到画布内"
ROUNDING_RULE = "round_half_up_to_nearest_pixel_index"   # round_half_up(v)=floor(v+0.5)
SAFE_AREA_PX_1080P = 16
LABEL_ANCHOR_RULE = "框左上外侧；越界翻转到框内左上；仍越界则钳入安全区"

# 画面语义：Wong 已定（2026-10-21）＝最新结果叠加（latest-result overlay）
DISPLAY_SEMANTICS = "B_latest_result_overlay"

# 显示层只允许消费这些 PS 侧记录字段（方案 B：时间/状态/丢帧字段只记 PS 侧，不经 UART）
CONSUMED_STAGE4_FIELDS: tuple[str, ...] = (
    "frame_id",
    "geometry",
    "state",
    "detection_count",
    "detections",
    "stale",
    "dropped_frames",
    "capture_time_ns",
    "result_time_ns",
    "inference_time_ns",
    "end_to_end_latency_ns",
    "error_code",
)
DETECTION_FIELDS: tuple[str, ...] = ("class_id", "class_name", "score", "xyxy", "source_order")
HUD_FIELDS: tuple[str, ...] = (
    "capture_fps", "inference_fps", "display_fps",
    "inference_time_ns", "age_result_ns", "age_frame_ns",
    "frame_id", "boxes", "stale_cleared", "dropped_frames", "timeouts", "warmup_state",
    "display_semantics",
)

STALE_REASON_NONE = "none"
STALE_REASON_FLAG = "stale_flag"
STALE_REASON_AGE = "age_frame_exceeds_limit"
STALE_REASON_BOTH = "both"

# 阶段4 结果记录的 uint32 关联域；session_id 是本显示绑定采用的会话键。
UINT32_MAX = (1 << 32) - 1
JOIN_KEY_FIELD_RANGES: dict[str, tuple[int, int]] = {
    "session_id": (0, UINT32_MAX),
    "frame_id": (0, UINT32_MAX),
    "result_seq": (1, UINT32_MAX),
    "repeat_index": (1, UINT32_MAX),
}


class DegenerateGeometryError(ValueError):
    """`new_w<=1` 或 `new_h<=1`：端点对齐逆式不适用，必须改用阶段4 原图坐标字段。"""


class ContractViolation(ValueError):
    """上游记录违反契约（字段缺失/类型错误/语义冲突）。"""


def round_half_up(value: float) -> int:
    """G0 固定的唯一取整规则：最近像素索引，0.5 向上（非负域等价于四舍五入）。"""
    if not math.isfinite(value):
        raise ContractViolation(f"取整输入必须有限，得到 {value!r}")
    return int(math.floor(value + 0.5))


def letterbox_geometry(src_width: int, src_height: int,
                       dst_width: int = NETWORK_INPUT_W,
                       dst_height: int = NETWORK_INPUT_H) -> dict:
    """复现 D2/Darknet 冻结正向几何（整数截断 resize + 左上 floor 偏移）。

    返回 new_width/new_height/offset_x/offset_y 及逆映射所需的 w_scale/h_scale
    （端点对齐，`new==1` 时按冻结实现取 0.0）。
    """
    if min(src_width, src_height, dst_width, dst_height) <= 0:
        raise ContractViolation("图像尺寸必须为正整数")
    if (float(dst_width) / src_width) < (float(dst_height) / src_height):
        new_width = dst_width
        new_height = (src_height * dst_width) // src_width
    else:
        new_height = dst_height
        new_width = (src_width * dst_height) // src_height
    offset_x = (dst_width - new_width) // 2
    offset_y = (dst_height - new_height) // 2
    return {
        "src_width": src_width,
        "src_height": src_height,
        "dst_width": dst_width,
        "dst_height": dst_height,
        "new_width": new_width,
        "new_height": new_height,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "w_scale": (src_width - 1) / (new_width - 1) if new_width > 1 else 0.0,
        "h_scale": (src_height - 1) / (new_height - 1) if new_height > 1 else 0.0,
        "padding_normalized": 0.5,
        "padding_uint8": 128,
        # 记录补边奇偶事实，供 T5-07（奇数补边半像素）断言使用
        "pad_right": dst_width - new_width - offset_x,
        "pad_bottom": dst_height - new_height - offset_y,
        "asymmetric_padding": ((dst_width - new_width) % 2 == 1)
        or ((dst_height - new_height) % 2 == 1),
    }


def _check_geom(geom: Mapping[str, object]) -> None:
    if not isinstance(geom, Mapping):
        raise ContractViolation("geometry 必须是对象")
    for key in ("src_width", "src_height", "new_width", "new_height", "offset_x", "offset_y"):
        if key not in geom:
            raise ContractViolation(f"geometry 缺少键 {key}")
    if int(geom["src_width"]) <= 1 or int(geom["src_height"]) <= 1:
        raise DegenerateGeometryError(
            "源尺寸 <=1 像素：无有效采样点，逆/正映射均无定义，必须使用阶段4 原图坐标字段"
        )
    if int(geom["new_width"]) <= 1 or int(geom["new_height"]) <= 1:
        raise DegenerateGeometryError(
            "退化几何（new_w<=1 或 new_h<=1）：端点对齐逆式不适用，必须使用阶段4 原图坐标字段"
        )


def network_norm_to_original_norm(box: Sequence[float], geom: Mapping[str, object]) -> tuple[float, float, float, float]:
    """网络输入归一化坐标 → 原图归一化坐标（不存在提前取整，float64 全程）。

    语义：`u,v` 相对 **letterbox 后 416×416** 网络输入；输出相对**原视频帧**。
    步骤：反补边（减 offset）→ 端点对齐反缩放 → 原图归一化。
    """
    _check_geom(geom)
    if len(box) != 4:
        raise ContractViolation("框必须是 4 个分量")
    src_w, src_h = int(geom["src_width"]), int(geom["src_height"])
    dst_w, dst_h = int(geom["dst_width"]), int(geom["dst_height"])
    off_x, off_y = int(geom["offset_x"]), int(geom["offset_y"])
    new_w, new_h = int(geom["new_width"]), int(geom["new_height"])
    w_scale = float(geom["w_scale"])
    h_scale = float(geom["h_scale"])
    out: list[float] = []
    for coord, dst, off, span in ((box[0], dst_w, off_x, src_w),
                                  (box[1], dst_h, off_y, src_h),
                                  (box[2], dst_w, off_x, src_w),
                                  (box[3], dst_h, off_y, src_h)):
        value = float(coord)
        if not math.isfinite(value):
            raise ContractViolation(f"坐标必须有限，得到 {coord!r}")
        if value < 0.0 or value > 1.0:
            raise ContractViolation(f"网络归一化坐标必须位于 [0,1]，得到 {value!r}")
        resized = value * dst - off                      # 反补边：落在缩放图坐标
        scale = w_scale if span == src_w else h_scale    # 端点对齐（与正向同一 scale）
        px = resized * scale                             # 反缩放：原图连续像素坐标
        out.append(px / (span - 1) if span > 1 else 0.0)  # 原图归一化
    return (out[0], out[1], out[2], out[3])


def original_norm_to_network_norm(box: Sequence[float], geom: Mapping[str, object]) -> tuple[float, float, float, float]:
    """正向：原图归一化坐标 → 网络输入归一化坐标（用于 round-trip 自检，非显示路径）。

    与逆向共用同一 `_check_geom` 退化守卫（禁止 ZeroDivisionError 或静默映射）。
    """
    _check_geom(geom)
    if len(box) != 4:
        raise ContractViolation("框必须是 4 个分量")
    src_w, src_h = int(geom["src_width"]), int(geom["src_height"])
    dst_w, dst_h = int(geom["dst_width"]), int(geom["dst_height"])
    off_x, off_y = int(geom["offset_x"]), int(geom["offset_y"])
    out: list[float] = []
    for coord, dst, off, span in ((box[0], dst_w, off_x, src_w), (box[1], dst_h, off_y, src_h),
                                  (box[2], dst_w, off_x, src_w), (box[3], dst_h, off_y, src_h)):
        px = float(coord) * (span - 1)                      # 原图归一化 → 连续像素
        scale = (span - 1) / ((int(geom["new_width"]) - 1) if span == src_w
                              else (int(geom["new_height"]) - 1))
        out.append((px / scale + off) / dst)                # 反缩放 → 加补边 → 归一化
    return (out[0], out[1], out[2], out[3])


def clip_unit_box(box: Sequence[float]) -> dict:
    """逐边裁剪到 [0,1]；返回裁剪后坐标、是否裁剪、是否零面积（零面积不得绘制）。"""
    if len(box) != 4:
        raise ContractViolation("框必须是 4 个分量")
    x1, y1, x2, y2 = (float(v) for v in box)
    for v in (x1, y1, x2, y2):
        if not math.isfinite(v):
            raise ContractViolation("框坐标必须有限")
    if not (x2 > x1 and y2 > y1):
        raise ContractViolation("上游框必须为正面积（x2>x1 且 y2>y1）")
    cx1, cy1 = max(0.0, min(1.0, x1)), max(0.0, min(1.0, y1))
    cx2, cy2 = max(0.0, min(1.0, x2)), max(0.0, min(1.0, y2))
    clipped = (cx1, cy1, cx2, cy2) != (x1, y1, x2, y2)
    zero_area = not (cx2 > cx1 and cy2 > cy1)
    return {"xyxy": (cx1, cy1, cx2, cy2), "clipped": clipped, "zero_area": zero_area}


def original_norm_to_display_px(box: Sequence[float], display_width: int, display_height: int,
                                fit: str = "exact") -> dict:
    """原图归一化坐标 → 显示画布像素索引（只在最后一步按 ROUNDING_RULE 取整一次）。

    fit="exact"          ：画布即原帧分辨率（默认；1:1）
    fit="fit_no_stretch" ：画布不同时用**整数倍**等比缩放居中（k>=1），四周留黑边，绝不拉伸
    """
    if fit not in ("exact", "fit_no_stretch"):
        raise ContractViolation(f"未知 fit={fit!r}")
    if display_width <= 0 or display_height <= 0:
        raise ContractViolation("画布尺寸必须为正")
    if fit == "fit_no_stretch":
        raise ContractViolation("fit_no_stretch 需要源尺寸：请改用 original_norm_to_canvas_px")
    return {axis: round_half_up(v * (span - 1))
            for axis, v, span in (("x1", float(box[0]), display_width), ("y1", float(box[1]), display_height),
                                  ("x2", float(box[2]), display_width), ("y2", float(box[3]), display_height))}


def canvas_fit(src_width: int, src_height: int, canvas_width: int, canvas_height: int) -> dict:
    """非方形视频入不同画布：整数倍等比缩放居中（k>=1），不放缩、不拉伸。"""
    k = min(canvas_width // src_width, canvas_height // src_height)
    if k < 1:
        raise ContractViolation("画布小于源帧，整数倍等比缩放不可用；须显式声明缩放策略")
    drawn_w, drawn_h = src_width * k, src_height * k
    return {"scale_k": k, "drawn_width": drawn_w, "drawn_height": drawn_h,
            "offset_x": (canvas_width - drawn_w) // 2, "offset_y": (canvas_height - drawn_h) // 2}


def original_norm_to_canvas_px(box: Sequence[float], fit_info: Mapping[str, object]) -> dict:
    """`canvas_fit` 结果上的像素索引：先连续坐标、再一次性取整。"""
    ox, oy = int(fit_info["offset_x"]), int(fit_info["offset_y"])
    dw, dh = int(fit_info["drawn_width"]), int(fit_info["drawn_height"])
    k = int(fit_info["scale_k"])
    values = {axis: float(v) * (span - 1) * k + off
              for axis, v, span, off in (("x1", float(box[0]), dw // k, ox), ("y1", float(box[1]), dh // k, oy),
                                         ("x2", float(box[2]), dw // k, ox), ("y2", float(box[3]), dh // k, oy))}
    return {axis: round_half_up(v) for axis, v in values.items()}


def border_pixel_sets(x1: int, y1: int, x2: int, y2: int, width: int,
                      canvas_width: int, canvas_height: int) -> list[tuple[int, int]]:
    """按 LINE_WIDTH_SEMANTICS 展开边框像素（供渲染与断言共用），逐边钳到画布内。"""
    if width < 1 or width % 2 != 0:
        raise ContractViolation("line width 必须是正偶数")
    offsets = range(-(width // 2), width // 2)   # width=2 → {-1, 0}；width=4 → {-2,-1,0,1}
    xa, xb = min(x1, x2), max(x1, x2)
    ya, yb = min(y1, y2), max(y1, y2)
    pixels: set[tuple[int, int]] = set()
    for x in range(xa, xb + 1):                  # 上/下边
        for d in offsets:
            for y in (y1 + d, y2 + d):
                if 0 <= x < canvas_width and 0 <= y < canvas_height:
                    pixels.add((x, y))
    for y in range(ya, yb + 1):                  # 左/右边
        for d in offsets:
            for x in (x1 + d, x2 + d):
                if 0 <= x < canvas_width and 0 <= y < canvas_height:
                    pixels.add((x, y))
    return sorted(pixels)


def is_stale(age_ns: int | float, limit_ns: int = STALE_AGE_LIMIT_NS) -> bool:
    """过期判定：`age > limit`（与阶段4 `stale` 同源同一常量、同一单调时基）。"""
    if limit_ns <= 0:
        raise ContractViolation("stale 阈值必须为正")
    return float(age_ns) > float(limit_ns)


def compute_ages(capture_time_ns: int, result_time_ns: int, overlay_commit_ns: int) -> dict:
    """语义 B 的两个年龄，必须分别记录、分别报告。"""
    if overlay_commit_ns < result_time_ns:
        raise ContractViolation("画面提交时刻早于结果发布时刻：时间倒流，不允许")
    return {
        "age_result_ns": overlay_commit_ns - result_time_ns,
        "age_frame_ns": overlay_commit_ns - capture_time_ns,
        "display_semantics": DISPLAY_SEMANTICS,
    }


def effective_stale(stale_flag: bool, age_frame_ns: int | float,
                    limit_ns: int = STALE_AGE_LIMIT_NS) -> dict:
    """合并判定：PS 侧 `stale` 标志与显示侧 `age_frame` 超限，**每个结果只计一次**。"""
    by_flag, by_age = bool(stale_flag), is_stale(age_frame_ns, limit_ns)
    if by_flag and by_age:
        reason = STALE_REASON_BOTH
    elif by_flag:
        reason = STALE_REASON_FLAG
    elif by_age:
        reason = STALE_REASON_AGE
    else:
        reason = STALE_REASON_NONE
    return {"stale_effective": by_flag or by_age, "reason": reason,
            "stale_flag": by_flag, "age_frame_exceeds_limit": by_age,
            "limit_ns": int(limit_ns), "age_frame_ns": int(age_frame_ns)}


def validate_result_record(record: Mapping[str, object]) -> list[str]:
    """显示层消费前的契约校验；返回问题列表（空＝通过）。不读文件、不改记录。"""
    problems: list[str] = []
    if not isinstance(record, Mapping):
        return ["record 必须是对象"]
    for key, (minimum, maximum) in JOIN_KEY_FIELD_RANGES.items():
        if key not in record:
            if key not in CONSUMED_STAGE4_FIELDS:
                problems.append(f"缺少必需字段 {key}")
            continue
        value = record.get(key)
        if type(value) is not int or not minimum <= value <= maximum:
            problems.append(f"{key} 必须是 uint32 整数且位于 {minimum}..{maximum}")
    if "repeat_declared" in record and type(record.get("repeat_declared")) is not bool:
        problems.append("repeat_declared 必须是布尔值")
    for key in CONSUMED_STAGE4_FIELDS:
        if key not in record:
            problems.append(f"缺少必需字段 {key}")
    geometry = record.get("geometry")
    if isinstance(geometry, Mapping):
        for key in ("width", "height"):
            if key not in geometry:
                problems.append(f"geometry 缺少 {key}")
    detections = record.get("detections")
    if not isinstance(detections, Iterable) or isinstance(detections, (str, bytes)):
        problems.append("detections 必须是数组")
        return problems
    detections = list(detections)
    if record.get("detection_count") != len(detections):
        problems.append("detection_count 与 detections 长度不一致")
    if len(detections) > MAX_OUTPUTS_PER_IMAGE:
        problems.append(f"框数 {len(detections)} 超过冻结上限 {MAX_OUTPUTS_PER_IMAGE}")
    state = record.get("state")
    if state == "NO_HAND" and detections:
        problems.append("NO_HAND 必须为零框")
    if state not in ("OK", "NO_HAND", "TIMEOUT", "ERROR", "DROPPED"):
        problems.append(f"未知 state={state!r}")
    if state == "DROPPED" and detections:
        problems.append("DROPPED 不得携带检测框")
    for index, det in enumerate(detections):
        if not isinstance(det, Mapping):
            problems.append(f"detections[{index}] 必须是对象")
            continue
        for key in DETECTION_FIELDS:
            if key not in det:
                problems.append(f"detections[{index}] 缺少 {key}")
        class_id = det.get("class_id")
        if isinstance(class_id, int) and not 0 <= class_id < len(CLASS_ORDER):
            problems.append(f"detections[{index}].class_id 越界：{class_id}")
        elif isinstance(class_id, int) and det.get("class_name") != CLASS_ORDER[class_id]:
            problems.append(f"detections[{index}] class_name 与 class_id 不一致")
        score = det.get("score")
        if isinstance(score, (int, float)) and not 0.0 <= float(score) <= 1.0:
            problems.append(f"detections[{index}].score 必须在 [0,1]")
        xyxy = det.get("xyxy")
        if isinstance(xyxy, (list, tuple)) and len(xyxy) == 4:
            x1, y1, x2, y2 = (float(v) for v in xyxy)
            if not (x2 > x1 and y2 > y1):
                problems.append(f"detections[{index}] 上游框非正面积")
        elif xyxy is not None:
            problems.append(f"detections[{index}].xyxy 必须是 4 元数组")
    return problems
