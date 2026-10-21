#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""S4-D 阶段5/6 规格草案自检（只读，标准库）。

校验：
  C1  s6_interaction_thresholds.json 可 json.load 且关键字段存在
  C2  文档 §8.4 镜像块与 JSON 文件逐字段相等
  C3  文档 §8.1 阈值表与 JSON 的 id/门槛/样本数关键值一致
  C4  阶段5 规格草案覆盖必需条目（锚点全命中）
  C5  阶段6 规格草案覆盖必需条目（锚点全命中）
  C6  草案状态声明（含「草案/未冻结」，无「已验收/已冻结/实测数值」伪装）
  C7  补边几何样例按 D2/2A 冻结公式复算，与文档表格逐值一致；并枚举奇数总补边样例
  C8  被引用只读上游文档在本地工作树的 SHA-256 记录（供 Review 复核漂移）

输出：selfcheck_result.json、coverage_matrix.json、letterbox_geometry_fixtures.json
退出码：0 = 全部 PASS；1 = 存在 FAIL；2 = 环境/输入错误。
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

RUN_ID = "s4d_spec_draft_20261021_r01"
SCRIPT_DIR = Path(__file__).resolve().parent          # <root>/report/evidence/S4-D/<run_id>
ROOT = SCRIPT_DIR.parents[3]                          # <root>（工作树根）
DOC_S5 = ROOT / "docs/stage5/S5_stage5_display_spec_draft.md"
DOC_S6 = ROOT / "docs/stage6/S6_stage6_interaction_spec_draft.md"
JSON_S6 = ROOT / "docs/stage6/s6_interaction_thresholds.json"
UPSTREAM = [
    "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md",
    "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
    "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md",
    "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md",
    "verification/s1_t02_d2_numeric_reference.py",
    "AGENTS.md",
]

MIRROR_START = "<!-- S6-THRESHOLDS-MIRROR-START -->"
MIRROR_END = "<!-- S6-THRESHOLDS-MIRROR-END -->"

DRAFT_BANNER = "草案（DRAFT），未冻结、未验收、未上板"
FORBIDDEN_CLAIMS = [
    r"本规格已冻结",
    r"本文已冻结",
    r"已通过阶段5验收",
    r"已通过阶段6验收",
    r"已通过\s*G4",
    r"验收通过",
    r"实测(数据|数值|结果)\s*[:：=]",
    r"实测(数据|数值|结果)为",
    r"测得\s*\d",
]

