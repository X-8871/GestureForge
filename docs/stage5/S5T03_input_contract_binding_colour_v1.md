# S5-T03 输入契约改绑：真实彩色（v2，2026-10-24）

> 状态：`BINDING_ALIGNED_WITH_STAGE4_R04_NOT_FROZEN`。本文是**外围绑定与范围标签**，**不改** `S5A-G0-v2` 的任何阈值/几何/语义（本轮仅按 N-1 修一处措辞，见 §9），也不把既有合成源结论升级为真实集成结论。
> 机器可读权威：`docs/stage5/s5t03_input_contract_binding_v1.json`（内容已升为 v2）；冻结参数：`docs/stage5/s5t03_offline_skeleton_params_v1.json`。
> 依据：`CDX-20261022-015`（r03）§2.2、`CDX-20261022-014`（r02）§4/§5、`decisions/stage_3_4_direction_20261024_r01.md`、**阶段4 r04 共享契约（commit `7a9507ab4a2067d493b4d9ff47b331c747f33796`，2026-10-24T00:52:29+08:00；JSON blob `611e6c7c…`、MD blob `23c8b4d2…`）**。

## 0. 取代关系（B-1 更正）

- 本文件上一版（v1，内容提交 `ba31126`）绑定的是阶段4 **已被取代**的 `f6fa9f0` 快照，并据此把 `camera_capture_replay_colour` 归入 `file_injection|synthetic` + `capture_time_ns=0` 哨兵；**该结论与 r04 相反且已作废**。
- 时间线：r04 提交于 **2026-10-24T00:52:29+08:00**，本文件 v1 定稿于 00:44–00:55、提交于 01:04 ⇒ v1 定稿时上游已是 r04（引用过期快照，属实质错误）。
- 现按 r04 重绑：**两个彩色标签都映射 `source_kind=camera`、`capture_time_available=true`**，回放仅以 **`timing_claim_scope=replay_only`** 区分；`capture_time_ns` 一律取**真实抓取时刻**（非零、不得标 unavailable）。
- **复审后修（NB 轮）**：等价 `frame_id` 判据改 fail-closed（§6）、漂移登记补全为**扫描判据**（§9 NB-2）、计数单位改为 JSON↔流水线**逐字相等**（§10 NB-3）、时间戳按实测（NB-4）、T01 补绑定断言并登记**实现状态**（§11 NB-5）。本轮仍只交付**合成流离线骨架**，回放/彩色**实现**未做。

## 1. 要解决的问题

015 r03 §2.2 要求各阶段单一写入方把自己的输入/结果契约显式标 `camera_live_colour` 或 `camera_capture_replay_colour`，并分别绑定：阶段3 部署（bit/XSA/ELF）、实际格式/字节序、宽高/stride、原图坐标口径、采集时钟与源帧哈希；同时明确「回放结论必须标回放」。原 `S5A-G0-v2`（2026-10-21）写的是「阶段3 颜色受阻 ⇒ 真实采集路径不可用」，该前提已由阶段3 新模块实测撤销，故必须补一份绑定把标签与上游身份写清，但**不得顺手改显示契约的指标**。

## 2. 输入范围标签（互斥，三选一）

| 标签 | 含义 | 阶段4 `source_kind` | `capture_time_ns` | `timing_claim_scope` | 状态 |
|---|---|---|---|---|---|
| `camera_live_colour` | 实时真实彩色采集（新模块 + 无补偿基线） | **`camera`** | 非零真值，不得标 unavailable | `real_live` | `ALIGNED_WITH_STAGE4_R04` |
| `camera_capture_replay_colour` | 抓取到的**真实彩色帧**在回放/注入路径重放 | **`camera`**（r04：两个彩色标签都映射 camera） | **真实抓取时刻（非零）**；不得填 0 哨兵、不得标 unavailable | **`replay_only`** | `ALIGNED_WITH_STAGE4_R04` |
| `synthetic_dynamic_reference` | 与阶段4 同 schema 的合成动态流（既有 120 帧/31.06 min 均属此列） | `synthetic` | `0` 哨兵 + `unavailable_fields` | —（非 015 的两个彩色标签） | `ALIGNED_WITH_STAGE4_R04` |

