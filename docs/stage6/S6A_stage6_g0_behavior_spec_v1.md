# S6-A 阶段6 G0 包与交互行为表 v1

> **状态：`G0_PACKET_PENDING_APPROVAL`（待批准）。** 本文是阶段6 的 G0 交付包：阶段6 目标与范围、上游绑定与冻结状态、状态机架构硬不变量、**交互行为表 v1**、时间边界口径、异常与恢复行为、低 FPS 交互延迟口径。
> **本文未冻结任何阈值或验收指标。** 全部数值参数（分数门、窗口、帧数、冷却、样本数、指标门槛）一律登记为 **待批准**（`PENDING_APPROVAL`），由项目总控转呈 Wong 决定；在获批前，任何统计结果只能报告为「观测值」，不得据此宣称通过。
> **本轮未实现状态机、未执行任何测试、未上板、未接摄像头、未操作 HDMI。** 本文不含任何实测数据。
> 机器可读权威：`docs/stage6/s6a_stage6_g0_behavior_v1.json`（契约身份 `S6A-G0-v1`）。两者冲突时以 JSON 为准并回改本文；一致性由 `verification/s6_g0_selfcheck.py` 机器校验。
> **修订记录（v1.4 / r05，2026-10-23）**：本包已通过**第 4 轮独立复评** `S6A_r04_20261023_r01`（`PASS`，0 阻断 / 5 项非阻断），现按该 5 项非阻断建议收尾：**N-r04-01** M5 条件补「本帧必须为窗口推进帧（`state ∈ {OK,NO_HAND}`、`stale=false`、非重复、非倒序）」并与 §4 锁存段、JSON `stable_latching` 一致，自检 C12 增加该文本断言，新增手算样例 HC-30 覆盖「锁存 STABLE + 冷却门恰在 `TIMEOUT` 帧开启」并断言该帧无动作（B21）；**N-r04-02** M5/B13 绑定叙述精确化（M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段）；**N-r04-03** 自检 C12 增加「任何条目的 `predicates_used` 出现时必须为非空列表，显式空列表 `[]` 不合法」的普适断言，并由注入探针 `verification/s6a_r05_probe.py` 证明可捕获；**N-r04-04** C7 窗口跨度改为「窗口首帧 → 第 `T6-S02` 个 `WINDOW_MATCH` 帧」（HC-29 由 320 ms 修正为 200 ms），并断言与宽松序列跨度口径下 `m3_fires` 结论一致；**N-r04-05** 清理 S6-B WIP 中对不存在文档的引用（WIP 仍不提交）。**全部 24 项参数值与 `PENDING_APPROVAL` 状态未改。** 复评由项目总控另行安排；本包不因收尾而视为通过。
>
> **上一轮修订记录（v1.3 / r04，2026-10-23）**：本包针对**第三轮独立复评** `S6A_r03_20261022_r01`（`CHANGES_REQUIRED`，R3-B01/R3-B02 + N01..N05 + 观察项）修订：**R3-B01** §12 `T6-S02` 行改用「连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02`」、`T6-L02` 行改用 `t_now − t_last_target_continues ≥ T6-L02`，并在 §3/§12/§13 给出该锚点定义，自检 C12 增加禁用标识符扫描；**R3-B02** `predicates.used_by` 与全部 `predicates_used` **全量双向一致**（B03 补 `TARGET_CONTINUES`、B17 补 `WINDOW_MATCH`、`TARGET_CONTINUES.used_by` 补 B14、M1 收敛为仅 `TARGET_CONTINUES`），M5/B13 改为「只有条件文本 + `global_cooldown_gate` 绑定、无 `predicates_used` 字段」，自检 C12 增加全量双向断言；**观察项** STABLE 定论为「本次获取内锁存」（§4 + JSON `stable_latching` + 自检 C17 + U6-16）；N01..N05 同批修（H-10 统一 `t_last_submit`、HC-27 去自比较、HC-28/29 由逐帧 score/几何序列真推导、旧包重跑纳入构建器并落盘可复现脚本、C7 样例数 29、旧哈希成因措辞）。**全部 24 项参数值与 `PENDING_APPROVAL` 状态未改。** 复评由项目总控另行安排；本包不因修订而视为通过。
>
> **上一轮修订记录（v1.2 / r03，2026-10-22）**：本包针对**复评** `S6A_20261022_r02`（`CHANGES_REQUIRED`，BLK-1/BLK-2/BLK-3 + NBL-1..NBL-5）修订：**BLK-1** 谓词拆分落到全部迁移与行为行（M3 改 `WINDOW_MATCH`；M10/B10 绑 `TARGET_CONTINUES`；M8/M9/M15/B04/B12 与 §12 同步；`predicates.used_by` 补 M3/M10；自检 C12 增加迁移/行为行断言）；**BLK-2** 旧包哈希改用 `git show 1fe4648:` 原始字节重算并重跑失败证据；**BLK-3** 入库自检改用 `--manifest`+`--state` 完整 C11 并落盘检查输出；NBL-1..5 同批修（inputs 清单 checks 实测、`t_last_submit` 单一名词、边界样例真算、§15 表头、B-05 措辞更正）。**全部参数值与 `PENDING_APPROVAL` 状态未改。** 复评由项目总控另行安排；本包不因修订而视为通过。
>
> **更早修订记录（v1.1 / r02，2026-10-22）**：针对独立评审 `S6A_20261022_r01`（`CHANGES_REQUIRED`，B-01..B-05 阻断 + N-01..N-10）修订，按项目总控裁定关闭：**B-01** 真实生成证据清单与真实退出码；**B-02** `NO_HAND` 不推进匹配计数、零框不得完成稳定窗口（H-4 与 JSON 同步改写）；**B-03** 冷却改为**全局门**（任意状态/任意获取在 `t_last_submit + T6-K01` 内不得提交动作，新增 H-10）；**B-04** 窗口完成时刻 = 第 N 个 `WINDOW_MATCH` 结果到达时刻，`W_min` 仅下界且不进入延迟统计；**B-05** 拆分 `TARGET_CONTINUES` 与 `WINDOW_MATCH` 两个唯一谓词并全表引用。另修 N-01..N-10（M14 删除、`A_DISPLAY_STATE` 删除、可达性登记、覆盖声明收敛、手算样例补实、±1 单位口径、措辞去“冻结/DONE”）。**全部参数值未改、24 项仍全部 `PENDING_APPROVAL`。** 复评由项目总控另行安排；本包不因修订而视为通过，也不代表独立审查通过。

---

## 0. 定位、范围与不宣称项

- 阶段目标（计划 L102–L108）：**稳定手势判定 → HDMI 切图 / 界面 / 显示状态**；冻结多框目标选择、目标丢失与重获、稳定判定窗口、保持时是否只触发一次、冷却、重新触发条件、无手/未知输入与恢复行为。
- 上轮结果（计划 L106）沿用为**强化建议**，不是已批准门槛：已知手势有效动作成功率 ≥90%、≥200 个独立未知输入误接受率 ≤5%、无有效手势 30 分钟误动作 ≤1 次。三项与样本数一律见 §14，状态 `PENDING_APPROVAL`。
- 本轮**只做 6-A**（操作文档 `CDX-20261022-012` §2）：G0 与行为表。6-B（实现可独立测试的状态机）、6-C（确定性测试矩阵）、6-D（无摄像头两级联调）、6-E（真摄像头验收与统计）全部 `NOT_RUN`。
- **边界**：交互通过不代替阶段7 最终性能与可靠性验收；注入/回放获得的任何结论只对「回放/注入输入」有效，不得冒充真实摄像头验收（真手势验收因摄像头不可用而延期）。
- 不宣称：G0 已通过；阈值已冻结；接口已集成验收；状态机已实现；任何板上/摄像头/HDMI 已实测。

## 1. 工作树、基线与上游绑定

- 工作树 `D:\codex-worktrees\w6`，分支 `stage6-interact-prep`，起始提交 `d8bc70e43572a8e44ddcd4b3489166e28a1c6151`（开工只读核验：工作区干净、`index.lock` 解析为 `D:/FPGA_Competition/.git/worktrees/w6/index.lock` 且不存在）。本阶段独占写入方 = 阶段6 总控；`main`/`w4`/`w5`/`dbdf`/`w2b`/厂商原件只读。
- 上游绑定与冻结状态（只读，哈希见 §17 与 JSON `upstream`）：

| 来源 | 用途 | 冻结状态 | 阶段6 可用性 |
|---|---|---|---|
| `docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md` | 类别顺序、`score` 语义与阈值 0.25、NMS IoU 0.45、≤15 框、稳定同分顺序、比较容限 | **G0_FROZEN** | 可直接引用并作为集成依赖 |
| `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md` L102–L108 | 阶段6 目标、测试场景与沿用建议 | 现行正式计划 | 可直接引用 |
| `docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md`、`…/S1-T02-D6_检测评估口径与离线指标基础.md` | `no_hand` 语义、评估口径 | 阶段1 冻结件 | 可直接引用 |
| `w4/docs/stage4/s4a_stage4_g0_fields.json`（`DRAFT_NOT_FROZEN`） | 结果记录字段、`state` 枚举、缺失值/丢帧/过期口径 | **草案，未冻结** | 只能作草案/隔离测试输入；**不得**作集成验收依赖 |
| `w5/docs/stage5/S5A_stage5_display_g0_spec_v2.md`（`STAGE5_G0_FINALIZED_OFFLINE_NOT_ACCEPTED`） | 画面语义（最新结果叠加）、`age_result`/`age_frame`、过期常量、零框规则 | 离线定稿，**未验收** | 只能作草案输入；显示侧新增 HUD 字段需与阶段5 协调 |
| `w5/docs/stage6/*`（v1 草案 + 阶段5 修订建议 S6-D-01…05） | 行为表起点 | **草案，未冻结** | 作为起点，逐条核对后由本阶段自行冻结语义 |

- **G0 就绪性结论（本阶段自评，不代表批准）**：接口语义对本轮**离线/隔离**工作足够明确；但**直接上游（阶段4 结果记录、阶段5 显示契约）均未冻结**，因此阶段6 的集成验收依赖 `BLOCKED`，只能先做离线规格与注入驱动自测。此项须由项目总控转呈 Wong。
- **上游并发写入事实（2026-10-22 19:12–19:22 观测）**：阶段4 工作树 `w4` HEAD 仍为 `73c3dad`，但其 `s4a_stage4_g0_fields.json` 与 `S4A_stage4_g0_tracking_and_timing_draft.md` 出现**未提交修改**（另有 S4B 共享输入契约、S4-C02 证据、`s4_inject_frame.c` 等新增未跟踪文件），即阶段4 窗口正在写入。本 G0 消费的是**提交版本 `73c3dad`** 的这两份文件；工作副本已漂移（`s4a_stage4_g0_fields.json` 由 `3524d02a…` 变为 `657ea2fb…`），漂移记录见 `upstream_bindings.json`。因此阶段4 契约**既未冻结、也仍在变动**，阶段6 集成验收依赖继续 `BLOCKED`。阶段5 工作树 `w5` HEAD 由 `e4533e1` 推进至 `875e487`，但本阶段引用的三份 w5 文件哈希未变。

## 2. 架构硬不变量（不可协商）

- **H-1 纯核心**：状态机核心的输入 = 一条结果记录 + 显式单调时间 + `session_id`；输出 = 状态转移与动作请求。核心**不得**直接读摄像头、系统墙钟（wall clock）、HDMI 或任何硬件寄存器；时间一律由调用方注入。
- **H-2 动作层隔离**：动作执行层单独实现，负责提交动作、返回 `success/fail/unobserved` 与生效时刻；日志保留 `action_id` 与来源 `frame_id`，防止重复发送导致重复动作。
- **H-3 单调时钟**：所有超时/失踪/冷却/窗口计时按单调时钟推进；停帧、重复帧或被丢弃的帧**不得**把状态永久卡在候选。系统墙钟不得参与任何判定。
- **H-4 窗口序列与匹配计数分离**：窗口**序列**按结果条数（result）推进，仅由 `state ∈ {OK, NO_HAND}`、`stale=false`、非重复、非倒序的结果推进；但**匹配计数只由 `WINDOW_MATCH` 成立的结果推进**。`NO_HAND`（合法零框）推进时间与结果计数、**不推进匹配计数、不得完成稳定窗口**；`TIMEOUT/ERROR/DROPPED` 不推进序列与匹配计数，但必须推进时间并计入异常。
- **H-5 `NO_HAND` 是合法零框**：不是第六类、不是未知、不是错误；不得被改写为未知，也不得把其他空标签改写为 `NO_HAND`。
- **H-6 未知拒绝不可自证**：不得以「`class_id` 落在五类内」证明未知拒绝。五类模型可能把未知场景判为已知类，故未知拒绝只能由 §11 的独立未知样本统计（未发生已提交动作）支撑，且样本必须包含「高分误识别」场景。
- **H-7 独立预期**：所有测试的预期序列必须由行为表独立推导或人工手算；**禁止**运行状态机生成 expected 后自我比较。
- **H-8 事件二分**：`ACTION_SUBMITTED`（提交成功）与 `ACTION_EFFECTIVE`（实际生效）是两类事件，必须分别记录、分别统计；提交成功不等于生效。
- **H-9 无硬件授权**：本阶段不得触碰板卡/JTAG/COM4/`hw_server`/HDMI 实物/摄像头，不得烧录。
- **H-10 冷却全局门**：自最近一次真实提交 `t_last_submit` 起 `T6-K01` 内，**任何状态、任何获取（含目标丢失后重获、异常恢复、目标切换）都不得提交动作**；展示状态 `COOLDOWN` 因丢失/异常提前退出**不解除**该门。门在动作执行前检查，命中记 `S_COOLDOWN`；被抑制或失败的提交尝试不更新 `t_last_submit`。

## 3. 术语与输入/输出事件

- **结果记录（result）**：某个 `frame_id` 的一次检测结果，可为零框；字段与 `state` 枚举沿用阶段4 草案（`OK`/`NO_HAND`/`TIMEOUT`/`ERROR`/`DROPPED`）。
- **当前目标（current target）**：状态机正在跟踪的一个具体检测框实例（`class_name` + 归一化 `xyxy` + `score` + 来源 `frame_id`）。
- **获取（acquisition）**：从某目标**首次**被选为当前目标，到该目标**丢失确认**（LOST）或**切换到另一目标**之间的连续区间。一次获取最多触发一次（§10）。
- **`TARGET_CONTINUES`（目标保持判定；仅用于迟滞/跟踪，不用于窗口计数）**：本帧存在与当前目标「类别相同」且「`IoU ≥ T6-P03` 或 归一化中心位移 ≤ `T6-P04`」的框。**不含** `score ≥ T6-P02`，也**不含**逐帧位移 `T6-P05`。
- **`WINDOW_MATCH`（窗口推进判定；仅用于稳定窗口计数）**：在 `TARGET_CONTINUES` 成立的框上，再满足 `score ≥ T6-P02` **且** 与前一个 `WINDOW_MATCH` 帧的归一化中心位移 ≤ `T6-P05`。稳定窗口帧数、抖动容忍、稳定判定一律使用 `WINDOW_MATCH`。
- **`t_last_target_continues`（丢失时间锚点）**：最近一次 `TARGET_CONTINUES` 成立的结果的显式输入时刻；`TARGET_CONTINUES` 不成立的结果不更新该锚点；被抑制或失败的动作尝试不更新该锚点（该锚点只由逐帧 `TARGET_CONTINUES` 判定更新）。用于 M10/B10 的 `T6-L02` 时间条件（定义见 §12）。
- **用词约束**：本文与 JSON 不再使用无修饰的“匹配”一词指代上述两类判定；需要时写全 `TARGET_CONTINUES` 或 `WINDOW_MATCH`（B-05）。
- **窗口序列推进帧**：`state ∈ {OK, NO_HAND}` 且 `stale=false`、`frame_id` 非重复、非倒序的结果。`NO_HAND` 属于窗口序列推进帧（推进时间/结果计数），但**不是** `WINDOW_MATCH`、不推进匹配计数；零框不得完成稳定窗口（H-4/B17）。
- **异常（anomaly）**：`E_FRAME_INVALID`（类别越界/非 finite/框数超限/字段不自洽）、未知类别、`TIMEOUT`、`ERROR`、`DROPPED`。
- 输入事件：`E_FRAME_RESULT`、`E_FRAME_TIMEOUT`、`E_FRAME_ERROR`、`E_FRAME_DROPPED`、`E_FRAME_STALE`、`E_FRAME_INVALID`、`E_FRAME_DUPLICATE`、`E_FRAME_CONFLICT`、`E_FRAME_OUT_OF_ORDER`、`E_SESSION_RESET_SUSPECTED`。
- 输出事件（动作，§7）：`ACTION_SUBMITTED`、`ACTION_EFFECTIVE`、`ACTION_FAILED`、`ACTION_UNOBSERVED`；抑制事件：`S_DEDUP`、`S_COOLDOWN`、`S_TARGET_HELD`、`S_JITTER_TOLERATED`、`S_WINDOW_TIMEOUT`、`S_CONFLICT_RESOLVED`。
- 必须记录的日志字段（沿用草案并补齐二类事件）：`session_id`、输入与结果 `frame_id`、输入 `state`、`age_result_ns`、`age_frame_ns`、前后状态、转移编号、计时器值、`action_id`、`action_type`、`target_id`、`trigger_frame_id`、`t_trigger`、`t_submit`、`t_effective`、`submit_result`、`effective_result`、`suppressions`、计数（`invalid/dropped/timeout/stale/false_actions`）、`warmup`。

## 4. 状态集合与迁移

状态（命名固定）：`IDLE`、`CANDIDATE`、`STABLE`、`TRIGGERED`、`COOLDOWN`、`LOST`、`UNKNOWN_RECOVER`。状态名**不代表实现已存在**。

| 编号 | 从 → 到 | 条件 | 优先级 |
|---|---|---|---|
| M1 | `IDLE` → `CANDIDATE` | 存在通过 §8 选择的目标，且连续 `T6-C01` 条窗口推进帧为同一目标（同一目标由 `TARGET_CONTINUES` 判定，不以 `WINDOW_MATCH` 计数） | P4 |
| M2 | `*`（任意状态） → `UNKNOWN_RECOVER` | 连续 `T6-U00_W` 条结果内异常数 ≥ `T6-U00_N` | P1 |
| M3 | `CANDIDATE` → `STABLE` | 连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02` 且窗口时长 ≥ `T6-S01`（**取较晚**满足者）；**不得按 `TARGET_CONTINUES` 计帧**（低分目标不得进入 STABLE） | P3 |
| M4 | `CANDIDATE` → `IDLE` | 抖动容忍耗尽（`> T6-J01` 帧不满足 `WINDOW_MATCH`）且候选停留 ≥ `T6-S04`；仅在 M10 未命中时求值。**当前草案 `T6-S04`=500 ms ≥ `T6-L02`=300 ms，M10 先命中，故 M4 在本轮参数下不可达**（见 JSON `reachability`、U6-12） | P3 |
| M5 | `STABLE` → `TRIGGERED` | 触发一次动作并记录 `ACTION_SUBMITTED`；**仅当本次获取尚未触发、且全局冷却门已结束**（`t_now − t_last_submit ≥ T6-K01`，无提交记录视为已结束）**且本帧必须为窗口推进帧**（`state ∈ {OK, NO_HAND}`、`stale=false`、非重复、非倒序）时可用；异常/过期/重复/倒序/缺帧帧即使恰逢门开启也不得触发（B18/B21/B22/B23、§13） | P3 |
| M6 | `TRIGGERED` → `COOLDOWN` | 动作提交事件落盘（同帧或下一帧） | P3 |
| M7 | `TRIGGERED` → `LOST` | 提交前目标已丢失。**M5 为同步提交，`TRIGGERED` 之后的提交前丢失没有独立路径，故 M7 在本轮实现中不可达**（见 JSON `reachability`） | P3 |
| M8 | `COOLDOWN` → `IDLE` | 冷却结束且当前目标 `TARGET_CONTINUES` 不成立/已丢失 | P3 |
| M9 | `COOLDOWN` → `STABLE` | 冷却结束、同一目标仍满足 `TARGET_CONTINUES` 且 `WINDOW_MATCH` 窗口再次满足 → **维持态，不再触发** | P3 |
| M10 | `*`（任意有目标状态） → `LOST` | 连续 `T6-L01` 条推进帧 `TARGET_CONTINUES` 不成立 **或** 距上一次 `TARGET_CONTINUES` 成立（`t_last_target_continues`）≥ `T6-L02`（取**较早**满足者）；**不得用 `WINDOW_MATCH` 判丢失**（低分但几何连续的目标仍维持） | P2 |
| M11 | `LOST` → `IDLE` | 丢失确认后立即清空当前目标与稳定证据 | P3 |
| M12 | `UNKNOWN_RECOVER` → `IDLE` | 连续 `T6-U01` 条合法结果且无未知类别 | P5 |
| M13 | `UNKNOWN_RECOVER` → `UNKNOWN_RECOVER` | 期间再次出现异常（按 §11.4 重置规则） | P1 |
| M15 | `COOLDOWN` → `CANDIDATE` | 冷却结束、目标仍满足 `TARGET_CONTINUES` 但 `WINDOW_MATCH` 窗口未满足；**该路径达到稳定也不再触发** | P3 |

- **M14 已删除（r02）**：`M10→M11` 使 `LOST` 立即回到 `IDLE`，故原 M14 的 `LOST` 分支不可达、`IDLE` 分支与 M1 同效；重获统一表达为 `M10→M11→M1`（新 `acquisition_id`）。删除记录见 JSON `revision.deleted_transitions`。
- **全局冷却门不依赖展示状态**：即使 M10/M11 使状态提前离开 `COOLDOWN`，`t_last_submit + T6-K01` 内的任何 M5 仍被 H-10 抑制。
- **STABLE 锁存（观察项定论，待 G0 确认 U6-16）**：STABLE 在本次获取内锁存：进入后不因窗口中断、score 跌破 T6-P02 或抖动耗尽而退回 CANDIDATE；离开 STABLE 仅有 M2（异常，P1）、M10（丢失确认，P2）、M5（触发，P3）三条路径。冷却门未结束时 M5 被 H-10 抑制，状态停留 STABLE；门开启后的下一条窗口推进帧即可触发，无需重新累积窗口证据。
- **M5/B13 的谓词绑定现状（R3-B02 / N-r04-02）**：M5 带 `global_cooldown_gate` 标记、B13 的抑制语义由 H-10 承载；两者都只有条件文本、均无 `predicates_used` 字段。
- 逐帧求值、首次命中即停；同一帧最多一条迁移；未命中候选写入 `transition_candidates` 并记录 `S_CONFLICT_RESOLVED`。
- 求值顺序：P1 异常（M2/M13）→ P2 丢失确认（M10）→ P3 当前状态推进（M5/M6/M8/M9/M15/M3/M4）→ P4 重获/获取（M1）→ P5 恢复（M12）。
- `CANDIDATE` 下 M4 与 M10 同帧同时满足时以 **M10 优先**（更长确认期优先）。
- 进入 `COOLDOWN`：**保留当前目标标识，重置稳定窗口证据**（帧计数、窗口起点、抖动计数归零）。冷却结束三种情形互斥且穷尽（M8/M9/M15），**不存在无出口的死状态**。

## 5. 行为表 v1

每行给出：条件 → 转移 → 输出 → 必须记录 → 判定依据 → 参数与批准状态。行为表 v1.1 基线已声明（状态 `DELIVERED_PENDING_APPROVAL`，**不是已批准、不是已冻结**）；**其中全部数值参数为待批准**。

| ID | 行为 | 条件 → 转移 | 输出/动作 | 必须记录 | 判定依据 | 参数（待批准） |
|---|---|---|---|---|---|---|
| B01 | 五类稳定触发 | 目标稳定（M3→M5） | 按 §7 表 A-1 提交唯一动作 | `ACTION_SUBMITTED` + `action_id`/`target_id`/`trigger_frame_id`/`t_submit` | 计划 L104 | `T6-S01/S02`、`T6-P01/P02` |
| B02 | 提交成功 ≠ 实际生效 | M5 后执行层回执 | 分记 `ACTION_SUBMITTED` 与 `ACTION_EFFECTIVE`；`fail`/`unobserved` 单列 | `submit_result`、`effective_result`、`t_effective` | 运行手册 §2.3；H-8 | 无 |
| B03 | 多框维持优先 | 存在与当前目标 `TARGET_CONTINUES` 成立的框 | 维持当前目标；即使他框类别不同且分更高也维持 | `S_TARGET_HELD` + 两条候选信息 | 计划 L104 | `T6-P03/P04` |
| B04 | 分数优先 | 当前目标 `TARGET_CONTINUES` 不成立时选最高分框 | 新目标 → 重新累积证据 | 选择依据与新目标字段 | 计划 L104 | `T6-P01` |
| B05 | 同分排序 | 分数完全相等 | 按 2A 冻结稳定顺序；`source_order` 可用时以其为权威 | 两者 `score` 与 `source_order` | 2A L75/L77 | 无（2A 冻结） |
| B06 | 禁止未冻结启发式 | 任何选择/排序 | 不得按面积、像素位置、"中央优先"重排或加权重排 | — | 2A L77 | 无 |
| B07 | 稳定窗口 | 连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02` 且窗口时长 ≥ `T6-S01`；**完成时刻 = 第 N 个 `WINDOW_MATCH` 结果到达时刻**；`NO_HAND` 不计入 | M3 进入 `STABLE`（取较晚满足者） | 帧计数、窗口起点、两条件各自满足时刻、完成时刻 | 计划 L104；评审 B-02/B-04 | `T6-S01/S02/S03` |
| B08 | 抖动容忍 | 窗口内短暂中断（窗口推进帧不满足 `WINDOW_MATCH`） | 中断 ≤ `T6-J01` 帧不重置；`= T6-J01+1` 立即重置 | `S_JITTER_TOLERATED` 或窗口重置原因 | 计划 L106 | `T6-J01` |
| B09 | 目标保持 | `TARGET_CONTINUES` 成立 | 获取延续，窗口不重启（证据连续） | `TARGET_CONTINUES 依据（IoU/位移）` | 计划 L104 | `T6-P03/P04/P05` |
| B10 | 丢失确认 | 连续 `T6-L01` 条推进帧 `TARGET_CONTINUES` 不成立 或 距上一次 `TARGET_CONTINUES` 成立（`t_last_target_continues`）≥ `T6-L02` | M10→M11 清空目标与证据；**不产生动作** | 丢失原因分类 + 满足的是帧条件还是时间条件 | 计划 L104 | `T6-L01/L02` |
| B11 | 重获 | `LOST`→`IDLE` 后同类目标再现并满足窗口 | 视为**新的独立获取**，可再次触发一次（受冷却约束） | 新获取的 `acquisition_id` | 计划 L104 | `T6-S01/S02` |
| B12 | 目标切换 | 当前目标 `TARGET_CONTINUES` 不成立且出现另一合法目标 | 切换 → 丢失/重获路径；新目标必须重新满足窗口 | 旧/新目标字段与切换原因 | 计划 L106 | `T6-P01/P03/P04` |
| B13 | 冷却抑制（全局门） | 自 `t_last_submit` 起 `t_now − t_last_submit < T6-K01`，**任意状态/任意获取** | 抑制**全部**触发（含其他目标、含目标丢失后重获），记录被抑制对象与剩余时间 | `S_COOLDOWN` + 目标与分数 + 剩余时间 | 计划 L104；评审 B-03；H-10 | `T6-K01` |
| B14 | 冷却结束三分支 | `t_now − t_last_submit ≥ T6-K01`（含等号） | `TARGET_CONTINUES` 成立且 `WINDOW_MATCH` 窗口满足→M9 维持（不触发）；`TARGET_CONTINUES` 成立但窗口未满足→M15 候选（不触发）；`TARGET_CONTINUES` 不成立/丢失→M8 `IDLE`。三分支只决定展示状态出口，**不解除全局冷却门** | 分支判定证据 | 计划 L104；评审 B-03 | `T6-K01` |
| B15 | 持续保持只触发一次 | 同一获取内目标持续稳定（含冷却后） | **恰好一次** `ACTION_SUBMITTED`；二次触发只允许来自新获取 | `acquisition_id` 与触发计数 | 计划 L104；本文 §10 | 无 |
| B16 | 动作去重窗口 | 相同 `(action_type,target_id)` 在 `T6-A02` 内重复提交 | 抑制并记录 | `S_DEDUP` | H-2 去重日志要求；CDX-20261022-012 §2.3（提交/回执分离） | `T6-A02` |
| B17 | 无手（零框） | `state=NO_HAND` | 合法结果：`IDLE` 下保持 `IDLE`；有目标时计入丢失判定；**不推进匹配计数、不得完成稳定窗口**；只推进时间与结果计数 | `boxes=0`、`no_hand` 计数 | 计划 L104；D2 L22；H-4/H-5；评审 B-02 | 无 |
| B18 | 过期结果 | `stale=true` | **不得触发**；可作非 `WINDOW_MATCH` 推进时间；必须显式标注年龄 | `E_FRAME_STALE`、`age`、`stale_cleared` | 计划 L98；阶段5 C-03 | `T6-STALE_LIMIT` |
| B19 | 未知类别/非法结果 | `class_id ∉ 0..4` 或非 finite/框数 >15/字段不自洽 | 丢弃该帧证据、计入异常；**不得**改写为 `NO_HAND` | `E_FRAME_INVALID` + 原始类别值 | 2A L77（classes=5、≤15 框）；D9 输出契约；D2 L22 仅提供空标签语义 | `T6-U00_*` |
| B20 | 未知场景（合法类别） | 未知手势被模型判为已知类 | 按正常检测处理但只能触发已定义动作；**拒绝能力不得由 class_id 证明** | 未知样本标识与场景类型 | 运行手册 §2.9；H-6 | 指标 `T6-02` |
| B21 | 超时/错误/丢帧 | `TIMEOUT`/`ERROR`/`DROPPED` | 无动作；推进时间、不推进匹配计数；计入异常；达阈进 `UNKNOWN_RECOVER` | 各自的 `error_code` 与计数 | 运行手册 §2.10；H-4 | `T6-U00_*`、`T6-U01` |
| B22 | 重复 `frame_id` | `frame_id` 等于上一条已处理值 | 幂等丢弃，不推进任何计数与状态；内容不同则判冲突 | `E_FRAME_DUPLICATE`（或 `E_FRAME_CONFLICT`） | 运行手册 §2.7 | 无 |
| B23 | 倒序 `frame_id` | `frame_id` 小于上一条已处理值（同 `session_id`） | 不推进窗口，计异常；不得延续旧会话状态 | `E_FRAME_OUT_OF_ORDER` | CDX-20261022-012 §4 测试矩阵第 8 行；本文 §13 | `T6-U00_*` |
| B24 | 缺帧 | `frame_id` 跳号（无结果且无 `DROPPED` 记录） | 由后续结果时间戳推进时间；不推进匹配计数；每个缺帧只计一次 | `dropped_frames` 累计 | 阶段4 丢帧互斥口径 | 无 |
| B25 | 重启/会话切换 | `session_id` 变化，或同会话 `frame_id` 大幅回退 | 全量复位到 `IDLE`（清目标与证据）并显式标记；**禁止**静默续用 | `E_SESSION_RESET_SUSPECTED`/新 `session_id` | 阶段4 `frame_id_allocation` | 无 |
| B26 | 时间边界 | 等于阈值 / 阈值 ±1 单位（帧类 1 条结果；时间类 1 ns；分数/几何 1 ULP） | 见 §12 逐条（除过期用严格 `>`，其余 `≥`）；未覆盖参数见 §12.1 缺口登记 | 边界判定所用比较与两侧取值 | 运行手册 §4 | 全部数值参数（`T6-C01`/`T6-U00_W`/`T6-U00_N`/`T6-S04`/`T6-P01..P05`/`T6-U01` 边界样例待补，见 §12.1） |
| B27 | 低 FPS 交互延迟 | 帧周期 P 较大时 | `W_min=max(T6-S01,(T6-S02−1)·P)` **只是下界、不得进入延迟统计**；窗口完成时刻 = 第 N 个 `WINDOW_MATCH` 结果到达时刻（实测）；动作延迟与交互延迟分别报告 | `P_meas`、窗口完成时刻、两个延迟 | 运行手册 §2.7；评审 B-04 | `T6-A01`、`T6-A03`、`T6-S01`、`T6-S02` |
| B28 | 动作失败/未观察/重复回执 | 执行层返回 `fail`/`unobserved` 或重复 ACK | **不虚报成功**；`fail` 计失败；`unobserved` 单列按 `NOT_RUN` 处理，不从分母剔除 | `ACTION_FAILED`/`ACTION_UNOBSERVED`、重试计数 | 运行手册 §4/§6 | 指标 `T6-01` |

## 6. 状态机的"一条结果 + 显式时间"输入契约

- 每条输入 = `{session_id, frame_id, state, detections[], score, xyxy, capture_time_ns, result_time_ns, stale, dropped_frames, error_code}` + **显式 `t_input`（单调时钟，由调用方注入）**。
- `t_input` 在真机上取该结果的消费/判定时刻（与阶段4/5 同一 PS 单调时基）；在注入/回放中取注入时刻；两者必须在日志中声明来源（`time_source ∈ {board_monotonic, injected}`）。
- 核心**不得**调用 `now()`、读墙钟、读摄像头或读 HDMI；实现若需要等待，由外部驱动提供下一条结果与时间。

## 7. 五类手势的动作、成功/失败反馈与可观察显示状态

类别顺序固定 `fist, palm, one, two_up, three`（`class_id` 0..4，不得重排）。动作统一为**设置到具名显示状态**（幂等），不使用无回执的增量/切换语义：

**表 A-1（动作映射为提案，待批准）**。本轮 `supported_types` 仅 `A_SWITCH_UI` 与 `A_SWITCH_CHANNEL`；`A_DISPLAY_STATE` 在 r01 JSON 中登记但从未被任何类映射，r02 已删除（U6-15），若后续需要须回 G0 冻结。

| 类别 | `class_id` | 动作类型 | `target_id` | 期望可观察显示状态 | 成功反馈（`ACTION_EFFECTIVE`） | 失败反馈 |
|---|---|---|---|---|---|---|
| `fist` | 0 | `A_SWITCH_UI` | `UI_MENU` | HUD `active_display_state=UI_MENU`，界面为菜单 | `t_effective` 已记录且 `active_display_state == UI_MENU` | `ACTION_FAILED`/`ACTION_UNOBSERVED`；HUD 保持原状态并显示 `last_action_result` |
| `palm` | 1 | `A_SWITCH_UI` | `UI_STATS` | HUD `active_display_state=UI_STATS`，统计/叠框面板可见 | 同上，目标状态为 `UI_STATS` | 同上 |
| `one` | 2 | `A_SWITCH_CHANNEL` | `CH_1` | HUD `active_channel=CH_1` | 同上，目标为 `CH_1` | 同上 |
| `two_up` | 3 | `A_SWITCH_CHANNEL` | `CH_2` | HUD `active_channel=CH_2` | 同上，目标为 `CH_2` | 同上 |
| `three` | 4 | `A_SWITCH_CHANNEL` | `CH_3` | HUD `active_channel=CH_3` | 同上，目标为 `CH_3` | 同上 |

- **幂等性要求**：同一 `(action_type,target_id)` 在已处于该状态时重复提交不得产生额外可见变化，也不得计入新的获取；否则 `T6-01` 的成功口径不可复算。
- **可观察性要求**：动作是否生效必须可由**显示侧证据**（HUD 字段 + 画面/截图 + 五元组 `(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`）独立核对；**未观察不得算成功**。
- **提出的显示侧新增字段（需与阶段5 协调，未批准）**：`sm_state`、`active_display_state`（或 `active_channel`）、`active_target_id`、`last_action_id`、`last_action_result`。在阶段5 未采纳前，本阶段只能用五元组 + 既有 HUD 字段做离线断言。
- **提案状态**：上表的动作类型与 `target_id` 命名属阶段6 提案，未获批准前不得作为集成验收依赖；若某类改用「切换/增量」动作，必须同时定义幂等性与可观察回执，否则该类的 `T6-01` 统计无效。
- **逐类用户体验要求（r02 补，N-06；具体可见时长待批准）**：五类动作共用同一反馈骨架——生效必须有可观察显示状态变化（`ACTION_EFFECTIVE`）、失败/未观察必须显示 `last_action_result` 且不得虚报成功、同一动作重复提交不得产生闪烁或额外可见变化（幂等）；反馈不得遮挡手势置信信息。各类目标状态见表 A-1。具体反馈可见时长与过渡动画属待批准项（U6-14），获批前只能按「可观察、可区分、不虚报」做离线断言。

## 8. 多框选择与同分排序

按优先级逐帧求值（输入为该结果的 `detections[]`，已过 2A 阈值与 NMS、≤15 框、顺序即 D9 输出顺序）：

1. **维持优先（迟滞）**：若存在当前目标且本帧有与其 `TARGET_CONTINUES` 成立的框（类别相同 **且**（`IoU ≥ T6-P03` **或** 归一化中心位移 ≤ `T6-P04`）），继续使用该目标，**不受更高分他框影响**；出现更高分且类别不同的框时必须记录 `S_TARGET_HELD` 与两条候选信息。**迟滞只看 `TARGET_CONTINUES`，不看 `T6-P02`/`T6-P05`**（B-05）。
2. **分数优先**：否则在 `score ≥ T6-P01` 的框中取最高分者。
3. **平票**：`score` **逐位完全相等**时，按 2A 冻结稳定同分顺序（head → row-major cell → anchor-local → `class_id`）；`source_order` 可用时以其为权威（离散字段，2A 要求逐值相同）。`source_order` 构成全序，故任何平票都可确定解析。
4. **无目标**：全部框低于 `T6-P01`、零框、或结果非法 → 本帧"无目标"，按 M10/M2 处理。
5. **禁止**：不得按框面积、像素位置或未冻结顺序重排候选；新增启发式必须先回 G0 冻结并写入本文与 JSON。
6. **同一目标判定**：`TARGET_CONTINUES` 仅在**同一次获取内**用于迟滞；丢失确认后重新出现的同类目标一律视为**新获取**（§10），不存在跨丢失的目标身份延续假设。

## 9. 稳定窗口与抖动

- **窗口条件（全部满足）**：连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02` **且** 窗口持续时间 ≥ `T6-S01`，按 `T6-S03` 语义取**较晚**满足者。
- **窗口完成时刻**：第 `T6-S02` 个 `WINDOW_MATCH` 结果到达且时长条件同时满足的那一帧的显式输入时刻；`W_min=max(T6-S01,(T6-S02−1)·P)` **只是下界**，不得当作完成时刻（B-04）。
- 窗口每一帧（除允许中断外）都必须 `WINDOW_MATCH` 成立（类别不变、`score ≥ T6-P02`、与前一个 `WINDOW_MATCH` 帧中心位移 ≤ `T6-P05`）；窗口内不得出现 `E_FRAME_INVALID`。`NO_HAND` 帧不满足 `WINDOW_MATCH`，**不推进匹配计数、不得完成窗口**（B-02/H-4）。
- **抖动容忍**：窗口内允许至多 `T6-J01` 条不满足 `WINDOW_MATCH` 的窗口推进帧而不重置窗口（记录 `S_JITTER_TOLERATED`）；中断数达到 `T6-J01 + 1` 立即重置窗口。时间在中断期间**继续流逝**。
- **丢帧/超时/过期对窗口的影响**：均**不增加** `WINDOW_MATCH` 计数（时间继续流逝）；`TIMEOUT/ERROR/INVALID` 走 §11 异常路径；`stale` 帧不得触发。若因丢帧导致帧数条件在合理时限内无法满足，该次获取按超时处理并记录 `S_WINDOW_TIMEOUT`。
- **窗口序列来源**：窗口由**结果 `frame_id` 序列**推进（不是显示帧），且只由 `state ∈ {OK, NO_HAND}`、`stale=false`、非重复/非倒序的结果推进；序列来源必须在日志中声明。

## 10. 冷却、再触发与"持续保持只触发一次"的**唯一**解释

- **冷却（全局门，H-10）**：`T6-K01`，锚点 = `t_last_submit` = **最近一次真实 `ACTION_SUBMITTED` 的 `t_submit`**（`t_submit` = 执行层接受提交时的显式单调时刻；不用 `t_effective`，因其在 `fail`/`unobserved` 下无定义）。**被抑制或失败的提交尝试不更新 `t_last_submit`，不得延长冷却；无提交记录时门开放。** **`t_now − t_last_submit < T6-K01` 内，任何状态、任何获取（含目标丢失后重获/异常恢复/目标切换）都不得提交动作**，逐个记录 `S_COOLDOWN`；动作执行层在真正提交前再次校验该门。展示状态 `COOLDOWN` 提前退出（M10/M11/异常）**不解除**该门。
- **冷却结束（含等号）**后的三条分支互斥且穷尽：M9（维持，不触发）/ M15（回到候选，**不再触发**）/ M8（回 IDLE）。
- **`T6-A02` 去重窗口**独立于冷却：同一 `(action_type,target_id)` 在 `T6-A02` 内重复提交一律抑制并记录 `S_DEDUP`。

**唯一解释（本阶段正式声明，取代草案 A/B 之争）**：

> **一次获取只触发一次。** 获取 = 从某目标首次被选为当前目标起，到该目标丢失确认（M10→M11）或切换到另一目标（§8-B12）为止的连续区间。在该区间内，无论目标保持多久、无论冷却是否结束、无论窗口是否再次满足，**恰好产生一次 `ACTION_SUBMITTED`**。
> **允许第二次触发的唯一条件是「新的获取」且全局冷却门已结束**：即 (a) 目标丢失确认后重新满足稳定窗口；或 (b) 当前目标切换为另一个合法目标并重新满足稳定窗口；且提交时刻满足 `t_now − 上一次 t_submit ≥ T6-K01`。M15 路径（冷却结束后目标仍 `TARGET_CONTINUES` 但窗口未满足）**不是**新获取，其再次达到稳定只是维持态。
> 「保持期按周期重复触发」（草案备选 B）**不被采纳**；若后续需要，属实质语义变更，必须交 Wong 决策并同步改写本文 §10、M5 与 JSON（登记为 U6-02）。

## 11. 过期、未知、无手、超时/错误的行为与恢复

1. **无手（`NO_HAND`，零框）**：合法成功结果。`IDLE` 下保持 `IDLE`；有目标时计入丢失判定；不计入异常；**不推进匹配计数、不得完成稳定窗口**（B-02/H-4）；分区统计（`no_hand_frames` ≠ `unknown_frames`）。
2. **过期（`stale=true`）**：仅在 `state ∈ {OK,NO_HAND}` 有意义；`stale` 结果不得触发动作，也不得作为 `WINDOW_MATCH` 帧；必须记录年龄（`age_result_ns`/`age_frame_ns`）并计入 `stale_cleared`。过期门槛与阶段5 同源常量对齐，**严格大于**判过期（§12）。
3. **未知类别/非法结果**：`class_id ∉ {0..4}`、非 finite、框数超限、字段缺失/不自洽 → 丢弃该帧证据并计入异常；**不得**改写为 `NO_HAND`；必须记录原始类别值。
4. **未知场景（合法类别）**：模型可能把未知手势判为已知类。因此未知拒绝**不能**由「`class_id` 落在五类内」证明；只能由 §14 `T6-02` 的独立未知样本统计支撑，且样本必须包含「高分误识别」与「无手」两类，分别计数。`T6-02` 的样本清单（编号、来源、时长、SHA-256）必须**预先登记**，事后不得增删。
5. **超时/错误**：`TIMEOUT`（`error_code=5`）、`ERROR`（非 0 非 5；候选超限固定为 `BAD_ARGUMENT=1`）与 `DROPPED`：无动作、不推进匹配计数、推进时间、计入异常；达 `T6-U00_*` 阈值进入 `UNKNOWN_RECOVER`。
6. **异常计数与恢复**：在连续 `T6-U00_W` 条结果窗口内异常数 ≥ `T6-U00_N` → M2 进入 `UNKNOWN_RECOVER`；处于恢复态期间再次异常按同一窗口规则**重置计数起点**（M13）。连续 `T6-U01` 条合法结果（`OK`/`NO_HAND`，无未知类别、无异常）→ M12 回 `IDLE`，当前目标必须为空。**恢复期间禁止保留旧目标触发；恢复期帧不得计入稳定窗口。** 恢复后必须重新按 §8/§9 重获。

## 12. 时间边界表（等于阈值 / 前后 1 个单位）

比较语义固定如下；除过期用严格 `>`，其余全部取**含等号**（`≥`/`≤`）。**已列入本表的边界**在证据中有独立人工手算样例（`hand_computed_cases.json`）；未列入的参数边界见 §12.1 缺口登记，未覆盖前不得声称“全部参数边界已覆盖”（N-03）。异常判定窗口 `T6-U00_W`/`T6-U00_N` 为**滑动窗口**（最近 W 条结果内的异常数 ≥ N；重复 frame_id 不计入结果序列）。

| 项 | 比较 | 恰好等于阈值 | −1 单位 | +1 单位 |
|---|---|---|---|---|
| 稳定帧数 `T6-S02` | 连续 `WINDOW_MATCH` 帧数 ≥ `T6-S02` | 满足（进入判定） | 不满足 | 满足 |
| 稳定时长 `T6-S01` | `t_now − t_window_start ≥ S01` | 满足 | 不满足 | 满足 |
| 抖动 `T6-J01` | `missing ≤ J01` 容忍 | 容忍（不重置） | — | 重置（`J01+1`） |
| 丢失帧 `T6-L01` | `miss_streak ≥ L01` | 确认丢失 | 不丢失 | 确认丢失 |
| 丢失时间 `T6-L02` | `t_now − t_last_target_continues ≥ T6-L02` | 确认丢失 | 不丢失 | 确认丢失 |
| 冷却 `T6-K01` | `t_now − t_last_submit ≥ K01` | 冷却结束（可走 M8/M9/M15） | 抑制中 | 结束 |
| 去重 `T6-A02` | `t_now − t_last_submit < A02` 抑制 | 不被抑制 | 抑制 | 不被抑制 |
| 候选超时 `T6-S04` | `dwell ≥ S04`（配合 M4） | M4 可用 | 不可用 | 可用 |
| 选择门 `T6-P01` | `score ≥ P01` | 入选 | 淘汰 | 入选 |
| 稳定门 `T6-P02` | `score ≥ P02` | `WINDOW_MATCH` 成立 | 不成立 | 成立 |
| 追踪 IoU `T6-P03` | `IoU ≥ P03` | `TARGET_CONTINUES` 成立 | 不成立 | 成立 |
| 追踪位移 `T6-P04` | `d ≤ P04` | `TARGET_CONTINUES` 成立 | 成立 | 不成立 |
| 逐帧位移 `T6-P05` | `d ≤ P05` | `WINDOW_MATCH` 接受 | 接受 | 不接受（窗口中断，按抖动规则处理） |
| 过期 `T6-STALE_LIMIT` | `age > LIMIT` | **不过期**（严格大于） | 不过期 | 过期 |
| 未知恢复 `T6-U01` | `legal_streak ≥ U01` | 恢复 | 未恢复 | 恢复 |

- **丢失时间锚点 `t_last_target_continues`（R3-B01 定义）**：最近一次 `TARGET_CONTINUES` 成立的结果的显式输入时刻；`TARGET_CONTINUES` 不成立的结果不更新该锚点；被抑制或失败的动作尝试不更新该锚点（该锚点只由逐帧 `TARGET_CONTINUES` 判定更新）。M10/B10 的 `T6-L02` 条件与本表丢失时间行一律使用该锚点，**不得**再使用已废弃的 `t_last_match`（已废弃）。
- **"±1 单位"定义**：帧类参数为 1 条结果；时间类参数为 **1 纳秒**（上报毫秒值时必须在日志中保留纳秒原值，避免舍入歧义）；分数类为 1 个 float64 ULP；归一化几何为 1 个 float64 ULP；`IoU` 同理。HC-02（199.0 ms vs 200 ms）与 HC-08（499 ms vs 500 ms）为**毫秒级方向性样例**，只验证不等式方向与 `W_min` 下界，不声称测试了 ±1 单位；±1 ns 样例见 HC-07/HC-10/HC-11 与新增 HC-27（N-09）。

### 12.1 边界覆盖缺口（r02 登记，N-03）

下列参数在 r01 中没有独立手算边界样例，r02 补了可复算的规则样例（HC-21..HC-27）但仍不等于完成 §12 全部边界；**未覆盖前不得声称全参数边界已覆盖**：

| 参数 | 现状 | 说明 |
|---|---|---|
| `T6-C01` | 新增 HC-21（`=C01` 建立获取、`C01−1` 不建立） | 帧类边界 |
| `T6-U00_W` / `T6-U00_N` | 新增 HC-22（滑动窗口 `=N` 触发、`N−1` 不触发） | 明确为滑动窗口 |
| `T6-S04` | 新增 HC-23（可达性推导：草案值下 M4 不可达） | 规则可达性，不是运行时样例 |
| `T6-P01` / `T6-P02` | 新增 HC-24/HC-25（`=阈值` 通过、`−1 ULP` 不通过） | 分数门 |
| `T6-P03` / `T6-P04` / `T6-P05` | 谓词级边界（`=` 含等号、`+1 ULP` 不含） | 几何浮点边界无法用有限样例穷尽，登记为待补 |
| `T6-U01` | 新增 HC-26（`=U01` 恢复、`U01−1` 不恢复） | 恢复帧数 |
- 判定一律使用**未舍入原值**；比率保留 4 位小数仅用于展示。

## 13. 重复、倒序、缺帧、重启帧号

| 情形 | 判定 | 处理 | 记录 |
|---|---|---|---|
| 重复 `frame_id` | 等于上一条已处理 `frame_id` | 幂等丢弃（不推进计数/状态）；内容哈希不同则判 `E_FRAME_CONFLICT` 并按非法输入处理 | `E_FRAME_DUPLICATE` / `E_FRAME_CONFLICT` |
| 倒序 | `frame_id` 小于上一条已处理值且 `session_id` 未变 | 不推进窗口、不推进 `WINDOW_MATCH` 计数；计异常 | `E_FRAME_OUT_OF_ORDER` |
| 缺帧 | `frame_id` 跳号且既无结果也无 `DROPPED` 记录 | 时间由后续结果时间戳推进；不推进匹配计数；每个缺帧只计一次 | `dropped_frames` 累计 |
| 重启帧号/会话切换 | `session_id` 变化，或同会话 `frame_id` 大幅回退 | 全量复位到 `IDLE`、清目标与证据、开启新会话计数；**禁止**静默续用旧状态 | `E_SESSION_RESET_SUSPECTED` 或新 `session_id` |
| `frame_id` 回绕 | 达到 `0xFFFFFFFE` | 不得自然溢出到 0；必须新会话或显式复位（阶段4 约定） | 复位标记 |

- 上述任一情形**都不得触发动作**；即使不推进计数，超时/失踪计时**仍按单调时钟推进**（H-3）。
- 丢失时间条件（`T6-L02`）一律使用锚点 `t_last_target_continues`（定义见 §12）：重复、倒序、缺帧、重启帧号均**不得**更新该锚点。

## 14. 阈值与指标登记（**全部待批准**）

下表全部为 `PENDING_APPROVAL`：`草案值` 指上游草案建议或本 G0 提议，**不是**已批准门槛。批准权在 Wong（由项目总控转呈）。

| ID | 含义 | 单位 | 比较 | 草案值 | 批准状态 |
|---|---|---|---|---|---|
| `T6-A01` | 动作延迟上限（触发→生效） | ms | `≤` | 1000（草案） | PENDING_APPROVAL |
| `T6-A02` | 动作去重窗口 | ms | `<` 抑制 | 500（草案） | PENDING_APPROVAL |
| `T6-A03` | 交互延迟上限（手势起始→生效） | ms | `≤` | 无草案值（待定） | PENDING_APPROVAL |
| `T6-C01` | 进入候选的连续同目标帧数 | 帧 | `≥` | 2（草案） | PENDING_APPROVAL |
| `T6-S01` | 稳定窗口时长 | ms | `≥` | 200（草案） | PENDING_APPROVAL |
| `T6-S02` | 稳定窗口帧数 | 帧 | `≥` | 6（草案） | PENDING_APPROVAL |
| `T6-S03` | 稳定窗口判定逻辑 | — | `later_of` | 同时满足帧数与时长，取较晚满足者（草案） | PENDING_APPROVAL |
| `T6-S04` | 候选停留超时 | ms | `≥` | 500（草案） | PENDING_APPROVAL |
| `T6-L01` | 丢失确认帧数 | 帧 | `≥` | 5（草案） | PENDING_APPROVAL |
| `T6-L02` | 丢失确认时间 | ms | `≥` | 300（草案） | PENDING_APPROVAL |
| `T6-K01` | 冷却时长 | ms | `≥` | 1000（草案） | PENDING_APPROVAL |
| `T6-J01` | 窗口内可容忍中断帧数 | 帧 | `≤` | 1（草案） | PENDING_APPROVAL |
| `T6-U00_W` | 异常判定窗口长度 | 帧 | 滑动窗口 | 3（草案） | PENDING_APPROVAL |
| `T6-U00_N` | 异常判定阈值 | 帧 | `≥` | 3（草案） | PENDING_APPROVAL |
| `T6-U01` | 未知恢复所需连续合法帧数 | 帧 | `≥` | 5（草案） | PENDING_APPROVAL |
| `T6-P01` | 选择最小分数 | 分数 | `≥` | 0.35（草案；必须 ≥ 2A 冻结 0.25） | PENDING_APPROVAL |
| `T6-P02` | 稳定最小分数 | 分数 | `≥` | 0.30（草案） | PENDING_APPROVAL |
| `T6-P03` | 追踪最小 IoU | ratio | `≥` | 0.30（草案） | PENDING_APPROVAL |
| `T6-P04` | 追踪最大归一化中心位移 | 归一化 | `≤` | 0.15（草案） | PENDING_APPROVAL |
| `T6-P05` | 窗口内逐帧最大归一化中心位移 | 归一化 | `≤` | 0.05（草案） | PENDING_APPROVAL |
| `T6-STALE_LIMIT` | 过期门槛（与阶段5 同源） | ms | `>` 判过期 | 200（阶段5 已用同源常量；阶段4 仍 `DRAFT_PROPOSED`） | PENDING_APPROVAL |
| `T6-01` | 已知手势有效动作成功率 | ratio | `≥` | 0.9；样本 ≥50、每类 ≥10 | PENDING_APPROVAL |
| `T6-02` | 独立未知输入误接受率 | ratio | `≤` | 0.05；≥200 独立样本 | PENDING_APPROVAL |
| `T6-03` | 无有效手势 30 分钟误动作次数 | 次/1800s | `≤` | 1；单段 ≥30 分钟 | PENDING_APPROVAL |

- 统计口径要点（沿用并强化）：分母含全部预定义试验与失败，**禁止只挑成功视频**；`unobserved` 单列按 `NOT_RUN`，不得计入成功也不得从分母剔除；`T6-02`/`T6-03` 的误接受/误动作按**已提交**动作计数（`fail`/`unobserved` 不豁免）；置信区间默认 Clopper-Pearson 并单列；样本预先登记、独立性去重、分环境报告。
- `T6-S04` 当前草案 500 ms ≥ `T6-L02` 300 ms：M10 会在 300 ms 先命中，M4 在本轮参数下不可达（JSON `reachability`）。**本行不代表可实现覆盖**；建议 G0 决定 `T6-S04 < T6-L02` 或删除 M4/`T6-S04`（U6-12）。
- **本轮不得在正式测试集上调整上述任何值**；获批前的任何统计只能报告为「观测值」。

## 15. 低 FPS 下的交互延迟口径

- 术语：帧周期 `P` **必须取阶段4 实测值 `P_meas`**；未取得实测 P 时 `T6-A03` 记 `NOT_RUN`，**不得用假设 FPS 代替**（N-05/U6-13）。
- **`W_min`（只是下界，不得进入延迟统计）**：`W_min = max(T6-S01, (T6-S02 − 1) · P_meas)`；N 个连续结果只跨越 `(N−1)` 个周期，帧栅格对齐会使实际完成更晚。
- **窗口完成时刻（`window_complete`）**：第 `T6-S02` 个 `WINDOW_MATCH` 结果到达且时长条件同时满足的那一帧的显式输入时刻（B-04）。
- **动作延迟**：`latency_action = t_effective − t_trigger`，其中 `t_trigger` = 触发该动作的那条结果的显式输入时刻。受 `T6-A01` 约束（待批准）。
- **交互延迟**：`latency_interaction = t_effective − window_complete`，**不得**用 `t_capture(窗口首个 `WINDOW_MATCH` 帧)` 或 `W_min` 顶替（B-04）；其上限为 `T6-A03`（**待批准**，草案未给值，且必须先有实测 P）。
- 两者**必须分别报告**，不得互相替代；日志必须给出该次获取所用的 `P_meas` 与 `window_complete`。
- 手算示例（参数取草案值 `T6-S01=200 ms`、`T6-S02=6`）：

| FPS | `P` | `(S02−1)·P` | `W_min = max(T6-S01, (S02−1)·P)` | 支配项 | 帧栅格实际完成（示例） |
|---|---|---|---|---|---|
| 30 | 33.3 ms | 166.7 ms | 200 ms（下界） | 时长 | 第 8 帧 233.1 ms（帧栅格对齐） |
| 10 | 100 ms | 500 ms | 500 ms（下界） | 帧数 | 第 6 帧 500 ms |
| 5 | 200 ms | 1000 ms | 1000 ms（下界） | 帧数 | 第 6 帧 1000 ms |

- 因此低 FPS 下窗口由**帧数**支配；交互延迟必须以 `window_complete`（实测）+ `latency_action` 计算，`W_min` 只用于说明下界。评估时必须声明所用 `P_meas` 与 `window_complete`。上表 FPS 只是公式演示，不是阶段4 实测值。
- **回放/注入的时间缩放必须显式声明**：加速回放只能验证相应时序条件，不能冒充真实 30 分钟物理运行。

## 16. 未决项与需 Wong 决定项

| 编号 | 事项 | 现状 | 归宿 |
|---|---|---|---|
| U6-01 | `T6-01/02/03` 三项目标值与样本数 | 沿用建议，草案 | 项目总控转呈 Wong（G0 批准） |
| U6-02 | 保持期触发语义 | 本 G0 声明「一次获取只触发一次」（唯一解释） | Wong 确认；若改则属语义变更 |
| U6-03 | 全部时间参数（§14） | 草案建议值 | Wong/G0 批准 |
| U6-04 | 选择阈值与 `TARGET_CONTINUES`/`WINDOW_MATCH` 谓词阈值、抖动容忍（§14） | 草案建议值 | Wong/G0 批准 |
| U6-05 | 阶段4 结果记录接口冻结 | `DRAFT_NOT_FROZEN` | 阶段4 G0；未冻结前阶段6 集成验收 `BLOCKED` |
| U6-06 | 阶段5 显示侧新增 HUD 字段（`sm_state` 等） | 阶段6 提案，阶段5 为离线定稿未验收 | 与阶段5 协调，需 Wong/项目总控确认 |
| U6-07 | 五类动作映射与 `target_id` 命名（表 A-1） | 阶段6 提案 | G0 批准 |
| U6-08 | `T6-A03` 交互延迟上限 | 无草案值 | Wong/G0 批准 |
| U6-09 | 摄像头不可用导致真手势验收 | 延期 | 等模块到货；阶段3 验收后回归 |
| U6-10 | `T6-STALE_LIMIT` 的正式冻结 | 阶段5 已用同源 200 ms；阶段4 仍 `DRAFT_PROPOSED` | 阶段4/阶段5/G0 |
| U6-11 | 状态机实现与确定性测试矩阵（6-B/6-C） | `NOT_RUN`（G0 v1.1 复评通过前不启动） | 下一任务（S6-B），依赖本包复评 |
| U6-12 | `T6-S04`/M4 可达性：调整 `T6-S04 < T6-L02` 或删除 M4/`T6-S04` | 新登记（评审 N-02） | Wong/G0 |
| U6-13 | 阶段4 实测帧周期 `P_meas`（`T6-A03` 与交互延迟基准） | 新登记 `BLOCKED`（无实测 P，评审 N-05/B-04） | 阶段4 + 项目总控 |
| U6-14 | 五类动作反馈可见时长/过渡（逐类 UX） | 新登记（评审 N-06） | Wong/G0 |
| U6-15 | `A_DISPLAY_STATE` 是否需要（r02 已从支持类型删除） | 新登记（评审 N-01） | Wong/G0 |
| U6-16 | STABLE 是否在本次获取内锁存（进入后不因窗口中断退回 `CANDIDATE`） | 本 G0 定论为「本次获取内锁存」，见 §4 与 JSON `stable_latching` | Wong/G0 确认；若改则属语义变更 |

## 17. 覆盖矩阵与上游哈希

**操作文档 `CDX-20261022-012` §2（6-A）覆盖**：1 独占写入方与 STATE → §1 + `.codex/STATE.md`；2 上游冻结版本核对 → §1；3 五类动作/成功失败反馈/可观察状态 + 两类事件 → §7 + §5-B01/B02；4 行为表冻结（多框选择、同分、保持/重获、抖动、稳定窗口、冷却、再触发、过期、未知、无手、超时/错误）→ §5 + §8–§13；5 草案状态作起点 → §4（状态名沿用，声明不代表已实现）；6 「持续保持只触发一次」唯一 → §10；7 窗口用真实时间与有效结果数、重复帧不推进、低 FPS 延迟估算 → §9 + §13 + §15；8 阈值未冻结、不在正式集调参 → §14；9 `NO_HAND` 与未知拒绝证明 → §11 + H-5/H-6；10 异常/重复/过期不触发、单调时钟推进 → §11 + §13 + H-3。

**独立评审 S6A_20261022_r01 关闭索引（r02）**：B-01 → §18 清单与真实退出码 + `delivery_manifest.json`/`inputs_manifest.json`/`hashes_sha256.txt` + `fix_record.json`；B-02 → H-4/§9/§11.1/B17/JSON；B-03 → H-10/§10/B13/B14/M5/JSON `cooldown_policy`；B-04 → §15/§9/B27/JSON `low_fps_latency`；B-05 → §3/§8/§9/B03/B07/B09/JSON `predicates`；N-01 → M14 删除、§14 `T6-S03`、§3 `E_FRAME_CONFLICT`、`A_DISPLAY_STATE` 删除；N-02 → JSON `reachability` + §14 脚注；N-03 → §12.1；N-04 → HC-16/17/20 改为可复算 + 新增 HC-21..HC-27；N-05 → §15/U6-13/limitations；N-06 → §7 逐类 UX；N-07 → B16/B19/B23 依据；N-08 → 新 RunId 保留旧包失败输出；N-09 → §12 ±1 单位口径 + HC-27；N-10 → §5/STATE 措辞。

**独立复评 S6A_20261022_r02 关闭索引（r03）**：BLK-1 → JSON `transitions.M1/M3/M4/M5/M8/M9/M10/M15` 与 `behavior_rows.B04/B08/B10/B12/B13/B14` 的谓词绑定、`predicates.*.used_by` 补 M3/M10、§4/§5/§9/§10/§12/§13 文本同步、自检 C12 增加迁移/行为行断言；BLK-2 → `old_package_under_test.json` 改为 `git show 1fe4648:` 原始字节哈希并重跑失败证据（`selfcheck_old_package_failure.json/.txt`），旧哈希错误原因见 `fix_record.json`；BLK-3 → 入库 `selfcheck_result.json` 改用 `--manifest`+`--state`，落盘 `selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`；NBL-1 → inputs 清单 checks 两阶段实测回写；NBL-2 → 统一 `t_last_submit`；NBL-3 → 边界样例引入 `t_now` 真算；NBL-4 → §15 六列表头；NBL-5 → 修正 B-05/`transitions.M10` 描述。

**第三轮复评 S6A_r03_20261022_r01 关闭索引（r04）**：R3-B01 → §12 `T6-S02`/`T6-L02` 行改写 + §3/§12/§13 `t_last_target_continues` 定义 + 自检 C12 禁用标识符扫描；R3-B02 → `behavior_rows.B03/B17.predicates_used`、`predicates.TARGET_CONTINUES.used_by` 补 B14、`transitions.M1.predicates_used` 收敛为仅 `TARGET_CONTINUES`、`predicate_binding_policy`（M5/B13）+ 自检 C12 全量双向断言；观察项 → §4 STABLE 锁存 + JSON `stable_latching` + 自检 C17 + U6-16；N01 → §2 H-10 与 §4 统一 `t_last_submit`；N02 → HC-27 去自比较、HC-28/29 逐帧序列真推导、`revision.changes` 措辞；N03 → `verification/s6a_rerun_legacy_failures.py` 并纳入构建器；N04 → C7 样例数 29、版本号统一 v1.3/r04；N05 → 旧哈希成因措辞改为「LF→CRLF + 末尾补 CRLF」。

**第 4 轮复评 S6A_r04_20261023_r01 收尾索引（r05）**：N-r04-01 → §4 M5 行与 JSON `transitions.M5` 补窗口推进帧限定 + `stable_latching.suppressed_trigger_release` 一致 + C12 文本断言 + HC-30 角落序列；N-r04-02 → `predicate_binding_policy.statement`（M5 带标记、B13 由 H-10 承载）+ §4 + STATE 同步；N-r04-03 → C12 非空列表普适断言 + `verification/s6a_r05_probe.py` 注入证明；N-r04-04 → C7 窗口跨度口径修正（HC-29 200 ms）+ 两种口径一致性断言；N-r04-05 → `src/stage6/s6_core.py` 引用清理（WIP 不提交）。

**计划 L102–L108 覆盖**：L104 目标与八项冻结要求 → §4/§8/§9/§10/§11；L106 五个测试场景与沿用建议 → §5-B01…B28 与 §14；L108 证据与"不代替阶段7" → §0、§18。

**上游只读文件 SHA-256（本轮开工核验；阶段6 未修改任何一份）**：

| 文件 | SHA-256 |
|---|---|
| `docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md` | `7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230` |
| `docs/obsidian-project/02-方案设计/B方案实施与阶段验收计划.md`（w6 基线版本） | `82ef0796baf6a8cd04ae942019e1af226f645e27fe8309fe56bcb05a7b1a5f9a` |
| `docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md` | `df95a8438eaa2d451b54ca3f1927c454eaef022c1f8f31a18874980f69702e57` |
| `docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md` | `735cbc78882dd299a952ee1d4c2f7ef972e8cc903782be3a64f1db830f311dd7` |
| `w4/docs/stage4/s4a_stage4_g0_fields.json`（只读） | `3524d02ae410ae365a9dbfc5f04dcd9f300f8013086a076259a641f7eb8afb87` |
| `w5/docs/stage5/S5A_stage5_display_g0_spec_v2.md`（只读） | `ca5968d444db7a017a3c2e4e95d838f385c605837da92e31b4c2aa9d3cf56932` |
| `w5/docs/stage6/S6_stage6_interaction_spec_draft.md`（只读） | `d7cf98093996fffb23180b078dfa4068dcab5b5031d5bd4c62e4c51baa40a0a1` |
| `w5/docs/stage6/s6_interaction_thresholds.json`（只读） | `b87234e4f091bac94f9d7cc7c8ab16c180932f60dc8e5160e32cd3278b11ec42` |
| `w5/docs/stage6/S6D_stage6_revision_suggestions_from_stage5.md`（只读） | `809a9ccd490f91ea13a669a7437a8d6b35272b07c9935557399428d3cbdb527e` |

**阶段5 修订建议采纳情况（S6-D-01…05）**：S6-D-01（窗口基于**结果 `frame_id` 序列**、单位明确为"结果条数"）→ 已采纳，H-4 + §9。S6-D-02（窗口推进与缺失/过期处理）→ 已采纳，§9 + §13。S6-D-03（未知与零框语义区分）→ 已采纳，§11.1/§11.4 分别计数。S6-D-04（动作携带 `frame_id` 与年龄）→ 已采纳，§3 日志字段。S6-D-05（统一用 `score`，禁止 `confidence` 命名）→ 已采纳，§7/§14 全表使用 `score`。

## 18. 证据、限制与不宣称项

- 本轮（v1.4 / r05）运行证据：`report/evidence/S6-A/s6a_g0_20261022_r05/`（清单与自检：`delivery_manifest.json`、`inputs_manifest.json`、`hashes_sha256.txt`、`selfcheck_result.json`、`selfcheck_c11_stdout.txt`、`check_inputs_mode_output.txt`、`check_evidence_mode_output.txt`；旧包失败证据：`selfcheck_old_package_failure.json`/`.txt` 与 `old_package_under_test.json`、`selfcheck_r02_blk1_failure.json`/`.txt` 与 `r02_package_under_test.json`、`selfcheck_r03_failure.json`/`.txt` 与 `r03_package_under_test.json`、`selfcheck_r04_failure.json`/`.txt` 与 `r04_package_under_test.json`（r05 加固自检在 r04 提交字节上的失败输出，证明新断言能捕获其缺失项）；注入探针：`probe_summary.json` 与 `probe_baseline_no_injection_stdout.txt`、`probe_m5_window_advance_removed_stdout.txt`、`probe_empty_predicates_used_stdout.txt`、`probe_b13_predicates_used_added_stdout.txt`、`probe_undeclared_predicate_name_stdout.txt`、`probe_suppressed_release_not_window_advancing_stdout.txt`、`probe_case_timeout_frame_action_stdout.txt`、`probe_case_span_wrong_stdout.txt`；记录：`fix_record.json`/`fix_record.md`、`coverage_matrix.json`、`limitations_not_executed.json`、`hand_computed_cases.json`、`upstream_bindings.json`、`S6A_run_summary.md`）。旧包失败证据由 `verification/s6a_rerun_legacy_failures.py` 用最终脚本重跑生成（r01/r02/r03/r04，git 字节二进制提取）。r01/r02/r03/r04 证据保持原样：`report/evidence/S6-A/s6a_g0_20261022_r01/`、`..._r02/`、`..._r03/`、`..._r04/`（**不覆盖、不改写**）。缓存 `tmp/6/S6-A/s6a_g0_20261022_r05/`（不入库）。
- **本轮全部实测类项目为 `NOT_RUN`**：状态机确定性测试（6-B/6-C）、脚本注入联调（6-D 一级）、独立图片/视频序列板上联调（6-D 二级）、≥30 分钟回放稳定性、真摄像头验收与统计（6-E）均未执行；真摄像头项为 `BLOCKED`（摄像头不可用，待重新采购）。
- 限制：阶段4 结果记录与阶段5 显示契约均未冻结 → 集成验收依赖 `BLOCKED`；阶段4 文件在本轮期间被 w4 窗口并发修改（未提交），本 G0 绑定的是提交 `73c3dad` 版本（见 §1 与 `upstream_bindings.json`）；显示侧新增 HUD 字段为提案；动作映射为提案；全部阈值待批准；无硬件授权，未做任何板上验证。**阶段4 实测帧周期 `P_meas` 未取得 → `T6-A03` 与交互延迟量级 `NOT_RUN`（U6-13）**；`T6-S04`/M4 在当前草案下不可达（U6-12）；五类逐类反馈可见时长未批准（U6-14）。
- **证据修订说明**：r02 的 `old_package_under_test.json` 5 个哈希曾因提取脚本用 PowerShell 文本管道（`git show | Set-Content -Encoding utf8`）重写行尾/编码而与 `git show` 原始字节不符（复评 BLK-2）；r03 改为二进制提取并重算，失败结论（exit 1，13 项）不变但被检字节已可复核。r02 的入库 `selfcheck_result.json` 只跑了文件计数（复评 BLK-3），r03 已改为完整 C11。 **r04 修订说明**：R3-B01 修正 §12 的 `T6-S02`/`T6-L02` 行并定义 `t_last_target_continues`（原 `t_last_match`/`matched_frames`/`t_submit+` 写法已废弃）；R3-B02 修正 `predicates.used_by` 与 `predicates_used` 的双向一致；M5/B13 叙述改为「只有条件文本 + `global_cooldown_gate` 绑定、无 `predicates_used` 字段」；旧哈希成因（N05）更正为「LF→CRLF + 末尾补 CRLF」，不再声称「编码」被改写。 **r05 修订说明**：N-r04-01..05 五项均为非阻断收尾；M5 的窗口推进帧限定同时写入 JSON 与文档，并由 C12 文本断言固定；C7 的窗口跨度口径按 §9 修正，并保留宽松口径一致性断言；新增注入探针证明 C12/C7 新断言具备判别力（探针失败输出随包保留）。
- **回放/注入限定**：任何由脚本注入或回放输入得到的结论，其适用范围**仅限回放/注入输入**，不得冒充真实摄像头验收。
- 检查器 `CHECKS_OK` 仅表示清单/文件绑定检查通过，不代表接口语义正确、测试成功、独立审查通过或 G0/G4/G5。
- 独立 Reviewer：本阶段总控在本次会话中**无法创建子代理**（运行环境限制：委派深度已用尽），故本轮**未完成独立审查**；该限制已如实登记，独立审查须在后续轮次由项目总控安排。