# (item_id, phase, plan_line, requirement, doc_key, section, anchors)
COVERAGE = [
    ("S5-L96-01", "5", 96, "原始画面＋检测框/类别/分数/FPS/延迟", "s5", "§2.3", ["采集FPS / 推理FPS / 显示FPS", "类别 + 分数"]),
    ("S5-L96-02", "5", 96, "补边逆映射", "s5", "§3.2", ["逆映射（草案公式", "反补边到缩放图坐标"]),
    ("S5-L96-03", "5", 96, "非方形视频", "s5", "§6 T5-01", ["T5-01", "非方形视频"]),
    ("S5-L96-04", "5", 96, "边缘框", "s5", "§6 T5-02", ["T5-02", "边缘框"]),
    ("S5-L96-05", "5", 96, "多框", "s5", "§6 T5-03", ["T5-03", "多框与零框"]),
    ("S5-L96-06", "5", 96, "零框", "s5", "§6 T5-03/§2.3", ["零框（无手）", "boxes=0"]),
    ("S5-L96-07", "5", 96, "过期清除", "s5", "§2.1/§6 T5-04", ["T5-04", "过期清除"]),
    ("S5-L96-08", "5", 96, "坐标误差门槛在阶段1/G0冻结", "s5", "§3.3", ["坐标误差门槛口径（沿用 2A 比较容限", "1e-6", "草案建议"]),
    ("S5-L96-09", "5", 96, "logits/整数分数显示为分数", "s5", "§1.2 R1", ["R1", "整数分数"]),
    ("S5-L96-10", "5", 96, "概率转换明确后才称置信度", "s5", "§1.2 R2/R3", ["R2", "置信度"]),
    ("S5-L96-11", "5", 96, "不把数值大等同可靠概率", "s5", "§1.2 R4", ["R4", "不得把数值大小等同于可靠概率"]),
    ("S5-L98-01", "5", 98, "显示结果关联对应帧号", "s5", "§2.4", ["T5-05", "displayed_frame_id"]),
    ("S5-L98-02", "5", 98, "画面语义与结果年龄", "s5", "§2.1", ["latest-result overlay", "age_result", "age_frame"]),
    ("S5-L98-03", "5", 98, "不能伪称同帧", "s5", "§2.1", ["禁止伪称同帧"]),
    ("S5-L98-04", "5", 98, "FPS分别说明采集/推理/显示", "s5", "§5.1-§5.3", ["### 5.1 采集 FPS", "### 5.2 推理 FPS", "### 5.3 显示 FPS"]),
    ("S5-L98-05", "5", 98, "预热、丢帧、超时不隐藏", "s5", "§5.5", ["### 5.5 预热、丢帧与超时（不得隐藏）", "| 过期清除 |"]),
    ("S5-L100-01", "5", 100, "G0确定布局/测量起止事件/允许延迟", "s5", "§2.3/§5/§8", ["U5-01", "U5-02", "U5-05", "U5-06"]),
    ("S5-L100-02", "5", 100, "至少100帧检查结果对应", "s5", "§6 T5-05", ["T5-05", "≥100 帧"]),
    ("S5-L100-03", "5", 100, "连续30分钟无死锁", "s5", "§6 T5-09", ["T5-09", "30 分钟无死锁"]),
    ("S5-L100-04", "5", 100, "回归阶段4数值链路", "s5", "§6 T5-10", ["T5-10", "回归阶段4 数值链路"]),
    ("S5-L100-05", "5", 100, "截图/连续视频和原始统计均留证", "s5", "§7", ["截图、连续视频、原始统计"]),
    ("S6-L104-01", "6", 104, "稳定手势判定→切图/界面/显示状态", "s6", "§1.3/§4.1", ["### 4.1 稳定窗口条件", "A_SWITCH_CHANNEL", "A_SWITCH_UI", "A_DISPLAY_STATE"]),
    ("S6-L104-02", "6", 104, "多框目标选择", "s6", "§3", ["## 3. 多框目标选择规则", "维持优先（迟滞）", "T6-P01"]),
    ("S6-L104-03", "6", 104, "目标丢失与重获", "s6", "§5", ["### 5.1 丢失", "### 5.2 重获", "T6-L01"]),
    ("S6-L104-04", "6", 104, "稳定判定窗口", "s6", "§4.1/§4.2", ["T6-S01", "T6-S02", "T6-S03"]),
    ("S6-L104-05", "6", 104, "保持时是否只触发一次", "s6", "§4.3", ["### 4.3 保持期是否只触发一次", "一次获取只触发一次", "trigger_once_while_held"]),
    ("S6-L104-06", "6", 104, "冷却", "s6", "§4.4", ["### 4.4 冷却", "T6-K01", "1000 ms"]),
    ("S6-L104-07", "6", 104, "重新触发条件", "s6", "§4.3/§5.2", ["重新触发条件（草案，配合 M8/M9）", "重获，§5.2"]),
    ("S6-L104-08", "6", 104, "无手/未知输入与恢复行为", "s6", "§7", ["## 7. 无手/未知输入与恢复", "UNKNOWN_RECOVER", "T6-U01", "### 7.1 无手（零框）"]),
    ("S6-L106-01", "6", 106, "短暂抖动", "s6", "§9 T6-SC-01", ["T6-SC-01", "S_JITTER_TOLERATED"]),
    ("S6-L106-02", "6", 106, "持续保持", "s6", "§9 T6-SC-02", ["T6-SC-02", "持续保持"]),
    ("S6-L106-03", "6", 106, "手势切换", "s6", "§6/§9 T6-SC-03", ["T6-SC-03", "手势切换"]),
    ("S6-L106-04", "6", 106, "手离开", "s6", "§9 T6-SC-04", ["T6-SC-04", "手离开"]),
    ("S6-L106-05", "6", 106, "未知场景", "s6", "§9 T6-SC-05", ["T6-SC-05", "未知场景"]),
    ("S6-L106-06", "6", 106, "已知手势有效动作成功率≥90%", "s6", "§8.1 T6-01", ["T6-01", "≥90%", "0.9"]),
    ("S6-L106-07", "6", 106, "至少200个独立未知输入误接受率≤5%", "s6", "§8.1 T6-02", ["T6-02", "≤5%", "≥200"]),
    ("S6-L106-08", "6", 106, "无有效手势30分钟误动作≤1次", "s6", "§8.1 T6-03", ["T6-03", "≤1 次", "1800"]),
    ("S6-L106-09", "6", 106, "各条件样本数及阈值在任务G0固定", "s6", "§8.1/§11 U6-01", ["待阶段6 G0 固定", "U6-01"]),
    ("S6-L106-10", "6", 106, "不能只挑成功视频", "s6", "§8.2", ["不得只挑成功视频", "不能只挑成功视频"]),
    ("S6-L108-01", "6", 108, "证据：状态机规格/日志/失败案例/连续视频", "s6", "§10.1", ["### 10.1 必须留存", "失败案例", "连续视频"]),
    ("S6-L108-02", "6", 108, "交互通过不代替阶段7验收", "s6", "§0/§11 U6-08", ["交互通过**不代替**阶段7", "U6-08"]),
]