- **标签是描述性范围标签，不是新枚举**：对齐 r04 `label_rule`——实际枚举值必须遵循该接口 G0，两个彩色标签都映射 `source_kind=camera`（→ S4-A `CAMERA`），不得新增 S4-A 未定义的取值。
- **回放必须逐帧携带**：`frame_integrity`（algorithm+value+实际 length_bytes）、`replay_source_path`、`replay_source_file_sha256`、`replay_source_width/height/stride_bytes/byte_order`、`stage3_capture_evidence_entry`、`source_frame_id`、`source_capture_time_ns`（对齐 r04 `source_frame_hash_rule.replay_binding`；`source_*` 为显示侧扩展命名，纳入契约与否见 `UR-1`）。
- **回放禁止结论**：计时字段只能用于回放内部一致性，**不得写为端到端延迟**、不得与实时采集的 FPS/延迟混表、不得升级为实物集成结论。
- **互斥**：一个证据包只能属于一种标签；五元组与产物清单必须携带该标签，并与阶段4 `source_kind` 一一对应（两个彩色标签均对应 `camera`）。

## 3. 阶段3 部署身份（本轮独立只读重算，实际核对时刻 2026-10-24 01:07:50）

| 产物 | 路径（dbdf，只读） | SHA-256（本树重算） | 与 015 r03 |
|---|---|---|---|
| 无补偿 SOF/bit | `dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\project\ov5640_single.runs\impl_1\design_1_wrapper.bit` | `7cb330685260ced38636d3e90a92160979b0f88770d380269e9864722ce48710` | **全哈希逐字符一致** |
| XSA | `dbdf\tmp\s3r06\t04_sof_fix_20261020_r01\design_1_wrapper.xsa` | `1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3` | 015 r03 只给**前缀** `1f5b138e…`，一致；全哈希与 dbdf 原部署清单一致 |
| 实时彩色应用 ELF | `dbdf\tmp\s3r06\t04_j11cmos2_elf_v10\elf_build\app\an5642_j11cmos2_v10_read.elf` | `1457cda4867649dce8b54b2ebe9c7bafc0a2a1d4d1deba112adc6f6492306073` | **全哈希逐字符一致** |

> 口径更正（N-5 附带）：原文「3/3 逐字符一致」不准确——015 r03 对 XSA 只给前缀；只有 bit/ELF 是全哈希比对。交叉核对：阶段4 r04 `stage3_deployment_bindings` 绑定的 bit/ELF 全哈希与本树重算相同（独立第二来源）。

- 次要（只读登记、本轮不部署）：`v11_freeze` ELF `c01133b1bb0204f07a5be215dbeb58ca0dcc627115cd3a06f1c56f9b21ca26c4`。
- 历史回退专用（**不得**当当前部署身份）：灰度 `44e609cc…`、纯绿 `2f72aaa4…`、补偿彩色 `30db09ba…`。
- **`UR-2` 已 RESOLVED**：dbdf `S3-T05/t05_new_module_reverify_20261023_r01/README.md` 已于 **2026-10-24T01:14:18+08:00** 更正为 `v10_read` 并附 UR-2 更正登记；更正后 sha256 `e60bab012ee87f92fe8ac0239863985e1b4dcd58b92c0bf248f9cfac6f23e54d`（本树 01:31 只读复核），与本树独立重算口径一致。
- **范围外**：J10 半屏黑（Wong 2026-10-24 移出范围，当前 J11/CMOS2；不得写成已修复）；`v12`/`0x503D` 仅既定彩条用例，本轮不动硬件。
- 命令与真实退出码：`report/evidence/S5-T03/s5t03_takeover_20261024_r01/console/deploy_hash_verify.txt`（r01 包；r02 包同命令重跑，见 r02 证据）。

## 4. 采集几何与字节序

| 项 | 值 | 依据 |
|---|---|---|
| 源分辨率 | 1280×720 | 阶段3 部署 |
| 每像素字节 | 3 | 行文件 3840 B / 1280 px |
| `row_stride_bytes` | 3840 | `row_y100/400/600.bin` 各 3840 B |
| 帧字节 | 2764800 | `bars_frame_full.bin` 实测大小 |
| DDR 转储通道序 | `B,G,R` | 015 §2.1/§2.2（本树未独立改判，仅登记） |
| 传感器格式 | RGB565 | 同上 |

