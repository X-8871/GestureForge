#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S5-C 回归勾连检查器：阶段5 显示消费 ← 阶段4 整数结果 / 2A D9 参考。

角色：本脚本是**验证器**，不是显示实现。它给出的机器可读证据覆盖：

  C1 全 109 样本字段级一致：离散字段（frame_id / 框数 / class_id / class_name / source_order）全等；
     score 与 xyxy 各分量绝对误差 ≤1e-6；**并且**显示侧数值与阶段4 记录逐字节（float64 位型）相同。
     位型一致是显示路径「只逐字节消费、不重算/不重新格式化」的必要条件，比 1e-6 更严；
     两个门槛分别报告（Gate A = 1e-6；Gate D = 位型一致）。
  C2 不引入第二套语义：显示路径常量与 S5-A 契约 / S4-A 权威逐项一致；accepted 集合 ≡ 阶段4 框集合；
     显示路径源码禁用 token 扫描（解码 / NMS / 阈值 / 排序 / 自造补边逆式 / 自造坐标）；
     显示记录对阶段4 字段对象做**别名引用**而非复制；运行期不导入解码/NMS 模块。
  C3 几何同源交叉核对：S4-B 三条 PS 记录的 geometry_letterbox 与 letterbox_geometry(w,h,416,416) 逐值相等；
     S4-C 全部 21 种几何三方互证（冻结参考实现 / D2 冻结实现 / 本脚本独立整数复算）。
  C4 显示像素层往返：clip_unit_box → original_norm_to_display_px（画布 = 原帧分辨率）→ border_pixel_sets；
     由边框像素集反推几何中线索引、再反推归一化坐标，与阶段4 xyxy 偏差 ≤1.0 px（G0 门槛 B）；
     零面积框必须不产生边框像素（含反例探针与正对照）。
  C5 D9 参考追溯：S4-B 三条 PS 记录与 S4-C 同 sample_id 的 detections_expected 逐字段一致
     （离散全等、score/xyxy ≤1e-6 且位型相同），并把显示消费的记录钉到 S4-C → 2A T29/T25 的既有上游绑定
     与逐样本张量摘要；对不上的 sample_id 显式 SKIP 并给理由（不静默跳过）。
  C6 反例（篡改探针）：对显示侧数值制造 1 ULP / 1 单位差异，检查器必须检出并返回退出码 1；
     未篡改正对照返回退出码 0。探针证据独立保存在 <out>/tamper/，不因失败而删除。
  C7 用词与契约：消费字段名为 score；对 docs/stage5/ 与 scripts/stage5_*/ 只读扫描禁用用词
     （「置信度」「confidence」「probability」），逐处分类为禁止声明 / 显式等价声明 / 文件级策略声明 /
     无依据使用（后者为 FAIL）。

实现边界（诚实声明）：
- 所有几何/取整/裁剪/边框像素一律**导入** verification/s5_display_geometry_reference.py（见 <out>/run_manifest.json
  的 imported_modules 与 SHA256），禁止在本脚本的显示路径内复制公式。
- 本脚本内的 `independent_letterbox` 与 `expected_border_pixels` 是**校验用独立复算**（三方互证 / 边框像素
  展开一致性与像素集反推），只在检查器侧使用，不参与显示路径，也不替代冻结参考实现。
- 本脚本不做解码、不重跑 NMS、不重新推导分数；只读上游 JSON。
- 未执行项（Vivado / xsim / 硬件 / 30 分钟运行 / 真实 HDMI 截图）一律 NOT_RUN，见 summary.md。

退出码：0 = 无 FAIL（可有 SKIP / NOT_RUN，均带理由）；1 = 存在 FAIL；2 = 环境或输入错误。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import random
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

SCHEMA_VERSION = "gestureforge_s5c_stage4_regression_v1"
TASK_ID = "S5-C"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

DEFAULT_GOLDEN = pathlib.Path(
    r"D:\codex-worktrees\w4\report\evidence\S4-C\s4c_replay_20261021_r05\replay_golden_109.json"
)
DEFAULT_S4B_DIR = pathlib.Path(r"D:\codex-worktrees\w4\report\evidence\S4-B\20261021_r13")
DEFAULT_T29 = pathlib.Path(r"D:\FPGA_Competition\report\evidence\S2A-T29\cpu_decode_nms_reference.json")

REF_PATH = REPO_ROOT / "verification" / "s5_display_geometry_reference.py"
D2_PATH = REPO_ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
CONTRACT_PATH = REPO_ROOT / "docs" / "stage5" / "s5a_stage5_display_g0_fields.json"
S4A_PATH = REPO_ROOT / "docs" / "stage4" / "s4a_stage4_g0_fields.json"

GATE_A_SCORE_TOL = 1e-06
GATE_A_XYXY_TOL = 1e-06
GATE_B_PIXEL_TOL = 1.0
GATE_D_ROLE = ("ADDITIONAL_INTERFACE_EVIDENCE（附加接口证据）：要求显示层逐字节消费阶段4 数值，"
               "不得替代或放宽契约门槛 Gate A（score/xyxy ≤1e-6）与 Gate B（像素往返 ≤1.0 px）；"
               "三项门槛在报告中分列")

# ── 证据保留事故（如实登记，不美化）────────────────────────────────────────
# 背景：Developer 在 report/evidence/S5-C/ 下删除了 r01（驱动脚本 JSON 写出 bug 导致同轮 finalize 中止）
# 与 r02（措辞修正前的完整 PASS 运行，被 r03 取代）两轮**中间运行**目录（含各自 _limit8 抽样目录）。
# 按 AGENTS.md「不得以节省空间为由删除原始失败证据」与本项目 RunId 口径，失败/中间运行目录应保留。
# 已删除内容不可恢复；本字段如实留痕，供 Reviewer 与项目总控核查；后续运行一律保留、不删除。
EVIDENCE_RETENTION_INCIDENT = {
    "deleted_runs": [
        "s5c_regression_20261021_r01",
        "s5c_regression_20261021_r02",
    ],
    "deleted_dirs": [
        "report/evidence/S5-C/s5c_regression_20261021_r01",
        "report/evidence/S5-C/s5c_regression_20261021_r01_limit8",
        "report/evidence/S5-C/s5c_regression_20261021_r02",
        "report/evidence/S5-C/s5c_regression_20261021_r02_limit8",
    ],
    "reason_claimed": ("r01：驱动脚本 run_s5c_evidence.ps1 的 JSON 写出 bug（有序哈希写入 List 失败）"
                       "导致该轮 finalize 与 observed_exit_codes.json 不完整；"
                       "r02：limitation 措辞修正前的完整 PASS 运行，被 r03 取代"),
    "policy": "AGENTS.md 要求保留失败与中间证据（不得以节省空间为由删除）；本次删除属口径违规",
    "recoverable": False,
    "corrective_action": ("后续运行一律保留、不删除；保留运行含 r03、r03_limit8 及本轮起的全部 RunId "
                          "与 _limit* 抽样运行；探针证据不因失败而删除"),
    "retained_runs_at_disclosure": [
        "s5c_regression_20261021_r03",
        "s5c_regression_20261021_r03_limit8",
    ],
    "disclosed_by": "dev-s5c（Developer，S5-C）",
    "authority": "Lead 2026-10-21 通知：要求在新 RunId 的 summary/manifest 与 console 原始文件中显式披露",
    "note": "本字段不构成对删除行为的正当化；删除内容无法恢复，登记即为如实留痕",
}

S4B_SAMPLE_IDS = ("test_one_056", "test_palm_036", "approved_no_hand_001")
S4B_GEOM_KEYS = (
    ("new_width", "resized_width"),
    ("new_height", "resized_height"),
    ("offset_x", "pad_left"),
    ("offset_y", "pad_top"),
)

PROBE_REQUIRED = ("score_ulp", "xyxy_ulp", "source_order", "box_count")
PROBE_KINDS = (
    "score_ulp",
    "score_tol",
    "xyxy_ulp",
    "xyxy_tol",
    "source_order",
    "frame_id",
    "box_count",
    "identity_rebuild",
)

# 禁用用词（S5-A 契约 scoring.forbidden_without_basis）；本行是策略声明，不是使用。
FORBIDDEN_WORDS = ("\u7f6e\u4fe1\u5ea6", "confidence", "probability")
EQUIVALENCE_MARKERS = ("\u2261", "\u7b49\u4ef7", "equivalent", "display_word")
PROHIBITION_MARKERS = (
    "\u7981\u6b62", "\u4e0d\u5f97", "\u7981\u7528", "\u56de\u9000", "\u65e0\u4f9d\u636e",
    "\u624d\u79f0", "\u7528\u8bcd", "\u4e0d\u8868\u793a\u53ef\u9760\u6982\u7387",
    "forbidden", "prohibit", "without_basis",
)
SCAN_SKIP_SUFFIX = (".png", ".jpg", ".jpeg", ".pyc", ".zip", ".bin", ".raw", ".gz", ".zlib")
SCAN_MAX_BYTES = 5 * 1024 * 1024

DISPLAY_PATH_BEGIN = "# ==== S5C DISPLAY PATH BEGIN ===="
DISPLAY_PATH_END = "# ==== S5C DISPLAY PATH END ===="
DISPLAY_PATH_FORBIDDEN_TOKENS = (
    "nms", "decode", "sigmoid", "iou", "threshold", "argmax", "sort(",
    "letterbox", "network_norm", "original_norm_to_network_norm", "confidence",
)

NOT_RUN_ITEMS = [
    {"id": "U5-05", "item": "真实 HDMI/摄像头联调、上板、30 分钟运行、截图/视频", "status": "NOT_RUN",
     "reason": "阶段3 颜色验收受阻（硬件）+ 阶段4 未联调 + 2B 未让出硬件；本轮为纯离线"},
    {"id": "T5-09", "item": "连续 30 分钟无死锁", "status": "NOT_RUN", "reason": "需要实板与完整链路"},
    {"id": "T5-08", "item": "FPS/延迟真实统计", "status": "NOT_RUN", "reason": "离线无 PS 单调时基与帧级事件日志"},
    {"id": "G3", "item": "实物验证", "status": "NOT_RUN", "reason": "本轮无板卡/HDMI/摄像头操作"},
    {"id": "T5-01/T5-02/T5-03/T5-04/T5-07", "item": "离线渲染用例（PNG/叠框/零面积绘制/非方形画布/过期清除）",
     "status": "NOT_APPLICABLE_THIS_TASK",
     "reason": "属 S5-B 交付范围（scripts/stage5_s5b/**、report/evidence/S5-B/**）；本任务只做数值链路勾连与像素索引级往返，不重复渲染出图"},
]

TEST_CASE_COVERAGE = [
    {"case": "T5-10", "requirement": "回归阶段4 数值链路：沿用 2A 容限、离散字段全等、可追溯到阶段4 整数结果与 D9 参考",
     "covered_by": ["C1", "C2", "C4", "C5"], "status": "OFFLINE_CHAIN_ASSERTED"},
    {"case": "T5-06", "requirement": "分数/置信度用词：字段名为 score、无依据时不出现禁用用词",
     "covered_by": ["C7"], "status": "OFFLINE_TEXT_SCANNED_AND_FIELD_CHECKED"},
    {"case": "T5-05", "requirement": "结果—帧号对应（≥100 帧）",
     "covered_by": ["C1"], "status": "PARTIAL_OFFLINE",
     "note": "本任务逐样本核对 109 条 frame_id 与阶段4 记录一致；五元组日志/年龄口径属 S5-B 与阶段5 正式运行"},
    {"case": "T5-01/T5-02/T5-03/T5-04/T5-07", "requirement": "非方形/边缘框/多框零框/过期清除/奇数补边渲染",
     "covered_by": ["C3", "C4"], "status": "PARTIAL_OFFLINE",
     "note": "几何与像素索引级断言在本任务内完成（C3/C4）；出图渲染与过期清除 HUD 属 S5-B"},
    {"case": "T5-08/T5-09/T5-11/T5-12", "requirement": "FPS/延迟统计、30 分钟无死锁、预热丢帧超时、显示语义一致性",
     "covered_by": [], "status": "NOT_RUN", "note": "需实板/完整链路或属 S5-B 序列用例"},
]


# ────────────────────────────── 通用工具 ──────────────────────────────

class InputError(RuntimeError):
    """输入或环境错误（退出码 2）。"""


