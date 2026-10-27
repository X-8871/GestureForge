# 阶段4↔阶段5 共享输入/结果契约 | `s4-shared-io/1.3.0` | `FROZEN_OFFLINE_ONLY`（r07，仅离线范围，2026-10-27 冻结）

- 日期：2026-10-25（UTC+8）；实施方：阶段4（本树 `D:\codex-worktrees\w4`，DSH 阶段4 总控）；消费方：阶段5（**只读**消费冻结交付）。
- 机器可读：[`s4b_shared_input_result_contract.json`](s4b_shared_input_result_contract.json)。
- 修订 r03：仅修正未冻结草案与 S4-A r06 权威的冲突；保留 r02 及其证据。session_id 统一为 u32，补充键角色、source_kind 一一映射和完整采集时间真值表，并纠正读前 invalidate 顺序；阶段5显示/HUD语义及 s2bu/1.1 不变。
- 修订 r04（本树）：
  1. 新增 `input_source_profiles`：按 `[CDX-015 §2.2]` 把输入契约改绑到阶段3 的**无补偿实时彩色**部署（bit/XSA/ELF、RGB565 传感器、DDR 转储 B/G/R、1280×720/stride 3840、原图坐标口径、采集时钟、逐帧源帧哈希），并定义 `camera_live_colour` / `camera_capture_replay_colour` **描述性范围标签**（回放必须标回放）。
  2. 显式更新已漂移的 `cdx_015` 绑定（r02 `a3ce50d2…` → r03 `be7b6520…`）并登记取代关系；新增 CDX-018/019、阶段6 批准记录、阶段3/4 方向决定、阶段3 彩色复测证据绑定。
  3. 应用已批准项：`stale_limit_ns` 由草案 `null` 变为 **200000000 ns**（`stale_limit_status = APPROVED_BY_WONG` + `approval_reference`），与 `[w5-G0]` 的 `STALE_AGE_LIMIT_NS` 同源同值。
  4. r04 已经独立复审 **`PASS`**（被审提交 `7a9507a`，阻断 0／非阻断 4）；本轮无任何硬件执行。
- 修订 r05（本树，2026-10-24）：
  1. 地址图重绑到 **r03**：新增 `raw_frame`/`raw_meta`、把**本阶段自设**禁区条目精确缩减至 `[0x12C08000,0x20000000)`（其余禁区不动）；`status` 仍 `DRAFT_PENDING_REVIEW`、两个新 region 为 `PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`（**非 FROZEN**、`enable_required=true`）。
  2. 新增顶层 `binding_byte_basis` **绑定字节口径声明**：默认**工作树磁盘字节**；跨换行环境复算须 `-c core.autocrlf=false` 或用 blob 口径；dbdf 两项彩色证据**改绑为 `git_blob_content`**，磁盘 SHA 降为注记（**dbdf 确有 `report/evidence/S3-T05/** -text` 覆盖，规则由 `4aada6d`（2026-10-24 01:59 +0800）加入**；详见 §0.2 的事实与成因）。
  3. 新增条件①事实绑定：阶段3 部署地址事实（采集=显示 `0x00110C00`、单缓冲、**运行期分配无静态保证**）与两份 Wong/DSH 决定记录。
  4. **r05 尚未复审**；冻结前必须另行独立复审并引用**固定提交 + 被审 SHA**。