**不得混同**：传感器 RGB565 展开、DDR 转储 B/G/R 三字节序、模型 RGB888 语义是三种东西；转换/量化/补边必须与冻结 D2 对齐；`stride` 之外的行尾填充未定义、不得被消费。

- **采集时钟**：`PENDING_MEASUREMENT`（对齐 r04 `capture_clock`）——采集时钟域与频率须在真实彩色回归时用 PS 单调计时器实测并逐帧记录；在此之前不得填造频率，也不得把回放计时当采集时钟。
- **源帧哈希**：每一帧逐帧记录 `frame_integrity`（algorithm ∈ {crc32_ieee, sha256} + value + 实际 `length_bytes`），与采集/回放时刻及 `session_id`/`frame_id` 绑定；禁止只记一次或只记总量（对齐 r04 `source_frame_hash_rule`）。

## 5. 原图坐标口径（沿用，未改）

- `detections[].xyxy` = **归一化原图坐标**（含补边逆映射、裁剪到 [0,1]、正面积），原图 = 1280×720 采集帧。
- 显示层**只允许**使用该字段，不得自行反算第二份坐标；缺失时才启用冻结逆式（启用待阶段4 G0）。
- 映射链（全部来自冻结参考实现 `verification/s5_display_geometry_reference.py`，哈希 `4d9fe369…` 与 S5-A 清单一致）：
  `clip_unit_box` → `original_norm_to_display_px`（`round_half_up(v*(span-1))`，只在最后取整一次）→ `border_pixel_sets`（2 px 偶数线宽居中、逐边钳到画布内）→ 标签锚点（框外左上→框内左上→安全区）、分数文本 ≤1e-3。
- 门槛全部沿用：逆映射 ≤1.0 px、绘制保真 ≤1 px、线宽 ±0.5 px、离散字段完全一致。

## 6. 帧关联键（对齐阶段4 草案，不自造）

| 键 | 字段 | 用途 |
|---|---|---|
| 共享契约结果键 | `(session_id, frame_id, result_seq)` | 唯一标识一条结果 |
| S4-A join key | `(session_id, frame_id, repeat_index)` | 结果与同一请求重复项连接 |
| PS 日志主键 | `(session_id, result_seq)` | 旁路结果日志 |
| UART 可观测键 | `(frame_id, repeat_index, sequence)` | 请求/响应配对（`sequence` 非唯一键） |
| **显示侧成对** | `displayed_frame_id` / `result_frame_id` | 语义 B 下不要求相等，禁止改写 `frame_id` 掩盖错配 |

