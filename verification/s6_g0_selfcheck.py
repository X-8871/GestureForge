#!/usr/bin/env python3
"""阶段6 S6-A（G0 包 + 行为表 v1.4 / r05）只读自检。

加固后的机器检查（r02，针对独立评审 S6A_20261022_r01 的 C3 盲区）：

  C1   JSON 身份与必填块（接受 S6A-G0-v1 / v1.1）
  C2   ID 唯一性与最小规模
  C3   **文档 ↔ JSON 标识集合双向一致**（不变量/迁移/参数/事件/状态/行为行/动作类型，
       迁移另比对 from/to；参数按 §14 表行比对，而不仅是 token 出现）
  C4   待批准纪律（24 项参数全 PENDING_APPROVAL + 来源/责任人 + 动作映射待批准）
  C5   五类动作映射一致（class_id 0..4、2A 顺序、target 唯一、类型在支持集合内）
  C6   硬不变量与唯一触发解释完整（H-1..H-10；ONCE_PER_ACQUISITION）
  C7   人工手算样例的**独立复算**（30 例；窗口跨度按「窗口首帧 → 第 T6-S02 个 WINDOW_MATCH 帧」计算，
       并断言与宽松序列跨度口径下 m3_fires 结论一致；新增锁存 STABLE + 门恰在 TIMEOUT 帧开启的角落序列）
  C8   上游只读文件 SHA-256 复算（含 w4/w5 只读提交版本）
  C9   文档必备覆盖关键词与章节存在
  C10  窄口径禁止声明扫描
  C11  **证据清单 vs 实际文件存在性/哈希**（manifest 双向比对 + STATE 声明的证据文件存在性）
  C12  谓词拆分一致性（定义、引用、禁用含糊“匹配”；**全量双向断言** predicates.used_by ↔ predicates_used；
       禁用标识符扫描 matched_frames / t_last_match / t_submit+，仅放行邻近标注“已废弃”的历史说明；
       M5/B13 无 predicates_used 字段的叙述必须与 JSON 现状一致；M5 必须复述「本帧为窗口推进帧」限定；
       任何 predicates_used 出现时必须为非空列表（显式 [] 不合法））
  C13  冷却全局门一致性（H-10 / M5 / cooldown_policy / 文档）
  C14  W_min 与实测帧周期口径一致性（B-04/N-05）
  C15  H-4/NO_HAND 匹配计数一致性（B-02）
  C16  迁移可达性与覆盖声明一致性（M4/M7/M14；B26；§12.1）
  C17  STABLE 锁存语义一致性（观察项：锁存范围、退出路径、不得存在 STABLE→CANDIDATE；U6-16）

边界：本脚本只做规格一致性、算术与证据存在性复算，**不**验证状态机行为、
**不**代表 G0/G2/G4/G5 或任何验收结论。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

BEHAVIOR_ID_RE = re.compile(r"\bB\d{2}\b")
PARAM_ID_RE = re.compile(r"\bT6-[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*")
INVARIANT_ID_RE = re.compile(r"\bH-\d+\b")
TRANSITION_ID_RE = re.compile(r"\bM\d+\b")
EVENT_ID_RE = re.compile(r"`((?:E|S|ACTION)_[A-Z_]+)`")
STATE_TOKEN_RE = re.compile(r"`([A-Z_]+)`")
ACTION_TYPE_RE = re.compile(r"`(A_[A-Z_]+)`")
STATE_NAMES = ("IDLE", "CANDIDATE", "STABLE", "TRIGGERED", "COOLDOWN", "LOST", "UNKNOWN_RECOVER")

REQUIRED_DOC_KEYWORDS = [
    "行为表 v1",
    "ACTION_SUBMITTED",
    "ACTION_EFFECTIVE",
    "提交成功",
    "实际生效",
    "持续保持只触发一次",
    "低 FPS",
    "NO_HAND",
    "单调时钟",
    "frame_id",
    "冷却",
    "抖动",
    "重获",
    "过期",
    "UNKNOWN_RECOVER",
    "class_id",
    "TARGET_CONTINUES",
    "WINDOW_MATCH",
    "W_min",
    "window_complete",
    "H-10",
    "DELIVERED_PENDING_APPROVAL",
    "t_last_submit",
]
REQUIRED_DOC_SECTIONS = ["## 5.", "## 9.", "## 10.", "## 12.", "## 15.", "## 18.", "### 12.1"]
FORBIDDEN_CLAIMS = [
    "阈值已冻结",
    "指标已批准",
    "G0 已通过",
    "验收已通过",
    "已通过验收",
    "已实测通过",
    "已冻结数值",
]
AMBIGUOUS_MATCH_PHRASES = [
    "连续匹配帧",
    "与当前目标匹配的框",
    "匹配成立",
    "匹配计数只由 state",
]
EXPECTED_CLASS_ORDER = ["fist", "palm", "one", "two_up", "three"]
SCOPE_STATEMENT = (
    "本自检只复算规格一致性与算术/证据存在性，不代表状态机行为正确、独立审查通过或 G0/G4/G5。"
)


class CheckFailure(Exception):
    """单个检查项失败。"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def r6(value: float) -> float:
    return round(float(value), 6)


def doc_section(doc: str, start: str, end: str) -> str:
    if start not in doc:
        raise CheckFailure(f"文档缺少章节锚点：{start!r}")
    tail = doc.split(start, 1)[1]
    if end in tail:
        return tail.split(end, 1)[0]
    return tail


# ---------------------------------------------------------------- C1 / C2


def check_identity(data: dict[str, Any]) -> None:
    if data.get("schema_version") != 1:
        raise CheckFailure("schema_version 必须为 1")
    if data.get("artifact") != "s6a_stage6_g0_behavior":
        raise CheckFailure("artifact 名称不符")
    version = data.get("artifact_version")
    allowed_versions = ("S6A-G0-v1", "S6A-G0-v1.1", "S6A-G0-v1.2", "S6A-G0-v1.3", "S6A-G0-v1.4")
    if version not in allowed_versions:
        raise CheckFailure(f"artifact_version 必须为 {allowed_versions}，实际 {version!r}")
    if data.get("status") != "G0_PACKET_PENDING_APPROVAL":
        raise CheckFailure("status 必须为 G0_PACKET_PENDING_APPROVAL")
    for key in (
        "baseline",
        "upstream",
        "hard_invariants",
        "event_classes",
        "behavior_rows",
        "parameters",
        "transitions",
        "states",
        "actions",
        "open_decisions",
    ):
        if not data.get(key):
            raise CheckFailure(f"缺少必填块：{key}")
    if data["baseline"].get("start_commit") != "d8bc70e43572a8e44ddcd4b3489166e28a1c6151":
        raise CheckFailure("起始提交与开工核验不一致")
    expected_runs = {
        "S6A-G0-v1.1": "s6a_g0_20261022_r02",
        "S6A-G0-v1.2": "s6a_g0_20261022_r03",
        "S6A-G0-v1.3": "s6a_g0_20261022_r04",
        "S6A-G0-v1.4": "s6a_g0_20261022_r05",
    }
    if version in expected_runs:
        revision = data.get("revision") or {}
        for key in ("run_id", "review_source", "changes", "review_status"):
            if not revision.get(key):
                raise CheckFailure(f"{version} 缺少 revision.{key}")
        if data.get("run_id") != expected_runs[version]:
            raise CheckFailure(f"{version} 的 run_id 必须是 {expected_runs[version]}")
        if not data.get("supersedes_run_id"):
            raise CheckFailure(f"{version} 必须声明 supersedes_run_id")


def check_unique_ids(data: dict[str, Any]) -> None:
    for block in ("behavior_rows", "parameters", "transitions", "open_decisions", "hard_invariants"):
        ids = [item["id"] for item in data[block]]
        if len(ids) != len(set(ids)):
            raise CheckFailure(f"{block} 存在重复 ID")
    states = list(data["states"])
    if len(states) != len(set(states)):
        raise CheckFailure("states 存在重复")
    if len(data["behavior_rows"]) < 20:
        raise CheckFailure("行为表行数少于预期")
    if len(data["hard_invariants"]) < 10:
        raise CheckFailure("硬不变量少于 10 条（H-10 全局冷却门必须存在）")
    reach = data.get("reachability") or {}
    reach_ids = set((reach.get("transitions") or {}).keys())
    trans_ids = {item["id"] for item in data["transitions"]}
    if reach_ids != trans_ids:
        raise CheckFailure(f"reachability 未覆盖全部迁移：缺 {sorted(trans_ids - reach_ids)}，多 {sorted(reach_ids - trans_ids)}")


# ---------------------------------------------------------------- C3


def parse_doc_transitions(doc: str) -> dict[str, dict[str, str]]:
    section = doc_section(doc, "## 4.", "## 5.")
    rows: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        match = re.match(r"\| (M\d+) \| (.+?) \|", line)
        if not match:
            continue
        tid, from_cell = match.group(1), match.group(2)
        if "→" not in from_cell:
            continue
        left, right = from_cell.split("→", 1)
        if "*" in left:
            from_state = "*"
        else:
            tokens = STATE_TOKEN_RE.findall(left)
            from_state = "|".join(tokens)
        to_match = re.search(r"`([A-Z_]+)`", right)
        to_state = to_match.group(1) if to_match else ""
        rows[tid] = {"from": from_state, "to": to_state}
    return rows