class RunLog:
    """控制台与文件双写日志（UTF-8）。"""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def __call__(self, message: str = "") -> None:
        line = str(message)
        self.lines.append(line)
        try:
            print(line)
        except UnicodeEncodeError:  # 极少数控制台代码页
            print(line.encode("utf-8", "replace").decode("ascii", "replace"))

    def text(self) -> str:
        return "\n".join(self.lines) + "\n"


def utc8_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_module_from_path(path: pathlib.Path, name: str):
    if not path.is_file():
        raise InputError(f"找不到必需模块：{path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise InputError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: pathlib.Path):
    if not path.is_file():
        raise InputError(f"找不到必需输入：{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"JSON 解析失败：{path}（{exc}）") from exc


def f64_bits(value) -> str:
    """float64 位型（hex），用于「逐字节消费」判定。"""
    return struct.pack("<d", float(value)).hex()


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: pathlib.Path, obj) -> None:
    write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def git_info() -> dict:
    def run(args):
        try:
            out = subprocess.run(args, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
            return out.returncode, out.stdout.strip()
        except Exception as exc:  # 只读探测失败不影响检查
            return None, f"<{exc}>"

    head_code, head = run(["git", "rev-parse", "HEAD"])
    branch_code, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    status_code, status = run(["git", "status", "--short"])
    return {
        "worktree": str(REPO_ROOT),
        "git_head": head if head_code == 0 else None,
        "git_head_probe_code": head_code,
        "git_branch": branch if branch_code == 0 else None,
        "git_status_short": status.splitlines() if status_code == 0 else [],
        "git_status_probe_code": status_code,
        "note": "只读探测；本任务不做 git add/commit（由 Lead 统一提交）",
    }


# ──────────────────── 校验用独立复算（非显示路径） ────────────────────

def independent_letterbox(src_w: int, src_h: int, dst_w: int = 416, dst_h: int = 416) -> dict:
    """校验用独立整数复算：用纯整数比较代替浮点除法，与冻结公式等价。

    仅用于三方互证（本复算 / 冻结参考实现 / D2 冻结实现）；显示路径不使用本函数。
    """
    if src_w <= 0 or src_h <= 0 or dst_w <= 0 or dst_h <= 0:
        raise ValueError("尺寸必须为正整数")
    if dst_w * src_h < dst_h * src_w:            # 等价于 dst_w/src_w < dst_h/src_h（正整数）
        new_w, new_h = dst_w, (src_h * dst_w) // src_w
    else:
        new_w, new_h = (src_w * dst_h) // src_h, dst_h
    return {
        "new_width": new_w,
        "new_height": new_h,
        "offset_x": (dst_w - new_w) // 2,
        "offset_y": (dst_h - new_h) // 2,
        "pad_right": dst_w - new_w - (dst_w - new_w) // 2,
        "pad_bottom": dst_h - new_h - (dst_h - new_h) // 2,
        "asymmetric_padding": ((dst_w - new_w) % 2 == 1) or ((dst_h - new_h) % 2 == 1),
    }


def expected_border_pixels(x1: int, y1: int, x2: int, y2: int, width: int,
                           canvas_w: int, canvas_h: int) -> list[tuple[int, int]]:
    """校验用独立复算：偶数线宽居中的边框像素展开（与 G0 LINE_WIDTH_SEMANTICS 同语义）。

    仅用于「边框像素一致性」与「由像素集反推中线索引」；显示路径使用冻结实现 border_pixel_sets。
    """
    half = width // 2
    xa, xb = min(x1, x2), max(x1, x2)
    ya, yb = min(y1, y2), max(y1, y2)
    pixels: set[tuple[int, int]] = set()
    for x in range(xa, xb + 1):
        for d in range(-half, half):
            for y in (y1 + d, y2 + d):
                if 0 <= x < canvas_w and 0 <= y < canvas_h:
                    pixels.add((x, y))
    for y in range(ya, yb + 1):
        for d in range(-half, half):
            for x in (x1 + d, x2 + d):
                if 0 <= x < canvas_w and 0 <= y < canvas_h:
                    pixels.add((x, y))
    return sorted(pixels)


def pixels_digest(pixels) -> str:
    return sha256_text(json.dumps([list(p) for p in pixels]))


def recover_center_indices(px: dict, observed: set, canvas_w: int, canvas_h: int, width: int) -> dict:
    """由边框像素集反推几何中线索引（逆问题搜索，只用独立展开语义，不用 px 自身）。"""
    if not observed:
        return {"status": "no_solution", "solutions": [], "reason": "像素集为空"}
    cols = [p[0] for p in observed]
    rows = [p[1] for p in observed]
    min_col, max_col = min(cols), max(cols)
    min_row, max_row = min(rows), max(rows)

    def clamp(values, upper):
        return sorted({v for v in values if 0 <= v <= upper})

    x1c = clamp((min_col, min_col + 1), canvas_w - 1)
    x2c = clamp((max_col - 1, max_col), canvas_w - 1)
    y1c = clamp((min_row, min_row + 1), canvas_h - 1)
    y2c = clamp((max_row - 1, max_row), canvas_h - 1)
    solutions = []
    for x1 in x1c:
        for x2 in x2c:
            if x2 < x1:
                continue
            for y1 in y1c:
                for y2 in y2c:
                    if y2 < y1:
                        continue
                    if set(expected_border_pixels(x1, y1, x2, y2, width, canvas_w, canvas_h)) == observed:
                        solutions.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
    status = "unique" if len(solutions) == 1 else ("non_unique" if solutions else "no_solution")
    return {"status": status, "solutions": solutions,
            "reason": None if solutions else "观察到的像素集与任何中线索引组合都不一致"}


# ==== S5C DISPLAY PATH BEGIN ====
# 被测显示消费路径：只做字段投影与像素化；不做解码/NMS/阈值筛选/排序/自造坐标。
class DisplayConsumer:
    """显示层消费者：逐字段直接取用阶段4 记录对象（别名，不复制、不重算数值）。"""

    def __init__(self, ref) -> None:
        self._ref = ref

    def consume(self, stage4_record: dict) -> dict:
        """构造显示可消费记录：字段对象直接引用，不做数值变换。"""
        return {key: stage4_record[key] for key in self._ref.CONSUMED_STAGE4_FIELDS}

    def boxes(self, display_record: dict) -> list:
        """显示层接受的框：原样返回阶段4 detections（不筛选、不重排、不复制）。"""
        return display_record["detections"]

    def draw_box(self, detection: dict, canvas_w: int, canvas_h: int, index: int) -> dict:
        """单个框的显示绘制路径：裁剪 → 原帧画布像素索引 → 边框像素（零面积不绘制）。"""
        clip = self._ref.clip_unit_box(detection["xyxy"])
        if clip["zero_area"]:
            return {"index": index, "clipped": clip["clipped"], "zero_area": True,
                    "unit_xyxy": clip["xyxy"], "px_geom": None, "pixels": []}
        px = self._ref.original_norm_to_display_px(clip["xyxy"], canvas_w, canvas_h)
        pixels = self._ref.border_pixel_sets(
            px["x1"], px["y1"], px["x2"], px["y2"], self._ref.DISPLAY_LINE_WIDTH_PX, canvas_w, canvas_h
        )
        return {"index": index, "clipped": clip["clipped"], "zero_area": False,
                "unit_xyxy": clip["xyxy"], "px_geom": px, "pixels": pixels}

    def draw_record(self, display_record: dict) -> list:
        """整条记录的绘制：画布即原帧分辨率（G0 fit='exact'）。"""
        canvas_w = int(display_record["geometry"]["width"])
        canvas_h = int(display_record["geometry"]["height"])
        return [self.draw_box(det, canvas_w, canvas_h, i)
                for i, det in enumerate(display_record["detections"])]
# ==== S5C DISPLAY PATH END ====


def display_path_source() -> str:
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    begin = source.index(DISPLAY_PATH_BEGIN) + len(DISPLAY_PATH_BEGIN)
    end = source.index(DISPLAY_PATH_END)
    return source[begin:end]


class TamperHarness:
    """反例探针工具（不属于显示路径）：重建显示侧记录后施加最小篡改。"""

    def __init__(self, ref) -> None:
        self._ref = ref

    def consume_rebuilt(self, stage4_record: dict) -> dict:
        """模拟「显示层自己重建了数值」：检测框做浅拷贝（值相同但不再是阶段4 对象）。"""
        record = {key: stage4_record[key] for key in self._ref.CONSUMED_STAGE4_FIELDS}
        record["detections"] = [dict(det) for det in stage4_record["detections"]]
        for det in record["detections"]:
            det["xyxy"] = list(det["xyxy"])
        return record


def authority_snapshot(samples) -> str:
    payload = [
        {"sample_id": s["sample_id"], "frame_id": s["frame_id"],
         "geometry_wh": list(s["geometry_wh"]), "detections": s["detections_expected"]}
        for s in samples
    ]
    return sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True))


# ──────────────────────────── 输入准备 ────────────────────────────

def build_context(args, log: RunLog) -> dict:
    golden_path = pathlib.Path(args.golden)
    s4b_dir = pathlib.Path(args.s4b_dir)
    log(f"[输入] 黄金对拍输入 {golden_path}")
    golden = load_json(golden_path)
    golden_sha = sha256_file(golden_path)

    s4b = {}
    for sample_id in S4B_SAMPLE_IDS:
        path = s4b_dir / f"host_result_{sample_id}.json"
        record = load_json(path)
        s4b[sample_id] = {"path": str(path), "sha256": sha256_file(path), "record": record}
        log(f"[输入] S4-B PS 记录 {sample_id} {path}")

    contract = load_json(CONTRACT_PATH)
    s4a = load_json(S4A_PATH)
    ref = load_module_from_path(REF_PATH, "s5_display_geometry_reference")
    d2 = load_module_from_path(D2_PATH, "s1_t02_d2_numeric_reference")

    t29 = {"path": str(DEFAULT_T29), "exists": DEFAULT_T29.is_file(), "sha256": None,
           "expected_sha256_from_s4c": None, "match": None, "bytes": None}
    if t29["exists"]:
        t29["sha256"] = sha256_file(DEFAULT_T29)
        t29["bytes"] = DEFAULT_T29.stat().st_size

    return {
        "golden": golden,
        "golden_path": str(golden_path),
        "golden_sha256": golden_sha,
        "s4b": s4b,
        "contract": contract,
        "contract_path": str(CONTRACT_PATH),
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "s4a": s4a,
        "s4a_path": str(S4A_PATH),
        "s4a_sha256": sha256_file(S4A_PATH),
        "ref": ref,
        "ref_path": str(REF_PATH),
        "ref_sha256": sha256_file(REF_PATH),
        "d2": d2,
        "d2_path": str(D2_PATH),
        "d2_sha256": sha256_file(D2_PATH),
        "t29": t29,
    }


def select_samples(golden: dict, limit, seed, log: RunLog):
    samples = golden["samples"]
    ids = [s["sample_id"] for s in samples]
    if limit is None or limit >= len(samples):
        selection = {
            "rule": "full_all_samples", "available": len(samples), "selected": len(samples),
            "limit": None, "seed": None, "seed_source": "not_used_full_selection",
            "sample_ids": ids,
        }
        return list(samples), selection
    if limit <= 0:
        raise InputError("--limit 必须为正整数")
    seed_used = 20261021 if seed is None else int(seed)
    rng = random.Random(seed_used)
    picked = sorted(rng.sample(range(len(samples)), limit))
    selection = {
        "rule": "seeded_random_subset", "available": len(samples), "selected": len(picked),
        "limit": limit, "seed": seed_used,
        "seed_source": "default_20261021" if seed is None else "cli",
        "sample_ids": [ids[i] for i in picked],
    }
    log(f"[抽样] rule=seeded_random_subset limit={limit} seed={seed_used} 选中 {len(picked)} 样本")
    return [samples[i] for i in picked], selection


