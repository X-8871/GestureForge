# 阶段4↔阶段5 共享输入/结果契约 | `s4-shared-io/1.1.0` | `DRAFT_PENDING_REVIEW`（r02）

- 日期：2026-10-22（UTC+8）；实施方：阶段4（本树 `D:\codex-worktrees\w4`）；消费方：阶段5（**只读**消费冻结交付）。
- 机器可读：[`s4b_shared_input_result_contract.json`](s4b_shared_input_result_contract.json)。
- 修订 r02：按 rev-spec 独立审查修复 T1（权威绑定）/T2（词表对齐 S4-A）/T3（显示语义取值）/T4（HUD 映射混键），并处理 N1/N3/N4/N5/N6。
- 来源标注：`[CDX-010 §3]`=4-B 共享契约与注入要求；`[CDX-014 §4]`=阶段5 五元组；`[CDX-014 §5.4]`=HUD 13 字段；`[CDX-015 §3/§5]`=执行与判定口径；`[S4-A]`=`docs/stage4/s4a_stage4_g0_fields.json`；`[w5-G0]`=`D:\codex-worktrees\w5\docs\stage5\s5a_stage5_display_g0_fields.json`。

## 0. 权威绑定与规则（T1）

| 权威 | 路径 | SHA-256 | 状态 |
|---|---|---|---|
| S4-A G0 契约（机器权威） | `docs/stage4/s4a_stage4_g0_fields.json` | `657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5` | `G0_ROUND_FROZEN_R06`（r06） |
| S4-A 人读镜像 | `docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md` | `314335cd…4a371`（r05 内容，r06 同步由 S4-A 任务完成） | 只读引用 |
| 阶段4 地址图 | `docs/stage4/S4B_stage4_address_map.json` | `416c02419ebe93e15bed0093a5e8c3bb8bca966395aa0c0febdf63d1646db6c3` | 由 4-B 任务冻结 |
| CDX-010 阶段4 运行书 | 邮箱 `CDX-20261022-010-…md` | `4cd61ee0…1cf89` | 只读 |
| CDX-014 阶段5 运行书 r02 | 邮箱 `CDX-20261022-014-…md` | `f25e5ebb…5a141` | 只读 |
| CDX-015 执行总入口 r02 | 邮箱 `CDX-20261022-015-…md` | `a3ce50d2…170a7` | 只读 |
| 阶段5 显示 G0 字段 | `w5/docs/stage5/s5a_stage5_display_g0_fields.json` | `8eac7007…709911` | 只读引用（不写 w5） |

规则：本契约只能引用**已提交且经独立审查**的权威版本，禁止引用“最新文件”；自检**现场复算**上述 SHA，任一不符即 FAIL，必须显式更新绑定并重新审查。权威被取代时必须记录取代关系（S4-A r05 `3524d02a…8afb87` → r06 `657ea2fb…930d5`）并通知阶段5 重新绑定。冻结前全部绑定必须与磁盘一致且权威自身已冻结。

## 1. 输入帧契约 `[CDX-010 §3.1]`

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `contract_version` | string | 是 | 固定 `s4-shared-io/1.1.0`；不匹配即拒绝消费 |
| `source_kind` | enum | 是 | `file_injection` / `camera` / `synthetic`（与 C 实现/CLI 同名）；映射到 S4-A `source_kind`（`BOARD_INJECTION`↔`file_injection`、`CAMERA`↔`camera`、`OFFLINE_REGRESSION`↔`synthetic`），证据中必须可互相换算 |
| `session_id` | string | 是 | PS 会话唯一标识（建议 32 hex）；唯一映射键之一，会话内不变 |
| `frame_id` | u32 | 是 | PS 侧 +1 单调分配（沿用 S4-A `frame_id_allocation`），与送入 PL 的 `FRAME_ID` 同值 |
| `width` / `height` | u32 | 是 | 原图像素尺寸；补边逆映射唯一基准 |
| `pixel_format` | enum | 是 | `RGB888`/`RGB565`/`GRAY8`/`INT8_CHW_416`；**覆盖范围由注入点决定** |
| `byte_order` | string | 是 | 当前平台 `little` |
| `stride_bytes` | u32 | 是 | 行跨距；行尾填充未定义、不得被消费 |
| `buffer` | object | 是 | `region_name`/`base_addr`/`offset_bytes`/`length_bytes`/`alignment`；半开区间；`region_name` 必须在地址图中 |
| `frame_integrity` | object | 是 | `algorithm`(crc32_ieee/sha256)+`value`+`length_bytes`；**逐帧记录** |
| `capture_time_available` | bool | 是 | 取值域与 S4-A `measurement_scope.capture_time_available` 一致；`file_injection` 下**必须为 false** |
| `injection_start_ns` | u64 | 条件 | 仅 `file_injection`：开始把帧写入 DDR 的单调时刻。**不是采集时间** |
| `capture_time_ns` | u64 | 条件 | 仅 `camera`：第一个有效像素时刻；`file_injection` 下必须省略或标不可用（结果侧按 S4-A 用 0 哨兵 + 注解判别） |
| `timestamp_source` | object | 是 | `clock`/`freq_hz`/`wrap_handling`/`epoch_note` |
| `clock_domain` | string | 是 | 时间戳所属时钟域；`file_injection` 下必填 |
| `measurement_scope` | object | 是 | 键与取值域**与 S4-A 完全一致**（`source_kind`/`pl_timing`/`uart_transport`/`board_pl`/`capture_time_available`/`injection_start_ns`/`clock_domain`/`unavailable_fields`）；**不得自造枚举**（原稿的 `INJECTION_ONLY` 已删除）；`file_injection` 下 `unavailable_fields` 必须含 `capture_time_ns` |