- 修订 r06（本树，2026-10-25）：
  1. `raw_frame` 明确采用 `pixel_format=BGR888`、`channel_order=B/G/R`；平台 `byte_order=little` 仅表示多字节标量端序，与通道排列分离。
  2. 冻结 D2 要求在 resize、归一化与量化之前逐像素执行 B/G/R→R/G/B。例：`[0x11,0x22,0x33]` → `[0x33,0x22,0x11]`。
  3. 当前转换只在离线 Python D2 图像参考路径可见；C 注入描述符无 BGR888 枚举，PL RAW 读取无通道重排且未接 RTL 顶层；`runtime_support_status=NOT_IMPLEMENTED`，不得外推为真实链路支持。
  4. G0 readiness 的 `mailbox_pixel_format_code=1` 是独立、未实现的候选 wire 编码；共享契约仍用字符串 `pixel_format=BGR888`。现有 C enum 值 `1` 是 `RGB565`；没有 mailbox PS driver 或显式映射，禁止将候选值直接 cast 为 C enum，G0/G1 继续保持未通过。
  5. 明确 Stage5 UR-1 的回放证据侧元数据字段，不新增运行时帧字段；地址图改至 r04，地址与状态保持未冻结。
  6. **r06 尚未复审**；冻结前必须另行独立复审并引用**固定提交 + 被审 SHA**。
- 来源标注：`[CDX-010 §3]`=4-B 共享契约与注入要求；`[CDX-014 §4]`=阶段5 五元组；`[CDX-014 §5.4]`=HUD 13 字段；`[CDX-015 §3/§5]`=执行与判定口径；`[S4-A]`=`docs/stage4/s4a_stage4_g0_fields.json`；`[w5-G0]`=`D:\codex-worktrees\w5\docs\stage5\s5a_stage5_display_g0_fields.json`。

## 0. 权威绑定与规则（T1）

| 权威 | 路径 | SHA-256 | 状态 |
|---|---|---|---|
| S4-A G0 契约（机器权威） | `docs/stage4/s4a_stage4_g0_fields.json` | `657ea2fbd2587873c4b8161e50390bc4139d373b4496dbfe6d8611081d6930d5` | `G0_ROUND_FROZEN_R06`（r07） |
| S4-A 人读镜像 | `docs/stage4/S4A_stage4_g0_tracking_and_timing_draft.md` | `75278f8dcad0fdacbec9946f59e1841061698c0237a090b1410b293be0460f84`（当前 r06 镜像） | 只读引用 |
| 阶段4 地址图 | `docs/stage4/S4B_stage4_address_map.json` | 见 JSON `upstream_bindings.stage4_address_map` 当前绑定（**r04**，BGR888 RAW 字节语义） | `DRAFT_PENDING_REVIEW`，未冻结 |
| 冻结 D2 离线图像参考 | `verification/s1_t02_d2_int8_forward.py` | `0b90ef46b923b046cfcabb0b8ff8aaff4f6b927b9b8ee9eaa10335362c6c922a` | 仅离线参考；不证明 C/PL 运行期支持 |
| RAW 回放适配器 | `scripts/stage4_s4ctrl/replay_forward_bridge.py` | `c6117bb4725974bf61033207cb11e6990b22a9adc988718cc96f4aa50d8fb229`（r12 现行字节；原 `ad71cae0…` 经 `replaces` 记于契约 JSON） | `frame_full.bin` BGR 字节离线适配；只调用 Python D2，不证明 C/PL 支持 |
| 阶段3 部署地址事实（条件①） | `dbdf/report/evidence/S3-T05/t05_stage3_window_20261024_r01/address_facts.md` | **blob 口径** `d5ba4b6b…9de4f7a`（dbdf 新 HEAD `6fa77a64`；原磁盘值 `19f754d8…` 已失效） | 只读（不写 dbdf） |
| Wong D1=A 批准记录 | `decisions/stage4_raw_address_optionA_20261024_r01.md` | `d18359aa…854f8` | 只读 |
| DSH D1–D4 初裁记录 | `decisions/stage4_raw_address_d1_d4_20261024_r01.md` | `3d5b2abd…e2bf34` | 只读 |
| CDX-010 阶段4 运行书 | 邮箱 `CDX-20261022-010-…md` | `4cd61ee0…1cf89` | 只读 |
| CDX-014 阶段5 运行书 r02 | 邮箱 `CDX-20261022-014-…md` | `f25e5ebb…5a141` | 只读 |
| CDX-015 执行总入口（内容 r03） | 邮箱 `CDX-20261022-015-…md` | `be7b6520…9508cde`（取代 r02 `a3ce50d2…170a7`） | 只读 |
| 阶段5 显示 G0 字段 | `w5/docs/stage5/s5a_stage5_display_g0_fields.json` | **blob 口径** `af51a4bf47e72df6b0ffef9d39536782a5ee31ca6c6314d2d4838d0ca21aaa7b`，**固定修订 `a54f09f`**（消费固定修订；`b6d11d4/10d24a39…` 与 `8eac7007…` 经 `replaces` 记录）| 只读引用（不写 w5）；阶段5 **r02 复审已 PASS**、`task-24` 在办，**未冻结** |
| CDX-018 硬件协调 | 邮箱 `CDX-20261023-018-…md` | `9360ae1b…e6f6bd6` | 只读 |
| CDX-019 阶段4 硬件暂缓 | 邮箱 `CDX-20261023-019-…md` | `57e14a15…cb970f` | 只读 |
| 阶段6 批准记录（Wong 2026-10-23） | `decisions/stage6_approval_receipt_20261023_r01.md` | `d8edb848…e874fb` | 只读 |
| 阶段3/4 方向决定（Wong 2026-10-24） | `decisions/stage_3_4_direction_20261024_r01.md` | `907084cd…e392a` | 只读 |
| 阶段3 彩色复测哈希清单 | `dbdf/report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/hashes.txt` | **blob 口径** `e29830c8…752f56d`（阶段3 新 HEAD 已归一化，disk==blob；旧值 `40ef1fda…`/`70cdd014…` 作废） | 只读（不写 dbdf） |
| 阶段3 彩色复测现场记录 | `dbdf/report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/README.md` | **blob 口径** `e60bab01…f23e54d`（dbdf 新 HEAD `6fa77a64`，disk==blob；旧值 `d8029c39…`/`aca598c7…` 作废） | 只读（不写 dbdf） |