def golden_to_stage4_record(sample: dict) -> dict:
    """S4-C 黄金样本 → S4-A 契约的「阶段4 结果记录」（方案 B：PS 侧记录形态）。

    detections 保持阶段4 侧对象引用（不复制），供显示消费别名判定。
    """
    width, height = sample["geometry_wh"]
    detections = sample["detections_expected"]
    state = "OK" if detections else "NO_HAND"
    return {
        "frame_id": sample["frame_id"],
        "result_seq": int(sample["position"]),
        "geometry": {"width": int(width), "height": int(height)},
        "state": state,
        "detection_count": int(sample["detection_count_expected"]),
        "detections": detections,
        "candidate_count": sample.get("raw_candidate_count_before_stable_nms"),
        "capture_time_ns": 0,
        "result_time_ns": 0,
        "inference_time_ns": 0,
        "end_to_end_latency_ns": 0,
        "dropped_frames": 0,
        "stale": False,
        "error_code": 0,
        "measurement_scope": {
            "pl_timing": "NOT_EXECUTED_OFFLINE",
            "uart_transport": "NOT_EXECUTED_OFFLINE",
            "board_pl": "NOT_EXECUTED_OFFLINE",
            "unavailable_fields": ["capture_time_ns", "result_time_ns",
                                   "inference_time_ns", "end_to_end_latency_ns"],
            "note": "S4-C 只读回放证据；时间字段为 0 哨兵，不是实测耗时",
        },
        "record_origin": {"kind": "S4-C replay_golden_109", "sample_id": sample["sample_id"],
                          "position": sample["position"], "state_derivation":
                          "state 由 detections_expected 长度派生（非零 => OK，零框 => NO_HAND），"
                          "与 S4-A state_enum 一致；S4-C 样本本身不含显式 state 字段"},
    }


# ──────────────────────────── C1 字段一致性 ────────────────────────────

def check_c1(ref, entries, identity_enforced: bool, log: RunLog) -> dict:
    per_sample, per_box, mismatches, alias_violations = [], [], [], []
    validate_problems = []
    field_values_compared = 0
    max_score_err = 0.0
    max_xyxy_err = 0.0
    authority_max_score = 0.0

    for sample, stage4_record, display_record in entries:
        expected = sample["detections_expected"]
        shown = display_record["detections"]
        sample_id = sample["sample_id"]

        problems = ref.validate_result_record(display_record)
        if problems:
            validate_problems.append({"sample_id": sample_id, "problems": problems})

        identity_ok = display_record["detections"] is stage4_record["detections"] and all(
            a is b for a, b in zip(display_record["detections"], stage4_record["detections"])
        )
        if not identity_ok:
            alias_violations.append({
                "sample_id": sample_id, "kind": "detections_not_aliased",
                "detail": "显示记录的 detections 不是阶段4 记录对象的别名（显示层重建了数值对象）",
            })

        sample_mismatches = []
        if sample["frame_id"] != display_record["frame_id"]:
            sample_mismatches.append(_mismatch(sample_id, None, "frame_id", "discrete",
                                               sample["frame_id"], display_record["frame_id"], None))
        field_values_compared += 1
        if sample["detection_count_expected"] != display_record["detection_count"]:
            sample_mismatches.append(_mismatch(sample_id, None, "detection_count", "discrete",
                                               sample["detection_count_expected"],
                                               display_record["detection_count"], None))
        field_values_compared += 1
        if len(expected) != len(shown):
            sample_mismatches.append(_mismatch(sample_id, None, "box_count", "discrete",
                                               len(expected), len(shown), None))
            identity_ok = False
        else:
            field_values_compared += 1

        box_rows = []
        sample_max_score = 0.0
        sample_max_xyxy = 0.0
        for index, expected_det in enumerate(expected):
            if index >= len(shown):
                break
            shown_det = shown[index]
            box_mismatches = []
            for field in ("class_id", "class_name", "source_order"):
                field_values_compared += 1
                if expected_det[field] != shown_det[field]:
                    box_mismatches.append(_mismatch(sample_id, index, field, "discrete",
                                                    expected_det[field], shown_det[field], None))
            field_values_compared += 1
            score_err = abs(float(expected_det["score"]) - float(shown_det["score"]))
            score_bit_ok = f64_bits(expected_det["score"]) == f64_bits(shown_det["score"])
            sample_max_score = max(sample_max_score, score_err)
            authority_max_score = max(authority_max_score, float(expected_det["score"]))
            if score_err > GATE_A_SCORE_TOL:
                box_mismatches.append(_mismatch(sample_id, index, "score", "A",
                                                expected_det["score"], shown_det["score"], score_err))
            if not score_bit_ok:
                box_mismatches.append(_mismatch(sample_id, index, "score", "D",
                                                f64_bits(expected_det["score"]),
                                                f64_bits(shown_det["score"]), score_err))

            comp_errs, comp_bit_ok = [], True
            for comp_index in range(4):
                field_values_compared += 1
                expected_value = expected_det["xyxy"][comp_index]
                shown_value = shown_det["xyxy"][comp_index]
                err = abs(float(expected_value) - float(shown_value))
                comp_errs.append(err)
                if err > GATE_A_XYXY_TOL:
                    box_mismatches.append(_mismatch(
                        sample_id, index, f"xyxy[{comp_index}]", "A", expected_value, shown_value, err))
                if f64_bits(expected_value) != f64_bits(shown_value):
                    comp_bit_ok = False
                    box_mismatches.append(_mismatch(
                        sample_id, index, f"xyxy[{comp_index}]", "D",
                        f64_bits(expected_value), f64_bits(shown_value), err))
            xyxy_err = max(comp_errs) if comp_errs else 0.0
            sample_max_xyxy = max(sample_max_xyxy, xyxy_err)
            box_rows.append({
                "sample_id": sample_id, "box_index": index,
                "class_id": expected_det["class_id"], "class_name": expected_det["class_name"],
                "source_order": expected_det["source_order"],
                "score_expected": expected_det["score"], "score_display": shown_det["score"],
                "score_abs_error": score_err, "score_bit_identical": score_bit_ok,
                "xyxy_expected": list(expected_det["xyxy"]), "xyxy_display": list(shown_det["xyxy"]),
                "xyxy_max_abs_error": xyxy_err, "xyxy_bit_identical": comp_bit_ok,
                "status": "PASS" if not box_mismatches else "FAIL",
            })
            sample_mismatches.extend(box_mismatches)

        per_box.extend(box_rows)
        mismatches.extend(sample_mismatches)
        max_score_err = max(max_score_err, sample_max_score)
        max_xyxy_err = max(max_xyxy_err, sample_max_xyxy)
        per_sample.append({
            "sample_id": sample_id, "position": sample["position"], "frame_id": sample["frame_id"],
            "geometry_wh": list(sample["geometry_wh"]), "state": stage4_record["state"],
            "boxes_expected": len(expected), "boxes_display": len(shown),
            "detection_count_expected": sample["detection_count_expected"],
            "identity_ok": identity_ok,
            "max_score_abs_error": sample_max_score, "max_xyxy_abs_error": sample_max_xyxy,
            "mismatch_count": len(sample_mismatches), "validate_problems": problems,
            "status": "PASS" if (not sample_mismatches and identity_ok) else "FAIL",
        })

    alias_ok_all = not alias_violations
    bit_identity_violation_count = sum(1 for item in mismatches if item["gate"] == "D")
    status = "PASS"
    if mismatches or validate_problems:
        status = "FAIL"
    if identity_enforced and not alias_ok_all:
        status = "FAIL"
    log(f"[C1] 样本 {len(per_sample)}，框 {len(per_box)}，字段值比较 {field_values_compared}，"
        f"mismatch {len(mismatches)}（其中位型 Gate D {bit_identity_violation_count}），"
        f"别名违规 {len(alias_violations)}，"
        f"最大 score 误差 {max_score_err:.3e}，最大坐标误差 {max_xyxy_err:.3e} → {status}")
    return {
        "status": status,
        "identity_enforced": identity_enforced,
        "identity_note": ("显示记录必须对阶段4 字段对象做别名引用；"
                          "篡改探针模式下显示侧刻意重建对象，故不据此判 FAIL（另见 C6）"
                          if not identity_enforced else "别名引用为硬性判定项"),
        "samples": len(per_sample), "boxes": len(per_box),
        "field_values_compared": field_values_compared,
        "max_score_abs_error": max_score_err, "max_xyxy_abs_error": max_xyxy_err,
        "max_authority_score": authority_max_score,
        "mismatch_count": len(mismatches), "mismatches": mismatches[:200],
        "mismatch_truncated": len(mismatches) > 200,
        "bit_identity_violation_count": bit_identity_violation_count,
        "alias_violations": alias_violations[:50],
        "validate_problems": validate_problems[:20],
        "per_sample": per_sample, "per_box": per_box,
    }


def _mismatch(sample_id, box_index, field, gate, expected, actual, abs_error) -> dict:
    return {"sample_id": sample_id, "box_index": box_index, "field": field, "gate": gate,
            "expected": expected, "actual": actual, "abs_error": abs_error}


# ──────────────────── C2 不引入第二套语义 ────────────────────