- 五元组：`(displayed_frame_id, result_frame_id, age_result_ns, age_frame_ns, display_semantics)`。
- 时间：同一 PS 单调时钟；`capture_time_ns` 在 `camera` 下必须非零且不得标 unavailable，在 `file_injection`/`synthetic` 下为 `0` 哨兵 + `unavailable_fields`。
- **拒绝规则（B-2 + NB-1，采用阶段4 r04 `frame_sequence_rules` 强制行为）**：
  - 重复结果键 `(session_id, frame_id, result_seq)` ⇒ **拒绝并记 FAIL**（`duplicate_results`）；
  - `frame_id`/`result_seq` **回退**（小于上一已接受值，除显式新会话/复位）⇒ **拒绝并记 FAIL**（`out_of_order_results`）；
  - **等价 `frame_id`（NB-1，fail-closed）**：同 session 的 `frame_id` 已被接受、且该记录**未显式声明**为重复/重放 ⇒
    **拒绝并记 FAIL**（`duplicate_frame_id_results`）；唯一放行依据＝`repeat_declared=true` 或 `repeat_index` 严格大于
    该 `(session_id, frame_id)` 已接受的最大值（对齐 r04 `stage4a_join_key=(session_id, frame_id, repeat_index)`）；
  - **分类优先级**：invalid（schema）→ duplicate（同结果键）→ out_of_order（回退）→ duplicate_frame_id（等价未声明）→ accepted；
  - 乱序接纳/回绕 ⇒ 拒绝；无法唯一关联或顺序矛盾的结果不得用于跨阶段证据；
  - 键字段必须先校验再查键：`session_id` 为本绑定的 uint32（0..4294967295），`frame_id` 为阶段4 声明的 uint32（0..4294967295），`result_seq` 为阶段4 声明的 uint32 且从 1 起（1..4294967295）；三者均拒绝布尔值、浮点数、字符串与越界值；
  - `repeat_index` 对应阶段4 `<Q8I>` 元数据中的 uint32，显示骨架按正整数编号（1..4294967295）；`repeat_declared` 若存在必须是布尔值。无效值按 schema 违规拒绝，不能改变已接受状态；
  - 拒绝必须**落在日志与证据中并记原因**，不得只记计数。紧凑 JSONL 每条提交都保存原始关联键、`reject_reason`、输入 `repeat_index`/`repeat_declared`、声明依据和前序最大 `repeat_index`（无值显式为 `null`），便于审计拒绝与放行；
  - 三类拒绝（duplicate / out_of_order / duplicate_frame_id）**同构**：不写已接受集合、不更新 latest、不绘制；
    并断言被拒帧的框与前一帧逐值相同。**NB-1 不得削弱 B-2**（回退仍在更早分支判 out_of_order）。

## 7. 既有合成源结论的处置（**不重做、不升级**）

| 既有结论 | 证据 | 范围标签 |
|---|---|---|
| 四 FPS（display 59.206 / video_refresh 59.175；`inference_fps=NA`） | `report/evidence/S5-T01/s5t01_board_fps4_20261022_r02/` | `synthetic_dynamic_reference`（显示侧） |
| 120 帧五元组 + 故障计数 + HUD 13 字段 | `report/evidence/S5-T01/s5t01_board_5t_20261022_r02/` | 同上 |
| 30 分钟长跑（r03：31.06 min、124 完整轮） | `report/evidence/S5-T01/s5t01_board_soak_20261022_r03/` | 同上（**仅显示/叠加路径**） |

- 这些 RunId 与产物**本轮不重跑、不改写**；已用 `git diff --name-only 654c72e -- report/evidence/S5-A|S5-B|S5-C|S5-T01`（空）核验，真实退出码在骨架证据包。
- 它们**不是**真实采集/真实推理集成结论；本轮离线骨架 PASS 同样只是骨架结论。

## 8. 未决与请求

| 编号 | 对象 | 状态 | 请求 | 影响 |
|---|---|---|---|---|
| `UR-1` | 阶段4 写入方（DSH/w4） | **对 r04 重发**（2026-10-24 01:35） | 确认显示侧回放扩展字段命名（`replay_source_*`/`stage3_capture_evidence_entry`/`source_frame_id`/`source_capture_time_ns`）是否纳入共享契约，并确认回放标注与 `timing_claim_scope=replay_only` 一致。原 v1 的「确认 source_kind 取值」已由 r04 自身回答，作废。 | 显示侧回放字段与阶段4 契约字段名最终对齐（不影响本轮骨架语义） |
| `UR-2` | 阶段3 写入方（DSH/dbdf） | **RESOLVED**（2026-10-24 01:14:18） | README 已更正为 `v10_read` 并附更正登记（sha256 `e60bab01…`），无剩余动作 | — |
| `UR-3` | Wong / 阶段5 正式 G0 | OPEN | 成品延迟上限、颜色表与字号、阶段4 `stale_age_limit` 正式冻结；并请一并裁定 N-1 登记的 stale 判定域口径 | 阶段5 正式验收（不影响本轮骨架） |
| `UR-4` | DSH 项目总控 | OPEN | 阶段5 板级窗口申请（阶段4 结果冻结后） | 见 `S5T03_board_verification_pending_v1.md` |

## 9. 本轮修订登记（v1→v2）