规则：本契约只能引用**已提交且经独立审查**的权威版本，禁止引用“最新文件”；自检**现场复算**上述 SHA，任一不符即 FAIL，必须显式更新绑定并重新审查。权威被取代时必须记录取代关系（S4-A r05 `3524d02a…8afb87` → r06 `657ea2fb…930d5`）并通知阶段5 重新绑定。冻结前全部绑定必须与磁盘一致且权威自身已冻结。

## 0.1 真实彩色输入改绑 `[CDX-015 §2.2]`（r04 新增）

阶段3 当前部署为**无补偿实时彩色**（`[S3-T05]` = `dbdf/report/evidence/S3-T05/t05_new_module_reverify_20261023_r01/`；本轮只读复算 6/6 哈希一致）：

| 绑定项 | 值 | 来源 |
|---|---|---|
| 无补偿 SOF 位流 | SHA-256 `7cb33068…ce48710` | `[CDX-015 §2.2]` |
| 配套 XSA | 以原部署清单 `1f5b138e…` 的完整哈希核对（本契约不复制其完整哈希，避免与阶段3 权威漂移） | `[CDX-015 §2.2]` |
| 运行应用 | `an5642_j11cmos2_v10_read.elf`，SHA-256 `1457cda4…2306073` | `[CDX-015 §2.2]` |
| 采集几何 | 1280×720，stride 3840 B/行，整帧 2,764,800 B | `[S3-T05]` 整帧与行样本 |
| 传感器格式 | RGB565 | `[CDX-015 §2.2]` |
| RAW 像素格式 | `BGR888`；每像素字节顺序 B/G/R | `[S3-T05]` 只读复算顺序；阶段4 契约语义 |
| 平台 `byte_order` | `little`，只描述多字节标量端序 | 平台字段约定；与像素通道排列独立 |
| 阶段3 旧字段映射 | 旧证据中的 `source_byte_order=BGR` 表示像素通道顺序 B/G/R；映射为 `pixel_format=BGR888` + `channel_order=[B,G,R]`，**不映射**为平台 `byte_order` | 保留旧证据原字节，不改写 |
| 模型语义 | RGB888（逐像素 R/G/B） | 2A/2B 冻结 D2 |
| 采集时钟 | `PENDING_MEASUREMENT`（不得填造频率） | 本轮未实测 |

