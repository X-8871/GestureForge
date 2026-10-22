# S6-A 修订记录 v1.6 / r07（第 6 轮复评 F1–F11 收尾 + BLK-1 的 M4 可达性修正）

- 任务：`S6-A`；被审基线：`04ea58e1`（r06，已 PASS）；新 RunId：`s6a_g0_20261022_r07`（r01..r06 均不覆盖）
- 复评来源：`S6A_r06_20261023_r01`（`PASS`，0 阻断 / `F1`–`F11`）；`S6B_20261023_r01`（`CHANGES_REQUIRED`，其 `BLK-1` 牵到 S6-A 的 M4 可达性）
- 阈值纪律：**24 项参数值与 `PENDING_APPROVAL` 状态未改**；未在测试集调参；未触碰硬件
- 状态：**PENDING_REVIEW**；本记录不构成“已审查/已通过”

## 最高优先：`F6` 冻结自证性（规则）

新增 `verification/export_selfproof.py`：`git archive` 导出目标提交到隔离目录后，用**该提交内的**自检与
`check_stage_delivery.py` 的 `inputs`/`evidence` 两项复跑，三项 exit 0 才判 `SELF_PROVEN`。
规则固定：**任何冻结/交付提交必须自证**（S6-B 最终冻结同样适用）。
实测：r06（`04ea58e1`）导出后自检 **C11 FAIL**（STATE 声明了该提交内 0 文件的 `report/evidence/S6-B/…`）；
r07 在同一提交内落入被声明目录。

## 其余项

| 项 | 处置 |
|---|---|
| `F1` | 文档 §9/B07/B27 与 JSON `B07.condition`/`B27.output` 统一为「第一个同时满足帧数与时长（取较晚）的帧」；C14 增加机器断言并注入证明 |
| `BLK-1(b)` | `reachability.M4` → `REACHABLE`（`TARGET_CONTINUES` 不含 `score ≥ T6-P02` → 低分中断不推进 `miss_streak`）；`U6-12` 改写为保留 M4；文档 §4/§12.1/§16 + C16 同步 |
| `F2`–`F5` | 限制项基线动态取值；探针计数写实；r04 归因统一为「样例数不足（29 < 32）」；STATE 陈旧行更新 |
| `F7` | 完成帧越界改报 `-1`/`0.0` + `required_completion_index`；新增 HC-32 与注入 |
| `F8`/`F9` | 登记为有意设计（浮点含等号鲁棒性；整段序列视为一个窗口） |
| `F10`/`F11` | 旧口径对照失败点描述改准；键名/版本/别名/完整版本令牌等零星清理 |

## 结论边界

`ALL_PASS` / `CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不代表状态机行为、
G0 复评、独立审查或实物验收通过。30fps 结论基于草案 `P`=33.3 ms 假设（`U6-13`）；
M4 可达性基于 §3 的 `TARGET_CONTINUES` 口径（该口径若变更需重推）。