def check_c2(ref, ctx, selection, entries, consumer, log: RunLog) -> dict:
    contract = ctx["contract"]
    s4a = ctx["s4a"]
    scoring = contract["scoring"]
    frozen = s4a["frozen_2a_constants"]
    consumed = contract["consumed_stage4_record"]

    constants = {
        "CLASS_ORDER": {
            "value": list(ref.CLASS_ORDER),
            "contract": scoring["class_order"], "s4a": frozen["classes"],
            "match": list(ref.CLASS_ORDER) == list(scoring["class_order"]) == list(frozen["classes"]),
        },
        "SCORE_THRESHOLD": {
            "value": ref.SCORE_THRESHOLD, "contract": scoring["score_threshold"],
            "s4a": frozen["score_threshold"],
            "match": ref.SCORE_THRESHOLD == scoring["score_threshold"] == frozen["score_threshold"],
        },
        "NMS_IOU": {
            "value": ref.NMS_IOU, "contract": scoring["nms_iou"], "s4a": frozen["nms_iou"],
            "match": ref.NMS_IOU == scoring["nms_iou"] == frozen["nms_iou"],
        },
        "MAX_OUTPUTS_PER_IMAGE": {
            "value": ref.MAX_OUTPUTS_PER_IMAGE, "contract": scoring["max_outputs_per_image"],
            "s4a": frozen["max_outputs_per_image"],
            "match": ref.MAX_OUTPUTS_PER_IMAGE == scoring["max_outputs_per_image"]
            == frozen["max_outputs_per_image"],
        },
        "NETWORK_INPUT": {
            "value": [ref.NETWORK_INPUT_W, ref.NETWORK_INPUT_H],
            "contract": [contract["geometry"]["network_input"]["width"],
                         contract["geometry"]["network_input"]["height"]],
            "s4a": frozen["network_input_wh"],
            "match": [ref.NETWORK_INPUT_W, ref.NETWORK_INPUT_H]
            == [contract["geometry"]["network_input"]["width"], contract["geometry"]["network_input"]["height"]]
            == list(frozen["network_input_wh"]),
        },
        "STALE_AGE_LIMIT_NS": {
            "value": ref.STALE_AGE_LIMIT_NS, "contract": contract["stale_and_age"]["stale_age_limit_ns"],
            "s4a": s4a["draft_proposed_thresholds"]["stale_age_limit_ms"] * 1_000_000,
            "match": ref.STALE_AGE_LIMIT_NS == contract["stale_and_age"]["stale_age_limit_ns"]
            == s4a["draft_proposed_thresholds"]["stale_age_limit_ms"] * 1_000_000,
            "note": "阶段4 侧仍 DRAFT_PROPOSED；此处只做同源一致性核对",
        },
        "ROUNDING_RULE_ID": {
            "value": ref.ROUNDING_RULE, "contract": contract["geometry"]["rounding_rule_id"],
            "s4a": None,
            "match": ref.ROUNDING_RULE == contract["geometry"]["rounding_rule_id"],
        },
        "DETECTION_FIELDS": {
            "value": list(ref.DETECTION_FIELDS), "contract": consumed["detection_fields"],
            "s4a": [f["name"] for f in s4a["detection_record"]["fields"] if f.get("required")],
            "match": list(ref.DETECTION_FIELDS) == list(consumed["detection_fields"])
            and set(ref.DETECTION_FIELDS).issubset({f["name"] for f in s4a["detection_record"]["fields"]}),
        },
        "CONSUMED_STAGE4_FIELDS": {
            "value": list(ref.CONSUMED_STAGE4_FIELDS), "contract": consumed["required_fields"],
            "s4a": [f["name"] for f in s4a["result_record"]["fields"] if f.get("required")],
            "match": list(ref.CONSUMED_STAGE4_FIELDS) == list(consumed["required_fields"]),
        },
    }
    constants_match = all(item["match"] for item in constants.values())

    # 阈值与上限：显示路径不筛选，故 accepted 集合必须与阶段4 框集合完全相同
    accepted_equals_stage4 = True
    min_accepted_score = 1.0
    max_box_count = 0
    threshold_violations = []
    count_over_limit = []
    for sample, stage4_record, display_record in entries:
        accepted = consumer.boxes(display_record)
        if len(accepted) != len(stage4_record["detections"]):
            accepted_equals_stage4 = False
        if not all(a is b for a, b in zip(accepted, stage4_record["detections"])):
            accepted_equals_stage4 = False
        max_box_count = max(max_box_count, len(accepted))
        if len(accepted) > ref.MAX_OUTPUTS_PER_IMAGE:
            count_over_limit.append({"sample_id": sample["sample_id"], "boxes": len(accepted)})
        for index, det in enumerate(accepted):
            score = float(det["score"])
            min_accepted_score = min(min_accepted_score, score)
            if not score >= ref.SCORE_THRESHOLD:
                threshold_violations.append({"sample_id": sample["sample_id"], "box_index": index,
                                             "score": score})
    if not entries:
        min_accepted_score = 0.0

    source = display_path_source()
    token_hits = []
    lowered = source.lower()
    for token in DISPLAY_PATH_FORBIDDEN_TOKENS:
        if token.lower() in lowered:
            token_hits.append(token)

    loaded_suspects = []
    for name, module in list(sys.modules.items()):
        file_path = getattr(module, "__file__", None)
        if not file_path:
            continue
        try:
            inside = pathlib.Path(file_path).resolve().is_relative_to(REPO_ROOT)
        except (OSError, ValueError):
            inside = False
        if inside and re.search(r"decode|nms", name, re.IGNORECASE):
            loaded_suspects.append({"module": name, "file": file_path})

    checks = {
        "constants_match_contract_and_s4a": constants_match,
        "accepted_set_equals_stage4_boxes": accepted_equals_stage4,
        "no_score_below_threshold_in_accepted": not threshold_violations,
        "box_count_within_frozen_limit": not count_over_limit,
        "display_path_forbidden_tokens_absent": not token_hits,
        "no_decoder_or_nms_module_loaded": not loaded_suspects,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    log(f"[C2] 常量一致={constants_match} accepted≡阶段4={accepted_equals_stage4} "
        f"禁用 token 命中={token_hits} 解码/NMS 模块={len(loaded_suspects)} → {status}")
    return {
        "status": status,
        "checks": checks,
        "constants": constants,
        "min_accepted_score": min_accepted_score,
        "max_box_count": max_box_count,
        "threshold_violations": threshold_violations[:20],
        "count_over_limit": count_over_limit[:20],
        "display_path_source_sha256": sha256_text(source),
        "display_path_forbidden_tokens_hit": token_hits,
        "display_path_forbidden_tokens_scanned": list(DISPLAY_PATH_FORBIDDEN_TOKENS),
        "loaded_suspect_modules": loaded_suspects,
        "no_second_semantics_statement": (
            "显示路径只消费 S4-A consumed_stage4_record 的字段对象；score/xyxy 逐字节相同（C1 Gate D）；"
            "阈值/上限/类别顺序与 2A 冻结常量同一来源；显示路径源码不含解码/NMS/阈值/排序/自造补边逆式 token；"
            "运行期未导入解码或 NMS 模块。"),
    }


# ──────────────────── C3 几何同源交叉核对 ────────────────────

def check_c3(ctx, golden, log: RunLog) -> dict:
    ref, d2 = ctx["ref"], ctx["d2"]
    s4b_rows = []
    s4b_ok = True
    for sample_id, item in ctx["s4b"].items():
        record = item["record"]
        width = int(record["geometry"]["width"])
        height = int(record["geometry"]["height"])
        letterbox = record["geometry_letterbox"]
        geom = ref.letterbox_geometry(width, height, 416, 416)
        d2_geom = d2.letterbox_geometry(width, height, 416, 416)
        indep = independent_letterbox(width, height, 416, 416)
        comparisons = []
        row_ok = True
        for ref_key, rec_key in S4B_GEOM_KEYS:
            value = geom[ref_key]
            recorded = letterbox[rec_key]
            d2_value = d2_geom[ref_key]
            indep_value = indep[ref_key]
            match = value == recorded == d2_value == indep_value
            row_ok = row_ok and match
            comparisons.append({"key": ref_key, "recorded": recorded, "reference": value,
                                "d2_reference": d2_value, "independent": indep_value, "match": match})
        s4b_rows.append({
            "sample_id": sample_id, "path": item["path"], "sha256": item["sha256"],
            "geometry_wh": [width, height], "recorded": letterbox, "computed": geom,
            "comparisons": comparisons, "status": "PASS" if row_ok else "FAIL",
            "padding_symmetry": {"pad_right": geom["pad_right"], "pad_bottom": geom["pad_bottom"],
                                 "asymmetric": geom["asymmetric_padding"]},
        })
        s4b_ok = s4b_ok and row_ok
        log(f"[C3] S4-B {sample_id} {width}x{height} → new=({geom['new_width']},{geom['new_height']}) "
            f"off=({geom['offset_x']},{geom['offset_y']}) 与记录一致={row_ok}")

    geometries = []
    for sample in golden["samples"]:
        key = tuple(int(v) for v in sample["geometry_wh"])
        if key not in geometries:
            geometries.append(key)
    geometries.sort()
    geometry_rows = []
    all_ok = True
    asymmetric = []
    for width, height in geometries:
        geom = ref.letterbox_geometry(width, height)
        d2_geom = d2.letterbox_geometry(width, height, 416, 416)
        indep = independent_letterbox(width, height, 416, 416)
        keys = ("new_width", "new_height", "offset_x", "offset_y")
        agree = all(geom[k] == d2_geom[k] == indep[k] for k in keys)
        # 退化守卫与非对称补边事实
        degenerate = geom["new_width"] <= 1 or geom["new_height"] <= 1
        row = {
            "src_wh": [width, height],
            "reference": {k: geom[k] for k in keys},
            "d2_reference": {k: d2_geom[k] for k in keys},
            "independent": {k: indep[k] for k in keys},
            "agree": agree, "degenerate": degenerate,
            "asymmetric_padding": geom["asymmetric_padding"],
            "pad_right": geom["pad_right"], "pad_bottom": geom["pad_bottom"],
            "w_scale_zero": geom["w_scale"] == 0.0, "h_scale_zero": geom["h_scale"] == 0.0,
        }
        geometry_rows.append(row)
        all_ok = all_ok and agree
        if geom["asymmetric_padding"]:
            asymmetric.append({"src_wh": [width, height], "offset_x": geom["offset_x"],
                               "offset_y": geom["offset_y"], "pad_right": geom["pad_right"],
                               "pad_bottom": geom["pad_bottom"]})

    supplemental = None
    width, height = 683, 384
    geom = ref.letterbox_geometry(width, height)
    d2_geom = d2.letterbox_geometry(width, height, 416, 416)
    indep = independent_letterbox(width, height, 416, 416)
    supplemental = {
        "case": "683x384（契约 §geometry.half_pixel_rule 指名用例）",
        "in_sample_set": [683, 384] in [list(g) for g in geometries],
        "reference": {k: geom[k] for k in ("new_width", "new_height", "offset_x", "offset_y")},
        "d2_reference": {k: d2_geom[k] for k in ("new_width", "new_height", "offset_x", "offset_y")},
        "independent": {k: indep[k] for k in ("new_width", "new_height", "offset_x", "offset_y")},
        "pad_bottom": geom["pad_bottom"], "pad_right": geom["pad_right"],
        "asymmetric_padding": geom["asymmetric_padding"],
        "expected_from_contract": {"offset_y": 91, "pad_bottom": 92},
        "match_contract": geom["offset_y"] == 91 and geom["pad_bottom"] == 92,
        "agree_three_way": all(geom[k] == d2_geom[k] == indep[k]
                               for k in ("new_width", "new_height", "offset_x", "offset_y")),
    }

    # 退化守卫（接口加固后行为）：src_w<=1 / src_h<=1 与 new_*<=1 都必须抛 DegenerateGeometryError，
    # 且正向逆式 original_norm_to_network_norm 也必须走同一守卫（不得以 ZeroDivisionError 结束）。
    guard_probes = []
    positive_control = None
    for src_w, src_h in ((1, 1), (1, 4160), (4160, 1), (2, 1), (1, 2), (1, 100)):
        guard_probes.append(_degenerate_probe(ref, src_w, src_h))
    positive_control = _degenerate_probe(ref, 1440, 1920)
    guard_ok = (all(row["all_raise_degenerate"] for row in guard_probes)
                and positive_control["all_raise_degenerate"] is False)

    status = "PASS" if (s4b_ok and all_ok and supplemental["agree_three_way"]
                        and supplemental["match_contract"] and guard_ok) else "FAIL"
    log(f"[C3] S4-B 3/3 一致={s4b_ok}；样本集内 {len(geometries)} 种几何三方一致={all_ok}；"
        f"非对称补边 {len(asymmetric)} 种；683x384 补充用例={supplemental['agree_three_way']}；"
        f"退化守卫达标={guard_ok} → {status}")
    return {
        "status": status,
        "s4b_records": s4b_rows,
        "sample_set_geometries": geometry_rows,
        "sample_set_geometry_count": len(geometries),
        "asymmetric_padding_cases": asymmetric,
        "supplemental_683x384": supplemental,
        "degenerate_guard": {
            "contract_key": "geometry.degenerate_source_rule",
            "contract_text": ctx["contract"]["geometry"].get("degenerate_source_rule"),
            "contract_key_present": "degenerate_source_rule" in ctx["contract"]["geometry"],
            "negative_probes": guard_probes,
            "positive_control": positive_control,
            "all_negative_raise": all(row["all_raise_degenerate"] for row in guard_probes),
            "positive_control_no_raise": positive_control["all_raise_degenerate"] is False,
            "status": "PASS" if guard_ok else "FAIL",
            "note": ("加固后：src_w<=1 或 src_h<=1（以及 new_w<=1/new_h<=1）在逆式与正向逆式上"
                     "都抛 DegenerateGeometryError，不得出现 ZeroDivisionError"),
        },
        "note": ("S4-C 样本集内不含 683x384，但含 %d 种非对称补边几何（已逐值核对）；"
                 "683x384 作为契约指名用例以补充用例形式一并核对。" % len(asymmetric)),
        "three_way_sources": {"reference_implementation": ctx["ref_path"],
                              "d2_frozen_implementation": ctx["d2_path"],
                              "independent_integer_recompute": "本脚本 independent_letterbox（校验用）"},
    }


def _degenerate_probe(ref, src_w: int, src_h: int) -> dict:
    """探测退化几何守卫：两个逆式/正向逆式是否都抛 DegenerateGeometryError。"""
    geom = ref.letterbox_geometry(src_w, src_h)
    box = (0.1, 0.2, 0.6, 0.8)
    outcome = {}
    for name, func in (("network_norm_to_original_norm", ref.network_norm_to_original_norm),
                       ("original_norm_to_network_norm", ref.original_norm_to_network_norm)):
        try:
            func(box, geom)
            outcome[name] = {"raised": None, "note": "未抛异常"}
        except ref.DegenerateGeometryError as exc:
            outcome[name] = {"raised": "DegenerateGeometryError", "note": str(exc)[:160]}
        except Exception as exc:  # 其他异常（如 ZeroDivisionError）属未加固行为
            outcome[name] = {"raised": type(exc).__name__, "note": str(exc)[:160]}
    raise_flags = [item["raised"] == "DegenerateGeometryError" for item in outcome.values()]
    return {
        "src_wh": [int(src_w), int(src_h)],
        "new_wh": [geom["new_width"], geom["new_height"]],
        "degenerate_by_new": geom["new_width"] <= 1 or geom["new_height"] <= 1,
        "degenerate_by_source": src_w <= 1 or src_h <= 1,
        "outcomes": outcome,
        "all_raise_degenerate": all(raise_flags),
    }


# ──────────────────── C4 显示像素层往返 ────────────────────

def check_c4(ref, selection, consumer, log: RunLog) -> dict:
    per_box = []
    max_roundtrip = 0.0
    fidelity_fail = []
    recovery_no_solution = []
    degenerate_pixels = []
    boxes = 0
    for sample in selection:
        width = int(sample["geometry_wh"][0])
        height = int(sample["geometry_wh"][1])
        for index, detection in enumerate(sample["detections_expected"]):
            boxes += 1
            drawn = consumer.draw_box(detection, width, height, index)
            if drawn["zero_area"]:
                per_box.append({"sample_id": sample["sample_id"], "box_index": index,
                                "canvas_wh": [width, height], "zero_area": True,
                                "border_pixel_count": 0, "status": "SKIP_ZERO_AREA_AFTER_CLIP"})
                continue
            px = drawn["px_geom"]
            pixels = drawn["pixels"]
            observed = set(pixels)
            unit = drawn["unit_xyxy"]
            spans = (("x1", width), ("y1", height), ("x2", width), ("y2", height))
            errors = {}
            for axis, span in spans:
                continuous = float(unit[{"x1": 0, "y1": 1, "x2": 2, "y2": 3}[axis]]) * (span - 1)
                errors[axis] = abs(px[axis] - continuous)
            roundtrip = max(errors.values())
            max_roundtrip = max(max_roundtrip, roundtrip)

            expected_pixels = expected_border_pixels(px["x1"], px["y1"], px["x2"], px["y2"],
                                                     ref.DISPLAY_LINE_WIDTH_PX, width, height)
            expansion_exact = pixels == expected_pixels
            if not expansion_exact:
                fidelity_fail.append({"sample_id": sample["sample_id"], "box_index": index,
                                      "expected": len(expected_pixels), "observed": len(pixels)})

            recovery = recover_center_indices(px, observed, width, height, ref.DISPLAY_LINE_WIDTH_PX)
            matches_geometry = any(sol == {"x1": px["x1"], "y1": px["y1"], "x2": px["x2"], "y2": px["y2"]}
                                   for sol in recovery["solutions"])
            if recovery["status"] == "no_solution":
                recovery_no_solution.append({"sample_id": sample["sample_id"], "box_index": index})

            cols = [p[0] for p in pixels]
            rows = [p[1] for p in pixels]
            outer_bound = max(
                abs(min(cols) - float(unit[0]) * (width - 1)),
                abs(max(cols) - float(unit[2]) * (width - 1)),
                abs(min(rows) - float(unit[1]) * (height - 1)),
                abs(max(rows) - float(unit[3]) * (height - 1)),
            )
            if px["x1"] == px["x2"] or px["y1"] == px["y2"]:
                degenerate_pixels.append({"sample_id": sample["sample_id"], "box_index": index,
                                          "px_geom": px,
                                          "note": "像素索引退化（亚像素框）：中线索引相等，仍按冻结语义绘制"})
            per_box.append({
                "sample_id": sample["sample_id"], "box_index": index,
                "canvas_wh": [width, height], "unit_xyxy": list(unit), "clipped": drawn["clipped"],
                "zero_area": False, "px_geom": px,
                "border_pixel_count": len(pixels), "border_pixels_sha256": pixels_digest(pixels),
                "border_expansion_exact": expansion_exact,
                "px_roundtrip_max_error_px": roundtrip, "px_axis_errors_px": errors,
                "recovery_status": recovery["status"], "recovery_solution_count": len(recovery["solutions"]),
                "recovery_matches_geometry": matches_geometry,
                "outer_pixel_bound_px": outer_bound,
                "status": "PASS" if (expansion_exact and recovery["status"] != "no_solution"
                                     and roundtrip <= GATE_B_PIXEL_TOL) else "FAIL",
            })

    zero_area_probes = []
    for name, box in (("left_clip_to_zero", (-0.2, 0.5, 0.0, 0.9)),
                      ("top_clip_to_zero", (0.5, -0.1, 0.9, 0.0)),
                      ("right_clip_to_zero", (1.0, 0.1, 1.4, 0.9)),
                      ("fully_outside", (1.2, 1.2, 1.5, 1.5))):
        clip = ref.clip_unit_box(box)
        canvas_w, canvas_h = 1440, 1920
        px_geom = ref.original_norm_to_display_px(clip["xyxy"], canvas_w, canvas_h)
        raw_pixels = ref.border_pixel_sets(px_geom["x1"], px_geom["y1"], px_geom["x2"], px_geom["y2"],
                                           ref.DISPLAY_LINE_WIDTH_PX, canvas_w, canvas_h)
        display_drawn = [] if clip["zero_area"] else raw_pixels
        zero_area_probes.append({
            "probe": name, "input_unit_box": list(box), "clipped_xyxy": list(clip["xyxy"]),
            "clipped": clip["clipped"], "zero_area": clip["zero_area"],
            "display_border_pixels": len(display_drawn),
            "raw_expansion_if_not_skipped": len(raw_pixels),
            "status": "PASS" if (clip["zero_area"] and len(display_drawn) == 0
                                 and len(raw_pixels) > 0) else "FAIL",
        })
    positive_control = ref.clip_unit_box((0.2, 0.3, 0.6, 0.7))
    control_px = ref.original_norm_to_display_px(positive_control["xyxy"], 1440, 1920)
    control_pixels = ref.border_pixel_sets(control_px["x1"], control_px["y1"], control_px["x2"],
                                           control_px["y2"], ref.DISPLAY_LINE_WIDTH_PX, 1440, 1920)
    positive_control_ok = (not positive_control["zero_area"]) and len(control_pixels) > 0

    probes_ok = all(p["status"] == "PASS" for p in zero_area_probes) and positive_control_ok
    status = "PASS" if (not fidelity_fail and not recovery_no_solution and probes_ok
                        and max_roundtrip <= GATE_B_PIXEL_TOL) else "FAIL"
    log(f"[C4] 框 {boxes}；最大像素往返误差 {max_roundtrip:.6f} px（门槛 {GATE_B_PIXEL_TOL}）；"
        f"边框展开不一致 {len(fidelity_fail)}；反推无解 {len(recovery_no_solution)}；"
        f"零面积探针 {sum(1 for p in zero_area_probes if p['status']=='PASS')}/{len(zero_area_probes)} → {status}")
    return {
        "status": status,
        "boxes": boxes,
        "max_pixel_roundtrip_px": max_roundtrip,
        "gate_b_pixel_tolerance_px": GATE_B_PIXEL_TOL,
        "measurement_method": ("逐框、逐边比较几何中线像素索引："
                               "px = round_half_up(u*(span-1))；反向 u' = px/(span-1) → px' = px；"
                               "误差 = |px - u*(span-1)| ≤ 0.5 px（线宽语义使外沿像素可外扩 ±1 px，"
                               "故另有 informational outer_pixel_bound_px）"),
        "border_expansion_failures": fidelity_fail[:20],
        "recovery_no_solution": recovery_no_solution[:20],
        "pixel_index_degenerate_boxes": degenerate_pixels[:20],
        "zero_area_probes": zero_area_probes,
        "positive_control": {"unit_box": list(positive_control["xyxy"]),
                             "border_pixel_count": len(control_pixels),
                             "zero_area": positive_control["zero_area"],
                             "status": "PASS" if positive_control_ok else "FAIL"},
        "per_box": per_box,
    }


# ──────────────────── C5 D9 参考追溯 ────────────────────

def check_c5(ref, ctx, golden, log: RunLog) -> dict:
    by_id = {s["sample_id"]: s for s in golden["samples"]}
    records, skips, mismatches = [], [], []
    d9_chain = []
    all_ok = True
    for sample_id in S4B_SAMPLE_IDS:
        item = ctx["s4b"][sample_id]
        ps = item["record"]
        if sample_id not in by_id:
            skips.append({"sample_id": sample_id, "reason": "S4-C 黄金 109 样本中无同名 sample_id，"
                                                           "不做数值勾连（不静默跳过）"})
            records.append({"sample_id": sample_id, "path": item["path"], "sha256": item["sha256"],
                            "found_in_s4c": False, "status": "SKIP"})
            all_ok = False
            continue
        sample = by_id[sample_id]
        geometry = ps["geometry"]
        derived_state = "OK" if sample["detections_expected"] else "NO_HAND"
        row_mismatches = []

        def add(field, expected, actual, gate):
            row_mismatches.append({"sample_id": sample_id, "field": field, "gate": gate,
                                   "expected": expected, "actual": actual})

        if ps["frame_id"] != sample["frame_id"]:
            add("frame_id", sample["frame_id"], ps["frame_id"], "discrete")
        if [int(geometry["width"]), int(geometry["height"])] != [int(v) for v in sample["geometry_wh"]]:
            add("geometry_wh", list(sample["geometry_wh"]),
                [int(geometry["width"]), int(geometry["height"])], "discrete")
        if ps["state"] != derived_state:
            add("state", derived_state, ps["state"], "discrete")
        if int(ps["detection_count"]) != int(sample["detection_count_expected"]):
            add("detection_count", sample["detection_count_expected"], ps["detection_count"], "discrete")

        ps_dets = ps["detections"]
        expected_dets = sample["detections_expected"]
        box_rows = []
        if len(ps_dets) != len(expected_dets):
            add("box_count", len(expected_dets), len(ps_dets), "discrete")
        for index, expected_det in enumerate(expected_dets):
            if index >= len(ps_dets):
                break
            ps_det = ps_dets[index]
            for field in ("class_id", "class_name", "source_order"):
                if expected_det[field] != ps_det[field]:
                    add(f"{field}[{index}]", expected_det[field], ps_det[field], "discrete")
            score_err = abs(float(expected_det["score"]) - float(ps_det["score"]))
            score_bit = f64_bits(expected_det["score"]) == f64_bits(ps_det["score"])
            if score_err > GATE_A_SCORE_TOL:
                add(f"score[{index}]", expected_det["score"], ps_det["score"], "A")
            if not score_bit:
                add(f"score[{index}]", f64_bits(expected_det["score"]), f64_bits(ps_det["score"]), "D")
            xyxy_errs = [abs(float(a) - float(b)) for a, b in zip(expected_det["xyxy"], ps_det["xyxy"])]
            xyxy_bit = all(f64_bits(a) == f64_bits(b)
                           for a, b in zip(expected_det["xyxy"], ps_det["xyxy"]))
            for comp, err in enumerate(xyxy_errs):
                if err > GATE_A_XYXY_TOL:
                    add(f"xyxy[{comp}][{index}]", expected_det["xyxy"][comp], ps_det["xyxy"][comp], "A")
                if f64_bits(expected_det["xyxy"][comp]) != f64_bits(ps_det["xyxy"][comp]):
                    add(f"xyxy[{comp}][{index}]", f64_bits(expected_det["xyxy"][comp]),
                        f64_bits(ps_det["xyxy"][comp]), "D")
            box_rows.append({
                "box_index": index, "class_id": expected_det["class_id"],
                "class_name": expected_det["class_name"], "source_order": expected_det["source_order"],
                "score_abs_error": score_err, "score_bit_identical": score_bit,
                "xyxy_max_abs_error": max(xyxy_errs), "xyxy_bit_identical": xyxy_bit,
            })
        status = "PASS" if not row_mismatches else "FAIL"
        all_ok = all_ok and status == "PASS"
        mismatches.extend(row_mismatches)
        records.append({
            "sample_id": sample_id, "path": item["path"], "sha256": item["sha256"],
            "found_in_s4c": True, "frame_id": ps["frame_id"], "geometry_wh": list(sample["geometry_wh"]),
            "state": ps["state"], "derived_state": derived_state,
            "detection_count": ps["detection_count"], "boxes": box_rows,
            "mismatch_count": len(row_mismatches), "status": status,
            "stale": ps.get("stale"), "dropped_frames": ps.get("dropped_frames"),
        })

        heads = sample.get("heads", {})
        chain_row = {
            "sample_id": sample_id,
            "s4c_status": sample.get("status"),
            "s4c_mismatch_count": sample.get("mismatch_count"),
            "s4c_max_score_abs_error": sample.get("max_score_abs_error"),
            "s4c_max_xyxy_abs_error": sample.get("max_xyxy_abs_error"),
            "head13_tensor_sha256_match_t29": heads.get("head13", {}).get("byte_match"),
            "head26_tensor_sha256_match_t29": heads.get("head26", {}).get("byte_match"),
            "head13_expected_t29": heads.get("head13", {}).get("expected_tensor_sha256_t29"),
            "head13_actual": heads.get("head13", {}).get("actual_tensor_sha256"),
        }
        d9_chain.append(chain_row)

    t29_binding = None
    for binding in golden.get("upstream_bindings", []):
        if binding.get("id") == "s2a_t29_cpu_decode_nms_reference":
            t29_binding = binding
    t29 = dict(ctx["t29"])
    if t29["exists"] and t29_binding:
        t29["expected_sha256_from_s4c"] = t29_binding.get("expected_sha256")
        t29["match"] = t29["sha256"] == t29_binding.get("expected_sha256")
    chain_ok = True
    for row in d9_chain:
        chain_ok = chain_ok and row["s4c_status"] == "PASS" and row["s4c_mismatch_count"] == 0
        chain_ok = chain_ok and row["head13_tensor_sha256_match_t29"] is True
        chain_ok = chain_ok and row["head26_tensor_sha256_match_t29"] is True
    if t29_binding is not None:
        chain_ok = chain_ok and t29_binding.get("status") == "MATCH"
    if t29["exists"]:
        chain_ok = chain_ok and t29["match"] is True

    status = "PASS" if (all_ok and chain_ok) else "FAIL"
    log(f"[C5] S4-B 记录 {len(records)} 条；勾连一致={all_ok}；SKIP {len(skips)}；"
        f"D9 追溯链完整={chain_ok}（T29 SHA256 匹配={t29.get('match')}）→ {status}")
    return {
        "status": status,
        "records": records,
        "skips": skips,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:100],
        "d9_traceability_chain": {
            "claim": ("显示层消费的 S4-B PS 记录（host_result_*.json）与 S4-C 黄金 detections_expected 逐字段相同；"
                      "S4-C 的 detections_expected 已由 S4-C 对冻结 D9 实现重算结果做过 109/109 PASS 对拍，"
                      "并逐样本绑定 2A T29 黄金框与 T25 逐层张量 SHA256。"),
            "s4c_golden": {"path": ctx["golden_path"], "sha256": ctx["golden_sha256"],
                           "status": golden.get("status"),
                           "summary": golden.get("summary"),
                           "tool": golden.get("tool")},
            "s4c_upstream_t29_binding": t29_binding,
            "t29_file": t29,
            "per_sample": d9_chain,
            "t29_expected_sha256": (t29_binding or {}).get("expected_sha256"),
            "authority_note": ("2A T29/T25 位于只读主树；本脚本只读取 S4-C 记录的绑定结果，"
                               "并对 T29 文件独立计算 SHA256 以确认绑定未被替换。" ),
            "chain_ok": chain_ok,
        },
        "note": "sample_id 对不上的记录显式列为 SKIP 并给理由，不静默跳过。",
    }