范围标签（**描述性，不是新的枚举值**；两者都映射到 `source_kind=camera` → S4-A `CAMERA`）：

| 标签 | 计时口径 | 允许结论 | 禁止结论 |
|---|---|---|---|
| `camera_live_colour` | `real_live` | 实时采集链路（RGB565 展开/通道顺序/缩放/补边/量化）与独立参考一致；真实场景交互与长跑 | 灰度诊断帧作为真彩质量依据；未联调时以注入/合成替代 |
| `camera_capture_replay_colour` | `replay_only` | 用已抓取的真实彩色帧回放，先验颜色/预处理一致性 | 把回放计时当实时端到端证据；把回放结论升级为实物集成结论 |

- **不得混同**：传感器 RGB565、RAW BGR888（像素通道 B/G/R）、平台 `byte_order=little` 与模型 RGB888（R/G/B）是四个不同概念。旧 Stage3 `source_byte_order=BGR` 按上表映射为像素通道顺序，不代表标量端序；旧证据保持不变。
- **D2 通道重排要求**：`raw_frame` 每像素 `[B,G,R]` 必须先转换为 `[R,G,B]`，再执行 resize/letterbox、归一化和量化。例如 `[0x11,0x22,0x33]` → `[0x33,0x22,0x11]`。当前该转换只在离线 Python D2 图像参考中存在。
- **运行期支持 fail-closed**：`runtime_support_status=NOT_IMPLEMENTED`、mailbox PS driver `NOT_IMPLEMENTED`、PL integration `NOT_INSTANTIATED`。现有 C 注入格式枚举不含 BGR888，且其数值 `1` 为 RGB565；G0 候选 `mailbox_pixel_format_code=1` 是独立 wire 编码，未实现显式映射且不得直接 cast。PL RAW 通道读取未实现重排。因此不得将离线 Python 参考、RAW 帧格式契约或容量证据表述为真实 C/PL/摄像头链路已支持。
- **原图坐标口径**：检测框 `xyxy` 以原图（1280×720 采集帧）像素坐标为准；416 张量坐标不得直接充当原图坐标。
- **逐帧源帧哈希与 Stage5 UR-1 回放元数据**：每帧必须逐帧记录 `frame_integrity`（CRC32/SHA-256 + 实际字节数）并绑定 session/frame 与采集/回放时刻。回放证据侧还需绑定源文件路径与 SHA-256、宽高、stride、`pixel_format=BGR888`、`channel_order=[B,G,R]`、平台 `byte_order=little`、阶段3 采集证据入口、`frame_identity`（session/frame/source frame ID）及 `capture_time_utc8`/`timestamp_source`/`clock_domain`。这些是证据侧回放元数据，不增加运行时帧字段。
- **时效边界**：以上仅为契约改绑；不表示真实彩色采集、回放或板级联调已执行（本轮 `NOT_RUN`）。

## 0.2 绑定字节口径（r05 新增，N-1）

