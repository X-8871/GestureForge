#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《阶段6 待批决策清单》（一次性工具，不进入交付）。

输入：阶段6 行为表 JSON（w6，只读）。
输出：report/evidence/CTRL-DSH-HANDOFF/approval_sheet_20261023_r01/stage6_approval_sheet.md

口径：
- 参数只做“机械抄录”（id/值/单位/比较口径/批准状态），不做任何解释性改写；
- 决策要点与建议由 DSH 项目总控撰写，注明依据来源（评审/规格条目）。
"""
from __future__ import annotations

import json
import pathlib
import sys

SRC = pathlib.Path(r"D:dex-worktreesw6docsstage6s6a_stage6_g0_behavior_v1.json")
OUT = pathlib.Path(r"D:\FPGA_Competition\report\evidence\CTRL-DSH-HANDOFF\approval_sheet_20261023_r01\stage6_approval_sheet.md")


def cell(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "是" if value else "否"
    if isinstance(value, (list, tuple)):
        return "、".join(str(v) for v in value) if value else "（空）"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    text = str(value).replace("|", "/").replace("\n", " ")
    return text if text else "—"


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    params = data.get("parameters") or []
    header = [
        "# 阶段6 待批决策清单（S6-A v1.6 / r07；生成时间 2026-10-23 03:40 UTC+8）",
        "",
        f"- 来源：`{SRC}`（只读抄录，未作解释性改写；参数共 {len(params)} 项）",
        "- 用途：供 Wong 一次性批准/修改阶段6 的阈值与语义开放项。**批准前**：实现可按草案值推进，但 **G4/G5 不得通过**，且冻结接口不得对外声明。",
        "- 填法：在“决定”列写 `批准` / `改：<值>` / `待议`；未填视为未批。",
        "",
        "## 一、会改变行为的三项（建议优先过）",
        "",
        "| # | 项 | 现状 | 影响 | 我的建议 | 决定 |",
        "|---|---|---|---|---|---|",
        "| 1 | `T6-A02`(去重窗 500ms) vs `T6-K01`(冷却 1000ms) | `T6-A02` < `T6-K01` | 去重路径 `B16/S_DEDUP` **永远不可达**（第二次提交必然已超 500ms） | 若希望“冷却内重复提交被去重”真实存在，把 `T6-A02` 提到 >1000ms；否则明确登记该路径为“设计上不可达” |  |",
        "| 2 | `T6-S01`(200ms) / `T6-S02`(6 帧) | 30fps 下 `(6−1)×33.3ms=166.5ms < 200ms` | 窗口完成时刻由**时长**支配 → 第 8 帧 233.1ms 才进 STABLE（与文档 §15 示例一致） | 批准（这是真实相机 30fps 的行为，已按 `T6-S03`“取较晚”实现） |  |",
        "| 3 | `U6-12`（M4 可达性） | 已改为 **M4 保留并计入覆盖**（评审证实 `M4@f7` 可达） | 若按旧结论“删 M4/`T6-S04`”会删掉一条实际可达且已覆盖的迁移 | 批准“保留 M4，仅由 G0 决定兜底次序” |  |",
        "",
        "## 二、语义开放项",
        "",
        "| 项 | 内容 | 现状 | 决定 |",
        "|---|---|---|---|",
        "| `U6-16` | STABLE 是否**本次获取内锁存** | 已定为“锁存”，退出仅 `M2/M10/M5`；`C17` 断言 |  |",
        "| `U6-13` | 交互延迟 `T6-A03` 基准 | **NOT_RUN**（缺阶段4 实测帧周期 P） |  |",
        "| `U6-15` | 动作支持类型 | 恰为 `A_SWITCH_UI` + `A_SWITCH_CHANNEL` |  |",
        "| 跨阶段 | `stale_age_limit`(200ms 草案) | 阶段5 已按 200ms 使用，阶段4 需在正式 G0 冻结同一常量 |  |",
        "",
        "## 三、24 项参数（机械抄录）",
        "",
        "| 参数 ID | 值 | 单位 | 比较口径 | 批准状态 | 决定 |",
        "|---|---|---|---|---|---|",
    ]

    rows = []
    for p in params:
        rows.append(
            "| `{}` | {} | {} | {} | {} |  |".format(
                cell(p.get("id")),
                cell(p.get("draft_value", p.get("value"))),
                cell(p.get("unit")),
                cell(p.get("comparison")),
                cell(p.get("approval_status")),
            )
        )

    extra_keys = sorted({k for p in params for k in p} - {"id", "draft_value", "value", "unit", "comparison", "approval_status"})
    tail = [
        "",
        f"- 参数对象另含字段（未逐项展开）：{cell(extra_keys)}",
        "",
        "## 四、批后效果",
        "",
        "1. 批准 → 阶段6 的 G4（任务验收）才可判定；`PENDING_APPROVAL` 不得出现在最终冻结声明里。",
        "2. 未批项在其被依赖的路径上**保持受阻**并如实登记（不得以“默认通过”处理）。",
        "3. 本清单只覆盖阶段6；阶段4/5 的指标与跨阶段常量另行出表。",
        "",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(header + rows + tail), encoding="utf-8", newline="\n")
    print(f"WROTE {OUT}")
    print(f"PARAMS {len(params)}")
    print("IDS " + ",".join(str(p.get("id")) for p in params))
    return 0


if __name__ == "__main__":
    sys.exit(main())