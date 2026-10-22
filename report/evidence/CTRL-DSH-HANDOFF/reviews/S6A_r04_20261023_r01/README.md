# S6-A r04 独立复评记录（PASS）

- 被审版本：`D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，提交 **`b20b670`**（契约 `S6A-G0-v1.3`）
- 评审方：DSH 项目总控派出的**第 4 位独立 Reviewer 子代理**（与前三轮无关联；只读被审文件，全部写入隔离目录 `tmp/review/S6A_r04_20261023_r01/`）
- 时间（UTC+8）：2026-10-23 01:45–01:56
- **结论：`PASS`（阻断 0 项；非阻断 5 项）**
- 边界：只覆盖 r04 的 S6-A 包，**不代表 G0/G2/G4/G5**，不涉及 6-B/6-C/6-D/6-E、状态机实现、摄像头、HDMI、板卡、`hw_server`。自检 `ALL_PASS` 仅表示规格一致性／算术／证据存在性复算通过。

## 1. 评审实际执行（真实退出码）

| 检查 | 结果 |
|---|---|
| r04 全量自检（绝对 `--project-root` + `--evidence-dir/--manifest/--state`） | **exit 0，ALL_PASS，17 项全 PASS，errors=0**；与入库 `selfcheck_result.json` 状态与 detail 逐字一致 |
| `check_stage_delivery --mode inputs` / `--mode evidence` | 均 **exit 0 / CHECKS_OK**；输出与提交的 `*_mode_output.txt` 逐字节相同 |
| 旧包重跑（`git cat-file blob` 原始字节 + 最终版自检，隔离复刻） | **r01 exit 1（14 项）**、**r02 exit 1（C7/C12/C13/C17）**、**r03 exit 1（C7/C12/C17）**；失败集与详情与提交的三份失败证据**逐字一致** |
| 自算哈希 | json `c6c11ed3…`、doc `f33e9a72…`、cases `e53a965a…`；`hashes_sha256.txt` 21 条全部通过 |

## 2. 逐项结论

- **R3-B01 真关闭**：§12 `T6-S02`/`T6-L02` 两行已绑 `WINDOW_MATCH` / `t_last_target_continues`，锚点在三处有定义且与 M10/B10 一致；`matched_frames`/`t_last_match`/`t_submit+` 字面残留全部位于「已废弃」禁令句或修订说明内，**无规范性用法**。评审用**故障注入**验证 C12 扫描有判别力（改回旧写法→FAIL；把"废弃"标注挪远>60 字符→**仍 FAIL**）。
- **R3-B02 真关闭**：评审**自写**独立双向比较（transitions + behavior_rows）→ `TARGET_CONTINUES`/`WINDOW_MATCH` 均 only_forward=[]、only_reverse=[]，**完全双向一致**；`M1` 只声明 `TARGET_CONTINUES`；`M5`/`B13` 均无 `predicates_used` 且叙述与 JSON 一致。C12 双向断言经 **6 项注入**（含 only_forward/only_reverse/M1 过声明/未定义谓词/新增 STABLE→CANDIDATE）**全部捕获**。
- **STABLE 锁存**：唯一答案「本次获取内锁存」，`from ∈ {STABLE,*}` = `['M2','M5','M10']` 与声明一致、`STABLE→CANDIDATE` = 0；C17 经 3 项注入验证有效。评审**自建四情形推演**（窗口失效／score 跌破 P02／抖动耗尽／冷却门开启）→ 状态与动作均唯一确定。
- **参数纪律与无回归**：24 项参数**逐字段差异 = 0**、全部 `PENDING_APPROVAL`；ID 集合全等，差异**恰好**为声明新增（`U6-16`、`predicate_binding_policy`、`stable_latching`、`time_anchors`）。**无"声明存在但缺失"的文件**；未发现任何虚假"已通过/已审查"声明。

## 3. 非阻断问题（供下一修订，不影响 PASS）

| # | 问题 | 关闭条件 |
|---|---|---|
| `N-r04-01` | `transitions.M5.condition` 未复述"**仅窗口推进帧**"限定，而 §4 锁存段与 `stable_latching.suppressed_trigger_release` 写了该限定 | 把限定补进 §4 与 JSON 的 M5 条件，并加 C12 文本断言（角落序列：锁存 + 门在 TIMEOUT 帧开启） |
| `N-r04-02` | `predicate_binding_policy.statement` 说"M5 与 B13 都有 `global_cooldown_gate` 绑定"，但 **B13 无该字段**（B13 的抑制由 H-10 承载） | 改为"M5 带该标记、B13 由 H-10 承载；两者都只有条件文本、均无 `predicates_used`" |
| `N-r04-03` | C12 不拒"空列表"：给 `M2` 加 `predicates_used: []` 后仍 `ALL_PASS`（当前 JSON 无此情况） | C12 增加"显式空列表=不合法"断言 |
| `N-r04-04` | C7 的 `window_span_ms=(len(frames)-1)*period_ms` 用整段序列跨度，与 §9"窗口首帧→第 `T6-S02` 个 `WINDOW_MATCH` 帧"不符（HC-29 写 320ms，真实 200ms）；两种口径下 `m3_fires` 相同，结论未受影响 | 公式改为按第 N 个匹配帧计算，或标注为宽松上界 |
| `N-r04-05` | w6 未跟踪 S6-B 草稿里 `src/stage6/s6_core.py` 引用了**不存在**的 `docs/stage6/S6B_stage6_state_machine_design_v1.md` | 修正引用或补文档；WIP 不得当作 S6-B 进展或实现依据 |

## 4. 处置

- 已派 `task-6`（N-r04-01..04 收尾 + S6-B 按 v1.3 开工）。
- 本记录只搬结论与边界；r04 的规格与证据仍在 w6，未复制到主树。