# 文档 §3.1 中给出的样例（源尺寸 → 期望几何），脚本按冻结公式复算后逐值比较
GEOMETRY_EXPECTED = {
    (1280, 720): (416, 234, 0, 91),
    (720, 1280): (234, 416, 91, 0),
    (1920, 1080): (416, 234, 0, 91),
    (640, 640): (416, 416, 0, 0),
    (800, 600): (416, 312, 0, 52),
    (640, 360): (416, 234, 0, 91),
    (683, 384): (416, 233, 0, 91),
}

S5_SECTION_RE = re.compile(
    r"^\|\s*(\d{3,4})×(\d{3,4})[^|]*\|\s*(\d+)×(\d+)\s*\|\s*(\d+)×(\d+)\s*\|\s*(\d+),\s*(\d+)\s*\|",
    re.MULTILINE,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def letterbox_geometry(src_w: int, src_h: int, dst_w: int = 416, dst_h: int = 416) -> dict:
    """复现 D2 冻结几何：整数截断 + 左上 floor 偏移（D2 第9行/2A 第77行）。"""
    if (float(dst_w) / src_w) < (float(dst_h) / src_h):
        new_w = dst_w
        new_h = (src_h * dst_w) // src_w
    else:
        new_h = dst_h
        new_w = (src_w * dst_h) // src_h
    return {
        "new_w": new_w,
        "new_h": new_h,
        "off_x": (dst_w - new_w) // 2,
        "off_y": (dst_h - new_h) // 2,
        "pad_total_x": dst_w - new_w,
        "pad_total_y": dst_h - new_h,
    }


def main() -> int:
    checks: list[dict] = []
    coverage_rows: list[dict] = []

    def add(name: str, ok: bool, detail: str) -> bool:
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})
        return ok

    if not DOC_S5.is_file() or not DOC_S6.is_file() or not JSON_S6.is_file():
        print("环境错误：规格文件缺失", file=sys.stderr)
        return 2

    s5 = DOC_S5.read_text(encoding="utf-8")
    s6 = DOC_S6.read_text(encoding="utf-8")

    # C1 JSON 可解析
    try:
        data = json.loads(JSON_S6.read_text(encoding="utf-8"))
        ok_c1 = (
            isinstance(data, dict)
            and data.get("schema_version") == 1
            and data.get("artifact") == "s6_interaction_thresholds"
            and isinstance(data.get("thresholds"), list)
            and len(data["thresholds"]) == 3
            and data.get("status") == "draft_proposed_unfrozen"
        )
        add("C1_json_parses", ok_c1, f"thresholds={len(data.get('thresholds', []))} status={data.get('status')}")
    except Exception as exc:  # noqa: BLE001
        add("C1_json_parses", False, f"{type(exc).__name__}: {exc}")
        data = None

    # C2 镜像块 == JSON 文件
    if data is not None:
        start = s6.find(MIRROR_START)
        end = s6.find(MIRROR_END)
        if start < 0 or end < 0 or end <= start:
            add("C2_mirror_equals_json", False, "文档未找到镜像标记或标记顺序错误")
        else:
            block = s6[start + len(MIRROR_START):end].strip()
            try:
                mirror = json.loads(block)
                add("C2_mirror_equals_json", mirror == data, f"mirror_keys={sorted(mirror.keys()) if isinstance(mirror, dict) else type(mirror).__name__}")
            except Exception as exc:  # noqa: BLE001
                add("C2_mirror_equals_json", False, f"镜像块 JSON 解析失败：{type(exc).__name__}: {exc}")

    # C3 文档阈值表与 JSON 一致
    if data is not None:
        problems: list[str] = []
        table_lines = [line for line in s6.splitlines() if line.startswith("| `T6-0")]
        by_id = {}
        for line in table_lines:
            match = re.match(r"\|\s*`(T6-0\d)`", line)
            if match:
                by_id[match.group(1)] = line
        for item in data["thresholds"]:
            line = by_id.get(item["id"])
            if line is None:
                problems.append(f"{item['id']} 表行缺失")
                continue
            if item["value_display"] not in line:
                problems.append(f"{item['id']} 缺少 {item['value_display']}")
            sample_token = item.get("min_samples", item.get("session_seconds"))
            if sample_token is None or str(sample_token) not in line:
                problems.append(f"{item['id']} 缺少样本数/时长 {sample_token}")
            if f"`{item['operator']} {item['value']}`" not in line:
                problems.append(f"{item['id']} 缺少运算符/值 {item['operator']} {item['value']}")
        for token in ("≥90%", "≤5%", "≤1 次", "≥200", "30 分钟"):
            if token not in s6:
                problems.append(f"文档缺少门槛 token {token}")
        t602 = next((x for x in data["thresholds"] if x["id"] == "T6-02"), None)
        if t602 and t602.get("max_false_accepts") != int(t602["value"] * t602["min_samples"]):
            problems.append("T6-02 max_false_accepts 与 value*min_samples 不一致")
        add("C3_threshold_table_matches_json", not problems, "; ".join(problems) if problems else "3 项阈值与表格一致")

    # C4/C5 覆盖锚点
    docs = {"s5": s5, "s6": s6}
    for item_id, phase, line, requirement, doc_key, section, anchors in COVERAGE:
        missing = [a for a in anchors if a not in docs[doc_key]]
        coverage_rows.append(
            {
                "id": item_id,
                "phase": phase,
                "plan_line": line,
                "requirement": requirement,
                "doc": str((DOC_S5 if doc_key == "s5" else DOC_S6).relative_to(ROOT)).replace("\\", "/"),
                "section": section,
                "anchors": anchors,
                "missing_anchors": missing,
                "status": "PASS" if not missing else "FAIL",
            }
        )
    s5_bad = [r["id"] for r in coverage_rows if r["phase"] == "5" and r["status"] == "FAIL"]
    s6_bad = [r["id"] for r in coverage_rows if r["phase"] == "6" and r["status"] == "FAIL"]
    add("C4_stage5_requirements_covered", not s5_bad, f"未命中：{s5_bad}" if s5_bad else f"{sum(1 for r in coverage_rows if r['phase']=='5')} 项全部命中")
    add("C5_stage6_requirements_covered", not s6_bad, f"未命中：{s6_bad}" if s6_bad else f"{sum(1 for r in coverage_rows if r['phase']=='6')} 项全部命中")

    # C6 草案状态
    problems = []
    for label, text in (("S5", s5), ("S6", s6)):
        if DRAFT_BANNER not in text:
            problems.append(f"{label} 缺少草案状态横幅")
        if "未冻结" not in text or "草案" not in text:
            problems.append(f"{label} 缺少「草案/未冻结」表述")
        for bad in FORBIDDEN_CLAIMS:
            if re.search(bad, text):
                problems.append(f"{label} 出现禁止表述：{bad}")
    if "沿用强化建议、待阶段6 G0 固定" not in s6:
        problems.append("S6 缺少「沿用强化建议、待阶段6 G0 固定」标注")
    add("C6_draft_status_only", not problems, "; ".join(problems) if problems else "两文档均为草案且无验收伪装表述")

    # C7 几何复算与文档表格
    problems = []
    fixtures = {}
    for (src_w, src_h), (exp_nw, exp_nh, exp_ox, exp_oy) in GEOMETRY_EXPECTED.items():
        got = letterbox_geometry(src_w, src_h)
        fixtures[f"{src_w}x{src_h}"] = got
        actual = (got["new_w"], got["new_h"], got["off_x"], got["off_y"])
        if actual != (exp_nw, exp_nh, exp_ox, exp_oy):
            problems.append(f"{src_w}x{src_h} 脚本复算 {actual} != 预期 {(exp_nw, exp_nh, exp_ox, exp_oy)}")
        row_re = re.compile(
            rf"^\|\s*{src_w}×{src_h}[^|]*\|\s*\d+×\d+\s*\|\s*(\d+)×(\d+)\s*\|\s*(\d+),\s*(\d+)\s*\|",
            re.MULTILINE,
        )
        match = row_re.search(s5)
        if not match:
            problems.append(f"文档 §3.1 缺少 {src_w}×{src_h} 行")
            continue
        doc_vals = tuple(int(x) for x in match.groups())
        if doc_vals != actual:
            problems.append(f"文档 {src_w}×{src_h} 行 {doc_vals} != 复算 {actual}")
    parsed_rows = S5_SECTION_RE.findall(s5)
    if len(parsed_rows) < len(GEOMETRY_EXPECTED):
        problems.append(f"文档 §3.1 可解析几何行 {len(parsed_rows)} < 预期 {len(GEOMETRY_EXPECTED)}")
    # 枚举奇数总补边样例（供 T5-07 用例选择）
    odd_pad = []
    for src_w in range(320, 1921, 1):
        geo = letterbox_geometry(src_w, 720)
        if geo["pad_total_y"] % 2 == 1 and len(odd_pad) < 8:
            odd_pad.append({"src": f"{src_w}x720", **geo})
    fixtures["odd_pad_examples_720p"] = odd_pad
    if not odd_pad:
        problems.append("未枚举到奇数总补边样例")
    add("C7_letterbox_geometry_recomputed", not problems, "; ".join(problems) if problems else f"{len(GEOMETRY_EXPECTED)} 个样例与文档逐值一致，奇数补边样例 {len(odd_pad)} 个")

    # C8 上游文档哈希记录
    upstream = {}
    problems = []
    for rel in UPSTREAM:
        path = ROOT / rel
        if not path.is_file():
            problems.append(f"上游文件缺失：{rel}")
            continue
        upstream[rel] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    add("C8_upstream_hashes_recorded", not problems, "; ".join(problems) if problems else f"{len(upstream)} 个只读上游文件哈希已记录")

    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    result = {
        "run_id": RUN_ID,
        "script": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "overall": overall,
        "checks": checks,
        "coverage_summary": {
            "total": len(coverage_rows),
            "pass": sum(1 for r in coverage_rows if r["status"] == "PASS"),
            "fail": sum(1 for r in coverage_rows if r["status"] == "FAIL"),
            "stage5_items": sum(1 for r in coverage_rows if r["phase"] == "5"),
            "stage6_items": sum(1 for r in coverage_rows if r["phase"] == "6"),
        },
        "docs": {
            "docs/stage5/S5_stage5_display_spec_draft.md": sha256_file(DOC_S5),
            "docs/stage6/S6_stage6_interaction_spec_draft.md": sha256_file(DOC_S6),
            "docs/stage6/s6_interaction_thresholds.json": sha256_file(JSON_S6),
        },
        "upstream_sources_worktree": upstream,
        "scope_statement": "本自检不代表 G0/G4/G5 或实物验收；未执行任何显示/交互/上板实测。",
    }
    (SCRIPT_DIR / "selfcheck_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SCRIPT_DIR / "coverage_matrix.json").write_text(
        json.dumps(
            {
                "run_id": RUN_ID,
                "source": "docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md 第 94-108 行",
                "phase5_doc": "docs/stage5/S5_stage5_display_spec_draft.md",
                "phase6_doc": "docs/stage6/S6_stage6_interaction_spec_draft.md",
                "thresholds_json": "docs/stage6/s6_interaction_thresholds.json",
                "items": coverage_rows,
                "summary": result["coverage_summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (SCRIPT_DIR / "letterbox_geometry_fixtures.json").write_text(
        json.dumps(
            {
                "run_id": RUN_ID,
                "formula_source": "S1-T02-D2 固定预处理与INT8数值规格 第9行 + S2A-T01 第77行；实现参考 verification/s1_t02_d2_numeric_reference.py 第116-137行",
                "dst": "416x416",
                "note": "由冻结公式算术推导，非实测；pad_total_y 为奇数时上下补边相差 1px。",
                "fixtures": fixtures,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for check in checks:
        print(f"[{check['status']}] {check['name']}: {check['detail']}")
    print(f"overall={overall} coverage={result['coverage_summary']}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())