**注入点覆盖范围**：`RGB888`/`RGB565` 在被验收的预处理**之前**才覆盖预处理链；`INT8_CHW_416` 只覆盖网络+后处理；直接写显示缓冲只覆盖显示。任何“全链路通过”的说法必须以其注入点覆盖为前提。

**事件顺序 `[CDX-010 §3.4]`**：`producer_write_start` → `producer_write_complete` → `cache_flush_by_producer` → `ownership_publish_to_consumer` → `consumer_start` → `consumer_done` → `consumer_invalidate` → `buffer_release_to_producer`。任一事件缺失即该帧不可消费；**不得用超时推断完成**。

**缓存与 DMA**：生产者在发布所有权前 flush（DCache 写回、64 B 外对齐）+ DSB；消费者读结果前 invalidate（64 B 外对齐）+ DSB；DMA/PL 完成事件后仍需 cache 维护才能读到数据；**不得覆盖仍被持有的帧**，多缓冲数 ≥ 在途消费者数 + 1；方向以地址图 `cache_maintenance` 为准。

**帧序列规则（N5）**：重复 `frame_id`（未声明为重放）→ 拒绝并记 FAIL，不得幂等静默接受；`frame_id` 回退 → 拒绝并记 FAIL（除显式新会话/复位）；结果乱序按 `(session_id, frame_id, result_seq)` 关联，无法唯一关联或顺序矛盾者不得用于跨阶段证据；以上拒绝必须落在 PS 侧日志与证据中（记原因，不只记计数）。

## 2. 结果契约

### 2.1 结果记录

字段与语义以 `[S4-A]` 为权威：`frame_id`、`result_seq`、`geometry`、`state`、`detection_count`、`detections`（`class_id`/`class_name`/`score`/`xyxy`/`xyxy_px`/`source_order`）、`candidate_count`、`candidate_count_pre_threshold`、`candidate_overflow`、`capture_time_ns`、`result_time_ns`、`inference_time_ns`、`end_to_end_latency_ns`、`dropped_frames`、`stale`、`error_code`。
`file_injection` 下 `capture_time_ns` 按 S4-A 约定为 **0 哨兵 + 注解判别**（不当作实测采集时间，也不得用 `injection_start_ns` 冒充），其派生的 `end_to_end_latency_ns` 不可定义。

### 2.2 显示关联五元组 `[CDX-014 §4]`

| 字段 | 语义 |
|---|---|
| `displayed_frame_id` | 该显示刷新实际展示的画面帧标识；**不得为对齐而改写为 `result_frame_id`** |
| `result_frame_id` | 叠加结果所属帧（与 `result_record.frame_id` 同值） |
| `age_result_ns` | `t_overlay_commit − t_result_publish`（与 `[w5-G0]` 一致）；无 result_time 时不可用 |
| `age_frame_ns` | `t_overlay_commit − t_capture(frame_id)`；注入下以 `injection_start_ns` 为基准必须显式声明 |
| `display_semantics` | **`B_latest_result_overlay`**（`[w5-G0]` 已决值，Wong 2026-10-21）；阶段5 G0 另登记 A/C 但未启用，本契约**不得**授权未批准语义 |

### 2.3 过期规则（N6：双基准、同一常量）

`stale_effective = stale_flag OR age_frame_ns > stale_limit_ns`

