# S6-A 修订记录 v1.3 / r04（第三轮复评 R3-B01/R3-B02 + N01..N05 + 观察项）

- 任务：`S6-A`；被审基线：`2ce290f`（r03）；新 RunId：`s6a_g0_20261022_r04`（r01/r02/r03 均不覆盖）
- 复评来源：`report/evidence/CTRL-DSH-HANDOFF/reviews/S6A_r03_20261022_r01/REVIEW_r03.md`
- 阈值纪律：**24 项参数值与 `PENDING_APPROVAL` 状态未改**；未在测试集调参；未触碰硬件；S6-B WIP 不提交
- 状态：**PENDING_REVIEW**；复评由项目总控另派，本记录不构成“已审查/已通过”

## 阻断项

| 项 | 处置 | 证据 |
|---|---|---|
| R3-B01 §12 谓词残留 | `T6-S02` 行改「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」；`T6-L02` 行改 `t_now − t_last_target_continues ≥ T6-L02`；§3/§12/§13 定义该锚点（含“被抑制/失败不更新”）；JSON 增 `time_anchors` 并同步 M10/B10；C12 增禁用标识符扫描 | 文档 §3/§4/§5/§12/§13；JSON `time_anchors`；`selfcheck_r03_failure.json`（C12 FAIL） |
| R3-B02 predicates 双向不一致 | B03 补 `TARGET_CONTINUES`、B17 补 `WINDOW_MATCH`、`TARGET_CONTINUES.used_by` 补 B14、M1 收敛为仅 `TARGET_CONTINUES`；`predicate_binding_policy` 明确 M5/B13「条件文本 + `global_cooldown_gate` 绑定、无 `predicates_used` 字段」；C12 增全量双向断言与字段现状断言 | JSON `predicates`/`predicate_binding_policy`；`selfcheck_r03_failure.json`（C12 FAIL） |

## 观察项（已定论）

STABLE **在本次获取内锁存**：不因窗口中断、`score` 跌破 `T6-P02`、抖动耗尽而退回 `CANDIDATE`；离开路径仅 M2/M10/M5；冷却门开启后下一条窗口推进帧即可触发。已写入 §4、JSON `stable_latching`，自检 C17 断言，登记 `U6-16` 待 Wong/G0 确认。

## 非阻断项

N01 统一 `t_last_submit` 并删除已废弃写法；N02 HC-27 去自比较（改帧时刻序列推导）、HC-28/29 逐帧序列真推导、`revision.changes` 措辞更正；N03 旧包失败证据由 `verification/s6a_rerun_legacy_failures.py` 用最终脚本重跑并纳入构建器；N04 C7 样例数 27→29、版本号统一 v1.3/r04；N05 旧哈希成因改为「LF→CRLF + 末尾补 CRLF」。

## 结论边界

- `ALL_PASS` / `CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定；不验证状态机行为，不代表 G0 复评、独立审查或实物验收通过。
- 回放/注入类结论仅限回放/注入输入；本包未运行任何状态机。
- `STABLE 锁存` 与全部阈值一样属待批准语义；复评未通过前不得据本包宣称 G0 通过。