| 编号 | 处置 |
|---|---|
| **B-1** | 重绑到阶段4 **r04**（commit `7a9507a`，JSON blob `611e6c7c…`/MD blob `23c8b4d2…`）：两个彩色标签都映射 `source_kind=camera`、`capture_time_available=true`、`capture_time_ns` 取真实抓取时刻；回放以 `timing_claim_scope=replay_only` 区分；登记取代关系与 r01 证据影响（见 §0 与 JSON `supersedes`）。 |
| **B-2** | 采用上游强制行为：乱序与重复**同构拒绝**（只计数、记 FAIL/原因、不写已接受集合、不更新 latest、不绘制），并补「`frame_id` 回退必须拒绝并记 FAIL」用例与「乱序帧框与前一帧逐值相同」断言（见 §6 与骨架 T03）。 |
| **N-1** | stale 判定域：**不改冻结语义/行为**，只把 `S5A-G0-v2` JSON 的一处措辞改为与冻结参考实现一致（新增 `stale_domain_note`），并在 STATE/缺口登记差异、提请正式 G0 裁定；该 JSON 哈希轨迹 `8eac7007…` → `10d24a39…`（N-1）→ `e3347c4e…` → `af51a4bf…`（NB-4 补来源说明并把 `revised_utc8` 改为实测分钟值），**阈值/几何/语义自 N-1 后未再变**；旧包绑定的仍是 `8eac7007…`，已按扫描判据登记（不删除其证据）。 |
| **N-2** | 长跑口径改正：判据用**区间数** 106572（= 帧数 106573 − 1），106572 × 16.89 ms = 1 800 001 080 000 ns，余量 **+1.08 ms**；原文把帧数当区间数并算错乘积，已改（见参数 JSON `long_run_min_frames_derivation`）。 |
| **N-3** | 计数单位与时机已声明（参数 JSON `counter_units`，并在 §10 与清单 checks/limitations 引用）：如 `timeouts` 计**提交帧**（240 帧 mixed 为 14，注入 TIMEOUT 结果数为 7）、`stale_cleared` 按**结果键**去重。 |
| **N-4** | 帧级事件日志随证据落盘（`logs/events_mixed_240.jsonl`、`logs/events_long_run.jsonl.gz`），并提供独立复算器 `scripts/stage5_t03/recompute_from_log.py`（不导入流水线内存计数）。 |
| **N-5** | 时间戳按实际值改正：部署核对 `verified_at_utc8=2026-10-24T01:07:50`（命令输出 mtime）；参数首次冻结 `frozen_utc8=00:43:33`（文件 mtime）、本轮 `revised_utc8=01:37`；绑定 `generated_utc8` 同改，并补 `*_note` 说明取值来源。 |
| **N-6** | `UR-2` 标 **RESOLVED**（dbdf 已于 01:14 更正，见 §3）。 |
| **N-7** | 清单改为 `interfaces=[]` + `interfaces_not_applicable_reason`，**首要理由＝无 `role=input` 文件**（本任务无本地输入文件），次因＝上游接口均未冻结（按 `report/README.md` 规定不伪造冻结字段）。 |
| 附 | 「3/3 逐字符一致」改述为 bit/ELF 全哈希一致 + XSA 前缀一致（全哈希与 dbdf 原部署清单一致），见 §3。

## 9b. 复审（r02）后修：NB-1..NB-5（本轮）