# ──────────────────── C6 反例（篡改探针） ────────────────────

def apply_tamper(kind: str, entries: list):
    """对显示侧记录施加最小篡改；返回 (before, after, target, description)。"""
    target = None
    for sample, stage4_record, display_record in entries:
        if len(display_record["detections"]) >= 1:
            target = (sample, stage4_record, display_record)
            break
    if target is None:
        raise InputError(f"篡改探针 {kind} 找不到带框样本")
    sample, stage4_record, display_record = target
    detections = display_record["detections"]
    det = detections[0]
    sample_id = sample["sample_id"]
    if kind == "score_ulp":
        before = det["score"]
        det["score"] = math.nextafter(float(det["score"]), math.inf)
        after = det["score"]
        description = "score 加 1 ULP（float64 最低位 1 字节级改动；仍在 1e-6 容差内）"
    elif kind == "score_tol":
        before = det["score"]
        det["score"] = float(det["score"]) + 2e-6
        after = det["score"]
        description = "score 加 2e-6（超过 Gate A 容差）"
    elif kind == "xyxy_ulp":
        before = list(det["xyxy"])
        det["xyxy"][0] = math.nextafter(float(det["xyxy"][0]), math.inf)
        after = list(det["xyxy"])
        description = "xyxy[0] 加 1 ULP（1 字节级改动；仍在 1e-6 容差内）"
    elif kind == "xyxy_tol":
        before = list(det["xyxy"])
        det["xyxy"][3] = float(det["xyxy"][3]) + 2e-6
        after = list(det["xyxy"])
        description = "xyxy[3] 加 2e-6（超过 Gate A 容差）"
    elif kind == "source_order":
        before = det["source_order"]
        det["source_order"] = int(det["source_order"]) + 1
        after = det["source_order"]
        description = "source_order 加 1（离散字段 1 单位差异）"
    elif kind == "frame_id":
        before = display_record["frame_id"]
        display_record["frame_id"] = int(before) + 1
        after = display_record["frame_id"]
        description = "frame_id 加 1（离散字段 1 单位差异）"
    elif kind == "box_count":
        before = {"display_box_count": len(detections),
                  "authority_box_count": len(stage4_record["detections"])}
        detections.pop()
        after = {"display_box_count": len(detections),
                 "authority_box_count": len(stage4_record["detections"])}
        description = "显示侧少一个框（框数 1 单位差异；detection_count 未同步改动）"
    elif kind == "identity_rebuild":
        before = {"detections_aliased": display_record["detections"] is stage4_record["detections"],
                  "values_equal": True}
        after = {"detections_aliased": display_record["detections"] is stage4_record["detections"],
                 "values_equal": True}
        description = ("显示侧重建了数值对象（值完全相同但不复用阶段4 对象）——"
                       "用于验证「逐字节消费/别名引用」这一接口证据判定是否有效")
    else:
        raise InputError(f"未知篡改探针 {kind}")
    return before, after, {"sample_id": sample_id, "box_index": 0, "kind": kind,
                           "description": description}, description