- **默认口径 = 工作树磁盘字节**：`upstream_bindings[].sha256` 默认记录文件**原始字节**的 SHA-256（复算：对磁盘字节直接算 SHA-256）。
- **跨换行环境要求**：复算必须使用 `-c core.autocrlf=false`（或改用 blob 口径），否则 checkout/commit 的换行归一化会造成失配。
- **显式 blob 口径**：条目给出 `byte_basis = "git_blob_content"` 时，`sha256` 记录该路径在**所属工作树 HEAD 提交中的 blob 内容** SHA-256（复算：`git -C <tree> cat-file blob HEAD:<rel>` 后对原始字节算 SHA-256）；对应的 `worktree_disk_sha256_annotation` 仅为注记、**不参与校验**。
- **覆盖范围（N-a 更正，含日期核实）**：本树 `-text` 覆盖 w4 的 `docs/stage4/**` 与 `report/evidence/**`（disk==blob）；**dbdf 确有 `report/evidence/S3-T05/** -text`**，规则由 **`4aada6d`（2026-10-24 01:59 +0800）** 加入，原文即 `report/evidence/S3-T05/** -text`（同提交注释：阶段3 板级窗口证据（S3-T05）保留原始字节；`git log -S'report/evidence/S3-T05' -- .gitattributes` 只有这一条）；更早的 `-text` 约定属 `report/evidence/S2A-*` 路径（2026-09-25…2026-10-01，如 `cdb2fbd`），**不覆盖 S3-T05**。上一版「2026-10-01 起」为**错误日期**，「unspecified/无覆盖」亦不成立（本树早期 `check-attr` 读数早于 `4aada6d`，当时确为 unspecified）；差额成因为文件**在 `-text` 生效前入库**（索引 stat 缓存使 `git status` 一度看似干净）。因此**跨树引用统一按 `git_blob_content` 绑定**；**不再新增 `.gitattributes` 覆盖**（与阶段3 同口径）。
- **fail-closed 漂移断言（B-3，复审立为规则）**：落盘清单为每个被绑树记录**期望 HEAD + 记录时间窗**，并断言**实际 HEAD == 记录值**；任一不等即该批次 **FAIL**（不得因“当时值是对的”而 PASS），须重绑、重跑并以新 RunId 落盘真实退出码。工具 `scripts/stage4_s4ctrl/check_bound_tree_heads.py`，清单 `report/evidence/S4-CTRL/t21_optionA_landing_20261024_r02/bound_trees.json`。
- **事实依据**：口径测量工具 `scripts/stage4_s4ctrl/check_binding_byte_semantics.py`（磁盘/过滤/原始/已提交 blob 四种口径）；证据 `t21_binding_byte_semantics_20261024_r04/`（本批改绑前）与 `t21_binding_byte_semantics_20261024_r05/`（改绑后复测）。
- **负向对照**：把某条 blob 口径条目的 `sha256` 改成其磁盘 SHA（或改成任意错误值）时，自检必须判 FAIL。

## 1. 输入帧契约 `[CDX-010 §3.1]`