| 编号 | 处置 |
|---|---|
| **NB-1** | `submit_result` 对**同 session 等价 `frame_id` + 新 `result_seq`** 原判 `accepted`（会更新 latest、改变绘制）⇒ 与 r04 `duplicate_frame_id` 不符。按裁决 **(a) fail-closed** 修：未显式声明即拒绝并记 FAIL（新增计数 `duplicate_frame_id_results`，与 `duplicate_results` 分列）；放行只看 `repeat_declared=true` / `repeat_index` 递增；补 3 条用例（未声明必拒、声明放行、**判别力对照**：复刻 r02 语义时该断言变红）+ `equiv` 流 40 帧覆盖；**未削弱 B-2**（回退仍先判 out_of_order）。 |
| **NB-2** | `impacted_by_this_revision` 由「只登记 S5-A r03」改为**扫描判据**：登记规则 + 旧/新哈希 + **19 个清单文件**（10 个包目录）逐条列出；新增 `scripts/stage5_t03/scan_hash_drift.py`（扫描 `report/evidence/**/*manifest*.json`，命中集合必须等于登记集合，exit 0/1）+ 测试 `test_drift_registration_covers_old_hash_bindings`（双向相等：不漏登记、不过时登记）。**未改写任何旧包**。 |
| **NB-3** | 「四处一致」改为精确表述：JSON **15 键 = 14 计数 + `definition`**、流水线 **14 键**、**逐字相等**（测试断言）、清单由 JSON **生成完整 14 条**；此前不符的文本（含 `**加粗**`、`timeouts` 特例句）已统一为同一文本。 |
| **NB-4** | 三处 `revised/generated_utc8` 改为**实测取值**并写明来源（`console/file_mtimes.txt` 记录冻结时实测 mtime；注明重新 checkout 后 mtime 会变、字节权威为 Git blob）。 |
| **NB-5** | T01 补断言：回放 `capture_time_ns` **非零要求**措辞、`carry_fields` 的 10 个必需字段、`implementation_status`（"尚未实现"）与 NB-1 规则登记；文档/STATE 明写**实现层 camera/回放路径未实现**（见 §11）。实现层运行时用例待回放路径实现时补（届时固定新基线重审）。 |

## 10. 计数单位与时机（N-3 摘要）

| 计数器 | 单位与时机 | 备注 |
|---|---|---|
| `frames_committed` / `overlay_drawn_frames` / `warmup_frames` | 每**显示帧** 1 | 绘制帧仅当真的画了边框 |
| `boxes_drawn` / `zero_area_dropped` | 每**框** 1（逐帧累加） | 被丢弃的零面积框逐帧计数 |
| `dropped_frames` / `timeouts` / `error_results` | 每**提交帧** 1 | TIMEOUT/ERROR/DROPPED 结果会被后续无新结果的帧继续复用 ⇒ 计数 ≥ 注入结果数 |
| `stale_cleared` | 每**结果键** 1（去重） | `(session_id, frame_id, result_seq)` |
| `duplicate_results` / `out_of_order_results` / `invalid_records` | 每次**提交** 1 | 均拒绝、不绘制、不更新 latest；乱序/回退记 FAIL |
| `duplicate_frame_id_results`（NB-1 新增） | 每次**提交** 1 | 同 session 等价 frame_id 且未显式声明重复/重放 ⇒ 拒绝并记 FAIL |

> **NB-3 精确表述**：参数 JSON 的 `counter_units` 共 **15 键 = 14 个计数器条目 + `definition` 说明键**；
> 流水线 `COUNTER_UNITS` 为 **14 键**；两者 14 条文本**逐字相等**（由测试 `test_counter_units_declared` 断言）；
> 清单 limitations 由参数 JSON **生成完整 14 条**（不再是概述）。此前"四处一致"的说法不准确，已更正。

## 11. 实现状态（NB-5：绑定层关闭 ≠ 实现完成）

| 项 | 状态 |
|---|---|
| 绑定/契约层（标签映射、部署身份、坐标/关联键、回放标注规则） | **已关闭**（本文件与 JSON，r04 对齐） |
| `camera_live_colour` 采集路径实现 | **NOT_RUN / 未实现** |
| `camera_capture_replay_colour` 回放路径实现（逐帧 `frame_integrity` 校验、`replay_source_*` 绑定、**非零** `capture_time_ns` 传递、`replay_not_live` 标记） | **NOT_RUN / 未实现**（`replay_source`/`frame_integrity` 未接线；合成流仍硬编码 `source_kind=synthetic`、`capture_time_available=false`） |
| 当前可用基线 | 仅**合成流离线骨架**（`synthetic_dynamic_reference`） |
| 下一轮 | 按"无板卡工作流"用阶段4 回放结果包实现回放路径并做离线动态显示回归（仍标"回放/离线"） |

- 该状态同时写入绑定 JSON `implementation_status`、`STATE`、本文件 §11 与骨架文档，避免把绑定层关闭读成实现已完成。
| `zero_hand_frames` | 每个 NO_HAND 且非过期的**提交帧** 1 | 合法零框，不算过期 |