def run_tamper_probe(ctx, args, selection, log: RunLog) -> dict:
    ref = ctx["ref"]
    harness = TamperHarness(ref)
    entries = [(sample, golden_to_stage4_record(sample), None) for sample in selection]
    entries = [(sample, stage4_record, harness.consume_rebuilt(stage4_record))
               for sample, stage4_record, _ in entries]
    authority_before = authority_snapshot(selection)
    before, after, target, description = apply_tamper(args.tamper_probe, entries)
    authority_after = authority_snapshot(selection)

    c1 = check_c1(ref, entries, identity_enforced=False, log=log)
    detected = c1["mismatch_count"] > 0
    gates = sorted({m["gate"] for m in c1["mismatches"]})
    identity_violated = bool(c1["alias_violations"])
    if args.tamper_probe == "identity_rebuild":
        detected = detected or identity_violated
    result = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "run_id": args.run_id,
        "generated_utc8": iso(utc8_now()),
        "probe_kind": args.tamper_probe,
        "probe_required_for_acceptance": args.tamper_probe in PROBE_REQUIRED,
        "detection_expected": True,
        "status": "FAIL" if detected else "PASS",
        "status_semantics": ("反例模式：status=FAIL 表示篡改被检出（期望结果），status=PASS 表示检查器漏检；"
                             "进程退出码同样由 detected 决定（检出=1）"),
        "description": description,
        "target": target,
        "before": before,
        "after": after,
        "detected": bool(detected),
        "gate_a_violated": "A" in gates,
        "gate_d_bit_identity_violated": "D" in gates,
        "discrete_violated": "discrete" in gates,
        "identity_invariant_violated": identity_violated,
        "violations": c1["mismatches"][:50],
        "violation_count": c1["mismatch_count"],
        "authority_unchanged": authority_before == authority_after,
        "authority_sha256_before": authority_before,
        "authority_sha256_after": authority_after,
        "c1_in_tamper_mode": {k: c1[k] for k in ("status", "identity_enforced", "samples", "boxes",
                                                 "max_score_abs_error", "max_xyxy_abs_error",
                                                 "mismatch_count", "bit_identity_violation_count")},
        "expected_exit_code": 1,
        "exit_code_self_reported": 0 if not detected else 1,
        "note": ("篡改施加在**显示侧**记录上（阶段4 权威记录不改动，authority_unchanged=true）；"
                 "探针模式下显示侧刻意重建对象，故不据「别名」判定，另设 identity_rebuild 探针单独验证该判定。"),
    }
    log(f"[C6] 探针 {args.tamper_probe}：检出={result['detected']} 违规={result['violation_count']} "
        f"命中门槛={gates} 篡改前={before} 篡改后={after} → 期望退出码 1")
    return result


# ──────────────────── C7 用词与契约 ────────────────────

def classify_occurrence(context: str, file_has_policy: bool) -> tuple[str, str | None]:
    for marker in EQUIVALENCE_MARKERS:
        if marker in context:
            return "EQUIVALENCE_DECLARATION", marker
    for marker in PROHIBITION_MARKERS:
        if marker.lower() in context.lower():
            return "PROHIBITION_DECLARATION", marker
    if file_has_policy:
        return "FILE_POLICY_DECLARATION", "file_declares_forbidden_word_policy"
    return "UNJUSTIFIED", None


def scan_text_file(path: pathlib.Path, rel: str, log: RunLog) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    file_has_policy = bool(re.search(r"FORBIDDEN_WORDS|forbidden_without_basis|\u7528\u8bcd",
                                     text, re.IGNORECASE))
    findings = []
    for index, line in enumerate(lines, start=1):
        for word in FORBIDDEN_WORDS:
            if word in line:
                window = "\n".join(lines[max(0, index - 2):index + 2])
                classification, marker = classify_occurrence(line + "\n" + window, file_has_policy)
                findings.append({"file": rel, "line": index, "word": word,
                                 "context": line.strip()[:200],
                                 "classification": classification, "matched_marker": marker})
    return findings


def scan_json_file(path: pathlib.Path, rel: str, log: RunLog) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return scan_text_file(path, rel, log)
    text = path.read_text(encoding="utf-8")
    file_has_policy = bool(re.search(r"FORBIDDEN_WORDS|forbidden_without_basis|\u7528\u8bcd",
                                     text, re.IGNORECASE))
    findings = []

    def walk(node, path_keys):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, path_keys + [str(key)])
        elif isinstance(node, list):
            for item in node:
                walk(item, path_keys)
        elif isinstance(node, str):
            for word in FORBIDDEN_WORDS:
                if word in node:
                    context = " ".join(path_keys) + " " + node
                    classification, marker = classify_occurrence(context, file_has_policy)
                    findings.append({"file": rel, "json_path": ".".join(path_keys), "line": None,
                                     "word": word, "context": node[:200],
                                     "classification": classification, "matched_marker": marker})

    walk(data, [])
    return findings


