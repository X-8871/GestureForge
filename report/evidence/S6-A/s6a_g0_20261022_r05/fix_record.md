# S6-A 修订记录 v1.4 / r05（第 4 轮复评 5 项非阻断收尾）

- 任务：`S6-A`；被审基线：`b20b670`（r04，已 PASS）；新 RunId：`s6a_g0_20261022_r05`（r01..r04 均不覆盖）
- 复评来源：`report/evidence/CTRL-DSH-HANDOFF/reviews/S6A_r04_20261023_r01/REVIEW_r04.md`（`PASS`，0 阻断 / 5 非阻断）
- 阈值纪律：**24 项参数值与 `PENDING_APPROVAL` 状态未改**；未在测试集调参；未触碰硬件；S6-B WIP 不提交
- 状态：**PENDING_REVIEW**；本记录不构成“已审查/已通过”

| 项 | 处置 | 证据 |
|---|---|---|
| N-r04-01 M5 缺「仅窗口推进帧」限定 | M5 条件补（`state ∈ {OK,NO_HAND}`、`stale=false`、非重复、非倒序）；`window_advance_required` 与 `suppressed_trigger_release` 同步；C12 三处文本断言；新增 HC-30（门在 `TIMEOUT` 帧开启 → 无动作；门在 `OK` 帧开启 → 该帧触发） | JSON `transitions.M5`/`stable_latching`；文档 §4；HC-30；`probe_*` |
| N-r04-02 policy 措辞 | statement 改为「M5 带 `global_cooldown_gate` 标记、B13 由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段」，§4 与 STATE 同步 | JSON `predicate_binding_policy`；`.codex/STATE.md` |
| N-r04-03 空列表未拒 | C12 增加非空列表普适断言；注入用例 `empty_predicates_used` 证明可捕获 | `probe_summary.json` |
| N-r04-04 窗口跨度口径 | 改为「窗口首帧 → 第 `T6-S02` 个 `WINDOW_MATCH` 帧」（HC-29 320→200 ms）；`span_conventions_agree` 断言两口径一致 | C7；HC-28/29 |
| N-r04-05 悬空文档引用 | `src/stage6/s6_core.py` 改引用现有 v1.4 契约文件（WIP 不提交） | `src/stage6/s6_core.py` |

## 结论边界

- 探针只证明自检断言有判别力；`ALL_PASS` / `CHECKS_OK` 只覆盖规格一致性、算术边界、证据存在性与清单/文件绑定，不代表状态机行为、G0 复评、独立审查或实物验收通过。
- 回放/注入类结论仅限回放/注入输入；S6-A 包未运行任何状态机（S6-B 实现另立 RunId）。