| 字段 | 类型 | 必填 | 语义 |
|---|---|---|---|
| `contract_version` | string | 是 | 固定 `s4-shared-io/1.3.0`；不匹配即拒绝消费 |
| `source_kind` | enum | 是 | `file_injection` / `camera` / `synthetic`（与 C 实现/CLI 同名）；映射到 S4-A `source_kind`（`BOARD_INJECTION`↔`file_injection`、`CAMERA`↔`camera`、`OFFLINE_REGRESSION`↔`synthetic`），证据中必须可互相换算 |
| `session_id` | uint32 | 是 | 沿用 S4-A u32。PS 每次启动、复位 `frame_id` 计数或同一请求重开 RUN 时重新分配；会话内不变且 `frame_id` 不复用，按 S4-A 规则拒绝回绕 |
| `frame_id` | u32 | 是 | PS 侧 +1 单调分配（沿用 S4-A `frame_id_allocation`），与送入 PL 的 `FRAME_ID` 同值 |
| `width` / `height` | u32 | 是 | 原图像素尺寸；补边逆映射唯一基准 |
| `pixel_format` | enum | 是 | `BGR888`/`RGB888`/`RGB565`/`GRAY8`/`INT8_CHW_416`；当前 `raw_frame` 必须是 BGR888，像素字节顺序 B/G/R；**覆盖范围由注入点决定** |
| `byte_order` | string | 是 | 当前平台 `little`，只描述多字节标量端序，不描述 RGB/BGR 像素通道顺序 |
| `stride_bytes` | u32 | 是 | 行跨距；行尾填充未定义、不得被消费 |
| `buffer` | object | 是 | `region_name`/`base_addr`/`offset_bytes`/`length_bytes`/`alignment`；半开区间；`region_name` 必须在地址图中 |
| `frame_integrity` | object | 是 | `algorithm`(crc32_ieee/sha256)+`value`+`length_bytes`；**逐帧记录** |
| `capture_time_available` | bool | 是 | 顶层与 `measurement_scope` 一致：`file_injection` / `synthetic` 必须为 false；`camera` 必须为 true |
| `injection_start_ns` | u64 | 条件 | 仅 `file_injection`：开始把帧写入 DDR 的单调时刻。**不是采集时间** |
| `capture_time_ns` | u64 | 条件 | `file_injection` / `synthetic` 使用 0 哨兵且在 `unavailable_fields` 标记不可用；`camera` 必须提供非零首个有效像素时刻且不得标记 unavailable |
| `timestamp_source` | object | 是 | `clock`/`freq_hz`/`wrap_handling`/`epoch_note` |
| `clock_domain` | string | 是 | 时间戳所属时钟域；`file_injection` 下必填 |
| `measurement_scope` | object | 是 | 键与取值域**与 S4-A 完全一致**；`source_kind` 与顶层严格映射。`file_injection` / `synthetic` 下时间不可用且 `unavailable_fields` 含 `capture_time_ns`；`camera` 下时间为非零真值且不得标记 unavailable |

**D2 输入顺序及运行期状态**：RAW `pixel_format=BGR888`、`channel_order=[B,G,R]`；冻结 D2 处理时必须逐像素重排到 RGB `[R,G,B]`，且发生在 resize、归一化、量化之前。字节样例 `[0x11,0x22,0x33]` → `[0x33,0x22,0x11]`。当前转换仅由离线 Python D2 图像参考执行，`runtime_support_status=NOT_IMPLEMENTED`；现有 C 注入 API/PL RAW 路径尚不支持 BGR888，运行期验收必须 fail-closed。

**注入点覆盖范围**：`BGR888`/`RGB888`/`RGB565` 只有在被验收的预处理**之前**注入才覆盖预处理链；`INT8_CHW_416` 只覆盖网络+后处理；直接写显示缓冲只覆盖显示。任何“全链路通过”的说法必须以其注入点覆盖为前提，且满足当前格式的真实运行期实现验收。

**事件顺序 `[CDX-010 §3.4]`**：`producer_write_start` → `producer_write_complete` → `cache_flush_by_producer` → `ownership_publish_to_consumer` → `consumer_invalidate` → `consumer_start` → `consumer_done` → `buffer_release_to_producer`。输入帧在消费者读取前完成 invalidate + DSB。任一事件缺失即该帧不可消费；**不得用超时推断完成**。

**缓存与 DMA**：冻结 2B BSP 在 `w2b/vitis/s2b_inference_app.c:71` 声明 `S2B_BSP_CACHELINE_BYTES==32U`，即 32 B 硬件缓存行；本阶段 C 常量 64 B 表示保守的维护区间向外取整/缓冲对齐策略，不代表物理缓存行。生产者发布前 flush + DSB；消费者读取输入前 invalidate + DSB。PL 完成后对输出 heads 做独立 invalidate + DSB，该输出维护不属于输入帧事件序列。**不得覆盖仍被持有的帧**；方向以地址图 `cache_maintenance` 为准。

**帧序列规则（N5）**：重复、回退、乱序接纳或回绕的 `frame_id` → 拒绝并记 FAIL；会话重开须按 S4-A 重新分配 u32 `session_id`。结果连接按下表各自角色执行，无法唯一关联或顺序矛盾者不得用于跨阶段证据；拒绝必须记录原因。

## 2. 结果契约

