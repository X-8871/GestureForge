# 阶段4 证据链 errata（S4-T34，2026-10-28 r01）

- 来源：外部复审（Workbuddy）提出 3 条账本缺陷，lead 独立核实（F1、F3 成立；F2 成立但性质较轻）。
- **本文件不改任何实测值、不改冻结成员、不动已提交文件**；只做**口径澄清与结构化引用**。
- 交叉核验：`hash_basis=commit_blob`（清单级）+ 逐条 `hash_basis` 覆盖（新增文件为 `worktree_disk`）。
- 基线提交：`f84d541bafb1bf24a72f86d28fa8a55377532d82`

## F1（阻断，真）—— 结论与退出码并存矛盾

| 项 | 事实 |
|---|---|
| 文件 | `report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/results_chainlite_b_final.json`（SHA-256 `2325ddf6536b6fe9cc05e1fb73ad3dc28ea9adfa51b16692e5f39080a3011514`） |
| 现象 | `conclusion = CHAINLITE_B_PASS` 与 `W3_compare.exit_code = 1`（窗口内 `W3A_PASS_W3B_PENDING`）**并存** |
| 性质 | `W3_compare.exit_code=1` 是**窗口执行时**离线参考尚未生成的 **pending 态**；最终判定由 `W3_compare_final.json` 给出 |
| 影响 | 汇总层若只看 `W3_compare.exit_code` 会误判为 FAIL；若只看 `conclusion` 会缺少可核依据 |
| 修正口径 | **权威引用 = `report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/W3_compare_final.json`**（结构化见 `ledger_reference.json`）；`W3_compare.exit_code=1` 标注为 `IN_WINDOW_PENDING_NOT_FINAL` |
| 实测值 | **未改**（原文件保留） |

## F2（真，轻）—— 汇总层引用裸字符串

| 项 | 事实 |
|---|---|
| 位置 | `report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/results_chainlite_b_final.json` 第 **288** 行：`"W3_compare_final": "PASS",` |
| 问题 | 汇总层用**裸字符串** `"PASS"` 引用，未给结构化指针 |
| 修正口径 | 以 `report/evidence/S4-T34/bringup_chainlite_b_20261028_r01/W3_compare_final.json`（SHA-256 `0a1c251fa8519c782784458d90ef208f9b8478449766b1f790893c257fe30c85`）为结构化权威；`ledger_reference.json` 给出 `reference_sha256 / tolerance / max_abs_diff / board_uart_sha256` |
| 实测值 | **未改** |

## F3（真，文档级）—— 命名漂移

- 冻结文档 `docs/stage4/S4D_m4b_csr_semantics_20261027_r01.md` 第 **58** 行使用 `first_diff13 / first_diff26 / premature`；
- 实现（`vitis/stage4/ps/s4d_ps_app.c`）输出字段为 `first13 / first26 / gate`；
- **不改冻结文档**（在 r5 冻结集内），以 `naming_map.json` 给出一对一映射与语义等价说明。

## F4（非阻断）—— 投毒只在明细披露

- `bringup_window6_20261028_r03` 的“输出区投毒”这一宿主侧前置只在 `report/evidence/S4-T34/bringup_window6_20261028_r03/W2_M4b_preload_details.json` 披露；
- 修正口径：`ledger_reference.json.evidence_preconditions` 显式登记该前置（目的：使 `stale` 可判定）。

## F5（非阻断）—— window5 结果未标 superseded

- `report/evidence/S4-T34/bringup_window6_20261028_r03/results_window5.json`（`conclusion=WINDOW6_STOPPED_ON_FAILURE`）已被 `report/evidence/S4-T34/bringup_window6_20261028_r03/results_window6.json`（`conclusion=WINDOW6_ALL_PASS`）取代；
- 修正口径：`supersession.json` 登记取代关系与原因（原文件**不删不改**）。

## F6（非阻断）—— 长跑 `failures=None` 缺词面

- `report/evidence/S4-T34/bringup_longrun_20261028_r01/results_longrun.json` 的 `conclusion=LONGRUN_STOPPED_ON_FAILURE`，但 `W2_longrun.parsed` 为空 ⇒ `failures=None`；
- 修正口径：`supersession.json.criteria_wording` 明确该情形词面为 **`CRITERIA_UNREACHED`**（未达判据，非“零失败通过”）。

## F7（非阻断）—— window5 统计口径事后定义

- window5 的失败步统计口径（P0/P1 只有 `exit_code` 无 `status`）是在事后于 `results_window6.json` 中重算；
- 修正口径：`supersession.json` 同时登记该口径修正说明（原 `results_window5.json` 保留）。

## 结论

- 7 条均为**账本/口径问题**，不改变任何实测结果；F1 由 `ledger_reference.json` 消除矛盾引用；
- 冻结成员（`docs/stage4/S4D_m4b_csr_semantics_*`）与已提交证据文件**均未修改**。

**边界**：离线；`ENABLE=0`；未烧 QSPI；未改线；未 push；不主张 G3/G4/G5；M3/M2 未闭合。