- 阶段4 侧定义（与 `[w5-G0].stale_and_age.stage4_stale_definition` 同义）：`stale=true` 当**结果年龄**（发布时刻 − `result_time_ns`）超过 `stale_limit_ns`，且仅 `state ∈ {OK, NO_HAND}`。
- 两个基准必须同时可复算：结果年龄（S4-A 的 `stale`）与 `age_frame_ns`（显示）；**共享同一数值常量，不得各造一份**。
- 唯一来源：阶段5 G0 的 `STALE_AGE_LIMIT_NS`（当前 `[w5-G0]` 记为 `G0_FIXED_OFFLINE`，值 200000000 ns）；阶段4 引用该值时必须记录来源与状态，且**阶段4 正式 G0 批准前不得作为验收门槛**（本契约 `stale_limit_status = DRAFT_PENDING_APPROVAL`，草案 200 ms）。
- 每结果只计一次 stale，原因留日志。

### 2.4 HUD 13 字段来源 `[CDX-014 §5.4]`

`capture_fps`（camera 可用；注入/合成必须标 UNAVAILABLE）、`inference_fps`、`display_fps`（阶段5 定义）、`inference_time_ns`、`age_result_ns`、`age_frame_ns`、`frame_id`（`displayed_frame_id`/`result_frame_id` 成对）、`boxes`、`stale_cleared`、`dropped_frames`、`timeouts`（不得记作零框成功）、`warmup_state`、`display_semantics`。
该映射的**键集合必须恰等于 13 字段**（说明性文字不得混入）；不可用者必须标注不可用，不得用 0 伪装实测。

### 2.5 PS 侧日志与唯一映射（UART 方案 B）`[CDX-010 §2.3]`

- 唯一映射键：`(session_id, frame_id, result_seq)`；会话内 `(session_id, frame_id)` 唯一。
- 日志必含：会话/帧/结果序号、`capture_time_ns` 或 `injection_start_ns`（按 `source_kind`）、发布/推理/结果时刻、`inference_time_ns`、age 原始时刻、丢帧/超时/队列满计数、所有权状态迁移、逐帧 `frame_integrity`、重复/乱序/拒绝原因。
- **阶段5 必须从该日志读取 UART 缺失的时间/过期/丢帧/状态量，不得声称这些量来自 UART。**
- 上游字段不足唯一关联时，阶段4 补版本化本地映射（随证据保存），**不得单方改上游协议**；冲突/缺失记 FAIL 并保留原始日志。

## 3. 三种范围的冻结口径 `[CDX-010 §2.4]`

| 范围 | 允许的结论 | 禁止的结论 |
|---|---|---|
| `offline_regression` | 冻结输入与参考的数值一致性（离散字段完全一致、score/坐标 ≤1e-6）、工具与判据有效性（含反例） | 板上行为、UART 实收、真实采集质量 |
| `board_injection` | 注入帧经真实 PL/PS 链路的整数头与后处理结果与冻结参考一致；注入子项的时间/丢帧/过期（PS 侧） | 真实摄像头采集质量/颜色；把注入时间当采集时间；完整阶段4 G5 通过 |
| `camera` | 真实采集链路（RGB565 展开/颜色/缩放/补边/量化）与独立参考一致；真实场景交互与长跑 | 摄像头未交付时以注入/合成替代；灰度诊断帧作为真彩质量或总体准确率依据 |

证据要求：离线=上游 SHA 绑定 + 逐样本/逐框差异 + 反例；板上注入=bit/XSA/ELF/输入 SHA + 注入点声明 + 每帧 CRC/长度 + heads 原始 INT8 + 逐框差异 + 错误恢复统计；摄像头=≥100 帧真实输入逐值比对 + ≥30 分钟且 ≥1000 次有效推理 + 每类 ≥10 次交互观察（阶段3 交付后方可执行）。

## 4. 消费边界与版本化 `[CDX-015 §3/§5]`

- 阶段5 只读；任何字段增删/语义变化必须**新版本号** + 阶段4 所有者批准 + 适用回归；阶段5 只能消费已冻结版本。
- 本契约 `DRAFT_PENDING_REVIEW`：经独立审查与 Lead 提交后冻结；冻结前不得作为验收依据。

## 5. 限制

- 不含真实板测结果；本轮无任何硬件执行。
- 不定义阶段5 布局/像素门槛/显示 FPS 语义（属阶段5 G0）。
- 候选上限、时间口径与异常行为取值以 S4-A 阶段4 G0 契约为准。
- 绑定 SHA 为本次修订时点实际值；权威变更时必须显式更新绑定（自检会 FAIL 直到更新）。