### 2.1 结果记录

字段与语义以 `[S4-A]` 为权威：`frame_id`、`result_seq`、`geometry`、`state`、`detection_count`、`detections`（`class_id`/`class_name`/`score`/`xyxy`/`xyxy_px`/`source_order`）、`candidate_count`、`candidate_count_pre_threshold`、`candidate_overflow`、`capture_time_ns`、`result_time_ns`、`inference_time_ns`、`end_to_end_latency_ns`、`dropped_frames`、`stale`、`error_code`。
`file_injection` / `synthetic` 下 `capture_time_available=false`、`capture_time_ns=0` 且 `unavailable_fields` 必须含 `capture_time_ns`；`camera` 下必须为 true、时间非零且不能标记 unavailable。注入起点不是采集时间；注入结果派生的 `end_to_end_latency_ns` 不可定义。

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
- 唯一来源：阶段5 G0 的 `STALE_AGE_LIMIT_NS`（`[w5-G0]` 记为 `G0_FIXED_OFFLINE`，值 **200000000 ns**）。
- **已批准（r04 应用）**：`stale_limit_ns = 200000000`，`stale_limit_status = APPROVED_BY_WONG`，批准依据 = `decisions/stage6_approval_receipt_20261023_r01.md`（SHA-256 `d8edb848…e874fb`，Wong 2026-10-23「按你建议」）。阶段4/5/6 **必须使用同一常量**，不得各建一套。
- 阶段4 侧同时记录 `twenty_four_params_note`：阶段6 的 24 项参数已按草案值同批批准（`T6-A03` 数值除外，仍 `NOT_RUN`）；阶段4 只引用跨阶段 stale 常量与 `T6-A03` 所需的帧周期 P 输入，不代改阶段6 行为表。
- **取代关系**：S4-A r06 冻结快照内的 `S4A-DRAFT-STALE-AGE-LIMIT` 仍标 `DRAFT_PENDING_APPROVAL`；那是该轮快照的历史标签，本契约按批准记录生效的 200000000 ns 为其取代值。S4-A r06 文件字节保留不改写。
- **『已批准』≠『实现已同步』**：本契约只固定常量与来源；阶段4 是否已在真实链路按该常量判定 stale 属实测范围，本轮 `NOT_RUN`。
- 每结果只计一次 stale，原因留日志。

### 2.4 HUD 13 字段来源 `[CDX-014 §5.4]`

`capture_fps`（camera 可用；注入/合成必须标 UNAVAILABLE）、`inference_fps`、`display_fps`（阶段5 定义）、`inference_time_ns`、`age_result_ns`、`age_frame_ns`、`frame_id`（`displayed_frame_id`/`result_frame_id` 成对）、`boxes`、`stale_cleared`、`dropped_frames`、`timeouts`（不得记作零框成功）、`warmup_state`、`display_semantics`。
该映射的**键集合必须恰等于 13 字段**（说明性文字不得混入）；不可用者必须标注不可用，不得用 0 伪装实测。

### 2.5 PS 侧日志与唯一映射（UART 方案 B）`[CDX-010 §2.3]`