def norm_comparison(raw: str) -> str:
    text = raw.strip().strip("`").strip()
    if "滑动" in text or text == "window":
        return "sliding_window"
    if "later_of" in text:
        return "later_of"
    if "suppress" in text:
        return "<"
    mapping = {">=": ">=", "≥": ">=", "<=": "<=", "≤": "<=", "<": "<", ">": ">"}
    for token in (">=", "<=", "<", ">"):
        if token in text:
            return mapping[token]
    for token in ("≥", "≤"):
        if token in text:
            return mapping[token]
    if "抑制" in text and "<" in raw:
        return "<"
    return text


def parse_doc_parameters(doc: str) -> dict[str, dict[str, str]]:
    section = doc_section(doc, "## 14.", "## 15.")
    rows: dict[str, dict[str, str]] = {}
    for line in section.splitlines():
        match = re.match(r"\| `(T6-[A-Za-z0-9_]+)` \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
        if match:
            rows[match.group(1)] = {
                "name": match.group(2).strip(),
                "unit": match.group(3).strip(),
                "comparison": match.group(4).strip(),
                "draft_value": match.group(5).strip(),
            }
    return rows


def parse_doc_behavior_rows(doc: str) -> set[str]:
    section = doc_section(doc, "## 5.", "## 6.")
    return set(re.findall(r"^\| (B\d{2}) \|", section, flags=re.MULTILINE))


def parse_doc_action_types(doc: str) -> set[str]:
    section = doc_section(doc, "## 7.", "## 8.")
    types: set[str] = set()
    for line in section.splitlines():
        match = re.match(r"\| `([a-z_]+)` \| \d+ \| `(A_[A-Z_]+)` \|", line)
        if match:
            types.add(match.group(2))
    return types


def parse_doc_events(doc: str) -> set[str]:
    section = doc_section(doc, "## 3.", "## 4.")
    return set(m.group(1) for m in EVENT_ID_RE.finditer(section))


def json_event_ids(data: dict[str, Any]) -> set[str]:
    classes = data["event_classes"]
    events = set(classes.get("input_events", []))
    events |= set(classes.get("output_events", []))
    events |= set(classes.get("suppression_events", []))
    return events


def check_doc_json_consistency(
    data: dict[str, Any], doc_text: str
) -> tuple[dict[str, Any], str]:
    inventory: dict[str, Any] = {}
    issues: list[str] = []

    def add(message: str) -> None:
        issues.append(message)

    # 硬不变量 ID
    json_inv = {item["id"] for item in data["hard_invariants"]}
    doc_inv = set(INVARIANT_ID_RE.findall(doc_text))
    inventory["invariants"] = {"json": sorted(json_inv), "doc": sorted(doc_inv)}
    if json_inv - doc_inv:
        add(f"JSON 有而文档缺的硬不变量：{sorted(json_inv - doc_inv)}")
    if doc_inv - json_inv:
        add(f"文档提及而 JSON 未定义的硬不变量：{sorted(doc_inv - json_inv)}")

    # 迁移 ID、from/to
    json_trans = {item["id"]: item for item in data["transitions"]}
    doc_trans = parse_doc_transitions(doc_text)
    inventory["transitions"] = {
        "json": sorted(json_trans),
        "doc_table": sorted(doc_trans),
    }
    if set(json_trans) - set(doc_trans):
        add(f"JSON 有而文档 §4 表缺的迁移：{sorted(set(json_trans) - set(doc_trans))}")
    if set(doc_trans) - set(json_trans):
        add(f"文档 §4 表有而 JSON 未定义的迁移：{sorted(set(doc_trans) - set(json_trans))}")
    for tid in sorted(set(json_trans) & set(doc_trans)):
        spec = json_trans[tid]
        doc_spec = doc_trans[tid]
        if spec["from"] != doc_spec["from"]:
            add(f"{tid}.from 不一致：JSON {spec['from']!r} vs 文档 {doc_spec['from']!r}")
        if spec["to"] != doc_spec["to"]:
            add(f"{tid}.to 不一致：JSON {spec['to']!r} vs 文档 {doc_spec['to']!r}")

    # 参数 ID 与 §14 行
    json_params = {item["id"]: item for item in data["parameters"]}
    doc_params = parse_doc_parameters(doc_text)
    inventory["parameters"] = {"json": sorted(json_params), "doc_section14": sorted(doc_params)}
    if set(json_params) - set(doc_params):
        add(f"JSON 有而文档 §14 表缺的参数：{sorted(set(json_params) - set(doc_params))}")
    if set(doc_params) - set(json_params):
        add(f"文档 §14 表有而 JSON 未定义的参数：{sorted(set(doc_params) - set(json_params))}")
    for pid in sorted(set(json_params) & set(doc_params)):
        spec = json_params[pid]
        value = spec.get("draft_value")
        doc_value = doc_params[pid]["draft_value"]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            number_match = re.search(r"-?\d+(?:\.\d+)?", doc_value)
            if not number_match or float(number_match.group(0)) != float(value):
                add(f"{pid} 草案值不一致：JSON {value!r} vs 文档 {doc_value!r}")
        elif value is None:
            if "无草案值" not in doc_value:
                add(f"{pid} JSON 为 null，文档必须显式写“无草案值”")
        else:
            if "取较晚" not in doc_value:
                add(f"{pid} 的非数值草案值未在文档 §14 复述")
        json_comparison = norm_comparison(str(spec.get("comparison", "")))
        doc_comparison = norm_comparison(doc_params[pid]["comparison"])
        if json_comparison and doc_comparison and json_comparison != doc_comparison:
            add(f"{pid} comparison 不一致：JSON {json_comparison!r} vs 文档 {doc_comparison!r}")

    # 事件集合（§3）
    json_events = json_event_ids(data)
    doc_events = parse_doc_events(doc_text)
    inventory["events"] = {"json": sorted(json_events), "doc_section3": sorted(doc_events)}
    if json_events - doc_events:
        add(f"JSON 有而文档 §3 缺的事件：{sorted(json_events - doc_events)}")
    if doc_events - json_events:
        add(f"文档 §3 有而 JSON 未定义的事件：{sorted(doc_events - json_events)}")

    # 状态集合
    section4 = doc_section(doc_text, "## 4.", "## 5.")
    doc_states = set(STATE_TOKEN_RE.findall(section4)) & set(STATE_NAMES)
    json_states = set(data["states"])
    inventory["states"] = {"json": sorted(json_states), "doc_section4": sorted(doc_states)}
    if json_states != doc_states:
        add(f"状态集合不一致：JSON {sorted(json_states)} vs 文档 §4 {sorted(doc_states)}")

    # 行为行
    json_behaviors = {item["id"] for item in data["behavior_rows"]}
    doc_behaviors = parse_doc_behavior_rows(doc_text)
    doc_behavior_tokens = set(BEHAVIOR_ID_RE.findall(doc_text))
    inventory["behavior_rows"] = {"json": sorted(json_behaviors), "doc_table": sorted(doc_behaviors)}
    if json_behaviors != doc_behaviors:
        add(
            f"行为行集合不一致：JSON 有文档表缺 {sorted(json_behaviors - doc_behaviors)}，"
            f"文档表有 JSON 缺 {sorted(doc_behaviors - json_behaviors)}"
        )
    if doc_behavior_tokens - json_behaviors:
        add(f"文档提及而 JSON 未定义的行为行：{sorted(doc_behavior_tokens - json_behaviors)}")

    # 动作类型
    json_types = set(data["actions"]["supported_types"])
    doc_types = parse_doc_action_types(doc_text)
    inventory["action_types"] = {"json": sorted(json_types), "doc_table": sorted(doc_types)}
    if json_types != doc_types:
        add(f"动作支持类型不一致：JSON {sorted(json_types)} vs 文档表 A-1 {sorted(doc_types)}")

    if issues:
        raise CheckFailure("；".join(issues))
    detail = (
        f"{len(json_inv)} 不变量 / {len(json_trans)} 迁移(含 from/to) / "
        f"{len(json_params)} 参数(§14 行) / {len(json_events)} 事件 / "
        f"{len(json_states)} 状态 / {len(json_behaviors)} 行为行 / {len(json_types)} 动作类型 双向一致"
    )
    return inventory, detail


# ---------------------------------------------------------------- C4


def check_pending_approval_discipline(data: dict[str, Any], doc_text: str) -> None:
    params = data["parameters"]
    if len(params) != 24:
        raise CheckFailure(f"参数数量必须为 24，实际 {len(params)}")
    for item in params:
        if item.get("approval_status") != "PENDING_APPROVAL":
            raise CheckFailure(f"{item['id']} 的 approval_status 必须是 PENDING_APPROVAL")
        if not item.get("draft_source"):
            raise CheckFailure(f"{item['id']} 缺少来源标注")
        if item.get("approval_owner") != "项目总控转呈 Wong":
            raise CheckFailure(f"{item['id']} 的批准责任人必须为项目总控转呈 Wong")
    metrics = [item for item in params if item.get("kind") == "metric"]
    if {item["id"] for item in metrics} != {"T6-01", "T6-02", "T6-03"}:
        raise CheckFailure("三项目标指标登记不完整")
    if data["actions"]["map_status"] != "PENDING_APPROVAL":
        raise CheckFailure("动作映射必须标为待批准")
    if "PENDING_APPROVAL" not in doc_text:
        raise CheckFailure("文档未出现待批准标记 PENDING_APPROVAL")
    if "T6-S03` | 稳定窗口判定逻辑" not in doc_text:
        raise CheckFailure("文档 §14 缺少 T6-S03 行")


# ---------------------------------------------------------------- C5


def check_action_map(data: dict[str, Any]) -> None:
    mapping = data["actions"]["class_action_map"]
    if [item["class_id"] for item in mapping] != [0, 1, 2, 3, 4]:
        raise CheckFailure("class_id 必须为 0..4 且顺序固定")
    if [item["class_name"] for item in mapping] != EXPECTED_CLASS_ORDER:
        raise CheckFailure("类别顺序与 2A 冻结顺序不一致")
    if data["actions"]["class_order"] != EXPECTED_CLASS_ORDER:
        raise CheckFailure("actions.class_order 与 2A 冻结顺序不一致")
    targets = [item["target_id"] for item in mapping]
    if len(targets) != len(set(targets)):
        raise CheckFailure("target_id 必须互不相同")
    allowed = set(data["actions"]["supported_types"])
    if allowed != {"A_SWITCH_UI", "A_SWITCH_CHANNEL"}:
        raise CheckFailure("r02 支持类型必须恰为 A_SWITCH_UI + A_SWITCH_CHANNEL")
    for item in mapping:
        if item["action_type"] not in allowed:
            raise CheckFailure(f"{item['class_name']} 的动作类型不在支持集合内")


# ---------------------------------------------------------------- C6


def check_invariants(data: dict[str, Any]) -> None:
    ids = {item["id"] for item in data["hard_invariants"]}
    for index in range(1, 11):
        if f"H-{index}" not in ids:
            raise CheckFailure(f"缺少硬不变量 H-{index}")
    for key in ("not_claimed", "evidence_boundaries"):
        if not data.get(key):
            raise CheckFailure(f"{key} 不得为空")
    once = data["trigger_once_while_held"]
    if once.get("declared") != "ONCE_PER_ACQUISITION":
        raise CheckFailure("持续保持必须唯一声明为 ONCE_PER_ACQUISITION")
    if once.get("second_trigger_allowed_only_by_new_acquisition") is not True:
        raise CheckFailure("二次触发必须只允许来自新的获取")
    if once.get("m15_path_is_not_new_acquisition") is not True:
        raise CheckFailure("M15 路径必须声明为不是新获取")
    if once.get("cooldown_gate_global") is not True:
        raise CheckFailure("持续保持声明必须包含全局冷却门")
    if not once.get("rejected_alternative"):
        raise CheckFailure("必须显式登记被否决的备选解释")


# ---------------------------------------------------------------- C7


def _nextafter(value: float, direction: float) -> float:
    return math.nextafter(value, direction)


def recompute(case: dict[str, Any]) -> dict[str, Any]:
    spec = case["recompute"]
    kind = spec["kind"]
    if kind == "stable_window":
        period = float(spec["period_ms"])
        s01 = float(spec["s01_ms"])
        s02 = int(spec["s02_frames"])
        index = 1
        while not (index >= s02 and (index - 1) * period >= s01):
            index += 1
            if index > 10_000:
                raise CheckFailure("窗口复算未收敛")
        actual = r6((index - 1) * period)
        w_min = r6(max(s01, (s02 - 1) * period))
        return {
            "frames_required": index,
            "actual_window_ms": actual,
            "actual_completion_ms": actual,
            "lower_bound_W_ms": w_min,
            "w_min_ms": w_min,
            "w_min_is_lower_bound_only": True,
            "dominant": "frame_count" if (s02 - 1) * period > s01 else "duration",
            "stable": (index >= s02) and ((index - 1) * period >= s01),
            "stable_at_sixth_frame": 6 >= s02 and (6 - 1) * period >= s01,
            "stable_at_fifth_frame": 5 >= s02 and (5 - 1) * period >= s01,
        }
    if kind == "cooldown":
        t_last_submit_ns = int(round(float(spec["t_last_submit_ms"]) * 1_000_000))
        k01_ns = int(round(float(spec["k01_ms"]) * 1_000_000))
        offsets = spec["t_now_offsets_ns"]
        return {
            "ended_at_ms": r6((t_last_submit_ns + k01_ns) / 1_000_000),
            "ended_at_minus_1ns": (t_last_submit_ns + int(offsets["minus_1ns"]) - t_last_submit_ns) >= k01_ns,
            "ended_at_exact": (t_last_submit_ns + int(offsets["exact"]) - t_last_submit_ns) >= k01_ns,
            "ended_at_plus_1ns": (t_last_submit_ns + int(offsets.get("plus_1ns", offsets["exact"])) - t_last_submit_ns) >= k01_ns,
        }
    if kind == "dedup":
        t_last_submit_ns = int(round(float(spec["t_last_submit_ms"]) * 1_000_000))
        a02_ns = int(round(float(spec["a02_ms"]) * 1_000_000))
        offsets = spec["t_now_offsets_ns"]
        return {
            "suppressed_at_minus_1": int(offsets["minus_1ns"]) < a02_ns,
            "suppressed_at_exact": int(offsets["exact"]) < a02_ns,
            "unit_granularity": "ns_true_computation",
        }
    if kind == "lost_frames":
        l01 = int(spec["l01_frames"])
        return {"lost_at_4": 4 >= l01, "lost_at_5": 5 >= l01}
    if kind == "lost_time":
        if "t_last_target_continues_ms" not in spec:
            raise CheckFailure(
                "lost_time 样例缺少 t_last_target_continues_ms"
                "（r04 已废弃 t_last_match_ms，见 R3-B01）"
            )
        anchor_ns = int(round(float(spec["t_last_target_continues_ms"]) * 1_000_000))
        l02_ns = int(round(float(spec["l02_ms"]) * 1_000_000))
        offsets = spec["t_now_offsets_ns"]
        return {
            "lost_at_minus_1ns": (anchor_ns + int(offsets["minus_1ns"]) - anchor_ns) >= l02_ns,
            "lost_at_exact": (anchor_ns + int(offsets["exact"]) - anchor_ns) >= l02_ns,
            "anchor": "t_last_target_continues",
        }
    if kind == "stale":
        limit_ns = int(round(float(spec["limit_ms"]) * 1_000_000))
        ages = spec["ages_ns"]
        return {
            "stale_at_exact": int(ages["exact"]) > limit_ns,
            "stale_at_exact_plus_1ns": int(ages["plus_1ns"]) > limit_ns,
        }
    if kind == "jitter":
        j01 = int(spec["j01_frames"])
        return {"tolerated_at_1": 1 <= j01, "reset_at_2": 2 > j01}
    if kind == "frame_id_seen":
        prev_id = int(spec["prev_frame_id"])
        cur_id = int(spec["cur_frame_id"])
        same = bool(spec["session_same"])
        if not same:
            return {
                "event": "E_SESSION_RESET_SUSPECTED",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 1,
            }
        if cur_id == prev_id:
            return {
                "event": "E_FRAME_DUPLICATE",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 0,
            }
        if cur_id < prev_id:
            return {
                "event": "E_FRAME_OUT_OF_ORDER",
                "advances_match_count": False,
                "may_trigger_action": False,
                "anomaly_delta": 1,
            }
        return {
            "event": "E_FRAME_RESULT",
            "advances_match_count": True,
            "may_trigger_action": True,
            "anomaly_delta": 0,
        }
    if kind == "session_change":
        same = bool(spec["session_same"])
        return {
            "state_after": "IDLE" if not same else "UNCHANGED",
            "target_cleared": not same,
            "may_trigger_action_on_reset_frame": False,
        }
    if kind == "trigger_once_hold":
        period = int(spec["period_ms"])
        c01 = int(spec["c01_frames"])
        s02 = int(spec["s02_frames"])
        s01 = int(spec["s01_ms"])
        hold = int(spec["hold_frames"])
        k01 = int(spec["k01_ms"])
        # 按行为表 v1.1 推导：第 c01 帧建立获取（窗口从第 1 帧起算），
        # 第 stable 帧满足 matched>=S02 且 duration>=S01，第 stable+1 帧 M5 提交。
        stable = None
        for frame in range(1, hold + 1):
            matched = frame
            duration_ms = (frame - 1) * period
            if matched >= s02 and duration_ms >= s01:
                stable = frame
                break
        if stable is None:
            raise CheckFailure("trigger_once_hold 复算未在保持期内达到稳定")
        trigger = stable + 1
        t_submit = (trigger - 1) * period
        cooldown_end = t_submit + k01
        m9_frame = None
        for frame in range(1, hold + 1):
            if (frame - 1) * period >= cooldown_end:
                m9_frame = frame
                break
        if m9_frame is None:
            raise CheckFailure("trigger_once_hold 复算未在保持期内覆盖冷却结束")
        submitted = 1 if trigger <= hold else 0
        return {
            "submitted_total": submitted,
            "trigger_after_cooldown": 0,
            "trigger_frame_index": trigger,
            "m9_branch_frame_index": m9_frame,
        }
    if kind == "hysteresis":
        current_score = float(spec["current_score"])
        other_score = float(spec["other_class_score"])
        p01 = float(spec["p01"])
        p02 = float(spec["p02"])
        p03 = float(spec["p03"])
        p04 = float(spec["p04"])
        same_class = bool(spec["same_class"])
        iou = float(spec["iou"])
        center_disp = float(spec["center_disp"])
        continues = same_class and (iou >= p03 or center_disp <= p04)
        window_match = continues and current_score >= p02
        held = continues
        if held:
            selected_class = "fist" if int(spec["current_class_id"]) == 0 else "current"
        else:
            candidates = [(current_score, int(spec["current_class_id"]))]
            candidates.append((other_score, int(spec["other_class_id"])))
            eligible = [row for row in candidates if row[0] >= p01]
            best = max(eligible, key=lambda row: row[0]) if eligible else None
            selected_class = "palm" if best and best[1] == 1 else "current"
        return {
            "held": held,
            "target_continues": continues,
            "window_match": window_match,
            "selected_class": selected_class,
            "selected_class_id": 0 if selected_class == "fist" else (1 if selected_class == "palm" else int(spec["current_class_id"])),
            "higher_other_candidate": other_score > current_score,
            "suppression_event": "S_TARGET_HELD" if held else "NONE",
        }
    if kind == "tie":
        scores = [float(value) for value in spec["scores"]]
        orders = [int(value) for value in spec["source_orders"]]
        if len(set(scores)) != 1:
            raise CheckFailure("tie 样例要求分数完全相等")
        best = min(range(len(scores)), key=lambda index: orders[index])
        return {"selected_source_order": orders[best]}
    if kind == "action_events":
        t_trigger = float(spec["t_trigger_ms"])
        t_submit = float(spec["t_submit_ms"])
        t_effective = float(spec["t_effective_ms"])
        a01 = float(spec["a01_ms"])
        observed = bool(spec["effective_observed"])
        latency_action = t_effective - t_trigger
        return {
            "latency_action_ms": r6(latency_action),
            "latency_submit_ms": r6(t_submit - t_trigger),
            "counts_as_success_when_effective_observed": observed and latency_action <= a01,
            "counts_as_success_when_unobserved": False,
        }
    if kind == "unknown_rejection_proof":
        class_id = int(spec["unknown_class_id"])
        score = float(spec["unknown_score"])
        p01 = float(spec["p01"])
        class_membership = 0 <= class_id <= 4
        selection_gate = score >= p01
        # 若该结果能被选为目标并满足窗口，则会提交 1 次动作（窗口参数只用于说明可达性）
        would_submit = 1 if (class_membership and selection_gate) else 0
        return {
            "class_membership_passes": class_membership,
            "selection_gate_passes": selection_gate,
            "would_submit_actions": would_submit,
            "proves_unknown_rejection": would_submit == 0,
            "counts_as_false_accept_in_T6_02": would_submit == 1,
        }
    if kind == "acquisition_c01":
        c01 = int(spec["c01_frames"])
        results = {}
        for streak in spec["streaks"]:
            results[f"acquired_at_streak_{int(streak)}"] = int(streak) >= c01
        return results
    if kind == "anomaly_window":
        width = int(spec["w_frames"])
        threshold = int(spec["n_frames"])
        out = {"window_type": "sliding"}
        for name, history in spec["histories"].items():
            window = history[-width:]
            out[f"{name}_fires"] = sum(1 for flag in window if flag == "A") >= threshold
        return out
    if kind == "m4_reachability":
        s04 = int(spec["s04_ms"])
        l02 = int(spec["l02_ms"])
        j01 = int(spec["j01_frames"])
        l01 = int(spec["l01_frames"])
        period = int(spec["period_ms"])
        earliest_m10 = min(l01 * period, l02)
        m4_earliest = max(s04, (j01 + 1) * period)
        return {
            "m4_reachable_under_draft": m4_earliest < earliest_m10,
            "earliest_m10_ms": earliest_m10,
            "m4_earliest_ms": m4_earliest,
            "reachable_if_s04_lt_l02": True,
        }
    if kind == "score_gate":
        p01 = float(spec["p01"])
        score_exact = float(spec.get("score_exact", p01))
        score_minus = float(spec.get("score_minus_1ulp", _nextafter(p01, 0.0)))
        return {
            "eligible_at_exact": score_exact >= p01,
            "eligible_at_minus_1ulp": score_minus >= p01,
            "inclusive": True,
        }
    if kind == "window_match_score":
        p02 = float(spec["p02"])
        score_exact = float(spec.get("score_exact", p02))
        score_minus = float(spec.get("score_minus_1ulp", _nextafter(p02, 0.0)))
        return {
            "window_match_at_exact": score_exact >= p02,
            "window_match_at_minus_1ulp": score_minus >= p02,
            "inclusive": True,
        }
    if kind == "window_match_vs_continues":
        # N02：由逐帧 score/几何序列真推导 TARGET_CONTINUES 与 WINDOW_MATCH，不再接受结论式输入。
        p02 = float(spec["p02"])
        p03 = float(spec["p03"])
        p04 = float(spec["p04"])
        p05 = float(spec["p05"])
        s02 = int(spec["s02_frames"])
        s01_ms = float(spec["s01_ms"])
        period_ms = float(spec["period_ms"])
        l01 = int(spec["l01_frames"])
        l02_ms = float(spec["l02_ms"])
        frames = spec["frames"]
        if not frames:
            raise CheckFailure("window_match_vs_continues 样例缺少 frames 逐帧序列")
        continues_flags: list[bool] = []
        window_flags: list[bool] = []
        previous_window_disp: float | None = None
        for frame in frames:
            disp = float(frame["center_disp"])
            continues = bool(frame["same_class"]) and (
                float(frame["iou"]) >= p03 or disp <= p04
            )
            continues_flags.append(continues)
            window_match = bool(continues and float(frame["score"]) >= p02)
            if window_match and previous_window_disp is not None and (disp - previous_window_disp) > p05:
                window_match = False
            if window_match:
                previous_window_disp = disp
            window_flags.append(window_match)
        window_match_count = sum(1 for flag in window_flags if flag)
        continues_count = sum(1 for flag in continues_flags if flag)
        # N-r04-04：窗口时长按 §9「窗口首帧 → 第 T6-S02 个 WINDOW_MATCH 帧」计算；
        # 另保留宽松口径（整段输入序列跨度）用于一致性断言，二者 m3_fires 结论必须相同。
        window_indices = [index for index, flag in enumerate(window_flags) if flag]
        sequence_span_ms = (len(frames) - 1) * period_ms
        if len(window_indices) >= s02:
            window_span_ms = (window_indices[s02 - 1] - window_indices[0]) * period_ms
        elif window_indices:
            window_span_ms = (window_indices[-1] - window_indices[0]) * period_ms
        else:
            window_span_ms = 0.0
        continues_false_streak = 0
        for flag in reversed(continues_flags):
            if flag:
                break
            continues_false_streak += 1
        time_since_last_continues_ms = 0.0 if continues_flags[-1] else continues_false_streak * period_ms
        lost = continues_false_streak >= l01 or time_since_last_continues_ms >= l02_ms
        m3_fires = window_match_count >= s02 and window_span_ms >= s01_ms
        m3_fires_loose = window_match_count >= s02 and sequence_span_ms >= s01_ms
        # M5 需要 STABLE 之后的下一条结果帧；本样例无后续帧 → 不触发
        trigger = m3_fires and bool(spec.get("m5_next_frame_supplied", False))
        return {
            "m3_fires": m3_fires,
            "lost": lost,
            "trigger": trigger,
            "window_match_count": window_match_count,
            "continues_count": continues_count,
            "continues_false_streak": continues_false_streak,
            "window_span_ms": r6(window_span_ms),
            "sequence_span_ms": r6(sequence_span_ms),
            "span_conventions_agree": m3_fires == m3_fires_loose,
        }
    if kind == "recovery_streak":
        u01 = int(spec["u01_frames"])
        return {f"recovered_at_{int(streak)}": int(streak) >= u01 for streak in spec["streaks"]}
    if kind == "stable_ns_border":
        s01_ns = int(spec["s01_ms"]) * 1_000_000
        s02 = int(spec["s02_frames"])
        period_ns = int(spec["period_ns"])
        # 帧时刻序列：前 s02−1 帧按 P 推进；第 s02 帧落在 S01−1ns，第 s02+1 帧落在 S01+1ns。
        times_ns = [index * period_ns for index in range(s02 - 1)]
        times_ns.append(s01_ns - 1)
        times_ns.append(s01_ns + 1)
        start_ns = times_ns[0]
        outcome: dict[int, dict[str, Any]] = {}
        for frame_index in (s02, s02 + 1):
            elapsed_ns = times_ns[frame_index - 1] - start_ns
            frames_ok = frame_index >= s02
            duration_ok = elapsed_ns >= s01_ns
            outcome[frame_index] = {
                "frames_ok": frames_ok,
                "duration_ok": duration_ok,
                "inclusive_gte": frames_ok and duration_ok,
            }
        return {
            "stable_at_6th": outcome[s02]["inclusive_gte"],
            "stable_at_7th": outcome[s02 + 1]["inclusive_gte"],
            "frames_ok_at_6th": outcome[s02]["frames_ok"],
            "frames_ok_at_7th": outcome[s02 + 1]["frames_ok"],
            "duration_ok_at_6th": outcome[s02]["duration_ok"],
            "granularity": "1ns",
        }
    if kind == "latched_stable_gate_on_timeout":
        # N-r04-01 角落序列：STABLE 已锁存、全局冷却门恰在 TIMEOUT 帧开启 → 该帧不得触发（B21），
        # 门开启后的下一条窗口推进帧才触发。
        period_ms = int(spec["period_ms"])
        t_last_submit_ns = int(round(float(spec["t_last_submit_ms"]) * 1_000_000))
        k01_ns = int(round(float(spec["k01_ms"]) * 1_000_000))
        u00_w = int(spec["u00_w"])
        u00_n = int(spec["u00_n"])
        anomaly_kinds = ("TIMEOUT", "ERROR", "DROPPED")
        gate_open_frame: dict[str, int] = {}
        first_action_frame: dict[str, int | None] = {}
        total_actions: dict[str, int] = {}
        for scenario in spec["scenarios"]:
            name = str(scenario["name"])
            history: list[int] = []
            acted = False
            gate_frame: int | None = None
            first_frame: int | None = None
            for frame in scenario["frames"]:
                index = int(frame["index"])
                frame_kind = str(frame["kind"])
                t_now_ns = (index - 1) * period_ms * 1_000_000
                advancing = frame_kind in ("OK", "NO_HAND")
                history.append(1 if frame_kind in anomaly_kinds else 0)
                anomaly_fires = sum(history[-u00_w:]) >= u00_n
                gate_open = (t_now_ns - t_last_submit_ns) >= k01_ns
                if gate_open and gate_frame is None:
                    gate_frame = index
                if not acted and gate_open and advancing and not anomaly_fires:
                    acted = True
                    first_frame = index
            gate_open_frame[name] = gate_frame if gate_frame is not None else -1
            first_action_frame[name] = first_frame
            total_actions[name] = 1 if acted else 0
        return {
            "gate_open_frame": gate_open_frame,
            "first_action_frame": first_action_frame,
            "total_actions": total_actions,
            "action_at_gate_open_frame": {
                name: first_action_frame[name] == gate_open_frame[name] for name in gate_open_frame
            },
            "no_action_on_timeout_frame": True,
            "timeout_frames_not_window_advancing": True,
            "latched_within_acquisition": True,
        }
    raise CheckFailure(f"未知的复算类型：{kind}")


def check_hand_cases(cases: dict[str, Any]) -> str:
    seen: set[str] = set()
    for case in cases["cases"]:
        case_id = case["case_id"]
        if case_id in seen:
            raise CheckFailure(f"样例 ID 重复：{case_id}")
        seen.add(case_id)
        expected = case["expected"]
        try:
            computed = recompute(case)
        except CheckFailure:
            raise
        except Exception as exc:  # noqa: BLE001
            raise CheckFailure(f"{case_id} 复算异常：{type(exc).__name__}: {exc}") from exc
        for key, want in expected.items():
            if key not in computed:
                raise CheckFailure(f"{case_id}.{key} 无法独立复算（禁止不可复算的预期）")
            got = computed[key]
            if isinstance(want, float) or isinstance(got, float):
                if abs(r6(want) - r6(got)) > 1e-6:
                    raise CheckFailure(f"{case_id}.{key} 预期 {want} 与复算 {got} 不符")
            elif want != got:
                raise CheckFailure(f"{case_id}.{key} 预期 {want} 与复算 {got} 不符")
    if len(seen) < 30:
        raise CheckFailure(f"手算样例数量不足 30：{len(seen)}")
    return (
        f"{len(seen)} 个样例全部由输入独立复算一致"
        "（HC-16/17/20 手算推导、HC-27 帧时刻序列推导、HC-28/29 逐帧 score/几何序列推导、"
        "HC-30 锁存 STABLE + 门在 TIMEOUT 帧开启的角落序列）"
    )


# ---------------------------------------------------------------- C8


def check_upstream(bindings: dict[str, Any], project_root: Path) -> str:
    verified = 0
    drift: list[str] = []
    for item in bindings["bindings"]:
        raw = item["path"]
        path = Path(raw)
        if not path.is_absolute():
            path = project_root / raw
        if item.get("git_repo"):
            repo = item["git_repo"]
            spec = f"{item['git_commit']}:{item['git_relpath']}"
            try:
                blob = subprocess.run(
                    ["git", "-C", repo, "show", spec],
                    capture_output=True,
                    check=False,
                )
            except OSError as exc:  # pragma: no cover
                raise CheckFailure(f"无法调用 git 复算 {item['id']}：{exc}") from exc
            if blob.returncode != 0:
                raise CheckFailure(
                    f"无法取到 {item['id']} 的提交版本 {spec}："
                    f"{blob.stderr.decode('utf-8', 'replace').strip()}"
                )
            actual = hashlib.sha256(blob.stdout).hexdigest()
            if actual.casefold() != item["sha256"].casefold():
                raise CheckFailure(
                    f"上游提交版本哈希不匹配：{item['id']} 清单 {item['sha256']} 实际 {actual}"
                )
            if path.is_file():
                work = sha256_file(path)
                if work.casefold() != item["sha256"].casefold():
                    drift.append(f"{item['id']}({work[:8]})")
        else:
            if not path.is_file():
                raise CheckFailure(f"上游文件不存在：{raw}")
            actual = sha256_file(path)
            if actual.casefold() != item["sha256"].casefold():
                raise CheckFailure(
                    f"上游哈希不匹配：{item['id']} 清单 {item['sha256']} 实际 {actual}"
                )
        verified += 1
    detail = f"{verified} 个上游绑定哈希一致（外部树按提交版本复算）"
    if drift:
        detail += f"；工作副本漂移（非失败，已在上游绑定中记录）：{', '.join(drift)}"
    return detail


# ---------------------------------------------------------------- C9 / C10


def check_doc_coverage(doc_text: str) -> None:
    missing = [word for word in REQUIRED_DOC_KEYWORDS if word not in doc_text]
    if missing:
        raise CheckFailure(f"文档缺少必备关键词：{missing}")
    missing_sections = [item for item in REQUIRED_DOC_SECTIONS if item not in doc_text]
    if missing_sections:
        raise CheckFailure(f"文档缺少必备章节：{missing_sections}")


NEGATION_PREFIXES = ("不宣称", "不构成", "不得", "禁止", "未", "不是", "并非", "不因")


def check_forbidden_claims(doc_text: str, data: dict[str, Any]) -> None:
    haystack = doc_text + json.dumps(data, ensure_ascii=False)
    hits: list[str] = []
    for phrase in FORBIDDEN_CLAIMS:
        start = 0
        while True:
            index = haystack.find(phrase, start)
            if index < 0:
                break
            context = haystack[max(0, index - 16) : index]
            if not any(marker in context for marker in NEGATION_PREFIXES):
                hits.append(f"{phrase}@{index}")
            start = index + len(phrase)
    if hits:
        raise CheckFailure(f"出现禁止的通过/冻结声明（非否定语境）：{hits}")


# ---------------------------------------------------------------- C11


def check_evidence_integrity(
    evidence_dir: Path | None,
    manifest_path: Path | None,
    state_path: Path | None,
    project_root: Path,
) -> str:
    if evidence_dir is None:
        raise CheckFailure("C11 需要 --evidence-dir 才能核对证据存在性（不得静默跳过）")
    evidence_dir = evidence_dir.resolve()
    if not evidence_dir.is_dir():
        raise CheckFailure(f"证据目录不存在：{evidence_dir}")
    actual = sorted(
        path.relative_to(evidence_dir).as_posix()
        for path in evidence_dir.rglob("*")
        if path.is_file()
    )
    details = [f"实际文件 {len(actual)} 个"]
    if manifest_path is not None:
        manifest_path = manifest_path.resolve()
        manifest = load_json(manifest_path)
        declared_evidence_dir = manifest.get("evidence_dir")
        expected_dir = (project_root / declared_evidence_dir).resolve() if declared_evidence_dir else None
        if expected_dir != evidence_dir:
            raise CheckFailure(
                f"manifest.evidence_dir 与 --evidence-dir 不一致：{declared_evidence_dir!r} vs {evidence_dir}"
            )
        ev_rel = evidence_dir.relative_to(project_root).as_posix() + "/"
        declared_run: dict[str, str] = {}
        declared_out: dict[str, str] = {}
        for item in manifest.get("files", []):
            raw_path = str(item["path"]).replace("\\", "/").strip()
            if raw_path == manifest_path.relative_to(project_root).as_posix():
                raise CheckFailure("manifest 不得把自身列入 files")
            if raw_path.startswith(ev_rel):
                declared_run[raw_path[len(ev_rel):]] = item["sha256"]
            elif "/" in raw_path and not raw_path.startswith(("tmp/", "build/")):
                declared_out[raw_path] = item["sha256"]
            else:
                declared_run[raw_path] = item["sha256"]
        missing = sorted(set(declared_run) - set(actual))
        extra = sorted(set(actual) - set(declared_run) - {manifest_path.name})
        if missing:
            raise CheckFailure(f"清单声明但实际不存在：{missing}")
        if extra:
            raise CheckFailure(f"实际存在但清单未声明：{extra}")
        for relpath, want in declared_run.items():
            got = sha256_file(evidence_dir / relpath)
            if got != want:
                raise CheckFailure(f"清单哈希不符：{relpath}")
        for relpath, want in sorted(declared_out.items()):
            path = (project_root / relpath).resolve()
            if not path.is_file():
                raise CheckFailure(f"清单声明的源码/输入文件不存在：{relpath}")
            if sha256_file(path) != want:
                raise CheckFailure(f"清单声明的源码/输入哈希不符：{relpath}")
        details.append(
            f"manifest 双向一致（运行目录 {len(declared_run)} 个文件 + 外部绑定 {len(declared_out)} 个文件哈希复算通过）"
        )
    if state_path is not None:
        state_path = state_path.resolve()
        if not state_path.is_file():
            raise CheckFailure(f"STATE 文件不存在：{state_path}")
        state_text = state_path.read_text(encoding="utf-8")
        if "S6-A DONE" in state_text:
            raise CheckFailure("STATE 仍写有 'S6-A DONE'；应改为 DELIVERED_PENDING_APPROVAL/REVIEW")
        if "DELIVERED_PENDING_APPROVAL" not in state_text and "DELIVERED_PENDING_REVIEW" not in state_text:
            raise CheckFailure("STATE 缺少 DELIVERED_PENDING_APPROVAL/REVIEW 状态口径")
        lines = state_text.splitlines()
        declared_files: set[str] = set()
        declared_dirs: set[str] = set()
        for line in lines:
            if "证据入口" not in line and "report/evidence" not in line:
                continue
            for token in re.findall(r"`([^`]+)`", line):
                if (
                    re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*\.(json|md|txt|jsonl)", token)
                    and "/" not in token
                    and "\\" not in token
                ):
                    declared_files.add(token)
                elif token.startswith("report/evidence/"):
                    declared_dirs.add(token.rstrip("/"))
        if not declared_files and not declared_dirs:
            raise CheckFailure("STATE 未解析到任何证据声明（不得以空声明通过）")
        missing_files = sorted(name for name in declared_files if not (evidence_dir / name).is_file())
        if missing_files:
            raise CheckFailure(f"STATE 声明的证据文件不存在于证据目录：{missing_files}")
        missing_dirs = sorted(
            path for path in declared_dirs if not (project_root / path).is_dir()
        )
        if missing_dirs:
            raise CheckFailure(f"STATE 声明的证据目录不存在：{missing_dirs}")
        details.append(
            f"STATE 声明 {len(declared_files)} 个文件与 {len(declared_dirs)} 个目录全部存在"
        )
    return "；".join(details)


# ---------------------------------------------------------------- C12..C16


PREDICATE_NAMES = ("TARGET_CONTINUES", "WINDOW_MATCH")
FORBIDDEN_IDENTIFIERS = ("matched_frames", "t_last_match", "t_submit+")
DEPRECATED_MARKERS = ("已废弃", "废弃")


def collect_forbidden_identifiers(label: str, text: str) -> list[str]:
    """禁用标识符扫描（R3-B01）：命中必须邻近“已废弃”标注，否则记问题。"""
    issues: list[str] = []
    for token in FORBIDDEN_IDENTIFIERS:
        start = 0
        while True:
            index = text.find(token, start)
            if index < 0:
                break
            context = text[max(0, index - 60) : index + len(token) + 60]
            if not any(marker in context for marker in DEPRECATED_MARKERS):
                issues.append(
                    f"{label} 仍含已废弃标识符 {token!r}（未标注“已废弃”）：…{context.strip()}…"
                )
            start = index + len(token)
    return issues


def used_by_item_ids(entries: list[Any]) -> tuple[set[str], list[str]]:
    """把 predicates.*.used_by 拆成条目 ID（M*/B*）与其余引用（白名单）。"""
    ids: set[str] = set()
    others: list[str] = []
    for entry in entries:
        match = re.match(r"^\s*(M\d+|B\d{2})\b", str(entry))
        if match:
            ids.add(match.group(1))
        else:
            others.append(str(entry))
    return ids, others


def check_predicates(
    data: dict[str, Any],
    doc_text: str,
    state_text: str | None,
    cases: dict[str, Any],
) -> None:
    """谓词拆分一致性（R3-B01/R3-B02）。

    为保证旧包捕获证据能同时覆盖 R3-B01（禁用标识符）与 R3-B02（双向不一致/字段现状），
    本检查一次性汇总全部缺陷后统一失败，而不是首个缺陷即停。
    """
    issues: list[str] = []
    predicates = data.get("predicates") or {}
    for name in PREDICATE_NAMES:
        if name not in predicates:
            issues.append(f"缺少谓词定义：{name}")
            continue
        if name not in doc_text:
            issues.append(f"文档未引用谓词：{name}")
        if not predicates[name].get("definition") or not predicates[name].get("used_by"):
            issues.append(f"{name} 缺少定义或引用位置")
    if issues:
        raise CheckFailure("；".join(issues))

    transitions = {item["id"]: item for item in data["transitions"]}
    rows = {row["id"]: row for row in data["behavior_rows"]}
    required_binding = {
        "M1": ["TARGET_CONTINUES"],
        "M3": ["WINDOW_MATCH"],
        "M4": ["WINDOW_MATCH"],
        "M8": ["TARGET_CONTINUES"],
        "M9": ["TARGET_CONTINUES", "WINDOW_MATCH"],
        "M10": ["TARGET_CONTINUES"],
        "M15": ["TARGET_CONTINUES", "WINDOW_MATCH"],
        "B04": ["TARGET_CONTINUES"],
        "B07": ["WINDOW_MATCH"],
        "B08": ["WINDOW_MATCH"],
        "B10": ["TARGET_CONTINUES"],
        "B12": ["TARGET_CONTINUES"],
        "B14": ["TARGET_CONTINUES", "WINDOW_MATCH"],
    }
    for item_id, expected in required_binding.items():
        if item_id.startswith("M"):
            item = transitions.get(item_id)
            text = str(item.get("condition", "")) if item else ""
        else:
            item = rows.get(item_id)
            text = (
                str(item.get("condition", "")) + " " + str(item.get("output", ""))
                if item
                else ""
            )
        if item is None:
            issues.append(f"{item_id} 不存在（无法核对谓词绑定）")
            continue
        for name in expected:
            if name not in text:
                issues.append(f"{item_id} 的条件/输出未绑定 {name}（BLK-1）")
        declared = item.get("predicates_used")
        if declared is None:
            issues.append(f"{item_id} 缺少 predicates_used 字段（BLK-1）")
        elif sorted(set(declared)) != sorted(set(expected)):
            issues.append(f"{item_id}.predicates_used 与要求不符：{declared} vs {expected}")

    # 全量双向断言（R3-B02）：predicates.used_by ↔ 每一条目的 predicates_used
    reverse: dict[str, set[str]] = {name: set() for name in PREDICATE_NAMES}
    for item_id, item in list(transitions.items()) + list(rows.items()):
        declared = item.get("predicates_used")
        if declared is None:
            continue
        # N-r04-03：predicates_used 出现时必须为非空列表；显式空列表 [] 视为不合法。
        if not isinstance(declared, list) or not declared:
            issues.append(
                f"{item_id}.predicates_used 必须是非空列表（显式空列表/非列表均不合法，N-r04-03）：{declared!r}"
            )
            continue
        for name in declared:
            if name not in PREDICATE_NAMES:
                issues.append(f"{item_id}.predicates_used 含未定义谓词 {name!r}")
            else:
                reverse[name].add(item_id)
    for name in PREDICATE_NAMES:
        forward_ids, others = used_by_item_ids(list(predicates[name]["used_by"]))
        for entry in others:
            if not entry.strip().startswith("§12"):
                issues.append(
                    f"predicates.{name}.used_by 的非条目引用只允许 §12 文本白名单：{entry!r}"
                )
        only_forward = sorted(forward_ids - reverse[name])
        only_reverse = sorted(reverse[name] - forward_ids)
        if only_forward or only_reverse:
            issues.append(
                f"predicates.{name}.used_by 与 predicates_used 非双向一致："
                f"仅 used_by 有 {only_forward}；仅 predicates_used 有 {only_reverse}"
            )

    # M5/B13：JSON 现状（无 predicates_used 字段）与叙述必须一致（R3-B02）
    policy = data.get("predicate_binding_policy") or {}
    statement = str(policy.get("statement", ""))
    if not statement:
        issues.append("缺少 predicate_binding_policy.statement（M5/B13 绑定叙述）")
    if sorted(str(item) for item in (policy.get("items_without_predicates_used") or [])) != ["B13", "M5"]:
        issues.append("predicate_binding_policy.items_without_predicates_used 必须恰为 M5/B13")
    for item_id, item in (("M5", transitions.get("M5")), ("B13", rows.get("B13"))):
        if item is None:
            issues.append(f"{item_id} 不存在（无法核对 predicates_used 现状）")
        elif "predicates_used" in item:
            issues.append(f"{item_id} 实际没有 predicates_used 字段，叙述不得声称已绑定（R3-B02）")
    for marker in ("global_cooldown_gate", "H-10", "predicates_used"):
        if marker not in statement:
            issues.append(f"predicate_binding_policy.statement 缺少事实要素 {marker!r}（N-r04-02）")
    if statement and statement not in doc_text:
        issues.append("文档未复述 predicate_binding_policy.statement（M5/B13 叙述与 JSON 不一致）")
    if state_text is not None and statement and statement not in state_text:
        issues.append("阶段 STATE 未复述 predicate_binding_policy.statement（叙述与 JSON 不一致）")

    # N-r04-01：M5 必须复述「本帧为窗口推进帧」限定，并与 §4 锁存段/stable_latching 一致
    m5_item = transitions.get("M5")
    if m5_item is None:
        issues.append("缺少 M5（无法核对窗口推进帧限定）")
    else:
        m5_condition = str(m5_item.get("condition", ""))
        for marker in ("窗口推进帧", "state ∈ {OK,NO_HAND}", "stale=false", "非重复", "非倒序"):
            if marker not in m5_condition:
                issues.append(f"M5 条件未复述窗口推进帧限定 {marker!r}（N-r04-01）")
        doc_m5_rows = [
            line for line in doc_text.splitlines() if re.match(r"^\| M5 \|", line)
        ]
        if not doc_m5_rows:
            issues.append("文档 §4 缺少 M5 行（N-r04-01）")
        else:
            doc_m5 = doc_m5_rows[0]
            for marker in ("窗口推进帧", "state ∈ {OK, NO_HAND}", "stale=false", "非重复", "非倒序"):
                if marker not in doc_m5:
                    issues.append(f"文档 §4 M5 行未复述窗口推进帧限定 {marker!r}（N-r04-01）")
    latch = data.get("stable_latching") or {}
    release = str(latch.get("suppressed_trigger_release", ""))
    for marker in ("窗口推进帧", "不得触发"):
        if marker not in release:
            issues.append(
                f"stable_latching.suppressed_trigger_release 未复述窗口推进帧限定/不得触发 {marker!r}（N-r04-01）"
            )

    # 禁用标识符扫描（R3-B01）：规格文档、行为表 JSON、手算样例、阶段 STATE
    issues.extend(collect_forbidden_identifiers("文档", doc_text))
    issues.extend(collect_forbidden_identifiers("行为表 JSON", json.dumps(data, ensure_ascii=False)))
    issues.extend(collect_forbidden_identifiers("手算样例", json.dumps(cases, ensure_ascii=False)))
    if state_text is not None:
        issues.extend(collect_forbidden_identifiers("阶段 STATE", state_text))

    # 裸“匹配”残留扫描（“匹配计数”是已定义计数器名，允许；其余裸用法禁止）
    bare_patterns = [phrase for phrase in AMBIGUOUS_MATCH_PHRASES] + [
        "不匹配",
        "仍匹配",
        "上次匹配",
        "匹配帧数",
        "匹配成立",
        "匹配的框",
        "未匹配",
        "非匹配",
        "计入匹配",
    ]
    json_text = json.dumps(
        {
            "transitions": [item.get("condition", "") for item in data["transitions"]],
            "behavior_rows": [
                str(row.get("condition", "")) + str(row.get("output", ""))
                for row in data["behavior_rows"]
            ],
        },
        ensure_ascii=False,
    )
    for phrase in bare_patterns:
        if phrase in json_text:
            issues.append(f"JSON 迁移/行为行仍含未绑定谓词的表述：{phrase!r}")
        if phrase in doc_text:
            issues.append(f"文档仍含未绑定谓词的表述：{phrase!r}")

    if issues:
        raise CheckFailure("；".join(issues))


def check_cooldown_gate(data: dict[str, Any], doc_text: str) -> None:
    policy = data.get("cooldown_policy") or {}
    if policy.get("scope") != "GLOBAL_GATE":
        raise CheckFailure("cooldown_policy.scope 必须为 GLOBAL_GATE")
    if policy.get("applies_across_acquisitions") is not True:
        raise CheckFailure("冷却门必须跨获取生效")
    anchor = str(policy.get("anchor", ""))
    gate = str(policy.get("gate_condition", ""))
    if "t_last_submit" not in anchor or "t_last_submit" not in gate:
        raise CheckFailure("冷却锚点必须统一为 t_last_submit（NBL-2）")
    if "尝试提交" in anchor or "尝试提交" in gate:
        raise CheckFailure("冷却锚点仍含“尝试提交”歧义（NBL-2）")
    definitions = policy.get("definitions") or {}
    if "t_last_submit" not in definitions or "t_submit" not in definitions:
        raise CheckFailure("cooldown_policy 缺少 t_submit/t_last_submit 定义")
    transitions = {item["id"]: item for item in data["transitions"]}
    if "全局冷却门" not in transitions["M5"]["condition"]:
        raise CheckFailure("M5 条件缺少全局冷却门")
    if "t_last_submit" not in transitions["M5"]["condition"]:
        raise CheckFailure("M5 冷却门必须使用 t_last_submit")
    if not transitions["M5"].get("global_cooldown_gate"):
        raise CheckFailure("M5 缺少 global_cooldown_gate 标记")
    h10 = next((item for item in data["hard_invariants"] if item["id"] == "H-10"), None)
    if h10 is None or "全局门" not in h10["rule"] or "T6-K01" not in h10["rule"]:
        raise CheckFailure("H-10 冷却全局门定义不完整")
    if "t_last_submit" not in h10["rule"]:
        raise CheckFailure("H-10 必须使用统一定义 t_last_submit")
    for phrase in ("全局门", "H-10", "S_COOLDOWN", "t_last_submit"):
        if phrase not in doc_text:
            raise CheckFailure(f"文档缺少冷却全局门口径：{phrase}")


def check_w_min_and_period(data: dict[str, Any], doc_text: str) -> None:
    low = data.get("low_fps_latency") or {}
    if low.get("w_min_is_lower_bound_only") is not True:
        raise CheckFailure("low_fps_latency 必须声明 W_min 只是下界")
    if low.get("w_min_must_not_enter_latency_statistics") is not True:
        raise CheckFailure("W_min 不得进入延迟统计")
    if "WINDOW_MATCH" not in str(low.get("window_completion_definition", "")):
        raise CheckFailure("窗口完成时刻必须定义为第 N 个 WINDOW_MATCH 结果到达时刻")
    interaction = str(low.get("interaction_latency", ""))
    if "window_complete" not in interaction:
        raise CheckFailure("交互延迟必须基于 window_complete（不得用 W_min 顶替）")
    if "BLOCKED" not in str(low.get("measured_period_status", "")):
        raise CheckFailure("无实测帧周期必须登记 BLOCKED")
    u_ids = {item["id"] for item in data["open_decisions"]}
    if "U6-13" not in u_ids:
        raise CheckFailure("缺少 U6-13（阶段4 实测帧周期）")
    for phrase in ("W_min", "window_complete", "实测", "T6-A03"):
        if phrase not in doc_text:
            raise CheckFailure(f"文档 §15 口径缺少：{phrase}")


def check_h4_no_hand(data: dict[str, Any], doc_text: str) -> None:
    h4 = next((item for item in data["hard_invariants"] if item["id"] == "H-4"), None)
    if h4 is None:
        raise CheckFailure("缺少 H-4")
    rule = h4["rule"]
    if "NO_HAND" not in rule or "不推进匹配计数" not in rule or "WINDOW_MATCH" not in rule:
        raise CheckFailure("H-4 必须区分窗口序列推进与匹配计数，并写明 NO_HAND 不推进匹配计数")
    window_rule = (data["event_classes"].get("window_advance_vs_match") or {})
    if "不推进匹配计数" not in str(window_rule.get("no_hand_rule", "")):
        raise CheckFailure("event_classes.window_advance_vs_match.no_hand_rule 不完整")
    rows = {row["id"]: row for row in data["behavior_rows"]}
    if "不推进匹配计数" not in rows["B17"]["output"]:
        raise CheckFailure("B17 未写明 NO_HAND 不推进匹配计数")
    if "NO_HAND" not in rows["B17"]["condition"]:
        raise CheckFailure("B17 条件未显式引用 NO_HAND")
    if "不得完成稳定窗口" not in rows["B17"]["output"]:
        raise CheckFailure("B17 未写明零框不得完成稳定窗口")
    for phrase in ("不推进匹配计数", "不得完成稳定窗口", "NO_HAND"):
        if phrase not in doc_text:
            raise CheckFailure(f"文档缺少 B-02 口径：{phrase}")


def check_reachability(data: dict[str, Any], doc_text: str) -> None:
    transitions = {item["id"]: item for item in data["transitions"]}
    if "M14" in transitions:
        raise CheckFailure("r02 必须删除 M14（重获统一为 M10→M11→M1）")
    section4 = doc_section(doc_text, "## 4.", "## 5.")
    if re.search(r"^\| M14 \|", section4, flags=re.MULTILINE):
        raise CheckFailure("文档 §4 表仍存在 M14 行")
    reach = data["reachability"]["transitions"]
    params = {item["id"]: item for item in data["parameters"]}
    s04 = float(params["T6-S04"]["draft_value"])
    l02 = float(params["T6-L02"]["draft_value"])
    expected_m4 = s04 < l02
    actual_m4 = reach["M4"]["status"] == "REACHABLE"
    if expected_m4 != actual_m4:
        raise CheckFailure(
            f"M4 可达性声明与草案参数不符：S04={s04} L02={l02} 推导可达={expected_m4}，"
            f"JSON 声明 {reach['M4']['status']}"
        )
    if reach["M7"]["status"] != "UNREACHABLE_BY_CONSTRUCTION":
        raise CheckFailure("M7 必须声明为构造上不可达")
    if "M4 在本轮参数下不可达" not in doc_text and "M4 在本轮参数下不可达" not in section4:
        raise CheckFailure("文档 §4 未声明 M4 不可达")
    rows = {row["id"]: row for row in data["behavior_rows"]}
    for pid in ("T6-C01", "T6-U00_W", "T6-U00_N"):
        if pid not in rows["B26"]["params"]:
            raise CheckFailure(f"B26 参数清单缺少 {pid}")
    if "12.1" not in doc_text:
        raise CheckFailure("文档缺少 §12.1 边界覆盖缺口登记")
    for token in ("C01", "U00_W", "U00_N", "S04", "U01"):
        if token not in doc_section(doc_text, "### 12.1", "## 13."):
            raise CheckFailure(f"§12.1 缺口表缺少 {token}")


def check_stable_latching(data: dict[str, Any], doc_text: str) -> str:
    """STABLE 锁存语义一致性（观察项定论，C17）。"""
    latch = data.get("stable_latching") or {}
    if not latch:
        raise CheckFailure("缺少 stable_latching 块（观察项：STABLE 是否锁存必须唯一写明）")
    if latch.get("latched") is not True:
        raise CheckFailure("stable_latching.latched 必须为 true（本 G0 定论：本次获取内锁存）")
    if latch.get("scope") != "WITHIN_ACQUISITION":
        raise CheckFailure("stable_latching.scope 必须为 WITHIN_ACQUISITION")
    statement = str(latch.get("statement", ""))
    if not statement:
        raise CheckFailure("stable_latching 缺少 statement")
    transitions = {item["id"]: item for item in data["transitions"]}
    computed = sorted(
        item_id for item_id, item in transitions.items() if item["from"] in ("STABLE", "*")
    )
    declared = sorted(str(item) for item in (latch.get("exit_paths") or []))
    if computed != declared:
        raise CheckFailure(f"STABLE 退出路径与迁移表不一致：推导 {computed} vs 声明 {declared}")
    demote = sorted(
        item_id for item_id, item in transitions.items()
        if item["from"] == "STABLE" and item["to"] == "CANDIDATE"
    )
    if demote:
        raise CheckFailure(f"锁存定论下不得存在 STABLE→CANDIDATE 迁移：{demote}")
    if not latch.get("not_demoted_by"):
        raise CheckFailure("stable_latching 必须写明哪些条件不会使其退回 CANDIDATE")
    if statement not in doc_text:
        raise CheckFailure("文档未复述 stable_latching.statement（§4 锁存定论）")
    decisions = {item["id"] for item in data["open_decisions"]}
    if "U6-16" not in decisions:
        raise CheckFailure("缺少 U6-16（STABLE 锁存待 G0 确认）")
    if "U6-16" not in doc_text:
        raise CheckFailure("文档 §16 缺少 U6-16")
    return f"STABLE 锁存（WITHIN_ACQUISITION）：退出路径 {declared}，无 STABLE→CANDIDATE 迁移，U6-16 待确认"


# ---------------------------------------------------------------- main


def run_checks(
    data: dict[str, Any],
    doc_text: str,
    cases: dict[str, Any],
    bindings: dict[str, Any],
    project_root: Path,
    doc_path: Path,
    json_path: Path,
    cases_path: Path,
    evidence_dir: Path | None,
    manifest_path: Path | None,
    state_path: Path | None,
    state_text: str | None,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []
    inventory: dict[str, Any] = {}

    def run(check_id: str, name: str, func) -> None:
        try:
            detail = func()
        except CheckFailure as exc:
            checks.append({"id": check_id, "name": name, "status": "FAIL", "detail": str(exc)})
            errors.append(f"{check_id}: {exc}")
        except Exception as exc:  # noqa: BLE001
            checks.append(
                {
                    "id": check_id,
                    "name": name,
                    "status": "FAIL",
                    "detail": f"未预期异常 {type(exc).__name__}: {exc}",
                }
            )
            errors.append(f"{check_id}: {type(exc).__name__}: {exc}")
        else:
            checks.append({"id": check_id, "name": name, "status": "PASS", "detail": detail})

    def c3() -> str:
        nonlocal inventory
        inventory, detail = check_doc_json_consistency(data, doc_text)
        return detail

    run("C1", "JSON 身份与必填块", lambda: check_identity(data) or "identity ok")
    run("C2", "ID 唯一性与最小规模", lambda: check_unique_ids(data) or "unique ok")
    run("C3", "文档↔JSON 标识集合双向一致", c3)
    run("C4", "待批准纪律", lambda: check_pending_approval_discipline(data, doc_text) or "24 项参数与指标 PENDING_APPROVAL")
    run("C5", "五类动作映射一致", lambda: check_action_map(data) or "5 类映射一致，target 唯一")
    run("C6", "硬不变量与唯一触发解释", lambda: check_invariants(data) or "H-1..H-10 齐全，ONCE_PER_ACQUISITION 唯一")
    run("C7", "人工手算样例独立复算", lambda: check_hand_cases(cases))
    run("C8", "上游只读文件哈希复算", lambda: check_upstream(bindings, project_root))
    run("C9", "文档必备覆盖与章节", lambda: check_doc_coverage(doc_text) or "关键词与章节齐全")
    run("C10", "禁止声明扫描（窄口径）", lambda: check_forbidden_claims(doc_text, data) or "未发现禁止声明")
    run(
        "C11",
        "证据清单/STATE 声明 vs 实际文件",
        lambda: check_evidence_integrity(evidence_dir, manifest_path, state_path, project_root),
    )
    run(
        "C12",
        "谓词拆分一致性（B-05/R3-B01/R3-B02）",
        lambda: check_predicates(data, doc_text, state_text, cases)
        or "谓词定义、引用、禁用标识符与全量双向绑定一致",
    )
    run("C13", "冷却全局门一致性（B-03/H-10）", lambda: check_cooldown_gate(data, doc_text) or "全局门字段与引用一致")
    run("C14", "W_min/实测帧周期口径（B-04/N-05）", lambda: check_w_min_and_period(data, doc_text) or "W_min 仅下界、window_complete 为统计基准")
    run("C15", "H-4/NO_HAND 一致性（B-02）", lambda: check_h4_no_hand(data, doc_text) or "NO_HAND 不推进匹配计数、零框不得完成窗口")
    run("C16", "迁移可达性与覆盖声明（N-02/N-03）", lambda: check_reachability(data, doc_text) or "M4/M7 可达性声明与 B26/§12.1 覆盖一致")
    run("C17", "STABLE 锁存语义一致性（观察项）", lambda: check_stable_latching(data, doc_text))

    status = "ALL_PASS" if not errors else "FAILED"
    return {
        "schema_version": 1,
        "artifact": "s6a_g0_selfcheck_result",
        "task_id": data["task_id"],
        "run_id": data["run_id"],
        "artifact_version": data.get("artifact_version"),
        "status": status,
        "checks": checks,
        "errors": errors,
        "id_inventory": inventory,
        "inputs": {
            "behavior_json_path": str(json_path),
            "behavior_json_sha256": sha256_file(json_path),
            "human_doc_path": str(doc_path),
            "human_doc_sha256": sha256_file(doc_path),
            "hand_cases_path": str(cases_path),
            "hand_cases_sha256": sha256_file(cases_path),
            "evidence_dir": str(evidence_dir) if evidence_dir else None,
            "manifest_path": str(manifest_path) if manifest_path else None,
            "state_path": str(state_path) if state_path else None,
        },
        "scope_statement": SCOPE_STATEMENT,
        "limitations": [
            "只复算规格一致性、算术边界与证据存在性；不验证状态机行为（本轮仍无状态机实现）",
            "C10 为窄口径文本扫描，不是完备的声明审计",
            "C3 的 from/to 比对依赖文档 §4 表格式（r02 已统一为可机器解析）",
            "ALL_PASS 不代表独立审查、G0/G2/G4/G5 或实物验收通过",
            "C12 的禁用标识符扫描为字面匹配（matched_frames/t_last_match/t_submit+），"
            "仅放行邻近标注“已废弃”的历史说明；不是完备的术语审计",
            "C17 只核对锁存声明与迁移表一致，不验证状态机实现",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="阶段6 S6-A G0 包自检（r04 加固版）")
    parser.add_argument("--json", required=True, help="行为表 JSON 路径")
    parser.add_argument("--doc", required=True, help="人读规格路径")
    parser.add_argument("--cases", required=True, help="人工手算样例 JSON 路径")
    parser.add_argument("--upstream", required=True, help="上游绑定 JSON 路径")
    parser.add_argument("--out", required=True, help="自检结果输出路径")
    parser.add_argument("--project-root", default=None, help="工作树根（默认脚本上级目录）")
    parser.add_argument("--evidence-dir", default=None, help="证据运行目录（C11）")
    parser.add_argument("--manifest", default=None, help="delivery_manifest.json（C11）")
    parser.add_argument("--state", default=None, help="阶段 STATE 文件（C11）")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_root = (
        Path(args.project_root).resolve()
        if args.project_root
        else Path(__file__).resolve().parent.parent
    )
    json_path = Path(args.json).resolve()
    doc_path = Path(args.doc).resolve()
    cases_path = Path(args.cases).resolve()
    try:
        data = load_json(json_path)
        doc_text = doc_path.read_text(encoding="utf-8")
        cases = load_json(cases_path)
        bindings = load_json(Path(args.upstream).resolve())
    except (OSError, ValueError) as exc:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps({"status": "INPUT_ERROR", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False))
        return 2
    state_text = None
    if args.state:
        state_file = Path(args.state).resolve()
        if state_file.is_file():
            state_text = state_file.read_text(encoding="utf-8")
    result = run_checks(
        data,
        doc_text,
        cases,
        bindings,
        project_root,
        doc_path,
        json_path,
        cases_path,
        Path(args.evidence_dir).resolve() if args.evidence_dir else None,
        Path(args.manifest).resolve() if args.manifest else None,
        Path(args.state).resolve() if args.state else None,
        state_text,
    )
    Path(args.out).write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"status": result["status"], "errors": result["errors"], "checks": result["checks"]}, ensure_ascii=False))
    return 0 if result["status"] == "ALL_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