def check_c7(ref, ctx, log: RunLog) -> dict:
    contract = ctx["contract"]
    scoring = contract["scoring"]
    consumed_fields = list(ref.DETECTION_FIELDS)
    field_name_ok = consumed_fields == list(contract["consumed_stage4_record"]["detection_fields"])
    display_word_ok = scoring["display_word"] == "score"
    score_is_consumed_field = "score" in consumed_fields
    confidence_not_a_field = "confidence" not in consumed_fields
    display_path_has_word = any(word.lower() in display_path_source().lower() for word in FORBIDDEN_WORDS)

    targets = []
    docs_dir = REPO_ROOT / "docs" / "stage5"
    if docs_dir.is_dir():
        for path in sorted(docs_dir.rglob("*")):
            if path.is_file():
                targets.append(path)
    scripts_root = REPO_ROOT / "scripts"
    if scripts_root.is_dir():
        for directory in sorted(scripts_root.glob("stage5_*")):
            if directory.is_dir():
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        targets.append(path)

    scanned_files, skipped_files, findings = [], [], []
    for path in targets:
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        if path.suffix.lower() in SCAN_SKIP_SUFFIX:
            skipped_files.append({"file": rel, "reason": "二进制/非文本后缀"})
            continue
        if path.stat().st_size > SCAN_MAX_BYTES:
            skipped_files.append({"file": rel, "reason": f"超过 {SCAN_MAX_BYTES} 字节扫描上限"})
            continue
        scanned_files.append(rel)
        if path.suffix.lower() == ".json":
            findings.extend(scan_json_file(path, rel, log))
        else:
            findings.extend(scan_text_file(path, rel, log))

    unjustified = [f for f in findings if f["classification"] == "UNJUSTIFIED"]
    declarations = [f for f in findings if f["classification"] != "UNJUSTIFIED"]
    from collections import Counter
    counts = Counter(f["classification"] for f in findings)

    checks = {
        "consumed_field_name_is_score": field_name_ok and score_is_consumed_field,
        "contract_display_word_is_score": display_word_ok,
        "no_confidence_field_consumed": confidence_not_a_field,
        "no_forbidden_word_inside_display_path": not display_path_has_word,
        "no_unjustified_forbidden_word_usage": not unjustified,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    log(f"[C7] 扫描文件 {len(scanned_files)}（跳过 {len(skipped_files)}）；禁用用词出现 {len(findings)} 处，"
        f"声明类 {len(declarations)}，无依据 {len(unjustified)} → {status}")
    return {
        "status": status,
        "checks": checks,
        "consumed_field_name": consumed_fields,
        "contract_display_word": scoring["display_word"],
        "forbidden_words": [w for w in FORBIDDEN_WORDS],
        "classification_rule": {
            "EQUIVALENCE_DECLARATION": f"上下文含 {list(EQUIVALENCE_MARKERS)} 之一（显式声明等价/字段映射）",
            "PROHIBITION_DECLARATION": f"上下文含 {list(PROHIBITION_MARKERS)} 之一（禁止/条件性允许/用词规则）",
            "FILE_POLICY_DECLARATION": "文件内声明用词策略但本行无策略标记（记录待审，不判 FAIL）",
            "UNJUSTIFIED": "无任何策略依据的实际使用（判 FAIL）",
        },
        "scanned_files": scanned_files, "skipped_files": skipped_files,
        "finding_count": len(findings), "classification_counts": dict(counts),
        "findings": findings[:200], "findings_truncated": len(findings) > 200,
        "unjustified": unjustified[:50],
        "note": ("扫描范围含本任务自身脚本（不静默排除）；本脚本与自检文件中的出现均为策略声明，"
                 "按上述规则分类并逐处留证。"),
    }


# ──────────────────────────── 汇总 ────────────────────────────

def run_checks(ctx, args, selection, samples, log: RunLog, tamper_result=None) -> dict:
    ref = ctx["ref"]
    consumer = DisplayConsumer(ref)
    entries = []
    for sample in samples:
        stage4_record = golden_to_stage4_record(sample)
        entries.append((sample, stage4_record, consumer.consume(stage4_record)))

    checks = {}
    checks["C1_field_consistency"] = check_c1(ref, entries, identity_enforced=tamper_result is None, log=log)
    checks["C2_no_second_semantics"] = check_c2(ref, ctx, samples, entries, consumer, log)
    checks["C3_geometry_crosscheck"] = check_c3(ctx, ctx["golden"], log)
    checks["C4_pixel_roundtrip"] = check_c4(ref, samples, consumer, log)
    checks["C5_d9_traceability"] = check_c5(ref, ctx, ctx["golden"], log)
    if tamper_result is not None:
        checks["C6_tamper_probe"] = tamper_result
    elif selection["rule"] == "seeded_random_subset":
        checks["C6_tamper_probe"] = {
            "status": "NOT_APPLICABLE_THIS_RUN",
            "summary_line": "本运行不适用（抽样复现运行未跑篡改探针）",
            "note": ("抽样运行只用于复现抽样确定性/子集回归；反例证据与终态汇总由 run_s5c_evidence.ps1 "
                     "写入本次任务主运行（full_all_samples）目录，本目录不做 finalize"),
        }
    else:
        checks["C6_tamper_probe"] = {
            "status": "PENDING_FINALIZE",
            "summary_line": "待 finalize 汇总（run_s5c_evidence.ps1 跑完全部探针后）",
            "note": "由 run_s5c_evidence.ps1 跑完全部探针后 --finalize-exit-codes 汇总，且必须由脚本写入本目录",
        }
    checks["C7_wording_contract"] = check_c7(ref, ctx, log)

    failures, skips, not_run = [], [], list(NOT_RUN_ITEMS)
    for name, item in checks.items():
        if item["status"] == "FAIL":
            failures.append({"check": name, "status": "FAIL"})
        elif item["status"] == "SKIP":
            skips.append({"check": name, "detail": item.get("skips", [])})
    for item in checks["C5_d9_traceability"]["skips"]:
        skips.append({"check": "C5_d9_traceability", "detail": item})
    overall = "PASS" if not failures else "FAIL"

    c1 = checks["C1_field_consistency"]
    c4 = checks["C4_pixel_roundtrip"]
    c5 = checks["C5_d9_traceability"]
    stats = {
        "samples_selected": len(samples),
        "samples_passed": sum(1 for row in c1["per_sample"] if row["status"] == "PASS"),
        "samples_failed": sum(1 for row in c1["per_sample"] if row["status"] == "FAIL"),
        "boxes_compared": c1["boxes"],
        "boxes_with_zero_detections": sum(1 for row in c1["per_sample"] if row["boxes_expected"] == 0),
        "field_values_compared": c1["field_values_compared"],
        "max_score_abs_error": c1["max_score_abs_error"],
        "max_xyxy_abs_error": c1["max_xyxy_abs_error"],
        "max_authority_score": c1["max_authority_score"],
        "max_pixel_roundtrip_px": c4["max_pixel_roundtrip_px"],
        "bit_identity_violations": c1["bit_identity_violation_count"],
        "alias_violations": len(c1["alias_violations"]),
        "geometries_checked": checks["C3_geometry_crosscheck"]["sample_set_geometry_count"],
        "asymmetric_padding_geometries": len(checks["C3_geometry_crosscheck"]["asymmetric_padding_cases"]),
        "s4b_records_checked": len(c5["records"]),
        "s4b_records_skipped": len(c5["skips"]),
        "tamper_probes_required": list(PROBE_REQUIRED),
        "seed": selection["seed"],
        "seed_source": selection["seed_source"],
        "selection_rule": selection["rule"],
        "max_box_count": checks["C2_no_second_semantics"]["max_box_count"],
        "min_accepted_score": checks["C2_no_second_semantics"]["min_accepted_score"],
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "run_id": args.run_id,
        "generated_utc8": iso(utc8_now()),
        "status": overall,
        "mode": "pristine" if tamper_result is None else f"tamper:{args.tamper_probe}",
        "contract": {
            "id": getattr(ref, "CONTRACT_ID", None),
            "status": getattr(ref, "CONTRACT_STATUS", None),
            "path": ctx["contract_path"], "sha256": ctx["contract_sha256"],
            "reference_implementation": ctx["ref_path"], "reference_sha256": ctx["ref_sha256"],
        },
        "inputs": [
            {"id": "s4c_replay_golden_109", "path": ctx["golden_path"], "sha256": ctx["golden_sha256"],
             "status": ctx["golden"].get("status"), "samples": len(ctx["golden"]["samples"])},
            *[{"id": f"s4b_host_result_{sid}", "path": item["path"], "sha256": item["sha256"]}
              for sid, item in ctx["s4b"].items()],
            {"id": "s5a_contract", "path": ctx["contract_path"], "sha256": ctx["contract_sha256"]},
            {"id": "s4a_contract", "path": ctx["s4a_path"], "sha256": ctx["s4a_sha256"]},
            {"id": "t29_cpu_decode_nms_reference", "path": ctx["t29"]["path"],
             "sha256": ctx["t29"].get("sha256"), "exists": ctx["t29"]["exists"]},
        ],
        "selection": selection,
        "checks": checks,
        "statistics": stats,
        "failures": failures,
        "skips": skips,
        "not_run": not_run,
        "limitations": [
            "纯离线：无 Vivado / xsim / JTAG / 硬件 / HDMI / 摄像头；所有板上与真实时延项 NOT_RUN",
            "S4-A 契约状态 DRAFT_NOT_FROZEN；本检查只核对字段名与语义一致性，不构成阶段4 G0",
            "S4-C 样本不含显式 state 字段，state 由 detections_expected 长度派生并已在报告中标注",
            "xyxy_px 派生字段未参与对拍；显示层不使用该字段（G0 规定只用 xyxy）",
            "1 ULP 级篡改在 Gate A（1e-6）内、只能由 Gate D（逐字节一致）捕获；两项门槛分别报告",
            "抽样运行（--limit）的 C6 为 NOT_APPLICABLE_THIS_RUN：篡改探针与终态汇总只在主运行目录完成",
        ],
        "test_case_coverage": TEST_CASE_COVERAGE,
    }
    return report


def render_summary(report: dict) -> str:
    stats = report["statistics"]
    checks = report["checks"]
    lines = [
        f"# S5-C 阶段4 数值链路回归勾连 · {report['run_id']}",
        "",
        f"- 生成时刻（UTC+8）：{report['generated_utc8']}",
        f"- 总体状态：**{report['status']}**（退出码 0 = 无 FAIL；1 = 存在 FAIL；2 = 输入/环境错误）",
        f"- 契约：{report['contract']['id']}（{report['contract']['status']}）",
        f"- 冻结参考实现：`{report['contract']['reference_implementation']}` "
        f"SHA256 `{report['contract']['reference_sha256']}`",
        f"- 样本选择：{stats['selection_rule']}，样本 {stats['samples_selected']}/"
        f"{report['selection']['available']}，框 {stats['boxes_compared']}，"
        f"种子 {stats['seed']}（{stats['seed_source']}）",
        "",
        "## 逐项结果",
        "",
        "| 检查 | 状态 | 关键量 |",
        "|---|---|---|",
        f"| C1 字段级一致（109 样本逐框） | {checks['C1_field_consistency']['status']} | "
        f"字段值比较 {stats['field_values_compared']}，mismatch "
        f"{checks['C1_field_consistency']['mismatch_count']}，最大 score 误差 "
        f"{stats['max_score_abs_error']:.3e}，最大坐标误差 {stats['max_xyxy_abs_error']:.3e} |",
        f"| C2 不引入第二套语义 | {checks['C2_no_second_semantics']['status']} | "
        f"常量一致={checks['C2_no_second_semantics']['checks']['constants_match_contract_and_s4a']}，"
        f"accepted≡阶段4={checks['C2_no_second_semantics']['checks']['accepted_set_equals_stage4_boxes']}，"
        f"禁用 token={checks['C2_no_second_semantics']['display_path_forbidden_tokens_hit']} |",
        f"| C3 几何同源交叉核对 | {checks['C3_geometry_crosscheck']['status']} | "
        f"S4-B 3/3，样本集内 {stats['geometries_checked']} 种几何三方一致，"
        f"非对称补边 {stats['asymmetric_padding_geometries']} 种 |",
        f"| C4 显示像素层往返 | {checks['C4_pixel_roundtrip']['status']} | "
        f"最大往返误差 {stats['max_pixel_roundtrip_px']:.6f} px（门槛 "
        f"{checks['C4_pixel_roundtrip']['gate_b_pixel_tolerance_px']}），零面积探针 "
        f"{sum(1 for p in checks['C4_pixel_roundtrip']['zero_area_probes'] if p['status'] == 'PASS')}/"
        f"{len(checks['C4_pixel_roundtrip']['zero_area_probes'])} |",
        f"| C5 D9 参考追溯 | {checks['C5_d9_traceability']['status']} | "
        f"PS 记录 {stats['s4b_records_checked']} 条，SKIP {stats['s4b_records_skipped']}，"
        f"mismatch {checks['C5_d9_traceability']['mismatch_count']} |",
        f"| C6 反例（篡改探针） | {checks['C6_tamper_probe']['status']} | "
        f"{checks['C6_tamper_probe'].get('summary_line', '见 regression_report.json')} |",
        f"| C7 用词与契约 | {checks['C7_wording_contract']['status']} | "
        f"扫描 {len(checks['C7_wording_contract']['scanned_files'])} 文件，"
        f"禁用用词 {checks['C7_wording_contract']['finding_count']} 处（无依据 "
        f"{len(checks['C7_wording_contract']['unjustified'])}） |",
        "",
        "## 用例覆盖（S5-A 契约 test_cases 与本任务的对应）",
        "",
        "| 用例 | 状态 | 覆盖检查 | 说明 |",
        "|---|---|---|---|",
    ]
    for item in report.get("test_case_coverage", []):
        lines.append(f"| {item['case']} | {item['status']} | {','.join(item['covered_by']) or '—'} | "
                     f"{item.get('note', item['requirement'])} |")
    lines += [
        "",
        "## 统计口径",
        "",
        f"- 样本数：{stats['samples_selected']}（通过 {stats['samples_passed']}，失败 {stats['samples_failed']}）",
        f"- 框数：{stats['boxes_compared']}（零框样本 {stats['boxes_with_zero_detections']}）",
        f"- 参与比较的字段值数：{stats['field_values_compared']}"
        "（每样本 frame_id/detection_count/框数 + 每框 class_id/class_name/source_order/score/xyxy×4）",
        f"- 最大 score 绝对误差：{stats['max_score_abs_error']:.3e}（Gate A 容差 1e-06）",
        f"- 最大坐标绝对误差：{stats['max_xyxy_abs_error']:.3e}（Gate A 容差 1e-06）",
        f"- 位型（逐字节）违规数：{stats['bit_identity_violations']}（Gate D）；"
        f"别名引用违规数：{stats.get('alias_violations')}",
        f"- 最大像素往返误差：{stats['max_pixel_roundtrip_px']:.6f} px（Gate B 门槛 1.0）",
        f"- 最大接受框数：{stats['max_box_count']}（上限 15）；接受框最小分数：{stats['min_accepted_score']}",
        "",
        "## 反例与对照（C6）",
        "",
    ]
    c6 = checks["C6_tamper_probe"]
    for row in c6.get("results", []):
        lines.append(f"- `{row['kind']}`：检出={row['detected']}，命中门槛={row.get('gates')}，"
                     f"真实退出码={row.get('observed_exit_code')}，证据 `{row.get('evidence')}`")
    lines += [
        f"- 未篡改正对照：真实退出码 {c6.get('pristine_control_exit_code')}",
        "",
        "## SKIP / NOT_RUN（如实标注）",
        "",
    ]
    for item in report["skips"]:
        lines.append(f"- SKIP `{item['check']}`：{json.dumps(item['detail'], ensure_ascii=False)[:400]}")
    for item in report["not_run"]:
        lines.append(f"- {item['status']} `{item['id']}` {item['item']}：{item['reason']}")
    lines += ["", "## 限制", ""]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


# ──────────────────────────── 终态汇总 ────────────────────────────

def finalize_exit_codes(args, out_dir: pathlib.Path, log: RunLog) -> int:
    observed_path = out_dir / "console" / "observed_exit_codes.json"
    if not observed_path.is_file():
        log(f"[FINALIZE] 缺少 {observed_path}：请先由 run_s5c_evidence.ps1 运行全部步骤")
        return 2
    observed = json.loads(observed_path.read_text(encoding="utf-8"))
    items = observed.get("steps", [])
    mismatched = [step for step in items if step.get("exit_code") != step.get("expected_exit_code")]
    log(f"[FINALIZE] 步骤 {len(items)}；退出码与期望不符 {len(mismatched)}")
    for step in items:
        log(f"  - {step['name']}: observed={step.get('exit_code')} expected={step.get('expected_exit_code')}")

    tamper_dir = out_dir / "tamper"
    probe_rows = []
    if tamper_dir.is_dir():
        for path in sorted(tamper_dir.glob("tamper_*_before_after.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            kind = data["probe_kind"]
            observed_step = next((s for s in items if s["name"] == f"tamper_{kind}"), None)
            probe_rows.append({
                "kind": kind, "required": kind in PROBE_REQUIRED,
                "detected": data["detected"], "gates": [g for g, flag in
                                                         (("discrete", data["discrete_violated"]),
                                                          ("A", data["gate_a_violated"]),
                                                          ("D", data["gate_d_bit_identity_violated"]))
                                                         if flag] or
                                                        (["identity_invariant"] if data["identity_invariant_violated"] else []),
                "violation_count": data["violation_count"],
                "expected_exit_code": 1,
                "observed_exit_code": observed_step["exit_code"] if observed_step else None,
                "before": data["before"], "after": data["after"],
                "evidence": str(path.relative_to(out_dir)).replace("\\", "/"),
                "authority_unchanged": data["authority_unchanged"],
            })
    required_rows = [r for r in probe_rows if r["required"]]
    required_ok = bool(required_rows) and all(
        r["detected"] and r["observed_exit_code"] == 1 for r in required_rows)
    extra_ok = all(r["detected"] and r["observed_exit_code"] == 1 for r in probe_rows if not r["required"])
    pristine_step = next((s for s in items if s["name"] == "pristine"), None)
    pristine_ok = bool(pristine_step and pristine_step["exit_code"] == 0)
    c6 = {
        "status": "PASS" if (required_ok and extra_ok and pristine_ok and not mismatched) else "FAIL",
        "probes": [r["kind"] for r in probe_rows],
        "required_probes": list(PROBE_REQUIRED),
        "results": probe_rows,
        "pristine_control_exit_code": pristine_step["exit_code"] if pristine_step else None,
        "all_required_detected": required_ok,
        "observed_exit_code_mismatches": mismatched,
        "summary_line": (f"必检探针 {len(required_rows)}/4 检出（真实退出码 1），"
                         f"正对照退出码 {pristine_step['exit_code'] if pristine_step else 'NA'}"),
        "evidence_dir": str(tamper_dir.relative_to(out_dir)).replace("\\", "/") if tamper_dir.is_dir() else None,
        "note": "探针证据独立保存，不因失败而删除；退出码为 run_s5c_evidence.ps1 记录的真实 $LASTEXITCODE",
    }

    report_path = out_dir / "regression_report.json"
    if not report_path.is_file():
        log(f"[FINALIZE] 缺少 {report_path}")
        return 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["checks"]["C6_tamper_probe"] = c6
    report["failures"] = [{"check": name, "status": item["status"]}
                          for name, item in report["checks"].items()
                          if item.get("status") == "FAIL"]
    report["status"] = "PASS" if not report["failures"] else "FAIL"
    report["generated_utc8"] = iso(utc8_now())
    report["finalize"] = {
        "observed_exit_codes_path": "console/observed_exit_codes.json",
        "observed_steps": items,
        "exit_code_mismatches": mismatched,
        "finalized_utc8": iso(utc8_now()),
    }
    write_json(report_path, report)
    write_text(out_dir / "summary.md", render_summary(report))

    manifest_path = out_dir / "run_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["observed_exit_codes"] = items
        manifest["exit_code_verification"] = {
            "all_match_expectation": not mismatched,
            "source": "console/observed_exit_codes.json（run_s5c_evidence.ps1 记录的真实 $LASTEXITCODE）",
            "finalize_exit_code": 0 if not mismatched else 1,
        }
        manifest["finalized_utc8"] = iso(utc8_now())
        manifest["final_status"] = report["status"]
        write_json(manifest_path, manifest)

    exit_code = 0 if (report["status"] == "PASS" and not mismatched) else 1
    log(f"[FINALIZE] 汇总后总体状态 {report['status']}；C6 {c6['status']}；退出码 {exit_code}")
    return exit_code


# ──────────────────────────── 主流程 ────────────────────────────

def build_manifest(args, ctx, selection, report, log: RunLog, started: float) -> dict:
    script_path = pathlib.Path(__file__).resolve()
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "run_id": args.run_id,
        "generated_utc8": iso(utc8_now()),
        "elapsed_seconds": round(time.time() - started, 3),
        "command": {
            "argv": [sys.executable, str(script_path)] + sys.argv[1:],
            "cwd": os.getcwd(),
            "python": sys.version.replace("\n", " "),
            "python_executable": sys.executable,
            "note": "真实退出码由 run_s5c_evidence.ps1 记录到 console/observed_exit_codes.json",
        },
        "source_baseline": git_info(),
        "scripts": [{"path": "scripts/stage5_s5c/check_s5c_stage4_regression.py",
                     "sha256": sha256_file(script_path)}],
        "imported_modules": [
            {"name": "s5_display_geometry_reference", "path": ctx["ref_path"],
             "sha256": ctx["ref_sha256"], "contract_id": getattr(ctx["ref"], "CONTRACT_ID", None),
             "role": "显示几何/取整/裁剪/边框像素的唯一来源（本检查器导入使用，未复制公式）"},
            {"name": "s1_t02_d2_numeric_reference", "path": ctx["d2_path"],
             "sha256": ctx["d2_sha256"], "role": "D2 冻结几何对拍参考（只读导入）"},
        ],
        "upstream_inputs": report["inputs"],
        "selection": selection,
        "statistics": report["statistics"],
        "checks_status": {name: item.get("status") for name, item in report["checks"].items()},
        "exit_code": 0 if report["status"] == "PASS" else 1,
        "exit_code_self_reported": 0 if report["status"] == "PASS" else 1,
        "skips": report["skips"],
        "not_run": report["not_run"],
        "limitations": report["limitations"],
        "tamper_probe": args.tamper_probe,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="S5-C：阶段5 显示消费 ← 阶段4 整数结果 / 2A D9 参考的回归勾连检查器")
    parser.add_argument("--run-id", default=None, help="运行标识（默认按 UTC+8 日期生成）")
    parser.add_argument("--out", default=None,
                        help="本次运行的证据目录（默认 report/evidence/S5-C/<run_id>；传入即为该目录）")
    parser.add_argument("--limit", type=int, default=None, help="随机抽样样本数（默认全 109）")
    parser.add_argument("--seed", type=int, default=None, help="抽样种子（默认 20261021）")
    parser.add_argument("--tamper-probe", default="none", choices=("none",) + PROBE_KINDS,
                        help="反例探针：对显示侧数值施加最小篡改，检查器必须检出")
    parser.add_argument("--golden", default=str(DEFAULT_GOLDEN), help="S4-C 黄金对拍输入路径")
    parser.add_argument("--s4b-dir", default=str(DEFAULT_S4B_DIR), help="S4-B PS 记录目录")
    parser.add_argument("--finalize-exit-codes", action="store_true",
                        help="汇总 run_s5c_evidence.ps1 记录的真实退出码与篡改探针证据到报告/清单/摘要")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    log = RunLog()
    started = time.time()
    if args.run_id is None:
        args.run_id = f"s5c_regression_{utc8_now().strftime('%Y%m%d')}_r01"
    out_dir = pathlib.Path(args.out) if args.out else (REPO_ROOT / "report" / "evidence" / "S5-C" / args.run_id)
    out_dir = out_dir.resolve()

    if args.finalize_exit_codes:
        log(f"[S5-C] finalize run_id={args.run_id} out={out_dir}")
        return finalize_exit_codes(args, out_dir, log)

    log(f"[S5-C] run_id={args.run_id} tamper={args.tamper_probe} limit={args.limit} seed={args.seed}")
    log(f"[S5-C] 证据目录 {out_dir}")

    try:
        if out_dir.exists() and any(out_dir.iterdir()) and args.tamper_probe == "none" and _has_run_artifacts(out_dir):
            raise InputError(f"证据目录已存在且含既有运行产物，禁止覆盖：{out_dir}（请换 --run-id）")
        ctx = build_context(args, log)
        samples, selection = select_samples(ctx["golden"], args.limit, args.seed, log)
        tamper_result = None
        if args.tamper_probe != "none":
            tamper_result = run_tamper_probe(ctx, args, samples, log)
        report = run_checks(ctx, args, selection, samples, log, tamper_result=tamper_result)
        report["tamper_probe"] = args.tamper_probe
    except InputError as exc:
        log(f"[输入/环境错误] {exc}")
        _write_console(out_dir, _label(args), log, 2)
        return 2
    except Exception as exc:  # 未预期异常也必须留痕
        import traceback
        log(f"[未预期异常] {type(exc).__name__}: {exc}")
        log(traceback.format_exc())
        _write_console(out_dir, _label(args), log, 2)
        return 2

    if args.tamper_probe == "none":
        write_json(out_dir / "regression_report.json", report)
        write_text(out_dir / "summary.md", render_summary(report))
        write_json(out_dir / "run_manifest.json", build_manifest(args, ctx, selection, report, log, started))
    else:
        tamper_dir = out_dir / "tamper"
        write_json(tamper_dir / f"regression_report_tamper_{args.tamper_probe}.json", report)
        write_json(tamper_dir / f"tamper_{args.tamper_probe}_before_after.json", tamper_result)
        write_json(tamper_dir / f"tamper_{args.tamper_probe}_manifest.json",
                   build_manifest(args, ctx, selection, report, log, started))

    if args.tamper_probe == "none":
        exit_code = 0 if report["status"] == "PASS" else 1
    else:
        exit_code = 1 if tamper_result["detected"] else 0
    log(f"[S5-C] 总体状态 {report['status']}（tamper={args.tamper_probe}，检出="
        f"{tamper_result['detected'] if tamper_result else 'NA'}）；退出码 {exit_code}")
    _write_console(out_dir, _label(args), log, exit_code)
    return exit_code


def _label(args) -> str:
    if args.tamper_probe != "none":
        return f"checker_tamper_{args.tamper_probe}"
    return "pristine" if args.limit is None else "seeded_subset"


def _has_run_artifacts(out_dir: pathlib.Path) -> bool:
    for name in ("regression_report.json", "run_manifest.json", "summary.md"):
        if (out_dir / name).is_file():
            return True
    return False


def _write_console(out_dir: pathlib.Path, label: str, log: RunLog, exit_code: int) -> None:
    text = log.text() + f"SELF_REPORTED_EXIT_CODE: {exit_code}\n"
    write_text(out_dir / "console" / f"{label}.log.txt", text)


if __name__ == "__main__":
    sys.exit(main())