- 本共享契约结果唯一关联键：`(session_id, frame_id, result_seq)`。S4-A `join_key=(session_id, frame_id, repeat_index)` 用于结果与重复项连接；PS 日志主键 `(session_id, result_seq)`；UART 可观测键 `(frame_id, repeat_index, sequence)`，其中 `sequence` 只作配对/一致性核对。三者用途不同，不得互相替代。
- 桥接旁路日志同时记录 `session_id`、`frame_id`、`repeat_index`、`result_seq`、UART `sequence`、来源、逐帧 `frame_integrity` 和所有权事件；并记录 `capture_time_ns` 或 `injection_start_ns`（按来源）、发布/推理/结果时刻、age 原始时刻、丢帧/超时/队列满计数及拒绝原因。
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
- 本契约和地址图当前均为 `DRAFT_PENDING_REVIEW`：经独立审查与 Lead 确认后再冻结；冻结前不得作为验收依据。
- **r06 消费方重绑清单（只读请求，不改 w5/w6）**：
  - **阶段5（w5）**：冻结前重绑地址图至 **r04**、共享契约至 **1.3.0/r07**；RAW 回放元数据新增 evidence-side `pixel_format=BGR888`、`channel_order=[B,G,R]`，并保留平台 `byte_order=little` 的独立含义。该元数据用于 UR-1 回放证据，不扩展运行时帧字段；阶段5 的显示五元组/HUD/`display_semantics=B_latest_result_overlay` 语义不变，仍不得写阶段4 缓冲。
  - **阶段6（w6）**：如消费本契约，冻结前重绑至 **1.3.0/r07**；跨阶段 `stale_age_limit` 常量值不变（200000000 ns、同源），`T6-A03` 数值仍待阶段4 实测帧周期 P（`NOT_RUN`）。
  - 两个消费方均须以跨方请求（本树 `report/evidence/S4-CTRL/**` 唯一编号）确认重绑并做适用回归；本契约**不代改** w5/w6 行为表。

## 5. 限制

- 不含真实板测结果；本轮无任何硬件执行（未装载位流、未打开 COM4/JTAG、未起 hw_server）。
- **r07 尚未经独立复审**（r04 既有 PASS 不覆盖 r06）；自检 PASS 只证明绑定/结构与约定一致，不等于接口语义已审、测试成功或 G0/G4/G5 通过。冻结前必须对**固定提交 + 被审 SHA** 另行独立复审。
- 地址图 r04 的 `raw_frame`/`raw_meta` 为 `PROPOSED_STAGE4_OWNED_PENDING_APPROVAL_AND_REVIEW`（非 FROZEN、`enable_required=true`）：**`ENABLE=0`、不访问候选区、不装载位流、不做板级操作**，直到独立审查和硬件窗口实测（CPU1 保持停止、无其他 DDR consumer、板上未被占用、cache 可见性）完成。
- 阶段3 部署实测的采集/显示帧基址为**运行期分配**（`dispCtrl.framePtr[curFrame]`），**无链接期静态保证**、换应用会变；任何消费方使用前必须运行期回读，**禁止硬编码**。
- 绑定字节口径：默认工作树磁盘字节；dbdf 两项按 `git_blob_content` 显式声明；跨换行环境复算须 `-c core.autocrlf=false` 或用 blob 口径。
- 不定义阶段5 布局/像素门槛/显示 FPS 语义（属阶段5 G0）。
- `camera_live_colour` / `camera_capture_replay_colour` 只是范围标签：写入本契约不代表真实彩色采集、回放或板级联调已执行；`capture_clock` 仍 `PENDING_MEASUREMENT`。
- 候选上限、时间口径与异常行为取值以 S4-A 阶段4 G0 契约为准。
- 绑定 SHA 为本次修订时点实际值；权威变更时必须显式更新绑定并登记取代关系（自检会 FAIL 直到更新）。

## r07 修订（2026-10-27）

1. `s4_offline_raw_replay_bridge`：由 `06c9ab8` 的 blob `ad71cae0…` 重绑到 r12 现行原始字节；
   `replaces.basis=git_blob_content`，并附 `raw_sha256=0c9e09d7…`，避免口径误标。
2. `stage5_display_g0_fields`：w5 在 `b6d11d4` 后经 `a465b48`/`5fd3336` 改动该文件，按规则重绑到
   `af51a4bf…`（修订 `a54f09f`），`replaces` 记录 `b6d11d4/10d24a39…`。
3. `contract_version` 升 `1.3.0`；补 `byte_basis_pointer` 指向口径登记表。
4. 语义未变；状态仍 `DRAFT_PENDING_REVIEW`，待独立复审后由阶段4 以仅改状态的提交登记。
